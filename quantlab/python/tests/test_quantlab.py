"""quantlab test suite — these tests ARE the acceptance checks referenced
by quantlab/BLUEPRINT.md; keep requirement ids (R#) in test names."""

import datetime as dt
import json
import shutil
import subprocess
from pathlib import Path

import polars as pl
import pytest

from quantlab import benchmarks, lake, monitors
from quantlab.features.flow import daily_flow_features
from quantlab.models.forecaster import ChronosForecaster, NaiveDrift, SeasonalNaive
from quantlab.pipelines import parsers
from quantlab.pricing.binomial import CRRPricer, black_scholes

FIXTURES = Path(__file__).parent / "fixtures"
UTC = dt.timezone.utc


# --- R1: storage infra — lake with mandatory provenance -------------------

def _prov(**kw):
    base = dict(
        source_url="https://example.test/x",
        effective_date="2026-07-07",
        published_at="2026-07-08T12:00:00+00:00",
    )
    base.update(kw)
    return lake.Provenance(**base)


def test_r1_lake_roundtrip_with_provenance(tmp_path):
    df = pl.DataFrame({"symbol": ["MU"], "value": [1.0]})
    lake.write(df, "test", "ds", "2026-07-08", _prov(), root=tmp_path)
    out = lake.read("test", "ds", root=tmp_path)
    assert out["snapshot_date"].to_list() == ["2026-07-08"]
    assert out["published_at"].dtype == pl.Datetime("us", "UTC")
    fresh = lake.freshness("test", "ds", root=tmp_path)
    assert fresh["latest"] == "2026-07-08" and fresh["row_count"] == 1


def test_r1_lake_refuses_missing_provenance_and_empty_frames(tmp_path):
    with pytest.raises(ValueError, match="required"):
        lake.Provenance(source_url="", effective_date="2026-01-01", published_at="x")
    with pytest.raises(ValueError, match="empty partition"):
        lake.write(pl.DataFrame({"a": []}), "t", "d", "2026-07-08", _prov(), root=tmp_path)


def test_r1_incomplete_partition_is_skipped(tmp_path):
    df = pl.DataFrame({"a": [1]})
    part = lake.write(df, "t", "d", "2026-07-08", _prov(), root=tmp_path)
    (part / "_meta.json").unlink()  # simulate crash mid-write
    with pytest.raises(FileNotFoundError):
        lake.read("t", "d", root=tmp_path)


# --- R2: parsers, incl. cross-language golden fixtures --------------------

def test_r2_regsho_python_parser_golden():
    df = parsers.parse_regsho((FIXTURES / "regsho_sample.txt").read_text())
    assert df.height == 3
    mu = df.filter(pl.col("symbol") == "MU").row(0, named=True)
    assert mu["date"] == "2026-07-06" and mu["short_volume_ratio"] == 0.5
    halted = df.filter(pl.col("symbol") == "HALTED").row(0, named=True)
    assert halted["short_volume_ratio"] is None


def test_r2_cboe_python_parser_golden():
    df = parsers.parse_cboe_chain((FIXTURES / "cboe_chain_sample.json").read_text())
    assert df.height == 2
    call = df.filter(pl.col("right") == "C").row(0, named=True)
    assert call["expiry"] == "2026-09-18" and call["strike"] == 130.0
    assert abs(call["mid"] - 7.20) < 1e-9


def test_r2_occ_symbol_edge_cases():
    assert parsers.parse_occ_symbol("BRKB261218P00450500") == ("BRKB", "2026-12-18", "P", 450.5)
    with pytest.raises(ValueError):
        parsers.parse_occ_symbol("GARBAGE")


@pytest.mark.skipif(shutil.which("ql-ingest") is None, reason="rust binary not on PATH")
def test_r2_cross_language_parity_regsho():
    raw = (FIXTURES / "regsho_sample.txt").read_text()
    rust = subprocess.run(["ql-ingest", "regsho"], input=raw, capture_output=True, text=True)
    rust_rows = [json.loads(l) for l in rust.stdout.splitlines()]
    py_rows = parsers.parse_regsho(raw).to_dicts()
    assert rust_rows == py_rows


# --- R3: benchmark construction — no lookahead by construction ------------

def _sample_frame(n=200):
    t0 = dt.datetime(2025, 1, 1, tzinfo=UTC)
    asof = [t0 + dt.timedelta(days=i) for i in range(n)]
    return pl.DataFrame(
        {
            "asof": asof,
            "resolve_at": [t + dt.timedelta(days=5) for t in asof],
            "target": [float(i % 7 - 3) for i in range(n)],
            "feat": [float(i) for i in range(n)],
        }
    )


def test_r3_benchmark_rejects_lookahead_targets():
    df = _sample_frame().with_columns(pl.col("asof").alias("resolve_at"))
    with pytest.raises(ValueError, match="lookahead"):
        benchmarks.Benchmark("bad", df, horizon_desc="5d")


def test_r3_purge_and_embargo():
    b = benchmarks.Benchmark("t", _sample_frame(), horizon_desc="5d", embargo_days=3)
    split = b.rolling_origin_splits(4)[0]
    train, test = b.split_frames(split)
    # No training label may resolve at/after test start (purge + embargo).
    assert train.filter(
        pl.col("resolve_at") + pl.duration(days=3) >= split.test_start
    ).is_empty()
    assert test.filter(pl.col("asof") < split.test_start).is_empty()


