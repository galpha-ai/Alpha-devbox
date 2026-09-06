# Refutation report — Task B (discriminant–force identity)

**Refuter, 6 September 2026.** Target: `push_B_discriminant_force.md` (+ `push_B_check.py`).
Independent script: `refute_B_discriminant_force.py` (log `refute_B_discriminant_force.log`, ~2 min; sections R1–R9).
Statuses as in the programme: [P] proved, [C] computed, [O] open.

## 0. Verdict in one screen

**Overall: minor issues. No [P] claim is false; two proofs contain a wrong-direction / wrong-factor step that does not
affect the conclusion; one [P] tag is an overclaim; one "empirical observation" is shown to be a lattice artefact by an
explicit off-lattice counterexample; one [C] claim can be upgraded to [P].**

| # | proposer's claim | status after review | where |
|---|---|---|---|
| 1 | ΣV² = Q − C_N; F′ = −A; F″ = −A′ | **holds** — re-derived by hand (both proofs), and re-verified through the exponential polynomial with *analytic* s-derivatives (no finite differences) at N = 3, 4, 5: 8·10⁻¹⁶ / 2.5·10⁻¹⁵, Im(disc′/disc) < 10⁻³⁰ | R1 |
| 2 | A′ = Σc_ij(V_i−V_j)² ≥ 0, gradient-ascent reading | holds; **but "d²E/ds² = 4∇EᵀH∇E = VᵀHV = A′/4" is off by a factor 2** — correct is E″ = 8∇EᵀH∇E = 2VᵀHV = A′/2, as F = −2E and F″ = −A′ require. Numerically E″/(A′/2) = 1 to 10⁻⁶ | R2, §1.1 |
| 3 | E_CUE F′(0) = −C_N, E_ACUE F′(0) = −C_N/2 | holds (algebra rechecked; enumeration reproduces) | — |
| 4 | exponential-polynomial structure, w_m ≤ N²(N−1)/2 | holds (sympy N = 3, 4, 5: max w_m = 8, 20, 40 vs bounds 9, 24, 50) | R1 |
| 5 | Riccati bound D ≥ (1/C_N)log(1 + C_N/A₀) | **theorem holds**, but the step "V_a − V_b ~ 4/g → ∞ (Theorem A's bracket is non-negative)" has the **inequality backwards**: Theorem A gives V_a − V_b ≤ 2cot(g/2). The correct reason A → ∞ is F(D⁻) = −∞ with F′ = −A and A monotone. | R7, §1.2 |
| 5 | "sharp in the near-clock regime" | **misleading**: D/bound → 2(N²−1)/(3N) (fastest mode) and larger for slower modes, i.e. off by a factor ≍ N even in the logarithmic regime | R8, §1.3 |
| 5′ | κ_N numerics ≈ 0.6N² | reproduced to 4 digits; extended: G_max/N² = 0.628, 0.632, 0.635 at N = 16, 24, 32 (not yet saturated) | R4 |
| 5″ | D ≥ 1.054·(2/N²)log(1 + N²/(2A₀)) on ACUE, "no mechanism" | **the inequality without the 1.054 is false off the lattice** (min ratio 0.971 at N = 4 random; explicit N = 3 counterexample), and there *is* a mechanism: D − (1/κ)log(1 + κ/A₀) = (δ⁴/128)(κ − G) + O(δ⁶). The 1.054 is a lattice artefact of δ_min = π/N | R3, §2 |
| 6 | midpoint family closed form, D = (2/M)artanh(1/M) | holds — closed form re-verified against a **Sylvester-resultant determinant** (no root finding) to 10⁻⁴⁸; depth re-verified with the independent `heat_depth.py` tracker at N = 101, 201 (1.7·10⁻⁹) | R5 |
| 6 | "first collision" [C] N ≤ 40 | **provable in five lines** (sign alternation, §3); "near the endpoint it follows from concavity of sin" is misattributed — concavity gives the wrong direction | R5, §3 |
| 6 | local ΔF(τ) closed form | holds; Richardson at N = 512…4096 converges to the closed form at rate 1/N² (7.6·10⁻⁸ at τ = 0.25, 2.6·10⁻⁴ at τ = 1.9); non-uniform near τ = 2 as stated | R6 |
| 6′ | ACUE 3-block + hole additivity tagged **[P]** | **overclaim**: the "O(1)-per-root bookkeeping" is a heuristic at s = 0, not a perturbation estimate along the flow; numerics support O(1/N) on compacts of (0, 2) only; should be [C] | §1.4 |
| 10 | side observation N = 12: N²D = 2.0000177 > 2 | confirmed by the existing 50-digit polyroots recheck (`push_C_verify_N12run8.log`: 2.00001772004931) | — |

