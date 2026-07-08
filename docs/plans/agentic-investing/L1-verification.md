# Plan: verification          Layer: L1 | Parent: L0-campaign-memory-storage.md | 2026-07-08, status: PLANNED

## Objective (one sentence, from parent)

Run the L4 adversarial layer over every campaign deliverable: point-in-time
audits of all datasets, cross-language parser fixture checks, calibration-
coverage checks, and independent refutation passes on anything that reaches
a belief file — nothing enters a conclusion unverified (skills:
inv-quant-foundations for standards; verifiers are spawned with different
lenses, never copies).

## Tree

- 1. Point-in-time dataset audits (one L4 pass per dataset, after ingest)
  - 1.1 Audit matrix over the lake: for each of cboe/chain_*, finra/
    regsho_daily, finra/short_interest, sec/form4, sec/8k, sec/13f,
    sec/nport, bars/daily, prices/*, capacity/ledger, estimates/*: verify
    `_meta.json` completeness; effective_date < published_at ≤ fetched_at;
    lag matches the dataset's statutory rule (13F ≤45d, SI ~T+7 bus. days,
    Form 4 ≤2 bus. days, chain OI = T+1 `oi_asof`); raw/ payload present;
    append-only respected (no partition mtime after later partitions).
    Verdict per dataset → audit log. [owner: L4-pit-audit | 1 ctx per ~4
    datasets | analysis/verification/pit_audit_memory.md]
  - 1.2 Row-count reconciliation vs source for one random dt per dataset
    (Reg SHO file line count, chain contract count vs raw JSON, 13F
    infotable rows) [needs-egress for re-fetch; fallback: reconcile against
    stored raw/ only, noted]. [owner: L4-rowcount | 1 ctx |
    analysis/verification/rowcount_audit.md]
- 2. Cross-language parser fixture checks
  - 2.1 Golden fixtures: one real Reg SHO file + one CBOE chain JSON (small
    ticker day) checked into quantlab test fixtures; assert rust ql-ingest
    output == independent Python (Polars) parse, field by field, including
    edge rows (halted names, sub-$0.10 quotes, weird strikes). Divergence =
    blocker bug filed to L1-data-pipeline. [owner: L4-parser-fixtures |
    1 ctx | quantlab/rust/crates/ql-ingest tests +
    quantlab/python tests]
  - 2.2 Form 4 XML parse spot-check: 5 filings re-read by hand vs parsed
    rows (codes, 10b5-1 flag, footnote presence). [owner: L4-form4-check |
    0.5 ctx | analysis/verification/form4_audit.md]
- 3. No-lookahead + statistical validity (over L1-benchmarks-models)
  - 3.1 Independent lookahead hunt: re-derive each benchmark's feature
    availability timeline; attempt to construct a leak (join on
    effective_date, drop embargo) and show the metric moves — proving the
    guard mattered; verify purge width ≥ label horizon.
    [owner: L4-lookahead | 1 ctx | analysis/verification/lookahead_audit.md]
  - 3.2 Multiple-testing audit: tried-variants ledger (N) present in every
    scorecard; winner's margin sanity vs N. [owner: L4-mult-test | 0.5 ctx |
    analysis/verification/mult_test_audit.md]
- 4. Calibration-coverage checks (standing, quarterly + post-print)
  - 4.1 Interval-coverage tally: every stated 80% interval across
    calibration files and model registry vs empirical coverage; "80% that
    covers 60% is a lie" — flag and force model-registry expansion entries.
    [owner: L4-coverage | 0.5 ctx | research/calibration/models/ + audit log]
  - 4.2 Post-print postmortem audit for MU and SNDK: calibration entry was
    armed BEFORE the print (timestamp proof), actuals filled, node-level
    error attribution written. [owner: L4-postmortem-audit | 0.5 ctx |
    research/postmortems/]
- 5. Refutation passes on belief-file claims (adversarial, different lenses)
  - 5.1 Standing rule: any new claim in research/beliefs/{MU,SNDK,WDC}.md or
    research/maps/memory-storage.yaml that cites data gets three
    independent lenses — (a) point-in-time/lag lens, (b) statistical lens
    (effect survives controls/placebo per inv-quant-foundations event-study
    rules), (c) domain-mechanism lens (does the causal chain hold on the
    strategy map?). Verifier writes REFUTED / WEAKENED / STANDS + reasons;
    belief edit reverted unless STANDS or WEAKENED-with-caveat.
    [owner: L4-refute (3 agents per claim) | 0.5 ctx each |
    analysis/verification/refutations/<claim-id>.md]
  - 5.2 Projection red-team: before each calibration entry freezes, one
    verifier builds the best opposite-direction case from the same lake
    partitions (bear case for a bullish variant, etc.); disagreement node
    must survive. [owner: L4-redteam | 1 ctx |
    analysis/verification/redteam_{MU,SNDK}.md]
- 6. Freshness/monitor tamper tests
  - 6.1 Simulate staleness (hide latest partition) and confirm every
    monitor emits STALE DATA rather than computing; confirm firings land in
    research/events/log.md. [owner: L4-freshness | 0.5 ctx |
    analysis/verification/freshness_test.md]

## What this layer decided NOT to do

- No re-verification of upstream vendors' own data quality (e.g. FINRA's
  reporting accuracy) — out of our control; provenance recording suffices.
- No formal proofs / property-based testing beyond golden fixtures this
  campaign — fixture parity catches the parser class of bug at far lower
  cost.
- No verification of narrative-only statements that cite no data — they are
  not allowed in belief files at all (integrity rule); flagging them is
  leaf 5.1's job, not verifying them.
- Not blocking daily monitor operation on audit completion — audits gate
  BELIEFS and CALIBRATION entries, not data collection.

## Definition of done + verification plan

Done: every dataset in the L0 scope has a dated PASS/FAIL pit-audit entry;
parser fixtures merged and green in both languages; lookahead + coverage
audits written; every belief-file claim carries a refutation verdict; both
projection red-teams done before calibration freeze; tamper test passed.
This layer's own check: L0 spot-samples two L4 verdicts and re-derives them
(verifier-of-the-verifier, shallow but real); all verdicts must cite exact
lake partitions/commands so any verdict is independently recomputable.

## Status log (append-only)

- 2026-07-08: Planned; 2.1 dispatchable as soon as ql-ingest parsers exist;
  1.x rolls dataset-by-dataset behind L1-data-pipeline; 5.x standing.
