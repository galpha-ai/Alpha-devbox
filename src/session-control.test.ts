import { describe, expect, it, vi } from 'vitest';

import {
  applyCleanedSessionControlState,
  cleanupSessionScope,
  parseSessionControlCommand,
} from './session-control.js';

describe('parseSessionControlCommand', () => {
  it('parses /done without force', () => {
    expect(parseSessionControlCommand('/done')).toEqual({
      name: 'done',
      force: false,
    });
  });

  it('rejects /kill', () => {
    expect(parseSessionControlCommand('/kill --force')).toBeNull();
  });

  it('parses /reset as an unconditional hard reset', () => {
    expect(parseSessionControlCommand('/reset')).toEqual({
      name: 'reset',
      force: true,
    });
  });

  it('rejects non-control messages', () => {
    expect(parseSessionControlCommand('/done later')).toBeNull();
  });
});

describe('applyCleanedSessionControlState', () => {
  it('clears the cached session id and records the cleanup cursor', () => {
    const state = {
      sessions: { 'slack:C123::1700000000.000100::main': 'session-1' },
      lastAgentTimestamps: {},
    };

    applyCleanedSessionControlState(
      'slack:C123::1700000000.000100::main',
      '2026-03-06T22:49:37.419Z',
      state,
    );

    expect(state).toEqual({
      sessions: {},
      lastAgentTimestamps: {
        'slack:C123::1700000000.000100::main': '2026-03-06T22:49:37.419Z',
      },
    });
  });

  it('can advance the cleanup cursor past ignored follow-up messages', () => {
    const state = {
      sessions: { 'slack:C123::1700000000.000100::main': 'session-1' },
      lastAgentTimestamps: {
        'slack:C123::1700000000.000100::main': '2026-03-06T22:49:37.419Z',
      },
    };

    applyCleanedSessionControlState(
      'slack:C123::1700000000.000100::main',
      '2026-03-06T22:49:37.419Z',
      state,
      '2026-03-06T22:50:00.000Z',
    );

    expect(state).toEqual({
      sessions: {},
      lastAgentTimestamps: {
        'slack:C123::1700000000.000100::main': '2026-03-06T22:50:00.000Z',
      },
    });
  });
});

describe('cleanupSessionScope', () => {
  const scope = {
    channelId: 'slack:C123',
    threadId: '1700000000.000100',
    agentName: 'main',
  };
  const sessionKey = 'slack:C123::1700000000.000100::main';

  it('warns and leaves the session intact when repos are dirty without force', async () => {
    const runtime = {
      stopContainer: vi.fn(),
    };
    const queue = {
      inspectSession: vi.fn().mockReturnValue({
        active: true,
        containerName: 'runner-1',
        agentName: 'main',
        pendingMessages: true,
        pendingTaskCount: 1,
      }),
      cancelSession: vi.fn(),
    };
    const deleteSessionFn = vi.fn();
    const removeDirFn = vi.fn();

    await expect(
      cleanupSessionScope(sessionKey, scope, {
        force: false,
        runtime,
        queue,
        deleteSessionFn,
        findDirtyReposFn: () => ['repo-a'],
        removeDirFn,
      }),
    ).resolves.toEqual({
      status: 'warning',
      dirtyRepos: ['repo-a'],
    });

    expect(runtime.stopContainer).not.toHaveBeenCalled();
    expect(queue.cancelSession).not.toHaveBeenCalled();
    expect(deleteSessionFn).not.toHaveBeenCalled();
    expect(removeDirFn).not.toHaveBeenCalled();
  });

  it('stops the active container and removes session state when forced', async () => {
    const runtime = {
      stopContainer: vi.fn().mockResolvedValue(undefined),
    };
    const queue = {
      inspectSession: vi.fn().mockReturnValue({
        active: true,
        containerName: 'runner-1',
        agentName: 'main',
        pendingMessages: false,
        pendingTaskCount: 0,
      }),
      cancelSession: vi.fn(),
    };
    const deleteSessionFn = vi.fn();
    const removeDirFn = vi.fn();

    await expect(
      cleanupSessionScope(sessionKey, scope, {
        force: true,
        runtime,
        queue,
        deleteSessionFn,
        findDirtyReposFn: () => ['repo-a', 'repo-b'],
        removeDirFn,
      }),
    ).resolves.toEqual({
      status: 'cleaned',
      dirtyRepos: ['repo-a', 'repo-b'],
      stoppedActiveContainer: true,
      removedSessionDir: true,
    });

    expect(runtime.stopContainer).toHaveBeenCalledWith('runner-1');
    expect(queue.cancelSession).toHaveBeenCalledWith(sessionKey);
    expect(deleteSessionFn).toHaveBeenCalledWith(
      scope.channelId,
      scope.threadId,
      scope.agentName,
    );
    expect(removeDirFn).toHaveBeenCalled();
  });

  it('still clears persisted state when there is no active runner', async () => {
    const runtime = {
      stopContainer: vi.fn(),
    };
    const queue = {
      inspectSession: vi.fn().mockReturnValue(null),
      cancelSession: vi.fn(),
    };
    const deleteSessionFn = vi.fn();
    const removeDirFn = vi.fn();

    await expect(
      cleanupSessionScope(sessionKey, scope, {
        force: false,
        runtime,
        queue,
        deleteSessionFn,
        findDirtyReposFn: () => [],
        removeDirFn,
      }),
    ).resolves.toEqual({
      status: 'cleaned',
      dirtyRepos: [],
      stoppedActiveContainer: false,
      removedSessionDir: true,
    });

    expect(runtime.stopContainer).not.toHaveBeenCalled();
    expect(queue.cancelSession).toHaveBeenCalledWith(sessionKey);
  });
});
