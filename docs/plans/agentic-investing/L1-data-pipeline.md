# Plan: data-pipeline          Layer: L1 | Parent: L0-campaign-memory-storage.md | 2026-07-08, status: PLANNED

## Objective (one sentence, from parent)

Stand up the theater's data lake and every recurring ingestor — CBOE chains,
FINRA Reg SHO daily, FINRA short interest, EDGAR Form 4 + 8-K polls, bars —
each with download→clean→store→freshness-check, so all other L1 layers
compute from stored, point-in-time-stamped data (skill: inv-data-pipeline).

## Tree

- 1. Lake bootstrap
  - 1.1 Init `/workspace/data/` layout + GCS mirror: check `$DEVBOX_GCS_BUCKET`,
    pull-then-work-then-push rsync; record bucket status in
    `research/process/lessons.md`. [owner: L2-lake-init | 0.5 ctx |
    /workspace/data/ + research/process/lessons.md] [needs-egress]
  - 1.2 Endpoint first-use verification: one small request each to
    cdn.cboe.com, cdn.finra.org, api.finra.org, data.sec.gov, efts.sec.gov,
    stooq.com; log working/blocked per environment. Fallback: mark blocked
    endpoints for devbox-container execution. [owner: L2-endpoint-verify |
    0.5 ctx | research/process/lessons.md] [needs-egress]
- 2. CBOE option-chain snapshots (MU, SNDK, WDC)
  - 2.1 Ingestor `/workspace/pipelines/ingest_cboe_chain.py`: GET
    `cdn.cboe.com/api/global/delayed_quotes/options/{T}.json` per ticker →
    raw gzip to `cboe/chain_{T}/dt=<date>/raw/` → parse via quantlab
    ql-ingest (rust) or Polars → parquet with `oi_asof` = prev trading day →
    `_meta.json` last. Freshness check: partition age ≤ 1 trading day.
    Fallback: Robinhood/FMP MCP chain tools, snapshotted to same lake path.
    [owner: L2-cboe-ingest | 1 ctx | /workspace/data/cboe/chain_{MU,SNDK,WDC}/]
    [needs-egress]
- 3. FINRA Reg SHO daily short volume
  - 3.1 Ingestor `/workspace/pipelines/ingest_regsho.py`:
    `cdn.finra.org/equity/regsho/daily/CNMSshvol{YYYYMMDD}.txt` → keep raw →
    parse pipe-delimited (ql-ingest parser) → filter+store all tickers,
    tag theater set → `finra/regsho_daily/dt=<date>/`. Backfill 250 trading
    days. Freshness: ≤1 bus. day. Fallback: none free — if CDN blocked, run
    inside devbox container. [owner: L2-regsho-ingest | 1 ctx |
    /workspace/data/finra/regsho_daily/] [needs-egress]
- 4. FINRA consolidated short interest (biweekly)
  - 4.1 Ingestor `/workspace/pipelines/ingest_short_interest.py`: POST
    `api.finra.org/data/group/otcMarket/name/consolidatedShortInterest`
    (free key if required — register, store key ref in lessons) →
    `finra/short_interest/dt=<publication date>/`; `published_at` =
    dissemination date, never settlement date. Backfill 3 years for MU,
    SNDK, WDC. Fallback: FINRA website CSV download, or exchange SI pages.
    [owner: L2-si-ingest | 1 ctx | /workspace/data/finra/short_interest/]
    [needs-egress]
- 5. EDGAR Form 4 + 8-K polls (US registrants)
  - 5.1 Watched-CIK file `/workspace/pipelines/watchlists/issuers.csv`:
    MU 0000723125, WDC 0000106040, SNDK [lookup via
    `data.sec.gov/cgi-bin/browse-edgar?company=sandisk` full-text search —
    new registrant post Feb-2025 spin]. [owner: L2-edgar-poll | shared ctx |
    watchlists/issuers.csv] [needs-egress]
  - 5.2 Poller `/workspace/pipelines/ingest_edgar_forms.py`:
    `data.sec.gov/submissions/CIK{10digit}.json` per issuer (UA header with
    contact email, ≤10 req/s) → new Form 4 → fetch ownershipDocument XML →
    parse rows (codes, 10b5-1 flag, footnotes) → `sec/form4/dt=<filing date>/`;
    new 8-K → store index + primary doc → `sec/8k/dt=<filing date>/`.
    Freshness: ≤1 bus. day. Fallback: FMP `insiderTrades`/`secFilings` MCP,
    snapshotted. [owner: L2-edgar-poll | 1 ctx | /workspace/data/sec/{form4,8k}/]
    [needs-egress]
  - 5.3 Non-EDGAR issuers: disclosure feed design for 000660.KS/005930.KS
    (KRX KIND / DART API — free key) and 285A.T (TDnet); ingest headlines +
    filing metadata only → `disclosures/kr_jp/dt=<date>/`. Fallback: manual
    weekly sweep documented as a monitor. [owner: L2-krjp-poll | 1 ctx |
    /workspace/data/disclosures/kr_jp/] [needs-egress]
- 6. Bars
  - 6.1 Ingestor `/workspace/pipelines/ingest_bars.py`: daily OHLCV for MU,
    SNDK, WDC, 000660.KS, 005930.KS, 285A.T + peer basket (STX, spot ETFs)
    via stooq CSV (`stooq.com/q/d/l/?s={t}.us&i=d`); yfinance fallback; MCP
    quotes fallback. 5y backfill; split/div adjustment factors stored
    separately per inv-quant-foundations. → `bars/daily/dt=<date>/`.
    [owner: L2-bars-ingest | 1 ctx | /workspace/data/bars/daily/] [needs-egress]
- 7. Scheduling + monitor wiring
  - 7.1 Register cadences per L0 standing-cadence table with the harness
    scheduler; each job ends by running its `research/monitors/*.md` specs
    and appending firings to `research/events/log.md`; STALE-DATA rule
    enforced in every monitor. [owner: L2-scheduler | 1 ctx |
    research/monitors/ + scheduler entries]

## What this layer decided NOT to do

- No intraday/minute bars: daily suffices for every consumer here;
  inv-flow-tape work is out of campaign scope.
- No 13F/N-PORT ingestion here — owned by L1-positioning (avoids two owners
  of one dataset).
- No price-curve/scrape ingestors — owned by L1-strategy-map (domain
  cleaning rules live there); it reuses these lake conventions.
- No paid data sources; no borrow-rate vendor — implied borrow comes from
  L1-options-pressure instead.

## Definition of done + verification plan

Done: all ingestors run twice on consecutive days producing valid partitions
(`_meta.json` present, row_count > 0, raw/ retained); backfills complete;
scheduler entries live; GCS push succeeded (or bucket-absence logged).
Verification (L4, per L1-verification.md): point-in-time audit of every
`_meta.json` (published_at vs effective_date correctness per dataset's rules);
row-count reconciliation vs source (Reg SHO file line count, chain contract
count); rust-vs-python parser fixture cross-check for Reg SHO + CBOE;
freshness-check tamper test (delete a partition, monitor must alert STALE).

## Status log (append-only)

- 2026-07-08: Planned; leaves 1.1–7.1 defined; nothing dispatched.
