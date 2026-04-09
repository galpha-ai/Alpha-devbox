# Agent seed.yaml Reference

This document describes all available configuration options in an agent's `seed.yaml` file.

## Overview

Each agent definition in `agents/{name}/` requires a `seed.yaml` file that configures the agent's runtime environment, workspace repositories, model behavior, and secret mounts.

## Complete Example

```yaml
# Container image (optional)
image: your-registry/devbox-runner:latest

# Model configuration (optional)
model: opus

# Thinking configuration (optional)
thinking:
  type: adaptive
  budgetTokens: 10000  # only for type: "enabled"

# Effort level (optional)
effort: high

# Workspace repositories (required)
repos:
  - name: my-repo
    source: https://github.com/org/repo.git
    ref: main

# Secret mounts for kubeconfigs, credentials, etc. (optional)
secretMounts:
  - secretName: my-kubeconfig
    mountPath: /home/devbox/.kube
    hostPath: /home/user/.kube/my-cluster
```

## Configuration Fields

### `image` (optional)

Override the default runner container image.

**Type:** string

**Default:** Value from `CONTAINER_IMAGE` environment variable

**Example:**
```yaml
image: your-registry/devbox-runner:latest
```

### `model` (optional)

Specify which Claude model the agent should use.

**Type:** string

**Accepted values:**
- Model aliases: `"sonnet"`, `"opus"`, `"haiku"`, `"opusplan"`, `"default"`
- Full model names: `"claude-opus-4-6"`, `"claude-sonnet-4-6"`, etc.
- Extended context: `"sonnet[1m]"`, `"opus[1m]"`

**Precedence:** seed.yaml > environment variables > SDK default

**Environment variable alternative:** `ANTHROPIC_DEFAULT_SONNET_MODEL`, `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_HAIKU_MODEL`

**Example:**
```yaml
model: opus
```

### `thinking` (optional)

Configure Claude's extended thinking behavior.

**Type:** object with `type` field and optional `budgetTokens` field

**Supported types:**
- `adaptive`: Model determines when and how much to reason (Opus 4.6+, Sonnet 4.6+)
- `enabled`: Fixed thinking token budget (specify with `budgetTokens`)
- `disabled`: No extended thinking

**Default:** `{ type: 'adaptive' }` for supported models

**Environment variable alternative:** `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` (disables adaptive thinking)

**Examples:**

Adaptive thinking (recommended for Opus 4.6, Sonnet 4.6):
```yaml
thinking:
  type: adaptive
```

Fixed thinking budget:
```yaml
thinking:
  type: enabled
  budgetTokens: 8000
```

Disable extended thinking:
```yaml
thinking:
  type: disabled
```

### `effort` (optional)

Control how much effort Claude puts into its response.

**Type:** string

**Accepted values:** `"low"`, `"medium"`, `"high"`, `"max"`

**Default:** `"high"`

**Model support:**
- ✅ Opus 4.6
- ✅ Sonnet 4.6
- ❌ Older models

**Environment variable alternative:** `CLAUDE_CODE_EFFORT_LEVEL=low|medium|high`

**Use cases:**
- `low`: Fast, straightforward tasks (quick fixes, simple queries)
- `medium`: Balanced performance (Opus 4.6 default for Max/Team subscribers)
- `high`: Complex reasoning tasks (architecture decisions, debugging)
- `max`: Most thorough reasoning (critical analysis, security reviews)

**Example:**
```yaml
effort: high
```

### `repos` (required)

List of Git repositories to clone into the agent's workspace.

**Type:** array of objects

**Required fields:**
- `name`: Repository name (directory name in `/workspace/{name}`)
- `source`: Git URL (must be a remote URL, not a local path)

**Optional fields:**
- `ref`: Git ref to checkout (branch, tag, or commit SHA). Default: repository's default branch

**Example:**
```yaml
repos:
  - name: devbox-agent
    source: https://github.com/your-org/devbox-agent.git
    ref: main
  - name: my-library
    source: https://github.com/org/my-library.git
    ref: v1.2.3
```

### `secretMounts` (optional)

Mount Kubernetes Secrets or local directories as read-only volumes in the runner container.

**Type:** array of objects

**Required fields:**
- `secretName`: Kubernetes Secret name (for K8s runtime)
- `mountPath`: Container destination path
- `hostPath`: Local directory path (for Docker runtime fallback)

**Use cases:** Kubeconfigs, credentials, certificates, static configuration files

**See also:** [agent-secret-mounts.md](agent-secret-mounts.md) for detailed setup instructions

**Example:**
```yaml
secretMounts:
  - secretName: quant-dev-kubeconfig
    mountPath: /home/devbox/.kube
    hostPath: /home/youruser/.kube/quant-dev
```

## Configuration Precedence

For `model`, `thinking`, and `effort` options:

1. **seed.yaml** (highest priority - per-agent configuration)
2. **Environment variables** (global defaults)
3. **SDK defaults** (lowest priority)

This allows you to:
- Set global defaults via environment variables for all agents
- Override specific agents via their `seed.yaml`
- Leave some agents unspecified to use global defaults

## Example Configurations

### Fast Triage Agent

Use Haiku with low effort for quick, simple tasks:

```yaml
model: haiku
effort: low
thinking:
  type: disabled

repos:
  - name: support-tickets
    source: https://github.com/org/support-tickets.git
```

### Deep Analysis Agent

Use Opus with high effort for complex reasoning:

```yaml
model: opus
effort: high
thinking:
  type: adaptive

repos:
  - name: codebase
    source: https://github.com/org/codebase.git
```

### Balanced Development Agent

Use Sonnet with adaptive thinking for general development:

```yaml
model: sonnet
thinking:
  type: adaptive

repos:
  - name: app
    source: https://github.com/org/app.git
  - name: infra
    source: https://github.com/org/infra.git
```

## Validation

The system validates seed.yaml during agent initialization:

- `repos` must be a non-empty array
- Each repo must have `name` and `source` fields
- `source` must be a remote Git URL (http://, https://, ssh://, or git@)
- `model` must be a non-empty string (if specified)
- `thinking.type` must be `"adaptive"`, `"enabled"`, or `"disabled"` (if specified)
- `effort` must be `"low"`, `"medium"`, `"high"`, or `"max"` (if specified)
- `secretMounts` entries must have all three required fields

Invalid configurations log a warning and fall back to workspace-level defaults.

## Migration from Environment Variables

If you currently configure model/thinking/effort via environment variables, you can migrate to per-agent configuration:

**Before (environment variables):**
```bash
export ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-4-6
export CLAUDE_CODE_EFFORT_LEVEL=high
```

**After (seed.yaml):**
```yaml
model: opus
effort: high
thinking:
  type: adaptive
```

You can keep environment variables as global defaults and override only specific agents in their seed.yaml files.
