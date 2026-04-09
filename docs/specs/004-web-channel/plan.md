# Web Channel Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add HTTP/WebSocket channel adapter so web frontends can have multi-conversation sessions with devbox agents, deployed behind the existing Envoy proxy on GKE.

**Architecture:** New `WebChannel` implements the existing `Channel` interface with an HTTP server for REST API + WebSocket for streaming. Each web conversation maps to a thread-scoped session (`channelId="web:{userId}"`, `threadId="{conversationId}"`), fully reusing the existing Controller session lifecycle. Auth is delegated to Envoy (JWT validation + `X-User-Id` header injection).

**Tech Stack:** Node.js `http` module (no framework), `ws` library for WebSocket, existing vitest for tests.

**Spec:** `docs/specs/004-web-channel/design.md`

---

### Task 1: Add `ws` dependency and config schema

**Files:**
- Modify: `package.json` — add `ws` + `@types/ws`
- Modify: `src/config.ts:87-119` — add `WebSchema` to `ConfigSchema`, export new constants

- [ ] **Step 1: Install ws dependency**

Run:
```bash
npm install ws && npm install --save-dev @types/ws
```

- [ ] **Step 2: Add WebSchema to config.ts**

In `src/config.ts`, add the schema definition before `ConfigSchema`:

```typescript
const WebSchema = z
  .object({
    enabled: z.boolean().default(false),
    port: z.number().int().positive().default(8080),
  })
  .optional();
```

Add `web: WebSchema` field to `ConfigSchema`:

```typescript
const ConfigSchema = z.object({
  // ... existing fields ...
  web: WebSchema,
});
```

Add exported mutable config values after the existing ones (near line 156):

```typescript
export let WEB_ENABLED = false;
export let WEB_PORT = 8080;
```

In `loadConfig()`, after the existing config parsing (after line 398), add:

```typescript
WEB_ENABLED = config.web?.enabled ?? false;
WEB_PORT = config.web?.port ?? 8080;
```

- [ ] **Step 3: Run typecheck**

Run: `npx tsc --noEmit`
Expected: No errors.

- [ ] **Step 4: Run existing tests to verify no regression**

Run: `npm test`
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add package.json package-lock.json src/config.ts
git commit -m "feat(web): add ws dependency and web config schema"
```

---

### Task 2: Add SessionQueue concurrency getters

**Files:**
- Modify: `src/session-queue.ts:30` — add `getActiveCount()` and `getWaitingCount()` methods
- Modify: `src/session-queue.test.ts` — add tests for new getters

- [ ] **Step 1: Write failing tests**

Add to the end of the `describe('SessionQueue', ...)` block in `src/session-queue.test.ts`:

```typescript
  describe('concurrency getters', () => {
    it('getActiveCount returns 0 when no sessions are active', () => {
      expect(queue.getActiveCount()).toBe(0);
    });

    it('getActiveCount reflects running sessions', async () => {
      let resolve1!: () => void;
      const blocker = new Promise<void>((r) => { resolve1 = r; });

      queue.setProcessMessagesFn(async () => {
        await blocker;
        return true;
      });
      queue.enqueueMessageCheck('session-1');
      // Let the microtask start
      await vi.advanceTimersByTimeAsync(0);

      expect(queue.getActiveCount()).toBe(1);

      resolve1();
      await vi.advanceTimersByTimeAsync(0);
    });

    it('getWaitingCount reflects queued sessions beyond concurrency limit', async () => {
      const blockers: Array<() => void> = [];
      queue.setProcessMessagesFn(async () => {
        await new Promise<void>((r) => blockers.push(r));
        return true;
      });

      // Fill up concurrency limit (2)
      queue.enqueueMessageCheck('session-1');
      queue.enqueueMessageCheck('session-2');
      await vi.advanceTimersByTimeAsync(0);

      // This one should be waiting
      queue.enqueueMessageCheck('session-3');
      await vi.advanceTimersByTimeAsync(0);

      expect(queue.getActiveCount()).toBe(2);
      expect(queue.getWaitingCount()).toBe(1);

      // Cleanup
      for (const r of blockers) r();
      await vi.advanceTimersByTimeAsync(0);
    });
  });
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npx vitest run src/session-queue.test.ts`
Expected: FAIL — `queue.getActiveCount is not a function`

- [ ] **Step 3: Implement getters**

Add to `SessionQueue` class in `src/session-queue.ts`, after the `isSessionActive` method (around line 448):

```typescript
  getActiveCount(): number {
    return this.activeCount;
  }

  getWaitingCount(): number {
    return this.waitingSessions.length;
  }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npx vitest run src/session-queue.test.ts`
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/session-queue.ts src/session-queue.test.ts
git commit -m "feat(web): add concurrency getters to SessionQueue"
```

