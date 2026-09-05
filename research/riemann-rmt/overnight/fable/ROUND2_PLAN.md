# Round 2 question bank (Fable overnight)

Launch order: B-cluster r2 (independent of r1) immediately; A-cluster r2 after r1 A1–A3 land;
D-cluster r2 after r1 D1–D2 land (CPU); C-cluster r2 chosen from C1's verdict.

## A-cluster r2 (depth, needs r1 A files)
- **A4 dynamic universality theorem** (`r2_dynamic_universality.md`): assemble Theorem A + repaired
  Theorem B (S*) + CUE/CβE background bounds + the external min-gap laws into ONE theorem with a
  complete proof and an explicit list of black boxes; state the abstract version (handoff §9.3):
  bandwidth-one sine pair correlation + repulsion exponent β + bounded background ⟹ D ≍ N^{−2−2/(β+1)}.
- **A5 marked-depth law** (`r2_marked_depth_proof.md`): prove Dτ[uu*] = (κδ/4)u*K_ab u + (δ²/8)κ′(u)
  by first-order perturbation of the first-collision time (Hadamard variation of the Cayley-transformed
  eigenvalues + the two-body-plus-background structure); verify against
  `riemann-impostors/verification/marked_depth_law.py`.
- **A6 ρ∞ = O(1) for ACUE** (`r2_acue_rho_bound.md`): deterministic lattice bound sup_{non-clock}
  N²D ≤ C via a refined comparison (Theorem B is vacuous at AN²δ² ≥ 4; need the exact one-defect or a
  better background integral). Enumerations for N ≤ 10 exist in `riemann-impostors/data/`.

## B-cluster r2 (zeta/RMT frontier, independent) — launched 06:35 UTC
- **B4 LR hard-core LP** (`r2_lr_hardcore_lp.md`): local-pattern LP relaxations on (1/M)ℤ for the
  Lagarias–Rodgers μ (published ½ ≤ μ ≤ 0.606894, conjectured ½); dual certificates uniform in M.
- **B5 function-field Newman universality** (`r2_function_field.md`): Katz–Sarnak equidistribution +
  a.e.-continuity of the depth ⟹ Law(depth(Θ_C)) → Law(depth(Haar)); USp/SO hard-edge exponents;
  genus-2 hyperelliptic numerics.
- **B6 DBM relaxation of the hard core** (`r2_dbm_relaxation.md`): Yau-flow experiment from ACUE:
  crossover time of the depth law vs the band-limited form factor.

## C-cluster r2 (after C1)
- if C1's triple LP moves the ceiling: **C3** push the LP (larger support, 4-point) and write the
  dual certificate as a theorem candidate; else **C3'** the M₋ lemma or close the question.

## D-cluster r2 (after D1–D2)
- **D3 push the H₂ record** (`r2_h2_push.md`): smaller k with M_k > 8 via the layer-cake engine at higher
  degree + narrow-tuple search; certificate in outward arithmetic from D1's tooling.
- **D4 m = 3 refresh** if D3 is quick.

## Round 3 candidates
- Newmanised parity barrier (handoff §9.7): Dobner flow experiment.
- Interference-code phase rigidity (open problem 12).
- One-defect closed form s* (open problem 3).
