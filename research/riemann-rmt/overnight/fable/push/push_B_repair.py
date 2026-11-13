"""push_B_repair.py -- verification of the REPAIR PASS on push_B_discriminant_force.md
(repairer, 6 Sep 2026).  Run: python push_B_repair.py [section numbers]   (all sections ~1-2 min)

RP1  Theorem 6.1, repaired 'A -> infinity' step: along a trajectory (pair +-0.15 in a 7-clock, N=8)
     V_a - V_b <= 2 cot(g/2)   (Theorem A's direction; the original text used the opposite),
     and A = Q - C_N >= 2 csc^2(g_min/2) - C_N -> infinity (Lemma 2.1), F -> -infinity.
RP2  E'' = A'/2 (the original text said A'/4): 4th-order differences along a DOP853 trajectory, N = 5, 7.
RP3  near-clock regime: mode-delta perturbation of the clock, D / [(1/C_N) log(1+C_N/A_0)] -> C_N/(2 delta (N-delta))
     (2(N^2-1)/(3N) for delta = N/2, N(N+1)/6 for delta = 1); D - log(1/A_0)/(2 delta(N-delta)) tends to a constant.
RP4  close-pair expansion  D - (1/k) log(1+k/A_0) = (delta^4/128)(k - G) + O(delta^6),  G = 2+3s-4b^2-2 sum v^2:
     depth from the SIGN of the phase-corrected discriminant R(s) = e^{-i(N-1) sum theta} Res(P_s, P_s') (Sylvester
     determinant, mpmath 40 digits, bisection; no root finding), cross-checked once against polyroots.
     N=3 with third point at pi (G=5): (D-bound(9/2))/delta^4 -> -1/256, and with k=G the delta^4 term vanishes.
     N=4 with the G-maximising background.  Also D = delta^2/8 + (1/3 + sigma/2) delta^4/64 + O(delta^6).
RP5  midpoint family: exact sympy factorisation P_s = (z-1)G(z); g_lam(x_k) = (-1)^k(1+lam) at 50 digits for N=3..12
     (all k, three lam); all roots of G on the circle, distinct, != 1 for lam < N/(N-2) at N = 50, 200, 1000.
RP6  G_max/N^2 at N = 12, 16, 24, 32 by multi-start Nelder-Mead on the closed-form close-pair ratio G.
"""
import sys, os, time
import numpy as np
import mpmath as mp
from math import pi, log
from scipy.optimize import minimize
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(1708)

def CN(N): return N * (N * N - 1) / 3.0

def forces(theta):
    th = np.asarray(theta, float); N = len(th)
    d = th[:, None] - th[None, :]
    off = ~np.eye(N, dtype=bool)
    cot = np.zeros((N, N)); csc2 = np.zeros((N, N))
    cot[off] = 1.0 / np.tan(d[off] / 2); csc2[off] = 1.0 / np.sin(d[off] / 2) ** 2
    V = cot.sum(1); Q = csc2.sum()
    Ap = 0.5 * np.sum(csc2 * (V[:, None] - V[None, :]) ** 2)
    return V, Q, Ap

def logdisc(theta):
    th = np.asarray(theta, float); N = len(th); d = th[:, None] - th[None, :]; iu = np.triu_indices(N, 1)
    return 2 * np.sum(np.log(np.abs(2 * np.sin(d[iu] / 2))))

# ---------------------------------------------------------------- discriminant-sign depth (Sylvester resultant)
def _coef(theta):
    """monic coefficients of prod (z - e^{i theta_j}), highest degree first, mpmath complex."""
    coef = [mp.mpc(1)]
    for t in theta:
        zj = mp.expj(mp.mpf(t)); new = [mp.mpc(0)] * (len(coef) + 1)
        for i, c in enumerate(coef): new[i] += c; new[i + 1] -= c * zj
        coef = new
    return coef

def _res(c):
    """Res(P, P') by the Sylvester determinant; c = coefficients highest first, c[0] = 1."""
    n = len(c) - 1
    dc = [c[i] * (n - i) for i in range(n)]
    S = mp.matrix(2 * n - 1, 2 * n - 1)
    for r in range(n - 1):
        for i, v in enumerate(c): S[r, r + i] = v
    for r in range(n):
        for i, v in enumerate(dc): S[n - 1 + r, r + i] = v
    return mp.det(S)

