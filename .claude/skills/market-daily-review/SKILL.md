---
name: market-daily-review
description: Generate a structured daily market review (每日复盘/盘前简报) for a sector watchlist (default TMT) — market overview with index table, gainers/losers ranking with catalysts, scored major events with sources, bull/bear sector logic, and next-session watch items. Designed to run automatically twice per trading day (9:00am ET pre-market, 3:30pm ET near close) via scheduled triggers, or on demand ("今天盘面复盘一下").
---

# Market Daily Review (每日复盘)

Produces the PODAAI-style TMT daily review: one screen that tells a portfolio manager what moved, why, and what to watch next. Two variants by time of day; the sector universe is configurable (default: TMT — semis, SaaS/大科技, AI infra; ~40 core tickers).

## Variants

| Run | Content basis |
|---|---|
| **9:00am ET 盘前简报** | Yesterday's close + overnight/pre-market: futures & index ETFs pre-market, aftermarket/pre-market movers, overnight news (Asia supply chain, 8-Ks, analyst actions), **今日关注点** (earnings after close, macro prints, Fed speakers) |
| **3:30pm ET 收盘前复盘** | Full intraday session (the example format): index moves, ranked gainers/losers with catalysts, scored events, bull/bear sector logic, **明日关注点** |

## Report template

```
# TMT 每日复盘 — YYYY年M月D日（周X）
北京时间 … / 美东时间 … | 数据来源: FMP + Robinhood + Web
大标题: 一句话主线（谁流入谁流出、什么叙事驱动）

#1 市场概览 + 全球指数联动
   主线: 2–3 句资金流向叙事（写清与昨日主线的延续/反转）
   全球联动表: | 地区 | 指数/标的 | 收盘 | 变动 | 备注 |
   ← 美股: S&P 500, NASDAQ, SOXX, VIX；亚洲半导体链: 韩国 KOSPI/SK海力士/
     三星, 日本 Nikkei/东京电子/Lasertec/Kioxia/软银, 台湾 TSMC, 中国 SMIC;
     欧洲: ASML。亚洲时段是美股半导体的前置信号——大跌/熔断要进重大事件

#2 涨跌幅排行（watchlist 内）
   涨幅前 10–12: | 排名 | 标的 | 涨跌幅 | 收盘价 | 催化剂 |
   跌幅前 10–20: 同列。催化剂一列必须诚实：查不到就写"无明确催化剂"
   盘后(AH)/盘前时段 Top 5–12: 财报日和大新闻日必列（batch-aftermarket-quote），
   注明是 AH/盘前价而非收盘价

#3 盘后财报与重磅活动专题（条件板块：watchlist 公司财报日/Investor Day 必写）
   每家一节：
   - 核心数字表: | 指标 | Actual | Cons | Beat/Miss | YoY/QoQ |
     ← 营收 / Non-GAAP EPS / 毛利率 / 分部收入（如 DRAM/NAND、数据中心）
   - 下季指引表: guide vs 一致预期（guide 比本季 beat/miss 更能定价）
   - 财报要点 + 电话会要点: 管理层原话加引号并标注（用 earnings-analysis skill
     拉 transcript；拿不到就用 PR/8-K 并注明）
   - 股价反应: AH 涨跌 + 时间线（盘中→AH→电话会后）
   - 对板块的传导 (read-across): 逐票列关联标的方向与逻辑
     （如 MU beat → SK海力士/三星/WDC/STX 存储链、AVGO HBM 配套…）

#4 今日重大事件（5–8 条，按重要度排序）
   事件N - 一句话标题 [重要度 X/10]
   数据: 事实 + 数字 + 来源（CNBC/Bloomberg/8-K/公司PR，给出处）
   市场解读: 与数据分开写，是推断就说是推断

#5 板块逻辑（多空对照，2+2）
   视角 A/B - Bull: …（各一段，含关键数字）
   视角 C/D - Bear: …

#6 藤本信号（固定板块）
   按 fujimoto-intraday-signal skill 对固定清单（SNDK/AMD/MRVL/INTC/TSM/
   2330.TW/000660.KS/285A.T/005930.KS）跑 signals.py，贴信号表：
   | 标的 | 信号 | 分值 | 触发规则 | 覆盖 | 距财报 |
   盘前变体给美股"今日开盘"信号（缺口代理）+ 亚洲票"下一交易日"信号；
   收盘变体用当日 30min 线复核早盘规则并生成明晨 R2 候选。
   与上次信号的翻转（如 买入倾向→锁利）单独点名。
   每次运行把各票当日 OHLC 追加到 reports/signals/history/<ticker>.jsonl
   （亚洲票历史积累的唯一来源，勿省略）。

#7 明日/今日关注点
   5–8 条 bullet：财报（含盘前/盘后）、宏观数据、国债拍卖、产业会议、
   期权到期、前日事件的后续确认点。
   明日有 watchlist 财报时写财报前瞻: 一致预期数字（营收/EPS/关键分部 cons）+
   市场关注的 2–3 个问题 + 期权隐含波动（earnings-analysis 的 implied move 流程）
```

## Data sourcing

