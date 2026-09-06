"""Independent checks for push_A_threeblock_limit.md (refuter, task A_limit_theorem).

Sections (run: python refute_A_limit_theorem.py <section> [args]):
  sym     : high-precision tau_N for the symmetric families (block4odd, block33) from an independent
            implementation (coefficients from the closed forms, verified against numpy.poly; the first zero
            of Q_s'(0) found by bracketing + mp bisection, NOT anderson); checks c1=-4/3, c2, F1's N=384 value.
  asym    : block4even: the first double zero of Q_s found as a genuine 2-D root (Q=Q_x=0) in mpmath, seeded
            by a double-precision zero-count scan; scaled residual (N^2(2-tau)-4/3) N^{2/3} up to N=2048.
  models  : local midpoint-insertion models q_tau = e^{-tau/4} Re/Im[e^{iu/2} P_tau(u+i tau)]: track all real
            zeros on a fine tau grid, report the first tau at which two real zeros merge, which pair merges,
            and where.  Includes the TRUE 9-block (u^2-pi^2)(u^2-9pi^2) sin(u/2) and the 11-block
            u(u^2-4pi^2)(u^2-16pi^2) cos(u/2) (which the deliverable calls the "9-block").
  roots   : fully independent depth via numpy.roots + bisection on the off-circle indicator (the enumeration's
            method) for block7 / block9 / block5 / two3 / block4even at small N; compare with heat_depth.py,
            heat_depth_robust.py and the local models.
  prop71  : numerical check of the midpoint-insertion closed form (Prop 7.1) against a direct Gaussian
            convolution quadrature.
  all     : everything except the slow parts.
"""
import sys, time
import numpy as np
import mpmath as mp

PI = np.pi

# ----------------------------------------------------------------------------------------------------
# configurations (gap patterns in units pi/N; site 0 at angle 0)
# ----------------------------------------------------------------------------------------------------
def gaps(name, N):
    if name == 'block4odd':
        assert N % 2 == 1; k = (N-3)//2; return [1,1]+[2]*k+[4]+[2]*(N-3-k)
    if name == 'block4even':
        assert N % 2 == 0; k = (N-4)//2; return [1,1]+[2]*k+[4]+[2]*(N-3-k)
    if name == 'block33':
        assert N % 2 == 0; k = (N-4)//2; return [1,1]+[2]*k+[3,3]+[2]*(N-4-k)
    if name == 'block5':
        k = (N-5)//2; return [1,1,1,1]+[2]*k+[6]+[2]*(N-5-k)
    if name == 'two3':
        k = (N-6)//2; return [1,1,2,1,1]+[2]*k+[6]+[2]*(N-6-k)
    if name == 'block7':
        k = (N-7)//2; return [1]*6+[2]*k+[8]+[2]*(N-7-k)
    if name == 'block9':
        k = (N-9)//2; return [1]*8+[2]*k+[10]+[2]*(N-9-k)
    if name == 'block11':
        k = (N-11)//2; return [1]*10+[2]*k+[12]+[2]*(N-11-k)
    raise ValueError(name)

def theta_from_gaps(g):
    N = len(g); assert sum(g) == 2*N and len(g) == N
    sites = np.concatenate([[0], np.cumsum(g)[:-1]]); return 2*PI*sites/(2*N)

# ----------------------------------------------------------------------------------------------------
# exact coefficients (Lemma 2.3) in mpmath, and their check against numpy.poly
# ----------------------------------------------------------------------------------------------------
def coeffs_mp(name, N):
    """a_0..a_N of P(z) for the root set with the added root at angle 0 (block centred at 0)."""
    if name == 'block4odd':
        a = [-2*(-1)**j for j in range(N+1)]; a[0] = -1; a[N] = 1
        return [mp.mpc(x) for x in a]
    if name == 'block33':
        s = mp.sin(mp.pi/N)
        r = [(-1)**k*mp.sin((k+1)*mp.pi/N)/s for k in range(N-1)] + [mp.mpf(0), mp.mpf(0)]
        return [mp.mpc((r[j-2] if j >= 2 else 0) - r[j]) for j in range(N+1)]
    if name == 'block4even':
        w = mp.exp(1j*mp.pi/N); wb = mp.conj(w)
        a = [mp.mpc(0)]*(N+1); a[N] = mp.mpc(1); a[0] = -w
        for j in range(1, N):
            a[j] = -(1+wb)*(-1)**j*mp.exp(1j*mp.pi*(j+1)/N)
        return a
    raise ValueError

