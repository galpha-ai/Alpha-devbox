# r1 — Is "Level B" a shortcut or a relabelling of the small-gap problem?

**Fable overnight, cluster B (zeta-frontier), 2026-09-05.** Task B1 of `FABLE_COORDINATION.md`.
Status tags: **[P]** proved here, **[C]** computed (script + data in this directory), **[R]** refuted or
repaired, **[O]** open with the obstruction stated. Every literature item is marked
*(recalled; not verified online)* unless stated otherwise; one web search was made (§2.4).

**Standing hypotheses for every zeta-side statement:** RH (so that all zeros of H_0 are real and the
window zeros can be continued along the flow), and the Polymath 15 normalisation of §1.1. The three
versions of the Alternative Hypothesis are kept apart throughout (cf. Astra `COORDINATION.md`):
AH-strong (Lagarias–Rodgers 2019: every normalised gap is in {½, 1, 3/2, …} + o(1), *no zero gaps*),
AH-mult (multiplicities allowed, gap 0 permitted), AH-dens (density-one exceptions permitted).

## 0. Verdict in one paragraph

Level B is a **relabelling, and a strictly harder one**. (i) In the correct units the ACUE floor π²/8 is
exactly the two-body collision time of a gap of one half mean spacing, and the finite model is the
*exact* backward heat flow of a periodised zero set (§1.3), so the dictionary between the circle and the
line is one-to-one with no small-gap approximation. (ii) Theorem A transfers to the line (Theorem A′,
§2.1) under one explicit hypothesis (NR) on the non-real zeros formed elsewhere before the window
collides; under (NR), Level B ⟹ μ ≤ √(2c)/π < ½ where c = liminf (log T)²D_T (§2.2), so any proof of
Level B is a proof of μ < ½ — which is open, the record being μ ≤ 0.515396. For the periodised
(finite-polynomial) version of Level B the implication is unconditional (Theorem A). (iii) The converse
fails: a gap λ ∈ (λ*, ½) does **not** break the floor. In a clock background the threshold is
λ* = 0.4719538 (exact N-body, N-independent to 10⁻⁸; a one-dimensional quadrature gives 0.4718999 and
the closed-form expansion ρ = 1 + (π²/4 − 2)λ² + …), and in a random CUE background λ* is again ≈ 0.47
with a narrow spread (§3.4). So to reach Level B through gaps one needs gaps ≈ 6 % *below* ½.
(iv) Level B refutes only AH-strong: a multiple zero gives D_T = 0 (Level B holds trivially) while AH-mult
is untouched; a liminf statement says nothing about AH-dens. What the depth adds is a clean deterministic
formulation (Theorem C(i)) of "AH-strong ⟹ no normalised gap below ½ − o(1)", an explicit dressing
factor ρ(λ) quantifying the loss, and a smooth first-passage functional; it removes no information
requirement (§4).

---

## 1. The zeta-side statement, made precise (task (a))

### 1.1 The Polymath 15 flow and its zero ODE [P]

H_t(z) = ∫_0^∞ e^{tu²} Φ(u) cos(zu) du with Φ(u) = Σ_{n≥1}(2π²n⁴e^{9u} − 3πn²e^{5u}) e^{−πn²e^{4u}}, so that
H_0(z) = ⅛ ξ(½ + iz/2) *(Polymath 15 normalisation; recalled)*. Under RH the zeros of H_0 are z = ±2γ_j.
Λ (de Bruijn–Newman) = inf{t : H_t has only real zeros}; Rodgers–Tao: Λ ≥ 0 *(recalled)*; de Bruijn: if
H_t has only real zeros so has H_{t′} for t′ > t *(recalled)*. Differentiating under the integral
(Φ decays like e^{−πe^{4u}}) gives

  ∂_t H_t = ∫ u² e^{tu²}Φ cos(zu) du = −∂_z² H_t,          (1.1)

the *backward* heat equation in t; t increasing = e^{−t∂²}, the direction that preserves real zeros
(e.g. e^{−t∂²}(x² + c) = x² + c − 2t acquires real zeros as t grows).

**Zero ODE.** H_t is even, real on ℝ, entire of order 1 *(recalled: preserved by the flow)*, so
H_t(z) = H_t(0)∏_k(1 − z²/ρ_k²) with one ρ_k from each ± pair, absolutely convergent. Let x(t) be a simple
zero. From H_t(x(t)) ≡ 0: ∂_tH + H′ẋ = 0, hence with (1.1) ẋ = H″(x)/H′(x). Writing H = (z − x)G with
G(x) ≠ 0: H′(x) = G(x), H″(x) = 2G′(x), so

  ẋ_j = 2 (log G)′(x_j) = 2 Σ′_{ρ≠x_j} 1/(x_j − ρ)          (paired summation over ρ and −ρ)   (1.2)

