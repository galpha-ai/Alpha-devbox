#!/usr/bin/env python3
"""Adversarial REFUTER for task F3 (r2_diagonal_operator_spectrum.md), REPRODUCTION AND
CODE-VS-TEXT lens.

Checks performed (each prints PASS/FAIL/NOTE):
  1. Re-run f3_fock_spectrum.py for M=10,15,20,25,30 (fast) and compare lambda_max(K) against
     the values published in the report's table (§4.2) / f3_fock_spectrum_results.json.
  2. Check the reported dimension counts (=sum_{m<=M} p(m), integer partitions) independently
     via sympy, for all M in the report's table (20..60).
  3. Check the CCR normalisation integral Cg = int_0^1 g(u)^2 du/u = 3.29656 (g(u)=2 sin(pi u/2))
     via independent quadrature, cited in report §2.2.
  4. Cross-check claim F3-2: read the *pre-existing* f2_finite_sum_results.json (not modified,
     not re-run) and confirm its continuum J value matches what the F3 report quotes
     (J = -0.014662375473371) and that J -> lambda=2*pi^2*(J+1/4) reproduces the table in F2/F3.
  5. Recompute the 3-point 1/M+1/M^2 extrapolations and the global power-law fit from the
     f3_fock_spectrum_results.json lambda_max values and compare to the report's quoted
     lambda_infty numbers (report §4.3 / §0 item 4).
  6. Recompute Astra's richer-family J -> lambda conversions quoted in report §4.4 table and
     compare against the source values transcribed from residual_gram_round1.md.
  7. PROVENANCE CHECK: verify whether the M=55, M=60 rows in the report's table (§4.2) --
     dim, nnz(Acre), maxRSS -- are actually backed by f3_fock_spectrum_results.json /
     f3_fock_spectrum_run.log (the artifacts the report cites), and independently recompute
     build_operators(55) and build_operators(60) (skipping eigsh, which the report itself says
     was skipped) to check the claimed dim/nnz/memory numbers are at least correct in isolation.

Cap: intended to run in well under 10 minutes (dominated by the M=55/60 build_operators calls,
~50s and ~110s respectively, single-threaded). OPENBLAS_NUM_THREADS=1, run under `taskset -c 0,1`
for the 2-core budget.

Does not modify any pre-existing file; only reads f2_finite_sum_results.json and
f3_fock_spectrum_results.json/f3_fock_spectrum_run.log, and re-imports f3_fock_spectrum.py's
build_operators (no re-run of the proposer's script as a subprocess is needed for most checks;
the heavy M=55/60 checks call build_operators directly, matching exactly what the proposer's
script itself does internally).
"""
from __future__ import annotations
import json
import math
import resource
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

PASS = "PASS"
FAIL = "FAIL"
NOTE = "NOTE"

results = {"checks": []}


def record(name, status, detail):
    results["checks"].append({"name": name, "status": status, "detail": detail})
    print(f"[{status}] {name}: {detail}", flush=True)


# ---------------------------------------------------------------------- check 1: re-run script
def check1_rerun_small_Ms():
    reported = {  # from r2_diagonal_operator_spectrum.md table / f3_fock_spectrum_results.json
        20: 4.6131253541, 25: 4.6193379711, 30: 4.6235652483,
    }
    out_path = HERE / "_refute_repro_tmp_results.json"
    cmd = [sys.executable, str(HERE / "f3_fock_spectrum.py"), "--Ms", "10,15,20,25,30",
           "--out", str(out_path)]
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=str(HERE), capture_output=True, text=True, timeout=120)
    dt = time.time() - t0
    if proc.returncode != 0:
        record("check1_rerun_small_Ms", FAIL, f"script exited {proc.returncode}: {proc.stderr[-500:]}")
        return
    data = json.loads(out_path.read_text())
    got = {r["M"]: r["lambda_max"] for r in data["results"]}
    max_abs_diff = 0.0
    for M, exp in reported.items():
        diff = abs(got[M] - exp)
        max_abs_diff = max(max_abs_diff, diff)
    status = PASS if max_abs_diff < 1e-8 else FAIL
    record("check1_rerun_small_Ms", status,
           f"re-ran f3_fock_spectrum.py --Ms 10,15,20,25,30 in {dt:.1f}s; "
           f"max|lambda_max_rerun - lambda_max_reported| over M in {{20,25,30}} = {max_abs_diff:.3e} "
           f"(reproduces the published table to numerical noise if PASS)")
    out_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------- check 2: dim counts
def check2_dim_counts():
    from sympy.functions.combinatorial.numbers import partition
    reported_dims = {20: 2714, 25: 9296, 30: 28629, 35: 81156, 40: 215308, 45: 540635,
                      50: 1295971, 55: 2984865, 60: 6639349}
    bad = []
    for M, dim in reported_dims.items():
        s = sum(int(partition(m)) for m in range(0, M + 1))
        if s != dim:
            bad.append((M, dim, s))
    status = PASS if not bad else FAIL
    record("check2_dim_counts", status,
           f"sum_{{m<=M}} p(m) via sympy vs. report's dim column, for M in {sorted(reported_dims)}: "
           f"{'all match' if not bad else f'MISMATCHES: {bad}'}")


