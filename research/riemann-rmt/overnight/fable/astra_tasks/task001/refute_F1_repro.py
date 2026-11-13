"""REFUTER (lens: reproduction & code-vs-text) for FABLE task001 / F1 arithmetic transfer.

Re-derives / re-runs (at reduced size, budget < 10 min) the quantities the proposer's report
(task001_F1_arithmetic_transfer.md) cites as evidence, using the proposer's OWN scripts'
functions (imported, never executing their __main__ blocks, so no pre-existing file is
touched or overwritten), and cross-checks the report's quoted numbers against:
  (a) the already-present result JSON files (f1_*_results.json) -- were they read correctly?
  (b) an independent from-scratch re-computation at reduced L/P -- does the code reproduce
      itself and match the report's prose, or did the report mis-transcribe a number?

Focus: the report's headline "two-term normalisation ratio" sequence in Summary point 1 / S2
(quoted as 1.002005, 1.000396, 1.0000833, 1.0000617 at L=10^4..10^7, v=1), since this is the
single number sequence the report calls "the strongest, cleanest numerical confirmation in
this report" and builds an error-ratio argument on.

Output: refute_F1_repro_results.json.  This file (refute_F1_repro.py) and its results JSON are
new files written by the refuter, not modifications of any proposer file.
"""
from __future__ import annotations
import json, sys, time
from math import gamma, log, floor
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from f1_common import ELL, sieve_d_S, euler_constants  # noqa: E402

t0 = time.time()
ell = ELL
a = ell * ell
EULER_GAMMA = 0.57721566490153286
out = {"lens": "reproduction and code-vs-text", "checks": []}


def add(name, passed, detail):
    out["checks"].append({"name": name, "passed": bool(passed), "detail": detail})
    print(("PASS " if passed else "FAIL "), name, "-", detail, flush=True)


# ---------------------------------------------------------------------------
# Check 1: f1_common self-test (exact, cheap) -- code matches its own docstring definitions.
d, S = sieve_d_S(1000)
ok = (abs(d[2] - ell) < 1e-15 and abs(d[4] - ell * (ell + 1) / 2) < 1e-15
      and abs(d[8] - ell * (ell + 1) * (ell + 2) / 6) < 1e-15
      and abs(d[12] - d[4] * d[3]) < 1e-15 and abs(d[6] - ell * ell) < 1e-15
      and abs(S[12] - (log(2) ** 2 + log(3) ** 2)) < 1e-12 and abs(S[8] - log(2) ** 2) < 1e-12)
add("f1_common self-test", ok, "d_ell/S~ sieve matches hand definitions to 1e-12..1e-15")

# ---------------------------------------------------------------------------
# Check 2: independently recompute Sigma0/1/2 and norm_ratio_2term at v=1, L in {1e4,1e5,1e6}
# (1e7 skipped here for time; already cross-checked against the JSON directly, see check 2b).
LMAX = 10 ** 6
d, St = sieve_d_S(LMAX, ell)
n = np.arange(LMAX + 1, dtype=float)
wt = np.zeros(LMAX + 1); wt[1:] = d[1:] ** 2 / n[1:]
ec = euler_constants(LMAX, ell)
C = ec["C_ell"]; GpG = ec["GprimeOverG"]

recomputed = {}
for L in (10 ** 4, 10 ** 5, 10 ** 6):
    logL = log(L)
    x = L
    lx = log(x)
    w0 = wt[:x + 1]
    s0 = float(np.sum(w0))
    one = C * lx ** a / gamma(a + 1)
    two = one + C * (a * EULER_GAMMA + GpG) * lx ** (a - 1) / gamma(a)
    recomputed[L] = {"norm_ratio_1term": s0 / one, "norm_ratio_2term": s0 / two}

reported_two_term_table = [1.002005, 1.000396, 1.0000833, 1.0000617]  # report's Summary pt.1 / section 2 sequence, L=1e4..1e7
mismatch_1e4 = abs(recomputed[10**4]["norm_ratio_2term"] - reported_two_term_table[0]) > 1e-4
mismatch_1e5 = abs(recomputed[10**5]["norm_ratio_2term"] - reported_two_term_table[1]) > 1e-4
add("independent recompute of norm_ratio_2term at L=1e4 (v=1) vs report's quoted 1.002005",
    not mismatch_1e4,
    f"recomputed (v=1, L=1e4) = {recomputed[10**4]['norm_ratio_2term']:.6f}; report quotes 1.002005 -- "
    f"{'MATCH' if not mismatch_1e4 else 'MISMATCH'}")
add("independent recompute of norm_ratio_2term at L=1e5 (v=1) vs report's quoted 1.000396",
    not mismatch_1e5,
    f"recomputed (v=1, L=1e5) = {recomputed[10**5]['norm_ratio_2term']:.6f}; report quotes 1.000396 -- "
    f"{'MATCH' if not mismatch_1e5 else 'MISMATCH'}")

# ---------------------------------------------------------------------------
# Check 2b: read the proposer's OWN f1_moment_results.json (already present, not modified) and
# show which (L, v) rows the report's quoted numbers actually came from.
mr = json.loads((HERE / "f1_moment_results.json").read_text())
rows_by_Lv = {(r["L"], r["v"]): r["norm_ratio_2term"] for r in mr["rows"]}
lookup = {}
for (L, v), val in rows_by_Lv.items():
    lookup.setdefault(round(val, 6), []).append((L, v))
found_sources = {}
for target in reported_two_term_table:
    # find the (L,v) row(s) in the proposer's own JSON whose norm_ratio_2term matches this quoted number to 1e-5
    matches = [(L, v) for (L, v), val in rows_by_Lv.items() if abs(val - target) < 1e-5]
    found_sources[target] = matches
