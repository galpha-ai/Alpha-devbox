# quantlab Blueprint & Acceptance Spec

The building drawing this system is inspected against. Every requirement
is numbered and machine-checkable; `scripts/acceptance.sh` runs the whole
inspection. A deliverable that cannot be checked against this document is
not done. (Conceptual blueprint: `docs/whitepaper/agentic-investing-system.md`;
skill layer: `container/skills/agentic-investing` + `inv-*`.)

## System shape

Two systems, one lake:

- **Research system** — (a) storage infra: snapshot-first hive-partitioned
  parquet lake with mandatory provenance (`quantlab/python/quantlab/lake.py`);
  (b) data-construction logic: publication-time joins and purged/embargoed
  rolling-origin benchmarks (`benchmarks.py`) — the ground ML hill-climbing
  stands on; (c) models: baselines-first forecaster interface (`models/`),
  verified option pricing (`pricing/`).
- **Production system** — freshness-gated live monitors that write alerts
  into the decision layer's event log (`monitors.py`), fed by scheduled
  ingestors (cadences in the `inv-data-pipeline` skill).
- **Language policy** — Python-first (Polars); Rust for raw-feed parsing
  and future hot loops (`quantlab/rust`); Go for orchestration glue
  (`quantlab/orchestrator`). All non-Python code is written/maintained by
  sub-agents and must be verifiable without reading it: README contract +
  golden-fixture parity tests + `cargo test` / `go test` green.

## Requirements

| ID | Requirement | Check |
|---|---|---|
| R1 | Lake writes require provenance (source_url, effective_date, published_at); empty partitions refused; incomplete partitions (no `_meta.json`) invisible to readers; freshness queryable | `pytest -k r1` |
| R2 | Raw-feed parsers (FINRA Reg SHO, CBOE chains) exist in Rust and Python with identical outputs on golden fixtures; malformed input errors carry line context; bad contracts are errors, not silent drops | `cargo test` + `pytest -k r2` (parity test runs when `ql-ingest` is on PATH) |
| R3 | Benchmarks reject targets known at prediction time; splits are rolling-origin with purge+embargo enforced on label *resolution* time; point-in-time joins require publication timestamps and never join future rows; every metric carries the benchmark fingerprint | `pytest -k r3` |
| R4 | All forecasters (baselines + FM wrappers) share one interface; FM wrappers fail loudly with install/verify hints when deps absent; comparison tables refuse to mix benchmarks | `pytest -k r4` |
| R5 | Option pricing ships with its verification block: European limit → Black-Scholes within 5e-3, American put early-exercise premium positive, discrete dividends lower calls, put-call parity residual < 1e-2 | `pytest -k r5` |
| R6 | Feature builders are trailing-only: values at row t identical with/without future rows present | `pytest -k r6` |
| R7 | Monitors gate on freshness (STALE DATA rather than computing on old partitions) and append alerts to the decision layer's `research/events/log.md` format | `pytest -k r7` |
| R8 | Go orchestrator: plan-driven dispatch→verify→retry→escalate loops, dependency ordering, atomic status.json, stdlib-only; verifiable without reading Go | `cd quantlab/orchestrator && go vet ./... && go test ./...` |
| R9 | Repo hygiene: no data files in the repo (lake lives under /workspace/data, mirrored to GCS); skills and blueprint stay consistent when either changes | `scripts/acceptance.sh` grep guard |

## Inspection

```bash
quantlab/scripts/acceptance.sh   # runs R1-R9, prints PASS/FAIL per requirement
```

Extending the system = adding a numbered requirement here + its check in
the test suites *first* (TDD), then building until the inspection passes.