(Csordas–Smith–Varga's formula; *recalled*). Positive sign: **t increasing is repulsive**; the finite
depth D is measured in the attractive direction, i.e. t decreasing from 0 (this is the sign point the
task asked to check: (1.1) has −∂_z² on the right, so ẋ = +H″/H′, not −H″/H′).

### 1.2 The γ-normalisation and the factor 4 [P]

Put G_τ(γ) := H_{4τ}(2γ). Then ∂_τG = 4(∂_tH)(2γ) = −4H″(2γ) = −∂_γ²G, so G_τ is the backward heat flow
of G_0(γ) = ⅛ξ(½ + iγ) = ⅛Ξ(γ) in the variable in which the zeros sit at the ordinates γ_j themselves.
The zeros γ_j(τ) = x_j(4τ)/2 obey dγ_j/dτ = 2ẋ_j = 2 Σ′ 1/(γ_j − γ_k): **the same ODE (1.2) in the
γ-variable, with τ = t/4.** Two zeros alone: (γ_a − γ_b)² = g₀² + 8τ, so running *backward* they meet at
τ = g₀²/8. The de Bruijn–Newman constants of the two normalisations differ by the same factor,
Λ^{(t)} = 4Λ^{(τ)} (this is the factor-4 discrepancy between older and Polymath normalisations of Λ;
*recalled*).

### 1.3 The finite model is exactly the periodised line flow [P]

For P_s(z) = Σ_j a_j e^{s j(N−j)} z^j put Q̃_s(θ) := e^{−sN²/4} e^{−iNθ/2} P_s(e^{iθ}) = Σ_m a_{m+N/2} e^{−sm²} e^{imθ}
(m = j − N/2). Since ∂_θ² e^{imθ} = −m²e^{imθ}, **∂_s Q̃ = ∂_θ² Q̃**: s is *forward* heat time on the circle,
so s ↔ −τ. The zeros of Q̃_s are θ_j(s) + 2πn, n ∈ ℤ. Lemma 1 (`depth_scaling_theorem.md`) gives
θ̇_j = −Σ_{k≠j} cot((θ_j − θ_k)/2), and the classical partial fraction ½cot(x/2) = Σ_{n∈ℤ} 1/(x + 2πn)
(symmetric partial sums) turns this into

  dθ_j/ds = −2 Σ′_{(k,n)≠(j,0)} 1/(θ_j − (θ_k + 2πn)),          (1.3)

which is (1.2) for the periodic zero set {θ_k + 2πn} run backward. **So the circle model is the τ-flow of
a 2π-periodic zero set, with θ ↔ γ and s ↔ −τ exactly; the cot kernel is the periodisation of the
1/x kernel.** Consistency: the exact two-body circle law D = −log cos(g₀/2) = g₀²/8 + g₀⁴/192 + … differs
from the line's g₀²/8 precisely by the periodic images. No small-gap approximation enters the dictionary.

### 1.4 The dimensionless depth; π²/8 ⟺ normalised gap ½ [P]

Let Δ be the local mean spacing and define the **dimensionless depth** 𝔇 := (2π/Δ)² × (backward collision
time in the matched time variable). On the circle Δ = 2π/N and 𝔇 = N²D. On the line at height T,
Δ_T = 2π/log(T/2π) (Riemann–von Mangoldt; *recalled*), and

  𝔇_T = (log(T/2π))² · D_T^{(τ)} = ¼ (log(T/2π))² · D_T^{(t)}.          (1.4)

𝔇 is invariant under any rescaling θ = cγ, s = −c²τ, so it does not depend on how many zeros one puts in
the window; N is only the unit 2π/Δ, i.e. **N ↔ log(T/2π)** (zeros per height 2π), not (log T)/2π (zeros
per unit height). For a normalised gap λ = g/Δ the two-body law gives 𝔇 = (2π/Δ)²(λΔ)²/8 = **π²λ²/2**, so
**λ = ½ ⟺ 𝔇 = π²/8** exactly, and this is the LR-bridge identity 𝔇 = ρπ²c²/2 of the handoff at ρ = 1.
Theorem C's floor is the N → ∞ limit of its own exact form: N²(−log cos(π/2N)) = π²/8 + π⁴/(192N²) + ….

**Level B, precisely.** With D_T as in §1.5: liminf_{T→∞} (log T)² D_T^{(τ)} < π²/8, equivalently
liminf (log T)² D_T^{(t)} < π²/2 in Polymath's t. (log T versus log(T/2π) changes nothing in a liminf.)

### 1.5 The local depth D_T: definition and why "local" is forced [P for the definition; O for the truncation]

Fix a window W_T = [T, T + H_T] (H_T ≥ Δ_T; H_T = 2π is the natural "N ≈ log T zeros" choice; only the
mean spacing enters 𝔇). Under RH the zeros of G_0 in W_T are real. For τ ≥ 0 let γ_j(τ) be the
continuation of γ_j along the zeros of G_{−τ}; it is real and obeys dγ_j/dτ = −2Σ′1/(γ_j − ρ) (sum over
all zeros ρ of G_{−τ}, real or not; a conjugate pair contributes the real number 4(γ_j − u)/((γ_j−u)²+v²))
as long as it is simple. Define

  **D_T := inf{τ > 0 : some γ_j(τ) with γ_j(0) ∈ W_T is a multiple zero of G_{−τ}}.**

Remarks. (i) *Why local.* Λ ≥ 0 means that for every τ > 0 the function G_{−τ} has a non-real zero;
under RH and by continuity of zeros this means collisions occur at arbitrarily small τ (necessarily at
heights → ∞ as τ → 0). The global first collision time is therefore 0 and only the window quantity is
meaningful. Zeros outside W_T may (and at large heights do) collide before D_T; after their collision
they are non-real and keep acting on the window zeros through the ODE. (ii) D_T = 0 iff W_T contains a
multiple zero; then Level B holds trivially at that T. (iii) A second, purely finite definition is
available: D_T^{per} := the circle depth of the N_T zeros of W_T mapped to the circle (θ_j = 2π(γ_j − T)/H_T);
then 𝔇_T^{per} = N_T²D_T^{per}. Relating D_T and D_T^{per} up to o(1) is the "truncation theorem", Step 1
of handoff §9.1, and is **[O]** here; everything below is stated for both.

### 1.6 Repairs to the handoff's wording [R]

1. §9.1 "N = (log T)/2π zeros in a window": the matching is N = log(T/2π) = 2π/Δ_T; the quoted quantity is
   the density per unit height. Harmless because Level B is written with (log T)² directly.
2. The constant π²/8 belongs to the τ-normalisation (backward heat flow of Ξ(γ)); in Polymath's t it
   is π²/2. Any zeta-side computation must say which.
3. §4.6 "Lagarias–Rodgers' μ ≤ 0.606894 is exactly μ_Λ ≤ 1.8177": one-directional. μ_Λ ≤ M ⟹ μ ≤ √(2M)/π
   is Theorem A; the reverse needs Theorem B, whose error O(N²δ²) is O(1) at the hard-core scale (§3).
4. "liminf N²(−Λ_ζ,local) < π²/8 ⟹ AH false" is correct for AH-strong (under (NR), §2), false as a
   statement about AH-mult (a double zero gives D_T = 0 and is allowed by AH-mult), and silent on AH-dens.

---

## 2. Level B ⟹ normalised gaps below ½ (task (b), first half)

### 2.1 Theorem A on the line [P]

**Theorem A′.** Let τ₁ > 0 and let γ_a(τ) > γ_b(τ) be two zeros of G_{−τ} which for τ ∈ [0, τ₁) are real,
simple and *adjacent among the real zeros* (no real zero strictly between them). Assume

  **(NR)** for every τ ∈ [0, τ₁) and every non-real zero u + iv of G_{−τ}: dist(u, [γ_b(τ), γ_a(τ)]) ≥ |v|.

Then g := γ_a − γ_b satisfies ġ ≥ −4/g on [0, τ₁), hence g(τ)² ≥ g(0)² − 8τ; in particular if the pair
collides at τ₁ then **τ₁ ≥ g(0)²/8**.

*Proof.* From the backward ODE, ġ = −4/g − 2Σ′_{ρ≠a,b}[1/(γ_a − ρ) − 1/(γ_b − ρ)], the sum over all other
zeros (paired; the differences are O(g/ρ²), so it converges absolutely). *Real ρ:* by adjacency ρ ∉
(γ_b, γ_a), so 1/(γ_a−ρ) − 1/(γ_b−ρ) = −g/((γ_a−ρ)(γ_b−ρ)) < 0 (both factors have the same sign), and the
bracket enters ġ with the sign +. *Conjugate pair ρ = u ± iv:* 1/(x−u−iv) + 1/(x−u+iv) = 2f(x) with
f(x) = (x−u)/((x−u)²+v²), so the pair contributes −4[f(γ_a) − f(γ_b)] = −4g f′(ξ) for some ξ ∈ (γ_b, γ_a),
with f′(x) = (v² − (x−u)²)/((x−u)²+v²)². Under (NR), (ξ−u)² ≥ v², so f′(ξ) ≤ 0 and the contribution is ≥ 0.
Every term is ≥ 0, so ġ ≥ −4/g, i.e. d(g²)/dτ ≥ −8. ∎

The real-zero half is verbatim Theorem A (monotonicity of the pair kernel); the only new ingredient
on the line is the non-real zeros produced by earlier collisions elsewhere, and (NR) is exactly the
condition under which their kernel is still monotone across the critical segment. On the circle,
where no root has left the circle before D, Theorem A needs no hypothesis.

### 2.2 Level B ⟹ μ < ½ [P under (NR); unconditional for the periodised version]

**Corollary.** Suppose the multiple zero at D_T is formed by two zeros a, b with γ_a(0) ∈ W_T that are
real and simple on [0, D_T) (the generic case; the codimension-two alternative — a real zero meeting a
conjugate pair — is excluded by hypothesis), and assume (NR) for the segment [γ_b(τ), γ_a(τ)] on
[0, D_T). Then (a, b) are consecutive zeros of ζ at τ = 0, and their normalised gap satisfies

  λ_ab ≤ √(8D_T) · log(T_ab/2π)/(2π) = (√(2𝔇_T)/π)(1 + o(1)).

Consequently, if liminf_T 𝔇_T = c < π²/8 along a sequence on which (NR) holds, then
**μ := liminf (γ′−γ) log γ/(2π) ≤ √(2c)/π < ½**; quantitatively μ ≤ √(2μ_Λ)/π with μ_Λ := liminf 𝔇_T.

*Proof.* If a zero c lay strictly between b and a at τ = 0, it would have to leave the axis before D_T
(real zeros cannot cross without colliding), by colliding with a zero d ≠ a, b (a and b are simple on
[0, D_T)); c stays in (γ_b, γ_a) until then, so the collision point and the real part of the resulting
non-real zero lie inside [γ_b, γ_a] while v ≠ 0 immediately after, violating (NR). So a, b are consecutive at τ = 0 and Theorem A′ applies on [0, D_T):
g(0)² ≤ 8D_T. Since the pair lies within one gap of W_T, log(T_ab/2π) = (1 + o(1)) log(T/2π) for
H_T = o(T), and (1.4) gives the bound. ∎

**Periodised version [P, no hypothesis].** For any N-point circle configuration Theorem A gives
N²D ≥ N²δ_min²/8 = π²λ_min²/2 (λ_min = δ_min N/2π), so 𝔇^{per} < π²/8 ⟹ λ_min < ½ outright. Hence
liminf 𝔇_T^{per} < π²/8 ⟹ μ < ½ with no hypothesis at all.

**Consequence for AH.** AH-strong ⟹ all normalised gaps ≥ ½ − o(1) ⟹ (Theorem A′ under (NR), or Theorem
A for the periodised version) 𝔇_T ≥ π²/8 − o(1): this is Theorem C(i) on the line. Level B is the
negation, and by the Corollary it *contains* μ < ½ — which already refutes AH-strong statically, with no
flow. So whatever proves Level B proves μ < ½ and refutes AH-strong without the flow.

### 2.3 What (NR) excludes, and the obstruction to removing it [O]

(NR) fails only if a non-real zero comes horizontally closer to the critical segment than its own
height. Heuristics for its size: a pair that collided at τ_c has, by the two-body law, v = √(2(τ − τ_c))
≤ √(2D_T) = Δ_T√(2𝔇_T)/(2π) ≈ 0.25Δ_T at 𝔇_T = π²/8; the real neighbours push it further
(v̇ = 1/v + 2vΣ_k 1/((u−x_k)²+v²) + [other non-real pairs]), giving v² ≈ (Δ²/2π²)(e^{4π²τ/Δ²} − 1), i.e.
v ≈ 0.35Δ_T at τ = D_T. So (NR) can fail only through a collision within ≈ 0.35 mean spacings of the
critical pair before D_T — a three-zero cluster. The circle experiment of §3.4 tests the analogous
event directly (a reciprocal pair formed elsewhere accelerating the forced pair): see the
`two_body_bound_violations` statistic there.

*Obstruction to a proof.* One needs a bound |Im w(τ)| ≤ C√τ, uniform in height, for the non-real zeros of
G_{−τ}. The ODE for v has the sign-indefinite terms 2(v − v_k)/|w − z_k|² from other non-real pairs (the
topmost zero is pushed *up* by every lower pair), and even ignoring them, the real-zero sum bounded only
through S(T) = O(log T) gives v² ≲ τ log T ≈ 1/log T ≫ Δ_T², useless at the gap scale. A genuine
rigidity input (control of the zero count at scale Δ_T) is required; this is the content of the
truncation theorem (Step 1 of §9.1) and is left open. (Attempted and abandoned; see §5.)

### 2.4 The record for μ (all under RH; recalled unless stated)

Montgomery–Odlyzko 1981: μ ≤ 0.5179; Conrey–Ghosh–Gonek 1984: 0.5172; Bui–Milinovich–Ng 2010: 0.5155;
Feng–Wu 2012: 0.5154; Preobrazhenskiĭ 2016: **0.515396** (all *recalled; not verified online*). One web
search (the single permitted attempt) returned a snippet stating "the best current results under RH
are μ ≤ 0.515396 by Preobrazhenskiĭ and λ ≥ 3.18 by Bui–Milinovich" (snippet only; source text not
read) and listed arXiv:2604.05733 "Small gaps between consecutive zeros of the Riemann zeta-function"
(2026; not read — it is the "Inoue" item assigned to Astra's Residual-Gram agent; whether it lowers
0.515396 must be checked in `r1_small_gaps.md`). Unconditionally, positive proportions of gaps below
1 − c and above 1 + c go back to Selberg, and Montgomery's pair-correlation theorem gives gaps below
≈ 0.68 (*recalled*). Nothing known reaches ½, and the Corollary shows Level B would.

