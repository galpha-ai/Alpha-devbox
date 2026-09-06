# Task C — The ceiling conjecture N²D < 2: refuted at N = 12, and replaced by the domain-wall constant C* = 2.11466488…

**Fable, 6 September 2026.** Scripts `push_C_*.py`, logs `push_C_*.log` (same directory). Statuses: **[P]** proved
here, **[C]** computed (script + numbers), **[O]** open. Nothing below is cited from memory as verified; the only
recalled fact is flagged "(recalled)".

Conventions (as in the task): N points on the circle, alternating clock = odd sites of ℤ/2N, gaps in units π/N;
flow P_s(z) = Σ a_j e^{s j(N−j)} z^j, equivalently Q_s = e^{sN²/4} e^{s∂²} Q_0 with Q_0(x) = ∏ sin((x−θ_j)/2); depth
D = first collision time; τ = N²s; local variable u = Nx; "N²D" always means N²·D.

## 0. Results in one screen

| # | statement | status |
|---|---|---|
| 1 | **The ceiling conjecture is false.** At N = 12 the orbit [1⁷,2,2,9,2,2] has N²D = 2.000017720049… > 2 (enumeration; re-verified by mpmath `polyroots` at 50 digits and by the N-body ODE to 10⁻¹²). For N ≥ 12 the maximum exceeds 2, and it increases with N: 2.0079 (13), 2.0281 (16), 2.0450 (20), 2.0708 (32), 2.0926 (64), 2.1036 (128), 2.1091 (256), 2.1110 (384), 2.1119 (512). N²D < 2 on the whole AH support holds exactly for N ≤ 11. | **[C]** |
| 2 | The argmax is the symmetric 3-block only for N ≤ 10. For N ≥ 11 it is the **run\|clock\|hole** configuration [1^{L−1}, 2^k, L+1, 2^k] (a run of L consecutive sites, two clock buffers of k points, one hole of L+1 sites, N = L+2k), with k/N → 0.25, L/N → 0.5. Complete enumeration N ≤ 12, a stochastic hill-climb over all gap patterns at N = 14, 16, 20, 24, and an exhaustive search over macroscopic segment profiles at N = 32, 48 found nothing else. | **[C]** |
| 3 | The premise "long runs collapse fast at the run edge" (values 1.84, 1.78 in `runs.log`, `families2.log`, `local_models.py`) is a **numerical artifact** of the fixed-initial-bracket extremum tracker in `heat_depth*.py`/`local_models.py`, which declares a false collision as soon as the run drifts. The true local (N → ∞) constants τ*_L of an L-run in the clock are 2.0000 (L=3), 1.9630 (4), 2.0000 (5), 2.0227 (6), 2.0381 (7), 2.0490 (8), 2.0573 (9), …, 2.1128 (241): **increasing** in L from L = 4 on, with τ*_L = C* − 0.45/L + O(L⁻²). Verified by `polyroots` at 60 digits (7-run, N = 63: 2.03707095080776 = ODE value). | **[C]** |
| 4 | **The L → ∞ limit is an exact local model:** semi-infinite run ∪ semi-infinite clock has q_0(u) = cos(u/2)/Γ(u/2π), and its heat flow is q_τ(u) = e^{−τ/4} Re[e^{iu/2} G_τ(u+iτ)], G_τ(w) = (2πi)⁻¹∫_Hankel exp(t + τ(ln t)²/4π² − (w/2π) ln t) dt. **C\* := first double-zero time of q_τ** is the domain-wall constant. Hankel-integral evaluation: **C\* = 2.1146648843** (double zero at u = 0.0934π); lattice extrapolation of τ*_L: 2.114665 — agreement to 7 digits. | **[P]** (model, identity), **[C]** (value) |
| 5 | 3-block local model: q_τ = e^{−τ/4}(u cos(u/2) − τ sin(u/2)); zeros solve u cot(u/2) = τ; since u cot(u/2) ≤ 2 with maximum only at u = 0 and is strictly decreasing on every (2πn, 2π(n+1)), all zeros are real and simple for τ < 2 and the first collision is the symmetric **triple** collision at τ = 2 exactly. | **[P]** |
| 6 | 5-block local model (added midpoints at 0, 2π): q_τ e^{τ/4} = (u²−2πu+2τ−τ²)cos(u/2) − τ(2u−2π) sin(u/2); q_τ(0) = −τ(τ−2)e^{−τ/4}, q_τ′(0) = π(τ−2)e^{−τ/4}: a **double** zero at the edge u = 0 at τ = 2 exactly [P]; no double zero for τ < 2 (certificate: zero count constant = 9 on [−6π,6π], min\|h′\| ≥ 0.264 on τ ≤ 1.99) [C]. Curiosity: q_τ(0) ∝ τ(τ−2) also for k = 3 but not k ≥ 4 (sympy). | **[P]/[C]** |
| 7 | **Unique-1-gap ceiling theorem.** If exactly one gap equals π/N (all others ≥ 2π/N) then N²D ≤ τ₁(N), an explicit comparison-ODE constant: τ₁ = 1.9861 (N=8), 1.8510 (12), 1.7209 (32), 1.6880 (64) ↓ 1.65737 (N → ∞). Hence N²D < 2 for every unique-1-gap configuration and every N (N ≤ 7 by enumeration, max 1.4663). The true class maximum is 1.4717 (N = 12), so the constant is within 13% at N = ∞. The proof uses only Theorem A, the mean-value bracket bound and elementary trig inequalities; the same proof gives D ≤ 0.16793·δ² = 1.3434·(δ²/8) for **any** circle configuration whose closest pair (gap δ) is isolated (all other gaps ≥ 2δ). | **[P]** |
| 8 | Monotonicity: "adding roots can only speed up the collapse" is **false** (5-block → 7-block: 2 → 2.038); "adding roots can only slow it" is **false** (adding a root next to the compensating hole of a 3-block creates a dislocation pair, 2 → 1.42). What the data support: removing a root next to the critical pair always sped up the collapse; adding roots that do not create a new 1-gap pair adjacent to a ≥ 3-gap never slowed it below the original value (14 superset tests at N = 64, §5). | **[C]** |
| 9 | Nyquist row \|p_N\|² = (n_even − n_odd)²: no monotone upper envelope; max N²D versus \|p_N\|² is non-monotone at every N ≥ 6; Pearson correlation of N²D with \|p_N\|²/N² over all orbits is +0.13 at N = 12 (Spearman +0.11). The 4-compensated 3-block has the **maximal** imbalance (N−2)² among non-clock configurations, the depth maximizers for N ≥ 11 have \|p_N\|² = 0 (L even) or (2k+1)² (L odd). Only the ACUE-weighted *mean* of N²D increases weakly with \|p_N\|² (1.41 → 1.50 at N = 12). | **[C]** |
| 10 | **Corrected conjecture (§9):** for all N and all non-clock lattice configurations, π²/8 ≤ N²D < C* = 2.11466488…, with sup_N max N²D = C* approached from below along the run\|clock\|hole family; the exact missing lemma is a protection inequality β_config(τ) ≤ β_wall(τ) for the first-colliding pair (§7). | **[O]** |

