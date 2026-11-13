# Bringing the finite theorems back to GUE versus AH

*What transfers to Tao's infinite-volume framework, what collapses, and what the half-lattice forces. Fable, 13 November 2026, for the programme of Bill (Qingyun) Sun with GPT-6 Astra. Companion to `NEW_RESULTS.md` and `TAO_BRIEF.md`.*

## 0. The answer in eight lines

1. Tao's ACUE(N) is the finite model; its infinite-volume limit is the AH process: the discrete sine process at half filling on ℤ, scaled to the half-lattice (1/2)ℤ and given a uniform shift. CUE(N) has the sine process (GUE statistics) as its limit. Everything below is stated for these two limits and for windows of L consecutive points.
2. The heat-flow depth transfers, and becomes *sharper* in the limit: under AH the windowed depth converges almost surely to the deterministic constant π²/8, under GUE it converges almost surely to 0 (Theorem 2). The constant π²/8 is the two-body collision time of an isolated pair at gap one half; the minimiser over the AH support at every finite N is exactly "longest run plus one isolated dimer", and its limit is π²/8 to four digits.
3. For the zeta function the depth criterion is *equivalent* to the small-gap criterion, and slightly weaker: a window with depth below π²/8 − ε must contain a gap below one half, and a window with a gap below λ* ≈ 0.472 has depth below π²/8 (Theorem 3). So on the axis "GUE versus AH" the depth adds nothing to counting gaps; the frontier remains a positive proportion of gaps a fixed margin below one half, just past Durkan and Pearce-Crump.
4. The content of the finite theorems lives on the other axis, *inside* the alternative world: the depth law of lattice processes (floor π²/8, exact constants 2 and C*, the domain wall) and the N = 11 fact that it is not a function of the gap law.
5. Montgomery's band |α| < 1 is exactly the Nyquist band of the half-lattice. On the half-lattice the structure measure is 2-periodic, so Montgomery's theorem already forces the *entire* pair correlation of every simple-point alternative to be F_AH, band-edge atoms included (Proposition 4, the infinite-volume form of the Nyquist conservation law). Impostors differ from AH only in third and higher correlations outside the band.
6. The explicit (N − 3)-parameter impostor family (tilts by functions of det U²) is a holonomy effect: its coupling to local patterns of width three vanishes to machine precision and its width-four coupling decays geometrically in N. In the infinite-volume limit the whole family *is* the AH process.
7. Whether the AH process is the unique stationary half-lattice process with the sine process's band-limited correlations of all orders is the right open question in Tao's framework. Linear programming over the positive fibre at N = 6, 7, 8, 9 shows that every occupation pattern of three consecutive sites is forced exactly, patterns out to two mean spacings are pinned to within 2·10⁻³, and the depth law is free over an interval of width 0.2 that grows with N: impostors are locally AH, and what the fibre frees is global first-passage information (§5).
8. Theorem A is the finite form of the Csordas–Smith–Varga Lehmer-pair bound, and "only the clock survives the collapsing flow forever" is the finite form of Newman's conjecture Λ ≥ 0 in the Rodgers–Tao local-equilibrium picture (Remark 6).

## 1. Dictionary

**Scaling.** Eigenangles θ ∈ [0, 2π) with mean spacing 2π/N; scaled position x = Nθ/2π with mean spacing 1. The ACUE support (π/N)ℤ becomes (1/2)ℤ.

**Limits.** ACUE(N) is the orthogonal-polynomial ensemble of the monomials 1, z, …, z^{N−1} on the uniform measure on the 2N-th roots of unity, hence determinantal with the Dirichlet kernel K_N(x, y) = (2N)^{−1} Σ_{k<N} ζ^{k(x−y)}. As N → ∞ the kernel converges to the discrete sine kernel at density one half, K(x, y) = e^{iπ(x−y)/2} sin(π(x−y)/2)/(π(x−y)) on ℤ, whose process we scale by one half and shift uniformly: this is the AH process. CUE(N) converges to the sine process. Both limits are stationary, determinantal with kernels decaying at infinity, hence mixing (cross terms of the correlation determinants vanish as blocks separate), and every finite pattern has positive probability (kernels restricted to finite sets have spectrum strictly inside (0, 1), so Janossy densities are positive).

