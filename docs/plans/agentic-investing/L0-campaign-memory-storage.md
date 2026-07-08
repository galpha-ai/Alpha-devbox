# Campaign: Memory & Storage          Layer: L0 | Parent: none (decision layer) | 2026-07-08, status: PLANNED

## Objective

Build the full data + map + projection stack for the memory/storage theater
(DRAM, NAND, HBM, consumer SSD, enterprise SSD) and produce **calibrated
next-quarter revenue projections for MU and SNDK** — point + 80% interval per
segment, graded against the actual prints in `research/calibration/`.

## Scope

- **Issuers**: Micron (MU, CIK 0000723125), SanDisk (SNDK, CIK [lookup —
  new registrant after Feb-2025 spin from WDC]), Western Digital (WDC, CIK
  0000106040), SK Hynix (000660.KS), Samsung Electronics (005930.KS), Kioxia
  (285A.T). US-listed trio get the full positioning cube; the Korean/Japanese
  three get strategy-map nodes + non-EDGAR disclosure feeds (DART/KIND, TDnet).
- **Products**: DRAM (DDR4/DDR5 by density), NAND (TLC/QLC wafer), HBM,
  consumer SSD, enterprise/DC SSD.
- **Projection targets**: next quarterly revenue prints for MU (FQ1-27,
  ~late Sep 2026) and SNDK (FQ4/FQ1 boundary, ~Aug 2026) — [confirm exact
  print dates via earnings calendar in L1-revenue-projection leaf 5.1].
- **Out of scope for this campaign**: EPS/margin trees beyond what revenue
  requires, STX/pure-HDD dynamics, YMTC/CXMT beyond map nodes, any trade
  execution. Decisions remain with this L0 layer, fed by L1 outputs.

## Budget judgment

Theater VoI is high: memory is mid-cycle with an HBM capacity super-cycle
overlay, both target names have scheduled falsifiers (prints) inside 90 days,
and the price-curve/capacity-ledger machinery is reusable for every future
memory-cycle question. Justified fleet: 7 L1 planners → ~35 L2 tasks →
per-ticker/per-quarter L3 fan-out → L4 verifiers on everything feeding a
belief. Roughly a full day of agent time for the build, then a small daily
standing cost. Spend is front-loaded in L1-data-pipeline and L1-strategy-map;
projection layers are cheap once the lake exists. Re-check this judgment if
egress blocks force manual fallbacks on >2 core datasets.

## L1 fan-out (plan docs in this directory; dependency order noted)

1. `L1-data-pipeline.md` — lake + ingestors (CBOE chains, Reg SHO, SI,
   EDGAR Form 4/8-K, bars). **Blocks everything else**; dispatch first.
2. `L1-positioning.md` — 13F/N-PORT crowding baseline + whale watch.
3. `L1-options-pressure.md` — P/C, OI walls, implied distribution, implied
   earnings move, GEX + squeeze screens for MU/SNDK/WDC.
4. `L1-strategy-map.md` — theater ontology YAML, capacity ledger, DRAM/NAND
   price curves, SSD retail scrape design, fog-of-war audit.
5. `L1-revenue-projection.md` — MU + SNDK driver trees, guidance bias,
   sell-side snapshot, whisper triangulation, calibration files armed.
6. `L1-benchmarks-models.md` — no-lookahead benchmarks from the lake
   (quantlab/python/quantlab/benchmarks.py), baselines, GBM + Chronos/TimesFM.
7. `L1-verification.md` — L4 adversarial layer over all of the above.

2–4 run in parallel once 1's relevant ingestors land; 5 needs 3+4 partials;
6 needs the lake populated; 7 runs continuously against everything.

## Definition of done

- Lake partitions exist with `_meta.json` for every dataset in L1-data-pipeline,
  freshness checks green two consecutive days.
- `research/maps/memory-storage.yaml` populated (nodes, edges, capacity
  ledger 2024–2026, sampling-frequency annotations, fog audit v1).
- Positioning cube baseline written into `research/beliefs/MU.md`,
  `research/beliefs/SNDK.md` (crowding, SI, insider, options pressure).
- MU and SNDK revenue projections with 80% intervals, consensus/guidance/
  whisper snapshots, registered in `research/calibration/MU.md` and
  `research/calibration/SNDK.md` **before** the respective prints.
- Benchmark suite frozen (hashes recorded) with baseline + GBM + FM
  scorecards; models beaten-or-benched decisions logged.
- Every L4 check in `L1-verification.md` executed with a written verdict;
  no belief-file claim without a passing verification entry.
- Synthesis note at L0: beliefs updated, question backlog updated,
  `research/process/lessons.md` appended.

## Standing cadence (registered once built; per inv-data-pipeline)

| Cadence | Jobs |
|---|---|
| Daily (post-close) | CBOE chain snapshots MU/SNDK/WDC; FINRA Reg SHO file + SVR z-alerts; bars refresh; EDGAR Form 4/8-K poll (MU, SNDK, WDC CIKs); DRAM/NAND spot headline scrape; SSD retail SKU scrape; P/C percentile, OI-wall migration, GEX-flip, implied-borrow alerts |
| Biweekly (SI pub days, ~T+7 bus. days) | FINRA consolidated SI pull + ΔSI diff alert + SVR-triangulation grading |
| Monthly | Korea (KITA/customs) + Taiwan memory export stats; N-PORT sweep for watched long-only funds; TWSE monthly sales read-across; DART/KIND + TDnet disclosure sweep for 000660.KS/005930.KS/285A.T |
| Quarterly | 13F sweep (peak ~45d after quarter end) + crowding refresh; fog-of-war audit; calibration grading (MAPE/hit-rate) + benchmark re-freeze; guidance-bias parameter update after each print |

All monitor firings append to `research/events/log.md`; this L0 session wakes
only for triaged material events.

## Status log (append-only)

- 2026-07-08: Campaign planned; 7 L1 docs written; nothing dispatched yet.