Everything in `push_B_check.log` reproduces bit-for-bit on re-run (9.5 s).

## 1. Errors and gaps in the [P] parts

### 1.1 Factor-2 slip in the gradient-ascent remark (§3 of the deliverable)

Text: "d²E/ds² = 4∇EᵀH∇E = VᵀHV = ¼Σc_jk(V_j−V_k)² = A′/4".
With E′ = 2|∇E|² one has E″ = 2·2∇Eᵀ H θ′ = 4∇EᵀH(2∇E) = 8∇EᵀH∇E = 2VᵀHV = A′/2. This is forced by the
proposer's own F = −2E and F″ = −A′. Verified [C] (R2): along DOP853 trajectories at N = 4, 6, 9,
|E″ − A′/2|/(A′/2) ≤ 1.1·10⁻⁶ (4th-order differences), |E′ − A/2|/(A/2) ≤ 5·10⁻¹¹. Harmless (Theorem 3.1 is proved directly).

### 1.2 Wrong-direction inequality in the proof of Theorem 6.1

Text: "At a collision of a pair with gap g, V_a − V_b ~ 4/g → ∞ (Theorem A's bracket is non-negative), so A → ∞ as s ↑ D."
Theorem A states g′ = −(V_a − V_b) ≥ −2cot(g/2), i.e. **V_a − V_b ≤ 2cot(g/2)**: the background bracket *reduces*
V_a − V_b, so the parenthetical argues the wrong way. R7 (pair at ±0.15 in a 7-clock background, N = 8) shows
V_a − V_b − 2cot(g/2) = −2.45, −2.22, …, −0.08 < 0 all the way to s = 0.999D. The conclusion A → ∞ is nevertheless
true: disc(P_s) is continuous with disc(P_D) = 0, so F(D⁻) = −∞; F′ = −A with A non-decreasing (Theorem 3.1) forces
A(s) → ∞. With this replacement the proof is complete. (A cluster collision also has V_a − V_b ≍ c/g with c ≠ 4, e.g.
c = 3 for the symmetric triple, so "~ 4/g" is not general either.) [P] status of Theorem 6.1 stands.

### 1.3 "Sharp in the near-clock regime" is off by a factor ≍ N

Text (§6.1): "it is sharp in the near-clock regime in the sense that D → ∞ like (1/C_N)log(C_N/A₀) as A₀ → 0."
Linearising θ′ = −V at the clock gives growth rates δ(N−δ) (the proposer's own remark), so a perturbation of size ε in
the fastest mode has D ≈ (4/N²)log(1/ε) + O(1) = (2/N²)log(1/A₀) + O(1), and D/[(1/C_N)log(C_N/A₀)] → 2C_N/N² =
2(N²−1)/(3N); slower modes give up to C_N/(2(N−1)) = N(N+1)/6. R8: ratios 2.43, 2.46, 2.47 at N = 4 (limit 2.5) and
3.75, 3.80, 3.83 at N = 6 (limit 3.89) for ε = 10⁻², 10⁻³, 10⁻⁴. So only the log-dependence is captured; the constant
is wrong by a factor growing linearly in N. Not an error in a theorem, but the sentence should be withdrawn or
qualified.

### 1.4 The [P] tag on additivity in §7.3 is an overclaim

"the force energy is additive, A(s) = A_block + A_hole + O(N log N) … hence F − F(0) = ΔF_block + ΔF_hole + o(1)
[P, by the O(1)-per-root bookkeeping above]". The bookkeeping is valid at s = 0 (forces superpose exactly there:
V_j = f_e(j) − f_h(j), cross term Σ_j f_e f_h = O(N log N)). Along the flow nothing is proved: the hole's O(1) far field
shifts the block roots by O(τ/N²), and the block's response near its triple collision is singular (a_block ~ 3/(2−τ)),
so an O(1/N) error needs a genuine perturbation estimate, uniform only on compact subsets of (0, 2). The numerics
(residual 0.004–0.012 at N = 127, exactly half of N = 63) support O(1/N) on τ ≤ 1.5, i.e. [C]. Note also that
"F = F_block + F_hole + O(1/N)" cannot hold near τ = 2: at the true ACUE collision τ_N = 2 − 1.34/N² the left side is
−∞ while ΔF_block = 3log(1.34/N²) + O(1) is finite.

