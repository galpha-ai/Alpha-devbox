# R2 / Task F3 — is the diagonal method dead at φ=1/2 for ALL resonator coefficients?

**Status (repaired 2026-09-05, after two independent refutation passes): the trivial "square the
sum" identity `K = (1/2)Φ² − (1/2)[A,A^T]` is exact algebra and now stated **only** in FABLE-native
letters (no creation/annihilation relabelling), which two independent numerical checks confirm to
machine precision — the *original* version of this report used a "physics convention" relabelling
that silently swapped an operator-application order and got the sign of the commutator term wrong;
this is now fixed (§2.2, "Repair note"). The claim that the *truncated* commutator acts as a scalar
`c(v)` on the whole mass-`v` sector is **withdrawn**: an independent refuter, and this repair pass
independently, showed by direct computation that it is false for multi-particle states (§2.3,
"Repair note" — falsified, not merely unproved). The crude Cauchy–Schwarz/number-operator bound is
still shown to fail completely (`‖Φ‖=∞`, proved, not estimated) via a route that does **not** depend
on either fixed error, so that verdict is unaffected. The finite-M truncated-Fock-space numerical
spectrum (M=20..55 now, exact diagonalisation via Lanczos — M=55 added in this repair pass; M=60
attempted, see §4.2) converges cleanly to ≈4.6456, about 6% below the π²/2 threshold and in
striking agreement with GPT-6 Astra's independently-obtained richer symmetric-prime-feature
optimum; this numerical part was **not** affected by the algebra errors (it is a direct
diagonalisation of the literal `K=A^T A+(A²+(A^T)²)/2` matrix, independently reproduced by a second
refuter to ~1e-12). Nothing here is a proof of a "wall" theorem, and nothing here is a theorem about
zeta zeros: this is a spectral question about one idealised continuum operator, and its relation to
the actual arithmetic operator on `n ≤ L` is itself an open arithmetic-transfer question (the
same kind of gap flagged throughout F1/F2).**

