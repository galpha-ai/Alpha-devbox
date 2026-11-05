#!/usr/bin/env python3
"""
refute_D1_rigour.py -- adversarial refuter checks for task D1 (Fable overnight, 2026-09-05).

Target: overnight/fable/r1_h2_interval_cert.md and scripts/r1_h2_interval_cert.py
(the outward-rounded certificate M_15856 > 8 for the H2 record).  Lens: rigour of the
certificate / criterion.  Nothing here is a proof; it is an independent attempt to BREAK
the certificate.  Checks:

  C1  DHL criterion normalisation (Maynard Prop. 4.1: r_k = ceil(theta*M_k/2); m=2, theta<1/2 arbitrary
      => need M_k > 8 strictly) and the theta actually needed for the certified numbers.
  C2  Independent exact layer (own fractions code): c2, mu, sigma^2, rho3, G at nodes, dG2 vs JSON.
  C3  TRUE tail probabilities P(S_K >= k-u_j) at all 399 nodes by numerical inversion of the
      characteristic function phi(xi)^K (Poisson-summation-exact trapezoid rule; non-rigorous but
      ~1e-12 accurate).  Every certified beta_ub_j must dominate the truth; and the true
      layer-cake value E[G((k-S_K)_+)^2]/(c2 P(S_k<=k)) must exceed the certified number.
  C4  Independent recomputation (mpmath, 60 digits, own code) of the chord-Chernoff and BE bounds at
      the recorded (B, lambda) per node; comparison with the exact-MGF Chernoff bound at the same
      lambda (chord bound must be >= exact-MGF bound, exact-MGF bound must be >= true tail).
  C5  Re-assembly of sum_j (1-beta_ub_dec_up_j) dG2_j / c2 from the JSON's 40-digit upper-rounded
      betas and my own exact dG2/c2 -> must be > 8 (arb and mpmath backends).
  C6  Independent admissibility / diameter / distinctness check of p9_tuple_k15856.npy for ALL
      primes p <= k (own sieve, sympy prime list cross-check).
  C7  Source scan of r1_h2_interval_cert.py for non-outward operations on the rigorous path.
  C8  Monte-Carlo sanity check of the CF machinery (mean/sd of S_K and two tail values).

Usage:  python3 refute_D1_rigour.py  [--quick]
Writes: overnight/fable/data/refute_D1_rigour.log (also printed).
"""
import hashlib
import json
import math
import re
import sys
import time
from fractions import Fraction as Fr

import mpmath as mp
import numpy as np

import argparse

RR = "/home/user/Alpha-devbox/research/riemann-rmt"
FAB = f"{RR}/overnight/fable"
_ap = argparse.ArgumentParser()
_ap.add_argument("--npz", default=f"{RR}/p9_g_k15856.npz")
_ap.add_argument("--tuple", default=f"{RR}/p9_tuple_k15856.npy")
_ap.add_argument("--cert", default=f"{FAB}/data/h2_k15856_interval_cert.json")
_ap.add_argument("--log", default=f"{FAB}/data/refute_D1_rigour.log")
_ap.add_argument("--threshold", type=int, default=8)
_ap.add_argument("--m", type=int, default=2, help="number of extra primes (DHL(k,m+1))")
_ap.add_argument("--skip-tuple", action="store_true")
_ap.add_argument("--quick", action="store_true")
ARGS = _ap.parse_args()
NPZ, TUP, CERT, LOG = ARGS.npz, ARGS.tuple, ARGS.cert, ARGS.log

_log_lines = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    _log_lines.append(s)


def frac_dec(fr, nd=30):
    """decimal string (truncated toward zero) of a Fraction."""
    sign = "-" if fr < 0 else ""
    x = abs(fr) * 10 ** nd
    n = x.numerator // x.denominator
    s = str(n).rjust(nd + 1, "0")
    return sign + s[:-nd] + "." + s[-nd:]


