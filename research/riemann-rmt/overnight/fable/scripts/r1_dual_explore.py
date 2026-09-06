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
    """value at x0 of the concave envelope of the point set {(xs,gs)}: max over chords (x1<=x0<=x2).
    Vectorised O(n^2); exact for the sampled point set."""
    xs = np.asarray(xs); gs = np.asarray(gs)
    L = xs <= x0; R = xs >= x0
    if not L.any() or not R.any():
        return float(gs.max())
    x1 = xs[L][:, None]; g1 = gs[L][:, None]; x2 = xs[R][None, :]; g2 = gs[R][None, :]
    dx = x2 - x1
    with np.errstate(divide='ignore', invalid='ignore'):
        v = np.where(dx > 0, g1 + (g2 - g1) * (x0 - x1) / dx, np.maximum(g1, g2))
    return float(v.max())

class Family:
    """P(x,u) = 1 + alpha(u) * min(x, L)/L,  L = u - b(u)  (linear rise 1 -> 1+alpha on [0,L], flat after);
    mass m(u) = int_0^u dx/P = L log(1+alpha)/alpha + b/(1+alpha);  H = P * m.
    alpha, b piecewise linear in u on unodes.  alpha = k-1, b = 0 is the classical weight."""
    def __init__(self, k, eps, unodes, alphas, bvals):
        self.k, self.eps = k, eps
        self.unodes, self.alphas, self.bvals = unodes, np.asarray(alphas, float), np.asarray(bvals, float)
    def alpha(self, u): return np.interp(u, self.unodes, self.alphas)
    def b(self, u): return np.minimum(np.interp(u, self.unodes, self.bvals), u)
    def mass(self, u):
        al, b = self.alpha(u), self.b(u)
        L = u - b
        return L * np.log1p(al) / al + b / (1 + al)
    def H(self, x, u):
        al, b = self.alpha(u), self.b(u)
        L = np.maximum(u - b, 1e-300)
        P = 1 + al * np.minimum(x, L) / L
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

def optimize(k, eps, nnodes=6, start="plateau", nsig=100, nx=120, maxiter=1500, verbose=True):
    lo = 2 * eps
    unodes = np.linspace(lo, 1 + eps, nnodes)
    if start == "classical":
        al0 = np.full(nnodes, k - 1.0); b0 = np.full(nnodes, 1e-6)
    else:
        al0 = np.full(nnodes, k - 1.0); b0 = np.full(nnodes, 2 * eps)
    x0 = np.concatenate([np.log(al0), np.log(np.maximum(b0, 1e-9) / unodes)])
    def build(x):
        al = np.exp(x[:nnodes]); b = np.exp(x[nnodes:]) * unodes
        return Family(k, eps, unodes, al, np.minimum(b, unodes * 0.9999))
    def obj(x):
        return Lambda(build(x), nsig, nx)[0]
    res = minimize(obj, x0, method="Nelder-Mead", options=dict(maxiter=maxiter, xatol=1e-6, fatol=1e-9, adaptive=True))
    fam = build(res.x)
    val, sarg = Lambda(fam, 4 * nsig, 4 * nx)
    if verbose:
        print(f"  k={k} eps={eps:.4f} start={start}: Lambda={val:.6f} (coarse {res.fun:.6f}) at sigma={sarg:.4f}; "
              f"alpha={np.round(fam.alphas,2)} b={np.round(fam.bvals,4)}", flush=True)
    return val, fam

if __name__ == "__main__":
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    eps_list = [float(e) for e in sys.argv[2].split(",")] if len(sys.argv) > 2 else [0.03, 0.06, 0.1, 0.15, 0.25, 0.5, 0.8]
    for eps in eps_list:
        crude = (1 + eps) * k / (k - 1) * math.log(k)
        un = np.array([2 * eps, 1 + eps]); fam0 = Family(k, eps, un, [k - 1, k - 1], [0, 0])
        v0, s0 = Lambda(fam0, 200, 200)
        fam1 = Family(k, eps, un, [k - 1, k - 1], [2 * eps, 2 * eps])
        v1, s1 = Lambda(fam1, 200, 200)
        print(f"k={k} eps={eps}: crude={crude:.6f} classical-member={v0:.6f} (sigma={s0:.3f}) plateau-member={v1:.6f} (sigma={s1:.3f})", flush=True)
        t0 = time.time()
        best = None
        for st in ("plateau", "classical"):
            val, fam = optimize(k, eps, start=st)
            if best is None or val < best[0]:
                best = (val, fam)
        print(f"  ==> best Lambda = {best[0]:.6f}   [{time.time()-t0:.0f}s]", flush=True)
