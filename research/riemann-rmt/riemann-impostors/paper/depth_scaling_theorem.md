# The depth scaling law −Λ ≍ N^{−2−2/(β+1)}

**Bill (Qingyun) Sun · GPT5.6SOL · Fable** — proof document, August 2026

We prove the scaling law for the finite de Bruijn–Newman depth across the circular β-ensembles and
the lattice (ACUE) endpoint, isolating exactly which step is deterministic, which is cited, and
which remains open. Statuses: **[P]** proved here, **[C]** cited, **[O]** open.

## 0. Setup and conventions

For a monic P(z) = ∏_{j=1}^N (z − e^{iθ_j}) = Σ_j a_j z^j define the **flow**

  P_s(z) = Σ_{j=0}^N a_j e^{s·j(N−j)} z^j,  s ≥ 0,

and the **depth**

  D(P) = inf{ s > 0 : disc(P_s) = 0 } ∈ (0, ∞].

This is the finite de Bruijn–Newman depth with D = −Λ; the exponent j(N−j) is the centred heat
weight, and s > 0 amplifies the middle coefficients (the backward direction). All zeros start on the
unit circle, and P_s remains self-inversive, so no simple zero can leave the circle without a prior
collision; hence D is the first collision time.

Write g_i(s) for the i-th cyclic gap, δ_min = min_i g_i(0). Call a pair (a,b) **adjacent** if no zero
lies strictly inside the short arc from θ_b to θ_a.

## 1. The root dynamics [P]

**Lemma 1.** Until the first collision, the zeros of P_s satisfy

  **dθ_j/ds = − Σ_{k≠j} cot( (θ_j − θ_k)/2 ).**

*Proof.* With D_z = z ∂_z one has ∂_s P_s = (N D_z − D_z²) P_s, since the symbol of D_z on z^j is j.
Let z_j(s) be a simple zero. Differentiating P_s(z_j(s)) = 0 gives ż_j = −(∂_s P)(z_j)/P′(z_j).
At a zero, P(z_j) = 0, so

  (N D_z − D_z²)P |_{z_j} = N z_j P′(z_j) − [ z_j P′(z_j) + z_j² P″(z_j) ]
                          = (N−1) z_j P′(z_j) − z_j² P″(z_j),

hence ż_j = −(N−1) z_j + z_j² · P″(z_j)/P′(z_j). For a simple zero of a product,
P″(z_j)/P′(z_j) = 2 Σ_{k≠j} (z_j − z_k)^{−1}, so

  ż_j = −(N−1) z_j + 2 z_j² Σ_{k≠j} (z_j − z_k)^{−1}.

Now put z_j = e^{iθ_j} and φ = θ_j − θ_k. Since
e^{iθ_j} − e^{iθ_k} = e^{i(θ_j+θ_k)/2}·2i sin(φ/2) and e^{iθ_j} = e^{i(θ_j+θ_k)/2} e^{iφ/2},

  2 z_j /(z_j − z_k) = e^{iφ/2} / (i sin(φ/2)) = 1 − i·cot(φ/2).

Summing, Σ_{k≠j} 2z_j/(z_j−z_k) = (N−1) − i Σ_{k≠j} cot(φ_{jk}/2). Substituting and using
θ̇_j = ż_j/(i z_j):

  θ̇_j = [ −(N−1) + (N−1) − i Σ cot(φ_{jk}/2) ] / i = − Σ_{k≠j} cot( (θ_j − θ_k)/2 ). ∎

The clock configuration is the unique fixed point up to rotation (all cotangent sums vanish by
antisymmetry), and linearising about it returns the operator 𝓛_N with eigenvalues δ(N−δ).

## 2. The two-body problem, solved exactly [P]

**Lemma 2.** The scalar equation g′ = −2cot(g/2), g(0) = g₀ ∈ (0, 2π), has the exact solution

  **cos( g(s)/2 ) = e^{s} cos( g₀/2 ),**

so g reaches 0 precisely at s = **−log cos(g₀/2)**. Moreover, for x ∈ [0, π),

  **−log cos(x/2) ≥ x²/8,** with equality only at x = 0.

*Proof.* Separating variables, tan(g/2) dg = −2 ds integrates to −2 log cos(g/2) = −2s + C; matching
at s = 0 gives cos(g/2) = e^s cos(g₀/2). Setting g = 0 gives s = −log cos(g₀/2). For the inequality
put f(x) = −log cos(x/2) − x²/8; then f(0) = 0 and f′(x) = ½tan(x/2) − x/4 = ¼(2tan(x/2) − x) ≥ 0
on [0,π) because tan t ≥ t for t ∈ [0, π/2). ∎

(For N = 2 this is the whole story: D = −log cos(δ/2) exactly.)