def check_coeffs(name, N):
    th = theta_from_gaps(gaps(name, N)) - PI/N          # rotate so that the added root (site 1) sits at angle 0
    a_np = np.poly(np.exp(1j*th))[::-1]
    a_mp = np.array([complex(x) for x in coeffs_mp(name, N)])
    return np.max(np.abs(a_np - a_mp))

class FlowMP:
    """Q_s(x) = Re[kappa * sum_j a_j e^{s j(N-j)} e^{i(j-N/2)x}], real for real x; derivatives in x and s."""
    def __init__(self, name, N, dps=40):
        mp.mp.dps = dps
        self.N = N; self.a = coeffs_mp(name, N)
        self.m = [mp.mpf(j) - mp.mpf(N)/2 for j in range(N+1)]
        self.w = [mp.mpf(j*(N-j)) for j in range(N+1)]
        # kappa: make Q real. kappa = (2i)^{-N} e^{-i sum theta/2}; sum theta computed from the gap list.
        th = theta_from_gaps(gaps(name, N)) - PI/N
        # exact sum of angles as a rational multiple of pi/N: sites*2pi/(2N) - pi/N
        sites = np.concatenate([[0], np.cumsum(gaps(name, N))[:-1]])
        sum_units = int(sites.sum()) - N            # sum theta = sum_units * pi/N
        self.kappa = (2j)**(-N) * mp.exp(-1j*mp.pi*sum_units/(2*N))
    def terms(self, x, s):
        return [self.a[j]*mp.exp(s*self.w[j] + 1j*self.m[j]*x) for j in range(self.N+1)]
    def all(self, x, s):
        E = self.terms(x, s); k = self.kappa
        Q   = k*sum(E)
        Qx  = k*sum(1j*self.m[j]*E[j] for j in range(self.N+1))
        Qxx = k*sum(-self.m[j]**2*E[j] for j in range(self.N+1))
        Qs  = k*sum(self.w[j]*E[j] for j in range(self.N+1))
        Qxs = k*sum(1j*self.m[j]*self.w[j]*E[j] for j in range(self.N+1))
        return Q, Qx, Qxx, Qs, Qxs
    def Qx0(self, s):
        """Q_s'(0) (the symmetric families: Q odd, so this is the triple-zero indicator)."""
        k = self.kappa
        return mp.re(k*sum(1j*self.m[j]*self.a[j]*mp.exp(s*self.w[j]) for j in range(self.N+1)))

# ----------------------------------------------------------------------------------------------------
# double precision Fourier evaluation (for scans)
# ----------------------------------------------------------------------------------------------------
class FlowNP:
    def __init__(self, theta):
        theta = np.sort(np.asarray(theta) % (2*PI)); N = len(theta); self.N = N
        a = np.poly(np.exp(1j*theta))[::-1]          # a_0..a_N
        j = np.arange(N+1); self.m = j - N/2; self.w = j*(N-j); self.a = a
        self.kappa = (2j)**(-N)*np.exp(-1j*theta.sum()/2)
    def Q(self, x, s, d=0):
        x = np.atleast_1d(x)
        ph = np.exp(np.outer(x, 1j*self.m))*(self.a*np.exp(s*self.w))
        if d == 1: ph = ph*(1j*self.m)
        if d == 2: ph = ph*(-(self.m**2))
        return np.real(self.kappa*ph.sum(axis=1))
    def zeros(self, s, xlo, xhi, M=4000):
        xs = np.linspace(xlo, xhi, M+1); v = self.Q(xs, s)
        idx = np.where(v[:-1]*v[1:] < 0)[0]; zs = []
        for i in idx:
            a, b = xs[i], xs[i+1]; fa = v[i]
            for _ in range(60):
                mm = 0.5*(a+b); fm = self.Q(mm, s)[0]
                if np.sign(fm) == np.sign(fa): a, fa = mm, fm
                else: b = mm
            zs.append(0.5*(a+b))
        return np.array(zs)