Written 2026-09-05 by Fable (Claude Code), task R2/F3, Astra's own §12 recommendation
("First investigate a uniform upper [bound] or a counterexample for the full arithmetic operator
… including its commutator structure and the shape of finite Perron vectors."). Input git commit:
`89393d5da61a45561ed199330c5b836f47fcd629`. Session note: this Claude session already hit its own
usage limit once tonight, so this report favours a clean, checkable finite computation over an
open-ended analytic search.

Primary source: one attempt at `WebFetch https://arxiv.org/html/2604.05733v1` was made for this
task; **the fetch tool is not available to this subagent invocation** (no network egress tool was
offered), so no attempt could actually be made. Every statement about Inoue's Theorems 2 and 4
below is **"(as described by Astra; paper not read)"**, propagated unchanged from
`astra_inputs/research/reports/residual_gram_round1.md` and
`astra_tasks/task001_F2_finite_sum_diagnostic.md`. All other citations are marked
"(recalled; not verified online)".

Result labels: **[exact algebra]** (standard, cited facts about bosonic Fock spaces are used but
not re-derived from measure theory), **[certified continuum integral]** (reused from Astra/F2,
not re-certified here), **[finite numerical check]**, **[open]**.

Scripts: `astra_tasks/task001/f3_fock_spectrum.py` (self-contained; nothing imported from
`astra_inputs/`, though conventions for `A`, `A^T`, `K` follow `f2_finite_sum.py` exactly so the
two are directly comparable). Results: `astra_tasks/task001/f3_fock_spectrum_results.json`,
log `astra_tasks/task001/f3_fock_spectrum_run.log`. **Added in this repair pass:**
`astra_tasks/task001/check_f3_repair.py` (independent verification of the corrected F3-1 identity
and of the falsification of the `c(v)`-scalar claim; imports `build_operators`/
`enumerate_partitions` from `f3_fock_spectrum.py`, no other dependency), log
`astra_tasks/task001/check_f3_repair_run.log`.

---

## 0. Summary

1. **[exact algebra] Fock-space formulation (repaired).** With `A` the FABLE-convention creation
   operator for test function `g(u)=2 sin(πu/2)` and `A^T` its adjoint (annihilation) on the
   truncated bosonic Fock space over `H=L²((0,1),du/u)` (mass ≤ 1), `Φ=A+A^T`, the identity
   `K = A^T A + (A²+(A^T)²)/2 = (1/2)Φ² − (1/2)[A,A^T]` (with `[A,A^T]:=AA^T−A^TA`, ordinary
   operator commutator, **FABLE letters throughout, no creation/annihilation relabelling**) is a
   *pure algebraic identity* — it is just the expansion of `(A+A^T)²`, true for any two operators,
   no CCR needed — and it holds independent of truncation. **Repair note:** the original version of
   this report derived the identity in the opposite ("physics", `A`=annihilate/`A*`=create)
   convention and then asserted the FABLE/physics relabelling was "purely cosmetic"; a refuter
   showed by direct numerical construction that the relabelling silently also swaps which operator
   in a two-letter product is applied first, which flips the sign of the commutator correction —
   confirmed independently here (§2.2). The FABLE-native identity above is correct and verified to
   machine precision (`4e-16`) at M=6,8,10 in this repair pass. On a state of fixed background mass
   `v`, the *untruncated* commutator `[A(g),A(g)^T]=−C_g·Id` is an honest state-independent
   constant (`C_g=⟨g,g⟩_H`); the report's original further claim — that the *truncated* commutator
   restricted to the mass-`v` sector still acts as a single scalar `c(v):=∫₀^{1−v}g(u)²du/u·Id` on
   *all* states of that mass, including multi-particle ones — is **withdrawn**: it is false, refuted
   by direct computation of the discretised commutator matrix (§2.3, "Repair note"; independently
   confirmed here at M=6,8,10, diagonal spread up to ~13× the mean within a single mass-8 sector at
   M=10). The formula matches the task's stipulation only in the single-insertion/leading sense
   described in §2.3, not as a general operator identity on the mass-`v` subspace.
2. **[exact algebra + certified continuum integral] Trial check.** The fixed rational trial's
   quadratic form, expressed in this Fock language, is literally the decomposition already
   computed in F2 §6 (D+O+C2, matching M3/I+M2b/I+M2a/I): `⟨Ψ,KΨ⟩/⟨Ψ,Ψ⟩ = 2π²(J+1/4)` with
   `J = −0.014662375473371` (F2's independently-quadratured value; Astra's certified enclosure
   `[−0.014662375473368995,−0.014662375473368974]`). No new computation was needed; this is a
   restatement, and the identity `⟨x,Kx⟩/⟨x,x⟩ = 2π²(J+1/4)` is the *same* algebraic fact already
   checked at finite L in F2 (`lambda_rayleigh` field).
3. **[exact algebra] The crude bound fails completely, not just numerically.** The natural
   Cauchy–Schwarz/number-operator bound `‖A*Ψₙ‖² ≤ (n+1)‖g‖²_H ‖Ψₙ‖²` (§3) requires bounding the
   particle-number operator N uniformly, but N is **unbounded** on the mass-≤1-truncated Fock
   space: for every n there is a valid n-particle state (n equal masses of size `1/(2n)`, total
   mass `1/2 ≤ 1`). Hence the crude bound gives `‖Φ‖ = ∞`: it produces **no finite bound at all**,
   let alone `≤ π²/2`. This is proved, not estimated. **This particular verdict does not depend on
   the sign/scalar errors in item 1 above** — it follows directly from the pure algebraic identity
   (which holds regardless of sign conventions) plus the exhibited unbounded family of states, with
   no need for the (now-withdrawn) claim that the commutator correction is a pointwise-nonpositive
   scalar (§3.1 is rewritten in this repair pass to make this explicit and remove the dependence).
4. **[finite numerical check] The true spectrum is nonetheless small and converges cleanly.**
   Discretising `u ∈ {1/M,...,1}` (task's own prescription: configurations = integer partitions of
   `m ≤ M`, a standard truncated multi-mode bosonic Fock space), exact Lanczos diagonalisation of
   K gives `λ_max(K)` = 4.61313 (M=20), 4.61934 (25), 4.62357 (30), 4.62662 (35), 4.62894 (40),
   4.63075 (45), 4.63221 (50), **4.63340 (55, new in this repair pass)** — monotone increasing,
   differences shrinking roughly like `1/M`. Three-point `1/M + 1/M²` fits on the last few windows
   are extremely stable: `λ_∞` = 4.645728 (20,25,30), 4.645624 (30,35,40), 4.645599 (35,40,45),
   4.645583 (40,45,50), **4.645572** (45,50,55); a global power-law fit `λ_∞ − c/M^p` over all 8
   points gives `λ_∞ = 4.64645`, `p = 0.928`. **The crude bound in item 3 is a real but hugely
   non-tight bound: the true operator norm on this idealised truncated space appears finite and
   well below π²/2.**
5. **[finite numerical check] Independent cross-match with Astra's richer family.** Converting
   Astra's exploratory richer-family continuum margins to the same `λ=2π²(J+1/4)` scale gives
   4.645390 (S2, degree 4), 4.645498 (S2,S3, degree 4), 4.645522 (S2,S3,S4, degree 4),
   **4.645530** (12-group richer family) — all *below* and converging toward our unrestricted-Fock
   extrapolation (4.6456–4.6465), exactly the ordering required since Astra's polynomial families
   are subspaces of the full Fock space and their sup can only be ≤ the global sup. The two
   numbers agree to 3–4 significant figures despite being computed by completely different methods
   (Astra: ill-conditioned generalized eigenproblem over specific symmetric-feature polynomials in
   `v,S2,S3,S4`; here: exact Lanczos on a first-principles truncated bosonic Fock space with no
   `ell`/`H` parametrisation at all). This is evidence — not proof — that Astra's degree-4
   polynomial family has already nearly saturated the sup over ALL symmetric-prime-factor
   resonators, in the idealised continuum model.
6. **[open] Threshold comparison and its caveats.** `4.6456 < π²/2 = 4.9348` by about 0.29
   (5.9%), i.e. the idealised continuum sup over arbitrary resonators does *not* cross the
   threshold — consistent with a "wall" for this operator, in this idealised model. But: (i) this
   is a numerical extrapolation of a genuine limit, not a proved bound (item 3's only *proved*
   statement is that the crude method gives no bound at all); (ii) whether `M → ∞` of this
   discretised Fock space is really the correct continuum limit of the actual finite-L arithmetic
   operator (primes only, no coincidences, `L→∞`) is itself an unproved "arithmetic transfer"
   question of exactly the type flagged as open in F1/F2 (Mertens-type prime density vs. the
   idealised `du/u` measure, prime powers, `p|m` coincidences — all *dropped* in this idealised
   Fock model); (iii) Astra's actual FINITE-L arbitrary-coefficient search (`arithmetic_operator.py`,
   λ_max(K_L) = 3.9493, 4.1059, 4.2053, 4.2739 for L=10³…10⁶) is still far below both 4.646 and
   π²/2 and its own L→∞ limit is not established (the same slow, unproved `1/log L`-type drift
   documented in F2 §5, not the much cleaner `1/M` drift found here in the idealised model).

---

## 1. Setup (recap, to fix notation for this report)

φ=1/2, ℓ=16/15, a=ℓ². `d_ℓ(pᵉ)=ℓ(ℓ+1)…(ℓ+e−1)/e!`. `v=log n/log L`, `S2(n)=Σ_{p|n}(log p/log L)²`
over distinct primes. `r(n)=d_ℓ(n)H(v,S2(n))`, `x_n=r(n)/√n`. Finite operator (F2/Astra
convention, at `log L/log T=1`): `A[qm,m]=2 sin((π/2) log q/log L)/(e√q)` for `q=pᵉ≤L`, `qm≤L`;
`K_L=A^T A+(A²+(A^T)²)/2`; threshold `π²/2=4.9348022`. `J_L=⟨x,K_L x⟩/(2π²⟨x,x⟩)−1/4`.

