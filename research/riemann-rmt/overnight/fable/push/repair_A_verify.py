#!/usr/bin/env python3
"""repair_A_verify.py -- repairer's independent checks for push_A_threeblock_limit.md,
written after refute_A_limit_theorem.md.  Every section is self-contained; nothing here
imports the proposer's or the refuter's code.

usage: python repair_A_verify.py <section>

  models  : (2k+1)-block local models built from the parity rule (k = 1..5); first real double zero
            of q_tau = e^{-tau/4} Re/Im[e^{iu/2} P_tau(u + i tau)] by zero tracking + mp 2-D Newton.
            Settles E1: the deliverable's "9-block" polynomial is the 11-block; the 9-block is
            (u^2-pi^2)(u^2-9pi^2) sin(u/2) with tau* = 2.05736.
  fold    : Prop. 7.3 fold constants -r_{tau*}(u*)/q_uu for the 7-, 9- and 11-block, psi from the exact
            far factors of the symmetric (N odd) compensation.
  tilt    : block4even: series of phi_N (sign of the tilt term), the eps^2 constant C_2(2) = -4pi/3, the
            corrected cusp bookkeeping (incl. the cancellation of the two eps^{7/3} corrections), and the
            middle-root trajectory at N = 64.  Settles E2.
  asym    : block4even tau_N = N^2 D_N to 15 digits for N = 16..2048 as a 2-D root (Q = Q_x = 0) in mpmath
            with the closed-form coefficients of Lemma 2.3; "first collision" by zero counting on a tau grid.
  blocks  : 7-, 9-, 11-block (N odd, symmetric compensation) at N = 33, 65, 129 (257 for the 7-block): tau_N
            as a 2-D root with exact coefficients from polynomial division in mpmath; "first" verified by an
            mp zero count (no double-precision cancellation).
  enumtol : why the enumeration's block4odd N = 11 value is 6e-7 low (np.roots resolves a triple-zero cluster
            only to eps_mach^{1/3}).
  prop61  : explicit sign change of a_N(tau) on [0, 3] for every N >= 13 (block4odd) / N >= 14 (block33):
            repairs the proviso of Prop. 6.1 without appealing to Theorem 5.4.
  tail    : the outer-tail bound of Prop. 3.4: 8 N^3 e^{-(N-2pi)^2/12} <= N^{-2} holds for N >= 21, not N >= 8.
"""
import sys, time
import numpy as np
import mpmath as mp
import sympy as sp

PI = np.pi
u, tau, w = sp.symbols('u tau w', real=True)

# ----------------------------------------------------------------------------------------------------
# local models
# ----------------------------------------------------------------------------------------------------
def block_model(k):
    """(2k+1)-block centred at u = 0 (sites -k..k occupied, then gaps of 2): q_0 = p(u) L(u/2).
    The lattice beyond the block has the parity of k: k even -> even multiples of pi -> L = sin,
    p has the odd sites +-1, +-3, ..., +-(k-1) as roots; k odd -> L = cos, p has 0, +-2, ..., +-(k-1)."""
    if k % 2 == 0:
        L = 'sin'; p = sp.Integer(1)
        for j in range(1, k, 2): p *= (u**2 - (j*sp.pi)**2)
    else:
        L = 'cos'; p = u
        for j in range(2, k, 2): p *= (u**2 - (j*sp.pi)**2)
    return sp.expand(p), L

def heat_poly(p):
    """P_tau(w) = e^{tau d^2} p = sum_n tau^n p^{(2n)}(w)/n!"""
    P = 0; d = p.subs(u, w); n = 0
    while d != 0:
        P += tau**n*d/sp.factorial(n); d = sp.diff(d, w, 2); n += 1
    return sp.expand(P)

def q_closed(p, L):
    """Prop. 7.1: e^{tau d^2}[p L] = e^{-tau/4} Re/Im[e^{iu/2} P_tau(u + i tau)]."""
    P = heat_poly(p)
    z = sp.expand(P.subs(w, u + sp.I*tau))
    e = sp.expand((sp.exp(sp.I*u/2)*z).rewrite(sp.cos))
    q = sp.re(e) if L == 'cos' else sp.im(e)
    return sp.simplify(sp.exp(-tau/4)*q)

def zeros_on_grid(f, t, lo, hi, M):
    us = np.linspace(lo, hi, M+1); v = f(us, t)
    idx = np.where(v[:-1]*v[1:] < 0)[0]; zs = []
    for i in idx:
        a, b = us[i], us[i+1]; fa = v[i]
        for _ in range(60):
            m = 0.5*(a+b); fm = f(m, t)
            if np.sign(fm) == np.sign(fa): a, fa = m, fm
            else: b = m
        zs.append(0.5*(a+b))
    return np.array(zs)

