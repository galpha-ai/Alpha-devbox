# GitHub App Token Auth for Workspace Repos

How devbox-agent authenticates to private GitHub repos when seeding runner container workspaces.

## Overview

Runner containers need to `git clone` private repos listed in each agent's `seed.yaml`. Rather than using long-lived PATs, we use a **GitHub App** that issues short-lived installation tokens scoped per-org. Tokens are generated on demand by the controller process, written into the run `input.json`, then copied by the entrypoint into a root-only temp file for the `gh` wrapper.

## How It Works

```
Controller process                        GitHub API
──────────────────                        ──────────
1. Read PEM private key from env/file
2. For each unique GitHub org in the seeded repo set:
   a. Look up installation ID for that org
   b. Sign a JWT (RS256) with APP_ID + PEM       ──>  POST /app/installations/{id}/access_tokens
   c. Receive short-lived token (1 hour)          <──  { token: "ghs_...", expires_at: "..." }
   d. Cache token in memory (reuse until expiry - 60s)
3. Pass tokens to container as `DEVBOX_GIT_AUTH_TOKENS` in run `input.json`

Runner container (entrypoint.sh)
────────────────────────────────
4. Parse tokens from run `input.json`
5. For each repo in seed-manifest.json:
   a. Extract GitHub owner from source URL
   b. Look up token for that owner
   c. Rewrite source URL:  git@github.com:Org/repo.git
                         -> https://x-access-token:<token>@github.com/Org/repo.git
   d. git clone
6. Persist the owner->token map to `/tmp/.gh-tokens.json` with mode `0600`
7. `gh` calls go through `/usr/local/bin/gh`, which selects the matching token from that file using `--repo`, `GH_REPO`, or `git remote origin`
```

## Setup

### Prerequisites