Astra's finite arbitrary-coefficient search (`arithmetic_operator.py`, reproduced in F2 §2 to 10
digits): `λ_max(K_L)` = 3.9492871367 (L=10³), 4.1058670454 (10⁴), 4.2052553801 (10⁵),
**4.2738969159 (10⁶, from `residual_gram_round1.md` §7)**.

---

## 2. Part (a): the continuum Fock-space limit

### 2.1 The prime measure (what's proved vs. heuristic)

For a fixed profile `f`, Mertens' theorem / PNT give `Σ_{p≤x} f(log p/log x)/p → ∫₀¹ f(u) du/u` as
`x→∞` **[recalled; the F2 report §5 already used and empirically confirmed the rate — its
"prime-sum discretisation" table shows the ratio converging to 1 like `1+c/log L` with `c` of
order 1]**. More generally, for symmetric functions of `k` distinct prime factors,

  `Σ_{n} F(prime factors of n) d_ℓ(n)²/n  ~  Σ_k (1/k!) ∫_{Σuᵢ≤1} F(u₁,...,u_k) ℓ^{2k} ∏ du_i/u_i`

is the content of F2 §7's exact marked-Euler-product identity plus the (recalled) Selberg–Delange
theorem, there proved at the level of *moments* of `S2` only (not the full joint law); the general
statement for arbitrary symmetric `F` is the Poisson–Dirichlet(a) limit law stated without proof
in `residual_gram_round1.md` §8 (formulas PF2/PF3), there labelled "coherent continuum
calculation," not an arithmetic theorem. **This report does not attempt to re-derive PF2/PF3; it
takes the stipulated `ℓ^{2k} ∏du_i/u_i` measure as given (as F2 and the FABLE task both do) and
asks only about the operator built on top of it.**

Crucially, the **operator** `A` itself carries **no** `ℓ` dependence (`A[qm,m]` has no `d_ℓ`
factor) — only the *trial vector* `x_n` does. So the "sup over arbitrary resonator coefficients"
question is a question about the operator `K` alone, acting on the bare `du/u`-measure Fock space
(rate 1 per unit `du/u`, no `a=ℓ²` factor), independent of any choice of `ℓ` or `H`. This is what
Astra's `arithmetic_operator.py` computes at finite `L` (unconstrained Perron eigenvector search),
and it is what is modelled below.

### 2.2 Creation operator and the K-identity **[exact algebra — repaired]**

**Repair note (issue found by an independent refuter, confirmed independently here):** the
original version of this section stated the identity using the opposite, "physics" convention
(`A`=annihilate, `A*`=create) and then claimed in a closing paragraph that relabelling
`FABLE_A↔physics_A*`, `FABLE_A^T↔physics_A` was "purely cosmetic." It is not: FABLE's literal
product `A^T A` means "apply `A` (create), then `A^T` (annihilate)"; under the stated relabelling
this is the physics product `A·A*` ("apply `A*`, then `A`"), **not** `A*·A` — the relabelling also
silently reverses which letter is applied first, and `A·A* = A*·A + [A,A*]` differ by the whole
commutator. The refuter verified this by building the discretised operators from
`f3_fock_spectrum.py`'s own `build_operators()` and comparing matrices entrywise (M=6: the
correctly-signed FABLE-native identity matches to `4.4e-16`, while the report's own
physics-convention `K` differs from the real `K_L` by `3.60`, not a rounding error). **Independently
reproduced in this repair pass** at M=6,8,10 (max entrywise error `2.2e-16`–`4.4e-16` for the
corrected identity below; see `check_f3_repair.py`, §2.3 for citation). Fix: state everything in
FABLE-native letters, with no relabelling step at all.

Let `H = L²((0,1), du/u)`, `Γ(H) = ⊕_k Sym^k(H)` the truncated bosonic Fock space (mass ≤ 1). Let
`A=A(g)` be the FABLE-convention creation operator for `g∈H` and `A^T=A(g)^†` its adjoint
(annihilation), `Φ=A+A^T`. Define the *ordinary operator commutator* `[A,A^T] := A A^T − A^T A`
(no convention choice here — this is just notation for the number `AA^T Ψ − A^T A Ψ`). Then,
**purely by expanding the square** (true for *any* two operators, no CCR needed yet):

  `Φ² = (A+A^T)² = A² + (A^T)² + A A^T + A^T A = A² + (A^T)² + 2 A^T A + [A,A^T]`
  ⟹ `K := A^T A + (A²+(A^T)²)/2 = (1/2)Φ² − (1/2)[A,A^T]`.   **(★)**

(★) is the FABLE-native form of the identity the task asked for and it is literally what the task
and `f2_finite_sum.py`/`f3_fock_spectrum.py` call `K`, with no relabelling anywhere. It holds
independent of truncation, and was checked to hold at machine precision (`≤4.4e-16`) against the
discretised `Acre`/`Aann` matrices for M=6,8,10 in this repair pass.

On the **untruncated** space, the canonical commutation relation
**[recalled; standard second-quantisation fact, e.g. Reed–Simon Vol. II §X.7 or any QFT Fock-space
reference]** gives `[A(g)^T, A(g)] = ⟨g,g⟩_H·Id` (annihilation-then-creation convention, the
positive/standard direction), i.e. `[A,A^T] = A A^T − A^T A = −⟨g,g⟩_H·Id = −C_g·Id`, a genuine
state-*independent* scalar, `C_g=∫₀¹g(u)²du/u=3.29656` **[value computed by quadrature,
`scipy.integrate.quad`, error 3.7e-14]**. Substituting into (★):

  `K = (1/2)Φ² + (1/2)C_g`   (untruncated space; note the **`+`** sign, not the `−` sign the
  original version of this report used — the sign flip is exactly the relabelling bug above:
  `[A,A^T]_{FABLE} = −[A,A^T]_{physics}`).

As shown in §3, this sign does not actually change the bottom-line verdict of Part (b) (item 3 of
the Summary), because the crude bound already fails to produce *any* finite number regardless of
the sign of an O(1) additive correction — but it does mean §3.1 of the original report (which used
the wrong sign to argue `K ≤ (1/2)Φ²` "pointwise") was invalid as written; §3.1 below is rewritten
to avoid depending on the sign of this correction at all.

