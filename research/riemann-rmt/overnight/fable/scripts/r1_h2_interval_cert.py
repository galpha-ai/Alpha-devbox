#!/usr/bin/env python3
"""
r1_h2_interval_cert.py -- Fable overnight, task D1 (2026-09-05).

Independent, outward-rounded re-certification of the H2-record inequality

        M_15856 > 8          (Maynard-Tao variational constant, closed standard simplex)

for the FIXED piecewise-linear profile g stored in research/riemann-rmt/p9_g_k15856.npz,
plus an independent admissibility / diameter check of research/riemann-rmt/p9_tuple_k15856.npy.

Mathematical chain (written out with proofs in r1_h2_interval_cert.md):
  F(t) = prod_i g(k t_i) * 1[sum t_i <= 1],   X_i iid with density g^2/c2 on [0,T],  K = k-1,
  M_k >= k J(F)/I(F) = E[G((k-S_K)_+)^2] / (c2 * P(S_k <= k))
      >= (1/c2) * sum_j w_j * (G(b_j)^2 - G(a_j)^2),     w_j = max(0, 1 - beta_j),
  where beta_j is ANY rigorous upper bound for P(S_K > k - b_j):
      (BE)  Phibar(z) + C_BE * rho3 / (sigma^3 sqrt(K)),  z = (s - K mu)/(sigma sqrt K),
            Phibar(z) <= min( exp(-z^2/2)/(z sqrt(2 pi)),  exp(-z^2/2)/2 )      (z > 0)
      (CH)  C(K,2) q_B^2 + exp( -lam (s - gap) + K * log MGF_B(lam) ),  gap = T (B < T) or 0 (B = T),
            MGF_B(lam) = E exp(lam X 1[X<=B]) bounded above by the chord of exp(lam t) on each piece.

Arithmetic design (three layers):
  (1) EXACT layer (fractions.Fraction): everything polynomial in the dyadic node data
      (c2, G at nodes, mu, sigma^2, rho3 = E|X-mu|^3 split exactly at mu, chord weights P0/P1,
      q_B, pN2 = C(K,2) q_B^2, Chernoff exponents -lam*se + K*L with L a dyadic upper bound
      of log MGF).  lam and B are themselves exact dyadic / rational numbers.
  (2) INTERVAL layer: only exp, log, sqrt, pi (and, for one informational variant, erfc) --
      evaluated with python-flint arb (ball arithmetic, 200 bits; the primary rigorous backend)
      and, as a second implementation, mpmath.iv (200 bits) with an extra relative guard band
      2^-150 around every transcendental result.  Endpoints are read back as exact dyadic
      rationals (arb: man_exp(); mpmath: _mpi_ tuples).  Every Fraction -> interval conversion
      is self-checked (endpoints bracket the rational).
  (3) EXACT assembly: beta_ub_j (dyadic) -> w_j = 1 - beta_ub_j -> sum_j w_j dG2_j / c2 in Fraction.
      The certified number is an exact rational; it is printed rounded DOWN.

Usage:
  python3 r1_h2_interval_cert.py [--npz PATH] [--tuple PATH] [--out PATH.json] [--backend arb|mpmath|both]
Runs in well under a minute on one core.
"""
import argparse
import hashlib
import json
import math
import sys
import time
from fractions import Fraction as Fr

import numpy as np

# ----------------------------------------------------------------------------------------------
# exact helpers
# ----------------------------------------------------------------------------------------------


def frac_to_dec(fr, ndig=25, mode="down"):
    """Decimal string of a Fraction with ndig digits after the point, rounded down/up."""
    sign = "-" if fr < 0 else ""
    x = abs(fr) * (10 ** ndig)
    n = x.numerator // x.denominator
    if x.numerator % x.denominator:
        # rounding direction is w.r.t. the signed value
        if (mode == "up" and fr > 0) or (mode == "down" and fr < 0):
            n += 1
    s = str(n).rjust(ndig + 1, "0")
    return sign + s[:-ndig] + "." + s[-ndig:]


def dyadic_str(fr):
    """exact representation 'man*2^exp' of a dyadic rational (or 'p/q' otherwise)."""
    d = fr.denominator
    if d & (d - 1) == 0:
        return f"{fr.numerator}*2^-{d.bit_length() - 1}"
    return f"{fr.numerator}/{fr.denominator}"


