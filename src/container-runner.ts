/**
 * Container Runner for Devbox Agent
 * Spawns agent execution in containers and handles IPC
 */
import { createSign } from 'crypto';
import fs from 'fs';
import os from 'os';
import path from 'path';
import YAML from 'yaml';

import {
  AGENTS_DIR,
  APP_ROOT,
  CONTAINER_IMAGE,
  CONTAINER_MAX_OUTPUT_SIZE,
  CONTAINER_RUNTIME,
  CONTAINER_TIMEOUT,
  IDLE_TIMEOUT,
  TIMEZONE,
  WORKSPACE_REPOS,
  getAgentPath,
} from './config.js';
import {
  resolveSessionClaudePath,
  resolveSessionIpcPath,
  resolveSessionPath,
  resolveSessionWorkspacePath,
} from './agent-folder.js';
import { logger } from './logger.js';
import {
  ContainerRuntime,
  RuntimeMount,
  RuntimeSecretMount,
} from './container-runtime.js';
import { touchSessionHeartbeat } from './session-gc.js';
import { RegisteredAgent } from './types.js';

const GITHUB_SEED_TOKEN_SECRET = 'DEVBOX_GIT_AUTH_TOKEN';
const GITHUB_SEED_TOKENS_SECRET = 'DEVBOX_GIT_AUTH_TOKENS';

interface GitHubAccessTokenResponse {
  token?: string;
  expires_at?: string;
}

interface GitHubTokenCache {
  token: string;
  expiresAtMs: number;
}

const githubTokenCache = new Map<string, GitHubTokenCache>();

export interface ThinkingConfig {
  type: 'adaptive' | 'enabled' | 'disabled';
  budgetTokens?: number;
}

export interface ContainerInput {
  prompt: string;
  sessionKey: string;
  sessionId?: string;
  agentName: string;
  chatJid: string;
  threadId?: string | null;
  isScheduledTask?: boolean;
  assistantName?: string;
  model?: string;
  thinking?: ThinkingConfig;
  effort?: 'low' | 'medium' | 'high' | 'max';
  secrets?: Record<string, string>;
}

export interface ContainerOutput {
  status: 'success' | 'error';
  result: string | null;
  newSessionId?: string;
  error?: string;
  errorKind?: 'stale_session_resume' | 'seed_clone_failed';
}

interface SeedManifestRepo {
  name: string;
  source: string;
  ref?: string;
}

interface SeedSecretMount {
  secretName: string;
  hostPath: string;
  mountPath: string;
}

interface AgentSeedDefinition {
  baseDir: string | null;
  image?: string;
  model?: string;
  thinking?: ThinkingConfig;
  effort?: 'low' | 'medium' | 'high' | 'max';
  repos: SeedManifestRepo[];
  secretMounts: SeedSecretMount[];
}

function isRemoteRepoSource(source: string): boolean {
  return /^(?:https?:\/\/|ssh:\/\/|git@|git:\/\/)/i.test(source);
}

function isGitHubRepoSource(source: string): boolean {
  return /^(?:git@github\.com:|ssh:\/\/git@github\.com\/|https?:\/\/github\.com\/)/.test(
    source,
  );
}

function extractGitHubOwner(source: string): string | null {
  const trimmed = source.trim();
  const match = trimmed.match(
    /^(?:git@github\.com:|ssh:\/\/git@github\.com\/|https?:\/\/github\.com\/)([^/]+)\//,
  );
  return match?.[1]?.toLowerCase() || null;
}

function workspaceGitHubOwners(repos: SeedManifestRepo[]): string[] {
  const owners = new Set<string>();
  for (const repo of repos) {
    const source = repo.source.trim();
    if (!isGitHubRepoSource(source)) continue;
    const owner = extractGitHubOwner(source);
    if (owner) owners.add(owner);
  }
  return [...owners];
}

// UID/GID of the devbox user inside runner containers.
const RUNNER_UID = 1000;
const RUNNER_GID = 1000;
const CONTAINER_HOME = '/workspace/.home';

// ---------------------------------------------------------------------------
// Owned file helpers — create files/dirs as uid 1000 (devbox) even when the
// controller process runs as root.  When the controller is NOT root (local
// dev / Docker Compose) the chown calls are skipped.
// ---------------------------------------------------------------------------
const IS_ROOT = process.getuid?.() === 0;

function chownIfRoot(p: string): void {
  if (IS_ROOT) fs.chownSync(p, RUNNER_UID, RUNNER_GID);
}

function mkdirOwned(dirPath: string): void {
  fs.mkdirSync(dirPath, { recursive: true });
  chownIfRoot(dirPath);
}

function writeFileOwned(filePath: string, data: string): void {
  fs.writeFileSync(filePath, data);
  chownIfRoot(filePath);
}

function cpOwned(src: string, dst: string): void {
  fs.cpSync(src, dst, { recursive: true });
  if (!IS_ROOT) return;
  // Recursively chown the copied tree — only used for small dirs (skills).
  const chownR = (p: string) => {
    fs.chownSync(p, RUNNER_UID, RUNNER_GID);
    if (fs.statSync(p).isDirectory()) {
      for (const entry of fs.readdirSync(p)) {
        chownR(path.join(p, entry));
      }
    }
  };
  chownR(dst);
}

function copyFileIfMissing(src: string, dst: string): void {
  if (!fs.existsSync(src) || fs.existsSync(dst)) return;
  mkdirOwned(path.dirname(dst));
  fs.copyFileSync(src, dst);
  chownIfRoot(dst);
}

function parseThinkingConfig(raw: unknown): ThinkingConfig | undefined {
  if (!raw || typeof raw !== 'object') return undefined;
  const obj = raw as Record<string, unknown>;

  if (obj.type === 'adaptive') {
    return { type: 'adaptive' };
  } else if (obj.type === 'enabled') {
    const budgetTokens =
      typeof obj.budgetTokens === 'number' ? obj.budgetTokens : undefined;
    return { type: 'enabled', ...(budgetTokens ? { budgetTokens } : {}) };
  } else if (obj.type === 'disabled') {
    return { type: 'disabled' };
  }
  return undefined;
}

