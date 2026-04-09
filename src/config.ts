import fs from 'fs';
import path from 'path';

import { z } from 'zod';
import YAML from 'yaml';

import { RegisteredAgent } from './types.js';

// --- Zod schema for config.yaml ---

const ContainerSchema = z.object({
  runtime: z.enum(['docker', 'kubernetes']).default('docker'),
  image: z.string().default('devbox-runner:latest'),
  timeout: z.number().int().positive().default(5400000),
  idle_timeout: z.number().int().positive().default(300000),
  max_concurrent: z.number().int().positive().default(2),
  max_output_size: z.number().int().positive().default(10485760),
  kubernetes: z
    .object({
      namespace: z.string().min(1).default('devbox-agent'),
      kubeconfig: z.string().optional(),
      pvc_name: z.string().min(1).default('devbox-data'),
      data_mount_path: z.string().min(1).default('/data/devbox-agent'),
      service_account: z.string().min(1).default('devbox-runner'),
      image_pull_policy: z
        .enum(['Always', 'IfNotPresent', 'Never'])
        .default('IfNotPresent'),
      runner_resources: z
        .object({
          cpu: z.string().default('2'),
          memory: z.string().default('4Gi'),
          ephemeral_storage: z.string().default('10Gi'),
        })
        .default({
          cpu: '2',
          memory: '4Gi',
          ephemeral_storage: '10Gi',
        }),
    })
    .default({
      namespace: 'devbox-agent',
      pvc_name: 'devbox-data',
      data_mount_path: '/data/devbox-agent',
      service_account: 'devbox-runner',
      image_pull_policy: 'IfNotPresent',
      runner_resources: {
        cpu: '2',
        memory: '4Gi',
        ephemeral_storage: '10Gi',
      },
    }),
});

const RepoSchema = z.object({
  name: z.string(),
  source: z.string(),
  ref: z.string().optional(),
});

const WorkspaceSchema = z.object({
  repos: z.array(RepoSchema).optional().default([]),
});

const LegacyGroupSchema = z.object({
  jid: z.string(),
  name: z.string(),
  folder: z.string(),
  requires_trigger: z.boolean().default(true),
});

const AgentDefinitionSchema = z.object({
  name: z.string(),
  path: z.string(),
});

const ChannelAgentBindingSchema = z.object({
  name: z.string(),
  trigger: z.string().optional(),
  requires_trigger: z.boolean().optional(),
});

const ChannelSchema = z.object({
  id: z.string(),
  agents: z.array(ChannelAgentBindingSchema).min(1),
});

const WebSchema = z
  .object({
    enabled: z.boolean().default(false),
    port: z.number().int().positive().default(8080),
  })
  .optional();

const ConfigSchema = z.object({
  assistant_name: z.string().default('Devbox'),
  telegram_bot_token: z.string().optional(),
  slack_bot_token: z.string().optional(),
  slack_app_token: z.string().optional(),
  trigger_pattern: z.string().optional(),
  timezone: z.string().optional(),
  data_root: z.string().optional(),
  container: ContainerSchema.optional().default({
    runtime: 'docker',
    image: 'devbox-runner:latest',
    timeout: 5400000,
    idle_timeout: 300000,
    max_concurrent: 2,
    max_output_size: 10485760,
    kubernetes: {
      namespace: 'devbox-agent',
      pvc_name: 'devbox-data',
      data_mount_path: '/data/devbox-agent',
      service_account: 'devbox-runner',
      image_pull_policy: 'IfNotPresent',
      runner_resources: {
        cpu: '2',
        memory: '4Gi',
        ephemeral_storage: '10Gi',
      },
    },
  }),
  workspace: WorkspaceSchema.optional(),
  groups: z.array(LegacyGroupSchema).optional(),
  agents: z.array(AgentDefinitionSchema).optional(),
  channels: z.array(ChannelSchema).optional(),
  web: WebSchema,
});

type Config = z.infer<typeof ConfigSchema>;

// --- Hardcoded constants (never change from config) ---