```
# Indexes & VIX + 全球联动
mcp__FMP__indexes {endpoint: "index-quote", symbol: "^GSPC"}   # 同理 ^IXIC ^VIX ^KS11(KOSPI) ^N225(Nikkei) ^TWII(台湾加权)
mcp__FMP__quote {endpoint: "batch-quote", symbols: ["SOXX","SMH","QQQ","SPY"]}
# 亚欧个股用 ADR/美股代码: TSM ASML SONY，或当地代码 000660.KS(SK海力士)
# 005930.KS(三星) 8035.T(东京电子) 6920.T(Lasertec) 0981.HK(SMIC) 9984.T(软银)
mcp__FMP__quote {endpoint: "batch-quote", symbols: ["TSM","ASML","000660.KS","8035.T", ...]}

# Watchlist quotes + movers
mcp__FMP__quote {endpoint: "batch-quote", symbols: [<watchlist>]}      # 涨跌幅排行的原料
mcp__FMP__marketPerformance {endpoint: "biggest-gainers"}              # 市场级散点补充
mcp__FMP__marketPerformance {endpoint: "sector-performance-snapshot", date: "YYYY-MM-DD"}
mcp__FMP__quote {endpoint: "batch-aftermarket-quote", symbols: [...]}  # 盘前变体用

# Catalysts & events
mcp__FMP__news {endpoint: "search-stock-news", symbols: [<movers>], from_date: <today>}
mcp__FMP__news {endpoint: "search-press-releases", symbols: [<movers>]}
mcp__FMP__analyst {endpoint: "grades", symbol: <mover>}                # 评级变动是常见催化剂
WebSearch — 主线叙事与传闻类事件的交叉验证（必须拿到可引用来源）

# 关注点
mcp__robinhood_MCP__get_earnings_calendar {start_date: <today>, days: 3, filter: "high_market_cap"}
mcp__FMP__calendar {endpoint: "earnings-calendar", from_date: <today>, to_date: <+3d>}
mcp__FMP__economics — 宏观数据日历

# 开市判断（自动运行的第一步）
mcp__FMP__marketHours {endpoint: "exchange-market-hours", exchange: "NYSE"}
mcp__FMP__marketHours {endpoint: "holidays-by-exchange", exchange: "NYSE"}
```

Parallelize the pulls; movers → then news lookups only for the actual movers.

## Rules

- **催化剂诚实**: every mover needs a catalyst with a source, or the literal "无明确催化剂 / 板块联动". Never invent a reason to make the table look complete — an unexplained −8% IS information.
- **数据与解读分离**: 事件条目里"数据"只放可引用事实，"市场解读"明确是推断。传闻类（"据报道/独家"）标注为传闻并给来源。
- **重要度评分** (X/10): 8–10 = 改变板块叙事或指数级影响; 5–7 = 单一大票重定价; ≤4 = 噪音（一般不进前八）。
- **主线连续性**: read yesterday's review file first; 主线要写"延续/反转昨日什么"，避免每天孤立叙事。
- **口径**: 涨跌幅统一用当日 regular-session close-to-close（盘前变体注明是盘前价）；指数用指数本身，SOXX 用 ETF 并标注。
- This is a review, not advice — no position recommendations in this format.

## Automation (twice per trading day)

Every scheduled run starts with the market-open check; on holidays/weekends, end silently (no output, no file).

**Cloud session (claude-code-remote)** — durable, fires into the session:

```
mcp__Claude_Code_Remote__create_trigger {
  name: "market-review-premarket",
  cron_expression: "0 13 * * 1-5",   # 9:00am ET during EDT; 14:00 UTC during EST
  prompt: "Run the market-daily-review skill, 盘前简报 variant. First check NYSE
           is open today (holidays → end silently). Write the report to
           reports/daily/YYYY-MM-DD-premarket.md and send it to me."
}
mcp__Claude_Code_Remote__create_trigger {
  name: "market-review-close",
  cron_expression: "30 19 * * 1-5",  # 3:30pm ET during EDT; 20:30 UTC during EST
  prompt: "Run the market-daily-review skill, 收盘前复盘 variant. First check NYSE
           is open today (holidays → end silently). Compare 主线 vs this morning's
           premarket file. Write reports/daily/YYYY-MM-DD-close.md and send it to me."
}
```

Cron is UTC here — **re-arm at DST transitions** (Mar/Nov: shift both by 1 hour), or note the drift in the report header.

**Local CLI session** — `CronCreate {cron: "0 9 * * 1-5", ...}` and `{cron: "30 15 * * 1-5", ...}` (local-time cron, no UTC math), but jobs are session-only and auto-expire after 7 days — suited to a week of babysitting, not standing coverage.

**/loop** is interval-based, not wall-clock — don't use it for this; use it only for ad-hoc intraday polling ("watch semis every 30m until close").

## Delivery

- Save under `reports/daily/YYYY-MM-DD-{premarket|close}.md` (the close run reads the premarket file; tomorrow reads today's) and send via SendUserFile.
- Keep it one screen dense — the example fits ~8 events and 30 tickers; resist padding. If nothing happened (quiet summer Friday), say so in one line and keep the report short.