---

## 3. The converse: does a gap λ < ½ force 𝔇 < π²/8? (task (b), second half)

Theorem B bounds 𝔇 ≤ (π²λ²/2)(1 + O(AN²δ²)) with A = S/N²; at λ ≍ 1 the error is O(1), so the converse is
not automatic. We compute it exactly.

### 3.1 The clock cotangent identity [P]

**Lemma.** For x ∉ (2π/N)ℤ, Σ_{k=0}^{N−1} cot((x + 2πk/N)/2) = N cot(Nx/2).

*Proof.* With w = e^{ix}, ω = e^{2πi/N} and cot(y/2) = i(e^{iy}+1)/(e^{iy}−1):
Σ_k cot((x+2πk/N)/2) = iΣ_k(1 + 2/(wω^k − 1)) = iN + 2iΣ_k 1/(wω^k − 1). Put z = 1/w; then
1/(wω^k − 1) = −z/(z − ω^k), and the logarithmic derivative of z^N − 1 = ∏_k(z − ω^k) gives
Σ_k 1/(z − ω^k) = Nz^{N−1}/(z^N − 1). Hence Σ_k 1/(wω^k − 1) = −Nz^N/(z^N − 1) = N/(w^N − 1), and the
total is iN(w^N + 1)/(w^N − 1) = N cot(Nx/2). ∎ (Checked numerically to 5·10⁻¹¹ at N = 37.)