# ====================================================================================================
def sec_sym(Ns_odd=(17, 33, 65, 129, 257, 513), Ns_even=(16, 32, 64, 128, 256, 384, 512), dps=40):
    print("== SYM: symmetric families, independent high-precision first zero of Q_s'(0)")
    for name, N in [('block4odd', 9), ('block4odd', 17), ('block33', 8), ('block33', 16), ('block4even', 8), ('block4even', 16)]:
        print(f"   coefficient check {name:10s} N={N:3d}: max|a_np - a_closed| = {check_coeffs(name, N):.2e}")
    for name, Ns in [('block4odd', Ns_odd), ('block33', Ns_even)]:
        print(" ", name)
        for N in Ns:
            t0 = time.time(); F = FlowMP(name, N, dps=dps)
            f = lambda tau: F.Qx0(tau/mp.mpf(N)**2)
            f0 = f(mp.mpf(0)); t = mp.mpf('1.5'); h = mp.mpf('0.1')
            assert mp.sign(f(t)) == mp.sign(f0), "unexpected sign at tau=1.5"
            while mp.sign(f(t)) == mp.sign(f0): t += h
            lo, hi = t-h, t
            for _ in range(140):
                mid = (lo+hi)/2
                if mp.sign(f(mid)) == mp.sign(f0): lo = mid
                else: hi = mid
            tau = (lo+hi)/2
            c1 = (tau-2)*N**2; c2 = (c1 + mp.mpf(4)/3)*N**2
            print(f"    N={N:4d}  tau_N={mp.nstr(tau,16)}  N^2(tau-2)={mp.nstr(c1,10)}  N^4(tau-2+4/3N^2)={mp.nstr(c2,9)}   [{time.time()-t0:.1f}s]", flush=True)
    print("   predicted c2: block4odd -8/5 = -1.6 ; block33 -8/5-pi^2 =", -1.6-PI**2)
    print("   F1 quoted block33 N=128: 1.999918565579, N=256: 1.999979605684, N=384: 1.999990889523")

# ====================================================================================================
def sec_asym(Ns=(16, 32, 64, 128, 256, 512, 1024, 2048), dps=40, verbose=True):
    print("== ASYM: block4even, first double zero as a 2-D root (Q=Q_x=0) in mpmath")
    rows = []
    for N in Ns:
        t0 = time.time()
        th = theta_from_gaps(gaps('block4even', N)) - PI/N
        Fd = FlowNP(th)
        # double-precision scan: count zeros of Q_s in u in (-2pi, 2pi) (x in (-2pi/N, 2pi/N)) for s near 2/N^2
        def count(tau):
            return len(Fd.zeros(tau/N**2, -2*PI/N, 2*PI/N, M=2000))
        lo, hi = 1.6, 2.2
        assert count(lo) == 3 and count(hi) == 1, (count(lo), count(hi))
        for _ in range(30):
            mid = 0.5*(lo+hi)
            if count(mid) == 3: lo = mid
            else: hi = mid
        zs = Fd.zeros(lo/N**2, -2*PI/N, 2*PI/N, M=4000)
        g = np.diff(zs); i = int(np.argmin(g)); xm = 0.5*(zs[i]+zs[i+1])
        tau_scan = 0.5*(lo+hi)
        # mp Newton on (Q, Q_x) in (x, s)
        F = FlowMP('block4even', N, dps=dps)
        x = mp.mpf(xm); s = mp.mpf(tau_scan)/N**2
        for it in range(60):
            Q, Qx, Qxx, Qs, Qxs = F.all(x, s)
            Q, Qx, Qxx, Qs, Qxs = [mp.re(v) for v in (Q, Qx, Qxx, Qs, Qxs)]
            det = Qx*Qxs - Qs*Qxx
            dx = -( Qxs*Q - Qs*Qx)/det
            ds = -(-Qxx*Q + Qx*Qx)/det
            x += dx; s += ds
            if abs(dx) < mp.mpf(10)**(-dps+8) and abs(ds)/s < mp.mpf(10)**(-dps+8): break
        Q, Qx, Qxx, Qs, Qxs = F.all(x, s)
        # sanity: imaginary parts vanish (Q real), residuals tiny, Q_xx != 0 (a fold, not a triple zero)
        imag = max(abs(mp.im(Q)), abs(mp.im(Qx)))
        tau = s*N**2
        c1 = (2-tau)*N**2; resid = (c1 - mp.mpf(4)/3)*mp.mpf(N)**(mp.mpf(2)/3)
        rows.append((N, tau, c1, resid))
        print(f"   N={N:5d}  tau_N={mp.nstr(tau,15)}  u*={mp.nstr(x*N,8)}  Q_xx*N^{-3}={mp.nstr(mp.re(Qxx)/N**3,4)}  |res|={mp.nstr(abs(Q)+abs(Qx),3)}  |Im|={mp.nstr(imag,3)}"
              f"  N^2(2-tau)={mp.nstr(c1,10)}  (N^2(2-tau)-4/3)N^(2/3)={mp.nstr(resid,8)}  scan tau={tau_scan:.6f}  [{time.time()-t0:.1f}s]", flush=True)
    print("   deliverable (heat_depth.py) N^2D: 16:1.993008041801 32:1.998429050189 64:1.999632821246 128:1.999912099912 192:1.999961627887 256:1.999978634911")
    print("   deliverable predicted limit of the scaled residual: 2*(pi^2/4)^(1/3) =", 2*(PI**2/4)**(1/3))
    return rows

