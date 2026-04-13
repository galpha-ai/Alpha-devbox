---
name: chart-markdown
description: Emit compact structured Markdown that better-markdown can turn into charts. Use for comparisons, trends, rankings, scenarios, readiness tables, and backtest parameter summaries.
---

# chart-markdown

When a chart materially helps, answer in plain Markdown with this shape:

1. `## Headline` — one sentence
2. short bullets or one short paragraph
3. one compact numeric GFM table
4. `## Bottom line` — one sentence

## Rules

- Use plain Markdown only.
- Prefer one numeric table over many tables.
- Keep the first column categorical or time-like.
- Keep value columns numeric.
- Do not wrap the table in code fences.
- Do not emit JSON, HTML, XML, or custom components.
- If there is no real numeric data, use a readiness/blocker table instead of forcing a chart.

## Good table shapes

### Trend / time series

| Date | Base | Bull | Bear |
| --- | ---: | ---: | ---: |
| 2026-04-01 | 42 | 55 | 31 |
| 2026-04-02 | 44 | 57 | 30 |

### Ranking / comparison

| Segment | Score | Cost |
| --- | ---: | ---: |
| Moderate favorites | 72 | 18 |
| Heavy favorites | 61 | 25 |
| Small favorites | 44 | 12 |

### Readiness / blocker

| Item | Status | Impact |
| --- | --- | --- |
| NBA odds feed | Missing | Cannot backtest |
| Historical win prob series | Missing | Cannot validate exits |

## Default heuristic

- Comparison / ranking / scenarios → emit one numeric table
- Backtest / strategy questions → emit parameter table or scenario table
- Missing data → emit readiness table
- Simple explanation → prose only