function validateEffort(
  raw: unknown,
): 'low' | 'medium' | 'high' | 'max' | undefined {
  if (typeof raw !== 'string') return undefined;
  const normalized = raw.trim().toLowerCase();
  if (
    normalized === 'low' ||
    normalized === 'medium' ||
    normalized === 'high' ||
    normalized === 'max'
  ) {
    return normalized;
  }
  return undefined;
}

function readSeedDefinition(agentName: string): AgentSeedDefinition {
  const seedPath = path.join(getAgentPath(agentName), 'seed.yaml');
  if (fs.existsSync(seedPath)) {
    try {
      const parsed = YAML.parse(fs.readFileSync(seedPath, 'utf-8')) as {
        image?: string;
        model?: string;
        thinking?: unknown;
        effort?: string;
        repos?: Array<{ name?: string; source?: string; ref?: string }>;
        secretMounts?: Array<{
          secretName?: string;
          mountPath?: string;
          hostPath?: string;
        }>;
      };
      const repos = (parsed.repos || [])
        .filter(
          (r): r is { name: string; source: string; ref?: string } =>
            !!r && typeof r.name === 'string' && typeof r.source === 'string',
        )
        .map((r) => ({
          name: r.name,
          source: r.source,
          ...(r.ref ? { ref: r.ref } : {}),
        }));
      const secretMounts = (parsed.secretMounts || [])
        .filter(
          (
            mount,
          ): mount is {
            secretName: string;
            mountPath: string;
            hostPath: string;
          } =>
            !!mount &&
            typeof mount.secretName === 'string' &&
            typeof mount.mountPath === 'string' &&
            typeof mount.hostPath === 'string',
        )
        .map((mount) => ({
          secretName: mount.secretName.trim(),
          mountPath: mount.mountPath.trim(),
          hostPath: mount.hostPath.trim(),
        }))
        .filter(
          (mount) =>
            mount.secretName.length > 0 &&
            mount.mountPath.length > 0 &&
            mount.hostPath.length > 0,
        );
      return {
        baseDir: path.dirname(seedPath),
        image:
          typeof parsed.image === 'string' && parsed.image.trim()
            ? parsed.image.trim()
            : undefined,
        model:
          typeof parsed.model === 'string' && parsed.model.trim()
            ? parsed.model.trim()
            : undefined,
        thinking: parseThinkingConfig(parsed.thinking),
        effort: validateEffort(parsed.effort),
        repos,
        secretMounts,
      };
    } catch (err) {
      logger.warn(
        { agentName, seedPath, err },
        'Failed to parse agent seed.yaml; falling back to workspace.repos',
      );
    }
  }

  return {
    baseDir: null,
    repos: WORKSPACE_REPOS.map((repo) => ({
      name: repo.name,
      source: repo.source,
      ...(repo.ref ? { ref: repo.ref } : {}),
    })),
    secretMounts: [],
  };
}

function syncInstructionFile(
  filename: 'CLAUDE.md' | 'AGENTS.md',
  sessionDir: string,
  workspaceDir: string,
  agentName: string,
): void {
  const imageInstruction = path.join(getAgentPath(agentName), filename);
  const legacyInstruction = path.join(APP_ROOT, 'groups', agentName, filename);
  const sessionInstruction = path.join(sessionDir, filename);
  const workspaceInstruction = path.join(workspaceDir, filename);

  copyFileIfMissing(imageInstruction, sessionInstruction);
  copyFileIfMissing(legacyInstruction, sessionInstruction);
  copyFileIfMissing(sessionInstruction, workspaceInstruction);
}

function syncStaticSessionConfig(
  sessionDir: string,
  workspaceDir: string,
  agentName: string,
): void {
  syncInstructionFile('CLAUDE.md', sessionDir, workspaceDir, agentName);
  syncInstructionFile('AGENTS.md', sessionDir, workspaceDir, agentName);

  const imageGlobalClaude = path.join(
    APP_ROOT,
    'groups',
    'global',
    'CLAUDE.md',
  );
  const dataGlobalClaude = path.join(AGENTS_DIR, 'global', 'CLAUDE.md');
  copyFileIfMissing(imageGlobalClaude, dataGlobalClaude);
}

function buildSeedManifest(
  definition: AgentSeedDefinition,
  sessionDir: string,
): SeedManifestRepo[] {
  const repos: SeedManifestRepo[] = [];

  for (const repo of definition.repos) {
    const source = repo.source.trim();
    if (!source) continue;

    if (!isRemoteRepoSource(source)) {
      const seedSource = definition.baseDir
        ? path.join(definition.baseDir, 'seed.yaml')
        : 'workspace.repos';
      throw new Error(
        `Local repo source is not supported for seeding: "${source}" ` +
          `(repo "${repo.name}" in ${seedSource}). ` +
          'Use a remote git source (https://, ssh://, git@, git://).',
      );
    }

    repos.push({
      name: repo.name,
      source,
      ...(repo.ref ? { ref: repo.ref } : {}),
    });
  }

  const manifestPath = path.join(sessionDir, 'seed-manifest.json');
  writeFileOwned(manifestPath, `${JSON.stringify({ repos }, null, 2)}\n`);
  return repos;
}

