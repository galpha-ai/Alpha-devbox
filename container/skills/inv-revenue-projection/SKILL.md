---
name: inv-revenue-projection
description: Forecasting the intermediate dimensions — next-quarter revenue by segment, EPS trajectory, margins — use for building revenue driver trees, decomposing historical growth (volume/ASP/mix/FX), projecting forward with supply-chain read-across, tracking sell-side estimates per bank with bias models, inferring buy-side whisper, and grading your own forecasts in calibration files. The semi-verifiable core of the investing system.
---

# Revenue Projection: Predicting Intermediate Dimensions

Persona: deep fundamental researcher, with the mid-frequency researcher
checking every join. The commitment: predict the *verifiable intermediate
dimension* (revenue, EPS, margin — things with a print date), and derive
price views from (your number − what's priced in). Every forecast lands in
a calibration file and gets graded. This is what makes the whole system
semi-verifiable rather than a narrative shop.

## Step 1: Build the driver tree from filings

From 10-K/10-Q segment disclosures (XBRL companyfacts + the segment tables
in the filing; MCP `statements`/segment tools as convenience, snapshot to
lake):

- Decompose: total revenue → reportable segments → (units × ASP) or
  (customers × ARPU) or (capacity × utilization × price) per segment.
- Decompose *historical* growth per segment into volume / price / mix /
  FX / M&A using management's own MD&A attribution where given, your
  estimate where not — tag every node `[filed]` / `[derived]` /
  `[assumed]`.
- Identify each node's **leading indicators** and their frequencies — this
  is where the tree meets the strategy map (`inv-strategy-map`): commodity
  price curves (daily), TWSE monthly sales of suppliers/customers
  (monthly), hyperscaler capex guidance (quarterly), peer prints landing
  *before* your company (the earnings calendar is a read-across schedule).
- The tree lives in `beliefs/<entity>.md` (template in agentic-investing)
  with lake paths for every indicator.

## Step 2: Measure what the market expects (three layers, never skip)

For each upcoming print, record in the calibration file *before* forming
your own number:

1. **Guidance**: what management guided last call (range, and whether they
   habitually sandbag — compute their guide-vs-actual history from
   transcript/8-K record; a company that beat its own midpoint 11 of 12
   quarters has a *guidance bias parameter*, use it).
2. **Sell-side, per bank**: each analyst's estimate, date, and prior
   revision (FMP `analyst` estimates tools; store history — the vendor
   restates, your snapshots don't). Model the water content: estimates
   cluster toward guidance (anchoring); pre-print numbers drift to be
   beatable (positive surprise base rate ~70-80% in US large caps is a
   *structural* artifact, not information); the informative objects are
   **revision breadth and velocity** (how many banks moved, how fast,
   after what datapoint) and the **highest/lowest estimate's reasoning**
   (read those two reports' logic via transcripts/notes if accessible —
   the extremes carry the actual disagreement).
3. **Buy-side whisper** (unobservable, so triangulate):
   - options implied move (`inv-options-pressure`) = market's uncertainty;
   - price reaction to *peer* prints and mid-quarter datapoints = which
     direction the buy side is leaning vs published consensus;
   - positioning changes into the print (SI drift, OI skew shift) =
     whisper direction with capital behind it;
   - the stock's reaction function history: quarters where it beat
     consensus but fell = whisper was above consensus; learn the gap.
   State whisper as a range with the evidence, e.g. "whisper ≈ consensus
   +2-4%: buy-side leaning long via call skew + stock rallied on peer's
   in-line".

## Step 3: Your number — the supply-chain jigsaw

Project each tree node bottom-up, then reconcile top-down:

- **Volume nodes**: from upstream shipments (foundry/ODM monthly revenue,
  TWSE), customer capex and inventory levels (their 10-Qs — inventory
  build at customers is *your* future order cut), industry unit forecasts
  only as priors.
- **Price nodes**: from the commodity price curves in `inv-strategy-map`
  (e.g. DRAM/NAND spot and contract trends → memory-maker ASPs with a
  1-2 quarter contract lag — estimate the lag per company from history,
  don't assume).
- **Mix/margin**: price × cost curves; operating leverage from the filed
  cost structure (fixed/variable split derived from incremental margins
  across past cycles).
- **Base rates**: your bottom-up number gets sanity-checked against the
  distribution of historical QoQ growth for this company and its sector at
  this cycle stage — a projection outside the historical 90% band needs a
  named mechanism, in writing.
- Reconcile: bottom-up sum vs top-down (market size × share). Gaps > a few
  % are a finding (double-counting or a hidden assumption), not rounding.

Output per print: point + 80% interval per segment and total, the variant
vs consensus/guidance/whisper, and **which tree node carries the
disagreement** — that node is what you monitor daily until the print.

## Step 4: Calibration files (the grading loop)

`research/calibration/<entity>.md`, append-only: date, print targeted, your
number + interval, consensus/guidance/whisper snapshot, actual, error,
directional hit vs consensus, and *which node was wrong*. Quarterly, compute
MAPE and hit rate per entity and per node type — node-level error patterns
("my ASP lags are systematically short") go to `process/lessons.md`. A
forecaster who doesn't know their own calibration is a pundit.

## Time-series models as priors, not oracles

For nodes with decent history, run the statistical baseline
(`inv-foundation-models`: TimesFM/Chronos zero-shot, plus a seasonal-naive
and a gradient-boosting model per `inv-quant-foundations`). The model gives
the *unconditional* prior; your supply-chain jigsaw is the *conditional*
update. When your number differs from the model prior by more than the
model's own interval, the writeup must name the conditioning information —
if you can't, you don't have any.

## Traps

- Consensus data restates (banks drop out, vendors backfill) — only your
  own dated snapshots are point-in-time.
- Guidance ranges are strategic instruments, not forecasts.
- Segment redefinitions break trees silently — diff segment names every
  10-K and re-map.
- Read-across double-counting: don't count the same demand signal once at
  the customer and once at the industry level.
- Your variant can be right and the trade wrong if whisper already had it
  — always price the *gap to whisper*, not the gap to published consensus.
