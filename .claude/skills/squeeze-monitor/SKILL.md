---
name: squeeze-monitor
description: Single-ticker short squeeze + gamma squeeze analysis and daily monitoring — short-cost-basis ladder from SI reporting periods, option chain OI/volume/P-C structure by expiry and strike, dealer gamma walls, institutional option positions from 13F, and a restrained quantitative estimate of squeeze fuel. Input is one ticker ("分析 XX 的轧空结构" / "监控 XX 的 squeeze"); outputs a crowding analysis plus an armed daily monitor.
---

# Squeeze Monitor (轧空/Gamma 挤压分析与监控)

Input: one US equity ticker (optionally a catalyst date, e.g. earnings). Two modes: **analyze**（一次性全量分析）and **monitor**（每日增量跟踪）。分析的灵魂是三件事：空头的**成本分布**（不是 SI 总量）、期权 OI 的**行权价结构**（不是总量）、以及**克制的量化估计**（14% SI 不是 40% 的史诗燃料，别吹）。

## Analyze 模式：六步流程

### 1. 底数 [filed]
`get_equity_fundamentals`（流通盘 float、总股本、ADV、52 周区间）+ `get_equity_historicals`（90 日日线，供第 3 步映射价区与计算 20 日 ADV）。

### 2. Short Interest 时间序列
WebSearch（`"<ticker>" short interest fintel OR marketbeat OR nasdaq`）取最近 ≥3 个 FINRA 结算日（每月两次，滞后 ~9 天）的 SI 股数。计算：SI% of float、days-to-cover = SI/ADV、期间增减。找 borrow fee/availability（fintel 口径）——fee 飙升 = 逼空的燃料门闩。

### 3. 空头成本分布（本 skill 的招牌，最重要的 nuance）
把每个 SI 报告期的 **ΔSI 映射到该期间的价格区间**（日线 high/low 包络）：

| 建仓窗口 | ΔSI（股） | 对应价区 | vs 现价盈亏 | 状态 |
|---|---:|---|---:|---|
| 例：6/13→6/30 | +160K | $96–115 | 现价$93.9 → 微浮盈 | 水线附近，不急 |
| 例：7/1→7/8 | +400K | $66–72 | **浮亏 30–40%** | 深度被套，必须决策 |

由此推导**两段式（或多段式）轧空剧本**：第一段 = 深亏 momentum 空头的被迫覆盖（触发条件：gap 不回补/放量突破近期高点）；第二段 = 主力空头的成本带被上穿（明确写出触发价，如"站上 $100 → 6 月 $96-115 建仓的全部转浮亏"），并给出第二段的目标参照（前高/52 周高点及距离%）。**注意**：SI 报告的滞后意味着最近 ~2 周的加减仓看不到——用期权 put 流量和 borrow fee 变化做代理，并明说这是代理。

### 4. 期权链结构扫描
Robinhood 三步：`get_option_chains` → 对最近 3-4 个到期日（周度优先 + catalyst 后首个到期）×现价 ±30% 的行权价 `get_option_instruments` → `get_option_quotes`（含 OI、volume、IV、delta、gamma）。产出：

- **P/C ratio**：分别按 OI 和按当日 volume、分到期日与总量（volume P/C 骤降 = 新增 call 投机流）
- **Call/Put 墙**：各到期日 OI 最大的行权价（call 墙 = 上方磁力位+做市商 gamma 翻转区；put 墙 = 下方支撑）
- **名义股数**：Σ(call OI)×100 vs float/股本——例：10.6 万张 ≈ 1,060 万股 notional 对 31.45M 股本"非常大"，写出这个比值
- **ITM call OI**：现价上穿后变 ITM 的 call 张数 → 做市商 delta 对冲的强制买盘估计（ΔOI×Δdelta×100）
- **Gamma 日历**：最近到期日的 gamma 托底何时到期（"周五到期前有天然 gamma 买盘"）、下一个行权价墙变 ATM 的续燃条件

