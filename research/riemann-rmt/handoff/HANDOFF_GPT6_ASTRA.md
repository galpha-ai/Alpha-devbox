# HANDOFF — The Riemann / Random-Matrix / Prime-Gap Programme

## Complete state of the research, for GPT6 Astra to take over

**Authors of the programme:** Bill (Qingyun) Sun · GPT5.6SOL · Fable
**Handoff written:** 5 September 2026, by Fable (Claude), at the end of a ~3-week multi-agent session
**Repository:** `galpha-ai/Alpha-devbox`, branch `claude/riemann-zeta-random-matrix-udxp3f`, directory `research/riemann-rmt/` (PR #11, draft). Standalone companion package: `research/riemann-rmt/riemann-impostors/`.

---

## 0. How to read this document

This is written for a successor system that will attempt a *major* theorem. It is therefore long,
and deliberately so: it records not only what was proved and computed, but what was tried and
failed, what the failures taught, and where every number came from. Nothing here is padded; if a
section seems long it is because the corresponding wall took weeks to map.

**Status tags, used throughout, with strict meanings.**

| tag | meaning |
|---|---|
| **[P]** | proved, with a proof written down in the cited file; elementary steps machine-checked where noted |
| **[X]** | exact: certified in exact rational / ball / cyclotomic arithmetic, no floating point in the chain |
| **[C]** | computed: verified numerically, usually by two independent implementations, not proved |
| **[R]** | reduced: follows from a *cited published theorem* plus an explicitly stated open lemma |
| **[H]** | heuristic / conjecture, with the evidence stated |
| **[✗]** | tried and refuted; the refutation is itself a result |
| **[U]** | unverified claim received from a collaborating system; recorded, not endorsed |

**Trust rules that we learned the hard way.** (1) Every headline number in this programme was
produced twice by independent code before being believed; where the two disagreed, the discrepancy
was tracked to source before any claim. (2) Nothing near a decision boundary is accepted in floating
point. (3) The default assumption for any "improvement" is that it is a misread constraint; five of
the most exciting-looking phenomena in this programme were exactly that. (4) "Machine-checked" and
"formalised" are different things; only the first is true of most of this work.

**What this programme did NOT do, so that the successor does not inherit a false belief.** We did
not prove the Riemann hypothesis, the Alternative Hypothesis or its negation, the pair correlation
conjecture, the density conjecture, the twin prime conjecture, Lagarias–Rodgers μ = 1/2, or any
improvement of H₁ ≤ 246. We did not compile any Lean. We could not read three URLs the human asked
us to incorporate at the very end (Anthropic's post on formalising Fermat's Last Theorem and two
`t.co` links): the session's egress proxy blocked `www.anthropic.com` and `t.co`. **Astra should
read those three sources first**; nothing in this document reflects their content.

**A note on a number the human mentioned.** The handoff request refers to a prime-gap bound of
"186" attributed to Weijie Su and GPT6 Astra (and, once, "286"). We have no record of either. Two
facts worth knowing before touching it: **H(40) = 186 exactly** in the Engelsma table of minimal
admissible-tuple diameters (independently re-proved minimal by us for k ≤ 62), so a bound of 186
would mean DHL(40, 2); and **286 is not the diameter of any minimal admissible tuple** (H(57) = 282,
H(58) = 288), so "286" is presumably a typo for 186 or 246. What DHL(40,2) would require is analysed
in §9.5.

---

## 1. Timeline: what each round asked and what it delivered

The programme ran in rounds. Each round posed one question to a fleet of 3–10 parallel agents with
a shared written context (state of knowledge, known errors, honesty rules) but no shared
conclusions; convergence was treated as evidence and divergence as a bug report.

| round | question | main deliverables |
|---|---|---|
| 1 | Analyse Anthropic's 2026 unconditional theorem "≥ 67.25% of zeta zeros are simple and on the line" (Lean repo `anthropics/zeta-23-lean`, constant δ_MT = 3/2 − (1/√2)cot(1/√2) = 0.672500703679) from random-matrix angles; connect to Tao's ACUE | RMT survey; popular note; identification of the bandwidth-one wall; first finite ACUE fibre computations |
| 2 | Verify five Codex (GPT5.6SOL-ULTRA) PDFs; extract real mathematics | `verify_codex.py` battery; `final_verified_paper.md`; several Codex claims corrected (e.g. transcription errors θ_n = arccos(1 − n⁻²/a_n); free-box requirement for the Wilson trace); our own overclaim retracted ("0.6725 is the exact bandwidth-one LP optimum") |
| 3 | Read Anthropic's method *at the Lean source*, couple it to the finite fibre machinery, ten directions | `round3_synthesis.md`: seven-term deficiency identity + √ε rigidity; N_d ≥ 0.8362503N + p; flat RH-frontier; edge no-go; weight freezing; centre-of-mass mimicker family; M₋ lemma with quantified payoff; ceiling candidate 15/22; kill-degree d* = 3(N−3) |
| 4 | Attack the bounded-gap record H₁ = 246 with ≥ 10 agents; improve *any* record concretely | Five proved walls; the k = 49 door priced; **new records H₂, H₃, H₄** via the layer-cake engine; `prime_gap_survey.md` ("The Walls and the Doors"); Codex handoff note |
| 5 | Zhang Yitang's directive: unify Maynard–Tao + Zhang's signed construction + ACUE certificates, run the signed-sieve phase experiment | **Signed no-gain theorem** (one-line identity); exact critical price β*; conditional price list with (E_θ); Chen-switch obstruction; Bourgain scale diagnosis of the 0.0301 gap |
| 6 (P0) | The de Bruijn–Newman finite depth Λ as a dynamic anti-ACUE observable | Exact ACUE enumeration N ≤ 10; CUE Monte Carlo N ≤ 256; **−Λ^CUE ≍ N^{−8/3} vs −Λ^ACUE ≍ N^{−2}**; β-universality; s* = 1.419640342; the operator unification 𝓛_N = Jacobian at the clock; marked-depth law; **Theorem A (ρ ≥ 1) proved**; Theorem C separation; LR bridge and the π²/8 threshold |
| 7 | Consolidation: papers, machine verification (18/18 sympy + z3), Lean specification, companion repository, this handoff | `impostors_paper.md`, `depth_scaling_theorem.md`, `riemann-impostors/` |

Two things happened operationally that the successor should plan around. Agents were killed twice
mid-run: once by a session usage limit, once by exhaustion of usage credits (six agents at once).
In both cases the scratchpad survived and partial results were harvested from disk; several of the
best results in this document (the exact β*, the FUSION-ACUE negative finding in §3.6) were
recovered that way. **Design every long computation so that its partial output is on disk in a
form that a stranger can resume.**


---

## 2. The zeta side: Anthropic's 2/3 theorem, read at the source, and what we added

### 2.1 The method as it actually is (from the Lean, not from paraphrase)

The theorem: at least δ_MT = 3/2 − (1/√2)·cot(1/√2) = **0.672500703679…** of the nontrivial zeros of
ζ are simple and lie on the critical line, unconditionally. The Lean repository `anthropics/zeta-23-lean`
(key files `Zeta23/ZeroSide/RankTraceMult.lean`, `TightMult.lean`, `Mult.lean`, `PairCeiling/*.lean`,
`XiPrime/`, `Taper/`, `Poisson.lean`, `MV/`, `Tail/`) organises the proof around:

- **Lemma R (rank–trace, k-form).** For Hermitian P, Q and c > 0:
  2c·tr(P+Q) − ‖P+Q‖²_F ≤ Σ_j k_c(m_j) + c²·b, with k_c(p) = c² − ((c−p)₊)². This converts a
  quadratic form built from zero data into a *count* of positive directions. It is tight
  (`lemmaR_tight`).
- **PairCeiling.** An upper constant 0.6818287 + 2.55·10⁻⁶·R under the hypothesis `EnclOK`; this
  is the "bandwidth-one ceiling" of the method's own data.
- **ξ′ quartic windows and TightMult**: the Montgomery–Taylor-type window optimisation, done with
  Fejér–Riesz-style nonnegativity at bandwidth one.

The core structural fact, which every later result respects: the method consumes exactly the
pair-correlation data of the zeros at Fourier bandwidth ≤ 1 (Montgomery's proven range), and its
constant is set by a Rayleigh quotient in that data.

### 2.2 What we proved about the method (Round 3, all in `round3_synthesis.md`)

**[P] Seven-term deficiency identity and √ε rigidity (D4).** Lemma R is an identity up to an
explicit seven-term deficiency (verified to 7·10⁻¹⁴, identically zero on the TightMult class); an
ε-near-equality configuration lies within Frobenius distance √ε of an exact equality configuration
(Löwdin frame). Zeta-side ledger: total deficiency over MT windows ≤ (q*−1)·N(T) = 0.3275·N(T),
giving an unconditional pair-repulsion-type bound (on-line pairs with taper overlap ≥ τ number
≤ 0.1637·N(T)/τ²). Reading: Montgomery–Taylor optimisation *is* minimisation of the RMT-predicted
deficiency, and under GUE the budget is exhausted by the Schur/von Neumann term alone.

**[P] The distinct-zeros upgrade N_d ≥ 0.8362503·N + p (D7).** Combining the c = 2 inequality with
the zero-count identity once (not twice) gives slope +1 in the off-line pair density — strictly
stronger than the repository's own c = 3 decoding (slope ½; pairs mispriced at c² = 9 against the
forced value k₃(2) = 8). This is an unformalised **five-line Lean edit** to `mult_two_pair` and would
yield a strictly stronger published constant for distinct zeros. Nobody has made the edit.

**[P] The RH-frontier is exactly flat.** δ(π) ≡ 0.6725007 for all off-line proportions
π ∈ [0, 0.16375]: **assuming RH buys nothing within this method** (the binding adversary is on-line
double zeros; exact 4p-budget/mass cancellation). At maximal off-line density all zeros are forced
simple; pair-block spectra are forced to (≈2, ≈0).

**[P] The edge no-go (D5).** Every admissible bandwidth-one window has r̂(±1) = 0 (two-line
Fejér–Riesz), so the weakest pointwise edge hypothesis |F(1) − 1| ≤ ε certifies exactly 0.6725 even
at ε = 0. The finite Nyquist conservation law is powered by lattice aliasing that ℝ lacks. The
correct zeta-side edge object is the Cesàro mean F̄(∞,T), with the exact collision identity
C(T) = N*·F̄(∞,T) − N(T).

**[P] Weight freezing.** All balanced moments of degree ≤ N are frozen across the mimicker fibre —
later (Round 6) shown to be frozen along the *entire* heat flow, because the flow is diagonal on
coefficients.

**[C] Φ₃ at the MT window.** The flat-window sine-Gram data sits on the {0,1,2} factorial face
(m₃ − 3m₂ + 2m₁ = 0, an identity at every finite N for ACUE), but at the Montgomery–Taylor window
itself Φ₃ = m₃ − 3m₂ + 2m₁ = **−0.0117753128** (closed trig form; verified symbolically, at 30
digits, and on the lattice to 3·10⁻⁷). The third moment carries information exactly where the proof
lives; the blocker is not arithmetic but that Lemma R's hypothesis class carries **no bound on the
magnitude of the compression's negative eigenvalues**.

**[✗] Window engineering cannot fix it.** The Rudnick–Sarnak–style clump term (log T zeros per unit
ordinate at zero kernel decay) forces the row-sum cap M = A₀·log T for *every* window; edge-vanishing
windows improve only the negligible far field, cost ≥ 0.006 in 2 − q(w), and flip Φ₃ to the
unmonetisable positive side. Adversarially settled.

**The surviving zeta-side target, precisely (D1).** A lemma **‖(c⁻¹Â)₋‖ ≤ M₋ uniform in T** —
depth-uniform control of off-line evaluation vectors (a cosh-weighted Poisson analogue plus an
overlap-angle bound). Payoff at the MT window with the capped cubic decoder: **δ = 0.6796896 if
M₋ = 2, up to 0.6844924 if M₋ ≤ 1**, with tr³ the only new prime-side input. This remains the
sharpest known formulation of "what would improve 0.6725 without new correlation ranges."

**[H] The true bandwidth-one ceiling.** Bracket [0.6725007, 0.6818287+], measured integrality gap
≈ 0.0093, candidate exact value **15/22 = 0.681818…**. Two exact-arithmetic conjectures were left
machine-attackable: the 15/22 identity and the kill-degree law d* = 3(N−3) (verified N = 5, 6, 7).

**[P forms + C] The Nyquist cotangent tower.** The three N⁻² convergence towers seen in different
places are one object — the Bernoulli tower of (cot, csc²) — and exist only at the edge.
Doubles density of any Nyquist equality law → 1/4 − 1/π² = 0.148679.

### 2.3 The 0.702642 vs 0.672500 anomaly, closed (Round 5, agent BRG-SCALE, files `brg_*.py`)

The free finite optimum of the marked-ACUE pencil is δ_free(N) = ½ + csc²(π/2N)/(2N²) →
**½ + 2/π² = 0.70264237**, with exact saddle ζ* = N² + N − csc²(π/2N); the Anthropic-feasible
restriction gives δ_MT = 0.672500704; gap 0.03014166.

**[C] The gap is multiscale in Fourier but single-site in position.** Band ledger (stable from
N = 128 to 1024): DC atom +20.33%, low band (0 < α ≤ ¼) **−12.73%**, mid +20.20%, edge quarter
+72.21%, Nyquist row **exactly 0.00%**; the density λ(α) vanishes linearly at α = 1 — no boundary
layer, so no single sharp frequency inequality closes it. The whole free advantage is certified by
**one lattice inequality S₁ ≥ 0** — nonnegativity of the pair count at displacement x = ±1, i.e. at
half the mean zero spacing — whose bandwidth-one shadow ĉ_k = cos²(πk/2N) is full-band coherent.
Decoupling-type bounds misprice the Rayleigh value by 15–77× (constructive alignment; both
extremisers are Perron vectors of a positive kernel), against a 4.5% target: **ℓ²-decoupling is
structurally the wrong tool here.**

**[C] Calibration that changes what one should chase.** Of the 0.030142, only ≈ **0.0093** is even
in principle recoverable in the continuum (to the ceiling ≈ 0.68183); the remaining ≈ 0.0208 is
pure lattice aliasing. "0.6725 → 0.7026" via any continuum inequality is hopeless; the real
continuum target is "0.6725 → 0.6818" and it needs integrality-aware (point-evaluation /
measure-valued) certificates — the ℝ-analogue of S₁ ≥ 0 at half mean spacing.

### 2.4 The moment-deflation audit (Round 5, `fab_deflation.py`) — relevant to Guth–Maynard

Guth–Maynard bound the top singular value of the Dirichlet-polynomial Gram matrix using tr B and a
centred third moment, noting that estimates for powers ≥ 4 are unavailable. The exact extremal
problem "given (p₁, p_r) and m nonnegative eigenvalues, bound λ₁" — sharp bound
λ₁^r + (p₁ − λ₁)^r/(m−1)^{r−1} ≤ p_r — shows that for a spike-plus-flat-bulk spectrum **the r = 3
bound is already exactly tight and r = 4, 6, 8, 10 gain 0.00%** (m = 10², 10³, 10⁴; spike fractions
0.5 … 0.05); with a secondary cluster the gain is 0.1–1.1%. Whatever room exists in Guth–Maynard is
not in the moment hierarchy alone but in the additive-energy input and the resonator geometry.
A formula received from Codex (e = η + κ, 240y² + (72 − 10e)y − 13e = 0, A(e) = 30/(13 + 10y_e))
is recorded as **[U]**: we never re-derived their argument.


---

## 3. Tao's Alternative Hypothesis and the ACUE impostor programme

### 3.1 Why AH matters and why it resists

Montgomery's pair-correlation conjecture: normalised zero gaps follow the GUE law. The Alternative
Hypothesis (AH): the gaps lie asymptotically in (1/2)ℤ. AH is consistent with every proven zero
statistic, has arithmetic consequences (class numbers; Landau–Siegel), and is precisely what current
technique cannot exclude. Tao's ACUE — the measure on N-subsets C of the 2N-th roots of unity with
μ_ACUE(C) = |Δ(ζ^C)|²/(2N)^N — reproduces CUE pair correlation exactly and is a finite model of AH.
The obstruction to "find the statistic ACUE cannot fake" is that one must rule out a *fibre*, not a
point: the measures matching any finite moment list form a large convex body.

### 3.2 The fibre, measured exactly [X]

Affine dimension (rotation-orbit level) of {measures on the ACUE support matching every balanced
moment E[p_λ p̄_ν] of degree ≤ N}:

| N | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|
| dim | 0 | 0 | 2 | 10 | 80 | 403 | 1804 |

(N = 6 and 8 re-confirmed by the tomography code: ranks 70 and 407 with spectral gaps > 10⁶.)
Structural facts: 2- and 3-point statistics are rigid, 4-point free (N = 5 onward); the fibre at
N = 5 is completely solved — a pentagon over ℚ(√5), the known mimicker being |v|² for a 5-sparse
coherent superposition of translated Fermi seas with the single syndrome a*Sa = 0. The reflection
symmetry of the functional equation kills the entire chiral half of the fibre (39/80 dims at N = 7)
at zero cost and provably cannot do more. At N = 8, of 403 directions, **401 are invisible to every
pattern count of window width ≤ 2**, 397 to ≤ 3, 396 to ≤ 4, 392 to ≤ 5, 383 to ≤ 6.

### 3.3 Explicit families [X]

**Centre-of-mass family** (`d6_allN_family.py`, `mimicker_fibre.py`): with X(C) = Σc mod N,
q_g(C) = μ_ACUE(C)·g(X(C)) matches every balanced moment of degree ≤ N **iff** E[g] = 1 and
**ĝ(±1) = 0**; all other frequencies free. Hence an (N−3)-parameter family of honest probability
laws for every N ≥ 4: null dims 2, 3, 4, 5 at N = 5, 6, 7, 8 (forced-zero frequency j = ±1; free
j = 2 / 2,3 / 2,3 / 2,3,4), worst moment error ≤ 1.5·10⁻¹¹, positivity radius 1.0–2.2. Mechanism:
X mod N is exactly uniform under ACUE and couplings to com-frequencies 2..N−2 vanish by a
transport-cost bound (hop budget 2N vs cost ≥ 2N+2).

**Determinant-character (secant) family.** D_r(C) = ∏_{c∈C} ζ^{rc} = det(U_C)^r. Tilts
q = μ·[1 + c·Re(η D_r(C))] lie in the fibre. Exact quantum-mechanical description (from the
colleague's message, verified consistent with our data): μ_ACUE(C) = |⟨C|(∧^N F)A₀⟩|² is the Born
distribution of a single Slater determinant (F = DFT, A₀ = e₀∧…∧e_{N−1}) — re-proving ACUE is a
projection DPP; ⟨C|Ω_r⟩ = ε_r D_r(C)⟨C|Ω_0⟩; the tilt with c = 2a/(1+a²) is the interference
pattern (|Ω₀⟩ + a|Ω_r⟩)/√(1+a²) — our c = ½ corresponds to a = 2 − √3. In Plücker coordinates ACUE
is a point of Gr(N,2N); the mimicker lies on σ₂(Gr(N,2N)) ∖ Gr: the minimal non-Gaussian deformation
of a fermionic Gaussian state.

**Parity sectors** (from the uploaded "Finite All-Depth Escape" paper; tested by us): for even
N ≥ 6, q_N^± = μ_N(1 ± (−1)^{Σc}) are mutually singular, match balanced trace moments of degree
d < N²/4, agree on every complete binary marginal on ≤ N−1 sites, yet have the same local limit.
That paper also proves pair rigidity for simple half-lattice processes (first spatial escape is
three-body) and constructs, for every s ≥ 3 and large N, honest laws matching bandwidth-one rows
through order s while the three-site decoder P(0,1,2 ∈ C) stays nonzero; the missing piece for a
second infinite LR mimicker is one uniform positivity ratio Γ*_{N,s}.

### 3.4 The autocorrelation–Bruhat structure [P (identities) + X]

Restricting to even shifts, |Ω_s⟩ := |Ω_{2s}⟩, z(C) := D₂(C) with z^N = 1, so the entire secant
family collapses to a polynomial P_a(z) = Σ a_s z^s on ℤ_N:

  q_a(C) = μ(C)·|P_a(z(C))|² = μ(C)·(1 + Σ_{δ≠0} A_δ z(C)^δ),  A_δ = Σ_s a_{s+δ} ā_s.

**The code object is the autocorrelation spectrum, not the support.** The invisibility depth is
d_vis(a) = min{δ(N−δ) : δ ≠ 0, A_δ ≠ 0}, because the sector pairing B_δ(f,g) = E_μ[D_{2δ} f ḡ]
vanishes for deg < δ(N−δ) and opens a rank-one channel at exactly that degree between the
conjugate rectangles (N−δ)^δ → δ^{N−δ}. So q_a agrees with ACUE on all balanced observables of
degree ≤ d iff A_δ = 0 for all δ with δ(N−δ) ≤ d. The critical detector
Φ_{N,s}(U) = det(U)^{2s}·s_{(N−s)^s}(U)·conj s_{s^{N−s}}(U) is the character of
W_{N,s} = V_R ⊗ V_S^∨ ⊗ det^{2s}, has E_ACUE Φ = (−1)^{s(N−s)}, and E_CUE Φ = 0 because
W^{U(N)} = 0. The pure max–min code problem is solved by pigeonhole: L states on the N-cycle give at
best m(N−m), m = ⌊N/L⌋, maximised at L = 2 with ⌊N²/4⌋ — **two Fermi seas are globally optimal;
do not spend compute on five.** The open problem is the *interference* code: A positive-definite on
ℤ_N, A₀ = 1, A_δ = 0 on a low-Bruhat-energy zone, A_{δ*} ≠ 0 as high as possible (a Delsarte LP;
"zero-Bruhat-correlation-zone sequences"; the CAZAC extreme A ≡ 0 gives q = μ, no impostor).

d_N(δ) = δ(N−δ) is simultaneously dim_ℂ Gr(δ,N), the pairing ⟨2ρ, ω_δ⟩ (hence the affine Bruhat
length ℓ(t_{ω_δ})), N·‖ω_δ‖², and (up to convention) the quadratic Casimir (N+1)/N·δ(N−δ). The fourth
identification — with the *dynamics* — is §4.7 and is the structural centre of the programme.

### 3.5 Monodromy separator: real Frobenius families are det-sector dark [C, exact averages]

Agent L3 (`monsep_*.py`; artifact "Monodromy Separator"). Over F_q[T] Dirichlet families
(N = 4: q ∈ {3,…,23}; N = 5: q ≤ 13; N = 6: q ≤ 11; ~40M characters, exact FFT character sums):
every winding ≠ 0 observable satisfies |E_χ| ≤ 1.7·q^{−1/2}, with observed decay slopes −2 to −5
(near the family-noise floor q^{−(N+1)/2}). ACUE is bright on the same detectors: E_μ[p_N²] = N,
E_μ[p_N²|p₁|²] = N−2, E_μ[det⁴|p_{N−1}p_{N−3}|²] = 1; the rank-4 twist mimicker has E[det⁴] = ½
(N=4), ¼ (N=5,6). The weight-(N+1) Gram is exactly Haar − 1 in every entry (Haar closed form
E[p_λ p̄_ν] = z_λ δ − sgn·sgn **[P]**). Families converge to Haar with a +c/q correction — the
*opposite* side from ACUE's −1. dim(V_λ ⊗ V_μ^∨ ⊗ det^r)^{U(N)} = 0 for all detectors **[P]**; det is
not pinned (per-class E[det] = 0). Certificate: |E_family| < bright/2 at every computed q except
det⁴|p₄p₂|² at (N,q) = (5,3). **Sign correction discovered:** Σ_{deg f = m} Λ(f)χ(f) = **−**q^{m/2}
tr(Θ^m). What remains for the colleague's Conjecture G2 (minimal derived-L separator) is to convert
W^{G_geom} = 0 into a uniform O(q^{−1/2}) trace estimate via Katz's big-monodromy theorem (IMRN
2013), and to extend the bright gap to the 7 non-twist fibre directions at N = 6.

### 3.6 FUSION-ACUE: a negative result recovered from a dead agent's logs [✗, exact]

Agent L1 (`fus_*.py`, killed by credit exhaustion; logs harvested). **Task 1 verified**: the ACUE
matrix coefficients M^{(r)}_{λ,μ} equal det of a 0/1 congruence matrix with phase +1 and Z_N = N!
(N = 2,3,4 exhaustive; N = 5 spot-checked, 0 mismatches), all values in {−1, 0, +1}. **Verlinde
S-matrix = Kac–Walton at sl(N) level N verified** (N = 2, 3, 4: 18/550/2100 triple coefficients,
0 mismatches). **But the identification "KW fusion = Σ_t ACUE triple pairings (charge
decomposition)" FAILS at N = 3: 22 mismatches out of 550** (it holds at N = 2). Examples:
KW (1,1)⊗(3,1)→() gives 0, ACUE gives 1; KW (2,1)⊗(2,1)→() gives 1, ACUE gives 2. So the naive
form of the colleague's FUSION-ACUE Conjecture A is false; the correct statement, if any, needs a
different charge bookkeeping. **This was never reported to the human before this document.**


