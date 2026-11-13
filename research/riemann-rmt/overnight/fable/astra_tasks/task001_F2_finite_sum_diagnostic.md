# FABLE task 001 / item F2 — bounded finite-sum diagnostic for the symmetric-prime trial

**Status: finite numerical check (plus one derivation sketch). Nothing here is a proof of the arithmetic transfer, and nothing here is a theorem about zeta zeros.**

Written 2026-09-05 by Fable (Claude Code) for GPT-6 Astra's task
`tasks/FABLE_001_SYMMETRIC_PRIME_TRANSFER.md`, section "Independent bounded finite-sum cross-check".
Input commit (read-only mirror in `astra_inputs/`): `97df092427a1035cf1c66dc712148ccccac09ac2`
(QingyunSun/Riemann-hypothesis-and-random-matrix, branch `codex/astra-research`).
Intended new-repo path: `research/fable/task001_F2_finite_sum_diagnostic.md`, scripts `research/fable/task001/`.

Primary source status: a single fetch of `https://arxiv.org/html/2604.05733v1` was attempted and refused
by the network egress proxy (`EGRESS_BLOCKED: arxiv.org`); the `abs` page is on the same blocked host.
**Every statement about Inoue's Theorems 2 and 4 below is "(as described by Astra; paper not read)".**
All other citations are marked "(recalled; not verified online)".

Result labels used: **[exact algebra]**, **[certified continuum integral]** (Astra's rational
certificate; I did not re-certify), **[numerical continuum integral]** (my floating quadrature of the
stipulated schema), **[finite numerical check]**, **[arithmetic asymptotic, sketch]**, **[open]**.

---

## 0. Summary

1. **[finite numerical check] Conventions cross-validated.** My matrix-free operator reproduces Astra's
   `arithmetic_operator.py` values λ_max(K_L) = 3.9492871367 (L=10³), 4.1058670454 (10⁴),
   4.2052553801 (10⁵) to all ten printed digits (eigsh residuals 1e-15, 5e-15, 2e-13).
2. **[numerical continuum integral] Continuum values reproduced independently.** A different simplex
   parametrisation gives J = −0.014662375473371 for the fixed rational trial (Astra's certified
   enclosure [−0.014662375473368995, −0.014662375473368974]; difference 1.6e-15) and
   J = −0.015357981703850 for the degree-14 one-variable optimum (difference 2e-16). New continuum values:
   mass-only f(v) at ℓ=16/15: **−0.0215652589**; H≡1 at ℓ=16/15: **−0.0333607118**; H≡1 at ℓ=1
   (x_n = n^{−1/2}): **−0.0307564823**. Quadrature orders 40/64 agree to 3e-15.
3. **[finite numerical check] Finite margins of the fixed vectors** (operator exactly as specified, all
   prime powers, all m), J_L for the fixed trial: −0.05199 (10³), −0.04312 (10⁴), −0.03763 (10⁵),
   −0.03392 (10⁶), −0.03124 (10⁷; beyond spec). The gap to the continuum value −0.01466 shrinks
   slowly: (J_L − J_∞^{cont})·log L = −0.258, −0.262, −0.264, −0.266, −0.267.
4. **[finite numerical check] The drift is not specific to the S2 feature.** H≡1, mass-only, and the
   degree-14 one-variable trial show the same shape and size of drift (all (J_L − J^{cont})·log L ≈ −0.26
   to −0.29). The *S2 gain* J_L(fixed) − J_L(mass-only) is +0.01043, +0.00986, +0.00943, +0.00910,
   +0.00884 (10³…10⁷) against the continuum gain +0.006903; it decreases monotonically toward it.
5. **[finite numerical check, diagnostic only] Three-point fits.** J_L = J_∞ + c/log L on (10³,10⁴,10⁵)
   gives J_∞ = −0.01615 (fixed); adding c′/log²L gives J_∞ = −0.01446; on (10⁴,10⁵,10⁶) the two-term
   fit gives −0.01470. The two-term fit on (10⁴,10⁵,10⁶) *predicts* the out-of-sample L=10⁷ value to
   3e-6 (predicted −0.0312390, measured −0.0312416). The same two-term extrapolation lands within
   2e-4 of the respective continuum value for all five trials. **This is consistent with, but cannot
   prove, the stipulated continuum schema being the limit of the finite operator on these vectors.**
   Three or five points on a function varying like 1/log L determine no limit; the one-term fits are
   1.5e-3 off and the "clean" operator (item 6) shows how badly a different sub-sum extrapolates.
   L = T (log L/log T = 1) is not a permitted finite instance of the theorem (as described by Astra;
   paper not read): the product cutoff is L ≤ T/(log T)², and a finite-L vector cannot be frozen as
   T → ∞.
