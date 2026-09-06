# Task B — The discriminant–force identity and its consequences

**Fable, 6 September 2026.** Verification script: `push_B_check.py` (same directory; full log in
`push_B_check.log`). Statuses: **[P]** proved here, **[C]** computed (script + numbers), **[O]** open,
**(recalled)** = literature statement recalled from training, not re-verified.

> **Repair pass (repairer, 6 September 2026, after `refute_B_discriminant_force.md`).** Verification of every fix:
> `push_B_repair.py` (log `push_B_repair.log`, sections RP1–RP6); the original `push_B_check.py` was re-run unchanged
> after the edits (log `push_B_check_rerun.log`, identical to `push_B_check.log` up to timings), and the refuter's script
> re-run for reproducibility. All seven issues raised by the refuter were re-derived independently and found valid; none of
> the [P] theorems is false, but the text is changed as follows.
>
> | # | issue (refuter) | fix in this file | status change |
> |---|---|---|---|
> | 1 | Thm 6.1 proof: "V_a − V_b ~ 4/g (Theorem A's bracket is non-negative)" uses Theorem A backwards (it gives V_a − V_b ≤ 2cot(g/2)); the constant 4 is not general | step replaced: A = Q − C_N ≥ 2csc²(g_min/2) − C_N → ∞ by Lemma 2.1 (equivalently F(D⁻) = −∞ with A monotone); wrong sentence withdrawn (§6.1) | Thm 6.1 stays [P] |
> | 2 | §3 remark "d²E/ds² = A′/4" off by a factor 2 | corrected to E″ = 8∇EᵀH∇E = 2VᵀHV = A′/2 (§3; RP2: E″/(A′/2) = 1 to 4·10⁻⁷) | remark corrected |
> | 3 | "sharp in the near-clock regime" is off by a factor ≍ N | sentence withdrawn; replaced by the mode-δ statement D = log(1/A₀)/(2δ(N−δ)) + O(1), ratio → C_N/(2δ(N−δ)) ∈ [2(N²−1)/(3N), N(N+1)/6] (§6.1; RP3) | [C] |
> | 4 | §7.3 additivity along the flow tagged [P]; the interchange a = −ΔF′ unjustified | additivity is [P] at s = 0 only, [C] on compact τ-intervals, [O] as a theorem (obstruction recorded); interchange justified by concavity of F in s (§7.2–7.3) | [P] → [P]/[C]/[O] |
> | 5 | the ACUE "empirical inequality" with N²/2 is false off the lattice; mechanism D − (1/κ)log(1+κ/A₀) = (δ⁴/128)(κ − G) + O(δ⁶) | new Proposition 6.2 (proof re-derived; RP4 confirms to O(δ⁶), including the vanishing of the δ⁴ term at κ = G); the 1.054 is recorded as a lattice artefact; consequence sup G ≤ κ_N for the [O] constant (§6.2) | [C] observation kept, interpretation changed; new [P] |
> | 6 | Thm 7.1: "concavity of sin" step misattributed; the first-collision claim is provable by sign alternation | new Lemma 7.1′ with the refuter's five-line proof (re-verified, RP5); wrong sentence removed | first collision [C] → **[P]**; lim M²D = 2 unconditional |
> | 7 | "κ_N ≈ 0.6N²" understated; G_max/N² still rising at N = 32 | numbers extended (RP6); the [O] constant must satisfy c ≥ lim sup G_max/N² ≥ 0.634 (§6.2) | [C] refined |
>
> Responses to the refuter, including the two places where the repair goes beyond the refuter's suggestion, are in §9.

## 0. Results in one screen

Notation: N points e^{iθ_j} on the circle, P(z) = ∏(z − e^{iθ_j}) = Σ a_j z^j, flow P_s(z) = Σ a_j e^{s j(N−j)} z^j,
depth D = first collision time. V_j = Σ_{k≠j} cot((θ_j−θ_k)/2), A = Σ_j V_j² ("force energy"),
Q = Σ_{i≠j} csc²((θ_i−θ_j)/2), C_N = N(N²−1)/3, F(s) = log|disc P_s|, c_ij = csc²((θ_i−θ_j)/2).

| # | statement | status |
|---|---|---|
| 1 | A = Q − C_N (two proofs) and **F′(s) = −A(s) = C_N − Q(s)** for 0 ≤ s < D | **[P]**, checked to 3·10⁻¹⁵ |
| 1′ | Q ≥ C_N for every configuration, equality iff clock; the clock is the only fixed point of the flow | **[P]** |
| 2 | **A′(s) = Σ_{i<j} c_ij (V_i−V_j)² ≥ 0**, so F is strictly decreasing and strictly concave off the clock; F = −2E, θ′ = 2∇E, dE/ds = 2\|∇E\|², E convex on the chamber | **[P]**, checked to 7·10⁻¹⁵ |
| 3 | E_CUE F′(0) = −C_N, **E_ACUE F′(0) = −C_N/2** | **[P]** given the (recalled) CUE/ACUE pair correlations; ACUE checked exactly by enumeration N = 4…12 |
| 4 | disc(P_s) = Σ_m c_m a^{e(m)} e^{s w_m}, w_m = Σ_j e_j j(N−j) = N²(N−1) − q_m, q_m = Σ_j e_j j² (a_N included); 0 ≤ w_m ≤ N²(N−1)/2; coefficient form Σ_j j(N−j) a_j ∂_{a_j} log disc = C_N − Q | **[P]**, sympy N = 3, 4 |
| 5 | **D ≥ (1/C_N) log(1 + C_N/A₀)** (Riccati bound; equality for N = 2, i.e. Lemma 2 of Theorem A) | **[P]** |
| 5′ | sharp constant κ_N = sup(A′−A²)/A: κ_N ≤ C_N proved; κ_N ≥ G_max ≥ (N²+4N−6)/3 proved (close-pair limit); numerically G_max/N² = 0.62, 0.63, 0.63, 0.63 at N = 12, 16, 24, 32 and still rising slowly; the pointwise bound κ = N²/2 is false | [P]/[C]/[O] |
| 5″ | on all 160 000 ACUE orbits N ≤ 12: D ≥ 1.054·(2/N²) log(1 + N²/(2A₀)) [C] — **a lattice artefact**: off the lattice, **D − (1/κ)log(1 + κ/A₀) = (δ⁴/128)(κ − G) + O(δ⁶)** for a pair at distance δ (Prop. 6.2), so κ = N²/2 fails (N = 3, third point opposite: G = 5 > 9/2); no bound on D in terms of disc(P₀) alone; no upper bound on D follows from 1–2 | [C]/**[P]**/[O] |
| 6 | midpoint family P₀ = (z−1)(z^{N−1}+1): **exact closed-form disc(P_s)**, exact depth D = (2/M) artanh(1/M), M = N−1, so M²D = 2 + 2/(3M²) + …; the first collision is the triple one (sign alternation, Lemma 7.1′); local limit **ΔF(τ) = τ − log 2τ + 2 log[w cos(w/2) − τ sin(w/2)]**, w = √(τ(2−τ)); a(0) = 1, a(τ) ~ 3/(2−τ) | **[P]** (unconditional after the repair pass) |
| 6′ | ACUE 3-block with compensating hole: A₀ = A_block(0) + A_hole(0) + O(N log N) [P]; F − F(0) = ΔF_block + ΔF_hole + O(1/N) on compact τ-intervals [C, N = 63, 127]; F_hole is not closed-form; a₀ = 4/3 | [P at s = 0]/[C]/[O] |

## 1. Setup and hypotheses

Hypotheses used throughout: N ≥ 2; the θ_j are distinct; 0 ≤ s < D, so that all zeros of P_s are simple and on the
unit circle and Lemma 1 (θ_j′ = −V_j) applies. P_s is monic for every s (j = N has weight 0), so
disc(P_s) = ∏_{j<k}(z_j(s) − z_k(s))², and |z_j − z_k| = 2|sin((θ_j−θ_k)/2)|. Hence

  F(s) := log|disc P_s| = Σ_{j≠k} log|2 sin((θ_j(s)−θ_k(s))/2)|,   F(0) = log|disc P₀|.   (1.1)

