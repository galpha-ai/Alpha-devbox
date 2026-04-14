# Getting Started

This is the step-by-step deployment guide for a human developer or another coding agent.

Follow the sections in order. If you only want one path, start with `Path 1: Fastest First Run`.

## Choose a Deployment Path

1. **Path 1: Fastest First Run**
   Direct Node.js controller + Docker runner + built-in Web channel. Best first deployment.
2. **Path 2: Docker Compose**
   Good for a local team stack or controller-level verification.
3. **Path 3: Kubernetes with Tilt**
   Best for full development and production-like behavior.

If you are unsure, choose Path 1 first.

## Step 0: Verify Prerequisites

You need:

- Node.js 20 or newer
- Docker for Path 1 or Path 2, or a Kubernetes cluster for Path 3
- One Claude credential:
  - `ANTHROPIC_API_KEY`, or
  - `CLAUDE_CODE_OAUTH_TOKEN`
- Optional chat credentials:
  - `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN`
  - `TELEGRAM_BOT_TOKEN`

Verify the basics:

```bash
node --version
docker info
```

Expected result:

- `node --version` prints `v20.x` or newer
- `docker info` succeeds if you are using Path 1 or Path 2

If Docker is unavailable, skip Path 1 and Path 2 and use Path 3.

## Optional: Connect Slack or Telegram

You can start with the built-in Web channel only, then add Slack or Telegram later.

### Slack

Slack support uses **Socket Mode** and needs both of these secrets:

- `SLACK_BOT_TOKEN` (`xoxb-...`)
- `SLACK_APP_TOKEN` (`xapp-...`, created with `connections:write`)

**Recommended path:** create the Slack app **from a manifest** instead of clicking through each setting manually.

1. Go to https://api.slack.com/apps
2. Click **Create New App**
3. Choose **From an app manifest**
4. Pick your workspace
5. Paste a manifest like this:

```json
{
  "display_information": {
    "name": "Devbox Agent",
    "description": "AI coding agent with isolated sandboxes",
    "background_color": "#2c2d30"
  },
  "features": {
    "bot_user": {
      "display_name": "Devbox",
      "always_online": true
    }
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "channels:history",
        "channels:read",
        "chat:write",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "im:write",
        "mpim:history",
        "mpim:read",
        "users:read",
        "reactions:write"
      ]
    }
  },
  "settings": {
    "event_subscriptions": {
      "bot_events": [
        "message.channels",
        "message.groups",
        "message.im",
        "message.mpim"
      ]
    },
    "socket_mode_enabled": true
  }
}
```

After the app is created:

1. In **Settings → Socket Mode**, create an app-level token with `connections:write` and save it as `SLACK_APP_TOKEN`
2. In **OAuth & Permissions**, click **Install to Workspace** and save the bot token as `SLACK_BOT_TOKEN`
3. Invite the bot to the target channel with `/invite @Devbox`

If you prefer to configure Slack manually instead of using a manifest, make sure the app includes these minimum pieces:

- bot token scopes for message reading and replying, such as:
  - `chat:write`
  - `channels:history`, `channels:read`
  - `groups:history`, `groups:read`
  - `im:history`, `im:read`, `im:write`
  - `mpim:history`, `mpim:read`
  - `users:read`
- bot events:
  - `message.channels`
  - `message.groups`
  - `message.im`
  - `message.mpim`
- `socket_mode_enabled: true`

If you want Slack status/typing reactions from the bot, also grant `reactions:write`.

In `config.yaml`, bind a specific Slack channel with `slack:<channel_id>`, for example:

```yaml
channels:
  - id: "slack:C0123456789"
    agents:
      - name: main
        trigger: "@Devbox"
        requires_trigger: true
```

Current docs and config only document **specific Slack channel bindings**. Do not assume a Slack DM wildcard binding exists.

### Telegram

Telegram support needs one secret:

- `TELEGRAM_BOT_TOKEN`

The bot exposes two useful commands:

- `/chatid` — prints the `tg:...` ID you can copy into config
- `/ping` — confirms the bot is online

Channel ID patterns:

- Telegram group or supergroup: `tg:<chat_id>`
- Telegram DM wildcard: `tg:user:*`
- Specific Telegram DM: `tg:user:<user_id>`

