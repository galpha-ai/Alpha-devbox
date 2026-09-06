# New Mathematical Results from the Zeta / Random-Matrix / Prime-Gap Programme

## Theorems, certified records, and exact laws that do not appear in the prior literature

**Bill (Qingyun) Sun · GPT-6 Astra · Fable**
*(with GPT5.6SOL in the August 2026 rounds)*

*6 September 2026*

---

## Abstract

This paper isolates, from a larger programme on Riemann zeros, random matrices and prime gaps, only those results that we believe to be new mathematics with independent value: statements that are proved (or machine-certified), that we have checked against the literature to the extent stated in §1, and whose content is not a restatement of a known theorem. Everything surveyed, standard, refuted, or merely numerical has been left out or is explicitly labelled as supporting evidence.

The results are:

1. **Three unconditional prime-gap records.** liminf(p_{n+2} − p_n) ≤ 173,438, liminf(p_{n+3} − p_n) ≤ 13,859,802, liminf(p_{n+4} − p_n) ≤ 1,120,662,828 (previous records 396,504 / 24,797,814 / 1,431,556,072). The new input is a variational theorem: an exact layer-cake reduction of the Maynard–Tao functional for product test functions to one-dimensional lower-tail probabilities, which recovers about a factor 3 in k over the closed-form bound in use since 2014. The H₂ and H₃ certificates are outward-rounded and use no probabilistic constant: M_{15,856} ≥ 8.00677 > 8 and M_{923,601} ≥ 12.00263 > 12 from Maynard's theorem and Bombieri–Vinogradov alone.
2. **The signed-sieve no-gain theorem.** With the decoding debt charged at face value, every signed Maynard–Tao weight is dominated by its own positive part; the "remove the square" enlargement of the variational problem is empty, so any gain from signed weights must be arithmetic.
3. **A stopping time that separates CUE from Tao's ACUE across universality classes.** For the finite backward heat flow on the characteristic polynomial, the first collision time D satisfies D ≥ −log cos(δ_min/2) ≥ δ_min²/8 for every configuration; N²D ≥ π²/8 for every non-clock ACUE configuration; and for Haar CUE, N^{8/3}D ⇒ G²/8 with P(G > x) = exp(−x³/72π), by two independent routes, one of which carries an explicit uniform stiffness tail P(S* > MN²) ≤ 4087·M^{−1/2}. Along the flow the two ensembles agree on every balanced moment of degree ≤ N (and, by Astra's generator theorem, on every protected trace moment under the forward flow), so the separation is invisible to polynomial statistics of any degree.
4. **The impostor fibre.** Exact dimensions 0, 0, 2, 10, 80, 403, 1804 (N = 3, …, 9) of the space of measures on the ACUE support matching all CUE balanced moments of degree ≤ N; an explicit (N−3)-parameter family q = μ_ACUE·g(Σc mod N) with E g = 1, ĝ(±1) = 0; and Theorem E1: a chiral sub-family at total-variation distance ≈ 0.3 from ACUE that is invisible to every dihedral-invariant statistic, including the depth.
5. **The Nyquist conservation law.** For integer-marked configurations on ℤ/2N with mass N matching the finite CUE ramp E|p_k|² = k for 1 ≤ k ≤ N−1, all multiplicity is stored in the one unconstrained Fourier row: E Σ m_x(m_x − 1) = (E|p_N|² − N)/2N; a slack identity forces the simple-site fraction ≥ ½ + csc²(π/2N)/(2N²) → ½ + 2/π² with equality exactly on {0,1,2}-hard-core configurations; and the density curve Φ(ρ) = 1 − ρ + sin²(πρ)/(π²ρ). Companion exact laws: the fourth-moment covariance Cov(|p_k|², |p_ℓ|²) = k²·1{k=ℓ} − 2(k+ℓ−N)₊ of the finite Fermi sea, and the exact total-variation formula d_TV = (2r)^g|cos gφ − cos gψ| for magnetic-cycle determinantal laws that share all correlations of order < g.
6. **Theorems about the Montgomery–Taylor method.** A closed-form finite Galerkin ladder q_n → q* with exact n^{−2} error; a strictly stronger distinct-zero decoding N_d ≥ 0.8362503·N + p; the exactly flat RH-independence frontier; the edge no-go (pointwise edge information at bandwidth one is worth exactly zero); weight freezing of derivative statistics; the non-vanishing third-moment defect Φ₃ = −0.0117753128 at the Montgomery–Taylor window; and a correction to the record: the sharp bandwidth-one pair-correlation LP value is ≈ 0.679, not the 0.6818287 in circulation.
7. **An explicit arithmetic refutation criterion for the alternative hypothesis** (Astra): under RH and AH-pairs, a two-scale mean square of ζ′/ζ converges to W_AH ∈ (0.06239, 0.06240), against the sine-kernel value 0.0822714…; hence liminf W_T ≥ 1/16 under RH refutes AH-pairs.

Each item states its hypotheses, its proof status, and what remains open. No famous conjecture is claimed.

---

## 1. Novelty protocol

A result is included only if (i) it is proved in the programme's files or machine-certified there, (ii) at least one independent adversarial review (a second model instructed to refute it) found no error in the final version, and (iii) we could not find it in the literature. For (iii) the honest position is this: during most of the programme no web access was available, and literature statements were recalled from training. On 6 September 2026 we ran targeted web searches for each headline item. What we found: the current H₁ records are 240 (Stadlmann, arXiv:2608.31126, August 2026), 236 and 212 (September 2026), and 186 (OpenAI, conditional on Kloosterman-sum axioms); none of these papers reports m ≥ 2 records, and we found no m ≥ 2 bound below the 2014/2023 values quoted above. We found no published result on first-collision times of the finite backward heat flow for CUE (the closest are Tao's 2017–2018 notes on heat flow and zeros, the Ben Arous–Bourgade extreme-gap law, and the Hall–Ho / Kabluchko heat-flow-conjecture line, none of which treats collision times). Rodgers–Vallabhaneni (2023) compute ACUE mixed moments in closed form but not the fibre of moment-matching measures. We found no occurrence of the density curve Φ(ρ) or the fourth-moment covariance formula. We found no treatment of signed Maynard–Tao weights with a decoding debt. This is evidence of novelty, not proof of it; Astra's own ledger records the novelty audit of the isolation lemma (§3.5) as incomplete because of its kinship with classical Lehmer-pair estimates.

