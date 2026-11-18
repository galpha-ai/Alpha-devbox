"""r2_ff_haar_depth.py -- Task B5 (6): depth law across the classical compact groups.

For G in {U(N), USp(2N), SO(2N), SO(2N+1), O^-(2N+2)} (N = number of free eigenangles) and
N in {8, 16, 32, 64, 128}: draw exact Haar samples (r2_ff_depth_core samplers), compute the
depth D of det(z - Theta) under the backward heat flow with the ODE solver (cross-checks: np.roots
bisection for bulk collisions at M <= 33; the exact high-precision scalar criterion P_s(+-1) = 0,
resp. P~_s(+-1) = 0 with the forced root stripped, for every edge collision at any M), and record delta_min, rho = D/(-log cos(delta_min/2)), the collision type
(bulk / edge+ / edge-) and localisation (did the smallest initial gap close first?).

Fits: log median(D) vs log N (expected slope -8/3 for every class, from the beta = 2 bulk),
log median(N^2 D) vs log N (expected -2/3), and the comparison of 8 N^{8/3} D with the CUE limit
law G^2, P(G > x) = exp(-x^3/(72 pi)), and with the class prediction G^2/4 for the symmetric
classes (N free gaps at density 2N/2pi).

Usage: python3 r2_ff_haar_depth.py [n_samples] [n_workers]
Outputs: ../data/r2_ff_haar_depth.npz (all samples), ../data/r2_ff_haar_depth_summary.json,
         and a printed table (tee to ../data/r2_ff_haar_depth.log).
"""
import sys, os, json, time
import numpy as np
from math import pi, log
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from r2_ff_depth_core import *

N_SAMPLES = int(sys.argv[1]) if len(sys.argv) > 1 else 400
N_WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 2
SIZES = [8, 16, 32, 64, 128]
GROUPS_RUN = ["U", "USp", "SO_even", "SO_odd", "O_minus"]


def job(args):
    group, N, seed, n = args
    rng = np.random.default_rng([seed, N, hash(group) % 1000])
    if N == 128:
        n = min(n, 300)
    rows = []
    t0 = time.time()
    for i in range(n):
        fr = free_angles(sample_group(group, N, rng), group, N)
        o = depth_ode(fr, group)
        cross = np.nan
        if o["ctype"] in ("edge+", "edge-"):
            try:
                cross = edge_time_exact(fr, group, +1 if o["ctype"] == "edge+" else -1, s_guess=o["D"])
            except Exception:
                cross = np.nan
        elif o["M"] <= 33 and i < 40:
            cross = depth_from_angles(fr, group, classify=False)["D"]
        rows.append((o["D"], o["delta_min"], o["rho"], {"bulk": 0, "edge+": 1, "edge-": 2}.get(o["ctype"], 3),
                     float(o["is_min_gap"]), o["gap_initial"], cross, o["nfev"]))
    return group, N, np.array(rows), time.time() - t0


