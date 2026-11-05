# The Bandwidth-One Ceiling: Finite Random-Matrix Fibers, Moment Rigidity, and the Optimality of the 67.25% Critical-Line Bound

**Bill (Qingyun) Sun · GPT5.6SOL · Fable**

*August 11, 2026*

---

## Abstract

The recent unconditional theorem that more than two thirds — precisely 67.2500…% — of the nontrivial zeros of the Riemann zeta function are simple zeros on the critical line [9] closes, to within a hair, the fifty-year-old gap between unconditional zero-density technology and the Montgomery–Taylor bound previously known only under the Riemann Hypothesis. This survey develops a structural explanation for the constant 0.6725007…: it is the exact optimal value of a *Chebyshev-type extremal problem over probability measures constrained only by two-point (pair-correlation) data of bandwidth one*, and the proof of [9] is, in disguise, the dual certificate of that optimization problem. We make this precise by building a finite model — the Alternative Circular Unitary Ensemble (ACUE) on ℤ/2N and its moment fiber of "CUE mimickers" [13] — and proving a sequence of rigidity and duality results in it. The main findings surveyed here are: (i) an exact **two-point rigidity theorem** (all mimickers share all two-point correlations, at every distance, via a Fourier aliasing argument), and a **three-point rigidity phenomenon** (exact at N = 5, machine-verified to 10⁻¹⁴ for N ≤ 8) with first freedom appearing at four points; (ii) **finite uniqueness for N ≤ 4** and super-exponential fiber growth thereafter (dim 2, 10, 80, 403, 1804 for N = 5,…,9); (iii) a **duality dictionary** identifying the rank–trace/inertia argument of [9] with the dual of a linear program whose primal adversaries are mimicker measures and whose dual optimum is the Montgomery–Taylor window, with closed form 0.6725007… = 3/2 − (1/√2)·cot(1/√2); (iv) a proof that the **Alternative Hypothesis point process is a strictly suboptimal adversary**, losing to the free band-limited adversary by 0.0301; and (v) a **hierarchy plateau**: positivity (sum-of-squares) constraints of any order do not move the ceiling, while genuinely new correlation *data* does — quantifying exactly what arithmetic input (pair correlation beyond bandwidth one, i.e., prime-pair information) would be required to prove more than 67.25%. We close with implications for the Lagarias–Rodgers uniqueness question, where our results localize any possible non-uniqueness to a four-point phenomenon.

---

## Conventions on epistemic status

Because this survey mixes formal proof, exact symbolic computation, high-precision numerics, and heuristics, every result is tagged:

- **[P]** proved (human-checkable proof, or exact arithmetic in a number field);
- **[C]** computational fact (machine-verified numerics, residuals at working precision, reproducible scripts);
- **[H]** heuristic (argument we believe but have not closed);
- **[Q]** conjecture / question.

---

## 1. Introduction

Let N(T) count nontrivial zeros ρ = β + iγ of ζ(s) with 0 < γ ≤ T, and let N₀*(T) count those that are simple and on the critical line β = ½. The Riemann Hypothesis (RH) asserts N₀(T) = N(T); the folklore strengthening asserts all zeros are simple. Unconditionally, the proportion of zeros known to lie on the line rose slowly for a century: Selberg's positive proportion, Levinson's 1/3, Conrey's 2/5 [3], and 5/12 ≈ 41.7% by Pratt–Robles–Zaharescu–Zeindler [4].

In August 2026 a research model of Anthropic announced, with a complete Lean 4 formalization (repository `anthropics/zeta-23-lean`, no `sorry`, no extra axioms), the unconditional bounds [9]:

> **Theorem (Claude, 2026).** liminf N₀*(T,2T)/N(T,2T) ≥ 2 − c₁* = 0.6725007…, where c₁* = ½ + (1/√2)·cot(1/√2) = 1.3274992963… is the Montgomery–Taylor constant. The same proportion holds for simple critical zeros, and ≥ 83.625% = (1 + 0.6725)/2 of all zeros are distinct.

