import fs from 'fs';

import { beforeEach, describe, expect, it, vi } from 'vitest';

const { findChannelMock, runContainerAgentMock } = vi.hoisted(() => ({
  findChannelMock: vi.fn(),
  runContainerAgentMock: vi.fn(),
}));

vi.mock('./router.js', async () => {
  const actual =
    await vi.importActual<typeof import('./router.js')>('./router.js');
  return {
    ...actual,
    findChannel: findChannelMock,
  };
});

vi.mock('./container-runner.js', () => ({
  runContainerAgent: runContainerAgentMock,
  writeGroupsSnapshot: vi.fn(),
  writeTasksSnapshot: vi.fn(),
}));

vi.mock('./logger.js', () => ({
  logger: {
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    fatal: vi.fn(),
  },
}));

import {
  _initTestDatabase,
  getMessageHistory,
  makeSessionScopeKey,
  storeChatMetadata,
  storeMessage,
} from './db.js';
import {
  _setContainerRuntimeForTesting,
  _setRegisteredAgents,
  processSessionMessages,
} from './index.js';
import type { Channel } from './types.js';

describe('processSessionMessages', () => {
  beforeEach(() => {
    _initTestDatabase();
    _setRegisteredAgents({});
    _setContainerRuntimeForTesting({} as any);
    findChannelMock.mockReset();
    runContainerAgentMock.mockReset();
  });

  it('emits success for each completed turn on a reused session container', async () => {
    vi.spyOn(fs, 'existsSync').mockReturnValue(true);

    const setTyping = vi.fn(async () => undefined);
    const sendMessage = vi.fn(async () => undefined);
    const channel: Channel = {
      name: 'web',
      connect: vi.fn(async () => undefined),
      sendMessage,
      isConnected: () => true,
      ownsJid: (jid) => jid.startsWith('web:'),
      disconnect: vi.fn(async () => undefined),
      setTyping,
    };
    findChannelMock.mockReturnValue(channel);

    _setRegisteredAgents({
      'web:user1': {
        name: 'main',
        agentName: 'main',
        trigger: '@Devbox',
        added_at: '2026-04-14T00:00:00.000Z',
        requiresTrigger: false,
      },
    });

    storeChatMetadata(
      'web:user1',
      '2026-04-14T00:00:00.000Z',
      'User One',
      'web',
      false,
    );
    storeMessage({
      id: 'u1',
      chat_jid: 'web:user1',
      thread_id: 'conv-1',
      sender: 'user1',
      sender_name: 'User One',
      content: 'First turn',
      timestamp: '2026-04-14T00:00:00.000Z',
      is_from_me: false,
      is_bot_message: false,
    });

    runContainerAgentMock.mockImplementation(
      async (
        _runtime,
        _agent,
        _input,
        _registerProcess,
        onOutput?: (output: {
          status: 'success' | 'error';
          result: string | null;
          newSessionId?: string;
        }) => Promise<void>,
      ) => {
        await onOutput?.({
          status: 'success',
          result: 'alpha one',
          newSessionId: 'session-1',
        });
        await onOutput?.({
          status: 'success',
          result: 'alpha two',
          newSessionId: 'session-1',
        });
        return {
          status: 'success',
          result: null,
          newSessionId: 'session-1',
        };
      },
    );

    const sessionKey = makeSessionScopeKey('web:user1', 'conv-1', 'main');

    await expect(processSessionMessages(sessionKey)).resolves.toBe(true);

    expect(setTyping).toHaveBeenNthCalledWith(1, 'web:user1', 'processing', {
      messageId: 'u1',
      threadId: 'conv-1',
    });
    expect(setTyping).toHaveBeenNthCalledWith(2, 'web:user1', 'success', {
      messageId: 'u1',
      threadId: 'conv-1',
    });
    expect(setTyping).toHaveBeenNthCalledWith(3, 'web:user1', 'success', {
      messageId: 'u1',
      threadId: 'conv-1',
    });
    expect(sendMessage).toHaveBeenCalledTimes(2);
  });

  it('stores raw structured content but sends plain text to text-first channels', async () => {
    vi.spyOn(fs, 'existsSync').mockReturnValue(true);

    const sendMessage = vi.fn(async () => undefined);
    const channel: Channel = {
      name: 'slack',
      connect: vi.fn(async () => undefined),
      sendMessage,
      isConnected: () => true,
      ownsJid: (jid) => jid.startsWith('slack:'),
      disconnect: vi.fn(async () => undefined),
      setTyping: vi.fn(async () => undefined),
    };
    findChannelMock.mockReturnValue(channel);

    _setRegisteredAgents({
      'slack:C1': {
        name: 'main',
        agentName: 'main',
        trigger: '@Devbox',
        added_at: '2026-04-14T00:00:00.000Z',
        requiresTrigger: false,
      },
    });

    storeChatMetadata(
      'slack:C1',
      '2026-04-14T00:00:00.000Z',
      'Slack Room',
      'slack',
      true,
    );
    storeMessage({
      id: 'u1',
      chat_jid: 'slack:C1',
      thread_id: 'thread-1',
      sender: 'user1',
      sender_name: 'User One',
      content: 'Show me a chart',
      timestamp: '2026-04-14T00:00:00.000Z',
      is_from_me: false,
      is_bot_message: false,
    });

    runContainerAgentMock.mockImplementation(
      async (_runtime, _agent, _input, _registerProcess, onOutput) => {
        await onOutput?.({
          status: 'success',
          result:
            'Visible answer\n<<<CHART_V1>>>{\"series\":[]}\n<<<END_CHART_V1>>>',
          newSessionId: 'session-1',
        });
        return {
          status: 'success',
          result: null,
          newSessionId: 'session-1',
        };
      },
    );

    const sessionKey = makeSessionScopeKey('slack:C1', 'thread-1', 'main');

    await expect(processSessionMessages(sessionKey)).resolves.toBe(true);

    const history = getMessageHistory('slack:C1', 'thread-1');
    const assistantReply = history.find(
      (message: any) => message.is_bot_message,
    );
    expect(assistantReply?.content).toContain('<<<CHART_V1>>>');
    expect(sendMessage).toHaveBeenCalledWith(
      'slack:C1',
      expect.stringContaining('Visible answer'),
      expect.objectContaining({ threadId: 'thread-1' }),
    );
    const calls = sendMessage.mock.calls as any[][];
    const deliveredText = calls[0]?.[1] as string | undefined;
    expect(deliveredText).not.toContain('<<<CHART_V1>>>');
  });
});
