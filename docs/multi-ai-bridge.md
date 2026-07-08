# Multi-AI Bridge

Connects four AI identities into one bidirectional prompt network, driven from
chat (including Slack on mobile):

```
        you (Slack / Telegram / Web, incl. mobile)
                        │
                multi-ai agent  ←— Claude Code orchestrator (Anthropic account)
                        │  multi-ai-bridge skill (ai-bridge CLI)
        ┌───────────┬───┴───────┬─────────────┐
      codex      chatgpt   claude-code      claude
   (coding)      (chat)     (coding)        (chat)
   └── OpenAI/ChatGPT account ──┘└── Anthropic/Claude account ──┘
```

## How the four accounts map

There is no official API for driving the ChatGPT or Claude _web apps_ directly.
The supported equivalents are the vendors' agent CLIs, each authenticated with
the corresponding consumer account:

| Identity    | Reached via                      | Account it uses        |
| ----------- | -------------------------------- | ---------------------- |
| Codex       | `codex` CLI (agent mode)         | ChatGPT/OpenAI login   |
| ChatGPT     | `codex` CLI (chat-only persona)  | ChatGPT/OpenAI login   |
| Claude Code | `claude` CLI (agent mode)        | Claude/Anthropic login |
| Claude      | `claude` CLI (chat-only persona) | Claude/Anthropic login |

The channel is genuinely bidirectional: each named channel resumes the peer's
native session (`codex exec resume`, `claude --resume`) on every exchange, and
the orchestrator forwards replies between peers (`ai-bridge relay`), so any
agent can prompt, direct, and respond to any other across multiple rounds.

## Components

- `container/skills/multi-ai-bridge/` — shared skill; ships the `ai-bridge.mjs`
  script (send / relay / channels / log / status). See its `SKILL.md` for the
  full command reference and orchestration patterns.
- `agents/multi-ai/` — orchestrator agent persona intended for chat binding.
- Runner image — installs `@openai/codex` alongside `@anthropic-ai/claude-code`.

## Setup

### 1. Authentication

**Anthropic/Claude account** — whatever the runner already uses
(`ANTHROPIC_API_KEY`, `CLAUDE_CODE_OAUTH_TOKEN`, or `~/.claude` credentials)
also powers the `claude-code` / `claude` peers.

**OpenAI/ChatGPT account** — run `codex login` once on your own machine (opens
a ChatGPT browser login), which writes `~/.codex/auth.json`. Mount that file
into the runner via the agent's `seed.yaml`:

```yaml
# agents/multi-ai/seed.yaml
secretMounts:
  - secretName: codex-auth # k8s Secret name (Kubernetes runtime)
    hostPath: /srv/devbox/secrets/codex-auth.json # host file (Docker runtime)
    mountPath: /home/devbox/.codex/auth.json
```

Alternatively set `OPENAI_API_KEY` (API billing instead of the ChatGPT plan).

### 2. Register the agent

```yaml
# config.yaml
agents:
  - name: multi-ai
    path: agents/multi-ai
```

### 3. Slack (works on mobile out of the box)

The Slack channel adapter uses Socket Mode, so no public URL is needed, and
because it is a normal Slack bot, **the Slack mobile app is the mobile client**
— nothing extra to build or install on the phone.

```yaml
# config.yaml
slack_bot_token: 'xoxb-...' # or SLACK_BOT_TOKEN env var
slack_app_token: 'xapp-...' # or SLACK_APP_TOKEN env var

channels:
  - id: 'slack:C0123456789' # your Slack channel ID
    agents:
      - name: multi-ai
        trigger: '@Devbox'
        requires_trigger: true
```

See `docs/configuration.md` for Slack app scopes and token details.

### 4. Rebuild the runner image

The runner image must include the codex CLI (`docker/runner.Dockerfile`
installs it). Rebuild and redeploy the image after pulling this change.

## Using it from Slack (phone or desktop)

Talk to the orchestrator in natural language; it routes to the right peer:

- `@Devbox 让 codex 重构 payments 模块，然后你 review 它的 diff`
- `@Devbox ask chatgpt and claude the same question about CRDTs and compare`
- `@Devbox split this feature: codex does the backend, claude-code does the frontend, then merge`
- `@Devbox have claude-code and codex debate the migration plan for 3 rounds and summarize`

Follow-ups in the same Slack thread keep the same sandbox session, and each
peer keeps its own conversation context per named channel, so you can keep
directing a long-running task from your phone.

## Security notes

- Peers run inside the same sandbox container as the orchestrator and share
  `/workspace`. Only give the agent repos you intend all peers to touch.
- `~/.codex/auth.json` grants use of your ChatGPT account; treat it like any
  other secret mount (k8s Secret, restrictive host permissions).
- Codex runs with `--sandbox workspace-write` (coding) or `--sandbox read-only`
  (chat persona); it has no network-exempt privileges beyond the container's.
