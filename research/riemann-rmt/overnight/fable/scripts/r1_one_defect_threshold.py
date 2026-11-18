"""r1_one_defect_threshold.py -- depth of one shortened gap in a clock background.

Configuration (N points on the unit circle, mean spacing Delta = 2 pi / N):
    defect pair at  +-lambda*Delta/2,
    background at   Delta*(k + 1/2),  k = 1 .. N-2        (the clock with the two slots
                                                            +-Delta/2 replaced by the pair)
so the cyclic gap pattern in units of Delta is  (lambda, (3-lambda)/2, 1, ..., 1, (3-lambda)/2).

Depth D = first collision time of the root ODE  theta_j' = -sum_{k != j} cot((theta_j-theta_k)/2)
(Lemma 1 of depth_scaling_theorem.md), integrated with DOP853 until the defect gap reaches
g_stop = 1e-3*Delta, plus the exact two-body remainder -log cos(g_stop/2)  (relative error of the
remainder is O(N^2 g_stop^2) ~ 1e-5, and the remainder itself is ~1e-6 of D).

Three quantities are produced:
  (1) exact N-body N^2 D(lambda) for N = 64, 128, 256 and lambda on a grid;
  (2) the rigid-background reduction: only the two defect points move, the other N-2 stay at the
      clock slots; the background sum is evaluated in closed form through
          sum_{k=0}^{N-1} cot((x + 2 pi k/N)/2) = N cot(N x / 2),
      giving the scalar ODE  phi' = -cot(phi) + N tan(N phi/2) + cot((phi-Delta/2)/2)
                                     + cot((phi+Delta/2)/2)
      and, as N -> infinity with u = phi/Delta, sigma = N^2 s,
          du/dsigma = F(u) = -1/(4 pi^2 u) + tan(pi u)/(2 pi) + u/(pi^2 (u^2 - 1/4)),
      so  N^2 D_rigid(lambda) = int_0^{lambda/2} du / (-F(u))   (a one-dimensional quadrature);
  (3) the threshold lambda* with N^2 D = pi^2/8 for each N (exact ODE) and for the rigid limit,
      by Brent root finding.

A cross-check against the coefficient-bisection solver dyn1_core.find_ustar is run at N = 64.

Usage:  python3 r1_one_defect_threshold.py          (writes ../data/r1_one_defect.json)
"""
import json
import os
import sys
import time
from math import pi, cos, log, tan

import numpy as np
from scipy.integrate import solve_ivp, quad
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PI2_8 = pi ** 2 / 8


# ----------------------------------------------------------------------------- configuration
def one_defect(N, lam):
    """Angles of the one-defect clock (sorted, in (-pi, pi])."""
    Delta = 2 * pi / N
    bg = Delta * (np.arange(1, N - 1) + 0.5)
    th = np.concatenate([[-lam * Delta / 2, lam * Delta / 2], bg])
    th = (th + pi) % (2 * pi) - pi
    return np.sort(th)


# ----------------------------------------------------------------------------- root ODE
def rhs(s, th):
    """theta_j' = -sum_{k != j} cot((theta_j - theta_k)/2)."""
    d = th[:, None] - th[None, :]
    np.fill_diagonal(d, np.nan)
    c = 1.0 / np.tan(0.5 * d)
    np.fill_diagonal(c, 0.0)
    return -c.sum(axis=1)


def depth_ode(th0, g_stop_frac=1e-3, rtol=1e-10, atol=1e-13):
    """First collision time of the sorted configuration th0 (any configuration).

    Integrates until the minimal cyclic gap reaches g_stop = g_stop_frac * 2pi/N, then adds
    the two-body remainder -log cos(g/2). Returns (D, index of the colliding gap, s_event, g_event).
    """
    N = len(th0)
    g_stop = g_stop_frac * 2 * pi / N

    def min_gap(th):
        s = np.sort(th)
        g = np.diff(np.concatenate([s, [s[0] + 2 * pi]]))
        return g.min(), int(np.argmin(g))

    def event(s, th):
        return min_gap(th)[0] - g_stop

    event.terminal = True
    event.direction = -1
    # generous horizon: the two-body time of the initial min gap times 4 is always enough
    g0, _ = min_gap(th0)
    horizon = 4.0 * (-log(cos(g0 / 2))) + 1e-9
    sol = solve_ivp(rhs, (0.0, horizon), th0, method="DOP853", rtol=rtol, atol=atol,
                    events=event, dense_output=False)
    if not sol.t_events[0].size:
        raise RuntimeError("no collision before horizon")
    s_e = float(sol.t_events[0][0])
    th_e = sol.y_events[0][0]
    g_e, idx = min_gap(th_e)
    return s_e - log(cos(g_e / 2)), idx, s_e, g_e