export const POLL_INTERVAL = 2000;
export const SCHEDULER_POLL_INTERVAL = 60000;
export const IPC_POLL_INTERVAL = 1000;

// --- Mutable config values (set by loadConfig) ---

// App root: location of checked-in source/bundled runtime files.
// Works in dev (`src/`) and dist (`dist/`) layouts.
export const APP_ROOT = path.resolve(import.meta.dirname, '..');

export let ASSISTANT_NAME = 'Devbox';
export let TELEGRAM_BOT_TOKEN = '';
export let SLACK_BOT_TOKEN = '';
export let SLACK_APP_TOKEN = '';
export let TRIGGER_PATTERN = new RegExp(`^@Devbox\\b`, 'i');
export let TIMEZONE =
  process.env.TZ || Intl.DateTimeFormat().resolvedOptions().timeZone;

// Runtime data root can be configured independently from APP_ROOT.
export let DATA_ROOT = path.resolve(
  process.env.DEVBOX_DATA_ROOT || process.cwd(),
);
export let STORE_DIR = path.resolve(DATA_ROOT, 'store');
export let AGENTS_DIR = path.resolve(DATA_ROOT, 'agents');
export let DATA_DIR = path.resolve(DATA_ROOT, 'data');

export let CONTAINER_IMAGE = 'devbox-runner:latest';
export let CONTAINER_RUNTIME: 'docker' | 'kubernetes' = 'docker';
export let CONTAINER_TIMEOUT = 5400000;
export let CONTAINER_MAX_OUTPUT_SIZE = 10485760;
export let IDLE_TIMEOUT = 300000;
export let MAX_CONCURRENT_CONTAINERS = 2;
export let WEB_ENABLED = false;
export let WEB_PORT = 8080;
export interface RunnerResources {
  cpu: string;
  memory: string;
  ephemeralStorage: string;
}
export interface KubernetesRuntimeConfig {
  namespace: string;
  kubeconfig?: string;
  pvcName: string;
  dataMountPath: string;
  serviceAccount: string;
  imagePullPolicy: 'Always' | 'IfNotPresent' | 'Never';
  runnerResources: RunnerResources;
}
const DEFAULT_RUNNER_RESOURCES: RunnerResources = {
  cpu: '2',
  memory: '4Gi',
  ephemeralStorage: '10Gi',
};
export let KUBERNETES_RUNTIME: KubernetesRuntimeConfig = {
  namespace: 'devbox-agent',
  pvcName: 'devbox-data',
  dataMountPath: '/data/devbox-agent',
  serviceAccount: 'devbox-runner',
  imagePullPolicy: 'IfNotPresent',
  runnerResources: { ...DEFAULT_RUNNER_RESOURCES },
};

export interface WorkspaceRepo {
  name: string;
  source: string;
  ref?: string;
}

export let WORKSPACE_REPOS: WorkspaceRepo[] = [];

// --- Internal state ---

let parsedRegisteredAgents: Record<string, RegisteredAgent> = {};
let parsedAgentPaths: Record<string, string> = {};

// --- Helpers ---

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function isTelegramDmChannelId(channelId: string): boolean {
  return channelId.startsWith('tg:user:');
}

function hasChannelPrefix(
  agents: Record<string, RegisteredAgent>,
  prefix: string,
): boolean {
  return Object.keys(agents).some((id) => id.startsWith(prefix));
}

function setDataRoot(root: string): void {
  DATA_ROOT = path.resolve(root);
  STORE_DIR = path.resolve(DATA_ROOT, 'store');
  AGENTS_DIR = path.resolve(DATA_ROOT, 'agents');
  DATA_DIR = path.resolve(DATA_ROOT, 'data');
}

function normalizeWorkspaceRepos(
  workspace: Config['workspace'],
): WorkspaceRepo[] {
  const repos: WorkspaceRepo[] = [];
  const seen = new Set<string>();

  const configuredRepos = workspace?.repos || [];
  for (const repo of configuredRepos) {
    const key = `${repo.name}::${repo.source}::${repo.ref || ''}`;
    if (seen.has(key)) continue;
    seen.add(key);
    repos.push(repo);
  }

  return repos;
}

