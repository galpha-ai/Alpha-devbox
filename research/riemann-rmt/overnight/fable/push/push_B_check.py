"""push_B_check.py -- verification script for push_B_discriminant_force.md

Sections (run all: python push_B_check.py ; or python push_B_check.py 1 3 5 for a subset):
 1  identity  sum_j V_j^2 = Q - C_N  and  d/ds log|disc P_s| = -sum V_j^2  (mpmath, 40 digits,
    random configurations, Richardson central differences; target 1e-10)
 2  concavity: d^2/ds^2 log|disc| = -sum_{i<j} csc^2((th_i-th_j)/2)(V_i-V_j)^2  (same machinery)
 3  expectations: E_ACUE[Q - C_N] = C_N/2 from the complete orbit enumerations N=4..12;
    E_CUE[Q] = 2 C_N by quadrature of the exact CUE pair correlation
 4  exponential-polynomial structure of disc(P_s): sympy at N=3,4, plus the coefficient-space form
    of the force identity  sum_j j(N-j) a_j d(log disc)/d a_j = C_N - Q
 5  the Riccati lower bound D >= (1/C_N) log(1 + C_N/A_0) on all ACUE orbits, and the test of the
    sharper conjectural inequality A' <= A^2 + (N^2/2) A
 6  the 3-block local limit: exact discriminant of the midpoint family z^N - lam z^{N-1} + lam z - 1,
    its depth log(N/(N-2))/(N-1), the local closed form
    Delta F(tau) = tau - log(2 tau) + 2 log|w cos(w/2) - tau sin(w/2)|, w = sqrt(tau(2-tau)),
    against N-body integration of Lemma 1; additivity block + hole for the ACUE family [1,1,2..2,4,2..2]
"""
import sys, os, itertools, time
import numpy as np
import mpmath as mp
from math import comb, pi, log

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20260906)

# ---------------------------------------------------------------- basic quantities
def forces(theta):
    """V_j = sum_{k!=j} cot((theta_j-theta_k)/2), Q = sum_{i!=j} csc^2, A' = sum_{i<j} csc^2 (V_i-V_j)^2"""
    th = np.asarray(theta, float); N = len(th)
    d = th[:, None] - th[None, :]
    off = ~np.eye(N, dtype=bool)
    cot = np.zeros((N, N)); csc2 = np.zeros((N, N))
    cot[off] = 1.0 / np.tan(d[off] / 2); csc2[off] = 1.0 / np.sin(d[off] / 2) ** 2
    V = cot.sum(1)
    Q = csc2.sum()
    Aprime = 0.5 * np.sum(csc2 * (V[:, None] - V[None, :]) ** 2)
    return V, Q, Aprime

def CN(N): return N * (N * N - 1) / 3.0

def logdisc_mp(theta, s, dps=40):
    """log|disc P_s| from the roots of P_s, computed in mpmath at dps digits."""
    mp.mp.dps = dps
    N = len(theta)
    z = [mp.expj(mp.mpf(t)) for t in theta]
    # monic coefficients a_N=1,...,a_0 (highest first) via polynomial multiplication
    coef = [mp.mpc(1)]
    for zj in z:
        new = [mp.mpc(0)] * (len(coef) + 1)
        for i, c in enumerate(coef):
            new[i] += c; new[i + 1] -= c * zj
        coef = new
    # flow: coefficient of z^j (index N-j in 'coef') times exp(s j (N-j))
    coef_s = [coef[i] * mp.exp(mp.mpf(s) * (N - i) * i) for i in range(N + 1)]
    roots = mp.polyroots(coef_s, maxsteps=200, extraprec=dps * 2)
    F = mp.mpf(0)
    for j in range(N):
        for k in range(j + 1, N):
            F += 2 * mp.log(abs(roots[j] - roots[k]))
    return F

def random_config(N, dmin=0.15):
    while True:
        th = np.sort(rng.uniform(0, 2 * pi, N))
        g = np.diff(np.concatenate([th, [th[0] + 2 * pi]]))
        if g.min() > dmin / N * 2 * pi: return th

