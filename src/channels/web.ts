import { randomUUID } from 'crypto';
import http from 'http';
import {
  createUIMessageStream,
  pipeUIMessageStreamToResponse,
  type UIMessage,
  type UIMessageStreamWriter,
} from 'ai';

import { MAX_CONCURRENT_CONTAINERS } from '../config.js';
import {
  getMessageHistory,
  getReplayLinkById,
  getSessionsByChannel,
} from '../db.js';
import { logger } from '../logger.js';
import { makeSessionScopeKey } from '../session-scope.js';
import {
  Channel,
  NewMessage,
  OnChatMetadata,
  OnInboundMessage,
  RegisteredAgent,
  SendMessageOptions,
  StatusIndicatorOptions,
} from '../types.js';

const CHAT_STREAM_TIMEOUT_MS = 600_000;
const CHAT_STREAM_TIMEOUT_MESSAGE =
  'The assistant did not write back a reply before the timeout window elapsed.';
const CHAT_STREAM_REPLACED_MESSAGE =
  'A newer chat request replaced the active response stream.';
const CHAT_STREAM_ERROR_MESSAGE =
  'The assistant failed before completing the reply.';

type DeliveryTarget = {
  agent: RegisteredAgent;
  sessionKey: string;
};

type DeliveryResult =
  | { ok: true; target: DeliveryTarget }
  | {
      ok: false;
      code: 'no_agent';
      message: string;
    };

interface PendingChatStream {
  writer?: UIMessageStreamWriter<UIMessage>;
  textPartId: string;
  queuedDeltas: string[];
  receivedTextCount: number;
  started: boolean;
  textStarted: boolean;
  resolved: boolean;
  completion:
    | { status: 'pending' }
    | { status: 'success' }
    | { status: 'error'; errorText: string };
  done: Promise<void>;
  resolveDone: () => void;
  timeout: NodeJS.Timeout;
}

export interface WebChannelOpts {
  onMessage: OnInboundMessage;
  onChatMetadata: OnChatMetadata;
  registeredAgents: () => Record<string, RegisteredAgent>;
  registerAgentForChat?: (chatJid: string, agent: RegisteredAgent) => void;
  getActiveCount: () => number;
  getWaitingCount: () => number;
}

export class WebChannel implements Channel {
  name = 'web';

  private server: http.Server;
  private port: number;
  private opts: WebChannelOpts;
  private pendingChatStreams = new Map<string, PendingChatStream>();

  constructor(port: number, opts: WebChannelOpts) {
    this.port = port;
    this.opts = opts;

    this.server = http.createServer((req, res) => this.handleHttp(req, res));
  }

  async connect(): Promise<void> {
    return new Promise((resolve) => {
      this.server.listen(this.port, () => {
        const addr = this.server.address();
        if (addr && typeof addr === 'object') {
          this.port = addr.port;
        }
        logger.info({ port: this.port }, 'Web channel listening');
        resolve();
      });
    });
  }

  getPort(): number {
    return this.port;
  }

  isConnected(): boolean {
    return this.server.listening;
  }

  ownsJid(jid: string): boolean {
    return jid.startsWith('web:');
  }

  async sendMessage(
    jid: string,
    text: string,
    options?: SendMessageOptions,
  ): Promise<void> {
    const conversationId = options?.threadId ?? null;
    if (!conversationId) {
      return;
    }

    const delivery = this.resolveDeliveryTarget(jid, conversationId);
    if (!delivery.ok) {
      return;
    }

    this.pushPendingChatText(delivery.target.sessionKey, text);
  }

  async setTyping(
    jid: string,
    status: 'processing' | 'success' | 'error' | 'idle',
    options?: StatusIndicatorOptions,
  ): Promise<void> {
    const conversationId = options?.threadId ?? null;
    if (!conversationId) {
      return;
    }

    const delivery = this.resolveDeliveryTarget(jid, conversationId);
    if (!delivery.ok) {
      return;
    }

    if (status === 'success') {
      this.completePendingChatStream(delivery.target.sessionKey, {
        status: 'success',
      });
      return;
    }

    if (status === 'error') {
      this.completePendingChatStream(delivery.target.sessionKey, {
        status: 'error',
        errorText: CHAT_STREAM_ERROR_MESSAGE,
      });
    }
  }

