---
name: inv-option-pricing-sde
description: Option pricing and stochastic-process modeling for single-stock American options — use for computing fair values, early-exercise decisions, extracting implied event jumps, calibrating SDE models (GBM, Heston, jump-diffusion) to a CBOE surface, implied borrow/dividend extraction, and validating any options math with put-call parity and convergence tests. The quantitative engine behind inv-options-pressure.
---

# American Option Pricing & SDE Modeling

Persona: the applied-math PhD seat. Everything here is verifiable against
closed forms and parity — so verify, every time. No pricing number ships
without its checks block.

## The American single-stock reality

US single-stock options are American with discrete dividends — Black-
Scholes is the *reference frame*, not the price:

- **Calls**: early exercise only just before a discrete dividend, and only
  when dividend > remaining time value at the ex-date. Otherwise American
  call ≈ European.
- **Puts**: early exercise driven by interest on strike vs time value —
  deep-ITM puts on high-rate regimes carry real premium; this is why
  BL-density extraction (`inv-options-pressure`) uses OTM only.
- **Implied borrow**: for hard-to-borrow names the effective carry makes
  puts rich / calls cheap; back out the implied rate from parity at
  near-ATM and hand it to `inv-short-interest`. A parity "arbitrage" in a
  meme name is almost always the borrow, not free money.

## The pricing stack (implement in quantlab, verify each layer)

1. **CRR binomial with discrete dividends** (escrowed-dividend or
   piecewise-forward handling — document which): the workhorse for
   American exercise. Convergence check: European limit → BS closed form
   within tolerance as steps ↑; Richardson-extrapolate node counts.
2. **Barone-Adesi–Whaley**: fast approximation for screens over whole
   chains; spot-check against binomial before trusting a screen.
3. **Longstaff–Schwartz LSMC**: when path-dependence or multi-factor
   models require simulation; regression basis choice documented; standard
   errors reported.
4. **Surface fitting**: SVI (or constrained spline) per expiry in
   log-moneyness, no-arbitrage checks (butterfly ≥ 0, calendar
   monotonicity) — shared with the BL pipeline.

## SDE toolkit (what each model is *for*)

- **GBM**: the null. Fit realized vol; its failures (skew, kurtosis,
  vol clustering) are the features other models price.
- **Heston (stochastic vol)**: for term-structure and skew dynamics;
  calibrate to the surface (feller condition checked, parameter bounds
  sane); use for scenario-consistent repricing ("if spot -15% and vol
  regime shifts, what does my book do") rather than "the true model".
- **Merton jump-diffusion**: the right frame for **event risk** — a
  binary print is a jump, not diffusion. Extract the implied jump: fit
  diffusive vol from post-event expiries, attribute the front-expiry
  excess variance to a jump distribution (size and probability). This is
  the rigorous version of "implied earnings move" and feeds the whisper
  triangulation (`inv-revenue-projection`) and your scenario-vs-implied
  comparison (main skill stage 7).
- Regime honesty: single-stock vol has earnings seasonality and gamma
  regimes — calibrations are per-window, dated, and stored with their
  data partition in the lake.

## Uses in the system (why this skill exists)

1. **Mispricing detection**: model value vs market across a chain →
   candidates for expression choice (when the decision layer wants a
   position, the cheap part of the surface is the instrument).
2. **Event-jump extraction** → implied scenario distribution vs yours.
3. **Squeeze mechanics quantification**: dealer hedge flow per $1 spot
   move from the gamma profile under your GEX sign assumption
   (`inv-options-pressure`) — turns "gamma squeeze" from a meme into a
   flow number comparable to ADV.
4. **Early-exercise/assignment hygiene** on any actual position around
   ex-dates.

## Verification block (mandatory in any output)

Every pricing/calibration deliverable includes: put-call parity residuals
across the chain (with borrow-adjusted carry); European-limit convergence
result; no-arbitrage surface checks; calibration RMSE in vol points with
per-expiry breakdown; and the data partition (`dt=`) used. A number
without its checks block does not leave the notebook.

Numerical work follows `inv-quant-foundations` discipline; heavy loops
(binomial trees over whole chains, LSMC paths) belong in the Rust core of
quantlab with Python bindings, not in Python loops.