function resolveConfiguredAgentPath(
  configDir: string,
  configuredPath: string,
): string {
  if (path.isAbsolute(configuredPath)) return configuredPath;
  const fromConfigDir = path.resolve(configDir, configuredPath);
  if (fs.existsSync(fromConfigDir)) return fromConfigDir;
  return path.resolve(APP_ROOT, configuredPath);
}

function buildFromLegacyGroups(config: Config): {
  registeredAgents: Record<string, RegisteredAgent>;
  agentPaths: Record<string, string>;
} {
  const groups = config.groups || [];
  if (groups.length === 0) {
    throw new Error(
      'Invalid config: must provide either channels/agents or legacy groups',
    );
  }

  console.warn(
    '[config] Deprecated "groups" format detected. Please migrate to "agents" + "channels".',
  );

  const now = new Date().toISOString();
  const registeredAgents: Record<string, RegisteredAgent> = {};
  const agentPaths: Record<string, string> = {};

  for (const g of groups) {
    registeredAgents[g.jid] = {
      name: g.name,
      agentName: g.folder,
      trigger: `@${ASSISTANT_NAME}`,
      added_at: now,
      requiresTrigger: g.requires_trigger,
    };

    if (!agentPaths[g.folder]) {
      agentPaths[g.folder] = path.resolve(APP_ROOT, 'agents', g.folder);
    }
  }

  return { registeredAgents, agentPaths };
}

function buildFromChannels(
  config: Config,
  configPath: string,
): {
  registeredAgents: Record<string, RegisteredAgent>;
  agentPaths: Record<string, string>;
} {
  if (!config.channels || config.channels.length === 0) {
    throw new Error('Invalid config: channels is required when using agents');
  }
  if (!config.agents || config.agents.length === 0) {
    throw new Error('Invalid config: agents is required when using channels');
  }

  const configDir = path.dirname(path.resolve(configPath));
  const definitions = new Map<string, string>();
  for (const agent of config.agents) {
    if (definitions.has(agent.name)) {
      throw new Error(`Invalid config: duplicate agent name "${agent.name}"`);
    }
    definitions.set(
      agent.name,
      resolveConfiguredAgentPath(configDir, agent.path),
    );
  }

  const now = new Date().toISOString();
  const registeredAgents: Record<string, RegisteredAgent> = {};

  for (const channel of config.channels) {
    if (channel.agents.length > 1) {
      console.warn(
        `[config] channel ${channel.id} has multiple agents configured; Phase 0 uses the first binding only`,
      );
    }
    const binding = channel.agents[0];
    if (!definitions.has(binding.name)) {
      throw new Error(
        `Invalid config: channel ${channel.id} references unknown agent "${binding.name}"`,
      );
    }

    registeredAgents[channel.id] = {
      name: binding.name,
      agentName: binding.name,
      trigger: binding.trigger || `@${ASSISTANT_NAME}`,
      added_at: now,
      requiresTrigger:
        binding.requires_trigger === undefined
          ? !isTelegramDmChannelId(channel.id)
          : binding.requires_trigger,
    };
  }

  return {
    registeredAgents,
    agentPaths: Object.fromEntries(definitions.entries()),
  };
}

// --- Public API ---

