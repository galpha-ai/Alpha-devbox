#!/usr/bin/env python3
"""Repair-pass independent verification for task F3 (r2_diagonal_operator_spectrum.md).

Checks, against the discretised operators built by f3_fock_spectrum.build_operators(M),
the two issues an independent refuter raised about the report's original Fock-space algebra
(F3-1 in the claims ledger):

  1. The FABLE-native identity K = (1/2)Phi^2 - (1/2)[A,A^T] (with [A,A^T]:=A@A^T-A^T@A, ordinary
     operator commutator, no creation/annihilation relabelling) should hold to machine precision,
     since it is a pure algebraic identity (expansion of (A+A^T)^2), independent of the CCR.
  2. The claim that the truncated commutator [A,A^T] acts as a SCALAR on the whole fixed-total-mass
     sector (as opposed to only on the one-particle sector) should be FALSE for multi-particle
     states: the diagonal of the commutator matrix, restricted to a fixed-mass sector, should show
     a spread that is a large fraction of (or exceeds) its mean for masses away from the smallest
     few.

Run:  OPENBLAS_NUM_THREADS=1 python3 check_f3_repair.py
"""
import math
import numpy as np

from f3_fock_spectrum import build_operators, enumerate_partitions


def main():
    for M in (6, 8, 10):
        N, Acre_sparse, t_enum, t_build, nnz = build_operators(M)
        Acre = Acre_sparse.toarray()
        Aann = Acre.T
        K = Aann @ Acre + 0.5 * (Acre @ Acre + Aann @ Aann)
        Phi = Acre + Aann
        comm_fable = Acre @ Aann - Aann @ Acre  # [A,A^T]_FABLE := A A^T - A^T A
        K_check = 0.5 * Phi @ Phi - 0.5 * comm_fable
        err = np.abs(K - K_check).max()
        print(f"M={M}: max|K - ((1/2)Phi^2 - (1/2)[A,A^T]_FABLE)| = {err:.3e}  "
              f"(should be ~machine precision: confirms the FABLE-native identity)")

        keys, masses = enumerate_partitions(M)
        masses = np.array(masses)
        for v_mass in range(0, M + 1):
            idx = np.where(masses == v_mass)[0]
            if len(idx) < 2:
                continue
            diag = np.diag(comm_fable)[idx]
            spread = diag.max() - diag.min()
            mean = diag.mean()
            if abs(mean) > 1e-12:
                print(f"  M={M} mass={v_mass}: n_states={len(idx)}, diag mean={mean:.4f}, "
                      f"spread={spread:.4f}, spread/|mean|={spread/abs(mean):.3f}"
                      + ("  <-- nonzero spread: c(v) is NOT a scalar here" if spread > 1e-9 else ""))


if __name__ == "__main__":
    main()