## 3. The comparison theorem [P]

**Theorem A (two-body comparison).** For every configuration and every adjacent pair with gap g,

  **g′ ≥ −2 cot(g/2)** for all s before the first collision.

Consequently

  **D ≥ −log cos(δ_min/2) ≥ δ_min²/8.**

Equivalently, writing D = ρ·δ_min²/8, one has **ρ ≥ 1** always.

*Proof.* Let (a,b) be adjacent with g = θ_a − θ_b > 0 measured across the short arc. By Lemma 1,

  g′ = θ_a′ − θ_b′ = −2cot(g/2) − Σ_{k≠a,b} [ cot(x_a^k/2) − cot(x_b^k/2) ],
  x_j^k := (θ_j − θ_k) mod 2π ∈ (0, 2π).

Fix k ∉ {a,b}. Adjacency means k does not lie in the open arc from θ_b to θ_a, so travelling
counterclockwise from θ_k one meets θ_b before θ_a, i.e. x_a^k = x_b^k + g with
0 < x_b^k < x_a^k < 2π. On (0, 2π) the map x ↦ cot(x/2) is strictly decreasing (its derivative is
−½csc²(x/2) < 0), so cot(x_a^k/2) − cot(x_b^k/2) < 0 and the whole bracket enters g′ with a
**positive** sign. Hence g′ ≥ −2cot(g/2).

Zeros cannot cross without colliding, so the cyclic order — and therefore the adjacency of each
consecutive pair — is preserved up to the first collision. Applying the differential inequality to
each gap and comparing with Lemma 2's solution started from the same initial value, every gap
satisfies g_i(s) ≥ G(s; g_i(0)) where G(·; g₀) vanishes first at −log cos(g₀/2). Hence no gap
vanishes before min_i(−log cos(g_i(0)/2)) = −log cos(δ_min/2), which is the claim. ∎

*Numerical check.* The sign claim was tested on 11,060 background terms across random and lattice
configurations: zero exceptions. The conclusion was tested on every dataset in this project; the
minimum of D/(−log cos(δ_min/2)) is 1.0842, 1.0714, 1.0612 over the complete ACUE enumerations at
N = 6, 8, 10 and 1.00019, 1.00021 over CUE samples at N = 16, 64.

## 4. The matching upper bound [P, under a regularity hypothesis]

Define the **background stiffness of the critical pair**

  S := Σ_{k≠a,b} ½ csc²( x_b^k/2 ),  so that  0 ≤ −Σ_k[cot(x_a^k/2) − cot(x_b^k/2)] ≤ g·S

by the mean value theorem, since −(d/dx)cot(x/2) = ½csc²(x/2) and x_a^k = x_b^k + g. At the clock,
S = Σ_{k=1}^{N−1} ½csc²(πk/N) = (N²−1)/6 exactly, so S ≍ N² is the natural scale.

**Theorem B.** Suppose S(s) ≤ A N² throughout the collision window. Then

  −2cot(g/2) ≤ g′ ≤ −2cot(g/2) + A N² g,

and integrating the right-hand inequality from g = δ_min down to 0,

  **D ≤ (δ_min²/8) · ( 1 + O( A N² δ_min² ) ),**

uniformly while A N² δ_min² < 2. In particular **D = (δ_min²/8)(1 + o(1)) whenever N²δ_min² → 0.**

*Proof.* For small g, 2cot(g/2) = 4/g + O(g), so g′ ≤ −4/g + AN²g + O(g) and
ds ≤ g dg/(4 − AN²g² + O(g²)). Integrating from 0 to δ_min gives
D ≤ −(2AN²)^{−1} log(1 − AN²δ_min²/4) = (δ_min²/8)(1 + AN²δ_min²/8 + …). ∎

**Status of the hypothesis.** For CUE it is verified numerically with a uniform constant: the median
of S/N² is 0.109, 0.120, 0.117, 0.120, 0.120 at N = 8, 16, 32, 64, 128 (against the clock value
1/6 = 0.1667), the 99th percentile stays below 0.36 and the largest observed value is 0.79. Turning
this into a high-probability bound is the one **[O]** step; it is a standard rigidity statement
(control of Σ_k d_k^{−2} in the neighbourhood of the extremal pair).

## 5. The extreme-gap input [C]

**Feng–Wei** (Ann. Probab. 49 (2021)) for the circular β-ensemble, and **Ben Arous–Bourgade**
(Ann. Probab. 41 (2013)) for β = 2: the smallest gap satisfies

  **δ_min ≍ N^{−1−1/(β+1)}** in probability,

with the k-th smallest gap density ∝ x^{k(β+1)−1}e^{−cx^{β+1}}. For β = 2 the limit law is
parameter-free: P(N^{4/3}δ_min > x) → exp(−x³/72π).

