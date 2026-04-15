import Database from 'better-sqlite3';
import { randomBytes } from 'crypto';
import fs from 'fs';
import path from 'path';

import { ASSISTANT_NAME, DATA_DIR, STORE_DIR } from './config.js';
import { isValidAgentName } from './agent-folder.js';
import { logger } from './logger.js';
import {
  makeSessionScopeKey,
  normalizeThreadId,
  parseSessionScopeKey,
} from './session-scope.js';
import {
  NewMessage,
  RegisteredAgent,
  ScheduledTask,
  TaskRunLog,
} from './types.js';

let db: Database.Database;

function hasTable(database: Database.Database, tableName: string): boolean {
  const row = database
    .prepare(`SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?`)
    .get(tableName) as { name: string } | undefined;
  return !!row;
}

function tableColumns(
  database: Database.Database,
  tableName: string,
): string[] {
  if (!hasTable(database, tableName)) return [];
  const rows = database
    .prepare(`PRAGMA table_info(${tableName})`)
    .all() as Array<{ name: string }>;
  return rows.map((r) => r.name);
}

function migrateSessionsTable(database: Database.Database): void {
  if (!hasTable(database, 'sessions')) return;
  const columns = tableColumns(database, 'sessions');
  if (columns.includes('channel_id') && columns.includes('agent_name')) return;
  if (!columns.includes('group_folder')) return;

  database.exec(`ALTER TABLE sessions RENAME TO sessions_legacy`);
  database.exec(`
    CREATE TABLE sessions (
      channel_id TEXT NOT NULL,
      thread_id TEXT NOT NULL DEFAULT '',
      agent_name TEXT NOT NULL,
      session_id TEXT NOT NULL,
      PRIMARY KEY (channel_id, thread_id, agent_name)
    );
  `);

  const legacyRows = database
    .prepare(`SELECT group_folder, session_id FROM sessions_legacy`)
    .all() as Array<{ group_folder: string; session_id: string }>;

  for (const row of legacyRows) {
    const agent = database
      .prepare(`SELECT jid FROM agents WHERE agent_name = ?`)
      .get(row.group_folder) as { jid: string } | undefined;
    if (!agent) {
      logger.warn(
        { agentName: row.group_folder },
        'Skipping legacy session row because no mapped agent/channel exists',
      );
      continue;
    }
    database
      .prepare(
        `INSERT OR REPLACE INTO sessions (channel_id, thread_id, agent_name, session_id) VALUES (?, '', ?, ?)`,
      )
      .run(agent.jid, row.group_folder, row.session_id);
  }

  database.exec(`DROP TABLE sessions_legacy`);
}

function migrateRegisteredGroupsTable(database: Database.Database): void {
  if (!hasTable(database, 'registered_groups')) return;

  const rows = database
    .prepare(
      `SELECT jid, name, folder, trigger_pattern, added_at, container_config, requires_trigger FROM registered_groups`,
    )
    .all() as Array<{
    jid: string;
    name: string;
    folder: string;
    trigger_pattern: string;
    added_at: string;
    container_config: string | null;
    requires_trigger: number | null;
  }>;

  for (const row of rows) {
    if (!isValidAgentName(row.folder)) {
      logger.warn(
        { jid: row.jid, folder: row.folder },
        'Skipping legacy registered_groups row with invalid folder',
      );
      continue;
    }
    database
      .prepare(
        `INSERT OR REPLACE INTO agents (jid, name, agent_name, trigger_pattern, added_at, container_config, requires_trigger)
         VALUES (?, ?, ?, ?, ?, ?, ?)`,
      )
      .run(
        row.jid,
        row.name,
        row.folder,
        row.trigger_pattern,
        row.added_at,
        row.container_config,
        row.requires_trigger,
      );
  }
}

