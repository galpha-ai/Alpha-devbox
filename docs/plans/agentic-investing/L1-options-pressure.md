# Plan: options-pressure          Layer: L1 | Parent: L0-campaign-memory-storage.md | 2026-07-08, status: PLANNED

## Objective (one sentence, from parent)

Turn daily CBOE chain snapshots for MU, SNDK, WDC into pressure ratios, OI
walls, Breeden–Litzenberger implied distributions, implied earnings moves,
GEX maps, and squeeze screens that measure what is priced in before the
prints (skill: inv-options-pressure; math checks per inv-option-pricing-sde).

## Tree

- 1. OI history foundation (depends on L1-data-pipeline leaf 2.1)
  - 1.1 Backfill impossibility check + start-date stamp: free OI history
    does not exist — history begins at first snapshot; record inception in
    `_meta.json` and in the fog audit. Contract-level hygiene filters
    (spread%, delta, sub-$0.10) as a shared Polars module.
    [owner: L2-chain-hygiene | 0.5 ctx |
    /workspace/pipelines/analysis/chain_filters.py]
- 2. Layer-1 pressure ratios (daily, per ticker)
  - 2.1 P/C OI + P/C volume ratios vs own trailing percentile (1y once
    history accrues; until then, growing window flagged as short-history);
    OI-by-strike/expiry wall map; IV term structure + 25Δ skew series →
    `derived/options_pressure_{T}/dt=<date>/`.
    [owner: L2-pressure-daily | 1 ctx |
    /workspace/data/derived/options_pressure_{MU,SNDK,WDC}/]
- 3. Implied distribution (the crown jewel)
  - 3.1 B-L pipeline `/workspace/pipelines/analysis/implied_dist.py`: OTM
    mids only → forward from put-call parity at min|C−P| (also emits
    implied borrow/dividend → feeds SI layer) → SVI-or-constrained-spline IV
    fit → reprice → numeric d²C/dK² on the fitted curve → density sanity
    (≥0, ∫≈1, mean≈F). Output per expiry: q(K), P(S>x) table.
    [owner: L2-implied-dist | 1.5 ctx | analysis/implied_dist.py +
    /workspace/data/derived/implied_dist_{T}/]
  - 3.2 Implied earnings move for MU and SNDK next prints: front straddle /
    spot, event variance stripped via later expiry (T₁σ₁² − baseline);
    compare vs 8-quarter realized post-print moves from bars lake → memo
    feeding whisper triangulation in L1-revenue-projection.
    [owner: L2-event-premium | 1 ctx | analysis/event_premium_memory.md]
- 4. GEX and squeeze mechanics
  - 4.1 GEX per strike + zero-gamma level, computed under the stated
    standard convention and re-signed where ΔOI-vs-volume evidence
    identifies customer direction; every output labeled "under assumption X"
    → `derived/gex_{T}/dt=<date>/`. [owner: L2-gex | 1 ctx |
    /workspace/data/derived/gex_{MU,SNDK,WDC}/]
  - 4.2 Squeeze screen for the trio: near-OTM call gamma notional / float
    ADV $, OI growth via ask-side inference, implied borrow trend + SI/DTC
    from finra lake; cross-check fuel/trigger/trap per inv-short-interest →
    ranked table + verdict memo. [owner: L2-squeeze | 1 ctx |
    analysis/squeeze_screen_memory.md]
- 5. Flow inference notes
  - 5.1 ΔOI-vs-volume + IV-direction triangulation write-up per name per week,
    labeled as inference with the triangulation shown; no trade-side claims
    from free data. [owner: L2-flow-notes | 0.5 ctx |
    analysis/flow_inference_memory.md]
- 6. Monitors
  - 6.1 Register daily post-snapshot monitors: P/C percentile alert,
    OI-wall migration, GEX sign flip, implied-borrow spike (→ SI layer),
    event-premium tracker into the MU/SNDK prints. Specs in
    `research/monitors/options-memory.md`; firings → events/log.md.
    [owner: L2-monitors | 0.5 ctx | research/monitors/options-memory.md]

## What this layer decided NOT to do

- No paid trade-level (side-tagged) options flow — inference only, labeled.
- No market-wide gamma squeeze funnel this campaign — trio only; the weekly
  market-wide screen is deferred until the theater stack is proven.
- No exotic model calibration (Heston/jump-diffusion) — B-L density +
  parity checks suffice for "what's priced in"; SDE work only if an
  L0 decision needs option fair value (then inv-option-pricing-sde).
- No options analytics for 000660.KS/005930.KS/285A.T (no free chain
  source of comparable quality) — recorded as fog, not proxied.

## Definition of done + verification plan

Done: daily derived partitions for all three tickers flowing for ≥3
consecutive sessions; implied distributions + implied earnings moves for
both target prints memo'd; GEX maps labeled; squeeze verdicts written;
monitors live. Verification (L4): parity/convergence checks on every
pricing-adjacent number (inv-option-pricing-sde checks block); density
sanity re-run independently; T+1 OI discipline audit (no same-day OI
reaction anywhere); ΔOI dedupe across weekly expiries via tenor buckets
spot-checked; refutation pass on any "market implies X%" claim that reaches
a belief file (recompute from raw snapshot).

## Status log (append-only)

- 2026-07-08: Planned; blocked on L1-data-pipeline leaf 2.1 (chain
  snapshots) for all leaves except 1.1 scaffolding.