# ---------------------------------------------------------------- section 1,2
def section12():
    print("== Section 1/2: force identity, discriminant derivative, concavity (mpmath 40 digits)")
    worst1 = worst2 = worst3 = 0.0
    for N in [3, 4, 5, 7, 10, 14]:
        for trial in range(3):
            th = random_config(N)
            V, Q, Ap = forces(th)
            A = np.sum(V ** 2)
            e1 = abs(A - (Q - CN(N))) / max(1, A)
            worst1 = max(worst1, e1)
            # derivative of log|disc| at s = s0 > 0 small (roots must be on the circle: s0 << D)
            # first move the configuration along the flow to s0 by using P_{s0} roots directly
            s0 = 0.02 / N ** 2
            mp.mp.dps = 40
            h = mp.mpf(1e-5) / N ** 2
            Fp = logdisc_mp(th, s0 + h); Fm = logdisc_mp(th, s0 - h); F0 = logdisc_mp(th, s0)
            Fp2 = logdisc_mp(th, s0 + 2 * h); Fm2 = logdisc_mp(th, s0 - 2 * h)
            d1 = (8 * (Fp - Fm) - (Fp2 - Fm2)) / (12 * h)          # 4th-order central difference
            d2 = (-Fp2 + 16 * Fp - 30 * F0 + 16 * Fm - Fm2) / (12 * h * h)
            # roots at s0 for the right-hand sides
            N_ = N
            zs = mp.polyroots([c for c in _coef_s(th, s0)], maxsteps=200, extraprec=80)
            th_s = np.array([float(mp.arg(r)) for r in zs])
            rad = max(abs(float(abs(r)) - 1) for r in zs)
            Vs, Qs, Aps = forces(th_s)
            As = np.sum(Vs ** 2)
            e2 = abs(float(d1) + As) / As
            e3 = abs(float(d2) + Aps) / Aps
            worst2 = max(worst2, e2); worst3 = max(worst3, e3)
            print(f"  N={N:2d} trial {trial}: |A-(Q-C_N)|/A={e1:.1e}  |F'+A|/A={e2:.1e}  |F''+A'|/A'={e3:.1e}"
                  f"  (max| |z|-1 |={rad:.1e}, A={As:.4g}, A'={Aps:.4g})")
    print(f"  worst relative errors: identity {worst1:.1e}, first derivative {worst2:.1e}, second derivative {worst3:.1e}")
    return worst1, worst2, worst3

def _coef_s(theta, s):
    mp.mp.dps = 40
    N = len(theta)
    z = [mp.expj(mp.mpf(t)) for t in theta]
    coef = [mp.mpc(1)]
    for zj in z:
        new = [mp.mpc(0)] * (len(coef) + 1)
        for i, c in enumerate(coef):
            new[i] += c; new[i + 1] -= c * zj
        coef = new
    return [coef[i] * mp.exp(mp.mpf(s) * (N - i) * i) for i in range(N + 1)]

