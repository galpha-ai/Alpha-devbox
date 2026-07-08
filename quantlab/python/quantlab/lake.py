"""Hive-partitioned parquet lake with mandatory provenance sidecars.

Layout (see the inv-data-pipeline skill):
    <root>/<source>/<dataset>/dt=<YYYY-MM-DD>/part-0.parquet
    <root>/<source>/<dataset>/dt=<YYYY-MM-DD>/_meta.json

The lake refuses writes without provenance: `source_url`, `effective_date`
and `published_at` are required, because every downstream point-in-time
join depends on them. `_meta.json` is written last — its presence marks a
partition complete; readers skip incomplete partitions.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

import polars as pl

DEFAULT_ROOT = Path(os.environ.get("QUANTLAB_LAKE_ROOT", "/workspace/data"))


@dataclass(frozen=True)
class Provenance:
    source_url: str
    effective_date: str  # what period the data describes (YYYY-MM-DD)
    published_at: str    # when the market could know it (ISO timestamp)
    fetched_at: str = ""  # when we grabbed it; defaults to now (UTC)
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.fetched_at:
            object.__setattr__(
                self,
                "fetched_at",
                dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            )
        for field in ("source_url", "effective_date", "published_at"):
            if not getattr(self, field):
                raise ValueError(f"provenance field {field!r} is required")


def partition_dir(source: str, dataset: str, snapshot_date: str, root: Path | None = None) -> Path:
    return (root or DEFAULT_ROOT) / source / dataset / f"dt={snapshot_date}"


def write(
    df: pl.DataFrame,
    source: str,
    dataset: str,
    snapshot_date: str,
    provenance: Provenance,
    root: Path | None = None,
) -> Path:
    """Write one snapshot partition (idempotent: re-run replaces the same dt=)."""
    if df.is_empty():
        raise ValueError(
            f"refusing to write empty partition {source}/{dataset}/dt={snapshot_date}: "
            "a silent empty partition poisons every monitor downstream"
        )
    part = partition_dir(source, dataset, snapshot_date, root)
    part.mkdir(parents=True, exist_ok=True)
    meta_path = part / "_meta.json"
    meta_path.unlink(missing_ok=True)  # mark incomplete while rewriting
    df.write_parquet(part / "part-0.parquet")
    meta = asdict(provenance) | {"row_count": df.height, "snapshot_date": snapshot_date}
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    return part


def read(
    source: str,
    dataset: str,
    root: Path | None = None,
    with_provenance: bool = True,
) -> pl.DataFrame:
    """Read all complete partitions of a dataset, stamped with provenance.

    Adds columns: `snapshot_date`, and (if with_provenance) `published_at`
    parsed as a datetime — the join key for all point-in-time work.
    """
    base = (root or DEFAULT_ROOT) / source / dataset
    frames: list[pl.DataFrame] = []
    for part in sorted(base.glob("dt=*")):
        meta_path = part / "_meta.json"
        if not meta_path.exists():
            continue  # incomplete partition
        meta = json.loads(meta_path.read_text())
        df = pl.read_parquet(part / "part-0.parquet")
        df = df.with_columns(pl.lit(meta["snapshot_date"]).alias("snapshot_date"))
        if with_provenance:
            df = df.with_columns(
                pl.lit(meta["published_at"]).str.to_datetime(time_zone="UTC").alias("published_at")
            )
        frames.append(df)
    if not frames:
        raise FileNotFoundError(f"no complete partitions under {base}")
    return pl.concat(frames, how="vertical_relaxed")


def freshness(source: str, dataset: str, root: Path | None = None) -> dict:
    """Latest complete partition info — monitors must check this before
    computing, and report STALE DATA rather than compute on old partitions."""
    base = (root or DEFAULT_ROOT) / source / dataset
    parts = [p for p in sorted(base.glob("dt=*")) if (p / "_meta.json").exists()]
    if not parts:
        return {"exists": False}
    meta = json.loads((parts[-1] / "_meta.json").read_text())
    return {"exists": True, "latest": meta["snapshot_date"], "row_count": meta["row_count"],
            "fetched_at": meta["fetched_at"], "partitions": len(parts)}
