# Lean formalisation

`RiemannImpostors/DepthComparison.lean` formalises the deterministic core of the
two-body comparison theorem (Theorem A of the paper):

- `cot_strictAntiOn` — cot is strictly decreasing on (0, π)   [proved]
- `background_sign`  — every other zero slows the collapse of an adjacent pair   [proved]
- `neg_log_cos_ge`   — −log cos(x/2) ≥ x²/8 on [0, π)   [proved modulo `t ≤ tan t`]
- `two_body_solution` — cos(g s/2) = eˢ·cos(g 0/2)   [**sorry**: scalar autonomous ODE uniqueness]
- `depth_ge`          — the depth lower bound          [**sorry**: Grönwall-type comparison]

**Status: written, NOT compiled.** The authoring environment's egress policy denied
`elan.lean-lang.org` and GitHub release downloads (403), so no Lean toolchain was available.
Every algebraic step of the informal proof was instead machine-checked by exact symbolic
computation (sympy) and SMT (z3) — see `../verification/verify_theorem_steps.py`, 18/18 passing.

To build: install elan, then `lake update && lake build` in this directory. Expect the two
`sorry`s above; discharging them via Mathlib's `ODE_solution_unique` / Grönwall API is the
intended contribution for anyone picking this up.