## 1. Solvers and the correction of an earlier numerical artifact

Three independent depth solvers were used (`push_C_verify.py`, `push_C_fast.py`):

* **Method A** — mpmath `polyroots` of P_s at 25–90 digits, off-circle indicator max_j \|\|z_j\|−1\| and the smallest
  root distance scanned on a τ-grid (to check that the on-circle set is an interval), then bisection. Ground truth.
* **Method C** — direct integration of Lemma 1, θ_j′ = −Σ_k cot((θ_j−θ_k)/2), with DOP853 (rtol 10⁻¹²) until the
  smallest gap reaches 10⁻⁵, then the exact two-body end law s* = s − log cos(g/2). Agrees with Method A to 10⁻¹²
  on nine test configurations at N = 12…24 (`push_C_fast_validate.log`), to all nine printed digits on the 7-run at N = 63
  (2.03707095 vs 2.03707095080776, `push_C_verify63.log`, 60 digits), and (pending, `push_C_verify128.log`) on the wall configuration at N = 128.
  Cost O(N²) per step; used for all N > 24.
* **Method R** — the `np.roots` bisection of `acue_depth_enum.py`: exact to 10⁻¹¹ for double collisions but
  underestimates triple collisions by 10⁻⁸…10⁻⁷ (eigenvalue accuracy ε^{1/3} at a triple root) and **fails**
  (returns 1.87 or 0) for runs of length ≥ 15 at N ≥ 20 because the coefficients grow like 2^N.

**The artifact.** `heat_depth.py`, `heat_depth_mp.py` and `local_models.py` track the extremum of Q_s between two
zeros with Newton, but reject the iterate — and declare a collision — as soon as it leaves the *initial* interval
(θ_i(0), θ_{i+1}(0)). For a run of L ≥ 7 sites the whole run contracts and drifts by O(1) in u before the true
collision, so the tracker reports a false early collision (e.g. 1.843 for the 7-block instead of 2.038; 1.78 for
L = 8 instead of 2.049; the "halfblock" values 2839 in `families2.log` are the same failure). The symmetric 3-block
and the dislocation have a pinned or nearly pinned pair, so their earlier values (2 − 1.34/N², 1.419640342) are
correct and are reproduced here. **All statements in the task premise (F3) about long runs being fast should be
discarded**; everything below uses Methods A and C only.

## 2. Evidence from the complete enumerations, N ≤ 12 (`push_C_tabulate.log`, `push_C_tables.log`, `push_C_recheck_top.log`)

Maximum of N²D over non-clock orbits, its argmax, and the symmetric 3-block values (block4 = 4-gap opposite,
block33 = 3,3 opposite; the top-12 of every N were re-verified with Method A at 30 digits):

| N | max N²D | argmax gaps | block33 | block4 | #orbits ≥ 1.95 |
|---|---|---|---|---|---|
| 4 | 1.8483925 | [1,1,3,3] = block33 | 1.8483925 | 1.7946941 | 0 |
| 5 | 1.9438834 | [1,1,2,4,2] = block4 | – | 1.9438834 | 0 |
| 6 | 1.9526287 | [1,1,2,3,3,2] = block33 | 1.9526287 | 1.9323562 | 1 |
| 7 | 1.9720950 | block4 | – | 1.9720950 | 2 |
| 8 | 1.9761218 | block33 | 1.9761218 | 1.9663749 | 4 |
| 9 | 1.9832893 | block4 | – | 1.9832893 | 11 |
| 10 | 1.9854576 | block33 | 1.9854576 | 1.9799810 | 50 |
| 11 | **1.9918105** | **[1⁶,2,2,8,2,2]** (L=7,k=2) | – | 1.9888697 | 156 |
| 12 | **2.0000177** | **[1⁷,2,2,9,2,2]** (L=8,k=2) | 1.9901672 | 1.9867593 | 436 |

(Values with a triple collision — the 3-blocks — are quoted from Method A; the enumeration file is low by ≤ 6·10⁻⁷.)

