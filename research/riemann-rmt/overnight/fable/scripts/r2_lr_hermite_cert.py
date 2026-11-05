"""r2_lr_hermite_cert.py -- rigorous dual certificates for the pair LP (bandwidth-one mimicry + Bochner).

Certificate (derived in r2_lr_hardcore_lp.md, part (a)): an even real T with FT phi such that
   (i) T(x) <= 0 for |x| >= c,   (ii) phi(alpha) >= 0 for |alpha| >= 1,
   (iii) J := phi(0) - T(0) + 2 int_0^1 alpha phi(alpha) dalpha > 0
proves that no stationary intensity-1 process with hard core c has Bartlett spectrum = |alpha| on (-1,1).
Class: T(x) = sum_{m=0}^{D} a_m h_{2m}(x/sigma), h_n = orthonormal Hermite function of sqrt(2 pi) x,
so phi(alpha) = sigma sum_m (-1)^m a_m h_{2m}(sigma alpha).  D odd so that a_D < 0 makes both leading
coefficients right.  LP: maximise J s.t. T(x_i) <= -eps e^{-pi x^2/sigma^2} on [c, XT], phi(alpha_i) >= eps sigma e^{-pi sigma^2 alpha^2} on [1, AT],
|a_m| <= 1, a_D <= 0.  Verification (function verify): leading-coefficient sign, Cauchy root bound,
grid + Lipschitz check of the sign conditions, J by high-order Gauss-Legendre (mpmath cross-check).
Usage: python3 r2_lr_hermite_cert.py D sigma eps [c]   (bisects c if c not given)
"""
import sys, json, time
import numpy as np
from scipy.optimize import linprog
import mpmath as mp

DATA = "/home/user/Alpha-devbox/research/riemann-rmt/overnight/fable/data"

def herm(nmax, y):
    """orthonormal Hermite functions psi_0..psi_nmax at points y (array). Returns (nmax+1, len(y))."""
    y = np.asarray(y, float)
    out = np.empty((nmax + 1, len(y)))
    out[0] = np.pi**-0.25*np.exp(-y*y/2)
    if nmax >= 1: out[1] = np.sqrt(2)*y*out[0]
    for n in range(1, nmax):
        out[n+1] = np.sqrt(2/(n+1))*y*out[n] - np.sqrt(n/(n+1))*out[n-1]
    return out

class Cert:
    def __init__(self, D, sigma):
        self.D, self.sigma = D, sigma
        self.ms = np.arange(D + 1)
    def T(self, x, a):
        H = herm(2*self.D, np.sqrt(2*np.pi)*np.asarray(x, float)/self.sigma)
        return a @ H[::2]
    def phi(self, al, a):
        H = herm(2*self.D, np.sqrt(2*np.pi)*self.sigma*np.asarray(al, float))
        return self.sigma*((-1.0)**self.ms*a) @ H[::2]
    def Jcoef(self, nq=400):
        t, w = np.polynomial.legendre.leggauss(nq); al = 0.5*(t + 1); w = 0.5*w
        H = herm(2*self.D, np.sqrt(2*np.pi)*self.sigma*al)[::2]          # D+1 x nq
        integ = H @ (w*al)                                                 # int_0^1 alpha h_2m(sigma alpha)
        h0 = herm(2*self.D, np.array([0.0]))[::2, 0]
        sgn = (-1.0)**self.ms
        return self.sigma*sgn*h0 - h0 + 2*self.sigma*sgn*integ

