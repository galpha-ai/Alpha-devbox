# r1 — Outward-rounded certificate for the H₂ record (k = 15,856)

Fable overnight harness, task D1, 2026-09-05. Author: Fable (Claude Code agent). Status tags: [P] proved here, [C] computed here (script + data in this directory), [R] refuted/repaired, [O] open.

Script: `scripts/r1_h2_interval_cert.py` (independent certifier), `scripts/r1_h2_crosscheck.py` (comparison with the historical files), `scripts/r1_h2_reference_p9_exact_cert_scratchpad_copy.py` (provenance copy of the uncommitted historical arb script). Data: `data/h2_k15856_interval_cert.json` (the certificate), `data/h2_k15856_replay_arb.json`, `data/*.log`, `data/h3_k923601_interval_cert_Mk_only.json` (bonus).

## 0. Summary

| id | claim | status |
|---|---|---|
| D1.1 | The H₂ ≤ 173,438 record is the chain: Maynard's criterion M_k > 2m/θ with m = 2, θ ↑ 1/2 (Bombieri–Vinogradov), i.e. **M₁₅,₈₅₆ > 8**, applied to a *closed-simplex* test function (no ε-trick, no vanishing-marginal variant, no cap), plus an admissible 15,856-tuple of diameter 173,438. | [C] (reconstructed from `p9_*` and the JSON; §1) |
| D1.2 | For the product test function F = ∏ g(k tᵢ)·1[Σtᵢ ≤ 1] with g ≥ 0 piecewise linear, M_k ≥ 𝔅(g;β) := c₂⁻¹ Σⱼ max(0, 1−βⱼ)(G(bⱼ)² − G(aⱼ)²) for **any** upper bounds βⱼ ≥ P(S_{k−1} ≥ k − bⱼ); the tail bounds used (chord-majorised Chernoff, one-big-jump, Berry–Esseen with elementary Φ̄ bounds) are valid. Full arguments in §2. | [P] |
| D1.3 | **Rigorous re-certification.** With the stored g (400 nodes, exact dyadic data) and C_BE = 0.56: 𝔅 ∈ [**8.013326752751306578613695503115**, 8.013326752751306578613695503116]; the lower end is an exact rational (434-bit numerator) obtained with every non-polynomial operation enclosed outward (python-flint/arb, 200 bits) and independently with mpmath.iv (200 bits + 2⁻¹⁵⁰ guard band); both agree to all 30 printed digits. Margin over 8: 0.0133267527513065786. | [C] |
| D1.4 | **Berry–Esseen-free certificate.** Dropping Berry–Esseen entirely (plain Chernoff + chord bound + Markov only): M₁₅,₈₅₆ ≥ **8.00677408008999410774 > 8**. Hence the record depends on *no* probabilistic literature constant — only on Maynard's theorem and Bombieri–Vinogradov. Same for H₃: M₉₂₃,₆₀₁ ≥ 12.00263034990571191492 > 12 (M_k part only, §3.6). | [C] |
| D1.5 | The historical number 8.013326752751306 (`p9_exact_cert_k15856.json`) is reproduced exactly: float(lower endpoint) coincides bit-for-bit, per-node β agree to 6.9·10⁻¹⁸ at all 399 nodes, identical strategy split (377 Chernoff, 22 BE). The committed mpmath+SAFE script's numbers (8.01332675275 / 8.01593628081 / 8.01916114663) are also reproduced. | [C] |
| D1.6 | The tuple `p9_tuple_k15856.npy` (sha256 9a0ba71e…5c0b) has 15,856 distinct sorted entries in [−86,719, 86,719], diameter **173,438**, and is admissible: for each of the 1,847 primes p ≤ 15,856 (count confirmed by `sympy.primepi`) the entries miss at least one class mod p (two independent implementations). | [C] |
| D1.7 | Astra audit item "the committed code alone does not demonstrate outward interval arithmetic" is **correct**: `p9_certify_hp.py` is 50-digit floating point with a multiplicative slack 1+10⁻³⁰ ("SAFE"), not outward rounding. The JSON was produced by an arb script that lived only in the scratchpad (now copied here with its sha256). Repaired by D1.3/D1.4, which do not rely on that script. | [R] |
| D1.8 | What is *not* established tonight: the precise statement of Maynard's theorem / Polymath 8b Thm 3.5 was not re-read at the source (recalled); Berry–Esseen constants are recalled (irrelevant for D1.4); the FLINT/arb library and CPU are trusted; the k = 923,601 tuple was not re-verified tonight. | [O] |

