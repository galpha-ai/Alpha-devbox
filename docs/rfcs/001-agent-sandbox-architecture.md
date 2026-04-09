# RFC 001: Agent-Sandbox Architecture

## Status

Draft

## Problem Statement

The company has dozens of microservices across multiple repos. Developers spend significant effort building context when working on tasks — cloning repos, understanding codebases, tracing cross-service dependencies. The goal is a **devbox agent** that lives in a well-prepared environment (all repos checked out, instruction files at root) and assists developers via chat (Slack, Telegram).

### Interaction model

Developers mention the agent in a thread with task requirements. Each thread becomes a parallel agent task with its own sandbox. Follow-up conversation happens in the same thread. The agent reads instructions from the environment, works on the task, and can create PRs, run tests, or produce analysis.

### Success metrics

- 20–50% of PRs drafted by the agent
- Engineers shift mindset from "doing the work" to "improving the environment for the agent" (better CLAUDE.md, better seed configs, better skills)

### Why the current architecture doesn't fit

The initial codebase was designed for a **personal assistant** model:

- A small number of **static groups** defined in `config.yaml`, each mapped 1:1 to a Telegram chat
- One shared workspace per group, reused across all messages
- Single `CLAUDE.md` persona optimized for personal assistant tasks (WhatsApp/Telegram formatting, memory management, casual conversation)
- Telegram-only channel adapter
- Session key is `group.folder` — no concept of threads or parallel tasks within a group
- Concurrency limited to `max_concurrent` containers globally, no per-context isolation

The target model requires:

- **Dynamic creation** of sandboxes when threads are opened
- **Parallel execution** — multiple threads = multiple sandboxes running concurrently
- **Multi-channel support** — Slack (primary for dev teams) + Telegram
- **Development-focused personas** — code review, PR creation, test execution
- **Thread-scoped sessions** — each thread gets its own Claude conversation state and workspace
- **Lifecycle management** — GC of idle thread sandboxes

---

## Core Concepts

The current system has one concept — **group** — that conflates three concerns: the agent's identity/instructions, the chat context, and the runtime environment. The new model separates these into three distinct concepts.

### Agent (replaces "group" as a template concept)

A self-contained directory defining a **type** of agent. Not bound to any chat channel — purely a definition.

Required:
- `CLAUDE.md` — agent instructions and persona
- `seed.yaml` — repos to clone, environment setup

Optional:
- `skills/` — custom Claude Code skills
- Future: `subagents/`, `hooks/`, `tools/`

Example agents:
- `agents/quant-research/` — works on service-a, service-b, service-c
- `agents/service-c/` — works on service-c, infra DAG configs
- `agents/infra/` — works on k8s manifests, deployment configs

### Session

The binding between a **chat context** and a **sandbox**. Tracks Claude conversation state (session ID, memory) and maps chat messages to the correct sandbox.

Key: `(channel_id, thread_id, agent_name)`

Lifecycle varies by context:
- **Persistent** for channels and DMs — long-lived shared context
- **Ephemeral** for threads — created on first mention, GC-able after inactivity

### Sandbox

A runtime instance: a directory on the host, bind-mounted into ephemeral containers.

- Seeded from an agent definition (CLAUDE.md copied, repos cloned, skills installed)
- Owned by exactly one session
- Container is ephemeral per turn; the **volume persists** across turns within a session
- Contains the workspace (repo checkouts), Claude state (.claude/), and IPC channels

### Relationships

```
Agent (1) ──seeds──> (N) Sandbox
Session (1) ──owns──> (1) Sandbox
Chat context + Agent ──maps to──> (1) Session
```

### Session key mapping

| Context              | Session key                           | Lifecycle  |
|----------------------|---------------------------------------|------------|
| DM                   | `(user_id, null, agent)`              | persistent |
| Channel (non-thread) | `(channel_id, null, agent)`           | persistent |
| Thread               | `(channel_id, thread_id, agent)`      | ephemeral  |

This design enables multi-agent per channel (Phase 4) — the `agent` component of the key means two different agents can each have their own session/sandbox within the same thread.

---

## High-Level Architecture

### Current state (Devbox Agent)

