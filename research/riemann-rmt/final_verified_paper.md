# Finite Spectral Certificates and Their Fibers: A Verified Synthesis

## What is actually proved, what is actually new, and what it means for the Riemann zeta function, the Alternative Hypothesis, and random-matrix inverse problems

**Bill (Qingyun) Sun · GPT5.6SOL · Fable**

*August 11, 2026*

---

## Abstract

This paper is a critical synthesis, with independent verification, of a series of finite-mathematics manuscripts produced around the 2026 unconditional theorem that at least δ_MT = 3/2 − (1/√2)·cot(1/√2) = 0.672500703679… of the nontrivial zeros of the Riemann zeta function are simple zeros on the critical line [Claude 2026]. The source manuscripts (the "finite spectral" series) are dense and difficult to referee by eye; we have therefore re-proved their central identities by hand where short, and re-verified every machine-checkable claim by independent computation — exact enumeration of determinantal laws, quadratic programming, and symbolic identity testing. Every exact claim we tested is **correct**; three apparent failures were traced to typographic ambiguity in the source PDFs and resolved in the papers' favor. We also record two claims that we could *not* independently verify and one place where an earlier synthesis (our own) overstated a result, which the present series correctly retracts.

The verified core consists of eight theorem packages. On the zeta-adjacent side: a closed-form finite Galerkin solution of the Montgomery–Taylor extremal problem with exact n⁻² error, making 0.6725007… an exactly computable finite object rather than a numerically fitted constant; and an exact "Nyquist conservation law" for integer-marked half-filled cyclic ensembles, in which one missing Fourier mode simultaneously stores all repeated-point mass, dualizes nearest-neighbor exclusion, and produces the density curve Φ(ρ) = 1 − ρ + sin²(πρ)/(π²ρ), with Φ(1/2) = 1/2 + 2/π². On the random-matrix side: an exact fourth-moment covariance formula for the finite Fermi-sea (ACUE-type) projection ensemble, Cov(V_k, V_ℓ) = k²·1{k=ℓ} − 2(k+ℓ−N)₊ with smallest eigenvalue exactly 1, yielding a quantitative moment-polytope inradius and an approximation-to-exact-law repair theorem; and four sharp non-identifiability theorems — Fermi-sea boundaries, magnetic-cycle holonomy with an exact total-variation formula, the quasi-free axiom gap with its necklace-counting fiber dimension, and marked homometry surviving complete diffraction. Finally, the series reduces its one central open problem — all-size attainment of the Nyquist equality face — to a three-tile integral language with exact no-go theorems for every natural construction.

We explain, for each package, what is classical, what is new, why it matters for the Riemann Hypothesis and the Alternative Hypothesis of Lagarias–Rodgers and Tao's ACUE, and what would falsify or extend it.

---

## 1. Provenance, method, and the verification protocol

### 1.1 What this paper is

Three survey manuscripts and their companion papers (referred to below as **[FSC]** *Finite Spectral Completion*, **[A23]** *After the Two-Thirds Theorem*, and **[FSI]** *Finite Spectral Identifiability*) were produced by a multi-agent research system. They contain a mixture of: classical mathematics restated; exact new finite theorems with short proofs; conditional thermodynamic statements; deliberate counterexamples ("counterfeits"); and open problems. A working mathematician reading them cold faces two obstacles: the volume (roughly eighty pages of dense statements), and the absence of external referee reports. The purpose of the present paper is to remove both obstacles for the results that deserve attention: we verify, we prune, and we explain.

### 1.2 Verification protocol

Each testable claim was checked by at least one of:

- **(H)** a complete short hand proof, reconstructed independently;
- **(E)** exact enumeration — determinantal laws computed as principal minors over all configurations, probabilities summing to 1 within 10⁻⁹, claimed identities holding to ≤ 10⁻⁹ (usually 10⁻¹³);
- **(N)** high-precision numerics against closed forms (quadratic programs to 10⁻¹⁰; constants to 12 digits).

The full script battery is available alongside this paper (`verify_codex.py`). The headline outcome:

