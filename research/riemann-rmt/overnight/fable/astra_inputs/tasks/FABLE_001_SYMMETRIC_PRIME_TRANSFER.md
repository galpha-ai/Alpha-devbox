# Fable task 001: independently test the arithmetic meaning of one symmetric-prime trial

**State: published, awaiting explicit pickup.** No evidence of Fable receipt or execution yet.
**Executor:** the user's ONE existing Claude Code/Fable 5.1 session. Do not create any Claude sessions or subagents, do not invoke parallel Claude calls, and do not start a next task after reporting. User reports selecting the highest mode; Astra has not independently verified that setting.
**Budget:** one bounded pass, at most about 45 minutes of computation and analysis. No open-ended parameter sweep. Return proof, counterexample, or the first exact missing step.

## Main theorem served

Under RH, seek a genuine zeta-zero normalized gap below 1/2. Inoue's resonance–correlation theorem is the current arithmetic interface: [arXiv:2604.05733v1, Theorems 2 and 4](https://arxiv.org/html/2604.05733v1). The observed half-gap negative margin is not yet crossed. This task decides whether a new symmetric-prime resonator family corresponds to the actual arithmetic theorem or only to an attractive continuum model.

Do not read the negative numerical output as a global no-go. Even a correct transfer of this trial will not prove the main theorem, because its margin is still negative. It will validate or invalidate a concrete new coefficient direction before further search.

## Files and exact baseline

Everything required for the computation is in `research/residual-gram/`:

- `inoue_variational.py` and `variational-results.json`: independent Jacobi-basis baseline.
- `original_inoue_probe.py` and `original_inoue_probe_results.json`: supplied original calculation, retained for independent comparison.
- `prime_feature_variational.py`: proposed symmetric-prime continuum Gram matrix.
- `rational_trial_certificate.py` and `rational-trial-certificate.json`: exact rational integral certificate for the fixed trial below.
- `arithmetic_operator.py`: finite coefficient-space operator, allowing a check not built from the proposed continuum moments.
- `check_algebra.py`: structural regressions; passing them does not prove an asymptotic theorem.
- `research/reports/residual_gram_round1.md`: full definitions, provenance, and gaps.

Use the commit containing this task as your fixed input. Report its SHA before beginning. Write only `research/fable/task001_report.md` and distinctly named independent verification scripts/results under `research/fable/task001/`. Do not change the input scripts or historical results. Do not commit or push without coordinating with the user's already active Fable workflow; a separate commit containing only your files is acceptable when that workflow is already authorized. Never force push or overwrite Astra files.

## Definition of the old and new margins

Set `phi=1/2`, `ell>0`, `a=ell^2`. The one-variable optimized continuum trial has margin

`J = M/I - phi*(1-phi)`.

Degree14 Jacobi search gives `ell=1.1762950386`, `J=-0.015357981703850554`. In the log-increment Hilbert-space normalization this deficit corresponds to `-2*pi^2*J=0.3031544076323465` of energy divided by the resonator norm. The published Inoue linear trial at `phi=.508949, ell=1.15, f(v)=1-.7v` has positive margin about `1.48716181335e-5`.

The proposed new coefficients are

`r(n)=d_ell(n)*H(v,S2(n))`,

`v=log(n)/log(L)`, `S2(n)=sum_{p|n}(log(p)/log(L))^2`, `n<=L`,

where `d_ell(p^e)=(ell)(ell+1)...(ell+e-1)/e!` and multiplication extends it to all n. The feature counts distinct prime divisors. This distinction matters for prime powers.

For the ONE fixed rational trial use `ell=16/15` and

`H(v,S)=f(v)+g(v)*S`,

`f(v)=(145+3v-116v^2+71v^3-6v^4)/100`,

`g(v)=(-563+1682v-2479v^2+1751v^3-488v^4)/100`.

The claimed continuum margin for this trial is in `(-1467/100000,-1465/100000)`, with tight enclosure approximately `[-.014662375473368995,-.014662375473368974]`. The exploratory richer-family value around `-.01465473` uses ill-conditioned generalized eigenproblems and is not this rational certificate.

