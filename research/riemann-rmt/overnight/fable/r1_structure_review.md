# r1 — Adversarial review of the "new structures" (Fable cluster E, task C2)

**Scope.** `impostors_paper.md` §§2–3 and `handoff/HANDOFF_GPT6_ASTRA.md` §§3–4: (1) the operator unification, (2) the
marked-depth rank-two law, (3) the ACUE mimicker families, (4) the depth statistic and Theorems A/C. For each: is it
standard (name + where), standard-but-newly-connected, or new to my knowledge. Then one theorem-shaped statement,
with a test actually run.

**Status tags.** [P] proved here (argument written out), [C] computed (script + data in this directory),
[R] refuted or repaired, [O] open with the obstruction stated. Every literature attribution below is
**(recalled; not verified online)** unless marked otherwise; §9 lists what to search for.

**Scripts** (all in `overnight/fable/scripts/`, logs in `overnight/fable/data/`):
`r1_structure_check.py` (identities A–I; 7 s), `r1_fibre_depth_separation.py` (fibre/depth test, N = 5..8; 3 min),
`r1_det_tilt_laws.py` (determinant-tilt family vs the depth law). Legacy reproduction: `data/r1_legacy_reproduction.log`.

---

## 0. Verdicts at a glance

| # | claimed structure | verdict | tag |
|---|---|---|---|
| 1a | Σ_δ δ(N−δ)e^{−2πikδ/N} = −N/(2sin²(πk/N)); 𝓛_N e_δ = δ(N−δ)e_δ | standard (finite Fourier transform of a quadratic on ℤ_N; Fejér-kernel identity) | [P] verified |
| 1b | 𝓛_N = Jacobian of the Coulomb flow at the clock | standard, and **tautological**: the flow is diagonal on coefficients a_j with rate j(N−j), and a_j is the j-th Fourier mode of the clock displacement (two-line proof, §1.2) | [P] here |
| 1c | N^{−1}𝓛_N → (−Δ)^{1/2} | standard (linearised Dyson Brownian motion / Hilbert-transform structure); sharpened to the **exact** identity 𝓛_N = N(−Δ)^{1/2} + Δ on band-limited functions | [P] here |
| 1d | "invisibility degree = relaxation rate" mechanism (§2.3) | **not established**: the two occurrences of δ(N−δ) live on different spaces (a density deviation on configuration space vs a tangent vector at the clock); no intertwining map is given or found. The static side (opening degree = δ(N−δ)) is verified; the dynamic side is the SU(N) Casimir of ∧^δ (§1.3) — a representation-theoretic coincidence, not a mechanism | [O] |
| 2a | marked-depth law Dτ[uu*] = (κδ/4)u*K_ab u + (δ²/8)κ′ | first term: textbook first-order perturbation of an eigenvalue gap under a rank-one update (Hellmann–Feynman + Cayley chain rule); second term: **the product rule** applied to the identity τ ≡ (8τ/δ²)·δ²/8. The 11-digit "confirmation" holds for any φ in place of δ²/8 (verified with φ = δ³ and φ = 1) | [R] |
| 2b | sign convention c_j = −2/(1+λ_j²) | wrong sign (dθ/dλ = +2/(1+λ²), as the Astra audit says), cancelled by the a/b labelling in the code; formula correct iff δ := θ_b − θ_a with b counter-clockwise of a | [R] |
| 2c | "polarisation not overlap", null cone, rank-two tomography | direct consequences of 2a's first term; correct but standard | [P] trivial |
| 2d | marked depth as a detector for ACUE-fibre elements | **ill-posed as stated**: fibre elements are measures on spectra; with the canonical conjugation-invariant lift, the marked depth reduces to statistics of ∇τ (first Haar moment ≡ 0, second = ‖∇τ‖²/(N(N+1))) | [P] here |
| 3 | centre-of-mass, det-character/secant, parity families | one family: **tilts by functions of det(U_C)**, q = μ·G(det U_C). CUE analogue is trivial (det carries only the global rotation); on the lattice the rotation is quantised and det² becomes a shape invariant. Elementary; not known to me in the literature | [P] here; novelty (iii) conservative |
| 4a | depth statistic, Coulomb ODE, two-body constant δ²/8 | standard (finite de Bruijn–Newman / Lehmer-pair collision time; Pólya–de Bruijn–Csordas–Smith–Varga; Tao's circle heat flow) | (i) |
| 4b | Theorem A (adjacent gap closes no faster than two-body) | correct; circle version of the elementary convexity fact used in the real-rooted setting. Consequence: **the depth threshold N²(−Λ) < π²/8 is implied by, and implies nothing beyond, the direct hard-core statement δ_min < π/N**; the claimed tractability advantage is unsupported | [P]/[R] |
| 4c | Theorem C(i) | trivial corollary of A + pigeonhole | [P] |
| 4d | Theorem C(ii) | reduced to Ben Arous–Bourgade (recalled) + an unproved background bound; as the handoff already records | [O] |
| 4e | "the depth is smooth in the configuration" (§1.5) | false on a positive-mass set: τ is a min over pairs and has kinks where the first collision is tied — 3, 4, 6 orbits at N = 5, 6, 7, all mirror-symmetric | [R] |

**Constructive result (§5).** *Theorem E1 (chiral blindness, [P]+[C]):* for N ≥ 5 and 2 ≤ k ≤ N−2 the closed-form
measures q_{k,ε} = μ_ACUE·(1 + ε·Im det(U_C)^{2k}), |ε| < 1, lie in the CUE-moment fibre, are at total variation
0.22–0.30 from ACUE (ε = 0.9), and give **exactly** the same law to every dihedral-invariant statistic — the depth,
its atom, every Haar-lifted even marked-depth moment, all pattern counts. The chiral tangent space of the fibre has
dimension 1, 3, 39, 186 at N = 5, 6, 7, 8. On the reflection-symmetric sub-fibre the (unmarked) depth law is already
injective at N ≤ 8 (E2), so the marked depth adds nothing there. The candidate conjecture of the brief is therefore
refuted as posed; the corrected formulation and its open general-N part are in §5.4.

---

## 1. Operator unification

### 1.1 What is standard [P, verified in `r1_structure_check.py` A–D]

Numerics (all N = 4..24 unless stated): Fourier identity, max deviation 8.5·10⁻¹² (exact in sympy at N = 6, 8);
𝓛_N e_δ = δ(N−δ)e_δ, 2.0·10⁻¹²; ‖𝓛_N − Jacobian‖_max = 2.4·10⁻¹³; (1/4π)∫(1−cos ky)csc²(y/2)dy = |k| to 30 digits.

*Names.* (a) The Fourier identity is the finite Fourier transform of the quadratic δ(N−δ) on ℤ_N — equivalently the
Fejér-kernel identity Σ_{|n|<k}(k−|n|)e^{iny} = (1−cos ky)/(2sin²(y/2)) sampled on ℤ_N; its k-sum gives the classical
Σ_{k=1}^{N−1} csc²(πk/N) = (N²−1)/3. (b) The circulant 𝓛_N with kernel 1/(2sin²) is the Hessian (times 2) of the
circular log-gas energy Σ_{j<k} log|2sin((θ_j−θ_k)/2)| at its minimiser, the equally spaced (Fekete) configuration;
that its eigenvalues are ∝ k(N−k) is the harmonic ("phonon") spectrum of the classical trigonometric
Calogero–Sutherland lattice — Sutherland 1971–72; Calogero–Perelomov, Commun. Math. Phys. 59 (1978), which is
precisely about matrices with entries 1/sin²(x_j − x_k) at the equilibrium configuration (recalled; not verified
online). The same numbers are the one-magnon dispersion of the Haldane–Shastry chain (Haldane 1988, Shastry 1988,
recalled): 𝓛_N *is* the Haldane–Shastry Hamiltonian restricted to the one-magnon sector, which is more than "sharing
a kernel". (c) The continuum limit: the linearisation of Dyson Brownian motion about equilibrium is the fractional
heat equation of order 1, ∂_t f = −(−Δ)^{1/2}f (the "Hilbert-transform structure" in the homogenisation of DBM:
Bourgade–Erdős–Yau–Yin 2016, Landon–Sosoe–Yau 2019; recalled).

### 1.2 Two additions proved here [P]

**(α) Exact band-limited identity.** Since δ(N−δ) = N|δ| − δ² for the representative |δ| ≤ N/2,
> 𝓛_N = N(−Δ)^{1/2} + Δ on trigonometric polynomials of degree ≤ N/2 sampled on ℤ_N.

So "N^{−1}𝓛_N → (−Δ)^{1/2}" is exact up to the aliasing-free correction Δ/N (check B, 6.4·10⁻¹³). The Nyquist
mode is where the two terms are comparable: N²/4 = N·(N/2) − (N/2)².

**(β) The Jacobian identity is a change of variables.** Let e_j be the elementary symmetric function of the roots
z_m = e^{iθ_m}. At the clock z_m = ω^m, ∏_{k≠m}(1+tz_k) = (1−(−t)^N)/(1+tz_m), so e_{j−1}(clock ∖ z_m) = (−z_m)^{j−1}
and
> ∂e_j/∂θ_m |_clock = i z_m e_{j−1}(clock ∖ z_m) = i(−1)^{j−1} ω^{mj}   (check C, 6.8·10⁻¹⁰ by central differences).

Hence δe_j = i(−1)^{j−1} Σ_m ω^{mj} ε_m: the j-th coefficient perturbation *is* the j-th Fourier mode of the
displacement ε. The flow is diagonal on coefficients with rate j(N−j) by definition (P_s = Σ a_j e^{s j(N−j)} z^j), so
mode j of ε grows at rate j(N−j). This is the whole content of "𝓛_N = Jacobian"; the csc² computation re-derives it.

### 1.3 The dynamic δ(N−δ) is the SU(N) Casimir: the finite depth flow is the backward SU(N) heat flow [P]

For the fundamental weight ω_j of SU(N), ⟨ω_j, ω_j + 2ρ⟩ = j(N−j)/N + j(N−j) = j(N−j)(N+1)/N (check E, 1.8·10⁻¹⁵,
N = 3..9). Since e_j(U) = χ_{∧^j}(U) is a character and characters are Laplace eigenfunctions on a compact group,
e^{tΔ}e_j = e^{−tC₂(ω_j)}e_j, and therefore
> P_s(z; U) = Σ_j a_j e^{s j(N−j)} z^j  =  (e^{tΔ_{SU(N)}} det(1 − z·))(U)   with  t = −sN/(N+1).

The depth direction s > 0 is the backward heat flow on SU(N) applied to the class function U ↦ det(1−zU); the
forward flow is E_B[det(1 − zUB_t)] with B_t Brownian motion on SU(N). (On U(N) the Casimir of ∧^j is j(N−j+1); the
extra U(1) term e^{−tj²/N} is a radial dilation z ↦ ze^{−t} and destroys self-inversiveness, so SU(N) is the right
group.) This upgrades the paper's "up to convention, the quadratic Casimir" to an exact statement, and it is the
honest representation-theoretic home of the number on the dynamic side. Classification: (ii) standard facts, newly
connected; I do not know this identification in the literature (search terms in §9).

### 1.4 The "mechanism" of §2.3 [O], and the static side [C]

Static side, verified: the first degree d at which some balanced observable p_λ p̄_ν (|λ| = |ν| = d, parts ≤ N, and also
parts ≤ 2N−1) has E_ACUE[z(C)^δ p_λ p̄_ν] ≠ 0 is exactly δ(N−δ): (δ, d) = (1,4), (2,6) at N = 5 and (1,5), (2,8), (3,9)
at N = 6 (check F). This is a **lattice aliasing cost**: on ℤ_{2N} momenta wrap, and moving the Fermi sea by 2δ with
balanced hops costs δ(N−δ) (e.g. N = 6, δ = 1: 7→0 by +5 and 6→1 by −5). It has nothing to do with the group
Laplacian. The dynamic side's δ(N−δ) is the Casimir of ∧^δ (§1.3), i.e. the rate at which the coefficient e_δ — a
*function on U(N)* — relaxes. The paper's sentence "an impostor invisible to degree ≤ d is one whose deviation is
supported on the modes that relax fastest" identifies a Fourier mode of a *density on configuration space*
(z(C)^δ μ) with a Fourier mode of a *tangent vector at the clock* (ε_m ∝ ω^{mδ}). No map between these spaces is
given; I could not construct one (Failed attempts, §7.1). What survives: both numbers equal |rectangle δ×(N−δ)| =
⟨2ρ, ω_δ⟩; the coincidence is representation-theoretic bookkeeping, not a theorem about detection. Verdict: [O].

---

## 2. The marked-depth rank-two law

### 2.1 Standard content
Rank-one update G → G + ηuu*: dλ_j/dη = |⟨u,v_j⟩|² (Hellmann–Feynman / Weyl interlacing, textbook); Cayley
dθ/dλ = +2/(1+λ²) (check G, 7.3·10⁻¹²; the paper prints −2/(1+λ²), the Astra audit is right). The first-order
response of a gap is therefore a difference of two weighted overlaps — a rank-≤2 quadratic form. The "null cone",
"polarisation not overlap", and the rank-two tomography are restatements of this one formula.

### 2.2 The decomposition is the product rule [R]
κ := 8τ/δ² is a definition, so τ ≡ κ·δ²/8 and Dτ = (κδ/4)δ′ + (δ²/8)κ′ *identically*. In `r1_structure_check.py` G
the same finite-difference "confirmation" (max error 2.9·10⁻¹¹) is obtained with φ = δ³ (3.5·10⁻¹¹) and with φ ≡ 1
(0): the 11-digit agreement measures the consistency of central differences, not physics. The reproduced legacy
run (`data/r1_legacy_reproduction.log`) gives the paper's numbers exactly (correlation 1.00000000, slope 1.00000,
residual 5.66·10⁻¹¹; local term alone 0.99581978 / 1.347 / 8.1·10⁻²; top-2 energy 0.9862; principal angles
2.26·10⁻⁶, 2.96·10⁻⁶ deg) — so the computations are right; only their interpretation is circular.