**Conditional theorem (as certified).** Assume (H1) Maynard's theorem in the form "if the primes have level of distribution θ and M_k > 2m/θ then DHL(k, m+1)" (Maynard, *Ann. of Math.* 181 (2015), Prop. 4.1; also Polymath 8b, Thm 3.5(i) — recalled; not verified online) and (H2) Bombieri–Vinogradov (every θ < 1/2 is a level of distribution — recalled; not verified online). Then, by D1.2 + D1.4 + D1.6, **liminf (p_{n+2} − p_n) ≤ 173,438**. No third hypothesis is needed. (With the additional recalled Berry–Esseen hypothesis (H3) the certified value improves from 8.0068 to 8.0133; the conclusion is the same.)

## 1. What the record certifies — reconstruction [C]

Sources read: `p9_mk_engine.py` (engine + optimizer), `p9_certify_hp.py` (committed mpmath certifier), scratchpad `p9_exact_cert.py` (uncommitted arb certifier that wrote the JSON; sha256 496c3d80…4b76), `p9_exact_cert_k15856.json`, `p9_g_k15856.npz` (sha256 51088913…3e2), `p9_tuple_k15856.npy` (sha256 9a0ba71e…5c0b), `p9_tuples.py`, `p9_scan.py`, `H2_H3_record_announcement.md`, `handoff/HANDOFF_GPT6_ASTRA.md` §5.

