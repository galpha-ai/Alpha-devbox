# Stopping Times See What Moments Cannot

## Prime gaps, signed sieves, and a dynamic separation of CUE from the alternative hypothesis

**Bill (Qingyun) Sun · GPT5.6SOL · Fable**

*August 2026*

---

## Abstract

We report on a research programme carried out by a human mathematician working with several
large language models in a tight adversarial loop. Three groups of results are described.

**(1) Prime gaps.** New unconditional bounds for gaps containing several primes:
liminf(p_{n+2} − p_n) ≤ 173,438, liminf(p_{n+3} − p_n) ≤ 13,859,802, and
liminf(p_{n+4} − p_n) ≤ 1,120,662,828, improving the previous records 396,504 / 24,797,814 /
1,431,556,072 by factors 2.3 / 1.8 / 1.3. The gain is purely variational: the records since 2014
had upgraded the arithmetic input while retaining a crude closed-form bound on the Maynard–Tao
functional. We also give a no-go map for H₁ = 246 with five proved walls, and price the two doors
that remain open.

**(2) Signed sieves.** A one-line pointwise identity shows that the signed (indefinite) enlargement
of the Maynard–Tao variational problem is *empty*: with the decode debt charged at face value,
every signed weight is dominated by its own positive part. This closes the variational side of a
programme suggested by Zhang's Landau–Siegel work and by Iwaniec's well-factorable weights, and
—more usefully—shows that everything of value in the signed route is arithmetic, not variational.
We give the precise missing estimate (E_θ) for each level θ ∈ {4/7, 7/12, 3/5, 5/8} together with
the conditional price list it would buy (H₁ ≤ 130, 114, 94, 80).

**(3) A dynamic separation.** Tao's alternative hypothesis ensemble ACUE matches CUE on every
low-order statistic that bandwidth-limited detectors can see. We first measure the obstruction: the
exact fibre of measures matching all balanced moments of degree ≤ N has dimension 0, 0, 2, 10, 80,
403, 1804 for N = 3, …, 9, contains an explicit (N−3)-parameter family q_ACUE(C)·g(Σc mod N) with
ĝ(±1) = 0, and — because the heat flow is diagonal in the coefficients — stays frozen to that
algebra along the *entire* flow. We then show that a *stopping time* escapes it: the finite
de Bruijn–Newman depth Λ, the first collision time of the zeros under backwards heat flow,
separates CUE from ACUE at the level of universality class, −Λ^CUE ≍ N^{−8/3} against
−Λ^ACUE ≍ N^{−2}. The exponent gap is the extreme-value statistics of the spectrum in scalar form:
CUE admits rare pairs at distance N^{−4/3} while the lattice quantises every gap at π/N, so the
alternative hypothesis satisfies its own RH-analogue *too robustly*. More generally, for the
circular β-ensembles we find and confirm −Λ ≍ N^{−2−2/(β+1)} at β = 1, 2, 4, with the rigid lattice
as the β = ∞ endpoint. The methodological content is a slogan:

> **moment matching does not imply stopping-time matching.**

---

## 1. What this paper is about

Three problems, three walls, and one way through.

The first wall is the bounded gaps problem. Since Zhang, Maynard and Polymath8, the record
liminf(p_{n+1} − p_n) ≤ 246 has stood for twelve years. We did not move it, and we explain in
§3 why we now believe it is protected by a specific and provable structure rather than by a lack
of effort. But the same analysis showed that the *higher* records — two, three, four primes in a
bounded window — were protected by nothing at all, and those we did move.

The second wall is positivity. Maynard–Tao weights are squares. Everybody who has worked with them
has wondered what happens if you drop the square; Zhang's Landau–Siegel programme is built around
exactly this, and Iwaniec's linear-sieve weights λ^± are signed and consume levels of distribution
that squares cannot reach. We settle the variational half of that question completely, in the
negative, by an identity that fits on one line.

The third wall is the alternative hypothesis. Tao's ACUE ensemble is a lattice-supported measure on
unitary spectra that reproduces CUE's pair correlation and, as we and others have verified, an
entire algebra of low-degree statistics. The programme of "find a moment ACUE cannot fake" has
been running for years and keeps hitting the same obstruction: the fibre of measures matching a
given set of moments is large — we compute it exactly, and it reaches dimension 403 by N = 8 — so
adding one more moment enlarges the search rather than ending it. Our contribution is to stop
adding moments. A *stopping time* is not a polynomial statistic, and the fibre's freedom does not
protect it: what it protects is the algebra of observables, and the first-passage time of a flow is
not in that algebra.

The paper is written to be read by mathematicians, not by machines; but the last section describes
how the work was actually done, because the method is part of the result.

---

## 2. Prime gaps: what moved and why

### 2.1 The framework in one paragraph

Fix an admissible k-tuple H = {h₁, …, h_k} (admissible: for each prime p, the h_i do not cover all
residues mod p). Maynard's method attaches to each n a weight w(n) = (Σ_d λ_d)² built from divisor
sums, and compares S₁ = Σ w(n) with S₂ = Σ w(n)·#{i : n + h_i prime}. If the primes have level of
distribution θ and the variational constant

  M_k = sup_F k·J(F)/I(F),  I(F) = ∫_{R_k} F², J(F) = ∫_{R_{k−1}} (∫₀^{1−Σ} F dt_k)²,

taken over symmetric F on the simplex R_k = {t ∈ [0,∞)^k : Σt_i ≤ 1}, exceeds 2m/θ, then every
admissible k-tuple contains m+1 primes infinitely often, and hence H_m := liminf(p_{n+m} − p_n) is
at most the diameter H(k) of the narrowest admissible k-tuple. Bombieri–Vinogradov gives θ = 1/2
unconditionally, so the criterion is M_k > 4m.

Two quantities therefore control everything: the analytic constant M_k, and the combinatorial
constant H(k). The record H₁ = 246 comes from k = 50 and a variant of M_k tuned by an ε-trick.

### 2.2 The observation

For m = 1, k is small (50) and M_k has been computed to death. For m ≥ 2, k is large — tens of
thousands to millions — and there M_k has never been computed at all. Every record since 2014 has
used the same crude closed-form lower bound, essentially M_k ≥ log k − C with an explicit but
generous C, obtained by truncating a product test function hard at the simplex boundary. The
improvements of 2023–2025 raised θ, not M_k.

The deficit in that bound is between 2.3 and 2.9 units of log k, and about 1.1 of those units are
recoverable by elementary means. Since M_k ≈ log k, recovering 1.1 units is a factor e^{1.1} ≈ 3
in k, and H(k) ≈ k(log k + 0.77) is nearly linear in k, so a factor 3 in k is close to a factor 3
in H_m.

### 2.3 The engine

Take F(t) = ∏_i g(t_i) · 1[Σt_i ≤ k] (working on the dilated simplex). Let X_i be i.i.d. with
density g²/c₂ where c₂ = ∫g², write S_j for partial sums, and G(u) = ∫₀^u g. Then exactly

  I(F) = k^{−k} c₂^k · P(S_k ≤ k),  J(F) = k^{−(k+1)} c₂^{k−1} · E[G((k − S_{k−1})₊)²].

