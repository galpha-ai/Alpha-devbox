"""Range of local statistics over the POSITIVE moment fibre (rotation-invariant laws on the ACUE support
matching all balanced moments of degree <= N), by LP. Statistics: width-3 window patterns, survival P(N^2 D > t),
and the Nyquist row E|p_N|^2/N (forced = 1 for simple points by the conservation law)."""
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
PUSH = '/home/user/Alpha-devbox/research/riemann-rmt/overnight/fable/push/'
for N in [int(a) for a in sys.argv[1:]] or [6, 7, 8, 9, 10]:
    M = 2*N
    # rotation orbits keyed by canonical cyclic gap tuple
    orbits = {}
    for Sx in itertools.combinations(range(M), N):
        key = min(tuple(sorted((x + r) % M for x in Sx)) for r in range(M))
        orbits.setdefault(key, []).append(Sx)
    reps = list(orbits)
    def gapkey(Sx):
        s = sorted(Sx); g = tuple((s[(i+1) % N] - s[i]) % M for i in range(N))
        return min(g[i:] + g[:i] for i in range(N))
    npz = np.load(PUSH + f'acue_depth_N{N}.npz', allow_pickle=True)
    Dmap = {}
    for i in range(len(npz['D'])):
        g = tuple(int(x) for x in npz['gaps'][i]); Dmap[min(g[j:] + g[:j] for j in range(N))] = float(npz['D'][i])
    depth = np.array([N*N*Dmap[gapkey(r)] for r in reps])
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
    # reduce the (highly redundant) equality system to an orthonormal row basis so HiGHS sees a consistent full-rank system
    U, sv, Vt = np.linalg.svd(A, full_matrices=False)
    r = int((sv > 1e-9*sv[0]).sum())
    A, b = U[:, :r].T @ A, U[:, :r].T @ b
    print(f"   constraint rank {r}", flush=True)
    # ACUE mass per orbit (feasibility check)
    tab = np.abs(zeta**np.arange(M)[:,None] - zeta**np.arange(M)[None,:])**2
    def wt(Sx):
        w = 1.0
        for i in range(N):
            for j in range(i+1, N): w *= tab[Sx[i], Sx[j]]
        return w
    acue = np.array([wt(r)*len(orbits[r]) for r in reps]); acue /= acue.sum()
    print(f"N={N}: orbits {len(reps)}, constraint rows {A.shape[0]}, ACUE residual {np.abs(A@acue-b).max():.1e}")
    def frange(f, label):
        out = []
        for sign in (1, -1):
            r = linprog(sign*f, A_eq=A, b_eq=b, bounds=(0, None), method='highs', options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
            out.append(sign*r.fun if r.status == 0 else float('nan')); (r.status == 0) or print('      LP status', r.status, r.message[:60])
        print(f"   {label:34s} ACUE {float(acue@f):.5f}   fibre range [{out[0]:.5f}, {out[1]:.5f}]  width {out[1]-out[0]:.5f}")
    # occupation patterns of w consecutive sites: max range over all patterns
    for width in (3, 4):
        worst = (-1.0, None, None)
        for pat in itertools.product([0,1], repeat=width):
            f = np.array([np.mean([all(((x in Sx) == bool(pat[i])) for i, x in enumerate(range(width))) for Sx in orbits[r]]) for r in reps])
            if (acue@f) < 1e-9: continue
            out = []
            for sign in (1, -1):
                t0 = time.time()
                r = linprog(sign*f, A_eq=A, b_eq=b, bounds=(0, None), method='highs', options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
                out.append(sign*r.fun if r.status == 0 else float('nan'))
                print(f"      [LP {''.join(map(str,pat))} sign {sign}: {time.time()-t0:.1f}s status {r.status}]", flush=True)
            wdt = out[1]-out[0]
            if wdt > worst[0]: worst = (wdt, pat, (float(acue@f), out[0], out[1]))
        print(f"   width {width}: max range over patterns = {worst[0]:.5f}  at {''.join(map(str,worst[1]))}: ACUE {worst[2][0]:.5f}, range [{worst[2][1]:.5f}, {worst[2][2]:.5f}]", flush=True)
    # Nyquist row and survival
    pN2 = np.array([abs(sum((-1)**x for x in r))**2 for r in reps])/N
    frange(pN2, "E|p_N|^2 / N")
    for t in (1.6, 1.8):
        frange((depth > t).astype(float), f"P(N^2 D > {t})")
