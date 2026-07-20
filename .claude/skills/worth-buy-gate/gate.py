#!/usr/bin/env python3
"""worth-buy-gate: 四层"现在能不能上车"评分器（移植自 starriv/worth-buy-stocks 方法论）

层1 Alpha 加权: momentum 55 / rel_strength 35 / efficiency 10 → 0-100 分
层2 风险否决: 大盘 regime(SPY vs 200DMA)、个股趋势门(50/200DMA)、相对强度、30日结构
层3 技术确认: MACD/RSI/KDJ/量价 —— 只做入场门槛，不加分
层4 入场时机: pullback_reversal / recovery_reversal / trend_continuation /
             pullback_no_trigger / overextended / trend_broken

原则（与源方法论一致）:
- 脚本是唯一数字权威，报告不得手算指标
- 新闻只降级不升级（新闻层在 LLM 侧执行，本脚本不处理）
- 核心数据缺失输出 无法评分，不猜测

Input(stdin 或 argv[1] JSON 文件):
{"tickers": {"AMD": {"daily": [{"date","open","high","low","close","volume"}, ... 旧→新]}},
 "benchmarks": {"SPY": {"daily":[...]}, "QQQ": {"daily":[...]}}}

Output: 每票 markdown 段落（结论/评分拆解/否决门/确认门/时机分类/交易计划）
"""
import json, sys, math

MIN_BARS = 120

def sma(xs, n):
    return [None]*(n-1) + [sum(xs[i-n+1:i+1])/n for i in range(n-1, len(xs))] if len(xs) >= n else [None]*len(xs)

def ema(xs, n):
    out, k, prev = [], 2/(n+1), None
    for x in xs:
        prev = x if prev is None else x*k + prev*(1-k)
        out.append(prev)
    return out

def macd(closes, fast=12, slow=26, sig=9):
    ef, es = ema(closes, fast), ema(closes, slow)
    line = [f-s for f, s in zip(ef, es)]
    signal = ema(line, sig)
    hist = [l-s for l, s in zip(line, signal)]
    return line, signal, hist

def rsi(closes, n=14):
    gains, losses, out = [], [], [None]
    for i in range(1, len(closes)):
        d = closes[i]-closes[i-1]
        gains.append(max(d, 0)); losses.append(max(-d, 0))
        if i < n: out.append(None); continue
        ag, al = sum(gains[-n:])/n, sum(losses[-n:])/n
        out.append(100.0 if al == 0 else 100 - 100/(1 + ag/al))
    return out

def kdj(highs, lows, closes, n=9):
    k, d, ks, ds, js = 50.0, 50.0, [], [], []
    for i in range(len(closes)):
        lo, hi = min(lows[max(0, i-n+1):i+1]), max(highs[max(0, i-n+1):i+1])
        rsv = 50.0 if hi == lo else (closes[i]-lo)/(hi-lo)*100
        k = 2/3*k + 1/3*rsv
        d = 2/3*d + 1/3*k
        ks.append(k); ds.append(d); js.append(3*k - 2*d)
    return ks, ds, js

def atr(highs, lows, closes, n=14):
    trs = [highs[0]-lows[0]]
    for i in range(1, len(closes)):
        trs.append(max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1])))
    return sum(trs[-n:])/n

def pct_ret(closes, n):
    return closes[-1]/closes[-1-n] - 1 if len(closes) > n else None

def squash(x, scale):
    """map return → 0..1 via tanh, scale = typical strong move"""
    return 0.5 + 0.5*math.tanh(x/scale) if x is not None else 0.5

