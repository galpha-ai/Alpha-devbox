# 002: Runner Workspace Layout Refactor

## Problem Statement

The runner still uses the legacy in-container path `/workspace/group`, even though the domain model has been refactored from "groups" to agent-driven, session-scoped sandboxes. That leaves the runtime layout harder to understand than it needs to be, especially because the editable repo root lives at `/workspace/group/workspace`.

The target layout is to separate session metadata from the editable repo checkout: `/session` for session control files, `/workspace` for repos and the working instruction file, and `/ipc` for controller-runner transport. The agent must start from `/workspace` so upward instruction discovery continues to work for `CLAUDE.md` and `AGENTS.md`.

## Initial State Snapshot

- `src/container-runner.ts` mounts the full host-side session root at `/workspace/group`, mounts IPC separately at `/workspace/ipc`, and writes `DEVBOX_RUN_DIR=/workspace/ipc/runs/{runId}`.
- `container/entrypoint.sh` reads `/workspace/group/seed-manifest.json`, clones repos into `/workspace/group/workspace`, uses `/workspace/group/workspace/.seeded` as the reseed sentinel, and then exports `WORKSPACE_DIR=/workspace/group/workspace`.
- `container/agent-runner/src/index.ts` still defaults `WORKSPACE_DIR` to `/workspace/group`, and `container/agent-runner/src/ipc-mcp-stdio.ts` still hardcodes `/workspace/ipc`.
- The host-side layout is already partly separated under `data/sessions/{agentName}/{sessionScopeKey}/`: `workspace/`, `.claude/`, `ipc/`, `seed-manifest.json`, and `CLAUDE.md` are distinct entries. This refactor can keep that disk layout and change the runner-facing mount contract first.

## Target Contract

| Concern | Host-side source | In-container path | Notes |
| --- | --- | --- | --- |
| Editable repos + agent cwd | `.../workspace/` | `/workspace` | Canonical working directory; `.seeded` lives here. |
| Session metadata | `.../` or projected metadata files | `/session` | Used for `seed-manifest.json` and any non-editable session metadata. |
| Controller-runner transport | `.../ipc/` | `/ipc` | Canonical IPC root; `DEVBOX_RUN_DIR` should resolve under this tree. |
| Claude state | `.../.claude/` | `/home/devbox/.claude` | Unchanged. |
| Shared global instructions | `agents/global/` | `/workspace/global` | Keep unchanged in this refactor to avoid mixing layout work with memory-loading behavior. |

The plan assumes the host-side session directory remains the source of truth. The refactor is about making the in-container contract match the domain model without rewriting the persisted on-disk schema.

## Plan

### Step 1: Define the runtime path contract
- **Action:** Document the target runner layout and invariants before code changes. The intended contract is: `/workspace` is the agent cwd and contains `.seeded` plus the primary `CLAUDE.md` or `AGENTS.md`; `/session` contains `seed-manifest.json` and other session metadata not required for upward discovery; `/ipc` contains controller-runner transport files; `/home/devbox/.claude` remains unchanged.
- **Result:** Expanded in this document. The canonical in-container paths are `/workspace`, `/session`, and `/ipc`, while the existing host-side session layout stays in place.
- **Notes:** Current controller sync logic only materializes `CLAUDE.md` into the session root. The implementation should either copy the active instruction file into the host-side `workspace/` directory before container start or bind-mount it directly into `/workspace`; do not assume `AGENTS.md` parity exists today.

### Step 2: Refactor controller mount targets
- **Action:** Update the controller-side mount assembly so it no longer mounts the full session root at `/workspace/group`. Split mounts by responsibility: session metadata mount, editable workspace mount, and IPC mount. The main code paths are `src/container-runner.ts` and any runtime-specific mount translation in `src/container-runtime.ts`.
- **Result:** Completed. `src/container-runner.ts` now mounts the session root at `/session` (read-only), the editable workspace at `/workspace`, and IPC at `/ipc`. Controller-generated run directories now resolve to `/ipc/runs/{runId}`.
- **Notes:** The implementation chose a read-only whole-directory `/session` mount as the compatibility layer. `/session/workspace` and `/session/ipc` remain visible through that metadata mount but are explicitly non-canonical; the runner uses the direct `/workspace` and `/ipc` mounts.

