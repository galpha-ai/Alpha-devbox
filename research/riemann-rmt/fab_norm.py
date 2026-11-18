"""fab_norm.py — WHY the signed problem is unbounded, and what actually bounds it.

Claim under test: in the classical (positive) Maynard-Tao problem, positivity does double duty.
 (1) it validates the decode (no debt), and
 (2) it makes the variational problem BOUNDED, because for w >= 0 the normalization
     S1(w) = sum_c mu(c) w_c = 1 IS the l1 norm ||w||_1.
Drop positivity and (2) is lost: {S1 = 1} is an unbounded affine slice, and the repaired
objective Phi - D is unbounded along rays u with S1(u)=0, Phi(u) > D(u).
The natural physical replacement for (2) is the ARITHMETIC ERROR BUDGET: the type-II error in
S2 scales with the l1 mass of the coefficients, so reality imposes ||w||_1 <= A.

So the correct signed variational problem is
     lam_signed(A) = max { Phi(w) - D(w) : S1(w) = 1, ||w||_1 <= A },
a concave, nondecreasing function of A with lam_signed(1) = classical positive value
(since ||w||_1 = S1 = 1 forces w >= 0 a.e.).  This script computes lam_signed(A).
"""
import sys, json, numpy as np
sys.path.insert(0, "/tmp/claude-0/-home-user-Alpha-devbox/00b3b5f7-f917-5641-a9be-c6a8f38f5cd7/scratchpad")
from scipy.optimize import linprog
from sgn1_model import build_model, primes_upto
from sgn1_solve import floatize


def lam_signed(M, A, beta=1.0):
    """max Phi(w) - beta*D(w) s.t. S1(w)=1, ||w||_1 <= A, w in span(features)."""
    Phi, N1, Nnu, G, a = floatize(M)
    nc, dim = Phi.shape
    # vars: x (dim, free), p (nc, >=0), n (nc, >=0)  with w = Phi x = p - n
    nv = dim + 2 * nc
    Aeq = np.zeros((nc + 1, nv)); beq = np.zeros(nc + 1)
    Aeq[:nc, :dim] = Phi
    Aeq[:nc, dim:dim + nc] = -np.eye(nc)
    Aeq[:nc, dim + nc:] = np.eye(nc)
    Aeq[nc, dim:dim + nc] = N1
    Aeq[nc, dim + nc:] = -N1
    beq[nc] = 1.0
    # ||w||_1 = sum_c mu(c)(p_c + n_c) <= A
    Aub = np.zeros((1, nv)); Aub[0, dim:dim + nc] = N1; Aub[0, dim + nc:] = N1
    bub = np.array([A])
    # objective: Phi(w) = a.w = a.(p-n) ; D(w) = sum_c G(c)*n_c   (G already carries mu)
    cvec = np.zeros(nv)
    cvec[dim:dim + nc] = -a
    cvec[dim + nc:] = a + beta * G
    r = linprog(cvec, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq,
                bounds=[(None, None)] * dim + [(0, None)] * (2 * nc), method="highs")
    if r.status == 3: return dict(status="unbounded")
    if r.status != 0: return dict(status=f"fail{r.status}")
    p = r.x[dim:dim + nc]; n = r.x[dim + nc:]
    w = p - n
    return dict(status="optimal", val=-r.fun, l1=float(N1 @ (p + n)),
                Dval=float(G @ n), negmass=float(N1 @ n), w=w)


if __name__ == "__main__":
    BIG = [p for p in primes_upto(37) if p > 7]
    out = {}
    for lab, H, feat, m in [("k3m1", (0, 2, 6), [2, 3, 5, 7], 1),
                            ("k4m1", (0, 2, 6, 8), [2, 3, 5, 7], 1),
                            ("k5m1", (0, 2, 6, 8, 12), [2, 3, 5, 7], 1),
                            ("k5m2", (0, 2, 6, 8, 12), [2, 3, 5, 7], 2)]:
        M = build_model(H, feat, BIG, m=m, L=1)
        rows = []
        for A in [1.0, 1.05, 1.1, 1.25, 1.5, 2.0, 3.0, 5.0, 10.0, 30.0, 100.0]:
            r = lam_signed(M, A)
            rows.append(dict(A=A, status=r["status"],
                             val=r.get("val"), l1=r.get("l1"),
                             D=r.get("Dval"), negmass=r.get("negmass")))
            print(lab, rows[-1], flush=True)
        out[lab] = rows
        # marginal leverage dlam/dA at A=1+
        v1 = rows[0]["val"]; v2 = rows[1]["val"]
        print(f"  {lab}: lam(1)={v1:.9f}  slope at A=1+: {(v2-v1)/0.05:.6f}", flush=True)
    json.dump(out, open("fab_norm_results.json", "w"), indent=1)
    print("saved fab_norm_results.json")