Top-10 at N = 12 (all run\|clock\|hole-like): 2.0000177 [1⁷,2,2,9,2,2]; 1.9956054 [1⁶,2,2,5,5,2,2]; 1.9951460
[1⁵,2,2,2,7,2,2,2]; 1.9944455 [1⁶,2,2,4,6,2,2] (×2 mirror); 1.9938695 [1⁶,2,2,7,3,2,2] (×2); 1.9937907
[1⁶,2,2,8,2,2,2] (×2); 1.9902489 [1⁵,2,2,2,6,3,2,2]. The 3-block (block33) is 12th. At N = 12 the collision of the
maximizer is a simultaneous symmetric double collision of the two outer pairs of the 8-run (root angles 1.1828 and
5.8172 in units π/N at τ = D·N²); at N = 11 likewise (1.1361, 4.8639).

Maximum by longest occupied run L (Table 1 of `push_C_tables.log`): at N = 12, L = 2: 1.4957, 3: 1.9902, 4: 1.9613,
5: 1.9780, 6: 1.9952, 7: 1.9956, 8: **2.0000**, 9: 1.9727, 10: 1.9711, 11: 1.8372, 12: 1.8318. Maximum on structure
classes (Table 2): unique 1-gap 1.4519 (N=4) … 1.4717 (N=12), always the dislocation [1,2,…,3,…] with the 3-gap far
away; isolated 1-gaps (no two adjacent) 1.4519 … 1.4957; L = 3 (3-blocks) as above; L ≥ 4: 1.7790 (4) … 2.0000 (12).

Minimum values (for completeness, not part of this task): 1.3863, 1.3726, 1.3531, 1.3426, 1.3304, 1.3229, 1.3146,
1.3091, 1.3032 (N = 4…12), all ≥ π²/8 = 1.2337 (Theorem C(i)).

## 3. The maximizers for N ≥ 11: the run\|clock\|hole family

The family F(N; L, k₁, k₂) = [1^{L−1}, 2^{k₁}, L+1, 2^{k₂}], N = L + k₁ + k₂ (the hole is forced to be L+1 by the
parity count: L consecutive sites contain ⌈L/2⌉ sites of the wrong parity, and the clock buffers are on the same
sublattice on both sides).

**(a) Symmetric buffers are optimal** (`push_C_family_asym.log`, N = 16, 20, 24, 32, all k₁ ≤ k₂ ≤ 10): the maximum is
always at k₁ = k₂; e.g. N = 20: (4,4) 2.045048 > (3,5) 2.036180 > (2,6) 2.018829.

**(b) The maximum over the family** (`push_C_family_sym.log`, `push_C_iface_largeN.log`, `push_C_iface_384_512.log`;
Method C):

| N | max N²D | k* | L* = N−2k* | N | max N²D | k* | L* |
|---|---|---|---|---|---|---|---|
| 12 | 2.0000177 | 2 | 8 | 40 | 2.0794929 | 9 | 22 |
| 13 | 2.0079088 | 3 | 7 | 48 | 2.0853005 | 11 | 26 |
| 14 | 2.0167610 | 3 | 8 | 64 | 2.0925893 | 15 | 34 |
| 15 | 2.0231992 | 3 | 9 | 80 | 2.0969788 | 19 | 42 |
| 16 | 2.0280554 | 3 | 10 | 96 | 2.0999120 | 23 | 50 |
| 18 | 2.0378406 | 4 | 10 | 128 | 2.1035866 | 31 | 66 |
| 20 | 2.0450484 | 4 | 12 | 160 | 2.1057956 | 39 | 82 |
| 22 | 2.0514630 | 5 | 12 | 256 | 2.1091153 | 63 | 130 |
| 24 | 2.0564578 | 5 | 14 | 384 | 2.1109628 | 95 | 194 |
| 28 | 2.0646502 | 6 | 16 | 512 | 2.1118874 | 127 | 258 |
| 32 | 2.0708192 | 7 | 18 | | | | |

The optimum has k*/N → 0.25, L*/N → 0.5 (a macroscopic profile: density 2 on a quarter of the circle, density 1
on a half, density 0 on a quarter), and max N²D increases with N with increments per doubling 0.043, 0.022,
0.011, 0.0055, 0.0028 (N = 16→32→64→128→256→512): geometric with ratio ½, so the fixed-N maxima extrapolate to
2.1119 + 0.0028 ≈ 2.1147 = C* (§4); at fixed N the maximum stays below C*, with C* − max = 1.42/N to three digits for N = 64, 128, 256, 512.

**(c) Nothing else found.** (i) Hill-climb over all compositions of 2N into N parts (moves: transfer one unit
between gaps, swap two gaps; 30/30/25/20 restarts × 400–800 steps; `push_C_hillclimb.log`): the global best at
N = 14, 16, 20, 24 is F(N; L*, k*, k*) in every case (2.016761, 2.028055, 2.039239, 2.056458); the next-best patterns
are the same family with the hole split or a buffer shifted by one. (ii) Exhaustive search over symmetric
macroscopic profiles run\|g₁^{b₁}\|g₂^{b₂}\|hole\|g₂^{b₂}\|g₁^{b₁} with g_i ∈ {2,3,4} and two-run/two-hole profiles at
N = 32 (513 profiles) and N = 48 (1085): every top entry is the family (buffers of 3- or 4-gaps never help;
`push_C_segments.log`).

**(d) The colliding pair** is always the outermost 1-gap of the run (pair index 0 or L−2; both, simultaneously, by
symmetry).

## 4. Local models: why the 3-block gives exactly 2, and why it is not the slowest defect

### 4.1 The heat flow of p(u) cos(u/2) [P]

