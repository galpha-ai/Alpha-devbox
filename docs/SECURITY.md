# Devbox Agent Security Model

This document describes the security model implemented by Devbox Agent today.

Devbox Agent runs AI coding agents inside isolated runner containers. The controller process receives chat messages, manages session state, and provisions runner containers with explicit mounts and scoped secrets. The main security goal is to contain agent execution to a single session sandbox and prevent one session from affecting another.

## Trust Model

| Entity | Trust Level | Notes |
|--------|-------------|-------|
| Chat messages and uploaded content | Untrusted input | May contain prompt injection, malicious instructions, or harmful file content |
| Seeded repos and workspace files | Untrusted input | Agent-readable code and docs can also contain prompt injection or hostile commands |
| Controller process | Trusted | Enforces routing, session isolation, mount construction, IPC authorization, and secret scoping |
| Runner container | Sandboxed, but not trusted | The agent may execute arbitrary commands inside its sandbox using any access intentionally granted to that session |
| External services | Partially trusted | GitHub, Telegram, Slack, Anthropic, and Kubernetes provide infrastructure, not policy enforcement |

## Primary Security Boundaries

### 1. Container Boundary

Agent execution happens inside a runner container rather than in the controller process. The controller does not execute agent logic directly. The container boundary limits filesystem visibility to explicitly mounted paths and isolates agent processes from the controller host process.

This is the primary containment boundary, but it is not sufficient by itself. The effective access of a runner is determined by the mounts, secrets, and network access granted to that session.

### 2. Session Boundary

Each session is identified by the triple `(channelId, threadId, agentName)`. Every session gets its own on-disk state under:

```text
data/sessions/{agentName}/{sessionScopeKey}/
```

**Kubernetes & GCP Access (SA-based):**

Runner pods access the cluster and GCP without mounting credential files.
Instead, the `devbox-runner` ServiceAccount provides identity:

- **kubectl**: Uses in-cluster SA token (auto-mounted by kubelet). Permissions
  are controlled by a `ClusterRole` / `ClusterRoleBinding` bound to the SA.
- **gcloud**: Uses GKE Workload Identity. The k8s SA is annotated with a GCP SA,
  allowing `gcloud` and ADC-aware tools to authenticate without key files.

This keeps `.kube` and `.gcloud` on the blocked list — no credential files
are ever mounted into runner containers.

**Protections:**
- Symlink resolution before validation (prevents traversal attacks)
- Container path validation (rejects `..` and absolute paths)
- `nonMainReadOnly` option forces read-only for non-main groups

- editable workspace contents
- Claude conversation state and memory
- IPC directories

This prevents one session from reading or writing another session's workspace or conversation state through normal runner access.

### 3. Controller <-> Runner Boundary

The controller and runner are separate long-lived processes that do not share memory.

- The controller writes run input files and follow-up IPC messages.
- The runner reads only the files mounted into its own session sandbox.
- The runner returns output by writing run output files and outbound IPC messages.

The controller remains the enforcement point for routing, state persistence, authorization checks, and container lifecycle.

### 4. IPC Authorization Boundary

IPC authorization is based on session directory identity.

- A runner can only send messages back to the same channel and thread scope that owns its IPC directory.
- A runner can only create, pause, resume, or cancel tasks for its own agent scope.
- There is no privileged "main group" or cross-chat bypass in the current model.

If a runner writes an IPC message or task operation that targets a different scope, the controller rejects it.

## Filesystem and Mount Model

The controller constructs runner access by mounting specific host paths into the container:

| Host path | Container path | Mode | Purpose |
|-----------|----------------|------|---------|
| `data/sessions/{agentName}/{sessionScopeKey}/` | `/session` | read-only | Session metadata such as `seed-manifest.json` and instruction source files |
| `data/sessions/{agentName}/{sessionScopeKey}/workspace/` | `/workspace` | read-write | Editable repo checkout root and agent working directory |
| `agents/global/` | `/workspace/global` | read-only | Shared global instructions |
| `data/sessions/{agentName}/{sessionScopeKey}/.claude/` | `/home/devbox/.claude` | read-write | Session-scoped Claude state, skills, and memory |
| `data/sessions/{agentName}/{sessionScopeKey}/ipc/` | `/ipc` | read-write | Session-scoped controller/runner transport |

