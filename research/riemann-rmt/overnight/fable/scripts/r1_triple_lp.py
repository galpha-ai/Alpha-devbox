"""
r1_triple_lp.py -- Task C1(d): do triple correlations (Rudnick-Sarnak band Sum|xi_i| < 2) raise the
pair-correlation ceiling for the simple-zero proportion?

Lattice model (see r1_lattice_common.py): P points with integer multiplicities on Z/(MP).
Hierarchy computed at each (P, M):
  L1  pair measure LP with F >= 0                       (Cheer-Goldston class certificate value)
  L2  L1 + Yamada interval integrality
  L3  pair+triple tensor relaxation, T >= 0, marginals, integrality inequalities, no RS data
  L3R L3 + RS triple data (E S_k1 S_k2 S_k3 = 0 in band)
  L3S/L3RS  the same with localized moment-matrix PSD constraints (cvxpy/Clarabel)
  L4  exact LP over all multisets (honest point process), pair data only
  L5  exact LP over all multisets, pair + RS triple data
Monotonicity expected: L1 <= L2 <= L3 <= L3S <= L4  and  L3R <= L3RS <= L5;  L4 <= L5.
The quantity of interest is L5 - L4 (what triple *data* buys over an honest pair-only adversary)
and L4 - L1 (what integrality/higher positivity buys), as functions of (P, M).
Output: data/r1_triple_lp.json (one record per size).
"""
import json, sys, time
import numpy as np
from r1_lattice_common import pair_lp, triple_lp, enumerate_stats, exact_lp

OUT = "/home/user/Alpha-devbox/research/riemann-rmt/overnight/fable/data/"


def run(P, M, do_exact=True, do_sdp=True):
    rec = dict(P=P, M=M, L=P * M)
    t = time.time()
    rec["L1"] = pair_lp(P, M, positivity=True)["delta"]
    rec["L1_noFpos"] = pair_lp(P, M, positivity=False)["delta"]
    rec["L2"] = pair_lp(P, M, positivity=True, yamada=True, yamada_unions=M)["delta"]
    r = triple_lp(P, M, rs_data=False); rec["L3"] = r["value"]; rec["L3_A"] = r["A"]; rec["nT"] = r["nT"]
    r = triple_lp(P, M, rs_data=True); rec["L3R"] = r["value"]; rec["L3R_A"] = r["A"]; rec["n_rs"] = r["rs"]
    rec["t_lp"] = time.time() - t
    if do_sdp:
        t = time.time()
        try:
            r = triple_lp(P, M, rs_data=False, sdp=True); rec["L3S"] = r["value"]; rec["L3S_status"] = r["status"]
            r = triple_lp(P, M, rs_data=True, sdp=True); rec["L3RS"] = r["value"]; rec["L3RS_status"] = r["status"]
        except Exception as e:
            rec["sdp_error"] = str(e)
        rec["t_sdp"] = time.time() - t
    if do_exact:
        t = time.time()
        st = enumerate_stats(P, M, verbose=False)
        rec["n_configs"] = st["n_configs"]; rec["n_columns"] = int(st["cols"].shape[0])
        r4 = exact_lp(st, use_rs=False); r5 = exact_lp(st, use_rs=True)
        rec["L4"] = r4["value"]; rec["L4_A"] = r4.get("A"); rec["L4_B"] = r4.get("B")
        rec["L5"] = r5["value"]; rec["L5_A"] = r5.get("A"); rec["L5_B"] = r5.get("B")
        rec["L5_support"] = r5.get("support")
        rec["t_exact"] = time.time() - t
    return rec


if __name__ == "__main__":
    sizes = [(4, 3), (5, 3), (6, 3), (7, 3), (8, 3),
             (4, 4), (5, 4), (6, 4), (7, 4),
             (4, 6), (5, 6), (6, 6),
             (4, 8), (5, 8), (4, 12), (5, 10), (4, 16), (4, 24)]
    if len(sys.argv) > 1:
        sizes = [tuple(map(int, a.split(","))) for a in sys.argv[1:]]
    results = []
    for (P, M) in sizes:
        L = P * M
        do_exact = True
        rec = run(P, M, do_exact=do_exact, do_sdp=(L <= 72))
        results.append(rec)
        print(json.dumps(rec), flush=True)
        with open(OUT + "r1_triple_lp.json", "w") as f:
            json.dump(results, f, indent=1)
