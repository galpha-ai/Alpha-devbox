# Configuration Reference

Devbox Agent is configured through a YAML config file (`config.yaml`) and environment variables. Environment variables take precedence over config file values where both are supported.

## Config File

The controller reads its config file on startup. By default it looks for `config.yaml` in the working directory. Override the path with:

```bash
npm run dev -- --config path/to/config.yaml
```

The config file is validated at startup using a Zod schema (defined in `src/config.ts`). Invalid configuration causes the controller to exit with a descriptive error message.

## Top-Level Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `assistant_name` | string | `"Devbox"` | Bot display name. Also used as the default trigger prefix (`@<assistant_name>`). |
| `telegram_bot_token` | string | -- | Telegram Bot API token. Can also be set via `TELEGRAM_BOT_TOKEN` env var. Required if any channel ID starts with `tg:`. The Telegram adapter also supports `/chatid` for discovering IDs and `/ping` for a quick health check. |
| `slack_bot_token` | string | -- | Slack bot token (`xoxb-...`). Can also be set via `SLACK_BOT_TOKEN` env var. Required if any channel ID starts with `slack:`. Typical app scopes include message read/write scopes and `users:read`; add `reactions:write` if you want Slack status/typing reactions. |
| `slack_app_token` | string | -- | Slack app-level token (`xapp-...`) for Socket Mode. Can also be set via `SLACK_APP_TOKEN` env var. Required alongside `slack_bot_token`. |
| `data_root` | string | Current working directory | Root directory for all runtime data (SQLite database, session workspaces, agent logs). Can also be set via `DEVBOX_DATA_ROOT` env var. |
| `trigger_pattern` | string | `^@<assistant_name>\b` | Regex override for the message trigger pattern. Case-insensitive. When omitted, the trigger is auto-generated from `assistant_name`. |
| `timezone` | string | System timezone | IANA timezone identifier (e.g., `America/New_York`). Overrides the detected system timezone for scheduling and logging. |

## container Section

Controls the sandbox runtime that executes agents.

```yaml
container:
  runtime: docker
  image: devbox-runner:latest
  timeout: 5400000
  idle_timeout: 300000
  max_concurrent: 2
  max_output_size: 10485760
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `runtime` | `"docker"` or `"kubernetes"` | `"docker"` | Container runtime to use. Docker spawns containers via the local Docker socket. Kubernetes creates Pods in the configured namespace. |
| `image` | string | `"devbox-runner:latest"` | Runner container image. Can be overridden per-agent in `seed.yaml`. |
| `timeout` | number (ms) | `5400000` (90 min) | Hard timeout per container run. The container is forcibly killed after this duration. |
| `idle_timeout` | number (ms) | `300000` (5 min) | Idle period before the controller writes a `_close` sentinel to shut down the runner. Resets on each new message. |
| `max_concurrent` | number | `2` | Global concurrency limit for running containers. Excess sessions are queued in `SessionQueue`. |
| `max_output_size` | number (bytes) | `10485760` (10 MB) | Maximum size of runner output before truncation. |

### kubernetes Subsection

Only relevant when `runtime` is `"kubernetes"`. All fields have sensible defaults for local development.

```yaml
container:
  runtime: kubernetes
  kubernetes:
    namespace: devbox-agent
    kubeconfig: ~/.kube/config
    pvc_name: devbox-data
    data_mount_path: /data/devbox-agent
    service_account: devbox-runner
    image_pull_policy: IfNotPresent
    runner_resources:
      cpu: "2"
      memory: 4Gi
      ephemeral_storage: 10Gi
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `namespace` | string | `"devbox-agent"` | Kubernetes namespace for runner Pods. |
| `kubeconfig` | string | -- | Path to kubeconfig file. When omitted, uses in-cluster configuration (for running inside a Pod). |
| `pvc_name` | string | `"devbox-data"` | Name of the shared RWX PersistentVolumeClaim used by both the controller and runner Pods. |
| `data_mount_path` | string | `"/data/devbox-agent"` | Mount path for the PVC inside runner Pods. Must match `data_root`. |
| `service_account` | string | `"devbox-runner"` | Kubernetes ServiceAccount for runner Pods. |
| `image_pull_policy` | `"Always"`, `"IfNotPresent"`, or `"Never"` | `"IfNotPresent"` | Image pull policy for runner Pods. |
| `runner_resources` | object | See below | Resource requests for runner Pods. |

**runner_resources defaults:**

