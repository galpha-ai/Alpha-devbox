# AlphaDev Neo-Lab: One-Year Development Plan

**Goal:** Build an AI researcher neo-lab that merges quant systematic investing
and discretionary (主观) investing, using DevBox + AlphaDevBox as the research
harness.

**Audience:** Early users, collaborators, and future LP investors.

---

## 1. Thesis

There are two camps in investing that barely talk to each other.

- **Quant systematic investing** is strong at execution, microstructure, market
  impact, adverse selection, attribution, robustness testing, and sim-to-real
  calibration. It is weak at questions that cannot be cleanly backtested.
- **Discretionary (主观) investing** is strong at reading the world — events,
  narratives, crowding, sentiment, asymmetric payoff structure — but weak at
  turning a view into a repeatable, falsifiable research process.

The AlphaDev neo-lab merges the two. We give discretionary research a quant-grade
research harness, and we give quant tooling a world-model layer that can reason
about events that have not happened yet. The product is a persistent, hosted AI
researcher that takes natural-language intent and runs the research end to end.

A one-line restatement:

> **Backtest any idea. Simulate any scenario. Automate low-value decisions.
> Keep humans on high-value judgment.**

---

## 2. Product stack

Three layers, matched to three kinds of research problem.

### Layer A — Forecast & Backtest (historically verifiable)

For any idea with a prediction target and enough historical comparables:

- Turn a view into a forecast ŷₜ.
- Run rolling regression / rolling predictive ML models (linear, tree, DNN).
- Compare ŷₜ against realized y over time.
- Handle trigger-based strategies, including non-linear and option-style
  payoffs. Triggers can be price, volume, earnings, news, a tweet from a
  specific account, or the conclusion of a previous model run.
- Produce standard statistical properties: Sharpe, turnover, drawdown,
  attribution, failure-mode analysis.

### Layer B — Scenario & Simulation (not historically verifiable)

For questions without a clean historical analog — post-COVID trading, major
geopolitical shocks, catalyst-driven bets:

- Bear / base / bull case with optional probabilities (default 1/3 each or
  50/50).
- Asymmetric payoff analysis: what do I win, what do I lose, across cases.
- Kelly-style sizing.
- What-if simulation and multi-player / multi-agent simulation (how each player
  might behave, how a news event might propagate).
- Calibration against real prediction markets (e.g. Polymarket) to import a
  market-implied probability.

### Layer C — Execution & Delegated Operation (human-in-the-loop)

For actually deploying capital:

- Shadow mode and small-capital live deployment ($10–$1,000) to measure the
  sim-to-real gap on spread, fill rate, market impact, adverse selection.
- Automation threshold: trades below $1,000 can be automated; trades above
  $1,000 stop automation and escalate to a human. The threshold is
  configurable.
- Live monitoring with simulated-vs-live PnL delta dashboards.
- Process validation: check whether the *reasons* for the move match the
  thesis, not only the final PnL.

### Cross-cutting: Financial World Model (research direction)

A Financial World Model is what is really missing. It is not a spread /
adverse-selection model; it is a model of the causal relations between events.
It is what allows the agent to reason about something that has never happened
before and to expose the right compute to the user. Year one lays the
foundations; a full model is a multi-year research program.

---

## 3. Target users

- **Discretionary traders** who want repeatable, verifiable strategy systems
  but do not want to — or cannot — write code.
- **Small investment teams** that want to compound research on a shared set of
  facts, in the same way programmers compound engineering in a shared
  repository.
- **Quant-curious generalists** with basic math but no rigorous methodology
  training.

We are explicitly not targeting large systematic funds running orderbook-level
foundation models on thousands of GPUs. That space is dominated by Jane Street,
XTX, HRT and similar firms. Our opportunity is one layer above: catalyst-based,
directional, scenario-driven research that those systems cannot do well.

---

## 4. Year-one roadmap

The year is split into four quarterly phases. Each phase has a user-facing
deliverable, a research deliverable, and an infrastructure deliverable.

### Q1 — Research harness and data spine (Months 1–3)

**User-facing:** Ship the first end-to-end "backtest any idea" demo. A user
types a natural-language strategy; the agent generates the research plan, pulls
historical data, runs a rolling predictive model, and returns a report with
attribution and failure modes.

