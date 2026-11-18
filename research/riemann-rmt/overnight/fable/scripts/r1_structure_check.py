"""r1_structure_check.py -- adversarial re-verification of the 'new structures' (Fable cluster E, task C2).

Checks (each prints PASS/FAIL with the measured deviation):

 A. Fourier identity  sum_{d=0}^{N-1} d(N-d) w^{-kd} = -N/(2 sin^2(pi k/N)), k != 0   (N = 4..24; exact for N=6,8 via sympy)
 B. L_N e_delta = delta(N-delta) e_delta,  L_N = Jacobian of the attracting Coulomb flow at the clock,
    and the EXACT band-limited identity  L_N = N(-Delta)^{1/2} + Delta  (symbol N|d| - d^2 for |d| <= N/2).
 C. Two-line proof of 'L_N = Jacobian': at the clock, d e_j / d theta_m = i(-1)^{j-1} w^{mj}  (e_j = elementary
    symmetric fn of the roots), so the j-th coefficient is the j-th Fourier mode of the displacement, and the flow is
    diagonal on coefficients with rate j(N-j).  Verified numerically at N = 8 (finite differences).
 D. Continuum: (1/4pi) int_{-pi}^{pi} (1 - cos ky) csc^2(y/2) dy = |k|  (kernel of (-Delta)^{1/2} on the circle),
    and N^{-1} delta(N-delta) -> |delta|.
 E. SU(N) quadratic Casimir of the fundamental representation wedge^j:  C_2(omega_j) = j(N-j)(N+1)/N, so the finite
    depth flow  a_j -> a_j e^{s j(N-j)}  is the SU(N) Casimir (heat) flow on the characters e_j = chi_{wedge^j}
    run BACKWARD, with time  t = -s N/(N+1).
 F. Sector pairing: smallest degree d at which some balanced observable p_lambda conj(p_nu), |lambda|=|nu|=d, has
    E_ACUE[ z(C)^delta p_lambda conj(p_nu) ] != 0,  z(C) = e^{2 pi i sum(C)/N};  claim: d = delta(N-delta).  N = 5, 6.
 G. Marked depth: Cayley sign  d theta/d lambda = +2/(1+lambda^2)  (peer audit); the 'rank-two law' with the
    paper's labelling; and the PRODUCT-RULE TAUTOLOGY: the decomposition  tau' = (d phi/d eta) kappa + phi kappa'
    with kappa := tau/phi holds to finite-difference accuracy for ANY phi (delta^2/8, delta^3, 1), so the
    '11-digit confirmation' of the law tests differentiation, not physics.  The honest content -- how much of tau'
    the constant-kappa local term carries -- is measured over random marks and configurations (N = 6, 8).
 H. Rotation-covariant marking  U -> U exp(i eta u u*): first-order eigenphase derivative = |<u,v_j>|^2; Haar-lifted
    first moment E_u[chi~ | theta] = (1/N) sum_j d tau/d theta_j = 0 exactly (rotation invariance); second moment
    = |grad tau|^2 / (N(N+1)).  Verified by Monte Carlo at one N = 6 configuration.
 I. Dihedral invariance of tau (rotation and reflection) to solver accuracy.

Run:  python3 r1_structure_check.py   (about 1-2 minutes, single core)
"""
import sys, os, time
import numpy as np
from itertools import combinations
from math import pi, factorial
from collections import Counter

RR = "/home/user/Alpha-devbox/research/riemann-rmt"
sys.path.insert(0, f"{RR}/riemann-impostors/counterexamples")
from dyn1_core import find_ustar

def tag(ok, name, dev):
    print(f"{'PASS' if ok else 'FAIL'}  {name}   dev={dev:.3e}")

# ---------------------------------------------------------------- A
print("== A. Fourier identity ==")
worst = 0.0
for N in range(4, 25):
    d = np.arange(N); w = d * (N - d)
    for k in range(1, N):
        lhs = (w * np.exp(-2j * pi * k * d / N)).sum()
        rhs = -N / (2 * np.sin(pi * k / N) ** 2)
        worst = max(worst, abs(lhs - rhs))
