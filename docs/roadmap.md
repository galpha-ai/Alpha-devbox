# Roadmap

## Vision

Devbox Agent aims to be the definitive self-hosted agent infrastructure for teams that need to run AI coding agents on their own Kubernetes clusters with full control over data, security, and integration.

Anthropic launched Claude Managed Agents in April 2026 -- a fully hosted service for running agents in cloud sandboxes. Managed Agents is the right choice for teams that want zero infrastructure overhead and are comfortable with Anthropic-hosted execution. Devbox Agent serves a complementary niche: organizations that require on-premise execution, custom networking, private model access, audit-grade data retention, or deep integration with internal toolchains and CI/CD systems that cannot be exposed to third-party services.

The roadmap below builds toward API compatibility with Claude Managed Agents semantics where possible, so teams can migrate workloads between hosted and self-hosted infrastructure without rewriting their orchestration layer.

## Current Status: v0.1 Alpha

What is implemented today:

- **Two-process controller/runner architecture.** A long-lived controller routes messages and manages state; long-lived runner containers execute Claude Code SDK queries inside isolated sandboxes. The two processes communicate exclusively through filesystem-based IPC.
- **Docker and Kubernetes container runtimes.** Docker for local development, Kubernetes with PVC-backed persistent volumes for production clusters.
- **Session management with persistent workspaces.** SQLite stores all persistent state (sessions, messages, agents, scheduled tasks). Workspace directories survive container restarts via bind mounts.
- **Multi-channel support.** Telegram (groups and DMs), Slack, and Web (HTTP REST + WebSocket streaming). Channel adapters implement a common `Channel` interface.
- **Agent-as-Code definitions.** Each agent is a directory containing `CLAUDE.md` (instructions), `seed.yaml` (repos, model, thinking config, secret mounts), and optional skills. Agents are version-controlled templates; runtime state is materialized separately.
- **Session garbage collection and lifecycle management.** Heartbeat-based GC with configurable TTL. Thread-scoped sessions are reclaimed after 6 hours of inactivity. Channel-scoped sessions are long-lived.
- **Concurrency control and message queuing.** Global container concurrency cap (`MAX_CONCURRENT_CONTAINERS`). Per-session message queuing with retry and exponential backoff. Follow-up messages are piped to active containers via IPC.
- **GitHub App integration for repo seeding.** Automatic token exchange per repo owner, `gh` CLI wrapper for transparent authentication inside containers.
- **Scheduled task execution.** Cron, interval, and one-shot task scheduling via SQLite-backed scheduler. Agents can self-schedule tasks through IPC-exposed MCP tools.
- **IPC-based follow-up message streaming.** Mid-query message injection via `MessageStream` async iterables, enabling multi-turn conversations within a single container lifecycle.

## Phase 1: Agent API Layer

**Timeline:** Q2--Q3 2026

**Goal:** Provide a REST API that aligns with Claude Managed Agents semantics, enabling programmatic agent management alongside chat-triggered workflows. Teams should be able to create agents, start sessions, and stream results without a chat frontend.

### Deliverables

- `POST /v1/agents` -- Register or update agent definitions at runtime. Accepts the same structure as the `agents/` directory format (instructions, seed config, skills) but via API payload.
- `POST /v1/sessions` -- Create a new session for a given agent. Returns a session ID and provisions the workspace directory and IPC structure.
- `POST /v1/sessions/:id/messages` -- Send a user message to a session. Enqueues the message and triggers container execution if no container is active.
- `GET /v1/sessions/:id/events` -- Server-Sent Events stream for session output. Streams `ContainerOutput` events (text, tool calls, errors, completion) in real time.
- `DELETE /v1/sessions/:id` -- Terminate a session. Writes the `_close` sentinel, waits for container exit, and optionally cleans up the workspace.
- `GET /v1/sessions/:id` -- Retrieve session metadata, status, and conversation history.
- `GET /v1/agents` -- List registered agents and their configurations.
- OpenAPI 3.1 specification generated from Zod schemas. SDK generation for TypeScript and Python via `openapi-generator`.
- API key authentication with scoped permissions. Keys are stored in SQLite with create/revoke lifecycle.

### Design Considerations

The existing Web channel (`channels/web.ts`) already exposes conversation CRUD and WebSocket streaming. Phase 1 extracts and generalizes this into a standalone API layer that the Web channel, CLI tools, and external integrations all consume. The chat-triggered flow remains the primary interface; the API is an additional entry point into the same session and container machinery.

## Phase 2: Observability and Governance

**Timeline:** Q3--Q4 2026

**Goal:** Enterprise-grade visibility into agent execution and organizational controls for safe deployment at scale.

### Deliverables

