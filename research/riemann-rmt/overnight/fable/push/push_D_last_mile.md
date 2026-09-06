# Push D — the last mile: what an AH refutation needs, exactly

**Fable overnight, push D, 2026-09-06.** Deliverable for task `push_D_last_mile`.
Tags: **[P]** proved here or in a cited programme file whose proof was re-read for this note; **[C]** computed (scripts `push_D_constants.py`, `push_D_ah_exact.py`, `push_D_lp.py` in this directory); **[O]** open. Literature items are marked *(recalled)* unless the text was actually read; §5 lists what could and could not be read (arxiv.org, ar5iv, export.arxiv, OUP, Cambridge, EUDML, Semantic Scholar, Wikipedia, KSU, GitHub pages, Wayback were all blocked; only search-engine snippets and the local `tao_ah_notes.pdf` were readable).

**Standing hypothesis for every statement about ζ: RH.** The three versions of the Alternative Hypothesis are kept apart (as in `r1_levelB_barrier.md`): **AH-strong** (Lagarias–Rodgers: every normalised gap in ½ℤ_{>0} + o(1), no multiple zeros), **AH-mult** (Baluyot 2016 / Baluyot–Goldston–Suriajaya–Turnage-Butterbaugh 2025: multiplicities allowed), **AH-pairs** (the pair-correlation consequence, formulated as AH0 in Goldston–Lee–Schettler–Suriajaya 2025 and used by Astra). Astra's W_T target refutes AH-pairs; Level B refutes AH-strong only.

---

## 0. Verdict in twelve lines

