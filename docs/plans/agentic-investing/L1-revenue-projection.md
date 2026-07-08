# Plan: revenue-projection          Layer: L1 | Parent: L0-campaign-memory-storage.md | 2026-07-08, status: PLANNED

## Objective (one sentence, from parent)

Build MU and SNDK revenue driver trees from filed segment data, measure the
three expectation layers (guidance bias, per-bank sell-side, triangulated
whisper), produce point + 80%-interval projections for the next prints, and
arm the calibration files before those prints (skill: inv-revenue-projection).

## Tree

- 1. Print calendar + filing pull
  - 1.1 Confirm next print dates/times (am/pm) for MU (FQ1-27, ~late Sep
    2026) and SNDK (~Aug 2026) via earnings calendar (FMP `calendar` MCP or
    IR pages); write the read-across schedule (peers printing first:
    Samsung prelim ~early Oct, SK Hynix ~late Oct, Kioxia, WDC, hyperscaler
    capex dates). [owner: L2-calendar | 0.5 ctx |
    research/monitors/earnings-calendar-memory.md] [needs-egress]
  - 1.2 Pull latest 10-K/10-Q + XBRL companyfacts for MU (CIK 0000723125)
    and SNDK (CIK [lookup]); snapshot segment tables →
    `sec/fundamentals/{MU,SNDK}/dt=<date>/`. [owner: L2-filings | 1 ctx |
    /workspace/data/sec/fundamentals/] [needs-egress]
- 2. Driver trees (per company; L3 fan-out MU / SNDK)
  - 2.1 MU tree: revenue → segments (CNBU/MBU/SBU/EBU or current structure —
    diff segment names vs prior 10-K first) → bit shipments × ASP per
    DRAM/NAND/HBM; nodes tagged [filed]/[derived]/[assumed]; leading
    indicators per node wired to strategy-map series (DRAM spot w/ contract
    lag estimated from history, exports, hyperscaler capex, HBM ledger).
    → `research/beliefs/MU.md` §driver-tree with lake paths.
    [owner: L3-tree-MU | 1.5 ctx | research/beliefs/MU.md]
  - 2.2 SNDK tree: revenue → end-market split (client/consumer/DC eSSD) →
    bits × ASP; NAND-spot lag node; JV cost structure note (Kioxia JV);
    post-spin history is short — backfill using WDC flash-segment history
    pre-spin, tagged [derived]. → `research/beliefs/SNDK.md`.
    [owner: L3-tree-SNDK | 1.5 ctx | research/beliefs/SNDK.md]
- 3. Expectation layer 1+2: guidance bias + sell-side
  - 3.1 Guidance-bias history: guide-vs-actual per quarter, 12 quarters
    (MU; SNDK since spin + WDC-flash proxy) from 8-Ks/transcripts →
    sandbagging parameter per company → `analysis/guidance_bias_memory.md`.
    [owner: L2-guidance-bias | 1 ctx | analysis/guidance_bias_memory.md]
    [needs-egress]
  - 3.2 Sell-side snapshot: per-bank estimates + revision dates (FMP
    `analyst` MCP; fallback: public consensus aggregators, recorded
    provenance) — SNAPSHOT to lake (vendors restate); compute revision
    breadth/velocity; read the highest + lowest estimate's reasoning where
    accessible. → `estimates/{MU,SNDK}/dt=<date>/`.
    [owner: L2-sellside | 1 ctx | /workspace/data/estimates/] [needs-egress]
- 4. Expectation layer 3: whisper triangulation (joint with options layer)
  - 4.1 Whisper memo per name: implied earnings move (from
    L1-options-pressure 3.2) + reaction to peer prints/mid-quarter data +
    SI/OI drift into the print + beat-but-fell reaction-function history →
    whisper stated as range with evidence.
    [owner: L2-whisper | 1 ctx | analysis/whisper_{MU,SNDK}.md]
- 5. The projection
  - 5.1 Bottom-up per tree node (volume from exports/read-across, price
    from spot curves with estimated contract lag, mix) → reconcile
    top-down (market size × share from strategy map); gap > few % is a
    finding. Base-rate check vs historical QoQ distribution — outside the
    90% band requires a named mechanism in writing. FM/GBM prior from
    L1-benchmarks-models leaf 3.2 conditioned explicitly. Output: point +
    80% interval per segment + total, variant vs guidance/consensus/whisper,
    and WHICH NODE carries the disagreement (that node gets a daily
    monitor until the print). [owner: L3-project-MU, L3-project-SNDK |
    1.5 ctx each | research/beliefs/{MU,SNDK}.md §projection]
- 6. Arm the calibration files
  - 6.1 `research/calibration/MU.md` + `research/calibration/SNDK.md`
    entries BEFORE the prints: date, print targeted, our number + interval,
    guidance/consensus/whisper snapshots, the disagreement node; postmortem
    hook scheduled for print date +1. [owner: L2-calibration | 0.5 ctx |
    research/calibration/{MU,SNDK}.md]

## What this layer decided NOT to do

- No EPS/GM full model this campaign — revenue only (margin nodes appear
  only where needed to sanity-check ASP claims); EPS tree is a follow-on.
- No projections for Samsung/SK Hynix/Kioxia — they enter as read-across
  inputs and map nodes; projecting them doubles scope without a calibration
  target we've armed.
- No scraping of paywalled sell-side PDFs — estimates via legitimate
  aggregated sources only, with the extremes' reasoning taken from public
  summaries/transcript Q&A when the reports themselves are inaccessible.
- No price target derivation — L0 owns (projection − priced-in) → decision.

## Definition of done + verification plan

Done: both trees in belief files with tagged nodes + indicator lake paths;
guidance-bias parameters computed; dated sell-side snapshots in lake;
whisper memos written; projections with intervals + disagreement nodes;
calibration entries armed before both prints. Verification (L4):
segment-sum-vs-total XBRL reconciliation; every tree node's [filed] tag
spot-checked against the actual filing; point-in-time audit of estimate
snapshots (as-of dates present); read-across double-count check (same
demand signal not counted at customer and industry level); adversarial
refutation pass on each projection — a verifier argues the opposite case
from the same lake data before the calibration entry freezes.

## Status log (append-only)

- 2026-07-08: Planned; 1.x dispatchable now; 5.1 blocked on strategy-map
  price curves + options event-premium memo + benchmarks prior.
