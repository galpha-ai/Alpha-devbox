# 001: Deployment Architecture

## Status

Draft

## Problem

devbox-agent conflates application code with runtime data. All paths resolve from `process.cwd()`, assuming execution from the repo root. This makes it impossible to package as a Docker image or deploy to Kubernetes without carrying the full repo checkout as the runtime environment.

The workspace model is also tightly coupled to a single-template seeding flow. The target is multi-repo projects where the agent works across several repositories, submits PRs, and maintains memory across sessions.

## Goals

- Package the controller as a deployable Docker image
- Deploy on k8s using the existing kustomize base + staging overlay pattern
- Support persistent multi-repo workspaces with deterministic initialization
- Separate config (versioned, deterministic) from state (mutable, persistent)
- Maintain backwards compatibility with local `just dev` workflow

## Non-Goals

- Replacing Docker-based container spawning with k8s Jobs API (future work)
- Dynamic group creation and GC (future extension, but design should not preclude it)
- Multi-node scheduling (single-node k3s is the target)

---

## Architecture

### Two-Process Model

The system has two process types:

1. **Controller** (long-lived) — owns all coordination: Telegram bot, message routing, group queue, task scheduling, SQLite, workspace seeding, and runner lifecycle management. Packaged as `devbox-controller` image, runs as a k8s Deployment.

2. **Runner** (ephemeral, per-turn) — executes a single turn of agent work: Claude Code + agent-runner scripts. Has no knowledge of Telegram, scheduling, or other groups. Receives a task via mounted IPC dir, executes, writes results back. Spawned by the controller via Docker CLI through a mounted Docker socket. Packaged as `devbox-runner` image.

### Three-Layer Data Model

All data falls into one of three categories with distinct lifecycle and persistence:

| Layer         | Lifecycle                                                           | Examples                                            | Persistence                                   |
|---------------|---------------------------------------------------------------------|-----------------------------------------------------|-----------------------------------------------|
| **Config**    | Immutable per deployment. Version-controlled.                       | CLAUDE.md, skills/, settings.json                   | Baked into image or copied at container start |
| **State**     | Mutable, persists across container restarts.                        | `.claude/` memory, `MEMORY.md`, session IDs, SQLite | Persistent volume                             |
| **Workspace** | Mutable, persists within a group. Seeded once, reused across turns. | Repo checkouts, agent code changes                  | Persistent volume, gated by `.seeded` marker  |

### Data Directory Layout

On the k8s node, a single directory holds all runtime data:

```
/data/devbox-agent/                    # DATA_ROOT (hostPath volume)
  store/
    messages.db                        # SQLite — all persistent DB state
  groups/
    global/
      CLAUDE.md                        # Shared instructions (config layer)
      logs/                            # Container run logs
  data/
    sessions/{agent}/{session}/
      CLAUDE.md                        # Session metadata copy of agent instructions
      seed-manifest.json               # Session seed manifest for entrypoint
      workspace/                       # Agent workspace (workspace layer)
        .seeded                        # Initialization gate marker
        CLAUDE.md                      # Working copy for upward instruction discovery
        repo1/
        repo2/
        ...
      .claude/                         # Claude Code state (state layer)
        settings.json
        skills/
        projects/                      # Agent memory — persists across turns
        MEMORY.md                      # Auto-memory — persists across turns
      ipc/
        messages/                      # Streamed output from container
        tasks/                         # Task snapshots
        input/                         # Piped messages to container
```

### Runner Container Mounts

When the controller spawns a runner:

| Host Path                                             | Container Path         | Mode | Layer     |
|-------------------------------------------------------|------------------------|------|-----------|
| `{DATA_ROOT}/data/sessions/{agent}/{session}/`        | `/session`             | RO   | Config    |
| `{DATA_ROOT}/data/sessions/{agent}/{session}/workspace` | `/workspace`         | RW   | Workspace |
| `{DATA_ROOT}/groups/global`                           | `/workspace/global`    | RO   | Config    |
| `{DATA_ROOT}/data/sessions/{agent}/{session}/.claude` | `/home/devbox/.claude` | RW   | State     |
| `{DATA_ROOT}/data/sessions/{agent}/{session}/ipc`     | `/ipc`                 | RW   | Transient |

