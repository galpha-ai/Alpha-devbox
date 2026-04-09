import { describe, it, expect, vi, beforeEach } from 'vitest';
import { EventEmitter } from 'events';
import { PassThrough } from 'stream';

const {
  mockConfig,
  mockK8sApi,
  mockLoadFromFile,
  mockLoadFromDefault,
  mockMakeApiClient,
} = vi.hoisted(() => ({
  mockConfig: {
    CONTAINER_RUNTIME: 'docker' as 'docker' | 'kubernetes',
    KUBERNETES_RUNTIME: {
      namespace: 'devbox-agent',
      pvcName: 'devbox-data',
      dataMountPath: '/data/devbox-agent',
      serviceAccount: 'devbox-runner',
      imagePullPolicy: 'IfNotPresent' as const,
      runnerResources: {
        cpu: '2',
        memory: '4Gi',
        ephemeralStorage: '10Gi',
      },
    },
  },
  mockK8sApi: {
    listNamespacedPod: vi.fn(),
    createNamespacedPod: vi.fn(),
    readNamespacedPod: vi.fn(),
    deleteNamespacedPod: vi.fn(),
  },
  mockLoadFromFile: vi.fn(),
  mockLoadFromDefault: vi.fn(),
  mockMakeApiClient: vi.fn(),
}));

mockMakeApiClient.mockImplementation(() => mockK8sApi);

vi.mock('./config.js', () => mockConfig);

// Mock logger
vi.mock('./logger.js', () => ({
  logger: {
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  },
}));

vi.mock('@kubernetes/client-node', () => ({
  KubeConfig: class {
    loadFromFile(pathname: string) {
      mockLoadFromFile(pathname);
    }
    loadFromDefault() {
      mockLoadFromDefault();
    }
    makeApiClient() {
      return mockMakeApiClient();
    }
  },
  CoreV1Api: class {},
}));

const mockExecSync = vi.fn();
const mockSpawn = vi.fn();
vi.mock('child_process', () => ({
  execSync: (...args: unknown[]) => mockExecSync(...args),
  spawn: (...args: unknown[]) => mockSpawn(...args),
}));

import {
  DOCKER_CLI_BIN,
  DockerRuntime,
  K8sRuntime,
  readonlyMountArgs,
  stopContainer,
  createContainerRuntime,
} from './container-runtime.js';
import { logger } from './logger.js';

function createFakeSpawnProcess() {
  const proc = new EventEmitter() as EventEmitter & {
    stdout: PassThrough;
    stderr: PassThrough;
  };
  proc.stdout = new PassThrough();
  proc.stderr = new PassThrough();
  return proc;
}

beforeEach(() => {
  vi.clearAllMocks();
  mockConfig.CONTAINER_RUNTIME = 'docker';
});

describe('readonlyMountArgs', () => {
  it('returns -v flag with :ro suffix', () => {
    expect(readonlyMountArgs('/host/path', '/container/path')).toEqual([
      '-v',
      '/host/path:/container/path:ro',
    ]);
  });
});

describe('stopContainer', () => {
  it('returns stop command using DOCKER_CLI_BIN by default', () => {
    expect(stopContainer('devbox-test-123')).toBe(
      `${DOCKER_CLI_BIN} stop devbox-test-123`,
    );
  });
});

describe('DockerRuntime.ensureRunning', () => {
  it('does nothing when runtime is already running', async () => {
    mockExecSync.mockReturnValueOnce('');
    const runtime = new DockerRuntime('docker');

    await runtime.ensureRunning();

    expect(mockExecSync).toHaveBeenCalledWith('docker info', {
      stdio: 'pipe',
      timeout: 10000,
    });
    expect(logger.debug).toHaveBeenCalledWith(
      'Container runtime already running',
    );
  });

  it('throws when docker info fails', async () => {
    mockExecSync.mockImplementationOnce(() => {
      throw new Error('Cannot connect to the Docker daemon');
    });
    const runtime = new DockerRuntime('docker');

    await expect(runtime.ensureRunning()).rejects.toThrow(
      'Container runtime is required but failed to start',
    );
    expect(logger.error).toHaveBeenCalled();
  });
});

describe('DockerRuntime.cleanupOrphans', () => {
  it('stops orphaned devbox containers', async () => {
    mockExecSync.mockReturnValueOnce(
      'devbox-group1-111\ndevbox-group2-222\n',
    );
    mockExecSync.mockReturnValue('');
    const runtime = new DockerRuntime('docker');

    await runtime.cleanupOrphans();

    expect(mockExecSync).toHaveBeenCalledTimes(3);
    expect(mockExecSync).toHaveBeenNthCalledWith(
      2,
      'docker stop devbox-group1-111',
      { stdio: 'pipe' },
    );
    expect(mockExecSync).toHaveBeenNthCalledWith(
      3,
      'docker stop devbox-group2-222',
      { stdio: 'pipe' },
    );
    expect(logger.info).toHaveBeenCalledWith(
      { count: 2, names: ['devbox-group1-111', 'devbox-group2-222'] },
      'Stopped orphaned containers',
    );
  });

  it('warns and continues when ps fails', async () => {
    mockExecSync.mockImplementationOnce(() => {
      throw new Error('docker not available');
    });
    const runtime = new DockerRuntime('docker');

    await runtime.cleanupOrphans();

    expect(logger.warn).toHaveBeenCalledWith(
      expect.objectContaining({ err: expect.any(Error) }),
      'Failed to clean up orphaned containers',
    );
  });
});

