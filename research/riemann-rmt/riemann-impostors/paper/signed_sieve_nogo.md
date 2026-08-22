# The signed Maynard–Tao sieve: a no-gain theorem, and where the door actually is

**Bill (Qingyun) Sun · GPT5.6SOL · Fable**

*August 18, 2026 — research note. Answers the question "does removing positivity from the
Maynard–Tao variational problem open a new phase?" The answer is no, for a reason that is
elementary, exact, and — this is the useful part — tells you precisely what would have to
replace positivity.*

## 0. The question

Maynard–Tao weights are squares, w(n) = (Σ_d λ_d)², hence pointwise nonnegative. Positivity is
what makes the decode valid: if w ≥ 0 and S₂ − mS₁ > 0, where S₁ = Σ_n w(n) and
S₂ = Σ_n w(n)ν(n) with ν(n) = #{i : n + h_i prime}, then some n has ν(n) ≥ m + 1. Zhang's
Landau–Siegel program ("摆脱平方" — remove the square) and Iwaniec's well-factorable λ^± both
suggest that signed weights are the natural next class, and that positivity is a self-imposed
restriction. The concrete question we were asked to settle: **after allowing signed/indefinite
sieve weights, does the variational optimum exhibit a phase the classical positive family cannot
see?**

For a signed w the decode fails as stated — the positive excess can be manufactured by w(n) < 0
at prime-poor n. It is repaired by paying the **debt**

  D(w) = Σ_{n : w(n) < 0} |w(n)| · (m − ν(n))₊,

so that S₂ − mS₁ − D > 0 does imply the conclusion. The experiment is then to optimize the
repaired functional Φ(w) − βD(w) over the signed class, with β = 1 the true price, and look for
a phase transition in β or in any enlargement parameter.

## 1. The theorem

**Pointwise identity.** For every integer ν ≥ 0 and every m ≥ 1,

  (ν − m) + (m − ν)₊ = (ν − m)₊.

*(Both sides equal ν − m when ν ≥ m, and 0 when ν < m.)*

**Theorem (Signed No-Gain).** Write w = w₊ − w₋ with w₊, w₋ ≥ 0 of disjoint support. Then

  **S₂ − mS₁ − D(w) = Σ_n w₊(n)(ν(n) − m) − Σ_n w₋(n)(ν(n) − m)₊ ≤ Σ_n w₊(n)(ν(n) − m).**

*Proof.* S₂ − mS₁ = Σ w₊(ν−m) − Σ w₋(ν−m) and D = Σ w₋(m−ν)₊; subtract and apply the identity
to the w₋ terms. The final inequality holds because w₋ ≥ 0 and (ν−m)₊ ≥ 0. ∎

**Corollary.** Any DHL(k, m+1) conclusion obtainable from a signed weight w with the debt charged
at face value is already obtainable from the nonnegative weight w₊: if the repaired functional at
w is positive, then the plain functional at w₊ is positive. **The negative part is pure loss**,
and the loss is exactly Σ w₋(n)(ν(n) − m)₊ — the overshoot mass sitting on the negative support.

The theorem is pointwise, so it needs no model, no cell structure, no asymptotics, and it holds
for every k, m, tuple, and weight class simultaneously. It subsumes the weaker fact we proved
first (that the *naked* ratio sup Tr(BQ)/Tr(AQ) over indefinite Q equals the PSD value by
rank-one extremality): the naked-ratio statement is about dropping positivity from the objective;
this one says that even after correctly repairing the decode, the enlargement is empty.

**Verification.** Exact rational arithmetic on the finite arithmetic microcosm (n uniform over
ℤ_W, W = ∏ feature primes × ∏ big primes; ν = coprimality count on the tuple; weights in the
span of level-L features): the cellwise form of the identity holds with zero violations on all
96/150/180/24-cell models, and the inequality holds on 1,000 random signed weights across five
models (k = 3, 4, 5; m = 1, 2; L = 1, 2). Script `fab_theorem.py`.

## 2. What the numerics were really showing

Before the identity was noticed, the LP experiments produced three facts that looked like a phase
structure. All three are corollaries of the theorem, and each is instructive.

