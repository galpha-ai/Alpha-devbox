# Multi-Agent Orchestration Doctrine

How this system scales beyond one context window: layered planning agents,
each layer producing a plan document that the next layer executes. The
constraint that shapes everything: **context is the scarce resource;
documents are the interface between layers.**

## The layer stack (3–5 layers per campaign)

```
L0  Decision layer (the main session, agentic-investing loop)
     └─ plans a CAMPAIGN: one theater or one thesis. Output: campaign doc.
L1  Domain planners (one per inv-* domain touched by the campaign)
     └─ each enters plan mode, expands its slice into a tree/mind-map
        planning doc with concrete sub-problems. Output: L1 plan doc.
L2  Task planners/executors (one per sub-problem)
     └─ small enough to hold in one context: download THIS dataset, clean
        it, build THIS monitor, run THIS event study. Plans briefly, then
        executes. Output: data partitions + analysis writeup + doc updates.
L3  Workers (optional, spawned by L2 for fan-out)
     └─ per-ticker / per-quarter / per-filing parallel grunt work.
L4  Verifiers (adversarial, always)
     └─ every L2/L3 deliverable that feeds a conclusion gets an
        independent checker: point-in-time audit, row counts vs source,
        recompute headline numbers, try to refute the finding.
```

## Plan documents (the inter-layer contract)

Every planning layer writes its plan as a tree/mind-map markdown doc
before any child is spawned, at `research/plans/<campaign>/<layer>-<name>.md`
(campaigns that are themselves repo deliverables may keep their plan tree in
the repo under `docs/plans/<campaign>/` instead — same format either way):

```markdown
# Plan: <name>          Layer: L1 | Parent: <parent doc> | Date, status
## Objective (one sentence, from parent)
## Tree
- 1. <sub-problem>  [owner: L2-agent | est. effort | deliverable path]
  - 1.1 <concrete step: download X / clean Y / analyze Z / predict W>
  - 1.2 ...
- 2. ...
## What this layer decided NOT to do (subtraction, with reasons)
## Definition of done + verification plan (which L4 checks apply)
## Status log (append-only: dispatched, done, failed, re-planned)
```

Rules:
- A child agent receives: its subtree, the objective chain (L0→its layer),
  the relevant skill names, and lake/doc paths. It does NOT receive the
  whole campaign context — if the subtree isn't self-sufficient, fix the
  plan doc, don't widen the prompt.
- Every sub-problem follows the same inner shape: **download data → clean
  (domain rules from the inv-* skill) → analyze → extract insight →
  predict the verifiable dimension → register calibration entry**.
- Children return structured summaries; parents update the plan doc's
  status log. The doc, not the chat, is the memory.
- Re-planning is a first-class move: an L2 that discovers its sub-problem
  is mis-framed reports back up rather than grinding.

## Fan-out discipline

- Parallelize where sub-problems are independent (per-ticker, per-quarter,
  per-dataset). A theater campaign legitimately fans to dozens of agents
  across a day: ~5 L1 planners → 15-30 L2 tasks → per-ticker L3 workers →
  L4 verifiers on everything that survived.
- Independent perspectives beat redundant ones: where judgment is
  involved (does this event study hold?), spawn verifiers with *different*
  lenses (point-in-time audit / statistical validity / domain mechanism),
  not three copies of one prompt.
- Every fan-out ends in a **synthesis step at the parent** that reads only
  the children's docs/summaries and updates: beliefs, the strategy map,
  the question backlog, and `process/lessons.md`. Fan-out without
  synthesis is noise generation.
- Cost scales with agents: match fleet size to what the campaign's
  value-of-information justifies, and log the spend judgment in the
  campaign doc.

## Code-driven loops, not prompt chains

Orchestration itself is code with verification gates, so runs are
test-driven and inspectable: the Go orchestrator (`quantlab/orchestrator`)
executes plan files as dispatch → verify → retry → escalate loops
(bounded attempts, per-task acceptance commands, atomic status.json, the
escalate state = the advisor pattern). Where the harness provides a
deterministic workflow engine, that is the same doctrine. A fan-out whose
acceptance criterion is "the parent liked the output" is a prompt chain;
every dispatched task carries a `verify_cmd` that can fail.

## Language policy (the SubAID rule)

Python first (Polars for anything dataframe-shaped); Rust where Python
packages can't do the job (raw-feed parsing, hot numerical loops); Go as
orchestration glue; C/C++ only when unavoidable. **All non-Python code is
written and maintained by sub-agents**, because the human principal reads
only Python — therefore every non-Python component must be verifiable
without reading it: a README contract written for a Python reader, golden-
fixture parity tests against a Python reference where one exists, and its
own green test suite wired into `quantlab/scripts/acceptance.sh`.

## Standing campaigns (event-triggered operation)

Recurring orchestration (daily data pulls + monitor sweeps, weekly
screens, quarterly fog-of-war audits) runs off the scheduler per
`inv-data-pipeline` cadences: each firing is a mini-campaign — L1 plan
refresh (usually a no-op diff), L2 pulls/monitors, L4 freshness checks,
then synthesis into `events/log.md`. The decision layer wakes only for
triaged material events, not for every pull.
