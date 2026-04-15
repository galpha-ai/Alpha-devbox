import { describe, it, expect, beforeEach } from 'vitest';

import {
  _initTestDatabase,
  createTask,
  deleteTask,
  getAllChats,
  getMessagesSince,
  getNewMessages,
  getAllRegisteredAgents,
  getTaskById,
  setRegisteredAgent,
  setSession,
  storeChatMetadata,
  storeMessage,
  updateTask,
  getSessionsByChannel,
  getMessageHistory,
  getOrCreateReplayLink,
  getReplayLinkById,
} from './db.js';

beforeEach(() => {
  _initTestDatabase();
});

// Helper to store a message using the normalized NewMessage interface
function store(overrides: {
  id: string;
  chat_jid: string;
  sender: string;
  sender_name: string;
  content: string;
  timestamp: string;
  is_from_me?: boolean;
}) {
  storeMessage({
    id: overrides.id,
    chat_jid: overrides.chat_jid,
    sender: overrides.sender,
    sender_name: overrides.sender_name,
    content: overrides.content,
    timestamp: overrides.timestamp,
    is_from_me: overrides.is_from_me ?? false,
  });
}

// --- storeMessage (NewMessage format) ---

describe('storeMessage', () => {
  it('stores a message and retrieves it', () => {
    storeChatMetadata('group@g.us', '2024-01-01T00:00:00.000Z');

    store({
      id: 'msg-1',
      chat_jid: 'group@g.us',
      sender: '123@s.whatsapp.net',
      sender_name: 'Alice',
      content: 'hello world',
      timestamp: '2024-01-01T00:00:01.000Z',
    });

    const messages = getMessagesSince(
      'group@g.us',
      '2024-01-01T00:00:00.000Z',
      'Andy',
    );
    expect(messages).toHaveLength(1);
    expect(messages[0].id).toBe('msg-1');
    expect(messages[0].sender).toBe('123@s.whatsapp.net');
    expect(messages[0].sender_name).toBe('Alice');
    expect(messages[0].content).toBe('hello world');
  });

  it('filters out empty content', () => {
    storeChatMetadata('group@g.us', '2024-01-01T00:00:00.000Z');

    store({
      id: 'msg-2',
      chat_jid: 'group@g.us',
      sender: '111@s.whatsapp.net',
      sender_name: 'Dave',
      content: '',
      timestamp: '2024-01-01T00:00:04.000Z',
    });

    const messages = getMessagesSince(
      'group@g.us',
      '2024-01-01T00:00:00.000Z',
      'Andy',
    );
    expect(messages).toHaveLength(0);
  });

  it('stores is_from_me flag', () => {
    storeChatMetadata('group@g.us', '2024-01-01T00:00:00.000Z');

    store({
      id: 'msg-3',
      chat_jid: 'group@g.us',
      sender: 'me@s.whatsapp.net',
      sender_name: 'Me',
      content: 'my message',
      timestamp: '2024-01-01T00:00:05.000Z',
      is_from_me: true,
    });

    // Message is stored (we can retrieve it — is_from_me doesn't affect retrieval)
    const messages = getMessagesSince(
      'group@g.us',
      '2024-01-01T00:00:00.000Z',
      'Andy',
    );
    expect(messages).toHaveLength(1);
  });

  it('upserts on duplicate id+chat_jid', () => {
    storeChatMetadata('group@g.us', '2024-01-01T00:00:00.000Z');

    store({
      id: 'msg-dup',
      chat_jid: 'group@g.us',
      sender: '123@s.whatsapp.net',
      sender_name: 'Alice',
      content: 'original',
      timestamp: '2024-01-01T00:00:01.000Z',
    });

    store({
      id: 'msg-dup',
      chat_jid: 'group@g.us',
      sender: '123@s.whatsapp.net',
      sender_name: 'Alice',
      content: 'updated',
      timestamp: '2024-01-01T00:00:01.000Z',
    });

    const messages = getMessagesSince(
      'group@g.us',
      '2024-01-01T00:00:00.000Z',
      'Andy',
    );
    expect(messages).toHaveLength(1);
    expect(messages[0].content).toBe('updated');
  });
});

describe('replay links', () => {
  it('returns stable replay links for the same scope', () => {
    const first = getOrCreateReplayLink('slack:C123', 'thread-1', 'main');
    const second = getOrCreateReplayLink('slack:C123', 'thread-1', 'main');

    expect(first.replayId).toBe(second.replayId);
    expect(first.replayId).toMatch(/^rpl_[a-f0-9]{32}$/);
  });

  it('looks up replay links by replay id', () => {
    const created = getOrCreateReplayLink('tg:user:123', null, 'main');

    expect(getReplayLinkById(created.replayId)).toEqual(created);
  });
});