**The flow.** With τ = N² s the root dynamics θ̇_j = −Σ cot((θ_j − θ_k)/2) becomes, for fixed scaled positions, dx_j/dτ = −(2π²)^{−1} Σ_k (x_j − x_k)^{−1} + O(N^{−2}): the attractive logarithmic-gas (Calogero) flow. Two isolated points at distance g satisfy d(g²)/dτ = −2/π², so they collide at τ = π²g²/2; at g = 1/2 this is π²/8.

**The windowed depth.** For a configuration X and a window [U, U + L), wrap the points of X in the window onto a circle of circumference L (angles θ = 2πx/L) and let D_L(X) be the depth of that circle configuration in the scaled time τ = L² s. Theorem A reads: if all gaps in the window are ≥ h then D_L ≥ −L² log cos(πh/L) ≥ π²h²/2, whatever the number of points.

**Protected algebra = Rudnick–Sarnak band.** The trace p_k = Σ e^{ikθ_j} = Σ e^{2πi(k/N)x_j} is the Fourier mode at frequency α = k/N cycles per mean spacing. A balanced moment of positive weight K = Σ k_i ≤ N is a test function with Σ|ξ_i| = 2K/N ≤ 2: exactly the Rudnick–Sarnak band Σ|ξ_i| < 2 in which the n-level correlations of zeta zeros are known. The Nyquist row k = N is the Montgomery band edge α = 1.

## 2. The depth dichotomy

**Theorem 2 (depth dichotomy).**
(i) [P] For every configuration on the half-lattice other than the full clock, and every window and L, D_L ≥ π²/8. (Theorem A with h = 1/2; the clock, which is the lattice ℤ + U of spacing one, has D = ∞.)
(ii) [P, proof sketch below] If a window contains a pair at gap g whose other points all lie at distance ≥ ℓ ≥ 2 from the pair (distances in mean spacings), then D_L ≤ (π²g²/2)(1 + 1/(2ℓ) + O(ℓ^{−2}) + O(L^{−2})).
(iii) For the AH process, lim_{L→∞} D_L = π²/8 almost surely. For the sine process, lim_{L→∞} D_L = 0 almost surely; for CUE(L) the quantitative law is L^{8/3}s-depth ⇒ G²/8, P(G > x) = exp(−x³/72π) (Theorem 3.10 of `NEW_RESULTS.md`), equivalently P(D_L > t) = exp(−(π²L/72)(8t/π²)^{3/2})(1 + o(1)) and P(D_L > π²/8) = exp(−π²L/72)(1 + o(1)).

*Proof of (iii) from (i), (ii).* AH: the lower bound is (i). For the upper bound, an isolated dimer (two adjacent occupied sites with 2ℓ empty sites on each side) is a finite pattern, so it has positive probability under the discrete sine process and, by ergodicity, occurs in almost every realisation inside every long enough window; (ii) with g = 1/2 gives limsup D_L ≤ (π²/8)(1 + 1/(2ℓ)) for every ℓ. GUE: for every ε > 0 a pair at gap < ε isolated at distance ≥ 2 is a positive-probability pattern of the sine process, so it occurs almost surely in long windows, and (ii) gives limsup D_L ≤ (π²ε²/2)(1 + 1/4). ∎

*Proof sketch of (ii).* Write g for the pair's angular gap and x_k for the angular distances to the other points. By Lemma 3.1, g′ = −2cot(g/2) − Σ_k [cot(x_a^k/2) − cot(x_b^k/2)], and by the mean value theorem each bracket has modulus ≤ (g/2) csc²(ξ_k/2) ≤ 2g/x_k² (1 + O(x_k²)). With x_k ≥ 2πℓ_k/L and Σ_k ℓ_k^{−2} ≤ 4/ℓ for points at distances ≥ ℓ on both sides (density at most two on the half-lattice, and the same bound with another constant for a density-one background), g′ ≤ −4/g + g(1/6 + 2L²/(π²ℓ)) so (g²)′ ≤ −8 + 2g₀²(1/6 + 2L²/(π²ℓ)) with g₀ = 2πg_scaled/L, which integrates to the stated bound. During the collapse the pair's neighbours recede rather than approach: the force on a neighbour from its own side dominates the pull of the pair by a factor of order ℓ log L, so the isolation is not lost. [The displacement bookkeeping is routine and is not written out here.] ∎