# ---------------------------------------------------------------- section 3
def section3():
    print("== Section 3: expectation identities")
    for N in range(4, 13):
        f = os.path.join(HERE, f"acue_depth_N{N}.npz")
        if not os.path.exists(f): continue
        d = np.load(f); w = d['mass'] * d['orbit_size']; Q0 = d['Q0']; C = CN(N)
        EA = np.sum(w * (Q0 - C)) / np.sum(w)
        print(f"  ACUE N={N:2d}: sum w = {np.sum(w):.15f}, E[Q]/C_N = {np.sum(w*Q0)/np.sum(w)/C:.15f}, "
              f"E[sum V^2]/(C_N/2) = {EA/(C/2):.15f}  (orbits {len(w)})")
    # CUE: (1/2pi) int (N^2 - S_N^2) csc^2(theta/2) dtheta = 2 C_N.  The integrand is a trigonometric
    # polynomial of degree N-1, so the midpoint (offset trapezoid) rule with M = 4N nodes is exact.
    mp.mp.dps = 30
    for N in [2, 3, 5, 8, 13, 21]:
        M = 4 * N; tot = mp.mpf(0)
        for k in range(M):
            t = (k + mp.mpf(1) / 2) * 2 * mp.pi / M
            S = mp.sin(N * t / 2) / mp.sin(t / 2)
            tot += (N * N - S * S) / mp.sin(t / 2) ** 2
        I = tot / M
        print(f"  CUE  N={N:2d}: E_CUE Q / (2 C_N) = {mp.nstr(I/(2*CN(N)), 20)}   (exact quadrature of the pair correlation)")
    # lattice sums used in the ACUE computation
    for M in [5, 8, 13, 24]:
        s2 = sum(1 / np.sin(pi * d / M) ** 2 for d in range(1, M)); s4 = sum(1 / np.sin(pi * d / M) ** 4 for d in range(1, M))
        print(f"  lattice sums M={M:2d}: sum csc^2 = {s2:.10f} vs (M^2-1)/3 = {(M*M-1)/3:.10f};"
              f"  sum csc^4 = {s4:.10f} vs (M^2-1)(M^2+11)/45 = {(M*M-1)*(M*M+11)/45:.10f}")
    # ACUE closed form E Q = (1/2N)[N^2 (4N^2-1)/3 - N^2(N^2+2)/3] = N(N^2-1)/2 = 3 C_N/2, checked as a lattice sum
    for N in [4, 7, 12, 25]:
        tot = 0.0
        for dd in range(1, 2 * N):
            t = pi * dd / N; S2 = (np.sin(N * t / 2) / np.sin(t / 2)) ** 2 if dd % 2 else 0.0
            tot += (N * N - S2) / np.sin(t / 2) ** 2
        print(f"  ACUE lattice kernel sum N={N:2d}: (1/2N) sum_d (N^2 - S_N^2) csc^2 / (3 C_N/2) = {tot/(2*N)/(1.5*CN(N)):.12f}")

# ---------------------------------------------------------------- section 4
def section4():
    import sympy as sp
    print("== Section 4: exponential-polynomial structure of disc(P_s)")
    s, E = sp.symbols('s E', positive=True)   # E = e^{s}
    z = sp.symbols('z')
    for N in [3, 4]:
        a = sp.symbols(f'a0:{N}')
        P = z ** N + sum(a[j] * E ** (j * (N - j)) * z ** j for j in range(N))
        disc = sp.expand(sp.discriminant(P, z))
        poly = sp.Poly(disc, *a, E)
        ok = True; wmax = 0
        for monom, c in poly.terms():
            e = monom[:N]; wexp = monom[N]
            eN = 2 * N - 2 - sum(e)
            q = sum(e[j] * j * j for j in range(N)) + eN * N * N
            w = sum(e[j] * j * (N - j) for j in range(N))
            iso = sum(e[j] * (N - j) for j in range(N))
            if not (wexp == w == N * N * (N - 1) - q and iso == N * (N - 1) and eN >= 0): ok = False
            wmax = max(wmax, wexp)
        print(f"  N={N}: {len(poly.terms())} monomials; every monomial has exponent of e^s equal to "
              f"sum_j e_j j(N-j) = N^2(N-1) - q_m, isobaric weight N(N-1): {ok}; max exponent {wmax} "
              f"(bound N^2(N-1)/2 = {N*N*(N-1)//2})")
        if N == 3:
            print("  disc(P_s), N=3:", sp.factor_terms(sp.collect(disc, E)))
        # coefficient-space form of the force identity at random circle-rooted P
        for trial in range(2):
            th = random_config(N)
            zz = np.exp(1j * th); coef = np.poly(zz)         # highest first
            aval = {a[j]: complex(coef[N - j]) for j in range(N)}
            D0 = sp.discriminant(z ** N + sum(a[j] * z ** j for j in range(N)), z)
            euler = sum(j * (N - j) * a[j] * sp.diff(D0, a[j]) for j in range(N))
            lhs = complex(euler.subs(aval)) / complex(D0.subs(aval))
            V, Q, _ = forces(th)
            print(f"     N={N} random P: sum_j j(N-j) a_j d log disc/d a_j = {lhs.real:.12f}{lhs.imag:+.1e}i,"
                  f"  C_N - Q = {CN(N)-Q:.12f}")

