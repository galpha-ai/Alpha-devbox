#!/usr/bin/env python3
"""Drift diagnostics for FABLE task 001 / F2.

Reads f2_finite_sum_results.json (L = 1e3..1e6) and, if present,
f2_finite_sum_results_1e7.json (beyond-spec extra point), and

  1. fits J_L = J_inf + c/log L                   (least squares, the three requested points
                                                    1e3,1e4,1e5; also all available points)
  2. solves J_L = J_inf + c/log L + c'/log^2 L     exactly on three points (1e4,1e5,1e6 and
                                                    1e3,1e4,1e5) and least-squares on all points
  3. does the same for the S2-feature GAIN  Delta_L = J_L(fixed) - J_L(massonly), whose
     continuum value is known (+0.006903), and for the coincidence share J_full - J_clean.
  4. prime-sum discretisation test: sum_{p<=L} G(u_p)/p vs int_0^1 G(u) du/u for the
     S2-moment kernel G(u) = a u^2 (1-u)^a, to show the size of O(1/log L) prime-sum errors.

These fits are DIAGNOSTIC ONLY.  Three or five points on a slowly varying function cannot
determine a limit; the fitted J_inf values are reported to show how unstable the
extrapolation is, not as estimates of the true limit.
Output: f2_drift_fit_results.json;  run: python3 f2_drift_fit.py
"""
from __future__ import annotations
import json
import math
from pathlib import Path
import numpy as np
from scipy.integrate import quad

HERE = Path(__file__).resolve().parent


def load():
    res = json.loads((HERE/"f2_finite_sum_results.json").read_text())["results"]
    extra = HERE/"f2_finite_sum_results_1e7.json"
    if extra.exists():
        try:
            res = res + json.loads(extra.read_text())["results"]
        except Exception as exc:  # partial file while the run is in progress
            print("extra file unreadable:", exc)
    return sorted(res, key=lambda r: r["L"])


def fit_1(Ls, Js):
    """J = J_inf + c/logL, least squares."""
    X = np.vstack([np.ones(len(Ls)), 1/np.log(Ls)]).T
    sol, *_ = np.linalg.lstsq(X, Js, rcond=None)
    return {"J_inf": float(sol[0]), "c": float(sol[1]), "resid_max": float(np.max(np.abs(X@sol - Js)))}


def fit_2(Ls, Js):
    """J = J_inf + c/logL + c'/log^2 L (exact if 3 points, least squares otherwise)."""
    X = np.vstack([np.ones(len(Ls)), 1/np.log(Ls), 1/np.log(Ls)**2]).T
    sol, *_ = np.linalg.lstsq(X, Js, rcond=None)
    return {"J_inf": float(sol[0]), "c": float(sol[1]), "c2": float(sol[2]), "resid_max": float(np.max(np.abs(X@sol - Js)))}


def series_fits(name, Ls, vals, cont):
    Ls = np.array(Ls, dtype=float); vals = np.array(vals, dtype=float)
    out = {"L": Ls.tolist(), "values": vals.tolist(), "continuum": cont,
           "values_times_logL_minus_cont": (None if cont is None else ((vals - cont)*np.log(Ls)).tolist())}
    idx3 = [i for i, L in enumerate(Ls) if L in (1e3, 1e4, 1e5)]
    out["fit1_1e3_1e4_1e5"] = fit_1(Ls[idx3], vals[idx3])
    out["fit2_1e3_1e4_1e5"] = fit_2(Ls[idx3], vals[idx3])
    idx3b = [i for i, L in enumerate(Ls) if L in (1e4, 1e5, 1e6)]
    if len(idx3b) == 3:
        out["fit1_1e4_1e5_1e6"] = fit_1(Ls[idx3b], vals[idx3b])
        out["fit2_1e4_1e5_1e6"] = fit_2(Ls[idx3b], vals[idx3b])
    if len(Ls) >= 4:
        out["fit1_all"] = fit_1(Ls, vals)
        out["fit2_all"] = fit_2(Ls, vals)
        top = [i for i, L in enumerate(Ls) if L >= 1e5]
        if len(top) == 3:
            out["fit2_1e5_1e6_1e7"] = fit_2(Ls[top], vals[top])
    print(f"--- {name}: continuum = {cont}")
    for k, v in out.items():
        if k.startswith("fit"):
            print(f"   {k:18s} J_inf={v['J_inf']:+.6f} c={v['c']:+.4f}" + (f" c2={v['c2']:+.3f}" if 'c2' in v else "") + f" resid={v['resid_max']:.1e}")
    return out


