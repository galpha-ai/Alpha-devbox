"""r2_ff_hyperelliptic.py -- Task B5 (7): an actual arithmetic family.

Genus-2 hyperelliptic curves C_f: y^2 = f(x), f monic squarefree of degree 5 over F_p (one rational
point at infinity).  Point counts by brute force over F_p and F_{p^2} = F_p[t]/(t^2 - d):
    N_n = p^n + 1 + sum_{x in F_{p^n}} chi_n(f(x)),  chi_2(w) = chi_p(Norm w) = chi_p(u^2 - d v^2).
Zeta function Z(C,u) = L(u)/((1-u)(1-pu)) with L(u) = 1 + a_1 u + a_2 u^2 + p a_1 u^3 + p^2 u^4,
    S_n := sum alpha_i^n = p^n + 1 - N_n,  a_1 = -S_1 = N_1 - p - 1,  a_2 = (S_1^2 - S_2)/2.
Unitarised: det(1 - u Theta_f) = L(u/sqrt p) = 1 + A u + B u^2 + A u^3 + u^4, A = a_1/sqrt p, B = a_2/p,
Theta_f in USp(4) with eigenangles +-phi_1, +-phi_2 where 2cos(phi_j) are the roots of
Q(x) = x^2 + A x + (B - 2) (x = z + 1/z).  Depth from the reduced quadratic
Q_s(x) = x^2 + A e^{3s} x + (B e^{4s} - 2): D = first s with disc Q_s = 0 (bulk) or Q_s(+-2) = 0 (edge);
vectorised here (grid + bisection), checked against r2_ff_depth_core.depth_usp4_closed_form and the
general ODE/bisection solver.

Comparison with Haar USp(4): Weyl-density rejection samples (2e5), same closed form; two-sample KS
for D, for the trace -A = 2cos phi_1 + 2cos phi_2, and for the smaller angle phi_1.  Also the
frequencies of the finite-p atoms D = 0 (repeated eigenvalue) and D = inf (clock: a_1 = a_2 = 0).

Usage: python3 r2_ff_hyperelliptic.py [quick]   (quick: p=101 only, 300 curves)
Outputs ../data/r2_ff_hyperelliptic_p{p}.npz, ../data/r2_ff_hyperelliptic_summary.json, printed log.
"""
import sys, os, json, time
import numpy as np
from math import pi, sqrt, acos
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from r2_ff_depth_core import depth_usp4_closed_form, weyl_rejection_sample, depth_from_angles, depth_ode
from scipy.stats import ks_2samp

QUICK = len(sys.argv) > 1 and sys.argv[1] == "quick"
PLAN = [(101, 20000), (211, 10000), (401, 5000), (1009, 2000)] if not QUICK else [(101, 300)]
N_HAAR = 200000 if not QUICK else 5000
S_MAX = 12.0


# ------------------------------------------------------------------ finite field helpers
def legendre_table(p):
    chi = -np.ones(p, dtype=np.int64); chi[0] = 0
    chi[(np.arange(1, p, dtype=np.int64) ** 2) % p] = 1
    return chi


def poly_gcd_deg(f, g, p):
    """degree of gcd(f, g) over F_p; f, g ascending coefficient lists (ints)."""
    def trim(a):
        a = list(a)
        while a and a[-1] % p == 0:
            a.pop()
        return a
    f, g = trim(f), trim(g)
    while g:
        # f mod g
        f = f[:]
        inv = pow(g[-1], p - 2, p)
        while len(f) >= len(g):
            c = (f[-1] * inv) % p
            sh = len(f) - len(g)
            for i in range(len(g)):
                f[sh + i] = (f[sh + i] - c * g[i]) % p
            f = trim(f)
            if not f:
                break
        f, g = g, f
    return len(f) - 1


def is_squarefree(c, p):
    d = [(k * c[k]) % p for k in range(1, len(c))]
    return poly_gcd_deg(c, d, p) == 0


class Counter:
    def __init__(self, p):
        self.p = p
        self.chi = legendre_table(p)
        self.d = int(np.where(self.chi == -1)[0][0])       # a non-residue: F_{p^2} = F_p(sqrt d)
        self.X = np.arange(p, dtype=np.int64)
        u, v = np.meshgrid(np.arange(p, dtype=np.int64), np.arange(p, dtype=np.int64), indexing="ij")
        self.U, self.V = u.ravel(), v.ravel()
        self.norm_chi = self.chi[(self.U * self.U - self.d * self.V * self.V) % p]   # chi_2(u + v t)

    def counts(self, c):
        """(N_1, N_2) for y^2 = f(x), f = sum c_k x^k, c ascending, monic degree 5."""
        p = self.p
        val = np.zeros_like(self.X)
        for k in range(5, -1, -1):
            val = (val * self.X + c[k]) % p
        N1 = p + 1 + int(self.chi[val].sum())
        A = np.zeros_like(self.U); B = np.zeros_like(self.U)
        for k in range(5, -1, -1):
            A, B = (A * self.U + B * self.V * self.d + c[k]) % p, (A * self.V + B * self.U) % p
        # chi_2(A + B t) = chi_p(A^2 - d B^2); the point (x, y) with x in F_{p^2}: 1 + chi_2(f(x)) points
        N2 = p * p + 1 + int(self.chi[(A * A - self.d * B * B) % p].sum())
        return N1, N2