For a local defect consisting of added roots at the even multiples a_i of π (the lattice roots being the odd
multiples), q_0(u) = p(u) cos(u/2), p(u) = ∏(u − a_i). Since (∂ + i/2)² = ∂² + i∂ − 1/4,

  e^{τ∂²}(e^{iu/2} p) = e^{iu/2} e^{τ(∂+i/2)²} p = e^{−τ/4} e^{iu/2} e^{iτ∂} e^{τ∂²} p = e^{−τ/4} e^{iu/2} P_τ(u + iτ),
  P_τ := e^{τ∂²} p = Σ_j τ^j p^{(2j)}/j!,

hence **q_τ(u) = e^{−τ/4} Re[e^{iu/2} P_τ(u+iτ)]**, and the zeros of q_τ are the solutions of the phase equation

  **φ_τ(u) := arg P_τ(u+iτ) + u/2 ≡ π/2 (mod π),  φ_τ′(u) = 1/2 − Σ_{ζ ∈ zeros(P_τ)} (τ − Im ζ)/((u − Re ζ)² + (τ − Im ζ)²).**

A double zero of q_τ is a point where φ_τ ≡ π/2 (mod π) and φ_τ′ = 0; a triple zero needs φ_τ″ = 0 as well. Every
zero ζ of P_τ below the line Im = τ contributes a Lorentzian dip of depth 1/(τ − Im ζ) to φ_τ′; for real ζ the dip has
depth 1/τ, so **as long as P_τ has a real zero, φ_τ′ < 0 somewhere for all τ < 2**, i.e. the "wiggle" that carries the
extra zeros cannot flatten before τ = 2. (Flattening is only one of the two collision mechanisms; the other — a
local extremum of φ crossing a level — is what happens for asymmetric defects.)

### 4.2 The 3-block (k = 1): τ* = 2, triple collision [P]

p = u: q_τ = e^{−τ/4}(u cos(u/2) − τ sin(u/2)), zeros at u = 0 and where **u cot(u/2) = τ**. The function
f(u) = u cot(u/2) is even, f(0⁺) = 2, and f′(u) = (sin u − u)/(2 sin²(u/2)) < 0 for u > 0, so f is strictly decreasing
on (0, 2π) from 2 to −∞ and on each (2πn, 2π(n+1)), n ≥ 1, from +∞ to −∞. Hence for 0 < τ < 2 the zeros are exactly
0, ±u₁(τ) with u₁ ∈ (0, π), and one zero in each (2πn, 2π(n+1)) and its mirror — all simple, none colliding; at
τ = 2 the three zeros near 0 merge (q_2(u) = −e^{−1/2}u³/12 + …), and for τ > 2 they are gone. So **τ* = 2 exactly, and
the reason is the elementary inequality u cot(u/2) ≤ 2**. In phase language: φ′(u) = 1/2 − τ/(u²+τ²) ≥ 1/2 − 1/τ, the
single dip flattens exactly at τ = 2, and by the symmetry u ↦ −u the pinned zero sits at the level π/2, so the
collision must be the flattening (triple) one. Finite N: N²D = 2 − 1.34/N² (F1, confirmed by Method C: 1.9996843 at
N = 65, 1.9999795 at N = 257).

### 4.3 The 5-block (k = 2): τ* = 2, double collision at the edge [P + C]

p = u(u − 2π): P_τ = u² − 2πu + 2τ and

  q_τ(u) e^{τ/4} = (u² − 2πu + 2τ − τ²) cos(u/2) − τ(2u − 2π) sin(u/2)   (sympy, `push_C_localmodel_sym.log`).

At the edge u = 0: q_τ(0) e^{τ/4} = τ(2 − τ), q_τ′(0) e^{τ/4} = −π(2 − τ) — both vanish at τ = 2 and
q_2(u) e^{1/2} = −u² + πu³/6 + …: a double zero at u = 0 at τ = 2 [P]. In the symmetric variable v = u − π,
h(v) = (v² − a²) sin(v/2) + 2τv cos(v/2), a² = π² − 2τ + τ², is odd; the central lattice zero v = 0 is pinned. The
certificate `push_C_fiveblock_cert.py` (25 digits) shows that for τ ∈ {0, 0.01, …, 1.99} the number of zeros of h on
[−6π, 6π] is constant (9) and min\|h′\| over all zeros is ≥ 0.264, and that at τ = 2, h(−π) = h′(−π) = 0, h″(−π) = 2. So
**the 5-block's first collision is also at τ = 2**, but it is a double (not triple) zero, located at the original
position of the edge added root: the lattice zero coming from −π and the added zero returning to 0 meet there.
Exact phase check: with c² = π² − 2τ, (π ∓ c)² + τ² = 2π(π ∓ c), so at τ = 2, φ′(0) = 1/2 − (1/π)·2π/(π²−c²) = 1/2 − 2/4 = 0.

Sympy (`push_C_localmodel_sym.log`): q_τ(0) e^{τ/4} = 6πτ(τ − 2) for k = 3 as well, but q_τ′(0) = −8 ≠ 0 there, and for
k = 4 the factor (τ − 2) is absent (value 16 at τ = 2). The coincidence "the edge zero passes through its starting
point at τ = 2" is therefore special to k ≤ 3 and is not the mechanism for longer runs.

### 4.4 L-runs, the Gamma representation and the domain-wall constant C* [P model, C value]

For k added midpoints at 0, −2π, …, −2π(k−1): p_k(u) = ∏_{j=0}^{k−1}(u + 2πj) = (2π)^k Γ(z + k)/Γ(z), z = u/2π. As
k → ∞ with the normalisation Γ(k)(2π)^k k^{z}, Γ(z+k)/(Γ(k)k^z) → 1, so p_k/(Γ(k)(2π)^k k^{u/2π}) → 1/Γ(u/2π); the
factor k^{u/2π} = e^{u ln k/2π} is a pure exponential, and e^{τ∂²}(e^{cu}f) = e^{c²τ}e^{cu}(e^{τ∂²}f)(u + 2cτ) is a
translation, so it does not affect collision times (it is the logarithmically divergent drift of a semi-infinite
run). Hence the **semi-infinite run ∪ semi-infinite clock** (all multiples of π that are ≤ π, and the odd multiples
beyond) has the exact local model

  **q_0(u) = cos(u/2)/Γ(u/2π)**  (zeros: odd multiples of π from cos, and 0, −2π, −4π, … from 1/Γ),