---

## 4. The finite de Bruijn–Newman depth: the P0 programme

### 4.1 Definition and conventions (get these right; two earlier write-ups had sign slips)

For monic P(z) = ∏(z − e^{iθ_j}) = Σ a_j z^j define P_s(z) = Σ a_j e^{s·j(N−j)} z^j for s ≥ 0 and
the **depth** D(P) = inf{s > 0 : disc(P_s) = 0}. D = −Λ. P_s stays self-inversive, so D is the
first collision time. **Lemma 1 [P, machine-checked]:** the zeros obey
θ̇_j = −Σ_{k≠j} cot((θ_j − θ_k)/2) (attracting circular Coulomb gas; derived from
∂_s P = (N D_z − D_z²)P and 2z_j/(z_j − z_k) = 1 − i·cot((θ_j−θ_k)/2), with the (N−1) terms
cancelling exactly). N = 2: D = −log cos(δ/2). Clocks (P = 1 − cz^N) are flow-invariant, D = ∞.

### 4.2 ACUE, exact enumeration N = 3..10 [X] (`dyn1_*`, data `dyn1_results_N*.npz`)

13,132 rotation orbits (184,756 configurations at N = 10), exact Vandermonde masses; 40-digit
spot checks worst 1.3·10⁻⁹. Results:
- **P(clock) = 2^{1−N} exactly [P]** (Cauchy–Binet: Σ_{|C|=N}|Δ|² = det(AA*) = (2N)^N; each clock
  has |Δ|² = N^N).