def first_double_zero(k, dtau=0.001, tmax=2.6, M=8000, verbose=True):
    p, L = block_model(k); q = q_closed(p, L)
    qu = sp.diff(q, u); quu = sp.diff(q, u, 2)
    f = sp.lambdify((u, tau), q, 'numpy'); fu = sp.lambdify((u, tau), qu, 'numpy')
    fm = sp.lambdify((u, tau), q, 'mpmath'); fum = sp.lambdify((u, tau), qu, 'mpmath'); fuum = sp.lambdify((u, tau), quu, 'mpmath')
    R = (k+5)*PI; lo = 1e-9
    z0 = zeros_on_grid(f, 1e-9, lo, R, M); n0 = len(z0)
    if verbose:
        print(f"  k={k} ({2*k+1}-block): p = {p}, L = {L}(u/2); zeros in (0,{k+5}pi) at tau=0+: {np.round(z0/PI, 4)} pi  (n0={n0})")
    prev, tprev = z0, 0.0; t = dtau; res = None
    while t <= tmax:
        zs = zeros_on_grid(f, t, lo, R, M)
        # a zero can also disappear by reaching u = 0 (triple zero at the centre); the grid starts at 1e-9
        if len(zs) < n0:
            g = np.diff(np.concatenate([[0.0], prev])); i = int(np.argmin(g))
            if i == 0:   # merge with the centre: triple zero at 0, tau from q_u(0, tau) = 0
                s0 = mp.findroot(lambda s: fum(mp.mpf(0), s), (mp.mpf(tprev), mp.mpf(t)), solver='bisect')
                res = (mp.mpf(0), s0, mp.mpf(0), 'triple zero at u=0', prev)
            else:
                um = 0.5*(prev[i-1]+prev[i])
                sol = mp.findroot(lambda x, s: [fm(x, s), fum(x, s)], (mp.mpf(um), mp.mpf(0.5*(tprev+t))))
                x, s = sol[0], sol[1]
                res = (x, s, fuum(x, s), f"pair started at ({prev[i-1]/PI:.3f}pi,{prev[i]/PI:.3f}pi) at tau={tprev:.3f}", prev)
            break
        prev, tprev = zs, t; t += dtau
    if res is None:
        print("     no merge found"); return None
    x, s, c, how, prev = res
    if verbose:
        print(f"     FIRST real double zero: u* = {mp.nstr(x, 12)} = {mp.nstr(x/mp.pi, 6)} pi,  tau* = {mp.nstr(s, 12)},  q_uu = {mp.nstr(c, 8)}   [{how}]")
        print(f"     zeros just before ({tprev:.3f}): {np.round(prev/PI, 4)} pi")
    return x, s, c

def sec_models():
    print("== MODELS: (2k+1)-block local models from the parity rule")
    out = {}
    for k in range(1, 6):
        out[k] = first_double_zero(k)
    print("   deliverable: 3-block 2, 5-block 2, 7-block 2.03812605359, '9-block' 2.0689 (polynomial u(u^2-4pi^2)(u^2-16pi^2)cos -> that is k=5)")
    print("   refuter    : 9-block (u^2-pi^2)(u^2-9pi^2) sin: 2.0573579730 at u*=2.8285pi; 11-block 2.0688935596 at 3.7754pi")
    return out

# ----------------------------------------------------------------------------------------------------
# Prop 7.3 fold constants
# ----------------------------------------------------------------------------------------------------
def Phi_N_symbolic(k, Nsym):
    """exact q_0^N/L for the (2k+1)-block with symmetric compensation (N odd): (2N)^k * prod(added)/prod(removed),
    a = u/2N, b = pi/2N.  Added midpoints at offsets j of the non-lattice parity, |j| <= k-1; removed lattice sites at
    offsets N + j (same j) from the block centre."""
    a = u/(2*Nsym); b = sp.pi/(2*Nsym)
    num = sp.Integer(1); den = sp.Integer(1)
    if k % 2 == 0:
        for j in range(1, k, 2): num *= (sp.sin(a)**2 - sp.sin(j*b)**2); den *= (sp.cos(a)**2 - sp.sin(j*b)**2)
    else:
        num *= sp.sin(a); den *= sp.cos(a)
        for j in range(2, k, 2): num *= (sp.sin(a)**2 - sp.sin(j*b)**2); den *= (sp.cos(a)**2 - sp.sin(j*b)**2)
    return (2*Nsym)**k*num/den

def sec_fold(folds=None):
    print("== FOLD: Prop. 7.3 constants -r_{tau*}(u*)/q_uu(u*,tau*) with psi = N^2-coefficient of the exact Phi_N")
    eps = sp.symbols('epsilon', positive=True)
    mp.mp.dps = 25
    if folds is None:
        folds = {}
        for k in (3, 4, 5):
            x, s, c = first_double_zero(k, verbose=False); folds[k] = (x, s)
    for k in (3, 4, 5):
        p, L = block_model(k)
        Phi = Phi_N_symbolic(k, 1/eps)
        ser = sp.expand(sp.series(Phi, eps, 0, 3).removeO())
        c0 = sp.expand(ser.coeff(eps, 0) - p); c1 = sp.expand(ser.coeff(eps, 1)); psi = sp.expand(ser.coeff(eps, 2))
        assert c0 == 0 and c1 == 0, (k, c0, c1)
        r = q_closed(psi, L); q = q_closed(p, L); quu = sp.diff(q, u, 2)
        us, ts = folds[k]
        rv = sp.N(r.subs({u: sp.Float(str(us), 25), tau: sp.Float(str(ts), 25)}), 15)
        qv = sp.N(quu.subs({u: sp.Float(str(us), 25), tau: sp.Float(str(ts), 25)}), 15)
        print(f"  {2*k+1}-block: psi(u) = {psi}")
        print(f"           (u*,tau*) = ({mp.nstr(us,10)}, {mp.nstr(ts,12)})  r_tau*(u*) = {rv}  q_uu = {qv}  =>  N^2(tau_N - tau*) -> {sp.N(-rv/qv, 10)}")
    print("   deliverable (7-block): -4.1540;  refuter finite-N 9-block: N^2(tau_N-2.05736) = -5.98, -5.73, -5.66 at N=33,65,129")

# ----------------------------------------------------------------------------------------------------
# block4even: tilt sign, eps^2 constant, cusp bookkeeping, trajectory
# ----------------------------------------------------------------------------------------------------
def coeffs_block4even(N):
    """Lemma 2.3: a_N = 1, a_0 = -omega, a_j = -(1+conj(omega)) (-1)^j e^{i pi (j+1)/N}, omega = e^{i pi/N}."""
    wv = mp.exp(1j*mp.pi/N); wb = mp.conj(wv)
    a = [mp.mpc(0)]*(N+1); a[N] = mp.mpc(1); a[0] = -wv
    for j in range(1, N): a[j] = -(1+wb)*(-1)**j*mp.exp(1j*mp.pi*(j+1)/N)
    return a