def R_phase_corrected(theta, s, dps=40):
    """R(s) = e^{-i(N-1) sum theta} Res(P_s, P_s') = prod_{j<k} 4 sin^2(theta_jk(s)/2) > 0 on [0, D); returns (Re, |Im|/|R|)."""
    mp.mp.dps = dps
    N = len(theta); c = _coef(theta)
    cs = [c[i] * mp.exp(mp.mpf(s) * (N - i) * i) for i in range(N + 1)]
    r = _res(cs) * mp.expj(-(N - 1) * mp.fsum(mp.mpf(t) for t in theta))
    return r.real, abs(r.imag) / abs(r)

def depth_discsign(theta, dps=40, tol=mp.mpf('1e-16'), s_hi=None):
    """first zero of R(s) located by sign bisection (valid when the first collision is a zero of odd order)."""
    mp.mp.dps = dps
    N = len(theta); r0, im0 = R_phase_corrected(theta, 0, dps)
    assert r0 > 0 and im0 < mp.mpf('1e-25'), (r0, im0)
    lo = mp.mpf(0); hi = mp.mpf(s_hi) if s_hi else mp.mpf(4) / N ** 2
    while R_phase_corrected(theta, hi, dps)[0] > 0: hi *= 2
    for _ in range(300):
        mid = (lo + hi) / 2
        if R_phase_corrected(theta, mid, dps)[0] > 0: lo = mid
        else: hi = mid
        if hi - lo < tol * hi: break
    return (lo + hi) / 2