---

### Task 3: Add `getSessionsByChannel` and `getMessageHistory` DB helpers

**Files:**
- Modify: `src/db.ts` — add two new query functions
- Modify: `src/db.test.ts` — add tests

- [ ] **Step 1: Write failing tests**

Add to the end of the test file `src/db.test.ts`. First check how the test file sets up the database — it likely calls `initDatabase()` in `beforeEach`. Add a new `describe` block:

```typescript
describe('web channel db helpers', () => {
  it('getSessionsByChannel returns sessions for a given channelId', () => {
    setSession('web:user1', 'conv-1', 'main', 'sid-1');
    setSession('web:user1', 'conv-2', 'main', 'sid-2');
    setSession('web:user2', 'conv-3', 'main', 'sid-3');

    const result = getSessionsByChannel('web:user1');
    expect(result).toHaveLength(2);
    expect(result.map((r) => r.threadId).sort()).toEqual(['conv-1', 'conv-2']);
    expect(result[0].agentName).toBe('main');
  });

  it('getSessionsByChannel returns empty array for unknown channel', () => {
    expect(getSessionsByChannel('web:nobody')).toEqual([]);
  });

  it('getMessageHistory returns messages in reverse chronological order with limit', () => {
    // Store test messages
    const base = { chat_jid: 'web:user1', sender: 'u1', sender_name: 'User', is_from_me: false, is_bot_message: false };
    storeMessage({ ...base, id: 'm1', thread_id: 'conv-1', content: 'first', timestamp: '2026-01-01T00:00:01Z' });
    storeMessage({ ...base, id: 'm2', thread_id: 'conv-1', content: 'second', timestamp: '2026-01-01T00:00:02Z' });
    storeMessage({ ...base, id: 'm3', thread_id: 'conv-1', content: 'third', timestamp: '2026-01-01T00:00:03Z' });

    const result = getMessageHistory('web:user1', 'conv-1', { limit: 2 });
    expect(result).toHaveLength(2);
    // Most recent first
    expect(result[0].id).toBe('m3');
    expect(result[1].id).toBe('m2');
  });

  it('getMessageHistory supports before cursor', () => {
    const base = { chat_jid: 'web:user1', sender: 'u1', sender_name: 'User', is_from_me: false, is_bot_message: false };
    storeMessage({ ...base, id: 'm1', thread_id: 'conv-1', content: 'first', timestamp: '2026-01-01T00:00:01Z' });
    storeMessage({ ...base, id: 'm2', thread_id: 'conv-1', content: 'second', timestamp: '2026-01-01T00:00:02Z' });
    storeMessage({ ...base, id: 'm3', thread_id: 'conv-1', content: 'third', timestamp: '2026-01-01T00:00:03Z' });

    const result = getMessageHistory('web:user1', 'conv-1', { before: '2026-01-01T00:00:03Z', limit: 10 });
    expect(result).toHaveLength(2);
    expect(result[0].id).toBe('m2');
    expect(result[1].id).toBe('m1');
  });
});
```

Make sure to import the new functions at the top of the test file:

```typescript
import { getSessionsByChannel, getMessageHistory } from './db.js';
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npx vitest run src/db.test.ts`
Expected: FAIL — cannot import `getSessionsByChannel`

- [ ] **Step 3: Implement the DB helpers**

Add to `src/db.ts`, after the `getAllSessions` function (around line 778):

