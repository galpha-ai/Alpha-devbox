# Architecture

Devbox Agent is a self-hosted system that runs AI coding agents in isolated container sandboxes, triggered by chat messages (Telegram, Slack, Web) or API calls. Each agent type has its own repos, instructions, and skills. Each chat context gets its own sandbox with persistent workspace and conversation state.

The system is structured around three core concepts: **Agents** (what to run), **Sessions** (conversation state), and **Sandboxes** (runtime environment). See `docs/rfcs/001-agent-sandbox-architecture.md` for the design rationale.

## Two-Process Model

The system runs as two processes that never share memory:

```
Controller (long-lived)                  Runner (long-lived container per session)
────────────────────────                 ────────────────────────────────────────
Receives chat messages                   Executes Claude Code SDK via query()
Routes to sessions                       Reads/writes workspace repos
Spawns one container per session         Writes output events to run files
Manages concurrency + lifecycle          Blocks between turns, polls IPC for messages
Persists state in SQLite                 Archives conversations on compaction
```

The **controller** is a Node.js process that runs indefinitely. It connects to chat platforms, stores messages, manages session state, and spawns containers for agent execution.

The **runner** is a Node.js process inside a container that stays alive across multiple turns within a session. It invokes the Claude Code SDK via `query()`, which accepts a `MessageStream` (async iterable) -- follow-up messages are pushed into the stream mid-query via IPC files. Between queries, the runner blocks in `waitForIpcMessage()` polling for the next IPC message, then starts a new `query()` with `resume: sessionId` to continue the conversation. The container only exits when the controller writes a `_close` sentinel (on idle timeout or shutdown). The bind-mounted workspace persists across container restarts.

## Codemap

### Controller (`src/`)

- `index.ts`: Entry point. Loads config, connects channels, starts the message loop, scheduler, and IPC watcher, then orchestrates message processing and container execution.
  It also owns stale-session recovery: if the runner reports that a persisted Claude session can no longer be resumed, the controller clears the saved session ID and replays pending messages without retry backoff.
