"""fab_transversal.py — the three-way classification, made computable.

Class test (i): TRANSVERSALITY at configuration level.
  Observables: bandwidth-r moment map M_r(X) = (p_1,...,p_r), p_k = sum_j e^{i k theta_j}.
  Depth: tau(X) = -Lambda(X).  Question: ker DM_r  subset-of?  ker D tau.
  Equivalently: does grad(tau) lie in rowspace(DM_r)?  Residual > 0  <=>  there is a
  moment-blind direction that MOVES the depth  <=>  Lambda kills that class directly.

Class test (ii): ISOSPECTRAL BLINDNESS and the marked repair.
  Lambda depends on the characteristic polynomial only, so isospectral G1,G2 have
  Lambda(G1)=Lambda(G2) identically.  Marked deformation G_eta = G + eta u u^*,
  U_eta = Cayley(G_eta), chi(G;u) = d/d_eta Lambda(U_eta)|_0.  By the determinant lemma
  det(zI-G-eta uu^*) = det(zI-G)(1 - eta u^*(zI-G)^{-1}u), so chi is driven by the
  directional resolvent -- exactly the inverse-Gram quantity the static counterexamples
  were built around.
"""
import numpy as np, sys, json
sys.path.insert(0, ".")
from dyn1_core import find_ustar

def coeffs_from_angles(th):
    p = np.array([1.0+0j])
    for t in th: p = np.convolve(p, np.array([1.0, -np.exp(1j*t)]))
    return p[::-1]                      # a_0..a_N, ascending

def depth(th):
    a = coeffs_from_angles(th)
    u,_,_ = find_ustar(a, len(th))
    return u

def grad_depth(th, h=1e-5):
    g = np.zeros(len(th))
    for j in range(len(th)):
        tp = th.copy(); tp[j] += h
        tm = th.copy(); tm[j] -= h
        g[j] = (depth(tp) - depth(tm)) / (2*h)
    return g

def DM_real(th, r):
    """real Jacobian of (Re p_1,Im p_1,...,Re p_r,Im p_r) wrt theta"""
    N = len(th); rows = []
    for k in range(1, r+1):
        d = 1j*k*np.exp(1j*k*th)
        rows.append(d.real); rows.append(d.imag)
    return np.array(rows)

def transversality(th, label):
    N = len(th); g = grad_depth(th); out = []
    for r in range(1, N):
        A = DM_real(th, r)
        # residual of g orthogonal to rowspace(A)
        Q, _ = np.linalg.qr(A.T)
        res = g - Q @ (Q.T @ g)
        out.append((r, float(np.linalg.norm(res)/max(np.linalg.norm(g),1e-300)),
                    int(np.linalg.matrix_rank(A, tol=1e-9))))
    print(f"\n{label}: N={N}, tau={depth(th):.8f}, |grad tau|={np.linalg.norm(g):.4e}")
    print("   r  rank(DM_r)  relative residual of grad(tau) off rowspace(DM_r)")
    for r, rel, rk in out:
        verdict = "MOVES depth (transversal)" if rel > 1e-6 else "blind"
        print(f"  {r:>2}   {rk:>6}      {rel:>12.3e}   {verdict}")
    return out

if __name__ == "__main__":
    # (a) single-dislocation ACUE configuration, N=6 and N=8
    for N in (6, 8):
        idx = [0] + list(range(1, 2*N-2, 2))
        th = np.array([np.pi*i/N for i in idx])
        transversality(th, f"single-dislocation ACUE (N={N})")
    # (b) a generic lattice (ACUE) configuration
    rng = np.random.default_rng(7)
    N = 7; M = 2*N
    idx = np.sort(rng.choice(M, N, replace=False))
    th = np.array([np.pi*i/N for i in idx])
    transversality(th, f"random ACUE lattice config N={N}, slots={list(idx)}")
    # (c) a generic (non-lattice) configuration for comparison
    th = np.sort(rng.uniform(0, 2*np.pi, 7))
    transversality(th, "generic non-lattice config N=7")