// --- getMessagesSince ---

describe('getMessagesSince', () => {
  beforeEach(() => {
    storeChatMetadata('group@g.us', '2024-01-01T00:00:00.000Z');

    store({
      id: 'm1',
      chat_jid: 'group@g.us',
      sender: 'Alice@s.whatsapp.net',
      sender_name: 'Alice',
      content: 'first',
      timestamp: '2024-01-01T00:00:01.000Z',
    });
    store({
      id: 'm2',
      chat_jid: 'group@g.us',
      sender: 'Bob@s.whatsapp.net',
      sender_name: 'Bob',
      content: 'second',
      timestamp: '2024-01-01T00:00:02.000Z',
    });
    storeMessage({
      id: 'm3',
      chat_jid: 'group@g.us',
      sender: 'Bot@s.whatsapp.net',
      sender_name: 'Bot',
      content: 'bot reply',
      timestamp: '2024-01-01T00:00:03.000Z',
      is_bot_message: true,
    });
    store({
      id: 'm4',
      chat_jid: 'group@g.us',
      sender: 'Carol@s.whatsapp.net',
      sender_name: 'Carol',
      content: 'third',
      timestamp: '2024-01-01T00:00:04.000Z',
    });
  });

  it('returns messages after the given timestamp', () => {
    const msgs = getMessagesSince(
      'group@g.us',
      '2024-01-01T00:00:02.000Z',
      'Andy',
    );
    // Should exclude m1, m2 (before/at timestamp), m3 (bot message)
    expect(msgs).toHaveLength(1);
    expect(msgs[0].content).toBe('third');
  });

  it('excludes bot messages via is_bot_message flag', () => {
    const msgs = getMessagesSince(
      'group@g.us',
      '2024-01-01T00:00:00.000Z',
      'Andy',
    );
    const botMsgs = msgs.filter((m) => m.content === 'bot reply');
    expect(botMsgs).toHaveLength(0);
  });

  it('returns all non-bot messages when sinceTimestamp is empty', () => {
    const msgs = getMessagesSince('group@g.us', '', 'Andy');
    // 3 user messages (bot message excluded)
    expect(msgs).toHaveLength(3);
  });

  it('includes thread parent message when querying a thread', () => {
    storeChatMetadata('slack:C123', '2024-01-01T00:00:00.000Z');

    // Parent message (no thread_id, its own id is the thread root)
    storeMessage({
      id: '1700000000.000100',
      chat_jid: 'slack:C123',
      sender: 'U123',
      sender_name: 'Alice',
      content: 'add clickhouse env var support',
      timestamp: '2024-01-01T00:00:10.000Z',
      // no thread_id — this is the parent
    });
    // Thread reply
    storeMessage({
      id: '1700000001.000200',
      chat_jid: 'slack:C123',
      thread_id: '1700000000.000100',
      sender: 'U123',
      sender_name: 'Alice',
      content: '@Devbox explore and give me a plan',
      timestamp: '2024-01-01T00:00:11.000Z',
    });

    const msgs = getMessagesSince(
      'slack:C123',
      '2024-01-01T00:00:00.000Z',
      'Devbox',
      '1700000000.000100', // thread_id = parent ts
      { includeThreadParent: true },
    );

    expect(msgs).toHaveLength(2);
    expect(msgs[0].content).toBe('add clickhouse env var support');
    expect(msgs[1].content).toBe('@Devbox explore and give me a plan');
  });

  it('omits thread parent message for resumed thread fetches', () => {
    storeChatMetadata('slack:C123', '2024-01-01T00:00:00.000Z');

    storeMessage({
      id: '1700000000.000100',
      chat_jid: 'slack:C123',
      sender: 'U123',
      sender_name: 'Alice',
      content: 'add clickhouse env var support',
      timestamp: '2024-01-01T00:00:10.000Z',
    });
    storeMessage({
      id: '1700000001.000200',
      chat_jid: 'slack:C123',
      thread_id: '1700000000.000100',
      sender: 'U123',
      sender_name: 'Alice',
      content: '@Devbox explore and give me a plan',
      timestamp: '2024-01-01T00:00:11.000Z',
    });
    storeMessage({
      id: '1700000002.000300',
      chat_jid: 'slack:C123',
      thread_id: '1700000000.000100',
      sender: 'U123',
      sender_name: 'Alice',
      content: 'one more follow-up',
      timestamp: '2024-01-01T00:00:12.000Z',
    });

    const msgs = getMessagesSince(
      'slack:C123',
      '2024-01-01T00:00:11.000Z',
      'Devbox',
      '1700000000.000100',
    );

    expect(msgs).toHaveLength(1);
    expect(msgs[0].content).toBe('one more follow-up');
  });

  it('filters pre-migration bot messages via content prefix backstop', () => {
    // Simulate a message written before migration: has prefix but is_bot_message = 0
    store({
      id: 'm5',
      chat_jid: 'group@g.us',
      sender: 'Bot@s.whatsapp.net',
      sender_name: 'Bot',
      content: 'Andy: old bot reply',
      timestamp: '2024-01-01T00:00:05.000Z',
    });
    const msgs = getMessagesSince(
      'group@g.us',
      '2024-01-01T00:00:04.000Z',
      'Andy',
    );
    expect(msgs).toHaveLength(0);
  });
});