function buildVolumeMounts(
  agent: RegisteredAgent,
  sessionKey: string,
): {
  mounts: RuntimeMount[];
  secretMounts: RuntimeSecretMount[];
  seedRepos: SeedManifestRepo[];
  containerImage?: string;
  model?: string;
  thinking?: ThinkingConfig;
  effort?: 'low' | 'medium' | 'high' | 'max';
} {
  const bvmStart = Date.now();
  const bvmE = () => `${Date.now() - bvmStart}ms`;
  const mounts: RuntimeMount[] = [];
  const sessionDir = resolveSessionPath(agent.agentName, sessionKey);
  const sessionWorkspaceDir = resolveSessionWorkspacePath(
    agent.agentName,
    sessionKey,
  );
  const definition = readSeedDefinition(agent.agentName);
  mkdirOwned(sessionDir);
  mkdirOwned(sessionWorkspaceDir);
  logger.info({ agent: agent.name }, `[bvm ${bvmE()}] syncStaticSessionConfig`);
  syncStaticSessionConfig(sessionDir, sessionWorkspaceDir, agent.agentName);
  logger.info(
    { agent: agent.name },
    `[bvm ${bvmE()}] syncStaticSessionConfig done`,
  );

  mounts.push({
    hostPath: sessionDir,
    containerPath: '/session',
    readonly: true,
  });
  mounts.push({
    hostPath: sessionWorkspaceDir,
    containerPath: '/workspace',
    readonly: false,
  });
  mkdirOwned(path.join(sessionWorkspaceDir, '.home'));

  // Global instructions are shared and read-only.
  const globalDir = path.join(AGENTS_DIR, 'global');
  if (fs.existsSync(globalDir)) {
    mounts.push({
      hostPath: globalDir,
      containerPath: '/workspace/global',
      readonly: true,
    });
  }

  // Generic workspace seeding manifest consumed by container/entrypoint.sh.
  logger.info({ agent: agent.name }, `[bvm ${bvmE()}] buildSeedManifest`);
  const seedRepos = buildSeedManifest(definition, sessionDir);
  logger.info({ agent: agent.name }, `[bvm ${bvmE()}] buildSeedManifest done`);

  // Per-session Claude state (isolated from other channel/thread scopes).
  const sessionClaudeDir = resolveSessionClaudePath(
    agent.agentName,
    sessionKey,
  );
  mkdirOwned(sessionClaudeDir);
  const settingsFile = path.join(sessionClaudeDir, 'settings.json');
  if (!fs.existsSync(settingsFile)) {
    writeFileOwned(
      settingsFile,
      JSON.stringify(
        {
          env: {
            // Enable agent swarms (subagent orchestration)
            // https://code.claude.com/docs/en/agent-teams#orchestrate-teams-of-claude-code-sessions
            CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS: '1',
            // Load CLAUDE.md from additional mounted directories
            // https://code.claude.com/docs/en/memory#load-memory-from-additional-directories
            CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD: '1',
            // Enable Claude's memory feature (persists user preferences between sessions)
            // https://code.claude.com/docs/en/memory#manage-auto-memory
            CLAUDE_CODE_DISABLE_AUTO_MEMORY: '0',
          },
        },
        null,
        2,
      ) + '\n',
    );
  }

  // Sync skills from agent definition (preferred), then shared defaults.
  logger.info({ agent: agent.name }, `[bvm ${bvmE()}] syncing skills`);
  const skillsDst = path.join(sessionClaudeDir, 'skills');
  const agentSkillsSrc = path.join(getAgentPath(agent.agentName), 'skills');
  const sharedSkillsSrc = path.join(APP_ROOT, 'container', 'skills');
  const skillSources = [agentSkillsSrc, sharedSkillsSrc];
  mkdirOwned(skillsDst);
  for (const skillsSrc of skillSources) {
    if (!fs.existsSync(skillsSrc)) continue;
    for (const skillDir of fs.readdirSync(skillsSrc)) {
      const srcDir = path.join(skillsSrc, skillDir);
      if (!fs.statSync(srcDir).isDirectory()) continue;
      const dstDir = path.join(skillsDst, skillDir);
      cpOwned(srcDir, dstDir);
    }
  }
  logger.info({ agent: agent.name }, `[bvm ${bvmE()}] skills done`);
  mounts.push({
    hostPath: sessionClaudeDir,
    containerPath: `${CONTAINER_HOME}/.claude`,
    readonly: false,
  });

  // Per-session IPC namespace.
  logger.info({ agent: agent.name }, `[bvm ${bvmE()}] creating IPC dirs`);
  const sessionIpcDir = resolveSessionIpcPath(agent.agentName, sessionKey);
  mkdirOwned(path.join(sessionIpcDir, 'messages'));
  mkdirOwned(path.join(sessionIpcDir, 'tasks'));
  mkdirOwned(path.join(sessionIpcDir, 'input'));
  mounts.push({
    hostPath: sessionIpcDir,
    containerPath: '/ipc',
    readonly: false,
  });

  // Copy GCP Application Default Credentials into the session directory when
  // using Vertex AI. We copy instead of bind-mounting to avoid host file
  // permission issues (the devbox user inside the container may not be able
  // to read the host's ADC file). The session dir is already bind-mounted
  // with correct ownership.
  if (process.env.CLAUDE_CODE_USE_VERTEX) {
    const adcSrc =
      process.env.GOOGLE_APPLICATION_CREDENTIALS ||
      path.join(
        os.homedir(),
        '.config',
        'gcloud',
        'application_default_credentials.json',
      );
    if (fs.existsSync(adcSrc)) {
      const adcDst = path.join(sessionDir, 'gcloud-adc.json');
      fs.copyFileSync(adcSrc, adcDst);
      fs.chmodSync(adcDst, 0o644);
      logger.info({ adcSrc }, '[bvm] copied GCP ADC for Vertex AI');
    } else {
      logger.warn(
        { adcSrc },
        '[bvm] CLAUDE_CODE_USE_VERTEX is set but no ADC file found; Vertex auth may fail inside the container',
      );
    }
  }

  logger.info(
    { agent: agent.name },
    `[bvm ${bvmE()}] buildVolumeMounts complete`,
  );

  return {
    mounts,
    secretMounts: definition.secretMounts.map((mount) => ({
      secretName: mount.secretName,
      hostPath: mount.hostPath,
      containerPath: mount.mountPath,
    })),
    seedRepos,
    containerImage: definition.image,
    model: definition.model,
    thinking: definition.thinking,
    effort: definition.effort,
  };
}

/**
 * Read allowed secrets from process.env for passing to the container via stdin.
 * Secrets are never written to disk or mounted as files.
 */
