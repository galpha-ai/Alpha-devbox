---
name: inv-buybacks
description: Buyback announcement and execution tracking — use for questions about share repurchase programs, buyback authorizations vs actual execution pace, accelerated share repurchases (ASR), net share count shrinkage, or the buyback blackout calendar's effect on flow. Covers EDGAR full-text hunting for announcements, the 10-Q issuer-purchases table, XBRL cash-flow cross-checks, and separating signal from IR theater.
---

# Buybacks: Authorization vs Execution

Persona: mid-frequency researcher. The single most important idea:
**an authorization is a press release; execution is a flow.** Most buyback
"analysis" stops at the announcement, which is exactly where the
information isn't.

## The three data layers

1. **Announcements** (authorization): 8-K filings and press releases.
   Hunt via EDGAR full-text search
   (`efts.sec.gov/LATEST/search-index?q="share repurchase program"&forms=8-K`,
   registry in `inv-data-pipeline`) plus watched-CIK 8-K polls. Capture:
   size ($ and % of market cap), new vs upsize vs refresh of an exhausted
   program, expiry, and whether an **ASR** (accelerated share repurchase —
   an upfront commitment executed by a dealer, i.e. guaranteed near-term
   flow) is included.
2. **Execution detail**: the 10-Q/10-K "Issuer Purchases of Equity
   Securities" table — **monthly** shares repurchased, average price paid,
   and remaining authorization. This is the ground truth of pace and
   price-sensitivity, disclosed quarterly. Parse it from the filing (it's a
   standard table near Part II Item 2) into `sec/buyback_exec/`.
3. **Cash-flow cross-check**: XBRL `PaymentsForRepurchaseOfCommonStock`
   (companyfacts API) quarterly, and **diluted share count trajectory**
   (`WeightedAverageNumberOfDilutedSharesOutstanding`) — the only number
   shareholders actually keep. Buybacks that merely mop up SBC dilution
   shrink nothing; compute **net shrink** = buyback $ minus SBC issuance
   effect, visible as ΔdilutedShares.

## Signal design

- **Execution pace ratio** = trailing-quarter repurchase $ / (remaining
  authorization / quarters to expiry). Pace ≫ 1 with price weakness =
  management conviction with money. Pace ≈ 0 on a big announcement =
  theater; flag it.
- **Price sensitivity**: from the monthly table, regress monthly avg price
  paid vs monthly VWAP — some companies systematically buy dips (real
  bid-under-the-stock), others buy blindly (10b5-1 corporate plans).
  Dip-buyers create a soft floor worth knowing about in `inv-flow-tape`
  terms.
- **Authorization % of float / of ADV**: a $2B program on a $200B mega-cap
  is rounding; the same on a 5-DTC mid-cap is a structural bid. Express
  programs in **days of ADV**.
- **Combo signals**: buyback upsizing + insider P-buys
  (`inv-insider-transactions`) is one of the cleanest bullish
  configurations; buyback exhaustion + insider selling is the mirror.
- **ASR** = guaranteed flow now (dealer shorts to deliver, buys back over
  the term — mildly gamma-like), and a management statement that the stock
  is cheap *today*, not "over time".

## The blackout calendar (flow structure)

Companies pause discretionary buybacks in the ~5 weeks before earnings
(10b5-1 corporate plans continue). For heavy-buyback names, the corporate
bid disappearing pre-earnings and returning after is a real, recurring flow
pattern — mark the windows in the flow context (`inv-flow-tape`) and don't
misread the pre-earnings drift as distribution. Aggregate blackout windows
across the market also modulate index-level flow into earnings seasons.

## Interpretation traps

- Announcements are unbounded promises: "up to $X over no particular
  timeframe" with no obligation. Never model an authorization as flow.
- Buybacks at cycle peaks destroy value with shareholder applause — pace
  is bullish *conditioning on* the driver tree saying value > price
  (`inv-revenue-projection`); the buyback itself doesn't make the equity
  cheap.
- Watch leverage-funded buybacks into deteriorating FCF (a common terminal
  behavior); the balance-sheet check is one DuckDB query away.
- Point-in-time: announcement = 8-K timestamp; execution detail =
  10-Q filing date (a quarter stale); shrink = observable only at print.

## Monitors

Per `inv-data-pipeline`: 8-K/full-text poll for new authorizations on
watched names (and market-wide weekly sweep for ≥5%-of-mktcap programs —
new-idea funnel); per-print execution-pace update with alert on pace
regime change; blackout-window calendar maintained per watched name.
Alerts append to `research/events/log.md`.