| Claim | Source | Method | Verdict |
|---|---|---|---|
| q\* = ½ + (1/√2)cot(1/√2); optimizer v\*(s) ∝ cos(√2 s); δ_MT = 2 − q\* | [A23] §3.2 | H + N | **Correct** |
| Galerkin closed form q_n and its n⁻² error coefficient | [A23] Prop 3.1 | H + N | **Correct** (see §1.3) |
| Nyquist collision identity E∑m(m−1) = (E\|p_N\|² − N)/2N | [FSC] Thm 5.1, [A23] Prop 3.2 | H | **Correct** |
| Full slack identity, equality face {0,1,2}-hard-core, Φ(ρ) curve | [FSC] Thm 5.1 | H + N (per-sample) | **Correct** |
| Cosine sum 2∑k·cos(πk/N) = N − csc²(π/2N) | [FSC] §5 | N (N = 2…39) | **Correct** |
| Fourth moments: Cov(V_k,V_ℓ) = k²1{k=ℓ} − 2(k+ℓ−N)₊; λ_min = 1 | [FSC] Thm 6.1 | E (N = 2…6) | **Correct** |
| Support bound ‖V − T_N‖₁ ≤ N² − N/2 | [FSC] Thm 6.2 | E (N ≤ 6) | **Correct** |
| Magnetic cycle: sub-g minors phase-blind; det gap; d_TV = (2r)^g\|cos gφ − cos gψ\| | [FSI] §5 | E (g = 3,4,5) | **Correct** |
| Marked homometric pair on ℤ/12 (autocorrelation, simple fractions 0 vs ½, cubic separation, no extinction) | [FSI] §7 | E | **Correct** |
| DPP homometric pair S={0,1,4,6}, T={0,1,3,7}: same covariogram, triple probabilities (8∓√3)/432 | [FSI] §4 | E (exact match to 10⁻¹²) | **Correct** |
| Deck-fiber dimension = n(M,L) − n(M,r) (necklace counts) | [FSI] §6 | E (5 cases) | **Correct** |
| F(γ) = ½\|S △ (S+γ)\|; F(1) = number of runs | [FSI] §4 | E (exhaustive M ≤ 12) | **Correct** |
| Tile language: \|E_N\| = C(2N,N); tile decomposition; filter q̂(k) = (1+e^{iπk/N})p_k | [FSC] Thm 8.1 | E | **Correct** |
| N = 3 lift obstruction: liftable charge spectra exactly {(0,0),(3,9),(9,3)}; DPP atom 111000 ↦ (12,0) outside | [FSC] Thm 8.2(ii) | E (exhaustive) | **Correct** |
| Destructive cross-spectrum 2Re E[η̂ h̄̂] = −E\|ĥ\|² | [FSC] Thm 8.2(iii) | H (one line) | **Correct** |
| Wilson fourth trace: tr A⁴_flat − tr A⁴ = 16∑_f w_f sin²(φ_f/2) on the free box | [FSI] §9 | E (three box sizes) | **Correct** |
| CCM finite Pontryagin extension: SDξ = −β, SD′ = D′\*S, D′ξ = 0 | [A23] §5.2 | E (random instance) + H | **Correct** |
| Determinant-tail counterfeit constant −1152/49 | [A23] §5.5 | H (series expansion) | **Correct** |
| Negative-square budget (1−δ_MT)/2 = 0.163749648160 | [A23] §4.3 | H | **Correct** (elementary corollary) |
| Prouhet trace counterfeit; Euler–Lee–Yang rank obstruction; Hurwitz rigidity | [A23] | H | **Correct** (classical mechanisms) |

**Not independently verified** (flagged, not doubted): the GOE counterfactual constant 0.559871849060 (the kernel normalization for the K₁ form factor is not reconstructible from the survey text alone); the PairCeiling value 0.6818287 (the source itself reports a verification boundary: a hashed rational witness absent from the public Lean repository — see §7.3); the N ≤ 6 cyclotomic endpoint certificates (asserted in companion papers we have not audited line by line); and all conditional thermodynamic statements (correctly labeled as conditional in the source).

### 1.3 Three transcription corrections

Three claims initially *failed* verification and were traced to reading errors rather than mathematical errors; we record them because future readers of the PDFs will hit the same traps. (i) In the Galerkin formula, the printed `arccos(1−n−2/an)` means θ_n = arccos(1 − n⁻²/a_n), not arccos((1−n⁻²)/a_n); the correct reading follows from the second-difference recurrence v_{i+1} − 2v_i + v_{i−1} + (2/n²a_n)v_i = 0, and with it the closed form matches the quadratic program to 10⁻¹³. (ii) The charge-filter identity holds with the phase (1 + e^{+iπk/N}) in the transform convention q̂(k) = ∑q_x e^{−iπkx/N}; only |1 + e^{±iπk/N}|² = 4cos²(πk/2N) is used downstream, so nothing depends on the sign. (iii) The Wilson fourth-trace identity is stated on the *free* (open-boundary) box; on a periodic box winding 4-walks add cycle-holonomy terms and the identity genuinely fails — the hypothesis is load-bearing, and the papers state it.

