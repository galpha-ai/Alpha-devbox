import { randomUUID } from 'crypto';
import http from 'http';
import { WebSocketServer, WebSocket } from 'ws';

import { ASSISTANT_NAME, MAX_CONCURRENT_CONTAINERS } from '../config.js';
import { getMessageHistory, getSessionsByChannel } from '../db.js';
import { logger } from '../logger.js';
import {
  Channel,
  OnChatMetadata,
  OnInboundMessage,
  RegisteredAgent,
  SendMessageOptions,
  StatusIndicatorOptions,
} from '../types.js';

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
  private wss: WebSocketServer;
  private connections = new Map<string, WebSocket>();
  private port: number;
  private opts: WebChannelOpts;

  constructor(port: number, opts: WebChannelOpts) {
    this.port = port;
    this.opts = opts;

    this.server = http.createServer((req, res) => this.handleHttp(req, res));
    this.wss = new WebSocketServer({ noServer: true });

    this.server.on('upgrade', (req, socket, head) => {
      const userId = req.headers['x-user-id'] as string | undefined;
      if (!userId) {
        socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n');
        socket.destroy();
        return;
      }

      this.wss.handleUpgrade(req, socket, head, (ws) => {
        this.connections.set(userId, ws);
        logger.info({ userId }, 'WebSocket connected');

        ws.on('message', (data) => {
          try {
            const msg = JSON.parse(data.toString());
            this.handleWsMessage(userId, msg);
          } catch (err) {
            logger.warn({ userId, err }, 'Invalid WebSocket message');
          }
        });

        ws.on('close', () => {
          if (this.connections.get(userId) === ws) {
            this.connections.delete(userId);
          }
          logger.info({ userId }, 'WebSocket disconnected');
        });
      });
    });
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
    const userId = jid.slice('web:'.length);
    const ws = this.connections.get(userId);
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    ws.send(
      JSON.stringify({
        type: 'output',
        conversationId: options?.threadId ?? null,
        content: text,
      }),
    );
  }

  async setTyping(
    jid: string,
    status: 'processing' | 'success' | 'error' | 'idle',
    options?: StatusIndicatorOptions,
  ): Promise<void> {
    const userId = jid.slice('web:'.length);
    const ws = this.connections.get(userId);
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    ws.send(
      JSON.stringify({
        type: 'status',
        conversationId: options?.threadId ?? null,
        status,
      }),
    );
  }

  async disconnect(): Promise<void> {
    for (const ws of this.connections.values()) {
      ws.close();
    }
    this.connections.clear();
    this.wss.close();
    return new Promise((resolve) => {
      this.server.close(() => resolve());
    });
  }

  private handleHttp(req: http.IncomingMessage, res: http.ServerResponse): void {
    const url = new URL(req.url || '/', `http://${req.headers.host}`);
    const path = url.pathname;

    if (path === '/api/devbox/health' && req.method === 'GET') {
      this.jsonResponse(res, 200, { status: 'ok' });
      return;
    }

    const userId = req.headers['x-user-id'] as string | undefined;
    if (!userId) {
      this.jsonResponse(res, 401, { error: 'Missing X-User-Id header' });
      return;
    }

    const chatJid = `web:${userId}`;

    if (path === '/api/devbox/conversations' && req.method === 'POST') {
      this.readBody(req).then(() => {
        const conversationId = randomUUID();
        this.opts.onChatMetadata(chatJid, new Date().toISOString(), undefined, 'web', false);
        this.jsonResponse(res, 201, { conversationId });
      }).catch(() => this.jsonResponse(res, 400, { error: 'Invalid request body' }));
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

    const msgMatch = path.match(/^\/api\/devbox\/conversations\/([^/]+)\/messages$/);
    if (msgMatch) {
      const conversationId = msgMatch[1];

      if (req.method === 'POST') {
        this.readBody(req).then((body) => {
          if (!body.content || typeof body.content !== 'string') {
            this.jsonResponse(res, 400, { error: 'content is required' });
            return;
          }
          this.deliverMessage(userId, chatJid, conversationId, body.content);
          this.jsonResponse(res, 202, { queued: true });
        }).catch(() => this.jsonResponse(res, 400, { error: 'Invalid request body' }));
        return;
      }

      if (req.method === 'GET') {
        const before = url.searchParams.get('before') ?? undefined;
        const limit = parseInt(url.searchParams.get('limit') ?? '50', 10);
        const messages = getMessageHistory(chatJid, conversationId, { before, limit });
        this.jsonResponse(res, 200, { messages });
        return;
      }
    }

    const delMatch = path.match(/^\/api\/devbox\/conversations\/([^/]+)$/);
    if (delMatch && req.method === 'DELETE') {
      const conversationId = delMatch[1];
      this.deliverMessage(userId, chatJid, conversationId, '/done --force');
      this.jsonResponse(res, 200, { deleted: true });
      return;
    }

    this.jsonResponse(res, 404, { error: 'Not found' });
  }

  private handleWsMessage(userId: string, msg: any): void {
    if (msg.type === 'ping') {
      const ws = this.connections.get(userId);
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'pong' }));
      }
      return;
    }

    if (msg.type === 'message') {
      if (!msg.conversationId || !msg.content) {
        logger.warn({ userId }, 'Invalid WS message: missing conversationId or content');
        return;
      }
      const chatJid = `web:${userId}`;
      this.deliverMessage(userId, chatJid, msg.conversationId, msg.content);
      return;
    }

    logger.warn({ userId, type: msg.type }, 'Unknown WebSocket message type');
  }

  private deliverMessage(
    userId: string,
    chatJid: string,
    conversationId: string,
    content: string,
  ): void {
    const activeCount = this.opts.getActiveCount();
    if (activeCount >= MAX_CONCURRENT_CONTAINERS) {
      const ws = this.connections.get(userId);
      if (ws && ws.readyState === WebSocket.OPEN) {
        const waitingCount = this.opts.getWaitingCount();
        ws.send(
          JSON.stringify({
            type: 'error',
            conversationId,
            code: 'concurrency_limit',
            message: `System busy, your request is queued (${waitingCount} ahead)`,
          }),
        );
      }
    }

    // Resolve agent for this user JID (wildcard matching like Telegram DMs)
    if (!this.resolveAgentForChat(chatJid)) {
      logger.warn({ chatJid }, 'No agent registered for web user, dropping message');
      const ws = this.connections.get(userId);
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: 'error',
          conversationId,
          code: 'no_agent',
          message: 'No agent configured for web channel',
        }));
      }
      return;
    }

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

  private jsonResponse(res: http.ServerResponse, status: number, body: any): void {
    res.writeHead(status, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(body));
  }

  private readBody(req: http.IncomingMessage): Promise<any> {
    return new Promise((resolve, reject) => {
      let data = '';
      req.on('data', (chunk) => { data += chunk; });
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
