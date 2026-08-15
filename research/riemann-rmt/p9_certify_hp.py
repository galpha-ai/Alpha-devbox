#!/usr/bin/env python3
"""P9: high-precision (mpmath, dps=50) certificate for M_k >= threshold.

Certifies the fixed piecewise-linear g stored in p9_g_k{K}.npz via
  M_k >= (1/c2) * sum_j w_lb(b_j) * (G(b_j)^2 - G(a_j)^2),
  w_lb(u) = max(0, 1 - beta(u)),
  beta(u) = min( BE bound , min_{B,lam} [C(K,2) q_B^2 + e^{-lam(s-gap)} MGF_B(lam)^K] ),
with every ingredient computed by exact polynomial integration in mpmath
(g pw-linear => all integrands polynomial; e^{lam t} majorized by its chord).
BE bound: P(S_K > s) <= Phibar(z) + C_BE * rho3 / (sigma^3 sqrt(K)),
z = (s - K mu)/(sqrt(K var_hi)), Phibar via mpmath.erfc (primary) and the
elementary bound min( exp(-z^2/2)/(z sqrt(2pi)), exp(-z^2/2)/2 ) (secondary).
C_BE = 0.56 (safe; also reports 0.4748).
All comparisons carry a relative safety factor 1e-30.
"""
import numpy as np
from mpmath import mp, mpf, exp, log, sqrt, erfc, pi, binomial

mp.dps = 50
SAFE = mpf(1) + mpf(10) ** (-30)


def poly_int(coeffs, a, b):
    """integral of sum c_i t^i over [a,b]."""
    s = mpf(0)
    for i, c in enumerate(coeffs):
        s += c * (b ** (i + 1) - a ** (i + 1)) / (i + 1)
    return s


def gsq_coeffs(a, ga, gb, du):
    """g(t) = ga + s(t-a), s=(gb-ga)/du; returns coeffs of g(t)^2 in t."""
    s = (gb - ga) / du
    c0 = (ga - s * a)
    # g = c0 + s t; g^2 = c0^2 + 2 c0 s t + s^2 t^2
    return [c0 * c0, 2 * c0 * s, s * s]


