/**
 * Container runtime lifecycle abstraction.
 * Runtime implementations manage process/pod lifecycle only.
 */
import path from 'path';
import { spawn } from 'child_process';
import { execSync } from 'child_process';
import * as k8s from '@kubernetes/client-node';

import {
  CONTAINER_RUNTIME,
  KUBERNETES_RUNTIME,
  KubernetesRuntimeConfig,
} from './config.js';
import { logger } from './logger.js';

/** Docker CLI binary name. */
export const DOCKER_CLI_BIN =
  process.env.DOCKER_CLI_BIN || process.env.CONTAINER_RUNTIME_BIN || 'docker';

export interface RuntimeMount {
  hostPath: string;
  containerPath: string;
  readonly: boolean;
}

export interface RuntimeSecretMount {
  secretName: string;
  hostPath: string;
  containerPath: string;
}

export interface ContainerSpawnConfig {
  name: string;
  image: string;
  mounts: RuntimeMount[];
  secretMounts?: RuntimeSecretMount[];
  env: Record<string, string>;
  user?: string;
  onStdoutChunk?: (chunk: string) => void;
  onStderrChunk?: (chunk: string) => void;
}

export interface ContainerHandle {
  id: string;
  waitForExit(): Promise<{ code: number | null }>;
  stop(): Promise<void>;
}

export interface ContainerRuntime {
  ensureRunning(): Promise<void>;
  cleanupOrphans(): Promise<void>;
  stopContainer(id: string): Promise<void>;
  spawn(config: ContainerSpawnConfig): Promise<ContainerHandle>;
}

/** Returns CLI args for a readonly bind mount. */
export function readonlyMountArgs(
  hostPath: string,
  containerPath: string,
): string[] {
  return ['-v', `${hostPath}:${containerPath}:ro`];
}

/** Returns the shell command to stop a container by name. */
export function stopContainer(name: string, cliBin = DOCKER_CLI_BIN): string {
  return `${cliBin} stop ${name}`;
}

class DockerContainerHandle implements ContainerHandle {
  constructor(
    public readonly id: string,
    private readonly waitPromise: Promise<{ code: number | null }>,
    private readonly cliBin: string,
  ) {}

  waitForExit(): Promise<{ code: number | null }> {
    return this.waitPromise;
  }

  async stop(): Promise<void> {
    try {
      execSync(stopContainer(this.id, this.cliBin), {
        stdio: 'pipe',
        timeout: 15000,
      });
    } catch {
      // ignore (already stopped, not found, etc)
    }
  }
}

export class DockerRuntime implements ContainerRuntime {
  constructor(private readonly cliBin = DOCKER_CLI_BIN) {}

  async ensureRunning(): Promise<void> {
    try {
      execSync(`${this.cliBin} info`, {
        stdio: 'pipe',
        timeout: 10000,
      });
      logger.debug('Container runtime already running');
    } catch (err) {
      logger.error({ err }, 'Failed to reach container runtime');
      console.error(
        '\n╔════════════════════════════════════════════════════════════════╗',
      );
      console.error(
        '║  FATAL: Container runtime failed to start                      ║',
      );
      console.error(
        '║                                                                ║',
      );
      console.error(
        '║  Agents cannot run without a container runtime. To fix:        ║',
      );
      console.error(
        '║  1. Ensure Docker is installed and running                     ║',
      );
      console.error(
        '║  2. Run: docker info                                           ║',
      );
      console.error(
        '║  3. Restart Devbox Agent                                           ║',
      );
      console.error(
        '╚════════════════════════════════════════════════════════════════╝\n',
      );
      throw new Error('Container runtime is required but failed to start');
    }
  }

  async cleanupOrphans(): Promise<void> {
    try {
      const output = execSync(
        `${this.cliBin} ps --filter name=devbox- --format '{{.Names}}'`,
        { stdio: ['pipe', 'pipe', 'pipe'], encoding: 'utf-8' },
      );
      const orphans = output.trim().split('\n').filter(Boolean);
      for (const name of orphans) {
        try {
          execSync(stopContainer(name, this.cliBin), { stdio: 'pipe' });
        } catch {
          /* already stopped */
        }
      }
      if (orphans.length > 0) {
        logger.info(
          { count: orphans.length, names: orphans },
          'Stopped orphaned containers',
        );
      }
    } catch (err) {
      logger.warn({ err }, 'Failed to clean up orphaned containers');
    }
  }

