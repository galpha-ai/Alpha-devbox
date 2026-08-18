# Telling the Riemann Zeros from Their Impostors

## A key step toward the alternative hypothesis, and a new bridge between zeta zeros and random matrix theory

**Bill (Qingyun) Sun · GPT5.6SOL · Fable**

*August 2026*

---

## What this is about

The zeros of the Riemann zeta function are conjectured to be spaced like the eigenvalues of a
large random unitary matrix. This is Montgomery's pair correlation conjecture, and half a century
of work has not settled it. The obstruction has a name: the **alternative hypothesis**, the
scenario in which the normalised gaps between zeros all lie asymptotically on a half-integer
lattice rather than fluctuating like a random spectrum. It is consistent with everything currently
provable, it has genuine arithmetic consequences, and — this is the hard part — it *imitates* the
random-matrix answer for every statistic anyone has managed to test.

Tao made the obstruction concrete by moving it into random matrix theory. The **ACUE** is a
lattice-supported measure on unitary spectra that reproduces the random-matrix two-point
correlation exactly. The programme of "find the first statistic ACUE cannot fake" has been running
ever since and keeps hitting the same wall: the set of measures matching any finite list of
moments is a large convex body, so ruling out ACUE never rules out its neighbours.

This paper does four things.

**We measure the wall exactly.** The family of impostors — measures matching every balanced moment
of degree ≤ N — has dimension 0, 0, 2, 10, 80, 403, 1804 for N = 3, …, 9. We give closed-form
families for every N, and show they remain invisible along the *entire* natural heat flow, because
that flow is diagonal in the coefficients. Adding one more moment, or evolving the moments you
have, is provably futile.

**We find an instrument that sees past it.** Not an average, but a *stopping time*: the finite
de Bruijn–Newman depth Λ, the first moment at which two zeros collide when the heat flow is run
backwards. It is not a polynomial statistic of any degree, so the impostors' freedom does not
protect it. It separates the random-matrix and lattice scenarios not by a number but by a
**universality class**: −Λ ≍ N^{−8/3} against N^{−2}. The alternative hypothesis fails not by being
fragile but by being **too stable** — it satisfies its own Riemann-hypothesis-analogue far too
robustly.

**We find the structure underneath, and it is the point of the paper.** The static invisibility
depth of the impostors and the dynamic relaxation spectrum of the flow turn out to be *the same
operator*. Concretely, the quantity δ(N−δ) that governs how deeply an impostor can hide is
simultaneously the dimension of a Grassmannian, an affine Bruhat length, and — the new equality —
the eigenvalue of the Jacobian of the zero dynamics at the clock configuration. This explains the
whole phenomenon in one sentence: *impostors hide in exactly the modes the flow acts on most
strongly*, which is why a hitting time sees what moments cannot.

**We obtain an exact law for the refined instrument.** Ordinary Λ is blind to eigenvectors, so
isospectral impostors need a *marked* depth: perturb by a rank-one mark and differentiate. Its
derivative turns out not to be the global quantity one expects from the determinant lemma, but a
**rank-two contrast supported on the pair of eigenvalues that is about to collide** — plus one
background term which, once identified, removes the last fitted constant from the theory. The
resulting formula is parameter-free and matches measurement to eleven digits (§3).

We also relate Λ quantitatively to the Lagarias–Rodgers extremum μ, the existing formulation of
the same question, and extract from that relation a single explicit number below which the
alternative hypothesis is false.

**What we do not claim.** We have not proved the Riemann hypothesis, refuted the alternative
hypothesis, or proved the pair correlation conjecture. §§1–3 are theorems and computations about
random matrices, plus a precise, falsifiable, currently unverified prediction about zeta. Where a statement is
numerical rather than proved, it is labelled. A separate part of the paper reports three new
unconditional records for prime clustering, which are proved and machine-certified.

---
## 1. The alternative hypothesis, and an instrument that sees past it

### 1.1 Why the alternative hypothesis is hard to kill

Montgomery's pair correlation conjecture says the normalised gaps between zeta zeros follow the GUE
law. The **alternative hypothesis** is the scenario in which those gaps all lie asymptotically in
(1/2)ℤ. It is consistent with everything provable about zeros, it has real arithmetic consequences,
and it is precisely what current technique cannot exclude.

Tao's article *The alternative hypothesis for unitary matrices* moves the obstruction into random
matrix theory, where it can be computed with. The **ACUE** is the measure on N-point configurations
C inside the 2N-th roots of unity given by μ_ACUE(C) = |Δ(ζ^C)|²/(2N)^N. It reproduces the CUE
two-point correlation exactly. The natural programme — find the first moment at which they differ —
keeps colliding with the same difficulty: the set of measures matching a moment list is a large
convex body, so ruling out ACUE never rules out its neighbours. One must rule out a *fibre*, not a
point.

**How large the fibre is.** We computed it exactly. The affine dimension of the set of measures on
the ACUE support matching every balanced moment of degree ≤ N is

| N | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|
| fibre dimension | 0 | 0 | 2 | 10 | 80 | 403 | 1804 |

with an explicit closed-form subfamily for every N: q_g(C) = μ_ACUE(C)·g(X(C)), X = Σc mod N,
matching every balanced moment of degree ≤ N **iff** E[g] = 1 and ĝ(±1) = 0 — an (N−3)-parameter
family, verified at N = 5, 6, 7, 8 with worst moment error 10⁻¹² and genuinely positive. A second
family comes from the determinant character: μ_ACUE is the Born distribution |⟨C|(∧^N F)A₀⟩|² of a
single Slater determinant, and the tilts by det(U)^r are the interference patterns of two shifted
Fermi seas — points of the first secant variety σ₂(Gr(N,2N)) rather than the Grassmannian itself.
At N = 8, of the 403 fibre directions, 401 are invisible to every pattern count of window width
≤ 2 and 383 to width ≤ 6.

**And the natural flow does not help.** Writing P(z) = det(I − zU) = Σ a_j z^j, the finite analogue
of the de Bruijn–Newman heat deformation is P_r(z) = Σ a_j r^{j(N−j)} z^j, t = log r — *diagonal in
the coefficients*. Every balanced moment of degree ≤ N therefore stays frozen along the **entire**
trajectory (verified to 4.5·10⁻¹⁶). Evolving the moments you have is as futile as adding one more.

### 1.2 The depth

Define the **finite de Bruijn–Newman depth**: −Λ(U) is the first time, running the heat flow
backwards, at which two zeros collide. It is well defined because the flowed polynomial stays
self-inversive, so a simple zero cannot leave the unit circle without first colliding. Equivalently
the zeros obey the attracting circular Coulomb dynamics θ̇_j = −Σ_{k≠j} cot((θ_j − θ_k)/2).

The right way to see it is geometric. Let R_N be the polynomials with all roots on the circle and
D_N = {Disc = 0} its boundary. Then

> **−Λ(P) is the distance from P to the discriminant hypersurface along the canonical heat ray.**

Static moments are coordinates *along* the mimicker fibre; the depth is a coordinate *transverse*
to it. It is not a polynomial statistic of any degree — it is a first-passage time — which is
exactly why the fibre's freedom does not protect it. This is the finite shadow of the picture in
which Λ_dBN ≤ 0 is the Riemann hypothesis and Rodgers–Tao's Λ_dBN ≥ 0 makes RH, if true, *barely*
true.

### 1.3 The separation

**ACUE, exactly.** Complete enumeration of all rotation orbits for N = 3, …, 10 — 13,132 orbits,
184,756 configurations at N = 10 — with exact Vandermonde masses, validated to 40 digits.
P(clock) = 2^{1−N} **exactly** (Cauchy–Binet: Σ_{|C|=N}|Δ|² = (2N)^N, each clock contributing N^N);
clock polynomials 1 − cz^N are flow-invariant, so Λ = −∞ there. Every non-clock configuration has
minimal gap *exactly* π/N (pigeonhole). The law is −Λ^ACUE ≍ N^{−2}, fitted exponent **−2.0009**,
with N²(−Λ) supported in ≈[1.31, 1.99]. In all 13,130 non-clock orbits the first collision occurs
at a pair already adjacent at t = 0 — zero exceptions.

**CUE, Monte Carlo to N = 256.** −Λ^CUE ≍ N^{−8/3}, fitted exponent −2.678 ± 0.016, and the law is
parameter-free: 8N^{8/3}(−Λ) ⟹ G² where P(G > x) = exp(−x³/72π) is the sine-kernel smallest-gap
law. The constant 72π was derived from the kernel, not fitted (measured 229–236 against 226.2,
KS 0.035–0.041, median 29.6–30.5 against (72π ln 2)^{2/3} = 29.08).

### 1.4 What the exponents mean

For an isolated close pair at gap δ the two-body reduction gives collision time δ²/8 + o(δ²) —
confirmed to 10⁻⁷, and exact at N = 2 where −Λ = −log cos(δ/2). So the depth is governed by the
smallest gap, and the smallest gap by the level repulsion exponent:

  p(s) ∼ c s^β ⟹ smallest of ≈N gaps ≍ N^{−1−1/(β+1)} ⟹ **−Λ ≍ N^{−2−2/(β+1)}**.