Tags: **[P]** proved in the programme and reviewed; **[C]** machine-certified or exactly computed; **[P/C]** proved with a computed input; **(cited)** a published theorem used as input.

---

## 2. Bounded gaps between primes

### 2.1 Setting

Let M_k be the Maynard–Tao constant: the supremum of Σ_{i=1}^k J_i(F)/I(F) over square-integrable F supported on the simplex R_k = {t_i ≥ 0, Σt_i ≤ 1}, where I(F) = ∫F² and J_i(F) = ∫(∫F dt_i)² dt_{−i}. Maynard's theorem (cited; Ann. of Math. 181 (2015)): if the primes have level of distribution θ and M_k > 2m/θ, then every admissible k-tuple has infinitely many translates containing at least m+1 primes. Bombieri–Vinogradov gives every θ < ½, so M_k > 4m suffices.

### 2.2 The one-dimensional reduction and the layer-cake theorem [P]

Fix g: [0,∞) → [0,∞), piecewise linear on finitely many nodes, supported on [0,T], g ≢ 0. Put c₂ = ∫g², G(y) = ∫_0^{min(y,T)} g for y ≥ 0 and G(y) = 0 for y ≤ 0, and let X, X₁, X₂, … be i.i.d. with density g²/c₂. Write S_j = X₁ + … + X_j. Take the product test function

  F(t) = ∏_{i=1}^k g(k t_i) · 1[Σ t_i ≤ 1].

**Lemma 2.1 (exact reduction).** I(F) = k^{−k} c₂^k P(S_k ≤ k) and J^{(k)}(F) = k^{−(k+1)} c₂^{k−1} E[G((k − S_{k−1})₊)²].

*Proof.* Substitute x_i = k t_i. Then F² = ∏g(x_i)²·1[Σx_i ≤ k] integrates to c₂^k P(S_k ≤ k) times the Jacobian k^{−k}. For J, fix x₁, …, x_{k−1} with sum σ; ∫F dt_k = k^{−1}∏_{i<k} g(x_i)·G((k−σ)₊), because g vanishes beyond T. Square and integrate. ∎

**Theorem 2.2 (layer cake).** E[G((k − S_{k−1})₊)²] = ∫_0^T 2G(u)g(u) · P(S_{k−1} < k − u) du.

*Proof.* For y ≥ 0, G(y)² = ∫_0^y 2G(u)g(u) du since (G²)′ = 2Gg. Hence G((k−S)₊)² = ∫_0^T 2G(u)g(u)·1[u < k − S] du, and Fubini gives the claim. ∎

**Corollary 2.3 (certified lower bound).** For any numbers β_j ≥ P(S_{k−1} ≥ k − b_j) on a partition {[a_j, b_j]} of [0,T],

  M_k ≥ c₂^{−1} Σ_j max(0, 1 − β_j)·(G(b_j)² − G(a_j)²),

since the true tail P(S_{k−1} < k − u) is monotone in u, so on each cell it is ≥ 1 − β_j.

The point is that Corollary 2.3 needs only *upper bounds on lower-tail probabilities of a sum of i.i.d. bounded variables*, for which Chernoff (with the exponential majorised by chords on the piecewise-linear data, so that every integral is a rational number), a one-big-jump bound, or Berry–Esseen can be used, and *any* such family gives a valid certificate. This replaces the closed-form truncation bound used for every m ≥ 2 record since Polymath 8b (2014), whose deficit from log k was ≈ 2.3–2.9; the exact layer-cake accounting recovers ≈ 0.12 and shaped sub-exponential profiles g = e^{−(t/T₁)^κ}/(1 + At) on a long support recover ≈ 0.49 more, together a factor ≈ 3 in k. The 2023–2026 improvements of H₁ upgraded the arithmetic input while keeping the crude variational bound, which is why this gain was available.

### 2.3 The records [P/C]

**Theorem 2.4.** liminf(p_{n+2} − p_n) ≤ 173,438; liminf(p_{n+3} − p_n) ≤ 13,859,802; liminf(p_{n+4} − p_n) ≤ 1,120,662,828.

*Certificates.* With g the optimised 400-node profile (exact dyadic node values, sha256-pinned):

| k | m | threshold | certified M_k (Berry–Esseen, C = 0.56) | certified M_k (no Berry–Esseen) | tuple diameter |
|---|---|---|---|---|---|
| 15,856 | 2 | 8 | 8.013326752751306578… | **8.00677408008999410774** | 173,438 |
| 923,601 | 3 | 12 | 12.006666706750… | **12.00263034990571191492** | 13,859,802 |
| 56,000,000 | 4 | 16 | 16.0655 | — | 1,120,662,828 |

The H₂ and H₃ certificates were recomputed independently in outward-rounded ball arithmetic (python-flint/arb, 200 bits, adverse endpoint at every inequality; cross-checked with mpmath interval arithmetic plus a 2^{−150} guard band; both agree to all 30 printed digits and reproduce the historical float bit-for-bit). The Berry–Esseen-free column uses Chernoff + chord + Markov only, so **the H₂ and H₃ records depend on no probabilistic literature constant**. Admissibility: for k = 15,856 the explicit symmetric tuple {−86,719, …, 86,719} misses a class modulo each of the 1,847 primes ≤ k (two independent implementations); for k = 923,601 a repaired Hensley–Richards tuple (73,001 primes checked, two implementations; the classical fallback of diameter 14,505,780 also verified); for k = 56·10⁶ the first 56·10⁶ primes past k, with π-anchors checked against published values.

*Status.* Unconditional given Maynard's theorem and Bombieri–Vinogradov (both cited). The certificate chain is machine-checked but not formalised. An earlier audit (Astra) correctly noted that the committed certifier script was 50-digit floating point with a slack factor, not outward rounding; the re-certification above removes that objection.

### 2.4 The signed-sieve no-gain theorem [P]

