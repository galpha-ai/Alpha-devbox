"""Exact finite-L decomposition of the arithmetic quadratic form by coincidence type (Fable task001 / F1).

x_n = r(n)/sqrt(n),  r(n) = d_ell(n) H(v_n, S2(n)),  A[qm, m] = 2 sin((pi/2) log q/log L)/(e sqrt q) for q = p^e, qm <= L.
T(L) = ||A x||^2 + <x, A(A x)>,   J_L = T/(2 pi^2 <x,x>) - 1/4  (Astra's finite operator at log L/log T = 1).
Exact classification of the terms of T (see the report, section 3):
  alpha : two distinct primes p != p', neither dividing the background m         <-> continuum M2
  beta  : same prime twice in ||Ax||^2, n = p m, ALL m (including p | m)          <-> continuum M3
  gamma : same prime twice in <x, A^2 x>  (terms r(m) r(p^2 m))                   predicted O((log L)^-2) relative
  delta : p != p' primes with p | m or p' | m (d_ell not multiplicative, S2 gains nothing)  predicted O(1/log L) relative
  eps   : at least one prime power q = p^e, e >= 2 (includes distinct powers of one prime)  predicted O(1/log L) relative
Computed exactly with three sparse operators: A (all prime powers), A1 (primes only), At (primes p, only columns m with p not | m):
  alpha = ||At x||^2 - beta~ + <x, At^2 x>,   beta~ = sum_p w_p^2/p sum_{m<=L/p, p not| m} r(m)^2/m,
  beta = sum_p w_p^2/p sum_{m<=L/p} r(m)^2/m,  gamma = sum_p w_p^2/p^2 sum_{m<=L/p^2} r(m) r(p^2 m)/m,
  delta = (||A1 x||^2 + <x,A1^2 x>) - alpha - beta - gamma,   eps = T - (||A1 x||^2 + <x,A1^2 x>).
Everything is normalised by D = 2 pi^2 <x,x> and compared with the continuum M2/I, M3/I, J from f1_continuum.py.
Repeated for H = f (mass-only) and H = 1 to diagnose finite-L drift.  lambda_max(K_L) is recomputed for L <= 1e4
as a sanity bound (Rayleigh quotient of any x must be <= lambda_max).  Output: f1_insertion_results.json.
Runtime: about 1 minute for L up to 1e6 (single core).
"""
from __future__ import annotations
import json, sys, time
from math import gamma, log, pi, sin, sqrt
from pathlib import Path
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import LinearOperator, eigsh

sys.path.insert(0, str(Path(__file__).resolve().parent))
from f1_common import ELL, primes_upto, sieve_d_S, trial_fg, euler_constants

ell = ELL; a = ell * ell
HERE = Path(__file__).resolve().parent
cont = json.loads((HERE / "f1_continuum_results.json").read_text())