6. **[finite numerical check] Coincidence terms are large at accessible L.** Removing the prime powers
   e ≥ 2 from A lowers J_L(fixed, 10⁶) from −0.0339 to −0.0715; additionally removing insertions of p
   into backgrounds m with p | m ("clean" operator, the exact combinatorics assumed by the continuum
   schema) lowers it to −0.0923. These are relative corrections of size ≈ c/log L with c of order 1
   (measured (J_full − J_clean)·log L = 0.52, 0.64, 0.74, 0.81, 0.86 for 10³…10⁷, still rising).
   Consequently the finite-L numbers cannot decide whether M3 "already accounts for all leading
   diagonal coincidences" (Astra's question 2): at L ≤ 10⁷ the coincidence terms are 10–20 % of
   ⟨x,K_L x⟩ and are not in any asymptotic regime. Their leading-order vanishing is argued heuristically
   in §6 (prime-power and p|m terms carry an extra factor ≈ Σ_p log p/p² or Σ_p log p/(p(p−1)) divided
   by log L) but is **[open]** as a proved statement with the short-background range included.
7. **[arithmetic asymptotic, sketch] The S2 moments do follow from the weighted integer sum**, not
   only from a Poisson–Dirichlet model: a marked Euler product identity **[exact algebra]** plus the
   Selberg–Delange theorem (recalled; not verified online) gives, for the d_ℓ(n)²/n-weighted integers
   n ≤ L^v, cumulative moments a v²/((a+1)(a+2)) and a(a+6) v⁴/((a+1)(a+2)(a+3)(a+4)), whose v-derivative
   ratios are exactly Astra's E_v[S] = v²/(a+1) and E_v[S²] = (a+6)v⁴/((a+1)(a+2)(a+3)). The finite
   check shows slow convergence: weighted-mean ratios 1.014, 1.023, 1.028, 1.030, 1.031 (mean S2) and 1.203,
   1.174, 1.152, 1.135, 1.121 (mean S2²) for L = 10³…10⁷. §7 gives the derivation and its hypotheses.
8. **[finite numerical check] Background norm.** N(L) = Σ_{n≤L} d_ℓ(n)²/n divided by the recalled
   Selberg–Delange leading term C_ℓ (log L)^a/Γ(a+1) is 1.1090, 1.0816, 1.0652, 1.0544, 1.0466 for
   10³…10⁷, i.e. (ratio − 1)·log L = 0.7528, 0.7516, 0.7511, 0.7509, 0.7507: a clean 1/log L correction with a
   stable constant, unlike the operator pieces.
9. **[finite numerical check] The fixed trial is nearly the finite Perron vector.** Its Rayleigh
   quotient is 98.97 %, 99.46 %, 99.69 %, 99.80 % of λ_max(K_L) at 10³…10⁶ (λ_max at 10⁶ from Astra's
   table). The continuum-designed vector is already close to the best possible finite-L vector at this
   boundary, so no finite-L vector in this family can cross π²/2 at these L.
10. **[open] What is not established:** the leading arithmetic evaluation of M2 (two insertions with
    the H-shifts (v,S) → (v+u, S+u²)) as an asymptotic of the integer sums, the error after normalising
    by the resonator norm including v → 0, and the rate at which the coincidence terms vanish. The
    finite data are *consistent* with the schema for all tested vectors and give no counterexample.

---

## 1. Definitions and implementation (independent of Astra's scripts)

Script: `astra_tasks/task001/f2_finite_sum.py` (nothing imported from `astra_inputs/`; the scripts there were read
only to match conventions).

* φ = 1/2, ℓ = 16/15, a = ℓ² = 256/225. `d_ℓ(p^e) = ℓ(ℓ+1)…(ℓ+e−1)/e!`, multiplicative.
  **Arithmetic: float64 throughout** (d_ℓ, S2, logs). The float64 sieve was checked against exact
  `fractions.Fraction` evaluation of d_ℓ(n) for every n ≤ 10⁴: max relative error 1.52e-15.
* Sieve: primes by Eratosthenes; for each prime p and each p^e ≤ L, `d[p^e::p^e] *= (ℓ+e−1)/e`
  (cumulative product gives d_ℓ(p^e) for p^e ∥ n); `S2[p::p] += (log p/log L)²` once per prime
  (distinct primes only, as specified).