# ------------------------------------------------------------------------------------------------
# C1: criterion normalisation
# ------------------------------------------------------------------------------------------------
def check_criterion(cert_lo_BE, cert_lo_noBE, m=2):
    log("== C1: DHL criterion normalisation ==")
    thr = 4 * m
    log("Maynard (Ann. Math. 181 (2015) Prop. 4.1, recalled; not verified online): level of distribution theta,")
    log("  r_k = ceil(theta * M_k / 2) primes among n+h_i infinitely often.  r_k >= 3 <=> theta*M_k/2 > 2 <=> M_k > 4/theta.")
    log("Polymath 8b Thm 3.5(i) form (recalled): EH[theta] and M_k > 2m/theta => DHL[k,m+1]; m=2 => M_k > 4/theta.")
    log("Both agree.  Bombieri-Vinogradov: EH[theta] for every theta < 1/2 (recalled) => need M_k > 8 STRICTLY,")
    log("  and then theta := any value in (4/M_k, 1/2) works.")
    log(f"  m = {m}: need M_k > 2m/theta = {2*m}/theta; theta < 1/2 arbitrary => M_k > {thr} strictly.")
    for name, v in (("BE, C=0.56", cert_lo_BE), ("BE-free", cert_lo_noBE)):
        th = 2 * m / v
        log(f"  certified {name}: M_k >= {frac_dec(v, 20)} -> needs theta > {frac_dec(th, 8)} ; < 1/2 ? {th < Fr(1, 2)} ; > {thr} ? {v > thr}")
    log("  consistency with the historical scan: p9_scan.py mode pure2 bisected 'certified > 8.0 + 1e-6' (read from source).")
    log("  epsilon-trick / vanishing-marginal / cap: NOT used by the certifier (F = prod g(k t_i) * 1[sum t_i <= 1]) -> no extra constraint to check.")
    return True


# ------------------------------------------------------------------------------------------------
# C2: independent exact layer
# ------------------------------------------------------------------------------------------------
def load():
    d = np.load(NPZ)
    u = [Fr(float(x)) for x in d["u"].tolist()]
    g = [Fr(float(x)) for x in d["g"].tolist()]
    k = int(d["k"])
    T = Fr(float(d["T"]))
    assert T == u[-1]
    return u, g, k, T


def pint(c, a, b):
    return sum(ci * (b ** (i + 1) - a ** (i + 1)) / (i + 1) for i, ci in enumerate(c) if ci)


def exact_layer(u, g):
    """own implementation: g(t) = ga + s*(t-a) on [a,b]; everything as Fractions."""
    n = len(u) - 1
    pcs = []
    for j in range(n):
        a, b, ga, gb = u[j], u[j + 1], g[j], g[j + 1]
        s = (gb - ga) / (b - a)
        # g^2 as polynomial in t (not in t-a): expand (ga - s a + s t)^2
        c0 = ga - s * a
        q = [c0 * c0, 2 * c0 * s, s * s]
        pcs.append((a, b, ga, gb, s, q))
    c2 = sum(pint(q, a, b) for (a, b, ga, gb, s, q) in pcs)
    m1 = sum(pint([Fr(0)] + q, a, b) for (a, b, ga, gb, s, q) in pcs) / c2
    m2 = sum(pint([Fr(0), Fr(0)] + q, a, b) for (a, b, ga, gb, s, q) in pcs) / c2
    var = m2 - m1 * m1
    # rho3: exact, splitting at mu
    rho3 = Fr(0)
    cub = [-m1 ** 3, 3 * m1 ** 2, -3 * m1, Fr(1)]
    for (a, b, ga, gb, s, q) in pcs:
        # multiply polynomials
        pr = [Fr(0)] * 6
        for i, ci in enumerate(cub):
            for jj, cj in enumerate(q):
                pr[i + jj] += ci * cj
        if b <= m1:
            rho3 -= pint(pr, a, b)
        elif a >= m1:
            rho3 += pint(pr, a, b)
        else:
            rho3 += pint(pr, m1, b) - pint(pr, a, m1)
    rho3 /= c2
    G = [Fr(0)]
    for (a, b, ga, gb, s, q) in pcs:
        G.append(G[-1] + (b - a) * (ga + gb) / 2)
    dG2 = [G[j + 1] ** 2 - G[j] ** 2 for j in range(n)]
    return dict(pcs=pcs, c2=c2, mu=m1, m2=m2, var=var, rho3=rho3, G=G, dG2=dG2)


# ------------------------------------------------------------------------------------------------
# C3: true tails via characteristic function
# ------------------------------------------------------------------------------------------------
def gl_nodes(n):
    x, w = np.polynomial.legendre.leggauss(n)
    return x, w


def quad_points(pcs_f, c2f, xi_max, phase_cap=1.0, ngl=12):
    """all Gauss-Legendre nodes t_q and weights W_q = w_q g(t_q)^2/c2, sub-dividing so xi_max*h <= phase_cap."""
    x, w = gl_nodes(ngl)
    ts, ws = [], []
    for (a, b, ga, gb, s) in pcs_f:
        m = max(1, int(math.ceil((b - a) * xi_max / phase_cap)))
        edges = np.linspace(a, b, m + 1)
        for i in range(m):
            lo, hi = edges[i], edges[i + 1]
            t = 0.5 * (hi - lo) * x + 0.5 * (hi + lo)
            gv = ga + s * (t - a)
            ts.append(t)
            ws.append(0.5 * (hi - lo) * w * gv * gv / c2f)
    return np.concatenate(ts), np.concatenate(ws)


