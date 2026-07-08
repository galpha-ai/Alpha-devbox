"""Flow/tape footprint features from daily bars (see inv-flow-tape skill).

Input frame: columns [date, symbol, open, high, low, close, volume],
one row per symbol-day, date ascending. All features are trailing-only by
construction (rolling windows end at the current row) — safe for
publication-time joins with asof = date's session close.
"""

from __future__ import annotations

import polars as pl

TRADING_DAYS_60 = 60


def daily_flow_features(bars: pl.DataFrame, z_window: int = TRADING_DAYS_60) -> pl.DataFrame:
    required = {"date", "symbol", "open", "high", "low", "close", "volume"}
    missing = required - set(bars.columns)
    if missing:
        raise ValueError(f"bars missing columns: {sorted(missing)}")

    rng = pl.col("high") - pl.col("low")
    clv = (
        pl.when(rng > 0)
        .then(((pl.col("close") - pl.col("low")) - (pl.col("high") - pl.col("close"))) / rng)
        .otherwise(0.0)
    )
    ret = pl.col("close") / pl.col("close").shift(1).over("symbol") - 1

    df = bars.sort(["symbol", "date"]).with_columns(
        ret.alias("ret"),
        clv.alias("clv"),
        (
            (pl.col("volume") - pl.col("volume").rolling_mean(z_window).over("symbol"))
            / pl.col("volume").rolling_std(z_window).over("symbol")
        ).alias("volume_z"),
    )

    up_vol = pl.when(pl.col("ret") > 0).then(pl.col("volume")).otherwise(0)
    down_vol = pl.when(pl.col("ret") < 0).then(pl.col("volume")).otherwise(0)

    return df.with_columns(
        (up_vol.rolling_sum(20).over("symbol") / down_vol.rolling_sum(20).over("symbol"))
        .alias("updown_vol_ratio_20d"),
        pl.col("clv").rolling_mean(20).over("symbol").alias("clv_20d"),
        # OBV slope over 20d, volume-scaled.
        (pl.col("volume") * pl.col("ret").sign()).cum_sum().over("symbol").alias("obv"),
        # Amihud illiquidity: |ret| per dollar volume (scaled 1e9).
        ((pl.col("ret").abs() / (pl.col("close") * pl.col("volume"))) * 1e9)
        .rolling_mean(20)
        .over("symbol")
        .alias("amihud_20d"),
        _absorption_score().alias("absorption_5d"),
    )


def _absorption_score() -> pl.Expr:
    """Capitulation→absorption (the strongest bottoming footprint):
    high 5d volume with little downward price progress after a flush.
    Score = 5d volume z proxy × (1 - |5d price progress| / 5d path length).
    High when heavy volume produces no net downside — someone is absorbing.
    """
    vol5 = pl.col("volume").rolling_sum(5).over("symbol")
    vol5_base = pl.col("volume").rolling_sum(5).over("symbol").rolling_mean(60).over("symbol")
    progress = (pl.col("close") - pl.col("close").shift(5).over("symbol")).abs()
    path = (pl.col("close") - pl.col("close").shift(1).over("symbol")).abs().rolling_sum(5).over("symbol")
    stall = pl.when(path > 0).then(1 - progress / path).otherwise(0.0)
    return (vol5 / vol5_base) * stall