def main():
    res = load()
    Ls = [r["L"] for r in res]
    out = {"status": "diagnostic fits only; not an extrapolation proof", "L": Ls, "series": {}}
    for trial in ("fixed", "massonly", "one", "one_ell1", "deg14"):
        for mode in ("full", "clean"):
            vals = [r["trials"][trial][mode]["J"] for r in res]
            cont = res[0]["trials"][trial]["continuum"]["J"]
            out["series"][f"{trial}/{mode}"] = series_fits(f"{trial}/{mode}", Ls, vals, cont)
    # S2 gain
    gain = [r["trials"]["fixed"]["full"]["J"] - r["trials"]["massonly"]["full"]["J"] for r in res]
    gcont = res[0]["trials"]["fixed"]["continuum"]["J"] - res[0]["trials"]["massonly"]["continuum"]["J"]
    out["series"]["S2_gain_fixed_minus_massonly/full"] = series_fits("S2 gain (fixed - massonly), full", Ls, gain, gcont)
    gain_c = [r["trials"]["fixed"]["clean"]["J"] - r["trials"]["massonly"]["clean"]["J"] for r in res]
    out["series"]["S2_gain_fixed_minus_massonly/clean"] = series_fits("S2 gain (fixed - massonly), clean", Ls, gain_c, gcont)
    # coincidence share
    share = [r["trials"]["fixed"]["full"]["J"] - r["trials"]["fixed"]["clean"]["J"] for r in res]
    out["series"]["coincidence_share_fixed(full-clean)"] = series_fits("fixed: J_full - J_clean", Ls, share, 0.0)
    # pieces vs continuum pieces
    pieces = {}
    for r in res:
        t = r["trials"]["fixed"]
        pieces[str(r["L"])] = {
            "full": t["full"]["pieces_over_2pi2N"], "clean": t["clean"]["pieces_over_2pi2N"],
            "continuum": {"D~M3/I": t["continuum"]["M3_over_I"], "O~M2b/I": t["continuum"]["M2b_over_I"], "C2~M2a/I": t["continuum"]["M2a_over_I"]}}
    out["pieces_fixed"] = pieces
    print("--- fixed trial pieces /(2 pi^2 N): D (diag), O (offdiag), C2 (<x,A^2x>) vs continuum M3/I, M2b/I, M2a/I")
    for L, pc in pieces.items():
        print(f"   L={L:>9s} full D={pc['full']['D']:.5f} O={pc['full']['O']:.5f} C2={pc['full']['C2']:.5f} | "
              f"clean D={pc['clean']['D']:.5f} O={pc['clean']['O']:.5f} C2={pc['clean']['C2']:.5f}")
    c = pieces[str(Ls[0])]["continuum"]
    print(f"   continuum      M3/I={c['D~M3/I']:.5f} M2b/I={c['O~M2b/I']:.5f} M2a/I={c['C2~M2a/I']:.5f}")
    # Perron comparison
    out["perron"] = {}
    for r in res:
        if "eigsh" in r:
            lam = r["eigsh"]["lambda_max"]
            out["perron"][str(r["L"])] = {"lambda_max": lam, "astra_lambda_max": None,
                                         "fixed_rayleigh": r["trials"]["fixed"]["full"]["lambda_rayleigh"],
                                         "fixed_over_max": r["trials"]["fixed"]["full"]["lambda_rayleigh"]/lam,
                                         "deg14_over_max": r["trials"]["deg14"]["full"]["lambda_rayleigh"]/lam}
    # S2 moments
    out["S2_moments"] = {str(r["L"]): r["S2_moments_fixed_ell"] for r in res}
    out["background_norm"] = {str(r["L"]): r["background_norm_fixed_ell"] for r in res}
    # prime-sum discretisation test
    a = (16/15)**2
    G = lambda u: a*u*u*(1 - u)**a
    integral = quad(lambda u: G(u)/u, 0, 1)[0]
    disc = {}
    for L in Ls:
        if L > 2*10**6:
            continue
        mask = np.ones(L + 1, dtype=bool); mask[:2] = False
        for p in range(2, math.isqrt(L) + 1):
            if mask[p]:
                mask[p*p::p] = False
        pr = np.flatnonzero(mask).astype(float)
        u = np.log(pr)/math.log(L)
        s = float(np.sum(G(u)/pr))
        disc[str(L)] = {"prime_sum": s, "integral": integral, "ratio": s/integral, "(ratio-1)*logL": (s/integral - 1)*math.log(L)}
        print(f"   prime-sum test L={L}: sum_p G(u_p)/p = {s:.6f}, integral = {integral:.6f}, ratio = {s/integral:.5f}")
    out["prime_sum_discretisation"] = disc
    (HERE/"f2_drift_fit_results.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