**Honest content [C].** How much of τ′ the constant-κ local term carries: over 4 random configurations × 6 random
marks, median L/τ′ = 0.915 (10–90 %: 0.33–1.00) at N = 6 and 0.9975 (0.973–1.000) at N = 8. Background
renormalisation is small and shrinks with N — as Theorem B (κ − 1 = O(N²δ²)) already predicts. That is the one
non-tautological statement in §3 of the paper, and it is a numerical observation at two sizes.

### 2.3 The isospectral-pair experiment [R]
G₁ = Q₁DQ₁ᵀ, G₂ = Q₂DQ₂ᵀ are conjugate matrices; χ(·;u) with a *fixed* u is not a class function, so of course it
takes different values on them (median |Δχ| = 0.081). As *ensembles* — the only meaning "impostor" has in this
programme — two conjugation-invariant laws with the same spectral law are identical, and nothing separates them.

### 2.4 On spectral measures the marked depth is the depth gradient [P]
Fibre elements are measures on configurations; to evaluate a marked depth one must lift to matrices. With the
canonical lift (eigenvectors Haar, independent of the spectrum) and the rotation-covariant marking
U ↦ U e^{iηuu*} (the Cayley marking is not rotation-covariant: its first Haar moment is −(1/N)Σ_j cosθ_j ∂_jτ, which
depends on the rotation representative and averages to 0 over the 2N lattice rotations):
> χ̃(U;u) = Σ_j (∂τ/∂θ_j)|⟨u,v_j⟩|²   (check H, 3.7·10⁻¹¹ over 300 Haar marks), so given the configuration χ̃ has the law
> of ⟨∇τ, q⟩ with q ∼ Dirichlet(1,…,1). Hence E[χ̃|θ] = (1/N)Σ_j∂_jτ = 0 exactly (rotation invariance; check H,
> 1.5·10⁻¹¹), E[χ̃²|θ] = ‖∇τ‖²/(N(N+1)) (MC 4.81·10⁻⁵ vs 5.11·10⁻⁵, n = 300), and the m-th moment is a symmetric
> polynomial of degree m in the components of ∇τ.

