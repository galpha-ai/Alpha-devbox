#!/usr/bin/env python3
"""FABLE task 001, item F2: bounded finite-sum diagnostic for the symmetric-prime trial.

Independent implementation (Astra's scripts were read for conventions only; nothing is
imported from them).  Everything here is a FINITE NUMERICAL CHECK at the asymptotic
boundary log L / log T = 1; it proves nothing about the limit and L = T is not a
permitted finite instance of Inoue's theorem (as described by Astra; paper not read).

Definitions (phi = 1/2, ell > 0, a = ell^2, n <= L):
  d_ell(p^e) = ell (ell+1) ... (ell+e-1) / e!, extended multiplicatively   [float64 sieve;
                validated against exact Fractions for all n <= 10^4]
  S2(n)      = sum_{p | n} (log p / log L)^2 over DISTINCT primes
  v_n        = log n / log L
  r(n)       = d_ell(n) H(v_n, S2(n)),   x_n = r(n)/sqrt(n)
  A[q m, m]  = 2 sin((pi/2) log q / log L) / (e sqrt q),  q = p^e <= L, q m <= L  (all e >= 1)
  J_L        = ( ||A x||^2 + <x, A(A x)> ) / (2 pi^2 <x, x>) - 1/4
  K_L        = A^T A + (A^2 + (A^T)^2)/2,   lambda_max(K_L)/(2 pi^2) - 1/4 = best finite margin.

Trials:
  fixed    : ell = 16/15, H = f(v) + g(v) S2 with Astra's rational f, g
  massonly : ell = 16/15, H = f(v)
  one      : ell = 16/15, H = 1
  one_ell1 : ell = 1,     H = 1  (x_n = 1/sqrt n; extra row, not requested)
  deg14    : ell = 1.1762950385645021, H = Astra's degree-14 Jacobi optimum f(v)

Operator modes (diagnostics beyond the requested table):
  full  : the operator as specified (all prime powers, all m)
  nopp  : primes only (e = 1)
  clean : primes only AND insertion p into m only when p does not divide m
          (the combinatorial structure assumed by the continuum schema)

Also reported: the split ||Ax||^2 = D + O (D = q1 = q2 diagonal, O = off-diagonal) and
C2 = <x, A^2 x>, each divided by 2 pi^2 <x,x>, against the continuum pieces M3/I, M2b/I,
M2a/I from f2_continuum_results.json; the d_ell^2/n-weighted moments of S2 against the
Poisson-Dirichlet(a) predictions; the background norm N(L) = sum d_ell(n)^2/n against the
recalled Selberg-Delange constant; eigsh cross-check of lambda_max(K_L) for L <= 1e5.

Run:  OPENBLAS_NUM_THREADS=1 python3 f2_finite_sum.py --lengths 1000,10000,100000,1000000
Output: f2_finite_sum_results.json (next to this file).
"""
from __future__ import annotations
import argparse
import json
import math
import resource
import time
from fractions import Fraction
from pathlib import Path
import numpy as np
from scipy.sparse.linalg import LinearOperator, eigsh
from scipy.special import eval_jacobi, gammaln

HERE = Path(__file__).resolve().parent
ASTRA = HERE.parents[1] / "astra_inputs" / "research" / "residual-gram"
ELL_FIXED = 16/15


# ----------------------------------------------------------------------------- sieve
def primes_upto(L):
    mask = np.ones(L + 1, dtype=bool)
    mask[:2] = False
    for p in range(2, math.isqrt(L) + 1):
        if mask[p]:
            mask[p*p::p] = False
    return np.flatnonzero(mask)


def prime_powers(L, primes):
    """Arrays (q, p, e) for all prime powers q = p^e <= L."""
    qs, ps, es = [], [], []
    for p in primes.tolist():
        q, e = p, 1
        while q <= L:
            qs.append(q); ps.append(p); es.append(e)
            if q > L // p:
                break
            q *= p; e += 1
    return np.array(qs, dtype=np.int64), np.array(ps, dtype=np.int64), np.array(es, dtype=np.int64)