if __name__ == "__main__":
    tasks = [(g, N, 20260905, N_SAMPLES) for g in GROUPS_RUN for N in SIZES]
    tasks.sort(key=lambda t: -matrix_size(t[0], t[1]))   # big ones first
    results = {}
    with Pool(N_WORKERS) as pool:
        for group, N, arr, dt in pool.imap_unordered(job, tasks):
            results[(group, N)] = arr
            D = arr[:, 0]
            print(f"done {group:8s} N={N:3d}: {len(D)} samples in {dt:.0f}s; median D = {np.median(D):.4e}, "
                  f"median 8N^(8/3)D = {8*N**(8/3)*np.median(D):.3f}, edge fraction = {np.mean(arr[:,3]>=1):.3f}, "
                  f"localisation = {np.mean(arr[:,4]):.3f}", flush=True)
    np.savez(os.path.join(HERE, "..", "data", "r2_ff_haar_depth.npz"),
             **{f"{g}_{N}": arr for (g, N), arr in results.items()})

    summary = {}
    print("\n=== summary: median D, median 8N^(8/3)D, edge fraction, localisation, KS of 8N^(8/3)D/c vs G^2 law ===")
    print(f"{'group':8s} {'N':>4s} {'M':>4s} {'n':>4s} {'med D':>11s} {'med 8N^8/3 D':>13s} {'q25':>8s} {'q75':>8s} {'edge':>6s} {'loc':>6s} {'med rho':>8s} {'KS(c=1)':>8s} {'KS(c=1/4)':>9s} {'cross':>8s}")
    for g in GROUPS_RUN:
        for N in SIZES:
            arr = results[(g, N)]
            D = arr[:, 0]; x = 8 * N ** (8 / 3) * D
            ks1 = ks_against_cdf(x, cue_G2_cdf); ks4 = ks_against_cdf(4 * x, cue_G2_cdf)
            cr = arr[:, 6]; ok = ~np.isnan(cr)
            cross = float(np.max(np.abs(cr[ok] - D[ok]) / D[ok])) if ok.any() else float("nan")
            summary[f"{g}_{N}"] = dict(n=int(len(D)), M=matrix_size(g, N), med_D=float(np.median(D)),
                                       med_scaled=float(np.median(x)), q25=float(np.quantile(x, .25)), q75=float(np.quantile(x, .75)),
                                       edge_frac=float(np.mean(arr[:, 3] >= 1)), edge_plus=float(np.mean(arr[:, 3] == 1)),
                                       edge_minus=float(np.mean(arr[:, 3] == 2)), localisation=float(np.mean(arr[:, 4])),
                                       med_rho=float(np.median(arr[:, 2])), ks_c1=ks1, ks_c14=ks4, cross_max_rel=cross,
                                       mean_logD=float(np.mean(np.log(D))))
            print(f"{g:8s} {N:4d} {matrix_size(g,N):4d} {len(D):4d} {np.median(D):11.4e} {np.median(x):13.3f} {np.quantile(x,.25):8.3f} {np.quantile(x,.75):8.3f} "
                  f"{np.mean(arr[:,3]>=1):6.3f} {np.mean(arr[:,4]):6.3f} {np.median(arr[:,2]):8.4f} {ks1:8.3f} {ks4:9.3f} {cross:8.1e}")
    print("\n=== exponent fits (least squares on log median D vs log N; also mean log D) ===")
    fits = {}
    for g in GROUPS_RUN:
        Ns = np.array(SIZES, float)
        med = np.array([summary[f"{g}_{N}"]["med_D"] for N in SIZES])
        mlog = np.array([summary[f"{g}_{N}"]["mean_logD"] for N in SIZES])
        sl_all = np.polyfit(np.log(Ns), np.log(med), 1)[0]
        sl_big = np.polyfit(np.log(Ns[2:]), np.log(med[2:]), 1)[0]
        sl_mean = np.polyfit(np.log(Ns), mlog, 1)[0]
        local = np.diff(np.log(med)) / np.diff(np.log(Ns))
        fits[g] = dict(slope_all=float(sl_all), slope_N32_128=float(sl_big), slope_meanlog=float(sl_mean), local=local.tolist())
        print(f"{g:8s}: slope(all N) = {sl_all:.3f}, slope(N>=32) = {sl_big:.3f}, slope(mean log D) = {sl_mean:.3f}; local slopes {np.round(local,3)}   [predicted -8/3 = -2.667; N^2 D slope = slope+2]")
    with open(os.path.join(HERE, "..", "data", "r2_ff_haar_depth_summary.json"), "w") as f:
        json.dump(dict(summary=summary, fits=fits, n_samples=N_SAMPLES, sizes=SIZES, groups=GROUPS_RUN), f, indent=1)
    print("saved ../data/r2_ff_haar_depth.npz and ../data/r2_ff_haar_depth_summary.json")
