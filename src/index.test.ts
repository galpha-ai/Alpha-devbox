import { describe, expect, it } from 'vitest';

import {
  planStaleResumeRecovery,
  shouldRecoverPendingMessages,
  shouldReplyThreadReclaimed,
  summarizePendingRecoveryMessages,
} from './index.js';
import { SessionScope } from './session-scope.js';
import type { NewMessage } from './types.js';

describe('shouldReplyThreadReclaimed', () => {
  const threadScope: SessionScope = {
    channelId: 'slack:C123',
    threadId: '1700000000.000100',
    agentName: 'main',
  };

  it('does not treat a brand-new thread as reclaimed', () => {
    expect(
      shouldReplyThreadReclaimed(
        threadScope,
        'slack:C123::1700000000.000100::main',
        false,
        {},
        {},
      ),
    ).toBe(false);
  });

  it('treats a missing thread directory with a persisted session as reclaimed', () => {
    expect(
      shouldReplyThreadReclaimed(
        threadScope,
        'slack:C123::1700000000.000100::main',
        false,
        { 'slack:C123::1700000000.000100::main': 'session-1' },
        {},
      ),
    ).toBe(true);
  });

  it('treats a missing thread directory with a persisted cursor as reclaimed', () => {
    expect(
      shouldReplyThreadReclaimed(
        threadScope,
        'slack:C123::1700000000.000100::main',
        false,
        {},
        { 'slack:C123::1700000000.000100::main': '2026-03-06T22:49:37.419Z' },
      ),
    ).toBe(true);
  });

  it('never treats an existing thread directory as reclaimed', () => {
    expect(
      shouldReplyThreadReclaimed(
        threadScope,
        'slack:C123::1700000000.000100::main',
        true,
        { 'slack:C123::1700000000.000100::main': 'session-1' },
        { 'slack:C123::1700000000.000100::main': '2026-03-06T22:49:37.419Z' },
      ),
    ).toBe(false);
  });

  it('never treats channel-scoped sessions as reclaimed', () => {
    expect(
      shouldReplyThreadReclaimed(
        { channelId: 'slack:C123', threadId: null, agentName: 'main' },
        'slack:C123::::main',
        false,
        { 'slack:C123::::main': 'session-1' },
        { 'slack:C123::::main': '2026-03-06T22:49:37.419Z' },
      ),
    ).toBe(false);
  });
});

describe('shouldRecoverPendingMessages', () => {
  it('does not recover when there are no pending user messages', () => {
    expect(shouldRecoverPendingMessages([], Date.UTC(2026, 2, 9, 18))).toBe(
      false,
    );
  });

  it('recovers recent pending user messages', () => {
    expect(
      shouldRecoverPendingMessages(
        [{ timestamp: '2026-03-09T17:45:00.000Z' }],
        Date.UTC(2026, 2, 9, 18),
      ),
    ).toBe(true);
  });

  it('skips stale pending user messages', () => {
    expect(
      shouldRecoverPendingMessages(
        [{ timestamp: '2026-03-09T11:00:00.000Z' }],
        Date.UTC(2026, 2, 9, 18),
      ),
    ).toBe(false);
  });
});

