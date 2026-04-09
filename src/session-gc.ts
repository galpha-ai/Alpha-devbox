import fs from 'fs';
import path from 'path';

import {
  decodeSessionScopeKey,
  isValidAgentName,
  resolveSessionPath,
} from './agent-folder.js';
import { DATA_DIR } from './config.js';
import { deleteSession, parseSessionScopeKey } from './db.js';
import { logger } from './logger.js';
import { SessionQueue } from './session-queue.js';

const HEARTBEAT_FILE = '_last_activity';

/**
 * Touch the heartbeat file in a session's root directory.
 * Called on container start and when piping follow-up messages.
 */
export function touchSessionHeartbeat(
  agentName: string,
  sessionKey: string,
): void {
  try {
    const sessionDir = resolveSessionPath(agentName, sessionKey);
    const heartbeatPath = path.join(sessionDir, HEARTBEAT_FILE);
    const now = new Date();
    fs.utimesSync(heartbeatPath, now, now);
  } catch (err) {
    if ((err as NodeJS.ErrnoException).code === 'ENOENT') {
      try {
        const sessionDir = resolveSessionPath(agentName, sessionKey);
        const heartbeatPath = path.join(sessionDir, HEARTBEAT_FILE);
        fs.writeFileSync(heartbeatPath, '');
      } catch {
        // best-effort
      }
    }
  }
}

export interface SessionGcDeps {
  queue: SessionQueue;
  getSessions: () => Record<string, string>;
  getLastAgentTimestamp: () => Record<string, string>;
  saveState: () => void;
  deleteSession?: typeof deleteSession;
  interval: number;
  maxAge: number;
}

/**
 * Start a periodic GC sweep that removes stale thread-scoped session directories.
 * Channel-scoped sessions (threadId === null) are never collected.
 */
export function startSessionGc(deps: SessionGcDeps): void {
  const sweep = () => {
    try {
      runGcSweep(deps);
    } catch (err) {
      logger.error({ err }, 'Session GC sweep failed');
    }
    setTimeout(sweep, deps.interval);
  };

  setTimeout(sweep, deps.interval);
  logger.info(
    { intervalMs: deps.interval, maxAgeMs: deps.maxAge },
    'Session GC started',
  );
}

function getSessionDirectories(): Array<{
  agentName: string;
  encodedSessionKey: string;
  sessionDir: string;
}> {
  const sessionsBaseDir = path.join(DATA_DIR, 'sessions');
  if (!fs.existsSync(sessionsBaseDir)) return [];

  const results: Array<{
    agentName: string;
    encodedSessionKey: string;
    sessionDir: string;
  }> = [];

  for (const agentName of fs.readdirSync(sessionsBaseDir)) {
    if (!isValidAgentName(agentName)) continue;
    const agentDir = path.join(sessionsBaseDir, agentName);
    if (!fs.statSync(agentDir).isDirectory()) continue;

    for (const encodedSessionKey of fs.readdirSync(agentDir)) {
      const sessionDir = path.join(agentDir, encodedSessionKey);
      if (!fs.statSync(sessionDir).isDirectory()) continue;
      results.push({ agentName, encodedSessionKey, sessionDir });
    }
  }

  return results;
}

function getSessionMtime(sessionDir: string): number {
  const heartbeatPath = path.join(sessionDir, HEARTBEAT_FILE);
  try {
    return fs.statSync(heartbeatPath).mtimeMs;
  } catch {
    // Fall back to directory mtime if heartbeat file doesn't exist
    try {
      return fs.statSync(sessionDir).mtimeMs;
    } catch {
      return 0;
    }
  }
}

function runGcSweep(deps: SessionGcDeps): void {
  const now = Date.now();
  const directories = getSessionDirectories();
  const deleteSessionFn = deps.deleteSession ?? deleteSession;
  let removedCount = 0;

  for (const { agentName, encodedSessionKey, sessionDir } of directories) {
    let sessionKey: string;
    try {
      sessionKey = decodeSessionScopeKey(encodedSessionKey);
    } catch {
      continue;
    }

    const scope = parseSessionScopeKey(sessionKey);
    if (!scope || scope.agentName !== agentName) continue;

    // Never GC channel-scoped sessions (long-lived)
    if (scope.threadId === null) continue;

    // Never GC active sessions
    if (deps.queue.isSessionActive(sessionKey)) continue;

    const mtime = getSessionMtime(sessionDir);
    if (now - mtime <= deps.maxAge) continue;

    // GC candidate — remove
    try {
      fs.rmSync(sessionDir, { recursive: true, force: true });
    } catch (err) {
      logger.warn(
        { sessionDir, err },
        'Failed to remove stale session directory',
      );
      continue;
    }

    // Clean up DB row
    try {
      deleteSessionFn(scope.channelId, scope.threadId, scope.agentName);
    } catch (err) {
      logger.warn({ sessionKey, err }, 'Failed to delete session from DB');
    }

    // Clean up in-memory state
    const sessions = deps.getSessions();
    const lastAgentTimestamp = deps.getLastAgentTimestamp();
    let stateChanged = false;

    if (sessionKey in sessions) {
      delete sessions[sessionKey];
      stateChanged = true;
    }
    if (sessionKey in lastAgentTimestamp) {
      delete lastAgentTimestamp[sessionKey];
      stateChanged = true;
    }
    if (stateChanged) {
      deps.saveState();
    }

    removedCount++;
    logger.info(
      {
        sessionKey,
        agentName,
        channelId: scope.channelId,
        threadId: scope.threadId,
        ageMins: Math.round((now - mtime) / 60000),
      },
      'GC removed stale thread session',
    );
  }

  if (removedCount > 0) {
    logger.info({ removedCount }, 'Session GC sweep completed');
  }
}
