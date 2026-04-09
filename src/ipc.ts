import fs from 'fs';
import path from 'path';

import { CronExpressionParser } from 'cron-parser';

import {
  decodeSessionScopeKey,
  isValidAgentName,
  resolveSessionPath,
} from './agent-folder.js';
import { DATA_DIR, IPC_POLL_INTERVAL, TIMEZONE } from './config.js';
import {
  createTask,
  deleteTask,
  getTaskById,
  parseSessionScopeKey,
  updateTask,
} from './db.js';
import { logger } from './logger.js';
import { RegisteredAgent, SendMessageOptions } from './types.js';

export interface IpcDeps {
  sendMessage: (
    jid: string,
    text: string,
    options?: SendMessageOptions,
  ) => Promise<void>;
  registeredAgents: () => Record<string, RegisteredAgent>;
}

let ipcWatcherRunning = false;

interface SessionIpcContext {
  agentName: string;
  sessionKey: string;
  channelId: string;
  threadId: string | null;
  ipcDir: string;
}

function getSessionIpcContexts(): SessionIpcContext[] {
  const sessionsBaseDir = path.join(DATA_DIR, 'sessions');
  fs.mkdirSync(sessionsBaseDir, { recursive: true });

  const contexts: SessionIpcContext[] = [];
  for (const agentName of fs.readdirSync(sessionsBaseDir)) {
    if (!isValidAgentName(agentName)) continue;
    const agentDir = path.join(sessionsBaseDir, agentName);
    if (!fs.statSync(agentDir).isDirectory()) continue;

    for (const encodedSessionKey of fs.readdirSync(agentDir)) {
      const sessionDir = path.join(agentDir, encodedSessionKey);
      if (!fs.statSync(sessionDir).isDirectory()) continue;

      try {
        const sessionKey = decodeSessionScopeKey(encodedSessionKey);
        const scope = parseSessionScopeKey(sessionKey);
        if (!scope || scope.agentName !== agentName) {
          logger.warn(
            { agentName, encodedSessionKey },
            'Skipping IPC directory with invalid session scope key',
          );
          continue;
        }
        contexts.push({
          agentName,
          sessionKey,
          channelId: scope.channelId,
          threadId: scope.threadId,
          ipcDir: path.join(resolveSessionPath(agentName, sessionKey), 'ipc'),
        });
      } catch (err) {
        logger.warn(
          { agentName, encodedSessionKey, err },
          'Skipping IPC directory with unreadable session key',
        );
      }
    }
  }

  return contexts;
}

export async function processMessageIpc(
  data: {
    type: string;
    chatJid?: string;
    threadId?: string | null;
    text?: string;
  },
  source: Pick<SessionIpcContext, 'agentName' | 'channelId' | 'threadId'>,
  deps: IpcDeps,
): Promise<void> {
  if (data.type !== 'message' || !data.chatJid || !data.text) {
    return;
  }

  const normalizedThreadId = data.threadId || null;
  if (
    data.chatJid !== source.channelId ||
    normalizedThreadId !== source.threadId
  ) {
    logger.warn(
      {
        sourceAgent: source.agentName,
        sourceChannelId: source.channelId,
        sourceThreadId: source.threadId,
        targetChatJid: data.chatJid,
        targetThreadId: normalizedThreadId,
      },
      'Unauthorized IPC message attempt blocked',
    );
    return;
  }

  await deps.sendMessage(data.chatJid, data.text, {
    threadId: normalizedThreadId,
  });
  logger.info(
    {
      sourceAgent: source.agentName,
      chatJid: data.chatJid,
      threadId: normalizedThreadId,
    },
    'IPC message sent',
  );
}

export function startIpcWatcher(deps: IpcDeps): void {
  if (ipcWatcherRunning) {
    logger.debug('IPC watcher already running, skipping duplicate start');
    return;
  }
  ipcWatcherRunning = true;

  const ipcBaseDir = path.join(DATA_DIR, 'sessions');
  fs.mkdirSync(ipcBaseDir, { recursive: true });

  const processIpcFiles = async () => {
    let contexts: SessionIpcContext[];
    try {
      contexts = getSessionIpcContexts();
    } catch (err) {
      logger.error({ err }, 'Error reading IPC base directory');
      setTimeout(processIpcFiles, IPC_POLL_INTERVAL);
      return;
    }

    for (const context of contexts) {
      const messagesDir = path.join(context.ipcDir, 'messages');
      const tasksDir = path.join(context.ipcDir, 'tasks');

      try {
        if (fs.existsSync(messagesDir)) {
          const messageFiles = fs
            .readdirSync(messagesDir)
            .filter((f) => f.endsWith('.json'));
          for (const file of messageFiles) {
            const filePath = path.join(messagesDir, file);
            try {
              const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
              await processMessageIpc(data, context, deps);
              fs.unlinkSync(filePath);
            } catch (err) {
              logger.error(
                { file, sourceAgent: context.agentName, err },
                'Error processing IPC message',
              );
              const errorDir = path.join(DATA_DIR, 'ipc-errors');
              fs.mkdirSync(errorDir, { recursive: true });
              fs.renameSync(
                filePath,
                path.join(errorDir, `${context.agentName}-${file}`),
              );
            }
          }
        }
      } catch (err) {
        logger.error(
          { err, sourceAgent: context.agentName },
          'Error reading IPC messages directory',
        );
      }

      try {
        if (fs.existsSync(tasksDir)) {
          const taskFiles = fs
            .readdirSync(tasksDir)
            .filter((f) => f.endsWith('.json'));
          for (const file of taskFiles) {
            const filePath = path.join(tasksDir, file);
            try {
              const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
              await processTaskIpc(data, context.agentName, deps);
              fs.unlinkSync(filePath);
            } catch (err) {
              logger.error(
                { file, sourceAgent: context.agentName, err },
                'Error processing IPC task',
              );
              const errorDir = path.join(DATA_DIR, 'ipc-errors');
              fs.mkdirSync(errorDir, { recursive: true });
              fs.renameSync(
                filePath,
                path.join(errorDir, `${context.agentName}-${file}`),
              );
            }
          }
        }
      } catch (err) {
        logger.error(
          { err, sourceAgent: context.agentName },
          'Error reading IPC tasks directory',
        );
      }
    }

    setTimeout(processIpcFiles, IPC_POLL_INTERVAL);
  };

  processIpcFiles();
  logger.info('IPC watcher started (per-session namespaces)');
}

