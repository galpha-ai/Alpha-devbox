#!/usr/bin/env python3
"""r1_dual_lp.py -- sequential-LP optimisation of the fiberwise Schur-test weight H(x,u) for the
epsilon-trick constant M_{k,eps}  (FLOAT discovery stage; certification is in r1_sub186_wall.py).

Class of duals (rigorous statement in r1_sub186_wall.md, Prop. 2):
  H(x,u) > 0 on {0 <= x <= u, 2eps <= u <= 1+eps},  int_0^u dx/H(x,u) <= 1 for all u,
  ==>  M_{k,eps} <= Lambda(H) := sup_sigma  inf_mu [ k sup_{x in [0,sigma]} ( g_sigma(x) - mu x ) + mu sigma ],
       g_sigma(x) = H(x, 1+eps-sigma+x) 1[x >= delta(sigma)],  delta = max(0, sigma-(1-eps)).
Discretisation: Hhat(xi,u) on a grid in xi = x/u in [0,1] and u in [2eps,1+eps], bilinear interpolation;
variables Hhat_{il}, mu_a (one per sigma grid point), Lambda; constraints
  (C1)  k (Hhat(xi_j(a), u_j(a)) - mu_a x_j) + mu_a sigma_a <= Lambda   for x_j in [delta_a, sigma_a]
        (plus the inactive point x=0: mu_a sigma_a <= Lambda, and x=delta^-: -k mu_a delta_a + mu_a sigma_a <= Lambda)
  (C2)  mass, linearised at the current iterate H0:  u_l sum_i w_i (2/H0_il - Hhat_il/H0_il^2) <= 1,
        with a multiplicative trust region; after each LP the rows are rescaled to exact unit mass.
The classical weight Hhat = u (1+(k-1) xi) log k/(k-1) is the starting point (Lambda = (1+eps) k log k/(k-1)).
Output: grid H and mu saved to ../data/r1_dualH_k{k}_e{eps}.npz, plus the float Lambda (fine evaluation).
"""
import sys, os, math, time, json
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "..", "data")

def row_mass_exact(u, xi, Hrow):
    """u * int_0^1 dxi / (piecewise-linear interpolant of Hrow on xi grid)  (closed form)."""
    tot = 0.0
    for i in range(len(xi) - 1):
        A, B = Hrow[i], Hrow[i + 1]; w = xi[i + 1] - xi[i]
        if abs(B - A) < 1e-12 * max(A, B):
            tot += w / A
        else:
            tot += w * math.log(B / A) / (B - A)
    return u * tot

class GridH:
    def __init__(self, k, eps, xi, ug, H):
        self.k, self.eps, self.xi, self.ug, self.H = k, eps, xi, ug, H   # H shape (nxi, nu)
    def eval(self, x, u):
        """bilinear interpolation of H at (xi=x/u, u); vectorised."""
        x = np.asarray(x, float); u = np.asarray(u, float)
        xi = np.clip(x / np.maximum(u, 1e-300), 0, 1)
        i = np.clip(np.searchsorted(self.xi, xi, side="right") - 1, 0, len(self.xi) - 2)
        l = np.clip(np.searchsorted(self.ug, u, side="right") - 1, 0, len(self.ug) - 2)
        wx = (xi - self.xi[i]) / (self.xi[i + 1] - self.xi[i]); wu = (u - self.ug[l]) / (self.ug[l + 1] - self.ug[l])
        wu = np.clip(wu, 0, 1)
        return ((1 - wx) * (1 - wu) * self.H[i, l] + wx * (1 - wu) * self.H[i + 1, l]
                + (1 - wx) * wu * self.H[i, l + 1] + wx * wu * self.H[i + 1, l + 1])

def hull_value(xs, gs, x0):
    L = xs <= x0; R = xs >= x0
    if not L.any() or not R.any():
        return float(gs.max())
    x1 = xs[L][:, None]; g1 = gs[L][:, None]; x2 = xs[R][None, :]; g2 = gs[R][None, :]
    dx = x2 - x1
    with np.errstate(divide='ignore', invalid='ignore'):
        v = np.where(dx > 0, g1 + (g2 - g1) * (x0 - x1) / dx, np.maximum(g1, g2))
    return float(v.max())

def Lambda_fine(G, nsig=400, nx=400):
    k, eps = G.k, G.eps
    best, arg = -1, None
    for s in np.linspace(0, 1 + eps, nsig):
        if s <= 0:
            v = k * G.eval(0.0, 1 + eps)
        else:
            d = max(0.0, s - (1 - eps))
            xs = np.linspace(d, s, nx); gs = G.eval(xs, 1 + eps - s + xs)
            if d > 0:
                xs = np.concatenate([[0.0], xs]); gs = np.concatenate([[0.0], gs])
            v = k * hull_value(xs, gs, s / k)
        if v > best:
            best, arg = v, s
    return best, arg

def classical_grid(k, eps, xi, ug):
    return np.outer(1 + (k - 1) * xi, ug) * math.log(k) / (k - 1)

