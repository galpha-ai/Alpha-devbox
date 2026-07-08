---
name: inv-options-pressure
description: Options positioning and market-pressure analysis — use for questions about option flow, open interest distribution, put/call ratios, implied probability distributions for a stock (e.g. SanDisk, Micron), implied earnings moves, dealer gamma exposure (GEX), max pain, implied borrow, and screening for gamma squeeze / short squeeze candidates. Covers building an OI history from daily CBOE chain snapshots and inferring flow without paid trade-level data.
---

# Options Pressure: OI, Flow, and the Implied Distribution

Persona: mid-frequency researcher. The options market is the only place
where the market's *entire probability distribution* for a stock is posted
publicly every day — most people just never deconvolve it. This skill turns
one free endpoint into: implied distributions, positioning pressure maps,
and squeeze screens.

## Data: build your own history

- **Source**: `cdn.cboe.com/api/global/delayed_quotes/options/{TICKER}.json`
  (registry in `inv-data-pipeline`) — full chain: bid/ask, last, volume,
  **open interest**, IV, delta/gamma/theta/vega per contract. 15-min
  delayed, free, no auth.
- **The catch**: it's a snapshot. **OI history does not exist for free —
  you must snapshot daily and diff.** OI updates once daily (previous
  day's settlement, posted next morning). So: snapshot after each close to
  `cboe/chain_{TICKER}/dt=<date>/`; today's file carries *yesterday's* OI
  — label `oi_asof` accordingly (point-in-time discipline).
- Same-day volume is in the snapshot; OI change arrives next morning. The
  pair (today's volume, tomorrow's ΔOI) is what lets you infer opening vs
  closing flow.
- MCP fallback (Robinhood chains/quotes, FMP) for interactive lookups;
  snapshot into the lake when it feeds a conclusion.

## Layer 1: pressure ratios (cheap, daily)

- **P/C OI ratio** and **P/C volume ratio** — level vs the stock's own
  1-year percentile (cross-stock comparison is meaningless; some names
  live at 0.3, others at 1.5). Volume ratio = today's mood; OI ratio =
  accumulated positioning. Divergence (put *volume* spiking while put OI
  flat) = day-trading noise, not new positioning.
- **OI distribution by strike/expiry**: where is the wall? Strike-level OI
  concentration near spot pins price into expiration (dealer hedging
  gravitates spot toward big-OI strikes — "max pain" is the caricature;
  the mechanism is dealer gamma, below).
- **IV term structure & skew**: front-expiry IV bump = event premium
  (extract the implied event move below); 25-delta put-call skew richening
  = downside insurance bid; skew *inverting* (calls over puts) is the
  classic pre-squeeze fingerprint.

## Layer 2: the implied distribution (the crown jewel)

Breeden–Litzenberger: the risk-neutral density is the second derivative of
call price w.r.t. strike, `q(K) = e^{rT} ∂²C/∂K²`. Practical recipe (script
in `/workspace/pipelines/analysis/`):

1. Use **OTM options only** (OTM calls above forward, OTM puts below —
   liquidity + smaller American-exercise bias), mid prices, one expiry.
2. Compute forward F from put-call parity at the strike where |C−P| is
   smallest (this also backs out **implied borrow/dividend** — a
   persistently depressed forward vs fair carry = hard-to-borrow;
   feed `inv-short-interest`).
3. Fit a smooth IV curve in delta or log-moneyness space (SVI or cubic
   spline with convexity constraints); reprice; differentiate the *fitted*
   price curve numerically. Never finite-difference raw quotes.
4. Sanity: density ≥ 0, integrates to ~1, mean ≈ F. Then read off:
   P(S_T > x), P(S_T < x), tail masses, distribution vs your scenario
   table from the decision layer. **Where your scenario probabilities
   disagree with q(K) is precisely your bet** — quote both in the journal
   entry. (q is risk-neutral: tails are bid vs real-world; fine for
   *relative* and *time-series* comparison, footnote it.)
- **Implied earnings move**: front ATM straddle / spot, term-structure
  cleaned (strip the post-event expiry's baseline IV using a later expiry:
  event variance = T₁σ₁² − T₂-implied baseline). Compare vs the stock's
  realized post-print moves (8-quarter history) — rich/cheap event vol is
  its own trade and also *the market's uncertainty estimate* for the
  whisper analysis in `inv-revenue-projection`.

## Layer 3: dealer gamma (GEX) and squeeze mechanics

- **GEX per strike** ≈ Σ gamma × OI × 100 × S² × 0.01, signed by the
  dealer-positioning assumption (baseline: dealers long calls customers
  sold? No — **standard naive convention: dealers short customer-bought
  calls? Use: dealers long gamma on calls they're short? State it.**).
  Convention to use and label: customers net *buy* calls and *buy* puts →
  dealers are short calls (short gamma above spot) and short puts (short
  gamma below? no — long). Because the true customer direction is
  unobservable in free data, compute GEX under the standard assumption
  (calls dealer-short, puts dealer-long is *not* standard; the common
  published convention is calls dealer-long, puts dealer-short) — **pick
  the OI-change-informed sign when you have it** (Layer 1 diffs: OI that
  grew on days volume traded near the ask = customer buying) and always
  report GEX as "under assumption X".
- **Zero-gamma level**: spot above it → dealer hedging dampens moves
  (sell rips, buy dips); below → hedging *amplifies* (sell dips). Regime
  variable for `inv-flow-tape` signal interpretation.
- **Gamma squeeze screen**: call OI stacked just OTM in near expiries +
  OI growing via ask-side volume + small float + dealer short-gamma sign
  + (optional but explosive) high SI/DTC from `inv-short-interest`. Rank
  by (near-OTM call gamma notional / float ADV $). The same screen with
  puts flags crash-accelerant names.
- Cross-check any squeeze candidate against the fuel/trigger/trap
  checklist in `inv-short-interest`; options are the accelerant, not the
  fuel.

## Flow inference without paid prints

Free data has no trade-side tags. Triangulate: (a) ΔOI vs volume —
volume ≫ ΔOI = closing/day-trading; ΔOI ≈ volume = fresh positioning;
(b) where the day's VWAP of the contract sat in its bid-ask range
(approximate with snapshot mid drift); (c) IV rising with ΔOI = net
buying pressure, IV falling with ΔOI = net selling (overwriting).
Label conclusions as inference, with the triangulation shown.

## Traps

- OI is T+1: never compute "OI reaction" to an event using same-day file.
- Deep-ITM and sub-$0.10 quotes are garbage — filter by spread% and delta.
- Splits/specials change multipliers and strike grids — the alias table.
- Weekly-expiry proliferation double-counts rolled positions in "OI
  growth" — dedupe by aggregating in delta/tenor buckets, not raw strikes.

## Monitors

Daily post-close snapshot on watched tickers, then: P/C percentile alerts,
OI-wall migration alert (wall strike moves), GEX sign flip alert, implied
borrow alert → `inv-short-interest`, event-premium tracker into earnings
(feeds `inv-revenue-projection`). Weekly market-wide gamma-squeeze screen
as a new-idea funnel. All append to `research/events/log.md`.