Example:

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
```

Use `tg:user:*` when you want the bot to handle Telegram DMs by default.

### Local fast-start config for Slack + Telegram

If you want the same local web demo plus chat channels, use the checked-in local template files:

- `config.chat-local.yaml.example` → copy to `config.chat-local.yaml`
- `.env.chat-local.example` → copy to `.env.chat-local`

That local chat config keeps `web:*` enabled, adds one sample Slack channel binding, one sample Telegram group binding, and `tg:user:*` for Telegram DMs.

### Where to find the full setup details

- See [Configuration](configuration.md) for all channel config fields and channel ID formats.
- See [Local Docker Compose Setup](local-compose-setup.md) for a fuller local stack walkthrough.

## Path 1: Fastest First Run

This is the shortest path to a working local deployment.

### 1. Clone and install

```bash
git clone https://github.com/galpha-ai/Alpha-devbox.git
cd Alpha-devbox
npm install
```

Expected result:

- dependencies install successfully
- `npm install` completes without errors

### 2. Add local credentials

Copy the example env file and fill one Claude credential:

```bash
cp .env.example .env.local
```

At minimum set one of:

- `ANTHROPIC_API_KEY`
- `CLAUDE_CODE_OAUTH_TOKEN`

Optional:

- `ANTHROPIC_BASE_URL` if you use a proxy / compatible endpoint
- `DEVBOX_DISABLE_SESSION_RESUME=1` for cleaner local smoke runs

This local path is already preconfigured for the built-in web chat workspace and local demo agent. No extra `config.yaml` is required.

If you also want Slack and/or Telegram on the same local stack, prepare these optional files:

```bash
cp config.chat-local.yaml.example config.chat-local.yaml
cp .env.chat-local.example .env.chat-local
```

Then replace the placeholder Slack channel ID / Telegram chat ID in `config.chat-local.yaml`, fill the tokens in `.env.chat-local`, and start with:

```bash
npm run dev:chat-local
```

### 3. Start the local web stack

```bash
npm run dev
```

If your shell exports other Claude / Anthropic variables globally, clear them for this project first so local `.env.local` stays authoritative:

```bash
unset ANTHROPIC_AUTH_TOKEN ANTHROPIC_BASE_URL CLAUDE_CODE_OAUTH_TOKEN
npm run dev
```

If you want a completely fresh local state, stop the stack and remove the data
directory explicitly before restarting:

```bash
rm -rf .devbox-local
npm run dev
```

If you want to prebuild the runner image yourself first, you can also run:

```bash
docker build -f docker/runner.Dockerfile -t devbox-runner:latest .
```

Expected result:

- the script refreshes the local `devbox-runner:latest` image before start
- the backend starts on `http://127.0.0.1:18092`
- the web chat workspace starts on `http://127.0.0.1:5175/`
- no Slack or Telegram tokens are required for this path

### 4. Verify the deployment

In a second terminal, check health:

```bash
curl http://127.0.0.1:18092/api/devbox/health
```

Then open:

```bash
open http://127.0.0.1:5175/
```

Optional automated smoke test:

```bash
npm run e2e:web-local
```

Expected result:

- health endpoint returns `{"status":"ok"}`
- `/` loads the chat UI
- sending a prompt produces an assistant reply
- markdown-table replies render charts inline

At this point, the local browser path is working.

## Path 2: Docker Compose

Use this when you want a local multi-container stack instead of running the controller directly on your machine.

### 1. Prepare the data root

```bash
sudo mkdir -p /data/devbox-agent
sudo chown "$(id -u):$(id -g)" /data/devbox-agent
```

### 2. Create the compose config

```bash
cp config.compose.yaml.example config.compose.yaml
```

Edit `config.compose.yaml` for your agent and channels.

For a web-only stack, make sure it includes:

```yaml
web:
  enabled: true
  port: 8080

channels:
  - id: 'web:*'
    agents:
      - name: example
        requires_trigger: false
```

### 3. Create `.env`

```bash
cat > .env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-...
EOF
```

Add Slack or Telegram tokens only if you configure those channels.

### 4. Build and start

```bash
just build-images
just compose-up
```

### 5. Verify

```bash
just compose-logs controller
curl http://localhost:8080/health
```

Expected result:

- controller container starts cleanly
- runner containers can be spawned
- web health endpoint responds

For the complete Compose runbook, see [Local Docker Compose Setup](local-compose-setup.md).

## Path 3: Kubernetes with Tilt

Use this when you want the full controller -> runner pod flow, RBAC behavior, and persistent-volume behavior.

### 1. Prepare the environment

You need:

- a local Kubernetes cluster such as OrbStack, minikube, or kind
- Tilt installed
- Docker available for image builds

### 2. Export secrets

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Add Slack or Telegram tokens only if your config uses those channels.

### 3. Start Tilt

```bash
just dev-k8s
```

### 4. Verify

Expected result:

- Tilt builds controller and runner images
- Kubernetes resources apply successfully
- the controller becomes healthy
- runner pods can be created from incoming requests

For the complete Kubernetes runbook, see [Local Kubernetes Development with Tilt](local-k8s-setup.md).

## Common Problems

- **`docker: command not found`**
  Install Docker or switch to Path 3.
- **Controller starts but agent never responds**
  Check Claude credentials and confirm the runner image exists.
- **Config validation fails on startup**
  Re-read `config.yaml` and compare it with [Configuration](configuration.md).
- **Runner fails to clone repos**
  Check the repo URLs in `seed.yaml` and any required GitHub credentials.
- **Slack or Telegram messages do nothing**
  Confirm the channel is present in config and the required bot tokens are exported.

## Next Docs

- [Architecture](architecture.md) for the controller/runner model
- [Configuration](configuration.md) for every config field
- [Local Docker Compose Setup](local-compose-setup.md) for a fuller Compose deployment
- [Local Kubernetes Development with Tilt](local-k8s-setup.md) for the full K8s workflow