The simplex truncation, which the classical treatment handles by throwing it away, is now a genuine
probability, and the second factor is unwrapped by the **layer-cake identity**

  E[G((k − S)₊)²] = ∫ 2G(u) g(u) · P(S_{k−1} < k − u) du,

turning it into an integral of true lower-tail probabilities. Each of those is bounded below
rigorously (chord-majorised Chernoff, one-big-jump, Berry–Esseen with the safe non-i.i.d. constant
0.56); because the bounds use only monotonicity of the true tail, discretisation cannot invalidate
them. Finally, replacing the hard truncation by **shaped subexponential tails**
g(t) = e^{−(t/T₁)^κ}/(1 + At) on a long support recovers the rest.

Exact accounting of the truncation contributes +0.12 units, tail shaping +0.49, and the remainder
comes from optimising the shape parameters — about 1.1 units in total, as predicted.

### 2.4 The results

| | bound | k | previous |
|---|---|---|---|
| H₂ = liminf(p_{n+2} − p_n) | **173,438** | 15,856 | 396,504 (Stadlmann 2023/25) |
| H₃ | **13,859,802** | 923,601 | 24,797,814 (Polymath8b 2014) |
| H₄ | **1,120,662,828** | 56,000,000 | 1,431,556,072 (Polymath8b 2014) |

The certificates M₁₅,₈₅₆ ≥ 8.013326752751, M₉₂₃,₆₀₁ ≥ 12.006666706750 and M₅₆·₁₀⁶ ≥ 16.065482942
are verified in ball arithmetic with outward rounding at every step; three independent
certification regimes (two Berry–Esseen constants × two tail routes) pass at each k. The tuples are
explicit: for k = 15,856 an admissible tuple of diameter 173,438 verified by two independent
implementations; for k = 923,601 a repaired Hensley–Richards tuple of diameter 13,859,802 (with a
fully classical fallback of diameter 14,505,780 from the primes past k); for k = 5.6·10⁷ the
primes-past-k tuple, its endpoints checked against published values of π(x).

These are computer-assisted results produced by AI systems and have not been refereed. All
certificates and scripts are published for replay. A further conditional improvement
(H₂ ≤ 145,226 via Polymath8a/Deligne-strength equidistribution) is deliberately **not** claimed:
it depends on a cap normalisation we reconstructed but could not verify verbatim.

### 2.5 Why 246 did not move: five walls

We spent a comparable effort on H₁ and failed, but the failure is informative. Five statements,
each proved during this work, close five different escape routes.

1. **The ceiling is the tuple diameter.** No post-processing of Maynard–Tao output can produce a
   bound below H(k_min). In particular, pair-correlation constants of the Wu/Lichtman type — which
   look like they should help — cannot lower H₁ at all.
2. **Scalar decoding is exactly optimal.** One might hope to replace "S₂ − mS₁ > 0" by a matrix,
   inertia, or higher-moment decode. A two-point counterfeit construction, ordered by convex order,
   defeats every such decode; the scalar threshold f(m) = 2m/θ is final.
3. **The weight cone is closed.** Enlarging squares to arbitrary PSD quadratic forms Q gains
   nothing: rank-r sums of squares decouple by subadditivity, so the supremum is attained at rank
   one. The copositive relaxation is flat as well, certified by an explicit nine-pattern dual with
   residual 1.3·10⁻¹⁴.
4. **Parity, made combinatorial.** A parity (Liouville) twist kills a set of pair-conclusions if
   and only if the associated *kill-graph* is bipartite; odd-cycle facets of the cut polytope are
   exactly the obstructions. This yields the floors H₁ ≥ 6 and k ≥ 2m + 1 for the whole method
   class.
5. **The usable arithmetic frontier is not the published frontier.** The post-2014 levels θ = 4/7
   (Bombieri–Friedlander–Iwaniec), 3/5 (Maynard II) and 5/8 (Pascadi) are *well-factorable* or
   *fixed-residue*. Maynard–Tao needs uniformity over a CRT-structured system of residues varying
   with the modulus, which none of them provides. The usable frontier is Maynard III's 11/21 with
   a shell truncation, Stadlmann's 1/2 + 1/40, and Pascadi's minorant 10/19 — all shell-restricted.

What remains open is narrow and precisely priced. The k = 49 door needs M₄₉-variant > 4; the pure
constant is M₄₉ ∈ [3.891258, 3.97290] (lower bound exact-rational), and the best certified ε-variant
is M₄₉,₁/₃₅ ≥ 3.930490592 with float optimum 3.959325169. Known upper-bound technology closes the
door only for ε ≤ 0.00682, so the door is open, exactly as Polymath left it. Crossing it would give
H₁ ≤ 240; k = 47 would give 226.

---

## 3. The signed sieve: a one-line no-go

### 3.1 The question

Since Maynard–Tao weights are squares, and since Chen's theorem and Iwaniec's λ^± are both built
from *signed* objects, it is natural to ask what a signed sieve would buy. Zhang's Landau–Siegel
programme is organised around removing the square. The hope is a variational phase invisible to the
positive family.

For signed w the decode fails: the positive excess can be manufactured by w(n) < 0 at prime-poor n.
It is repaired by paying the **debt**

  D(w) = Σ_{n : w(n) < 0} |w(n)| · (m − ν(n))₊,  ν(n) = #{i : n + h_i prime},

after which S₂ − mS₁ − D > 0 does imply that some n has ν(n) ≥ m + 1. So the honest experiment is
to optimise Φ(w) − βD(w) with β = 1 the true price, and look for a phase transition.

### 3.2 The identity

For every integer ν ≥ 0 and every m ≥ 1,

  (ν − m) + (m − ν)₊ = (ν − m)₊,

both sides being ν − m when ν ≥ m and 0 otherwise. Writing w = w₊ − w₋ with w₊, w₋ ≥ 0 of disjoint
support and substituting:

> **Theorem (Signed No-Gain).**
>   S₂ − mS₁ − D(w) = Σ_n w₊(n)(ν(n) − m) − Σ_n w₋(n)(ν(n) − m)₊ ≤ Σ_n w₊(n)(ν(n) − m).

Since w₋ ≥ 0 and (ν − m)₊ ≥ 0, the negative part is pure loss, and the loss is exactly the
overshoot mass Σ w₋(ν − m)₊ sitting on the negative support.

**Corollary.** Any DHL(k, m+1) conclusion obtainable from a signed weight w with the debt charged
at face value is already obtainable from the nonnegative weight w₊. The signed class is redundant.

The statement is pointwise, so it holds for every k, m, tuple and weight class at once, needs no
asymptotics, and subsumes the weaker fact that the naked ratio sup Tr(BQ)/Tr(AQ) over indefinite Q
equals the PSD value by rank-one extremality.

### 3.3 What the numerics had been showing

We found the identity only after a substantial LP campaign on a finite arithmetic microcosm
(n uniform on ℤ_W, ν the coprimality count on the tuple, weights in the span of level-L features,
everything in exact rational arithmetic). Three phenomena had looked like a phase structure; all
three are corollaries.