tag(worst < 1e-9, "sum d(N-d) w^{-kd} = -N/(2 sin^2(pi k/N)), N=4..24", worst)
import sympy as sp
for N in (6, 8):
    k = sp.symbols('k', integer=True)
    ok = True
    for kk in range(1, N):
        lhs = sum(dd * (N - dd) * sp.exp(-2 * sp.pi * sp.I * kk * dd / N) for dd in range(N))
        rhs = -sp.Integer(N) / (2 * sp.sin(sp.pi * kk / N) ** 2)
        ok &= (sp.nsimplify(sp.simplify(lhs - rhs)) == 0) or abs(complex(lhs - rhs)) < 1e-12
    print(f"      exact (sympy) check N={N}: {'OK' if ok else 'MISMATCH'}")

# ---------------------------------------------------------------- B
print("== B. L_N spectrum, Jacobian, band-limited identity ==")
def L_matrix(N):
    M = np.zeros((N, N))
    for x in range(N):
        for k in range(1, N):
            c = 1.0 / (2 * np.sin(pi * k / N) ** 2)
            M[x, x] += c; M[x, (x + k) % N] -= c
    return M
def jacobian_clock(N):
    J = np.zeros((N, N))
    for j in range(N):
        for k in range(N):
            if k == j: continue
            c = 1.0 / (2 * np.sin(pi * (j - k) / N) ** 2)
            J[j, j] += c; J[j, k] -= c
    return J