```typescript
export function getSessionsByChannel(
  channelId: string,
): Array<{ threadId: string; agentName: string; sessionId: string }> {
  const rows = db
    .prepare(
      `SELECT thread_id, agent_name, session_id FROM sessions WHERE channel_id = ? AND thread_id != ''`,
    )
    .all(channelId) as Array<{
    thread_id: string;
    agent_name: string;
    session_id: string;
  }>;
  return rows.map((row) => ({
    threadId: row.thread_id,
    agentName: row.agent_name,
    sessionId: row.session_id,
  }));
}

export function getMessageHistory(
  chatJid: string,
  threadId: string,
  options: { before?: string; limit?: number } = {},
): NewMessage[] {
  const limit = options.limit ?? 50;
  const normalized = normalizeThreadId(threadId);

  if (options.before) {
    const rows = db
      .prepare(
        `SELECT id, chat_jid, thread_id, sender, sender_name, content, timestamp, is_bot_message
         FROM messages
         WHERE chat_jid = ? AND thread_id = ? AND timestamp < ?
         ORDER BY timestamp DESC
         LIMIT ?`,
      )
      .all(chatJid, normalized, options.before, limit) as Array<
      NewMessage & { thread_id: string }
    >;
    return rows.map((row) => ({ ...row, thread_id: row.thread_id || null }));
  }

  const rows = db
    .prepare(
      `SELECT id, chat_jid, thread_id, sender, sender_name, content, timestamp, is_bot_message
       FROM messages
       WHERE chat_jid = ? AND thread_id = ?
       ORDER BY timestamp DESC
       LIMIT ?`,
    )
    .all(chatJid, normalized, limit) as Array<
    NewMessage & { thread_id: string }
  >;
  return rows.map((row) => ({ ...row, thread_id: row.thread_id || null }));
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npx vitest run src/db.test.ts`
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/db.ts src/db.test.ts
git commit -m "feat(web): add getSessionsByChannel and getMessageHistory db helpers"
```

---

### Task 4: Implement WebChannel

**Files:**
- Create: `src/channels/web.ts`
- Create: `src/channels/web.test.ts`

- [ ] **Step 1: Write the test file**

Create `src/channels/web.test.ts`:

```typescript
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import http from 'http';
import { WebSocket } from 'ws';

vi.mock('../config.js', () => ({
  ASSISTANT_NAME: 'Devbox',
  WEB_PORT: 0, // random port for tests
  MAX_CONCURRENT_CONTAINERS: 2,
}));

vi.mock('../logger.js', () => ({
  logger: {
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  },
}));

vi.mock('../db.js', () => ({
  getSessionsByChannel: vi.fn().mockReturnValue([]),
  getMessageHistory: vi.fn().mockReturnValue([]),
  storeMessage: vi.fn(),
  storeChatMetadata: vi.fn(),
}));

import { WebChannel } from './web.js';
import type { OnInboundMessage, OnChatMetadata, RegisteredAgent } from '../types.js';

function makeOpts(overrides: Partial<{
  onMessage: OnInboundMessage;
  onChatMetadata: OnChatMetadata;
  registeredAgents: () => Record<string, RegisteredAgent>;
  getActiveCount: () => number;
  getWaitingCount: () => number;
}> = {}) {
  return {
    onMessage: overrides.onMessage ?? vi.fn(),
    onChatMetadata: overrides.onChatMetadata ?? vi.fn(),
    registeredAgents: overrides.registeredAgents ?? (() => ({
      'web:*': {
        name: 'main',
        agentName: 'main',
        trigger: '@Devbox',
        added_at: new Date().toISOString(),
        requiresTrigger: false,
      },
    })),
    getActiveCount: overrides.getActiveCount ?? (() => 0),
    getWaitingCount: overrides.getWaitingCount ?? (() => 0),
  };
}