def depth_polyroots(theta, dps=30, tol=1e-13):
    """independent: bisection on the off-circle indicator of mpmath polyroots (handles even-order collisions)."""
    mp.mp.dps = dps
    N = len(theta); c = _coef(theta); thr = mp.mpf(10) ** (-dps // 2)
    def off(s):
        cs = [c[i] * mp.exp(mp.mpf(s) * (N - i) * i) for i in range(N + 1)]
        return max(abs(abs(x) - 1) for x in mp.polyroots(cs, maxsteps=200, extraprec=80))
    lo = mp.mpf(0); hi = mp.mpf(4) / N ** 2
    while off(hi) < thr: hi *= 2
    for _ in range(200):
        mid = (lo + hi) / 2
        if off(mid) > thr: hi = mid
        else: lo = mid
        if hi - lo < tol * hi: break
    return (lo + hi) / 2

def flow(theta0, s_end, rtol=1e-13):
    def rhs(s, th):
        V, _, _ = forces(th); return -V
    return solve_ivp(rhs, [0, s_end], np.asarray(theta0, float), method='DOP853', rtol=rtol, atol=1e-14, dense_output=True)

# ---------------------------------------------------------------- RP1
def RP1():
    print("== RP1: Theorem 6.1 repaired step.  Pair at +-0.15 in a 7-clock background (N=8)")
    N = 8
    th = np.concatenate([[-0.15, 0.15], 2 * pi * np.arange(1, N - 1) / (N - 1)])
    D = float(depth_polyroots(th)); sol = flow(th, 0.9995 * D)
    print(f"   D = {D:.10f}   (Theorem A: g' >= -2cot(g/2), i.e. V_a - V_b <= 2cot(g/2))")
    print("   s/D      g         V_a-V_b   2cot(g/2)  diff(<=0)    A        2csc^2(g/2)-C_N   F(s)")
    for f in [0, 0.5, 0.9, 0.99, 0.999, 0.9995]:
        t_ = sol.sol(f * D); V, Q, Ap = forces(t_); A = np.sum(V ** 2); g = t_[1] - t_[0]
        lb = 2 / np.sin(g / 2) ** 2 - CN(N)
        assert V[1] - V[0] <= 2 / np.tan(g / 2) + 1e-9 and A >= lb - 1e-9
        print(f"   {f:6.4f}  {g:9.6f}  {V[1]-V[0]:9.4f}  {2/np.tan(g/2):9.4f}  {V[1]-V[0]-2/np.tan(g/2):+8.4f}  {A:10.4g}  {lb:12.4g}   {logdisc(t_):9.3f}")
    print("   => V_a - V_b < 2cot(g/2) throughout (the original 'bracket is non-negative' argued the wrong way);")
    print("      A >= 2csc^2(g_min/2) - C_N -> infinity as g_min -> 0, which is all the Riccati comparison needs.")

# ---------------------------------------------------------------- RP2
def RP2():
    print("== RP2: E'' = A'/2 (text had A'/4); E' = A/2")
    for N in [5, 7]:
        th = np.sort(rng.uniform(0, 2 * pi, N))
        while np.diff(np.concatenate([th, [th[0] + 2 * pi]])).min() < 0.3 * 2 * pi / N: th = np.sort(rng.uniform(0, 2 * pi, N))
        D = float(depth_polyroots(th)); sol = flow(th, 0.6 * D); h = 1e-4 * D; w1 = w2 = 0
        for f in [0.1, 0.3, 0.5]:
            s = f * D
            E = lambda t: -0.5 * logdisc(sol.sol(t))
            V, Q, Ap = forces(sol.sol(s)); A = np.sum(V ** 2)
            d2E = (-E(s + 2 * h) + 16 * E(s + h) - 30 * E(s) + 16 * E(s - h) - E(s - 2 * h)) / (12 * h * h)
            dE = (8 * (E(s + h) - E(s - h)) - (E(s + 2 * h) - E(s - 2 * h))) / (12 * h)
            w1 = max(w1, abs(d2E / (Ap / 2) - 1)); w2 = max(w2, abs(dE / (A / 2) - 1))
        print(f"   N={N}: max |E''/(A'/2) - 1| = {w1:.1e},  max |E'/(A/2) - 1| = {w2:.1e}   (E''/(A'/4) would be 2)")

# ---------------------------------------------------------------- RP3
def RP3():
    print("== RP3: near-clock regime, mode-delta perturbation eps*cos(2 pi delta j/N) of the N-clock")
    print("   prediction: D = log(1/A_0)/(2 delta (N-delta)) + O(1);  ratio D/bound -> C_N/(2 delta (N-delta))")
    for N, delta in [(4, 2), (4, 1), (5, 2), (5, 1), (6, 3), (6, 1)]:
        base = 2 * pi * np.arange(N) / N; mode = np.cos(2 * pi * delta * np.arange(N) / N)
        rate = delta * (N - delta); lim = CN(N) / (2 * rate)
        line = f"   N={N} delta={delta} (rate {rate}, limit {lim:.4f}):"
        for eps in [1e-2, 1e-3, 1e-4, 1e-5]:
            th = base + eps * mode; V, Q, Ap = forces(th); A0 = np.sum(V ** 2)
            D = float(depth_polyroots(th, dps=30)); b = np.log1p(CN(N) / A0) / CN(N)
            line += f"  eps={eps:.0e}: ratio {D/b:.4f}, D - log(1/A_0)/(2 rate) = {D - log(1/A0)/(2*rate):+.4f};"
        print(line)

# ---------------------------------------------------------------- RP4
def close_pair_G(x):
    x = np.asarray(x, float); n = len(x)
    sigma = np.sum(1 / np.sin(x / 2) ** 2); beta = np.sum(1 / np.tan(x / 2))
    d = x[:, None] - x[None, :]; off = ~np.eye(n, dtype=bool)
    W = np.zeros((n, n)); W[off] = 1 / np.tan(d[off] / 2)
    v = 2 / np.tan(x / 2) + W.sum(1)
    return 2 + 3 * sigma - 4 * beta ** 2 - 2 * np.sum(v ** 2), sigma

def RP4():
    print("== RP4: D - (1/k) log(1+k/A_0) = (delta^4/128)(k - G) + O(delta^6)   [depth from the discriminant sign]")
    # cross-check the two depth routines once
    th = np.array([-0.15, 0.15, pi]); d1 = depth_discsign(th); d2 = depth_polyroots(th)
    print(f"   cross-check N=3 delta=0.3: disc-sign D = {mp.nstr(d1, 15)}, polyroots D = {mp.nstr(d2, 15)}, rel diff {float(abs(d1/d2-1)):.1e}")
    print("   (a) N=3, points (-delta/2, delta/2, pi): G = 5, sigma = 1; k = 9/2 gives (k-G)/128 = -1/256 = -0.00390625")
    print("       delta   D                 (D-b(9/2))/d^4   (D-b(G))/d^4   (D-d^2/8)/d^4  pred (1/3+s/2)/64")
    for delta in [0.4, 0.2, 0.1, 0.05, 0.025]:
        th = np.array([-delta / 2, delta / 2, pi]); V, Q, Ap = forces(th); A0 = np.sum(V ** 2)
        G, sig = close_pair_G(th[2:]); D = depth_discsign(th)
        b1 = mp.log1p(mp.mpf(4.5) / A0) / mp.mpf(4.5); bG = mp.log1p(mp.mpf(G) / A0) / mp.mpf(G)
        d4 = mp.mpf(delta) ** 4
        print(f"       {delta:6.3f}  {mp.nstr(D, 14):16s}  {mp.nstr((D-b1)/d4, 7):>14s}  {mp.nstr((D-bG)/d4, 4):>12s}  {mp.nstr((D-delta**2/8)/d4, 7):>13s}  {(1/3+sig/2)/64:.7f}")
    # N = 4: G-maximising background
    best = (-np.inf, None)
    for t in range(40):
        x0 = np.sort(rng.uniform(0.4, 2 * pi - 0.4, 2))
        def f(x):
            xs = np.sort(x)
            if xs.min() < 0.05 or xs.max() > 2 * pi - 0.05 or np.diff(xs).min() < 0.05: return 1e9
            return -close_pair_G(xs)[0]
        res = minimize(f, x0, method='Nelder-Mead', options={'xatol': 1e-10, 'fatol': 1e-12, 'maxiter': 4000})
        if -res.fun > best[0]: best = (-res.fun, np.sort(res.x))
    G, x = best; sig = close_pair_G(x)[1]; k = 8.0
    print(f"   (b) N=4, background x = {np.round(x, 6)}: G_max = {G:.6f} > N^2/2 = 8;  predicted (k-G)/128 = {(k-G)/128:.6f}")
    for delta in [0.2, 0.1, 0.05]:
        th = np.concatenate([[-delta / 2, delta / 2], x]); V, Q, Ap = forces(th); A0 = np.sum(V ** 2)
        D = depth_discsign(th); b = mp.log1p(mp.mpf(k) / A0) / mp.mpf(k); bG = mp.log1p(mp.mpf(G) / A0) / mp.mpf(G); d4 = mp.mpf(delta) ** 4
        print(f"       delta={delta:5.3f}: D/bound(8) = {mp.nstr(D/b, 9)}, (D-bound(8))/delta^4 = {mp.nstr((D-b)/d4, 6)}, (D-bound(G))/delta^4 = {mp.nstr((D-bG)/d4, 3)},"
              f" (D-d^2/8)/d^4 = {mp.nstr((D-delta**2/8)/d4, 6)} (pred {(1/3+sig/2)/64:.6f})")
    print("   (c) which N have the PROVED lower bound (N^2+4N-6)/3 (doubled (N-1)-clock) above N^2/2?  (N-2)(N-6) < 0:",
          [N for N in range(3, 13) if (N * N + 4 * N - 6) / 3 > N * N / 2], " (N=6: equal)")

# ---------------------------------------------------------------- RP5
def RP5():
    import sympy as sp
    print("== RP5: midpoint family P_s = z^N - lam z^{N-1} + lam z - 1 = (z-1) G(z), sign alternation of g_lam")
    z, lam = sp.symbols('z lam')
    ok = True
    for N in range(3, 10):
        M = N - 1
        P = z ** N - lam * z ** (N - 1) + lam * z - 1
        G = z ** M + 1 + (1 - lam) * sum(z ** k for k in range(1, M))
        ok &= sp.expand(P - (z - 1) * G) == 0
    print(f"   sympy: P_s == (z-1)[z^M + 1 + (1-lam)(z + ... + z^(M-1))] for N = 3..9: {ok}")
    mp.mp.dps = 50; worst = mp.mpf(0)
    for N in range(3, 13):
        M = N - 1; lam_max = mp.mpf(N) / (N - 2)
        for f in [mp.mpf('0.1'), mp.mpf('0.5'), mp.mpf('0.999')]:
            lm = 1 + f * (lam_max - 1)
            for k in range(1, M):
                x = 2 * mp.pi * k / M
                g = (mp.expj(-M * x / 2) * (mp.expj(M * x) + 1 + (1 - lm) * mp.fsum(mp.expj(j * x) for j in range(1, M))))
                worst = max(worst, abs(g - (-1) ** k * (1 + lm)))
            g0 = (1 + 1 + (1 - lm) * (M - 1)); assert g0 > 0
    print(f"   |e^(-iMx_k/2) G(e^(ix_k)) - (-1)^k (1+lam)| <= {mp.nstr(worst, 3)} over N=3..12, all k, three lam;  g_lam(0) = 2-(lam-1)(M-1) > 0")
    for N in [50, 200, 1000]:
        M = N - 1; lam_max = N / (N - 2); worst_r = 0; worst_sep = np.inf; near1 = np.inf
        for f in [0.5, 0.9, 0.999]:
            lm = 1 + f * (lam_max - 1)
            coeffs = np.concatenate([[1.0], np.full(M - 1, 1 - lm), [1.0]])   # z^M + (1-lam)(z^{M-1}+...+z) + 1
            r = np.roots(coeffs); ang = np.sort(np.angle(r) % (2 * pi))
            worst_r = max(worst_r, np.max(np.abs(np.abs(r) - 1)))
            worst_sep = min(worst_sep, np.min(np.diff(np.concatenate([ang, [ang[0] + 2 * pi]]))))
            near1 = min(near1, np.min(np.abs(r - 1)))
        print(f"   N={N}: max ||root|-1| = {worst_r:.1e}, min angular separation = {worst_sep:.3e} (2pi/M = {2*pi/M:.3e}), min |root-1| = {near1:.3e}  (lam/lam_max = 0.5, 0.9, 0.999)")
    # depth formula vs a direct polyroots bisection at moderate N
    for N in [12, 25]:
        th = np.concatenate([[0.0], (2 * np.arange(N - 1) + 1) * pi / (N - 1)])
        D = float(depth_polyroots(th, dps=30)); Dex = log(N / (N - 2)) / (N - 1)
        print(f"   N={N}: D (polyroots bisection) = {D:.12f}, log(N/(N-2))/(N-1) = {Dex:.12f}, rel diff {abs(D/Dex-1):.1e}")

# ---------------------------------------------------------------- RP6
def RP6():
    print("== RP6: G_max / N^2 (close-pair limit of (A'-A^2)/A maximised over the background)")
    for N in [12, 16, 24, 32]:
        best = (-np.inf, None); t0 = time.time(); starts = 16 if N <= 16 else 8
        for t in range(starts):
            if t % 2 == 0: x0 = 2 * pi * np.arange(1, N - 1) / (N - 1) + rng.normal(0, 0.5 / N, N - 2)
            else: x0 = np.sort(rng.uniform(0.3, 2 * pi - 0.3, N - 2))
            def f(x):
                xs = np.sort(x)
                if xs.min() < 1e-3 or xs.max() > 2 * pi - 1e-3 or np.diff(xs).min() < 1e-3: return 1e9
                return -close_pair_G(xs)[0]
            res = minimize(f, x0, method='Nelder-Mead', options={'xatol': 1e-9, 'fatol': 1e-11, 'maxiter': 30000, 'maxfev': 60000})
            res = minimize(f, res.x, method='Nelder-Mead', options={'xatol': 1e-10, 'fatol': 1e-12, 'maxiter': 30000, 'maxfev': 60000})
            if -res.fun > best[0]: best = (-res.fun, np.sort(res.x))
        G, x = best
        print(f"   N={N:2d}: G_max = {G:9.4f} = {G/N**2:.4f} N^2   [(N^2+4N-6)/3 = {(N*N+4*N-6)/3:.2f}, N^2/2 = {N*N/2:.0f}, C_N = {CN(N):.0f}]  ({time.time()-t0:.0f}s)")

if __name__ == "__main__":
    which = [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4, 5, 6]
    t0 = time.time()
    for k in which:
        globals()[f"RP{k}"]()
        print(f"   [{time.time()-t0:.0f}s]")