function migrateAgentsTable(database: Database.Database): void {
  if (!hasTable(database, 'agents')) return;

  const row = database
    .prepare(`SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?`)
    .get('agents') as { sql: string } | undefined;
  if (!row?.sql?.includes('agent_name TEXT NOT NULL UNIQUE')) return;

  database.exec(`ALTER TABLE agents RENAME TO agents_legacy`);
  database.exec(`
    CREATE TABLE agents (
      jid TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      agent_name TEXT NOT NULL,
      trigger_pattern TEXT NOT NULL,
      added_at TEXT NOT NULL,
      container_config TEXT,
      requires_trigger INTEGER DEFAULT 1
    );
    CREATE INDEX IF NOT EXISTS idx_agents_agent_name ON agents(agent_name);
  `);

  database.exec(`
    INSERT OR REPLACE INTO agents (jid, name, agent_name, trigger_pattern, added_at, container_config, requires_trigger)
    SELECT jid, name, agent_name, trigger_pattern, added_at, container_config, requires_trigger
    FROM agents_legacy
  `);
  database.exec(`DROP TABLE agents_legacy`);
}

function migrateScheduledTasksTable(database: Database.Database): void {
  if (!hasTable(database, 'scheduled_tasks')) return;
  const columns = tableColumns(database, 'scheduled_tasks');
  if (columns.includes('agent_name')) return;
  if (!columns.includes('group_folder')) return;

  database.exec(
    `ALTER TABLE scheduled_tasks RENAME COLUMN group_folder TO agent_name`,
  );
}

const SCHEDULED_TASK_SELECT = `
  SELECT
    id,
    agent_name AS agentName,
    chat_jid,
    prompt,
    schedule_type,
    schedule_value,
    context_mode,
    next_run,
    last_run,
    last_result,
    status,
    created_at
  FROM scheduled_tasks
`;

function createSchema(database: Database.Database): void {
  // Create tables first (without indexes that reference renamed columns)
  database.exec(`
    CREATE TABLE IF NOT EXISTS chats (
      jid TEXT PRIMARY KEY,
      name TEXT,
      last_message_time TEXT,
      channel TEXT,
      is_group INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS messages (
      id TEXT,
      chat_jid TEXT,
      thread_id TEXT NOT NULL DEFAULT '',
      sender TEXT,
      sender_name TEXT,
      content TEXT,
      timestamp TEXT,
      is_from_me INTEGER,
      is_bot_message INTEGER DEFAULT 0,
      PRIMARY KEY (id, chat_jid),
      FOREIGN KEY (chat_jid) REFERENCES chats(jid)
    );
    CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp);

    CREATE TABLE IF NOT EXISTS scheduled_tasks (
      id TEXT PRIMARY KEY,
      agent_name TEXT NOT NULL,
      chat_jid TEXT NOT NULL,
      prompt TEXT NOT NULL,
      schedule_type TEXT NOT NULL,
      schedule_value TEXT NOT NULL,
      next_run TEXT,
      last_run TEXT,
      last_result TEXT,
      status TEXT DEFAULT 'active',
      created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_next_run ON scheduled_tasks(next_run);
    CREATE INDEX IF NOT EXISTS idx_status ON scheduled_tasks(status);

    CREATE TABLE IF NOT EXISTS task_run_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      task_id TEXT NOT NULL,
      run_at TEXT NOT NULL,
      duration_ms INTEGER NOT NULL,
      status TEXT NOT NULL,
      result TEXT,
      error TEXT,
      FOREIGN KEY (task_id) REFERENCES scheduled_tasks(id)
    );
    CREATE INDEX IF NOT EXISTS idx_task_run_logs ON task_run_logs(task_id, run_at);

    CREATE TABLE IF NOT EXISTS router_state (
      key TEXT PRIMARY KEY,
      value TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS sessions (
      channel_id TEXT NOT NULL,
      thread_id TEXT NOT NULL DEFAULT '',
      agent_name TEXT NOT NULL,
      session_id TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS replay_links (
      replay_id TEXT PRIMARY KEY,
      channel_id TEXT NOT NULL,
      thread_id TEXT NOT NULL DEFAULT '',
      agent_name TEXT NOT NULL,
      created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS agents (
      jid TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      agent_name TEXT NOT NULL,
      trigger_pattern TEXT NOT NULL,
      added_at TEXT NOT NULL,
      container_config TEXT,
      requires_trigger INTEGER DEFAULT 1
    );
  `);

  // Run migrations before creating indexes on renamed columns
  migrateAgentsTable(database);
  migrateRegisteredGroupsTable(database);
  migrateSessionsTable(database);
  migrateScheduledTasksTable(database);

  // Create indexes after migrations (columns may have been renamed)
  database.exec(`
    CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_agent_name
      ON scheduled_tasks(agent_name);
    CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_scope
      ON sessions(channel_id, thread_id, agent_name);
    CREATE UNIQUE INDEX IF NOT EXISTS idx_replay_links_scope
      ON replay_links(channel_id, thread_id, agent_name);
    CREATE INDEX IF NOT EXISTS idx_agents_agent_name ON agents(agent_name);
  `);

  // Add context_mode column if it doesn't exist (migration for existing DBs)
  try {
    database.exec(
      `ALTER TABLE scheduled_tasks ADD COLUMN context_mode TEXT DEFAULT 'isolated'`,
    );
  } catch {
    /* column already exists */
  }

  // Add is_bot_message column if it doesn't exist (migration for existing DBs)
  try {
    database.exec(
      `ALTER TABLE messages ADD COLUMN is_bot_message INTEGER DEFAULT 0`,
    );
    // Backfill: mark existing bot messages that used the content prefix pattern
    database
      .prepare(`UPDATE messages SET is_bot_message = 1 WHERE content LIKE ?`)
      .run(`${ASSISTANT_NAME}:%`);
  } catch {
    /* column already exists */
  }

  // Add thread_id column if it doesn't exist (migration for existing DBs)
  try {
    database.exec(`ALTER TABLE messages ADD COLUMN thread_id TEXT DEFAULT ''`);
  } catch {
    /* column already exists */
  }

  // Add channel and is_group columns if they don't exist (migration for existing DBs)
  try {
    database.exec(`ALTER TABLE chats ADD COLUMN channel TEXT`);
    database.exec(`ALTER TABLE chats ADD COLUMN is_group INTEGER DEFAULT 0`);
    // Backfill from JID patterns
    database.exec(
      `UPDATE chats SET channel = 'whatsapp', is_group = 1 WHERE jid LIKE '%@g.us'`,
    );
    database.exec(
      `UPDATE chats SET channel = 'whatsapp', is_group = 0 WHERE jid LIKE '%@s.whatsapp.net'`,
    );
    database.exec(
      `UPDATE chats SET channel = 'discord', is_group = 1 WHERE jid LIKE 'dc:%'`,
    );
    database.exec(
      `UPDATE chats SET channel = 'telegram', is_group = 1 WHERE jid LIKE 'tg:%'`,
    );
  } catch {
    /* columns already exist */
  }
}