### 3.2 The rigid-background reduction [P]

Configuration: defect pair at ±φ, φ = λΔ/2, background at Δ(k+½), k = 1, …, N−2 (the clock with the two
slots ±Δ/2 replaced by the pair; gap pattern λ, (3−λ)/2, 1, …, 1, (3−λ)/2 in units of Δ). It is
reflection-symmetric, so by uniqueness of ODE solutions the pair stays at ±φ(s) and the background
stays mirror-symmetric. **Rigid ansatz:** freeze the background at the clock slots. The force on the
point at +φ is −cot(φ) (partner) minus the background sum, which by the Lemma with x = φ − Δ/2 (the full
clock sum is −N tan(Nφ/2)) minus the two removed slots is

  φ′ = −cot φ + N tan(Nφ/2) + cot((φ − Δ/2)/2) + cot((φ + Δ/2)/2).          (3.1)

With u = φ/Δ = λ/2 initially and σ = N²s, (3.1) becomes, as N → ∞ (the O(1/N) corrections of the
three cot terms cancel identically at first order),

  du/dσ = F(u) := −1/(4π²u) + tan(πu)/(2π) + u/(π²(u² − ¼)),          (3.2)

  **𝔇_rigid(λ) = ∫_0^{λ/2} du/(−F(u)).**          (3.3)

