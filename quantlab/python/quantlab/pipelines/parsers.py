"""Raw-feed parsing: Rust-first with Python fallback.

The Rust binary (quantlab/rust, `ql-ingest`) is the low-latency path; the
Python parsers here are the readable reference. Both must produce identical
records on the golden fixtures under tests/fixtures/ — that cross-language
test is the acceptance gate for either implementation changing.
"""

from __future__ import annotations

import json
import shutil
import subprocess

import polars as pl

RUST_BIN = "ql-ingest"


def _rust(mode: str, raw: str) -> pl.DataFrame | None:
    exe = shutil.which(RUST_BIN)
    if not exe:
        return None
    proc = subprocess.run([exe, mode], input=raw, capture_output=True, text=True)
    if proc.returncode != 0:
        raise ValueError(f"{RUST_BIN} {mode}: {proc.stderr.strip()}")
    rows = [json.loads(line) for line in proc.stdout.splitlines() if line]
    return pl.DataFrame(rows)


def parse_regsho(raw: str) -> pl.DataFrame:
    """FINRA Reg SHO daily file → normalized frame (see rust regsho.rs)."""
    if (df := _rust("regsho", raw)) is not None:
        return df
    rows = []
    for i, line in enumerate(raw.splitlines()):
        line = line.strip()
        if not line or line.startswith("Date|"):
            continue
        f = line.split("|")
        if len(f) < 6:
            if len(f) == 1 and f[0].isdigit():
                continue  # trailer record count
            raise ValueError(f"line {i + 1}: expected 6 fields, got {len(f)}")
        if len(f[0]) != 8 or not f[0].isdigit():
            raise ValueError(f"line {i + 1}: bad date {f[0]!r}")
        short_v, total_v = int(f[2]), int(f[4])
        rows.append(
            {
                "date": f"{f[0][:4]}-{f[0][4:6]}-{f[0][6:]}",
                "symbol": f[1],
                "short_volume": short_v,
                "short_exempt_volume": int(f[3]),
                "total_volume": total_v,
                "markets": f[5],
                "short_volume_ratio": short_v / total_v if total_v else None,
            }
        )
    return pl.DataFrame(rows)


def parse_occ_symbol(sym: str) -> tuple[str, str, str, float]:
    """OCC contract symbol → (root, expiry YYYY-MM-DD, right, strike)."""
    if len(sym) < 16:
        raise ValueError(f"bad OCC symbol {sym!r}")
    head, strike_part = sym[:-8], sym[-8:]
    head, right = head[:-1], head[-1]
    root, date = head[:-6], head[-6:]
    if right not in ("C", "P") or not root or not date.isdigit() or not strike_part.isdigit():
        raise ValueError(f"bad OCC symbol {sym!r}")
    return root, f"20{date[:2]}-{date[2:4]}-{date[4:]}", right, int(strike_part) / 1000.0


def parse_cboe_chain(raw_json: str) -> pl.DataFrame:
    """CBOE delayed chain JSON → flat normalized frame (see rust cboe.rs).

    Reminder: `open_interest` in a snapshot is as of the PRIOR session's
    settlement; the lake write must set effective_date accordingly.
    """
    if (df := _rust("cboe-chain", raw_json)) is not None:
        return df
    doc = json.loads(raw_json)
    rows = []
    for i, o in enumerate(doc["data"]["options"]):
        root, expiry, right, strike = parse_occ_symbol(o["option"])
        bid, ask = o.get("bid"), o.get("ask")
        mid = (bid + ask) / 2 if bid is not None and ask is not None and ask >= bid > -1 and ask > 0 else None
        rows.append(
            {
                "underlying": doc["symbol"],
                "underlying_close": doc["data"].get("close"),
                "snapshot_ts": doc.get("timestamp"),
                "contract": o["option"],
                "expiry": expiry,
                "right": right,
                "strike": strike,
                "bid": bid,
                "ask": ask,
                "mid": mid,
                "iv": o.get("iv"),
                "open_interest": o.get("open_interest"),
                "volume": o.get("volume"),
                "delta": o.get("delta"),
                "gamma": o.get("gamma"),
            }
        )
    return pl.DataFrame(rows)
