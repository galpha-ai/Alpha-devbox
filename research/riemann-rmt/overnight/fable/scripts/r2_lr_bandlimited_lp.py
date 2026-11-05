"""r2_lr_bandlimited_lp.py -- the general bandwidth-one-only certificate LP (no Bochner outside [-1,1]).

Certificates: even T with supp That = phi in [-1,1] and T <= 0 on |x| >= c.  For a hard-core-c
process E sum_{x!=y} T(x-y) <= 0, but mimicry fixes it to  int T g_sine = J(phi) :=
phi(0) - T(0) + 2 int_0^1 a phi(a) da.  So J_max(c) > 0  ==>  no hard core c.
phi piecewise linear on knots k/n, phi(1)=0 (else T ~ sin(2 pi x)/x oscillates), |phi_k| <= 1.
T(x) = -(2/(2 pi x)^2) sum_k phi'_k [cos(2 pi a_k x) - cos(2 pi a_{k+1} x)]  (exact), imposed <= 0
on a grid of [c, Xfar].  Caveat (documented in the report): a piecewise-linear phi makes x^2 T(x)
periodic, so T <= 0 on ALL of [c,inf) would force T <= 0 everywhere and no certificate; the LP value
therefore approaches the true sup only as n, Xfar -> inf, and the tail beyond Xfar is bounded by
M_T/x^2 with M_T = (1/pi^2) sum_k |phi'_k|.  A rigorous version adds the tail penalty
tau = M_T (1/c + 1)/(Xfar - 1)  (hard core => at most 1/c+1 points per unit interval).
Usage: python3 r2_lr_bandlimited_lp.py n Xfar h [penalty]
"""
import sys, time, json
import numpy as np
from scipy.optimize import linprog

def build(n, c, Xfar, h):
    ak = np.arange(n + 1)/n
    xs = np.arange(c, Xfar + 1e-12, h)
    # T(x) = sum_k phi_k B_k(x);  phi'_k = n (phi_{k+1} - phi_k) on piece k (k = 0..n-1)
    # contribution of piece k:  -(2/(2 pi x)^2) * n (phi_{k+1}-phi_k) [cos(2 pi a_k x) - cos(2 pi a_{k+1} x)]
    X2 = (2*np.pi*xs)**2
    D = np.cos(2*np.pi*np.outer(xs, ak))                 # cos(2 pi a_k x)
    piece = -(2/X2)[:, None]*n*(D[:, :-1] - D[:, 1:])     # coefficient of (phi_{k+1}-phi_k), k=0..n-1
    B = np.zeros((len(xs), n + 1))
    B[:, 1:] += piece
    B[:, :-1] -= piece
    # objective J = phi_0 - T(0) + 2 int_0^1 a phi ; T(0) = 2 int phi = (2/n)(sum phi_k - phi_0/2 - phi_n/2)
    # int_0^1 a phi = sum_k (1/(6n)) [a_k(2 phi_k + phi_{k+1}) + a_{k+1}(phi_k + 2 phi_{k+1})]
    J = np.zeros(n + 1)
    J[0] += 1.0
    J -= 2.0/n; J[0] += 1.0/n; J[n] += 1.0/n
    for k in range(n):
        J[k] += 2*(2*ak[k] + ak[k+1])/(6*n)
        J[k+1] += 2*(ak[k] + 2*ak[k+1])/(6*n)
    return B, J

def jmax(n, c, Xfar, h, penalty=False):
    B, J = build(n, c, Xfar, h)
    nv = n + 1
    if not penalty:
        cost = -J
        A_ub, b_ub = B, np.zeros(B.shape[0])
        bounds = [(-1, 1)]*nv; bounds[n] = (0, 0)
        res = linprog(cost, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
        return -res.fun, res.x[:nv]
    # with tail penalty.  Exact representation (two integrations by parts, phi(1)=0):
    #   T(x) = -(2/(2 pi x)^2) [ phi'(0+) - phi'(1-) cos(2 pi x) + sum_{k=1}^{n-1} s_k cos(2 pi a_k x) ],
    #   s_k = phi'_k - phi'_{k-1} = n (phi_{k+1} - 2 phi_k + phi_{k-1}),
    # so |T(x)| <= M_T / x^2 with M_T = (1/(2 pi^2)) [ |phi'_0| + |phi'_{n-1}| + sum |s_k| ].
    # Hard core c => at most 1/c + 1 points per unit interval, so the tail loss is
    #   int_{Xfar}^inf g T <= M_T (1/c + 1) sum_{m>=0} 1/(Xfar+m)^2 <= M_T (1/c+1)/(Xfar-1) =: tau.
    # variables: phi (nv), d (n+1) with d_0 >= |phi'_0|, d_n >= |phi'_{n-1}|, d_k >= |s_k| (1<=k<=n-1)
    nd = n + 1
    coef = (1/(2*np.pi**2))*(1/c + 1)/(Xfar - 1)
    cost = np.concatenate([-J, np.full(nd, coef)])
    A1 = np.hstack([B, np.zeros((B.shape[0], nd))])
    Dm = np.zeros((nd, nv))
    Dm[0, 1] = n; Dm[0, 0] = -n                      # phi'_0
    Dm[n, n] = n; Dm[n, n-1] = -n                    # phi'_{n-1}
    for k in range(1, n):
        Dm[k, k+1] = n; Dm[k, k] = -2*n; Dm[k, k-1] = n
    A2 = np.hstack([Dm, -np.eye(nd)]); A3 = np.hstack([-Dm, -np.eye(nd)])
    A_ub = np.vstack([A1, A2, A3]); b_ub = np.zeros(A_ub.shape[0])
    bounds = [(-1, 1)]*nv + [(0, None)]*nd; bounds[n] = (0, 0)
    res = linprog(cost, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    return -res.fun, res.x[:nv]

if __name__ == "__main__":
    n, Xfar, h = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
    pen = len(sys.argv) > 4 and sys.argv[4] == 'penalty'
    t0 = time.time()
    for c in (0.55, 0.6, 0.606894, 0.61, 0.62, 0.65):
        v, _ = jmax(n, c, Xfar, h, pen)
        print(f"n={n} Xfar={Xfar} h={h} pen={pen}  c={c:.6f}  J_max={v:+.6e}  ({time.time()-t0:.0f}s)", flush=True)
    lo, hi = 0.5, 0.7
    for _ in range(25):
        mid = 0.5*(lo + hi)
        v, _ = jmax(n, mid, Xfar, h, pen)
        if v > 1e-9: hi = mid
        else: lo = mid
    print(f"c_bandlimited(n={n},Xfar={Xfar},h={h},pen={pen}) = {0.5*(lo+hi):.7f}   [target 0.606894]")
    v, phi = jmax(n, 0.5*(lo+hi) + 0.002, Xfar, h, pen)
    json.dump(dict(n=n, Xfar=Xfar, h=h, penalty=pen, c=0.5*(lo+hi), phi=phi.tolist()),
              open(f"/home/user/Alpha-devbox/research/riemann-rmt/overnight/fable/data/r2_lr_bandlimited_n{n}_X{Xfar}_h{h}_pen{int(pen)}.json", "w"))