function toBase64Url(input: Buffer | string): string {
  const base64 = Buffer.isBuffer(input)
    ? input.toString('base64')
    : Buffer.from(input).toString('base64');
  return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
}

function parseMultilineKey(value: string): string {
  return value.includes('\\n') ? value.replace(/\\n/g, '\n') : value;
}

function readGitHubAppPrivateKey(): string | undefined {
  const inline = process.env.GITHUB_APP_PRIVATE_KEY?.trim();
  if (inline) return parseMultilineKey(inline);

  const privateKeyPath = process.env.GITHUB_APP_PRIVATE_KEY_FILE?.trim();
  if (!privateKeyPath) return undefined;
  if (!fs.existsSync(privateKeyPath)) {
    logger.warn(
      { privateKeyPath },
      'GITHUB_APP_PRIVATE_KEY_FILE does not exist; skipping GitHub App auth',
    );
    return undefined;
  }
  return fs.readFileSync(privateKeyPath, 'utf-8');
}

function buildGitHubAppJwt(appId: string, privateKeyPem: string): string {
  const now = Math.floor(Date.now() / 1000);
  const header = { alg: 'RS256', typ: 'JWT' };
  const payload = {
    iat: now - 60,
    exp: now + 9 * 60,
    iss: appId,
  };

  const unsignedToken = `${toBase64Url(JSON.stringify(header))}.${toBase64Url(
    JSON.stringify(payload),
  )}`;
  const signer = createSign('RSA-SHA256');
  signer.update(unsignedToken);
  signer.end();
  const signature = signer.sign(privateKeyPem);

  return `${unsignedToken}.${toBase64Url(signature)}`;
}

