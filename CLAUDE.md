# Devbox Agent

## Architecture

Use `docs/architecture.md` as the code map. Read it before making code changes or engaging in design discussion. Keep it up to date.

## Development

- `npm run dev` — start controller in development mode
- `npm test` — run tests
- `npm run typecheck` — check types
- `npm run format:check` — check formatting

## Project Structure

- `src/` — Controller process (message routing, session management, container lifecycle)
- `container/` — Runner process (Claude Code SDK invocation, IPC, workspace management)
- `agents/` — Agent definitions (CLAUDE.md + seed.yaml per agent)
- `k8s/` — Kubernetes deployment manifests (kustomize)
- `docs/` — Documentation
