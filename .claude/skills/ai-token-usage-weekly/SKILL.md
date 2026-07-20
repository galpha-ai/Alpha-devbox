---
name: ai-token-usage-weekly
description: Weekly AI monetization & token-usage monitor — track frontier-lab ARR estimates, model token usage and market share (OpenRouter/Vercel Gateway), SDK downloads, GPU rental prices, and AI datacenter buildout from ai.castoramoney.com and primary sources; snapshot locally, compute week-over-week deltas, and push a weekly brief. Run on a weekly trigger or on demand ("这周 AI token 用量怎么样").
---

# AI Token Usage & Monetization Weekly (AI 变现周报)

Tracks the AI monetization dashboard (https://ai.castoramoney.com/) plus its primary sources, and turns them into a WoW delta brief. The site shows current state; **trend claims require our own history** — every run snapshots to disk first, then compares against prior snapshots.

## Data sources (in priority order)

```
# 1. The tracker itself (all four panels)
WebFetch https://ai.castoramoney.com/          # ① Lab ARR 估算 ② Token 用量/份额
                                               # ③ GPU 租赁价格(Ornn OCPI) ④ 数据中心(Epoch+news)
# If the page is JS-rendered and WebFetch gets a shell, use agent-browser
# (open → snapshot → get text) to extract the numbers.

# 2. Primary cross-checks (use when the tracker is stale/unreachable, and to verify big moves)
WebFetch https://openrouter.ai/rankings        # model token share, top models
curl https://api.npmjs.org/downloads/point/last-week/@anthropic-ai/sdk   # SDK 下载 (同理
     openai, @google/genai, @anthropic-ai/claude-code)                   # developer-adoption proxy
WebSearch — GPU rental spot prices (H100/H200/B200 $/hr), datacenter announcements
mcp__FMP__news {endpoint:"search-stock-news", symbols:["NVDA","MSFT","GOOGL","AMZN","ORCL","VRT"]}
```

## Snapshot store (do this BEFORE writing the report)

Append one JSON per run: `reports/ai-weekly/snapshots/YYYY-MM-DD.json`

```json
{"date":"2026-07-13","arr":{"anthropic":66.5e9,"openai":46.2e9},
 "tokens_bday":{"claude-fable-5":..., "top_models":[{"model":"...","btokens_wk":...}]},
 "gateway_share":{"openrouter_total_bday":..., "vercel_top":[...]},
 "sdk_dl_7dma":{"anthropic":..., "openai":..., "gemini":...},
 "gpu_hr":{"h100_sxm":2.57,"h200":4.03,"b200":5.14,"a100":1.01,"rtx5090":0.51},
 "datacenter":{"sites":67,"it_power_gw":10.8,"h100_eq_m":10.2},
 "source_notes":"castoramoney as-of ...; openrouter cross-checked"}
```

WoW/MoM deltas come from diffing snapshots — never from memory of last week. First run has no baseline: report levels only and say so.

## Report template

```
# AI Token & Monetization Weekly — YYYY-MM-DD
主线: 一句话（谁的份额在涨、算力价格方向、本周最大单点事件）

#1 Lab 变现: | Lab | est. ARR | WoW | implied M/M growth |  ← Anthropic/OpenAI，
   标注这是 tracker 的估算口径 [derived-external]，不是财报数字
#2 Token 用量与份额: 总量 (OpenRouter B/day) WoW；Top 模型合计 tokens 表 +
   份额变动前 3/后 3；Vercel Gateway token 份额 vs $ 份额背离（贵的模型 $ 份额
   高于 token 份额 → 定价权信号）
#3 开发者采用: SDK 下载 7DMA WoW（npm，developer-adoption proxy，注明口径）
#4 算力价格: | GPU | $/hr | WoW |  ← H100/H200/B200/A100/5090；价格指数方向
   （降价 = 供给出清或需求转移，结合 #5 判断哪个）
#5 数据中心建设: sites/GW/H100-eq 变化 + 本周 3–5 条最重要 buildout 新闻（带来源）
#6 投资 read-across: 2–4 条，把上面信号映射到公开标的
   （token 增速 → 推理算力需求 → NVDA/网络/电力链；GPU 时租跌 → neocloud 毛利…）
   标注为推断
#7 异常与数据问题: 抓取失败的面板、口径变化、与 primary source 对不上的数字
```

## Rules

- **口径谨慎**: OpenRouter/Vercel Gateway 只是 routed 流量的样本，不等于全市场（大客户直连 API 不经过网关）；ARR 是第三方估算。每个数字带来源，read-across 明确标注为推断。
- **大变动先验证再报**: 份额单周 >5pp 或 GPU 价格 >15% 的跳变，先查是不是口径/抓取问题（cross-check primary source），确认后写进 #7 或正文。
- **推送纪律**: 无 baseline 或本周无显著变化（阈值：token 总量 WoW <±3%、份额变动 <1pp、GPU 价格 <±5%）时，报告压缩成 5 行摘要，不注水。

## Automation (weekly push)

```
mcp__Claude_Code_Remote__create_trigger {
  name: "ai-token-usage-weekly",
  cron_expression: "0 12 * * 1",   # 周一 8am ET (EDT)；EST 期间为 13:00 UTC
  prompt: "Run the ai-token-usage-weekly skill: snapshot first, then write
           reports/ai-weekly/YYYY-MM-DD.md with WoW deltas vs prior snapshots,
           and send it to me via SendUserFile."
}
```

Local CLI alternative: `CronCreate {cron: "0 8 * * 1", ...}`（会话内、7 天过期）。推送渠道：SendUserFile 为主；若 PushNotification 工具可用且本周有显著变化，同时推一条一句话摘要。

## Cross-links

Token/算力信号是 **market-daily-review** 主线和 **supply-chain-bottleneck**（算力链瓶颈迁移）的上游输入；对具体标的的深入验证走 **sec-filing-fundamentals** / **earnings-analysis**。