def sieve_d_S2(L, ell, primes, logL):
    """float64 arrays d[n] = d_ell(n) and S2[n] (index 0 unused) for n <= L."""
    d = np.ones(L + 1)
    d[0] = 0.0
    S2 = np.zeros(L + 1)
    for p in primes.tolist():
        up = math.log(p)/logL
        S2[p::p] += up*up
        q, e = p, 1
        while q <= L:
            d[q::q] *= (ell + e - 1)/e          # cumulative product gives d_ell(p^e) for p^e || n
            if q > L // p:
                break
            q *= p; e += 1
    return d, S2


def d_ell_exact(n, ell_frac):
    """Exact rational d_ell(n) by trial division (validation only)."""
    out = Fraction(1)
    m = n
    p = 2
    while p*p <= m:
        if m % p == 0:
            e = 0
            while m % p == 0:
                m //= p; e += 1
            for j in range(e):
                out *= (ell_frac + j)/(j + 1)
        p += 1
    if m > 1:
        out *= ell_frac
    return out


# --------------------------------------------------------------------------- operator
class PrimeOperator:
    """Matrix-free A and A^T for a given L, with modes 'full', 'nopp', 'clean'."""

    def __init__(self, L, primes, logL):
        self.L = L
        self.q, self.p, self.e = prime_powers(L, primes)
        self.w = 2*np.sin((np.pi/2)*np.log(self.q)/logL)/(self.e*np.sqrt(self.q))
        self.nnz = int(np.sum(L // self.q))

    def _items(self, mode):
        sel = slice(None) if mode == "full" else (self.e == 1)
        return zip(self.q[sel].tolist(), self.p[sel].tolist(), self.w[sel].tolist())

    def A(self, x, mode="full"):
        L = self.L
        y = np.zeros(L + 1)
        clean = mode == "clean"
        for q, p, wq in self._items(mode):
            n = L // q
            y[q::q] += wq*x[1:n + 1]
            if clean:
                n2 = L // (q*p)
                if n2:
                    y[q*p::q*p] -= wq*x[p::p][:n2]
        return y

    def AT(self, y, mode="full"):
        L = self.L
        z = np.zeros(L + 1)
        clean = mode == "clean"
        for q, p, wq in self._items(mode):
            n = L // q
            z[1:n + 1] += wq*y[q::q]
            if clean:
                n2 = L // (q*p)
                if n2:
                    z[p::p][:n2] -= wq*y[q*p::q*p]
        return z

    def diagonal_part(self, x, mode="full"):
        """D = sum_q w_q^2 sum_{m <= L/q, [p not | m if clean]} x_m^2  (the q1 = q2 part of ||Ax||^2)."""
        L = self.L
        C = np.cumsum(x*x)
        D = 0.0
        for q, p, wq in self._items(mode):
            s = C[L // q]
            if mode == "clean":
                n2 = L // (q*p)
                if n2:
                    s -= np.sum(x[p::p][:n2]**2)
            D += wq*wq*s
        return D

    def K(self, x, mode="full"):
        ax = self.A(x, mode); atx = self.AT(x, mode)
        return self.AT(ax, mode) + 0.5*(self.A(ax, mode) + self.AT(atx, mode))


# ------------------------------------------------------------------------------ trials
def f_fixed(v):
    return (145 + 3*v - 116*v**2 + 71*v**3 - 6*v**4)/100


def g_fixed(v):
    return (-563 + 1682*v - 2479*v**2 + 1751*v**3 - 488*v**4)/100


def deg14():
    data = json.loads((ASTRA/"variational-results.json").read_text())
    entry = [e for e in data["half_boundary"] if e["degree"] == 14][0]
    ell = entry["ell"]; a = ell*ell
    c = np.array(entry["jacobi_coefficients"])

    def f(v):
        return sum(c[j]*np.sqrt(2*j + a)*eval_jacobi(j, 0, a - 1, 2*v - 1) for j in range(len(c)))
    return ell, f


def selberg_delange_constant(ell, primes_big, emax=80):
    """C = prod_p (1-1/p)^a sum_e d_ell(p^e)^2 p^{-e}  (recalled Selberg-Delange constant; the
    tail p > max(primes_big) is estimated by the leading term -a(a-1)... ignored -> reported as is)."""
    a = ell*ell
    logC = 0.0
    for p in primes_big.tolist():
        s, term = 1.0, 1.0
        for e in range(1, emax):
            term *= ((ell + e - 1)/e)**2/p
            s += term
            if term < 1e-18*s:
                break
        logC += a*math.log1p(-1/p) + math.log(s)
    return math.exp(logC)


# --------------------------------------------------------------------------------- main
def run_L(L, cont, do_eigsh, ell14, f14):
    t0 = time.perf_counter()
    logL = math.log(L)
    primes = primes_upto(L)
    op = PrimeOperator(L, primes, logL)
    n = np.arange(L + 1, dtype=float)
    n[0] = 1.0
    v = np.log(n)/logL
    v[0] = 0.0
    sq = np.sqrt(n)
    t_setup = time.perf_counter() - t0

    t1 = time.perf_counter()
    d_f, S2 = sieve_d_S2(L, ELL_FIXED, primes, logL)
    d_14, _ = sieve_d_S2(L, ell14, primes, logL)
    t_sieve = time.perf_counter() - t1

    trials = {
        "fixed": d_f*(f_fixed(v) + g_fixed(v)*S2),
        "massonly": d_f*f_fixed(v),
        "one": d_f.copy(),
        "one_ell1": np.ones(L + 1),
        "deg14": d_14*f14(v),
    }
    rec = {"L": L, "logL": logL, "n_primes": int(len(primes)), "n_prime_powers": int(len(op.q)),
           "nnz_A": op.nnz, "trials": {}}

    for name, r in trials.items():
        x = r/sq
        x[0] = 0.0
        tr = {}
        for mode in ("full", "nopp", "clean"):
            tt = time.perf_counter()
            ax = op.A(x, mode)
            aax = op.A(ax, mode)
            N = float(x @ x)
            T1 = float(ax @ ax)
            C2 = float(x @ aax)
            D = float(op.diagonal_part(x, mode))
            O = T1 - D
            J = (T1 + C2)/(2*np.pi**2*N) - 0.25
            tr[mode] = {"N": N, "Ax_norm2": T1, "x_A2x": C2, "diag_D": D, "offdiag_O": O,
                        "J": float(J), "lambda_rayleigh": float(2*np.pi**2*(J + 0.25)),
                        "pieces_over_2pi2N": {"D": D/(2*np.pi**2*N), "O": O/(2*np.pi**2*N), "C2": C2/(2*np.pi**2*N)},
                        "seconds": time.perf_counter() - tt}
        ct = cont["trials"][name]["pieces_order64"]
        tr["continuum"] = {"J": ct["J"], "M3_over_I": ct["M3"]/ct["I"], "M2b_over_I": ct["M2b"]/ct["I"],
                           "M2a_over_I": ct["M2a"]/ct["I"]}
        rec["trials"][name] = tr
        print(f"L={L:>8d} {name:9s} J_full={tr['full']['J']:+.7f} J_nopp={tr['nopp']['J']:+.7f} "
              f"J_clean={tr['clean']['J']:+.7f} cont={ct['J']:+.7f}", flush=True)

    # weighted S2 moments (fixed ell) vs Poisson-Dirichlet(a) cumulative predictions
    a = ELL_FIXED**2
    wgt = d_f**2/n
    wgt[0] = 0.0
    Nb = float(wgt.sum())
    R1 = float((wgt*S2).sum()/Nb)
    R2 = float((wgt*S2*S2).sum()/Nb)
    rec["S2_moments_fixed_ell"] = {
        "weighted_mean_S2": R1, "PD_prediction_mean": a/((a + 1)*(a + 2)),
        "weighted_mean_S2sq": R2, "PD_prediction_meansq": a*(a + 6)/((a + 1)*(a + 2)*(a + 3)*(a + 4)),
        "ratio_mean": R1/(a/((a + 1)*(a + 2))), "ratio_meansq": R2/(a*(a + 6)/((a + 1)*(a + 2)*(a + 3)*(a + 4)))}
    # background norm vs recalled Selberg-Delange leading term
    rec["background_norm_fixed_ell"] = {"N_L": Nb, "logL_pow_a": logL**a}

    if do_eigsh:
        tt = time.perf_counter()
        Kop = LinearOperator((L, L), matvec=lambda z: op.K(np.concatenate(([0.0], np.asarray(z).ravel())))[1:],
                             dtype=np.float64)
        val, vec = eigsh(Kop, k=1, which="LA", v0=np.ones(L), tol=1e-12, maxiter=5000)
        lam = float(val[0]); u = vec[:, 0]*np.sign(vec[0, 0])
        res = float(np.linalg.norm(Kop.matvec(u) - lam*u))
        rec["eigsh"] = {"lambda_max": lam, "margin": lam/(2*np.pi**2) - 0.25, "residual": res,
                        "min_eigvec_entry": float(u.min()), "seconds": time.perf_counter() - tt}
        print(f"L={L:>8d} eigsh lambda_max={lam:.10f} margin={lam/(2*np.pi**2)-0.25:+.10f} res={res:.1e}", flush=True)

    rec["timing"] = {"setup_s": t_setup, "sieve_s": t_sieve, "total_s": time.perf_counter() - t0}
    rec["maxrss_MB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lengths", default="1000,10000,100000,1000000")
    ap.add_argument("--eigsh-max", type=int, default=100000)
    ap.add_argument("--out", default=str(HERE/"f2_finite_sum_results.json"))
    args = ap.parse_args()
    cont = json.loads((HERE/"f2_continuum_results.json").read_text())
    ell14, f14 = deg14()

    # exact-rational validation of the float sieve
    Lv = 10000
    pr = primes_upto(Lv)
    d_float, _ = sieve_d_S2(Lv, ELL_FIXED, pr, math.log(Lv))
    ellF = Fraction(16, 15)
    maxrel = max(abs(d_float[k] - float(d_ell_exact(k, ellF)))/float(d_ell_exact(k, ellF)) for k in range(1, Lv + 1))
    print(f"float64 sieve vs exact Fractions, n <= {Lv}: max relative error {maxrel:.2e}", flush=True)

    # recalled Selberg-Delange constant for ell = 16/15 (primes up to 1e7 in the product)
    pr_big = primes_upto(10**7)
    C_sd = selberg_delange_constant(ELL_FIXED, pr_big)
    a = ELL_FIXED**2
    lead = C_sd/math.exp(gammaln(a + 1))

    out = {"status": "finite numerical check; not a proof; L = T is not a permitted finite instance",
           "arithmetic": "float64 for d_ell, S2, logs; d_ell validated against exact rationals for n <= 1e4",
           "float_sieve_max_rel_error_n_le_1e4": maxrel,
           "ell_fixed": "16/15", "ell_deg14": ell14,
           "selberg_delange_constant_ell16_15": {"C": C_sd, "C_over_Gamma_a_plus_1": lead,
                                                  "note": "recalled; not verified online; product over p <= 1e7"},
           "results": []}
    for L in map(int, args.lengths.split(",")):
        rec = run_L(L, cont, do_eigsh=(L <= args.eigsh_max), ell14=ell14, f14=f14)
        bn = rec["background_norm_fixed_ell"]
        bn["ratio_to_leading_term"] = bn["N_L"]/(lead*bn["logL_pow_a"])
        out["results"].append(rec)
        print(f"L={L:>8d} N(L)/(C (log L)^a/Gamma(a+1)) = {bn['ratio_to_leading_term']:.6f}  "
              f"S2 mean ratio={rec['S2_moments_fixed_ell']['ratio_mean']:.5f}  "
              f"S2^2 mean ratio={rec['S2_moments_fixed_ell']['ratio_meansq']:.5f}  "
              f"time={rec['timing']['total_s']:.1f}s maxrss={rec['maxrss_MB']:.0f}MB", flush=True)
        Path(args.out).write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
