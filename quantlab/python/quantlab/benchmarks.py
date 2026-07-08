"""Benchmark construction: turn live time series into causally-ordered,
no-lookahead ML prediction tasks.

This is the load-bearing module of the research system (see the
inv-quant-foundations skill): infrastructure first, hill-climbing second.
A `Benchmark` is a frozen, reproducible task — features joined strictly on
publication time, rolling-origin splits with purge and embargo — that any
model (baseline, GBM, foundation model) can be evaluated on with identical
rules.

Core guarantees, enforced in code rather than by convention:
1. Feature rows enter a sample only if `published_at` <= the sample's
   `asof` time (publication-time join via join_asof backward).
2. Targets are built from strictly-future outcome timestamps and carry
   their resolution time; a split's training set excludes any sample whose
   target resolves after the test origin (purging), plus an embargo gap.
3. Every benchmark serializes its construction parameters, so a metric is
   meaningless without the benchmark hash it was computed on.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

import polars as pl


def pit_join(
    samples: pl.DataFrame,
    features: pl.DataFrame,
    on: str = "asof",
    published_col: str = "published_at",
    by: list[str] | None = None,
    tolerance: str | None = None,
) -> pl.DataFrame:
    """Point-in-time join: latest feature row published at-or-before `asof`.

    Refuses frames lacking the publication column — if a dataset has no
    publication timestamps, fix the ingestion, don't guess here.
    """
    if published_col not in features.columns:
        raise ValueError(
            f"features frame has no {published_col!r} column; point-in-time "
            "joins require publication timestamps (see inv-data-pipeline)"
        )
    samples = samples.sort(on)
    features = features.sort(published_col)
    return samples.join_asof(
        features,
        left_on=on,
        right_on=published_col,
        by=by,
        strategy="backward",
        tolerance=tolerance,
    )


@dataclass(frozen=True)
class Split:
    train_end: object  # datetime: last allowed target-resolution time in train
    test_start: object
    test_end: object


@dataclass
class Benchmark:
    """A frozen prediction task over a sample frame.

    sample frame columns (mandatory):
      asof         — when the prediction is made (datetime, UTC)
      resolve_at   — when the target becomes known (datetime, UTC, > asof)
      target       — the value to predict (known only at resolve_at)
    plus arbitrary feature columns, each joined via pit_join.
    """

    name: str
    samples: pl.DataFrame
    horizon_desc: str
    embargo_days: int = 0
    params: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        missing = {"asof", "resolve_at", "target"} - set(self.samples.columns)
        if missing:
            raise ValueError(f"benchmark samples missing columns: {sorted(missing)}")
        bad = self.samples.filter(pl.col("resolve_at") <= pl.col("asof"))
        if bad.height:
            raise ValueError(
                f"{bad.height} samples resolve at-or-before their asof time — "
                "the target would be known at prediction time (lookahead)"
            )
        self.samples = self.samples.sort("asof")

    def rolling_origin_splits(self, n_splits: int, min_train_frac: float = 0.3) -> list[Split]:
        """Expanding-window rolling-origin splits over asof time."""
        asof = self.samples.get_column("asof")
        t0, t1 = asof.min(), asof.max()
        span = t1 - t0
        splits: list[Split] = []
        for k in range(n_splits):
            frac_start = min_train_frac + (1 - min_train_frac) * k / n_splits
            frac_end = min_train_frac + (1 - min_train_frac) * (k + 1) / n_splits
            splits.append(
                Split(
                    train_end=t0 + span * frac_start,
                    test_start=t0 + span * frac_start,
                    test_end=t0 + span * frac_end,
                )
            )
        return splits

    def split_frames(self, split: Split) -> tuple[pl.DataFrame, pl.DataFrame]:
        """Materialize (train, test) with purging and embargo.

        Train keeps only samples whose targets have RESOLVED (and cleared
        the embargo) before the test origin — an unresolved label at the
        origin is information from the future.
        """
        embargo = pl.duration(days=self.embargo_days)
        train = self.samples.filter(
            (pl.col("resolve_at") + embargo) < split.test_start
        )
        test = self.samples.filter(
            (pl.col("asof") >= split.test_start) & (pl.col("asof") < split.test_end)
        )
        return train, test

    def fingerprint(self) -> str:
        """Hash of construction parameters + sample shape — metrics are
        reported alongside this so results are tied to an exact task."""
        payload = json.dumps(
            {
                "name": self.name,
                "horizon": self.horizon_desc,
                "embargo_days": self.embargo_days,
                "params": self.params,
                "n": self.samples.height,
                "columns": sorted(self.samples.columns),
                "asof_range": [str(self.samples["asof"].min()), str(self.samples["asof"].max())],
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


def evaluate(
    benchmark: Benchmark,
    fit_predict,
    n_splits: int = 5,
    feature_cols: list[str] | None = None,
) -> dict:
    """Walk-forward evaluation. `fit_predict(train_df, test_df) -> list[float]`.

    Returns per-split and pooled metrics (MAE, MAPE where target != 0,
    directional hit rate vs zero). Reports the benchmark fingerprint —
    a metric without its fingerprint is not a result.
    """
    rows = []
    for i, split in enumerate(benchmark.rolling_origin_splits(n_splits)):
        train, test = benchmark.split_frames(split)
        if train.is_empty() or test.is_empty():
            continue
        preds = list(fit_predict(train, test))
        if len(preds) != test.height:
            raise ValueError(f"split {i}: {len(preds)} preds for {test.height} samples")
        t = test.with_columns(pl.Series("pred", preds))
        err = (pl.col("pred") - pl.col("target")).abs()
        rows.append(
            t.select(
                pl.lit(i).alias("split"),
                err.mean().alias("mae"),
                (err / pl.col("target").abs()).filter(pl.col("target") != 0).mean().alias("mape"),
                ((pl.col("pred") * pl.col("target")) > 0).mean().alias("dir_hit"),
                pl.len().alias("n"),
            )
        )
    if not rows:
        raise ValueError("no evaluable splits — not enough resolved history")
    per_split = pl.concat(rows)
    pooled = per_split.select(
        pl.col("mae").mean(), pl.col("mape").mean(), pl.col("dir_hit").mean(), pl.col("n").sum()
    ).row(0, named=True)
    return {
        "benchmark": benchmark.name,
        "fingerprint": benchmark.fingerprint(),
        "pooled": pooled,
        "per_split": per_split.to_dicts(),
    }