- **A critical price.** The value of max{Φ − βD : S₁ = 1} is *exactly* the classical positive
  optimum for β above a sharp β\*, and acquires a signed optimiser below it. In the base model
  (k = 3, features {2,3,5,7}) an exact-rational simplex with certified dual gives the classical
  value **1087376209/3212440751** = 0.3384891094603102 and the critical price

    **β\* = 23051796480/10991046857 = 2.0973249209031…**,

  the signed vertex having Φ = 1.2082816957…, D = 0.4147152297…, with 85% of its mass negative on
  16 of 96 cells. The transition is certified on both sides: at β\* − 10⁻³ the optimum is strictly
  above the plateau (0.3389038246899884 > 0.3384891094603102) and genuinely signed, while at
  β\* + 10⁻³ it equals the plateau as exact rationals. At β = 2 the programme is unbounded. The
  theorem explains why β\* > 1 always: at the true price the signed class is dominated.
- **An apparent linear gain.** Imposing ‖w‖₁ ≤ A gives λ(1) = λ_positive exactly (for w ≥ 0 the
  normalisation S₁ = 1 *is* the ℓ¹ norm) and then a strictly positive slope 0.32–0.89 per unit of
  budget. This is not a gain: the decode is scale-invariant, and what grows with A is the mass of
  w₊, not the truth of the conclusion.
- **Unboundedness at β = 1.** In all eight model variants. Same cause. This exposes a second,
  usually unremarked, job that positivity performs in Maynard–Tao: *it makes the variational
  problem bounded*, by tying the ℓ¹ norm to the normalisation. Remove it and boundedness must be
  re-imposed by hand — and by the theorem, no choice of norm bound creates a gain.

### 3.4 Where the door actually is

The theorem has exactly two hypotheses, hence exactly two escapes, and neither is variational.

**(i) Charge the debt below face value.** This needs arithmetic information bounding (m − ν)₊ on a
*designed* negative support by strictly less than the truth — that is, an input asserting that
primes are anomalously common on a prescribed set. This is precisely the exceptional-character
mechanism. By the theorem, Zhang's programme is not one route among several; it is the only route
that changes the variational picture at all.

**(ii) Keep w evaluable while w₊ is not.** The theorem compares w with w₊, presuming both usable.
Arithmetically they are not interchangeable: the positive part of a divisor-sum quadratic is not a
divisor-sum quadratic, so a signed well-factorable λ can be evaluable at θ = 4/7, 3/5, 5/8 while its
positive part is evaluable at no level beyond 1/2. **The signed route's entire value is which
weights the arithmetic can evaluate, never the shape of the optimum.**

An independent argument from the switching side reaches the same conclusion. Switching is a
re-indexing bijection: it lowers the anatomical depth of one linear form but never the number r of
exact-primality conditions in a debt term. Chen's debt has r = 1 and is payable by an upper sieve
(parity-free). Every DHL(k, m+1) conclusion with m ≥ 1 forces residual debt with r ≥ 2; a two-vertex
kill-graph is an edge, hence bipartite, hence parity-blocked for every input class admitting
Liouville twists. The escape is not a cleverer switch but an input class in which the twist is
inadmissible — the exceptional-character regime again. Two disjoint analyses, one door.

### 3.5 The price list

If the debt is paid at level θ, the consequences are fully computed; all eight m = 1 crossings carry
exact-rational certificates, and H(k) is Engelsma-exact.

| θ | 2/θ | k pure (certified M_k) | k with ε | H₁ ≤ pure / ε |
|---|---|---|---|---|
| 1/2 (Bombieri–Vinogradov) | 4 | 54 | 50 | 270 / **246** (unconditional) |
| 4/7 (BFI) | 3.5 | 31 (3.502015…) | 29 (3.519881…) | 140 / **130** |
| 7/12 (Maynard II, linear sieve) | 24/7 | 29 (3.443305…) | 26 (3.433616…) | 130 / **114** |
| 3/5 (Maynard II) | 10/3 | 26 (3.350647…) | 23 (3.334616…) | 114 / **94** |
| 5/8 (Pascadi) | 3.2 | 22 (3.207656…) | 20 (3.222666…) | 90 / **80** |
| 1 (Elliott–Halberstam) | 2 | 5 (M₅ = 2.007080) | — | **12** |

The missing statement, in the form we would want to see proved:

> **(E_θ).** Fix an admissible tuple H, an index i, and A, ε > 0. For coefficient systems c_q(a)
> jointly well-factorable with the residue selection — for every factorisation q = q₁q₂ (resp.
> q₁q₂q₃) with ∏Q_j = x^{θ−ε} one can write c_q(a) = ∏_j γ_j(q_j, a mod q_j) with |γ_j| ≤ 1 and
> a mod p ∈ {h_i − h_j mod p : j ≠ i} for all p | q — one has
>   Σ_{q ≤ x^{θ−ε}} Σ_{a ∈ A_i(q)} c_q(a) · E(x; q, a) ≪_{H,A,ε} x (log x)^{−A}.

(E_{4/7}) is "BFI Theorem 10, uniform over the CRT residue system of a fixed tuple polynomial".
Polymath8a's MPZ[ϖ,δ] is its absolute-value cousin, proved by the same dispersion-plus-Deligne
technology but only to level ≈ 0.5286 and for densely divisible moduli, so (E_θ) interpolates two
proved endpoints rather than crossing a parity barrier.

---

## 4. Stopping times: the finite de Bruijn–Newman depth

### 4.1 Why the alternative hypothesis is worth attacking

Montgomery's pair correlation conjecture says the normalised gaps between zeros of ζ follow the
GUE law. Half a century later it remains open, and the reason is sharper than "it is hard". The
**alternative hypothesis** (AH) is the scenario in which the normalised gaps all lie
asymptotically in (1/2)ℤ — the zeros sitting on a half-integer lattice rather than fluctuating like
a random matrix spectrum. AH is not idle: it is consistent with everything currently provable about
zeros, and it has real arithmetic consequences (it would force strong bounds on class numbers, and
would be incompatible with certain conjectures on Landau–Siegel zeros). It is precisely the
scenario that the known techniques cannot exclude.

Tao's blog article *The alternative hypothesis for unitary matrices* makes the obstruction concrete
by moving it into random-matrix theory, where it can be computed with. Define the **ACUE** — the
alternative circular unitary ensemble — as the measure on N-point configurations
C ⊂ {2N-th roots of unity}, |C| = N, with

  μ_ACUE(C) = |Δ(ζ^C)|² / (2N)^N,  Δ = Vandermonde, ζ = e^{2πi/2N}.

This is a lattice-supported measure whose eigenvalue gaps are all multiples of half the mean
spacing — a perfect finite model of AH. Tao's point is that ACUE reproduces the CUE two-point
correlation exactly, so any argument that only sees pair statistics cannot distinguish them, and
he asks what does. The natural programme — find the first moment or correlation at which they
differ — has been running ever since, and it keeps colliding with the same difficulty: the set of
measures matching a given list of moments is a large convex body, so ruling out ACUE itself never
rules out its neighbours. One must rule out a *fibre*, not a point.

