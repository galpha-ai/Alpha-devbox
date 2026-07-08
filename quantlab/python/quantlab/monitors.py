"""Production live-monitoring runner.

Research data answers "what was true"; production monitoring answers "what
just changed". A Monitor is a small pure function over lake frames that
returns alert lines; the runner enforces freshness (STALE DATA beats a
wrong number) and appends alerts to research/events/log.md in the event
format the decision layer (agentic-investing skill) triages.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import polars as pl

from . import lake


@dataclass
class Monitor:
    name: str
    source: str
    dataset: str
    max_staleness_days: int
    # check(df) -> list of alert strings (empty = quiet)
    check: Callable[[pl.DataFrame], list[str]]


@dataclass
class MonitorResult:
    name: str
    status: str  # "ok" | "alert" | "stale" | "missing"
    alerts: list[str]


def run_monitors(
    monitors: list[Monitor],
    events_log: Path = Path("research/events/log.md"),
    today: dt.date | None = None,
    root: Path | None = None,
) -> list[MonitorResult]:
    today = today or dt.date.today()
    results: list[MonitorResult] = []
    for m in monitors:
        fresh = lake.freshness(m.source, m.dataset, root=root)
        if not fresh["exists"]:
            results.append(MonitorResult(m.name, "missing", [f"no data for {m.source}/{m.dataset}"]))
            continue
        age = (today - dt.date.fromisoformat(fresh["latest"])).days
        if age > m.max_staleness_days:
            results.append(
                MonitorResult(
                    m.name, "stale",
                    [f"STALE DATA: {m.source}/{m.dataset} latest={fresh['latest']} ({age}d old, "
                     f"max {m.max_staleness_days}d) — not computing on it"],
                )
            )
            continue
        alerts = m.check(lake.read(m.source, m.dataset, root=root))
        results.append(MonitorResult(m.name, "alert" if alerts else "ok", alerts))

    firing = [r for r in results if r.status in ("alert", "stale", "missing")]
    if firing:
        events_log.parent.mkdir(parents=True, exist_ok=True)
        with events_log.open("a") as fh:
            for r in firing:
                fh.write(f"\n## {today} monitor:{r.name} [{r.status}]\n")
                for a in r.alerts:
                    fh.write(f"- {a}\n")
                fh.write("Materiality: (triage me — decision layer)\n")
    return results


def svr_zscore_alert(symbols: list[str], z_thresh: float = 2.0, window: int = 60) -> Callable:
    """Example production check: Reg SHO short-volume-ratio z-score spike
    (see inv-short-interest: levels are meaningless, changes matter)."""

    def check(df: pl.DataFrame) -> list[str]:
        alerts = []
        for sym, sub in df.filter(pl.col("symbol").is_in(symbols)).group_by("symbol"):
            s = sub.sort("date").with_columns(
                (
                    (pl.col("short_volume_ratio") - pl.col("short_volume_ratio").rolling_mean(window))
                    / pl.col("short_volume_ratio").rolling_std(window)
                ).alias("z")
            )
            last = s.tail(1).row(0, named=True)
            if last["z"] is not None and abs(last["z"]) >= z_thresh:
                alerts.append(
                    f"{last['symbol']}: SVR z={last['z']:.2f} on {last['date']} "
                    f"(ratio {last['short_volume_ratio']:.2%})"
                )
        return alerts

    return check