## Proposed continuum schema to challenge

Let E_v denote a formal background-prime expectation with

`E_v[S]=v^2/(a+1)`,

`E_v[S^2]=(a+6)*v^4/((a+1)*(a+2)*(a+3))`.

Prime insertion of size u is `(v,S)->(v+u,S+u^2)`. Define

`I = integral_0^1 v^(a-1) E_v[H(v,S)^2] dv`.

At `phi=1/2`, the proposed numerator is `M=M2+M3`, with

`M2 = (2*ell^2/pi^2) integral_{v,u,w>=0; v+u+w<=1} v^(a-1) * sin(pi*u/2)/u * sin(pi*w/2)/w * E_v[ H(v,S)H(v+u+w,S+u^2+w^2) + H(v+u,S+u^2)H(v+w,S+w^2) ] dv du dw`,

`M3 = (2/pi^2) integral_{v,u>=0; v+u<=1} v^(a-1) * sin(pi*u/2)^2/u * E_v[H(v,S)^2] dv du`.

Values at zero are the continuous limits. The linear-in-resonator term vanishes at phi=1/2. The rational script integrates exactly this stipulated form using rational pi enclosures, Taylor remainders and simplex monomials. It does NOT establish that the form is the correct asymptotic of the integer sums.

## Your single main obligation

Independently derive, or find a defect in, the leading arithmetic evaluation of this fixed H trial under Inoue Theorem4. In particular check:

1. The normalization of `sum_{n<=L} d_ell(n)^2 H(v,S2(n))^2/n`, including the Euler-product constant and cancellation of the common factor.
2. The coefficients of the two prime-insertion terms: inserted prime coinciding with another insertion, `p|m` in the background, and prime powers. Determine whether the proposed M3 already accounts for all leading diagonal coincidences.
3. Whether the stated S2 moments follow from the weighted integer sum, rather than being assumed from a Poisson–Dirichlet model. Derive the relevant marked Euler product or Dirichlet convolution identity before invoking an asymptotic theorem.

An acceptable positive outcome is a complete derivation with a precise cited asymptotic theorem and an error tending to zero after normalization, including the short-background range. An acceptable negative outcome is one missing leading term or an explicit finite-sum calculation that contradicts the proposed limiting formula. If you only validate the continuum integral, say the arithmetic transfer remains open.

## Independent bounded finite-sum cross-check

As a diagnostic, build d_ell and S2 by a prime-power sieve for L in `{1000,10000,100000}`. Form `x_n=r(n)/sqrt(n)`. At the asymptotic boundary `logL/logT=1`, define sparse real A by

`A[q*m,m]=2*sin((pi/2)*log(q)/log(L))/(e*sqrt(q))` for `q=p^e`, `q*m<=L`.

Evaluate, without forming a dense matrix,

`J_L = ( ||A*x||^2 + dot(x,A*(A*x)) )/(2*pi^2*dot(x,x)) - 1/4`.

Compare the same finite formula with H=1 or a mass-only polynomial to diagnose finite-L drift. Finite-L results cannot prove the limiting transfer, and `L=T` is not itself a permitted finite instance of the theorem. Do not extrapolate three data points into an asymptotic proof.

## Reproducible commands

Use existing Python with numpy, scipy, sympy and mpmath. From repo root:

```text
OPENBLAS_NUM_THREADS=1 python3 research/residual-gram/check_algebra.py
python3 research/residual-gram/rational_trial_certificate.py
```

The full baseline reproduction is optional if needed to diagnose a discrepancy:

```text
OPENBLAS_NUM_THREADS=1 python3 research/residual-gram/inoue_variational.py
```

Do not run all parameter searches or the million-dimensional eigenproblem for this task. The fixed-vector finite-sum check is enough.

## Return format and stopping point

Give the strongest precise statement you established, the derivation or earliest failed step, independent computation and its normalization, and what this changes in the main proof. Label every result as exact algebra, certified continuum integral, finite numerical check, or proved arithmetic asymptotic. Return after this ONE task; wait for an explicit next task. No new Claude sessions, subagents or automatic next rounds.
