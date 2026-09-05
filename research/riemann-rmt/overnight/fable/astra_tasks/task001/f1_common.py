"""Shared sieve utilities for Fable task001 / F1 (arithmetic transfer of the fixed symmetric-prime trial).

Definitions (from Astra's task FABLE_001):
  ell = 16/15, a = ell^2;  d_ell(p^e) = ell(ell+1)...(ell+e-1)/e!  extended multiplicatively;
  S~(n) = sum_{p | n, distinct primes} (log p)^2,   S2(n) = S~(n)/(log L)^2  (so S2 depends on L only through the scalar (log L)^-2);
  fixed trial: H(v,S) = f(v) + g(v) S with
     f(v) = (145+3v-116v^2+71v^3-6v^4)/100,  g(v) = (-563+1682v-2479v^2+1751v^3-488v^4)/100.
Functions:
  primes_upto(N)         -> numpy array of primes <= N (Eratosthenes)
  sieve_d_S(N, ell)      -> (d, S) arrays indexed by n = 0..N; d[n] = d_ell(n) (d[0] = 0), S[n] = S~(n)
  trial_fg(v)            -> (f(v), g(v))
  euler_constants(P,ell) -> dict with C_ell = prod_p (1-1/p)^a sum_e d_ell(p^e)^2 p^-e (primes <= P, tail estimate)
                            and G'(1)/G(1) for G(s) = prod_p (1-p^-s)^a sum_e d_ell(p^e)^2 p^{-es}.
All arithmetic is float64; the sums checked in the task are compared at relative accuracy ~1e-9, far above rounding.
"""
from __future__ import annotations
import numpy as np
from math import log, log1p

ELL = 16.0 / 15.0


def primes_upto(N: int) -> np.ndarray:
    mask = np.ones(N + 1, dtype=bool)
    mask[:2] = False
    for p in range(2, int(N ** 0.5) + 1):
        if mask[p]:
            mask[p * p::p] = False
    return np.flatnonzero(mask)


def d_ell_powers(ell: float, emax: int) -> np.ndarray:
    """d_ell(p^e) for e = 0..emax (independent of p)."""
    out = np.ones(emax + 1)
    for e in range(1, emax + 1):
        out[e] = out[e - 1] * (ell + e - 1) / e
    return out


def sieve_d_S(N: int, ell: float = ELL):
    """d[n] = d_ell(n) (multiplicative, d[0] = 0);  S[n] = sum over DISTINCT primes p | n of (log p)^2."""
    d = np.ones(N + 1)
    d[0] = 0.0
    S = np.zeros(N + 1)
    for p in primes_upto(N):
        p = int(p)
        S[p::p] += log(p) ** 2
        q, e, prev, cur = p, 1, 1.0, ell
        while True:
            d[q::q] *= cur / prev          # multiples of p^e (not yet of p^{e+1}) get d_ell(p^e)/d_ell(p^{e-1})
            prev, cur, e = cur, cur * (ell + e) / (e + 1), e + 1
            if q > N // p:
                break
            q *= p
    return d, S


def trial_fg(v):
    v = np.asarray(v, dtype=float)
    f = (145 + 3 * v - 116 * v ** 2 + 71 * v ** 3 - 6 * v ** 4) / 100
    g = (-563 + 1682 * v - 2479 * v ** 2 + 1751 * v ** 3 - 488 * v ** 4) / 100
    return f, g


def euler_constants(P: int, ell: float = ELL, emax: int = 90):
    """C_ell and G'(1)/G(1) from primes <= P, with crude tail estimates.
    E_p = sum_{e>=1} d_ell(p^e)^2 p^{-e}.  log C = sum_p [a log(1-1/p) + log(1+E_p)].
    G'(1)/G(1) = sum_p [a log p/(p-1) - (sum_e e d_ell(p^e)^2 p^{-e} log p)/(1+E_p)].
    Tails: summands are O(1/p^2) resp. O(log p/p^2); estimated with sum_{p>P} p^{-2} ~ 1/(P log P), sum_{p>P} log p/p^2 ~ 1/P."""
    a = ell * ell
    ps = primes_upto(P).astype(float)
    de = d_ell_powers(ell, emax)
    inv = 1.0 / ps
    E = np.zeros_like(ps)
    Ed = np.zeros_like(ps)      # sum_e e d_e^2 p^-e
    pe = np.ones_like(ps)
    for e in range(1, emax + 1):
        pe = pe * inv
        term = de[e] ** 2 * pe
        E += term
        Ed += e * term
    lp = np.log(ps)
    logC = float(np.sum(a * np.log1p(-inv) + np.log1p(E)))
    GpG = float(np.sum(a * lp / (ps - 1) - Ed * lp / (1 + E)))
    d2 = de[2]
    c_tail_C = d2 ** 2 - a / 2 - a * a / 2            # coefficient of p^-2 in the summand of log C
    c_tail_G = a - 2 * d2 ** 2 + a * a                # coefficient of log p / p^2 in the summand of G'/G
    tailC = c_tail_C / (P * log(P))
    tailG = c_tail_G / P
    return {"P": P, "C_ell": float(np.exp(logC + tailC)), "C_ell_noTail": float(np.exp(logC)), "tail_logC_est": tailC,
            "GprimeOverG": GpG + tailG, "GprimeOverG_noTail": GpG, "tail_G_est": tailG}


if __name__ == "__main__":
    d, S = sieve_d_S(1000)
    # spot checks against the definition
    ell = ELL
    assert abs(d[2] - ell) < 1e-15 and abs(d[4] - ell * (ell + 1) / 2) < 1e-15 and abs(d[8] - ell * (ell + 1) * (ell + 2) / 6) < 1e-15
    assert abs(d[12] - d[4] * d[3]) < 1e-15 and abs(d[6] - ell * ell) < 1e-15
    assert abs(S[12] - (log(2) ** 2 + log(3) ** 2)) < 1e-12 and abs(S[8] - log(2) ** 2) < 1e-12
    print("f1_common self-test passed; euler constants (P=1e6):", euler_constants(10 ** 6))
