# Devbox Agent

### The open-source Claude Managed Agents.

**Self-host your Claude agents. Your repos, your cloud, your data.**

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](LICENSE)
[![Status: alpha](https://img.shields.io/badge/status-v0.1%20alpha-orange.svg)](#status)
[![Node 20+](https://img.shields.io/badge/node-20%2B-brightgreen.svg)](https://nodejs.org)
[![Powered by Claude Agent SDK](https://img.shields.io/badge/powered%20by-Claude%20Agent%20SDK-7c3aed.svg)](https://docs.anthropic.com/en/docs/claude-code/sdk)

<!-- TODO: replace with actual demo GIF / screenshot -->
<!-- ![Demo](docs/assets/demo.gif) -->

> Anthropic ships [Claude Managed Agents](https://docs.anthropic.com/en/docs/agents) — hosted agents in cloud sandboxes.
> **Devbox Agent is the self-hosted version:** same persistent-sandbox model, but everything runs on your own clusters.
> Think **Ollama for ChatGPT**, **Supabase for Firebase** — that's what Devbox Agent is for Claude Managed Agents.

---

## Try it in 60 seconds

```bash
git clone https://github.com/galpha-ai/Alpha-devbox.git && cd Alpha-devbox
npm install
cp .env.example .env.local   # add your Claude credential (Anthropic / Vertex / Bedrock / OpenRouter)
npm run dev                   # one command: builds runner image, starts controller + web UI
```

Open **http://127.0.0.1:5175/** — type a question, get an answer. Your conversation runs inside a persistent sandbox on your machine.

No Slack setup. No Kubernetes. No repo cloning. Just `npm run dev`.

---

## Why this exists

Every coding agent today makes you choose:

| | Stateless CLI | Hosted SaaS | **Devbox Agent** |
|---|---|---|---|
| Examples | Claude Code, Codex, Aider | Devin, Cursor, Replit Agent | — |
| Persistent workspace | ❌ | ✅ | ✅ |
| Self-hosted | ✅ (local only) | ❌ | ✅ (your cloud) |
| Multi-user / team | ❌ | ✅ | ✅ |
| Chat-native (Slack/TG) | ❌ | ❌ | ✅ |
| Open source | partial | ❌ | ✅ |

**Devbox Agent fills the gap**: persistent, multi-user, chat-native agents — on infrastructure you own.

<details>
<summary><strong>Detailed comparison vs 5 alternatives</strong></summary>

| | Claude Managed Agents | Devin / Cursor / Replit | Claude Code / Codex CLI | OpenHands | **Devbox Agent** |
| --- | :---: | :---: | :---: | :---: | :---: |
| Open source | ❌ | ❌ | partial | ✅ | ✅ |
| Self-hosted in your cloud | ❌ | ❌ | local only | ✅ | ✅ |
| Persistent workspace per session | ✅ | ✅ | ❌ | ✅ | ✅ |
| Multi-channel chat (Slack / TG / Web) | partial | ❌ | ❌ | ❌ | ✅ |
| Agent-as-Code (Git-versioned) | ❌ | ❌ | local files | partial | ✅ |
| Kubernetes-native runtime | ❌ | ❌ | n/a | partial | ✅ |
| Model providers | partial | ❌ | ❌ | ✅ | ✅¹ |

> ¹ Runs Claude via Anthropic API, Google Vertex AI, Amazon Bedrock, or any Anthropic-compatible gateway (OpenRouter, LiteLLM, etc.). See `.env.example` for configuration.

</details>

---

## How it works

```
   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
   │  Slack  │    │Telegram │    │   Web   │    │   API   │
   └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘
        └──────────────┴────┬─────────┴──────────────┘
                            │
                  ┌─────────▼─────────┐
                  │    Controller     │   Long-lived Node.js process.
                  │                   │   Routes messages, manages state
                  │  SQLite · IPC ·   │   in SQLite, spawns containers.
                  │  Session mgmt    │
                  └─────────┬─────────┘
                            │ one container per session
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        ┌───────────┐ ┌───────────┐ ┌───────────┐
        │  Runner   │ │  Runner   │ │  Runner   │
        │ Sandbox A │ │ Sandbox B │ │ Sandbox C │   Each runner is a
        │           │ │           │ │           │   long-lived container
        │ Claude    │ │ Claude    │ │ Claude    │   with bind-mounted
        │ Agent SDK │ │ Agent SDK │ │ Agent SDK │   workspace that
        │ + repos   │ │ + repos   │ │ + repos   │   persists across
        └───────────┘ └───────────┘ └───────────┘   restarts.
```

**Two processes, never shared memory:**
- **Controller** listens to chat platforms, persists state, spawns containers
- **Runner** executes Claude Agent SDK queries inside an isolated sandbox
- **IPC** is filesystem-based — no fragile sockets, no shared memory
- **Bind mounts** make session state durable — the container is ephemeral; the workspace survives

---

## Key features

### Chat-first, multi-channel
Slack, Telegram, and a bundled web UI out of the box. Mention `@Devbox` in a Slack thread — that thread becomes its own sandbox. The PM, the engineer, and the agent all see the same conversation.

### Persistent sessions
Workspaces and Claude conversation state survive across turns **and** container restarts. Start a backtest at 5pm, come back at 9am — your session is exactly where you left it.

### Agent-as-Code
Each agent is a Git-versioned directory:
```
agents/my-agent/
  CLAUDE.md      # instructions and persona
  seed.yaml      # repos to clone, model, thinking config
  skills/        # optional Claude Code skills
```
Review agents in PRs. Roll back bad prompts with `git revert`. Version your agent fleet like you version your infra.

### Self-hosted, end-to-end
Repos, storage, logs, secrets, model traffic, tool calls — all stay on infrastructure you operate. Docker for local dev; Kubernetes with PVC-backed persistent volumes for production.

---

## Use cases

**Shared company workspace** — Multiple engineers + the agent share the same repos, tools, and cloud environment. Different Slack threads track different tasks without losing org-level context.

**Long-running coding tasks from chat** — "Fix the flake in `tests/integration/payments_test.go`" → the agent reads, edits, runs tests, opens a PR. Follow-up replies in the same thread route to the same workspace.

**AI research environments** — Describe a strategy in plain language → the agent turns it into code → runs a simulation → iterates. All in one persistent workspace with full session history.

> The bundled `frontend/` is a working example of this pattern — a React + Tailwind research assistant UI that pairs with the `agents/localqa/` demo agent.

---

## Status

**v0.1 alpha** — core architecture shipped, ready for early adopters. See **[docs/roadmap.md](docs/roadmap.md)** for what's next.

---

## Docs

| | |
| --- | --- |
| **[Getting Started](docs/getting-started.md)** | Deploy: Node.js, Docker Compose, or Kubernetes |
| **[Architecture](docs/architecture.md)** | Two-process model, code map, invariants |
| **[Configuration](docs/configuration.md)** | Every config field with examples |
| **[Security](docs/SECURITY.md)** | Threat model and reporting |

---

## Contributing

Small, opinionated codebase. The two-process model is intentional and load-bearing — read [`docs/architecture.md`](docs/architecture.md) before structural changes. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the workflow.

---

## License

[AGPL-3.0](LICENSE)