async function fetchGitHubInstallationToken(
  appId: string,
  installationId: string,
  privateKeyPem: string,
): Promise<GitHubTokenCache> {
  const jwt = buildGitHubAppJwt(appId, privateKeyPem);
  const endpoint = `https://api.github.com/app/installations/${encodeURIComponent(installationId)}/access_tokens`;
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${jwt}`,
      Accept: 'application/vnd.github+json',
      'User-Agent': 'devbox-agent',
    },
  });

  if (!response.ok) {
    const body = (await response.text()).slice(0, 300);
    throw new Error(
      `GitHub App token request failed (${response.status}): ${body}`,
    );
  }

  const payload = (await response.json()) as GitHubAccessTokenResponse;
  if (!payload.token || !payload.expires_at) {
    throw new Error('GitHub App token response missing token or expires_at');
  }

  const expiresAtMs = Date.parse(payload.expires_at);
  if (!Number.isFinite(expiresAtMs)) {
    throw new Error('GitHub App token response has invalid expires_at');
  }

  return {
    token: payload.token,
    expiresAtMs,
  };
}

function readDirectGitHubToken(): string | undefined {
  for (const directKey of [
    GITHUB_SEED_TOKEN_SECRET,
    'GITHUB_TOKEN',
    'GH_TOKEN',
    'GITHUB_PAT',
  ]) {
    const directValue = process.env[directKey]?.trim();
    if (directValue) return directValue;
  }
  return undefined;
}

function normalizeOwnerForEnv(owner: string): string {
  return owner.replace(/[^A-Za-z0-9]/g, '_').toUpperCase();
}

function parseInstallationIdsMap(): Record<string, string> {
  const raw = process.env.GITHUB_APP_INSTALLATION_IDS?.trim();
  if (!raw) return {};

  // Accept JSON object (`{"org":"id"}`) or `org=id,org2=id2` format.
  if (raw.startsWith('{')) {
    try {
      const parsed = JSON.parse(raw) as Record<string, unknown>;
      const result: Record<string, string> = {};
      for (const [owner, id] of Object.entries(parsed)) {
        const normalizedOwner = owner.trim().toLowerCase();
        const normalizedId = String(id).trim();
        if (normalizedOwner && normalizedId)
          result[normalizedOwner] = normalizedId;
      }
      return result;
    } catch (err) {
      logger.warn(
        { error: err },
        'Failed to parse GITHUB_APP_INSTALLATION_IDS JSON; ignoring',
      );
      return {};
    }
  }

  const result: Record<string, string> = {};
  for (const pair of raw.split(',')) {
    const trimmedPair = pair.trim();
    if (!trimmedPair) continue;
    const sep = trimmedPair.includes('=') ? '=' : ':';
    const [rawOwner, rawId] = trimmedPair.split(sep, 2);
    const owner = rawOwner?.trim().toLowerCase();
    const id = rawId?.trim();
    if (owner && id) result[owner] = id;
  }
  return result;
}

function resolveGitHubAppInstallationId(
  owner: string,
  installationMap: Record<string, string>,
): string | undefined {
  const ownerSpecificEnv =
    process.env[
      `GITHUB_APP_INSTALLATION_ID_${normalizeOwnerForEnv(owner)}`
    ]?.trim();
  if (ownerSpecificEnv) return ownerSpecificEnv;

  const mapped = installationMap[owner];
  if (mapped) return mapped;

  const defaultInstallationId = process.env.GITHUB_APP_INSTALLATION_ID?.trim();
  if (defaultInstallationId) return defaultInstallationId;

  return undefined;
}

async function resolveCachedInstallationToken(
  appId: string,
  installationId: string,
  privateKeyPem: string,
): Promise<string> {
  const cached = githubTokenCache.get(installationId);
  if (cached && cached.expiresAtMs - 60_000 > Date.now()) {
    return cached.token;
  }

  const fresh = await fetchGitHubInstallationToken(
    appId,
    installationId,
    privateKeyPem,
  );
  githubTokenCache.set(installationId, fresh);
  logger.info(
    {
      installationId,
      expiresAt: new Date(fresh.expiresAtMs).toISOString(),
    },
    'Fetched GitHub App installation token for repo seeding',
  );
  return fresh.token;
}

async function resolveGitHubSeedTokens(
  owners: string[],
): Promise<Record<string, string>> {
  if (owners.length === 0) return {};

  const directToken = readDirectGitHubToken();
  if (directToken) {
    const directTokens: Record<string, string> = {};
    for (const owner of owners) directTokens[owner] = directToken;
    return directTokens;
  }

  const appId = process.env.GITHUB_APP_ID?.trim();
  const privateKeyPem = readGitHubAppPrivateKey();
  const hasAnyGitHubAppConfig = Boolean(
    appId ||
    process.env.GITHUB_APP_INSTALLATION_ID ||
    process.env.GITHUB_APP_INSTALLATION_IDS ||
    process.env.GITHUB_APP_PRIVATE_KEY ||
    process.env.GITHUB_APP_PRIVATE_KEY_FILE ||
    Object.keys(process.env).some((k) =>
      k.startsWith('GITHUB_APP_INSTALLATION_ID_'),
    ),
  );

  if (!hasAnyGitHubAppConfig) return {};
  if (!appId || !privateKeyPem) {
    logger.warn(
      {
        hasAppId: Boolean(appId),
        hasPrivateKey: Boolean(privateKeyPem),
      },
      'GitHub App auth is partially configured; skipping token-based repo auth',
    );
    return {};
  }

  const tokensByOwner: Record<string, string> = {};
  const installationMap = parseInstallationIdsMap();
  for (const owner of owners) {
    const installationId = resolveGitHubAppInstallationId(
      owner,
      installationMap,
    );
    if (!installationId) {
      logger.warn(
        { owner },
        'Missing GitHub App installation ID for repo owner; this owner will fail to clone',
      );
      continue;
    }
    tokensByOwner[owner] = await resolveCachedInstallationToken(
      appId,
      installationId,
      privateKeyPem,
    );
  }
  return tokensByOwner;
}

async function readSecrets(
  seedRepos: SeedManifestRepo[],
): Promise<Record<string, string>> {
  const result: Record<string, string> = {};
  for (const key of [
    'CLAUDE_CODE_OAUTH_TOKEN',
    'ANTHROPIC_API_KEY',
    'ANTHROPIC_BASE_URL',
    'ANTHROPIC_AUTH_TOKEN',
    'CLAUDE_CODE_USE_VERTEX',
    'CLOUD_ML_REGION',
    'ANTHROPIC_VERTEX_PROJECT_ID',
    'CLAUDE_CODE_USE_BEDROCK',
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_SESSION_TOKEN',
    'AWS_REGION',
    'AWS_DEFAULT_REGION',
    'ANTHROPIC_BEDROCK_BASE_URL',
    'ANTHROPIC_DEFAULT_SONNET_MODEL',
  ]) {
    const val = process.env[key];
    if (val) result[key] = val;
  }

  const githubOwners = workspaceGitHubOwners(seedRepos);
  if (githubOwners.length > 0) {
    const tokensByOwner = await resolveGitHubSeedTokens(githubOwners);
    const entries = Object.entries(tokensByOwner);
    if (entries.length > 0) {
      result[GITHUB_SEED_TOKENS_SECRET] = JSON.stringify(tokensByOwner);
      // Backwards compatibility for older entrypoint consumers.
      result[GITHUB_SEED_TOKEN_SECRET] = entries[0][1];
    }
  }

  return result;
}

interface RunFiles {
  runId: string;
  hostRunDir: string;
  hostInputPath: string;
  hostOutDir: string;
  hostDonePath: string;
  containerRunDir: string;
}

interface RunDonePayload {
  status: 'success' | 'error';
  error?: string;
  details?: unknown;
}

function isStaleSessionResumeFailure(
  donePayload: RunDonePayload | null,
  sessionId?: string,
): boolean {
  if (!sessionId || donePayload?.status !== 'error') return false;

  const details = donePayload.details;
  if (!details || typeof details !== 'object' || Array.isArray(details)) {
    return false;
  }

  const record = details as Record<string, unknown>;
  if (record.subtype !== 'error_during_execution') return false;
  if (record.num_turns !== 0) return false;
  if (record.total_cost_usd !== 0) return false;

  const errors = Array.isArray(record.errors)
    ? record.errors.filter(
        (value): value is string => typeof value === 'string',
      )
    : [];

  return errors.some((value) =>
    value.includes('No conversation found with session ID:'),
  );
}

function isSeedCloneFailure(
  stderr: string,
  donePayload: RunDonePayload | null,
): boolean {
  if (stderr.includes('DEVBOX_SEED_CLONE_ERROR:')) return true;
  return (
    donePayload?.status === 'error' &&
    typeof donePayload.error === 'string' &&
    donePayload.error.includes('DEVBOX_SEED_CLONE_ERROR:')
  );
}

function buildResumeFailureLogLines(
  agentName: string,
  input: ContainerInput,
): string[] {
  if (!input.sessionId) return [];

  const claudeDir = resolveSessionClaudePath(agentName, input.sessionKey);
  const projectsDir = path.join(claudeDir, 'projects');
  const projectsDirExists = fs.existsSync(projectsDir);
  let projectsDirEntries = 0;
  if (projectsDirExists) {
    try {
      projectsDirEntries = fs.readdirSync(projectsDir).length;
    } catch {
      projectsDirEntries = -1;
    }
  }

  return [
    `=== Resume Diagnostics ===`,
    `Resume Attempt: yes`,
    `Resume Session ID: ${input.sessionId}`,
    `Transcript Expected To Exist: yes`,
    `Claude State Dir: ${claudeDir}`,
    `Claude Projects Dir Exists: ${projectsDirExists}`,
    `Claude Projects Dir Entries: ${projectsDirEntries >= 0 ? projectsDirEntries : 'unreadable'}`,
    ``,
  ];
}

function createRunFiles(agentName: string, sessionKey: string): RunFiles {
  const runId = `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
  const hostRunDir = path.join(
    resolveSessionIpcPath(agentName, sessionKey),
    'runs',
    runId,
  );
  const hostOutDir = path.join(hostRunDir, 'out');
  const hostInputPath = path.join(hostRunDir, 'input.json');
  const hostDonePath = path.join(hostRunDir, 'done.json');
  const containerRunDir = `/ipc/runs/${runId}`;

  mkdirOwned(hostOutDir);

  return {
    runId,
    hostRunDir,
    hostInputPath,
    hostOutDir,
    hostDonePath,
    containerRunDir,
  };
}