* v_n = log n/log L, r(n) = d_ℓ(n)·H(v_n, S2(n)), x_n = r(n)/√n, n = 1…L.
* Operator, matrix-free: for every prime power q = p^e ≤ L (all e ≥ 1),
  `(Ax)[q·m] += w_q x[m]` for m ≤ L/q with `w_q = 2 sin((π/2) log q/log L)/(e√q)`, implemented as one
  strided numpy slice per q; Aᵀ likewise. nnz(A) = 2 877 (10³), 31 985 (10⁴), 343 614 (10⁵),
  3 626 619 (10⁶) — identical to Astra's nnz counts — and 37 861 249 (10⁷).
* J_L = (‖Ax‖² + ⟨x, A(Ax)⟩)/(2π²⟨x,x⟩) − 1/4, and K_L = AᵀA + (A² + (Aᵀ)²)/2, whose Rayleigh
  quotient at x is 2π²(J_L + 1/4) **[exact algebra]** (for real x, ⟨x,K_L x⟩ = ‖Ax‖² + ⟨x,A²x⟩).
* Trials: `fixed` (H = f + g·S2, Astra's f, g), `massonly` (H = f), `one` (H ≡ 1), `deg14` (ℓ =
  1.1762950385645021, H = Σ_j c_j √(2j+a) P_j^{(0,a−1)}(2v−1) with c_j from Astra's
  `variational-results.json`, degree-14 entry), and an extra row `one_ell1` (ℓ = 1, H ≡ 1, x_n = n^{−1/2}).
* Operator modes (diagnostics): `full` = as specified; `nopp` = primes only (e = 1); `clean` = primes
  only and insertion of p into m only when p ∤ m. In `clean` mode ‖Ax‖² and ⟨x,A²x⟩ contain exactly the
  configurations the continuum schema models (two distinct new primes, or one new prime on each side).
* Decomposition: ‖Ax‖² = D + O with D = Σ_q w_q² Σ_{m≤L/q} x_m² (q₁ = q₂ diagonal, the finite analogue of
  M3) and O the off-diagonal part (analogue of the second M2 term); C2 = ⟨x,A²x⟩ (analogue of the first
  M2 term). Each is reported divided by 2π²⟨x,x⟩ next to M3/I, M2b/I, M2a/I.

Continuum script: `astra_tasks/task001/f2_continuum.py`. Gauss–Jacobi in v (weight v^{a−1}); inserted masses written
u = στ, w = σ(1−τ), σ = (1−v)s, Jacobian (1−v)² s, Gauss–Legendre in s, τ (this differs from both
`prime_feature_variational.py` and `original_inoue_probe.py`). E_v[S], E_v[S²] and the shift rule
(v,S) → (v+u, S+u²) exactly as stipulated.

Drift script: `astra_tasks/task001/f2_drift_fit.py` (fits, decomposition tables, prime-sum test).

---

## 2. Cross-validation against `arithmetic_operator.py` [finite numerical check]

eigsh (`which='LA'`, v0 = ones, tol 1e-12) on my LinearOperator K_L:

| L | my λ_max(K_L) | Astra | my margin λ/(2π²) − 1/4 | Astra margin | residual ‖Kx − λx‖ |
|---:|---:|---:|---:|---:|---:|
| 10³ | 3.9492871367 | 3.9492871367 | −0.0499267764 | −0.0499267764 | 1.3e-15 |
| 10⁴ | 4.1058670454 | 4.1058670454 | −0.0419943455 | −0.0419943455 | 4.6e-15 |
| 10⁵ | 4.2052553801 | 4.2052553801 | −0.0369592737 | −0.0369592737 | 2.0e-13 |

Threshold at this boundary: π²/2 = 4.9348022. Conventions (prime-power weight 1/e, factor 2, sin at
φ = 1/2, θ = log L/log T = 1) therefore agree.

## 3. Continuum values of the stipulated schema [numerical continuum integral]

| trial | ℓ | I | M2a | M2b | M3 | J = M/I − 1/4 | Astra |
|---|---:|---:|---:|---:|---:|---:|---|
| fixed (f + g·S2) | 16/15 | 0.997681 | 0.074755 | 0.075633 | 0.084403 | **−0.014662375473371** | certified ⊂ [−0.014662375473368995, −0.014662375473368974] |
| mass-only f | 16/15 | — | — | — | — | **−0.021565258857** | — |
| H ≡ 1 | 16/15 | 1/a | — | — | — | **−0.033360711847** | — |
| H ≡ 1 | 1 | 1 | — | — | — | **−0.030756482296** | — |
| degree-14 optimum | 1.17629504 | — | — | — | — | **−0.015357981703850** | −0.015357981703850554 (floating) |

