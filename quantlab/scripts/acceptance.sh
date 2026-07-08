#!/usr/bin/env bash
# Acceptance inspection against quantlab/BLUEPRINT.md. Exit 0 = the built
# house matches the drawing.
set -u
cd "$(dirname "$0")/.."
FAIL=0

check() { # id, description, command...
  local id="$1" desc="$2"; shift 2
  if "$@" >/tmp/acc_out 2>&1; then
    echo "PASS  $id  $desc"
  else
    echo "FAIL  $id  $desc"
    tail -5 /tmp/acc_out | sed 's/^/      /'
    FAIL=1
  fi
}

# Rust: build (so the parity test can find the binary) + tests (R2 rust side)
check R2r "rust parsers: cargo test" bash -c "cd rust && cargo test --quiet"
export PATH="$PWD/rust/target/debug:$PATH"

# Python: R1-R7 (R2 parity auto-enabled now that ql-ingest is on PATH)
check R1  "lake provenance & freshness"            bash -c "cd python && python3 -m pytest -q -k r1"
check R2  "parsers + cross-language parity"        bash -c "cd python && python3 -m pytest -q -k r2"
check R3  "no-lookahead benchmarks"                bash -c "cd python && python3 -m pytest -q -k r3"
check R4  "forecaster interface & baselines"       bash -c "cd python && python3 -m pytest -q -k r4"
check R5  "pricing verification block"             bash -c "cd python && python3 -m pytest -q -k r5"
check R6  "trailing-only features"                 bash -c "cd python && python3 -m pytest -q -k r6"
check R7  "monitor freshness gate & event wiring"  bash -c "cd python && python3 -m pytest -q -k r7"

# Go orchestrator (R8) — checked when present (delegated to a sub-agent)
if [ -d orchestrator ]; then
  check R8 "go orchestrator vet+test" bash -c "cd orchestrator && /usr/local/go/bin/go vet ./... && /usr/local/go/bin/go test ./..."
else
  echo "SKIP  R8  orchestrator not yet delivered"
fi

# R9: no data files committed
check R9 "no parquet/lake data in repo" bash -c "! git ls-files | grep -E '\\.(parquet|zst)$'"

exit $FAIL