1. A GitHub App installed on each org that owns repos referenced from agent `seed.yaml` files
2. The App's private key (PEM file)
3. The installation ID for each org (find it in the App's installation settings or via the GitHub API)

### Configuration

Add these to `.env` (loaded by justfile via `dotenv-load`):

```bash
# GitHub App ID (shared across all orgs)
GITHUB_APP_ID=<your-app-id>

# Private key -- pick one method:
GITHUB_APP_PRIVATE_KEY_FILE=/path/to/github-app.pem
# or inline (escape newlines):
# GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\nMIIE...\n-----END RSA PRIVATE KEY-----"

# Installation ID per org (owner name uppercased, hyphens replaced with underscores)
GITHUB_APP_INSTALLATION_ID_MY_ORG=123456789
GITHUB_APP_INSTALLATION_ID_ANOTHER_ORG=987654321
```

For Docker Compose, the private key PEM file is mounted from `~/.config/devbox-agent/github-app.pem` into the container at `/run/devbox-secrets/github-app.pem` (see `docker-compose.yml` line 60). The default `GITHUB_APP_PRIVATE_KEY_FILE` points there.

### Alternative: installation ID formats

Instead of per-owner env vars, you can use a single variable:

```bash
# Comma-separated
GITHUB_APP_INSTALLATION_IDS="my-org=123456789,another-org=987654321"

# Or JSON
GITHUB_APP_INSTALLATION_IDS='{"my-org":"123456789","another-org":"987654321"}'
```

There is also a default fallback `GITHUB_APP_INSTALLATION_ID` that applies to all orgs without a specific mapping.

## Onboarding a New Repo

### Step 1: Ensure the GitHub App is installed on the org

Go to the GitHub App settings page and install it on the target org. Note the **installation ID** from the URL or API response.

### Step 2: Add the installation ID to `.env`

The env var name is `GITHUB_APP_INSTALLATION_ID_<OWNER>`, where `<OWNER>` is the GitHub org/user name **uppercased** with **hyphens replaced by underscores**.

Examples:
| GitHub owner       | Env var name                                  |
|--------------------|-----------------------------------------------|
| `my-org`           | `GITHUB_APP_INSTALLATION_ID_MY_ORG`           |
| `another-org`      | `GITHUB_APP_INSTALLATION_ID_ANOTHER_ORG`      |
| `my-org`           | `GITHUB_APP_INSTALLATION_ID_MY_ORG`           |

### Step 3: Add the repo to an agent seed manifest

Add the repo to the relevant agent's `seed.yaml`:

```yaml
repos:
  - name: my-new-repo
    source: git@github.com:MyOrg/my-new-repo.git
    ref: main    # optional
```

The source URL can be SSH (`git@github.com:...`) or HTTPS (`https://github.com/...`) -- the entrypoint rewrites both formats to HTTPS with the token injected.

### Step 4: Clear the seed sentinel for an existing session workspace

Workspace seeding only runs once per session workspace (guarded by a `.seeded` file). To pick up the new repo in an existing session:

```bash
# Local dev
rm data/sessions/<agentName>/<encodedSessionScopeKey>/workspace/.seeded

# Docker Compose (default data root)
rm /data/devbox-agent/data/sessions/<agentName>/<encodedSessionScopeKey>/workspace/.seeded
```

On next container run, all repos will be re-seeded. Local-source repos are rsynced (fast), remote repos are re-cloned.

### Step 5: Restart

```bash
# Local dev
just dev

# Docker Compose
just compose-down && just compose-up
```

## PR Creation via `gh` CLI

The runner container includes the GitHub CLI (`gh`) behind a wrapper at `/usr/local/bin/gh`. This allows the agent to create PRs using `gh pr create` after completing coding tasks, even when the workspace includes repos from multiple GitHub orgs.

### How auth works

During container startup, `entrypoint.sh` exports a fallback `GH_TOKEN` and writes the full owner-token map to `/tmp/.gh-tokens.json`. The `gh` wrapper resolves the repo owner from `--repo`, `GH_REPO`, or `git remote origin`, then exports the matching `GH_TOKEN`/`GITHUB_TOKEN` just for the delegated `gh` process. The agent-runner's bash sanitization hook intentionally allows `GH_TOKEN` and `GITHUB_TOKEN` through to subprocesses (unlike `ANTHROPIC_API_KEY` which is always stripped). This is safe because the GitHub token is short-lived (~1 hour) and scoped to specific repos via the GitHub App installation.

### Required GitHub App permissions

The GitHub App must have these permissions for PR creation to work:

| Permission | Access | Purpose |
|---|---|---|
| **Contents** | Read & write | Push branches |
| **Pull requests** | Read & write | Create and manage PRs |
| **Metadata** | Read-only | Required by GitHub (always enabled) |

Configure these in the GitHub App settings page under "Permissions & events" > "Repository permissions".

### Limitations

- The installation tokens are still minted once at container startup and expire after ~1 hour. If the container runs longer, both git remotes and `gh` commands will eventually fail with auth errors until a fresh container is started.
- The wrapper can only auto-select a token when it can infer the repo owner from `--repo`, `GH_REPO`, or `git remote origin`. Commands that target a repo through some other mechanism fall back to the inherited `GH_TOKEN`.

## Relevant Source Files

| File | What it does |
|------|-------------|
| `src/container-runner.ts` | Token resolution (`resolveGitHubSeedTokens`), JWT signing, seed manifest generation, secret passing via run input |
| `container/entrypoint.sh` | Token parsing, URL rewriting, `git clone` execution, `/tmp/.gh-tokens.json` persistence |
| `container/gh-wrapper.sh` | Owner detection for `gh` and per-invocation `GH_TOKEN` selection |
| `agents/<name>/seed.yaml` | Declares which repos are seeded into each agent workspace |
| `docker-compose.yml` | Env var passthrough and PEM file mount |

## Fallback: Direct Token

If GitHub App auth is not configured, the controller checks for a direct PAT in this order:

1. `DEVBOX_GIT_AUTH_TOKEN`
2. `GITHUB_TOKEN`
3. `GH_TOKEN`
4. `GITHUB_PAT`

If found, this single token is used for all repos regardless of owner. This is simpler but less secure (long-lived, broader scope).