function readRunDone(pathname: string): RunDonePayload | null {
  if (!fs.existsSync(pathname)) return null;
  try {
    return JSON.parse(fs.readFileSync(pathname, 'utf-8')) as RunDonePayload;
  } catch (err) {
    return {
      status: 'error',
      error: `Invalid done.json: ${err instanceof Error ? err.message : String(err)}`,
    };
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function runContainerAgent(
  runtime: ContainerRuntime,
  agent: RegisteredAgent,
  input: ContainerInput,
  onProcess: (containerName: string) => void,
  onOutput?: (output: ContainerOutput) => Promise<void>,
): Promise<ContainerOutput> {
  const startTime = Date.now();
  const elapsed = () => `${Date.now() - startTime}ms`;

  logger.info(
    { agent: agent.name },
    `[${elapsed()}] runContainerAgent started`,
  );

  mkdirOwned(resolveSessionPath(agent.agentName, input.sessionKey));
  mkdirOwned(resolveSessionWorkspacePath(agent.agentName, input.sessionKey));
  touchSessionHeartbeat(agent.agentName, input.sessionKey);

  logger.info({ agent: agent.name }, `[${elapsed()}] Building volume mounts`);

  let mounts: RuntimeMount[];
  let secretMounts: RuntimeSecretMount[];
  let seedRepos: SeedManifestRepo[];
  let containerImage: string | undefined;
  let model: string | undefined;
  let thinking: ThinkingConfig | undefined;
  let effort: 'low' | 'medium' | 'high' | 'max' | undefined;
  try {
    ({
      mounts,
      secretMounts,
      seedRepos,
      containerImage,
      model,
      thinking,
      effort,
    } = buildVolumeMounts(agent, input.sessionKey));
  } catch (err) {
    const errorMessage =
      err instanceof Error ? err.message : 'Unknown mount setup error';
    logger.error(
      { agent: agent.name, error: err },
      'Failed to prepare container mounts',
    );
    return {
      status: 'error',
      result: null,
      error: `Failed to prepare container mounts: ${errorMessage}`,
    };
  }

  // When running locally via Docker Compose, chown all writable mount
  // directories so the runner (uid 1000) can write to them. Skip on
  // Kubernetes — the runner pod uses securityContext instead, and recursive
  // chown over NFS (Filestore) takes 2+ minutes.
  if (process.getuid?.() === 0 && CONTAINER_RUNTIME === 'docker') {
    for (const mount of mounts) {
      if (mount.readonly) continue;
      try {
        fs.chownSync(mount.hostPath, RUNNER_UID, RUNNER_GID);
        const chownRecursive = (dir: string) => {
          for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
            if (entry.isSymbolicLink()) continue;
            const full = path.join(dir, entry.name);
            fs.chownSync(full, RUNNER_UID, RUNNER_GID);
            if (entry.isDirectory()) chownRecursive(full);
          }
        };
        chownRecursive(mount.hostPath);
      } catch (err) {
        logger.warn(
          { mount: mount.hostPath, err },
          'Failed to chown mount for runner',
        );
      }
    }
  }

  logger.info({ agent: agent.name }, `[${elapsed()}] Volume mounts ready`);

  let secrets: Record<string, string> = {};
  try {
    logger.info({ agent: agent.name }, `[${elapsed()}] Resolving secrets`);
    secrets = await readSecrets(seedRepos);
  } catch (err) {
    const errorMessage =
      err instanceof Error ? err.message : 'Unknown token setup error';
    logger.error(
      { agent: agent.name, error: err },
      'Failed to prepare container secrets',
    );
    return {
      status: 'error',
      result: null,
      error: `Failed to prepare container secrets: ${errorMessage}`,
    };
  }

  logger.info({ agent: agent.name }, `[${elapsed()}] Secrets resolved`);

  const safeName = agent.agentName.replace(/[^a-zA-Z0-9-]/g, '-');
  const containerName = `devbox-${safeName}-${Date.now()}`;
  const runFiles = createRunFiles(agent.agentName, input.sessionKey);

  // Merge seed.yaml model configuration into input (seed.yaml takes precedence)
  const enhancedInput = {
    ...input,
    ...(model ? { model } : {}),
    ...(thinking ? { thinking } : {}),
    ...(effort ? { effort } : {}),
    secrets,
  };

  fs.writeFileSync(
    runFiles.hostInputPath,
    `${JSON.stringify(enhancedInput, null, 2)}\n`,
  );

  // Chown the run directory so the runner (uid 1000) can write output files.
  // The run directory is created after the earlier mount-level chown pass,
  // so it needs its own ownership fix when the controller runs as root.
  if (process.getuid?.() === 0) {
    for (const p of [
      runFiles.hostRunDir,
      runFiles.hostOutDir,
      runFiles.hostInputPath,
    ]) {
      try {
        fs.chownSync(p, RUNNER_UID, RUNNER_GID);
      } catch {
        // best-effort
      }
    }
  }

  const hostUid = process.getuid?.();
  const hostGid = process.getgid?.();
  const runtimeUser =
    hostUid != null && hostUid !== 0 && hostGid != null
      ? `${hostUid}:${hostGid}`
      : undefined;

  const runtimeEnv: Record<string, string> = {
    TZ: TIMEZONE,
    DEVBOX_RUN_DIR: runFiles.containerRunDir,
    HOME: CONTAINER_HOME,
  };

  // Point the runner at the copied ADC file when using Vertex AI.
  if (process.env.CLAUDE_CODE_USE_VERTEX) {
    runtimeEnv.GOOGLE_APPLICATION_CREDENTIALS = '/session/gcloud-adc.json';
  }

  // Forward model/API configuration from controller env to runner pods.
  for (const key of [
    'CLAUDE_CODE_USE_VERTEX',
    'CLOUD_ML_REGION',
    'ANTHROPIC_VERTEX_PROJECT_ID',
    'CLAUDE_CODE_USE_BEDROCK',
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_SESSION_TOKEN',
    'AWS_REGION',
    'AWS_DEFAULT_REGION',
    'ANTHROPIC_BEDROCK_BASE_URL',
    'ANTHROPIC_DEFAULT_SONNET_MODEL',
  ]) {
    const val = process.env[key];
    if (val) runtimeEnv[key] = val;
  }

  logger.debug(
    {
      agent: agent.name,
      containerName,
      runId: runFiles.runId,
      mounts: mounts.map(
        (m) =>
          `${m.hostPath} -> ${m.containerPath}${m.readonly ? ' (ro)' : ''}`,
      ),
      secretMounts: secretMounts.map(
        (m) => `${m.secretName}: ${m.hostPath} -> ${m.containerPath} (ro)`,
      ),
    },
    'Container mount configuration',
  );

  logger.info(
    {
      agent: agent.name,
      containerName,
      image: containerImage || CONTAINER_IMAGE,
      mountCount: mounts.length,
      runId: runFiles.runId,
    },
    'Spawning container agent',
  );

  const logsDir = path.join(AGENTS_DIR, agent.agentName, 'logs');
  fs.mkdirSync(logsDir, { recursive: true });

  let stdout = '';
  let stderr = '';
  let stdoutTruncated = false;
  let stderrTruncated = false;
  let timedOut = false;
  let hadStreamingOutput = false;
  let newSessionId: string | undefined;
  let lastOutput: ContainerOutput | null = null;
  let outputChain = Promise.resolve();
  const processedOutputFiles = new Set<string>();

  const drainRunOutputs = () => {
    let files: string[] = [];
    try {
      files = fs
        .readdirSync(runFiles.hostOutDir)
        .filter((f) => f.endsWith('.json'))
        .sort();
    } catch {
      return;
    }

    for (const file of files) {
      if (processedOutputFiles.has(file)) continue;
      const outputPath = path.join(runFiles.hostOutDir, file);
      let parsed: ContainerOutput;
      try {
        parsed = JSON.parse(fs.readFileSync(outputPath, 'utf-8'));
      } catch (err) {
        logger.warn(
          { file: outputPath, err },
          'Failed to parse run output file',
        );
        processedOutputFiles.add(file);
        continue;
      }

      processedOutputFiles.add(file);
      lastOutput = parsed;
      if (parsed.newSessionId) newSessionId = parsed.newSessionId;
      hadStreamingOutput = true;
      resetTimeout();
      if (onOutput) {
        outputChain = outputChain.then(() => onOutput(parsed));
      }
    }
  };

  const configTimeout = agent.containerConfig?.timeout || CONTAINER_TIMEOUT;
  const timeoutMs = Math.max(configTimeout, IDLE_TIMEOUT + 30_000);
  let handle: Awaited<ReturnType<ContainerRuntime['spawn']>> | null = null;
  let timeout: ReturnType<typeof setTimeout> | null = null;

  const killOnTimeout = () => {
    timedOut = true;
    logger.error(
      { agent: agent.name, containerName },
      'Container timeout, stopping gracefully',
    );
    void handle?.stop();
  };

  const resetTimeout = () => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(killOnTimeout, timeoutMs);
  };

  resetTimeout();

  logger.info(
    { agent: agent.name, containerName },
    `[${elapsed()}] Spawning container`,
  );

  try {
    handle = await runtime.spawn({
      name: containerName,
      image: containerImage || CONTAINER_IMAGE,
      mounts,
      secretMounts,
      env: runtimeEnv,
      user: runtimeUser,
      onStdoutChunk: (chunk) => {
        if (!stdoutTruncated) {
          const remaining = CONTAINER_MAX_OUTPUT_SIZE - stdout.length;
          if (chunk.length > remaining) {
            stdout += chunk.slice(0, remaining);
            stdoutTruncated = true;
            logger.warn(
              { agent: agent.name, size: stdout.length },
              'Container stdout truncated due to size limit',
            );
          } else {
            stdout += chunk;
          }
        }
      },
      onStderrChunk: (chunk) => {
        const lines = chunk.trim().split('\n');
        for (const line of lines) {
          if (line) logger.debug({ container: agent.agentName }, line);
        }
        if (stderrTruncated) return;
        const remaining = CONTAINER_MAX_OUTPUT_SIZE - stderr.length;
        if (chunk.length > remaining) {
          stderr += chunk.slice(0, remaining);
          stderrTruncated = true;
          logger.warn(
            { agent: agent.name, size: stderr.length },
            'Container stderr truncated due to size limit',
          );
        } else {
          stderr += chunk;
        }
      },
    });
  } catch (err) {
    if (timeout) clearTimeout(timeout);
    try {
      fs.unlinkSync(runFiles.hostInputPath);
    } catch {
      // ignore
    }
    logger.error(
      { agent: agent.name, containerName, error: err },
      'Container spawn error',
    );
    return {
      status: 'error',
      result: null,
      error: `Container spawn error: ${err instanceof Error ? err.message : String(err)}`,
    };
  }

  logger.info(
    { agent: agent.name, containerName },
    `[${elapsed()}] Container spawned, waiting for exit`,
  );

  onProcess(containerName);

  const outputPoll = setInterval(drainRunOutputs, 250);
  let exitCode: number | null = null;
  let donePayload: RunDonePayload | null = null;

  try {
    const exit = await handle.waitForExit();
    exitCode = exit.code;
  } catch (err) {
    if (timeout) clearTimeout(timeout);
    clearInterval(outputPoll);
    try {
      fs.unlinkSync(runFiles.hostInputPath);
    } catch {
      // ignore
    }
    logger.error(
      { agent: agent.name, containerName, error: err },
      'Container waitForExit failed',
    );
    return {
      status: 'error',
      result: null,
      error: `Container process error: ${err instanceof Error ? err.message : String(err)}`,
    };
  } finally {
    if (timeout) clearTimeout(timeout);
    clearInterval(outputPoll);
  }

  drainRunOutputs();

  const doneWaitDeadline = Date.now() + 2000;
  donePayload = readRunDone(runFiles.hostDonePath);
  while (!donePayload && Date.now() < doneWaitDeadline) {
    await sleep(100);
    drainRunOutputs();
    donePayload = readRunDone(runFiles.hostDonePath);
  }

  await outputChain;

  const duration = Date.now() - startTime;
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const logFile = path.join(logsDir, `container-${timestamp}.log`);
  const isVerbose =
    process.env.LOG_LEVEL === 'debug' || process.env.LOG_LEVEL === 'trace';

  const logLines = [
    `=== Container Run Log ===`,
    `Timestamp: ${new Date().toISOString()}`,
    `Group: ${agent.name}`,
    `Duration: ${duration}ms`,
    `Exit Code: ${exitCode}`,
    `Run Id: ${runFiles.runId}`,
    `Stdout Truncated: ${stdoutTruncated}`,
    `Stderr Truncated: ${stderrTruncated}`,
    ``,
  ];

  const isError =
    timedOut ||
    donePayload?.status === 'error' ||
    (exitCode !== 0 && exitCode !== null);

  if (isVerbose || isError) {
    if (donePayload?.status === 'error') {
      logLines.push(...buildResumeFailureLogLines(agent.agentName, input));
    }
    logLines.push(
      `=== Input ===`,
      JSON.stringify(input, null, 2),
      ``,
      `=== Mounts ===`,
      mounts
        .map(
          (m) =>
            `${m.hostPath} -> ${m.containerPath}${m.readonly ? ' (ro)' : ''}`,
        )
        .join('\n'),
      ``,
      `=== Run Paths ===`,
      `Host: ${runFiles.hostRunDir}`,
      `Container: ${runFiles.containerRunDir}`,
      ``,
      `=== Done ===`,
      donePayload ? JSON.stringify(donePayload, null, 2) : 'missing',
      ``,
      `=== Stderr${stderrTruncated ? ' (TRUNCATED)' : ''} ===`,
      stderr,
      ``,
      `=== Stdout${stdoutTruncated ? ' (TRUNCATED)' : ''} ===`,
      stdout,
    );
  } else {
    logLines.push(
      `=== Input Summary ===`,
      `Prompt length: ${input.prompt.length} chars`,
      `Session ID: ${input.sessionId || 'new'}`,
      ``,
      `=== Mounts ===`,
      mounts
        .map((m) => `${m.containerPath}${m.readonly ? ' (ro)' : ''}`)
        .join('\n'),
      ``,
    );
  }

  fs.writeFileSync(logFile, logLines.join('\n'));
  logger.debug({ logFile, verbose: isVerbose }, 'Container log written');

  // Best effort: remove run input file that contained secrets.
  try {
    fs.unlinkSync(runFiles.hostInputPath);
  } catch {
    // ignore
  }

  if (timedOut) {
    if (hadStreamingOutput) {
      logger.info(
        { agent: agent.name, containerName, duration, exitCode },
        'Container timed out after output (idle cleanup)',
      );
      return {
        status: 'success',
        result: null,
        newSessionId,
      };
    }

    logger.error(
      { agent: agent.name, containerName, duration, exitCode },
      'Container timed out with no output',
    );
    return {
      status: 'error',
      result: null,
      error: `Container timed out after ${configTimeout}ms`,
    };
  }

  if (donePayload?.status === 'error') {
    const errorKind = isStaleSessionResumeFailure(donePayload, input.sessionId)
      ? 'stale_session_resume'
      : isSeedCloneFailure(stderr, donePayload)
        ? 'seed_clone_failed'
        : undefined;
    return {
      status: 'error',
      result: null,
      error: donePayload.error || 'Runner reported error in done.json',
      newSessionId,
      errorKind,
    };
  }

  if (exitCode !== 0 && exitCode !== null) {
    const errorKind = isSeedCloneFailure(stderr, donePayload)
      ? 'seed_clone_failed'
      : undefined;
    return {
      status: 'error',
      result: null,
      error: `Container exited with code ${exitCode}: ${stderr.slice(-200)}`,
      newSessionId,
      errorKind,
    };
  }

  if (!onOutput) {
    return (
      lastOutput || {
        status: 'success',
        result: null,
        newSessionId,
      }
    );
  }

  return {
    status: 'success',
    result: null,
    newSessionId,
  };
}