and by Hankel's formula 1/Γ(z) = (2πi)⁻¹∫_H e^t t^{−z} dt with the mode t^{−z} = e^{−z ln t} flowing to
e^{τ(ln t)²/4π²}e^{−z ln t} (the factor e^{t} on the contour dominates the sub-polynomial growth e^{τ(ln t)²/4π²}),

  **q_τ(u) = e^{−τ/4} Re[e^{iu/2} G_τ(u + iτ)],  G_τ(w) = (2πi)⁻¹ ∫_H exp(t + τ(ln t)²/4π² − (w/2π) ln t) dt.**

`push_C_wall_gamma.py` evaluates G_τ on the contour {\|t\| = 1} ∪ two rays (checked against 1/Γ to 12 digits at τ = 0)
and tracks the zeros: at τ = 0, 1, 1.5, 2, 2.05, 2.1 the edge pair (0, π) is at (0, 1)π, (−0.060, 0.748)π,
(−0.077, 0.563)π, (−0.026, 0.273)π, (−0.003, 0.224)π, (0.043, 0.152)π, and at τ = 2.12 it is gone; the other zeros
(−3π, −2π, −π, 3π) move by < 0.15π. A first bisection on the zero count (`push_C_wall_gamma.log`) gives 2.11445, biased low by ≈ g²/8 because a
sign-change grid misses the pair once its gap is below the grid spacing; tracking the extremum of q_τ between the two
zeros (Newton on q_τ′ with derivatives taken under the Hankel integral, secant in τ; `push_C_wall_gamma_refine.log`)
gives **C\* = 2.1146648843**, the double zero sitting at u_c = 0.29337514 = 0.0933842π. Independently, the lattice values τ*_L = lim_N N²D(N, L) (Richardson in 1/N² from N ≈ 4L
and 8L, `push_C_wall_const.log`):

| L | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 12 | 15 | 21 | 31 | 41 | 61 | 81 | 121 | 161 | 241 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| τ*_L | 2.0000 | 1.9630 | 2.0000 | 2.0227 | 2.0381 | 2.0490 | 2.0573 | 2.0637 | 2.0730 | 2.0819 | 2.0919 | 2.0995 | 2.1033 | 2.1071 | 2.1090 | 2.1109 | 2.1118 | 2.1128 |

and the fit τ*_L = C* + c₁/L + c₂/L² over L = 61…241 gives **C* = 2.114665, c₁ = −0.452** (linear fit over
121…241: 2.114684). The lattice extrapolation and the Hankel-model value 2.1146648843 agree to 7 digits, which
validates both the identification of the local model and the ODE solver at N up to 1929. τ*_L is monotone increasing in L
for L ≥ 4 (odd and even L interleave: the parity domain wall of even L has q_0 = (u−2π)/(Γ(u/2π)Γ(½ − u/2π)) for L = 4,
value 1.9630, and converges to the same C*), and the single exception is L = 3 > L = 4.

**So the 3-block is the slowest-collapsing defect only among runs of length ≤ 5**; among all local defects tested
(runs, pairs of 3-blocks, 3-block with adjacent holes, dislocations) the order is: dislocation [3,1] 1.419640 <
block_4adj [4,1,1] 1.796827 < block_3adj3 [3,1,1,3] 1.856676 < half-block [1^{N−1},N+1] 1.8384 < 4-run 1.9630 <
3-block = 5-block = two separated 3-blocks = 2.0000 < 6-run 2.0227 < 7-run 2.0381 < … < C* = 2.1147
(`push_C_otherdefects.log`, `push_C_monotone.log`).

### 4.5 What makes the wall slower than the 3-block (diagnostics, `push_C_trajectories.log`, `push_C_beta_envelope.log`) [C]

Write the critical gap equation as g′ = −2cot(g/2) + B, B = Σ_k[cot(x_b^k/2) − cot(x_a^k/2)] ≥ 0 (Theorem A), and
β := B/(N²g) (the "protection" per unit gap; the linearised stiffness bound is B ≤ g S*, and B/(gS*) ≈ 0.6 for all
the defects here — the mean-value bound loses 40%). Along the trajectories (τ = 0 → 0.97 N²D):

| defect | N²D | β(0) | β at τ ≈ 1.0 | β at τ ≈ 1.9 | drift (θ_a′+θ_b′)/2N at τ=0 |
|---|---|---|---|---|---|
| dislocation N=32 | 1.4196 | 0.101 | 0.101 | 0.101 (τ=1.39) | 0.16 |
| 3-block N=257 | 2.0000 | 0.203 | 0.288 | 1.09 (τ=1.83) | 0.32 |
| wall N=256, L=130 | 2.1091 | 0.264 | 0.295 | 0.343 (τ=1.93) | 0.8–1.1 (N = 12–28) |

(The dislocation's β is constant to three digits along its whole trajectory; the 3-block's grows because its
collision is triple.) The edge pair of a run is protected from inside by the run (stiffness ≈ N²/3 from points at distances π, 2π, …
in u) and from outside by the clock (≈ N²/12), versus ≈ N²/6 for a pair in a clock; the wall's β starts 30% above the
3-block's and stays moderate, while the 3-block's β diverges at its triple collision. This is the mechanism, not a
proof: β(τ) is an output of the N-body dynamics. The initial gap rate is −(2/π)(1 − ln 2 + 1/(L−1) + …) for the edge
pair of an L-run in u-units (−0.64 for L = 3, −0.44 for L → ∞, two-body −1.27), so the run edge starts slower and
stays slower.