def poly_int(coeffs, a, b):
    """exact integral of sum_i coeffs[i] t^i over [a,b] (Fractions)."""
    s = Fr(0)
    for i, c in enumerate(coeffs):
        if c:
            s += c * (b ** (i + 1) - a ** (i + 1)) / (i + 1)
    return s


def poly_mul(p, q):
    r = [Fr(0)] * (len(p) + len(q) - 1)
    for i, ci in enumerate(p):
        for j, cj in enumerate(q):
            r[i + j] += ci * cj
    return r


# ----------------------------------------------------------------------------------------------
# interval backends: only need const(Fraction), exp, log, sqrt, pi, lo(), hi()
# ----------------------------------------------------------------------------------------------


class ArbBackend:
    name = "python-flint arb (ball arithmetic)"

    def __init__(self, prec=200):
        from flint import arb, ctx, fmpq
        ctx.prec = prec
        self.prec = prec
        self.arb, self.fmpq = arb, fmpq
        self._selftest()

    def const(self, fr):
        x = self.arb(self.fmpq(fr.numerator, fr.denominator))
        lo, hi = self.lo(x), self.hi(x)
        assert lo <= fr <= hi, "arb const enclosure failed"
        return x

    def exp(self, x):
        return x.exp()

    def log(self, x):
        return x.log()

    def sqrt(self, x):
        return x.sqrt()

    def pi(self):
        return self.arb.pi()

    def erfc(self, x):
        return x.erfc()

    @staticmethod
    def _arf_to_frac(a):
        assert a.is_exact()
        man, ex = a.man_exp()
        man, ex = int(man), int(ex)
        return Fr(man) * (Fr(2) ** ex) if ex < 0 else Fr(man * 2 ** ex)

    def lo(self, x):
        return self._arf_to_frac(x.lower())

    def hi(self, x):
        return self._arf_to_frac(x.upper())

    def _selftest(self):
        arb = self.arb
        # certain-comparison semantics (documented, not relied upon below)
        x, y = arb(1, 0.5), arb(1.2)
        assert (not bool(x < y)) and (not bool(x > y))
        # exact big integers and man_exp round trip
        N = 2 ** 300 + 12345
        assert self._arf_to_frac(arb(N)) == N
        for fr in (Fr(3, 7), Fr(-2 ** 400 + 1, 3 ** 200), Fr(1, 10), Fr(123456789, 2 ** 90)):
            self.const(fr)
        e = self.exp(self.const(Fr(1)))
        assert self.lo(e) < Fr("2.71828182845904523536028747135266249775724709369996")
        assert self.hi(e) > Fr("2.71828182845904523536028747135266249775724709369995")


class MpmathBackend:
    name = "mpmath.iv (interval arithmetic) + 2^-150 guard band"

    def __init__(self, prec=200, guard_bits=150):
        import mpmath
        from mpmath import iv, mp
        from mpmath.libmp import from_rational, round_floor, round_ceiling
        iv.prec = prec
        mp.prec = prec
        self.prec = prec
        self.iv, self.mp = iv, mp
        self._from_rational = from_rational
        self._rf, self._rc = round_floor, round_ceiling
        self.guard = Fr(1, 2 ** guard_bits)
        self._selftest()

    # -- conversions ------------------------------------------------------------------------
    @staticmethod
    def _tuple_to_frac(t):
        sign, man, ex, bc = t
        man = int(man)
        v = Fr(man) * (Fr(2) ** ex) if ex < 0 else Fr(man * 2 ** ex)
        return -v if sign else v

    def _from_endpoints(self, lo, hi):
        """build an interval from two exact Fractions lo <= hi, outward rounded."""
        a = self._from_rational(lo.numerator, lo.denominator, self.prec, self._rf)
        b = self._from_rational(hi.numerator, hi.denominator, self.prec, self._rc)
        x = self.iv.mpf((self.mp.make_mpf(a), self.mp.make_mpf(b)))
        l2, h2 = self.lo(x), self.hi(x)
        assert l2 <= lo and hi <= h2, "mpmath outward conversion failed"
        return x

    def const(self, fr):
        return self._from_endpoints(fr, fr)

    def lo(self, x):
        return self._tuple_to_frac(x._mpi_[0])

    def hi(self, x):
        return self._tuple_to_frac(x._mpi_[1])

    def _pad(self, x):
        """widen by a relative guard band (covers any last-ulp misrounding inside mpmath)."""
        lo, hi = self.lo(x), self.hi(x)
        w = max(abs(lo), abs(hi)) * self.guard
        return self._from_endpoints(lo - w, hi + w)

    # -- transcendental ops -----------------------------------------------------------------
    def exp(self, x):
        return self._pad(self.iv.exp(x))

    def log(self, x):
        return self._pad(self.iv.log(x))

    def sqrt(self, x):
        return self._pad(self.iv.sqrt(x))

    def pi(self):
        return self._pad(self.iv.pi)

    def _selftest(self):
        N = 2 ** 300 + 12345
        x = self.const(Fr(N))
        assert self.lo(x) <= N <= self.hi(x)
        for fr in (Fr(3, 7), Fr(-2 ** 400 + 1, 3 ** 200), Fr(1, 10), Fr(123456789, 2 ** 90)):
            self.const(fr)
        e = self.exp(self.const(Fr(1)))
        assert self.lo(e) < Fr("2.71828182845904523536028747135266249775724709369996")
        assert self.hi(e) > Fr("2.71828182845904523536028747135266249775724709369995")