def certify(npzfile, threshold, C_BE=mpf("0.56"), use_erfc=True, nlam=40, nB=8, verbose=True):
    d = np.load(npzfile)
    u_np, g_np, k, T_np = d["u"], d["g"], int(d["k"]), float(d["T"])
    u = [mpf(float(x)) for x in u_np]
    g = [mpf(float(x)) for x in g_np]
    n = len(u) - 1
    K = k - 1
    T = u[-1]
    pieces = []
    for j in range(n):
        a, b, ga, gb = u[j], u[j + 1], g[j], g[j + 1]
        du = b - a
        if du <= 0:
            continue
        pieces.append((a, b, ga, gb, du, gsq_coeffs(a, ga, gb, du)))
    # c2, G nodes
    c2 = mpf(0)
    Gn = [mpf(0)]
    for (a, b, ga, gb, du, cs) in pieces:
        c2 += poly_int(cs, a, b)
        Gn.append(Gn[-1] + du * (ga + gb) / 2)
    # moments
    m1 = sum(poly_int([0] + cs, a, b) for (a, b, ga, gb, du, cs) in pieces) / c2
    m2 = sum(poly_int([0, 0] + cs, a, b) for (a, b, ga, gb, du, cs) in pieces) / c2
    var = m2 - m1 * m1
    # rho3 exact: split at m1
    rho3 = mpf(0)
    for (a, b, ga, gb, du, cs) in pieces:
        for (lo, hi, sign) in ((a, min(b, m1), -1), (max(a, m1), b, 1)) if a < m1 < b else (((a, b, 1 if a >= m1 else -1),)):
            if hi <= lo:
                continue
            # |t-m1|^3 = sign*(t-m1)^3 ; expand (t-m1)^3 * g^2
            # (t-m1)^3 = t^3 -3 m1 t^2 + 3 m1^2 t - m1^3
            cub = [-m1 ** 3, 3 * m1 ** 2, -3 * m1, mpf(1)]
            prod = [mpf(0)] * (len(cub) + len(cs) - 1)
            for i, ci in enumerate(cub):
                for jj, cj in enumerate(cs):
                    prod[i + jj] += ci * cj
            rho3 += sign * poly_int(prod, lo, hi)
    rho3 = rho3 / c2
    var_hi = var * SAFE
    var_lo = var / SAFE
    sK = sqrt(mpf(K))

    def phibar_upper(z):
        vals = []
        if use_erfc:
            vals.append(erfc(z / sqrt(mpf(2))) / 2 * SAFE)
        if z > 0:
            e = exp(-z * z / 2)
            vals.append(e / (z * sqrt(2 * pi)) * SAFE)
            vals.append(e / 2 * SAFE)
        return min(vals) if vals else mpf(1)

    be_term = C_BE * rho3 * SAFE / (var_lo ** mpf("1.5") * sK)

    # precompute per-B: qmass, chord data
    def mgf_upper_log(lam, B):
        tot = mpf(0)
        for (a, b, ga, gb, du, cs) in pieces:
            if a >= B:
                tot += poly_int(cs, a, b)  # Y=0 part
                continue
            hi = min(b, B)
            P0 = poly_int(cs, a, hi)
            # P1 = int (t-a)/(hi-a) g^2
            shifted = [cs[0] + cs[1] * a + cs[2] * a * a,  # not needed; do direct
                       ]
            # direct: (t-a) * g^2 coeffs
            tg = [-a * cs[0], cs[0] - a * cs[1], cs[1] - a * cs[2], cs[2]]
            P1 = poly_int(tg, a, hi) / (hi - a)
            tot += exp(lam * a) * (P0 - P1) + exp(lam * hi) * P1
            if b > B:
                tot += poly_int(cs, B, b)
        return log(tot * SAFE / c2)

    def qtail(B):
        t = mpf(0)
        for (a, b, ga, gb, du, cs) in pieces:
            if b <= B:
                continue
            t += poly_int(cs, max(a, B), b)
        return t * SAFE / c2

    Bs = [T * mpf(f) for f in ("0.005", "0.02", "0.06", "0.12", "0.2", "0.35", "0.55", "0.75", "1.0")][:nB + 3]
    # lambda scaled to T: lam = c/T, c from 1e-3 to ~300 (log grid, 8 per decade)
    lam_grid = [(mpf(10) ** (mpf(e) / 8)) / T for e in range(-24, 45)]
    mgf_cache = {}
    q_cache = {}
    logC2b = log(mpf(K) * (K - 1) / 2)

    def beta(uv):
        s = mpf(k) - uv
        best = mpf(1)
        # BE
        z = (s - K * m1) / sqrt(K * var_hi)
        if z > 0:
            best = min(best, phibar_upper(z) + be_term)
        # Chernoff / big jump
        for B in Bs:
            plain = (B == T)
            gap = mpf(0) if plain else T
            se = s - gap
            if se <= 0:
                continue
            if B not in q_cache:
                q_cache[B] = qtail(B) if not plain else mpf(0)
            pN2 = mpf(0)
            if not plain:
                q = q_cache[B]
                pN2 = exp(logC2b + 2 * log(q)) if q > 0 else mpf(0)
            for lam in lam_grid:
                if lam * B > 300:
                    break
                key = (B, lam)
                if key not in mgf_cache:
                    mgf_cache[key] = mgf_upper_log(lam, B)
                expo = -lam * se + K * mgf_cache[key]
                if expo < 300:
                    cand = pN2 + exp(min(expo, mpf(0)))
                    if cand < best:
                        best = cand
        return best

    total = mpf(0)
    for j in range(len(pieces)):
        b = pieces[j][1]
        w = 1 - beta(b) * SAFE
        if w > 0:
            idx = j + 1
            total += w * (Gn[idx] ** 2 - Gn[idx - 1] ** 2)
    cert = total / (c2 * SAFE)
    ok = cert > mpf(threshold) * SAFE
    if verbose:
        print(f"file={npzfile} k={k}: HP certificate M_k >= {mp.nstr(cert, 12)}  threshold {threshold}  PASS={ok}")
        print(f"   mu={mp.nstr(m1,8)} var={mp.nstr(var,8)} rho3={mp.nstr(rho3,8)} c2={mp.nstr(c2,8)} G(T)^2/c2={mp.nstr(Gn[-1]**2/c2,8)}")
    return cert, ok


if __name__ == "__main__":
    import sys
    f = sys.argv[1]; th = float(sys.argv[2])
    for cbe, ue, tag in [(mpf("0.56"), True, "C_BE=0.56, erfc"),
                         (mpf("0.4748"), True, "C_BE=0.4748, erfc"),
                         (mpf("0.56"), False, "C_BE=0.56, elementary Phibar only")]:
        print(f"--- {tag}")
        certify(f, th, C_BE=cbe, use_erfc=ue)