Checks: −F(u) = 1/(4π²u) − (½ − 4/π²)u + O(u³) > 0 on (0, ½); as u → ½⁻ the tan and rational poles cancel
and F(½) = 0 exactly — the clock is an equilibrium (numerically F(0.4999) = −2.2·10⁻⁵, F(0.49999) = −2.2·10⁻⁶).
Expanding the integrand and integrating termwise (sympy, `r1_one_defect_threshold.py` companion check):

  **ρ_rigid(λ) := 𝔇_rigid/(π²λ²/2) = 1 + (π²/4 − 2)λ² + (7π⁴/72 − 4π²/3 + 4)λ⁴ + (41π⁶/960 − 5π⁴/6 + 5π² − 9)λ⁶ + …**
  = 1 + 0.467401λ² + 0.310856λ⁴ + 0.233110λ⁶ + …

(numerically verified: residual/λ⁴ → 0.311 as λ → 0). No elementary antiderivative of 1/(−F) was found
(sympy did not return within 300 s); (3.3) is a one-line quadrature.

### 3.3 Exact N-body depth of the one-defect clock [C]

Script `scripts/r1_one_defect_threshold.py` (root ODE of Lemma 1, DOP853, rtol 10⁻¹⁰, event at
g = 10⁻³Δ plus the exact two-body remainder). Validation (`scripts/r1_solver_validation.py`): it
reproduces the programme's single-dislocation constant s* = 1.419640342 (two independent earlier
routes) to 1.419640341 at N = 256, and agrees with a 50-digit coefficient-flow bisection at N = 32 to
1.7·10⁻¹¹. (The double-precision coefficient route `dyn1_core.find_ustar`/`np.roots` is *not* usable at
N ≥ 32 for near-clock or CUE polynomials: catastrophic cancellation in the coefficient construction,
§5.)