| ensemble | β | predicted | measured |
|---|---|---|---|
| COE | 1 | −3 | −3.064 (local slopes −3.03 … −3.10) |
| CUE | 2 | −8/3 = −2.667 | −2.678 ± 0.016 (N ≤ 256) |
| CSE | 4 | −12/5 = −2.4 | −2.510 (N ≤ 64, still drifting) |
| ACUE lattice | ∞ | −2 | −2.0009 (exact enumeration) |

All measured slopes are slightly steeper than predicted, in the direction and of the size of the
finite-N drift independently calibrated at β = 2, where the larger range shows the local slope
converging to the prediction. The circular β-ensembles were sampled by the Killip–Nenciu CMV
construction, validated against Haar CUE (KS 0.005) and direct COE = VVᵀ (KS 0.004); the
localisation assumption holds in 95–99% of samples and in 100% of ACUE configurations.

So the depth is a scalar fingerprint of the microscopic repulsion exponent. And the interpretation
inverts the naive expectation. One would guess a fake universe is caught by being *fragile*
somewhere. The opposite: **ACUE's defect is that it is too stable.** CUE admits rare pairs at
distance N^{−4/3}, a full factor N^{−1/3} below the mean spacing, so it is always within N^{−8/3}
of losing real-rootedness; the lattice quantises every gap at π/N and forbids the accidents. A true
random-matrix world is real-rooted but *microscopically fragile*; the alternative hypothesis
satisfies its own Riemann-hypothesis-analogue far too robustly. That is Newman's dictum — "RH, if
true, is only just true" — as a statement about a scaling exponent.

### 1.5 The depth is the Lagarias–Rodgers hard core in another coordinate

This is the sharpest consequence, and it says the depth is not a competitor to the existing
formulation of the alternative hypothesis but that formulation in computable coordinates.

Lagarias and Rodgers study processes mimicking the sine process at coordinatewise bandwidth one and
define μ = sup{c : some mimicker has minimum spacing ≥ c}, mean spacing 1. They prove μ ≥ 1/2 by
the randomly shifted half-lattice — which is exactly ACUE — record the pair-only bound
μ ≤ 0.606894…, and conjecture μ = 1/2. The alternative hypothesis is precisely the assertion that
zeta's zeros realise a hard core of 1/2.

On the circle a hard core of c mean-spacings is δ_min = 2πc/N, so with −Λ = ρ·δ_min²/8,

  **N²(−Λ) = ρ·π²c²/2, and at the alternative-hypothesis value c = 1/2, N²(−Λ) = ρ·π²/8.**

Every number in §3.3 is this identity read one way or the other. The ACUE quantiles give

| N | min N²(−Λ) | ρ_min | median | ρ_med | max | ρ_max |
|---|---|---|---|---|---|---|
| 6 | 1.353146 | 1.0968 | 1.419374 | 1.15050 | 1.952629 | 1.5827 |
| 8 | 1.330383 | 1.0784 | 1.418216 | 1.14956 | 1.976122 | 1.6018 |
| 10 | 1.314614 | 1.0656 | 1.412774 | 1.14515 | 1.985458 | 1.6094 |

**An exactly computed configuration constant.** Take the alternating clock (the zeros of z^N + 1),
delete e^{−iπ/N} and insert 1, so the gap pattern becomes 1, 2, …, 2, 3 in half-lattice units and

  P_N(z) = (z − 1)(z^N + 1)/(z − e^{−iπ/N}).

Two independent routes agree. The lattice solver on this configuration gives N²(−Λ) rising
monotonically to **1.41963827** at N = 20; the continuum limit t = −s/N², z = e^{iu/N} yields

  G_s(u) = 2cos(u/2) − 2π∫₀^{1/2} e^{s(1/4−y²)} cos((π+u)y) dy,

whose first double zero (G = ∂_u G = 0) sits at **s\* = 1.419640342…, u\* = 1.812942145…** with
G″(u\*) = −0.3767 ≠ 0. The two agree to 2·10⁻⁶ at N = 20, consistent with an O(N⁻²) approach. And
s\* = ρ_∞·π²/8 with ρ_∞ = 1.150717118… — the constant is the hard core, dressed by the background.
*(One correction to the record: s\* is not the limit of the ensemble median. For N ≤ 7 the two
coincide, but the complete enumeration shows the median turns around at N = 7 and falls —
1.41822, 1.41520, 1.41277 at N = 8, 9, 10 — as the support spreads from [1.4147, 1.8246] to
[1.3146, 1.9855]. s\* belongs to the support of the limit law, via the single-dislocation stratum.)*

**Equivalence of the two extremal problems.** With μ_Λ = sup{liminf N²(−Λ)} over mimickers,

  **μ_Λ ≥ π²μ²/2 and μ ≤ √(2μ_Λ)/π.**

These are tight, not loose: LR's published μ ≤ 0.606894… is *exactly* the depth bound
μ_Λ ≤ 1.8177…. So **any improvement of the depth bound improves the Lagarias–Rodgers bound**, at an
explicit exchange rate; a depth bound of 1.29 — barely below what ACUE configurations themselves
realise — would already give μ ≤ 0.511.

**A falsifiable number for the alternative hypothesis.** Running the inequality the cheap way:

> **If the zeros of ζ have, in a window at height T containing N = (log T)/2π zeros, local Newman
> depth with liminf N²(−Λ) < π²/8 = 1.2337…, the alternative hypothesis is false.**

This uses only the hard-core consequence of AH. Compare: AH predicts ≥ 1.2337 with actual typical
value 1.41964; CUE predicts N²(−Λ) ≍ N^{−2/3} → 0. The margin to the threshold is a factor 1.15;
the margin from CUE is unbounded. And crucially, refuting AH does **not** require the full N^{−8/3}
law — only that the depth eventually drops below one explicit constant.

**Why this reformulation may be more tractable.** The LR extremum constrains a *minimum*, a hard
combinatorial quantity, whereas Palm-type certificates — the row-sum square
Var⁰_sine(S_f) ≤ (M_h − A_f)(A_f − m_h) for band-limited f, and its multiwindow quadratic
generalisation on the packing body K_h — apply naturally to smooth functionals. The depth is smooth
in the configuration (we compute its gradient below), has a variational characterisation as a
distance to a hypersurface, and has an explicit derivative law. Transporting those certificates from
the row sum to the depth is the natural next attempt, and unlike the row-sum searches — which failed
for an exact local reason, the pattern {−h, 0, h} already forcing S₀ = 2f(h) > 9/7 for the first
nonnegative Fejér profile — the depth has no such immediate obstruction.

**Two lemmas, not one.** It is worth separating them, because they have different status and do
different jobs.

> **Hard-core lemma (ρ ≥ 1).** Proved in §1.7 directly from the adjacent-gap ODE. It gives the
> inequality in the direction used here, hence the falsification threshold: **N²(−Λ) < π²/8 ⟹ the
> alternative hypothesis is false.**
>
> **Localisation lemma (ρ → 1 for finite β).** The remaining probabilistic estimate. It is what
> upgrades the exponents to distributional limits.

Only the second is open, and §1.7 predicts its rate.

**The leverage on μ, made explicit.** Since μ_Λ ≥ π²μ²/2, any upper bound D_dyn ≤ M for the depth
of an admissible class gives

  **μ ≤ √(2M)/π.**

M = 1.29 — barely below what ACUE configurations themselves realise — already gives
μ ≤ 0.511281…, a large improvement on the published 0.606894…. Crossing the alternative-hypothesis
barrier itself requires M < π²/8 = 1.2337005501…. So the depth is not merely an equivalent
coordinate for the Lagarias–Rodgers problem; it is a coordinate in which a *quantitative* target is
visible, and the target is a single number.

### 1.6 A classification of impostors, with two computable criteria

**Criterion I (transversality).** For a configuration X and bandwidth r, with M_r = (p₁,…,p_r) and
τ = −Λ, ordinary Λ catches the class exactly when ker DM_r ⊄ ker Dτ. The relative residual of
grad τ off the row space of DM_r:

| configuration | r = 1 | r = 2 | r = 3 | r ≥ N/2 |
|---|---|---|---|---|
| single dislocation, N = 8 | 0.991 | 0.941 | 0.737 | rank saturates |
| random ACUE lattice, N = 7 | 0.996 | 0.963 | 0.569 | rank saturates |
| generic non-lattice, N = 7 | 0.998 | 0.926 | 0.195 | rank saturates |

While rank DM_r < N the kernel is nontrivial and the answer is decisively yes: 80–99% of the depth
gradient lies in directions the first one or two moments cannot see. At r ≈ N/2 the rank saturates
at N, ker DM_r = 0, and the residual drops to 10⁻¹⁶ — not because Λ fails but because the question
becomes vacuous.

**Class I, caught by Λ directly.** Anything whose defect changes the geometry of the closest pair:
collision-stratum families (δ = 0 gives Λ = 0 outright, the mechanism by which function-field
Newman constants are pinned by double roots), half-lattice adversaries with a hard lower spacing,
and the centre-of-mass and secant families, which move the depth law by total variation 0.12–0.24
with every balanced moment frozen. Linear-programming tomography over the exact fibre at N = 6
gives E[N²(−Λ) | non-clock] ranging over **[1.3610, 1.4770]** against ACUE's 1.4336, while the mass
at Λ = −∞ can be pushed from 0 to **0.0975**, tripling ACUE's 0.03125, with every constrained
moment held fixed.

