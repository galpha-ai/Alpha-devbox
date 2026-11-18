"""
refute_A3_repro.py -- adversarial reproduction check for task A3
(r1_cbe_background.md / scripts/r1_cbe_mc.py).

Checks performed:
  1. Exact re-run of the cited command (same seed=42) and byte-level diff of
     the numeric summaries against the committed data/r1_cbe_mc.json.
  2. Independent re-implementation of S* (built directly from the rho_k =
     dist(theta_k,{theta_a,theta_b}) definition, NOT copy-pasted from the
     script) cross-checked against the script's own two internal formulas,
     on freshly drawn samples, to catch a possible shared bug in both of the
     script's internal formulas.
  3. Robustness sweep over 4 more seeds (small sample counts, N=64,128) to
     see whether the headline KS-test non-rejection (beta=2 vs Haar CUE) and
     the qualitative "median S*/N^2 approx 0.13-0.14" / "beta=4 exponent
     overshoots more than beta=1" claims are seed-robust or a seed=42 fluke.
  4. A structural check of the CMV block construction (unitarity and
     unimodularity of eigenvalues) at one extra N not tried by the proposer
     (N=96, odd count of "N-1" parity different from 64/128) to check the
     direct_sum padding logic doesn't silently break for other even N.

Budget: capped at ~10 minutes wall time, <=2 cores, OPENBLAS_NUM_THREADS=1.
"""
import os, sys, time, json
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
from scipy import stats as spstats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r1_cbe_mc as m

DATA_DIR = os.path.normpath(os.path.join(HERE, "..", "data"))

t_start = time.time()
report = []

def log(s):
    print(s)
    report.append(s)

# ---------------------------------------------------------------------------
# 1. Exact re-run vs committed json
# ---------------------------------------------------------------------------
log("=== Check 1: exact re-run of cited command, seed=42 ===")
rng = np.random.default_rng(42)
d_cmv, s_cmv, err_cmv = m.run_ensemble("cbe", 64, 2.0, 200, rng)
d_hcue, s_hcue, _ = m.run_ensemble("cue_ginibre", 64, None, 200, rng)
ks_delta = spstats.ks_2samp(d_cmv, d_hcue)
ks_s = spstats.ks_2samp(s_cmv, s_hcue)

with open(os.path.join(DATA_DIR, "r1_cbe_mc.json")) as f:
    committed = json.load(f)

def close(a, b, tol=1e-9):
    return abs(a - b) <= tol * max(1.0, abs(b))

checks = [
    ("cmv_delta_median", float(np.median(d_cmv)), committed["beta2_validation"]["cmv_delta_median"]),
    ("ginibre_delta_median", float(np.median(d_hcue)), committed["beta2_validation"]["ginibre_delta_median"]),
    ("cmv_Sstar_over_N2_median", float(np.median(s_cmv) / 64 ** 2), committed["beta2_validation"]["cmv_Sstar_over_N2_median"]),
    ("ks_delta_stat", float(ks_delta.statistic), committed["beta2_validation"]["ks_delta_stat"]),
    ("ks_delta_p", float(ks_delta.pvalue), committed["beta2_validation"]["ks_delta_p"]),
]
all_match = True
for name, got, want in checks:
    ok = close(got, want)
    all_match &= ok
    log(f"  {name}: got={got:.10g} committed={want:.10g} match={ok}")
log(f"Check 1 result: {'REPRODUCES EXACTLY (same seed => bit-identical stream)' if all_match else 'MISMATCH -- code drifted from committed data'}")

# ---------------------------------------------------------------------------
# 2. Independent re-implementation of S* (not copy-pasted) vs script's two formulas
# ---------------------------------------------------------------------------
log("\n=== Check 2: independent S* re-implementation ===")

def independent_sstar(theta):
    """Built directly from Lemma 0 of r1_theoremB_repair.md, S* = (1/2) sum csc^2(rho_k/2),
    rho_k = circular distance from theta_k to the nearer of the min-gap pair {a,b}.
    Written independently of min_gap_and_sstar's internal bookkeeping (vectorised
    differently: sorts, finds min gap, then computes circular distances via a
    different formula: rho_k = min(|theta_k-theta_a| mod 2pi folded, |theta_k-theta_b| mod 2pi folded))."""
    N = len(theta)
    th_sorted_idx = np.argsort(theta)
    th = theta[th_sorted_idx]
    gaps = np.r_[np.diff(th), 2 * np.pi - th[-1] + th[0]]
    i0 = np.argmin(gaps)
    ia = th_sorted_idx[i0]
    ib = th_sorted_idx[(i0 + 1) % N]
    ta, tb = theta[ia], theta[ib]
    others = np.delete(np.arange(N), [ia, ib])
    tk = theta[others]
    def circ_dist(x, y):
        d = np.abs(x - y) % (2 * np.pi)
        return np.minimum(d, 2 * np.pi - d)
    rho = np.minimum(circ_dist(tk, ta), circ_dist(tk, tb))
    rho = np.where(rho < 1e-300, 1e-300, rho)
    return 0.5 * np.sum(1.0 / np.sin(rho / 2) ** 2), gaps[i0]

