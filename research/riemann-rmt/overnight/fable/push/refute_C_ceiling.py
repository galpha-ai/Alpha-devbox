"""Refuter checks for Task C (push_C_ceiling_conjecture.md).  Independent code throughout: no import of the
proposer's push_C_*.py modules.  Sections (argv[1]):

  gamma      domain-wall model q_0 = cos(u/2)/Gamma(u/2pi): heat flow by DIRECT Gaussian convolution (no Hankel
             integral), cross-check of the Hankel representation at sample points, C* by 2-D Newton on (q, q_u)=0,
             and a zero-count certificate that the edge pair is the FIRST collision (window [-8pi, 6pi]).
  local      finite-L local models: odd L=2k+1 via the exact polynomial closed form e^{tau d^2}p = sum tau^j p^(2j)/j!,
             even L=2m via the parity-wall function p(u)/(Gamma(u/2pi) Gamma(1/2-u/2pi)) and direct convolution.
             Gives tau*_L for L=3..12(+), tests the monotonicity claim, and extrapolates to C*.
  fourier    exact finite-N depth of the run|clock|hole family maximisers at N=64,128,256 (and N=11,12 winners)
             from the Fourier representation Q_s(x) = Re kappa sum a_j e^{s j(N-j)} e^{i(j-N/2)x} at 70-200 digits,
             tracking the extremum of Q_s between the two edge zeros (no ODE, no polyroots).
  polyroots  mpmath polyroots ground truth at N=64 (k=15, L=34) -- slow (minutes).
  ode        my own N-body ODE solver (Lemma 1) -- used by the searches; validated here against 'fourier'.
  unique     unique-1-gap comparison ODE re-solved independently (tau_1(N) and the N->inf limit), the elementary
             inequalities re-proved exactly, and an in-class hill-climb looking for a counterexample.
  beta       the 'protection lemma' beta_config <= beta_wall tested on the 3-block, 5-block, 7-block, N=12 winner.
  cond       the conditional theorem's ODE: the stated formula vs the one that actually follows from Sec.6(iv).
  search     hill-climb / annealing over gap patterns at N=13..20 with my own moves, and a full 1-move neighbourhood
             scan around the family optimum at N=32, 48 (looking for anything above the family or above C*).
  enum13     read the complete N=13 enumeration (acue_depth_enum.py run into the scratchpad) and compare.
"""
import sys, time, itertools, os
import numpy as np
import mpmath as mp
from scipy.integrate import solve_ivp

PI = np.pi
SCR = "/tmp/claude-0/-home-user-Alpha-devbox/00b3b5f7-f917-5641-a9be-c6a8f38f5cd7/scratchpad"
CSTAR_DOC = 2.1146648843

# ----------------------------------------------------------------------------------------------------------
# Heat flow by DIRECT Gaussian convolution.  numpy (trapezoid on a fine grid; the integrand is entire and
# Gaussian-decaying, so the trapezoid rule converges super-geometrically) for scanning / zero counting, and an
# mpmath composite Gauss-Legendre version for the final high-precision Newton.
#   q(u,tau) = int K_tau(v) f(u-v) dv,   d/du K = -(v/2tau) K,  etc.  -> moments [q, q_u, q_uu, q_uuu]
# ----------------------------------------------------------------------------------------------------------
import scipy.special as sps
def heat_np(fnp, us, tau, R=45.0, h=0.02, nmom=4):
    """vectorised: returns array (nmom, len(us))"""
    v = np.arange(-R, R + h / 2, h)
    K = np.exp(-v * v / (4 * tau)) / np.sqrt(4 * PI * tau)
    t1 = -v / (2 * tau)
    polys = [np.ones_like(v), t1, t1 * t1 - 1 / (2 * tau), t1 ** 3 - 3 * t1 / (2 * tau)][:nmom]
    us = np.atleast_1d(np.asarray(us, float))
    out = np.zeros((nmom, len(us)))
    # chunk over u to bound memory
    for a in range(0, len(us), 400):
        ub = us[a:a + 400]
        F = fnp(ub[:, None] - v[None, :])            # (nu, nv)
        for m in range(nmom):
            out[m, a:a + 400] = h * (F * (K * polys[m])[None, :]).sum(axis=1)
    return out

_GL = {}
def gl_nodes(deg):
    key = (deg, mp.mp.dps)
    if key not in _GL:
        gq = mp.calculus.quadrature.GaussLegendre(mp.mp)
        _GL[key] = gq.calc_nodes(deg, mp.mp.prec)   # list of (x, w) on [-1, 1]
    return _GL[key]

def heat_mp(f, u, tau, R=None, nsub=None, deg=4, nmom=4):
    tau = mp.mpf(tau); u = mp.mpf(u)
    if R is None: R = mp.mpf(45)
    if nsub is None: nsub = 60
    nodes = gl_nodes(deg)
    hh = 2 * R / nsub
    acc = [mp.mpf(0)] * nmom
    norm = 1 / mp.sqrt(4 * mp.pi * tau)
    for i in range(nsub):
        a = -R + i * hh; c = a + hh / 2; r = hh / 2
        for x, w in nodes:
            v = c + r * x
            K = mp.exp(-v * v / (4 * tau)) * norm
            base = w * r * K * f(u - v)
            t1 = -v / (2 * tau)
            polys = [1, t1, t1 * t1 - 1 / (2 * tau), t1 ** 3 - 3 * t1 / (2 * tau)]
            for m in range(nmom): acc[m] += base * polys[m]
    return acc

def newton_double_zero(mom, u0, tau0, tol=1e-13, maxit=40, verbose=False):
    """2-D Newton on F(u,tau) = (q, q_u) = 0 using q_tau = q_uu, q_{u tau} = q_uuu.  mom returns mp values."""
    u, tau = mp.mpf(u0), mp.mpf(tau0)
    for it in range(maxit):
        q, qu, quu, quuu = mom(u, tau)
        J = mp.matrix([[qu, quu], [quu, quuu]])
        try: d = mp.lu_solve(J, mp.matrix([-q, -qu]))
        except ZeroDivisionError: return None
        u += d[0]; tau += d[1]
        if verbose: print(f"    newton {it}: u={mp.nstr(u,12)} tau={mp.nstr(tau,14)} |q|={mp.nstr(abs(q),3)} |q_u|={mp.nstr(abs(qu),3)}", flush=True)
        if abs(d[0]) + abs(d[1]) < tol: break
    q, qu, quu, quuu = mom(u, tau)
    return u, tau, q, qu, quu