1. Astra's target `liminf W_T ≥ 1/16` is, under RH, a linear functional of Montgomery's form factor: `W_T = ∫ K(α) F_T(α) dα + o(1)`, `K(α) = sinh2·e^{−2|α|} − sinh1·e^{−|α|}` **[P]**. K > 0 for |α| < α₀ = log(2cosh 1) = 1.126928 and K < 0 beyond.
2. F_AH satisfies every RH-only theorem about F (Montgomery's band, positivity in both senses, Goldston's 3/2 − |α|), and W[F_AH] = 0.0623924 < 1/16. Hence no argument using only those inputs proves the target **[P, Theorem 2.1]**.
3. Quantitatively: with F ≥ 0 only, the best bound from the known inputs is −∞; with the pair measure's physical positivity added, the best bound is W ≥ 0.0236 (LP, converged) **[C]** — about 38 % of 1/16, still below W_AH; Astra's own minorant gave −0.2087.
4. The band contributes exactly B = 0.4560940 (Round 8's constant). The last mile is the sign-indefinite tail 2∫₁^∞ K F, and since K ≥ 0 on (1, α₀), it is an **upper** bound that is missing: `limsup 2∫_{α₀}^∞ |K| F_T ≤ 0.396795` (with Goldston) / 0.393594 (without) — i.e. the |K|-averaged F on (1.127, ∞) must be ≤ 1.0420 (resp. 1.0336). AH has 1.0515, GUE has 1.0000 **[P+C]**.
5. AH beats GUE in W only through its Bragg atoms at even frequencies: they contribute e^{−2} − e^{−1} = −0.2325 to W_AH; AH's continuous spectrum alone would give W = 0.2949 > W_GUE **[C]**.
6. Any hypothesis of the form "no spectral mass above the GUE level on (α₀,∞)" (F ≤ 1 there in the measure sense) already gives W ≥ 0.0753 > 1/16 **[P]**; so the missing input is a no-Bragg-excess statement at frequencies α ∈ (1.127, ≈5), Goldston-Montgomery-equivalently an upper bound for the variance of ψ in intervals of length h = x^{1−1/α}, at the level 1.042 × the GUE prediction.
7. The depth/stopping-time route does not evade this: Level B ⟹ μ < ½ (under (NR)) ⟹ gaps 6 % below ½ after the dressing factor, which by Conrey–Iwaniec is Siegel-hard and which every band-limited statistic of every order (Lagarias–Rodgers mimicry) is blind to **[P modulo (NR)]**.
8. Every refutation route in the programme (W_T, compact Fourier bump, Bragg-atom deficit, prime variance V̄_T, Level B) is either a linear functional of F on |α| > 1 or implies a small-gap statement that band-limited data of every order cannot give. That is Tao's 2019 remark restated: one out-of-band value of F suffices and is comparable to averaged Hardy–Littlewood with power saving.
9. Rounds 8–28 achieved reductions only: X^{1.023}log⁵X for one component (needs X log X), exact Type-I removal below X^{0.477}, Vaughan signed remainder, full-range variance reduction with its singular-series constant 2M; the single missing estimate is displayed in §3.3.
10. Provable now: Theorems 9.1–9.2, the barrier Theorem 2.1, the LP bound, the dictionary α ↔ h, Theorem A′; not provable now: liminf W_T ≥ 1/16, μ < ½, any refutation of any AH version, Montgomery–Dyson, RH.
11. Minimal new arithmetic input: one one-sided bound on a signed two-prime correlation at interval length x^{1−1/α}, 1 < α ≤ 2 (equivalently one out-of-band F value); §4 displays it.
12. Nothing here moves a zeta zero; the deliverable is the exact location, size (0.0001 above W_AH; 0.039 above the best provable bound) and prime-side translation of the obstruction.

---

## 1. Tao's motivation for the ACUE, and what the separation programme can say

### 1.1 The hypothesis, as documented

- **AH-strong** (Lagarias–Rodgers 2020, *Higher correlations and the alternative hypothesis*, Q. J. Math. 71, 257–280; abstract read via search snippets): "the renormalized distance between nontrivial zeros is supposed to always lie at a half integer"; the paper "asks whether current knowledge about higher correlation functions of the zeros is sufficient to rule out the Alternative Hypothesis and shows by construction of an explicit counterexample point process that it is not"; they "work under the assumption that almost all of the points of the point process are distinct".
- **AH-pairs** (Goldston–Lee–Schettler–Suriajaya 2025, arXiv:2507.06823, abstract and one introduction sentence via snippets): AH "arose as a consequence of the (possible) existence of Landau–Siegel zeros. If there is a sequence of real Dirichlet L-functions with Landau–Siegel zeros, then the zeros occur at spacings that are nearly exactly integer multiples of half the average spacing between zeros, and these hypothetical properties need not depend on the existence of Landau–Siegel zeros." "The Alternative Hypothesis is discussed in Farmer, Gonek and Lee and in Baluyot." Under RH their AH0 determines a pair-correlation conjecture different from Montgomery's, and (their theorem) still forces 100 % simple critical zeros by the Gallagher–Mueller method. Astra's `TWO_SCALE_ZETA_TARGET.md` §1 transcribes its consequence (masses at half-integers, eq. (5) there, with near-diagonal parameter 1 + o(1) ≤ p₀(T) ≤ 3/2 − 2/π² + o(1)); its Fourier transform is 2-periodic, so
  `F_AH(α) = dist(α, 2ℤ) dα + Σ_{m≠0} δ_{2m}`, in particular F_AH(α) = 2 − |α| on 1 ≤ |α| ≤ 2 **[P, from the pair masses; Astra (9)]**.
- **AH-mult** (Baluyot 2016, J. Number Theory; BGST 2025, arXiv:2508.10857; abstracts via snippets): consecutive zeros spaced at multiples of half the average spacing, simplicity not assumed; BGST obtain, under RH + AH, constraints on the density of pairs at each k/2 and hence on multiple zeros, and show a stronger AH implies the Essential Simplicity Hypothesis.
- **Farmer–Gonek–Lee**: the reference the AH literature cites is their JLMS (2) 90 (2014) 241–269 paper (arXiv:0803.0425) on the pair correlation of zeros of ξ′; the search results confirm the bibliographic data and that GLSS credit them with discussing AH. I could not read the paper; that they were the first to note that a half-integer spacing law is compatible with Montgomery's theorem is **my reconstruction** from the secondary citations, not a checked fact.

### 1.2 Why AH is *the* obstruction to Montgomery–Dyson (documented + reconstruction)

Montgomery's theorem *(recalled; corroborated by a snippet giving the Goldston–Montgomery error term)*: under RH,
`F(α,T) = (1+o(1)) T^{−2|α|} log T + |α| + o(1)` uniformly for |α| ≤ 1, where `F(α,T) = (T/2π · log T)^{−1} Σ_{0<γ,γ′≤T} T^{iα(γ−γ′)} w(γ−γ′)`, w(u) = 4/(4+u²). Montgomery's conjecture is F(α) = 1 + o(1) for |α| ≥ 1, equivalent to the pair correlation 1 − (sin πu/πu)² (Montgomery–Dyson). The band |α| ≤ 1 is the *only* proven pair-correlation information; beyond it only three things are known (§2.3).

F_AH agrees with |α| on |α| ≤ 1 and deviates only outside the band. Lagarias–Rodgers (snippets): AH "is compatible not only with Montgomery's unconditional results on the pair correlation function for |α| ≤ 1, but for all band-limited higher correlations"; their explicit process (a random translate of ½ℤ carrying a sine-kernel-type determinantal law) has n-point correlations equal to the sine process's against test functions whose Fourier transform is supported in the Rudnick–Sarnak/Hejhal range Σ|ξ_i| < 2 (unit mean spacing). The "< 2" is documented for n = 2, where it is exactly |α| < 1; for n ≥ 3 it is my reconstruction from the degree count in §1.3, consistent with `tao_ah_notes.pdf` §1. Lagarias–Rodgers 2021 (*Band-limited mimicry…*, Ann. Appl. Probab. 31; snippet) give existence and non-existence regions in the (lattice spacing a, bandwidth B) plane for mimicking the sine process by a process on aℤ.

Consequence **[P, by the existence of the LR process]**: no statement about the zeros that follows from band-limited correlation data of any order can prove Montgomery–Dyson, or even exclude the half-lattice law; AH is the named survivor of everything that is proved.

### 1.3 Tao's ACUE: what is documented, what is reconstructed

*Documented* (search snippets of the 8 May 2019 post; `tao_ah_notes.pdf`): "ACUE can be viewed as normalised Lebesgue measure on [a disconnected smooth submanifold of] unitary matrices whose phase spacings are non-zero integer multiples of [π/N]; informally, ACUE is CUE restricted to this lower dimensional submanifold"; it corresponds to an "alternative GUE" hypothesis "that the spacing between adjacent zeroes is almost always approximately a half-integer multiple of the mean spacing", "a stronger version of the alternative hypothesis". Concretely: fix N, take the 2N-th roots of unity rotated by a uniform random angle, choose N of the 2N sites with probability ∝ |Vandermonde|²; equivalently the determinantal process with the rank-N projection kernel onto N consecutive Fourier modes (`tao_ah_notes.pdf` §1).

*Matching theorem — reconstruction, consistent with the secondary source.* For partitions λ, ν with |λ|, |ν| ≤ N,
`E_ACUE[p_λ(U) \overline{p_ν(U)}] = E_CUE[p_λ(U) \overline{p_ν(U)}] = δ_{λν} z_λ` (Diaconis–Shahshahani values).
Proof sketch: |Δ(θ)|² is a trigonometric polynomial of degree N−1 in each θ_j; p_λ \bar p_ν has per-variable Laurent range [−|ν|, |λ|]; the equispaced 2N-point rule integrates exactly every trigonometric polynomial of per-variable degree ≤ 2N−1; so the ACUE expectation equals the CUE (Haar) expectation as soon as (N−1) + max(|λ|,|ν|) ≤ 2N−1. The random rotation kills |λ| ≠ |ν|. In correlation language (traces tr U^{k_1}⋯tr U^{k_n}, Σk_i = 0, |λ| = |ν| = ½Σ|k_i|): all n-point correlations tested against f̂ supported in Σ|ξ_i| ≤ 2 (ξ_i = k_i/N) agree — the LR range. The same count gives E|det(1−U)|^{2k} equal to CUE for integer k ≤ N; Rodgers–Vallabhaneni (Glasgow Math. J. 66 (2024) 51; arXiv:2301.00268; abstract via snippet) prove closed formulas for arbitrary mixed moments and ratios of ACUE characteristic polynomials via symmetric functions and the Borodin–Olshanski–Strahov formula and compare with CUE; their exact statements were not read. The programme's own finite theorems (`tao_ah_notes.pdf` §2: fibre dimensions 0,0,2,10,80,403,1804; 2- and 3-point statistics frozen on the fibre; Nyquist law) are theorems about this finite object, not about ζ.

*What Tao says would be needed* (snippets, near-verbatim): "a verification of the pair correlation conjecture for even a single [parameter value α > 1] would rule out the alternative hypothesis. However, such a verification appears to be on comparable difficulty with an averaged version of the Hardy–Littlewood conjecture with power saving error term, and Siegel zeroes can cause distortions in the Hardy–Littlewood conjecture." The single-value statement is exactly the mechanism of §2: F_AH(α) = 2 − α ≠ 1 for every α ∈ (1,2).

*Siegel-zero connection* (snippets): Tao: AH "is implied by the existence of a Siegel zero, as discussed in a paper of Conrey and Iwaniec". Conrey–Iwaniec, *Spacing of zeros of Hecke L-functions and the class number problem*, Acta Arith. 103 (2002) 259–312 (abstract via snippets): they "deduce lower bounds on the class number h(−D), on the hypothesis that sufficiently many zeros of various L-functions attached to characters of the class group are sufficiently closely spaced"; a secondary source (arXiv:2602.03626, snippet) states the contrapositive used in the folklore: "if one could prove that any L-function has a sufficient number of consecutive zeros whose spacing is smaller than 1/2 of what is expected, then one could disprove the existence of the Landau–Siegel zero", and "the existence of a small class number (or equivalently a Landau–Siegel zero of L(s,χ_{−D})) forces very many zeros of ζ(s) to be very regularly spaced". Exactly which L-functions, which height range in terms of D, and how many pairs "sufficient" means, I could not verify; the dependence of the statement on the height range is the reason "Siegel-hard" is a heuristic and not a theorem about AH for ζ at all heights.

### 1.4 What the CUE/ACUE separation programme can and cannot say

**(a) About RH: nothing.** Both models place all points on the line; every reduction below assumes RH; GLSS show that even AH-pairs implies 100 % simple critical zeros, so no AH version is in tension with RH and no AH refutation says anything about RH.

**(b) About AH.** *Can:* locate the statistics that could separate (order ≥ 4 correlations or Fourier support outside Σ|ξ_i| < 2; `tao_ah_notes.pdf` §2.2), certify by exact enclosure that a specific statistic separates the two limiting laws (W_AH < 1/16 < W_GUE with margin 1.08·10⁻⁴), and translate the separation into one arithmetic inequality. *Cannot:* refute any version of AH for ζ: every input the programme uses (RH, Montgomery's band, both positivities, Goldston's bound, integrality of multiplicities, the explicit formula with proven prime estimates) is satisfied by the LR/ACUE law, so the missing step is exactly the out-of-band arithmetic input of §2.5 — which Tao places at the difficulty of averaged Hardy–Littlewood with power saving, and which in the small-gap direction is Siegel-hard by Conrey–Iwaniec.

**(c) About Montgomery–Dyson / GUE.** Refuting AH-pairs needs one one-sided out-of-band inequality; Montgomery–Dyson needs F(α) = 1 + o(1) for *all* α ≥ 1 (equivalently, Goldston–Montgomery, the variance asymptotic for all interval lengths x^ε ≤ h ≤ x^{1−ε}); GUE spacing needs all correlations. The programme's own rigidity ladder shows 2- and 3-point data do not even determine the finite model. So the separation programme can at most exclude named alternatives; it cannot prove GUE, and it does not claim to.

---

## 2. The barrier theorem for the last mile

### 2.1 The kernel: the two-scale statistic as a Laplace transform of F [P]

Astra's target: `I_T(c) = ∫₀^T |ζ′/ζ(½ + c/log T + it)|² dt`, `W_T = 2[sinh2·I_T(1) − sinh1·I_T(½)]/(T log²T)`.

Under RH, `ζ′/ζ(s) = Σ_ρ 1/(s−ρ) + (bounded)`, so |ζ′/ζ|² is a pair sum with kernel 1/((a+i(t−γ))(a−i(t−γ′))), a = c/log T, and `∫_ℝ dt/((a+i(t−γ))(a−i(t−γ′))) = 2π/(2a + i(γ′−γ))`; the real part is the Poisson kernel of width 2a in γ−γ′, whose Fourier transform in the normalised variable L(γ−γ′), L = log T/2π, is e^{−2c|α|}. Astra's `TWO_SCALE_ZETA_TARGET.md` §§5–6, eqs. (18)–(23), carries this out with all endpoint, Γ-factor and holomorphic-square (∫F² = o(T log²T)) terms, giving `Q_T(b) = (2/(T log²T)) I_T(b/2) + o(1)` where Q_T(b) is the e^{−b|α|}-smoothed centred pair statistic. Hence, for fixed c > 0,

  **`I_T(c) = T log²T · ∫₀^∞ e^{−2cα} F_T(α) dα + o(T log²T)`,**  (GGM kernel)

with F_T Montgomery's form factor (the zero-frequency atom removed). This is the Goldston–Gonek–Montgomery 2001 correspondence *(recalled: J. reine angew. Math. 537, 105–126, whose abstract — read via snippet — states the equivalence of asymptotics for (a) averages of F, (b) the mean square of ζ′/ζ near the line, (c) the variance of primes in short intervals, (d) small gaps)*; the sine-kernel evaluation `∫₀^∞ e^{−2cα} min(α,1) dα = (1−e^{−2c})/(4c²)` is the classical GGM constant. Therefore

  **`W_T = ∫_ℝ K(α) F_T(α) dα + o(1)`, `K(α) = sinh2·e^{−2|α|} − sinh1·e^{−|α|}`.**

K vanishes at |α| = α₀ := log(2cosh 1) = 1.12692801, is positive inside and negative outside. Its inverse transform `k(u) = 4 sinh2/(4+4π²u²) − 2 sinh1/(1+4π²u²)` is ≥ 0 for all u (k ≥ 0 ⟺ 4π²u²(sinh2 − sinh1) ≥ 2 sinh1(2 − 2cosh1), always true) **[P]**: W_T is a nonnegative-kernel pair statistic minus its mean, which is why physical positivity alone gives the trivial bound W ≥ k(0) − K(0) = −sinh 1.

### 2.2 Verification against F_GUE and F_AH [C, mpmath 30 digits]

| quantity | value | source of the number |
|---|---|---|
| W_GUE = ∫K·min(|α|,1) | 0.0822714431214773232 | agrees with Astra's closed form (15) to 30 digits |
| W_AH = ∫K·F_AH | 0.0623924179764985431 | agrees with Astra's closed form (15) to 30 digits |
| 1/16 − W_AH | 1.0759·10⁻⁴ | Astra: "> 0.00010" |
| B = ∫_{|α|≤1} K|α| (band) | 0.4560939793292317 | Round 8's constant B |
| W_AH continuous part ∫K·dist(α,2ℤ) | +0.2949365759 | |
| W_AH atoms 2Σ_{m≥1}K(2m) = e^{−2} − e^{−1} | −0.2325441579 | exact |
| 2∫₁^{α₀} K·(3/2−α) (Goldston floor) | +0.0032014647 | |
| 2∫₁^{α₀} K·1 (GUE) | +0.0069745418 | |
| 2∫₁^{α₀} K·(2−α) (AH) | +0.0066887356 | |
| 2∫_{α₀}^∞ K = −tanh(1)/2 (GUE tail) | −0.3807970780 | exact |
| AH tail 2∫_{α₀}^∞ K F_AH | −0.4003902969 | = −0.1678461390 (continuous) − 0.2325441579 (atoms) |
| W_GUE − B (sine residual) | −0.3738225362 | Round 8: −0.3738225362 |
| W_AH − B (AH residual) | −0.3937015685 | 1/16 − B = −0.3935939793 |

Two facts the table makes visible. (i) The known band gives exactly Round 8's B; Round 8's "residual energy" E_T is exactly `2∫₁^∞ K F_T`. (ii) AH is below GUE in W *only because of its Bragg atoms*: on the continuous spectrum AH has less mass than GUE where K < 0 (dist ≤ 1), which raises W by 0.21295; the atoms lower it by 0.23254; net −0.01959 on the tail, +0.00029 on (1, α₀), total W_GUE − W_AH = 0.019879.

### 2.3 The three known constraints, and F_AH

Everything proved about F outside the band, under RH:

- **(i) Montgomery's band**: F_T(α) = |α| + o(1) uniformly on |α| ≤ 1 *(recalled)*.
- **(ii) Positivity, in two senses.** (ii-F) F_T ≥ 0, because F_T is |Σ_γ T^{iαγ}…|²-type (Montgomery). (ii-μ) the pair measure μ_T is a nonnegative measure: `∫ F_T r̂ ≥ 0 for every r ≥ 0`, i.e. in the limit `R(u) := 1 + ∫(F(α) − 1)e(αu)dα ≥ 0` as a measure. (ii-μ) is strictly stronger than (ii-F) for the purposes below.
- **(iii) Goldston's bound** *(recalled: Goldston, J. reine angew. Math. 385 (1988) 24–40; a search snippet corroborates the form "F(α,T) ≥ 3/2 − α + o(1) on (1, 3/2)", attributing the assumption to GRH in one secondary source; the primary text was not read)*: F(α) ≥ 3/2 − |α| − o(1) for 1 ≤ |α| ≤ 3/2.

F_AH satisfies all three: (i) by construction (dist(α,2ℤ) = |α| on |α| ≤ 1); (ii-F) and (ii-μ) because F_AH is the spectral measure of an actual point process (Lagarias–Rodgers); (iii) because 2 − |α| ≥ 3/2 − |α|. Any proven RH-only lower bound must be satisfied by F_AH, otherwise AH would already be refuted under RH.

### 2.4 Theorem 2.1 (barrier) [P]

Let 𝓕 be the set of even, locally finite, nonnegative measures F on ℝ (density plus atoms) satisfying (i), (ii-F), (iii), and let 𝓕⁺ ⊂ 𝓕 be those also satisfying (ii-μ). Let W[F] = ∫K dF.

**(a)** F_AH ∈ 𝓕⁺ and W[F_AH] = 0.0623924 < 1/16; F_GUE ∈ 𝓕⁺ and W[F_GUE] = 0.0822714.

**(b)** inf_{𝓕} W = −∞. Explicitly, for any U ≥ 3/2 − α₀ = 0.3731, the minimiser of W over {F ∈ 𝓕 : F ≤ U on |α| > α₀} is
  `F*_U = |α| on [−1,1]; (3/2 − |α|) on 1 < |α| ≤ α₀; U on |α| > α₀`,
  with `W[F*_U] = B + 0.0032015 − 0.3807971·U = 0.4592954 − 0.3807971·U`, which → −∞ as U → ∞. (Proof: W is linear; on (1, α₀) K > 0 so F is pushed to its floor max(0, 3/2−|α|) = 3/2−|α|; on (α₀, ∞) K < 0 so F is pushed to its cap.)

**(c)** inf_{𝓕⁺} W is finite, and equals 0.0236 (without (iii): 0.0207) **[C, discretised LP with cutting planes; details in §2.5]**. Finiteness: by (ii-μ) applied to a nonnegative test with nonnegative transform (Astra Round 16's comparison 0 ≤ C_ε(b) ≤ C_ε(0) → 1 + ε²m₁), the F-mass in any window of width ε is at most 1 + O(ε²), so ∫_{|α|>α₀}|K|dF is bounded by an absolute constant.

**(d) Barrier.** Let 𝒜 be any collection of statements about F_T (or about the zeros) each of which is a consequence of (i), (ii-F), (ii-μ), (iii) — equivalently, each of which holds for F_AH. Then 𝒜 ⊬ liminf_T W_T ≥ 1/16. Proof: a valid derivation of `W ≥ 1/16` from 𝒜 is a valid inequality on the set of measures satisfying 𝒜, which contains F_AH by (a); but W[F_AH] < 1/16. ∎

The same argument applies with any finite family of band-limited higher correlations added to 𝒜 (the LR process satisfies them), with integrality of multiplicities added (the ACUE is a simple point process), and with any proven prime estimate that AH's prime-side shadow (§2.6) does not contradict. It does *not* apply to arithmetic inputs that F_AH violates — and by (b),(c) those are the only inputs that can close the gap.

### 2.5 The best bound from the known inputs, computed [C]

Discretise F on (1, 12] (cells of width 0.01 on (1,3], 0.02 on (3,6], 0.05 on (6,12]; F = 1 beyond 12, where 2∫_{12}^∞|K| < 1.5·10⁻⁵), fix F = |α| on [0,1], impose F ≥ 0, optionally (iii), and impose (ii-μ), `R(u) = 1 − sinc²(u) + 2∫₁^{12}(F−1)cos(2παu)dα ≥ 0`, by cutting planes on u ∈ (0, 400] (initial grid u ≤ 20, step 0.02; violated points added until min R ≥ −10⁻⁶ on a grid of step 0.002). The long u-range is essential: with positivity enforced only up to u = 30 the optimiser places off-lattice near-atoms (e.g. mass 0.31 at α = 1.395) and reports W ≈ 0.0206 while R(37.5) = −0.58; commensurable atoms (the AH comb at 2ℤ, whose R-contribution is a Dirac comb) survive the long range, incommensurable ones do not (Kronecker: total incommensurable atomic mass ≤ ½).

| constraints on F beyond the band | best lower bound for W | vs 1/16 = 0.0625 |
|---|---|---|
| (ii-F) F ≥ 0 only, with or without (iii) | −∞ | — |
| trivial physical bound k ≥ 0 | −sinh 1 = −1.1752 | |
| Astra Round 8 band-limited minorant (one-parameter family) | −0.2087 | |
| (ii-μ) pair positivity + band, LP | 0.0207 | |
| (ii-μ) + band + (iii) Goldston, LP | **0.0236** | gap 0.0389 |
| (iii) + cap F ≤ 1.042 on (α₀, ∞) [no LP needed] | 0.0625 | = threshold |
| (iii) + cap F ≤ 1 on (α₀, ∞) | 0.0785 | > 1/16 |
| F ≥ 0 only on (1,α₀) + cap F ≤ 1 on (α₀, ∞) | 0.0753 | > 1/16 |
| AH itself | 0.0624 | below by 1.1·10⁻⁴ |
| GUE | 0.0823 | |

The converged values are 0.020696 (band + (ii-μ)) and 0.023579 (band + (ii-μ) + Goldston); each is stable to four decimals from the first cut round on, and a finer discretisation (cells 0.01, positivity to u = 30 only) gave 0.0206 for the first problem before the long-range cuts were added. The minimiser is *not* AH-like: on (1, α₀), where K > 0, it sits on its floor (0 without Goldston, 3/2 − α with; the latter contributes exactly 0.0031908), and on (α₀, ∞) it concentrates its mass in a quasi-periodic comb of near-atoms — with Goldston at α ≈ 1.41, 2.82, 4.23, 5.65, 7.05, 8.45 (spacing ≈ 1.41; cell masses 0.84, 0.66, 0.65, 0.50, 0.35, 0.23), without Goldston at 1.38, 2.78, 4.15, 5.55, 6.95, 8.35 — plus continuous density ≈ 1.5 near α = 5 and ≈ 1.3 near α = 8; its |K|-averaged tail is 1.144 (0.43569/0.38080; AH: 1.051; needed: ≤ 1.042). It satisfies pair positivity to 10⁻⁶ on u ∈ (0, 400] but is a relaxation only: no claim is made that it is the spectral measure of a point process (higher-order consistency is not imposed). Files: `push_D_lp_gold0.log/.json`, `push_D_lp_gold1.log/.json`.

So the honest statement of the size of the last mile is: the provable lower bound is 0.0236; the target is 0.0625; AH sits at 0.0624; GUE at 0.0823. The whole margin is in the constraint set beyond the band.

### 2.6 What the last mile is, exactly, and its prime-side name

**In F-language [P].** Since W_T = B + 2∫₁^{α₀}K F_T − 2∫_{α₀}^∞|K|F_T + o(1) and the middle term is ≥ 0 (K > 0, F ≥ 0; ≥ 0.0032015 with (iii)), the target `liminf W_T ≥ 1/16` follows from, and (given only (iii) on (1,α₀)) is equivalent to,

  **`limsup_{T→∞} 2∫_{α₀}^∞ |K(α)| F_T(α) dα ≤ 0.3967954`  (with Goldston), resp. ≤ 0.3935940 (without),**

i.e. the |K|-weighted average of F_T over (1.127, ∞) must be at most **u* = 1.04201** (resp. 1.03361). GUE has this average equal to 1; AH has 1.05145. Because |K| ≍ e^{−α}, the weight is concentrated on 1.13 < α < ≈5: 56 % of the total |K|-weight 0.3808 lies on (α₀, 2.5]; AH's unit atom at α = 2 alone contributes 2|K(2)| = 0.1852 (49 % of the tail weight), all even atoms together e^{−1} − e^{−2} = 0.2325. Conversely, any lower-bound-type information on (1, α₀) is nearly worthless: the most it can add is 2∫₁^{α₀}K·F, at most ≈ 0.007 for any F ≤ 1 there. **The last mile is an upper bound on the spectral mass of the zeros at frequencies α > 1.127, of size 4 % above the GUE level; it is not a lower bound, and it is not information at α ≤ 1.**

The weakest sufficient statement with a single fixed test: with any nonnegative φ supported in (1,2) with ∫φ = 1 concentrated near 2, `∫φ F_T ≥ (2−α_φ) + ε` refutes AH-pairs (Astra Round 7's compact test: φ on [6/5,7/5], AH value 7/10, GUE 1); with a bump ψ((α−2)/ε) around the atom, `limsup C_{ε,T}(2) < 1 + ε²m₁` refutes it (Round 16). Every one of these is a statement about F on |α| > 1 and nothing else.

**In prime language.** *Goldston–Montgomery 1987* (*Pair correlation of zeros and primes in short intervals*, Progr. Math. 70; recalled; the equivalence is corroborated by snippets, the exact constants are from memory): under RH, for fixed 0 < B₁ ≤ B₂ ≤ 1,
  `∫₁^X (ψ(x+δx) − ψ(x) − δx)² dx ~ ½ δ X² log(1/δ)` uniformly for X^{−B₂} ≤ δ ≤ X^{−B₁}
is equivalent to `F(α,T) ~ 1` uniformly for 1/B₂ ≤ α ≤ 1/B₁. The dictionary (from the explicit formula: zeros up to height T ≍ 1/δ, primes near x = T^α) is

  **frequency α ⟷ prime scale x = T^α, interval length h = x/T = x^{1−1/α}**;   α ∈ (1, 2] ⟷ h ∈ (x^{0+}, x^{1/2}];  α = α₀ ⟷ h = x^{0.1126};  α = 5 ⟷ h = x^{0.8}.

The exact (non-asymptotic) form of the same correspondence is Montgomery's representation used by Astra Round 16: `F_T(α) = (xT log T)^{−1} ∫₀^T |Σ_n Λ(n) a_n(x) n^{−it} − M_x(t)|² dt + o(1)`, x = T^α, a_u(x) = min((u/x)^{1/2},(x/u)^{3/2}), M_x the pole term; by Gallagher's lemma the mean square over t ∈ [0,T] of a Dirichlet polynomial supported at n ≍ x is the variance of ψ over intervals of length ≍ x/T at x. Astra's Rounds 19–20 make this exact for the frequency-2 test: `V̄_T = ∫₀^∞ p(y) C_{Ty} dy + o(1)`, p(y) = 4y²/(π(1+y²)²), where V̄_T is the exponentially length-averaged, fully centred variance of ψ over intervals of length ≍ x/T for x ∈ [T^{7/4}, T^{9/4}].

Hence the prime-side name of the last mile is: **an upper bound for the (|K|-weighted, α > 1.127) short-interval variance of ψ(x+h) − ψ(x) − h at h = x^{1−1/α}, at the level 1.042 × ½·h·x·log(x/h), where the best level provable from band + positivity + Goldston is 1.144 × (the LP tail of §2.5) and AH's level is 1.0515 ×; for the single frequency-2 window the proven upper bound (Round 20, from the same inputs) is exactly the AH value A_ε = 1.0106, against the GUE value M ≈ 0.185.** In Astra's own residual form (Round 8, exact under RH): `liminf_T E_T ≥ 1/16 − B = −0.3935940`, with `E_T = (2/(T log²T))[sinh2‖R₁‖² − sinh1‖R_{1/2}‖²]` and R_c the centred-ψ Mellin tail; sine predicts −0.3738, AH −0.3937.

---

## 3. Does the depth / stopping-time route evade the barrier? No.

### 3.1 Level B is a small-gap statement, hence out-of-band [P modulo (NR)]

`r1_levelB_barrier.md` (re-read): (a) the finite model is the exact periodised backward heat flow of the zero set (§1.3 there), the dimensionless depth 𝔇 = (2π/Δ)²·(collision time) satisfies 𝔇 = π²λ²/2 for an isolated pair of normalised gap λ, so π²/8 ⟺ λ = ½ exactly (§1.4); (b) Theorem A′: under RH and the hypothesis (NR) (no non-real zero formed elsewhere comes horizontally closer to the critical pair than its own height before the collision), an adjacent pair closes no faster than the two-body rate, so **Level B ⟹ μ ≤ √(2c)/π < ½**; (c) the converse fails: a gap λ ∈ (λ*, ½) with λ* = 0.4719538 (clock background; ≈ 0.47 in a random CUE background) does *not* break the floor, so the gap Level B needs is 6 % below ½ (the record is μ ≤ 0.515396, Preobrazhenskiĭ, recalled; Astra reads a 2026 preprint as μ < 0.50895); (d) the periodised "hypothesis-free" shortcut is wrong (wrap-gap counterexample) and reduces to the same (NR)-type condition; (e) Level B refutes AH-strong only (a multiple zero gives D_T = 0 with AH-mult intact; a liminf cannot touch AH-dens).

Therefore the depth route's arithmetic content is a proof of gaps below ½ − 0.028. Two consequences:
- **Band-limited blindness [P].** The LR mimicker with hard core ½ (and the ACUE at every N) has *no* gap below ½ and matches every band-limited correlation of every order. By the argument of Theorem 2.1(d), no derivation of μ < ½ from band-limited correlation data (of any order), positivity, integrality, or the flow itself (H_t is determined by the t = 0 zero set, so Level B is a nonlinear functional of the initial configuration — `r1_levelB_barrier.md` §4.3) can exist. The handoff's proposed inputs "pair correlation at bandwidth ≤ 1 plus Rodgers–Tao energy/variance" are of this type; the Rodgers–Tao argument excludes a *full* lattice, which is visible at bandwidth < 1, not a half-lattice hard core.
- **Siegel-hardness (documented, §1.3).** By Conrey–Iwaniec, sufficiently many consecutive zeros spaced below ½ of the mean spacing disprove Landau–Siegel zeros. So a Level B proof, through Theorem A′, would be a Siegel-zero theorem. This is stronger than what W_T needs: W_T refutes AH-pairs through an *average* out-of-band statement, and does not by itself produce a small gap.

### 3.2 Every route in the programme reduces to out-of-band information [P]

Claim: every AH-refutation route in the programme either is a linear functional of F on |α| > 1, or implies μ < ½. Case list:

| route | statistic | AH-version refuted | reduces to |
|---|---|---|---|
| W_T ≥ 1/16 (R7) | ∫K F | AH-pairs | upper bound on F on (α₀,∞), §2.6 |
| compact bump φ on [6/5,7/5] (R7) | ∫φF > 7/10 | AH-pairs | F on (1,2) |
| Bragg deficit D_{ε,T} > 0 (R16) | C_ε(0) − C_ε(2) | AH-pairs | F near α = 2 |
| prime variance V̄_T < A (R19–20) | ∫p(y)C_{Ty}dy | AH-pairs | same, via GM dictionary |
| Mellin/operator (R27–28) | ‖C‖_op, sup_t|𝓜_T(t)| | AH-pairs | Σ_ρ ã_t(ρ), i.e. F beyond 1 |
| Level B / depth (r1, Part I) | liminf (log T)²D_T < π²/8 | AH-strong | μ < ½ (under NR) |
| impostor/fibre, Nyquist, moments (Part I) | finite-model statistics | none for ζ | — |

Proof of the claim for the first five rows: each is, by the displayed reductions (all [P] under RH), an integral of F_T against a fixed kernel plus o(1); its band part is known (Montgomery) and identical for AH and GUE; what remains is F_T on |α| > 1. For the depth row: Theorem A′. There is no sixth kind of route in the programme: the "arithmetic" inputs used (explicit formula, Bombieri–Vinogradov, Vaughan, sieve upper bounds, RH prime estimates, Möbius cancellation under RH) are all consistent with AH's prime shadow — this is the content of Rounds 8–28 having failed to close, and of Tao's "comparable to averaged Hardy–Littlewood with power saving": AH's shadow is a specific prime-pair covariance (Round 21–26: Z_T → A − 2M rather than −M) that no proven prime estimate contradicts. **This is Tao's point restated**: one out-of-band F value suffices, and it costs an averaged two-prime asymptotic with power saving.

### 3.3 What Rounds 8–28 actually achieved toward F beyond 1, and the single missing inequality

All under RH unless stated; all are reductions, none is a bound on F beyond 1.

| round | result | scale reached | scale needed |
|---|---|---|---|
| 8 | short-prime projection: W_T = B + E_T + o(1), B = 0.4560940; centred-ψ representation of E_T; positivity minorant −0.2087 | exact identity | E_T ≥ −0.3936 |
| 9 | 186-paper transfer: complementary-modulus Möbius–log correlations to X^{0.523}, per-shift O_A(X log^{−A}X) (unconditional) | X log^{−A}X per shift, HX log^{−A}X summed | X log X |
| 10 | smooth shift packet: |𝔇_Q^V| ≪ √(HX(X+Q²)) log⁴X (unconditional) | X^{1.023+θ/2} | X log X |
| 11 | RH small-arc: |𝔇_Q^V| ≪ X^{1.023} log⁵X; conductor lower bound ≫ H/log^{348}X kills coefficient-only savings | X^{1.023} | X log X |
| 12 | three exact no-go's: positive sampling is crowded; phase absorption fails Siegel–Walfisz (mod-3 witness); Selberg/Saffari–Vaughan caps lose the sign | — | — |
| 13–14 | rational-core extraction X^{923/1000}; exact Type-I removal: 𝔇[Λ_{≤U}] = o(X log X) for U ≤ X^{0.477−η} | done | — |
| 15 | Vaughan: 𝔇[Λ] = 𝔇[μ_{>A} * β_B] + O(X^{1711/1750}log²X); β_B has Siegel–Walfisz; remainder signed, vanishes on primes | exact | o(X) per dyadic block, unproved |
| 16–18 | Bragg-atom target; exact pole-cancelling packets; functional-equation trace with all residues; the H² ≠ |H|² warning | exact | strict deficit, unproved |
| 19–20 | positive prime-variance V̄_T; exact RH transfer V̄_T = ∫p(y)C_{Ty}dy + o(1); height regularity | exact | liminf V̄_T < A |
| 21–24 | renormalisation (singleton, parity, mod-6, growing wheel), all odd shifts removed, nonprimitive removal X^η/T, joint main cancellation | exact | — |
| 25–26 | central-scale packet 𝒫 = 𝒵_Q^{(2)} + o(1) at X = T²; **full-range reduction V̄_T = Z_T + 2M + o(1)** with the nonzero singular-series constant | exact | liminf Z_T < A − 2M |
| 27–28 | central divisor band removable; pure-divisor moments calculable; Mellin transpose pairings reach 35–55 % of ‖C‖_op at X ≤ 1.6·10⁷ | exact / finite | operator norm ‖C‖²_op ≪ X(log X)^{2−δ}, unproved |

The single missing estimate, in Astra's final normalisation (Round 26, RH), with M = ∫ω ≈ 0.18515 and A = 1 + ε²m₁ ≈ 1.01059 (ε = ¼):

  **`liminf_{T→∞} Z_T < A − 2M ≈ 0.64028`,   `Z_T = 2 Σ_{m odd, h even} b_T(m) r(m/2U) r(Th/Rm) (m/(m+h))^T c_T(m,h) [Λ(m+h) − 2]`,**

where c_T(m,h) = Σ_j β(h/Y_j) c_{Q_j}(m), c_Q(m) = Σ_{d|m, d>Q} μ(d) log(m/d), b_T the Pareto mass weight on [T^{7/4}, T^{9/4}]; the inherited RH bound is only Z_T ≤ A − 2M + o(1). In F-language it is the same inequality as `limsup C_{ε,T}(2) < 1 + ε²m₁`, i.e. an upper bound on the spectral mass of the zeros in the ε-window around α = 2 — one instance of §2.6.

---

## 4. Verdict on "prove a major conjecture from this angle"

**Provable now (and proved):**
1. Theorem 9.1: RH + AH-pairs ⟹ W_T → W_AH ∈ (0.06239, 0.06240); hence liminf W_T ≥ 1/16 refutes AH-pairs under RH.
2. Theorem 9.2: W_T = B + E_T + o(1), B = 0.4560939793, with E_T an exact centred-ψ energy.
3. Theorem 2.1 here: F_AH satisfies every RH-only theorem about F; inf of W over (i)+(ii-F)+(iii) is −∞; over (i)+(ii-μ)+(iii) it is 0.0236; the minimiser is explicit; no derivation from these inputs (nor from band-limited correlations of any order, nor integrality) proves the target.
4. The reduction of the target to `limsup 2∫_{α₀}^∞|K|F_T ≤ 0.3967954` (|K|-average ≤ 1.0420), and the identification of AH's advantage with its even-integer Bragg atoms (e^{−2} − e^{−1}).
5. The dictionary α ⟷ h = x^{1−1/α} and the Goldston–Montgomery / Montgomery-representation translation to short-interval prime variance.
6. Theorem A′ and the Level B ⟹ μ < ½ implication under (NR); λ* = 0.4719538; the failure of the periodised shortcut.
7. Rounds 8–28's reductions listed in §3.3, each [P] under RH with independent review.

**Not provable now, by anything in the programme or in the literature as read:** liminf W_T ≥ 1/16; liminf Z_T < A − 2M; any positive Bragg deficit; μ < ½; Level B; a refutation of AH-pairs, AH-strong, AH-mult or AH-dens; Montgomery–Dyson; RH.

**The exact minimal new arithmetic input for an AH-pairs refutation through this angle** (any one of the following, each equivalent to the others up to the fixed kernels; all under RH):

  **`limsup_{T→∞} ∫_ℝ ψ((α−2)/ε) F_T(α) dα < 1 + ε² ∫|v|ψ(v)dv`  for one fixed ε ∈ (0,1) and one fixed nonnegative ψ with ψ̂ ≥ 0,**

equivalently `liminf_T V̄_T < A_ε` for the exponentially length-averaged centred variance of ψ(x + x/T) − ψ(x) − x/T over x ∈ [T^{2−ε}, T^{2+ε}], equivalently `liminf Z_T < A − 2M` for the Möbius–prime covariance above. This is an **upper bound**, of relative size 1 % below the AH value (A − 1 = 0.0106 out of 1.0106) at the frequency-2 atom, or 4 % above the GUE level in the |K|-averaged form; it concerns primes in intervals of length ≍ x^{1/2} (α = 2) — the scale at which no asymptotic for the variance is known and at which Siegel zeros would distort the answer. No smoothing, no change of test function, no finite-model computation, no heat-flow argument and no positivity argument substitutes for it, because the AH point process satisfies all of those.

---

## 5. Sources: read, snippet-only, recalled

- **Read in full (local):** `NEW_RESULTS.md` §7, `PROGRAMME_PAPER.md` §§7–9, `dyson_round7.md` … `dyson_round28.md`, `TWO_SCALE_ZETA_TARGET.md`, `r1_levelB_barrier.md`, `tao_ah_notes.pdf` (programme-authored secondary source, 8 pp.).
- **Search snippets only (no full text reachable):** Tao, *The alternative hypothesis for unitary matrices* (8 May 2019); Lagarias–Rodgers, Q. J. Math. 71 (2020) and Ann. Appl. Probab. 31 (2021); Goldston–Lee–Schettler–Suriajaya, arXiv:2507.06823; Baluyot–Goldston–Suriajaya–Turnage-Butterbaugh, arXiv:2508.10857; Conrey–Iwaniec, Acta Arith. 103 (2002); Rodgers–Vallabhaneni, Glasgow Math. J. 66 (2024); Goldston–Gonek–Montgomery, Crelle 537 (2001); Goldston, Crelle 385 (1988); Goldston–Montgomery (1987); Farmer–Gonek–Lee, JLMS 90 (2014) (bibliographic data only).
- **Recalled, not verified:** the exact statements of Montgomery's theorem with the Goldston–Montgomery error term, Goldston's 1988 range/hypothesis, the Goldston–Montgomery uniformity ranges and constant ½, the GGM constant (1−e^{−2a})/(4a²) (verified numerically against Astra's independently reviewed derivation, which does not cite GGM's constant), Tao's Theorem numbering, the μ-record.
- **Scripts:** `push_D_constants.py` (kernel, W_GUE, W_AH, B, tails, u*, k ≥ 0), `push_D_ah_exact.py` (exact AH decomposition into continuous and atomic parts), `push_D_lp.py` (cutting-plane LP; logs and minimisers `push_D_lp_gold{0,1}.log/.json`).