describe('planStaleResumeRecovery', () => {
  it('replays the full pending thread delta after clearing a stale thread session', () => {
    const plan = planStaleResumeRecovery(
      {
        channelId: 'slack:C123',
        threadId: '1700000000.000100',
        agentName: 'main',
      },
      [
        {
          id: 'msg-1',
          chat_jid: 'slack:C123',
          thread_id: '1700000000.000100',
          sender: 'U123',
          sender_name: 'Alice',
          content: 'Continue the work',
          timestamp: '2026-03-09T17:45:00.000Z',
        },
      ],
      '2026-03-09T17:40:00.000Z',
    );

    expect(plan).toEqual({
      cursor: '2026-03-09T17:40:00.000Z',
      replayCount: 1,
      droppedCount: 0,
    });
  });

  it('drops older channel backlog and replays from the latest trigger window', () => {
    const plan = planStaleResumeRecovery(
      {
        channelId: 'slack:C123',
        threadId: null,
        agentName: 'main',
      },
      [
        {
          id: 'msg-1',
          chat_jid: 'slack:C123',
          sender: 'U123',
          sender_name: 'Alice',
          content: 'older context',
          timestamp: '2026-03-09T17:41:00.000Z',
        },
        {
          id: 'msg-2',
          chat_jid: 'slack:C123',
          sender: 'U123',
          sender_name: 'Alice',
          content: '@Devbox first try',
          timestamp: '2026-03-09T17:42:00.000Z',
        },
        {
          id: 'msg-3',
          chat_jid: 'slack:C123',
          sender: 'U123',
          sender_name: 'Alice',
          content: 'more context',
          timestamp: '2026-03-09T17:43:00.000Z',
        },
        {
          id: 'msg-4',
          chat_jid: 'slack:C123',
          sender: 'U123',
          sender_name: 'Alice',
          content: 'another note',
          timestamp: '2026-03-09T17:44:00.000Z',
        },
        {
          id: 'msg-5',
          chat_jid: 'slack:C123',
          sender: 'U123',
          sender_name: 'Alice',
          content: '@Devbox latest try',
          timestamp: '2026-03-09T17:45:00.000Z',
        },
        {
          id: 'msg-6',
          chat_jid: 'slack:C123',
          sender: 'U123',
          sender_name: 'Alice',
          content: 'latest follow-up',
          timestamp: '2026-03-09T17:46:00.000Z',
        },
      ],
      '2026-03-09T17:40:00.000Z',
    );

    expect(plan).toEqual({
      cursor: '2026-03-09T17:42:00.000Z',
      replayCount: 4,
      droppedCount: 2,
      anchorMessageId: 'msg-5',
    });
  });
});

describe('summarizePendingRecoveryMessages', () => {
  it('includes ids, sender info, timestamps, and content previews', () => {
    const pending: NewMessage[] = [
      {
        id: 'msg-1',
        chat_jid: 'slack:C123',
        sender: 'U123',
        sender_name: 'Alice',
        content: 'Ship the fix',
        timestamp: '2026-03-09T17:45:00.000Z',
      },
    ];

    expect(summarizePendingRecoveryMessages(pending, null)).toEqual([
      {
        id: 'msg-1',
        sender: 'Alice',
        senderId: 'U123',
        timestamp: '2026-03-09T17:45:00.000Z',
        contentPreview: 'Ship the fix',
      },
    ]);
  });

  it('marks thread parent bootstrap messages and normalizes whitespace', () => {
    const pending: NewMessage[] = [
      {
        id: '1700000000.000100',
        chat_jid: 'slack:C123',
        sender: 'U123',
        sender_name: 'Alice',
        content: 'Parent subject\nwith extra spacing',
        timestamp: '2026-03-09T17:45:00.000Z',
      },
      {
        id: '1700000001.000200',
        chat_jid: 'slack:C123',
        thread_id: '1700000000.000100',
        sender: 'U123',
        sender_name: 'Alice',
        content: 'Follow-up',
        timestamp: '2026-03-09T17:46:00.000Z',
      },
    ];

    expect(
      summarizePendingRecoveryMessages(pending, '1700000000.000100'),
    ).toEqual([
      {
        id: '1700000000.000100',
        sender: 'Alice',
        senderId: 'U123',
        timestamp: '2026-03-09T17:45:00.000Z',
        contentPreview: 'Parent subject with extra spacing',
        role: 'thread_parent',
      },
      {
        id: '1700000001.000200',
        sender: 'Alice',
        senderId: 'U123',
        timestamp: '2026-03-09T17:46:00.000Z',
        contentPreview: 'Follow-up',
      },
    ]);
  });

  it('truncates long content previews', () => {
    const pending: NewMessage[] = [
      {
        id: 'msg-1',
        chat_jid: 'slack:C123',
        sender: 'U123',
        sender_name: 'Alice',
        content: 'abcdefghijklmnopqrstuvwxyz',
        timestamp: '2026-03-09T17:45:00.000Z',
      },
    ];

    expect(summarizePendingRecoveryMessages(pending, null, 10)).toEqual([
      {
        id: 'msg-1',
        sender: 'Alice',
        senderId: 'U123',
        timestamp: '2026-03-09T17:45:00.000Z',
        contentPreview: 'abcdefg...',
      },
    ]);
  });
});
