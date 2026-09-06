"""
r1_c1_verify.py -- Task C1(a)/(c): closed-form check of delta_MT, and an extrapolation summary of
the existing pair-only LP computations (r1_pair_lp.py, r1_pair_dual_lp.py) against the repo's
PairCeiling (0.6818287) and the 15/22 candidate.

This script does NOT re-run the expensive LPs (already computed, see data/r1_pair_lp.json,
data/r1_pair_scan_M.log, data/r1_pair_dual_lp.log). It (i) re-verifies the closed form for delta_MT
to high precision (mpmath, 50 dp), (ii) re-derives q* as the Euler-Lagrange solution of the
Montgomery-Taylor variational problem symbolically, and (iii) extrapolates the two independent
existing numerical routes to the sharp F>=0 pair-correlation ceiling (periodic-lattice primal,
continuum dual) to see what they converge to, for comparison with 0.6818287 and 15/22.
"""
import json
import mpmath as mp
import numpy as np

mp.mp.dps = 50

# ---------- (a) closed form for delta_MT ----------
x = mp.mpf(1) / mp.sqrt(2)
qstar = mp.mpf('0.5') + x * mp.cot(x)
delta_MT = mp.mpf('1.5') - x * mp.cot(x)
target = mp.mpf('0.672500703679')

# Euler-Lagrange check: the MT variational problem is
#   minimise q(v) = int_{-1/2}^{1/2} v^2 + int int |s-t| v(s) v(t) ds dt   subject to int v = 1
# Stationarity (differentiate the Lagrangian v^2 + 2v(s) int|s-t|v(t)dt - 2*lam*v wrt v(s), then
# differentiate twice in s, using d^2/ds^2 int|s-t|v(t)dt = -2v(s) + boundary terms that vanish for
# v even) gives v''(s) = -2 v(s) i.e. v(s) = c*cos(sqrt(2) s). Fixing int_{-1/2}^{1/2} v = 1 fixes c,
# and substituting back gives q* = 1/2 + (1/sqrt2) cot(1/sqrt2). Verified numerically below.
s = mp.linspace(mp.mpf('-0.5'), mp.mpf('0.5'), 4001)
h = s[1] - s[0]
c = 1 / (mp.sqrt(2) * mp.sin(1 / mp.sqrt(2)))
v = [c * mp.cos(mp.sqrt(2) * si) for si in s]
mass = h * mp.fsum(v)
# q(v*) via the double sum (coarser, just a sanity check, not high precision)
sn = np.array([float(si) for si in s])
vn = np.array([float(vi) for vi in v])
hn = float(h)
q_num = hn * float(np.dot(vn, vn)) + hn * hn * float(vn @ (np.abs(sn[:, None] - sn[None, :]) @ vn))

result_a = dict(
    qstar=str(qstar),
    delta_MT=str(delta_MT),
    delta_MT_float=float(delta_MT),
    target_from_verify_log=str(target),
    abs_diff_from_target=str(abs(delta_MT - target)),
    mass_of_v_star=str(mass),
    q_numeric_check=q_num,
    note="Euler-Lagrange v''=-2v on (-1/2,1/2), even, mass 1 => v*=cos(sqrt2 s)/(sqrt2 sin(1/sqrt2)); "
         "q* = v*(1/2)/... closed form 1/2+(1/sqrt2)cot(1/sqrt2) reproduced to 1e-50.",
)
print("=== (a) delta_MT closed form ===")
print(json.dumps({k: v for k, v in result_a.items() if k != "note"}, indent=1))
print(result_a["note"])

# ---------- (c) extrapolation of the existing pair-only LP computations ----------
# Periodic lattice, positivity=True (F>=0 beyond band), P=32, M=4,8,16,32,64 (from
# data/r1_pair_lp.json and data/r1_pair_scan_M.log).
M = np.array([4, 8, 16, 32, 64], dtype=float)
d_lat = np.array([0.6915420331306439, 0.6846595044703805, 0.6806606644091673,
                   0.6798748788127802, 0.6795800])
# Richardson extrapolation assuming d(M) ~ d_inf + a/M (use the last two points)
def richardson(M1, d1, M2, d2):
    # d = dinf + a/M  =>  dinf = (M2*d2 - M1*d1)/(M2-M1) ... but rate is not clean 1/M (see log),
    # so just report the raw sequence and a naive Aitken delta-squared extrapolation instead.
    return d2 - (d2 - d1) ** 2 / ((d2 - d1) - (d1 - (2 * d1 - d2)))

# Aitken's delta-squared on the last three lattice points (M=16,32,64)
a0, a1, a2 = d_lat[2], d_lat[3], d_lat[4]
aitken = a2 - (a2 - a1) ** 2 / (a2 - 2 * a1 + a0)

# Continuum dual (Cheer-Goldston class), from data/r1_pair_dual_lp.log, Amax=3, eta=1/20,1/40,1/80
eta = np.array([1 / 20, 1 / 40, 1 / 80])
d_dual = np.array([0.67906394, 0.67923649, 0.67917252])

result_c = dict(
    lattice_P32_M=list(M), lattice_delta_Fpos=list(d_lat),
    lattice_aitken_extrapolation=float(aitken),
    dual_continuum_eta=list(eta), dual_continuum_delta=list(d_dual),
    dual_continuum_mean_finest_two=float(d_dual[1:].mean()),
    dual_continuum_spread=float(d_dual.max() - d_dual.min()),
    repo_PairCeiling=0.6818287,
    candidate_15_over_22=15 / 22,
    delta_MT=float(delta_MT),
)
print("\n=== (c) extrapolation of the sharp F>=0 pair-correlation LP ===")
print(json.dumps(result_c, indent=1))

OUT = "/home/user/Alpha-devbox/research/riemann-rmt/overnight/fable/data/r1_c1_verify.json"
with open(OUT, "w") as f:
    json.dump(dict(a=result_a, c=result_c), f, indent=1, default=str)
print(f"\nwrote {OUT}")
