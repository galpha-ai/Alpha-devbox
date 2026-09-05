# r1 — The CUE background bound holds with high probability (task A2)

**Fable overnight harness, 2026-09-05.** Deliverable for cluster A (depth-rigor), task A2.
Companion files: `depth_scaling_theorem.md` (Lemmas 1–3, Theorems A/B/C), the Astra audit
(`handoff/astra-2026-09-05/COORDINATION.md`, item "background endpoint bound"), and task A1's
`r1_theoremB_repair.md` (repaired Theorem B; not read here — it is used only through the explicit
Assumption B\* stated in §6).

Scripts: `overnight/fable/scripts/r1_cue_background_constants.py` (exact identities, global
inequalities, constant assembly; 14/14 checks pass) and `overnight/fable/scripts/r1_cue_background_mc.py`
(CUE Monte Carlo, N = 64, 128, 256). Data: `overnight/fable/data/r1_cue_background_constants.json`,
`r1_cue_background_mc.json`, `r1_cue_background_mc_samples.npz`, `r1_cue_background_mc.log`.

Status tags: **[P]** proved here in full; **[C]** computed (script + data); **[R]** refuted/repaired;
**[O]** open with the obstruction stated. Citations are marked *(recalled; not verified online)*; no
web access was attempted for this file (the harness brief says it may be blocked; nothing below
depends on a citation except the limit law in Theorem 2, and the constant of that law is re-derived
here at the level of the first moment).

---

## 0. Results at a glance

Let θ_1,…,θ_N be CUE(N) eigenangles, δ_min the smallest cyclic gap, (a,b) its endpoints, and

  **S\*** := Σ_{k≠a,b} ½·max( csc²(x_b^k/2), csc²(x_a^k/2) ),  x_j^k := (θ_j − θ_k) mod 2π ∈ (0,2π),

the *repaired* background stiffness (the endpoint maximum is what the mean value theorem gives; the
Astra audit shows the un-repaired version S = Σ ½csc²(x_b^k/2) is false as an upper bound for the
difference quotient when x_b^k > π).