def newton_np(momnp, u0, tau0, tol=1e-12, maxit=50):
    u, tau = float(u0), float(tau0)
    for it in range(maxit):
        q, qu, quu, quuu = momnp(u, tau)
        J = np.array([[qu, quu], [quu, quuu]]); d = np.linalg.solve(J, [-q, -qu])
        u += d[0]; tau += d[1]
        if abs(d[0]) + abs(d[1]) < tol: break
    return u, tau, momnp(u, tau)

def zeros_np(qgrid_fun, lo, hi, n):
    """qgrid_fun(us)->values; returns refined zeros (bisection in the bracketing cells, 40 steps)"""
    xs = np.linspace(lo, hi, n + 1); vs = qgrid_fun(xs)
    idx = np.where(vs[:-1] * vs[1:] < 0)[0]
    zs = []
    for i in idx:
        a, b = xs[i], xs[i + 1]; fa = vs[i]
        for _ in range(40):
            m = 0.5 * (a + b); fm = qgrid_fun(np.array([m]))[0]
            if fa * fm <= 0: b = m
            else: a, fa = m, fm
        zs.append(0.5 * (a + b))
    return np.array(zs)

def track_first_fold(momnp, lo, hi, n, taus, label, mp_mom=None):
    """zero count on [lo,hi] along taus; at the first drop take the closest pair and Newton (numpy, then mp)."""
    q_of = lambda tau: (lambda us: momnp(us, tau)[0])
    prev = None
    for tau in taus:
        zs = zeros_np(q_of(tau), lo, hi, n)
        if prev is not None and len(zs) < len(prev[0]):
            zp = prev[0]; gaps = np.diff(zp); im = int(np.argmin(gaps))
            u0 = 0.5 * (zp[im] + zp[im + 1])
            un, tn, m = newton_np(lambda u, t: momnp(np.array([u]), t)[:, 0], u0, prev[1])
            line = f"  {label}: tau* = {tn:.10f}  u* = {un/PI:.7f} pi  (pair before: {zp[im]/PI:.4f},{zp[im+1]/PI:.4f} pi at tau={prev[1]:.3f}; count {len(prev[0])} -> {len(zs)}; q_uu={m[2]:.4f})"
            res = None
            if mp_mom is not None:
                res = newton_double_zero(mp_mom, un, tn)
                line += f"  mp-refined: tau* = {mp.nstr(res[1],13)}, u*/pi = {mp.nstr(res[0]/mp.pi,9)}"
            print(line, flush=True)
            return (float(res[1]) if res else tn), un, (zp[im], zp[im + 1]), zp
        prev = (zs, tau)
    print(f"  {label}: no fold found up to tau={taus[-1]}"); return None

# ----------------------------------------------------------------------------------------------------------
def section_gamma():
    print("== gamma section: direct-convolution heat flow of q_0(u) = cos(u/2)/Gamma(u/2pi)   [no Hankel integral]")
    fnp = lambda x: np.cos(x / 2) * sps.rgamma(x / (2 * PI))
    momnp = lambda us, tau: heat_np(fnp, us, tau)
    # (0) quadrature convergence + heat equation
    for h in [0.05, 0.02, 0.01]:
        print(f"  h={h}: q(0.3,2.1) = {heat_np(fnp, [0.3], 2.1, h=h)[0,0]:.15f}")
    for (u0, t0) in [(0.3, 1.0), (2.0, 2.0), (-4.0, 1.5)]:
        m = momnp([u0], t0)[:, 0]; dq = (momnp([u0], t0 + 1e-5)[0, 0] - momnp([u0], t0 - 1e-5)[0, 0]) / 2e-5
        print(f"  heat-equation check at (u,tau)=({u0},{t0}): q_uu={m[2]:.12f}  dq/dtau (FD)={dq:.12f}")
    # (1) Hankel cross-check (re-implemented, not imported)
    mp.mp.dps = 20
    def G_hankel(w, tau):
        tau = mp.mpf(tau); w = mp.mpc(w)
        def g(t, lnt): return mp.exp(t + tau * lnt ** 2 / (4 * mp.pi ** 2) - (w / (2 * mp.pi)) * lnt)
        ray = mp.quad(lambda x: g(-x, mp.log(x) - 1j * mp.pi) - g(-x, mp.log(x) + 1j * mp.pi), [1, 4, 16, 64, mp.inf])
        circ = mp.quad(lambda ph: g(mp.expj(ph), 1j * ph) * 1j * mp.expj(ph), [-mp.pi, 0, mp.pi])
        return (ray + circ) / (2j * mp.pi)
    q_hankel = lambda u, tau: mp.re(mp.expj(u / 2) * G_hankel(u + 1j * tau, tau)) * mp.exp(-mp.mpf(tau) / 4)
    for (u0, t0) in [(0.3, 2.1), (1.5, 1.0), (-2.5, 2.0), (0.29, 2.114), (-7.0, 2.0)]:
        a = momnp([u0], t0)[0, 0]; b = q_hankel(u0, t0)
        print(f"  Hankel vs convolution at (u,tau)=({u0},{t0}): conv={a:.12f}  hankel={mp.nstr(b,13)}  diff={mp.nstr(a-b,3)}")
    # (2) zero count on [-10pi, 6pi] along tau: certificate that nothing collides before the edge pair
    print("  zeros on [-10pi,6pi] (grid step 0.02) and the smallest gap:")
    lo, hi = -10 * PI, 6 * PI; n = int((hi - lo) / 0.02)
    for t0 in [1e-6, 0.5, 1.0, 1.5, 2.0, 2.1, 2.11, 2.114, 2.1146]:
        zs = zeros_np(lambda us: momnp(us, t0)[0], lo, hi, n)
        gaps = np.diff(zs); im = int(np.argmin(gaps))
        print(f"    tau={t0:<7}: {len(zs)} zeros; min gap {gaps[im]/PI:.5f} pi at ({zs[im]/PI:.4f},{zs[im+1]/PI:.4f}) pi; zeros/pi: {np.round(zs/PI,3).tolist()}", flush=True)
    # (3) first fold by tracking, numpy Newton, then mp refinement
    mp.mp.dps = 22
    fmp = lambda v: mp.cos(v / 2) * mp.rgamma(v / (2 * mp.pi))
    mp_mom = lambda u, tau: heat_mp(fmp, u, tau, deg=4)
    taus = list(np.arange(2.0, 2.2, 0.002))
    r = track_first_fold(momnp, -3 * PI, 3 * PI, 600, taus, "wall", mp_mom=mp_mom)
    print(f"  ==> C* (mine) vs doc {CSTAR_DOC}: difference {r[0]-CSTAR_DOC:+.3e}")
    mp.mp.dps = 30
    mp_mom2 = lambda u, tau: heat_mp(fmp, u, tau, deg=5, nsub=90, R=mp.mpf(50))
    res = newton_double_zero(mp_mom2, r[1], r[0])
    print(f"  high-precision re-solve (dps 30, 48-node GL x 90 panels, R=50): C* = {mp.nstr(res[1],15)}, u_c/pi = {mp.nstr(res[0]/mp.pi,11)}, q_uu = {mp.nstr(res[4],8)}")
    # (4) zero count around the fold
    for t0 in [r[0] - 1e-4, r[0] + 1e-4, r[0] + 0.02]:
        zs = zeros_np(lambda us: momnp(us, t0)[0], -PI / 2, 3 * PI / 2, 4000)
        print(f"  zeros in (-pi/2,3pi/2) at tau={t0:.6f}: {len(zs)}  {np.round(zs/PI,4).tolist()}")