# ----------------------------------------------------------------------------------------------
# the certificate
# ----------------------------------------------------------------------------------------------

B_FRACS = ["0.005", "0.02", "0.06", "0.12", "0.2", "0.35", "0.55", "0.75", "1"]   # B = T * frac
LAM_EXPS = list(range(-24, 45))                                                 # lam = 10^(e/8)/T, rounded to float64
LAM_B_CUTOFF = Fr(300)                                                          # skip lam*B > 300 (heuristic only)


def load_profile(npz_path):
    d = np.load(npz_path)
    u_np, g_np, k = d["u"], d["g"], int(d["k"])
    assert u_np.dtype == np.float64 and g_np.dtype == np.float64
    u = [Fr(float(x)) for x in u_np.tolist()]
    g = [Fr(float(x)) for x in g_np.tolist()]
    assert len(u) == len(g) >= 2
    assert u[0] == 0, "first node must be 0"
    assert all(u[i] < u[i + 1] for i in range(len(u) - 1)), "nodes must be strictly increasing"
    assert all(x >= 0 for x in g), "g must be nonnegative at every node (=> nonnegative pw-linear)"
    assert abs(float(d["T"]) - float(u[-1])) == 0.0
    return u, g, k, u_np, g_np


def exact_layer(u, g, k):
    """all polynomial quantities, exactly."""
    K = k - 1
    T = u[-1]
    pieces = []
    for j in range(len(u) - 1):
        a, b, ga, gb = u[j], u[j + 1], g[j], g[j + 1]
        s = (gb - ga) / (b - a)
        c0 = ga - s * a                       # g(t) = c0 + s t on [a,b]
        cs = [c0 * c0, 2 * c0 * s, s * s]     # g(t)^2
        P0 = poly_int(cs, a, b)               # int_a^b g^2
        tg = [-a * cs[0], cs[0] - a * cs[1], cs[1] - a * cs[2], cs[2]]   # (t-a) g^2
        P1 = poly_int(tg, a, b) / (b - a)     # int_a^b (t-a)/(b-a) g^2
        pieces.append(dict(a=a, b=b, ga=ga, gb=gb, cs=cs, P0=P0, P1=P1))
    c2 = sum(p["P0"] for p in pieces)
    assert c2 > 0
    Gn = [Fr(0)]
    for p in pieces:
        Gn.append(Gn[-1] + (p["b"] - p["a"]) * (p["ga"] + p["gb"]) / 2)
    dG2 = [Gn[j + 1] ** 2 - Gn[j] ** 2 for j in range(len(pieces))]
    assert all(x >= 0 for x in dG2)
    m1 = sum(poly_int([Fr(0)] + p["cs"], p["a"], p["b"]) for p in pieces) / c2
    m2 = sum(poly_int([Fr(0), Fr(0)] + p["cs"], p["a"], p["b"]) for p in pieces) / c2
    var = m2 - m1 * m1
    assert var > 0
    # rho3 = E|X - mu|^3, exactly: split the (unique) piece containing mu at mu
    rho3 = Fr(0)
    cub = [-m1 ** 3, 3 * m1 ** 2, -3 * m1, Fr(1)]           # (t - mu)^3
    for p in pieces:
        prod = poly_mul(cub, p["cs"])
        a, b = p["a"], p["b"]
        if b <= m1:
            rho3 -= poly_int(prod, a, b)
        elif a >= m1:
            rho3 += poly_int(prod, a, b)
        else:
            rho3 += -poly_int(prod, a, m1) + poly_int(prod, m1, b)
    rho3 /= c2
    assert rho3 > 0
    # truncation data per B
    Bdata = []
    for f in B_FRACS:
        B = T * Fr(f)
        plain = (B == T)
        n_full = sum(1 for p in pieces if p["b"] <= B)          # pieces entirely below B
        straddle = None
        if not plain:
            p = pieces[n_full]
            assert p["a"] < B < p["b"]
            a, cs = p["a"], p["cs"]
            P0s = poly_int(cs, a, B)
            tg = [-a * cs[0], cs[0] - a * cs[1], cs[1] - a * cs[2], cs[2]]
            P1s = poly_int(tg, a, B) / (B - a)
            straddle = dict(a=a, hi=B, P0=P0s, P1=P1s)
        mass_above = sum(poly_int(p["cs"], max(p["a"], B), p["b"]) for p in pieces if p["b"] > B)
        qB = mass_above / c2
        pN2 = Fr(K * (K - 1), 2) * qB * qB if not plain else Fr(0)
        gap = Fr(0) if plain else T
        Bdata.append(dict(frac=f, B=B, plain=plain, n_full=n_full, straddle=straddle,
                          mass_above=mass_above, qB=qB, pN2=pN2, gap=gap))
    lams = [Fr(float(10.0 ** (e / 8.0) / float(T))) for e in LAM_EXPS]   # exact dyadics
    return dict(K=K, T=T, pieces=pieces, c2=c2, Gn=Gn, dG2=dG2, mu=m1, m2=m2, var=var, rho3=rho3,
                Bdata=Bdata, lams=lams)


