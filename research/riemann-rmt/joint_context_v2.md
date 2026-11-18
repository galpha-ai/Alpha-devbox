# Shared context v2 — Anthropic method (from Lean source) × finite RMT fiber program

Read this fully before starting your task. You are one of 10 parallel agents; your final text is your report.

## A. Anthropic's actual method (read from the real Lean repo, NOT paraphrase)

The full Lean 4 formalization is cloned at **/workspace/anthropics/zeta-23-lean** (read it!). Key facts extracted:

1. **Lemma R (rank–trace), k-form** (`Zeta23/ZeroSide/RankTraceMult.lean`):
   For P = Σ_j m_j v_j v_j* (on-line zero atoms, multiplicities m_j, near-unit vectors), Q Hermitian with n₊(Q) ≤ b:
   `2c·tr(P+Q) − ‖P+Q‖_F² ≤ Σ_j k_c(m_j) + c²·b`,
   where **k_c(p) = c² − ((c−p)₊)²** (= 2cp − p² for p ≤ c, saturates at c² for p ≥ c) — a concave clipped secant.
   Decoding values: k₂(1)=3, k₂(≥2)=4 (⇒ simple-zero counts, c=2); k₃(1)=5, k₃(2)=8, k₃(≥3)=9 (⇒ distinct counts, c=3, gives 5/6).
   Proof: spectral split Q = Q₊−Q₋, drop tr(PQ₊) ≥ 0, von Neumann trace inequality, elementary secants (x−c/2)²≥0, (x−c)²≥0.
2. **Tightness** (`Zeta23/ZeroSide/TightMult.lean`, `lemmaR_tight`): for on-line atoms with integer m_j ≤ c on orthonormal vectors plus b pair-blocks of eigenvalue c, EQUALITY holds: 2c·tr(P+Q) − ‖P+Q‖_F² = Σ_j k_c(m_j) + c²·b. So the certificate cannot be improved using only (tr, ‖·‖_F, rank, inertia).
3. **Prime side**: tr G and tr G² = ‖G‖_F² of the Gabor/taper compression are computed unconditionally from the explicit formula (`Zeta23/PrimeSideA,B`, `Poisson.lean`, `Taper/`), with Montgomery–Vaughan Hilbert inequality (`Zeta23/MV/`) giving near-orthogonality of zero vectors (Gram ≈ I). Bandwidth-one support; Weyl perturbation for tails.
4. **The constant**: Theorem D optimal window (ThmD/Functional.lean) = Montgomery–Taylor: v*(s) ∝ cos(√2 s), q* = ½+(1/√2)cot(1/√2), δ_MT = 2−q* = 0.672500703679.
5. **PairCeiling** (`Zeta23/PairCeiling/Stability.lean`): stability inequality (two integrations by parts): any valid bandwidth-one certificate (c₀, r), r ∈ C¹[0,1], against a configuration with grid form-factor masses s_j and simple fraction p: `c₀ + ∫₀¹ r(x)·x dx ≤ p + |r(1)|·|D(1)| + |r′(1)|·|E(1)| + sup|E|·∫₀¹|r″|`. Instance at explicit 256-periodic marked law (`LawN256.lean`): every bandwidth-one certificate certifies ≤ **0.6818287 + 2.55·10⁻⁶·(|r′(1)| + ∫|r″|)**. The only unverified input is `EnclOK` (256 integer enclosures from an exact-rational certificate, hash-named, not in repo). Note 2.55e-6 ≈ 1/(6·256²) (grid/Bernoulli fingerprint).
6. **ξ′ theorems** (`Zeta23/XiPrime/`): same rank–trace device on the Farmer–Gonek/Montgomery argument for ξ′ gives unconditionally 0.85838 simple-on-line (flat window) and **0.86864 with a QUARTIC window** — so quartic windows already pay when the arithmetic input exists (ξ′ explicit formula supplies it).

## B. Verified finite results (our program; verify scripts in this scratchpad)