---

## 2. The constant, finally an exact finite object

### 2.1 Background

Montgomery's pair-correlation method (1973) bounds the proportion of simple zeta zeros using one quadratic functional of a test profile v on I = [−1/2, 1/2]:

  E(v) = ∫_I v² + ∫_I∫_I |s−t| v(s)v(t) ds dt,  normalized by ∫_I v = 1.

The kernel |s−t| is fed by the unitary (CUE) pair form factor min(|u|,1) — this is the precise sense in which "random matrices" enter. Montgomery and Taylor found the optimum: the Euler equation v + T v = const differentiates to v″ + 2v = 0, giving

  **v\*(s) = cos(√2 s)/(√2 sin(1/√2)), E(v\*) = q\* = ½ + (1/√2)cot(1/√2) = 1.327499296320…**

and the integer-multiplicity ("secant") decoding step maps q\* to 2 − q\* = δ_MT = 0.672500703679…. Under RH this gave the classical Montgomery–Taylor simple-zero proportion; the 2026 theorem obtains the same constant *unconditionally* by measuring finite compressions of the indefinite Weil explicit-formula form from the prime side and decoding positive inertia through rank–trace inequalities. We verified the variational solution independently (discretized QP, n = 4000: optimum matches q\* to 8 digits, profile matches cos(√2s) to 6×10⁻⁹).

An important bookkeeping point the series gets right and popular accounts get wrong: the constant is the output of *two* operations — a pair-energy optimization (which is random-matrix geometry) and an integer-multiplicity secant (which is arithmetic of multiplicities). Neither alone produces the decimal.

### 2.2 New result: the exact Galerkin certificate (verified)

**Theorem (Galerkin closed form).** Partition I into n cells and minimize the exactly integrated piecewise-constant energy. With a_n = 1 + 1/(3n²) and θ_n = arccos(1 − 1/(n²a_n)), the minimum is exactly

  q_n = ½ + (a_n n/2)·sin θ_n · cot(nθ_n/2),

and δ_n = 2 − q_n = δ_MT − [csc²(1/√2) − √2·cot(1/√2)]/(24 n²) + O(n⁻⁴).

We verified the closed form against direct quadratic programming for n = 2, …, 80 (agreement 4×10⁻¹⁴) and confirmed the n⁻² coefficient numerically. **Why this matters:** it converts 0.6725007… from "the output of an optimization run" into a checkable finite formula with a proved discretization rate. Any formalization, discretized dual certificate, or SDP approximation of the Montgomery–Taylor problem can now be unit-tested against an exact ladder q_2, q_3, … → q\*. It is a modest theorem with an outsized hygiene value: constants in this subject have historically propagated through numerics.

### 2.3 A clean corollary: the off-line pair budget

Since every distinct off-critical zero pair {ρ, 1−ρ̄} consumes at least two zeros of the count while contributing none to the simple-critical count, the two-thirds theorem immediately gives

  limsup_{T→∞} p(T)/N(T) ≤ (1 − δ_MT)/2 = **0.163749648160…**,

where p counts distinct off-line reflection pairs. In the Pontryagin-space reading of the Weil form (each off-line pair = one hyperbolic plane = one negative square), this is a *normalized negative-index budget*: the density of hyperbolic defects of the Weil form is at most 0.1637…. The proof is one line; the value of the statement is the typing. It is not a bound on the number of off-line zeros (which can still be infinite), and RH requires the budget to be zero, not small. We verified the arithmetic; the conceptual frame (ambient signature vs. observed signature, and the theorem that a finite Gabor observation can *hide* a negative square — the eigenvalue-collapse estimate |λ₋| = O(a²) for a pair at distance a from the line) is the series' most useful contribution to the operator-theoretic reading of the theorem.

---

## 3. The Nyquist conservation law (the strongest new theorem package)

### 3.1 Setting

Fix N, let m = (m_x), x ∈ ℤ/2N, be random nonnegative integer marks ("zeros with multiplicity") with ∑m_x = N in every sample, and let p_k = ∑_x m_x e^{iπkx/N}. The reference is the rank-N consecutive-band projection determinantal process — the finite Fermi sea, whose scaling limit realizes Tao's ACUE and the half-lattice Alternative Hypothesis, and whose form factor is the finite CUE ramp E|p_k|² = min(k, N). Impose only the *open* rows:

  E|p_k|² = k for 1 ≤ k ≤ N−1,  (the Nyquist row k = N left free).