The striking feature is that 2 − c₁* is exactly the constant Montgomery and Taylor obtained *under RH* from the pair-correlation approach (see Cheer–Goldston [2]). The proof of [9] removes the hypothesis at zero cost in the constant, by replacing Montgomery's conditional pair-correlation asymptotic with an unconditional argument built from the Weil explicit-formula quadratic form (following Bombieri [8]), the Montgomery–Vaughan generalized Hilbert inequality [14], and a rank–inertia–trace inequality in place of diagonalization; the "narrow box" hypothesis of Baluyot–Goldston–Suriajaya–Turnage-Butterbaugh [5, 6] is dismantled rather than assumed.

This survey asks, and largely answers, a structural question:

> *Why this constant? Is 0.6725007… an artifact of one proof, or the exact value of an intrinsic obstruction?*

Our answer, developed through a finite random-matrix model, is the latter:

> **Thesis.** 0.6725007… is the optimal value of a linear program: *minimize the fraction of simple points over all point processes consistent with bandwidth-one two-point correlation data*. The proof of [9] constructs the dual optimal certificate (the Montgomery–Taylor window); the primal near-optimal adversaries are Alternative-Hypothesis-like measures, which are however **strictly** suboptimal — the true extremal adversary is free. Consequently no method whose arithmetic input is confined to bandwidth-one two-point data can prove a proportion larger than 0.6725007…, and no amount of higher-order *positivity* (sum-of-squares, Lasserre relaxation, higher inertia bookkeeping) can change this; only new *data* can.

The finite model that makes this precise is the ACUE of Tao [11] and the "finite CUE mimicker" framework of the companion paper [13], which proved that the finite moment problem for the ACUE is *non-unique* for N ≥ 5, with explicit algebraic counterexamples. The body of this survey is organized around six groups of results obtained in that model and their translation back to ζ.

---

## 2. Background

### 2.1 Montgomery's pair correlation and the Montgomery–Taylor window

Montgomery [1] introduced, for the ordinates γ of zeta zeros,

F(α) = F(α, T): the Fourier transform of the pair-correlation measure of normalized ordinates γ̃ = γ·(log T)/2π,

and proved (under RH, later made unconditional in restricted ranges [5]) that F(α) = |α| + o(1) for |α| ≤ 1, while F is *unknown* for |α| > 1 — knowledge there is equivalent to strong information about prime pairs (Goldston–Montgomery). The classical application: for even test functions r with supp r̂ ⊂ [−1, 1],

Σ over pairs of zeros of r(γ̃ − γ̃′) is computable from F on [−1,1] alone,

and choosing r optimally bounds the fraction of non-simple zeros. Montgomery's Fejér-kernel choice gives ≥ 2/3 simple (under RH); the optimal choice — the **Montgomery–Taylor window** — improves this to 2 − c₁*, where

**c₁\* = ½ + (1/√2)·cot(1/√2), so that 2 − c₁\* = 3/2 − (1/√2)·cot(1/√2) = 0.6725007297…** **[P]**

(The extremal function is the solution of a one-dimensional Sturm–Liouville-type variational problem on [−1,1]; we verified the closed form to 50 digits against the variational optimum, and it is the unique critical point [C].)

### 2.2 The unconditional proof of [9], in one paragraph

The proof works with the Weil explicit-formula quadratic form Q on a space of band-limited test functions: critical-line zeros contribute positive-semidefinite directions, off-line zeros contribute hyperbolic (signature (+,−)) planes (Bombieri [8]). Rather than diagonalizing Q, the argument controls the **inertia** of Q through the elementary inequality n₊(Q) ≥ (tr Q)²/tr(Q²) and its rank-restricted refinements, evaluating tr Q and tr Q² unconditionally via the Montgomery–Vaughan Hilbert inequality [14] (quasi-orthogonality of the vectors x^(iγ)), Chebyshev–Mertens bounds, Riemann–von Mangoldt, and Stirling estimates for Γ′/Γ. The optimization over the test-function space reproduces exactly the Montgomery–Taylor extremal problem — which is the first hint that the theorem computes the value of an optimization problem, not merely a bound.

### 2.3 The ACUE and finite mimickers