```
┌─────────────────────────────────────────────────────────┐
│ Controller (long-lived process)                         │
│                                                         │
│  Telegram Bot ──> Message Router ──> Group Queue        │
│                   (static JID      (one queue per       │
│                    lookup)          config group)        │
│                                         │               │
│                                         ▼               │
│                                   Container Runner      │
│                                   (spawn per turn)      │
└──────────────────────────────┬──────────────────────────┘
                               │ docker run
                               ▼
                    ┌──────────────────────┐
                    │ Runner Container     │
                    │ (ephemeral)          │
                    │                      │
                    │ Claude Code SDK      │
                    │ + agent-runner       │
                    │ + MCP server         │
                    │                      │
                    │ Mounts:              │
                    │  /workspace/group    │
                    │  /workspace/global   │
                    │  /home/devbox/.claude│
                    │  /workspace/ipc      │
                    └──────────────────────┘
```

Key characteristics of the current system:

- **Controller/Runner two-process model** — controller is long-lived, runners are ephemeral containers spawned per turn. This model is sound and preserved.
- **Static groups** — defined in `config.yaml` as `groups:` array, each with a `jid`, `name`, `folder`. Loaded at startup, never change at runtime.
- **Single workspace per group** — `groups/{folder}/workspace/` is seeded once (`.seeded` marker) and reused for all messages in that group. No isolation between conversations.
- **Telegram-only** — single `TelegramChannel` adapter implementing the `Channel` interface.
- **Personal assistant persona** — CLAUDE.md instructs the agent to use WhatsApp/Telegram formatting, manage personal memory, handle casual conversation.
- **Global concurrency limit** — `max_concurrent` containers across all groups. No per-session or per-agent limits.
- **Session key = group folder** — `sessions` table maps `group_folder → session_id`. No support for multiple sessions within a group.
- **IPC via filesystem** — controller writes messages to `/workspace/ipc/input/`, runner polls and processes them. `_close` sentinel triggers graceful shutdown.

### Target state

```
┌──────────────────────────────────────────────────────────────┐
│ Controller (long-lived process)                              │
│                                                              │
│  ┌──────────┐  ┌──────────┐                                  │
│  │ Telegram  │  │  Slack   │  ... (future channels)          │
│  │ Adapter   │  │ Adapter  │                                  │
│  └────┬──────┘  └────┬─────┘                                  │
│       │              │                                        │
│       ▼              ▼                                        │
│  ┌────────────────────────────┐                               │
│  │ Orchestrator               │                               │
│  │                            │                               │
│  │ • Route message to session │                               │
│  │ • Create session/sandbox   │                               │
│  │   on first message         │                               │
│  │ • Resolve agent from       │                               │
│  │   channel config           │                               │
│  │ • GC idle thread sandboxes │                               │
│  └─────────────┬──────────────┘                               │
│                │                                              │
│                ▼                                              │
│  ┌──────────────────────────┐                                 │
│  │ Sandbox Manager          │                                 │
│  │                          │                                 │
│  │ • Seed from agent defn   │                                 │
│  │ • Mount into container   │                                 │
│  │ • Track lifecycle        │                                 │
│  └─────────────┬────────────┘                                 │
│                │ docker run                                   │
└────────────────┼──────────────────────────────────────────────┘
                 │
      ┌──────────┴──────────────┐
      │                         │
      ▼                         ▼
┌────────────────┐  ┌────────────────┐
│ Runner (thread │  │ Runner (thread │  ... (N concurrent)
│ sandbox A)     │  │ sandbox B)     │
│                │  │                │
│ Claude Code    │  │ Claude Code    │
│ + agent-runner │  │ + agent-runner │
└────────────────┘  └────────────────┘
```

Key changes:

- **Agent definitions as directories** — `agents/quant-research/` replaces `groups/main/`. Contains CLAUDE.md, seed.yaml, skills. Purely declarative.
- **Dynamic session/sandbox creation** — first message in a new thread triggers sandbox creation and seeding. No pre-configuration required per thread.
- **Multi-channel support** — Slack adapter implements the same `Channel` interface as Telegram. Both route through the orchestrator.
- **Session key = (channel, thread, agent)** — enables parallel sandboxes, thread isolation, and multi-agent per channel.
- **Development-focused personas** — CLAUDE.md instructs the agent to write code, create PRs, run tests. No WhatsApp formatting, no personal assistant behavior.
- **Sandbox lifecycle management** — GC cleans up thread sandboxes after N hours of inactivity.

---

## Agent Directory Convention

```
agents/
  quant-research/
    CLAUDE.md          # required — agent instructions
    seed.yaml          # required — repos, env setup
    skills/            # optional — custom Claude Code skills
    # future: subagents/, hooks/, tools/
```

### seed.yaml

```yaml
repos:
  - name: service-a
    source: git@github.com:user/service-a.git
    ref: main
  - name: service-b
    source: git@github.com:user/service-b.git
    ref: main
  - name: service-c
    source: git@github.com:user/service-c.git
```

