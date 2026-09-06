# Zeta Zeros, Random Matrices, and Stopping Times

## A consolidated account of the programme: what was proved, what was computed, what was refuted, and what remains open

**Bill (Qingyun) Sun · GPT-6 Astra · Fable**
*(earlier rounds with GPT5.6SOL; see §0.3 for provenance)*

*6 September 2026*

---

## Abstract

This paper consolidates a research programme, carried out over August and September 2026 by a human mathematician working with several large language models in an adversarial loop, on the relationship between the zeros of the Riemann zeta function and random-matrix statistics, and on two neighbouring problems: the proportion of simple zeros and bounded gaps between primes. It is written to be read cold by a mathematician; every statement carries one of four status tags, **[P]** proved in the programme (a written argument that survived at least one independent adversarial review), **[C]** computed (script and data available, reproducible), **[R]** refuted or repaired during review, **[O]** open with the obstruction stated.

The results fall into four groups.

**(I) A stopping time that separates random matrices from Tao's alternative-hypothesis ensemble.** Write P(z) = det(I − zU) = Σ a_j z^j and run the backward heat flow P_s(z) = Σ a_j e^{s·j(N−j)} z^j. The *finite de Bruijn–Newman depth* D is the first s at which two zeros collide. The zeros obey the attracting circular Coulomb dynamics θ̇_j = −Σ_{k≠j} cot((θ_j − θ_k)/2) [P]. Every adjacent gap closes no faster than in the two-body problem, so D ≥ −log cos(δ_min/2) ≥ δ_min²/8 for the smallest gap δ_min [P]. For Tao's ACUE, the determinantal process supported on the 2N-th roots of unity that reproduces the CUE pair correlation exactly, every non-clock configuration has δ_min = π/N, hence N²D ≥ π²/8 [P]. For Haar-distributed CUE, N^{8/3}D converges in law to G²/8 where P(G > x) = exp(−x³/72π) is the Ben Arous–Bourgade smallest-gap law; the proof has two routes (a repaired stiffness bound with an explicit uniform tail P(S* > MN²) ≤ 4087·M^{−1/2}, and Astra's isolation lemma D = (δ²/8)(1 + o(1)) under δ²B → 0), both of which are written out and internally reviewed but rest on the cited extreme-gap law and, for one route, an unproved flow-window stability statement. The exponents −2 (lattice) versus −8/3 (CUE) hold although the two ensembles agree on every balanced moment of degree ≤ N, and — because the flow is diagonal on coefficients — continue to agree along the entire flow. Moment matching does not imply stopping-time matching.

**(II) A quantitative bridge to zeta.** In the Lagarias–Rodgers formulation, μ is the largest hard core a bandwidth-one mimicker of the sine process can have; the alternative hypothesis (AH) is μ = 1/2 realised by the zeros. On the circle a hard core of c mean spacings gives N²D = ρ·π²c²/2, so μ ≤ √(2μ_Λ)/π where μ_Λ is the corresponding depth extremum [P modulo the reverse comparison]. Transferred to the line under RH and one explicit hypothesis (NR), the statement "local depth of ζ-zeros eventually falls below π²/8" implies μ < 1/2, which is open; we prove that it is a *relabelling* of the small-gap problem, not a shortcut, and that the threshold gap is λ* = 0.4719538 mean spacings, six percent below 1/2 [P/C]. Astra reduced AH to explicit arithmetic inequalities: under RH and AH-pairs a two-scale mean square of ζ′/ζ tends to W_AH ∈ (0.06239, 0.06240), so any lower bound liminf ≥ 1/16 refutes AH-pairs [P]; twenty further rounds isolate the single missing signed prime-correlation estimate.

**(III) The simple-zero constant.** We re-derive δ_MT = 3/2 − (1/√2)cot(1/√2) = 0.672500703679 as the Montgomery–Taylor variational optimum [P], prove five structural theorems about the method (rigidity of the inertia lemma, a strictly stronger distinct-zero decoding N_d ≥ 0.8362503·N + p, an exactly flat RH-independence frontier, an edge no-go, and a weight-freezing no-go) [P], and show that the only in-method route past 0.6725 is one operator lemma worth +0.007 to +0.012. We correct the record on the pair-correlation "ceiling": the value 0.6818287 in circulation is a stability-inequality witness, not the sharp bandwidth-one LP value, which two independent computations put at ≈ 0.679 [C]. No correlation-only construction here or in the literature beats the mollifier value 19/27.

**(IV) Prime gaps.** liminf(p_{n+2} − p_n) ≤ 173,438, liminf(p_{n+3} − p_n) ≤ 13,859,802, liminf(p_{n+4} − p_n) ≤ 1,120,662,828, improving the previous records by factors 2.3, 1.8, 1.3 [P + C, machine-certified]. The gain is variational: an exact layer-cake reduction of the Maynard–Tao functional to one-dimensional tail probabilities plus shaped sub-exponential profiles. The H₂ certificate has been re-run in outward-rounded ball arithmetic and needs *no* Berry–Esseen input: M₁₅,₈₅₆ ≥ 8.00677 > 8 from Maynard's theorem and Bombieri–Vinogradov alone. We also prove that the signed (indefinite) enlargement of the Maynard–Tao problem is empty at face-value debt, so everything of value in Zhang's "remove the square" programme is arithmetic, not variational [P].

**What is not claimed.** No proof of RH, of Montgomery's conjecture, of the Lagarias–Rodgers conjecture μ = 1/2, of a refutation of AH, or of any prime gap below 186. Several claims made earlier in the programme were found to be wrong and are recorded as such in §6 and §17, together with what each correction taught.

---

## 0. How to read this paper

### 0.1 Status tags

Every numbered statement carries a tag. **[P]** means a written proof exists in the cited file and was reviewed by at least one independent agent whose job was to refute it; "proved" here never means Lean-checked or externally refereed. **[C]** means a reproducible computation with script and data in the repository. **[R]** means the claim as first stated was false and the text records the repair. **[O]** means open, and the sentence after the tag states the obstruction. "(recalled)" after a citation means the statement of a published theorem was used from memory and not re-read at the source during the programme.

### 0.2 Notation

θ_1, …, θ_N ∈ ℝ/2πℤ are eigenangles; g_i the cyclic gaps; δ_min = min g_i. CUE is Haar measure on U(N); CβE the circular β-ensemble with density ∝ ∏_{j<k}|e^{iθ_j} − e^{iθ_k}|^β; ACUE (Tao) is the measure on N-subsets C of the 2N-th roots of unity with mass |Δ(ζ^C)|²/(2N)^N. The *clock* is any rotation of the N-th roots of unity. Mean spacing is 2π/N; a *hard core of c* means all gaps ≥ 2πc/N.

### 0.3 Provenance and repositories

Rounds 1–5 (August 2026, with GPT5.6SOL) produced `impostors_paper.md`, `depth_scaling_theorem.md`, `stopping_times_paper.md`, `final_verified_paper.md`, `round3_synthesis.md`, `signed_sieve_nogo.md`, `H2_H3_record_announcement.md` and the handoff document `handoff/HANDOFF_GPT6_ASTRA.md`, all under `research/riemann-rmt/` on branch `claude/riemann-zeta-random-matrix-udxp3f` (PR #11 of `galpha-ai/Alpha-devbox`). The overnight adversarial session of 5–6 September (Fable, seven proposer–refuter–repair clusters) produced the files under `research/riemann-rmt/overnight/fable/`. GPT-6 Astra's twenty-eight rounds, its independent audit of the historical work, and its intake reviews of the Fable files live in `QingyunSun/Riemann-hypothesis-and-random-matrix` (branch `codex/astra-research`, `research/reports/`, `research/claims/CLAIM_LEDGER.md`). Each result below names its file.

---

## 1. The landscape

Three questions frame everything that follows.

**Montgomery's conjecture and the alternative hypothesis.** Montgomery (1973) proved, under RH, that the pair-correlation form factor F(α) of the zeros equals |α| for |α| ≤ 1 and conjectured that the normalised gaps follow the GUE/sine-kernel law. Everything provable today about the zeros is consistent with a very different scenario, the **alternative hypothesis (AH)**: all normalised gaps lie asymptotically in ½ℤ. Lagarias and Rodgers (2019) made this quantitative: among point processes that mimic the sine process at coordinatewise bandwidth one, let μ be the supremum of achievable hard cores; then μ ≥ 1/2 (the randomly shifted half-lattice), and AH is the assertion that the zeros achieve 1/2. Tao's ACUE is the random-matrix model of the half-lattice, and it reproduces the CUE pair correlation exactly. Any statistic that distinguishes CUE from ACUE *and* is provable for zeta would refute AH.

**The proportion of simple zeros.** Montgomery–Taylor showed, under RH, that at least δ_MT = 0.6725… of the zeros are simple; the 2026 Lean-verified theorem of Anthropic's group obtains the same constant unconditionally by reading the indefinite Weil form from the prime side and decoding positive inertia. The best mollifier-based constant is 19/27 ≈ 0.7037 (Conrey–Ghosh–Gonek, under GRH; recalled).

**Bounded gaps.** Since Maynard (2015) and Polymath 8b, liminf(p_{n+1} − p_n) ≤ 246; a 2026 preprint reports 186 by enlarging the coefficient support of restricted-modulus distribution estimates. For two, three, four primes in a window the records stood at 396,504 / 24,797,814 / 1,431,556,072.

The programme attacked the first question by a new instrument (Part I), tried to transfer it to zeta (Part II), audited the second question from the inside (Part III), and moved the higher records in the third (Part IV).

---

## Part I. The finite de Bruijn–Newman depth

### 2. Definition and the root dynamics

**Definition 2.1.** For monic P(z) = ∏(z − e^{iθ_j}) = Σ_{j=0}^N a_j z^j put

  P_s(z) = Σ_j a_j e^{s·j(N−j)} z^j,  s ≥ 0,   D(P) = inf{s > 0 : disc(P_s) = 0} ∈ (0, ∞].

P_s is again self-inversive, so a simple zero cannot leave the unit circle without first colliding; D is the first collision time. It is the finite analogue of −Λ for the de Bruijn–Newman constant: Λ_dBN ≤ 0 is RH, and Rodgers–Tao's Λ_dBN ≥ 0 says RH, if true, is barely true.

**Lemma 2.2 (root dynamics) [P].** Until the first collision, dθ_j/ds = −Σ_{k≠j} cot((θ_j − θ_k)/2).

*Proof sketch.* ∂_s P_s = (N D_z − D_z²)P_s with D_z = z∂_z; at a simple zero z_j the implicit-function derivative gives ż_j = −(N−1)z_j + 2z_j² Σ_{k≠j}(z_j − z_k)^{−1}, and 2z_j/(z_j − z_k) = 1 − i·cot((θ_j − θ_k)/2). Summing, the constants cancel exactly. (`depth_scaling_theorem.md` §1.)

Astra's independent derivation (`yau_flow.md` §2) gives the same flow as the *scalar* heat equation: with Q_0(x) = ∏ sin((x − θ_j)/2), the polynomial at time s is e^{sN²/4} e^{s∂_x²} Q_0. This identification is what makes the isolation lemma of §5.3 possible, and it is also why the three flows in play (Dyson Brownian motion, the Erdős–Schlein–Yau reverse heat argument, and this deterministic attractive Coulomb flow) must not be conflated: only the last one is being run here.

The clock is the unique fixed point up to rotation. Linearising at the clock gives the circulant operator 𝓛_N with (𝓛_N f)(x) = Σ_{k=1}^{N−1}[f(x) − f(x+k)]/(2sin²(πk/N)), eigenvalues δ(N−δ) — exactly the exponents of the flow, since a_j is the j-th Fourier mode of the clock displacement (two lines; `r1_structure_review.md` §1.2). The adversarial review of this "operator unification" found it standard: 𝓛_N is twice the Hessian of the circular log-gas energy at its Fekete minimiser, the phonon spectrum of the trigonometric Calogero–Sutherland lattice, and N^{−1}𝓛_N → (−Δ)^{1/2}; sharpened here to the exact identity 𝓛_N = N(−Δ)^{1/2} + Δ on band-limited functions [P]. The claimed "mechanism" that impostors hide in the fastest-relaxing modes was **not** established: the two occurrences of δ(N−δ) live on different spaces and no intertwining map was found [O].

### 3. The two-body problem and the comparison theorem

**Lemma 3.1 [P].** g′ = −2cot(g/2), g(0) = g_0, has the exact solution cos(g(s)/2) = e^s cos(g_0/2); the gap closes at s = −log cos(g_0/2) ≥ g_0²/8, with equality only at 0.

**Theorem A (two-body comparison) [P].** For every configuration and every adjacent pair with gap g, g′ ≥ −2cot(g/2) before the first collision. Consequently

  D ≥ −log cos(δ_min/2) ≥ δ_min²/8.

*Proof.* For adjacent (a,b), g′ = −2cot(g/2) − Σ_{k≠a,b}[cot(x_a^k/2) − cot(x_b^k/2)] with x_j^k = (θ_j − θ_k) mod 2π. Adjacency forces x_a^k = x_b^k + g inside (0, 2π), where cot(·/2) is strictly decreasing, so every bracket is negative and enters with a plus sign: *every other zero slows the collapse*. Order is preserved until collision, so the differential inequality applies to each gap for all time. ∎

Numerically the ratio D/(−log cos(δ_min/2)) has minimum 1.0842, 1.0714, 1.0612 over complete ACUE enumerations at N = 6, 8, 10, and 1.00019, 1.00021 over CUE samples at N = 16, 64.

**Corollary (Theorem C(i)) [P].** Every non-clock ACUE configuration has δ_min = π/N exactly (gaps are multiples of π/N summing to 2π; if all were ≥ 2π/N the configuration is the clock), hence N²D ≥ π²/8 = 1.2337005501….

Astra's audit (`BRIDGE-001`) supplies an exact rational counterexample showing that the initially smallest gap need *not* be the first to collide; Theorem A's lower bound is unaffected, but every statement that identifies "the critical pair" with "the initially closest pair" needs a pair-selection hypothesis, which the repaired Theorem B below states explicitly.

### 4. The impostor fibre: why moments cannot see, and why the flow cannot help

**Theorem 4.1 [C, exact arithmetic].** The affine dimension of the set of measures on the ACUE support matching every balanced moment E[∏ p_{m_i} ∏ \bar p_{n_j}] of degree ≤ N is 0, 0, 2, 10, 80, 403, 1804 for N = 3, …, 9. (A tighter-tolerance recount at N = 8 gave 399; an exact recount is on the open list.)

**Theorem 4.2 (centre-of-mass family) [P].** q_g(C) = μ_ACUE(C)·g(X(C)), X = Σ_{c∈C} c mod N, matches every balanced moment of degree ≤ N iff E[g] = 1 and ĝ(±1) = 0: an explicit (N−3)-parameter family at every N. The adversarial review (§5 of `r1_structure_review.md`) identifies this, the determinant-character (secant) family and the parity family as one family, tilts by functions of det(U_C); on the lattice the global rotation is quantised and det² becomes a shape invariant.

**Theorem 4.3 (diagonal flow) [P].** Since P_s multiplies a_j by e^{s·j(N−j)}, every balanced moment of degree ≤ N is frozen along the entire flow. Astra's `dynamic_generator.md` proves the forward-flow analogue in the observable algebra: for L = Σ_k V_k ∂_k the generator of the repulsive circular Coulomb flow, L p_m = −m((N−m)p_m + Σ_{a=1}^{m−1} p_a p_{m−a}), total positive Fourier weight exactly m, so E_ACUE L^r|p_m|² = E_CUE L^r|p_m|² for all r and all m ≤ N, and likewise at every finite forward time. The proposal that iterated derivatives would raise the degree until lattice aliasing becomes visible is false.

**Theorem 4.4 (an observable outside the protected algebra) [P, Astra].** With V_i = Σ_{j≠i} cot((θ_i − θ_j)/2), D_force = Σ V_i² = Σ_{i≠j} csc²((θ_i − θ_j)/2) − N(N²−1)/3, and E_CUE D_force = N(N²−1)/3 while E_ACUE D_force = N(N²−1)/6. The generator dissipates it: 𝓛D_force ≤ 0, E_CUE 𝓛D_force = −∞, E_ACUE 𝓛D_force = −2N(N⁴−1)/15. This is a rational observable of inverse gaps, not a polynomial one; the factor-two gap is a singular two-point statement and does not by itself supply an arithmetically accessible statistic of zeta zeros.

The depth is a first-passage time, not a polynomial statistic of any degree; that is why the fibre's freedom does not protect it. But the review also corrected an overstatement: the depth is **not** smooth in the configuration. It is a minimum over pairs and has kinks on a positive-mass set where the first collision is tied (3, 4, 6 orbits at N = 5, 6, 7, all mirror-symmetric) [R].

**Theorem E1 (chiral blindness) [P + C].** For N ≥ 5 and 2 ≤ k ≤ N−2 the measures q_{k,ε} = μ_ACUE·(1 + ε·Im det(U_C)^{2k}), |ε| < 1, lie in the CUE-moment fibre, sit at total-variation distance 0.22–0.30 from ACUE (ε = 0.9), and give exactly the same law to every dihedral-invariant statistic: the depth, its atom, all pattern counts, every Haar-lifted even marked-depth moment. The chiral tangent space of the fibre has dimension 1, 3, 39, 186 at N = 5, …, 8. So the depth alone cannot resolve the whole fibre; on the reflection-symmetric sub-fibre it is already injective at N ≤ 8 (E2). The functional equation's reflection symmetry kills exactly this chiral half at zero cost on the zeta side (round 3, D10), and provably cannot do more.

### 5. The separation and the scaling laws

**Theorem 5.1 (ACUE, exact) [C].** Complete enumeration of all rotation orbits for N = 3, …, 10 (13,132 orbits, 184,756 configurations at N = 10, Vandermonde masses to 40 digits). P(clock) = 2^{1−N} exactly (Cauchy–Binet). Clock polynomials 1 − cz^N are flow-invariant (D = ∞). Off the clock, N²D ∈ [1.31, 1.99], fitted exponent −2.0009, and in all 13,130 non-clock orbits the first collision is between a pair adjacent at s = 0. ρ = 8D/δ_min² lies in [1.049, 1.610] for N ≤ 10; that ρ_∞ = O(1) for all N is **[O]**.

**Theorem 5.2 (CUE, Monte Carlo to N = 256) [C].** Fitted exponent −2.678 ± 0.016 against the prediction −8/3, and 8N^{8/3}D ⇒ G² with P(G > x) = exp(−x³/72π), the constant 72π derived from the sine kernel, not fitted (measured 229–236 against 226.2; KS 0.035–0.041).

**The heuristic.** An isolated pair at gap δ collides at δ²/8 + o(δ²); a level-repulsion exponent β makes the smallest of N gaps of order N^{−1−1/(β+1)}; hence D ≍ N^{−2−2/(β+1)}. Measured: COE −3.064 (predicted −3), CUE −2.678 (−8/3), CSE −2.510 (−12/5, still drifting at N ≤ 64), ACUE −2.0009 (−2) [C]. The lattice endpoint β = ∞ is *singular*, not limiting: there N²δ_min² = π² does not vanish, the background contributes at leading order, and the single-dislocation configuration (delete e^{−iπ/N} from the alternating clock and insert 1) has N²D → s* = 1.419640342… = ρ_∞·π²/8 with ρ_∞ = 1.150717118…, obtained by two independent routes (lattice solver at N = 20 and a continuum double-zero condition for G_s(u) = 2cos(u/2) − 2π∫_0^{1/2} e^{s(1/4−y²)}cos((π+u)y)dy) agreeing to 2·10⁻⁶ [C]. Interpretation: CUE admits rare pairs a factor N^{−1/3} below mean spacing and is always within N^{−8/3} of losing real-rootedness; the lattice forbids the accidents. *The alternative hypothesis fails not by being fragile but by being too stable.*

#### 5.1 Theorem B and its repair

The matching upper bound needs the background not to interfere. The original statement used the stiffness S = Σ_{k≠a,b} ½csc²(x_b^k/2); Astra's audit produced configurations where the bound 0 ≤ background ≤ g·S is false (it fails in 34–49% of CUE/ACUE samples, by up to 57%), because the mean-value bound must use the *larger* endpoint of the pair [R].

**Definition 5.3 (repaired stiffness).** S* := Σ_{k≠a,b} ½·max(csc²(x_b^k/2), csc²(x_a^k/2)) = ½Σ_k csc²(dist(θ_k, {θ_a,θ_b})/2). Then exactly, with B the background bracket, 0 ≤ B = 2sin(g/2)·S_exact ≤ g·S* [P, `r1_theoremB_repair.md` §2]. At the clock S* = (N²−1)/6.

**Theorem B′ [P].** Let (a,b) be an adjacent pair with gap δ. Suppose S*(s) ≤ Θ·S*(0) for s ∈ [0,D) ∩ [0, δ²/4], and put μ = Θ·S*(0) + κ_0 with κ_0 ≤ 4/π² the explicit constant of −2cot(g/2) ≤ −4/g + κ(δ/2)g. If μδ² ≤ 2 then

  −log cos(δ/2) ≤ D ≤ −(2μ)^{−1} log(1 − μδ²/4) ≤ (δ²/8)(1 + μδ²/4),

whichever pair collides first. The proof is a linear inequality for g², with no comparison lemma. The window hypothesis S*(s) ≤ Θ S*(0) is itself proved (Θ = 2) when all other gaps are ≥ 2δ, or under a one-sided density hypothesis (H_C): N_ab(ρ) ≤ CNρ + m_0 points within ρ of the pair, with CNδ ≤ 0.2071 [P, §5.2]. Without a neighbour-gap hypothesis the window claim is false: a three-cluster with neighbour gap 1.01δ has sup S*/S*(0) = 9.5 [R+C].

**Corollary 5.4 [P].** Under (H_C) with CNδ ≤ 0.2 and Nδ ≤ 1, δ²/8 ≤ D ≤ (δ²/8)(1 + 4C²N²δ² + 0.29δ). Numerically D ≤ T(sup S* + κ_0) held in every one of 300 CUE samples at each of N = 16, 32, 64, in ACUE, in dislocation and cluster tests, with D certified to 10⁻⁶ by 60-digit brackets [C].

#### 5.2 The CUE background theorem

The one open analytic ingredient of the August write-up was "S ≤ AN² with high probability". It is now a theorem for CUE, with an explicit uniform tail.

**Proposition 5.5 [P, constant repaired].** For all N ≥ 2 and L > 0, P(δ_min > L·N^{−4/3}) ≤ 4086/L³. First moment: E[#gaps ≤ xN^{−4/3}] = (x³/72π)(1 − N^{−2})(1 + O(x²N^{−2/3})), which pins 72π in our normalisation. The original proof used a reversed inequality in one regime (Astra's intake review); the repair splits at the deterministic pigeonhole threshold L = 2πN^{1/3} and is verified in `scripts/r1_cue_background_prop33_repair_check.py`, which also confirms that the original direction fails.

**Theorem 5.6 [P].** For all N ≥ 3 and M ≥ 1, P(S* > M·N²) ≤ 4087·M^{−1/2}, uniformly in N. Ingredients: the exact three-point structure ρ_3 = (2π)^{−3}∏|z_i − z_j|² Σ_{m_1<m_2<m_3}|s_λ(z)|² giving the global clustering bound ρ_3 ≤ C_3(N)∏|z_i − z_j|² with C_3(N) = N³(N²−1)²(N²−4)/(69120π³) (constant π⁶/135 in density-one units), a second-moment count of triples with one pair at scale N^{−4/3} and a third point within c/N, and a layer-cake bound on the bulk sum. Monte Carlo (N = 64/128/256; 6800 samples): median S*/N² ≈ 0.13, q99 ≈ 0.45, max ≈ 1.5; no sample with S* > N² log N [C]. The true tail exponent is 5/2; the proved 1/2 is lossy through Chebyshev [O].

**Theorem 5.7 (CUE depth law).** N^{8/3}D_N ⇒ G²/8, P(G > x) = exp(−x³/72π); equivalently P(N^{8/3}D_N > t) → exp(−(2√2/9π)t^{3/2}). Also 8D_N/δ_min² − 1 = O_P(N^{−2/3}).

*Status.* Two routes. (i) Fable: Theorem A + Theorem B′ + Theorem 5.6 + Ben Arous–Bourgade (recalled), which is [P] modulo the window-stability statement (E-B*) that S* at s = 0 controls sup_{s<D} S*(s) [O, stated not proved]. (ii) Astra (`yau_flow.md`, `yau_flow_galilean_refinement.md`, round 14): an initial-data **isolation lemma** — if δ → 0 and δ²B → 0 with B = ¼Σ_{k≠±} csc²(θ_k/2), then D = (δ²/8)(1 + o(1)) with explicit constants when δ²(B+1) ≤ ε_0 — proved directly on the scalar heat equation after an exact Galilean transformation removing the common background velocity, with no assumption on the evolving background and no assumption that the closest pair collides first; the CUE input E Σ_{gap≤ε} B_i ≤ N⁶ε³/18 gives B_min/N² = O_P(1) from the classical extreme-gap law. Route (ii) has two internal reviews and a quantified second-pass audit (`galilean-proof-audit.md`); it is the cleaner argument and closes the CUE localisation gap modulo the cited gap law. Neither route is Lean-checked or externally refereed, and Astra's own ledger records the novelty audit as incomplete: the isolation lemma overlaps conceptually with classical Lehmer-pair criteria.

#### 5.3 General β

**Theorem 5.8 [P modulo (U3) and Feng–Wei].** For CβE, β > 0, reusing Theorem B′ verbatim: P(δ_min ≤ cN^{−1−1/(β+1)} and a third point within L/N of the pair) ≤ K·L^{β+1}c^{2β+1}, and the background hypothesis (H_C) holds with probability → 1, giving D_N = (δ_min²/8)(1 + O_P(N^{−2/(β+1)+o(1)})) ≍ N^{−2−2/(β+1)}. The one weakest link is a near-diagonal three-point density bound, hypothesis **(U3)**: ρ_3 ≤ [K/(2π)³]N^{3+3β}∏(d_ij)^β at microscopic separations; verified explicitly only for n = 2, β = 2 [O for n = 3 and β ≠ 2]. This file went through two repair passes (its own refuters, then Astra's `CBETA_REPAIR_REVIEW.md`); the N-rescaling of the sine argument, a finite-N Taylor coefficient (1 − N^{−2})/12, a transcribed partition function, an invalid relative-error step near v = 0, a status overclaim for β ∈ {1,4}, and an equality that should be an inclusion were all fixed. The headline exponents survived every repair (checked symbolically and numerically for β = 1, 1.5, 2, 4 in `scripts/r1_cbe_prop31_ncheck.py`). The predicted rate ρ_β − 1 = O(N^{−2/(β+1)}) is confirmed at three points: fitted −1.012 / −0.710 / −0.501 against −1 / −2/3 / −2/5 for β = 1, 2, 4 [C].

### 6. What did not survive review in Part I

- **Marked-depth "rank-two law" [R].** Λ is blind to eigenvectors; the marked depth χ(G;u) = ∂_η D(Cayley(G + ηuu*)) was proposed to see them, and a law Dτ[uu*] = (κδ/4)u*K_ab u + (δ²/8)κ′(u) was "confirmed to eleven digits". The review shows the first term is Hellmann–Feynman for the colliding pair (correct, standard), and the second is the product rule applied to τ ≡ (8τ/δ²)·δ²/8; the eleven-digit fit holds with any function in place of δ²/8. The sign convention c_j = −2/(1+λ_j²) was also wrong, cancelled by labelling in the code. The polarisation-detector and tomography corollaries are correct consequences of the first term.
- **Tractability claim [R].** "The depth threshold N²D < π²/8 is a more tractable route to AH than the gap" is unsupported: by Theorem A the threshold is implied by, and implies nothing beyond, δ_min < π/N.
- **Smoothness of D [R]** (see §4).
- **"S changes by ≤ 2 in the collision window" [R]** without a neighbour-gap hypothesis (§5.1).
- **s* as the ACUE median limit [R].** The median turns at N = 7 (1.41822, 1.41520, 1.41277 at N = 8, 9, 10); s* is a configuration constant of the single-dislocation stratum.
- **Marked depth as a fibre detector [R, ill-posed].** Fibre elements are measures on spectra; with the canonical conjugation-invariant lift the marked depth reduces to statistics of ∇τ.

---

## Part II. The bridge to zeta

### 7. The Lagarias–Rodgers exchange rate

**Proposition 7.1 [P modulo the reverse comparison].** On the circle a hard core of c mean spacings gives δ_min = 2πc/N, so N²D = ρ·π²c²/2 with ρ ≥ 1 (Theorem A). With μ_Λ := sup over mimickers of liminf N²D,

  μ_Λ ≥ π²μ²/2,  μ ≤ √(2μ_Λ)/π.

The value μ ≤ 0.606894 corresponds to μ_Λ ≤ 1.8177; a depth bound of 1.29 would give μ ≤ 0.511. *Correction (Astra, SOURCE-001):* Lagarias–Rodgers *suggest* 0.606894 as a hard-core upper bound from the pair-correlation constraint; it is not proved in the cited passage. The best proved bound in this programme's reading is Inoue's μ < 0.50895 under RH (2026 preprint, as read by Astra; the overnight Level-B file cites the earlier record 0.515396); the once-cited "μ ≤ 0.50412" was withdrawn by its authors in 2019.

### 8. Level B: a relabelling, not a shortcut

Call **Level B** the statement: for the zeros of ζ in a window at height T containing N ≈ (log T)/2π zeros, the local Newman depth satisfies liminf N²D < π²/8. Under AH-strong (all gaps in ½ℤ + o(1), no multiple zeros) every window has hard core 1/2 and Theorem A gives N²D ≥ π²/8; so Level B refutes AH-strong. The question posed to the overnight session was whether Level B is *easier* than a direct gap statement.

**Theorem A′ [P, under RH and (NR)].** In the Polymath-15 normalisation H_t(z) = ∫e^{tu²}Φ(u)cos(zu)du, the flow toward t < 0 is the exact backward heat equation on the line and the window zeros obey the line analogue of Lemma 2.2 with the periodised model being the *exact* backward flow of a periodised zero set (no small-gap approximation). Under the hypothesis (NR) that no non-real zero formed elsewhere enters the window before it collides, an adjacent pair closes no faster than the two-body rate, and

  Level B ⟹ μ ≤ √(2c)/π < 1/2,  c := liminf (log T)²D_T.

So any proof of Level B is a proof of μ < 1/2, which is open. The converse fails: a gap of λ mean spacings with λ ∈ (λ*, ½) does **not** break the floor. In a clock background the threshold is **λ* = 0.4719538** (exact N-body, N-independent to 10⁻⁸; one-dimensional quadrature 0.4718999; expansion ρ = 1 + (π²/4 − 2)λ² + …), and in a random CUE background again ≈ 0.47 with narrow spread [C]. One needs gaps six percent below one half. Level B refutes only AH-strong: a multiple zero gives D_T = 0 trivially while AH-with-multiplicities is untouched.

**Repair [R → O].** The first draft claimed the periodised (finite-polynomial) version unconditionally. Astra's counterexample: N points 0, …, N−1 in a window of length N−1+ε have all internal gaps 1 but the wrap gap ε, so a small circular depth need not come from a real zeta gap. The periodised implication is downgraded to [O] pending a non-wrap witness; Theorem A′ on the line is unaffected.

**Verdict.** The depth adds a clean deterministic formulation of "AH-strong ⟹ no gap below ½ − o(1)", an explicit dressing factor ρ(λ), and a first-passage functional; it removes no information requirement.

### 9. Astra's explicit actual-zeta targets

The main lane of Astra's rounds 7–28 is to turn "refute AH" into one arithmetic inequality about primes, with every reduction written as an ordinary proof and independently reviewed. The results, in order of strength:

**Theorem 9.1 (two-scale target) [P, under RH and AH-pairs].** For I_T(c) = ∫_0^T |ζ′/ζ(½ + c/log T + it)|² dt and W_T = 2[sinh(2)I_T(1) − sinh(1)I_T(½)]/(T log²T), W_T → W_AH with 0.06239 < W_AH < 0.06240 (exact rational enclosure). The sine-kernel prediction is 0.0822714431…. Hence a proof under RH that liminf W_T ≥ 1/16 = 0.0625 refutes AH-pairs; the certified gap 1/16 − W_AH > 0.00010 is what a lower-bound argument must deliver.

**Theorem 9.2 (short-prime projection) [P, under RH].** The mean square in 9.1 equals its short-prime diagonal (N = ⌊T/log⁶T⌋) plus a residual norm squared plus O_c(N log⁴T); the residual has an absolutely convergent centred-ψ continuation whose pole can be removed at cost O(log^{−3}T); the short-prime two-scale main term is B ∈ (0.45609397932923, 0.45609397932924), so the sufficient target is liminf E_T ≥ 1/16 − B for the residual energy [rounds 8–9].

**Reductions of the residual [P, rounds 9–27].** Selected Möbius–log divisor correlations on complementary moduli up to X^{0.523} have per-shift error O_A(X log^{−A}X) unconditionally; under RH the smooth discrepancy is O(√(X(X+Q²)) log⁵X), i.e. X^{1.023}log⁵X, still above the X log X needed; exact Type-I removal (Λ_{≤U}, U ≤ X^{0.477−η}) is o(X log X); an exact full-kernel Vaughan reduction leaves the signed remainder D[μ_{>A} * β_B] with error X^{1711/1750}log²X; frequency-two saturation gives a sharp AH target; a full actual-variance reduction with its nonzero singular-series constant covers the whole height/length range (round 26); a central Möbius divisor band can be removed jointly (round 27). Several shortcuts are proved *not* to work (round 12): phase absorption into Siegel–Walfisz fails by an explicit modulus-3 discrepancy, the product-local residue lift costs φ(d), and centred Selberg–Gallagher gives only a weak one-sided bound.

**Round 28 (finite experiment) [C].** Actual-prime matrices C_{d,k} = f_T(dk) over odd d, k ∈ (1.05T, 1.35T], X = T² = 10⁶, 4·10⁶, 1.6·10⁷ (dimensions 150, 300, 600). Selected Mellin transpose pairings w_t^T C w_t reach 35%, 47%, 55% of the operator norm, whereas the fixed Möbius/log contraction is only 5–8% of its Cauchy bound; there is no isolated dominant singular value. The exact bound ‖C‖_op ≥ sup_t |𝓜_T(t)| identifies these pairings as centred prime and zeta-zero observables. This is evidence about where the operator's mass sits, not an asymptotic.

**Status.** The strict lower bound on the signed prime correlation is **[O]** in every formulation; Astra's ledger (`OPEN-002`) records no new fixed-width pair-correlation theorem beyond known support. Nothing in Part II refutes AH.

---

## Part III. The simple-zero constant 0.6725

### 10. What the constant is [P]

Montgomery's method bounds the proportion of simple zeros through one quadratic functional of a window profile v on [−½, ½]:

  q(v) = ∫v² + ∫∫|s − t| v(s)v(t) ds dt,  ∫v = 1,  δ = 2 − q(v).

The kernel |s − t| is the CUE form factor min(|u|,1) in disguise. The Euler–Lagrange equation is v″ = −2v, the even mass-one solution v*(s) = cos(√2 s)/(√2 sin(1/√2)), and

  q* = ½ + (1/√2)cot(1/√2) = 1.327499296320…,  δ_MT = 2 − q* = 3/2 − (1/√2)cot(1/√2) = 0.672500703679116….

Re-derived at 50 digits (`scripts/r1_c1_verify.py`) and by a discretised QP at n = 4000 (8 digits; profile to 6·10⁻⁹). A closed-form finite Galerkin solution with exact n^{−2} error makes δ_MT an exactly computable finite object (the printed angle must be read θ_n = arccos(1 − n^{−2}/a_n); `final_verified_paper.md` §1.3).

### 11. Theorems about the method (round 3) [P]

Read from the Lean source of the 2026 theorem, not from paraphrase:

1. **Rigidity of the inertia lemma.** An exact seven-term deficiency decomposition turns Lemma R into an identity; an ε-near-equality configuration lies within Frobenius distance √ε of an exact one. Zeta-side ledger: total deficiency over MT windows ≤ (q* − 1)N(T) = 0.3275·N(T), which yields an unconditional pair-repulsion-type bound (on-line pairs with taper overlap ≥ τ number ≤ 0.1637·N(T)/τ²). The Montgomery–Taylor optimisation *is* minimisation of the RMT-predicted deficiency.
2. **Distinct-zero decoding.** N_d ≥ 0.8362503·N + p with slope +1 in the off-line pair density, strictly stronger than the c = 3 decoding in the repository (a five-line Lean edit, not yet made).
3. **Flat RH-independence frontier.** δ(π) ≡ 0.6725007 for all off-line densities π ∈ [0, 0.16375]: *assuming RH buys nothing within this method*; the binding adversary is on-line double zeros.
4. **Edge no-go.** Every admissible bandwidth-one window has r̂(±1) = 0 (two-line Fejér–Riesz), so a pointwise edge hypothesis |F(1) − 1| ≤ ε certifies exactly 0.6725 even at ε = 0; the correct edge object is the Cesàro mean F̄(∞,T) with the exact collision identity C(T) = N*·F̄ − N(T).
5. **Weight freezing.** Derivative power sums are weight-homogeneous, so bandwidth-one holomorphic statistics of ξ′ are frozen on the fibre; "differentiate then pair-correlate" cannot work; AH is not closed under differentiation (exact N = 3 counterexample).
6. **The one in-method upgrade.** At the MT window the third moment is genuinely informative, Φ_3 = m_3 − 3m_2 + 2m_1 = −0.0117753128 (closed trigonometric form; it vanishes identically at the flat window), and tr Â³ at bandwidth one is licensed arithmetically; the blocker is that the hypothesis class carries no bound on the size of the compression's negative eigenvalues. A zero-side lemma ‖(c^{−1}Â)_−‖ ≤ M_− uniform in T would give δ = 0.6796896 (M_− = 2) up to 0.6844924 (M_− ≤ 1). Window engineering cannot substitute (the clump term forces M = A_0 log T for every window) [R for the naive idea, P for the reduction].

### 12. Two ceilings, and a correction to the record

**The 0.7026 anomaly, closed [C].** The free finite optimum of the marked-ACUE pencil is δ_free → ½ + 2/π² = 0.70264237; the Anthropic-feasible restriction gives 0.6725. The whole gap 0.030142 is certified by one lattice inequality S_1 ≥ 0 (nonnegative pair count at half mean spacing), single-site in position and full-band in Fourier; ℓ²-decoupling misprices it by 15–77×. Only ≈ 0.0093 is recoverable in the continuum, to a ceiling ≈ 0.6818; the rest is lattice aliasing.

**C1: what "PairCeiling 0.6818287" is [R, repaired in place].** This number, carried in the programme's context files as "the pair-correlation ceiling", is a specific stability-inequality witness from `LawN256.lean` resting on an unverified hash, already flagged as unreproducible in `final_verified_paper.md`. It is **not** the sharp value of the F ≥ 0 bandwidth-one pair-correlation LP. Two independent computations of that LP (`scripts/r1_pair_lp.py`, `r1_pair_dual_lp.py`: primal and dual, lattice sizes to 64, mesh to 1/80) converge to **≈ 0.679–0.680** (Aitken 0.67940), *below* 0.6818287 [C]. The candidate exact value 15/22 = 0.6818… from round 3 is therefore not supported as the sharp LP. Adding triple-correlation (Rudnick–Sarnak band) constraints raises the exact small-lattice (P ≤ 8) ceiling by 3–7%, shrinking with resolution; its continuum limit is [O].

**Honest verdict on 19/27.** The Conrey–Ghosh–Gonek constant comes from mollified discrete moments, not from a correlation LP; no correlation-only construction here or known to us beats it, and the M_− lemma of §11 is the only identified route past 0.6725 inside Montgomery's framework.

### 13. Toward μ < 1/2: the residual-Gram operator wall

Inoue's 2026 theorem gives μ < 0.50895 under RH by a weighted second factorial moment of short-interval zero counts with arbitrary resonator coefficients under a product cutoff. The question posed to both agents: is the diagonal method dead at half a mean spacing (φ = ½) for *all* coefficients?

- **Exact saturation [P, Astra].** For fixed resonator r and cutoff L the approximator-dependent main term satisfies 2Re⟨b_a, b_g⟩ − ‖b_a‖² = ‖b_g‖² − ‖b_a − b_g‖², so the chosen approximator is a global maximiser on its own support; no rewriting on the same support helps. Sparse longer tails under sub-polynomial coefficient bounds cannot supply constant energy [P].
- **Numbers [C, both].** Degree-14 half-gap margin −0.01535798; symmetric-prime-factor features −0.01465473 (4.6% of the deficit); a rational instance has certified continuum margin in (−0.01467, −0.01465). Full eigenvalue searches through L = 10⁷ stay below the threshold π²/2.
- **F3 (diagonal operator on Fock space) [C, corrected].** The continuum idealisation K = A*A + (A² + A*²)/2 on bosonic Fock space over L²((0,1], du/u), truncated to total mass ≤ 1, has Lanczos spectrum converging to **λ_∞ ≈ 4.6456** (M up to 55), 6% below π²/2 = 4.9348, and matching Astra's independent richer feature search (4.6455) to four figures by a structurally unrelated computation. The first draft claimed the crude Cauchy–Schwarz bound was infinite; Astra's mass-weighted estimate gives ‖a(g)‖² ≤ ∫|g|²/u² and hence **‖K‖ ≤ 2B_g² = 2(2π·Si(π) − 4) ≈ 15.272**, finite [R], verified to 30 digits. A claimed scalar action of the truncated commutator on fixed-mass sectors was falsified (up to 13× spread) and withdrawn.
- **F1/F2 (arithmetic transfer) [mixed].** The normalisation and leading S2 moments of Astra's symmetric-prime family transfer modulo Selberg–Delange; the Π_4 leading coefficient is 6a (m_4 = a² + 6a), corrected from a self-contradictory 6a² (the numerical value was already right); the insertion-term (M2) transfer and M3 completeness are [O]; the α-piece converges like log log L/log L, slower than a Mertens correction, across L = 10³…10⁸ [C].

**Status.** Whether λ_max ≤ π²/2 for the true arithmetic operator — the "wall" — is fully open in both directions.

---

## Part IV. Bounded gaps between primes

### 14. The records [P + C, machine-certified]

**Theorem 14.1.** liminf(p_{n+2} − p_n) ≤ 173,438; liminf(p_{n+3} − p_n) ≤ 13,859,802; liminf(p_{n+4} − p_n) ≤ 1,120,662,828.

*Inputs.* Exactly three: Maynard's theorem (if the primes have level of distribution θ and M_k > 2m/θ then every admissible k-tuple has infinitely many translates with ≥ m+1 primes; closed simplex, no ε-enlargement), Bombieri–Vinogradov (every θ < ½), and — for the stronger certificate only — Berry–Esseen. Certificates M_{15,856} ≥ 8.0133, M_{923,601} ≥ 12.0067, M_{56,000,000} ≥ 16.0655, with admissible tuples of diameters 173,438 (explicit, sha256-pinned, admissibility by two implementations), 13,859,802 (repaired Hensley–Richards; classical fallback 14,505,780), 1,120,662,828 (primes past k).

*The method.* For F = ∏g(x_i)·1[Σx_i ≤ k] the Maynard functionals are exactly one-dimensional: I(F) = k^{−k}c_2^k P(S_k ≤ k) and J(F) = k^{−(k+1)}c_2^{k−1}E[G((k − S_{k−1})_+)²] with X_i i.i.d. of density g²/c_2 and G = ∫g. The **layer-cake identity** E[G((k−S)_+)²] = ∫2G(u)g(u)P(S_{k−1} < k−u)du turns the simplex truncation into an integral of true lower-tail probabilities, each bounded below by 1 − β(u) with rigorous β (chord-majorised Chernoff, one-big-jump, Berry–Esseen), using only monotonicity of the true tail so grid artefacts cannot invalidate a bound [P, `r1_h2_interval_cert.md` §2 Lemmas 1–6]. **Shaped sub-exponential tails** g = e^{−(t/T_1)^κ}/(1 + At) replace the hard truncation. Against the crude closed-form bound used for all m ≥ 2 records since 2014 this recovers ≈ 1.1 units of the log k deficit, a factor ≈ 3 in k.

**Re-certification (overnight) [C].** Astra's audit correctly observed that the committed certifier is 50-digit floating point with a 1 + 10⁻³⁰ slack, not outward rounding; the JSON came from an uncommitted arb script. Repaired: an independent outward-rounded certificate (python-flint/arb at 200 bits, cross-checked with mpmath interval arithmetic plus a 2^{−150} guard band) gives the exact rational lower bound 8.013326752751306578613695503115…, bit-for-bit the historical float. **Dropping Berry–Esseen entirely** (Chernoff + chord + Markov only): M_{15,856} ≥ 8.00677408008999 > 8 and M_{923,601} ≥ 12.00263034990571 > 12. The H₂ and H₃ records therefore rest on Maynard plus Bombieri–Vinogradov and nothing else.

*Not claimed.* H₂ ≤ 145,226 via k = 13,476 with Deligne-strength equidistribution (a cap normalisation was reconstructed but not verified verbatim against Polymath 8b).

### 15. Walls and doors for H₁

**Five walls [P, `prime_gap_survey.md`].** (1) No post-processing of Maynard–Tao output beats the tuple diameter H(k_min). (2) The scalar decode f(m) = 2m/θ is exactly optimal (convex-order two-point counterfeit kills matrix, inertia and moment decodes). (3) The weight cone is closed: rank-r sums of squares decouple; the matrix-Maynard SDP has a rank-one optimiser. (4) Parity: the kill-graph is bipartite iff killable; floors H₁ ≥ 6, k ≥ 2m+1. (5) Level wall: the well-factorable levels 4/7, 3/5, 5/8 are structurally unusable by classical Maynard–Tao; usable-restricted frontier 11/21, ½ + 1/40, 10/19.

**Theorem 15.1 (signed no-gain) [P].** Write w = w_+ − w_−. With the decode debt D(w) = Σ_{w(n)<0}|w(n)|(m − ν(n))_+ charged at face value, the pointwise identity (ν − m) + (m − ν)_+ = (ν − m)_+ gives

  S_2 − mS_1 − D(w) = Σw_+(ν − m) − Σw_−(ν − m)_+ ≤ Σw_+(ν − m).

Every signed weight is dominated by its own positive part: the variational half of the "remove the square" programme is empty. Positivity's second job is to make the problem bounded (‖w‖_1 = S_1). Diagnostics on an exact finite microcosm show the apparent phase transition at β* = 2.0973249209 is a normalisation artefact. What remains is purely arithmetic: debt below face value through an exceptional character (Zhang), or weights evaluable when w_+ is not (Iwaniec's λ^±). The missing estimate (E_θ) is a tuple-residue well-factorable estimate; its conditional price list is H₁ ≤ 130, 114, 94, 80 at θ = 4/7, 7/12, 3/5, 5/8, and H₂ ≤ 58,058 at 4/7 [C].

**The doors [C].** k = 49 → H = 240, k = 47 → 226. Pure M_49 ∈ [3.891257590916, 3.97290] (closed by the classical upper bound); ε-variant M_{49,1/35} certified ≥ 3.930490592 (float 3.959325169) against threshold 4; upper bounds close the ε-door only for ε ≤ 0.00682.

### 16. Below 186 [O]

Astra's rounds on the 2026 preprint (`prime186*.md`) reconstruct the actual mechanism (enlarged coefficient support with rootwise dense-divisibility predicates f(p)g(p) = p³, shared primes allowed; an exact integer example Y = 10, D = 330, E = 455 where the merged modulus is triply densely divisible although E alone is not) and prove a finite complementary-support allocation frontier [P]. The k = 39 obstruction: a 39-element admissible tuple of diameter 182 exists [C]; the cap-only Ritz quotient reaches 0.9944678 (< 1 needed) after a 78-dimensional extension generated by the full signed cap operator (certified outside the old 77-dimensional trial space), and the k = 40 margin improves to 24.866 ppm with a certified restoration credit. **No gap below 186 is claimed.** The five walls above and the signed no-gain theorem say where the door is not.

---

## Part V. Method, errata, and open problems

### 17. How the programme worked, and what it caught

Every deliverable was produced by a proposer agent and attacked by at least one refuter whose instruction was to find a false step; repairs were made in place with the failure recorded, and the files were then cross-reviewed by the other model (Astra's intake reviews of Fable; Fable's audits of Astra's dynamic proposals). The following genuine mathematical errors were caught and fixed this way; we list them because their pattern is the most transferable finding of the programme.

| where | error | who caught | fix |
|---|---|---|---|
| Theorem B stiffness | mean-value bound used the wrong endpoint | Astra | S* (endpoint max), Theorem B′ |
| CUE Prop 5.5 | reversed inequality 1/N < 64/L³ | Astra | split at 2πN^{1/3}; 4086/4087 |
| F3 operator | "‖Φ‖ = ∞" from raw particle number | Astra | mass-weighted CS; ‖K‖ ≤ 15.27 |
| F3 commutator | scalar on fixed-mass sectors | Fable refuter | falsified (13× spread), withdrawn |
| CβE BB-LD | missing N-rescaling in sine argument | Fable refuter | re-derived; exponents unchanged |
| CβE Prop 3.1 | relative error v′ = v(1+O(1/N)) false at v ≈ 0 | Astra | crude bound + hypothesis (U3) |
| CβE status line | "[P] for β ∈ {1,2,4}" never verified | Astra | downgraded to n = 2, β = 2 |
| Level B periodised | wrap gap can be the minimising gap | Astra | downgraded to [O]; Theorem A′ stands |
| Marked-depth law | second term is the product rule | Fable review | [R]; first term standard |
| F1 Π_4 | leading coefficient 6a² vs 6a | Fable refuter | 6a; numerics were right |
| F1 refuter's probe | sign of −zz3·ε⁴ mislabelled | both | fixed, no effect on m_4 |
| H₂ certifier | committed script not outward-rounded | Astra | arb re-certification; BE-free bound |
| Fibre count N = 8 | 403 vs 399 at tighter tolerance | round 3 | exact recount pending |
| Galerkin angle | arccos((1−n^{−2})/a_n) misread | round 3 | arccos(1 − n^{−2}/a_n) |
| Round 1 claim | "0.6725 is the exact LP optimum; AH suboptimal by 0.0301" | own round 5 | retracted: feasible-set conflation |

Five apparent "phase transitions" (β-kink, ℓ¹ ramp, unboundedness at β = 1, ρ ≈ 1.72, the median → s*) were normalisation artefacts. When an idea uses only static polynomial information about a moment-frozen family, it fails; the escapes were stopping times, rational observables, and marks.

### 18. The status ledger in one table

| result | tag | file |
|---|---|---|
| Root dynamics; two-body solution; Theorem A; Theorem C(i) | P | `depth_scaling_theorem.md` |
| Fibre dimensions; centre-of-mass family; diagonal flow | C / P | `impostors_paper.md`, `r1_structure_review.md` |
| Forward-flow protected moments (Astra); force-energy factor 2 | P | `dynamic_generator.md`, `force_energy.md` |
| Theorem E1 chiral blindness | P + C | `r1_structure_review.md` §5 |
| ACUE exact law N ≤ 10; CUE law to N = 256; β = 1, 4 | C | `impostors_paper.md` §1.3–1.4 |
| Theorem B′ with S*; window lemma; Corollary 5.4 | P | `r1_theoremB_repair.md` |
| P(δ_min > LN^{−4/3}) ≤ 4086/L³; P(S* > MN²) ≤ 4087 M^{−1/2} | P | `r1_cue_background.md` |
| CUE depth law N^{8/3}D ⇒ G²/8 | P modulo (E-B*) / Astra isolation lemma modulo gap law | `r1_cue_background.md`, `yau_flow*.md` |
| CβE exponents N^{−2−2/(β+1)} | P modulo (U3), Feng–Wei | `r1_cbe_background.md` |
| ρ_∞ = O(1) for ACUE all N; s* as a theorem | O | — |
| LR exchange rate μ ≤ √(2μ_Λ)/π | P modulo reverse comparison | `impostors_paper.md` §1.5 |
| Theorem A′; Level B ⟹ μ < ½ under (NR); λ* = 0.4719538 | P / C | `r1_levelB_barrier.md` |
| W_AH ∈ (0.06239, 0.06240); 1/16 refutes AH-pairs | P under RH | Astra round 7 |
| Rounds 8–28 arithmetic reductions | P (each), target O | Astra `dyson_round*.md` |
| δ_MT closed form; Galerkin; five method theorems; M_− payoffs | P | `round3_synthesis.md`, `final_verified_paper.md` |
| Sharp pair LP ≈ 0.679; "0.6818287" not the LP | C / R | `r1_simple_zeros.md` |
| Residual-Gram saturation; margins; F3 λ_∞ ≈ 4.6456; ‖K‖ ≤ 15.27 | P / C | Astra `residual_gram_*`, `r2_diagonal_operator_spectrum.md` |
| H₂, H₃, H₄ records; BE-free H₂/H₃ certificates | P + C | `H2_H3_record_announcement.md`, `r1_h2_interval_cert.md` |
| Five walls; signed no-gain; price list | P / C | `prime_gap_survey.md`, `signed_sieve_nogo.md` |
| 186 mechanism; k = 39 frontier | P / C, gap O | Astra `prime186*.md` |
| RH, Montgomery, μ = ½, AH refutation, sub-186 | O | — |

### 19. Open problems, ranked by (probability of a theorem) × (size)

1. **The signed prime-correlation lower bound** in Astra's frequency-two / two-scale formulation (§9): one inequality, under RH, refutes AH-pairs. Everything else on the zeta side has been reduced to it.
2. **Window stability (E-B*)** for the Fable route, or a priority check and write-up of Astra's isolation lemma as the CUE depth theorem; then the general-β hypothesis (U3) via Pfaffian/Jack formulas at n = 3.
3. **ρ_∞ = O(1) for ACUE at all N**, and s* = 1.419640342 as a theorem (single dislocation in the infinite clock, Calogero–Moser framing).
4. **The M_− lemma** ‖(c^{−1}Â)_−‖ ≤ M_− uniform in T: +0.007 to +0.012 on 0.6725 with tr³ at bandwidth one; and the five-line Lean edit for N_d ≥ 0.8362503·N + p.
5. **The continuum triple-correlation LP** and an exact identification of the sharp bandwidth-one pair ceiling (≈ 0.679).
6. **The wall λ_max ≤ π²/2** for the true arithmetic residual-Gram operator, or a counterexample; the M2/M3 arithmetic transfer.
7. **(E_θ)** for any θ > ½ (cheapest 7/12): the one statement between the price list and H₁ ≤ 114.
8. **k = 49 ε-door** (Galerkin d = 20–22, ε ∈ [1/40, 1/30]); SHELL-M49; tuple k = 35,265 below 396,504.
9. **A non-wrap witness** for periodised Level B; the interference-code / phase-rigidity conjecture for the fibre; the d* = 3(N−3) kill-degree law.
10. **Formalisation:** discharge the Lean obligations; formalise the records' certificate chain.

### 20. Closing

The single methodological sentence of the programme is *moment matching does not imply stopping-time matching*: a first-passage time sees what an infinite list of frozen moments cannot, and on the random-matrix side this is now a theorem up to a cited extreme-gap law. The single mathematical lesson is less comfortable: transferring any of it to the zeros of ζ requires exactly the arithmetic input — a signed correlation of primes at the scale of one zero spacing — that has been the obstruction since Montgomery, and the programme's contribution there is to have made the missing inequality explicit to five decimal places rather than to have proved it. The prime-gap records, by contrast, are unconditional, machine-certified, and now independent of every probabilistic constant.

---

## References (primary sources used; "recalled" where not re-read during the programme)

Ben Arous, G., Bourgade, P.: Extreme gaps between eigenvalues of random matrices. Ann. Probab. 41 (2013). · Bombieri, E. (1965); Vinogradov, A.I. (1965). · Conrey, J.B., Ghosh, A., Gonek, S.M.: Simple zeros of the Riemann zeta-function. Proc. LMS 76 (1998) (recalled). · Erdős, L., Schlein, B., Yau, H.-T. et al.: arXiv:0905.4176, 0911.3687. · Feng, R., Wei, D.: Small gaps of circular β-ensemble. Ann. Probab. 49 (2021) (recalled). · Inoue, S.: arXiv:2604.05733 (as described by Astra; not read by Fable). · Killip, R., Nenciu, I.: Matrix models for circular ensembles. IMRN (2004). · Lagarias, J.C., Rodgers, B.: Higher correlations and the alternative hypothesis. Q. J. Math. 71 (2020). · Maynard, J.: Small gaps between primes. Ann. of Math. 181 (2015). · Montgomery, H.L.: The pair correlation of zeros of the zeta function (1973). · Polymath, D.H.J.: Variants of the Selberg sieve. Res. Math. Sci. 1 (2014); Polymath 15 (2019). · Rodgers, B., Tao, T.: The de Bruijn–Newman constant is non-negative. Forum Math. Pi (2020). · Rudnick, Z., Sarnak, P.: Zeros of principal L-functions and random matrix theory. Duke (1996). · Stadlmann, J.: arXiv:2309.00425. · Tao, T.: The alternative hypothesis for unitary matrices (blog, 2019). · OpenAI: Improved short gaps between primes (2026 preprint) and the PrimeGaps186 repository. · Anthropic: zeta-23-lean (2026).
