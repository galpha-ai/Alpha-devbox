import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

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
import { getMessageHistory } from '../db.js';
import type {
  OnInboundMessage,
  OnChatMetadata,
  RegisteredAgent,
} from '../types.js';

const mockedGetMessageHistory = vi.mocked(getMessageHistory);

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
    mockedGetMessageHistory.mockReset().mockReturnValue([]);
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

  it('POST /chat streams an AI SDK SSE reply from channel callbacks', async () => {
    const onMessage = vi.fn(() => {
      queueMicrotask(() => {
        void channel.sendMessage('web:user1', 'hello back', {
          threadId: 'conv-1',
        });
        void channel.setTyping?.('web:user1', 'success', {
          threadId: 'conv-1',
        });
      });
    });

    await channel.disconnect();
    channel = new WebChannel(0, makeOpts({ onMessage }));
    await channel.connect();
    port = channel.getPort();

    const res = await fetch(`http://localhost:${port}/api/devbox/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-User-Id': 'user1' },
      body: JSON.stringify({
        id: 'conv-1',
        messages: [
          {
            id: 'u1',
            role: 'user',
            parts: [{ type: 'text', text: 'hello agent' }],
          },
        ],
      }),
    });

    expect(res.status).toBe(200);
    expect(res.headers.get('content-type')).toContain('text/event-stream');

    const body = await res.text();
    expect(body).toContain('"type":"start"');
    expect(body).toContain('"type":"text-delta"');
    expect(body).toContain('hello back');
    expect(onMessage).toHaveBeenCalledTimes(1);
  });

  it('POST /chat emits an AI SDK error when no reply arrives', async () => {
    const onMessage = vi.fn(() => {
      queueMicrotask(() => {
        void channel.setTyping?.('web:user1', 'error', { threadId: 'conv-2' });
      });
    });

    await channel.disconnect();
    channel = new WebChannel(0, makeOpts({ onMessage }));
    await channel.connect();
    port = channel.getPort();

    const res = await fetch(`http://localhost:${port}/api/devbox/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-User-Id': 'user1' },
      body: JSON.stringify({
        id: 'conv-2',
        messages: [
          {
            id: 'u2',
            role: 'user',
            parts: [{ type: 'text', text: 'hello agent' }],
          },
        ],
      }),
    });

    expect(res.status).toBe(200);
    const body = await res.text();
    expect(body).toContain('"type":"error"');
    expect(body).toContain('The assistant failed before completing the reply.');
  });

  it('sendMessage is a no-op without an active AI SDK stream', async () => {
    await expect(
      channel.sendMessage('web:user1', 'agent reply', { threadId: 'conv-1' }),
    ).resolves.toBeUndefined();
  });
});
