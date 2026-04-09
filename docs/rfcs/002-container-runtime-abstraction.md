# RFC 002: Container Runtime Abstraction

## Status

Draft

## Problem Statement

The devbox agent controller currently depends on Docker CLI (`docker run`) and host-path bind mounts. This works on local machines and self-managed nodes, but blocks deployment to managed Kubernetes platforms (for example GKE Autopilot) where Docker socket access and arbitrary host paths are not available.

Today, the controller and runner exchange:

- Initial input and streamed results via process `stdin/stdout`
- Follow-up messages and control signals via filesystem IPC (`/data/.../ipc/...`)

The `stdin/stdout` dependency forces Kubernetes-specific stream attach behavior (exec/websocket), which adds failure modes and complexity.

### Current coupling to Docker

The main Docker touch points are in `src/container-runtime.ts` and `src/container-runner.ts`:

- Docker binary selection and health checks
- `docker run` argument assembly
- `docker stop` lifecycle handling

## Decisions in this RFC

1. Introduce a runtime abstraction so Docker and Kubernetes share the same controller flow.
2. Make **file protocol** (shared filesystem) the primary transport for runner input/output in both runtimes.
3. Drop local seed repo sources (only remote git sources are supported).
4. Drop SSH key mount-based cloning (`workspace.ssh_dir` path); use token-based HTTPS auth for GitHub seeding.

---

## Design

### Runtime Interface

```typescript
interface ContainerSpawnConfig {
  name: string;
  image: string;
  mounts: RuntimeMount[];
  env: Record<string, string>;
  user?: string; // e.g. "1000:1000" in Docker mode
}

interface ContainerHandle {
  id: string; // Docker container name or K8s pod name
  waitForExit(): Promise<{ code: number | null }>;
  stop(): Promise<void>;
}

interface ContainerRuntime {
  ensureRunning(): Promise<void>;
  cleanupOrphans(): Promise<void>;
  spawn(config: ContainerSpawnConfig): Promise<ContainerHandle>;
}
```

Key simplification: runtime abstraction manages **process lifecycle only**. It does not expose `stdin/stdout` streams.

### File Protocol (Primary Transport)

The controller and runner communicate through files on shared storage (same mechanism family as current IPC polling).

For each run, controller creates a run directory, for example:

```
/data/devbox-agent/data/ipc/<agent>/runs/<runId>/
  input.json
  out/
  done.json         # written by runner at completion
```

Flow:

1. Controller writes `input.json` containing the current `ContainerInput` payload.
2. Runtime starts runner container/pod with env vars pointing to `runId` (or input path).
3. Runner reads `input.json` at startup instead of reading from stdin.
4. Runner writes each output event as ordered JSON files under `out/` (for example `000001.json`).
5. Runner writes `done.json` when exiting normally (or error payload if failed).
6. Controller polls `out/` and `done.json` and drives existing queue/session behavior.

This is a natural extension of existing file-based IPC already used for follow-up messages and `_close` sentinel files.

### DockerRuntime

Docker mode remains available for local/self-managed deployment:

- `spawn()` uses `docker run` with mounts/env/user config
- `stop()` maps to `docker stop`
- `cleanupOrphans()` maps to filtered `docker ps` + stop

Transport no longer depends on container stdio markers.

### K8sRuntime

Uses `@kubernetes/client-node` to manage runner Pods:

1. Create pod from `ContainerSpawnConfig`
2. Wait for Running
3. Let runner read/write files on shared PVC
4. Wait for pod completion, or stop by deleting pod

No `pods/exec` stream attach is required.

### Volume Strategy

Controller and runner share one RWX PVC (`devbox-data`), mounted at the same base path.

Required shared paths:

- `data/sessions/{name}/{sessionScopeKey}/` -> runner `/session` (read-only metadata)
- `data/sessions/{name}/{sessionScopeKey}/workspace/` -> runner `/workspace`
- `agents/global/` -> runner `/workspace/global` (read-only)
- `data/sessions/{name}/{sessionScopeKey}/.claude/` -> runner `/home/devbox/.claude`
- `data/sessions/{name}/{sessionScopeKey}/ipc/` -> runner `/ipc`

### Seeding/Auth Constraints (Intentional Simplification)

To keep runtime mounts portable:

- `seed.yaml` repo `source` must be remote (`https://`, `ssh://`, `git@`, `git://`).
- Local filesystem sources are rejected.
- SSH key mount bootstrap (`workspace.ssh_dir` -> `/workspace/bootstrap/ssh`) is removed.
- GitHub repo auth uses token-based HTTPS rewriting (GitHub App installation tokens).

