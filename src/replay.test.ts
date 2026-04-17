import { describe, expect, it } from 'vitest';

import {
  appendReplayUrl,
  buildReplayUrl,
  getReplayBaseUrl,
  isReplayWorthyContent,
  REPLAY_SUGGESTION_COOLDOWN_MS,
  shouldAttachReplayUrl,
  shouldSuggestReplayLink,
} from './replay.js';

describe('replay helpers', () => {
  it('prefers public replay base url over frontend base url', () => {
    const originalPublic = process.env.DEVBOX_PUBLIC_WEB_BASE_URL;
    const originalFrontend = process.env.DEVBOX_FRONTEND_URL;
    process.env.DEVBOX_PUBLIC_WEB_BASE_URL = 'https://public.example.com/';
    process.env.DEVBOX_FRONTEND_URL = 'https://frontend.example.com/';

    expect(getReplayBaseUrl()).toBe('https://public.example.com/');

    process.env.DEVBOX_PUBLIC_WEB_BASE_URL = originalPublic;
    process.env.DEVBOX_FRONTEND_URL = originalFrontend;
  });

  it('builds replay URLs with optional reply ids', () => {
    expect(
      buildReplayUrl('rpl_123', undefined, 'https://example.com/app/'),
    ).toBe('https://example.com/replay/rpl_123');
    expect(buildReplayUrl('rpl_123', 'bot-1', 'https://example.com/app/')).toBe(
      'https://example.com/replay/rpl_123?reply=bot-1',
    );
  });

  it('only attaches replay URLs for telegram/slack messages', () => {
    expect(shouldAttachReplayUrl('slack:C123')).toBe(true);
    expect(shouldAttachReplayUrl('tg:user:123')).toBe(true);
    expect(shouldAttachReplayUrl('web:user-1')).toBe(false);
  });

  it('appends replay URLs to outbound text', () => {
    expect(appendReplayUrl('done', 'https://example.com/replay/rpl_123')).toBe(
      'done\n\nWeb 优化显示：https://example.com/replay/rpl_123',
    );
  });

  it('detects replay-worthy rich markdown content', () => {
    expect(
      isReplayWorthyContent(
        '## Revenue trend\n\n| Month | Revenue |\n| --- | ---: |\n| Jan | 120 |',
      ),
    ).toBe(true);
    expect(
      isReplayWorthyContent(
        'Visible answer\n<<<CHART_V1>>>{\"series\":[]}\n<<<END_CHART_V1>>>',
      ),
    ).toBe(true);
    expect(
      isReplayWorthyContent('Short answer without structure or chart hints.'),
    ).toBe(false);
  });

  it('only suggests replay links for rich tg/slack replies outside cooldown', () => {
    const richText =
      '## Bottom line\n\n- one\n- two\n- three\n\n```ts\nconsole.log(1)\n```';
    expect(
      shouldSuggestReplayLink({
        chatJid: 'slack:C123',
        text: richText,
      }),
    ).toBe(true);
    expect(
      shouldSuggestReplayLink({
        chatJid: 'web:user-1',
        text: richText,
      }),
    ).toBe(false);
    expect(
      shouldSuggestReplayLink({
        chatJid: 'tg:user:1',
        text: richText,
        lastSuggestedAt: 1_000,
        now: 1_000 + REPLAY_SUGGESTION_COOLDOWN_MS - 1,
      }),
    ).toBe(false);
  });
});
