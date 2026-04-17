import { describe, expect, it } from 'vitest';

import {
  buildAssistantUiMessageProjection,
  buildCanonicalChatMessage,
  stringifyUiMessageProjection,
} from './ui-message.js';

describe('ui-message canonical projection', () => {
  it('stores assistant structured output as a single text part', () => {
    const message = buildAssistantUiMessageProjection({
      id: 'bot-1',
      content:
        'Visible answer\n<<<CHART_V1>>>{\"series\":[]}\n<<<END_CHART_V1>>>',
      timestamp: '2026-04-17T00:00:00.000Z',
      sender: 'Devbox',
      senderName: 'Devbox',
    });

    expect(message.parts).toEqual([
      {
        type: 'text',
        text: 'Visible answer\n<<<CHART_V1>>>{\"series\":[]}\n<<<END_CHART_V1>>>',
        state: 'done',
      },
    ]);
  });

  it('prefers stored ui_message_json when available', () => {
    const storedProjection = stringifyUiMessageProjection({
      id: 'bot-1',
      role: 'assistant',
      parts: [{ type: 'text', text: 'projected', state: 'done' }],
      metadata: {
        timestamp: '2026-04-17T00:00:00.000Z',
        sender: 'Devbox',
        senderName: 'Devbox',
      },
    });

    const message = buildCanonicalChatMessage({
      id: 'bot-1',
      sender: 'Devbox',
      sender_name: 'Devbox',
      content: 'raw fallback',
      timestamp: '2026-04-17T00:00:00.000Z',
      is_bot_message: true,
      ui_message_json: storedProjection,
    });

    expect(message.parts[0]).toEqual({
      type: 'text',
      text: 'projected',
      state: 'done',
    });
  });

  it('normalizes legacy structured parts into a single text part', () => {
    const storedProjection = JSON.stringify({
      id: 'bot-1',
      role: 'assistant',
      parts: [
        {
          type: 'data-artifact',
          data: {
            kind: 'chart',
            version: 1,
            payload: { series: [] },
          },
        },
      ],
      metadata: {
        timestamp: '2026-04-17T00:00:00.000Z',
        sender: 'Devbox',
        senderName: 'Devbox',
      },
    });

    const message = buildCanonicalChatMessage({
      id: 'bot-1',
      sender: 'Devbox',
      sender_name: 'Devbox',
      content: 'raw fallback',
      timestamp: '2026-04-17T00:00:00.000Z',
      is_bot_message: true,
      ui_message_json: storedProjection,
    });

    expect(message.parts).toEqual([
      {
        type: 'text',
        text: '<<<CHART_V1>>>\n{\"series\":[]}\n<<<END_CHART_V1>>>',
        state: 'done',
      },
    ]);
  });
});
