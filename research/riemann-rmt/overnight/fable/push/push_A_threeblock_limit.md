# push A — The symmetric 3-block: lim N²D_N = 2, exact characterisation, and the midpoint-insertion principle

**Fable**, 6 September 2026. Deliverable for Task A of the adversarial depth programme.

Status tags: **[P]** proved here (proof written out), **[C]** computed (script + numbers given), **[O]** open (obstruction stated). All scripts are in this directory; every numerical claim below can be regenerated from them.

## 0. Results in one page

Setting: N points on the unit circle drawn from the 2N-th roots of unity; the *alternating clock* is the set of odd sites (roots of z^N+1, all gaps 2 in units π/N); the flow is P_s(z)=Σ a_j e^{s j(N−j)} z^j; D_N = first collision time; τ_N := N² D_N.

The **symmetric 3-block families** are the alternating clock with one root added at angle 0 (gaps 1,1) and one root removed (gap 4) at, or one root pair shifted (gaps 3,3) around, the antipode:

| name | N | polynomial | gap pattern | mirror-symmetric? |
|---|---|---|---|---|
| block4odd | odd | (z^N+1)(z−1)/(z+1) | [1,1,2,…,2,4,2,…,2] | yes |
| block4even | even | (z^N+1)(z−1)/(z+ω̄), ω=e^{iπ/N} | [1,1,2,…,2,4,2,…,2] | no (removed site N−1) |
| block33 | even | (z^N+1)(z²−1)/(z²+2cos(π/N)z+1) | [1,1,2,…,2,3,3,2,…,2] | yes |

1. **Theorem 5.4 [P].** For all three families, lim_{N→∞} N² D_N = 2. The proof has four ingredients: (i) closed forms of Q_0(x)=∏sin((x−θ_j)/2) (§2); (ii) the heat flow of a trigonometric polynomial is a Gaussian convolution, which gives the local limit q_τ(u)=e^{−τ/4}(u cos(u/2) − τ sin(u/2)) with an explicit O(N^{−2}) error in C¹ on compact sets, uniformly for τ∈[0,3] — no Euler–Maclaurin and no endpoint terms (§3); (iii) the complete real-zero structure of q_τ (§4); (iv) Theorem A (no gap of initial size ≥2π/N closes before τ=π²/2>2) plus a confinement-and-counting argument, which needs neither symmetry nor Hurwitz in the complex plane (§5).

