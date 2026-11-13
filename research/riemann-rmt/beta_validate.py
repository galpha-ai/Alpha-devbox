"""beta_validate.py — validate the Killip–Nenciu CbetaE sampler + solvers.

(1) beta=2 KN must reproduce CUE: two-sample KS on (a) all normalized spacings
    N*g/(2pi), (b) smallest gap N^{4/3}*dmin, vs dyn2's stored CUE data at N=64
    and vs fresh Haar draws.
(2) beta=1 KN vs direct COE = V V^T at N=16: two-sample KS on spacings & dmin.
(3) Solver cross-check on KN samples: ODE vs coefficient bisection, beta=1,4.
(4) Tracked solver == dyn2 solver on identical inputs.
"""
import numpy as np
from scipy import stats
import time, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from beta_core import (cbe_eigenangles, coe_eigenangles, adjacent_gaps,
                       haar_eigenangles, neg_lambda_ode, neg_lambda_coeff,
                       neg_lambda_ode_tracked)

SP = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20260818)

# ---------------- (1) beta=2 vs CUE at N=64
N = 64
M = 2500
t0 = time.time()
sp_kn, dmin_kn = [], []
for _ in range(M):
    th = cbe_eigenangles(N, 2.0, rng)
    g = adjacent_gaps(th)
    sp_kn.append(g)
    dmin_kn.append(g.min())
sp_kn = np.concatenate(sp_kn) * N / (2 * np.pi)
dmin_kn = np.array(dmin_kn) * N ** (4 / 3)
print(f"KN beta=2 sampling: {time.time()-t0:.1f}s for {M} draws at N={N}")

# stored dyn2 CUE dmin at N=64
d = np.load(os.path.join(SP, "dyn2_data_N64.npz"))
dmin_cue_stored = d["dmin"] * N ** (4 / 3)
ks1 = stats.ks_2samp(dmin_kn, dmin_cue_stored)
print(f"[V1a] smallest-gap law, KN beta=2 vs dyn2 stored CUE (N=64, {len(dmin_cue_stored)} samples): "
      f"KS={ks1.statistic:.4f} p={ks1.pvalue:.3f}")

# fresh Haar spacings
sp_cue = []
for _ in range(600):
    g = adjacent_gaps(haar_eigenangles(N, rng))
    sp_cue.append(g)
sp_cue = np.concatenate(sp_cue) * N / (2 * np.pi)
sub = rng.choice(len(sp_kn), size=len(sp_cue), replace=False)
ks2 = stats.ks_2samp(sp_kn[sub], sp_cue)
print(f"[V1b] spacing distribution, KN beta=2 vs fresh Haar CUE (N=64): "
      f"KS={ks2.statistic:.4f} p={ks2.pvalue:.3f}")
print(f"      spacing means: KN={sp_kn.mean():.4f} CUE={sp_cue.mean():.4f} (both should be 1)")
print(f"      spacing var  : KN={sp_kn.var():.4f} CUE={sp_cue.var():.4f}")

# ---------------- (2) beta=1 KN vs direct COE at N=16
N = 16
M = 4000
sp_kn1, dmin_kn1, sp_coe, dmin_coe = [], [], [], []
for _ in range(M):
    g = adjacent_gaps(cbe_eigenangles(N, 1.0, rng)); sp_kn1.append(g); dmin_kn1.append(g.min())
    g = adjacent_gaps(coe_eigenangles(N, rng));      sp_coe.append(g); dmin_coe.append(g.min())
sp_kn1 = np.concatenate(sp_kn1) * N / (2 * np.pi)
sp_coe = np.concatenate(sp_coe) * N / (2 * np.pi)
ks3 = stats.ks_2samp(sp_kn1, sp_coe)
ks4 = stats.ks_2samp(np.array(dmin_kn1), np.array(dmin_coe))
print(f"[V2] beta=1: KN vs direct COE=V V^T at N=16 ({M} draws each): "
      f"spacings KS={ks3.statistic:.4f} p={ks3.pvalue:.3f}; dmin KS={ks4.statistic:.4f} p={ks4.pvalue:.3f}")
print(f"     spacing var: KN={sp_kn1.var():.4f} COE={sp_coe.var():.4f}")

# ---------------- (3) ODE vs coefficient bisection on KN samples
for beta in (1.0, 4.0):
    errs = []
    for _ in range(15):
        th = cbe_eigenangles(16, beta, rng)
        a = neg_lambda_ode(th)
        b = neg_lambda_coeff(th)
        errs.append(abs(a - b) / b)
    print(f"[V3] beta={beta}: ODE vs coeff-bisection rel err over 15 draws at N=16: "
          f"max={max(errs):.2e} median={np.median(errs):.2e}")

# ---------------- (4) tracked solver equals dyn2 solver
errs = []
for _ in range(10):
    th = cbe_eigenangles(24, 1.0, rng)
    a = neg_lambda_ode(th)
    b, idx = neg_lambda_ode_tracked(th)
    errs.append(abs(a - b) / a)
print(f"[V4] tracked vs dyn2 ODE solver: max rel diff = {max(errs):.2e}")
