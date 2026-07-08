---
name: inv-insider-transactions
description: Insider transaction analysis from SEC Form 4/5 — use for questions about insider buying or selling, CEO/CFO trades, cluster buys, whether an insider sale is mechanical (10b5-1, tax, option exercise) or informative, and building insider-signal monitors. Covers EDGAR Form 4 XML parsing, transaction-code cleaning, the signal hierarchy, and event-study validation.
---

# Insider Transactions (Form 4/5)

Persona: mid-frequency researcher. The fastest filing in the positioning
cube (≤2 business days) and the one where **cleaning IS the alpha** — raw
insider "selling" is mostly noise; the signal lives in a small, well-defined
subset.

## Download

- **Incremental**: poll `data.sec.gov/submissions/CIK{...}.json` for
  watched issuer CIKs, filter form type 4, fetch the `ownershipDocument`
  XML from the archives. Store parsed rows to `sec/form4/dt=<filing date>/`.
- **Backfill**: DERA "Insider Transactions data sets" quarterly TSVs.
- MCP fallback: FMP `insiderTrades` for interactive questions — snapshot to
  lake if used in a conclusion.

Parse per transaction: insider name, role (officer/director/10% owner —
`isOfficer` + `officerTitle`; CEO/CFO from title string), transaction code,
shares, price, post-transaction holdings, the **10b5-1 checkbox** (mandatory
flag since 2023), and the footnotes (real information hides in footnotes:
trust transfers, prepaid variable forwards, pledges).

## Cleaning: the transaction-code hierarchy

| Code | Meaning | Signal value |
|---|---|---|
| **P** | open-market purchase | THE signal — insiders buy for one reason |
| **S** | open-market sale | conditional (see below) |
| M | option exercise | not a signal alone |
| M+S same day | exercise-and-sell | compensation cash-out, discard |
| F | shares withheld for tax | mechanical, discard |
| A | award/grant | comp, discard |
| G | gift | usually discard (watch year-end tax gifting) |
| C, J, ... | conversions/other | read footnotes case by case |

**Sales filter** (in order): drop 10b5-1-flagged; drop same-day M+S; drop
sales < ~10% of the insider's post-transaction holdings (diversification
trickle); what survives — **discretionary, large-fraction-of-stake sales,
especially CEO/CFO, especially first sale after a long gap, especially
several insiders in the same window** — is the informative subset. A CFO
discretionarily selling 40% of their stake three weeks before earnings is
a different object than "insider selling" headlines.

## The signal hierarchy (validated regularities to re-verify, not assume)

1. **Cluster buys**: ≥3 distinct insiders open-market buying within ~30
   days. Historically the strongest positive configuration; validate on
   your own event study before trusting (method: `inv-quant-foundations`,
   matched controls, publication-date timestamps).
2. **CEO/CFO open-market buys, sized** ≥ meaningful vs their annual comp
   (comp from the proxy statement; a $50k buy from a $20M/yr CEO is PR).
3. **Buy after price break**: P-buys within weeks of a >30% drawdown —
   the insider disagrees with the market's re-rating.
4. **Informative sales** (post-filter) — bearish conditioner; combine with
   crowding (`inv-13f-positioning`) and the driver tree's fragile
   assumptions (`inv-revenue-projection`).
5. Officer buys > director buys > 10%-owner adds (information proximity).

Aggregate metrics per stock: net discretionary insider flow (6m, $),
buy/sell count ratio vs the company's own 5-year baseline (some companies
culturally never buy — baseline-relative only), and days-since-last-P-buy.

## Point-in-time and interpretation traps

- Timestamp = **filing datetime** (acceptance timestamp), not transaction
  date; the market reacts at filing.
- Insiders are early: buys front-run fundamentals by quarters, not days.
  Wrong horizon = "signal doesn't work". Test at 60-250 trading days.
- Sector waves (energy insiders all buy at cycle bottoms) — cluster your
  event-study errors by date.
- Blackout windows: insiders mostly can't trade in the ~5 weeks before
  earnings; an absence of buying pre-earnings is structure, not signal.
  Conversely a P-buy in an *open* window right after a selloff is clean.
- 10b5-1 plans can be adopted/canceled informatively — plan adoption
  disclosures (8-K/proxy) after big run-ups are themselves a mild bearish
  tell. Footnote-read when it matters.

## Monitors

Per `inv-data-pipeline`: daily Form 4 poll on watched CIKs → alert on any
post-filter P-buy or informative sale; weekly cluster-buy screen across the
whole market (cluster buys in names you *don't* watch are how new longs
enter the funnel); alert into `research/events/log.md` with the code-level
detail (who, role, $ size, % of stake, window context) so the decision
layer never has to re-derive it.
