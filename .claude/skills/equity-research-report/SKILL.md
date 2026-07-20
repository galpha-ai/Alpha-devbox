---
name: equity-research-report
description: Produce a deep, buy-side-grade company research report (深度投资研究报告) — executive summary with dimension summaries, five deep-dive chapters, an investment recommendation with rating/target-price/monitoring signals, a ~40-topic appendix with quantified competitor benchmarks, and a mind-map whose leaves carry numeric conclusions. Orchestrates the sec-filing-fundamentals, earnings-analysis, equity-options-data, and quant-data-science skills into one deliverable.
---

# Deep Equity Research Report (深度投资研究报告)

The deliverable is one structured report on one company, following a fixed template (the format used for the Tesla/NVIDIA/Alibaba/PDD 深度投资研究报告 series): 摘要 → 五大深度章节 → 附录专题 → 思维导图. Everything obeys the discipline rules in **sec-filing-fundamentals** (mechanism decomposition, `[filed]/[derived]/[assumed]` tags, 口径 consistency, market-implied-expectation anchoring, time discipline).

Title format: `<Legal Name>（<中文名>公司）深度投资研究报告`, followed by a linked 目录.

## Scope tiers

| Tier | Content | When |
|---|---|---|
| Brief | 摘要 + 投资建议 only | "quick take" |
| Standard | 摘要 + 5 chapters + 10–15 appendix topics | "research report on X" |
| Deep | full template, 30–40 appendix topics | "深度/exhaustive report" |

## Template

```
1 摘要
  1.1 关键结论 — 5±1 bullets; each states a POSITION, not a topic
      (e.g. "AI基础设施领导地位不可撼动，但业务集中度风险显著")
  1.2 公司基本面与核心业务分析   ┐
  1.3 竞争环境深度分析           │ one-paragraph summaries
  1.4 财务表现与商业模型         │ of the chapters below
  1.5 行业趋势与战略风险         ┘
  1.6 投资建议 — rating + target + signals (see below)

2 各章节内容 (five deep chapters, each standalone)
  2.1 核心业务深度解析 — product system & tech architecture (revenue mix % by
      segment), market demand & growth drivers (quantified), pricing & cost structure
  2.2 市场竞争格局深度分析 — market share table with numbers per competitor,
      per-sub-market competitive dynamics, tech benchmarks vs rivals
  2.3 财务状况深度分析 — revenue-model evolution (one-time vs subscription vs
      usage-based, with unit prices), cost/expense structure, cash flow quality,
      R&D intensity & payback, shareholder structure
  2.4 行业趋势与战略风险深度分析 — TAM/CAGR with source, policy & regulation,
      disruption-risk matrix (see Risk matrix), geopolitical exposure
  2.5 公司治理与团队现状深度分析 — founder & key-executive backgrounds and how
      they shaped strategy, governance mechanisms, crisis history & responses,
      governance→financial-performance transmission channels

3 附录 (numbered deep-dive topics, self-contained)
思维导图 (mind-map of the whole report)
```

## 投资建议 (the actionable core — never skip)

Four mandatory elements:

1. **Rating**: 买入/增持/中性/减持 — stated once, defended by the disagreement with market-implied expectations, not by adjective stacking.
2. **Target price**: explicit arithmetic — either `multiple × year-N EPS` (e.g. "30× 2026E EPS $38.7 → $1,161, +25% vs current") or SOTP per-segment multiples (e.g. "核心电商 15× PE + 云 4.5× PS + 国际 2× PS → HK$120–150, 对应 2025年 20–25× PE"). Always a range or a sensitivity note; multiples tagged `[assumed]` with peer basis.
3. **关注信号 (monitoring signals)**: exactly 3–6 falsifiable metrics, each with current value, threshold, and which conclusion it validates/kills (e.g. "Blackwell 量产进度 / 中国区收入占比变化 / 软件收入增速"; "4680良率 65%→85%").
4. **风险提示**: top risks with the mechanism transmitting each to earnings.