### Config references

The top-level `config.yaml` references agent directories and maps them to channels:

```yaml
agents:
  - name: quant-research
    path: agents/quant-research

channels:
  - id: "slack:#quant-research"
    agents:
      - name: quant-research
        trigger: "@Devbox"

  - id: "tg:-1001234567890"
    agents:
      - name: quant-research
        trigger: "@Devbox"
```

The `agents:` section declares available agent types. The `channels:` section binds agents to chat contexts with trigger patterns. A channel can have multiple agents (Phase 4), and an agent can be bound to multiple channels.

---

## Sandbox Lifecycle

### Creation

Triggered by the first message in a new chat context (thread, DM, or channel) that matches a configured agent's trigger pattern. The orchestrator:

1. Resolves which agent handles this channel + trigger
2. Checks if a session already exists for `(channel_id, thread_id, agent_name)`
3. If no session: creates a new session record and sandbox directory
4. Seeds the sandbox from the agent definition

### Seeding

1. Copy `CLAUDE.md` from agent directory into sandbox
2. Copy `skills/` from agent directory into sandbox's `.claude/skills/`
3. Clone repos listed in `seed.yaml` into sandbox workspace
4. Write `.seeded` marker (existing pattern from 001-deployment-architecture)

This reuses the existing `seed-manifest.json` + `entrypoint.sh` seeding mechanism. The change is that the manifest is built from `agents/{name}/seed.yaml` instead of the global `workspace.repos` config.

### Runtime

- Each turn spawns an ephemeral container with the sandbox directory bind-mounted
- Container executes Claude Code via agent-runner, reads/writes to the sandbox
- Container exits after the turn; sandbox volume persists
- Follow-up messages in the same thread route to the same sandbox (via session lookup)
- IPC mechanism unchanged: controller writes to `ipc/input/`, runner polls

### Garbage Collection

Thread sandboxes are cleaned up after N hours of inactivity (configurable, default: 24h):

1. Controller periodically scans sessions for `last_activity_at` older than threshold
2. For matching thread sessions: delete sandbox directory, remove session record
3. If a user sends a message to a GC'd thread:
   - **Phase 1**: return error "Sandbox no longer available, please create a new thread"
   - **Future**: reconstruct sandbox by replaying thread chat history

DM and channel sessions are persistent — not subject to GC.

---

## Phases

### Phase 0: Structural refactor

Rename and restructure internal concepts without changing external behavior. Existing Telegram group support continues to work.

**Changes:**

1. **Rename "group" to "agent" throughout codebase**
   - `RegisteredGroup` type → `RegisteredAgent` (or keep internal naming, just change semantics)
   - `groups/` config directory → `agents/` directory convention
   - `group_folder` → `agent_name` in session management
   - `GroupQueue` → `SessionQueue`

2. **Introduce `agents/` directory convention**
   - Required: `CLAUDE.md`, `seed.yaml`
   - `seed.yaml` replaces the global `workspace.repos` config — each agent defines its own repos
   - Existing `groups/global/CLAUDE.md` and `groups/main/CLAUDE.md` migrate to `agents/main/CLAUDE.md` with global instructions inlined or loaded via `additionalDirectories`

3. **Update config schema**
   - New top-level `agents:` section pointing to directories
   - New top-level `channels:` section for routing (replaces `groups:` array with JID+folder pairs)
   - Backwards-compatible: old `groups:` format auto-mapped internally

4. **Refactor session management**
   - Session key changes from `group_folder` to composite `(channel_id, thread_id, agent_name)`
   - `sessions` table schema: add `channel_id`, `thread_id`, `agent_name` columns
   - Session lookup uses composite key instead of folder name

5. **Refactor sandbox creation**
   - `buildVolumeMounts()` reads agent directory instead of global config
   - `buildSeedManifest()` reads `seed.yaml` from agent directory
   - `syncStaticGroupConfig()` copies from `agents/{name}/` instead of `groups/{folder}/`

6. **Update database schema**
   - `registered_groups` table → `agents` table (or add migration)
   - `sessions` table: composite key `(channel_id, thread_id, agent_name)` replaces `group_folder` primary key

7. **Rewrite CLAUDE.md for devbox persona**
   - Remove WhatsApp/Telegram formatting instructions
   - Remove personal assistant behavior (memory files, casual conversation)
   - Add development focus: code review, PR creation, test execution, codebase navigation

### Phase 1: Telegram DM support

Validates the core sandbox lifecycle end-to-end with minimal new surface area.

**Changes:**