1. **Criterion.** Pure Maynard–Tao: M_k := sup_F Σᵢ Jᵢ(F)/I(F) over square-integrable F supported on the closed simplex R_k = {tᵢ ≥ 0, Σtᵢ ≤ 1}, I(F) = ∫F², Jᵢ(F) = ∫(∫F dtᵢ)² dt_{−i}. DHL(k, m+1) ⇐ M_k > 2m/θ. With Bombieri–Vinogradov every θ < 1/2 is admissible, so M_k > 4m suffices (strict; any θ ∈ (2m/M_k, 1/2) works). For m = 2: **M_k > 8**. The `p9_scan.py` mode `pure2` bisected the smallest k with certified bound > 8 + 10⁻⁶ and found k = 15,856. No ε-enlargement, no vanishing-marginal condition, no coordinate cap (the `cap`/Deligne modes of `p9_scan.py` were used only for the *unclaimed* 145,226 figure).
2. **Test function.** F(t) = ∏ᵢ₌₁ᵏ g(k tᵢ) · 1[Σtᵢ ≤ 1], with g the piecewise-linear interpolant on the 400 nodes 0 = u₀ < … < u₃₉₉ = T = 2430.63 of the optimised profile (family g = e^{−(t/T₁)^κ}/(1+At); only node values are stored, as exact float64, i.e. exact dyadic rationals; g(0) = 1, g(T) = 9.84·10⁻⁷, g ≥ 0 at all nodes). In t-units g(k·) is supported on [0, T/k] = [0, 0.1533].
3. **Lower-bound method ("layer cake").** The 1-D reduction of §2: M_k ≥ 𝔅(g;β) with βⱼ = min(Berry–Esseen bound, min over 9 truncation levels B and 69 Chernoff parameters λ of the chord-majorised Chernoff/one-big-jump bound). Everything is a polynomial integral of the piecewise-linear data except exp, log, sqrt, π (and erfc in an informational variant). No Gamma/Beta functions appear.
4. **Certified number.** `p9_exact_cert_k15856.json`: `certificate_lower_bound = 8.013326752751306`, `PASS = true`, `C_BE = 0.56`, `arb_precision_bits = 200`, "elementary only" Φ̄ bounds. The per-node chain lists u, β_ub, strategy, contribution.
5. **The "SAFE factor".** `p9_certify_hp.py` runs mpmath at `mp.dps = 50` (round-to-nearest floating point) and multiplies by `SAFE = 1 + 10⁻³⁰` at eight places (var_hi/var_lo, Φ̄, the BE term, the MGF total, q_B, β, the final denominator, and the threshold). This is a heuristic guard (mpmath's per-operation error is ~10⁻⁵⁰, the slack 10⁻³⁰), **not** outward rounding; it is not a proof by itself. The uncommitted arb script is genuinely outward-rounded (ball arithmetic with adverse endpoints taken at each inequality), but the repository did not contain it — which is exactly the Astra finding.
6. **Tuple.** `p9_tuples.py`: greedy residue-class sieve with a window refinement; the stored tuple is symmetric, {−86,719, …, 86,719}, diameter 173,438.

## 2. The bound as a mathematical statement [P]

Throughout k ≥ 2, K := k − 1, 0 = u₀ < u₁ < … < u_n = T, g: ℝ → [0,∞) piecewise linear on the nodes, g = 0 outside [0,T], g ≢ 0; c₂ := ∫₀ᵀ g²; G(y) := ∫₀^{min(y,T)} g for y ≥ 0 and G(y) := 0 for y ≤ 0; X, X₁, X₂, … i.i.d. with density g²/c₂ on [0,T]; S_j := X₁ + … + X_j. F(t) := ∏ᵢ g(k tᵢ)·1[Σtᵢ ≤ 1] on [0,∞)^k. F is symmetric, bounded by max g = 1, supported on R_k, and piecewise polynomial on finitely many polytopes (node cells × simplex), hence square-integrable and piecewise differentiable with bounded partial derivatives — the regularity Maynard's Prop. 4.1 asks for (Maynard's own numerical test functions are polynomials times 1_{R_k}, with the same jump on ∂R_k). Polymath 8b's version takes the sup over all square-integrable F, and since |∫(F−F′)dtᵢ|² ≤ ∫(F−F′)² dtᵢ on the unit interval, I and Jᵢ are L²-continuous, so nothing is lost either way.

**Lemma 1 (exact reduction).** I(F) = k^{−k} c₂^k P(S_k ≤ k) and J^{(k)}(F) := ∫(∫F dt_k)² dt₁…dt_{k−1} = k^{−(k+1)} c₂^{k−1} E[G((k − S_K)₊)²].

*Proof.* Substitute xᵢ = k tᵢ, dt = k^{−k}dx. Then F² = ∏g(xᵢ)²·1[Σxᵢ ≤ k], whose integral is c₂^k P(S_k ≤ k). For J: fix x₁…x_{k−1}, σ := Σ_{i<k} xᵢ. Then ∫₀^∞ F dt_k = k⁻¹ ∏_{i<k} g(xᵢ) ∫₀^{(k−σ)₊} g = k⁻¹ ∏_{i<k} g(xᵢ) G((k−σ)₊) (G(y) = G(T) for y ≥ T because g vanishes beyond T). Squaring and integrating dt₁…dt_{k−1} = k^{−(k−1)}dx gives k^{−(k−1)}k^{−2}c₂^{k−1}E[G((k−S_{k−1})₊)²]. ∎

**Corollary.** Since F is symmetric, Σᵢ Jᵢ(F) = k J^{(k)}(F), so
M_k ≥ k J^{(k)}(F)/I(F) = E[G((k−S_K)₊)²] / (c₂ P(S_k ≤ k)) ≥ E[G((k−S_K)₊)²]/c₂. (The last step drops P(S_k ≤ k) ≤ 1; this is the only place where the simplex truncation of the *denominator* is handled, and it is handled by discarding it — a loss, not an error.)

