#!/usr/bin/env python3
"""FABLE task 001 / item F3: truncated bosonic Fock-space spectrum of K = A^T A + (A^2+(A^T)^2)/2.

Discretisation of the continuum schema in r2_diagonal_operator_spectrum.md, part (c):
  u in {1/M, 2/M, ..., 1}; a configuration is a multiset of "parts" j in {1,...,M} with
  sum j <= M (an integer partition of some m <= M).  This is the standard occupation-number
  basis of the bosonic Fock space over M modes with mode j costing mass j/M, truncated to
  total mass <= 1 (i.e. total occupied mass <= M).

  Creation operator (matches the FABLE/F2 convention: "A" raises the configuration):
    A |partition p> = sum_{j=1}^{M-|p|} g(j/M) sqrt(mult_j(p)+1) |p + one part j>,
    g(u) = 2 sin(pi u / 2).
  A^T is the adjoint (annihilation): standard bosonic ladder, sqrt(mult_j(p)) removing a part j.
  K = A^T A + (A^2 + (A^T)^2)/2, same formula as the finite arithmetic operator and as the
  abstract Fock-space K = (1/2)Phi^2 - (1/2)[A^T,A] derived in part (a)/(b) of the report
  (here "A" plays the role of the creation operator A* of that section).

  This is the RAW / arbitrary-coefficient operator (no ell, d_ell, or H weighting) -- it tests
  the sup over ALL resonator vectors, matching Astra's arithmetic_operator.py Perron-eigenvalue
  search, in the idealised L -> infinity (Poissonised prime measure du/u) limit.

Run:  OPENBLAS_NUM_THREADS=1 python3 f3_fock_spectrum.py --Ms 20,30,40
Output: f3_fock_spectrum_results.json next to this file (or --out).
"""
from __future__ import annotations
import argparse
import json
import math
import resource
import sys
import time
from pathlib import Path

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import eigsh

sys.setrecursionlimit(10000)
HERE = Path(__file__).resolve().parent


def enumerate_partitions(M):
    """All partitions with parts in {1,...,M}, total sum <= M.  Each partition is a tuple of
    (part, mult) pairs, part descending, mult > 0 only (canonical key).  Returns
    (list_of_keys, list_of_masses)."""
    keys = []
    masses = []

    def rec(max_part, remaining, current):
        if max_part == 0:
            keys.append(tuple(current))
            return
        max_mult = remaining // max_part
        for mult in range(max_mult, -1, -1):
            if mult > 0:
                current.append((max_part, mult))
            rec(max_part - 1, remaining - mult * max_part, current)
            if mult > 0:
                current.pop()

    rec(M, M, [])
    masses = [sum(part * mult for part, mult in k) for k in keys]
    return keys, masses