describe('DockerRuntime.stopContainer', () => {
  it('stops a named container directly', async () => {
    const runtime = new DockerRuntime('docker');

    await runtime.stopContainer('devbox-test-123');

    expect(mockExecSync).toHaveBeenCalledWith('docker stop devbox-test-123', {
      stdio: 'pipe',
      timeout: 15000,
    });
  });
});

describe('DockerRuntime.spawn', () => {
  it('spawns docker run and returns a stoppable handle', async () => {
    const proc = createFakeSpawnProcess();
    mockSpawn.mockReturnValueOnce(proc);
    const runtime = new DockerRuntime('docker');

    const stdoutSpy = vi.fn();
    const stderrSpy = vi.fn();
    const handle = await runtime.spawn({
      name: 'devbox-test',
      image: 'devbox-runner:latest',
      mounts: [
        {
          hostPath: '/host/a',
          containerPath: '/container/a',
          readonly: false,
        },
      ],
      secretMounts: [
        {
          secretName: 'quant-dev-kubeconfig',
          hostPath: '/host/kubeconfigs/quant-dev',
          containerPath: '/home/devbox/.kube',
        },
      ],
      env: {
        TZ: 'America/New_York',
      },
      user: '1000:1000',
      onStdoutChunk: stdoutSpy,
      onStderrChunk: stderrSpy,
    });

    proc.stdout.push('hello');
    proc.stderr.push('world');
    proc.emit('close', 0);

    await expect(handle.waitForExit()).resolves.toEqual({ code: 0 });
    expect(stdoutSpy).toHaveBeenCalledWith('hello');
    expect(stderrSpy).toHaveBeenCalledWith('world');
    expect(mockSpawn).toHaveBeenCalledWith(
      'docker',
      [
        'run',
        '--rm',
        '--name',
        'devbox-test',
        '--user',
        '1000:1000',
        '-e',
        'TZ=America/New_York',
        '-v',
        '/host/a:/container/a',
        '-v',
        '/host/kubeconfigs/quant-dev:/home/devbox/.kube:ro',
        'devbox-runner:latest',
      ],
      { stdio: ['ignore', 'pipe', 'pipe'] },
    );

    await handle.stop();
    expect(mockExecSync).toHaveBeenCalledWith('docker stop devbox-test', {
      stdio: 'pipe',
      timeout: 15000,
    });
  });
});

describe('createContainerRuntime', () => {
  it('returns DockerRuntime when configured for docker', () => {
    mockConfig.CONTAINER_RUNTIME = 'docker';
    const runtime = createContainerRuntime();
    expect(runtime).toBeInstanceOf(DockerRuntime);
  });

  it('returns K8sRuntime when configured for kubernetes', () => {
    mockConfig.CONTAINER_RUNTIME = 'kubernetes';
    const runtime = createContainerRuntime();
    expect(runtime).toBeInstanceOf(K8sRuntime);
    expect(mockLoadFromDefault).toHaveBeenCalled();
  });
});