def make_ops(L):
    """Return (A, A1, At) as csr matrices of shape (L, L), index n-1."""
    logL = log(L)
    R = {"A": [], "A1": [], "At": []}
    for p in primes_upto(L):
        p = int(p); q = p; e = 1
        while q <= L:
            m = np.arange(1, L // q + 1)
            wq = 2 * sin(pi / 2 * log(q) / logL) / (e * sqrt(q))
            R["A"].append((q * m - 1, m - 1, wq))
            if e == 1:
                R["A1"].append((q * m - 1, m - 1, wq))
                mc = m[m % p != 0]
                R["At"].append((q * mc - 1, mc - 1, wq))
            if q > L // p:
                break
            q *= p; e += 1
    ops = {}
    for k, lst in R.items():
        rows = np.concatenate([r for r, c, w in lst]); cols = np.concatenate([c for r, c, w in lst])
        vals = np.concatenate([np.full(len(r), w) for r, c, w in lst])
        ops[k] = csr_matrix((vals, (rows, cols)), shape=(L, L))
    return ops["A"], ops["A1"], ops["At"]


def decompose(L, ops, r):
    A, A1, At = ops
    logL = log(L)
    nn = np.arange(1, L + 1, dtype=float)
    x = r / np.sqrt(nn)
    xx = float(x @ x)
    def T(M):
        Mx = M @ x
        return float(Mx @ Mx), float(x @ (M @ Mx))
    nA, qA = T(A); nA1, qA1 = T(A1); nAt, qAt = T(At)
    r2n = r * r / nn
    pref = np.concatenate([[0.0], np.cumsum(r2n)])            # pref[k] = sum_{m<=k} r(m)^2/m
    ps = primes_upto(L)
    w = 2 * np.sin(pi / 2 * np.log(ps) / logL)
    beta = float(np.sum(w ** 2 / ps * pref[L // ps]))
    beta_div = 0.0; gam = 0.0
    for p, wp in zip(ps[ps * ps <= L], w[ps * ps <= L]):
        p = int(p); K = L // (p * p); k = np.arange(1, K + 1)
        beta_div += wp ** 2 / p * float(np.sum(r2n[p * k - 1]))                         # m = p k, r(m)^2/m
        gam += wp ** 2 / p ** 2 * float(np.sum(r[k - 1] * r[p * p * k - 1] / k))
    beta_t = beta - beta_div
    alpha = nAt - beta_t + qAt
    T1 = nA1 + qA1; Tf = nA + qA
    delta = T1 - alpha - beta - gam
    delta1 = nA1 - nAt - beta_div          # p != p' with p^2 | n or p'^2 | n inside ||A1 x||^2
    delta2 = qA1 - qAt - gam               # p != p' with p | m or p' | m inside <x, A1^2 x>
    eps = Tf - T1
    D = 2 * pi ** 2 * xx
    return {"L": L, "xx": xx, "normA_sq": nA, "quad_A2": qA, "T": Tf,
            "J_L": Tf / D - 0.25, "rayleigh": Tf / xx,
            "alpha_over_D": alpha / D, "beta_over_D": beta / D, "beta_tilde_over_D": beta_t / D,
            "gamma_over_D": gam / D, "delta_over_D": delta / D, "delta1_over_D": delta1 / D, "delta2_over_D": delta2 / D,
            "eps_over_D": eps / D, "J_alpha_beta_only": (alpha + beta) / D - 0.25,
            "check_sum": (alpha + beta + gam + delta + eps - Tf) / Tf}


if __name__ == "__main__":
    t0 = time.time()
    ec = euler_constants(2 * 10 ** 6, ell)
    C = ec["C_ell"]
    results = {"ell": "16/15", "a": a, "euler_C": ec, "continuum": cont, "runs": []}
    keys = {"trial_f_plus_gS": None, "mass_only_f": None, "H_equals_1": None}
    for L in (10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6):
        t1 = time.time()
        d, St = sieve_d_S(L, ell)
        nn = np.arange(1, L + 1, dtype=float)
        v = np.log(nn) / log(L); S2 = St[1:] / log(L) ** 2
        f, g = trial_fg(v)
        rs = {"trial_f_plus_gS": d[1:] * (f + g * S2), "mass_only_f": d[1:] * f, "H_equals_1": d[1:].copy()}
        ops = make_ops(L)
        lam = None
        if L <= 10 ** 4:
            A = ops[0]; At_ = A.T.tocsr()
            def mv(y):
                ay = A @ y; aty = At_ @ y
                return At_ @ ay + 0.5 * (A @ ay + At_ @ aty)
            val, vec = eigsh(LinearOperator((L, L), matvec=mv, dtype=float), k=1, which='LA', v0=np.ones(L), tol=1e-10)
            lam = float(val[0])
        for name, r in rs.items():
            res = decompose(L, ops, r)
            c = cont[name]
            res.update({"H": name, "cont_M2_over_I": float(c["M2_over_I"]), "cont_M3_over_I": float(c["M3_over_I"]),
                        "cont_J": float(c["J"]), "cont_I": float(c["I"]),
                        "xx_over_C_logL_a_Gamma_a": res["xx"] / (C * log(L) ** a / gamma(a)),
                        "lambda_max_K": lam, "seconds": time.time() - t1})
            res["alpha_minus_M2_times_logL"] = (res["alpha_over_D"] - res["cont_M2_over_I"]) * log(L)
            res["beta_minus_M3_times_logL"] = (res["beta_over_D"] - res["cont_M3_over_I"]) * log(L)
            res["JL_minus_J_times_logL"] = (res["J_L"] - res["cont_J"]) * log(L)
            results["runs"].append(res)
            print(f"L={L:>7} {name:16s} J_L={res['J_L']:+.6f} (cont {res['cont_J']:+.6f}) | alpha/D={res['alpha_over_D']:.6f} (M2/I {res['cont_M2_over_I']:.6f})"
                  f" beta/D={res['beta_over_D']:.6f} (M3/I {res['cont_M3_over_I']:.6f}) | gamma={res['gamma_over_D']:.2e} delta={res['delta_over_D']:+.5f}"
                  f" (d1 {res['delta1_over_D']:+.5f}, d2 {res['delta2_over_D']:+.5f}) eps={res['eps_over_D']:+.5f} | <x,x>/(C logL^a/G(a))={res['xx_over_C_logL_a_Gamma_a']:.5f} vs I={res['cont_I']:.5f}"
                  f" | rayleigh={res['rayleigh']:.4f} lam_max={lam} | chk={res['check_sum']:.1e}", flush=True)
    results["seconds"] = time.time() - t0
    Path(HERE / "f1_insertion_results.json").write_text(json.dumps(results, indent=2))
    print("done", f"{time.time()-t0:.1f}s")
