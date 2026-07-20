---
name: equity-options-backtest
description: Backtest US equity and options trading strategies (signal-driven equity trades, earnings straddles/strangles, covered calls, post-earnings drift) over the local Parquet store using pandas/DuckDB, with the fill/lookahead/latency discipline ported from the crypto trade-server engine. Equity/options counterpart of the crypto-backtest skill.
---

# Equity & Options Backtesting

There is no Rust replay engine for equities (the `trade-server` engine is Polymarket-specific), so equity/options backtests are Python over the `~/.equityquant` Parquet store (see **equity-options-data**). What carries over from `trade-server` is the discipline — the rules below are the equity translations of its fill model, latency simulation, and logical-time requirements.

## Rules ported from trade-server

| trade-server concept | Equity/options translation |
|---|---|
| Logical time, never wall-clock | Signals at bar `t` may only read data with `ts <= t` — no `.shift(-1)`, no full-series statistics (mean/std/min/max computed over the whole frame), no resolving earnings `actual` before the report timestamp |
| Order placement latency | Execute at the **next bar's open**, never the signal bar's close |
| Trade-based fill model | Limit orders fill only if the next bar's range crosses the limit price; fill at your price, not the touch |
| Slippage config | Deduct explicit slippage + spread: equities ~1–5 bps; options: cross half the bid-ask spread minimum, and spreads on single-name options are wide — model `mark ± spread/2` |
| Deterministic replay | Seed any randomness; same inputs → identical results |
| JSONL event log | Emit one JSON event per line (`Signal`, `OrderPlaced`, `Filled`, `Position`) so the **quant-data-science** analysis patterns apply unchanged |

## Vectorized equity backtest skeleton

```python
import pandas as pd, duckdb, json

bars = duckdb.sql("""
  SELECT ts, symbol, open, close FROM read_parquet(
    '~/.equityquant/data/equities/bars/interval=1d/*/bars.parquet')
  ORDER BY symbol, ts
""").df()

def run(bars, signal_fn, cost_bps=5):
    events, cash, pos = [], 0.0, {}
    for sym, g in bars.groupby("symbol"):
        g = g.reset_index(drop=True)
        sig = signal_fn(g)                    # uses only rows <= t (enforce: sig[t] from g.iloc[:t+1])
        for t in range(len(g) - 1):
            nxt = g.iloc[t + 1]               # execute at NEXT bar open
            px = nxt.open * (1 + cost_bps / 1e4 * sig[t])
            if sig[t] != pos.get(sym, 0):
                events.append({"ts": str(nxt.ts), "event_type": "Filled",
                               "data": {"symbol": sym, "side": "Buy" if sig[t] > pos.get(sym, 0) else "Sell",
                                        "fill_price": px, "filled_size": abs(sig[t] - pos.get(sym, 0))}})
                cash -= (sig[t] - pos.get(sym, 0)) * px
                pos[sym] = sig[t]
    with open("output/backtest_events.jsonl", "w") as f:
        f.writelines(json.dumps(e) + "\n" for e in events)
    return cash, pos, events
```

Mark final PnL as `cash + Σ pos × last close` (cash-flow PnL, same definition as `BacktestMetrics.final_pnl`).

## Event-driven backtests around earnings

Post-earnings drift / earnings reversal template:

1. Load `earnings.parquet` (report_date, timing, eps_estimate, eps_actual).
2. Entry timestamp: `timing == "pm"` → next day's open; `timing == "am"` → same day's open. Getting this wrong is the equity version of the wall-clock-time bug — it leaks the announcement into the entry price.
3. Surprise = `(eps_actual - eps_estimate) / |eps_estimate|`; bucket into quantiles **using only past events** (expanding window), not the full sample.
4. Hold N days, exit at open; log events to JSONL; compare surprise buckets on the same symbol set and date range only.
5. **Point-in-time fundamentals only.** If the signal uses fundamentals or estimates, they must be as-known-then: pre-print estimates (not today's revised consensus), statements gated by their **filing date** (a Q2 number is usable ~4–6 weeks after quarter end, not on the quarter-end date; use FMP `financial-reports-dates` / as-reported statements), and no restated figures. Hindsight contamination in fundamental data is the same bug as price lookahead — it just fails silently.

## Options strategy backtests

Two data regimes — state which one a result came from:

**Regime A — realized contract prices (preferred).** Resolve past contracts with `get_option_instruments {state: "expired"}`, pull `get_option_historicals` per contract into `options/bars`, and backtest on actual OHLC. E.g. earnings straddle: buy ATM call+put at the close before the report, sell at the next day's open; fills at `close`/`open` ± half-spread estimate.

**Regime B — model prices (fallback).** No contract history → Black-Scholes from the underlying bar series and an IV assumption. Label results clearly: BS mid-prices with assumed IV overstate PnL because they ignore spread and IV crush. Never quietly mix regimes.

Options-specific rules:

- **Expiration handling**: exercise/assignment at intrinsic value on expiry; a position you can't close before expiry settles at intrinsic, not at the last mark.
- **IV crush**: front-expiry IV drops sharply after a report; long-premium earnings strategies must beat the crush, so backtests need realized contract prices (Regime A) around the event.
- **Implied vs realized move**: implied move = ATM straddle mid ÷ spot (see **earnings-analysis**); a straddle backtest is a bet that realized > implied — report both columns.
- **Position sizing**: contracts are 100× multipliers; enforce max-positions and per-trade capital like `PositionConfig` did (`initial_balance`, `trade_amount`, `max_open_positions`, `take_profit`, `stop_loss`, `max_holding_period`).

## Sanity checks before believing a result

- Re-run with 2× the slippage/spread assumption — a strategy that dies is spread-capture, not edge.
- Shift entries one bar later — collapse means lookahead leakage.
- Check turnover × cost against gross PnL.
- Split-adjustment: verify no bar has a >30% overnight "move" that is actually a split (see **equity-options-data** gotchas).
- Report per-year subperiod results, not just full-sample.

## Output

Same contract as the crypto backtester: `output/backtest_events.jsonl` + a headline metrics dict (`final_pnl`, `total_fills`, fill rate, max drawdown, Sharpe from daily marks). Analyze and present with the **quant-data-science** skill (compact GFM table, one headline, one bottom line).
