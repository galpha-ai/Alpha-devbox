import fs from 'fs';
import path from 'path';

import {
  ASSISTANT_NAME,
  IDLE_TIMEOUT,
  POLL_INTERVAL,
  SLACK_APP_TOKEN,
  SLACK_BOT_TOKEN,
  TELEGRAM_BOT_TOKEN,
  TRIGGER_PATTERN,
  WEB_ENABLED,
  WEB_PORT,
  getRegisteredAgents,
  loadConfig,
} from './config.js';
import { SlackChannel } from './channels/slack.js';
import { WebChannel } from './channels/web.js';
import { TelegramChannel } from './channels/telegram.js';
import {
  ContainerOutput,
  runContainerAgent,
  writeGroupsSnapshot,
  writeTasksSnapshot,
} from './container-runner.js';
import {
  ContainerRuntime,
  createContainerRuntime,
} from './container-runtime.js';
import {
  deleteSession,
  getAllChats,
  getAllRegisteredAgents,
  getAllSessions,
  getAllTasks,
  getMessagesSince,
  getNewMessages,
  getRouterState,
  initDatabase,
  makeSessionScopeKey,
  parseSessionScopeKey,
  setRegisteredAgent,
  setRouterState,
  setSession,
  storeChatMetadata,
  storeMessage,
} from './db.js';
import { SessionQueue } from './session-queue.js';
import { resolveAgentPath, resolveSessionPath } from './agent-folder.js';
import { startIpcWatcher } from './ipc.js';
import { startSessionGc } from './session-gc.js';
import { findChannel, formatMessages, formatOutbound } from './router.js';
import {
  applyCleanedSessionControlState,
  cleanupSessionScope,
  parseSessionControlCommand,
} from './session-control.js';
import { SessionScope } from './session-scope.js';
import { startSchedulerLoop } from './task-scheduler.js';
import {
  Channel,
  NewMessage,
  RegisteredAgent,
  StatusIndicatorOptions,
} from './types.js';
import { logger } from './logger.js';

// Re-export for backwards compatibility during refactor
export { escapeXml, formatMessages } from './router.js';

let lastTimestamp = '';
let sessions: Record<string, string> = {};
let registeredAgents: Record<string, RegisteredAgent> = {};
let lastAgentTimestamp: Record<string, string> = {};
let messageLoopRunning = false;
const statusIndicatorTargets = new Map<string, StatusIndicatorOptions>();

const channels: Channel[] = [];
const queue = new SessionQueue();
let containerRuntime: ContainerRuntime | null = null;
const STARTUP_RECOVERY_MAX_AGE_MS = 6 * 60 * 60 * 1000;
const RECOVERY_LOG_CONTENT_PREVIEW_CHARS = 160;
const CHANNEL_RESUME_RECOVERY_CONTEXT_MESSAGES = 2;

function scopeForMessage(msg: NewMessage, agentName: string): SessionScope {
  return {
    channelId: msg.chat_jid,
    threadId: msg.thread_id || null,
    agentName,
  };
}

function requiresTrigger(
  agent: RegisteredAgent,
  scope: SessionScope,
  sessionKey: string,
): boolean {
  if (agent.requiresTrigger === false) return false;

  // When requires_trigger is true, always check for trigger pattern
  // regardless of whether thread session is active
  return true;
}

export function shouldReplyThreadReclaimed(
  scope: SessionScope,
  sessionKey: string,
  sessionDirExists: boolean,
  knownSessions: Record<string, string>,
  knownAgentTimestamps: Record<string, string>,
): boolean {
  if (!scope.threadId || sessionDirExists) return false;
  return Boolean(knownSessions[sessionKey] || knownAgentTimestamps[sessionKey]);
}

function hasSessionContext(sessionKey: string): boolean {
  return Boolean(sessions[sessionKey] || lastAgentTimestamp[sessionKey]);
}

function setStatusIndicatorTarget(
  sessionKey: string,
  target: StatusIndicatorOptions | undefined,
): void {
  if (target?.messageId) {
    statusIndicatorTargets.set(sessionKey, target);
    return;
  }
  statusIndicatorTargets.delete(sessionKey);
}

async function setChannelStatus(
  channel: Channel,
  chatJid: string,
  sessionKey: string,
  status: 'processing' | 'success' | 'error' | 'idle',
): Promise<void> {
  await channel.setTyping?.(
    chatJid,
    status,
    statusIndicatorTargets.get(sessionKey),
  );
}

export function shouldRecoverPendingMessages(
  pending: Array<{ timestamp: string }>,
  nowMs = Date.now(),
  maxAgeMs = STARTUP_RECOVERY_MAX_AGE_MS,
): boolean {
  if (pending.length === 0) return false;

  const newestPendingAt = Date.parse(pending[pending.length - 1].timestamp);
  if (!Number.isFinite(newestPendingAt)) return true;

  return nowMs - newestPendingAt <= maxAgeMs;
}