describe('WebChannel', () => {
  let channel: WebChannel;
  let port: number;

  beforeEach(async () => {
    channel = new WebChannel(0, makeOpts());
    await channel.connect();
    port = channel.getPort();
  });

  afterEach(async () => {
    await channel.disconnect();
  });

  it('ownsJid matches web: prefix', () => {
    expect(channel.ownsJid('web:user1')).toBe(true);
    expect(channel.ownsJid('tg:123')).toBe(false);
    expect(channel.ownsJid('slack:C123')).toBe(false);
  });

  it('health endpoint returns 200', async () => {
    const res = await fetch(`http://localhost:${port}/api/devbox/health`);
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body.status).toBe('ok');
  });

  it('rejects requests without X-User-Id', async () => {
    const res = await fetch(`http://localhost:${port}/api/devbox/conversations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
    expect(res.status).toBe(401);
  });

  it('POST /conversations creates a conversation', async () => {
    const res = await fetch(`http://localhost:${port}/api/devbox/conversations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-User-Id': 'user1' },
      body: JSON.stringify({}),
    });
    expect(res.status).toBe(201);
    const body = await res.json();
    expect(body.conversationId).toBeDefined();
    expect(typeof body.conversationId).toBe('string');
  });

  it('POST /conversations/:id/messages calls onMessage', async () => {
    const onMessage = vi.fn();
    await channel.disconnect();
    channel = new WebChannel(0, makeOpts({ onMessage }));
    await channel.connect();
    port = channel.getPort();

    const res = await fetch(`http://localhost:${port}/api/devbox/conversations/conv-1/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-User-Id': 'user1' },
      body: JSON.stringify({ content: 'hello agent' }),
    });
    expect(res.status).toBe(202);
    expect(onMessage).toHaveBeenCalledTimes(1);

    const call = onMessage.mock.calls[0];
    expect(call[0]).toBe('web:user1');
    expect(call[1].content).toBe('hello agent');
    expect(call[1].thread_id).toBe('conv-1');
    expect(call[1].chat_jid).toBe('web:user1');
  });

  it('sendMessage delivers to connected WebSocket', async () => {
    const ws = new WebSocket(`ws://localhost:${port}/api/devbox/ws`, {
      headers: { 'X-User-Id': 'user1' },
    });
    await new Promise<void>((resolve) => ws.on('open', resolve));

    const messagePromise = new Promise<any>((resolve) => {
      ws.on('message', (data) => resolve(JSON.parse(data.toString())));
    });

    await channel.sendMessage('web:user1', 'agent reply', { threadId: 'conv-1' });

    const msg = await messagePromise;
    expect(msg.type).toBe('output');
    expect(msg.conversationId).toBe('conv-1');
    expect(msg.content).toBe('agent reply');

    ws.close();
  });

  it('setTyping sends status message via WebSocket', async () => {
    const ws = new WebSocket(`ws://localhost:${port}/api/devbox/ws`, {
      headers: { 'X-User-Id': 'user1' },
    });
    await new Promise<void>((resolve) => ws.on('open', resolve));

    const messagePromise = new Promise<any>((resolve) => {
      ws.on('message', (data) => resolve(JSON.parse(data.toString())));
    });

    await channel.setTyping!('web:user1', 'processing', { threadId: 'conv-1' });

    const msg = await messagePromise;
    expect(msg.type).toBe('status');
    expect(msg.status).toBe('processing');

    ws.close();
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npx vitest run src/channels/web.test.ts`
Expected: FAIL — cannot import `WebChannel`

- [ ] **Step 3: Implement WebChannel**

Create `src/channels/web.ts`:

```typescript
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

  // --- HTTP routing ---

  private handleHttp(req: http.IncomingMessage, res: http.ServerResponse): void {
    const url = new URL(req.url || '/', `http://${req.headers.host}`);
    const path = url.pathname;

    // Health check — no auth required
    if (path === '/api/devbox/health' && req.method === 'GET') {
      this.jsonResponse(res, 200, { status: 'ok' });
      return;
    }

    // All other routes require X-User-Id
    const userId = req.headers['x-user-id'] as string | undefined;
    if (!userId) {
      this.jsonResponse(res, 401, { error: 'Missing X-User-Id header' });
      return;
    }

    const chatJid = `web:${userId}`;

    // POST /api/devbox/conversations
    if (path === '/api/devbox/conversations' && req.method === 'POST') {
      this.readBody(req).then((body) => {
        const conversationId = randomUUID();
        this.opts.onChatMetadata(chatJid, new Date().toISOString(), undefined, 'web', false);
        this.jsonResponse(res, 201, { conversationId });
      }).catch(() => this.jsonResponse(res, 400, { error: 'Invalid request body' }));
      return;
    }

    // GET /api/devbox/conversations
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

    // Match /api/devbox/conversations/:id/messages
    const msgMatch = path.match(/^\/api\/devbox\/conversations\/([^/]+)\/messages$/);
    if (msgMatch) {
      const conversationId = msgMatch[1];

      // POST — send message
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

      // GET — message history
      if (req.method === 'GET') {
        const before = url.searchParams.get('before') ?? undefined;
        const limit = parseInt(url.searchParams.get('limit') ?? '50', 10);
        const messages = getMessageHistory(chatJid, conversationId, { before, limit });
        this.jsonResponse(res, 200, { messages });
        return;
      }
    }

    // DELETE /api/devbox/conversations/:id
    const delMatch = path.match(/^\/api\/devbox\/conversations\/([^/]+)$/);
    if (delMatch && req.method === 'DELETE') {
      // The actual cleanup is handled by the controller's session-control logic.
      // We deliver a /done --force command as a message so it goes through
      // the existing session control pipeline.
      const conversationId = delMatch[1];
      this.deliverMessage(userId, chatJid, conversationId, '/done --force');
      this.jsonResponse(res, 200, { deleted: true });
      return;
    }

    this.jsonResponse(res, 404, { error: 'Not found' });
  }

  // --- WebSocket message handling ---

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

  // --- Shared helpers ---

  private deliverMessage(
    userId: string,
    chatJid: string,
    conversationId: string,
    content: string,
  ): void {
    // Send concurrency limit notification if applicable
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npx vitest run src/channels/web.test.ts`
Expected: All tests pass.

- [ ] **Step 5: Run full test suite**

Run: `npm test`
Expected: All tests pass (no regressions).

- [ ] **Step 6: Commit**

```bash
git add src/channels/web.ts src/channels/web.test.ts
git commit -m "feat(web): implement WebChannel with HTTP REST + WebSocket"
```

---

### Task 5: Wire WebChannel into Controller

**Files:**
- Modify: `src/index.ts:1130-1156` — add web channel initialization

- [ ] **Step 1: Add imports**

At the top of `src/index.ts`, add:

```typescript
import { WebChannel } from './channels/web.js';
import { WEB_ENABLED, WEB_PORT } from './config.js';
```

- [ ] **Step 2: Add WebChannel initialization**

In `src/index.ts`, in the `main()` function, after the Slack channel initialization block (after line 1150), add:

```typescript
  const wantsWeb = WEB_ENABLED || configuredJids.some((jid) => jid.startsWith('web:'));

  if (wantsWeb) {
    channels.push(
      new WebChannel(WEB_PORT, {
        ...channelOpts,
        getActiveCount: () => queue.getActiveCount(),
        getWaitingCount: () => queue.getWaitingCount(),
      }),
    );
  }
```

- [ ] **Step 3: Update the empty channels check**

Change the error message on line 1152-1156 from:

```typescript
  if (channels.length === 0) {
    throw new Error(
      'No channels were initialized. Configure tg:* or slack:* channel bindings.',
    );
  }
```

To:

```typescript
  if (channels.length === 0) {
    throw new Error(
      'No channels were initialized. Configure tg:*, slack:*, or web:* channel bindings.',
    );
  }
```

- [ ] **Step 4: Run typecheck**

Run: `npx tsc --noEmit`
Expected: No errors.

- [ ] **Step 5: Run full test suite**

Run: `npm test`
Expected: All tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/index.ts
git commit -m "feat(web): wire WebChannel into controller startup"
```

---

### Task 6: K8s deployment — Service, ports, probes

**Files:**
- Create: `k8s/base/service.yaml`
- Modify: `k8s/base/deployment.yaml` — add port + probes
- Modify: `k8s/base/kustomization.yaml` — add service.yaml to resources

- [ ] **Step 1: Create Service resource**

Create `k8s/base/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: devbox-agent
spec:
  ports:
    - name: http
      port: 80
      targetPort: 8080
```

Note: the `app: devbox-agent` selector label is applied automatically by kustomization.yaml's `labels` config.

- [ ] **Step 2: Add port and probes to deployment**

In `k8s/base/deployment.yaml`, add to the `devbox-controller` container spec, after the `image` line (around line 27):

```yaml
          ports:
            - name: http
              containerPort: 8080
          livenessProbe:
            httpGet:
              path: /api/devbox/health
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /api/devbox/health
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
```

- [ ] **Step 3: Add service.yaml to kustomization**

In `k8s/base/kustomization.yaml`, add `service.yaml` to the `resources` list:

```yaml
resources:
  - serviceaccount-controller.yaml
  - serviceaccount-runner.yaml
  - role.yaml
  - rolebinding.yaml
  - clusterrole-runner.yaml
  - clusterrolebinding-runner.yaml
  - pvc.yaml
  - deployment.yaml
  - service.yaml
```

- [ ] **Step 4: Validate kustomize build**

Run: `kubectl kustomize k8s/base/`
Expected: Valid YAML output including the Service resource with proper labels.

If `kubectl` is not available locally, run: `npx kustomize build k8s/base/` or just visually verify the YAML is correct.

- [ ] **Step 5: Commit**

```bash
git add k8s/base/service.yaml k8s/base/deployment.yaml k8s/base/kustomization.yaml
git commit -m "feat(web): add K8s Service, port, and health probes"
```

---

### Task 7: Staging config — enable web channel

**Files:**
- Modify: `k8s/overlays/staging/config.staging.yaml` — add web config + web:* channel

- [ ] **Step 1: Update staging config**

In `k8s/overlays/staging/config.staging.yaml`, add `web` section and the `web:*` channel binding.

Add after the `container` section (after line 14):

```yaml
web:
  enabled: true
  port: 8080
```

Add to the `channels` list (after the existing Slack channels):

```yaml
  - id: "web:*"
    agents:
      - name: main
        requires_trigger: false
```

The full file should look like:

```yaml
assistant_name: Devbox

container:
  runtime: kubernetes
  image: your-registry/devbox-runner:latest
  timeout: 5400000
  idle_timeout: 300000
  max_concurrent: 2
  max_output_size: 10485760
  kubernetes:
    namespace: devbox-agent-staging
    pvc_name: devbox-data
    data_mount_path: /data/devbox-agent
    service_account: devbox-runner

web:
  enabled: true
  port: 8080

agents:
  - name: main
    path: agents/quant-dev
  - name: example
    path: agents/example

channels:
  - id: "slack:C0AJYNBU6KT"
    agents:
      - name: main
        trigger: "@Devbox"
        requires_trigger: true
  - id: "slack:C0ALREB53JM"
    agents:
      - name: example
        trigger: "@Devbox"
        requires_trigger: true
  - id: "web:*"
    agents:
      - name: main
        requires_trigger: false
```

- [ ] **Step 2: Validate staging kustomize build**

Run: `kubectl kustomize k8s/overlays/staging/`
Expected: Valid YAML with the updated ConfigMap containing web config.

- [ ] **Step 3: Commit**

```bash
git add k8s/overlays/staging/config.staging.yaml
git commit -m "feat(web): enable web channel in staging config"
```

---

### Task 8: Update architecture docs

**Files:**
- Modify: `docs/architecture.md` — add WebChannel to codemap, config example, and data layout

- [ ] **Step 1: Add WebChannel to codemap**

In `docs/architecture.md`, in the `### Controller (src/)` section, add after the Telegram channel entry:

```markdown
- `channels/web.ts`: Web adapter using HTTP + WebSocket. Exposes REST API for conversation CRUD and message history, plus a single-connection-per-user WebSocket for streaming agent output and status. Auth is delegated to the upstream Envoy proxy (`X-User-Id` header). Implements the `Channel` interface.
```

- [ ] **Step 2: Update config example**

In the `## Config Structure` section, add the `web` section to the example config:

```yaml
web:
  enabled: true
  port: 8080                # HTTP + WebSocket listen port
```

And add a web channel example to the `channels` list:

```yaml
  - id: 'web:*'              # Web frontend wildcard
    agents:
      - name: main
        requires_trigger: false
```

- [ ] **Step 3: Commit**

```bash
git add docs/architecture.md
git commit -m "docs: add web channel to architecture codemap"
```
