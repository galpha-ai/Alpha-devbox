#!/usr/bin/env python3
"""PROVENANCE COPY (Fable overnight, task D1, 2026-09-05).

Verbatim copy of the UNCOMMITTED scratchpad script  scratchpad/p9_exact_cert.py
sha256(original) = 496c3d808a25d39395c81038ce4c489bc628e4180cfedcb940af429060394b76
This is the python-flint/arb (ball-arithmetic) certifier that actually produced
research/riemann-rmt/p9_exact_cert_k15856.json (the JSON carries the key
"arb_precision_bits": 200 and arb-style ball strings).  The committed
p9_certify_hp.py is the mpmath(dps=50)+SAFE-factor version, which is why the
Astra audit could not see outward-rounded arithmetic in the committed code.
Copied unchanged below (only this header added) so that the record can be replayed;
the independent re-certification lives in r1_h2_interval_cert.py.
"""
"""P9: interval-arithmetic (flint/arb, outward-rounded) certificate for M_k >= threshold.

Every quantity is an arb ball rigorously containing the exact value of the
corresponding formula; every inequality is applied against the adverse
endpoint (upper endpoint for tail bounds beta, lower endpoint for the final
certificate). Only the elementary normal-tail bounds are used
(Phibar(z) <= min(exp(-z^2/2)/(z sqrt(2 pi)), exp(-z^2/2)/2)); no erfc.
Berry-Esseen constant C_BE = 0.56 (safe, non-iid value; Shevtsova 2010).

Chain (g >= 0 pw-linear on [0,T], c2 = int g^2, X iid ~ g^2/c2, K = k-1):
  M_k >= (1/c2) sum_j w_j (G(b_j)^2 - G(a_j)^2),   w_j = max(0, 1 - beta(b_j))
  beta(u) >= P(S_K > k-u) via:
   (BE)  Phibar((s-K mu)/sqrt(K var)) + C_BE rho3/(var^{3/2} sqrt(K))
   (CH)  min_{B,lam} [ K(K-1)/2 * q_B^2 + exp(-lam(s-gap)) MGF_B(lam)^K ],
         gap = T for B<T (one big jump), 0 for B=T;
         MGF_B chord-majorized on each linear piece (convexity of e^{lam t}).
All integrals are of polynomials (exact antiderivatives, evaluated in ball
arithmetic).
"""
import numpy as np
import json, sys
from flint import arb, ctx

ctx.prec = 200


def ub(x):  # adverse upper endpoint as exact arb
    return arb(x.upper())


def lb(x):
    return arb(x.lower())


def poly_int(coeffs, a, b):
    s = arb(0)
    for i, c in enumerate(coeffs):
        s += c * (b ** (i + 1) - a ** (i + 1)) / (i + 1)
    return s


