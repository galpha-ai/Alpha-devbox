import path from 'path';

import { AGENTS_DIR, DATA_DIR } from './config.js';

const AGENT_NAME_PATTERN = /^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/;
const RESERVED_AGENT_NAMES = new Set(['global']);

export function isValidAgentName(agentName: string): boolean {
  if (!agentName) return false;
  if (agentName !== agentName.trim()) return false;
  if (!AGENT_NAME_PATTERN.test(agentName)) return false;
  if (agentName.includes('/') || agentName.includes('\\')) return false;
  if (agentName.includes('..')) return false;
  if (RESERVED_AGENT_NAMES.has(agentName.toLowerCase())) return false;
  return true;
}

export function assertValidAgentName(agentName: string): void {
  if (!isValidAgentName(agentName)) {
    throw new Error(`Invalid agent name "${agentName}"`);
  }
}

function ensureWithinBase(baseDir: string, resolvedPath: string): void {
  const rel = path.relative(baseDir, resolvedPath);
  if (rel.startsWith('..') || path.isAbsolute(rel)) {
    throw new Error(`Path escapes base directory: ${resolvedPath}`);
  }
}

export function resolveAgentPath(agentName: string): string {
  assertValidAgentName(agentName);
  const agentPath = path.resolve(AGENTS_DIR, agentName);
  ensureWithinBase(AGENTS_DIR, agentPath);
  return agentPath;
}

function encodeSessionScopeKey(sessionKey: string): string {
  if (!sessionKey || sessionKey !== sessionKey.trim()) {
    throw new Error(`Invalid session key "${sessionKey}"`);
  }
  return Buffer.from(sessionKey, 'utf-8').toString('base64url');
}

export function decodeSessionScopeKey(encodedSessionKey: string): string {
  if (!encodedSessionKey || encodedSessionKey !== encodedSessionKey.trim()) {
    throw new Error(`Invalid encoded session key "${encodedSessionKey}"`);
  }
  return Buffer.from(encodedSessionKey, 'base64url').toString('utf-8');
}

export function resolveSessionPath(
  agentName: string,
  sessionKey: string,
): string {
  assertValidAgentName(agentName);
  const sessionsBaseDir = path.resolve(DATA_DIR, 'sessions');
  const sessionPath = path.resolve(
    sessionsBaseDir,
    agentName,
    encodeSessionScopeKey(sessionKey),
  );
  ensureWithinBase(sessionsBaseDir, sessionPath);
  return sessionPath;
}

export function resolveSessionWorkspacePath(
  agentName: string,
  sessionKey: string,
): string {
  return path.join(resolveSessionPath(agentName, sessionKey), 'workspace');
}

export function resolveSessionClaudePath(
  agentName: string,
  sessionKey: string,
): string {
  return path.join(resolveSessionPath(agentName, sessionKey), '.claude');
}

export function resolveSessionIpcPath(
  agentName: string,
  sessionKey: string,
): string {
  return path.join(resolveSessionPath(agentName, sessionKey), 'ipc');
}

export function resolveSessionRunnerSourcePath(
  agentName: string,
  sessionKey: string,
): string {
  return path.join(
    resolveSessionPath(agentName, sessionKey),
    'agent-runner-src',
  );
}

// Backward-compatible aliases during migration.
export const isValidGroupFolder = isValidAgentName;
export const assertValidGroupFolder = assertValidAgentName;
export const resolveGroupFolderPath = resolveAgentPath;
export const resolveGroupIpcPath = resolveSessionIpcPath;
