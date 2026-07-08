# Plan: benchmarks-models          Layer: L1 | Parent: L0-campaign-memory-storage.md | 2026-07-08, status: PLANNED

## Objective (one sentence, from parent)

Freeze no-lookahead prediction benchmarks from the theater lake using
quantlab's `Benchmark`/`pit_join` machinery (rolling-origin, purged,
embargoed), establish dumb baselines, then hill-climb with GBM and
Chronos/TimesFM — models enter conclusions only as priors with calibration
receipts (skills: inv-quant-foundations, inv-foundation-models).

## Tree

- 1. Benchmark construction (quantlab/python/quantlab/benchmarks.py; every
     benchmark serializes params + hash; samples carry asof/resolve_at/target)
  - 1.1 BM-SI-DIR: predict next FINRA SI print direction (Δ sign) for MU,
    SNDK, WDC; features = daily SVR z-scores, implied borrow, P/C drift,
    bars — all pit_join'ed on published_at; asof = day before publication,
    resolve_at = dissemination date. Baselines: base rate, last-Δ persist.
    [owner: L2-bm-si | 1 ctx | /workspace/pipelines/analysis/bm_si_dir.py +
    /workspace/data/benchmarks/si_dir/]
  - 1.2 BM-REV-Q: predict quarterly revenue (log level + QoQ) for MU and
    SNDK-flash-lineage (WDC flash segment pre-spin for depth, tagged);
    features = spot curves, exports, TWSE read-across, guidance — joined on
    publication time; ~20–40 samples, so interval quality > point accuracy.
    Baselines: seasonal-naive, drift, guidance midpoint (must-beat).
    [owner: L2-bm-rev | 1.5 ctx | analysis/bm_rev_q.py +
    /workspace/data/benchmarks/rev_q/]
  - 1.3 BM-DRAM-20D: forecast DRAM spot (the exact scraped series) 20
    trading days ahead, distributional; rolling-origin weekly origins once
    ≥120 obs (backfilled from public archive where available, else clock
    starts at scrape inception — no backcasting). Baselines: naive, drift,
    AR(1). [owner: L2-bm-dram | 1 ctx | analysis/bm_dram_20d.py +
    /workspace/data/benchmarks/dram_20d/]
  - 1.4 Optional (only if 1.1–1.3 green): BM-SVR-3D short-horizon SVR drift
    and BM-SSD-PPG retail price-per-GB 20d, same rules.
    [owner: L2-bm-extra | 1 ctx | /workspace/data/benchmarks/]
- 2. Baseline scorecards
  - 2.1 Run all baselines on all benchmarks; metrics per
    inv-quant-foundations: directional hit + calibration for BM-SI-DIR,
    MAPE + interval coverage for BM-REV-Q, CRPS/pinball + coverage for
    BM-DRAM-20D; lab-notebook section records every variant tried (N).
    [owner: L2-baselines | 1 ctx | analysis/benchmark_scorecards.md]
- 3. Hill-climb
  - 3.1 GBM per benchmark: dozens of features max, strong regularization,
    monotonic constraints where sign is known (e.g. NAND spot ↑ → SNDK ASP
    node ↑); purged walk-forward only; beats-all-baselines-or-benched, in
    writing. [owner: L2-gbm | 1.5 ctx | analysis/gbm_{si,rev,dram}.py]
  - 3.2 Foundation models: verify current checkpoints on HF hub first
    (record exact ids in research/process/lessons.md) [needs-egress —
    model download]; Chronos-Bolt small + TimesFM base (CPU-sized) via the
    quantlab `Forecaster` interface; zero-shot only, log-returns for bar
    series; outputs = sampled paths → intervals. FM forecast for BM-REV-Q
    and BM-DRAM-20D becomes the unconditional prior handed to
    L1-revenue-projection leaf 5.1. Fallback if download blocked: ship
    baselines + GBM only and record FM-unavailable in the model registry.
    [owner: L2-fm | 1.5 ctx | quantlab wrappers + analysis/fm_scorecards.md]
  - 3.3 Bayesian criticism loop (Box's loop) per deployed model: prior/
    posterior predictive checks, empirical interval coverage tracking →
    `research/calibration/models/<name>.md`; failing models get expanded
    or benched, dated. [owner: L2-criticism | 1 ctx |
    research/calibration/models/]
- 4. Wiring
  - 4.1 Nightly/weekly forecast jobs write to lake with model id + version +
    input partition hashes; benchmark re-freeze scheduled quarterly.
    [owner: L2-wiring | 0.5 ctx | pipelines/forecast_jobs.py + scheduler]

## What this layer decided NOT to do

- No fine-tuning of FMs — per-series samples never justify it here;
  context-conditioning (DRAM spot as related series) is the only lever.
- No price/return direction benchmarks for the equities — the system
  predicts intermediate dimensions; equity Sharpe games invite
  multiple-testing self-deception (and would need deflated-Sharpe
  machinery out of scope).
- No orderbook/microstructure FMs — research-grade, no stable checkpoint;
  recorded as unavailable capability rather than pretended.
- No benchmark on series with < 8 usable origins — thin tasks produce
  noise scorecards; they wait for history to accrue.

## Definition of done + verification plan

Done: ≥3 benchmarks frozen with hashes; baseline + GBM + FM scorecards
written with tried-variant counts; model registry entries with coverage
tracking; rev-Q prior delivered to the projection layer; jobs scheduled.
Verification (L4): independent no-lookahead audit — verifier greps every
benchmark's feature builders and re-runs pit_join assertions (no fwd_
columns in features, purge/embargo params sane vs label horizon);
benchmark-hash reproducibility (rebuild from lake, hash must match);
one scorecard recomputed from scratch; coverage claims re-tallied against
raw forecasts.

## Status log (append-only)

- 2026-07-08: Planned; all leaves blocked on lake population
  (L1-data-pipeline + L1-strategy-map price curves); 1.2 can start once
  XBRL fundamentals land.