// --- getNewMessages ---

describe('getNewMessages', () => {
  beforeEach(() => {
    storeChatMetadata('group1@g.us', '2024-01-01T00:00:00.000Z');
    storeChatMetadata('group2@g.us', '2024-01-01T00:00:00.000Z');

    store({
      id: 'a1',
      chat_jid: 'group1@g.us',
      sender: 'user@s.whatsapp.net',
      sender_name: 'User',
      content: 'g1 msg1',
      timestamp: '2024-01-01T00:00:01.000Z',
    });
    store({
      id: 'a2',
      chat_jid: 'group2@g.us',
      sender: 'user@s.whatsapp.net',
      sender_name: 'User',
      content: 'g2 msg1',
      timestamp: '2024-01-01T00:00:02.000Z',
    });
    storeMessage({
      id: 'a3',
      chat_jid: 'group1@g.us',
      sender: 'user@s.whatsapp.net',
      sender_name: 'User',
      content: 'bot reply',
      timestamp: '2024-01-01T00:00:03.000Z',
      is_bot_message: true,
    });
    store({
      id: 'a4',
      chat_jid: 'group1@g.us',
      sender: 'user@s.whatsapp.net',
      sender_name: 'User',
      content: 'g1 msg2',
      timestamp: '2024-01-01T00:00:04.000Z',
    });
  });

  it('returns new messages across multiple groups', () => {
    const { messages, newTimestamp } = getNewMessages(
      ['group1@g.us', 'group2@g.us'],
      '2024-01-01T00:00:00.000Z',
      'Andy',
    );
    // Excludes bot message, returns 3 user messages
    expect(messages).toHaveLength(3);
    expect(newTimestamp).toBe('2024-01-01T00:00:04.000Z');
  });

  it('filters by timestamp', () => {
    const { messages } = getNewMessages(
      ['group1@g.us', 'group2@g.us'],
      '2024-01-01T00:00:02.000Z',
      'Andy',
    );
    // Only g1 msg2 (after ts, not bot)
    expect(messages).toHaveLength(1);
    expect(messages[0].content).toBe('g1 msg2');
  });

  it('returns empty for no registered groups', () => {
    const { messages, newTimestamp } = getNewMessages([], '', 'Andy');
    expect(messages).toHaveLength(0);
    expect(newTimestamp).toBe('');
  });
});

// --- storeChatMetadata ---

describe('storeChatMetadata', () => {
  it('stores chat with JID as default name', () => {
    storeChatMetadata('group@g.us', '2024-01-01T00:00:00.000Z');
    const chats = getAllChats();
    expect(chats).toHaveLength(1);
    expect(chats[0].jid).toBe('group@g.us');
    expect(chats[0].name).toBe('group@g.us');
  });

  it('stores chat with explicit name', () => {
    storeChatMetadata('group@g.us', '2024-01-01T00:00:00.000Z', 'My Group');
    const chats = getAllChats();
    expect(chats[0].name).toBe('My Group');
  });

  it('updates name on subsequent call with name', () => {
    storeChatMetadata('group@g.us', '2024-01-01T00:00:00.000Z');
    storeChatMetadata('group@g.us', '2024-01-01T00:00:01.000Z', 'Updated Name');
    const chats = getAllChats();
    expect(chats).toHaveLength(1);
    expect(chats[0].name).toBe('Updated Name');
  });

  it('preserves newer timestamp on conflict', () => {
    storeChatMetadata('group@g.us', '2024-01-01T00:00:05.000Z');
    storeChatMetadata('group@g.us', '2024-01-01T00:00:01.000Z');
    const chats = getAllChats();
    expect(chats[0].last_message_time).toBe('2024-01-01T00:00:05.000Z');
  });
});

// --- registered agents ---