# ---------------------------------------------------------------- section 5
def section5():
    print("== Section 5: Riccati lower bound on ACUE data and the (N^2/2) conjecture")
    for N in range(4, 13):
        f = os.path.join(HERE, f"acue_depth_N{N}.npz")
        if not os.path.exists(f): continue
        d = np.load(f); D = d['D']; Q0 = d['Q0']; C = CN(N); fin = np.isfinite(D)
        A0 = Q0[fin] - C
        bound = np.log1p(C / A0) / C
        ratio = D[fin] / bound
        bound2 = (2 / N ** 2) * np.log1p(N ** 2 / (2 * A0))
        ratio2 = D[fin] / bound2
        print(f"  N={N:2d}: min D/[(1/C_N)log(1+C_N/A_0)] = {ratio.min():.4f} (max {ratio.max():.1f});"
              f"  min D/[(2/N^2)log(1+N^2/(2A_0))] = {ratio2.min():.4f}  (N^2 D_min={N*N*D[fin].min():.4f})")
    # the sharp Riccati constant kappa_N := sup (A'-A^2)/A.  Proved: kappa_N <= C_N.  Close-pair limit in the
    # doubled (N-1)-clock: (N^2+4N-6)/3.  Random search + local optimisation over backgrounds of a close pair.
    print("  sharp Riccati constant kappa_N = sup (A'-A^2)/A  [proved <= C_N; the pointwise (N^2/2) bound is FALSE]:")
    from scipy.optimize import minimize
    def ratio(th):
        V, Q, Ap = forces(th); A = np.sum(V ** 2); return (Ap - A * A) / A
    for N in [3, 4, 5, 6, 8, 12]:
        worst = -np.inf
        for trial in range(3000):
            kind = trial % 3
            if kind == 0: th = np.sort(rng.uniform(0, 2 * pi, N))
            elif kind == 1: th = np.sort(2 * pi * np.arange(N) / N + rng.normal(0, 0.3 / N, N))
            else:
                th = np.sort(rng.uniform(0, 2 * pi, N)); th[1] = th[0] + 10 ** rng.uniform(-4, -1)
            worst = max(worst, ratio(th))
        # close pair (gap 1e-4) with optimised background
        best = -np.inf
        for trial in range(20 if N <= 8 else 5):
            x0 = np.sort(rng.uniform(0.3, 2 * pi - 0.3, N - 2))
            def f(x):
                xs = np.sort(x)
                if np.min(xs) < 1e-3 or np.max(xs) > 2 * pi - 1e-3 or (len(xs) > 1 and np.min(np.diff(xs)) < 1e-3): return 1e9
                return -ratio(np.concatenate([[-5e-5, 5e-5], xs]))
            res = minimize(f, x0, method='Nelder-Mead', options={'xatol': 1e-8, 'fatol': 1e-10, 'maxiter': 3000})
            best = max(best, -res.fun)
        th = np.concatenate([[-5e-5, 5e-5], 2 * pi * np.arange(1, N - 1) / (N - 1)])
        print(f"    N={N:2d}: random search max {worst:9.4f}; close pair + optimised background {best:9.4f};"
              f"  doubled-clock value (N^2+4N-6)/3 = {(N*N+4*N-6)/3:8.4f} (numeric {ratio(th):8.4f});"
              f"  N^2/2 = {N*N/2:6.1f};  C_N = {CN(N):7.1f}")

# ---------------------------------------------------------------- section 6
def flow_ode(theta0, s_end, n_out=200, rtol=1e-12):
    """integrate Lemma 1 theta' = -V(theta) with DOP853; return s grid and F(s)=log|disc| and A(s)."""
    from scipy.integrate import solve_ivp
    N = len(theta0)
    def rhs(s, th):
        V, _, _ = forces(th); return -V
    sol = solve_ivp(rhs, [0, s_end], np.asarray(theta0, float), method='DOP853', rtol=rtol, atol=1e-13,
                    dense_output=True)
    ss = np.linspace(0, s_end, n_out)
    F = np.zeros(n_out); A = np.zeros(n_out)
    for i, s in enumerate(ss):
        th = sol.sol(s)
        d = th[:, None] - th[None, :]; iu = np.triu_indices(N, 1)
        F[i] = np.sum(2 * np.log(np.abs(2 * np.sin(d[iu] / 2))))
        V, Q, _ = forces(th); A[i] = np.sum(V ** 2)
    return ss, F, A