export function initDatabase(): void {
  const dbPath = path.join(STORE_DIR, 'messages.db');
  fs.mkdirSync(path.dirname(dbPath), { recursive: true });

  db = new Database(dbPath);
  createSchema(db);

  // Migrate from JSON files if they exist
  migrateJsonState();
}

/** @internal - for tests only. Creates a fresh in-memory database. */
export function _initTestDatabase(): void {
  db = new Database(':memory:');
  createSchema(db);
}

/**
 * Store chat metadata only (no message content).
 * Used for all chats to enable group discovery without storing sensitive content.
 */
export function storeChatMetadata(
  chatJid: string,
  timestamp: string,
  name?: string,
  channel?: string,
  isGroup?: boolean,
): void {
  const ch = channel ?? null;
  const group = isGroup === undefined ? null : isGroup ? 1 : 0;

  if (name) {
    // Update with name, preserving existing timestamp if newer
    db.prepare(
      `
      INSERT INTO chats (jid, name, last_message_time, channel, is_group) VALUES (?, ?, ?, ?, ?)
      ON CONFLICT(jid) DO UPDATE SET
        name = excluded.name,
        last_message_time = MAX(last_message_time, excluded.last_message_time),
        channel = COALESCE(excluded.channel, channel),
        is_group = COALESCE(excluded.is_group, is_group)
    `,
    ).run(chatJid, name, timestamp, ch, group);
  } else {
    // Update timestamp only, preserve existing name if any
    db.prepare(
      `
      INSERT INTO chats (jid, name, last_message_time, channel, is_group) VALUES (?, ?, ?, ?, ?)
      ON CONFLICT(jid) DO UPDATE SET
        last_message_time = MAX(last_message_time, excluded.last_message_time),
        channel = COALESCE(excluded.channel, channel),
        is_group = COALESCE(excluded.is_group, is_group)
    `,
    ).run(chatJid, chatJid, timestamp, ch, group);
  }
}

