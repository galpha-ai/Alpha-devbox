import { execFileSync } from 'child_process';
import fs from 'fs';
import path from 'path';

import {
  resolveSessionPath,
  resolveSessionWorkspacePath,
} from './agent-folder.js';
import { ContainerRuntime } from './container-runtime.js';
import { deleteSession } from './db.js';
import { logger } from './logger.js';
import { SessionScope } from './session-scope.js';
import { SessionQueue } from './session-queue.js';

export interface SessionControlCommand {
  name: 'done' | 'reset';
  force: boolean;
}

export type SessionCleanupResult =
  | {
      status: 'warning';
      dirtyRepos: string[];
    }
  | {
      status: 'cleaned';
      dirtyRepos: string[];
      stoppedActiveContainer: boolean;
      removedSessionDir: boolean;
    };

export function parseSessionControlCommand(
  content: string,
): SessionControlCommand | null {
  const trimmed = content.trim();
  if (/^\/reset\s*$/i.test(trimmed)) {
    return {
      name: 'reset',
      force: true,
    };
  }

  const match = trimmed.match(/^\/done(?:\s+(--force|-f))?\s*$/i);
  if (!match) return null;
  return {
    name: 'done',
    force: Boolean(match[1]),
  };
}

export function applyCleanedSessionControlState(
  sessionKey: string,
  commandTimestamp: string,
  state: {
    sessions: Record<string, string>;
    lastAgentTimestamps: Record<string, string>;
  },
  latestHandledTimestamp = commandTimestamp,
): void {
  delete state.sessions[sessionKey];
  state.lastAgentTimestamps[sessionKey] = latestHandledTimestamp;
}

export function findDirtyWorkspaceRepos(workspaceDir: string): string[] {
  if (!fs.existsSync(workspaceDir)) return [];

  const dirtyRepos: string[] = [];
  for (const entry of fs.readdirSync(workspaceDir, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;

    const repoDir = path.join(workspaceDir, entry.name);
    try {
      execFileSync(
        'git',
        ['-C', repoDir, 'rev-parse', '--is-inside-work-tree'],
        { stdio: 'ignore' },
      );
    } catch {
      continue;
    }

    try {
      const output = execFileSync(
        'git',
        ['-C', repoDir, 'status', '--porcelain'],
        { encoding: 'utf-8' },
      ).trim();
      if (output) dirtyRepos.push(entry.name);
    } catch (err) {
      logger.warn(
        { err, repoDir },
        'Failed to inspect workspace repo status before session cleanup',
      );
    }
  }

  return dirtyRepos.sort();
}

export async function cleanupSessionScope(
  sessionKey: string,
  scope: SessionScope,
  options: {
    force: boolean;
    runtime: Pick<ContainerRuntime, 'stopContainer'>;
    queue: Pick<SessionQueue, 'inspectSession' | 'cancelSession'>;
    deleteSessionFn?: typeof deleteSession;
    findDirtyReposFn?: (workspaceDir: string) => string[];
    removeDirFn?: (target: string) => void;
  },
): Promise<SessionCleanupResult> {
  const sessionDir = resolveSessionPath(scope.agentName, sessionKey);
  const workspaceDir = resolveSessionWorkspacePath(scope.agentName, sessionKey);
  const dirtyRepos = (options.findDirtyReposFn ?? findDirtyWorkspaceRepos)(
    workspaceDir,
  );
  if (dirtyRepos.length > 0 && !options.force) {
    return {
      status: 'warning',
      dirtyRepos,
    };
  }

  const sessionState = options.queue.inspectSession(sessionKey);
  if (sessionState?.active && sessionState.containerName) {
    await options.runtime.stopContainer(sessionState.containerName);
  }
  options.queue.cancelSession(sessionKey);

  (options.deleteSessionFn ?? deleteSession)(
    scope.channelId,
    scope.threadId,
    scope.agentName,
  );

  let removedSessionDir = false;
  try {
    (
      options.removeDirFn ??
      ((target) => fs.rmSync(target, { recursive: true, force: true }))
    )(sessionDir);
    removedSessionDir = fs.existsSync(sessionDir) ? false : true;
  } catch (err) {
    logger.warn({ err, sessionDir }, 'Failed to remove session directory');
  }

  return {
    status: 'cleaned',
    dirtyRepos,
    stoppedActiveContainer: Boolean(
      sessionState?.active && sessionState.containerName,
    ),
    removedSessionDir,
  };
}
