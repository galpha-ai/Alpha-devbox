"""fab_deflation.py — exact exchange rate for deflated spectral moments.

Guth-Maynard bound the top singular value of the Dirichlet-polynomial Gram matrix B_W
using tr B and a CENTERED third moment, and state that estimates for powers >= 4 are
unavailable.  The question this settles: if a power-r trace WERE estimable, how much
better is the resulting bound on lambda_1?

Exact extremal problem.  Fix m, p_1 = tr B, and p_r = tr B^r.  Among nonnegative spectra
with these two data, lambda_1 is largest when the remaining mass is spread as evenly as
possible (Schur-convexity of the power sum for r > 1), giving the sharp implicit bound

    lambda_1^r + (p_1 - lambda_1)^r / (m-1)^{r-1}  <=  p_r .

Solve for lambda_1 at each r and compare.  The deflation term is the bulk's contribution;
it decays like (m-1)^{-(r-1)}, so higher r isolates the spike far more sharply -- that is
the whole content of "deflated fourth trace power saving".
"""
import numpy as np
from scipy.optimize import brentq

def lam_max_bound(m, p1, pr, r):
    """largest lambda_1 consistent with (p1, pr) and m nonnegative eigenvalues"""
    f = lambda t: t**r + (p1-t)**r/(m-1)**(r-1) - pr
    lo, hi = p1/m, p1
    if f(lo) > 0: return lo
    if f(hi) < 0: return hi
    return brentq(f, lo, hi, xtol=1e-14)

print("Model spectrum: one spike of height h plus a flat bulk carrying the rest of the trace.")
print("We give the solver only (p_1, p_r) and ask for the best bound on lambda_1.\n")
for m in (100, 1000, 10000):
    print(f"m = {m}")
    print(f"{'true spike':>11} {'r=3 bound':>11} {'r=4':>10} {'r=6':>10} {'r=8':>10} {'r=10':>10}"
          f" {'gain 3->4':>10} {'gain 3->10':>11}")
    for frac in (0.5, 0.3, 0.15, 0.05):
        p1 = 1.0
        h = frac*p1
        bulk = (p1-h)/(m-1)
        lam = np.concatenate([[h], np.full(m-1, bulk)])
        row=[]
        for r in (3,4,6,8,10):
            pr = float((lam**r).sum())
            row.append(lam_max_bound(m, p1, pr, r))
        g34 = (row[0]-row[1])/row[0]
        g3_10 = (row[0]-row[4])/row[0]
        print(f"{h:>11.5f} {row[0]:>11.6f} {row[1]:>10.6f} {row[2]:>10.6f} {row[3]:>10.6f}"
              f" {row[4]:>10.6f} {g34:>9.2%} {g3_10:>10.2%}")
    print()

print("Adversarial case: the bulk is NOT flat but itself has a secondary cluster")
print("(this is what a real large-value set looks like -- resonator windows).")
m = 1000
for nsec, hsec in ((10, 0.03), (30, 0.015), (100, 0.005)):
    p1 = 1.0; h = 0.2
    rest = p1 - h - nsec*hsec
    lam = np.concatenate([[h], np.full(nsec, hsec), np.full(m-1-nsec, rest/(m-1-nsec))])
    out=[]
    for r in (3,4,6,8,10):
        out.append(lam_max_bound(m, p1, float((lam**r).sum()), r))
    print(f"  secondary cluster {nsec} x {hsec}:  true spike {h:.3f} ->"
          f" r=3 {out[0]:.6f}  r=4 {out[1]:.6f}  r=8 {out[3]:.6f}  r=10 {out[4]:.6f}"
          f"   (3->10 gain {100*(out[0]-out[4])/out[0]:.1f}%)")
