---
name: inv-flow-tape
description: Market flow and tape reading from bar data — use for questions about whether large funds are accumulating or distributing a stock, volume signals, VWAP footprints, absorption/capitulation patterns, "show color" on who is active, and integrating technical analysis with flow evidence. Covers institutional execution footprints in minute/daily bars and regime-aware TA.
---

# Flow & Tape: Institutional Footprints in Bar Data

Persona: mid-frequency researcher. Free data has no counterparty tags — but
institutional execution leaves *mechanical* footprints in bars, because
parent orders are sliced by the same execution algos everywhere. Read the
footprints, not the candles' mood.

## Data

Minute and daily bars for watched names + their peer group (bars via MCP
quote/historicals tools or stooq/yfinance fallback, snapshotted to
`bars/{ticker}/` per `inv-data-pipeline`). Everything below is computable
with close, high, low, volume — by design, so the whole layer runs on free
data.

## The footprint library (what execution mechanics look like)

- **Parent-order accumulation** (a large long-only buying over days/weeks):
  elevated but *smooth* volume (z = 1–2, not spikes), positive
  close-location-value bias (closes in upper half of range), shallow
  pullbacks on low volume, price grinding along VWAP from above.
  Confirm later against N-PORT/13F adds (`inv-13f-positioning`) — every
  confirmed match calibrates your detector; log hits/misses in the monitor.
- **Distribution**: the mirror — rallies stall on volume, closes in lower
  range half, heavy prints into strength.
- **Capitulation → absorption** (the "large fund starts catching the
  knife" pattern, the strongest bottoming tell): high-volume flush (volume
  z > 3, wide range, close near low) followed within days by
  *equal-or-higher volume with no further price progress downward* —
  someone is absorbing everything sold. Quantify: rolling 5-day
  volume-at-loss vs price-progress ratio.
- **Block prints**: minute bars with volume z > 4 and range ≪ volume-implied
  range = negotiated crosses; cluster of them at one price level = an
  institution with a target price, i.e. "color".
- **Squeeze fuel burning**: gap-and-fade on huge volume repeatedly = supply
  overwhelming the squeeze (cross `inv-short-interest`).

## Signals (compute per `inv-quant-foundations` discipline)

Daily per stock: volume z-score (60d), up/down volume ratio, OBV slope,
Amihud illiquidity trend, close-location-value (20d mean), VWAP deviation
persistence, 5-day absorption score, block-print count. Store as a feature
frame in the lake — these feed both monitors and any predictive model.

## Regime awareness (where naive TA dies)

Interpret every footprint conditional on:

1. **Dealer gamma regime** (`inv-options-pressure` zero-gamma level):
   long-gamma tape mean-reverts (fade breakouts), short-gamma tape trends
   (respect breakouts). The same volume pattern means opposite things.
2. **Buyback blackout calendar** (`inv-buybacks`): corporate bid on/off
   changes baseline down-day absorption.
3. **Index events**: rebalances, option expiries (OpEx pinning then
   un-pinning), month/quarter-end — mark the calendar, exclude from event
   studies, expect flow without information.
4. **Volatility regime**: realized vol tercile; z-scores are computed
   within-regime or they mostly measure the regime.

Classical TA (RSI, MACD, moving averages) enters only as *features with a
prior*, never as standalone signals: trend-following primitives work in
short-gamma/trending regimes, mean-reversion primitives in long-gamma
ranges. A TA claim in a writeup must carry its regime qualifier.

## "Show color" workflow

When the decision layer asks "who is active in X this week":

1. Footprint scan (library above) over the last 20 sessions.
2. Cross-reference the positioning cube: Form 4 (2-day lag), 13D/G, SVR
   drift, OI migration — which holder class *could* it be.
3. Peer-relative check: is the flow stock-specific or sector-wide
   (footprints on the whole peer basket = macro/sector flow, not color).
4. Output: "consistent with <holder class> <accumulating/distributing>
   because <footprints> + <cube corroboration>; alternatives: <...>" —
   color is stated as a hypothesis with corroboration, never as fact.

## Monitors

Daily post-close footprint scan on watched names; absorption-score and
block-cluster alerts; OpEx/rebalance calendar pre-alerts. Append to
`research/events/log.md`.