def phi_closed_form(pcs_f, c2f, xi):
    """closed-form phi(xi) = sum_pieces e^{i xi a} int_0^h e^{i xi tau} (ga + s tau)^2 dtau / c2 (vectorised in xi)."""
    xi = np.asarray(xi, dtype=float)
    ix = 1j * xi
    tot = np.zeros_like(xi, dtype=complex)
    for (a, b, ga, gb, s) in pcs_f:
        h = b - a
        E = np.exp(ix * h)
        # int_0^h e^{ix tau} tau^n dtau
        I0 = (E - 1) / ix
        I1 = (E * h) / ix - I0 / ix
        I2 = (E * h * h) / ix - 2 * I1 / ix
        tot += np.exp(ix * a) * (ga * ga * I0 + 2 * ga * s * I1 + s * s * I2)
    return tot / c2f


def phi_gl_single(pcs_f, c2f, xi_val):
    """phi(xi) at one xi by Gauss-Legendre with sub-division (robust for all xi; slow for large xi*T)."""
    tq, wq = quad_points(pcs_f, c2f, xi_val, phase_cap=1.0, ngl=12)
    return np.sum(wq * np.exp(1j * xi_val * tq))


def true_tails(E, k, s_list, u_eval, quick=False):
    """returns dict with P(S_K >= s) for s in s_list, P(S_k <= k), and w(u)=P(S_K<k-u) at u_eval, plus diagnostics."""
    K = k - 1
    pcs_f = [(float(a), float(b), float(ga), float(gb), float(s)) for (a, b, ga, gb, s, q) in E["pcs"]]
    c2f = float(E["c2"])
    T = pcs_f[-1][1]
    # --- scan |phi| on [1e-4, 200] to locate where K log|phi| is negligible (closed form)
    xs = np.geomspace(1e-4, 200.0, 20000)
    ph = phi_closed_form(pcs_f, c2f, xs)
    Klog = K * np.log(np.abs(ph))
    # xi_max: smallest xi beyond which K log|phi| < -90 everywhere on the scan
    ok = Klog < -90.0
    # find last index where not ok
    bad_idx = np.where(~ok)[0]
    xi_max = xs[bad_idx[-1]] * 1.5 if len(bad_idx) else xs[0]
    log(f"  |phi| scan (closed form): K log|phi| < -90 for all xi > {xi_max/1.5:.5g} on the scan grid (max K log|phi| on (xi_max,200]: "
        f"{Klog[xs > xi_max].max() if np.any(xs > xi_max) else float('nan'):.1f}); using xi_max = {xi_max:.5g}")
    # confirm the scan with the (cancellation-free) GL evaluation at a few xi beyond xi_max
    conf = []
    for xv in (xi_max, 2 * xi_max, 5 * xi_max, 20 * xi_max, 1.0, 10.0):
        if xv * T > 4e5:
            continue
        conf.append((xv, K * math.log(abs(phi_gl_single(pcs_f, c2f, xv)))))
    log("  GL confirmation of K log|phi| beyond xi_max: " + ", ".join(f"xi={a:.4g}: {b:.1f}" for a, b in conf) + "  (all must be < -90)")
    assert all(b < -90 for a, b in conf)
    # --- main grid (Poisson-exact trapezoid): period L, chosen >> K mu + many sigma
    L = 2.0 ** math.ceil(math.log2(8 * K * float(E["mu"]) + 60 * math.sqrt(K * float(E["var"]))))
    dxi = 2 * math.pi / L
    N = int(math.ceil(xi_max / dxi))
    n = np.arange(1, N + 1)
    xi = n * dxi
    tq, wq = quad_points(pcs_f, c2f, xi_max, phase_cap=1.0, ngl=12)
    log(f"  grid: L={L:.0f}, dxi={dxi:.3e}, N={N}, GL nodes={len(tq)}")
    # phi on the grid, blockwise
    phi = np.zeros(N, dtype=complex)
    blk = 256
    for i in range(0, N, blk):
        x = xi[i:i + blk]
        phi[i:i + blk] = np.exp(1j * np.outer(x, tq)) @ wq
    # cross-check the vectorised GL phi against the single-xi GL evaluation at a few grid points
    idxs = [0, N // 3, 2 * N // 3, N - 1]
    cf = np.array([phi_gl_single(pcs_f, c2f, xi[i]) for i in idxs])
    log(f"  vectorised-vs-single GL phi discrepancy at 4 grid points: {np.abs(cf - phi[idxs]).max():.2e}; "
        f"closed-form-vs-GL at xi_N (closed form is cancellation-prone at tiny xi): {abs(phi_closed_form(pcs_f, c2f, xi[[N-1]])[0] - phi[N-1]):.2e}")
    logphi = np.log(phi)
    cK = np.exp(K * logphi) * dxi / (2 * math.pi)      # coefficients for S_K
    ck = np.exp(k * logphi) * dxi / (2 * math.pi)      # coefficients for S_k

    def tail_ge(c, s):
        """P(S >= s) = (L-s)/L + 2 Re sum_n c_n (e^{-i xi_n s} - 1)/(i xi_n)."""
        s = np.atleast_1d(np.asarray(s, dtype=float))
        out = np.empty(len(s))
        for i, sv in enumerate(s):
            term = c * (np.exp(-1j * xi * sv) - 1.0) / (1j * xi)
            out[i] = (L - sv) / L + 2.0 * term.real.sum()
        return out

    def dens(c, t):
        t = np.atleast_1d(np.asarray(t, dtype=float))
        out = np.empty(len(t))
        for i, tv in enumerate(t):
            out[i] = 1.0 / L + 2.0 * (c * np.exp(-1j * xi * tv)).real.sum()
        return out

    # diagnostics: wrapped density at 0 and L (should be ~0), mean and variance
    d0 = dens(cK, [0.0, 1.0, L - 1.0])
    log(f"  wrapped density of S_K at t=0,1,L-1: {d0} (should be ~0: no wrap-around mass)")
    # mean and second moment via quadrature of the wrapped density on [0,L] with fine grid near the bulk
    tt = np.linspace(0, L, 2 ** 16 + 1)
    ft = dens(cK, tt) if not quick else None
    if ft is not None:
        mass = np.trapezoid(ft, tt)
        mean = np.trapezoid(tt * ft, tt)
        m2 = np.trapezoid(tt * tt * ft, tt)
        log(f"  S_K wrapped: mass={mass:.12f}, mean={mean:.6f} (K mu = {K*float(E['mu']):.6f}), "
            f"var={m2-mean*mean:.3f} (K var = {K*float(E['var']):.3f}), min density {ft.min():.2e}")
    tails = tail_ge(cK, s_list)
    Pk_le = 1.0 - tail_ge(ck, [float(k)])[0]
    w_eval = 1.0 - tail_ge(cK, [float(k) - float(uu) for uu in u_eval])
    return dict(tails=tails, Pk_le=Pk_le, w_eval=w_eval, tail_ge=tail_ge, dens=dens, cK=cK, xi=xi, L=L)


# ------------------------------------------------------------------------------------------------
# C4: independent mpmath recomputation of the tail bounds at the recorded parameters
# ------------------------------------------------------------------------------------------------
def mp_setup(E, k, dps=60):
    mp.mp.dps = dps
    F = lambda fr: mp.mpf(fr.numerator) / fr.denominator
    pcs = [(F(a), F(b), F(ga), F(gb), F(s)) for (a, b, ga, gb, s, q) in E["pcs"]]
    return F, pcs


def mgf_chord_and_exact(pcs, c2, lam):
    """returns (chord upper bound of E e^{lam X}, exact E e^{lam X}) in mpmath at current dps (round-to-nearest)."""
    chord = mp.mpf(0)
    exact = mp.mpf(0)
    for (a, b, ga, gb, s) in pcs:
        h = b - a
        # P0 = int_a^b g^2, P1 = int_a^b (t-a)/h g^2 with g = ga + s tau, tau = t-a
        P0 = ga * ga * h + ga * s * h ** 2 + s * s * h ** 3 / 3
        P1 = (ga * ga * h ** 2 / 2 + 2 * ga * s * h ** 3 / 3 + s * s * h ** 4 / 4) / h
        chord += mp.e ** (lam * a) * (P0 - P1) + mp.e ** (lam * b) * P1
        # exact: e^{lam a} int_0^h e^{lam tau} (ga + s tau)^2 dtau
        I0 = (mp.e ** (lam * h) - 1) / lam
        I1 = (mp.e ** (lam * h) * h) / lam - I0 / lam
        I2 = (mp.e ** (lam * h) * h * h) / lam - 2 * I1 / lam
        exact += mp.e ** (lam * a) * (ga * ga * I0 + 2 * ga * s * I1 + s * s * I2)
    return chord / c2, exact / c2


# ------------------------------------------------------------------------------------------------
# C6: tuple
# ------------------------------------------------------------------------------------------------
def check_tuple(k):
    import sympy
    t = np.load(TUP)
    vals = t.astype(object).tolist()
    n = len(vals)
    sha = hashlib.sha256(open(TUP, "rb").read()).hexdigest()
    distinct = len(set(vals)) == n
    srt = all(vals[i] < vals[i + 1] for i in range(n - 1))
    diam = max(vals) - min(vals)
    primes = list(sympy.primerange(2, k + 1))
    arr = np.array(vals, dtype=np.int64)
    bad = []
    for p in primes:
        r = np.unique(arr % p)
        if len(r) >= p:
            bad.append(p)
    # extra: also test primes in (k, 2k] (must be automatically fine; catches a wrong k in the file)
    bad_big = []
    for p in sympy.primerange(k + 1, 2 * k):
        if len(np.unique(arr % p)) >= p:
            bad_big.append(p)
    return dict(sha256=sha, n=n, count_ok=(n == k), distinct=distinct, sorted=srt, min=int(min(vals)), max=int(max(vals)),
                diameter=int(diam), n_primes=len(primes), largest_prime=primes[-1], violations=bad, violations_above_k=bad_big,
                admissible=(n == k and distinct and not bad))


# ------------------------------------------------------------------------------------------------
# C7: source scan
# ------------------------------------------------------------------------------------------------
def source_scan():
    src = open(f"{FAB}/scripts/r1_h2_interval_cert.py").read().splitlines()
    hits = []
    for i, line in enumerate(src, 1):
        if re.search(r"\bfloat\(|math\.|np\.(exp|log|sqrt)|mp\.(exp|log|sqrt)\(|SAFE|safety|1e-", line) and not line.strip().startswith("#"):
            hits.append((i, line.strip()))
    return hits


# ------------------------------------------------------------------------------------------------
def main():
    quick = ARGS.quick
    t0 = time.time()
    cert = json.load(open(CERT))
    arbres = cert["backends"]["python-flint arb (ball arithmetic)"]
    mpres = cert["backends"].get("mpmath.iv (interval arithmetic) + 2^-150 guard band")
    cert_lo = Fr(arbres["cert_lo_exact"])
    noBE = Fr(arbres["variants"]["Chernoff_only_no_BE"]["lo"])
    log(f"refute_D1_rigour.py  {time.strftime('%Y-%m-%d %H:%M:%S')}  quick={quick}")
    log(f"certificate JSON: cert_lo (exact) = {frac_dec(cert_lo, 32)} ; BE-free lo = {noBE}")

    check_criterion(cert_lo, noBE, ARGS.m)

    # ---------------- C2 ----------------
    log("== C2: independent exact layer ==")
    u, g, k, T = load()
    K = k - 1
    E = exact_layer(u, g)
    sha_npz = hashlib.sha256(open(NPZ, "rb").read()).hexdigest()
    log(f"  profile sha256 {sha_npz}  (JSON says {cert['profile']['sha256']}) match={sha_npz == cert['profile']['sha256']}")
    log(f"  n_nodes={len(u)} k={k} T={T}  g>=0 at all nodes: {all(x >= 0 for x in g)}  u strictly increasing: {all(u[i] < u[i+1] for i in range(len(u)-1))}")
    log(f"  g(0)={g[0]} g(T)={float(g[-1]):.3e}  max g = {float(max(g))}")
    c2_json = Fr(cert["exact_constants"]["c2"])
    log(f"  c2 exact equal to JSON: {E['c2'] == c2_json}")
    for name, key in (("mu", "mu_dec"), ("var", "var_dec"), ("rho3", "rho3_dec")):
        mine = frac_dec(E[name], 30)
        log(f"  {name}: mine={mine} json={cert['exact_constants'][key]} equal(30 digits)={mine == cert['exact_constants'][key]}")
    GT2 = E["G"][-1] ** 2 / E["c2"]
    log(f"  G(T)^2/c2 = {frac_dec(GT2, 20)} (json {cert['exact_constants']['GT2_over_c2_dec']})")
    log(f"  all dG2 >= 0: {all(x >= 0 for x in E['dG2'])}; sum dG2 / c2 = G(T)^2/c2 check: {sum(E['dG2'])/E['c2'] == GT2}")
    # hex data in JSON identical to file?
    d = np.load(NPZ)
    same_hex = [float(x).hex() for x in d["u"].tolist()] == cert["profile"]["u_hex"] and [float(x).hex() for x in d["g"].tolist()] == cert["profile"]["g_hex"]
    log(f"  JSON hex node data identical to npz: {same_hex}")

    # ---------------- C5 (needs only JSON + dG2) ----------------
    log("== C5: re-assembly from the JSON per-node beta (40-digit upper-rounded decimals) ==")
    for label, res in (("arb", arbres), ("mpmath", mpres)):
        if res is None:
            continue
        chain = res["node_chain"]
        assert len(chain) == len(E["dG2"]) == 399
        tot = Fr(0)
        nBE = 0
        for j, c in enumerate(chain):
            assert abs(c["u"] - float(u[j + 1])) < 1e-12
            b = Fr(c["beta_ub_dec_up"])
            tot += max(Fr(0), 1 - b) * E["dG2"][j]
            nBE += c["strategy"].startswith("BE")
        val = tot / E["c2"]
        log(f"  [{label}] sum (1-beta_ub_dec_up) dG2 / c2 = {frac_dec(val, 30)}  > {ARGS.threshold} ? {val > ARGS.threshold}   (cert_lo_exact = {frac_dec(Fr(res['cert_lo_exact']), 30)}; diff = {float(Fr(res['cert_lo_exact']) - val):.2e}); BE nodes={nBE}")
    # per-node consistency between backends
    if mpres is not None:
        md = max(abs(Fr(a["beta_ub_dec_up"]) - Fr(b["beta_ub_dec_up"])) for a, b in zip(arbres["node_chain"], mpres["node_chain"]))
        log(f"  max |beta_ub(arb) - beta_ub(mpmath)| over nodes = {float(md):.3e}")

    # ---------------- C3 ----------------
    log("== C3: TRUE tail probabilities by characteristic-function inversion (non-rigorous, ~1e-12) ==")
    t1 = time.time()
    nodes_u = [u[j + 1] for j in range(399)]
    s_list = [float(k) - float(uu) for uu in nodes_u]
    # GL points on each piece for the layer-cake integral
    xg, wg = gl_nodes(8)
    u_eval, w_fac = [], []
    for j in range(399):
        a, b = float(u[j]), float(u[j + 1])
        u_eval.extend((0.5 * (b - a) * xg + 0.5 * (b + a)).tolist())
    TT = true_tails(E, k, s_list, u_eval, quick=quick)
    log(f"  CF inversion done in {time.time()-t1:.1f}s")
    tails = TT["tails"]
    chain = arbres["node_chain"]
    beta = np.array([float(Fr(c["beta_ub_dec_up"])) for c in chain])
    viol = np.where(beta < tails - 1e-9)[0]
    ratio = beta / np.maximum(tails, 1e-300)
    log(f"  nodes where certified beta_ub < true tail (tolerance 1e-9): {len(viol)}  {viol[:10].tolist()}   [true-tail accuracy ~1e-12 absolute]")
    log(f"  true tail at first/last nodes: u={float(nodes_u[0])}: {tails[0]:.6e} (beta {beta[0]:.6e});  u={float(nodes_u[-1])}: {tails[-1]:.6e} (beta {beta[-1]:.6e})")
    log(f"  min over nodes of beta_ub/true_tail = {ratio.min():.4f} at node {ratio.argmin()} (u={float(nodes_u[ratio.argmin()])}); max = {ratio.max():.3e}")
    # true layer-cake value
    w_eval = TT["w_eval"]
    Etrue = 0.0
    idx = 0
    G = [float(x) for x in E["G"]]
    for j in range(399):
        a, b, ga, gb, s, q = E["pcs"][j]
        a, b, ga, gb, s = float(a), float(b), float(ga), float(gb), float(s)
        tpts = 0.5 * (b - a) * xg + 0.5 * (b + a)
        gv = ga + s * (tpts - a)
        Gv = G[j] + ga * (tpts - a) + 0.5 * s * (tpts - a) ** 2
        Etrue += 0.5 * (b - a) * np.sum(wg * 2 * Gv * gv * w_eval[idx:idx + 8])
        idx += 8
    c2f = float(E["c2"])
    Pk = TT["Pk_le"]
    Rtrue = Etrue / (c2f * Pk)
    log(f"  P(S_k <= k) = {Pk:.10f};  E[G((k-S_K)_+)^2]/c2 = {Etrue/c2f:.10f};  TRUE ratio k J/I for this F = {Rtrue:.10f}")
    log(f"  certified {float(cert_lo):.10f} <= true ratio ? {float(cert_lo) <= Rtrue}   (slack {Rtrue - float(cert_lo):.6f});  un-truncated ceiling G(T)^2/c2 = {float(GT2):.6f}")
    # Lemma 3 sandwich with TRUE w at nodes: sum w(b_j) dG2 <= E <= sum w(a_j) dG2
    wb = 1.0 - tails
    dG2f = np.array([float(x) for x in E["dG2"]])
    lower = np.sum(wb * dG2f) / c2f
    wa = np.concatenate([[1.0], wb[:-1]])
    upper = np.sum(wa * dG2f) / c2f
    log(f"  Lemma-3 sandwich with TRUE tails: {lower:.8f} <= {Etrue/c2f:.8f} <= {upper:.8f}  -> {lower <= Etrue/c2f + 1e-9 <= upper + 2e-9}")
    # second formula for E via the density: G(T)^2 P(S_K <= k-T) + int_{k-T}^{k} G(k-s)^2 f_K(s) ds
    if not quick:
        sgrid = np.linspace(float(k) - float(T), float(k), 4001)
        fK = TT["dens"](TT["cK"], sgrid)
        # G(k-s) via interpolation of exact G at nodes (G is C^1; use fine piecewise-quadratic evaluation)
        un = np.array([float(x) for x in u])
        gn = np.array([float(x) for x in g])
        Gn = np.array(G)
        uu = float(k) - sgrid
        jj = np.clip(np.searchsorted(un, uu, side="right") - 1, 0, 398)
        a_ = un[jj]
        s_ = (gn[jj + 1] - gn[jj]) / (un[jj + 1] - un[jj])
        Gu = Gn[jj] + gn[jj] * (uu - a_) + 0.5 * s_ * (uu - a_) ** 2
        E2 = G[-1] ** 2 * (1.0 - TT["tail_ge"](TT["cK"], [float(k) - float(T)])[0]) + np.trapezoid(Gu ** 2 * fK, sgrid)
        log(f"  cross-formula E via density: {E2/c2f:.8f} (layer-cake {Etrue/c2f:.8f}); rel diff {abs(E2-Etrue)/Etrue:.2e}")

    # ---------------- C4 ----------------
    log("== C4: independent mpmath (60 dps) recomputation of the recorded bounds; exact-MGF comparison ==")
    F, pcs = mp_setup(E, k, 60)
    c2m = F(E["c2"])
    mu_m, var_m, rho3_m = F(E["mu"]), F(E["var"]), F(E["rho3"])
    Km = mp.mpf(K)
    be_unit = rho3_m / (var_m ** mp.mpf("1.5") * mp.sqrt(Km))
    log(f"  BE unit rho3/(sigma^3 sqrt K) = {mp.nstr(be_unit, 12)};  0.56*unit = {mp.nstr(mp.mpf('0.56')*be_unit, 12)}  (this is the size of the BE error term)")
    Tf = float(T)
    lam_cache = {}
    maxrel = 0.0
    n_chord_lt_exact = 0
    n_exact_lt_true = 0
    worst_exact_vs_true = 0.0
    be_maxrel = 0.0
    for j, c in enumerate(chain):
        strat = c["strategy"]
        s_val = F(Fr(k) - nodes_u[j])
        bj = Fr(c["beta_ub_dec_up"])
        if strat.startswith("CH"):
            m = re.match(r"CH\(B=(\S+)T,lam=10\^\((-?\d+)/8\)/T\)", strat)
            assert m, strat
            assert m.group(1) == "1", f"unexpected truncation B at node {j}: {strat}"
            e = int(m.group(2))
            lam_fr = Fr(float(10.0 ** (e / 8.0) / Tf))
            if e not in lam_cache:
                lam_cache[e] = mgf_chord_and_exact(pcs, c2m, F(lam_fr))
            Mchord, Mexact = lam_cache[e]
            lam = F(lam_fr)
            b_chord = mp.e ** (-lam * s_val + Km * mp.log(Mchord))
            b_exact = mp.e ** (-lam * s_val + Km * mp.log(Mexact))
            rel = abs(b_chord - F(bj)) / F(bj)
            maxrel = max(maxrel, float(rel))
            if b_chord > F(bj) * (1 + mp.mpf(10) ** -40):
                log(f"  !! node {j}: my chord bound {mp.nstr(b_chord, 25)} exceeds certified beta_ub {frac_dec(bj, 25)}")
            if Mchord < Mexact:
                n_chord_lt_exact += 1
            if float(b_exact) < tails[j] * (1 - 1e-9):
                n_exact_lt_true += 1
            worst_exact_vs_true = max(worst_exact_vs_true, tails[j] / float(b_exact))
        else:
            assert strat == "BE_elem", strat
            z = (s_val - Km * mu_m) / mp.sqrt(Km * var_m)
            assert z > 0
            ph = min(mp.e ** (-z * z / 2) / (z * mp.sqrt(2 * mp.pi)), mp.e ** (-z * z / 2) / 2)
            b_be = ph + mp.mpf("0.56") * be_unit
            rel = abs(b_be - F(bj)) / F(bj)
            be_maxrel = max(be_maxrel, float(rel))
            if b_be > F(bj) * (1 + mp.mpf(10) ** -40):
                log(f"  !! node {j}: my BE bound {mp.nstr(b_be, 25)} exceeds certified beta_ub {frac_dec(bj, 25)}")
            # also: the true Phibar(z) (erfc) must be <= elementary bound
            phibar_true = mp.erfc(z / mp.sqrt(2)) / 2
            assert phibar_true <= ph
    log(f"  Chernoff nodes: max rel |my chord bound - certified beta_ub| = {maxrel:.3e}; chord MGF < exact MGF at {n_chord_lt_exact} lambda-values (must be 0)")
    log(f"  Chernoff nodes: exact-MGF Chernoff bound < true tail at {n_exact_lt_true} nodes (must be 0); max true/exactMGF ratio = {worst_exact_vs_true:.4f}")
    log(f"  BE nodes: max rel |my BE bound - certified beta_ub| = {be_maxrel:.3e}")
    for e, (Mc, Me) in sorted(lam_cache.items()):
        log(f"    lam=10^({e}/8)/T: chord MGF = {mp.nstr(Mc, 20)}, exact MGF = {mp.nstr(Me, 20)}, K*(log chord - log exact) = {mp.nstr(Km*(mp.log(Mc)-mp.log(Me)), 6)}")
    # what would the certificate be with EXACT MGF (not chord) at the best lambda? (informational: is chord loss material?)
    # ---------------- C8: Monte Carlo sanity ----------------
    if not quick:
        log("== C8: Monte-Carlo sanity check of the CF machinery ==")
        rng = np.random.default_rng(12345)
        un = np.array([float(x) for x in u]); gn = np.array([float(x) for x in g])
        fine = np.unique(np.concatenate([np.linspace(un[i], un[i + 1], 41) for i in range(399)]))
        gf = np.interp(fine, un, gn)
        pdf = gf * gf
        cdf = np.concatenate([[0.0], np.cumsum(0.5 * (pdf[1:] + pdf[:-1]) * np.diff(fine))])
        cdf /= cdf[-1]
        nsamp = max(200, int(3000 * 15855 / K))
        S = np.zeros(nsamp)
        for i in range(nsamp):
            U = rng.random(K)
            S[i] = np.interp(U, cdf, fine).sum()
        log(f"  MC (n={nsamp}): mean S_K = {S.mean():.1f} +- {S.std()/math.sqrt(nsamp):.1f} (K mu = {K*float(E['mu']):.1f}); sd = {S.std():.1f} (sqrt(K var) = {math.sqrt(K*float(E['var'])):.1f})")
        for sv in (float(k) - float(T), float(k) - 1000.0, float(k) - 100.0):
            mc = np.mean(S >= sv)
            cf = TT["tail_ge"](TT["cK"], [sv])[0]
            log(f"  P(S_K >= {sv:.2f}): MC {mc:.4f} +- {math.sqrt(mc*(1-mc)/nsamp):.4f}   CF {cf:.6f}")

    # ---------------- C6 ----------------
    if not ARGS.skip_tuple:
        log("== C6: independent tuple check ==")
        t2 = time.time()
        tup = check_tuple(k)
        log(f"  {tup}  ({time.time()-t2:.1f}s)")
        log(f"  JSON tuple sha256 match: {tup['sha256'] == cert['tuple']['sha256']}; admissible & count & distinct: {tup['admissible']}; diameter {tup['diameter']}")
    else:
        log("== C6: tuple check skipped (--skip-tuple) ==")

    # ---------------- C7 ----------------
    log("== C7: source scan of r1_h2_interval_cert.py for float/non-interval ops ==")
    for i, line in source_scan():
        log(f"  L{i}: {line}")
    log("  (assessment in the refuter's structured output)")

    log(f"total time {time.time()-t0:.1f}s")
    open(LOG, "w").write("\n".join(_log_lines) + "\n")


if __name__ == "__main__":
    main()