function truncateRecoveryLogContent(
  content: string,
  maxChars = RECOVERY_LOG_CONTENT_PREVIEW_CHARS,
): string {
  const normalized = content.replace(/\s+/g, ' ').trim();
  if (normalized.length <= maxChars) return normalized;
  if (maxChars <= 3) return normalized.slice(0, maxChars);
  return `${normalized.slice(0, maxChars - 3)}...`;
}

export function planStaleResumeRecovery(
  scope: SessionScope,
  missedMessages: NewMessage[],
  previousCursor: string,
  contextMessages = CHANNEL_RESUME_RECOVERY_CONTEXT_MESSAGES,
): {
  cursor?: string;
  replayCount: number;
  droppedCount: number;
  anchorMessageId?: string;
} {
  if (scope.threadId) {
    return {
      cursor: previousCursor || undefined,
      replayCount: missedMessages.length,
      droppedCount: 0,
    };
  }

  if (missedMessages.length === 0) {
    return {
      cursor: previousCursor || undefined,
      replayCount: 0,
      droppedCount: 0,
    };
  }

  let anchorIndex = missedMessages.length - 1;
  for (let i = missedMessages.length - 1; i >= 0; i--) {
    if (TRIGGER_PATTERN.test(missedMessages[i].content.trim())) {
      anchorIndex = i;
      break;
    }
  }

  const startIndex = Math.max(0, anchorIndex - contextMessages);
  return {
    cursor:
      startIndex > 0
        ? missedMessages[startIndex - 1].timestamp
        : previousCursor || undefined,
    replayCount: missedMessages.length - startIndex,
    droppedCount: startIndex,
    anchorMessageId: missedMessages[anchorIndex]?.id,
  };
}

export function summarizePendingRecoveryMessages(
  pending: NewMessage[],
  threadId: string | null,
  maxChars = RECOVERY_LOG_CONTENT_PREVIEW_CHARS,
): Array<{
  id: string;
  sender: string;
  senderId: string;
  timestamp: string;
  contentPreview: string;
  role?: 'thread_parent';
}> {
  return pending.map((msg) => {
    const summary = {
      id: msg.id,
      sender: msg.sender_name,
      senderId: msg.sender,
      timestamp: msg.timestamp,
      contentPreview: truncateRecoveryLogContent(msg.content, maxChars),
    };
    if (threadId && msg.id === threadId && !msg.thread_id) {
      return { ...summary, role: 'thread_parent' as const };
    }
    return summary;
  });
}

