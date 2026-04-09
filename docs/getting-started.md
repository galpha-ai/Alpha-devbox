# Getting Started

This guide walks you through installing, configuring, and running Devbox Agent for the first time.

## Prerequisites

- **Node.js >= 20** (check with `node --version`)
- **Docker** (for Docker runtime) or a **Kubernetes cluster** (for K8s runtime)
- **A Claude API key** (`ANTHROPIC_API_KEY`) or a **Claude Code OAuth token** (`CLAUDE_CODE_OAUTH_TOKEN`)
- (Optional) **Telegram bot token** if using the Telegram channel
- (Optional) **Slack bot token + app token** if using the Slack channel

## Installation

```bash
git clone https://github.com/galpha-ai/devbox-agent-open.git
cd devbox-agent-open
npm install
```

Build the TypeScript source:

```bash
npm run build
```

## Configuration

### 1. Create your config file

Copy the example configuration and edit it:

```bash
cp config.example.yaml config.yaml
```

### 2. Set credentials

Set your bot tokens and API keys either in `config.yaml` or as environment variables. Environment variables take precedence over config file values.

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export TELEGRAM_BOT_TOKEN="123456:ABC..."   # if using Telegram
```

### 3. Minimal config.yaml

A working configuration with one agent and one channel:

```yaml
assistant_name: Devbox

container:
  runtime: docker
  image: devbox-runner:latest
  timeout: 5400000
  idle_timeout: 300000
  max_concurrent: 2

agents:
  - name: my-agent
    path: agents/my-agent

channels:
  # Telegram DM wildcard -- responds to all direct messages
  - id: "tg:user:*"
    agents:
      - name: my-agent
        requires_trigger: false
```

For web-only usage (no Telegram or Slack), use the web channel instead:

```yaml
assistant_name: Devbox

container:
  runtime: docker
  image: devbox-runner:latest

web:
  enabled: true
  port: 8080

agents:
  - name: my-agent
    path: agents/my-agent

channels:
  - id: "web:*"
    agents:
      - name: my-agent
        requires_trigger: false
```

## Creating Your First Agent

Each agent lives in its own directory under `agents/`. An agent directory requires two files: `CLAUDE.md` (instructions) and `seed.yaml` (metadata).

### 1. Create the agent directory

```bash
mkdir -p agents/my-agent
```

### 2. Write CLAUDE.md

This file defines the agent's persona and instructions. Claude reads it at the start of every session.

```bash
cat > agents/my-agent/CLAUDE.md << 'EOF'
# My Agent

You are a software development assistant working in an isolated sandbox.

## Guidelines

- Read existing code before making changes
- Run tests after modifications
- Create focused, well-scoped commits
EOF
```

### 3. Write seed.yaml

This file defines the sandbox environment: which repos to clone, which model to use, and how the agent should think.

```yaml
# agents/my-agent/seed.yaml

repos:
  - name: my-project
    source: https://github.com/your-org/your-repo.git
    ref: main

model: sonnet

thinking:
  type: adaptive

effort: high
```

**Field reference:**

| Field | Required | Description |
|-------|----------|-------------|
| `repos` | Yes | List of git repositories to clone into the sandbox workspace. Each entry has `name` (directory name), `source` (remote git URL), and optional `ref` (branch/tag/commit). |
| `image` | No | Override the default runner container image. |
| `model` | No | Claude model selection. Short names: `sonnet`, `opus`, `haiku`. Or a full model identifier like `claude-sonnet-4-20250514`. |
| `thinking` | No | Thinking configuration. `type` can be `adaptive` (model decides), `enabled` (always on), or `disabled`. Optional `budgetTokens` sets a token budget when thinking is enabled. |
| `effort` | No | Effort level: `low`, `medium`, `high`, or `max`. Controls how much work the agent puts into each response. |

### 4. (Optional) Add agent-specific skills

Place Claude Code skill files in `agents/my-agent/skills/`. These override the shared skills in `container/skills/`.

## Running

### Option 1: Kubernetes with Tilt

This is the recommended approach for development. Tilt watches source files and live-reloads both the controller and runner images.

**Prerequisites:**
- A local Kubernetes cluster (e.g., OrbStack, minikube, kind)
- [Tilt](https://tilt.dev/) installed
- Docker for building images

**Steps:**

```bash
# Set environment variables for secrets
export TELEGRAM_BOT_TOKEN="..."      # if using Telegram
export ANTHROPIC_API_KEY="..."