**(a) The critical-price kink.** Sweeping β in max{Φ(w) − βD(w) : S₁(w) = 1}, the value is
*exactly* the classical positive optimum for β above a sharp β\*, then acquires a signed optimizer
below it. Certified example (k = 3, m = 1, features {2,3,5,7}), exact-rational simplex with verified
dual: val_pos = **1087376209/3212440751** = 0.3384891094603102, signed vertex Φ = 1.2082816957…,
D = 0.4147152297…, giving the exact critical price

  **β\* = (Φ − val_pos)/D = 23051796480/10991046857 = 2.0973249209031…**,

the optimizer carrying 85% of its mass negative on 16 of 96 cells. Certified on both sides: at
β\* − 10⁻³ the optimum is 0.3389038246899884 > val_pos with a genuinely signed optimizer; at
β\* + 10⁻³ it equals val_pos as exact rationals. Below β_unb = 2.03265 the LP is unbounded (in
particular at β = 2, certified). Across eight model variants β\* ranged 1.44–6.72, and in five of the eight the window
(β_unb, β\*) was numerically **empty** (width < 10⁻⁶): the value falls off the classical plateau
directly into unboundedness. Table in `fab_phase_results.json`.

The theorem explains this: β\* > 1 always, because at β = 1 the signed class is dominated. The
"phase" lives entirely in the unphysical region β < 1, where the debt is charged at less than face
value.

**(b) The apparent linear gain in the coefficient budget.** Adding the constraint ‖w‖₁ ≤ A gives
λ_signed(A) with λ_signed(1) = λ_positive exactly (since ‖w‖₁ = S₁ = 1 forces w ≥ 0), and then a
strictly positive slope: dλ/dA at A = 1⁺ equals 0.320, 0.504, 0.894, 0.394 in the four models
(60–170% of the classical value per unit of budget), with the constraint active at every A and
asymptotically linear growth. This looks like a large gain and is not one: the decode criterion is
scale-invariant (only the *sign* of S₂ − mS₁ − D matters), and by the theorem the repaired value
is Φ(w₊) minus a loss, so what grows with A is simply the total mass of w₊, not the truth of the
conclusion. `fab_norm_results.json`.

**(c) Unboundedness at the true price.** At β = 1 every model is unbounded. Same cause: the affine
slice {S₁ = 1} does not bound ‖w₊‖ once negative mass is allowed, and Φ(w₊) scales with it. For
w ≥ 0 the normalization S₁ = 1 *is* the ℓ¹ norm — **that is the second, usually unremarked job
positivity does in Maynard–Tao: it makes the variational problem bounded.** Remove it and
boundedness must be re-imposed by hand; no choice of norm bound creates a gain, by the theorem.

## 3. Where the door actually is

The theorem has exactly two hypotheses, so there are exactly two escapes, and they are not
variational.

**(i) Charge the debt at less than face value (β < 1).** This requires arithmetic information that
bounds (m − ν)₊ on the *designed* negative support by strictly less than the truth — i.e. an input
that says "on this set, primes are more common than the trivial bound allows". This is precisely
the exceptional-character mechanism: near a Landau–Siegel zero the distribution of primes in the
relevant progressions is anomalously rigid, and the shortfall on a set designed around the
exceptional modulus can be bounded below face value. **Zhang's program is not one route among
several; by the theorem it is the only route that changes the variational picture at all.**

**(ii) Keep w evaluable while w₊ is not.** The theorem compares w with w₊, which presumes both are
usable. In the arithmetic setting they are not interchangeable: the positive part of a divisor-sum
quadratic is not itself a divisor-sum quadratic, so a signed, well-factorable λ can be evaluable at
level θ = 4/7, 3/5, 5/8 while its positive part is not evaluable at any level beyond 1/2. **This is
the entire content of the signed route: the gain is never variational, it is exclusively about
which weights the arithmetic can evaluate.** It is therefore correctly priced by the conditional
ledger (§4), not by any optimization over weight cones.

**Independent confirmation from the switching side.** The Chen-switch audit reaches the same
conclusion by a disjoint argument. Switching is a re-indexing bijection: it reduces the anatomical
depth of one linear form but never the number r of exact-primality conditions a debt term carries.
Chen's debt has r = 1 and is payable by an upper sieve (parity-free). Every DHL(k, m+1) conclusion
with m ≥ 1 forces residual debt with r ≥ 2; a two-vertex kill-graph is an edge, hence bipartite,
hence parity-blocked for every input class admitting Liouville twists. The escape is not a cleverer
switch but an input class in which the twist is inadmissible — the exceptional-character regime
again, or full GEH. Two independent analyses, one door.

