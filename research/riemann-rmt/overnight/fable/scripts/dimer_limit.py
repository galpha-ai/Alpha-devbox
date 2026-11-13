"""Scaled depth N^2 D of the ACUE minimiser family [1^(N-3), a, 1, b] (longest run + isolated dimer), a+b=N+2,
for increasing N, certified by isolated-root classification in ball arithmetic; fit N^2 D = pi^2/8 + c/N + d/N^2."""
import sys, numpy as np
from flint import acb, arb, acb_poly, ctx
ctx.prec = 300
def config_from_gaps(gaps):
    pos = [0]
    for g in gaps[:-1]: pos.append(pos[-1] + g)
    return pos
def survival(sites, N, s):
    zeta = (acb(0, arb.pi()/N)).exp()
    P = acb_poly([1])
    for x in sites: P = P * acb_poly([-(zeta**x), 1])
    lam = arb(s).exp()
    a = [P[j] * lam**(j*(N-j)) for j in range(N+1)]
    try: roots = acb_poly(a).roots()
    except Exception: return None
    if len(roots) != N: return None
    for z in roots:
        if (abs(z) - 1) != 0: return False
    refl = [1/z.conjugate() for z in roots]
    if all((abs(refl[k]-roots[j]) != 0) for k in range(N) for j in range(N) if j != k): return True
    return None
def depth(sites, N, lo=0.0, hi=None, iters=46):
    hi = hi if hi is not None else 3.0/N**2
    assert survival(sites, N, lo) is True and survival(sites, N, hi) is False
    for _ in range(iters):
        mid = (lo+hi)/2; r = survival(sites, N, mid)
        if r is True: lo = mid
        elif r is False: hi = mid
        else: hi = mid  # inconclusive: treat as collided (conservative upper bound), rare
    return (lo+hi)/2
res = []
for N in [int(a) for a in sys.argv[1:]] or [12, 16, 24, 32, 48, 64]:
    a = (N+2)//2; b = N+2-a
    gaps = [1]*(N-3) + [a, 1, b]
    sites = config_from_gaps(gaps)
    D = depth(sites, N); res.append((N, N*N*D))
    print(f"N={N:3d} a,b={a},{b}  N^2 D = {N*N*D:.10f}   excess over pi^2/8 = {N*N*D - np.pi**2/8:.6f}   N*(excess) = {N*(N*N*D-np.pi**2/8):.4f}", flush=True)
Ns = np.array([r[0] for r in res], float); vals = np.array([r[1] for r in res])
A = np.vstack([np.ones_like(Ns), 1/Ns, 1/Ns**2]).T
coef = np.linalg.lstsq(A, vals, rcond=None)[0]
print("fit N^2D = c0 + c1/N + c2/N^2 :", coef, "  pi^2/8 =", np.pi**2/8)
A2 = np.vstack([1/Ns, 1/Ns**2]).T
coef2 = np.linalg.lstsq(A2, vals - np.pi**2/8, rcond=None)[0]
print("fit with c0 fixed at pi^2/8: c1, c2 =", coef2, " residual max", np.abs(A2@coef2 - (vals-np.pi**2/8)).max())
