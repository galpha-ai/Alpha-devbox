# Telling the Riemann Zeros from Their Impostors

**Bill (Qingyun) Sun · GPT5.6SOL · Fable** — August 2026

This repository accompanies the paper [`paper/impostors_paper.md`](paper/impostors_paper.md).
It contains, for each major result: the statement, its verification status, the construction or
certificate that witnesses it, and (for the deterministic core) a Lean formalisation.

These are computer-assisted results produced by a human mathematician working with AI systems in an
adversarial loop. They have **not been refereed**. Every claim below is labeled **[proved]**,
**[reduced]** (to a cited published theorem plus a stated open lemma), **[computed]** (exhaustive or
certified computation), or **[numerical]**. We do **not** claim the Riemann hypothesis, the
Alternative Hypothesis, the density conjecture, the twin prime conjecture, or any improvement to
H₁ ≤ 246.

---

## 1. Prime-gap records **[proved, machine-certified]**

For H_m = liminf (p_{n+m} − p_n):

| quantity | new bound | previous record | k |
|---|---|---|---|
| H₂ | **173,438** | 396,504 (Stadlmann 2023/25) | 15,856 |
| H₃ | **13,859,802** | 24,797,814 (Polymath8b 2014) | 923,601 |
| H₄ | **1,120,662,828** | 1,431,556,072 (Polymath8b 2014) | 56,000,000 |

Unconditional: Maynard's theorem + Bombieri–Vinogradov + ball-arithmetic certificates for the
variational constants (M₁₅,₈₅₆ ≥ 8.0133…, M₉₂₃,₆₀₁ ≥ 12.0067…, M₅₆·₁₀⁶ ≥ 16.0655…, each under
three independent certification regimes) + explicit admissible tuples verified by two independent
implementations. The gain is purely variational: a layer-cake identity and shaped subexponential
tails recover ≈1.1 units of log k that the crude truncation bound used by all records since 2014
had discarded. Certificates: [`certificates/`](certificates/). Statement and hypothesis chain:
[`paper/H2_H3_record_announcement.md`](paper/H2_H3_record_announcement.md).

## 2. The signed-sieve no-gain theorem **[proved]**

For ν(n) = #{i : n+h_i prime}, the pointwise identity (ν−m) + (m−ν)₊ = (ν−m)₊ gives: for any
signed weight w = w₊ − w₋ with decode debt D(w) = Σ_{w<0}|w|(m−ν)₊,

> S₂ − mS₁ − D(w) = Σ w₊(ν−m) − Σ w₋(ν−m)₊ ≤ Σ w₊(ν−m).

**The negative part is pure loss**: any bounded-gap conclusion obtainable from a signed weight at
face-value debt is already obtainable from its positive part. This closes the variational side of
the "remove the square" programme and shows its entire content is arithmetic — either sub-face-value
debt (the exceptional-character mechanism) or evaluability of w without w₊ (well-factorable levels
θ = 4/7, 7/12, 3/5, 5/8, with certified conditional price list H₁ ≤ 130/114/94/80 and the exact
missing estimate (E_θ) stated). Verification in exact rationals:
[`verification/signed_no_gain.py`](verification/signed_no_gain.py). Full note:
[`paper/signed_sieve_nogo.md`](paper/signed_sieve_nogo.md).

## 3. The two-body comparison theorem **[proved]** and the depth scaling law **[reduced]**

Define the finite de Bruijn–Newman depth −Λ of a configuration on the unit circle as the first
collision time of its zeros under the backward heat flow P_s(z) = Σ a_j e^{s·j(N−j)} z^j
(zeros obey θ̇_j = −Σ_{k≠j} cot((θ_j−θ_k)/2)).

**Theorem A [proved].** Every adjacent gap obeys g′ ≥ −2cot(g/2): each of the other zeros strictly
slows the collapse (cot(·/2) is decreasing on (0,2π), and adjacency fixes the sign of every
background term). Hence

> −Λ ≥ −log cos(δ_min/2) ≥ δ_min²/8, i.e. ρ := 8(−Λ)/δ_min² ≥ 1, always.

**Theorem B [proved, conditional].** If the background stiffness satisfies S ≤ A·N² (clock value:
exactly (N²−1)/6), then −Λ ≤ (δ_min²/8)(1 + O(AN²δ_min²)).

**The scaling law [reduced].** With the cited CβE extreme-gap theorems (Ben Arous–Bourgade;
Feng–Wei), Theorems A+B give, for every finite β,

> −Λ ≍ N^{−2−2/(β+1)},  with ρ_β − 1 = O(N^{−2/(β+1)}),

confirmed at β = 1, 2, 4 (fitted rates −1.012, −0.710, −0.501 against predicted −1, −2/3, −2/5).
The single open ingredient is a high-probability bound on S (measured median S/N² = 0.120).
β = ∞ (the lattice) is a **singular endpoint**: δ_min = π/N exactly, so the background enters at
leading order and ρ_∞ ≠ 1. Proof document:
[`paper/depth_scaling_theorem.md`](paper/depth_scaling_theorem.md); Lean formalisation of the
deterministic core (uncompiled, two `sorry`s): [`lean/`](lean/); machine verification of all 18
algebraic steps (sympy exact + z3):
[`verification/verify_theorem_steps.py`](verification/verify_theorem_steps.py).

## 4. The CUE/ACUE separation **[one side proved, one side reduced]**

