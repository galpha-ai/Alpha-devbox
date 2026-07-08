---
name: inv-strategy-map
description: Supply-demand strategy world map — use for building the competitive/supply-chain ontology around a company (who is monopolist, who is substitutable, who is expanding capacity), tracking commodity-like price curves (DRAM, NAND, HBM, consumer vs enterprise SSD, foundry pricing), the capacity-expansion cycle that starts and ends stock moves, and the fog-of-war audit of where our sampling is precise, stale, or absent.
---

# The Strategy World Map (supply, demand, and the war fog)

Persona: deep fundamental researcher with a general-staff map habit. A
single company is not analyzable in isolation: its revenue is a line
through a supply-demand field. This skill builds and maintains that field
as data, not vibes.

## The core cycle (why this map predicts stock turns)

The repeated shape of commodity-ish tech (memory, storage, panels, ships,
chemicals — anything capacity-bound):

1. Demand > supply → prices rise → margins expand → **stock goes
   parabolic while spot prices rise** — the up-leg is a price-curve
   phenomenon, watchable daily.
2. Fat margins summon capacity: competitors (and the company itself)
   announce **expansions (扩产)**. The *announcement* of credible new
   supply — not its arrival 18 months later — is where the stock's
   down-leg historically begins, because the equity discounts the future
   supply-demand balance, not the current price.
3. Capacity lands into decelerating demand → price war → margin collapse →
   capex cuts and exits → the next shortage is seeded.

Therefore the two highest-value monitors on the map are: **the price
curve's slope** (up-leg intact?) and **the capacity-announcement feed**
(down-leg trigger armed?). Everything else refines these.

## Map ontology (per theater, stored as data)

Maintain per theater (e.g. "NAND/storage", "DRAM/HBM") a machine-readable
map at `research/maps/<theater>.yaml`:

- **Nodes**: companies (SanDisk, Kioxia, Micron, SK Hynix, Samsung,
  Solidigm/Intel-legacy, YMTC...) with role (IDM/fabless/foundry/OEM),
  share by product, and **substitutability score** per product (is their
  NAND interchangeable in a customer's BOM? qualification cycles create
  6-18 month switching frictions — that friction IS pricing power).
- **Edges**: supplies/buys/competes/second-sources, with revenue
  dependence weights where filed (customer-concentration disclosures in
  10-Ks give you real edge weights).
- **Structural attributes** per node: monopoly/oligopoly position (HBM ≈
  3 players, leading-edge foundry ≈ 1.5 — pricing power lives here),
  capacity share, cost-curve position, balance-sheet ability to survive a
  price war (the player who can bleed longest sets the bottom).
- **Capacity ledger** (the crown data): every announced fab/line/expansion
  with: who, product, wafer-starts or GB/month, capex $, announce date,
  target ramp date, and status (announced/under construction/ramping/
  delayed/cancelled). Sources: earnings calls (capex guidance),
  8-K/press releases, trade press. Supply arrives with 12-24 month lags —
  the ledger converts announcements into a **forward supply curve** by
  quarter, which is exactly the input the driver trees in
  `inv-revenue-projection` need for their price nodes.

## Price curves: treat the products as commodities

Memory/storage trades in many venues, so daily/weekly price series exist —
find the highest-frequency sampling available and snapshot it (lake:
`prices/<product>/`):

| Product | Series to hunt | Frequency |
|---|---|---|
| DRAM (DDR4/DDR5 by density) | spot + contract (TrendForce/DRAMeXchange publish spot daily, contract monthly; free tier = headlines/summary numbers — scrape what is public, record exactly which series) | daily / monthly |
| NAND flash (TLC/QLC wafers, by layer count) | same vendors; wafer spot | daily / monthly |
| HBM | no public spot — infer from the 3 players' mix disclosures, ASP commentary, and capacity ledger; treat as contract-only with quarterly sampling | quarterly + event |
| Consumer SSD | retail price indices — scrapeable retail prices per GB (PCPartPicker-style history, or your own daily scrape of standard SKUs) | daily |
| Enterprise/DC SSD | channel price trackers where public; otherwise proxy = NAND wafer spot + controller BOM with a lag | weekly at best |
| Foundry/wafer, substrates, etc. | TWSE monthly revenue of TSMC/UMC/ASE etc. as volume×price composite | monthly |

Rules: a price series' **provenance and basis** (spot vs contract, density,
grade) is recorded in `_meta.json` — mixing DDR4 spot with DDR5 contract
in one chart is how wrong theses get charts. Where no public series
exists, *say the sampling is absent* (fog, below) rather than substituting
a vibe.

## Sampling-frequency doctrine

Earnings give quarterly samples of every node. The map's job is to beat
quarterly: for each map node and each driver-tree leaf, hunt the
highest-frequency public series that correlates with it — daily spot
prices, weekly retail SKU prices, monthly TWSE sales, monthly trade
statistics (Korea/Taiwan export data by category are monthly and free —
memory exports are a superb DRAM/NAND volume proxy), quarterly filings.
Record the found frequency in the map node. **A node sampled only
quarterly is a node where you cannot beat the market's mid-quarter
information; know which nodes those are.**

## The fog-of-war audit (run quarterly per theater)

Three questions, answered in writing in the map file:

1. **Where are we familiar vs blind?** Nodes with current driver trees and
   calibrated forecasts vs nodes carried as names only.
2. **Where is our sampling precise?** Per node: best series frequency,
   last refresh, provenance quality.
3. **Is our data leading, coincident, or consensus?** For each series:
   does the market broadly watch it (TrendForce headlines: yes), is it
   public-but-ignored (Korean export micro-categories, TWSE second-tier
   suppliers: often), or self-collected (your own SSD retail scrape:
   yes)? **Public-but-ignored and self-collected series are the only
   places a data edge can live**; mark them and defend them with
   monitors.

The audit's output prioritizes next quarter's research: extend the map
where fog and payoff-relevance overlap (`questions/backlog.md`).

## Integration

- Driver trees pull price/volume nodes from this map
  (`inv-revenue-projection`).
- Capacity-ledger changes are triaged as events (main skill stage 1) —
  a credible 扩产 announcement in a theater where you're long the
  incumbent is a first-class falsifier candidate.
- Event triage consults the map's edges for second-order effects (an HBM
  capacity shift is a NAND supply event two steps away, because shared
  fab/capex envelopes).
- Monitors: price-curve slope-change alerts (spot rolling 20d slope sign
  flip), capacity-ledger deltas, monthly export-data refresh. All append
  to `research/events/log.md`.
