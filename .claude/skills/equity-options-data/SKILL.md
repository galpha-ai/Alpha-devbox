---
name: equity-options-data
description: Download, snapshot, and manage US equity and options market data (price bars, option chains/quotes/historicals, earnings dates) using the FMP and Robinhood MCP tools, persisted to a local Parquet store for backtesting. Equity/options counterpart of the crypto-data skill.
---

# Equity & Options Data Download & Management

Data sources are MCP tools already connected to this environment:

| Source | Best for |
|---|---|
| `mcp__FMP__chart` / `quote` / `calendar` | EOD + intraday equity bars, batch quotes, earnings/dividend/split calendars |
| `mcp__robinhood_MCP__get_equity_historicals` | OHLCV bars, split-adjusted by default (right for backtests) |
| `mcp__robinhood_MCP__get_option_chains/instruments/quotes/historicals` | Option chain discovery, contract-level quotes and OHLC history |
| `mcp__robinhood_MCP__get_earnings_calendar/results` | Report dates + am/pm timing + EPS est/actual |

Persist anything you'll reuse into the local Parquet store (below) — MCP calls are rate-limited and not reproducible; Parquet + DuckDB is (same convention as the crypto `~/.polysharp` store).

## Local data layout

```
~/.equityquant/data/equities/bars/interval=1d/symbol=AAPL/bars.parquet
~/.equityquant/data/equities/bars/interval=5m/symbol=AAPL/date=YYYY-MM-DD/bars.parquet
~/.equityquant/data/options/chains/underlying=AAPL/snapshot_date=YYYY-MM-DD/chain.parquet
~/.equityquant/data/options/bars/underlying=AAPL/expiry=YYYY-MM-DD/bars.parquet
~/.equityquant/data/earnings/symbol=AAPL/earnings.parquet
```

## Minimum schemas

| File | Columns |
|---|---|
| equity `bars.parquet` | `ts` TIMESTAMP, `symbol`, `open` F64, `high` F64, `low` F64, `close` F64, `volume` F64, `adjustment` (`split`/`none`/`all`) |
| option `chain.parquet` | `snapshot_ts`, `underlying`, `instrument_id`, `expiration` DATE, `strike` F64, `type` (`call`/`put`), `bid` F64, `ask` F64, `mark` F64, `open_interest` F64, `volume` F64, `iv` F64 (nullable) |
| option `bars.parquet` | `ts`, `instrument_id`, `underlying`, `expiration`, `strike`, `type`, `open`, `high`, `low`, `close`, `volume` |
| `earnings.parquet` | `symbol`, `report_date` DATE, `timing` (`am`/`pm`), `eps_estimate` F64, `eps_actual` F64, `verified` BOOL |

## Equity bars

```
# Daily EOD, long history (FMP)
mcp__FMP__chart {endpoint: "historical-price-eod-full", symbol: "AAPL", from_date: "2023-01-01", to_date: "2026-07-01"}

# Intraday (FMP): intraday-1-min / 5-min / 15-min / 30-min / 1-hour / 4-hour

# Robinhood (split-adjusted default; symbols ≤ 10/call; interval names: minute, 5minute, hour, day, week — NOT 1minute)
mcp__robinhood_MCP__get_equity_historicals {symbols: ["AAPL","MSFT"], start_time: "2026-01-01T00:00:00Z", interval: "day"}
```

Rules: use split-adjusted prices for backtests (`adjustment_type: "split"`, the Robinhood default; FMP `historical-price-eod-dividend-adjusted` for total-return work). `bounds: "regular"` unless extended-hours is the question. Explicit interval + wide range can exceed the bar cap — narrow the range or coarsen the interval.

## Options: chain → instruments → quotes/bars

Options require a 3-step resolution (ticker symbols are NOT accepted downstream):

```
# 1. Chain: expiration dates + chain id
mcp__robinhood_MCP__get_option_chains {underlying_symbol: "AAPL"}

# 2. Contracts for an expiry (filter by type/strike; state: "expired" for past contracts)
mcp__robinhood_MCP__get_option_instruments {chain_symbol: "AAPL", expiration_dates: "2026-07-17", type: "call"}

# 3a. Real-time quotes (bid/ask/mark + prior close), instrument UUIDs from step 2
mcp__robinhood_MCP__get_option_quotes {instrument_ids: ["<uuid>", ...]}

# 3b. OHLC history per contract (≤ 10 ids/call; use state:"expired" instruments to study past earnings cycles)
mcp__robinhood_MCP__get_option_historicals {instrument_ids: ["<uuid>"], start_time: "2026-06-01T00:00:00Z", interval: "day"}
```

**Historical chain snapshots (bid/ask/IV as-of a past date) are not queryable.** Like the crypto live-collection services, if a strategy needs chain history (IV surfaces, spreads), snapshot the chain on a schedule and append to `chain.parquet` — a snapshot loop you run daily is the equity analog of `polymarket-sub`.

## Earnings dates

```
# Market-wide window (≤ 31 days; filter: "high_market_cap" for >$1B names)
mcp__robinhood_MCP__get_earnings_calendar {start_date: "2026-07-08", days: 7, filter: "high_market_cap"}

# One symbol, trailing 8 quarters with est/actual EPS + am/pm timing
mcp__robinhood_MCP__get_earnings_results {symbol: "AAPL"}

# Longer history / date-range queries (FMP)
mcp__FMP__calendar {endpoint: "earnings-company", symbol: "AAPL"}
mcp__FMP__calendar {endpoint: "earnings-calendar", from_date: "2026-07-01", to_date: "2026-07-31"}
```

Also available in `mcp__FMP__calendar`: `dividends-calendar/-company`, `splits-calendar/-company`, `ipos-calendar` — check dividends/splits before interpreting raw price gaps.

## Persisting MCP results to Parquet

Write JSON results to the scratchpad, then convert once:

```python
import duckdb
con = duckdb.connect()
con.sql("""
  COPY (SELECT * FROM read_json_auto('bars_aapl.json'))
  TO '~/.equityquant/data/equities/bars/interval=1d/symbol=AAPL/bars.parquet' (FORMAT PARQUET)
""")
```

Query the whole store with globs: `read_parquet('~/.equityquant/data/equities/bars/interval=1d/*/bars.parquet')`.

## Gotchas

- FMP plan gating: `earningsTranscript` and `form13F` need Ultimate/Enterprise; `technicalIndicators` needs Starter+. If a call errors on plan, fall back to computing indicators locally from bars.
- Robinhood earnings entries carry a `verified` flag — unverified future dates move; re-check close to the event.
- Option instrument UUIDs are per-contract and stable; store them in `chain.parquet` so later historicals pulls skip re-resolution.
- Mixed adjustment is the top source of silent backtest bugs: never join `split`-adjusted bars with `none` bars; record the `adjustment` column.

Analyze with the **quant-data-science** skill; feed backtests via the **equity-options-backtest** skill.
