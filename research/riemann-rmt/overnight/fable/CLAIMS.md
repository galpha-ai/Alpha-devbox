# Claims ledger (Fable overnight)

Format: `| id | claim | status | file | notes |`. Status in {P, C, R, O}. Refuter votes recorded.

| id | claim | status | file | notes |
|---|---|---|---|---|
| D1.2 | product-ansatz layer-cake bound M_k >= c2^-1 sum_j max(0,1-beta_j)(G(b_j)^2-G(a_j)^2) with chord-Chernoff / one-big-jump / Berry-Esseen tails is valid | P | r1_h2_interval_cert.md §2 | Lemmas 1-6 written out; any tail bound family works |
| D1.3 | M_15856 >= 8.013326752751306578613695503115 (exact rational; C_BE=0.56, elementary Phibar), outward-rounded (arb 200 bits) and cross-checked with mpmath.iv | C | r1_h2_interval_cert.md §3, data/h2_k15856_interval_cert.json | margin 0.01333; reproduces historical JSON bit-for-bit |
| D1.4 | M_15856 >= 8.00677408008999410774 with NO Berry-Esseen input (Markov + convexity only); M_923601 >= 12.00263034990571191492 likewise | C | r1_h2_interval_cert.md §3.2, §3.6 | H2/H3 records need only Maynard + Bombieri-Vinogradov |
| D1.6 | p9_tuple_k15856.npy: 15856 entries, diameter 173438, admissible for all 1847 primes <= 15856 (two implementations) | C | r1_h2_interval_cert.md §4 | prime count confirmed by sympy.primepi |
| D1.7 | committed p9_certify_hp.py is mpmath dps=50 + SAFE=1+1e-30, not outward rounding (Astra audit confirmed); JSON came from an uncommitted arb script, now copied with sha256 | R | r1_h2_interval_cert.md §1.5, scripts/r1_h2_reference_p9_exact_cert_scratchpad_copy.py | repaired by D1.3/D1.4 |
| D1.8 | Maynard/Polymath theorem statements and BE constants are recalled not re-read; arb library trusted; k=923601 tuple not re-verified tonight | O | r1_h2_interval_cert.md §5, §8 | |
| A1.1 | cot(x/2) − cot((x+g)/2) = sin(g/2)/(sin(x/2) sin((x+g)/2)); background bracket B = 2 sin(g/2)·S_exact exactly | P | r1_theoremB_repair.md §2 | identity checked to 1e-14 on 1200 configurations |
| A1.2 | 0 ≤ B ≤ g·S* with S* = Σ ½max(csc²(x_b^k/2), csc²(x_a^k/2)) = ½Σ csc²(dist(θ_k,{θ_a,θ_b})/2); also B ≤ g S_exact ≤ g S_avg ≤ g S* | P | r1_theoremB_repair.md §2 | endpoint max because csc²(t/2) is decreasing on (0,π], increasing on [π,2π) |
| A1.3 | old bound B ≤ g·S_old (depth_scaling_theorem.md §4) is false; fails in 34–49% of CUE/ACUE configurations, by up to 57% | R | r1_theoremB_repair.md §2, §7 Table 1 | Astra's counterexample confirmed |
| A1.4 | −4/g ≤ −2cot(g/2) ≤ −4/g + κ(δ/2)g for 0<g≤δ≤π, κ(x)=(1−x cot x)/x² increasing, κ∈(1/3,4/π²] | P | r1_theoremB_repair.md §3 | replaces the hidden O(g) |
| A1.5 | Theorem B′: if S*(s) ≤ Θ S*(0) on [0,D)∩[0,δ²/4] and μ=ΘS*(0)+κ₀ has μδ²≤2 then −log cos(δ/2) ≤ D ≤ −(2μ)⁻¹log(1−μδ²/4) ≤ (δ²/8)(1+μδ²/4), whichever pair collides first | P | r1_theoremB_repair.md §4 | linear inequality for g², no comparison lemma; direction of integration and constant re-checked |
| A1.6 | static bound: N_ab(ρ) ≤ CNρ+m₀ on [r,π] ⇒ S*(0) ≤ N/2 + 4CN/r + 2m₀/r²; m₀=0 forces Nr ≥ 1/C and S*(0) ≤ N²(4C²+1/(2N)) | P | r1_theoremB_repair.md §5.1 | layer cake; dyadic gives 8CN/r + (8/3)m₀/r²; 1/(Nr)² term only from exceptional points |
| A1.7 | window lemma: S*(s) ≤ S*(0)/ψ(τ)² on [0,D)∩[0,τ] with ψ from the unconditional gap bound g_i(s)² ≥ g_i(0)² − 8s; Θ=2 if all other gaps ≥ 2δ, or under one-sided density (H_C) with CNδ ≤ 0.2071 | P | r1_theoremB_repair.md §5.2 | uses only Theorem A on every gap; pair's fast motion is inward and harmless |
| A1.8 | "S* changes by ≤ 2 when D ≤ δ²/4 and Nδ ≤ 1" is false without a neighbour-gap hypothesis: 3-cluster with neighbour gap 1.01δ gives sup S*/S*(0) = 9.5 | R+C | r1_theoremB_repair.md §5.2, scripts/r1_theoremB_check.py [CLUSTER3] | |
| A1.9 | explicit corollary: (H_C), CNδ ≤ 0.2, Nδ ≤ 1 ⇒ δ²/8 ≤ D ≤ (δ²/8)(1 + 4C²N²δ² + 0.29δ) | P | r1_theoremB_repair.md §6 | CβE rate N^{−2/(β+1)} with explicit constant, conditional on (H_C) w.h.p. |
| A1.10 | numerics: CUE N=16,32,64 (300 each), ACUE (100 each), dislocation, clusters: D ≤ T(sup S*+κ₀) in every sample; D certified to 1e-6 by 60-digit brackets; dislocation N²D → 1.419640 | C | r1_theoremB_repair.md §7, data/r1_theoremB_check.json | np.roots unusable at N=64; exponent-symmetry bug in mp flow found and fixed (§9) |
| A1.11 | regularity hypothesis for CβE reduced to static (H_C) + CNδ_min ≤ 0.2 with probability → 1; unproved | O | r1_theoremB_repair.md §8 | input for r1_cue_background.md |
| A1 | Theorem B repair with endpoint-max stiffness S* (Astra's counterexample fixed); Theorem B' with explicit window hypotheses | P (several sub-lemmas O) | r1_theoremB_repair.md |
| A2 | CUE background bound S*/N² tight w.h.p. from 3-point sine-kernel clustering + extreme-gap tightness; N^{8/3}D→G²/8 | P modulo two cited black boxes | r1_cue_background.md |
| B1 | Level B vs μ<1/2: exact τ/t normalisation, Level B⟹μ<1/2 under (NR); one-defect λ*=0.4719538 exact; verdict "relabelling, not shortcut, under AH-strong" | P/C, one O (truncation D_T≈D_T^per) | r1_levelB_barrier.md |
| C2 | Adversarial review of "new structures": operator unification standard (Calogero-Sutherland/DBM linearisation); chiral-blindness Theorem E1 (new, proved); **marked-depth law refuted as circular (S5)**; **Theorem A's practical direction reversed (S10)**; **depth is non-smooth on a positive-mass set (S11, refutes impostors_paper.md §1.5)** | mixed P/R/C, see file | r1_structure_review.md |
| D1 | H2 record (k=15,856) re-certified in exact rational + arb ball arithmetic; M≥8.0067 with NO Berry-Esseen input (margin 0.0068 over threshold 8); bonus H3 M≥12.0026 | C (rigorous certificate, two independent backends) | r1_h2_interval_cert.md |
| F2 | Astra task001 finite-sum diagnostic: reproduces Astra's λ_max(K_L) to 10 digits; J_L negative at all tested L for all four H variants; two-term 1/log L extrapolation lands within 2e-4 of Astra's continuum value | C (diagnostic only, no proof) | astra_tasks/task001_F2_finite_sum_diagnostic.md |
| A3 | CβE background bound (β general) | not started (credit exhaustion; queued) | — |
| B2 | CGG mollifier limits on μ | not started | — |
| B3 | zeta-zero depth numerics | not started | — |
| C1 | what 0.6725 is / pair+triple LP ceiling | not started | — |
| D2 | sub-186 wall k=38-40 | not started (Astra's prime186 rounds 4-6 supersede much of this) | — |
| B4-B6 | LR hard-core LP / function-field / DBM relaxation | not started | — |
| F1/F3 | Astra task001 arithmetic transfer / diagonal-operator spectrum (Astra §12) | not started (queued next) | — |

**IMPORTANT NOTE ON THE ABOVE:** rows A1/A2/B1/C2/D1/F2 were marked "failed" by the workflow harness's
own bookkeeping (the proposer agent's *final structured-output call* hit the Fable session credit
limit, so the harness recorded an error and an empty result) but the agent had **already written its
deliverable file to disk** in an earlier tool call before failing. Recovered by direct inspection at
10:42 UTC after the credit reset (resets 10:40am UTC per the failure messages). None of these six
files received their adversarial refute pass — read them as single-proposer drafts, not verified.

## Gap-fill batch (workflow w623on41v, started 10:47 UTC)

| A3 | CβE general-β background bound, reusing Theorem B' | proposer done (r1_cbe_background.md); refute pending | r1_cbe_background.md |
| F1 | Astra task001 arithmetic-transfer derivation | proposer done (task001_F1_arithmetic_transfer.md); refute pending | astra_tasks/task001_F1_arithmetic_transfer.md |
| F3 | diagonal-operator Fock-space spectrum (Astra §12) | in progress at last check | — |