| # | statement | status |
|---|---|---|
| T1 | **Theorem 1.** For every N ≥ 3 and M ≥ 1, P(S\* > M·N²) ≤ 1055·M^{−1/2}. Uniform in N. | **[P]** §5 |
| T1′ | The shell/Markov route of the task brief gives the weaker P(S\* > M N²) ≤ 1055·M^{−3/8}, also uniform in N, with no log factor. | **[P]** §5 |
| C1 | P(S\* > N² log N) ≤ 1055 (log N)^{−1/2} → 0; more generally P(S\* > ω_N N²) → 0 for any ω_N → ∞. | **[P]** §5 |
| P1 | Exact 3-point structure: ρ_3(x,y,z) = (2π)^{−3} ∏_{i<j}\|z_i−z_j\|² Σ_{m_1<m_2<m_3} \|s_λ(z)\|², hence the **global** bound ρ_3 ≤ C_3(N)∏_{i<j}\|z_i−z_j\|² with C_3(N) = N³(N²−1)²(N²−4)/(69120 π³), sharp as the three points cluster. In density-1 units the clustering constant is π⁶/135 (and π²/3 for ρ_2). | **[P]** §2 |
| P2 | E[#ordered triples (x,y,z): d(x,y) ≤ L N^{−4/3}, dist(z,{x,y}) ≤ c/N] ≤ (4320π²)^{−1}[L³c⁵/15 + L⁴c⁴N^{−1/3}/8 + L⁵c³N^{−2/3}/15]; the exponents are explained (L³ from ∫u² du, c⁵ from ∫v⁴ dv). | **[P]** §4 |
| P3 | Self-contained: P(δ_min > L N^{−4/3}) ≤ 1054/L³ for all N ≥ 2, L > 0 (second moment with ρ_2, ρ_3, ρ_4; Fischer's inequality replaces the ρ_4 asymptotics). First moment: E[#gaps ≤ xN^{−4/3}] = (x³/72π)(1 − N^{−2})(1 + O(x²N^{−2/3})), which pins the constant 72π of the Ben Arous–Bourgade law in our normalisation. | **[P]** §3 |
| T2 | **Theorem 2 (CUE depth law).** N^{8/3} D_N ⇒ G²/8, P(G > x) = exp(−x³/72π). Inputs: Theorem A [P, cited from `depth_scaling_theorem.md`], Assumption B\* (task A1's repaired Theorem B, *assumed*), Ben Arous–Bourgade [C, recalled], and Theorem 1 [P]. Also ρ_N − 1 := 8N^{8/3}D_N/(N^{4/3}δ_min)² − 1 = O_P(N^{−2/3}). | **[P] modulo B\* and the citation** §6 |
| N1 | Monte Carlo (N = 64/128/256; 4000/2000/800 samples): median S\*/N² ≈ 0.13, q99 ≈ 0.45, max ≈ 1.5; fraction with S\* > N² log N is 0 in all 6800 samples; lower tail of N·d_3 consistent with exponent 5 and with the predicted constant c⁵/(3600π) once the midpoint correction is applied. | **[C]** §7 |
| O1 | Theorem 2 uses S\* at s = 0; the repaired Theorem B may need sup_{s ≤ D} S\*(s). A short-time stability lemma (all points move by o(1/N) during the collision window) is stated but not proved. | **[O]** §8 |
| O2 | The true tail of S\*/N² is ≈ (2/M)^{5/2}/(3600π) (exponent 5/2, from the third-point law); the proved exponent 1/2 is lossy because of Markov/Chebyshev on the bulk sum. | **[O]** §8 |

---

## 1. Setting, and the wrap-around done right

**CUE(N).** θ_1,…,θ_N ∈ [0,2π) are the eigenangles of a Haar unitary N×N matrix. The point
process is determinantal with respect to dθ with the projection kernel

  K_N(θ,φ) = sin(N(θ−φ)/2) / (2π sin((θ−φ)/2)) = (1/2π) Σ_{m=0}^{N−1} e^{i(m−(N−1)/2)(θ−φ)},

so that ρ_n(x_1,…,x_n) = det[K_N(x_i,x_j)]_{i,j≤n} are the correlation functions:
E[Σ_{distinct i_1,…,i_n} F(θ_{i_1},…,θ_{i_n})] = ∫ F ρ_n dx. In particular ρ_1 ≡ N/2π. [Standard; the
kernel identity is a geometric sum, checked in the script.]

**Circular distance.** d(θ,φ) := min((θ−φ) mod 2π, (φ−θ) mod 2π) ∈ [0,π]. For k ∉ {a,b} put

  d_k := dist(θ_k, {θ_a, θ_b}) = min(d(θ_k,θ_a), d(θ_k,θ_b)).

**Lemma 1.1 (wrap-around) [P].** For x ∈ (0,2π), csc²(x/2) = csc²(d/2) with d = min(x, 2π−x); the
function x ↦ csc²(x/2) is strictly decreasing on (0,π] and strictly increasing on [π,2π). Consequently

  S\* = Σ_{k≠a,b} ½ csc²(d_k/2),  and  4/d_k² ≤ csc²(d_k/2) ≤ π²/d_k².

*Proof.* sin(x/2) = sin(π − x/2) = sin((2π−x)/2), so csc²(x/2) depends on x only through d.
Monotonicity: (d/dx)csc²(x/2) = −csc²(x/2)cot(x/2), whose sign is −sign(cot(x/2)). For the pair
(a,b) with θ_a = θ_b + δ_min (mod 2π), x_a^k = x_b^k + δ_min, and since csc²(·/2) is decreasing then
increasing on (0,2π), its maximum over the segment [x_b^k, x_a^k] is attained at an endpoint — this is
exactly why the repaired S\* uses the endpoint maximum and why max(csc²(x_b^k/2), csc²(x_a^k/2)) =
csc²(d_k/2): the endpoint nearer to θ_k (in circular distance) wins. A point just *clockwise* of θ_a
has x_a^k close to 2π, hence d_k = 2π − x_a^k small, and is captured. The inequalities: sin(t) ≥ 2t/π
on [0,π/2] (concavity) gives csc²(d/2) ≤ π²/d²; sin t ≤ t gives csc²(d/2) ≥ 4/d². ∎

(Both identities are also checked numerically: the Monte Carlo script computes S\* literally from the
definition with x_j^k mod 2π and asserts equality with Σ ½csc²(d_k/2) on every sample.)

So the whole problem is to control Σ_{k≠a,b} d_k^{−2}, where the pair (a,b) is *selected by the
configuration*. This selection bias is handled below by counting over *all* close pairs (a union
bound weighted by ρ_2, ρ_3, ρ_4), never by conditioning.

---

## 2. Determinantal toolkit [P]

### 2.1 Cauchy–Binet + bialternant formula: the exact n-point structure

**Lemma 2.1 [P].** Let z_j = e^{i x_j}, j = 1..n, n ≤ N. Then

  ρ_n(x_1,…,x_n) = (2π)^{−n} Σ_{0≤m_1<…<m_n≤N−1} | det[ z_j^{m_k} ]_{j,k} |²
                  = (2π)^{−n} ∏_{i<j} |z_i − z_j|² · Σ_{λ ⊆ ((N−n)^n)} | s_λ(z_1,…,z_n) |²,

where s_λ is the Schur polynomial and λ runs over partitions with at most n parts and λ_1 ≤ N−n
(λ = (m_n−(n−1), …, m_2−1, m_1)). Consequently, for **all** x ∈ [0,2π)^n,

  ρ_n(x) ≤ C_n(N) ∏_{i<j} |z_i − z_j|² ≤ C_n(N) ∏_{i<j} (x_i − x_j)²,   C_n(N) := (2π)^{−n} Σ_λ s_λ(1,…,1)²,

with s_λ(1^n) = ∏_{i<j}(m_j − m_i) / ∏_{k=1}^{n−1} k!, and the bound is sharp in the clustering
limit: ρ_n(x) = C_n(N) ∏_{i<j}(x_i − x_j)² (1 + o(1)) as max|x_i − x_j| → 0.

*Proof.* Write ψ_m(x) = e^{i(m−(N−1)/2)x}. Then [K_N(x_i,x_j)]_{i,j} = (2π)^{−1} Ψ Ψ\* with
Ψ_{j,m} = ψ_m(x_j) an n×N matrix, and the Cauchy–Binet formula gives det(ΨΨ\*) =
Σ_{|M|=n} |det Ψ_{·,M}|². For M = {m_1<…<m_n}, det[ψ_{m_k}(x_j)] = ∏_j e^{−i(N−1)x_j/2} · det[z_j^{m_k}],
of modulus |det[z_j^{m_k}]|. The bialternant formula det[z_j^{m_k}] = a_{λ+δ}(z) = s_λ(z)·a_δ(z), with
a_δ(z) = ∏_{i<j}(z_j − z_i) the Vandermonde determinant, gives the second expression. s_λ has
non-negative integer coefficients (Kostka numbers), and |z_j| = 1, so |s_λ(z)| ≤ s_λ(1^n) by the
triangle inequality; s_λ(1^n) is the Weyl dimension formula ∏_{i<j}(l_i − l_j)/(j−i) with
l_i = λ_i + n − i, i.e. {l_i} = {m_k}. Finally |z_i − z_j| = 2|sin((x_i−x_j)/2)| ≤ |x_i − x_j|. In the
clustering limit z_j → z_0 we have s_λ(z) → z_0^{|λ|} s_λ(1^n), so the inequality is asymptotically
an equality. ∎

**Exact constants.** With A_2(N) := Σ_{m_1<m_2}(m_2−m_1)² and A_3(N) := Σ_{m_1<m_2<m_3}[(m_2−m_1)(m_3−m_1)(m_3−m_2)]²:

  A_2(N) = N²(N²−1)/12,  A_3(N) = N³(N²−1)²(N²−4)/2160  (script check S2, S3: exact for N ≤ 21 and by
  degree-9 interpolation),

  **C_2(N) = N²(N²−1)/(48π²) ≤ N⁴/(48π²),  C_3(N) = A_3(N)/(4·(2π)³) = N³(N²−1)²(N²−4)/(69120 π³) ≤ N⁹/(69120 π³).**

The leading coefficient of A_3 is the Selberg integral: ∫_{0<a<b<c<1}[(b−a)(c−a)(c−b)]² = (1/6)·(1/360) = 1/2160
(script S3b computes ∫_{[0,1]³}∏(x_i−x_j)² = 1/360 symbolically). Cross-check in density-1 units
(x = 2πs/N): C_2 → (2π)⁴/(48π²) = π²/3 and C_3 → (2π)⁹/(69120π³) = π⁶/135, the familiar sine-process
clustering constants (ρ_2^{sine}(s) = 1 − (sin πs/πs)² = π²s²/3 + …). This is the "honest Taylor
expansion of the 3×3 determinant": the leading term is ∏(x_i−x_j)² times C_3(N), *and* the same
constant gives a global inequality, which is what the probability bounds need.

*Numerical confirmation (script S4):* the identity holds to 1e−9 on 1000 random triples for
N ∈ {3,4,6,9,13}; the global bound holds with worst ratio 1.0000000002; the clustering ratio
ρ_3/(C_3∏(x_i−x_j)²) at separations 10^{−3} is within 10^{−3} of 1 for all tested N.

### 2.2 Fischer's inequality: cluster counts are sub-Poisson, uniformly

**Lemma 2.2 [P].** For any n, m ≥ 1 and points x ∈ [0,2π)^n, y ∈ [0,2π)^m,

  ρ_{n+m}(x, y) ≤ ρ_n(x) · ρ_m(y);  in particular ρ_3(x,y,z) ≤ ρ_2(x,y)·N/2π,
  ρ_4(x,y,z,z′) ≤ ρ_2(x,y)·(N/2π)², and ρ_4(x,y,x′,y′) ≤ ρ_2(x,y)ρ_2(x′,y′).

*Proof.* The matrix G = [K_N(w_i,w_j)] over the combined points is a Gram matrix (positive
semidefinite, §2.1). Fischer's inequality for PSD block matrices, det [[A,B],[B\*,D]] ≤ det A · det D,
applied once (and iterated, ending with Hadamard's inequality for the 1×1 blocks K(z,z) = N/2π)
gives all three. ∎ (Checked numerically on 900 random 4-point Gram matrices, script S6.)

### 2.3 The two-point function, two-sided

**Lemma 2.3 [P].** Let u = θ − φ and S_N(t) := sin(Nt)/(N sin t) = (1/N)Σ_{m=0}^{N−1} cos((2m−N+1)t),
so that ρ_2(θ,φ) = (N/2π)²(1 − S_N(u/2)²). Then

  (i) ρ_2(θ,φ) ≤ N²(N²−1)u²/(48π²) ≤ N⁴u²/(48π²) for all u ∈ ℝ;
  (ii) ρ_2(θ,φ) ≥ [N²(N²−1)u²/(48π²)]·(1 − N²u²/30) whenever N²u² ≤ 24.

*Proof.* Put t = u/2 and a := t²(N²−1)/6, b := t⁴(N²−1)(3N²−7)/360. From
cos y ≥ 1 − y²/2 and Σ_{m=0}^{N−1}(2m−N+1)² = N(N²−1)/3 we get S_N(t) ≥ 1 − a; from
cos y ≤ 1 − y²/2 + y⁴/24 and Σ_m(2m−N+1)⁴ = N(N²−1)(3N²−7)/15 we get S_N(t) ≤ 1 − a + b (both power
sums checked exactly for N ≤ 15, script S1; they are the second and fourth moments of the symmetric
arithmetic progression and follow from Faulhaber's formulas).
(i) If a ≤ 1 then 0 ≤ 1 − a ≤ S_N ≤ 1, so 1 − S_N² ≤ 1 − (1−a)² ≤ 2a; if a > 1 then 1 − S_N² ≤ 1 < 2a.
Hence ρ_2 ≤ (N/2π)²·2a = (N/2π)²·u²(N²−1)/12 = N²(N²−1)u²/(48π²).
(ii) If a ≤ 1 (⇔ u²(N²−1) ≤ 24, implied by N²u² ≤ 24) then S_N ∈ [1−a, 1−a+b] ⊂ [0, 1−a+b], so
1 − S_N² ≥ 1 − (1−a+b)² = 2(a−b) − (a−b)² ≥ 2a − 2b − a², using 0 ≤ b ≤ a (indeed b/a =
t²(3N²−7)/60 ≤ (3N²−7)/(10(N²−1)) < 3/10 when a ≤ 1). Thus 1 − S_N² ≥ 2a(1 − b/a − a/2) and
b/a + a/2 = t²[(3N²−7)/60 + (N²−1)/12] = t²(2N²−3)/15 = u²(2N²−3)/60 ≤ N²u²/30. ∎
(Both bounds are checked on a fine grid for N ∈ {2,3,5,8,16,40,100}, script S5, with the
cancellation-free evaluation 1 − S_N² = (1−S_N)(1+S_N), 1 − S_N = (2/N)Σ sin²((2m−N+1)t/2).)

---

## 3. Step (ii): the smallest gap is ≤ L·N^{−4/3} with probability ≥ 1 − 1054/L³ [P]

Fix ε ∈ (0, π] and let Z := #{ unordered pairs {i,j} : d(θ_i,θ_j) ≤ ε }, and Z_ord := 2Z the number of
ordered pairs. Since δ_min is the minimum over *adjacent* pairs and every pair has distance ≥ δ_min,

  {δ_min ≤ ε} = {Z ≥ 1}.

**Lemma 3.1 (first moment) [P].** For 0 < ε ≤ π,

  E[Z] = π ∫_{−ε}^{ε} ρ_2(u) du,  and  N²(N²−1)ε³(1 − N²ε²/50)/(72π) ≤ E[Z] ≤ N²(N²−1)ε³/(72π),

the lower bound valid when N²ε² ≤ 24. In particular, with ε = xN^{−4/3}: E[Z] → x³/(72π) as N → ∞,
which is the intensity ∫_0^x s²ds/(24π) of the Ben Arous–Bourgade Poisson limit (their constant, in
our normalisation, is thus pinned by an exact computation; see §6).

*Proof.* E[Z] = ½∫∫ 1{d(x,y) ≤ ε} ρ_2(x,y) dx dy = ½·2π·∫_{−ε}^{ε}ρ_2(u)du (translation invariance; for
ε ≤ π the arc {y: d(x,y) ≤ ε} is parametrised once by u ∈ [−ε,ε]). Insert Lemma 2.3: ∫_{−ε}^{ε}u²du =
2ε³/3 and ∫_{−ε}^{ε}u²(1 − N²u²/30)du = (2ε³/3)(1 − N²ε²/50). ∎

**Lemma 3.2 (second moment) [P].** Var(Z) ≤ E[Z] + T_3, where
T_3 := ∫∫∫ ρ_3(x,y,z) 1{d(x,y)≤ε} 1{d(x,z)≤ε} dx dy dz ≤ (31π/15)·C_3(N)·ε⁸ ≤ 31 N⁹ ε⁸/(1036800 π²).

*Proof.* Write Z = Σ_{i<j} f_{ij}, f_{ij} = 1{d(θ_i,θ_j) ≤ ε}. Expanding Z² = Σ_{i<j}Σ_{k<l} f_{ij}f_{kl}:
the diagonal terms give Z; the pairs sharing exactly one index are in bijection with ordered triples
(shared point; other point of the first pair; other point of the second pair) of distinct points, so
their expectation is T_3; the disjoint pairs give ¼∫ρ_4(x,y,x′,y′)f(x,y)f(x′,y′) ≤ ¼(∫ρ_2 f)² = E[Z]²
by Lemma 2.2 (ρ_4 ≤ ρ_2ρ_2). Hence E[Z²] ≤ E[Z] + T_3 + E[Z]². For T_3 use Lemma 2.1 with
u = y−x, v = z−x ∈ [−ε,ε]: ρ_3 ≤ C_3(N)·u²v²(y−z)² and |y − z| ≤ |u| + |v| (the chord bound
2|sin(w/2)| ≤ |w| holds for any representative w), so
T_3 ≤ 2π C_3(N)∫_{−ε}^{ε}∫_{−ε}^{ε} u²v²(|u|+|v|)² du dv = 2πC_3·4·(31ε⁸/120) = (31π/15)C_3ε⁸, using
∫_0^ε∫_0^ε u²v²(u+v)² = 2ε⁸/15 + ε⁸/8 = 31ε⁸/120. Insert C_3 ≤ N⁹/(69120π³). ∎

**Proposition 3.3 [P].** For every N ≥ 2 and every L > 0,

  **P(δ_min > L·N^{−4/3}) ≤ 1054 / L³.**

*Proof.* By Chebyshev, P(Z = 0) ≤ P(|Z − EZ| ≥ EZ) ≤ Var(Z)/E[Z]² ≤ 1/E[Z] + T_3/E[Z]².

*Regime 1: L ≤ 4N^{1/3}.* Take ε = LN^{−4/3} ≤ 4/N ≤ 2 < π; then N²ε² = L²N^{−2/3} ≤ 16 < 24, so
Lemma 3.1's lower bound applies: E[Z] ≥ (L³/72π)(1 − N^{−2})(1 − L²N^{−2/3}/50) ≥ (L³/72π)·(3/4)·(17/25)
(N ≥ 2, L²N^{−2/3} ≤ 16). Hence 1/E[Z] ≤ 443.6/L³. Next T_3 ≤ 31L⁸N^{−5/3}/(1036800π²), so
T_3/E[Z]² ≤ 0.596·L²N^{−5/3} ≤ 0.596·16/N ≤ 9.54·64/L³ = 610.2/L³, using L² ≤ 16N^{2/3} and then
N ≥ (L/4)³. Total ≤ 1053.8/L³.

*Regime 2: L > 4N^{1/3}.* Then LN^{−4/3} > 4/N, so P(δ_min > LN^{−4/3}) ≤ P(δ_min > 4/N), and we take
ε = 4/N (N²ε² = 16 < 24, ε ≤ 2 < π). Lemma 3.1: E[Z] ≥ (17/25)·64(N²−1)/(72πN) ≥ 0.1443·N (N ≥ 2), and
T_3 ≤ 31·4⁸N/(1036800π²) = 0.1986·N. So P(δ_min > 4/N) ≤ 6.93/N + 9.54/N = 16.47/N < 16.47·64/L³ =
1053.8/L³ since N < (L/4)³. ∎ (Constants assembled in the script, item S8.)

*Remarks.* (1) Nothing here is asymptotic: the statement is uniform in N ≥ 2 and L > 0 (it is vacuous
for L³ < 1054). (2) The proof also shows P(δ_min > 4/N) ≤ 17/N: CUE has a gap below four mean
spacings with probability → 1 at rate 1/N, without any citation. (3) The second-moment method with
Fischer's inequality avoids the ρ_4 cluster asymptotics that a Poisson-limit proof needs; this is why
the tail bound comes for free while the limit *law* (§6) is cited.

---

## 4. Step (i): a third point within c/N of the closest pair — why L³·c⁵ [P]

Let T(ε,w) := #{ ordered triples (x,y,z) of distinct points : d(x,y) ≤ ε, dist(z,{x,y}) ≤ w }.

**Proposition 4.1 [P].** For 0 < ε ≤ π and w > 0,

  E[T(ε,w)] ≤ 16π C_3(N) [ ε³w⁵/15 + ε⁴w⁴/8 + ε⁵w³/15 ] ≤ (N⁹/(4320π²)) [ ε³w⁵/15 + ε⁴w⁴/8 + ε⁵w³/15 ].

With ε = L N^{−4/3} and w = c/N this reads

  **E[T] ≤ (4320π²)^{−1} [ L³c⁵/15 + L⁴c⁴N^{−1/3}/8 + L⁵c³N^{−2/3}/15 ] = L³c⁵/(64800π²) · (1 + O(L N^{−1/3}/c)).**

*Proof.* 1{dist(z,{x,y}) ≤ w} ≤ 1{d(z,x) ≤ w} + 1{d(z,y) ≤ w}, and the two resulting integrals are
equal (swap x ↔ y; ρ_3 and the constraint d(x,y) ≤ ε are symmetric). With u = y − x ∈ [−ε,ε],
v = z − x ∈ [−w,w], Lemma 2.1 gives ρ_3 ≤ C_3(N)u²v²(|u|+|v|)², so

  E[T] ≤ 2·2π·C_3(N)·∫_{−ε}^{ε}∫_{−w}^{w} u²v²(|u|+|v|)² dv du = 16πC_3(N)∫_0^ε∫_0^w u²v²(u+v)² dv du,

and ∫_0^w v²(u+v)²dv = u²w⁵/5 + u³w⁴/2 + u⁴w³/3, then ∫_0^ε(·)du = ε³w⁵/15 + ε⁴w⁴/8 + ε⁵w³/15. ∎

**Why the exponents.** The Vandermonde factor of the three-point function is u²·v²·(u−v)² with u the
pair separation and v the third point's offset; for u ≪ v this is u²v⁴. Integrating u² over |u| ≤ ε
gives ε³ ∝ L³N^{−4} (the same ε³ that makes the min-gap scale N^{−4/3}: N⁴ε³ = L³), and integrating
v⁴ over |v| ≤ c/N gives ∝ c⁵N^{−5}; the prefactor N⁹ of C_3 exactly compensates N^{−4}·N^{−5}. So the
probability that the min-gap pair has a third point within c/N is O(L³c⁵): two powers of L·c come
from the pair, four from the repulsion of the third point by *both* members of the pair. The
sub-leading terms L⁴c⁴N^{−1/3} and L⁵c³N^{−2/3} are the cost of |z − y| ≤ |z − x| + |x − y| when the
pair separation is not negligible against c/N; they vanish as N → ∞ for fixed L, c but must be kept
for a bound uniform in N (§5).

**Corollary 4.2 (the third-point law, leading order) [P for the bound, heuristic for the "≈"].**
As u = |x − y| → 0 the two neighbourhoods {d(z,x) ≤ w} and {d(z,y) ≤ w} coincide, so the factor 2 in
the proof of Proposition 4.1 double counts at leading order and the sharp leading term of E[T] is
L³c⁵/(129600π²), i.e. L³c⁵/(259200π²) for unordered pairs. Dividing by E[#unordered close pairs] →
L³/(72π) gives c⁵/(3600π) expected third points within c/N per close pair. The same number comes
from the conditional intensity of a third point at offset v from the *midpoint* of a pair of
separation u: ρ_3/ρ_2 = (C_3/C_2)(v² − u²/4)²(1 + O(N²v²)) → (N⁵/1440π)·v⁴, hence

  P( N·v_mid ≤ c ) ≈ 2∫_0^{c/N} (N⁵/1440π) v⁴ dv = **c⁵/(3600π)** ≈ 8.84·10^{−5} c⁵

for the nearest third point of a *typical* close pair (C_3/C_2 = N⁵/(1440π)). Turning "typical close
pair" into "the min-gap pair" and controlling the O(N²v²) and O(Nδ_min) corrections is not done here;
§7 tests the prediction numerically (exponent 5 and the constant 1/(3600π)).

---

## 5. Step (iii): shells, Markov, and the theorem [P]

Fix L ≥ 1, c ∈ (0,1], M ≥ 1. Set ε := LN^{−4/3} if L ≤ 4N^{1/3} and ε := 4/N otherwise (the two regimes
of Proposition 3.3), and w := c/N. Define the events

  E_δ := {δ_min > ε},  E_1 := {δ_min ≤ ε and ∃k ∉ {a,b}: d_k ≤ w},  E_good := {δ_min ≤ ε} ∖ E_1.

**Lemma 5.1 (uniform pair count) [P].** In both regimes E[Z_ord] ≤ L³/(36π).
*Proof.* Lemma 3.1: E[Z_ord] ≤ N⁴ε³/(36π); regime 1 gives L³/(36π); regime 2 gives 64N/(36π) < L³/(36π)
because N < (L/4)³. ∎

**Lemma 5.2 (third point, uniform) [P].** For L ≥ 1 and c ∈ (0,1], in both regimes,
P(E_1) ≤ (49/30)(4320π²)^{−1}·L³c³ = 3.83·10^{−5}·L³c³; in particular P(E_1) ≤ 3.9·10^{−5}/L³ for c = L^{−2}.
*Proof.* On E_1 the ordered triple (θ_a,θ_b,θ_k) is counted by T(ε,w), so P(E_1) ≤ E[T(ε,w)]. Regime 1:
Proposition 4.1 with N^{−1/3} ≤ 4/L and N^{−2/3} ≤ 16/L² gives
(4320π²)^{−1}[L³c⁵/15 + L³c⁴/2 + 16L³c³/15] ≤ (49/30)(4320π²)^{−1}L³c³ for c ≤ 1.
Regime 2 (ε = 4/N, N < L³/64): (N⁹/(4320π²))·N^{−8}[64c⁵/15 + 32c⁴ + 1024c³/15] <
(L³/(4320π²))[c⁵/15 + c⁴/2 + 16c³/15], the same expression. ∎

**Lemma 5.3 (dyadic shells) [P].** Let r_j := w·2^j, j ≥ 0, and for an ordered pair (x,y) of points let
n_j(x,y) := #{ z ∉ {x,y} : dist(z,{x,y}) ∈ [r_j, r_{j+1}) }. Let
W := Σ_{ordered pairs (x,y): d(x,y) ≤ ε} Σ_{j ≥ 0} r_j^{−2} n_j(x,y). Then on E_good,
S\* ≤ (π²/2)·W, and E[W] ≤ (2N/(πw))·2·E[Z_ord] = (4N²/(πc))·E[Z_ord].

*Proof.* On E_good every d_k ≥ w, so each k ∉ {a,b} lies in exactly one shell j with r_j ≤ d_k < r_{j+1}
(shells with r_j > π are empty), and by Lemma 1.1, ½csc²(d_k/2) ≤ (π²/2)d_k^{−2} ≤ (π²/2)r_j^{−2}.
Summing, S\* ≤ (π²/2)Σ_j r_j^{−2}n_j(θ_a,θ_b) ≤ (π²/2)W, since (θ_a,θ_b) is one of the ordered close
pairs and all terms are non-negative. For the expectation, the set {z : dist(z,{x,y}) ∈ [r_j,r_{j+1})}
is contained in two "annuli" (four arcs) of total length ≤ 4(r_{j+1} − r_j) = 4r_j, and Lemma 2.2
(ρ_3 ≤ ρ_2·N/2π) gives E[Σ_{pairs} n_j] ≤ (N/2π)·4r_j·E[Z_ord]. Therefore
E[W] ≤ Σ_j r_j^{−2}(N/2π)4r_j E[Z_ord] = (2N/π)E[Z_ord]Σ_j r_j^{−1} = (2N/π)(2/w)E[Z_ord] = (4N²/(πc))E[Z_ord]. ∎

Note the wrap-around: "dist(z,{x,y})" is the circular distance to the nearer endpoint, so the arcs on
both sides of *both* endpoints are included; nothing is lost when x_a^k is near 2π.

**Theorem 1′ (shell/Markov version) [P].** For all N ≥ 3 and M ≥ 1, P(S\* > M N²) ≤ 1055·M^{−3/8}.

*Proof.* {S\* > MN²} ⊂ E_δ ∪ E_1 ∪ ({S\* > MN²} ∩ E_good). With L := M^{1/8} ≥ 1 and c := L^{−2}:
P(E_δ) ≤ 1054/L³ (Proposition 3.3, monotone in the threshold in regime 2), P(E_1) ≤ 3.9·10^{−5}/L³
(Lemma 5.2), and by Markov and Lemmas 5.1, 5.3,

  P(S\* > MN², E_good) ≤ E[(π²/2)W]/(MN²) ≤ (π²/2)(4/(πc))·(L³/(36π))/M = L³/(18cM) = L⁵/(18M) = 1/(18L³).

Altogether P(S\* > MN²) ≤ (1054 + 0.0000383 + 0.0556)/L³ ≤ 1055·M^{−3/8}. ∎

There is no log N: Markov is applied once to the geometric sum Σ_j r_j^{−2}n_j, whose expectation is
dominated by the innermost shell. (Applying Markov shell by shell with weights 2^{−j}, as in the task
brief, gives the same bound times the number of shells ≈ log_2(πN/c) — the "log factor" — and is
strictly worse; we record it as an alternative in §8.)

**Proposition 5.4 (second-moment refinement) [P].** For η ∈ (0,1] put g_η(d) := d^{−2}1{d ≥ η/N} and
B := Σ_{k≠a,b} g_η(d_k). If δ_min ≤ ε and no third point lies within η/N of the pair then S\* ≤ (π²/2)B, and

  E[ Σ_{ordered close pairs (x,y)} ( Σ_{z∉{x,y}} g_η(dist(z,{x,y})) )² ] ≤ E[Z_ord]·[ 2N⁴/(3πη³) + 4N⁴/(π²η²) ].

*Proof.* Expand the square: the diagonal is ∫ρ_3(x,y,z)f(x,y)g_η² ≤ E[Z_ord]·(N/2π)∫g̃², the
off-diagonal is ∫ρ_4(x,y,z,z′)f g̃(z)g̃(z′) ≤ E[Z_ord]·((N/2π)∫g̃)² by Lemma 2.2, where
g̃(z) = g_η(dist(z,{x,y})). Now ∫g̃ dz ≤ 2·2∫_{η/N}^{∞}v^{−2}dv = 4N/η and ∫g̃² ≤ 4∫_{η/N}^{∞}v^{−4}dv =
4N³/(3η³); so (N/2π)∫g̃² ≤ 2N⁴/(3πη³) and ((N/2π)∫g̃)² ≤ 4N⁴/(π²η²). ∎

**Theorem 1 [P].** For all N ≥ 3 and M ≥ 1,

  **P( S\* > M·N² ) ≤ 1055·M^{−1/2}.**

*Proof.* Take L := M^{1/6}, η := M^{−1/3}, and decompose as before with w = η/N. P(E_δ) ≤ 1054/L³ =
1054·M^{−1/2}. Lemma 5.2's computation with c = η gives (for η ≤ 1, in both regimes)
P(E_1) ≤ (49/30)(4320π²)^{−1}L³η³ = 3.83·10^{−5}·M^{−1/2}. On E_good, S\* > MN² forces B > 2MN²/π², so by
Chebyshev–Markov on the square and Proposition 5.4 with Lemma 5.1,

  P(S\* > MN², E_good) ≤ (L³/(36π))·[2N⁴/(3πη³) + 4N⁴/(π²η²)]·(π²/(2MN²))² = (L³/M²)(π⁴/4)(1/36π)[2/(3πη³) + 4/(π²η²)]
                        ≤ (π³/144)(2/(3π) + 4/π²)·L³η^{−3}/M² = 0.133·M^{1/2}·M/M² = 0.133·M^{−1/2}

(using η^{−2} ≤ η^{−3} for η ≤ 1). Sum: (1054 + 0.00004 + 0.133)M^{−1/2} ≤ 1055·M^{−1/2}. ∎

**Corollary 5.5 [P].** P(S\* > N² log N) ≤ 1055·(log N)^{−1/2} → 0; and S\*/N² is tight: for any
ω_N → ∞, P(S\* > ω_N N²) → 0. The old hypothesis "S ≤ A·N² throughout" of Theorem B is thus replaced by
a quantitative statement about the initial repaired stiffness, true with probability ≥ 1 − 1055 A^{−1/2}
for every N.

*What is lossy.* The 1055 comes from Proposition 3.3's crude constants (the true P(δ_min > LN^{−4/3}) is
≈ e^{−L³/72π}); the exponent 1/2 comes from a second moment on the bulk sum whose mean is dominated by
the innermost allowed shell. Higher moments (ρ_{2+p} ≤ ρ_2(N/2π)^p, same proof) push the exponent up
towards the third-point value 5/2 but never reach it; a proof of the exact tail M^{−5/2} would need the
Vandermonde vanishing inside the bulk sum, i.e. a Palm-measure computation — see §8.

---

## 6. The CUE depth law

### 6.1 Inputs, with their status

**(E-A) Theorem A** (`depth_scaling_theorem.md` §3, **[P]** there; the proof was re-read for this file
and is correct): for every configuration, with D the first collision time of the backward flow
P_s(z) = Σ a_j e^{s·j(N−j)} z^j and δ_min the smallest cyclic gap,

  D ≥ −log cos(δ_min/2) ≥ δ_min²/8.

**(E-B\*) Assumption B\*** (the repaired Theorem B, task A1's `r1_theoremB_repair.md`; *assumed here,
not re-proved*): with A := S\*/N² and S\* the repaired stiffness of the min-gap pair, if A·N²·δ_min² < 4 then

  D ≤ −(2AN²)^{−1} log(1 − AN²δ_min²/4).

Two readings are possible: (B\*-0) with S\* evaluated at s = 0; (B\*-sup) with S\* replaced by
sup_{0≤s≤D} S\*(s), the stiffness along the flow. The mean-value argument of Theorem B literally
needs (B\*-sup). Theorem 1 controls S\*(0). The gap between the two is the open item O1 (§8); the
theorem below is stated under (B\*-0), i.e. under whatever short-time stability statement task A1
proves or assumes.

**(E-BAB) Ben Arous–Bourgade** *(recalled; not verified online)*: G. Ben Arous, P. Bourgade, "Extreme
gaps between eigenvalues of random matrices", Ann. Probab. 41 (2013). For Haar unitary matrices the
rescaled small gaps Σ_i δ_{N^{4/3}·gap_i} converge to a Poisson point process on (0,∞) whose intensity
in our normalisation (angles on [0,2π)) is x²dx/(24π); equivalently the k-th smallest gap has limiting
density ∝ x^{3k−1}e^{−x³/72π}, and for the smallest gap

  P( N^{4/3} δ_min > x ) → exp(−x³/(72π)) =: P(G > x).

The recalled statement in the paper is "density proportional to x^{3k−1}e^{−x³}" in the authors'
normalisation; the constant 72π in ours is **not** taken from memory: Lemma 3.1 shows
E[#gaps ≤ xN^{−4/3}] → x³/(72π) exactly, which is the intensity measure of the limit and therefore
fixes the constant, given that the limit is Poisson. Only the Poisson property is cited.

**(E-1) Theorem 1** and **Proposition 3.3** (this file, **[P]**): S\*/N² and N^{4/3}δ_min are tight,
uniformly in N, with explicit polynomial tails.

### 6.2 Statement and proof

**Theorem 2 (CUE depth law) [P modulo (E-B\*) and (E-BAB)].** Let D_N be the depth of the CUE(N)
configuration and X_N := N^{4/3}δ_min, A_N := S\*/N². Then, with G as in (E-BAB),

  **N^{8/3} D_N ⟹ G²/8,**  and more precisely  X_N²/8 ≤ N^{8/3}D_N ≤ (X_N²/8)·(1 + q_N/2) on {q_N ≤ 2},

where q_N := A_N X_N² N^{−2/3} = S\*·δ_min² satisfies P(q_N > t) ≤ 1055·(t N^{2/3})^{−1/4}·1054^{1/2}… — more
simply q_N = O_P(N^{−2/3}); in particular the ratio ρ_N := 8D_N/δ_min² satisfies ρ_N − 1 = O_P(N^{−2/3}).

*Proof.* Lower bound: (E-A) gives D_N ≥ δ_min²/8, i.e. N^{8/3}D_N ≥ X_N²/8, deterministically.

Upper bound: on {q_N < 4}, (E-B\*) gives, with 1/(2A_N N²) = δ_min²/(2q_N),

  D_N ≤ (δ_min²/(2q_N))·(−log(1 − q_N/4)) = (δ_min²/8)·φ(q_N),  φ(q) := −(4/q)log(1 − q/4).

Since −log(1 − t) ≤ t/(1−t) for t ∈ [0,1), φ(q) ≤ 1/(1 − q/4) ≤ 1 + q/2 for q ≤ 2. This is the
two-sided inequality.

Tightness: by Theorem 1, P(A_N > M) ≤ 1055M^{−1/2}; by Proposition 3.3, P(X_N > L) ≤ 1054L^{−3}, both for
all N. Hence for any t > 0 and any M ≥ 1,

  P(q_N > t) ≤ P(A_N > M) + P(X_N² > tN^{2/3}/M) ≤ 1055M^{−1/2} + 1054·(M/(tN^{2/3}))^{3/2},

which tends to 0 as N → ∞ for every fixed t, M → ∞ slowly (e.g. M = N^{1/3} gives
P(q_N > t) ≤ 1055N^{−1/6} + 1054 t^{−3/2}N^{−1/2}); so q_N → 0 in probability, and since A_N and X_N are
tight, q_N = O_P(N^{−2/3}). Therefore N^{8/3}D_N = (X_N²/8)(1 + O_P(N^{−2/3})).

Limit law: X_N ⟹ G by (E-BAB), so X_N²/8 ⟹ G²/8 by the continuous mapping theorem, and
N^{8/3}D_N ⟹ G²/8 by Slutsky's lemma. ∎

*What each step rests on.* The inequality chain is deterministic (E-A, E-B\*). The only probabilistic
inputs are (i) tightness of S\*/N² — **proved here** (Theorem 1), which is exactly the regularity
hypothesis flagged as the "single open analytic ingredient" in `depth_scaling_theorem.md` §4 and
handoff §8 item 1 — and (ii) tightness of N^{4/3}δ_min — **proved here** (Proposition 3.3). The
*distributional* statement additionally uses the cited Poisson limit. The rate N^{−2/3} for ρ_N − 1
predicted in `depth_scaling_theorem.md` §7 (and fitted there as −0.710 / local −0.624) is now a
consequence of tightness alone.

*Theorem C(ii) of the source document* (P(N²D_N^{CUE} < π²/8) → 1) follows in the same way:
N²D_N ≤ (N²δ_min²/8)(1 + q_N/2) = N^{−2/3}X_N²(1 + q_N/2)/8 → 0 in probability, without the Poisson
limit (only Proposition 3.3 and Theorem 1), still under (E-B\*).

---
