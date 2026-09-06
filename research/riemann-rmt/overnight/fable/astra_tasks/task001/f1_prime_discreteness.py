"""Discrete-prime / continuum-background model of the insertion terms (Fable task001 / F1).

The exact alpha (two distinct primes, both coprime to the background) and beta (same prime twice) terms of the finite
operator differ from the continuum M2, M3 by (i) replacing prime sums sum_p (.)/p by integrals du/u (Mertens) and
(ii) replacing the background integer sums by their Selberg-Delange asymptotics.  This script isolates (i):
  alpha_semi(L)/D_semi = ell^2 sum_{p != p', p p' <= L} (w_p w_p'/(p p')) B(1-u_p-u_p'; u_p, u_p') / (2 pi^2 I),
  beta_semi(L)/D_semi  =       sum_{p <= L}             (w_p^2/p)        Bq(1-u_p)               / (2 pi^2 I),
with w_p = 2 sin(pi u_p/2), u_p = log p/log L, and the continuum backgrounds
  B(y;u,w) = int_0^y v^{a-1} P(v,u,w) dv,   Bq(y) = int_0^y v^{a-1} Q(v) dv,
  P = E_v[H(v,S)H(v+u+w,S+u^2+w^2) + H(v+u,S+u^2)H(v+w,S+w^2)],  Q = E_v[H^2]  (rational polynomials, sympy).
As L -> infinity these tend to M2/I and M3/I (Mertens twice / once).  Leading Mertens correction (derived in the report):
  alpha_semi/D_semi = M2/I + A1/log L + o(1/log L),   A1 = (2 E/(pi I)) int_0^1 sin(pi w/2) Phi(0,w)/w dw,  Phi(0,w) = ell^2 B(1-w;0,w),
  E = lim (sum_{p<=t} log p/p - log t) = -gamma - sum_p sum_{e>=2} log p/p^e  (Mertens),  and no 1/log L term for beta
  (its kernel 4 sin^2(pi u/2) vanishes to second order at u = 0).
Primes are binned in u (NB bins, 1/p-weighted mean u per bin) for L >= 1e6; exact pair sums for L <= 1e5 validate the binning.
Output: f1_prime_discreteness_results.json.  Runtime: a few minutes (sieve to 1e8).
"""
from __future__ import annotations
import json, sys, time
from math import log, pi, sin, sqrt
from pathlib import Path
import numpy as np
import sympy as sp
import mpmath as mp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from f1_common import ELL, primes_upto

HERE = Path(__file__).resolve().parent
cont = json.loads((HERE / "f1_continuum_results.json").read_text())
ell = ELL; a = ell * ell
v, u, w, S = sp.symbols('v u w S')
ellr = sp.Rational(16, 15); ar = ellr ** 2
mu1 = 1 / (ar + 1); mu2 = (ar + 6) / ((ar + 1) * (ar + 2) * (ar + 3))
f_poly = (145 + 3 * v - 116 * v ** 2 + 71 * v ** 3 - 6 * v ** 4) / 100
g_poly = (-563 + 1682 * v - 2479 * v ** 2 + 1751 * v ** 3 - 488 * v ** 4) / 100


def avg(expr):
    poly = sp.Poly(sp.expand(expr), S); out = 0
    for (k,), c in poly.terms():
        out += c * {0: 1, 1: mu1 * v ** 2, 2: mu2 * v ** 4}[k]
    return sp.expand(out)


def polys(H):
    def shift(*xs):
        return H.subs({v: v + sum(xs), S: S + sum(x * x for x in xs)}, simultaneous=True)
    Pp = sp.Poly(avg(H * shift(u, w) + shift(u) * shift(w)), v, u, w)
    Qp = sp.Poly(avg(H * H), v)
    Pt = [((k, i, j), float(c)) for (k, i, j), c in Pp.terms()]
    Qt = [(k, float(c)) for (k,), c in Qp.terms()]
    return Pt, Qt


def B_eval(Pt, y, uu, ww):
    """int_0^y v^{a-1} P(v,uu,ww) dv, vectorised (y, uu, ww arrays of equal shape)."""
    ya = np.where(y > 0, np.abs(y) ** a, 0.0)
    out = np.zeros_like(y)
    for (k, i, j), c in Pt:
        out += c * (uu ** i) * (ww ** j) * ya * y ** k / (a + k)
    return out


def Bq_eval(Qt, y):
    ya = np.where(y > 0, np.abs(y) ** a, 0.0)
    return sum(c * ya * y ** k / (a + k) for k, c in Qt)