describe('K8sRuntime', () => {
  it('checks runtime health via listNamespacedPod', async () => {
    const coreApi = {
      listNamespacedPod: vi.fn().mockResolvedValue({ items: [] }),
    };
    const runtime = new K8sRuntime(
      coreApi as any,
      mockConfig.KUBERNETES_RUNTIME,
    );

    await runtime.ensureRunning();

    expect(coreApi.listNamespacedPod).toHaveBeenCalledWith({
      namespace: 'devbox-agent',
      limit: 1,
    });
  });

  it('cleans up orphaned pods by runner label', async () => {
    const coreApi = {
      listNamespacedPod: vi.fn().mockResolvedValue({
        items: [
          { metadata: { name: 'devbox-a' } },
          { metadata: { name: 'devbox-b' } },
        ],
      }),
      deleteNamespacedPod: vi.fn().mockResolvedValue({}),
    };
    const runtime = new K8sRuntime(
      coreApi as any,
      mockConfig.KUBERNETES_RUNTIME,
    );

    await runtime.cleanupOrphans();

    expect(coreApi.listNamespacedPod).toHaveBeenCalledWith({
      namespace: 'devbox-agent',
      labelSelector: 'devbox-runner=true',
    });
    expect(coreApi.deleteNamespacedPod).toHaveBeenCalledTimes(2);
  });

  it('stops a named pod directly', async () => {
    const coreApi = {
      deleteNamespacedPod: vi.fn().mockResolvedValue({}),
    };
    const runtime = new K8sRuntime(
      coreApi as any,
      mockConfig.KUBERNETES_RUNTIME,
    );

    await runtime.stopContainer('devbox-main-123');

    expect(coreApi.deleteNamespacedPod).toHaveBeenCalledWith({
      name: 'devbox-main-123',
      namespace: 'devbox-agent',
      gracePeriodSeconds: 10,
      propagationPolicy: 'Background',
    });
  });

  it('creates pod with PVC subPath mounts and secret volumes and returns a handle', async () => {
    const coreApi = {
      createNamespacedPod: vi.fn().mockResolvedValue({}),
      readNamespacedPod: vi
        .fn()
        .mockResolvedValueOnce({ status: { phase: 'Running' } })
        .mockResolvedValueOnce({ status: { phase: 'Succeeded' } }),
      deleteNamespacedPod: vi.fn().mockResolvedValue({}),
    };
    const runtime = new K8sRuntime(
      coreApi as any,
      mockConfig.KUBERNETES_RUNTIME,
    );

    const handle = await runtime.spawn({
      name: 'devbox-Main-123',
      image: 'devbox-runner:latest',
      mounts: [
        {
          hostPath: '/data/devbox-agent/data/sessions/main/session-123',
          containerPath: '/session',
          readonly: true,
        },
        {
          hostPath:
            '/data/devbox-agent/data/sessions/main/session-123/workspace',
          containerPath: '/workspace',
          readonly: false,
        },
      ],
      secretMounts: [
        {
          secretName: 'quant-dev-kubeconfig',
          hostPath: '/ignored/in-k8s',
          containerPath: '/home/devbox/.kube',
        },
      ],
      env: {
        TZ: 'America/New_York',
      },
      user: '1000:1000',
    });

    expect(coreApi.createNamespacedPod).toHaveBeenCalledWith({
      namespace: 'devbox-agent',
      body: expect.objectContaining({
        metadata: expect.objectContaining({
          name: 'devbox-main-123',
          labels: { 'devbox-runner': 'true' },
        }),
        spec: expect.objectContaining({
          serviceAccountName: 'devbox-runner',
          restartPolicy: 'Never',
          containers: [
            expect.objectContaining({
              image: 'devbox-runner:latest',
              securityContext: {
                runAsUser: 1000,
                runAsGroup: 1000,
              },
              env: [{ name: 'TZ', value: 'America/New_York' }],
              volumeMounts: expect.arrayContaining([
                expect.objectContaining({
                  mountPath: '/session',
                  subPath: 'data/sessions/main/session-123',
                  readOnly: true,
                }),
                expect.objectContaining({
                  mountPath: '/workspace',
                  subPath: 'data/sessions/main/session-123/workspace',
                }),
                expect.objectContaining({
                  mountPath: '/home/devbox/.kube',
                  readOnly: true,
                }),
              ]),
            }),
          ],
          volumes: expect.arrayContaining([
            expect.objectContaining({
              name: 'data',
              persistentVolumeClaim: {
                claimName: 'devbox-data',
              },
            }),
            expect.objectContaining({
              name: 'secret-mount-0',
              secret: {
                secretName: 'quant-dev-kubeconfig',
              },
            }),
          ]),
        }),
      }),
    });

    await expect(handle.waitForExit()).resolves.toEqual({ code: 0 });
    await handle.stop();
    expect(coreApi.deleteNamespacedPod).toHaveBeenCalled();
  });

  it('throws when mount is outside kubernetes data mount path', async () => {
    const runtime = new K8sRuntime(
      {
        createNamespacedPod: vi.fn(),
      } as any,
      mockConfig.KUBERNETES_RUNTIME,
    );

    await expect(
      runtime.spawn({
        name: 'devbox-main-1',
        image: 'devbox-runner:latest',
        mounts: [
          {
            hostPath: '/tmp/not-shared',
            containerPath: '/workspace',
            readonly: false,
          },
        ],
        env: {},
      }),
    ).rejects.toThrow('is outside kubernetes.data_mount_path');
  });

  it('keeps pod names RFC1123-safe and bounded to 63 chars', async () => {
    const coreApi = {
      createNamespacedPod: vi.fn().mockResolvedValue({}),
    };
    const runtime = new K8sRuntime(
      coreApi as any,
      mockConfig.KUBERNETES_RUNTIME,
    );

    await runtime.spawn({
      name: 'devbox-AGENT_NAME_WITH_VERY_LONG_ID-1234567890123456789012345678901234567890',
      image: 'devbox-runner:latest',
      mounts: [
        {
          hostPath:
            '/data/devbox-agent/data/sessions/main/session-123/workspace',
          containerPath: '/workspace',
          readonly: false,
        },
      ],
      env: {},
    });

    const body = coreApi.createNamespacedPod.mock.calls[0][0].body;
    const podName = body.metadata.name as string;
    expect(podName.length).toBeLessThanOrEqual(63);
    expect(podName).toMatch(/^[a-z0-9]([-a-z0-9]*[a-z0-9])?$/);
  });
});