function formatSessionControlCommandReply(
  command: ReturnType<typeof parseSessionControlCommand>,
  result: Awaited<ReturnType<typeof cleanupSessionScope>>,
  ignoredLaterMessages = false,
): string {
  if (result.status === 'warning') {
    return `This session has uncommitted changes in ${result.dirtyRepos
      .map((repo) => `\`${repo}\``)
      .join(', ')}. Re-run \`/done --force\` to discard them and clean up.`;
  }

  const action =
    command?.name === 'reset' ? 'Reset the session' : 'Ended the session';

  if (result.dirtyRepos.length > 0) {
    const base = `${action} and discarded uncommitted changes in ${result.dirtyRepos
      .map((repo) => `\`${repo}\``)
      .join(', ')}.`;
    return ignoredLaterMessages
      ? `${base} Re-send any message you sent after the command to start a fresh session.`
      : base;
  }

  return ignoredLaterMessages
    ? `${action} and cleaned up the workspace. Re-send any message you sent after the command to start a fresh session.`
    : `${action} and cleaned up the workspace.`;
}

function normalizeLastAgentTimestamps(
  value: Record<string, string>,
): Record<string, string> {
  const normalized: Record<string, string> = {};
  for (const [key, timestamp] of Object.entries(value)) {
    if (key.includes('::')) {
      normalized[key] = timestamp;
      continue;
    }

    // Backward compatibility: old state keyed by chat JID.
    const agent = registeredAgents[key];
    if (!agent) continue;
    const scopeKey = makeSessionScopeKey(key, null, agent.agentName);
    normalized[scopeKey] = timestamp;
  }
  return normalized;
}

function loadState(): void {
  lastTimestamp = getRouterState('last_timestamp') || '';
  sessions = getAllSessions();
  const configuredAgents = getRegisteredAgents();
  const persistedAgents = getAllRegisteredAgents();
  registeredAgents = { ...configuredAgents };

  // Runtime DM bindings are persisted; restore them on startup.
  for (const [jid, agent] of Object.entries(persistedAgents)) {
    if (!jid.startsWith('tg:user:')) continue;
    if (registeredAgents[jid]) continue;
    registeredAgents[jid] = agent;
  }

  const agentTs = getRouterState('last_agent_timestamp');
  try {
    const parsed = agentTs
      ? (JSON.parse(agentTs) as Record<string, string>)
      : {};
    lastAgentTimestamp = normalizeLastAgentTimestamps(parsed);
  } catch {
    logger.warn('Corrupted last_agent_timestamp in DB, resetting');
    lastAgentTimestamp = {};
  }

  // Ensure agent directories exist on disk.
  for (const agent of Object.values(registeredAgents)) {
    const agentDir = resolveAgentPath(agent.agentName);
    fs.mkdirSync(path.join(agentDir, 'logs'), { recursive: true });
  }

  logger.info(
    { agentCount: Object.keys(registeredAgents).length },
    'State loaded',
  );
}

function saveState(): void {
  setRouterState('last_timestamp', lastTimestamp);
  setRouterState('last_agent_timestamp', JSON.stringify(lastAgentTimestamp));
}

/**
 * Get available groups list for the agent.
 * Returns groups ordered by most recent activity.
 */
export function getAvailableGroups(): import('./container-runner.js').AvailableGroup[] {
  const chats = getAllChats();
  const registeredJids = new Set(Object.keys(registeredAgents));

  return chats
    .filter((c) => c.jid !== '__group_sync__' && c.is_group)
    .map((c) => ({
      jid: c.jid,
      name: c.name,
      lastActivity: c.last_message_time,
      isRegistered: registeredJids.has(c.jid),
    }));
}

/** @internal - exported for testing */
export function _setRegisteredAgents(
  agents: Record<string, RegisteredAgent>,
): void {
  registeredAgents = agents;
}

/**
 * Process all pending messages for a session.
 * Called by the SessionQueue when it's this session's turn.
 */
async function processSessionMessages(sessionKey: string): Promise<boolean> {
  const psmStart = Date.now();
  const psmElapsed = () => `${Date.now() - psmStart}ms`;
  logger.info(
    { sessionKey },
    `[${psmElapsed()}] processSessionMessages called`,
  );

  const scope = parseSessionScopeKey(sessionKey);
  if (!scope) {
    logger.warn({ sessionKey }, 'Invalid session key, skipping');
    return true;
  }

  const chatJid = scope.channelId;
  const agent = registeredAgents[chatJid];
  if (!agent || agent.agentName !== scope.agentName) {
    logger.info(
      { sessionKey, chatJid, agentName: scope.agentName },
      `[${psmElapsed()}] No matching agent, skipping`,
    );
    return true;
  }

  const channel = findChannel(channels, chatJid);
  if (!channel) {
    logger.warn(
      { chatJid },
      `[${psmElapsed()}] No channel owns JID, skipping messages`,
    );
    return true;
  }

  // Check if a thread-scoped session was GC'd (directory removed).
  if (scope.threadId) {
    const sessionDir = resolveSessionPath(scope.agentName, sessionKey);
    const sessionDirExists = fs.existsSync(sessionDir);
    if (
      shouldReplyThreadReclaimed(
        scope,
        sessionKey,
        sessionDirExists,
        sessions,
        lastAgentTimestamp,
      )
    ) {
      logger.info(
        { sessionKey, threadId: scope.threadId },
        "Session directory missing (GC'd), sending error reply",
      );
      await channel.sendMessage(
        chatJid,
        "This thread's workspace has been reclaimed after inactivity. Please start a new thread to continue.",
        { threadId: scope.threadId },
      );
      statusIndicatorTargets.delete(sessionKey);
      delete sessions[sessionKey];
      delete lastAgentTimestamp[sessionKey];
      saveState();
      return true;
    }
    if (!sessionDirExists) {
      logger.info(
        { sessionKey, threadId: scope.threadId },
        'Thread session directory missing with no persisted state; treating as new thread',
      );
    }
  }

  const sinceTimestamp = lastAgentTimestamp[sessionKey] || '';
  logger.info(
    { sessionKey, sinceTimestamp },
    `[${psmElapsed()}] Fetching messages since cursor`,
  );
  const includeThreadParent =
    scope.threadId !== null && !hasSessionContext(sessionKey);
  const missedMessages = getMessagesSince(
    chatJid,
    sinceTimestamp,
    ASSISTANT_NAME,
    scope.threadId,
    { includeThreadParent },
  );

  if (missedMessages.length === 0) {
    logger.info(
      { sessionKey },
      `[${psmElapsed()}] No missed messages, returning`,
    );
    return true;
  }

  logger.info(
    { sessionKey, missedCount: missedMessages.length },
    `[${psmElapsed()}] Found missed messages`,
  );

  if (requiresTrigger(agent, scope, sessionKey)) {
    const hasTrigger = missedMessages.some((m) =>
      TRIGGER_PATTERN.test(m.content.trim()),
    );
    if (!hasTrigger) {
      logger.info(
        { sessionKey },
        `[${psmElapsed()}] Trigger required but not found, skipping`,
      );
      return true;
    }
    logger.info({ sessionKey }, `[${psmElapsed()}] Trigger found`);
  }

  const prompt = formatMessages(missedMessages);
  setStatusIndicatorTarget(sessionKey, {
    messageId: missedMessages[missedMessages.length - 1].id,
    threadId: scope.threadId,
  });
  logger.info(
    { sessionKey, promptLength: prompt.length },
    `[${psmElapsed()}] Prompt formatted`,
  );

  // Advance cursor so the piping path in startMessageLoop won't re-fetch
  // these messages. Save the old cursor so we can roll back on error.
  const previousCursor = lastAgentTimestamp[sessionKey] || '';
  lastAgentTimestamp[sessionKey] =
    missedMessages[missedMessages.length - 1].timestamp;
  saveState();

  logger.info(
    { agent: agent.name, messageCount: missedMessages.length },
    `[${psmElapsed()}] Processing messages, calling runAgent`,
  );

  // Track idle timer for closing stdin when agent is idle.
  let idleTimer: ReturnType<typeof setTimeout> | null = null;

  const resetIdleTimer = () => {
    if (idleTimer) clearTimeout(idleTimer);
    idleTimer = setTimeout(() => {
      logger.debug(
        { agent: agent.name },
        'Idle timeout, closing container stdin',
      );
      queue.closeStdin(sessionKey);
    }, IDLE_TIMEOUT);
  };

  logger.info(
    { sessionKey },
    `[${psmElapsed()}] Setting typing, calling runAgent`,
  );
  await setChannelStatus(channel, chatJid, sessionKey, 'processing');
  let hadError = false;
  let outputSentToUser = false;
  let finalStatusSent = false;

  const output = await runAgent(
    agent,
    prompt,
    scope,
    async (result: ContainerOutput) => {
      // Streaming output callback — called for each agent result.
      if (result.result) {
        const raw =
          typeof result.result === 'string'
            ? result.result
            : JSON.stringify(result.result);
        const text = raw.replace(/<internal>[\s\S]*?<\/internal>/g, '').trim();
        logger.info(
          { agent: agent.name },
          `Agent output: ${raw.slice(0, 200)}`,
        );
        if (text) {
          const timestamp = new Date().toISOString();
          storeMessage({
            id: `bot-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
            chat_jid: chatJid,
            thread_id: scope.threadId,
            sender: ASSISTANT_NAME,
            sender_name: ASSISTANT_NAME,
            content: text,
            timestamp,
            is_from_me: true,
            is_bot_message: true,
          });
          await channel.sendMessage(chatJid, text, {
            threadId: scope.threadId,
          });
          outputSentToUser = true;
        }
        // Only reset idle timer on actual results, not session-update markers (result: null).
        resetIdleTimer();
      }

      if (result.status === 'success') {
        queue.notifyIdle(sessionKey);
        if (!finalStatusSent) {
          await setChannelStatus(channel, chatJid, sessionKey, 'success');
          finalStatusSent = true;
        }
      }

      if (result.status === 'error') {
        hadError = true;
        if (!finalStatusSent) {
          await setChannelStatus(channel, chatJid, sessionKey, 'error');
          finalStatusSent = true;
        }
      }
    },
  );

  logger.info(
    { sessionKey, output, hadError },
    `[${psmElapsed()}] runAgent finished`,
  );
  if (!finalStatusSent) {
    const finalStatus =
      output.status === 'error' || hadError ? 'error' : 'success';
    await setChannelStatus(channel, chatJid, sessionKey, finalStatus);
  }
  if (idleTimer) clearTimeout(idleTimer);
  statusIndicatorTargets.delete(sessionKey);

  if (output.status === 'error' || hadError) {
    if (output.errorKind === 'stale_session_resume' && !outputSentToUser) {
      const recoveryPlan = planStaleResumeRecovery(
        scope,
        missedMessages,
        previousCursor,
      );
      delete sessions[sessionKey];
      deleteSession(scope.channelId, scope.threadId, scope.agentName);
      if (recoveryPlan.cursor) {
        lastAgentTimestamp[sessionKey] = recoveryPlan.cursor;
      } else {
        delete lastAgentTimestamp[sessionKey];
      }
      saveState();
      logger.warn(
        {
          agent: agent.name,
          sessionKey,
          threadId: scope.threadId,
          droppedCount: recoveryPlan.droppedCount,
          replayCount: recoveryPlan.replayCount,
          anchorMessageId: recoveryPlan.anchorMessageId,
        },
        'Cleared stale Claude session ID after resume failure; re-enqueueing without retry backoff',
      );
      queue.enqueueMessageCheck(sessionKey);
      return true;
    }

    if (output.errorKind === 'seed_clone_failed') {
      if (!outputSentToUser) {
        const timestamp = new Date().toISOString();
        const text =
          'Failed to start the workspace because the seed repo clone timed out or failed. Check runner network access to the repo host and retry.';
        storeMessage({
          id: `bot-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
          chat_jid: chatJid,
          thread_id: scope.threadId,
          sender: ASSISTANT_NAME,
          sender_name: ASSISTANT_NAME,
          content: text,
          timestamp,
          is_from_me: true,
          is_bot_message: true,
        });
        await channel.sendMessage(chatJid, text, {
          threadId: scope.threadId,
        });
      }
      logger.warn(
        { agent: agent.name, sessionKey, threadId: scope.threadId },
        'Seed repo clone failed; skipping automatic retry',
      );
      return true;
    }

    // If output was already sent to the user, don't roll back the cursor.
    if (outputSentToUser) {
      logger.warn(
        { agent: agent.name },
        'Agent error after output was sent, skipping cursor rollback to prevent duplicates',
      );
      return true;
    }

    // Roll back cursor so retries can re-process these messages.
    lastAgentTimestamp[sessionKey] = previousCursor;
    saveState();
    logger.warn(
      { agent: agent.name },
      'Agent error, rolled back message cursor for retry',
    );
    return false;
  }

  return true;
}

async function runAgent(
  agent: RegisteredAgent,
  prompt: string,
  scope: SessionScope,
  onOutput?: (output: ContainerOutput) => Promise<void>,
): Promise<{
  status: 'success' | 'error';
  errorKind?: ContainerOutput['errorKind'];
}> {
  const raStart = Date.now();
  const raElapsed = () => `${Date.now() - raStart}ms`;
  logger.info({ agent: agent.name }, `[${raElapsed()}] runAgent called`);

  if (!containerRuntime) {
    throw new Error('Container runtime is not initialized');
  }
  const sessionKey = makeSessionScopeKey(
    scope.channelId,
    scope.threadId,
    scope.agentName,
  );
  const sessionId = sessions[sessionKey];
  logger.info(
    { agent: agent.name, sessionKey, sessionId },
    `[${raElapsed()}] Session resolved`,
  );

  // Update tasks snapshot for container to read (filtered by agent).
  const tasks = getAllTasks();
  writeTasksSnapshot(
    agent.agentName,
    sessionKey,
    tasks.map((t) => ({
      id: t.id,
      agentName: t.agentName,
      prompt: t.prompt,
      schedule_type: t.schedule_type,
      schedule_value: t.schedule_value,
      status: t.status,
      next_run: t.next_run,
    })),
  );
  logger.info(
    { agent: agent.name, taskCount: tasks.length },
    `[${raElapsed()}] Tasks snapshot written`,
  );

  // Update available groups snapshot (main agent only can see all groups).
  const availableGroups = getAvailableGroups();
  writeGroupsSnapshot(agent.agentName, sessionKey);
  logger.info(
    { agent: agent.name, groupCount: availableGroups.length },
    `[${raElapsed()}] Groups snapshot written`,
  );

  // Wrap onOutput to track session ID from streamed results.
  const wrappedOnOutput = onOutput
    ? async (output: ContainerOutput) => {
        if (output.newSessionId) {
          sessions[sessionKey] = output.newSessionId;
          setSession(
            scope.channelId,
            scope.threadId,
            scope.agentName,
            output.newSessionId,
          );
        }
        await onOutput(output);
      }
    : undefined;

  try {
    logger.info(
      { agent: agent.name, promptLength: prompt.length },
      `[${raElapsed()}] Calling runContainerAgent`,
    );
    const output = await runContainerAgent(
      containerRuntime,
      agent,
      {
        prompt,
        sessionKey,
        sessionId,
        agentName: agent.agentName,
        chatJid: scope.channelId,
        threadId: scope.threadId,
        assistantName: ASSISTANT_NAME,
      },
      (containerName) =>
        queue.registerProcess(sessionKey, containerName, agent.agentName),
      wrappedOnOutput,
    );
    logger.info(
      { agent: agent.name, status: output.status },
      `[${raElapsed()}] runContainerAgent returned`,
    );

    if (output.newSessionId) {
      sessions[sessionKey] = output.newSessionId;
      setSession(
        scope.channelId,
        scope.threadId,
        scope.agentName,
        output.newSessionId,
      );
    }

    if (output.status === 'error') {
      logger.error(
        { agent: agent.name, error: output.error },
        `[${raElapsed()}] Container agent error`,
      );
      return { status: 'error', errorKind: output.errorKind };
    }

    logger.info(
      { agent: agent.name },
      `[${raElapsed()}] runAgent completed successfully`,
    );
    return { status: 'success' };
  } catch (err) {
    logger.error({ agent: agent.name, err }, `[${raElapsed()}] Agent error`);
    return { status: 'error' };
  }
}

async function startMessageLoop(): Promise<void> {
  if (messageLoopRunning) {
    logger.debug('Message loop already running, skipping duplicate start');
    return;
  }
  messageLoopRunning = true;

  logger.info(`Devbox Agent running (trigger: @${ASSISTANT_NAME})`);

  while (true) {
    try {
      const jids = Object.keys(registeredAgents);
      const { messages, newTimestamp } = getNewMessages(
        jids,
        lastTimestamp,
        ASSISTANT_NAME,
      );

      logger.debug(
        { jids, lastTimestamp, messageCount: messages.length, newTimestamp },
        'Message loop poll',
      );

      if (messages.length > 0) {
        logger.info({ count: messages.length }, 'New messages');

        // Advance the "seen" cursor for all messages immediately.
        lastTimestamp = newTimestamp;
        saveState();

        // Deduplicate by session scope (channel + thread + agent).
        const messagesBySession = new Map<
          string,
          { scope: SessionScope; messages: NewMessage[] }
        >();
        for (const msg of messages) {
          const agent = registeredAgents[msg.chat_jid];
          if (!agent) {
            logger.info(
              { chatJid: msg.chat_jid },
              'No agent registered for JID, skipping',
            );
            continue;
          }

          const scope = scopeForMessage(msg, agent.agentName);
          const sessionKey = makeSessionScopeKey(
            scope.channelId,
            scope.threadId,
            scope.agentName,
          );
          logger.info(
            { sessionKey, agent: agent.name, chatJid: msg.chat_jid },
            'Message mapped to session',
          );
          const existing = messagesBySession.get(sessionKey);
          if (existing) {
            existing.messages.push(msg);
          } else {
            messagesBySession.set(sessionKey, { scope, messages: [msg] });
          }
        }

        for (const [sessionKey, batch] of messagesBySession) {
          const { scope, messages: channelMessages } = batch;
          const chatJid = scope.channelId;
          const agent = registeredAgents[chatJid];
          if (!agent) {
            logger.info(
              { chatJid, sessionKey },
              'No agent for chatJid in batch, skipping',
            );
            continue;
          }

          const channel = findChannel(channels, chatJid);
          if (!channel) {
            logger.warn({ chatJid }, 'No channel owns JID, skipping messages');
            continue;
          }

          const controlIndex = channelMessages.findIndex((msg) =>
            Boolean(parseSessionControlCommand(msg.content)),
          );
          if (controlIndex !== -1) {
            const commandMessage = channelMessages[controlIndex];
            const command = parseSessionControlCommand(commandMessage.content);
            if (!command) continue;
            if (!containerRuntime) {
              throw new Error('Container runtime is not initialized');
            }

            lastAgentTimestamp[sessionKey] = commandMessage.timestamp;
            saveState();

            const result = await cleanupSessionScope(sessionKey, scope, {
              force: command.force,
              runtime: containerRuntime,
              queue,
            });
            const hasLaterMessages = controlIndex < channelMessages.length - 1;
            const ignoredLaterMessages =
              result.status === 'cleaned' &&
              result.stoppedActiveContainer &&
              hasLaterMessages;
            if (result.status === 'cleaned') {
              statusIndicatorTargets.delete(sessionKey);
              applyCleanedSessionControlState(
                sessionKey,
                commandMessage.timestamp,
                {
                  sessions,
                  lastAgentTimestamps: lastAgentTimestamp,
                },
                ignoredLaterMessages
                  ? channelMessages[channelMessages.length - 1].timestamp
                  : undefined,
              );
              saveState();
            }
            await channel.sendMessage(
              chatJid,
              formatSessionControlCommandReply(
                command,
                result,
                ignoredLaterMessages,
              ),
              {
                threadId: scope.threadId,
              },
            );

            if (hasLaterMessages && !ignoredLaterMessages) {
              queue.enqueueMessageCheck(sessionKey);
            }
            continue;
          }

          if (requiresTrigger(agent, scope, sessionKey)) {
            const hasTrigger = channelMessages.some((m) =>
              TRIGGER_PATTERN.test(m.content.trim()),
            );
            if (!hasTrigger) {
              logger.info(
                { sessionKey, agent: agent.name },
                'No trigger found, skipping',
              );
              continue;
            }
            logger.info({ sessionKey, agent: agent.name }, 'Trigger matched');
          }

          // Pull all messages since lastAgentTimestamp so non-trigger
          // context that accumulated between triggers is included.
          const allPending = getMessagesSince(
            chatJid,
            lastAgentTimestamp[sessionKey] || '',
            ASSISTANT_NAME,
            scope.threadId,
            {
              includeThreadParent:
                scope.threadId !== null && !hasSessionContext(sessionKey),
            },
          );
          const messagesToSend =
            allPending.length > 0 ? allPending : channelMessages;
          const formatted = formatMessages(messagesToSend);

          if (queue.sendMessage(sessionKey, formatted)) {
            logger.info(
              {
                chatJid,
                threadId: scope.threadId,
                count: messagesToSend.length,
              },
              'Piped messages to active container',
            );
            lastAgentTimestamp[sessionKey] =
              messagesToSend[messagesToSend.length - 1].timestamp;
            saveState();
            setStatusIndicatorTarget(sessionKey, {
              messageId: messagesToSend[messagesToSend.length - 1].id,
              threadId: scope.threadId,
            });
            channel
              .setTyping?.(
                chatJid,
                'processing',
                statusIndicatorTargets.get(sessionKey),
              )
              ?.catch((err) =>
                logger.warn({ chatJid, err }, 'Failed to set typing indicator'),
              );
          } else {
            // No active container — check if thread session was GC'd.
            if (scope.threadId) {
              const sessionDir = resolveSessionPath(
                scope.agentName,
                sessionKey,
              );
              const sessionDirExists = fs.existsSync(sessionDir);
              if (
                shouldReplyThreadReclaimed(
                  scope,
                  sessionKey,
                  sessionDirExists,
                  sessions,
                  lastAgentTimestamp,
                )
              ) {
                logger.info(
                  { sessionKey, threadId: scope.threadId },
                  "Session directory missing (GC'd), sending error reply",
                );
                statusIndicatorTargets.delete(sessionKey);
                channel
                  .sendMessage(
                    chatJid,
                    "This thread's workspace has been reclaimed after inactivity. Please start a new thread to continue.",
                    { threadId: scope.threadId },
                  )
                  .catch((err) =>
                    logger.warn(
                      { chatJid, err },
                      'Failed to send GC error reply',
                    ),
                  );
                delete sessions[sessionKey];
                delete lastAgentTimestamp[sessionKey];
                saveState();
                continue;
              }
              if (!sessionDirExists) {
                logger.info(
                  { sessionKey, threadId: scope.threadId },
                  'Thread session directory missing with no persisted state; treating as new thread',
                );
              }
            }
            logger.info(
              { sessionKey, agent: agent.name },
              'No active container, enqueuing message check',
            );
            queue.enqueueMessageCheck(sessionKey);
          }
        }
      }
    } catch (err) {
      logger.error({ err }, 'Error in message loop');
    }
    await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL));
  }
}

/**
 * Startup recovery: check for unprocessed messages in registered sessions.
 * Handles crash between advancing lastTimestamp and processing messages.
 */
function recoverPendingMessages(): void {
  const candidateScopeKeys = new Set<string>();

  for (const [chatJid, agent] of Object.entries(registeredAgents)) {
    candidateScopeKeys.add(makeSessionScopeKey(chatJid, null, agent.agentName));
  }
  for (const sessionKey of Object.keys(sessions)) {
    candidateScopeKeys.add(sessionKey);
  }
  for (const sessionKey of Object.keys(lastAgentTimestamp)) {
    candidateScopeKeys.add(sessionKey);
  }

  for (const sessionKey of candidateScopeKeys) {
    const scope = parseSessionScopeKey(sessionKey);
    if (!scope) continue;

    const agent = registeredAgents[scope.channelId];
    if (!agent || agent.agentName !== scope.agentName) continue;

    const sinceTimestamp = lastAgentTimestamp[sessionKey] || '';
    const pending = getMessagesSince(
      scope.channelId,
      sinceTimestamp,
      ASSISTANT_NAME,
      scope.threadId,
      {
        includeThreadParent:
          scope.threadId !== null && !hasSessionContext(sessionKey),
      },
    );
    if (shouldRecoverPendingMessages(pending)) {
      logger.info(
        {
          agent: agent.name,
          chatJid: scope.channelId,
          threadId: scope.threadId,
          pendingCount: pending.length,
          pendingMessages: summarizePendingRecoveryMessages(
            pending,
            scope.threadId,
          ),
        },
        'Recovery: found unprocessed messages',
      );
      queue.enqueueMessageCheck(sessionKey);
    } else if (pending.length > 0) {
      logger.info(
        {
          agent: agent.name,
          chatJid: scope.channelId,
          threadId: scope.threadId,
          pendingCount: pending.length,
          newestPendingTimestamp: pending[pending.length - 1].timestamp,
          maxAgeMs: STARTUP_RECOVERY_MAX_AGE_MS,
        },
        'Recovery: skipping stale pending messages',
      );
    }
  }
}

async function ensureContainerSystemRunning(): Promise<ContainerRuntime> {
  const runtime = createContainerRuntime();
  await runtime.ensureRunning();
  await runtime.cleanupOrphans();
  return runtime;
}

async function main(): Promise<void> {
  const configIdx = process.argv.indexOf('--config');
  if (configIdx === -1 || !process.argv[configIdx + 1]) {
    console.error('Usage: devbox-agent --config <path>');
    process.exit(1);
  }
  loadConfig(process.argv[configIdx + 1]);

  const runtime = await ensureContainerSystemRunning();
  containerRuntime = runtime;
  initDatabase();
  logger.info('Database initialized');
  loadState();

  // Graceful shutdown handlers.
  const shutdown = async (signal: string) => {
    logger.info({ signal }, 'Shutdown signal received');
    await queue.shutdown(10000);
    for (const ch of channels) await ch.disconnect();
    process.exit(0);
  };
  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT', () => shutdown('SIGINT'));

  // Channel callbacks (shared by all channels).
  const channelOpts = {
    onMessage: (_chatJid: string, msg: NewMessage) => {
      logger.info(
        {
          chatJid: _chatJid,
          sender: msg.sender_name,
          timestamp: msg.timestamp,
          isBotMsg: msg.is_bot_message,
        },
        'onMessage: storing message to SQLite',
      );
      storeMessage(msg);
      logger.info({ chatJid: _chatJid }, 'onMessage: message stored');
    },
    onChatMetadata: (
      chatJid: string,
      timestamp: string,
      name?: string,
      channel?: string,
      isGroup?: boolean,
    ) => storeChatMetadata(chatJid, timestamp, name, channel, isGroup),
    registeredAgents: () => registeredAgents,
    registerAgentForChat: (chatJid: string, agent: RegisteredAgent) => {
      registeredAgents[chatJid] = agent;
      setRegisteredAgent(chatJid, agent);
      logger.info(
        { chatJid, agentName: agent.agentName },
        'Registered dynamic agent binding',
      );
    },
  };

  const configuredJids = Object.keys(registeredAgents);
  const wantsTelegram = configuredJids.some((jid) => jid.startsWith('tg:'));
  const wantsSlack = configuredJids.some((jid) => jid.startsWith('slack:'));

  if (wantsTelegram) {
    if (!TELEGRAM_BOT_TOKEN) {
      throw new Error('telegram_bot_token is required for tg:* channels');
    }
    channels.push(new TelegramChannel(TELEGRAM_BOT_TOKEN, channelOpts));
  }

  if (wantsSlack) {
    if (!SLACK_BOT_TOKEN || !SLACK_APP_TOKEN) {
      throw new Error(
        'slack_bot_token and slack_app_token are required for slack:* channels',
      );
    }
    channels.push(
      new SlackChannel(SLACK_BOT_TOKEN, SLACK_APP_TOKEN, channelOpts),
    );
  }

  const wantsWeb =
    WEB_ENABLED || configuredJids.some((jid) => jid.startsWith('web:'));

  if (wantsWeb) {
    channels.push(
      new WebChannel(WEB_PORT, {
        ...channelOpts,
        getActiveCount: () => queue.getActiveCount(),
        getWaitingCount: () => queue.getWaitingCount(),
      }),
    );
  }

  if (channels.length === 0) {
    throw new Error(
      'No channels were initialized. Configure tg:*, slack:*, or web:* channel bindings.',
    );
  }

  for (const channel of channels) {
    await channel.connect();
  }

  // Start subsystems (independently of connection handler).
  startSchedulerLoop({
    runtime,
    registeredAgents: () => registeredAgents,
    getSessions: () => sessions,
    queue,
    onProcess: (sessionKey, containerName, agentName) =>
      queue.registerProcess(sessionKey, containerName, agentName),
    sendMessage: async (jid, rawText) => {
      const channel = findChannel(channels, jid);
      if (!channel) {
        logger.warn({ jid }, 'No channel owns JID, cannot send message');
        return;
      }
      const text = formatOutbound(rawText);
      if (text) await channel.sendMessage(jid, text);
    },
  });
  startIpcWatcher({
    sendMessage: (jid, text, options) => {
      const channel = findChannel(channels, jid);
      if (!channel) throw new Error(`No channel for JID: ${jid}`);
      return channel.sendMessage(jid, text, options);
    },
    registeredAgents: () => registeredAgents,
  });
  startSessionGc({
    queue,
    getSessions: () => sessions,
    getLastAgentTimestamp: () => lastAgentTimestamp,
    saveState,
    interval: 10 * 60 * 1000, // scan every 10 minutes
    maxAge: 6 * 60 * 60 * 1000, // 6 hour TTL
  });
  queue.setProcessMessagesFn(processSessionMessages);
  recoverPendingMessages();
  startMessageLoop().catch((err) => {
    logger.fatal({ err }, 'Message loop crashed unexpectedly');
    process.exit(1);
  });
}

// Guard: only run when executed directly, not when imported by tests.
const isDirectRun =
  process.argv[1] &&
  new URL(import.meta.url).pathname ===
    new URL(`file://${process.argv[1]}`).pathname;

if (isDirectRun) {
  main().catch((err) => {
    logger.error({ err }, 'Failed to start Devbox Agent');
    process.exit(1);
  });
}
