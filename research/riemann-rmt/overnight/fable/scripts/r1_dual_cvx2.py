#!/usr/bin/env python3
"""r1_dual_cvx2.py -- convex-programme discovery of the optimal fiberwise Schur-test weight for M_{k,eps}
(FLOAT stage; the rigorous interval certification of the resulting weight is r1_sub186_wall.py).

Dual class (Prop. 2 of r1_sub186_wall.md): densities g(.,u) > 0 on [0,u] with int_0^u g <= 1, H = 1/g:
      M_{k,eps} <= Lambda := sup_t sum_{i active} H(t_i, u_i),  u_i = 1+eps-sigma+t_i, active <=> u_i >= 2eps.
Grid: G(xi,u), xi = x/u, on a WARPED xi-grid xi_i = (k^{y_i}-1)/(k-1), y_i uniform in [0,1] (uniform in the
classical weight's cumulative mass, so the hyperbolic base profile 1/(u+(k-1)x) is resolved), u uniform in
[2eps, 1+eps]; bilinear interpolation in (xi,u).  Mass = trapezoid in xi (exact for the interpolant).
Slice constraints (Lagrangian form, mu shared along a slice): for EVERY grid node (xi_i,u_l) the slice
sigma_il = 1+eps-u_l(1-xi_i) through it is sampled at nxc points x in [delta, sigma] (interpolated G) plus
the node itself, plus the inactive points x = 0, delta^-:
      k * inv_pos(G_interp(x, 1+eps-sigma+x)) - k mu x + mu sigma <= Lambda.
Convex; solved with cvxpy/Clarabel.  Lambda is then re-evaluated on a fine grid with the exact
concave-envelope slice bound (Lambda_fine).  Output: ../data/r1_dualG2_k{k}_e{eps}.npz
"""
import sys, os, math, time
import numpy as np
import cvxpy as cp
import scipy.sparse as sp
from r1_dual_lp import hull_value

HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "..", "data")

class GridG:
    def __init__(self, k, eps, xi, ug, G):
        self.k, self.eps, self.xi, self.ug, self.G = k, eps, np.asarray(xi), np.asarray(ug), G
    def weights(self, x, u):
        x = np.asarray(x, float); u = np.asarray(u, float)
        xiv = np.clip(x / np.maximum(u, 1e-300), 0, 1)
        i = np.clip(np.searchsorted(self.xi, xiv, side="right") - 1, 0, len(self.xi) - 2)
        l = np.clip(np.searchsorted(self.ug, u, side="right") - 1, 0, len(self.ug) - 2)
        wx = np.clip((xiv - self.xi[i]) / (self.xi[i + 1] - self.xi[i]), 0, 1)
        wu = np.clip((u - self.ug[l]) / (self.ug[l + 1] - self.ug[l]), 0, 1)
        return i, l, wx, wu
    def g(self, x, u):
        i, l, wx, wu = self.weights(x, u); G = self.G
        return ((1 - wx) * (1 - wu) * G[i, l] + wx * (1 - wu) * G[i + 1, l] + (1 - wx) * wu * G[i, l + 1] + wx * wu * G[i + 1, l + 1])
    def H(self, x, u):
        return 1.0 / self.g(x, u)

def Lambda_fine(GG, nsig=400, nx=400):
    k, eps = GG.k, GG.eps
    best, arg = -1, None
    for s in np.linspace(0, 1 + eps, nsig):
        if s <= 0:
            v = k * GG.H(0.0, 1 + eps)
        else:
            d = max(0.0, s - (1 - eps))
            xs = np.linspace(d, s, nx); gs = GG.H(xs, 1 + eps - s + xs)
            if d > 0:
                xs = np.concatenate([[0.0], xs]); gs = np.concatenate([[0.0], gs])
            v = k * hull_value(xs, gs, s / k)
        if v > best:
            best, arg = v, s
    return best, arg

def classical_G(k, xi, ug):
    return np.outer((k - 1) / (1 + (k - 1) * xi), 1.0 / ug) / math.log(k)