  async disconnect(): Promise<void> {
    return new Promise((resolve) => {
      this.server.close(() => resolve());
    });
  }

  private handleHttp(
    req: http.IncomingMessage,
    res: http.ServerResponse,
  ): void {
    const url = new URL(req.url || '/', `http://${req.headers.host}`);
    const path = url.pathname;

    if (path === '/api/devbox/health' && req.method === 'GET') {
      this.jsonResponse(res, 200, { status: 'ok' });
      return;
    }

    const replayMatch = path.match(
      /^\/api\/devbox\/replays\/([^/]+)\/ui-messages$/,
    );
    if (replayMatch && req.method === 'GET') {
      const replayId = replayMatch[1];
      const before = url.searchParams.get('before') ?? undefined;
      const limit = parseInt(url.searchParams.get('limit') ?? '100', 10);
      const replay = getReplayLinkById(replayId);
      if (!replay) {
        this.jsonResponse(res, 404, {
          error: 'Replay not found',
          code: 'replay_not_found',
        });
        return;
      }

      const rawMessages = getMessageHistory(
        replay.channelId,
        replay.threadId || '',
        {
          before,
          limit,
          includeThreadParent: true,
        },
      );
      const messages = canonicalizeChatMessages(rawMessages);
      this.jsonResponse(res, 200, {
        replayId,
        derivedAt: new Date().toISOString(),
        messages,
      });
      return;
    }

    const userId = req.headers['x-user-id'] as string | undefined;
    if (!userId) {
      this.jsonResponse(res, 401, { error: 'Missing X-User-Id header' });
      return;
    }

    const chatJid = `web:${userId}`;

    if (path === '/api/devbox/conversations' && req.method === 'POST') {
      this.readBody(req)
        .then(() => {
          const conversationId = randomUUID();
          this.opts.onChatMetadata(
            chatJid,
            new Date().toISOString(),
            undefined,
            'web',
            false,
          );
          this.jsonResponse(res, 201, { conversationId });
        })
        .catch(() =>
          this.jsonResponse(res, 400, { error: 'Invalid request body' }),
        );
      return;
    }

    if (path === '/api/devbox/conversations' && req.method === 'GET') {
      const sessions = getSessionsByChannel(chatJid);
      this.jsonResponse(res, 200, {
        conversations: sessions.map((s) => ({
          conversationId: s.threadId,
          agentName: s.agentName,
        })),
      });
      return;
    }

    if (path === '/api/devbox/chat' && req.method === 'POST') {
      this.readBody(req)
        .then((body) => {
          const conversationId =
            typeof body.id === 'string' ? body.id.trim() : '';
          const content = getLatestUserMessageText(body.messages);

          if (!conversationId) {
            this.jsonResponse(res, 400, { error: 'id is required' });
            return;
          }

          if (!content) {
            this.jsonResponse(res, 400, {
              error: 'messages must include a user text prompt',
            });
            return;
          }

          const delivery = this.resolveDeliveryTarget(chatJid, conversationId);
          if (!delivery.ok) {
            this.jsonResponse(res, 400, { error: delivery.message });
            return;
          }

          const pending = this.registerPendingChatStream(
            delivery.target.sessionKey,
          );
          const stream = createUIMessageStream<UIMessage>({
            execute: async ({ writer }) => {
              this.attachPendingChatStreamWriter(pending, writer);
              await pending.done;
              this.cleanupPendingChatStream(
                delivery.target.sessionKey,
                pending,
              );
            },
          });

          pipeUIMessageStreamToResponse({
            response: res,
            stream,
          });

          try {
            this.deliverInboundMessage(
              userId,
              chatJid,
              conversationId,
              content,
              delivery.target,
            );
          } catch (error) {
            logger.error(
              { error, chatJid, conversationId },
              'Failed to enqueue web chat message',
            );
            this.completePendingChatStream(delivery.target.sessionKey, {
              status: 'error',
              errorText: CHAT_STREAM_ERROR_MESSAGE,
            });
          }
        })
        .catch(() =>
          this.jsonResponse(res, 400, { error: 'Invalid request body' }),
        );
      return;
    }

    const canonicalMatch = path.match(
      /^\/api\/devbox\/conversations\/([^/]+)\/ui-messages$/,
    );
    if (canonicalMatch) {
      const conversationId = canonicalMatch[1];
      if (req.method === 'GET') {
        const before = url.searchParams.get('before') ?? undefined;
        const limit = parseInt(url.searchParams.get('limit') ?? '50', 10);
        const derivedAt = new Date().toISOString();
        const rawMessages = getMessageHistory(chatJid, conversationId, {
          before,
          limit,
        });
        const messages = canonicalizeChatMessages(rawMessages);
        this.jsonResponse(res, 200, { messages, derivedAt });
        return;
      }
    }

    const msgMatch = path.match(
      /^\/api\/devbox\/conversations\/([^/]+)\/messages$/,
    );
    if (msgMatch) {
      const conversationId = msgMatch[1];

      if (req.method === 'POST') {
        this.readBody(req)
          .then((body) => {
            if (!body.content || typeof body.content !== 'string') {
              this.jsonResponse(res, 400, { error: 'content is required' });
              return;
            }

            const delivery = this.resolveDeliveryTarget(
              chatJid,
              conversationId,
            );
            if (!delivery.ok) {
              this.jsonResponse(res, 400, { error: delivery.message });
              return;
            }

            this.deliverInboundMessage(
              userId,
              chatJid,
              conversationId,
              body.content,
              delivery.target,
            );
            this.jsonResponse(res, 202, { queued: true });
          })
          .catch(() =>
            this.jsonResponse(res, 400, { error: 'Invalid request body' }),
          );
        return;
      }

      if (req.method === 'GET') {
        const before = url.searchParams.get('before') ?? undefined;
        const limit = parseInt(url.searchParams.get('limit') ?? '50', 10);
        const messages = getMessageHistory(chatJid, conversationId, {
          before,
          limit,
        });
        this.jsonResponse(res, 200, { messages });
        return;
      }
    }

    const delMatch = path.match(/^\/api\/devbox\/conversations\/([^/]+)$/);
    if (delMatch && req.method === 'DELETE') {
      const conversationId = delMatch[1];
      const delivery = this.resolveDeliveryTarget(chatJid, conversationId);
      if (delivery.ok) {
        this.deliverInboundMessage(
          userId,
          chatJid,
          conversationId,
          '/done --force',
          delivery.target,
        );
      }
      this.jsonResponse(res, 200, { deleted: true });
      return;
    }

    this.jsonResponse(res, 404, { error: 'Not found' });
  }