/**
 * Update chat name without changing timestamp for existing chats.
 * New chats get the current time as their initial timestamp.
 * Used during group metadata sync.
 */
export function updateChatName(chatJid: string, name: string): void {
  db.prepare(
    `
    INSERT INTO chats (jid, name, last_message_time) VALUES (?, ?, ?)
    ON CONFLICT(jid) DO UPDATE SET name = excluded.name
  `,
  ).run(chatJid, name, new Date().toISOString());
}

export interface ChatInfo {
  jid: string;
  name: string;
  last_message_time: string;
  channel: string;
  is_group: number;
}

/**
 * Get all known chats, ordered by most recent activity.
 */
export function getAllChats(): ChatInfo[] {
  return db
    .prepare(
      `
    SELECT jid, name, last_message_time, channel, is_group
    FROM chats
    ORDER BY last_message_time DESC
  `,
    )
    .all() as ChatInfo[];
}

/**
 * Get timestamp of last group metadata sync.
 */
export function getLastGroupSync(): string | null {
  // Store sync time in a special chat entry
  const row = db
    .prepare(`SELECT last_message_time FROM chats WHERE jid = '__group_sync__'`)
    .get() as { last_message_time: string } | undefined;
  return row?.last_message_time || null;
}

/**
 * Record that group metadata was synced.
 */
export function setLastGroupSync(): void {
  const now = new Date().toISOString();
  db.prepare(
    `INSERT OR REPLACE INTO chats (jid, name, last_message_time) VALUES ('__group_sync__', '__group_sync__', ?)`,
  ).run(now);
}

/**
 * Store a message with full content.
 * Only call this for registered groups where message history is needed.
 */
export function storeMessage(msg: NewMessage): void {
  db.prepare(
    `INSERT OR REPLACE INTO messages (id, chat_jid, thread_id, sender, sender_name, content, timestamp, is_from_me, is_bot_message) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
  ).run(
    msg.id,
    msg.chat_jid,
    normalizeThreadId(msg.thread_id),
    msg.sender,
    msg.sender_name,
    msg.content,
    msg.timestamp,
    msg.is_from_me ? 1 : 0,
    msg.is_bot_message ? 1 : 0,
  );
}

/**
 * Store a message directly (for non-WhatsApp channels that don't use Baileys proto).
 */
export function storeMessageDirect(msg: {
  id: string;
  chat_jid: string;
  thread_id?: string | null;
  sender: string;
  sender_name: string;
  content: string;
  timestamp: string;
  is_from_me: boolean;
  is_bot_message?: boolean;
}): void {
  db.prepare(
    `INSERT OR REPLACE INTO messages (id, chat_jid, thread_id, sender, sender_name, content, timestamp, is_from_me, is_bot_message) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
  ).run(
    msg.id,
    msg.chat_jid,
    normalizeThreadId(msg.thread_id),
    msg.sender,
    msg.sender_name,
    msg.content,
    msg.timestamp,
    msg.is_from_me ? 1 : 0,
    msg.is_bot_message ? 1 : 0,
  );
}

export function getNewMessages(
  jids: string[],
  lastTimestamp: string,
  botPrefix: string,
): { messages: NewMessage[]; newTimestamp: string } {
  if (jids.length === 0) return { messages: [], newTimestamp: lastTimestamp };

  const placeholders = jids.map(() => '?').join(',');
  // Filter bot messages using both the is_bot_message flag AND the content
  // prefix as a backstop for messages written before the migration ran.
  const sql = `
    SELECT id, chat_jid, thread_id, sender, sender_name, content, timestamp
    FROM messages
    WHERE timestamp > ? AND chat_jid IN (${placeholders})
      AND is_bot_message = 0 AND content NOT LIKE ?
      AND content != '' AND content IS NOT NULL
    ORDER BY timestamp
  `;

  const rows = db
    .prepare(sql)
    .all(lastTimestamp, ...jids, `${botPrefix}:%`) as Array<
    NewMessage & { thread_id: string }
  >;

  const messages = rows.map((row) => ({
    ...row,
    thread_id: row.thread_id || null,
  }));

  let newTimestamp = lastTimestamp;
  for (const row of messages) {
    if (row.timestamp > newTimestamp) newTimestamp = row.timestamp;
  }

  return { messages, newTimestamp };
}