def analyze(name, bars, spy, qqq):
    if len(bars) < MIN_BARS:
        return {"ticker": name, "verdict": "无法评分",
                "reason": f"日线仅 {len(bars)} 根 (<{MIN_BARS})，核心数据不足——不猜测"}
    c = [b["close"] for b in bars]; h = [b["high"] for b in bars]
    l = [b["low"] for b in bars]; v = [b.get("volume") or 0 for b in bars]

    # ---- 层1 Alpha ----
    mom = 0.6*squash(pct_ret(c, 21), 0.15) + 0.4*squash(pct_ret(c, 63), 0.30)
    spy_c = [b["close"] for b in spy]; qqq_c = [b["close"] for b in qqq]
    rs21 = (pct_ret(c, 21) or 0) - ((pct_ret(spy_c, 21) or 0) + (pct_ret(qqq_c, 21) or 0))/2
    rs63 = (pct_ret(c, 63) or 0) - ((pct_ret(spy_c, 63) or 0) + (pct_ret(qqq_c, 63) or 0))/2
    rs = 0.6*squash(rs21, 0.10) + 0.4*squash(rs63, 0.20)
    net = abs(c[-1]-c[-64]) if len(c) > 63 else abs(c[-1]-c[0])
    path = sum(abs(c[i]-c[i-1]) for i in range(max(1, len(c)-63), len(c)))
    eff = net/path if path > 0 else 0
    score = round(55*mom + 35*rs + 10*min(eff/0.5, 1.0), 1)

    # ---- 层2 否决门 ----
    ma20, ma50, ma200 = sma(c, 20)[-1], sma(c, 50)[-1], sma(c, 200)[-1]
    spy200 = sma(spy_c, 200)[-1]
    hi30 = max(c[-30:]); off_hi30 = c[-1]/hi30 - 1
    ext20 = c[-1]/ma20 - 1 if ma20 else 0
    gates = {
        "大盘 regime (SPY>200DMA)": spy_c[-1] > spy200 if spy200 else None,
        "个股趋势门 (close>50DMA 或 >200DMA)": (ma50 is not None and c[-1] > ma50) or (ma200 is not None and c[-1] > ma200),
        "相对强度 (63日超额>0)": rs63 > 0,
        "30日结构 (距30日高点≤15%)": off_hi30 >= -0.15,
    }
    veto = [k for k, ok in gates.items() if ok is False]

    # ---- 层3 确认门（只做门槛不加分）----
    _, _, hist = macd(c)
    r = rsi(c)[-1]
    ks, ds, js = kdj(h, l, c)
    vol20 = sum(v[-21:-1])/20 if len(v) > 21 and sum(v[-21:-1]) > 0 else None
    up_day = c[-1] >= c[-2]
    confirms = {
        "MACD hist 走强或>0": hist[-1] > hist[-2] or hist[-1] > 0,
        "RSI 在 40-70 参与区": r is not None and 40 <= r <= 70,
        "KDJ 非高位钝化 (K<80 或 K>D)": ks[-1] < 80 or ks[-1] > ds[-1],
        "量价 (上涨日量≥20日均量的80%)": True if vol20 is None else (not up_day or v[-1] >= 0.8*vol20),
    }
    confirmed = sum(1 for x in confirms.values() if x) >= 3

    # ---- 层4 时机分类 ----
    a = atr(h, l, c)
    deep_dd = c[-1]/max(c[-63:]) - 1 <= -0.25
    reversal_trigger = c[-1] > c[-2] and c[-1] > (h[-2] if len(h) > 1 else c[-1])  # 收复前日高点的简化触发
    if veto and "个股趋势门 (close>50DMA 或 >200DMA)" in veto and not deep_dd:
        timing = "trend_broken"
    elif deep_dd:
        timing = "recovery_reversal" if reversal_trigger and confirmed else "trend_broken"
    elif ext20 > 0.08 or (r is not None and r > 75):
        timing = "overextended"
    elif -0.08 <= off_hi30 < -0.02:
        timing = "pullback_reversal" if reversal_trigger and confirmed else "pullback_no_trigger"
    else:
        timing = "trend_continuation"

    # ---- 结论合成（脚本层；新闻降级在 LLM 层另行执行）----
    if veto:
        verdict = "否" if timing != "recovery_reversal" else "观察"
    elif timing in ("trend_continuation", "pullback_reversal") and confirmed and score >= 60:
        verdict = "是"
    elif timing == "overextended" and score >= 60:
        verdict = "观察"  # 分数够但追高——等回踩
    elif timing == "recovery_reversal":
        verdict = "观察"  # 深回撤反转：试仓≤15% 上限，按源规则归入观察+试仓注记
    else:
        verdict = "观察" if score >= 50 else "否"

    # ---- 交易计划 (1R/2R/3R) ----
    entry = c[-1]
    stop = max(min(l[-10:]), entry - 2*a)
    risk = entry - stop
    plan = None
    if risk > 0 and verdict in ("是", "观察"):
        plan = {"entry": round(entry, 2), "stop": round(stop, 2), "R": round(risk, 2),
                "T1(1R)": round(entry+risk, 2), "T2(2R)": round(entry+2*risk, 2),
                "T3(3R)": round(entry+3*risk, 2),
                "note": "达 1R 后转保本+移动止损" + ("；recovery_reversal 试仓≤15%" if timing == "recovery_reversal" else "")}

    return {"ticker": name, "verdict": verdict, "score": score,
            "breakdown": {"momentum(55)": round(55*mom, 1), "rel_strength(35)": round(35*rs, 1),
                          "efficiency(10)": round(10*min(eff/0.5, 1.0), 1)},
            "gates": gates, "veto": veto, "confirms": confirms, "confirmed": confirmed,
            "timing": timing, "rsi": round(r, 1) if r else None,
            "off_30d_high": f"{off_hi30:+.1%}", "ext_vs_20dma": f"{ext20:+.1%}",
            "plan": plan}

def main():
    data = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else json.load(sys.stdin)
    spy = data["benchmarks"]["SPY"]["daily"]; qqq = data["benchmarks"]["QQQ"]["daily"]
    for name, td in data["tickers"].items():
        res = analyze(name, td["daily"], spy, qqq)
        print(f"\n## {res['ticker']} — 结论: {res['verdict']}"
              + (f"（{res['score']}分, {res['timing']}）" if 'score' in res else ""))
        if res["verdict"] == "无法评分":
            print(f"- {res['reason']}"); continue
        b = res["breakdown"]
        print(f"- 评分拆解: momentum {b['momentum(55)']} + rel_strength {b['rel_strength(35)']}"
              f" + efficiency {b['efficiency(10)']} = {res['score']}")
        print(f"- 否决门: " + ("; ".join(f"{k}={'✓' if ok else '✗' if ok is False else '?'}"
                                for k, ok in res["gates"].items()))
              + (f" → **触发否决: {res['veto']}**" if res["veto"] else " → 全过"))
        print(f"- 确认门(只做门槛): " + "; ".join(f"{k}={'✓' if ok else '✗'}" for k, ok in res["confirms"].items())
              + f" → {'过' if res['confirmed'] else '不过'}")
        print(f"- 位置: 距30日高 {res['off_30d_high']}, 距20DMA {res['ext_vs_20dma']}, RSI {res['rsi']}")
        if res["plan"]:
            p = res["plan"]
            print(f"- 交易计划: entry {p['entry']} / stop {p['stop']} (R={p['R']}) /"
                  f" 1R {p['T1(1R)']} / 2R {p['T2(2R)']} / 3R {p['T3(3R)']} — {p['note']}")

if __name__ == "__main__":
    main()