- `config.ts`: Parses `config.yaml` via Zod, resolves agent definitions and channel bindings, and exports runtime constants such as `DATA_ROOT`, `CONTAINER_RUNTIME`, `CONTAINER_IMAGE`, and `MAX_CONCURRENT_CONTAINERS`.
- `db.ts`: SQLite persistence via better-sqlite3. Owns the `messages`, `chats`, `sessions`, `agents`, `scheduled_tasks`, `task_run_logs`, and `router_state` tables and handles schema migrations from legacy formats. `messages` rows now also carry `ui_message_json`, a persisted canonical `UIMessage` projection used by web/replay reads when available. The canonical projection is text-only; legacy structured parts are folded back into markdown/text during read normalization.
- `container-runner.ts`: Builds session-scoped volume mounts, agent-declared secret mounts, seed manifests, run directories, and runtime spawn config. Writes run `input.json`, polls run `out/*.json` and `done.json`, streams parsed `ContainerOutput` events back into controller flow, and manages GitHub App token exchange for repo seeding.
- `container-runtime.ts`: Runtime lifecycle abstraction (`ContainerRuntime` / `ContainerHandle`) with `DockerRuntime` and `K8sRuntime` implementations. Handles runtime health checks, orphan cleanup, bind mounts for Docker, and PVC/Secret volume wiring for Kubernetes Pods.
- `session-queue.ts`: Concurrency control. Enforces `MAX_CONCURRENT_CONTAINERS` globally, queues messages and tasks per session, handles retry with exponential backoff, and pipes follow-up messages to active containers via session-scoped IPC files.
- `session-gc.ts`: Garbage collection for stale thread-scoped session directories. Provides `touchSessionHeartbeat()` (called by `container-runner.ts` and `session-queue.ts`) and `startSessionGc()` for the periodic sweep loop.
- `ipc.ts`: Filesystem-based IPC watcher. Polls `data/sessions/{agentName}/{sessionScopeKey}/ipc/messages/` and `tasks/` directories, processes outbound messages and task scheduling, and enforces authorization by session directory identity.
- `router.ts`: Message formatting for agent input (XML) and outbound filtering that strips `<internal>` tags. Resolves which channel owns a given JID.
- `session-control.ts`: Parses the `/done` and `/reset` session control commands. Performs dirty-workspace detection for `/done`, explicit runner shutdown, session ID clearing, and session directory cleanup before replying to the user.
- `task-scheduler.ts`: Polls SQLite for due scheduled tasks (cron, interval, once), spawns containers to execute them, and logs run history.
- `agent-folder.ts`: Path validation and resolution. Prevents directory traversal and validates agent name format (`^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$`).
- `channels/telegram.ts`: Telegram adapter using grammy. Handles group and DM detection, `@mention` normalization, non-text message placeholders, and the `Channel` interface.
- `channels/web.ts`: Web adapter using plain HTTP. Serves the backend canonical `UIMessage[]` read endpoint for web chat, and exposes the AI SDK-compatible streaming endpoint (`POST /api/devbox/chat`) that maps controller `sendMessage` / `setTyping` callbacks directly into SSE UI message chunks. The live web write path accepts a **last-message-only** submit body (`{ id, message }`) from the AI SDK transport instead of full client history; prior canonical history is persisted server-side. Canonical reads lazily upgrade legacy rows by writing back the normalized `ui_message_json` projection when older rows are encountered for live conversations; replay reads stay read-only. Auth is delegated to the upstream Envoy proxy (`X-User-Id` header). Implements the `Channel` interface without DB polling or reply-stability heuristics; normalization stays server-side.
- `../frontend/`: Minimal browser chat workspace for the web channel. Uses a client-generated UUID sent as `X-User-Id`, renders and streams chat turns through `@ai-sdk/react` + the AI SDK transport, and reads the backend canonical `UIMessage[]` for web chat. The transport uses `prepareSendMessagesRequest` to submit only the latest message plus conversation id; it does not resend full client history on the main path. Live chat identity is route-backed: `/` is the starter/new entry, `/chat/:conversationId` is the canonical live conversation URL, and `/replay/:replayId` is the read-only replay route. Transcript rendering stays on a single markdown/text surface and delegates chart/table rendering to `@galpha-ai/better-markdown`. Voice input now uses the official AI Voice Elements `SpeechInput` component and still reuses the normal text send path.
- `replay_links` + `/api/devbox/replays/:replayId/ui-messages`: replay-only bridge for Telegram/Slack threads. Replay ids are opaque public identifiers for a stored `(channelId, threadId, agentName)` scope and are consumed by the frontend route `/replay/:replayId?reply=<dbMessageId>`.

### Runner (`container/`)

- `agent-runner/src/index.ts`: In-container entry point. Reads `ContainerInput` from run `input.json`, invokes Claude Code SDK via `query()`, polls IPC for follow-up messages using `MessageStream`, writes ordered run output files and `done.json`, archives transcripts on compaction, and sanitizes Bash tool invocations to strip secrets from subprocess env.
- `agent-runner/src/error-logging.ts`: Shared runner helper for secret-safe error serialization and log formatting. Keeps SDK error payload sanitization separate from query loop control flow.
- `agent-runner/src/ipc-mcp-stdio.ts`: MCP server exposed to Claude Code inside the container. Provides tools for sending messages and scheduling tasks.
- `entrypoint.sh`: Container initialization. Reads the seed manifest from `/session`, seeds `/workspace` via git clone (gated by `.seeded`), reads seed auth secrets from run `input.json`, persists per-owner GitHub tokens for `gh`, and then launches agent-runner.
- `gh-wrapper.sh`: Wrapper installed as `/usr/local/bin/gh`. Resolves the target repo owner from `--repo`, `GH_REPO`, or `git remote origin`, swaps in the matching GitHub App token, and delegates to the packaged GitHub CLI.
- `skills/`: Shared Claude Code skills available to all agents, copied into each agent's `.claude/skills/` on container setup.

### Agent Definitions (`agents/`)

Each agent is a directory containing:

- `CLAUDE.md` (required): Agent instructions and persona.
- `seed.yaml` (required): Agent seed metadata, including:
  - `repos:` sandbox repos (`name`, `source`, `ref`; `source` must be a remote git URL)
  - `image:` (optional) runner image override
  - `model:` (optional) Claude model selection (`"sonnet"`, `"opus"`, `"haiku"`, or full model name)
  - `thinking:` (optional) thinking configuration (`type: adaptive|enabled|disabled`, optional `budgetTokens`)
  - `effort:` (optional) effort level (`"low"`, `"medium"`, `"high"`, `"max"`)
  - `secretMounts:` (optional) static file mounts (e.g., kubeconfigs)
- `skills/` (optional): Agent-specific Claude Code skills that override shared ones.

## Key Types

- `Channel` (`types.ts`) -- interface for chat platform adapters. Methods: `connect()`, `sendMessage()`, `ownsJid()`, `setTyping()`.
- `RegisteredAgent` (`types.ts`) -- an agent bound to a channel. Fields: `name`, `agentName`, `trigger`, `requiresTrigger`.
- `SessionScope` (`session-scope.ts`) -- composite key `(channelId, threadId, agentName)` identifying a session. Serialized as `"channelId::threadId::agentName"` by `makeSessionScopeKey()`.
- `ContainerInput` / `ContainerOutput` (`container-runner.ts`) -- the contract between controller and runner. Input written to run `input.json`; output consumed from ordered run `out/*.json` files.
- `SessionQueue` (`session-queue.ts`) -- manages container lifecycle per session. Tracks active/idle state, pending messages, pending tasks.

## Data Layout

```
DATA_ROOT/                          (configurable, default: cwd or /data/devbox-agent)
  store/messages.db                 SQLite: all persistent state
  agents/{name}/                    Per-agent runtime directory
    logs/                           Container run logs
  agents/global/CLAUDE.md           Shared instructions (mounted as /workspace/global, read-only)
  data/
    sessions/{agentName}/{sessionScopeKey}/
      _last_activity                Heartbeat file (mtime = last activity, used by GC)
      CLAUDE.md                     Session copy of agent instructions
      AGENTS.md                     Optional session copy of agent instructions for non-Claude tooling
      seed-manifest.json            Generated repo list for entrypoint.sh
      workspace/                    Git repos plus working instruction files for this channel/thread scope (.seeded lives here)
      .claude/                      Claude Code state (settings, skills, memory)
      ipc/
        input/                      Controller -> Runner messages (JSON files, consumed on read)
        messages/                   Runner -> Controller outbound messages
        tasks/                      Runner -> Controller task operations
        runs/{runId}/
          input.json                Initial ContainerInput payload for a run
          out/*.json                Ordered ContainerOutput events
          done.json                 Run completion marker
```

## Container Mount Map

When the controller spawns a runner container, it bind-mounts these paths:

| Host path                                                | Container path         | Mode | Purpose                                                                  |
| -------------------------------------------------------- | ---------------------- | ---- | ------------------------------------------------------------------------ |
| `data/sessions/{agentName}/{sessionScopeKey}/`           | `/session`             | RO   | Session metadata root (`seed-manifest.json`, session instruction source) |
| `data/sessions/{agentName}/{sessionScopeKey}/workspace/` | `/workspace`           | RW   | Editable repo checkout root and agent cwd                                |
| `agents/global/`                                         | `/workspace/global`    | RO   | Shared global instructions                                               |
| `data/sessions/{agentName}/{sessionScopeKey}/.claude/`   | `/home/devbox/.claude` | RW   | Claude Code state (session, skills, memory)                              |
| `data/sessions/{agentName}/{sessionScopeKey}/ipc/`       | `/ipc`                 | RW   | Bidirectional IPC for one channel/thread scope                           |

## Session Garbage Collection

Thread-scoped sessions accumulate on disk and in the database over time. A background GC sweep (`session-gc.ts`) reclaims stale ones:

- **Heartbeat file:** Each session root contains a `_last_activity` file whose mtime tracks the last meaningful activity. Touched when a container run starts (`container-runner.ts`) and when a follow-up message is piped (`session-queue.ts`). If the file is missing, the GC falls back to the session directory's own mtime.
- **Sweep loop:** Runs every 10 minutes via `setTimeout`. Enumerates `DATA_ROOT/data/sessions/{agentName}/{encodedSessionKey}/`.
- **Eligibility:** Only **thread-scoped** sessions (threadId is non-null) are candidates. Channel-scoped sessions are long-lived and never collected. Active sessions (container running) are always skipped.
- **TTL:** 6 hours since last heartbeat.
- **Cleanup:** Removes the session directory (`rm -rf`), deletes the DB row from the `sessions` table, and clears in-memory state (`sessions`, `lastAgentTimestamp`).
- **Follow-up to GC'd session:** If a message targets a thread whose session directory no longer exists but the controller still has persisted state for that thread (saved session ID or last processed cursor), it replies with an error asking the user to start a new thread and cleans up any remaining in-memory state. A missing directory with no persisted state is treated as a brand-new thread and initializes a fresh session.

## Startup Recovery

When the controller boots, it performs a recovery scan for interrupted user work before starting the main message loop:

- **Scope discovery:** It checks every registered channel scope plus any scope with a persisted session ID or `lastAgentTimestamp`.
- **Recovery unit:** It only recovers **unreplied user-message deltas** after the saved `lastAgentTimestamp`. Bot messages never count as pending work.
- **Thread bootstrap context:** For a brand-new thread with no saved session state, the recovery payload includes the thread's parent/root message once so the first turn has the thread title/context. For resumed thread sessions, the parent/root message is not re-sent.
- **Freshness limit:** Pending work older than 6 hours is considered stale and is not auto-recovered. The controller waits for the user to re-engage instead of reviving old work on boot.
- **Conservative policy:** Recovery prefers silence over duplicate completions. If there is no unreplied user message delta, startup does nothing for that scope.
- **Observability:** When recovery finds recent pending work, the controller logs structured per-message summaries (message ID, sender, timestamp, truncated content preview) and marks thread parent bootstrap entries separately.

## Architectural Invariants

1. **Containers are long-lived per session; volumes outlive containers.** A container is spawned on the first message and stays alive across turns, blocking between queries. It exits only when the controller writes a `_close` sentinel (idle timeout or shutdown). The workspace, Claude state, and IPC directories are bind-mounted and persist even if the container is killed and a new one spawned for the same session.

2. **Controller never executes agent logic.** All Claude Code invocation happens inside runner containers. The controller only routes messages, manages state, and spawns containers.

3. **IPC identity is directory-based.** A runner's identity is determined by which `sessions/{agentName}/{sessionScopeKey}/ipc/` directory it writes to. Authorization checks in `ipc.ts` use the session directory scope, not any token or credential.

4. **Session key is a composite triple.** Every session is identified by `(channelId, threadId, agentName)`. This enables: thread isolation, DM support, and future multi-agent per channel.

5. **One active container per session at a time.** `SessionQueue` ensures no two containers run concurrently for the same session key. Follow-up messages are either piped to the active container via IPC or queued until it exits.

6. **Initial payload uses run files; follow-ups use IPC files.** Controller writes `ContainerInput` (including transient secrets) to `sessions/{agentName}/{sessionScopeKey}/ipc/runs/{runId}/input.json`; runner reads it via `/ipc/runs/{runId}/input.json`, writes run outputs to `out/*.json`, and writes `done.json`. Follow-up turns still flow via `sessions/{agentName}/{sessionScopeKey}/ipc/input/*.json` and `_close`.

7. **Agent definitions are read-only templates.** The `agents/{name}/` directory under the source tree (or config path) is the template. Runtime session state goes under `DATA_ROOT/data/sessions/{agentName}/{sessionScopeKey}/`. The controller syncs instruction files into the session root and materializes working copies in `workspace/` so the agent can start from `/workspace`.

8. **Global concurrency is capped.** `MAX_CONCURRENT_CONTAINERS` (default: 2) limits how many containers run simultaneously across all sessions. Excess work is queued in `SessionQueue.waitingSessions`.