# ------------------------------------------------------------------ vectorised genus-2 depth
def depth_usp4_vec(A, B, s_max=S_MAX, K=3000, n_bis=45, chunk=4000):
    """First positive zero of each of disc Q_s, Q_s(2), Q_s(-2) on a quadratically spaced grid,
    refined by bisection; D = min, type = argmin (0 bulk, 1 edge+, 2 edge-).  inf if none."""
    A = np.asarray(A, float); B = np.asarray(B, float)
    n = len(A)
    grid = s_max * (np.arange(K + 1) / K) ** 2
    D = np.full(n, np.inf); T = np.full(n, -1)
    funcs = [lambda s, A, B: A * A * np.exp(6 * s) - 4.0 * (B * np.exp(4 * s) - 2.0),
             lambda s, A, B: 2.0 + 2.0 * A * np.exp(3 * s) + B * np.exp(4 * s),
             lambda s, A, B: 2.0 - 2.0 * A * np.exp(3 * s) + B * np.exp(4 * s)]
    for st in range(0, n, chunk):
        a = A[st:st + chunk, None]; b = B[st:st + chunk, None]
        for ti, f in enumerate(funcs):
            v = f(grid[None, :], a, b)
            sg = np.sign(v)
            change = (sg[:, 1:] != sg[:, :1]) & (sg[:, :1] != 0)
            has = change.any(axis=1)
            kk = np.argmax(change, axis=1)          # first index with a sign change (v[k+1] vs v[0])
            lo = grid[kk]; hi = grid[kk + 1]
            aa = a[:, 0]; bb = b[:, 0]
            for _ in range(n_bis):
                mid = 0.5 * (lo + hi)
                vm = f(mid, aa, bb)
                same = np.sign(vm) == sg[:, 0]
                lo = np.where(same, mid, lo); hi = np.where(same, hi, mid)
            cand = np.where(has, 0.5 * (lo + hi), np.inf)
            better = cand < D[st:st + chunk]
            D[st:st + chunk] = np.where(better, cand, D[st:st + chunk])
            T[st:st + chunk] = np.where(better, ti, T[st:st + chunk])
    return D, T


def angles_from_AB(A, B):
    disc = A * A - 4.0 * (B - 2.0)
    x1 = (-A - np.sqrt(np.maximum(disc, 0))) / 2; x2 = (-A + np.sqrt(np.maximum(disc, 0))) / 2
    return np.arccos(np.clip(x1 / 2, -1, 1)), np.arccos(np.clip(x2 / 2, -1, 1))


