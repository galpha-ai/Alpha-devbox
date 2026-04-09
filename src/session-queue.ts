import fs from 'fs';
import path from 'path';

import { resolveSessionIpcPath } from './agent-folder.js';
import { MAX_CONCURRENT_CONTAINERS } from './config.js';
import { logger } from './logger.js';
import { touchSessionHeartbeat } from './session-gc.js';

interface QueuedTask {
  id: string;
  sessionKey: string;
  fn: () => Promise<void>;
}

const MAX_RETRIES = 5;
const BASE_RETRY_MS = 5000;

interface SessionState {
  active: boolean;
  idleWaiting: boolean;
  isTaskContainer: boolean;
  pendingMessages: boolean;
  pendingTasks: QueuedTask[];
  containerName: string | null;
  agentName: string | null;
  retryCount: number;
  cancelRequested: boolean;
}

export class SessionQueue {
  private sessions = new Map<string, SessionState>();
  private activeCount = 0;
  private waitingSessions: string[] = [];
  private processMessagesFn: ((sessionKey: string) => Promise<boolean>) | null =
    null;
  private shuttingDown = false;

  private getSessionState(sessionKey: string): SessionState {
    let state = this.sessions.get(sessionKey);
    if (state?.cancelRequested && !state.active) {
      this.sessions.delete(sessionKey);
      state = undefined;
    }
    if (!state) {
      state = {
        active: false,
        idleWaiting: false,
        isTaskContainer: false,
        pendingMessages: false,
        pendingTasks: [],
        containerName: null,
        agentName: null,
        retryCount: 0,
        cancelRequested: false,
      };
      this.sessions.set(sessionKey, state);
    }
    return state;
  }

  setProcessMessagesFn(fn: (sessionKey: string) => Promise<boolean>): void {
    this.processMessagesFn = fn;
  }

  enqueueMessageCheck(sessionKey: string): void {
    if (this.shuttingDown) {
      logger.info(
        { sessionKey },
        'enqueueMessageCheck: shutting down, ignoring',
      );
      return;
    }

    const state = this.getSessionState(sessionKey);
    logger.info(
      {
        sessionKey,
        active: state.active,
        activeCount: this.activeCount,
        maxConcurrent: MAX_CONCURRENT_CONTAINERS,
      },
      'enqueueMessageCheck called',
    );

    if (state.active) {
      state.pendingMessages = true;
      logger.info(
        { sessionKey },
        'enqueueMessageCheck: container active, message queued',
      );
      return;
    }

    if (this.activeCount >= MAX_CONCURRENT_CONTAINERS) {
      state.pendingMessages = true;
      if (!this.waitingSessions.includes(sessionKey)) {
        this.waitingSessions.push(sessionKey);
      }
      logger.info(
        { sessionKey, activeCount: this.activeCount },
        'enqueueMessageCheck: at concurrency limit, message queued',
      );
      return;
    }

    logger.info({ sessionKey }, 'enqueueMessageCheck: starting runForSession');
    this.runForSession(sessionKey, 'messages').catch((err) =>
      logger.error({ sessionKey, err }, 'Unhandled error in runForSession'),
    );
  }

  enqueueTask(
    sessionKey: string,
    taskId: string,
    fn: () => Promise<void>,
  ): void {
    if (this.shuttingDown) return;

    const state = this.getSessionState(sessionKey);

    // Prevent double-queuing of the same task
    if (state.pendingTasks.some((t) => t.id === taskId)) {
      logger.debug({ sessionKey, taskId }, 'Task already queued, skipping');
      return;
    }

    if (state.active) {
      state.pendingTasks.push({ id: taskId, sessionKey, fn });
      if (state.idleWaiting) {
        this.closeStdin(sessionKey);
      }
      logger.debug({ sessionKey, taskId }, 'Container active, task queued');
      return;
    }

    if (this.activeCount >= MAX_CONCURRENT_CONTAINERS) {
      state.pendingTasks.push({ id: taskId, sessionKey, fn });
      if (!this.waitingSessions.includes(sessionKey)) {
        this.waitingSessions.push(sessionKey);
      }
      logger.debug(
        { sessionKey, taskId, activeCount: this.activeCount },
        'At concurrency limit, task queued',
      );
      return;
    }

    // Run immediately
    this.runTask(sessionKey, { id: taskId, sessionKey, fn }).catch((err) =>
      logger.error({ sessionKey, taskId, err }, 'Unhandled error in runTask'),
    );
  }

  registerProcess(
    sessionKey: string,
    containerName: string,
    agentName?: string,
  ): void {
    const state = this.getSessionState(sessionKey);
    state.containerName = containerName;
    if (agentName) state.agentName = agentName;
  }

