import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { RegisteredAgent } from '../types.js';

vi.mock('../config.js', () => ({
  ASSISTANT_NAME: 'Devbox',
  TRIGGER_PATTERN: /^@Devbox\b/i,
}));

vi.mock('../logger.js', () => ({
  logger: {
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  },
}));

type Handler = (...args: any[]) => any;

const appRef = vi.hoisted(() => ({ current: null as any }));

vi.mock('@slack/bolt', () => ({
  App: class MockApp {
    eventHandlers = new Map<string, Handler>();
    client = {
      auth: {
        test: vi.fn().mockResolvedValue({ user_id: 'U_BOT' }),
      },
      chat: {
        postMessage: vi.fn().mockResolvedValue(undefined),
      },
      reactions: {
        add: vi.fn().mockResolvedValue(undefined),
        remove: vi.fn().mockRejectedValue(new Error('missing_reaction')),
      },
      users: {
        info: vi.fn().mockResolvedValue({
          user: { real_name: 'Alice' },
        }),
      },
      conversations: {
        list: vi.fn().mockResolvedValue({
          channels: [],
          response_metadata: {},
        }),
      },
    };

    constructor(_opts: any) {
      appRef.current = this;
    }

    event(name: string, handler: Handler) {
      this.eventHandlers.set(name, handler);
    }

    async start() {}
    async stop() {}
  },
  LogLevel: { ERROR: 'error' },
}));

import { SlackChannel, SlackChannelOpts } from './slack.js';

function currentApp() {
  return appRef.current;
}

function createOpts(overrides?: Partial<SlackChannelOpts>) {
  const onMessage: SlackChannelOpts['onMessage'] = vi.fn(
    (_chatJid: string, _message: any) => {},
  );
  const onChatMetadata: SlackChannelOpts['onChatMetadata'] = vi.fn(
    (
      _chatJid: string,
      _timestamp: string,
      _name?: string,
      _channel?: string,
      _isGroup?: boolean,
    ) => {},
  );

  return {
    onMessage,
    onChatMetadata,
    registeredAgents: () => ({
      'slack:C123': {
        name: 'main',
        agentName: 'main',
        trigger: '@Devbox',
        added_at: '2026-01-01T00:00:00.000Z',
      },
    }),
    ...overrides,
  };
}

function messageEvent(overrides?: Partial<Record<string, unknown>>) {
  return {
    channel: 'C123',
    channel_type: 'channel',
    user: 'U_USER',
    text: 'hello',
    ts: '1700000000.000100',
    ...overrides,
  };
}

async function triggerMessage(event: Record<string, unknown>) {
  const handler = currentApp().eventHandlers.get('message');
  if (handler) await handler({ event });
}