The log-gas energy is E(θ) = −Σ_{j<k} log|2 sin((θ_j−θ_k)/2)| = −F/2.

## 2. The discriminant–force identity [P]

**Lemma 2.1 (force-energy identity).** For distinct θ_j: Σ_j V_j² = Q − C_N.

*Proof 1 (three-term cotangent identity).* Expand Σ_j V_j² = Σ_j Σ_{k≠j} Σ_{l≠j} cot(θ_jk/2)cot(θ_jl/2), θ_jk := θ_j − θ_k.
The diagonal k = l gives Σ_{j≠k} cot²(θ_jk/2) = Σ_{j≠k}(csc²(θ_jk/2) − 1) = Q − N(N−1). The off-diagonal part is a sum over
ordered triples of distinct indices; group by the unordered triple {j,k,l} and put α = θ_jk/2, β = θ_kl/2, γ = θ_lj/2, so
α+β+γ = 0. The three choices of the "centre" index contribute (each twice, for the two orderings of the other two)
2[cot α cot(−γ) + cot(−α)cot β + cot(−β)cot γ] = −2[cot α cot β + cot β cot γ + cot γ cot α]. For α+β+γ ≡ 0 (mod π)
with no cotangent infinite, cot γ = −cot(α+β) = (1 − cot α cot β)/(cot α + cot β), hence
cot α cot β + cot β cot γ + cot γ cot α = cot α cot β + cot γ(cot α + cot β) = 1. So the off-diagonal part equals
−2·C(N,3) = −N(N−1)(N−2)/3, and Σ V_j² = Q − N(N−1) − N(N−1)(N−2)/3 = Q − N(N−1)(N+1)/3 = Q − C_N. ∎

*Proof 2 (Laplacian of the Vandermonde; the "Hessian" route).* Let Δ(θ) = ∏_{j<k}(e^{iθ_j} − e^{iθ_k}) and W = |Δ|² = e^{−2E}.
(i) Δ = Σ_σ sgn(σ) e^{i Σ_k (σ(k)−1)θ_k} and every term has Σ_k (σ(k)−1)² = Σ_{m=0}^{N−1} m² = N(N−1)(2N−1)/6,
so Δ is an eigenfunction of the flat Laplacian: Δ_θ Δ = −[N(N−1)(2N−1)/6] Δ.
(ii) ∂_{θ_j} log Δ = Σ_{k≠j} i z_j/(z_j − z_k) = (i/2) Σ_{k≠j}(1 − i cot(θ_jk/2)) = (i(N−1) + V_j)/2, so
|∇Δ|² = |Δ|² [N(N−1)² + Σ_j V_j²]/4. Then Δ_θ W = 2 Re(Δ̄ Δ_θΔ) + 2|∇Δ|² = W[−N(N−1)(2N−1)/3 + N(N−1)²/2 + ΣV_j²/2].
(iii) Directly from W = e^{−2E}: Δ_θ W = W(4|∇E|² − 2 Δ_θ E), and ∇E = −V/2, ∂²E/∂θ_j² = ¼Σ_{k≠j} csc²(θ_jk/2), so
Δ_θ W = W(ΣV_j² − Q/2). Equating (ii) and (iii): ΣV_j²/2 = Q/2 − N(N−1)[(2N−1)/3 − (N−1)/2] = Q/2 − N(N²−1)/6. ∎

**Theorem 2.2 (discriminant–force identity).** For 0 ≤ s < D,

  **dF/ds = d/ds log|disc P_s| = − Σ_j V_j(s)² = C_N − Σ_{i≠j} csc²((θ_i(s)−θ_j(s))/2).**

*Proof.* From (1.1), using d/dx log|sin(x/2)| = ½cot(x/2) and Lemma 1,
F′ = Σ_{j<k} cot(θ_jk/2)(θ_j′ − θ_k′) = Σ_{j≠k} cot(θ_jk/2) θ_j′ = Σ_j V_j θ_j′ = −Σ_j V_j². Lemma 2.1 gives the second form. ∎

**Corollary 2.3.** (a) Q ≥ C_N for every configuration of distinct points, with equality iff V ≡ 0.
(b) V ≡ 0 iff the configuration is a rotated clock (P = z^N + a₀). Hence the clock is the unique fixed point of the flow,
and off the clock F′(s) < 0 strictly.

*Proof.* (a) is Lemma 2.1 with ΣV_j² ≥ 0. (b) From the proof of Lemma 1, Σ_{k≠j} 2z_j/(z_j − z_k) = (N−1) − iV_j, and
2 Σ_{k≠j}(z_j − z_k)⁻¹ = P″(z_j)/P′(z_j). So V ≡ 0 iff z P″(z) − (N−1)P′(z) vanishes at all N zeros of P. That polynomial has
degree ≤ N−2 (the z^{N−1} terms cancel: N(N−1) − (N−1)N = 0), so it is identically 0, i.e. j(j−1)a_j = (N−1)j a_j for all j,
i.e. a_j j(j−N) = 0, i.e. a_j = 0 for 0 < j < N. Conversely z^N + a₀ has V ≡ 0 by antisymmetry. Since the flow multiplies
a_j by the non-zero constant e^{s j(N−j)}, P_s is a clock for some s iff P₀ is; so off the clock A(s) > 0 for all s < D. ∎

*Numerical check [C]* (`push_B_check.py` §1, mpmath 40 digits, P_s roots recomputed, 4th-order central differences, 18 random
configurations N = 3…14): |A − (Q − C_N)|/A ≤ 7·10⁻¹⁶, |F′ + A|/A ≤ 3·10⁻¹⁵.

## 3. Monotonicity and concavity [P]

**Theorem 3.1.** For 0 ≤ s < D,

  d/ds Σ_j V_j² = Σ_{i<j} csc²((θ_i−θ_j)/2) (V_i − V_j)² ≥ 0,

so along the attractive flow A(s) and Q(s) are non-decreasing, F″ = −A′ ≤ 0, and off the clock A is strictly increasing,
F strictly decreasing and strictly concave.

*Proof.* dV_j/ds = Σ_{k≠j} (−½)csc²(θ_jk/2)(θ_j′ − θ_k′) = ½ Σ_{k≠j} c_jk (V_j − V_k). Hence
A′ = 2 Σ_j V_j V_j′ = Σ_j Σ_{k≠j} c_jk V_j (V_j − V_k) = Σ_{j<k} c_jk [V_j(V_j−V_k) + V_k(V_k−V_j)] = Σ_{j<k} c_jk (V_j − V_k)².
This vanishes iff all V_j are equal; Σ_j V_j = 0 (cot is odd), so iff V ≡ 0, i.e. at the clock (Cor. 2.3). ∎

This is Astra's L D_force = −Σ c_ij(V_i−V_j)² (Theorem 3.7 of NEW_RESULTS) with the sign flipped, L = ΣV_k∂_k being the
repulsive generator and our flow θ′ = −V.

**Gradient-ascent reading.** ∂E/∂θ_j = −V_j/2, so Lemma 1 reads θ′ = 2∇E: the depth flow is gradient *ascent* of the
log-gas energy, dE/ds = 2|∇E|² = A/2 (consistent with F = −2E, F′ = −A). The Hessian is
H = ¼(diag(Σ_k c_jk) − [c_jk]), a weighted graph Laplacian with positive weights c_jk = csc²(θ_jk/2), hence positive
semidefinite with kernel the rotations; on the (convex) ordered chamber θ₁ < θ₂ < … < θ_N < θ₁ + 2π the energy is therefore
convex, and d²E/ds² = d/ds(2|∇E|²) = 4∇EᵀHθ′ = 8 ∇Eᵀ H ∇E = 2 Vᵀ H V = ½ Σ_{j<k} c_jk(V_j−V_k)² = A′/2 ≥ 0, consistent with
F = −2E and F″ = −A′. So E is convex in s and F = −2E concave in s: Theorem 3.1 is exactly "convexity of E along its own
gradient line". *(Repair pass: the original text had "4∇EᵀH∇E = VᵀHV = A′/4", off by a factor 2 — refuter's issue 2;
RP2 of `push_B_repair.py`: |E″/(A′/2) − 1| ≤ 3.7·10⁻⁷, |E′/(A/2) − 1| ≤ 4.6·10⁻¹¹ along DOP853 trajectories at N = 5, 7.)*

