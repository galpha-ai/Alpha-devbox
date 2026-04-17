import { App, LogLevel } from '@slack/bolt';

import { ASSISTANT_NAME, TRIGGER_PATTERN } from '../config.js';
import { logger } from '../logger.js';
import {
  Channel,
  OnChatMetadata,
  OnInboundMessage,
  RegisteredAgent,
  SendMessageOptions,
  StatusIndicatorOptions,
} from '../types.js';

const MAX_MESSAGE_LENGTH = 4000;

type SlackMessageEvent = {
  channel: string;
  channel_type?: string;
  user?: string;
  text?: string;
  ts: string;
  thread_ts?: string;
  subtype?: string;
  bot_id?: string;
  message?: {
    text?: string;
    user?: string;
    ts: string;
    thread_ts?: string;
    bot_id?: string;
    edited?: {
      user: string;
      ts: string;
    };
  };
  previous_message?: {
    text?: string;
    user?: string;
    ts: string;
  };
};

export interface SlackChannelOpts {
  onMessage: OnInboundMessage;
  onChatMetadata: OnChatMetadata;
  registeredAgents: () => Record<string, RegisteredAgent>;
}

export class SlackChannel implements Channel {
  name = 'slack';

  private app: App;
  private connected = false;
  private botUserId: string | undefined;
  private flushing = false;
  private userNameCache = new Map<string, string>();
  private outgoingQueue: Array<{
    jid: string;
    text: string;
    options?: SendMessageOptions;
  }> = [];

  constructor(
    botToken: string,
    appToken: string,
    private opts: SlackChannelOpts,
  ) {
    this.app = new App({
      token: botToken,
      appToken,
      socketMode: true,
      logLevel: LogLevel.INFO,
      ignoreSelf: false,
    });
    this.setupEventHandlers();
  }

  private setupEventHandlers(): void {
    this.app.event('message', async ({ event }) => {
      const msg = event as SlackMessageEvent;
      logger.info(
        {
          channel: msg.channel,
          user: msg.user,
          subtype: msg.subtype,
          hasText: Boolean(msg.text),
        },
        'Slack message event received',
      );

      if (
        msg.subtype &&
        msg.subtype !== 'bot_message' &&
        msg.subtype !== 'message_changed'
      )
        return;

      // Extract the actual message from the nested structure for edited messages
      const actualMessage =
        msg.subtype === 'message_changed' && msg.message ? msg.message : msg;

      if (!actualMessage.text) return;

      const jid = `slack:${msg.channel}`;
      const timestamp = new Date(
        parseFloat(actualMessage.ts) * 1000,
      ).toISOString();
      const isGroup = msg.channel_type !== 'im';

      this.opts.onChatMetadata(jid, timestamp, undefined, 'slack', isGroup);

      const agents = this.opts.registeredAgents();
      if (!agents[jid]) {
        logger.info(
          { jid, registeredJids: Object.keys(agents) },
          'Ignoring message: no registered agent for JID',
        );
        return;
      }

      const isBotMessage =
        Boolean(actualMessage.bot_id) || actualMessage.user === this.botUserId;

      if (isBotMessage) {
        logger.info(
          { jid, messageId: actualMessage.ts },
          'Ignoring Slack self/bot echo event to avoid duplicate persistence',
        );
        return;
      }

      let senderName: string;

      senderName =
        (await this.resolveUserName(actualMessage.user || '')) ||
        actualMessage.user ||
        'unknown';

      let content = actualMessage.text;
      if (this.botUserId) {
        const mention = `<@${this.botUserId}>`;
        if (content.includes(mention) && !TRIGGER_PATTERN.test(content)) {
          content = `@${ASSISTANT_NAME} ${content}`;
        }
      }

      this.opts.onMessage(jid, {
        id: actualMessage.ts,
        chat_jid: jid,
        thread_id: actualMessage.thread_ts || msg.thread_ts || null,
        sender: actualMessage.user || actualMessage.bot_id || '',
        sender_name: senderName,
        content,
        timestamp,
        is_from_me: isBotMessage,
        is_bot_message: isBotMessage,
      });
    });
  }

  async connect(): Promise<void> {
    await this.app.start();
    try {
      const auth = await this.app.client.auth.test();
      this.botUserId = auth.user_id as string;
    } catch (err) {
      logger.warn({ err }, 'Connected to Slack but failed to resolve bot user');
    }
    this.connected = true;
    await this.flushOutgoingQueue();
    await this.syncChannelMetadata();
    logger.info('Slack channel connected');
  }

