---
name: quant-data-science
description: Analyze crypto market data and backtest results with DuckDB SQL over Parquet and pandas over JSONL event logs — coverage checks, PnL curves, fill-rate analysis, strategy comparison, and presenting results as compact Markdown tables.
---

# Quant Data Science

Analysis conventions from the alpha-devbox quant workflow: **DuckDB (in-memory SQL) for Parquet**, **pandas for backtest JSONL event logs**, results presented as compact numeric GFM tables.

## Tooling

```bash
uv run --with duckdb python ...        # Parquet analysis
uv run --with pandas python ...        # JSONL / dataframe analysis
```

## Parquet analysis with DuckDB (not pandas)

Query market data directly — no loading step, handles files larger than RAM:

```python
import duckdb

con = duckdb.connect()  # in-memory
root = "~/.polysharp/data/polymarket"

# Coverage: rows/tickers/time-range per day
con.sql(f"""
  SELECT count(*) AS trades, count(DISTINCT ticker) AS tickers,
         min(ts) AS first_ts, max(ts) AS last_ts
  FROM read_parquet('{root}/trades/date=2025-01-05/trades.parquet')
""").show()

# Per-ticker liquidity ranking
con.sql(f"""
  SELECT ticker, outcome, count(*) AS n, sum(price*size) AS notional
  FROM read_parquet('{root}/trades/date=2025-01-05/trades.parquet')
  WHERE ticker LIKE 'btc-updown-15m-%'
  GROUP BY 1,2 ORDER BY notional DESC LIMIT 20
""").show()

# Quote-gap detection in snapshots
con.sql(f"""
  SELECT ticker, max(ts - prev_ts) AS max_gap_ms FROM (
    SELECT ticker, ts, lag(ts) OVER (PARTITION BY ticker ORDER BY ts) AS prev_ts
    FROM read_parquet('{root}/snapshots/date=2025-01-05/snapshots.parquet'))
  GROUP BY 1 ORDER BY 2 DESC LIMIT 10
""").show()
```

`bids`/`asks` in snapshots are JSON strings — parse with DuckDB JSON functions, e.g. best bid: `json_extract(bids, '$[0].price')::DOUBLE`.

## Backtest event-log analysis (JSONL → pandas)

The backtest writes one JSON event per line (see the **crypto-backtest** skill for event types):

```python
import json, pandas as pd

events = [json.loads(l) for l in open("output/backtest_events.jsonl")]
df = pd.DataFrame(events)
df["timestamp"] = pd.to_datetime(df["timestamp"])

placed = df[df.event_type == "LimitOrder.OrderPlaced"]
fills  = df[df.event_type.str.contains("Filled", na=False)]
print(f"fill rate: {len(fills)/max(len(placed),1):.1%}")

# Cash-flow PnL curve from fills
fd = pd.json_normalize(fills["data"])
fd["timestamp"] = fills["timestamp"].values
fd["cash"] = fd.apply(
    lambda r: r.filled_size * r.fill_price * (-1 if r.side == "Buy" else 1), axis=1)
pnl_curve = fd.set_index("timestamp")["cash"].cumsum()

# Position lifecycle / holding periods
positions = pd.json_normalize(df[df.event_type == "Position"]["data"])
```

Key headline metrics (also emitted by the runner as `BacktestMetrics`): `final_pnl` (cash-flow based: `net_cash_flow + final_inventory_value`), fill rate, `total_fills`, `net_cash_flow`, `final_inventory`.

## Data-quality guardrails before drawing conclusions

- Run `poly-data prescreen` / `poly-data completeness` (see **crypto-data** skill) — exclude tickers with missing outcomes or long quote gaps; backtest only `allowlist.csv` tickers.
- Check `summary.json` exclusion reasons: `jq '.exclusion_reason_counts' output/data_completeness/date=$DATE/summary.json`.
- Compare strategies on the same date/ticker set only; backtests are deterministic, so diffs are attributable to the strategy.
- Prefer latency-simulation runs for realistic fill rates; a strategy profitable only without latency is a red flag.

## Presenting results

Answer with compact Markdown: one-sentence headline, short bullets, ONE numeric GFM table (first column categorical/time-like, value columns numeric), one-sentence bottom line. No HTML/JSON wrappers, no code-fenced tables.

```
## Headline
Strategy A captures spread; B overtrades.

| Strategy | PnL | Fills | Fill rate | Max drawdown |
| --- | ---: | ---: | ---: | ---: |
| A (spread 0.01) | 142.50 | 380 | 62% | -35.20 |
| B (spread 0.02) | 87.10 | 190 | 41% | -22.40 |

## Bottom line
A wins on PnL; B on risk.
```

If there is no real numeric data yet, show a readiness/blocker table instead of forcing a chart.