- **Structured execution tracing.** Per-turn trace records capturing: tool calls (name, arguments, duration, result summary), model decisions (thinking output when enabled), errors (with secret-safe sanitization), and token usage. Traces are stored in SQLite and queryable via API.
- **Session event streaming and replay.** Full event log per session, exportable as JSON. Replay mode reconstructs a session timeline for debugging and post-incident review.
- **Permission model.** Agent-scoped access controls: which repos an agent can clone, which tools are available, which secrets are mounted, and which channels can trigger it. Defined in `seed.yaml` and enforced by the controller at container spawn time.
- **Cost tracking.** Per-session and per-agent token usage accounting (input tokens, output tokens, cache reads/writes). Aggregated into daily and monthly rollups. Exposed via API and optionally pushed to external billing systems.
- **Audit logging.** Append-only log of all state-changing operations: session creation, message routing, container spawn/exit, secret access, scheduled task execution. Exportable for compliance.
- **Prometheus metrics export.** `/metrics` endpoint exposing: active sessions, container queue depth, container spawn latency, message processing latency, token usage counters, error rates, and GC sweep statistics.

## Phase 3: Multi-Agent Coordination

**Timeline:** Q4 2026 -- Q1 2027

**Goal:** Enable agent-to-agent collaboration within and across sessions. A lead agent should be able to delegate subtasks to specialist agents running in their own sandboxes, share context, and synthesize results.

### Deliverables

- **Agent-to-agent messaging via MCP tools.** Extend the existing IPC MCP server (`ipc-mcp-stdio.ts`) with tools for sending messages to other agents. The controller mediates routing: messages from agent A addressed to agent B are delivered through B's session queue.
- **Parent-child agent spawning.** An agent can request the controller to spawn a sub-agent in a new sandbox. The parent provides initial context and receives a completion event when the child finishes. The child session has its own workspace, IPC, and lifecycle.
- **Shared workspace mounting.** Cross-agent read-only mounts. A parent agent can expose specific directories from its workspace to child agents. Implemented as additional read-only bind mounts in the container spec.
- **Agent team definitions in config.** New `teams` section in `config.yaml` declaring agent groups with roles (lead, reviewer, specialist). Team definitions inform the coordination protocol but do not enforce hard boundaries -- agents can still communicate ad hoc.
- **Coordination protocols.** Structured patterns for common multi-agent workflows: fan-out/fan-in (parallelize subtasks, aggregate results), review chain (author then reviewer), and escalation (hand off to a more capable agent or human).

### Design Considerations

Multi-agent coordination reuses the existing session and container primitives. A child agent session is a regular session with a parent reference. The controller already supports concurrent sessions for different agents; the new capability is letting agents initiate sessions for other agents rather than requiring a human trigger.

## Phase 4: Self-Evaluation

**Timeline:** Q1--Q2 2027

**Goal:** Agents can define and verify their own success criteria, enabling autonomous retry loops and integration with CI/CD pipelines for automated quality gates.

### Deliverables

- **`seed.yaml` success criteria field.** New `success_criteria` block in agent seed configuration. Supports declarative checks: command exit codes, file existence, content assertions, and custom evaluator references.
- **Evaluation loop.** After the primary agent query completes, the runner executes the success criteria checks. On failure, it retries the query with evaluation feedback appended to the conversation. The loop continues until success or the iteration limit is reached.
- **Configurable iteration limits and timeouts.** Per-agent settings for maximum retry attempts (`max_eval_retries`, default: 3) and total evaluation wall-clock timeout (`eval_timeout`, default: 30 minutes). Prevents runaway loops.
- **Custom evaluator agent support.** An evaluation can delegate to a separate agent (running in its own sandbox or the same one) that reviews the primary agent's output and returns a structured pass/fail verdict with feedback. This composes with Phase 3 multi-agent infrastructure.
- **CI/CD pipeline integration.** Webhook or API callback on session completion with evaluation results. Enables workflows where a PR triggers an agent session, the agent makes changes, the evaluator verifies them, and the result is reported back to the PR as a status check.

### Design Considerations

Self-evaluation builds on the existing run lifecycle. The runner already writes `done.json` on completion; the evaluation loop wraps the query cycle with a check-retry outer loop before writing the final `done.json`. The controller does not need to change -- evaluation is internal to the runner process.

## Contributing to the Roadmap

Devbox Agent is an open project and roadmap priorities are shaped by community input.

**Proposing a feature:**

1. Open a GitHub Issue using the "Feature Proposal" template.
2. Describe the use case, not just the solution. Explain what you are trying to accomplish and why existing capabilities are insufficient.
3. Reference the relevant roadmap phase if your proposal fits within one, or explain why it should be considered independently.

**Roadmap discussions:**

- Major roadmap items are tracked as GitHub Issues with the `roadmap` label.
- Design discussions for upcoming phases happen in GitHub Discussions under the "Architecture" category.
- RFCs for significant changes live in `docs/rfcs/` and follow the established format (see `docs/rfcs/001-agent-sandbox-architecture.md` for an example).

**Implementation contributions:**

- Check the issue tracker for items tagged `good first issue` or `help wanted`.
- For Phase 1 work, the API layer builds directly on the existing Web channel code in `src/channels/web.ts` -- familiarity with that module is a good starting point.
- All contributions should follow the two-process architecture: controller logic stays in `src/`, runner logic stays in `container/`. See `docs/architecture.md` for the full code map.
