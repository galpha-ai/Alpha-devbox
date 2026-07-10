---
name: fujimoto-intraday-signal
description: Quantified intraday direction signals from 藤本茂 (88-year-old Japanese day trader)'s 8 market principles — contrarian morning mean-reversion, afternoon-drop carry, chaos/consolidation filters, and post-consolidation breakout profit-taking — scored daily for the semis watchlist (SNDK/AMD/MRVL/SK海力士/Kioxia/三星/INTC/TSMC). Runs inside the market-daily-review loop or on demand ("今天藤本信号怎么样").
---

# 藤本茂八原则 → 量化日内方向信号

Converts the eight experience rules into deterministic votes computed by `signals.py` (this skill's directory). Character of the system: **逆向均值回归**（急跌买、急涨卖）+ **状态过滤**（动荡休息、盘整等待）+ **唯一的顺势例外**（高位盘整后跳涨 → 止盈）。信号是方向倾向，不是交易指令。

## 八条规则的量化定义

所有阈值以 **ATR14%**（14 日真实波幅/收盘价）为单位，跨标的可比：

| # | 原则 | 量化 | 票值 |
|---|---|---|---|
| 1 | 早盘急跌买入，急涨卖出 | 开盘后 60 分钟收益 ≤ -1.0×ATR → +2；≤ -0.5×ATR → +1；≥ +1.0×ATR → -2（对称）。盘前变体用缺口（盘前价/昨收-1，阈值 0.8/0.4×ATR）代理 | ±2 |
| 2 | 午后急涨不追；午后急跌次晨瞄准 | 昨日午后半场收益 ≤ -0.7×ATR → 今晨 +1（买入候选）；≥ +0.7×ATR → 剥离动量票（不加分，防追高） | +1/0 |
| 3 | 动荡时休息 | 昨日振幅 ≥ 2.2×ATR 且实体 < 30% 振幅（长上下影）→ **强制"休息"，总分清零** | 覆盖 |
| 4/7 | 横盘不动、盘整期等待 | 10 日箱体高度 < 1.6×ATR → **"等待"，总分清零**（除非 R8 触发） | 覆盖 |
| 5 | 阴线买入，阳线卖出 | 昨日实体 < -0.15×ATR（阴线）→ +1；阳线 → -1 | ±1 |
| 6 | 不随波逐流，始终逆向 | 连跌 3 日 → +1，连跌 5 日 → +2；连涨对称给负 | ±2 |
| 8 | 高位盘整后跳涨 → 锁定利润 | 收盘 ≥ 90% 年内高 且 前 10 日箱体 < 2.0×ATR 且 突破前箱体高点 > 0.5×ATR → **-2（止盈）**，可穿透盘整过滤 | -2 |

**合成**：分值 = Σ票值。≥ +2 = 逆向买入倾向；≤ -2 = 逆向卖出/锁利倾向；其间 = 观望；R3/R4 触发时强制休息/等待。

## 关注清单（固定）

| 标的 | 代码 | 数据源 | 覆盖档位 |
|---|---|---|---|
| Sandisk | SNDK | Robinhood 日线+30min | full |
| AMD | AMD | 同上 | full |
| Marvell | MRVL | 同上 | full |
| Intel | INTC | 同上 | full |
| 台积电 ADR | TSM | 同上 | full |
| 台积电 台股 | 2330.TW | FMP quote 快照 | daily-only |
| SK海力士 | 000660.KS | FMP quote 快照 | daily-only |
| SK海力士 美股 | （上市后补充；Barron's 7/9 报道正在推进美国上市，现有 OTC 无担保 ADR HXSCL 流动性差不用） | — | 待上市 |
| Kioxia | 285A.T | FMP quote 快照 | daily-only |
| 三星电子 | 005930.KS | FMP quote 快照 | daily-only |

## 执行流程（每次 daily loop 运行时）

1. **拉数据**：
   - 美股 5 票：`get_equity_historicals {interval:"day"}` 近 30+ 根日线；收盘复盘变体加 `{interval:"30minute", start_time:今晨}` 当日 30 分钟线（R1/R2 用）；盘前变体加 `batch-aftermarket-quote` 盘前中值（R1 缺口代理）。
   - 亚洲 4 票：`mcp__FMP__quote batch-quote` 取当日 OHLC 快照（FMP chart 历史被套餐限制）。
2. **积累历史**（亚洲票的关键）：把每票当日 `{date,open,high,low,close}` 追加到 `reports/signals/history/<ticker>.jsonl` ——loop 每天跑，两周后亚洲票的 ATR/连续日/箱体自动可算。历史不足时按 `coverage` 降档打分并在表格标注。
3. **跑脚本**：把数据整理成输入 JSON（格式见 signals.py docstring），`python .claude/skills/fujimoto-intraday-signal/signals.py input.json`，得到逐票信号表。
4. **写入复盘报告**：信号表进 market-daily-review 报告的"藤本信号"一节；与前一次信号的翻转（买入倾向→锁利）单独点名。

## 时区语义

- **9am ET 盘前跑**：美股票给"今日开盘"信号（缺口代理 R1 + 昨日 R2/R5/R6 + 过滤器）；亚洲票当天已收盘——给的是**今晚（下一交易日）**的信号，报告中注明。
- **3:30pm ET 收盘跑**：美股票用真实盘中 30min 线复核 R1（早盘急跌买了吗）并生成 R2（今日午后急跌 → 明晨候选）；亚洲票不变。

## 回测结论（SNDK 2026-04~07，5min 24×5，62 日——见 backtest/ 目录）

- **固定 ATR 阈值对高波动票（ATR>8%）失效**：改用滚动 20 日同时段收益的 **P15/P85 分位数**定义急跌/急涨（signals.py 的 ATR 阈值仅适用于常规波动票）。
- ✅ 成立：R1 早盘急跌买入**持至收盘**（+118bps/次，64%，n=11；只持 1 小时则无效）；R5 阴线买/阳线空（阳线空 +129bps 是最强项）；R6 逆向（n 太小仅供参考）。
- ❌ 证伪（本 regime）：早盘急涨**做空**（25% 胜率——原则里的"卖出"只能实现为持仓止盈，不能做空）；夜盘急跌开盘买（夜盘信息含量高，急跌不修复）；"午后急涨不追"（单边市里追多反而 +94bps）。
- 结构事实：SNDK 涨幅几乎全在隔夜（隔夜基准 +16.2% vs 日内基准 -5.7%）——日内均值回归系统的生存空间正来自于此。
- 局限：单票单 regime、n=4~19、多重检验偏差——扩票+拉长周期前，以上不构成权重依据。

## 纪律

- 这是**单一交易员经验规则的量化转写**，仅在 SNDK 单一 regime 上做过初步回测（见上节）——对其余 8 票用 backtest/ 脚本扩测（R1/R2 需 30min 或 5min 历史）再给权重。
- 每条触发规则在表格中透明列出（votes），不给黑箱结论；阈值（0.5/0.7/1.0/1.6/2.2×ATR）是初始参数 `[assumed]`，回测后校准。
- 藤本原则天然是逆向系统：在单边趋势市会持续逆势报错——R3/R4 过滤器就是他自己的解法（"动荡休息、盘整等待"），不要移除。
- 信号≠建议；财报日（用 **earnings-analysis** 查）前后 R1/R5 失效风险最高，报告需标注"X 天后财报"。
