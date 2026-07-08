# An Agentic Investing System as a Semi-Verifiable Environment for Training Agentic Intelligence

*Alpha-devbox project — system whitepaper (blueprint edition)*
*Draft, 2026-07. This document describes the designed system: the devbox agent platform, the agentic-investing skill suite (`agentic-investing`, `inv-*`), and the quantlab engineering layer. Where the built system and this blueprint diverge, the blueprint is the acceptance test.*

---

## Abstract

Reinforcement of agentic intelligence has so far concentrated at two poles: fully verifiable environments (mathematics, competitive programming, unit-tested software), where reward is exact but the task distribution is narrow; and unverifiable open-ended tasks (research assistance, writing), where the task distribution is rich but the grading signal is a preference model. We argue that **discretionary investing, instrumented correctly, is a semi-verifiable environment** occupying the useful middle: an open-world task stream (corporate events, filings, supply-chain shocks) whose intermediate products — timestamped, falsifiable forecasts of revenue, EPS, short interest, and option open-interest migration — resolve against public ground truth on a known calendar. We describe a working system built on this thesis: a persistent, container-hosted agent that runs a 13-step cognition loop over public market data, maintains an append-only research state (beliefs, decisions, calibration files, postmortems), and is engineered so that every conclusion is computed from a point-in-time-honest data lake rather than asserted. The system is simultaneously a research instrument and a training environment: its calibration files and process-lesson journals constitute a dense, delayed, but *objective* reward channel for capabilities that current benchmarks cannot exercise — event world-modeling, continual learning across months, taste in question generation, and allocation of finite research compute under uncertainty. We detail the environment design (Sections 2–3), the two-system architecture separating research-data construction from production monitoring (Section 4), the data and model layers (Sections 5–6), the multi-agent hierarchy and its engineering discipline (Sections 7–8), the training-signal construction (Section 9), and the honest limitations of grading an agent with free public data (Section 10).

---

## 1. Introduction

The system described here is not a trading bot and not a chat assistant with market-data tools. It is a **discretionary investor implemented as an agent harness**: a long-lived process that observes events, decides what is worth researching, executes that research against downloaded primary data, commits to falsifiable intermediate predictions before outcomes are known, and grades itself when the outcomes print.

Two claims motivate the design:

1. **As an investing method**: discretionary judgment fails not for lack of ideas but for lack of a workflow that makes views repeatable, falsifiable, and cumulative. Quant firms solved this for systematic strategies; nobody has packaged the equivalent discipline for event-driven, catalyst-based, single-name research. The system gives discretionary research a quant-grade harness — point-in-time data, purged validation, calibration files — without pretending the underlying decisions are systematizable.

2. **As an ML research direction**: the environment is a candidate answer to the question "what should agents train on after verifiable-reward tasks saturate?" It is open-world, non-stationary, adversarial (the market prices in whatever is easy), and yet produces objective scalar grades on a weekly-to-quarterly cadence. The rest of this paper elaborates why that combination is rare and valuable.

The platform substrate is the devbox agent: a controller/runner architecture that hosts persistent Claude-Code-SDK sessions in containers, with bind-mounted workspaces that survive container restarts, a filesystem IPC layer, and a scheduler for recurring triggers (`docs/architecture.md`). Everything below runs inside that substrate; the substrate itself is investing-agnostic.

Contributions, in the order the paper presents them:

1. A characterization of instrumented discretionary investing as a *semi-verifiable environment*, and a commitment device — timestamped intermediate-dimension forecasts graded by calibration files — that makes the environment's reward objective (Section 2).
2. A cognition-loop formulation of the discretionary research process with explicit stage disciplines, stopping conditions, and self-improvement channels (Section 3).
3. A two-system architecture that reproduces, at agent scale, the research-data vs production-monitoring split of institutional quant practice, with point-in-time correctness obtained *by construction* from live snapshotting rather than by reconciliation of purchased history (Sections 4–5).
4. A model-layer doctrine — baselines first, foundation models as priors with receipts, Box's-loop criticism over every model, and a fully verifiable option-pricing island with mandatory verification blocks (Section 6).
5. A document-mediated multi-agent hierarchy with adversarial verification, and an engineering policy (asymmetric-literacy code ownership under golden-fixture contracts) for agent-maintained polyglot code (Sections 7–8).
6. An argument for what this environment could measure and train that current benchmarks cannot, together with an honest account of its limits (Sections 9–10).

---

## 2. The Semi-Verifiable Environment Thesis

### 2.1 The verification spectrum

| Environment class | Task distribution | Grading | Examples |
|---|---|---|---|
| Fully verifiable | Narrow, stationary | Exact, immediate | Math proofs, unit-tested code, games |
| **Semi-verifiable** | **Open-world, non-stationary** | **Objective but delayed, noisy, partial** | **Intermediate-dimension investing forecasts** |
| Unverifiable | Open-world | Preference models, human raters | Open-ended writing, advice |

Fully verifiable environments give clean reward but cannot teach world-modeling of an open economy, because the world is not in the loop. Unverifiable environments have the world in the loop but grade with a proxy that is itself learned, inviting reward hacking at the exact frontier we care about. Discretionary investing, naively formulated ("predict the price"), is nearly unverifiable at the single-decision level: prices are noisy, attribution is confounded, and a bad process wins often enough to corrupt any per-trade signal.

### 2.2 The commitment device: predict intermediate dimensions, not prices

The system's core methodological commitment converts investing into a semi-verifiable task:

> **Do not predict price. Predict the intermediate dimensions** — next quarter's revenue by segment, EPS change, margin trajectory, short-interest trajectory, option open-interest migration — **and derive price views from (intermediate outcome) × (what is priced in).**

Intermediate dimensions have three properties price predictions lack:

- **A print date.** Revenue resolves at earnings; TWSE monthly sales resolve on ~the 10th of each month; FINRA short interest resolves on a published dissemination calendar. The environment's reward schedule is literally published in advance.
- **Attributability.** A revenue forecast decomposed over a driver tree (Section 6) fails at a *node*; the postmortem can say "the ASP lag assumption was wrong," which is a gradient. A price forecast fails as a scalar; there is nothing to update.
- **Insulation from reflexivity.** The market does not adjust a company's actual quarterly revenue in response to the agent's forecast of it.

Operationally the commitment is enforced by **calibration files** (`research/calibration/<entity>.md`, append-only): before each print, the agent records its point + 80% interval per segment, the measured consensus/guidance/whisper snapshot, and which driver-tree node carries its disagreement; after the print, the actual, the error, the directional hit vs consensus, and *which node was wrong*. Quarterly, MAPE and hit rates are computed per entity and per node type. A forecaster that does not know its own calibration is a pundit; here, not knowing is structurally impossible, because the grading is a standing pipeline, not a virtue.

"Semi"-verifiable is honest: the grades are delayed (days to a quarter), the sample is small (a covered name yields four revenue prints a year), the environment is non-stationary, and part of the loop — question taste, sizing judgment — is graded only indirectly through decision postmortems. Section 9 argues this partiality is a feature for training, not merely a defect.

---

## 3. The Cognition Loop

The agent's outer loop, from `container/skills/agentic-investing/SKILL.md`, is thirteen steps:

```
observe event → generate questions → decompose uncertainty → identify key drivers
→ collect information → weight evidence → subtract noise → form belief
→ run scenarios → decide action / no action → track outcome
→ update world model → improve research process
```

Three structural points distinguish this from a prompt-response pattern.

**Event-triggered, not turn-based.** Inputs arrive from monitors (scheduled data pulls that diff lake partitions and append alerts to `research/events/log.md`), filings, price moves, and the user. Stage 1 is *triage*, not obedience: state what changed in one sentence with no adjectives, test materiality against held beliefs, map second-order effects through the strategy map's supply-chain edges (an HBM capacity announcement is a NAND supply event two steps removed), and be willing to write "noise" and stop. Every WAIT decision must register a monitor — a wait without a monitor is a forgotten decision.

**Two personas, worn in sequence.** Each serious task passes through (1) a *mid-frequency quant researcher* — point-in-time datasets, z-scores, event studies with matched controls, walk-forward validation; owner of the data layer — and (2) a *deep fundamental researcher* — revenue driver trees, supply-chain read-across, base rates, "what is the market mispricing and how do I know what the market believes"; owner of the judgment layer. The named failure mode is persona 2 writing narrative without persona 1's data, or persona 1 producing dashboards without persona 2's question. Each loop iteration alternates: question → data → updated question.

**The loop closes on itself.** Steps 11–13 are first-class: postmortems separate decision quality from outcome quality; entity lessons update `beliefs/`; process lessons accumulate in `process/lessons.md` (skimmed at session start as standing corrections); monitors that fire only noise for three months are deleted, in writing. The loop must improve the loop — including its own data pipelines and its own question taste. This is the continual-learning channel (Section 9).

The stages carry specific, checkable disciplines rather than exhortations:

| Stage(s) | Governing discipline |
|---|---|
| Observe / triage | One-sentence statement of what changed, no adjectives; materiality test against held beliefs; second-order map via strategy-map edges; cross-check the headline against positioning (the same news means opposite things at 2% vs 25% short interest); "noise" is a legitimate and common verdict |
| Generate questions | Rank candidates by value-of-information × resolvability and **cut** the rest in writing; a mispricing claim must cite a *measured* market belief — consensus estimates, the option-implied distribution, or positioning — or "it is a mood" |
| Decompose / key drivers | Decompose along supply chain, demand, competition, margin structure, policy, positioning, expectation — until parts are *checkable* (a part is checkable when a specific dataset can confirm or deny it); then subtract back to the 1–3 drivers that dominate |
| Collect | Read the positioning cube fast-to-slow; run the fundamental stack (filings → segment tree → drivers → projection → consensus gap); stopping conditions checked every few steps: marginal lookup no longer moves the belief; uncertainty irreducible on this horizon (a sizing problem, not a research problem); thesis already priced in; kill-criterion hit |
| Weight / subtract | Primary > secondary; point-in-time verified > vendor-restated; bears-on-a-key-driver > sideshow; new information > re-narration; **a dataset's weight is capped by its lag**; the noise list is written explicitly |
| Form belief | `beliefs/<entity>.md` records variant view vs the *measured* consensus, confidence, and mandatory **falsifiers** — the best falsifiers are scheduled: a specific print on a specific date that the view says must land in a specific range |
| Run scenarios | 3–5 scenarios with probability and payoff, compared against the option-implied distribution; where they disagree is exactly the bet; a 30% scenario at 5x payoff dominates a 60% scenario at 1.2x |
| Decide | ACT / WAIT / NO-ACTION are all first-class and all journaled with reference price, key-driver bet, scenario table, invalidation condition decided *now*, and review date; act only when the payoff distribution is asymmetric *after* what is priced in; every WAIT registers a monitor |
| Track / update / improve | Postmortem at review date or falsifier hit; decision quality scored separately from outcome quality; lessons routed to `beliefs/`, `process/lessons.md`, and monitor tightening/retirement |

Persistent state lives under `research/` in the workspace — `beliefs/`, `events/log.md`, `questions/backlog.md`, `decisions/journal.md`, `postmortems/`, `process/lessons.md`, `monitors/`, `calibration/` — all dated, append-only where journal-like, and each entry carrying the market price at write time. Judgments live in `research/`; facts live in the lake (Section 5). The separation matters: beliefs may be revised, but the record of what was believed when may not.

---

## 4. System Architecture: Research System and Production System

Top quant firms maintain two distinct plants: a **research data platform** (point-in-time historical data, backtest engines, strict no-lookahead reconstruction of "what was knowable at t") and a **production monitoring plant** (live feeds, alerting, execution-adjacent state). Blurring them is the classic institutional failure: research quietly consumes restated production data and backtests become crystal balls. This system reproduces the split at miniature scale, deliberately.