### 3.2 The three verified identities

**(a) Collisions live only at Nyquist.** For every such law (hand proof from Parseval, three lines):

  E ∑_x m_x(m_x − 1) = (E|p_N|² − N)/(2N).

Consequently, closing the endpoint row E|p_N|² = N forces all marks into {0,1}: *the complete finite ramp admits only simple configurations.* One missing measurement is exactly the storage location of all multiplicity.

**(b) The slack identity.** Let s₁ = #{x : m_x = 1} and h(j) = 0 for j ≤ 2, j(j−2) for j ≥ 3. Then

  E s₁ − (N/2 + csc²(π/2N)/(2N)) = E ∑_x m_x m_{x+1} + E ∑_x h(m_x),

with both right-hand terms nonnegative. We reconstructed the proof: the observable s₁ − ∑m_x m_{x+1} − ∑h(m_x) equals 2N − (1/2N)∑_k |p_k|²(1 + cos(πk/N)) *configuration by configuration* (verified per-sample to 4×10⁻¹⁴ over random marked configurations), and the crucial mechanism is that the Nyquist coefficient 1 + cos π = 0 — this particular combination of simple-site count, nearest-neighbor overlap, and high-mark penalty is *blind* to the one unconstrained Fourier row. Taking expectations under the open ramp and using the (verified) cosine identity 2∑_{k<N} k cos(πk/N) = N − csc²(π/2N) gives the constant.

**(c) The equality face and the density curve.** Equality holds exactly on hard-core {0,1,2}-configurations (no adjacent occupied sites, no mark above 2), and the bound

  E s₁/N ≥ ½ + csc²(π/2N)/(2N²) → **½ + 2/π² = 0.702642367284…**

follows, together with the all-density version: matching the rank-L band process at every row except Nyquist forces E s₁/L ≥ Φ(ρ) := 1 − ρ + sin²(πρ)/(π²ρ) in the limit L/M → ρ. At low density Φ(ρ) = 1 − (π²/3)ρ³ + O(ρ⁵): the sine kernel's quadratic repulsion becomes a *cubic* collision-rigidity loss. All numerics confirmed, including the finite value at N = 256 (0.702644910435).

### 3.3 Why this is genuinely new mathematics

The ingredients (Parseval, Fourier inversion, Delsarte duality) are classical; the theorem package is not, and we consider it the strongest publishable unit of the whole program:

1. **It is an exact conservation law, not an inequality found by search.** One scalar budget (the Nyquist intensity) is simultaneously: the factorial collision count (a), the dual variable of nearest-neighbor exclusion (b), the equality-face selector (c), and — in the conditional thermodynamic extension — the mass of a period-two Bragg atom whose square norm is a dynamical ℤ/2-eigenfunction. Exact four-way dictionaries of this kind are rare.

2. **It sharpens, and finitizes, the known relationship between the Alternative Hypothesis and multiplicity.** The AH scenario stores zeros on a half-integer lattice; the finite theorem says precisely which *measurement* separates the multiplicity-carrying half-lattice world from the forced-simple world: the order-two character at the edge of the band, whose normalized weight (1/N) vanishes in every scaling limit. A statistic invisible in the vague limit rigidly controls the integer feasible cone. This is a precise finite mechanism for a phenomenon that in the zeta literature is only heuristic ("the AH hides at the edge of the Montgomery band").

3. **It cleanly separates relaxation sharpness from realizability.** The pair-cone (Delsarte) endpoint a\* = L + L² − D²_{M,L} is certified by the single facet C(1) ≥ 0; but the series proves — with an explicit (M,L) = (6,3) law — that *realizing the extremal pair function does not imply attaining the simple-site equality*, because of the mark-≥3 penalty channel. Optimization sharpness and probability-law sharpness are different theorems. This distinction, verified and correct, is exactly what most informal "LP bound = truth" arguments in this area elide (including, we note candidly, an earlier synthesis by the present authors — see §7.2).

### 3.4 The two constants that must not be confused