# ----------------------------------------------------------------------------------------------------------
def poly_from_roots(roots):
    a = [mp.mpf(1)]
    for r in roots:
        new = [mp.mpf(0)] * (len(a) + 1)
        for k, c in enumerate(a):
            new[k + 1] += c; new[k] -= c * r
        a = new
    return a

def poly_deriv(a, n=1):
    for _ in range(n):
        a = [k * a[k] for k in range(1, len(a))]
        if not a: a = [mp.mpf(0)]
    return a

def heat_poly(a, tau):
    out = list(a); d = a; j = 1
    while True:
        d = poly_deriv(d, 2)
        if len(d) == 1 and d[0] == 0: break
        for k in range(len(d)): out[k] += tau ** j / mp.factorial(j) * d[k]
        j += 1
    return out

def polyval(a, x):
    s = mp.mpc(0)
    for c in reversed(a): s = s * x + c
    return s

def odd_model(k):
    """(2k+1)-run: p(u) = prod_{j=0}^{k-1}(u + 2 pi j), q_0 = p cos(u/2); q = e^{-tau/4} Re[e^{iu/2} P_tau(u+i tau)].
    returns (numpy moments over a u-array, mp moments)"""
    a = poly_from_roots([-2 * mp.pi * j for j in range(k)])
    def mom_mp(u, tau):
        u = mp.mpf(u); tau = mp.mpf(tau)
        P = heat_poly(a, tau); P1 = poly_deriv(P); P2 = poly_deriv(P1); P3 = poly_deriv(P2)
        w = u + 1j * tau; e = mp.expj(u / 2) * mp.exp(-tau / 4); i = mp.mpc(0, 1)
        p0, p1, p2, p3 = polyval(P, w), polyval(P1, w), polyval(P2, w), polyval(P3, w)
        return [mp.re(e * p0), mp.re(e * (i / 2 * p0 + p1)), mp.re(e * (-p0 / 4 + i * p1 + p2)),
                mp.re(e * (-i / 8 * p0 - mp.mpf(3) / 4 * p1 + 3 * i / 2 * p2 + p3))]
    def mom_np(us, tau):
        tau = float(tau); P = [float(c) for c in heat_poly(a, mp.mpf(tau))]
        Pp = np.polynomial.polynomial
        P1 = Pp.polyder(P); P2 = Pp.polyder(P1); P3 = Pp.polyder(P2)
        us = np.atleast_1d(np.asarray(us, float)); w = us + 1j * tau; e = np.exp(1j * us / 2) * np.exp(-tau / 4)
        p0, p1, p2, p3 = Pp.polyval(w, P), Pp.polyval(w, P1), Pp.polyval(w, P2), Pp.polyval(w, P3)
        return np.array([np.real(e * p0), np.real(e * (0.5j * p0 + p1)), np.real(e * (-p0 / 4 + 1j * p1 + p2)),
                         np.real(e * (-0.125j * p0 - 0.75 * p1 + 1.5j * p2 + p3))])
    return mom_np, mom_mp

def even_model(m):
    """2m-run (parity wall): q_0 = prod_{j=1}^{m-1}(u-2 pi j) / (Gamma(u/2pi) Gamma(1/2-u/2pi)).
    zeros: 0,-2pi,-4pi,... (run start + left clock), pi,3pi,... (run + right clock), 2pi..2pi(m-1) (interior)."""
    def fnp(x):
        z = x / (2 * PI); p = np.ones_like(x)
        for j in range(1, m): p = p * (x - 2 * PI * j)
        return p * sps.rgamma(z) * sps.rgamma(0.5 - z)
    def fmp(v):
        z = v / (2 * mp.pi); p = mp.mpf(1)
        for j in range(1, m): p *= (v - 2 * mp.pi * j)
        return p * mp.rgamma(z) * mp.rgamma(mp.mpf(1) / 2 - z)
    return (lambda us, tau: heat_np(fnp, us, tau)), (lambda u, tau: heat_mp(fmp, u, tau, deg=4))