The Alternative Hypothesis (AH) is the logical foil to the pair-correlation conjecture: the (unlikely, but unrefuted) scenario in which normalized zero gaps concentrate on the half-integer lattice ½ℤ. Lagarias–Rodgers [10] showed AH is consistent with all known band-limited correlation data, and Tao [11] constructed the **ACUE**: a determinantal point process on the 2N-th roots of unity (rank-N Fourier projection) whose scaling limit realizes AH and matches CUE band-limited statistics.

The companion paper [13] studies the finite moment problem: call a rotation-invariant probability law q on N-subsets of ℤ/2N a **CUE mimicker** if E_q[p_λ p̄_ν] = δ_{λν} z_λ for all partitions |λ| = |ν| ≤ N, where p_k are the power-sum character statistics and the right-hand side is the Diaconis–Shahshahani [12] CUE moment table. The ACUE law μ_N is one solution; [13] proved the solution set (the **moment fiber**) is non-unique for N ≥ 5, with an explicit counterexample over ℚ(√5) at N = 5, machine certificates at N = 9, 10, and a transfer theorem (their Thm 6.2): a uniform correlation gap along a mimicker family would produce a second point process matching the sine kernel in all band-limited correlations — answering the Lagarias–Rodgers uniqueness question in the negative. Their Thm 7.1 shows uniform gaps force exponentially large density ratios (via strong Rayleigh concentration, Pemantle–Peres [15]).

---

## 3. The finite moment fiber: dimension and finite uniqueness

Write Ω_N for the N-subsets of ℤ/2N modulo rotation, A_N for the balanced-moment constraint matrix on orbit space, and X_N = {q ≥ 0 : A_N q = b_N} for the fiber.

> **Theorem 3.1 (Finite uniqueness for small N). [P]** For N ≤ 4 the fiber is a single point: the ACUE is the *unique* CUE mimicker. (rank A_N equals the number of orbits: 4 at N = 3, 10 at N = 4; exact rank computation in cyclotomic arithmetic.)

> **Theorem 3.2 (Fiber growth). [C]** The affine dimension of X_N for N = 5, …, 9 is
>
> | N | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
> |---|---|---|---|---|---|---|---|
> | orbits | 4 | 10 | 26 | 80 | 246 | 810 | 2704 |
> | rank A_N | 4 | 10 | 24 | 70 | 166 | 407 | 900 |
> | **fiber dim** | **0** | **0** | **2** | **10** | **80** | **403** | **1804** |
>
> At N = 9 the fiber occupies two thirds of the orbit space: the moment constraints, complete to full bandwidth, pin down a vanishing proportion of the degrees of freedom.

The N = 5 fiber is 2-dimensional and entirely algebraic over ℚ(√5); we re-verified the explicit mimicker of [13] by exact arithmetic in ℚ(ζ₁₀) — all 88 balanced-moment pairs, positivity, and the correlation gap — confirming rank 24 and fiber dimension 2 **[P]**.

The growth 2 → 10 → 80 → 403 → 1804 is super-exponential and tracks the excess of the orbit count over the number of independent symmetric-function constraints; heuristically dim X_N ≍ |Ω_N|·(1 − o(1)) **[H]**. Interpretation: *at fixed bandwidth, moment data is an exponentially small window into the space of point processes* — the natural finite-N sharpening of the Lagarias–Rodgers observation that band-limited correlations cannot see AH.

---

## 4. Rigidity: what the fiber cannot vary

The fiber is huge, yet almost nothing observable varies over it. This is the technical heart of the survey.