def interval_layer(E, k, IV, C_list, use_erfc=False):
    """tail-bound upper bounds beta_j (and lower endpoints of the same formulas) per node."""
    K, T, pieces, c2 = E["K"], E["T"], E["pieces"], E["c2"]
    Bdata, lams = E["Bdata"], E["lams"]
    n = len(pieces)
    inv_c2 = IV.const(1 / c2)
    Kiv = IV.const(Fr(K))

    # ---- log MGF upper/lower bounds L[i][l] for every (B_i, lam_l) via prefix sums over lam ----
    t0 = time.time()
    Lub = [[None] * len(lams) for _ in Bdata]
    Llb = [[None] * len(lams) for _ in Bdata]
    W0 = [IV.const(p["P0"] - p["P1"]) for p in pieces]
    W1 = [IV.const(p["P1"]) for p in pieces]
    for l, lam in enumerate(lams):
        Ea = [IV.exp(IV.const(lam * u_)) for u_ in [p["a"] for p in pieces] + [pieces[-1]["b"]]]
        prefix = [None] * (n + 1)
        acc = IV.const(Fr(0))
        prefix[0] = acc
        for j in range(n):
            acc = acc + Ea[j] * W0[j] + Ea[j + 1] * W1[j]
            prefix[j + 1] = acc
        for i, bd in enumerate(Bdata):
            if lam * bd["B"] > LAM_B_CUTOFF:
                continue
            tot = prefix[bd["n_full"]]
            if bd["straddle"] is not None:
                st = bd["straddle"]
                tot = tot + IV.exp(IV.const(lam * st["a"])) * IV.const(st["P0"] - st["P1"]) \
                          + IV.exp(IV.const(lam * st["hi"])) * IV.const(st["P1"])
            tot = tot + IV.const(bd["mass_above"])
            Lv = IV.log(tot * inv_c2)
            Lub[i][l], Llb[i][l] = IV.hi(Lv), IV.lo(Lv)
    t_mgf = time.time() - t0

    # ---- Berry-Esseen ingredients ----
    sqrtK_var = IV.sqrt(IV.const(K * E["var"]))
    be_unit = IV.const(E["rho3"]) / (IV.sqrt(IV.const(E["var"])) ** 3 * IV.sqrt(IV.const(Fr(K))))
    be_unit_hi, be_unit_lo = IV.hi(be_unit), IV.lo(be_unit)
    sqrt2pi = IV.sqrt(2 * IV.pi())
    sqrt2 = IV.sqrt(IV.const(Fr(2)))
    one = IV.const(Fr(1))

    nodes = []
    t0 = time.time()
    for j in range(n):
        bnode = pieces[j]["b"]
        s = Fr(k) - bnode
        cands = {}   # name -> (ub, lb)
        # (BE): only for z > 0, i.e. s > K mu
        smean = s - K * E["mu"]
        if smean > 0:
            z = IV.const(smean) / sqrtK_var
            e = IV.exp(-(z * z) / 2)
            v1 = e / (z * sqrt2pi)
            v2 = e / 2
            ph_hi = min(IV.hi(v1), IV.hi(v2))
            ph_lo = min(IV.lo(v1), IV.lo(v2))
            cands["BE_elem"] = (ph_hi, ph_lo)
            if use_erfc:
                ph = IV.erfc(z / sqrt2) / 2
                cands["BE_erfc"] = (IV.hi(ph), IV.lo(ph))
        # (CH): for each B pick the lam with the smallest exact exponent, then one exp
        for i, bd in enumerate(Bdata):
            se = s - bd["gap"]
            if se <= 0:
                continue
            best_l, best_expo = None, None
            for l, lam in enumerate(lams):
                if Lub[i][l] is None:
                    continue
                expo = -lam * se + K * Lub[i][l]
                if best_expo is None or expo < best_expo:
                    best_l, best_expo = l, expo
            if best_l is None:
                continue
            if best_expo >= 0:
                ub = bd["pN2"] + 1
                lb = bd["pN2"] + 1
            else:
                ub = bd["pN2"] + IV.hi(IV.exp(IV.const(best_expo)))
                expo_lo = -lams[best_l] * se + K * Llb[i][best_l]
                lb = bd["pN2"] + (IV.lo(IV.exp(IV.const(expo_lo))) if expo_lo < 0 else Fr(1))
            cands[f"CH(B={bd['frac']}T,lam=10^({LAM_EXPS[best_l]}/8)/T)"] = (ub, lb)
        nodes.append(dict(u=bnode, s=s, cands=cands, dG2=E["dG2"][j]))
    t_nodes = time.time() - t0
    return dict(nodes=nodes, be_unit_hi=be_unit_hi, be_unit_lo=be_unit_lo, t_mgf=t_mgf, t_nodes=t_nodes)