There is a second thread. The Riemann ξ function has a canonical heat deformation ξ_t, and de
Bruijn and Newman showed there is a constant Λ_dBN such that ξ_t has only real zeros exactly when
t ≥ Λ_dBN. The Riemann hypothesis is Λ_dBN ≤ 0; Rodgers and Tao proved Λ_dBN ≥ 0. So RH, if true,
is *barely* true: ξ sits exactly on the boundary of heat stability, which is Newman's dictum that
the Riemann hypothesis, if true, is only just true. Crucially, Rodgers and Tao's proof is a
statement about *dynamics*: assuming Λ_dBN < 0 forces the zeros, run backwards, into an
increasingly rigid local equilibrium — a clock — which contradicts what is known about their
fluctuations.

This paper joins the two threads. The second suggests the observable that resolves the first.

### 4.2 How large the blind spot really is: explicit mimicker families

Before looking for a distinguishing statistic it is worth measuring the enemy. We constructed, for
each N, the exact convex body of probability measures on the ACUE support matching every balanced
moment E[p_λ p̄_ν] of degree ≤ N — the *mimicker fibre*. Everything here is exact (rational
Vandermonde masses, rank computed with a spectral gap of 10⁶ or better).

**The fibre.** Its affine dimension at the level of rotation orbits is

| N | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|
| dim of mimicker fibre | 0 | 0 | 2 | 10 | 80 | 403 | 1804 |

So for N ≤ 4 the moment data pins the measure — ACUE is rigid and any statistic distinguishes it.
From N = 5 the fibre opens, and it grows explosively. At N = 8 there are 403 independent directions
in which one may deform ACUE without changing a single balanced moment of degree ≤ N.

**An explicit family for every N.** Inside the fibre there is a clean closed-form subfamily. Let
X(C) = Σ_{c ∈ C} c mod N be the centre-of-mass class and set

  q_g(C) = μ_ACUE(C) · g(X(C)),  g : ℤ/N → ℝ_{≥0}.

Then q_g matches all balanced moments of degree ≤ N **iff** E[g] = 1 and the Fourier coefficients
ĝ(±1) vanish; all other frequencies are free. Hence a family of affine dimension **N − 3**,
nonempty for every N ≥ 4 and verified directly at N = 5, 6, 7, 8 (null dimensions 2, 3, 4, 5;
worst balanced-moment error 10⁻¹²; positivity radius in random null directions up to 1.0–2.2, so
genuinely positive measures, not signed deformations).

| N | family dim | forced-zero frequencies | free frequencies |
|---|---|---|---|
| 5 | 2 | j = ±1 | j = 2 |
| 6 | 3 | j = ±1 | j = 2, 3 |
| 7 | 4 | j = ±1 | j = 2, 3 |
| 8 | 5 | j = ±1 | j = 2, 3, 4 |

**A second, representation-theoretic family.** Writing D_r(C) = ∏_{c∈C} ζ^{rc} = det(U_C)^r for the
determinant character, the tilts

  q(C) = μ_ACUE(C)·[1 + c·Re(η D_r(C))],  |η| = 1, 0 ≤ c ≤ 1,

also lie in the fibre. These have an exact quantum-mechanical description: μ_ACUE is the Born
distribution |⟨C | (∧^N F)A₀⟩|² of a single Slater determinant (F the DFT matrix, A₀ the Fermi sea
e₀∧…∧e_{N−1}) — a re-proof that ACUE is a projection determinantal process — and the tilted family
is the interference pattern of *two* shifted Fermi seas, a coherent superposition
(|Ω₀⟩ + a|Ω_r⟩)/√(1+a²) with c = 2a/(1+a²). In Plücker coordinates ACUE is a point of the
Grassmannian Gr(N, 2N) and the mimickers are points of its first secant variety
σ₂(Gr(N,2N)) \ Gr(N,2N): the minimal non-Gaussian deformations of a fermionic Gaussian state.

**How invisible are these directions?** At N = 8, of the 403 fibre directions, 401 are invisible to
*every* pattern count of window width ≤ 2, 397 to width ≤ 3, 396 to width ≤ 4, 392 to width ≤ 5,
and 383 to width ≤ 6. The blind spot is not a thin exceptional set; it is almost the whole fibre.

**And the flow does not help.** Writing P(z) = det(I − zU) = Σ_j a_j z^j, the finite analogue of
the de Bruijn–Newman deformation is

  P_r(z) = Σ_j a_j r^{j(N−j)} z^j,  t = log r,

which is *diagonal in the coefficients*. Consequently every balanced moment of degree ≤ N is a
t-dependent linear combination of frozen quantities, so it stays frozen along the **entire**
trajectory — we verified this to 4.5·10⁻¹⁶ on explicit mimickers. Evolving the moments you already
have is provably futile, and so is adding one more.

This is the situation the rest of the section is about: a large, explicitly parameterised family of
impostors, invisible to a whole algebra of observables, and invisible to that algebra for all time.

### 4.3 The observable

Define the **finite depth**

  −Λ(U) = t\*, the first time (going backwards, t < 0) at which the discriminant of P_t vanishes,

i.e. the first collision of two zeros. Because the flowed polynomial stays self-inversive, a simple
zero cannot leave the unit circle without first colliding, so this is well defined. Equivalently the
zeros move by the attracting circular Coulomb dynamics

  θ̇_j = −Σ_{k ≠ j} cot((θ_j − θ_k)/2),

derived from ∂_t P = (ND − D²)P with D = z d/dz. The right way to think of −Λ is geometric:

> **−Λ(P) is the distance from P to the discriminant hypersurface along the canonical heat ray.**

Static moments are coordinates *along* the mimicker fibre; Λ is a coordinate *transverse* to it,
pointing at the boundary. It is not a polynomial statistic of any degree — it is a first-passage
time — and that is exactly why the fibre's freedom does not protect it.

### 4.4 The separation

Two independent computations, one exact and one Monte Carlo, settle the scaling.

**ACUE (exact).** Complete enumeration of all rotation orbits for N = 3, …, 10 — 13,132 orbits,
184,756 configurations at N = 10 — with exact Vandermonde masses, validated to 40 digits.

- P(clock) = 2^{1−N} **exactly**. By Cauchy–Binet, Σ_{|C|=N} |Δ(C)|² = det(AA\*) = (2N)^N for the
  DFT matrix A, while each of the two clock configurations has |Δ|² = N^N. Clock polynomials are
  1 − cz^N, hence flow-invariant, hence have Λ = −∞: they are the exact stationary atoms.
- For every non-clock configuration the minimal gap is exactly π/N (pigeonhole: all gaps ≥ 2π/N
  forces the clock).
- −Λ^ACUE ≍ N^{−2}, with fitted exponent **−2.0009**; N²(−Λ) is supported in ≈[1.31, 1.99]. The
  alternative N^{−8/3} is decisively excluded.
- In all 13,130 non-clock orbits the first collision occurs at a pair that was already adjacent at
  t = 0 — zero exceptions.

**CUE (Monte Carlo, N up to 256).** −Λ^CUE ≍ N^{−8/3}, fitted exponent −2.678 ± 0.016. More than
the exponent, the *law* is parameter-free:

  8N^{8/3}(−Λ) ⟹ G², where P(G > x) = exp(−x³/72π)