(Full piece tables are in `f2_continuum_results.json`.) The certificate is Astra's; my number only
shows that an independently parametrised quadrature of the same stipulated form agrees to 1.6e-15.
Nothing about the arithmetic meaning of the form is tested by this agreement.

## 4. Finite margins J_L of the fixed vectors [finite numerical check]

Operator exactly as specified (`full`). Continuum value in the last column.

| L | fixed (f+g·S2) | mass-only f | H≡1, ℓ=16/15 | H≡1, ℓ=1 | degree-14 |
|---:|---:|---:|---:|---:|---:|
| 10³ | −0.0519926 | −0.0624271 | −0.0757862 | −0.0721550 | −0.0521013 |
| 10⁴ | −0.0431175 | −0.0529804 | −0.0660752 | −0.0626498 | −0.0436240 |
| 10⁵ | −0.0376302 | −0.0470595 | −0.0599583 | −0.0566769 | −0.0383148 |
| 10⁶ | −0.0339176 | −0.0430127 | −0.0557633 | −0.0525863 | −0.0346862 |
| 10⁷ (beyond spec) | −0.0312416 | −0.0400738 | −0.0527097 | −0.0496106 | −0.0320506 |
| continuum | −0.0146624 | −0.0215653 | −0.0333607 | −0.0307565 | −0.0153580 |

Same vectors, primes only (`nopp`) and coincidence-free (`clean`):

| L | fixed nopp | fixed clean | mass-only nopp | mass-only clean | H≡1 nopp | H≡1 clean | deg-14 nopp | deg-14 clean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10³ | −0.1022309 | −0.1269461 | −0.1086167 | −0.1327861 | −0.1202985 | −0.1452729 | −0.0983082 | −0.1203483 |
| 10⁴ | −0.0892650 | −0.1129781 | −0.0960455 | −0.1192720 | −0.1080466 | −0.1319965 | −0.0867461 | −0.1086689 |
| 10⁵ | −0.0793054 | −0.1015971 | −0.0864525 | −0.1083494 | −0.0986198 | −0.1211548 | −0.0779362 | −0.0991244 |
| 10⁶ | −0.0715145 | −0.0922927 | −0.0789299 | −0.0994034 | −0.0911774 | −0.1122071 | −0.0710042 | −0.0912065 |
| 10⁷ | −0.0653055 | −0.0846320 | −0.0729053 | −0.0920092 | −0.0851868 | −0.1047752 | −0.0654226 | −0.0845744 |