| Field | Default | Description |
|-------|---------|-------------|
| `cpu` | `"2"` | CPU request/limit. |
| `memory` | `"4Gi"` | Memory request/limit. |
| `ephemeral_storage` | `"10Gi"` | Ephemeral storage request/limit. |

## web Section

Enables the HTTP API for the web frontend, including the AI SDK-compatible SSE chat endpoint.

```yaml
web:
  enabled: true
  port: 8080
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `false` | Whether to start the web server. |
| `port` | number | `8080` | HTTP listen port. |

When enabled, the web server exposes REST conversation endpoints plus an AI SDK-compatible SSE chat stream on `/api/devbox/chat`. Auth is delegated to an upstream proxy via the `X-User-Id` header.

## agents Section

Declares which agent definitions are available. Each entry maps a name to a directory path.

```yaml
agents:
  - name: main
    path: agents/main
  - name: researcher
    path: agents/researcher
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique agent identifier. Must match `^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$`. |
| `path` | string | Path to the agent definition directory. Relative paths are resolved first from the config file directory, then from the application root. |

Each agent directory must contain at minimum `CLAUDE.md` and `seed.yaml`. See the Agent Definition section below.

## channels Section

Maps chat platform channels to agents. Each channel binding determines which agent handles messages and how the trigger works.

```yaml
channels:
  - id: "tg:-1001234567890"
    agents:
      - name: main
        trigger: "@Devbox"
        requires_trigger: true

  - id: "tg:user:*"
    agents:
      - name: main
        requires_trigger: false

  - id: "slack:C0123456789"
    agents:
      - name: main
        trigger: "@Devbox"
        requires_trigger: true

  - id: "web:*"
    agents:
      - name: main
        requires_trigger: false
```

### Channel entry fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Channel identifier. See format table below. |
| `agents` | array | List of agent bindings for this channel. Currently only the first binding is used. |

### Agent binding fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | -- | Agent name, must match an entry in the `agents` section. |
| `trigger` | string | `@<assistant_name>` | Text prefix that activates the agent in group contexts. |
| `requires_trigger` | boolean | `true` for groups, `false` for DMs | Whether messages must start with the trigger to be processed. |

### Channel ID formats

| Format | Description | Example |
|--------|-------------|---------|
| `tg:<chat_id>` | Specific Telegram group or supergroup. | `tg:-1001234567890` |
| `tg:user:*` | Wildcard matching all Telegram DMs. Useful when you want the bot to auto-handle Telegram private chats by default. | `tg:user:*` |
| `tg:user:<user_id>` | Specific Telegram user DM. You can discover the numeric ID with `/chatid`. | `tg:user:123456789` |
| `slack:<channel_id>` | Specific Slack channel. Current docs/config only describe specific channel bindings, not a Slack DM wildcard. | `slack:C0123456789` |
| `web:*` | Wildcard matching all web frontend users. | `web:*` |

Wildcard channels (`tg:user:*`, `web:*`) act as catch-all bindings. A message is matched against specific channel IDs first; the wildcard is used only if no specific match exists. For Telegram, `/chatid` is the easiest way to discover the right `tg:...` value for a group or DM.

## Agent Definition (seed.yaml)

Each agent directory contains a `seed.yaml` that defines the sandbox environment.

```yaml
repos:
  - name: my-project
    source: https://github.com/your-org/your-repo.git
    ref: main

image: custom-runner:latest

model: sonnet

thinking:
  type: adaptive
  budgetTokens: 10000

effort: high
```

### repos

List of repositories to clone into the sandbox workspace on first run.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Directory name for the clone inside `/workspace`. |
| `source` | string | Yes | Remote git URL. Must be a valid git remote (HTTPS or SSH). |
| `ref` | string | No | Branch, tag, or commit to check out. Defaults to the repository's default branch. |

### image

Optional runner image override. When set, this agent uses a different container image than the global `container.image`. Useful for agents that need specialized tooling.

### model

Optional Claude model selection. Accepts short names or full model identifiers:

| Short name | Description |
|------------|-------------|
| `sonnet` | Claude Sonnet (default if omitted) |
| `opus` | Claude Opus |
| `haiku` | Claude Haiku |

Full model names (e.g., `claude-sonnet-4-20250514`) are also accepted.

### thinking

