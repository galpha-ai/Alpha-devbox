# DevBox and AlphaDevBox: Concept

## What DevBox is

DevBox is an open-source Cloud Managed Agent. It lets a user host their own Cloud
Agent SDK, together with the ways it connects to other front ends, on Google
Cloud. At its core, DevBox is an agent built on Google Cloud's Cloud Agent SDK.

The difference from a generic coding agent is what sits inside. We built a large
set of tools so that this persistent, hosted agent can do tasks that traditional
coding agents cannot: rolling regression toolboxes, classical statistical
hypothesis testing, VS statistics, and other applied data-science workflows. This
set of problems is, in our view, a new and meaningful Agent Harness scenario —
one where even very strong general models behave more like a stepping stone than
a finished worker.

Right now, these workflows do not cleanly fit into the H3 / R11 style of system.
In practice, people still hand-build an agent harness to lift the adaptability of
traditional models on this kind of task. The most natural next research question
is: how do we expose this compute, cleanly, to the agent and to the user?

## What AlphaDevBox is

AlphaDevBox is the internal name for the financial-research layer built on top
of DevBox. Its core demo is simple to state:

> Backtest any idea with natural language.

More broadly: study any idea that can be studied with historical data, statistics,
or data-science methods. If the question is reachable by rolling regression,
hypothesis testing, or a predictive ML model, AlphaDevBox should handle it.

AlphaDevBox is aimed at people who like trading and have some quantitative or
backtesting-oriented way of thinking, want to build repeatable and verifiable
strategies, but either don't want to write code or don't know how. Many
discretionary traders have no quantitative tools; they can only rely on rough
intuition, and they can't use data to test or overturn their own views. With
AlphaDevBox, they can interact with the system in natural language to figure out
what they know and what they don't, and pay for access as ordinary users rather
than as engineering-heavy funds.

## Why this is not a generic coding agent

A traditional coding agent writes code. AlphaDevBox calls code. The difference
is who holds the research workflow.

Inside DevBox, the agent has a tool layer for:

- applied mathematics and statistics packages
- quantitative research packages
- ClickHouse historical data
- a financial historical simulator that can construct a simple historical-data
  environment
- persistent runtime state across long research sessions

These are wired into the agent harness so the user's natural-language intent is
turned into a real research procedure — not just a script.

We can also expose the ClickHouse historical data and the financial historical
simulator as a CLI that plugs into external coding agents. That works, but it
trades away the thing we actually care about: a shared, persistent research
environment that multiple people can use together.

## Collaboration model

DevBox + AlphaDevBox is designed to be multi-user from day one. A group can be
added to a Telegram or Slack workspace and compound research ideas on top of the
same hosted agent, the same historical data, and the same tool layer. The mental
model is programmers doing compound engineering in a shared Slack — except the
work product is research on historical financial data rather than code.

This gives the system a property that matters for serious research: a shared
facts layer. Everyone on the team is arguing over the same rolling regression,
the same backtest, the same attribution, instead of private spreadsheets.

## Core thesis in one paragraph

Any problem that can be framed as a hypothesis about historical data should be
reachable by natural language. The bottleneck for discretionary traders is not
ideas — it is the workflow to turn ideas into repeatable, verifiable,
falsifiable research. AlphaDevBox turns that workflow into an agent harness.
DevBox is the open-source platform underneath it.

## Open-source core

The open-source piece is not any single feature. It is the framework:

> Take the applied math, statistics, and quantitative-research tooling that a
> researcher would normally run by hand, and expose it as a reusable tool layer
> inside an agent harness running on a persistent cloud runtime.

Everything else — the UI, the collaboration layer, the financial data, the
paid access — sits on top of that.

## Terms to preserve

The following terms are internal or context-dependent. They are kept as-is and
should not be silently normalized:

- 灰色工具
- VS 统计 / DataS 统计
- Driver, Misos
- H3, R11
- shared facts
- compound research, compound engineering