### 2.3 The truncated commutator: `c(v)` is **not** a scalar on multi-particle states **[falsified — repaired]**

**Repair note.** The original derivation below is kept for the record because it is the natural
first attempt and shows exactly where it breaks, but its **conclusion is wrong** as an operator
identity on the whole mass-`v` sector, for multi-particle states. This was flagged by an
independent refuter and **confirmed independently in this repair pass** by direct computation of
the discretised commutator matrix `A_cre A_cre^T − A_cre^T A_cre` (using `f3_fock_spectrum.py`'s
own `build_operators()`) at M=6, 8, 10: restricted to a fixed-total-mass sector, the diagonal is
constant (spread `=0`, to machine precision) only for the *smallest* masses in each M (partitions
dominated by few, large parts), but for masses closer to the truncation edge the spread is a
large fraction of, or even several times, the mean — e.g. at M=10, mass-8 sector (22 states):
mean `≈0.053`, spread `≈0.691` (spread/|mean| ≈ 13); at M=8, mass-6 sector (11 states): mean
`≈−0.103`, spread `≈0.823` (spread/|mean| ≈ 8). Different partition *shapes* of the same total
mass genuinely give different commutator eigenvalues — the claim that they don't is false, not
merely unproved.

**Original (flawed) derivation, and where it breaks.** Impose the mass cutoff: let `Π` project onto
configs of total mass ≤ 1, and work with `A_trunc=ΠA(g)Π`, `A^T_trunc=(A_trunc)^†=ΠA(g)^TΠ`. On a
state `Ψ` of **total mass exactly `v`**, `A(g)Ψ` only *decreases* mass so `A_trunc Ψ = A(g)Ψ`
exactly; and *if* `Ψ` is such that all of `A(g)^T Ψ`'s support has mass exactly `v` too before any
truncation (true for a one-particle `Ψ`, since there is only one way to "add back" the single
part removed), the creation side needs cutting off beyond `1−v`, giving `A^T_trunc = A(g_v)^T`,
`g_v(u):=g(u)·1_{u≤1−v}`, and `[A_trunc,A^T_trunc]Ψ = ⟨g,g_v⟩_H Ψ = c(v)Ψ`,
`c(v):=∫₀^{1−v}g(u)²du/u`. **This step is where the general claim breaks**: for a genuine
multi-particle `Ψ` of mass `v`, the *other* term of the commutator, `A^T_trunc A_trunc Ψ`, first
removes one part of some mass `w<v` (landing on a state of mass `v−w`, a different value for each
part removed), and *then* the creation-side cutoff that actually applies is `1−(v−w)`, which
depends on `w` — not simply `1−v`. Averaging over which part gets removed first (weighted by the
occupation numbers and `g`) does not, in general, collapse back to the single number `c(v)`; hence
the operator `[A_trunc,A^T_trunc]` is genuinely non-scalar on the multi-particle part of the
mass-`v` sector, as the numbers above show.

**What survives:** `c(v)=∫₀^{1−v}g(u)²du/u` is the exact value of `⟨Ψ,[A_trunc,A^T_trunc]Ψ⟩/‖Ψ‖²`
on a **one-particle** state of mass `v` (a single mode at `u=v`), and it is the exact
state-independent constant `−C_g` on the fully **untruncated** space (§2.2). Beyond that, it is at
most a plausible leading-order/mean-field estimate, not an operator identity; no corrected general
formula for the multi-particle commutator was derived in the time available (open, see §5). `c(v)`
remains manifestly non-increasing in `v` on the one-particle sector: `c(0)=C_g=3.29656`, `c(1)=0`.
This withdrawal does **not** change §4's numerics (F3-4/5/6), which diagonalise the literal `K`
matrix directly and never used `c(v)` as an intermediate step; it does invalidate §3.1 of the
original report, which is rewritten below (§3.1) to avoid relying on `c(v)` being a scalar or
having any particular sign.

### 2.4 Trial-vector check

The task asks to verify the fixed trial gives `2π²(J+1/4)` for the quadratic form. This is not a
new computation: F2 §1/§6 already defines, for the *finite* operator, `lambda_rayleigh =
2π²(J_L+1/4) = ⟨x,K_L x⟩/⟨x,x⟩` by direct algebraic expansion of `K_L=A^T A+(A²+(A^T)²)/2`
(**[exact algebra]**, F2 §1), and separately defines the *continuum* `J = M/I − 1/4` where `I` is
the norm and `M2a/I, M2b/I, M3/I` are, in the Fock language above, exactly `⟨Ψ,A²Ψ⟩/⟨Ψ,Ψ⟩`,
the off-diagonal part of `⟨Ψ,A*AΨ⟩/⟨Ψ,Ψ⟩`, and the diagonal part, respectively, for the coherent
trial state `Ψ` built from `H(v,S2)` (F2 §1's "Decomposition" paragraph, and the piece table in F2
§6 comparing `D,O,C2` to `M3/I,M2b/I,M2a/I`). So `⟨Ψ,KΨ⟩/⟨Ψ,Ψ⟩ = 2π²(M/I) = 2π²(J+1/4)` is the
*definition* of `M,I` transcribed into this operator language, already numerically confirmed in F2
§3 (`J=−0.014662375473371` vs. Astra's certified `[−0.014662375473368995,−0.014662375473368974]`,
agreement 1.6e-15) and in F2 §2 at finite L. No further check was run here; re-deriving it would
duplicate F2 exactly.

---

## 3. Part (b): does a crude bound give `λ_max(K) ≤ π²/2`?

### 3.1 The intended bound **[rewritten in this repair pass — see note]**

**Repair note.** The original §3.1 argued `K ≤ (1/2)Φ²` "pointwise" from `−(1/2)[A,A*]` being a
non-positive *multiplication operator*, using both (i) the wrong sign for the commutator
correction (§2.2 — the correctly-signed correction is `+(1/2)C_g` on the untruncated space, not
`−(1/2)c(v)`) and (ii) the now-withdrawn claim that the truncated commutator is a scalar
multiplication operator at all on multi-particle states (§2.3). Both defects are real, but neither
one is needed for, nor changes, the actual bottom-line verdict of Part (b): the crude method fails
regardless, for the more elementary reason given below.