  private resolveDeliveryTarget(
    chatJid: string,
    conversationId: string,
  ): DeliveryResult {
    if (this.opts.getActiveCount() >= MAX_CONCURRENT_CONTAINERS) {
      logger.info(
        {
          chatJid,
          conversationId,
          waitingCount: this.opts.getWaitingCount(),
        },
        'Web request queued behind active sessions',
      );
    }

    const agent = this.resolveAgentForChat(chatJid);
    if (!agent) {
      logger.warn(
        { chatJid },
        'No agent registered for web user, dropping message',
      );
      return {
        ok: false,
        code: 'no_agent',
        message: 'No agent configured for web channel',
      };
    }

    return {
      ok: true,
      target: {
        agent,
        sessionKey: makeSessionScopeKey(
          chatJid,
          conversationId,
          agent.agentName,
        ),
      },
    };
  }

  private deliverInboundMessage(
    userId: string,
    chatJid: string,
    conversationId: string,
    content: string,
    target: DeliveryTarget,
  ): void {
    const timestamp = new Date().toISOString();
    const msgId = `web-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;

    this.opts.onChatMetadata(chatJid, timestamp, undefined, 'web', false);
    this.opts.onMessage(chatJid, {
      id: msgId,
      chat_jid: chatJid,
      thread_id: conversationId,
      sender: userId,
      sender_name: userId,
      content,
      timestamp,
      is_from_me: false,
      is_bot_message: false,
    });

    logger.debug(
      {
        chatJid,
        conversationId,
        sessionKey: target.sessionKey,
        agentName: target.agent.agentName,
      },
      'Queued inbound web message',
    );
  }

  private registerPendingChatStream(sessionKey: string): PendingChatStream {
    const existing = this.pendingChatStreams.get(sessionKey);
    if (existing) {
      this.setPendingChatStreamCompletion(existing, {
        status: 'error',
        errorText: CHAT_STREAM_REPLACED_MESSAGE,
      });
    }

    let resolveDone: () => void = () => {};
    const pending: PendingChatStream = {
      textPartId: `text-${randomUUID()}`,
      queuedDeltas: [],
      receivedTextCount: 0,
      started: false,
      textStarted: false,
      resolved: false,
      completion: { status: 'pending' },
      done: new Promise<void>((resolve) => {
        resolveDone = resolve;
      }),
      resolveDone,
      timeout: setTimeout(() => {
        if (pending.receivedTextCount > 0) {
          this.setPendingChatStreamCompletion(pending, { status: 'success' });
          return;
        }

        this.setPendingChatStreamCompletion(pending, {
          status: 'error',
          errorText: CHAT_STREAM_TIMEOUT_MESSAGE,
        });
      }, CHAT_STREAM_TIMEOUT_MS),
    };

    this.pendingChatStreams.set(sessionKey, pending);
    return pending;
  }

  private attachPendingChatStreamWriter(
    pending: PendingChatStream,
    writer: UIMessageStreamWriter<UIMessage>,
  ): void {
    pending.writer = writer;
    this.flushPendingChatStream(pending);
  }

  private pushPendingChatText(sessionKey: string, text: string): void {
    const pending = this.pendingChatStreams.get(sessionKey);
    const nextText = text.trim();
    if (!pending || !nextText) {
      return;
    }

    const delta = pending.receivedTextCount > 0 ? `\n\n${nextText}` : nextText;
    pending.receivedTextCount += 1;
    pending.queuedDeltas.push(delta);
    this.flushPendingChatStream(pending);
  }

  private completePendingChatStream(
    sessionKey: string,
    completion: { status: 'success' } | { status: 'error'; errorText: string },
  ): void {
    const pending = this.pendingChatStreams.get(sessionKey);
    if (!pending) {
      return;
    }

    if (completion.status === 'error' && pending.receivedTextCount > 0) {
      this.setPendingChatStreamCompletion(pending, { status: 'success' });
      return;
    }

    this.setPendingChatStreamCompletion(pending, completion);
  }

  private setPendingChatStreamCompletion(
    pending: PendingChatStream,
    completion: { status: 'success' } | { status: 'error'; errorText: string },
  ): void {
    if (pending.completion.status !== 'pending') {
      return;
    }

    pending.completion = completion;
    clearTimeout(pending.timeout);
    this.flushPendingChatStream(pending);
  }

  private flushPendingChatStream(pending: PendingChatStream): void {
    const writer = pending.writer;
    if (!writer) {
      return;
    }

    if (!pending.started) {
      writer.write({ type: 'start' });
      writer.write({ type: 'start-step' });
      pending.started = true;
    }

    if (!pending.textStarted && pending.queuedDeltas.length > 0) {
      writer.write({ type: 'text-start', id: pending.textPartId });
      pending.textStarted = true;
    }

    while (pending.queuedDeltas.length > 0) {
      writer.write({
        type: 'text-delta',
        id: pending.textPartId,
        delta: pending.queuedDeltas.shift()!,
      });
    }

    if (pending.completion.status === 'pending' || pending.resolved) {
      return;
    }

    if (pending.textStarted) {
      writer.write({ type: 'text-end', id: pending.textPartId });
    }

    if (pending.completion.status === 'error') {
      writer.write({
        type: 'error',
        errorText: pending.completion.errorText,
      });
    } else {
      writer.write({ type: 'finish-step' });
      writer.write({ type: 'finish' });
    }

    pending.resolved = true;
    pending.resolveDone();
  }

  private cleanupPendingChatStream(
    sessionKey: string,
    pending: PendingChatStream,
  ): void {
    clearTimeout(pending.timeout);
    if (this.pendingChatStreams.get(sessionKey) === pending) {
      this.pendingChatStreams.delete(sessionKey);
    }
  }

  private resolveAgentForChat(chatJid: string): RegisteredAgent | undefined {
    const agents = this.opts.registeredAgents();
    const direct = agents[chatJid];
    if (direct) return direct;

    const wildcard = agents['web:*'];
    if (!wildcard) return undefined;

    const boundAgent: RegisteredAgent = {
      ...wildcard,
      requiresTrigger: false,
    };
    this.opts.registerAgentForChat?.(chatJid, boundAgent);
    return boundAgent;
  }

  private jsonResponse(
    res: http.ServerResponse,
    status: number,
    body: any,
  ): void {
    res.writeHead(status, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(body));
  }

  private readBody(req: http.IncomingMessage): Promise<any> {
    return new Promise((resolve, reject) => {
      let data = '';
      req.on('data', (chunk) => {
        data += chunk;
      });
      req.on('end', () => {
        try {
          resolve(data ? JSON.parse(data) : {});
        } catch {
          reject(new Error('Invalid JSON'));
        }
      });
      req.on('error', reject);
    });
  }
}

function getLatestUserMessageText(messages: unknown) {
  if (!Array.isArray(messages)) {
    return '';
  }

  const latestUserMessage = [...messages].reverse().find(
    (
      message,
    ): message is {
      role: string;
      content?: unknown;
      parts?: Array<{ type?: string; text?: string }>;
    } =>
      Boolean(message) &&
      typeof message === 'object' &&
      'role' in message &&
      (message as { role?: string }).role === 'user',
  );

  if (!latestUserMessage) {
    return '';
  }

  if (typeof latestUserMessage.content === 'string') {
    return latestUserMessage.content.trim();
  }

  if (!Array.isArray(latestUserMessage.parts)) {
    return '';
  }

  return latestUserMessage.parts
    .filter(
      (
        part,
      ): part is {
        type: 'text';
        text: string;
      } => part?.type === 'text' && typeof part.text === 'string',
    )
    .map((part) => part.text)
    .join('')
    .trim();
}

type CanonicalChatMessage = {
  id: string;
  role: 'user' | 'assistant';
  parts: Array<{ type: 'text'; text: string; state: 'done' }>;
  metadata: {
    timestamp: string;
    sender: string;
    senderName: string;
  };
};

function canonicalizeChatMessages(
  messages: NewMessage[],
): CanonicalChatMessage[] {
  return [...messages]
    .filter((msg) => msg.content?.length)
    .sort((a, b) => {
      if (a.timestamp === b.timestamp) {
        return a.id.localeCompare(b.id);
      }
      return a.timestamp.localeCompare(b.timestamp);
    })
    .map((msg) => ({
      id: msg.id,
      role: msg.is_bot_message ? 'assistant' : 'user',
      parts: [
        {
          type: 'text',
          text: msg.content,
          state: 'done',
        },
      ],
      metadata: {
        timestamp: msg.timestamp,
        sender: msg.sender,
        senderName: msg.sender_name || msg.sender,
      },
    }));
}
