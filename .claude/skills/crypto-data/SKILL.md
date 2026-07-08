---
name: crypto-data
description: Download, sync, inspect, and manage crypto market data (Polymarket orderbooks/trades, Binance spot prices, Solana transactions) using the poly-data CLI and open-crypto-quant ingestion services. Use when acquiring or validating historical data for backtests or model training.
---

# Crypto Data Download & Management

The canonical data workflow is the `poly-data` Python CLI in `galpha-ai/open-crypto-quant` (`tools/poly-data`). Do not write ad-hoc download scripts — use `poly-data` so data lands in the standard layout and gets indexed.

## Prerequisites

```bash
git clone --depth 1 https://github.com/galpha-ai/open-crypto-quant /workspace/open-crypto-quant  # if missing
cd /workspace/open-crypto-quant/tools/poly-data
uv run poly-data --help    # Python 3.12+, managed by uv; deps: duckdb, pyyaml
```

Note: `poly-data sync` pulls from a remote data host over rsync/SSH (default host `ewr1-3`, remote root `/mnt/local-storage/airflow-data`; override with `--host/--user/--remote-root`). It requires SSH access to that host — without it, obtain the Parquet files another way and place them in the local layout, then run `poly-data index`.

## Local data layout

```
~/.polysharp/data/polymarket/snapshots/date=YYYY-MM-DD/snapshots.parquet
~/.polysharp/data/polymarket/updates/date=YYYY-MM-DD/updates.parquet
~/.polysharp/data/polymarket/trades/date=YYYY-MM-DD/trades.parquet
~/.polysharp/data/polymarket/spot/date=YYYY-MM-DD/spot_prices.parquet
~/.polysharp/index.db          # SQLite metadata index
```

Ticker names encode the market window in the suffix, e.g. `btc-updown-15m-1704067200` (unix start ts).

## CLI cheatsheet

```bash
DATE=YYYY-MM-DD

# Download & index
uv run poly-data sync --date "$DATE"                 # one date
uv run poly-data sync --date-range 2025-01-01..2025-01-07
uv run poly-data sync --latest 3 --purge             # newest 3 remote dates, purge older local
uv run poly-data index --date "$DATE"                # (re)index manually placed files

# Inspect coverage
uv run poly-data status
uv run poly-data status --date "$DATE"

# Enumerate tickers (no manual parquet scanning)
uv run poly-data tickers --date "$DATE" --pattern "btc-updown-15m-*"
uv run poly-data tickers --date "$DATE" --regex '...' --sample 20 --latest 5 --after 14:00 --json

# Resolve concrete parquet paths for a ticker set (feed these to the backtest)
uv run poly-data resolve --date "$DATE" --pattern "btc-updown-15m-*" --json

# Prescreen tickers on coverage metrics from the index DB
uv run poly-data prescreen --date "$DATE" --pattern "btc-updown-15m-*" --json \
  --min-snapshots 1 --min-window-coverage 0.9

# Data-completeness manifest (allowlist.csv / exclusions.csv / summary.json)
uv run poly-data completeness --date "$DATE" [--synthetic-bbo ./output/synthetic_bbo.parquet]

# Garbage-collect old data/cache
uv run poly-data gc --keep-days 7 --dry-run
```

## Parquet schemas (minimum columns)

| File | Columns |
|---|---|
| `snapshots.parquet` | `ts` TIMESTAMP_MS, `ticker`, `outcome`, `bids` (JSON string), `asks` (JSON string), `end_date` |
| `updates.parquet` | `ts`, `asset_id`, `price` F64, `size` F64, `side` (`BUY`/`SELL`), `ticker`, `outcome` |
| `trades.parquet` | `ts`, `ticker`, `outcome`, `side`, `price` F64, `size` F64 |
| `spot.parquet` | `ts`, `symbol`, `price` F64 |

`bids`/`asks` JSON format: `[{"price": 0.50, "size": 100.0}, ...]`.

## Live data collection services (Rust crates)

For collecting fresh data rather than syncing historical dumps:

| Crate | Source | What it captures |
|---|---|---|
| `crates/tx-sub/crates/spot-price-sub` | Binance aggTrade WebSocket | Real-time spot prices |
| `crates/tx-sub/crates/polymarket-sub` | Polymarket WebSocket | Orderbook snapshots/updates/trades |
| `crates/tx-sub/crates/solana-sub` | Yellowstone gRPC | Solana transactions (pump.fun etc.) |
| `crates/ingester` | Redis streams → ClickHouse | Persistent ingestion (DDL in `sql/clickhouse.sql`) |

Build with `cargo build -p spot-price-sub` etc.; configure via each crate's `config/config.yaml` (see `config/config.example.yaml` at repo root).

## Reference docs (in the clone)

- `tools/poly-data/docs/backtest-data.md` — required inputs, schemas, synthetic BBO, manifest workflow
- `tools/poly-data/docs/data-completeness.md` — completeness metrics and thresholds
- `tools/poly-data/docs/architecture.md` — CLI internals (DuckDB analysis, SQLite index)
- `crates/ingester/sql/clickhouse.sql` — ClickHouse table DDL
