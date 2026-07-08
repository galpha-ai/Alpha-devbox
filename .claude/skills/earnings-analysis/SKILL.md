---
name: earnings-analysis
description: Earnings-date-driven fundamental analysis — earnings calendars, EPS surprise history, estimate vs actual, call transcripts, guidance, options-implied move vs historical realized move, and post-earnings drift setups. Use for "who reports this week", "how does X trade around earnings", and pre/post-earnings deep dives.
---

# Earnings Data & Earnings-Date Analysis

Everything here is anchored to the **report date + timing (am/pm)**. Getting the timing wrong shifts every "reaction" measurement by a day — establish it first, from a verified source.

## 1. Discovery: who reports, when

```
# Market-wide window (≤ 31 days; negative days looks back)
mcp__robinhood_MCP__get_earnings_calendar {start_date: "2026-07-08", days: 7, filter: "high_market_cap"}

# One symbol: trailing 8 quarters, est/actual EPS, am/pm timing, verified flag
mcp__robinhood_MCP__get_earnings_results {symbol: "NVDA"}

# Date-range / longer history (FMP)
mcp__FMP__calendar {endpoint: "earnings-calendar", from_date: "2026-07-01", to_date: "2026-07-31"}
mcp__FMP__calendar {endpoint: "earnings-company", symbol: "NVDA"}
```

Trust rules: prefer entries with `verified: true`; unverified future dates move — re-check near the event. `pm` (after close) → market reaction is the **next** session; `am` (before open) → reaction is the **same** session.

## 2. Surprise history & estimates

- Surprise = `(eps_actual − eps_estimate) / |eps_estimate|` per quarter from the 8-quarter history; note beat/miss streaks and whether the estimate was rising or falling into the print (`mcp__FMP__analyst {endpoint: "financial-estimates", symbol, period: "quarter"}`).
- Revenue matters as much as EPS: pull the reported quarter via `mcp__FMP__statements {endpoint: "income-statement", period: "quarter", limit: 8}` and compare to revenue estimates.
- Analyst reaction after the print: `mcp__FMP__analyst {endpoint: "grades", symbol}` (upgrades/downgrades) and `price-target-consensus`.

## 3. The report itself (fundamental deep dive)

For a just-reported quarter:

1. **Press release / 8-K**: `mcp__FMP__news {endpoint: "search-press-releases", symbols: ["NVDA"]}` and `mcp__FMP__secFilings {endpoint: "search-by-symbol", symbol: "NVDA"}` — the 8-K carries guidance; guidance moves stocks more than the beat/miss itself.
2. **Transcript** (FMP Ultimate plan): `mcp__FMP__earningsTranscript {endpoint: "search-transcripts", symbol: "NVDA", year: 2026, quarter: 2}`; if plan-gated, fall back to the press release + news. Read for: guidance language, margin commentary, one-time items, Q&A evasiveness.
3. **Statement quality**: run the reported quarter through the **sec-filing-fundamentals** red-flag checklist (cash flow vs earnings, receivables, inventory) — a "beat" with deteriorating quality is a different trade than a clean beat.

## 4. Options angle: implied vs realized move

**Implied move** (what the market prices for the event):

```
1. mcp__robinhood_MCP__get_option_chains {underlying_symbol: "NVDA"}     → pick first expiry AFTER the report date
2. mcp__robinhood_MCP__get_option_instruments {chain_symbol: "NVDA", expiration_dates: "<expiry>"}  → ATM call + put (strike nearest spot)
3. mcp__robinhood_MCP__get_option_quotes {instrument_ids: [call_id, put_id]}

implied_move = (call_mid + put_mid) / spot        # straddle mid ÷ spot
```

**Realized move** (what actually happens): for each past report date, compute the close→next-open gap and close→close move from daily bars (**equity-options-data** store). Compare:

| Quarter | Surprise | Implied move (pre) | Realized gap | Straddle PnL |
| --- | ---: | ---: | ---: | ---: |

- Realized consistently < implied → the name systematically overprices earnings (short-premium candidate); the reverse → long-premium candidate. 8 quarters is a small sample — say so.
- **IV crush**: front-expiry IV collapses after the print. Long straddles must overcome crush + spread; verify with actual expired-contract prices (`get_option_instruments {state: "expired"}` → `get_option_historicals`), not model prices.

## 5. Post-earnings drift & event backtests

To turn any of the above into a tested strategy (drift after big surprises, straddle buy/sell, gap fade), use the **equity-options-backtest** skill's event-driven template — it encodes the am/pm entry-timing rule, expanding-window surprise buckets, and the two option-pricing regimes. Store the event table first:

```
~/.equityquant/data/earnings/symbol=NVDA/earnings.parquet
(symbol, report_date, timing, eps_estimate, eps_actual, verified)
```

## Output format

Per **quant-data-science** conventions: one headline ("NVDA reports 8/27 pm; market implies ±7.2%, average realized ±9.1%"), ONE compact numeric table (quarters × surprise/implied/realized), bullets for guidance and statement-quality notes with filing citations, one-sentence bottom line. Flag small sample sizes and unverified dates. This is analysis, not investment advice — say so when the user is deciding a trade.