# Create the Kubernetes secrets and start Tilt
tilt up
```

Tilt will:
- Build the `devbox-controller` and `devbox-runner` Docker images
- Apply the Kubernetes manifests from `k8s/local`
- Create secrets from your environment variables
- Port-forward 8080 for the web interface (if enabled)
- Live-sync source changes without full rebuilds

Press `space` to open the Tilt UI in your browser to monitor resource status.

### Option 2: Docker Compose

Docker Compose runs the controller as a container that spawns runner containers via the Docker socket.

**Prerequisites:**
- Docker with Compose v2

**Steps:**

```bash
# Build the controller and runner images
docker build -f docker/controller.Dockerfile -t devbox-controller:latest .
docker build -f docker/runner.Dockerfile -t devbox-runner:latest .

# Create the data directory (must be identity-mapped between host and container)
sudo mkdir -p /data/devbox-agent
sudo chown "$(id -u):$(id -g)" /data/devbox-agent

# Copy and edit the compose config
cp config.example.yaml config.compose.yaml
# Edit config.compose.yaml with your settings

# Create .env with your secrets
cat > .env << 'ENVEOF'
TELEGRAM_BOT_TOKEN=your-token-here
ANTHROPIC_API_KEY=sk-ant-...
ENVEOF

# Start the stack
docker compose up
```

**Key environment variables for Docker Compose:**

| Variable | Default | Description |
|----------|---------|-------------|
| `DEVBOX_DATA_ROOT` | `/data/devbox-agent` | Host path for persistent data. Must be the same path inside the container. |
| `DEVBOX_COMPOSE_CFG` | `./config.compose.yaml` | Path to the config file mounted into the controller. |
| `ANTHROPIC_API_KEY` | -- | Claude API key. |
| `TELEGRAM_BOT_TOKEN` | -- | Telegram bot token. |

### Option 3: Direct Node.js

The simplest option for quick testing. Runs the controller directly on your machine.

**Prerequisites:**
- Docker must be running (the controller spawns runner containers via the Docker socket)
- The runner image must be built: `docker build -f docker/runner.Dockerfile -t devbox-runner:latest .`

**Steps:**

```bash
# With config.yaml in the project root
npm run dev
```

Or with a custom config path:

```bash
npm run dev -- --config path/to/config.yaml
```

The controller will start, connect to configured chat platforms, and begin listening for messages.

## Verifying It Works

### Telegram

1. Open a DM with your Telegram bot.
2. Send a message (e.g., "Hello, what can you do?").
3. The bot should acknowledge the message and spawn a runner container.
4. After a few seconds, you should see the agent's response.

In a group chat, prefix your message with the trigger (e.g., `@Devbox what can you do?`).

### Web Channel

If you enabled the web channel (`web.enabled: true`), send a test request:

```bash
# Create a conversation
curl -X POST http://localhost:8080/api/conversations \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test-user" \
  -d '{"title": "Test"}'

# Send a message (use the conversation ID from the response)
curl -X POST http://localhost:8080/api/conversations/<id>/messages \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test-user" \
  -d '{"content": "Hello, what can you do?"}'
```

### Troubleshooting

- **Container not starting:** Check that Docker is running and the runner image is built.
- **No response from agent:** Verify your `ANTHROPIC_API_KEY` is set and valid.
- **Telegram bot not responding:** Confirm `TELEGRAM_BOT_TOKEN` is correct and the bot is not blocked.
- **Config errors on startup:** The controller validates config via Zod and prints specific error paths. Check the startup logs.

## Next Steps

- [Architecture](architecture.md) -- understand the two-process model, session lifecycle, and data layout.
- [Configuration Reference](configuration.md) -- full documentation of every config field and environment variable.
- [Local Compose Setup](local-compose-setup.md) -- detailed Docker Compose deployment guide.
- [Local K8s Setup](local-k8s-setup.md) -- detailed Kubernetes development setup.