**Lemma 2 (layer cake).** With Y := (k − S_K)₊: E[G(Y)²] = ∫₀ᵀ 2G(u)g(u)·P(S_K < k − u) du.

*Proof.* H := G² is C¹ on [0,∞) with H(0) = 0, H′ = 2Gg on [0,T], H′ = 0 on (T,∞). H(Y) = ∫₀^∞ H′(u)1[u < Y]du; take expectations and use Tonelli (nonnegative integrand): E H(Y) = ∫₀ᵀ 2Gg·P(Y > u)du, and for u ≥ 0, {Y > u} = {S_K < k − u}. ∎

**Lemma 3 (monotone piece bound).** Let w(u) := P(S_K < k − u), nonincreasing in u, and let βⱼ ≥ P(S_K ≥ k − bⱼ) for the piece [aⱼ, bⱼ]. Then
E[G(Y)²] ≥ Σⱼ max(0, 1 − βⱼ)·(G(bⱼ)² − G(aⱼ)²),  hence  **M_k ≥ 𝔅(g;β) := c₂⁻¹ Σⱼ max(0, 1−βⱼ)(G(bⱼ)² − G(aⱼ)²)**.

*Proof.* On [aⱼ,bⱼ], w ≥ w(bⱼ) and 2Gg ≥ 0, so ∫_{aⱼ}^{bⱼ} 2Gg w ≥ w(bⱼ)∫_{aⱼ}^{bⱼ}(G²)′ = w(bⱼ)(G(bⱼ)² − G(aⱼ)²); and w(bⱼ) = 1 − P(S_K ≥ k − bⱼ) ≥ max(0, 1 − βⱼ). Sum over the pieces (they partition [0,T]) and use Lemma 2 and the Corollary. ∎

The bound is therefore valid for *any* family of upper tail bounds βⱼ; grids in λ or B only select which valid bound is used. (S_K has a density, so ≥ vs > in the tail is immaterial, but every bound below is stated with ≥.)

**Lemma 4 (chord-majorised MGF).** For λ > 0 and B ∈ (0,T], let Y := X·1[X ≤ B], q_B := P(X > B) = c₂⁻¹∫_B^T g². For a piece [a,h] ⊂ [0,B] put P₀ := ∫ₐʰ g², P₁ := ∫ₐʰ ((t−a)/(h−a)) g². Then ∫ₐʰ e^{λt}g(t)²dt ≤ e^{λa}(P₀ − P₁) + e^{λh}P₁, and consequently
E e^{λY} ≤ M̄_B(λ) := c₂⁻¹ [ Σ_{pieces [a,h] ⊂ [0,B]} (e^{λa}(P₀−P₁) + e^{λh}P₁) + ∫_B^T g² ].

*Proof.* t ↦ e^{λt} is convex, so on [a,h] it lies below its chord ((h−t)e^{λa} + (t−a)e^{λh})/(h−a); multiply by g² ≥ 0 and integrate. The pieces are the node cells clipped at B (the cell containing B is split at B exactly). The part X > B contributes e^{λ·0}·q_B. ∎

**Lemma 5 (Chernoff / one big jump).** For every λ > 0 and s ∈ ℝ: (a) P(S_K ≥ s) ≤ e^{−λs} M̄_T(λ)^K. (b) For B < T: P(S_K ≥ s) ≤ C(K,2) q_B² + e^{−λ(s−T)} M̄_B(λ)^K.

*Proof.* (a) Markov's inequality on e^{λS_K} and independence. (b) N := #{i ≤ K : Xᵢ > B}; P(N ≥ 2) ≤ Σ_{i<j}P(Xᵢ>B)P(Xⱼ>B) = C(K,2)q_B². On {N ≤ 1}, S_K = Σ Yᵢ + Σ_{Xᵢ>B}Xᵢ ≤ S_Y + T because X ≤ T a.s. Hence {S_K ≥ s} ⊂ {N ≥ 2} ∪ {S_Y ≥ s − T}, and Markov on S_Y with Lemma 4. ∎ (In the actual certificate (b) is never the minimiser at any node; see §3.3.)

