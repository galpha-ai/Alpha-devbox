---
name: inv-short-interest
description: Short interest and short-flow analysis — use for questions about how shorted a stock is, days-to-cover, short interest changes, daily short volume ratio, borrow cost pressure, or screening for short squeeze setups. Covers FINRA consolidated short interest (biweekly) and Reg SHO daily short volume, their very different meanings, point-in-time publication lags, and how shorts interact with crowding and options positioning.
---

# Short Interest & Short Flow

Persona: mid-frequency researcher. Two datasets that sound alike and mean
different things — most retail-grade shorting analysis dies by conflating
them.

## Dataset 1: FINRA consolidated short interest (the position)

Actual open short positions per security, reported by broker-dealers as of
**two settlement dates per month** (mid-month and month-end), published
~7 business days later.

- Endpoint: FINRA Query API `consolidatedShortInterest` (registry in
  `inv-data-pipeline`); store to `finra/short_interest/dt=<pub date>/`.
- **Point-in-time**: the market learns the mid-June number in late June.
  Join on publication date. Between publications you are blind at the
  position level — that blindness is why Dataset 2 exists.
- Core metrics:
  - **SI % float** (get float right: shares outstanding minus insider +
    strategic holdings from the latest 10-Q/proxy; free-float vendors
    disagree — record which definition you used).
  - **Days-to-cover (DTC)** = SI / 30-day ADV. The squeeze-relevant
    quantity: %float says how wrong shorts are, DTC says how *trapped*.
  - **ΔSI** between reports, and SI percentile vs the stock's own 3-year
    history and vs sector.

## Dataset 2: Reg SHO daily short volume (the flow-ish proxy)

Daily per-ticker short *volume* from `cdn.finra.org/equity/regsho/daily/
CNMSshvol{YYYYMMDD}.txt` (pipe-delimited, free, no auth).

**The trap**: a large fraction of reported short volume is market-maker
liquidity provision (they short to fill your buy). The *level* of short
volume ratio (SVR = short vol / total vol, typically ~40-50%) is nearly
meaningless. Use only **changes and extremes**: SVR z-score vs the stock's
own trailing 60-day distribution, sustained multi-day drifts, and
divergences (SVR falling while price falls = shorts covering into
weakness, often pre-squeeze; SVR spiking on rallies = shorts pressing).

Daily SVR + biweekly SI triangulate: SI tells position, SVR hints at the
direction of change between SI prints. Verify the triangulation whenever a
new SI print lands — record hit/miss in the monitor log; if your SVR read
keeps mis-predicting ΔSI for a name, stop using it there.

## Borrow cost (the missing free variable)

Real borrow rates (the third leg: %float=wrongness, DTC=trapped-ness,
borrow=bleeding) have no good free source. Proxies, in order: hard-to-borrow
signatures in options (put-call parity violations — deep ITM call prices
imply the borrow; compute from the CBOE chain via `inv-options-pressure`),
scraping IBKR-based public trackers where accessible. When borrow is
unknown, say so — don't silently assume GC.

## Squeeze setup screen

A short squeeze needs fuel, trigger, and trap. Screen on:

1. **Fuel**: SI % float > ~15% (or top decile vs own history), DTC > ~5.
2. **Trap**: float small; HF crowding on the *long* side low-to-moderate
   (crowded-long + crowded-short names squeeze less — longs supply stock
   into the rip; cross-check `inv-13f-positioning`).
3. **Trigger proximity**: scheduled catalyst inside the horizon (earnings,
   guidance, SI publication itself) — from the calendar in
   `inv-revenue-projection` monitors.
4. **Accelerant**: options-side gamma squeeze conditions (call OI stacked
   just OTM, dealers short gamma — from `inv-options-pressure`); implied
   borrow rising.
5. **Tape confirmation**: absorption pattern on down moves
   (`inv-flow-tape`), SVR falling into weakness.

Score candidates on all five; a name with fuel but no trigger is a watch,
not a trade. Squeeze longs are **rentals with an exit plan** — the same SI
that squeezes a stock up mean-reverts it after; define the exit at entry in
`decisions/journal.md`.

The mirror screen (crowded long + deteriorating fundamentals + insiders
selling) flags **air-pocket shorts/avoids**; same mechanics, opposite sign.

## Interpretation discipline

High SI is not a buy or sell signal by itself: shorts are often right
(they do more work per position than longs). The research question is
always *why* the short book exists — read the bear case (borrow the best
short-seller argument you can construct from filings via
`inv-revenue-projection` driver tree) before betting against it. Record
which leg (fuel/trigger/trap) your thesis actually disputes.

## Monitors

Per `inv-data-pipeline`: daily Reg SHO pull + SVR z-score alert (>2σ,
3-day drift) on watched names; SI publication-day diff alert (ΔSI > 20% or
decile jump); implied-borrow spike alert from the options skill. All append
to `research/events/log.md`.
