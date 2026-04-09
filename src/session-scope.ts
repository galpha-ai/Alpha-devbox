export interface SessionScope {
  channelId: string;
  threadId: string | null;
  agentName: string;
}

export function normalizeThreadId(threadId: string | null | undefined): string {
  return threadId || '';
}

export function makeSessionScopeKey(
  channelId: string,
  threadId: string | null,
  agentName: string,
): string {
  return `${channelId}::${normalizeThreadId(threadId)}::${agentName}`;
}

export function parseSessionScopeKey(scopeKey: string): SessionScope | null {
  const parts = scopeKey.split('::');
  if (parts.length !== 3) return null;
  return {
    channelId: parts[0],
    threadId: parts[1] || null,
    agentName: parts[2],
  };
}