**Class II, invisible to Λ, caught by a marked depth.** Λ is a function of the characteristic
polynomial alone, so isospectral matrices have *identically* the same depth — verified to machine
zero (τ(G₁) = τ(G₂) = 0.068725421516, difference 8·10⁻¹⁷). The repair deforms G ↦ G + η uu\*,
transports to the circle by Cayley, and differentiates: χ(G;u) = ∂_η(−Λ)|₀. It separates the
isospectral pair immediately, median |χ(G₁;u) − χ(G₂;u)| = 0.081 against |χ| of order 0.01–0.2.

What χ actually measures is **not** the directional resolvent the determinant lemma suggests, but a
rank-two contrast on the colliding pair, and the exact law — parameter-free, verified to eleven
digits — is the subject of §3.

**Class III, immune to the linear flow.** If the observable algebra misses a direction v, the heat
operator — being diagonal — keeps H_t v in the same hidden sector, so static invisibility persists
for all t. **A linear flow does not destroy linear invisibility.** Λ escapes that argument only
because it is not a linear observable transported by the flow but the first hitting time of the
orbit against a variety: two orbits can share an invariant hidden sector and stand at different
distances from D.

**A test case at the boundary.** The strongest known static escape is the pair of parity sectors
q_N^±(C) = μ_N(C)(1 ± (−1)^{Σx}), which are mutually singular, agree on every complete marginal on
at most N − 1 sites, and match balanced trace moments of degree far beyond N. The depth *does*
separate them at every finite N, but entirely through the atom: for even N both clocks have even
slot-sum, so P(Λ = −∞) = 2^{2−N} in q⁺ and **exactly 0** in q⁻. The non-clock bulk is nearly
identical — at N = 8 the quantiles are 1.3739/1.3959/1.4182/1.4554/1.4839 against
1.3752/1.3959/1.4196/1.4338/1.4788 — and the conditional means differ by 8.9·10⁻³, 3.4·10⁻³,
1.1·10⁻³ at N = 6, 8, 10, shrinking. Since the separating mass 2^{2−N} vanishes, the parity sectors
are a Class II/III object: caught at finite N, invisible in the limit, and a natural first target
for the marked depth.

### 1.7 What is now proved: a two-body comparison theorem

The three scaling laws above were, until this point, numerical. They are not independent: all three
follow from a local collision law plus a smallest-gap law, and the smallest-gap laws are known. What
was missing was control of the *background* — the effect of the other N − 2 zeros on the collision
time of the closest pair. That is now a theorem, and it is elementary.

Parameterise the flow by the depth u = −t, so the zeros obey θ_j′ = −Σ_{k≠j} cot((θ_j − θ_k)/2) and
collisions occur as u increases. Two facts:

**Exact two-body solution.** For N = 2, separating variables in δ′ = −2cot(δ/2) gives
cos(δ(u)/2) = e^u cos(δ(0)/2), hence collision exactly at u = −log cos(δ(0)/2) = δ(0)²/8·(1 + δ(0)²/24 + …).

> **Theorem A (two-body comparison).** Let (a,b) be an *adjacent* pair, i.e. no zero lies strictly
> inside the short arc from θ_b to θ_a, and let g be its gap. Then under the depth flow
>   **g′ ≥ −2cot(g/2).**
> Consequently no collision occurs before u = −log cos(δ_min/2), so
>   **−Λ ≥ −log cos(δ_min/2) ≥ δ_min²/8,  i.e. ρ ≥ 1 always.**

*Proof.* Write x_j^k = (θ_j − θ_k) mod 2π ∈ (0, 2π). Then

  g′ = θ_a′ − θ_b′ = −2cot(g/2) − Σ_{k≠a,b} [ cot(x_a^k/2) − cot(x_b^k/2) ].

Adjacency says that for every other zero k one has x_a^k = x_b^k + g with both in (0, 2π): going
counterclockwise from k one meets b before a, and k is not inside the arc. Since cot(x/2) is
strictly decreasing on (0, 2π), each bracket is negative, so each term enters g′ with a positive
sign — **every other zero slows the collapse.** Hence g′ ≥ −2cot(g/2). The ordering of the zeros
is preserved until the first collision, so each gap dominates the two-body solution started from
its own initial value, and the earliest possible vanishing is at u = −log cos(δ_min/2). ∎