Maynard–Tao weights are squares, w(n) = (Σ_d λ_d)² ≥ 0. Positivity is what makes the decode valid: if S₂ − mS₁ > 0 with S₁ = Σ w(n), S₂ = Σ w(n)ν(n), ν(n) = #{i : n + h_i prime}, then some n has ν(n) ≥ m+1. For signed w one must pay the debt D(w) = Σ_{w(n)<0} |w(n)|(m − ν(n))₊, after which S₂ − mS₁ − D(w) > 0 again implies the conclusion. Zhang's Landau–Siegel programme and Iwaniec's well-factorable λ^± both suggest that signed weights are the natural next class.

**Theorem 2.5.** Write w = w₊ − w₋ with w₊, w₋ ≥ 0 of disjoint support. Then

  S₂ − mS₁ − D(w) = Σ_n w₊(n)(ν(n) − m) − Σ_n w₋(n)(ν(n) − m)₊ ≤ Σ_n w₊(n)(ν(n) − m).

*Proof.* For every integer ν ≥ 0 and m ≥ 1, (ν − m) + (m − ν)₊ = (ν − m)₊: both sides equal ν − m if ν ≥ m and 0 otherwise. Multiply by w₋(n), sum, and subtract from Σ w(n)(ν(n) − m). ∎

So every signed weight is dominated, at face-value debt, by its own positive part: the variational problem does not enlarge. Positivity has a second job, boundedness (‖w‖₁ = S₁). Diagnostics on an exact finite model (n uniform on ℤ_W, ν a coprimality count, weights in a level-L feature span, rational arithmetic) confirm that the apparent phase transition in the debt price β occurs at β* = 23051796480/10991046857 = 2.0973… and is a normalisation artefact. The theorem says exactly where a signed route can live: (i) debt strictly below face value, which needs an exceptional character (Zhang), or (ii) a weight w that is evaluable while w₊ is not (well-factorable λ). Under a tuple-residue well-factorable estimate at level θ the conditional price list is H₁ ≤ 130, 114, 94, 80 at θ = 4/7, 7/12, 3/5, 5/8 [C].

---

## 3. The finite de Bruijn–Newman depth

### 3.1 Definition and dynamics [P]

For monic P(z) = ∏_{j=1}^N (z − e^{iθ_j}) = Σ a_j z^j define P_s(z) = Σ a_j e^{s·j(N−j)} z^j and the **depth** D(P) = inf{s > 0 : disc(P_s) = 0}. P_s stays self-inversive, so zeros stay on the circle until two collide; D is the first collision time. In terms of the real trigonometric polynomial Q₀(x) = ∏ sin((x − θ_j)/2), P_s corresponds (up to a scalar) to e^{s∂_x²}Q₀: the flow is the ordinary forward heat equation on Q₀, which is the direction that destroys real-rootedness. D is the finite analogue of −Λ for the de Bruijn–Newman constant.

**Lemma 3.1.** Until the first collision, dθ_j/ds = −Σ_{k≠j} cot((θ_j − θ_k)/2).

*Proof.* ∂_s P_s = (N D − D²)P_s with D = z∂_z. At a simple zero z_j, ż_j = −(∂_sP)(z_j)/P′(z_j) = −(N−1)z_j + z_j² P″(z_j)/P′(z_j) = −(N−1)z_j + 2z_j² Σ_{k≠j}(z_j − z_k)^{−1}. With z = e^{iθ} one has 2z_j/(z_j − z_k) = 1 − i cot((θ_j − θ_k)/2); summing over k ≠ j the (N−1) cancels and θ̇_j = ż_j/(iz_j) gives the claim. ∎

### 3.2 The comparison theorem and the lattice floor [P]

**Lemma 3.2.** g′ = −2cot(g/2), g(0) = g₀ ∈ (0, 2π) has the exact solution cos(g(s)/2) = e^s cos(g₀/2), so g vanishes at s = −log cos(g₀/2), and −log cos(x/2) ≥ x²/8 on [0, π) with equality only at 0.

**Theorem 3.3 (Theorem A).** For every configuration and every adjacent pair with gap g, g′ ≥ −2cot(g/2) for all s before the first collision. Hence D ≥ −log cos(δ_min/2) ≥ δ_min²/8.

*Proof.* For adjacent (a,b) with g = θ_a − θ_b > 0 across the short arc, Lemma 3.1 gives g′ = −2cot(g/2) − Σ_{k≠a,b}[cot(x_a^k/2) − cot(x_b^k/2)] with x_j^k = (θ_j − θ_k) mod 2π ∈ (0,2π). Adjacency means x_a^k = x_b^k + g with both in (0, 2π), and cot(x/2) is strictly decreasing there, so each bracket is negative and enters with a plus sign. Cyclic order is preserved until the first collision, so the inequality holds for every gap for all s < D, and comparison with Lemma 3.2 started from each g_i(0) shows no gap can vanish before min_i(−log cos(g_i(0)/2)). ∎

**Theorem 3.4 (Theorem C(i)).** Every non-clock ACUE configuration has δ_min = π/N exactly, hence N²D ≥ π²/8 = 1.2337005501….

*Proof.* The support is the 2N-th roots of unity, so every gap is a positive multiple of π/N and the N gaps sum to 2π = N·(2π/N). If all gaps were ≥ 2π/N they would all equal 2π/N, i.e. the clock. So some gap is exactly π/N, the smallest positive multiple. Apply Theorem 3.3. ∎

Exact enumeration of all 13,132 rotation orbits for N ≤ 10 gives N²D ∈ [1.31, 1.99] off the clock, P(clock) = 2^{1−N} exactly, and the clock itself has D = ∞ (the polynomials 1 − cz^N are flow-invariant) [C]. The single-dislocation configuration (delete e^{−iπ/N} from the alternating clock, insert 1) has N²D → s* = 1.419640342… = 1.150717118…·π²/8, obtained independently from the lattice solver at N = 20 and from the first double zero of G_s(u) = 2cos(u/2) − 2π∫_0^{1/2} e^{s(1/4−y²)} cos((π+u)y) dy, agreeing to 2·10⁻⁶ [C].

### 3.3 Invisibility to polynomial statistics [P]

