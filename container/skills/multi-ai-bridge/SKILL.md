---
name: multi-ai-bridge
description: Bidirectional prompt bridge between four AI identities backed by two accounts — Claude Code & Claude (Anthropic account, via the claude CLI) and Codex & ChatGPT (OpenAI account, via the codex CLI). Send prompts to another AI, keep persistent two-way channels, have one AI direct another, run multi-round relays, or split a task across AIs and merge results. Use whenever the user asks to consult, delegate to, cross-check with, or orchestrate Codex, ChatGPT, or another Claude.
allowed-tools: Bash(node:*), Bash(codex:*), Bash(claude:*)
---

# Multi-AI Bridge

Bridge prompts between AI agents. You (Claude Code) are one side of the channel;
the `ai-bridge` script gives you the other three identities:

| Peer          | Backed by  | Account          | Behavior                                  |
| ------------- | ---------- | ---------------- | ----------------------------------------- |
| `codex`       | codex CLI  | ChatGPT/OpenAI   | Full coding agent, can edit the workspace |
| `chatgpt`     | codex CLI  | ChatGPT/OpenAI   | Chat-only persona, read-only sandbox      |
| `claude-code` | claude CLI | Claude/Anthropic | Full coding agent (a second Claude)       |
| `claude`      | claude CLI | Claude/Anthropic | Chat-only persona, read-only tools        |

Run everything through the bundled script:

```bash
BRIDGE=~/.claude/skills/multi-ai-bridge/scripts/ai-bridge.mjs

node "$BRIDGE" status   # verify CLIs are installed and both accounts are authenticated
```

Always run `status` first in a fresh session. If codex auth is missing, tell the
user how to fix it (see "Auth" below) instead of silently degrading.

## Send a prompt (bidirectional channel)

```bash
node "$BRIDGE" send codex "Refactor src/parser.ts to remove the recursion. Report what you changed."
node "$BRIDGE" send chatgpt "What are the tradeoffs of CRDTs vs OT for collaborative editing?"
node "$BRIDGE" send claude "Summarize this design doc: $(cat docs/design.md)" --channel design-review
```

- The reply is printed to stdout; run metadata goes to stderr.
- `--channel NAME` names a persistent conversation. The same channel resumes the
  peer's native session on every send, so follow-ups keep full context — this is
  what makes the channel bidirectional rather than one-shot.
- Default channel = peer name. Use `--fresh` to drop the session and start over.
- Other flags: `--cwd DIR` (where the peer works, default: current dir),
  `--model M`, `--timeout SEC` (default 1200), `--quiet`.

## Orchestration patterns

**One AI directs another (boss/worker).** You act as the dispatcher:

```bash
node "$BRIDGE" send codex "Implement the API client in src/client/ per docs/api.md. List files changed." --channel task-client
# read the reply, review the diff yourself with git, then follow up on the same channel:
node "$BRIDGE" send codex "Tests fail with <error>. Fix and re-run." --channel task-client
```

**Autonomous multi-round relay** — two peers talk to each other without you in
the middle (`--driver` makes one side the lead who instructs the other):

```bash
node "$BRIDGE" relay claude-code codex --goal "Agree on a schema migration plan for the orders table" --rounds 3
node "$BRIDGE" relay codex claude-code --driver a --goal "A directs B to write unit tests for src/utils/, then reviews them" --rounds 2
```

Each round is printed as it happens; the full exchange is saved to the channel
transcript.

**Split a task and merge.** Decompose yourself, farm out subtasks (run sends in
parallel with background Bash when they're independent), then merge:

```bash
node "$BRIDGE" send codex "Subtask 1: implement the backend endpoint ..." --channel split-be &
node "$BRIDGE" send claude-code "Subtask 2: implement the frontend form ..." --channel split-fe &
wait
# then review both replies/diffs and integrate.
```

**Cross-check.** Ask `chatgpt` and `claude` the same question on separate
channels and compare answers before deciding.

## Inspecting channels

```bash
node "$BRIDGE" channels          # list channels, turn counts, last activity
node "$BRIDGE" log task-client --tail 30
```

Transcripts and session state live under `/workspace/.ai-bridge/` (persists
across container restarts; override with `AI_BRIDGE_HOME`).

## Auth

- **Claude/Anthropic account**: shared with your own runtime — `~/.claude`
  credentials, `CLAUDE_CODE_OAUTH_TOKEN`, or `ANTHROPIC_API_KEY`.
- **ChatGPT/OpenAI account**: the codex CLI reads `~/.codex/auth.json`
  (created by `codex login` on the user's machine and mounted into the
  container via the agent's `secretMounts`), or `OPENAI_API_KEY`.

## Guidelines

- Report which AI produced which result — never present a peer's output as your own.
- Review a coding peer's changes (`git diff`/tests) before telling the user they're done.
- Peers share your filesystem. Point `--cwd` at the intended repo, and don't run
  two coding peers concurrently in the same repo.
- Long tasks: raise `--timeout`; codex/claude runs are synchronous.