def kappa_block4even(N):
    # root set: odd sites (sum theta = pi N) + angle 0 - angle (pi - pi/N)  ->  sum theta = pi N - pi + pi/N
    return (2j)**(-N)*mp.exp(-1j*(mp.pi*N - mp.pi + mp.pi/N)/2)

class FlowB4E:
    """Q(x,s) = Re[kappa sum_j a_j e^{s j(N-j)} e^{i(j-N/2)x}] for block4even, double and mp versions."""
    def __init__(self, N, dps=30):
        mp.mp.dps = dps; self.N = N
        self.a_mp = coeffs_block4even(N); self.kap = kappa_block4even(N)*mp.mpf(2)**N     # the positive factor 2^-N is dropped: it would underflow double precision at N >= 512
        self.a = np.array([complex(z) for z in self.a_mp]); self.k = complex(self.kap)
        j = np.arange(N+1); self.m = j - N/2; self.w = (j*(N-j)).astype(float)
        self.m_mp = [mp.mpf(j) - mp.mpf(N)/2 for j in range(N+1)]; self.w_mp = [mp.mpf(j*(N-j)) for j in range(N+1)]
    def Q(self, x, s, d=0):
        x = np.atleast_1d(x)
        ph = np.exp(np.outer(x, 1j*self.m))*(self.a*np.exp(s*self.w))
        if d == 1: ph = ph*(1j*self.m)
        if d == 2: ph = ph*(-(self.m**2))
        return np.real(self.k*ph.sum(axis=1))
    def Qim(self, x, s):
        ph = np.exp(np.outer(np.atleast_1d(x), 1j*self.m))*(self.a*np.exp(s*self.w))
        return np.imag(self.k*ph.sum(axis=1))
    def zeros(self, s, xlo, xhi, M):
        xs = np.linspace(xlo, xhi, M+1) + 0.2371*(xhi-xlo)/M; v = self.Q(xs, s)      # offset: the exact root at x=0 never sits on a grid point
        idx = np.where(v[:-1]*v[1:] < 0)[0]; zs = []
        for i in idx:
            a, b = xs[i], xs[i+1]; fa = v[i]
            for _ in range(60):
                m = 0.5*(a+b); fm = self.Q(m, s)[0]
                if np.sign(fm) == np.sign(fa): a, fa = m, fm
                else: b = m
            zs.append(0.5*(a+b))
        return np.array(zs)
    def all_mp(self, x, s):
        N = self.N; z = mp.exp(1j*x); zp = mp.exp(-1j*mp.mpf(N)/2*x)   # e^{i(j-N/2)x} = zp * z^j
        Q = Qx = Qxx = Qs = Qxs = mp.mpc(0)
        for j in range(N+1):
            E = self.a_mp[j]*mp.exp(s*self.w_mp[j])*zp
            m = self.m_mp[j]; wj = self.w_mp[j]
            Q += E; Qx += 1j*m*E; Qxx += -m*m*E; Qs += wj*E; Qxs += 1j*m*wj*E
            zp *= z
        k = self.kap
        return [mp.re(k*v) for v in (Q, Qx, Qxx, Qs, Qxs)] + [abs(mp.im(k*Q))]

def newton_fold(F, x, s, dps):
    N = F.N; capx = mp.pi/N; caps = mp.mpf('0.1')/N**2          # damped: a step never exceeds a lattice gap in x or 0.1 in tau
    for it in range(120):
        Q, Qx, Qxx, Qs, Qxs, Im = F.all_mp(x, s)
        det = Qx*Qxs - Qs*Qxx
        dx = -( Qxs*Q - Qs*Qx)/det; ds = -(-Qxx*Q + Qx*Qx)/det
        if abs(dx) > capx: dx = capx*mp.sign(dx)
        if abs(ds) > caps: ds = caps*mp.sign(ds)
        x += dx; s += ds
        if abs(dx) < mp.mpf(10)**(-dps+8) and abs(ds)/abs(s) < mp.mpf(10)**(-dps+8): break
    return x, s, F.all_mp(x, s)