| λ | 𝔇_exact (N = 64, 128, 256 agree to 10⁻⁸) | ρ_exact | 𝔇_rigid (N → ∞) | ρ_rigid |
|---|---|---|---|---|
| 0.30 | 0.46399733 | 1.044728 | 0.46401475 | 1.044767 |
| 0.40 | 0.85565655 | 1.083702 | 0.85576419 | 1.083838 |
| 0.45 | 1.10869763 | 1.109477 | 1.10892947 | 1.109709 |
| 0.47 | 1.22220868 | 1.121192 | 1.22251788 | 1.121475 |
| 0.48 | 1.28180699 | 1.127380 | 1.28216282 | 1.127693 |
| 0.49 | 1.34337958 | 1.133801 | 1.34378818 | 1.134146 |
| **0.50** | **1.40699039** | **1.140463** | 1.40745863 | 1.140843 |
| 0.60 | 2.17266439 | 1.222983 | 2.17433589 | 1.223924 |
| 0.80 | 4.89977410 | 1.551409 | 4.91684566 | 1.556814 |
| 0.90 | 7.85403414 | 1.964889 | 7.91567281 | 1.980309 |

The first collision is always the defect pair. The rigid ansatz is accurate to 3·10⁻⁴ at λ = ½ (the
background moves by ≈ 10⁻² spacings during the collapse) and its error is O(λ⁴). The finite-N
corrections are below 10⁻⁸ already at N = 64 (the O(1/N) terms of (3.1) cancel; the O(1/N²) ones are
tiny), so these numbers are the N → ∞ values.

**Threshold.** 𝔇(λ*) = π²/8 at

  **λ*_exact = 0.4719538 (N = 64: 0.471953775; N = 128, 256: 0.471953773), λ*_rigid = 0.4718999,**

with ρ(λ*) = 1/(4λ*²) = 1.12266. For comparison the symmetric defect at λ = ½ has ρ = 1.1405 (the
asymmetric ACUE dislocation, gaps ½, 1, …, 1, 3/2, has ρ = 1.1507).

### 3.4 One forced gap in a random CUE background [C]

[[CUE-RESULTS]]

### 3.5 Consequence: the converse fails, quantitatively [P + C]