export function writeTasksSnapshot(
  agentName: string,
  sessionKey: string,
  tasks: Array<{
    id: string;
    agentName: string;
    prompt: string;
    schedule_type: string;
    schedule_value: string;
    status: string;
    next_run: string | null;
  }>,
): void {
  const agentIpcDir = resolveSessionIpcPath(agentName, sessionKey);
  mkdirOwned(agentIpcDir);

  const filteredTasks = tasks.filter((t) => t.agentName === agentName);

  const tasksFile = path.join(agentIpcDir, 'current_tasks.json');
  writeFileOwned(tasksFile, JSON.stringify(filteredTasks, null, 2));
}

export interface AvailableGroup {
  jid: string;
  name: string;
  lastActivity: string;
  isRegistered: boolean;
}

/**
 * Write available groups snapshot for the container to read.
 * Only main group can see all available groups (for activation).
 * Non-main groups only see their own registration status.
 */
export function writeGroupsSnapshot(
  agentName: string,
  sessionKey: string,
): void {
  const agentIpcDir = resolveSessionIpcPath(agentName, sessionKey);
  mkdirOwned(agentIpcDir);

  const groupsFile = path.join(agentIpcDir, 'available_groups.json');
  writeFileOwned(
    groupsFile,
    JSON.stringify(
      {
        groups: [],
        lastSync: new Date().toISOString(),
      },
      null,
      2,
    ),
  );
}