def sec_tilt():
    print("== TILT: block4even, phi_N(v) = 2N sin(a) cos(b)/cos(a+b), a = v/2N, b = pi/2N")
    eps = sp.symbols('epsilon', positive=True); v = sp.symbols('v', real=True)
    a = v*eps/2; b = sp.pi*eps/2
    phi = 2/eps*sp.sin(a)*sp.cos(b)/sp.cos(a+b)
    ser = sp.expand(sp.series(phi, eps, 0, 5).removeO())
    c2 = sp.expand(ser.coeff(eps, 2)); c4 = sp.expand(ser.coeff(eps, 4))
    print(f"   phi_N = v + ({c2})/N^2 + ({c4})/N^4 + O(N^-6)      [deliverable had v^3/12 - pi v^2/4: wrong sign of the tilt]")
    for N in (100, 1000):
        for vv in (1.0, 2.0):
            ph = 2*N*np.sin(vv/2/N)*np.cos(PI/2/N)/np.cos((vv+PI)/2/N)
            print(f"   numeric N={N}: N^2(phi_N({vv}) - v - v^3/12N^2) = {N*N*(ph - vv - vv**3/12/N**2):+.5f}   vs +pi v^2/4 = {PI*vv**2/4:.5f}")
    # constant term of e^{tau/4} q^N_tau(0): even powers v^{2n} cos(v/2) -> M_{2n}(tau) = (-1)^n e^{tau/4} d^{2n}/dt^{2n} e^{-tau t^2} |_{t=1/2}
    t = sp.symbols('t', real=True)
    def M(n):
        return sp.simplify((-1)**n*sp.exp(tau/4)*sp.diff(sp.exp(-tau*t**2), t, 2*n).subs(t, sp.Rational(1, 2)))
    C1 = sp.simplify(c2.coeff(v, 2)*M(1))
    C2 = sp.simplify(c4.coeff(v, 4)*M(2) + c4.coeff(v, 2)*M(1))
    print(f"   e^(tau/4) q^N_tau(0) = eps*C1(tau) + eps^2*C2(tau) + ...,  C1 = {sp.factor(C1)},  C2 = {sp.factor(C2)}")
    print(f"   C1(2-sigma) = {sp.expand(C1.subs(tau, 2-sp.symbols('sigma')))},   C2(2) = {sp.nsimplify(C2.subs(tau, 2))} = {float(C2.subs(tau, 2)):.6f}   [refuter: -4pi/3 = {-4*PI/3:.6f}]")
    # u^2 coefficient of the even perturbation at tau = 2 (B = eps*beta2)
    r_even = q_closed(c2.coeff(v, 2)*u**2, 'cos')
    beta2 = sp.simplify((sp.exp(tau/4)*r_even).series(u, 0, 3).removeO().coeff(u, 2).subs(tau, 2))
    print(f"   u^2 coefficient of e^(tau/4) r~_tau at tau=2: beta_2 = {beta2}  (= -pi/4)")
    # cusp bookkeeping
    A_c = (sp.Rational(9, 16)*(2*sp.pi/3)**2)**sp.Rational(1, 3)
    print(f"   fold of A u - u^3/12 + C: A^3 = (9/16) C^2;  with C(sigma_c) = (pi/2)(4/3) eps^2 - (4pi/3) eps^2 = -(2pi/3) eps^2:")
    print(f"   A_c = (pi^2/4)^(1/3) eps^(4/3) = {float(A_c):.6f} eps^(4/3);  tau_N = 2 - (4/3) eps - 2 A_c = 2 - 4/(3N^2) - {2*float(A_c):.6f} N^(-8/3)")
    print(f"   eps^(7/3) corrections at the fold: 4 A B = 4 A (-pi/4 eps) = -pi eps A ;  delta C = (pi/2) eps delta, delta = 2A  -> +pi eps A : they cancel,")
    print(f"   so the scaled residual should converge at rate N^(-4/3) (refuter observed a factor 2.53 per doubling; 2^(4/3) = {2**(4/3):.3f}).")
    # numerical trajectory at N = 64
    N = 64; F = FlowB4E(N, dps=30)
    tauN = None
    # 2-D root
    x0 = 0.0083/N; s0 = 1.99963/N**2
    x, s, vals = newton_fold(F, mp.mpf(x0), mp.mpf(s0), 30)
    tauN = float(s*N**2)
    print(f"   N=64: tau_N = {tauN:.12f}, u* = {float(x)*N:+.6f}   (refuter: 1.99963282131129, u* = +0.00832)")
    norm = N**3/F.Q(0.0, 0.0, d=1)[0]          # N^2 q^N_tau(0) = N^3 e^{-tau/4} Q_s(0)/Q_0'(0)  (phi_N'(0) = 1 normalisation)
    for tt in (1.99, 1.995, 1.999, 1.9995, 1.9996, 1.99963, tauN - 1e-6):
        sg = tt/N**2
        val = norm*np.exp(-tt/4)*F.Q(0.0, sg)[0]/N**2; zs = F.zeros(sg, -0.3/N, 0.3/N, 6000)*N
        sigma = 2 - tt
        pred = np.exp(-tt/4)*((PI/4)*tt*sigma - (4*PI/3)/N**2)     # N^2 q(0) to O(eps^2)
        print(f"     tau={tt:.7f}: N^2 q_tau^N(0) = {N*N*val:+.6f}  (corrected leading terms {pred:+.6f}; deliverable's -(pi/2) e^(-tau/4) sigma = {-np.exp(-tt/4)*(PI/2)*sigma:+.6f})   zeros in |u|<0.3: {np.round(zs, 4)}")