if __name__ == "__main__":
    rng = np.random.default_rng(20260905)
    summary = {}
    # ---- Haar reference
    t0 = time.time()
    H = weyl_rejection_sample("USp", 2, N_HAAR, rng)
    cH1, cH2 = np.cos(H[:, 0]), np.cos(H[:, 1])
    A_H = -2.0 * (cH1 + cH2); B_H = 2.0 + 4.0 * cH1 * cH2
    D_H, T_H = depth_usp4_vec(A_H, B_H)
    print(f"Haar USp(4): {N_HAAR} Weyl samples, depth in {time.time()-t0:.1f}s; median D = {np.median(D_H):.5f}, "
          f"quartiles {np.quantile(D_H,.25):.5f}/{np.quantile(D_H,.75):.5f}, P(D>2) = {np.mean(D_H>2):.4f}, "
          f"types bulk/edge+/edge- = {np.mean(T_H==0):.3f}/{np.mean(T_H==1):.3f}/{np.mean(T_H==2):.3f}")
    # cross-check the vectorised closed form against the scalar closed form and the general solvers
    worst_cf = 0.0; worst_ode = 0.0
    for i in range(200):
        Dc, tc = depth_usp4_closed_form(H[i, 0], H[i, 1])
        worst_cf = max(worst_cf, abs(Dc - D_H[i]) / Dc)
        Do = depth_ode(H[i], "USp")["D"]
        worst_ode = max(worst_ode, abs(Do - D_H[i]) / Do)
    print(f"   vectorised vs scalar closed form: worst rel {worst_cf:.1e}; vs ODE solver: worst rel {worst_ode:.1e}")
    summary["haar"] = dict(n=N_HAAR, median=float(np.median(D_H)), q25=float(np.quantile(D_H, .25)), q75=float(np.quantile(D_H, .75)),
                           frac_bulk=float(np.mean(T_H == 0)), frac_edge=float(np.mean(T_H >= 1)), worst_cf=worst_cf, worst_ode=worst_ode)
    np.savez(os.path.join(HERE, "..", "data", "r2_ff_hyperelliptic_haar.npz"), phi=H, D=D_H, T=T_H)

    for p, n_curves in PLAN:
        t0 = time.time()
        C = Counter(p)
        sp = sqrt(p)
        rows = []
        tried = 0; nonsq = 0
        while len(rows) < n_curves:
            c = [int(x) for x in rng.integers(0, p, size=5)] + [1]
            tried += 1
            if not is_squarefree(c, p):
                nonsq += 1
                continue
            N1, N2 = C.counts(c)
            S1 = p + 1 - N1; S2 = p * p + 1 - N2
            a1 = -S1
            twoa2 = S1 * S1 - S2
            assert twoa2 % 2 == 0, "a_2 not integral"
            a2 = twoa2 // 2
            rows.append((a1, a2, N1, N2) + tuple(c[:5]))
        R = np.array(rows, dtype=np.int64)
        a1 = R[:, 0].astype(float); a2 = R[:, 1].astype(float)
        A = a1 / sp; B = a2 / p
        assert np.all(np.abs(a1) <= 4 * sp + 1e-9) and np.all(A * A - 4 * (B - 2) >= -1e-9), "Weil bounds violated"
        D, T = depth_usp4_vec(A, B)
        ph1, ph2 = angles_from_AB(A, B)
        dt = time.time() - t0
        clock = np.mean((a1 == 0) & (a2 == 0))
        repeated = np.mean(np.abs(A * A - 4 * (B - 2)) < 1e-12) + np.mean((np.abs(A) > 0) & (np.abs(np.abs(A) - 2 - B) < 1e-12) * 0)   # x1=x2
        rep2 = np.mean(np.isclose(ph1, 0) | np.isclose(ph2, 0) | np.isclose(ph1, pi) | np.isclose(ph2, pi))   # eigenvalue +-1 (double)
        fin = np.isfinite(D) & (D > 0)
        finH = np.isfinite(D_H) & (D_H > 0)
        ks_D = ks_2samp(D[fin], D_H[finH])
        ks_tr = ks_2samp(-A, -A_H)
        ks_ph = ks_2samp(np.minimum(ph1, ph2), H[:, 0])
        ks_logD = ks_2samp(np.log(D[fin]), np.log(D_H[finH]))
        noise95 = 1.36 * sqrt((len(D) + len(D_H)) / (len(D) * len(D_H)))
        print(f"p={p}: {n_curves} squarefree monic quintics ({tried} tried, {nonsq} non-squarefree, expected fraction 1/p = {1/p:.4f}, observed {nonsq/tried:.4f}) in {dt:.0f}s")
        print(f"   E[a1]={a1.mean():+.3f} (Haar 0), E[a1^2]/p={np.mean(a1**2)/p:.4f} (Haar 1, family exact 1-1/p={1-1/p:.4f}), E[a2]/p={a2.mean()/p:.4f} (Haar: E[e_2]=1 -> B mean 1)")
        print(f"   atoms: P(clock a1=a2=0) = {clock:.5f}; P(repeated eigenvalue, D=0) = {np.mean(~fin)-clock:.5f}; P(D=inf) = {np.mean(np.isinf(D)):.5f}")
        print(f"   depth: median D = {np.median(D[fin]):.5f} (Haar {np.median(D_H[finH]):.5f}); types bulk/edge+/edge- = {np.mean(T==0):.3f}/{np.mean(T==1):.3f}/{np.mean(T==2):.3f} (Haar {np.mean(T_H==0):.3f}/{np.mean(T_H==1):.3f}/{np.mean(T_H==2):.3f})")
        print(f"   KS(D) = {ks_D.statistic:.4f} (p-value {ks_D.pvalue:.3g}); KS(log D) = {ks_logD.statistic:.4f}; KS(trace) = {ks_tr.statistic:.4f} (p {ks_tr.pvalue:.3g}); KS(phi_min) = {ks_ph.statistic:.4f} (p {ks_ph.pvalue:.3g}); 95% two-sample noise level = {noise95:.4f}")
        summary[f"p{p}"] = dict(p=p, n=int(n_curves), tried=tried, nonsq=nonsq, mean_a1=float(a1.mean()), mean_a1sq_over_p=float(np.mean(a1**2)/p),
                                mean_B=float(B.mean()), clock=float(clock), D0=float(np.mean(~fin) - clock), median_D=float(np.median(D[fin])),
                                frac_bulk=float(np.mean(T == 0)), frac_edge_plus=float(np.mean(T == 1)), frac_edge_minus=float(np.mean(T == 2)),
                                ks_D=float(ks_D.statistic), ks_D_p=float(ks_D.pvalue), ks_logD=float(ks_logD.statistic),
                                ks_trace=float(ks_tr.statistic), ks_trace_p=float(ks_tr.pvalue), ks_phimin=float(ks_ph.statistic), ks_phimin_p=float(ks_ph.pvalue),
                                noise95=float(noise95), seconds=dt)
        np.savez(os.path.join(HERE, "..", "data", f"r2_ff_hyperelliptic_p{p}.npz"), R=R, A=A, B=B, D=D, T=T, phi1=ph1, phi2=ph2)
    with open(os.path.join(HERE, "..", "data", "r2_ff_hyperelliptic_summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print("saved ../data/r2_ff_hyperelliptic_*.npz and ../data/r2_ff_hyperelliptic_summary.json")
