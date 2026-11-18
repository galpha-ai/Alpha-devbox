"""r2_lr_pair_lp.py -- pair-positivity-only LP relaxation of the Lagarias-Rodgers hard core mu.

Setting (recalled, not verified online).  X stationary point process on R, intensity 1, reduced pair
correlation g (a nonnegative even measure; E sum_{x!=y in X} f(x-y) = int f g).  Bandwidth-one sine
mimicry: the Bartlett spectrum S = 1 + FT(g - 1) equals |alpha| on (-1,1) (sine process:
g = 1 - sinc^2, S = min(|alpha|,1)).  Hard core c: g = 0 on (-c,c).  Bochner: S >= 0 everywhere.

Pair LP(c):  find g >= 0 on |x| >= c,  S = |alpha| on [0,1),  S >= 0 on [1,A].
c_LP = sup{c : LP(c) feasible}  (an upper bound on mu, if the discretisation is controlled).

Parametrisation: g = g_sine + u with u a signed measure supported in [0,X] (even), so the 1/x^2
tail responsible for the |alpha| kink is carried exactly by g_sine and u is compactly supported.
Then S = min(|alpha|,1) + uhat, constraints  uhat = 0 on [0,1),  uhat >= -1 on [1,A],
u = -g_sine on [0,c),  u >= -g_sine on [c,X],  u = 0 beyond X.  u piecewise constant on cells of
width dx starting at c.  Feasibility measured by the minimal slack s* (LP: minimise s).

Usage: python3 r2_lr_pair_lp.py [X dx A dalpha]   (defaults 8 0.01 12 0.01)
Outputs a bisection on c and a convergence table; writes data/r2_lr_pair_lp_*.json.
"""
import sys, json, time
import numpy as np
from scipy.optimize import linprog
from scipy.integrate import quad

def gsine(x):
    x = np.asarray(x, float)
    with np.errstate(divide='ignore', invalid='ignore'):
        s = np.where(x == 0, 1.0, np.sin(np.pi*x)/(np.pi*x))
    return 1.0 - s*s

def cell_cos(a, b, alpha):
    """int_a^b cos(2 pi alpha x) dx for arrays a,b (cells) and scalar alpha."""
    if alpha == 0:
        return b - a
    return (np.sin(2*np.pi*alpha*b) - np.sin(2*np.pi*alpha*a))/(2*np.pi*alpha)

def K_core(c, alphas):
    """K(alpha) = 2 int_0^c g_sine(x) cos(2 pi alpha x) dx  (the forced part u=-g_sine on [0,c))."""
    out = np.empty(len(alphas))
    for i, al in enumerate(alphas):
        out[i] = 2*quad(lambda x: gsine(x)*np.cos(2*np.pi*al*x), 0, c, limit=200, epsabs=1e-13)[0]
    return out

def build(c, X, dx, A, dal):
    edges = c + dx*np.arange(0, int(np.ceil((X - c)/dx)) + 1)
    a, b = edges[:-1], edges[1:]
    ncell = len(a)
    alphas = np.round(np.arange(0, A + 1e-12, dal), 12)
    eq = alphas < 1 - 1e-12
    C = np.array([2*cell_cos(a, b, al) for al in alphas])     # rows: alpha, cols: cells
    K = K_core(c, alphas)
    # lower bounds for u: u_j >= -min_cell g_sine (conservative: keeps g >= 0 pointwise)
    xs = np.linspace(0, 1, 9)
    gmin = np.min(np.array([gsine(a + t*(b - a)) for t in xs]), axis=0)
    return dict(a=a, b=b, C=C, K=K, eq=eq, alphas=alphas, lb=-gmin, ncell=ncell)

def solve(c, X, dx, A, dal, want_dual=False):
    B = build(c, X, dx, A, dal)
    C, K, eq, lb = B['C'], B['K'], B['eq'], B['lb']
    n = B['ncell']
    # variables: u (n), s (1).  minimise s.
    # equality rows (as two inequalities): C u - K <= s ; -(C u - K) <= s
    # inequality rows: C u >= K - 1 - s  ->  -C u - s <= 1 - K
    Ce, Ke = C[eq], K[eq]
    Ci, Ki = C[~eq], K[~eq]
    A_ub = np.vstack([np.hstack([Ce, -np.ones((Ce.shape[0], 1))]),
                      np.hstack([-Ce, -np.ones((Ce.shape[0], 1))]),
                      np.hstack([-Ci, -np.ones((Ci.shape[0], 1))])])
    b_ub = np.concatenate([Ke, -Ke, 1 - Ki])
    cost = np.zeros(n + 1); cost[-1] = 1.0
    bounds = [(lb[j], None) for j in range(n)] + [(0, None)]
    res = linprog(cost, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs',
                  options=dict(presolve=True, dual_feasibility_tolerance=1e-9,
                               primal_feasibility_tolerance=1e-9))
    out = dict(s=res.fun if res.status == 0 else np.inf, status=res.status, u=None)
    if res.status == 0:
        out['u'] = res.x[:n]
        if want_dual:
            out['dual_ub'] = res.ineqlin.marginals
            out['B'] = B
    return out

def bisect(X, dx, A, dal, lo=0.5, hi=0.75, tol_s=1e-7, iters=22, verbose=True):
    t0 = time.time()
    for it in range(iters):
        mid = 0.5*(lo + hi)
        r = solve(mid, X, dx, A, dal)
        feas = r['s'] <= tol_s
        if verbose:
            print(f"  c={mid:.7f}  s*={r['s']:.3e}  {'feasible' if feas else 'INFEASIBLE'}  ({time.time()-t0:.1f}s)", flush=True)
        if feas: lo = mid
        else: hi = mid
        if hi - lo < 2e-7: break
    return lo, hi

if __name__ == "__main__":
    args = [float(v) for v in sys.argv[1:]]
    X, dx, A, dal = (args + [8, 0.01, 12, 0.01][len(args):])[:4]
    print(f"pair LP: X={X} dx={dx} A={A} dalpha={dal}")
    # sanity: c = 0.5 must be feasible, c = 0.75 should not
    for c in (0.5, 0.6, 0.65, 0.75):
        r = solve(c, X, dx, A, dal)
        print(f"  probe c={c}: s*={r['s']:.3e}")
    lo, hi = bisect(X, dx, A, dal)
    print(f"RESULT X={X} dx={dx} A={A} dalpha={dal}:  c_LP in [{lo:.6f}, {hi:.6f}]")
    json.dump(dict(X=X, dx=dx, A=A, dalpha=dal, c_lo=lo, c_hi=hi),
              open(f"/home/user/Alpha-devbox/research/riemann-rmt/overnight/fable/data/r2_lr_pair_lp_X{X}_dx{dx}_A{A}_da{dal}.json", "w"), indent=1)