- **δ_min = π/N for every non-clock configuration [P]** (pigeonhole).
- **−Λ ≍ N^{−2}**, fitted slope −2.0009; N²(−Λ) ∈ [1.31, 1.99].
- First collision always at an initially-adjacent pair: 13,130/13,130.
- Generator identity L p_m = −m(N−m)p_m − m Σ_{a<m} p_a p_{m−a} (verified 4.1·10⁻²⁸).
- Quantiles of N²(−Λ) (min / median / max): N=6: 1.353146 / 1.419374 / 1.952629;
  N=8: 1.330383 / 1.418216 / 1.976122; N=10: 1.314614 / 1.412774 / 1.985458.
- **The median turns around at N = 7** (1.41474, 1.41822, 1.41908, 1.41937, 1.41950, then 1.41822,
  1.41520, 1.41277) — so the single-dislocation constant is NOT the ensemble median limit
  (a colleague's extrapolation from N ≤ 7 was corrected).
- Minimising family {0..N−3} ∪ {N+3, N+4}: ρ = 1.0656 (N=10) … 1.0495 (N=18), slowly decreasing
  toward ≈ 1.03–1.05. Maximising symmetric 3-block: ρ → 1.6094, N²(−Λ) → 1.9861.

### 4.3 CUE, Monte Carlo N ≤ 256 [C] (`dyn2_*`, data `dyn2_data_N*.npz`)

Two independent Λ-solvers (ODE vs coefficient bisection) agree to 10⁻⁶; N = 2 law to 8.7·10⁻¹³.
**−Λ ≍ N^{−8/3}**: fitted −2.691 ± 0.010 (N ≥ 16), −2.678 ± 0.016 (N ≥ 32). Distributional law:
**8N^{8/3}(−Λ) ⟹ G², P(G > x) = exp(−x³/72π)** (72π derived from the sine kernel, not fitted:
measured 229–236 vs 226.2; KS 0.035–0.041; median 29.6–30.5 vs (72π ln 2)^{2/3} = 29.08).
Local law R = 8(−Λ)/δ_min² > 1 with med(R−1) = 0.598·N^{−0.729}. Depth ratio to ACUE falls as
3.64·N^{−0.704}; 10× separation at N* ≈ 165 (predicted ≈ 160).

### 4.4 β-universality [C, three-point + endpoint] (`beta_*`)

Killip–Nenciu CMV sampling validated (β=2 vs stored CUE KS 0.0236; vs Haar spacing KS 0.0048; β=1
vs direct COE = VVᵀ KS 0.0035). Prediction −Λ ≍ N^{−2−2/(β+1)}:

| β | predicted | fitted | local slopes |
|---|---|---|---|
| 1 (COE) | −3 | −3.064 | −3.080, −3.026, −3.100 |
| 2 (CUE) | −8/3 | −2.678 | → −2.627 at 128→256 |
| 4 (CSE) | −12/5 | −2.510 | −2.546, −2.480, −2.515 |
| ∞ (ACUE) | −2 | −2.0009 | exact enumeration |

Localisation (first collision = minimal initial gap) holds in 95–99% of CβE samples and 100% of
ACUE. Convergence *rate* prediction ρ_β − 1 = O(N^{−2/(β+1)}): fitted −1.012 / −0.710 / −0.501
vs −1 / −2/3 / −2/5, local slopes at largest N −0.851 / −0.624 / −0.407.

### 4.5 The single-dislocation constant [C, two independent routes]

Alternating clock minus e^{−iπ/N} plus 1: P_N(z) = (z−1)(z^N+1)/(z−e^{−iπ/N}), gap pattern
1,2,…,2,3. Lattice solver: N²(−Λ) = 1.41473945 (N=3) … **1.41963827** (N=20), monotone. Continuum
limit t = −s/N², z = e^{iu/N}: G_s(u) = 2cos(u/2) − 2π∫₀^{1/2} e^{s(1/4−y²)}cos((π+u)y)dy, first
double zero at **s* = 1.419640342, u* = 1.812942145**, G″(u*) = −0.3767. Agreement 2·10⁻⁶ at
N = 20 (O(N⁻²) approach). **s* = ρ_∞ · π²/8 with ρ_∞ = 1.150717118022** (corrected from an earlier
misprint 1.1507015): a two-body collision time dressed by ≈ 15% many-body shielding.

### 4.6 Theorems A, B, C and the Lagarias–Rodgers bridge [P / R] (`depth_scaling_theorem.md`)

**Theorem A [P].** For an adjacent pair, g′ = −2cot(g/2) − Σ_{k≠a,b}[cot(x_a^k/2) − cot(x_b^k/2)]
with x_j^k = (θ_j − θ_k) mod 2π; adjacency forces x_a^k = x_b^k + g in (0,2π) and cot(·/2) is
strictly decreasing there, so every bracket is negative and enters with a plus sign: **every other
zero slows the collapse**. Hence g′ ≥ −2cot(g/2), and since order is preserved until collision,
**−Λ ≥ −log cos(δ_min/2) ≥ δ_min²/8 (ρ ≥ 1)**. Checked: 11,060/11,060 background terms positive;
ratio minima 1.0842 / 1.0714 / 1.0612 (ACUE N = 6, 8, 10), 1.00019 / 1.00021 (CUE N = 16, 64).
Exact two-body solution: cos(g(s)/2) = e^s cos(g₀/2); and −log cos(x/2) ≥ x²/8 on [0,π).

**Theorem B [P given hypothesis].** With background stiffness S = Σ_k ½csc²(x_b^k/2) (clock value
(N²−1)/6 exactly), if S ≤ AN² then −Λ ≤ (δ_min²/8)(1 + O(AN²δ_min²)). Measured S/N² on CUE:
median 0.109 / 0.120 / 0.117 / 0.120 / 0.120 (N = 8…128), q99 ≤ 0.36, max 0.79. **The
high-probability bound S ≤ AN² is the single open analytic ingredient**; it closes Law 1, Law 3 and
Theorem C(ii) at once. Because N²δ_min² ≍ N^{−2/(β+1)} → 0 for finite β but = π² at β = ∞, the
lattice is a *singular* endpoint where ρ ≠ 1.

**Theorem C.** (i) **[P]** N²(−Λ) ≥ π²/8 = 1.2337005501 for every non-clock ACUE configuration.
(ii) **[R]** P(N²(−Λ^CUE) < π²/8) → 1, from P(δ_min > π/N) ≈ exp(−π²N/72) plus the S-bound.
Measured fraction below the floor: 0.565, 0.823, 0.967, 0.9984, **1.0000, 1.0000** (N = 8…256);
sample maxima 0.911 (N=128), 0.437 (N=256).

**LR bridge [P modulo the reverse comparison].** A hard core of c mean spacings gives
δ_min = 2πc/N, so N²(−Λ) = ρ·π²c²/2. Hence μ_Λ ≥ π²μ²/2 and **μ ≤ √(2μ_Λ)/π**: Lagarias–Rodgers'
μ ≤ 0.606894 is exactly μ_Λ ≤ 1.8177; a depth bound 1.29 would give μ ≤ 0.511281; the AH barrier is
M < π²/8. **Falsifiable threshold: liminf N²(−Λ_ζ,local) < π²/8 ⟹ AH false.**

### 4.7 The operator unification [P + X] (`fab_halflaplacian.py`)

Σ_{δ=0}^{N−1} δ(N−δ) e^{−2πikδ/N} = −N/(2sin²(πk/N)) for k ≠ 0, so
(𝓛_N f)(x) = Σ_{k=1}^{N−1}[f(x) − f(x+k)]/(2sin²(πk/N)) has 𝓛_N e_δ = δ(N−δ)e_δ. **Linearising the
Coulomb flow at the clock, ε̇_j = Σ_{k≠j}(ε_j − ε_k)/(2sin²(π(j−k)/N)) = (𝓛_N ε)_j** —
‖𝓛_N − Jacobian‖ ≤ 2.4·10⁻¹³ for N = 4…24, top eigenvalue N²/4 = ⌊N²/4⌋ = the pigeonhole maximal
invisibility depth. **Mechanism: impostors hide in exactly the fastest-relaxing modes of the clock's
stability operator**, which is why adding moments fails and a hitting time does not. As N → ∞,
N^{−1}𝓛_N → (−Δ)^{1/2}: the invisibility hierarchy's natural semigroup is Poisson, not heat. The
1/sin² kernel is Haldane–Shastry's; whether the hierarchy is a sector of an integrable spectrum is
a lead, not a claim.

### 4.8 The marked depth: exact rank-two law [C, parameter-free]

Λ is blind to eigenvectors (isospectral G₁, G₂: τ equal to 8·10⁻¹⁷). Marked depth
χ(G;u) = ∂_η(−Λ(Cayley(G + ηuu*)))|₀ separates them (median difference 0.081). Falsified guess: χ
does *not* track the resolvent u*(zI−G)⁻¹u (resolvent 1.615 → 6.667 while χ 0.0267 → 0.0028). Law:

  **Dτ[uu*] = (κδ/4)·u*K_ab u + (δ²/8)·κ′(u),  K_ab = c_a v_a v_a* − c_b v_b v_b*, c_j = −2/(1+λ_j²),**

with (a,b) the first colliding pair and κ = 8τ/δ² a *functional*. Correlation 1.00000000, slope
1.00000, residual 5.7·10⁻¹¹ (local term alone: 0.9958 / 1.347 / 8.1·10⁻²) — the earlier "ρ ≈ 1.72"
was κ + (δ/2)(κ′/δ′) varying per mark. It is a **polarisation detector** (P_a − P_b, ≈ c·σ_z):
u = (v_a + v_b)/√2 gives zero response; null cone c_a q_a = c_b q_b; orthogonal and null-cone floors
≈ 3·10⁻³ are background (orthogonal marks fix λ_a, λ_b exactly); the resolvent returns at second
order via λ_j″ = 2q_j Σ_{k≠j} q_k/(λ_j − λ_k). Blind rank-2 tomography from 60 random marks recovers
span{v_a, v_b} to principal angles 2.3·10⁻⁶, 3.0·10⁻⁶ degrees (top-2 energy 0.986).

### 4.9 Classification of impostors [C]

Criterion I (transversality): relative residual of grad τ off row(DM_r): single dislocation N=8:
0.991 / 0.941 / 0.737 (r = 1,2,3); random ACUE N=7: 0.996 / 0.963 / 0.569; generic N=7:
0.998 / 0.926 / 0.195; collapses to 10⁻¹⁶ once rank DM_r = N (question becomes vacuous).
Class I (caught by Λ): collision strata, half-lattice adversaries, centre-of-mass and secant
families (TV 0.12–0.24 at N=8); fibre tomography at N=6: E[N²(−Λ)|non-clock] ∈ **[1.3610, 1.4770]**
vs ACUE 1.4336, clock atom ∈ [0, **0.0975**] vs 0.03125. Class II (needs marked Λ): isospectral
families. Class III: linear invisibility survives the linear flow (heat operator is diagonal), and
Λ escapes only because it is a nonlinear stopping time. **Parity sectors**: separated by Λ at every
finite N *only through the atom* (2^{2−N} vs exactly 0; N=8 bulk quantiles 1.3739/1.3959/1.4182/
1.4554/1.4839 vs 1.3752/1.3959/1.4196/1.4338/1.4788; conditional-mean differences 8.9·10⁻³ →
1.1·10⁻³) — Class II/III in the limit.

### 4.10 Two ideas from the colleague not yet executed

- **Dynamic inertia profile.** Hermite–Sylvester: real-rootedness ⟺ positivity of a Hermite form
  H(p); along the flow, I_p(t) = signature H(p_t); Λ = first loss of full signature. Inertia counts
  *how many* negative directions, depth *how far to the first* — same geometry, two coordinates.
  Ties the Anthropic inertia (Lemma R) programme to the Newman programme; untested.
- **Arithmetic heat flow (Dobner).** ζ_t(s) = Σ exp((t/4)log²n) n^{−s}: the dBN flow is diagonal on
  Dirichlet coefficients, a_n ↦ a_n e^{(t/4)log²n}. Log-Gaussian weights inserted into
  sieve/mollifier/character sums — untested "Newmanized parity" idea (§9.7).


---

## 5. Bounded gaps between primes

### 5.1 Framework and the two controlling constants

Admissible k-tuple H; Maynard weights w(n) = (Σ_d λ_d)²; S₁ = Σw, S₂ = Σw·ν(n). If primes have
level of distribution θ and M_k = sup_F k·J(F)/I(F) (symmetric F on the simplex R_k) exceeds 2m/θ,
then DHL(k, m+1) and H_m ≤ H(k). Bombieri–Vinogradov: θ = 1/2, criterion M_k > 4m. Upper bound
[P]: M_k ≤ (k/(k−1))·log k; ε-variants M_{k,ε} ≤ (1+ε)(k/(k−1))log k. Ladder of minimal diameters
(Engelsma, proven minimal ≤ 342; our independent exhaustive re-proof ≤ 62, `p4_rho_exhaust.c`,
`p4_payoff_table.txt` with witnesses): H(40..50) = 186, 188, 196, 200, 210, 212, 216, 226, 236, 240,
246; H(54) = 270; H(105) = 600. Empirical H(k) ≈ k(log k + 0.77) for k ~ 10⁴ (fits (35410, 398130)).

### 5.2 The records [X + P] — `H2_H3_record_announcement.md`, `p9_*`

| | bound | k | previous |
|---|---|---|---|
| H₂ | **173,438** | 15,856 | 396,504 (Stadlmann; earlier 398,130 Polymath8b) |
| H₃ | **13,859,802** | 923,601 | 24,797,814 (Polymath8b) |
| H₄ | **1,120,662,828** | 56,000,000 | 1,431,556,072 (Polymath8b) |

Chain: Maynard's theorem (closed simplex, no ε, no extra equidistribution) + Bombieri–Vinogradov
(margins 0.013 / 0.0067 / 0.065 leave room for θ < 1/2) + Berry–Esseen C = 0.56 + ball arithmetic.
Certificates M₁₅,₈₅₆ ≥ 8.013326752751, M₉₂₃,₆₀₁ ≥ 12.006666706750, M₅₆·₁₀⁶ ≥ 16.065482942209
(`p9_exact_cert_k*.json`, `p9_certify_hp.py`; three regimes each: two BE constants × two tail
routes; small-k sanity: engine stays below known M₂, M₅, M₅₄, M₁₀₅). Tuples: k = 15,856 diameter
173,438 (`p9_tuple_k15856.npy`, second-implementation admissibility check); k = 923,601 repaired
Hensley–Richards tuple diameter 13,859,802 (symmetric window {±1} ∪ {±q : q prime ∈ [45,007,
6,929,899], 5,692 mid-size primes deleted by a deletion-fixpoint repair that converged in 4
iterations} ∪ {+6,929,903}; sha256 d5fe6890…6f02; classical fallback primes-past-k diameter
14,505,780); k = 5.6·10⁷ primes-past-k, endpoints 56,000,003 → 1,176,662,831, π-anchors matched.

**The engine (`p9_mk_engine.py`).** F = ∏g(t_i)·1[Σt_i ≤ k]; X_i iid density g²/c₂; exactly
I = k^{−k}c₂^k·P(S_k ≤ k), J = k^{−(k+1)}c₂^{k−1}·E[G((k−S_{k−1})₊)²]; **layer-cake identity**
E[G((k−S)₊)²] = ∫2G(u)g(u)·P(S_{k−1} < k−u)du with rigorous lower tails (chord-majorised Chernoff /
one-big-jump / Berry–Esseen; monotonicity-only, so grids cannot invalidate); **shaped tails**
g = e^{−(t/T₁)^κ}/(1+At). Recovers ≈ 1.1 units of log k (exact accounting +0.12, tail shape +0.49,
rest by shape optimisation) = factor ≈ 3 in k. The 2014 crude closed-form bound had a deficit of
2.3–2.9 units; the 2023–25 improvements raised θ only. **Engine-vs-engine reconciliation:** an
independent product-ansatz engine (P3) crossed m = 2 at k ≈ 29,500 vs P9's 15,856; the difference was
fully explained (layer-cake + tail shape) before anything was claimed. **Pitfall fixed:** P9's first
HP run at k = 923,601 gave 9.61 because the λ grid was not scaled with T — fixed by λ ∝ 1/T.

**Not claimed:** H₂ ≤ 145,226 via k = 13,467 (Deligne-strength MPZ[ϖ,δ] at (δ,ϖ) = (0.0205, 0.00552),
threshold 7.8273): depends on a cap-normalisation in the truncated variational criterion that we
reconstructed but never verified verbatim against Polymath8b. Also computed but not claimed: Deligne
crossings k = 13,467 (m=2), 660,985 (m=3).

### 5.3 Five walls for H₁ = 246 [P] — `prime_gap_survey.md`

1. **Ceiling = tuple diameter.** No post-processing of Maynard–Tao output beats H(k_min); pair
   correlation constants (Wu 3.3996 → Lichtman ≈ 3.30, parity floor 2) cannot lower H₁.
2. **Scalar decode exactly optimal.** Convex-order two-point counterfeit kills all matrix / inertia /
   moment decodes; f(m) = 2m/θ is final.
3. **Weight cone closed.** rank-r SOS decouples by subadditivity; copositive cone flat (9-pattern
   dual, residual 1.3·10⁻¹⁴). Matrix-Maynard reformulation (uploaded doc) agrees: the SDP has a
   rank-one optimiser; even at level 1, M₂/2 = 0.692965 < 1 with M₂ = 1/(1 − W(1/e)) = 1.38593 —
   no positive eigenvalue at the twin threshold.
4. **Parity, combinatorial.** Kill-graph bipartite ⟺ killable (cut-polytope odd-cycle facets);
   floors H₁ ≥ 6, k ≥ 2m+1. (The graph fact is Tao's 2014 note; the packaging is ours.)
5. **Level wall.** BFI 4/7, Maynard II 3/5, Pascadi 5/8 are well-factorable / fixed-residue and
   structurally unusable by classical MT; usable-restricted frontier: Maynard III 11/21 (uniform
   residues, shell-truncated), Stadlmann 1/2 + 1/40, Pascadi minorant 10/19. Guth–Maynard zero
   density is orthogonal to H₁; GRH gives only θ = 1/2.

**The doors, priced.** k = 49 → H = 240 (pays 6); k = 47 → 226 (pays 20). Pure M₄₉ ∈ [3.891257590916
exact (d = 20 power-sum basis p ≤ 5, dim 1125, `mt_hp_k49_p5.json`), 3.97290]; M₅₀ ≥ 3.907113699811.
ε-variant M_{49,1/35} (d = 18, n = 1597): float 3.959325169, **certified ≥ 3.930490592**;
M_{49,1/25} (d=14) 3.915989908. Upper bounds close the door only for ε ≤ 0.00682; Polymath left
it "undecided". Tipping: k = 49/48/47 need δ ≈ 0.002/0.004/0.006 in θ, or 8–13% of the Maynard-III
shell surplus (open computation SHELL-M49). Tuple search at k = 35,265: best 397,352 vs record
396,504 (P4 annealing chains; missing: iterated merging, LP repair). **Pure-support kill test for
k = 49 is unnecessary**: (49/48)log 49 = 3.97290 < 4 already kills every basis enrichment (higher
power sums, SDP); only the ε-class is alive.

### 5.4 The signed sieve [P + X] — `signed_sieve_nogo.md`, `sgn1_*`, `sgn2_*`, `fab_theorem.py`

Identity (ν−m) + (m−ν)₊ = (ν−m)₊ ⟹ **S₂ − mS₁ − D(w) = Σw₊(ν−m) − Σw₋(ν−m)₊ ≤ Σw₊(ν−m)**: the
signed class is redundant at face-value debt. Diagnostics on a finite microcosm (n uniform on ℤ_W,
ν = coprimality count, weights in level-L feature span, exact rationals): value = classical plateau
for β > β* with **β* = 23051796480/10991046857 = 2.0973249209**, classical value
1087376209/3212440751 = 0.3384891094603102 (verified dual; signed vertex Φ = 1.2082816957,
D = 0.4147152297, 85% negative mass on 16/96 cells; certified on both sides; unbounded below
β_unb = 2.03265 and at β = 2). Across eight variants β* ∈ [1.44, 6.72], and in five of eight the
window (β_unb, β*) is empty (< 10⁻⁶). ℓ¹-budget ramp: λ(1) = λ_positive, slope 0.32–0.89 — gauge,
not gain. **Positivity's second job: it makes the variational problem bounded** (‖w‖₁ = S₁ = 1).
Escapes: (i) debt below face value (exceptional character — Zhang's programme is the *only* route
changing the variational picture); (ii) w evaluable while w₊ is not (well-factorable λ). Chen-switch
obstruction [P-level]: switching never reduces the number r of exact-primality conditions; Chen's
debt has r = 1; DHL(k, m+1), m ≥ 1 forces r ≥ 2 = edge = bipartite = parity-blocked.

**Conditional price list [X certificates]** (`sgn2_certificates.json`, `sgn2_mk_large.json`):

| θ | 2/θ | k pure (M_k) | k ε (M_{k,ε}) | H₁ pure/ε | m=2: k, H₂ ≤ | m=3: k, H₃ ≤ |
|---|---|---|---|---|---|---|
| 1/2 | 4 | 54 | 50 | 270 / 246 | 15,856 → 173,438 | 923,601 → 13,859,802 |
| 4/7 | 3.5 | 31 (3.502015496) | 29 (3.519881250) | 140 / 130 | 5,647 → 58,058 | 202,528 → 2,856,288 |
| 7/12 | 24/7 | 29 (3.443305315) | 26 (3.433616498) | 130 / 114 | 4,835 → 48,988 | 160,703 → 2,226,804 |
| 3/5 | 10/3 | 26 (3.350647068) | 23 (3.334615948) | 114 / 94 | 3,931 → 38,878 | 120,497 → 1,632,566 |
| 5/8 | 3.2 | 22 (3.207656229) | 20 (3.222665844) | 90 / 80 | 3,022 → 29,180 | 80,165 → 1,051,602 |
| 1 (EH) | 2 | 5 (2.007080) | — | 12 | 221 → 1,498 | 1,978 → 18,144 |

(m ≥ 2 rows use the p9 engine's certified-lower-bound path and primes-past-k diameters.) All rows
are parity-consistent (≥ 12 for m = 1). **Missing estimate (E_θ)** — tuple-residue well-factorable
estimate: for c_q(a) jointly well-factorable with the CRT residue selection a mod p ∈ {h_i − h_j},
Σ_{q≤x^{θ−ε}} Σ_{a∈A_i(q)} c_q(a)E(x;q,a) ≪ x(log x)^{−A}. None of BFI Thm 10 / Maynard II /
Pascadi covers it (all fix one residue per modulus); MPZ[ϖ,δ] is its absolute-value cousin at
level ≤ 0.5286. (E_{7/12}) is structurally cheapest (λ can literally be Iwaniec's λ±).

### 5.5 EH → 8 via one signed cross block [P conditional] (uploaded `EH8_OBJECTIVE_ALIGNED_CROSSBLOCK.md`)

For H = (0,2,6,8,12), with the frozen exact trial Q₅ = 1562651575013110693/778568621714732244 =
2.00708265325605 (M₅ > 2), EH plus one Maynard-weighted scalar
Σ ν_x(n)C₈(n)(Θ_H(n) − log 3x) = o(log x·Σν_x), C₈ = λ(n)λ(n+2) − λ(n)λ(n+12) − λ(n+2)λ(n+12),
gives H₁ ≤ 8 (tolerance −1/500, or −7/2000 under full EH). W₈ = (1−ac)(1−bc) is the *unique*
parity-neutral blocker (Theorem 4.1); connected bipartite bad graph on r vertices imports even
Walsh orders through 2⌊r/2⌋ (Theorem 4.2). Ladder: gap 10 needs one 2-point Liouville correlation;
8 needs the degree-2 block; 6 needs one quartic; 4 is odd-cycle impossible (parity wall).
RMT corollary: GRH + Dirichlet-WPC_β with β > 2 − Q₅/2 = 0.996458673… + OMC₈ ⟹ H₁ ≤ 8. Novelty is
narrow (objective-aligned one-scalar compression); Ford–Maynard's primal–dual theory and
Murty–Vatwani are the benchmarks; OMC₈ is not known to be easier than GEH.

### 5.6 The Lagarias–Rodgers μ programme (uploaded LR docs, verified in part)

μ = sup hard core of bandwidth-one sine mimickers: 1/2 ≤ μ ≤ 0.606894 (LR); conjecture μ = 1/2.
Our contributions there: exact signed Fermi-path formula for DPP targets; hard-core necklace
enumeration; **Theorem 4.1** (unbounded exact feasible branch ⟹ LR process, one-way);
**Theorem 11.1** exact all-cardinality 20-cycle separator over ℚ(2cos(π/10)) (positive on all 109
orbits, Fermi target −1/500) and its exact non-transfer to the continuous circle
(L(X_△) = −954123/256000000; seam obstructions {0,19}, {0,18}); the smooth nine-coordinate ansatz
collapses to zero margin jointly at N = 4,5,6,7 (a lattice-trained vector already fails at N = 8:
min −1.08·10⁻³ at {0,3,…,36} ⊂ ℤ/40). **Palm row-sum square (Theorem 13.1 / Prop 5.1):** for
band-limited f (supp f̂ ⊂ [−½,½]), Var⁰_sine(S_f) ≤ (M_h − A_f)(A_f − m_h) is necessary for an
h-hard-core mimicker; the multiwindow quadratic version on the packing body K_h. The first
nonnegative Fejér profile fails for an exact local reason ({−h,0,h} forces S₀ = 2f(h) > 9/7); signed
sinc-power searches found nothing. **The depth bridge (§4.6) is the new lever on μ.**

### 5.7 Agendas received and their status

- **Zhang Yitang (2026).** Landau–Siegel; "remove the square". Verdict: the variational half is
  closed (§5.4); the arithmetic half — sub-face-value debt via the exceptional character — is the
  only door. His "first experiment" (λ_signed vs λ_positive) is answered: no new phase.
- **Bourgain toolkit.** Exp 3 (ACUE × decoupling) done (§2.3, negative for decoupling); Exp 2
  merged with Zhang's; Exp 1 (Type III × additive energy) and Exp 4 (function-field affine sieve)
  never launched.
- **Cross-field tools list** (log-Chowla bridge, exponent-calculus compiler, hypermetric facets,
  magic functions): approved in principle, superseded, never launched.


---

## 6. Failed trials, refutations, and what each one taught

These are first-class results. Each closed a direction that a fresh system would otherwise re-open.

| trial | outcome | insight |
|---|---|---|
| "0.6725 is the exact bandwidth-one LP optimum; AH is suboptimal by 0.0301" (our own Round-1 claim) | **[✗]** retracted (feasible-set conflation) | the free lattice optimum and the Anthropic-feasible optimum live in different cones; 0.0208 of the 0.0301 is aliasing artifact |
| Improve 0.6725 by window engineering | **[✗]** | the clump term forces M = A₀log T for every window; only the M₋ lemma can help |
| Pointwise edge hypothesis \|F(1)−1\| ≤ ε | **[✗]** buys exactly 0 even at ε = 0 | r̂(±1) = 0 for every admissible window; the edge object is the Cesàro mean |
| Derivative pair correlation at bandwidth one | **[✗]** blind | — |
| tr Q³ as a free upgrade | **[✗]** (worthless at flat window; Φ₃ = −0.01178 at MT window but unmonetisable without M₋) | the blocker is the unbounded negative spectrum of the compression, not arithmetic |
| ℓ²-decoupling on the 0.0301 gap | **[✗]** misprices by 15–77× | gap is single-site in position (S₁ ≥ 0 at half spacing), full-band in Fourier |
| Higher traces (tr B⁴…B¹⁰) improving Guth–Maynard by pure deflation | **[✗]** 0% in the idealised regime, 0.1–1.1% with secondary clusters | room must come from additive energy / resonator geometry |
| Matrix / inertia / moment decode for Maynard–Tao | **[✗]** rank-one optimiser; scalar decode optimal | convex-order two-point counterfeit |
| PSD / copositive enlargement of the weight cone | **[✗]** flat | rank-r SOS decouples |
| Signed weights open a new variational phase (Zhang's experiment) | **[✗]** one-line identity | positivity also *bounds* the problem; the value of signed weights is purely arithmetic |
| k = 49 pure-support basis enrichment / SDP kill test | unnecessary | classical upper bound 3.97290 < 4 already kills it; only ε-class alive |
| Higher-order (5+ Fermi sea) secant adversaries for deeper invisibility | **[✗]** L = 2 is globally optimal by pigeonhole (⌊N²/4⌋) | the open problem is the *interference* code (autocorrelation zeros), not the support |
| FUSION-ACUE "KW fusion = ACUE triple pairings" | **[✗]** at N = 3 (22 mismatches) though Verlinde = KW holds | charge bookkeeping in Conjecture A is wrong as stated |
| Marked depth tracks the directional resolvent | **[✗]** an order of magnitude the wrong way | first order is a rank-2 critical-pair contrast; resolvent returns at second order |
| s* = 1.419640342 as the ACUE median limit | **[✗]** median turns at N = 7 | s* is a configuration constant of the single-dislocation stratum |
| ρ ≈ 1.72 as a universal constant in the marked-depth law | **[✗]** | it is κ + (δ/2)κ′/δ′ per mark; law is parameter-free with κ measured |
| Linear heat flow "mixing" hidden fibre directions into visibility | **[✗]** the flow is diagonal; invisibility persists for all t | only the nonlinear stopping time escapes |
| Smooth nine-coordinate LR separator uniform in N | **[✗]** zero margin at N = 4..7 jointly; fails at N = 8 | continuum stability is a two-parameter (mesh × volume) limit; fixed-cardinality certificates can be spurious |
| Nonnegative Fejér profile in the Palm row-sum bound | **[✗]** exact local failure ({−h,0,h}) | signed f with certified packing bounds is the right search |
| Tuple search at k = 35,265 beating 396,504 | not achieved (397,352) | needs iterated merging / LP repair |
| Deligne-route H₂ ≤ 145,226 | **not claimed** | cap-normalisation unverified verbatim |
| Shared-context data errors (H(47) = 232, H₂ = 398,130, exponent 3.815, H(26) = 120) | corrected by agents to 226 / 396,504 / 3.8075 / 114 | keep a living errata list in the context file |

**Meta-lessons.** (a) Each refutation came with the corrected statement; that is the standard to
keep. (b) Five different "phase transitions" turned out to be normalisation artifacts (β-kink,
ℓ¹ ramp, unboundedness at β = 1, ρ = 1.72, the median → s*). Always ask whether the decode is
scale-invariant before reading a growth as a gain. (c) When an idea uses only static
polynomial information about a family that is moment-frozen, it will fail; move to stopping-time /
hitting-time / marked observables.


---

## 7. Verification status, Lean, and where everything lives

### 7.1 Machine verification (`fab_verify_proof.py` / `verification/verify_theorem_steps.py`)

18 checks, 18 passing, no floating point: flow generator identity; 2z_j/(z_j−z_k) = 1 − i·cot;
the (N−1) cancellation; two-body solution and collision time; d/dx cot(x/2) = −½csc²; f(0) = 0 and
f′ = ¼(2tan(x/2) − x); nonnegative Taylor coefficients of tan t − t (⅓, 2/15, 17/315, 62/2835,
1382/155925, …); **the sign lemma as a z3 decision problem (unsat for the negation)**; ACUE
pigeonhole; Σ½csc²(πk/N) = (N²−1)/6 at N = 4,6,8,12,20. Other exact checks: the signed identity on
1,000 random weights across five models; β* with verified dual; the cellwise identity a + G = Gp.

### 7.2 Lean — written, NOT compiled

`research/riemann-rmt/lean/DepthComparison.lean` (also packaged as
`riemann-impostors/lean/RiemannImpostors/DepthComparison.lean` with `lakefile.toml`, toolchain pin
`leanprover/lean4:v4.33.0-rc2` — matching the `anthropics/zeta-23-lean` clone at
`/workspace/anthropics/zeta-23-lean`). Declarations: `cot`, `hasDerivAt_cot`, `cot_strictAntiOn`,
`background_sign`, `self_le_tan`, `neg_log_cos_ge` (proofs written), `two_body_solution` and
`depth_ge` (**sorry**: scalar autonomous ODE uniqueness; Grönwall-type comparison). No toolchain
could be installed: egress 403 for `elan.lean-lang.org` and for GitHub *release* downloads
(`git ls-remote` of public repos works; releases do not; building Lean + Mathlib from source is not
feasible in-session). **If Astra has a toolchain: `lake update && lake build`, then discharge the
two sorries.** Also unformalised but small: the five-line `mult_two_pair` edit in zeta-23-lean
giving N_d ≥ 0.8362503·N + p.

### 7.3 Repository index (branch `claude/riemann-zeta-random-matrix-udxp3f`, PR #11)

`research/riemann-rmt/`:
- Papers: `impostors_paper.md` (canonical, 10 sections), `stopping_times_paper.md`,
  `depth_scaling_theorem.md`, `signed_sieve_nogo.md`, `newman_depth_note.md`,
  `H2_H3_record_announcement.md`, `prime_gap_survey.md`, `round3_synthesis.md`,
  `final_verified_paper.md`, `rmt_zeta_survey.md`, `rmt_zeta_popular.md`, `tao_ah_notes.pdf`,
  `codex_handoff.md`, `README.md`.
- Context files given to agents: `joint_context_v2.md`, `prime_gap_context.md`,
  `signed_context.md` (and `lambda_context.md` in the scratchpad).
- Engines/certificates: `p9_mk_engine.py`, `p9_certify_hp.py`, `p9_exact_cert_k*.json`,
  `p9_tuple_k*.npy`, `p9_g_k*.npz`, `p9_scan.py`, `p9_tuples.py`, `verify_codex.py`.
- Theorem checks: `fab_*.py` (+ `*_results.json`), `sgn1_t1_exact.{py,json}`, `beta_*.py`,
  `tomo_fiber.py`, `d6_allN_family.py`.
- `riemann-impostors/`: standalone package (README = labeled results summary; paper/, lean/,
  counterexamples/, verification/, certificates/, data/ with `dyn1_results_N3..10.npz`;
  `PUBLISHING.md` — repo creation returned 403 from the GitHub App integration, so publish via
  `git subtree split`).
- `handoff/`: this document (md + pdf).

Session scratchpad (`/tmp/claude-0/…/scratchpad`, ~1,150 files) holds everything else: `dyn2_data_N*.npz`
(CUE, N = 2..256), `beta_data_b{1,4}_N*.npz`, `monsep_*`, `fus_*`, `brg_*`, `dir*_`, `p1_–p10_*`,
`sgn*`, `tomo_*`, `dyn1_*`, agent logs. It survived two container restarts but is not guaranteed
to outlive the session; anything essential has been copied into the repo.

### 7.4 Key constants (verified this programme)

δ_MT = 3/2 − (1/√2)cot(1/√2) = 0.672500703679 · PairCeiling 0.6818287 · ceiling candidate 15/22 ·
Φ₃(MT) = −0.0117753128 · N_d/N ≥ 0.8362503 · deficiency ledger 0.3275 · M₋ payoffs 0.6796896 /
0.6844924 · δ_free → ½ + 2/π² = 0.70264237 · doubles density 1/4 − 1/π² = 0.148679 · M₂ = 1.385933,
M₃ = 1.646440, M₄ = 1.845401, M₅ = 2.007080 (Q₅ exact above), M₅₄ > 4.00238, M₄₉ ≥ 3.891257590916,
M_{49,1/35} ≥ 3.930490592 (float 3.959325169) · β* = 2.0973249209 · π²/8 = 1.2337005501 ·
s* = 1.419640342, u* = 1.812942145, ρ_∞ = 1.150717118 · separated-defect ρ = 1.19120
(N²(−Λ) = 1.46946) · ρ_max → 1.6094 · 72π = 226.19 · (72π ln2)^{2/3} = 29.08 · N* ≈ 165 ·
LR: 1/2 ≤ μ ≤ 0.606894 ⟺ μ_Λ ≤ 1.8177 · clock stiffness (N²−1)/6 · fibre dims 0,0,2,10,80,403,1804.


---

## 8. Open problems, ranked, with the exact statement and its price

1. **The background bound [the linchpin].** Prove: for CβE (β fixed), with probability → 1 the
   background stiffness of the first-colliding pair satisfies S ≤ A·N² (measured median 0.120·N²,
   max 0.79·N²). This single rigidity statement upgrades to theorems: 8N^{8/3}(−Λ) ⟹ G² (β=2),
   −Λ ≍ N^{−2−2/(β+1)} for all finite β, and Theorem C(ii). It is a standard-shaped estimate
   (Σ_k d_k^{−2} near the extremal pair) and is the best-value item on this list.
2. **ρ_∞ = O(1) for ACUE at all N** (lattice upper bound). Deterministic; proven only for N ≤ 10 by
   enumeration (ρ ∈ [1.049, 1.610]); the minimising family's ρ decreases toward ≈ 1.03–1.05.
3. **Exact constants:** s* = 1.419640342 as a theorem (infinite clock + one dislocation under the
   Coulomb flow; Calogero–Moser framing); the separated-defect ρ = 1.19120…; ρ_∞ of the minimising
   family. Targets: closed forms in theta/Bessel/trigonometric data.
4. **The marked-depth law as a theorem**, Dτ[uu*] = (κδ/4)u*K_ab u + (δ²/8)κ′(u), with κ′
   characterised; on the null cone c_a q_a = c_b q_b the leading term should be
   λ_j″ = 2q_j Σ q_k/(λ_j − λ_k).
5. **Transversality theorem:** τ|_{F_m} generically non-constant; marks added until
   ⋂ ker DΛ_{u_j} ∩ ker DM = {0}.
6. **The M₋ lemma** on the zeta side: ‖(c⁻¹Â)₋‖ ≤ M₋ uniform in T; worth +0.007..0.012 on 0.6725.
7. **The 15/22 ceiling identity** and **d* = 3(N−3)** kill-degree law (exact-arithmetic conjectures).
8. **(E_θ)** for any θ > 1/2 (cheapest: 7/12) — the one statement between the price list and
   H₁ ≤ 114/130.
9. **k = 49 ε-door:** push the Galerkin engine to d = 20–22 at ε ∈ {1/40..1/30}, warm-start from
   `p2_vec_hp_k49_d18_e35.npy`; if the float plateaus < 3.98, try the vanishing-marginal variant;
   non-separable dual certificates are the only known way to *close* the door above ε = 0.0068.
10. **SHELL-M49:** compute M₄₉ on Maynard-III's shell polytope with the ε-trick layered; needs
    8–13% of the full-shell surplus; undecided in print.
11. **Tuple k = 35,265 below 396,504** (best 397,352; add iterated merging + LP repair).
12. **Interference code / phase-rigidity conjecture:** among phase-twisted Slater states
    u ∈ U(1)^{2N}, vanishing of all balanced Schur minors below ⌊N²/4⌋ forces u_c = αβ^c up to
    gauge/dihedral symmetry (would make the det-character impostor the canonical extremiser of its
    whole class). Computationally attackable via circulant Toeplitz minors / Plücker relations.
13. **FUSION-ACUE, corrected:** find the charge bookkeeping under which KW fusion matches ACUE
    triple pairings (fails at N = 3 as stated).
14. **Function-field Newman universality** (§9.4).
15. **Formalisation:** discharge the two Lean sorries; formalise the records' certificate chain;
    make the five-line `mult_two_pair` edit.


---

## 9. Wide-open research programme for GPT6 Astra: which famous conjecture, and by what route

This section answers the second half of the handoff request. It is opinionated and it is honest
about odds. The ordering is by (probability of a genuine theorem) × (size of the theorem), not by
glamour. The human's stated ambition is a historic result, not another small one; the way to earn
that is to pick the target whose *remaining gap* is a statement of a shape people already know how
to prove.

### 9.1 The best target: refute the Alternative Hypothesis dynamically

**Claim to aim for.** *Under a hypothesis strictly weaker than GUE, the zeros of ζ cannot have
asymptotic hard core 1/2.* Equivalently, a proof that the Alternative Hypothesis is false — the
statement Tao, Lagarias–Rodgers and others have posed as the obstruction to Montgomery.

**Why this is now the right target.** The static route needs pair-correlation information at
Fourier bandwidth > 1, which is exactly what no one can prove. The dynamic route needs only that
*the zeros are, locally, more fragile than a lattice under the de Bruijn–Newman flow*. Concretely
(Theorem C(i) + the LR bridge, both **[P]**): AH ⟹ every window's local depth satisfies
liminf N²(−Λ) ≥ π²/8 = 1.2337. So:

> **Level B target.** For ζ, with N = (log T)/2π zeros in a window at height T under the *true*
> H_t flow, prove liminf (log T)²·D_T < π²/8 — or merely D_T = o((log T)^{−2}) — from averaged
> information (pair-correlation at bandwidth ≤ 1, plus variance/energy inputs of Rodgers–Tao type).

Level A (the full N^{−8/3} CUE law) is *not* needed; Level C (liminf(log T)²D_T = 0 along a
subsequence) may already exclude rigid subclasses.

**What Rodgers–Tao already give you.** Their proof of Λ_dBN ≥ 0 runs exactly this kind of
argument in reverse: assume the zeros are over-stable (Λ < 0), push the flow, obtain a local clock
equilibrium, contradict known fluctuations. The needed extension is *quantitative and local*: the
same energy method in a window, with the over-stability hypothesis replaced by "hard core 1/2" and
the contradiction replaced by a fluctuation input weaker than GUE. The finite results say what the
right normalisation is (the clock stiffness (N²−1)/6; the two-body constant 1/8; the singular
endpoint at β = ∞ where the background is leading-order).

**Steps, in order.**
1. **Truncation theorem.** One may not cut a window of zeros and call it a polynomial. Use the
   Polymath15 machinery for H_t (effective approximations to the flow) to define D_T rigorously
   and prove that the window's first collision time is controlled by the finite depth of the
   local configuration up to o(1) — the same localisation lemma as Theorem B, now for ξ.
2. **Hard-core ⟹ depth (already proved at finite N).** Transfer Theorem A to the H_t flow (the
   cotangent interaction becomes the Rodgers–Tao kernel; the sign argument survives since it only
   uses monotonicity of the pair interaction).
3. **The fluctuation input.** Show that near-collisions at scale o(1/N) occur along a positive
   proportion of windows using *only* bandwidth-≤1 pair correlation plus an energy/variance bound.
   Note Montgomery's own theorem already gives a positive proportion of gaps < 0.68 mean spacing
   (unconditionally, via bandwidth-1 data); the question is whether such inputs plus the flow give
   gaps *below 1/2* often enough to break the floor. This is where new mathematics is required, and
   it is a concrete analytic-number-theory question, not a random-matrix metaphor.
4. Assemble: (2) + (3) ⟹ liminf N²D_T < π²/8 ⟹ AH false.

**Risk.** Step 3 may be equivalent in strength to the static statement one is trying to avoid. The
finite theory suggests not — the depth is a *first-passage* quantity and Theorem C(ii) needed only
the gap tail plus a bounded background — but this has to be settled on the zeta side. Either way
the outcome is a theorem: either AH is refuted, or a precise equivalence "dynamic AH-refutation ⟺
bandwidth-(1+η) pair correlation" is proved, which would itself be new.

### 9.2 Second target: the Lagarias–Rodgers conjecture μ = 1/2

Fully within random-matrix/point-process theory, no arithmetic input. **[P]** already: μ ≤ √(2μ_Λ)/π.
So one needs a *depth upper bound* for every bandwidth-one sine mimicker: prove that any such
process has liminf N²(−Λ) ≤ M with M < 1.8177 to beat the published bound, and M ≤ π²/8·ρ_lat to
reach 1/2. Route: transport the Palm row-sum-square / multiwindow packing-body certificates (LR
docs, Prop 5.1–5.2) from the row sum to the depth. The depth is smooth in the configuration
(gradient computed in §4.9), has an explicit critical-pair derivative law, and — unlike the row sum
— has no known local obstruction of the {−h,0,h} type. A win here is a clean, publishable theorem in
its own right and directly feeds 9.1.

### 9.3 Third target: a Dyson–Montgomery statement one can actually prove

The honest position: the full pair-correlation conjecture is not reachable by these tools. What
*is* plausibly reachable, and would count as a partial Dyson–Montgomery result, is a **dynamic
universality theorem**:

> *Any point process with (a) bandwidth-one sine pair correlation, (b) a repulsion exponent β at
> short range, and (c) bounded background stiffness, has finite depth law −Λ ≍ N^{−2−2/(β+1)}.*

This is Theorems A + B plus the extreme-gap input, stated abstractly; the CβE case reduces to
Feng–Wei, and the ACUE case is the β = ∞ endpoint. It says the Newman depth is a *fingerprint of the
repulsion exponent* — a random-matrix theorem with a clear statement, four confirmed data points and
one missing lemma (open problem 1). Expected effort: weeks, not years.

### 9.4 Fourth target: function-field Newman-depth universality (Katz–Sarnak)

Function-field Newman constants exist in the literature (Andrade–Chang–Miller-type explicit
formulas; e.g. Λ_{D_p} = log(|a_p|/2√p) at genus 1 is exactly our N = 2 law in arithmetic clothing).
Define, for a family of L-functions over F_q with Frobenius classes Θ_C ∈ G, the depth of
det(1 − uΘ_C); Λ is a highly nonlinear class function on G. **Theorem to prove:** as q → ∞ at fixed
rank N, Law(Λ_C) → Law(Λ_Haar(G)) for USp/SO/U families with big monodromy (Katz–Sarnak
equidistribution pushes through a *singular* statistic because Λ is continuous off the discriminant
locus, whose Haar measure is zero; the delicate part is the near-collision set). Then N → ∞ gives
the universality exponents per symmetry class, with the ±1 hard edge in Sp/SO possibly changing the
minimal-gap law. Our monodromy-separator computation (§3.5) shows the det-sector is already dark at
q^{−1/2}; the U(N) family machinery (`monsep_core.py`) is reusable. This is the most *reliable* big
theorem on the list, and the one best suited to a geometric collaborator.

### 9.5 Prime gaps: from 246 (or from the reported 186) downward — what is and is not possible

**Consistency check on "186".** H(40) = 186 exactly, so a proof of H₁ ≤ 186 is a proof of
DHL(40, 2). Under Bombieri–Vinogradov (θ = 1/2) that needs a Maynard–Tao variant > 4 at k = 40.
The classical bound gives pure M₄₀ ≤ (40/39)log 40 = **3.78347**, so the pure problem is
*impossible*; an ε-variant needs (1+ε)·3.78347 > 4, i.e. **ε > 0.05723** — far beyond anything
Polymath ever certified (their ε-trick at k = 50 used ε ≈ 1/25 and moved M by ≈ 0.02); alternatively
a level of distribution θ with 2/θ < M₄₀-variant, i.e. **θ > 0.529** at least (with pure M₄₀ ≈ 3.75
one needs θ > 0.533), which is beyond Maynard III's 11/21 = 0.5238 and would need residue-uniform
input of (E_θ) type. So *if* 186 is real, its proof contains either a new equidistribution theorem
at level ≳ 0.53 uniform in CRT residues, or a variational enlargement beyond every known variant.
Astra should first identify which, since that determines everything below. (If the number was
actually 246, ignore this paragraph.)

**From wherever the record stands, the levers, priced:**
- **k = 49 ε-door → 240**: open, undecided; float 3.9593 vs 4; degree-22 Galerkin + ε-scan
  (open problem 9). Cheapest possible improvement of 246.
- **k = 47 → 226**: pays 20; needs ≈ 0.06 more in M or a level δ ≈ 0.006.
- **(E_{7/12}) → 114**, **(E_{4/7}) → 130**, **(E_{3/5}) → 94**, **(E_{5/8}) → 80**: the
  well-factorable route, blocked only by the tuple-residue estimate (E_θ). This is the route with the
  largest payoff and the clearest missing statement; the structurally cheapest is 7/12 where λ can
  literally be Iwaniec's λ^±.
- **EH ⟹ 12**, **EH + OMC₈ ⟹ 8**, **EH + quartic block ⟹ 6**; parity floor 6 absolute.
- **What cannot work** (walls 1–5): post-processing, matrix decodes, PSD/copositive cones, signed
  weights at face-value debt, zero-density inputs, GRH.
- **m ≥ 2 records are ours and are far from optimal**: Galerkin/ε refinement would shave 3–10% off
  k*; H-R tuple repair at k = 5.6·10⁷; the Deligne cap-normalisation (verify verbatim → H₂ ≤ 145,226).

### 9.6 A formalisation programme in the FLT style

We could not read Anthropic's post on formalising Fermat's Last Theorem; Astra should, and should
import its agent architecture. What in this programme is *ready* to formalise, in order of value per
effort: (1) Theorem A (two sorries away); (2) the five-line `mult_two_pair` edit giving
N_d ≥ 0.8362503·N + p in `zeta-23-lean` — a strictly stronger published constant, in an existing
verified codebase; (3) the records' hypothesis chain (Maynard's theorem is not in Mathlib, but the
*certificate* — ball-arithmetic bounds on I and J for an explicit F — is a finite verification and
the tuples' admissibility is decidable); (4) the signed no-gain identity (trivial to formalise,
useful as a lemma); (5) P(clock) = 2^{1−N} and δ_min = π/N.

### 9.7 Speculative but structured: the "Newmanised parity barrier"

ACUE proved once that a static information barrier is not a dynamic one. The twin-prime parity
barrier is also a static barrier (sieve-accessible observables cannot separate a and b). Look for a
flow S_t on arithmetic sequences — the Dobner flow a_n ↦ a_n e^{(t/4)log²n} is the canonical
candidate, being the dBN flow on the Dirichlet side — under which sieve observables stay matched but
a positivity/stability hitting time differs. No theorem is known; the problem is now well-posed
enough to search.

### 9.8 What not to spend the first month on

Larger N simulations of the depth (the exponents are settled); five-Fermi-sea adversaries (L = 2 is
optimal); decoupling on the bandwidth-one gap; pure-support k = 49; higher traces for Guth–Maynard
by deflation alone; any "new phase" from signed weights; window engineering on the zeta side.

---

## 10. Closing note to Astra

The programme's single deepest fact is that the invisibility hierarchy of Tao's impostors and the
stability spectrum of the zero dynamics at the clock are the same operator: impostors hide exactly
where the flow acts hardest. Everything else — the depth laws, the separation, the LR bridge, the
π²/8 threshold — is that fact read in different coordinates. The route to a historic theorem runs
through §9.1, and its one genuinely new ingredient (step 3) is an analytic statement about
near-collisions of zeros that current technique might reach. Prove open problem 1 first; it costs
little and upgrades three numerical laws to theorems. Then go for AH.

Everything here is reproducible from the repository. Where we were wrong, we have said so; where
we were uncertain, the tag says so. Good hunting.