By (★) (§2.2, a pure algebraic identity, no sign or scalar assumption involved),
`⟨Ψ,KΨ⟩ = (1/2)‖ΦΨ‖² − (1/2)⟨Ψ,[A,A^T]Ψ⟩` for *any* state `Ψ`. If one tries to bound
`λ_max(K)` via a bound on `‖Φ‖_op` alone (the natural "crude" route, and the one the task asks
about), the *only* way this can work is if `‖Φ‖_op` is itself finite — at which point the sign and
exact multi-particle structure of the correction term become second-order questions to sharpen
the resulting bound. §3.2 below shows `‖Φ‖_op=∞` by the standard Cauchy–Schwarz/number-operator
estimate. **That already ends the crude-bound route with no finite information whatsoever**,
independent of how the (possibly non-scalar, possibly either sign) correction term behaves — so
the sign error and the scalar-claim error in the original §2.3/§3.1, while real defects in the
supporting derivation, do not change the Part (b) verdict itself (Summary item 3). No corrected
"pointwise operator inequality" of the kind originally attempted is asserted here; whether one
exists (using the correct, non-scalar commutator structure) is left open alongside the rest of
§3.3/§5.

### 3.2 The standard Cauchy–Schwarz/number-operator bound, and why it fails **[exact algebra]**

The standard bosonic estimate (Nelson-type `N`-bound; **[recalled]**, standard second-quantisation
fact) is: on the `n`-particle sector, `‖A(g)*Ψₙ‖² ≤ (n+1)‖g‖²_H‖Ψₙ‖²`, so `Φ(g)` restricted to
particle number `≤ n_max` has operator norm `≤ √(2(n_max+1))‖g‖_H`. This is exactly the intended
"Cauchy–Schwarz/Hardy-type" bound.

**The catch: the particle-number operator `N` is unbounded on the mass-≤1-truncated Fock space.**
For every `n≥1`, the symmetric `n`-particle state with all masses equal to `u=1/(2n)` has total
mass `n·(1/(2n))=1/2 ≤ 1`: it is a legitimate, normalisable state in the truncated space for every
`n`. So `sup{n : an n-particle state satisfies the mass≤1 truncation} = ∞`, and the bound
`√(2(n_max+1))‖g‖_H` is `+∞`. **The crude bound therefore gives no information whatsoever** — not
merely a bound worse than `π²/2`, but literally `λ_max(K) ≤ ∞`. This is a clean, provable negative
statement, not a numerical estimate: mass-truncation alone does not control particle number, so the
generic `N`-bound is vacuous here.

### 3.3 Why the crude bound is not tight, and where the real control comes from

The `N`-bound is loose because it ignores that `g(u)→0` (linearly) as `u→0`: a *single* mode at
location `u=ε`, truncated to occupation number `≤ 1/ε` (all budget spent on that one mode), has a
standard truncated-harmonic-oscillator-type top eigenvalue of size `~ g(ε)·√(1/ε) ~ ε/√ε = √ε → 0`
as `ε→0` — i.e. **individual very-small-mass modes contribute a *vanishing*, not diverging,
maximal eigenvalue**, exactly the opposite of what the raw `N`-bound (which ignores the
`u`-dependence of `g`) suggests. So the true obstruction to a finite bound is not "many small
modes" one at a time, but whether *combining* arbitrarily many of them (a genuine multi-mode/
entangled Perron vector, exactly the kind of vector Astra's finite-L Perron search explores) can
still build up an unbounded Rayleigh quotient. **This report did not find a rigorous multi-mode
Hardy-type inequality settling that question in the time available; it is left open (§5).** What
*is* established, numerically and with a growing base of cross-checks (§4), is that the true
answer for this specific `g` looks like convergence to a finite value comfortably below `π²/2`,
not divergence — but the analytic proof of that (as opposed to the numerical evidence) remains to
be done.

**Verdict for (b), stated precisely: the crude bound fails completely (gives `∞`, not merely a
bound in excess of `π²/2`); it does *not* establish a no-go for the whole diagonal method, and it
does *not* refute one either.**

---

## 4. Part (c): numerics — truncated bosonic Fock space, exact diagonalisation

### 4.1 Discretisation

Following the task's own prescription: `u ∈ {1/M, 2/M, …, 1}`; a configuration is an integer
partition of some `m ≤ M` (parts `j∈{1,…,M}`, `Σj≤M`, repeats allowed — bosonic, matching that
many primes can share a coarse-grained log-scale bin). This is exactly `M` independent bosonic
modes, mode `j` costing mass `j/M`, standard ladder operators `a_j,a_j^†` (`[a_j,a_k^†]=δ_{jk}`),
truncated to total occupied mass ≤ `M` (i.e. states = partitions of `0,1,…,M`; dimension =
`Σ_{m=0}^M p(m)`, e.g. 215,308 for M=40, 1,295,971 for M=50).

**Normalisation (the one nontrivial modelling choice, checked and fixed by a failed first
attempt):** an orthonormal basis function for the bin `[  (j-1)/M, j/M ]` of `H=L²((0,1),du/u)` has
height `≈√j` there (since `∫_{bin} du/u ≈ (1/M)/(j/M) = 1/j`), so its overlap with the
(unnormalised) test function `g` is `⟨φ_j,g⟩_H ≈ g(j/M)/√j` — an extra `1/√j` beyond `g` itself,
matching the finite operator's `1/√q` factor exactly (`w_q=2sin(...)/√q`, not `2sin(...)`). Using
`g(j/M)` alone (no `1/√j`) was tried first and gives `λ_max(K)=12.66` (M=5), `23.17` (M=10) —
diverging fast, an obviously wrong/unnormalised model; the corrected `g(j/M)/√j` weight gives the
converged, sensible results below. Creation operator `Acre = Σ_j [g(j/M)/√j] a_j^†`, annihilation
`Aann=Acre^T`, `K=Aann·Acre+(Acre²+Aann²)/2` (identical formula and naming to `f2_finite_sum.py`).

