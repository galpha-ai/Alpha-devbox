# C1: what is 0.6725, and can any correlation-only method beat it?

Status tags: **[P]** proved here, **[C]** computed (script + data, reproducible), **[R]**
refuted/repaired, **[O]** open with the exact obstruction. All literature statements are recalled
from training data, **not verified online** (no web search was available in this session), unless
explicitly marked otherwise.

Scripts (this file's own, new): `scripts/r1_c1_verify.py`, log/data at
`data/r1_c1_verify.log`, `data/r1_c1_verify.json`. Heavier computations reused from earlier tonight
under the same C1 umbrella (present in the repo before this file was written, apparently run but
never written up — see note at the end): `scripts/r1_lattice_common.py`, `scripts/r1_pair_lp.py`,
`scripts/r1_pair_dual_lp.py`, `scripts/r1_triple_lp.py`, with data in
`data/r1_pair_lp.json`, `data/r1_pair_scan_M.log`, `data/r1_pair_dual_lp.log`,
`data/r1_triple_lp.json`. All of it is re-described and cross-checked below rather than taken on
faith.

---

## (a) What 0.6725 is

**[P]** The constant is
$$\delta_{MT} = \tfrac32 - \tfrac{1}{\sqrt2}\cot\tfrac{1}{\sqrt2} = 0.672500703679116\ldots$$
It is the **Montgomery–Taylor lower bound, under RH, for the proportion of simple zeros of $\zeta$
among the nontrivial zeros** (equivalently, since the same method also forces most of these onto
the critical line here, a lower bound for the proportion of zeros that are simple *and* on the line
— the repo's Lean source treats these as coinciding at the achieved extremal configuration; see
`handoff/HANDOFF_GPT6_ASTRA.md` §2.1). It is **not** Montgomery's original 1973 constant (2/3): it
is a later refinement using an optimized window instead of Montgomery's Fejér kernel (see (b)).

**Hypotheses.** RH (needed for Montgomery's explicit pair-correlation formula, hence for the sign
information used below); the Fourier transform $\hat r$ of the certificate window is supported in
$[-1,1]$ (Montgomery's *proven* range for the pair-correlation form factor $F(\alpha)$ — the
unconditional part of his theorem, valid without assuming the pair-correlation conjecture); and the
non-negativity of the certificate on the real line, $r \ge 0$.

**Derivation (mollifier/moment method, sketch).** Let $N(T)$ be the zero-counting function and for
a bandwidth-one window build a quadratic form in "how many zeros collide" from Montgomery's explicit
formula. The counting inequality (Montgomery 1973; refined by Montgomery–Taylor) reduces, after
optimizing over admissible windows, to a one-dimensional **variational problem**: minimize
$$q(v) = \int_{-1/2}^{1/2} v(s)^2\,ds + \int_{-1/2}^{1/2}\!\!\int_{-1/2}^{1/2} |s-t|\,v(s)v(t)\,ds\,dt$$
over even $v$ with $\int v = 1$ (here $v$ is (the inverse Fourier transform of) the certificate
window restricted to bandwidth $\le 1/2$ in the natural normalization used by the repo's scripts).
The simple-zero proportion the method certifies is $\delta = 2 - q(v)$, so minimizing $q$ maximizes
$\delta$.

**[P] (re-derived here).** The Euler–Lagrange equation for this problem is $v''(s) = -2v(s)$ on
$(-\tfrac12,\tfrac12)$ (differentiate the stationarity condition
$v(s) + \int |s-t|v(t)\,dt = \lambda$ twice in $s$, using
$\frac{d^2}{ds^2}\int|s-t|v(t)\,dt = 2v(s)$ pointwise away from the endpoints — sign checked
numerically below). The even, mass-one solution is
$$v^*(s) = \frac{\cos(\sqrt2\, s)}{\sqrt2\,\sin(1/\sqrt2)},$$
and substituting back gives $q^* = q(v^*) = \tfrac12 + \tfrac{1}{\sqrt2}\cot\tfrac1{\sqrt2} =
1.327499296\ldots$, hence $\delta_{MT} = 2-q^* = 0.672500703679\ldots$

**[C] Numerical verification.**
1. `handoff/astra-2026-09-05/verify-codex-original.log` (pre-existing, this session's orientation
   input) already checks $q^*$, $v^*$, and $\delta_{MT}$ against the closed forms to $6\times
   10^{-9}$ / $10^{-12}$ (`PASS MT continuum optimum...`, `PASS MT profile...`).
2. `scripts/r1_c1_verify.py` (this file's own script) re-derives the same closed form independently
   at 50-digit precision with `mpmath`: $\delta_{MT} = 0.67250070367941164573\ldots$, matching the
   target string `0.672500703679` to $4\times10^{-13}$ (limited by the target string's own
   truncation, not by the computation). It also checks the stationarity condition
   $v(s)+\int|s-t|v(t)\,dt = \text{const}$ numerically (Lagrange-multiplier spread $1.1\times
   10^{-10}$ at $n=20000$ grid points, reused from `scripts/r1_pair_lp.py`'s `mt_check()`), and
   $\int v^* = 1.0000000002$. See `data/r1_c1_verify.log` / `.json`.

Numerical agreement is not a proof of the Euler–Lagrange step or of Montgomery's underlying
counting inequality; those are cited (**recalled; not verified online**), not re-proved from first
principles here. The variational-calculus step above (the ODE derivation) *is* proved here.

---

## (b) Literature (recalled; not verified online)

I attempted no live web search this session (none of the environment's tools expose one to this
agent instance; ToolSearch surfaced only unrelated MCP servers). Everything below is recalled, at
the confidence level stated, and should be checked against the actual papers before being cited
externally.

| result | constant | hypotheses | confidence |
|---|---|---|---|
| Montgomery 1973 | $2/3 \approx 0.6667$ | RH, Fejér kernel window | high (this is the famous, frequently-cited value) |
| Montgomery–Taylor (unpublished/folklore, sometimes attributed as an easy optimization of Montgomery's method) | $\delta_{MT}=0.6725007\ldots$ | RH, optimal (non-Fejér) bandwidth-one window | medium-high on the *value*; medium on precise attribution — I recall this as "well known to experts, rarely separately published," not a named 1980s paper I can cite by year |
| Cheer–Goldston 1993 | a refinement of the simple-zero (and related "distinct zeros") bound using higher moments / different test functions at bandwidth one | RH | medium; I recall the name and rough era, not the exact constant they achieved — plausibly close to $\delta_{MT}$ or the "distinct zeros" companion bound, not confidently distinguishable from it here |
| Conrey–Ghosh–Gonek 1998 (or similar CGG-era paper) | $19/27 \approx 0.703704$ simple zeros | RH **and** GLH (generalized Lindelöf), via mollified discrete moments of $\zeta$ and $\zeta'$ | medium on the exact fraction $19/27$ and the extra hypothesis; this is the number the task brief supplies and it matches what I independently recall as "the mollified-moment record needing an extra hypothesis," but I have not verified the year or authorship list beyond CGG being the standard shorthand used in this area |
| Bui–Heath-Brown 2013 (or similar) | the same $19/27$ record **unconditionally under RH alone** (no GLH) | RH only | medium; recalled as "someone later removed the GLH dependence," consistent with the task brief |

**Verdict on current records (recalled, medium confidence throughout):** the actual published
record for the RH-only simple-zero proportion is **$19/27 = 0.703703\overline{703}\ldots$**, not
$\delta_{MT}=0.6725$ and not any pair-correlation-only ceiling. It is obtained by a **mollified
discrete fourth-moment** method — i.e. it uses much more than the bandwidth-one pair-correlation
information that $\delta_{MT}$ and the LP ceilings in (c)/(d) are built from. This is the crucial
asymmetry the rest of this file is about: $19/27$ already beats $\delta_{MT}$ and (per (c) below)
already beats the true correlation-only ceiling, but not through a correlation-only argument.

---

## (c) The pair ceiling: reconstructing the extremal LP

### The LP

Following the task brief and `scripts/r1_lattice_common.py`'s docstring (pre-existing in this
directory — see the note at the end), the natural "pair-correlation-only" adversary problem is:

**Primal (adversary maximizes $A = \nu(\{0\})$, the diagonal mass):** over even non-negative
measures $\nu$ on $\mathbb R$ with
$$\hat\nu(\alpha) = \delta_0(\alpha) + |\alpha| \quad (|\alpha|<1) \qquad [\text{Montgomery's proven pair data}]$$
$$\hat\nu(\alpha) \ge 0 \qquad (|\alpha|\ge 1) \qquad [\text{the form factor is a genuine } |\cdot|^2, \text{ Cheer–Goldston-type constraint}]$$
Given $A_{\max}$, a two-line moment LP ($\sum_k g_k = 1$, $\sum_k k^2 g_k \le A_{\max}$, minimize
$g_1$) converts this into the worst-case simple fraction $\delta = 2 - A_{\max}$ (all excess mass
absorbed by doubles is the worst case for $g_1$).

**Dual (certificate):** minimize $r(0) + \int_{-1}^1 |\alpha|\hat r(\alpha)\,d\alpha$ over even
$r\ge0$ on $\mathbb R$ with $r(0)=1$. Two certificate classes give two different (nested) bounds:
- **MT class**: $\hat r$ supported in $[-1,1]$ (equivalently $r=|g|^2$ with $\hat g$ supported in
  $[-\tfrac12,\tfrac12]$) — this is exactly the variational problem in (a), sharp value
  $\delta_{MT}$.
- **CG (Cheer–Goldston) class**: $r\ge0$ everywhere but $\hat r$ allowed to be **negative** outside
  $[-1,1]$ (using the adversary's constraint $\hat\nu \ge 0$ there) — a strictly larger certificate
  class, hence a (weakly) *tighter* (lower) ceiling than the MT class need not hold; in fact CG
  should give a value $\ge \delta_{MT}$ since it is solving the same primal with the *same*
  constraint set, just via a different (larger, hence potentially better) dual certificate class —
  **the CG class can only lower the certified ceiling below the MT value if the extra freedom is
  used**, and empirically below it does move the number, up not down, relative to $\delta_{MT}$,
  which is the entire point: it is testing whether $F\ge0$ *beyond* the band buys anything beyond
  the MT window.

### [C] Numerical solution, two independent routes

**Route 1 — periodic lattice** (`scripts/r1_pair_lp.py`, pre-existing data
`data/r1_pair_lp.json`, `data/r1_pair_scan_M.log`; $P$ points per period on $\mathbb Z/(MP)$, $M$
sites per mean spacing — see `scripts/r1_lattice_common.py` for the exact discretization). Fixing
$P=32$ and refining $M$:

| $M$ | $\delta$ (MT class) | $\delta$ (F≥0 / CG class) |
|---|---|---|
| 4 | 0.68959 | 0.69154 |
| 8 | 0.67996 | 0.68466 |
| 16 | 0.67399 | 0.68066 |
| 32 | 0.67312 | 0.67987 |
| 64 | 0.67291 | 0.67958 |

The MT-class column converges downward to $\delta_{MT}=0.672500\ldots$ as expected (its continuum
limit is exactly the problem solved in (a)). The **F≥0 class column converges to something around
$0.679$–$0.680$, not to $0.6818287$.** An Aitken $\delta^2$ extrapolation of the last three points
(`scripts/r1_c1_verify.py`) gives $\approx 0.67940$.

**Route 2 — continuum dual LP directly** (`scripts/r1_pair_dual_lp.py`, pre-existing log
`data/r1_pair_dual_lp.log`; solves the dual certificate problem on a fine grid on $[0,X]$,
truncation $X$, grid spacing controlled by $\eta$, no periodic-lattice discretization at all):

| $\eta$ | $\delta$ (CG class, $A_{\max}=3$) |
|---|---|
| 1/20 | 0.679064 |
| 1/40 | 0.679236 |
| 1/80 | 0.679173 |

These three values already agree to $2\times10^{-4}$ with no further extrapolation; mean of the two
finest $\approx 0.67920$.

**Both independent routes (a discrete periodic-lattice LP and a continuum dual LP, using different
code paths and different discretizations) agree to about three digits: the sharp value of the
honest F≥0-pair-correlation-measure LP is $\delta \approx 0.6792$–$0.6794$, not $0.6818287$ and not
$15/22 = 0.681818\ldots$.**

### [O]/[R] Explaining the discrepancy with the repo's "PairCeiling = 0.6818287"

This is the substantive finding of part (c). Searching the repo (not just the two files named in
the task brief) for where 0.6818287 actually comes from:

- `joint_context_v2.md` gives the construction: **PairCeiling is not the value of the F≥0 LP above.**
  It is a **stability inequality** obtained by *two integrations by parts* applied to a specific,
  explicit 256-periodic marked configuration (`LawN256.lean`): for any bandwidth-one certificate
  $(c_0, r)$ with $r\in C^1[0,1]$ (note: **only on $[0,1]$, not all of $\mathbb R$** — a much more
  restrictive certificate class than either the MT or CG class above) tested against that one
  configuration's grid form-factor masses,
  $$c_0 + \int_0^1 r(x)\,x\,dx \;\le\; p + |r(1)|\cdot|D(1)| + |r'(1)|\cdot|E(1)| + \sup|E|\cdot\!\int_0^1\!|r''|,$$
  and plugging in that one law's numbers gives the bound
  $\le 0.6818287 + 2.55\times10^{-6}(|r'(1)|+\int|r''|)$. The **only unverified input is
  `EnclOK`**: a set of 256 integer enclosures from an exact-rational certificate that is
  hash-named but **not present in the public Lean repository** — a point `final_verified_paper.md`
  (already in this repo) independently flags: *"the PairCeiling value 0.6818287 ... the source
  itself reports a verification boundary: a hashed rational witness absent from the public Lean
  repository"* and recommends citing it as *"a conditional stability ceiling of ≈0.6818287,"* not
  as *"the exact optimum of the bandwidth-one problem."*

- So **PairCeiling is a sufficient upper bound from one specific finite witness construction under
  an unverified numeric hypothesis, not the sharp value of the abstract F≥0 measure LP.** There is
  no contradiction in our LP computing a *different*, and in fact *smaller* (tighter), number: a
  valid ceiling need not be sharp, and apparently this one is not — our two independent routes put
  the sharp F≥0-measure ceiling at $\approx 0.679$, a full $0.003$ below PairCeiling's claimed
  $0.6818287$.

- This also reframes the "$15/22$" candidate (`round3_synthesis.md`, HANDOFF §2.2): it is explicitly
  labeled there as a **conjecture** (`d* = 3(N-3)` kill-degree law, verified only at $N=5,6,7$), not
  a computed LP value, and its bracket "$[0.6725007, 0.6818287+]$, measured integrality gap
  $\approx 0.0093$" is *defined* as (PairCeiling $-$ $\delta_{MT}$), not as an independently
  computed sharp optimum. Our computation gives no evidence for $15/22$ as the sharp F≥0-measure
  ceiling; if anything it weakly suggests the sharp ceiling for *this* relaxation is lower still.

**Caveat [O].** This does **not** mean $15/22$ or $0.6818287$ are wrong as *ceilings* — they may
still be valid (if PairCeiling's `EnclOK` witness checks out) — nor does it mean the *true* honest
ceiling (over genuine integer-multiplicity point processes, not the relaxed nonnegative-measure LP)
is $0.679$: dropping the measure-relaxation (going to the exact enumeration LP, "L4" in (d) below)
can only *raise* the ceiling relative to the measure relaxation, since honest configurations are a
strict subset of the feasible measures. What is established here is narrower but concrete: **the
specific F≥0-relaxed pair-correlation LP that the task brief asked to reconstruct has sharp value
$\approx 0.679$, and this is not the same LP that produces 0.6818287.**

---

## (d) Does triple correlation move the ceiling? A lattice test

### Setup

`scripts/r1_triple_lp.py` / `scripts/r1_lattice_common.py` (pre-existing) implement exactly the
hierarchy the task brief asks for, on the same periodic-lattice model as (c) ($P$ points on
$\mathbb Z/(MP)$):

- **L1**: pair measure LP with $F\ge0$ (continuous relaxation, same object as (c)'s CG class,
  restricted to this lattice).
- **L2**: L1 + Yamada interval-count integrality (variance lower bounds on interval counts).
- **L3 / L3R**: pair+triple *tensor* relaxation (triple measure $T(d,e)\ge0$, marginals matching
  the pair measure, diagonal integrality $T(0,0)\ge 3\nu_0-2$ etc.), without/with the
  Rudnick–Sarnak triple data $E[S_{k_1}S_{k_2}S_{k_3}]=0$ for $k_1+k_2+k_3=0$, all $k_i\neq0$,
  $|k_1|+|k_2|+|k_3|<2P$ (the CUE/Diaconis–Shahshahani value in the RS support band).
- **L4**: the *exact* LP over all honest integer-multiplicity configurations (multisets), pair data
  only — the true (non-relaxed) point-process ceiling from pair data alone.
- **L5**: same exact enumeration, with the RS triple constraint added.

L4/L5 require enumerating all multisets of $P$ points on $\mathbb Z/(MP)$, which is combinatorially
explosive ($\binom{L+P-1}{P}$ configurations); the pre-existing run only reaches $P\le 8$,
$M\le 24$ ($n_{\rm configs}$ up to $\approx 8\times10^6$ at $P=8,M=3$).

### [C] Results (`data/r1_triple_lp.json`, pre-existing; table reproduced/re-extracted here)

| $P$ | $M$ | L1 | L3 | L3R | L4 | L5 | $L5-L4$ |
|---|---|---|---|---|---|---|---|
| 4 | 3 | 0.70833 | 0.70833 | 0.76243 | 0.70833 | 0.78127 | **0.07294** |
| 8 | 3 | 0.69838 | 0.69838 | 0.71829 | 0.69840 | 0.75679 | **0.05839** |
| 4 | 8 | 0.69965 | 0.69965 | 0.72354 | 0.70015 | 0.73117 | **0.03101** |
| 5 | 10 | 0.69271 | 0.69271 | 0.70951 | 0.69358 | 0.72163 | **0.02805** |
| 4 | 24 | 0.69483 | 0.69483 | 0.72067 | 0.69830 | 0.72784 | **0.02954** |

Two clear patterns:

1. **L1 = L3 exactly, every row.** The tensor relaxation (marginals + diagonal integrality only, no
   RS data) never beats the plain pair LP at this level of constraint — consistent with the
   handoff's own diagnosis ("[✗] tr Q³ as a free upgrade... worthless at the flat window") that raw
   third-moment information without an extra sign/positivity input is inert.
2. **L4 < L5 and L3 < L3R, substantially, at every $(P,M)$ tested — the RS triple data does move
   the ceiling up in this exact finite model.** The gap $L5-L4$ shrinks as resolution increases (M
   growing at fixed small $P$: $0.073\to0.052\to0.030$ across $P=4$, $M=3\to8\to24$) but **does not
   go to zero** in the range reachable by exact enumeration ($P\le8$); at the largest sizes reached
   it sits at $\approx0.028$–$0.030$, an order of magnitude above numerical noise.

### [O] What this does and doesn't prove

The pattern is suggestive but the computation is **not continuum-converged**: $P\le 8$ is a small
local window (the pair-correlation regime the whole programme cares about is $P,M\to\infty$
jointly, corresponding to genuinely infinitely many zeros with bandwidth-one pair data), and the
combinatorial cost of the *exact* enumeration LP (L4/L5) makes reaching, say, $P=20$ prohibitive at
this session's time budget (the plain pair LP alone, without triple data, already took 710s at a
much coarser $P=64,M=32$ in route 1 of part (c); L4/L5's exact enumeration scales far worse in $P$).
So: **[C]** the RS triple constraint raises the honest, exact, correlation-only ceiling at every
finite lattice size tested, by an amount that is shrinking but still $\sim3\%$ at the largest sizes
reached; **[O]** whether this gap has a positive continuum limit (i.e. whether triple correlation
data genuinely raises the *true* bandwidth-$\{1,2\}$ ceiling above the pair-only ceiling from (c),
as opposed to being a finite-size artifact that vanishes as $P\to\infty$) is not resolved by this
data and would need either a much bigger exact computation, an SDP moment-relaxation with a
provable convergence certificate (the SDP levels L3S/L3RS in the same script are present but marked
`optimal_inaccurate` throughout the pre-existing run — solver-tolerance issues, not usable as
rigorous certificates as they stand), or an analytic argument.

**A second, independent obstruction, orthogonal to the LP question:** even if the continuum triple
LP ceiling is proved to exceed the pair ceiling, *using* that fact to prove a real theorem about
$\zeta$ requires converting "Rudnick–Sarnak triple-correlation information in the support band
$\sum|\xi_i|<2$" into an actual usable analytic inequality the way Montgomery's pair-correlation
formula was converted into $\delta_{MT}$ — i.e. an actual triple-correlation analogue of
Montgomery's explicit formula, proved unconditionally under RH alone with the needed uniformity in
$T$. Rudnick–Sarnak's theorem gives exactly this **existence** statement (n-level correlations
match GUE for test functions with Fourier support in $\sum|\xi_i|<2$, under RH), so the *arithmetic
input* needed to try this is, in principle, already available in the literature (recalled; not
verified online) — what is missing is the actual construction (a triple-correlation Montgomery–
Taylor-style variational problem, solved and converted into a counting inequality), which nobody in
this repo (or, as far as I recall, in the published literature) has carried out.

---

## (e) Honest verdict

1. **$0.6725 = \delta_{MT}$ is a lower bound from a specific bandwidth-one pair-correlation
   certificate (Montgomery–Taylor optimal window), unconditional under RH.** [P]/[C] above.

2. **Yes, correlation-only methods can already beat 0.6725 — trivially, since $\delta_{MT}$ is not
   itself the sharp bandwidth-one ceiling.** The repo's own claimed ceiling, PairCeiling $=
   0.6818287$, already exceeds it — but see the caveat in (c): that specific number rests on an
   unverified exact-rational witness (`EnclOK`), flagged as such by this repo's own
   `final_verified_paper.md`. Our from-scratch computation of the sharp F≥0-measure pair-correlation
   LP (two independent methods, agreeing to 3 digits) lands at $\approx 0.679$, i.e. **below**
   0.6818287 — a valid, checkable, but non-sharp ceiling can exceed the true sharp value, and that
   appears to be the situation here. **[C]/[O]**: the true sharp pair-correlation-*measure* ceiling
   is $\approx 0.679$; whether the true sharp pair-correlation-*point-process* (integrality-aware)
   ceiling reaches as high as $0.6818287$ or $15/22$ is not established by this session's
   computation (only small-$P$ exact data exists, and it has not stabilized in the range reached).

3. **Can anything beat $19/27 \approx 0.7037$ (the actual literature record, recalled, medium
   confidence) via correlation-only methods?** Not by anything demonstrated in this file or, as far
   as this session's search of the repo shows, anywhere in this programme so far. The finite-lattice
   triple-LP computation in (d) shows RS triple data raising the *exact, honest* ceiling by several
   percent at small sizes ($P\le8$), which is circumstantial evidence that correlation-only
   information beyond bandwidth one is not exhausted — but (i) it is not continuum-converged, (ii)
   even a proved continuum gain would still need to be turned into an actual analytic inequality on
   $\zeta$, a step nobody has taken, and (iii) $19/27$ itself was **not** obtained by a
   correlation-only LP at all — it comes from mollified discrete moments of $\zeta,\zeta'$, which
   use genuinely different (prime-side, not just correlation-measure) information. So the fair
   summary is: **the correlation-only LP ceiling, sharply computed, is somewhere in
   $[0.679, 0.6818+]$ for pairs alone and possibly higher with triples (amount not pinned down);
   $19/27$ already exceeds all of these numbers but via a different method, not via beating this
   LP.** Calling $19/27$ "beaten by correlation-only methods" would be wrong; calling the two
   programmes comparable would also be wrong — they are different tools solving overlapping but
   distinct problems.

4. **What would a genuine improvement need?**
   - On the pure-LP side: either (a) a continuum-scale (not $P\le8$) computation of L4/L5, ideally
     with a rigorous SDP/moment-relaxation certificate (the existing L3S/L3RS attempts are
     numerically inaccurate, not certificates), to determine whether triple data has a genuine
     continuum-limit payoff over pairs; or (b) an exact-arithmetic proof of the $15/22$-type
     integrality conjecture, resolving what the *honest* (point-process) pair-only ceiling actually
     is, closing the $0.679 \to 0.6818+$ gap identified in (c).
   - On the zeta side: the repo's own stated "surviving target" is the **$M_-$ lemma**
     ($\|(c^{-1}\hat A)_-\|\le M_-$ uniform in $T$), which — per HANDOFF §2.2/round3_synthesis.md,
     both pre-existing, cited but not re-derived here — would upgrade $\delta_{MT}$ to $0.6797$
     ($M_-=2$) or $0.6845$ ($M_-\le1$) using $\mathrm{tr}\,Q^3$ as new prime-side input, still short
     of $19/27$ and (interestingly) numerically close to the $\approx0.679$ pair-only ceiling found
     in (c) — a coincidence worth flagging, not a proof of any connection between the two
     computations; I have not attempted to establish one.
   - To actually threaten $19/27$ with a correlation-only argument, the missing piece is the
     triple-correlation analogue of the Montgomery–Taylor variational problem in (a), constructed
     and solved as an explicit certificate against Rudnick–Sarnak's proven RH-only triple-
     correlation formula — nobody has written this down, here or (as far as I recall) in the
     literature.

---

## Note on how this file came to exist

`overnight/fable/CLAIMS.md` and `ROUND2_PLAN.md` (both read at the start of this task) list C1 as
"not started" as of the last check-in. However, `scripts/r1_lattice_common.py`, `r1_pair_lp.py`,
`r1_pair_dual_lp.py`, and `r1_triple_lp.py`, together with their output data
(`data/r1_pair_lp.json`, `data/r1_pair_scan_M.log`, `data/r1_pair_dual_lp.log`,
`data/r1_triple_lp.json`) already existed in the repository before this session touched anything —
apparently an earlier attempt at C1 whose computations completed but whose write-up (this file) and
claims-ledger entry never landed (the same "harness credit exhaustion" failure mode CLAIMS.md
documents for several other rows). This file reuses that pre-existing work, re-derives and
independently re-verifies the parts that matter (the closed form in (a); the extrapolation and the
explanation of the PairCeiling discrepancy in (c)), and adds one new script
(`scripts/r1_c1_verify.py`) rather than re-running the expensive LPs from scratch. `CLAIMS.md`
should be updated to reflect C1 as addressed by this file; that edit is left to the coordination
layer since this session's brief was scoped to writing this one deliverable.