**Numerical confirmation.** The minimiser of N²D over the whole ACUE support at N = 4, …, 12 is in every case the gap pattern [1^{N−3}, a, 1, b] with a + b = N + 2 (units π/N): a run of N − 2 consecutive sites and one isolated dimer diametrically opposite. Its scaled depth, certified in ball arithmetic (`overnight/fable/scripts/dimer_limit.py`), is

| N | 12 | 16 | 24 | 32 | 48 | 64 |
|---|---|---|---|---|---|---|
| N²D | 1.30318 | 1.28779 | 1.27113 | 1.26231 | 1.25314 | 1.24841 |

and the fit N²D = c₀ + c₁/N + c₂/N² gives c₀ = 1.23382 against π²/8 = 1.23370, with c₁ = 0.96 and c₂ = −1.6 when c₀ is fixed at π²/8 (maximum residual 4·10⁻⁵). The dimer density under ACUE, E#{gaps = 1}/N = 0.2947, 0.2957, 0.2962 at N = 8, 10, 12, converges to the discrete-sine value P(two adjacent sites occupied)·2 = 1/2 − 2/π² = 0.29736, so dimers are a positive fraction of all AH gaps and the pattern in (iii) is not exotic. On the GUE side, Monte Carlo over Haar-distributed CUE(N) with the same ball-arithmetic classification (`overnight/fable/scripts/cue_depth_mc.py`) gives

| N | 12 (4000 samples) | 24 (2000) | 48 (600) |
|---|---|---|---|
| P(N²D > π²/8) | 0.277 | 0.073 | 0.005 |
| asymptotic exp(−π²N/72) | 0.193 | 0.037 | 0.0014 |
| P(N²D > 1/2) | 0.692 | 0.466 | 0.227 |

so the event that is certain under AH has probability decaying exponentially in the window length under GUE, with the asymptotic rate π²/72 per point approached from above.

**What the dichotomy says.** The depth is a hard-core detector. Its separation between the two worlds is driven entirely by the minimum gap: one half on the AH side, arbitrarily small on the GUE side. It is not a pair-correlation statistic and does not use Montgomery–Dyson at all. The nontrivial part of the depth, the distribution of D_L − π²/8 at finite L and the exact constants of §3.7 of `NEW_RESULTS.md`, is a statement about *which* lattice configurations are present, that is, about the alternative world's internal structure.

## 3. What this means for the zeta function

Let a window be L consecutive zeros near height T in the usual scaling γ log T/2π, and D its τ-depth.

**Theorem 3.** (a) [P] Assume RH and AH-pairs (the pair-correlation measure is supported on (1/2)ℤ, Lagarias–Rodgers). For every fixed L and ε > 0 the proportion of windows at height ≤ T with D < π²/8 − ε tends to 0 as T → ∞. (b) [P/C] A positive proportion of windows with D < π²/8 − ε refutes AH-pairs. Conversely a positive proportion of gaps below λ* = 0.4719538 (the threshold gap of Proposition 3.13 of `NEW_RESULTS.md`, computed for a clock background and ≈ 0.47 for a random background) produces a positive proportion of such windows.

*Proof.* (a) By Theorem A, D < π²/8 − ε forces a gap below 1/2 − ε′ in the window; each gap lies in at most L windows; under AH-pairs the proportion of gaps below 1/2 − ε′ is o(1). (b) The first sentence is the contrapositive of (a). The second is Theorem 2(ii) together with the threshold computation. ∎

So, as a tool for refuting the alternative hypothesis on the zeta function, the depth is a gap statistic with a slightly worse threshold (0.472 instead of 0.5). The current frontier is Inoue's μ < 0.50895 under RH and Durkan and Pearce-Crump's positive proportion of gaps below 1/2 + ε under RH; what refutation needs is a fixed margin below one half, and the depth cannot manufacture that margin. This is the same conclusion as the barrier theorem (Theorem 3.17 of `NEW_RESULTS.md`), reached from the configuration side instead of the form-factor side. It is also a genuinely new *numerical* GUE test: for Odlyzko-height zeros the windowed τ-depth should be far below π²/8 in essentially every window of a hundred zeros, with the law of §2(iii).

## 4. The half-lattice forces its own pair correlation

**Proposition 4 [P].** Let a stationary process on (1/2)ℤ + U (U uniform) have intensity one and satisfy Montgomery's theorem, F(α) = |α| for 0 < |α| < 1. Then its structure measure is determined on all of ℝ up to atoms at the odd integers, and equals that of F_AH = dist(α, 2ℤ) + Σ_{m≠0} δ_{2m}. If moreover the points are simple, there is no atom at the odd integers either, and the entire pair correlation is that of AH.