**Research:** Library of rolling regression, classical hypothesis tests,
standard predictive ML baselines, and event-trigger backtesting primitives,
exposed as agent tools rather than raw notebooks.

**Infrastructure:**
- DevBox MVP: persistent hosted agent on Google Cloud, multi-user sessions.
- ClickHouse historical data spine (equities first; options and crypto
  scaffolded).
- Financial historical simulator CLI with realistic fills, spreads, and
  transaction costs.
- Agent harness with the tool layer above, versioned.

**Exit criteria:**
- One external user can run a non-trivial rolling forecast by voice / text.
- Team of three can run compound research in a shared Slack / Telegram on the
  same hosted DevBox session.

### Q2 — Scenario and simulation layer (Months 4–6)

**User-facing:** "Simulate any scenario." A user types a thesis that cannot be
backtested ("if the Fed cuts 50bp in July, which sectors win?"), and the agent
returns bear / base / bull payoffs, an asymmetric-bet summary, and, where
available, a calibration against real prediction-market probabilities.

**Research:**
- Scenario generator with probability elicitation and Kelly sizing.
- Multi-agent simulation sandbox: configurable player personalities, news
  propagation, sentiment dynamics.
- Option strategy builder for constructing explicit asymmetric payoff shapes
  (OTM calls, spreads, risk reversals).
- Prediction-market bridge for Polymarket-style contracts.

**Infrastructure:**
- News / social / earnings event feed as first-class triggers.
- Sandbox runtime for multi-agent simulations, reproducible from a seed.

**Exit criteria:**
- A user can go from a hand-written thesis to a sized, asymmetric bet
  recommendation in a single session.
- At least one simulation replayed against a real event after the fact, with a
  published process postmortem.

### Q3 — Human-in-the-loop operator (Months 7–9)

**User-facing:** Deploy tiny live capital. Users can promote a researched
strategy into shadow mode, then into small-capital live mode (default cap
$1,000). Larger trades are routed to a human approver.

**Research:**
- Sim-to-real gap measurement: live vs simulated fills, spreads, market
  impact, adverse selection. Build the first local execution model.
- Process-validation pipeline: for every closed trade, check whether the
  reasons for the move match the original thesis. Use this to grade
  methodology with higher statistical efficiency than raw PnL.

**Infrastructure:**
- Broker adapters (start with one equities broker, one options-capable broker).
- Live monitoring dashboard: sim PnL vs live PnL, thesis-vs-reason match rate,
  drift alerts.
- Per-user kill switches, capital caps, and audit trails.

**Exit criteria:**
- At least one strategy runs shadow → small-live without human code changes.
- A live trade flagged as "reason mismatch" triggers a human review inside the
  same Slack / Telegram thread.

### Q4 — Neo-lab scale-up and Financial World Model v0 (Months 10–12)

**User-facing:** From solo user to neo-lab. A team of 5–10 AI researchers
(human + AI) share a research graph: every idea, backtest, scenario, and
postmortem is a node linked to the shared facts layer. New members inherit the
state of the lab.

**Research:**
- Financial World Model v0: an event causal graph connecting macro prints,
  earnings, geopolitical catalysts, and sector-level narratives. Not a
  full model — a scaffold that higher layers can query.
- Risk / factor-exposure analysis for every live strategy: how much do we
  lose in the tail if factor X dislocates.
- Classification of returns as alpha, carry, risk premium, or scenario bet.

**Infrastructure:**
- Research graph storage and visualisation.
- Shared-facts layer with per-fact provenance (who computed it, with which
  data, at which version).
- Onboarding flow for new researchers (human or AI) that replays the graph.

**Exit criteria:**
- A monthly LP-facing report is generated directly from the research graph:
  PnL, thesis, process-validation results, and risk exposures, with every
  number linked back to the underlying query.
- At least three external teams running on DevBox with separate isolated
  research graphs.

---

## 5. What success looks like at the end of year one

- A hosted AI researcher that a discretionary trader can talk to in natural
  language and get repeatable, verifiable research from.
- A scenario simulator that can reason about events that have never happened.
- A human-in-the-loop operator that automates small trades and escalates big
  trades.
