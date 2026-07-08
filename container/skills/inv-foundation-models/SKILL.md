---
name: inv-foundation-models
description: Time-series foundation models and AI-statistician workflows as forecasting sub-capabilities — use when a driver-tree node, price curve, or bar series needs a statistical forecast baseline (TimesFM, Chronos zero-shot), when evaluating orderbook/K-line foundation models, or when running a Bayesian model-criticism loop over any predictive model in the system. Defines how learned models are allowed to enter conclusions: as priors with calibration receipts, never as oracles.
---

# Foundation Models & the AI Statistician Seat

Persona: the Stanford AI + statistics PhDs seat. Two capabilities: (1) use
pretrained time-series foundation models as cheap, strong forecasting
baselines; (2) run a Bayesian-workflow criticism loop over every model in
the system, learned or hand-built.

## Model inventory (verify availability at runtime — do not trust memory)

Names and checkpoints move fast. On first use in an environment, verify on
the web/HF hub what the current best checkpoints are, and record the chosen
ones (with exact model ids + versions) in `research/process/lessons.md`.
The stable landscape as a starting point:

- **TimesFM** (Google): decoder-only TS foundation model, zero-shot point
  forecasts + quantile heads; good default for daily/weekly univariate
  nodes (price curves, export series, revenue proxies).
- **Chronos / Chronos-Bolt** (Amazon): tokenizes real-valued series for a
  T5-style LM; zero-shot *probabilistic* forecasts (sample paths →
  intervals); strong on short business series; the K-line usage below.
- **Moirai / Lag-Llama / GraniteTTM**: alternates worth benchmarking when
  the two above disagree; covariate support varies by family — check per
  version.
- **Orderbook / market-microstructure FMs**: research-stage (LOB
  pretraining literature); no stable public checkpoint to rely on — if a
  question needs microstructure, say the capability is research-grade and
  scope it explicitly rather than pretending.
- **"AI statistician" / Bayesian-workflow agents** (Google-line work on
  automated statistical modeling): treat as a *workflow* to implement with
  our own tools (below) rather than a dependency — the workflow is the
  durable part; whatever released assistant/model exists at runtime can
  slot in after verification.

## Usage doctrine: models are priors with receipts

1. **Always run the dumb baselines next to the FM**: seasonal-naive,
   drift, and a GBM per `inv-quant-foundations`. An FM that doesn't beat
   seasonal-naive on *your* series' backtest gets benched for that series
   — and this happens often on quarterly fundamentals (8-40 points is
   thin for any model; the FM's value there is calibrated intervals, not
   point accuracy).
2. **Zero-shot first, fine-tune almost never**: our per-series sample
   sizes rarely justify fine-tuning; context-window conditioning (feed
   the related series — e.g. DRAM spot as covariate/context where the
   model family supports it) is the cheaper lever.
3. **Backtest = rolling-origin, publication-time honest**: forecasts made
   only from data published before each origin (`inv-quant-foundations`
   rules apply to FM inputs identically — an FM fed restated data
   backtests as a crystal ball).
4. **K-line (bar) usage**: Chronos-style models on OHLCV work as
   *distributional* short-horizon baselines — use the sampled paths for
   interval and tail estimates feeding scenario tables, not for point
   direction bets; log-returns in, never raw prices; volume as separate
   channel where supported.
5. **The FM's role in the loop**: `inv-revenue-projection` treats the FM
   forecast as the unconditional prior that your supply-chain jigsaw
   conditions on. Disagreement beyond the FM's own interval must be
   justified by named conditioning information.

## The Bayesian criticism loop (applies to every model here)

Box's loop, run explicitly and logged per model in
`research/calibration/models/<name>.md`:

1. **Prior predictive check**: before fitting/deploying, simulate — do the
   model's assumptions generate data that looks like the domain at all?
2. **Fit / condition.**
3. **Posterior predictive check**: residual structure, coverage of the
   stated intervals (an "80% interval" that covers 60% is a lie — track
   empirical coverage), tail behavior on the events that matter.
4. **Criticize & expand**: where checks fail, expand the model (covariate,
   regime split, jump component) or shrink its mandate (bench it for that
   series class). Every expansion is a dated entry — the model registry
   is itself a continual-learning artifact.

Hand-built Bayesian models (PyMC/Stan-style) earn their place for
*structured* problems where the FM has no covariate path: hierarchical
guidance-bias models across companies (partial pooling of sandbagging
parameters), state-space models of contract-vs-spot price lags, capacity-
ledger arrival models. Same criticism loop, same registry.

## Engineering

Inference runs in quantlab's Python layer (Polars in/out, model wrappers
behind one `Forecaster` interface so baselines and FMs swap freely);
anything latency-sensitive stays out of the hot path — FMs are batch
tools here, not tick-time tools. GPU absent → CPU-size checkpoints
(Chronos-Bolt small/TimesFM base run on CPU acceptably for daily batch).
Every forecast written to the lake carries model id + version + context
window + input partition hashes, so any number in a memo can be traced to
the exact model call that produced it.