describe('registered agents', () => {
  it('allows multiple JIDs to map to the same agent name', () => {
    setRegisteredAgent('tg:user:1001', {
      name: 'main',
      agentName: 'main',
      trigger: '@Andy',
      added_at: '2024-01-01T00:00:00.000Z',
      requiresTrigger: false,
    });
    setRegisteredAgent('tg:user:1002', {
      name: 'main',
      agentName: 'main',
      trigger: '@Andy',
      added_at: '2024-01-01T00:00:00.000Z',
      requiresTrigger: false,
    });

    const agents = getAllRegisteredAgents();
    expect(agents['tg:user:1001']?.agentName).toBe('main');
    expect(agents['tg:user:1002']?.agentName).toBe('main');
  });
});

// --- Task CRUD ---

describe('task CRUD', () => {
  it('creates and retrieves a task', () => {
    createTask({
      id: 'task-1',
      agentName: 'main',
      chat_jid: 'group@g.us',
      prompt: 'do something',
      schedule_type: 'once',
      schedule_value: '2024-06-01T00:00:00.000Z',
      context_mode: 'isolated',
      next_run: '2024-06-01T00:00:00.000Z',
      status: 'active',
      created_at: '2024-01-01T00:00:00.000Z',
    });

    const task = getTaskById('task-1');
    expect(task).toBeDefined();
    expect(task!.prompt).toBe('do something');
    expect(task!.status).toBe('active');
  });

  it('updates task status', () => {
    createTask({
      id: 'task-2',
      agentName: 'main',
      chat_jid: 'group@g.us',
      prompt: 'test',
      schedule_type: 'once',
      schedule_value: '2024-06-01T00:00:00.000Z',
      context_mode: 'isolated',
      next_run: null,
      status: 'active',
      created_at: '2024-01-01T00:00:00.000Z',
    });

    updateTask('task-2', { status: 'paused' });
    expect(getTaskById('task-2')!.status).toBe('paused');
  });

  it('deletes a task and its run logs', () => {
    createTask({
      id: 'task-3',
      agentName: 'main',
      chat_jid: 'group@g.us',
      prompt: 'delete me',
      schedule_type: 'once',
      schedule_value: '2024-06-01T00:00:00.000Z',
      context_mode: 'isolated',
      next_run: null,
      status: 'active',
      created_at: '2024-01-01T00:00:00.000Z',
    });

    deleteTask('task-3');
    expect(getTaskById('task-3')).toBeUndefined();
  });
});

// --- web channel db helpers ---

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
    storeChatMetadata('web:user1', '2026-01-01T00:00:00Z');
    const base = {
      chat_jid: 'web:user1',
      sender: 'u1',
      sender_name: 'User',
      is_from_me: false,
      is_bot_message: false,
    };
    storeMessage({
      ...base,
      id: 'm1',
      thread_id: 'conv-1',
      content: 'first',
      timestamp: '2026-01-01T00:00:01Z',
    });
    storeMessage({
      ...base,
      id: 'm2',
      thread_id: 'conv-1',
      content: 'second',
      timestamp: '2026-01-01T00:00:02Z',
    });
    storeMessage({
      ...base,
      id: 'm3',
      thread_id: 'conv-1',
      content: 'third',
      timestamp: '2026-01-01T00:00:03Z',
    });

    const result = getMessageHistory('web:user1', 'conv-1', { limit: 2 });
    expect(result).toHaveLength(2);
    expect(result[0].id).toBe('m3');
    expect(result[1].id).toBe('m2');
  });

  it('getMessageHistory supports before cursor', () => {
    storeChatMetadata('web:user1', '2026-01-01T00:00:00Z');
    const base = {
      chat_jid: 'web:user1',
      sender: 'u1',
      sender_name: 'User',
      is_from_me: false,
      is_bot_message: false,
    };
    storeMessage({
      ...base,
      id: 'm1',
      thread_id: 'conv-1',
      content: 'first',
      timestamp: '2026-01-01T00:00:01Z',
    });
    storeMessage({
      ...base,
      id: 'm2',
      thread_id: 'conv-1',
      content: 'second',
      timestamp: '2026-01-01T00:00:02Z',
    });
    storeMessage({
      ...base,
      id: 'm3',
      thread_id: 'conv-1',
      content: 'third',
      timestamp: '2026-01-01T00:00:03Z',
    });

    const result = getMessageHistory('web:user1', 'conv-1', {
      before: '2026-01-01T00:00:03Z',
      limit: 10,
    });
    expect(result).toHaveLength(2);
    expect(result[0].id).toBe('m2');
    expect(result[1].id).toBe('m1');
  });
});
