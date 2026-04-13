import fs from 'fs';
import path from 'path';
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';

import { runContainerAgent, ContainerOutput } from './container-runner.js';
import type {
  ContainerHandle,
  ContainerRuntime,
  ContainerSpawnConfig,
} from './container-runtime.js';
import type { RegisteredAgent } from './types.js';

// Mock config
vi.mock('./config.js', () => ({
  AGENTS_DIR: '/tmp/devbox-test-agents',
  APP_ROOT: '/tmp/devbox-app',
  CONTAINER_IMAGE: 'devbox-agent:latest',
  CONTAINER_MAX_OUTPUT_SIZE: 10485760,
  CONTAINER_TIMEOUT: 10,
  DATA_DIR: '/tmp/devbox-test-data',
  IDLE_TIMEOUT: 10,
  TIMEZONE: 'America/Los_Angeles',
  WORKSPACE_REPOS: [],
  getAgentPath: (agentName: string) => `/tmp/devbox-app/agents/${agentName}`,
}));

// Mock logger
vi.mock('./logger.js', () => ({
  logger: {
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  },
}));

const testGroup: RegisteredAgent = {
  name: 'Test Group',
  agentName: 'test-group',
  trigger: '@Andy',
  added_at: new Date().toISOString(),
};

const testInput = {
  prompt: 'Hello',
  sessionKey: 'test@g.us::::test-group',
  agentName: 'test-group',
  chatJid: 'test@g.us',
  threadId: null,
};

function containerPathToHostPath(
  config: ContainerSpawnConfig,
  containerPath: string,
): string {
  for (const mount of config.mounts) {
    if (!containerPath.startsWith(mount.containerPath)) continue;
    const relative = path.relative(mount.containerPath, containerPath);
    return path.join(mount.hostPath, relative);
  }
  throw new Error(`No mount mapping found for path: ${containerPath}`);
}

function createManualHandle() {
  let resolveExit: ((value: { code: number | null }) => void) | null = null;
  const stop = vi.fn(async () => {});
  const waitForExit = vi.fn(
    () =>
      new Promise<{ code: number | null }>((resolve) => {
        resolveExit = resolve;
      }),
  );
  const handle: ContainerHandle = {
    id: 'test-container',
    waitForExit,
    stop,
  };
  return {
    handle,
    resolveExit: (code: number | null) => resolveExit?.({ code }),
    stop,
  };
}

function makeRuntime(
  onSpawn: (
    config: ContainerSpawnConfig,
  ) => ContainerHandle | Promise<ContainerHandle>,
): ContainerRuntime {
  return {
    ensureRunning: async () => {},
    cleanupOrphans: async () => {},
    stopContainer: async () => {},
    spawn: async (config) => onSpawn(config),
  };
}

function readLatestContainerLog(): string {
  const logsDir = '/tmp/devbox-test-agents/test-group/logs';
  const logFiles = fs
    .readdirSync(logsDir)
    .filter((entry) => entry.endsWith('.log'))
    .sort();
  const latestLog = logFiles.at(-1);
  if (!latestLog) {
    throw new Error('No container log file found');
  }
  return fs.readFileSync(path.join(logsDir, latestLog), 'utf-8');
}

