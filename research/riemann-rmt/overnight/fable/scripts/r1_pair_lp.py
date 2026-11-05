"""
r1_pair_lp.py -- Task C1(c): the pair-correlation-only ceiling for the simple-zero proportion.

Primal (adversary):  maximise  A = nu({0})  over even positive measures nu on R with
      nu^(alpha) = delta_0(alpha) + |alpha|   on (-1, 1)          [Montgomery pair data, bandwidth one]
      nu^(alpha) >= 0                          on |alpha| >= 1     [form factor is a |.|^2: optional]
Given A_max, the multiplicity LP  min g_1  s.t.  sum k g_k = 1, sum k^2 g_k <= A_max  gives the
pair-only bound  N_simple/N >= 2 - A_max   (worst case: only doubles), and
N_distinct/N >= (3 - A_max)/2.

Dual (certificate):  minimise  r^(0) + int_{-1}^{1} |alpha| r^(alpha) d alpha  over even r with
      r >= 0 on R,  r(0) = 1,  r^ supported in [-1,1]            (Montgomery-Taylor class)
      r >= 0 on R,  r(0) = 1,  r^ <= 0 on |alpha| > 1            (Cheer-Goldston class, uses F >= 0)
Weak duality:  A <= int r dnu = int r^ nu^ <= r^(0) + int_{|a|<1} |a| r^(a) da.
In the MT class r = |g|^2 with g^ = v on [-1/2,1/2], r(0)=1 <=> int v = 1, and the objective is
q(v) = int v^2 + int int |s-t| v(s) v(t), minimised by v''=-2v: v*(s) = cos(sqrt2 s)/(sqrt2 sin(1/sqrt2)),
q* = 1/2 + (1/sqrt2) cot(1/sqrt2) = 1.32749929..., delta_MT = 2 - q* = 0.672500703679.

Numerics: the periodic-lattice model of r1_lattice_common.pair_lp (P points per period, M grid
points per mean spacing) is solved by HiGHS for increasing (P, M); the value converges to the
continuum optimum (the lattice restricts the adversary, so lattice delta >= continuum delta).
Outputs: data/r1_pair_lp.json (table) and data/r1_pair_dual_P{P}_M{M}.npz (dual certificate).
"""
import json, sys, time
import numpy as np
from r1_lattice_common import pair_lp, pair_cos_matrix

OUT = "/home/user/Alpha-devbox/research/riemann-rmt/overnight/fable/data/"
qstar = 0.5 + (1 / np.sqrt(2)) / np.tan(1 / np.sqrt(2))
delta_MT = 2 - qstar


def mt_check():
    """Euler-Lagrange check of the MT optimum: v'' = -2 v, v = c cos(sqrt2 s); q(v*) = q*."""
    n = 20000
    s = (np.arange(n) + 0.5) / n - 0.5
    h = 1.0 / n
    v = np.cos(np.sqrt(2) * s) / (np.sqrt(2) * np.sin(1 / np.sqrt(2)))
    mass = h * v.sum()
    q = h * (v @ v) + h * h * (v @ (np.abs(s[:, None] - s[None, :]) @ v))
    # stationarity: v(s) + int |s-t| v(t) dt should be constant (Lagrange multiplier)
    lag = v + h * (np.abs(s[:, None] - s[None, :]) @ v)
    return dict(mass=mass, q=q, qstar=qstar, lagrange_spread=float(lag.max() - lag.min()))


def dual_certificate(P, M, positivity):
    """Recover r^ from the LP multipliers and verify r >= 0 on the grid, r(0) = 1, and the value."""
    r = pair_lp(P, M, positivity=positivity, return_res=True)
    L = M * P
    C = pair_cos_matrix(L)
    y = r["eq_marg"]                      # multipliers of the equality rows k = 0..P-1 (sign: HiGHS)
    z = r["ineq_marg"] if positivity else None
    # HiGHS marginals: d(objective)/d(rhs). objective = -A (minimisation).  Build R(d):
    Rd = -(y @ C[0:P, :])
    if positivity:
        Rd = Rd - (z @ (-C[P:L // 2 + 1, :]))
    R0 = Rd[0]
    rhat = np.concatenate([-y, (-z if positivity else np.zeros(0))]) / R0
    rgrid = Rd / R0
    val = -(y[0] * P + (y[1:P] @ (np.arange(1, P) / P))) / R0
    return dict(P=P, M=M, A=r["A"], delta=r["delta"], rhat_k=rhat, r_grid=rgrid, dual_value=val,
                min_r=float(rgrid.min()), r0=float(rgrid[0]),
                neg_tail_mass=float(rhat[P:].sum()) if positivity else 0.0)


if __name__ == "__main__":
    print("MT analytic check:", mt_check())
    print(f"q* = {qstar:.12f}   delta_MT = {delta_MT:.12f}   (1+delta_MT)/2 = {(1+delta_MT)/2:.10f}")
    sizes = [(32, 4), (32, 8), (32, 16), (32, 32), (48, 32), (64, 32), (96, 32), (64, 48), (64, 64)]
    if len(sys.argv) > 1:
        sizes = [tuple(map(int, a.split(","))) for a in sys.argv[1:]]
    table = []
    for (P, M) in sizes:
        t = time.time()
        r0 = pair_lp(P, M, positivity=False)
        r1 = pair_lp(P, M, positivity=True)
        row = dict(P=P, M=M, L=P * M, delta_MTclass=r0["delta"], delta_Fpos=r1["delta"],
                   A_MTclass=r0["A"], A_Fpos=r1["A"], secs=time.time() - t)
        if P * M <= 1024:
            r2 = pair_lp(P, M, positivity=True, yamada=True, yamada_unions=M)
            row["delta_Fpos_yamada"] = r2["delta"]
        table.append(row)
        print(json.dumps(row), flush=True)
        with open(OUT + "r1_pair_lp.json", "w") as f:
            json.dump(dict(qstar=qstar, delta_MT=delta_MT, table=table), f, indent=1)
    for (P, M) in [(32, 16), (64, 32)]:
        for pos in (False, True):
            d = dual_certificate(P, M, pos)
            np.savez(OUT + f"r1_pair_dual_P{P}_M{M}_pos{int(pos)}.npz", **d)
            print(f"dual P={P} M={M} positivity={pos}: value {d['dual_value']:.8f} primal A {d['A']:.8f} "
                  f"delta {d['delta']:.8f} min r on grid {d['min_r']:.2e} r(0) {d['r0']:.6f} "
                  f"sum of rhat beyond band {d['neg_tail_mass']:.5f}", flush=True)
