"""Exact weighted integer sums versus the continuum S2 moments (Fable task001 / F1, numerical support).

For L in {1e4, 1e5, 1e6} (+1e7 as an extra) and v in {0.25, 0.5, 0.75, 1}, sieve d_ell(n) and
S2(n) = sum_{p|n} (log p/log L)^2 (distinct primes) and compute EXACTLY (float64, pairwise summation)
     Sigma_j(x) = sum_{n<=x} d_ell(n)^2 S2(n)^j / n,   x = floor(L^v),  j = 0,1,2.
Compared quantities (ell = 16/15, a = ell^2):
  (a) cumulative ratios  Sigma_1/Sigma_0 vs a v^2/((a+1)(a+2)),   Sigma_2/Sigma_0 vs a(a+6) v^4/((a+1)(a+2)(a+3)(a+4));
  (b) local window ratios over n in (L^{v-h}, L^v], h = 0.1, vs the v^{a-1}dv-weighted window averages of the
      claimed densities E_v[S2] = v^2/(a+1), E_v[S2^2] = (a+6) v^4/((a+1)(a+2)(a+3));
  (c) normalisation Sigma_0(x) vs C_ell (log x)^a/Gamma(a+1), one- and two-term Selberg-Delange expansions
      (second coefficient K'(0) = C_ell (a*gamma + G'(1)/G(1)));
  (d) leading coefficients of the marked sums: Sigma_1 (log L)^2/(log x)^{a+2} -> ell^2 C_ell/Gamma(a+3),
      Sigma_2 (log L)^4/(log x)^{a+4} -> a(a+6) C_ell/Gamma(a+5).
The observed convergence rate is exhibited as (observed/predicted - 1) * log x, which should stabilise if the
relative error is O(1/log x).  Euler constants from primes <= 1e7.  Output: f1_moment_results.json.
Runtime: about 1-2 minutes (single core).
"""
from __future__ import annotations
import json, sys, time
from math import gamma, log, floor
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from f1_common import ELL, sieve_d_S, euler_constants

EULER_GAMMA = 0.57721566490153286
ell = ELL
a = ell * ell
LMAX = 10 ** 7
Ls = [10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7]
vs = [0.25, 0.5, 0.75, 1.0]
h = 0.1

t0 = time.time()
d, St = sieve_d_S(LMAX, ell)
print(f"sieve to {LMAX}: {time.time()-t0:.1f}s", flush=True)
n = np.arange(LMAX + 1, dtype=float)
wt = np.zeros(LMAX + 1); wt[1:] = d[1:] ** 2 / n[1:]
ec = euler_constants(LMAX, ell)
C = ec["C_ell"]; GpG = ec["GprimeOverG"]
print("Euler constants:", ec, flush=True)

pred_cum1 = lambda v: a * v ** 2 / ((a + 1) * (a + 2))
pred_cum2 = lambda v: a * (a + 6) * v ** 4 / ((a + 1) * (a + 2) * (a + 3) * (a + 4))
def pred_loc1(v0, v1):
    return (a / ((a + 1) * (a + 2))) * (v1 ** (a + 2) - v0 ** (a + 2)) / (v1 ** a - v0 ** a)
def pred_loc2(v0, v1):
    return ((a + 6) / ((a + 1) * (a + 2) * (a + 3))) * (a / (a + 4)) * (v1 ** (a + 4) - v0 ** (a + 4)) / (v1 ** a - v0 ** a)

rows = []
for L in Ls:
    logL = log(L)
    S2 = St[:L + 1] / logL ** 2
    w0 = wt[:L + 1]; w1 = w0 * S2; w2 = w1 * S2
    for v in vs:
        x = int(floor(L ** v + 1e-9)); lx = log(x)
        s0 = float(np.sum(w0[:x + 1])); s1 = float(np.sum(w1[:x + 1])); s2 = float(np.sum(w2[:x + 1]))
        xl = int(floor(L ** (v - h) + 1e-9))
        l0 = float(np.sum(w0[xl + 1:x + 1])); l1 = float(np.sum(w1[xl + 1:x + 1])); l2 = float(np.sum(w2[xl + 1:x + 1]))
        one = C * lx ** a / gamma(a + 1)
        two = one + C * (a * EULER_GAMMA + GpG) * lx ** (a - 1) / gamma(a)
        row = {"L": L, "v": v, "x": x, "log_x": lx,
               "Sigma0": s0, "Sigma1": s1, "Sigma2": s2,
               "cum_ratio1": s1 / s0, "cum_pred1": pred_cum1(v), "cum_ratio2": s2 / s0, "cum_pred2": pred_cum2(v),
               "loc_ratio1": l1 / l0, "loc_pred1": pred_loc1(v - h, v), "loc_ratio2": l2 / l0, "loc_pred2": pred_loc2(v - h, v),
               "norm_ratio_1term": s0 / one, "norm_ratio_2term": s0 / two,
               "lead1_obs": s1 * logL ** 2 / lx ** (a + 2), "lead1_pred": ell ** 2 * C / gamma(a + 3),
               "lead2_obs": s2 * logL ** 4 / lx ** (a + 4), "lead2_pred": a * (a + 6) * C / gamma(a + 5)}
        for k in ("cum", "loc"):
            for j in (1, 2):
                r = row[f"{k}_ratio{j}"] / row[f"{k}_pred{j}"] - 1
                row[f"{k}_relerr{j}"] = r; row[f"{k}_relerr{j}_times_logx"] = r * lx
        row["norm_relerr_1term_times_logx"] = (row["norm_ratio_1term"] - 1) * lx
        row["norm_relerr_2term_times_logx2"] = (row["norm_ratio_2term"] - 1) * lx ** 2
        rows.append(row)
        print(f"L={L:>8} v={v:4.2f} x={x:>8} | cum1 {s1/s0:.6f} vs {pred_cum1(v):.6f} (rel {row['cum_relerr1']:+.4f}, *logx {row['cum_relerr1_times_logx']:+.3f})"
              f" | cum2 {s2/s0:.6f} vs {pred_cum2(v):.6f} (rel {row['cum_relerr2']:+.4f}, *logx {row['cum_relerr2_times_logx']:+.3f})"
              f" | loc1 rel {row['loc_relerr1']:+.4f} loc2 rel {row['loc_relerr2']:+.4f}"
              f" | norm 1t {row['norm_ratio_1term']:.5f} 2t {row['norm_ratio_2term']:.6f}", flush=True)
out = {"ell": "16/15", "a": a, "window_h": h, "euler_constants": ec, "rows": rows,
       "labels": "finite numerical check; predictions are the Selberg-Delange/Mertens asymptotics derived in the report",
       "seconds": time.time() - t0}
Path(__file__).with_name("f1_moment_results.json").write_text(json.dumps(out, indent=2))
print("done", f"{time.time()-t0:.1f}s")