### 5. 机构持仓拥挤度
- 13F 期权持仓：`mcp__FMP__form13F {endpoint:"positions-summary"}`（Ultimate 套餐；被挡则 WebSearch `"<ticker>" 13F put call institutional`）——找 Situational Awareness 类基金的集中 call/put 仓
- 机构持股%、内部人近期买卖（insiderTrades）、股东集中度——多头筹码锁定度决定可借券池
- 综合成 crowding 评分：多头拥挤（回调踩踏风险）vs 空头拥挤（squeeze 燃料）哪边更满

### 6. 量化估计（必须克制）
```
覆盖买盘 = SI × [1/3, 1/2]（未来 5 个交易日情景）
        → 每日增量 = 覆盖买盘/5 ÷ 20日ADV = 平均成交量的 X–Y%
gamma 对冲买盘 = ITM 化 call OI × delta 变化 × 100（事件情景下）
```
校准标尺（写进结论）：SI% of float **<10% = 低燃料**；**10-20% = 中等，值 +10~20% 的额外动能**；**>30% = 史诗级候选**。给出"squeeze 因素本身值多少额外上行"的区间估计和价格目标区，并明确它**不是**基本面观点。所有推导数字标 `[derived]`，情景假设标 `[assumed]`。

## Monitor 模式（每日）

`analyze` 完成后把状态存入 `reports/squeeze/<TICKER>/state.json`（SI 序列、成本分布表、关键行权价墙、触发价位），再建每日 trigger：

```
mcp__Claude_Code_Remote__create_trigger {
  name: "squeeze-monitor-<TICKER>",
  cron_expression: "40 13 * * 1-5",   # 9:40am ET 开盘后（EDT）
  prompt: "Run squeeze-monitor monitor mode for <TICKER>: reload state.json, pull
           spot/volume + option quotes for the tracked strikes + new SI if published,
           diff vs state, update state, and report ONLY the deltas per the skill's
           monitor checklist. Silent (no SendUserFile) if no trigger fires."
}
```

每日检查清单（只报变化，无变化则静默）：
1. **价格 vs 触发价位表**：上穿任一段空头成本带下沿 / call 墙 / gap 回补位 → 推送警报
2. **关键行权价 OI 变化**（OI 为 T+1 数据）：单日 OI +30% 或新墙形成 → 报
3. **volume P/C 骤变**（<0.5 或日环比减半）→ 报
4. **新 SI 数据发布日**（FINRA 双月周期）→ 重算成本分布表全表
5. **borrow fee/IV 异动**（fee 翻倍或 ATM IV 单日 +10 vol 点）→ 报
6. gamma 托底到期日当天 → 提醒"托底消失"
7. 触发推送时给一句话行动语境（"第一段剧本进行中/第二段触发价还差 X%"），不给建议

## 诚实与口径规则

- **数据滞后必须声明**：SI 滞后 ~9 天且双周一报；OI 是 T+1；13F 滞后 45 天。最近两周的空头行为只能从 borrow fee/期权流代理。
- **做市商仓位是推断不是观测**：gamma 墙分析假设 OI 净卖方为做市商——当大 OI 来自机构双向策略时会失真，写明此假设 `[assumed]`。
- 成本分布映射假设"期间 ΔSI 均匀分布于期间价区"——粗粒度近似，区间要给宽。
- 轧空分析≠看多论文：squeeze 是仓位力学，燃料烧完价格回到基本面。报告结尾必须有此句 + 非投资建议声明。
- Robinhood 期权链扫描控制在 ≤4 个到期日 × ≤20 个行权价（约 8-10 次 instruments/quotes 调用）；更宽的扫描用 subagent 分段拉取落盘。

## 与其他 skill 的衔接

- catalyst 日期（财报/Investor Day）用 **earnings-analysis** 查并把 implied move 纳入第 4 步
- 若 ticker 在 **fujimoto-intraday-signal** 清单内，monitor 警报与藤本信号互相引用（squeeze 触发 + 藤本锁利同时出现 = 冲突信号，如实并列）
- 报告呈现遵循 **quant-data-science** 规范（表格 + 一句话结论），数字带 `[filed]/[derived]/[assumed]` 标签