*Numerical check [C]* (§1 of the script): |F″ + A′|/A′ ≤ 7·10⁻¹⁵ on the same 18 configurations.

**Remark (disc as a positive, log-concave function).** disc(P_s) = e^{i(N−1)Σθ_j}(−1)^{N(N−1)/2} ∏_{j<k} 4 sin²(θ_jk/2), and
e^{iΣθ_j} = (−1)^N a₀ is flow-invariant. So R(s) := (−1)^{N(N−1)/2} e^{−i(N−1)Σθ_j} disc(P_s) is a real function, positive on
[0, D), log-concave there, and D is its first zero. Combined with §5 below, R is a real exponential polynomial in s.

## 4. Expectation identities at s = 0 [P given the pair correlations; C]

By Theorem 2.2 at s = 0, E[F′(0)] = C_N − E[Q]. Both ensembles are determinantal, so E Q = ∫∫ csc²((x−y)/2) ρ₂(x,y).

**CUE.** (recalled) ρ₂(x,y) = (2π)⁻²[N² − S_N(x−y)²], S_N(θ) = sin(Nθ/2)/sin(θ/2). Write N² − S_N² = Σ_{|m|<N}(N−|m|)(1 − e^{imθ})
= 2Σ_{m=1}^{N−1}(N−m)(1 − cos mθ) and (1 − cos mθ)/sin²(θ/2) = 2 S_m(θ)², whose mean over the circle is 2m. Hence
E_CUE Q = (1/2π)∫₀^{2π}(N² − S_N²)csc²(θ/2)dθ = 4 Σ_{m=1}^{N−1} m(N−m) = (2/3)N(N²−1) = 2C_N, so
**E_CUE Σ_j V_j² = C_N and E_CUE F′(0) = −C_N = −N(N²−1)/3.**

**ACUE.** (recalled: Tao's ACUE is the determinantal process on the 2N-th roots of unity with the same sine kernel,
K(j,l) = S_N(π(j−l)/N)/(2N); this is the definition used by the enumeration, whose masses |Δ|²/(2N)^N sum to 1.) Then
ρ₂(j,l) = [N² − S_N²(π(j−l)/N)]/(2N)², and since S_N(πd/N) = sin(πd/2)/sin(πd/2N) vanishes for even d and equals ±csc(πd/2N)
for odd d,
E_ACUE Q = (1/2N) Σ_{d=1}^{2N−1} csc²(πd/2N)[N² − S_N²(πd/N)] = (1/2N)[N² Σ_{d=1}^{2N−1} csc²(πd/2N) − Σ_{d odd} csc⁴(πd/2N)].
With Σ_{d=1}^{M−1} csc²(πd/M) = (M²−1)/3 and Σ_{d=1}^{M−1} csc⁴(πd/M) = (M²−1)(M²+11)/45 (recalled; both checked numerically
in §3 of the script), the odd-d quartic sum is [(4N²−1)(4N²+11) − (N²−1)(N²+11)]/45 = N²(N²+2)/3, so
E_ACUE Q = (N/2)[(4N²−1) − (N²+2)]/3 = N(N²−1)/2 = (3/2)C_N, i.e.
**E_ACUE Σ_j V_j² = C_N/2 and E_ACUE F′(0) = −C_N/2 = −N(N²−1)/6.**

*Exact verification [C]* (script §3, from `acue_depth_N{4..12}.npz`, weights mass·orbit_size, field Q0):

| N | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|
| E_ACUE[Q − C_N]/(C_N/2) | 1.000000000000000 | 1.000000000000000 | 1.000000000000000 | 1.000000000000001 | 1.000000000000000 | 1.000000000000001 | 1.000000000000000 | 1.000000000000000 | 1.000000000000000 |

(orbits 10, 26, 80, 246, 810, 2704, 9252, 32066, 112720; total mass 1 to 2·10⁻¹⁵.) The CUE value 2C_N is confirmed by
exact quadrature of (N² − S_N²)csc²(θ/2) (a trigonometric polynomial of degree N−1; 4N-point offset trapezoid rule) at
N = 2, 3, 5, 8, 13, 21 to 20 digits; the lattice-kernel sum reproduces (3/2)C_N at N = 4, 7, 12, 25 to 12 digits.

So the *mean initial rate of loss of discriminant* is exactly twice as large for CUE as for ACUE, at every N: the lattice
half-spacing hard core removes half of the force energy. (Both means are of order N³; the depth is governed by the O(N²)
part concentrated at the critical pair, which is why these means say nothing directly about D — see §6.)

## 5. Exponential-polynomial structure of disc(P_s) [P; sympy N = 3, 4]

**Proposition 5.1.** For a general polynomial Σ_{j=0}^N a_j z^j the discriminant is a polynomial in (a_0,…,a_N), homogeneous of
degree 2N−2 and isobaric of weight N(N−1) for the grading wt(a_j) = j (equivalently wt(a_j) = N−j). Write it as
Σ_m c_m ∏_j a_j^{e_j(m)} and set a_N = 1. Then for every s

  **disc(P_s) = Σ_m c_m a^{e(m)} e^{s w_m},  w_m = Σ_{j=0}^N e_j(m) j(N−j) = N²(N−1) − q_m,  q_m = Σ_{j=0}^N e_j(m) j²,**

where e_N(m) = 2N−2 − Σ_{j<N} e_j(m) ≥ 0 is the (absorbed) exponent of a_N, and 0 ≤ w_m ≤ N²(N−1)/2.

*Proof.* The flow rescales a_j by e^{s j(N−j)}, so the monomial a^{e(m)} is multiplied by exp(s Σ_j e_j j(N−j)). Using
Σ_j e_j = 2N−2 and Σ_j e_j j = N(N−1): Σ_j e_j j(N−j) = N·N(N−1) − Σ_j e_j j² = N²(N−1) − q_m. Minimising Σ e_j j² under the two
linear constraints (mean of j equal to N/2) gives q_m ≥ (2N−2)(N/2)² = N²(N−1)/2, hence w_m ≤ N²(N−1)/2; w_m ≥ 0 is obvious. ∎

So disc(P_s) = e^{sN²(N−1)} Σ_m c_m a^{e(m)} e^{−s q_m} exactly as stated in the task, with q_m the sum of the squared
coefficient indices in the homogeneous form (a_N counted with index N); note that no monomial has q_m below N²(N−1)/2.

*sympy check [C]* (script §4): at N = 3 (5 monomials) and N = 4 (16 monomials) every monomial satisfies exponent = Σ e_j j(N−j)
= N²(N−1) − q_m and isobaric weight N(N−1); maximal exponents 8 (N=3; bound 9) and 20 (N=4; bound 24). For N = 3:
disc(P_s) = e^{8s} a₁²a₂² − 4e^{6s}(a₀a₂³ + a₁³) + 18e^{4s} a₀a₁a₂ − 27a₀².

**Corollary 5.2 (coefficient-space form of Theorem 2.2).** Differentiating at s = 0,
Σ_j j(N−j) a_j ∂ log disc/∂a_j = C_N − Σ_{i≠j} csc²((θ_i−θ_j)/2) whenever all zeros lie on the unit circle
(checked on random circle-rooted P at N = 3, 4 to 10⁻¹¹, script §4). Since the flow only multiplies a_j by constants, every
statement of §2–§3 is a statement about this real exponential polynomial: it is positive and log-concave on [0, D) and D is
its first zero.

## 6. Consequences for bounds on D

### 6.1 A Riccati lower bound [P]