*Proof.* The pair-correlation measure is supported on (1/2)ℤ, so its Fourier transform is 2-periodic; a 2-periodic measure is determined by its restriction to (−1, 1) except for atoms at the period boundary ±1. The atoms at 2ℤ are forced by the lattice and the intensity. For the band-edge atoms use the finite identity of Theorem 5.1 of `NEW_RESULTS.md`: for integer-marked configurations on ℤ/2N of mass N matching the ramp E|p_k|² = k (k < N), E Σ_x m_x(m_x − 1) = (E|p_N|² − N)/2N; simple points force E|p_N|² = N exactly, i.e. the structure factor at the Nyquist frequency equals the limit of the ramp, which is the statement that there is no atom at ±1. The identity holds at every N, hence for every limit. ∎

Thus every simple-point impostor on the half-lattice has the pair correlation of AH *exactly*, atoms included; the finite impostor fibre differs from ACUE only in third and higher correlations outside the band. The Nyquist conservation law is the finite version of this rigidity, and it adds the one thing the limit statement hides: an alternative with multiple zeros would place an atom of mass twice the multiplicity rate exactly at the band edge α = ±1, the one point Montgomery's method does not reach.

## 5. The impostor fibre in the infinite-volume limit

**(a) The explicit family collapses.** The tilts q_g = μ_ACUE·g(X), X = Σc mod N, (det U_C)² = e^{2πiX/N}, are holonomy insertions: they multiply the law by a function of the global phase. Their coupling to local patterns, max over k ∈ {2, …, N−2} and over occupation patterns of w consecutive sites of |E[e^{2πikX/N} | pattern]|, is

| N | 8 | 10 | 12 |
|---|---|---|---|
| width 3 | 3.9·10⁻¹⁶ | 7.6·10⁻¹⁶ | 1.2·10⁻¹⁵ |
| width 4 | 1.4·10⁻⁵ | 4.1·10⁻⁷ | 2.2·10⁻⁸ |

(`overnight/fable/scripts/dettilt_local.py`, exact enumeration). Width-three coupling vanishes identically, width-four coupling decays by a factor of about thirty per step. In the infinite-volume limit every member of the family has the same local law, the AH process: the (N − 3) parameters are a finite-size phenomenon, like the magnetic-cycle laws of Theorem 5.5 of `NEW_RESULTS.md` whose total-variation distance (2r)^g vanishes with the cycle length.

**(b) The right question.** Is the AH process the unique stationary process on the half-lattice with intensity one whose correlation functions agree with the sine process's inside the Rudnick–Sarnak band at every order? Proposition 4 settles order two. For order three and beyond, the finite evidence is the range of local statistics over the positive moment fibre, computed by linear programming over rotation-invariant laws on the ACUE support:

| N | 6 | 7 | 8 | 9 |
|---|---|---|---|---|
| orbits / constraint rank | 80 / 70 | 246 / 166 | 810 / 407 | 2704 / 900 |
| width-3 patterns: max range | 0 | 0 | 0 | 0 |
| width-4 patterns: max range | 4·10⁻⁵ | 7·10⁻⁵ | 9·10⁻⁵ | 1.2·10⁻⁴ |
| width-5 patterns: max range (ACUE value ≈ 0.11) | 6.5·10⁻⁴ | 1.1·10⁻³ | 1.5·10⁻³ | running |
| Nyquist row E∣p_N∣²/N | forced = 1 | forced = 1 | forced = 1 | 1 (LP running) |
| P(N²D > 1.6): ACUE value | 0.170 | 0.131 | 0.099 | 0.075 |
| P(N²D > 1.6): fibre range | [0.114, 0.282] | [0.066, 0.245] | [0.021, 0.227] | [0.002, 0.218] |
| P(N²D > 1.8): fibre range | [0.087, 0.219] | [0.052, 0.211] | [0.012, 0.200] | [0.0005, 0.195] |