A consecutive gap of normalised size λ ∈ (0.472, ½) in a clock-like environment has 𝔇 > π²/8 (e.g.
λ = 0.49 gives 𝔇 = 1.343 > 1.234). Hence **μ < ½ does not imply Level B**; to reach Level B through a gap
one needs λ < λ*(environment), and λ* ≈ 0.472 both in the clock and (§3.4) in a typical CUE
environment. In gap terms the depth formulation costs a factor 1/(2λ*) = 1.059: the small-gap theorem
that Level B *requires* is ≈ 6 % stronger than μ < ½, while the best known is μ ≤ 0.5154 — the
distance to be covered is 0.5154 → 0.472, not 0.5154 → 0.5.

---

## 4. Verdict (task (c))

**Relabelling, and a strictly harder one.**

1. *Logic.* Level B ⟹ μ < ½ (Corollary 2.2; unconditional for 𝔇^{per}, under (NR) for the true flow).
   Every proof of Level B is a proof of μ < ½. There is no reading under which Level B is "easier".
2. *Converse.* μ < ½ ⇏ Level B: gaps in (λ*, ½) satisfy the floor (§3). Level B ⊂ {μ ≤ λ* ≈ 0.472}.
3. *Information.* Handoff §9.1 hopes to prove Level B from bandwidth-≤1 pair correlation plus
   "energy/variance inputs of Rodgers–Tao type". Any input consistent with AH-strong is consistent with
   the floor (Theorem C(i)/A′): Tao's ACUE and the LR2019 T₁-mimickers (*recalled*) reproduce the
   sine-kernel pair correlation at bandwidth ≤ 1 and have δ_min = Δ/2 deterministically, hence
   periodised depth 𝔇 ≥ π²/8 for every non-clock configuration. So Step 3 of §9.1 must
   use information that AH-strong violates — the same bandwidth-> 1 wall as the static route. The
   Rodgers–Tao argument contradicts a *full lattice* (bandwidth-<1 visible); a half-lattice hard core
   is invisible at that bandwidth by construction. The flow adds no arithmetic: H_t is determined by
   the t = 0 zero set, so Level B is a nonlinear functional statement about the zeros at t = 0, and
   Theorem A′ says which functional it dominates — the minimum gap.
4. *AH versions.* Level B refutes AH-strong only. A multiple zero gives D_T = 0 (Level B true) with
   AH-mult intact; a liminf statement is a sparse-window statement and cannot touch AH-dens — that
   needs a positive-proportion depth statement, which by the same Corollary contains the
   positive-proportion small-gap problem below ½ (also open) with the same ≈ 6 % dressing loss.
5. *What the depth formulation adds.* (a) Theorem C(i)/A′ as a clean deterministic formulation:
   "hard core ½ − o(1) ⟹ 𝔇 ≥ π²/8 − o(1)", with the exact dictionary of §1. (b) The one-way bridge
   μ ≤ √(2μ_Λ)/π with explicit constants, and the dressing law ρ(λ) = 1 + (π²/4 − 2)λ² + … saying how
   much is lost. (c) A smooth first-passage functional of the configuration, potentially usable in the
   variational LR problem of §9.2 (bounding μ_Λ over mimickers gives μ bounds — one direction only).
   (d) A sharp experimental probe: the CUE/ACUE separation N^{−8/3} vs N^{−2}.
   *What it does not add:* any reduction of the information requirement; any access to AH-mult or
   AH-dens from a liminf; a rigorous statement for the true flow without the truncation theorem/(NR).

---

## 5. Failed attempts

1. **Removing (NR).** Tried to bound the height of non-real zeros formed before D_T. The v-equation
   v̇ = 2Σ_k(v − v_k)/|w − z_k|² has sign-indefinite contributions from other non-real pairs (every lower
   pair pushes the topmost one up), and the real-zero part bounded only by S(T) = O(log T) gives
   v² ≲ τ log T — the right order for a fixed-length margin but not at the gap scale. Needs zero-count
   rigidity at scale Δ_T; left as [O] (§2.3).
2. **Closed form for (3.3).** sympy did not return an antiderivative of 1/(−F(u)) within 300 s; the
   series (§3.2) is the closed-form content obtained.