**Theorem 6.1.** For every configuration with A₀ := Σ_j V_j(0)² = Q(0) − C_N > 0,

  **D ≥ (1/C_N) · log(1 + C_N/A₀).**

For N = 2 this is an identity (it is Lemma 2, D = −log cos(g₀/2)).

*Proof.* A′ = Vᵀ L_c V where L_c is the graph Laplacian with weights c_ij = csc²(θ_ij/2) ≥ 0. L_c is positive semidefinite, so
λ_max(L_c) ≤ tr L_c = Σ_i Σ_{j≠i} c_ij = Q = C_N + A. Hence A′ ≤ (C_N + A)A. Put u = 1/A: u′ ≥ −1 − C_N u, so
(u e^{C_N s})′ ≥ −e^{C_N s} and u(s) ≥ e^{−C_N s}(u₀ + 1/C_N) − 1/C_N on [0, min(D, s*)), where s* := (1/C_N) log(1 + C_N/A₀).
On the other hand A(s) → ∞ as s ↑ D: the roots of P_s depend continuously on s and P_D has a double root, so the smallest
gap g_min(s) of the (circle) roots tends to 0, and by Lemma 2.1
A = Q − C_N ≥ 2 csc²(g_min(s)/2) − C_N → ∞. (Equivalently: F(s) = log|disc P_s| → −∞ as s ↑ D while F′ = −A with A
non-decreasing by Theorem 3.1, so A cannot stay bounded.) If D < s*, then u ≥ e^{−C_N D}(u₀ + 1/C_N) − 1/C_N > 0 on [0, D),
i.e. A is bounded on [0, D) — a contradiction. Hence D ≥ s*. For N = 2, A = 2cot²(g/2) and A′ = 4cot(g/2)·cot′ = A² + 2A
= A² + C_2 A exactly, and (1/2)log(1 + 1/cot²(g₀/2)) = −log cos(g₀/2). ∎