is the sine-kernel smallest-gap law. The constant 72π was derived from the kernel, not fitted;
measured 229–236 against 226.2, with KS distances 0.035–0.041 and median 29.6–30.5 against the
prediction (72π ln 2)^{2/3} = 29.08.

The ratio of depths therefore grows like N^{2/3} — the two hypotheses do not merely differ, they
sit in **different universality classes of subcriticality**. The 10× separation point is N\* ≈ 165,
matching an a-priori estimate of ≈160.

The interpretation is the striking part. ACUE's defect is not that it is fragile in some direction;
it is that it is **too robust**. CUE is barely stable under reverse heat flow, in exactly Newman's
sense; ACUE is over-equilibrated, sitting far from the discriminant because its lattice rigidity
forbids the rare very close pairs (δ_min ≍ N^{−4/3}) that CUE produces. A fake RH universe survives
too long under a natural deformation.

### 4.5 What the exponents mean

The numbers 8/3 and 2 are not two readings on a dial; they encode a structural difference, and it is
worth unpacking exactly what.

**Λ measures a distance to a hypersurface.** Let R_N be the set of degree-N polynomials with all
roots on the circle, and D_N = {Disc = 0} the discriminant hypersurface, which is exactly the
boundary of R_N: a configuration leaves the "all roots on the circle" locus precisely by two roots
first colliding. The heat flow gives a canonical vector field on coefficient space. Then

  −Λ(P) = how far one must travel from P, against the heat field, to reach D_N.

So Λ is a *margin*: the distance from a configuration to the failure of its own Riemann-hypothesis
analogue. This is the exact finite-dimensional shadow of the de Bruijn–Newman picture, in which
Λ_dBN ≤ 0 is RH and Λ_dBN = 0 says ξ sits on the boundary.

**Why the exponent is a fingerprint of level repulsion.** For an isolated close pair at angular gap
δ, the two-body reduction of the Coulomb dynamics gives collision time δ²/8 + o(δ²) — a purely
local law we confirmed to 10⁻⁷ in the continuum regime, and exactly at N = 2 where
−Λ = −log cos(δ/2). Hence the depth is governed by the *smallest gap in the configuration*, and the
smallest gap is governed by the level repulsion exponent:

  p(s) ∼ c s^β ⟹ min of ≈N gaps ≍ N^{−1/(β+1)} (normalised) ≍ N^{−1−1/(β+1)} (angular)
       ⟹ −Λ ≍ N^{−2−2/(β+1)}.

Reading the chain for the two cases in question:

- **CUE (β = 2).** Quadratic repulsion still permits rare, anomalously close pairs: the smallest of
  N gaps is of order N^{−4/3}, a full factor N^{−1/3} *below* the mean spacing N^{−1}. One such
  accident is enough, and it produces depth N^{−8/3}.
- **ACUE (β = ∞).** The lattice forbids accidents. Every gap is a multiple of π/N, so the smallest
  gap is *exactly* π/N — deterministically, with no fluctuation at all (we prove this: any
  configuration all of whose gaps exceed 2π/N must be a clock). Depth N^{−2}.

So the ratio −Λ^ACUE / −Λ^CUE ≍ N^{2/3} is precisely the ratio between "the closest pair among N
random ones" and "the closest pair when closeness is quantised". The exponent gap *is* the
extreme-value statistics of the spectrum, converted into a single scalar.

**The interpretive punchline.** One might have expected a fake RH universe to be caught out by
being fragile somewhere. The opposite happens. ACUE's defect is that it is **too stable**: it sits
N^{2/3} times farther from the discriminant than a genuine random-matrix spectrum does. A true
GUE/CUE world is real-rooted but *microscopically fragile* — it is always within N^{−8/3} of losing
the property, because it always contains one near-collision. ACUE is over-equilibrated: it satisfies
its RH-analogue far too robustly, because its rigidity rules out the near-collisions.

This is the finite-N precise form of Newman's dictum. "RH, if true, is only just true" is not a
piece of rhetoric; it is a statement about a scaling exponent, and the alternative hypothesis fails
it by getting the exponent wrong in the direction of excessive safety.

It also reframes what one must prove about ζ. The static programme asks for a correlation statistic
at frequencies beyond the reach of current technique. The dynamic programme asks instead: *is the
zeta zero configuration, locally, as fragile as a random matrix?* Those are different questions, and
§4.10 argues the second may be the easier one — because refuting ACUE needs only that the depth be
**o(N^{−2})**, with any rate whatsoever, not the full N^{−8/3} law.

### 4.6 A universality law

The mechanism suggests, and the data confirm, a general law. If the normalised nearest-neighbour
gap density behaves like p(s) ∼ c s^β as s → 0, then the smallest of ≈N gaps is of order
N^{−1/(β+1)}, the physical gap is N^{−1−1/(β+1)}, and since an isolated pair collides in time
δ²/8 + o(δ²),

> **Dynamic Newman universality.**  −Λ_N ≍ N^{−2−2/(β+1)}.

| ensemble | β | predicted | measured |
|---|---|---|---|
| COE | 1 | −3 | −3.064 (local slopes −3.03 … −3.10) |
| CUE | 2 | −8/3 = −2.667 | −2.678 ± 0.016 (N ≤ 256) |
| CSE | 4 | −12/5 = −2.4 | −2.510 (N ≤ 64, still drifting) |
| ACUE lattice | ∞ | −2 | −2.0009 (exact) |

All measured slopes are slightly steeper than predicted, in the direction and of the size of the
finite-N drift independently calibrated at β = 2, where the larger N range shows the local slope
converging to the prediction from below. The circular β-ensembles were sampled by the Killip–Nenciu
CMV construction, validated against Haar CUE (KS 0.005) and against direct COE = VVᵀ (KS 0.004).
The localisation assumption behind the law — that the first collision is governed by the minimal
initial gap — holds in 95–99% of samples, and in 100% of ACUE configurations.

So the depth is a scalar fingerprint of the microscopic repulsion exponent. That is a clean
random-matrix statement independent of anything about zeta.

### 4.7 A configuration constant, computed two ways

Inside the ACUE law there is a distinguished stratum. Take the alternating clock (the zeros of
z^N + 1), delete the point e^{−iπ/N}, and insert 1; the gap pattern becomes 1, 2, 2, …, 2, 3 in
half-lattice units and the polynomial is exactly

  P_N(z) = (z − 1)(z^N + 1)/(z − e^{−iπ/N}).

Two completely independent routes give the same asymptotic depth.

*Lattice route.* Our exact solver on this configuration, N = 3 … 20, gives N²(−Λ) increasing
monotonically 1.41473945, 1.41821551, …, **1.41963827** at N = 20.

*Continuum route.* Setting t = −s/N², z = e^{iu/N} and passing to the limit yields the local
function

  G_s(u) = 2 cos(u/2) − 2π ∫₀^{1/2} e^{s(1/4 − y²)} cos((π + u)y) dy,

whose first double zero (G = ∂_u G = 0) is at

  **s\* = 1.419640342…, u\* = 1.812942145…,** with G″(u\*) = −0.3767 ≠ 0 (a generic tangency).