def test_r3_pit_join_requires_publication_and_joins_backward():
    samples = pl.DataFrame({"asof": [dt.datetime(2026, 1, 10, tzinfo=UTC)]})
    feats = pl.DataFrame(
        {
            "published_at": [
                dt.datetime(2026, 1, 5, tzinfo=UTC),
                dt.datetime(2026, 1, 11, tzinfo=UTC),  # future — must not join
            ],
            "x": [1.0, 99.0],
        }
    )
    out = benchmarks.pit_join(samples, feats)
    assert out["x"].to_list() == [1.0]
    with pytest.raises(ValueError, match="publication"):
        benchmarks.pit_join(samples, feats.drop("published_at"))


def test_r3_evaluate_walk_forward_with_fingerprint():
    b = benchmarks.Benchmark("t", _sample_frame(), horizon_desc="5d")
    res = benchmarks.evaluate(b, lambda tr, te: [0.0] * te.height, n_splits=4)
    assert res["fingerprint"] == b.fingerprint()
    assert res["pooled"]["n"] > 0


# --- R4: baselines / forecaster interface ---------------------------------

def test_r4_baselines():
    hist = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    assert NaiveDrift().forecast(hist, 2) == [9.0, 10.0]
    assert SeasonalNaive(season=4).forecast(hist, 4) == [5.0, 6.0, 7.0, 8.0]


def test_r4_chronos_wrapper_fails_loudly_without_dep():
    with pytest.raises(ImportError, match="chronos"):
        ChronosForecaster().forecast([1.0] * 30, 5)


# --- R5: pricing verification block ---------------------------------------

def test_r5_european_limit_matches_black_scholes():
    err = CRRPricer(steps=800).european_limit_check(100, 100, 0.5, 0.04, 0.3, "C")
    assert err < 5e-3


def test_r5_american_put_carries_early_exercise_premium():
    p = CRRPricer(steps=400)
    amer = p.price(100, 110, 1.0, 0.08, 0.25, "P", american=True)
    euro = p.price(100, 110, 1.0, 0.08, 0.25, "P", american=False)
    assert amer > euro + 1e-4


def test_r5_dividend_lowers_call_value():
    no_div = CRRPricer(steps=400).price(100, 100, 1.0, 0.04, 0.3, "C")
    with_div = CRRPricer(steps=400, dividends=[(0.5, 3.0)]).price(100, 100, 1.0, 0.04, 0.3, "C")
    assert with_div < no_div


def test_r5_put_call_parity_european_no_div():
    import math
    p = CRRPricer(steps=800)
    c = p.price(100, 105, 0.75, 0.04, 0.3, "C", american=False)
    put = p.price(100, 105, 0.75, 0.04, 0.3, "P", american=False)
    parity = c - put - (100 - 105 * math.exp(-0.04 * 0.75))
    assert abs(parity) < 1e-2


# --- R6: features are trailing-only ----------------------------------------

def test_r6_flow_features_do_not_use_future_rows():
    bars = pl.DataFrame(
        {
            "date": [dt.date(2026, 1, 1) + dt.timedelta(days=i) for i in range(80)],
            "symbol": ["MU"] * 80,
            "open": [100.0] * 80,
            "high": [101.0 + i * 0.1 for i in range(80)],
            "low": [99.0] * 80,
            "close": [100.0 + i * 0.1 for i in range(80)],
            "volume": [1e6 + (i % 9) * 1e5 for i in range(80)],
        }
    )
    full = daily_flow_features(bars)
    truncated = daily_flow_features(bars.head(60))
    # Feature values on day 59 must be identical whether or not days 60-79 exist.
    import math
    for col in ("volume_z", "clv_20d", "absorption_5d"):
        a = full[col][59]
        b = truncated[col][59]
        both_undefined = (a is None and b is None) or (
            a is not None and b is not None and math.isnan(a) and math.isnan(b)
        )
        assert both_undefined or abs(a - b) < 1e-12, col


# --- R7: production monitoring — freshness gate + event wiring -------------

def test_r7_monitor_freshness_gate_and_event_append(tmp_path):
    df = parsers.parse_regsho((FIXTURES / "regsho_sample.txt").read_text())
    lake.write(df, "finra", "regsho_daily", "2026-07-06", _prov(), root=tmp_path)
    log = tmp_path / "events.md"
    mon = monitors.Monitor(
        name="svr", source="finra", dataset="regsho_daily",
        max_staleness_days=3, check=lambda d: ["always-fires"],
    )
    # Fresh enough → check runs, alert appended.
    res = monitors.run_monitors([mon], events_log=log, today=dt.date(2026, 7, 8), root=tmp_path)
    assert res[0].status == "alert" and "always-fires" in log.read_text()
    # Too old → STALE DATA instead of computing.
    res = monitors.run_monitors([mon], events_log=log, today=dt.date(2026, 8, 1), root=tmp_path)
    assert res[0].status == "stale" and "STALE DATA" in log.read_text()