The sign claim was checked on 11,060 background terms across random and lattice configurations with
zero exceptions, and the resulting inequality holds on every dataset in this paper: the minimum of
(−Λ)/(−log cos(δ_min/2)) is 1.0842, 1.0714, 1.0612 over the complete ACUE enumerations at
N = 6, 8, 10, and 1.00019, 1.00021 over the CUE samples at N = 16, 64. (At N = 256 the measured
minimum is 1 − 1.3·10⁻⁵, an absolute discrepancy of 2·10⁻¹¹, at the solver's tolerance.)

**Corollaries, all now rigorous.**
- **−Λ^ACUE ≥ π²/(8N²) exactly**, since δ_min = π/N for every non-clock configuration (§1.3).
- **Any point process with hard core c has N²(−Λ) ≥ π²c²/2.** The exchange inequality
  μ_Λ ≥ π²μ²/2 of §1.5 — hence the Lagarias–Rodgers direction we actually use, and the
  falsification threshold π²/8 = 1.2337 — is a theorem, not numerics. What remains conjectural
  there is only the *reverse* comparison.

**Theorem B (matching upper bound where the background is subcritical).** The background term is
bounded by the mean value theorem: |Σ_{k≠a,b}[…]| ≤ g·Σ_{k} ½csc²(x_b^k/2), and for a configuration
all of whose gaps exceed c/N this is ≤ C·N²g, using Σ_{k=1}^{N−1} ½csc²(πk/N) = (N²−1)/6.
Integrating δ′ ≤ −2cot(δ/2) + CN²δ gives

  **−Λ ≤ (δ_min²/8)·(1 + O(N²δ_min²)),** hence −Λ = (δ_min²/8)(1 + o(1)) whenever N²δ_min² → 0.

**What this reduces the three laws to.**

*Law 1 (CUE).* δ_min ≍ N^{−4/3} gives N²δ_min² ≍ N^{−2/3} → 0, so Theorems A and B pin
−Λ = δ_min²/8·(1 + O(N^{−2/3})). The predicted relative correction exponent −2/3 = −0.667 matches
the independently measured 0.598·N^{−0.729}. Composing with the sine-kernel smallest-gap law
P(N^{4/3}δ_min > x) → exp(−x³/72π) — Ben Arous–Bourgade, and Feng–Wei for CβE — yields
**8N^{8/3}(−Λ) ⟹ G²**. So Law 1 is reduced to a cited theorem plus Theorems A and B; what is still
needed for a complete proof is that the error in Theorem B is uniform in probability, i.e. that the
minimal gap is with high probability isolated and unaccompanied by a second anomalously small gap —
which is precisely what the extreme-gap literature supplies.

*Law 3 (β-universality).* Identical, for every finite β: δ_min ≍ N^{−1−1/(β+1)} gives
N²δ_min² ≍ N^{−2/(β+1)} → 0, so **−Λ ≍ N^{−2−2/(β+1)}** reduces to the CβE extreme-gap law. The
exponent is not an empirical fit; it is the image of the repulsion exponent under two elementary
steps.

*Law 2 (ACUE).* Here δ_min = π/N exactly, so N²δ_min² = π² — **the background correction does not
vanish**, which is precisely why ρ^ACUE ∈ [1.05, 1.61] rather than → 1. The lower bound
−Λ ≥ π²/(8N²) is exact and proved; the matching upper bound needs ρ ≤ C, which our complete
enumeration establishes for N ≤ 10 and to which the slowly decreasing minimising family of §1.5
gives strong evidence, but which is not proved in general. This is the one remaining gap, and it is
a lattice-specific constant problem rather than a universality problem.

**The finite-β / β = ∞ dichotomy, and why it is singular.** The background correction is governed by
δ_min²·S with S ≍ N² the background stiffness (the clock value is exactly (N²−1)/6). Feng–Wei give
δ_min ≍ N^{−1−1/(β+1)} for the circular β-ensembles, so

  δ_min²·S ≍ N^{−2−2/(β+1)}·N² = **N^{−2/(β+1)} → 0 for every finite β**,

whence ρ_β → 1 and the two-body constant 1/8 is asymptotically exact. But at β = ∞ the hard core
pins δ_min ≍ 1/N, so δ_min²·S ≍ 1: the background contributes at leading order and **ρ_∞ ≠ 1**.
The lattice endpoint is therefore *not* the smooth limit of the finite-β formula — it is a singular
hard-core endpoint, and that is exactly why the single-dislocation configuration realises

  **s\* = 1.419640342… = 1.150717118… × π²/8**,

a two-body collision time dressed by roughly 15% of many-body shielding, rather than π²/8 itself.

This also predicts the *rate* at which ρ_β approaches 1, which is a sharper and independently
testable statement than the leading exponent:

  **ρ_β − 1 = O_ℙ(N^{−2/(β+1)+o(1)}).**

| β | predicted rate | fitted over N ≤ 128–256 | local slope at the largest N |
|---|---|---|---|
| 1 (COE) | −1 | **−1.012** | −0.851 |
| 2 (CUE) | −2/3 = −0.667 | −0.710 | **−0.624** |
| 4 (CSE) | −2/5 = −0.400 | −0.501 | **−0.407** |

β = 1 lands on the prediction; for β = 2 and 4 the global fits are steeper but the local slopes
decrease monotonically toward the predicted value and essentially reach it at the largest sizes,
with the finite-N drift growing with β as expected (a slower predicted decay is more heavily
contaminated).

**The pipeline.** The three laws are therefore not three empirical facts but one mechanism:

  extreme-gap law (cited) + first-collision identity (§1.7) + background localisation (open)
    ⟹ −Λ = ρ·δ_min²/8 with ρ ≥ 1 proved, ρ → 1 for finite β, ρ = O(1) but ≠ 1 at β = ∞
    ⟹ **−Λ ≍ N^{−2−2/(β+1)}** across the whole family, lattice included.

So the honest status of the three laws changes from "numerical" to: **Law 1 and Law 3 reduced to
published extreme-gap theorems plus the localisation lemma; Law 2 proved in the direction that
matters for the alternative hypothesis, with its non-unit constant explained rather than fitted.**


### 1.8 The separation, proved on one side and reduced on the other

The two laws can now be separated by a *deterministic threshold* rather than by comparing fitted
exponents.

> **Theorem C (CUE/ACUE separation).**
> **(i)** For every N and every non-clock ACUE configuration, **N²(−Λ) ≥ π²/8 = 1.2337…**
> **(ii)** P( N²(−Λ^CUE) < π²/8 ) → 1.
> Hence the two depth laws are eventually separated by the fixed constant π²/8, almost surely on
> the ACUE side.

Part (i) is unconditional and needs nothing new: δ_min = π/N exactly for every non-clock ACUE
configuration (§1.3, pigeonhole), and Theorem A gives −Λ ≥ δ_min²/8. There is no probability in it
— the bound holds configuration by configuration.

Part (ii) rests on two events, and it is worth separating what is cited from what we verified.

*The gap event.* The sine-kernel law P(N^{4/3}δ_min > x) → exp(−x³/72π) gives
P(δ_min > π/N) = P(N^{4/3}δ_min > πN^{1/3}) → exp(−π²N/72): the CUE minimum gap exceeds the lattice
gap with **superpolynomially small** probability. This is the cited input.

*The regularity event.* Theorem B needs the background slowdown coefficient
B := Σ_{k≠a,b}[cot(x_b^k/2) − cot(x_a^k/2)]/g to satisfy B ≤ AN². The clock value is exactly
(N²−1)/6, so A ≈ 1/6 = 0.1667 is the natural scale. Measured on fresh Haar samples:

| N | 8 | 16 | 32 | 64 | 128 |
|---|---|---|---|---|---|
| median B/N² | 0.1092 | 0.1202 | 0.1171 | 0.1202 | 0.1200 |
| 99th percentile | 0.2192 | 0.2551 | 0.3572 | 0.2829 | 0.3273 |
| maximum observed | 0.2974 | 0.3106 | 0.6075 | 0.7948 | 0.3595 |

so B ≤ N² comfortably, with a stable median of 0.120 and no observed excursion past 0.80. On that
event Theorem B gives N²(−Λ) ≤ (N²δ_min²/8)(1 + O(N²δ_min²)), and the same samples give
median N²δ_min² = 7.41, 4.66, 2.92, 1.85, 1.18 at N = 8, …, 128 — a ratio of 6.28 across a factor
16 in N, against the predicted N^{−2/3} scaling factor 16^{2/3} = 6.35, agreement to 1%.

**The conclusion, measured directly.** The fraction of CUE samples with N²(−Λ) below the ACUE floor
π²/8, and the largest value observed:

| N | 8 | 16 | 32 | 64 | 128 | 256 |
|---|---|---|---|---|---|---|
| fraction below π²/8 | 0.565 | 0.823 | 0.967 | 0.9984 | **1.0000** | **1.0000** |
| max N²(−Λ) observed | 7.93 | 4.92 | 2.48 | 1.34 | **0.911** | **0.437** |
| median N²(−Λ) | 1.083 | 0.627 | 0.385 | 0.231 | 0.146 | 0.0946 |

From N = 128 onward **every** sampled CUE configuration lies below the deterministic ACUE floor,
and by N = 256 the median sits a factor 13 below it. The separation is not asymptotic bookkeeping:
it is visible as a strict inequality between two computable quantities at accessible sizes.

**What is proved and what is not.** (i) is a theorem. In (ii), the gap event is a cited theorem and
the regularity event is verified numerically rather than proved; converting the table above into a
proof requires a high-probability bound on B, which is a standard rigidity statement for CUE
(control of Σ_k d_k^{−2} for the neighbourhood of the extremal pair) but one we have not carried
out. That is the precise remaining gap, and it is narrower than the one we started with: the
separation no longer depends on the exponent −8/3 at all, only on the CUE minimum gap being
eventually smaller than π/N together with a bounded background.


---

## 2. One operator: why a hitting time sees what moments cannot

This section is the structural core. Everything above says *that* the depth escapes the moment
algebra; this says *why*, and the answer identifies two objects that had no known relation.

### 2.1 The static side: how deep an impostor can hide

Restrict to the gauge-invariant even shifts and let |Ω_s⟩ be the Slater state obtained from the
Fermi sea by the shift 2s, s ∈ ℤ/Nℤ. Then ⟨C|Ω_s⟩ = z(C)^s⟨C|Ω_0⟩ where z(C) = D₂(C) satisfies
z^N = 1, so the entire secant family collapses to a single polynomial on ℤ_N: for normalised
coefficients a, the state Ψ_a = Σ a_s|Ω_s⟩ induces

  q_a(C) = μ_ACUE(C)·|Σ_s a_s z(C)^s|² = μ_ACUE(C)·(1 + Σ_{δ≠0} A_δ z(C)^δ),

with A_δ = Σ_s a_{s+δ} ā_s the periodic autocorrelation. **The code object is not the support of a
but its autocorrelation spectrum**, and the invisibility depth is

  d_vis(a) = min{ δ(N−δ) : δ ≠ 0, A_δ ≠ 0 }.

This is exact, not an analogy: the sector pairing E_μ[D_{2δ} f ḡ] vanishes for degrees below
δ(N−δ) and first opens a rank-one channel at that degree, so q_a agrees with ACUE on all balanced
observables of degree ≤ d **iff** A_δ = 0 for every δ with δ(N−δ) ≤ d. Since d_N(δ) = δ(N−δ)
depends only on the cyclic Lee distance and is increasing, the pure max–min code problem is settled
by pigeonhole: for L states the best possible minimum distance is m(N−m) with m = ⌊N/L⌋, maximised
at L = 2 with value **⌊N²/4⌋**. Two Fermi seas are globally optimal; there is nothing to gain from
five, and no compute should be spent looking.

The quantity d_N(δ) = δ(N−δ) is simultaneously the complex dimension of the Grassmannian Gr(δ,N),
the pairing ⟨2ρ, ω_δ⟩ — hence the affine Bruhat length ℓ(t_{ω_δ}) of the dominant translation — and,
up to the standard normalisation, the quadratic Casimir of the fundamental coweight. Those three
identifications are representation theory. The fourth is new.

### 2.2 The dynamic side: the clock's stability operator

Its finite Fourier transform is elementary and exact: for k ≠ 0,

  Σ_{δ=0}^{N−1} δ(N−δ) e^{−2πikδ/N} = **−N / (2 sin²(πk/N))**,

so d_N is the symbol of the long-range operator

  (𝓛_N f)(x) = Σ_{k=1}^{N−1} [ f(x) − f(x+k) ] / (2 sin²(πk/N)),  𝓛_N e_δ = δ(N−δ)·e_δ.

Now recall the dynamics. Backwards heat flow moves the zeros by the attracting Coulomb law
θ̇_j = −Σ_{k≠j} cot((θ_j − θ_k)/2), whose fixed point is the clock. Linearise about it,
θ_j = 2πj/N + ε_j, using d/du[−cot(u/2)] = ½csc²(u/2):

  **ε̇_j = Σ_{k≠j} (ε_j − ε_k) / (2 sin²(π(j−k)/N)) = (𝓛_N ε)_j.**

> **The operator controlling how deeply a static impostor can hide is the Jacobian of the zero
> dynamics at the clock.**

Verified to machine precision at N = 4, 6, 8, 10, 12, 16, 20, 24: the Fourier identity to 10⁻¹²,
the eigenvalues of 𝓛_N against δ(N−δ) to 10⁻¹³, and ‖𝓛_N − Jacobian‖ ≤ 2.4·10⁻¹³. The spectrum is
0, and δ(N−δ) with multiplicity two for 0 < δ < N/2, and the Nyquist mode δ = N/2 alone at the top
with eigenvalue **N²/4 = ⌊N²/4⌋ — exactly the maximal invisibility depth obtained above by
pigeonhole**, two entirely different derivations of the same number.

### 2.3 The mechanism, in one sentence

The eigenvalue δ(N−δ) has two readings that now coincide: it is the degree at which a δ-mode
becomes visible to balanced observables, and it is the rate at which that mode relaxes under the
flow. Therefore

> **an impostor invisible to degree ≤ d observables is one whose deviation is supported on the
> modes that relax fastest — and those are exactly the modes the flow acts on most strongly.**

Hiding statically and being acted on dynamically are the same condition, read from opposite ends.
That is why adding moments is futile while a hitting time is not: the moment algebra is blind
precisely where the flow is loudest, and Λ is a functional of the flow. It also explains why the
Nyquist channel keeps appearing on both sides of this project — as the top of the invisibility
hierarchy and as the fastest-relaxing mode — and why ACUE, whose deviation from the clock lives at
the *bottom* of this spectrum, sits so far from the discriminant.

### 2.4 What this opens

Three directions follow immediately, and each is computational rather than philosophical.

**A quantum code.** For S ⊂ ℤ_N the span 𝒞_S = span{Ω_s : s ∈ S} satisfies the Knill–Laflamme
condition against the algebra of balanced observables of degree < min_{s≠t} d_N(s−t): diagonal
matrix elements are equal because D_{2s} is a phase, and off-diagonal ones are the sector pairings
above. The ACUE cyclic shifts form an exact error-detecting code whose distance is the affine
Bruhat length.

**An interference problem that is genuinely open.** Since Â(k) = |â(k)|² ≥ 0, the design space is
{A : A₀ = 1, A positive-definite on ℤ_N, A_δ = 0 on a low-Bruhat-energy region, A_{δ*} ≠ 0 as high
as possible} — a Delsarte-type linear program, and the natural name is a *zero-Bruhat-correlation-zone
sequence*. Note the degenerate case: A_δ = 0 for all δ ≠ 0 gives q_a = μ_ACUE, no impostor at all.

**A different semigroup.** As N → ∞ at fixed δ, d_N(δ)/N → |δ|, so N^{−1}𝓛_N → (−Δ)^{1/2}, the
half-Laplacian on the circle. The natural semigroup attached to the invisibility hierarchy is
therefore the **Poisson** flow e^{−t|k|}, not the ordinary heat flow e^{−tk²}. The 1/sin² kernel is
also the defining interaction of the Haldane–Shastry chain, so the question of whether this
hierarchy is a sector of an integrable spectrum is a concrete one, worth asking because an
affirmative answer would replace brute-force moment computation by Bethe-type identities. We flag
this as a lead, not a claim: sharing a kernel is not sharing a Hamiltonian.

A larger deformation class is available and largely unexplored. Any phase twist
u ∈ U(1)^{2N} acting on the Fermi sea leaves the Born distribution |⟨C|Ω_u⟩| unchanged, and the
Cauchy–Binet identity gives E_μ[(∏_{c∈C} u_c) s_λ(x_C) \overline{s_ν(x_C)}] = det((T_u)_{A_ν,A_λ})
with T_u = F\*D_u F circulant. So every phase-twisted moment is a circulant Toeplitz minor, hence
automatically satisfies the Plücker relations and sits inside the KP/Toda τ-function formalism. The
sharp question — whether vanishing of all such minors below degree ⌊N²/4⌋ forces u to be a linear
phase up to gauge — would say that the determinant-character impostor is the canonical extremiser
of its whole deformation class, which is a strictly stronger statement than exhibiting one
counterexample.


---

---

## 3. The marked depth: an exact rank-two law

Λ is a function of the characteristic polynomial alone, so isospectral matrices share it exactly —
we verify τ(G₁) = τ(G₂) = 0.068725421516 to 8·10⁻¹⁷. Impostors built to match rank, trace and
Hilbert–Schmidt norm while differing in directional data therefore need a refinement. Deform by a
rank-one **mark**, transport to the circle by Cayley, and differentiate:

  G_η = G + η uu\*,  U_η = (G_η − iI)(G_η + iI)^{−1},  χ(G;u) = ∂_η(−Λ(U_η))|_{η=0}.

It separates the isospectral pair at once — median |χ(G₁;u) − χ(G₂;u)| = 0.081 against |χ| of order
0.01–0.2. The interesting question is what it measures.

### 3.1 Not the resolvent

The determinant lemma det(zI − G − ηuu\*) = det(zI − G)(1 − η·u\*(zI − G)^{−1}u) suggests that χ
should track the directional resolvent and blow up wherever the inverse-Gram data is worst. **It
does the opposite.** Rotating the mark onto the smallest-|eigenvalue| direction drives
u\*(z₀I − G)^{−1}u from 1.615 to 6.667 = 1/|λ_min| while χ *falls* from 0.0267 to 0.0028 — an order
of magnitude the wrong way. Condition-number susceptibility and collision susceptibility are
different questions: the resolvent asks how much mass the mark puts on a spectral singularity, the
depth asks how much *differential angular velocity* the mark induces on the pair that collides
first. A near-null eigenvector orthogonal to that pair scores high on the first and nothing on the
second.

### 3.2 The law

Let (a,b) be the first colliding pair with gap δ, and write

  q_j(u) = |⟨u, v_j⟩|²,  c_j = −2/(1 + λ_j²),  **K_{ab} = c_a v_a v_a\* − c_b v_b v_b\***.

Hellmann–Feynman gives dλ_j/dη = q_j, the Cayley map contributes dθ_j/dλ_j = c_j, so the first-order
response of the critical gap is exactly the rank-≤2 quadratic form

  δ′(u) = c_a q_a(u) − c_b q_b(u) = u\* K_{ab} u.

The remaining ingredient is that the local collision law −Λ = κ·δ²/8 has κ = 8τ/δ² a *functional of
the configuration*, not a constant. Differentiating τ = κδ²/8 therefore gives two terms, and this
is the whole content of the earlier fitted factor:

> **Marked depth derivative law.**
>   **Dτ_G[uu\*] = (κ(G)·δ(G)/4)·u\*K_{ab}u + (δ(G)²/8)·κ′(u).**

Measured at N = 6 with κ(G) = 1.280050 taken directly from the configuration (not fitted): the
correlation with measurement is **1.00000000**, the slope **1.00000**, and the residual **5.7·10⁻¹¹**
— finite-difference accuracy. The local term alone gives correlation 0.9958, slope 1.347, residual
8.1·10⁻². So the previously reported empirical constant ρ ≈ 1.72 was never a constant: fitting
χ = ρ(δ/4)δ′ forces ρ = κ + (δ/2)(κ′/δ′), which varies from mark to mark and averages to something
larger than κ. **The law is now parameter-free**, and it decomposes cleanly into a local gap
response and a background renormalisation response.

### 3.3 It is a polarisation detector, not an overlap detector

Write T(u) = q_a + q_b for the mark's total mass in the critical two-plane and
I(u) = (q_a − q_b)/(q_a + q_b) for its imbalance. When the two critical eigenvalues are close,
c_a ≈ c_b ≈ c and

  δ′(u) ≈ c·T(u)·I(u).

In the critical two-plane K_{ab} = diag(c_a, −c_b) ≈ c·σ_z. **The marked depth measures P_a − P_b,
not P_a + P_b.** This corrects the natural guess: overlapping the critical pair is *not* sufficient.
The mark u = (v_a + v_b)/√2 lies entirely inside the critical subspace, T = 1, yet has I = 0 and so
gives no first-order response at all; the maximal-response marks are v_a and v_b themselves. The
exact null cone is

  𝒩_{ab} = { u : c_a q_a = c_b q_b } = { u : q_a/(1 + λ_a²) = q_b/(1 + λ_b²) },

which reduces to q_a = q_b only when λ_a ≈ λ_b.

### 3.4 Three confirmations

**Blind tomography.** Sampling 60 random marks and solving χ(u_k) ≈ u_k\*K u_k for a symmetric K,
without telling the solver which pair collides: the recovered K has top-two energy fraction 0.986,
and its leading two-dimensional eigenspace agrees with the true span{v_a, v_b} to principal angles
of **2.3·10⁻⁶ and 3.0·10⁻⁶ degrees**. The residual 1.4% of energy is the κ′ term, which is not
rank-two. So the critical pair can be recovered from depth measurements alone.

**The null cone is reachable, and reveals a floor.** Constructing marks with c_a q_a = c_b q_b to
10⁻¹⁶ while keeping q_a = 0.244, q_b = 0.694 leaves χ = −3.3·10⁻³ to −3.9·10⁻³ — the same order as
the orthogonal control, 2.8·10⁻³. This is a genuine background channel, not a residue of the local
one, and it is worth noting *why*: for u ⊥ v_a, v_b the perturbation leaves λ_a and λ_b **exactly**
fixed, not merely to first order, since (G + ηuu\*)v_a = λ_a v_a. So the floor cannot come from
critical-pair eigenvalue motion at all; it is background renormalisation and trajectory shift, which
is precisely the κ′ term. The experiments therefore separate χ = χ_local + χ_background cleanly.

**The resolvent returns at second order.** It was not meaningless, only mis-ordered. Second-order
rank-one perturbation theory gives λ_j″ = 2q_j Σ_{k≠j} q_k/(λ_j − λ_k), so the denominators
1/(λ_j − λ_k) — the resolvent structure — govern the *next* term. The correct hierarchy is:
first order, critical-pair differential overlap; second order, spectral mixing through the
resolvent; then global heat-flow background renormalisation. On the null cone the first channel is
switched off by construction, which makes it the natural place to test the second.

At finite η the two-plane picture continues: the mark contributes off-diagonal coupling
α_a ᾱ_b inside span{v_a, v_b}, giving a 2×2 effective Hamiltonian whose gap has the usual
square-root form. So the regimes are linear response, then an avoided-crossing (Landau–Zener)
crossover as η approaches the original gap, then exact degeneracy where the off-diagonal term
leads — a finite-dimensional local model, not an N×N resolvent computation.

### 3.5 The pattern this belongs to

Two very different compressions in this paper have the same shape. In the ACUE fibre, an enormous
moment space collapses at the critical degree to a **rank-one** transport channel between conjugate
rectangles. In the marked depth, an enormous spectral geometry collapses at first order to a
**rank-two** contrast on the colliding pair. We record the pattern as a working principle rather
than a theorem:

> **First-defect compression.** When a model is indistinguishable from its target under all
> low-complexity observables, the first observable that does distinguish them tends to act through
> a channel of very low rank.

If that is right, the search for detectors should be reorganised. The natural objects are not
further class functions Tr ρ(U) or Schur polynomials s_λ(U), but **marked matrix coefficients**: the
quantity χ measures a dipole of the mark's spectral measure μ_u = Σ_j q_j(u) δ_{θ_j} across the
critical pair, c_a μ_u(θ_a) − c_b μ_u(θ_b). In the Langlands setting the analogous objects are
periods and relative characters ⟨v, π(g)v⟩ rather than traces Tr π(g) — which is an argument, from
this side, that a relative trace formula is the right home for an arithmetic version of this
detector.

---

## 4. What we can and cannot say about zero density

The other headline target adjacent to this circle of ideas is the zero-density exponent. Guth and
Maynard's large-value estimate gives N(σ,T) ≤ T^{(30/13)(1−σ)+o(1)} and primes in intervals of
length x^{17/30+o(1)}, the first improvement on the supremal exponent in four decades. Their
argument bounds the top singular value of a Dirichlet-polynomial Gram matrix using its trace and a
*centered third* spectral moment, and they note that estimates for fourth and higher powers are
unavailable. It is tempting to conclude that supplying higher traces would improve the exponent.

We tested the pure moment-deflation channel exactly, and the answer is discouraging. Given only
(p₁, p_r) and m nonnegative eigenvalues, the sharp bound on the largest is
λ₁^r + (p₁ − λ₁)^r/(m−1)^{r−1} ≤ p_r. For a spectrum consisting of one spike plus a flat bulk — the
idealised large-value picture — **the r = 3 bound is already exactly tight, and r = 4, 6, 8, 10 buy
precisely nothing** (gain 0.00% at m = 100, 1000, 10000, at spike fractions 0.5, 0.3, 0.15, 0.05).
A gain appears only when the bulk itself carries secondary structure, and even then it is small:
for a secondary cluster of 10 eigenvalues at 3% of the trace, going from r = 3 to r = 10 removes
1.1% of the overestimate; for 30 at 1.5%, 0.4%; for 100 at 0.5%, 0.1%.

The honest reading: whatever room exists in the Guth–Maynard framework is not in the moment
hierarchy alone. It must come from the additive-energy input and the geometry of the large-value
set, where higher traces could interact with the resonator structure rather than merely sharpening
an already-tight scalar inequality. We have seen a proposed formula quantifying such a combined
gain — a saving parameter e = η + κ, a root y_e of 240y² + (72 − 10e)y − 13e = 0, and an improved
exponent A(e) = 30/(13 + 10y_e) < 30/13 — but we have not re-derived the Guth–Maynard argument and
therefore neither endorse nor dispute it. It is recorded here as an unverified claim from a
collaborating system, not as a result of this paper.

---

## 5. Records for clustered primes

### 5.1 The mechanism

Fix a set of offsets H = {h₁, …, h_k} that is *admissible* — for each prime p the offsets miss a
residue class mod p, so nothing forbids all of n + h₁, …, n + h_k being prime at once. Maynard's
method weights each n by a square w(n) = (Σ_d λ_d)² built from divisor sums, and compares the total
weight S₁ = Σ w(n) against the prime-counting weight S₂ = Σ w(n)·#{i : n + h_i prime}. If the
primes are equidistributed to level θ and a variational constant

  M_k = sup_F k·J(F)/I(F),  I(F) = ∫_{R_k} F², J(F) = ∫_{R_{k−1}} (∫₀^{1−Σ} F dt_k)²

over symmetric F on the simplex R_k exceeds 2m/θ, then every admissible k-tuple contains m + 1
primes infinitely often, hence H_m := liminf(p_{n+m} − p_n) ≤ H(k), the diameter of the narrowest
admissible k-tuple. Bombieri–Vinogradov gives θ = 1/2 unconditionally, so the criterion is
M_k > 4m.

### 5.2 What everyone had missed

For m = 1 the relevant k is 50 and M_k has been computed exhaustively. For m ≥ 2 the relevant k
runs from ten thousand to fifty million, and there M_k had never been computed at all: every record
since 2014 used the same crude closed-form bound, M_k ≥ log k − C, obtained by truncating a product
test function hard at the simplex boundary. The improvements of 2023–2025 raised the arithmetic
input θ and left that bound untouched.

Its deficit is 2.3 to 2.9 units of log k, and about 1.1 units are recoverable elementarily. Since
M_k ≈ log k and H(k) ≈ k(log k + 0.77), recovering 1.1 units is a factor e^{1.1} ≈ 3 in k, hence
nearly a factor 3 in H_m.

### 5.3 The engine

Take F(t) = ∏_i g(t_i)·1[Σt_i ≤ k]. Let X_i be i.i.d. with density g²/c₂, c₂ = ∫g², write S_j for
partial sums and G(u) = ∫₀^u g. Then, exactly,

  I(F) = k^{−k} c₂^k · P(S_k ≤ k),  J(F) = k^{−(k+1)} c₂^{k−1} · E[G((k − S_{k−1})₊)²],

and the truncation, discarded classically, becomes a genuine probability. The **layer-cake
identity**

  E[G((k − S)₊)²] = ∫ 2G(u) g(u) · P(S_{k−1} < k − u) du

converts it into an integral of true lower-tail probabilities, each bounded below rigorously
(chord-majorised Chernoff, one-big-jump, Berry–Esseen with the safe non-i.i.d. constant 0.56); the
bounds use only monotonicity of the true tail, so discretisation cannot invalidate them. Replacing
the hard truncation by **shaped subexponential tails** g(t) = e^{−(t/T₁)^κ}/(1 + At) on a long
support recovers the remainder: +0.12 units from exact truncation accounting, +0.49 from tail
shaping, the rest from shape optimisation.

### 5.4 The results

| | new bound | k | previous record |
|---|---|---|---|
| H₂ = liminf(p_{n+2} − p_n) | **173,438** | 15,856 | 396,504 (Stadlmann 2023/25) |
| H₃ | **13,859,802** | 923,601 | 24,797,814 (Polymath8b 2014) |
| H₄ | **1,120,662,828** | 56,000,000 | 1,431,556,072 (Polymath8b 2014) |

Certificates M₁₅,₈₅₆ ≥ 8.013326752751, M₉₂₃,₆₀₁ ≥ 12.006666706750, M₅₆·₁₀⁶ ≥ 16.065482942,
verified in ball arithmetic with outward rounding at every step, under three independent
certification regimes (two Berry–Esseen constants × two tail routes). Tuples explicit: diameter
173,438 at k = 15,856 (admissibility re-verified by a second implementation); a repaired
Hensley–Richards tuple of diameter 13,859,802 at k = 923,601, with a fully classical fallback of
diameter 14,505,780; the primes-past-k tuple at k = 5.6·10⁷ with endpoints checked against
published values of π(x).

These are computer-assisted results produced by AI systems and have not been refereed; all
certificates and scripts are published for replay. A further conditional improvement
(H₂ ≤ 145,226 via Deligne-strength equidistribution) is deliberately **not** claimed.

### 5.5 Why 246 did not move: five walls

1. **The ceiling is the tuple diameter.** No post-processing of Maynard–Tao output beats H(k_min);
   pair-correlation constants cannot lower H₁ at all.
2. **Scalar decoding is exactly optimal.** A two-point counterfeit ordered by convex order defeats
   every matrix, inertia or higher-moment decode; the threshold f(m) = 2m/θ is final.
3. **The weight cone is closed.** Enlarging squares to PSD forms gains nothing — rank-r sums of
   squares decouple by subadditivity — and the copositive relaxation is flat, certified by an
   explicit nine-pattern dual with residual 1.3·10⁻¹⁴.
4. **Parity, made combinatorial.** A Liouville twist kills a set of pair-conclusions iff its
   kill-graph is bipartite (odd-cycle facets of the cut polytope), giving the floors H₁ ≥ 6 and
   k ≥ 2m + 1. *(The graph fact is Tao's, from his 2014 parity-obstruction note; the cut-polytope
   packaging is ours.)*
5. **The usable arithmetic frontier is not the published frontier.** The levels θ = 4/7 (BFI),
   3/5 (Maynard II) and 5/8 (Pascadi) are well-factorable or fixed-residue, while Maynard–Tao needs
   uniformity over a CRT-structured residue system varying with the modulus.

**The k = 49 door, priced exactly.** The pure constant obeys the classical bound
M₄₉ ≤ (49/48)·log 49 = **3.97290 < 4**, so *no enrichment of the test-function basis can ever reach
the threshold in the pure class* — higher power-sum rows, semidefinite relaxations and generalised
eigenvalue tests are all dead on arrival there, and running them is wasted compute. Only the
ε-variant survives, where the bound relaxes to (1 + ε)·3.97290 and closes only for ε ≤ 0.00682. Our
best certified value is M₄₉,₁/₃₅ ≥ 3.930490592 with float optimum 3.959325169, against the threshold
4: gap 0.0407. That, and k = 47 (payoff H₁ ≤ 226), are the only doors left.

---

## 6. The signed sieve: an identity that closes a decade-old temptation

Maynard–Tao weights are squares, hence nonnegative, and positivity is what makes the decode valid.
Chen's theorem, Iwaniec's linear-sieve weights λ^±, and Zhang's Landau–Siegel programme are all
built from *signed* objects, so it is natural to ask what the signed enlargement buys. For signed w
the decode fails — positive excess can be manufactured by w(n) < 0 at prime-poor n — and is repaired
by paying the **debt** D(w) = Σ_{w(n)<0} |w(n)|·(m − ν(n))₊, where ν(n) = #{i : n + h_i prime}.

**Pointwise identity.** For every integer ν ≥ 0 and every m ≥ 1, (ν − m) + (m − ν)₊ = (ν − m)₊.

**Theorem (Signed No-Gain).** With w = w₊ − w₋ of disjoint support,

  **S₂ − mS₁ − D(w) = Σ w₊(n)(ν(n) − m) − Σ w₋(n)(ν(n) − m)₊ ≤ Σ w₊(n)(ν(n) − m).**

*Proof.* Substitute the identity in the w₋ terms; the last step is w₋ ≥ 0 and (ν − m)₊ ≥ 0. ∎

**Corollary.** Any DHL(k, m+1) conclusion obtainable from a signed weight with the debt charged at
face value is already obtainable from its positive part. The negative part is pure loss, of exactly
the overshoot mass Σ w₋(ν − m)₊.

The statement is pointwise: no model, no asymptotics, all k, m, tuples and weight classes at once.
Verified additionally in exact rational arithmetic on a finite arithmetic microcosm — cellwise
identity with zero violations, and the inequality on 1,000 random signed weights across five models.

**What the numerics had been showing.** Three phenomena looked like a phase structure; all three are
corollaries. (i) Sweeping the debt price β in max{Φ − βD : S₁ = 1}, the value equals the classical
optimum above a sharp β\*, computed here in exact rational arithmetic with a verified dual:
classical value **1087376209/3212440751**, critical price **β\* = 23051796480/10991046857 =
2.0973249209…**, with 85% of the optimiser's mass negative on 16 of 96 cells, and unboundedness
below β_unb = 2.03265. Since β\* > 1 always, the "phase" lives entirely at debt prices below face
value. (ii) Imposing ‖w‖₁ ≤ A gives λ(1) = λ_positive exactly and then a positive slope
0.32–0.89 — not a gain, since the decode is scale-invariant and what grows is the mass of w₊.
(iii) At β = 1 every model is unbounded, which exposes the second, usually unremarked job positivity
performs: for w ≥ 0 the normalisation S₁ = 1 *is* the ℓ¹ norm, so **positivity is what makes the
variational problem bounded.**

**Hence exactly two escapes, neither variational.** (a) Charge the debt below face value — requiring
arithmetic information that bounds (m − ν)₊ on a designed negative support below the truth, which is
precisely the exceptional-character mechanism. By the theorem, **Zhang's programme is not one route
among several; it is the only route that changes the variational picture at all.** (b) Keep w
evaluable while w₊ is not — the positive part of a divisor-sum quadratic is not a divisor-sum
quadratic, so a signed well-factorable λ can be evaluable at θ = 4/7, 3/5, 5/8 while its positive
part is evaluable at no level beyond 1/2.

An independent argument from the switching side agrees. Switching never reduces the number r of
exact-primality conditions in a debt term; Chen's debt has r = 1 and is payable by an upper sieve,
while every DHL(k, m+1) with m ≥ 1 forces residual debt with r ≥ 2, and a two-vertex kill-graph is
an edge, hence bipartite, hence parity-blocked wherever Liouville twists are admissible. Two
disjoint analyses, one door.

**The price list, if the debt were paid at level θ.** All eight m = 1 crossings carry exact-rational
certificates; H(k) is Engelsma-exact.

| θ | threshold | k pure (certified M_k) | k with ε | H₁ ≤ pure / ε |
|---|---|---|---|---|
| 1/2 (Bombieri–Vinogradov) | 4 | 54 | 50 | 270 / **246** (unconditional) |
| 4/7 (BFI) | 3.5 | 31 (3.502015…) | 29 (3.519881…) | 140 / **130** |
| 7/12 (Maynard II) | 24/7 | 29 (3.443305…) | 26 (3.433616…) | 130 / **114** |
| 3/5 (Maynard II) | 10/3 | 26 (3.350647…) | 23 (3.334616…) | 114 / **94** |
| 5/8 (Pascadi) | 3.2 | 22 (3.207656…) | 20 (3.222666…) | 90 / **80** |
| 1 (Elliott–Halberstam) | 2 | 5 (M₅ = 2.007080) | — | **12** |

None of BFI, Maynard II or Pascadi covers the sums the decode generates: all three fix one residue
per modulus, while the decode's residues are CRT-composed from the shift set and vary with q. The
sufficient intermediate statement is

> **(E_θ).** For coefficient systems c_q(a) jointly well-factorable with the residue selection —
> for every factorisation q = q₁q₂ (resp. q₁q₂q₃) with ∏Q_j = x^{θ−ε} one can write
> c_q(a) = ∏_j γ_j(q_j, a mod q_j), |γ_j| ≤ 1, with a mod p ∈ {h_i − h_j mod p : j ≠ i} for p | q —
>   Σ_{q ≤ x^{θ−ε}} Σ_{a ∈ A_i(q)} c_q(a)·E(x; q, a) ≪_{H,A,ε} x(log x)^{−A}.

(E_{4/7}) is "BFI Theorem 10, uniform over the CRT residue system of a fixed tuple polynomial".
Polymath8a's MPZ[ϖ,δ] is its absolute-value cousin, proved by the same dispersion-plus-Deligne
technology but only to level ≈ 0.5286, so (E_θ) interpolates two proved endpoints rather than
crossing a parity barrier.

---

## 7. Formalisation and machine verification

Every theorem in §1.7, §1.8 and §2 is elementary enough to formalise, and we report precisely what
has been machine-checked, by which tool, and what has not.

### 7.1 What could not be done here, and why

We could not compile Lean. The session's egress proxy returns a **403 policy denial** for
`elan.lean-lang.org` and for `github.com` release downloads, and organisation policy denials are not
to be retried. Public repositories are readable over git, but a Lean toolchain ships as a binary
release, and building Lean plus Mathlib from source is not feasible here. The Lean file below is
therefore **written but not compiled**; we present it as a formal specification rather than a
verified artifact, and mark with `sorry` the two steps that need Mathlib's ODE comparison API,
which we decline to guess at without a compiler.

### 7.2 What was machine-checked, and how

In place of Lean we discharged every algebraic and analytic step by exact symbolic computation
(`sympy`, rational arithmetic throughout — no floating point) and, where the statement is a decision
problem over the reals, by SMT (`z3`). Script `fab_verify_proof.py`: 18 checks, all passing.

| step | statement | tool | status |
|---|---|---|---|
| 1a | ∂_s of the flow equals (N·D_z − D_z²) on each monomial z^j | sympy, exact | ✔ |
| 1b | 2z_j/(z_j − z_k) = 1 − i·cot((θ_j − θ_k)/2) | sympy, exact | ✔ |
| 1c | the (N−1) terms cancel, leaving θ̇_j = −Σ cot | sympy, exact | ✔ |
| 2a | cos(g/2) = e^s cos(g₀/2) solves g′ = −2cot(g/2) | sympy, exact | ✔ |
| 2b | the collision time is −log cos(g₀/2), and the gap vanishes there | sympy, exact | ✔ |
| 3 | d/dx cot(x/2) = −½csc²(x/2), strictly negative on (0, 2π) | sympy, exact | ✔ |
| 4a | f(0) = 0 and f′(x) = ¼(2tan(x/2) − x) for f = −log cos(x/2) − x²/8 | sympy, exact | ✔ |
| 4b | tan t − t has nonnegative Taylor coefficients (⅓, 2/15, 17/315, 62/2835, 1382/155925, …) | sympy, exact | ✔ |
| 5 | the sign lemma as a real-arithmetic decision problem: **unsat** for the negation | z3 | ✔ |
| 6 | the ACUE pigeonhole giving δ_min = π/N | exact integer reasoning | ✔ |
| 7 | Σ_{k=1}^{N−1} ½csc²(πk/N) = (N²−1)/6, at N = 4, 6, 8, 12, 20 | sympy, exact | ✔ |

Step 5 deserves comment, because it is the one place where a decision procedure is genuinely the
right tool. Encoding the cosines and sines of the two half-angles as reals ca, sa, cb, sb subject to
ca² + sa² = 1, cb² + sb² = 1, sa, sb > 0, together with the ordering constraint sa·cb − ca·sb > 0
(that is, sin(a − b) > 0 for 0 < a − b < π), z3 reports **unsat** for the negation
ca·sb − cb·sa ≥ 0 of the conclusion. The sign of every background term is therefore certified by a
complete decision procedure over the reals rather than by inspection of a graph.

### 7.3 The Lean specification

```lean
/-- The cotangent, spelled directly so as not to depend on a particular Mathlib name. -/
noncomputable def cot (x : ℝ) : ℝ := Real.cos x / Real.sin x

lemma hasDerivAt_cot {x : ℝ} (hx : Real.sin x ≠ 0) :
    HasDerivAt cot (-(1 / Real.sin x ^ 2)) x

/-- `cot` is strictly decreasing on `(0, π)`: the sign input to Theorem A. -/
lemma cot_strictAntiOn : StrictAntiOn cot (Set.Ioo (0 : ℝ) π)

/-- **Background sign lemma.**  For an adjacent pair the other zeros satisfy
`0 < x_b < x_a < 2π`, and the resulting bracket is negative — so it enters the gap
derivative with a positive sign and slows the collapse. -/
lemma background_sign {xb xa : ℝ} (h0 : 0 < xb) (hlt : xb < xa) (h2 : xa < 2 * π) :
    cot (xa / 2) - cot (xb / 2) < 0

/-- **The depth inequality.** `−log (cos (x/2)) ≥ x²/8` on `[0, π)`. -/
lemma neg_log_cos_ge {x : ℝ} (h0 : 0 ≤ x) (h : x < π) :
    x ^ 2 / 8 ≤ -Real.log (Real.cos (x / 2))

/-- Exact solution of the two-body gap equation. -/
theorem two_body_solution
    (g : ℝ → ℝ) (hg : ∀ s, HasDerivAt g (-2 * cot (g s / 2)) s)
    (hrange : ∀ s, g s ∈ Set.Ioo (0 : ℝ) (2 * π)) (s : ℝ) :
    Real.cos (g s / 2) = Real.exp s * Real.cos (g 0 / 2)

/-- **Theorem A.** Every gap dominates the two-body solution started from the same
initial value, so no gap reaches `0` before `−log (cos (δ/2)) ≥ δ²/8`. -/
theorem depth_ge {ι : Type*} [Fintype ι] (g : ι → ℝ → ℝ) (δ : ℝ)
    (hδ0 : 0 < δ) (hδπ : δ < π) (hmin : ∀ i, δ ≤ g i 0)
    (hineq : ∀ i s, -2 * cot (g i s / 2) ≤ deriv (g i) s) :
    δ ^ 2 / 8 ≤ -Real.log (Real.cos (δ / 2))
```

The full file — proofs for the first four items, `sorry` for the last two — is
`lean/DepthComparison.lean`. `cot_strictAntiOn` is proved from the derivative via
`strictAntiOn_of_hasDerivWithinAt_neg`; `background_sign` follows at once; `neg_log_cos_ge` reduces
to `t ≤ tan t` on `[0, π/2)`. What remains for a complete formalisation is `two_body_solution`
(uniqueness for a scalar autonomous ODE) and the comparison step inside `depth_ge` (a Grönwall-type
argument); both are standard and both are within Mathlib's reach.

### 7.4 The honest summary

The mathematics of Theorem A is verified: every algebraic identity by exact symbolic computation,
the one inequality with real content by a complete decision procedure over the reals, and the
numerical consequences on 11,060 background terms with zero exceptions. What is *not* verified is a
Lean proof object, because no Lean toolchain could be obtained in this environment. The distinction
is worth stating plainly, since "formalised" and "machine-checked" are often conflated and only the
second is true here.

---

## 8. How this was done

The method is part of the result, so we describe it plainly.

**Fleets, not oracles.** Work proceeded in rounds. Each round posed one question and three to ten
language-model agents attacked it in parallel from deliberately different angles, each writing and
running its own code, each reporting line by line as *proved*, *computed*, *heuristic* or
*conjecture*. Agents shared a written context file stating the current state of knowledge including
known errors, but not conclusions: convergence of independent agents was treated as evidence,
divergence as a bug report.

**Adversarial defaults.** Every context file instructed agents that the default assumption is that
the idea has already been tried and failed, and that their first job is to find the reason. The
prompt for the prime-gap round said outright that any improvement to 246 was 99% likely to be a
misread constraint. Of the phenomena that looked like discoveries during this project, most were
arithmetic or normalisation errors; the survivors survived because they were attacked first by
their own authors.

**Exact arithmetic at every threshold.** Nothing near a decision boundary was accepted in floating
point: ball arithmetic with outward rounding for the Maynard certificates, exact-rational Rayleigh
quotients for the variational crossings, exact Vandermonde masses with 40-digit spot checks for the
ACUE enumeration, exact rationals for the signed-sieve identity and the critical price β\*. The most
common failure mode in machine-generated mathematics is a plausible float, and the remedy is cheap.

**Two implementations or it did not happen.** Every headline number here was produced twice by
independent code, usually by agents that could not see each other's work: record tuples re-verified
by a second admissibility checker; CUE depth by an ODE integrator and by coefficient bisection
agreeing to 10⁻⁶; the single-dislocation constant by a lattice enumeration and by a transcendental
double-root equation, agreeing to six digits. Where two implementations disagreed — an engine
crossing at k = 15,856 against another at 29,500 — the discrepancy was tracked to its source before
anything was claimed.

**The human supplies the questions.** Every genuinely new direction came from a human
mathematician's judgement: to stop optimising 246 and look at H₂; to ask whether removing the
square opens a phase; to propose the de Bruijn–Newman depth as a dynamic observable at all; to
insist that the constant 72π be factorised rather than fitted; to recognise the single-dislocation
configuration as the right object to compute exactly. The models supplied speed, breadth, exact
arithmetic, and the willingness to write and discard fifty scripts a day.

**Negative results are the main product.** Five walls, one no-go theorem, one empty phase, one
refuted extrapolation, one refuted mechanism for the marked depth, one refuted hope for the
moment-deflation channel. A method that only reports successes cannot be trusted about them. The
single most valuable output of the signed-sieve round is that the route is closed and we can say
exactly what would open it.

---

## 9. Open problems

1. **Complete the CUE depth law**: Theorems A and B (§1.7) reduce 8N^{8/3}(−Λ) ⟹ G² to the cited
   smallest-gap law; what remains is a high-probability bound on the background coefficient
   B ≤ AN² (§1.8) — a CUE rigidity statement controlling Σ_k d_k^{−2} near the extremal pair.
   Measured: median B/N² = 0.120, max observed 0.79. This same bound completes Theorem C(ii).
2. **Bound ρ for the lattice**: prove ρ^ACUE ≤ C, completing Law 2's upper bound. The lower bound
   −Λ ≥ π²/(8N²) is now exact (§1.7). This is a constant problem for one specific configuration
   family, not a universality problem.
3. **Make s\* = 1.419640342… a theorem** for the single-dislocation family, and compute the
   separated-defect constant ρ∞ = 1.19120… exactly; the natural setting is an infinite clock with
   one localised defect under the Coulomb dynamics.
4. **The marked depth law**: prove Dτ_G[uu\*] = (κδ/4)·u\*K_{ab}u + (δ²/8)·κ′(u) as an asymptotic
   identity with controlled error, and characterise the background term κ′. Numerically the law is
   exact (correlation 1.00000000, residual 5.7·10⁻¹¹); what is missing is the same localisation
   estimate as problem 1, differentiated. A natural sub-target: on the null cone c_a q_a = c_b q_b,
   show the leading behaviour is governed by λ_j″ = 2q_j Σ_{k≠j} q_k/(λ_j − λ_k).
5. **A transversality theorem**: with static observables M and fibre F_m, prove τ|_{F_m} generically
   non-constant, adding marks until ⋂ ker DΛ_{u_j} ∩ ker DM = {0}.
6. **Transport the Palm certificates to the depth**, aiming at a bound μ_Λ < 1.8177 — which by
   §3.5 would improve the Lagarias–Rodgers upper bound on μ.
7. **(E_θ)**, the tuple-residue well-factorable estimate, for any θ > 1/2: the single statement
   between the certified price list and H₁ ≤ 130.
8. **The k = 49 door**, in the ε-class only: certified 3.930490592, float 3.959325169, threshold 4,
   upper bounds closing only ε ≤ 0.00682.

---

## References

J. Maynard, *Small gaps between primes*, Ann. of Math. 181 (2015) 383–413 ·
D.H.J. Polymath, *Variants of the Selberg sieve…*, Res. Math. Sci. 1:12 (2014) ·
Y. Zhang, *Bounded gaps between primes*, Ann. of Math. 179 (2014) ·
J. Stadlmann, Adv. Math. (2025) ·
E. Bombieri, J. Friedlander, H. Iwaniec, Acta Math. 156 (1986) ·
J. Maynard, *…large moduli II: well-factorable estimates*, Mem. AMS 1543 ·
A. Pascadi, arXiv:2505.00653 ·
K. Ford, J. Maynard, *On the theory of prime producing sieves*, arXiv:2407.14368 ·
T. Tao, *A general parity problem obstruction* (2014) ·
B. Rodgers, T. Tao, *The de Bruijn–Newman constant is non-negative*, Forum Math. Pi 8 (2020) ·
T. Tao, *The alternative hypothesis for unitary matrices* (2019) ·
J.C. Lagarias, B. Rodgers, *Band-limited mimicry of point processes by point processes supported on
a lattice*, Ann. Appl. Probab. 31 (2021) 351–376; *Higher correlations and the Alternative
Hypothesis*, Q. J. Math. 71 (2020) 257–280 ·
L. Guth, J. Maynard, *New large value estimates for Dirichlet polynomials*, arXiv:2405.20552 ·
G. Ben Arous, P. Bourgade, Ann. Probab. 41 (2013) ·
R. Feng, D. Wei, Ann. Probab. 49 (2021) ·
R. Killip, I. Nenciu, IMRN (2004) ·
T. Engelsma, minimal admissible tuples; A.V. Sutherland, narrow admissible tuples database.
