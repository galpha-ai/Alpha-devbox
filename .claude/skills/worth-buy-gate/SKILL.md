---
name: worth-buy-gate
description: "现在能不能上车"参与时机评估 — 四层框架（alpha 加权评分 → 硬性风险否决 → 技术确认门槛 → 入场时机六分类）+ 新闻只降级不升级纪律 + 1R/2R/3R 交易计划。回答的是"此刻参与是否合适"，不是"这家公司好不好"。用于"XX 值得买吗/现在能上车吗/给我一个交易计划"类请求。方法论移植自 starriv/worth-buy-stocks，数据栈换为 FMP + Robinhood。
---

# Worth-Buy Gate（参与时机四层门）

**回答的问题**："现在参与合适吗？"——与 sec-filing-fundamentals（公司好不好）、equity-research-report（值多少钱）严格分工。一票的基本面再好，被否决门拦住就是"否"。

## 核心纪律（源方法论八条中保留的六条）

1. **脚本是唯一数字权威**：所有指标、评分、入场/止损价来自 `gate.py` 输出——报告中不得手算 MACD/RSI/KDJ，不得在 agent 间投票。脚本输出缺字段时写"无法确认"，不猜。
2. **新闻只降级不升级**：利好催化剂不加分。新闻风控分三档（LLM 层执行）：高危（造假/退市/持续经营疑问）→ 结论封顶"否"；中危（摊薄/诉讼/监管调查）→ "是"降"观察"；低危+利好 → 仅展示，不改分。
3. **确认类指标只做门槛不加分**：MACD/RSI/KDJ/量价 gate 入场，不进 alpha 分——动量分数与确认信号分离，防止指标堆叠自我强化。
4. **数据诚实**：日线 <120 根或核心价量缺失 → 输出"无法评分"，不给猜测性估计。
5. **只分析不交易**：本 skill 不下单（Robinhood 下单工具存在但不属于本 skill 的动作空间）。
6. **观察性输出**：与本套件其他 skill 一致，结论附非投资建议声明（此处有意偏离源仓库的"禁止免责声明"规则——本套件的既定纪律优先）。

## 四层结构

```
层1 Alpha 加权(0-100): momentum 55%（21日/63日收益 tanh 压缩）
                      + rel_strength 35%（vs SPY/QQQ 均值超额）
                      + efficiency 10%（63日净移动/路径比）
层2 硬否决(任一失败即封顶): SPY>200DMA regime 门 / 个股 50或200DMA 趋势门
                      / 63日相对强度>0 / 距30日高点≤15%
层3 确认门(≥3/4 通过): MACD hist 走强 / RSI 40-70 / KDJ 非高位钝化 / 上涨日量能
层4 时机六分类: pullback_reversal · recovery_reversal(试仓≤15%) · trend_continuation
              · pullback_no_trigger · overextended · trend_broken
结论: 是 / 观察 / 否 / 持仓需减风险 / 无法评分
```

## 执行流程

1. **拉数据**（≥300 交易日日线，含基准）：
   - 首选 `mcp__robinhood_MCP__get_equity_historicals {symbols:[T,"SPY","QQQ"], interval:"day", span:"year"}`
   - 备用 FMP `chart` endpoint（plan 允许时）；两源都不可用 → 无法评分
2. **组 JSON 喂脚本**：`python3 gate.py input.json`（格式见脚本头注释；bars 旧→新）
3. **新闻风控层**（脚本外，LLM 执行）：`mcp__FMP__news {endpoint:"search-stock-news"}` 近 14 天——按三档降级规则调整脚本结论，**只降不升**，写明降级原因与档位
4. **持仓者视角**（可选）：若用户已持仓且脚本结论为 否/trend_broken → 输出"持仓需减风险"而非"否"（增量 vs 存量的语义差）
5. **输出七节固定格式**：结论 / 关键证据 / 风控过滤表（8 行）/ 评分拆解 / 交易计划 / 新闻面风控 / 建议

### 8 行风控过滤表（固定行，不得省略合并）

| # | 过滤条件 | 内容来源 |
|---|---|---|
| 1 | 大盘 regime | 脚本 gates |
| 2 | 个股趋势门 | 脚本 gates |
| 3 | 相对强度 | 脚本 gates |
| 4 | 30日结构与追价位置 | 脚本 off_30d_high / ext_vs_20dma |
| 5 | 技术与量价确认 | 脚本 confirms |
| 6 | 流动性/数据质量 | bar 数、成交量水平 |
| 7 | 新闻/事件红旗 | LLM 新闻层（附来源） |
| 8 | 账户敞口 | 用户持仓（Robinhood get_equity_positions，用户授权时） |

## 交易计划规则

脚本给出 entry（现价）/ stop（10 日 swing low 与 2×ATR14 取高者）/ 1R/2R/3R 目标。纪律：**达 1R 后转保本+移动止损**；recovery_reversal 类试仓上限 15%；财报窗口内（用 earnings-analysis 查日期）计划降级为"事件后再评估"。

## 与其他 skill 的分工与衔接

- **fujimoto-intraday-signal**：藤本是日内逆向（接恐慌），本 skill 是波段趋势跟随（顺趋势）——两者结论相反时如实并列（"藤本 +2 逆向买 vs gate 否/trend_broken"是常见组合，语义：日内反弹可期但波段趋势未修复）
- **market-daily-review**：daily loop 发现的候选票用本 skill 做参与裁决
- **squeeze-monitor**：gate 否决但 squeeze 燃料满 → 标注"仓位行情，非趋势行情"
- **earnings-analysis**：财报日期查询 + 事件窗口降级
- **sec-filing-fundamentals / equity-research-report**：基本面与估值归它们；本 skill 不看估值（源方法论如此——估值不改变时机结论）

## 校准状态

阈值（tanh scale、追高 8%、深回撤 25%、确认门 3/4 等）为移植初始值，未在本套件数据上回测——参照 fujimoto 的流程：先累积每日样本，再用 equity-options-backtest 校准后调权。结论前先声明校准状态。
