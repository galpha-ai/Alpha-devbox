# Round-3 Synthesis: Ten Directions Coupling the Two-Thirds Method to the Finite Fiber Program

**Bill (Qingyun) Sun · GPT5.6SOL · Fable** — *August 11, 2026*

All ten agent reports complete; every quantitative claim below carries its origin (Direction n) and epistemic tag from the underlying report. Scripts in the session scratchpad; Lean citations to `anthropics/zeta-23-lean` @ 3635e74.

---

## 0. The headline in three sentences

Reading Anthropic's method at the Lean source (not through paraphrase) and coupling it to the finite ACUE fiber machinery produced: **one near-miss improvement of the headline constant reduced to a single missing operator lemma with quantified payoff (+0.007 to +0.012)**; **five new provable theorems about the method itself** (a rigidity upgrade of Lemma R, a strictly stronger distinct-zeros decoding, an exactly flat RH-independence frontier, an edge no-go, and a weight-freezing no-go); and **the first explicit closed-form resolution of the mimicker fiber** (the center-of-mass modulation family), together with an exact price list — in prime-correlation currency — for every escape route past 0.6725.

---

## 1. The near-miss: 0.6725 is one operator lemma away from improvable (D1 + follow-ups)

The most consequential finding, established over three rounds of adversarial checking:

1. **The face identity is a flat-window accident.** The reason tr Q³ appears worthless is that the *flat-window* sine–Gram data sits exactly on the {0,1,2} factorial face: m₃ − 3m₂ + 2m₁ = 0 (an identity holding at *every* finite N for ACUE — new rigidity fact). But at the **Montgomery–Taylor window itself**, Φ₃ = m₃ − 3m₂ + 2m₁ = **−0.0117753128** ≠ 0 (closed trig form obtained; verified symbolically, numerically at 30 digits, and independently on the ACUE lattice to 3·10⁻⁷). The third moment genuinely carries new information exactly where the proof already lives.
2. **The blocker is not arithmetic.** tr Â³ at bandwidth one is licensed by the ⌊k/2⌋·L support staircase (D1; consistent with papers XI/XII). The blocker is that Lemma R's hypothesis class carries **no bound on the size of the compression's negative eigenvalues** — the in-window off-line blocks are constrained in count (n₊ ≤ p) but not in magnitude, and the Φ₃-deficit escapes through that channel.
3. **Window engineering cannot fix it** (adversarially settled): the RvM clump term (log T zeros per unit ordinate at zero kernel decay) forces the row-sum cap M = A₀·log T for *every* window; edge-vanishing windows only improve the negligible far field, cost ≥ 0.006 in 2−q(w), and flip Φ₃ to the unmonetizable positive side.
4. **The surviving target, precisely:** a zero-side lemma `‖(c⁻¹Â)₋‖ ≤ M₋` uniform in T. Payoff at the MT window with the capped cubic decoder: **δ = 0.6796896 if M₋ = 2, up to 0.6844924 if M₋ ≤ 1** — no window change, tr³ the only new prime-side input. Required: depth-uniform control of off-line evaluation vectors (a cosh-weighted Poisson analogue + overlap-angle bound). This is now the sharpest known formulation of "what would improve 0.6725 without new correlation ranges."

*(Cross-check from D2: the true bandwidth-one ceiling is strictly above δ_MT — measured integrality gap ≈ 0.0093 — so headroom exists; the M₋ route targets exactly that headroom.)*

## 2. New theorems about the method itself

**2a. Stability/rigidity of Lemma R (D4) [PROVED].** The exact 7-term deficiency decomposition turns Lemma R into an identity (verified 7e-14; identically zero on the TightMult class), and the rigidity theorem with constant 1: an ε-near-equality configuration lies within Frobenius distance √ε of an exact equality configuration (Löwdin frame). Zeta-side ledger: total deficiency over MT windows ≤ (q\*−1)·N(T) = 0.3275·N(T), yielding a new unconditional pair-repulsion-type bound (on-line pairs with taper overlap ≥ τ number ≤ 0.1637·N(T)/τ²) and forcing hypothetical off-line zeros to look exactly like eigenvalue-2 pair blocks. Bonus reading: q(window) = m₂(window-Gram) — **Montgomery–Taylor optimization *is* minimization of the RMT-predicted deficiency**, and under GUE the budget is exhausted by the Schur/von-Neumann term alone.

**2b. The distinct-zeros upgrade N_d ≥ 0.8362503·N + p (D7) [PROVED; ~5-line Lean edit].** Combining the c=2 inequality with the zero-count identity once (not twice) gives slope +1 in the off-line pair density — strictly stronger than the repo's own c=3 decoding (slope ½; pairs mispriced at c²=9 vs forced value k₃(2)=8). Companion facts: the **simple-zero frontier is exactly flat** — δ(π) ≡ 0.6725007 for all π ∈ [0, 0.16375], hence **assuming RH buys nothing within this method** (the binding adversary is on-line doubles; exact 4p-budget/mass cancellation); at maximal off-line density all zeros are forced simple; the data forces pair-block spectra to (≈2, ≈0).

