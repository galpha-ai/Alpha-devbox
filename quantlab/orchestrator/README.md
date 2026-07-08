# quantlab/orchestrator

A small, deterministic, plan-driven agent-loop orchestrator written in Go
(stdlib only, no external dependencies). It is the "general" from
`container/skills/agentic-investing/references/orchestration.md`: instead of
prompting one big agent and hoping, you write a **plan file** listing tasks
with hard acceptance gates, and this program drives the
**dispatch → verify → retry → escalate** loop for every task, in dependency
order, with bounded parallelism.

You never need to read the Go to trust it — see
[Verify this component without reading Go](#verify-this-component-without-reading-go).

## What it does

1. Reads `plan.json` (schema below) — a DAG of tasks.
2. Topologically sorts tasks by `depends_on` (deterministic: ties broken
   alphabetically by task id). Cycles, duplicate ids, and unknown
   dependencies are rejected before anything runs.
3. Runs ready tasks concurrently with a bounded worker pool (`-parallel`,
   default 4).
4. For each task, loops:
   - run `exec_cmd` (the work — e.g. `claude -p "..."`, a Python script,
     anything executable via `/bin/sh -c`),
   - run `verify_cmd` (the acceptance gate — exit code 0 means passed),
   - on failure, retry up to `max_attempts` (default 2). Each retry gets the
     previous failure's output in the environment variable
     **`QL_PREV_FAILURE`** so an agentic `exec_cmd` can self-correct
     (e.g. `claude -p "fix the task; previous failure: $QL_PREV_FAILURE"`).
   - after exhausting attempts, the task is marked **`escalate`** and the
     run continues with every task that does not depend on it.
5. Persists `status.json` next to the plan file after **every** state
   change, atomically (written to a temp file in the same directory, then
   renamed — a reader can never observe a half-written file).
6. Prints a one-line summary and exits 0 only if every task reached `done`.

## Usage

```
orchestrator -plan plan.json [-parallel 4] [-task-timeout 30m] [-dry-run]
```

| Flag            | Default | Meaning                                                            |
|-----------------|---------|--------------------------------------------------------------------|
| `-plan`         | (required) | Path to the plan file.                                          |
| `-parallel`     | 4       | Max tasks running at once.                                         |
| `-task-timeout` | 30m     | Wall-clock budget per task, covering **all** of its attempts. On timeout the task's whole process group is killed and it escalates. |
| `-dry-run`      | off     | Print the topological execution order and exit; nothing runs.     |

Build: `/usr/local/go/bin/go build -o orchestrator .` (run inside this
directory). Exit codes: `0` all done, `1` something escalated or was
blocked, `2` bad flags or invalid plan.

## plan.json schema

JSON (chosen over YAML so the tool needs zero dependencies). Top level is
an object with one key, `tasks`, a list of task objects:

| Field          | Type          | Required | Meaning                                                       |
|----------------|---------------|----------|---------------------------------------------------------------|
| `id`           | string        | yes (unique) | Task name; referenced by `depends_on`.                    |
| `layer`        | string        | no       | `L1`..`L4` doctrine layer (metadata; copied into status).     |
| `objective`    | string        | no       | Human-readable one-liner (metadata).                          |
| `exec_cmd`     | string        | yes      | Shell command that does the work (`/bin/sh -c`).              |
| `verify_cmd`   | string        | yes      | Shell command; **exit 0 = accepted**. This is the hard gate.  |
| `max_attempts` | int           | no (default 2) | Total exec attempts before escalating.                  |
| `depends_on`   | list of ids   | no       | Tasks that must reach `done` first.                           |

Full example (this exact file ships as `testdata/sample-plan.json`, a
diamond: one L1 planner fans out to two L2 downloads, which join into an
L3 analysis, which is checked by an L4 verifier):

```json
{
  "tasks": [
    {"id": "l1-plan-earnings",   "layer": "L1", "objective": "Expand the earnings-season slice of the campaign into concrete sub-problems",
     "exec_cmd": "echo 'writing L1 plan doc'",  "verify_cmd": "true", "depends_on": []},
    {"id": "l2-download-prices", "layer": "L2", "objective": "Download daily prices for the watchlist",
     "exec_cmd": "echo 'downloading prices'",   "verify_cmd": "true", "depends_on": ["l1-plan-earnings"]},
    {"id": "l2-download-filings","layer": "L2", "objective": "Download the latest 10-Q filings",
     "exec_cmd": "echo 'downloading filings'",  "verify_cmd": "true", "depends_on": ["l1-plan-earnings"]},
    {"id": "l3-event-study",     "layer": "L3", "objective": "Run the per-ticker earnings event study",
     "exec_cmd": "echo 'running event study'",  "verify_cmd": "true", "max_attempts": 3,
     "depends_on": ["l2-download-prices", "l2-download-filings"]},
    {"id": "l4-verify-event-study","layer": "L4","objective": "Adversarially verify the event study",
     "exec_cmd": "echo 'verifying'",            "verify_cmd": "true", "depends_on": ["l3-event-study"]}
  ]
}
```

In real use `exec_cmd` invokes a sub-agent
(`claude -p "$(cat prompts/l2-download.md)"`) and `verify_cmd` is an
independent check (`python checks/row_counts.py`, `test -s data/prices.parquet`).

## Retry / escalate / advisor semantics

- **Retry with feedback.** A failed attempt (exec non-zero OR verify
  non-zero) does not immediately fail the task. The next attempt's
  `exec_cmd` runs with `QL_PREV_FAILURE` set to the failure output
  (`verify failed (attempt N, exit status X):\n<output>`), so a
  self-correcting agent can read what went wrong. `verify_cmd` always runs
  with `QL_PREV_FAILURE` empty — the gate never gets to grade on a curve.
- **Escalate, don't crash.** After `max_attempts`, the task's state becomes
  `escalate`. This is the *advisor pattern*: the orchestrator (the general)
  does not improvise past a hard gate — a human or a higher-layer agent
  reads `status.json`, decides (re-plan, relax the gate, drop the branch),
  and re-runs. The run itself continues with all unaffected tasks.
- **Blocked descendants.** Tasks downstream of an escalated/failed task are
  marked `failed` with `last_verify_output` = `blocked: dependency "X"
  ended in state escalate`. So in the final status: `escalate` = "this task
  itself exhausted its gate, decision needed here", `failed` = "never ran,
  upstream blocked it".

## status.json and the L1–L4 layer doctrine

`status.json` is written next to the plan file. Shape:

```json
{
  "plan": "plan.json",
  "updated_at": "2026-07-08T21:48:55Z",
  "tasks": [
    {"id": "l1-plan-earnings", "layer": "L1", "state": "done", "attempts": 1,
     "last_verify_output": "", "started_at": "...", "finished_at": "..."}
  ]
}
```

Per task: `state` is one of `pending | running | done | failed | escalate`;
`attempts` counts exec attempts so far; `last_verify_output` holds the most
recent failure (or final verify) output, truncated to 2000 characters;
timestamps are UTC RFC3339. Tasks are sorted by id.

Mapping to the orchestration doctrine (`orchestration.md`): each plan is
one L1 planner's expansion of a campaign slice. `layer: L2` rows are task
executors, `L3` rows are fan-out workers, and `L4` rows are the adversarial
verifiers — note that *every* task additionally carries its own micro-L4 in
`verify_cmd`. `status.json` is the machine-readable status log of the plan
doc: the parent layer (L0/L1, human or agent) polls it, treats `escalate`
rows as the triaged material events that wake the decision layer, and
appends the outcome to the campaign doc's status log. Because writes are
atomic, a watcher (e.g. a Python `json.load` in a loop) can poll it safely
mid-run.

## Verify this component without reading Go

Run the test suite (also run `vet`, Go's static analyzer):

```
cd quantlab/orchestrator
/usr/local/go/bin/go vet ./... && /usr/local/go/bin/go test -v ./...
```

All tests must pass. What each test proves (tests build tiny shell scripts
in a temp dir and run real plans through the real code path):

- `TestTopoOrderDiamond` — a diamond DAG (a → b,c → d) orders as
  `a, b, c, d`; cycles and unknown dependencies are rejected.
- `TestRetryThenPassWithPrevFailureEnv` — a verify script that fails
  exactly once (via a state file) yields `state=done, attempts=2`, and the
  second exec attempt really received the first failure's output in
  `QL_PREV_FAILURE`.
- `TestEscalationAndDependencyBlocking` — an always-failing gate ends in
  `escalate` after exactly `max_attempts`; its dependent is `failed`
  ("blocked"); an independent task still runs to `done`.
- `TestStatusFileShapeAndAtomicity` — the task's own `exec_cmd` greps
  `status.json` mid-run and finds itself `"running"` in valid JSON (state
  is persisted before/during execution, never half-written), all schema
  fields are present, output is ≤ 2000 chars, and no temp files leak.
- `TestTaskTimeoutEscalates` — a `sleep 5` task under a 200 ms
  `-task-timeout` escalates in well under 5 s.
- `TestDryRunPrintsTopologicalOrder` — `-dry-run` prints the numbered
  topological order with layers and dependencies.
- `TestSamplePlanRuns` — `testdata/sample-plan.json` runs end-to-end to
  5/5 `done`.

Then try it by hand with the sample plan (uses only `echo`/`true`):

```
/usr/local/go/bin/go build -o /tmp/orchestrator .
cp testdata/sample-plan.json /tmp/plan.json
/tmp/orchestrator -plan /tmp/plan.json -dry-run
/tmp/orchestrator -plan /tmp/plan.json && cat /tmp/status.json
```

Expected: the dry run prints the 5-task order (L1 first, L4 last); the real
run prints `plan finished: 5/5 done, 0 escalate, 0 failed`, exits 0, and
`/tmp/status.json` shows five `done` rows. To see the failure path, change
one `verify_cmd` to `"false"` and re-run: that task shows `escalate` with
`attempts: 2`, everything downstream shows `failed` ("blocked: …"),
independent branches still complete, and the exit code is 1.