# ----------------------------------------------------------------------------------------------------
# block4even tau_N high precision
# ----------------------------------------------------------------------------------------------------
def depth_block4even(N, dps=30, dtau_verify=None, verbose=True):
    t0 = time.time(); F = FlowB4E(N, dps=dps)
    win = (-4*PI/N, 4*PI/N); M = 4000
    cnt = lambda t: len(F.zeros(t/N**2, win[0], win[1], M))
    n0 = cnt(0.0); assert n0 == 5, n0
    lo, hi = 1.5, 2.2
    assert cnt(lo) == 5 and cnt(hi) == 3, (cnt(lo), cnt(hi))
    for _ in range(28):
        mid = 0.5*(lo+hi)
        if cnt(mid) == 5: lo = mid
        else: hi = mid
    zs = F.zeros(lo/N**2, win[0], win[1], 4*M); g = np.diff(zs); i = int(np.argmin(g)); xm = 0.5*(zs[i]+zs[i+1])
    x, s, vals = newton_fold(F, mp.mpf(xm), mp.mpf(0.5*(lo+hi))/N**2, dps)
    if abs(float(s)*N**2 - 0.5*(lo+hi)) > 1e-3:      # fallback seed from the cusp asymptotics u* ~ 2 (pi^2/4)^(1/6) N^(-4/3)
        x, s, vals = newton_fold(F, mp.mpf(2*(PI**2/4)**(1/6)*N**(-4/3))/N, mp.mpf(lo)/N**2, dps)
    Q, Qx, Qxx, Qs, Qxs, Im = vals
    tauN = s*N**2; tf = float(tauN)
    # first-collision check: count stays 5 on a tau grid up to tau_N - 1e-4, is 3 at tau_N + 1e-4
    step = dtau_verify or (0.005 if N <= 512 else 0.02)
    grid = list(np.arange(1.0, tf - 1e-4, step)) + [tf - 1e-4]
    bad = [t for t in grid if cnt(t) != 5]
    after = cnt(tf + 1e-4)
    c1 = (2 - tauN)*N**2; resid = (c1 - mp.mpf(4)/3)*mp.mpf(N)**(mp.mpf(2)/3)
    ok = (not bad) and after == 3
    if verbose:
        print(f"   N={N:5d}  tau_N = {mp.nstr(tauN, 15)}  u* = {mp.nstr(x*N, 6)}  |Q|+|Qx| = {mp.nstr(abs(Q)+abs(Qx), 2)}  |Im Q| = {mp.nstr(Im, 2)}"
              f"  N^2(2-tau) = {mp.nstr(c1, 10)}  (N^2(2-tau)-4/3) N^(2/3) = {mp.nstr(resid, 7)}"
              f"  first-collision: {'verified' if ok else 'NOT verified'} (grid step {step}, drops at earlier tau: {bad[:3]}, count after = {after})  [{time.time()-t0:.0f}s]", flush=True)
    return float(tauN), float(resid), ok

def sec_asym(Ns=(16, 32, 64, 128, 192, 256, 512, 1024, 2048)):
    print("== ASYM: block4even tau_N as a 2-D root (Q = Q_x = 0), closed-form coefficients, mpmath 30 digits")
    rows = []
    for N in Ns:
        rows.append((N,) + depth_block4even(N))
    print(f"   predicted limit of the scaled residual: 2 (pi^2/4)^(1/3) = {2*(PI**2/4)**(1/3):.6f}")
    print("   deliverable's heat_depth.py values: 16:1.993008041801 32:1.998429050189 64:1.999632821246 128:1.999912099912 192:1.999961627887 256:1.999978634911")
    print("   refuter's values: 256:1.99997863054997 512:1.99999475255446 1024:1.99999870305884 2048:1.99999967811276 4096:1.99999991989788")
    prev = None
    for N, t, r, ok in rows:
        d = r - 2*(PI**2/4)**(1/3)
        print(f"   N={N:5d}  residual - limit = {d:+.6f}" + (f"  ratio to previous = {prev/d:.3f}" if prev and d != 0 else ""))
        prev = d

# ----------------------------------------------------------------------------------------------------
# multi-midpoint blocks at finite N: exact coefficients by polynomial division
# ----------------------------------------------------------------------------------------------------
def block_sites(k, N):
    """gap list [1]^{2k} + [2]^m + [2k+2] + [2]^{N-2k-1-m}, m = (N-2k-1)/2 (N odd): sites in Z/2N."""
    assert N % 2 == 1
    m = (N - 2*k - 1)//2
    g = [1]*(2*k) + [2]*m + [2*k+2] + [2]*(N - 2*k - 1 - m)
    assert len(g) == N and sum(g) == 2*N
    sites = np.concatenate([[0], np.cumsum(g)[:-1]]).astype(int)
    return g, sites

def poly_mul_linear(c, r):
    """c(z) * (z - r)"""
    new = [mp.mpc(0)]*(len(c)+1)
    for i, ci in enumerate(c):
        new[i] -= r*ci; new[i+1] += ci
    return new

def poly_div_linear(c, r):
    """c(z)/(z - r), c(r) = 0 (synthetic division); returns quotient and |remainder|"""
    d = len(c) - 1; q = [mp.mpc(0)]*d
    q[d-1] = c[d]
    for i in range(d-1, 0, -1):
        q[i-1] = c[i] + r*q[i]
    rem = c[0] + r*q[0]
    return q, abs(rem)

