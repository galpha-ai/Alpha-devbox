"""fab_phase.py — orchestrator's own diagnosis of the signed-sieve phase structure.

val(beta) = max { S2 - m S1 - beta D(w) : w in W2L, S1 = 1 },  D(w) = sum_{w_c<0} |w_c| G(c).
Structure: val is a max of affine functions of beta => convex, non-increasing, piecewise linear.
Two critical prices:
  beta_unb = sup{ Phi(u)/D(u) : S1(u)=0, D(u)>0 }  (below it the LP is unbounded)
  beta_*   = price where the optimal vertex stops being the D=0 (classical) one
Window (beta_unb, beta_*) = prices at which signed weights give a FINITE STRICT gain.
"""
import sys, json, numpy as np
sys.path.insert(0, "/tmp/claude-0/-home-user-Alpha-devbox/00b3b5f7-f917-5641-a9be-c6a8f38f5cd7/scratchpad")
from fractions import Fraction as F
from sgn1_model import build_model, model_summary, primes_upto
from sgn1_solve import solve_beta_float, floatize


def analyze(H, feat, big, m, L=1, label=""):
    M = build_model(tuple(H), feat, big, m=m, L=L)
    Phi, N1, Nnu, G, a = floatize(M)
    nc, dim = Phi.shape
    out = dict(label=label, H=list(H), feat=feat, big_max=max(big), m=m, L=L,
               ncell=nc, dim=dim, nG0=int((G == 0).sum()))
    rp = solve_beta_float(M, 0, pos_only=True)
    if rp["status"] != "optimal":
        out["status"] = "pos_" + rp["status"]; return out, M
    vpos = rp["val"]; out["val_pos"] = vpos

    # bracket beta_unb by bisection on boundedness
    lo, hi = 1e-6, 1024.0
    r = solve_beta_float(M, hi)
    if r["status"] != "optimal":
        out["status"] = "unbounded_everywhere"; return out, M
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        rm = solve_beta_float(M, mid)
        if rm["status"] == "optimal":
            hi = mid
        else:
            lo = mid
        if hi - lo < 1e-9:
            break
    beta_unb = 0.5 * (lo + hi)
    out["beta_unb"] = beta_unb

    # beta_*: smallest beta with D=0 at optimum. val(beta) convex pw-linear.
    lo2, hi2 = beta_unb * (1 + 1e-9), 1024.0
    for _ in range(80):
        mid = 0.5 * (lo2 + hi2)
        rm = solve_beta_float(M, mid)
        if rm["status"] == "optimal" and rm["D"] <= 1e-11 and rm["val"] <= vpos + 1e-11:
            hi2 = mid
        else:
            lo2 = mid
        if hi2 - lo2 < 1e-10 * max(1, hi2):
            break
    beta_star = 0.5 * (lo2 + hi2)
    out["beta_star"] = beta_star
    # certified line through the signed vertex just below beta_*
    bt = beta_unb + 0.55 * (beta_star - beta_unb)
    rs = solve_beta_float(M, bt)
    if rs["status"] == "optimal" and rs["D"] > 1e-12:
        Phi_ray, D_ray = rs["Phi_obj"], rs["D"]
        out["signed_vertex"] = dict(beta=bt, val=rs["val"], Phi=Phi_ray, D=D_ray,
                                    negmass=float(np.sum(np.abs(rs["w"][rs["w"] < 0]) * N1[rs["w"] < 0])),
                                    nneg=int((rs["w"] < -1e-12).sum()))
        out["beta_star_from_line"] = (Phi_ray - vpos) / D_ray
        out["gain_at_beta1"] = Phi_ray - 1.0 * D_ray - vpos  # gain at the TRUE price beta=1
    out["window_width"] = beta_star - beta_unb
    out["window_rel"] = (beta_star - beta_unb) / beta_star
    out["status"] = "ok"
    return out, M


if __name__ == "__main__":
    BIG = [p for p in primes_upto(37) if p > 7]
    cases = [
        ((0, 2, 6), [2, 3, 5, 7], BIG, 1, 1, "base k3 m1 L1"),
        ((0, 2, 6), [2, 3, 5, 7], BIG, 1, 2, "k3 m1 L2 (richer weights)"),
        ((0, 2, 6, 8), [2, 3, 5, 7], BIG, 1, 1, "k4 m1"),
        ((0, 4, 6), [2, 3, 5, 7], BIG, 1, 1, "k3 alt tuple"),
        ((0, 2, 6, 8, 12), [2, 3, 5, 7], BIG, 1, 1, "k5 m1"),
        ((0, 2, 6, 8, 12), [2, 3, 5, 7], BIG, 2, 1, "k5 m2"),
        ((0, 2, 6), [2, 3, 5], BIG, 1, 1, "k3 fewer features"),
        ((0, 2, 6), [2, 3, 5, 7, 11], [p for p in primes_upto(41) if p > 11], 1, 1, "k3 more features"),
    ]
    res = []
    for H, feat, big, m, L, lab in cases:
        try:
            o, _ = analyze(H, feat, big, m, L, lab)
        except Exception as e:
            o = dict(label=lab, status="ERR " + str(e)[:120])
        res.append(o)
        print(json.dumps(o), flush=True)
    json.dump(res, open("fab_phase_results.json", "w"), indent=1)
    print("saved fab_phase_results.json")