## 5. Monotonicity principles — what survives (`push_C_monotone.py`, N = 64, added roots at even sites, compensating hole opposite) [C]

| added set | N²D | | added set | N²D |
|---|---|---|---|---|
| {0} (3-block) | 1.999633 | | {0,2,6} | 2.012469 |
| {0,2} (5-block) | 1.999344 | | {0,2,8} | 2.005804 |
| {0,2,4} (7-block) | 2.037098 | | {0,4,8} | 2.007705 |
| {0,2,4,6} (9-block) | 2.055919 | | {0,2,4,8} | 2.021218 |
| {0,4}, {0,6}, {0,8}, {0,12}, {0,20} | 1.99933, 1.99931, 1.99929, 1.99920, 1.99887 | | {0,2,6,8} | 2.028128 |

* "Adding roots near a collapsing pair can only speed up the collapse": **false** ({0,2} → {0,2,4}: 2 → 2.037;
  every superset in the table is ≥ the 3-block value up to the O(1/N²) effect of the larger compensating hole).
* "Adding roots can only slow it": **false** in general — adding a root adjacent to the compensating hole of the
  3-block creates the pair [3,1] whose depth is the dislocation constant 1.4196 < 2; and Theorem A is a pointwise
  statement about one configuration, not a comparison between two.
* Removing a root next to the critical pair always sped up the collapse (3-block 2.000 → [4,1,1] 1.797 → [3,1] 1.420).
* Tentative principle (all tests): the depth is set by the least-protected 1-gap pair; protection grows with roots on
  both sides (runs, buffers) and drops with holes within distance ~3 of the pair. A precise version is the missing
  lemma of §7.

## 6. Theorem (unique-1-gap ceiling) [P]

**Theorem.** Let θ be any configuration of N points on the circle whose smallest gap δ is attained by exactly one
adjacent pair and all other gaps are ≥ 2δ (for lattice configurations: exactly one gap equal to π/N). Then
D ≤ s₁(δ), where s₁(δ) is the first zero of the solution of the scalar comparison problem below. For the lattice,
N²s₁(π/N) =: τ₁(N) with

| N | 8 | 9 | 10 | 11 | 12 | 16 | 24 | 32 | 64 | 128 | 256 | 1024 | ∞ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| τ₁(N) | 1.9861 | 1.9372 | 1.9010 | 1.8732 | 1.8510 | 1.7947 | 1.7443 | 1.7209 | 1.6880 | 1.6724 | 1.6648 | 1.6592 | 1.65737 |

so **N²D < 2 for every unique-1-gap lattice configuration with N ≥ 8**, and for N ≤ 7 by the enumeration (class
maxima 1.4519, 1.4576, 1.4642, 1.4663). Asymptotically D ≤ 0.16793 δ² = 1.3434·(δ²/8): the two-body constant is
exceeded by at most 34% when the closest pair is isolated. (For comparison the class maximum is 1.4717 = 1.193·π²/8 at
N = 12, the dislocation family.)

*Proof.* Label the critical pair b, a (a counterclockwise of b), g = θ_a − θ_b, and the other points p₂, …, p_{N−1} in
cyclic order from a; g_i are the cyclic gaps, g_1 = g. All statements hold for 0 ≤ s < D (all zeros simple, cyclic order
preserved).

(i) *Other gaps.* By Theorem A, g_i(s) ≥ G(s; g_i(0)) = 2 arccos(e^s cos(g_i(0)/2)), which is increasing in g_i(0);
hence g_i(s) ≥ G(s) := 2 arccos(e^s cos δ) for all i ≠ 1 and all s < min(D, −log cos δ).

(ii) *Bracket bound.* g′ = −2cot(g/2) + Σ_{k≠a,b}[cot(x_b^k/2) − cot(x_a^k/2)] with x_a^k = x_b^k + g (Theorem A's
proof). Each term equals ½∫_{x_b^k}^{x_b^k+g} csc²(y/2) dy ≤ (g/2)·max(csc²(x_b^k/2), csc²(x_a^k/2)), because csc²(y/2)
is decreasing on (0, π] and increasing on [π, 2π), so its maximum on a subinterval of (0, 2π) is at an endpoint;
and csc²(x/2) = csc²(dist/2) with dist ∈ (0, π] the circular distance. So B ≤ g S*, S* := ½Σ_k csc²(d_k/2),
d_k = dist(θ_k, {θ_a, θ_b}).

(iii) *Ordering.* The point p_j is at circular distance D_a = g_2 + … + g_j from a (counterclockwise) and D_b =
g_{j+1} + … + g_N from b (clockwise), with D_a + D_b = 2π − g, so d_k = min(D_a, D_b) ≤ π − g/2 and d_k ≥ G·min(j−1, N−j)
by (i). As csc² is decreasing on (0, π/2] and G·min(j−1,N−j)/2 ≤ d_k/2 ≤ π/2, and each value m = min(j−1, N−j) ≥ 1
occurs for at most two j, S* ≤ Σ_{m ≥ 1, mG ≤ π} csc²(mG/2).

(iv) *Elementary bounds.* csc² y ≤ y⁻² + 1 on (0, π/2] (csc²y − y⁻² increases from 1/3 to 1 − 4/π²), so
S*(s) ≤ S̄(s) := 2π²/(3G(s)²) + π/G(s); and cot x ≥ 1/x − x/3 − x³/40 on (0, 1] (the Laurent series of cot has all
coefficients negative after 1/x; checked on a 2000-point grid at 30 digits), so −2cot(g/2) ≤ −4/g + g/3 + g³/160 for
g ≤ 2.