export async function processTaskIpc(
  data: {
    type: string;
    taskId?: string;
    prompt?: string;
    schedule_type?: string;
    schedule_value?: string;
    context_mode?: string;
    agentName?: string;
    chatJid?: string;
    targetJid?: string;
  },
  sourceGroup: string, // Verified identity from IPC directory
  deps: IpcDeps,
): Promise<void> {
  const registeredAgents = deps.registeredAgents();

  switch (data.type) {
    case 'schedule_task':
      if (
        data.prompt &&
        data.schedule_type &&
        data.schedule_value &&
        data.targetJid
      ) {
        // Resolve the target group from JID
        const targetJid = data.targetJid as string;
        const targetAgentEntry = registeredAgents[targetJid];

        if (!targetAgentEntry) {
          logger.warn(
            { targetJid },
            'Cannot schedule task: target group not registered',
          );
          break;
        }

        const targetFolder = targetAgentEntry.agentName;

        if (targetFolder !== sourceGroup) {
          logger.warn(
            { sourceGroup, targetFolder },
            'Unauthorized schedule_task attempt blocked',
          );
          break;
        }

        const scheduleType = data.schedule_type as 'cron' | 'interval' | 'once';

        let nextRun: string | null = null;
        if (scheduleType === 'cron') {
          try {
            const interval = CronExpressionParser.parse(data.schedule_value, {
              tz: TIMEZONE,
            });
            nextRun = interval.next().toISOString();
          } catch {
            logger.warn(
              { scheduleValue: data.schedule_value },
              'Invalid cron expression',
            );
            break;
          }
        } else if (scheduleType === 'interval') {
          const ms = parseInt(data.schedule_value, 10);
          if (isNaN(ms) || ms <= 0) {
            logger.warn(
              { scheduleValue: data.schedule_value },
              'Invalid interval',
            );
            break;
          }
          nextRun = new Date(Date.now() + ms).toISOString();
        } else if (scheduleType === 'once') {
          const scheduled = new Date(data.schedule_value);
          if (isNaN(scheduled.getTime())) {
            logger.warn(
              { scheduleValue: data.schedule_value },
              'Invalid timestamp',
            );
            break;
          }
          nextRun = scheduled.toISOString();
        }

        const taskId = `task-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
        const contextMode =
          data.context_mode === 'group' || data.context_mode === 'isolated'
            ? data.context_mode
            : 'isolated';
        createTask({
          id: taskId,
          agentName: targetFolder,
          chat_jid: targetJid,
          prompt: data.prompt,
          schedule_type: scheduleType,
          schedule_value: data.schedule_value,
          context_mode: contextMode,
          next_run: nextRun,
          status: 'active',
          created_at: new Date().toISOString(),
        });
        logger.info(
          { taskId, sourceGroup, targetFolder, contextMode },
          'Task created via IPC',
        );
      }
      break;

    case 'pause_task':
      if (data.taskId) {
        const task = getTaskById(data.taskId);
        if (task && task.agentName === sourceGroup) {
          updateTask(data.taskId, { status: 'paused' });
          logger.info(
            { taskId: data.taskId, sourceGroup },
            'Task paused via IPC',
          );
        } else {
          logger.warn(
            { taskId: data.taskId, sourceGroup },
            'Unauthorized task pause attempt',
          );
        }
      }
      break;

    case 'resume_task':
      if (data.taskId) {
        const task = getTaskById(data.taskId);
        if (task && task.agentName === sourceGroup) {
          updateTask(data.taskId, { status: 'active' });
          logger.info(
            { taskId: data.taskId, sourceGroup },
            'Task resumed via IPC',
          );
        } else {
          logger.warn(
            { taskId: data.taskId, sourceGroup },
            'Unauthorized task resume attempt',
          );
        }
      }
      break;

    case 'cancel_task':
      if (data.taskId) {
        const task = getTaskById(data.taskId);
        if (task && task.agentName === sourceGroup) {
          deleteTask(data.taskId);
          logger.info(
            { taskId: data.taskId, sourceGroup },
            'Task cancelled via IPC',
          );
        } else {
          logger.warn(
            { taskId: data.taskId, sourceGroup },
            'Unauthorized task cancel attempt',
          );
        }
      }
      break;

    default:
      logger.warn({ type: data.type }, 'Unknown IPC task type');
  }
}
