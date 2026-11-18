"""Row-space check for statistics that the fibre LP reports as forced.  A statistic f (a function of the
rotation orbit) is forced on the whole AFFINE moment fibre, with value y.b, iff f = A^T y for the balanced-moment
constraint system (A, b): then every signed measure q with A q = b has f.q = y.A q = y.b.  This is stronger than
the LP range over the positive fibre and takes seconds, so it replaces the simplex check of the Nyquist row at
N = 9, where both HiGHS methods stalled on that objective (it is constant on the feasible set).  Checked here:
the Nyquist row E|p_N|^2/N (forced to 1 by the conservation law) and the eight width-3 occupation patterns."""
import itertools, sys, time, numpy as np
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
for N in [int(a) for a in sys.argv[1:]] or [6, 7, 8, 9]:
    M = 2*N; t0 = time.time()
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
    A, b = U[:, :r].T @ A, U[:, :r].T @ b          # orthonormal row basis, same reduction as the LP scripts
    print(f"N={N}: orbits {len(reps)}, constraint rank {r}, setup {time.time()-t0:.0f}s", flush=True)
    def check(f, label):
        y, *_ = np.linalg.lstsq(A.T, f, rcond=None)
        resid = np.abs(A.T @ y - f).max()
        print(f"   {label:28s} forced value y.b = {float(y@b):.12f}   row-space residual {resid:.1e}", flush=True)
    pN2 = np.array([abs(sum((-1)**x for x in r))**2 for r in reps])/N
    check(pN2, "E|p_N|^2 / N")
    for pat in itertools.product([0,1], repeat=3):
        f = np.array([np.mean([all(((x in Sx) == bool(pat[i])) for i, x in enumerate(range(3))) for Sx in orbits[r]]) for r in reps])
        check(f, f"width-3 pattern {''.join(map(str,pat))}")
    # a control that is NOT forced: the survival indicator's companion, the width-4 pattern 0100
    f = np.array([np.mean([all((x in Sx) == bool(p) for x, p in zip(range(4), (0,1,0,0))) for Sx in orbits[r]]) for r in reps])
    check(f, "width-4 pattern 0100 (control)")