The series is emphatic, and correct: **½ + 2/π² = 0.70264… is not an improvement of δ_MT = 0.67250…, and neither bounds the other.** The first is a lower certificate for the simple-*site* fraction in a marked integer moment model with an open Nyquist row; the second is a lower proportion of simple critical zeta zeros proved from arithmetic. Different state spaces, different observables, different theorems. Their kinship is methodological — in both, a low-order spectral certificate is strengthened by integrality, and a missing Fourier direction marks the boundary of what the certificate can see.

---

## 4. Fourth moments, the moment polytope, and exact repair

### 4.1 The covariance formula (verified exactly)

For the half-filled finite Fermi sea on ℤ/2N (the discrete-CUE/ACUE reference law), with V_k = |p_k|², 1 ≤ k < N:

  **E[V_k V_ℓ] = kℓ + k²·1{k=ℓ} − 2(k + ℓ − N)₊, Cov(V_k, V_ℓ) = k²·1{k=ℓ} − 2(k + ℓ − N)₊.**

We verified this by exact enumeration of all C(2N, N) determinantal atoms for N = 2,…,6: the ramp E V_k = k holds to 10⁻⁹ and the covariance matches entrywise to 10⁻⁹. Structurally: the diagonal k² is the free-fermion exchange term, and the negative correction −2(k+ℓ−N)₊ counts the two cyclic wrap intervals produced when two particle-hole excitations of total momentum k+ℓ exceed the band. Off-diagonal entries are ≤ 0 and Gershgorin gives C_N ⪰ I; we confirmed **λ_min(C_N) = 1.000000 exactly at every tested N**, with the first coordinate an eigenvector.

### 4.2 Inradius and the repair theorem

Two consequences, both verified where checkable. First, the binary feature rows affinely span ℝ^{N−1} and the CUE target T_N = (1, …, N−1) is interior to their convex hull, with Euclidean inradius ρ_N ≥ 1/(N² − N/2) (via λ_min = 1, the Bhatia–Davis inequality, and the support bound ‖V − T_N‖₁ ≤ N² − N/2, which we confirmed by enumeration through N = 6 — the observed maxima 1, 5, 10, 16.94, 27 all sit below the bound). Second, the **repair theorem**: if a candidate law on the hard-core equality face matches the ramp to feature error ε_N, it can be mixed with an explicitly constructed binary correction law (a density tilt 1 + ⟨C_N⁻¹y, V − T_N⟩) to match the ramp *exactly*, at simple-site slack cost ≤ N·ε_N/(ρ_N + ε_N); in particular feature error o(N⁻²) suffices for o(N) slack.

### 4.3 Assessment

The covariance formula is, to our knowledge, a new exact computation (fourth moments of Fourier intensities for the finite band projection process), and the inradius/repair mechanism is a genuinely useful bridge: it reduces the hard open realizability problem (§6) from "construct an exact law" to "construct an approximate law at rate o(N⁻²)" — a strictly easier analytic target with a quantified exchange rate. The connection of three usually separate languages — fermionic normal ordering, convex geometry of truncated moment problems, and stability of integer realization — is the innovation; the individual tools are standard.

---

## 5. Four identifiability theorems: what pair data can and cannot know

This is the random-matrix side proper — the inverse-problem geometry underlying "zeta zeros look like CUE eigenvalues." Each theorem is finite, exact, and verified.

### 5.1 Form factors are Fermi-sea boundaries

For a stationary projection DPP on a finite abelian group with Fourier support S, the form factor at γ is exactly a boundary: F(γ) = ½|S △ (S+γ)|; on a cycle, F(1) equals the number of occupied runs of S (verified exhaustively for all subsets of ℤ/M, M ≤ 12). Hence F(1) < 2 ⟺ S is one interval: **inside the stationary projection class, a single scalar — the first form-factor row — identifies the discrete-CUE law.** Every edge-isoperimetric inequality transfers to a form-factor inequality with no loss (the Cayley identity ∑w_α F(α) = |∂S|).

But the same dictionary shows its limit: the full form-factor table is the covariogram of S, and covariograms admit homometric pairs. The witness S = {0,1,4,6}, T = {0,1,3,7} in ℤ/12 (verified: equal covariograms; not translates or reflections) gives two projection DPPs with identical 1- and 2-point functions whose triple probabilities differ: P({0,1,2} ⊆ X) = (8−√3)/432 vs. (8+√3)/432 — confirmed to twelve digits. Periodic lifting amplifies the pairwise-indistinguishable pair to total-variation distance → 1.

### 5.2 Holonomy: an exact total-variation formula (the sharpest single theorem)