These constraints remove non-portable host-path assumptions and simplify Kubernetes parity.

### Runtime Selection

Configured at startup:

```yaml
container:
  runtime: docker # "docker" | "kubernetes"
  image: devbox-runner:latest
  kubernetes:
    namespace: devbox-agent
    kubeconfig: ~/.kube/your-cluster.yaml # optional; in-cluster by default
    pvc_name: devbox-data
    data_mount_path: /data/devbox-agent
    service_account: devbox-runner
```

Default remains `docker` when omitted.

---

## Architecture

### Docker Mode

```
Controller
  -> writes run/input.json on shared data path
  -> docker run runner container
Runner
  -> reads run/input.json
  -> writes run/out/*.json + run/done.json
Controller
  -> polls run/out + done, handles outputs, session updates, and cleanup
```

### Kubernetes Mode

```
Controller Pod (mounted RWX PVC)
  -> writes run/input.json
  -> creates runner Pod via K8s API

Runner Pod (same RWX PVC)
  -> reads run/input.json
  -> writes run/out/*.json + run/done.json

Controller Pod
  -> polls run/out + done.json
  -> deletes Pod on timeout/cancel
```

Both modes share the same transport semantics.

### RBAC

Controller service account needs:

```yaml
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["create", "get", "list", "watch", "delete"]
```

`pods/exec` is not required in this design.

---

## What Changes and What Doesn't

### Unchanged

- Session queue model and per-session concurrency behavior
- Filesystem IPC model for follow-up messages (`input/*.json`, `_close`)
- Container input/output payload schema (`ContainerInput` / `ContainerOutput` fields)
- Shared PVC strategy for controller + runner in Kubernetes mode

### Changed

| Component | Change |
|---|---|
| `src/container-runtime.ts` | Converted to runtime interface + `DockerRuntime` implementation |
| New `src/k8s-runtime.ts` | Kubernetes implementation for pod lifecycle |
| `src/container-runner.ts` | Uses runtime handle lifecycle + file-protocol polling instead of stdio parsing |
| `container/entrypoint.sh` + runner startup | Read initial input from file path instead of stdin |
| runner output path | Write ordered output files + completion file instead of stdout marker stream |
| `src/config.ts` | Add runtime selector + kubernetes settings; remove SSH seeding settings |
| seed validation | Reject local source paths |
| K8s manifests | Replace Docker socket/hostPath assumptions with PVC + SA/RBAC |

---

## Phases

### Phase 1: Extract runtime lifecycle interface

1. Introduce `ContainerRuntime` + `ContainerHandle`
2. Implement `DockerRuntime` without behavior changes
3. Inject runtime into controller and scheduler call paths

Validation: existing Docker deployment still works.

### Phase 2: File protocol in Docker mode

1. Add run directory contract (`input.json`, `out/*.json`, `done.json`)
2. Update runner startup to read initial input from file
3. Update controller to poll file outputs instead of stdout markers
4. Keep follow-up IPC (`input/*.json`, `_close`) unchanged

Validation: Docker mode end-to-end parity with current behavior.

### Phase 3: K8sRuntime + storage/manifests

1. Implement pod create/wait/delete runtime
2. Add PVC-backed deployment and SA/RBAC
3. Remove Docker socket dependency from manifests

Validation: GKE Autopilot E2E path works (message -> runner pod -> response).

### Phase 4: Seeding/auth simplification rollout

1. Reject local repo sources in seed validation
2. Remove `workspace.ssh_dir` support and bootstrap copy logic
3. Ensure GitHub App token seeding remains functional
4. Update docs/config examples accordingly

Validation: remote GitHub seed repos clone successfully without SSH key mounts.

---

## Alternatives Considered

### Attach-to-main-process (stdio attach)

Attach to container/pod process streams and preserve stdin/stdout marker protocol.

Pros:
- Smaller runner protocol changes

Cons:
- Kubernetes stream attach introduces websocket/exec lifecycle complexity
- More difficult recovery semantics on attach disconnects
- Requires broader RBAC (`pods/exec`)

Decision: rejected for primary path; file protocol is simpler and aligns with existing IPC pattern.

---

## Future Extensions (out of scope)

- Pod template overrides per agent (resources, node selectors, tolerations)
- Warm pod reuse/pooling to reduce cold starts
- Multi-cluster runtime routing