add("trace report's quoted two-term-ratio numbers to actual rows of f1_moment_results.json",
    all(len(v) > 0 for v in found_sources.values()),
    json.dumps({str(k): v for k, v in found_sources.items()}))

v1_L_values = [(10 ** 4, 1.0), (10 ** 5, 1.0), (10 ** 6, 1.0), (10 ** 7, 1.0)]
actual_v1_sequence = [rows_by_Lv[key] for key in v1_L_values]
add("does report's quoted 4-number sequence equal the actual v=1 sequence across L=1e4..1e7 in f1_moment_results.json?",
    all(abs(actual_v1_sequence[i] - reported_two_term_table[i]) < 1e-5 for i in range(4)),
    f"actual v=1 sequence (L=1e4,1e5,1e6,1e7) = {[round(x,7) for x in actual_v1_sequence]}; "
    f"report's quoted sequence = {reported_two_term_table}. "
    "First two entries of the report's sequence match the (L=1e4, v=0.5) and (L=1e4, v=0.75) rows "
    "instead of the (L=1e4, v=1.0) and (L=1e5, v=1.0) rows -- i.e. the report mixes rows from "
    "different v at the same L=1e4 into what is presented as a single v=1 sequence across four "
    "decades of L. The last two entries (L=1e6, L=1e7 at v=1) are correctly transcribed.")

# ---------------------------------------------------------------------------
# Check 3: independently re-derive C_ell, kappa1 at reduced P and compare with f1_sd_expansion_results.json
ec_full = json.loads((HERE / "f1_sd_expansion_results.json").read_text())["constants"]
ec_small = euler_constants(10 ** 6, ell)
add("C_ell reproducibility (P=1e6 here vs P=1e7 in f1_sd_expansion_results.json)",
    abs(ec_small["C_ell"] - ec_full["C"]) < 1e-4,
    f"C_ell(P=1e6)={ec_small['C_ell']:.8f} vs reported C={ec_full['C']:.8f} (diff {abs(ec_small['C_ell']-ec_full['C']):.2e})")

# ---------------------------------------------------------------------------
# Check 4: independently re-run the insertion decomposition at a small L, importing the
# proposer's own functions (module import only -- __main__ guard means no file is overwritten),
# and compare against the report's L=1000 table row / f1_insertion_results.json.
import importlib.util
spec = importlib.util.spec_from_file_location("f1_insertion_decomposition", HERE / "f1_insertion_decomposition.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)  # runs module top level (imports + function defs only; __main__ guarded)
from f1_common import trial_fg  # noqa: E402

L_test = 1000
d_t, St_t = sieve_d_S(L_test, ell)
nn = np.arange(1, L_test + 1, dtype=float)
v_t = np.log(nn) / log(L_test); S2_t = St_t[1:] / log(L_test) ** 2
f_t, g_t = trial_fg(v_t)
r_t = d_t[1:] * (f_t + g_t * S2_t)
ops_t = mod.make_ops(L_test)
res_t = mod.decompose(L_test, ops_t, r_t)

ir = json.loads((HERE / "f1_insertion_results.json").read_text())
ref_row = next(rr for rr in ir["runs"] if rr["L"] == 1000 and rr["H"] == "trial_f_plus_gS")
keys_to_check = ["alpha_over_D", "beta_over_D", "gamma_over_D", "delta_over_D", "eps_over_D", "check_sum", "J_L"]
diffs = {k: abs(res_t[k] - ref_row[k]) for k in keys_to_check}
add("independent re-run of f1_insertion_decomposition.decompose at L=1000 matches f1_insertion_results.json",
    all(diff < 1e-9 for diff in diffs.values()),
    json.dumps({k: {"recomputed": res_t[k], "reported_json": ref_row[k], "diff": diffs[k]} for k in keys_to_check}))
add("exact 5-way identity alpha+beta+gamma+delta+eps=T holds in independent re-run at L=1000",
    abs(res_t["check_sum"]) < 1e-10,
    f"check_sum = {res_t['check_sum']:.2e}")

# report's L=1000 table row values (section 5): alpha/D 0.04474, beta/D 0.08207, gamma/D 3.82e-3, delta/D 0.01714, eps/D 0.05024
report_l1000 = {"alpha_over_D": 0.04474, "beta_over_D": 0.08207, "gamma_over_D": 3.82e-3, "delta_over_D": 0.01714, "eps_over_D": 0.05024}
add("report's printed L=1000 table row (section 5) matches independent recomputation to quoted precision",
    all(abs(res_t[k] - report_l1000[k]) < 6e-4 for k in report_l1000),
    json.dumps({k: {"recomputed": round(res_t[k], 5), "report_table": report_l1000[k]} for k in report_l1000}))

# ---------------------------------------------------------------------------
# Check 5: sanity check the operator entry formula against the task prompt's A[qm,m] definition,
# by reading the source line directly (code-vs-text check on the exact formula string).
src = (HERE / "f1_insertion_decomposition.py").read_text()
formula_present = "2 * sin(pi / 2 * log(q) / logL) / (e * sqrt(q))" in src
add("A[qm,m] formula in f1_insertion_decomposition.py matches task prompt's A[qm,m]=2 sin((pi/2) log q/log L)/(e sqrt q)",
    formula_present, "grep of make_ops() found the exact formula string" if formula_present else "formula string not found verbatim")

out["seconds"] = time.time() - t0
n_fail = sum(1 for c in out["checks"] if not c["passed"])
out["n_checks"] = len(out["checks"]); out["n_failed"] = n_fail
Path(HERE / "refute_F1_repro_results.json").write_text(json.dumps(out, indent=2, default=str))
print(f"\ndone: {len(out['checks'])} checks, {n_fail} failed, {out['seconds']:.1f}s")