The two agree to 2·10⁻⁶ at N = 20, consistent with an O(N⁻²) approach. This is Proposition-grade:
a lattice enumeration and a transcendental double-root equation meeting to six digits.

One correction to the record. It is tempting to read s\* as the limit of the ensemble median,
because for N ≤ 7 the two coincide: the median of N²(−Λ) rises 1.41474, 1.41908, 1.41950. The
complete enumeration shows the median **turns around at N = 7** and falls — 1.41822 (N = 8),
1.41520 (N = 9), 1.41277 (N = 10) — as the support spreads from [1.4147, 1.8246] to
[1.3146, 1.9855]. At small N the single-dislocation orbit dominates the ACUE measure; from N = 8
the ensemble outgrows it. So s\* is a *configuration* constant belonging to the support of the
limit law, not the median's limit. The neighbouring constant for a well-separated defect pair is
N²(−Λ) → 1.46946 (i.e. ρ∞ = 8N²(−Λ)/π² → 1.19120), the other end of the same defect family.

### 4.8 The depth escapes the freezing theorem

The point of the whole exercise. Return to the mimicker families of §4.2 — the 403-dimensional
fibre at N = 8, the centre-of-mass family q_ACUE·g(X), the secant tilts by det(U)^r — every one of
which is frozen to the moment algebra for all time. Λ separates them at O(1):

- an N = 5 mimicker in the ℚ(√5) family moves the clock atom from 0.0625 to 0.1398 and shifts
  E[N²(−Λ) | non-clock] by −0.093;
- at N = 8, mimicker families move the entire Λ-law by total variation 0.12–0.24, with the
  dependence concentrated on the centre-of-mass class X = 0;
- linear-programming tomography over the exact fibre at N = 6 (affine dimension 10 at orbit level)
  gives E[N²(−Λ) | non-clock] ranging over **[1.3610, 1.4770]** against ACUE's 1.4336, while the
  clock atom — the mass at Λ = −∞ — can be pushed from 0 to **0.0975**, i.e. tripled from ACUE's
  0.03125, with every constrained moment held fixed.

The conclusion deserves stating twice.

> **Moment matching does not imply stopping-time matching.** Two ensembles can be indistinguishable
> to a whole algebra of observables, and remain indistinguishable along an entire natural flow, yet
> have first-passage laws in different scaling universality classes.

### 4.9 A classification of counterexamples, and two computable criteria

Not every impostor is caught by the same instrument. The counterexample families that arose in this
project fall into three classes, and — this is the useful part — membership is decidable by two
computations rather than by taste.

**Criterion I (transversality).** Fix a configuration X and a bandwidth r; let M_r(X) = (p₁,…,p_r)
be the moment map and τ = −Λ the depth. The class is caught by ordinary Λ precisely when
ker DM_r ⊄ ker Dτ, i.e. when grad τ has a component off the row space of DM_r. We compute the
relative residual directly.

| configuration | r = 1 | r = 2 | r = 3 | r ≥ N/2 |
|---|---|---|---|---|
| single dislocation, N = 6 | 0.976 | 0.800 | — | rank saturates |
| single dislocation, N = 8 | 0.991 | 0.941 | 0.737 | rank saturates |
| random ACUE lattice, N = 7 | 0.996 | 0.963 | 0.569 | rank saturates |
| generic non-lattice, N = 7 | 0.998 | 0.926 | 0.195 | rank saturates |

Read this correctly. While rank DM_r < N the moment map has a kernel and the question is
meaningful; in that entire regime the answer is decisively yes — 80% to 99% of the depth gradient
lies in directions the first one or two moments cannot see. Once r ≈ N/2 the rank saturates at N,
ker DM_r = 0, and there are no moment-blind directions left to test: the residual drops to 10⁻¹⁶
not because Λ fails but because the question becomes vacuous. So: **moment-null does not imply
depth-null**, quantitatively, for every bandwidth at which the distinction exists.

