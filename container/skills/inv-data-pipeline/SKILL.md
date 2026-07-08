---
name: inv-data-pipeline
description: Data lake, download, storage, and monitoring conventions for all investing datasets — use before downloading any market/filing/options/short-interest data, when setting up a recurring data pull or monitor, when syncing data to Google Cloud Storage, or when another inv-* skill references "the lake". Defines the parquet layout, point-in-time metadata rules, endpoint verification, scheduling cadences, and alert wiring into research/events.
---

# Investing Data Pipeline (the lake)

Every other `inv-*` skill stores through this one. The design goals:
**snapshot-first** (never overwrite history — future you needs yesterday's
view of the data), **point-in-time honest** (record when *you* could have
known each fact), and **local-first with a GCS mirror**.

## Lake layout

```
/workspace/data/
  <source>/<dataset>/dt=<YYYY-MM-DD>/part-*.parquet   # hive-partitioned by snapshot date
  <source>/<dataset>/dt=<YYYY-MM-DD>/_meta.json       # provenance sidecar
```

Examples: `sec/form4/dt=2026-07-08/`, `cboe/chain_MU/dt=2026-07-08/`,
`finra/regsho_daily/dt=2026-07-08/`, `finra/short_interest/dt=2026-07-01/`.

`_meta.json` is mandatory:

```json
{"source_url": "...", "fetched_at": "2026-07-08T21:05:00Z",
 "effective_date": "2026-06-30", "published_at": "2026-07-07",
 "row_count": 4812, "notes": "..."}
```

`fetched_at` ≠ `effective_date` ≠ `published_at`. Predictive joins use
`published_at` (when the market could know), never `effective_date` (what
period the data describes). This one rule kills most forward-looking bias.

Rules:
- **Append-only**: a new pull writes a new `dt=` partition. Corrections are
  new partitions, not edits. Diffing partitions IS the signal for most
  monitors (OI change, SI change, new filings).
- **Raw + curated**: keep the raw payload (`raw/` subdir, gzipped as-is) next
  to the parsed parquet. Parsers have bugs; raw lets you re-parse history.
- **Query with DuckDB** over parquet globs
  (`read_parquet('/workspace/data/cboe/chain_MU/dt=*/part-*.parquet',
  hive_partitioning=true)`). Pandas for modeling, DuckDB for scanning.

## Google Cloud Storage mirror

The devbox runs on GCP; use the bucket from `$DEVBOX_GCS_BUCKET` (ask the
user once and persist to `research/process/lessons.md` if unset; check
`gsutil ls` / `gcloud config get-value project` for what's available).

```bash
# push after each ingestion; pull at session start if local lake is empty
gsutil -m rsync -r /workspace/data gs://$DEVBOX_GCS_BUCKET/marketdata
gsutil -m rsync -r gs://$DEVBOX_GCS_BUCKET/marketdata /workspace/data
```

The GCS copy is the durable one — session workspaces can be reclaimed. Sync
direction discipline: pull-then-work-then-push; never push a lake you didn't
pull first.

## Endpoint registry and first-use verification

Networks differ per environment (some proxies block finance hosts). On first
use of any endpoint **in a given environment**, verify with a small request
before building on it, and record working/blocked status in
`research/process/lessons.md`.

Primary free endpoints used by the sub-skills:

| Data | Endpoint | Auth | Notes |
|---|---|---|---|
| SEC submissions per company | `https://data.sec.gov/submissions/CIK{10digit}.json` | UA header | ≤10 req/s, User-Agent must contain contact email |
| XBRL company facts | `https://data.sec.gov/api/xbrl/companyfacts/CIK{10digit}.json` | UA header | all tagged financials, point-in-time `filed` dates |
| XBRL single concept | `https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{Tag}.json` | UA header | |
| EDGAR full-text search | `https://efts.sec.gov/LATEST/search-index?q="{phrase}"&forms=8-K` | UA header | JSON; buyback/announcement hunting |
| EDGAR filing archives | `https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/` | UA header | raw documents incl. Form 4 XML, 13F infotable |
| DERA structured sets (13F, insider, financials) | `https://www.sec.gov/data-research/sec-markets-data/` | browser-ish UA | quarterly TSV zips, best for backfill |
| FINRA Reg SHO daily short volume | `https://cdn.finra.org/equity/regsho/daily/CNMSshvol{YYYYMMDD}.txt` | none | pipe-delimited, per-ticker daily short volume |
| FINRA consolidated short interest | `https://api.finra.org/data/group/otcMarket/name/consolidatedShortInterest` | free API key (some public) | POST JSON; twice-monthly settlement data |
| CBOE delayed option chains | `https://cdn.cboe.com/api/global/delayed_quotes/options/{TICKER}.json` | none | full chain: OI, volume, IV, greeks; 15-min delayed |
| Daily bars fallback | `https://stooq.com/q/d/l/?s={ticker}.us&i=d` | none | CSV; or yfinance library |
| Taiwan monthly revenue (TSMC etc.) | TWSE/MOPS monthly sales disclosures | none | monthly, ~10th of month — rare truly-monthly fundamental data |

MCP-first rule: if the session has financial MCP tools (FMP: `form13F`,
`insiderTrades`, `analyst`, `statements`, `quote`, `secFilings`,
`earningsTranscript`; Robinhood: quotes/chains/historicals), prefer them for
interactive lookups — but **still snapshot results into the lake** with
`_meta.json` if they feed a conclusion or monitor. Vendor tools restate
history; the lake preserves what you saw when.

## Ingestion script conventions

Write ingestors as small idempotent Python scripts under
`/workspace/pipelines/` (they are workspace state, persisted like research/):

- one dataset per script; args: `--date` (default today) and `--tickers`;
- re-running for the same date overwrites only that `dt=` partition —
  idempotent;
- always write `_meta.json` last (its presence marks partition complete);
- polite headers everywhere: `User-Agent: <project> <contact-email>`;
- failures raise loudly — a silent empty partition poisons every monitor
  downstream. Freshness check: a monitor that reads a partition older than
  its cadence must say "STALE DATA" in its alert rather than compute on it.

## Scheduling cadences

Register recurring pulls with whatever scheduler the harness offers (devbox
triggers/cron). Standard cadence table — schedule only what a live thesis or
monitor actually needs, not everything:

| Pull | When |
|---|---|
| CBOE chain snapshot (watched tickers) | daily ~1h after US close (OI updates next morning — see inv-options-pressure) |
| FINRA Reg SHO daily file | daily post-close |
| EDGAR Form 4 / 8-K poll (watched CIKs) | daily, or hourly around events |
| FINRA consolidated short interest | on publication days (~T+7 bus. days after mid/end-month settlement) |
| 13F / N-PORT sweep | quarterly (peak: 45 days after quarter end) / monthly |
| Bars refresh | daily |
| TWSE monthly sales (supply-chain names) | ~10th of each month |

Every scheduled pull ends by running its monitors (defined in
`research/monitors/`) and appending any firing to `research/events/log.md`
in the main skill's event format — that is how the data layer talks to the
decision layer.
