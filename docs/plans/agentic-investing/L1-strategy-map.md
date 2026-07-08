# Plan: strategy-map          Layer: L1 | Parent: L0-campaign-memory-storage.md | 2026-07-08, status: PLANNED

## Objective (one sentence, from parent)

Build the memory/storage war map — node/edge ontology, capacity ledger
2024–2026, DRAM/NAND/HBM/SSD price curves at the highest public frequency,
and the fog-of-war audit — as machine-readable data feeding the driver
trees' price/volume nodes (skill: inv-strategy-map).

## Tree

- 1. Ontology YAML
  - 1.1 `research/maps/memory-storage.yaml` v1: nodes = Micron, SanDisk,
    Kioxia (NAND JV partners — model the JV explicitly), SK Hynix (+
    Solidigm), Samsung, WDC (HDD + post-spin remainder), YMTC, CXMT,
    Nanya; per node: role, share by product (DRAM/NAND/HBM/cSSD/eSSD),
    substitutability score with qualification-friction notes, oligopoly
    position (HBM ≈ 3 players), cost-curve seat, balance-sheet stamina.
    Edges: supplies/buys/competes/second-sources with 10-K customer-
    concentration weights where filed [derived] elsewhere.
    [owner: L2-ontology | 1.5 ctx | research/maps/memory-storage.yaml]
- 2. Capacity ledger backfill (the crown data)
  - 2.1 Public announcements 2024-01→2026-07: earnings-call capex guidance,
    8-K/press releases, trade press; per entry: who, product, wafer-starts
    or GB/mo, capex $, announce date, target ramp, status. Sources: EDGAR
    full-text search (`efts.sec.gov` — "fab", "capacity expansion"), MU/WDC/
    SNDK transcripts (FMP `earningsTranscript` MCP), DART/TDnet + trade
    press for the KR/JP three. → ledger section of the YAML + snapshot
    `capacity/ledger/dt=<date>/`. [owner: L2-capacity-ledger | 2 ctx,
    split per company as L3 | research/maps/memory-storage.yaml +
    /workspace/data/capacity/ledger/] [needs-egress]
  - 2.2 Forward supply curve by product-quarter derived from ledger (12–24mo
    ramp lags, status-weighted) → parquet the driver trees can join.
    [owner: L2-supply-curve | 1 ctx | /workspace/data/capacity/supply_curve/]
- 3. Price curves (snapshot everything; provenance/basis in _meta)
  - 3.1 DRAM + NAND spot: TrendForce/DRAMeXchange **public** headline
    numbers (free tier) scraped daily — record exactly which series (DDR5
    16Gb spot avg, TLC 512Gb wafer, etc.) → `prices/dram_spot/`,
    `prices/nand_spot/`. Fallback if scrape blocked/paywalled: weekly manual
    sweep of public trade-press quotes (TrendForce press releases, DigiTimes
    headlines), logged with provenance. [owner: L2-spot-scrape | 1.5 ctx |
    /workspace/data/prices/{dram_spot,nand_spot}/] [needs-egress]
  - 3.2 Korea/Taiwan export stats (monthly, free, public-but-ignored):
    Korea customs/KITA memory-chip export value+volume categories; Taiwan
    MOF export data → `prices/kr_tw_exports/`; superb DRAM/NAND volume
    proxy. Fallback: TradingEconomics/Bank of Korea series.
    [owner: L2-exports | 1 ctx | /workspace/data/prices/kr_tw_exports/]
    [needs-egress]
  - 3.3 Consumer-SSD retail scrape DESIGN + v1: pick ~8 standard SKUs
    (1TB/2TB TLC NVMe across Samsung 990, WD SN850X, Crucial T500, SK P41
    etc.), daily price per GB from 2–3 retailers; self-collected series =
    defensible edge → `prices/ssd_retail/`. Fallback: PCPartPicker-style
    public history pages weekly. [owner: L2-ssd-scrape | 1.5 ctx |
    /workspace/data/prices/ssd_retail/ + pipelines/ingest_ssd_retail.py]
    [needs-egress]
  - 3.4 HBM: no public spot — quarterly inference note from the 3 players'
    mix/ASP commentary + ledger; enterprise SSD: proxy = NAND wafer spot +
    controller BOM lag, stated as proxy. [owner: L2-hbm-essd-notes | 1 ctx |
    analysis/hbm_essd_pricing.md]
- 4. Sampling-frequency annotation + fog-of-war audit v1
  - 4.1 Annotate every YAML node/series: best frequency, last refresh,
    provenance, leading/coincident/consensus classification (TrendForce
    headlines = consensus-watched; export micro-categories = ignored; SSD
    scrape = self-collected). Answer the three audit questions in writing;
    output prioritizes `research/questions/backlog.md`.
    [owner: L2-fog-audit | 1 ctx | research/maps/memory-storage.yaml §audit]
- 5. Monitors
  - 5.1 Register: spot 20d-slope sign-flip alert (DRAM + NAND), capacity-
    ledger delta triage (a credible expansion announcement = first-class
    event), monthly export refresh, SSD scrape freshness. Specs in
    `research/monitors/strategy-map-memory.md`. [owner: L2-monitors |
    0.5 ctx | research/monitors/strategy-map-memory.md]

## What this layer decided NOT to do

- No paid TrendForce/DRAMeXchange subscription data; public headline
  numbers only, provenance recorded — mixing bases is how wrong theses
  get charts.
- No HDD market modeling (WDC's other half) beyond a stub node — not a
  driver of the two projection targets.
- No China domestic-market deep dive (YMTC/CXMT carried as capacity-ledger
  + share nodes only) — high fog, low near-term print relevance; revisit
  at the quarterly audit.
- No backcast of price curves we didn't sample — history starts where
  public archives start; gaps recorded as fog, never interpolated.

## Definition of done + verification plan

Done: YAML v1 with ≥9 nodes fully attributed, capacity ledger ≥ 2024-01
with status per entry, forward supply curve parquet, three live price
series (DRAM spot, NAND spot, SSD retail) + monthly exports, fog audit
answered, monitors live. Verification (L4): ledger spot-audit — 5 random
entries re-verified against primary sources with dates; price-series basis
check (no DDR4-spot/DDR5-contract mixing in any derived chart); export-data
category mapping cross-checked one month by hand; refutation pass on any
map-derived claim ("HBM crowds out NAND capex") before it enters a belief.

## Status log (append-only)

- 2026-07-08: Planned; 1.1 dispatchable immediately (no lake dependency);
  3.x depend on L1-data-pipeline leaf 1.2 endpoint verification.
