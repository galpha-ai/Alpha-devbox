#!/usr/bin/env python3
"""r1_dual_explore.py -- FLOAT exploration of the fiberwise Schur-test (Cauchy-Schwarz) upper bound
for the epsilon-trick constant M_{k,eps}; the rigorous interval version is r1_sub186_wall.py.

Dual principle (rigorous; proof in r1_sub186_wall.md):
  For any family H(x,u) > 0 (u = fiber length in [2eps, 1+eps], x in [0,u]) with
  int_0^u dx / H(x,u) <= 1 for every u,
      M_{k,eps} <= Lambda := sup_{t in (1+eps)R_k} sum_{i active} H(t_i, u_i),
  u_i = 1+eps-sigma+t_i (sigma = sum_j t_j), fiber i active <=> sigma - t_i <= 1-eps <=> u_i >= 2eps.
Slice reduction: fix sigma; g(x) := H(x, 1+eps-sigma+x) 1[x >= delta], delta = max(0, sigma-(1-eps));
  sup{ sum_i g(t_i) : t_i >= 0, sum t_i = sigma } <= k * ghat(sigma/k),  ghat = concave envelope on [0,sigma].
Family (plateau-linear):  P(x,u) = 1 + a(u) min(x, u-b(u)),  H = P * m(u),  m(u) = int_0^u dx/P
  (closed form), a,b piecewise-linear in u on nodes.  b = 0, a = (k-1)/u is the classical weight
  (Lambda = (1+eps) k log k/(k-1)); b ~ 2 eps imitates the true eigenfunction's flat outer stretch.
"""
import sys, os, math, json, time
import numpy as np
from scipy.optimize import minimize

def upper_hull_value(xs, gs, x0):
    """value at x0 of the concave envelope of the point set {(xs,gs)} (xs sorted ascending)."""
    hull = []
    for x, g in zip(xs, gs):
        while len(hull) >= 2:
            (x1, g1), (x2, g2) = hull[-2], hull[-1]
            # remove hull[-1] if it lies below chord (x1,g1)-(x,g)
            if (g2 - g1) * (x - x1) <= (g - g1) * (x2 - x1):
                hull.pop()
            else:
                break
        hull.append((x, g))
    hx = np.array([h[0] for h in hull]); hg = np.array([h[1] for h in hull])
    if x0 <= hx[0]:
        return hg[0]
    if x0 >= hx[-1]:
        return hg[-1]
    return float(np.interp(x0, hx, hg))

class Family:
    def __init__(self, k, eps, unodes, avals, bvals):
        self.k, self.eps = k, eps
        self.unodes, self.avals, self.bvals = unodes, avals, bvals
    def a(self, u): return np.interp(u, self.unodes, self.avals)
    def b(self, u): return np.minimum(np.interp(u, self.unodes, self.bvals), u)
    def mass(self, u):
        a, b = self.a(u), self.b(u)
        L = u - b
        return np.log1p(a * L) / a + b / (1 + a * L)
    def H(self, x, u):
        a, b = self.a(u), self.b(u)
        P = 1 + a * np.minimum(x, u - b)
        return P * self.mass(u)

def slice_bound(fam, sigma, nx=400):
    k, eps = fam.k, fam.eps
    if sigma <= 0:
        return k * fam.H(0.0, 1 + eps)
    delta = max(0.0, sigma - (1 - eps))
    xs = np.linspace(delta, sigma, nx)
    us = 1 + eps - sigma + xs
    gs = fam.H(xs, us)
    if delta > 0:
        xs = np.concatenate([[0.0], xs]); gs = np.concatenate([[0.0], gs])
    return k * upper_hull_value(xs, gs, sigma / k)

def Lambda(fam, nsig=300, nx=300):
    sigs = np.linspace(0, 1 + fam.eps, nsig)
    vals = [slice_bound(fam, s, nx) for s in sigs]
    i = int(np.argmax(vals))
    return vals[i], sigs[i]

def optimize(k, eps, nnodes=6, start="plateau", nsig=120, nx=160, maxiter=2500, verbose=True):
    lo = 2 * eps
    unodes = np.linspace(lo, 1 + eps, nnodes)
    if start == "classical":
        a0 = (k - 1) / unodes; b0 = np.zeros(nnodes) + 1e-9
    else:
        a0 = (k - 1) / np.maximum(unodes - 2 * eps, 1e-3); b0 = np.full(nnodes, 2 * eps)
    x0 = np.concatenate([np.log(a0), np.log(np.maximum(b0, 1e-9) / unodes)])
    def build(x):
        a = np.exp(x[:nnodes]); b = np.exp(x[nnodes:]) * unodes
        return Family(k, eps, unodes, a, np.minimum(b, unodes * 0.999))
    def obj(x):
        return Lambda(build(x), nsig, nx)[0]
    res = minimize(obj, x0, method="Nelder-Mead", options=dict(maxiter=maxiter, xatol=1e-6, fatol=1e-9, adaptive=True))
    fam = build(res.x)
    val, sarg = Lambda(fam, 4 * nsig, 4 * nx)
    if verbose:
        print(f"  k={k} eps={eps:.4f} start={start}: Lambda={val:.6f} (coarse {res.fun:.6f}) at sigma={sarg:.4f}; "
              f"a={np.round(fam.avals,2)} b={np.round(fam.bvals,4)}", flush=True)
    return val, fam

if __name__ == "__main__":
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    eps_list = [float(e) for e in sys.argv[2].split(",")] if len(sys.argv) > 2 else [0.03, 0.06, 0.1, 0.15, 0.25, 0.5, 0.8]
    for eps in eps_list:
        crude = (1 + eps) * k / (k - 1) * math.log(k)
        # sanity: classical member reproduces the crude bound
        un = np.array([2 * eps, 1 + eps]); fam0 = Family(k, eps, un, (k - 1) / un, np.zeros(2))
        v0, _ = Lambda(fam0, 200, 200)
        # plateau member with b = 2eps, a=(k-1)/(u-2eps)
        un = np.linspace(2 * eps, 1 + eps, 6); fam1 = Family(k, eps, un, (k - 1) / np.maximum(un - 2 * eps, 1e-3), np.full(6, 2 * eps))
        v1, s1 = Lambda(fam1, 200, 200)
        print(f"k={k} eps={eps}: crude={crude:.6f} classical-member={v0:.6f} plateau-member={v1:.6f} (sigma={s1:.3f})", flush=True)
        t0 = time.time()
        best = None
        for st in ("plateau", "classical"):
            val, fam = optimize(k, eps, start=st)
            if best is None or val < best[0]:
                best = (val, fam)
        print(f"  ==> best Lambda = {best[0]:.6f}   [{time.time()-t0:.0f}s]", flush=True)