### 4.2 Results (`f3_fock_spectrum.py`, exact Lanczos via `scipy.sparse.linalg.eigsh`)

**Repair note (provenance gap fixed):** a refuter found that the M=55/60 rows quoted in the
original table were not present in the cited `f3_fock_spectrum_results.json`/`_run.log` (both
stopped at M=50) — a real reproducibility gap, since those numbers came from an untracked
exploratory run. Fixed in this repair pass: `f3_fock_spectrum.py --Ms 20,25,30,35,40,45,50,55,60`
was re-run in full and both files now contain every row below, M=55 included with its own
`λ_max` (its resident memory, 3,542 MB, came in just under the script's 4,000 MB `eigsh` cutoff,
so unlike in the original exploratory run it was **not** skipped this time — a genuine bonus data
point for the extrapolation in §4.3). M=60 still exceeds the memory cutoff and `eigsh` is skipped
for it, exactly as before, and its `dim`/`nnz` match the originally-quoted values exactly.

| M | dim | nnz(Acre) | λ_max(K) | residual | time (s) | max RSS |
|---:|---:|---:|---:|---:|---:|---:|
| 20 | 2,714 | 8,266 | 4.6131253541 | 1.9e-14 | 0.0 | 62 MB |
| 25 | 9,296 | 32,095 | 4.6193379711 | 4.9e-12 | 0.1 | 69 MB |
| 30 | 28,629 | 109,350 | 4.6235652483 | 1.8e-10 | 0.2 | 88 MB |
| 35 | 81,156 | 337,506 | 4.6266239556 | 2.7e-12 | 0.8 | 148 MB |
| 40 | 215,308 | 963,320 | 4.6289382253 | 3.9e-11 | 2.5 | 293 MB |
| 45 | 540,635 | 2,579,411 | 4.6307496033 | 1.4e-12 | 9.8 | 647 MB |
| 50 | 1,295,971 | 6,547,151 | 4.6322055576 | 5.9e-12 | 26.5 | 1,542 MB |
| 55 | 2,984,865 | 15,877,562 | **4.6334011377** | 3.5e-11 | 67.7 | 3,542 MB |
| 60 | 6,639,349 | 37,013,901 | — (matrix built; eigsh skipped, 4.0 GB memory limit) | | | 7,910 MB |

All operators are entrywise non-negative (Perron–Frobenius applies, top eigenvector non-negative;
`min_signed_entry` in the JSON confirms this at every M run). Total wall time for M≤55: under 2.5
minutes; M=60 was attempted only to see where the ~4GB guidance bites and was stopped there, per
the task's own instruction ("stop if memory exceeds ~4GB").

### 4.3 Extrapolation vs. π²/2 and vs. 4.646

Differences shrink monotonically (0.00621, 0.00423, 0.00306, 0.00231, 0.00181, 0.00146, 0.00120 for
successive `ΔM=5` steps, the last using the new M=55 point) with slowly increasing ratio
(0.680→0.821), consistent with a leading `1/M` term (not exponential decay). Fits (now using all 8
points, M=20..55):

* **Three-point `λ = λ_∞ + c₁/M + c₂/M²`** (exact on 3 points, most informative near the edge):
  `(20,25,30)→4.645728`, `(30,35,40)→4.645624`, `(35,40,45)→4.645599`, `(40,45,50)→4.645583`,
  **`(45,50,55)→4.645572`** — monotone, shrinking corrections, evidently converging to ≈4.6456.
* **Global power-law fit** `λ_∞ − c/M^p` over all 8 points: `λ_∞=4.646446`, `c=0.53719`,
  `p=0.9280` (residuals ≤1.4e-5), consistent with a leading `1/M` term (`p≈1`) plus a slower
  correction.
* **Linear fit in `1/M`** (all 8 points): `λ_∞=4.644920`, residuals up to 1.1e-4 (worse than the
  3-point/power-law fits, as expected if there is a genuine `1/M²`-type correction).

**Best estimate: `λ_∞ ≈ 4.6456 ± 0.0010`** (the spread between the three extrapolation methods,
essentially unchanged by adding the M=55 point — the extra data point tightens confidence in the
limit without moving it). This is **6.0% below** `π²/2 = 4.9348022`.

### 4.4 Cross-check against Astra's richer symmetric-prime family

Converting Astra's `residual_gram_round1.md` §8 table (continuum margins for symmetric-feature
families) to the same `λ=2π²(J+1/4)` scale:

| family (Astra, `residual_gram_round1.md` §8) | J | λ = 2π²(J+1/4) |
|---|---:|---:|
| 1 only, degree 6 (= Inoue-style, no prime features) | −0.0153579822 | 4.631648 |
| 1, S2, degree 4 | −0.0146618161 | 4.645390 |
| 1, S2, S3, degree 4 | −0.0146563150 | 4.645498 |
| 1, S2, S3, S4, degree 4 | −0.0146551195 | 4.645522 |
| 12 groups incl. S2², S2·S3, S2³, S2⁴, degree 4 | −0.0146547256 | **4.645530** |
| this task's fixed rational trial (F2 §3) | −0.014662375473… | 4.645379 |

Every one of these restricted-family values is **below** the M→∞ Fock extrapolation (4.6456), as
it must be (they are optimisations over specific finite-dimensional subspaces of the full Fock
space, so their sup is ≤ the global sup computed here), and the gap shrinks monotonically as
Astra's family is enriched (4.645390 → 4.645498 → 4.645522 → 4.645530), landing within **0.0001**
of this report's independent 3-point extrapolation and within **0.0010** of the power-law fit.
Two structurally unrelated calculations — Astra's ill-conditioned generalized eigenproblem over
explicit polynomial features in `(v,S2,S3,S4)`, and this report's exact Lanczos diagonalisation of
a first-principles truncated bosonic Fock space with no `H`/`ℓ` parametrisation at all — agree to
3–4 significant figures. This is strong (not conclusive) evidence that (i) the M→∞ limit computed
here is the correct sup of the idealised continuum operator, and (ii) Astra's degree-4
polynomial family has already nearly saturated that sup: richer symmetric-prime features are very
unlikely to buy much more margin in this idealised model.

