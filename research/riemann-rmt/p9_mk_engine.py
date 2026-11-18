#!/usr/bin/env python3
"""
P9: certified lower bounds for the Maynard-Tao variational quantity M_k
(and its coordinate-capped variant M_k^{[alpha]}) at large k, via the
product ansatz  F(t) = prod_i g(k t_i) 1_{sum t_i <= 1}.

Derivation (exact, no approximation):
  Let g >= 0 piecewise linear on [0,T], c2 = int g^2, X iid with density g^2/c2,
  S_j = X_1+...+X_j, G(y) = int_0^{min(y,T)} g.
  I(F) = k^{-k} c2^k P(S_k <= k)
  J(F) = k^{-(k+1)} c2^{k-1} E[ G((k - S_{k-1})_+)^2 ]
  M_k >= k J/I = E[G((k-S_{k-1})_+)^2] / (c2 * P(S_k <= k))
       >= (1/c2) * int_0^T 2 G(u) g(u) * P(S_{k-1} < k-u) du     [layer cake]
       >= (1/c2) * sum_j w_lb(b_j) * (G(b_j)^2 - G(a_j)^2)
  where w_lb(u) = max(0, 1 - beta(u)) and beta(u) is any rigorous upper bound
  on P(S_{k-1} > k-u).  (w decreasing => per-piece bound is exact.)

Tail bounds beta(u), all rigorous:
  (a) Chernoff: beta <= exp(-lam*s) * MGF(lam)^{k-1}, s = k-u,
      MGF upper-bounded by chord-majorizing e^{lam t} on each linear piece.
  (b) one-big-jump: for any B<T:  P(S>s) <= C(k-1,2) q_B^2
        + min_lam exp(-lam*(s-(T-B)))*MGF_B(lam)^{k-1},
      where q_B = P(X>B), Y = X 1[X<=B], MGF_B = E e^{lam Y} = int_0^B e^{lam t} p + q_B.
      (On {N_B<=1}: S <= S_Y + T - ... <= S_Y + (T-B) + B*1... we use S <= S_Y + T,
       conservative: P(S>s) <= P(N>=2) + P(S_Y > s - T).)

Optimization: maximize B(g) = <g, K g>/c2, K(u,v) = w(u v max), by iterating
a discretized symmetric eigenproblem (w recomputed from g each round).
"""
import numpy as np
from numpy.polynomial import polynomial as P

# ---------------- piecewise-linear g utilities ----------------

def make_grid(T, n, dense0=1.0):
    """grid on [0,T]: linear near 0 then log-spaced."""
    n1 = n // 4
    g1 = np.linspace(0, min(dense0, T / 10), n1, endpoint=False)
    g2 = np.geomspace(max(g1[-1] * 1.05, 1e-3), T, n - n1)
    u = np.unique(np.concatenate([g1, g2, [T]]))
    u[0] = 0.0
    return u


def pw_c2_G(u, g):
    """c2 = int g^2 (exact for pw-linear g), G at nodes (exact)."""
    du = np.diff(u)
    ga, gb = g[:-1], g[1:]
    c2 = np.sum(du * (ga * ga + ga * gb + gb * gb) / 3.0)
    Gn = np.concatenate([[0.0], np.cumsum(du * (ga + gb) / 2.0)])
    return c2, Gn


def moments(u, g, c2):
    du = np.diff(u)
    ga, gb = g[:-1], g[1:]
    a, b = u[:-1], u[1:]
    # int t g(t)^2 dt on each piece: g(t) = ga + (gb-ga)*(t-a)/du
    # do with 5-pt Gauss-Legendre exact for deg<=9 (integrand deg 3)
    xs, ws = np.polynomial.legendre.leggauss(5)
    t = 0.5 * (a[:, None] * (1 - xs) + b[:, None] * (1 + xs))
    gg = ga[:, None] + (gb - ga)[:, None] * (t - a[:, None]) / du[:, None]
    m1 = np.sum(0.5 * du[:, None] * ws * t * gg * gg) / c2
    m2 = np.sum(0.5 * du[:, None] * ws * t * t * gg * gg) / c2
    return m1, m2