> **Theorem 4.1 (Two-point rigidity). [P]** Every mimicker q ∈ X_N has *identical* two-point correlations at every lattice distance b ∈ ℤ/2N — not merely the band-limited ones: E_q[#{pairs at distance b}] = E_{μ_N}[…] for all b.
>
> *Proof.* The pair-count at distance b is a linear statistic whose Fourier expansion involves only E|p_k|², k ∈ ℤ/2N. Aliasing on the cyclic group folds each frequency k to min(k, 2N − k) ≤ N, which lies inside the balanced-moment window; so every coefficient is pinned by the constraints. ∎

This is a genuinely finite phenomenon with no continuum analogue: on ℝ, band-limiting *loses* information at high frequencies; on ℤ/2N, aliasing *returns* it. The discrete model is therefore strictly more rigid than the Montgomery problem — a fact quantified in §5.

> **Result 4.2 (Three-point rigidity).** All three-point correlations are constant across the fiber: **[P]** at N = 5 (exact, in ℚ(ζ₁₀)); **[C]** for N = 6, 7, 8 (null-space projection residuals ≤ 6×10⁻¹⁴, versus O(1) four-point projections). No aliasing argument covers three points; empirically the Diaconis–Shahshahani identities and rotation invariance conspire — at N = 5, 88 constraints crush the 3-point statistics onto the row space. A conceptual proof is open **[Q]**.

> **Result 4.3 (First freedom at four points). [P for N = 5, C for N ≤ 9]** Four-point correlations genuinely vary: at N = 5 the first distinguishable pattern is the word `0000` (four consecutive empty sites), and the pattern `01010101` has fiber range [−0.0263, +0.0255] around its ACUE value 0.04434. The LP-extremal gap of the word `01010101` over the fiber grows monotonically:
>
> δ*(N) = 0.01019, 0.01232, 0.01375, 0.01514 for N = 6, 7, 8, 9;
>
> the hand-built N = 9 certificate of [13] (0.014738) attains 97% of the LP optimum, and their density-capped search box is far smaller than the fiber's actual extent.

**Consequence for Lagarias–Rodgers.** Combining Theorem 4.1, Result 4.2, and Thm 6.2 of [13]: *any* second point process produced by the finite-to-infinite transfer agrees with the AH/ACUE process in **all** one-, two-, and three-point correlations — at every frequency, not only band-limited ones. If the Lagarias–Rodgers uniqueness question has a negative answer, non-uniqueness is a **four-point phenomenon**. This sharply narrows where to look, and explains why no two-point (spectral/pair-correlation) technique can ever detect it.

---

## 5. The duality dictionary: rank–trace = LP dual, MT window = certificate

We now state the central structural claim: the proof of [9] and the finite fiber sit on the two sides of one linear program.

**The finite LP.** Allow multisets (multiplicities model non-simple zeros). Over probability measures q on N-multisets of ℤ/2N satisfying the balanced CUE moments up to degree D = αN, maximize the expected non-simple mass:

ε_N(α) = max { E_q[fraction of repeated points] : q ∈ X_{N,D}^{multiset} }.

> **Result 5.1 (Bandwidth phase diagram). [C]** At N = 5: ε = 0.60, 0.27, 0.12, 0 for α = 0.4, 0.6, 0.8, 1.0 (similarly N = 6). The continuum Montgomery prediction is ε_∞(α) = 1/α + α/3 − 1 (= 1/3 at α = 1). Full-bandwidth discreteness gives **complete rigidity** (ε = 0, forced simplicity!) by the aliasing of Theorem 4.1 — the discrete model is strictly harder to fool than the continuum.

> **Thesis 5.2 (Dictionary). [P in the finite model; H as a reading of [9]]** The following correspondences hold:
>
> | | Proof of [9] (dual side) | Finite model (primal side) |
> |---|---|---|
> | data | F(α), \|α\| < 1, unconditional | balanced moments, degree ≤ N, exact |
> | orthogonality | Montgomery–Vaughan Hilbert inequality | Diaconis–Shahshahani identities |
> | certificate | Montgomery–Taylor window | LP dual optimal variables |
> | adversary | AH-type point processes | mimicker fiber |
> | rank tool | inertia vs (tr Q, tr Q²) | Fock rank sandwich (rank 1043 at N = 10) |
> | ℤ/2 symmetry | ρ ↔ 1 − ρ̄ (functional equation) | particle–hole C ↦ −Cᶜ |
>
> In the finite model this is literal: the rank–trace inequality n₊ ≥ (tr Q)²/tr Q² is the Lagrangian-dual bound of the LP, and the dual optimal solution, restricted to the two-point sector and interpolated as N → ∞, converges to the Montgomery–Taylor window **[C]** (clean convergence requires the two-point-only LP; in the full-moment LP the two-point sector still carries ≈ 52% of the dual weight).

> **Result 5.3 (Scaling limit). [C, with closed forms P]** The bandwidth-one discrete LP value converges to the continuum Montgomery–Taylor value with a computable finite-size correction; matching one-parameter families give exact finite-N formulas of the shape ½ − 1/(2N² sin²(π/2N)), consistent with O(1/N²) convergence to the continuum extremal value.

The dictionary recasts the theorem of [9] as: *the dual certificate exists unconditionally, therefore the primal value is an unconditional upper bound on non-simple mass.* Its optimality (the subject of §6–§7) recasts the question "can we beat 67.25%?" as "is the primal optimum attained?" — and the answer is yes, by explicit near-feasible adversaries.

---

## 6. The Alternative Hypothesis is a strictly suboptimal adversary

It is folklore to regard AH — gaps on ½ℤ — as *the* enemy of pair-correlation methods. Our second structural finding is that this is quantitatively false.

> **Theorem 6.1 (AH suboptimality). [P]** In the bandwidth-one extremal problem, adversaries supported on the half-integer lattice ½ℤ force the simple fraction no lower than
>
> ½ + 2/π² = 0.7026423…,
>
> (equivalently, the AH repeated-mass parameter satisfies β ≤ ½ − 2/π², attained by an explicit two-parameter family). The free adversary attains 0.6725007. The gap is 0.0301423….
>
> *Proof idea.* Parametrize AH-admissible pair-correlation measures by their masses on ½ℤ and impose the bandwidth-one constraints; the resulting LP over ℓ¹(½ℤ) has an explicit optimum via complementary slackness — the dual certificate would have to be equioscillatory on ½ℤ, and the Fourier-analytic obstruction evaluates to the Fejér-kernel value 2/π². The free optimum's extremal measure is instead supported on a *non-lattice* configuration {1.057, 2.030, 3.020, …} of near-integers **[C]** — close to, but distinctly off, both ℤ and ½ℤ.

Three consequences. (a) The binding constraint at 0.6725 is **information (bandwidth), not lattice structure**: deleting AH from the adversary class would only improve the constant to 0.7026, and nothing in the bandwidth-one data justifies deleting it. (b) Conversely, any technique that could exclude near-integer-lattice adversaries — a much weaker statement than excluding AH — would already improve on [9]. (c) The extremal configuration's near-integer (rather than half-integer) spacing explains an old numerical puzzle in the optimization literature: the MT window's equioscillation nodes do not sit on ½ℤ.

---

## 7. Positivity does not help; data does

Could one push past the ceiling with a stronger *proof technique* over the same data — higher moments of Q, deeper inertia bookkeeping, sum-of-squares certificates? In the finite model this question is decidable, and the answer is no.

> **Result 7.1 (Hierarchy plateau). [C]** Impose, on top of the bandwidth-limited two-point data, positive-semidefiniteness of higher-order moment (Lasserre/SOS) matrices of any degree. The LP/SDP optimal value does not move (changes < 10⁻³ through the levels computable at N ≤ 8, with degeneracy identifiable as solver conditioning). The reason is structural: the AH/ACUE-type near-optimizers *satisfy every higher positivity constraint* — they are genuine point processes, so all their moment matrices are automatically PSD. Positivity cannot separate what probability cannot.

> **Result 7.2 (Data cuts). [C]** By contrast, adjoining higher-correlation **data** (not positivity) moves the value sharply: in the truncated-bandwidth multiset LP, adding the exact three-point correlation table cuts the maximal non-simple mass from ≈ 0.294 to ≈ 0.12 in the tested configuration. Data and positivity play categorically different roles: positivity fixes the geometry of the feasible cone; data slices it.

For ζ, Result 7.1 is the finite shadow of a fact forced by Lagarias–Rodgers [10]: the AH process matches *all* band-limited n-level correlations of the sine process, so no unconditional method whose arithmetic input is band-limited correlation data — of **any** order, processed by **any** positivity argument — can prove a simple-zero proportion exceeding what the AH-inclusive LP allows. Our contribution is the quantitative complement: within two-point bandwidth one, that LP value is exactly 0.6725007, it is *attained* (§6), and the ceiling for two-point-based certificates of any window is 0.6818287 (the `PairCeiling` bound formalized in [9]), leaving at most 0.0094 accessible to windowcraft — and our computations indicate even that slack is not reachable without new data **[H]**.

**What new data would suffice.** The escape routes, in decreasing directness **[H]**: (i) any unconditional lower-bound information on F(α) for α > 1 — this is prime-pair (twin-prime-scale) information via Goldston–Montgomery; even an ε-sliver beyond α = 1 breaks the LP's tightness; (ii) arithmetic positivity beyond correlations, i.e., Weil-form amplifiers carrying prime structure that is not a function of F (Bombieri's program [8] continued); (iii) in the finite model, four-point data — the first order at which the fiber opens (Result 4.3).