### Step 3: Refactor entrypoint seeding around `/workspace`
- **Action:** Update `container/entrypoint.sh` so seeding reads the manifest from `/session`, clones repos into `/workspace`, and uses `/workspace/.seeded` as the sentinel. Keep the existing GitHub token parsing and remote URL refresh behavior, but point it at the new locations.
- **Result:** Completed. `container/entrypoint.sh` now reads `${SESSION_DIR}/seed-manifest.json`, seeds `/workspace`, and keeps `/workspace/.seeded` as the one-time initialization gate.
- **Notes:** The existing remote-refresh loop already iterated over the workspace root and continued to work after switching `WORKSPACE_ROOT` to `/workspace`.

### Step 4: Start the agent from `/workspace`
- **Action:** Update the runner startup contract so `WORKSPACE_DIR=/workspace`, and make sure the instruction file visible to the coding agent is on the `/workspace` ancestry. The main paths are `container/agent-runner/src/index.ts` and `container/agent-runner/src/ipc-mcp-stdio.ts`.
- **Result:** Completed. The runner now defaults to `WORKSPACE_DIR=/workspace`, the MCP server uses `/ipc`, and the controller materializes `CLAUDE.md` plus optional `AGENTS.md` into the host-side workspace before container start.
- **Notes:** The instruction discovery rule is now: sync instructions into the session metadata root, then copy them into `workspace/` if missing so the SDK can discover them from the `/workspace` ancestry without overwriting user edits.

### Step 5: Update tests and docs
- **Action:** Update path assertions and examples that still reference `/workspace/group`, including `src/container-runtime.test.ts`, `src/container-runner.test.ts`, `docs/architecture.md`, `docs/SECURITY.md`, and any RFC/spec material that describes the runner mount layout.
- **Result:** Completed. Path-sensitive tests now assert `/session`, `/workspace`, `/ipc`, and the architecture/security/spec docs have been updated to describe the new contract.
- **Notes:** Updated docs include `docs/architecture.md`, `docs/SECURITY.md`, `docs/rfcs/002-container-runtime-abstraction.md`, `docs/specs/001-deployment-architecture/design.md`, and `docs/github-app-repo-auth.md`. Historical references in `docs/rfcs/001-agent-sandbox-architecture.md` were left intact because that document explicitly describes a prior design state.

### Step 6: Validate restart and reseed behavior
- **Action:** Verify that a container restart for the same session still reuses the mounted workspace, skips reseeding when `.seeded` exists, preserves `.claude` state, and refreshes GitHub-backed remotes with a fresh token. Also verify that deleting `.seeded` triggers a full reseed on the next run.
- **Result:** Partially completed. Automated validation passed for mount translation, run-dir generation, and workspace instruction materialization via targeted unit tests and `tsc --noEmit`.
- **Notes:** Executed `npm ci`, `npm test -- --run src/container-runner.test.ts src/container-runtime.test.ts`, and `npm run typecheck`. The automated suite covered the new controller-runner contract and Kubernetes mount translation. A manual end-to-end restart/reseed exercise that deletes `.seeded` inside a real runner container was not run as part of this change.

## Acceptance Criteria

- No runtime code, tests, or docs rely on `/workspace/group` as the canonical workspace root.
- Runner-side IPC defaults use `/ipc/...`, and controller-generated `DEVBOX_RUN_DIR` points at `/ipc/runs/{runId}`.
- Seeding and reseeding use `/workspace/.seeded` and do not require a nested `/workspace/group/workspace` directory.
- The coding agent starts with `cwd=/workspace`, and the instruction file needed for upward discovery is visible from that ancestry.
- Docker and Kubernetes runtime tests both pass with the new mount targets.

## References

- `src/container-runner.ts`
- `src/container-runtime.ts`
- `src/container-runtime.test.ts`
- `src/container-runner.test.ts`
- `container/entrypoint.sh`
- `container/agent-runner/src/index.ts`
- `container/agent-runner/src/ipc-mcp-stdio.ts`
- `docs/architecture.md`
- `docs/SECURITY.md`

## Guide for AI Agent

When updating this document during execution:
1. Fill in the **Result** field after each step with the actual outcome.
2. Add observations, issues, or decisions to **Notes**.
3. If the runtime path contract changes during implementation, update the Problem Statement and Step 1 before continuing.
4. If the instruction discovery approach changes, record the exact rule in Step 4 Notes.
5. Keep the document synchronized with any code or documentation changes made as part of the refactor.
