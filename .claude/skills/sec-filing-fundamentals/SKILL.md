---
name: sec-filing-fundamentals
description: Fundamental analysis of US-listed companies grounded in SEC filings — 10-K/10-Q/8-K discovery, financial statements (standard and as-reported), ratios, DCF valuation, insider trades, 13F ownership, and an accounting red-flag checklist. Use for "is this company financially healthy / cheap / deteriorating" questions.
---

# SEC Filing Fundamental Analysis

Ground fundamental claims in filings and statements pulled via the FMP MCP tools — not in memory. Every number in the final answer should be traceable to a tool call or a filing document.

## Analysis discipline (non-negotiable)

These rules bind every step below. Violating them produces confident-sounding but wrong research.

1. **Decompose the mechanism before concluding.** Aggregates hide the answer: split multi-segment companies into segments, split a ratio into its numerator and denominator, split a cross-metric into its legs. The default chain for any operating business is `volume / ASP → revenue → margin → profit → multiple → implied value` — build it in that order so every link is checkable. When two data points appear to contradict each other (revenue up, cash down; stock up, estimates down), find the mechanical reconciliation (definition, timing, denominator, mix) BEFORE reaching for a narrative or outside macro explanation.
2. **Tag every number: `[filed]` / `[derived]` / `[assumed]`.** `[filed]` = read from a statement endpoint or filing; `[derived]` = arithmetic on filed numbers (show the arithmetic); `[assumed]` = a model input you chose (state the basis). When the data doesn't contain a number you need (segment ASP, unit economics), SAY SO and bound it — never fill a gap with an invented specific value, and never promote an `[assumed]` number to fact in the conclusion. An honest "not disclosed; bounded between X and Y because …" scores over a fabricated point estimate.
3. **口径 (basis) consistency.** State the basis of every ratio and never mix them: TTM vs FY vs annualized-quarter denominators; diluted vs basic share count; gross margin is not operating margin is not unit net profit; a regional gross margin cannot stand in for a regional per-unit net profit; GAAP vs non-GAAP EPS. If two sources disagree, reconcile the basis before averaging or choosing.
4. **Anchor on market-implied expectations.** "Cheap/expensive" is meaningless without a reference: reverse out what the current market cap implies (which year's earnings at what multiple, what growth) against `[filed]` history and analyst estimates, then state where the actual disagreement with the market lies. That disagreement — not the multiple itself — is the thesis.
5. **Time discipline in retrospectives.** When explaining a past period, use only information available then: filing dates gate what was knowable; explain past price action with then-current market cap / PE / earnings, not with technology, capacity, or demand facts disclosed years later. If a claim needs later data, label it hindsight explicitly.

## Workflow

### 1. Identity & context

```
mcp__FMP__company {endpoint: "profile-symbol", symbol: "AAPL"}     # sector, CIK, description
mcp__FMP__company {endpoint: "peers", symbol: "AAPL"}              # comparison set
mcp__FMP__secFilings {endpoint: "sec-company-full-profile", symbol: "AAPL"}
```

### 2. Filing discovery

```
mcp__FMP__secFilings {endpoint: "search-by-symbol", symbol: "AAPL", from_date: "2025-01-01", to_date: "2026-07-01"}
mcp__FMP__secFilings {endpoint: "search-by-form-type", formType: "10-K", from_date: ..., to_date: ...}
mcp__FMP__secFilings {endpoint: "8k-latest"}                       # material events market-wide
```

Results include EDGAR links — `WebFetch` the filing URL to read MD&A, risk factors, and footnotes directly. Form cheat-sheet: **10-K** annual, **10-Q** quarterly, **8-K** material events (departures, M&A, guidance; **Item 4.02** = non-reliance on prior financials — serious), **S-1** IPO, **DEF 14A** proxy/compensation, **4** insider transactions, **13F** institutional holdings.

### 3. Financial statements (the core)

```
mcp__FMP__statements {endpoint: "income-statement", symbol: "AAPL", period: "annual", limit: 5}
mcp__FMP__statements {endpoint: "balance-sheet-statement", symbol: "AAPL", period: "quarter", limit: 8}
mcp__FMP__statements {endpoint: "cashflow-statement", symbol: "AAPL", period: "annual", limit: 5}
mcp__FMP__statements {endpoint: "key-metrics-ttm", symbol: "AAPL"}      # per-share, ROIC, yields
mcp__FMP__statements {endpoint: "metrics-ratios-ttm", symbol: "AAPL"}   # margins, turnover, leverage
mcp__FMP__statements {endpoint: "financial-scores", symbol: "AAPL"}     # Altman Z, Piotroski
mcp__FMP__statements {endpoint: "financial-statement-growth", symbol: "AAPL", period: "annual"}
mcp__FMP__statements {endpoint: "owner-earnings", symbol: "AAPL"}
mcp__FMP__statements {endpoint: "revenue-product-segmentation", symbol: "AAPL"}
mcp__FMP__statements {endpoint: "revenue-geographic-segments", symbol: "AAPL"}
```

Use `as-reported-*` endpoints when the standardized view hides something (unusual line items, restatements); use `income-statements-ttm` / `balance-sheet-statements-ttm` for valuation denominators.

### 4. Valuation

```
mcp__FMP__statements {endpoint: "enterprise-values", symbol: "AAPL"}
mcp__FMP__discountedCashFlow {endpoint: "dcf-advanced", symbol: "AAPL"}
mcp__FMP__discountedCashFlow {endpoint: "dcf-levered", symbol: "AAPL"}
# Sensitivity: override assumptions explicitly
mcp__FMP__discountedCashFlow {endpoint: "custom-dcf-advanced", symbol: "AAPL",
  revenueGrowthPct: "0.06", longTermGrowthRate: "0.025", taxRate: "0.21", beta: "1.2"}
```

Always run DCF as a sensitivity band (bear/base/bull growth + WACC), never a single point. Cross-check against multiples vs peers (`key-metrics-ttm` P/E, EV/EBITDA, FCF yield across the peer list from step 1).

**Segment / SOTP valuation** — mandatory for multi-segment companies; a blended multiple on a conglomerate is a basis error:

1. Per-segment revenue from `revenue-product-segmentation` / `revenue-geographic-segments` `[filed]`; segment margins from the 10-K segment footnote (`as-reported-*` endpoints or WebFetch the filing) — if a segment margin is not disclosed, bound it from peer pure-plays and tag `[assumed]`.
2. Build each segment's chain independently: `volume/ASP → revenue → segment profit → segment-appropriate multiple → segment EV`. Different businesses in one company get different multiples.
3. Sum segment EVs, subtract net debt (`enterprise-values`), adjust minorities → SOTP equity value.
4. Close the loop against the market: current market cap vs SOTP and vs estimate-implied earnings — state which year's profit the market is already pricing and what the residual disagreement is (that's the actionable conclusion, not the SOTP number itself).