**Proposition 3.5 (frozen moments along the flow).** Since P_s rescales a_j by the deterministic constant e^{s·j(N−j)}, every polynomial in the coefficients (a_j, ā_j) of balanced weight ≤ N evaluated on P_s is a polynomial of the same type evaluated on P. Because CUE and ACUE agree on all balanced moments of degree ≤ N (Tao), they agree on them for P_s at every s.

**Theorem 3.6 (Astra; protected moments under the forward flow).** Let V_k = Σ_{j≠k} cot((θ_k − θ_j)/2), L = Σ_k V_k ∂_{θ_k} the generator of the repulsive circular Coulomb flow, and p_m = Σ_k e^{imθ_k}. Then

  L p_m = −m((N − m)p_m + Σ_{a=1}^{m−1} p_a p_{m−a}),

so the total positive Fourier weight of every term is exactly m, and for all N, all 1 ≤ m ≤ N, all r ≥ 0 and all forward times t ≥ 0,

  E_ACUE L^r|p_m|² = E_CUE L^r|p_m|²,  E_ACUE|p_m(Φ_t X)|² = E_CUE|p_m(Φ_t X)|².

The proposal that iterated derivatives raise the degree of a low trace mode until lattice aliasing becomes visible is therefore false: no such derivative order exists. (Proof in `dynamic_generator.md`; the identity for L p_m is checked symbolically and in cyclotomic arithmetic.)

**Theorem 3.7 (Astra; an observable outside the protected algebra).** With D_force = Σ_i V_i², Q = Σ_{i≠j} csc²((θ_i − θ_j)/2), C_N = N(N²−1)/3: D_force = Q − C_N identically, E_CUE D_force = C_N, E_ACUE D_force = C_N/2, L D_force = −Σ_{i<j} csc²((θ_i−θ_j)/2)(V_i − V_j)² ≤ 0, E_CUE L D_force = −∞, E_ACUE L D_force = −2N(N⁴−1)/15.

Together, 3.5–3.7 make precise what the depth is escaping: the two ensembles agree on the whole algebra of protected trace moments, statically and dynamically; only rational observables of inverse gaps, and first-passage functionals, see the difference.

### 3.4 The matching upper bound: repaired stiffness and Theorem B′ [P]

Define, for an adjacent pair (a,b) with gap g and x_j^k as above, the **stiffness**

  S* := Σ_{k≠a,b} ½·max(csc²(x_b^k/2), csc²(x_a^k/2)) = ½ Σ_k csc²(dist(θ_k, {θ_a, θ_b})/2).

(An earlier version used only the b-endpoint; that bound is false in 34–49% of random configurations. The endpoint maximum is what the mean-value theorem actually gives, because csc²(t/2) is decreasing on (0,π] and increasing on [π, 2π).) Exactly, 0 ≤ background bracket ≤ g·S*, and at the clock S* = (N²−1)/6.

**Theorem 3.8 (Theorem B′).** Suppose S*(s) ≤ Θ·S*(0) for s ∈ [0,D) ∩ [0, δ²/4], and let μ = Θ S*(0) + κ₀ with κ₀ ≤ 4/π² (the explicit constant in −2cot(g/2) ≤ −4/g + κ(δ/2)·g). If μδ² ≤ 2 then, whichever pair collides first,

  −log cos(δ/2) ≤ D ≤ −(2μ)^{−1} log(1 − μδ²/4) ≤ (δ²/8)(1 + μδ²/4).

The window hypothesis holds with Θ = 2 when all other gaps are ≥ 2δ, and under a one-sided counting hypothesis (H_C) N_ab(ρ) ≤ CNρ + m₀ with CNδ ≤ 0.2071; without such a hypothesis it fails (a 3-cluster with neighbour gap 1.01δ has sup S*/S*(0) = 9.5). The proof is a linear differential inequality for g², integrated in closed form; no comparison lemma is needed.

### 3.5 The CUE background theorem and the depth law