export function getMessagesSince(
  chatJid: string,
  sinceTimestamp: string,
  botPrefix: string,
  threadId: string | null = null,
  options?: {
    includeThreadParent?: boolean;
  },
): NewMessage[] {
  // Filter bot messages using both the is_bot_message flag AND the content
  // prefix as a backstop for messages written before the migration ran.
  const normalized = normalizeThreadId(threadId);
  const isThread = normalized !== '';
  const includeThreadParent = isThread && options?.includeThreadParent === true;
  const sql = includeThreadParent
    ? `
    SELECT id, chat_jid, thread_id, sender, sender_name, content, timestamp
    FROM messages
    WHERE chat_jid = ?
      AND (
        (thread_id = ? AND timestamp > ? AND is_bot_message = 0 AND content NOT LIKE ?)
        OR (thread_id = '' AND id = ? AND content != '' AND content IS NOT NULL)
      )
      AND content != '' AND content IS NOT NULL
    ORDER BY timestamp
  `
    : `
    SELECT id, chat_jid, thread_id, sender, sender_name, content, timestamp
    FROM messages
    WHERE chat_jid = ? AND thread_id = ? AND timestamp > ?
      AND is_bot_message = 0 AND content NOT LIKE ?
      AND content != '' AND content IS NOT NULL
    ORDER BY timestamp
  `;
  const rows = includeThreadParent
    ? (db.prepare(sql).all(
        chatJid,
        normalized, // thread_id = ?
        sinceTimestamp, // timestamp > ?
        `${botPrefix}:%`, // content NOT LIKE ?
        normalized, // id = ? (parent message)
      ) as Array<NewMessage & { thread_id: string }>)
    : (db
        .prepare(sql)
        .all(chatJid, normalized, sinceTimestamp, `${botPrefix}:%`) as Array<
        NewMessage & { thread_id: string }
      >);
  return rows.map((row) => ({ ...row, thread_id: row.thread_id || null }));
}

export function createTask(
  task: Omit<ScheduledTask, 'last_run' | 'last_result'>,
): void {
  db.prepare(
    `
    INSERT INTO scheduled_tasks (id, agent_name, chat_jid, prompt, schedule_type, schedule_value, context_mode, next_run, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `,
  ).run(
    task.id,
    task.agentName,
    task.chat_jid,
    task.prompt,
    task.schedule_type,
    task.schedule_value,
    task.context_mode || 'isolated',
    task.next_run,
    task.status,
    task.created_at,
  );
}

export function getTaskById(id: string): ScheduledTask | undefined {
  return db.prepare(`${SCHEDULED_TASK_SELECT} WHERE id = ?`).get(id) as
    | ScheduledTask
    | undefined;
}

export function getTasksForAgent(agentName: string): ScheduledTask[] {
  return db
    .prepare(
      `${SCHEDULED_TASK_SELECT} WHERE agent_name = ? ORDER BY created_at DESC`,
    )
    .all(agentName) as ScheduledTask[];
}

export function getAllTasks(): ScheduledTask[] {
  return db
    .prepare(`${SCHEDULED_TASK_SELECT} ORDER BY created_at DESC`)
    .all() as ScheduledTask[];
}

export function updateTask(
  id: string,
  updates: Partial<
    Pick<
      ScheduledTask,
      'prompt' | 'schedule_type' | 'schedule_value' | 'next_run' | 'status'
    >
  >,
): void {
  const fields: string[] = [];
  const values: unknown[] = [];

  if (updates.prompt !== undefined) {
    fields.push('prompt = ?');
    values.push(updates.prompt);
  }
  if (updates.schedule_type !== undefined) {
    fields.push('schedule_type = ?');
    values.push(updates.schedule_type);
  }
  if (updates.schedule_value !== undefined) {
    fields.push('schedule_value = ?');
    values.push(updates.schedule_value);
  }
  if (updates.next_run !== undefined) {
    fields.push('next_run = ?');
    values.push(updates.next_run);
  }
  if (updates.status !== undefined) {
    fields.push('status = ?');
    values.push(updates.status);
  }

  if (fields.length === 0) return;

  values.push(id);
  db.prepare(
    `UPDATE scheduled_tasks SET ${fields.join(', ')} WHERE id = ?`,
  ).run(...values);
}

