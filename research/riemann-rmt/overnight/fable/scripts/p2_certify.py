# Vendored verbatim from the session scratchpad (earlier P2 agent, k=49/50 work) so that the
# r1_sub186_* scripts are self-contained.  Not modified.

"""Exact rational certification of M_{k,eps} lower bounds (gmpy2.mpq).

Usage: python3 p2_certify.py k d den vecfile [prune]
Computes the exact Rayleigh quotient k(1+eps) x^T Jtil x / x^T Itil x for the
float vector x in vecfile (components converted EXACTLY, binary->mpq).
Any x gives a valid lower bound on M_{k,eps} (restricted-subspace Rayleigh).
"""
import sys, math, time
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import numpy as np
from fractions import Fraction
from gmpy2 import mpq
from p2_eps_engine import Engine, Zint, p_expansion, count_lam

def zint_mpq_factory(n):
    cache = {}
    def z(A, B):
        key = (A, B)
        if key not in cache:
            tot = mpq(0)
            fA = math.factorial(A)
            for lam, c in p_expansion(B, n):
                cnt = count_lam(lam, n)
                if cnt == 0:
                    continue
                num = fA * cnt * c
                for v in lam:
                    num *= math.factorial(v)
                tot += mpq(num, math.factorial(n + A + sum(lam)))
            cache[key] = tot
        return cache[key]
    return z

def certify(k, d, den, vecfile, prune=0.0):
    t0 = time.time()
    E = Engine(k, d, d)
    x = np.load(vecfile)
    assert len(x) == E.n, (len(x), E.n)
    epsF = Fraction(1, den)
    rho = mpq(den - 1, den + 1)
    omr = 1 - rho
    maxM = 2 * (d + 1)
    rpow = [rho ** i for i in range(maxM + k + 3 * d + 6)]
    ompow = [omr ** i for i in range(maxM + 2)]
    zJ = zint_mpq_factory(k - 1)
    zI = zint_mpq_factory(k)
    # prune tiny components (optional): valid lower bound regardless
    xa = np.abs(x)
    thresh = prune * xa.max() if prune else 0.0
    idx = [i for i in range(E.n) if xa[i] > thresh]
    print(f"n={E.n}, using {len(idx)} components", flush=True)
    xm = {i: mpq(Fraction(float(x[i])).numerator, Fraction(float(x[i])).denominator)
          for i in idx}
    # precompute per-element marginal terms in mpq
    mt = {}
    for i in idx:
        mt[i] = [(M, beta, mpq(c.numerator, c.denominator))
                 for (M, beta, c) in E.mterms[i]]
    Scache = {}
    def Sval(M, B):
        key = (M, B)
        s = Scache.get(key)
        if s is None:
            s = mpq(0)
            for j in range(M + 1):
                z = zJ(j, B)
                if z:
                    s += math.comb(M, j) * ompow[M - j] * rpow[j] * z
            Scache[key] = s
        return s
    num = mpq(0); dnm = mpq(0)
    cnt = 0
    for ii, al in enumerate(idx):
        a1, b1 = E.bas[al]
        t1 = mt[al]
        for be in idx[ii:]:
            mult = 2 if be != al else 1
            cxx = mult * xm[al] * xm[be]
            a2, b2 = E.bas[be]
            # I entry
            B = tuple(p + q for p, q in zip(b1, b2))
            dnm += cxx * zI(a1 + a2, B)
            # J entry
            jent = mpq(0)
            for (M1, beta1, c1) in t1:
                for (M2, beta2, c2) in mt[be]:
                    Bp = tuple(p + q for p, q in zip(beta1, beta2))
                    srb = sum((i2 + 2) * Bp[i2] for i2 in range(len(Bp)))
                    jent += c1 * c2 * rpow[k - 1 + srb] * Sval(M1 + M2, Bp)
            num += cxx * jent
        cnt += 1
        if cnt % 100 == 0:
            print(f"  row {cnt}/{len(idx)} [{time.time()-t0:.0f}s]", flush=True)
    Mcert = mpq(k) * (1 + mpq(1, den)) * num / dnm
    print(f"CERTIFIED (exact rational): M_{{{k},1/{den}}} >= {float(Mcert):.9f}")
    print(f"  num/den bit sizes: {Mcert.numerator.bit_length()}/{Mcert.denominator.bit_length()}")
    print(f"  total {time.time()-t0:.0f}s")
    return Mcert

if __name__ == "__main__":
    k = int(sys.argv[1]); d = int(sys.argv[2]); den = int(sys.argv[3])
    vec = sys.argv[4]
    prune = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
    certify(k, d, den, vec, prune)
