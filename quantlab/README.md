# quantlab

The engineering layer behind the `agentic-investing` skill suite
(`container/skills/agentic-investing`, `container/skills/inv-*`): a
Rust core for low-latency data parsing/normalization and a Python layer
using modern dataframe tooling (Polars) for time-series data science,
feature engineering, forecasting, and option pricing.

## Architecture

```
quantlab/
  rust/                     # cargo workspace — the low-latency core
    crates/ql-ingest/       # raw-feed parsers & normalizers (FINRA Reg SHO,
                            # CBOE option chain JSON), zero-copy where it matters
  python/                   # the data-science layer
    quantlab/
      lake.py               # hive-partitioned parquet lake IO + _meta.json
                            # provenance sidecars (see inv-data-pipeline skill)
      pipelines/            # dataset-specific ingest→lake pipelines
      features/             # Polars feature builders (flow/tape footprints, ...)
      models/               # Forecaster interface: baselines + TS foundation
                            # model wrappers (Chronos/TimesFM as optional deps)
      pricing/              # reference option pricing (CRR American binomial,
                            # Black-Scholes checks) — Rust port when hot
```

Division of labor:

- **Rust** owns parsing of raw feeds (pipe-delimited FINRA files, large
  CBOE chain JSON) and, over time, hot numerical loops (binomial trees
  over whole chains, LSMC paths). Output is normalized CSV/JSONL handed
  to the Python layer.
- **Polars (not pandas)** owns dataframe work: lake IO, joins
  (`join_asof` for point-in-time), feature engineering, backtest frames.
  Pandas appears only at the edge when a library demands it.
- **Point-in-time rules** from the `inv-quant-foundations` skill are
  enforced in code: every lake write requires `effective_date` /
  `published_at` metadata; `lake.read` exposes them; asof joins default
  backward on `published_at`.

## Dev

```bash
cd quantlab/rust && cargo test          # Rust core
cd quantlab/python && python -m pytest  # Python layer (pip install -e .[dev])
```

Data lands under `/workspace/data` (mirrored to GCS) per the
`inv-data-pipeline` skill — never inside this repo.