**Theorem C.** (i) **[proved]** Every non-clock ACUE configuration satisfies, deterministically,

> N²(−Λ) ≥ π²/8 = 1.2337005501…

(δ_min = π/N exactly, by pigeonhole, plus Theorem A). (ii) **[reduced]**
P(N²(−Λ^CUE) < π²/8) → 1, from the sine-kernel gap law (P(δ_min > π/N) ≤ e^{−π²N/72}) plus the
open background bound. Measured: the fraction of CUE samples below the ACUE floor is 0.565, 0.823,
0.967, 0.9984, 1.0000, 1.0000 at N = 8…256. **The Alternative Hypothesis ensemble fails not by
fragility but by excess stability** — it satisfies its own RH-analogue too robustly. Since
N²(−Λ) = ρ·π²c²/2 for a hard core of c mean spacings, this yields a falsifiable threshold:

> if the zeta zeros in a window have local depth with liminf N²(−Λ) < π²/8, AH is false,

and the exchange rate μ ≤ √(2μ_Λ)/π against the Lagarias–Rodgers extremum (their published
μ ≤ 0.606894 is exactly the depth bound μ_Λ ≤ 1.8177). Scripts:
[`verification/separation.py`](verification/separation.py),
[`verification/lr_bridge.py`](verification/lr_bridge.py).

## 5. The counterexample constructions **[computed, exact]**

The mimicker fibre — measures matching every balanced moment of degree ≤ N — has exact dimension
**0, 0, 2, 10, 80, 403, 1804** for N = 3…9, and stays frozen along the *entire* heat flow (the flow
is diagonal in the coefficients). Constructions in [`counterexamples/`](counterexamples/):

- **Centre-of-mass family** (`mimicker_fibre.py`): q_g(C) = μ_ACUE(C)·g(Σc mod N) lies in the fibre
  iff E[g] = 1 and ĝ(±1) = 0 — an explicit (N−3)-parameter family of honest probability laws for
  every N ≥ 4, verified to 10⁻¹² at N = 5…8.
- **Parity sectors** (`parity_sectors.py`): q^± = μ(1 ± (−1)^{Σc}) are mutually singular, agree on
  every marginal of ≤ N−1 sites, yet are separated by the depth through the clock atom
  (mass 2^{2−N} in q⁺, exactly 0 in q⁻).
- **Fibre tomography** (`fibre_tomography.py`): over the exact fibre at N = 6, E[N²(−Λ)] ranges over
  [1.3610, 1.4770] and the Λ = −∞ atom can be tripled, with every constrained moment fixed.
- **Exact ACUE enumeration** (`dyn1_core.py`, `dyn1_enum.py`, data in [`data/`](data/)): all 13,132
  rotation orbits for N ≤ 10 with exact Vandermonde masses; P(clock) = 2^{1−N} exactly
  (Cauchy–Binet); in all 13,130 non-clock orbits the first collision is at an initially-adjacent
  pair.

## 6. The structure underneath **[proved + computed]**

The invisibility depth d_N(δ) = δ(N−δ) of a fibre direction is simultaneously: dim_ℂ Gr(δ,N);
the affine Bruhat length ⟨2ρ, ω_δ⟩; N·‖ω_δ‖² (Casimir up to normalisation); and — the new
equality — **the eigenvalue of the Jacobian of the zero dynamics at the clock**
(‖𝓛_N − Jacobian‖ ≤ 2.4·10⁻¹³ for N = 4…24, `verification/operator_unification.py`). Mechanism in
one sentence: *impostors hide in exactly the modes the flow acts on most strongly*, which is why a
stopping time sees what moments cannot. The Nyquist mode carries N²/4 = ⌊N²/4⌋, the pigeonhole
maximal invisibility depth — same number, two derivations. As N → ∞, N^{−1}𝓛_N → (−Δ)^{1/2}: the
natural semigroup of the invisibility hierarchy is the Poisson flow.

Additionally: the marked depth χ(G;u) = ∂_η(−Λ(G+ηuu*)) obeys the parameter-free rank-two law
Dτ[uu*] = (κδ/4)·u*(c_aP_a − c_bP_b)u + (δ²/8)κ′(u) on the first colliding pair (correlation
1.00000000, residual 5.7·10⁻¹¹; blind tomography recovers the critical two-plane to 2·10⁻⁶ degrees)
— it is a polarisation detector, not a resolvent probe.
Scripts: `verification/marked_depth.py`, `verification/marked_depth_law.py`,
`verification/dislocation_constant.py` (the single-dislocation constant
s* = 1.419640342 = 1.150717118 × π²/8, lattice enumeration and continuum double-root equation
agreeing to 6 digits).

---

## Reproducing

All Python scripts run with `python3` + numpy/scipy/sympy (z3-solver for
`verify_theorem_steps.py`); the exact-arithmetic paths use `fractions`/sympy rationals only. The
Lean package builds with `lake update && lake build` under the pinned toolchain (not compiled by
the authors — see [`lean/README.md`](lean/README.md) for why, and for the two `sorry`s that remain).

## Provenance

Produced in a multi-agent Claude Code session; the methodology (agent fleets, adversarial defaults,
exact arithmetic at thresholds, two independent implementations for every headline number, negative
results as first-class products) is described in §9 of the paper. Session:
https://claude.ai/code/session_018CraCE45emdCCdHMfwupxs
