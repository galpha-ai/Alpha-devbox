"""Pattern-only variant of fibre_lp.py (interior point first): max range over the POSITIVE moment fibre of the
probabilities of all occupation patterns of w consecutive sites, w in WIDTHS, at the N given on the command line.
Written for N = 9, where the dual simplex needed ~5 min per LP and the width-4 sweep did not fit the background
time limit; the interior-point method needs ~100 s per LP there and reproduces the N = 8 simplex values."""
import itertools, sys, time, numpy as np
from scipy.optimize import linprog
from math import factorial
from collections import Counter
def partitions(n, m=None):
    if m is None: m = n
    if n == 0: yield (); return
    for f in range(min(n, m), 0, -1):
        for rest in partitions(n - f, f): yield (f,) + rest
def zlam(lam):
    z = 1
    for r, m in Counter(lam).items(): z *= r**m * factorial(m)
    return z
OPTS = {'primal_feasibility_tolerance': 1e-9, 'dual_feasibility_tolerance': 1e-9}
N = int(sys.argv[1]); WIDTHS = tuple(int(w) for w in sys.argv[2:]) or (4,)
M = 2*N
orbits = {}
for Sx in itertools.combinations(range(M), N):
    key = min(tuple(sorted((x + r) % M for x in Sx)) for r in range(M))
    orbits.setdefault(key, []).append(Sx)
reps = list(orbits)
zeta = np.exp(1j*np.pi/N)
PK = {k: np.array([sum(zeta**(k*x) for x in r) for r in reps]) for k in range(1, N+1)}
rows, rhs = [], []
rows.append(np.ones(len(reps))); rhs.append(1.0)
for d in range(1, N+1):
    P = list(partitions(d))
    prod = {lam: np.prod([PK[a] for a in lam], axis=0) for lam in P}
    for lam in P:
        for mu in P:
            obs = prod[lam]*np.conj(prod[mu]); tgt = zlam(lam) if lam == mu else 0.0
            sc = max(1.0, np.abs(obs).max())
            rows.append(obs.real/sc); rhs.append(tgt/sc)
            if np.abs(obs.imag).max() > 1e-12: rows.append(obs.imag/sc); rhs.append(0.0)
A = np.array(rows); b = np.array(rhs)
U, sv, Vt = np.linalg.svd(A, full_matrices=False)
r = int((sv > 1e-9*sv[0]).sum())
A, b = U[:, :r].T @ A, U[:, :r].T @ b
tab = np.abs(zeta**np.arange(M)[:,None] - zeta**np.arange(M)[None,:])**2
def wt(Sx):
    w = 1.0
    for i in range(N):
        for j in range(i+1, N): w *= tab[Sx[i], Sx[j]]
    return w
acue = np.array([wt(r)*len(orbits[r]) for r in reps]); acue /= acue.sum()
print(f"N={N}: orbits {len(reps)}, constraint rank {A.shape[0]}, ACUE residual {np.abs(A@acue-b).max():.1e}", flush=True)
def solve(f, sign, tag):
    for method in ('highs-ipm', 'highs'):
        t0 = time.time()
        res = linprog(sign*f, A_eq=A, b_eq=b, bounds=(0, None), method=method, options=OPTS)
        resid = np.abs(A@res.x - b).max() if res.status == 0 else float('nan')
        print(f"      [{tag} {method} sign {sign:+d}: {time.time()-t0:.1f}s status {res.status} residual {resid:.1e}]", flush=True)
        if res.status == 0: return sign*res.fun
    return float('nan')
for width in WIDTHS:
    worst = (-1.0, None, None)
    for pat in itertools.product([0,1], repeat=width):
        f = np.array([np.mean([all(((x in Sx) == bool(pat[i])) for i, x in enumerate(range(width))) for Sx in orbits[r]]) for r in reps])
        if (acue@f) < 1e-9: continue
        tag = ''.join(map(str, pat))
        lo = solve(f, 1, tag); hi = solve(f, -1, tag)
        print(f"   pattern {tag}: ACUE {float(acue@f):.6f}  range [{lo:.6f}, {hi:.6f}]  width {hi-lo:.2e}", flush=True)
        if hi-lo > worst[0]: worst = (hi-lo, pat, (float(acue@f), lo, hi))
    print(f"   width {width}: max range over patterns = {worst[0]:.2e}  at {''.join(map(str,worst[1]))}: ACUE {worst[2][0]:.5f}, range [{worst[2][1]:.5f}, {worst[2][2]:.5f}]", flush=True)
