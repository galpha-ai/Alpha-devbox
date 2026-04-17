# RFC 003: Human-Imitation Task Dispatcher for Continuous AI Research

**Status:** Draft
**Author:** Bill Sun
**Date:** 2026-04-12

---

## Abstract

This RFC proposes a two-agent architecture where an **Outer Loop Agent** (the "Boss") mimics a human researcher's task-giving style, priorities, and iterative refinement patterns, while an **Inner Loop Agent** (the "Worker") executes research tasks inside a verifiable environment. Together they form a self-sustaining research loop that runs without continuous human attention, requiring human input only at genuine decision boundaries.

The design extends Alpha-devbox's existing controller-runner architecture with a new agent class: one that generates tasks rather than executing them. The quant research workflow (iterative backtesting with hypothesis refinement) serves as the canonical example, but the architecture generalizes to any domain where experiments produce machine-gradeable results.

---

## Table of Contents

1. [Motivation: The Attention Bottleneck](#1-motivation-the-attention-bottleneck)
2. [Theoretical Foundation](#2-theoretical-foundation)
3. [Architecture Overview](#3-architecture-overview)
4. [The Outer Loop Agent: Human Imitation](#4-the-outer-loop-agent-human-imitation)
5. [The Inner Loop Agent: Verifiable Execution](#5-the-inner-loop-agent-verifiable-execution)
6. [The Feedback Bridge](#6-the-feedback-bridge)
7. [Skill and Intent System](#7-skill-and-intent-system)
8. [Continuum Learning](#8-continuum-learning)
9. [Quant Research: Concrete Walkthrough](#9-quant-research-concrete-walkthrough)
10. [Mapping to Alpha-devbox Primitives](#10-mapping-to-alpha-devbox-primitives)
11. [Safety and Verification Boundaries](#11-safety-and-verification-boundaries)
12. [Comparison with Prior Art](#12-comparison-with-prior-art)
13. [Implementation Roadmap](#13-implementation-roadmap)

---

## 1. Motivation: The Attention Bottleneck

The dominant AI interaction model is synchronous chat: human prompts, model responds, human prompts again. This model has a fundamental throughput constraint — human attention. Every iteration burns the scarcest resource in research: the researcher's focus.

The repetitive parts of research — generating variants, rerunning experiments, tightening assumptions, comparing baselines, extracting signal from failures, killing weak branches — are machine jobs. The human should not sit inside that loop. The human should sit above it.

**The core problem this RFC addresses:** How do you encode a human researcher's task-giving behavior — their priorities, style, iterative refinement patterns, and stopping criteria — into an agent that can drive a research loop autonomously, while preserving the human's ability to intervene at genuine decision boundaries?

This is not prompt engineering. This is behavioral cloning of a task dispatcher.

---

## 2. Theoretical Foundation

### 2.1 The Outer-Inner Loop Decomposition

Research work decomposes into two fundamentally different loops:

```
┌─────────────────────────────────────────────────────────────────┐
│  OUTER LOOP (compounding, slow, high-judgment)                  │
│                                                                 │
│  • Choose the problem                                           │
│  • Set the objective function                                   │
│  • Inject taste: "this direction feels dead, try X instead"     │
│  • Prune bad branches                                           │
│  • Decide what deserves another week of compute                 │
│  • Revise the framework when reality invalidates assumptions    │
│                                                                 │
│  Human operates here. Or: an agent trained to imitate           │
│  this human's specific decision patterns operates here.         │
└─────────────────────────┬───────────────────────────────────────┘
                          │ tasks, priorities, stopping criteria
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  INNER LOOP (recursive, fast, verifiable)                       │
│                                                                 │
│  • Generate variants of current hypothesis                      │
│  • Run experiments against ground truth                         │
│  • Compare against baselines                                    │
│  • Extract gradient from failures                               │
│  • Report structured results upward                             │
│  • Stop when local frontier is exhausted                        │
│                                                                 │
│  AI worker operates here. Always has.                           │
└─────────────────────────────────────────────────────────────────┘
```

The insight is that the outer loop, while requiring judgment, is **also patterned**. A given researcher tends to:
- Ask the same kinds of follow-up questions
- Prioritize the same metrics
- Have consistent taste about what "looks promising"
- Follow recognizable refinement trajectories
- Apply consistent stopping criteria

These patterns are learnable. Not perfectly — the human still supplies genuine novelty at decision boundaries — but well enough to keep the inner loop fed with work for hours or days without human attention.

### 2.2 Self-Recursive Improvement Requires a Verifiable Environment

A model can only improve itself if the environment can grade its moves. This is the fundamental constraint:

| Domain | Verification Signal | Feedback Latency |
|--------|-------------------|------------------|
| Software engineering | Tests pass/fail, type checks, linting | Seconds |
| ML research | Validation loss, eval metrics | Minutes to hours |
| Quantitative finance | Out-of-sample Sharpe, drawdown, turnover | Minutes |
| Mathematics | Proof verification, counterexample search | Seconds to hours |

Domains without machine-gradeable feedback (pure philosophy, taste-driven design, political analysis) cannot support autonomous inner loops. The outer loop agent must recognize this boundary and escalate to the human.

### 2.3 Behavioral Cloning vs. Reward Modeling

There are two approaches to encoding human task-giving behavior:

**Behavioral cloning** (what we propose): Learn the human's task-dispatch patterns from observation. Given the current state of research (results so far, open questions, resource budget), predict what task the human would assign next. This is a supervised learning problem over the human's historical task-giving traces.

**Reward modeling**: Learn a reward function that scores research states, then optimize task dispatch to maximize reward. This is more powerful in theory but requires much more data and risks reward hacking — the agent learns to produce states that score well on the proxy rather than states the human would actually value.

We start with behavioral cloning because:
1. It requires less data (dozens of task-giving episodes, not thousands)
2. It is more interpretable (the agent's reasoning mirrors the human's stated reasoning)
3. It degrades gracefully (when uncertain, it asks the human — which is the correct behavior)
4. It naturally captures the human's *style*, not just their *objectives*

### 2.4 The Skill–Intent–Priority Triangle

Drawing from Hermes Agent's skill system and the broader agent framework literature, we identify three orthogonal dimensions of human task-giving behavior:

```
                    INTENT
                   (what to achieve)
                      ╱╲
                     ╱  ╲
                    ╱    ╲
                   ╱      ╲
                  ╱        ╲
                 ╱          ╲
            SKILL ────────── PRIORITY
        (how to do it)    (what matters most)
```

- **Intent**: The research question or hypothesis. "Does momentum reversal at the 4h timeframe predict next-day returns?"
- **Skill**: The procedural knowledge for executing the intent. "Run a backtest with walk-forward optimization, report Sharpe, max drawdown, and regime-conditional performance."
- **Priority**: The value function for triaging results. "Sharpe above 1.5 is interesting. Drawdown above 15% is disqualifying. Regime stability matters more than raw returns."

A human researcher holds all three simultaneously. The outer loop agent must encode all three to generate useful tasks. Crucially, these are **personalized** — different researchers with the same intent will dispatch different tasks because their skills and priorities differ.

---

## 3. Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                         HUMAN RESEARCHER                             │
│                                                                      │
│  Intervenes at decision boundaries:                                  │
│  • New research direction    • Priority change    • Kill decision    │
│  • Offline truth injection   • Framework revision                    │
└──────────────────────┬───────────────────────────────────────────────┘
                       │ sparse, high-value interventions
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    OUTER LOOP AGENT ("Boss")                         │
│                    agents/research-boss/                              │
│                                                                      │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐     │
│  │ Human Model  │  │ Research     │  │ Priority                │     │
│  │              │  │ State        │  │ Function                │     │
│  │ • Style      │  │              │  │                         │     │
│  │ • Priorities │  │ • Hypotheses │  │ • Metric weights        │     │
│  │ • Patterns   │  │ • Results    │  │ • Kill thresholds       │     │
│  │ • Vocabulary │  │ • Branches   │  │ • Exploration budget    │     │
│  │ • Tempo      │  │ • Dead ends  │  │ • Escalation criteria   │     │
│  └─────────────┘  └──────────────┘  └─────────────────────────┘     │
│                                                                      │
│  Generates:                                                          │
│  • Next experiment specification (natural language + structured)      │
│  • Stopping / branching / escalation decisions                       │
│  • Progress summaries for human review                               │
└──────────────────────┬───────────────────────────────────────────────┘
                       │ task dispatch (via IPC / schedule_task)
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    INNER LOOP AGENT ("Worker")                        │
│                    agents/research-worker/                            │
│                                                                      │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐     │
│  │ Execution   │  │ Workspace    │  │ Verification            │     │
│  │ Skills      │  │ State        │  │ Environment             │     │
│  │             │  │              │  │                         │     │
│  │ • Backtest  │  │ • Code       │  │ • Test harness          │     │
│  │ • Sweep     │  │ • Data       │  │ • Metric computation    │     │
│  │ • Analyze   │  │ • Notebooks  │  │ • Baseline comparison   │     │
│  │ • Report    │  │ • Git hist.  │  │ • Regression detection  │     │
│  └─────────────┘  └──────────────┘  └─────────────────────────┘     │
│                                                                      │
│  Produces:                                                           │
│  • Structured experiment results                                     │
│  • Code changes (committed to workspace)                             │
│  • Failure analysis                                                  │
│  • "Gradient" — what improved, what degraded, what to try next       │
└──────────────────────┬───────────────────────────────────────────────┘
                       │ structured results
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    FEEDBACK BRIDGE                                    │
│                                                                      │
│  • Parses worker output into structured experiment record            │
│  • Appends to research state (experiment log, hypothesis tracker)    │
│  • Triggers outer loop agent for next-task decision                  │
│  • Detects escalation conditions → notifies human                    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 4. The Outer Loop Agent: Human Imitation

This is the novel component. The outer loop agent is not a general-purpose assistant — it is a **behavioral model of a specific human researcher**.

### 4.1 What We Clone

From observing a human's task-giving history, we extract:

**Dispatch Patterns** — The grammar of how this human gives tasks:

```
Pattern: REFINE_ON_PARTIAL_SUCCESS
Trigger: Worker reports Sharpe 1.2 (below 1.5 threshold but showing signal)
Human would say: "Interesting — the signal is there but weak. Try:
  1. Tighten the entry filter (require confirmation from volume)
  2. Test shorter holding periods (2h, 4h instead of 24h)
  3. Check if the signal is stronger in high-vol regimes"
```

```
Pattern: KILL_AND_PIVOT
Trigger: Worker reports negative Sharpe across all parameter sweeps
Human would say: "Dead end. The momentum reversal thesis doesn't
hold at this timeframe. Archive results. Move to mean-reversion
on the same universe — start with Bollinger band width as entry signal."
```

```
Pattern: DEEPEN_ON_STRONG_RESULT
Trigger: Worker reports Sharpe 2.1 with low drawdown
Human would say: "This looks real. Before we trust it:
  1. Run on 3 additional out-of-sample periods
  2. Add transaction cost sensitivity (2x, 5x current estimate)
  3. Check for lookahead bias — re-run with strict point-in-time data
  4. Compare against the 4 closest published factors"
```

**Priority Vocabulary** — The specific language this human uses to express importance:
- "This is the main thread" → high priority, allocate more compute
- "Side experiment" → low priority, time-boxed
- "Sanity check" → must pass before proceeding, but fast
- "I'm curious whether..." → exploration, no success threshold

**Tempo and Patience** — How long this human lets experiments run before intervening:
- After 3 failed variants: some humans pivot, others tighten parameters
- After a surprise result: some humans immediately want robustness checks, others want to push further first
- Overnight: what does this human expect to see in the morning?

**Escalation Judgment** — When to stop autonomous work and ask the human:
- Novel situation not covered by prior patterns
- Result that contradicts the human's stated priors
- Resource budget approaching limit
- Ethical or risk boundary
- Genuine ambiguity between two equally reasonable next steps

### 4.2 Representation: The Human Model File

We introduce a new artifact: `human-model.yaml`, stored in the agent definition directory.

```yaml
# agents/research-boss/human-model.yaml

researcher:
  name: "Bill"
  style:
    verbosity: concise           # concise | detailed | mixed
    notation: quantitative       # quantitative | narrative | mixed
    default_language: en         # primary language for task dispatch
    code_languages: [rust, python]

  priorities:
    primary_metric: sharpe_ratio
    secondary_metrics: [max_drawdown, turnover, regime_stability]
    kill_thresholds:
      sharpe_ratio: { below: 0.5, after_n_variants: 5 }
      max_drawdown: { above: 0.20 }
    interest_thresholds:
      sharpe_ratio: { above: 1.5 }
    exploration_budget:
      max_variants_per_hypothesis: 20
      max_hours_per_branch: 48

  dispatch_patterns:
    on_partial_success:
      action: refine
      typical_refinements:
        - tighten_entry_filter
        - test_alternative_timeframes
        - check_regime_conditioning
      max_refinement_depth: 3

    on_strong_result:
      action: deepen
      typical_checks:
        - out_of_sample_validation
        - transaction_cost_sensitivity
        - lookahead_bias_audit
        - published_factor_comparison

    on_failure:
      action: pivot_after_threshold
      pivot_threshold: 5    # variants before pivot
      pivot_strategy: adjacent_hypothesis

    on_ambiguity:
      action: escalate_to_human
      escalation_message_style: concise_with_options

  tempo:
    overnight_expectation: "morning summary with top 3 results"
    check_in_frequency: "every 6 hours or on breakthrough"
    patience_on_slow_convergence: moderate  # low | moderate | high
```

This file is **not hand-authored from scratch** — it is generated by analyzing the human's historical task-giving messages and refined through a calibration dialogue:

```
Boss Agent: "Based on your last 47 task messages, I've modeled your dispatch
patterns. Here's what I think you'd say after a Sharpe of 1.2:

  'Signal is there but weak. Tighten entry, test shorter horizons,
   check regime conditioning.'

Is that roughly right? What would you change?"