# ----------------------------------------------------------------------------- rigid ansatz
def rigid_rhs_finiteN(phi, N):
    """phi' for the defect point at +phi, partner at -phi, rigid clock background at
    Delta(k+1/2), k=1..N-2, evaluated by the direct sum (stable near phi -> Delta/2)."""
    Delta = 2 * pi / N
    bg = Delta * (np.arange(1, N - 1) + 0.5)
    return -1.0 / tan(phi) - np.sum(1.0 / np.tan(0.5 * (phi - bg)))


def rigid_rhs_closed(phi, N):
    """Same as rigid_rhs_finiteN but through the closed-form clock sum (identity check)."""
    Delta = 2 * pi / N
    return (-1.0 / tan(phi) + N * tan(N * phi / 2)
            + 1.0 / tan(0.5 * (phi - Delta / 2)) + 1.0 / tan(0.5 * (phi + Delta / 2)))


def F_inf(u):
    """N -> infinity rigid-background velocity du/dsigma, u = phi/Delta, sigma = N^2 s."""
    return -1.0 / (4 * pi ** 2 * u) + tan(pi * u) / (2 * pi) + u / (pi ** 2 * (u * u - 0.25))


def rigid_depth_inf(lam):
    """N^2 D in the rigid limit: int_0^{lam/2} du/(-F_inf(u)).  Integrand ~ 4 pi^2 u near 0."""
    val, err = quad(lambda u: 1.0 / (-F_inf(u)), 0.0, lam / 2, limit=200, epsabs=1e-13, epsrel=1e-12)
    return val


def rigid_depth_finiteN(lam, N):
    """N^2 D under the rigid ansatz at finite N (scalar ODE integrated by quadrature in phi)."""
    Delta = 2 * pi / N
    phi0 = lam * Delta / 2
    val, err = quad(lambda p: 1.0 / (-rigid_rhs_finiteN(p, N)), 0.0, phi0, limit=200,
                    epsabs=1e-16, epsrel=1e-12)
    return N * N * val


# ----------------------------------------------------------------------------- coefficient cross-check
def poly_coeffs_ascending(th):
    """a_j of P(z) = prod (1 - e^{i th_j} z), ascending, a_0 = 1 (dyn1_core convention)."""
    N = len(th)
    a = np.zeros(N + 1, complex)
    a[0] = 1.0
    for k, t in enumerate(th):
        z = np.exp(1j * t)
        a[1:k + 2] = a[1:k + 2] - z * a[:k + 1]
    return a


