#!/usr/bin/env python3
"""Fujimoto (藤本茂) 8-rule intraday direction scorer.

Usage: python signals.py input.json
Input JSON: {
  "<TICKER>": {
    "daily":      [{"date","open","high","low","close"} ...oldest->newest, >=15 bars for full scoring],
    "intraday30": [{"ts","open","high","low","close"} ...today's session 30-min bars] (optional),
    "prev_intraday30": [...yesterday's session bars] (optional),
    "premarket_mid": 123.45 (optional),
    "year_high": 999.0, "year_low": 100.0 (optional; else derived from daily)
  }, ...
}
Output: markdown table + JSON lines with per-rule votes, composite score, label.

Rules (votes in [-2,+2]; +=contrarian BUY bias, -=SELL/take-profit bias):
  R1 早盘急跌买/急涨卖    (needs intraday30)
  R2 午后急跌→次晨买; 午后急涨不追 (needs prev_intraday30 or intraday30 at close run)
  R3 动荡即休息            (chaos filter -> force WAIT)
  R4/R7 横盘/盘整期等待     (compression filter -> dampen votes)
  R5 阴线买阳线卖
  R6 连续同向 -> 逆向加码
  R8 高位盘整后跳涨 -> 锁定利润 (overrides compression damping)
Gap vote (premarket_mid vs prev close) applies R1 logic pre-open.
"""
import json, sys


def atr_pct(daily, n=14):
    trs = []
    for i in range(1, len(daily)):
        h, l, pc = daily[i]["high"], daily[i]["low"], daily[i - 1]["close"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)) / pc)
    if not trs:
        return 0.02
    return sum(trs[-n:]) / min(n, len(trs))


