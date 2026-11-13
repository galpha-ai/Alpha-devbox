#!/usr/bin/env python3
"""r1_dual_cvx.py -- convex-programme discovery of the optimal fiberwise Schur-test weight for M_{k,eps}
(FLOAT stage; the rigorous interval certification of the resulting weight is r1_sub186_wall.py).

Dual class (Prop. 2 of r1_sub186_wall.md): a density family g(.,u) > 0 on [0,u], int_0^u g <= 1,
H = 1/g, gives  M_{k,eps} <= Lambda := sup_t sum_{i active} H(t_i, u_i),  u_i = 1+eps-sigma+t_i.

ALIGNED GRID.  Spacing h = 2eps/n0.  Fiber lengths u_l = 2eps + l h (l = 0..L, u_L >= 1+eps), positions
x_i = i h (0 <= x_i <= u_l  <=>  i <= n0 + l).  A node (i,l) lies on the slice sigma = 1+eps-u_l+x_i =
1+eps - m h with m = n0 + l - i, so every node lies on exactly one slice sigma_m and every slice's sample
points are exactly its nodes: no interpolation inside the programme.
  mass:   u_l-trapezoid of G[0..n0+l, l] <= 1                       (exact for the pw-linear interpolant)
  slice:  k * inv_pos(G[i,l]) - k mu_m x_i + mu_m sigma_m <= Lambda  for every node (weak Lagrangian duality
          of sup{sum_j g_m(t_j): sum t_j = sigma_m} <= k * concave-envelope(g_m)(sigma_m/k)),
          plus the inactive points x = 0 and x = delta_m^- (value 0).
Convex (inv_pos of a variable); solved with cvxpy/Clarabel.  G is then bilinearly interpolated in (x,u)
and Lambda re-evaluated with the exact concave-envelope slice bound on a fine grid (Lambda_fine).
Output: ../data/r1_dualG_k{k}_e{eps}_h{h}.npz  (x, u grids, G, mu per slice, Lambda_cvx, Lambda_fine).
"""
import sys, os, math, time
import numpy as np
import cvxpy as cp
from r1_dual_lp import hull_value

HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "..", "data")

class GridG:
    """G on the aligned (x,u) grid, bilinear interpolation; H = 1/G."""
    def __init__(self, k, eps, xg, ug, G):
        self.k, self.eps, self.xg, self.ug, self.G = k, eps, xg, ug, G   # G shape (nx, nu); NaN where x > u
    def g(self, x, u):
        x = np.asarray(x, float); u = np.asarray(u, float)
        xg, ug = self.xg, self.ug
        i = np.clip(np.searchsorted(xg, x, side="right") - 1, 0, len(xg) - 2)
        l = np.clip(np.searchsorted(ug, u, side="right") - 1, 0, len(ug) - 2)
        wx = np.clip((x - xg[i]) / (xg[i + 1] - xg[i]), 0, 1); wu = np.clip((u - ug[l]) / (ug[l + 1] - ug[l]), 0, 1)
        G = self.G
        return ((1 - wx) * (1 - wu) * G[i, l] + wx * (1 - wu) * G[i + 1, l]
                + (1 - wx) * wu * G[i, l + 1] + wx * wu * G[i + 1, l + 1])
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

def solve(k, eps, n0=10, verbose=True, solver="CLARABEL", gmin=1e-6):
    h = 2 * eps / n0
    L = int(math.ceil((1 - eps) / h)) + 1          # u_L >= 1+eps
    nu = L + 1; nx = n0 + L + 1
    xg = np.arange(nx) * h; ug = 2 * eps + np.arange(nu) * h
    nodes = [(i, l) for l in range(nu) for i in range(n0 + l + 1)]
    nid = {nd: j for j, nd in enumerate(nodes)}
    N = len(nodes)
    G = cp.Variable(N, pos=True); Lam = cp.Variable()
    mmax = n0 + L
    mu = cp.Variable(mmax + 1)
    cons = [G >= gmin]
    # mass rows: trapezoid on x_0..x_{n0+l} (spacing h) for fiber u_l
    import scipy.sparse as sp
    rows, cols, vals = [], [], []
    for l in range(nu):
        n = n0 + l
        for i in range(n + 1):
            wgt = h * (0.5 if i in (0, n) else 1.0)
            rows.append(l); cols.append(nid[(i, l)]); vals.append(wgt)
    Mmass = sp.coo_matrix((vals, (rows, cols)), shape=(nu, N)).tocsr()
    cons.append(Mmass @ G <= 1)
    # slice rows (one per node): k/G_j - k mu_m x_i + mu_m sigma_m <= Lam
    mj = np.array([n0 + l - i for (i, l) in nodes]); xj = np.array([xg[i] for (i, l) in nodes])
    sigj = 1 + eps - mj * h
    Em = sp.coo_matrix((np.ones(N), (np.arange(N), mj)), shape=(N, mmax + 1)).tocsr()
    cons.append(k * cp.inv_pos(G) + cp.multiply(Em @ mu, sigj - k * xj) <= Lam)
    # inactive points for slices with delta > 0 (m < n0): x=0 and x=delta^-
    ms = np.arange(0, n0); sg = 1 + eps - ms * h; dl = sg - (1 - eps)
    cons.append(cp.multiply(mu[ms], sg) <= Lam)
    cons.append(cp.multiply(mu[ms], sg - k * dl) <= Lam)
    prob = cp.Problem(cp.Minimize(Lam), cons)
    t0 = time.time()
    prob.solve(solver=solver, verbose=False)
    Gm = np.full((nx, nu), np.nan)
    for (i, l), j in nid.items():
        Gm[i, l] = G.value[j]
    # fill x > u entries by the fiber-end value (unused inside the domain; keeps interpolation finite)
    for l in range(nu):
        Gm[n0 + l + 1:, l] = Gm[n0 + l, l]
    GG = GridG(k, eps, xg, ug, Gm)
    lam_f, sarg = Lambda_fine(GG, 400, 400)
    if verbose:
        print(f"k={k} eps={eps} h={h:.4f} nodes={N}: cvx Lambda={Lam.value:.6f}  fine={lam_f:.6f} at sigma={sarg:.4f}  "
              f"crude={(1+eps)*k/(k-1)*math.log(k):.6f}  [{prob.status}, {time.time()-t0:.0f}s]", flush=True)
    return GG, np.array(mu.value), float(Lam.value), lam_f, h

if __name__ == "__main__":
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    eps_list = [float(e) for e in sys.argv[2].split(",")] if len(sys.argv) > 2 else [0.1]
    n0 = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    for eps in eps_list:
        GG, mu, lam, lam_f, h = solve(k, eps, n0=n0)
        np.savez(os.path.join(DATA, f"r1_dualG_k{k}_e{eps:.4f}_n{n0}.npz"), k=k, eps=eps, h=h, xg=GG.xg, ug=GG.ug, G=GG.G, mu=mu, Lambda_cvx=lam, Lambda_fine=lam_f)