def solve(D, sigma, c, eps, XT=10.0, AT=10.0, hx=0.005):
    C = Cert(D, sigma)
    xs = np.arange(c, XT, hx); als = np.arange(1.0, AT, hx)
    HT = herm(2*D, np.sqrt(2*np.pi)*xs/sigma)[::2].T                      # T(x_i) = HT a
    Hp = (sigma*(-1.0)**C.ms)*herm(2*D, np.sqrt(2*np.pi)*sigma*als)[::2].T   # phi(al_i) = Hp a
    A_ub = np.vstack([HT, -Hp]); b_ub = np.concatenate([-eps*np.exp(-np.pi*xs**2/sigma**2), -eps*sigma*np.exp(-np.pi*sigma**2*als**2)])
    J = C.Jcoef()
    bounds = [(-1, 1)]*(D + 1); bounds[D] = (-1, 0)
    res = linprog(-J, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    if res.status != 0:
        return -np.inf, None
    return -res.fun, res.x

def verify(D, sigma, a, c, eta=2e-4, verbose=True):
    """Check of (i),(ii),(iii) with explicit bounds; returns (ok, J, details)."""
    C = Cert(D, sigma)
    mp.mp.dps = 40
    def herm_polys(nmax):   # orthonormal Hermite polynomial parts, ascending monomial coefficients in y
        polys = [[mp.pi**mp.mpf(-0.25)], [mp.mpf(0), mp.sqrt(2)*mp.pi**mp.mpf(-0.25)]]
        for n in range(1, nmax):
            pn, pm = polys[n], polys[n-1]
            new = [mp.mpf(0)]*(n + 2)
            for i, cc in enumerate(pn): new[i+1] += mp.sqrt(mp.mpf(2)/(n+1))*cc
            for i, cc in enumerate(pm): new[i] -= mp.sqrt(mp.mpf(n)/(n+1))*cc
            polys.append(new)
        return polys
    polys = herm_polys(2*D)
    def combo(signs):
        P = [mp.mpf(0)]*(2*D + 1)
        for m in range(D + 1):
            for i, cc in enumerate(polys[2*m]): P[i] += signs[m]*mp.mpf(float(a[m]))*cc
        return P
    PT = combo([1]*(D + 1))                      # T(x) = e^{-y^2/2} PT(y), y = sqrt(2pi) x/sigma
    Pp = combo([(-1)**m for m in range(D + 1)])  # phi(al) = sigma e^{-y^2/2} Pp(y), y = sqrt(2pi) sigma al
    def cauchy(P):
        lead = P[-1]
        return lead, 1 + max(abs(cc/lead) for cc in P[:-1])
    leadT, RT = cauchy(PT); leadp, Rp = cauchy(Pp)
    det = dict(leadT=float(leadT), leadphi=float(leadp), RT_y=float(RT), Rphi_y=float(Rp))
    ok = (leadT < 0) and (leadp > 0)
    # Lipschitz bounds: |T'(x)| <= (sqrt(2pi)/sigma) pi^{-1/4} sum |a_m| (sqrt(m) + sqrt(m+1/2))  (Cramer bound)
    L_T = np.sqrt(2*np.pi)/sigma*np.pi**-0.25*np.sum(np.abs(a)*(np.sqrt(C.ms) + np.sqrt(C.ms + 0.5)))
    L_p = np.sqrt(2*np.pi)*sigma*sigma*np.pi**-0.25*np.sum(np.abs(a)*(np.sqrt(C.ms) + np.sqrt(C.ms + 0.5)))
    xmax = float(RT)*sigma/np.sqrt(2*np.pi); amax = float(Rp)/(sigma*np.sqrt(2*np.pi))
    xs = np.arange(c, max(xmax, c) + eta, eta); als = np.arange(1.0, max(amax, 1.0) + eta, eta)
    Tmax = np.max(C.T(xs, a)); pmin = np.min(C.phi(als, a))
    fp_allow = 1e-11*np.sum(np.abs(a))*(2*D + 1)
    okT = Tmax + L_T*eta/2 + fp_allow <= 0
    okp = pmin - L_p*eta/2 - fp_allow >= 0
    det.update(xmax=xmax, amax=amax, Tmax_grid=float(Tmax), phimin_grid=float(pmin), L_T=float(L_T), L_phi=float(L_p),
               marginT=float(-(Tmax + L_T*eta/2 + fp_allow)), marginphi=float(pmin - L_p*eta/2 - fp_allow))
    ok = ok and okT and okp
    J_np = float(C.Jcoef() @ a)
    def f(al):
        y = mp.sqrt(2*mp.pi)*sigma*al
        return mp.exp(-y*y/2)*sum(mp.mpf(float(a[m]))*(-1)**m*mp.polyval(polys[2*m][::-1], y) for m in range(D + 1))
    I = mp.quad(lambda al: al*f(al), [0, 0.25, 0.5, 0.75, 1])
    T0 = sum(mp.mpf(float(a[m]))*polys[2*m][0] for m in range(D + 1))
    J_mp = sigma*f(mp.mpf(0)) - T0 + 2*sigma*I
    det.update(J_numpy=J_np, J_mpmath=float(J_mp))
    ok = ok and (J_mp > 0)
    if verbose:
        print("verify:", json.dumps(det))
    return ok, float(J_mp), det

if __name__ == "__main__":
    D, sigma, eps = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
    t0 = time.time()
    if len(sys.argv) > 4:
        c = float(sys.argv[4])
        J, a = solve(D, sigma, c, eps)
        print(f"D={D} sigma={sigma} eps={eps} c={c}: J_max={J:.6e}  ({time.time()-t0:.0f}s)")
        if a is not None and J > 0:
            ok, Jv, det = verify(D, sigma, a, c)
            print("VERIFIED" if ok else "verification FAILED", "J =", Jv)
            json.dump(dict(D=D, sigma=sigma, eps=eps, c=c, a=a.tolist(), J=Jv, ok=bool(ok), det=det),
                      open(f"{DATA}/r2_lr_hermite_D{D}_s{sigma}_c{c}.json", "w"), indent=1)
    else:
        lo, hi = 0.5, 0.7
        for c in (0.55, 0.6, 0.65):
            J, a = solve(D, sigma, c, eps); print(f"  c={c}: J_max={J:+.4e}", flush=True)
        for _ in range(16):
            mid = 0.5*(lo + hi)
            J, a = solve(D, sigma, mid, eps)
            print(f"  c={mid:.6f}: J_max={J:+.4e}  ({time.time()-t0:.0f}s)", flush=True)
            if J > 0: hi = mid
            else: lo = mid
        print(f"c_H(D={D}, sigma={sigma}, eps={eps}) in [{lo:.5f}, {hi:.5f}]")