  async stopContainer(id: string): Promise<void> {
    try {
      execSync(stopContainer(id, this.cliBin), {
        stdio: 'pipe',
        timeout: 15000,
      });
    } catch {
      // ignore (already stopped, not found, etc)
    }
  }

  async spawn(config: ContainerSpawnConfig): Promise<ContainerHandle> {
    const args: string[] = ['run', '--rm', '--name', config.name];

    if (config.user) {
      args.push('--user', config.user);
    }

    for (const [key, value] of Object.entries(config.env)) {
      args.push('-e', `${key}=${value}`);
    }

    for (const mount of config.mounts) {
      if (mount.readonly) {
        args.push(...readonlyMountArgs(mount.hostPath, mount.containerPath));
      } else {
        args.push('-v', `${mount.hostPath}:${mount.containerPath}`);
      }
    }

    for (const mount of config.secretMounts || []) {
      args.push(...readonlyMountArgs(mount.hostPath, mount.containerPath));
    }

    args.push(config.image);

    const proc = spawn(this.cliBin, args, {
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    if (config.onStdoutChunk) {
      proc.stdout.on('data', (data) => config.onStdoutChunk?.(data.toString()));
    }
    if (config.onStderrChunk) {
      proc.stderr.on('data', (data) => config.onStderrChunk?.(data.toString()));
    }

    const waitPromise = new Promise<{ code: number | null }>(
      (resolve, reject) => {
        let settled = false;
        proc.once('error', (err) => {
          if (settled) return;
          settled = true;
          reject(err);
        });
        proc.once('close', (code) => {
          if (settled) return;
          settled = true;
          resolve({ code });
        });
      },
    );

    return new DockerContainerHandle(config.name, waitPromise, this.cliBin);
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isK8sStatusCode(err: unknown, code: number): boolean {
  if (!err || typeof err !== 'object') return false;
  const maybeErr = err as {
    statusCode?: number;
    body?: { code?: number };
    response?: { statusCode?: number };
  };
  return (
    maybeErr.statusCode === code ||
    maybeErr.body?.code === code ||
    maybeErr.response?.statusCode === code
  );
}

function sanitizePodName(name: string): string {
  const lower = name.toLowerCase();
  const cleaned = lower.replace(/[^a-z0-9-]/g, '-').replace(/-+/g, '-');
  const trimmed = cleaned.replace(/^-+/, '').replace(/-+$/, '');
  const base = trimmed || 'devbox-runner';
  if (base.length <= 63) return base;

  const tail = base.slice(-16).replace(/^-+/, '');
  const headBudget = Math.max(1, 63 - tail.length - 1);
  const head = base.slice(0, headBudget).replace(/-+$/, '');
  return `${head}-${tail}`.slice(0, 63).replace(/-+$/, '');
}

function parseUserSecurityContext(
  user: string | undefined,
): k8s.V1SecurityContext | undefined {
  if (!user) return undefined;
  const match = user.match(/^(\d+)(?::(\d+))?$/);
  if (!match) return undefined;

  const runAsUser = Number.parseInt(match[1], 10);
  const runAsGroup = match[2] ? Number.parseInt(match[2], 10) : undefined;
  if (!Number.isFinite(runAsUser)) return undefined;

  return {
    runAsUser,
    ...(Number.isFinite(runAsGroup) ? { runAsGroup } : {}),
  };
}

function makeCoreV1Api(kubeconfigPath?: string): k8s.CoreV1Api {
  const kubeConfig = new k8s.KubeConfig();
  if (kubeconfigPath) {
    const resolvedPath = kubeconfigPath.startsWith('~/')
      ? path.join(process.env.HOME || '', kubeconfigPath.slice(2))
      : path.resolve(kubeconfigPath);
    kubeConfig.loadFromFile(resolvedPath);
  } else {
    kubeConfig.loadFromDefault();
  }
  return kubeConfig.makeApiClient(k8s.CoreV1Api);
}

class K8sContainerHandle implements ContainerHandle {
  constructor(
    public readonly id: string,
    private readonly coreApi: k8s.CoreV1Api,
    private readonly namespace: string,
  ) {}

  async waitForExit(): Promise<{ code: number | null }> {
    for (;;) {
      let pod: k8s.V1Pod;
      try {
        pod = await this.coreApi.readNamespacedPod({
          name: this.id,
          namespace: this.namespace,
        });
      } catch (err) {
        if (isK8sStatusCode(err, 404)) {
          return { code: null };
        }
        throw err;
      }

      const phase = pod.status?.phase;
      if (phase === 'Succeeded') {
        return { code: 0 };
      }

      if (phase === 'Failed') {
        const terminatedState = pod.status?.containerStatuses?.find(
          (status) => status.name === 'runner',
        )?.state?.terminated;
        return { code: terminatedState?.exitCode ?? 1 };
      }

      await sleep(1000);
    }
  }

  async stop(): Promise<void> {
    try {
      await this.coreApi.deleteNamespacedPod({
        name: this.id,
        namespace: this.namespace,
        gracePeriodSeconds: 10,
        propagationPolicy: 'Background',
      });
    } catch (err) {
      if (isK8sStatusCode(err, 404)) return;
      logger.warn({ err, pod: this.id }, 'Failed to delete runner pod');
    }
  }
}

export class K8sRuntime implements ContainerRuntime {
  static readonly RUNNER_LABEL_KEY = 'devbox-runner';
  static readonly RUNNER_LABEL_VALUE = 'true';

  constructor(
    private readonly coreApi: k8s.CoreV1Api,
    private readonly runtimeConfig: KubernetesRuntimeConfig = KUBERNETES_RUNTIME,
  ) {}

  static fromConfig(
    runtimeConfig: KubernetesRuntimeConfig = KUBERNETES_RUNTIME,
  ): K8sRuntime {
    return new K8sRuntime(
      makeCoreV1Api(runtimeConfig.kubeconfig),
      runtimeConfig,
    );
  }

  private hostPathToSubPath(hostPath: string): string | undefined {
    const resolvedHostPath = path.resolve(hostPath);
    const resolvedDataRoot = path.resolve(this.runtimeConfig.dataMountPath);
    const relative = path.relative(resolvedDataRoot, resolvedHostPath);

    if (relative.startsWith('..') || path.isAbsolute(relative)) {
      throw new Error(
        `Mount path "${resolvedHostPath}" is outside kubernetes.data_mount_path "${resolvedDataRoot}"`,
      );
    }

    if (!relative || relative === '.') return undefined;
    return relative.split(path.sep).join(path.posix.sep);
  }

  async ensureRunning(): Promise<void> {
    try {
      await this.coreApi.listNamespacedPod({
        namespace: this.runtimeConfig.namespace,
        limit: 1,
      });
      logger.debug(
        { namespace: this.runtimeConfig.namespace },
        'Kubernetes runtime reachable',
      );
    } catch (err) {
      logger.error(
        { err, namespace: this.runtimeConfig.namespace },
        'Failed to reach Kubernetes API',
      );
      throw new Error('Kubernetes runtime is required but failed to start');
    }
  }

  async cleanupOrphans(): Promise<void> {
    try {
      const pods = await this.coreApi.listNamespacedPod({
        namespace: this.runtimeConfig.namespace,
        labelSelector: `${K8sRuntime.RUNNER_LABEL_KEY}=${K8sRuntime.RUNNER_LABEL_VALUE}`,
      });

      const stalePods = pods.items || [];
      for (const pod of stalePods) {
        const name = pod.metadata?.name;
        if (!name) continue;
        try {
          await this.coreApi.deleteNamespacedPod({
            name,
            namespace: this.runtimeConfig.namespace,
            gracePeriodSeconds: 5,
            propagationPolicy: 'Background',
          });
        } catch (err) {
          if (!isK8sStatusCode(err, 404)) {
            logger.warn({ err, pod: name }, 'Failed to clean up orphan pod');
          }
        }
      }

      if (stalePods.length > 0) {
        logger.info(
          { count: stalePods.length, namespace: this.runtimeConfig.namespace },
          'Deleted orphaned runner pods',
        );
      }
    } catch (err) {
      logger.warn({ err }, 'Failed to clean up orphaned pods');
    }
  }

  async stopContainer(id: string): Promise<void> {
    try {
      await this.coreApi.deleteNamespacedPod({
        name: id,
        namespace: this.runtimeConfig.namespace,
        gracePeriodSeconds: 10,
        propagationPolicy: 'Background',
      });
    } catch (err) {
      if (isK8sStatusCode(err, 404)) return;
      logger.warn({ err, pod: id }, 'Failed to delete runner pod');
    }
  }

  async spawn(config: ContainerSpawnConfig): Promise<ContainerHandle> {
    const podName = sanitizePodName(config.name);
    const securityContext = parseUserSecurityContext(config.user);

    const pvcVolumeName = 'data';
    const volumeMounts: k8s.V1VolumeMount[] = [];

    for (const mount of config.mounts) {
      const subPath = this.hostPathToSubPath(mount.hostPath);

      volumeMounts.push({
        name: pvcVolumeName,
        mountPath: mount.containerPath,
        readOnly: mount.readonly || undefined,
        ...(subPath ? { subPath } : {}),
      });
    }

    for (const [index, mount] of (config.secretMounts || []).entries()) {
      volumeMounts.push({
        name: `secret-mount-${index}`,
        mountPath: mount.containerPath,
        readOnly: true,
      });
    }

    const volumes: k8s.V1Volume[] = [
      {
        name: pvcVolumeName,
        persistentVolumeClaim: {
          claimName: this.runtimeConfig.pvcName,
        },
      },
      ...(config.secretMounts || []).map((mount, index) => ({
        name: `secret-mount-${index}`,
        secret: {
          secretName: mount.secretName,
        },
      })),
    ];

    // No init container needed — the controller pre-creates all PVC
    // directories with uid 1000 ownership via mkdirOwned/writeFileOwned
    // in container-runner.ts, so the runner can write immediately.

    const podSpec: k8s.V1Pod = {
      apiVersion: 'v1',
      kind: 'Pod',
      metadata: {
        name: podName,
        labels: {
          [K8sRuntime.RUNNER_LABEL_KEY]: K8sRuntime.RUNNER_LABEL_VALUE,
        },
      },
      spec: {
        restartPolicy: 'Never',
        serviceAccountName: this.runtimeConfig.serviceAccount,
        containers: [
          {
            name: 'runner',
            image: config.image,
            imagePullPolicy: this.runtimeConfig.imagePullPolicy,
            env: Object.entries(config.env).map(([name, value]) => ({
              name,
              value,
            })),
            volumeMounts,
            resources: {
              requests: {
                cpu: this.runtimeConfig.runnerResources.cpu,
                memory: this.runtimeConfig.runnerResources.memory,
                'ephemeral-storage':
                  this.runtimeConfig.runnerResources.ephemeralStorage,
              },
              limits: {
                cpu: this.runtimeConfig.runnerResources.cpu,
                memory: this.runtimeConfig.runnerResources.memory,
                'ephemeral-storage':
                  this.runtimeConfig.runnerResources.ephemeralStorage,
              },
            },
            ...(securityContext ? { securityContext } : {}),
          },
        ],
        volumes,
      },
    };

    await this.coreApi.createNamespacedPod({
      namespace: this.runtimeConfig.namespace,
      body: podSpec,
    });

    return new K8sContainerHandle(
      podName,
      this.coreApi,
      this.runtimeConfig.namespace,
    );
  }
}

export function createContainerRuntime(): ContainerRuntime {
  if (CONTAINER_RUNTIME === 'docker') {
    return new DockerRuntime();
  }
  if (CONTAINER_RUNTIME === 'kubernetes') {
    return K8sRuntime.fromConfig();
  }

  throw new Error(`Unsupported container runtime "${CONTAINER_RUNTIME}"`);
}
