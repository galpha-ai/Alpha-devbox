# Hand-off Document: AI Research Agent Design Session

**Session Date:** 2026-04-17
**Branch:** `claude/ai-research-agent-design-6cY8x`
**Status:** Research complete, RFC partially drafted, needs sections 4.3–13 completed

---

## 1. Original User Ask (verbatim intent)

The user has been using Claude Code heavily for ~2 months (~200k LOC written by Claude, not the user). Observation: writing the same dispatch instructions repeatedly to the AI worker is tedious. Every project cycles through the same kind of "run next backtest with refined idea" type of tasks.

**Core request:**

> Plan a question. AI that is very specialized in mimic human in his question style based on his tasks way of interacting as AI worker. To create a imitation human acts version of task dispatcher. That behaves similar to the human who give priority to the existing All the the style AI worker. To write code first give me a very deep research thinking PhD and the professor level insight on how you would design this The architect You can consider all the agent harness framework in terms of continuum learning. Such as, Nous research's Hermes agent, Open Cloud, and, Andrew Kaplatzi's auto research LLM Wiki.
>
> Look at alpha-devbox as the open source version of managed claude agent; and the dependency to quant research as an example on the human task generator can behavior similar to the boss human, that can give iterative numerical experiment plan like run next backtest with a refined idea; to make the two agent system continuously keep working.

**Supporting references provided by user:**

1. **Nous Research's Hermes Agent** — https://github.com/nousresearch/hermes-agent and https://hermes-agent.nousresearch.com/
2. **User's own article** (key thesis): *"Humans belong on the compounding outer loop. AI belongs on the recursive inner loop."*
   - The Strait of Hormuz vs. Anthropic eval table analogy
   - Claude Mythos Preview under Project Glasswing (77.8% SWE-bench Pro, 82.0% Terminal-Bench 2.0)
   - Three things humans still contribute: offline truth, taste, priority/weighting
   - Self-recursive improvement requires a verifiable environment
3. **Alpha-devbox** as the open-source orchestration layer (this repo)
4. **Quant research** as the canonical concrete example (natural-language → backtest → refined-backtest loop)

**Deliverable requested:**
- PhD / professor-level deep architectural design
- A two-agent system (boss/worker) that continuously keeps working
- Must integrate with alpha-devbox primitives
- Must borrow from Hermes Agent's skill + memory patterns

---

## 2. Research Findings Summary

### 2.1 Alpha-devbox Architecture (verified via Explore agent)

**Two-process model:**
- **Controller** (`src/`): Node.js, long-lived, routes chat messages, manages SQLite state, spawns containers per session, never runs agent logic itself.
- **Runner** (`container/agent-runner/`): Node.js inside container, per-session long-lived, invokes Claude Code SDK via `query()` with `MessageStream`, blocks between turns polling IPC.

**IPC is filesystem-based** — no shared memory. JSON files in `data/sessions/{agentName}/{sessionScopeKey}/ipc/`.

**Session scope = composite triple:** `(channelId, threadId, agentName)`. SQLite-backed.

**Agent definitions** (`agents/{name}/`):
- `CLAUDE.md` (required) — persona & instructions
- `seed.yaml` (required) — model, repos to clone, secretMounts, thinking config
- `skills/` (optional) — Claude Code skills scoped to this agent

**Concrete example agent:** `agents/quant-agent/` — seeds `crypto-quant` repo, runs in `/workspace/crypto-quant`, focused on `crates/poly-strat-starter` and `crates/trade-server`.

**Key primitives available to build on:**
- **`schedule_task` MCP tool** (`container/agent-runner/src/ipc-mcp-stdio.ts`) — agent can schedule its own future runs (cron, interval, once) in either `group` (conversation context) or `isolated` (fresh session) mode.
- **`send_message` MCP tool** — agent can push messages mid-query without terminating.
- **Workspace persistence** — bind-mounted `/workspace` survives container exits, so experiment code/results accumulate.
- **Session resume** — SDK `query(prompt, sessionId)` resumes full conversation context.
- **Task scheduler** (`src/task-scheduler.ts`) — polls SQLite for due tasks, spawns containers.

**Architectural invariants (must respect):**
1. Containers are long-lived per session; volumes outlive containers
2. Controller never executes agent logic
3. IPC identity is directory-based
4. One active container per session at a time
5. Global concurrency cap via `MAX_CONCURRENT_CONTAINERS`

### 2.2 Hermes Agent (Nous Research) Findings

**Multi-layer system prompt:**
- `SOUL.md` — core personality (loaded first)
- `USER.md` — user profile (~500 tokens)
- `AGENTS.md` — project context
- `MEMORY.md` — learned patterns (~800 tokens)

**Skills system (procedural memory):**
- Structured as directories with `SKILL.md` (YAML frontmatter + Markdown)
- Compatible with agentskills.io open standard
- Auto-extracted after complex tasks (5+ tool calls)
- Lazy-loaded — compact list at session start, full content only when needed
- Every `SKILL.md` auto-registers as a slash command