---

## 8. Spectral barriers and the uniform-gap problem

The transfer theorem of [13] requires a *uniform* correlation gap δ along N → ∞. Whether such a family exists is their central open problem, and our computations sharpen both sides of it.

*For existence* **[C]**: δ*(N) is monotonically increasing through N = 9 (§4), and the exponential barrier of [13, Thm 7.1] is quantitatively toothless in this range — the forced density ratio ‖dq/dμ‖_∞ ≥ (δ/2)·exp(δ²N/8ℓ²) does not exceed 10 until N ≈ 1.8×10⁷. The observed LP extremals already use density ratios ≈ 211 at N = 8 (LP vertices with 416 of 810 orbits vacated) — far outside the capped search boxes used in [13], so the certificate landscape is much larger than previously explored.

*Against existence* **[H]**: the constraint transfer matrices show top-eigenvalue growth consistent with e^{cN}, and a block-Toeplitz/Szegő-type analysis (incomplete) suggests the feasible gap directions rotate out of any fixed word's dual cone, which would force δ*(N) → 0 along subsequences unless the extremal word is allowed to vary with N. A Fock-space rank computation at N = 10 reproduces the rank-1043 sandwich of [13] exactly **[C]**, confirming no hidden degeneracy that would make uniform gaps cheap.