def main():
    out = {"pi2_8": PI2_8, "exact": {}, "rigid_finiteN": {}, "rigid_inf": {}, "lambda_star": {},
           "checks": {}}
    t0 = time.time()

    # identity check: closed-form clock sum vs direct sum
    N = 37
    xs = np.linspace(0.05, 6.0, 25)
    direct = [np.sum(1.0 / np.tan(0.5 * (x + 2 * pi * np.arange(N) / N))) for x in xs]
    closed = [N / tan(N * x / 2) for x in xs]
    out["checks"]["cot_identity_max_abs_err_N37"] = float(np.max(np.abs(np.array(direct) - np.array(closed))))
    # rigid RHS: direct vs closed form
    N = 64
    Delta = 2 * pi / N
    errs = [abs(rigid_rhs_finiteN(p, N) - rigid_rhs_closed(p, N)) for p in np.linspace(0.05, 0.95, 19) * Delta / 2]
    out["checks"]["rigid_rhs_direct_vs_closed_maxerr_N64"] = float(max(errs))
    # clock equilibrium of F_inf near u = 1/2
    out["checks"]["F_inf_at_u_0.4999"] = F_inf(0.4999)
    out["checks"]["F_inf_at_u_0.49999"] = F_inf(0.49999)
    print("checks:", out["checks"])

    lams = [0.30, 0.35, 0.40, 0.45, 0.46, 0.47, 0.48, 0.49, 0.50, 0.55, 0.60, 0.70, 0.80, 0.90]

    # rigid limit
    print("\nrigid N->inf:  lambda   N^2 D   rho=N^2D/(pi^2 lam^2/2)")
    for lam in lams:
        v = rigid_depth_inf(lam)
        out["rigid_inf"][str(lam)] = v
        print(f"   {lam:.2f}  {v:.8f}  {v / (pi ** 2 * lam ** 2 / 2):.6f}")
    ls_rigid = brentq(lambda l: rigid_depth_inf(l) - PI2_8, 0.3, 0.6, xtol=1e-12)
    out["lambda_star"]["rigid_inf"] = ls_rigid
    print(f"   lambda*_rigid,inf = {ls_rigid:.9f}   rho(lambda*) = {1 / (4 * ls_rigid ** 2):.6f}")

    for N in (64, 128, 256):
        print(f"\nN = {N}")
        out["exact"][N] = {}
        out["rigid_finiteN"][N] = {}
        print("   lambda   N^2D_exact    N^2D_rigid(N)   rho_exact   colliding-gap-is-defect")
        for lam in lams:
            th = one_defect(N, lam)
            D, idx, s_e, g_e = depth_ode(th)
            v = N * N * D
            vr = rigid_depth_finiteN(lam, N)
            out["exact"][N][str(lam)] = v
            out["rigid_finiteN"][N][str(lam)] = vr
            # the defect gap is the one between the two points nearest angle 0
            srt = np.sort(th)
            j0 = int(np.argmin(np.abs(srt)))  # one of the pair
            defect_ok = idx in (j0, j0 - 1, (j0 + 1) % N, (j0 - 1) % N)
            print(f"   {lam:.2f}   {v:.8f}   {vr:.8f}   {v / (pi ** 2 * lam ** 2 / 2):.6f}   {defect_ok}")
        f = lambda l: N * N * depth_ode(one_defect(N, l))[0] - PI2_8
        ls = brentq(f, 0.40, 0.55, xtol=1e-9)
        fr = lambda l: rigid_depth_finiteN(l, N) - PI2_8
        lsr = brentq(fr, 0.40, 0.55, xtol=1e-12)
        out["lambda_star"][f"exact_N{N}"] = ls
        out["lambda_star"][f"rigid_N{N}"] = lsr
        print(f"   lambda*_exact(N={N}) = {ls:.9f}   lambda*_rigid(N={N}) = {lsr:.9f}   "
              f"[elapsed {time.time() - t0:.1f}s]")

    # cross-check with dyn1_core.find_ustar at N = 64, lambda = 0.5
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "riemann-impostors", "counterexamples"))
    try:
        from dyn1_core import find_ustar
        N = 64
        th = one_defect(N, 0.5)
        a = poly_coeffs_ascending(th)
        u, lo, hi = find_ustar(a, N)
        D_ode = depth_ode(th)[0]
        out["checks"]["N64_lam0.5_find_ustar_N2D"] = N * N * u
        out["checks"]["N64_lam0.5_ode_N2D"] = N * N * D_ode
        print(f"\ncross-check N=64 lam=0.5: N^2 D (coefficient bisection) = {N * N * u:.8f}, "
              f"(root ODE) = {N * N * D_ode:.8f}, rel diff {abs(u - D_ode) / D_ode:.2e}")
    except Exception as e:  # pragma: no cover
        out["checks"]["find_ustar_error"] = repr(e)
        print("find_ustar cross-check failed:", e)

    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "r1_one_defect.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {os.path.join(DATA, 'r1_one_defect.json')}   total {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