def assemble(E, R, C_BE, use_BE=True, be_key="BE_elem"):
    """exact assembly: beta_j = min over candidates; certificate = sum (1-beta_ub)^+ dG2 / c2."""
    tot_lo, tot_hi = Fr(0), Fr(0)
    chain = []
    for nd in R["nodes"]:
        best_ub, best_lb, best_name = Fr(1), Fr(1), "none"
        for name, (ub, lb) in nd["cands"].items():
            if name.startswith("BE"):
                if not use_BE or name != be_key:
                    continue
                ub = ub + C_BE * R["be_unit_hi"]
                lb = lb + C_BE * R["be_unit_lo"]
            if ub < best_ub:
                best_ub, best_name = ub, name
            if lb < best_lb:
                best_lb = lb
        w_lo = max(Fr(0), 1 - best_ub)   # certified weight (uses the UPPER end of beta)
        w_hi = max(Fr(0), 1 - best_lb)
        tot_lo += w_lo * nd["dG2"]
        tot_hi += w_hi * nd["dG2"]
        chain.append(dict(u=float(nd["u"]), strategy=best_name, beta_ub=float(best_ub),
                          beta_ub_dec_up=frac_to_dec(best_ub, 40, "up"), w_lo=float(w_lo),
                          contrib_lb=float(w_lo * nd["dG2"] / E["c2"])))
    return tot_lo / E["c2"], tot_hi / E["c2"], chain


# ----------------------------------------------------------------------------------------------
# admissible tuple check (two implementations)
# ----------------------------------------------------------------------------------------------