describe('SlackChannel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('connects and resolves bot identity', async () => {
    const channel = new SlackChannel('xoxb-token', 'xapp-token', createOpts());
    await channel.connect();
    expect(channel.isConnected()).toBe(true);
    expect(currentApp().client.auth.test).toHaveBeenCalledTimes(1);
  });

  it('stores inbound thread metadata and message', async () => {
    const opts = createOpts();
    const channel = new SlackChannel('xoxb-token', 'xapp-token', opts);
    await channel.connect();

    await triggerMessage(
      messageEvent({
        text: 'thread reply',
        ts: '1700000001.000200',
        thread_ts: '1700000000.000100',
      }),
    );

    expect(opts.onChatMetadata).toHaveBeenCalledWith(
      'slack:C123',
      expect.any(String),
      undefined,
      'slack',
      true,
    );
    expect(opts.onMessage).toHaveBeenCalledWith(
      'slack:C123',
      expect.objectContaining({
        chat_jid: 'slack:C123',
        thread_id: '1700000000.000100',
        content: 'thread reply',
      }),
    );
  });

  it('ignores self-generated bot echo events', async () => {
    const opts = createOpts();
    const channel = new SlackChannel('xoxb-token', 'xapp-token', opts);
    await channel.connect();

    await triggerMessage(
      messageEvent({
        text: 'bot echo',
        ts: '1700000009.000900',
        bot_id: 'B0AK3UMMH1C',
      }),
    );

    expect(opts.onMessage).not.toHaveBeenCalled();
  });

  it('emits metadata but skips unregistered channels', async () => {
    const opts = createOpts({
      registeredAgents: () => ({}),
    });
    const channel = new SlackChannel('xoxb-token', 'xapp-token', opts);
    await channel.connect();

    await triggerMessage(messageEvent({ channel: 'C999' }));

    expect(opts.onChatMetadata).toHaveBeenCalled();
    expect(opts.onMessage).not.toHaveBeenCalled();
  });

  it('translates bot mention into trigger prefix', async () => {
    const opts = createOpts();
    const channel = new SlackChannel('xoxb-token', 'xapp-token', opts);
    await channel.connect();

    await triggerMessage(
      messageEvent({
        text: 'ping <@U_BOT> please check',
      }),
    );

    expect(opts.onMessage).toHaveBeenCalledWith(
      'slack:C123',
      expect.objectContaining({
        content: '@Devbox ping <@U_BOT> please check',
      }),
    );
  });

  it('sends replies into thread when threadId is provided', async () => {
    const channel = new SlackChannel('xoxb-token', 'xapp-token', createOpts());
    await channel.connect();

    await channel.sendMessage('slack:C123', 'done', {
      threadId: '1700000000.000100',
    });

    expect(currentApp().client.chat.postMessage).toHaveBeenCalledWith({
      channel: 'C123',
      text: 'done',
      thread_ts: '1700000000.000100',
    });
  });

  it('splits long outbound text', async () => {
    const channel = new SlackChannel('xoxb-token', 'xapp-token', createOpts());
    await channel.connect();

    await channel.sendMessage('slack:C123', 'A'.repeat(4100));

    expect(currentApp().client.chat.postMessage).toHaveBeenCalledTimes(2);
  });

  it('queues outbound messages while disconnected and flushes on connect', async () => {
    const channel = new SlackChannel('xoxb-token', 'xapp-token', createOpts());

    await channel.sendMessage('slack:C123', 'queued');
    expect(currentApp().client.chat.postMessage).not.toHaveBeenCalled();

    await channel.connect();
    expect(currentApp().client.chat.postMessage).toHaveBeenCalledWith({
      channel: 'C123',
      text: 'queued',
      thread_ts: undefined,
    });
  });

  it('syncs channel metadata on connect', async () => {
    const opts = createOpts();
    const channel = new SlackChannel('xoxb-token', 'xapp-token', opts);
    currentApp().client.conversations.list.mockResolvedValueOnce({
      channels: [{ id: 'C100', name: 'devbox', is_member: true }],
      response_metadata: {},
    });
    await channel.connect();

    expect(opts.onChatMetadata).toHaveBeenCalledWith(
      'slack:C100',
      expect.any(String),
      'devbox',
      'slack',
      true,
    );
  });

  it('updates status reactions using the provided message id', async () => {
    const channel = new SlackChannel('xoxb-token', 'xapp-token', createOpts());
    await channel.connect();

    currentApp().client.reactions.remove.mockResolvedValue(undefined);

    await channel.setTyping('slack:C123', 'success', {
      messageId: '1700000000.000100',
    });

    expect(currentApp().client.reactions.remove).toHaveBeenCalledWith({
      channel: 'C123',
      name: 'hourglass_flowing_sand',
      timestamp: '1700000000.000100',
    });
    expect(currentApp().client.reactions.add).toHaveBeenCalledWith({
      channel: 'C123',
      name: 'white_check_mark',
      timestamp: '1700000000.000100',
    });
  });

  it('skips status reactions when no message id is provided', async () => {
    const channel = new SlackChannel('xoxb-token', 'xapp-token', createOpts());
    await channel.connect();

    await channel.setTyping('slack:C123', 'processing');

    expect(currentApp().client.reactions.remove).not.toHaveBeenCalled();
    expect(currentApp().client.reactions.add).not.toHaveBeenCalled();
  });

  it('owns only slack-prefixed JIDs', () => {
    const channel = new SlackChannel('xoxb-token', 'xapp-token', createOpts());
    expect(channel.ownsJid('slack:C123')).toBe(true);
    expect(channel.ownsJid('tg:123')).toBe(false);
  });
});