# ====================================================================================================
# local models
# ====================================================================================================
def model_q(name):
    """returns (q(u,tau), q_u, q_uu, q_tau) as numpy-callables, from Prop 7.1 (heat-evolved polynomial)."""
    import sympy as sp
    u, tau, w = sp.symbols('u tau w', real=True)
    models = {
        'three':  (u, 'cos'),
        'five':   (u**2 - sp.pi**2, 'sin'),
        'two3':   (u**2 - 4*sp.pi**2, 'cos'),
        'seven':  (u*(u**2 - 4*sp.pi**2), 'cos'),
        'nine_true':   ((u**2 - sp.pi**2)*(u**2 - 9*sp.pi**2), 'sin'),
        'eleven': (u*(u**2 - 4*sp.pi**2)*(u**2 - 16*sp.pi**2), 'cos'),
        'two3b':  (u**2 - 9*sp.pi**2, 'sin'),
    }
    p, lat = models[name]
    P = 0; d = p.subs(u, w); k = 0
    while d != 0:
        P += tau**k*d/sp.factorial(k); d = sp.diff(d, w, 2); k += 1
    z = sp.expand(P.subs(w, u + sp.I*tau))
    e = sp.expand((sp.exp(sp.I*u/2)*z).rewrite(sp.cos))
    q = sp.exp(-tau/4)*(sp.re(e) if lat == 'cos' else sp.im(e))
    q = sp.simplify(q)
    fs = [sp.lambdify((u, tau), ex, 'numpy') for ex in (q, sp.diff(q, u), sp.diff(q, u, 2), sp.diff(q, tau))]
    return fs, sp.simplify(q*sp.exp(tau/4)), p, lat

def zeros_of(f, t, R, M=6000):
    us = np.linspace(1e-9, R, M+1); v = f(us, t)
    idx = np.where(v[:-1]*v[1:] < 0)[0]; zs = []
    for i in idx:
        a, b = us[i], us[i+1]; fa = v[i]
        for _ in range(60):
            mm = 0.5*(a+b); fm = f(mm, t)
            if np.sign(fm) == np.sign(fa): a, fa = mm, fm
            else: b = mm
        zs.append(0.5*(a+b))
    return np.array(zs)

def sec_models(names=('five', 'two3', 'seven', 'nine_true', 'eleven', 'two3b'), R=None, dtau=0.002, tmax=3.0):
    from scipy.optimize import fsolve
    print("== MODELS: local midpoint-insertion models, first merging of real zeros on (0,R]")
    for name in names:
        (f, fu, fuu, ft), qexpr, p, lat = model_q(name)
        Rr = R or 5*PI
        z_prev = zeros_of(f, 0.0 + 1e-9, Rr); n0 = len(z_prev)
        print(f"  {name:10s} p={p}, L={lat}(u/2);  zeros in (0,{Rr/PI:.0f}pi) at tau=0+: {np.round(z_prev/PI,4)} (units pi)")
        t = dtau; found = None; traj = []
        while t <= tmax:
            zs = zeros_of(f, t, Rr)
            traj.append((t, zs.copy()))
            if len(zs) < len(z_prev):
                # which pair vanished: the adjacent pair of z_prev with the smallest gap
                g = np.diff(z_prev); i = int(np.argmin(g))
                um = 0.5*(z_prev[i]+z_prev[i+1])
                sol, info, ier, msg = fsolve(lambda v: [f(v[0], v[1]), fu(v[0], v[1])], [um, t-dtau/2], full_output=True)
                found = (sol[0], sol[1], fuu(sol[0], sol[1]), i, z_prev, t-dtau)
                break
            # triple zero at 0 for odd models: q_u(0,tau) changes sign
            if fu(0.0, t)*fu(0.0, max(t-dtau, 1e-9)) < 0:
                s0 = fsolve(lambda v: fu(0.0, v[0]), [t-dtau/2])[0]
                found = (0.0, s0, 0.0, -1, z_prev, t-dtau); break
            z_prev = zs; t += dtau
        if found is None:
            print(f"     no merging of real zeros found for tau <= {tmax}"); continue
        us, ts, quu, i, zp, tp = found
        # identify the pair by tracing zeros back to tau=0 (nearest-neighbour continuation)
        # crude: report the two zeros just before the merge and their positions at tau=0 by continuation
        def trace_back(idx_pair):
            pos = [zp[idx_pair[0]], zp[idx_pair[1]]]
            for (tt, zz) in reversed(traj[:-1]):
                pos = [zz[np.argmin(np.abs(zz-pp))] for pp in pos]
            z00 = zeros_of(f, 1e-9, Rr)
            return [z00[np.argmin(np.abs(z00-pp))] for pp in pos]
        if i >= 0:
            orig = trace_back((i, i+1))
            print(f"     FIRST double zero: u*={us:.10f} ({us/PI:.5f} pi)  tau*={ts:.10f}  q_uu={quu:.6f};"
                  f"  merging pair started at u = {orig[0]/PI:.3f}pi, {orig[1]/PI:.3f}pi; zeros just before: {np.round(zp/PI,4)} pi")
        else:
            print(f"     FIRST double zero: triple zero at u=0, tau*={ts:.10f}")
        # also report q_tau(pi) style sanity for five/two3
    print("   deliverable claims: five tau*=2 at u=pi; two3 tau*=2 at u=2pi; seven tau*=2.03812605359 at u*=5.9643;"
          " 'nine' (=u(u^2-4pi^2)(u^2-16pi^2)cos) tau*=2.0689")

