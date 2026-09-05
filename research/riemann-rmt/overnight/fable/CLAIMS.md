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

| A3 | CβE general-β background bound, reusing Theorem B'; repaired after refutation (BB-LD's near-diagonal density definition was dimensionally wrong — missing an N-rescaling of the sine argument, false even at β=2 as originally stated; corrected and re-derived in one clean pass; a directional numerics claim was also withdrawn after an 8-seed robustness sweep contradicted it) | P for β∈{1,2,4} modulo Feng-Wei; general β modulo BB-LD too (both cited, not proved) | r1_cbe_background.md |
| F1 | Astra task001 arithmetic-transfer derivation; repaired after refutation (the S2² Selberg-Delange moment derivation was arithmetically self-contradictory — claimed leading coefficient 6a², correct value is 6a, though the coded numeric value was already right; a headline 4-point numerical table mixed rows from different v at small L with correct v=1 rows at large L) | mixed: normalisation + leading S2 moments proved modulo recalled Selberg-Delange; kernel derivation exact algebra; M2 insertion-term transfer and M3 completeness remain open | astra_tasks/task001_F1_arithmetic_transfer.md |
| F3 | diagonal-operator Fock-space spectrum (Astra §12); repaired after refutation (a sign error in the K=½Φ²−½[A,A*] identity from a silent operator-order swap; the claim that the truncated commutator acts as a scalar on a whole mass-v sector is false for multi-particle states — up to 13× spread within a fixed-mass sector — withdrawn to "one-particle sector / untruncated space only") | **notable cross-validation**: extrapolated λ_∞≈4.6456 (Lanczos on the Fock-space truncation, M up to 55) independently matches Astra's own richer symmetric-prime-feature search (λ≈4.6455, from residual_gram_round1.md §8) to 3-4 significant figures via two structurally unrelated computations; no rigorous bound vs the π²/2=4.9348 threshold either way — the wall question stays fully open | r2_diagonal_operator_spectrum.md |

## Astra intake-review corrections applied (11:5x UTC)

Astra's `fable/reviews/pr11-89393d5/` intake review (INTAKE_REVIEW.md, BACKGROUND_AND_BOUNDARY_REVIEW.md
in the new repo) found five real issues in commit 89393d5's content. All are now fixed directly in the
source files (not just noted):

