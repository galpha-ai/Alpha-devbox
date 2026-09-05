# Theorem B repaired: the background bound with the endpoint maximum, explicit constants, and window stability

**Fable overnight, round 1, task A1 (depth-rigor cluster)** — 2026-09-05.
Repairs §4 of `research/riemann-rmt/depth_scaling_theorem.md` after Astra's audit
(`handoff/astra-2026-09-05/audit_research.py`, check "Counterexample to old background endpoint bound").
Intended mirror path in the collaboration repo: `fable/overnight-2026-09-05/r1_theoremB_repair.md`.

Status tags: **[P]** proved here (argument written out), **[C]** computed (script + data in this
directory), **[R]** refuted/repaired, **[O]** open with the obstruction named. Numerical evidence is
never used as proof; every [P] item is self-contained modulo Lemma 1 (root ODE) and Lemma 2/Theorem A
of the source document, which are quoted, not re-proved.

## 0. Summary

| what | old (§4 of the source) | repaired | status |
|---|---|---|---|
| endpoint bound on the background bracket | 0 ≤ B ≤ g·S, S = Σ ½csc²(x_b^k/2) | **false**; B ≤ g·S\*, S\* = Σ ½max(csc²(x_b^k/2), csc²(x_a^k/2)) = ½Σ csc²(ρ_k/2) | [R]→[P] §2 |
| exact form of the bracket | — | B = 2 sin(g/2)·S_exact, S_exact = ½Σ 1/(sin(y_k/2) sin(w_k/2)); B ≤ g S_exact ≤ g S_avg ≤ g S\* | [P] §2 |
| −2cot(g/2) = −4/g + O(g) | hidden O(g) | −4/g ≤ −2cot(g/2) ≤ −4/g + κ₀ g, κ₀ = κ(δ/2) ∈ [1/3, 4/π²] | [P] §3 |
| Theorem B | D ≤ (δ²/8)(1 + O(AN²δ²)) "given S ≤ AN² on the window" | D ≤ −(2μ)⁻¹log(1 − μδ²/4) ≤ (δ²/8)(1 + μδ²/4), μ = Θ·S\*(0) + κ₀, under (W) window factor Θ and (M) μδ² ≤ 2 | [P] §4 |
| what the hypothesis needs | unspecified | static bound S\*(0) ≤ N/2 + 4CN/r + 2m₀/r² from a local density bound (Lemma S); Θ = 2 from a *time-0* separation hypothesis via the unconditional gap bound g_i(s)² ≥ g_i(0)² − 8s (Lemma W) | [P] §5 |
| "S\* changes by ≤ 2 when D ≤ δ²/4 and Nδ ≤ 1" | conjectured in the task | **false as stated**: 3-cluster with neighbour gap 1.01δ gives S\*_sup/S\*(0) = 9.5; true under (H_C) with √2·CNδ ≤ 1 − 1/√2 | [R]+[P]+[C] §5 |
| fully explicit CUE-type corollary | — | under (H_C), CNδ ≤ 0.2, Nδ ≤ 1: δ²/8 ≤ D ≤ (δ²/8)(1 + 4C²N²δ² + 0.29δ) | [P] §6 |
| numerics | — | CUE N = 16, 32, 64 (300 each), ACUE lattice (100 each), dislocation family, adversarial clusters; old bound fails in 34–49% of configurations, S\* never; D ≤ T(μ_sup) in every sample | [C] §7 |
| the regularity hypothesis for CβE | [O] | still [O], but reduced to a static statement about the configuration at s = 0 (one-sided density near the min-gap pair and Nδ_min small) | [O] §8 |

## 1. Setting and notation

