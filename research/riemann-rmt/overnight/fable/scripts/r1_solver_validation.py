"""r1_solver_validation.py -- two independent validations of depth_ode (root-ODE depth solver).

(i) ACUE single dislocation P_N(z) = (z-1)(z^N+1)/(z-e^{-i pi/N}) (gap pattern 1,2,...,2,3 in
    units of pi/N).  The programme's value N^2 D -> s* = 1.419640342 (lattice solver + continuum
    integral, HANDOFF §4.5) is reproduced here for N = 32, 64, 128, 256; approach O(N^-2).
(ii) Symmetric one-defect clock at N = 32, lambda = 0.5: high-precision (mpmath, 50 digits)
    bisection on the coefficient flow P_u(z) = sum a_j e^{u j(N-j)} z^j, detecting the first u at
    which a root leaves |z| = 1.  This is the dyn1_core method, re-implemented in multiprecision
    because np.roots is inaccurate (7e-3) on near-clock polynomials of degree >= 32.
"""
import os
import sys
from math import pi

import mpmath as mp
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from r1_one_defect_threshold import depth_ode, one_defect  # noqa: E402

S_STAR = 1.419640342


def acue_dislocation(N):
    ang = [0.0] + [pi * (2 * k + 1) / N for k in range(N - 1)]
    th = (np.array(ang) + pi) % (2 * pi) - pi
    return np.sort(th)


def mp_depth_bisect(th, N, dps=50, tol=1e-18):
    mp.mp.dps = dps
    roots0 = [mp.expj(mp.mpf(t)) for t in th]
    # coefficients of prod (z - z_j), ascending
    a = [mp.mpc(1)]
    for z in roots0:
        a = [mp.mpc(0)] + a
        for k in range(len(a) - 1):
            a[k] -= z * a[k + 1]
    a = a[:N + 1]
    w = [j * (N - j) for j in range(N + 1)]

    def offcircle(u):
        c = [a[j] * mp.e ** (u * w[j]) for j in range(N + 1)]
        rts = mp.polyroots(c[::-1], maxsteps=200, extraprec=60)
        return max(abs(abs(r) - 1) for r in rts)

    lo, hi = mp.mpf(0), mp.mpf(2) / (N * N)
    assert offcircle(lo) < 1e-30
    while offcircle(hi) < 1e-12:
        hi *= 2
    for _ in range(60):
        mid = (lo + hi) / 2
        if offcircle(mid) > 1e-12:
            hi = mid
        else:
            lo = mid
        if hi - lo < tol:
            break
    return float((lo + hi) / 2)


if __name__ == "__main__":
    print("(i) ACUE single dislocation, N^2 D vs s* = 1.419640342")
    for N in (32, 64, 128, 256):
        D = depth_ode(acue_dislocation(N))[0]
        print(f"   N={N:4d}  N^2 D = {N * N * D:.9f}   diff = {N * N * D - S_STAR:+.2e}   "
              f"N^2*diff = {N * N * (N * N * D - S_STAR):+.4f}")
    print("(ii) symmetric one-defect, N = 32, lambda = 0.5: ODE vs 50-digit coefficient bisection")
    N = 32
    th = one_defect(N, 0.5)
    D_ode = depth_ode(th)[0]
    D_mp = mp_depth_bisect(th, N)
    print(f"   N^2 D_ode = {N * N * D_ode:.10f}   N^2 D_mp = {N * N * D_mp:.10f}   "
          f"rel diff = {abs(D_ode - D_mp) / D_mp:.2e}")