def certify(npzfile, threshold, C_BE="0.56", outfile=None):
    d = np.load(npzfile)
    u_np, g_np, k = d["u"], d["g"], int(d["k"])
    C_BE = arb(C_BE)
    K = k - 1
    u = [arb(float(x)) for x in u_np]   # float64 -> exact binary rational -> arb exact
    g = [arb(float(x)) for x in g_np]
    T = u[-1]
    pieces = []
    for j in range(len(u) - 1):
        a, b, ga, gb = u[j], u[j + 1], g[j], g[j + 1]
        du = b - a
        s = (gb - ga) / du
        c0 = ga - s * a
        cs = [c0 * c0, 2 * c0 * s, s * s]      # g(t)^2 coefficients
        pieces.append((a, b, ga, gb, du, cs))
    c2 = arb(0)
    Gn = [arb(0)]
    for (a, b, ga, gb, du, cs) in pieces:
        c2 += poly_int(cs, a, b)
        Gn.append(Gn[-1] + du * (ga + gb) / 2)
    m1 = sum(poly_int([arb(0)] + cs, a, b) for (a, b, ga, gb, du, cs) in pieces) / c2
    m2 = sum(poly_int([arb(0), arb(0)] + cs, a, b) for (a, b, ga, gb, du, cs) in pieces) / c2
    var = m2 - m1 * m1
    rho3 = arb(0)
    for (a, b, ga, gb, du, cs) in pieces:
        segs = []
        if bool(b <= m1):
            segs = [(a, b, -1)]
        elif bool(a >= m1):
            segs = [(a, b, 1)]
        else:
            segs = [(a, m1, -1), (m1, b, 1)]
        for (lo, hi, sign) in segs:
            cub = [-m1 ** 3, 3 * m1 ** 2, -3 * m1, arb(1)]
            prod = [arb(0)] * 6
            for i, ci in enumerate(cub):
                for jj, cj in enumerate(cs):
                    prod[i + jj] += ci * cj
            rho3 += sign * poly_int(prod, lo, hi)
    rho3 = rho3 / c2
    sqrtK = arb(K).sqrt()
    be_term = ub(C_BE * rho3 / (var ** (arb(3) / 2) * sqrtK))
    twopi = 2 * arb.pi()

    def phibar_ub(z):
        # valid rigorous upper bounds for z>0
        e = (-z * z / 2).exp()
        v1 = e / (z * twopi.sqrt())
        v2 = e / 2
        return ub(v1) if bool(v1 < v2) else ub(v2)

    def mgf_log_ub(lam, B):
        tot = arb(0)
        for (a, b, ga, gb, du, cs) in pieces:
            if bool(a >= B):
                tot += poly_int(cs, a, b)
                continue
            hi = b if bool(b <= B) else B
            P0 = poly_int(cs, a, hi)
            tg = [-a * cs[0], cs[0] - a * cs[1], cs[1] - a * cs[2], cs[2]]
            P1 = poly_int(tg, a, hi) / (hi - a)
            tot += (lam * a).exp() * (P0 - P1) + (lam * hi).exp() * P1
            if bool(b > B):
                tot += poly_int(cs, B, b)
        return ub((tot / c2).log())

    def qtail(B):
        t = arb(0)
        for (a, b, ga, gb, du, cs) in pieces:
            if bool(b <= B):
                continue
            lo = a if bool(a >= B) else B
            t += poly_int(cs, lo, b)
        return ub(t / c2)

    Bs = [ub(T * arb(f)) for f in ("0.005", "0.02", "0.06", "0.12", "0.2", "0.35", "0.55", "0.75")] + [T]
    lam_grid = [arb(10) ** (arb(e) / 8) / T for e in range(-24, 45)]
    mgf_cache, q_cache = {}, {}
    logC2b = (arb(K) * (K - 1) / 2).log()

    nodes = []
    total = arb(0)
    for j in range(len(pieces)):
        bnode = pieces[j][1]
        s = arb(k) - bnode
        best = arb(1)
        tag = "none"
        z = (s - K * m1) / (K * var).sqrt()
        if bool(z > 0):
            cand = phibar_ub(z) + be_term
            if bool(cand < best):
                best, tag = ub(cand), "BE"
        for bi, B in enumerate(Bs):
            plain = (bi == len(Bs) - 1)
            gap = arb(0) if plain else T
            se = s - gap
            if not bool(se > 0):
                continue
            if bi not in q_cache:
                q_cache[bi] = qtail(B) if not plain else arb(0)
            q = q_cache[bi]
            pN2 = arb(0)
            if not plain:
                if bool(q > 0):
                    pN2 = ub((logC2b + 2 * q.log()).exp())
            for li, lam in enumerate(lam_grid):
                if bool(lam * B > 300):
                    break
                key = (bi, li)
                if key not in mgf_cache:
                    mgf_cache[key] = mgf_log_ub(lam, B)
                expo = -lam * se + K * mgf_cache[key]
                if bool(expo < 40):
                    zero = arb(0)
                    ee = expo if bool(expo < zero) else zero
                    cand = pN2 + ub(ee.exp())
                    if bool(cand < best):
                        best, tag = ub(cand), f"CH(B={bi},lam={li})"
        w = 1 - best
        dG2 = Gn[j + 1] ** 2 - Gn[j] ** 2
        contrib = arb(0)
        if bool(w > 0):
            contrib = lb(w) * dG2
            total += contrib
        nodes.append(dict(u=float(bnode.mid()), beta_ub=float(arb(best.upper()).mid()),
                          strategy=tag, contrib_lb=float(arb(contrib.lower()).mid())))
    cert = total / c2
    cert_lower = float(arb(cert.lower()).mid())
    ok = bool(cert > arb(threshold))
    result = dict(k=k, threshold=threshold, certificate_lower_bound=cert_lower,
                  PASS=ok, C_BE=str(C_BE),
                  c2=[float(arb(c2.lower()).mid()), float(arb(c2.upper()).mid())],
                  mu=[float(arb(m1.lower()).mid()), float(arb(m1.upper()).mid())],
                  var=[float(arb(var.lower()).mid()), float(arb(var.upper()).mid())],
                  rho3=[float(arb(rho3.lower()).mid()), float(arb(rho3.upper()).mid())],
                  arb_precision_bits=200,
                  tail_bounds="elementary only: Phibar(z) <= min(exp(-z^2/2)/(z sqrt(2pi)), exp(-z^2/2)/2); Chernoff chord-majorized MGF; one-big-jump union bound; Berry-Esseen C=" + str(C_BE),
                  g_nodes_hex=[float(x).hex() for x in u_np.tolist()],
                  g_values_hex=[float(x).hex() for x in g_np.tolist()],
                  node_chain=nodes)
    print(f"k={k}: ARB certificate M_k >= {cert_lower:.10f}  (threshold {threshold})  PASS={ok}")
    if outfile:
        with open(outfile, "w") as f:
            json.dump(result, f, indent=1)
        print("wrote", outfile)
    return cert_lower, ok


if __name__ == "__main__":
    certify(sys.argv[1], float(sys.argv[2]), outfile=(sys.argv[3] if len(sys.argv) > 3 else None))
