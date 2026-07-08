---
name: inv-quant-foundations
description: Time-series data science and predictive ML discipline for all investing research — read before writing any pandas/DuckDB analysis, backtest, event study, factor/signal evaluation, or Random Forest / gradient boosting / regression model on market or fundamental data. Encodes point-in-time hygiene, purged walk-forward validation, causal analysis standards, domain-knowledge data cleaning, and how to avoid forward-looking bias and multiple-testing self-deception.
---

# Quant Research Foundations

This is the basic training of the old world that the new world is built on:
if the pandas is sloppy, every conclusion above it is fiction. These rules
apply to every `inv-*` analysis and every model.

## Time discipline (the cardinal rules)

1. **Every row has three times**: `effective_date` (what period it
   describes), `published_at` (when the market could know it), `fetched_at`
   (when we grabbed it). All predictive joins use `published_at`. Vendor
   datasets that only carry effective dates are guilty until proven
   innocent — reconstruct publication lag from the source's rules (13F:
   ≤45d; SI: ~7 bus. days; Form 4: ≤2 bus. days; earnings: the announcement
   timestamp, am/pm matters).
2. **Join with `merge_asof(direction='backward')`** on publication time, with
   an explicit `tolerance`. Never join fundamentals to prices on calendar
   quarter.
3. **Targets never touch the future accidentally.** Forward return targets
   are built by shifting *prices* forward explicitly
   (`px.shift(-h)/px - 1`), computed once, named `fwd_ret_{h}d`, and the
   feature matrix is asserted to contain no column with `fwd_` prefix.
4. **Timezones**: everything UTC internally; US market timestamps are
   America/New_York at source — convert once at ingestion, never ad hoc.
5. **Trading calendar**: business-day arithmetic uses the actual NYSE
   calendar (`pandas_market_calendars` or an exchange holiday file in the
   lake), not `freq='B'`. Off-by-one-holiday bugs move event studies.

## Universe and survivorship

A backtest universe assembled from *today's* index members or *today's*
liquid names is survivorship-biased. Build point-in-time universes from
historical constituent lists or from a liquidity rule computed on
trailing-only data. Delisted names stay in with their delisting returns.
If clean constituent history is unavailable, say so in the writeup and
bound the bias direction.

## Data cleaning with domain knowledge

Cleaning is not `dropna()`. Each fix must be justified by market mechanics:

- **Splits/dividends**: raw prices need adjustment factors; volume adjusts
  inversely to price on splits. Signals mixing adjusted prices with
  unadjusted volume are a classic silent bug.
- **Zero/low volume days**: halts and holidays, not "quiet days" — mask,
  don't interpolate.
- **Outliers**: winsorize cross-sectional features at 1%/99% *within each
  date* (never across the panel — that leaks the future's scale), but
  investigate before clipping: option-data "outliers" are often the trade.
- **Restatements**: XBRL company facts include multiple filings of the same
  concept-period; keep the *first* filing for point-in-time work and the
  latest for descriptive work — store both, tag which you used.
- **Corporate actions**: ticker changes and mergers break naive
  ticker-keyed joins; key on CIK for filings, FIGI/permno-style stable IDs
  where possible, and keep a manual alias table in the lake.

## Predictive modeling (RF / GBM / regression)

- **Validation is walk-forward, purged, and embargoed.** Expanding or
  rolling train window; test strictly later; purge overlapping-label rows
  (an h-day forward return label leaks h days across the split boundary);
  embargo a further gap for slow-moving features. `KFold(shuffle=True)` on
  time series is an automatic rejection.
- **Baselines first**: any GBM must beat (a) unconditional base rate,
  (b) regularized linear regression on the same features, (c) the single
  best feature alone — else the complexity bought nothing and the writeup
  says so.
- **Feature count vs sample size**: mid-frequency equity work has hundreds
  to thousands of effective observations, not millions. Dozens of features,
  strong regularization, monotonic constraints where domain knowledge gives
  the sign (e.g. crowding ↑ → squeeze magnitude ↑).
- **Evaluation**: rank-IC (Spearman of prediction vs outcome per date, then
  time-series mean and t-stat) for cross-sectional signals; MAPE +
  directional hit rate for level forecasts (revenue, EPS); calibration
  curves for probabilities. Sharpe of a toy portfolio comes last, and is
  reported with the **deflated Sharpe** adjustment for the number of things
  tried.
- **Multiple testing is the house edge against you.** Keep a lab notebook
  section in the analysis file: every variant tried, not just the winner.
  N tried variants ⇒ report the winner's stats alongside N.

## Event studies and causal analysis

The standard tool for "does X move Y" (insider cluster buys, SI spikes,
buyback announcements...):

1. Define the event with a point-in-time timestamp (publication, not
   effective).
2. Abnormal return = raw − beta×market (beta from trailing window ending
   *before* the event) over windows like [-20,+60].
3. **Matched controls**: for each event stock-date, sample non-event names
   matched on sector/size/momentum; report event minus control, not raw
   drift.
4. **Placebo test**: rerun with event dates shifted ±90 days; if the
   "effect" survives, it's a regime artifact, not the event.
5. **Confounder list in writing**: what else co-occurs (earnings proximity,
   index rebalance, macro prints)? Either exclude the window or dummy it.
6. Cluster standard errors by date (events cluster in crashes; iid t-stats
   flatter you).

"X preceded Y" is not a finding. "X preceded Y by k days, controls didn't,
placebos didn't, and the effect concentrates where the mechanism says it
should (small float, high SI)" is a finding.

## Deliverable standard

Every analysis lands as a reproducible script/notebook in
`/workspace/pipelines/analysis/` reading only from the lake, plus a short
writeup stating: data (lake paths + partitions), sample period, method,
point-in-time audit (one paragraph: how each join avoids lookahead),
results with uncertainty, the tried-variants count, and limitations. If a
result feeds a belief or decision, link it from `research/beliefs/` — and
the writeup's headline number must be recomputable by rerunning the script.