def logdisc_midpoint_exact(N, s):
    """log|disc P_s| for P_0=(z-1)(z^{N-1}+1): 4 (lam(N-1))^N [sin(N phi/2)-lam sin((N-2)phi/2)]^2/(lam^2-1)"""
    if s == 0: return log(4) + (N - 1) * log(N - 1)
    lam = np.exp(s * (N - 1))
    cphi = (N + lam ** 2 * (N - 2)) / (2 * lam * (N - 1))
    phi = np.arccos(cphi)
    return log(4) + N * (log(lam) + log(N - 1)) + 2 * log(abs(np.sin(N * phi / 2) - lam * np.sin((N - 2) * phi / 2))) - log(lam ** 2 - 1)

def depth_bisect(theta, tol=1e-13):
    """first collision time by bisection on the off-circle indicator (copy of acue_depth_enum.depth_bisect)"""
    N = len(theta); z = np.exp(1j * theta); a = np.poly(z)
    powers = np.arange(N, -1, -1); w = powers * (N - powers)
    def off(s): return np.max(np.abs(np.abs(np.roots(a * np.exp(s * w))) - 1.0))
    lo = 0.0; hi = 4.0 / N ** 2
    while off(hi) < 1e-7: hi *= 2
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if off(mid) > 1e-7: hi = mid
        else: lo = mid
        if hi - lo < tol * max(1, hi): break
    return 0.5 * (lo + hi)

def DeltaF_local(tau):
    w = np.sqrt(tau * (2 - tau))
    return tau - np.log(2 * tau) + 2 * np.log(np.abs(w * np.cos(w / 2) - tau * np.sin(w / 2)))

def a_local_closed(tau):
    """a(tau) = -d/dtau Delta F_local, differentiated in closed form"""
    w = np.sqrt(tau * (2 - tau)); wp = (1 - tau) / w
    num = wp * ((1 - tau / 2) * np.cos(w / 2) - (w / 2) * np.sin(w / 2)) - np.sin(w / 2)
    return -1 + 1 / tau - 2 * num / (w * np.cos(w / 2) - tau * np.sin(w / 2))

def a_local(tau, nroots=4000):
    """local force energy 4 sum_{u_j != 0} u_j^2/(u_j^2 - c)^2, c = tau(2-tau), u_j roots of u cot(u/2) = tau"""
    from scipy.optimize import brentq
    c = tau * (2 - tau); tot = 0.0
    for m in range(nroots):
        lo = 2 * m * pi + 1e-12; hi = (2 * m + 2) * pi - 1e-12   # one root of u cot(u/2)=tau in each (2m pi,(2m+2)pi)
        f = lambda u: u * np.cos(u / 2) - tau * np.sin(u / 2)
        u = brentq(f, lo, hi)
        tot += 2 * 4 * u * u / (u * u - c) ** 2                  # +-u
    return tot