export function deleteTask(id: string): void {
  // Delete child records first (FK constraint)
  db.prepare('DELETE FROM task_run_logs WHERE task_id = ?').run(id);
  db.prepare('DELETE FROM scheduled_tasks WHERE id = ?').run(id);
}

export function getDueTasks(): ScheduledTask[] {
  const now = new Date().toISOString();
  return db
    .prepare(
      `
    ${SCHEDULED_TASK_SELECT}
    WHERE status = 'active' AND next_run IS NOT NULL AND next_run <= ?
    ORDER BY next_run
  `,
    )
    .all(now) as ScheduledTask[];
}

export function updateTaskAfterRun(
  id: string,
  nextRun: string | null,
  lastResult: string,
): void {
  const now = new Date().toISOString();
  db.prepare(
    `
    UPDATE scheduled_tasks
    SET next_run = ?, last_run = ?, last_result = ?, status = CASE WHEN ? IS NULL THEN 'completed' ELSE status END
    WHERE id = ?
  `,
  ).run(nextRun, now, lastResult, nextRun, id);
}

export function logTaskRun(log: TaskRunLog): void {
  db.prepare(
    `
    INSERT INTO task_run_logs (task_id, run_at, duration_ms, status, result, error)
    VALUES (?, ?, ?, ?, ?, ?)
  `,
  ).run(
    log.task_id,
    log.run_at,
    log.duration_ms,
    log.status,
    log.result,
    log.error,
  );
}

// --- Router state accessors ---

export function getRouterState(key: string): string | undefined {
  const row = db
    .prepare('SELECT value FROM router_state WHERE key = ?')
    .get(key) as { value: string } | undefined;
  return row?.value;
}

export function setRouterState(key: string, value: string): void {
  db.prepare(
    'INSERT OR REPLACE INTO router_state (key, value) VALUES (?, ?)',
  ).run(key, value);
}

// --- Session accessors ---
export { makeSessionScopeKey, normalizeThreadId, parseSessionScopeKey };

export function getSession(
  channelId: string,
  threadId: string | null,
  agentName: string,
): string | undefined {
  const row = db
    .prepare(
      'SELECT session_id FROM sessions WHERE channel_id = ? AND thread_id = ? AND agent_name = ?',
    )
    .get(channelId, normalizeThreadId(threadId), agentName) as
    | { session_id: string }
    | undefined;
  return row?.session_id;
}

export function setSession(
  channelId: string,
  threadId: string | null,
  agentName: string,
  sessionId: string,
): void {
  db.prepare(
    'INSERT OR REPLACE INTO sessions (channel_id, thread_id, agent_name, session_id) VALUES (?, ?, ?, ?)',
  ).run(channelId, normalizeThreadId(threadId), agentName, sessionId);
}

export function deleteSession(
  channelId: string,
  threadId: string | null,
  agentName: string,
): void {
  db.prepare(
    'DELETE FROM sessions WHERE channel_id = ? AND thread_id = ? AND agent_name = ?',
  ).run(channelId, normalizeThreadId(threadId), agentName);
}