Also in §7.2: "a(τ) := lim A(s)/N² = −ΔF′(τ)" interchanges a limit and a derivative without comment. It is
justified — F is concave in s (Theorem 3.1), concave functions converging pointwise have converging derivatives at
every point where the limit is differentiable — but the sentence should say so.

### 1.5 Misattributed step in Theorem 7.1

"near the endpoint it follows from concavity of sin": concavity of sin on [0, π] gives sin(Nφ/2) ≤ (N/(N−2))sin((N−2)φ/2),
an *upper* bound on the bracket, which cannot exclude bracket = 0 for λ < N/(N−2). What actually excludes a collision
near the endpoint is the expansion ρ(φ) = N/(N−2) − η/3 > λ = N/(N−2) − η (which the proposer also states). See §3
for a complete proof of the global claim.

## 2. Counterexample: the "empirical inequality" of §6.2 is a lattice artefact

**Claim under test** (row 5″, "recorded as an observation only"): on ACUE, D ≥ 1.054·(2/N²)log(1 + N²/(2A₀)), and
"we have no mechanism for it".

**Expansion [P].** Take a pair at ±δ/2 with background x_3, …, x_N and let G(x) = 2 + 3σ − 4β² − 2Σv_k² be the
proposer's close-pair limit of (A′ − A²)/A. With S₀ := −lim_{g→0} g⁻¹Σ_k[cot(x_a^k/2) − cot(x_b^k/2)] = σ/2,
g′ = −2cot(g/2) + gS₀ + O(g³) + O(gN⁴δ²) (the last term is the background's drift over a time O(δ²)), so
D = δ²/8 + (1/3 + σ/2)δ⁴/64 + O(δ⁶). With A₀ = 8/δ² + K + O(δ²), K = 2β² − 4/3 − 2σ + Σv²,
(1/κ)log(1 + κ/A₀) = δ²/8 − Kδ⁴/64 − κδ⁴/128 + O(δ⁶). Subtracting,

  **D − (1/κ)log(1 + κ/A₀) = (δ⁴/128)(κ − G(x)) + O(δ⁶).**

Hence every background with G(x) > κ violates D ≥ (1/κ)log(1 + κ/A₀) for small δ. For κ = N²/2 such backgrounds
exist for all N ≥ 3 (the proposer's own κ_N > N²/2), the simplest being N = 3 with the third point opposite: G = 5 > 9/2.

**Numerics [C] (R3).** Points (−δ/2, δ/2, π), depth by 30-digit root bisection:

| δ | D/bound(N²/2) | (D − bound)/δ⁴ | predicted −1/256 |
|---|---|---|---|
| 0.8 | 0.98424 | −0.003358 | −0.003906 |
| 0.3 | 0.99727 | −0.003832 | −0.003906 |
| 0.1 | 0.99969 | −0.003898 | −0.003906 |

At N = 4, 5, 6 with the G-maximising backgrounds (G = 9.282, 14.847, 21.693): (D − bound)/δ⁴ = −0.00998, −0.01822,
−0.02860 at δ = 0.1 against predicted (N²/2 − G)/128 = −0.01002, −0.01833, −0.02885. Random configurations: min
D/bound(N²/2) = 0.981, 0.971, 0.981 at N = 3, 4, 5; the N = 3 grid minimum is 0.975 at gaps (2.50, 1.28, 2.50).
The Riccati bound with C_N (Theorem 6.1) is never violated (min 1.0005 on the N = 3 grid, 1.008 random N = 4).

**Consequences.** (i) The stable constant 1.0546–1.0576 on ACUE is explained by δ_min = π/N being bounded below on
the lattice: the violation mechanism needs N²δ² → 0. (ii) Any bound of the form D ≥ (1/κ)log(1 + κ/A₀) valid for
all configurations requires κ ≥ sup_x G(x) ≈ 0.63N² (R4: 0.6345N² at N = 32); together with the proposer's
κ_N ≤ C_N this pins the sharp universal Riccati constant to [sup G, C_N] and shows the [O] target "κ_N ≤ cN²" cannot
be met with c < 0.63. (iii) The expansion is an independent check, through the depth itself, of the proposer's
close-pair formula for (A′ − A²)/A.

## 3. Upgrade: the midpoint family's first collision is the triple one [P]

P_s(z) = z^N − λz^{N−1} + λz − 1 = (z − 1)G(z), G(z) = z^{M} + 1 + (1 − λ)(z + z² + … + z^{M−1}), M = N − 1.
On |z| = 1, g_λ(x) := e^{−iMx/2}G(e^{ix}) = 2cos(Mx/2) + (1 − λ)sin((M−1)x/2)/sin(x/2) is real. At x_k = 2πk/M,
1 ≤ k ≤ M−1: sin((M−1)x_k/2) = sin(πk − πk/M) = (−1)^{k+1}sin(πk/M), so

  **g_λ(x_k) = (−1)^k(1 + λ)**, and g_λ(0) = 2 − (λ−1)(M−1), g_λ(2π) = (−1)^M g_λ(0).

For 1 ≤ λ < N/(N−2) = (M+1)/(M−1), g_λ(0) > 0, so g_λ alternates strictly in sign at x_0 < x_1 < … < x_M = 2π and
has at least M zeros in (0, 2π). G has exactly M roots, so all of them are simple, on the unit circle, and ≠ 1.
Hence P_s has N distinct roots on the circle for every λ < N/(N−2): no collision precedes the triple one at
λ = N/(N−2), and D = log(N/(N−2))/(N−1) = (2/M)artanh(1/M) exactly, for every N ≥ 3. ∎
(R5 checks g_λ(x_k) = (−1)^k(1+λ) to 10⁻¹³ for N up to 4000; `heat_depth.HeatDepth` reproduces D at N = 101, 201 to
1.7·10⁻⁹.) With this, "lim M²D = 2" for the midpoint family is unconditionally [P].

## 4. What was re-verified and holds

* Lemma 2.1 (both proofs), Theorem 2.2, Corollary 2.3, Theorem 3.1: algebra rechecked line by line; R1 confirms
  F′ = −A and F″ = −A′ *without finite differences* (analytic derivatives of Σ c_m a^{e(m)} e^{sw_m}, 40 digits,
  s = 0, 0.3D, 0.7D, N = 3, 4, 5), and Im(disc′/disc) < 10⁻³⁰ (the phase of disc is flow-invariant, as claimed).
* Section 4: CUE and ACUE lattice sums, N² − S_N² = 2Σ(N−m)(1 − cos mθ), the odd-d csc⁴ sum N²(N²+2)/3 — all rechecked.
* Proposition 5.1 (isobaric weight N(N−1), q_m ≥ N²(N−1)/2 by Cauchy–Schwarz).
* Theorem 6.1's algebra (λ_max ≤ tr, Riccati comparison, N = 2 exactness A′ = A² + 2A).
* Close-pair expansion of A, A′ (re-derived: A = 8/g² + K, A′ = 64/g⁴ − (16/3 + 8σ)/g²), the doubled-clock value
  (N² + 4N − 6)/3, κ_3 = 5.
* Theorem 7.1: closed form vs Sylvester determinant 10⁻⁴⁸ (N = 3…12); triple zero; φ_max; D expansion.
* Theorem 7.2: all expansions; positivity of w cot(w/2) − τ; a(0) = 1; a ~ 3/(2−τ); root-sum identity
  v_j = u_j/(u_j² − w²); Richardson at N up to 4096 (R6).
* §7.3: a_hole(0) = (N−1)(N−2)/3 exactly, midpoint A₀ = N² − 3N + 2 exactly, ACUE [4]-family A₀/N² = 1.3061, 1.3169,
  1.3330, 1.3333 at N = 7, 9, 63, 127 (R9).
* All ACUE ratios of §5/§6 (R3 re-implemented from the npz fields; minimisers are the single dislocation [1,2,…,2,3]).

## 5. Summary for the orchestrator

1. No [P] statement is false; the deliverable's theorems survive.
2. Two proof defects: E″ = A′/2 not A′/4 (§3 remark); Theorem 6.1's "A → ∞" justification uses Theorem A backwards —
   replace by F(D⁻) = −∞ + monotonicity of A.
3. "Sharp near the clock" is wrong by a factor 2(N²−1)/(3N) or worse.
4. §7.3 additivity should be [C], not [P]; the O(1/N) is not uniform up to τ = 2.
5. The "empirical" D ≥ 1.054·(2/N²)log(1 + N²/(2A₀)) is lattice-specific: off-lattice the inequality (even without
   1.054) fails, with the exact mechanism D − bound(κ) = (δ⁴/128)(κ − G) + O(δ⁶); the universal Riccati constant must
   be ≥ sup G ≈ 0.63N².
6. The first-collision [C] for the midpoint family is a five-line [P] (sign alternation), making lim M²D = 2 unconditional.
7. κ_N/N² keeps rising past 0.6 (0.635 at N = 32); the N = 12 side observation is confirmed at 50 digits.
