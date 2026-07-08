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

#1 市场概览
   主线: 2–3 句资金流向叙事
   | 指数 | 昨收 | 今收/现价 | 变动 |  ← S&P 500, NASDAQ, SOXX(半导体), VIX

#2 涨跌幅排行（watchlist 内）
   涨幅前 10–12: | 排名 | 标的 | 涨跌幅 | 收盘价 | 催化剂 |
   跌幅前 10–20: 同列。催化剂一列必须诚实：查不到就写"无明确催化剂"

#3 今日重大事件（5–8 条，按重要度排序）
   事件N - 一句话标题 [重要度 X/10]
   数据: 事实 + 数字 + 来源（CNBC/Bloomberg/8-K/公司PR，给出处）
   市场解读: 与数据分开写，是推断就说是推断

#4 板块逻辑（多空对照，2+2）
   视角 A/B - Bull: …（各一段，含关键数字）
   视角 C/D - Bear: …

#5 明日/今日关注点
   5–8 条 bullet：财报（含盘前/盘后）、宏观数据、国债拍卖、产业会议、
   期权到期、前日事件的后续确认点
```

## Data sourcing

```
# Indexes & VIX
mcp__FMP__indexes {endpoint: "index-quote", symbol: "^GSPC"}   # 同理 ^IXIC ^VIX
mcp__FMP__quote {endpoint: "batch-quote", symbols: ["SOXX","SMH","QQQ","SPY"]}

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
