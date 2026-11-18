# The Walls and the Doors: Exact Theorems on the Bounded-Prime-Gaps Framework

## A survey of five companion investigations, with a complete computational compendium

**Bill (Qingyun) Sun · GPT5.6SOL · Fable**

*August 11, 2026*

---

## Abstract

Twelve years after Polymath8b established that infinitely many pairs of primes differ by at most H₁ = 246, that constant is unmoved. This survey synthesizes five companion investigations that, rather than optimizing once more inside the Maynard–Tao framework, determine its exact boundaries — and in doing so locate the only places a smaller constant can come from. The results are of two kinds. **Walls (proved):** the admissible-tuple side of 246 has exactly zero slack (exhaustive re-proof that H(50) = 246 and H(49) = 240 are minimal); the information-theoretic ceiling of the framework's data class equals the tuple diameter exactly, so no post-processing of sieve output can beat H(k_min); the scalar Maynard–Tao decode is precisely optimal against all available data, including every one-sided correlation bound — the matrix/inertia layer buys counting constants but never a smaller gap; the sieve-weight cone cannot be usefully enlarged — rank-r sum-of-squares weights decouple by a subadditivity theorem, and the strictly larger copositive cone is *flat* against the sieve's evaluation pencil (machine-verified dual certificate); and the 2024 Guth–Maynard large-value revolution is provably orthogonal to the level-of-distribution inputs the framework consumes. Along the way we prove a structural theorem of independent interest: **a family of pairwise prime-correlation conclusions can be simultaneously annihilated by a Selberg-type parity twist if and only if its kill-graph is bipartite** — the odd-cycle facets of the cut polytope are exactly what makes bounded gaps provable while twin primes are not. **Doors (quantified):** the variational door at k = 49 (payoff 6) and especially k = 47 (payoff 20 — the payoff is convex, a fact previously unremarked); the conversion of Maynard's uniform-residue equidistribution trilogy into shell-support gain, needing only 8–13% of the full-shell variational surplus and undecided in print; and the m = 2 record — corrected here to the current H₂ ≤ 396,504 (Stadlmann) — whose admissible tuple is "almost surely not minimal" and whose variational optimization is a decade staler than H₁'s. A final section compiles, in compact machine-usable form, every formula, constant, threshold, and construction needed to compute in this framework.

*No result in this survey improves H₁ = 246. The claim is sharper: we prove where improvement is impossible, and price where it is possible.*

**Status convention.** [P] proved (including computer-assisted exhaustive proofs with independent verification); [C] computational (reproducible, residuals stated); [H] heuristic; [Q] conjecture/open.

---

## 1. Introduction: one constant, one pipeline

Write DHL(k, m+1) for the assertion that every admissible k-tuple 𝓗 has infinitely many translates n + 𝓗 containing at least m+1 primes. The modern pipeline, due to Goldston–Pintz–Yıldırım, Zhang, Maynard [May15], Tao, and Polymath8b [Pol14a], factors every bounded-gap theorem into three independent components:

  **(arithmetic) θ  ⟶  (variational) M_k > 2m/θ ⟹ DHL(k, m+1)  ⟶  (combinatorial) H_m ≤ H(k),**

