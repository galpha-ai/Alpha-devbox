"""r2_lr_support_class.py -- certificates T supported in [-c,c] with That >= 0 only outside [-1,1].

For a hard-core-c process, E sum_{x!=y} T(x-y) = 0 exactly when supp T is in [-c,c].  Mimicry + Bochner
(S >= 0 on |alpha| >= 1, S = |alpha| inside) then force  J := That(0) - T(0) + int_{|a|<=1} |a| That <= 0.
Krein-type factorisation (recalled): a real entire That of exponential type 2 pi c, nonnegative on
|alpha| >= 1, is Q(alpha)|Ghat(alpha)|^2 with Q an even polynomial (roots of odd multiplicity in (-1,1),
positive at infinity) and supp G in [-c/2, c/2].  With Q(a) = sum_k q_k a^{2k},
   J = sum_k q_k J_k(G),  J_k(G) = delta_{k0} |Ghat(0)|^2 - (4 pi^2)^{-k} ||G^(k)||^2 + int_{|a|<=1} |a|^{2k+1} |Ghat|^2,
a quadratic form in G (Nystrom on a Legendre basis of H^k_0(-c/2,c/2)).  A certificate exists iff the
form has a positive eigenvalue.  Q = 1 is the weighted-window class (c_pd = 0.65633).  Scans
Q in {1, a^2 - e^2 (e in [0,1]), (a^2-1)(a^2-e^2), (a^2-e1^2)(a^2-e2^2)} and bisects c.
"""
import numpy as np, itertools
from scipy.linalg import eigh
from numpy.polynomial import legendre as Lg
from numpy.polynomial import polynomial as Pn

def kfun(j, x):
    """k_j(x) = 2 int_0^1 a^j cos(2 pi a x) da, via Gauss-Legendre (smooth, exact enough)."""
    t, w = np.polynomial.legendre.leggauss(200); al = 0.5*(t+1); w = 0.5*w
    return 2*(w*al**j) @ np.cos(2*np.pi*np.outer(al, x))

def forms(c, kmax, K=30, nq=600):
    """Return list of matrices [J_0, ..., J_kmax] in a basis of H^kmax_0(-c/2, c/2)."""
    t, w = np.polynomial.legendre.leggauss(nq); x = 0.5*c*t; w = 0.5*c*w
    env = Pn.Polynomial([(c/2)**2, 0, -1])**kmax if kmax > 0 else Pn.Polynomial([1.0])
    basis = [env*Pn.Polynomial(Lg.leg2poly([0]*j + [1]))(Pn.Polynomial([0, 2/c])) for j in range(K)]
    out = []
    for k in range(kmax + 1):
        Dk = np.array([p.deriv(k)(x) for p in basis])          # K x nq   G^(k)
        D0 = np.array([p(x) for p in basis])
        Kk = kfun(2*k + 1, x[:, None] - x[None, :]) if False else None
        # int int G(x)G(y) k_{2k+1}(x-y): build kernel matrix on the grid
        diff = (x[:, None] - x[None, :]).ravel()
        Kmat = kfun(2*k + 1, diff).reshape(nq, nq)
        M = (D0*w) @ Kmat @ (D0*w).T - (Dk*w) @ Dk.T/(4*np.pi**2)**k
        if k == 0:
            g0 = D0 @ w
            M = M + np.outer(g0, g0)
        out.append(M)
    return out

def has_cert(c, q, K=30):
    Js = forms(c, len(q) - 1, K)
    H = sum(q[k]*Js[k] for k in range(len(q)))
    return eigh(H, eigvals_only=True)[-1] > 1e-12

def cmin(q, lo=0.5, hi=0.75):
    if has_cert(lo, q): return lo
    if not has_cert(hi, q): return hi
    for _ in range(30):
        mid = 0.5*(lo + hi)
        if has_cert(mid, q): hi = mid
        else: lo = mid
    return hi

if __name__ == "__main__":
    print(f"Q = 1                      : c_min = {cmin([1.0]):.7f}   (weighted window, expect 0.65633)")
    best = (9, None)
    for e in np.linspace(0, 1, 41):
        cv = cmin([-e**2, 1.0])
        if cv < best[0]: best = (cv, e)
    print(f"Q = a^2 - e^2              : best c_min = {best[0]:.7f} at e = {best[1]:.3f}")
    best2 = (9, None)
    for e in np.linspace(0, 1, 21):
        cv = cmin(np.polymul([1.0, -1.0][::-1], [1.0, -e**2][::-1]).tolist())   # (a^2-1)(a^2-e^2) ascending in a^2
        if cv < best2[0]: best2 = (cv, e)
    print(f"Q = (a^2-1)(a^2-e^2)       : best c_min = {best2[0]:.7f} at e = {best2[1]:.3f}")
    best3 = (9, None)
    for e1 in np.linspace(0, 1, 11):
        for e2 in np.linspace(e1, 1, 11):
            q = Pn.polymul([-e1**2, 1.0], [-e2**2, 1.0])
            cv = cmin(list(q))
            if cv < best3[0]: best3 = (cv, (e1, e2))
    print(f"Q = (a^2-e1^2)(a^2-e2^2)   : best c_min = {best3[0]:.7f} at e = {best3[1]}")
    print("target 0.606894")