def _piece_moments(u, g, B):
    """For pieces clipped to [0,B]: returns arrays aa, hi, P0, P1 and scalar qmass,
    where P0_j = int_{aa}^{hi} g^2, P1_j = int_{aa}^{hi} ((t-aa)/(hi-aa)) g^2,
    qmass = int over [B,T] of g^2 (unnormalized).
    Chord bound: int e^{lam t} g^2 over [aa,hi] <= e^{lam aa}(P0-P1) + e^{lam hi} P1."""
    a, b = u[:-1], u[1:]
    du = np.diff(u)
    ga, gb = g[:-1], g[1:]
    xs, ws = np.polynomial.legendre.leggauss(4)
    lo = a.copy()
    hi = np.minimum(b, B)
    mask = hi > lo  # pieces (partially) below B
    aa, hh = lo[mask], hi[mask]
    t = 0.5 * ((hh - aa)[:, None] * xs[None, :] + (hh + aa)[:, None])
    w2 = 0.5 * (hh - aa)[:, None] * ws[None, :]
    gg = ga[mask][:, None] + ((gb - ga)[mask] / du[mask])[:, None] * (t - a[mask][:, None])
    gg2 = gg * gg
    P0 = np.sum(w2 * gg2, axis=1)
    frac = (t - aa[:, None]) / np.where((hh - aa) > 0, (hh - aa), 1.0)[:, None]
    P1 = np.sum(w2 * frac * gg2, axis=1)
    # mass above B
    lo2 = np.maximum(a, B)
    mask2 = b > lo2
    qmass = 0.0
    if np.any(mask2):
        aa2, bb2 = lo2[mask2], b[mask2]
        t2 = 0.5 * ((bb2 - aa2)[:, None] * xs[None, :] + (bb2 + aa2)[:, None])
        w3 = 0.5 * (bb2 - aa2)[:, None] * ws[None, :]
        gg3 = ga[mask2][:, None] + ((gb - ga)[mask2] / du[mask2])[:, None] * (t2 - a[mask2][:, None])
        qmass = np.sum(w3 * gg3 * gg3)
    return aa, hh, P0, P1, qmass


def log_mgf_upper(u, g, c2, lam, B):
    """Rigorous upper bound for log E[e^{lam Y}], Y = X 1[X<=B]. Vectorized over lam."""
    aa, hh, P0, P1, qmass = _piece_moments(u, g, B)
    lam = np.asarray(lam)
    Ea = np.exp(np.outer(lam, aa))
    Eh = np.exp(np.outer(lam, hh))
    tot = Ea @ (P0 - P1) + Eh @ P1 + qmass
    return np.log(tot / c2)


def abs_central_moments(u, g, c2):
    """exact mu, and rigorous sigma^2 = E X^2 - mu^2, rho3 = E|X-mu|^3 (Gauss-exact,
    pieces split at mu so integrand is polynomial)."""
    du = np.diff(u)
    a, b = u[:-1], u[1:]
    ga, gb = g[:-1], g[1:]
    xs, ws = np.polynomial.legendre.leggauss(6)
    # first pass: mu, EX2
    t = 0.5 * (a[:, None] * (1 - xs) + b[:, None] * (1 + xs))
    gg = ga[:, None] + ((gb - ga) / du)[:, None] * (t - a[:, None])
    w2 = 0.5 * du[:, None] * ws
    m1 = np.sum(w2 * t * gg * gg) / c2
    m2 = np.sum(w2 * t * t * gg * gg) / c2
    var = m2 - m1 * m1
    # rho3: split each piece at mu
    edges = np.unique(np.concatenate([u, [np.clip(m1, u[0], u[-1])]]))
    aa, bb = edges[:-1], edges[1:]
    t = 0.5 * (aa[:, None] * (1 - xs) + bb[:, None] * (1 + xs))
    gv = np.interp(t, u, g)
    w3 = 0.5 * (bb - aa)[:, None] * ws
    rho3 = np.sum(w3 * np.abs(t - m1) ** 3 * gv * gv) / c2
    return m1, var, rho3