Rayleigh quotient of the fixed trial relative to the finite optimum: λ(x_fixed)/λ_max(K_L) =
0.98967 (10³), 0.99460 (10⁴), 0.99685 (10⁵), 0.99799 (10⁶, λ_max = 4.2738969 from Astra's table). The
degree-14 one-variable optimum gives 0.98913, 0.99217, 0.99364, 0.99444.

## 5. Drift diagnostic [finite numerical check; fits are diagnostic only]

Fits of J_L = J_∞ + c/log L (one-term, least squares) and J_∞ + c/log L + c′/log²L (two-term; exact on three
points). Natural logarithms.

| series | points | one-term J_∞ | two-term J_∞ (c, c′) | continuum |
|---|---|---:|---|---:|
| fixed, full | 10³,10⁴,10⁵ | −0.016153 | −0.014464 (−0.278, +0.129) | −0.014662 |
| fixed, full | 10⁴,10⁵,10⁶ | −0.015539 | −0.014701 (−0.273, +0.104) | −0.014662 |
| fixed, full | 10⁵,10⁶,10⁷ | — | −0.014764 (−0.271, +0.094) | −0.014662 |
| fixed, full | all five (least squares) | −0.015777 | −0.014609 (−0.275, +0.118) | −0.014662 |
| mass-only, full | 10⁴,10⁵,10⁶ | −0.023117 | −0.021585 (−0.310, +0.190) | −0.021565 |
| H≡1 (ℓ=16/15), full | 10⁴,10⁵,10⁶ | −0.035186 | −0.033383 (−0.325, +0.224) | −0.033361 |
| H≡1 (ℓ=1), full | 10⁴,10⁵,10⁶ | −0.032502 | −0.030830 (−0.316, +0.207) | −0.030756 |
| degree-14, full | 10⁴,10⁵,10⁶ | −0.016846 | −0.015472 (−0.278, +0.170) | −0.015358 |
| S2 gain (fixed − mass-only), full | 10⁴,10⁵,10⁶ | +0.007577 | +0.006884 (+0.037, −0.086) | +0.006903 |
| fixed, clean | 10³,10⁴,10⁵ | −0.064798 | −0.033572 (−0.990, +2.39) | −0.014662 |
| fixed, clean | 10⁴,10⁵,10⁶ | −0.051600 | −0.025166 (−1.165, +3.28) | −0.014662 |
| fixed, J_full − J_clean | 10⁴,10⁵,10⁶ | +0.036061 | +0.010465 (+0.892, −3.17) | 0 (if coincidences are lower order) |

Out-of-sample test of the expansion form: the two-term fit on (10⁴,10⁵,10⁶) predicts J_{10⁷}(fixed, full)
= −0.0312390; measured −0.0312416 (error 2.6e-6); the one-term fit predicts −0.0313031 (error 6.2e-5). The same test on the `clean` series fails by 1.7e-4 (two-term) and 2.2e-3 (one-term).

Plain statement. These fits cannot prove the limit: (i) a function of the form J_∞ + c/log L + c′/log²L +
c″/log³L + … with |c″| of order 1 is indistinguishable from the two-term form on L ≤ 10⁷
(1/log³L ≈ 2.4e-4 at 10⁷, the same size as the observed agreement); (ii) the `clean` sub-sum, which has
the *same* claimed limit if the coincidence terms are lower order, extrapolates to −0.025…−0.065
depending on the points used; (iii) log L/log T = 1 is the boundary of the admissible range (as described
by Astra; paper not read) and L = T is not a permitted finite instance; a vector optimised at one
finite L cannot be frozen as T → ∞. What the fits do show: on every tested vector the finite operator
as specified drifts toward the value of the stipulated schema with a leading 1/log L coefficient
c ≈ −0.27 to −0.33 (in J units), and the S2 gain drifts toward the schema's gain.

Prime-sum discretisation (why c is of order 1): for the S2-moment kernel G(u) = a u²(1−u)^a,
Σ_{p≤L} G(log p/log L)/p divided by ∫₀¹ G(u) du/u is 0.8448, 0.8900, 0.9193, 0.9387 for 10³…10⁶, i.e.
(ratio − 1)·log L ≈ −1.07, −1.01, −0.93, −0.85. Replacing prime sums by ∫ du/u costs O(1/log L) with
constants of order 1 (Mertens-type constants Σ_{p≤x} log p/p = log x + E + o(1), E ≈ −1.33 (recalled;
not verified online)), before any question about the operator arises.

## 6. Piece decomposition and coincidence terms [finite numerical check]

Fixed trial, each piece divided by 2π²⟨x,x⟩ (so that D + O + C2 = J_L + 1/4):

| L | D (diag) full | O (offdiag) full | C2 (A²) full | D clean | O clean | C2 clean |
|---:|---:|---:|---:|---:|---:|---:|
| 10³ | 0.08716 | 0.05950 | 0.05135 | 0.07831 | 0.02252 | 0.02222 |
| 10⁴ | 0.08753 | 0.06276 | 0.05660 | 0.08126 | 0.02809 | 0.02768 |
| 10⁵ | 0.08775 | 0.06470 | 0.05992 | 0.08314 | 0.03288 | 0.03239 |
| 10⁶ | 0.08781 | 0.06606 | 0.06221 | 0.08431 | 0.03698 | 0.03642 |
| 10⁷ | 0.08777 | 0.06709 | 0.06390 | 0.08504 | 0.04047 | 0.03986 |
| continuum | M3/I = 0.08460 | M2b/I = 0.07581 | M2a/I = 0.07493 | same | same | same |

Reading: the diagonal piece D (kernel sin²(πu/2)/u, second order in the insertion weight) is already
within 4 % of M3/I and has essentially converged; the two first-order pieces O and C2 are 13–17 %
below their continuum analogues at 10⁶ and rising. In the `clean` operator O and C2 are *half* of the
full values: the terms in which an inserted prime power has e ≥ 2 or divides the background carry about
half of the first-order mass at L = 10⁶ — a consequence of the d_ℓ²/n measure giving the small primes
2, 3, 5 weight ≈ (ℓ²/p)/(1 + ℓ²/p + …) each, and of 2 sin(π log p/(2 log L)) being 0.16–0.36 for p ≤ 5
at L = 10⁶.

Heuristic size of the coincidence terms (not a proof): with x_{pm} ≈ (ℓ/√p) x_m for p ∤ m, the p | m
insertions contribute to O and C2 a relative amount of order Σ_p 2 sin(πu_p/2)/p² ≈ (π/log L) Σ_p log p/p²
≈ 1.5/log L (times an O(1) kernel factor), and the prime powers e ≥ 2 a relative amount of order
Σ_{p^e, e≥2} 2 sin(πu_q/2)/(e q) ≈ (π/log L) Σ_p log p/(p(p−1)) ≈ 2.4/log L (times an O(1) kernel factor) (constants Σ_p log p/p² ≈ 0.49, Σ_p log p/(p(p−1)) ≈ 0.755, recalled; not verified online).
Both vanish only like 1/log L, with constants that together match the measured 10–20 % at 10⁶. Whether
the exact leading term of the full integer sum contains an extra O(1) contribution from these
configurations is therefore **not decidable from L ≤ 10⁷**; the extrapolation evidence in §5 (full
operator → schema value; clean operator far away and unstable) is consistent with "no extra term", i.e.
with M3 already containing all leading diagonal coincidences, but is not evidence of the required quality.

## 7. S2 moments from the weighted integer sum [exact algebra + arithmetic asymptotic, sketch]

Let a = ℓ², F(s) = Σ_n d_ℓ(n)² n^{−s} = Π_p E_p(s), E_p(s) = Σ_{e≥0} d_ℓ(p^e)² p^{−es} (Re s > 1).

**[exact algebra]** Since d_ℓ(p)² = a, E_p(s)(1 − p^{−s})^a = 1 + O(p^{−2s}), so F(s) = ζ(s)^a G(s) with G
holomorphic and non-vanishing for Re s > 1/2, G(1) = C_ℓ := Π_p (1−1/p)^a E_p(1). For S2 taken over distinct
primes, Σ_{n : p|n} d_ℓ(n)² n^{−s} = F(s)(1 − 1/E_p(s)), hence the marked series

  Σ_n d_ℓ(n)² S2(n) n^{−s} = F(s) (log L)^{−2} Σ_p (log p)² (1 − 1/E_p(s)),
  Σ_n d_ℓ(n)² S2(n)² n^{−s} = F(s) (log L)^{−4} [ Σ_p (log p)⁴ (1 − 1/E_p(s)) + Σ_{p≠p′} (log p)²(log p′)² (1−1/E_p(s))(1−1/E_{p′}(s)) ].

These identities are exact for Re s > 1 and immediate from multiplicativity of d_ℓ(n)²: the Dirichlet
series of {n : p | n} is (E_p − 1)·Π_{p′≠p} E_{p′} = F·(1 − 1/E_p), that of {n : pp′ | n} (p ≠ p′) is
F·(1−1/E_p)(1−1/E_{p′}), and S2(n)² = Σ_{p|n} u_p⁴ + Σ_{p≠p′, pp′|n} u_p² u_{p′}². (No machine check of these
identities was run; they are one-line consequences of the Euler product.)
Moreover 1 − 1/E_p(s) = a p^{−s} + O(p^{−2s}), and Σ_p (log p)^k p^{−s} = Γ(k)(s−1)^{−k} + (holomorphic
near s = 1) for k ≥ 1 (from −ζ′/ζ and its derivatives). So near s = 1

  Σ_n d² S2 n^{−s} = (a/log²L) (s−1)^{−a−2} G(s)(1 + O(s−1)),
  Σ_n d² S2² n^{−s} = ((a² + 6a)/log⁴L) (s−1)^{−a−4} G(s)(1 + O(s−1)).

**[arithmetic asymptotic, sketch]** By the Selberg–Delange theorem (recalled; Tenenbaum, *Introduction
to analytic and probabilistic number theory*, Ch. II.5; not verified online), applied with the standard
zero-free region, Σ_{n≤y} c_n ~ (G(1)/Γ(z)) y (log y)^{z−1} for a series (s−1)^{−z} G(s) of this type, and
partial summation gives Σ_{n≤y} c_n/n ~ (G(1)/Γ(z+1)) (log y)^z. Hence, with y = L^v,

  N(y) = Σ_{n≤y} d²/n ~ (C_ℓ/Γ(a+1)) (v log L)^a,
  Σ_{n≤y} d² S2/n ~ (a C_ℓ/Γ(a+3)) v^{a+2} (log L)^a,
  Σ_{n≤y} d² S2²/n ~ ((a²+6a) C_ℓ/Γ(a+5)) v^{a+4} (log L)^a.

The v-derivatives of these three quantities are proportional to v^{a−1}, a v^{a+1}/((a+1)), and
(a+6) v^{a+3}/((a+1)(a+2)(a+3)) — i.e. the background at logarithmic mass v carries density v^{a−1} dv
(after the common factor C_ℓ (log L)^a/Γ(a) cancels) and conditional moments exactly E_v[S2] = v²/(a+1),
E_v[S2²] = (a+6)v⁴/((a+1)(a+2)(a+3)), which are Astra's stipulated (Poisson–Dirichlet(a)) moments. The
common Euler-product constant cancels in every ratio entering J. Hypotheses: a > 0 fixed, the classical
Selberg–Delange theorem as recalled, and S2 normalised by the *same* log L for all n (as in the schema).
The prime-power contributions p^{−2s} only alter the holomorphic factor, so they do not change the leading
moments; they do contribute O(1/log L) corrections, which is what the finite check sees.

Finite check (weighted cumulative moments at y = L, divided by the predicted a/((a+1)(a+2)) = 0.169618 and
a(a+6)/((a+1)(a+2)(a+3)(a+4)) = 0.036822):

| L | mean S2 ratio | mean S2² ratio | N(L)/[C_ℓ (log L)^a/Γ(a+1)] | (ratio−1)·log L |
|---:|---:|---:|---:|---:|
| 10³ | 1.01416 | 1.20345 | 1.108966 | 0.7528 |
| 10⁴ | 1.02250 | 1.17425 | 1.081599 | 0.7516 |
| 10⁵ | 1.02758 | 1.15196 | 1.065243 | 0.7511 |
| 10⁶ | 1.03016 | 1.13458 | 1.054351 | 0.7509 |
| 10⁷ | 1.03114 | 1.12058 | 1.046576 | 0.7507 |

C_ℓ computed as the product over p ≤ 10⁷: C_ℓ = 0.999124, C_ℓ/Γ(a+1) = 0.936993 (tail p > 10⁷ neglected; it is O(1/(10⁷ log 10⁷)) relatively). The second moment
converges from above at rate ≈ 1/log L; the first moment's ratio is still moving *away* from 1 at 10⁷
(competing O(1/log L) corrections of opposite sign: the +0.75/log L correction in N(L/p)/N(L) versus the
prime-sum deficit of §5). This is the expected slow convergence, not a contradiction of the asymptotic;
but it means that no finite L ≤ 10⁷ verifies the moment formulas to better than a few per cent.

## 8. What this changes for the main obligation (Astra's items 1–3) — and what it does not

* Item 1 (normalisation, Euler constant, cancellation): §7 gives the exact marked Euler product and the
  Selberg–Delange leading terms; the constant C_ℓ cancels in every ratio. The finite N(L) check confirms
  the leading term with a stable 0.751/log L first correction. This is a derivation sketch relying on a
  recalled theorem; it should be written out with the theorem's exact hypotheses before being cited.
* Item 3 (S2 moments from the integer sum): settled at leading order by §7 for the *background*
  moments used in I and M3, and for the background factor in M2. Not covered: the joint distribution of
  the background feature with the *inserted* primes when the inserted prime divides the background —
  the schema's rule S → S + u² is wrong for such configurations (S is unchanged for p | m, and S → S +
  (u/e)² for q = p^e) — and these configurations are numerically 10–20 % of the first-order pieces at
  L = 10⁶ (§6). Their asymptotic vanishing is heuristically O(1/log L) and remains **[open]** as a proof.