  async sendMessage(
    jid: string,
    text: string,
    options?: SendMessageOptions,
  ): Promise<void> {
    const channelId = jid.replace(/^slack:/, '');
    const threadId = options?.threadId || undefined;

    if (!this.connected) {
      this.outgoingQueue.push({ jid, text, options });
      logger.info(
        { jid, queueSize: this.outgoingQueue.length },
        'Slack disconnected, queued outbound message',
      );
      return;
    }

    try {
      if (text.length <= MAX_MESSAGE_LENGTH) {
        await this.app.client.chat.postMessage({
          channel: channelId,
          text,
          thread_ts: threadId,
        });
      } else {
        for (let i = 0; i < text.length; i += MAX_MESSAGE_LENGTH) {
          await this.app.client.chat.postMessage({
            channel: channelId,
            text: text.slice(i, i + MAX_MESSAGE_LENGTH),
            thread_ts: threadId,
          });
        }
      }
      logger.info({ jid, threadId }, 'Slack message sent');
    } catch (err) {
      this.outgoingQueue.push({ jid, text, options });
      logger.warn(
        { jid, err, queueSize: this.outgoingQueue.length },
        'Failed to send Slack message, queued for retry',
      );
    }
  }

  isConnected(): boolean {
    return this.connected;
  }

  ownsJid(jid: string): boolean {
    return jid.startsWith('slack:');
  }

  async disconnect(): Promise<void> {
    this.connected = false;
    await this.app.stop();
    logger.info('Slack channel disconnected');
  }

  async setTyping(
    jid: string,
    status: 'processing' | 'success' | 'error' | 'idle',
    options?: StatusIndicatorOptions,
  ): Promise<void> {
    const channelId = jid.replace(/^slack:/, '');
    const messageTs = options?.messageId;

    if (!messageTs) {
      logger.debug(
        { jid, status },
        'No triggering message timestamp for typing indicator',
      );
      return;
    }

    const EMOJI_MAP = {
      processing: 'hourglass_flowing_sand',
      success: 'white_check_mark',
      error: 'x',
      idle: null,
    };

    try {
      // Remove all status emojis to ensure clean state
      const allStatusEmojis = [
        'hourglass_flowing_sand',
        'white_check_mark',
        'x',
      ];
      for (const emoji of allStatusEmojis) {
        try {
          await this.app.client.reactions.remove({
            channel: channelId,
            name: emoji,
            timestamp: messageTs,
          });
        } catch (err) {
          // Ignore - emoji might not exist, which is fine
        }
      }

      // Add new status emoji if not idle
      const emoji = EMOJI_MAP[status];
      if (emoji) {
        await this.app.client.reactions.add({
          channel: channelId,
          name: emoji,
          timestamp: messageTs,
        });
      }

      logger.debug({ jid, status, emoji }, 'Updated Slack typing indicator');
    } catch (err) {
      logger.warn(
        { jid, status, err },
        'Failed to update Slack typing indicator',
      );
    }
  }

  private async resolveUserName(userId: string): Promise<string | undefined> {
    if (!userId) return undefined;

    const cached = this.userNameCache.get(userId);
    if (cached) return cached;

    try {
      const result = await this.app.client.users.info({ user: userId });
      const name = result.user?.real_name || result.user?.name;
      if (name) this.userNameCache.set(userId, name);
      return name || undefined;
    } catch (err) {
      logger.debug({ userId, err }, 'Failed to resolve Slack user name');
      return undefined;
    }
  }

  private async flushOutgoingQueue(): Promise<void> {
    if (this.flushing || this.outgoingQueue.length === 0) return;

    this.flushing = true;
    try {
      while (this.outgoingQueue.length > 0) {
        const item = this.outgoingQueue.shift();
        if (!item) break;
        await this.sendMessage(item.jid, item.text, item.options);
      }
    } finally {
      this.flushing = false;
    }
  }

  private async syncChannelMetadata(): Promise<void> {
    try {
      let cursor: string | undefined;
      do {
        const result = await this.app.client.conversations.list({
          types: 'public_channel,private_channel',
          exclude_archived: true,
          limit: 200,
          cursor,
        });

        const now = new Date().toISOString();
        for (const ch of result.channels || []) {
          if (!ch.id || !ch.name || !ch.is_member) continue;
          this.opts.onChatMetadata(
            `slack:${ch.id}`,
            now,
            ch.name,
            'slack',
            true,
          );
        }

        cursor = result.response_metadata?.next_cursor || undefined;
      } while (cursor);
    } catch (err) {
      logger.warn({ err }, 'Slack metadata sync failed');
    }
  }
}