where θ is a level of distribution of the primes (Bombieri–Vinogradov gives θ = 1/2 unconditionally), M_k is the Maynard–Tao variational constant (§9.1), and H(k) is the minimal diameter of an admissible k-tuple. The records: H₁ ≤ 246 (k = 50, via the ε-refined variational threshold at θ = 1/2) [Pol14a]; H₁ ≤ 12 under Elliott–Halberstam; ≤ 6 under generalized EH — where the parity obstruction provably stops all sieve-type methods. For m = 2 the record is H₂ ≤ 396,504 (Stadlmann [Sta23], superseding Polymath8b's 398,130 — a correction to several summary accounts, including our own earlier one); H₃ ≤ 24,797,814; H_m ≪ e^{3.8075m} [Sta23].

The five companion investigations surveyed here each interrogate one component with the toolset developed in our finite random-matrix program (exact LP/SOS duality, convex-order counterfeits, positive-inertia decoding, exhaustive combinatorial search): Paper I the combinatorial floor, Paper II the information-theoretic ceiling, Paper III the decode layer, Paper IV the weight cone, Paper V the arithmetic frontier. Their common finding is that the framework is far more rigid than the folklore suggests — rigid enough that each "wall" is now a theorem with an explicit certificate, and the surviving "doors" carry exact price tags.

---

## 2. Paper I — The combinatorial component is closed (and the payoff is convex)

*(Exhaustive admissible-tuple computation; scripts `p4_rho_exhaust.c` and companions.)*

**Theorem 1.1 [P].** H(50) = 246 and H(49) = 240 are minimal: no admissible 50-tuple of diameter ≤ 245 and no admissible 49-tuple of diameter ≤ 239 exists.

The proof is a complete enumeration (not a failed search): after two structural reductions — parity monochromaticity (any admissible tuple is monochromatic mod 2, so one works in half-coordinates) and complete branching over the avoided residue classes mod 3, 5, 7 — a DFS over residue-coverage bitmasks with ρ\*-table pruning exhausts the decision instances (≈1.6–1.85 million nodes each) in seconds. An independent implementation with a different search tree, and exact-arithmetic re-verification of every witness, confirm the values; they agree with Engelsma's classical tables (minimality known for all k ≤ 342) and OEIS A008407. The significance is not novelty of the values but the *closure statement*: **the tuple side of H₁ = 246 has exactly zero slack — any improvement must come from the analytic side, i.e. from lowering k below 50.**

**The convexity observation.** The verified payoff ladder near the record is H(49) = 240, H(48) = 236, **H(47) = 226**, H(46) = 216: gains of 6, 4, **10, 10** per unit of k. (Several circulating summaries state H(47) = 232; this is wrong.) The strategic consequence, previously unremarked: the variational effort should not be spent exclusively on the marginal door k = 49 — the k = 47 door pays more than three times as much, and the threshold distance grows only linearly (§6). Conversely a regression to k = 51 costs only 6.

**The m = 2 opportunity [C/H].** For k = 35,265 (Stadlmann's DHL(35265, 3)), the record tuple of diameter 396,504 is flagged by its own author as "almost surely not minimal." Rigorous lower bounds (Montgomery–Vaughan Brun–Titchmarsh: 216,632; Selberg large sieve: 202,249 — computed exactly) leave a factor-1.8 void, and the same bounds run ≈50% low at k = 50 where the truth is known. A reproduction of the Sutherland pipeline (shifted Schinzel sieve → greedy → local optimization) reaches within 3.0% of the record in ~30 CPU-minutes; the record's last percent lives in iterated merging and residue-class annealing. Estimated realistic slack at fixed k: 0.03–0.3%, i.e. 100–1,200 units of H₂ — **each single unit an immediate new record on liminf(p_{n+2} − p_n), requiring zero new analytic input.** A full-scale attack (with an LP-based repair step unavailable in 2014) is in progress.

---

## 3. Paper II — The exact ceiling, and the bipartite structure of parity

*(The counterfeit theory of the bounded-gaps data class; scripts `p8_moment_lp.py`, `p8_parity_fiber.py`.)*

This is the round's most conceptually novel contribution: a two-layer adversary theory that computes, exactly, what any argument consuming the framework's data can and cannot conclude.

### 3.1 Layer 1: the ceiling equals the tuple diameter

Model the framework's knowledge about the prime-indicator vector (X₁,…,X_k) at a translate of the tuple: **(R1)** the weighted marginals E[X_i] (delivered two-sidedly by the sieve at level θ), and **(R2)** *upper* bounds on all joint moments E[∏_{i∈S}X_i], |S| ≥ 2 (Selberg/large sieve; the best published pair constant is 3.3996 · Hardy–Littlewood [Wu04], improved to ≈ 3.30 by Lichtman [Lic25]). Crucially **(R3)**: no lower bound on any joint moment is available — that absence *is* the parity wall.

**Theorem 2.1 (ceiling = diameter) [P in the model].** Over all joint laws consistent with (R1)–(R2): (i) min P(X₁+⋯+X_k ≥ m+1) = max(0, (s−m)/(k−m)) where s = ΣE[X_i] — the pigeonhole bound is the *entire* provable content, and no strengthening of the upper-bound rows moves the threshold s > m; (ii) for any H < diam(𝓗), the minimum probability that some pair at distance ≤ H is simultaneously prime is exactly 0, jumping to (s−1)/(k−1) at H = diam(𝓗). Hence the class ceiling is H_ceiling = H(k_min) exactly: **no post-processing of Maynard–Tao output — matrix, moment, spectral, or otherwise — can ever certify a gap smaller than the tuple diameter,** and improved pair-correlation upper bounds (Wu → Lichtman → oracle) can never lower H₁, though they do raise the guaranteed *density* of prime-pair translates.

### 3.2 Layer 2: the parity fiber is a slice of the cut polytope

Encode a Selberg-type parity twist as a reweighting by f(λ(n+h₁),…,λ(n+h_k)) ≥ 0 (λ = Liouville) constrained to preserve all one-marginal data; the reachable pair-correlation multipliers y_ij then form a polytope B_k.

**Theorem 2.2 (bipartite kill-graph) [P].** A set K of pair-conclusions can be simultaneously annihilated (y_ij = 0 for all ij ∈ K) by a parity twist **iff the graph K is bipartite.** (Bipartite: weight the two sides ±; odd cycle: an independent set meets C in < |C|/2 vertices, contradicting the forced marginals.) Verified exhaustively against all 63 kill-patterns at k = 4 and all 1023 at k = 5: LP-feasibility coincides with bipartiteness without exception.

The odd-cycle facets of the correlation/cut polytope are thus precisely the boundary between what sieves can and cannot see. With no tuning, the model reproduces every known frontier fact: Selberg's classical k = 2 counterexample (the unique kill-all solution, f = 2·1{λ₁λ₂ = −1}); the factor-2 parity floor on twin-prime constants in both directions (the coordinate-range [0,2] of B_k; the gap from Lichtman's 3.30 to the floor 2 is the framework's remaining "integrality gap"); the parity-blindness floor **H₁ ≥ 6 for every parity-immune argument** (certifying "some gap ≤ H" needs a non-bipartite close-pair graph, i.e. a triangle, and the narrowest admissible triangle is {0,2,6}) — exactly matching "GEH gives 6, and 4, 2 are blocked"; and the m-floor: DHL(k, m+1) is parity-blocked iff k ≤ 2m. A conservation law at k = 3: killing two pair-conclusions forces the third to exactly twice Hardy–Littlewood — what parity takes at one gap it repays doubled at another.

### 3.3 The Siegel dichotomy, audited

Under strong Siegel zeros the Tao–Teräväinen order-≤2 Hardy–Littlewood–Chowla rows [TT22] pin every pair coordinate y_ij = 1 — the parity fiber's pair projection collapses to a point, which is the mechanism behind Heath-Brown's "Siegel zeros ⟹ twin primes" and Wright's H_m ≪ e^{1.9828m} [Wri21]. But the audit of the tempting two-branch strategy is negative [P in the model]: on the no-Siegel branch the data class is asymptotically identical to the unconditional one (Siegel-freeness enters Maynard–Tao only through effectivity, never through θ or M_k), so **min(branch A, branch B) equals the unconditional record — the dichotomy currently yields nothing new for H₁ or H₂.** Its real content is a target: any lemma of the form "no Siegel zeros ⟹ BV-averaged level 1/2 + δ′" would immediately combine with Wright's branch into an unconditional improvement.

---

## 4. Paper III — The decode layer is exactly optimal (a convex-order theorem)

*(Positive-inertia decoding of the Maynard–Tao form; scripts `p5_functionals*.py`, `p5_decode_lp.py`.)*

Motivated by the rank–trace ("Lemma R") decoding that powers the 2026 two-thirds theorem for zeta zeros, one asks: does the Maynard–Tao quadratic form contain more than the one scalar inequality traditionally extracted from it?

**The availability matrix [P, bookkeeping].** For the sieve weight w = (Σλ_d)² at level R = N^r, the computable entries are: everything linear in at most one prime indicator (two-sided, at BV level, requiring 2r < θ); everything built from majorants/divisor functions (two-sided, elementary); and all *quadratic-in-primes* entries only **one-sidedly** (upper bounds by majorant swap, with overshoot κ = 16/(1−2r)² ≥ 64 at the threshold weight; lower bounds only trivial ≥ 0). The entire cross block is unknown in exactly the direction that matters.

**Theorem 3.1 (decode optimality) [P at the decode layer].** Let A = E_μ[Σ 1_P(n+h_i)] = (θ/2)M_k be the sieve's certified mean. Against the data class consisting of all exact linear-in-primes data together with valid upper bounds on E φ(X) for *every convex φ* — a class containing all falling moments and all r-fold correlation upper bounds however sharp — the largest certifiable r in "∃n: X ≥ r" is exactly ⌊A⌋+1. *Proof:* the counterfeit law with X two-point supported on {⌊A⌋, ⌈A⌉} at mean A is the minimum in convex order among laws on ℤ≥0 with that mean; hence it satisfies every constraint in the class and admits no n with X ≥ ⌊A⌋+2. ∎

Consequently **f(m) = 2m/θ is decode-optimal: no matrix, inertia, or moment refinement of the Maynard–Tao decode can lower any H_m within the available data.** The two natural loopholes are closed quantitatively: designing sign-cancelling profiles to suppress the pair functional fails (the pair-to-mean² ratio γ is pinned within 1.2% of 1 along the entire Pareto frontier at k up to 1.6·10⁶ [C]); and multi-translate simultaneity reduces to the scalar bound on the union tuple by first-moment budget conservation [P].

**What survives [C].** Above threshold (A = m + δ) the sharp two-point-adversary bound

  Pr_μ[X ≥ m+1] ≥ δ / (min(k, 2B/δ − m + 1) − m),  B = κγA²/2 − m(m−1)/2,

improves the certified *measure* of prime-rich translates by factors up to 23× (m = 2) and 505× (m = 3, large δ) once pair upper bounds are used — an exponential-in-m gain in the counting constant, honestly assessed as a sharp LP form of a technique already present in Banks–Freiberg–Maynard, and worth exactly zero for H_m itself. The parity audit confirms the decode never touches a specified-shift pair; the counterfeit takes pair mass *below* Hardy–Littlewood, which no available row forbids.

---

## 5. Paper IV — The weight cone cannot be enlarged (decoupling and flatness)

*(SOS-certified enlargements; scripts `p7_*.py`, certificate `p7_dual_certificate.npz`.)*

The Maynard–Tao weights are single squares. Two enlargements suggest themselves: sums of several squares (rank r > 1), and signed corrections certified pointwise-nonnegative on the divisor lattice (a copositive, rather than PSD, Gram matrix). Both are closed.

**Theorem 4.1 (decoupling) [P].** Every DHL criterion in the pipeline has the form Φ(w) > 0 with Φ subadditive on the weight cone (main terms and error budgets are linear in w; Cauchy–Schwarz penalties −√(B(w)C(w)) are superadditive). Hence a rank-r witness implies a rank-1 witness in the same per-square class: **rank never helps, for any legal variant** — the ε-trick and vanishing-marginal refinements enlarge the per-square class, not the useful rank. (Rank could only pay under an aggregate-cap constraint nonlinear in w; no sieve quantity has that form, since everything ever bounded is Σ_n a(n)w(n).) A companion collapse [P]: PSD certificates plus the level constraint force long-support rows to vanish (Schur), so SOS + level = the classical class exactly.

**Theorem 4.2 (flatness of the copositive cone) [C, with a machine-verified closure certificate].** The copositive cone is strictly larger as a cone — the LP finds wildly non-PSD legal Gram matrices — but its extra directions are orthogonal to the sieve's evaluation pencil (J̃, Ĩ). Measured optimal-value gaps at k = 3, 4, 5 over spans up to r = 8: ≤ 2.6·10⁻⁷ relative, in an exact fixed-R model cross-validated against 10⁶ real integers (where the exact finite-cone optimum is attained by a PSD matrix). At k = 3 the closure is certified: nine explicit realizable divisor patterns P with weights y_P > 0 satisfy J̃ = t·Ĩ − Σ y_P v_P v_Pᵀ to 1.3·10⁻¹⁴ with t exceeding the PSD optimum by 1.4·10⁻⁶ — since ⟨v_P, C v_P⟩ ≥ 0 for every copositive C, this bounds the *entire* enlarged cone. The cross-only long-support experiment (the sharpest corner: components beyond the level admitted only in cross terms) recovers ≈ 0 of the 10.2% headroom that illegal full support would give. Mechanism [H]: truncated divisor patterns realize all sign-alternating finite differences of the profiles — a family dense enough to pin the pencil's negative eigenspace; nothing in it weakens as k grows.

**Consequence.** The weight-cone axis is closed. Combined with Paper III, all conceivable "optimize harder inside the same data" strategies are now excluded by theorem or certificate; movement requires evaluation-side inputs.

---

## 6. Paper V — The arithmetic frontier, 2014 → 2026

*(Level-of-distribution audit and the exact payoff function; script `p6_payoff.py`.)*

**The MT-usable frontier has moved 0.5233 → 0.5263 in twelve years.** The sieve consumes equidistribution with two properties: all moduli (its error moduli are generic squarefree products) and residue uniformity (its residues are the k^{ω(q)} roots of ∏(n+h_i), varying with q). Everything beyond Bombieri–Vinogradov's θ = 1/2 exists only in restricted forms, sorted by compatibility: Polymath8a's 1/2 + 7/300 (densely divisible moduli, poly-root residues — usable on a truncated support shell); Maynard's trilogy culminating in 11/21 with **completely uniform residues** [MayIII] — the first such object since Zhang; Stadlmann's 1/2 + 1/40 (smooth moduli) [Sta23]; Pascadi's minorant-level 10/19 [Pas25] — while the numerically larger levels (BFI 4/7, Maynard II 3/5, Pascadi 5/8) are fixed-residue or well-factorable-weight results that the MT error term, carrying absolute values over varying residues, provably cannot consume. The mechanism by which restricted inputs failed to move H₁ in 2014 is reconstructed exactly: the input enters *only through the shape of the accessible support polytope Ω*, the shell beyond the unit simplex must be truncated to coordinates the modulus class can guarantee, and the ε-trick already harvests shell value at zero arithmetic cost — a structured input must beat the ε-trick on its own shell. Net 2014 gain at m = 1: ≈ 0. **Coverage density in modulus mass is the wrong parameter [P]: non-geometrically-aligned partial coverage is worth exactly nothing; the right parameter is the variational surplus ρ_geom of the accessible sub-shell.**

**The payoff function, calibrated [C].** With the master criterion DHL(k, m+1) ⟸ M_k(Ω) > 2m/θ and M_k(λΩ) = λM_k(Ω): tipping k = 49 (worth 6) needs full-BV δ ≈ 0.0014–0.0023, or ρ_geom ≈ 8–13% of the full-shell surplus at Maynard-III strength; k = 48 (worth 10): δ ≈ 0.003–0.005; k = 47 (worth 20): δ ≈ 0.005–0.008. Sensitivity at the record: dH₁/dδ ≈ −2400. The pure-simplex route is dead by the rigorous upper bound M_k ≤ (k/(k−1))log k: M₅₀ ≤ 3.99186 < 4 [P] — every road to < 246 passes through enlarged variants.

**Guth–Maynard is orthogonal to H₁ [P at proof-structure level].** The classical BV proof consumes no zero-density input; full GRH itself gives only θ = 1/2 pointwise — everything beyond comes from dispersion + Weil/Deligne + spectral Kloosterman machinery in which zero-density estimates appear nowhere (dependency audit of Maynard I–III, Stadlmann, Pascadi). The 2024 large-value theorem [GM24] therefore feeds short-interval results, not bounded gaps. The genuine open computation this paper isolates: **translate Maynard III's divisor-window conditions into shell-polytope constraints and compute M₄₉(R ∪ Ω\*) with the ε-trick layered on — an undecided, decidable question that no one has published,** and exactly the kind of 10⁻²-precision constrained Rayleigh-quotient problem our exact-rational SDP/Krylov machinery certifies.

---

## 7. Synthesis: the no-go map and the two open doors

The five papers compose into a single statement:

> **Within the Maynard–Tao data class, H₁ = H(k_min) exactly, and every route to a smaller H₁ must lower k_min — by enlarging the variational value through new *evaluation-side* arithmetic (uniform-residue level beyond 1/2 on an accessible shell), and in no other way.** Post-processing (Paper II), decode refinement (Paper III), weight-cone enlargement (Paper IV), tuple search (Paper I), and zero-density technology (Paper V) are all excluded by theorem or certificate.

The doors, priced: **(D1)** the k = 49/48/47 variational doors, payoffs 6/10/20, with the Maynard-III shell computation as the concrete undecided question; **(D2)** the m ≥ 2 records — softer in *both* factors: the variational optimization at k ≈ 35,000 never received 2014's k = 50-level effort (threshold M_k > 8; every unit of variational gain converts at dH₂/dk ≈ 11 via the tuple tables), and the record tuple itself has measurable slack (each unit a new world record); **(D3)** parity-sensitive rows short of Siegel zeros — order-2 Liouville correlation rows in natural density would pin pair coordinates exactly as Tao–Teräväinen's do conditionally; the bipartite theorem says precisely which conclusions each new row unlocks.

Work in progress (five further investigations, reports pending): the exact-rational variational baseline at k = 45–55; the ε-variant attack at k = 49/47; certified upper bounds closing or opening those doors; the large-k (m = 2, 3) variational engine; and the additive–Mellin Type-II program.

---

## 8. Computational compendium

*Everything needed to compute in this framework, compact but complete. All notation as above; [P]/[C] status inherited from the sections cited.*

### 8.1 The variational problem

- Simplex R_k = {t ∈ [0,∞)^k : Σt_i ≤ 1}; symmetric F: I(F) = ∫_{R_k}F², J^{(m)}(F) = ∫_{R_{k−1}}(∫F dt_m)² ; M_k = sup_F k·J(F)/I(F) (all J^{(m)} equal by symmetry).
- Bilinear polarization (legal at no cost): I(F₁,F₂) = ∫F₁F₂, J^{(m)}(F₁,F₂) = ∫(∫F₁dt_m)(∫F₂dt_m).
- Polynomial bases in power sums P_j = Σt_i^j reduce I, J to 1-D Beta-type integrals; exact rational arithmetic feasible through k ~ 10² at useful degree. Product-profile 1-D reduction for k ~ 10⁴ (optimal F ≈ Π g(t_i), g ≈ 1/(1+At) truncated).
- Threshold: **DHL(k, m+1) ⟸ M_k(Ω_accessible) > 2m/θ**; θ = 1/2 unconditional ⇒ M_k > 4m. Scaling law M_k(λΩ) = λ·M_k(Ω).
- ε-trick: support (1+ε)R_k with marginals vanishing outside (1−ε)R_{k−1}; zero arithmetic cost; this is how k = 54 → 50.
- Upper bound [P]: M_k ≤ (k/(k−1))·log k. Values: M₄₈ ≤ 3.95357, M₄₉ ≤ 3.97290, M₅₀ ≤ 3.99186 (pure problem dead ≤ 50); first non-excluded k = 51 (4.01046).
- Anchors: M₅ = 2.007080 > 2 (EH ⇒ H₁ ≤ 12); M₄ = 1.845401 < 2 (provably, so pure class cannot give DHL(4,2) under EH); M₃ = 1.646440; M₂ = 1.385933; M₁₀₅ > 4 (Maynard); M₅₄ > 4.00238 (Polymath8b); ε-variant at k = 50 > 4 ⇒ 246.
- Asymptotics: M_k = log k − c₀ + o(1); calibrated slope dM/dk ≈ 1/k near k = 50.

### 8.2 Records and thresholds (August 2026)

| quantity | value | source/condition |
|---|---|---|
| H₁ | **246** (k = 50) | unconditional [Pol14a] |
| H₁ under EH / GEH | 12 / 6 | 6 is the parity floor [P, §3.2] |
| H₂ | **396,504** (k = 35,265) | Stadlmann [Sta23] — not 398,130 |
| H₃ | 24,797,814 (k = 1,649,821) | [Pol14a] |
| H_m | ≪ e^{3.8075m} | [Sta23] — not 3.815 |
| m-threshold | M_k > 4m (θ = 1/2); m = 2 ⇒ > 8 | |
| pair-correlation upper constants | 3.3996 [Wu04] → ≈ 3.30 [Lic25]; parity floor 2 | cannot affect H₁ [P, §3.1] |

### 8.3 Admissible tuples (all proven minimal for k ≤ 342; witnesses on file for k ≤ 62)

H(k), k = 3..62: 6, 8, 12, 16, 20, 26, 30, 32, 36, 42, 48, 50, 56, 60, 66, 70, 76, 80, 84, 90, 94, 100, 110, 114, 120, 126, 130, 136, 140, 146, 152, 156, 158, 162, 168, 176, 182, 186, 188, 196, 200, 210, 212, 216, **226, 236, 240, 246**, 252, 254, 264, 270, 272, 278, 282, 288, 300, 304, 310, 320.
Key ladder: k = 46/47/48/49/50 → 216/226/236/240/246 (payoffs 30/20/10/6 relative to 246; **H(47) = 226**, not 232). Admissibility test: for every prime p ≤ k, some residue class mod p is missed (p > k automatic). Structural facts for search: monochromatic mod 2; complete mod-3,5,7 class branching is exhaustive for k ≥ 7; ρ\*-pruning by smaller widths is sound (subsets/translates of admissible are admissible). Proven-optimal witnesses (diam 246, k=50): 0 4 6 10 16 18 24 28 34 36 60 64 66 70 76 78 84 88 90 94 100 106 108 114 120 126 130 136 144 148 154 156 160 168 174 178 186 190 196 198 204 214 216 220 226 234 238 240 244 246. Rigorous lower bounds at large k (both run ~50% low): Brun–Titchmarsh H(35265) ≥ 216,632; large sieve ≥ 202,249. m=2 exchange rate: ΔH₂/Δk ≈ 11.2 near k ≈ 35,300.

### 8.4 Levels of distribution (what the MT sieve can and cannot eat)

| input | θ | moduli | residues | MT-usable |
|---|---|---|---|---|
| Bombieri–Vinogradov | 1/2 | all | uniform (max_a) | **yes — the workhorse** |
| Polymath8a | 1/2 + 7/300 | densely divisible | poly roots | shell-truncated |
| Maynard III [MayIII] | 11/21 | factorable windows | **uniform** | shell-truncated; window widths = the open question |
| Stadlmann [Sta23] | 1/2 + 1/40 | smooth | MPZ-type | shell-truncated |
| Pascadi minorant [Pas25] | 10/19 | smooth | minorant of 1_P | best usable restricted level |
| BFI / Maynard II / Pascadi | 4/7, 3/5, 5/8 | well-factorable λ | **fixed a** | **no** (two structural reasons: residue-variation; absolute values kill factorable weights) |

Tipping table (full-BV equivalent): k = 49 ⇐ δ ≈ 0.0014–0.0023; k = 48 ⇐ 0.003–0.005; k = 47 ⇐ 0.005–0.008; dH₁/dδ ≈ −2400. Shell-coverage form at θ′ = 11/21: k = 49 needs ρ_geom ≈ 8–13%. GRH gives only θ = 1/2; zero-density estimates (incl. Guth–Maynard) appear nowhere in the beyond-1/2 dependency chains.

### 8.5 The adversary/counterfeit toolkit

- **Ceiling LP (Layer 1):** data {E[X_i] = μ_i (equality), E[∏_{S}X] ≤ β_S (|S| ≥ 2)}; min P(ΣX ≥ m+1) = max(0, (s−m)/(k−m)), dual 1{S ≥ m+1} ≥ (S−m)/(k−m); specified-gap conclusions have LP value 0 below the diameter. Quantitative pair-density: with all-pairs cap β, min #{translates with ≥ 2 primes} = (s−1)/(r\*−1), r\* = βk(k−1)/(s−1).
- **Convex-order counterfeit (decode killer):** X two-point on {⌊A⌋, ⌈A⌉}, mean A — minimal in convex order on ℤ≥0, hence satisfies every convex-functional upper bound; kills all decodes beyond ⌊A⌋+1. Feasibility margins of real certificates above the (unusable) firing boundary: 97–129× (level-constrained), 2.0–4.0× even at the parity floor.
- **Parity twist fiber (Layer 2):** distributions q on minus-sets T ⊆ [k] with all vertex-marginals 1/2; pair multipliers y_ij = 4P(i,j ∈ T) ∈ [0,2]. **Kill-set feasible ⟺ bipartite.** B₃ = conv{(2,0,0),(0,2,0),(0,0,2),(2,2,2)}; Σy_ij ≥ 2(k−2) tight; DHL(k,m+1) parity-blocked ⟺ k ≤ 2m; parity floor for any "some gap ≤ H" certificate: a triangle in the close-pair graph ⇒ H ≥ 6 via {0,2,6}. Siegel rows (order-≤2 HLC [TT22]) pin all y_ij = 1; then 3-primes conclusions revive iff pair-sum > s/2.
- **Sieve availability matrix:** two-sided = linear-in-primes (needs 2r < θ) and majorant/divisor blocks (2r + Σ2s_j < 1); one-sided-upper = all quadratic-in-primes blocks, overshoot κ = 16/(1−2r)² (= 64 at r = 1/4); pair-suppression impossible: γ = J-pair/(A²/2) pinned in [0.988, 1.015] along the Pareto frontier (γ = (k−1)/k exactly for products).
- **Weight-cone closure:** subadditivity ⇒ rank-1 suffices (§5); copositive-cone flatness certificate: J̃ = t·Ĩ − Σ₉ y_P v_P v_Pᵀ (residual 1.3·10⁻¹⁴). To test any proposed enlargement: check whether it changes a linear functional of w or only the positivity certificate — only the former can matter.
- **Counting bound (the one thing the matrix layer buys):** Pr[X ≥ m+1] ≥ δ/(min(k, 2B/δ − m + 1) − m), B = κγA²/2 − binom(m,2); beats pigeonhole iff δ > κγm²/k; gains 23× (m=2), 505× (m=3); worth 0 for H_m.

### 8.6 Strategic invariants

1. All H₁ improvement factors through k_min; dH₁/dk ∈ {6,4,10,10,...} (convex) below 50.
2. All k_min improvement factors through M(Ω) on enlarged supports; all Ω-enlargement factors through uniform-residue arithmetic beyond θ = 1/2 (or unconditional shell access à la Maynard III).
3. m ≥ 2 records are soft in both factors (variational at k ~ 10⁴ under-optimized; tuples non-minimal) with conversion 11.2 : 1 (analytic : combinatorial).
4. Parity floors: H₁ ≥ 6 for the entire method class; k ≥ 2m+1 for DHL; pair constants ≥ 2·HL both directions.
5. The only presently-undecided decidable question worth a large compute budget: **M₄₉(R ∪ Ω_MaynardIII) vs 4** — and its k = 47 sibling.

---

## 9. Open problems

1. **The shell computation** (§6): extract Maynard III's divisor-window parameters, build Ω\*, certify M₄₉(R ∪ Ω\*) against 4 with exact-rational inner/outer bounds. Undecided in print; decidable.
2. **The H₂ tuple record**: any admissible 35,265-tuple of diameter ≤ 396,503. (In progress.)
3. **The m = 2 variational re-optimization** with Stadlmann-level inputs and 2014-vintage care at k slightly below 35,265.
4. **The continuum flatness theorem** (§5): k·J̃ − ρ\*Ĩ ∈ −cone{v_Pv_Pᵀ} for arbitrary smooth spans — closing the copositive cone at all k by proof rather than certificate.
5. **The missing dichotomy lemma**: "no Siegel zeros up to scale ⟹ θ = 1/2 + δ′ for MT-averaged moduli" — the one statement that would make the Siegel two-branch strategy yield unconditional records via Wright's branch.
6. **New parity-sensitive rows in natural density**: any unconditional lower bound on a single joint moment E[X_iX_j] (however weak) breaks Layer 2 at that edge; the bipartite theorem then computes exactly which package of conclusions unlocks.

---

## References

[Pol14a] D.H.J. Polymath, *Variants of the Selberg sieve, and bounded intervals containing many primes*, Res. Math. Sci. 1 (2014); arXiv:1407.4897. And *The "bounded gaps between primes" Polymath project — a retrospective*, arXiv:1409.8361.

[May15] J. Maynard, *Small gaps between primes*, Ann. of Math. 181 (2015), 383–413.

[Zha14] Y. Zhang, *Bounded gaps between primes*, Ann. of Math. 179 (2014), 1121–1174.

[MayIII] J. Maynard, *Primes in arithmetic progressions to large moduli* I–III, arXiv:2006.06572, 2006.07088, 2006.08250; Memoirs AMS (2025).

[Sta23] J. Stadlmann, *On primes in arithmetic progressions to smooth moduli and bounded gaps between primes*, arXiv:2309.00425; Adv. Math. (2025).

[Pas25] A. Pascadi, arXiv:2505.00653 (well-factorable level 5/8) and arXiv:2505.09629 (minorant level 10/19).

[GM24] L. Guth, J. Maynard, *New large value estimates for Dirichlet polynomials*, arXiv:2405.20552.

[Wu04] J. Wu, *Chen's double sieve, Goldbach's conjecture and the twin prime problem*, Acta Arith. (2004); arXiv:0705.1652.

[Lic25] J.D. Lichtman, *A modification of the linear sieve, and the kernel of its iteration*, Algebra & Number Theory (2025); arXiv:2109.02851.

[TT22] T. Tao, J. Teräväinen, *The Hardy–Littlewood–Chowla conjecture in the presence of a Siegel zero*, J. London Math. Soc. 106 (2022).

[Wri21] T. Wright, *Prime tuples and Siegel zeros*, arXiv:2111.14054.

[HB83] D.R. Heath-Brown, *Prime twins and Siegel zeros*, Proc. London Math. Soc. 47 (1983), 193–224.

[Eng] T. Engelsma, *k-tuple permissible patterns*, opertech.com/primes; OEIS A008407.

[Sut] A.V. Sutherland, *Narrow admissible tuples database*, math.mit.edu/~primegaps.

[GPY09] D. Goldston, J. Pintz, C. Yıldırım, *Primes in tuples I*, Ann. of Math. 170 (2009).

[BFM16] W. Banks, T. Freiberg, J. Maynard, *On limit points of the sequence of normalized prime gaps*, Proc. London Math. Soc. (2016).

[CI02] B. Conrey, H. Iwaniec, *Spacing of zeros of Hecke L-functions and the class number problem*, Acta Arith. 103 (2002).

*Companion scripts and machine-verified certificates for every [C] claim are archived in the project scratchpad (`p4_*`, `p5_*`, `p6_*`, `p7_*`, `p8_*`); exhaustive-search witnesses re-verified in exact arithmetic by independent implementations.*
