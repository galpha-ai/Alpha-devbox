---
name: inv-13f-positioning
description: Institutional positioning from SEC 13F and N-PORT filings — use for questions about who owns a stock, hedge fund crowding, big fund long-side position changes, whale watching (what did Berkshire/Tiger/Coatue buy), ownership concentration, or building a crowding index. Covers download from EDGAR, quarter-over-quarter diffing, hedge-fund universe construction, crowding metrics, and the 45-day-lag discipline.
---

# 13F / N-PORT Institutional Positioning

Persona: mid-frequency alt-data researcher. This is the *slowest* layer of
the positioning cube — structural context, never timing. Its weight in any
argument is capped by its lag.

## What the filings actually contain (and don't)

- **13F-HR**: quarterly, institutional managers ≥$100M US equity AUM, filed
  ≤45 days after quarter end. Long US-listed equity positions **plus listed
  call/put option positions** (`putCall` column — HF option books are
  visible and usually ignored by tourists; don't ignore them). **No shorts,
  no swaps, no non-US, no bonds.** A "net short" fund can look long-only
  here.
- **13F-HR/A** amendments: restate or add; always take the latest accession
  per (CIK, period) but record the original `published_at` for
  point-in-time work.
- **N-PORT-P**: registered funds (mutual funds/ETFs) file **monthly**
  portfolios, public with ~60-day lag. This is the best free window into
  **large long-only funds** (Fidelity/Capital Group/T. Rowe complexes) —
  monthly granularity shows accumulation *paths*, not just quarter ends.
- **13D/G**: >5% activist/passive stakes, event-driven — catches
  concentrated new positions faster than 13F.

## Download

Per the endpoint registry in `inv-data-pipeline`:

1. **Backfill**: DERA "Form 13F data sets" quarterly TSV zips (structured
   `INFOTABLE` for every filer) — one download per quarter, load to
   `sec/13f/dt=<pubdate>/`.
2. **Incremental / per-manager**: `data.sec.gov/submissions/CIK{...}.json`
   for the manager's CIK → newest 13F-HR accession → fetch
   `infotable.xml` from the archives. Keep a watched-managers file
   (`/workspace/pipelines/watchlists/managers.csv`: CIK, name, type
   HF/LO/quant, why watched).
3. N-PORT via full-text search or submissions API per fund CIK; parse the
   holdings section for watched tickers only (files are big).
4. MCP fallback for interactive questions: FMP `form13F` tools — snapshot
   into the lake if it feeds a conclusion.

Issuer join key is CUSIP (map CUSIP→ticker via a maintained alias table in
the lake; tickers change, CUSIPs mostly don't).

## The quarterly diff (the basic object)

For each (manager, issuer): `new / added / trimmed / exited / unchanged`,
with Δshares, Δ$ value, and position rank within the manager's book. Value
changes confound price moves with flows — **always diff shares, not
dollars**, and compute the implied flow at quarter-average price.

## Crowding metrics (compute, don't vibe)

Maintain a hedge-fund sub-universe (fundamentally-driven HFs — the
watched-managers file, type=HF; start with the well-known tiger cubs +
majors and grow it) and compute per stock, per quarter:

- **HF ownership % of float** = Σ HF shares / float.
- **Crowding score** = z-score combo of: HF count holding, HF % float,
  mean position rank (a stock that is a top-5 position for 12 HFs is
  crowded in the way that matters), and QoQ change in each.
- **Breadth vs concentration**: many small holders ≠ few huge holders;
  report both.
- **Consensus-book overlap**: pairwise overlap of HF books (Jaccard on
  top-20 holdings) — rising overlap = systemic crowding, matters for
  drawdown correlation.
- **Exit risk asymmetry**: crowded + illiquid (HF % float / ADV) is the
  quantity that turns "great company" into "-25% in a week" when the
  thesis cracks. Always report crowding next to days-to-exit.

Crowding is a **conditioner, not a signal**: it amplifies whatever else is
true (squeeze setups with `inv-short-interest`, air pockets on misses with
`inv-revenue-projection`).

## Whale watch

For each watched manager, quarterly: new positions and exits (with sizing
as % of their book), plus 13D/G events between quarters. Interpretation
discipline: a Q1 buy reported in mid-Q2 tells you the *thesis exists*, not
that the entry price is available — check what price range the position
was accumulated in (quarter VWAP band) before "following".

## Point-in-time traps

- Join on **filing date** (published_at), never quarter end. A backtest
  using holdings on their effective date has a 45-day crystal ball.
- Q4 filings cluster in mid-February; "quarterly" signals are actually
  event-dated to publication bursts.
- Managers file confidential treatment for some positions (revealed
  later) — new-position discovery is right-censored.
- Value units: older filings report $ thousands; post-2023 in dollars.
  Sanity-check magnitudes at ingestion (a $4T single position is a parse
  bug, which you will otherwise discover in a writeup).

## Monitors

Standard monitors (register per `inv-data-pipeline`, state in
`research/monitors/`): quarterly crowding-score refresh on watched tickers
with alert on decile jumps; watched-manager new/exit alerts; 13D/G
real-time poll on watched tickers. Alerts append to `research/events/log.md`.