The model is explicit allow-by-construction. A runner can access only the paths mounted for that session plus any additional mounts declared for the agent.

### Optional Secret Mounts

Agents may declare static file mounts in `seed.yaml` via `secretMounts`.

These mounts are explicit per-agent exceptions for files such as kubeconfigs. They are mounted read-only into the runner. Because these files become visible inside the container, they must be treated as accessible to the agent.

## Secret and Credential Handling

Devbox Agent uses two secret delivery paths:

### 1. Per-run injected secrets

The controller writes selected per-run secrets into the run `input.json` payload under the session's IPC run directory. These secrets are available to the runner for that run.

This includes Claude/Anthropic credentials and, when repo seeding requires it, short-lived GitHub installation tokens.

### 2. Static mounted secrets

Long-lived file-based credentials can be exposed through `seed.yaml` `secretMounts`. This is intended for infrastructure files such as kubeconfigs.

### Bash subprocess sanitization

The runner strips selected secrets from Bash tool subprocess environments before commands run. This reduces accidental credential exposure in shell commands.

However, this is only a partial mitigation:

- secrets already visible as mounted files are still readable by the agent
- secrets needed by the runner itself may still be reachable from the runner process
- GitHub tokens are intentionally left available for `gh` workflows

### Security implication

If a secret is available inside the runner container, the agent may be able to discover or misuse it. The system reduces exposure by scoping and minimizing secrets, but it does not guarantee that in-container secrets are opaque to the agent.

## Messaging and Task Authorization

The controller validates outbound actions from runners before applying them.

### Outbound messages

The runner may emit outbound chat messages through IPC only for its own `(channelId, threadId)` scope.

### Task operations

The runner may schedule or manage tasks only for its own agent scope. It cannot manage tasks that belong to another agent.

### No privileged session

The current implementation does not grant any chat, agent, or session global administrative privileges through IPC.

## Network and External Access

Runner containers have network access unless the underlying runtime or deployment environment restricts it.

That means a runner may:

- call external APIs
- clone seeded repos
- access services reachable from its network environment

This is useful for coding workflows, but it increases the impact of prompt injection or credential misuse. Network policy should be enforced outside the application if stricter isolation is required.

## Isolation Guarantees

The system is designed to provide these guarantees:

- one session cannot directly access another session's workspace, Claude state, or IPC directory through normal mounted paths
- the controller, not the runner, decides which paths and secrets are exposed
- outbound messages are restricted to the runner's own chat/thread scope
- task management is restricted to the runner's own agent scope

## Non-Goals and Limits

The system does not guarantee:

- that secrets exposed inside the runner remain hidden from the agent
- that prompt injection from chat messages or repo content can be fully prevented
- that network access is restricted by default
- that a mounted infrastructure credential cannot be used by the agent

The security model assumes that the agent may execute arbitrary code within whatever access the controller intentionally grants.

## Residual Risks

The main residual risks are:

- prompt injection from chat content, code, docs, or generated files
- over-broad `secretMounts` that expose sensitive infrastructure credentials
- misuse of in-container credentials by the agent
- data exfiltration over unrestricted network access
- persistence of sensitive material in long-lived session workspaces or Claude state

## Operational Guidance

To reduce risk:

- keep `seed.yaml` repo lists and `secretMounts` minimal
- prefer short-lived credentials over long-lived static secrets
- treat any secret visible inside the runner as potentially accessible to the agent
- avoid mounting broad host directories when a narrow file or directory is sufficient
- clean up stale sessions and workspaces when they are no longer needed
- review agent instructions carefully, especially around shell usage, GitHub access, and infrastructure operations