def section6():
    print("== Section 6: the 3-block local limit")
    # (a) exact discriminant of the midpoint family vs numerical, and its depth
    for N in [5, 7, 11, 16]:
        th = np.concatenate([[0.0], (2 * np.arange(N - 1) + 1) * pi / (N - 1)])
        Dex = log(N / (N - 2)) / (N - 1)
        errs = []
        for s in [0.1 * Dex, 0.5 * Dex, 0.9 * Dex]:
            Fnum = float(logdisc_mp(th, s)); Fex = logdisc_midpoint_exact(N, s)
            errs.append(abs(Fnum - Fex))
        Dnum = depth_bisect(th)
        print(f"  midpoint family N={N:2d}: max |log disc_num - log disc_exact| = {max(errs):.1e};"
              f"  D_num = {Dnum:.12f}, log(N/(N-2))/(N-1) = {Dex:.12f}, N^2 D = {N*N*Dex:.6f}")
    # (b) local closed form vs N-body for the midpoint family
    print("  local limit, midpoint family: Delta F(tau) N-body vs tau - log 2tau + 2 log|w cos(w/2) - tau sin(w/2)|")
    taus = np.array([0.25, 0.5, 1.0, 1.5, 1.8])
    for N in [32, 64, 128, 256]:
        th = np.concatenate([[0.0], (2 * np.arange(N - 1) + 1) * pi / (N - 1)])
        F0 = log(4) + (N - 1) * log(N - 1)
        vals = np.array([logdisc_midpoint_exact(N, tau / N ** 2) - F0 for tau in taus])
        print(f"    N={N:3d}: exact-finite-N Delta F = {np.array2string(vals, precision=6)}")
        if N == 128: v128 = vals
        if N == 256: print(f"    Richardson 2*F(256)-F(128)   = {np.array2string(2*vals - v128, precision=6)}")
    print(f"    local closed form         = {np.array2string(DeltaF_local(taus), precision=6)}")
    print(f"    local force energy a(tau) = -dDeltaF/dtau, by root sum: "
          f"{np.array2string(np.array([a_local(t) for t in taus]), precision=6)}")
    dd = 1e-5
    print(f"    ... by differentiating the closed form: "
          f"{np.array2string(np.array([-(DeltaF_local(t+dd)-DeltaF_local(t-dd))/(2*dd) for t in taus]), precision=6)}")
    print(f"    ... analytic derivative a_local_closed: "
          f"{np.array2string(np.array([a_local_closed(t) for t in taus]), precision=6)}")
    print(f"    a(0) by root sum = {a_local(1e-9):.6f} (predicted 1);  a(tau)(2-tau) near tau=2: "
          f"{a_local(1.99)*0.01:.4f}, {a_local(1.999)*0.001:.4f} (predicted 3)")
    # (c) N-body ODE check of the closed form for the midpoint family at N=96 (Lemma 1 integrated)
    N = 96
    th = np.concatenate([[0.0], (2 * np.arange(N - 1) + 1) * pi / (N - 1)])
    ss, F, A = flow_ode(th, 1.5 / N ** 2, n_out=7)
    print(f"    N-body ODE N={N}: tau = {np.array2string(ss*N*N, precision=3)}")
    print(f"       Delta F (ODE)   = {np.array2string(F - F[0], precision=6)}")
    print(f"       Delta F (exact) = {np.array2string(np.array([logdisc_midpoint_exact(N, s) for s in ss]) - (log(4)+(N-1)*log(N-1)), precision=6)}")
    print(f"       A/N^2 (ODE)     = {np.array2string(A / N**2, precision=6)}")
    print(f"       a(tau) local    = {np.array2string(np.array([a_local(s*N*N) for s in ss]), precision=6)}")
    # (d) ACUE 3-block with hole [1,1,2..2,4,2..2] (N odd): additivity block + hole
    print("  ACUE family [1,1,2,...,2,4,2,...,2]: Delta F = Delta F_block + Delta F_hole + o(1)?")
    for N in [63, 127]:
        k = (N - 3) // 2; g = [1, 1] + [2] * k + [4] + [2] * (N - 3 - k)
        sites = np.concatenate([[0], np.cumsum(g)[:-1]]); th = 2 * pi * sites / (2 * N)
        ss, Fb, Ab = flow_ode(th, 1.5 / N ** 2, n_out=4)
        # pure hole: the N-clock (N odd, so -1 is a clock root) minus the root at -1: N-1 roots, same lattice
        thh = np.array([(2 * j + 1) * pi / N for j in range(N) if abs(((2 * j + 1) * pi / N) - pi) > 1e-9])
        assert len(thh) == N - 1
        ssh, Fh, Ah = flow_ode(thh, 1.5 / N ** 2, n_out=4)
        tau = ss * N * N
        print(f"    N={N}: tau = {np.array2string(tau, precision=3)}")
        print(f"      Delta F (ACUE 3-block+hole, ODE) = {np.array2string(Fb - Fb[0], precision=5)}")
        print(f"      Delta F_block (closed form)       = {np.array2string(np.array([DeltaF_local(t) if t>0 else 0 for t in tau]), precision=5)}")
        print(f"      Delta F_hole  (pure hole, ODE)    = {np.array2string(Fh - Fh[0], precision=5)}")
        print(f"      block + hole                      = {np.array2string(np.array([DeltaF_local(t) if t>0 else 0 for t in tau]) + Fh - Fh[0], precision=5)}")
        print(f"      A_0/N^2 = {Ab[0]/N**2:.5f} (block 1 + hole 1/3 = 1.33333);  hole alone A_0/N^2 = {Ah[0]/N**2:.5f}")