---

## 5. Part (d): verdict

**What is established (this report, after repair):**

* **[exact algebra]** `K=(1/2)Φ²−(1/2)[A,A^T]` on the mass-truncated bosonic Fock space over
  `H=L²((0,1),du/u)`, `g(u)=2sin(πu/2)`, **in FABLE-native letters with no relabelling** — a pure
  algebraic identity, verified to machine precision against the discretised operators. On the
  *untruncated* space `[A,A^T]=−C_g·Id` is an honest scalar (`C_g=3.29656`). The claim that the
  *truncated* commutator is still a scalar `c(v)=∫₀^{1−v}g²du/u` on the whole mass-`v` sector is
  **false** for multi-particle states (falsified by direct computation, §2.3) and is withdrawn; it
  survives only as an exact fact about the one-particle sector.
* **[exact algebra]** The naive Cauchy–Schwarz/number-operator bound on `‖Φ‖` is *literally
  infinite* on this space — mass truncation does not bound particle number, so this standard tool
  gives zero information, in either direction, about whether `λ_max(K) ≤ π²/2`. This conclusion
  does not depend on the two corrections above (§3.1).
* **[finite numerical check]** The *actual* spectrum of a finite-mode-count (`M≤55`) truncation of
  this Fock space converges cleanly (stable multi-point extrapolations agreeing to 4 significant
  figures) to `λ_∞ ≈ 4.6456`, about 6% *below* `π²/2=4.9348`, and matches — to a precision beyond
  what either calculation individually would inspire much confidence in — Astra's independently
  obtained richer-family continuum optimum (4.645530). This numerical result was **not** affected
  by the algebra corrections above (it diagonalises the literal `K` matrix directly) and was
  independently reproduced to ~1e-12 by a second refuter.

**Precise statement of the "wall conjecture" these numbers support (not proved):**

> *In the idealised continuum model of §2.1 (bare Mertens/`du/u` prime density, no coincidences,
> no prime powers `e≥2`, arbitrary symmetric resonator coefficients built from prime factor
> log-sizes), the supremum over ALL such resonators of the half-gap margin at `φ=1/2` is a finite
> number near `2π²·(−0.0146)−1/4·2π² ≈ 4.6456` (equivalently `J_∞≈−0.01465`), strictly less than
> the threshold `π²/2`. If true, this is a genuine "wall": no resonator built from symmetric
> functions of prime-factor sizes alone can cross `φ=1/2` via this diagonal method, in this
> idealised continuum picture — extending the negative conclusion beyond Astra's specific
> polynomial families to essentially every resonator of this type.*

**What is explicitly NOT established, and is open:**

1. A rigorous finite (let alone `≤π²/2`) analytic bound on `‖Φ‖` or `λ_max(K)` — the only rigorous
   statement in this direction (§3) is that the standard tool gives no bound. The `M→∞` numerics
   are a strong extrapolation of a smooth, apparently-convergent sequence, not a proof of the
   limit or of any explicit rate. A genuine Hardy-type multi-mode inequality exploiting
   `g(u)=O(u)` near `u=0`, tight enough to reproduce ≈4.646 analytically, was not found in the time
   available.
2. **The arithmetic transfer.** This entire §2–4 analysis is of the *idealised continuum* operator
   (bare `du/u` measure with no `ℓ`/`a` weighting, no prime powers, no `p|m` coincidences, and — a
   further idealisation beyond even Astra's continuum schema — the Poissonised limit of the
   Mertens sum itself, `M→∞` inside an already-idealised `L→∞` picture). Whether
   `limsup_L λ_max(K_L)` for the **actual finite arithmetic operator** (all prime powers, all `m`,
   real primes not Poissonised) has the *same* limit ≈4.646, or something larger (finite or
   infinite), is not decided here. F2 §6 already showed that the coincidence terms (`e≥2`, `p|m`)
   are 10–20% of the first-order pieces at `L≤10⁷` and decay no faster than `1/log L` — an order-1
   effect at any accessible `L`, exactly parallel to this report's finding that the discretisation
   parameter `M` (here) and `log L` (there) both drive genuinely slow, unproved convergences.
3. Astra's own finite-L arbitrary-coefficient search (`arithmetic_operator.py`) is far from either
   number at accessible `L` (4.2739 at `L=10⁶`, vs. 4.646 and π²/2=4.935): the finite data alone
   cannot distinguish "converges to ≈4.65, safely below π²/2" from "converges to something
   between 4.65 and π²/2" from "diverges very slowly past π²/2" using only `L≤10⁶` — exactly the
   caveat F2 §5 already raised about extrapolating a handful of points on a slowly-varying
   function. Nothing here changes that.
4. **(New, added in this repair pass) The exact multi-particle structure of the truncated
   commutator `[A_trunc,A^T_trunc]`.** §2.3's `c(v)` formula is confirmed false as a scalar
   operator identity on general (multi-particle) states of the mass-`v` sector — only its
   one-particle-sector and untruncated-space special cases are established. A corrected general
   formula (e.g. as an honest operator, or at least an operator-norm bound on the discrepancy) was
   not derived in the time available. This does not affect §4's numerics (which never used `c(v)`
   as an intermediate step) but leaves open any future attempt to build a rigorous bound via the
   `(1/2)Φ²∓(1/2)[commutator]` route of §3.1, since the correction term's exact operator structure
   on multi-particle states is now known to be nontrivial rather than a simple multiplication
   operator.

