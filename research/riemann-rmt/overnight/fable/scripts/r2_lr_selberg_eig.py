"""r2_lr_selberg_eig.py -- band-limited certificates of the form T(x) = (c^2 - x^2)|F(x)|^2.

If supp Fhat = psi is in [-1/2,1/2] then T = (c^2-x^2)|F|^2 has supp That in [-1,1] (bandwidth one),
and T <= 0 for |x| >= c automatically.  For a hard-core-c process, E sum_{x!=y} T(x-y) <= 0, while
bandwidth-one sine mimicry fixes E sum T = int T g_sine, g_sine = 1 - sinc^2.  So no hard core c
exists whenever  int (c^2 - x^2)|F|^2 g_sine dx > 0  for some F, i.e. whenever
    c^2 > lambda_min := inf_psi  B(psi)/A(psi),
    A = int |F|^2 g_sine = ||psi||^2 - <psi, Lambda * psi>,
    B = int x^2 |F|^2 g_sine = (1/4pi^2) ( ||psi'||^2 - <psi', Lambda * psi'> ),  psi in H^1_0(-1/2,1/2),
with Lambda(b) = (1-|b|)_+ (the FT of sinc^2).  Uses only mimicry, not Bochner on |alpha| > 1.
Computed by a sine basis psi_k = sin(k pi (b + 1/2)) on [-1/2,1/2]; prints sqrt(lambda_min) vs 0.606894.
"""
import numpy as np, sys
from scipy.integrate import dblquad
from scipy.linalg import eigh

def run(K, nq=2000):
    # Gauss-Legendre on [-1/2,1/2]
    t, w = np.polynomial.legendre.leggauss(nq)
    b = 0.5*t; w = 0.5*w
    ks = np.arange(1, K+1)
    S = np.sin(np.outer(ks, np.pi*(b + 0.5)))            # K x nq   psi_k(b)
    dS = (np.pi*ks)[:, None]*np.cos(np.outer(ks, np.pi*(b + 0.5)))
    L = 1 - np.abs(b[:, None] - b[None, :])              # Lambda(b-b') on the grid (|b-b'|<=1)
    Wm = np.sqrt(w)
    def gram(P):
        Pw = P*w
        G = Pw @ P.T                                     # int psi_k psi_l
        C = (Pw @ L @ Pw.T)                               # int int psi_k(b) Lambda(b-b') psi_l(b')
        return G - C
    A = gram(S); B = gram(dS)/(4*np.pi**2)
    lam = eigh(B, A, eigvals_only=True)
    return lam[:3]

if __name__ == "__main__":
    for K in (10, 20, 40, 80):
        lam = run(K)
        print(f"K={K:3d}  lambda_min={lam[0]:.9f}  sqrt={np.sqrt(lam[0]):.7f}   next: {np.sqrt(lam[1]):.5f}", flush=True)
    print("target 0.606894")