export function loadConfig(configPath: string): void {
  const raw = fs.readFileSync(configPath, 'utf-8');
  const parsed = YAML.parse(raw);
  const result = ConfigSchema.safeParse(parsed);
  if (!result.success) {
    const issues = result.error.issues
      .map((i) => `  - ${i.path.join('.')}: ${i.message}`)
      .join('\n');
    throw new Error(`Invalid config ${configPath}:\n${issues}`);
  }
  const config = result.data;

  const configuredDataRoot =
    process.env.DEVBOX_DATA_ROOT || config.data_root || DATA_ROOT;
  setDataRoot(configuredDataRoot);

  ASSISTANT_NAME = config.assistant_name;
  TELEGRAM_BOT_TOKEN =
    process.env.TELEGRAM_BOT_TOKEN || config.telegram_bot_token || '';
  SLACK_BOT_TOKEN = process.env.SLACK_BOT_TOKEN || config.slack_bot_token || '';
  SLACK_APP_TOKEN = process.env.SLACK_APP_TOKEN || config.slack_app_token || '';

  const triggerSrc =
    config.trigger_pattern || `^@${escapeRegex(ASSISTANT_NAME)}\\b`;
  TRIGGER_PATTERN = new RegExp(triggerSrc, 'i');

  if (config.timezone) {
    TIMEZONE = config.timezone;
  }

  CONTAINER_RUNTIME = config.container.runtime;
  CONTAINER_IMAGE = config.container.image;
  CONTAINER_TIMEOUT = config.container.timeout;
  IDLE_TIMEOUT = config.container.idle_timeout;
  MAX_CONCURRENT_CONTAINERS = config.container.max_concurrent;
  CONTAINER_MAX_OUTPUT_SIZE = config.container.max_output_size;
  const k8s = config.container.kubernetes;
  const res = k8s.runner_resources;
  KUBERNETES_RUNTIME = {
    namespace: k8s.namespace,
    kubeconfig: k8s.kubeconfig,
    pvcName: k8s.pvc_name,
    dataMountPath: path.resolve(k8s.data_mount_path),
    serviceAccount: k8s.service_account,
    imagePullPolicy: k8s.image_pull_policy,
    runnerResources: {
      cpu: res?.cpu ?? DEFAULT_RUNNER_RESOURCES.cpu,
      memory: res?.memory ?? DEFAULT_RUNNER_RESOURCES.memory,
      ephemeralStorage:
        res?.ephemeral_storage ?? DEFAULT_RUNNER_RESOURCES.ephemeralStorage,
    },
  };

  WORKSPACE_REPOS = normalizeWorkspaceRepos(config.workspace);

  WEB_ENABLED = config.web?.enabled ?? false;
  WEB_PORT = config.web?.port ?? 8080;

  const hasNewConfig = Boolean(config.agents && config.channels);
  const hasLegacyConfig = Boolean(config.groups && config.groups.length > 0);

  if (hasNewConfig) {
    const mapped = buildFromChannels(config, configPath);
    parsedRegisteredAgents = mapped.registeredAgents;
    parsedAgentPaths = mapped.agentPaths;
  } else if (hasLegacyConfig) {
    const mapped = buildFromLegacyGroups(config);
    parsedRegisteredAgents = mapped.registeredAgents;
    parsedAgentPaths = mapped.agentPaths;
  } else {
    throw new Error(
      'Invalid config: expected either legacy groups or agents/channels sections',
    );
  }

  const needsTelegram = hasChannelPrefix(parsedRegisteredAgents, 'tg:');
  if (needsTelegram && !TELEGRAM_BOT_TOKEN) {
    throw new Error(
      'Missing telegram bot token: set TELEGRAM_BOT_TOKEN env var or telegram_bot_token in config',
    );
  }

  const needsSlack = hasChannelPrefix(parsedRegisteredAgents, 'slack:');
  if (needsSlack && (!SLACK_BOT_TOKEN || !SLACK_APP_TOKEN)) {
    throw new Error(
      'Missing Slack credentials: set SLACK_BOT_TOKEN + SLACK_APP_TOKEN env vars or slack_bot_token + slack_app_token in config',
    );
  }
}

export function getRegisteredAgents(): Record<string, RegisteredAgent> {
  return { ...parsedRegisteredAgents };
}

export function getAgentPath(agentName: string): string {
  return (
    parsedAgentPaths[agentName] || path.resolve(APP_ROOT, 'agents', agentName)
  );
}

export function getAllAgentPaths(): Record<string, string> {
  return { ...parsedAgentPaths };
}