| # | file | issue | fix |
|---|---|---|---|
| 1 | `r1_cue_background.md` | Proposition 3.3 regime-2 had a **reversed inequality** (N<(L/4)³ was used to claim 1/N<64/L³, which is backwards) — the stated constant 1054/1055 was not established as written; fails outright for small fixed N, L→∞ | Split regime 2 at the deterministic threshold L=2πN^(1/3) (pigeonhole δ_min≤2π/N); correct reciprocal direction in the remaining bounded sub-range. New constants 4086 (Prop 3.3) / 4087 (Theorem 1, Theorem 1′, Corollary 5.5, the LR-bridge tightness section) replace 1054/1055 throughout. Verified by `scripts/r1_cue_background_prop33_repair_check.py` (confirms the original direction fails, the repair holds, plus small-scale Monte Carlo). |
| 2 | `r1_cbe_background.md` | BB-LD near-diagonal density definition missing an N-rescaling (already caught by our own A3 refuter and repaired in 2073028 before Astra's review landed) | independently confirmed consistent; no further change needed |
| 3 | `r1_cbe_background.md` | Fact 1.1 overclaimed that ρ_1≡N/2π **alone** gives the 1-sided counting-function bound N_ab(ρ) needed by Lemma S, for CβE "exactly as it does for CUE" — false (Astra's rotated-cluster counterexample: uniform 1-point density is compatible with an arbitrarily bad single realization) | Corrected in place: ρ_1 is only a first-moment fact; the probabilistic hypothesis needs BB-LD+Feng-Wei (§2-3), never claimed as following from ρ_1 alone |
| 4 | `r1_cue_background.md` / depth theorems | static-stiffness-persists-to-collision caution | already correctly conditional ([P] modulo (E-B*), (E-BAB)); no overclaim found, no change needed |
| 5 | `r1_levelB_barrier.md` | the "periodised version [P, no hypothesis]" claim that a small circular depth ⟹ an actual zeta gap < ½ is **wrong**: the circle's minimising gap can be purely the window-boundary **wrap gap** (Astra's counterexample: N points 0..N-1 in a window of length N-1+ε have all internal gaps =1 but wrap gap =ε) | Downgraded to [O] pending a non-wrap witness; the (NR)-conditioned line version (Theorem A′, unaffected — no window boundary) remains the operative [P] result; propagated through §0, §2.2, §4 verdict, and the claim ledger (new row B1-7′) |

Also fixed independently (not from Astra, from our own refuters, recorded earlier): the F1 refuter's own
sign-error probe (labelled +6, computed -6; did not affect the final m4=a²+6a) — see the
`astra_tasks/task001/refute_F1_rigour.py` patch and the file's own repair-pass note.

Net effect: no headline verdict in any of the three files reverses (CUE background bound survives with
a larger explicit constant; the CβE elementary machinery was already correctly scoped once the one
overclaiming sentence is removed; Level B still implies μ<1/2 under (NR), just not "for free" via
periodisation as originally overclaimed). This is exactly the kind of adversarial cross-review the
collaboration is for.

## Astra's intake review of 2073028 (12:31 UTC round-13/14 checkpoint)

A second real correction, applied directly: `r2_diagonal_operator_spectrum.md` claimed the crude
Cauchy–Schwarz/number-operator bound on `‖Φ‖` is *literally infinite* on the mass-≤1-truncated Fock
space (using the generic particle-number bound, correctly noting particle number is unbounded
there). **This was wrong.** Astra's `F3_MASS_CUTOFF_BOUND.md` gives the correct fix: weight the
Cauchy–Schwarz estimate by *mass* (`E`), not by raw particle count — since `E≤1` on the truncated
space by definition, this gives directly `‖Φ‖≤2√(B_g²)`, `‖K‖≤2B_g²` with
`B_g²=∫₀¹|g(u)|²/u²du=2π·Si(π)−4≈7.63606367`, hence `‖K‖≤15.2721` — **finite**, not infinite.
Verified independently here (`astra_tasks/task001/f3_mass_weighted_bound_check.py`, agreement to
30 digits with Astra's closed form). Practically nothing changes: 15.27 is still far above
`π²/2≈4.9348`, so the corrected (finite) bound gives no more information toward the wall question
than the wrong (infinite) one did — but the earlier claim was still false as stated, and is now
fixed throughout the file (top summary, §3.1–§3.3 rewritten, §5 verdict, ledger row F3-3).

The intake also flagged (already known/consistent, no new fix needed): the F1 refuter's own sign
probe (already fixed by us, independently reproduced by Astra); the general-β repair still needing
recorded corrections (tracked in `r1_cbe_background.md`'s own open items); a units caveat about
memory reporting on the source scripts (macOS vs Linux `ru_maxrss` units) — noted, not acted on
since these scripts only ran on this Linux container.

## Astra's follow-up review of r1_cbe_background.md (12:31 UTC checkpoint, CBETA_REPAIR_REVIEW.md)

A third, substantial correction round applied directly (this is the file's **second** repair pass;
Astra's verdict was "partial repair, not an accepted proof as written"). Five genuine defects fixed:

1. **BB-LD sanity check's Taylor coefficient was wrong** (`1/12`, the N→∞ limit, instead of the exact
   finite-N `(1−N^{−2})/12`), and the "bounded on any compact `[0,s₀]`" claim is false once `s₀`
   reaches `2π` (exact counterexample: `d=2π/N` gives density ratio 1 against a comparator that is
   exactly 0 there). Fixed by restricting the statement to `s₀<2π` explicitly — this was already all
   the file's own downstream uses needed (`s₀≥1` only), so nothing else breaks.
2. **A transcribed partition-function formula was wrong** (β=2,N=2: displayed `4(2π)²`, correct is
   `2(2π)²` by direct integration, verified independently here) — flagged in place; it was already
   marked "not used" but should not have been left as if verified.
3. **Proposition 3.1's proof used an invalid relative-error step**: `v′=v(1+O(1/N))`, which is false
   near `v=0` (Astra's exact counterexample: `x=0,y=ε/2,z=−ε²/w` gives `v′/v→∞`). Replaced with
   Astra's robust alternative — bound the far distance crudely, `v′≤v+u≤w+ε`, requiring a new,
   explicitly named hypothesis **(U3)** (distinct from BB-LD(3,·) as originally defined). The headline
   exponents `L^{β+1}c^{2β+1}` survive exactly (verified independently here, both symbolically and
   numerically across β=1,1.5,2,4, `scripts/r1_cbe_prop31_ncheck.py`) — the repair changes the route,
   not the conclusion.
4. **The "[P] for β∈{1,2,4}" BB-LD status line overclaimed**: the n=3 case (needed by Prop 3.1) and the
   β∈{1,4} cases were never actually verified, only asserted by citing that exact Pfaffian formulas
   exist. Downgraded to open except the single case (n=2, β=2) explicitly checked.
5. **An equality should have been an inclusion**: `P(E_1)=P(T≥1)` → `P(E_1)≤P(T≥1)` (a different,
   non-minimal pair can trigger `T≥1` without the minimal pair having a nearby third point).

Net effect: no headline verdict reverses (A3(a)/(c) remain "[P] modulo an explicit, mostly-open
hypothesis," now named `(U3)` instead of the less precise "BB-LD"; the honest weakest-link accounting
is, if anything, sharper than before), but several intermediate "[P]" tags were wrong as stated and
are now correctly scoped. Full detail in `r1_cbe_background.md`'s second repair-pass note (top of
file) and inline "Correction"/"Repair box" annotations at each defect site.
