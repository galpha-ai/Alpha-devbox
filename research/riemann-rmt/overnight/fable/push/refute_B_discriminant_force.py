"""refute_B_discriminant_force.py -- independent adversarial checks of push_B_discriminant_force.md

Run: python refute_B_discriminant_force.py [section numbers]   (all sections by default, ~2-3 min)

R1  F' = -A and F'' = -A' via the EXPONENTIAL POLYNOMIAL of the discriminant (sympy monomials, mpmath 40 digits),
    i.e. without any finite differencing: disc(P_s) = sum_m c_m a^{e(m)} e^{s w_m} differentiated analytically.
R2  ODE route: integrate theta' = -V (DOP853, rtol 1e-13); check dA/ds = sum c_ij (V_i-V_j)^2 and
    d^2E/ds^2 = A'/2 (the text says A'/4 in Section 3 -- factor-2 slip; inconsistent with F = -2E, F'' = -A').
R3  Riccati bound D >= (1/C_N) log(1+C_N/A_0): ACUE re-run, random configurations at N=3..7, N=3 exhaustive grid.
    Off-lattice COUNTEREXAMPLE to the "empirical" inequality D >= (2/N^2) log(1 + N^2/(2A_0)):
    prediction  D - (1/k)log(1+k/A_0) = (delta^4/128)(k - G) + O(delta^6),  G = 2+3 sigma-4 beta^2-2 sum v_k^2,
    so any background with G > N^2/2 (e.g. N=3, third point opposite: G = 5 > 4.5) violates it for small delta.
R4  kappa_N: maximise the closed-form close-pair ratio G over backgrounds (multi-start, N up to 32) and compare
    with the proposer's 0.6 N^2; check kappa_N <= C_N on random/cluster configurations.
R5  Midpoint family: (i) closed-form |disc| vs Sylvester resultant (no root finding) at 50 digits;
    (ii) the first-collision claim is PROVABLE: P_s = (z-1) G(z), g_lam(x) = e^{-i(N-1)x/2} G(e^{ix}) is real with
         g_lam(2 pi k/(N-1)) = (-1)^k (1+lam) for 1<=k<=N-2 and g_lam(0) = 2-(lam-1)(N-2) > 0 iff lam < N/(N-2);
         M = N-1 sign changes => N-1 simple roots of G on the circle, none at z=1, for every lam < N/(N-2).
         Checked numerically for N up to 4000, plus direct root tracking (HeatDepth solver) at N = 101, 201.
R6  Local closed form Delta F(tau): Richardson at N = 512..4096 (proposer stopped at 256), including tau = 1.9, 1.99.
R7  Theorem 6.1's parenthetical "V_a - V_b ~ 4/g (Theorem A's bracket is non-negative)" has the inequality
    backwards: Theorem A gives V_a - V_b <= 2 cot(g/2).  Shown on a trajectory; A -> infinity holds anyway (F -> -inf).
R8  "Sharp in the near-clock regime": D / [(1/C_N) log(1+C_N/A_0)] -> 2(N^2-1)/(3N) (not 1) as A_0 -> 0.
R9  Exact A_0 for the pure hole ((N-1)(N-2)/3) and for the midpoint family (N^2-3N+2); ACUE [4]-family A_0/N^2.
"""
import sys, os, time, itertools
import numpy as np
import mpmath as mp
from math import pi, log, comb
from scipy.optimize import minimize, brentq
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
rng = np.random.default_rng(777)

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

def random_config(N, dmin=0.15):
    while True:
        th = np.sort(rng.uniform(0, 2 * pi, N))
        g = np.diff(np.concatenate([th, [th[0] + 2 * pi]]))
        if g.min() > dmin * 2 * pi / N: return th

def depth_bisect(theta, tol=1e-13):
    """first collision time: bisection on the off-circle indicator (np.roots)."""
    N = len(theta); z = np.exp(1j * theta); a = np.poly(z)
    powers = np.arange(N, -1, -1); w = powers * (N - powers)
    def off(s): return np.max(np.abs(np.abs(np.roots(a * np.exp(s * w))) - 1.0))
    lo = 0.0; hi = 4.0 / N ** 2
    while off(hi) < 1e-7: hi *= 2
    for _ in range(70):
        mid = 0.5 * (lo + hi)
        if off(mid) > 1e-7: hi = mid
        else: lo = mid
        if hi - lo < tol * max(1, hi): break
    return 0.5 * (lo + hi)