def score_ticker(d):
    daily = d.get("daily", [])
    votes, notes = {}, []
    if len(daily) < 3:
        return {"votes": {}, "score": 0, "label": "数据不足", "coverage": "none", "notes": ["<3 daily bars"]}
    a = atr_pct(daily)
    last, prev = daily[-1], daily[-2]

    # R5 阴线买入 阳线卖出 (most recent completed day)
    body = (last["close"] - last["open"]) / last["open"]
    if body < -0.15 * a:
        votes["R5阴阳线"] = 1
    elif body > 0.15 * a:
        votes["R5阴阳线"] = -1
    else:
        votes["R5阴阳线"] = 0

    # R6 连续同向 -> 逆向
    streak = 0
    for i in range(len(daily) - 1, 0, -1):
        ch = daily[i]["close"] - daily[i - 1]["close"]
        if streak == 0:
            streak = 1 if ch > 0 else -1 if ch < 0 else 0
        elif (ch > 0 and streak > 0) or (ch < 0 and streak < 0):
            streak += 1 if streak > 0 else -1
        else:
            break
    if streak <= -3:
        votes["R6逆向"] = 2 if streak <= -5 else 1
    elif streak >= 3:
        votes["R6逆向"] = -2 if streak >= 5 else -1
    else:
        votes["R6逆向"] = 0
    notes.append(f"连续{'涨' if streak>0 else '跌'}{abs(streak)}日" if abs(streak) >= 2 else "无连续行情")

    # R1 早盘急跌买/急涨卖 (intraday) or premarket gap proxy
    intr = d.get("intraday30") or []
    if len(intr) >= 2:
        o = intr[0]["open"]
        m_ret = (intr[1]["close"] - o) / o  # first ~60min
        if m_ret <= -1.0 * a:
            votes["R1早盘"] = 2
        elif m_ret <= -0.5 * a:
            votes["R1早盘"] = 1
        elif m_ret >= 1.0 * a:
            votes["R1早盘"] = -2
        elif m_ret >= 0.5 * a:
            votes["R1早盘"] = -1
        else:
            votes["R1早盘"] = 0
        notes.append(f"早盘60min {m_ret:+.1%} (ATR {a:.1%})")
    elif d.get("premarket_mid"):
        gap = (d["premarket_mid"] - last["close"]) / last["close"]
        if gap <= -0.8 * a:
            votes["R1缺口"] = 2
        elif gap <= -0.4 * a:
            votes["R1缺口"] = 1
        elif gap >= 0.8 * a:
            votes["R1缺口"] = -2
        elif gap >= 0.4 * a:
            votes["R1缺口"] = -1
        else:
            votes["R1缺口"] = 0
        notes.append(f"盘前缺口 {gap:+.1%}")

    # R2 午后急跌 -> 次晨买入候选; 午后急涨 -> 不追(剥离动量票)
    pintr = d.get("prev_intraday30") or (intr if len(intr) >= 8 else [])
    if len(pintr) >= 8:
        half = len(pintr) // 2
        pm_o = pintr[half]["open"]
        pm_ret = (pintr[-1]["close"] - pm_o) / pm_o
        if pm_ret <= -0.7 * a:
            votes["R2午后跌"] = 1
            notes.append(f"昨午后 {pm_ret:+.1%} -> 今晨候选买点")
        elif pm_ret >= 0.7 * a:
            votes["R2午后涨"] = 0
            notes.append(f"昨午后急涨 {pm_ret:+.1%} -> 不追")

    # R3 动荡休息: 大振幅 + 小实体 -> 强制观望
    rng = (last["high"] - last["low"]) / prev["close"]
    chaos = rng >= 2.2 * a and abs(last["close"] - last["open"]) < 0.3 * (last["high"] - last["low"])
    # R4/R7 横盘/盘整: 10日区间压缩 -> 等待
    win = daily[-10:]
    box = (max(x["high"] for x in win) - min(x["low"] for x in win)) / last["close"]
    compressed = len(daily) >= 10 and box < 1.6 * a

    # R8 高位盘整后跳涨 -> 锁利 (needs 52w context)
    yh = d.get("year_high") or max(x["high"] for x in daily)
    r8 = False
    if len(daily) >= 11 and last["close"] >= 0.90 * yh:
        prior_high = max(x["high"] for x in daily[-11:-1])
        pwin = daily[-11:-1]
        pbox = (max(x["high"] for x in pwin) - min(x["low"] for x in pwin)) / last["close"]
        if pbox < 2.0 * a and last["close"] > prior_high * (1 + 0.5 * a):
            votes["R8跳涨锁利"] = -2
            r8 = True
            notes.append("高位盘整后跳涨 -> 锁定利润")

    score = sum(votes.values())
    if chaos:
        label, score = "休息(R3动荡)", 0
    elif compressed and not r8:
        label = "等待(R4/R7盘整)"
        notes.append(f"10日箱体 {box:.1%} < 1.6xATR")
        score = 0
    elif score >= 2:
        label = "逆向买入倾向"
    elif score <= -2:
        label = "逆向卖出/锁利倾向"
    else:
        label = "观望"

    cov = "full" if intr else ("gap" if d.get("premarket_mid") else "daily-only")
    return {"votes": votes, "score": score, "label": label, "coverage": cov,
            "atr_pct": round(a, 4), "notes": notes}


def main():
    data = json.load(open(sys.argv[1]))
    rows = []
    for t, d in data.items():
        r = score_ticker(d)
        rows.append((t, r))
        print(json.dumps({"ticker": t, **r}, ensure_ascii=False))
    print("\n| 标的 | 信号 | 分值 | 触发规则 | 覆盖 |")
    print("| --- | --- | ---: | --- | --- |")
    for t, r in sorted(rows, key=lambda x: -abs(x[1]["score"])):
        fired = ", ".join(f"{k}{'+' if v>0 else ''}{v}" for k, v in r["votes"].items() if v) or "-"
        print(f"| {t} | {r['label']} | {r['score']:+d} | {fired} | {r['coverage']} |")


if __name__ == "__main__":
    main()