class FlowBlock:
    """(2k+1)-block with symmetric compensation, N odd.  P(z) = (z^N - 1) prod_{j=1..k}(z - e^{i pi(2j-1)/N}) / prod_{j=1..k}(z + e^{i pi(2j-1)/N}).
    Q(x,s) = Re[kappa sum a_j e^{s j(N-j)} e^{i(j-N/2)x}], kappa = (2i)^{-N} e^{-i pi (N-1-k)/2}; block centre at x = k pi/N."""
    def __init__(self, k, N, dps=50):
        mp.mp.dps = dps; self.N = N; self.k = k
        g, sites = block_sites(k, N)
        # sanity: the site set is (even sites) + {1,3,..,2k-1} - {N+1,..,N+2k-1}
        ev = set(range(0, 2*N, 2)); S = (ev | set(range(1, 2*k, 2))) - set(range(N+1, N+2*k, 2))
        assert S == set(sites.tolist()), "site bookkeeping"
        c = [mp.mpc(0)]*(N+1); c[0] = mp.mpc(-1); c[N] = mp.mpc(1)
        for j in range(1, k+1): c = poly_mul_linear(c, mp.exp(1j*mp.pi*(2*j-1)/N))
        self.rem = 0
        for j in range(1, k+1):
            c, rem = poly_div_linear(c, -mp.exp(1j*mp.pi*(2*j-1)/N)); self.rem = max(self.rem, rem)
        assert len(c) == N+1
        self.a_mp = c
        self.kap = (2j)**(-N)*mp.exp(-1j*mp.pi*(N-1-k)/2)
        self.m_mp = [mp.mpf(j) - mp.mpf(N)/2 for j in range(N+1)]; self.w_mp = [mp.mpf(j*(N-j)) for j in range(N+1)]
        self.xc = k*PI/N
        self.maxcoef = max(abs(z) for z in c)
    def Q_mp(self, x, s):
        N = self.N; z = mp.exp(1j*x); zp = mp.exp(-1j*mp.mpf(N)/2*x); Q = mp.mpc(0)
        for j in range(N+1):
            Q += self.a_mp[j]*mp.exp(s*self.w_mp[j])*zp; zp *= z
        return mp.re(self.kap*Q)
    def Q_grid_mp(self, xs, s):
        # precompute e^{s w_j} a_j once
        N = self.N; A = [self.a_mp[j]*mp.exp(s*self.w_mp[j]) for j in range(N+1)]
        out = []
        for x in xs:
            z = mp.exp(1j*x); zp = mp.exp(-1j*mp.mpf(N)/2*x); Q = mp.mpc(0)
            for j in range(N+1):
                Q += A[j]*zp; zp *= z
            out.append(mp.re(self.kap*Q))
        return out
    def count_mp(self, s, xlo, xhi, M):
        h = (mp.mpf(xhi)-mp.mpf(xlo))/M
        xs = [mp.mpf(xlo) + h*i + mp.mpf('0.2371')*h for i in range(M+1)]
        v = self.Q_grid_mp(xs, s)
        return sum(1 for i in range(M) if v[i]*v[i+1] < 0)
    def all_mp(self, x, s):
        N = self.N; z = mp.exp(1j*x); zp = mp.exp(-1j*mp.mpf(N)/2*x)
        Q = Qx = Qxx = Qs = Qxs = mp.mpc(0)
        for j in range(N+1):
            E = self.a_mp[j]*mp.exp(s*self.w_mp[j])*zp; m = self.m_mp[j]; wj = self.w_mp[j]
            Q += E; Qx += 1j*m*E; Qxx += -m*m*E; Qs += wj*E; Qxs += 1j*m*wj*E; zp *= z
        k = self.kap
        return [mp.re(k*v) for v in (Q, Qx, Qxx, Qs, Qxs)] + [abs(mp.im(k*Q))]