def depth_mp(theta, dps=30, tol=1e-12):
    """same, but roots in mpmath (for tiny gaps / N=3 counterexample where np.roots is not enough)."""
    mp.mp.dps = dps
    N = len(theta)
    z = [mp.expj(mp.mpf(t)) for t in theta]
    coef = [mp.mpc(1)]
    for zj in z:
        new = [mp.mpc(0)] * (len(coef) + 1)
        for i, c in enumerate(coef):
            new[i] += c; new[i + 1] -= c * zj
        coef = new
    def off(s):
        cs = [coef[i] * mp.exp(mp.mpf(s) * (N - i) * i) for i in range(N + 1)]
        r = mp.polyroots(cs, maxsteps=100, extraprec=60)
        return max(abs(abs(x) - 1) for x in r)
    lo = mp.mpf(0); hi = mp.mpf(4) / N ** 2
    while off(hi) < mp.mpf(10) ** (-dps // 2): hi *= 2
    for _ in range(200):
        mid = (lo + hi) / 2
        if off(mid) > mp.mpf(10) ** (-dps // 2): hi = mid
        else: lo = mid
        if hi - lo < tol * hi: break
    return float((lo + hi) / 2)

# ---------------------------------------------------------------- R1
def R1():
    import sympy as sp
    print("== R1: F' = -A, F'' = -A' through the exponential polynomial (no finite differences)")
    z = sp.symbols('z')
    for N in [3, 4, 5]:
        a = sp.symbols(f'a0:{N}')
        P = z ** N + sum(a[j] * z ** j for j in range(N))
        disc = sp.Poly(sp.expand(sp.discriminant(P, z)), *a)
        terms = disc.terms()   # (exponent tuple, coefficient)
        wm = [sum(e[j] * j * (N - j) for j in range(N)) for e, c in terms]
        print(f"  N={N}: {len(terms)} monomials, max w_m = {max(wm)} (bound N^2(N-1)/2 = {N*N*(N-1)//2})")
        mp.mp.dps = 40
        worst = [0, 0, 0]
        for trial in range(3):
            th = random_config(N)
            zz = [mp.expj(mp.mpf(t)) for t in th]
            coef = [mp.mpc(1)]
            for zj in zz:
                new = [mp.mpc(0)] * (len(coef) + 1)
                for i, c in enumerate(coef): new[i] += c; new[i + 1] -= c * zj
                coef = new
            aval = [coef[N - j] for j in range(N)]           # a_j = coefficient of z^j (a_N = 1)
            D0 = depth_bisect(th)
            for frac in [0.0, 0.3, 0.7]:
                s = mp.mpf(frac * D0)
                d0 = d1 = d2 = mp.mpc(0)
                for (e, c), w in zip(terms, wm):
                    mon = mp.mpc(int(c))
                    for j in range(N):
                        if e[j]: mon *= aval[j] ** e[j]
                    t = mon * mp.exp(s * w)
                    d0 += t; d1 += w * t; d2 += w * w * t
                r1 = d1 / d0; r2 = d2 / d0 - r1 * r1
                # roots of P_s at s for A, A'
                cs = [coef[i] * mp.exp(s * (N - i) * i) for i in range(N + 1)]
                roots = mp.polyroots(cs, maxsteps=200, extraprec=80)
                ths = np.array([float(mp.arg(r)) for r in roots])
                V, Q, Ap = forces(ths); A = np.sum(V ** 2)
                e1 = abs(float(mp.re(r1)) + A) / A
                e2 = abs(float(mp.re(r2)) + Ap) / Ap
                e3 = abs(float(mp.im(r1)))
                worst = [max(worst[0], e1), max(worst[1], e2), max(worst[2], e3)]
        print(f"     worst |Re(disc'/disc) + A|/A = {worst[0]:.1e}, |Re(disc''/disc - (disc'/disc)^2) + A'|/A' = {worst[1]:.1e},"
              f" |Im disc'/disc| = {worst[2]:.1e}   (s = 0, 0.3D, 0.7D)")

# ---------------------------------------------------------------- R2
def flow(theta0, s_end, n_out, rtol=1e-13):
    def rhs(s, th):
        V, _, _ = forces(th); return -V
    sol = solve_ivp(rhs, [0, s_end], np.asarray(theta0, float), method='DOP853', rtol=rtol, atol=1e-14, dense_output=True)
    ss = np.linspace(0, s_end, n_out)
    return ss, sol

def R2():
    print("== R2: ODE route: dA/ds = sum_{i<j} c_ij (V_i-V_j)^2 ; d^2E/ds^2 = A'/2 (text: A'/4)")
    for N in [4, 6, 9]:
        th = random_config(N); D = depth_bisect(th)
        ss, sol = flow(th, 0.5 * D, 5)
        h = 1e-4 * D
        w1 = w2 = w3 = 0
        for s in ss[1:]:
            def A_of(t):
                V, Q, Ap = forces(sol.sol(t)); return np.sum(V ** 2), Ap, Q
            def E_of(t):
                t_ = sol.sol(t); d = t_[:, None] - t_[None, :]; iu = np.triu_indices(N, 1)
                return -np.sum(np.log(np.abs(2 * np.sin(d[iu] / 2))))
            A0, Ap0, Q0 = A_of(s)
            dA = (8 * (A_of(s + h)[0] - A_of(s - h)[0]) - (A_of(s + 2 * h)[0] - A_of(s - 2 * h)[0])) / (12 * h)
            d2E = (-E_of(s + 2 * h) + 16 * E_of(s + h) - 30 * E_of(s) + 16 * E_of(s - h) - E_of(s - 2 * h)) / (12 * h * h)
            dE = (8 * (E_of(s + h) - E_of(s - h)) - (E_of(s + 2 * h) - E_of(s - 2 * h))) / (12 * h)
            w1 = max(w1, abs(dA - Ap0) / Ap0); w2 = max(w2, abs(d2E - Ap0 / 2) / (Ap0 / 2)); w3 = max(w3, abs(dE - A0 / 2) / (A0 / 2))
        print(f"  N={N}: |dA/ds - A'|/A' <= {w1:.1e};  |E'' - A'/2|/(A'/2) <= {w2:.1e};  |E' - A/2|/(A/2) <= {w3:.1e}"
              f"   (so E'' = A'/2, and 'A'/4' in Section 3 is off by 2)")

# ---------------------------------------------------------------- R3
def close_pair_G(x):
    """G = 2 + 3 sigma - 4 beta^2 - 2 sum v_k^2 for a background x (pair fused at 0)."""
    x = np.asarray(x, float); n = len(x)
    sigma = np.sum(1 / np.sin(x / 2) ** 2); beta = np.sum(1 / np.tan(x / 2))
    d = x[:, None] - x[None, :]; off = ~np.eye(n, dtype=bool)
    W = np.zeros((n, n)); W[off] = 1 / np.tan(d[off] / 2)
    v = 2 / np.tan(x / 2) + W.sum(1)
    return 2 + 3 * sigma - 4 * beta ** 2 - 2 * np.sum(v ** 2)

def R3():
    print("== R3: Riccati bound and the (N^2/2) inequality")
    # (a) ACUE re-run (independent code path from the npz fields)
    for N in range(4, 13):
        f = os.path.join(HERE, f"acue_depth_N{N}.npz")
        if not os.path.exists(f): continue
        d = np.load(f); D = d['D']; Q0 = d['Q0']; fin = np.isfinite(D); C = CN(N)
        A0 = Q0[fin] - C
        r1 = D[fin] / (np.log1p(C / A0) / C); r2 = D[fin] / ((2 / N ** 2) * np.log1p(N ** 2 / (2 * A0)))
        i1 = np.argmin(r1); i2 = np.argmin(r2)
        g = d['gaps'][fin]
        print(f"  ACUE N={N:2d}: min D/Riccati(C_N) = {r1.min():.4f} at gaps {g[i1].tolist()};"
              f"  min D/Riccati(N^2/2) = {r2.min():.4f} at gaps {g[i2].tolist()}")
    # (b) random configurations, N = 3..7: Theorem 6.1 must hold (ratio >= 1); N^2/2 version need not
    print("  random configurations (depth by bisection):")
    for N in [3, 4, 5, 6, 7]:
        r1 = []; r2 = []
        for t in range(60):
            th = random_config(N, dmin=0.05 if t % 2 else 0.4)
            V, Q, Ap = forces(th); A0 = np.sum(V ** 2); D = depth_bisect(th)
            r1.append(D / (np.log1p(CN(N) / A0) / CN(N))); r2.append(D / ((2 / N ** 2) * np.log1p(N ** 2 / (2 * A0))))
        print(f"    N={N}: min D/Riccati(C_N) = {min(r1):.4f};  min D/Riccati(N^2/2) = {min(r2):.5f}")
    # (c) N=3 exhaustive grid over the two free gaps (third gap = 2pi - g1 - g2)
    print("  N=3 grid over gaps (g1,g2) in (0.05,2pi-0.1)^2 with g3>0.05:")
    best1 = (np.inf, None); best2 = (np.inf, None)
    for g1 in np.linspace(0.05, 2 * pi - 0.1, 41):
        for g2 in np.linspace(0.05, 2 * pi - 0.1, 41):
            g3 = 2 * pi - g1 - g2
            if g3 < 0.05: continue
            th = np.array([0, g1, g1 + g2]); V, Q, Ap = forces(th); A0 = np.sum(V ** 2); D = depth_bisect(th)
            v1 = D / (np.log1p(8 / A0) / 8); v2 = D / ((2 / 9) * np.log1p(9 / (2 * A0)))
            if v1 < best1[0]: best1 = (v1, (g1, g2, g3))
            if v2 < best2[0]: best2 = (v2, (g1, g2, g3))
    print(f"    min D/Riccati(C_3=8) = {best1[0]:.5f} at gaps {np.round(best1[1],3)};  min D/Riccati(9/2) = {best2[0]:.5f} at gaps {np.round(best2[1],3)}")
    # (d) the explicit counterexample: pair at +-delta/2 and a third point at pi (G = 5 > 9/2)
    print("  N=3 counterexample to D >= (2/N^2) log(1+N^2/(2A_0)): points at +-delta/2 and pi (close-pair G = 5 > N^2/2 = 4.5)")
    print("     predicted D - bound = (delta^4/128)(9/2 - 5) = -delta^4/256")
    for delta in [0.8, 0.5, 0.3, 0.2, 0.1]:
        th = np.array([-delta / 2, delta / 2, pi]); V, Q, Ap = forces(th); A0 = np.sum(V ** 2)
        D = depth_mp(th, dps=30)
        b = (2 / 9) * np.log1p(9 / (2 * A0))
        print(f"     delta={delta:4.2f}: D = {D:.12f}, bound = {b:.12f}, D/bound = {D/b:.8f}, (D-bound)/delta^4 = {(D-b)/delta**4:.6f} (pred -1/256 = {-1/256:.6f})")
    # (e) N=4,5: optimised background (G > N^2/2) with delta = 0.15
    for N in [4, 5, 6]:
        best = (-np.inf, None)
        for t in range(40):
            x0 = np.sort(rng.uniform(0.4, 2 * pi - 0.4, N - 2))
            def f(x):
                xs = np.sort(x)
                if xs.min() < 0.05 or xs.max() > 2 * pi - 0.05 or (len(xs) > 1 and np.diff(xs).min() < 0.05): return 1e9
                return -close_pair_G(xs)
            res = minimize(f, x0, method='Nelder-Mead', options={'xatol': 1e-9, 'fatol': 1e-11, 'maxiter': 4000})
            if -res.fun > best[0]: best = (-res.fun, np.sort(res.x))
        G, x = best
        for delta in [0.2, 0.1]:
            th = np.concatenate([[-delta / 2, delta / 2], x]); V, Q, Ap = forces(th); A0 = np.sum(V ** 2)
            D = depth_mp(th, dps=30); k = N * N / 2
            b = np.log1p(k / A0) / k
            print(f"  N={N}: background G_max = {G:.4f} (N^2/2 = {k}), delta={delta}: D/bound(N^2/2) = {D/b:.7f},"
                  f" (D-bound)/delta^4 = {(D-b)/delta**4:.5f}, predicted (k-G)/128 = {(k-G)/128:.5f}")

# ---------------------------------------------------------------- R4
def R4():
    print("== R4: kappa_N -- closed-form close-pair ratio G maximised over backgrounds; global random search")
    def ratio(th):
        V, Q, Ap = forces(th); A = np.sum(V ** 2); return (Ap - A * A) / A
    for N in [3, 4, 5, 6, 8, 12, 16, 24, 32]:
        best = (-np.inf, None); t0 = time.time()
        starts = 60 if N <= 8 else (30 if N <= 16 else 12)
        for t in range(starts):
            if t % 2 == 0: x0 = np.sort(rng.uniform(0.3, 2 * pi - 0.3, N - 2))
            else: x0 = 2 * pi * np.arange(1, N - 1) / (N - 1) + rng.normal(0, 0.5 / N, N - 2)
            def f(x):
                xs = np.sort(x)
                if xs.min() < 1e-3 or xs.max() > 2 * pi - 1e-3 or (len(xs) > 1 and np.diff(xs).min() < 1e-3): return 1e9
                return -close_pair_G(xs)
            res = minimize(f, x0, method='Nelder-Mead', options={'xatol': 1e-9, 'fatol': 1e-11, 'maxiter': 20000, 'maxfev': 40000})
            if -res.fun > best[0]: best = (-res.fun, np.sort(res.x))
        G, x = best
        # global random search over general configurations (not only close pairs): clusters of 2,3,4 points
        worst = -np.inf
        for t in range(3000):
            th = np.sort(rng.uniform(0, 2 * pi, N)); k = min(N, 2 + t % 3)
            eps = 10 ** rng.uniform(-3, -0.5)
            th[:k] = th[0] + np.sort(rng.uniform(0, eps, k))
            worst = max(worst, ratio(np.sort(th)))
        # nearest neighbours of the maximiser relative to the clock spacing 2pi/(N-1)
        nn = np.sort(np.minimum(x, 2 * pi - x))[:2] * (N - 1) / (2 * pi)
        print(f"  N={N:2d}: max G = {G:9.4f} = {G/N**2:.4f} N^2  [(N^2+4N-6)/3 = {(N*N+4*N-6)/3:.3f}, C_N = {CN(N):.0f}];"
              f" random clusters max (A'-A^2)/A = {worst:8.3f}; maximiser's two nearest background pts at {np.round(nn,3)} clock spacings ({time.time()-t0:.0f}s)")

# ---------------------------------------------------------------- R5
def sylvester_disc(coeffs, dps=50):
    """|disc| of a monic polynomial via the Sylvester resultant determinant (mpmath), no root finding."""
    mp.mp.dps = dps
    c = [mp.mpf(x) for x in coeffs]            # highest degree first, c[0] = 1
    n = len(c) - 1
    dc = [c[i] * (n - i) for i in range(n)]    # derivative, highest first
    S = mp.matrix(2 * n - 1, 2 * n - 1)
    for r in range(n - 1):
        for i, v in enumerate(c): S[r, r + i] = v
    for r in range(n):
        for i, v in enumerate(dc): S[n - 1 + r, r + i] = v
    return abs(mp.det(S))

def midpoint_exact(N, lam):
    mp.mp.dps = 50
    lam = mp.mpf(lam)
    cphi = (N + lam ** 2 * (N - 2)) / (2 * lam * (N - 1))
    phi = mp.acos(cphi)
    return 4 * (lam * (N - 1)) ** N * (mp.sin(N * phi / 2) - lam * mp.sin((N - 2) * phi / 2)) ** 2 / (lam ** 2 - 1)

def R5():
    print("== R5: midpoint family P_s = z^N - lam z^{N-1} + lam z - 1")
    # (i) closed form vs Sylvester resultant
    for N in [3, 4, 5, 7, 9, 12]:
        lam_max = N / (N - 2); worst = 0
        for f in [0.2, 0.6, 0.95]:
            lam = 1 + f * (lam_max - 1)
            coeffs = [1, -lam] + [0] * (N - 3) + [lam, -1]
            ds = sylvester_disc(coeffs); dx = midpoint_exact(N, lam)
            worst = max(worst, float(abs(ds - dx) / dx))
        print(f"  N={N:2d}: max rel. diff |disc| closed form vs Sylvester determinant = {worst:.1e}")
    # (ii) the sign-alternation proof of the first-collision claim
    print("  first-collision claim: g_lam(x) = 2 cos((N-1)x/2) + (1-lam) sin((N-2)x/2)/sin(x/2) at x_k = 2 pi k/(N-1)")
    worst = 0
    for N in [3, 4, 5, 8, 13, 50, 200, 1000, 4000]:
        M = N - 1; lam = 1 + 0.999 * (N / (N - 2) - 1)
        xk = 2 * pi * np.arange(1, M) / M
        g = 2 * np.cos(M * xk / 2) + (1 - lam) * np.sin((M - 1) * xk / 2) / np.sin(xk / 2)
        pred = (-1.0) ** np.arange(1, M) * (1 + lam)
        worst = max(worst, np.max(np.abs(g - pred)) / (1 + lam))
        g0 = 2 + (1 - lam) * (M - 1)
    print(f"     max |g_lam(x_k) - (-1)^k (1+lam)|/(1+lam) over N in {{3..4000}} = {worst:.1e};  g_lam(0) = 2-(lam-1)(N-2) > 0 iff lam < N/(N-2)")
    print("     => for every lam < N/(N-2) the real function g_lam alternates in sign at the N points x_0..x_{N-1} of [0,2pi],")
    print("        so G has N-1 distinct roots on the circle, none equal to 1: no collision before the triple one. [P]")
    # (iii) HeatDepth root tracking at N=101, 201
    try:
        from heat_depth import HeatDepth
        for N in [101, 201]:
            th = np.concatenate([[0.0], (2 * np.arange(N - 1) + 1) * pi / (N - 1)])
            H = HeatDepth(th); d, i = H.depth(pairs=[0, N - 1, 1, N - 2, N // 2])
            Dex = log(N / (N - 2)) / (N - 1)
            print(f"     HeatDepth N={N}: D = {d:.12e} (pair {i}), exact {Dex:.12e}, rel.diff {abs(d/Dex-1):.1e}, (N-1)^2 D = {(N-1)**2*d:.8f}")
    except Exception as e:
        print("     HeatDepth unavailable:", e)

# ---------------------------------------------------------------- R6
def DeltaF_local(tau):
    w = np.sqrt(tau * (2 - tau))
    return tau - np.log(2 * tau) + 2 * np.log(np.abs(w * np.cos(w / 2) - tau * np.sin(w / 2)))

def logdisc_mid(N, s):
    mp.mp.dps = 40
    lam = mp.exp(mp.mpf(s) * (N - 1))
    cphi = (N + lam ** 2 * (N - 2)) / (2 * lam * (N - 1)); phi = mp.acos(cphi)
    return float(mp.log(4) + N * (mp.log(lam) + mp.log(N - 1)) + 2 * mp.log(abs(mp.sin(N * phi / 2) - lam * mp.sin((N - 2) * phi / 2))) - mp.log(lam ** 2 - 1))

def R6():
    print("== R6: local closed form Delta F(tau) -- Richardson at N = 512..4096")
    taus = [0.25, 1.0, 1.5, 1.9, 1.99]
    prev = None
    for N in [512, 1024, 2048, 4096]:
        F0 = log(4) + (N - 1) * log(N - 1)
        vals = np.array([logdisc_mid(N, t / N ** 2) - F0 for t in taus])
        line = f"  N={N:4d}: Delta F = {np.array2string(vals, precision=6)}"
        if prev is not None:
            rich = 2 * vals - prev
            line += f"   Richardson(2F_N - F_{N//2}) - closed form = {np.array2string(rich - DeltaF_local(np.array(taus)), precision=2)}"
        print(line); prev = vals
    print(f"  closed form            = {np.array2string(DeltaF_local(np.array(taus)), precision=6)}")
    print(f"  N*(closed form - F_N) at N=4096 (should converge to a finite 1/N-coefficient): {np.array2string(4096*(DeltaF_local(np.array(taus)) - vals), precision=3)}")

# ---------------------------------------------------------------- R7
def R7():
    print("== R7: Theorem 6.1's parenthetical: is V_a - V_b >= 2 cot(g/2)?  (Theorem A says <=)")
    N = 8
    th = np.concatenate([[-0.15, 0.15], 2 * pi * np.arange(1, N - 1) / (N - 1)])   # pair in a clock background
    D = depth_bisect(th); ss, sol = flow(th, 0.999 * D, 6)
    for s in ss:
        t_ = sol.sol(s); V, Q, Ap = forces(t_); A = np.sum(V ** 2)
        g = t_[1] - t_[0]
        print(f"   s/D={s/D:.3f}: g={g:.5f}, V_a-V_b = {V[1]-V[0]:.4f}, 2cot(g/2) = {2/np.tan(g/2):.4f}, difference = {V[1]-V[0]-2/np.tan(g/2):+.4f} (<0), A = {A:.4g}")
    print("   So V_a - V_b < 2cot(g/2) (Theorem A's bracket REDUCES V_a - V_b); A -> infinity anyway because F -> -inf and A is monotone.")

# ---------------------------------------------------------------- R8
def R8():
    print("== R8: near-clock 'sharpness': D / [(1/C_N) log(1 + C_N/A_0)] as A_0 -> 0 (prediction 2(N^2-1)/(3N) for the fastest mode)")
    for N in [4, 6]:
        base = 2 * pi * np.arange(N) / N
        mode = np.cos(pi * np.arange(N)) if N % 2 == 0 else np.cos(2 * pi * (N // 2) * np.arange(N) / N)   # delta = N/2 mode
        for eps in [1e-2, 1e-3, 1e-4]:
            th = base + eps * mode; V, Q, Ap = forces(th); A0 = np.sum(V ** 2)
            D = depth_bisect(th); b = np.log1p(CN(N) / A0) / CN(N)
            print(f"   N={N}: eps={eps:.0e}: A_0={A0:.3e}, D={D:.6f}, bound={b:.6f}, ratio={D/b:.4f}  (pred -> {2*(N*N-1)/(3*N):.4f})")

# ---------------------------------------------------------------- R9
def R9():
    print("== R9: exact initial force energies")
    for N in [7, 9, 63, 127]:
        thh = np.array([(2 * j + 1) * pi / N for j in range(N) if abs(((2 * j + 1) * pi / N) - pi) > 1e-9])
        V, Q, Ap = forces(thh); A = np.sum(V ** 2)
        print(f"   pure hole N={N}: A_0 = {A:.6f}, (N-1)(N-2)/3 = {(N-1)*(N-2)/3:.6f}")
    for N in [8, 16, 96]:
        th = np.concatenate([[0.0], (2 * np.arange(N - 1) + 1) * pi / (N - 1)]); V, Q, Ap = forces(th); A = np.sum(V ** 2)
        print(f"   midpoint family N={N}: A_0 = {A:.6f}, N^2-3N+2 = {N*N-3*N+2}")
    for N in [7, 9, 63, 127]:
        k = (N - 3) // 2; g = [1, 1] + [2] * k + [4] + [2] * (N - 3 - k)
        sites = np.concatenate([[0], np.cumsum(g)[:-1]]); th = 2 * pi * sites / (2 * N)
        V, Q, Ap = forces(th); A = np.sum(V ** 2)
        print(f"   ACUE [1,1,2..2,4,2..2] N={N}: A_0/N^2 = {A/N**2:.6f}  (block N^2-3N+2 + hole (N-1)(N-2)/3, /N^2 = {(N*N-3*N+2+(N-1)*(N-2)/3)/N**2:.6f})")

if __name__ == "__main__":
    which = [int(x) for x in sys.argv[1:]] or list(range(1, 10))
    t0 = time.time()
    for k in which:
        globals()[f"R{k}"]()
        print(f"   [{time.time()-t0:.0f}s]")
