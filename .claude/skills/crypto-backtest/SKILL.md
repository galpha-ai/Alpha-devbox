---
name: crypto-backtest
description: Run quantitative backtests of crypto/prediction-market trading strategies using the open-crypto-quant trade-server engine and the poly-strat-starter template. Use for strategy backtesting, PnL simulation, fill/latency modeling, and strategy parameter sweeps.
---

# Crypto Quant Backtesting

Backtesting is powered by the `trade_server` crate in the `galpha-ai/open-crypto-quant` monorepo — an event-driven replay engine over historical Polymarket orderbook + trade data with realistic trade-based fill simulation and optional order latency modeling.

## Prerequisites

1. Clone the repo if not already present:
   ```bash
   git clone --depth 1 https://github.com/galpha-ai/open-crypto-quant /workspace/open-crypto-quant
   ```
2. Rust toolchain (`cargo`) — the workspace builds with stable Rust.
3. Backtest data: three Parquet files (`snapshots.parquet`, `updates.parquet`, `trades.parquet`), plus `spot.parquet` for spot-dependent strategies. Use the **crypto-data** skill to sync/discover data.

## Quickest path: poly-strat-starter

`crates/poly-strat-starter` is a ready-to-run CLI backtester with a starter strategy (buys cheap outcomes). Edit `src/strategy.rs` to implement your own strategy; `src/main.rs` wires the CLI to `BacktestConfig`.

```bash
cd /workspace/open-crypto-quant
cargo run -p poly-strat-starter -- \
  --snapshot-path ~/.polysharp/data/polymarket/snapshots/date=YYYY-MM-DD/snapshots.parquet \
  --update-path   ~/.polysharp/data/polymarket/updates/date=YYYY-MM-DD/updates.parquet \
  --trade-path    ~/.polysharp/data/polymarket/trades/date=YYYY-MM-DD/trades.parquet \
  --output-path output/backtest_events.jsonl \
  --outcome-filter Up \
  --ticker-pattern 'btc-updown-15m-*' \
  --threshold 0.30 --trade-amount 100 --max-positions 10 \
  --take-profit 0.15 --stop-loss 0.10 --max-hold-secs 3600 \
  --initial-balance 10000
```

Market-data events are NOT captured in the JSONL by default (size). Re-enable while debugging with `--capture-snapshots`, `--capture-updates`, `--capture-trades`, `--capture-spot-prices`.

## Library usage (custom runner)

```rust
use trade_server::backtest::{BacktestConfig, BacktestRunner, PositionConfig};

let config = BacktestConfig::new(snapshots, updates, trades, output_jsonl)
    .with_outcome_filter("Up")
    .with_ticker_patterns(vec!["btc-updown-15m-*".into()])
    .with_timer_interval(Duration::from_secs(1))
    .with_slippage(0.001, 0.001)
    .with_position_config(
        PositionConfig::new(10_000.0, 10, Duration::from_secs(3600), 100.0)
            .with_take_profit(0.15)
            .with_stop_loss(0.05),
    );
let result = BacktestRunner::run(config, signal_generator).await?;
println!("PnL: {:.2}", result.metrics.final_pnl);
```

## Implementing a strategy

Implement `trade_server::signal::SignalGenerator` — `generate_signal(&mut self, event: &SystemEvent)` returns `Vec<Box<dyn TradableSignal>>`.

- **Entry/Exit/ModifyOrder/CancelOrder** actions via `signal_action()`.
- **Intent signals** (market making): return `is_intent_signal() == true` + `get_order_intent()` expressing desired book state (`QuoteLevel::gtc(price, size)`); the runner reconciles diffs into cancels/placements automatically.
- **Limit orders**: `is_limit_order() == true` + `get_limit_price()` + `get_time_in_force()`.

### Critical: logical time, not wall-clock time

Signals MUST carry the event's timestamp, not `Utc::now()`. With latency simulation enabled, wall-clock timestamps make every fill check miss (zero fills). Track logical time from `event.timestamp()` and build metadata with `SignalMetadata::with_timestamp(current_time)`.

## Fill simulation (trade-based model)

- BID fills when a historical SELL trade crosses at or below the bid price; ASK fills when a BUY trade crosses at or above the ask.
- Orders fill at the **order price**, size capped by `min(order.remaining, trade.size)`; partial fills supported.
- Latency simulation (recommended for realism): orders become fillable only after `T + random(min_place_latency, max_place_latency)`; cancels stay fillable until confirmed. Configure with `.with_latency(LatencySimulationConfig { min_place_latency_ms: 150, max_place_latency_ms: 500, .. })` or the `backtest.latency` YAML block.

## Output & metrics

- JSONL event log: one event per line (`MarketData.*`, `Signal.*`, `LimitOrder.OrderPlaced/OrderPartiallyFilled/OrderCancelled`, `Execution`, `Position`, `Timer`, `Redemption.*`). Analyze with the **quant-data-science** skill.
- `BacktestMetrics`: `total_signals`, `total_orders_placed`, `total_fills`, `net_cash_flow`, `final_inventory`, `final_inventory_value`, `final_pnl` (cash-flow based — correctly captures market-making spread), `total_redemptions`, etc.
- Backtests are deterministic and single-threaded: same inputs → identical results.

## Data quality: manifest-driven ticker selection

Backtests get biased by missing markets or long quote gaps. Build a completeness manifest with `poly-data completeness` (see the **crypto-data** skill) and paste `allowlist.csv` tickers into `ticker_patterns`.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `EmptyDataError` | Data missing, outcome filter mismatch, or timestamps not ms |
| `InvalidSchemaError` | Column names/types off (ts INT64, price/size FLOAT64, bids/asks JSON strings) |
| No fills | Bid prices unrealistic; SELL trades fill bids, BUY trades fill asks |
| Zero fills only with latency sim | Wall-clock timestamps in signals — use logical time |

## Reference docs (in the clone)

- `crates/trade-server/docs/usage-guide/backtesting.md` — full guide (config, fill model, latency, examples)
- `crates/trade-server/docs/usage-guide/intent-signals.md` — intent signal system, pair redemption
- `crates/trade-server/docs/usage-guide/orderbook-trading.md`, `paper-trading.md`, `core-traits.md`
- `crates/trade-server/docs/design/backtest.md` — engine design
- `crates/poly-strat-starter/CLAUDE.md` — starter template workflow
