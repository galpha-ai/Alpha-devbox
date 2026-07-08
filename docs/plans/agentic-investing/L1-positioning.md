# Plan: positioning          Layer: L1 | Parent: L0-campaign-memory-storage.md | 2026-07-08, status: PLANNED

## Objective (one sentence, from parent)

Build the 13F/N-PORT crowding baseline and whale watch for the memory/storage
theater (MU, SNDK, WDC US-listed; ADR/foreign holdings where visible) so
every thesis is conditioned on who already owns it (skill: inv-13f-positioning).

## Tree

- 1. Universe and reference data
  - 1.1 Watched-managers file `/workspace/pipelines/watchlists/managers.csv`:
    tiger cubs + majors + memory-active HFs and the big long-only complexes
    (Fidelity, Capital Group, T. Rowe), with CIK, type HF/LO/quant, why
    watched. [owner: L2-universe | 0.5 ctx | watchlists/managers.csv]
  - 1.2 CUSIP→ticker alias table for MU, SNDK, WDC (SNDK CUSIP new since
    Feb-2025 spin — [lookup] from a recent 13F infotable), stored in lake.
    [owner: L2-universe | 0.5 ctx | /workspace/data/ref/cusip_alias/]
- 2. 13F backfill + incremental
  - 2.1 DERA 13F quarterly TSV zips, 2023Q1–2026Q1 → filter theater CUSIPs →
    `sec/13f/dt=<pub date>/`; keep latest accession per (CIK, period) but
    record original published_at. Fallback: FMP `form13F` MCP snapshotted to
    same path. [owner: L2-13f-backfill | 1.5 ctx |
    /workspace/data/sec/13f/] [needs-egress]
  - 2.2 Incremental per watched manager via
    `data.sec.gov/submissions/CIK{...}.json` → newest 13F-HR → infotable.xml;
    include `putCall` option rows (HF option books on MU/SNDK are part of
    positioning). [owner: L2-13f-incr | 1 ctx | /workspace/data/sec/13f/]
    [needs-egress]
- 3. N-PORT monthly long-only window
  - 3.1 For the LO complexes' flagship funds [lookup fund CIKs via EDGAR
    company search], parse N-PORT-P holdings for theater tickers only →
    `sec/nport/dt=<pub date>/` (~60d lag noted in _meta). Fallback: skip to
    quarterly 13F view and record the sampling gap in the fog audit.
    [owner: L2-nport | 1.5 ctx | /workspace/data/sec/nport/] [needs-egress]
- 4. Quarterly diff + crowding metrics
  - 4.1 Diff engine (Polars, `/workspace/pipelines/analysis/pos_diff.py`):
    per (manager, issuer) new/added/trimmed/exited with Δshares (never Δ$),
    implied flow at quarter-VWAP. [owner: L2-crowding | 1 ctx |
    analysis/pos_diff.py + parquet output]
  - 4.2 Crowding scorecard per stock-quarter: HF % float, HF count, mean
    position rank, breadth vs concentration, Jaccard consensus-book overlap,
    exit-risk (HF%float / ADV from bars lake) → writeup + numbers into
    `research/beliefs/{MU,SNDK,WDC}.md` positioning section.
    [owner: L2-crowding | 1 ctx | analysis/crowding_memory.md]
- 5. Whale watch + 13D/G
  - 5.1 Latest-quarter new/exit report for watched managers in theater names,
    with quarter-VWAP accumulation bands; 13D/G poll wired onto the EDGAR
    poller from L1-data-pipeline leaf 5.2. [owner: L2-whale | 1 ctx |
    analysis/whale_memory.md + research/monitors/13dg-memory.md] [needs-egress]
- 6. Monitors
  - 6.1 Register: quarterly crowding refresh with decile-jump alert;
    watched-manager new/exit alert; 13D/G real-time poll on MU/SNDK/WDC.
    Specs in `research/monitors/positioning-memory.md`; firings →
    `research/events/log.md`. [owner: L2-monitors | 0.5 ctx |
    research/monitors/positioning-memory.md]

## What this layer decided NOT to do

- No full-market crowding index — theater tickers + watched managers only;
  a market-wide index is a different campaign's infrastructure.
- No foreign-listing ownership reconstruction for Samsung/SK Hynix/Kioxia
  (no 13F visibility beyond ADR/GDR slivers); their ownership is carried as
  fog in the strategy map, not fake data.
- No short-side inference from 13F (impossible — the filing is long-only);
  shorts come from the SI dataset.
- Not "following" any whale trade — interpretation stays at L0; this layer
  reports positioning facts and VWAP bands only.

## Definition of done + verification plan

Done: 13-quarter backfill + current quarter loaded; crowding scorecards for
MU/SNDK/WDC written into belief files with lake paths; whale report done;
monitors registered. Verification (L4): point-in-time audit — all joins on
filing date not quarter end (Q4 mid-February clustering spot-checked);
value-unit sanity (post-2023 dollars vs older $thousands — flag any position
> $100B); diff engine recompute on one manager by hand; N-PORT lag correctly
stamped; refutation pass on any "crowded/uncrowded" claim reaching a belief
file (recompute score from raw partitions).

## Status log (append-only)

- 2026-07-08: Planned; awaiting L1-data-pipeline leaves 1.1, 6.1 (bars for
  ADV) before 4.2 dispatch.