def section_local():
    print("== local section: finite-L local models, first double zero tau*_L (numpy scan + mp Newton)")
    doc = {3: 2.0000, 4: 1.9630, 5: 2.0000, 6: 2.0227, 7: 2.0381, 8: 2.0490, 9: 2.0573, 10: 2.0637, 12: 2.0730, 15: 2.0819, 21: 2.0919}
    refA = {7: 2.0381260536, 9: 2.0573579730, 11: 2.0688935596}
    results = {}
    mp.mp.dps = 30
    taus = list(np.arange(1.5, 2.4, 0.004))
    for k in range(1, 11):     # odd L = 3..21
        L = 2 * k + 1; mnp, mmp = odd_model(k)
        lo = -2 * PI * (k - 1) - 5 * PI; hi = 6 * PI; n = int((hi - lo) / 0.02)
        r = track_first_fold(mnp, lo, hi, n, taus, f"L={L:2d} (odd, k={k})", mp_mom=mmp)
        if r: results[L] = r[0]
    mp.mp.dps = 20
    taus = list(np.arange(1.5, 2.4, 0.005))
    for m in range(2, 7):      # even L = 4..12
        L = 2 * m; mnp, mmp = even_model(m)
        lo = -5 * PI; hi = 2 * PI * (m - 1) + 6 * PI; n = int((hi - lo) / 0.02); t0 = time.time()
        r = track_first_fold(mnp, lo, hi, n, taus, f"L={L:2d} (even, m={m})", mp_mom=mmp)
        if r: results[L] = r[0]
        print(f"      [{time.time()-t0:.0f}s]")
    print("\n  L   tau*_L (mine)     doc table    refuter-A model")
    for L in sorted(results):
        print(f"  {L:2d}  {results[L]:.10f}   {doc.get(L,'-')}      {refA.get(L,'-')}")
    Ls = sorted(results)
    mono = all(results[Ls[i]] < results[Ls[i + 1]] for i in range(len(Ls) - 1) if Ls[i] >= 4)
    print(f"  monotone increasing for L>=4: {mono};  L=3 vs L=4: {results.get(3)} vs {results.get(4)}")
    odd = [L for L in Ls if L % 2 == 1 and L >= 9]
    if len(odd) >= 3:
        A = np.array([[1, 1 / L, 1 / L ** 2] for L in odd]); y = np.array([results[L] for L in odd])
        c = np.linalg.lstsq(A, y, rcond=None)[0]
        print(f"  fit tau*_L = C + c1/L + c2/L^2 over odd L={odd}: C = {c[0]:.6f}, c1 = {c[1]:.4f}, c2 = {c[2]:.3f}   (doc: C* = {CSTAR_DOC}, c1 = -0.452)")
    np.save(f"{SCR}/local_models.npy", np.array([(L, results[L]) for L in Ls]))

