# refute A — audit of `push_A_threeblock_limit.md` (lim N²D_N = 2 for the symmetric 3-block)

**Refuter (Fable), 6 September 2026.** Task A_limit_theorem. Check script: `refute_A_limit_theorem.py` (this directory; sections `sym`, `asym2`, `asym2fast`, `models`, `blocks`, `polyroots`, `prop71`, `roots`). Logs of every run quoted below are reproduced in §6. Status tags as in the programme: [P] proved, [C] computed, [O] open.

## 0. Verdict in one paragraph

**The headline [P] claims survive.** I audited the whole proof chain of Theorem 5.4 (Lemmas 2.1–2.3, 3.1–3.3, Prop. 3.4, Lemma 4.1, Lemmas 5.1–5.2, the confinement/counting argument), Prop. 6.1 (D_N = first zero of P_s′(1)), Prop. 6.2 (τ_N = 2 − 4/(3N²) + c₂/N⁴), Prop. 7.1 (midpoint-insertion closed form) and Prop. 7.3 (fold correction), line by line, and re-derived every formula that enters them; I found no invalid step, no missing hypothesis that is actually used, and no sign error that propagates. All numbers that enter the [P] statements were reproduced by an *independent* implementation (different code, different root-finder, mpmath, up to N = 4096) to every printed digit. **Genuine errors exist, but only in [C] claims and in one derivation:** (E1) the local model the deliverable calls the "9-block" is the **11-block**; the true 9-block constant is τ* = 2.05736, not 2.0689, and the finite-N 9-block data converge to 2.05736; (E2) the cusp derivation of §6.4 contains **two compensating errors** (the tilt term has the wrong sign, and an O(ε²) constant equal to exactly −4π/3·ε² is omitted); the final coefficient 2·(π²/4)^{1/3} = 2.70257 is nevertheless right, and I confirm it to 4 digits at N = 4096 — which the deliverable's own table did not (its N = 256 datum 2.695 is a 4·10⁻⁹ solver error); (E3) a handful of smaller slips: Prop. 6.1's proviso "true for all N ≥ 4 by Theorem 5.4" is a logical overreach (the theorem is asymptotic with no explicit N₀); hypothesis (H) of Theorem 7.2, as written, is false for every symmetric model to which it is applied (the zero count drops by 4, not 2); "of order λ²" in §6.3 should be λ^{2/3}; the enumeration agreement claimed as 10⁻⁸ is 6·10⁻⁷ at N = 11; and `midpoint_models.py` prints a spurious answer for the double 3-block (the deliverable's stated value is right). **Structured verdict: minor-issues** — no [P] statement is refuted; two [C] statements need correction (E1 substantively, E2 in its derivation).

## 1. Re-running the proposer's scripts

All four scripts run to completion (`threeblock_exact.py`, `threeblock_asymptotics.py`, `midpoint_models.py`, `fold_constants.py`, plus `local_convergence_check.py`); their printed output agrees with the numbers quoted in the deliverable, with three exceptions that are the proposer's own bookkeeping rather than mathematics:

* `threeblock_exact.py` part (3): block4odd N = 11, enumeration 1.9888690636 vs exact 1.9888696692, **diff 6.1·10⁻⁷** (the deliverable says "agreement 10⁻⁸"; at N ≤ 10 the diffs are 1–9·10⁻⁸). Part (1) also prints `rel.err Q0 = 2.64e+00` for block4odd N = 11 — an artefact of its sign-ambiguity handling (both ±Q are compared to the product but only over a grid that happens to include a pole-cancelled point); my own coefficient check (`sym` section) gives max|a_j − a_j^closed| = 4·10⁻¹⁵ … 3·10⁻¹³ for all three families at N = 8, 9, 16, 17, so the closed forms are right.
* `midpoint_models.py` prints `two3: first double zero at u*=0.0 tau*=1.95 q_uu=0.0`. That is a bug in the script (for an *even* model q_u(0,τ) ≡ 0, so its "triple-zero-at-0" test always fires at the bottom of the bracket). The deliverable's stated value (double zero at (2π, 2)) is correct — see §2.3.
* `heat_depth.py`'s block4even value at N = 256, 1.999978634911, is 4.4·10⁻⁹ below the true 1.999978630550 (§2.2). The deliverable calls heat_depth "reliable for this family"; it is reliable to ~10⁻⁹ only, which is exactly the size that matters for the N^{−8/3} claim.

## 2. Independent checks

### 2.1 Symmetric families: exact τ_N, c₁ = −4/3, c₂ (section `sym`) [C, reproduces]

Independent code (closed-form coefficients checked against `numpy.poly`; F_N(τ) = ∂_x Q_s(0) evaluated from the Fourier sum; first zero by bracketing from τ = 1.5 and 140 mp bisection steps at 40 digits, not `findroot`/anderson):

| family | N | τ_N (mine) | τ_N (deliverable) | N²(τ−2) | N⁴(τ−2+4/3N²) |
|---|---|---|---|---|---|
| block4odd | 65 | 1.999684328472802 | 1.99968432847280 | −1.333712 | −1.60072 |
| block4odd | 513 | 1.999994933524035 | 1.99999493352403543 | −1.3333394 | −1.600012 |
| block33 | 128 | 1.999918577050696 | 1.99991857705069568 | −1.334034 | −11.47319 |
| block33 | **384** | 1.99999095722711 | (not tabulated) | −1.333411 | −11.47000 |
| block33 | 512 | 1.999994913570071 | 1.99999491357007119 | −1.3333771 | −11.46983 |

Agreement to all printed digits; c₂ → −1.6 and → −11.4696 = −8/5 − π² as claimed. Fact (F1)'s N = 384 value 1.999990889523 is 6.8·10⁻⁸ below the exact block33 value, and its N = 128 and 256 values are 1.1·10⁻⁸ and 4.7·10⁻⁸ low — the deliverable's diagnosis "F1 was block33, drift = solver error" is confirmed.

### 2.2 Asymmetric family block4even: the N^{−8/3} cusp term (sections `asym2`, `asym2fast`) [C, corrected and confirmed]

The first collision was found as a genuine 2-D root (Q_s(x) = ∂_x Q_s(x) = 0) by mp Newton at 40 digits from exact closed-form coefficients, seeded by a double-precision zero-count scan, and *verified as the first* by re-counting zeros (coarse grid plus an 8000-point grid around the fold) on a τ-grid up to τ_N − 10⁻⁴ (step 2·10⁻³ for N ≤ 256, 0.1 above):

| N | τ_N = N²D_N | N²(2−τ_N) | (N²(2−τ_N) − 4/3)·N^{2/3} | deliverable |
|---|---|---|---|---|
| 16 | 1.99300804179871 | 1.7899413 | 2.89928 | 2.899 |
| 32 | 1.99842905019986 | 1.6086526 | 2.77504 | 2.775 |
| 64 | 1.99963282131129 | 1.5039639 | 2.73009 | 2.730 |
| 128 | 1.99991209969416 | 1.4401586 | 2.71319 | 2.713 |
| 256 | 1.99997863054997 | 1.4004683 | **2.70671** | **2.695** (solver error) |
| 512 | 1.99999475255446 | 1.3755864 | 2.70419 | — |
| 1024 | 1.99999870305884 | 1.3599414 | 2.70321 | — |
| 2048 | 1.99999967811276 | 1.3500929 | 2.70282 | — |
| 4096 | 1.99999991989788 | 1.3438906 | 2.70267 | — |

Limit 2·(π²/4)^{1/3} = 2.702568. The residual 2.70267 − 2.70257 = 1.0·10⁻⁴ at N = 4096 decays by a factor 2.53 per doubling (N^{−4/3}), so the claimed **τ_N = 2 − 4/(3N²) − 2.7026·N^{−8/3} + O(N^{−4}) is confirmed to four digits**. Note that with the deliverable's own data (…, 2.713, 2.703, 2.695, monotonically *through* the predicted value) the claim was not supported; it is the corrected N = 256 value and the N ≥ 512 points that establish it.

**But the derivation in §3.3/§6.4 is wrong in two compensating places** (E2, §3 below).

### 2.3 Local midpoint-insertion models (section `models`) [C, one mislabelling found]

Every real zero of q_τ = e^{−τ/4}·Re/Im[e^{iu/2}P_τ(u+iτ)] on (0, 5π) was tracked on a τ-grid of step 0.002 and the first merging refined by a 2-D solve; Prop. 7.1's closed form was first checked against direct Gaussian-convolution quadrature (max error 7·10⁻¹⁵, 3·10⁻¹⁴, 6·10⁻¹³ for the 5-, 7-, 9-block polynomials).

| model | p, L | first double zero (u*, τ*) | merging pair started at | deliverable |
|---|---|---|---|---|
| 5-block | u²−π², sin | (π, 2.0000000000), q_uu = −1.2131 | π, 2π | (π, 2) ✓ |
| double 3-block | u²−4π², cos | (2π, 2.0000000000), q_uu = +1.2131 | 2π, 3π | (2π, 2) ✓ |
| 7-block | u(u²−4π²), cos | (5.9643126848, 2.0381260536), q_uu = 14.478 | 2π, 3π | ✓ |
| **9-block** | **(u²−π²)(u²−9π²), sin** | **(8.8860856 = 2.8285π, 2.0573579730)**, q_uu = 261.15 | 3π, 4π | **2.0689 ✗** |
| 11-block | u(u²−4π²)(u²−16π²), cos | (11.8606259 = 3.7754π, 2.0688935596) | 4π, 5π | called "9-block" |
| [1,1,2,2,1,1] | u²−9π², sin | (3π, 2.0000000001) | 3π, 4π | not stated |

So the 5-block, double-3-block and 7-block claims reproduce exactly (including "no earlier double zero" on (0,5π) for τ ≤ 3, and the zeros just before the merge, e.g. 7-block: 0.867π, 1.894π, 1.904π, 4.715π), but the "9-block" line is the 11-block (E1).

### 2.4 Finite-N multi-block families (sections `blocks`, `polyroots`) [C]

Generic fold solver (mp product coefficients at 60 + N/4 digits, double-precision count scan, mp 2-D Newton, first-collision verification as in §2.2), and, fully independently of any Fourier/heat representation, `mp.polyroots` on the flowed polynomial with bisection on the off-circle indicator (tolerance 10⁻¹⁵):

| family | N | N²D_N (fold solver) | N²D_N (polyroots) | N²D_N (deliverable, robust) | N²(τ_N − τ*) | predicted |
|---|---|---|---|---|---|---|
| 7-block | 16 | — | 2.017717012851 | 2.017714843750 | | |
| 7-block | 17 | — | 2.021979178848 | 2.021979178838 | | |
| 7-block | 24 | — | 2.030167157485 | 2.030167157483 | | |
| 7-block | 33 | 2.034196345071 | 2.034196345071 | 2.034196338652 | −4.2795 | |
| 7-block | 65 | 2.037135368679 | — | 2.037135310173 | −4.1856 | |
| 7-block | 129 | 2.037875950822 | — | 2.037870579847 | −4.1620 | |
| 7-block | 257 | 2.038063131044 | — | (not reported) | **−4.1560** | **−4.1540** |
| 9-block | 17 | — | 2.032700299359 | — | | |
| 9-block | 33 | 2.051868526544 | 2.051868526544 | 2.051868514973 | −5.978 (vs 2.05736) | |
| 9-block | 65 | 2.056002600008 | — | 2.056003799438 | −5.727 | |
| 9-block | 129 | 2.057017582093 | — | 2.056533203125 | −5.664 | → ≈ −5.64 |
| 5-block | 17 | — | 1.990372454420 | 1.990372454416 | | |
| 5-block | 65 | 1.999367031642 | — | 1.999367031298 | −2.6743 | |
| 5-block | 129 | 1.999839637124 | — | 1.999839626618 | −2.6686 | |
| 5-block | 257 | 1.999959618568 | — | 1.999959727377 | **−2.6672** | **−8/3** |
| double 3-block | 16 | — | 1.988014867577 | 1.988014867578 | | |
| double 3-block | 32 | — | 1.997303715214 | 1.997303715220 | | |
| double 3-block | 64 | 1.999343288763 | — | 1.999343288988 | −2.6899 | |
| double 3-block | 128 | 1.999836886590 | — | 1.999836878627 | −2.6725 | |
| double 3-block | 256 | 1.999959287855 | — | 1.999959413409 | **−2.6681** | **−8/3** |
| 11-block | 33 | 2.061688836107 | — | — | −7.846 (vs 2.06889) | |
| 11-block | 65 | 2.067164398563 | — | — | −7.306 | → finite |
| block4even | 16, 32 | (§2.2) | 1.993008041799, 1.998429050200 | 1.993008041801, 1.998429050189 | | |
| block33 | 16, 32 | (§2.1) | 1.994613077983, 1.998686923390 | exact 1.994613077983, 1.998686923390 | | |
| block4odd | 17, 33 | (§2.1) | 1.995367105387, 1.998774283610 | exact 1.995367105387, 1.998774283610 | | |

Conclusions: (i) the 7-block correction converges to −4.154 with clean N^{−2} differences (0.094, 0.024, 0.006) — the deliverable's own evidence (4.28, 4.19, 4.25 from `heat_depth_robust.py`) was too noisy to call it "confirmed", but the claim is right; its robust solver is off by 6·10⁻⁹ at N = 33 and 5·10⁻⁶ at N = 129 for the 7-block and by 5·10⁻⁴ at N = 129 for the 9-block; (ii) the 5-block and double-3-block corrections converge to −8/3 as claimed; (iii) **the finite-N 9-block converges to 2.05736, the constant of the true 9-block model, not to 2.0689**: against 2.0689 the "corrections" N²(τ_N − 2.0689) would be −18.7, −54.6, −196 — not O(1); conversely the finite-N **11-block** ([1]^{10} + 2^k + [12] + 2^{N−11−k}) gives N²(τ_N − 2.06889) = −7.85, −7.31 at N = 33, 65, i.e. 2.0689 is the 11-block constant; (for the 9-block at N = 257 and the 11-block at N ≥ 129 my double-precision seeding scan fails — the monic coefficients are of size ~N⁴–N⁵ and cancel catastrophically in double precision — so those N are not reported; nothing in the conclusion depends on them); (iv) `heat_depth.py`'s 7-block value 1.7754 (N = 16) is indeed spurious — three independent methods give 2.01771–2.01772; the deliverable's diagnosis of `depth_pair` (rejection of the extremum once it leaves the *initial* gap) is correct, and I add that for the 5-block the merge happens exactly *at* the initial left endpoint of the (3,4) gap, which is why `run_families_A.py block5` (min over pairs 0..5) is wrong while `run_families.py block5` (pairs 0,1,2) happened to be right — the deliverable attributes the failure to the wrong script.

### 2.5 Prop. 3.4 rates (`local_convergence_check.py` re-run) [C, reproduces]

N²·sup|q_τ^N − q_τ| = 20.957, 20.746, 20.690, 20.676, 20.672 (block4odd, N = 17…257) and 21.620, 20.902, 20.728, 20.685, 20.674 (block33); N⁴·sup|q_τ^N − q_τ − r_τ/N²| = 87.5, 86.4, 86.2, 86.1, 86.2 and 243.1, 236.7, 235.1, 234.7, 234.6. Identical to the deliverable.

## 3. Errors found

### E1 [C, substantive] — the "9-block" of §7.1/§7.4/§0(5)/§8 is the 11-block

Quote (§7.1): "**9-block** [1]^8: u(u²−4π²)(u²−16π²)·cos(u/2)". The zeros of this function are 0, ±π, ±2π, ±3π, ±4π, ±5π, ±7π, ±9π, …: eleven consecutive sites −5…5 followed by a gap of 2, i.e. the block [1]^{10}. The 9-block [1]^8 (sites 0…8, then 10, 12, …; before it −2, −4, …) has, centred at site 4, roots 0, ±π, ±2π, ±3π, ±4π, ±6π, ±8π, … = zeros of **(u²−π²)(u²−9π²)·sin(u/2)** — the lattice is the *even* sites (L = sin), exactly as for the 5-block, since k midpoints give a (2k+1)-block and the lattice parity alternates with k (3: cos, 5: sin, 7: cos, 9: sin, 11: cos). Consequences: (a) "9-block 2.0689…" (§0 item 5, §7.4, §8 ledger) is the 11-block constant; the 9-block constant is **τ* = 2.0573579730** (first double zero at u* = 2.8285π, pair (3π, 4π), q_uu = 261.2); (b) `model_nine.log` ("zeros just before: 2.88, 5.74, 8.55, 11.86, 11.86", pair from (4π,5π)) describes the 11-block; (c) the finite-N `block9` runs of `heat_depth_robust.py` (2.0519, 2.0560, 2.0565) were never compared with "2.0689" — had they been, the mismatch would have shown; my fold solver gives 2.051869, 2.056003, 2.057018 at N = 33, 65, 129, i.e. N²(τ_N − 2.05736) = −5.98, −5.73, −5.66 → a finite constant, confirming the corrected model. The qualitative statement "longer blocks collide later" survives (2, 2, 2.0381, 2.0574, 2.0689 for the 3-, 5-, 7-, 9-, 11-block), and so does "the 3-block is not the maximiser for N ≥ 11".

### E2 [derivation of a [C] claim] — §6.4's cusp constant is right for the wrong reason

Quote (Lemma 3.3 proof and §6.4): "the a²b term produces the even contribution **−πv²/(4N²)**", "φ_N(v) = v + (v³/12 **−** πv²/4)/N² + …", "C = ε·e^{τ/4} r̃_τ(0) = −(π/2)εσ + O(εσ²)". Both are wrong:

1. With the deliverable's own φ_N = 2N sin a cos b / cos(a+b) (a = v/2N, b = π/2N): sin a cos b/cos(a+b) = tan a/(1 − tan a tan b) = tan a (1 + ab + …), so the even term is **+πv²/(4N²)**. Numerically, N²(φ_N(v) − v − v³/12N²) = 0.7855, 3.1426 at v = 1, 2 (N = 100) against πv²/4 = 0.7854, 3.1416. Symbolically (sympy): φ_N = u + (u³/12 + πu²/4)/N² + (u⁵/120 + πu⁴/24 + π²u³/16 + π³u²/48)/N⁴ + O(N⁻⁶).
2. The constant term of the normal form is therefore e^{τ/4}q_τ^N(0) = **+(π/4)τσ·ε − (π/48)τ(−2τ³+24τ²−24τ+π²τ−2π²)·ε² + …**, and at τ = 2 the second bracket equals **−4π/3 ≠ 0**. The deliverable's "O(εσ²)" error term is thus wrong: there is an O(ε²) constant, and at the fold, where σ_c ≈ (4/3)ε, it is of the *same order* as the term kept. The correct total is C(σ_c) = (π/2)(4/3)ε² − (4π/3)ε² = **−(2π/3)ε²**, which coincides with the deliverable's −(π/2)εσ_c = −(2π/3)ε² only because the two errors cancel exactly (sign of the tilt ↔ the identity C₂(2) = −4π/3, which follows from E[V⁴cos(V/2)], E[V²cos(V/2)] at τ = 2 applied to πu⁴/24 + π³u²/48). Since only C² enters A³ = (9/16)C², the coefficient 2(π²/4)^{1/3} survives, and §2.2 confirms it to 4 digits. Two things do change: the trajectory of the middle root (with the true C(σ) = (π/2)εσ − (4π/3)ε² + …, q_τ^N(0) is *positive* for σ > (8/3)ε, so the middle zero first sits at u < 0, crosses u = 0 at σ ≈ (8/3)ε and only then merges with the root from +π at u* > 0; numerically at N = 64: N²q_τ^N(0) = +0.0089 at τ = 1.99 against the corrected leading term (π/4)e^{−τ/4}τσ = +0.0095, and −0.00027 at τ = 1.99963 with zeros at u = −0.0193, +0.0062, +0.0109 just before the merge, u* = +0.0083 — whereas the deliverable's C = −(π/2)εσ < 0 would keep the middle zero at u > 0 throughout), and the next-order term N^{−10/3}, which is not claimed. Nothing in the [P] Theorem 5.4 is affected (only |φ_N − v| ≤ C(1+|v|³)/N² is used there).

### E3 [P-tagged statements with logical slips; none propagates]

* **Prop. 6.1, proviso.** "provided this minimum is < −log cos(π/N) (true for all N ≥ 4 by Theorem 5.4 and, for N ≤ 12, by the enumeration)". Theorem 5.4 is an asymptotic statement with an unspecified N₀(ε); it cannot certify the proviso for 13 ≤ N < N₀. For each tabulated N the proviso *is* verified (the computed first zero is ≈ 2 < π²/2), so Prop. 6.1 holds [P] for N ≥ N₀ and [C] for each N ≤ 2049 that was computed — but not "for all N ≥ 4" by the argument given. (A uniform proof would need an explicit constant in Prop. 3.4, which Lemma 3.3 leaves as "an absolute constant C₀".)
* **Theorem 7.2, hypothesis (H).** "(H) … the number of zeros of q_τ in [−R,R] … equals **n−2** (all simple) for τ ∈ (τ*, τ*+δ]". For every model to which the theorem is applied (5-block, double 3-block, 7-block, all odd or even in u), the fold at u* and its mirror image at −u* occur at the same τ*, so the count drops by **4**. As literally stated (H) is false for these families; the proof only needs "drops by ≥ 2", so the fix is trivial, but the statement should be corrected. (This also explains why my first-collision verifier needed a mirror-aware local grid — §6.)
* **§6.3**: "the shift is still O(N⁻²) (of order **λ²**)". For a 1/N tilt λ the fold condition (σ/2 − 2ε/3)³ = (9/4)λ²σ²ε gives δ = σ_c − 4ε/3 = (32λ²)^{1/3}ε, i.e. of order **λ^{2/3}** — non-analytic in λ, as expected at a cusp. The order-N⁻² conclusion is unaffected.
* **§6.1, table caption**: "(agreement 10⁻⁸, the enumeration's own tolerance)": 6.1·10⁻⁷ at N = 11 (block4odd), 8.9·10⁻⁸ at N = 10.
* **§0(6)/§7.4**: "`run_families.py`'s `block5` numbers are affected at the O(N⁻²) level" — it is `run_families_A.py`'s (`families2.log`'s block5 column from `run_families.py` gives N²(2−τ_N) = 2.68, 2.70 at N = 256, 384, i.e. the right −8/3).

### What I tried and could not break

* **Theorem 5.4.** Checked: the sign bookkeeping in (1.1) and (1.2); Lemma 2.1 (Σθ_j = πN ⇒ i^N; the (−1)^N); Lemma 2.2 (sin((x−π)/2) = −cos(x/2), the parity of the removed sites); Lemma 3.2 ([∂², u] = 2∂ terminates the Hadamard series); the normalisations φ_N′(0) = 1; (B1)–(B3) (all elementary Taylor remainders; C₀ unspecified but plainly finite); (B2) via |(z^N+1)/(z+e^{iα})| ≤ N (needs (−e^{iα})^N = −1, true for α = ∓π/N with the right parity of N) and 2Σ|U_k| ≤ N²; Prop. 3.4 (inner/outer split; the outer bound as written drops the |v| growth of |g| outside |v| ≤ N but the Gaussian tail absorbs it — cosmetic); Lemma 4.1 (h′ = (sin u − u)/(2sin²(u/2)) < 0; the derivative at ±u_τ equals e^{−τ/4}(sin u_τ − u_τ)/(2 sin(u_τ/2)) after substituting τ = u cot(u/2) — verified); Lemmas 5.1–5.2; and the confinement argument: (iii) ⇒ no zero crosses ±2π, Lemma 1.1 ⇒ the colliding pair is a 1-gap pair, (i)/(ii) ⇒ contradiction on each side. I looked specifically for (a) a hidden use of oddness (there is none — block4even is genuinely covered), (b) an interchange of the N → ∞ limit with the first-collision time (there is none: the argument is a zero count at fixed τ, uniform in τ on compacts), (c) a gap in "multiplicity ≥ 2 of P_s ⇒ multiplicity ≥ 2 of the real function Q_s" (fine: Q_s = κe^{−iNx/2}P_s(e^{ix}) is real-analytic in x), (d) the possibility that lattice roots at ±3π enter [−2π,2π] (excluded by (iii), not by Theorem A — the deliverable says so correctly). Nothing failed.
* **Prop. 6.1 converse direction**: the only collision compatible with oddness and Lemma 1.1 is g(D_N) = 0; correct.
* **Prop. 6.2**: (6.1) re-derived (∂_uG_τ(−v) = (v/2τ)G_τ(v)); a₀, a₂, a₄, c₁ = −4/3, c₂ re-derived symbolically (my own sympy run agrees with `threeblock_asymptotics.py`: a₂(2) = −(2/3)e^{−1/2}, a₀′(2) = −e^{−1/2}/2).
* **Prop. 7.1**: the conjugation e^{−iu/2}(u+2τ∂)e^{iu/2} = u + iτ + 2τ∂ and the polynomial identity in c are correct; numerically verified against quadrature (§2.3).
* **Prop. 7.3 constants**: r_{τ*}(u*) = −(16/3)e^{−1/2} and q_uu(π,2) = −2e^{−1/2} for the 5-block re-derived by hand (Ψ_τ(π+2i) = [−32 + i(8π³+64π)]/6); for "five_even" I checked by hand that the extra piece (π/4)(u²−π²)(2u+π) of ψ contributes exactly 0 to r at both (±π, 2), so the same −8/3 is right.
* **Counterexample search for "lim = 2"**: none possible in principle once Theorem 5.4 stands; numerically every family in §2 approaches its model constant with O(N⁻²) corrections.

## 4. Claim ledger (refuter's view)

| deliverable statement | proposer | refuter |
|---|---|---|
| Theorem 5.4: lim N²D_N = 2 for block4odd, block4even, block33 | [P] | **[P] — proof checked, no error** |
| Prop. 6.1: D_N = first zero of P_s′(1) (symmetric families) | [P] | [P] for N ≥ N₀ and [C] for each tabulated N; the "for all N ≥ 4" wording is unjustified (E3) |
| Prop. 6.2: τ_N = 2 − 4/(3N²) + c₂/N⁴, c₂ = −8/5, −8/5−π² | [P] | **[P]**; reproduced to 15 digits, c₂ to 7 digits |
| block4even τ_N = 2 − 4/(3N²) − 2.703·N^{−8/3} | [C] + derivation | **[C] confirmed to 4 digits (2.70267 at N = 4096 → 2.70257)**; derivation has two compensating errors (E2) |
| Prop. 7.1 closed form; Prop. 7.3 fold formula | [P] | [P] |
| Theorem 7.2 (limit under (H)) | [P] | [P] once (H) is corrected to "count drops by ≥ 2" (E3) |
| 5-block and double 3-block: τ* = 2 exactly, first double zero | [P]/[C] | [P]/[C] reproduced; finite-N corrections → −8/3 confirmed |
| 7-block τ* = 2.0381260536, N²(τ_N − τ*) → −4.154 | [C] | [C] confirmed (−4.156 at N = 257) |
| **9-block τ* = 2.0689** | [C] | **wrong: that is the 11-block; 9-block τ* = 2.05736** (E1) |
| `heat_depth.py` failure mode; robust solver correct to 10⁻⁹ | [C] | failure mode confirmed; robust solver is 10⁻⁹ for the 3-block but 5·10⁻⁶ (7-block, N = 129) and 5·10⁻⁴ (9-block, N = 129) elsewhere |
| F1's −1.34 is −4/3, N = 384 drift is solver error | [C] | confirmed (exact 1.99999095722711 vs F1 1.999990889523) |

## 5. Structured verdict

* **Verdict: minor-issues.** The theorem the task asked for (lim N²D_N = 2, [P]) and its exact refinement (Prop. 6.1–6.2, [P]) are sound and reproduced independently. Two computed claims need correction: the "9-block" constant (E1, a mislabelled model; corrected value 2.05736) and the derivation (not the value) of the N^{−8/3} coefficient (E2). Four wording/logic slips (E3) do not propagate.
* Nothing in the deliverable is refuted at the level of a [P] statement; no counterexample to any [P] claim exists, and I looked for one in every place a limit interchange, a parity assumption or a sign could hide.

## 6. Files and logs

* `refute_A_limit_theorem.py` — sections: `sym` (§2.1), `asym2`/`asym2fast` (§2.2), `models`/`prop71` (§2.3), `blocks`/`polyroots` (§2.4), `roots` (numpy.roots; unreliable beyond N ≈ 25 for long blocks, kept for the record). The first-collision verifier is mirror-aware (a fine local grid at the fold and at its mirror image; the double-3-block "u* rel. centre" printed by the `blocks` section is offset by π because that family's block has an even number of sites — its folds are at ±2π as in the model).
* Scratch logs (session scratchpad, copied here in spirit): `sym` reproduces the table of §2.1; `asym2fast` N = 512…4096 residuals 2.704194, 2.703209, 2.702821, 2.702668 with "FIRST collision verified"; `blocks` block7 33/65/129/257, block9 33/65/129, block5 65/129/257, two3 64/128, all with mp residual |Q|+|Q_x| ≤ 10⁻⁶⁵; `polyroots` as in §2.4. At N = 129 (9-block) and N = 257 (7-block) the double-precision count scan is no longer meaningful (coefficients of size ~N³ with cancellation), so those τ_N are certified as double zeros by the mp residual and as *first* only by continuity of the N⁻² pattern.