  /**
   * Mark the container as idle-waiting (finished work, waiting for IPC input).
   * If tasks are pending, preempt the idle container immediately.
   */
  notifyIdle(sessionKey: string): void {
    const state = this.getSessionState(sessionKey);
    if (state.cancelRequested) return;
    state.idleWaiting = true;
    if (state.pendingTasks.length > 0) {
      this.closeStdin(sessionKey);
    }
  }

  /**
   * Send a follow-up message to the active container via IPC file.
   * Returns true if the message was written, false if no active container.
   */
  sendMessage(sessionKey: string, text: string): boolean {
    const state = this.getSessionState(sessionKey);
    if (!state.active || !state.agentName || state.isTaskContainer)
      return false;
    if (state.cancelRequested) return false;
    state.idleWaiting = false; // Agent is about to receive work, no longer idle

    const inputDir = path.join(
      resolveSessionIpcPath(state.agentName, sessionKey),
      'input',
    );
    try {
      fs.mkdirSync(inputDir, { recursive: true });
      const filename = `${Date.now()}-${Math.random().toString(36).slice(2, 6)}.json`;
      const filepath = path.join(inputDir, filename);
      const tempPath = `${filepath}.tmp`;
      fs.writeFileSync(tempPath, JSON.stringify({ type: 'message', text }));
      fs.renameSync(tempPath, filepath);
      touchSessionHeartbeat(state.agentName, sessionKey);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Signal the active container to wind down by writing a close sentinel.
   */
  closeStdin(sessionKey: string): void {
    const state = this.getSessionState(sessionKey);
    if (!state.active || !state.agentName) return;

    const inputDir = path.join(
      resolveSessionIpcPath(state.agentName, sessionKey),
      'input',
    );
    try {
      fs.mkdirSync(inputDir, { recursive: true });
      fs.writeFileSync(path.join(inputDir, '_close'), '');
    } catch {
      // ignore
    }
  }

  inspectSession(sessionKey: string): {
    active: boolean;
    containerName: string | null;
    agentName: string | null;
    pendingMessages: boolean;
    pendingTaskCount: number;
  } | null {
    const state = this.sessions.get(sessionKey);
    if (!state) return null;
    return {
      active: state.active,
      containerName: state.containerName,
      agentName: state.agentName,
      pendingMessages: state.pendingMessages,
      pendingTaskCount: state.pendingTasks.length,
    };
  }

  cancelSession(sessionKey: string): void {
    this.waitingSessions = this.waitingSessions.filter(
      (key) => key !== sessionKey,
    );

    const state = this.sessions.get(sessionKey);
    if (!state) return;

    state.pendingMessages = false;
    state.pendingTasks = [];
    state.idleWaiting = false;
    state.retryCount = 0;
    state.cancelRequested = true;

    if (!state.active) {
      this.sessions.delete(sessionKey);
    }
  }

  private async runForSession(
    sessionKey: string,
    reason: 'messages' | 'drain',
  ): Promise<void> {
    const rfsStart = Date.now();
    const rfsElapsed = () => `${Date.now() - rfsStart}ms`;
    const state = this.getSessionState(sessionKey);
    state.active = true;
    state.idleWaiting = false;
    state.isTaskContainer = false;
    state.pendingMessages = false;
    this.activeCount++;

    logger.info(
      { sessionKey, reason, activeCount: this.activeCount },
      `[${rfsElapsed()}] runForSession: starting`,
    );

    try {
      if (this.processMessagesFn) {
        logger.info(
          { sessionKey },
          `[${rfsElapsed()}] runForSession: calling processMessagesFn`,
        );
        const success = await this.processMessagesFn(sessionKey);
        logger.info(
          { sessionKey, success },
          `[${rfsElapsed()}] runForSession: processMessagesFn returned`,
        );
        if (success) {
          state.retryCount = 0;
        } else if (!state.cancelRequested) {
          this.scheduleRetry(sessionKey, state);
        }
      } else {
        logger.warn(
          { sessionKey },
          `[${rfsElapsed()}] runForSession: no processMessagesFn set!`,
        );
      }
    } catch (err) {
      logger.error(
        { sessionKey, err },
        `[${rfsElapsed()}] runForSession: error processing messages`,
      );
      if (!state.cancelRequested) {
        this.scheduleRetry(sessionKey, state);
      }
    } finally {
      state.active = false;
      state.containerName = null;
      state.agentName = null;
      this.activeCount--;
      if (state.cancelRequested) {
        this.sessions.delete(sessionKey);
        this.drainWaiting();
        return;
      }
      logger.info(
        { sessionKey, activeCount: this.activeCount },
        `[${rfsElapsed()}] runForSession: finished, draining`,
      );
      this.drainSession(sessionKey);
    }
  }

  private async runTask(sessionKey: string, task: QueuedTask): Promise<void> {
    const state = this.getSessionState(sessionKey);
    state.active = true;
    state.idleWaiting = false;
    state.isTaskContainer = true;
    this.activeCount++;

    logger.debug(
      { sessionKey, taskId: task.id, activeCount: this.activeCount },
      'Running queued task',
    );

    try {
      await task.fn();
    } catch (err) {
      logger.error({ sessionKey, taskId: task.id, err }, 'Error running task');
    } finally {
      state.active = false;
      state.isTaskContainer = false;
      state.containerName = null;
      state.agentName = null;
      this.activeCount--;
      if (state.cancelRequested) {
        this.sessions.delete(sessionKey);
        this.drainWaiting();
        return;
      }
      this.drainSession(sessionKey);
    }
  }

  private scheduleRetry(sessionKey: string, state: SessionState): void {
    state.retryCount++;
    if (state.retryCount > MAX_RETRIES) {
      logger.error(
        { sessionKey, retryCount: state.retryCount },
        'Max retries exceeded, dropping messages (will retry on next incoming message)',
      );
      state.retryCount = 0;
      return;
    }

    const delayMs = BASE_RETRY_MS * Math.pow(2, state.retryCount - 1);
    logger.info(
      { sessionKey, retryCount: state.retryCount, delayMs },
      'Scheduling retry with backoff',
    );
    setTimeout(() => {
      if (!this.shuttingDown) {
        this.enqueueMessageCheck(sessionKey);
      }
    }, delayMs);
  }

  private drainSession(sessionKey: string): void {
    if (this.shuttingDown) return;

    const state = this.getSessionState(sessionKey);

    // Tasks first (they won't be re-discovered from SQLite like messages)
    if (state.pendingTasks.length > 0) {
      const task = state.pendingTasks.shift()!;
      this.runTask(sessionKey, task).catch((err) =>
        logger.error(
          { sessionKey, taskId: task.id, err },
          'Unhandled error in runTask (drain)',
        ),
      );
      return;
    }

    // Then pending messages
    if (state.pendingMessages) {
      this.runForSession(sessionKey, 'drain').catch((err) =>
        logger.error(
          { sessionKey, err },
          'Unhandled error in runForSession (drain)',
        ),
      );
      return;
    }

    // Nothing pending for this session; check if other sessions are waiting.
    this.drainWaiting();
  }

  private drainWaiting(): void {
    while (
      this.waitingSessions.length > 0 &&
      this.activeCount < MAX_CONCURRENT_CONTAINERS
    ) {
      const nextSessionKey = this.waitingSessions.shift()!;
      const state = this.getSessionState(nextSessionKey);

      // Prioritize tasks over messages
      if (state.pendingTasks.length > 0) {
        const task = state.pendingTasks.shift()!;
        this.runTask(nextSessionKey, task).catch((err) =>
          logger.error(
            { sessionKey: nextSessionKey, taskId: task.id, err },
            'Unhandled error in runTask (waiting)',
          ),
        );
      } else if (state.pendingMessages) {
        this.runForSession(nextSessionKey, 'drain').catch((err) =>
          logger.error(
            { sessionKey: nextSessionKey, err },
            'Unhandled error in runForSession (waiting)',
          ),
        );
      }
      // If neither pending, skip this session.
    }
  }

  /**
   * Check if a session currently has an active container running.
   */
  isSessionActive(sessionKey: string): boolean {
    const state = this.sessions.get(sessionKey);
    return state?.active === true;
  }

  getActiveCount(): number {
    return this.activeCount;
  }

  getWaitingCount(): number {
    return this.waitingSessions.length;
  }

  async shutdown(_gracePeriodMs: number): Promise<void> {
    this.shuttingDown = true;

    // Count active containers but don't kill them — they'll finish on their own
    // via idle timeout or container timeout. The --rm flag cleans them up on exit.
    // This prevents WhatsApp reconnection restarts from killing working agents.
    const activeContainers: string[] = [];
    for (const [_sessionKey, state] of this.sessions) {
      if (state.active && state.containerName) {
        activeContainers.push(state.containerName);
      }
    }

    logger.info(
      { activeCount: this.activeCount, detachedContainers: activeContainers },
      'SessionQueue shutting down (containers detached, not killed)',
    );
  }
}