1. Implement DM detection in Telegram channel adapter (distinguish `tg:user:123` from `tg:-100group`)
2. DM creates a persistent session/sandbox for the `(user_id, null, agent)` tuple
3. Agent selection: config maps a default agent for DMs, or user specifies via command
4. Full sandbox lifecycle exercised: create, seed, use across turns, GC (manual for now)

**Why DMs first:** Low complexity — no thread semantics, no new platform integration. Iterates on the sandbox model without the overhead of Slack integration.

### Phase 2: Slack integration — thread support

The primary interaction pattern from the problem statement. Developers mention the agent in a thread, each thread gets its own sandbox.

**Changes:**

1. Build Slack channel adapter implementing the `Channel` interface
   - Slack Events API (or Socket Mode) for inbound messages
   - Slack Web API for outbound messages
   - Thread detection: messages with `thread_ts` are thread replies
2. Thread mention → create session/sandbox from agent definition
   - First message with trigger in a channel creates a new thread (or user creates thread, mentions agent)
   - Session key: `(channel_id, thread_ts, agent_name)`
3. Thread replies → pipe to active session via existing IPC mechanism
4. Thread sandbox GC after configurable inactivity period

### Phase 3: Slack integration — channel support

Non-threaded messages in a Slack channel route to a shared persistent session/sandbox. This is the "ambient context" mode — the agent accumulates context from channel messages and responds when triggered.

**Changes:**

1. Non-threaded channel messages → shared persistent session
   - Session key: `(channel_id, null, agent_name)`
   - Trigger pattern or always-on per config
2. Accumulate context between triggers (existing behavior from the message loop)
3. Channel sandbox persists indefinitely (same as current group behavior)

### Phase 4: Multi-agent support

Multiple agents registerable per channel. Different triggers route to different agents, each with its own session and sandbox.

**Changes:**

1. Multiple agents in `channels:` config per channel entry
2. Trigger-based routing: message content matched against each agent's trigger pattern
3. Each agent gets its own session/sandbox — session key `(channel, thread, agent)` already supports this
4. Handoff via chat: agent A can mention @AgentB in the thread, triggering agent B's turn

---

## Migration

### Config migration

Existing Telegram group configs map directly:

```yaml
# Old format
groups:
  - jid: "tg:-1001234567890"
    name: "Quant Research"
    folder: "quant-research"
    requires_trigger: true

# New format (equivalent)
agents:
  - name: quant-research
    path: agents/quant-research

channels:
  - id: "tg:-1001234567890"
    agents:
      - name: quant-research
        trigger: "@Devbox"
```

### Filesystem migration

```
# Old layout
groups/
  global/CLAUDE.md
  main/CLAUDE.md
  quant-research/workspace/

# New layout
agents/
  quant-research/
    CLAUDE.md       ← merged from groups/global/CLAUDE.md + groups/quant-research/CLAUDE.md
    seed.yaml       ← extracted from top-level workspace.repos config
    skills/         ← moved from container/skills/
```

### Database migration

1. `registered_groups` table renamed or migrated to `agents`
2. `sessions` table: add `channel_id`, `thread_id`, `agent_name` columns with composite unique constraint
3. Existing sessions migrated: `group_folder` mapped to `(channel_id=tg:jid, thread_id=null, agent_name=folder)`

### Backwards compatibility

The old `groups:` config format is auto-mapped internally during Phase 0 but deprecated. A deprecation warning is logged at startup if the old format is detected.

---

## Future Extensions (out of scope)

Listed for context to validate that the architecture supports them without redesign.

- **Template workspace optimization** — maintain a pre-seeded "golden" workspace per agent on the host. New sandboxes copy from the template instead of cloning repos. Reduces sandbox creation from minutes (git clone) to seconds (cp -r). Not Phase 1 because sandbox creation latency is acceptable for thread-scoped usage.

- **GC recovery via chat history replay** — when a user messages a GC'd thread, reconstruct the sandbox by replaying the thread's chat history through the agent. Requires a replay protocol and is complex; Phase 1 returns an error instead.

- **Structured handoff between agents** — agent A invokes agent B via an MCP tool (not just mentioning in chat). Enables typed data passing and coordination. Requires defining a handoff protocol.

- **PR lifecycle tracking** — webhook-based feedback loop where the agent monitors PR review comments and iterates. Requires GitHub webhook integration and a state machine for PR status.

- **k8s-native container runtime** — replace Docker CLI spawning with k8s Jobs API. Eliminates Docker socket mount and path alignment concerns. Runners become k8s Jobs with PVC mounts. Requires refactoring `container-runner.ts` to use `@kubernetes/client-node`.