**Class I — caught by Λ directly.** Anything whose defect changes the geometry of the closest
pair. This includes the collision-stratum families (a configuration sitting on δ = 0 has Λ = 0
outright, the same mechanism by which function-field Newman constants are pinned by double roots),
the half-lattice and PairCeiling adversaries (§4.5: a hard lower spacing δ_min ≳ c/N forces
−Λ ≳ N^{−2}, incompatible with CUE's N^{−8/3}), and the centre-of-mass and secant families of §4.2,
which move the depth law by total variation 0.12–0.24 while every balanced moment stays frozen.

**Class II — invisible to Λ, caught by the marked depth.** Λ is a function of the characteristic
polynomial alone, so it cannot see eigenvectors. Two isospectral matrices have *identically* the
same depth; we verify this to machine zero (τ(G₁) = τ(G₂) = 0.068725421516, difference 8·10⁻¹⁷).
Counterexamples built to match rank, trace and Hilbert–Schmidt norm while differing in a directional
Schur complement live here. The repair is a **marked depth**: deform G ↦ G + η uu\*, transport to
the circle by Cayley, and differentiate,

  χ(G; u) = ∂_η ( −Λ(U_{η,u}) ) |_{η=0}.

It separates the isospectral pair immediately — median |χ(G₁;u) − χ(G₂;u)| = 0.081 over random
marks, against |χ| itself of order 0.01–0.2.

*What drives χ is not what one would guess.* The determinant lemma
det(zI − G − ηuu\*) = det(zI − G)(1 − η·u\*(zI − G)^{−1}u) suggests the marked depth should track
the directional resolvent, and hence blow up wherever the inverse-Gram pathology is worst. It does
not. Rotating the mark onto the smallest-|eigenvalue| direction drives the resolvent
u\*(z₀I − G)^{−1}u from 1.615 to 6.667 = 1/|λ_min| while χ *falls* from 0.0267 to 0.0028 — an order
of magnitude the wrong way. The correct mechanism is local to the collision. Rank-one perturbation
moves λ_j by η|⟨u, v_j⟩|², the Cayley map contributes dθ/dλ = −2/(1 + λ²), and the depth responds
through the critical gap, giving

  **χ(G; u) ≈ ρ · (δ/4) · ( c_a |⟨u, v_a⟩|² − c_b |⟨u, v_b⟩|² ),  c_j = −2/(1 + λ_j²),**

where (a, b) is the pair that collides first, δ their gap, and ρ a background renormalisation of the
same kind as the ACUE constant of §4.7. Measured against random marks the correlation with this
formula is **0.9958** (best-fit ρ = 1.72 in the instance tested, against τ/(δ²/8) = 1.28 for the
value itself — derivative and value renormalise differently). The control confirms the mechanism: a
mark orthogonal to *both* critical eigenvectors gives χ = 2.8·10⁻³, two orders below typical.

So the marked depth is a **differential alignment detector**: it measures how asymmetrically the
mark couples to the two eigenvectors about to collide, and vanishes on marks that couple to them
equally. That is a sharper instrument than a resolvent probe, and it says exactly which marks to
choose when testing a Class II family — those overlapping the critical pair, not those exploring the
ill-conditioned directions.

**Class III — genuinely immune to the linear flow.** Suppose the observable algebra misses a
direction v. Because the heat operator is diagonal in the coefficient basis, H_t v generally stays
in the same hidden sector, so if F(X) = F(X + εv) for all observables F, then F(H_t X) =
F(H_t(X + εv)) for all t as well. **A linear flow does not destroy linear invisibility** — this is
a genuine negative result and it is why "evolve the moments you have" fails, as §4.2 records.

The point is that Λ is not in that argument's scope. It is not a linear observable transported by
the flow; it is the first hitting time of the orbit against the discriminant variety. Two orbits can
live in the same invariant hidden sector and still stand at different distances from
D = {Disc = 0}. Class III is therefore not "counterexamples the depth cannot see" but
"counterexamples for which the *linear* dynamic argument gives nothing" — and Criterion I is what
decides whether the nonlinear stopping time recovers them.

**The programme in one line.** With static observables M and fibre F_m = {X : M(X) = m}, the
statement to prove is that τ restricted to F_m is generically non-constant, with marks added,
Λ_{u₁}, …, Λ_{u_k}, until ⋂_j ker DΛ_{u_j} ∩ ker DM = {0}. Static moments supply coarse
coordinates; marked Newman constants supply the directional ones. The tables above are the first
evidence that this is achievable rather than merely well-posed.

### 4.10 The depth is the Lagarias–Rodgers hard core in another coordinate

The sharpest consequence of the depth law is that it is not a new statistic competing with the
existing formulation of the alternative hypothesis — it is that formulation, in coordinates where
our machinery computes exactly.

Lagarias and Rodgers study the class 𝒯₁ of point processes that mimic the sine process at
coordinatewise bandwidth one — for every r and every Schwartz η with supp η̂ ⊂ [−1,1]^r, the
factorial correlation statistics agree — and define

  μ = sup{ c : some X ∈ 𝒯₁ has minimum spacing ≥ c },  mean spacing normalised to 1.

They prove μ ≥ 1/2 by the randomly shifted half-lattice (which is exactly ACUE), record the
pair-only upper bound μ ≤ 0.606894…, and conjecture μ = 1/2. The alternative hypothesis is
precisely the assertion that zeta's zeros realise a hard core of 1/2.

**The bridge.** On the circle with N points the mean angular spacing is 2π/N, so a hard core of c
mean-spacings is δ_min = 2πc/N. Combined with the local collision law −Λ = ρ·δ_min²/8 this gives

  **N²(−Λ) = ρ · π²c² / 2,  and at the alternative-hypothesis value c = 1/2, N²(−Λ) = ρ · π²/8.**

Here ρ ≥ 1 is the background delay factor of §4.5 and §4.7. Every number we computed is this
identity read in one direction or the other. The ACUE quantiles at N = 3, …, 10 give

| N | min N²(−Λ) | ρ_min | median | ρ_med | max | ρ_max |
|---|---|---|---|---|---|---|
| 6 | 1.353146 | 1.0968 | 1.419374 | 1.15050 | 1.952629 | 1.5827 |
| 8 | 1.330383 | 1.0784 | 1.418216 | 1.14956 | 1.976122 | 1.6018 |
| 10 | 1.314614 | 1.0656 | 1.412774 | 1.14515 | 1.985458 | 1.6094 |

and the single-dislocation constant of §4.7 is exactly the median branch:
s\* = 1.41964034… = ρ_∞ · π²/8 with **ρ_∞ = 1.1507015…**. The minimising family
{0,…,N−3} ∪ {N+3, N+4} — a maximally packed block beside a void — has ρ falling slowly
(1.0656, 1.0611, 1.0579, …, 1.0495 at N = 18) toward a limit near 1.03–1.05; the block is nearly
stationary under the flow, so only its ends move, which is why it resists collapse and keeps ρ > 1.
The maximising symmetric three-block family gives ρ → 1.6094, i.e. N²(−Λ) → 1.9861.

**The equivalence of extremal problems.** Define the depth extremum
μ_Λ = sup{ liminf N²(−Λ) : X ∈ 𝒯₁ }. The identity gives, in both directions,

  **μ_Λ ≥ π²μ²/2  and  μ ≤ √(2μ_Λ)/π.**

These are not loose: LR's published bound μ ≤ 0.606894… is *exactly* the depth bound
μ_Λ ≤ π²(0.606894)²/2 = 1.8177…, and the conjecture μ = 1/2 is exactly μ_Λ = π²/8 · ρ for the
half-lattice's own ρ. So **any improvement of the depth bound is an improvement of the
Lagarias–Rodgers bound**, at the explicit exchange rate above; a depth bound of 1.29 — barely below
what the ACUE configurations themselves realise — would already give μ ≤ 0.511.

**A falsifiable threshold for the alternative hypothesis.** Running the inequality in the direction
that costs nothing:

> **If the zeros of ζ have, in a window at height T with N = (log T)/2π zeros, local Newman depth
> satisfying liminf N²(−Λ) < π²/8 = 1.2337…, then the alternative hypothesis is false.**

This uses only the hard-core consequence of AH — not the lattice structure, not any correlation
beyond it — and it replaces the vague target "beat the bandwidth wall" with one number. Compare the
two sides: AH predicts N²(−Λ) ≥ 1.2337 with the half-lattice's actual typical value 1.41964, while
CUE predicts N²(−Λ) ≍ N^{−2/3} → 0. The gap between prediction and threshold is a factor 1.15, and
between CUE and threshold it is unbounded.

**Why this reformulation may be easier to attack.** The LR extremum is a constraint on a *minimum*,
a hard combinatorial quantity; Palm-type certificates — the row-sum square
Var⁰_sine(S_f) ≤ (M_h − A_f)(A_f − m_h) for band-limited f, and its multiwindow quadratic
generalisation on the packing body K_h — apply naturally to smooth functionals and awkwardly to a
minimum. The depth is smooth in the configuration (§4.9 computes its gradient), it has a variational
characterisation as a distance to a hypersurface, and its derivative has the explicit critical-pair
law of §4.9. Transporting the Palm/packing certificates from the row sum to the depth is therefore
the natural next attempt, and unlike the row-sum searches — which failed for an exact local reason,
the pattern {−h, 0, h} already forcing S₀ = 2f(h) > 9/7 for the first nonnegative Fejér profile —
the depth has no such immediate obstruction.

**One missing lemma.** The bridge is rigorous except for ρ ≥ 1, i.e. that the background never
*accelerates* the first collision below the isolated two-body time δ_min²/8. Every computation in
this project supports it: on the CUE side the correction is positive with median 0.598·N^{−0.729},
on the ACUE side ρ ∈ [1.049, 1.610] over all configurations and sizes tested, and the mechanism is
clear — the neighbours of a close pair pull its members outward. We have not proved it. It is the
single lemma standing between the numerology above and a theorem, and it is exactly the same
localisation estimate that Open Problems 1 and 3 require.

### 4.11 What this could mean for zeta, stated carefully

We claim no theorem about ζ. But the structure suggests a target that is strictly weaker than what
the static programme requires. ACUE predicts N²(−Λ) ≍ 1; CUE predicts N²(−Λ) ≍ N^{−2/3} → 0.
Therefore, to exclude the ACUE universality class for zeta one does not need the full 8/3 law: it
suffices to prove that the local depth of ξ under the true de Bruijn–Newman flow, suitably
normalised at height T, satisfies

  (log T)² · D_T → 0,

with any rate. That is a substantially weaker statement than a full extreme-gap theorem, and
Rodgers–Tao's method — averaged information plus a heat-flow energy argument, rather than the full
GUE law — is evidence that such intermediate statements are reachable. Making the truncation
rigorous (one may not simply cut a window of zeros and call the result a polynomial; the Polymath15
machinery for computing H_t is the honest route) is the first obstacle.

---

## 5. How this was done

The methodology is not incidental, so we describe it plainly.

**Fleets, not oracles.** Work proceeded in rounds. Each round posed one question, and between three
and ten language-model agents attacked it in parallel from deliberately different angles, each
writing and running its own code, each producing a report tagged line by line as *proved*,
*computed*, *heuristic* or *conjecture*. Agents shared a written context file stating the current
state of knowledge, including known errors. They did not share conclusions; convergence of
independent agents was treated as evidence, and divergence as a bug report.

**Adversarial defaults.** Every context file instructed agents that the default assumption is that
the idea has already been tried and failed, and that their first job is to find the reason. The
prompt for the prime-gap round said outright that any improvement to 246 was 99% likely to be a
misread constraint. This is not modesty; it is calibration. Of the phenomena that looked like
discoveries during this project, most were arithmetic or normalisation errors, and the ones that
survived did so because they were attacked first by their own authors.

**Exact arithmetic at every threshold.** Nothing near a decision boundary was accepted in floating
point. The Maynard–Tao certificates are ball-arithmetic with outward rounding; the variational
crossings are exact-rational Rayleigh quotients of rounded eigenvectors; the ACUE enumeration uses
exact Vandermonde masses with 40-digit spot checks; the signed-sieve identity was verified in exact
rationals on a thousand random weights. The single most common failure mode in machine-generated
mathematics is a plausible float, and the remedy is cheap.

**Two implementations or it did not happen.** Every headline number here was produced twice by
independent code, usually by agents that could not see each other's work: the record tuples were
re-verified by a second admissibility checker; the CUE depth was computed by an ODE integrator and
by coefficient bisection agreeing to 10⁻⁶; the single-dislocation constant was obtained from a
lattice enumeration and from a transcendental equation, agreeing to six digits. Where two
implementations disagreed — an engine crossing at k = 15,856 against another at 29,500 — the
discrepancy was tracked to its source before anything was claimed.

**The human supplies the questions.** Every genuinely new direction in this paper came from a human
mathematician's judgement: to stop optimising 246 and look at H₂; to ask whether removing the square
opens a phase; to propose the de Bruijn–Newman depth as a dynamic observable in the first place; to
insist that 72π be factorised rather than fitted; to recognise that the single-dislocation
configuration was the right object to compute exactly. The models supplied speed, breadth, exact
arithmetic, and — importantly — the willingness to write and discard fifty scripts a day. The
division of labour was not "human checks machine" but "human chooses the question, machine
exhausts it, human reads the residue".

**Negative results are the main product.** Five walls, one no-go theorem, one empty phase, one
refuted extrapolation. A method that only reports successes cannot be trusted about them. The most
valuable single output of the signed-sieve round is that it is closed, and that we can say exactly
what would open it.

---

## 6. Open problems

1. **Rigorise the CUE depth law.** Prove 8N^{8/3}(−Λ) ⟹ G². The hard half — the smallest-gap
   limit law — exists in the literature (Ben Arous–Bourgade, Feng–Wei). What is needed is the
   localisation lemma: that the remaining N − 2 zeros perturb the two-body collision time by
   1 + o(1). Our data show the correction is positive and of size ≈0.60·N^{−0.73}.
2. **Make s\* = 1.419640342… a theorem** for the single-dislocation family, and compute the
   separated-defect constant ρ∞ = 1.19120… exactly. The natural framework is an infinite clock with
   one localised defect under the Coulomb dynamics, i.e. a Calogero–Moser problem; the target is a
   closed form in terms of theta or Bessel data.
3. **The marked depth law.** Prove χ(G;u) = ρ·(δ/4)·(c_a|⟨u,v_a⟩|² − c_b|⟨u,v_b⟩|²) with the
   background constant ρ, and determine ρ for the lattice families. Empirically the correlation is
   0.9958 (§4.9); what is missing is the same localisation estimate as in problem 1, differentiated.
4. **A transversality conjecture.** With static observables M and fibre F_m = {X : M(X) = m}, prove
   that τ = −Λ restricted to F_m is generically non-constant; equivalently ker DM ⊄ ker DΛ, with
   marks added until the intersection is trivial.
5. **Function-field depth.** Frobenius conjugacy classes give characteristic polynomials, hence
   depths. Does equidistribution of Frobenius push through to the depth law — a genuinely arithmetic
   Newman-depth universality theorem, rather than a random-matrix analogy? The g = 1 case is the
   exact N = 2 law in arithmetic clothing, Λ = log(|a_p|/2√p).
6. **(E_θ), the tuple-residue well-factorable estimate**, for any θ > 1/2. This is the single
   statement standing between the certified price list of §3.5 and H₁ ≤ 130.
7. **The k = 49 door.** Decide whether some legal Maynard–Tao variant has M₄₉ > 4. Certified
   3.930490592, float optimum 3.959325169, upper bounds closing only ε ≤ 0.00682.

---

## References

J. Maynard, *Small gaps between primes*, Ann. of Math. 181 (2015) 383–413 ·
D.H.J. Polymath, *Variants of the Selberg sieve, and bounded intervals containing many primes*,
Res. Math. Sci. 1:12 (2014) ·
Y. Zhang, *Bounded gaps between primes*, Ann. of Math. 179 (2014) ·
J. Stadlmann, *On primes in arithmetic progressions to smooth moduli*, Adv. Math. (2025) ·
E. Bombieri, J. Friedlander, H. Iwaniec, *Primes in arithmetic progressions to large moduli*,
Acta Math. 156 (1986) ·
J. Maynard, *Primes in arithmetic progressions to large moduli II: well-factorable estimates*,
Mem. AMS 1543 ·
A. Pascadi, arXiv:2505.00653 ·
B. Rodgers, T. Tao, *The de Bruijn–Newman constant is non-negative*, Forum Math. Pi 8 (2020) ·
T. Tao, *The alternative hypothesis for unitary matrices* (blog, 2019) ·
D.H.J. Polymath, *Effective approximation of heat flow evolution of the Riemann ξ function*
(Polymath15) ·
G. Ben Arous, P. Bourgade, *Extreme gaps between eigenvalues of random matrices*, Ann. Probab.
41 (2013) ·
R. Feng, D. Wei, *Small gaps of circular β-ensemble*, Ann. Probab. 49 (2021) ·
R. Killip, I. Nenciu, *Matrix models for circular ensembles*, IMRN (2004) ·
N. Katz, P. Sarnak, *Random matrices, Frobenius eigenvalues, and monodromy*, AMS (1999) ·
T. Engelsma, tables of minimal admissible tuples; A.V. Sutherland, narrow admissible tuples database.

*All engines, certificates, tuples and audit scripts are in the accompanying repository.*
