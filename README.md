# Devbox Agent

Self-hosted, Kubernetes-native sandbox orchestration for AI coding agents.

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![Node.js >= 20](https://img.shields.io/badge/Node.js-%3E%3D20-green.svg)](https://nodejs.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

Devbox Agent orchestrates AI coding agents (powered by [Claude Code SDK](https://docs.anthropic.com/en/docs/claude-code/sdk)) in isolated containers on your own infrastructure. Each agent session runs in its own sandbox with persistent workspace, conversation state, and version-controlled instructions.

---

## Why Devbox Agent

- **Self-hosted**: Your infrastructure, your data, your control. No code or conversation data leaves your network.
- **Kubernetes-native**: Agents run as Pods, workspaces are Persistent Volume Claims, and RBAC controls access. Runs equally well on Docker for local development.
- **Chat-first developer experience**: Trigger agents from Slack, Telegram, or the built-in Web UI. Agents respond in-thread with full conversation context.
- **Agent-as-Code**: Agent definitions are version-controlled directories containing a `CLAUDE.md` (instructions) and `seed.yaml` (repos, model, configuration). Review agent changes in pull requests like any other code.

---

## How It Works

Devbox Agent uses a two-process model where the controller and runner never share memory:

**Controller** (long-lived process): Receives chat messages from connected platforms, routes them to the correct session, spawns and manages runner containers, persists state in SQLite, and enforces concurrency limits.

**Runner** (one container per session): Executes the Claude Code SDK via `query()`, reads and writes the workspace, and communicates results back through filesystem-based IPC. The runner stays alive across conversation turns and exits only on idle timeout or explicit shutdown.

```
                         +------------------+
                         |  Chat Platforms   |
                         |  (Slack/Telegram/ |
                         |   Web UI/API)     |
                         +--------+---------+
                                  |
                                  v
                         +--------+---------+
                         |    Controller     |
                         |  (Node.js, SQLite)|
                         |  Routes messages  |
                         |  Manages sessions |
                         +----+----+----+---+
                              |    |    |
                    +---------+    |    +---------+
                    v              v              v
              +-----+----+  +-----+----+  +------+---+
              |  Runner   |  |  Runner   |  |  Runner  |
              | Container |  | Container |  | Container|
              | (Agent A) |  | (Agent B) |  | (Agent A)|
              | Session 1 |  | Session 2 |  | Session 3|
              +----------+  +----------+  +----------+
                   |              |              |
                   v              v              v
              /workspace     /workspace     /workspace
              (PVC/bind)     (PVC/bind)     (PVC/bind)
```

---

## Comparison with Claude Managed Agents

Devbox Agent is the self-hosted complement to [Anthropic's Claude Managed Agents](https://docs.anthropic.com/en/docs/agents). Both provide sandboxed agent execution, but they target different deployment models.

| Feature | Devbox Agent | Claude Managed Agents |
|---|---|---|
| **Deployment** | Self-hosted on your infrastructure | Cloud-hosted by Anthropic |
| **Sandbox** | Kubernetes Pods or Docker containers | Anthropic-managed sandboxes |
| **Orchestration** | Your K8s cluster, your scaling rules | Fully managed by Anthropic |
| **Triggers** | Slack, Telegram, Web UI, API | API |
| **Session persistence** | SQLite + PVCs, survives restarts | Managed by Anthropic |
| **Multi-agent** | Multiple agent definitions per deployment | Single agent per session |
| **Observability** | Container logs, structured IPC, your monitoring stack | Anthropic dashboard |
| **Agent definition** | `CLAUDE.md` + `seed.yaml` in your repo | API parameters |
| **Data residency** | Your network, your storage, your rules | Anthropic's infrastructure |

Devbox Agent and Claude Managed Agents are complementary -- use Managed Agents for zero-ops cloud execution, use Devbox Agent when you need self-hosted infrastructure, Kubernetes integration, or data sovereignty.

---

## Quick Start

### Option 1: Kubernetes with Tilt (recommended)

Full feature set including Pod isolation, RBAC, and persistent volumes.

```bash
# Prerequisites: OrbStack or Minikube, Tilt
brew install orbstack tilt

# Start the development environment
just dev-k8s
```

Tilt UI opens at `http://localhost:10350` with hot-reload, logs, and resource monitoring.

See [docs/local-k8s-setup.md](docs/local-k8s-setup.md) for detailed setup.

### Option 2: Docker Compose (lightweight)

Quick setup for controller logic testing on low-resource machines.

```bash
just build-images
just compose-up
```

Note: Cannot test Kubernetes-specific features (Pod API, RBAC, PVC).

See [docs/local-compose-setup.md](docs/local-compose-setup.md) for detailed setup.

### Option 3: Direct Node.js (fastest)

Controller-only development without containers.

```bash
just dev-node
```

---

## Agent Definition

Each agent is a directory under `agents/` containing two files:

```
agents/example/
  CLAUDE.md       # Agent instructions and persona
  seed.yaml       # Sandbox configuration (repos, model, settings)
```

**CLAUDE.md** defines the agent's behavior, capabilities, and guidelines. This is the system prompt that Claude Code receives inside the sandbox.

**seed.yaml** declares the sandbox environment:

```yaml
# Repositories to clone into the sandbox workspace
repos:
  - name: my-project
    source: https://github.com/your-org/your-repo.git
    ref: main

# Optional overrides
# image: custom-runner:latest       # Runner image
# model: sonnet                     # Claude model (sonnet, opus, haiku, or full name)
# thinking:                         # Thinking configuration
#   type: adaptive
# effort: high                      # Effort level (low, medium, high, max)
```

Agents can also include a `skills/` directory for agent-specific Claude Code skills that supplement or override the shared skill set.

---

## Architecture Overview

The codebase is organized into four layers:

- **Controller** (`src/`): Message routing, session management, container orchestration, chat platform adapters, SQLite persistence.
- **Runner** (`container/`): In-container agent execution, Claude Code SDK integration, IPC communication, workspace seeding.
- **Agent Definitions** (`agents/`): Version-controlled agent templates with instructions and seed configuration.
- **Kubernetes Manifests** (`k8s/`): Kustomize overlays for staging and production deployment.

For the full code map, type hierarchy, data layout, and architectural invariants, see [docs/architecture.md](docs/architecture.md).

---

## Roadmap

Devbox Agent is currently at **v0.1 alpha**. The project follows a phased roadmap:

- **Phase 0** (current): Open-source foundation -- sandbox isolation, session management, multi-channel chat integration, filesystem-based IPC.
- **Phase 1**: Agent API layer -- REST API aligned with Managed Agents semantics (`/v1/agents`, `/v1/sessions`), enabling programmatic agent management alongside chat triggers.
- **Phase 2**: Observability and governance -- structured tracing, permission model, cost tracking, audit logging.
- **Phase 3**: Multi-agent coordination -- agent-to-agent messaging, parent-child agent spawning, shared workspace protocols.
- **Phase 4**: Self-evaluation -- success criteria definitions, evaluation loops, iteration limits, automated quality gates.

See [docs/roadmap.md](docs/roadmap.md) for details.

---

## Documentation

- [Architecture](docs/architecture.md) -- System design, code map, and architectural invariants
- [Getting Started](docs/getting-started.md) -- First-run setup and configuration
- [Configuration](docs/configuration.md) -- Full configuration reference
- [Roadmap](docs/roadmap.md) -- Project phases and planned features
- [Contributing](CONTRIBUTING.md) -- Contribution guidelines

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting issues, proposing changes, and setting up a development environment.

---

## License

AGPL-3.0. See [LICENSE](LICENSE) for the full text.
