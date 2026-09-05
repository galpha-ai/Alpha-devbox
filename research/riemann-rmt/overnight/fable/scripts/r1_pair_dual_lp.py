"""
r1_pair_dual_lp.py -- independent (non-lattice) cross-check of the pair-only ceilings by solving the
DUAL (certificate) problem directly in the continuum.

Certificate class:  r even, r(0) = 1, r(x) >= 0 for all x,
     r^ supported in [-Amax, Amax], r^ <= 0 on |alpha| > 1      (Cheer-Goldston class; F >= 0 used)
     [MT class: r^ supported in [-1, 1]]
Objective:  q(r) = r^(0) + int_{-1}^{1} |alpha| r^(alpha) d alpha ;  bound  N_simple/N >= 2 - q(r).

Discretisation: r^(alpha) = sum_j c_j B((alpha - alpha_j)/eta) with cubic B-splines on the grid
alpha_j = j*eta (even in alpha: the pair +-alpha_j is one basis element), so that
r(x) = sum_j c_j * eta * sinc^4(eta x) * [2 cos(2 pi alpha_j x) or 1 for j = 0]  (sinc(t) = sin(pi t)/(pi t)),
which decays like x^-4.  Positivity r >= 0 is imposed on a grid x in [0, X] with step hx; between
grid points the band-limited r can only dip by O(hx^2 * Amax^2), reported as 'margin'.
Sign constraint: c_j <= 0 for every spline whose support meets (1, Amax]  (slight over-restriction).
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
    """Centered cubic B-spline B(u), support (-2, 2), integral 1."""
    a = np.abs(u)
    out = np.zeros_like(a)
    m1 = a < 1
    m2 = (a >= 1) & (a < 2)
    out[m1] = (4 - 6 * a[m1] ** 2 + 3 * a[m1] ** 3) / 6
    out[m2] = (2 - a[m2]) ** 3 / 6
    return out


def solve(eta, Amax, X, hx, cg=True):
    J = int(round(Amax / eta))
    alphas = np.arange(J + 1) * eta
    x = np.arange(0, X + 1e-9, hx)
    s = np.sinc(eta * x) ** 4 * eta        # FT of B((alpha)/eta) (up to the even pairing)
    # r(x) = sum_j c_j * s(x) * w_j(x)
    W = np.empty((x.size, J + 1))
    W[:, 0] = s
    for j in range(1, J + 1):
        W[:, j] = 2 * s * np.cos(2 * np.pi * alphas[j] * x)
    # objective: q = r^(0) + int_{-1}^1 |alpha| r^(alpha) d alpha
    # r^(0) = c_0 B(0) + 2 sum_{j>=1} c_j B(-j)  (B(-j) nonzero for j = 1 only)
    B0, B1 = cubic_bspline_vals(np.array([0.0]))[0], cubic_bspline_vals(np.array([1.0]))[0]
    obj = np.zeros(J + 1)
    obj[0] += B0
    if J >= 1:
        obj[1] += 2 * B1
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
            bounds.append((0.0, 0.0) if alphas[j] + 2 * eta > 1 + 1e-12 else (None, None))
        else:
            bounds.append((None, 0.0) if alphas[j] + 2 * eta > 1 + 1e-12 else (None, None))
    res = linprog(obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if res.status != 0:
        return dict(status=res.message)
    c = res.x
    r = W @ c
    # positivity margin between grid points: check on a 10x finer grid
    xf = np.arange(0, X + 1e-9, hx / 10)
    sf = np.sinc(eta * xf) ** 4 * eta
    rf = c[0] * sf + sum(2 * c[j] * sf * np.cos(2 * np.pi * alphas[j] * xf) for j in range(1, J + 1))
    return dict(eta=eta, Amax=Amax, X=X, hx=hx, cg=cg, q=float(res.fun), delta=2 - float(res.fun),
                min_r_fine=float(rf.min()), c=c.tolist(), alphas=alphas.tolist(),
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
                  f"delta={r['delta']:.8f} min r (fine grid)={r['min_r_fine']:.2e} rhat(1)={r['rhat_at_1']:.4f} ({r['secs']:.1f}s)", flush=True)
    with open(OUT + "r1_pair_dual_lp.json", "w") as f:
        json.dump(runs, f)