9. **Thread parent messages are bootstrap-only context.** The controller includes a thread's root message when activating a brand-new thread session, but resumed turns and startup recovery for existing sessions send only unread user-message deltas.

10. **Replay identity is distinct from live web identity.** Replay pages use opaque `replayId` values backed by `replay_links`; they do not depend on or mutate the live `web:<userId>` conversation/session model.

11. **Live web conversation identity is route-backed.** The active live conversation is selected by the browser route (`/chat/:conversationId`), while `/` remains a starter/new state. The frontend may hold transient stream state, but route identity is the product-level source of truth for which conversation is open.

12. **Canonical UI projection is persisted at the message row.** Each stored message may carry `ui_message_json`, a canonical `UIMessage` projection. Web/replay canonical reads prefer this projection over fallback derivation from raw `content`, and live conversation reads lazily write back the normalized projection when legacy rows are encountered. The canonical projection intentionally stays text-only so chart/report rendering remains a better-markdown concern rather than a second structured-renderer system.

## Boundaries

### Controller <-> Runner

- **Inbound:** Controller writes `ContainerInput` JSON to `sessions/{agentName}/{sessionScopeKey}/ipc/runs/{runId}/input.json` and starts the runner with `DEVBOX_RUN_DIR=/ipc/runs/{runId}`. Follow-up messages are written as JSON files to `sessions/{agentName}/{sessionScopeKey}/ipc/input/`. The `_close` sentinel signals the runner to exit.
- **Outbound:** Runner writes ordered `ContainerOutput` events to `sessions/{agentName}/{sessionScopeKey}/ipc/runs/{runId}/out/*.json` and writes `done.json` on completion. Runner writes outbound chat messages as JSON files to `sessions/{agentName}/{sessionScopeKey}/ipc/messages/`.

### Controller <-> Chat Platforms

- **Inbound:** Channel adapters receive messages and call `onMessage(chatJid, msg)` / `onChatMetadata(...)`. Messages are stored in SQLite. The message loop polls for new messages and routes them by JID to the correct session.
- **Outbound:** Controller calls `channel.sendMessage(jid, text)`. The `router.ts` module strips `<internal>` tags before delivery.

### Controller <-> SQLite

All persistent state flows through `db.ts`. The database is the source of truth for sessions, registered agents, messages, scheduled tasks, and router cursors. State is loaded into memory at startup (`loadState()`) and persisted on mutation (`saveState()`).

## Config Structure

```yaml
assistant_name: 'Devbox' # Bot display name and trigger prefix
telegram_bot_token: '...' # Or via TELEGRAM_BOT_TOKEN env var
data_root: '/data/devbox-agent' # Or via DEVBOX_DATA_ROOT env var

container:
  runtime: 'docker' # "docker" | "kubernetes"
  image: 'devbox-runner:latest'
  timeout: 5400000 # Hard timeout per container (ms)
  idle_timeout: 300000 # Idle period before writing _close sentinel (ms)
  max_concurrent: 2 # Global container concurrency limit
  kubernetes:
    namespace: 'devbox-agent'
    kubeconfig: '~/.kube/config' # Optional (in-cluster config when omitted)
    pvc_name: 'devbox-data' # Shared RWX PVC used by controller + runner pods
    data_mount_path: '/data/devbox-agent'
    service_account: 'devbox-runner'
    image_pull_policy: 'IfNotPresent'

web:
  enabled: true
  port: 8080 # HTTP listen port

agents:
  - name: main
    path: agents/main # Relative to config dir or APP_ROOT

channels:
  - id: 'tg:-1001234567890' # Telegram group
    agents:
      - name: main
        trigger: '@Devbox'
        requires_trigger: true
  - id: 'tg:user:*' # Telegram DM wildcard
    agents:
      - name: main
        requires_trigger: false
  - id: 'web:*' # Web chat wildcard
    agents:
      - name: main
        requires_trigger: false
```

See `config.ts` ConfigSchema for the full Zod schema.