(v) *Comparison.* With y = g², y′ ≤ −8 + 2y(1/3 + S̄(s)) + y²/80 =: F(s, y), F increasing in y; let Y solve Y′ = F(s, Y),
Y(0) = δ². Standard comparison gives y ≤ Y while both exist, so g(s)² ≤ Y(s) ≤ δ² (Y is decreasing on [0, s₁] — checked
in the computation), which also justifies g ≤ 2 in (iv). If no collision occurred before s₁ := first zero of Y, then
g(s₁)² ≤ 0, impossible; hence D ≤ s₁. ∎

The numbers in the table are s₁ from DOP853 (rtol 10⁻¹¹). For a proof free of ODE numerics, `push_C_unique1gap_bound.py`
also evaluates the piecewise-frozen majorant Y′ ≤ −8 + κ_i Y on 4000 sub-intervals (κ_i = 2/3 + 2S̄(s_{i+1}) + δ²/80,
each piece solved in closed form; S̄ is increasing so freezing it at the right end is a valid upper bound):
τ₁^{rig} = 1.986325 (N = 8), 1.851198 (12), 1.721018 (32), 1.688095 (64), 1.664920 (256), 1.659315 (1024) — the same
to 3·10⁻⁴, and every step is a finite number of elementary-function evaluations. In the limit N → ∞ the comparison
problem is Ȳ′ = −8/π² + Ȳ/(3(1 − 2τ/π²)), Ȳ(0) = 1, first zero 1.65737 (frozen-stiffness value 1/6 would give 1.5892;
two-body only 1.2337).

*Why the argument stops at this class.* For a second 1-gap elsewhere, Theorem A gives only g ≥ G(s; π/N), which
vanishes at τ = π²/8 = 1.23 < τ₁, so the stiffness bound is lost before the comparison closes; for the "isolated 1-gaps"
class the same chain with alternating lower bounds (G, 0, G, 0, …) doubles S̄ and the majorant no longer reaches zero
(Ȳ′ ≈ 0 at τ ≈ 1.5). A bootstrap on the first time some 1-gap reaches ε would be needed; this is **[O]**.

## 7. Conditional theorem and the exact missing lemma

**Proposition (comparison form) [P].** Let β_max : [0, T] → [0, ∞) be measurable and suppose that for a configuration
with δ_min = π/N, the pair (a, b) that collides first satisfies B(s) ≤ N² β_max(N²s) g(s) for all s < D with N²s ≤ T.
Let Ȳ solve Ȳ′(τ) = −8/π² + 2β_max(τ)Ȳ + (π²/(80N²))Ȳ², Ȳ(0) = 1, with first zero τ₂ ≤ T. Then N²D ≤ τ₂.
(Proof: as in §6(v) with the bracket bound replaced by the hypothesis; the −2cot bound of §6(iv) supplies the last
term.)

**Missing lemma (protection lemma) [O].** For every non-clock lattice configuration and its first-colliding pair,
β_config(τ) ≤ β_wall(τ), where β_wall is the ratio B/(N²g) along the edge pair of the domain wall (the N → ∞ limit of
the run\|clock\|hole family; tabulated in `push_C_beta_envelope.log`: 0.2636, 0.2683, 0.2737, 0.2799, 0.2870, 0.2952,
0.3047, 0.3157, 0.3285, 0.3433 at τ = 0, 0.21, …, 1.93 for N = 256, changing by < 10⁻³ between N = 128 and 256).
Since Ȳ with β = β_wall reaches zero exactly at the wall's N²D (checked: Ȳ(0.999·N²D) = 0.0017 at N = 256), the
protection lemma implies **N²D ≤ C\* for all N** by the Proposition. It is equivalent to the statement that the wall
edge pair is the best-protected 1-gap pair at every stage of the flow, which is what all searches (§3c) show
empirically, and it is the precise obstruction: a proof needs control of the bracket B of a pair from the *evolving*
positions of the other zeros, which Theorem A gives only as a lower bound (B ≥ 0), and which the mean-value bound
B ≤ gS* over-estimates by ≈ 40% (§4.5) — too much, since the frozen-stiffness majorant with the wall's S* ≈ 5N²/12
does not close at all (2·(5/12)·π² > 8).

## 8. The Nyquist row does not control the depth (`push_C_tables.log`, Tables 3–5) [C]

\|p_N\|² = (n_even − n_odd)² takes the values (N mod 2)², …, (N−2)² off the clock. Max N²D as a function of \|p_N\|²:
N = 12: 0 → 2.0000, 4 → 1.9902, 16 → 1.9956, 36 → 1.9944, 64 → 1.9902, 100 → 1.9868 (non-monotone; N = 6…11 likewise).
The 4-compensated 3-block has n_odd = N−1, n_even = 1, i.e. the **maximal** imbalance (N−2)² = 100 at N = 12 (the
3,3-compensated one has (N−4)² = 64), while the maximizer [1⁷,2,2,9,2,2] is perfectly balanced (\|p_N\|² = 0), and the
family F(N; L, k, k) has \|p_N\|² = 0 for even L and (2k+1)² for odd L. Over all orbits the Pearson/Spearman
correlations of N²D with \|p_N\|²/N² are +0.13/+0.11 at N = 12 (+0.08/+0.18 at N = 4), decreasing in N; with Q_0/N³
(Σ csc²) they are +0.20/+0.03. The only clean monotone relation is in the ACUE-weighted *mean*: E[N²D \| \|p_N\|²] =
1.412, 1.414, 1.420, 1.431, 1.461, 1.504 for \|p_N\|² = 0, 4, 16, 36, 64, 100 at N = 12 — the configurations with maximal
imbalance are close to the clock (one defect) and have depth ≈ 1.42–2.0. So: no monotone upper envelope, and
maximal parity imbalance is neither necessary nor sufficient for maximal depth.