def tail_prob_ub(u, g, c2, B):
    """q_B = P(X > B) exact-ish (Gauss exact for poly)."""
    a, b = u[:-1], u[1:]
    du = np.diff(u)
    ga, gb = g[:-1], g[1:]
    xs, ws = np.polynomial.legendre.leggauss(4)
    tot = 0.0
    for j in range(len(a)):
        if b[j] <= B:
            continue
        lo = max(a[j], B)
        t = 0.5 * ((b[j] - lo) * xs + (b[j] + lo))
        w2 = 0.5 * (b[j] - lo) * ws
        gg = ga[j] + (gb[j] - ga[j]) * (t - a[j]) / du[j]
        tot += np.sum(w2 * gg * gg)
    return tot / c2


# ---------------- beta(u): rigorous upper bound on P(S_{k-1} > k-u) -------------

from scipy.special import erfc

BE_CONST = 0.4748  # Shevtsova 2011, iid Berry-Esseen constant


def beta_bounds(u_eval, u, g, c2, k, T, nlam=48, nB=10):
    """for each u in u_eval: beta(u) >= P(S_{k-1} > k - u), rigorous."""
    K = k - 1
    s = np.asarray(k - u_eval, dtype=float)  # thresholds
    best = np.ones(len(s))
    # strategy (a): Chernoff with one-big-jump truncations (B grid; B=T is plain)
    Bgrid = np.unique(np.append(np.geomspace(T / 200.0, T, nB), T))
    logC2 = np.log(K * (K - 1) / 2.0)
    for B in Bgrid:
        lam = np.geomspace(1e-3 / max(T, 1.0), 200.0 / B, nlam)
        lmg = log_mgf_upper(u, g, c2, lam, B)
        plain = B >= T * (1 - 1e-9)
        if plain:
            pN2, gap = 0.0, 0.0
        else:
            qB = tail_prob_ub(u, g, c2, B * (1 - 1e-12))
            pN2 = np.exp(logC2 + 2 * np.log(max(qB, 1e-300))) if qB > 0 else 0.0
            gap = T  # on {N_B <= 1}: S <= S_Y + T
        se = s - gap
        with np.errstate(over='ignore'):
            expo = -np.outer(se, lam) + K * lmg[None, :]
        ch = np.exp(np.minimum(np.min(expo, axis=1), 0.0))
        ch[se <= 0] = 1.0
        best = np.minimum(best, pN2 + ch)
    # strategy (b): Berry-Esseen (dominant in the CLT window)
    mu, var, rho3 = abs_central_moments(u, g, c2)
    var_hi, var_lo = var * (1 + 1e-9), var * (1 - 1e-9)
    if var_lo > 0:
        z = (s - K * mu) / np.sqrt(K * var_hi)
        phibar = 0.5 * erfc(z / np.sqrt(2.0))
        be = BE_CONST * rho3 * (1 + 1e-9) / (var_lo ** 1.5 * np.sqrt(K))
        bb = phibar + be
        bb[z <= 0] = 1.0
        best = np.minimum(best, bb)
    return np.minimum(best, 1.0)


# ---------------- certified bound for given g ----------------

def certified_bound(u, g, k, T, safety=1e-9):
    c2, Gn = pw_c2_G(u, g)
    beta = beta_bounds(u, u, g, c2, k, T)
    w = np.maximum(0.0, 1.0 - beta * (1 + safety))
    # per-piece: w at right node * (G(b)^2 - G(a)^2)
    contrib = w[1:] * (Gn[1:] ** 2 - Gn[:-1] ** 2)
    return np.sum(contrib) / c2


def crude_bound(u, g, k, T):
    """8b-style: full G(T)^2 * (1 - P(S_{k-1} > k - T)) / c2."""
    c2, Gn = pw_c2_G(u, g)
    beta = beta_bounds(np.array([T]), u, g, c2, k, T)[0]
    return Gn[-1] ** 2 * max(0.0, 1 - beta) / c2


# ---------------- optimizer ----------------

def param_g(u, A, T1, kappa):
    """g(t) = exp(-(t/T1)^kappa) / (1 + A t), sampled at nodes -> pw-linear."""
    return np.exp(-np.power(u / T1, kappa)) / (1.0 + A * u)


def eval_params(x, k, cap=None, n=260):
    """x = (logA, logT1, logkappa, logTfac); returns certified bound."""
    A = np.exp(x[0]); T1 = np.exp(x[1]); kappa = np.exp(x[2]); Tfac = np.exp(x[3])
    T = T1 * Tfac
    if cap is not None:
        T = min(T, cap)
    if T <= 1e-6:
        return -1.0
    u = make_grid(T, n)
    g = param_g(u, A, T1, kappa)
    return certified_bound(u, g, k, T)


