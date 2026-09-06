"""r2_lr_pd_window_eig.py -- weighted-window-count certificates (positive-definite T supported in [-c,c]).

For F supported on an interval of length c and a hard-core-c process, at most one point lies in the
window, so N(F)^2 = sum F(x)^2 and Var N(F) = int F^2 - (int F)^2.  Bochner + bandwidth-one mimicry:
Var N(F) >= int_{|a|<=1} |a| |Fhat(a)|^2 da.  Hence the quadratic form
    Q_c(F) = (int F)^2 - int F^2 + int_{|a|<=1} |a| |Fhat|^2
          = <F, (1 1^T - I + K) F>,   K(x,y) = k(x-y),  k(x) = sin(2 pi x)/(pi x) + (cos 2 pi x - 1)/(2 pi^2 x^2)
must be <= 0 on L^2[-c/2,c/2].  (T = F * F~ is the dual certificate; F = 1 gives the triangle.)
c_pd := smallest c with lambda_max(1 1^T - I + K) = 0.  Computed by Nystrom discretisation.
"""
import numpy as np
from scipy.linalg import eigh
import mpmath as mp

def k(x):
    x = np.asarray(x, float)
    out = np.empty_like(x)
    small = np.abs(x) < 1e-6
    xs = x[~small]
    out[~small] = np.sin(2*np.pi*xs)/(np.pi*xs) + (np.cos(2*np.pi*xs) - 1)/(2*np.pi**2*xs**2)
    out[small] = 1.0   # k(0) = 2 int_0^1 a da = 1
    return out

def lam_max(c, n=400):
    t, w = np.polynomial.legendre.leggauss(n)
    x = 0.5*c*t; w = 0.5*c*w
    sw = np.sqrt(w)
    M = np.outer(sw, sw)*(1.0 + k(x[:, None] - x[None, :])) - np.eye(n)   # symmetrised Nystrom
    return eigh(M, eigvals_only=True)[-1]

if __name__ == "__main__":
    for c in (0.5, 0.55, 0.6, 0.606894, 0.62, 0.65, 0.6695):
        print(f"c={c:.6f}  lambda_max={lam_max(c):+.7f}")
    lo, hi = 0.5, 0.7
    for _ in range(40):
        mid = 0.5*(lo+hi)
        if lam_max(mid) > 0: hi = mid
        else: lo = mid
    print(f"c_pd (n=400) = {0.5*(lo+hi):.8f}")
    for n in (200, 800):
        lo, hi = 0.5, 0.7
        for _ in range(40):
            mid = 0.5*(lo+hi)
            if lam_max(mid, n) > 0: hi = mid
            else: lo = mid
        print(f"c_pd (n={n}) = {0.5*(lo+hi):.8f}")
    print("target 0.606894")
