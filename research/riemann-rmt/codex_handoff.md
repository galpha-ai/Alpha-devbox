# CODEX HANDOFF — Bounded prime gaps: formulas, methods, current state, and open computations

*Session handoff, August 15, 2026. Everything below is machine-actionable; file paths relative to the session scratchpad. Status tags: [P] proved, [X] exact-rational certified, [C] computed (float/hp, uncertified), [R] recalled-needs-verification.*

## 1. The framework in five formulas

1. **Variational constant.** R_k = {t ∈ [0,∞)^k : Σt_i ≤ 1}; symmetric F;
   I(F) = ∫_{R_k} F² dt, J^{(m)}(F) = ∫_{R_{k−1}} (∫₀^{1−Σ} F dt_m)² ; **M_k = sup k·J/I**.
2. **Threshold.** DHL(k, m+1) ⟸ M_k-variant > 2m/θ. Unconditional θ = 1/2 (Bombieri–Vinogradov): **> 4m**. With MPZ[ϖ,δ] (Polymath8a Deligne strength: 600ϖ + 180δ < 7): threshold **2m/(1/2 + 2ϖ)** but support truncated by δ (see §4). Then H_m ≤ H(k) = min diameter of admissible k-tuple.
3. **ε-trick.** Support (1+ε)R_k; J-integrals truncated to fibers with Σ_{j≠i}t_j ≤ 1−ε (vanishing marginal). Zero arithmetic cost. This is how Polymath8b got k = 54 → 50.
4. **Upper bounds [P].** M_k ≤ (k/(k−1))·log k ⇒ M₄₉ ≤ 3.97290, M₅₀ ≤ 3.99186 (pure door dead ≤ 50). ε-variants: M_{k,ε} ≤ (1+ε)(k/(k−1))log k ⇒ k=49 door *rigorously* closed only for ε ≤ 0.00682. No upper-bound technology beyond this exists for larger ε — the k=49 door is OPEN (Polymath: "undecided").
5. **Tuple side.** Admissible: for every prime p ≤ k some class mod p is missed. H(k) proven minimal ∀k ≤ 342 (Engelsma + our independent exhaustive re-proof ≤ 62). Ladder: H(46..50) = 216, 226, 236, 240, 246. Payoffs from k=50: −6/−10/−20/−30. Empirical H(k) ≈ k(log k + 0.77) at k ~ 10⁴ (fits (50,246), (35410,398130)).

## 2. Current numerical state (the live numbers)

| object | value | status | file |
|---|---|---|---|
| M₄₉ (pure, d=20 power-sum basis p≤5, dim 1125) | ≥ 3.891257590916 | [X] exact rational | `mt_hp_k49_p5.json` |
| M₅₀ (pure, same basis) | ≥ 3.907113699811 | [X] | `hpE.log` |
| M_{49, ε=1/35} (d=18 basis, n=1597) | float opt 3.959325169; **certified ≥ 3.930490592** | [C]/[X] | `p2_arb_d18_k49.log`, `p2_cert_d18_float.log` |
| M_{49, ε=1/25} (d=14) | 3.915989908 | [C] | `p2_arb_d14_epsscan.log` |
| gap to the k=49 door | 4 − 3.9593 = 0.0407 (float), 0.0695 (certified) | — | — |
| m=2 pure-BV crossing (M_k > 8) | **k = 15,856** (certified 8.00108 by the 1-D engine) | [C — ENGINE UNVERIFIED] | `p9_pure2.log` |
| m=2 Deligne crossing | **k = 13,467** (thresh 7.8273 at δ=0.0205, ϖ=0.00552) | [C — ENGINE+THRESHOLD UNVERIFIED] | `p9_del2.log` |
| m=3 pure-BV / Deligne | k = 923,601 / **660,985** | [C — same caveats] | `p9_pure3.log`, `p9_del3.log` |
| m=2 tuple search (k=35,265) | best diameter **397,352** vs record 396,504 | [C], search interrupted | `p4_run_*_d3973*.txt` |
| record H₂ | 396,504 @ k=35,265 (Stadlmann θ=1/2+1/40) | [verified via search] | — |
| P3's independent product-ansatz m=2 crossing | k ≈ 29,500 | [C, weaker engine] | `p3_m2_machine2.py` |

**If P9's engine and threshold chain survive verification, H₂ drops to ≈ H(13,467) ≈ 138,000 (Deligne) or ≈ H(15,856) ≈ 165,000 (pure BV) — a ~2.5–2.9× record improvement. This is the highest-value open verification on the board.**

## 3. The variational engines (how to compute M_k)

