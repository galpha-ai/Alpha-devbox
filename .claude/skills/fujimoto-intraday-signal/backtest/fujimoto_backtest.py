#!/usr/bin/env python3
"""Backtest Fujimoto's 8 principles on SNDK 5-min 24x5 bars (price+volume).

Input: JSONL files with {"ts","o","h","l","c","v","s"} 5-min bars (UTC, 24_5).
Sessions (ET): overnight 20:00(prev)-04:00, premarket 04:00-09:30,
regular 09:30-16:00 (早盘=09:30-10:30, 午后=13:00-16:00), after-hours 16:00-20:00.

Execution model (ported from trade-server discipline):
- signal at bar t -> enter at bar t+1 OPEN (next-bar-open, no lookahead)
- exits at fixed session times, same next-bar-open rule
- costs: 10 bps round-trip base case (5bps/side incl. spread), 0 bps shown for reference
- ATR14% from daily aggregates of regular-session bars; thresholds in ATR units
"""
import json, sys, glob, math
from datetime import datetime, timedelta, timezone
from collections import defaultdict

ET_OFFSET = -4  # EDT for Apr-Jul 2026

def load_bars(paths):
    bars = {}
    for p in paths:
        for line in open(p):
            b = json.loads(line)
            bars[b["ts"]] = b
    out = sorted(bars.values(), key=lambda x: x["ts"])
    for b in out:
        dt = datetime.fromisoformat(b["ts"].replace("Z", "+00:00")) + timedelta(hours=ET_OFFSET)
        b["et"] = dt
        b["date"] = dt.date() if dt.hour >= 4 else (dt - timedelta(hours=9)).date()  # trading date anchor 4am ET
        b["hm"] = dt.hour * 60 + dt.minute
    return out

def build_days(bars):
    """Group into trading days with session slices."""
    days = defaultdict(list)
    for b in bars:
        days[b["date"]].append(b)
    out = []
    for d in sorted(days):
        bs = days[d]
        reg = [b for b in bs if 570 <= b["hm"] < 960]   # 09:30-16:00
        if len(reg) < 30:
            continue
        early = [b for b in reg if b["hm"] < 630]        # 09:30-10:30
        pm    = [b for b in reg if b["hm"] >= 780]       # 13:00-16:00
        pre   = [b for b in bs if 240 <= b["hm"] < 570]  # 04:00-09:30
        ah    = [b for b in bs if 960 <= b["hm"] < 1200] # 16:00-20:00
        onite = [b for b in bs if b["hm"] < 240 or b["hm"] >= 1200]  # 20:00-04:00
        out.append({"date": d, "all": bs, "reg": reg, "early": early, "pm": pm,
                    "pre": pre, "ah": ah, "onite": onite,
                    "o": reg[0]["o"], "c": reg[-1]["c"],
                    "h": max(b["h"] for b in reg), "l": min(b["l"] for b in reg),
                    "vol": sum(b["v"] for b in reg)})
    for i, d in enumerate(out):
        d["prev"] = out[i - 1] if i > 0 else None
    return out

def atr_pct(days, i, n=14):
    lo = max(1, i - n)
    trs = []
    for j in range(lo, i + 1):
        pc = days[j - 1]["c"]
        trs.append(max(days[j]["h"] - days[j]["l"], abs(days[j]["h"] - pc), abs(days[j]["l"] - pc)) / pc)
    return sum(trs) / len(trs) if trs else 0.03

def ret(entry, exit_):
    return exit_ / entry - 1

class Book:
    def __init__(self, name):
        self.name, self.trades = name, []
    def add(self, r, side, tag=""):
        self.trades.append((r * side, tag))
    def stats(self, cost=0.0010):
        rs = [t[0] - cost for t in self.trades]
        if not rs:
            return None
        n = len(rs); tot = 1.0
        for r in rs: tot *= (1 + r)
        avg = sum(rs) / n
        hit = sum(1 for r in rs if r > 0) / n
        sd = (sum((r - avg) ** 2 for r in rs) / n) ** 0.5 if n > 1 else 0
        return {"n": n, "hit": hit, "avg_bps": avg * 1e4, "total_pct": (tot - 1) * 100,
                "sharpe_like": (avg / sd * math.sqrt(252)) if sd > 0 else 0}

def first_after(bars, hm):
    for b in bars:
        if b["hm"] >= hm:
            return b
    return None