On the g-cycle, take the magnetic kernel K_φ = aI + rH_φ (forward edge phase e^{iφ}, 0 < 2r < min(a, 1−a)). Verified exactly for g = 3, 4, 5:

- every principal minor of order < g is independent of φ (forests are gauge-trivial);
- det K_φ − det K_ψ = 2(−1)^{g−1} r^g (cos gφ − cos gψ);
- **d_TV(P_φ, P_ψ) = (2r)^g |cos gφ − cos gψ|**, an exact closed-form law distance (we computed all 2^g atoms by inclusion–exclusion; agreement 10⁻¹⁶).

The connected stationary version (adding a small circulant term and M translated g-cycles) keeps all correlations of order < g exactly equal while d_TV → 1. **Assessment:** this is the cleanest counterexample we know to any hope of learning or identifying a determinantal law from bounded-order correlations, with the entire information loss computed in closed form; it is directly relevant to the DPP-learning literature (cf. Urschel–Brunel–Moitra–Rigollet) and, as a diagnostic for zeta methodology, it is the exact finite statement of "fixed correlation order misses a global phase." A companion fact with the same moral: the complete DPP law sees only cos(gφ) — orientation (the sign of the holonomy) is invisible to *all* sampling statistics and needs an ordered operator word. Publishable as it stands.

### 5.3 The quasi-free axiom gap