def slp(k, eps, nxi=48, nu=48, nsig=96, nxc=96, iters=40, rho0=1.6, verbose=True, xi_power=1.0):
    xi = np.linspace(0, 1, nxi) ** xi_power
    ug = np.linspace(2 * eps, 1 + eps, nu)
    H = classical_grid(k, eps, xi, ug)
    sig = np.linspace(0, 1 + eps, nsig)
    nH = nxi * nu
    idx = lambda i, l: i * nu + l
    # (C1) rows: for each sigma_a, x_j grid in [delta_a, sigma_a]
    rows, cols, vals, rhs_rows = [], [], [], 0
    def add_row(entries):
        nonlocal rhs_rows
        for c, v in entries:
            rows.append(rhs_rows); cols.append(c); vals.append(v)
        rhs_rows += 1
    imu = lambda a: nH + a
    iL = nH + nsig
    for a, s in enumerate(sig):
        d = max(0.0, s - (1 - eps))
        if s <= 0:
            xs = np.array([0.0])
        else:
            xs = np.linspace(d, s, nxc)
        for x in xs:
            u = 1 + eps - s + x
            xiv = 0.0 if u <= 0 else min(1.0, x / u)
            i = min(max(np.searchsorted(xi, xiv, side="right") - 1, 0), nxi - 2)
            l = min(max(np.searchsorted(ug, u, side="right") - 1, 0), nu - 2)
            wx = (xiv - xi[i]) / (xi[i + 1] - xi[i]); wu = min(1.0, max(0.0, (u - ug[l]) / (ug[l + 1] - ug[l])))
            ent = [(idx(i, l), k * (1 - wx) * (1 - wu)), (idx(i + 1, l), k * wx * (1 - wu)),
                   (idx(i, l + 1), k * (1 - wx) * wu), (idx(i + 1, l + 1), k * wx * wu),
                   (imu(a), -k * x + s), (iL, -1.0)]
            add_row(ent)
        if d > 0:
            add_row([(imu(a), s), (iL, -1.0)])              # x = 0 inactive point
            add_row([(imu(a), -k * d + s), (iL, -1.0)])     # x = delta^- inactive
    nC1 = rhs_rows
    A1 = coo_matrix((vals, (rows, cols)), shape=(nC1, iL + 1)).tocsr()
    b1 = np.zeros(nC1)
    # trapezoid weights on xi
    w = np.zeros(nxi); dx = np.diff(xi); w[:-1] += dx / 2; w[1:] += dx / 2
    lam_hist = []
    rho = rho0
    G = GridH(k, eps, xi, ug, H)
    lam0, _ = Lambda_fine(G, 200, 200)
    if verbose:
        print(f"k={k} eps={eps}: start Lambda={lam0:.6f} (crude {(1+eps)*k/(k-1)*math.log(k):.6f}); LP rows {nC1}, vars {iL+1}", flush=True)
    best = (lam0, H.copy(), np.zeros(nsig))
    for it in range(iters):
        # (C2) linearised mass rows
        r2, c2, v2 = [], [], []
        for l in range(nu):
            for i in range(nxi):
                r2.append(l); c2.append(idx(i, l)); v2.append(-ug[l] * w[i] / H[i, l] ** 2)
        A2 = coo_matrix((v2, (r2, c2)), shape=(nu, iL + 1)).tocsr()
        b2 = np.array([1.0 - ug[l] * np.sum(w * 2.0 / H[:, l]) for l in range(nu)])
        from scipy.sparse import vstack
        A = vstack([A1, A2]).tocsr(); b = np.concatenate([b1, b2])
        c = np.zeros(iL + 1); c[iL] = 1.0
        bounds = [(H.flat[j] / rho, H.flat[j] * rho) for j in range(nH)] + [(None, None)] * nsig + [(None, None)]
        res = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method="highs")
        if res.status != 0:
            print("LP failed", res.message); break
        Hn = res.x[:nH].reshape(nxi, nu); mu = res.x[nH:nH + nsig]
        # rescale rows to exact unit mass
        for l in range(nu):
            m = row_mass_exact(ug[l], xi, Hn[:, l])
            Hn[:, l] *= m
        G = GridH(k, eps, xi, ug, Hn)
        lam, sarg = Lambda_fine(G, 200, 200)
        lam_hist.append(lam)
        if lam < best[0]:
            best = (lam, Hn.copy(), mu.copy()); H = Hn
        else:
            rho = 1 + (rho - 1) * 0.6   # shrink trust region, keep old H
        if verbose:
            print(f"  it {it}: LP Lambda={res.x[iL]:.6f}  true(fine)={lam:.6f} at sigma={sarg:.3f}  rho={rho:.3f}  best={best[0]:.6f}", flush=True)
        if rho < 1.002:
            break
    lam, Hb, mu = best
    lam_f, sarg = Lambda_fine(GridH(k, eps, xi, ug, Hb), 600, 600)
    return lam_f, sarg, xi, ug, Hb, mu

if __name__ == "__main__":
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    eps_list = [float(e) for e in sys.argv[2].split(",")] if len(sys.argv) > 2 else [0.1]
    nxi = int(sys.argv[3]) if len(sys.argv) > 3 else 48
    nu = int(sys.argv[4]) if len(sys.argv) > 4 else 48
    for eps in eps_list:
        t0 = time.time()
        lam, sarg, xi, ug, H, mu = slp(k, eps, nxi=nxi, nu=nu)
        tag = f"k{k}_e{eps:.4f}_n{nxi}x{nu}"
        np.savez(os.path.join(DATA, f"r1_dualH_{tag}.npz"), k=k, eps=eps, xi=xi, ug=ug, H=H, mu=mu, Lambda=lam)
        print(f"RESULT k={k} eps={eps}: Lambda(fine)={lam:.6f} at sigma={sarg:.4f}; crude={(1+eps)*k/(k-1)*math.log(k):.6f}  [{time.time()-t0:.0f}s]", flush=True)
