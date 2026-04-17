const DEFAULT_FRONTEND_URL = 'http://127.0.0.1:5175/';
export const REPLAY_SUGGESTION_COOLDOWN_MS = 15 * 60 * 1000;

export function getReplayBaseUrl(): string {
  return (
    process.env.DEVBOX_PUBLIC_WEB_BASE_URL ||
    process.env.DEVBOX_FRONTEND_URL ||
    DEFAULT_FRONTEND_URL
  );
}

export function buildReplayUrl(
  replayId: string,
  replyId?: string,
  baseUrl = getReplayBaseUrl(),
): string {
  const url = new URL(`/replay/${encodeURIComponent(replayId)}`, baseUrl);
  if (replyId) {
    url.searchParams.set('reply', replyId);
  }
  return url.toString();
}

export function shouldAttachReplayUrl(chatJid: string): boolean {
  return chatJid.startsWith('slack:') || chatJid.startsWith('tg:');
}

export function appendReplayUrl(text: string, replayUrl: string): string {
  return `${text}\n\nWeb 优化显示：${replayUrl}`.trim();
}

export function shouldSuggestReplayLink({
  chatJid,
  text,
  lastSuggestedAt,
  now = Date.now(),
  cooldownMs = REPLAY_SUGGESTION_COOLDOWN_MS,
}: {
  chatJid: string;
  text: string;
  lastSuggestedAt?: number;
  now?: number;
  cooldownMs?: number;
}): boolean {
  if (!shouldAttachReplayUrl(chatJid)) {
    return false;
  }

  if (!isReplayWorthyContent(text)) {
    return false;
  }

  if (
    typeof lastSuggestedAt === 'number' &&
    now - lastSuggestedAt < cooldownMs
  ) {
    return false;
  }

  return true;
}

export function isReplayWorthyContent(text: string): boolean {
  const trimmed = text.trim();
  if (!trimmed) return false;

  if (trimmed.length >= 280) return true;
  if (/```[\s\S]*?```/m.test(trimmed)) return true;
  if (/```mermaid/i.test(trimmed)) return true;
  if (/<<<CHART_V1>>>[\s\S]*?<<<END_CHART_V1>>>/m.test(trimmed)) return true;
  if (/<<<THESIS_REPORT_V1>>>[\s\S]*?<<<END_THESIS_REPORT_V1>>>/m.test(trimmed))
    return true;
  if (/^\s{0,3}#{1,6}\s/m.test(trimmed)) return true;
  if (
    /\|[^\n]+\|\n\|(?:\s*:?-+:?\s*\|){2,}/m.test(trimmed) ||
    /\|[^\n]+\|\n\|(?:\s*:?-+:?\s*\|)+/m.test(trimmed)
  ) {
    return true;
  }
  if (/(^|\n)([-*]|\d+\.)\s.+(\n(?:[-*]|\d+\.)\s.+){2,}/m.test(trimmed)) {
    return true;
  }
  if (/^>\s*\[!(NOTE|TIP|WARNING|IMPORTANT|CAUTION)\]/im.test(trimmed)) {
    return true;
  }

  return false;
}