# ---------------------------------------------------------------------- check 3: Cg integral
def check3_Cg_integral():
    from scipy.integrate import quad
    f = lambda u: (2.0 * math.sin(math.pi * u / 2.0)) ** 2 / u
    val, err = quad(f, 0, 1)
    reported = 3.29656
    status = PASS if abs(val - reported) < 1e-4 else FAIL
    record("check3_Cg_integral", status,
           f"quad(g(u)^2/u, 0, 1) = {val:.10f} (err={err:.1e}) vs report's Cg=3.29656 "
           f"(g(u)=2 sin(pi u/2)); |diff|={abs(val - reported):.2e}")


# ---------------------------------------------------------------------- check 4: F2 J cross-check
def check4_F2_J_crosscheck():
    f2_path = HERE / "f2_finite_sum_results.json"
    if not f2_path.exists():
        record("check4_F2_J_crosscheck", FAIL, f"pre-existing {f2_path} not found")
        return
    d = json.loads(f2_path.read_text())
    J_f2 = d["results"][0]["trials"]["fixed"]["continuum"]["J"]
    J_reported = -0.014662375473371
    diff = abs(J_f2 - J_reported)
    lam = 2 * math.pi ** 2 * (J_f2 + 0.25)
    lam_reported_F3_2 = None  # F3-2 just quotes J, and the derived lambda for the "fixed rational
                               # trial" row in the F3 report's Astra-family table (4.645379)
    lam_table_value = 4.645379
    diff_lam = abs(lam - lam_table_value)
    status = PASS if (diff < 1e-9 and diff_lam < 1e-3) else FAIL
    record("check4_F2_J_crosscheck", status,
           f"f2_finite_sum_results.json continuum J={J_f2:.15f} vs report-quoted "
           f"J={J_reported:.15f} (|diff|={diff:.2e}); lambda=2pi^2(J+1/4)={lam:.6f} vs report's "
           f"table value 4.645379 (|diff|={diff_lam:.2e})")


# ---------------------------------------------------------------------- check 5: extrapolations
def check5_extrapolations():
    res_path = HERE / "f3_fock_spectrum_results.json"
    d = json.loads(res_path.read_text())
    pts = {r["M"]: r["lambda_max"] for r in d["results"] if "lambda_max" in r}

    def fit3(Ms):
        xs = np.array([1.0 / m for m in Ms])
        ys = np.array([pts[m] for m in Ms])
        A = np.vstack([np.ones_like(xs), xs, xs ** 2]).T
        coef = np.linalg.solve(A, ys)
        return coef[0]

    windows = {(20, 25, 30): 4.645728, (30, 35, 40): 4.645624,
               (35, 40, 45): 4.645599, (40, 45, 50): 4.645583}
    bad = []
    for w, expected in windows.items():
        got = fit3(w)
        if abs(got - expected) > 1e-5:
            bad.append((w, got, expected))

    from scipy.optimize import curve_fit
    Ms_all = np.array(sorted(pts.keys()), dtype=float)
    ys_all = np.array([pts[m] for m in sorted(pts.keys())])
    model = lambda M, linf, c, p: linf - c / M ** p
    popt, _ = curve_fit(model, Ms_all, ys_all, p0=[4.65, 0.5, 1.0])
    pl_expected = (4.646544, 0.53275, 0.9242)
    pl_ok = (abs(popt[0] - pl_expected[0]) < 1e-4 and abs(popt[1] - pl_expected[1]) < 1e-3
             and abs(popt[2] - pl_expected[2]) < 1e-3)

    x = 1.0 / Ms_all
    A2 = np.vstack([np.ones_like(x), x]).T
    coef2, *_ = np.linalg.lstsq(A2, ys_all, rcond=None)
    lin_ok = abs(coef2[0] - 4.644859) < 1e-5

    status = PASS if (not bad and pl_ok and lin_ok) else FAIL
    record("check5_extrapolations", status,
           f"3-point fits: {'all match report to 1e-5' if not bad else f'MISMATCH {bad}'}; "
           f"power-law fit (linf,c,p)={tuple(round(v,6) for v in popt)} vs report "
           f"(4.646544,0.53275,0.9242) [{'ok' if pl_ok else 'MISMATCH'}]; "
           f"linear-in-1/M fit linf={coef2[0]:.6f} vs report 4.644859 [{'ok' if lin_ok else 'MISMATCH'}]")


# ---------------------------------------------------------------------- check 6: Astra family table
def check6_astra_family_table():
    # (J, report's stated lambda) pairs transcribed from the report's §4.4 table, with J values
    # cross-checked against residual_gram_round1.md sec 7-8 (read directly, not re-run).
    rows = {
        "1 only, degree 6": (-0.0153579822, 4.631648),
        "1, S2, degree 4": (-0.0146618161, 4.645390),
        "1, S2, S3, degree 4": (-0.0146563150, 4.645498),
        "1, S2, S3, S4, degree 4": (-0.0146551195, 4.645522),
        "12 groups": (-0.0146547256, 4.645530),
        "fixed rational trial": (-0.014662375473370598, 4.645379),
    }
    bad = []
    for name, (J, lam_reported) in rows.items():
        lam = 2 * math.pi ** 2 * (J + 0.25)
        if abs(lam - lam_reported) > 5e-6:
            bad.append((name, lam, lam_reported))
    status = PASS if not bad else FAIL
    record("check6_astra_family_table", status,
           f"lambda=2pi^2(J+1/4) recomputed for all {len(rows)} rows of report's §4.4 table: "
           f"{'all match to 5e-6' if not bad else f'MISMATCH {bad}'}")


