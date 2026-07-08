# Templates for research/ files

Copy the relevant template when creating a new entry. Keep entries terse —
these files are working memory, not essays. All dates ISO (`YYYY-MM-DD`).

## research/beliefs/<entity>.md

```markdown
# <Entity> — belief file

Updated: 2026-07-08 | Ref price/level at update: <px>

## Variant view vs consensus
Consensus: <one sentence>
My view: <one sentence>
Confidence: low / medium / high

## Key drivers (1–3, ranked)
1. <driver> — current read: <...>
2. <driver> — current read: <...>

## Falsifiers (what would prove me wrong)
- <observable event/datapoint> → would flip view to <...>

## What I am deliberately ignoring (noise list)
- <topic> — why it doesn't move the payoff distribution

## Belief changelog
- 2026-07-08: <what changed and why> (was: <old view>)
```

## research/events/log.md (append-only)

```markdown
## 2026-07-08 <event one-liner>
Entities: <A, B>
What changed (no adjectives): <...>
Materiality: noise | watch | material — <one-line reason>
Second-order: <who else is affected, or "none seen">
Action: dropped | added question Q<n> | triggered decision D<n>
```

## research/questions/backlog.md

```markdown
# Question backlog (ranked)

## Open
- Q7 [impact:H prob-resolvable:M] <question> (entity, added 2026-07-08)

## Resolved
- Q3 → answered 2026-07-08: <finding, one line> → belief updated: yes/no

## Cut (with reason — this section is the taste record)
- Q5 — looks important, is noise because <...>
```

## research/decisions/journal.md (append-only)

```markdown
## D12 | 2026-07-08 | <entity> | ACT / WAIT / NO-ACTION
Ref price/level: <px>
Thesis (one sentence): <...>
Key driver bet: <which driver, which direction>
Scenarios: bear <p%, payoff> / base <p%, payoff> / bull <p%, payoff>
Asymmetry rationale: <why the distribution justifies this>
Size & instrument (if ACT): <...>
Invalidation / exit: <observable condition, decided now>
Waiting on (if WAIT): <datapoint X, expected by <date>>
Review date: 2026-08-08
```

## research/postmortems/<id>.md

```markdown
# Postmortem D12 — <entity>

Decision date: 2026-07-08 → resolved: 2026-09-15
Outcome: <what happened, with numbers>

Decision quality (independent of outcome): good / mixed / poor — <why>
Outcome quality: good / poor

Was the key driver actually the driver? <...>
Question we failed to ask: <...>
Research that was wasted effort: <...>

Lessons → beliefs/<entity>.md: <entity-specific>
Lessons → process/lessons.md: <process-level, or "none">
```

## research/process/lessons.md

```markdown
# Process lessons (standing corrections — skim at session start)

- 2026-07-08 (from D12): <recurring bias or workflow fix, one line>
```

## research/monitors/<name>.md

```markdown
# Monitor: <name>

Created: 2026-07-08 | For: <decision D<n> / thesis in beliefs/<entity>.md>
Watches: <dataset + condition, e.g. "MU short interest % float crosses 8%,
         or call OI at $130 strike doubles">
Cadence: <daily post-close / biweekly on SI publication / quarterly>
Data source: <inv-* skill + lake path>
Alert action: append to events/log.md + <notify user / re-run projection>
Retire when: <condition — every monitor has an expiry or it becomes noise>

## Firing log (append-only)
- 2026-07-15: fired — <what was observed> → <action taken / noise>
```

## Driver tree (inside beliefs/<entity>.md, for fundamental names)

```markdown
## Revenue driver tree (as of 2026-07-08, sources in lake)
Total revenue
├── Segment A (62% of rev, filed 10-Q) = units × ASP
│   ├── units ← <leading indicator + lake path>  [filed/derived/assumed]
│   └── ASP   ← <contract price series / mgmt comment>  [tag]
└── Segment B (38%) = ...
Forecast next Q: <point + range>, consensus <x> (as-of <date>), variant <±y%>
Verifies on: <earnings date> — logged in calibration file
```