def primes_upto(n):
    s = bytearray([1]) * (n + 1)
    s[0] = s[1] = 0
    for p in range(2, int(n ** 0.5) + 1):
        if s[p]:
            s[p * p::p] = bytearray(len(range(p * p, n + 1, p)))
    return [i for i in range(n + 1) if s[i]]


def check_tuple(path, k):
    t = np.load(path)
    assert t.dtype == np.int64
    vals = [int(x) for x in t.tolist()]
    n = len(vals)
    distinct_sorted = all(vals[i] < vals[i + 1] for i in range(n - 1))
    diam = max(vals) - min(vals)
    pr = primes_upto(k)
    # implementation 1: pure python sets
    bad = []
    for p in pr:
        if len({v % p for v in vals}) >= p:
            bad.append(p)
    # implementation 2: numpy bincount over shifted values
    arr = np.array(vals, dtype=np.int64) - min(vals)
    bad2 = [p for p in pr if int(np.count_nonzero(np.bincount(arr % p, minlength=p))) >= p]
    # extra: primes k < p <= diam cannot be fully covered by k < p residues -- automatic
    return dict(file=path, sha256=hashlib.sha256(open(path, "rb").read()).hexdigest(),
                k=k, count=n, count_ok=(n == k), distinct_sorted=distinct_sorted,
                min=min(vals), max=max(vals), diameter=diam, primes_tested=len(pr), largest_prime_tested=pr[-1],
                violations_impl1=bad, violations_impl2=bad2,
                admissible=(n == k and distinct_sorted and not bad and not bad2))


