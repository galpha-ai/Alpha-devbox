---
name: semis-weekly-watch
description: Weekly memory/HBM and CPU watchlist analysis using the supply-chain-bottleneck methodology — for SNDK/MU/SK海力士/Kioxia(285A)/三星 and AMD/Intel/ARM, track expansion risk, crash catalysts, melt-up catalysts, revenue updates, margin core signals, and next week's key dates. Run on a weekly trigger or on demand ("这周存储/CPU 什么情况").
---

# Semis Weekly Watch (存储/HBM + CPU 每周跟踪)

Weekly repeated analysis of two groups, applying the **supply-chain-bottleneck** framework (binding constraint, cobweb capacity lag, LTA coverage, bullwhip/double-ordering). Same six questions for every name, every week — the value is in the deltas.

## Universe

| Group | Tickers | Notes |
|---|---|---|
| 存储/HBM | MU, SNDK, 000660.KS (SK海力士), 285A.T (Kioxia), 005930.KS (三星电子) | SNDK↔Kioxia 共享 NAND 合资产能——两家的扩产决策要合并分析; 三星是 DRAM/NAND/HBM+代工混合体，只看存储分部 |
| CPU | AMD, INTC, ARM | AMD/ARM 是 AI 叙事 beta; INTC 要拆产品与代工两条线; ARM 看 royalty rate 与 v9/CSS 渗透 |
| Read-across (不单列，用于佐证) | NVDA (HBM 需求), WDC/STX (NAND/HDD 替代), TSM (CoWoS/代工), AVGO (定制ASIC vs CPU) | |

## The six questions (每票每周固定回答)

1. **扩产风险 (expansion risk)** — 本周有无新 capex/fab/wafer-start 信息？行业总供给弯曲点在哪（cobweb：今天宣布的产能 L 个季度后落地）？关键判别：是"瓶颈环节在自己垄断期扩产"（周期顶信号）还是"落后者追赶"（份额战信号）。存储组盯 HBM 转产对 commodity DRAM 供给的挤出；CPU 组盯 INTC 代工 capex 与 18A/14A 进度。
2. **暴跌 catalyst** — 下周~下季度可能触发 >10% 下跌的具体事件：库存天数拐头 `[filed]`、现货价跌破合约价、大客户砍单/资本开支下修、出口管制升级、HBM qualification 失败、财报 miss + 指引下修。每条给触发条件和可观察前兆，不写泛泛的"宏观风险"。
3. **暴涨 catalyst** — 对称地：涨价函/"sold out through 20XX"表述、新 LTA/预付款、HBM4 qual 通过、AI server 上修、竞对事故（断电/良率）。同样要可观察。
4. **正常 revenue update** — 下季度一致预期营收/EPS，本周有无 guidance/分析师上下修 `[derived]`；距离下次财报的天数。
5. **Profit margin 核心信息** — 毛利率方向与驱动拆解（存储: HBM 占比×HBM 溢价 + commodity ASP 方向 + 库存减值/回冲；AMD: DC GPU 占比与 MI 系列毛利爬坡；INTC: 产品毛利 vs 代工亏损收窄节奏；ARM: royalty rate 与授权收入节奏）。口径：non-GAAP GM，与上周结论的差异要点名。
6. **未来一周重要时间点** — 财报（含盘前/盘后与 implied move）、TrendForce/DRAMeXchange 价格数据发布、产业会议（SEMICON/CES/Computex）、竞对财报的 read-across 窗口、监管/出口管制节点、产品发布。列成带日期的表。

## Data sourcing

```
# 行情与 WoW（含海外票）
mcp__FMP__quote {endpoint:"batch-quote", symbols:["MU","SNDK","AMD","INTC","ARM","000660.KS","285A.T","005930.KS"]}

# 财报日历与预期
mcp__robinhood_MCP__get_earnings_results / get_earnings_calendar
mcp__FMP__calendar {endpoint:"earnings-company", symbol: ...}
mcp__FMP__analyst {endpoint:"financial-estimates"/"grades", symbol: ...}

# 事件与扩产信息
mcp__FMP__news {endpoint:"search-stock-news"/"search-press-releases", symbols:[...]}
WebSearch — DRAM/NAND 现货与合约价方向 (TrendForce/DRAMeXchange 周度报道)、
  HBM qual/涨价函传闻（标注为传闻+来源）、韩日媒体的海力士/Kioxia 扩产报道

# 库存/毛利 [filed]
mcp__FMP__statements {endpoint:"balance-sheet-statement"/"income-statement", period:"quarter"}
# 深挖用 earnings-analysis (transcript 语言) 和 sec-filing-fundamentals (10-Q 库存注记)
```

MCP 工具不可用时降级为 WebSearch + WebFetch（交易所/IR 页面），并在报告 #7 注明数据面板缺失。

## Snapshot & continuity

每次运行先落 `reports/semis-weekly/snapshots/YYYY-MM-DD.json`：每票收盘价、下季 cons rev/EPS、GM 预期、库存天数(最新季)、六问结论的一行摘要。WoW 对比来自历史 snapshot；**结论变化才是信号**——"扩产风险从低升到中，因为 X" 比重复静态描述有用。首次运行无 baseline，只报当前状态并说明。

## Report template

```
# 存储/CPU 每周跟踪 — YYYY-MM-DD
主线: 一句话（两组各自的边际变化 + 本周最大的单点信息）

#1 供需状态盘 (组级)
   存储: DRAM/NAND 现货 vs 合约价方向、HBM 占产能比、binding constraint 在哪一环
   CPU: server/client 需求方向、x86 vs ARM 份额边际、代工产能状态
#2 逐票六问表 (每票一节，六问各 1–3 行，标注 vs 上周的变化)
#3 本周价格行动: | 标的 | WoW | 催化剂 |  （催化剂诚实规则同 market-daily-review）
#4 未来一周时间点日历: | 日期 | 事件 | 影响标的 | 看点 |
#5 结论变化清单: 本周六问结论翻转/升降级的条目（这是给老读者的 diff）
#6 数据问题: 抓取失败/口径变化/传闻未证实项
```

## Rules

- 供应链纪律沿用 **supply-chain-bottleneck**：扩产信息区分"宣布产能"与"落地产能"（滞后 L 记清楚）；需求判断先排除双重下单（sell-in vs sell-through、链上库存天数）。
- Catalyst 必须可观察、可证伪（"如果 X 发生则 Y"），日期能定就定到周。
- 数字带 `[filed]/[derived]/[assumed]` 标签；现货价与传闻类必须给来源；分析非投资建议。

## Automation

```
mcp__Claude_Code_Remote__create_trigger {
  name: "semis-weekly-watch",
  cron_expression: "0 11 * * 1",   # 周一 7am ET (EDT)；EST 期间为 12:00 UTC
  prompt: "Run the semis-weekly-watch skill: snapshot first, write
           reports/semis-weekly/YYYY-MM-DD.md with WoW conclusion diffs,
           send via SendUserFile."
}
```

财报周加密：universe 内有票当周出财报时，在财报日 T-1 手动补跑一次该组（或用 earnings-analysis 做单票深挖）。