So on spectral data the "polarisation detector" is the vector ∇τ. Its even functionals (‖∇τ‖², …) are reflection-even;
its odd ones (Σ_j(∂_jτ)³, …) are reflection-odd — this matters in §5.

---

## 3. The mimicker families are one family: determinant tilts [P]

Write X(C) = Σ_{c∈C} c. Then det(U_C) = ∏ζ^c = e^{iπX/N}, so a function of X mod 2N is a function of det U_C; a
function of X mod N is a function of det²; (−1)^X = det^N. Slot rotation adds N to X, so det² (and every even power)
is rotation-invariant on the lattice while odd powers flip sign.
- **Centre-of-mass family** q = μ·g(X mod N) = μ·G(det²). Every g ≥ 0 on ℤ_N with mean 1 is |P_a(z)|² for some a
  (take P̂_a = √g·e^{iφ} and invert the DFT), so the "secant / two-Fermi-sea" family with even shifts is the same
  family, and "the code object is the autocorrelation spectrum" is the statement that the Fourier coefficients of G
  are what matter. The constraint ĝ(±1) = 0 is "det² has visibility degree 1·(N−1) ≤ N".
- **Parity sectors** q^± = μ(1 ± (−1)^X) = μ(1 ± det^N): the k = N/2 member (even N), with visibility (N/2)² = N²/4.
- **Odd powers** det^{2k+1}: not rotation-invariant, hence orthogonal to *every* rotation-invariant observable of
  every degree — they are in the fibre trivially, exactly as in CUE.