def model(L, Pt, Qt, I, primes, NB=6000, exact_pairs=False):
    logL = log(L)
    ps = primes[primes <= L].astype(float)
    up = np.log(ps) / logL
    wp = 2 * np.sin(pi * up / 2)
    beta = float(np.sum(wp ** 2 / ps * Bq_eval(Qt, 1 - up))) / (2 * pi ** 2 * I)
    # diagonal p = p' (to be removed from the binned double sum)
    sm = ps[ps * ps <= L]; usm = np.log(sm) / logL; wsm = 2 * np.sin(pi * usm / 2)
    diag = float(np.sum(wsm ** 2 / sm ** 2 * B_eval(Pt, 1 - 2 * usm, usm, usm)))
    if exact_pairs:
        tot = 0.0
        for p, up_, wp_ in zip(ps[ps <= L / 2], up[ps <= L / 2], wp[ps <= L / 2]):
            mask = ps <= L / p
            q = ps[mask]; uq = up[mask]; wq = wp[mask]
            tot += wp_ / p * float(np.sum(wq / q * B_eval(Pt, 1 - up_ - uq, np.full(len(q), up_), uq)))
        alpha = ell * ell * (tot - diag) / (2 * pi ** 2 * I)
        return alpha, beta
    # binning in u: weights 1/p, bin mean u
    idx = np.minimum((up * NB).astype(int), NB - 1)
    Sb = np.bincount(idx, weights=1 / ps, minlength=NB)
    Ub = np.bincount(idx, weights=up / ps, minlength=NB)
    keep = Sb > 0
    Sb = Sb[keep]; Ub = Ub[keep] / Sb
    Wb = 2 * np.sin(pi * Ub / 2)
    tot = 0.0
    for b in range(len(Sb)):
        y = 1 - Ub[b] - Ub
        m = y >= 0
        if not m.any():
            continue
        tot += Sb[b] * Wb[b] * float(np.sum(Sb[m] * Wb[m] * B_eval(Pt, y[m], np.full(int(m.sum()), Ub[b]), Ub[m])))
    alpha = ell * ell * (tot - diag) / (2 * pi ** 2 * I)
    return alpha, beta


if __name__ == "__main__":
    t0 = time.time()
    LMAX = 10 ** 8
    primes = primes_upto(LMAX)
    print(f"primes to {LMAX}: {len(primes)} ({time.time()-t0:.1f}s)", flush=True)
    # Mertens constant E for sum log p / p
    lp = np.log(primes.astype(float))
    E_num = float(np.sum(lp / primes)) - log(LMAX)
    E_formula = -0.57721566490153286 - float(np.sum(lp / (primes.astype(float) * (primes.astype(float) - 1))))
    print("Mertens E (numerical at 1e8, formula):", E_num, E_formula, flush=True)
    trials = {"trial_f_plus_gS": f_poly + g_poly * S, "H_equals_1": sp.Integer(1)}
    ins = json.loads((HERE / "f1_insertion_results.json").read_text())["runs"] if (HERE / "f1_insertion_results.json").exists() else []
    out = {"E_mertens_numerical_1e8": E_num, "E_mertens_formula": E_formula, "results": {}}
    for name, H in trials.items():
        Pt, Qt = polys(H)
        I = float(cont[name]["I"]); M2I = float(cont[name]["M2_over_I"]); M3I = float(cont[name]["M3_over_I"])
        # first-order Mertens constant A1 = (2E/(pi I)) int_0^1 sin(pi w/2) ell^2 B(1-w;0,w)/w dw
        def phi0(wv):
            wv = mp.mpf(wv); y = 1 - wv
            tot = mp.mpf(0)
            for (k, i, j), c in Pt:
                if i == 0:
                    tot += c * wv ** j * y ** (a + k) / (a + k)
            return ell * ell * tot
        integ = mp.quad(lambda wv: mp.sin(mp.pi * wv / 2) * phi0(wv) / wv, [0, 1])
        A1 = float(2 * E_formula / (mp.pi * I) * integ)
        res = {"I": I, "M2_over_I": M2I, "M3_over_I": M3I, "A1_mertens": A1, "rows": []}
        for L in (10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7, 10 ** 8):
            t1 = time.time()
            al, be = model(L, Pt, Qt, I, primes)
            row = {"L": L, "alpha_semi": al, "beta_semi": be, "M2I_plus_A1_over_logL": M2I + A1 / log(L),
                   "alpha_semi_minus_M2I_times_logL": (al - M2I) * log(L), "beta_semi_minus_M3I_times_logL": (be - M3I) * log(L)}
            if L <= 10 ** 5:
                ale, bee = model(L, Pt, Qt, I, primes, exact_pairs=True)
                row["alpha_semi_exact_pairs"] = ale; row["binning_rel_err"] = al / ale - 1
            ex = [r for r in ins if r["L"] == L and r["H"] == name]
            if ex:
                row["alpha_exact_over_D"] = ex[0]["alpha_over_D"]; row["beta_exact_over_D"] = ex[0]["beta_over_D"]
                row["alpha_exact_over_alpha_semi"] = ex[0]["alpha_over_D"] / al; row["beta_exact_over_beta_semi"] = ex[0]["beta_over_D"] / be
            row["seconds"] = time.time() - t1
            res["rows"].append(row)
            print(f"{name:16s} L=1e{round(log(L)/log(10))}: alpha_semi={al:.5f} (M2/I {M2I:.5f}, M2/I+A1/logL {row['M2I_plus_A1_over_logL']:.5f}, (a-M2I)*logL {row['alpha_semi_minus_M2I_times_logL']:+.4f})"
                  f" beta_semi={be:.5f} (M3/I {M3I:.5f}) " + (f"exact alpha/D={row['alpha_exact_over_D']:.5f} ratio={row['alpha_exact_over_alpha_semi']:.4f}, exact beta/D={row['beta_exact_over_D']:.5f} ratio={row['beta_exact_over_beta_semi']:.4f}" if ex else "")
                  + (f" bin-err={row['binning_rel_err']:.1e}" if 'binning_rel_err' in row else "") + f" [{row['seconds']:.1f}s]", flush=True)
        out["results"][name] = res
    out["seconds"] = time.time() - t0
    Path(HERE / "f1_prime_discreteness_results.json").write_text(json.dumps(out, indent=2))
    print("done", f"{time.time()-t0:.1f}s")