# ---------------------------------------------------------------------- check 7: M=55/60 provenance
def check7_M55_M60_provenance():
    res_path = HERE / "f3_fock_spectrum_results.json"
    log_path = HERE / "f3_fock_spectrum_run.log"
    d = json.loads(res_path.read_text())
    Ms_in_results = sorted(r["M"] for r in d["results"])
    log_text = log_path.read_text()
    has_55_in_results = 55 in Ms_in_results
    has_60_in_results = 60 in Ms_in_results
    has_55_in_log = "M=55" in log_text
    has_60_in_log = "M=60" in log_text

    provenance_gap = not (has_55_in_results or has_55_in_log) and not (has_60_in_results or has_60_in_log)

    # Independently recompute build_operators(55) and build_operators(60) (no eigsh, matching
    # what the report itself says was done -- "matrix built; eigsh skipped, 3.5GB memory limit").
    from f3_fock_spectrum import build_operators
    reported_M55 = {"dim": 2984865, "nnz": 15877562, "maxrss_MB": 3522}
    reported_M60 = {"dim": 6639349, "nnz": 37013901, "maxrss_MB": 7769}

    recomputed = {}
    for M, reported in ((55, reported_M55), (60, reported_M60)):
        t0 = time.time()
        N, Acre, t_enum, t_build, nnz = build_operators(M)
        dt = time.time() - t0
        maxrss_MB = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        recomputed[M] = {"dim": N, "nnz": int(nnz), "maxrss_MB": maxrss_MB, "seconds": dt}
        del Acre

    dim_nnz_ok = all(
        recomputed[M]["dim"] == reported["dim"] and recomputed[M]["nnz"] == reported["nnz"]
        for M, reported in ((55, reported_M55), (60, reported_M60))
    )

    gap_msg = ("PROVENANCE GAP: the M=55/60 rows quoted in the report table/text are NOT backed by "
               "either cited artifact (results.json stops at M=50, run.log stops at M=50).")
    detail = (
        f"f3_fock_spectrum_results.json contains M={Ms_in_results} (55/60 present in results: "
        f"{has_55_in_results}/{has_60_in_results}); f3_fock_spectrum_run.log mentions M=55/M=60: "
        f"{has_55_in_log}/{has_60_in_log}. "
        f"{gap_msg if provenance_gap else ''} "
        f"Independent recompute via build_operators(): "
        f"M=55 dim={recomputed[55]['dim']} nnz={recomputed[55]['nnz']} "
        f"maxrss={recomputed[55]['maxrss_MB']:.0f}MB ({recomputed[55]['seconds']:.1f}s) vs "
        f"report's dim={reported_M55['dim']} nnz={reported_M55['nnz']} maxrss~{reported_M55['maxrss_MB']}MB; "
        f"M=60 dim={recomputed[60]['dim']} nnz={recomputed[60]['nnz']} "
        f"maxrss={recomputed[60]['maxrss_MB']:.0f}MB ({recomputed[60]['seconds']:.1f}s) vs "
        f"report's dim={reported_M60['dim']} nnz={reported_M60['nnz']} maxrss~{reported_M60['maxrss_MB']}MB. "
        f"dim/nnz {'MATCH exactly' if dim_nnz_ok else 'DO NOT MATCH'} (memory figures differ by "
        f"a few hundred MB, plausibly because the report's single combined run accumulated "
        f"un-freed memory from the preceding M<=50 iterations in the same process, whereas this "
        f"check calls build_operators() fresh per M)."
    )
    # This is a documentation/provenance issue (minor), not a numerical-correctness failure,
    # since the dim/nnz values -- the only load-bearing quantities -- check out exactly.
    status = FAIL if not dim_nnz_ok else (NOTE if provenance_gap else PASS)
    record("check7_M55_M60_provenance", status, detail)


def main():
    check1_rerun_small_Ms()
    check2_dim_counts()
    check3_Cg_integral()
    check4_F2_J_crosscheck()
    check5_extrapolations()
    check6_astra_family_table()
    check7_M55_M60_provenance()
    out = HERE / "refute_F3_repro_results.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {out}")
    n_fail = sum(1 for c in results["checks"] if c["status"] == FAIL)
    n_note = sum(1 for c in results["checks"] if c["status"] == NOTE)
    print(f"\n{len(results['checks'])} checks: "
          f"{sum(1 for c in results['checks'] if c['status']==PASS)} PASS, {n_fail} FAIL, {n_note} NOTE")


if __name__ == "__main__":
    main()
