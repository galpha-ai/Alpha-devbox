# Local Docker Compose Setup

How to run the devbox-agent stack locally using Docker Compose.

## Prerequisites

- Docker with Compose v2
- [just](https://github.com/casey/just) command runner
- Node.js >= 20 (for building TypeScript)
- A chat platform bot configured (Slack and/or Telegram)

## 1. Create a Slack Bot (if using Slack)

1. Go to https://api.slack.com/apps > **Create New App** > **From scratch**
2. Enable **Socket Mode** (Settings > Socket Mode > toggle On)
   - Generate an App-Level Token with scope `connections:write` — this is your `SLACK_APP_TOKEN` (`xapp-...`)
3. Add **Bot Token Scopes** (Features > OAuth & Permissions > Bot Token Scopes):
   - `chat:write` — send messages
   - `channels:history`, `channels:read` — public channel reads + discovery
   - `groups:history`, `groups:read` — private channel reads + discovery
   - `im:history`, `im:read`, `im:write` — direct-message event compatibility in Slack app settings
   - `mpim:history`, `mpim:read` — multi-party DM event compatibility in Slack app settings
   - `users:read` — resolve user display names
   - `reactions:write` — required if you want the bot's Slack status/typing reactions
4. **Subscribe to bot events** (Features > Event Subscriptions > Subscribe to bot events):
   - `message.channels`
   - `message.groups`
   - `message.im`
   - `message.mpim`
5. **Install to Workspace** (Settings > Install App) — copy the Bot User OAuth Token (`xoxb-...`) as `SLACK_BOT_TOKEN`
6. Invite the bot to a channel: `/invite @YourBotName`
7. Note the **channel ID** (click channel name > About > bottom of panel, or from the URL)
8. In `config.compose.yaml`, bind Slack with a specific `slack:<channel_id>` entry. Current config docs do not describe a Slack DM wildcard binding.

## 2. Set Up Environment

### Data directory

The data root must be identity-mapped (same absolute path on host and inside the controller container) because the controller passes these paths to `docker run -v` when spawning runners.

```sh
sudo mkdir -p /data/devbox-agent
sudo chown "$(id -u):$(id -g)" /data/devbox-agent
```

To use a different path, set `DEVBOX_DATA_ROOT` in `.env`.

### `.env` file

Create `.env` in the repo root. The justfile loads it automatically (`set dotenv-load`).

```sh
# --- Chat platform (include at least one) ---
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
# TELEGRAM_BOT_TOKEN=...

# --- Claude auth (one of these) ---
ANTHROPIC_API_KEY=sk-ant-...
# CLAUDE_CODE_OAUTH_TOKEN=...

# --- GitHub auth for private repo cloning (optional) ---
# Option A: PAT
# GITHUB_TOKEN=ghp_...

# Option B: GitHub App (see docs/github-app-repo-auth.md)
# GITHUB_APP_ID=123456
# GITHUB_APP_INSTALLATION_IDS="org-name=installation-id"
# GITHUB_APP_PRIVATE_KEY_FILE=/path/to/pem
```

## 3. Configure the Stack

```sh
cp config.compose.yaml.example config.compose.yaml
```

Edit `config.compose.yaml`:

```yaml
assistant_name: YourBotName

timezone: America/New_York

container:
  image: devbox-runner:latest
  timeout: 5400000
  idle_timeout: 300000
  max_concurrent: 2
  max_output_size: 10485760

agents:
  - name: main
    path: agents/main

channels:
  # Slack channel — replace with your channel ID
  - id: "slack:C0XXXXXXXXX"
    agents:
      - name: main
        trigger: "@YourBotName"
        requires_trigger: true

  # Telegram group (optional)
  # - id: "tg:-100XXXXXXXXXX"
  #   agents:
  #     - name: main
  #       trigger: "@YourBotName"
  #       requires_trigger: true

  # Telegram DMs (optional)
  # - id: "tg:user:*"
  #   agents:
  #     - name: main
  #       requires_trigger: false
```

Only include channel types you have tokens for. The controller validates at startup that the required tokens are present for each channel prefix (`slack:*` needs `SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN`, `tg:*` needs `TELEGRAM_BOT_TOKEN`). For Telegram setup, use `/chatid` to copy a group or DM identifier and `/ping` to confirm the bot is online.

## 4. Build and Start

```sh
# Build both controller and runner images
just build-images

# Start the stack
just compose-up
```

Verify the controller is running:

```sh
just compose-logs controller
```

You should see `Slack channel connected` (or `Telegram channel connected`) in the output.

## 5. Test It

In Slack, go to the configured channel and send:

```
@YourBotName hello
```

If using threads: start a thread and mention the bot. Each thread gets its own isolated sandbox and session.

## Common Operations

| Command | Description |
|---|---|
| `just compose-up` | Start the stack (detached) |
| `just compose-down` | Stop the stack |
| `just compose-logs` | Tail all logs |
| `just compose-logs controller` | Tail controller logs only |
| `just compose-clean` | Stop stack and delete all persisted data |
| `just compose-clean-data` | Delete persisted data without stopping |
| `just build-images` | Rebuild both images |

## Environment Variables Reference

All set via `.env` or shell. The justfile loads `.env` automatically.

| Variable | Default | Description |
|---|---|---|
| `DEVBOX_DATA_ROOT` | `/data/devbox-agent` | Host path for persistent data (must be identity-mapped) |
| `DEVBOX_COMPOSE_CFG` | `./config.compose.yaml` | Path to config file mounted into controller |
| `SLACK_BOT_TOKEN` | — | Slack bot OAuth token (`xoxb-...`) |
| `SLACK_APP_TOKEN` | — | Slack app-level token for Socket Mode (`xapp-...`) |
| `TELEGRAM_BOT_TOKEN` | — | Telegram bot token |
| `ANTHROPIC_API_KEY` | — | Anthropic API key for Claude |
| `CLAUDE_CODE_OAUTH_TOKEN` | — | Alternative: Claude OAuth token |
| `GITHUB_TOKEN` | — | GitHub PAT for private repo cloning |

For GitHub App auth, see `docs/github-app-repo-auth.md`.

## Troubleshooting

**`pull access denied for devbox-controller`** — Images aren't built yet. Run `just build-images`.

**`Missing Slack credentials`** — Config has `slack:*` channels but `SLACK_BOT_TOKEN` or `SLACK_APP_TOKEN` is not set. Check `.env`.

**`Missing telegram bot token`** — Config has `tg:*` channels but `TELEGRAM_BOT_TOKEN` is not set. Remove the `tg:*` channel entries from config or set the token.

**Runner containers fail to clone repos** — Check GitHub token/app auth configuration (`GITHUB_TOKEN` or GitHub App env vars). See `docs/github-app-repo-auth.md`.

**Path mismatch errors in runners** — The data root must be the same absolute path on host and in the controller container. Verify `DEVBOX_DATA_ROOT` is identity-mapped in `docker-compose.yml`.
