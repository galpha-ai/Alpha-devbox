#!/usr/bin/env python3
"""Pass 2: adaptive percentile thresholds (急跌/急涨 = trailing 20-day P15/P85 of the
same session-segment's returns), same next-bar-open execution, 10bps round-trip."""
import json, sys, glob, math
from datetime import datetime, timedelta
from collections import defaultdict
sys.path.insert(0, '.')
from fujimoto_backtest import load_bars, build_days, atr_pct, ret, Book, first_after

def pctile(xs, q):
    if not xs: return None
    s = sorted(xs); i = max(0, min(len(s)-1, int(q*len(s))))
    return s[i]

def run(days):
    B = {k: Book(k) for k in [
        "R1p_早盘急跌买_持至收盘", "R1p_早盘急跌买_持1小时", "R1p_早盘急涨空_持至收盘",
        "R1pv_急跌买+量>1.5x中位", "R2p_午后急跌次晨买", "R2pc_午后急涨次日追多(反例)",
        "ONp_夜盘+盘前急跌开盘买", "ONp_夜盘急涨开盘空",
        "R5_阴线买入", "R5_阳线卖空", "R6_连跌3日买", "R6_连涨3日空",
        "基准_隔夜持有", "基准_日内持有(开盘买收盘卖)"]}
    m_hist, pm_hist, on_hist = [], [], []
    for i, d in enumerate(days):
        p = d["prev"]
        if p and p["early"]:
            m_hist.append(ret(p["early"][0]["o"], p["early"][-1]["c"]))
        if p and p["pm"]:
            pm_hist.append(ret(p["pm"][0]["o"], p["pm"][-1]["c"]))
        if p:
            pre_all = d["onite"] + d["pre"]
            if pre_all: on_hist.append(ret(p["c"], pre_all[-1]["c"]))
        if i < 21: continue
        a = atr_pct(days, i - 1)
        mlo, mhi = pctile(m_hist[-21:-1], 0.15), pctile(m_hist[-21:-1], 0.85)
        plo, phi = pctile(pm_hist[-21:-1], 0.15), pctile(pm_hist[-21:-1], 0.85)
        olo, ohi = pctile(on_hist[-21:-1], 0.15), pctile(on_hist[-21:-1], 0.85)
        # R1 早盘 (signal at 10:30, enter 10:35)
        if d["early"] and mlo is not None:
            m_ret = ret(d["early"][0]["o"], d["early"][-1]["c"])
            eb = first_after(d["reg"], 635); xb = first_after(d["reg"], 695)
            if eb:
                if m_ret <= mlo:
                    B["R1p_早盘急跌买_持至收盘"].add(ret(eb["o"], d["c"]), +1)
                    if xb: B["R1p_早盘急跌买_持1小时"].add(ret(eb["o"], xb["c"]), +1)
                    ev = sum(b["v"] for b in d["early"])
                    med = pctile([sum(b["v"] for b in days[j]["early"]) for j in range(max(0,i-20), i) if days[j]["early"]], 0.5)
                    if med and ev > 1.5 * med:
                        B["R1pv_急跌买+量>1.5x中位"].add(ret(eb["o"], d["c"]), +1)
                elif m_ret >= mhi:
                    B["R1p_早盘急涨空_持至收盘"].add(ret(eb["o"], d["c"]), -1)
        # R2 午后 -> 次晨
        if p and p["pm"] and plo is not None:
            pm_ret = ret(p["pm"][0]["o"], p["pm"][-1]["c"])
            xb = first_after(d["reg"], 630)
            if xb:
                if pm_ret <= plo: B["R2p_午后急跌次晨买"].add(ret(d["o"], xb["c"]), +1)
                elif pm_ret >= phi: B["R2pc_午后急涨次日追多(反例)"].add(ret(d["o"], xb["c"]), +1)
        # 夜盘
        pre_all = d["onite"] + d["pre"]
        if p and pre_all and olo is not None:
            on_ret = ret(p["c"], pre_all[-1]["c"])
            xb = first_after(d["reg"], 630)
            if xb:
                if on_ret <= olo: B["ONp_夜盘+盘前急跌开盘买"].add(ret(d["o"], xb["c"]), +1)
                elif on_ret >= ohi: B["ONp_夜盘急涨开盘空"].add(ret(d["o"], xb["c"]), -1)
        # R5/R6 same as pass1
        body = (p["c"] - p["o"]) / p["o"]
        if body < -0.15 * a: B["R5_阴线买入"].add(ret(d["o"], d["c"]), +1)
        elif body > 0.15 * a: B["R5_阳线卖空"].add(ret(d["o"], d["c"]), -1)
        streak = 0
        for j in range(i - 1, 0, -1):
            ch = days[j]["c"] - days[j-1]["c"]
            s = 1 if ch > 0 else -1 if ch < 0 else 0
            if streak == 0: streak = s
            elif s == (1 if streak > 0 else -1): streak += s
            else: break
        if streak <= -3: B["R6_连跌3日买"].add(ret(d["o"], d["c"]), +1)
        elif streak >= 3: B["R6_连涨3日空"].add(ret(d["o"], d["c"]), -1)
        B["基准_隔夜持有"].add(ret(p["c"], d["o"]), +1)
        B["基准_日内持有(开盘买收盘卖)"].add(ret(d["o"], d["c"]), +1)
    return B

days = build_days(load_bars(sorted(glob.glob(sys.argv[1]))))
print(f"days={len(days)} range={days[0]['date']}..{days[-1]['date']} buy&hold(from d22)={ (days[-1]['c']/days[21]['o']-1)*100:+.1f}%")
for cost, tag in [(0.0010, "含10bps成本"), (0.0, "零成本")]:
    print(f"\n### {tag}")
    print("| 策略 | n | 胜率 | 均次bps | 累计% | Sharpe~ |")
    print("|---|---:|---:|---:|---:|---:|")
    for k, b in run(days).items():
        s = b.stats(cost)
        if s: print(f"| {k} | {s['n']} | {s['hit']:.0%} | {s['avg_bps']:+.0f} | {s['total_pct']:+.1f} | {s['sharpe_like']:+.1f} |")
        else: print(f"| {k} | 0 | - | - | - | - |")