(`overnight/fable/scripts/fibre_lp.py`: variables are the masses of the rotation orbits, constraints the balanced moments of degree ≤ N reduced to an orthonormal row basis, constraint residual of the ACUE point ≤ 10⁻¹⁵; "max range" is the largest width of [min, max] over all occupation patterns of w consecutive sites. At N = 9 the dual simplex needed about five minutes per LP, so the sweeps were rerun with the interior-point method (`fibre_lp_survival.py`, `fibre_lp_patterns.py`; at N = 8 it reproduces the simplex values to five digits, and one pattern that it could not solve fell back to the simplex); the width-5 sweep and the Nyquist-row check at N = 9 were still running when this was written and are reported in `fibre_lp_N9_patterns.log` and `fibre_lp_N9_survival.log` as they finish. N = 10, with 9252 orbits, was not attempted.)

Three things stand out. Every occupation pattern on three consecutive sites is *forced* on the whole positive fibre, to 10⁻¹⁵, which together with Proposition 4 suggests a Nyquist-type identity for three-point patterns that we have not written down. Patterns of width four and five, that is three-point and higher correlations out to two mean spacings, are pinned to within 1.2·10⁻⁴ and 2·10⁻³, with slow, roughly linear growth in N (width four: 4, 7, 9, 12 in units of 10⁻⁵ for N = 6 to 9). The survival probabilities, by contrast, range over an interval of width 0.17 to 0.22 that grows with N; at N = 9 the fibre contains a law under which the event N²D > 1.6, of ACUE probability 0.075, has probability 0.002. In words: **the impostors are locally AH, and what the fibre frees is global, first-passage information**. The depth is exactly such a global functional, which is why it separates impostors from ACUE (the N = 11 theorem) while every local pattern cannot.

For Tao's question this cuts both ways. If the small local ranges tend to zero as N → ∞, the AH process is the unique local limit of the fibre and is canonical; then the whole finite fibre, like the det-tilt family, is a finite-size effect and the depth's freedom on it concerns global structure that no stationary limit sees. If the ranges stabilise at a positive value, there exist stationary half-lattice processes other than AH with the sine process's band-limited correlations at every order, differing from AH in three-point correlations at distance two or more. The N ≤ 9 data cannot decide this; it does decide that any such difference is at most a few parts in a thousand at the scale of two mean spacings.

The N = 11 construction (addendum to §4 of `NEW_RESULTS.md`) shows that the depth law is a free coordinate of the finite fibre even after the full pair-displacement and sorted-gap laws are fixed. Its periodic lift gives examples at every N = 11r with vanishing mass differences, which is consistent with uniqueness in the limit and does not prove it.

## 6. Remarks on Rodgers–Tao

**Remark 6.1 (Lehmer pairs).** Theorem A and Theorem 2(ii) are the finite-N forms of the Csordas–Smith–Varga Lehmer-pair mechanism: a close pair of zeros forces the collapsing flow to produce a double zero within time proportional to the squared gap, with a correction controlled by the pair's isolation. Astra's isolation lemma (δ²B → 0) is the same quantity.

**Remark 6.2 (only the clock survives).** On the circle, D < ∞ for every configuration other than the clock. Proof: if some a_j with 0 < j < N is nonzero, the terms with j nearest N/2 dominate P_s as s → ∞, and the limiting polynomial z^j(a_j + a_{N−j}z^{N−2j}) has j roots at 0 and j at ∞, so roots have left the circle and a collision occurred. The clock is the lattice of spacing one in mean-spacing units, which is the local arithmetic progression that Rodgers and Tao show a negative Λ would force, and which Montgomery's theorem forbids. The half-lattice is the finest lattice Montgomery's theorem permits, and Theorem 2 says it is distinguished from the clock by a finite depth and from GUE by a positive one.

**Remark 6.3 (what Λ sees).** In unscaled de Bruijn–Newman time the collapse time of a window at height T is τ(2π/log T)², which tends to 0 under both hypotheses; Λ = 0 under RH is consistent with both. Only the rescaled windowed depth separates them.

## 7. Files

`overnight/fable/scripts/dimer_limit.py`, `dettilt_local.py`, `fibre_lp.py`, `fibre_lp_survival.py`, `fibre_lp_patterns.py`, `cue_depth_mc.py` with logs. Claims tagged [P] are proved in `NEW_RESULTS.md` or above; the proof sketch of Theorem 2(ii) is complete except for the displacement bookkeeping; all numerical values are exact enumerations or ball-arithmetic certifications except the Monte Carlo of §5 and the LP values, which are floating-point linear programming with the constraint residual reported.