# ====================================================================================================
# independent depth: numpy.roots + bisection on the off-circle indicator (the enumeration's method)
# ====================================================================================================
def depth_roots(g, tol_off=1e-7):
    N = len(g); theta = theta_from_gaps(g); z = np.exp(1j*theta); a = np.poly(z)
    powers = np.arange(N, -1, -1); w = powers*(N-powers)
    def off(s):
        r = np.roots(a*np.exp(s*w)); return np.max(np.abs(np.abs(r)-1))
    lo, hi = 0.0, 1.5/N**2
    while off(hi) < tol_off: hi *= 1.3
    for _ in range(80):
        mid = 0.5*(lo+hi)
        if off(mid) > tol_off: hi = mid
        else: lo = mid
        if hi-lo < 1e-14*hi: break
    return 0.5*(lo+hi)

def sec_roots():
    print("== ROOTS: numpy.roots-based depth (independent of the heat solvers)")
    table = {
        'block7':  [16, 17, 24, 25, 32, 33, 48],
        'block9':  [17, 25, 33, 41, 49],
        'block11': [21, 25, 33, 41, 49],
        'block5':  [17, 25, 33, 49],
        'two3':    [16, 24, 32, 48],
        'block4even': [16, 24, 32, 48, 64],
        'block33': [16, 32, 64],
    }
    for name, Ns in table.items():
        print(" ", name)
        for N in Ns:
            try: g = gaps(name, N)
            except AssertionError: continue
            t0 = time.time(); D = depth_roots(g)
            print(f"    N={N:3d}  N^2D={N*N*D:.9f}   [{time.time()-t0:.1f}s]", flush=True)
    print("   deliverable: heat_depth.py block7: 16:1.7754 32:1.8271; robust: 16:2.017715 24:2.030167 32:2.033841 33:2.034196 48:2.036279;")
    print("   robust block9: 33:2.051869 65:2.056004 129:2.056533;  local 'nine'(=11-block) tau*=2.0689, 7-block 2.0381")

# ====================================================================================================
def sec_prop71():
    print("== PROP 7.1: closed form vs direct Gaussian convolution quadrature")
    from scipy.integrate import quad
    import sympy as sp
    for name in ['five', 'seven', 'nine_true']:
        (f, fu, fuu, ft), qexpr, p, lat = model_q(name)
        pf = sp.lambdify(sp.Symbol('u', real=True), p, 'numpy')
        L = (lambda v: np.cos(v/2)) if lat == 'cos' else (lambda v: np.sin(v/2))
        worst = 0
        for (uu, tt) in [(0.7, 0.5), (3.0, 2.0), (6.0, 2.5), (9.5, 1.3)]:
            G = lambda v: np.exp(-(uu-v)**2/(4*tt))/np.sqrt(4*PI*tt)*pf(v)*L(v)
            val, err = quad(G, uu-40*np.sqrt(tt), uu+40*np.sqrt(tt), limit=400)
            worst = max(worst, abs(val - f(uu, tt)))
        print(f"   {name:10s}: max |closed form - quadrature| = {worst:.2e}")