def optimize_parametric(k, cap=None, n=260, verbose=False, x0=None):
    from scipy.optimize import minimize
    L = np.log(k)
    if x0 is None:
        # heuristic init: A ~ L-2.7, T1 ~ e^{L-3}, kappa ~ 2, Tfac ~ 2
        x0 = np.array([np.log(max(L - 2.7, 1.0)), L - 3.0, np.log(2.0), np.log(2.0)])
        if cap is not None and np.exp(x0[1]) > 0.7 * cap:
            x0[1] = np.log(0.7 * cap)
    f = lambda x: -eval_params(x, k, cap=cap, n=n)
    res = minimize(f, x0, method='Nelder-Mead',
                   options=dict(maxfev=260, xatol=1e-4, fatol=1e-7))
    # restart once from solution
    res2 = minimize(f, res.x, method='Nelder-Mead',
                    options=dict(maxfev=160, xatol=1e-5, fatol=1e-8))
    if res2.fun < res.fun:
        res = res2
    if verbose:
        A, T1, kap, Tf = np.exp(res.x)
        print(f"k={k}: best {-res.fun:.6f} at A={A:.3f} T1={T1:.1f} kappa={kap:.3f} T={T1*Tf:.1f}")
    return -res.fun, res.x


def optimize_g(k, T, n=240, iters=8, A0=None, verbose=False):
    u = make_grid(T, n)
    if A0 is None:
        A0 = max(np.log(k) - 2.0, 1.0)
    g = 1.0 / (1.0 + A0 * u)
    mid = 0.5 * (u[:-1] + u[1:])
    h = np.diff(u)
    best_val, best_g = -1, g.copy()
    for it in range(iters):
        c2, Gn = pw_c2_G(u, g)
        beta = beta_bounds(mid, u, g, c2, k, T)
        w = np.maximum(0.0, 1.0 - beta)
        # kernel on midpoints: K_ij = w(max(mi,mj)); symmetric eig
        idx = np.maximum.outer(np.arange(len(mid)), np.arange(len(mid)))
        Kmat = w[idx]
        sq = np.sqrt(h)
        A = Kmat * np.outer(sq, sq)
        # power iteration (matrix ~ n x n, direct eigh fine)
        vals, vecs = np.linalg.eigh(A)
        y = vecs[:, -1]
        if y.sum() < 0:
            y = -y
        y = np.maximum(y, 0)
        gm = y / sq
        # back to nodes (pw-linear interp of midpoint values)
        gn = np.interp(u, mid, gm)
        gn[0] = gm[0] + (gm[0] - gm[1]) * 0.5  # linear extrapolate to 0
        gn = np.maximum(gn, 0)
        if gn.max() <= 0:
            break
        g = gn / np.sqrt(pw_c2_G(u, gn)[0])
        val = certified_bound(u, g, k, T)
        if verbose:
            print(f"  iter {it}: certified B = {val:.6f}")
        if val > best_val:
            best_val, best_g = val, g.copy()
    return best_val, u, best_g


def best_bound(k, Tfrac_list=None, cap=None, n=240, verbose=False):
    """optimize over T; cap = max coordinate (x-units) or None."""
    L = np.log(k)
    if Tfrac_list is None:
        Tfrac_list = [0.5, 1, 2, 4, 8, 16, 32, 64]
    results = []
    for tf in Tfrac_list:
        T = tf * np.exp(L - 3.0)  # scale ~ e^{A}
        if cap is not None:
            T = min(T, cap)
        val, u, g = optimize_g(k, T, n=n)
        results.append((val, T, u, g))
        if verbose:
            print(f"k={k} T={T:.1f} (frac {tf}): certified {val:.5f}")
        if cap is not None and T >= cap * (1 - 1e-9):
            break
    return max(results, key=lambda r: r[0])


if __name__ == "__main__":
    import sys
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 35410
    val, T, u, g = best_bound(k, verbose=True)
    print(f"BEST k={k}: certified M_k >= {val:.6f}  (log k = {np.log(k):.4f}, deficit {np.log(k)-val:.4f})")
