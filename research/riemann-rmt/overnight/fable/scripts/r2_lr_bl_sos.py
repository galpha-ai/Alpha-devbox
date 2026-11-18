"""r2_lr_bl_sos.py -- the complete bandwidth-one-only certificate class, solved as eigenproblems.

Fact (Fejer-Riesz / Krein, recalled): a real entire T of exponential type 2 pi with T <= 0 on |x| >= c
has even-multiplicity real zeros outside (-c,c), so T = (c^2 - x^2) Q(x) |F(x)|^2 with Q an even
polynomial whose real roots lie in (-c,c) and F of exponential type pi (supp Fhat = psi in [-1/2,1/2]).
Certificate value: J = int T g_sine, g_sine = 1 - sinc^2.  With moments
    I_{2m}(psi) = int x^{2m} |F|^2 g_sine = (2 pi)^{-2m} ( ||psi^(m)||^2 - <psi^(m), Lambda * psi^(m)> ),
Q = prod (x^2 - d_i^2):  J = quadratic form in psi with coefficients polynomial in c, d_i.
A certificate exists iff the form has a positive eigenvalue.  psi in H^m_0(-1/2,1/2): basis
(1/4 - b^2)^m * Legendre_j(2b).  Scans d for deg Q = 0, 2, 4 and bisects c.  (No Bochner used.)
"""
import numpy as np, itertools, sys
from scipy.linalg import eigh
from numpy.polynomial import legendre as Lg

def moments(mmax, K, nq=1500):
    t, w = np.polynomial.legendre.leggauss(nq); b = 0.5*t; w = 0.5*w
    L = 1 - np.abs(b[:, None] - b[None, :])
    # basis: (1/4 - b^2)^mmax * P_j(2b), j = 0..K-1, and its derivatives up to order mmax (numerically via
    # polynomial algebra in the monomial basis of 2b)
    basis = []
    env = np.polynomial.polynomial.Polynomial([0.25, 0, -1])**mmax   # (1/4 - b^2)^mmax in b
    for j in range(K):
        Pj = np.polynomial.polynomial.Polynomial(Lg.leg2poly([0]*j + [1]))   # P_j(u), u = 2b
        Pj_b = Pj(np.polynomial.polynomial.Polynomial([0, 2]))                # P_j(2b)
        basis.append(env*Pj_b)
    Is = []
    for m in range(mmax + 1):
        D = np.array([p.deriv(m)(b) for p in basis])          # K x nq
        Dw = D*w
        G = Dw @ D.T - Dw @ L @ Dw.T
        Is.append(G/(2*np.pi)**(2*m))
    return Is

def has_cert(c, ds, Is):
    # Q(x) = prod (x^2 - d^2) ;  T = (c^2 - x^2) Q(x) |F|^2  ->  polynomial in x^2 with coefficients
    poly = np.array([c**2, -1.0])            # coefficients in y = x^2: c^2 - y
    for d in ds:
        poly = np.convolve(poly, np.array([-d**2, 1.0]))
    H = sum(poly[m]*Is[m] for m in range(len(poly)))
    lam = eigh(H, eigvals_only=True)
    return lam[-1] > 1e-13

def cmin(ds, Is, lo=0.4, hi=0.9):
    if has_cert(lo, ds, Is): return lo
    if not has_cert(hi, ds, Is): return hi
    for _ in range(40):
        mid = 0.5*(lo+hi)
        if has_cert(mid, ds, Is): hi = mid
        else: lo = mid
    return hi

if __name__ == "__main__":
    K = 24
    for deg in (0, 1, 2):
        Is = moments(deg + 1, K)
        if deg == 0:
            print(f"deg Q = 0:  c_min = {cmin([], Is):.7f}")
        elif deg == 1:
            best = (9, None)
            for d in np.linspace(0.0, 0.7, 71):
                cv = cmin([d], Is)
                if cv < best[0]: best = (cv, d)
            print(f"deg Q = 2:  best c_min = {best[0]:.7f} at d = {best[1]:.3f}")
            # refine
            d0 = best[1]
            for d in np.linspace(max(0, d0-0.02), d0+0.02, 41):
                cv = cmin([d], Is)
                if cv < best[0]: best = (cv, d)
            print(f"deg Q = 2:  refined c_min = {best[0]:.7f} at d = {best[1]:.4f}")
        else:
            best = (9, None)
            for d1 in np.linspace(0.0, 0.7, 36):
                for d2 in np.linspace(d1, 0.7, 36):
                    cv = cmin([d1, d2], Is)
                    if cv < best[0]: best = (cv, (d1, d2))
            print(f"deg Q = 4:  best c_min = {best[0]:.7f} at d = {best[1]}")
    print("targets: 0.606894 (LR), 0.7075761 (deg 0)")