## 9. The corrected conjecture, with all evidence

**Conjecture C′ (domain-wall ceiling).** Let C* be the first double-zero time of e^{τ∂²}[cos(u/2)/Γ(u/2π)]
(C* = 2.1146648843…; §4.4). For every N ≥ 3 and every non-clock N-subset of the 2N-th roots of unity,

  **π²/8 ≤ N²D < C\*,**

the lower bound being Theorem C(i) and the upper bound sharp: max_config N²D is attained by [1^{L−1}, 2^k, L+1, 2^k]
with k ≈ N/4, L ≈ N/2 for N ≥ 11 (by the symmetric 3-block for N ≤ 10), is strictly increasing in N, and converges to
C* from below. In particular N²D < 2 holds if and only if N ≤ 11; the polynomial Σ_j a_j e^{2j(N−j)/N²} z^j of the
task statement is not real-rooted on the circle for the maximizer at every N ≥ 12 (first failure N = 12, margin
1.8·10⁻⁵), while Σ_j a_j e^{C* j(N−j)/N²} z^j is conjecturally never real-rooted on the circle for any non-clock
lattice configuration.

Evidence: complete enumeration N ≤ 12 (160 000 orbits; top-12 re-verified at 30 digits); the family maxima up to
N = 512; hill-climbs at N = 14–24 and profile searches at N = 32, 48 finding nothing else; the fixed-L limits τ*_L
converging to the same C* from the lattice and from the Hankel model; the three exact local statements (3-block,
5-block, Gamma wall). What is proved: N²D ≥ π²/8 (Theorem C(i)); N²D < 2 on the unique-1-gap class (§6); τ* = 2 for the
3-block local model (§4.2) and the double zero of the 5-block at τ = 2 (§4.3); the Gamma representation of the wall
(§4.4). What would close it: the protection lemma of §7.

Two remarks on what the constant is not. (a) It is not a universal bound for arbitrary circle configurations with
δ_min = π/N: taking the run\|clock\|hole family and slightly shrinking one interior gap of the buffer does not change
the leading behaviour, but the lattice constraint is what pins δ_min and makes the sup finite — for general
configurations with δ_min = δ, sup D/δ² is a different (open) question. (b) C* is a macroscopic optimum only through
the choice L ≈ N/2 at finite N; the constant itself is local (a single domain wall between densities 2 and 1), and
the O(1/L) approach τ*_L = C* − 0.45/L is the finite-run correction, while the finite-N corrections at fixed L are
O(1/N²) and negative.

## 10. Claim ledger

| statement | status |
|---|---|
| N = 12 maximum 2.0000177200 > 2, [1⁷,2,2,9,2,2]; N = 11 maximum 1.9918104778 [1⁶,2,2,8,2,2] beats the 3-block 1.9888697 | **[C]** three solvers agree |
| max_config N²D(N) increasing, values of §3(b) up to N = 512 | **[C]** Method C, validated to 10⁻¹² |
| maximizer = F(N; L, k, k) for 11 ≤ N ≤ 24 (enumeration / hill-climb) and among macroscopic profiles at N = 32, 48 | **[C]** |
| τ*_L table, monotone in L ≥ 4; C* = 2.114665 from the lattice and 2.1146648843 from the Hankel model | **[C]** |
| exact local models: 3-block (τ* = 2, triple), 5-block (double zero at u=0, τ=2), wall q_0 = cos(u/2)/Γ(u/2π) with Hankel flow | **[P]** (5-block first-collision: [C] certificate) |
| earlier long-run values (1.84, 1.78, "halfblock" 2839) are tracker artifacts | **[C]** diagnosed and reproduced |
| unique-1-gap theorem, τ₁(N) < 2 for N ≥ 8, τ₁(∞) = 1.65737; general isolated-closest-pair bound 1.3434·δ²/8 | **[P]** |
| conditional theorem (comparison form) | **[P]** |
| protection lemma β_config ≤ β_wall ⇒ N²D ≤ C* | **[O]** (exact missing lemma) |
| monotonicity principles: both naive versions false; empirical version stated | **[C]** |
| Nyquist row: no control of the depth | **[C]** |
| Conjecture C′ | **[O]** |

## Appendix: files

`push_C_tabulate.py/.log` (enumeration maxima, top-10), `push_C_tables.py/.log` (run-length and structure classes,
Nyquist tables), `push_C_verify.py` (Method A; `push_C_verify_N12run8.log` scan), `push_C_recheck_top.py/.log`,
`push_C_fast.py` (Methods C, R; `push_C_fast_validate.log`), `push_C_verify63.py/.log`, `push_C_verify128.py/.log`,
`push_C_family_scan.py` (`push_C_family_sym.log`, `push_C_family_asym.log`), `push_C_largeN.py`
(`push_C_runs_largeN.log`, `push_C_iface_largeN.log`, `push_C_iface_384_512.log`), `push_C_wall_const.py/.log`,
`push_C_wall_gamma.py/.log`, `push_C_wall_gamma_refine.py/.log`, `push_C_hillclimb.py/.log`, `push_C_segments.py/.log`, `push_C_localmodel_sym.py/.log`,
`push_C_fiveblock_cert.py/.log`, `push_C_trajectories.py/.log`, `push_C_beta_envelope.py/.log`, `push_C_monotone.py/.log`,
`push_C_otherdefects.log`, `push_C_unique1gap_bound.py/.log`.