**Scenario/sensitivity output**: for multi-variable questions (price recovery × mix shift × share gain), build ONE unified framework across all entities being compared, list every assumption in a table with its tag and source, and rank the sensitivities (which variable moves EPS most per unit of change) before giving per-scenario EPS/PE ranges.

### 5. Corroborating signals

```
mcp__FMP__insiderTrades {endpoint: "search-insider-trades", symbol: "AAPL"}   # Form 4 buys/sells
mcp__FMP__insiderTrades {endpoint: "insider-trade-statistics", symbol: "AAPL"}
mcp__FMP__form13F {endpoint: "positions-summary", symbol: "AAPL", year: 2026, quarter: 1}  # Ultimate plan
mcp__FMP__analyst {endpoint: "financial-estimates", symbol: "AAPL", period: "annual"}
mcp__FMP__analyst {endpoint: "price-target-consensus", symbol: "AAPL"}
mcp__FMP__news {endpoint: "search-press-releases", symbols: ["AAPL"]}
```

Insider selling is weak signal (10b5-1 plans); clustered open-market **buys** are strong. 13F is 45 days stale — treat as position, not timing.

## Accounting red-flag checklist

Run through these against the 5-year statement history; flag any hit in the output:

| Flag | Test |
|---|---|
| Earnings/cash divergence | Net income growing while operating cash flow flat/falling over 2+ years |
| Receivables outrunning revenue | DSO trending up ≥ 20% over 2 years (channel stuffing) |
| Inventory build | Inventory growth ≫ revenue growth |
| Serial "one-time" items | Restructuring/impairment charges in ≥ 3 consecutive years |
| Goodwill-heavy balance sheet | Goodwill+intangibles > 50% of assets after acquisitions |
| Dilution treadmill | Share count rising > 3%/yr while touting "record EPS" |
| Leverage cliff | Debt/EBITDA > 4× or large maturities inside 24 months (check 10-K debt footnote) |
| Auditor/reporting events | 8-K Item 4.01 (auditor change) or 4.02 (non-reliance), late filings |
| Score deterioration | Altman Z < 1.8, Piotroski ≤ 3 (`financial-scores`) |

## Output format

Follow **quant-data-science** presentation conventions: headline verdict → key numbers in ONE compact GFM table (metric rows vs 3–5 periods, or company vs peers) → red flags found (or "none") → valuation band vs current price and the market-implied expectation it disagrees with → one-sentence bottom line. Carry the `[filed]/[derived]/[assumed]` tags into the assumptions table so the reader can re-derive every conclusion; list data gaps explicitly rather than papering over them. Cite the filing (form + date) for any claim that came from reading a document rather than a statements endpoint. State clearly that this is analysis, not investment advice, when the user is making an investment decision.

For earnings-event-specific analysis (surprise history, implied move, transcripts) use the **earnings-analysis** skill.