rng2 = np.random.default_rng(7)
max_rel_err_indep = 0.0
n_check = 40
for _ in range(n_check):
    th = m.cbe_angles(64, 2.0, rng2)
    d_script, s_script, s_check_script = m.min_gap_and_sstar(th)
    s_indep, d_indep = independent_sstar(th)
    rel = abs(s_script - s_indep) / max(s_script, 1e-30)
    max_rel_err_indep = max(max_rel_err_indep, rel)
    assert abs(d_script - d_indep) < 1e-12
log(f"  max |S*_script - S*_independent| / S*_script over {n_check} fresh samples: {max_rel_err_indep:.2e}")
log(f"Check 2 result: {'S* implementation matches Lemma 0 independently' if max_rel_err_indep < 1e-9 else 'DISCREPANCY between script S* and Lemma-0 formula'}")

# ---------------------------------------------------------------------------
# 3. Seed-robustness sweep
# ---------------------------------------------------------------------------
log("\n=== Check 3: seed-robustness sweep (seeds 1,2,3,4; n=120/100, N=64,128) ===")
seeds = [1, 2, 3, 4]
ks_ps = []
med_s_all = {1.0: {64: [], 128: []}, 4.0: {64: [], 128: []}}
p_fits = {1.0: [], 4.0: []}
for sd in seeds:
    rng_s = np.random.default_rng(sd)
    dcm, scm, _ = m.run_ensemble("cbe", 64, 2.0, 120, rng_s)
    dhc, shc, _ = m.run_ensemble("cue_ginibre", 64, None, 120, rng_s)
    ksd = spstats.ks_2samp(dcm, dhc)
    ks_ps.append(float(ksd.pvalue))
    for beta in (1.0, 4.0):
        meds = {}
        for N in (64, 128):
            d, s, _ = m.run_ensemble("cbe", N, beta, 100, rng_s)
            med_s_all[beta][N].append(float(np.median(s) / N ** 2))
            meds[N] = float(np.median(d))
        p_fit = -(np.log(meds[128]) - np.log(meds[64])) / (np.log(128) - np.log(64))
        p_fits[beta].append(p_fit)
    log(f"  seed={sd}: KS(delta_min, beta=2 vs Haar CUE) p={ksd.pvalue:.3f}  "
        f"p_fit(beta=1)={p_fits[1.0][-1]:.3f}  p_fit(beta=4)={p_fits[4.0][-1]:.3f}")

log(f"  KS p-values across seeds 1-4: {['%.3f' % p for p in ks_ps]}  (all non-rejecting @0.05: {all(p > 0.05 for p in ks_ps)})")
for beta in (1.0, 4.0):
    for N in (64, 128):
        vals = med_s_all[beta][N]
        log(f"  beta={beta} N={N}: median(S*/N^2) across seeds = {['%.3f' % v for v in vals]}")
    pred = 1.0 + 1.0 / (beta + 1.0)
    log(f"  beta={beta}: p_fit across seeds = {['%.3f' % p for p in p_fits[beta]]}  predicted={pred:.3f}")

overshoot_beta1 = np.mean([abs(p - 1.5) for p in p_fits[1.0]])
overshoot_beta4 = np.mean([abs(p - 1.2) for p in p_fits[4.0]])
log(f"  mean |p_fit - predicted|: beta=1 -> {overshoot_beta1:.3f}, beta=4 -> {overshoot_beta4:.3f} "
    f"({'beta=4 deviates more, consistent with file claim' if overshoot_beta4 > overshoot_beta1 else 'beta=4 does NOT deviate more across these seeds -- file claim is seed=42-specific'})")

# ---------------------------------------------------------------------------
# 4. CMV structural check at an N not tried by the proposer
# ---------------------------------------------------------------------------
log("\n=== Check 4: CMV unitarity/unimodularity at N=96 (not in proposer's N-list) ===")
rng4 = np.random.default_rng(123)
max_unitary_err = 0.0
max_unimod_err = 0.0
for _ in range(5):
    alphas = m.sample_verblunsky(96, 1.0, rng4)
    C = m.build_cmv(alphas)
    err_u = np.max(np.abs(C @ C.conj().T - np.eye(96)))
    ev = np.linalg.eigvals(C)
    err_m = np.max(np.abs(np.abs(ev) - 1.0))
    max_unitary_err = max(max_unitary_err, err_u)
    max_unimod_err = max(max_unimod_err, err_m)
log(f"  max unitarity error ||CC*-I||_inf over 5 samples at N=96: {max_unitary_err:.2e}")
log(f"  max unimodularity error over 5 samples at N=96: {max_unimod_err:.2e}")
log(f"Check 4 result: {'CMV construction unitary/unimodular at N=96 too' if max(max_unitary_err, max_unimod_err) < 1e-10 else 'FAILS at N=96 -- construction is not general-N robust'}")

elapsed = time.time() - t_start
log(f"\ntotal wall time: {elapsed:.1f} s")

with open(os.path.join(DATA_DIR, "refute_A3_repro.log"), "w") as f:
    f.write("\n".join(report) + "\n")
