---
name: supply-chain-bottleneck
description: Supply-chain bottleneck analysis and interactive deliverables — map a full industry chain (default: AI compute), locate the binding constraint, analyze pricing power and capacity-cycle economics (梭哈扩产 vs LTA锁价 vs 渠道囤货), and one-shot two signature artifacts, an interactive full-chain explorer and a century-of-bottlenecks supply-demand strategy game. Use for "瓶颈在哪/谁有定价权/产能周期" questions and "做一个产业链交互页面/供需博弈游戏" requests.
---

# Supply-Chain Bottleneck Analysis (供应链瓶颈分析)

Two modes: **analyze** a real chain with data, or **one-shot** an interactive artifact (chain explorer / bottleneck game). Both are built on the same economics.

## The analytical framework

1. **Map the chain as stages, not companies.** Default AI-compute chain:
   `电力/能源 → 土地/数据中心(冷却) → 上游设备(EUV光刻 ASML) → 晶圆代工(TSMC先进制程) → 存储(HBM: SK海力士/三星/MU) → 先进封装(CoWoS) → 加速器(NVDA/AMD/ASIC) → 整机/ODM(SMCI/Dell/鸿海) → 网络(AVGO/ANET/光模块) → 云(hyperscalers) → 模型 → 应用`
   Each stage: capacity, utilization, lead time, capex intensity, expansion lag (months to bring new capacity), # of credible suppliers.
2. **Locate the binding constraint.** At any moment ONE stage is binding (最紧的那一环定价). Evidence ranking: lead times stretching `[filed/news]` > price/ASP hikes sticking > take-or-pay LTAs being signed > customers prepaying/investing in suppliers > "sold out through 20XX" transcript language. Everything downstream of the bottleneck queues; everything upstream of it gets squeezed.
3. **Pricing power follows the constraint.** Margin pool migrates to the binding stage (2021 代工, 2023-24 CoWoS/HBM, 2025 电力/机柜?). Track gross-margin deltas per stage across quarters — the migration IS the investment signal.
4. **The three classic responses** (the game's strategy triangle) — each rational, each dangerous:
   - **梭哈扩产 (all-in expansion)**: capture share if demand holds; creates the next glut if everyone does it. Capacity arrives with lag L — the cobweb theorem: supply decided at today's price arrives into tomorrow's price.
   - **LTA 锁价 (long-term agreements / take-or-pay)**: buyer secures supply, seller secures utilization; whoever misjudges the cycle eats the writedown (LTA penalties, inventory reserves).
   - **渠道囤货 (hoarding / double-ordering)**: rational per-agent, catastrophic in aggregate — bullwhip: perceived demand = real demand + hoarding; when shortage breaks, orders vanish overnight (2022 消费芯片).
5. **Cycle diagnosis checklist**: is current demand real or double-ordered (compare sell-in vs sell-through, inventory days across the chain `[filed]`)? How much capacity is committed but not yet online (capex → capacity with stage-specific lag)? What does the bottleneck stage's OWN capex say (they expand into their monopoly = cycle top signal)?

## Data grounding (analyze mode)

| Question | Source |
|---|---|
| Capex trajectory per stage | `mcp__FMP__statements {endpoint:"cashflow-statement"}` capex, YoY, vs guidance in transcripts |
| Inventory/lead-time stress | inventory days from balance sheets across chain tiers; DSO/DPO shifts |
| Pricing power shift | gross-margin per stage by quarter (`metrics-ratios`); ASP commentary via **earnings-analysis** transcripts |
| LTA/prepay evidence | 10-K purchase-obligation footnotes, 8-Ks, press releases (WebFetch/`secFilings`) |
| Sold-out/expansion language | earnings transcripts, `mcp__FMP__news` press releases |
| Market pricing of the bottleneck | relative multiples along the chain (**sec-filing-fundamentals**) |

Tag everything `[filed]/[derived]/[assumed]`; capacity numbers are mostly `[assumed from news]` — say so. Present per **quant-data-science** conventions.

## One-shot deliverable A: AI 全产业链交互 (chain explorer)

Self-contained HTML artifact (Artifact tool; load `artifact-design` + `dataviz` first; no external assets — inline everything).

- **Layout**: chain stages as columns left→right (电力→…→应用), companies as nodes within each stage. One screen, horizontal scroll inside a container if needed.
- **Node data** (inline JSON): name, stage, capacity/share note, margin trend, bottleneck score 0–10, key customers/suppliers (edges), one-line thesis. Tag which figures are real vs illustrative.
- **Interactions**: click a node → side panel (details + upstream/downstream edges highlighted); bottleneck heat coloring toggle (score → color); a "constraint propagation" mode — click a stage to shade everything queued behind it; hover edges show what flows (wafers, HBM stacks, GPUs, $).
- **Header strip**: today's binding constraint + the 2–3 candidate next bottlenecks.
- Dark/light theme per Artifact rules; favicon 🔗 or ⚡.

## One-shot deliverable B: 百年瓶颈供需史 game (梭哈扩产 / LTA锁价 / 囤货)

Self-contained HTML game. The player runs a firm through historical bottleneck cycles; each turn choose among the three strategies (+观望). The engine makes the economics teach themselves:

- **Engine (per turn = quarter)**: demand = trend + shock; perceived demand = real + Σchannel hoarding (bullwhip); capacity arrives L turns after expansion is paid (cobweb); price = f(perceived demand / online capacity), sticky up, cliff down; LTA = locked price/volume with take-or-pay penalty if you walk; hoarding profits if shortage persists, forces markdowns when it breaks.
- **Levels = historical episodes** (each with its real resolution shown after play): 1970s 石油危机, 1988 & 1995 & 2017-18 DRAM 周期, 2000 光纤泡沫, 2020-22 集运费率, 2020-22 缺芯潮(双重下单), 2023-25 HBM/CoWoS. Level intro states what was knowable then (time discipline — the player decides with period information only).
- **Scoring**: through-cycle ROIC + survival (bankruptcy possible on leveraged 梭哈 into the glut), not peak-quarter profit — the whole point.
- **Endgame screen**: player's path vs the three pure strategies vs what the real firms did (三星 1990s 逆周期梭哈赢, 2018 囤货者被 2019 砸死, 长协锁价者 2023 吃掉 HBM 红利…), one paragraph each.
- AI opponents: 2–3 rival firms playing fixed archetypes so over-expansion gluts are endogenous.
- Keep it one file, playable in 5 minutes, numbers illustrative but mechanics real (label as 教学模拟, not history data).

## Cross-links

Chain analysis feeds **equity-research-report** (chapter 2.2 竞争格局 / risk matrix) and **market-daily-review** (半导体链全球联动的因果解释). Company-level verification of any bottleneck claim goes through **sec-filing-fundamentals**.
