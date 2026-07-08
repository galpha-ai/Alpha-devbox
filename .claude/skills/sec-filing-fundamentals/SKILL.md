---
name: sec-filing-fundamentals
description: Fundamental analysis of US-listed companies grounded in SEC filings — 10-K/10-Q/8-K discovery, financial statements (standard and as-reported), ratios, DCF valuation, insider trades, 13F ownership, and an accounting red-flag checklist. Use for "is this company financially healthy / cheap / deteriorating" questions.
---

# SEC Filing Fundamental Analysis

Ground fundamental claims in filings and statements pulled via the FMP MCP tools — not in memory. Every number in the final answer should be traceable to a tool call or a filing document.

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

Follow **quant-data-science** presentation conventions: headline verdict → key numbers in ONE compact GFM table (metric rows vs 3–5 periods, or company vs peers) → red flags found (or "none") → valuation band vs current price → one-sentence bottom line. Cite the filing (form + date) for any claim that came from reading a document rather than a statements endpoint. State clearly that this is analysis, not investment advice, when the user is making an investment decision.

For earnings-event-specific analysis (surprise history, implied move, transcripts) use the **earnings-analysis** skill.