Optional thinking configuration that controls how Claude reasons about problems.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"adaptive"`, `"enabled"`, or `"disabled"` | `adaptive` lets the model decide when to think. `enabled` forces thinking on every turn. `disabled` turns thinking off entirely. |
| `budgetTokens` | number | Maximum tokens allocated to thinking when enabled. Only meaningful when `type` is `enabled` or `adaptive`. |

### effort

Optional effort level controlling how much work the agent puts into each response.

| Value | Description |
|-------|-------------|
| `low` | Quick, concise responses. |
| `medium` | Balanced depth and speed. |
| `high` | Thorough analysis and implementation. |
| `max` | Maximum effort on every turn. |

### secretMounts

Optional list of static file mounts (e.g., kubeconfig files, credentials) that are mounted into the runner container. These are defined in the agent's `seed.yaml` and mounted at specified container paths.

## Environment Variables

All supported environment variables, listed in order of precedence (env vars override config file values).

### Core

| Variable | Description |
|----------|-------------|
| `DEVBOX_DATA_ROOT` | Root directory for runtime data. Overrides `data_root` in config. |
| `DEVBOX_PUBLIC_WEB_BASE_URL` | Preferred public base URL for replay/preview links suggested in Telegram/Slack replies. |
| `DEVBOX_FRONTEND_URL` | Fallback base URL for replay/preview links when no public base URL is set; defaults to local frontend usage. |
| `ANTHROPIC_API_KEY` | Claude API key for the runner to authenticate with the Anthropic API. |
| `ANTHROPIC_BASE_URL` | Override the Anthropic API base URL (e.g., for proxies or Vertex AI). |
| `CLAUDE_CODE_OAUTH_TOKEN` | Alternative to API key: Claude Code OAuth token for authentication. |

### Telegram

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token. Overrides `telegram_bot_token` in config. |

### Slack

| Variable | Description |
|----------|-------------|
| `SLACK_BOT_TOKEN` | Slack bot token (`xoxb-...`). Overrides `slack_bot_token` in config. |
| `SLACK_APP_TOKEN` | Slack app-level token (`xapp-...`) for Socket Mode. Overrides `slack_app_token` in config. |

### GitHub (for repo seeding)

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub personal access token for cloning private repositories. |
| `GH_TOKEN` | Alternative to `GITHUB_TOKEN`. Used by the `gh` CLI. |
| `GITHUB_PAT` | Another alternative for GitHub authentication. |
| `GITHUB_APP_ID` | GitHub App ID for installation-based authentication. |
| `GITHUB_APP_PRIVATE_KEY` | GitHub App private key (PEM contents). |
| `GITHUB_APP_PRIVATE_KEY_FILE` | Path to a file containing the GitHub App private key. |
| `GITHUB_APP_INSTALLATION_ID` | Default GitHub App installation ID. |
| `GITHUB_APP_INSTALLATION_IDS` | Per-org installation IDs. Format: `"org1=id1,org2=id2"` or JSON `{"org1":"id1"}`. |

### Docker Compose Specific

| Variable | Default | Description |
|----------|---------|-------------|
| `DEVBOX_COMPOSE_CFG` | `./config.compose.yaml` | Path to the config file mounted into the controller container. |
| `HOME` | -- | Used to locate `~/.config/devbox-agent` for the secrets directory mount. |

## Full Config Example

A complete `config.yaml` demonstrating all sections:

```yaml
assistant_name: Devbox
telegram_bot_token: "123456:ABC-DEF..."
slack_bot_token: "xoxb-..."
slack_app_token: "xapp-..."
trigger_pattern: "^@Devbox\\b"
timezone: America/New_York
data_root: /data/devbox-agent

container:
  runtime: kubernetes
  image: devbox-runner:latest
  timeout: 5400000
  idle_timeout: 300000
  max_concurrent: 4
  max_output_size: 10485760
  kubernetes:
    namespace: devbox-agent
    kubeconfig: ~/.kube/config
    pvc_name: devbox-data
    data_mount_path: /data/devbox-agent
    service_account: devbox-runner
    image_pull_policy: IfNotPresent
    runner_resources:
      cpu: "2"
      memory: 4Gi
      ephemeral_storage: 10Gi

web:
  enabled: true
  port: 8080

agents:
  - name: main
    path: agents/main
  - name: researcher
    path: agents/researcher

channels:
  - id: "tg:-1001234567890"
    agents:
      - name: main
        trigger: "@Devbox"
        requires_trigger: true

  - id: "tg:user:*"
    agents:
      - name: main
        requires_trigger: false

  - id: "slack:C0123456789"
    agents:
      - name: researcher
        trigger: "@Devbox"
        requires_trigger: true

  - id: "web:*"
    agents:
      - name: main
        requires_trigger: false
```