describe('container-runner timeout behavior (file protocol)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    fs.rmSync('/tmp/devbox-test-data', { recursive: true, force: true });
    fs.rmSync('/tmp/devbox-test-agents', { recursive: true, force: true });
    fs.rmSync('/tmp/devbox-app', { recursive: true, force: true });
    fs.mkdirSync('/tmp/devbox-app/agents/test-group', { recursive: true });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('timeout after output resolves as success', async () => {
    const manual = createManualHandle();
    const runtime = makeRuntime((config) => {
      const runDir = containerPathToHostPath(config, config.env.DEVBOX_RUN_DIR);
      const outDir = path.join(runDir, 'out');
      fs.mkdirSync(outDir, { recursive: true });
      fs.writeFileSync(
        path.join(outDir, '000001.json'),
        JSON.stringify({
          status: 'success',
          result: 'Here is my response',
          newSessionId: 'session-123',
        } satisfies ContainerOutput),
      );
      fs.writeFileSync(
        path.join(runDir, 'done.json'),
        JSON.stringify({ status: 'success' }),
      );
      return manual.handle;
    });

    const onOutput = vi.fn(async () => {});
    const resultPromise = runContainerAgent(
      runtime,
      testGroup,
      testInput,
      () => {},
      onOutput,
    );

    await vi.advanceTimersByTimeAsync(500);
    await vi.advanceTimersByTimeAsync(30_100);

    expect(manual.stop).toHaveBeenCalledTimes(1);

    manual.resolveExit(137);
    await vi.advanceTimersByTimeAsync(200);

    const result = await resultPromise;
    expect(result.status).toBe('success');
    expect(result.newSessionId).toBe('session-123');
    expect(onOutput).toHaveBeenCalledWith(
      expect.objectContaining({ result: 'Here is my response' }),
    );
  });

  it('timeout with no output resolves as error', async () => {
    const manual = createManualHandle();
    const runtime = makeRuntime((config) => {
      const runDir = containerPathToHostPath(config, config.env.DEVBOX_RUN_DIR);
      fs.mkdirSync(path.join(runDir, 'out'), { recursive: true });
      fs.writeFileSync(
        path.join(runDir, 'done.json'),
        JSON.stringify({ status: 'success' }),
      );
      return manual.handle;
    });

    const onOutput = vi.fn(async () => {});
    const resultPromise = runContainerAgent(
      runtime,
      testGroup,
      testInput,
      () => {},
      onOutput,
    );

    await vi.advanceTimersByTimeAsync(30_100);
    expect(manual.stop).toHaveBeenCalledTimes(1);

    manual.resolveExit(137);
    await vi.advanceTimersByTimeAsync(200);

    const result = await resultPromise;
    expect(result.status).toBe('error');
    expect(result.error).toContain('timed out');
    expect(onOutput).not.toHaveBeenCalled();
  });

  it('normal exit after output resolves as success', async () => {
    const runtime = makeRuntime((config) => {
      const runDir = containerPathToHostPath(config, config.env.DEVBOX_RUN_DIR);
      const outDir = path.join(runDir, 'out');
      fs.mkdirSync(outDir, { recursive: true });
      fs.writeFileSync(
        path.join(outDir, '000001.json'),
        JSON.stringify({
          status: 'success',
          result: 'Done',
          newSessionId: 'session-456',
        } satisfies ContainerOutput),
      );
      fs.writeFileSync(
        path.join(runDir, 'done.json'),
        JSON.stringify({ status: 'success' }),
      );
      return {
        id: 'test-container',
        waitForExit: async () => ({ code: 0 }),
        stop: async () => {},
      };
    });

    const onOutput = vi.fn(async () => {});
    const result = await runContainerAgent(
      runtime,
      testGroup,
      testInput,
      () => {},
      onOutput,
    );

    expect(result.status).toBe('success');
    expect(result.newSessionId).toBe('session-456');
    expect(onOutput).toHaveBeenCalledWith(
      expect.objectContaining({ result: 'Done' }),
    );
  });

  it('mounts session metadata separately and materializes instructions in /workspace', async () => {
    fs.writeFileSync(
      '/tmp/devbox-app/agents/test-group/CLAUDE.md',
      '# Agent instructions\n',
    );
    fs.writeFileSync(
      '/tmp/devbox-app/agents/test-group/AGENTS.md',
      '# Workspace instructions\n',
    );

    let spawnConfig: ContainerSpawnConfig | undefined;
    const runtime = makeRuntime((config) => {
      spawnConfig = config;
      const runDir = containerPathToHostPath(config, config.env.DEVBOX_RUN_DIR);
      fs.mkdirSync(path.join(runDir, 'out'), { recursive: true });
      fs.writeFileSync(
        path.join(runDir, 'done.json'),
        JSON.stringify({ status: 'success' }),
      );
      return {
        id: 'test-container',
        waitForExit: async () => ({ code: 0 }),
        stop: async () => {},
      };
    });

    const result = await runContainerAgent(
      runtime,
      testGroup,
      testInput,
      () => {},
    );

    expect(result.status).toBe('success');
    expect(spawnConfig).toBeDefined();
    expect(spawnConfig?.env.DEVBOX_RUN_DIR).toMatch(/^\/ipc\/runs\//);
    expect(spawnConfig?.env.HOME).toBe('/workspace/.home');
    expect(spawnConfig?.user).toMatch(/^\d+:\d+$/);
    expect(spawnConfig?.mounts).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          containerPath: '/session',
          readonly: true,
        }),
        expect.objectContaining({
          containerPath: '/workspace',
          readonly: false,
        }),
        expect.objectContaining({
          containerPath: '/ipc',
          readonly: false,
        }),
        expect.objectContaining({
          containerPath: '/workspace/.home/.claude',
          readonly: false,
        }),
      ]),
    );

    const workspaceMount = spawnConfig?.mounts.find(
      (mount) => mount.containerPath === '/workspace',
    );
    expect(workspaceMount).toBeDefined();
    expect(
      fs.readFileSync(
        path.join(workspaceMount!.hostPath, 'CLAUDE.md'),
        'utf-8',
      ),
    ).toContain('Agent instructions');
    expect(
      fs.readFileSync(
        path.join(workspaceMount!.hostPath, 'AGENTS.md'),
        'utf-8',
      ),
    ).toContain('Workspace instructions');
  });

  it('logs resume diagnostics when done.json reports an error', async () => {
    const runtime = makeRuntime((config) => {
      const runDir = containerPathToHostPath(config, config.env.DEVBOX_RUN_DIR);
      fs.mkdirSync(path.join(runDir, 'out'), { recursive: true });
      fs.writeFileSync(
        path.join(runDir, 'done.json'),
        JSON.stringify({
          status: 'error',
          error: 'Runner reported error in done.json',
          details: {
            type: 'result',
            subtype: 'error_during_execution',
            duration_ms: 0,
            total_cost_usd: 0,
            num_turns: 0,
            errors: ['No conversation found with session ID: session-789'],
          },
        }),
      );
      return {
        id: 'test-container',
        waitForExit: async () => ({ code: 1 }),
        stop: async () => {},
      };
    });

    const result = await runContainerAgent(
      runtime,
      testGroup,
      {
        ...testInput,
        sessionId: 'session-789',
      },
      () => {},
    );

    expect(result.status).toBe('error');
    expect(result.error).toContain('Runner reported error');
    expect(result.errorKind).toBe('stale_session_resume');

    const logContent = readLatestContainerLog();
    expect(logContent).toContain('=== Resume Diagnostics ===');
    expect(logContent).toContain('Resume Session ID: session-789');
    expect(logContent).toContain('Transcript Expected To Exist: yes');
    expect(logContent).toContain('"details"');
    expect(logContent).toContain('No conversation found with session ID');
  });

  it('detects stale session resume when error message has redacted session ID', async () => {
    const runtime = makeRuntime((config) => {
      const runDir = containerPathToHostPath(config, config.env.DEVBOX_RUN_DIR);
      fs.mkdirSync(path.join(runDir, 'out'), { recursive: true });
      fs.writeFileSync(
        path.join(runDir, 'done.json'),
        JSON.stringify({
          status: 'error',
          error: 'SDK error during execution',
          details: {
            type: 'result',
            subtype: 'error_during_execution',
            duration_ms: 0,
            total_cost_usd: 0,
            num_turns: 0,
            errors: [
              'No conversation found with session ID: d8333d5[REDACTED]-da8d-40[REDACTED]f-a64a-f[REDACTED]092e845588',
            ],
          },
        }),
      );
      return {
        id: 'test-container',
        waitForExit: async () => ({ code: 1 }),
        stop: async () => {},
      };
    });

    const result = await runContainerAgent(
      runtime,
      testGroup,
      {
        ...testInput,
        sessionId: 'd8333d51-da8d-401f-a64a-f1092e845588',
      },
      () => {},
    );

    expect(result.status).toBe('error');
    expect(result.errorKind).toBe('stale_session_resume');
  });

  it('classifies seed clone failures emitted by the runner entrypoint', async () => {
    const runtime = makeRuntime((config) => {
      const runDir = containerPathToHostPath(config, config.env.DEVBOX_RUN_DIR);
      fs.mkdirSync(path.join(runDir, 'out'), { recursive: true });
      fs.writeFileSync(
        path.join(runDir, 'done.json'),
        JSON.stringify({ status: 'success' }),
      );
      config.onStderrChunk?.("Cloning into '/workspace/crypto-quant'...\n");
      config.onStderrChunk?.(
        'DEVBOX_SEED_CLONE_ERROR: Timed out cloning https://github.com/galpha-ai/crypto-quant.git after 20s.\n',
      );
      return {
        id: 'test-container',
        waitForExit: async () => ({ code: 128 }),
        stop: async () => {},
      };
    });

    const result = await runContainerAgent(
      runtime,
      testGroup,
      testInput,
      () => {},
    );

    expect(result.status).toBe('error');
    expect(result.errorKind).toBe('seed_clone_failed');
    expect(result.error).toContain('DEVBOX_SEED_CLONE_ERROR');
  });

  it('fails fast when seed repo source is local path', async () => {
    fs.mkdirSync('/tmp/devbox-app/agents/test-group', { recursive: true });
    fs.writeFileSync(
      '/tmp/devbox-app/agents/test-group/seed.yaml',
      'repos:\n  - name: local-repo\n    source: ./local-repo\n',
    );

    const runtime = makeRuntime(() => {
      throw new Error('spawn should not be called');
    });

    const result = await runContainerAgent(
      runtime,
      testGroup,
      testInput,
      () => {},
    );

    expect(result.status).toBe('error');
    expect(result.error).toContain('Local repo source is not supported');
  });

  it('uses runner image from seed.yaml when configured', async () => {
    fs.mkdirSync('/tmp/devbox-app/agents/test-group', { recursive: true });
    fs.writeFileSync(
      '/tmp/devbox-app/agents/test-group/seed.yaml',
      [
        'image: custom/agent-runner:rust',
        'repos:',
        '  - name: remote-repo',
        '    source: https://github.com/example/remote-repo.git',
        '',
      ].join('\n'),
    );

    let spawnedImage: string | undefined;
    const runtime = makeRuntime((config) => {
      spawnedImage = config.image;
      const runDir = containerPathToHostPath(config, config.env.DEVBOX_RUN_DIR);
      fs.mkdirSync(path.join(runDir, 'out'), { recursive: true });
      fs.writeFileSync(
        path.join(runDir, 'done.json'),
        JSON.stringify({ status: 'success' }),
      );
      return {
        id: 'test-container',
        waitForExit: async () => ({ code: 0 }),
        stop: async () => {},
      };
    });

    const result = await runContainerAgent(
      runtime,
      testGroup,
      testInput,
      () => {},
    );

    expect(result.status).toBe('success');
    expect(spawnedImage).toBe('custom/agent-runner:rust');
  });

  it('passes secret mounts from seed.yaml to the runtime spawn config', async () => {
    fs.mkdirSync('/tmp/devbox-app/agents/test-group', { recursive: true });
    fs.writeFileSync(
      '/tmp/devbox-app/agents/test-group/seed.yaml',
      [
        'secretMounts:',
        '  - secretName: example-kubeconfig',
        '    mountPath: /home/devbox/.kube',
        '    hostPath: /tmp/kubeconfigs/example',
        '',
      ].join('\n'),
    );

    let spawnedSecretMounts: ContainerSpawnConfig['secretMounts'];
    const runtime = makeRuntime((config) => {
      spawnedSecretMounts = config.secretMounts;
      const runDir = containerPathToHostPath(config, config.env.DEVBOX_RUN_DIR);
      fs.mkdirSync(path.join(runDir, 'out'), { recursive: true });
      fs.writeFileSync(
        path.join(runDir, 'done.json'),
        JSON.stringify({ status: 'success' }),
      );
      return {
        id: 'test-container',
        waitForExit: async () => ({ code: 0 }),
        stop: async () => {},
      };
    });

    const result = await runContainerAgent(
      runtime,
      testGroup,
      testInput,
      () => {},
    );

    expect(result.status).toBe('success');
    expect(spawnedSecretMounts).toEqual([
      {
        secretName: 'example-kubeconfig',
        hostPath: '/tmp/kubeconfigs/example',
        containerPath: '/home/devbox/.kube',
      },
    ]);
  });

  it('falls back to global runner image when seed.yaml omits image', async () => {
    fs.mkdirSync('/tmp/devbox-app/agents/test-group', { recursive: true });
    fs.writeFileSync(
      '/tmp/devbox-app/agents/test-group/seed.yaml',
      [
        'repos:',
        '  - name: remote-repo',
        '    source: https://github.com/example/remote-repo.git',
        '',
      ].join('\n'),
    );

    let spawnedImage: string | undefined;
    const runtime = makeRuntime((config) => {
      spawnedImage = config.image;
      const runDir = containerPathToHostPath(config, config.env.DEVBOX_RUN_DIR);
      fs.mkdirSync(path.join(runDir, 'out'), { recursive: true });
      fs.writeFileSync(
        path.join(runDir, 'done.json'),
        JSON.stringify({ status: 'success' }),
      );
      return {
        id: 'test-container',
        waitForExit: async () => ({ code: 0 }),
        stop: async () => {},
      };
    });

    const result = await runContainerAgent(
      runtime,
      testGroup,
      testInput,
      () => {},
    );

    expect(result.status).toBe('success');
    expect(spawnedImage).toBe('devbox-agent:latest');
  });
});