* Item 2 (insertion coefficients, prime powers, M3 coincidences): not decided. The finite data say the
  full operator drifts to the schema value and the coincidence-free sub-sum is far away; if the schema
  is right, the coincidence terms must be lower order *and* large at accessible L, which is exactly what
  the heuristic constants predict. A finite-sum contradiction of the schema was **not** found for any of
  the five vectors.
* The margin of every vector at every L is negative and the fixed rational trial is within 0.2 % of the
  finite Perron optimum at 10⁶; nothing here moves the half-gap boundary.

## 9. Timing and memory

Single process, `OPENBLAS_NUM_THREADS=1`, pinned to 2 cores (`taskset -c 0,1` / `-c 2,3`), Python 3.11.15,
numpy 2.4.6, scipy 1.17.1. Times are wall-clock per L for all five trials in all three modes plus the
diagnostics (eigsh included for L ≤ 10⁵):

| L | primes | prime powers | nnz(A) | total time | max RSS |
|---:|---:|---:|---:|---:|---:|
| 10³ | 168 | 193 | 2 877 | 0.1 s | 94 MB |
| 10⁴ | 1 229 | 1 280 | 31 985 | 0.5 s | 94 MB |
| 10⁵ | 9 592 | 9 700 | 343 614 | 4.2 s (eigsh 3.6 s) | 112 MB |
| 10⁶ | 78 498 | 78 734 | 3 626 619 | 9.9 s | 213 MB |
| 10⁷ | 664 579 | 665 134 | 37 861 249 | 207 s (sieve 16 s) | 1 478 MB |