worstB = worstJ = worstS = 0.0
for N in (4, 5, 6, 7, 8, 12, 16, 24):
    L = L_matrix(N); J = jacobian_clock(N)
    x = np.arange(N)
    for dlt in range(N):
        e = np.exp(2j * pi * dlt * x / N)
        worstB = max(worstB, np.abs(L @ e - dlt * (N - dlt) * e).max())
    worstJ = max(worstJ, np.abs(L - J).max())
    # band-limited identity: on e_delta with |delta|<=N/2 representative, L_N = N|delta| - delta^2
    for dlt in range(-(N // 2), N // 2 + 1):
        e = np.exp(2j * pi * dlt * x / N)
        worstS = max(worstS, np.abs(L @ e - (N * abs(dlt) - dlt ** 2) * e).max())
tag(worstB < 1e-9, "L_N e_delta = delta(N-delta) e_delta", worstB)
tag(worstJ < 1e-9, "L_N = Jacobian of Coulomb flow at the clock", worstJ)
tag(worstS < 1e-9, "L_N = N(-Delta)^{1/2} + Delta on |delta|<=N/2 (exact symbol N|d|-d^2)", worstS)

# ---------------------------------------------------------------- C
print("== C. two-line proof: coefficients are Fourier modes of the displacement at the clock ==")
def esym(z):
    p = np.array([1.0 + 0j])
    for zz in z: p = np.convolve(p, np.array([1.0, zz]))
    return p          # coefficients of prod(1 + t z_k): e_0..e_N
N = 8; w = np.exp(2j * pi / N); h = 1e-6
worstC = 0.0
for m in range(N):
    th = 2 * pi * np.arange(N) / N
    tp = th.copy(); tp[m] += h; tm = th.copy(); tm[m] -= h
    de = (esym(np.exp(1j * tp)) - esym(np.exp(1j * tm))) / (2 * h)
    for j in range(1, N):
        pred = 1j * (-1) ** (j - 1) * w ** (m * j)
        worstC = max(worstC, abs(de[j] - pred))
tag(worstC < 1e-6, "d e_j/d theta_m |clock = i(-1)^{j-1} w^{mj}  (N=8, central differences)", worstC)
print("      => delta e_j = i(-1)^{j-1} * N * (DFT of eps)_j ; flow a_j e^{s j(N-j)} => mode j relaxes at rate j(N-j) = L_N eigenvalue.")

# ---------------------------------------------------------------- D
print("== D. continuum kernel of (-Delta)^{1/2} ==")
import mpmath as mp
mp.mp.dps = 30
worstD = 0.0
for k in range(0, 6):
    val = mp.quad(lambda y: (1 - mp.cos(k * y)) / mp.sin(y / 2) ** 2, [-mp.pi, 0, mp.pi]) / (4 * mp.pi)
    worstD = max(worstD, abs(float(val) - abs(k)))
tag(worstD < 1e-12, "(1/4pi) int (1-cos ky) csc^2(y/2) dy = |k|, k=0..5", worstD)
N = 1000; print(f"      N^-1 delta(N-delta) at N=1000: delta=1..5 -> {[round((d*(N-d))/N,4) for d in range(1,6)]}  (-> |delta|)")

# ---------------------------------------------------------------- E
print("== E. SU(N) Casimir of wedge^j ==")
worstE = 0.0
for N in range(3, 10):
    rho = np.array([(N + 1) / 2 - i for i in range(1, N + 1)])
    for j in range(1, N):
        om = np.array([1.0] * j + [0.0] * (N - j)) - j / N
        C2 = om @ om + 2 * om @ rho
        worstE = max(worstE, abs(C2 - j * (N - j) * (N + 1) / N))
tag(worstE < 1e-12, "C_2(omega_j) = <omega_j, omega_j + 2 rho> = j(N-j)(N+1)/N  (N=3..9)", worstE)
print("      => e^{t Delta_SU(N)} e_j = e^{-t C_2(omega_j)} e_j (characters are Laplace eigenfunctions),")
print("         so P_s(z) = sum a_j e^{s j(N-j)} z^j is the SU(N) heat flow of det(1 - zU) at time t = -s N/(N+1).")

# ---------------------------------------------------------------- F
print("== F. sector-pairing opening degree ==")
def partitions(n, maxpart):
    def gen(n, maxp):
        if n == 0:
            yield (); return
        for f in range(min(n, maxp), 0, -1):
            for rest in gen(n - f, f):
                yield (f,) + rest
    return list(gen(n, maxpart))
for N in (5, 6):
    M = 2 * N; zeta = np.exp(1j * pi / N)
    configs = list(combinations(range(M), N))
    mu = np.array([np.prod([abs(zeta ** x - zeta ** y) ** 2 for x, y in combinations(S, 2)]) for S in configs])
    mu /= mu.sum()
    X = np.array([sum(S) for S in configs])
    PK = {k: np.array([sum(zeta ** (k * x) for x in S) for S in configs]) for k in range(1, 2 * N)}
    for maxpart, label in ((N, "parts<=N"), (2 * N - 1, "parts<=2N-1")):
        out = []
        for dlt in range(1, N // 2 + 1):
            z = np.exp(2j * pi * dlt * X / N)
            found = None
            for d in range(1, dlt * (N - dlt) + 2):
                pl = partitions(d, maxpart)
                Pl = {lam: np.prod([PK[p] for p in lam], axis=0) for lam in pl}
                mx = 0.0
                for lam in pl:
                    for nu in pl:
                        mx = max(mx, abs((mu * z * Pl[lam] * np.conj(Pl[nu])).sum()))
                if mx > 1e-9:
                    found = d; break
            out.append((dlt, found, dlt * (N - dlt)))
        print(f"      N={N} [{label}]: (delta, first nonzero degree, delta(N-delta)) = {out}")

# ---------------------------------------------------------------- G
print("== G. marked depth: Cayley sign, labelling, product-rule tautology, local share ==")
lam0 = 0.7; hh = 1e-6
th_of = lambda l: np.angle((l - 1j) / (l + 1j))
dth = (th_of(lam0 + hh) - th_of(lam0 - hh)) / (2 * hh)
tag(abs(dth - 2 / (1 + lam0 ** 2)) < 1e-6, "d theta/d lambda = +2/(1+lambda^2) (peer's sign; paper prints -2/(1+lambda^2))", abs(dth - 2 / (1 + lam0 ** 2)))

def angles_evecs(G):
    w, V = np.linalg.eigh(G); return np.angle((w - 1j) / (w + 1j)), w, V
def coeffs(th):
    p = np.array([1.0 + 0j])
    for t in th: p = np.convolve(p, np.array([1.0, -np.exp(1j * t)]))
    return p[::-1]
def tau_of_angles(th):
    return find_ustar(coeffs(th), len(th))[0]
def tau_gap(G):
    th, w, V = angles_evecs(G)
    t = tau_of_angles(th)
    s = np.sort(th); order = np.argsort(th)
    g = np.diff(np.concatenate([s, [s[0] + 2 * pi]])); i = int(np.argmin(g))
    return t, g[i], order[i], order[(i + 1) % len(th)]      # a = first (smaller angle), b = next ccw; gap = th_b - th_a
def dir_deriv(f, G, u, h=1e-5):
    u = u / np.linalg.norm(u); P = np.outer(u, u)
    return (f(G + h * P) - f(G - h * P)) / (2 * h)

rng = np.random.default_rng(3); N = 6
lam = np.array([-1.7, -0.6, -0.15, 0.4, 1.1, 2.3])
Q, _ = np.linalg.qr(rng.normal(size=(N, N))); G = Q @ np.diag(lam) @ Q.T
th, w, V = angles_evecs(G); tau0, d0, ia, ib = tau_gap(G)
# (i) labelling: with gap = theta_b - theta_a, the correct first-order law is gap' = c_b q_b - c_a q_a, c = +2/(1+lambda^2)
u = rng.normal(size=N); u /= np.linalg.norm(u)
qa, qb = (u @ V[:, ia]) ** 2, (u @ V[:, ib]) ** 2
gp_meas = dir_deriv(lambda X: tau_gap(X)[1], G, u)
gp_true = 2 / (1 + w[ib] ** 2) * qb - 2 / (1 + w[ia] ** 2) * qa
gp_paper = (-2 / (1 + w[ia] ** 2)) * qa - (-2 / (1 + w[ib] ** 2)) * qb     # paper: c_a q_a - c_b q_b with c=-2/(1+l^2)
tag(abs(gp_meas - gp_true) < 1e-6, "gap' = (+2/(1+l_b^2)) q_b - (+2/(1+l_a^2)) q_a  (correct-sign form)", abs(gp_meas - gp_true))
print(f"      paper's form c_a q_a - c_b q_b with c=-2/(1+l^2) gives {gp_paper:+.6e} vs measured {gp_meas:+.6e}: "
      f"identical -- the two sign slips (c and the a/b labelling) cancel; the printed formula is right iff delta := theta_b - theta_a with b counter-clockwise of a.")
# (ii) product-rule tautology for three different 'laws'
print("      product-rule test  tau' = phi' kappa + phi kappa'  with kappa := tau/phi :")
for name, phi in (("delta^2/8 (paper)", lambda X: tau_gap(X)[1] ** 2 / 8), ("delta^3", lambda X: tau_gap(X)[1] ** 3), ("1 (no gap at all)", lambda X: 1.0)):
    errs = []
    for i in range(5):
        u = rng.normal(size=N)
        tp = dir_deriv(lambda X: tau_gap(X)[0], G, u)
        php = dir_deriv(phi, G, u)
        kap = lambda X: tau_gap(X)[0] / phi(X)
        kp = dir_deriv(kap, G, u)
        errs.append(abs(tp - (php * kap(G) + phi(G) * kp)))
    print(f"        phi = {name:20s}: max |tau' - (phi' kappa + phi kappa')| = {max(errs):.2e}   (always ~1e-10: it is the product rule)")
# (iii) honest content: share of the local (constant-kappa) term
print("      local-term share  L/(L+B),  L = kappa*delta/4*delta',  B = delta^2/8*kappa'  (random marks, random configs):")
for N in (6, 8):
    shares = []
    for c in range(4):
        lamc = np.sort(rng.normal(size=N) * 1.2)
        Q, _ = np.linalg.qr(rng.normal(size=(N, N))); Gc = Q @ np.diag(lamc) @ Q.T
        t0, dd, ia, ib = tau_gap(Gc); k0 = 8 * t0 / dd ** 2
        thc, wc, Vc = angles_evecs(Gc)
        for i in range(6):
            u = rng.normal(size=N); u /= np.linalg.norm(u)
            qa, qb = (u @ Vc[:, ia]) ** 2, (u @ Vc[:, ib]) ** 2
            gp = 2 / (1 + wc[ib] ** 2) * qb - 2 / (1 + wc[ia] ** 2) * qa
            Lt = k0 * dd / 4 * gp
            tp = dir_deriv(lambda X: tau_gap(X)[0], Gc, u)
            shares.append(Lt / tp if abs(tp) > 1e-12 else np.nan)
    shares = np.array(shares)
    print(f"        N={N}: median L/tau' = {np.nanmedian(shares):.4f}, 10%/90% = {np.nanpercentile(shares,10):.3f}/{np.nanpercentile(shares,90):.3f}, "
          f"min/max = {np.nanmin(shares):.3f}/{np.nanmax(shares):.3f}   (n={len(shares)})")

# ---------------------------------------------------------------- H
print("== H. rotation-covariant marking U -> U e^{i eta u u*}, Haar-lifted moments ==")
N = 6
th0 = np.sort(rng.uniform(0, 2 * pi, N))
U0 = np.diag(np.exp(1j * th0))
def grad_tau(th, h=1e-5):
    g = np.zeros(len(th))
    for j in range(len(th)):
        tp = th.copy(); tp[j] += h; tm = th.copy(); tm[j] -= h
        g[j] = (tau_of_angles(tp) - tau_of_angles(tm)) / (2 * h)
    return g
g = grad_tau(th0)
tag(abs(g.sum()) < 1e-6, "sum_j d tau/d theta_j = 0 (rotation invariance) at a random N=6 config", abs(g.sum()))
def chi_twist(Uc, u, h=1e-5):
    u = u / np.linalg.norm(u); P = np.outer(u, u.conj())
    def tau_U(Um):
        return tau_of_angles(np.angle(np.linalg.eigvals(Um)))
    from scipy.linalg import expm
    return (tau_U(Uc @ expm(1j * h * P)) - tau_U(Uc @ expm(-1j * h * P))) / (2 * h)
# first-order eigenphase derivative = |<u,v_j>|^2 (here v_j = e_j): chi~ = sum_j g_j |u_j|^2
vals, preds = [], []
for i in range(300):
    u = rng.normal(size=N) + 1j * rng.normal(size=N); u /= np.linalg.norm(u)
    vals.append(chi_twist(U0, u)); preds.append(g @ (np.abs(u) ** 2))
vals, preds = np.array(vals), np.array(preds)
tag(np.abs(vals - preds).max() < 1e-5, "chi~(U;u) = sum_j (d tau/d theta_j)|u_j|^2  (300 Haar marks)", np.abs(vals - preds).max())
m1 = vals.mean(); m2 = (vals ** 2).mean(); pred2 = g @ g / (N * (N + 1))
print(f"      Haar mean = {m1:+.3e} (exact 0), Haar 2nd moment = {m2:.4e} vs |grad tau|^2/(N(N+1)) = {pred2:.4e}  (MC n=300, rel err {abs(m2-pred2)/pred2:.2%})")
# exact Dirichlet moments: E[q_j q_k] = (1+delta_jk)/(N(N+1))
print(f"      exact: E[chi~^2|theta] = (|g|^2 + (sum g)^2)/(N(N+1)) = {(g@g + g.sum()**2)/(N*(N+1)):.4e}")

# ---------------------------------------------------------------- I
print("== I. dihedral invariance of tau ==")
t0 = tau_of_angles(th0); worstI = 0.0
for alpha in (0.3, 1.7, 4.0):
    worstI = max(worstI, abs(tau_of_angles((th0 + alpha) % (2 * pi)) - t0))
worstI = max(worstI, abs(tau_of_angles((-th0) % (2 * pi)) - t0))
tag(worstI < 1e-8, "tau(theta + alpha) = tau(-theta) = tau(theta)", worstI)
print("done.")