**Memory / continuum learning:**
- Core memory files (`MEMORY.md`, `USER.md`) injected at session start
- SQLite FTS5 for session search
- Gemini Flash summarization
- Periodic "nudge" prompt asks agent to evaluate what's worth persisting
- External memory plugins: Honcho, Mem0, Supermemory, RetainDB, etc.
- Honcho does dialectic user modeling — builds persistent user representation across sessions

**ReAct loop:** Observation → Reasoning → Action. Synchronous `while api_call_count < max_iterations` (default 90).

**Subagent delegation:** Two task types — `delegate_task` (reasoning) vs `execute_code` (mechanical). Each subagent gets fresh conversation, zero parent context.

**MCP integration:** Dynamic tool discovery, `notifications/tools/list_changed`, sampling/createMessage for external LLM requests.

---

## 3. Design Delivered So Far: RFC 003

**Location:** `docs/rfcs/003-ai-research-agent-design.md`
**Completed sections:** Abstract, TOC, §1 Motivation, §2 Theoretical Foundation (2.1–2.4), §3 Architecture Overview, §4.1 What We Clone, §4.2 The Human Model File (`human-model.yaml`)
**Partial/incomplete sections:** §4.3 onward (still to be written)

### 3.1 Key design decisions made

1. **New agent class: "Boss" (outer loop)** — mimics the specific human researcher. Not a generic assistant.
2. **Behavioral cloning over reward modeling** — needs less data, more interpretable, degrades gracefully, captures *style* not just *objectives*.
3. **Skill–Intent–Priority triangle** — three orthogonal dimensions of human task-giving.
4. **`human-model.yaml` artifact** — structured representation of a researcher's style, priorities, dispatch patterns, tempo, escalation criteria. Generated from observation + calibration dialogue, not hand-authored from scratch.
5. **Verifiable environment requirement** — explicit table of domains (software, ML, quant, math) with feedback latency. Boss must escalate when domain lacks machine-gradeable signal.
6. **Three dispatch patterns explicitly named:** `REFINE_ON_PARTIAL_SUCCESS`, `KILL_AND_PIVOT`, `DEEPEN_ON_STRONG_RESULT`.

---

## 4. Remaining Work (for next session)

The following sections of RFC 003 still need to be written. Outline provided so work can continue:

### §4.3 The Prompt Stack for the Boss Agent
Layered system prompt built from:
- `CLAUDE.md` — base persona ("you are a research task dispatcher")
- `human-model.yaml` — rendered into prose at session start
- `research-state.md` — current hypothesis tree, past experiments, dead ends
- Recent worker reports (last N experiments as compact JSON)
- Escalation policy

### §4.4 The Decision Procedure
Pseudocode for the outer loop:
```
on worker_report(result):
    state.append(result)
    if escalation_condition(result, state, human_model):
        notify_human(build_summary(state))
        return
    next_task = dispatch_policy(state, human_model)
    if confidence(next_task) < threshold:
        notify_human(propose_options(state, top_k=3))
        return
    send_to_worker(next_task)
```

### §5 The Inner Loop Agent: Verifiable Execution
- Reuse `agents/quant-agent` pattern — seed repo + CLAUDE.md
- Standardized output contract (YAML envelope with metrics, artifacts, gradient)
- Experiment log append-only at `/workspace/experiments/log.jsonl`
- Git-commit-per-experiment (branch naming: `exp/{hypothesis_id}/{variant_id}`)

### §6 The Feedback Bridge
- New controller component: parses worker output, updates research state, decides whether to wake boss agent
- Options: (a) dedicated process, (b) Boss Agent's own polling via `schedule_task`, (c) IPC task type `worker_completed`
- Recommendation: (b) — reuse existing `schedule_task` primitive, Boss schedules itself to re-evaluate every N minutes or on worker completion event

### §7 Skill and Intent System
- Per-domain skill directory: `agents/research-boss/skills/quant/`, `agents/research-boss/skills/ml/`, etc.
- Intent routing: "is this a quant question or an ML question?" → load matching skill pack
- Intent → Skill composition: `backtest_refinement` skill composes `generate_parameter_sweep` + `compare_against_baseline` + `format_as_boss_task`
- Follow Hermes open standard (`SKILL.md` frontmatter) for portability

### §8 Continuum Learning
- **Calibration mode** — first few days, Boss proposes tasks and human approves/edits. Every edit becomes training signal.
- **Update loop** — after each session, Boss summarizes human interventions and updates `human-model.yaml` (tracked in git for auditability).
- **Skill extraction** — Hermes pattern: after N successful dispatches of the same shape, extract as named skill.
- **Drift detection** — if human interventions exceed threshold, trigger recalibration dialogue.