### 4.1 Research System

Three components:

**(a) Real-time data monitoring infrastructure.** Scheduled pulls (devbox triggers/cron) against the endpoint registry: daily CBOE chain snapshots ~1h after the close, daily FINRA Reg SHO files, daily Form 4/8-K polls on watched CIKs, biweekly short-interest publication-day pulls, quarterly 13F sweeps peaking 45 days after quarter end, monthly TWSE sales around the 10th. Each pull ends by running its monitors and appending firings to `events/log.md` — that is the only channel through which the data layer addresses the decision layer.

**(b) Snapshot-first storage.** A hive-partitioned parquet lake:

```
/workspace/data/<source>/<dataset>/dt=<YYYY-MM-DD>/part-*.parquet
                                   dt=<YYYY-MM-DD>/_meta.json      # provenance sidecar
```

The mandatory `_meta.json` records `source_url`, `fetched_at`, `effective_date`, `published_at`, `row_count`. The three timestamps are never conflated: `effective_date` is what period the data describes, `published_at` is when the market could know it, `fetched_at` is when we grabbed it. Partitions are append-only — corrections are new partitions, never edits — so *diffing partitions is itself the signal* for most monitors (ΔOI, ΔSI, new filings). Raw payloads are retained gzipped beside the parsed parquet, because parsers have bugs and raw permits re-parsing history. The lake is mirrored to GCS (pull-then-work-then-push discipline); session workspaces are reclaimable, the mirror is durable.

**(c) Benchmark construction.** The step that turns the lake into an ML asset: any live-monitored series can be recast as a **causally ordered, no-lookahead prediction task**. The construction rules, from `inv-quant-foundations`:

- **Publication-time joins**: all predictive joins use `merge_asof(direction='backward')` on `published_at` with explicit tolerance — never on effective date, never on calendar quarter. Vendor data carrying only effective dates is guilty until publication lag is reconstructed from the source's own rules (13F ≤45d; SI ~7 business days; Form 4 ≤2 business days; earnings at the announcement timestamp, am/pm mattering).
- **Rolling-origin evaluation**: forecasts at each origin use only data published before it; expanding or rolling train windows; test strictly later.
- **Purging and embargo**: rows whose h-day forward labels overlap the split boundary are purged, with a further embargo for slow features — following the purged cross-validation program of López de Prado (2018). `KFold(shuffle=True)` on time series is an automatic rejection.
- **Point-in-time universes**: constituent lists and liquidity filters computed on trailing data only; delisted names retained with delisting returns; where clean history is unavailable, the writeup says so and bounds the bias direction.
- **Restatement handling**: XBRL facts keep the *first* filing for point-in-time work and the latest for descriptive work — both stored, usage tagged.

Because the lake is built by *snapshotting live* rather than buying restated history, every dataset is point-in-time by construction from its first partition forward. This inverts the usual economics: vendors sell you history and you fight their restatements; here the agent manufactures unimpeachable point-in-time history as a by-product of operating.

### 4.2 Production System

The live half consumes the same lake but serves decisions rather than datasets: standing **monitors** (spec + firing log per monitor in `research/monitors/`, each with an explicit retire-when condition), **event triage** (loop stage 1), the **decision journal** (every ACT/WAIT/NO-ACTION with reference price, thesis, key-driver bet, scenario table, and an invalidation condition decided *now*, not later), and **calibration grading** on print days. Freshness is a hard gate: a monitor reading a partition older than its cadence must say "STALE DATA" rather than compute on it; a silent empty partition poisons everything downstream, so ingestion failures raise loudly.

The two systems meet only at the lake and the event log. Research never reads live mutable state; production never writes history.

### 4.3 Correspondence to institutional practice

| Institutional component | This system's analog | Deliberate difference |
|---|---|---|
| Point-in-time research database (vendor-licensed, restatement-managed) | Snapshot-first lake with provenance sidecars | PIT-by-construction from live snapshots instead of PIT-by-reconciliation of purchased history |
| Backtest platform with survivorship/lookahead controls | `inv-quant-foundations` rules enforced in `quantlab.lake` code | Rules live in the library defaults, not in analyst discipline |
| Production monitoring & alerting plant | Scheduled monitors + `events/log.md` + triage stage | Alerts route into a cognition loop, not a human on-call rotation |
| Research review / model risk committee | L4 adversarial verifiers + calibration registries | Review is spawned per-deliverable, with different lenses, rather than periodic |

---

## 5. The Data Layer

### 5.1 Sources, cadences, lags, and traps

The system runs entirely on public/free data — a constraint (Section 10) and a discipline. Each source below carries a specific point-in-time trap that the corresponding `inv-*` skill encodes.