export function getAllSessions(): Record<string, string> {
  const rows = db
    .prepare(
      'SELECT channel_id, thread_id, agent_name, session_id FROM sessions',
    )
    .all() as Array<{
    channel_id: string;
    thread_id: string;
    agent_name: string;
    session_id: string;
  }>;
  const result: Record<string, string> = {};
  for (const row of rows) {
    result[makeSessionScopeKey(row.channel_id, row.thread_id, row.agent_name)] =
      row.session_id;
  }
  return result;
}

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
  options: {
    before?: string;
    limit?: number;
    includeThreadParent?: boolean;
  } = {},
): NewMessage[] {
  const limit = options.limit ?? 50;
  const normalized = normalizeThreadId(threadId);
  const includeThreadParent =
    options.includeThreadParent === true && normalized !== '';

  if (includeThreadParent) {
    const whereBefore = options.before ? 'AND timestamp < ?' : '';
    const rows = db
      .prepare(
        `SELECT id, chat_jid, thread_id, sender, sender_name, content, timestamp, is_bot_message
         FROM messages
         WHERE chat_jid = ?
           AND (thread_id = ? OR (thread_id = '' AND id = ?))
           ${whereBefore}
         ORDER BY timestamp DESC, id DESC
         LIMIT ?`,
      )
      .all(
        ...(options.before
          ? [chatJid, normalized, normalized, options.before, limit]
          : [chatJid, normalized, normalized, limit]),
      ) as Array<NewMessage & { thread_id: string }>;
    return rows.map((row) => ({ ...row, thread_id: row.thread_id || null }));
  }

  if (options.before) {
    const rows = db
      .prepare(
        `SELECT id, chat_jid, thread_id, sender, sender_name, content, timestamp, is_bot_message
         FROM messages
         WHERE chat_jid = ? AND thread_id = ? AND timestamp < ?
         ORDER BY timestamp DESC, id DESC
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
       ORDER BY timestamp DESC, id DESC
       LIMIT ?`,
    )
    .all(chatJid, normalized, limit) as Array<
    NewMessage & { thread_id: string }
  >;
  return rows.map((row) => ({ ...row, thread_id: row.thread_id || null }));
}

export interface ReplayLink {
  replayId: string;
  channelId: string;
  threadId: string | null;
  agentName: string;
  createdAt: string;
}

export function getReplayLinkById(replayId: string): ReplayLink | undefined {
  const row = db
    .prepare(
      `SELECT replay_id, channel_id, thread_id, agent_name, created_at
       FROM replay_links
       WHERE replay_id = ?`,
    )
    .get(replayId) as
    | {
        replay_id: string;
        channel_id: string;
        thread_id: string;
        agent_name: string;
        created_at: string;
      }
    | undefined;
  if (!row) return undefined;

  return {
    replayId: row.replay_id,
    channelId: row.channel_id,
    threadId: row.thread_id || null,
    agentName: row.agent_name,
    createdAt: row.created_at,
  };
}

export function getReplayLinkByScope(
  channelId: string,
  threadId: string | null,
  agentName: string,
): ReplayLink | undefined {
  const row = db
    .prepare(
      `SELECT replay_id, channel_id, thread_id, agent_name, created_at
       FROM replay_links
       WHERE channel_id = ? AND thread_id = ? AND agent_name = ?`,
    )
    .get(channelId, normalizeThreadId(threadId), agentName) as
    | {
        replay_id: string;
        channel_id: string;
        thread_id: string;
        agent_name: string;
        created_at: string;
      }
    | undefined;
  if (!row) return undefined;

  return {
    replayId: row.replay_id,
    channelId: row.channel_id,
    threadId: row.thread_id || null,
    agentName: row.agent_name,
    createdAt: row.created_at,
  };
}

export function getOrCreateReplayLink(
  channelId: string,
  threadId: string | null,
  agentName: string,
): ReplayLink {
  const existing = getReplayLinkByScope(channelId, threadId, agentName);
  if (existing) return existing;

  const normalizedThreadId = normalizeThreadId(threadId);
  const createdAt = new Date().toISOString();

  for (let attempt = 0; attempt < 5; attempt += 1) {
    const replayId = `rpl_${randomBytes(16).toString('hex')}`;
    db.prepare(
      `INSERT OR IGNORE INTO replay_links (replay_id, channel_id, thread_id, agent_name, created_at)
       VALUES (?, ?, ?, ?, ?)`,
    ).run(replayId, channelId, normalizedThreadId, agentName, createdAt);

    const link = getReplayLinkByScope(channelId, threadId, agentName);
    if (link) return link;
  }

  throw new Error('Failed to allocate replay link');
}

// --- Registered agent accessors ---

export function getRegisteredAgent(
  jid: string,
): (RegisteredAgent & { jid: string }) | undefined {
  const row = db.prepare('SELECT * FROM agents WHERE jid = ?').get(jid) as
    | {
        jid: string;
        name: string;
        agent_name: string;
        trigger_pattern: string;
        added_at: string;
        container_config: string | null;
        requires_trigger: number | null;
      }
    | undefined;
  if (!row) return undefined;
  if (!isValidAgentName(row.agent_name)) {
    logger.warn(
      { jid: row.jid, agentName: row.agent_name },
      'Skipping registered agent with invalid name',
    );
    return undefined;
  }
  return {
    jid: row.jid,
    name: row.name,
    agentName: row.agent_name,
    trigger: row.trigger_pattern,
    added_at: row.added_at,
    containerConfig: row.container_config
      ? JSON.parse(row.container_config)
      : undefined,
    requiresTrigger:
      row.requires_trigger === null ? undefined : row.requires_trigger === 1,
  };
}

export function setRegisteredAgent(jid: string, group: RegisteredAgent): void {
  if (!isValidAgentName(group.agentName)) {
    throw new Error(`Invalid agent name "${group.agentName}" for JID ${jid}`);
  }
  db.prepare(
    `INSERT OR REPLACE INTO agents (jid, name, agent_name, trigger_pattern, added_at, container_config, requires_trigger)
     VALUES (?, ?, ?, ?, ?, ?, ?)`,
  ).run(
    jid,
    group.name,
    group.agentName,
    group.trigger,
    group.added_at,
    group.containerConfig ? JSON.stringify(group.containerConfig) : null,
    group.requiresTrigger === undefined ? 1 : group.requiresTrigger ? 1 : 0,
  );
}

export function getAllRegisteredAgents(): Record<string, RegisteredAgent> {
  const rows = db.prepare('SELECT * FROM agents').all() as Array<{
    jid: string;
    name: string;
    agent_name: string;
    trigger_pattern: string;
    added_at: string;
    container_config: string | null;
    requires_trigger: number | null;
  }>;
  const result: Record<string, RegisteredAgent> = {};
  for (const row of rows) {
    if (!isValidAgentName(row.agent_name)) {
      logger.warn(
        { jid: row.jid, agentName: row.agent_name },
        'Skipping registered agent with invalid name',
      );
      continue;
    }
    result[row.jid] = {
      name: row.name,
      agentName: row.agent_name,
      trigger: row.trigger_pattern,
      added_at: row.added_at,
      containerConfig: row.container_config
        ? JSON.parse(row.container_config)
        : undefined,
      requiresTrigger:
        row.requires_trigger === null ? undefined : row.requires_trigger === 1,
    };
  }
  return result;
}

// --- JSON migration ---

function migrateJsonState(): void {
  const migrateFile = (filename: string) => {
    const filePath = path.join(DATA_DIR, filename);
    if (!fs.existsSync(filePath)) return null;
    try {
      const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
      fs.renameSync(filePath, `${filePath}.migrated`);
      return data;
    } catch {
      return null;
    }
  };

  // Migrate router_state.json
  const routerState = migrateFile('router_state.json') as {
    last_timestamp?: string;
    last_agent_timestamp?: Record<string, string>;
  } | null;
  if (routerState) {
    if (routerState.last_timestamp) {
      setRouterState('last_timestamp', routerState.last_timestamp);
    }
    if (routerState.last_agent_timestamp) {
      setRouterState(
        'last_agent_timestamp',
        JSON.stringify(routerState.last_agent_timestamp),
      );
    }
  }

  // Migrate sessions.json
  const sessions = migrateFile('sessions.json') as Record<
    string,
    string
  > | null;
  if (sessions) {
    for (const [agentName, sessionId] of Object.entries(sessions)) {
      const agentRow = db
        .prepare(`SELECT jid FROM agents WHERE agent_name = ?`)
        .get(agentName) as { jid: string } | undefined;
      if (!agentRow) {
        logger.warn(
          { agentName },
          'Skipping migrated session without matching registered agent',
        );
        continue;
      }
      setSession(agentRow.jid, null, agentName, sessionId);
    }
  }

  // Migrate registered_groups.json
  const groups = migrateFile('registered_groups.json') as Record<
    string,
    RegisteredAgent & { folder?: string }
  > | null;
  if (groups) {
    for (const [jid, group] of Object.entries(groups)) {
      const normalizedGroup: RegisteredAgent = {
        ...group,
        agentName: group.agentName || group.folder || '',
      };
      try {
        setRegisteredAgent(jid, normalizedGroup);
      } catch (err) {
        logger.warn(
          { jid, agentName: normalizedGroup.agentName, err },
          'Skipping migrated registered agent with invalid name',
        );
      }
    }
  }
}