# ====================================================================================================
# generic high-precision fold solver for any gap pattern (exact coefficients, double scan + mp 2-D Newton)
# ====================================================================================================
def sites_of(g):
    return np.concatenate([[0], np.cumsum(g)[:-1]]).astype(int)

def coeffs_product_mp(g, dps=None):
    """monic coefficients a_0..a_N of prod (z - e^{i pi k/N}) over the sites k of the gap list g, by mp product."""
    N = len(g); sites = sites_of(g)
    dps = dps or int(60 + 0.25*N)
    mp.mp.dps = dps
    # interleave the multiplication order (even/odd sites alternately) to limit intermediate coefficient growth
    order = sorted(range(N), key=lambda i: (sites[i] % 2, sites[i]))
    poly = [mp.mpc(1)]
    for i in order:
        r = mp.exp(1j*mp.pi*int(sites[i])/N)
        new = [mp.mpc(0)]*(len(poly)+1)
        for k, c in enumerate(poly):
            new[k]   -= r*c
            new[k+1] += c
        poly = new
    sum_units = int(sites.sum())          # sum theta = sum_units * pi/N
    return poly, sum_units

class FlowGeneric:
    """Q(x,s) = Re[kappa_phase * sum_j a_j e^{s j(N-j)} e^{i(j-N/2)x}] (real up to the positive factor 2^N)."""
    def __init__(self, g, closed=None, dps=None):
        N = len(g); self.N = N; self.g = g
        if closed is not None:
            mp.mp.dps = dps or 40
            self.a_mp = coeffs_mp(closed, N)
            # closed forms are for the block centred at 0 (rotation by -pi/N of the gap-list sites)
            self.sum_units = int(sites_of(g).sum()) - N
            self.rot = -PI/N
        else:
            self.a_mp, self.sum_units = coeffs_product_mp(g, dps)
            self.rot = 0.0
        self.kappa = (1j)**(-N) * mp.exp(-1j*mp.pi*self.sum_units/(2*N))
        self.m_mp = [mp.mpf(j) - mp.mpf(N)/2 for j in range(N+1)]
        self.w_mp = [mp.mpf(j*(N-j)) for j in range(N+1)]
        # double precision copies
        self.a = np.array([complex(x) for x in self.a_mp]); self.k = complex(self.kappa)
        j = np.arange(N+1); self.m = j - N/2; self.w = (j*(N-j)).astype(float)
    # --- double precision ---
    def Q(self, x, s):
        x = np.atleast_1d(x)
        ph = np.exp(np.outer(x, 1j*self.m))*(self.a*np.exp(s*self.w))
        return np.real(self.k*ph.sum(axis=1))
    def zeros(self, s, xlo, xhi, M):
        xs = np.linspace(xlo, xhi, M+1) + 0.2371*(xhi-xlo)/M; v = self.Q(xs, s)     # offset grid: never hits a lattice root exactly
        idx = np.where(v[:-1]*v[1:] < 0)[0]; zs = []
        for i in idx:
            a, b = xs[i], xs[i+1]; fa = v[i]
            for _ in range(50):
                mm = 0.5*(a+b); fm = self.Q(mm, s)[0]
                if np.sign(fm) == np.sign(fa): a, fa = mm, fm
                else: b = mm
            zs.append(0.5*(a+b))
        return np.array(zs)
    # --- mp ---
    def all(self, x, s):
        N = self.N; k = self.kappa
        E = [self.a_mp[j]*mp.exp(s*self.w_mp[j] + 1j*self.m_mp[j]*x) for j in range(N+1)]
        Q   = mp.re(k*sum(E))
        Qx  = mp.re(k*sum(1j*self.m_mp[j]*E[j] for j in range(N+1)))
        Qxx = mp.re(k*sum(-self.m_mp[j]**2*E[j] for j in range(N+1)))
        Qs  = mp.re(k*sum(self.w_mp[j]*E[j] for j in range(N+1)))
        Qxs = mp.re(k*sum(1j*self.m_mp[j]*self.w_mp[j]*E[j] for j in range(N+1)))
        Im  = abs(mp.im(k*sum(E)))
        return Q, Qx, Qxx, Qs, Qxs, Im