| Source | Content | Cadence | Publication lag | The point-in-time trap |
|---|---|---|---|---|
| SEC EDGAR submissions / archives | All filings per CIK; Form 4 XML; 13F infotables | event-driven | filing acceptance time | React at *filing datetime*, not transaction/effective date |
| SEC XBRL companyfacts | All tagged financials with `filed` dates | per filing | days | Restatements: same concept-period filed multiple times; first-filed for PIT work |
| EDGAR full-text search | Phrase hunting (buyback announcements, 8-Ks) | event-driven | minutes–hours | Announcements are unbounded promises, not flow |
| SEC DERA structured sets | Quarterly TSVs: 13F, insider, financials | quarterly | weeks | Backfill only; unit changes (13F $ thousands pre-2023) |
| 13F-HR | Long US equity + listed option positions, ≥$100M managers | quarterly | ≤45 days | No shorts/swaps/non-US; join on filing date or gain a 45-day crystal ball; Q4 filings cluster mid-February |
| N-PORT-P | Registered-fund (mutual fund/ETF) monthly portfolios | monthly | ~60 days | Best free window into long-only accumulation *paths*; still two months stale |
| FINRA consolidated short interest | Open short positions, two settlement dates/month | biweekly | ~7 business days | Market learns mid-June positions in late June; between prints you are position-blind |
| FINRA Reg SHO daily short volume | Per-ticker daily short *volume* | daily | same day | Level is ~meaningless (market-maker liquidity provision); only z-scored changes and divergences signify |
| CBOE delayed chains | Full chain: OI, volume, IV, greeks | daily snapshot | 15-min delayed; **OI is T+1** | Free OI history does not exist — snapshot daily and diff; today's file carries yesterday's OI (`oi_asof`) |
| Form 4/5 insider transactions | Insider trades with codes and 10b5-1 flags | event-driven | ≤2 business days | Raw "selling" is mostly mechanical noise; cleaning is the alpha; blackout windows are structure, not signal |
| Buyback disclosures | 8-K authorizations; 10-Q issuer-purchases table; XBRL repurchase cash flow | event / quarterly | 8-K immediate; execution a quarter stale | Authorization ≠ execution; net shrink visible only in diluted share count |
| TWSE/MOPS monthly revenue | Taiwan-listed monthly sales (TSMC, suppliers) | monthly, ~10th | ~10 days | Rare genuinely monthly fundamental data; a supply-chain sampling gift |
| Korea/Taiwan export statistics | Category-level trade data (memory exports) | monthly | weeks | Superb DRAM/NAND volume proxy; public but broadly ignored |
| Commodity price curves (DRAM/NAND/HBM/SSD) | Spot/contract memory prices, retail SSD scrapes | daily–quarterly | varies | Basis mixing (DDR4 spot vs DDR5 contract) fabricates theses; HBM has no public spot at all |

Cross-source identity is its own trap: tickers change and merge; filings key on CIK, issuers on CUSIP, with a maintained alias table in the lake.

### 5.2 The positioning cube

Positioning data is organized as a seven-layer cube ordered fast-to-slow:

| Layer | Cadence | Lag |
|---|---|---|
| Tape: volume, VWAP footprints | intraday/daily | none |
| Options OI, P/C, IV surface, GEX | daily | T+1 OI |
| Buyback authorization/execution | event/quarterly | days–quarter |
| Insider transactions (Form 4) | event-driven | ≤2 business days |
| Short interest (FINRA) | biweekly | ~7 business days |
| Mutual-fund books (N-PORT) | monthly | ~60 days |
| 13F institutional books | quarterly | ~45 days |

Two doctrines govern its use. **Read fast-to-slow**: the tape and options say what changed this week; SI this fortnight; 13F/N-PORT give structural backdrop. **A dataset's evidential weight is capped by its lag**: a 45-day-old 13F fact cannot overrule what the tape did this week; it can only contextualize it. Divergences *between* layers are the signal — price flat + SI rising + call OI accumulating at one strike is a coiled spring; price up + long-only adds + insiders selling into it is distribution.

### 5.3 Derived objects: from raw cube to signals

Raw positioning layers become decision-relevant only after domain-specific cleaning and combination — and in several layers, *cleaning is the alpha*:

- **Crowding (13F/N-PORT).** The basic object is the quarterly diff per (manager, issuer) — new/added/trimmed/exited, diffed in *shares* (dollar diffs confound price with flow). Over a maintained hedge-fund sub-universe, a crowding score combines HF count, HF % of float, mean position rank, and their QoQ changes; breadth is reported separately from concentration; pairwise book overlap (Jaccard on top-20 holdings) tracks systemic crowding. Crowding is a **conditioner, not a signal**: it amplifies whatever else is true, and it is always reported next to days-to-exit (HF % float / ADV) — the quantity that turns "great company" into −25% in a week.
- **Insider signal (Form 4).** Raw insider selling is mostly mechanical. The transaction-code hierarchy keeps open-market purchases (code P) as *the* signal; sales survive only after dropping 10b5-1-flagged, same-day exercise-and-sell, and small-fraction-of-stake trades. The validated-then-re-verified hierarchy: cluster buys (≥3 insiders in ~30 days) > sized CEO/CFO buys (measured against their comp) > buys after >30% drawdowns > filtered discretionary sales. Horizons are quarters, not days — insiders are early — and blackout windows make pre-earnings silence structure, not signal.
- **Short-squeeze screen (SI + options + tape).** A squeeze needs *fuel* (SI % float top-decile, days-to-cover > ~5), a *trap* (small float, longs not crowded — crowded-long names supply stock into the rip), *trigger proximity* (a scheduled catalyst inside the horizon), an *accelerant* (near-OTM call OI growing via ask-side volume, dealers short gamma, implied borrow rising), and *tape confirmation* (absorption on down moves, short-volume ratio falling into weakness). Names scoring on fuel without a trigger are watches, not trades; squeeze longs are rentals with the exit defined at entry. The mirror screen — crowded long, deteriorating drivers, insiders selling — flags air-pocket shorts.
- **Execution footprints (bars only).** Institutional parent orders leave mechanical traces in free bar data: smooth elevated volume with upper-half closes (accumulation); high-volume flush followed by equal-volume price stabilization (capitulation → absorption, the strongest bottoming tell); minute bars with extreme volume and compressed range (negotiated blocks). Every footprint call is later confirmed or refuted against N-PORT/13F disclosures, and the hit/miss log calibrates the detector. Interpretation is regime-conditional — dealer-gamma sign, buyback blackout windows, OpEx/rebalance calendar, volatility tercile — because the same volume pattern means opposite things in long- and short-gamma tape.
- **Buyback flow.** An authorization is a press release; execution is a flow. The execution-pace ratio (trailing repurchase $ vs remaining authorization per quarter to expiry), price sensitivity of the monthly purchase table, and program size expressed in *days of ADV* separate a structural bid from IR theater; net shrink is computed against SBC dilution via the diluted share count, the only number shareholders keep.

### 5.4 The fog-of-war audit

Quarterly, per theater (e.g. "NAND/storage"), the strategy map answers three questions in writing:

1. **Familiar vs blind**: which map nodes have current driver trees and calibrated forecasts, and which are carried as names only.
2. **Sampling precision**: per node, the best public series frequency, last refresh, and provenance quality. A node sampled only quarterly is a node where the agent cannot beat the market's mid-quarter information — knowing *which* nodes those are is itself the deliverable.
3. **Leadingness**: for each series — is it consensus-watched (TrendForce headlines), public-but-ignored (Korean export micro-categories, second-tier TWSE suppliers), or self-collected (a daily retail-SSD price scrape)? **Only the latter two classes can host a data edge**; they are marked and defended with monitors.

The audit output prioritizes the next quarter's research: extend the map where fog and payoff-relevance overlap. This is resource allocation under uncertainty made explicit and gradeable — the "taste" dimension of the environment.

---

## 6. The Model Layer

### 6.1 Baselines-first doctrine

Every predictive model in the system must beat, on the same purged walk-forward split: (a) the unconditional base rate, (b) regularized linear regression on the same features, (c) the single best feature alone — or the writeup states that the complexity bought nothing. Evaluation is rank-IC (per-date Spearman, then time-series mean and t-stat) for cross-sectional signals; MAPE + directional hit rate for level forecasts; calibration curves for probabilities. Portfolio Sharpe comes last and is reported deflated for the number of variants tried (Bailey & López de Prado's deflated Sharpe ratio [verify exact form]); the lab-notebook rule — every variant tried is logged, not just the winner — makes the multiple-testing correction computable rather than aspirational.

### 6.2 Forecasting the intermediate dimensions: driver trees and the measured consensus

The semi-verifiable core (`inv-revenue-projection`) is a three-step pipeline run per covered name per print:

**Step 1 — the driver tree.** From 10-K/10-Q segment disclosures and XBRL facts: total revenue → reportable segments → (units × ASP), (customers × ARPU), or (capacity × utilization × price) per segment; historical growth decomposed into volume/price/mix/FX/M&A; every node tagged `[filed]` / `[derived]` / `[assumed]`. Each node is annotated with its **leading indicators and their sampling frequencies** — the point where the tree meets the strategy map: daily commodity price curves feed price nodes (memory-maker ASPs follow spot with a per-company contract lag estimated from history, never assumed); monthly TWSE supplier/customer sales and export statistics feed volume nodes; customer 10-Q inventory builds are future order cuts. Segment redefinitions break trees silently, so segment names are diffed at every 10-K.

**Step 2 — measure what the market expects, in three layers, before forming a number.** (1) *Guidance*, adjusted by the company's own guide-vs-actual history — a company that beat its midpoint 11 of 12 quarters has a guidance-bias parameter, and it is used. (2) *Sell-side per bank*, snapshotted (vendors restate; the agent's dated snapshots do not), with the water modeled: estimates anchor to guidance and drift to be beatable — the ~70–80% positive-surprise base rate in US large caps is a structural artifact, not information — so the informative objects are revision breadth and velocity and the reasoning of the highest and lowest estimates, where the actual disagreement lives. (3) *Buy-side whisper*, unobservable and therefore triangulated: the options-implied move (the market's uncertainty), price reactions to peer prints and mid-quarter datapoints (the lean), positioning drift into the print (the lean with capital behind it), and the stock's reaction-function history (quarters that beat consensus and fell locate the whisper above consensus). Whisper is stated as a range with its evidence.

**Step 3 — the supply-chain jigsaw.** Each node projected bottom-up from its leading indicators, sanity-checked against base rates (a projection outside the company's historical 90% QoQ-growth band needs a named mechanism, in writing), and reconciled top-down against market-size × share — gaps beyond a few percent are findings, not rounding. Output per print: point + 80% interval per segment and total, the variant vs consensus/guidance/whisper, and **which tree node carries the disagreement** — that node is monitored daily until the print, and it is the credit-assignment pointer the postmortem will use. A final discipline: the variant can be right and the trade wrong if the whisper already had it — the tradeable quantity is the gap to whisper, not to published consensus.

### 6.3 Time-series foundation models as priors, not oracles

Zero-shot TS foundation models — Chronos (Ansari et al., 2024), TimesFM (Das et al., 2024), with Moirai/Lag-Llama-class models as cross-checks — serve one specific role: the **unconditional prior** for a driver-tree node or price curve, which the agent's supply-chain jigsaw then conditions. The contract in `inv-revenue-projection`: when the agent's number differs from the FM prior by more than the FM's own interval, the writeup must *name the conditioning information* — if it cannot, the agent does not have any. Doctrine: dumb baselines (seasonal-naive, drift, a GBM) always run beside the FM, and an FM that fails to beat seasonal-naive on a given series is benched for that series — which happens routinely on quarterly fundamentals, where 8–40 observations mean the FM's residual value is calibrated intervals, not point accuracy. Zero-shot first; fine-tuning almost never (samples don't justify it); on OHLCV bars, Chronos-style sampled paths feed interval and tail estimates for scenario tables, never point-direction bets. Every stored forecast carries model id, version, context window, and input partition hashes — any number in a memo traces to the exact model call.

### 6.4 The Bayesian criticism loop

Every model — learned or hand-built — lives under Box's loop, the build-criticize-expand cycle of Box (1976) as operationalized in the Bayesian workflow of Gelman et al. (2020), logged per model in `research/calibration/models/<name>.md`:

1. **Prior predictive check** before deployment: do the model's assumptions generate data that resembles the domain at all?
2. Fit / condition.
3. **Posterior predictive check**: residual structure; *empirical coverage of stated intervals* (an "80% interval" that covers 60% is a lie, and coverage is tracked as a time series); tail behavior on the events that matter.
4. **Criticize and expand**: failed checks trigger either model expansion (covariate, regime split, jump component) or a shrunken mandate, as a dated registry entry.

Hand-built Bayesian models (PyMC/Stan-style) earn their place on structured problems where FMs have no covariate path: hierarchical guidance-bias models partially pooling sandbagging parameters across companies; state-space models of contract-vs-spot price lags; capacity-ledger arrival models.

### 6.5 Option pricing and the SDE toolkit

US single-stock options are American with discrete dividends; Black–Scholes is the reference frame, not the price. The pricing stack (implemented in quantlab, each layer verified):

| Tool | Role | Verification |
|---|---|---|
| CRR binomial (Cox–Ross–Rubinstein, 1979) with discrete dividends | Workhorse for American exercise | European limit converges to BS closed form; Richardson extrapolation across node counts |
| Barone-Adesi–Whaley (1987) | Fast approximation for whole-chain screens | Spot-checked against binomial before any screen is trusted |
| Longstaff–Schwartz LSMC (2001) | Path-dependence and multi-factor simulation | Regression basis documented; standard errors reported |
| Heston (1993) | Skew/term-structure dynamics; scenario-consistent repricing | Feller condition checked; parameter bounds sane |
| Merton jump-diffusion (1976) | **Event risk**: a binary print is a jump, not diffusion — implied jump size/probability extracted from front-expiry excess variance | Diffusive vol anchored to post-event expiries |

A **mandatory verification block** accompanies every pricing output: put-call parity residuals across the chain (borrow-adjusted), European-limit convergence, no-arbitrage surface checks (butterfly ≥ 0, calendar monotonicity), calibration RMSE per expiry, and the `dt=` partition used. A number without its checks block does not leave the notebook. This sub-domain is the *fully verifiable* island inside the semi-verifiable environment — and deliberately so: it anchors the agent's numeracy where exactness is available.

### 6.6 Implied distributions

The options market posts the market's entire probability distribution daily; the system deconvolves it via Breeden–Litzenberger (1978): the risk-neutral density is `q(K) = e^{rT} ∂²C/∂K²`. The practical recipe uses OTM options only (mitigating American-exercise bias), backs out the forward — and thereby **implied borrow** — from put-call parity at the strike minimizing |C−P|, fits a smooth IV curve (SVI or convexity-constrained spline) in log-moneyness, and differentiates the *fitted* price curve, never raw quotes; density sanity checks (non-negativity, unit mass, mean ≈ F) gate use. The implied earnings move comes from the front straddle with the post-event baseline variance stripped using a later expiry. Where the agent's scenario probabilities disagree with q(K) is *precisely its bet*, and both are quoted in the decision journal — with the standing footnote that q is risk-neutral, so tail comparisons are valid in relative and time-series terms only (Section 10).

---

## 7. The Agent Hierarchy

One context window cannot hold a theater campaign. The orchestration doctrine (`references/orchestration.md`) scales by layering, under one constraint: **context is the scarce resource; documents are the interface between layers.**

```
L0  Decision layer — the main session running the cognition loop.
    Plans a CAMPAIGN (one theater or thesis). Output: campaign doc.
L1  Domain planners — one per inv-* domain touched.
    Expand their slice into a tree-shaped plan doc of concrete sub-problems.
L2  Task executors — one per sub-problem, small enough for one context:
    download THIS dataset, build THIS monitor, run THIS event study.
L3  Workers — optional fan-out: per-ticker / per-quarter / per-filing.
L4  Verifiers — adversarial, always: every deliverable feeding a conclusion
    gets an independent point-in-time audit, row-count check, headline-number
    recompute, and an attempted refutation.
```

**Plan documents are the inter-layer contract.** Each planning layer writes a tree/mind-map markdown doc (`research/plans/<campaign>/`) before spawning children:

```markdown
# Plan: <name>        Layer: L1 | Parent: <parent doc> | Date, status
## Objective (one sentence, from parent)
## Tree
- 1. <sub-problem>  [owner: L2-agent | est. effort | deliverable path]
  - 1.1 <concrete step: download X / clean Y / analyze Z / predict W>
- 2. ...
## What this layer decided NOT to do (subtraction, with reasons)
## Definition of done + verification plan (which L4 checks apply)
## Status log (append-only: dispatched, done, failed, re-planned)
```

A child receives its subtree, the objective chain (L0 → its layer), relevant skill names, and lake/doc paths — not the campaign context. If a subtree is not self-sufficient, the fix is the plan doc, not a wider prompt. Every sub-problem follows one inner shape: **download data → clean (domain rules from the relevant `inv-*` skill) → analyze → extract insight → predict the verifiable dimension → register a calibration entry** — so even grunt work terminates in a gradeable commitment. Children return structured summaries; parents update the status log; the doc, not the chat, is the memory. Re-planning is first-class: an L2 that discovers its sub-problem is mis-framed reports up rather than grinding.

**Code-driven orchestration, not prompt chains.** Recurring operation (daily pulls + monitor sweeps, weekly screens, quarterly fog audits) runs as deterministic scheduled loops with verification gates: each firing is a mini-campaign — L1 plan refresh (usually a no-op diff), L2 pulls, L4 freshness checks, synthesis into the event log. The decision layer wakes only for triaged material events. LLM judgment sits at the nodes; the edges are code.

**Fan-out discipline.** Sub-problems parallelize when independent; a theater campaign legitimately fans to dozens of agents in a day (~5 L1 → 15–30 L2 → per-ticker L3 → L4 on everything that survives). Where judgment is involved, verifiers are spawned with *different lenses* (point-in-time audit / statistical validity / domain mechanism), not three copies of one prompt — independent perspectives beat redundant ones. Every fan-out terminates in a synthesis step at the parent that reads only children's docs and updates beliefs, the map, the question backlog, and process lessons: fan-out without synthesis is noise generation. Fleet size is matched to the campaign's value-of-information, and the spend judgment is itself logged.

**Advisor/escalation pattern.** Irreversible actions confirm with the human principal unless durably authorized; the one-year plan's production analog sets a capital threshold below which execution automates and above which it escalates. The hierarchy is advisory upward and delegated downward.

**Test-driven acceptance.** This whitepaper and the skill documents are the drawings; the built system must verify against them the way a building verifies against its blueprints. Concretely: golden-fixture tests pin parser behavior, verification blocks pin pricing math, calibration files pin forecasting claims, and L4 verifiers pin every research deliverable. A component that cannot be checked against a written contract is, by policy, not yet built.

---

## 8. Engineering

### 8.1 Language policy

The policy is shaped by an unusual constraint: **the human principal reads only Python.** Therefore:

- **Python-first, with Polars** (not pandas) for all dataframe work: lake IO, `join_asof` point-in-time joins, feature engineering, backtest frames. Pandas appears only at the edges where a library demands it.
- **Rust** for raw-feed parsing and hot numerical loops: the `ql-ingest` crate parses FINRA pipe-delimited files and large CBOE chain JSON zero-copy where it matters; binomial trees over whole chains and LSMC path generation migrate to Rust as they become hot.
- **Go** for orchestration glue where long-running schedulers/daemons outgrow scripts.
- **All non-Python code is produced and maintained by sub-agents**, behind Python-visible contracts. The acceptance mechanism is **golden-fixture cross-language tests**: the Rust and Python implementations must produce identical normalized records on shared fixtures (`quantlab/rust/crates/ql-ingest`: "the cross-language fixture test is the acceptance check for parser correctness"). The principal audits behavior through the Python surface and the fixtures; the sub-agents own the foreign internals. This is a deliberate experiment in *asymmetric-literacy* code ownership: correctness is enforced by executable contracts rather than by human review of every line.

### 8.2 quantlab layout

```
quantlab/
  rust/crates/ql-ingest/     # feed parsers/normalizers (Reg SHO, CBOE chains)
  python/quantlab/
    lake.py                  # hive-partitioned parquet IO + _meta.json sidecars;
                             # every write requires effective_date/published_at;
                             # asof joins default backward on published_at
    pipelines/               # dataset-specific ingest→lake pipelines
    features/                # Polars feature builders (flow/tape footprints, ...)
    models/                  # one Forecaster interface: baselines and FM wrappers
                             # (Chronos/TimesFM optional deps) swap freely
    pricing/                 # CRR American binomial + BS checks; Rust port when hot
```

Point-in-time rules are enforced *in code*, not in prose: `lake.write` rejects partitions without provenance; `lake.read` exposes the three timestamps; the default join direction is backward on `published_at`. Ingestors are small idempotent scripts (one dataset each, `--date`/`--tickers` args, re-runs overwrite only their own partition, `_meta.json` written last as the completion marker, polite User-Agent headers, loud failures). Data lands under `/workspace/data`, mirrored to GCS — never inside the repo.

### 8.3 Substrate

The devbox platform supplies the properties the environment needs: per-session containers whose bind-mounted workspaces (and hence `research/` and the lake) outlive any single container; a scheduler for cron/interval/once triggers (how monitors run); filesystem IPC for event injection mid-session; and multi-user chat surfaces (Telegram/Slack/Web) so a human team and the agent share one persistent research state — the "shared facts layer" of the product concept: everyone argues over the same computed artifact instead of private spreadsheets.

---

## 9. Semi-Verifiability as Training Signal

The system doubles as a training environment. The signal channels, ordered by objectivity:

1. **Calibration files** (fully objective): per-entity, per-node MAPE, interval coverage, directional hit rate vs consensus, all against public prints. Node-level error attribution ("my ASP-lag assumptions run systematically short") is a *structured* gradient — it names the sub-model to fix, not merely the fact of error.
2. **Monitor hit/miss logs** (objective): the SVR-vs-ΔSI triangulation is verified at every SI print; footprint-based accumulation calls are confirmed or refuted by later N-PORT/13F disclosures; a detector that keeps missing for a name is retired for that name, in writing.
3. **Postmortems** (semi-objective): decision quality scored *independently of outcome quality* — was the key driver actually the driver, which question that mattered went unasked, what research was wasted. The one-year plan formalizes this as process validation: did the stock move *for the predicted reason*? Grading process alongside PnL raises statistical efficiency enormously — a thesis's causal chain has many checkable links, while its PnL is one noisy draw.
4. **Process lessons** (`process/lessons.md`) and the question backlog's **Cut section** (the taste record: questions killed, with reasons): the least verifiable channel, but the one that compounds — standing corrections re-read at every session start.

What could this environment teach a model that current benchmarks cannot?

- **Event world-modeling.** Second-order propagation through a supply-demand graph (capacity announcement → forward supply curve → competitor ASP → customer margin) is exactly the causal-graph competence that static QA cannot exercise, because here wrong graphs produce wrong falsifiable forecasts that print within months. The capacity-cycle doctrine — the down-leg begins at the credible *announcement* of supply, not its arrival 18 months later — is a nontrivial learned regularity of exactly this type.
- **Continual learning over months.** The loop's memory artifacts are the curriculum: beliefs must be read before written; contradicting a prior belief is legal, silently ignoring it is not. Improvement is measurable as calibration trend, not benchmark delta.
- **Taste in question generation.** Value-of-information × resolvability ranking, with mandatory culling; a backlog where nothing gets cut is a graded failure. No existing benchmark scores *which questions an agent chose not to ask*.
- **Resource allocation under uncertainty.** Fog-of-war audits, stopping conditions ("marginal lookup no longer moves the belief"; "uncertainty irreducible on this horizon → sizing problem, not research problem"), and fleet-size-vs-VOI judgments in campaign docs make research-compute allocation an explicit, journaled, later-gradeable decision.
- **Adversarial epistemics.** The environment prices in whatever is easy. A mispricing claim without a measured consensus (options-implied distribution, positioning, estimate snapshots) "is a mood"; the reward for lazy claims is systematic, graded wrongness.

The delay structure of the reward (days to a quarter) is arguably the point: it forces credit assignment through the agent's *own written intermediate commitments* — the driver-tree node named as carrying the disagreement is the credit-assignment pointer, recorded before the outcome. The environment thus supplies not just scalar grades but *targeted* ones, which is what small-sample learning needs.

---

## 10. Limitations and Open Problems

**Flow inference is triangulation, not ground truth.** Free data carries no counterparty or trade-side tags. Opening-vs-closing options flow is inferred from (volume, next-day ΔOI, IV drift) triangles; institutional accumulation from bar-level footprints; buy-side whisper from peer-print reactions and positioning drift. All conclusions in this class are labeled as inference with the triangulation shown — but a paid-tape shop simply *knows* many of the things this system estimates. The honest framing: the system optimizes inference under a data budget, and its confidence calibration must price that budget in.

**GEX sign assumptions.** Dealer gamma exposure requires signing OI by who is short the option, which free data does not reveal. The system computes GEX under a stated convention, upgrades the sign with OI-change/ask-side-volume evidence where available, and always reports "under assumption X" — but zero-gamma levels and squeeze-flow numbers inherit the assumption's fragility, and the assumption itself drifts with market structure (e.g. systematic call overwriting vs retail call buying regimes).

**Risk-neutral vs real-world densities.** Breeden–Litzenberger yields q, not p: tails embed risk premia and are systematically bid relative to physical probabilities. The system uses q for relative and time-series comparison and footnotes the wedge, but any scenario-vs-implied "edge" computation is partially measuring the variance/jump risk premium, not disagreement. Estimating the pricing kernel from free data is open.

**Small samples on fundamentals.** Four revenue prints per name per year, 8–40 usable points per node: calibration statistics converge slowly, node-level MAPE patterns can be noise, and hierarchical pooling across names (Section 6.4) is a partial fix that imports its own exchangeability assumptions. The semi-verifiable reward is real but *thin*; the training-signal claims of Section 9 are correspondingly medium-term claims.

**Non-stationarity.** Guidance-bias parameters, contract-price lags, footprint signatures, and the capacity cycle itself all drift. Every calibration is per-window and dated, and Box's loop exists precisely to catch decay — but there is no theoretical guarantee that yesterday's validated regularity survives the regime that matters. The system's defense is honesty (coverage tracking, dated registries), not immunity.

**Blueprint vs Citadel-grade production.** This is a design-complete, partially built system operated by an agent on free data with quarterly-audit discipline — not an institutional plant. Missing relative to a top firm: real-time consolidated feeds and tick history, a securities master with survivorship-clean corporate actions, borrow/locate data, execution infrastructure with impact models, independent risk oversight, and redundancy engineering throughout. Some gaps are capital (data licenses), some are genuinely open engineering. The one-year plan's shadow-mode → small-capital → sim-to-real-gap-measurement path is the intended bridge, with the automation threshold and human escalation as the safety envelope.

**Open problems** worth stating as such: (i) grading question-generation taste directly rather than through downstream calibration; (ii) principled fleet-sizing (VOI estimates for research campaigns are currently judgment, journaled but unmodeled); (iii) the Financial World Model — an event-causal graph queryable by higher layers — of which the strategy map is a hand-built v0; (iv) whether asymmetric-literacy code ownership (Section 8.1) scales past the current two-language surface without the fixture contracts becoming the bottleneck; (v) how to prevent an agent trained against calibration files from gaming interval width (coverage is tracked, but proper scoring rules over the full predictive distribution would close the loophole and are not yet standard in the pipeline).

---

## 11. Conclusion

The system makes one wager twice. As an investing method, it wagers that discretionary judgment becomes cumulative — rather than anecdotal — the moment every belief is written down falsifiably, every forecast lands in a calibration file, and every decision is journaled with its invalidation condition decided in advance. As an ML research direction, it wagers that the same instrumentation turns an open, adversarial, non-stationary world into a training environment with objective (if delayed and thin) reward — one that exercises event world-modeling, continual learning, question taste, and compute allocation in a way neither verifiable-reward benchmarks nor preference-graded open tasks can. Both wagers resolve the same way everything else in this system resolves: on a schedule, against the record. The calibration files will say whether the agent forecasts well; the postmortems will say whether it decides well; and the trend of both will say whether the loop is, as designed, improving the loop.

---

## References

- Ansari, A. F., et al. (2024). *Chronos: Learning the Language of Time Series.* arXiv:2403.07815.
- Bailey, D. H., & López de Prado, M. (2014). *The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality.* Journal of Portfolio Management. [verify]
- Barone-Adesi, G., & Whaley, R. E. (1987). *Efficient Analytic Approximation of American Option Values.* Journal of Finance, 42(2).
- Box, G. E. P. (1976). *Science and Statistics.* Journal of the American Statistical Association, 71(356).
- Breeden, D. T., & Litzenberger, R. H. (1978). *Prices of State-Contingent Claims Implicit in Option Prices.* Journal of Business, 51(4).
- Cox, J. C., Ross, S. A., & Rubinstein, M. (1979). *Option Pricing: A Simplified Approach.* Journal of Financial Economics, 7(3).
- Das, A., et al. (2024). *A Decoder-Only Foundation Model for Time-Series Forecasting (TimesFM).* ICML 2024.
- Gelman, A., et al. (2020). *Bayesian Workflow.* arXiv:2011.01808.
- Heston, S. L. (1993). *A Closed-Form Solution for Options with Stochastic Volatility.* Review of Financial Studies, 6(2).
- Longstaff, F. A., & Schwartz, E. S. (2001). *Valuing American Options by Simulation: A Simple Least-Squares Approach.* Review of Financial Studies, 14(1).
- López de Prado, M. (2018). *Advances in Financial Machine Learning.* Wiley. (Purged and embargoed cross-validation.)
- Merton, R. C. (1976). *Option Pricing When Underlying Stock Returns Are Discontinuous.* Journal of Financial Economics, 3.

*Internal sources: `container/skills/agentic-investing/` and the ten `inv-*` skills; `quantlab/README.md`; `docs/architecture.md`; `concept-and-future-plan-on-financial-investing-harness/devbox-concept.md` and `one-year-plan.md`.*