# ---------------------------------------------------------------- section 7 (supplementary)
def section7():
    print("== Section 7: supplementary checks")
    # (a) midpoint family: the triple collision at z=1 is the first collision, N=3..40
    worst = 0
    for N in range(3, 41):
        th = np.concatenate([[0.0], (2 * np.arange(N - 1) + 1) * pi / (N - 1)])
        Dnum = depth_bisect(th); Dex = log(N / (N - 2)) / (N - 1)
        worst = max(worst, abs(Dnum / Dex - 1))
    print(f"  (a) midpoint family N=3..40: max |D_num/D_exact - 1| = {worst:.1e}  (D_exact = log(N/(N-2))/(N-1))")
    # (b) close-pair limit of (A'-A^2)/A -> 2 + 3 sigma - 4 beta^2 - 2 sum v_k^2 for a random background
    for N in [4, 6, 9]:
        x = np.sort(rng.uniform(0.4, 2 * pi - 0.4, N - 2))
        sigma = np.sum(1 / np.sin(x / 2) ** 2); beta = np.sum(1 / np.tan(x / 2))
        W = np.array([sum(1 / np.tan((x[k] - x[l]) / 2) for l in range(N - 2) if l != k) for k in range(N - 2)])
        v = 2 / np.tan(x / 2) + W
        pred = 2 + 3 * sigma - 4 * beta ** 2 - 2 * np.sum(v ** 2)
        g = 1e-4; th = np.concatenate([[-g / 2, g / 2], x])
        V, Q, Ap = forces(th); A = np.sum(V ** 2)
        print(f"  (b) N={N}: (A'-A^2)/A at gap 1e-4 = {(Ap-A*A)/A:.6f}, close-pair limit formula = {pred:.6f}")
    # (c) is D a function of disc(P_0) alone?  ACUE N=12: spread of N^2 D within narrow bands of log|disc P_0|
    f = os.path.join(HERE, "acue_depth_N12.npz")
    if os.path.exists(f):
        d = np.load(f); N = 12; D = d['D']; fin = np.isfinite(D)
        F0 = np.log(d['mass'][fin]) + N * log(2 * N); ND = N * N * D[fin]
        order = np.argsort(F0); bands = np.array_split(order, 8)
        print("  (c) ACUE N=12, orbits binned by log|disc P_0| (8 quantile bands): [F0 range] -> N^2 D min / max")
        for b in bands:
            print(f"      [{F0[b].min():7.2f},{F0[b].max():7.2f}] -> {ND[b].min():.4f} / {ND[b].max():.4f}")
        print(f"      Pearson corr(F0, N^2 D) = {np.corrcoef(F0, ND)[0,1]:.3f}; clock value F0 = N log N = {N*log(N):.2f}")

if __name__ == "__main__":
    which = [int(x) for x in sys.argv[1:]] or [1, 3, 4, 5, 6, 7]
    t0 = time.time()
    if 1 in which or 2 in which: section12()
    if 3 in which: section3()
    if 4 in which: section4()
    if 5 in which: section5()
    if 6 in which: section6()
    if 7 in which: section7()
    print(f"total time {time.time()-t0:.1f}s")