The 10⁶ run took 10 s, far under the 10-minute allowance; the 10⁷ run is an extra, outside the task's
specification, included only to test the fit's out-of-sample prediction. The one-million-dimensional
eigenproblem was not run (not requested; Astra's value is used for the 10⁶ Perron ratio).

## 10. Failed attempts and things that did not work

1. Fetching the primary source: `WebFetch https://arxiv.org/html/2604.05733v1` → `EGRESS_BLOCKED`. Not
   retried on the abs page (same host). All theorem statements are as described by Astra.
2. A one-term fit J_∞ + c/log L on three points (as literally requested) gives J_∞ 1.5e-3 below the
   continuum value for every trial with residual 7e-5; fitted on (10⁴,10⁵,10⁶) it misses the 10⁷ point by
   6e-5 (the two-term fit misses by 3e-6) and is superseded by the two-term fit, which is itself only diagnostic.
3. Attempting to read the coincidence question off the finite sums by comparing `full` and `clean`:
   the difference is 0.058 at 10⁶ and its (·log L) product is still rising at 10⁷, so no asymptotic
   regime is reached; the question stays open.
4. The weighted first S2 moment does not approach its predicted limit monotonically at L ≤ 10⁷ (ratio
   1.014 → 1.031); this was first suspected to be a sign error in the PD moment and was resolved by the
   exact marked-Euler-product computation of §7 (the limit is right; the approach is slow with competing
   1/log L terms). No exact rational verification of the second-moment identity beyond the first few
   Euler factors was done.
5. No attempt was made to certify the continuum quadrature with interval arithmetic (Astra's certificate
   already does this for the fixed trial; the new continuum values for the other trials are floating only,
   with order-40/64 agreement 3e-15).

## 11. Reproduction

```text
cd research/riemann-rmt/overnight/fable/astra_tasks/task001
OPENBLAS_NUM_THREADS=1 python3 f2_continuum.py                       # 2 s  -> f2_continuum_results.json
OPENBLAS_NUM_THREADS=1 python3 f2_finite_sum.py --lengths 1000,10000,100000,1000000
                                                                      # 15 s -> f2_finite_sum_results.json
OPENBLAS_NUM_THREADS=1 python3 f2_finite_sum.py --lengths 10000000 --out f2_finite_sum_results_1e7.json
                                                                      # extra point
python3 f2_drift_fit.py                                               # -> f2_drift_fit_results.json
```
Logs: `f2_continuum_run.log`, `f2_finite_sum_run.log`, `f2_finite_sum_run_1e7.log`, `f2_drift_fit_run.log`.

## 12. Claims (for the ledger)

| id | claim | label |
|---|---|---|
| F2-1 | My matrix-free operator reproduces Astra's λ_max(K_L) at L = 10³,10⁴,10⁵ to 10 digits | finite numerical check |
| F2-2 | Independent quadrature reproduces the certified fixed-trial continuum margin to 1.6e-15 and the degree-14 value to 2e-16; new continuum values for mass-only (−0.0215653), H≡1 (−0.0333607 at ℓ=16/15; −0.0307565 at ℓ=1) | numerical continuum integral |
| F2-3 | J_L(fixed) = −0.05199, −0.04312, −0.03763, −0.03392, −0.03124 at L = 10³…10⁷, all negative; the fixed trial has 98.97–99.80 % of λ_max(K_L) | finite numerical check |
| F2-4 | Two-term 1/log L extrapolation of the full operator lands within 2e-4 of the schema value for all five vectors and predicts the 10⁷ point to 3e-6; this is diagnostic and proves no limit | finite numerical check |
| F2-5 | Prime-power and p|m coincidence terms are 10–20 % of the first-order pieces at L ≤ 10⁷ and decay no faster than 1/log L; the coincidence-free sub-sum extrapolates unstably | finite numerical check |
| F2-6 | Marked Euler product identities for Σ d² S2 n^{−s} and Σ d² S2² n^{−s} | exact algebra |
| F2-7 | Leading-order conditional moments E_v[S2] = v²/(a+1), E_v[S2²] = (a+6)v⁴/((a+1)(a+2)(a+3)) follow from the weighted integer sum via Selberg–Delange (recalled) | arithmetic asymptotic, sketch |
| F2-8 | Arithmetic transfer of the M2 insertion structure, and the vanishing of the coincidence terms after normalisation including v → 0 | open |