**Lemma 6 (Berry–Esseen route; needed only for the 8.0133 variant).** Hypothesis (H3_C): for i.i.d. summands with μ = EX, σ² = Var X, ρ₃ = E|X−μ|³ < ∞, sup_x |P((S_K − Kμ)/(σ√K) ≤ x) − Φ(x)| ≤ C ρ₃/(σ³√K). Then for z := (s − Kμ)/(σ√K) > 0,
P(S_K ≥ s) ≤ Φ̄(z) + Cρ₃/(σ³√K),  Φ̄(z) ≤ min( e^{−z²/2}/(z√(2π)), e^{−z²/2}/2 ).

*Proof.* P(S_K ≥ s) = 1 − P(Z < z) and P(Z < z) = lim_{x↑z}P(Z ≤ x) ≥ Φ(z) − Δ. Elementary bounds: Φ̄(z) = ∫_z^∞φ ≤ ∫_z^∞ (x/z)φ(x)dx = φ(z)/z; and h(z) := ½e^{−z²/2} − Φ̄(z) satisfies h(0) = 0, h′(z) = e^{−z²/2}(1/√(2π) − z/2), so h increases on [0, 2/√(2π)] and then decreases monotonically to h(∞) = 0, hence h ≥ 0 on [0,∞). ∎ Constants (recalled; not verified online): C = 0.4748 (Shevtsova 2011, i.i.d.), 0.5600 (Shevtsova 2010, general independent), 0.7056 (Shevtsova 2007), 0.7915 (Shiganov 1986), 0.7975 (van Beek 1972). The certificate passes with every one of them (§3.4), and without Lemma 6 (D1.4).

**Transcendental content of 𝔅.** c₂, G(uⱼ), μ, σ², ρ₃ (split exactly at μ), P₀, P₁, q_B, C(K,2)q_B² are rational functions of the dyadic node data — exact rationals. The only non-polynomial evaluations: e^{λuⱼ} and e^{λB} (chord weights), log M̄_B(λ) (to form the exponent −λ(s−gap) + K log M̄ exactly and compare candidates as rationals), one final exp per (node, B), √(Kσ²), σ³, √K, √(2π), e^{−z²/2}. Choosing λ and B as exact dyadic/rational numbers (λ = float64(10^{e/8}/T), B = T·f with f ∈ {0.005, …, 0.75, 1}) removes every dependency problem: the interval only ever encloses a single exact real.

## 3. The rigorous re-certification [C]