- A multi-user neo-lab running compound research on a shared facts layer.
- A first cut of a Financial World Model, enough to ground the next year's
  research program.

---

## 6. What we explicitly are *not* doing

- Not building an orderbook foundation model. That is a compute arms race with
  incumbents.
- Not selling a fully autonomous PM from day one. We believe humans should
  keep high-value decisions; automation starts at the low-value end.
- Not building a generic coding agent. DevBox is specialised for historical
  data, statistics, and investment research.
- Not producing opaque black-box recommendations. Every number is traceable
  through the research graph.

---

## 7. Validation philosophy

Realised PnL is not enough. Markets are noisy; a good process can lose and a
bad process can win. The neo-lab validates methodology on two axes:

1. **Outcome** — trajectory-averaged PnL across trades.
2. **Process** — did the stock move for the reason we predicted? Did the
   causal chain we wrote down actually fire? Did fundamentals, sentiment,
   crowding, and information flow evolve in the direction the thesis implied?

Grading on (2) in addition to (1) increases statistical efficiency and makes
feedback useful within weeks instead of years. This is a first-class part of
the product, not an afterthought.

---

## 8. Competition and positioning

- **Orderbook / HFT foundation models** (Jane Street, XTX, HRT style) —
  extremely well funded, compute-bound. We do not compete there.
- **Generic coding agents** — can help write code, cannot do investment
  research. We differentiate by shipping the tool layer, the historical data,
  and the simulators as first-class agent capabilities.
- **Traditional quant platforms** — assume users can code and require fully
  systematic strategies. We sit upstream of them, where the user is a
  discretionary trader who wants to test, not a quant engineer who wants to
  deploy.
- **Retail copilots** — typically stop at charting and commentary. We go all
  the way to backtest, scenario, small-live deployment, and process review.

Our defensible surface is the stack: research harness + historical data +
scenario simulator + human-in-the-loop operator + shared-facts collaboration,
on a single persistent runtime.

---

## 9. Business model (sketch)

- Open-source DevBox core. Attracts contributors, lowers trust cost for
  serious users.
- Hosted AlphaDevBox as the paid surface. Individual seats plus team
  workspaces.
- Usage-based compute pricing for heavy simulations and scenario runs.
- Team / fund tier with private shared-facts graph, audit trails, and
  compliance features.

Users pay for research capability, not for outsourced engineering.

---

## 10. Ask for LPs

Year one is a focused, staged build with a real product at the end of each
quarter. What we need:

- Capital for a small, senior team (agent infra, quant research, financial
  engineering, frontend).
- Data licensing for broader historical coverage (options, alt data, crypto).
- Introductions to discretionary funds, family offices, and sophisticated
  individual traders willing to be design partners.

In return, LPs get early access to the hosted product, quarterly reports
generated directly from the research graph, and a front-row seat to the
Financial World Model research program that year two will build on.

---

## 11. Risks and how we mitigate them

- **Research correctness risk** — wrong conclusions from silent data bugs.
  Mitigation: versioned data, deterministic pipelines, shared-facts layer with
  provenance.
- **Sim-to-real gap risk** — simulator flatters live PnL. Mitigation:
  Q3 gap-measurement program and small-capital shadow trading before any
  size.
- **Narrative / sentiment modeling risk** — multi-agent simulations feel good
  but don't predict. Mitigation: always calibrate against real prediction
  markets, and grade process-validation rates honestly.
- **Concentration risk on a small team** — mitigated by the open-source core
  and by designing the system so AI researchers and human researchers share
  the same graph.
- **Regulatory risk on live trading** — mitigated by starting with tiny
  caps, explicit human approval above threshold, full audit trails, and
  conservative broker choice.

---

## 12. Open questions we want feedback on

- Where is the right automation threshold in practice? $1,000 is a first
  guess, not a final number.
- Which broker and data combination gives the cleanest sim-to-real
  calibration at small size?
- How aggressively should we lean on prediction markets for probability
  calibration vs. internal multi-agent simulations?
- What is the right first vertical — US equities, US options, crypto, or a
  cross-asset macro focus?

These are the questions we want to answer with design partners over the next
four quarters.
