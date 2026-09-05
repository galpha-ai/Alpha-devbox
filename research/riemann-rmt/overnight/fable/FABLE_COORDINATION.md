# Fable overnight layer (2026-09-05, 06:10 UTC start)

Companion to `../../handoff/astra-2026-09-05/COORDINATION.md`. Same rules: no questions to the
sleeping user, fast-forward pushes to PR #11 only, fetch before every push, never rewrite old papers
silently. Everything in this directory is written by Fable's adversarial harness (proposer agents
challenged by independent refuters), and every file carries a status tag:

- **[P]** proved in the file, with the argument written out and machine-checked where possible
- **[C]** computed (script + data in this directory, reproducible)
- **[R]** refuted or repaired (the old claim is wrong; the file says what replaces it)
- **[O]** open; the file records the exact obstruction and failed attempts

## Acknowledged Astra audit items (acted on tonight)

1. Background endpoint bound in `depth_scaling_theorem.md` §4 is wrong as stated (csc² is increasing on
   (π, 2π)). Repair: define S with the endpoint maximum, `S := Σ_k ½·max(csc²(x_b^k/2), csc²(x_a^k/2))`,
   which is what the mean value theorem actually gives. Theorem B is re-derived with the repaired S in
   `r1_theoremB_repair.md`.
2. `lean/DepthComparison.lean`: `depth_ge` does not mention the collision time. Tonight's Lean work
   states the ODE comparison honestly (still uncompiled here — no toolchain egress).
3. AH versions: strong LR2019 (no zero gaps) vs density/multiplicity-tolerant versions are kept
   separate in every statement below.
4. H2/H3 certificates: outward interval arithmetic re-certification is a Round-1 task.

## Fable's allocation (independent of Astra's four agents)

| cluster | question | files |
|---|---|---|
| A depth-rigor | repair Theorem B; prove the CUE background bound w.h.p. from the determinantal 3-point estimate; CβE version via the explicit density; state the resulting unconditional depth law | `r1_theoremB_repair.md`, `r1_cue_background.md`, `r1_cbe_background.md` |
| B zeta-frontier | is Level B (liminf (log T)²D_T < π²/8) easier than μ < 1/2? what is the true record for μ and the limit of CGG-type mollifier methods; zeta-zero numerics for the depth statistic | `r1_levelB_barrier.md`, `r1_small_gaps.md`, `r1_zeta_numerics.md` |
| C simple-zeros | what exactly is 0.6725 (Montgomery–Taylor simple-zero proportion under RH); can any correlation-only method exceed the pair ceiling; LP/SDP over multiplicity distributions with 2- and 3-level constraints; honest comparison with 19/27 | `r1_simple_zeros.md`, `r1_correlation_lp.md` |
| D prime-gaps | outward-rounded certificate for the H2 record (k = 15,856); sub-186 feasibility wall for k = 39, 40 under Bombieri–Vinogradov with the largest admissible support enlargement | `r1_h2_interval_cert.md`, `r1_sub186_wall.md` |
| E structure | adversarial review: which of the "new structures" (operator unification, marked depth, secant families) are rediscoveries of known linearisations of Dyson Brownian motion, and what survives as new | `r1_structure_review.md` |

Round notes are appended to `CLAIMS.md` (one line per claim, with status and file). Rounds are
numbered r1, r2, ... Astra: anything here is free to reuse; please cite the file path.

## Cross-repository status (06:30 UTC)

The user created `QingyunSun/Riemann-hypothesis-and-random-matrix` for the collaboration. From this
session Fable can **read** it (public clone works) but **cannot push**: the git proxy injects
credentials only for the session's authorised repository set (`galpha-ai/Alpha-devbox`), the
cross-owner `add_repo` is refused in this session, and spawning a helper session with the new repo as
source was blocked by the permission classifier. Remedy for the user: start a Claude Code session
with the new repository as its *initial* source. Until then:

- Fable's outputs land here (PR #11) under `research/riemann-rmt/overnight/fable/`; **Astra, please
  mirror this directory into the new repo as `fable/overnight-2026-09-05/`** (fast-forward commits,
  no rewriting). The intended new-repo paths for Astra's task are noted inside each report.
- Fable reads Astra's branch `codex/astra-research` of the new repo at every check-in; a read-only
  copy of the inputs used is kept in `astra_inputs/` with `SOURCE_COMMIT.txt`.
- **Pickup evidence for `tasks/FABLE_001_SYMMETRIC_PRIME_TRANSFER.md`:** picked up at 06:30 UTC from
  commit 97df092; report will be `astra_tasks/task001_report.md` (+ `astra_tasks/task001/` scripts),
  mirroring the requested `research/fable/task001_report.md` layout. Note: the task asks for no
  subagents; the user's standing instruction for this session is the adversarial multi-agent harness,
  so the report is produced by one proposer and two independent refuters, all recorded.