- **CUE analogue.** Under Haar, det U = e^{i(Σθ̄ + Nα)} where α is the global rotation, which is uniform and
  independent of the shape; tilting by G(det U) leaves the law of every rotation-invariant observable unchanged.
  The families exist on the lattice only because the rotation is quantised to 2N values and det² becomes a shape
  invariant. That is the whole "mechanism" behind the transport-cost/hop-budget explanation in the handoff.
- **Membership rule** [C, `r1_det_tilt_laws.py`]: μ·Re det^{2k} and μ·Im det^{2k} are fibre directions iff k(N−k) > N,
  i.e. 2 ≤ k ≤ N−2 — confirmed for all k at N = 5..8 (residual ≤ 4·10⁻¹⁶ when in, ≥ 10⁻² when out). At N = 6 the
  three com-family dimensions reported by the peer audit (and by `mimicker_fibre.py`, reproduced: null dims 2,3,4,5 at
  N = 5..8) are exactly cos, sin of det⁴ and cos of det⁶.

Classification: elementary; (iii) new to my knowledge as a *family* (Tao's ACUE paper and Lagarias–Rodgers'
band-limited mimicry construct lattice-shift mimickers; I do not recall determinant tilts; recalled, not verified).
The det-tilt family is a proper subfamily: the fibre has 10, 80, 403 dims at N = 6, 7, 8 versus 3, 4, 5 det-tilt dims.