# ----------------------------------------------------------------------------------------------------------
# Exact finite-N Fourier tracker
# ----------------------------------------------------------------------------------------------------------
class Fourier:
    def __init__(self, gaps, dps):
        mp.mp.dps = dps
        N = len(gaps); self.N = N; M = 2 * N
        sites = [0]
        for g in gaps[:-1]: sites.append(sites[-1] + g)
        assert sites[-1] + gaps[-1] == M
        self.sites = sites
        theta = [2 * mp.pi * s / M for s in sites]
        roots = [mp.expj(t) for t in theta]
        a = [mp.mpc(1)]
        for r in roots:
            new = [mp.mpc(0)] * (len(a) + 1)
            for k, c in enumerate(a): new[k + 1] += c; new[k] -= c * r
            a = new
        kappa = mp.expj(sum(theta) / 2) / (2j) ** N
        self.c = [kappa * a[j] for j in range(N + 1)]
        self.m = [mp.mpf(j) - mp.mpf(N) / 2 for j in range(N + 1)]
        self.w = [mp.mpf(j) * (N - j) for j in range(N + 1)]
        self.theta = theta
        # sanity: Q_0 vs product at a random point
        x = mp.mpf('0.3'); prod = mp.mpf(1)
        for t in theta: prod *= mp.sin((x - t) / 2)
        Q = self.Q(x, mp.mpf(0))
        self.check = (Q, prod)
    def Q(self, x, s, d=0):
        tot = mp.mpc(0)
        for c, mm, w in zip(self.c, self.m, self.w):
            tot += c * mp.exp(s * w) * mp.expj(mm * x) * (1j * mm) ** d
        return mp.re(tot)
    def extremum(self, x0, s, it=60):
        x = x0
        for _ in range(it):
            f = self.Q(x, s, 1); fp = self.Q(x, s, 2)
            if fp == 0: return None
            dx = -f / fp; x += dx
            if abs(dx) < mp.mpf(10) ** (-(mp.mp.dps - 12)): break
        return x
    def pair_collision(self, i, tau_max=3.0, dtau=0.05):
        """collision time of the pair (site i, site i+1): track the extremum of Q_s between them."""
        N = self.N
        x = (self.theta[i] + self.theta[(i + 1) % N]) / 2
        if (i + 1) % N == 0: x = (self.theta[i] + self.theta[0] + 2 * mp.pi) / 2
        s = mp.mpf(0); sg = mp.sign(self.Q(x, s))
        x = self.extremum(x, s)
        h = lambda x, s: sg * self.Q(x, s)
        hs = h(x, s)
        assert hs > 0
        # march
        ds = mp.mpf(dtau) / N ** 2
        while True:
            s2 = s + ds; x2 = self.extremum(x, s2)
            if x2 is None: raise RuntimeError("extremum lost")
            h2 = h(x2, s2)
            if h2 <= 0: break
            s, x = s2, x2
            if s * N ** 2 > tau_max: return None
        lo, hi, xlo = s, s2, x
        for _ in range(200):
            mid = (lo + hi) / 2; xm = self.extremum(xlo, mid)
            if h(xm, mid) > 0: lo, xlo = mid, xm
            else: hi = mid
            if hi - lo < mp.mpf(10) ** (-(mp.mp.dps // 2)) * hi: break
        return (lo + hi) / 2, xlo

def fam(N, k):
    L = N - 2 * k; return [1] * (L - 1) + [2] * k + [L + 1] + [2] * k

def section_fourier():
    print("== fourier section: exact finite-N collision time of the edge pair from the Fourier representation")
    cases = [(12, [1] * 7 + [2, 2, 9, 2, 2], 0, 40, 2.0000177200),
             (11, [1] * 6 + [2, 2, 8, 2, 2], 0, 40, 1.9918104778),
             (64, fam(64, 15), 0, 70, 2.0925893),
             (128, fam(128, 31), 0, 110, 2.1035866),
             (256, fam(256, 63), 0, 200, 2.1091153)]
    out = {}
    for N, g, pair, dps, docval in cases:
        t0 = time.time(); F = Fourier(g, dps)
        Q0, prod = F.check
        r = F.pair_collision(pair)
        s, x = r
        val = float(N * N * s)
        out[N] = val
        print(f"  N={N:3d} gaps=[1^{N-2*(N-len([x for x in g if x==2])//2)-1}...] dps={dps}: Q_0 check |Q-prod|/|prod| = {mp.nstr(abs(Q0-prod)/abs(prod),3)};  N^2 D(pair {pair}) = {N*N*s}  (doc {docval}, diff {val-docval:+.2e});  extremum at x = {mp.nstr(x*N/mp.pi,6)} pi/N  [{time.time()-t0:.0f}s]", flush=True)
    print("  C* - max(N) times N (doc says 1.42/N 'to three digits'):")
    for N in [64, 128, 256]:
        if N in out: print(f"    N={N}: (C*-max)*N = {(CSTAR_DOC-out[N])*N:.4f}")

def section_polyroots():
    print("== polyroots section: mpmath polyroots ground truth, N=64, k=15 (L=34)")
    N = 64; g = fam(N, 15); dps = 60; mp.mp.dps = dps
    M = 2 * N; sites = [0]
    for x in g[:-1]: sites.append(sites[-1] + x)
    roots = [mp.expj(2 * mp.pi * s / M) for s in sites]
    a = [mp.mpc(1)]
    for r in roots:
        new = [mp.mpc(0)] * (len(a) + 1)
        for k, c in enumerate(a): new[k + 1] += c; new[k] -= c * r
        a = new
    def off(tau):
        s = mp.mpf(tau) / N ** 2
        c = [a[j] * mp.exp(s * j * (N - j)) for j in range(N + 1)]
        rts = mp.polyroots(c[::-1], maxsteps=300, extraprec=2 * mp.mp.prec)
        return max(abs(abs(z) - 1) for z in rts)
    t0 = time.time()
    lo, hi = mp.mpf('2.0'), mp.mpf('2.2')
    print(f"  off(2.0)={mp.nstr(off(lo),3)}  off(2.2)={mp.nstr(off(hi),3)}  [{time.time()-t0:.0f}s]", flush=True)
    assert off(lo) < 1e-25 and off(hi) > 1e-25
    for it in range(40):
        mid = (lo + hi) / 2
        if off(mid) > 1e-25: hi = mid
        else: lo = mid
        print(f"  bisect {it}: [{mp.nstr(lo,12)}, {mp.nstr(hi,12)}]  [{time.time()-t0:.0f}s]", flush=True)
        if hi - lo < 1e-10: break
    print(f"  ==> N^2 D (polyroots, N=64, k=15) = {mp.nstr((lo+hi)/2,12)}   (ODE value in the doc: 2.0925893)")

# ----------------------------------------------------------------------------------------------------------
# My own N-body ODE solver (Lemma 1), used by the searches
# ----------------------------------------------------------------------------------------------------------
def theta_of(gaps):
    N = len(gaps); s = np.concatenate([[0], np.cumsum(gaps)[:-1]]); return PI * s / N

def rhs(t, th):
    d = th[:, None] - th[None, :]
    np.fill_diagonal(d, PI)
    return -np.sum(1.0 / np.tan(0.5 * d), axis=1)

def depth(gaps, rtol=1e-11, eps1=2e-4, eps2=2e-5, theta=None):
    """first-collision time s* for a lattice gap pattern (or angles theta); returns (N^2 s*, colliding pair index)"""
    if theta is not None: th0 = np.asarray(theta, float); N = len(th0)
    else:
        th0 = theta_of(gaps); N = len(gaps)
        if all(g == 2 for g in gaps): return np.inf, None
    def mingap(y):
        t = np.sort(np.mod(y, 2 * PI)); gg = np.diff(np.concatenate([t, [t[0] + 2 * PI]])); return gg.min(), int(np.argmin(gg))
    def ev(t, y): return mingap(y)[0] - eps1
    ev.terminal = True; ev.direction = -1
    sol = solve_ivp(rhs, (0, 6.0 / N ** 2), th0, method='DOP853', rtol=rtol, atol=1e-14, events=ev)
    if not len(sol.t_events[0]): return np.inf, None
    s1 = sol.t_events[0][0]; y1 = sol.y_events[0][0]
    def ev2(t, y): return mingap(y)[0] - eps2
    ev2.terminal = True; ev2.direction = -1
    sol2 = solve_ivp(rhs, (s1, s1 + 1e-2 / N ** 2 + eps1 ** 2), y1, method='DOP853', rtol=rtol, atol=1e-14, events=ev2)
    s2 = sol2.t_events[0][0]; y2 = sol2.y_events[0][0]; g2, i2 = mingap(y2)
    # identify the pair in original labelling: sorted positions -> labels
    order = np.argsort(np.mod(y2, 2 * PI)); lab = int(order[i2])
    return N * N * (s2 - np.log(np.cos(g2 / 2))), lab

def section_ode():
    print("== ode section: my N-body solver vs the exact Fourier values")
    for N, g, ref in [(12, [1] * 7 + [2, 2, 9, 2, 2], 2.0000177200), (11, [1] * 6 + [2, 2, 8, 2, 2], 1.9918104778),
                      (32, [1, 1] + [2] * 14 + [4] + [2] * 14, None), (64, fam(64, 15), 2.0925893), (128, fam(128, 31), 2.1035866), (256, fam(256, 63), 2.1091153)]:
        t0 = time.time(); v, i = depth(g)
        print(f"  N={N:3d}: N^2 D = {v:.10f} (pair {i})  ref {ref}  diff {v-ref if ref else float('nan'):+.2e}  [{time.time()-t0:.1f}s]", flush=True)

# ----------------------------------------------------------------------------------------------------------
def section_unique():
    print("== unique section: the unique-1-gap ceiling theorem")
    # (a) the two elementary inequalities, proved exactly rather than on a grid
    mp.mp.dps = 30
    # cot x = 1/x - sum_{n>=1} 2 zeta(2n) x^{2n-1}/pi^{2n}; the tail from n>=2 at x=1 is bounded by its value at x=1
    tail = 2 * sum(mp.zeta(2 * n) / mp.pi ** (2 * n) for n in range(2, 200))
    closed = 2 * ((1 - mp.cot(1)) / 2 - mp.mpf(1) / 6)
    print(f"  cot x >= 1/x - x/3 - x^3/40 on (0,1]: need sum_{{n>=2}} 2 zeta(2n)/pi^(2n) <= 1/40: tail = {mp.nstr(tail,10)} = {mp.nstr(closed,10)} (closed form 1 - cot 1 - 1/3) vs 1/40 = 0.025  -> {'OK' if tail < mp.mpf(1)/40 else 'FAILS'}")
    # csc^2 y <= 1/y^2 + 1 on (0, pi/2]: csc^2 y - 1/y^2 is increasing (derivative sign) -- check max at pi/2
    print(f"  csc^2 y - 1/y^2 at pi/2 = {mp.nstr(1 - 4/mp.pi**2,8)} < 1; at 0+ = 1/3; monotone (numerically): {all(mp.csc(mp.pi/2*(i+1)/400)**2 - (400/(mp.pi/2*(i+1)))**2 >= mp.csc(mp.pi/2*i/400)**2 - (400/(mp.pi/2*i))**2 for i in range(1,400))}")
    # (b) re-solve the comparison ODE (my own code, RK45 and DOP853 cross-check)
    def tau1(N, method='DOP853'):
        c = np.cos(PI / N); smax = -np.log(c)
        G = lambda s: 2 * np.arccos(min(1.0, np.exp(s) * c))
        Sb = lambda s: 2 * PI ** 2 / (3 * G(s) ** 2) + PI / G(s)
        f = lambda s, Y: [-8 + 2 * Y[0] * (1 / 3 + Sb(s)) + Y[0] ** 2 / 80]
        ev = lambda s, Y: Y[0]; ev.terminal = True; ev.direction = -1
        sol = solve_ivp(f, (0, 0.999 * smax), [PI ** 2 / N ** 2], method=method, rtol=1e-12, atol=1e-18, events=ev)
        return N * N * sol.t_events[0][0] if len(sol.t_events[0]) else np.nan
    doc = {8: 1.9861, 9: 1.9372, 10: 1.9010, 11: 1.8732, 12: 1.8510, 16: 1.7947, 24: 1.7443, 32: 1.7209, 64: 1.6880, 128: 1.6724, 256: 1.6648, 1024: 1.6592}
    for N in [7, 8, 9, 10, 11, 12, 16, 24, 32, 64, 128, 256, 1024]:
        print(f"  N={N:5d}: tau_1 = {tau1(N):.6f} (RK45: {tau1(N,'RK45'):.6f})   doc {doc.get(N,'-')}")
    fl = lambda t, y: [-8 / PI ** 2 + y[0] / (3 * (1 - 2 * t / PI ** 2))]
    ev = lambda t, y: y[0]; ev.terminal = True; ev.direction = -1
    sol = solve_ivp(fl, (0, 4.9), [1.0], method='DOP853', rtol=1e-12, atol=1e-16, events=ev)
    print(f"  N->inf limit: {sol.t_events[0][0]:.6f} (doc 1.65737);  /pi^2 = {sol.t_events[0][0]/PI**2:.5f} (doc 0.16793)")
    # (c) is tau_1(N) < 2 for N >= 8 but > 2 for N <= 7?  (the doc needs N<=7 from enumeration)
    print(f"  tau_1(7) = {tau1(7):.4f} > 2, so N<=7 indeed needs the enumeration")
    # (d) the lattice class is tiny: one gap = 1 and N-1 gaps >= 2 summing to 2N-1 forces exactly one 3-gap, i.e. the
    #     class is the dislocation family [1, 2^a, 3, 2^b] only.  Enumerate it exactly and compare with tau_1(N).
    print("  lattice unique-1-gap class = dislocation family [1,2^a,3,2^b] only (exact statement).  Class maxima:")
    for N in [8, 12, 16, 24, 32, 64]:
        vals = []
        for a in range(0, N - 1):
            b = N - 2 - a
            if b < a: break
            g = [1] + [2] * a + [3] + [2] * b; assert sum(g) == 2 * N and len(g) == N
            vals.append((depth(g)[0], a))
        vmax = max(vals)
        print(f"    N={N:3d}: {len(vals)} configurations, max N^2D = {vmax[0]:.6f} (a={vmax[1]}), min = {min(vals)[0]:.6f};  tau_1(N) = {tau1(N):.4f}")
    # (e) the theorem is stated for ANY circle configuration with an isolated closest pair (other gaps >= 2 delta):
    #     random continuous test at N=6,8 of D <= s_1(delta), where s_1 solves the comparison ODE with this delta.
    def s1_of_delta(delta):
        c = np.cos(delta / 2); smax = -np.log(c)
        G = lambda s: 2 * np.arccos(min(1.0, np.exp(s) * c))
        Sb = lambda s: 2 * PI ** 2 / (3 * G(s) ** 2) + PI / G(s)
        f = lambda s, Y: [-8 + 2 * Y[0] * (1 / 3 + Sb(s)) + Y[0] ** 2 / 80]
        ev = lambda s, Y: Y[0]; ev.terminal = True; ev.direction = -1
        sol = solve_ivp(f, (0, 0.999 * smax), [delta ** 2], method='DOP853', rtol=1e-11, atol=1e-18, events=ev)
        return sol.t_events[0][0] if len(sol.t_events[0]) else np.nan
    rng = np.random.default_rng(3); worst = (0, None); cnt = 0
    for N in [5, 6, 8, 10]:
        for trial in range(150):
            delta = rng.uniform(0.05, 0.6)
            # other N-2 points: gaps >= 2 delta.  total remaining arc 2 pi - delta split into N-1 gaps each >= 2 delta
            free = 2 * PI - delta - 2 * delta * (N - 1)
            if free <= 0: continue
            w = rng.dirichlet(np.ones(N - 1) * rng.uniform(0.3, 3)); gaps = 2 * delta + free * w
            th = np.concatenate([[0, delta], delta + np.cumsum(gaps)[:-1]])
            D, _ = depth(None, theta=th); D /= N ** 2
            s1 = s1_of_delta(delta); ratio = D / s1; cnt += 1
            if ratio > worst[0]: worst = (ratio, (N, round(delta, 4), round(D / delta ** 2, 5), round(s1 / delta ** 2, 5)))
    print(f"  continuous isolated-pair test: {cnt} random configurations; max D/s_1(delta) = {worst[0]:.4f} at (N,delta,D/delta^2,s_1/delta^2) = {worst[1]}  -> theorem {'holds' if worst[0] < 1 else 'VIOLATED'}")
    print(f"  note: s_1(delta)/delta^2 is NOT 0.16793 at finite delta: delta=pi/8: {s1_of_delta(PI/8)/(PI/8)**2:.5f}, pi/4: {s1_of_delta(PI/4)/(PI/4)**2:.5f}, 0.05: {s1_of_delta(0.05)/0.05**2:.5f}")

# ----------------------------------------------------------------------------------------------------------
def beta_curve(gaps, pair, npts=12):
    N = len(gaps); th0 = theta_of(gaps); D, ip = depth(gaps); D /= N ** 2
    sol = solve_ivp(rhs, (0, 0.999 * D), th0, method='DOP853', rtol=1e-12, atol=1e-14, dense_output=True)
    out = []
    for t in np.linspace(0, 0.999 * N * N * D, npts):
        th = sol.sol(t / N ** 2); a, b = pair, (pair + 1) % N; g = (th[b] - th[a]) % (2 * PI)
        xb = (th[a] - th) % (2 * PI); xa = (th[b] - th) % (2 * PI); m = np.ones(N, bool); m[[a, b]] = False
        B = np.sum(1 / np.tan(xb[m] / 2) - 1 / np.tan(xa[m] / 2)); out.append((t, g * N / PI, B / (N * N * g)))
    return N * N * D, np.array(out)

def section_beta():
    print("== beta section: is beta_config(tau) <= beta_wall(tau) for the first-colliding pair?  (the 'protection lemma')")
    Dw, wall = beta_curve(fam(256, 63), 0, npts=40)
    bw = lambda t: np.interp(t, wall[:, 0], wall[:, 2])
    print(f"  wall N=256 L=130: N^2D={Dw:.6f}; beta_wall at tau=0,1,1.5,1.9,2.0: {[round(bw(t),4) for t in [0,1,1.5,1.9,2.0]]}")
    tests = {'3-block N=257 [1,1,2^127,4,2^127]': ([1, 1] + [2] * 127 + [4] + [2] * 127, 0),
             '3-block N=64 (block33)': ([1, 1] + [2] * 30 + [3, 3] + [2] * 30, 0),
             '5-block N=65 [1^4,2^k,6,2^k]': ([1] * 4 + [2] * 30 + [6] + [2] * 30, 0),
             '7-block N=65 [1^6,2^k,8,2^k]': ([1] * 6 + [2] * 29 + [8] + [2] * 29, 0),
             'N=12 winner [1^7,2,2,9,2,2]': ([1] * 7 + [2, 2, 9, 2, 2], 0),
             'dislocation N=32 [3,1,2^30]': ([3, 1] + [2] * 30, 1),
             'two 3-blocks adjacent N=64 [1,1,2,1,1,2^k,6,2^k]': ([1, 1, 2, 1, 1] + [2] * 29 + [6] + [2] * 29, 0)}
    for k, (g, p) in tests.items():
        D, c = beta_curve(g, p, npts=40)
        # the pair index reported by depth() may differ from p if the mirror pair collides; use p (symmetric anyway)
        viol = [(round(t, 3), round(b, 4), round(bw(t), 4)) for t, gg, b in c if b > bw(t) + 1e-6]
        mx = max(c[:, 2] - np.array([bw(t) for t in c[:, 0]]))
        print(f"  {k:48s}: N^2D={D:.6f}; beta at tau=0: {c[0,2]:.4f}, at 0.9*N^2D: {c[int(0.9*len(c))][2]:.4f}, at 0.999*N^2D: {c[-1,2]:.4f};  max(beta-beta_wall) = {mx:+.4f};  first violation {viol[0] if viol else None}", flush=True)

def section_cond():
    print("== cond section: the conditional theorem's comparison ODE")
    print("  From y=g^2, y' <= -8 + 2y/3 + y^2/80 + 2gB (Sec.6(iv),(v)) and B <= N^2 beta g, with Ybar = N^2 y/pi^2, tau = N^2 s:")
    print("    dYbar/dtau <= -8/pi^2 + 2 beta Ybar + (2/(3N^2)) Ybar + (pi^2/(80 N^4)) Ybar^2")
    print("  The doc states:  -8/pi^2 + 2 beta Ybar + (pi^2/(80 N^2)) Ybar^2   (no 2/(3N^2) term; N^2 instead of N^4).")
    Dw, wall = beta_curve(fam(256, 63), 0, npts=60)
    tt, bb = wall[:, 0], wall[:, 2]
    def zero_of(f, N):
        ev = lambda t, y: y[0]; ev.terminal = True; ev.direction = -1
        sol = solve_ivp(f, (0, tt[-1]), [1.0], method='DOP853', rtol=1e-12, atol=1e-15, events=ev, dense_output=True)
        return (sol.t_events[0][0] if len(sol.t_events[0]) else None), sol.y[0][-1]
    for N in [12, 64, 256]:
        f_doc = lambda t, y: [-8 / PI ** 2 + 2 * np.interp(t, tt, bb) * y[0] + PI ** 2 / (80 * N ** 2) * y[0] ** 2]
        f_cor = lambda t, y: [-8 / PI ** 2 + 2 * np.interp(t, tt, bb) * y[0] + 2 / (3 * N ** 2) * y[0] + PI ** 2 / (80 * N ** 4) * y[0] ** 2]
        zd, yd = zero_of(f_doc, N); zc, yc = zero_of(f_cor, N)
        print(f"  N={N:4d} with beta=beta_wall(N=256): Ybar(tau_end={tt[-1]:.4f}) doc-ODE {yd:.6f}, corrected {yc:.6f}; zero: doc {zd}, corrected {zc}")

# ----------------------------------------------------------------------------------------------------------
def canon_gaps(g):
    g = list(map(int, g)); N = len(g); b = None
    for h in (g, g[::-1]):
        for r in range(N):
            t = tuple(h[r:] + h[:r])
            if b is None or t < b: b = t
    return b

def section_search():
    print("== search section: independent stochastic search for anything above the run|clock|hole family")
    rng = np.random.default_rng(7)
    famval = {}
    for N in [13, 14, 15, 16, 18, 20]:
        cache = {}
        def val(g):
            c = canon_gaps(g)
            if c not in cache:
                cache[c] = depth(list(c), rtol=1e-9)[0] if not all(x == 2 for x in c) else -np.inf
            return cache[c]
        # family reference
        fv = max((val(fam(N, k)), k) for k in range(1, (N - 2) // 2 + 1))
        famval[N] = fv
        best = (-1, None); t0 = time.time()
        for restart in range(24):
            # random composition of 2N into N parts >= 1
            cuts = np.sort(rng.choice(np.arange(1, 2 * N), N - 1, replace=False))
            g = list(map(int, np.diff(np.concatenate([[0], cuts, [2 * N]]))))
            v = val(g); T = 0.03
            for st in range(400):
                g2 = list(g); mv = rng.random()
                if mv < 0.45:      # move one site: transfer a unit between ADJACENT gaps
                    i = rng.integers(N); j = (i + 1) % N
                    if rng.random() < 0.5: i, j = j, i
                    if g2[i] >= 2: g2[i] -= 1; g2[j] += 1
                    else: continue
                elif mv < 0.75:    # transfer between arbitrary gaps
                    i, j = rng.choice(N, 2, replace=False)
                    if g2[i] >= 2: g2[i] -= 1; g2[j] += 1
                    else: continue
                elif mv < 0.9:     # swap two gaps
                    i, j = rng.choice(N, 2, replace=False); g2[i], g2[j] = g2[j], g2[i]
                else:              # reverse a random segment
                    i, j = sorted(rng.choice(N + 1, 2, replace=False)); g2[i:j] = g2[i:j][::-1]
                v2 = val(g2)
                if v2 >= v or rng.random() < np.exp((v2 - v) / T): g, v = g2, v2
                if v > best[0]: best = (v, canon_gaps(g))
                T = max(0.004, T * 0.995)
        top = sorted([(v, c) for c, v in cache.items() if np.isfinite(v)], reverse=True)[:5]
        print(f"  N={N}: family best {fv[0]:.7f} (k={fv[1]}); search best {best[0]:.7f} {list(best[1])}; {len(cache)} evals [{time.time()-t0:.0f}s]")
        for v, c in top: print(f"        {v:.7f} {list(c)}")
    # full 1-move neighbourhood of the family optimum at N=32 (k=7) and N=48 (k=11): all unit transfers and swaps
    for N, k in [(32, 7), (48, 11)]:
        g0 = fam(N, k); v0 = depth(g0)[0]; best = (v0, tuple(g0)); seen = set([canon_gaps(g0)]); cnt = 0; t0 = time.time()
        for i in range(N):
            for j in range(N):
                if i == j or g0[i] < 2: continue
                g = list(g0); g[i] -= 1; g[j] += 1; c = canon_gaps(g)
                if c in seen: continue
                seen.add(c); v = depth(list(c), rtol=1e-9)[0]; cnt += 1
                if v > best[0]: best = (v, c)
        for i in range(N):
            for j in range(i + 1, N):
                if g0[i] == g0[j]: continue
                g = list(g0); g[i], g[j] = g[j], g[i]; c = canon_gaps(g)
                if c in seen: continue
                seen.add(c); v = depth(list(c), rtol=1e-9)[0]; cnt += 1
                if v > best[0]: best = (v, c)
        print(f"  N={N} k={k}: family value {v0:.7f}; best over {cnt} distinct 1-move neighbours: {best[0]:.7f} {'(the family itself)' if best[1]==tuple(g0) else list(best[1])}  [{time.time()-t0:.0f}s]", flush=True)

def section_enum13():
    fn = f"{SCR}/acue_depth_N13.npz"
    if not os.path.exists(fn): print("N=13 enumeration not finished yet"); return
    d = np.load(fn); D = d['D']; G = d['gaps']; N = 13; fin = np.isfinite(D); ND = np.where(fin, N * N * D, -np.inf)
    order = np.argsort(-ND)
    print(f"== enum13: {fin.sum()} non-clock orbits; max N^2D = {ND[order[0]]:.10f}; #>=2: {np.sum(ND>=2)}; #>=1.99: {np.sum(ND>=1.99)}")
    for r, i in enumerate(order[:12]):
        g = list(map(int, G[i])); v, p = depth(g)
        print(f"   {r+1:2d}  enum {ND[i]:.10f}  my ODE {v:.10f}  gaps {g}")
    print(f"  family value at N=13 (doc): 2.00790882 at k=3 (L=7) = [1^6,2,2,2,8,2,2,2]")

if __name__ == "__main__":
    sec = sys.argv[1]
    globals()["section_" + sec]()