Same state space (L-subsets of ℤ/M), two model classes. Unrestricted rotation-invariant laws: the order-r inclusion deck has invariant fiber dimension exactly n(M, L) − n(M, r), where n(·,·) counts binary necklaces (Gottlieb's incidence rank + cyclic averaging; we verified five (M, L, r) cases by direct rank computation). At half filling the worst-case identification threshold is exactly r\* = N, and even the order-(N−1) deck leaves a fiber of dimension ~ 4^N/(2√π N^{5/2}) — exponentially large. Inside the stationary rank-N projection-DPP class, by contrast, the single row E|p₁|² = 1 identifies discrete CUE (§5.1). **The pair between these two statements is the theorem:** the determinantal/Wick axiom is an information-compression law worth an exponential factor. "The zeros have CUE pair statistics" and "the zeros are determinantal" differ by exactly this gap; conflating observation with constitution is the most common informal error in the field, and this makes it quantitative. A supplementary no-go (correct, and important for our own earlier work): a large fiber dimension does *not* imply a visible gap in any fixed local observable — matching decks through growing order forces all fixed cylinder statistics to converge, so fiber mass can hide entirely in observables whose support grows with N.

### 5.4 Marked homometry: complete diffraction misses the generator

The verified witness: u = (0,0,0,0,0,2,0,0,0,0,2,2) and v = (0,0,0,0,1,1,0,0,0,0,1,3) on ℤ/12 have identical cyclic autocorrelation (12,4,0,0,0,4,8,4,0,0,0,4) — hence identical complete squared Fourier data, with no extinctions — yet u has *no* simple site and v has three; cubic moments (24 vs. 30) separate them at third order. Lifted through a Fibonacci cut-and-project scheme, this yields period-free weighted model sets with equal complete pure-point diffraction and simple-particle fractions 0 and ½. The sharp threshold is also right: with all marks ≤ 2, mass plus complete autocorrelation *does* determine the simple-site count; mark 3 is the first escape, and v uses it. **Assessment:** the cleanest possible finite demonstration that a diffraction-only (power-spectrum-only) version of Dyson's quasicrystal program cannot recover local multiplicity structure — phase or a higher-order/bispectral observable is mandatory. The lift to genuine aperiodic model sets is what elevates it above a toy.

### 5.5 Prime labels and the Wilson fourth moment

On the free d-dimensional box with labelled unitary edge phases: one-edge windows are phase-blind; the fourth trace satisfies (verified on three box sizes to 10⁻⁸)

  tr A⁴_flat − tr A⁴ = 16 ∑_faces w_f sin²(φ_f/2),

so within the fixed pair-window fiber the fourth trace is maximized exactly on the gauge-flat orbit; orientation needs an ordered word; and the generated C\*-algebra is the full matrix algebra — Morita-trivial, K-theory ℤ — so *everything* of arithmetic interest (labels, holonomy, filtration) lives in the distinguished subalgebra structure, not in the abstract algebra. Together with the parity-interaction construction (every proper prime-marginal exactly product, global law not product, with d_TV computed), this packages the precise senses in which "Euler product" is labelled gluing data invisible to scalar spectra. As mathematics this is elementary-but-sharp; as a diagnostic for noncommutative-geometry approaches to RH it is well aimed: it says which structures a Connes-style finite-section model must *retain* to be nonvacuous.

---

## 6. The one central open problem, and its exact perimeter

Everything above funnels into a single finite question, which the series has surrounded with verified no-go theorems without solving:

> **Open Problem (all-size Nyquist equality law).** For every N, does there exist a probability law on the hard-core face E_N = {m ∈ {0,1,2}^{ℤ/2N} : ∑m = N, m_x m_{x+1} = 0} with E|p_k|² = k for all 1 ≤ k < N?

A positive answer makes the ½ + 2/π² certificate sharp at every size and — via the transfer principle for finite mimickers — would produce a multiplicity-carrying point process matching the full open finite CUE ramp, the strongest finite counterpart yet of Alternative-Hypothesis mimicry with collisions. A negative answer requires an explicit separating facet of the correlation polytope, which would itself be a new kind of obstruction.

The verified perimeter: (i) |E_N| = C(2N,N) via the run-pairing bijection — configurations are plentiful; the problem is barycentric, not combinatorial (verified N ≤ 4). (ii) The edge-charge recoding q_x = m_x + m_{x+1} − 1 turns E_N into the balanced three-tile cyclic language {(−1), (0,0), (+1,+1)} (verified), with target spectrum E|q̂(k)|² = 4k·cos²(πk/2N) — realizable by a free-fermion filter *outside* the language. (iii) Exact no-gos (all verified where finite): among half-grid projection-DPP atoms only the two alternating words lift; at N = 3 the liftable charge spectra are exactly {(0,0), (3,9), (9,3)} while the positive-probability source atom 111000 filters to (12,0), outside their hull, killing atomwise repair; and every repair field h must satisfy the destructive cross-spectrum identity 2Re E[η̂(k)h̄̂(k)] = −E|ĥ(k)|² mode by mode — independent decorations are impossible. (iv) The repair theorem (§4.2) lowers the bar to o(N⁻²) feature error. The surviving constructive proposal — a Pfaffian/hard-rod source with a correlated doublon field tuned to the destructive cross-spectrum — is a program, not a theorem, and the series says so.

We regard this as a well-posed, genuinely open, and attackable problem in finite point-process moment theory, of independent interest even with every zeta motivation stripped away.

---

## 7. What all this means for RH, the AH, and the ACUE — with corrections

### 7.1 The honest ledger

None of the verified theorems proves anything about zeta zeros, and the series never claims otherwise — indeed its most valuable habit is aggressive typing of claims. The genuine relations are these:

- **To the two-thirds theorem:** the Galerkin ladder (§2.2) gives the constant an exact finite meaning and a formal-verification target; the negative-square budget (§2.3) is its sharpest structural corollary; and the Gabor/Pick "common-signature" analysis locates the two missing bridges for any operator-theoretic strengthening — *observability* (a compressed observation can hide a negative square, quantitatively: |λ₋| = O(a²) for an off-line pair at distance a) and *cross-cutoff coherence* (self-moments at two cutoffs do not control mixed traces; the determinant-tail counterfeit, verified, refutes trace-to-determinant inference exactly).
- **To the Alternative Hypothesis / ACUE / Lagarias–Rodgers:** the Nyquist theorem is the exact finite mechanism by which multiplicity hides at the band edge; the quasi-free gap quantifies how far pair data are from a law; and the local-blindness theorem corrects the naive inference from fiber dimension to observable gaps. The Lagarias–Rodgers band-limited mimicry remains the decisive obstruction at the process level; the finite theorems are its exact, checkable shadows and sharpen where a counter-construction must operate (order ≥ 4 data, growing support, or the Nyquist channel).
- **To Dyson's quasicrystal idea:** diffraction-only is now provably insufficient in the strongest finite sense (marked homometry with no extinctions, aperiodic lift); any viable version must carry phase (bispectrum) or Euler-labelled sign data, and the rational-rank obstruction forces infinite-dimensionality on any Lee–Yang-type realization of the prime spectrum.
- **To Connes-type programs:** the UV/IR separation ([A23] §5) — the two-thirds proof is a *moving high-frequency* probe of the same Weil form of which CCM's construction is a *fixed-cutoff spectral-edge* problem — is an interpretation, not a theorem, but the finite Pontryagin extension lemma (verified) and the pollution/counterfeit battery give it teeth: they specify exactly which convergence statements are missing and what would falsify proposed bridges.

### 7.2 A correction to our own earlier synthesis

An earlier synthesis by the present authors asserted that 0.6725007… "is the exact optimal value of a bandwidth-one LP" and that the Alternative Hypothesis adversary "is strictly suboptimal by 0.0301," citing the proximity of ½ + 2/π² − δ_MT. The present series shows this framing conflates three feasible sets that must be kept apart ([A23] §3.7): the Montgomery–Taylor profile space (where δ_MT is sharp *for that certificate class*), the marked open-Nyquist model (where ½ + 2/π² lives, as a lower certificate for a different statistic), and the literal ACUE balanced-moment fiber (on which every state is binary and the simple fraction is identically 1, so the "LP value" is trivially degenerate there). Whether δ_MT is optimal over *all* bandwidth-one configurationwise certificates is open: the known ceiling for that broader class is ≈ 0.68183 (itself carrying an unresolved verification boundary — §7.3), leaving a genuine gap. We consider the retraction itself informative: it is a live demonstration that the series' typing discipline catches real errors made by competent readers.

### 7.3 A verification boundary that should be closed

The PairCeiling component of the public Lean artifact reportedly kernel-checks its stability statement downstream of a hypothesis whose exact-rational witness is named by hash but absent from the public repository. Until that witness is published and replayed, the correct citation form is "a conditional stability ceiling of ≈ 0.6818287," not "the exact optimum of the bandwidth-one problem." This is a reproducibility observation, not a mathematical doubt; but in a field newly proud of formal verification, the distinction between kernel-checked-given-inputs and independently-replayable deserves exactly the care the series gives it.

### 7.4 The information ladder

The durable conceptual product, supported at every rung by a verified finite witness, is a strict hierarchy:

  pair ramp < wider Fourier support or new arithmetic positivity < full correlation hierarchy < point-process law < spectral determinant,

with independent side-axes (phase, orientation, labels, constitution, realizability) that no amount of climbing substitutes for. The two-thirds theorem is remarkable precisely because it extracts a strong zero-count from the *lowest* rung by exploiting indefinite-form geometry and integrality; the verified counterexamples explain why silent promotion up the ladder is impossible; and the open problems (§6, plus growing arithmetic support beyond the unit band) say exactly what a further advance must purchase.

---

## 8. Ranked assessment of novelty

Our referee's ranking of the verified contributions, by mathematical value:

1. **The Nyquist conservation-law package** (§3): exact, sharp, multi-faced, with a well-posed open endpoint problem. Publishable in a good probability or analysis journal on its own.
2. **The magnetic-holonomy TV formula and connected fixed-order mimicry** (§5.2): the sharpest known non-identifiability statement for DPPs; immediately relevant to the learning literature.
3. **The fourth-moment covariance / inradius / repair mechanism** (§4): a new exact computation with a genuinely useful reduction of the open problem.
4. **The quasi-free axiom gap with the necklace fiber formula and local-blindness theorem** (§5.3): the cleanest quantification of "observation ≠ constitution."
5. **The Galerkin closed form** (§2.2) and the **marked homometric aperiodic pair** (§5.4): smaller, but exact and well aimed.
6. The signature dictionary, budget corollary, Pontryagin extension, and counterfeit battery (§2.3, §7.1): mostly interpretation and regression tests — but of a kind this subject conspicuously lacked.

Everything in this ranking passed independent verification; the claims we could not verify are quarantined in §1.2 and §7.3. All-size attainment, the thermodynamic sine–Bragg limit, and every zeta-side bridge remain open, as the source papers themselves state.

---

## Appendix: reproducibility

The verification battery (`verify_codex.py`, plus the follow-up script with the three corrected tests) runs in under two minutes on commodity hardware: exact enumeration of determinantal laws through 2N = 12 sites, all-atom total-variation computations for magnetic cycles through g = 5, quadratic programs to n = 4000 cells, and per-sample identity checks over random marked configurations. Deviations quoted in §1.2 are worst-case over all tested instances. The three transcription corrections of §1.3 are the only places where our reading of the source PDFs required repair; in each case the papers' mathematics was correct as intended.

*Authors' note: the source manuscripts were produced by GPT5.6SOL-class agents under Codex orchestration; the verification and this synthesis were carried out independently in a separate session. Neither the sources nor this paper proves a new statement about the zeros of ζ(s); both aim to make the finite mathematics around the two-thirds theorem exact, checkable, and honestly typed.*