**(a) Exact symmetric-polynomial Galerkin (small k ≤ ~60).** Basis: monomials (1−P₁)^a P₂^b P₃^c … (power sums P_j = Σt_i^j), degree ≤ d. All I- and J-integrals reduce via the Dirichlet formula ∫_{R_k} ∏t_i^{a_i}(1−Σt)^b dt = ∏Γ(a_i+1)·Γ(b+1)/Γ(k+Σa_i+b+1) — assemble exact rational Gram matrices A (for kJ) and B (for I); solve the generalized eigenproblem; **certify** by exact rational Rayleigh quotient of the rounded eigenvector (numerator/denominator sizes ~600 bits at d=18). Engines: P1's (`hpE/hpD/hpM.log` conventions, precision-boosted inverse iteration 544→1570 bits) and P2's (`p2_*` — includes the ε-trick truncation: J-fiber integrals with upper limit 1−ε; assembly is the bottleneck, ~25 min for n=1597).
**(b) ε-scan protocol.** ε = 1/den rational for exact arithmetic; scan den ∈ {35, 31, 28, 25}; observed optimum near ε ≈ 0.0286–0.04 at d=14–18. Shift-invert accelerator: "[shift → 0.078...]" lines mark the spectral shift used.
**(c) 1-D product-profile engine (large k ~ 10⁴–10⁶) — P9's, UNVERIFIED.** Ansatz F = ∏g(t_i)·1_{R_k}; reduce I, J to 1-D integrals of g plus a truncation correction for the simplex constraint (Chernoff/exponential-tilt bound on P(Σt_i > 1) under the g-density). *The soundness of the certified lower bound hinges entirely on the direction of the truncation correction in both I (upper-bounded) and J (lower-bounded) — this is exactly where a sign error would fabricate records.* Read `p9_*.py` before trusting; re-derive the two-sided correction independently. P3's slower-but-cleaner variant (`p3_m2_machine2.py`, mpmath 30-digit) crossed at 29,500 — the 15,856 vs 29,500 gap between the two engines MUST be explained before any claim.
**(d) MPZ/Deligne thresholds (P9's del runs).** Parameters scanned: (δ, ϖ) ∈ {(0.008, 0.00927), (0.0143, 0.00739), (0.0205, 0.00552)} — the constraint is 600ϖ + 180δ < 7 [R: verify exact form + whether the k-dependent dense-divisibility truncation cost was correctly charged into the certified value; this is the weakest link].

## 4. Walls — do not spend compute here (all proved this session)

1. Ceiling = tuple diameter: no post-processing of MT output beats H(k_min). Pair-correlation upper-bound constants can never lower H₁.
2. Scalar decode optimal: convex-order two-point counterfeit kills all matrix/inertia/moment decodes; f(m) = 2m/θ final.
3. Weight cone closed: rank-r SOS decouples (subadditivity); copositive cone flat (9-pattern dual certificate, residual 1.3e-14).
4. Parity: kill-graph bipartite ⟺ killable; H ≥ 6 absolute floor for the method class; DHL(k,m+1) parity-blocked iff k ≤ 2m.
5. Guth–Maynard orthogonal to H₁ (zero-density inputs appear nowhere in the beyond-1/2 dependency chains); GRH gives only θ = 1/2.
6. Fixed-residue / well-factorable levels (BFI 4/7, Maynard II 3/5, Pascadi 5/8) structurally unusable by MT. Usable-restricted frontier: Maynard III 11/21 (uniform residues), Stadlmann 1/2+1/40, Pascadi minorant 10/19 — all shell-truncated.

## 5. Open computations, ranked (with method + acceptance criteria)

1. **VERIFY-P9 (record-critical).** (i) Re-derive the 1-D engine's truncation control two-sidedly; (ii) reconcile 15,856 (P9) vs 29,500 (P3); (iii) re-derive the exact DHL(k,3) criterion from Polymath8b (Thm 3.5-family) including all ε/truncation charges at MPZ[ϖ,δ]; (iv) re-certify the crossing k in exact arithmetic. Accept: an exact-rational certificate M-variant(k*) > threshold with every constant re-derived. Then: narrow-tuple search at k* (engine: §6) ⇒ new H₂.
2. **TUPLE-35265.** Beat 396,504: restart from `p4_run_*` state files (best 397,352). Methods that got there: shifted-Schinzel + greedy + class-swap annealing (mod-p re-choices, p ∈ [50, 2000], min-cost repair). Missing (2014's edge): iterated merging of two good tuples on overlapping windows; LP-based repair. Any diameter ≤ 396,503 with exact admissibility verification (every p ≤ 35,265) = world record.
3. **K49-DOOR.** Push (a)-engine to d = 20–22 at ε-scan granularity den ∈ {30…40} (warm-start from `p2_vec_hp_k49_d18_e35.npy`); if the float optimum plateaus < 3.98, run the vanishing-marginal variant (larger legal class, unexplored at k=49 — Polymath blog IX stopped at single-digit k). Non-separable dual certificates (weights on (t_i, u_i, P₂-fiber)) are the only known route to CLOSE the door above ε = 0.0068.
4. **SHELL-M49 (undecided in print).** Extract Maynard III divisor-window parameters → shell polytope Ω*; compute M₄₉(R ∪ Ω*) with ε-trick layered; needs only 8–13% of full-shell surplus. Inner/outer sandwich decides vs 4.
5. **P10 wrap-up.** `p10_corner_eig.log` calibrated; sideband corners give conditional zeta-side gains (+0.022 at B=4) — finish the BFI-range map and the honest verdict.

## 6. Tuple-search machinery (P4's, all in scratchpad)

`p4_rho_exhaust.c` (exact minimal diameters ≤ 62, ρ*-pruning + mod-3,5,7 branching + parity halving), `p4_verify_witnesses.py` (exact admissibility checker — run on EVERYTHING before claiming), `p4_bigtuple*.py` (Schinzel/greedy/anneal pipeline), state files `p4_run_{A,B,C,D}2*.{log,txt}` (four annealing chains, best 397,352). Exchange rates: ΔH₂/Δk ≈ 11.2 near k = 35,300; tuple-side slack estimate 0.03–0.3%.

## 7. Key constants (verified this session)

M₂ = 1.385933, M₃ = 1.646440, M₄ = 1.845401, M₅ = 2.007080 (EH ⇒ H₁ ≤ 12); M₅₄ > 4.00238 [Polymath]; H₁ = 246 (k=50, proven-minimal tuple); H₂ = 396,504 (k=35,265, Stadlmann); H₃ = 24,797,814 (k=1,649,821); pair upper constants 3.3996 (Wu) → ≈3.30 (Lichtman), parity floor 2; H(k) k=3..62 full list in `p4_payoff_table.txt`; dH₁/dδ ≈ −2400; k=49/48/47 tipping δ ≈ 0.002/0.004/0.006.