### 3.1 Arithmetic design of `scripts/r1_h2_interval_cert.py`
1. **Exact layer** (`fractions.Fraction`): all quantities of §2 that are polynomial in the data, including ρ₃ with the piece containing μ split at the exact rational μ (no ambiguity, unlike the ball comparison in the historical arb script, which I checked is conservative in the ambiguous case anyway).
2. **Interval layer**: only exp, log, sqrt, π (erfc in one informational variant). Two backends: python-flint 0.9.0 / arb ball arithmetic at 200 bits (primary; every ball rigorously contains the exact value, endpoints read back as exact dyadics via `man_exp()`); mpmath 1.3.0 `iv` at 200 bits with explicit directed-rounding conversion of every rational (`libmp.from_rational` with floor/ceiling, self-checked) and a relative guard band 2⁻¹⁵⁰ added around every transcendental result (mpmath's directed rounding of exp/log is best-effort, not proven). Start-up self-tests: ball-comparison semantics, big-integer exactness, rational enclosure, e bracketed between two 50-digit decimals.
3. **Exact assembly**: βⱼ := min over candidates of the *upper* endpoints; wⱼ := max(0, 1−βⱼ) exactly; 𝔅_lo := c₂⁻¹Σ wⱼ ΔG²ⱼ as an exact rational, printed rounded **down**; 𝔅_hi from the lower endpoints, rounded up. The certificate is thus a single exact rational number, and the chain of inequalities M_k ≥ 𝔅(g;β_formula) ≥ 𝔅_lo is what D1.2 proves.

### 3.2 Results (k = 15,856, K = 15,855, 399 pieces, T = 2430.63)

| quantity | value (exact rational, printed rounded down unless stated) |
|---|---|
| c₂ | 2972033794830606459853975067340397426336214468287779369 / 24519928653854221733733552434404946937899825954937634816 = 0.12120890875281728… |
| μ | 0.811131889934305585879383282704 |
| σ² | 48.092351380302280213515897691667 |
| ρ₃ | 16801.254240967144149801045938755156 |
| G(T)²/c₂ (un-truncated ceiling of this g) | 8.286702668099250133699207159759 |
| **𝔅, C_BE = 0.56, elementary Φ̄ (arb)** | **[8.013326752751306578613695503115, 8.013326752751306578613695503116]** |
| same, mpmath.iv backend | identical to all 30 digits |
| **margin 𝔅_lo − 8** | **0.013326752751306578613695503115** |
| 𝔅 with Berry–Esseen removed (Chernoff+chord only) | [8.00677408008999410774, 8.00677408008999410775] |
| 𝔅 with Φ̄ = erfc(z/√2)/2 via arb's rigorous erfc | 8.01593628080580075677 |
| threshold ratio: the record needs any θ > 2m/𝔅_lo | θ > 4/8.00677 = 0.49958 (BE-free) or θ > 0.49917 (BE) — both < 1/2 |

Strategy split at the 399 nodes: 377 plain Chernoff (B = T; λ = 10^{6/8}/T at 334 nodes, 10^{5/8}/T at 43), 22 Berry–Esseen (the largest u); no node has zero weight; the one-big-jump bound never wins. Run time 7.4 s (arb 1.6 s, mpmath 4.0 s, tuple 1.2 s) on one core.

### 3.3 Reproduction of the historical numbers
- `p9_exact_cert_k15856.json`: 8.013326752751306 = float(𝔅_lo) bit-for-bit (`r1_h2_crosscheck.py`); per-node β_ub: max |new − old| = 6.9·10⁻¹⁸ over all 399 nodes; same BE/Chernoff class at 399/399 nodes.
- Replay of the uncommitted arb script (provenance copy): 8.0133267528, PASS (`data/h2_k15856_replay_arb.log`, 1.9 s).
- Committed `p9_certify_hp.py` (mpmath dps 50 + SAFE), three regimes: 8.01593628081 (C = 0.56, erfc), 8.01916114663 (C = 0.4748, erfc), 8.01332675275 (C = 0.56, elementary) (`data/h2_k15856_replay_mpmath_hp.log`, 30.5 s). The first and third coincide with my rigorous erfc and elementary variants to 11 digits.

### 3.4 Sensitivity to the Berry–Esseen constant (all rigorous, arb = mpmath to 20 digits)

| C_BE | 𝔅_lo | PASS |
|---|---|---|
| 0.4748 | 8.01642038133547810353 | yes |
| 0.56 | 8.01332675275130657861 | yes |
| 0.7056 | 8.00986119079813881516 | yes |
| 0.7915 | 8.00857812100371282259 | yes |
| 0.7975 | 8.00850042391522292780 | yes |
| none (Chernoff only) | 8.00677408008999410774 | yes |

### 3.5 Cost scaling
The certificate costs O(n_nodes·n_λ) interval exponentials + O(n_nodes·n_B·n_λ) exact rational operations, **independent of k** (k enters only as the integers K, C(K,2) and through the exact rationals). The full k = 15,856 evaluation is therefore not heavy — 7 s — and the "smallest feasible k" fallback in the task statement was not needed. The exact-rational layer's integers reach ~1800 bits (ρ₃ through μ³); nothing else grows.

### 3.6 Bonus: the H₃ profile (M_k part only)
Same script on `p9_g_k923601.npz` with threshold 12: 𝔅 ∈ [12.006666706750045697159697557467, …468] (matches the announced 12.006666706750), BE-free 12.00263034990571191492 > 12, both backends agree (`data/h3_k923601_interval_cert_Mk_only.json`, 5.9 s). The k = 923,601 tuple was **not** re-verified tonight (§8).

## 4. Tuple admissibility and diameter [C]

`p9_tuple_k15856.npy` (int64, sha256 9a0ba71e981b75606fcd02b5ecc17b210416e6ad61ffe0e0267b7e86d9a75c0b): 15,856 strictly increasing integers, min −86,719, max 86,719, diameter 173,438. For every prime p ≤ 15,856 — 1,847 primes, largest 15,823, count and largest confirmed independently by `sympy.primepi(15856)` and `sympy.prevprime(15857)` — the residues mod p occupy fewer than p classes: implementation 1 (pure-Python sets) and implementation 2 (numpy bincount on the shifted tuple) both report zero violations. For p > k a k-element set cannot cover all p classes, so admissibility holds for all primes. Hence H(15,856) ≤ 173,438, and DHL(15,856, 3) gives three primes among n + hᵢ for infinitely many n, i.e. p_{a+2} − p_a ≤ 173,438 infinitely often.

## 5. Exact hypotheses of the certified statement

- (H1) Maynard's theorem: level of distribution θ and M_k > 2m/θ ⇒ DHL(k, m+1), for test functions that are piecewise differentiable (Maynard) or square-integrable (Polymath 8b) and supported on the closed simplex. Recalled; not verified online. Our F satisfies both regularity versions (§2).
- (H2) Bombieri–Vinogradov: every θ < 1/2 is a level of distribution in Maynard's sense (Σ_{q ≤ x^θ} max_{(a,q)=1}|π(x;q,a) − π(x)/φ(q)| ≪_A x(log x)^{−A}). Recalled; not verified online.
- (H3_C) [only for the 8.0133 value] Berry–Esseen with C = 0.56 for i.i.d. summands. Recalled; not verified online. Not needed for the BE-free value 8.0068.
- (H4) Correctness of python-flint 0.9.0 / FLINT-arb ball arithmetic (exp, log, sqrt, π, erfc, and the arithmetic operations) at 200 bits, of Python's `fractions`, and of the hardware. The mpmath.iv backend is an independent second implementation of the interval layer, but mpmath's transcendental directed rounding is not formally guaranteed (hence the 2⁻¹⁵⁰ guard band); arb is the backend the certificate rests on.
- Everything in §2 is proved here; the data (g, tuple) are the fixed files whose hashes are recorded in the JSON.

## 6. Where each ingredient stands
- Lemmas 1–6 and the assembled bound: [P], self-contained above.
- The 1-D bound value and its interval: [C], exact rational + arb; second implementation agrees.
- Historical numbers: [C] reproduced.
- Tuple: [C], two implementations.
- Record theorem: conditional on (H1), (H2) only (BE-free route) — the citations are recalled, not fetched (WebFetch not attempted: the coordination file states the relevant sites are egress-blocked).

## 7. Failed attempts and pitfalls (recorded so nobody repeats them)
1. **mpmath.iv silently rounds big integers**: `iv.mpf(2**300 + 12345)` returns the degenerate interval [2³⁰⁰, 2³⁰⁰], which does *not* contain the argument (no outward rounding on integer conversion). A naive mpmath.iv port of the certifier would be unsound. Fixed by converting every rational with `libmp.from_rational(p, q, prec, round_floor/round_ceiling)` and asserting the enclosure. (The committed `p9_certify_hp.py` is not affected: it converts float64 values only, which are exact.)
2. My first self-test asserted lo(e) < 2.718281828459045235360287 < hi(e) with a 25-digit *truncation* of e; a 60-digit-wide enclosure correctly rejected it. Replaced by a two-sided 50-digit bracket. (Lesson: test constants must be brackets, not truncations.)
3. The one-big-jump truncation (Lemma 5b) is dead weight at this k: at none of the 399 nodes is it the minimiser; removing it would not change the certificate (not done, to keep the reproduction exact).
4. Not attempted: a fully exp-free certificate (rational Taylor enclosures of exp). Unnecessary given arb, and the chord bound already needs only ~28k exponentials.
5. Not attempted: reproducing the *optimisation* that produced g (Nelder–Mead in `p9_mk_engine.py`); the certificate is about the stored g and does not depend on how it was found.

## 8. Open items [O]
- (H1)/(H2) statement-level verification against the primary texts (Maynard 2015 Prop. 4.1 + Thm 3.1 pipeline; Polymath 8b Thm 3.5(i) and the definition of M_k over square-integrable F). Everything used here is standard, but tonight's proof of the record is conditional on the recalled statements.
- Independent library trust (H4): arb is the only outward-rounded backend with proven semantics here; a third route (e.g. exact rational Taylor bounds for the ≈28k exponentials, or a Lean/Isabelle check of the 399-term sum) would remove it.
- The k = 923,601 tuple (H₃ record) admissibility was not re-verified tonight (73,001 primes × 923,601 entries ≈ 7·10¹⁰ residue operations; needs a compiled sieve, ~minutes in C).
- Whether the same profile family certifies a smaller k for m = 2 (the H₂ tuple k could drop if the 0.0067–0.0133 margin were spent) — outside D1.

## 9. Commands and output summaries
```
cd research/riemann-rmt/overnight/fable/data
python3 ../scripts/r1_h2_interval_cert.py --backend both          # 7.4 s -> h2_k15856_interval_cert.json, r1_h2_interval_cert_run.log
python3 ../scripts/r1_h2_crosscheck.py                            # -> r1_h2_crosscheck.log
python3 ../scripts/r1_h2_reference_p9_exact_cert_scratchpad_copy.py ../../../p9_g_k15856.npz 8.0 h2_k15856_replay_arb.json   # 1.9 s
python3 ../../../p9_certify_hp.py ../../../p9_g_k15856.npz 8.0    # 30.5 s -> h2_k15856_replay_mpmath_hp.log
python3 ../scripts/r1_h2_interval_cert.py --backend both --skip-tuple --npz ../../../p9_g_k923601.npz --threshold 12 --out h3_k923601_interval_cert_Mk_only.json   # 5.9 s
```
Key output lines: `[python-flint arb (ball arithmetic)] certificate M_15856 >= 8.013326752751306578613695503115 (formula value <= …116)`, `margin over 8: 0.013326752751306578613695503115 PASS=True`, `variant Chernoff_only_no_BE: lo=8.00677408008999410774 PASS=True`, `[tuple] count=15856 sorted/distinct=True diameter=173438 admissible=True (primes tested: 1847, largest 15823)`.

Environment: Python 3.11.15, numpy 2.4.6, mpmath 1.3.0, python-flint 0.9.0, sympy (for the prime-count cross-check only).

## 10. Files
- `overnight/fable/r1_h2_interval_cert.md` — this report.
- `overnight/fable/scripts/r1_h2_interval_cert.py` — independent certifier (exact rational + arb + mpmath.iv, tuple check).
- `overnight/fable/scripts/r1_h2_crosscheck.py` — comparison with the historical JSON and replay.
- `overnight/fable/scripts/r1_h2_reference_p9_exact_cert_scratchpad_copy.py` — provenance copy of the uncommitted arb script (sha256 of the original in its header).
- `overnight/fable/data/h2_k15856_interval_cert.json` — the certificate: exact parameters (hex node data, λ grid, B fractions, constants), exact rational lower bound, per-node β chain (40-digit upper-rounded decimals), tuple check, both backends, all variants.
- `overnight/fable/data/h2_k15856_replay_arb.json`, `h2_k15856_replay_arb.log`, `h2_k15856_replay_mpmath_hp.log`, `r1_h2_interval_cert_run.log`, `r1_h2_crosscheck.log`, `h3_k923601_interval_cert_Mk_only.json`, `h3_k923601_Mk_only_run.log`.