**Honest bottom line.** The Fock-space picture gives a clean, internally consistent, and
numerically well-supported *candidate* value for the true sup over arbitrary symmetric-prime-
factor resonators (≈4.6456, matching Astra's richer family), comfortably below `π²/2`. It also
proves that the obvious analytic tool for turning this into a real bound (Cauchy–Schwarz on the
number operator) is vacuous on the relevant (mass-truncated, not particle-number-truncated) space.
Whether a sharper argument exists that actually proves `λ_max(K) < π²/2` uniformly — closing the
"diagonal method dead at φ=1/2" question for good — or whether the true limit sits above π²/2 (or
is `+∞`) once the idealisations of §2.1/§4.1 are removed, is **open**, and is the natural next
bounded task: either (a) a Hardy/Nelson-type multi-mode inequality tight enough to reproduce
≈4.65 analytically, or (b) pushing the *actual* finite arithmetic operator (Astra's, not this
idealised Fock model) to larger L with the coincidence-decomposition machinery already built in F2
to see whether its drift constant is heading toward 4.65, π²/2, or neither.

---

## 6. Reproduction and timing

```text
cd research/riemann-rmt/overnight/fable/astra_tasks/task001
OPENBLAS_NUM_THREADS=1 python3 f3_fock_spectrum.py --Ms 20,25,30,35,40,45,50,55,60
  # ~2.5 min total, max RSS 7.9 GB at M=60 (eigsh skipped there; largest run WITH eigsh is
  # M=55, max RSS 3.5 GB, 68s)
```

Single process, `OPENBLAS_NUM_THREADS=1`, `taskset -c 0,1` (2 cores), Python 3.11.15, numpy
2.4.6, scipy 1.17.1. **Repair-pass update:** this command (identical to the script's own
documented invocation, just with M=55,60 included) was re-run in full so that
`f3_fock_spectrum_results.json`/`_run.log` now contain every row quoted in §4.2's table, including
a real `λ_max` for M=55 (previously only built, not diagonalised, in an untracked exploratory run —
see §4.2's repair note). M=60 is still built but `eigsh`-skipped (7.9 GB > 4.0 GB cutoff), matching
the task's explicit instruction to stop at that point; it is not needed for the extrapolation.
Total task time for this repair pass (re-reading the two refutation reports, the small independent
verification script `check_f3_repair.py`, the full M=20..60 re-run, and rewriting this report): well
under the 20-minute *single-computation* guidance (the longest single run was the M=60 build/skip
step, ~100s); the re-run of M≤55 with `eigsh` completed in under 2.5 minutes total.

## 7. Claims (for the ledger)

| id | claim | label | evidence |
|---|---|---|---|
| F3-1 | **[repaired]** `K=(1/2)Φ²−(1/2)[A,A^T]` (FABLE-native letters, `[A,A^T]:=AA^T−A^TA`) is a pure algebraic identity on the truncated bosonic Fock space over `L²((0,1),du/u)`, verified to machine precision (≤4.4e-16, M=6,8,10) against the discretised operators; on the untruncated space `[A,A^T]=−C_g·Id` (`C_g=3.29656`) is an honest scalar. The further claim that the *truncated* commutator is still a scalar `c(v)=∫₀^{1−v}g²du/u` on the whole mass-`v` sector is **false** for multi-particle states (confirmed by direct computation: diagonal spread up to ~13× the mean within a fixed-mass sector at M=10) and is withdrawn; it survives only for the one-particle sector and the fully untruncated space | exact algebra (identity) + falsified sub-claim (withdrawn) | §2.2, §2.3; independent refuter's numerical construction (M=6, error 3.60 in the mis-signed version vs 4.4e-16 in the corrected one) and this repair pass's own reproduction at M=6,8,10, `astra_tasks/task001/check_f3_repair.py`, log `check_f3_repair_run.log` |
| F3-2 | The fixed rational trial's quadratic form equals `2π²(J+1/4)` with `J≈−0.0146624`, by direct identification with F2's already-certified/quadratured decomposition (no new computation) | exact algebra + certified continuum integral (reused) | §2.4; independently re-derived by a refuter from `f2_finite_sum_results.json` and confirmed unaffected by the F3-1 sign/scalar errors (it never used the Fock-commutator identity) |
| F3-3 | The Cauchy–Schwarz/number-operator bound on `‖Φ‖` is literally infinite on the mass-≤1-truncated Fock space (particle number is unbounded there); it gives no information about `λ_max(K)` vs. `π²/2`, in either direction. This verdict is unaffected by the F3-1 sign/scalar corrections (§3.1 rewritten to make the independence explicit) | exact algebra | §3.1 (rewritten), §3.2 |
| F3-4 | Exact Lanczos diagonalisation of the discretised (partitions-of-`m≤M`) truncated bosonic Fock space gives `λ_max(K)` = 4.61313, 4.61934, 4.62357, 4.62662, 4.62894, 4.63075, 4.63221, **4.63340** for M=20,25,30,35,40,45,50,**55 (new)**, monotone increasing with shrinking `~1/M` differences | finite numerical check | §4.2; `f3_fock_spectrum_results.json`/`_run.log` (both re-generated in this repair pass, now including the M=55 `eigsh` result and the M=60 build); independently reproduced to ~1e-12 by a second refuter for M=10..30 |
| F3-5 | Multiple extrapolations (3-point `1/M+1/M²`, global power law) agree to give `λ_∞ ≈ 4.6456 ± 0.0010`, about 6.0% below `π²/2=4.9348022`; adding the new M=55 point (window `(45,50,55)→4.645572`, power-law fit over 8 points `4.646446`) tightens but does not move this estimate | finite numerical check (extrapolation, not a proof of the limit) | §4.3; independently reproduced by a refuter for the original 7-point data, recomputed here with the 8th (M=55) point |
| F3-6 | This value matches Astra's independently-computed richer symmetric-prime-feature continuum optimum (4.645530, converted from J=−0.0146547256) to 3–4 significant figures, with the expected ordering (restricted family ≤ full Fock sup) | finite numerical check (cross-validation between two independent methods) | §4.4; independently reproduced by a refuter |
| F3-7 | A rigorous analytic bound reproducing the ≈4.646 numerical value, and the transfer of this idealised-continuum conclusion to the actual finite-L arithmetic operator (prime powers, `p|m` coincidences, real (non-Poissonised) primes), are both unresolved | open | §3.3, §5 |
| F3-8 | **(New)** The exact multi-particle operator structure of the truncated commutator `[A_trunc,A^T_trunc]` (beyond the one-particle sector and the untruncated space, both of which are exact) is unresolved — no corrected general formula, nor an operator-norm bound on its deviation from scalar, was derived in the time available | open | §2.3 (repair note), §5 open item 4 |