2. **Proposition 6.1 [P] (exact one-variable characterisation).** For the two mirror-symmetric families, D_N is *exactly* the first zero of the explicit exponential sum F_N(s)=P_s′(1)=Σ_j j a_j e^{s j(N−j)}; for block4odd
   F_N(s) = N − 2 Σ_{j=1}^{N−1} (−1)^j j e^{s j(N−j)}.
   Checked against the complete enumerations N≤12 (agreement 10^{−8}, the enumeration's own tolerance) and against `heat_depth.py` at N=32…65 (10^{−9}) [C].

3. **Proposition 6.2 [P].** For both symmetric families τ_N = 2 − 4/(3N²) + c₂/N⁴ + O(N^{−6}) with c₂ = −8/5 (block4odd) and c₂ = −8/5 − π² (block33). The first coefficient −4/3 is what the numbers in fact (F1) were approximating (F1's "−1.34" at N=128, 256, 384 was block33; its drift at N=384 is solver error — the exact values are N²(τ_N−2) = −1.33403, −1.33351, and −4/3 to 6 digits by N=2048) [C, mpmath 30 digits].

4. **Asymmetric placement (block4even) [C + derivation].** τ_N = 2 − 4/(3N²) − 2.703·N^{−8/3} + …: the odd part of the perturbation gives the same −4/3, the even (tilt) part converts the triple zero into a cusp and produces the fractional power. Verified: (N²(2−τ_N) − 4/3)·N^{2/3} = 2.899, 2.775, 2.730, 2.713, 2.703, 2.695 at N=16, 32, 64, 128, 192, 256, against the predicted 2·(9/16)^{1/3}(2π/3)^{2/3} = 2.7030.

5. **Midpoint-insertion principle, Proposition 7.1 [P].** For k midpoints inserted with polynomial p and lattice L∈{cos(u/2), sin(u/2)},
   e^{τ∂²}[p L] = e^{−τ/4}·Re / Im [ e^{iu/2} (e^{τ∂²}p)(u+iτ) ],
   with e^{τ∂²}p = Σ_k τ^k p^{(2k)}/k! — a closed form for every such family. Consequences: the **5-block** (gaps 1,1,1,1) and the **double 3-block** (gaps 1,1,2,1,1) both have local constant τ* = **2**, with the double zero at u=π resp. u=2π occurring *exactly* at τ=2 [P]; that no double zero occurs earlier is reduced to a one-variable system and checked [C]. The **7-block** has τ* = 2.03812605359… > 2 and the 9-block 2.0689…: longer blocks collide *later*, consistent with the enumeration's maximisers at N=11,12 being long 1-runs, so the 3-block is not the maximiser of N²D beyond N=10. First-order corrections N²(τ_N−τ*) → −8/3, −8/3, −4.154 for the 5-block, double 3-block and 7-block (Prop. 7.3 [P] formula, values [C]) are confirmed by a corrected solver [C].

6. **A failure mode of `heat_depth.py` [C].** Its `depth_pair` discards the tracked extremum as soon as it leaves the *initial* interval (θ_i,θ_{i+1}); for defects whose colliding roots drift (7-block outer gap, and the 5-block / double-3-block gaps at the 10^{−4} level) this returns a spurious early time (7-block: 1.843 instead of 2.038). `heat_depth_robust.py` fixes this by bracketing with the current zeros; it reproduces the exact 3-block values to 10^{−9}. `run_families.py`'s `block5` numbers are affected at the O(N^{−2}) level only, `block7` at O(1).

## 1. Setting and the scalar flow

Write P(z)=∏_{j=1}^N(z−e^{iθ_j})=Σ_{j=0}^N a_j z^j and P_s(z)=Σ a_j e^{s j(N−j)} z^j. Put

  Q_0(x) := ∏_{j=1}^N sin((x−θ_j)/2).

Since e^{ix}−e^{iθ} = 2i e^{i(x+θ)/2} sin((x−θ)/2), one has P(e^{ix}) = (2i)^N e^{iΣθ_j/2} e^{iNx/2} Q_0(x), so Q_0(x)=κ e^{−iNx/2}P(e^{ix}) = κ Σ_j a_j e^{i(j−N/2)x} for a unimodular constant κ (Q_0 is defined up to sign by the choice of representatives θ_j mod 2π; nothing below depends on it). With m=j−N/2 the weight j(N−j)=N²/4−m², so

  Q_s(x) := κ e^{−iNx/2} P_s(e^{ix}) = e^{sN²/4} Σ_m c_m e^{−s m²} e^{imx} = e^{sN²/4} (e^{s∂_x²} Q_0)(x),   c_m := κ a_{m+N/2}.   (1.1)

Q_s is real for real x (Q_0 is, and the heat semigroup preserves realness), 2π-periodic for N even and 4π-periodic for N odd, and its real zeros are exactly the arguments of the zeros of P_s on the unit circle.

**Facts used from `depth_scaling_theorem.md`** (all [P] there): P_s is self-inversive, its zeros stay on the circle and are simple for 0≤s<D, they are C^∞ functions of s there and obey Lemma 1 (dθ_j/ds = −Σ_k cot((θ_j−θ_k)/2)); D is the first time two zeros coincide; and **Theorem A**: an adjacent pair whose gap is g_0 at s=0 cannot collide before s=−log cos(g_0/2) ≥ g_0²/8.

**Lemma 1.1 (the only gaps that can close before τ=π²/2 are the 1-gaps).** [P] If a configuration on the 2N-th roots of unity has a gap of size 2π/N or more, that gap is still open at every s < −log cos(π/N), and −log cos(π/N) ≥ π²/(2N²). *Proof.* Theorem A with g_0 ≥ 2π/N (−log cos(g/2) is increasing in g on (0,π)), and Lemma 2 of the theorem file (−log cos(x/2) ≥ x²/8 at x=2π/N). ∎

Scaled variables: u := N x, τ := N² s. Then (1.1) reads

  Q_{τ/N²}(u/N) = e^{τ/4} Σ_m c_m e^{−τ (m/N)²} e^{i(m/N)u}.   (1.2)

## 2. Closed forms of Q_0 for the three families [P]

**Lemma 2.1 (lattice product).** For θ_j = π(2j+1)/N, j=0,…,N−1,

  ∏_{j=0}^{N−1} sin((x−θ_j)/2) = (−1)^N 2^{1−N} cos(Nx/2).

*Proof.* ∏(e^{ix}−e^{iθ_j}) = e^{iNx}+1. Each factor is 2i e^{i(x+θ_j)/2} sin((x−θ_j)/2), and Σθ_j = πN, so the product equals (2i)^N i^N e^{iNx/2} ∏sin = (−2)^N e^{iNx/2}∏sin. Hence ∏sin = (−2)^{−N} e^{−iNx/2}(e^{iNx}+1) = (−1)^N 2^{1−N}cos(Nx/2). ∎

**Lemma 2.2 (the families).** With the added root at angle 0:

* block4odd (N odd, removed root at angle π):  Q_0(x) = 2^{1−N} cos(Nx/2) · tan(x/2).
* block4even (N even, removed root at angle π−π/N, i.e. z=−ω̄):  Q_0(x) = −2^{1−N} cos(Nx/2) · sin(x/2)/cos((x+π/N)/2).
* block33 (N even, sites N±1 removed, sites 0 and N added):  Q_0(x) = −2^{1−N} cos(Nx/2) · sin(x/2)cos(x/2) / [cos((x−π/N)/2) cos((x+π/N)/2)].

*Proof.* Multiply Lemma 2.1 by sin((x−θ_a)/2) for each added root and divide by sin((x−θ_r)/2) for each removed one, using sin((x−π)/2)=−cos(x/2) and sin((x−π∓π/N)/2) = −cos((x∓π/N)/2). ∎

**Lemma 2.3 (coefficients).** [P]
* block4odd: P(z) = (z^N+1)(z−1)/(z+1) = z^N − 1 − 2Σ_{j=1}^{N−1}(−1)^j z^j. (Since N is odd, (z^N+1)/(z+1)=Σ_{i=0}^{N−1}(−1)^i z^i; multiply by z−1.)
* block33: P(z) = (z²−1)R(z), R(z) = (z^N+1)/(z²+2cz+1) = Σ_{k=0}^{N−2} (−1)^k U_k(c) z^k, c=cos(π/N), U_k(c) = sin((k+1)π/N)/sin(π/N). (Chebyshev expansion 1/(1+2cz+z²) = Σ(−1)^k U_k(c) z^k; the terms of order ≥ N−1 cancel because U_{N−1}(c)=0 and U_{k−N}(c)=−U_k(c).)
* block4even: a_N=1, a_0=−ω, a_j = −(1+ω̄)(−1)^j e^{iπ(j+1)/N} for 1≤j≤N−1.

Both lemmas are verified in `threeblock_exact.py` (part (1),(2)): the closed forms agree with the product ∏sin to 10^{−14}, and the coefficient formulas agree with `numpy.poly` of the root set to 10^{−14}, at N=7, 8, 11, 12 [C].

## 3. The Weierstrass representation and the local limit

### 3.1 Heat flow of a trigonometric polynomial is a Gaussian convolution [P]

**Lemma 3.1.** Let f(v)=Σ_m c_m e^{iμ_m v} be a finite sum with real frequencies μ_m, and G_τ(w)=(4πτ)^{−1/2}e^{−w²/4τ}. Then for every τ>0 and u∈ℝ,

  (G_τ * f)(u) = ∫_ℝ G_τ(u−v) f(v) dv = Σ_m c_m e^{−τμ_m²} e^{iμ_m u} =: (e^{τ∂²}f)(u).

*Proof.* ∫G_τ(w)e^{−iμw}dw = e^{−τμ²} (Gaussian integral), termwise. ∎

Apply this to (1.2): define the **scaled initial function** q_0^N(u) := κ_N Q_0(u/N), a finite exponential sum in u with frequencies m/N, and

  q_τ^N(u) := (G_τ * q_0^N)(u) = κ_N e^{−τ/4} Q_{τ/N²}(u/N).   (3.1)

The real zeros of q_τ^N are exactly N times the real zeros of Q_{τ/N²}; the normalising constant κ_N ≠ 0 is chosen below.

### 3.2 The exact local solution [P]

**Lemma 3.2.** On the space of functions (polynomial)×e^{iλu}, e^{τ∂²} u e^{−τ∂²} = u + 2τ∂. Consequently e^{τ∂²}[u f] = (u+2τ∂) e^{τ∂²} f, and

  q_τ(u) := e^{τ∂²}[u cos(u/2)] = (u+2τ∂)[e^{−τ/4}cos(u/2)] = e^{−τ/4}( u cos(u/2) − τ sin(u/2) ).   (3.2)

*Proof.* [∂², u] = 2∂ and [∂², 2∂]=0, so the Hadamard series of e^{τ∂²} u e^{−τ∂²} terminates after one term. Each space (polynomials of degree ≤ d)·e^{iλu} is finite-dimensional and invariant under ∂ and u, so all operators are matrices and the identities are algebraic. ∎

(3.2) is fact (F2), now with a proof. q_τ is entire in u, real for real u, odd in u, and ∂_τ q_τ = ∂_u² q_τ.

### 3.3 The initial functions and their bounds [P]

Choose κ_N so that q_0^N(u) = cos(u/2)·φ_N(u) with φ_N′(0)=1:

* block4odd: φ_N(u) = 2N tan(u/2N).
* block4even: φ_N(u) = 2N sin(u/2N)·cos(π/2N)/cos((u+π)/2N).
* block33: φ_N(u) = N sin(u/N)·cos²(π/2N)/[cos²(u/2N) − sin²(π/2N)]  (using cos(a−b)cos(a+b)=cos²a−sin²b).

**Lemma 3.3.** There is an absolute constant C_0 such that for all N ≥ 8 and all three families:

(B1) |φ_N(v) − v| ≤ C_0 (1+|v|³)/N²  and  |φ_N′(v) − 1| ≤ C_0 (1+|v|²)/N²  for |v| ≤ N;

(B2) |q_0^N(v)| ≤ N³ and |∂_v q_0^N(v)| ≤ N³ for all v ∈ ℝ.

Moreover, for the two symmetric families φ_N is odd and

(B3) φ_N(v) = v + v³/(12N²) + R_N(v),  |R_N(v)| ≤ C_0(1+|v|^5)/N⁴  for |v| ≤ N.

*Proof.* (B1),(B3): with a=v/2N (|a|≤1/2) and b=π/2N, block4odd is 2N(tan a) = v + v³/(12N²) + v⁵/(120N⁴)+…, a convergent Taylor series with positive coefficients, so the remainders are bounded by the next term times an absolute constant; the derivative is sec²a−1 = tan²a ≤ 2a². For block33, the numerator N sin(v/N)cos²b − v(cos²a−sin²b) equals (N sin(v/N)−v) − N sin(v/N) sin²b + v sin²a + v sin²b, each term being O((|v|³+|v|)/N²), and the denominator cos²a − sin²b ≥ cos²(1/2) − sin²(π/16) > 0.7; the derivative bound is the same computation one order down. block4even: the numerator sin a − a cos(a+b)·(cos b)^{−1}·… expands as (sin a − a cos a) − a cos a(1−cos b) + a sin a sin b = O(a³ + ab² + a²b), and cos((v+π)/2N) ≥ cos(1/2+π/16) > 0.5; the a²b term produces the even contribution −πv²/(4N²) that is responsible for the asymmetry (§6.4). In every case the Taylor remainders are those of sin, cos, tan on |a|≤1/2 and are controlled by the next term; the symbolic expansions are printed by `threeblock_asymptotics.py` and `fold_constants.py`, and (B1),(B3) are confirmed numerically to the stated orders in `local_convergence_check.py` [C].

(B2): |q_0^N(v)| = |2N sin a|·|cos(v/2)/cos(…)| ≤ 2N·N for block4odd/even because, with z = e^{iv/N}, |cos(Nx/2)/cos((x−α)/2)| = |(z^N+1)/(z+e^{iα})| = |Σ_{k=0}^{N−1} z^{N−1−k}(−e^{iα})^k| ≤ N whenever (−e^{iα})^N = −1. For block33 the same identity gives |cos(v/2)/(cos(a−b)cos(a+b))| = 2|R(z)| ≤ 2Σ_k|U_k(c)| ≤ 2Σ_{k≤N−2}(k+1) ≤ N², so |q_0^N| ≤ N·N². The derivative bound follows from Bernstein's inequality for exponential sums with frequencies |m/N| ≤ 1/2 bounded on ℝ (|f′| ≤ (1/2) sup|f|; classical, recalled). ∎

### 3.4 The local limit with an explicit rate [P]

**Proposition 3.4.** For all three families there is C_1 such that for all N ≥ 8, all τ ∈ [0,3], all |u| ≤ 2π and k∈{0,1},

  |∂_u^k q_τ^N(u) − ∂_u^k q_τ(u)| ≤ C_1 / N².

*Proof.* Put g := q_0^N − q_0 where q_0(v) = v cos(v/2); then g(v) = cos(v/2)(φ_N(v)−v), and q_τ^N − q_τ = G_τ * g, ∂_u(q_τ^N − q_τ) = G_τ * g′ (differentiate q_0^N and q_0 rather than the kernel, so that no τ^{−1/2} appears). By (B1), |g(v)|+|g′(v)| ≤ 2C_0(1+|v|³)/N² for |v| ≤ N; by (B2), |g|+|g′| ≤ 2N³+2(1+|v|) everywhere. Split the convolution at |v| = N. Inner part: ≤ 2C_0 N^{−2} E[1+|u+√(2τ)Z|³] ≤ 2C_0 N^{−2}(1 + 8(2π)³ + 8·6^{3/2}E|Z|³) for |u|≤2π, τ≤3, Z standard Gaussian. Outer part: ≤ (2N³+2+2N)·P(|u+√(2τ)Z| ≥ N) ≤ 4N³·2e^{−(N−2π)²/12} for τ≤3, which is ≤ N^{−2} for N ≥ 8. ∎

**Numerical check [C]** (`local_convergence_check.py`, q_τ^N evaluated exactly from the Fourier representation of `heat_depth.py`, sup over u∈[−2π,2π], τ∈{0,0.5,…,3}): N²·sup|q_τ^N−q_τ| = 20.96, 20.75, 20.69, 20.68, 20.67 (block4odd, N=17…257) and 21.62, 20.90, 20.73, 20.69, 20.67 (block33, N=16…256); the second-order remainder N⁴·sup|q_τ^N − q_τ − N^{−2}r_τ| with r_τ := e^{τ∂²}[cos(u/2)u³/12] is 87.5, 86.4, 86.2, 86.1, 86.2 resp. 243, 237, 235, 234.7, 234.6 — both orders are exactly as claimed.

## 4. The real zeros of the limit function [P]

**Lemma 4.1.** Let q_τ(u) = e^{−τ/4}(u cos(u/2) − τ sin(u/2)), τ ≥ 0.

(a) q_τ(±2π) = ∓2π e^{−τ/4} ≠ 0 for every τ.

(b) For 0 ≤ τ < 2 the zeros of q_τ in [−2π,2π] are exactly 0 and ±u_τ, where u_τ ∈ (0,π] is the unique solution of u cot(u/2) = τ on (0,π); all three are simple, with q_τ′(0) = e^{−τ/4}(1−τ/2) and q_τ′(±u_τ) = e^{−τ/4}(sin u_τ − u_τ)/(2 sin(u_τ/2)) ≠ 0. u_τ decreases continuously from π (τ=0) to 0 (τ→2), u_τ² = 6(2−τ)(1+o(1)).

(c) For τ ≥ 2 the only zero of q_τ in [−2π,2π] is 0; it is simple for τ > 2 and a triple zero for τ = 2 (q_2(u) = −e^{−1/2}u³/12 + O(u⁵)).

*Proof.* On (0,2π), sin(u/2)>0, so q_τ(u)=0 iff h(u) := u cot(u/2) = τ. h′(u) = (sin u − u)/(2 sin²(u/2)) < 0 on (0,2π), so h is strictly decreasing, from h(0+)=2 to h(π)=0 to h(2π−) = −∞. Hence h(u)=τ has exactly one solution in (0,2π) when 0 ≤ τ < 2, lying in (0,π], and none when τ ≥ 2. Oddness gives (−2π,0). At u=±2π, sin(u/2)=0 and cos(u/2)=−1. Derivatives: q_τ′ = e^{−τ/4}[cos(u/2)(1−τ/2) − (u/2)sin(u/2)]; at u=u_τ substitute τ=u cot(u/2). The expansion h(u) = 2 − u²/6 − u⁴/360 − … gives u_τ ~ √(6(2−τ)); q_2′(0)=0 and q_2‴(0) = −e^{−1/2}/2. ∎

## 5. Localisation and the limit theorem

**Lemma 5.1 (zero counting under C¹ perturbation).** Let f ∈ C²[−R,R] have finitely many zeros z_1<…<z_n in (−R,R), all simple. Put m := min_i|f′(z_i)|, M := sup|f″|, ρ := min( m/(2M), ½ min_{i<j}|z_i−z_j|, min_i (R−|z_i|) ) and η_0 := min( m/4, mρ/2, min{|f(u)| : |u|≤R, dist(u,{z_i}) ≥ ρ} ) > 0. If g ∈ C¹[−R,R] and ‖g−f‖_{C¹} < η_0, then g has exactly n zeros in [−R,R], all simple, one in each (z_i−ρ, z_i+ρ).

*Proof.* On [z_i−ρ, z_i+ρ], |f′| ≥ m/2 (mean value theorem, |f″|≤M), so |g′| ≥ m/4 > 0: g is strictly monotone there, with at most one zero; and |f(z_i±ρ)| ≥ mρ/2 > η_0 > |g−f|, so g(z_i±ρ) have the opposite signs of f(z_i±ρ), which are opposite: exactly one zero. Outside these intervals |f| ≥ η_0 > |g−f|, so g ≠ 0. ∎

**Lemma 5.2 (uniform constants for the limit family).** Fix ε∈(0,1/2). The constants of Lemma 5.1 for f=q_τ on [−2π,2π] can be chosen uniformly in τ ∈ [0,2−ε] (n=3) and uniformly in τ ∈ [2+ε,3] (n=1).

*Proof.* q_τ, q_τ′, q_τ″ are jointly continuous in (τ,u); by Lemma 4.1 the zero set has the stated structure with zeros depending continuously on τ, m(τ) = min(e^{−τ/4}|1−τ/2|, e^{−τ/4}(u_τ−sin u_τ)/(2sin(u_τ/2))) is continuous and positive on [0,2−ε], and min{|q_τ(u)|: dist(u, zeros) ≥ ρ} is continuous and positive; a continuous positive function on a compact set is bounded below. Same for [2+ε,3] with the single zero 0 and m = e^{−τ/4}(τ/2−1) ≥ e^{−3/4}ε/2. ∎

**Theorem 5.4.** For each of the three families, lim_{N→∞} N² D_N = 2.

*Proof.* Fix ε ∈ (0, 1/2). By Proposition 3.4 and Lemma 5.2 there is N_0(ε) such that for N ≥ N_0:

(i) for every τ ∈ [0,2−ε], q_τ^N has exactly three zeros in [−2π,2π], all simple;
(ii) for every τ ∈ [2+ε,3], q_τ^N has exactly one zero in [−2π,2π];
(iii) for every τ ∈ [0,3], q_τ^N(±2π) ≠ 0 (Lemma 4.1(a) and |q_τ^N−q_τ| ≤ C_1/N² < 2πe^{−3/4}).

Write τ_N = N²D_N and s = τ/N². Recall from §1: for 0 ≤ τ < τ_N all zeros of Q_s are real and simple and move continuously; the zeros of q_τ^N on [−2π,2π] are N times the zeros of Q_s on the arc [−2π/N, 2π/N].

*Confinement.* At τ=0 the zeros in the arc are the three block roots u = 0, ±π (the next lattice roots are at ±3π). By (iii) no zero can cross the endpoints ±2π while τ < min(τ_N,3) (a crossing would give a zero at ±2π at some τ by continuity). Hence, for 0 ≤ τ < min(τ_N,3), the zeros of q_τ^N in (−2π,2π) are exactly the three block roots (continuously continued), and any zero in the closed interval [−2π,2π] is one of them.

*Lower bound: τ_N > 2−ε.* Suppose τ_N ≤ 2−ε. At s=D_N two zeros of Q_s coincide. By Lemma 1.1, since τ_N < 2 < π²/2 ≤ N²(−log cos(π/N)), the colliding pair is not one of the gaps of initial size ≥2π/N; so it is one of the two block gaps, i.e. two block roots coincide, at a point of the closed arc (they cannot have left it, and by (iii) the point is interior). Thus q^N_{τ_N} has a real zero of multiplicity ≥2 in (−2π,2π) — contradicting (i), which says all zeros of q^N_{τ_N} in [−2π,2π] are simple.

*Upper bound: τ_N ≤ 2+ε.* Suppose τ_N > 2+ε. Then at τ = 2+ε < 3 all zeros of Q_s are real and simple and, by confinement, three of them lie in (−2π,2π) — contradicting (ii).

Hence 2−ε < τ_N ≤ 2+ε for all N ≥ N_0(ε). ∎

*Remarks.* (1) The proof uses neither mirror symmetry nor complex zeros; the asymmetric block4even is covered verbatim. (2) The only input about the global dynamics is Theorem A through Lemma 1.1; everything else is a statement about a single explicit function on [−2π,2π]. (3) Confinement comes from (iii) alone — the nonvanishing of the limit function at u=±2π — not from Theorem A; Theorem A is used only to identify the colliding pair as a block pair. In particular the lattice neighbours at ±3π never enter [−2π,2π] for τ<3 because no zero can ever sit at ±2π.

## 6. The symmetric families: an exact one-variable characterisation and the full expansion

### 6.1 D_N is the first zero of P_s′(1) [P]

**Proposition 6.1.** Let the configuration be mirror-symmetric about the added root (block4odd, block33), so that P has real coefficients and P(1)=0. Then P_s(1)=0 for all s, and

  D_N = min{ s>0 : F_N(s) = 0 },   F_N(s) := P_s′(1) = Σ_{j=0}^N j a_j e^{s j(N−j)},

provided this minimum is < −log cos(π/N) (true for all N ≥ 4 by Theorem 5.4 and, for N ≤ 12, by the enumeration).

*Proof.* Mirror symmetry means Q_0 is odd in x; the heat flow preserves oddness, so Q_s(0)=Q_s″(0)=0 for all s, i.e. P_s(1)=0 and P_s′(1) = −i κ̄ Q_s′(0). If F_N(s_0)=0 then Q_{s_0} has a zero of multiplicity ≥3 at 0, so disc(P_{s_0})=0 and D_N ≤ s_0. Conversely, let s_0 be the first zero of F_N and suppose D_N < s_0. Then D_N < −log cos(π/N), so by Lemma 1.1 the collision at D_N is between block roots; by oddness the block roots are 0 and ±g(s), and a collision among them forces g(D_N)=0, a triple zero at 0, whence F_N(D_N)=0 with D_N<s_0 — contradiction. ∎

Explicitly (Lemma 2.3), with s=τ/N², m=j−N/2, and after removing the common factor e^{τ/4}:

* block4odd:  F_N ∝ N e^{−τ/4} − 2Σ_{j=1}^{N−1} (−1)^j j e^{−τ(j−N/2)²/N²} = N e^{−τ/4} + 4 Σ_{j=1}^{(N−1)/2} (−1)^j (N/2−j) e^{−τ(1/2−j/N)²};
* block33:  F_N ∝ Σ_j j (r_{j−2} − r_j) e^{−τ(j−N/2)²/N²},  r_k = (−1)^k sin((k+1)π/N)/sin(π/N) (0≤k≤N−2), r_k=0 otherwise.

Note the structure that makes a naive Euler–Maclaurin treatment delicate: the alternating sum is O(N) and is balanced against the single endpoint term N e^{−τ/4}; the Gaussian-convolution representation of §3 is the clean way to expand it.

**Verification [C]** (`threeblock_exact.py`, parts (3),(3b)): first zero of F_N versus the complete enumerations (`acue_depth_N*.npz`, bisection tolerance ≈10^{−8} in N²D) and versus `heat_depth.py`:

| family | N | enumeration N²D | first zero of F_N | heat_depth.py |
|---|---|---|---|---|
| block33 | 6 | 1.9526286569 | 1.9526286880 | — |
| block33 | 8 | 1.9761217503 | 1.9761218138 | — |
| block33 | 10 | 1.9854575487 | 1.9854576378 | — |
| block33 | 12 | 1.9901671516 | 1.9901671829 | — |
| block4odd | 5 | 1.9438833689 | 1.9438833804 | — |
| block4odd | 7 | 1.9720950491 | 1.9720950757 | — |
| block4odd | 9 | 1.9832892135 | 1.9832892689 | — |
| block4odd | 11 | 1.9888690636 | 1.9888696692 | — |
| block33 | 32 | — | 1.998686923391 | 1.998686921661 |
| block4odd | 33 | — | 1.998774283610 | 1.998774283608 |
| block33 | 64 | — | 1.999673794669 | 1.999673792112 |
| block4odd | 65 | — | 1.999684328473 | 1.999684320700 |

### 6.2 The expansion τ_N = 2 − 4/(3N²) + c₂/N⁴ + O(N^{−6}) [P]

Let a_N(τ) := ∂_u q_τ^N(0) (∝ F_N(τ/N²) for the symmetric families). By Lemma 3.1, ∂_u(G_τ*f)(0) = ∫ (v/2τ) G_τ(v) f(v) dv, so

  a_N(τ) = (1/2τ) E[ V cos(V/2) φ_N(V) ],  V ~ N(0, 2τ),   (6.1)

and E[V^{2n} cos(V/2)] = (−1)^n (d/dt)^{2n} e^{−τt²}|_{t=1/2}. Inserting (B3) (and its one-order-higher analogue) and the Gaussian tail bound of Prop. 3.4:

  a_N(τ) = e^{−τ/4}[ (1−τ/2) + τ(τ²−12τ+12)/(24N²) + a_4(τ)/N⁴ ] + O(N^{−6}),  uniformly on τ∈[1,3],

with a_4 = −τ²(τ³−30τ²+180τ−120)/240 (block4odd; from φ_N = v + v³/12N² + v⁵/120N⁴ + …) and a_4 = τ(−2τ⁴+60τ³−360τ²+15π²τ²−180π²τ+240τ+180π²)/480 (block33; from φ_N = v + v³/12N² + (v⁵/120 + π²v³/16)/N⁴ + …). Both expansions are produced symbolically by `threeblock_asymptotics.py`.

**Proposition 6.2.** For block4odd and block33, τ_N = N²D_N satisfies

  τ_N = 2 − 4/(3N²) + c₂/N⁴ + O(N^{−6}),  c₂ = −8/5 (block4odd),  c₂ = −8/5 − π² (block33).

*Proof.* The leading term a_0(τ)=e^{−τ/4}(1−τ/2) has its unique zero on [0,3] at τ=2 with a_0′(2) = −e^{−1/2}/2 ≠ 0, and a_0 ≥ e^{−1/4}/2 on [0,1]; since |a_N − a_0| ≤ C/N² uniformly on [0,3] (Prop. 3.4 with k=1), a_N has no zero on [0,1] and, by the implicit function theorem applied to the C¹ function (τ, N^{−2}) ↦ a_N(τ), exactly one zero near 2, τ_N, which by Prop. 6.1 is N²D_N. Substituting τ = 2 + c₁/N² + c₂/N⁴ into the expansion and solving order by order: c₁ = −a_2(2)/a_0′(2) with a_2(2) = e^{−1/2}·2(4−24+12)/24 = −(2/3)e^{−1/2}, giving c₁ = −4/3; and c₂ as stated (the O(N^{−4}) coefficient involves a_0″(2), a_2′(2), a_4(2); the algebra is in the script). ∎

**Verification [C]** (`threeblock_exact.py` part (4), mpmath at 30 digits, first zero of the exact F_N):

| N | block33: τ_N | N²(τ_N−2) | N⁴(τ_N−2+4/(3N²)) | N | block4odd: τ_N | N²(τ_N−2) | N⁴(τ_N−2+4/(3N²)) |
|---|---|---|---|---|---|---|---|
| 16 | 1.99461307798305 | −1.379052 | −11.7040 | 17 | 1.99536710538719 | −1.338907 | −1.61066 |
| 64 | 1.99967379466878 | −1.336137 | −11.4840 | 65 | 1.99968432847280 | −1.333712 | −1.60072 |
| 256 | 1.99997965227723 | −1.333508 | −11.4705 | 257 | 1.99997981260037 | −1.333358 | −1.60005 |
| 1024 | 1.99999872842381 | −1.333344 | −11.46966 | 1025 | 1.99999873091269 | −1.333335 | −1.600003 |
| 2048 | 1.99999968210791 | −1.3333361 | −11.469618 | 2049 | 1.99999968241868 | −1.3333337 | −1.6000007 |

−8/5−π² = −11.4696044…, −8/5 = −1.6: agreement to 6–7 digits at N=2048, with the residual decaying like N^{−2} as an O(N^{−6}) term should. Fact (F1)'s N=128 value 1.999918565579 is block33 (exact: 1.999918577051; the solver was 1.1·10^{−8} low), which is why its "−1.34" was drifting.

### 6.3 Why the 1/N term is absent

φ_N − v starts at order N^{−2} because the compensation sits within O(1/N) of the antipode: the removed/added far roots contribute a factor ∏ sin((x−θ_r)/2)^{∓1} = cos((u−ρπ)/2N)^{∓1}·const with ρ=O(1), whose expansion 1 ∓ (u²−2ρπu)/(8N²)+… has no u/N term. For a compensation at a generic angle α the factor is ρ(0)(1 + λu/N + …) with λ = ½cot(α/2)-type constants, and then q_0^N = u cos(u/2)(1+λu/N)+…; the even perturbation (λ/N)·e^{τ∂²}[u²cos(u/2)] = (λ/N)e^{−τ/4}[(u²+2τ−τ²)cos(u/2) − 2τu sin(u/2)] vanishes at u=0 when τ=2 (because E[V²cos(V/2)] ∝ H_2(√τ/2) ∝ τ−2), so the cusp analysis of §6.4 shows the shift is still O(N^{−2}) (of order λ²) — a generic compensation changes the −4/3 but not the order. [P for the vanishing; the resulting constant is O: not computed.]

### 6.4 The asymmetric family block4even: a cusp and the N^{−8/3} term [C, with derivation]

For block4even, φ_N(v) = v + (v³/12 − πv²/4)/N² + …, so q_τ^N = q_τ + N^{−2}(r_τ + r̃_τ) + O(N^{−4}) with the odd part r_τ as before and the even part r̃_τ = −(π/4)e^{τ∂²}[v² cos(v/2)] = −(π/4)e^{−τ/4}[(u²+2τ−τ²)cos(u/2) − 2τu sin(u/2)]. Near (u,τ)=(0,2) write σ = 2−τ, ε=N^{−2}; the local normal form is

  e^{τ/4} q_τ^N(u) = A u − u³/12 + ε β_2 u² + C + …,  A = σ/2 − (2/3)ε + O(εσ, ε², σ²),  C = ε·e^{τ/4} r̃_τ(0) = −(π/2)εσ + O(εσ²).

The u² term is removed by a shift u→u+4εβ_2 at negligible cost. The cubic −u³/12 + Au + C has a real double root iff A³ = (9/16)C², and this happens *before* A reaches 0: with C ≈ −(2π/3)ε² at σ≈(4/3)ε, A_c = (9/16)^{1/3}(2π/3)^{2/3} ε^{4/3} = 1.3515 ε^{4/3}, so

  τ_N = 2 − (4/3)N^{−2} − 2·1.3515·N^{−8/3} + o(N^{−8/3}),  2·1.3515 = 2.7030.

`run_families_A.py block4even` (heat_depth.py, reliable for this family since the block roots stay in their initial gaps):

| N | N²D_N | N²(2−τ_N) | (N²(2−τ_N) − 4/3)·N^{2/3} |
|---|---|---|---|
| 16 | 1.993008041801 | 1.78994 | 2.899 |
| 32 | 1.998429050189 | 1.60865 | 2.775 |
| 64 | 1.999632821246 | 1.50396 | 2.730 |
| 128 | 1.999912099912 | 1.44016 | 2.713 |
| 192 | 1.999961627887 | 1.41455 | 2.703 |
| 256 | 1.999978634911 | 1.40018 | 2.695 |

The N^{2/3}-scaled residual converges to 2.70 as predicted. Making this rigorous requires a cusp (A₂) normal-form argument with the O(N^{−4}) remainder of Prop. 3.4; the leading −4/3 for block4even is therefore [C] here, while the limit 2 is [P] (Theorem 5.4).

## 7. The midpoint-insertion principle

### 7.1 Closed form of the local flow [P]

**Proposition 7.1.** Let p be a real polynomial and L ∈ {cos(u/2), sin(u/2)}. Then

  e^{τ∂²}[ p(u) L(u) ] = e^{−τ/4} · Re[ e^{iu/2} P_τ(u+iτ) ]  (L=cos),  e^{−τ/4} · Im[ e^{iu/2} P_τ(u+iτ) ]  (L=sin),

where P_τ := e^{τ∂²}p = Σ_{k≥0} τ^k p^{(2k)}/k! = E[p(· + √(2τ)Z)] is the heat-evolved polynomial.

*Proof.* By Lemma 3.2, e^{τ∂²}[p(u)e^{iu/2}] = p(u+2τ∂) e^{τ∂²}e^{iu/2} = e^{−τ/4} p(u+2τ∂) e^{iu/2} = e^{−τ/4} e^{iu/2} p(u+iτ+2τ∂)·1, using e^{−iu/2}(u+2τ∂)e^{iu/2} = u+iτ+2τ∂. Finally (u+c+2τ∂)^n·1 = e^{τ∂²}[(u+c)^n] (apply e^{τ∂²}u e^{−τ∂²} = u+2τ∂ n times to the constant function 1, which is fixed by e^{τ∂²}), and e^{τ∂²}[(u+c)^n] = P_τ(u+c) for real c, hence for complex c by polynomial identity in c. Take real/imaginary parts (p real). ∎

Examples (`midpoint_models.py`; all are odd or even in u):
* p=u (3-block): e^{−τ/4}[u cos(u/2) − τ sin(u/2)]  — (3.2).
* p=u²−c², L=sin: e^{−τ/4}[(u²−c²+2τ−τ²) sin(u/2) + 2τu cos(u/2)];  L=cos: e^{−τ/4}[(u²−c²+2τ−τ²) cos(u/2) − 2τu sin(u/2)].
* p=u(u²−4π²), L=cos: e^{−τ/4}[(u³−3uτ²−4π²u+6τu)cos(u/2) − (3u²τ−τ³−4π²τ+6τ²) sin(u/2)].

Which family is which (gap patterns in units π/N; centre of the block at u=0):
* **5-block** [1,1,1,1]: roots 0, ±π, ±2π, ±4π, ±6π… = zeros of (u²−π²)·sin(u/2). (The sites left of the block are even, right of the block even too; the two odd sites ±1 are the midpoints.)
* **double 3-block** [1,1,2,1,1]: roots ±π, ±2π, ±3π, ±5π… = zeros of (u²−4π²)·cos(u/2).
* **7-block** [1]^6: zeros of u(u²−4π²)·cos(u/2); **9-block** [1]^8: u(u²−4π²)(u²−16π²)·cos(u/2); **[1,1,2,2,1,1]**: (u²−9π²)·sin(u/2).

### 7.2 The limit theorem for midpoint-insertion families [P, modulo a hypothesis checked per family]

**Theorem 7.2.** Let a family of N-point ACUE configurations consist of the alternating clock with k added midpoints at fixed sites within O(1) of 0 (polynomial p, lattice L) and k lattice roots removed within O(1) sites of the antipode, so that q_0^N = L·Φ_N with |Φ_N − p| ≤ C(1+|v|^{k+2})/N² on |v|≤N and polynomial global bounds (as in Lemma 3.3; this holds by the same computation, the far factors being ∏cos((u−ρ_iπ)/2N)^{∓1}). Let q_τ := e^{τ∂²}[pL] (Prop. 7.1) and let τ* be the first τ>0 at which q_τ has a real zero of multiplicity ≥2. Assume

 (H) τ* < π²/2, and there is R>0 with q_τ(±R) ≠ 0 for τ∈[0,τ*+1], such that the number of zeros of q_τ in [−R,R] is constant (=n, all simple) for τ<τ*, and equals n−2 (all simple) for τ∈(τ*, τ*+δ].

Then N²D_N → τ*.

*Proof.* Identical to Theorem 5.4 with [−2π,2π] replaced by [−R,R], Lemma 4.1 by (H), and "the colliding pair is a block pair" by Lemma 1.1 (τ* < π²/2). ∎

*When (H) holds automatically.* If the first double zero (u*,τ*) is non-degenerate (q_uu(u*,τ*) ≠ 0), then since ∂_τ q = ∂_u² q the extremum value h(τ) = q_τ(x_ext(τ)) between the colliding pair satisfies h′(τ*) = q_uu(u*,τ*) ≠ 0: the pair crosses transversally and the count drops by exactly 2 — the second half of (H). If instead the collision is a symmetric triple zero at 0 (odd families), (H) follows from a sign change of a(τ) = q_τ′(0). The first half of (H) — that no earlier double zero exists — is the part that must be verified for each p; for p=u it is Lemma 4.1.

### 7.3 First-order finite-N correction at a fold [P]

**Proposition 7.3.** In the setting of Theorem 7.2 with a non-degenerate first double zero (u*,τ*) and q_τ^N = q_τ + N^{−2}r_τ + O(N^{−4}) in C² near (u*,τ*) (r_τ := e^{τ∂²}[L ψ], ψ := lim N²(Φ_N − p)),

  N²(τ_N − τ*) → − r_{τ*}(u*) / q_uu(u*,τ*).

*Proof.* The extremum value h_N(τ) of q_τ^N between the pair is C¹ in (τ, N^{−2}) near (τ*,0) with h_N(τ) = h(τ) + N^{−2}r_τ(u*) + O(N^{−4}) (the extremum shifts by O(N^{−2}) but q_u=0 there, so the value shifts only at second order); h′(τ*) = q_uu(u*,τ*) ≠ 0; implicit function theorem. ∎

### 7.4 The examples [P]/[C]

**5-block and double 3-block: τ* = 2 exactly.** For p=u²−c² the double-zero equations reduce to one variable: from q=0 one eliminates the bracket u²−c²+2τ−τ², and q_u=0 becomes

  τ = T(u) := u(1−cos u)/(u−sin u) (L=sin),  τ = T̃(u) := u(1+cos u)/(u+sin u) (L=cos),

after which q=0 reads c² = K(u) := u²+2τ−τ²+2τu cot(u/2) resp. c² = K̃(u) := u²+2τ−τ²−2τu tan(u/2) with τ=T(u) resp. T̃(u). [P] At u=π (L=sin): T(π)=2, K(π)=π²; at u=2π (L=cos): T̃(2π)=2, K̃(2π)=4π² — so the 5-block model has a double zero at (u,τ)=(π,2) and the double 3-block model at (2π,2), both non-degenerate (q_uu(π,2) = −2e^{−1/2} = −1.21306 for the 5-block, q_uu(2π,2) = +2e^{−1/2} for the double 3-block, symbolically). Directly: for the 5-block q_τ(π) = e^{−τ/4}τ(2−τ) and q_τ′(π) = e^{−τ/4}π(2−τ). [C] A scan of the reduced systems over u∈(0,60π) (`fold_constants.py` companion scan, 6·10⁶ points) finds no other solution with τ ≤ 6: the first double zero is at τ*=2 in both cases, and the zero-count scan of q_τ on (0,4π) confirms the count drops exactly at τ=2. So both families have lim N²D_N = 2, with (H) checked numerically and the double zero at τ=2 exact.

In words: in the 5-block the roots starting at π and 2π first move apart (q_τ(π)>0 for 0<τ<2 pushes the π-root left), then return and meet *at* π exactly when τ=2; in the double 3-block the outer gap (2π,3π) closes at u=2π, τ=2, while the inner gap (π,2π) is still open.

**7-block and 9-block.** The first double zero of u(u²−4π²)cos(u/2) is at u*=5.9643126848, τ*=**2.03812605359** (q_uu=14.478): the pair starting at (2π,3π) collides at u*<2π, both roots having drifted inward; the 9-block model gives τ*=2.0689 (zero count in (0,6π) drops 5→3 at τ=2.0688935, pair from (4π,5π)). Longer blocks collide later. This matches the complete enumerations: the maximiser of N²D at N=11 is [1,1,1,1,1,1,2,2,8,2,2] (a 7-block) with 1.9918, and at N=12 it is a 8-block with 2.00002 > 2 (`enum_N9_12.log`); the 3-block ceases to be the maximiser at N=11, and the supremum of the lattice constant ρ_∞ over families is strictly larger than 2 [C].

**First-order corrections (Prop. 7.3, `fold_constants.py`)** with ψ the N^{−2} coefficient of Φ_N (from the far factors cos((u∓π)/2N) etc.):

| family | ψ(u) | r_{τ*}(u*) | q_uu(u*,τ*) | N²(τ_N−τ*) → |
|---|---|---|---|---|
| 5-block (N odd) | u⁴/6 − π⁴/6 | −3.23483 = −(16/3)e^{−1/2} | −1.21306 = −2e^{−1/2} | **−8/3** |
| 5-block (N even, sites N−2,N removed) | u⁴/6 + πu³/2 + π²u²/4 − π³u/2 − 5π⁴/12 | −3.23483 | −1.21306 | −8/3 |
| double 3-block (N even) | u⁴/6 − 3π²u²/4 + π⁴/3 | 3.23483 | 1.21306 | **−8/3** |
| 7-block (N odd) | u⁵/4 − π²u³/3 − 8π⁴u/3 | 60.1425 | 14.4784 | **−4.1540** |

Robust-solver values (`heat_depth_robust.py`, [C]):

| family | N | N²D_N | N²(τ*−N²D_N) | predicted |
|---|---|---|---|---|
| 5-block | 65 | 1.999367031298 | 2.674 | 8/3 = 2.667 |
| 5-block | 129 | 1.999839626618 | 2.669 | |
| 5-block | 193 | 1.999928321837 | 2.670 | |
| 5-block | 257 | 1.999959727377 | 2.660 | |
| double 3-block | 64 | 1.999343288988 | 2.690 | 2.667 |
| double 3-block | 128 | 1.999836878627 | 2.673 | |
| double 3-block | 256 | 1.999959413409 | 2.660 | |
| 7-block | 33 | 2.034196338652 | 4.28 | 4.154 |
| 7-block | 65 | 2.037135310173 | 4.19 | |
| 7-block | 129 | 2.037870579847 | 4.25 | |

(For the 7-block the robust solver's bracket does not close below 10^{−4} for N ≥ 193 — the pair sits at u≈5.96 where three roots are within 0.6 of each other — so those N are not reported.)

**Sanity of the solvers [C].** `heat_depth_robust.py` reproduces the exact block33 values 1.994613077983 (N=16) and 1.998686923391 (N=32) to 1.4·10^{−9} and 2.3·10^{−9}. `heat_depth.py` gives for the 7-block 1.775 (N=16), 1.827 (32), 1.842 (128), 1.8428 (256), all wrong; the independent root-based bisection of `defect_families.py` gives 2.0177 (N=16) and 2.0301 (N=24), agreeing with the robust solver (2.0177, 2.0302) and with the local model. The failure is in `depth_pair`: the Newton iterate for the extremum is rejected when it leaves the *initial* gap (a,b)=(θ_i,θ_{i+1}); in the 7-block both roots of the outer gap drift by ≈0.3 (in u) before colliding. `run_families.py block5` is affected only at the O(N^{−2}) level (it reports N²(2−τ_N) ≈ 9.3 instead of 8/3), `disloc`, `block4`, `block33` are unaffected.

## 8. What is proved, what is computed, what is open

| statement | status |
|---|---|
| Closed forms of Q_0 and of the coefficients a_j for the three families (Lemmas 2.1–2.3) | **[P]** + [C] check |
| Heat flow = Gaussian convolution; exact local solution q_τ (Lemmas 3.1, 3.2) | **[P]** |
| Uniform C¹ convergence q_τ^N → q_τ on [−2π,2π]×[0,3] with error O(N^{−2}) (Prop. 3.4) | **[P]** (elementary Taylor-remainder bounds in Lemma 3.3 stated with an unspecified absolute constant C_0; the expansions are produced symbolically and the rates confirmed numerically) |
| Real zeros of q_τ (Lemma 4.1) | **[P]** |
| **lim N²D_N = 2 for block4odd, block4even, block33 (Theorem 5.4)** | **[P]** |
| D_N = first zero of P_s′(1) for the symmetric families (Prop. 6.1) | **[P]**, verified to 10^{−8}/10^{−9} |
| τ_N = 2 − 4/(3N²) + c₂/N⁴ + O(N^{−6}), c₂ = −8/5, −8/5−π² (Prop. 6.2) | **[P]** (coefficient algebra by script; remainder bounds as in Lemma 3.3); verified to 7 digits |
| block4even: τ_N = 2 − 4/(3N²) − 2.703N^{−8/3} + … | **[C]** with a cusp normal-form derivation; making it [P] needs the O(N^{−4}) remainder in C² — routine but not written |
| Midpoint-insertion closed form (Prop. 7.1); limit theorem under (H) (Thm 7.2); fold correction (Prop. 7.3) | **[P]** |
| 5-block and double 3-block: double zero at τ=2 exactly | **[P]**; that it is the first: **[C]** (reduced one-variable scan; an interval-arithmetic certificate of "K(u)≠c² for T(u)<2" would close it) |
| 7-block τ*=2.0381260536, 9-block 2.0689; N²(τ_N−τ*) → −8/3, −8/3, −4.154 | **[C]** |
| 3-block is the maximiser of N²D over non-clock ACUE configurations | **false for N ≥ 11** [C]: longer blocks are deeper; the supremum over families exceeds 2 (7-block 2.038, 9-block 2.069, enumeration argmax at N=12 is 2.00002 already). Determining sup_families lim N²D (half-block? ) is **[O]** |
| Compensation at a generic angle α: limit still 2, constant in N^{−2} depends on α | limit **[P]** by the same proof once a 1/N tilt is allowed in Lemma 3.3 (the tilt is an even perturbation and does not affect Theorem 5.4); the N^{−2} constant **[O]** |

The one step of Task A's suggested route that was *not* needed is the Euler–Maclaurin treatment of the alternating Fourier sum with its endpoint terms: the Gaussian-convolution identity (Lemma 3.1) turns the finite-N function into a smooth perturbation of the limit at once, and Theorem A + confinement replaces Hurwitz/Rouché in the complex plane by a real-variable count.

## 9. Scripts (all in this directory)

* `threeblock_exact.py` — closed forms, coefficients, D_N as first zero of P_s′(1) vs enumeration and heat_depth, high-precision τ_N and the expansion coefficients.
* `threeblock_asymptotics.py` — symbolic derivation of φ_N expansions, a_0, a_2, a_4 and of c₁=−4/3, c₂.
* `local_convergence_check.py` — numerical verification of Prop. 3.4 at orders N^{−2} and N^{−4}.
* `midpoint_models.py` — Prop. 7.1 closed forms, first double zero of the local models (3-, 5-, 7-, 9-block, double 3-blocks).
* `fold_constants.py` — ψ, r_{τ*}(u*), q_uu and the fold constants of Prop. 7.3.
* `run_families_A.py` — heat_depth.py runs (block4even, and the block5/two3/block7 runs that exposed the failure mode); logs `famA.log`, `famA_block4even.log`.
* `heat_depth_robust.py` — corrected solver; logs `robust2.log`, `robust3.log`.