# ----------------------------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--npz", default="/home/user/Alpha-devbox/research/riemann-rmt/p9_g_k15856.npz")
    ap.add_argument("--tuple", default="/home/user/Alpha-devbox/research/riemann-rmt/p9_tuple_k15856.npy")
    ap.add_argument("--out", default="/home/user/Alpha-devbox/research/riemann-rmt/overnight/fable/data/h2_k15856_interval_cert.json")
    ap.add_argument("--backend", default="both", choices=["arb", "mpmath", "both"])
    ap.add_argument("--threshold", default="8")
    ap.add_argument("--skip-tuple", action="store_true")
    args = ap.parse_args()
    thr = Fr(args.threshold)

    t0 = time.time()
    u, g, k, u_np, g_np = load_profile(args.npz)
    E = exact_layer(u, g, k)
    print(f"[exact] k={k} K={E['K']} pieces={len(E['pieces'])} T={float(E['T'])}")
    print(f"[exact] c2={float(E['c2'])!r} mu={float(E['mu'])!r} var={float(E['var'])!r} rho3={float(E['rho3'])!r}")
    print(f"[exact] G(T)^2/c2 = {float(E['Gn'][-1]**2/E['c2'])!r}  (crude, un-truncated ceiling of this g)")
    print(f"[exact] layer done in {time.time()-t0:.2f}s")

    C_main = Fr("0.56")
    C_variants = [Fr("0.4748"), Fr("0.56"), Fr("0.7056"), Fr("0.7915"), Fr("0.7975")]
    backends = []
    if args.backend in ("arb", "both"):
        backends.append(ArbBackend(200))
    if args.backend in ("mpmath", "both"):
        backends.append(MpmathBackend(200))

    results = {}
    for IV in backends:
        t1 = time.time()
        R = interval_layer(E, k, IV, C_variants, use_erfc=isinstance(IV, ArbBackend))
        lo, hi, chain = assemble(E, R, C_main)
        res = dict(backend=IV.name, prec_bits=IV.prec,
                   cert_lo_exact=f"{lo.numerator}/{lo.denominator}",
                   cert_lo_dec_down=frac_to_dec(lo, 30, "down"),
                   cert_hi_dec_up=frac_to_dec(hi, 30, "up"),
                   margin_dec_down=frac_to_dec(lo - thr, 30, "down"),
                   PASS=bool(lo > thr),
                   time_s=round(time.time() - t1, 2), t_mgf_s=round(R["t_mgf"], 2), t_nodes_s=round(R["t_nodes"], 2),
                   strategy_counts={}, variants={})
        for c in chain:
            res["strategy_counts"][c["strategy"]] = res["strategy_counts"].get(c["strategy"], 0) + 1
        for C in C_variants:
            l2, h2, _ = assemble(E, R, C)
            res["variants"][f"C_BE={C}"] = dict(lo=frac_to_dec(l2, 20, "down"), hi=frac_to_dec(h2, 20, "up"), PASS=bool(l2 > thr))
        l3, h3, _ = assemble(E, R, C_main, use_BE=False)
        res["variants"]["Chernoff_only_no_BE"] = dict(lo=frac_to_dec(l3, 20, "down"), hi=frac_to_dec(h3, 20, "up"), PASS=bool(l3 > thr))
        if isinstance(IV, ArbBackend):
            l4, h4, _ = assemble(E, R, C_main, be_key="BE_erfc")
            res["variants"]["C_BE=0.56_with_rigorous_erfc_Phibar"] = dict(lo=frac_to_dec(l4, 20, "down"), hi=frac_to_dec(h4, 20, "up"), PASS=bool(l4 > thr))
        res["node_chain"] = chain
        results[IV.name] = res
        print(f"[{IV.name}] certificate M_{k} >= {res['cert_lo_dec_down']}  (formula value <= {res['cert_hi_dec_up']})")
        print(f"[{IV.name}] margin over {thr}: {res['margin_dec_down']}   PASS={res['PASS']}   time {res['time_s']}s")
        print(f"[{IV.name}] strategies: {res['strategy_counts']}")
        for name, v in res["variants"].items():
            print(f"[{IV.name}]   variant {name}: lo={v['lo']} PASS={v['PASS']}")

    tup = None
    if not args.skip_tuple:
        t2 = time.time()
        tup = check_tuple(args.tuple, k)
        tup["time_s"] = round(time.time() - t2, 2)
        print(f"[tuple] count={tup['count']} sorted/distinct={tup['distinct_sorted']} diameter={tup['diameter']} "
              f"admissible={tup['admissible']} (primes tested: {tup['primes_tested']}, largest {tup['largest_prime_tested']})")

    out = dict(
        task="Fable overnight D1: outward-rounded certificate for the H2 record (k=15856)",
        date="2026-09-05",
        k=k, K=E["K"], threshold=str(thr),
        criterion="Maynard: DHL(k,m+1) if M_k > 2m/theta; Bombieri-Vinogradov theta<1/2 arbitrary => M_k > 4m; m=2 => M_k > 8",
        certificate_statement=f"M_{k} >= cert_lo (exact rational below) > 8, hence DHL({k},3), hence liminf(p_(n+2)-p_n) <= H({k}) <= diameter of the tuple",
        profile=dict(file=args.npz, sha256=hashlib.sha256(open(args.npz, "rb").read()).hexdigest(),
                     n_nodes=len(u), T=str(E["T"]), u_hex=[float(x).hex() for x in u_np.tolist()],
                     g_hex=[float(x).hex() for x in g_np.tolist()]),
        exact_constants=dict(c2=f"{E['c2'].numerator}/{E['c2'].denominator}", mu_dec=frac_to_dec(E["mu"], 30, "down"),
                             var_dec=frac_to_dec(E["var"], 30, "down"), rho3_dec=frac_to_dec(E["rho3"], 30, "down"),
                             GT2_over_c2_dec=frac_to_dec(E["Gn"][-1] ** 2 / E["c2"], 30, "down")),
        tail_bound_parameters=dict(B_fractions_of_T=B_FRACS, lam_grid="10^(e/8)/T rounded to float64, e in [-24,44]",
                                   lam_hex=[float(l).hex() for l in E["lams"]], lam_B_cutoff=str(LAM_B_CUTOFF),
                                   BE_constant_main=str(C_main),
                                   BE_constants_tested=[str(c) for c in C_variants],
                                   Phibar_bounds="min(exp(-z^2/2)/(z sqrt(2 pi)), exp(-z^2/2)/2), z>0 (elementary); arb erfc variant informational only"),
        backends=results,
        tuple=tup,
        conventions="beta_ub uses the UPPER endpoint of every interval; certificate uses w_j = 1 - beta_ub_j exactly; "
                    "cert_lo is an exact rational (printed rounded down); cert_hi is the upper end of the same formula (rounded up).",
    )
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {args.out}   total time {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