def solve(k, eps, nxi=36, nu=30, nxc=36, verbose=True, solver="CLARABEL", gmin_rel=0.02, warp=True):
    y = np.linspace(0, 1, nxi)
    xi = (k ** y - 1) / (k - 1) if warp else y
    ug = np.linspace(2 * eps, 1 + eps, nu)
    nG = nxi * nu
    idx = lambda i, l: i * nu + l
    Gcl = classical_G(k, xi, ug)
    G = cp.Variable(nG, pos=True); Lam = cp.Variable(); mu = cp.Variable(nG)
    cons = [G >= gmin_rel * Gcl.flatten()]
    # mass
    w = np.zeros(nxi); dx = np.diff(xi); w[:-1] += dx / 2; w[1:] += dx / 2
    rows, cols, vals = [], [], []
    for l in range(nu):
        for i in range(nxi):
            rows.append(l); cols.append(idx(i, l)); vals.append(ug[l] * w[i])
    cons.append(sp.coo_matrix((vals, (rows, cols)), shape=(nu, nG)).tocsr() @ G <= 1)
    # slices through every node
    tmp = GridG(k, eps, xi, ug, None)
    rows, cols, vals, rmu, coef = [], [], [], [], []
    r = 0
    ina_mu, ina_coef = [], []
    for l in range(nu):
        for i in range(nxi):
            s = 1 + eps - ug[l] * (1 - xi[i]); a = idx(i, l)
            d = max(0.0, s - (1 - eps))
            xs = np.unique(np.concatenate([np.linspace(d, s, nxc), [xi[i] * ug[l]]])) if s > 0 else np.array([0.0])
            us = 1 + eps - s + xs
            ii, ll, wx, wu = tmp.weights(xs, us)
            for q in range(len(xs)):
                for c, v in [(idx(ii[q], ll[q]), (1 - wx[q]) * (1 - wu[q])), (idx(ii[q] + 1, ll[q]), wx[q] * (1 - wu[q])),
                             (idx(ii[q], ll[q] + 1), (1 - wx[q]) * wu[q]), (idx(ii[q] + 1, ll[q] + 1), wx[q] * wu[q])]:
                    if v > 0:
                        rows.append(r); cols.append(c); vals.append(v)
                rmu.append(a); coef.append(s - k * xs[q]); r += 1
            if d > 0:
                ina_mu += [a, a]; ina_coef += [s, s - k * d]
    A = sp.coo_matrix((vals, (rows, cols)), shape=(r, nG)).tocsr()
    Em = sp.coo_matrix((np.ones(r), (np.arange(r), rmu)), shape=(r, nG)).tocsr()
    cons.append(k * cp.inv_pos(A @ G) + cp.multiply(Em @ mu, np.array(coef)) <= Lam)
    if ina_mu:
        Ei = sp.coo_matrix((np.ones(len(ina_mu)), (np.arange(len(ina_mu)), ina_mu)), shape=(len(ina_mu), nG)).tocsr()
        cons.append(cp.multiply(Ei @ mu, np.array(ina_coef)) <= Lam)
    prob = cp.Problem(cp.Minimize(Lam), cons)
    t0 = time.time()
    prob.solve(solver=solver, verbose=False)
    Gv = np.array(G.value).reshape(nxi, nu)
    GG = GridG(k, eps, xi, ug, Gv)
    lam_f, sarg = Lambda_fine(GG, 300, 300)
    # sanity: classical member value on this grid
    if verbose:
        lam_cl, _ = Lambda_fine(GridG(k, eps, xi, ug, Gcl), 200, 200)
        print(f"k={k} eps={eps} grid {nxi}x{nu} rows={r}: cvx Lambda={Lam.value:.6f}  fine={lam_f:.6f} (sigma={sarg:.4f})  "
              f"classical-on-grid={lam_cl:.6f}  crude={(1+eps)*k/(k-1)*math.log(k):.6f}  [{prob.status}, {time.time()-t0:.0f}s]", flush=True)
    return GG, np.array(mu.value).reshape(nxi, nu), float(Lam.value), lam_f

if __name__ == "__main__":
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    eps_list = [float(e) for e in sys.argv[2].split(",")] if len(sys.argv) > 2 else [0.1]
    nxi = int(sys.argv[3]) if len(sys.argv) > 3 else 36
    nu = int(sys.argv[4]) if len(sys.argv) > 4 else 30
    for eps in eps_list:
        GG, mu, lam, lam_f = solve(k, eps, nxi=nxi, nu=nu)
        np.savez(os.path.join(DATA, f"r1_dualG2_k{k}_e{eps:.4f}_n{nxi}x{nu}.npz"), k=k, eps=eps, xi=GG.xi, ug=GG.ug, G=GG.G, mu=mu, Lambda_cvx=lam, Lambda_fine=lam_f)
