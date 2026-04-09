import fs from 'fs';
import path from 'path';
import os from 'os';

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

import { SessionQueue } from './session-queue.js';

// Use a temp dir for DATA_DIR so tests don't collide with real data
let testDataDir: string;

vi.mock('./config.js', () => ({
  get DATA_DIR() {
    return testDataDir;
  },
  MAX_CONCURRENT_CONTAINERS: 2,
}));

// Dynamic import after mocks are set up
const { touchSessionHeartbeat, startSessionGc } =
  await import('./session-gc.js');

// Helper to encode session keys the same way agent-folder.ts does
function encodeSessionScopeKey(sessionKey: string): string {
  return Buffer.from(sessionKey, 'utf-8').toString('base64url');
}

function makeSessionDir(
  agentName: string,
  sessionKey: string,
  heartbeatAgeMs?: number,
): string {
  const encoded = encodeSessionScopeKey(sessionKey);
  const sessionDir = path.join(testDataDir, 'sessions', agentName, encoded);
  fs.mkdirSync(sessionDir, { recursive: true });

  if (heartbeatAgeMs !== undefined) {
    const heartbeatPath = path.join(sessionDir, '_last_activity');
    fs.writeFileSync(heartbeatPath, '');
    const pastTime = new Date(Date.now() - heartbeatAgeMs);
    fs.utimesSync(heartbeatPath, pastTime, pastTime);
  }

  return sessionDir;
}

describe('Session GC', () => {
  beforeEach(() => {
    testDataDir = fs.mkdtempSync(path.join(os.tmpdir(), 'session-gc-test-'));
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });

  afterEach(() => {
    vi.useRealTimers();
    fs.rmSync(testDataDir, { recursive: true, force: true });
  });

  describe('touchSessionHeartbeat', () => {
    it('creates heartbeat file if missing', () => {
      const sessionKey = 'tg:123::::main';
      const encoded = encodeSessionScopeKey(sessionKey);
      const sessionDir = path.join(testDataDir, 'sessions', 'main', encoded);
      fs.mkdirSync(sessionDir, { recursive: true });

      touchSessionHeartbeat('main', sessionKey);

      const heartbeatPath = path.join(sessionDir, '_last_activity');
      expect(fs.existsSync(heartbeatPath)).toBe(true);
    });

    it('updates mtime of existing heartbeat file', () => {
      const sessionKey = 'tg:123::thread1::main';
      const sessionDir = makeSessionDir('main', sessionKey, 3600000);

      const oldMtime = fs.statSync(
        path.join(sessionDir, '_last_activity'),
      ).mtimeMs;

      // Advance time and touch again
      vi.advanceTimersByTime(1000);
      touchSessionHeartbeat('main', sessionKey);

      const newMtime = fs.statSync(
        path.join(sessionDir, '_last_activity'),
      ).mtimeMs;
      expect(newMtime).toBeGreaterThan(oldMtime);
    });
  });

  describe('startSessionGc', () => {
    function makeDeps(
      overrides?: Partial<Parameters<typeof startSessionGc>[0]>,
    ) {
      const sessions: Record<string, string> = {};
      const lastAgentTimestamp: Record<string, string> = {};
      const deleteSession = vi.fn();
      return {
        queue: new SessionQueue(),
        getSessions: () => sessions,
        getLastAgentTimestamp: () => lastAgentTimestamp,
        saveState: vi.fn(),
        deleteSession,
        interval: 1000, // 1s for fast tests
        maxAge: 6 * 60 * 60 * 1000, // 6 hours
        sessions,
        lastAgentTimestamp,
        deleteSessionFn: deleteSession,
        ...overrides,
      };
    }

    it('removes thread-scoped session older than maxAge', async () => {
      const sessionKey = 'tg:123::thread1::main';
      const sessionDir = makeSessionDir(
        'main',
        sessionKey,
        7 * 60 * 60 * 1000, // 7 hours old
      );

      const deps = makeDeps();
      deps.sessions[sessionKey] = 'some-session-id';
      deps.lastAgentTimestamp[sessionKey] = '2024-01-01T00:00:00Z';

      startSessionGc(deps);

      // Advance past the first sweep interval
      await vi.advanceTimersByTimeAsync(1500);

      expect(fs.existsSync(sessionDir)).toBe(false);
      expect(deps.sessions[sessionKey]).toBeUndefined();
      expect(deps.lastAgentTimestamp[sessionKey]).toBeUndefined();
      expect(deps.deleteSessionFn).toHaveBeenCalledWith(
        'tg:123',
        'thread1',
        'main',
      );
      expect(deps.saveState).toHaveBeenCalled();
    });

    it('never removes channel-scoped session (no threadId)', async () => {
      const sessionKey = 'tg:123::::main';
      const sessionDir = makeSessionDir(
        'main',
        sessionKey,
        24 * 60 * 60 * 1000, // 24 hours old
      );

      const deps = makeDeps();
      startSessionGc(deps);
      await vi.advanceTimersByTimeAsync(1500);

      expect(fs.existsSync(sessionDir)).toBe(true);
    });

    it('skips active session (container running)', async () => {
      const sessionKey = 'tg:123::thread1::main';
      const sessionDir = makeSessionDir('main', sessionKey, 7 * 60 * 60 * 1000);

      const deps = makeDeps();
      // Simulate an active container by setting up processMessagesFn
      // that blocks, then enqueuing to make the session active.
      let resolveProcess: () => void;
      deps.queue.setProcessMessagesFn(async () => {
        await new Promise<void>((resolve) => {
          resolveProcess = resolve;
        });
        return true;
      });
      deps.queue.enqueueMessageCheck(sessionKey);
      await vi.advanceTimersByTimeAsync(10);

      startSessionGc(deps);
      await vi.advanceTimersByTimeAsync(1500);

      // Session dir should still exist because session is active
      expect(fs.existsSync(sessionDir)).toBe(true);

      // Clean up
      resolveProcess!();
      await vi.advanceTimersByTimeAsync(10);
    });

    it('keeps session with recent heartbeat', async () => {
      const sessionKey = 'tg:123::thread1::main';
      const sessionDir = makeSessionDir(
        'main',
        sessionKey,
        30 * 60 * 1000, // 30 minutes old (within 6h TTL)
      );

      const deps = makeDeps();
      startSessionGc(deps);
      await vi.advanceTimersByTimeAsync(1500);

      expect(fs.existsSync(sessionDir)).toBe(true);
    });

    it('falls back to directory mtime when no heartbeat file', async () => {
      const sessionKey = 'tg:123::thread1::main';
      const encoded = encodeSessionScopeKey(sessionKey);
      const sessionDir = path.join(testDataDir, 'sessions', 'main', encoded);
      fs.mkdirSync(sessionDir, { recursive: true });

      // Set directory mtime to 7 hours ago (no heartbeat file)
      const pastTime = new Date(Date.now() - 7 * 60 * 60 * 1000);
      fs.utimesSync(sessionDir, pastTime, pastTime);

      const deps = makeDeps();
      startSessionGc(deps);
      await vi.advanceTimersByTimeAsync(1500);

      expect(fs.existsSync(sessionDir)).toBe(false);
    });
  });
});
