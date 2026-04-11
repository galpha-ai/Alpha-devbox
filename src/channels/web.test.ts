import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import http from 'http';
import { WebSocket } from 'ws';

vi.mock('../config.js', () => ({
  ASSISTANT_NAME: 'Devbox',
  WEB_PORT: 0,
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
import type {
  OnInboundMessage,
  OnChatMetadata,
  RegisteredAgent,
} from '../types.js';

function makeOpts(
  overrides: Partial<{
    onMessage: OnInboundMessage;
    onChatMetadata: OnChatMetadata;
    registeredAgents: () => Record<string, RegisteredAgent>;
    getActiveCount: () => number;
    getWaitingCount: () => number;
  }> = {},
) {
  return {
    onMessage: overrides.onMessage ?? vi.fn(),
    onChatMetadata: overrides.onChatMetadata ?? vi.fn(),
    registeredAgents:
      overrides.registeredAgents ??
      (() => ({
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
    const body = (await res.json()) as any;
    expect(body.status).toBe('ok');
  });

  it('rejects requests without X-User-Id', async () => {
    const res = await fetch(
      `http://localhost:${port}/api/devbox/conversations`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      },
    );
    expect(res.status).toBe(401);
  });

  it('POST /conversations creates a conversation', async () => {
    const res = await fetch(
      `http://localhost:${port}/api/devbox/conversations`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-User-Id': 'user1' },
        body: JSON.stringify({}),
      },
    );
    expect(res.status).toBe(201);
    const body = (await res.json()) as any;
    expect(body.conversationId).toBeDefined();
    expect(typeof body.conversationId).toBe('string');
  });

  it('POST /conversations/:id/messages calls onMessage', async () => {
    const onMessage = vi.fn();
    await channel.disconnect();
    channel = new WebChannel(0, makeOpts({ onMessage }));
    await channel.connect();
    port = channel.getPort();

    const res = await fetch(
      `http://localhost:${port}/api/devbox/conversations/conv-1/messages`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-User-Id': 'user1' },
        body: JSON.stringify({ content: 'hello agent' }),
      },
    );
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

    await channel.sendMessage('web:user1', 'agent reply', {
      threadId: 'conv-1',
    });

    const msg = await messagePromise;
    expect(msg.type).toBe('output');
    expect(msg.conversationId).toBe('conv-1');
    expect(msg.content).toBe('agent reply');

    ws.close();
  });

  it('accepts browser-safe WebSocket auth via query param', async () => {
    const ws = new WebSocket(
      `ws://localhost:${port}/api/devbox/ws?userId=user1`,
    );
    await new Promise<void>((resolve) => ws.on('open', resolve));

    const messagePromise = new Promise<any>((resolve) => {
      ws.on('message', (data) => resolve(JSON.parse(data.toString())));
    });

    await channel.sendMessage('web:user1', 'agent reply', {
      threadId: 'conv-1',
    });

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