Config-layer files (CLAUDE.md, skills, settings.json) are managed by the controller:
- `data/sessions/{agent}/{session}/CLAUDE.md` is the session metadata copy, and a working copy is materialized into `workspace/CLAUDE.md` so the agent can start from `/workspace`
- `skills/` are synced from the app's `container/skills/` into each session's `.claude/skills/` before each container run (existing behavior in `container-runner.ts`)
- `settings.json` is written once on first run with default Claude Code settings

The agent can update its own memory (`.claude/projects/`, `MEMORY.md`) — this persists in the state layer. But CLAUDE.md is treated as deployment config, not agent-writable state.

### Path Alignment

The data directory is mounted into the controller pod at the **same path** as on the k8s node:

```
hostPath: /data/devbox-agent  →  pod mountPath: /data/devbox-agent
```

This ensures that when the controller runs Docker or creates a runner pod with mounts like `/data/devbox-agent/data/sessions/main/<scope>/workspace:/workspace`, the runtime resolves the shared path on the k8s node correctly. No path translation is needed.

---

## Workspace Initialization

### Per-Group Seeding

Each group workspace is initialized once, gated by a `.seeded` marker file:

```
1. Check: does `data/sessions/{agent}/{session}/workspace/.seeded` exist?
2. If yes → skip, workspace is ready
3. If no →
   a. Clone/copy configured repos into `data/sessions/{agent}/{session}/workspace/`
   b. Write .seeded marker
4. Workspace is ready for agent use
```

To re-initialize a group, delete the `.seeded` file. The next runner invocation triggers fresh seeding. This is safe and idempotent.

### Init Phase (k8s)

In production, workspace initialization runs as a k8s initContainer:

```yaml
initContainers:
- name: seed-workspaces
  image: alpine/git
  command: ["/bin/sh", "/scripts/seed.sh"]
  volumeMounts:
  - name: data
    mountPath: /data/devbox-agent
```

The seed script:
1. For each configured group, check `.seeded` marker
2. If not seeded, clone repos from configured sources (git URLs or local paths)
3. Write `.seeded` marker

For local dev, the same logic runs inline (existing `entrypoint.sh` behavior).

### Workspace Schema Change

Replace the current rigid workspace config with a repo list:

```yaml
# Current contract
workspace:
  repos:
    - name: service-a
      source: git@github.com:user/service-a.git
      ref: main                          # optional, default: HEAD
    - name: service-b
      source: git@github.com:user/service-b.git
      ref: main
```

Each repo is cloned into the session workspace during seeding. Repo sources are
remote git URLs; local filesystem paths are rejected by the controller before
the runner starts.

---

## Persistent Groups

### Stable Groups

Configured in `config.yaml`, created at startup. The workspace persists indefinitely. Example: a dedicated chat where you interact with the agent directly.

### Dynamic Groups (Future Extension)

Created on demand when a user starts a thread and mentions the agent in a dev channel. The system:
1. Creates a new group entry (DB + filesystem)
2. Seeds workspace (clone repos)
3. Agent works on the task across multiple turns
4. User can ask agent to create PR, upload files, etc. after completion

Group workspaces accumulate over time. A GC policy cleans up old groups:
- After N days of inactivity
- After the workspace exceeds a size threshold
- Manual cleanup via admin command

The persistent group model supports this naturally — GC is just deleting the group directory and DB entries.

---

## Code Changes

### 1. Separate app root from data root (`src/config.ts`)

```typescript
// App root: derived from module location, not cwd
// In dev: <repo>/src/ → resolve('..') → <repo>/
// In built: <repo>/dist/ → resolve('..') → <repo>/
// In Docker: /app/dist/ → resolve('..') → /app/
export const APP_ROOT = path.resolve(import.meta.dirname, '..');

// Data root: where runtime state lives
// Env var > config file > cwd (backwards compat)
let DATA_ROOT = process.env.DEVBOX_DATA_ROOT || process.cwd();
```

Add optional `data_root` to config schema:

```typescript
const ConfigSchema = z.object({
  // ... existing fields ...
  data_root: z.string().optional(),
});
```

In `loadConfig()`, if `data_root` is set in config and env var is not set, use it. Then recompute `STORE_DIR`, `GROUPS_DIR`, `DATA_DIR` from `DATA_ROOT`.

### 2. Replace `process.cwd()` in `src/container-runner.ts`

Two references to fix:

```typescript
// Line 138: skills source
const skillsSrc = path.join(APP_ROOT, 'container', 'skills');

// Line 169: agent-runner source
const agentRunnerSrc = path.join(APP_ROOT, 'container', 'agent-runner', 'src');
```

### 3. Make container runtime configurable (`src/container-runtime.ts`)

```typescript
export const CONTAINER_RUNTIME_BIN = process.env.CONTAINER_RUNTIME || 'docker';
```

### 4. Generalize workspace config (`src/config.ts`)

Replace `WorkspaceSchema` with:

```typescript
const RepoSchema = z.object({
  name: z.string(),
  source: z.string(),           // git URL or local path
  ref: z.string().optional(),   // branch/tag/commit
});

const WorkspaceSchema = z.object({
  repos: z.array(RepoSchema).optional().default([]),
});
```

### 5. Update seeding logic (`container/entrypoint.sh`)

The controller writes a `seed-manifest.json` into the group directory before runner start:

```json
{
  "repos": [
    {"name": "service-a", "source": "git@github.com:user/service-a.git"},
    {"name": "service-b", "source": "git@github.com:user/service-b.git"}
  ]
}
```

The entrypoint reads this manifest and clones each repo if not already seeded.

### 6. Dockerfiles (`docker/controller.Dockerfile`, `docker/runner.Dockerfile`)

```dockerfile
FROM node:22-slim

RUN apt-get update && apt-get install -y \
    docker.io git openssh-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY dist/ ./dist/
COPY container/skills/ ./container/skills/
COPY container/agent-runner/src/ ./container/agent-runner/src/

ENTRYPOINT ["node", "dist/index.js"]
```

Includes Docker CLI (talks to mounted socket) and git (for seed operations). The `container/skills/` and `container/agent-runner/src/` directories are needed by the controller to sync into per-group state dirs.

Runner image is defined separately at `docker/runner.Dockerfile` and contains Claude Code + language/toolchain dependencies used for per-turn execution.

### 7. Build script (`scripts/build-push.sh`)

Builds and pushes both images:
- Controller: `nuoyiman001/devbox-controller:<sha>`
- Runner: `nuoyiman001/devbox-runner:<sha>`

---

## Kubernetes Manifests

Following the current repo structure and kustomize layout.

### Base (`k8s/base/`)

```
k8s/base/
  kustomization.yaml
  deployment.yaml
  config.yaml
```

`deployment.yaml` defines the `devbox-controller` Deployment, mounts:
- hostPath data volume at `/data/devbox-agent`
- docker socket at `/var/run/docker.sock`
- config map at `/etc/devbox-agent/config.yaml`
- secrets for Telegram/Anthropic credentials and SSH keys

### Overlay (`k8s/overlays/staging/`)

```
k8s/overlays/staging/
  kustomization.yaml
  namespace.yaml
  config.staging.yaml
```

**kustomization.yaml**:

```yaml
namespace: devbox-agent
resources:
  - namespace.yaml
  - ../../base
images:
  - name: devbox-controller
    newName: nuoyiman001/devbox-controller
    newTag: "<commit-sha>"
configMapGenerator:
  - name: devbox-agent-config
    behavior: replace
    files:
      - config.yaml=config.staging.yaml
```

---

## Migration Path

Migration behavior:

| Scenario                               | Behavior                                                         |
|----------------------------------------|------------------------------------------------------------------|
| `just dev` (local, no env vars)        | `DATA_ROOT` = cwd, `APP_ROOT` = repo root. Identical to current. |
| Docker image (with `DEVBOX_DATA_ROOT`) | `DATA_ROOT` = env var, `APP_ROOT` = `/app`. Production mode.     |
| New config with `repos` list           | Used directly for multi-repo seeding.                            |

---

## Future Extensions

### Dynamic Groups
- API/command to create groups on the fly (e.g., from Telegram thread)
- Same persistent workspace model — seed on first use, persist across turns
- GC policy: inactivity timeout, size threshold, manual cleanup

### k8s-Native Container Runtime
- Replace Docker CLI spawning with k8s Jobs API
- Eliminates Docker socket mount and path alignment concerns
- Runners become k8s Jobs with PVC mounts
- Requires refactoring `container-runner.ts` to use `@kubernetes/client-node`

### Multi-Node Scheduling
- Move SQLite to PostgreSQL for shared state
- Use k8s node affinity or PV access modes for workspace locality
- Or: NFS/shared filesystem for workspace data
