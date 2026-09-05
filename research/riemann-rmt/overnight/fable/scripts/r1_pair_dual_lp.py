"""
r1_pair_dual_lp.py -- independent (non-lattice) cross-check of the pair-only ceilings by solving the
DUAL (certificate) problem directly in the continuum.

Certificate class:  r even, r(0) = 1, r(x) >= 0 for all x,
     r^ supported in [-Amax, Amax], r^ <= 0 on |alpha| > 1      (Cheer-Goldston class; F >= 0 used)
     [MT class: r^ supported in [-1, 1]]
Objective:  q(r) = r^(0) + int_{-1}^{1} |alpha| r^(alpha) d alpha ;  bound  N_simple/N >= 2 - q(r).

Discretisation: r^(alpha) = sum_j c_j Lambda((alpha - alpha_j)/eta) with HAT functions (piecewise
linear, Lambda(u) = (1-|u|)_+) on the grid alpha_j = j*eta (even in alpha: the pair +-alpha_j is one
basis element), so that
r(x) = sum_j c_j * eta * sinc^2(eta x) * [2 cos(2 pi alpha_j x) or 1 for j = 0]  (sinc(t) = sin(pi t)/(pi t)).
A C^0 basis is essential: the Montgomery-Taylor r^ = v*v~ vanishes only LINEARLY at alpha = +-1
(v*(+-1/2) != 0); a C^2 (cubic B-spline) basis forced to vanish at 1 vanishes like (1-alpha)^3 and the
certificate value collapses (first version of this script: q = 2.17 instead of 1.3275 -- kept in the
'Failed attempts' section of r1_simple_zeros.md).
Positivity r >= 0 is imposed on a grid x in [0, X] with step hx and re-checked on a 10x finer grid and
on [X, 3X] afterwards (r decays like x^-2 only).
Sign constraint: c_j <= 0 for every hat centred at alpha_j >= 1 (over-restricts r^ on (1-eta, 1) by O(eta)).
Any feasible c gives a VALID certificate up to the grid-positivity caveat, so the LP value is an
upper bound on q over the class, i.e. 2 - q is a lower bound on delta for that class, up to the
caveat; agreement with the primal lattice values (r1_pair_lp.py) pins the continuum optimum.
"""
import json, sys, time
import numpy as np
from scipy.optimize import linprog
from scipy.interpolate import BSpline

OUT = "/home/user/Alpha-devbox/research/riemann-rmt/overnight/fable/data/"


def cubic_bspline_vals(u):
    """Hat function Lambda(u) = (1-|u|)_+ (name kept for the failed-attempt history; see docstring)."""
    return np.clip(1 - np.abs(u), 0, None)


def solve(eta, Amax, X, hx, cg=True):
    J = int(round(Amax / eta))
    alphas = np.arange(J + 1) * eta
    x = np.arange(0, X + 1e-9, hx)
    s = np.sinc(eta * x) ** 2 * eta        # FT of Lambda(alpha/eta) (up to the even pairing)
    # r(x) = sum_j c_j * s(x) * w_j(x)
    W = np.empty((x.size, J + 1))
    W[:, 0] = s
    for j in range(1, J + 1):
        W[:, j] = 2 * s * np.cos(2 * np.pi * alphas[j] * x)
    # objective: q = r^(0) + int_{-1}^1 |alpha| r^(alpha) d alpha
    # r^(0) = c_0 (hats at alpha_j, j>=1, vanish at 0)
    obj = np.zeros(J + 1)
    obj[0] += 1.0
    # int_{-1}^{1} |alpha| r^ = 2 int_0^1 alpha r^(alpha) d alpha, r^ even; compute by fine quadrature
    ag = np.linspace(0, 1, 200001)
    for j in range(0, J + 1):
        bj = cubic_bspline_vals((ag - alphas[j]) / eta) + (cubic_bspline_vals((ag + alphas[j]) / eta) if j else 0)
        obj[j] += 2 * np.trapezoid(ag * bj, ag)
    # constraints: r(x_i) >= 0  ->  -W c <= 0 ; r(0) = 1 -> W[0] c = 1
    A_ub = -W
    b_ub = np.zeros(x.size)
    A_eq = W[0:1, :]
    b_eq = np.array([1.0])
    bounds = []
    for j in range(J + 1):
        if not cg:
            bounds.append((0.0, 0.0) if alphas[j] > 1 - 1e-12 else (None, None))
        else:
            bounds.append((None, 0.0) if alphas[j] > 1 - 1e-12 else (None, None))
    res = linprog(obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if res.status != 0:
        return dict(status=res.message)
    c = res.x
    r = W @ c
    # positivity margin between grid points: check on a 10x finer grid
    xf = np.arange(0, X + 1e-9, hx / 10)
    sf = np.sinc(eta * xf) ** 2 * eta
    rf = c[0] * sf + sum(2 * c[j] * sf * np.cos(2 * np.pi * alphas[j] * xf) for j in range(1, J + 1))
    xt = np.arange(X, 3 * X, hx)
    st_ = np.sinc(eta * xt) ** 2 * eta
    rt = c[0] * st_ + sum(2 * c[j] * st_ * np.cos(2 * np.pi * alphas[j] * xt) for j in range(1, J + 1))
    return dict(eta=eta, Amax=Amax, X=X, hx=hx, cg=cg, q=float(res.fun), delta=2 - float(res.fun),
                min_r_fine=float(rf.min()), min_r_tail=float(rt.min()), c=c.tolist(), alphas=alphas.tolist(),
                rhat_at_1=float(sum(c[j] * (cubic_bspline_vals(np.array([(1 - alphas[j]) / eta]))[0] +
                                        cubic_bspline_vals(np.array([(1 + alphas[j]) / eta]))[0]) for j in range(J + 1))))


if __name__ == "__main__":
    runs = []
    for cg in (False, True):
        for (eta, Amax, X, hx) in [(1 / 20, 3, 120, 0.01), (1 / 40, 3, 240, 0.01), (1 / 80, 3, 480, 0.01),
                                    (1 / 40, 2, 240, 0.01), (1 / 40, 4, 240, 0.01), (1 / 40, 6, 240, 0.005)]:
            if not cg and Amax != 3:
                continue
            t = time.time()
            r = solve(eta, Amax, X, hx, cg=cg)
            r["secs"] = time.time() - t
            runs.append(r)
            print(f"class={'CG' if cg else 'MT'} eta=1/{round(1/eta)} Amax={Amax} X={X} hx={hx}: q={r['q']:.8f} "
                  f"delta={r['delta']:.8f} min r (fine grid)={r['min_r_fine']:.2e} min r on [X,3X]={r['min_r_tail']:.2e} rhat(1)={r['rhat_at_1']:.4f} ({r['secs']:.1f}s)", flush=True)
    with open(OUT + "r1_pair_dual_lp.json", "w") as f:
        json.dump(runs, f)