**2c. The edge no-go (D5) [PROVED].** Every admissible bandwidth-one window has r̂(±1) = 0 (two-line Fejér–Riesz), so the weakest pointwise edge hypothesis |F(1)−1| ≤ ε certifies exactly 0.6725 — even at ε = 0. The finite Nyquist conservation law is powered by lattice aliasing that ℝ lacks; the correct zeta-side edge object is the Cesàro mean F̄(∞,T), with the exact collision identity C(T) = N\*·F̄(∞,T) − N(T). New reading: TightMult + PairCeiling/Signed = "the 2026 certificate is edge-blind by construction, and optimally so." Genuine new target: an unconditional *upper* bound on the edge-cell average of F via the Nyquist-blind null window (r(0) = 0).

**2d. Weight-freezing (D9) [PROVED].** Derivative power sums are weight-homogeneous in the original power sums, so all bandwidth-one holomorphic statistics of the derivative process (ξ′-analog) are frozen on the fiber — "differentiate then pair-correlate at bandwidth one" cannot work, and the Lean ξ′ gain (→ 0.86864) is purely arithmetic (the D₁ coefficient density). But the transport is real in *modulus/counting* observables: at N=6 the 1-point radial law of critical points resolves 7/10 fiber dimensions (κ = 2.14× the best direct 4-point statistic), and **AH is not closed under differentiation** (exact N=3 counterexample). Finite Hardy identity: on-circle stationary points = roots of zZ′ − (N/2)Z, all on the circle.

**2e. The no-escape lemma for certificates (D2) [PROVED]** — validity against the optimal period-M adversary forces c₀ + ∫r·x ≤ V_M by a Riemann sum with no regularity assumption: the stability penalty buys rate, never limit. Quadratic-class certificates converge to exactly δ_MT (excess 0.31/M²): **MT is optimal in its class at every period, and the ≈0.0093 headroom above it is a pure integrality gap**, accessible only to integrality-aware certificates.

## 3. The fiber, finally explicit (D6 + D3 + D10)

**3a. The center-of-mass modulation family (D6).** q_g = q_ACUE · g(X mod N), X = Σx·m_x, is an exact balanced-moment mimicker iff E g = 1 and ĝ(±1) = 0 — an explicit **(N−3)-dimensional** family at every N (dims 0,0,2,3,4,5 at N=3..8, matching/entering the known fiber). The N=5 fiber is *completely solved*: a pentagon over ℚ(√5); the known mimicker is |v|² for a 5-sparse coherent superposition of translated Fermi seas; the destructive cross-spectrum constraint is the single syndrome a\*Sa = 0 (vanishing nearest-translate coherence). Mechanism: X mod N is exactly uniform under ACUE, and moment couplings to com-frequencies 2..N−2 vanish by a transport-cost bound (hop budget 2N vs cost ≥ 2N+2).

**3b. The minimal detector theorem (D3).** The cheapest observable with O(1) fiber leverage is E|p_a p_b|², a+b = N+1 — bandwidth exactly **1 + 1/N**; nothing cheaper exists (earthmover lower bound: fiber seas have displacement ≥ 2N+2). Dichotomy: bounded-likelihood mimickers (twists) cost bandwidth 2 − 4/N → 2 (twin-prime class); the cheap detectors work only on likelihood-degenerate directions. Prime-side price of the minimal detector: **h-averaged bipartite E₂×E₂ shifted correlations at length T^{1+1/N}** (dispersion-method-shaped, Linnik/Motohashi/BFI class). Open danger sign: leverage dropped 4.94 → 0.92 from N=5 to 6 — uniformity in N undetermined.

**3c. The arithmetic shadow and the two-scale cost law (D10).** The fiber's out-of-band profile: the first sliver past the edge kills 54–100% of the fiber with O(1) leverage, but the last direction survives to kill-degree d\* = 3(N−3) (α\* → 3, conjectured law). Free structural kill: the functional equation's reflection symmetry eliminates the entire chiral half of the fiber (39/80 dims at N=7) at zero cost — and provably cannot do more. All squared-modulus data saturates below full rank. Marginal-value curve: pinning F on (1, 1+ε] buys dδ/dε ≈ 0.68 at the edge; the AH deviation lives in the *constant term* of the ψ-variance at short shifts — the Siegel-zero price tag (Conrey–Iwaniec), consistent with everything above.