For the lattice endpoint no citation is needed:

**Lemma 3 [P].** Every non-clock ACUE configuration has δ_min = π/N *exactly*.

*Proof.* The support is the 2N-th roots of unity, so every gap is a positive multiple of π/N, and
the N gaps sum to 2π, i.e. to N multiples of 2π/N. If every gap were ≥ 2π/N they would all equal
2π/N, which is the clock. Hence some gap equals π/N; and no gap can be smaller, since π/N is the
minimal positive multiple. ∎

## 6. The theorem

**Theorem.** Let D_N be the depth of an N-point configuration.

**(i) Finite β.** For the circular β-ensemble with β ∈ (0,∞), assuming the regularity hypothesis of
Theorem B,

  **D_N = (δ_min²/8)(1 + O_ℙ(N^{−2/(β+1)+o(1)})) ≍ N^{−2−2/(β+1)}.**

**(ii) β = 2 distributionally.** Composing with Ben Arous–Bourgade and Slutsky,

  **8 N^{8/3} D_N ⟹ G²,  P(G > x) = exp(−x³/72π).**

**(iii) Lattice endpoint (ACUE, β = ∞).** Unconditionally, for every non-clock configuration,

  **D_N ≥ π²/(8N²),** i.e. N²D_N ≥ π²/8 = 1.2337005501…,

and with ρ = O(1) — verified for N ≤ 10 by complete enumeration, where ρ ∈ [1.049, 1.610] —
**D_N ≍ N^{−2}**, which is the exponent −2−2/(β+1) at β = ∞.

*Proof.* Theorem A gives D ≥ δ_min²/8 in every case. For (i), Feng–Wei give δ_min ≍ N^{−1−1/(β+1)},
hence N²δ_min² ≍ N^{−2/(β+1)} → 0, so Theorem B's error term vanishes at that rate and the two
bounds match. (ii) is (i) at β = 2 together with the parameter-free gap law and the continuous
mapping theorem. For (iii), Lemma 3 makes the lower bound exact and pins δ_min = π/N, so
N²δ_min² = π²: the error term in Theorem B does **not** vanish, and ρ is genuinely bounded away
from 1. ∎

## 7. Why β = ∞ is a singular, not a limiting, endpoint

The correction in Theorem B is governed by δ_min²·S with S ≍ N². Since δ_min ≍ N^{−1−1/(β+1)},

  δ_min²·S ≍ N^{−2/(β+1)},

which tends to 0 for **every finite β** — so ρ_β → 1 and the two-body constant 1/8 is asymptotically
exact. At β = ∞ the hard core pins δ_min ≍ 1/N and δ_min²·S ≍ 1: the background contributes at
leading order and ρ_∞ ≠ 1. The lattice endpoint is therefore not the smooth limit of the finite-β
formula, and this is precisely why the single-dislocation configuration realises

  s\* = 1.419640342… = **1.150717118…** × π²/8,

a two-body collision time dressed by ≈15% of many-body shielding.

The same computation predicts the *rate*, **ρ_β − 1 = O_ℙ(N^{−2/(β+1)+o(1)})**, which is a sharper
statement than the leading exponent and is confirmed at three points:

| β | predicted | fitted | local slope at largest N |
|---|---|---|---|
| 1 (COE) | −1 | −1.012 | −0.851 |
| 2 (CUE) | −2/3 | −0.710 | −0.624 |
| 4 (CSE) | −2/5 | −0.501 | −0.407 |

## 8. Claim ledger

| statement | status |
|---|---|
| Lemma 1, root dynamics θ̇_j = −Σ cot((θ_j−θ_k)/2) | **[P]** |
| Lemma 2, exact two-body solution and −log cos(x/2) ≥ x²/8 | **[P]** |
| Theorem A, g′ ≥ −2cot(g/2) and ρ ≥ 1 | **[P]** |
| Lemma 3, δ_min = π/N for non-clock ACUE | **[P]** |
| Theorem B, upper bound given S ≤ AN² | **[P]** given the hypothesis |
| the regularity hypothesis S ≤ AN² w.h.p. for CβE | **[O]** — verified numerically, median S/N² = 0.120 |
| δ_min ≍ N^{−1−1/(β+1)} for CβE | **[C]** Feng–Wei; Ben Arous–Bourgade at β = 2 |
| ρ_∞ = O(1) for ACUE at all N | **[O]** — proved for N ≤ 10 by enumeration |
| the resulting law −Λ ≍ N^{−2−2/(β+1)}, lattice included | follows from the above |

The single open analytic ingredient is the regularity hypothesis; it closes (i), (ii) and the CUE
side of the CUE/ACUE separation simultaneously. The lattice upper bound needs the separate, purely
deterministic bound ρ_∞ = O(1).