---

## 4. The depth statistic, Theorem A, Theorem C

### 4.1 Standard
The backward heat deformation of a polynomial and the finite "Λ" of a real-rooted polynomial (first collision time)
are the objects of Pólya (1926), de Bruijn (1950) and Csordas–Smith–Varga (Constr. Approx. 1994, "Lehmer pairs of
zeros, the de Bruijn–Newman constant Λ, and the Riemann hypothesis"), where a close pair of zeros of Ξ bounds Λ from
below via exactly the two-body collision time — the δ²/8-type constant is theirs. The Coulomb ODE for the zeros
under the heat flow is in Csordas–Smith–Varga and in Rodgers–Tao (2018) §2; the circle version with weights
e^{tj(N−j)} and θ̇_j = −Σcot((θ_j−θ_k)/2) is Tao's blog post "Heat flow and zeroes of polynomials II: zeroes on a
circle" (7 June 2018; existence, title and date **verified by one web search**, text not fetched — see §9). The operator N·D − D², D = z d/dz, is forced by "second order +
preserves self-inversive polynomials". The CUE exponent −8/3 = −2·(4/3) is the Ben Arous–Bourgade smallest-gap
exponent composed with the two-body law; nothing about it is new beyond the composition. All (i).

### 4.2 Theorem A: correct, and what it really says [P]/[R]
The proof is right: for an adjacent pair, each third body enters g′ with the sign of cot(x_b/2) − cot(x_a/2) > 0, so
g′ ≥ −2cot(g/2) and −Λ ≥ −log cos(δ_min/2) ≥ δ_min²/8. On the line the same convexity (2/(x_a−x_k) − 2/(x_b−x_k) > 0
for x_k outside [x_a, x_b]) is the standard observation; (ii) newly stated on the circle.

**Consequence the paper does not draw.** Under (hard-core) AH every gap is ≥ π/N, and Theorem A gives
N²(−Λ) ≥ π²/8. Contrapositively, N²(−Λ) < π²/8 ⇒ δ_min < π/N. So *the depth falsification threshold is a strictly
stronger hypothesis than the direct gap statement it is supposed to make tractable*: to get the depth below π²/8 one
must first exhibit a gap below half the mean spacing. The reverse implication (gap ⇒ depth) needs Theorem B's
background bound and fails on the lattice (ρ_∞ ≥ 1.05). Hence "the depth is the Lagarias–Rodgers hard core in
another coordinate" is true only in the direction in which it is useless, and the claimed advantage ("Palm-type
certificates apply to smooth functionals") is unsupported: any certificate that bounds the depth bounds δ_min
directly through Theorem A. [R] for the tractability claim; the theorem itself stands. (The Astra audit's point that
this uses the strong LR2019 form of AH — no zero gaps, hard core exactly 1/2 — applies verbatim.)

### 4.3 Theorem C
(i) is A + pigeonhole; N²(−Λ) ≥ 1.31 > 1.2337 in all data. (ii) rests on P(N^{4/3}δ_min > x) → exp(−x³/72π)
(Ben Arous–Bourgade 2013 for CUE, Feng–Wei for CβE; recalled) plus the background bound S ≤ AN² w.h.p., which is
open; the handoff already marks it [R]. Note also (Astra) that E_ACUE[−Λ] = +∞ at every N because of the clock atom,
so all "laws" must be read as (atom, conditional law).

### 4.4 τ is not smooth [R for §1.5 "the depth is smooth in the configuration"]
τ = min over pairs of a collision time; where the first collision is tied it has a kink. Central differences with
one-sided-difference disagreement detect kinks on 3, 4, 6 non-clock orbits at N = 5, 6, 7 — all of them
mirror-symmetric configurations (where the two mirror pairs collide simultaneously). The transversality Criterion I
(handoff §4.9) is evaluated at non-symmetric configurations and is unaffected; but "smooth" and "gradient" need the
qualifier "away from tied first collisions", a set of positive ACUE mass.

---

## 5. Constructive part: what these structures do support tonight

### 5.1 Theorem E1 (chiral blindness) [P] with dimension counts [C]
Let F_N be the fibre of measures on N-subsets of ℤ_{2N} matching all balanced moments E[p_λ p̄_ν], |λ| = |ν| ≤ N,
of ACUE; R the reflection C ↦ −C; μ = μ_ACUE (R-invariant, strictly positive on every configuration).

**(a)** For N ≥ 5, 2 ≤ k ≤ N−2 and |ε| < 1, q_{k,ε} := μ·(1 + ε·Im det(U_C)^{2k}) is a probability measure in F_N.
*Proof.* Im det^{2k} = sin(2πkX/N) has modulus ≤ 1, so q ≥ 0; it is R-odd and μ is R-even, so Σ_C μ·Im det^{2k} = 0
and q sums to 1; E_μ[det^{2k}·p_λ p̄_ν] = 0 for |λ| = |ν| ≤ N because the sector pairing opens only at degree
k(N−k) > N (handoff §3.4 [P]; verified here at N = 5, 6 for all balanced observables of degree < k(N−k), and the
fibre membership verified directly at N = 5..8, residual ≤ 4·10⁻¹⁶). ∎

**(b)** Let S be any statistic of the configuration with S∘R = S (and S rotation-invariant, so that it is a function
on orbits): the depth −Λ, the pair (clock atom, law of N²(−Λ)), ‖∇τ‖² and every even Haar moment of every marked
depth, every window pattern count, |E p_λ p̄_ν| of every degree. Then S has the same law under q_{k,ε} as under μ, and
more generally under μ(1+εh) for every R-odd fibre direction h. *Proof.* For any Borel B, the set {S ∈ B} is
R-invariant, and Σ_{C: S(C)∈B} μ(C)h(C) = 0 since μh is R-odd. ∎

**(c)** [C] The fibre tangent space splits R-evenly/oddly as 1+1, 7+3, 41+39, 217+186 at N = 5, 6, 7, 8 (the N = 7 split
matches the handoff's "39/80"); the det-type directions Im det^{2k} account for 1, 1, 2, 2 of the chiral dimensions.
Numerics: for q_{k,0.9}, TV(q, μ) = 0.291, 0.300, 0.289, 0.225–0.272, while the TV between the laws of N²(−Λ)
(atom + values) is ≤ 1.3·10⁻¹⁵ and the clock atom and E[N²(−Λ)|non-clock] agree to all printed digits
(`r1_det_tilt_laws.py`); a random μ-weighted chiral direction gives the same (`r1_fibre_depth_separation.py` §2).
For contrast the R-even tilts μ(1 + 0.9 Re det^{2k}) move the depth law by TV 0.22–0.60 and double the clock atom —
the paper's Class I claim for the com/secant families is confirmed, but only for their even half.

### 5.2 E2: on the symmetric sub-fibre the unmarked depth law is already complete [C]
τ takes pairwise distinct values on the 15, 49, 132, 439 reflection classes of non-clock orbits (no coincidence to
10⁻⁹; minimal separations 7.6·10⁻⁵, 2.6·10⁻⁶, 8.6·10⁻⁷, 2.0·10⁻⁷ in N²τ units against solver accuracy ~10⁻¹²). Hence
the map q ↦ (clock atom, law of τ) is injective on the symmetric part of the fibre: rank 1/1, 7/7, 41/41, 217/217.
But this is generic, not a compression: the atom plus m power moments of τ see exactly m+1 dimensions at every N
(one per moment, checked up to 30 moments in a bounded Chebyshev basis), so d_sym functionals are needed — the depth
moments behave like arbitrary functionals of the configuration. Adding ‖∇τ‖² (the second Haar moment of the marked
depth) adds nothing (rank unchanged). [Conjecture E2′, open: τ is injective on reflection classes for all N. No
mechanism; expected generically; a proof would need an argument that two non-mirror lattice configurations cannot
share a first-collision time, which I do not have.]

### 5.3 E3: the odd Haar moment of the marked depth sees chiral impostors, as does any odd statistic of degree > N [C]
G₃ := Σ_j(∂_jτ)³ (∝ the third Haar moment of χ̃, set to 0 on kinked orbits, which are self-mirror and irrelevant) is
R-odd (|G₃∘R + G₃| ≤ 3·10⁻⁹) and detects one chiral direction: for the explicit chiral impostor,
E_q[G₃] − E_μ[G₃] = −3.0·10⁻³, +6.7·10⁻³, −6.7·10⁻⁵ at N = 5, 6, 7 while the τ-laws coincide to 10⁻¹⁷. For comparison
the odd (Im) balanced moments of degree N+1 see 1/1, 2/3, 21/39 chiral dimensions. So there is nothing special about
the marked depth here: any rotation-invariant, reflection-odd function outside the span of degree-≤N moments works.

### 5.4 Verdict on the candidate conjecture, and the corrected formulation
*"The marked-depth rank-two law (or the polarisation detector) separates ACUE from every other measure in the
CUE-moment-matching fibre at N = 6, 7."* — **[R], on three counts.** (1) Ill-posed: fibre elements are spectral
measures; the marked depth needs a lift, and with the canonical lift it is a function of ∇τ (§2.4). (2) Its even
part (and the unmarked depth, and every dihedral-invariant statistic) is blind to a 3- resp. 39-dimensional family
of honest impostors containing closed-form members at TV ≈ 0.3 from ACUE (E1). (3) On the symmetric part it is
redundant: the unmarked depth law is already injective (E2).

*Corrected statement (what is true and what remains).* "For N ≤ 8 the pair (clock atom, law of N²(−Λ)) is a
complete invariant of the reflection-symmetric fibre F_N^sym, and no dihedral-invariant statistic is an invariant of
F_N ∖ F_N^sym; F_N^sym has codimension 1, 3, 39, 186 in F_N." The open part is E2′ (all N) and, more importantly,
whether the chiral half is physically admissible: the handoff says the functional equation "kills the chiral half at
zero cost", but the functional equation relates heights +T and −T; it does **not** make the local limit of the
positive-ordinate zero process reversible (for n ≥ 3 the permutation symmetry of R_n gives R_3(a,b) = R_3(−b,−a), not
R_3(a,b) = R_3(−a,−b)). Reversibility of the local limit is an extra hypothesis [O]; without it the chiral impostors
are legitimate, and E1 says the whole depth programme cannot see them.

---

## 6. Commands and outputs

```
cd overnight/fable/scripts
python3 r1_structure_check.py            > ../data/r1_structure_check.log            # 7 s : 9 PASS, 0 FAIL
python3 r1_fibre_depth_separation.py 5 6 7 8 > ../data/r1_fibre_depth_separation.log # 3 min; writes ../data/r1_fibre_N{5,6,7,8}.npz
python3 r1_det_tilt_laws.py              > ../data/r1_det_tilt_laws.log
cd ../../../riemann-impostors/counterexamples && python3 mimicker_fibre.py; python3 ../verification/marked_depth_law.py; python3 ../verification/marked_depth.py   # -> data/r1_legacy_reproduction.log
```

Fibre / depth summary (`r1_fibre_depth_separation.log`):

| N | orbits (self-mirror) | fibre dim = sym + chiral | τ-levels on classes | min class separation | law rank on sym | kinked orbits (all self-mirror) | odd deg-(N+1) moments see |
|---|---|---|---|---|---|---|---|
| 5 | 26 (6) | 2 = 1 + 1 | 15/15 | 7.6e−5 | 1/1 | 3 | 1/1 |
| 6 | 80 (20) | 10 = 7 + 3 | 49/49 | 2.6e−6 | 7/7 | 4 | 2/3 |
| 7 | 246 (20) | 80 = 41 + 39 | 132/132 | 8.6e−7 | 41/41 | 6 | 21/39 |
| 8 | 810 (70) | 403 = 217 + 186 | 439/439 | 2.0e−7 | 217/217 | — | — |

Determinant tilts μ(1 + 0.9·{cos, sin}(2πkX/N)) (`r1_det_tilt_laws.log`): in fibre iff k(N−k) > N (all N = 5..8);
sin: TV(τ-laws) ≤ 1.3e−15, atom and conditional mean unchanged; cos: TV(τ-laws) = TV(q, μ) = 0.22–0.60, atom ×1.9–2.8.

Structure checks (`r1_structure_check.log`): A 8.5e−12 (sympy exact N = 6, 8); B 2.0e−12 / 2.4e−13 / 6.4e−13;
C 6.8e−10; D 0 (30 digits); E 1.8e−15; F opening degrees (1,4),(2,6) | (1,5),(2,8),(3,9); G Cayley 7.3e−12, gap′
1.3e−11, product rule 2.9e−11 / 3.5e−11 / 0, local share medians 0.915 (N=6), 0.9975 (N=8); H 1.5e−11, 3.7e−11,
Haar mean 7.6e−4 (n=300; exact 0), second moment 4.81e−5 vs 5.11e−5; I 2.8e−16.

---

## 7. Failed attempts

1. **An intertwiner for §2.3.** Tried to realise the sector pairing B_δ(f,g) = E_μ[z^δ f ḡ] as a matrix element of
   𝓛_N (or of the flow) on some space of functions of configurations: the flow moves lattice points off the lattice,
   so (Φ_s)_* of a fibre measure lives on a different support and the ℤ_N-Fourier label δ of z(C)^δ has no
   invariant meaning after time 0. No candidate map survived. The Casimir identification (§1.3) explains the
   dynamic number; the aliasing count explains the static one; they are not the same object.
2. **Rescuing the marked depth on spectral measures.** With the Cayley marking the first Haar moment is
   −(1/N)Σcosθ_j ∂_jτ — not rotation-invariant; averaging over the 2N lattice rotations kills it. With the covariant
   marking it vanishes identically. Only ∇τ-statistics survive (§2.4); none is special.
3. **Compression of the depth law.** Hoped that few moments of τ pin the symmetric fibre; found exactly one
   dimension per moment at N = 5..8 (generic). A first attempt with a standardised (unbounded) Chebyshev basis at
   N = 7, 8 produced a non-monotone rank count — a conditioning artefact, fixed by mapping τ to [−1, 1].
4. **Two bugs of my own, fixed before any number above was recorded:** fibre directions live in δq-space (a
   spurious "degree-≤N moments see 3 chiral dims" appeared before the fix; it is now 0 by construction), and an
   absolute row filter kept the numerically-zero row Im|p₁|^{2N} in `r1_det_tilt_laws.py` (membership then failed
   for k ≥ 2 at N ≥ 6; now a relative filter, and membership matches k(N−k) > N exactly).
5. **Online verification.** One web search was made (the permitted single attempt): it confirmed the existence,
   title and date of Tao's "Heat flow and zeroes of polynomials II: zeroes on a circle" (7 June 2018); its text was
   not fetched, so the attribution of the specific ODE to it remains recalled. Every other attribution stays
   "(recalled; not verified online)".

## 8. Unresolved (exact obstruction)

- **E2′** (τ injective on reflection classes for all N): needs a non-coincidence argument for first-collision times
  of non-mirror lattice configurations; nothing in the flow's structure forbids coincidences.
- **Reversibility of the local zero process** (whether the chiral half of the fibre is admissible for ζ): the
  functional equation does not give it; the n-level correlation conjectures assume GUE, which is reversible, but an
  AH-type impostor need not be.
- **§2.3 mechanism**: no intertwiner between density modes on configuration space and tangent modes at the clock.
- **Theorem C(ii)**: high-probability bound on the background stiffness S = Σ_k ½csc²(x_b^k/2) for the extremal
  pair in CUE (a rigidity estimate); not attempted here.
- Whether the SU(N)-heat-flow identification (§1.3) gives anything beyond a change of language, e.g. a Brownian
  characterisation of the depth (the largest backward heat time before det(1 − z·) leaves the unimodular-rooted class).

## 9. References (all recalled; not verified online) and what to search for

- Csordas, Smith, Varga, *Lehmer pairs of zeros, the de Bruijn–Newman constant Λ, and the Riemann hypothesis*,
  Constr. Approx. 10 (1994) — the two-body collision bound for close pairs.
- Rodgers, Tao, *The de Bruijn–Newman constant is non-negative*, Forum Math. Pi (2020) — Coulomb ODE for the zeros
  of H_t, §2; T. Tao, blog posts *Heat flow and zeroes of polynomials* (17 Oct 2017) and *… II: zeroes on a circle*
  (7 June 2018), https://terrytao.wordpress.com/2018/06/07/heat-flow-and-zeroes-of-polynomials-ii-zeroes-on-a-circle/
  — **existence/title/date verified by web search on 2026-09-05; content not fetched.** The search also surfaced
  arXiv:2308.11685 (*Zeros of random polynomials undergoing the heat flow*) and arXiv:2512.17808 (*Zeros of polynomial
  powers under the heat flow*), not read — the first is the natural place to check whether the CUE depth law
  N^{−8/3} is already implicit in the literature.
- Calogero, Perelomov, *Properties of certain matrices related to the equilibrium configuration of the one-dimensional
  many-body problems with the pair potentials V₁ = −ln|sin x| and V₂ = 1/sin²x*, Commun. Math. Phys. 59 (1978);
  Sutherland, Phys. Rev. A 4 (1971), 5 (1972) — spectrum ∝ k(N−k) at the equally spaced equilibrium.
- Haldane, PRL 60 (1988); Shastry, PRL 60 (1988) — one-magnon dispersion ∝ k(N−k) for the 1/sin² chain.
- Bourgade, Erdős, Yau, Yin, *Fixed energy universality for generalized Wigner matrices* (CPAM 2016); Landon, Sosoe,
  Yau, *Fixed energy universality of Dyson Brownian motion* (Adv. Math. 2019) — linearised DBM as a discrete
  fractional heat equation.
- Ben Arous, Bourgade, *Extreme gaps between eigenvalues of random matrices*, Ann. Probab. (2013); Feng, Wei (CβE
  smallest gaps).
- Tao, *The alternative hypothesis for unitary matrices* (2019/20); Lagarias, Rodgers, *Band-limited mimicry of point
  processes by point processes supported on a lattice* (Ann. Appl. Probab. 2021?) — search for any determinant-tilt
  or "total momentum sector" construction of AH-compatible measures: "ACUE" "determinant" "tilt"; "alternative
  hypothesis" "det(U)^k".
- For §1.3: search "Casimir" "self-inversive" "heat flow"; "Brownian motion on SU(N)" "characteristic polynomial"
  "backward heat"; I know of no source.