## 4. The conditional ledger (what the door is worth)

If the debt is paid at level θ, the price list is fully computed. All eight m = 1 crossings below
carry exact-rational certificates produced this session (Galerkin engine, full-vector Rayleigh
quotients, no truncation loss); H(k) values are Engelsma-exact and were independently re-proved
here for k ≤ 62.

| θ | threshold 2/θ | k_min pure (certified M_k) | k_min ε (certified M_{k,ε}) | H₁ ≤ pure / ε |
|---|---|---|---|---|
| 1/2 (Bombieri–Vinogradov) | 4 | 54 | 50 | 270 / **246** (unconditional, current record) |
| 4/7 (BFI) | 3.5 | 31 (3.502015495…) | 29 (3.519881249…) | 140 / **130** |
| 7/12 (Maynard II, linear sieve) | 24/7 ≈ 3.4286 | 29 (3.443305315…) | 26 (3.433616497…) | 130 / **114** |
| 3/5 (Maynard II) | 10/3 ≈ 3.3333 | 26 (3.350647068…) | 23 (3.334615948…) | 114 / **94** |
| 5/8 (Pascadi) | 3.2 | 22 (3.207656229…) | 20 (3.222665844…) | 90 / **80** |
| 1 (Elliott–Halberstam) | 2 | 5 (M₅ = 2.007080) | — | **12** |

m = 2 rows (p9 product-profile engine, certified-lower-bound path, rigorous primes-past-k
diameters): θ = 4/7 → k = 5,647, H₂ ≤ 58,058; 7/12 → 4,835, 48,988; 3/5 → 3,931, 38,878;
5/8 → 3,022, 29,180; EH → 221, 1,498. m = 3: 4/7 → 202,528; 7/12 → 160,703; EH → 1,978
(H₃ ≤ 18,144). Every row is parity-consistent (all ≥ the floor 6, and ≥ the EH value 12).

**The missing estimate, stated precisely.** None of BFI (Acta Math. 156, Thm 10), Maynard II
(Mem. AMS 1543), or Pascadi (arXiv:2505.00653) covers the sums the decode generates: all three fix
one residue a for every modulus, while the decode's residues a ∈ A_i(q) are CRT-composed from the
fixed shift set {h_i − h_j} and therefore vary with q. What would suffice is the intermediate
statement

> **(E_θ).** Fix an admissible tuple H, an index i, and A, ε > 0. For coefficient systems c_q(a)
> jointly well-factorable with the residue selection — for every factorization q = q₁q₂ (resp.
> q₁q₂q₃) with ∏Q_j = x^{θ−ε} one can write c_q(a) = ∏_j γ_j(q_j, a mod q_j), |γ_j| ≤ 1, with
> a mod p ∈ {h_i − h_j mod p : j ≠ i} for all p | q —
>   Σ_{q ≤ x^{θ−ε}} Σ_{a ∈ A_i(q)} c_q(a) · E(x; q, a) ≪_{H,A,ε} x (log x)^{−A}.

(E_{4/7}) is "BFI Theorem 10, uniform over the CRT residue system of a fixed tuple polynomial".
Evidence that the gap is bridgeable rather than parity-hard: Polymath8a's MPZ[ϖ,δ] is exactly this
statement's absolute-value cousin, proved by the same dispersion + Deligne technology, but only to
level 1/2 + 2ϖ ≤ 0.5286 and for densely-divisible moduli. So (E_θ) interpolates two proved
endpoints — bilinear strength with one residue, and residue flexibility at weak level.

## 5. Verdict

**No new phase.** The signed enlargement of the Maynard–Tao variational problem is empty: with the
decode debt charged at face value, every signed weight is dominated by its own positive part, by an
exact pointwise identity. This kills the route cheaply and completely, as intended — and it
converts an open-ended search into two sharply stated arithmetic requirements, (E_θ) for
evaluability and the exceptional-character input for sub-face-value debt. The variational side of
the signed programme is closed; everything of value in it is arithmetic.

*Artifacts: `fab_theorem.py` (identity, exact verification), `fab_phase.py` /
`fab_phase_results.json` (β-structure, β\*, β_unb across eight models), `fab_norm.py` /
`fab_norm_results.json` (ℓ¹-budget ramp), `sgn1_*` (finite model + LP engines), `sgn2_*`
(ledger certificates, `sgn2_certificates.json`, `sgn2_mk_large.json`).*