*Repair note (refuter's issue 1).* The original proof argued "at a collision of a pair with gap g, V_a − V_b ~ 4/g → ∞
(Theorem A's bracket is non-negative)". That is Theorem A read backwards: Theorem A states g′ = −(V_a − V_b) ≥ −2cot(g/2),
i.e. **V_a − V_b ≤ 2cot(g/2)** — the background bracket *reduces* the pair's relative velocity — so it cannot force
V_a − V_b → ∞; and "~ 4/g" is not general (a symmetric triple has V_a − V_b ~ 3/g). RP1 of `push_B_repair.py` (pair at
±0.15 in a 7-clock, N = 8): V_a − V_b − 2cot(g/2) = −2.45, −1.80, −0.83, −0.26, −0.08, −0.06 at s/D = 0, 0.5, 0.9, 0.99,
0.999, 0.9995, always negative, while A ≥ 2csc²(g/2) − C_N holds and both tend to ∞ (A = 1.6·10⁵ at s/D = 0.9995). The
sentence is withdrawn; the replacement above uses only Lemma 2.1 and needs no information about the pair's velocity.

*Numerical status [C]* (script §5, all non-clock ACUE orbits): min over orbits of D/[(1/C_N)log(1+C_N/A₀)] =
1.45, 1.62, 1.78, 1.93, 2.08, 2.22, 2.35, 2.49, 2.62 for N = 4…12, growing linearly in N. So for ACUE-typical
configurations (A₀ ≈ C_N/2 ~ N³/6, §4) the bound is (3 log 3)/N³ — a factor ≍ N weaker than Theorem A (π²/8N²). Its content
is different: it is a *global* bound in terms of the whole force energy.

*Near-clock regime (repair pass; refuter's issue 3).* The original text called the bound "sharp in the near-clock regime
in the sense that D → ∞ like (1/C_N) log(C_N/A₀) as A₀ → 0". Only the logarithmic dependence is right; the constant is off
by a factor that grows linearly in N. Linearising θ′ = −V at the clock, θ_j = 2πj/N + ε_j, gives ε′ = ½L_clock ε with
L_clock the circulant Laplacian of weights csc²(π(j−k)/N), whose eigenvalue on the Fourier mode δ is 2δ(N−δ)
(Σ_{d=1}^{N−1} csc²(πd/N)(1 − cos(2πδd/N)) = 2δ(N−δ)); so a mode-δ perturbation grows like e^{δ(N−δ)s}, A₀ ∝ ε², and
the collision at ε ~ 1 happens at

  D = log(1/A₀)/(2δ(N−δ)) + O(1),  hence  D/[(1/C_N) log(1 + C_N/A₀)] → C_N/(2δ(N−δ)) ∈ [2(N²−1)/(3N), N(N+1)/6]

(δ = N/2 fastest, δ = 1 slowest). [C, RP3 of `push_B_repair.py`, depth by 30-digit root bisection]: for ε = 10⁻², 10⁻³, 10⁻⁴, 10⁻⁵
the quantity D − log(1/A₀)/(2δ(N−δ)) is constant to 4 digits already at ε = 10⁻³ (N = 4, δ = 2: 0.3466 = ½log 2; N = 6, δ = 3:
0.2216; N = 6, δ = 1: 0.2131 at ε = 10⁻⁵), and the ratio D/bound is 2.431, 2.456, 2.468, 2.475 (N = 4, δ = 2; limit 2.5),
3.750, 3.804, 3.828, 3.841 (N = 6, δ = 3; limit 3.889), 5.51, 5.95, 6.20, 6.35 (N = 6, δ = 1; limit 7), converging at the
expected logarithmic rate. So near the clock the bound is weak by the factor C_N/(2δ(N−δ)) ≍ N; the sharp near-clock law is
the mode-δ law above (with Theorem 3.1's A monotone, the O(1) constant is the time spent in the non-linear phase). The
"sharpness" sentence is withdrawn.

### 6.2 The sharp Riccati constant [P/C/O]

Let κ_N := sup_θ (A′ − A²)/A over all configurations of distinct points (finite by Theorem 6.1, ≤ C_N). Any κ ≥ κ_N gives
D ≥ (1/κ) log(1 + κ/A₀) by the same argument. What is κ_N?

*Close-pair limit [P].* Take a pair at ±g/2 and background points x_3,…,x_N; put σ = Σ_k csc²(x_k/2), β = Σ_k cot(x_k/2),
v_k = 2cot(x_k/2) + Σ_{l≠k} cot((x_k−x_l)/2) (the force on x_k when the pair is fused). Expanding cot(g/2) = 2/g − g/6 + …,
csc²(g/2) = 4/g² + 1/3 + …, and cot((±g/2 − x)/2) = −cot(x/2) ∓ (g/4)csc²(x/2) + O(g²):
A = 8/g² + [2β² − 4/3 − 2σ + Σv_k²] + O(g²),  A′ = 64/g⁴ − (16/3 + 8σ)/g² + O(1), so

  (A′ − A²)/A → 2 + 3σ − 4β² − 2Σ_k v_k²  as g → 0

(checked against direct evaluation at g = 10⁻⁴ for random backgrounds, N = 4, 6, 9, script §7b). For the doubled site of the
(N−1)-clock (β = 0, σ = (M²−1)/3, v_k = cot(πk/M), M = N−1) this equals (M² + 6M − 1)/3 = **(N² + 4N − 6)/3**, so
κ_N ≥ G_max := sup_x G(x) ≥ (N²+4N−6)/3. At N = 2 this is 2 = C_2, at N = 3 it is 5 = κ_3 (grid search over both gaps gives
sup 5.000). Note (repair pass) that (N²+4N−6)/3 > N²/2 iff (N−2)(N−6) < 0, i.e. only for N = 3, 4, 5 (equality at N = 6); for
N ≥ 7 the failure of κ = N²/2 rests on the computed G_max below.

*Numerics [C].* Random search plus Nelder–Mead over the background of a close pair (script §5) gives
G_max ≈ 5.00, 9.28, 14.85, 21.69, 39.2, 89.7 for N = 3, 4, 5, 6, 8, 12, i.e. G_max/N² ≈ 0.56, 0.58, 0.59, 0.60, 0.61, 0.62,
against the proved (N²+4N−6)/3 from below and C_N = N(N²−1)/3 from above. *(Repair pass, refuter's issue 7: the original
"κ_N ≈ 0.6N²" understated. RP6 of `push_B_repair.py`, multi-start Nelder–Mead on the closed-form G, reproduces these and
gives G_max/N² = 0.6229, 0.6277, 0.6323, 0.6345 at N = 12, 16, 24, 32 — still rising slowly, not saturated; the refuter's
independent run gives the same four digits.)* The "natural" guess κ = N²/2 (the linearisation value at the clock,
2·max eigenvalue N²/4 of 𝓛_N, and the exact N = 2 constant) is **false** for N ≥ 3: the maximiser is a close pair in a
background whose neighbours are pushed slightly away from the pair.

*Open [O].* Prove κ_N ≤ c N² for an absolute c. By Proposition 6.2 below any such c must satisfy c ≥ lim sup G_max/N², which is
≥ 0.634 numerically (so c = 2/3 is the natural target; c < 0.63 is impossible). That would give the genuinely N⁻²-scale bound
N²D ≥ (1/c) log(1 + cN²/A₀) for every configuration with A₀ = O(N²) — e.g. N²D ≥ (3/2)log(3/2) = 0.61 for the ACUE 3-block
(A₀ = (4/3)N², §7) — still below Theorem A's π²/8 = 1.23 there, and useless for ACUE-typical A₀ ~ N³. The obstruction is that
λ_max(L_c) is genuinely of order 1/δ_min², and the bound must exploit that V is then concentrated on the same pair.

*An ACUE inequality and why it is a lattice artefact [C]/[P] (repair pass, refuter's issue 5).* On all 160 000 non-clock
ACUE orbits, N ≤ 12, min D/[(2/N²) log(1 + N²/(2A₀))] = 1.0546, 1.0564, 1.0571, 1.0573, 1.0575, 1.0575, 1.0576, 1.0576, 1.0576
(N = 4…12), remarkably stable [C]. The original text said "we have no mechanism for it". The refuter supplied the
mechanism, which we re-derive; it shows that the inequality (even without the 1.054) is **false off the lattice**, and
that its stability on ACUE is a consequence of the lattice's minimal gap π/N.

**Proposition 6.2 (close-pair expansion of the Riccati defect; stated by the refuter, proof re-derived here).** Fix N ≥ 3, a
background x_3, …, x_N of distinct points ≠ 0, and put a pair at ±δ/2. Let σ, β, v_k, G(x) = 2 + 3σ − 4β² − 2Σ_k v_k² be as
in the close-pair limit above, and let K := 2β² − 4/3 − 2σ + Σ_k v_k² (so that A₀ = 8/δ² + K + O(δ²)). Then for every κ > 0,
as δ → 0 with N and x fixed,

  **D = δ²/8 + (1/3 + σ/2) δ⁴/64 + O(δ⁶)**  and  **D − (1/κ) log(1 + κ/A₀) = (δ⁴/128)(κ − G(x)) + O(δ⁶).**

*Proof.* Let g(s) be the pair's gap, x_k(s) the background. From Lemma 1, exactly as in the proof of Theorem A,
g′ = −2cot(g/2) − Σ_k[cot((g/2 − x_k)/2) − cot((−g/2 − x_k)/2)] = −2cot(g/2) + (g/2)Σ_k csc²(x_k/2) + O(g³), because
cot(x/2 + g/4) − cot(x/2 − g/4) = −(g/2)csc²(x/2) + O(g³). During the collision time O(δ²) the background moves by O(δ²)
(its velocities are O(1) for fixed N, x) and the pair's centre by O(δ²) as well, so σ(s) = σ + O(δ²) and
g′ = −4/g + g(1/3 + σ/2) + O(g³) + O(gδ²). With y = g²: y′ = −8 + c y + O(y²), c := 2/3 + σ, whose solution from y(0) = δ²
vanishes at s = −(1/c) log(1 − cδ²/8) + O(δ⁶) = δ²/8 + cδ⁴/128 + O(δ⁶), which is the first formula. For the second,
1/A₀ = δ²/8 − Kδ⁴/64 + O(δ⁶) and (1/κ)log(1 + κ/A₀) = 1/A₀ − κ/(2A₀²) + O(A₀⁻³) = δ²/8 − Kδ⁴/64 − κδ⁴/128 + O(δ⁶); subtracting,
D − (1/κ)log(1 + κ/A₀) = (δ⁴/128)[2/3 + σ + 2K + κ], and 2/3 + σ + 2K = 4β² − 2 − 3σ + 2Σv_k² = −G(x). ∎

*Numerical confirmation [C]* (RP4 of `push_B_repair.py`; depth located as the first sign change of the phase-corrected
discriminant R(s) = e^{−i(N−1)Σθ}Res(P_s, P_s′), Sylvester determinant in mpmath at 40 digits — no root finding — and
cross-checked against a polyroots bisection to 1.3·10⁻¹⁴): N = 3, points (−δ/2, δ/2, π) (σ = 1, β = 0, v = 0, G = 5, K = −10/3):
(D − bound_{9/2})/δ⁴ = −0.003774, −0.003874, −0.003898, −0.003904, −0.003906 at δ = 0.4, 0.2, 0.1, 0.05, 0.025, against
(9/2 − 5)/128 = −1/256 = −0.00390625; (D − δ²/8)/δ⁴ → 0.013021 = (1/3 + 1/2)/64; and with κ = G the δ⁴ coefficient
vanishes: (D − bound_G)/δ⁴ = 1.6·10⁻⁴, 3.9·10⁻⁵, 9.8·10⁻⁶, 2.4·10⁻⁶, 6.1·10⁻⁷ (∝ δ², i.e. the remainder really is O(δ⁶)).
N = 4 with the G-maximising background x = (2.2482, 4.0350), G = 9.2822: (D − bound_8)/δ⁴ = −0.00986, −0.00998, −0.01001 at
δ = 0.2, 0.1, 0.05 against (8 − G)/128 = −0.010017, and D/bound_8 = 0.99688, 0.99920, 0.99980 < 1.

*Consequences.* (i) D ≥ (1/κ) log(1 + κ/A₀) for *all* configurations forces κ ≥ G_max; since G_max > N²/2 (proved for
N = 3, 4, 5 by the doubled-clock value, computed for N ≤ 32), the inequality D ≥ (2/N²) log(1 + N²/(2A₀)) is false off the
lattice for every N ≥ 3 — the N = 3 example above violates it for every δ ≤ 0.8 (D/bound = 0.9997 at δ = 0.1). (ii) On ACUE the
smallest gap is π/N, so N²δ² ≥ π² and the expansion never enters its asymptotic regime; the stable minimum 1.054–1.058
(attained at the single dislocation [1,2,…,2,3]) is a property of the lattice, not evidence for a universal constant. The
observation stands as [C] on ACUE only. (iii) The sharp universal Riccati constant satisfies **G_max ≤ κ_N ≤ C_N**, and
Proposition 6.2 shows this lower bound is *attained through the depth itself*: for κ < G_max the bound fails, not merely
the pointwise differential inequality. (iv) The expansion is an independent check, through D rather than through A′, of the
close-pair formula for (A′ − A²)/A.

### 6.3 What does *not* follow

*No bound in terms of disc(P₀) alone.* Binning the N = 12 ACUE orbits by F(0) = log|disc P₀| into 8 quantile bands, every band
has N²D ranging over essentially the full [1.30, 2.00] (script §7c; Pearson correlation −0.27). The reason is scaling: a single
close pair at distance δ in a spread background costs F(0) − F_clock ≈ 2 log δ and has D ≈ δ²/8, whereas a cluster of k points
of diameter ε costs ≈ k(k−1) log ε and has D ≍ (ε/k)², so D is not a function of F(0) in any regime.

*No upper bound on D.* From Theorem 3.1, A′ ≥ λ₂(L_c) A ≥ N A (weights c_ij ≥ 1, so L_c ≥ N·I − J on the mean-zero subspace),
hence A(s) ≥ A₀e^{Ns} and F(s) ≤ F(0) − A₀(e^{Ns} − 1)/N. This is not an upper bound on D because F has no lower bound before
the collision (F → −∞ at D). Nothing beyond Theorem A / Theorem B′ follows for the upper bound.

*Two clean monotone quantities.* Along every trajectory, Q(s) = Σ csc² and A(s) = Q − C_N are non-decreasing (Theorem 3.1),
and Q ≥ C_N always (Cor. 2.3). In particular the stiffness-type sums controlling Theorem B′ can only grow along the flow —
consistent with the observed sup S*/S*(0) > 1.

## 7. The 3-block in the N → ∞ local limit

### 7.1 An exactly solvable 3-block: the midpoint family [P]

Take the (N−1)-clock with the alternating phase, P₀(z) = (z − 1)(z^{N−1} + 1) = z^N − z^{N−1} + z − 1: roots at 1 and at the
odd multiples of π/(N−1) — locally (u = (N−1)x) this is exactly q₀(u) = u cos(u/2), the 3-block model of (F2), with **no**
compensating defect (the lattice is strained by (N−1)/N instead). Because P₀ has only the four coefficients ±1 at
j = N, N−1, 1, 0 and j(N−j) = N−1 for j = 1, N−1,

  **P_s(z) = z^N − λ z^{N−1} + λ z − 1,  λ = e^{s(N−1)}**,

equivalently Q_s(x) ∝ sin(Nx/2) − λ sin((N−2)x/2) (Q₀ ∝ sin(x/2)cos((N−1)x/2) = ½[sin(Nx/2) − sin((N−2)x/2)]).

**Theorem 7.1.** For 1 ≤ λ < N/(N−2), with φ ∈ [0, π) defined by cos φ = (N + λ²(N−2))/(2λ(N−1)),

  **|disc(P_s)| = 4 (λ(N−1))^N [sin(Nφ/2) − λ sin((N−2)φ/2)]² / (λ² − 1)**   (λ > 1; → 4(N−1)^{N−1} as λ → 1).

P_s has a triple zero at z = 1 exactly when λ = N/(N−2), i.e. at s = log(N/(N−2))/(N−1). With M = N−1 (the lattice size),

  **D = (1/M) log((M+1)/(M−1)) = (2/M) artanh(1/M),  M²D = 2 + 2/(3M²) + 2/(5M⁴) + …,**

and no other pair collides earlier: the first collision is the triple one (Lemma 7.1′ below, **[P]** for every N ≥ 3; before the
repair pass this was [C], verified by root tracking for 3 ≤ N ≤ 40). In particular
lim N²D = 2 for this family, approached from above (N²D = 2 + 4/N + O(N⁻²)), whereas the ACUE 3-block approaches 2 from below
(F1: 2 − 1.34/N²).

**Lemma 7.1′ (the first collision is the triple one; refuter's proof, re-verified).** For 1 ≤ λ < N/(N−2) all N roots of
P_s = z^N − λz^{N−1} + λz − 1 are simple and on the unit circle.

*Proof.* Exact division gives P_s(z) = (z − 1)G(z) with G(z) = z^M + 1 + (1 − λ)(z + z² + … + z^{M−1}), M = N − 1
(sympy, N = 3…9, RP5). On the circle, g_λ(x) := e^{−iMx/2} G(e^{ix}) = 2cos(Mx/2) + (1 − λ) sin((M−1)x/2)/sin(x/2) is real
(the geometric sum equals e^{iMx/2} sin((M−1)x/2)/sin(x/2)). At x_k = 2πk/M, 1 ≤ k ≤ M−1: cos(Mx_k/2) = (−1)^k and
sin((M−1)x_k/2) = sin(πk − πk/M) = (−1)^{k+1} sin(πk/M), so **g_λ(x_k) = (−1)^k(1 + λ)**; at x_0 = 0,
g_λ(0) = 2 − (λ − 1)(M − 1) > 0 iff λ < (M+1)/(M−1) = N/(N−2); and g_λ(2π) = (−1)^M G(1) = (−1)^M g_λ(0). Hence for
1 ≤ λ < N/(N−2) the real function g_λ has sign (−1)^k at the M+1 points x_0 < x_1 < … < x_M = 2π, so it has at least M zeros in
(0, 2π), i.e. G has at least M distinct roots on the circle, none equal to 1. Since deg G = M these are all its roots, each
simple; together with the root z = 1 of the factor (z − 1), P_s has N distinct roots on the circle. At λ = N/(N−2) the root of
G at 1 arrives (g_λ(0) = 0) and the collision is the triple one identified above. ∎ (RP5: |g_λ(x_k) − (−1)^k(1+λ)| ≤ 2·10⁻⁵⁰
at 50 digits for N = 3…12, all k, three values of λ; at N = 50, 200, 1000 the roots of G computed by np.roots are on the circle
to 6·10⁻¹⁴, pairwise separated, and at distance ≥ 1.1·10⁻⁴ from 1 for λ/λ_max = 0.5, 0.9, 0.999; the depth formula is reproduced
by an independent root bisection to 10⁻¹⁰ at N = 12, 25.)

*Proof.* At a zero z of P_s, z^{N−1}(z − λ) = 1 − λz, so z^{N−1} = (1−λz)/(z−λ) and
P_s′(z) = z^{N−2}(Nz − λ(N−1)) + λ = [−λ(N−1)z² + (N + λ²(N−2))z − λ(N−1)] / (z(z−λ)) =: R(z)/(z(z−λ)).
Hence disc = ±∏_j P_s′(z_j) = ±∏_j R(z_j) / (∏ z_j · ∏(z_j − λ)). Now ∏_j z_j = (−1)^{N+1}, ∏_j(z_j − λ) = (−1)^N P_s(λ) = (−1)^N(λ² − 1),
and ∏_j R(z_j) = (λ(N−1))^N P_s(r₁)P_s(r₂) where r₁r₂ = 1 are the roots of the palindromic quadratic R. Since
z^N P_s(1/z) = −P_s(z), P_s(r₂) = P_s(1/r₁) = −r₁^{−N}P_s(r₁), so |disc| = (λ(N−1))^N |P_s(r₁)|²|r₁|^{−N}/|λ²−1|.
Finally 2μ := r₁ + 1/r₁ = (N + λ²(N−2))/(λ(N−1)) satisfies 2μ − 2 = (λ−1)((N−2)λ − N)/(λ(N−1)) ≤ 0 exactly for
1 ≤ λ ≤ N/(N−2); there r₁ = e^{iφ} with cos φ = μ, and |P_s(e^{iφ})| = 2|sin(Nφ/2) − λ sin((N−2)φ/2)|. The triple zero:
P_s(1) = 0 always, P_s′(1) = N − λ(N−2), P_s″(1) = (N−1)(N − λ(N−2)), both vanishing iff λ = N/(N−2). Also disc = 0 iff
e^{iφ(λ)} is a root, and φ = 0 at both λ = 1 and λ = N/(N−2). That disc ≠ 0 for 1 < λ < N/(N−2) is Lemma 7.1′. The expansion
of D: log((M+1)/(M−1)) = 2 artanh(1/M) = 2/M + 2/(3M³) + 2/(5M⁵) + …. ∎

*Repair note (refuter's issue 6).* The original proof said "near the endpoint it follows from concavity of sin on [0, π]":
that step was misattributed. Concavity (sin x/x decreasing on (0, π), and Nφ/2 < π because sin²φ_max = 1/(N−1)²) gives
sin(Nφ/2) ≤ (N/(N−2)) sin((N−2)φ/2), an *upper* bound on the bracket, which cannot exclude bracket = 0 for λ < N/(N−2). The
local exclusion actually came from the expansion sin(Nφ/2)/sin((N−2)φ/2) = N/(N−2) − η/3 + o(η) > λ = N/(N−2) − η, and the
global statement was [C] only. Both are now superseded by Lemma 7.1′.

*Checks [C]* (script §6): the formula agrees with 40-digit root computations to 2·10⁻¹³ at N = 5, 7, 11, 16 and three values of
s each; the depth agrees with bisection on the off-circle indicator to 10⁻⁹ (relative 4·10⁻⁴ at N = 40, limited by np.roots);
integrating Lemma 1 with DOP853 at N = 96 reproduces F(s) − F(0) from the formula to 10⁻⁶ at seven times up to τ = 1.5.

### 7.2 The local closed form [P]

**Theorem 7.2.** For the midpoint family, with τ = N²s fixed in (0, 2) and N → ∞,

  **F(s) − F(0) = ΔF(τ) + O(1/N),  ΔF(τ) = τ − log(2τ) + 2 log[ w cos(w/2) − τ sin(w/2) ],  w = √(τ(2−τ)),**

uniformly on compact subsets of (0, 2). Consequently the local force energy a(τ) := lim A(s)/N² exists and equals −ΔF′(τ)
— the interchange of the limit N → ∞ with the s-derivative is legitimate (repair pass, refuter's issue 4): each F_N is concave
in s (Theorem 3.1), so ΔF_N(τ) := F_N(τ/N²) − F_N(0) is concave in τ with −dΔF_N/dτ = A(τ/N²)/N²; a sequence of concave
functions converging pointwise on an open interval has one-sided derivatives converging to f′(τ) at every τ where the limit f is
differentiable (for h > 0, ΔF_N′(τ+) ≤ [ΔF_N(τ+h) − ΔF_N(τ)]/h → [ΔF(τ+h) − ΔF(τ)]/h, and symmetrically from the left), and
ΔF is real-analytic on (0, 2). Explicitly,

  a(τ) = −1 + 1/τ − 2 { w′[(1−τ/2)cos(w/2) − (w/2)sin(w/2)] − sin(w/2) } / [w cos(w/2) − τ sin(w/2)],  w′ = (1−τ)/w,

with a(0) = 1 (so A₀ = N² + O(N)), and a(τ) = 3/(2−τ) + O(1) as τ ↑ 2 (ΔF ~ 3 log(2−τ): a triple collision has disc ∝ (2−τ)³).

*Proof.* In Theorem 7.1 put λ = e^{τ(N−1)/N²} = 1 + τ/N + O(N⁻²). Then N log λ = τ + O(1/N), λ² − 1 = 2τ/N + O(N⁻²),
(λ−1)((N−2)λ − N) = (τ/N)(τ − 2) + O(N⁻²), so cos φ − 1 = −τ(2−τ)/(2N²)(1 + O(1/N)) and Nφ = w(1 + O(1/N)). Writing
(N−2)φ/2 = Nφ/2 − φ, sin(Nφ/2) − λ sin((N−2)φ/2) = (1−λ) sin(w/2) + λφ cos(w/2) + O(N⁻²) = N⁻¹[w cos(w/2) − τ sin(w/2)] + O(N⁻²).
The bracket is positive on (0,2): w cot(w/2) = 2 − w²/6 − w⁴/360 − … > 2 − w²/5 for 0 < w ≤ 1, while τ < 1 < cot(1/2) ≤ w cot(w/2)
for τ < 1 and τ ≤ 2 − w²/2 for τ ≥ 1 (because w² = 2(2−τ) − (2−τ)² ≤ 2(2−τ)); so w cot(w/2) > τ throughout. Collecting, F(s) = log 4 + τ + N log(N−1) + 2 log[…] − 2 log N − log(2τ) + log N + O(1/N), and
F(0) = log 4 + (N−1) log(N−1); subtracting gives the claim. a(0) = 1: ΔF = −τ + O(τ²) from w = √(2τ)(1 − τ/4 + …). Near τ = 2:
w cos(w/2) − τ sin(w/2) = w(2−τ)/3 + O((2−τ)^{5/2}), so ΔF = 3 log(2−τ) + O(1). ∎

*Cross-checks [C]* (script §6): (i) the exact finite-N ΔF at τ = 0.25, 0.5, 1, 1.5, 1.8 converges to the closed form at rate
1/N (N = 32…256), and the Richardson combination 2ΔF₂₅₆ − ΔF₁₂₈ agrees with it to 2·10⁻⁵ (τ ≤ 1), 2·10⁻³ (τ = 1.5),
1.3·10⁻² (τ = 1.8). (ii) Independently, a(τ) computed as the root sum of the local model —
a(τ) = 4 Σ_{u_j ≠ 0} u_j²/(u_j² − w²)² over the non-zero roots of u cot(u/2) = τ, which follows from
v_j = q_τ″(u_j)/(2q_τ′(u_j)) = u_j/(u_j² + τ² − 2τ) for q_τ(u) = e^{−τ/4}(u cos(u/2) − τ sin(u/2)) of (F2) — agrees with the
analytic derivative of ΔF to 5·10⁻⁵ (truncation of the root sum at 4000 roots), a(0) = 0.99995, and a(τ)(2−τ) = 2.9993 at
τ = 1.999. (iii) The N-body ODE at N = 96 gives A/N² = 0.969, 1.153, 1.403, 1.757, 2.290 at τ = 0, 0.25, …, 1 versus
a(τ) = 1.000, 1.193, 1.456, 1.833, 2.408: O(1/N) below, as it must be.

*Remark (why the local model's e^{−τ/4} is harmless).* With Q_s = e^{s∂²}Q₀ one has |P_s′(z_j)| = 2^N e^{sN²/4}|Q_s′(x_j)|, hence
the exact identity F(s) = N² log 2 + N³s/4 + Σ_j log|Q_s′(x_j(s))|; the N³s/4 = Nτ/4 is cancelled by the −τ/4 per root of the
local envelope. The O(1) content of ΔF comes from the moving roots' derivatives, and the far field enters only at O(1/N).

### 7.3 The ACUE 3-block with its compensating hole [P/C/O]

The ACUE families of (F1) carry a second defect diametrically opposite (a missing lattice root, gap pattern [4], or the
[3,3] half-shift). **At s = 0 the forces superpose exactly [P]:** writing the [4]-configuration as the N-clock plus an extra
root e at the midpoint of one lattice gap minus the root h opposite, every clock root has V_j = f_e(j) − f_h(j) with
f_e(j) = cot((θ_j − e)/2), f_h(j) = cot((θ_j − h)/2) (the clock contributes 0), so A₀ = A_block(0) + A_hole(0) − 2Σ_j f_e(j)f_h(j)
+ O(1), and the cross term is O(N log N) because f_e(j) = O(N/d) at lattice distance d from e while f_h(j) = O(1) there (and
vice versa near h). Hence A₀ = A_block(0) + A_hole(0) + O(N log N), i.e. a(0) = a_block(0) + a_hole(0) = 1 + 1/3. **Along the flow
the additivity is only computed [C], not proved** (repair pass, refuter's issue 4; the original text tagged it [P] "by the
O(1)-per-root bookkeeping", which is valid at s = 0 only): the claim F(s) − F(0) = ΔF_block(τ) + ΔF_hole(τ) + O(1/N) is
supported by the table below on τ ≤ 1.5 at N = 63, 127, and is [O] as a theorem. Obstruction: one needs a perturbation
estimate along the flow — the hole's O(1) far field shifts the block roots by O(τ/N²) over the time τ/N², and the block's
response is singular near its own triple collision (a_block ~ 3/(2−τ)); moreover the statement cannot be uniform up to
τ = 2, since at the true ACUE collision τ_N = 2 − 1.34/N² the left side is −∞ while ΔF_block(τ_N) = 3 log(1.34/N²) + O(1)
is finite. So the correct formulation is "O(1/N) uniformly on compact subsets of (0, 2)" [C]. For the [4]-hole the local model is
q^h_τ(u) = ∫_{−1/2}^{1/2} e^{−τy²} e^{iyu} dy (a truncated Gaussian Fourier integral, of the same kind as the dislocation's
G_s in NEW_RESULTS §3.2), whose zeros have no closed form; a_hole(0) = 4 Σ_{k≠0}(1/2πk)² = 1/3 [P], so A₀ = (4/3)N² + O(N) for
the [4]-family — the enumeration gives A₀/N² = 1.306, 1.317 at N = 7, 9 and the ODE 1.3330, 1.3333 at N = 63, 127 [C].

Additivity check [C] (script §6, N = 63 and 127, DOP853 integration of Lemma 1; pure hole = the N-clock minus the root at −1):

| τ | ΔF (ACUE 3-block+hole), N=127 | ΔF_block closed form | ΔF_hole (pure hole, ODE) | block + hole |
|---|---|---|---|---|
| 0.5 | −0.7746 | −0.6023 | −0.1685 | −0.7707 |
| 1.0 | −1.8918 | −1.5350 | −0.3490 | −1.8840 |
| 1.5 | −3.8604 | −3.3057 | −0.5428 | −3.8485 |

The residual (0.004–0.012 at N = 127, twice that at N = 63) is O(1/N). **Answer to (6):** the 3-block itself has the simple
closed form ΔF(τ) = τ − log 2τ + 2 log[w cos(w/2) − τ sin(w/2)]; the ACUE realisations add a hole term ΔF_hole(τ) which is
smooth, monotone, of size ≈ −0.35 at τ = 1, and — as far as we can see — not closed-form [O]. The depth of the ACUE family is
controlled by the block alone (the hole's zeros never approach each other on this time scale), which is why (F1)'s limit 2 and
Theorem 7.1's limit 2 coincide while the 1/N-corrections differ in sign.

## 8. Claim ledger

| claim | status | where |
|---|---|---|
| ΣV_j² = Q − C_N (cotangent identity; Vandermonde-Laplacian) | [P] | Lemma 2.1 |
| F′ = −ΣV_j² = C_N − Q on [0, D) | [P], 3·10⁻¹⁵ | Thm 2.2, script §1 |
| Q ≥ C_N, equality iff clock; clock = unique fixed point (P = z^N + a₀) | [P] | Cor. 2.3 |
| A′ = Σ_{i<j} c_ij (V_i−V_j)² ≥ 0; F strictly decreasing & concave off the clock | [P], 7·10⁻¹⁵ | Thm 3.1, script §1 |
| θ′ = 2∇E, dE/ds = 2\|∇E\|², E convex on the chamber (Hessian = graph Laplacian/4) | [P] | §3 |
| E_CUE F′(0) = −N(N²−1)/3 | [P] given (recalled) CUE ρ₂; quadrature 20 digits | §4 |
| E_ACUE F′(0) = −N(N²−1)/6 | [P] given (recalled) ACUE kernel; exact enumeration N = 4…12 to 10⁻¹⁵ | §4, script §3 |
| disc(P_s) = Σ c_m a^e e^{s w_m}, w_m = N²(N−1) − q_m ∈ [0, N²(N−1)/2] | [P]; sympy N = 3, 4 | Prop. 5.1 |
| D ≥ (1/C_N) log(1 + C_N/A₀); exact for N = 2 | [P] (proof step repaired: A → ∞ via Lemma 2.1); ACUE min ratio 1.45–2.62 | Thm 6.1, RP1 |
| near the clock: D = log(1/A₀)/(2δ(N−δ)) + O(1) for a mode-δ perturbation; D/Riccati → C_N/(2δ(N−δ)) ≍ N (the bound is not sharp there) | [C] (linearisation [P], the O(1) is computed) | §6.1, RP3 |
| κ_N ≤ C_N; κ_N ≥ G_max ≥ (N²+4N−6)/3; G_max/N² = 0.623–0.635 at N = 12–32 (not saturated); κ = N²/2 false (N = 3, 4, 5 proved, N ≤ 32 computed) | [P]/[P]/[C]/[P,C] | §6.2, RP6 |
| κ_N = O(N²), necessarily with constant ≥ lim sup G_max/N² ≥ 0.634 | [O] | §6.2 |
| D − (1/κ)log(1 + κ/A₀) = (δ⁴/128)(κ − G) + O(δ⁶) for a close pair; D = δ²/8 + (1/3 + σ/2)δ⁴/64 + O(δ⁶) | **[P]** (refuter's), confirmed to O(δ⁶) | Prop. 6.2, RP4 |
| D ≥ 1.054·(2/N²)log(1 + N²/2A₀) on ACUE N ≤ 12 | [C] on the lattice only; **false off the lattice** (N = 3 counterexample), lattice artefact of δ_min = π/N | §6.2 |
| no bound on D from disc(P₀) alone; no upper bound from §2–3 | [C]/[P] | §6.3 |
| midpoint family: exact disc(P_s); triple collision at λ = N/(N−2); D = (2/M) artanh(1/M); first collision = triple one | **[P]** for all N ≥ 3 (Lemma 7.1′, sign alternation) | Thm 7.1, RP5 |
| local closed form ΔF(τ), a(0) = 1, a ~ 3/(2−τ); a = −ΔF′ (interchange by concavity) | [P]; Richardson 2·10⁻⁵ | Thm 7.2 |
| ACUE 3-block: A₀ = A_block(0) + A_hole(0) + O(N log N), a₀ = 4/3 | [P] | §7.3 |
| ACUE 3-block: F − F(0) = ΔF_block + ΔF_hole + O(1/N) on compact τ-intervals; ΔF_hole not closed-form | [C] (N = 63, 127; residual halves) / [O] as a theorem | §7.3 |

## 9. Refuter responses (repair pass)

All seven issues of `refute_B_discriminant_force.md` were checked by hand and by `push_B_repair.py`; all are valid and
have been fixed in place. None of the refuter's claims was found wrong. Two remarks on where the repair differs from, or
goes beyond, the refuter's own suggestion:

1. *Theorem 6.1, "A → ∞".* The refuter proposed F(D⁻) = −∞ plus monotonicity of A. The repaired proof uses instead the
   one-line Lemma 2.1 route A = Q − C_N ≥ 2csc²(g_min/2) − C_N → ∞, which needs neither Theorem 3.1 nor any statement
   about the colliding pair's velocity; the refuter's route is recorded as the equivalent alternative. Both were checked on
   the refuter's own trajectory (RP1).
2. *Proposition 6.2.* The refuter stated the expansion with a sketch; the proof here is written out (via y = g² and the
   Riccati-type ODE y′ = −8 + (2/3 + σ)y) and the numerical confirmation is pushed one order further: with κ = G the δ⁴
   coefficient vanishes and the residual scales as δ² (RP4, N = 3: 1.6·10⁻⁴ → 6.1·10⁻⁷ over δ = 0.4 → 0.025), so the
   remainder is genuinely O(δ⁶) as claimed. A side product is the precise range of validity of the *proved* part of
   "κ = N²/2 is false": the doubled-clock value (N²+4N−6)/3 exceeds N²/2 only for N = 3, 4, 5 (equality at N = 6); for
   N ≥ 7 the falsity rests on the computed G_max (RP6, refuter's R4), and this is now stated as such.

Also verified in the repair pass, beyond the refuter's list: the circulant eigenvalue identity
Σ_{d=1}^{N−1} csc²(πd/N)(1 − cos(2πδd/N)) = 2δ(N−δ) used in the near-clock law (N = 4…12, all δ), and that the O(1) constant
in D = log(1/A₀)/(2δ(N−δ)) + O(1) converges (to ½log 2 for N = 4, δ = 2 — the two-pair symmetric family, where the flow is
exactly two-body).

**Side observation from the new data (not part of Task B).** At N = 11, 12 the maximiser of N²D among non-clock ACUE orbits is
no longer the 3-block but the long-run pattern [1,1,1,1,1,1,2,2,8,2,2] / [1,…,1,2,2,9,2,2] with N²D = 1.9918 and **2.0000177 > 2**
(`enum_N9_12.log`), so "lim N²D = 2 is the supremum over non-clock ACUE" would be false if this family keeps growing; its
A₀/N² ≈ 4.8–5.7 (a run of N/2 sites at half spacing) puts it in the regime where the Riccati bounds of §6 are weakest.