3. **Coefficient-route cross-check with `dyn1_core.find_ustar` at N = 64.** Returned 0: `np.poly` builds
   ∏(z − z_j) by sequential convolution and, for 64 unit-circle roots, passes through partial products
   with coefficients ~2⁶⁴ that cancel to O(1); the resulting polynomial had |P(z_j)| ≈ 1.8 at its own
   roots (and 0.7 % root errors for the near-clock case). Repaired by building the coefficients in
   50-digit arithmetic (then double-precision `np.roots` is accurate to 5·10⁻¹⁵); `dyn1_core` itself is
   fine at its design range N ≤ 10.
4. **Level B ⟹ AH-dens refutation.** Not possible from a liminf; recorded in §4.4.
5. **Web verification.** One search only (rule 4); the 2026 preprint arXiv:2604.05733 surfaced but was
   not read.

---

## 6. Scripts, commands, data

All under `research/riemann-rmt/overnight/fable/`.

| script | what | command | output |
|---|---|---|---|
| `scripts/r1_one_defect_threshold.py` | one-defect clock: exact N-body depth (N = 64, 128, 256), rigid finite-N and N → ∞ quadrature, λ*, identity checks | `python3 r1_one_defect_threshold.py` (14 s) | `data/r1_one_defect.json`, `data/r1_one_defect_log.txt` |
| `scripts/r1_solver_validation.py` | ODE solver vs s* = 1.419640342 (N = 32…256) and vs 50-digit coefficient bisection (N = 32) | `python3 r1_solver_validation.py` | `data/r1_solver_validation_log.txt` |
| `scripts/r1_cue_forced_gap.py` | CUE background with one forced gap: D_pair(λ) through the full coefficient flow with root continuation (collisions elsewhere included), λ* distribution | `python3 r1_cue_forced_gap.py N samples seed [tag]` | `data/r1_cue_forced_gap_N{32,64,128}*.json`, logs |

Output summaries: §3.3 table (from `r1_one_defect_log.txt`); validation: dislocation 1.419640026 /
1.419640322 / 1.419640340 / 1.419640341 at N = 32/64/128/256; mp bisection rel. diff 1.68·10⁻¹¹;
identity error 4.8·10⁻¹¹; rigid direct-vs-closed RHS 6.3·10⁻¹³. CUE: §3.4.

---

## 7. Claim ledger

| id | claim | status |
|---|---|---|
| B1-1 | ∂_tH_t = −∂_z²H_t; ẋ_j = +2Σ′1/(x_j − x_k); t increasing repulsive | [P] |
| B1-2 | γ-normalisation G_τ(γ) = H_{4τ}(2γ), same ODE, τ = t/4; floor π²/8 in τ-units, π²/2 in t-units | [P] |
| B1-3 | circle flow = τ-flow of the 2π-periodic zero set, exactly (cot = periodised 1/x); s ↔ −τ, N ↔ log(T/2π) | [P] |
| B1-4 | 𝔇 = π²λ²/2 two-body; λ = ½ ⟺ 𝔇 = π²/8; Theorem C floor is the N → ∞ half-gap two-body time | [P] |
| B1-5 | definition of the local depth D_T; global collision time is 0 by Λ ≥ 0 (recalled) + RH | [P] (definition) |
| B1-6 | Theorem A′ on the line under (NR) | [P] |
| B1-7 | Level B ⟹ μ ≤ √(2c)/π < ½ (under (NR) for the true flow; unconditional for 𝔇^{per}) | [P] |
| B1-8 | (NR) cannot be removed by the ODE for Im w alone; needs zero-count rigidity at scale Δ_T | [O] |
| B1-9 | Σ_k cot((x+2πk/N)/2) = N cot(Nx/2) | [P] |
| B1-10 | rigid reduction (3.1)–(3.3), clock equilibrium, ρ_rigid = 1 + (π²/4−2)λ² + 0.3109λ⁴ + 0.2331λ⁶ + … | [P] |
| B1-11 | one-defect clock: λ* = 0.4719538 exact (N-independent), 0.4718999 rigid; ρ(½) = 1.1405 | [C] |
| B1-12 | CUE background: λ* distribution (§3.4) | [C] |
| B1-13 | converse fails: gaps in (λ*, ½) satisfy the floor; Level B needs gaps ≈ 6 % below ½ | [P+C] |
| B1-14 | handoff wording repairs (§1.6): N = log(T/2π); τ vs t; one-way bridge; AH-strong only | [R] |
| B1-15 | Level B cannot follow from inputs consistent with AH-strong (bandwidth ≤ 1); relabelling verdict | [P modulo recalled LR2019 mimicker facts] |
| B1-16 | truncation theorem D_T ≈ D_T^{per} | [O] |