def depth_fold(name, N, closed=None, tau_lo=1.0, tau_hi=2.6, verbose=True, per_site=40, dtau_verify=2e-3):
    """first collision time tau_N = N^2 D_N: (1) double-precision zero-count scan in a window around the block
       (block sites 0..nb-1 plus two lattice neighbours on each side) and bisection in tau on the count drop
       (this bracket can be EARLY when the merging pair is closer than the grid spacing); (2) mp Newton on
       (Q, Q_x) = 0 seeded by the closest pair; (3) verification: on the tau grid [tau_lo, tau_N - 1e-4] the
       zero count (coarse grid + fine local grid near the fold) stays at its initial value, and drops at tau_N+1e-4."""
    t0 = time.time(); g = gaps(name, N); F = FlowGeneric(g, closed=closed)
    nb = len([x for x in g if x == 1]) + 1
    xlo = F.rot + (-5.5)*PI/N; xhi = F.rot + (nb-1+5.5)*PI/N
    M = int(per_site*(nb+11))
    n0 = len(F.zeros(0.0, xlo, xhi, M)); assert n0 == nb+4, (n0, nb)
    cnt = lambda tau: len(F.zeros(tau/N**2, xlo, xhi, M))
    assert cnt(tau_lo) == n0, ("count at tau_lo", cnt(tau_lo), n0)
    assert cnt(tau_hi) < n0, ("no drop by tau_hi", cnt(tau_hi), n0)
    lo, hi = tau_lo, tau_hi
    for _ in range(22):
        mid = 0.5*(lo+hi)
        if cnt(mid) == n0: lo = mid
        else: hi = mid
    zs = F.zeros(lo/N**2, xlo, xhi, 4*M)
    gp = np.diff(zs); i = int(np.argmin(gp)); xm = 0.5*(zs[i]+zs[i+1])
    x = mp.mpf(xm); s = mp.mpf(0.5*(lo+hi))/N**2
    for it in range(80):
        Q, Qx, Qxx, Qs, Qxs, Im = F.all(x, s)
        det = Qx*Qxs - Qs*Qxx
        dx = -( Qxs*Q - Qs*Qx)/det; ds = -(-Qxx*Q + Qx*Qx)/det
        x += dx; s += ds
        if abs(dx) < mp.mpf(10)**(-mp.mp.dps+10) and abs(ds)/s < mp.mpf(10)**(-mp.mp.dps+10): break
    Q, Qx, Qxx, Qs, Qxs, Im = F.all(x, s)
    tau = float(s*N**2); xs_ = float(x)
    # --- verification of "first" ---
    xc = F.rot + (nb-1)*PI/(2*N)                     # block centre; mirror pairs collide simultaneously for symmetric N
    def cnt_fine(t):
        zc = F.zeros(t/N**2, xlo, xhi, M); tot = 0
        for xf in {xs_, 2*xc - xs_}:
            a, b = xf - 0.5*PI/N, xf + 0.5*PI/N
            if abs(xf - xs_) > 1e-12 and abs((2*xc - xs_) - xs_) < 1.0*PI/N:   # overlapping windows: handled by the first
                continue
            zf = F.zeros(t/N**2, a, b, 8000)
            zc = zc[(zc < a) | (zc > b)]; tot += len(zf)
        return len(zc) + tot
    bad = [t for t in np.arange(tau_lo, tau - 1e-4, dtau_verify) if cnt_fine(t) != n0]
    c_before = cnt_fine(tau - 1e-4); c_after = cnt_fine(tau + 1e-4)
    scale = max(abs(float(F.Q(np.linspace(xlo, xhi, 200), float(s)).max())), 1e-300)
    ustar = (xs_ - F.rot - (nb-1)*PI/(2*N))*N
    ok = (not bad) and c_before == n0 and c_after < n0
    if verbose:
        print(f"   {name:10s} N={N:5d}  tau_N={mp.nstr(s*N**2,15)}  u*(rel. centre)={ustar:.5f} ({ustar/PI:.4f} pi)"
              f"  counts: before={c_before} after={c_after} (n0={n0}, earlier-drop taus: {bad[:3]}) -> {'FIRST collision verified' if ok else 'NOT VERIFIED'}"
              f"  |Q|+|Qx|={mp.nstr(abs(Q)+abs(Qx),2)} (scale {scale:.1e})  Qxx/scale={mp.nstr(Qxx/scale,3)}  |Im|={mp.nstr(Im,2)}  scan bracket=[{lo:.6f},{hi:.6f}]  [{time.time()-t0:.1f}s]", flush=True)
    return tau, ustar