def build_operators(M):
    t0 = time.perf_counter()
    keys, masses = enumerate_partitions(M)
    N = len(keys)
    index = {k: i for i, k in enumerate(keys)}
    dicts = [dict(k) for k in keys]
    t_enum = time.perf_counter() - t0

    # Orthonormal-mode coefficient for inserting mass j/M: an orthonormal basis function for the
    # bin [((j-1)/M,j/M)] of H=L^2((0,1),du/u) has height ~ sqrt(u_j/Delta u) = sqrt(j) there, so
    # its overlap with the (unnormalised, per-unit-du/u) test function g(u) picks up an extra
    # 1/sqrt(j): c_j = <phi_j, g>_H ~ g(u_j)/sqrt(j).  This matches the finite operator's
    # w_q = 2 sin((pi/2) log q/log L)/sqrt(q) (the 1/sqrt(q) is NOT optional -- omitting it gives
    # an unnormalised model whose lambda_max blows up immediately, see f3 dev notes).
    g = lambda j: 2.0 * math.sin(math.pi * (j / M) / 2.0) / math.sqrt(j)

    t1 = time.perf_counter()
    rows, cols, vals = [], [], []
    for i in range(N):
        d = dicts[i]
        m = masses[i]
        budget = M - m
        if budget <= 0:
            continue
        for j in range(1, budget + 1):
            old = d.get(j, 0)
            d[j] = old + 1
            newkey = tuple(sorted(d.items(), reverse=True))
            if old == 0:
                del d[j]
            else:
                d[j] = old
            newidx = index[newkey]
            rows.append(newidx)
            cols.append(i)
            vals.append(g(j) * math.sqrt(old + 1))
    t_build = time.perf_counter() - t1

    Acre = coo_matrix((vals, (rows, cols)), shape=(N, N)).tocsr()
    nnz = Acre.nnz
    return N, Acre, t_enum, t_build, nnz


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--Ms", default="20,30,40")
    ap.add_argument("--out", default=str(HERE / "f3_fock_spectrum_results.json"))
    ap.add_argument("--mem-limit-mb", type=float, default=4000.0)
    args = ap.parse_args()

    out = {"model": "truncated bosonic Fock space, modes j=1..M cost mass j/M, creation weight "
                     "g(j/M)=2 sin(pi j/(2M)), K = A^T A + (A^2+(A^T)^2)/2 (A = creation, "
                     "FABLE/F2 convention)",
           "threshold_pi2_over_2": math.pi ** 2 / 2,
           "expanded_family_reference": 4.646,
           "results": []}

    for M in map(int, args.Ms.split(",")):
        t0 = time.perf_counter()
        N, Acre, t_enum, t_build, nnz = build_operators(M)
        maxrss_MB = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        print(f"M={M}: dim={N}, nnz(Acre)={nnz}, enum {t_enum:.1f}s, build {t_build:.1f}s, "
              f"maxrss {maxrss_MB:.0f} MB", flush=True)
        if maxrss_MB > args.mem_limit_mb:
            print(f"M={M}: memory {maxrss_MB:.0f} MB exceeds limit {args.mem_limit_mb} MB, skipping eigsh", flush=True)
            out["results"].append({"M": M, "dim": N, "nnz_Acre": int(nnz),
                                    "status": "built, eigsh skipped (memory limit)",
                                    "maxrss_MB": maxrss_MB})
            Path(args.out).write_text(json.dumps(out, indent=2))
            continue

        Aann = Acre.transpose().tocsr()

        def Kmatvec(x):
            ax = Acre @ x
            atx = Aann @ x
            return Aann @ ax + 0.5 * (Acre @ ax + Aann @ atx)

        from scipy.sparse.linalg import LinearOperator
        Kop = LinearOperator((N, N), matvec=Kmatvec, dtype=np.float64)

        t1 = time.perf_counter()
        v0 = np.ones(N)
        val, vec = eigsh(Kop, k=1, which="LA", v0=v0, tol=1e-10, maxiter=20000)
        t_eig = time.perf_counter() - t1
        lam = float(val[0])
        u = vec[:, 0]
        res = float(np.linalg.norm(Kmatvec(u) - lam * u))
        min_entry = float(u.min()) * float(np.sign(u[np.argmax(np.abs(u))]))
        maxrss_MB2 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

        rec = {"M": M, "dim": N, "nnz_Acre": int(nnz), "lambda_max": lam,
               "margin_over_2pi2_minus_quarter": lam / (2 * math.pi ** 2) - 0.25,
               "eigsh_residual": res, "min_signed_entry": min_entry,
               "timing_s": {"enum": t_enum, "build": t_build, "eigsh": t_eig,
                            "total": time.perf_counter() - t0},
               "maxrss_MB": maxrss_MB2}
        out["results"].append(rec)
        print(f"M={M}: lambda_max(K)={lam:.10f}  (pi^2/2={math.pi**2/2:.7f})  "
              f"residual={res:.2e}  total {rec['timing_s']['total']:.1f}s  maxrss {maxrss_MB2:.0f} MB",
              flush=True)
        Path(args.out).write_text(json.dumps(out, indent=2))

    # simple 1/M extrapolation if >= 2 usable points
    pts = [(r["M"], r["lambda_max"]) for r in out["results"] if "lambda_max" in r]
    if len(pts) >= 2:
        xs = np.array([1.0 / m for m, _ in pts])
        ys = np.array([lam for _, lam in pts])
        if len(pts) == 2:
            # linear in 1/M
            A = np.vstack([np.ones_like(xs), xs]).T
            coef, *_ = np.linalg.lstsq(A, ys, rcond=None)
            out["extrapolation_linear_1_over_M"] = {"lambda_infty": float(coef[0]), "slope": float(coef[1])}
        else:
            A = np.vstack([np.ones_like(xs), xs, xs ** 2]).T
            coef, *_ = np.linalg.lstsq(A, ys, rcond=None)
            out["extrapolation_quadratic_1_over_M"] = {"lambda_infty": float(coef[0]),
                                                         "c1": float(coef[1]), "c2": float(coef[2])}
            A2 = np.vstack([np.ones_like(xs), xs]).T
            coef2, *_ = np.linalg.lstsq(A2, ys, rcond=None)
            out["extrapolation_linear_1_over_M"] = {"lambda_infty": float(coef2[0]), "slope": float(coef2[1])}
    Path(args.out).write_text(json.dumps(out, indent=2))
    print("done", flush=True)


if __name__ == "__main__":
    main()