**3d. Deficiency blindness dichotomy (D4).** Lemma R's total deficiency is *exactly* frozen on the fiber (2-point functional); the fiber-detecting observables among spectral functionals are the interior clips Σ((μ−c′)₊)², c′ strictly inside (1,2) — the boundaries are blinded by two new lattice facts (spectral cap μ ≤ 2 exactly; particle-hole symmetry μ ↔ 2−μ), while the continuum sine-Gram violates the cap (support [0,3] — the Christoffel hard-edge).

## 4. The updated quantitative map

| object | value | status |
|---|---|---|
| headline constant δ_MT | 0.672500703679 | proved (repo) |
| conditional cubic upgrade (M₋ = 2 / ≤ 1) | 0.6796896 / 0.6844924 | one lemma missing (D1) |
| true bandwidth-one ceiling | 0.6818 ± 0.0015; candidate **15/22** exactly | D2 [CONJECTURE]; rigorous bracket [0.6725007, 0.6818287+] |
| quadratic-class ceiling | δ_MT exactly (excess 0.31/M²) | D2 [COMPUTED/PROVED] |
| lattice-union adversary cap | 1 − 3/π² = 0.69603 | D2 [PROVED] (totient forcing g = φ) |
| distinct zeros | N_d/N ≥ 0.8362503 + p/N | D7 [PROVED, unformalized] |
| off-line pair budget | p/N ≤ 0.1637496; at saturation all zeros simple | D7 [PROVED] |
| deficiency ledger | ΣD ≤ 0.3275·N(T); rigidity √ε | D4 [PROVED] |
| doubles density of any Nyquist equality law | → 1/4 − 1/π² = 0.148679 | D6 [PROVED identities] |
| fiber's cheapest detector | bandwidth 1 + 1/N; robust directions 2 − 4/N | D3 [PROVED at N=5,6] |
| fiber kill-degree | d\* = 3(N−3), α\* → 3 | D10 [CONJECTURE, verified N=5,6,7] |
| proved zeta rate | 1/log T (two removable first-order losses; true tower 1/L² conjectured) | D8 [read from repo + CONJECTURE] |
| the three N⁻² towers | one object: the Nyquist cotangent tower (Bernoulli tower of (cot, csc²)); exists only at the edge | D8 [PROVED forms + COMPUTED] |

## 5. Corrections and errata from this round

- The naive premises of three directions were *refuted* by their own agents (the healthiest sign of the round): pointwise edge hypotheses buy nothing (D5); derivative pair correlation at bandwidth one is blind (D9); window engineering cannot cap the negative spectrum (D1 follow-up). Each refutation came with the corrected statement.
- D8 flagged a discrepancy in an earlier verification-script closed form for the Galerkin ladder (two variants circulating; both match the QP after the θ_n fix under their respective normalizations — final reconciliation recorded in `dir8_exact_form.py`, whose two-generator form q_n = ½ + t_n·cot κ_n is verified to 60 digits and supersedes both).
- The finite N=8 fiber dimension re-derived as 399 vs the earlier 403 at tighter rank tolerance (D4) — worth an exact-arithmetic recount.
- Support-field version of the destructive cross-spectrum is *infeasible* on the hard-core face (D6) — the constraint's true home is the com-syndrome on the original fiber.

## 6. Ranked program (what to actually do next)

1. **The M₋ lemma** (D1): prove ‖(c⁻¹Â)₋‖ = O(1) via depth-uniform off-line vector control — worth +0.007..0.012 on the headline constant with tr³ at bandwidth one. The single highest-value open item.
2. **Formalize `mult_two_pair`** (D7): N_d ≥ 0.83625·N + p — a five-line Lean edit yielding a strictly stronger published constant.
3. **The transport-cost lemma** (D6): finish the proof of the com-modulation family — an explicit (N−3)-dimensional mimicker polytope at every N, the paper-ready core of the fiber theory.
4. **Uniformity of the minimal detector** (D3): N = 7, 8 leverage of E|p_a p_b|², a+b = N+1; decides whether the dispersion-method target (bipartite E₂ correlations at T^{1+1/N}) is the real gateway.
5. **Edge-cell upper bound** (D5): the Nyquist-blind null-window route to the first unconditional upper edge datum for F.
6. **Max-ent Gibbs family at N ~ 30** (D6) + the D8 tightness evidence: the all-N Nyquist equality law now looks provable; its doubles density and E|p_N|² are already pinned by the frozen identities.
7. **d\* = 3(N−3) kill-degree law** (D10) and the 15/22 ceiling identity (D2): two exact-arithmetic conjectures, both machine-attackable.

*Every claim above traces to a tagged agent report with scripts in the scratchpad; the four refuted premises are retained in §5 deliberately — the round's value lies as much in the closed doors as the opened ones.*
