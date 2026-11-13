# Refutation report on `push_D_last_mile.md`

**Fable overnight, refuter pass, 2026-09-06.** Target: `push_D_last_mile.md` (push D, "the last mile"). Script: `refute_D_check.py` (log `refute_D_check.log`), plus a re-run of push D's LP with dual extraction and a finer check grid (`refute_D_lpdual.py`, results quoted in §4). Tags: **[P]** proved here or re-derived; **[C]** computed here; **[O]** open/unverifiable from here. Literature statements are **(recalled)** unless a search snippet is quoted; no primary text could be read (arxiv.org, ar5iv, alphaxiv, OUP, Cambridge, ScienceDirect, Semantic Scholar, ResearchGate, ADS, EUDML, NSF-PAR, Bristol, Williams all egress-blocked; WebSearch snippets only). Standing hypothesis for every ζ statement: RH.

---

## 0. Verdict in twelve lines

1. **The GGM kernel formula and its normalisation are correct.** Recomputed from Astra's physical-space definitions (pair masses (5)–(6), Poisson kernel (16), combination (13)) without using push D's formulas: W_GUE = 0.08227144312147732…, W_AH = 0.06239241797649854…, both matching Astra's closed forms (15) to 30 digits; 1/16 − W_AH = 1.0758·10⁻⁴; K = sinh2·e^{−2|α|} − sinh1·e^{−|α|} with α₀ = log(2cosh1) = 1.126928011 **[C, P]**.
2. Astra's V_A(b) = 2tanh(b/2)/b² + 2/(e^{2b}−1) is re-derived here by partial fractions directly from the half-lattice pair masses (no Poisson summation), and the p₀-nuisance cancels exactly in W (odd-integer atoms carry weight 2Σ_{m≥0}K(2m+1) = 0) **[P]**. All fifteen table constants of push D §2.2 and the derived numbers (B, u* = 1.04201/1.03361, AH average 1.05145, 0.0753/0.0785 caps, 2|K(2)| = 0.18524, 56 % weight on (α₀, 2.5]) reproduce to ≥ 10 digits **[C]**.
3. **Constraint (iii) is misattributed and is not RH-only.** Two independent search snippets (GLSS 2025 Part I intro; Chirre–Gonçalves–de Laat / Carneiro et al.) attribute the bound F(α) ≥ 3/2 − |α| − ε on 1 ≤ |α| ≤ 3/2 − 2ε to Goldston–Gonek–Özlük–Snyder, Proc. LMS 80 (2000), and GLSS state the hypothesis as **GRH**; the snippet on Goldston's Crelle 385 (1988) paper describes a different result (RH, simple zeros). Push D cites "Goldston 1988, RH". F_AH satisfies the bound trivially (2−α ≥ 3/2−α), so the barrier survives, but "F_AH satisfies every RH-only theorem about F" was only checked for (i), (ii) and a GRH bound, and the **RH-only** LP number is 0.0207, not 0.0236.
4. **Theorem 2.1(d) is a relativisation tautology, correctly directed but loosely quantified**: "𝒜 ⊬" should be semantic non-entailment (𝒜 ⊭); "each of which is a consequence of (i)–(iii) — equivalently, each of which holds for F_AH" is false as an equivalence (only the second clause is used); "statements … about the zeros" has no interpretation for inputs that mention primes, so the theorem covers exactly the inputs push D lists and nothing arithmetic. All of its content is in (a) = Astra's Theorem 7.1.
5. The class 𝓕 should carry (i) on the **open** band |α| < 1: Montgomery's theorem does not exclude limit mass at α = 1⁺; the LP (cells starting at 1) already allows it, so no number changes.
6. **The LP is misdescribed**: the code uses cells 0.02/0.05/0.1 on (1,3]/(3,6]/(6,12] and an initial u-grid to 40, not 0.01/0.02/0.05 and 20; "satisfies pair positivity to 10⁻⁶ on (0,400]" holds on the 0.002 grid only — at grid midpoints the minimisers violate R ≥ 0 by 2.0·10⁻³ (gold0, u = 2.973) and 1.6·10⁻³ (gold1, u = 2.903) **[C]**. Refining the check grid to 0.0007 moves W by +3·10⁻⁶, so the values 0.0207/0.0236 stand numerically **[C]**; R > 0 for all u > 400 is proved by a 1/u bound (|Σ(x−1)cc| ≤ 0.40/0.33 at u = 400) **[P]**.
7. **0.0236 is an LP estimate, not a bound**: the discretised LP is exact (dual = primal to 10⁻¹³, 137/175 active multipliers), but the dual function g(α) = 2K(α) − Σ y_j·2cos(2παu_j) is not pointwise nonnegative on (1,12] (§4.3), so no proof "W ≥ 0.0236 for every F ∈ 𝓕⁺" exists in the files; the true infimum is bracketed only loosely (piecewise-constant restriction and F = 1 beyond 12 push it up, grid relaxation pushes it down; point-process constraints beyond pair positivity, e.g. Var N(I) ≥ {ℓ}(1−{ℓ}), are omitted). Honest statement: inf ≈ 0.021 (RH inputs) / ≈ 0.024 (with the GRH floor), in [0.02, 0.0624].
8. **"Siegel-hard by Conrey–Iwaniec" is a heuristic stated as a theorem in line 7 and §3.1.** The C–I hypothesis (snippets) is that *sufficiently many* consecutive zeros of the Hecke L-functions of class-group characters in a D-dependent height range have gaps somewhat below the average; a liminf statement (one small gap infinitely often) is not that hypothesis — μ ≤ 0.5154 is already known and is not Siegel-hard. Push D §1.3 says this itself; the verdict line contradicts it.
9. Line 7's chain "Level B ⟹ μ < ½ ⟹ gaps 6 % below ½ after the dressing factor [P modulo (NR)]" conflates the proved direction (Level B ⟹ μ ≤ √(2c)/π < ½, Theorem A′) with the computed converse (a gap must be < λ* ≈ 0.472 to *produce* Level B in clock/CUE backgrounds, [C]); "Level B ⊂ {μ ≤ λ*}" is not proved for arbitrary backgrounds.
10. Line 8 / §3.2 overreach: "all proven prime estimates are consistent with AH's prime shadow — this is the content of Rounds 8–28 having failed to close" is a non sequitur (failure to close is not consistency); "no sixth kind of route" is an inventory of the programme, not a theorem. Tao's "single value" remark (snippet confirmed) needs the caveat α ∉ 2ℤ+1: F_AH(α) = 1 at odd integers when p₀ = 1, so a single verification must be at α with dist(α,2ℤ) ≠ 1.
11. Minor: the k ≥ 0 algebra as displayed (4π²u²(sinh2 − sinh1) ≥ 2sinh1(2−2cosh1)) is not the cross-multiplied inequality (correct: (sinh2 − 2sinh1) + π²u²(4sinh2 − 2sinh1) ≥ 0), conclusion unaffected; "E_T is exactly 2∫_1^∞KF_T" holds up to o(1); GLSS's 100 %-simple theorem is unconditional (snippet), not "under RH"; "Gallagher–Mueller method" and the BGST content are unverified; the [P] tag on line 6's Goldston–Montgomery variance translation should be "heuristic dictionary" (GM is an asymptotic equivalence, not a weighted one-sided transfer — Round 8's E_T identity is the exact statement).
12. **Net:** the mathematical core survives — W_T = ∫K F_T + o(1) under RH, W_AH < 1/16 < W_GUE with the stated margins, the Bragg-atom mechanism, the "missing upper bound on (α₀,∞)" reformulation, and the relativisation barrier for band-limited/positivity inputs. What must be corrected: (iii)'s attribution and hypothesis, the RH-only LP number, the LP description, the certification status of 0.0236, the Siegel-hardness and dressing-factor phrasing, and the "every RH-only theorem" claim.

---

## 1. The kernel and its normalisation, recomputed independently [C, P]

### 1.1 What was recomputed and how

`refute_D_check.py` starts from Astra's definitions only: pair masses (5) with the nuisance comb (6); the Poisson kernel K_b(x) = 2b/(b² + 4π²x²) of (16); Q(b) = ∫K_b dμ − 1; and W = sinh2·V(2) − sinh1·V(1) of (13). Nothing from push D's formulas is used, so agreement checks push D's kernel K, its Fourier normalisation and every table constant.

**Physical-space sums (no Poisson summation).** For the half-lattice model at p₀ = 1, μ = δ₀ + ½Σ_{k≠0}(1 − sinc²(k/2))δ_{k/2}. Splitting parities (even k = 2j: 1 − sinc²(j) = 1; odd k: 1 − 4/(π²(2j+1)²)) and using

  Σ_{j≥1} K_b(j) = ½coth(b/2) − 1/b,  Σ_{j≥0} K_b(j+½) = ½tanh(b/2),  Σ_{j≥0} (4/(π²(2j+1)²))K_b(j+½) = 1/b − 2tanh(b/2)/b²,  K_b(0) = 2/b,

gives V_A(b) = ½(coth(b/2) + tanh(b/2)) − 1 + 2tanh(b/2)/b² = coth b − 1 + 2tanh(b/2)/b² = 2/(e^{2b}−1) + 2tanh(b/2)/b², which is Astra's (10) **[P, independent derivation]**. Numerically the parity-split sums agree with (10) to 30 digits at b = 0.7, 1, 2. (A single `nsum` over k mis-extrapolates the parity oscillation by 1.2·10⁻⁵ — a trap worth recording, since the whole AH margin is 1.08·10⁻⁴.) The nuisance comb contributes exactly 2(p₀−1)/sinh b (Astra (12)), verified to 30 digits at p₀ = 1.3, and W at p₀ = 1.29 equals W at p₀ = 1 to 30 digits.

**Fourier side.** With F_AH = dist(α,2ℤ)dα + Σ_{m≠0}δ_{2m} and K as in push D, ∫K dF_AH reproduces W_AH (to 7·10⁻⁹ with a naive breakpoint list; push D's per-period integration in `push_D_ah_exact.py` is the right way and gets 30 digits). The odd-integer atoms have weight 2Σ_{m≥0}K(2m+1) = −7·10⁻³² ≈ 0: this is the Fourier-side form of the (12)–(13) cancellation and is why W is p₀-blind **[P]**.

**GGM normalisation.** ∫_0^∞ e^{−2cα}min(α,1)dα = (1−e^{−2c})/(4c²) = V_sine(2c)/2 at c = 1, ½ (30 digits), and the c → ∞ limit 1/(4c²) matches the trivial mean value T·Σ Λ(n)²n^{−2σ} ~ T/(2σ−1)² = T log²T/(4c²) at σ − ½ = c/log T, a consistency check of the T log²T scaling **[P]**. The chain (16)→(19)→(18)→(22)→(23) in Astra's file is re-read: the Γ-factor ½log(t/2π) divided by πL is exactly the "−1" of Q_T, i.e. the removed zero-frequency atom; (23) with b = 2c gives I_T(c) = (T log²T/2)·Q_T(2c) + o(T log²T) and hence W_T = sinh2·Q_T(2) − sinh1·Q_T(1) + o(1) = ∫K F_T + o(1) **[P under RH, Astra's estimates]**. Identification of the unweighted μ̂_T with Montgomery's w-weighted F(α,T) − T^{−2|α|}log T costs O(b/log T) for fixed b (the weight 1 − w(u) = u²/(4+u²) against K_b(Lu) sums to O(b/L)), so push D's "F_T Montgomery's form factor (zero-frequency atom removed)" is correct in the limit; it should say so rather than "exactly".

### 1.2 Table of constants (push D §2.2 vs this recomputation)

| quantity | push D | refuter (30-digit mpmath) | status |
|---|---|---|---|
| W_GUE | 0.0822714431214773232 | 0.0822714431214773232487733005552 | ✓ |
| W_AH | 0.0623924179764985431 | 0.0623924179764985431237712221837 | ✓ |
| 1/16 − W_AH | 1.0759·10⁻⁴ | 1.07582023501·10⁻⁴ | ✓ |
| W_GUE − W_AH | 0.019879 | 0.0198790251449787801 = H(2) − H(1) | ✓ |
| α₀ | 1.12692801 | 1.12692801104297249644 | ✓ |
| B | 0.4560939793292317 | 0.456093979329231721502 | ✓ |
| AH continuous part | 0.2949365759 | 0.294936568802 | ✓ |
| AH atoms | −0.2325441579 | −0.232544157935 = e⁻² − e⁻¹ | ✓ |
| 2∫₁^{α₀}K(3/2−α) | 0.0032014647 | 0.00320146468510 | ✓ |
| 2∫₁^{α₀}K | 0.0069745418 | 0.00697454177013 | ✓ |
| 2∫₁^{α₀}K(2−α) | 0.0066887356 | 0.00668873557017 | ✓ |
| 2∫_{α₀}^∞K | −0.3807970780 | −0.380797077978 = −tanh(1)/2 | ✓ |
| AH tail | −0.4003902969 | −0.400390296923 = −0.167846138988 − 0.232544157935 | ✓ |
| W_GUE − B, W_AH − B, 1/16 − B | −0.3738225362, −0.3937015685, −0.3935939793 | −0.373822536208, −0.393701561353, −0.393593979329 | ✓ |
| u* (Goldston / none) | 1.04201 / 1.03361 | 1.0420128382 / 1.0336055660 | ✓ |
| AH |K|-average on (α₀,∞) | 1.05145 | 1.05145317566 | ✓ |
| caps: F ≤ 1 beyond α₀ (floor 0 / Goldston) | 0.0753 / 0.0785 | 0.0752969014 / 0.0784983660 | ✓ |
| 2|K(2)| ; |K|-weight fraction on (α₀,2.5] | 0.1852 ; 56 % | 0.185235842 ; 55.75 % | ✓ |
| decomposition of W_GUE − W_AH | +0.00029 / +0.21295 / −0.23254 | +0.000285806 / +0.212950939 / −0.232544158 | ✓ |
| k(0), K(0), k(0) − K(0) | —, —, −sinh1 | 1.276458, 2.451659, −1.175201 = −sinh1 | ✓ |
| min_u k(u) | ≥ 0 | 7.7·10⁻⁴ at the grid end (k → 0⁺) | ✓ |

### 1.3 Small defects in §2.1–2.2

- The displayed k ≥ 0 criterion, "k ≥ 0 ⟺ 4π²u²(sinh2 − sinh1) ≥ 2sinh1(2 − 2cosh1)", is not what cross-multiplication gives; the correct form is (sinh2 − 2sinh1) + π²u²(4sinh2 − 2sinh1) ≥ 0, both terms positive. Same conclusion (k ≥ 0, k → 0⁺), wrong algebra.
- "Round 8's residual energy E_T is exactly 2∫₁^∞KF_T": true up to o(1) (both sides are defined through different exact objects), not exactly.
- (i) for the limit class: Montgomery's theorem gives F(α,T) → |α| uniformly on the closed band as a *function*, but a limit *measure* may carry an atom at α = ±1 from mass at 1 + o(1) (e.g. a spike at 1 + 1/log T). 𝓕 should impose F = |α|dα on |α| < 1 only. The LP already does this (cells begin at 1), so nothing numerical moves, but Theorem 2.1(b)'s minimiser statement and (c) should be read with the open band.

---

## 2. Constraint (iii): the "Goldston bound" is misattributed and is a GRH result

Push D §2.3(iii): "*Goldston, J. reine angew. Math. 385 (1988) 24–40; a search snippet corroborates the form F(α,T) ≥ 3/2 − α + o(1) on (1,3/2), attributing the assumption to GRH in one secondary source*", tagged as an RH-only theorem in §2.3, Theorem 2.1, and lines 2, 3, 10.

What the snippets say (this session; none of the primary texts readable):

- GLSS, *Pair correlation … I* (arXiv:2501.14545) introduction, via search snippet: "estimates of F(α,T) when α ≥ 1 remain elusive, with the only progress in this direction being a lower bound F(α,T) ≥ 3/2 − α + o(1) on the interval (1, 3/2) under the assumption of the **Generalized Riemann Hypothesis**."
- Search summary of the semidefinite-programming / Fourier-optimisation literature (arXiv:1810.08843, 2310.01913): "Goldston, Gonek, Özlük and Snyder … showed that F(α) ≥ 3/2 − |α| − ε, uniformly for 1 ≤ |α| ≤ 3/2 − 2ε" (Proc. LMS (3) 80 (2000) 31–49). A second snippet on the same authors: "Assuming GRH, Goldston, Gonek, Özlük and Snyder … showed that 67.38 % of zeros are simple using the pair correlation approach" — the GGÖS results are GRH results (my recollection agrees: the input is Özlük's q-averaged pair correlation of Dirichlet L-functions, which needs GRH).
- Goldston, Crelle 385 (1988), via snippet: "assumed RH and provided a short proof that at least 2/3 of zeta-zeros are simple" — a different theorem; no snippet attributes the 3/2 − α bound to it. *(recalled, consistent)*: Goldston 1988 concerns consequences of the pair correlation conjecture and RH-only pair sums, not a lower bound for F beyond 1.

Consequences for push D:

1. §2.3's list "everything proved about F outside the band, under RH" contains a GRH item and cites the wrong paper. Under RH alone the list is (i), (ii-F), (ii-μ) and nothing else known to this session **[O: no RH-only lower bound for F on (1,∞) other than 0 could be located]**.
2. Theorem 2.1(c)'s number with (iii) (0.0236) is a GRH number; the RH-only LP value is **0.0207** (push D's own gold0 run). Lines 3, 10, 12 ("0.039 above the best provable bound") should say 0.0207 / 0.042 under RH, 0.0236 / 0.039 under GRH.
3. §2.6's "with Goldston" branch (needed tail ≤ 0.3967954, u* = 1.04201) is the GRH branch; the RH branch is 0.3935940 / 1.03361 — push D gives both numbers but labels the first as the default.
4. Nothing breaks in the barrier: F_AH satisfies the GGÖS floor with room to spare (2 − α − (3/2 − α) = ½ on [1,3/2]), and adding constraints to 𝒜 only strengthens Theorem 2.1(d). But the sentence "F_AH satisfies every RH-only theorem about F" (line 2, §2.3, Theorem 2.1(a)) is not the result of a check; it is the meta-observation "otherwise AH-pairs would already be refuted under RH", which push D also states. It should be stated only in that form.

---

## 3. The barrier theorem: quantifiers, admissible class, o(1) terms

### 3.1 What Theorem 2.1(d) actually asserts [P as a tautology]

The proof is: F_AH ∈ 𝓕⁺ and W[F_AH] < 1/16, so no property shared by F_AH implies W ≥ 1/16. That is correct and is a relativisation-type barrier; its entire content is (a), i.e. Astra's Theorem 7.1 (RH + AH-pairs ⟹ W_T → W_AH) plus the LR/ACUE realisability of F_AH. Three quantifier issues:

- **"𝒜 ⊬ liminf W_T ≥ 1/16."** The argument establishes semantic non-entailment (there is a model of 𝒜 ∧ ¬target), so "⊭". Fine in substance; the symbol suggests a proof-theoretic result that is not there.
- **"each of which is a consequence of (i), (ii-F), (ii-μ), (iii) — equivalently, each of which holds for F_AH."** Not equivalent: "F has an atom at 2" holds for F_AH and is no consequence of (i)–(iii). Only the second clause is used, and with the second clause the theorem is: *any set of constraints satisfied by F_AH* cannot imply the target. Correct, and stronger than the first clause, but the word "equivalently" is wrong.
- **"statements about F_T (or about the zeros)."** A statement about the zeros is admissible only if it has a truth value for the LR/ACUE process. Statements involving primes (explicit formula, Bombieri–Vinogradov, Vaughan, Round 8's E_T representation) have none; push D concedes this in the paragraph after (d) ("It does not apply to arithmetic inputs that F_AH violates") but then, in line 8 and §3.2, treats "consistent with AH's prime shadow" as if it were decidable and decided (§6 below).

### 3.2 Sequences versus limits, liminf versus lim, the o(1)s

The constraints (i)–(iii) are statements about the sequence F_T with o(1) errors; W is evaluated on limit measures. The passage requires tightness: for any subsequence, F_T → F weak-* along a further subsequence and ∫K F_T → ∫K dF. This holds because ∫e^{−|α|/2}F_T dα = Q_T(½) + 1 ≪ 1 by the pair bound μ_T([−h,h]) ≪ 1 + h (Astra §4), so ∫_{|α|>M}|K|F_T ≪ e^{−M/2} uniformly in T. Push D does not say this; it should, since without it "liminf W_T ≥ inf_{limit points} W[F]" is unjustified. With it, the target liminf W_T ≥ 1/16 is equivalent to W[F] ≥ 1/16 for every subsequential limit F, and Theorem 2.1(d) is correctly stated for liminf (the weakest target). Astra's Theorem 7.1 gives the full limit under AH-pairs, so lim/liminf is not an issue on the AH side either.

§2.6's "the target follows from, and (given only (iii) on (1,α₀)) is equivalent to, limsup 2∫_{α₀}^∞|K|F_T ≤ 0.3967954" is an equivalence of *proof obligations* (if the only information on (1,α₀) is the floor), not a mathematical equivalence for ζ; and the number is the GRH branch (§2).

### 3.3 The admissible class 𝓕⁺

- (i) should be on the open band (§1.3).
- (ii-μ) as written, "R := 1 + ∫(F − 1)e(αu)dα ≥ 0 as a measure", presupposes that F − 1 is a tempered distribution whose transform is a measure on u ≠ 0; for limit measures with unbounded mass this needs the same tightness. Harmless.
- (ii-μ) is necessary but far from sufficient for realisability: a point process also has Var N(I) ≥ {ℓ}(1−{ℓ}) for |I| = ℓ (integrality), nonnegative n-point correlations, etc. Every such constraint is satisfied by the LR process, so Theorem 2.1(d) survives them, but Theorem 2.1(c)'s "inf_{𝓕⁺} W equals 0.0236" is the infimum over a *relaxation*, and "best bound from the known inputs" is then a lower estimate of what those inputs give (the true value lies in [≈0.02, W_AH = 0.0624]).

---

## 4. The LP: what the code does, what the text says, and what is certified [C]

### 4.1 Description versus code

| item | push D §2.5 text | `push_D_lp.py` / logs |
|---|---|---|
| cells | 0.01 on (1,3], 0.02 on (3,6], 0.05 on (6,12] | **0.02, 0.05, 0.1** (`segs=[(1,3,0.02),(3,6,0.05),(6,12,0.1)]`; the top cells 1.37/1.39/1.41, 4.175, 6.95 confirm) |
| initial u-grid | u ≤ 20, step 0.02 | **u ≤ 40**, step 0.02 |
| check grid | step 0.002 to 400 | step 0.002 to 400 ✓ |
| stopping | min R ≥ −10⁻⁶ | ✓ |
| values | 0.020696 / 0.023579 | 0.020695994 / 0.023578944 ✓ (recomputed from the saved x: identical) |

The text's "a finer discretisation (cells 0.01, positivity to u = 30 only) gave 0.0206" suggests an earlier run; the archived runs are the coarser ones.

### 4.2 Feasibility of the archived minimisers

- On the 0.002 check grid: min R = −2.4·10⁻¹² (gold0), −6.5·10⁻¹³ (gold1) ✓.
- At the **midpoints** of that grid: min R = **−2.04·10⁻³** at u = 2.973 (gold0), **−1.55·10⁻³** at u = 2.903 (gold1). So "satisfies pair positivity to 10⁻⁶ on u ∈ (0,400]" is a grid statement; the minimisers are infeasible for the continuum constraint at the 10⁻³ level. The cause is the piecewise-constant F with jumps at cell edges, whose transform has O(1/u) oscillations at all frequencies up to 12.
- For u > 400 no check was run; the bound |Σ_i(x_i−1)cc_i(u)| ≤ Σ_i|x_i−1|·min(2Δ_i, 2/(πu)) = 0.404 (gold0) / 0.326 (gold1) at u = 400, decreasing like 1/u, against 1 − sinc²(u) ≥ 1 − 10⁻⁶, proves R > 0.59 for all u > 400 **[P]**. Push D's "the long u-range is essential" is right; its minimisers are fine beyond 400.
- Re-running push D's LP with the check grid refined to 0.0007 (this session): W = 0.020699 (gold0), i.e. +3·10⁻⁶, converging in the same way. The numbers 0.0207 / 0.0236 are therefore stable to four decimals as claimed, even though the archived minimisers are slightly infeasible.

### 4.3 Certification status

Re-running with HiGHS dual simplex and extracting multipliers: primal = dual to 10⁻¹³ (−0.43538354 for gold0, −0.43250059 for gold1), with 137 (gold0) and 175 (gold1) active cutting planes; per-cell dual feasibility holds to 10⁻¹⁵. So the **discretised** LP value is exact. To turn it into a theorem "W[F] ≥ c for every F ∈ 𝓕⁺ with F = 1 beyond 12" one needs the dual function

  g(α) = 2K(α) − Σ_j y_j·2cos(2παu_j)  (plus the Goldston multipliers on (1, 3/2])

to be nonnegative **pointwise** on (1,12], not merely cell-averaged; then W ≥ B + tail + Σ_j y_j(sinc²(u_j) − 1 + Σ_i cc_{ji}) for every admissible measure. This session's re-run gives, for the archived discretisation, g with minimum **−8.5·10⁻⁴** (gold0, at α = 11.9995) / **−7.6·10⁻⁴** (gold1), negative on 41 % / 44 % of a 0.001-grid of (1,12], with L¹-mass of the negative part 3.4·10⁻⁵ / 3.3·10⁻⁵ **[C]**. So the cell-averaged dual is not a pointwise certificate. The dips are small, but the only mass bound available for a general F ∈ 𝓕⁺ (Round 16's window bound, ≲ 2.3 per half-unit window, hence ≲ 50 on (1,12]) allows a loss of up to ≈ 8.5·10⁻⁴ × 50 ≈ 0.04 > 0.0207, so these multipliers certify nothing nontrivial. A certificate would need the dual re-optimised under pointwise constraints (a semi-infinite LP, the Fourier-optimisation set-up of Carneiro–Chandee–Littmann–Milinovich / Chirre–Gonçalves–de Laat *(recalled)*); the tiny L¹ defect suggests this costs O(10⁻⁴–10⁻³) in the objective, but that is a conjecture **[O]**.

Beyond 12 the certificate cannot hold as written (g oscillates with amplitude Σy_j while K is ≤ 10⁻⁵), so any rigorous version must bound ∫_{12}^∞|K|dF separately by the window-mass bound of Round 16 (mass ≤ 1 + O(ε²) per window), which costs ≲ 10⁻⁴. None of this is in push D; its Theorem 2.1(c) "inf_{𝓕⁺} W … equals 0.0236 [C, discretised LP with cutting planes]" is an estimate of the infimum, tagged [C], but lines 3, 10 and 12 use "best provable bound" and "provable now" language for it. The honest statement is: **the pair-positivity relaxation gives inf ≈ 0.021 under RH inputs and ≈ 0.024 with the GRH floor, numerically stable, not certified, and in any case ≤ W_AH = 0.0624 by Theorem 2.1(a).**

### 4.4 What the minimiser is and is not

Push D's description of the comb (near-atoms at 1.41, 2.82, 4.23, …, spacing ≈ 1.41; total near-atom mass ≈ 7–8 in 38–45 cells; F on (1,α₀) at its floor) is accurate for the archived JSONs. It is a relaxation object, as push D says; its mean density on (1,12] is 1.052 (gold0) / 1.061 (gold1), i.e. the R(0) ≥ 0 constraint (mean of F − 1 on (1,12] ≥ 0, a legitimate consequence of continuity of R for compactly supported F − 1) is active in spirit: the LP lowers W by piling mass where |K| is largest subject to keeping R ≥ 0 at all scales.

---

## 5. Attributions and literature (snippet-level only)

| item in push D | status | note |
|---|---|---|
| Tao 2019: "verification of the pair correlation conjecture for even a single [α > 1] … comparable to averaged Hardy–Littlewood with power saving … Siegel zeroes" | **confirmed** near-verbatim by a search snippet of the post | The bracket "[parameter value α > 1]" is push D's gloss (the snippet says "for even a single value"). Precision: at p₀ = 1, F_AH(α) = dist(α,2ℤ) equals 1 at odd integers, so the single value must have dist(α,2ℤ) ≠ 1; the odd-integer atoms of the general AH-pairs family (mass 2(p₀−1) ≤ 0.595) make odd integers ambiguous rather than decisive. |
| Tao: AH "implied by the existence of a Siegel zero, as discussed in a paper of Conrey and Iwaniec" | **confirmed** by snippet ("The Alternative Hypothesis is implied by the existence of a Siegel zero and is discussed in a paper by Conrey and Iwaniec") | — |
| Conrey–Iwaniec, Acta Arith. 103 (2002) 259–312 | bibliography confirmed; hypothesis via snippets: "if the gap between consecutive zeros of the L-function is somewhat smaller than the average for sufficiently many pairs of zeros on the critical line, then h ≫ √q(log q)^{−A}"; "lower bounds on h(−D) on the hypothesis that sufficiently many zeros of various L-functions attached to characters of the class group are sufficiently closely spaced" | The hypothesis is a **count** of small gaps of the class-group Hecke L-functions in a D-dependent range. A liminf small-gap statement for ζ is not that hypothesis. Push D §1.3 says "Siegel-hard is a heuristic"; line 7 and §3.1 say "by Conrey–Iwaniec is Siegel-hard" as if proved. Overclaim in the verdict. |
| Lagarias–Rodgers, Q. J. Math. 71 (2020) 257–280 | **confirmed**: "show by construction of an explicit counterexample point process that [known higher correlations are] not [sufficient]" and "proved that the Alternative Hypothesis is compatible with all band-limited higher correlations" | The n ≥ 3 range Σ|ξ_i| < 2 remains push D's reconstruction; the snippet says "all band-limited higher correlations", consistent. |
| GLSS 2025 (arXiv:2507.06823, JNT) | snippet: PCC ⟹ 100 % simple and on the line **without RH**; "formulates an appropriate form of AH, which determines a different PCC, and using the same method proves 100 % simple and critical"; "The authors do not assume RH" | Push D §1.1 "Under RH their AH0 determines a pair-correlation conjecture … and (their theorem) still forces 100 % simple critical zeros by the Gallagher–Mueller method": the theorem is unconditional; "Gallagher–Mueller" unverified. Astra's use of the RH-dependent (1.14)–(1.15) is a separate matter and is correctly described by Astra. |
| Goldston 1988 for (iii) | **misattributed** (§2) | should be GGÖS 2000, GRH |
| GGM, Crelle 537 (2001) 105–126 | bibliography confirmed; the constant (1−e^{−2a})/(4a²) not readable, but it is forced by the sine-kernel integral and the σ → ∞ check (§1.1) | fine as "(recalled, consistent)" |
| Rodgers–Vallabhaneni, Glasgow Math. J. (arXiv:2301.00268) | **confirmed** title and content ("closed formulas for arbitrarily high mixed moments … and ratios … via symmetric function theory and a general formula of Borodin–Olshanski–Strahov; comparison to CUE") | volume/page not checked |
| Baluyot 2016 JNT; BGST arXiv:2508.10857 | not verifiable here (blocked) | push D's summary of BGST ("constraints on the density of pairs at each k/2 … stronger AH implies Essential Simplicity") is unverified |
| Farmer–Gonek–Lee, JLMS 90 (2014) | not verified; push D flags its own reconstruction | fine |
| Preobrazhenskiĭ 0.515396; "Inoue 2026, μ < 0.50895 as read by Astra" | recalled / hearsay | fine as labelled |
| Montgomery's theorem, GM 1987 constant ½δX²log(1/δ) | recalled; consistent with the variance heuristic h·log(x/h) | fine as labelled |

---

## 6. Overclaims, itemised

1. **Line 2 / Theorem 2.1(a):** "F_AH satisfies every RH-only theorem about F" — checked only against (i), (ii) and a GRH bound; should read "against every constraint used here; if it violated any proven RH-only statement, AH-pairs would already be refuted under RH".
2. **Line 3, 10, 12, Theorem 2.1(c):** "best bound … W ≥ 0.0236 (LP, converged)", "provable now: … the LP bound" — an uncertified relaxation estimate, GRH-dependent; RH-only 0.0207.
3. **Line 7 / §3.1:** "Level B ⟹ μ < ½ ⟹ gaps 6 % below ½ after the dressing factor, which by Conrey–Iwaniec is Siegel-hard [P modulo (NR)]" — the second arrow is the computed converse (λ* ≈ 0.472 is what a gap must be to *cause* Level B in clock/CUE backgrounds; r1 §3.5), not an implication; "Level B ⊂ {μ ≤ λ*}" (r1 §4.2) is not proved for arbitrary environments; "Siegel-hard by C–I" is a heuristic by push D's own §1.3.
4. **Line 8 / §3.2:** "There is no sixth kind of route … the 'arithmetic' inputs used … are all consistent with AH's prime shadow — this is the content of Rounds 8–28 having failed to close." Non sequitur; consistency of, e.g., Bombieri–Vinogradov or Selberg's RH variance bound with AH's shadow is plausible but not established anywhere in the files. The barrier is a theorem for band-limited/positivity/integrality inputs and a heuristic for arithmetic ones; §3.2's "[P]" should be split accordingly.
5. **Line 6:** the Goldston–Montgomery translation "an upper bound for the variance of ψ in intervals of length h = x^{1−1/α}, at the level 1.042 × the GUE prediction" is tagged [P]; GM is an asymptotic equivalence (∼) on ranges, not a transfer of a one-sided |K|-weighted bound. The exact statement is Round 8's E_T identity, which push D also gives; the "1.042 × variance" phrasing is a heuristic dictionary.
6. **§2.5:** "Kronecker: total incommensurable atomic mass ≤ ½" holds for the truncated class (F − 1 compactly supported, so the continuous part's transform decays); for general limit measures the continuous part need not decay and the statement is heuristic.
7. **§2.6:** "is equivalent to" (proof-obligation equivalence, see §3.2); "exactly the AH value A_ε = 1.0106 … against the GUE value M ≈ 0.185": correct per Round 16/20 (C_ε(2) = 1.0105877964 AH, 0.1851531433 GUE); fine.
8. **§1.2:** "The '< 2' is documented for n = 2 … for n ≥ 3 it is my reconstruction" — honest; but Rudnick–Sarnak's range Σ|ξ_i| < 2 is the standard published statement *(recalled)*, so the reconstruction is of LR's matching range, not of RS's theorem.
9. **§1.1:** "GLSS … Under RH … Gallagher–Mueller method" — see §5.

---

## 7. What survives, precisely

- **[P under RH]** W_T = ∫K F_T dα + o(1) with K = sinh2·e^{−2|α|} − sinh1·e^{−|α|}; K > 0 on |α| < α₀ = log(2cosh1), K < 0 beyond; k = K̂⁻¹ ≥ 0; W_T ≥ −sinh1 trivially (Astra §§4–6 + Parseval; identification with Montgomery's F up to O(1/log T)).
- **[P]** W_AH = e²/4 + 5/(4e²) − e − 2/e + 3/2 = 0.062392418…, W_GUE = 0.082271443…, W_AH < 1/16 < W_GUE; p₀-independence; atoms e⁻² − e⁻¹ are AH's whole advantage; the band contributes B = 0.456093979…; the sign-indefinite tail decomposition and the numbers u* = 1.03361 (RH inputs) / 1.04201 (with the GRH floor).
- **[P]** Theorem 2.1(a),(b),(d) as a relativisation barrier for any inputs the LR/ACUE process satisfies (band, both positivities, the GGÖS floor, band-limited higher correlations, integrality), with (d) read semantically.
- **[C]** Pair-positivity relaxation infimum ≈ 0.0207 (RH inputs) / ≈ 0.0236 (with GRH floor), stable to 4 decimals under grid refinement, minimiser a quasi-periodic comb; not certified.
- **[P]** The "missing input is an upper bound on the |K|-weighted spectral mass on (α₀,∞), not a lower bound and not information at α ≤ 1" — correct and the most useful sentence in the file.
- **[P under RH + (NR)]** Level B ⟹ μ < ½ (r1's Theorem A′); the converse fails ([C], λ* ≈ 0.472); the periodised shortcut is wrong; Level B touches AH-strong only.
- **[O]** liminf W_T ≥ 1/16; any RH-only lower bound for F on (1,∞) other than 0; any certified lower bound for W from pair positivity; μ < ½; any AH refutation.

---

## 8. Sources: read, snippet-only, blocked

- **Read in full (local):** `push_D_last_mile.md`, `push_D_constants.py`, `push_D_ah_exact.py`, `push_D_lp.py`, `push_D_lp_gold{0,1}.{log,json}`, `TWO_SCALE_ZETA_TARGET.md`, `dyson_round7.md`, `dyson_round8.md`, `dyson_round16.md`, `dyson_round19.md` (§§1–3), `dyson_round20.md` (§§1–2), `dyson_round26.md` (grep for Z_T, A − 2M), `NEW_RESULTS.md` §7, `PROGRAMME_PAPER.md` §§7–9, `r1_levelB_barrier.md`.
- **Search snippets only:** Tao (8 May 2019 post); Lagarias–Rodgers 2020; GLSS 2025 (arXiv:2507.06823 and its Part I 2501.14545 introduction); GGÖS 2000; Goldston 1988; Conrey–Iwaniec 2002 (and Stopple's "On the theorem of Conrey and Iwaniec"); Rodgers–Vallabhaneni; GGM 2001.
- **Blocked (attempted):** academic.oup.com, par.nsf.gov, semanticscholar.org, eudml.org, alphaxiv.org, ui.adsabs.harvard.edu, researchgate.net, web.williams.edu, research-information.bris.ac.uk, ar5iv.labs.arxiv.org, sciencedirect.com (arxiv.org and terrytao.wordpress.com not attempted, per instructions).
- **Recalled, not verified:** GGÖS's hypothesis being GRH (corroborated by the GLSS snippet); the content of Goldston 1988; Rudnick–Sarnak's range; GM's constant; Preobrazhenskiĭ's record.

---

## 9. Concrete corrections for push D

1. §2.3(iii), Theorem 2.1, lines 2/3/10/12: replace "Goldston 1988, RH" by "Goldston–Gonek–Özlük–Snyder 2000, **GRH**"; give the RH-only LP number 0.0207 as the default and 0.0236 as the GRH variant; replace "best provable bound" by "pair-positivity relaxation value (LP, uncertified)".
2. Theorem 2.1(d): "⊭" for "⊬"; delete "equivalently"; restrict "(or about the zeros)" to statements with a truth value for the LR/ACUE process; add the tightness remark (§3.2).
3. 𝓕: open band |α| < 1.
4. §2.5: cells 0.02/0.05/0.1, initial grid u ≤ 40; "positivity ≥ −10⁻⁶ on the 0.002 grid; between grid points violations of order 2·10⁻³ occur; W moves by 3·10⁻⁶ on refinement"; add the u > 400 bound; state that no pointwise dual certificate was produced.
5. §2.1: fix the k ≥ 0 algebra; "exactly" → "up to o(1)" for E_T.
6. Line 7 / §3.1: "Level B ⟹ μ < ½ under (NR) [P]; producing Level B through a gap needs λ < λ* ≈ 0.472 in clock/CUE backgrounds [C]; Siegel-hardness of gaps below ½ is a heuristic via Conrey–Iwaniec, whose hypothesis is a count of small gaps at D-dependent heights".
7. Line 8 / §3.2: separate the proved barrier (band-limited/positivity/integrality inputs) from the heuristic one (arithmetic inputs); delete "this is the content of Rounds 8–28 having failed to close".
8. §1.1 GLSS: "unconditionally (no RH)"; drop "Gallagher–Mueller" unless read.
9. Line 6: tag the GM variance translation as a heuristic dictionary; keep Round 8's E_T identity as the [P] statement.
10. §1.3 Tao quote: keep the bracket but mark it as a gloss; note the odd-integer caveat.

**Scripts:** `refute_D_check.py` (this directory; log `refute_D_check.log`); LP dual/refinement re-run: `refute_D_lpdual.py` (this directory; logs `refute_D_lpdual_gold{0,1}.log`, `refute_D_lpdual_gold0_dc0007.log`; values quoted in §4).