## Risk matrix (chapter 2.4)

Disruption and policy risks as a probability × impact × response table — forces explicit `[assumed]` probabilities instead of vague "值得关注":

| 风险 | 概率 | 影响 | 应对/观察点 |
| --- | ---: | --- | --- |
| 量子计算突破 | ~15% `[assumed]` | 高 | 量子-经典混合计算研发 |
| CUDA生态被开源侵蚀 | ~25% `[assumed]` | 极高 | PyTorch/TensorFlow绑定深度 |

## 附录 topic taxonomy

Generate topics from what the chapters surfaced as load-bearing or contested, drawing from these five blocks (a Deep-tier report takes ~8 from each):

1. **产品与客户** — per-product-line market size/growth, pricing strategy & tier design, customer segments/geography, channel system, customer-acquisition cost trends, third-party satisfaction data
2. **竞争对标 (the signature block)** — head-to-head QUANTIFIED benchmarks: rival product specs & unit-economics (e.g. "AMD MI300 vs H100 单位算力成本定价差异"), ecosystem lock-in overlap (e.g. "CUDA vs ROCm 客户重叠度"), share evolution per sub-market, rival channel/pricing design. Every claim needs a number and a source tag
3. **财务专题** — specific-quarter cost/expense structure, margin YoY bridges, cash-flow changes, capex allocation, shareholder concentration, "背后逻辑" pieces reconciling divergences (revenue up / profit down)
4. **行业与监管** — market-size forecasts, regulator policy analyses, export/antitrust exposure, industry M&A and capital flows
5. **治理与组织** — founder education/career and its imprint on risk style, management team backgrounds, historical crises & responses, values/culture systems, org structure & reporting lines, KPI/incentive design

Each appendix item: the question → data pulled (tagged) → mechanism chain → one-line conclusion.

## 思维导图 (mind-map)

Mermaid mindmap mirroring the report tree. **Leaves must carry quantified conclusions, not topic labels** — "2024年AI芯片份额: NVIDIA 94.7%, Google 6.3%" not "市场份额分析"; "目标价: 30×2026E EPS → $1,161 (+25%)" not "估值建议". A reader should get the entire report's conclusions from the map alone.

## Section → source mapping

| Section | Skills / tools |
|---|---|
| Business, segments, pricing | **sec-filing-fundamentals** steps 1–3; `revenue-product-segmentation`; 10-K via EDGAR WebFetch |
| Competitive chapter + 对标 appendices | `mcp__FMP__company {endpoint:"peers"}` → same statement/metric pulls per rival; spec/price benchmarks from filings, press releases, `mcp__FMP__news`; unsourced share claims get `[assumed]` |
| Financial chapter | statements/ratios/scores/owner-earnings + red-flag checklist (**sec-filing-fundamentals**) |
| Earnings trajectory, guidance | **earnings-analysis** (point-in-time surprises, transcripts, implied vs realized move) |
| Industry & policy | news/press releases, filing risk factors, `mcp__FMP__economics`; growth numbers carry source tags |
| Governance/team | DEF 14A + 10-K via WebFetch, `company-executives`, `executive-compensation`, insider trades, 13F |
| Valuation & rating | **sec-filing-fundamentals** step 4 (DCF band + SOTP) closed against market-implied expectations |
| Price/volume context | **equity-options-data** bars + **quant-data-science** |

Gather in parallel (independent tool calls or one subagent per chapter), compose serially. For Deep tier, appendix topics also fan out well as subagents — give each the tagging rules and its exact question.

## Delivery

- One Markdown file `<TICKER>-research-report.md` (send via SendUserFile); optionally render an HTML Artifact for reading (load `artifact-design` first; charts follow `dataviz`).
- Front matter: data as-of date, quarters/filings used, and the analysis-not-investment-advice disclaimer.
- Every table carries `[filed]/[derived]/[assumed]` tags; a closing "数据缺口" section lists what was unobtainable and how it was bounded.