Roots e^{iθ_j}, j = 1,…,N (N ≥ 3, distinct). Flow P_s(z) = Σ_j a_j e^{s·j(N−j)} z^j, s ≥ 0; D = first
collision time (= −Λ; the task's window [−D, 0] in the Λ-variable is [0, D] here). Until D
(Lemma 1 of the source, [P] there):

  θ_j′ = −Σ_{k≠j} cot((θ_j − θ_k)/2).

The cyclic order of the roots is preserved on [0, D) (roots cannot cross without colliding), so all
index sets below are fixed in time.

Fix an **adjacent** pair (a, b) with g := θ_a − θ_b ∈ (0, 2π) measured counter-clockwise from θ_b to
θ_a and no root strictly inside that arc. For k ∉ {a, b} put x_j^k := (θ_j − θ_k) mod 2π ∈ (0, 2π).
Adjacency gives

  x_a^k = x_b^k + g,  0 < x_b^k < x_a^k < 2π,                                      (1.1)

(going counter-clockwise from θ_k one meets θ_b, then, after an empty arc of length g, θ_a; and
θ_k is not in the open arc (θ_b, θ_a), so x_a^k < 2π). Define the two **pair-anchored arcs**

  y_k := 2π − x_a^k = ccw arc from θ_a to θ_k,   w_k := x_b^k = ccw arc from θ_k to θ_b,

so y_k, w_k > 0 and y_k + w_k + g = 2π, and the distance to the pair

  ρ_k := dist(θ_k, {θ_a, θ_b}) = min(y_k, w_k) ≤ π − g/2 < π.                          (1.2)

(Indeed dist(θ_k, θ_a) = min(y_k, 2π − y_k) = min(y_k, w_k + g) and dist(θ_k, θ_b) = min(w_k, y_k + g).)

**Gap equation.** Differencing Lemma 1 (as in the source's Theorem A),

  g′ = −2cot(g/2) + B(s),   B := Σ_{k≠a,b} [cot(x_b^k/2) − cot(x_a^k/2)] ≥ 0,          (1.3)

B ≥ 0 because cot(·/2) is strictly decreasing on (0, 2π) and x_b^k < x_a^k (this is Theorem A).
Using x_a^k = 2π − y_k, cot(x_a^k/2) = −cot(y_k/2), so equivalently

  B = Σ_{k≠a,b} [cot(w_k/2) + cot(y_k/2)],  θ_a′ = −cot(g/2) + Σ_k cot(y_k/2),  θ_b′ = cot(g/2) − Σ_k cot(w_k/2).   (1.4)

**Stiffnesses** (all sums over k ∉ {a, b}):

  S_old := Σ ½csc²(x_b^k/2)  (the source's S),
  S\*   := Σ ½max(csc²(x_b^k/2), csc²(x_a^k/2)),
  S_avg := Σ ¼(csc²(x_b^k/2) + csc²(x_a^k/2)),
  S_exact := Σ ½ / (sin(x_b^k/2) sin(x_a^k/2)) = Σ ½ / (sin(w_k/2) sin(y_k/2)).

**Lemma 0 [P].** S\* = ½ Σ_{k≠a,b} csc²(ρ_k/2).
*Proof.* For t ∈ (0, 2π), csc²(t/2) = csc²(d(t)/2) with d(t) = min(t, 2π − t) ∈ (0, π], and
csc²(·/2) is decreasing on (0, π]. Hence max(csc²(x_b^k/2), csc²(x_a^k/2)) = csc²(min(d(x_b^k), d(x_a^k))/2),
and min(d(w_k), d(2π − y_k)) = min(w_k, y_k + g, y_k, w_k + g) = min(y_k, w_k) = ρ_k. ∎

So S\* is the natural symmetric object: the sum of ½csc²(·/2) over the distances of the other roots to
the pair. S_old uses only the distances to θ_b, i.e. it is a labelling artefact.

## 2. (a) The exact identity and the correct mean-value bound

**Proposition 2.1 (exact identity) [P].** For all x, g with sin(x/2) sin((x+g)/2) ≠ 0,

  cot(x/2) − cot((x+g)/2) = sin(g/2) / ( sin(x/2) · sin((x+g)/2) ).

*Proof.* cot A − cot B = (cos A sin B − sin A cos B)/(sin A sin B) = sin(B − A)/(sin A sin B) with
A = x/2, B = (x+g)/2, B − A = g/2. ∎

Consequently, from (1.3), (1.1) and sin(x_a^k/2) = sin(π − y_k/2) = sin(y_k/2):

  **B = sin(g/2) Σ_{k≠a,b} 1/( sin(w_k/2) sin(y_k/2) ) = 2 sin(g/2) · S_exact.**            (2.1)

**Proposition 2.2 (endpoint mean-value bound) [P].** For 0 < x < x + g < 2π,

  0 < cot(x/2) − cot((x+g)/2) ≤ g · ½ max( csc²(x/2), csc²((x+g)/2) ).

*Proof.* cot(x/2) − cot((x+g)/2) = ∫_x^{x+g} ½csc²(t/2) dt. On (0, 2π), (d/dt)csc²(t/2) =
−csc²(t/2)cot(t/2), which is negative on (0, π) and positive on (π, 2π); so csc²(t/2) is decreasing
on (0, π], increasing on [π, 2π), and its maximum over any sub-interval [x, x+g] ⊂ (0, 2π) is attained
at an endpoint (this holds whether or not the interval straddles π). Bound the integrand by that
maximum. Positivity is the monotonicity of cot(·/2). ∎

Summing over k with x = x_b^k (allowed by (1.1)):

  **0 ≤ B ≤ g · S\*.**                                                                 (2.2)

**Proposition 2.3 (refinements) [P].**  B ≤ g·S_exact ≤ g·S_avg ≤ g·S\*, and S_avg ≤ S\* ≤ 2 S_avg.
*Proof.* B = 2sin(g/2)S_exact ≤ g S_exact since sin(g/2) ≤ g/2. AM–GM on 1/p², 1/q² gives
1/(pq) ≤ ½(1/p² + 1/q²), i.e. S_exact ≤ S_avg. ¼(p⁻² + q⁻²) ≤ ½max(p⁻², q⁻²) ≤ ½(p⁻² + q⁻²). ∎

A trivial lower bound in the same spirit: since csc² ≥ 1, B ≥ (N − 2)g/2.

**Why the old bound is false [R].** The source bounded the integrand by its value at the *left*
endpoint x_b^k only. For every k on the a-side of the pair (y_k < w_k, i.e. x_b^k = w_k > π − g/2)
the whole segment [x_b^k, x_a^k] lies where csc²(t/2) is increasing (as soon as w_k > π), and the
maximum is at the right endpoint. Astra's instance g = 0.05, x_b = 2π − 0.15 (so y = 0.10, w = 6.133):
difference quotient 133.500132, old term 89.055743 (fails), S\*-term ½csc²(0.05) = 200.166750,
S_avg-term 144.611247, identity (2.1) reproduces the quotient to 5·10⁻¹³ (script §7, item [1]).
In random configurations the old bound fails whenever the a-side contributes more stiffness than the
b-side, i.e. in roughly half of all configurations (Table 1: 34–49%).

Nothing downstream of (2.2) in the source used S_old except through the mean-value step, so the repair
is exactly: S → S\* (or, more sharply, S_avg or S_exact), plus the two further corrections in §3–§5
that the audit did not raise but a full re-derivation exposes.

## 3. Three elementary inequalities (used with explicit constants)

**(I1) [P]** Let κ(x) := (1 − x cot x)/x² on (0, π). Then κ is increasing, κ(0⁺) = 1/3,
κ(π/2) = 4/π² = 0.40528…, and for 0 < x ≤ x₀ < π:

  1/x − κ(x₀)·x ≤ cot x ≤ 1/x.

*Proof.* Upper bound: φ(x) := 1 − x cot x has φ(0⁺) = 0 and φ′ = x csc²x − cot x = (x − sin x cos x)/sin²x ≥ 0
(x ≥ ½ sin 2x), so φ ≥ 0. Monotonicity of κ = φ/x²: κ′ ≥ 0 ⇔ xφ′ ≥ 2φ ⇔ x² csc²x + x cot x − 2 ≥ 0
⇔ (multiplying by sin²x) ψ(x) := x² + ½x sin 2x + cos 2x − 1 ≥ 0. Now ψ(0) = ψ′(0) = 0,
ψ′ = 2x + x cos 2x − (3/2) sin 2x, ψ″ = 2 − 2cos 2x − 2x sin 2x = 4 sin x (sin x − x cos x) > 0 on (0, π)
(sin x − x cos x vanishes at 0 and has derivative x sin x > 0). Hence ψ ≥ 0. The lower bound is
φ(x) ≤ κ(x₀)x², and the two values are x cot x = 1 − x²/3 + O(x⁴) and κ(π/2) = 1/(π²/4). ∎

In particular, with g ∈ (0, δ], δ ≤ π, and **κ₀ := κ(δ/2)** (so 1/3 < κ₀ ≤ 4/π²):

  −4/g ≤ −2cot(g/2) ≤ −4/g + κ₀·g.                                                    (3.1)

(The two-body time −log cos(δ/2) = δ²/8 + δ⁴/192 + … corresponds exactly to κ = 1/3 in the closed form
of §4 with S\* = 0, which is a check on the constant.)

**(I2) [P]** For x ∈ (0, π/2]: csc²x ≤ 1/x² + 1 − 4/π². Hence for ρ ∈ (0, π]: csc²(ρ/2) ≤ 4/ρ² + 1 − 4/π².
*Proof.* h(x) := csc²x − x⁻² has h′ = 2x⁻³ − 2cos x sin⁻³x ≥ 0 ⇔ (sin x/x)³ ≥ cos x ⇔ F(x) :=
3 log(sin x / x) − log cos x ≥ 0. F(0⁺) = 0 and F′ = 3cot x − 3/x + tan x ≥ 0 ⇔ (multiplying by
x sin x cos x > 0) x(2 + cos 2x) ≥ (3/2) sin 2x =: G(x) ≥ 0, where G(0) = 0 and
G′ = 2 − 2cos 2x − 2x sin 2x = 4 sin x(sin x − x cos x) ≥ 0 (same function as in (I1)). So h is
increasing and h(x) ≤ h(π/2) = 1 − 4/π². ∎

**(I3) [P]** t ↦ t² csc²(t/2) is increasing on (0, π] (because u/sin u is increasing on (0, π/2]:
(u/sin u)′ = (sin u − u cos u)/sin²u > 0). Hence for 0 < ψ ≤ 1 and 0 < ρ ≤ π:
csc²(ψρ/2) ≤ ψ⁻² csc²(ρ/2).

**(I4) [P]** For every cyclic gap g_i ∈ (0, 2π): g_i′ ≥ −2cot(g_i/2) ≥ −4/g_i on [0, D)
(Theorem A of the source for the first inequality, valid for every adjacent pair; for the second,
(I1) if g_i ≤ π and −2cot(g_i/2) > 0 > −4/g_i if g_i > π). Therefore

  **g_i(s)² ≥ g_i(0)² − 8s  for all i and all s ∈ [0, D).**                                (3.2)

## 4. (b) Theorem B re-derived

Throughout, (a, b) is a pair realising δ := δ_min (it is adjacent), g(s) its gap, S\*(s) the stiffness
of §1 along the flow, κ₀ = κ(δ/2).

**Proposition 4.1 (two-sided differential inequality) [P].** For 0 ≤ s < D,

  −2cot(g/2) ≤ g′ ≤ −2cot(g/2) + g·S\*(s),   and also   g′ ≤ −2cot(g/2) + g·S_avg(s) = −2cot(g/2) + 2sin(g/2)·S_exact(s).

*Proof.* (1.3) with (2.2) and Proposition 2.3; adjacency persists on [0, D). ∎

**Theorem B′ (repaired) [P under (W), (M)].** Let Θ ≥ 1 and suppose

  (W) S\*(s) ≤ Θ·S\*(0) for every s ∈ [0, D) with s ≤ δ²/4;
  (M) μ := Θ·S\*(0) + κ₀ satisfies μδ² ≤ 2.

Then

  δ²/8 ≤ −log cos(δ/2) ≤ D ≤ T(μ) := −(2μ)⁻¹ log(1 − μδ²/4) ≤ (δ²/8)·(1 + μδ²/(8(1 − μδ²/4))) ≤ (δ²/8)(1 + μδ²/4).

In the source's notation A N² := Θ S\*(0): D = (δ²/8)(1 + E) with 0 ≤ E ≤ (AN² + κ₀)δ²/4, no hidden
constants, valid whenever (AN² + κ₀)δ² ≤ 2. (T(μ) itself is finite for μδ² < 4.)

*Proof.* Step 1 (g stays ≤ δ). Let I := [0, D) ∩ [0, δ²/4]. Suppose g(s₁) = δ for some s₁ ∈ I with
g ≤ δ on [0, s₁]. By Proposition 4.1, (W) and (3.1) at g = δ,
g′(s₁) ≤ −4/δ + κ₀δ + ΘS\*(0)δ = (μδ² − 4)/δ ≤ −2/δ < 0 by (M). Hence g < δ immediately after any
such time and, since g(0) = δ, g ≤ δ on all of I.

Step 2 (a linear inequality for v := g²). On I, by Step 1, Proposition 4.1, (W), (3.1):
g′ ≤ −4/g + μg, so v′ = 2gg′ ≤ −8 + 2μv, i.e. (v e^{−2μs})′ ≤ −8e^{−2μs}. Integrating from 0,

  v(s) ≤ u(s) := 4/μ − (4/μ − δ²) e^{2μs}   for s ∈ I.                                     (4.1)

(No comparison lemma is needed: the inequality is linear in v.)

Step 3 (collision time). By (M), 4/μ − δ² > 0, so u decreases from δ² and vanishes exactly at
T(μ) = (2μ)⁻¹ log[(4/μ)/(4/μ − δ²)] = −(2μ)⁻¹ log(1 − μδ²/4). Put y := μδ²/4 ≤ ½. Since
−log(1 − y) ≤ y/(1 − y), T(μ) ≤ (δ²/8)/(1 − y) ≤ δ²/4, so T(μ) ∈ [0, δ²/4]. If D > T(μ) then
T(μ) ∈ I and (4.1) gives g(T(μ))² ≤ u(T(μ)) = 0, a collision at time T(μ) < D: contradiction.
Hence D ≤ T(μ). The lower bounds are Lemma 2 + Theorem A of the source (or (3.2) applied to the
minimal gap: g² ≥ δ² − 8s).

Step 4 (the two displayed expansions). −log(1 − y)/y = Σ_{n≥0} yⁿ/(n+1) ≤ 1 + (y/2)Σ_{n≥0} yⁿ =
1 + y/(2(1 − y)), and y/(2(1 − y)) ≤ y for y ≤ ½. ∎

**Check of the constant and of the direction of integration.** Separating the comparison equation
G′ = −4/G + μG: ds = −G dG/(4 − μG²), and s runs from 0 (G = δ) to T (G = 0), so
T = ∫_0^δ G dG/(4 − μG²) = −(2μ)⁻¹[log(4 − μG²)]_0^δ = −(2μ)⁻¹ log(1 − μδ²/4) — the source's formula
with AN² replaced by μ. Its series is (δ²/8)(1 + μδ²/8 + μ²δ⁴/48 + …), matching the source's
"(δ²/8)(1 + AN²δ²/8 + …)". So the source's closed form was right *for its comparison equation*; what
was wrong or missing were (i) the input S (must be S\*), (ii) the O(g) term (must be κ₀g, and it
enters μ additively: AN² → AN² + κ₀, a 1% effect at N = 16, negligible for large N), and (iii) the
meaning of "throughout the collision window" (§5).

**A different pair colliding first.** D is the first collision of *any* pair. The proof only uses
the gap of (a, b) on [0, D). If some other pair collides at D ≤ T(μ) there is nothing to prove; if
D > T(μ) the argument shows (a, b) itself collides by T(μ), contradiction. So the upper bound
D ≤ T(μ) holds regardless of which pair collides first, and the hypothesis (W) is only needed on
[0, D), whichever pair ends the window. The identity of the colliding pair matters for nothing in
Theorem B′; it matters for the numerics of §7 only in that S\*(s) as seen from (a, b) can blow up
when a *neighbour* of a or b is the one that collides (lattice configurations, Table 3).

**Remark (sharper variants).** (i) With S_avg or S_exact in place of S\* in (W) the same proof
gives the same conclusion with the smaller μ; (ii) if one knows S\*(s) ≤ Σ(s) for an explicit
increasing Σ, the linear inequality v′ ≤ −8 + 2(Σ(s) + κ₀)v integrates to
v(s) ≤ δ² e^{2∫₀ˢ(Σ+κ₀)} − 8∫₀ˢ e^{2∫_σ^s(Σ+κ₀)} dσ, which is what one would use to remove the
factor Θ; not pursued.

## 5. (c) What "S\*(s) ≤ AN² throughout the window" needs

### 5.1 Static bound at s = 0 from a local density hypothesis

Let r := min_{k≠a,b} ρ_k > 0 (note r ≥ δ) and N_ab(ρ) := #{k ∉ {a, b} : ρ_k ≤ ρ}.

**Lemma S (static bound) [P].** Suppose N_ab(ρ) ≤ CNρ + m₀ for all ρ ∈ [r, π] (C > 0, m₀ ≥ 0). Then

  **S\*(0) ≤ N/2 + 4CN/r + 2m₀/r²  =  N²·[ 1/(2N) + 4C/(Nr) + 2m₀/(Nr)² ]**   (layer cake),

and the dyadic-shell argument gives the slightly weaker S\*(0) ≤ N/2 + 8CN/r + (8/3)m₀/r².

*Proof.* By Lemma 0 and (I2), S\*(0) = ½Σ csc²(ρ_k/2) ≤ 2Σ_k ρ_k⁻² + (N − 2)(½ − 2/π²).
Layer cake: for each k, ρ_k⁻² = π⁻² + ∫_{ρ_k}^π 2t⁻³ dt, so summing and exchanging sum and integral,
Σ_k ρ_k⁻² = (N − 2)π⁻² + ∫_r^π 2t⁻³ N_ab(t) dt ≤ (N − 2)π⁻² + 2CN(1/r − 1/π) + m₀(1/r² − 1/π²)
≤ (N − 2)/π² + 2CN/r + m₀/r². Insert: S\*(0) ≤ 2(N − 2)/π² + 4CN/r + 2m₀/r² + (N − 2)(½ − 2/π²)
= (N − 2)/2 + 4CN/r + 2m₀/r². Dyadic shells: Ω_m := {k : 2^m r ≤ ρ_k < 2^{m+1}r}, m ≥ 0, cover all k;
#Ω_m ≤ N_ab(min(2^{m+1}r, π)) ≤ 2^{m+1}CNr + m₀ (the hypothesis at min(2^{m+1}r, π) and monotonicity), and
ρ_k⁻² ≤ 4^{−m}r⁻² on Ω_m; so Σρ_k⁻² ≤ Σ_m (2^{m+1}CNr + m₀)4^{−m}r⁻² = 4CN/r + (4/3)m₀/r². ∎

**Honest dependence.** The 1/(Nr)² term is carried *only* by the m₀ exceptional points allowed by
the hypothesis, and it cannot be removed: a single root at distance r contributes ½csc²(r/2) ≥ 2/r²
= 2N²/(Nr)² by itself. The density part contributes linearly in 1/(Nr). Under the task's reading of
the hypothesis (the "+2" counts θ_a, θ_b themselves, so m₀ = 0 for the other roots) the hypothesis at
ρ = r already forces 1 ≤ N_ab(r) ≤ CNr, i.e. **Nr ≥ 1/C**, and then

  S\*(0) ≤ N/2 + 4C²N² = N²(4C² + 1/(2N)).

Calibration at the clock (r = 2π/N, N_ab(ρ) = 2⌊ρN/2π⌋ ≤ ρN/π, so C = 1/π, m₀ = 0): the bound gives
S\*(0) ≤ 2N²/π² + N/2 = 0.2026N² + N/2 against the exact (N² − 1)/6 = 0.1667N², so Lemma S loses only
a factor ≈ 1.2 in the density term.

### 5.2 Window stability from the unconditional gap bound

The task suggested controlling S\*(s) through velocity bounds |θ_k′| for the background roots. That
route works but needs a *global* density hypothesis (around every θ_k, not only around the pair) and
loses a logarithm; it is recorded in §9. The following route is cleaner and uses only (3.2), which
is unconditional. Its key point is structural: **the fast motion of the pair is directed inward and
therefore only increases every ρ_k**, and every arc from the pair to another root is a sum of gaps,
each of which obeys (3.2).

By (1.4) the midpoint c := (θ_a + θ_b)/2 has c′ = ½Σ_k[cot(y_k/2) − cot(w_k/2)], so
|c′| ≤ 2Σ_{k≠a,b} 1/ρ_k (using |cot(t/2)| ≤ 2/dist(t) and y_k, w_k ≥ ρ_k in circular distance): the
midpoint moves at background speed, while θ_a = c + g/2 and θ_b = c − g/2 carry the fast part ∓g′/2,
which increases y_k = θ_k − c − g/2 and w_k = c − g/2 + 2π − θ_k as g decreases. This is the
quantitative form of "the pair moves fast but harmlessly"; we do not need it below because the gap
formulation absorbs it.

For k ∉ {a, b}, y_k(s) = Σ_{i∈A_k} g_i(s) and w_k(s) = Σ_{i∈A′_k} g_i(s), where A_k (resp. A′_k) is the
fixed set of cyclic gaps on the arc from θ_a counter-clockwise to θ_k (resp. from θ_k to θ_b); these
are the **pair-anchored arcs**, and neither contains the pair gap. For τ > 0 define the shrinkage factor

  ψ(τ) := min over all pair-anchored arcs A of  Σ_{i∈A} (g_i(0)² − 8τ)₊^{1/2} / Σ_{i∈A} g_i(0)  ∈ [0, 1].

**Lemma W (window stability) [P].** For every s ∈ [0, D) with s ≤ τ and every k ∉ {a, b},
ρ_k(s) ≥ ψ(τ)ρ_k(0); consequently, if ψ(τ) > 0,

  **S\*(s) ≤ S\*(0)/ψ(τ)²  for all s ∈ [0, D) ∩ [0, τ].**

*Proof.* By (3.2), g_i(s) ≥ (g_i(0)² − 8s)₊^{1/2} ≥ (g_i(0)² − 8τ)₊^{1/2}; summing over A_k gives
y_k(s) ≥ ψ(τ)y_k(0), likewise w_k(s) ≥ ψ(τ)w_k(0), hence ρ_k(s) = min(y_k(s), w_k(s)) ≥ ψ(τ)ρ_k(0).
Since ρ_k(s) < π and csc²(·/2) is decreasing on (0, π], csc²(ρ_k(s)/2) ≤ csc²(ψρ_k(0)/2) ≤
ψ⁻²csc²(ρ_k(0)/2) by (I3). Sum over k and use Lemma 0. ∎

Two sufficient conditions at s = 0, with τ = δ²/4 (so 8τ = 2δ²):

**Corollary W1 [P].** If every cyclic gap other than the pair gap is ≥ Lδ at s = 0, with L > √2, then
ψ(δ²/4) ≥ (1 − 2/L²)^{1/2} and S\*(s) ≤ S\*(0)/(1 − 2/L²) on [0, D) ∩ [0, δ²/4]. For L = 2: **Θ = 2**.
*Proof.* (g_i² − 2δ²)^{1/2} = g_i(1 − 2δ²/g_i²)^{1/2} ≥ g_i(1 − 2/L²)^{1/2} termwise. ∎

**Corollary W2 (one-sided density) [P].** Assume

  (H_C) for every n ≥ 1 and on each side of the pair, the n cyclic gaps nearest to the pair span an arc of length ≥ n/(CN)

(equivalently #{k : y_k ≤ ρ} ≤ CNρ and #{k : w_k ≤ ρ} ≤ CNρ for all ρ). If √2·CNδ ≤ 1 − 1/√2, i.e.
**CNδ ≤ 0.2071**, then ψ(δ²/4) ≥ 1/√2 and **Θ = 2**.
*Proof.* For any gap, the loss over the window is g_i(0) − (g_i(0)² − 2δ²)₊^{1/2} ≤ min(g_i(0), 2δ²/g_i(0)) ≤ √2δ
(if g_i² ≥ 2δ² the loss is 2δ²/(g_i + (g_i² − 2δ²)^{1/2}) ≤ 2δ²/g_i ≤ √2δ; otherwise it is ≤ g_i < √2δ).
An arc of n gaps therefore loses at most n√2δ ≤ √2·CNδ·(its length) by (H_C), so ψ ≥ 1 − √2CNδ ≥ 1/√2. ∎

**Remark (the two hypotheses fit together).** (H_C) implies N_ab(ρ) ≤ 2CNρ (m₀ = 0) and r ≥ 1/(CN), so
Lemma S gives S\*(0) ≤ N/2 + 8CN/r ≤ N/2 + 8C²N². Thus a *single* time-0 hypothesis — one-sided
density with constant C near the min-gap pair — controls both the size of S\*(0) and its growth over
the window; the only other input is CNδ ≤ 0.2.

**The task's version is false as stated [R].** "S\* changes by a factor ≤ 2 over the window when
D ≤ δ²/4 and Nδ ≤ 1" fails without a separation hypothesis on the *neighbouring* gaps: with N = 8,
δ = 0.02, roots at 0, δ, (2 + t)δ and five roots spread over the rest of the circle, the neighbour gap
(1 + t)δ shrinks almost as fast as δ itself, and sup_{[0,D]} S\*(s)/S\*(0) = 1.62, 3.43, 9.51 for
t = 0.2, 0.05, 0.01 (script, item [CLUSTER3]; Nδ = 0.16 ≤ 1 and D ≤ 0.17δ² in all three). Note the
pair (a, b) still collides first in these examples, so this is not the trivial blow-up caused by a
neighbour colliding. The mechanism is exactly the one Lemma W quantifies: ψ(δ²/4) is small because
the arc a→k consists of a single gap of size (1 + t)δ < 2δ. The condition Nδ ≤ 1 by itself does not
constrain the nearest gap, and the true sufficient condition is W1/W2.

### 5.3 What the lattice endpoint looks like in this language

For ACUE every non-clock configuration has δ = π/N (Lemma 3 of the source) and typically other gaps
equal to δ as well, so W1 fails (L = 1), (H_C) holds only with C = 1/π and then CNδ = 1 > 0.2, and
(M) fails at the natural scale (S\*(0) ≈ 0.3N² gives μδ² ≈ 2·0.3·π² ≈ 6 > 2 with Θ = 2; even Θ = 1
gives ≈ 3). Theorem B′ is therefore silent for ACUE — as it must be, since there the background is
a leading-order effect (ρ_∞ ≠ 1, source §7). The numerics of §7 show what actually happens: S\*(s)
grows over the window by a median factor 1.35–1.5 (90th percentile 2.5–2.9); in 90–95% of random
lattice configurations a *different* pair collides first (many gaps tie at π/N), and when that pair is
adjacent to (a, b) the growth is unbounded (5.8·10⁹ observed at N = 16); the un-doubled closed form
T(S\*(0) + κ₀) is finite in 74–79% of samples and then bounds D with slack between 0.6% and a factor
4.9 (median ≈ 1.5).

## 6. Fully explicit corollary (the CUE-type regime)

**Corollary 6.1 [P].** Let N ≥ 3, (a, b) a minimum-gap pair, δ = δ_min. Assume (H_C) with constant C,
CNδ ≤ 0.2 and Nδ ≤ 1. Then

  **δ²/8 ≤ −log cos(δ/2) ≤ D ≤ (δ²/8)·(1 + 4C²N²δ² + 0.29δ).**

*Proof.* Lemma S with N_ab ≤ 2CNρ, m₀ = 0, r ≥ 1/(CN): S\*(0) ≤ N/2 + 8C²N². Corollary W2 (√2·0.2 <
0.2929): Θ = 2. So μ ≤ N + 16C²N² + κ₀ and, using δ ≤ 1/N ≤ 1/3 and κ₀ ≤ 4/π²,
μδ² ≤ Nδ² + 16(CNδ)² + κ₀δ² ≤ 1/3 + 0.64 + 0.046 < 2: (M) holds. Theorem B′:
D ≤ (δ²/8)(1 + μδ²/4) ≤ (δ²/8)(1 + 4C²N²δ² + Nδ²/4 + κ₀δ²/4) and Nδ²/4 ≤ δ/4, κ₀δ²/4 ≤ (4/π²)(δ/3)/4 ≤ 0.034δ. ∎

For CβE with δ ≍ N^{−1−1/(β+1)} (Feng–Wei; Ben Arous–Bourgade for β = 2 — recalled from the source,
not verified online tonight) the error term is 4C²N²δ² ≍ C²N^{−2/(β+1)} + O(δ), which is the source's
claimed rate with an explicit constant, **provided** (H_C) holds with C = O(1) and CNδ ≤ 0.2 with
probability → 1. That is the regularity hypothesis, now in static form (§8).

## 7. (d) Numerics [C]

**Script.** `research/riemann-rmt/overnight/fable/scripts/r1_theoremB_check.py` (docstring at the top
describes every quantity). **Command:** `python3 r1_theoremB_check.py --n-cue 300 --n-acue 100 --n-cert 5 --seed 1`
(wall time ≈ 6 min on one core). **Data:** `research/riemann-rmt/overnight/fable/data/r1_theoremB_check.json`
(summaries + one record per sample) and `…/data/r1_theoremB_check.log` (the tables below verbatim).

**Method.** CUE = eigenangles of Haar unitaries (QR of complex Ginibre with the Mezzadri phase
correction), N = 16, 32, 64, 300 samples each. ACUE = uniformly random non-clock N-subsets of the 2N-th
roots of unity, N = 16, 32, 64, 100 samples each, plus the single-dislocation configuration
(clock with one root moved by one slot) at N = 8, 16, 32, 64, plus the adversarial 3-clusters of §5.2.
For the minimum-gap pair the script computes B, S_old, S\*, S_avg, S_exact at s = 0. The depth D is
obtained by integrating Lemma 1's ODE with DOP853 (rtol 10⁻¹², atol 10⁻¹⁵) up to the terminal event
"minimum gap = 10⁻⁵δ", then adding the exact two-body residual −log cos(g_end/2) (relative effect
10⁻¹⁰; by (I4) this residual is a lower bound for the true one, so the truncation can only *under*-
estimate D, by a relative 10⁻¹⁰). Three independent checks of D: (i) re-integration with rtol 10⁻¹³ and
event 10⁻⁶δ (column "tight": max relative difference); (ii) `dyn1_core.find_ustar`, the source's
polynomial method (column "ode/poly"; usable only for N ≤ 32, see §9 item 5 — at N = 32 the 10⁻⁴
discrepancies are on the polynomial side, whose s = 0 roots are already 10⁻⁸ off the circle there);
(iii) for the first five samples of each ensemble, a 60-digit certificate: all roots of P_s unimodular
to < 10⁻¹² at s = D(1 − 10⁻⁶) and some root > 10⁻⁸ off the circle at s = D(1 + 10⁻⁶) (column "mp-cert";
the observed values are ≤ 10⁻²⁴ and ≥ 10⁻⁵ respectively). Along the ODE trajectory S\*(s) of the initial
pair is evaluated at every accepted step (dense near the end) and its supremum recorded. Closed forms:
T(μ) = −log(1 − μδ²/4)/(2μ), reported for μ_emp = S\*(0) + κ₀ (no window factor), μ_rig = 2S\*(0) + κ₀
(Θ = 2, the rigorous value under W1/W2), μ_sup = sup_{[0,D)} S\*(s) + κ₀ (the exact hypothesis of Theorem
B′ with the true window factor, so D ≤ T(μ_sup) must hold whenever it is finite — this tests the whole
chain Lemma 1 → (2.2) → (3.1) → (4.1)). "vac" = fraction of samples where μδ² ≥ 4 and T = ∞.

**Item [1] — Astra's counterexample reproduced.** quotient 133.500132, old term 89.055743 (fails),
S\*-term 200.166750, S_avg-term 144.611247, identity (2.1) = 133.500132 (|difference| 5·10⁻¹³).

**Table 1 — the background bracket at s = 0 for the minimum-gap pair.**

| ensemble | n | old bound fails | max B/(g S_old) | S\* bound fails | min g S\*/B | min g S_avg/B | min g S_exact/B | max \|B − 2sin(g/2)S_exact\|/B | median S\*/N² | median S_old/N² |
|---|---|---|---|---|---|---|---|---|---|---|
| CUE N=16 | 300 | 48.7% | 1.4725 | 0 | 1.0152 | 1.0002 | 1.000008 | 8.7e-15 | 0.1378 | 0.1148 |
| CUE N=32 | 300 | 43.7% | 1.3577 | 0 | 1.0199 | 1.0002 | 1.000004 | 7.0e-14 | 0.1433 | 0.1206 |
| CUE N=64 | 300 | 44.0% | 1.4642 | 0 | 1.0210 | 1.0003 | 1.000001 | 2.7e-14 | 0.1331 | 0.1149 |
| ACUE N=16 | 100 | 40.0% | 1.4722 | 0 | 1.0876 | 1.0064 | 1.001608 | 1.8e-15 | 0.3276 | 0.1757 |
| ACUE N=32 | 100 | 40.0% | 1.5481 | 0 | 1.1145 | 1.0079 | 1.000402 | 6.0e-16 | 0.3013 | 0.1694 |
| ACUE N=64 | 100 | 34.0% | 1.5745 | 0 | 1.1220 | 1.0089 | 1.000100 | 9.6e-16 | 0.3237 | 0.1633 |

Reading: the source's bound is violated in 34–49% of configurations, by up to 57%; the repaired bounds
never fail (as they cannot — they are theorems), and the chain B ≤ gS_exact ≤ gS_avg ≤ gS\* is tight to
10⁻⁶, 3·10⁻⁴ and 2% respectively for CUE. The source's "median S/N² ≈ 0.12" was measured with S_old;
the correct quantity S\* has median 0.13–0.14 N² for CUE (clock value 1/6) and ≈ 0.32 N² for ACUE.

**Table 2 — depth D against the bounds.**

| ensemble | n | ode/poly | mp-cert | tight | D/(δ²/8) min | median | max | D/(−log cos(δ/2)) min | median N²δ² | T(μ_emp)/D min | vac | T(μ_rig)/D min | vac | T(μ_sup)/D min | violations |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CUE N=16 | 300 | 2.2e-8 | 5/5 | 3.4e-11 | 1.00051 | 1.06794 | 1.59217 | 1.000502 | 4.19 | 1.00001 | 0% | 1.00052 | 8% | 1.00001 | 0 |
| CUE N=32 | 300 | 1.2e-4† | 5/5 | 6.2e-11 | 1.00114 | 1.04757 | 1.26711 | 1.001138 | 2.95 | 1.00002 | 0% | 1.00119 | 1% | 1.00002 | 0 |
| CUE N=64 | 300 | n/a | 5/5 | 2.1e-10 | 1.00137 | 1.02806 | 1.19939 | 1.001365 | 1.78 | 1.00003 | 0% | 1.00143 | 0% | 1.00003 | 0 |
| ACUE N=16 | 100 | 1.2e-10 | 5/5 | 1.3e-11 | 1.05458 | 1.12346 | 1.57965 | 1.052885 | 9.87 | 1.00596 | 25% | 1.07720 | 70% | 1.00596 | 0 |
| ACUE N=32 | 100 | fails† | 5/5 | 2.3e-11 | 1.05058 | 1.10746 | 1.20730 | 1.050160 | 9.87 | 1.00830 | 21% | 1.09028 | 67% | 1.00830 | 0 |
| ACUE N=64 | 100 | n/a | 5/5 | 2.7e-11 | 1.04150 | 1.08324 | 1.14404 | 1.041392 | 9.87 | 1.00844 | 26% | 1.08854 | 69% | 1.00844 | 0 |

† polynomial side (double-precision `np.roots`), see §9 item 5. Reading: Theorem A (ρ ≥ 1) holds in
every sample with minimum ratio 1.0005; **D ≤ T(μ_sup) in every sample** (0 violations, minimum slack
10⁻⁵ at N = 16, far above the 10⁻¹⁰ numerical uncertainty); the un-doubled closed form T(μ_emp) also
bounds D in every sample where it is finite, with slack as small as 10⁻⁵ — i.e. for typical CUE
configurations S\*(0)·δ²/8 is essentially the *exact* first correction; the rigorous Θ = 2 version is
vacuous only where N²δ² is large (N = 16), and in every CUE sample where its hypotheses (W1 or W2)
hold it is finite and valid, with minimum slack T(μ_rig)/D = 1.0005, 1.0012, 1.0014 at N = 16, 32, 64.
For ACUE T(μ_emp) is finite in 74–79% of samples and then bounds D with slack between 0.6% and a
factor 4.9 (median ≈ 1.5); T(μ_rig) is mostly vacuous, as §5.3 predicts.

**Table 3 — growth of S\* over the window and the hypotheses of §5.**

| ensemble | n | S\*_sup/S\*(0) median | q90 | max | frac > 2 | frac W1 (g₍₂₎ ≥ 2δ) | max ratio given W1 | frac (H_C)+√2CNδ≤0.29 | max ratio given it | median g₍₂₎/δ | median C | max C | median N·r | pair (a,b) collides first |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CUE N=16 | 300 | 1.0000 | 1.034 | 3.208 | 1.3% | 15.0% | 1.000 | 10.3% | 1.000 | 1.30 | 0.186 | 0.459 | 6.09 | 96.7% |
| CUE N=32 | 300 | 1.0000 | 1.000 | 1.612 | 0.0% | 17.0% | 1.000 | 17.3% | 1.000 | 1.32 | 0.187 | 0.588 | 5.90 | 100% |
| CUE N=64 | 300 | 1.0000 | 1.000 | 1.318 | 0.0% | 9.3% | 1.000 | 29.0% | 1.000 | 1.32 | 0.181 | 0.513 | 6.36 | 98.7% |
| ACUE N=16 | 100 | 1.48 | 2.70 | ∞ (5.8e9) | 35% | 0% | — | 0% | — | 1.00 | 0.318 | 0.318 | 3.14 | 9% |
| ACUE N=32 | 100 | 1.35 | 2.92 | 3.54 | 30% | 0% | — | 0% | — | 1.00 | 0.318 | 0.318 | 3.14 | 10% |
| ACUE N=64 | 100 | 1.37 | 2.47 | 3.42 | 30% | 0% | — | 0% | — | 1.00 | 0.318 | 0.318 | 3.14 | 5% |

Here C is the empirical one-sided density constant C_emp = max_n n/(N·y₍ₙ₎) over both sides, so (H_C)
holds with C = C_emp by definition and the column tests only √2·C_emp·Nδ ≤ 1 − 1/√2. Reading: whenever
either sufficient condition of §5.2 holds, S\* does not grow at all (max ratio 1.000 — in fact it
decreases, because the pair's inward motion pushes the neighbours away), consistent with and much
stronger than Lemma W's factor 2. The conditions themselves hold in only 9–29% of CUE samples at these
N because Nδ_min ≈ 1.3–2 there (N^{−1/3} decay is slow: median N²δ² = 4.2, 3.0, 1.8): the asymptotic
regime CNδ ≤ 0.2 is not reached by N = 64. Growth beyond 2 occurs only in 1.3% of CUE samples (all at
N = 16, with g₍₂₎/δ = 1.02–1.06, i.e. exactly the 3-cluster mechanism) and in 30–35% of lattice
samples; it is unbounded when the colliding pair is adjacent to (a, b) (5.8·10⁹ at N = 16). Among
lattice samples in which (a, b) itself collides first, the ratio never exceeds 1.0 at N = 32, 64.

**Single dislocation (clock with one root moved by one slot).** N²D = 1.419558, 1.419635, 1.419640,
1.419640 at N = 8, 16, 32, 64 (certified to 10⁻⁶), i.e. D/(π²/8N²) → 1.15072, reproducing the source's
constant 1.150717…; S\*(0)/N² = 0.1229 → 0.1306; S\* does not grow over the window (ratio 1.000); the
un-doubled closed form gives T(μ_emp)/D = 1.0445 → 1.0491 (μ_emp δ² ≈ 1.29 < 2), so here the repaired
Theorem B′ with the *true* window factor Θ = 1 bounds the lattice constant within 5%.

**Adversarial 3-clusters (N = 8, δ = 0.02, neighbour gap (1+t)δ).** t = 0.2, 0.05, 0.01:
D/(δ²/8) = 1.148, 1.232, 1.291; S\*_sup/S\*(0) = 1.62, 3.43, 9.52; the pair collides first in all three;
T(μ_rig)/D = 1.49, 2.14, 3.16 (still valid bounds since the growth is < Θ = 2 only in the first case —
in the other two, (W) with Θ = 2 is false and the bound holds by accident); T(μ_sup) = ∞ in the last two
(μ_sup δ² > 4). This is the witness for §5.2's [R].

## 8. What remains open [O]

**(O1) The regularity hypothesis for CβE, now in static form.** Theorem B′ + Corollaries 6.1/W2 reduce
the source's "S(s) ≤ AN² throughout the collision window" to two statements about the configuration
at s = 0 only: (H_C) one-sided density near the minimum-gap pair with C = O(1), and CNδ_min ≤ 0.2.
For CUE the second is δ_min ≍ N^{−4/3} (Ben Arous–Bourgade, recalled; not verified online) and the
first is a rigidity statement conditional on the location of the minimum gap. Both are expected to hold
with probability → 1, but nothing here proves it; this is the input `r1_cue_background.md` is meant
to supply from the determinantal 3-point estimate. Obstruction: (H_C) is a statement about *all* n
simultaneously, i.e. about the whole one-sided counting function anchored at a random (extremal)
point; the n = 1 case (nearest neighbour gap ≥ 1/(CN)) is a small-gap-near-a-smaller-gap estimate,
and the large-n cases are the usual rigidity, but the union over n and the conditioning on the
extremal pair have to be handled explicitly.

**(O2) The window factor.** Θ = 2 is far from what is observed for CUE (Table 3: S\*_sup/S\*(0) has
median 1.000 and never exceeds 2 under (H_C)); in fact the pair's inward motion typically makes S\*
*decrease*. A time-dependent version of Lemma W (remark after Theorem B′) would remove most of the
factor 2, at the price of a less transparent statement. Not done.

**(O3) The lattice endpoint.** For ACUE the hypotheses of Theorem B′ fail at the natural scale (§5.3)
and the theorem is silent; the numerics show the un-doubled closed form is finite in ~75% of random
lattice configurations and then bounds D with 0.6–10% slack, but this is unproved and cannot be
proved by this route: in 90–95% of lattice samples a different pair collides first, and when it is
adjacent to (a, b) S\*(s) → ∞ on the window. The lattice needs a different argument for ρ_∞ = O(1)
(source §6(iii)),
e.g. one that tracks the colliding *cluster* rather than a pair.

**(O4) Sharpness of the constant.** Whether D ≤ (δ²/8)(1 + c·S\*(0)δ²) holds with c = 1/8 (the
source's series coefficient) rather than the 1/2 proved here (Θ = 2 and −log(1−y)/y ≤ 1 + y) is not
settled; numerically T(S\*(0) + κ₀)/D ≥ 1.00001 in every CUE sample, consistent with c = 1/8 being
the truth for typical configurations, but the 3-cluster examples show that some window factor is
necessary in general.

## 9. Failed attempts (recorded so nobody repeats them)

1. **Keeping the source's S.** Impossible: the endpoint-left bound is false on the increasing branch of
   csc²(t/2); Astra's example is the minimal counterexample and about half of all random
   configurations violate it (Table 1).
2. **Proving the factor-2 window bound from "D ≤ δ²/4 and Nδ_min ≤ 1" alone.** False: the
   3-cluster family of §5.2 has Nδ = 0.16, D ≤ 0.17δ², and S\*_sup/S\*(0) = 9.5. The nearest gap must be
   controlled; W1/W2 are the honest sufficient conditions.
3. **The velocity route suggested in the task.** Bounding |θ_k′| ≤ Σ_{j≠k} 2/dist(θ_k, θ_j) needs a
   density hypothesis around *every* k (a global statement), and under a linear density bound it gives
   |θ_k′| ≤ 2CN log(π/r_k) + 2m₀/r_k, so the displacement over a window of length δ²/4 is
   ≲ δ²(CN log(π/r) + m₀/r); making this ≤ ηr requires δ log(1/r) ≪ r, a logarithm worse than W2 and
   with a global hypothesis. The pair's own motion is harmless (midpoint at background speed, fast part
   inward — §5.2), so the difficulty was never the pair; it was the background. Superseded by Lemma W.
4. **Using S_exact in Lemma W.** The factor sin(y_k/2) sin(w_k/2) is not monotone in the arcs (y_k/2
   can exceed π/2), so the clean ψ⁻² argument does not go through verbatim; since S_exact ≤ S\*, using
   S\* in (W) costs nothing in the theorem's form. Abandoned.
5. **Double-precision polynomial root-finding as the ground truth at N = 64.** `np.roots` puts the
   s = 0 roots 10⁻² off the unit circle for degree 64 (companion-matrix conditioning), so
   `dyn1_core.find_ustar` cannot be used beyond N ≈ 32 (Table 2, column ode/poly); replaced by the
   40-digit certificate.
6. **A first version of the 40-digit certificate.** It formed the flow exponent as the double product
   `u*j*(N-j)`; `(u*j)*(N-j)` and `(u*(N-j))*j` differ by an ulp, which breaks self-inversiveness of
   P_s at the 10⁻¹¹ level and, divided by |P′| ≈ 10⁻⁸ at a 16-root lattice cluster, threw roots 10⁻⁴
   off the circle *before* the collision. Diagnosed by the pairing test (off-circle roots of a
   self-inversive polynomial must come in (z, 1/z̄) pairs; these did not) and fixed by forming the
   exponent in multiprecision from the exact integer j(N−j). Recorded because the same bug would
   silently corrupt any high-precision re-implementation of the flow.
7. **ODE tolerance.** rtol = 10⁻¹⁰ was insufficient for lattice configurations with a collapsing
   multi-root cluster (relative error 2·10⁻⁶ in D, detected by the certificate); rtol = 10⁻¹² and
   10⁻¹³ agree to 10⁻¹⁰ and pass the certificate at relative width 10⁻⁶.

## 10. Claim ledger for this file

| id | claim | status | where |
|---|---|---|---|
| A1.1 | cot(x/2) − cot((x+g)/2) = sin(g/2)/(sin(x/2) sin((x+g)/2)); B = 2 sin(g/2)·S_exact | P | §2, Prop. 2.1, (2.1) |
| A1.2 | 0 ≤ B ≤ g·S\*, S\* = Σ ½max(csc²(x_b^k/2), csc²(x_a^k/2)) = ½Σ csc²(ρ_k/2); also B ≤ g S_exact ≤ g S_avg ≤ g S\* | P | §2, Prop. 2.2–2.3, Lemma 0 |
| A1.3 | the source's bound B ≤ g·S_old is false (Astra's example; fails in 34–49% of sampled configurations) | R | §2, §7 Table 1 |
| A1.4 | −4/g ≤ −2cot(g/2) ≤ −4/g + κ(δ/2)g for 0 < g ≤ δ ≤ π, κ increasing, κ ∈ (1/3, 4/π²] | P | §3 (I1) |
| A1.5 | Theorem B′: under (W) window factor Θ and (M) μδ² ≤ 2, μ = ΘS\*(0)+κ₀: −log cos(δ/2) ≤ D ≤ −(2μ)⁻¹log(1−μδ²/4) ≤ (δ²/8)(1+μδ²/4); holds whichever pair collides first | P | §4 |
| A1.6 | Lemma S: N_ab(ρ) ≤ CNρ + m₀ on [r, π] ⇒ S\*(0) ≤ N/2 + 4CN/r + 2m₀/r²; with m₀ = 0, Nr ≥ 1/C and S\*(0) ≤ N²(4C² + 1/(2N)) | P | §5.1 |
| A1.7 | Lemma W: S\*(s) ≤ S\*(0)/ψ(τ)² on [0,D)∩[0,τ], ψ from the unconditional gap bound g_i(s)² ≥ g_i(0)² − 8s | P | §5.2 |
| A1.8 | Θ = 2 on [0, δ²/4] if all other gaps ≥ 2δ (W1), or under (H_C) with CNδ ≤ 0.2071 (W2) | P | §5.2 |
| A1.9 | "S\* changes by ≤ 2 when D ≤ δ²/4 and Nδ ≤ 1" is false without a neighbour-gap hypothesis (3-cluster, ratio 9.5) | R + C | §5.2, §7 |
| A1.10 | Corollary 6.1: (H_C), CNδ ≤ 0.2, Nδ ≤ 1 ⇒ δ²/8 ≤ D ≤ (δ²/8)(1 + 4C²N²δ² + 0.29δ) | P | §6 |
| A1.11 | numerics: identities to 10⁻¹⁴; S\* bound never fails; D ≤ T(sup S\* + κ₀) in every sample; ODE depths certified to 10⁻⁶ by 40-digit brackets | C | §7, `scripts/r1_theoremB_check.py`, `data/r1_theoremB_check.json` |
| A1.12 | regularity hypothesis for CβE reduced to static (H_C) + CNδ ≤ 0.2 w.h.p.; unproved | O | §8 |
| A1.13 | lattice endpoint: Theorem B′ silent; ρ_∞ = O(1) needs a cluster argument | O | §5.3, §8 |