def depth_block(k, N, seed, dps=None, verbose=True, per_site=24, dtau_verify=0.05):
    """seed = (u*, tau*) of the local model (+ fold correction if known)."""
    t0 = time.time(); dps = dps or (40 + N//8)
    F = FlowBlock(k, N, dps=dps)
    us, ts = seed
    x = mp.mpf(F.xc) + mp.mpf(us)/N; s = mp.mpf(ts)/N**2
    x, s, vals = newton_fold(F, x, s, dps)
    Q, Qx, Qxx, Qs, Qxs, Im = vals
    tauN = s*N**2; tf = float(tauN); ustar = float((x - F.xc)*N)
    # verification by mp zero count in the window centre +- (k+5)pi/N: n0 = 2k+5 zeros initially, mirror folds -> 2k+1
    R = (k+5)*PI/N; xlo, xhi = F.xc - R, F.xc + R; M = per_site*(2*k+10)
    n0 = F.count_mp(mp.mpf(0), xlo, xhi, M); assert n0 == 2*k+5, (n0, 2*k+5)
    def cnt_fine(t):
        # coarse count on the window, offset grid (the centre root never sits on a grid point); the two fold
        # neighbourhoods (u* and -u*) are replaced by fine counts on grid-aligned sub-windows, so that the coarse
        # intervals and the fine windows partition the window exactly
        s_ = mp.mpf(t)/N**2
        h = (mp.mpf(xhi)-mp.mpf(xlo))/M
        xs = [mp.mpf(xlo) + h*i + mp.mpf('0.2371')*h for i in range(M+1)]
        v = F.Q_grid_mp(xs, s_)
        wins = []
        for uf in (ustar, -ustar):
            xf = F.xc + uf/N
            ia = max(0, int((xf - 0.5*PI/N - float(xs[0]))/float(h))); ib = min(M, int((xf + 0.5*PI/N - float(xs[0]))/float(h)) + 1)
            if any(not (ib <= a0 or ia >= b0) for (a0, b0) in wins):      # overlapping windows: merge
                a0, b0 = wins.pop(); ia, ib = min(ia, a0), max(ib, b0)
            wins.append((ia, ib))
        tot = sum(1 for i in range(M) if not any(a0 <= i < b0 for (a0, b0) in wins) and v[i]*v[i+1] < 0)
        for (a0, b0) in wins:
            tot += F.count_mp(s_, xs[a0], xs[b0], 1500)
        return tot
    grid = list(np.arange(1.0, tf - 1e-3, dtau_verify)) + [tf - 1e-3, tf - 1e-4]
    bad = [t for t in grid if cnt_fine(t) != n0]
    after = cnt_fine(tf + 1e-4)
    ok = (not bad) and after < n0
    if verbose:
        print(f"   {2*k+1}-block N={N:4d}  tau_N = {mp.nstr(tauN, 14)}  u* = {ustar:+.6f} ({ustar/PI:+.5f} pi)  |Q|+|Qx| = {mp.nstr(abs(Q)+abs(Qx), 2)}  |Im Q| = {mp.nstr(Im, 2)}"
              f"  Qxx = {mp.nstr(Qxx, 4)}  max|a_j| = {mp.nstr(F.maxcoef, 3)}  division remainder = {mp.nstr(F.rem, 2)}"
              f"  zeros in window: {n0} until tau_N-1e-4, {after} at tau_N+1e-4; earlier drops: {bad[:3]}  -> {'FIRST collision verified' if ok else 'NOT verified'}  [{time.time()-t0:.0f}s]", flush=True)
    return tf, ustar, ok

def sec_blocks(which=None):
    print("== BLOCKS: finite-N (2k+1)-blocks, symmetric compensation, exact coefficients by polynomial division")
    models = {3: (5.9643126848125, 2.03812605359085, -4.1540), 4: (8.8860856, 2.0573579730, -5.6), 5: (11.8606259, 2.0688935596, -7.0)}
    plan = {3: (33, 65, 129, 257), 4: (33, 65, 129), 5: (33, 65, 129)}
    if which: plan = {k: plan[k] for k in which}
    for k, Ns in plan.items():
        us, ts, cf = models[k]
        print(f"  {2*k+1}-block: local model tau* = {ts}, u* = {us}")
        for N in Ns:
            tf, u_, ok = depth_block(k, N, (us, ts + cf/N**2))
            print(f"        N={N:4d}  N^2 D_N = {tf:.12f}   N^2(tau_N - tau*) = {(tf-ts)*N**2:+.4f}", flush=True)
    print("   robust solver (deliverable): 7-block 33:2.034196338652 65:2.037135310173 129:2.037870579847; 9-block 33:2.051868514973 65:2.056003799438 129:2.056533203125")
    print("   refuter fold solver: 7-block 33:2.034196345071 65:2.037135368679 129:2.037875950822 257:2.038063131044; 9-block 33:2.051868526544 65:2.056002600008 129:2.057017582093; 11-block 33:2.061688836107 65:2.067164398563")

# ----------------------------------------------------------------------------------------------------
# enumeration tolerance at a triple zero
# ----------------------------------------------------------------------------------------------------
def sec_enumtol():
    print("== ENUMTOL: block4odd N=11, np.roots-based off-circle indicator near the (triple-zero) collision")
    N = 11
    mp.mp.dps = 30
    F = lambda t: N*mp.exp(-t/4) - 2*sum((-1)**j*j*mp.exp(-t*(j-mp.mpf(N)/2)**2/N**2) for j in range(1, N))
    tau = mp.findroot(F, (mp.mpf('1.9'), mp.mpf('2.0')), solver='bisect'); D = tau/N**2
    print(f"   exact: tau_N = {mp.nstr(tau, 12)}  (first zero of F_N)")
    # the enumeration's canonical representative of the orbit (gaps [1,1,2,2,2,2,4,2,2,2,2] from site 0); np.roots'
    # accuracy at a near-triple root depends on the rotation, so use exactly the representative the file used
    try:
        d = np.load('acue_depth_N11.npz'); gaps = d['gaps']; Dfile = d['D']
        def canon(g):
            g = list(g); return min(tuple(g[r:]+g[:r]) for r in range(len(g)))
        idx = [i for i, g in enumerate(gaps) if canon(g.tolist()) == canon([1,1]+[2]*4+[4]+[2]*4)][0]
        sites = np.concatenate([[0], np.cumsum(gaps[idx])[:-1]]).astype(int); print(f"   enumeration orbit {idx}: sites {sites.tolist()}, stored N^2D = {N*N*Dfile[idx]:.10f}")
    except Exception as e:
        print("   (npz not found, using sites from the gap list)", e); sites = np.array([0,1,2,4,6,8,10,14,16,18,20])
    theta = 2*PI*sites/(2*N)
    assert len(theta) == N
    a = np.poly(np.exp(1j*theta)); powers = np.arange(N, -1, -1); wgt = powers*(N-powers)
    def off(s):
        r = np.roots(a*np.exp(s*wgt)); return np.max(np.abs(np.abs(r) - 1))
    for m in (3, 4, 5, 6, 7, 8, 9, 10, 12):
        s = float(D)*(1 - 10.0**(-m)); print(f"   s = D(1 - 1e-{m:2d}): max||r|-1| = {off(s):.2e}   (enumeration flags 'off circle' when > 1e-7)")
    # the enumeration's bisection
    lo, hi = 0.0, 4.0/N**2
    while off(hi) < 1e-7: hi *= 2
    for _ in range(60):
        mid = 0.5*(lo+hi)
        if off(mid) > 1e-7: hi = mid
        else: lo = mid
        if hi-lo < 1e-13*max(1, hi): break
    print(f"   enumeration-style bisection: N^2 D = {N*N*0.5*(lo+hi):.10f}  vs exact {mp.nstr(tau, 10)}  diff = {N*N*0.5*(lo+hi)-float(tau):+.2e}   (enumeration file: 1.9888690636)")
    print("   the three roots near angle 0 collide as a triple zero; numpy resolves a triple cluster only to ~eps_mach^(1/3) ~ 1e-5 in |r|,")
    print("   so the 1e-7 threshold fires while the cluster is still open: the enumeration value is a lower bound, low by O(N^4 * 1e-10).")

# ----------------------------------------------------------------------------------------------------
# Prop 6.1 proviso: explicit sign change of a_N on [0,3]
# ----------------------------------------------------------------------------------------------------
def sec_prop61():
    print("== PROP61: a_N(3) < 0 for all N >= 13 (block4odd) / N >= 14 (block33) by an explicit bound; a_N(0) = 1")
    mp.mp.dps = 30
    sig = mp.sqrt(6)                       # V ~ N(0, 2 tau) at tau = 3
    lead = -3*mp.exp(-mp.mpf(3)/4)         # E[V^2 cos(V/2)] = (2tau - tau^2) e^{-tau/4} at tau = 3
    phi = lambda t: mp.exp(-t*t/2)/mp.sqrt(2*mp.pi)
    E_abs = lambda Nn: 2*sig*phi(Nn/sig)                                  # E[|V| 1_{|V|>N}]
    E_sq = lambda Nn: 2*(sig*Nn*phi(Nn/sig) + 6*mp.ncdf(-Nn/sig))          # E[V^2 1_{|V|>N}]
    # constants: |tan a - a| <= (4/9)|a|^3 on |a| <= 1/2  (ratio increasing, = 0.3704 at a = 1/2)
    aa = np.linspace(1e-4, 0.5, 20000); rat = (np.tan(aa) - aa)/aa**3
    print(f"   max_{{|a|<=1/2}} (tan a - a)/a^3 = {rat.max():.4f} <= 4/9 = {4/9:.4f}  ->  |phi_N(v) - v| <= |v|^3/(9 N^2) on |v| <= N (block4odd)")
    # block33: |phi_N(v) - v| <= c33 |v|^3/N^2 with c33 = (5/12)/(cos^2(1/2) - sin^2(pi/28)) for N >= 14
    c33 = (5/12)/(np.cos(0.5)**2 - np.sin(PI/28)**2)
    worst = 0
    for Nn in (14, 16, 20, 30, 50, 100):
        vv = np.linspace(1e-3, Nn, 20000); a_ = vv/(2*Nn); b_ = PI/(2*Nn)
        ph = Nn*np.sin(vv/Nn)*np.cos(b_)**2/(np.cos(a_)**2 - np.sin(b_)**2)
        worst = max(worst, np.max(np.abs(ph - vv)*Nn**2/vv**3))
    print(f"   block33: numerical max_N,v N^2|phi_N(v)-v|/|v|^3 = {worst:.4f} <= c33 = {c33:.4f} (analytic bound for N >= 14)")
    print(f"   leading term E[V^2 cos(V/2)] at tau=3: {mp.nstr(lead, 8)}")
    print("   block4odd (N odd): 6 a_N(3) exact | bound 12/N^2 + E[|V|(2N^2+|V|); |V|>N] | first zero of a_N")
    for N in (13, 15, 17, 21, 25, 31, 41, 61):
        aN = lambda t: N*mp.exp(-t/4) - 2*sum((-1)**j*j*mp.exp(-t*(j-mp.mpf(N)/2)**2/N**2) for j in range(1, N))
        val = 6*aN(mp.mpf(3)); bound = mp.mpf(12)/N**2 + 2*N**2*E_abs(N) + E_sq(N)
        z = mp.findroot(aN, (mp.mpf('1.5'), mp.mpf('2.5')), solver='bisect')
        print(f"      N={N:3d}: 6a_N(3) = {mp.nstr(val, 8)}  |6a_N(3) - lead| = {mp.nstr(abs(val-lead), 3)} <= bound {mp.nstr(bound, 4)};  lead + bound = {mp.nstr(lead+bound, 5)} < 0 {'OK' if lead+bound < 0 else 'FAIL'};  a_N(0) = {mp.nstr(aN(0), 6)};  first zero tau = {mp.nstr(z, 10)}")
    print("   block33 (N even): 6 a_N(3) exact | bound c33*108/N^2 + E[|V|(N^3+|V|); |V|>N]")
    for N in (14, 16, 20, 24, 32, 40, 64):
        c = mp.cos(mp.pi/N); s_ = mp.sin(mp.pi/N)
        r = [(-1)**kk*mp.sin((kk+1)*mp.pi/N)/s_ for kk in range(N-1)] + [mp.mpf(0), mp.mpf(0)]
        a = [(r[j-2] if j >= 2 else 0) - r[j] for j in range(N+1)]
        norm = sum(j*a[j] for j in range(N+1))
        aN = lambda t: sum(j*a[j]*mp.exp(-t*(j-mp.mpf(N)/2)**2/N**2) for j in range(N+1))/norm
        val = 6*aN(mp.mpf(3)); bound = mp.mpf(c33)*108/N**2 + N**3*E_abs(N) + E_sq(N)
        z = mp.findroot(aN, (mp.mpf('1.5'), mp.mpf('2.5')), solver='bisect')
        print(f"      N={N:3d}: 6a_N(3) = {mp.nstr(val, 8)}  |6a_N(3) - lead| = {mp.nstr(abs(val-lead), 3)} <= bound {mp.nstr(bound, 4)};  lead + bound = {mp.nstr(lead+bound, 5)} < 0 {'OK' if lead+bound < 0 else 'FAIL'};  a_N(0) = {mp.nstr(aN(0), 6)};  first zero tau = {mp.nstr(z, 10)}")
    print("   since 12/N^2, c33*108/N^2 and the Gaussian tails decrease in N, the bound holds for every larger N as well.")

def sec_tail():
    print("== TAIL: Prop 3.4 outer bound 8 N^3 exp(-(N-2pi)^2/12) vs N^-2")
    for N in (8, 12, 16, 20, 21, 22, 30):
        b = 8*N**3*np.exp(-(N-2*PI)**2/12)
        print(f"   N={N:3d}: 8N^3 e^(-(N-2pi)^2/12) = {b:.3e}   N^-2 = {1/N**2:.3e}   {'<=' if b <= 1/N**2 else '>'}")

if __name__ == "__main__":
    sec = sys.argv[1] if len(sys.argv) > 1 else 'models'
    if sec == 'models': sec_models()
    elif sec == 'fold': sec_fold()
    elif sec == 'tilt': sec_tilt()
    elif sec == 'asym': sec_asym(Ns=tuple(int(x) for x in sys.argv[2:]) or (16, 32, 64, 128, 192, 256, 512, 1024, 2048))
    elif sec == 'blocks': sec_blocks(which=tuple(int(x) for x in sys.argv[2:]) or None)
    elif sec == 'enumtol': sec_enumtol()
    elif sec == 'prop61': sec_prop61()
    elif sec == 'tail': sec_tail()
    else: raise SystemExit("unknown section")