### §9 Quant Research: Concrete Walkthrough
Full traced example:
- Human: "Explore momentum reversal on crypto majors"
- Boss generates experiment v1 → Worker runs → reports Sharpe 1.2
- Boss applies `REFINE_ON_PARTIAL_SUCCESS` → 3 variants in parallel
- Variants return: 1.8, 0.6, 1.5
- Boss applies `DEEPEN_ON_STRONG_RESULT` on the 1.8 → 4 robustness checks
- Overnight run completes → morning summary delivered to human
- Human intervenes: "try longer holding period too"
- Boss updates `human-model.yaml` (new refinement pattern: `test_longer_holding`)

### §10 Mapping to Alpha-devbox Primitives
| Design concept | Alpha-devbox primitive |
|---|---|
| Boss Agent | New `agents/research-boss/` directory |
| Worker Agent | Existing `agents/quant-agent/` pattern |
| Task dispatch | `send_message` MCP tool + new inter-agent message type |
| Continuous running | `schedule_task` with interval |
| Research state | Persisted in `/workspace/research-state/` |
| Session isolation | Existing composite session key `(channel, thread, agent)` |
| Escalation | `send_message` with `sender="Boss"` for Telegram ping |
| Human interventions | Normal user messages into the boss session |

### §11 Safety and Verification Boundaries
- **Resource budget** — Boss must track cumulative compute cost, escalate at 80%
- **Kill switches** — `/done` and `/reset` from session-control.ts work unchanged
- **Containment** — Worker runs in isolated container (existing invariant)
- **No live execution** — Boss cannot dispatch "run this trade live" tasks without human confirmation (policy encoded in `human-model.yaml`)
- **Audit trail** — every task dispatch stored with justification; every human intervention diffed into model update

### §12 Comparison with Prior Art
- **Hermes Agent** — we borrow skill system, memory model, ReAct loop. We add: boss/worker separation, behavioral cloning of dispatcher.
- **AutoGPT / BabyAGI** — similar "AI-driving-AI" pattern. We differ: personalized to specific human, verifiable environment requirement, escalation-first design.
- **Devin / SWE-agent** — coding-only, single-agent. We differ: research domain, two-agent outer/inner structure.
- **Andrew Karpathy's LLM Wiki / auto-research** — aspirational reference; we implement one concrete instantiation with alpha-devbox as substrate.
- **Project Glasswing (Mythos Preview)** — the model-side enabler. Strong enough to run the loop.

### §13 Implementation Roadmap

**Phase 1: Skeleton (1-2 weeks)**
- Create `agents/research-boss/` with minimal `CLAUDE.md`
- Define `human-model.yaml` schema + parser
- Wire Boss ↔ Worker via existing IPC (Boss uses `send_message` with `sender="Boss"`)

**Phase 2: Calibration (2-3 weeks)**
- Ingest user's historical Telegram/web messages to quant-agent
- Generate first-pass `human-model.yaml`
- Calibration dialogue: "here's what I think you'd do — agree?"

**Phase 3: Autonomous loop (3-4 weeks)**
- `schedule_task`-based self-invocation
- Escalation criteria enforcement
- Morning summary report format

**Phase 4: Continuum learning (ongoing)**
- Per-session model update diff
- Skill extraction after N similar dispatches
- Drift detection and recalibration

---

## 5. Session Artifact Inventory

| File | Status | Path |
|---|---|---|
| RFC 003 draft | Partial (§1–§4.2 done) | `docs/rfcs/003-ai-research-agent-design.md` |
| Hand-off doc | This file | `docs/rfcs/003-handoff.md` |

**No code changes** have been made. This session is design-only.

---

## 6. Tool / Environment Issues Encountered

- Edit tool rejects identical-content no-ops (can't use it to append)
- Had to use Write (full file overwrite) to extend the RFC
- Several deferred tool announcements/retractions during the session (GitHub MCP, PushNotification) — did not affect design work
- Context got partially truncated mid-Write call; RFC 003 ended at §4.2 calibration example

---

## 7. Recommended Next Session Prompt

> "Continue RFC 003 at docs/rfcs/003-ai-research-agent-design.md. Sections §4.3 through §13 still need to be written. The outline is in docs/rfcs/003-handoff.md §4. Write each section with PhD-level depth matching the existing sections. After the RFC is complete, create a minimal `agents/research-boss/` skeleton (CLAUDE.md + seed.yaml + human-model.yaml schema) as the Phase 1 deliverable."

---

## 8. Core Design Thesis (one paragraph)

The repetitive cost of AI-driven research is the human's task-dispatch burden, not the AI's execution capability. By cloning a specific human researcher's dispatch patterns into a "Boss" agent — their priorities, vocabulary, tempo, refinement strategies, and escalation thresholds — we close the loop so the AI worker stays fed with well-specified tasks around the clock. The human's scarce attention is redirected from the inner loop (repetitive) to the outer loop (compounding): problem selection, framework revision, injecting offline truth, taste. Alpha-devbox already provides the substrate (containerized workers, persistent workspaces, scheduled tasks, IPC); Hermes Agent provides the skill/memory idiom (`SKILL.md`, `MEMORY.md`, dialectic user modeling). What's new is the Boss agent class itself: a behaviorally cloned task dispatcher that treats the verifiable environment as its action space and the human as its optimizer.