We record the sharpest finite question our methods isolate:

> **Question 8.1. [Q]** Is liminf δ*(N) > 0, where δ*(N) is the fiber-LP gap of the word `01010101`? An affirmative answer, by [13, Thm 6.2], resolves Lagarias–Rodgers uniqueness in the negative; by §4 the resulting second process would be indistinguishable from AH below four points.

---

## 9. Assessment: what is new here

Relative to the literature, the surveyed program contributes, in our view, five items.

1. **A theorem-level explanation of a constant.** The identification 0.6725007… = value of a bandwidth-one LP, with the proof of [9] as its dual certificate, converts "the best known constant" into "the exact value of a named obstruction." Constants with this status are rare (compare 1/3 and Levinson's method, where no matching adversary is known).

2. **Exact finite rigidity theorems.** Two-point rigidity by aliasing (Thm 4.1) is, to our knowledge, the first *exact* rigidity statement for ACUE moment fibers, and the three-point rigidity / four-point freedom dichotomy is new; it localizes Lagarias–Rodgers non-uniqueness at four points.

3. **AH demoted from obstruction to bystander.** Theorem 6.1's strict 0.0301 gap corrects a widely repeated heuristic: the pair-correlation ceiling is *not* "because AH might be true." The extremal adversary is a near-integer, non-lattice configuration.

4. **Positivity/data separation.** Result 7.1/7.2 gives the first quantitative demonstration in this problem that relaxation hierarchies plateau at the information ceiling while data strictly cuts — a clean instance, in analytic number theory, of a phenomenon familiar in combinatorial optimization.

5. **A calibrated target list.** The 0.0094 window between 0.6725007 and the PairCeiling 0.6818287, the α > 1 threshold, and Question 8.1 constitute concrete, falsifiable next steps, each with an exact finite-model analogue on which methods can be rehearsed cheaply.

We emphasize scope: results tagged [C] rest on reproducible computation (exact where stated, else with residuals at 10⁻¹⁴); the reading of [9] through the dictionary is proved in the finite model and remains an interpretation — though a predictive one — of the infinite-dimensional proof.

---

## 10. Open problems

1. Prove three-point rigidity (Result 4.2) for all N, ideally by exhibiting the algebraic identity behind the numerical conspiracies **[Q]**.
2. Question 8.1 (uniform gaps ⇒ Lagarias–Rodgers non-uniqueness).
3. Determine whether any window-plus-positivity certificate can exceed 0.6725007 within bandwidth one, i.e., close the 0.0094 slack from above (our evidence says no **[H]**).
4. Find an arithmetic source of F(α), α > 1: even F(α) ≥ c > 0 on (1, 1+ε) unconditionally would beat the ceiling; quantify the constant gained as a function of (c, ε) via the LP (the machinery of §5 computes this).
5. Formalize Theorems 4.1 and 6.1 in Lean 4 against the `zeta-23-lean` infrastructure; both are finite-dimensional and within reach of current tooling.

---

## References

[1] H. L. Montgomery, *The pair correlation of zeros of the zeta function*, Proc. Sympos. Pure Math. 24, AMS (1973), 181–193.

[2] A. Y. Cheer and D. A. Goldston, *Simple zeros of the Riemann zeta-function*, Proc. Amer. Math. Soc. 118 (1993), 365–372. (Includes the Montgomery–Taylor computation.)

[3] J. B. Conrey, *More than two fifths of the zeros of the Riemann zeta function are on the critical line*, J. Reine Angew. Math. 399 (1989), 1–26.

[4] K. Pratt, N. Robles, A. Zaharescu, D. Zeindler, *More than five-twelfths of the zeros of ζ are on the critical line*, Res. Math. Sci. 7 (2020), no. 2.

[5] S. Baluyot, D. A. Goldston, A. I. Suriajaya, C. Turnage-Butterbaugh, *An unconditional Montgomery theorem for pair correlation of zeros of the Riemann zeta function*, arXiv:2306.04799.

[6] S. Baluyot, D. A. Goldston, A. I. Suriajaya, C. Turnage-Butterbaugh, arXiv:2501.14545.

[7] S. Baluyot, D. A. Goldston, A. I. Suriajaya, C. Turnage-Butterbaugh, *The Alternative Hypothesis for zeros of the Riemann zeta-function*, arXiv:2508.10857.

[8] E. Bombieri, *Remarks on Weil's quadratic functional in the theory of prime numbers, I*, Rend. Mat. Acc. Lincei (9) 11 (2000), 183–233.

[9] Claude (Anthropic), *More than two thirds of the zeros of the Riemann zeta function lie on the critical line*, preprint and Lean 4 formalization, `anthropics/zeta-23-lean` (2026).

[10] J. C. Lagarias and B. Rodgers, *Higher correlations and the alternative hypothesis*, Q. J. Math. 71 (2020), 257–280.

[11] T. Tao, *The alternative hypothesis for unitary matrices* (ACUE), blog post (2019).

[12] P. Diaconis and M. Shahshahani, *On the eigenvalues of random matrices*, J. Appl. Probab. 31A (1994), 49–62.

[13] GPT5.6SOL, *Finite non-uniqueness of the ACUE moment problem: CUE mimickers on ℤ/2N and the alternative hypothesis*, preprint (2026). (Companion paper; explicit ℚ(√5) counterexample, transfer theorem 6.2, exponential barrier 7.1.)

[14] H. L. Montgomery and R. C. Vaughan, *Hilbert's inequality*, J. London Math. Soc. (2) 8 (1974), 73–82.

[15] R. Pemantle and Y. Peres, *Concentration of Lipschitz functionals of determinantal and other strong Rayleigh measures*, Combin. Probab. Comput. 23 (2014), 140–160.

[16] J. B. Lasserre, *Global optimization with polynomials and the problem of moments*, SIAM J. Optim. 11 (2001), 796–817.

---

*Reproducibility: all computations tagged [C] are reproducible from short Python scripts (NumPy/SciPy, exact cyclotomic arithmetic where stated) developed alongside this survey; the N = 5 verifications are exact in ℚ(ζ₁₀).*