def run(days):
    books = {k: Book(k) for k in
             ["R1_早盘急跌买(至收盘)", "R1_早盘急涨卖空(至收盘)", "R1v_急跌买+高量确认",
              "R2_午后急跌次晨买(至10:30)", "R2c_午后急涨次日追多(反例测试)",
              "R5_阴线买入(次日持有)", "R5_阳线卖空(次日持有)",
              "R6_连跌3日逆向买", "R6_连涨3日逆向空",
              "R8_高位盘整跳涨做空(3日)", "ON_夜盘急跌早盘买(至10:30)", "ON_隔夜持有基准(收盘买次晨卖)"]}
    filt = {"R3_动荡日的R1表现": Book("x"), "R3反_平稳日的R1表现": Book("x"),
            "R4_盘整期R5表现": Book("x"), "R4反_趋势期R5表现": Book("x")}
    hi52, streak = 0.0, 0
    for i, d in enumerate(days):
        if i < 15:
            hi52 = max(hi52, d["h"]); continue
        p = d["prev"]; a = atr_pct(days, i - 1)  # ATR as of prior day (no lookahead)
        hi52 = max(hi52, p["h"])
        # --- R1 早盘 ---
        if d["early"]:
            o = d["early"][0]["o"]; e_end = d["early"][-1]
            m_ret = ret(o, e_end["c"])
            entry_bar = first_after(d["reg"], 635)
            if entry_bar:
                chaos = (p["h"] - p["l"]) / p["c"] >= 2.2 * a and abs(p["c"] - p["o"]) < 0.3 * (p["h"] - p["l"] + 1e-9)
                if m_ret <= -1.0 * a:
                    r = ret(entry_bar["o"], d["c"])
                    books["R1_早盘急跌买(至收盘)"].add(r, +1)
                    (filt["R3_动荡日的R1表现"] if chaos else filt["R3反_平稳日的R1表现"]).add(r, +1)
                    early_vol = sum(b["v"] for b in d["early"])
                    med20 = sorted(sum(b["v"] for b in days[j]["early"]) for j in range(max(0, i-20), i) if days[j]["early"])
                    if med20 and early_vol > 1.5 * med20[len(med20)//2]:
                        books["R1v_急跌买+高量确认"].add(r, +1)
                if m_ret >= 1.0 * a:
                    books["R1_早盘急涨卖空(至收盘)"].add(ret(entry_bar["o"], d["c"]), -1)
        # --- R2 午后 -> 次日 ---
        if p and p["pm"]:
            pm_ret = ret(p["pm"][0]["o"], p["pm"][-1]["c"])
            exit_bar = first_after(d["reg"], 630)
            if exit_bar:
                if pm_ret <= -0.7 * a:
                    books["R2_午后急跌次晨买(至10:30)"].add(ret(d["o"], exit_bar["c"]), +1)
                if pm_ret >= 0.7 * a:
                    books["R2c_午后急涨次日追多(反例测试)"].add(ret(d["o"], exit_bar["c"]), +1)
        # --- R5 阴阳线 (次日 close->close, 用今日open入) ---
        body = (p["c"] - p["o"]) / p["o"]
        compressed = False
        if i >= 10:
            win = days[i-10:i]
            box = (max(x["h"] for x in win) - min(x["l"] for x in win)) / p["c"]
            compressed = box < 1.6 * a
        if body < -0.15 * a:
            r = ret(d["o"], d["c"])
            books["R5_阴线买入(次日持有)"].add(r, +1)
            (filt["R4_盘整期R5表现"] if compressed else filt["R4反_趋势期R5表现"]).add(r, +1)
        elif body > 0.15 * a:
            books["R5_阳线卖空(次日持有)"].add(ret(d["o"], d["c"]), -1)
        # --- R6 streak ---
        streak = 0
        for j in range(i - 1, 0, -1):
            ch = days[j]["c"] - days[j - 1]["c"]
            s = 1 if ch > 0 else -1 if ch < 0 else 0
            if streak == 0: streak = s
            elif s == (1 if streak > 0 else -1): streak += s
            else: break
        if streak <= -3:
            books["R6_连跌3日逆向买"].add(ret(d["o"], d["c"]), +1)
        elif streak >= 3:
            books["R6_连涨3日逆向空"].add(ret(d["o"], d["c"]), -1)
        # --- R8 高位盘整跳涨 -> 做空3日 ---
        if i >= 11 and p["c"] >= 0.9 * hi52:
            pwin = days[i-11:i-1]
            pbox = (max(x["h"] for x in pwin) - min(x["l"] for x in pwin)) / p["c"]
            prior_high = max(x["h"] for x in pwin)
            if pbox < 2.0 * a and p["c"] > prior_high * (1 + 0.5 * a):
                exit_i = min(i + 2, len(days) - 1)
                books["R8_高位盘整跳涨做空(3日)"].add(ret(d["o"], days[exit_i]["c"]), -1)
        # --- 夜盘扩展: 夜盘(20:00-04:00)+盘前 急跌 -> 开盘买 ---
        pre_all = d["onite"] + d["pre"]
        if pre_all and p:
            on_ret = ret(p["c"], pre_all[-1]["c"])
            exit_bar = first_after(d["reg"], 630)
            if on_ret <= -1.0 * a and exit_bar:
                books["ON_夜盘急跌早盘买(至10:30)"].add(ret(d["o"], exit_bar["c"]), +1)
        # 基准: 隔夜持有
        books["ON_隔夜持有基准(收盘买次晨卖)"].add(ret(p["c"], d["o"]), +1)
    return books, filt

def main():
    bars = load_bars(sorted(glob.glob(sys.argv[1])))
    days = build_days(bars)
    bh = (days[-1]["c"] / days[15]["o"] - 1) * 100
    print(f"bars={len(bars)} days={len(days)} range={days[0]['date']}..{days[-1]['date']}")
    print(f"buy&hold (from day16 open): {bh:+.1f}%  | 日均ATR≈{atr_pct(days, len(days)-1):.1%}\n")
    books, filt = run(days)
    hdr = "| 策略 | n | 胜率 | 均次(bps,含成本) | 累计% | 年化Sharpe~ |"
    print(hdr); print("|---|---:|---:|---:|---:|---:|")
    for k, b in books.items():
        s = b.stats()
        if s: print(f"| {k} | {s['n']} | {s['hit']:.0%} | {s['avg_bps']:+.0f} | {s['total_pct']:+.1f} | {s['sharpe_like']:+.1f} |")
        else: print(f"| {k} | 0 | - | - | - | - |")
    print("\n过滤器验证（R1/R5 在过滤器开/关状态下的表现差）:")
    for k, b in filt.items():
        s = b.stats()
        if s: print(f"  {k}: n={s['n']} 胜率{s['hit']:.0%} 均次{s['avg_bps']:+.0f}bps")
        else: print(f"  {k}: n=0")

if __name__ == "__main__":
    main()