- ACUE = rank-N Fourier projection DPP on ℤ/2N (Tao 2019); mimicker fiber (all laws matching balanced moments E[p_λ p̄_ν]=δz_λ, |λ|=|ν|≤N): dims 0,0,2,10,80,403,1804 for N=3..9. N=5 exact over ℚ(√5).
- Rigidity: all 2-point (proved, aliasing) and 3-point (verified 1e-14) correlations frozen on the fiber; first freedom at 4-point. Fiber gap δ*(N) for word 01010101: 0.0102, 0.0123, 0.0138, 0.0151 (N=6..9), transfer theorem: uniform gap ⇒ Lagarias–Rodgers non-uniqueness.
- **Nyquist conservation law** (verified): with marks m_x ≥ 0, Σm = N on ℤ/2N and open rows E|p_k|²=k (k<N): EΣm(m−1) = (E|p_N|²−N)/2N; closing row k=N forces binary. Slack identity: Es₁ − (N/2 + csc²(π/2N)/2N) = EΣm_x m_{x+1} + EΣh(m_x), h=0 on {0,1,2}; the combination is Nyquist-blind (1+cos π = 0). Bound Es₁/N ≥ ½ + 2/π² = 0.70264. Equality face E_N = hard-core {0,1,2}, |E_N| = C(2N,N). Open: all-N attainment ("Nyquist equality law").
- **Fourth moments of the sine–Gram features** (verified N≤6): for V_k=|p_k|² under ACUE, Cov(V_k,V_ℓ) = k²1{k=ℓ} − 2(k+ℓ−N)₊, λ_min = 1 exactly. Inradius ρ_N ≥ 1/(N²−N/2); repair theorem: feature error o(N⁻²) on the equality face ⇒ exact law with o(N) slack.
- Holonomy: DPP laws on g-cycles agreeing to order <g with dTV = (2r)^g|cos gφ−cos gψ| exactly. Homometry: marked pairs equal complete |Fourier|², different simple fractions. Local blindness: exponential fibers can have zero projection on all fixed local words.
- **Phase twists** (new paper): multiplying by center-of-mass characters translates the Fermi sea; rank-4 twists are stochastically homometric to ACUE (equal Patterson autocorrelation at all frequencies, marginals through order 3, separated at 4-point); the full moment-null space has an exact Fourier–Slater description, exponential dimension; matched-block compressions are forced = identity (all residual in the cross block).
- **Christoffel trace hierarchy through degree 12** (new papers XI/XII): exact continuum moments of the sine–Gram matrix m9=11166011/151200, m10=83443081/554400, m11=852071287/2721600, m12=1033020076559/1556755200; sharp forced-rank (Christoffel at 0) R10 = 0.9385985…, R12 = 0.9482017… (exact rationals; Gauss–Radau adversaries attain). Marked benchmarks: 80.39% (deg 6), 84.94% (8), 87.72% (10), 89.64% (12). Odd–even Schur law: odd trace = coupling coordinate (no standalone gain), next even trace = innovation energy, gain = squared ratio. Bandwidth: order-k collision channel has max Fourier weight ⌊k/2⌋·L (quotient-MaxCut). All-order N⁻² parity (Gorenstein). Hard-edge conjecture: support [0,3], Christoffel Λ_n(0) ~ (3n)⁻¹.
- Third-moment escape (series synthesis): E(M)₃ = r without cap gives NO gain (mass escapes to high marks); fourth factorial moment restores p₁ − (2−q) ≥ r²/(s+2r).
- **Scalar-compression moment code** (Prop 8.1, series synthesis): if subspace V satisfies P_V D_j P_V = b_j P_V for diagonal moment observables D_j, then every unit v ∈ V gives an honest law q_v(o) = |v(o)|² matching all moments. (Quantum-marginal-style realization tool.)
- Inner-SOS ⊆ exact LP ⊆ outer-SDP sandwich; signed PSD pseudo-laws are not laws. Inertia alone gives no local gap: exponentially large word-invisible positive tangent exists (rank ceiling 2^{ℓ−1}−1 for length-ℓ words).
- Two constants NEVER to conflate: δ_MT = 0.6725007 (zeta certificate) vs ½+2/π² = 0.70264 (marked open-Nyquist model). Literal ACUE fiber is binary (s₁ ≡ N).

## C. Environment

- python3 + numpy/scipy in this scratchpad; write scripts here, name by your topic. Exact rational/cyclotomic arithmetic via sympy (pip install sympy if needed).
- Lean repo at /workspace/anthropics/zeta-23-lean — READ the relevant files for your task (grep docstrings; they cite paper §§).
- arxiv.org / anthropic.com are egress-blocked; WebSearch summaries work.
- Report format: English, precise; tag every claim [PROVED] / [COMPUTED] (with script path + numbers) / [HEURISTIC] / [CONJECTURE]. State explicitly what is NEW relative to sections A/B above. End with the single most promising concrete next step.