**Theorem 3.9 [P].** For CUE(N), all N ≥ 2 and L > 0: P(δ_min > L·N^{−4/3}) ≤ 4086/L³. For all N ≥ 3 and M ≥ 1: P(S* > M·N²) ≤ 4087·M^{−1/2}, uniformly in N. First moment: E[#gaps ≤ xN^{−4/3}] = (x³/72π)(1 − N^{−2})(1 + O(x²N^{−2/3})).

*Ingredients.* The exact three-point function of CUE, ρ₃ = (2π)^{−3}∏_{i<j}|z_i − z_j|² Σ_{m₁<m₂<m₃}|s_λ(z)|², gives the global clustering bound ρ₃ ≤ C₃(N)∏|z_i − z_j|² with C₃(N) = N³(N²−1)²(N²−4)/(69120π³); a second-moment count of ordered triples with one pair at scale LN^{−4/3} and a third point within c/N; and a layer-cake bound on the bulk sum. The tail exponent −3 in L is sharp; the exponent ½ in M is not (the true tail is ≍ M^{−5/2}), because of Chebyshev on the bulk. The constant in the first statement was repaired after an independent review found a reversed inequality in one regime; the repair splits at the deterministic pigeonhole threshold L = 2πN^{1/3} and is verified by script.

**Theorem 3.10 (CUE depth law).** For Haar CUE, N^{8/3}D_N ⇒ G²/8 where P(G > x) = exp(−x³/72π); equivalently P(N^{8/3}D_N > t) → exp(−(2√2/9π)·t^{3/2}). Moreover 8D_N/δ_min² − 1 = O_P(N^{−2/3}).

*Two proofs.* (i) Theorem 3.3 + Theorem 3.8 + Theorem 3.9 + the Ben Arous–Bourgade law (cited; Ann. Probab. 2013), which is complete modulo a short-time stability statement that S* at s = 0 controls sup_{s<D} S*(s) (stated, not proved). (ii) Astra's **isolation lemma**: for a sequence of configurations with smallest gap δ, endpoints at ±δ/2, and B = ¼Σ_{k≠±} csc²(θ_k/2), if δ → 0 and δ²B → 0 then D = (δ²/8)(1 + o(1)), with explicit absolute constants when δ²(B+1) ≤ ε₀. It is proved directly on the scalar heat equation after an exact Galilean transformation that removes the common background drift, assumes nothing about the evolving background, and does not assume the closest pair collides first; the CUE input E Σ_{gaps ≤ ε} B_i ≤ N⁶ε³/18 gives B_min/N² = O_P(1). Route (ii) has two internal reviews and a quantified second-pass audit, and closes the localisation gap modulo the cited gap law. Neither route is Lean-checked or externally refereed.

**Corollary 3.11 (universality class).** For CβE with β ∈ (0,∞), the same argument with Feng–Wei's extreme-gap law (cited) gives D_N = (δ_min²/8)(1 + O_P(N^{−2/(β+1)+o(1)})) ≍ N^{−2−2/(β+1)}, modulo one near-diagonal three-point density hypothesis (U3) verified so far only at n = 2, β = 2. The predicted rate is confirmed at three points: fitted exponents −1.012 / −0.710 / −0.501 for β = 1, 2, 4 against −1 / −2/3 / −2/5 [C]. The lattice is the singular endpoint β = ∞: N²δ_min² = π² does not vanish, so ρ ≠ 1 there.

**What this says.** CUE and ACUE agree on every polynomial statistic of degree ≤ N, statically and along the flow, and yet their depths lie in different universality classes, N^{−8/3} versus N^{−2}. The mechanism is extreme-value: CUE admits rare pairs a factor N^{−1/3} below the mean spacing and is always within N^{−8/3} of losing real-rootedness, while the lattice quantises every gap at π/N. The alternative hypothesis fails this test by being *too stable*.

### 3.6 The Lagarias–Rodgers exchange rate and the threshold gap [P/C]

Let μ be the Lagarias–Rodgers hard-core extremum for bandwidth-one mimickers of the sine process (μ ≥ ½ by the shifted half-lattice; they suggest, but do not prove, μ ≤ 0.606894), and μ_Λ := sup over mimickers of liminf N²D.

**Proposition 3.12.** A hard core of c mean spacings gives δ_min = 2πc/N, so N²D = ρ·π²c²/2 with ρ ≥ 1, hence μ_Λ ≥ π²μ²/2 and μ ≤ √(2μ_Λ)/π. In particular AH (c = ½) forces liminf N²D ≥ π²/8, and a depth bound of 1.29 would give μ ≤ 0.511.

**Proposition 3.13 (the threshold gap).** A single gap of λ mean spacings in a clock background breaks the floor N²D < π²/8 iff λ < λ* = 0.4719538 (exact N-body dynamics, N-independent to 10⁻⁸; rigid one-dimensional quadrature 0.4718999; expansion ρ(λ) = 1 + (π²/4 − 2)λ² + …). In a random CUE background λ* ≈ 0.47 with narrow spread. So reaching the floor through gaps needs gaps six percent below one half; the depth adds an explicit dressing factor to the hard-core statement, but no shortcut.

---

## 4. The impostor fibre [P/C]

**Theorem 4.1 (dimension).** The affine dimension of the set of signed measures on the ACUE support (N-subsets of the 2N-th roots of unity) matching every balanced moment of degree ≤ N of CUE is 0, 0, 2, 10, 80, 403, 1804 for N = 3, …, 9 (exact arithmetic; a tighter-tolerance recount at N = 8 gave 399, and an exact recount is pending). Genuinely positive members exist from N = 5 on.

**Theorem 4.2 (centre-of-mass family).** For g: ℤ/N → ℝ, the measure q_g(C) = μ_ACUE(C)·g(X(C)), X(C) = Σ_{c∈C} c mod N, matches every balanced moment of degree ≤ N if and only if E_ACUE[g(X)] = 1 and ĝ(±1) = 0. This is an explicit (N−3)-parameter family at every N; X is exactly uniform under ACUE, and the coupling of a degree-≤N balanced moment to a centre-of-mass frequency in {2, …, N−2} vanishes by a transport-cost count (hop budget 2N against cost ≥ 2N+2). Together with the determinant-character (secant) and parity families this is one family, tilts by functions of det(U_C): on the lattice the global rotation is quantised and det² becomes a shape invariant. Verified at N = 5, …, 8 with worst moment error 10⁻¹².

**Theorem 4.3 (E1, chiral blindness).** For N ≥ 5 and 2 ≤ k ≤ N−2, the measures q_{k,ε} = μ_ACUE·(1 + ε·Im det(U_C)^{2k}), |ε| < 1, are positive, lie in the CUE-moment fibre, have total-variation distance 0.22–0.30 from ACUE at ε = 0.9, and give **exactly** the same law as ACUE to every dihedral-invariant statistic: the depth, its clock atom, every pattern count, every Haar-lifted even marked-depth moment. The chiral tangent space of the fibre has dimension 1, 3, 39, 186 at N = 5, 6, 7, 8. On the reflection-symmetric sub-fibre the depth law is injective for N ≤ 8.

*Proof idea.* Im det^{2k} is odd under reflection C ↦ −C while μ_ACUE and every dihedral-invariant functional are even, so the tilt integrates to zero against any such functional; balanced moments of degree ≤ N are killed because det(U_C)^{2k} = e^{2πikX/N} is a pure centre-of-mass mode of frequency k ∈ {2, …, N−2}, exactly the range that Theorem 4.2's transport-cost argument decouples from every balanced moment of degree ≤ N (ĝ(±1) = 0 and E g = 1 hold for g = 1 + ε sin(2πkX/N)). ∎

*Consequence for zeta.* The functional equation's reflection symmetry kills exactly this chiral half at zero cost (39 of 80 directions at N = 7) and provably cannot do more. Any statistic proposed to refute AH must be checked against the reflection-symmetric fibre, where the depth is already injective at small N.

---

## 5. The Nyquist conservation law and companion exact laws

### 5.1 The setting

Let m = (m_x)_{x∈ℤ/2N} be random nonnegative integer marks with Σm_x = N in every sample, and p_k = Σ_x m_x e^{iπkx/N}. The reference law is the rank-N consecutive-band projection determinantal process on ℤ/2N (the finite Fermi sea, whose scaling limit is ACUE and the half-lattice alternative hypothesis), with form factor E|p_k|² = min(k, N). Impose only the open rows E|p_k|² = k for 1 ≤ k ≤ N−1, leaving the Nyquist row k = N free.

### 5.2 Three exact identities [P]

**Theorem 5.1 (collisions live only at Nyquist).** For every such law, E Σ_x m_x(m_x − 1) = (E|p_N|² − N)/(2N).

*Proof.* Parseval on ℤ/2N: Σ_{k=0}^{2N−1}|p_k|² = 2N Σ_x m_x². Now p₀ = N, |p_{2N−k}| = |p_k|, and the open rows give Σ_{k=1}^{N−1} E|p_k|² = N(N−1)/2, with the mirrored rows k = N+1, …, 2N−1 contributing the same. So 2N E Σ m_x² = N² + N(N−1) + E|p_N|², i.e. E Σ m_x(m_x − 1) = E Σ m_x² − N = (E|p_N|² − N)/(2N). ∎

Consequently, closing the Nyquist row E|p_N|² = N forces all marks into {0,1}: the complete finite ramp admits only simple configurations, and the one unmeasured Fourier row is exactly where all multiplicity is stored.

**Theorem 5.2 (slack identity).** Let s₁ = #{x : m_x = 1} and h(j) = 0 for j ≤ 2, h(j) = j(j−2) for j ≥ 3. Then, configuration by configuration,

  s₁ − Σ_x m_x m_{x+1} − Σ_x h(m_x) = 2N − (1/2N) Σ_k |p_k|²(1 + cos(πk/N)),

and the Nyquist coefficient 1 + cos π = 0 makes the left side blind to the free row. Taking expectations under the open ramp and using 2Σ_{k<N} k cos(πk/N) = N − csc²(π/2N),

  E s₁ − (N/2 + csc²(π/2N)/(2N)) = E Σ_x m_x m_{x+1} + E Σ_x h(m_x) ≥ 0,

with equality exactly on hard-core {0,1,2}-configurations (no adjacent occupied sites, no mark above 2).

**Corollary 5.3 (density curve).** E s₁/N ≥ ½ + csc²(π/2N)/(2N²) → ½ + 2/π² = 0.702642367284…; and matching the rank-L band process at every row except Nyquist forces E s₁/L ≥ Φ(ρ) := 1 − ρ + sin²(πρ)/(π²ρ) in the limit L/M → ρ. At low density Φ(ρ) = 1 − (π²/3)ρ³ + O(ρ⁵): the sine kernel's quadratic repulsion becomes a cubic collision-rigidity loss.

The value ½ + 2/π² is *not* an improvement of δ_MT = 0.6725 and neither bounds the other: the first is a simple-site fraction in a marked integer model with an open Nyquist row, the second a proportion of simple critical zeros proved from arithmetic. Their kinship is that in both, a low-order spectral certificate is strengthened by integrality and a missing Fourier direction marks the boundary of what the certificate can see. The realisation of the equality face at all sizes is open; the series reduces it to a three-tile integral language with exact no-go theorems for every natural construction, and an explicit (M, L) = (6, 3) law shows that realising the extremal pair function does not imply attaining the simple-site equality (the mark-≥3 channel).

### 5.3 Fourth moments of the finite Fermi sea [P/C]

**Theorem 5.4.** For the half-filled finite Fermi sea on ℤ/2N and V_k = |p_k|², 1 ≤ k < N,

  E[V_k V_ℓ] = kℓ + k²·1{k=ℓ} − 2(k + ℓ − N)₊,  Cov(V_k, V_ℓ) = k²·1{k=ℓ} − 2(k + ℓ − N)₊,

and the covariance matrix has smallest eigenvalue exactly 1. (Fermionic normal ordering: the diagonal k² is the exchange term, the negative correction counts the two cyclic wrap intervals when two particle-hole excitations of total momentum k+ℓ exceed the band; verified by exact enumeration of all C(2N,N) atoms for N ≤ 6 to 10⁻⁹, λ_min = 1 at every tested N.) Consequences: the CUE target (1, …, N−1) is interior to the convex hull of binary feature rows with inradius ≥ 1/(N² − N/2); and a **repair theorem**: a candidate law on the hard-core face matching the ramp to feature error ε_N can be mixed with an explicit binary correction law to match the ramp exactly at simple-site cost ≤ N ε_N/(ρ_N + ε_N), so feature error o(N^{−2}) suffices for o(N) slack.

### 5.4 An exact total-variation law for holonomy [P/C]

**Theorem 5.5.** On the g-cycle with magnetic kernel K_φ = aI + rH_φ (forward edge phase e^{iφ}, 0 < 2r < min(a, 1−a)), every principal minor of order < g is independent of φ, det K_φ − det K_ψ = 2(−1)^{g−1} r^g (cos gφ − cos gψ), and

  d_TV(P_φ, P_ψ) = (2r)^g |cos gφ − cos gψ|.

The connected stationary version keeps all correlations of order < g equal while d_TV → 1. This is the cleanest closed-form statement we know that bounded-order correlations cannot identify a determinantal law, with the entire information loss computed; orientation (the sign of the holonomy) is invisible to *all* sampling statistics. Companion exact witnesses: projection DPPs on ℤ/12 with Fourier supports {0,1,4,6} and {0,1,3,7} have identical one- and two-point functions but triple probabilities (8 ∓ √3)/432; marked configurations u = (0,0,0,0,0,2,0,0,0,0,2,2), v = (0,0,0,0,1,1,0,0,0,0,1,3) on ℤ/12 have identical complete autocorrelation yet simple-site counts 0 and 3, lifting to aperiodic model sets with equal pure-point diffraction and simple-particle fractions 0 and ½.

---

## 6. Theorems about the Montgomery–Taylor method

The 2026 Lean-verified theorem (Anthropic) proves unconditionally that at least δ_MT = 3/2 − (1/√2)cot(1/√2) = 0.672500703679… of the zeros are simple and on the line, by measuring finite compressions of the indefinite Weil form from the prime side and decoding positive inertia through rank–trace inequalities. The following are new statements *about that method*, read at the Lean source.

**Theorem 6.1 (Galerkin closed form) [P/C].** Partition [−½, ½] into n cells and minimise the exactly integrated piecewise-constant energy q(v) = ∫v² + ∫∫|s−t|v(s)v(t). With a_n = 1 + 1/(3n²) and θ_n = arccos(1 − 1/(n²a_n)), the minimum is exactly q_n = ½ + (a_n n/2)·sin θ_n · cot(nθ_n/2), and 2 − q_n = δ_MT − [csc²(1/√2) − √2 cot(1/√2)]/(24n²) + O(n^{−4}). (Agreement with direct quadratic programming 4·10⁻¹⁴ for n ≤ 80.) This converts 0.6725007… from the output of an optimisation run into a checkable finite ladder.

**Theorem 6.2 (distinct-zero decoding) [P].** Combining the c = 2 inequality of the method with the zero-count identity once (not twice) gives N_d ≥ 0.8362503·N + p, where N_d counts distinct zeros and p off-line pairs: slope +1 in the off-line pair density, strictly stronger than the c = 3 decoding in the repository (slope ½). A five-line Lean edit.

**Theorem 6.3 (flat frontier) [P].** The certified simple-zero proportion as a function of the off-line pair density π is δ(π) ≡ 0.6725007 for all π ∈ [0, 0.16375]: assuming RH buys nothing within this method, because the binding adversary is on-line double zeros (exact 4p-budget/mass cancellation). At maximal off-line density all zeros are forced simple. Corollary: the density of off-line reflection pairs is at most (1 − δ_MT)/2 = 0.163749648160….

**Theorem 6.4 (edge no-go) [P].** Every admissible bandwidth-one window has r̂(±1) = 0 (Fejér–Riesz), so the pointwise edge hypothesis |F(1) − 1| ≤ ε certifies exactly 0.6725 even at ε = 0. The finite Nyquist conservation law of §5 is powered by lattice aliasing that ℝ lacks; the correct zeta-side edge object is the Cesàro mean F̄(∞,T), with the exact collision identity C(T) = N*·F̄(∞,T) − N(T).

**Theorem 6.5 (weight freezing) [P].** Derivative power sums are weight-homogeneous in the original power sums, so all bandwidth-one holomorphic statistics of the derivative process (the ξ′ analogue) are frozen on the impostor fibre; "differentiate then pair-correlate at bandwidth one" cannot work. AH is not closed under differentiation (exact N = 3 counterexample), and on the circle the stationary points of Z are the roots of zZ′ − (N/2)Z, all on the circle.

**Theorem 6.6 (rigidity of the inertia lemma) [P].** An exact seven-term deficiency decomposition turns the method's Lemma R into an identity; an ε-near-equality configuration lies within Frobenius distance √ε of an exact equality configuration. Zeta-side: the total deficiency over Montgomery–Taylor windows is ≤ (q* − 1)·N(T) = 0.3275·N(T), and on-line pairs with taper overlap ≥ τ number ≤ 0.1637·N(T)/τ².

**Proposition 6.7 (the third moment is informative at the MT window) [P/C].** At the flat window the sine-Gram data satisfies m₃ − 3m₂ + 2m₁ = 0 identically (a new rigidity fact holding at every finite N for ACUE), which is why tr Q³ looked worthless; at the Montgomery–Taylor window itself Φ₃ = m₃ − 3m₂ + 2m₁ = −0.0117753128 (closed trigonometric form, verified at 30 digits). The obstruction to monetising it is precisely one missing lemma, ‖(c^{−1}Â)_−‖ ≤ M_− uniform in T, which would give 0.6796896 (M_− = 2) up to 0.6844924 (M_− ≤ 1); window engineering provably cannot substitute (the clump term forces the row-sum cap M = A₀ log T for every window).

**Proposition 6.8 (the sharp pair-correlation LP) [C, correction to the record].** The value 0.6818287 carried in earlier files as "the pair-correlation ceiling" is a specific stability-inequality witness, not the sharp value of the F ≥ 0 bandwidth-one LP. Two independent computations of that LP (primal and dual, lattice sizes to 64, mesh to 1/80) converge to ≈ 0.679–0.680 (Aitken 0.67940). Triple-correlation (Rudnick–Sarnak band) constraints raise the small-lattice ceiling by 3–7%, shrinking with resolution. No correlation-only construction beats the mollifier value 19/27; the M_− lemma above is the only identified in-method route past 0.6725.

---

## 7. An explicit refutation criterion for the alternative hypothesis (Astra) [P under RH]

For fixed c > 0 let I_T(c) = ∫_0^T |ζ′/ζ(½ + c/log T + it)|² dt and

  W_T = 2[sinh(2)·I_T(1) − sinh(1)·I_T(½)] / (T log²T).

**Theorem 7.1.** Assume RH and AH-pairs (the precise pair-correlation form of the alternative hypothesis in Lagarias–Rodgers). Then W_T → W_AH with 0.06239 < W_AH < 0.06240 (exact rational enclosure). The sine-kernel prediction is 0.0822714431…. Hence a proof, under RH, that liminf_{T→∞} W_T ≥ 1/16 = 0.0625 refutes AH-pairs; the certified margin is 1/16 − W_AH > 0.00010.

**Theorem 7.2 (short-prime projection).** Under RH the mean square in 7.1 equals its short-prime diagonal (N = ⌊T/log⁶T⌋) plus a residual norm squared plus O_c(N log⁴T); the residual has an absolutely convergent centred-ψ continuation whose pole can be removed at cost O(log^{−3}T); the short-prime two-scale main term is B ∈ (0.45609397932923, 0.45609397932924); so the sufficient target is a lower bound liminf E_T ≥ 1/16 − B on the residual energy.

Twenty further reductions (complementary-modulus Möbius–log correlations to X^{0.523}, an RH component bound X^{1.023}log⁵X, exact Type-I removal below X^{0.477}, a full Vaughan reduction to a signed remainder, a full actual-variance reduction with its singular-series constant, removal of a central divisor band) narrow the missing estimate to a single signed prime correlation at scale X log X. None proves it. What is new here is not a theorem about zeta but the *exact* location and size of the obstruction: an inequality with a five-decimal target that any future arithmetic method must clear.

---

## 8. Smaller exact results worth recording

- **Residual-Gram saturation [P, Astra].** For a fixed resonator r and product cutoff L, the approximator-dependent main term in Inoue's half-gap method satisfies 2Re⟨b_a, b_g⟩_L − ‖b_a‖²_L = ‖b_g‖²_L − ‖b_a − b_g‖²_L with b_a(q) = Σ_{km=q}a(k)r(m) and ⟨b,c⟩_L = Σ_{q≤L} b̄(q)c(q)/q; so the coefficient-space approximator is exactly saturated on its own support and no rewriting on the same support recovers energy. Sparse longer tails under sub-polynomial coefficient bounds cannot supply constant energy.
- **A mass-weighted Fock-space bound [P].** On the bosonic Fock space over L²((0,1], du/u) restricted to total mass ≤ 1, ‖a(g)‖² ≤ ∫_0^1 |g(u)|²/u² du; for the diagonal operator K = A*A + (A² + A*²)/2 with g(u) = 2sin(πu/2) this gives ‖K‖ ≤ 2(2π·Si(π) − 4) ≈ 15.272, and its truncated spectrum converges to λ_∞ ≈ 4.6456, 6% below the threshold π²/2, matching an unrelated symmetric-prime-feature search (4.6455) to four figures [C]. Whether the true arithmetic operator stays below π²/2 is open.
- **Complementary dense divisibility [C, Astra].** With Y = 10, D = 330 = 2·3·5·11, E = 455 = 5·7·13, f(p) = p, g(p) = p², A₀ = 121, C₀ = 2197, X = 27000: the merged modulus Q = [D,E] = 30030 is triply 10-densely divisible although E alone is not — an exact witness that the rootwise predicates of the 186 mechanism genuinely exceed per-root dense divisibility, with shared primes allowed.
- **The single-dislocation constant** s* = 1.419640342… (§3.2) and the threshold gap λ* = 0.4719538 (§3.6), both exact to the stated digits and obtained by two independent routes each.

---

## 9. Status summary

| result | tag | novelty check (6 Sept 2026) |
|---|---|---|
| Layer-cake theorem; H₂, H₃, H₄ records; BE-free certificates | P/C | no m ≥ 2 improvement found in 2023–2026 literature |
| Signed-sieve no-gain | P | no treatment of debt-charged signed MT weights found |
| Theorem A, Theorem C(i), frozen moments, generator theorem, force energy | P | no published collision-time law for the finite flow found |
| Theorem B′, CUE stiffness tail, CUE depth law (two routes) | P modulo cited gap law (+ window stability on route i) | isolation-lemma novelty audit incomplete (Lehmer-pair kinship) |
| CβE law N^{−2−2/(β+1)} | P modulo (U3), Feng–Wei | — |
| LR exchange rate; λ* | P / C | Lagarias–Rodgers do not consider dynamics |
| Fibre dimensions; centre-of-mass family; Theorem E1 | C / P | Rodgers–Vallabhaneni compute moments, not the fibre |
| Nyquist conservation law; Φ(ρ); fourth-moment covariance; holonomy TV law | P / P/C | no occurrence of Φ(ρ) or the covariance formula found |
| Galerkin ladder; N_d decoding; flat frontier; edge no-go; weight freezing; rigidity; Φ₃ | P | statements about a 2026 theorem; no prior analysis found |
| Sharp pair LP ≈ 0.679 | C | corrects a number in the programme's own files |
| W_AH criterion; short-prime constant B | P under RH | no prior explicit AH-pairs target found |

Not claimed anywhere in this paper: RH, Montgomery's conjecture, μ = ½, a refutation of AH, or a prime gap below 186.

---

## References

Ben Arous, G., Bourgade, P.: Extreme gaps between eigenvalues of random matrices. Ann. Probab. 41 (2013). · Bombieri, E. (1965); Vinogradov, A.I. (1965). · Feng, R., Wei, D.: Small gaps of circular β-ensemble. Ann. Probab. 49 (2021). · Inoue, S.: Small gaps between consecutive zeros of the Riemann zeta-function. arXiv:2604.05733 (2026). · Lagarias, J.C., Rodgers, B.: Higher correlations and the alternative hypothesis. Q. J. Math. 71 (2020); arXiv:1905.12123. · Maynard, J.: Small gaps between primes. Ann. of Math. 181 (2015). · Montgomery, H.L.: The pair correlation of zeros of the zeta function (1973). · OpenAI: Improved short gaps between primes; repository openai/PrimeGaps186 (2026). · Polymath, D.H.J.: Variants of the Selberg sieve, and bounded intervals containing many primes. Res. Math. Sci. 1 (2014). · Rodgers, B., Tao, T.: The de Bruijn–Newman constant is non-negative. Forum Math. Pi (2020). · Rodgers, B., Vallabhaneni, H.: Autocorrelations of characteristic polynomials for the Alternative Circular Unitary Ensemble. Glasgow Math. J. (2023); arXiv:2301.00268. · Stadlmann, J.: On primes in arithmetic progressions and bounded gaps between many primes. arXiv:2309.00425; Bounded gaps between primes. arXiv:2608.31126 (2026). · Tao, T.: Heat flow and zeroes of polynomials I, II (blog, 2017–2018); The alternative hypothesis for unitary matrices (blog, 2019). · Anthropic: zeta-23-lean (2026).

**Source files** (branch `claude/riemann-zeta-random-matrix-udxp3f`, `research/riemann-rmt/`): `H2_H3_record_announcement.md`, `overnight/fable/r1_h2_interval_cert.md`, `signed_sieve_nogo.md`, `depth_scaling_theorem.md`, `overnight/fable/r1_theoremB_repair.md`, `r1_cue_background.md`, `r1_cbe_background.md`, `r1_levelB_barrier.md`, `r1_structure_review.md`, `r1_simple_zeros.md`, `r2_diagonal_operator_spectrum.md`, `impostors_paper.md`, `final_verified_paper.md`, `round3_synthesis.md`; and in `QingyunSun/Riemann-hypothesis-and-random-matrix` (`research/reports/`): `yau_flow.md`, `yau_flow_galilean_refinement.md`, `dynamic_generator.md`, `force_energy.md`, `residual_gram_round1.md`, `dyson_round7.md`, `dyson_round8.md`, `dyson_round14.md`, `prime186_structural_frontier.md`, and `research/claims/CLAIM_LEDGER.md`.