def sec_asym2(Ns=(16, 32, 64, 128, 256, 512, 1024, 2048), dtau_verify=2e-3):
    print("== ASYM2: block4even (exact closed-form coefficients), first double zero as a 2-D root", f"(verification tau-grid step {dtau_verify})")
    for N in Ns:
        tau, us = depth_fold('block4even', N, closed='block4even', dtau_verify=dtau_verify)
        c1 = (2-tau)*N**2; resid = (c1-4/3)*N**(2/3)
        print(f"        N={N:5d}  N^2(2-tau)={c1:.9f}   (N^2(2-tau)-4/3)N^(2/3)={resid:.6f}", flush=True)
    print("   deliverable predicted limit of the scaled residual: 2*(pi^2/4)^(1/3) =", 2*(PI**2/4)**(1/3))

def sec_blocks(which=('block7', 'block9', 'block5', 'two3', 'block11')):
    print("== BLOCKS: multi-midpoint families, first collision by the generic fold solver (mp product coefficients)")
    pred = {'block7': (2.03812605359, -4.153958), 'block9': (2.0573579730, None), 'block5': (2.0, -8/3), 'two3': (2.0, -8/3), 'block11': (2.0688935596, None)}
    Ns = {'block7': (33, 65, 129, 257), 'block9': (33, 65, 129, 257), 'block5': (65, 129, 257), 'two3': (64, 128, 256), 'block11': (33, 65, 129, 257)}
    for name in which:
        ts, corr = pred[name]
        print(f"  {name}: local model tau* = {ts}" + (f", predicted N^2(tau_N - tau*) -> {corr:.4f}" if corr else ""))
        for N in Ns[name]:
            try:
                tau, us = depth_fold(name, N, tau_lo=1.0, tau_hi=2.6)
                print(f"        N={N:4d}  N^2 D_N={tau:.12f}   N^2(tau_N - tau*)={(tau-ts)*N**2:.4f}", flush=True)
            except AssertionError as e:
                print(f"        N={N:4d}  scan failed: {e}")

def depth_polyroots_mp(g, dps=None, tol=1e-15):
    """fully independent: mp.polyroots of the flowed polynomial, bisection on max| |r|-1 |."""
    N = len(g); a, _ = coeffs_product_mp(g, dps)         # a_0..a_N
    mp.mp.dps = max(mp.mp.dps, 50)
    w = [j*(N-j) for j in range(N+1)]
    def off(s):
        coef = [a[j]*mp.exp(s*w[j]) for j in range(N, -1, -1)]   # highest first
        r = mp.polyroots(coef, maxsteps=400, extraprec=200)
        return max(abs(abs(z)-1) for z in r)
    lo, hi = mp.mpf(0), mp.mpf(3)/N**2
    while off(hi) < tol: hi *= 1.3
    for _ in range(60):
        mid = (lo+hi)/2
        if off(mid) > tol: hi = mid
        else: lo = mid
    return float((lo+hi)/2)

def sec_polyroots():
    print("== POLYROOTS: mp.polyroots-based depth (independent of every Fourier/heat solver)")
    table = {'block7': [16, 17, 24, 25, 33], 'block9': [17, 25, 33], 'block5': [17, 33], 'two3': [16, 32],
             'block4even': [16, 32], 'block33': [16, 32], 'block4odd': [17, 33]}
    for name, Ns in table.items():
        for N in Ns:
            t0 = time.time(); D = depth_polyroots_mp(gaps(name, N))
            print(f"   {name:10s} N={N:3d}  N^2D={N*N*D:.12f}   [{time.time()-t0:.1f}s]", flush=True)

# ====================================================================================================
if __name__ == "__main__":
    sec = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if sec == 'sym':     sec_sym()
    elif sec == 'asym':  sec_asym(Ns=tuple(int(x) for x in sys.argv[2:]) or (16, 32, 64, 128, 256, 512, 1024, 2048))
    elif sec == 'models': sec_models(names=tuple(sys.argv[2:]) or ('five', 'two3', 'seven', 'nine_true', 'eleven', 'two3b'))
    elif sec == 'roots': sec_roots()
    elif sec == 'prop71': sec_prop71()
    elif sec == 'asym2': sec_asym2(Ns=tuple(int(x) for x in sys.argv[2:]) or (16, 32, 64, 128, 256, 512, 1024, 2048))
    elif sec == 'asym2fast': sec_asym2(Ns=tuple(int(x) for x in sys.argv[2:]) or (512, 1024, 2048), dtau_verify=0.1)
    elif sec == 'blocks': sec_blocks(which=tuple(sys.argv[2:]) or ('block7', 'block9', 'block5', 'two3', 'block11'))
    elif sec == 'polyroots': sec_polyroots()
    elif sec == 'all':
        sec_prop71(); sec_models(); sec_roots(); sec_sym(); sec_asym(Ns=(16, 32, 64, 128, 256, 512))
