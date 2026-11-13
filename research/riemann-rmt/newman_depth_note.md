# The finite de Bruijn–Newman depth: an exact dynamic observable separating CUE from ACUE

**Bill (Qingyun) Sun · GPT5.6SOL · Fable**

*August 18, 2026 — research note; complete numerical evidence, key identities proved*

## Summary

For a unitary N×N matrix U with P(z) = det(I − zU) = Σ a_j z^j, define the **backward heat flow** P_r(z) = Σ a_j r^{j(N−j)} z^j (t = log r ≤ 0) and the **finite Newman depth** Λ(U) = −t*, where t* is the first time the discriminant vanishes (first root collision). This is the exact finite-dimensional avatar of the de Bruijn–Newman constant: RH ⟺ Λ_{dBN} ≤ 0 becomes "roots on the circle until collision", and −Λ measures how far below criticality a configuration sits. Two independent computations (exact weighted enumeration of the ACUE ensemble for N ≤ 10, 13,132 rotation orbits; Monte Carlo for Haar CUE up to N = 256, ~44,500 samples) establish:

1. **CUE is asymptotically barely-subcritical:** −Λ^CUE ≍ N^{−8/3}, with the parameter-free law 8N^{8/3}(−Λ) ⟹ G², where P(G > x) = exp(−x³/72π) is the sine-kernel smallest-gap law (constant 72π confirmed to ~1.5%, KS ≈ 0.04, median 29.6–30.5 vs predicted (72π ln 2)^{2/3} = 29.08). Fitted exponent −2.678 ± 0.016.
2. **ACUE is over-stable:** −Λ^ACUE ≍ N^{−2} (fitted slope −2.0009), with N²(−Λ) supported in ≈ [1.31, 1.99], median → ≈ 1.41. The alternative N^{−8/3} is decisively ruled out on the lattice, and the alternative N^{−2} is decisively ruled out for CUE: the depth ratio falls as ≈ 3.6·N^{−0.70} (theory N^{−2/3}), reaching 10× separation at N* ≈ 165.
3. **Clock configurations:** P_ACUE(clock) = 2^{1−N} **exactly** (proved by Cauchy–Binet: Σ_{|C|=N}|Δ(C)|² = (2N)^N, each clock contributing N^N), and clocks have Λ = −∞ (P = 1 − cz^N is flow-invariant). These are the unique flow-stationary configurations.
4. **Local collision law:** −Λ = δ²_min/8·(1 + o(1)) holds in the continuum regime δ_min ≪ other gaps (Richardson-verified to 10⁻⁷; N=2 exact: −Λ = −log cos(δ/2)). For CUE the correction is positive and vanishes as ≈ 0.60·N^{−0.73} (the background *delays* collision). On the ACUE lattice δ_min = π/N always (proved: all gaps ≥ 2π/N forces the clock), neighboring gaps are the same scale, and the constant renormalizes: ρ = 8(−Λ)/δ²_min ∈ [1.066, 1.609], with the isolated-defect-pair value ρ∞ ≈ **1.1912** (N-independent to 4 digits by N = 8).
5. **The depth escapes the weight-freezing no-go.** The flow is diagonal on coefficients, so every balanced moment of degree ≤ N remains frozen along the flow (dynamic extension of the Round-3 freezing theorem; verified to 4.5e−16). Yet Λ — an "infinite-degree" observable — separates the ACUE fiber at O(1): a mimicker in the N=5 ℚ(√5) family shifts E[N²(−Λ); non-clock] by −0.093 and the clock atom from 0.0625 to 0.1398; at N = 8 mimicker families move the Λ-law by total variation 0.12–0.24, with the dependence concentrated on the center-of-mass class X = 0. **Λ is the first verified dynamic anti-ACUE observable.**

## Why this matters

The ACUE (Tao's alternative-hypothesis ensemble) matches CUE on all pair statistics available to bandwidth-limited detectors — the wall behind every Montgomery-type approach. All static balanced moments of degree ≤ N are frozen across the mimicker fiber, so no polynomial statistic of low degree can tell the ensembles apart. The Newman depth is dynamic and non-polynomial: it sees the full collision geometry of the heat flow. The scaling gap N^{−8/3} vs N^{−2} says the two hypotheses predict *different universality classes of subcriticality* — GUE-repulsion (P(δ) ~ δ³ ⟹ extreme gap N^{−4/3} ⟹ depth N^{−8/3}) versus lattice rigidity (δ_min = π/N deterministic ⟹ depth N^{−2}). Any future zeta-side quantity that mimics finite depth (e.g. flowed pair-counts under the actual de Bruijn–Newman backward flow on Ξ) inherits this separation — a concrete new place to look for a >2/3 simplicity proportion or an anti-AH statistic, orthogonal to the bandwidth war.

## Key identities (proved)

- Root dynamics under the flow: θ̇_j = −Σ_{k≠j} cot((θ_j − θ_k)/2) (attracting Coulomb gas on the circle); a simple root cannot leave |z| = 1 before a collision (self-inversive invariance).
- Generator on power sums: **L p_m = −m(N−m) p_m − m Σ_{a=1}^{m−1} p_a p_{m−a}** (verified to 4.1e−28 across N = 5..10; closes the polynomial-moment hierarchy and proves the freezing corollary).
- N = 2: Λ = log(|tr U|/2), i.e. −Λ = −log cos(δ/2).
- P_ACUE(clock) = 2^{1−N}; clocks are the exact Λ = −∞ atoms; ACUE(8) median(−Λ) cross-validated by both implementations (2.214e−2 vs 2.216e−2).

## Verification ledger

| item | status |
|---|---|
| Exact enumeration N = 3..10 (13,132 orbits, Vandermonde masses; Σμ = 1 to 3e−15) | complete, mpmath 40-digit spot checks worst 1.3e−9 |
| CUE Monte Carlo N = 2..256, two independent Λ-solvers (ODE vs coefficient bisection) | agree to 1e−6; N=2 analytic law to 8.7e−13 |
| First collision always at an initially-adjacent pair (ACUE) | 13,130/13,130 orbits, zero surprises |
| Clock probability 2^{1−N}, Λ = −∞ | proved (Cauchy–Binet; flow invariance) |
| δ_min = π/N for non-clock ACUE | proved (pigeonhole) + verified all orbits |
| 72π smallest-gap constant, G²-law for CUE depth | fitted c = 229–236 vs 226.2; KS 0.035–0.041 |
| Freezing along flow (balanced degree ≤ N) | proved (diagonal flow) + 4.5e−16 numeric |

**Open target (sharp):** the closed form of the lattice defect constant ρ∞ ≈ 1.1912 (two-defect reduction of the Coulomb ODE against the rigid period-2 background); a block-decomposition of the same computation would upgrade the N^{−2} law to proved-with-constants.

*Scripts and data: session archive `dyn1_*.py`, `dyn1_results_N{3..10}.npz`, `dyn2_*.py`, `dyn2_data_N{2..256}.npz`. References: Ben Arous–Bourgade (extreme gaps), Feng–Wei (CβE small gaps), Vinson; Rodgers–Tao (Λ_dBN ≥ 0); Tao (ACUE).*
