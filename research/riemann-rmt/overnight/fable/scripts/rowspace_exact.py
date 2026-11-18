"""Exact (mod-p) membership test: is a rotation-invariant statistic f in the row space of the balanced-moment
constraint system on rotation orbits?  Over K = Q(zeta_2N) the real/imaginary splitting of the LP scripts spans
the same space as the complex rows p_lam * conj(p_mu) (closed under conjugation), so f (rational) is forced on the
whole affine fibre iff f lies in their K-span.  Rank mod p is <= rank over K, so if the row f raises the rank
mod p above rank_K(A) (= 2704 - 1804 = 900 at N = 9, exact by the alternant sandwich of verify403.py), then f
is certified NOT to be in the K-row space.  Equal rank at two primes is strong evidence of membership.
Tested: the Nyquist row (itself the constraint lam = mu = (N)), the eight width-3 patterns, one width-4 control."""
import sys, itertools, numpy as np
from math import gcd
sys.setrecursionlimit(10000)
def partitions(n, m=None):
    if m is None: m = n
    if n == 0: yield (); return
    for f in range(min(n, m), 0, -1):
        for rest in partitions(n - f, f): yield (f,) + rest
def prim_root_2N(p, N):
    M = 2*N; assert (p-1) % M == 0
    for g in range(2, p):
        w = pow(g, (p-1)//M, p)
        if all(pow(w, k, p) != 1 for k in range(1, M)): return w
def echelon_mod(A, p):
    """row-reduce A mod p (vectorised); returns (reduced rows, pivot columns)"""
    A = A.copy() % p; r = 0; rows, cols = A.shape; piv_cols = []
    for c in range(cols):
        nzc = np.nonzero(A[r:, c])[0]
        if len(nzc) == 0: continue
        piv = r + nzc[0]
        A[[r, piv]] = A[[piv, r]]
        A[r] = (A[r] * pow(int(A[r, c]), p-2, p)) % p
        nz = np.nonzero(A[:, c])[0]; nz = nz[nz != r]
        if len(nz): A[nz] = (A[nz] - np.outer(A[nz, c], A[r])) % p
        piv_cols.append(c); r += 1
        if r == rows: break
    return A[:r], piv_cols
def reduce_vec(f, R, piv_cols, p):
    f = f.copy() % p
    for i, c in enumerate(piv_cols):
        if f[c]: f = (f - f[c] * R[i]) % p
    return f
for N in [int(a) for a in sys.argv[1:]] or [6, 7, 8, 9]:
    M = 2*N
    orbits = {}
    for S in itertools.combinations(range(M), N):
        key = min(tuple(sorted((x + r) % M for x in S)) for r in range(M))
        orbits.setdefault(key, []).append(S)
    reps = list(orbits)
    primes = [q for q in range(M*2+1, 5000, M) if all(q % r for r in range(2, int(q**0.5)+1))][:2]
    for p in primes:
        w = prim_root_2N(p, N)
        PS = {k: np.array([sum(pow(w, (k*x) % M, p) for x in S) % p for S in reps], dtype=np.int64) for k in range(-N, N+1)}
        rows = [np.ones(len(reps), dtype=np.int64)]
        for d in range(1, N+1):
            P = list(partitions(d))
            for lam in P:
                for mu in P:
                    v = np.ones(len(reps), dtype=np.int64)
                    for a in lam: v = (v * PS[a]) % p
                    for b in mu: v = (v * PS[-b]) % p
                    rows.append(v)
        A = np.array(rows, dtype=np.int64)
        R, pc = echelon_mod(A, p)
        print(f"N={N} prime {p}: rows {A.shape[0]}, orbits {len(reps)}, rank mod p = {len(pc)}, affine dim = {len(reps)-len(pc)}", flush=True)
        def test(f, label):
            rem = reduce_vec(np.array(f, dtype=np.int64), R, pc, p)
            nz = int(np.count_nonzero(rem))
            print(f"   {label:30s} {'IN row space (remainder 0)' if nz == 0 else f'NOT in row space (remainder has {nz} nonzero entries)'}", flush=True)
        invN = pow(N, p-2, p)
        test((PS[N] * PS[N] * invN) % p, "E|p_N|^2 / N")
        for width, pats in ((3, list(itertools.product([0,1], repeat=3))), (4, [(0,1,0,0)])):
            for pat in pats:
                f = []
                for r in reps:
                    cnt = sum(all((x in S) == bool(pat[i]) for i, x in enumerate(range(width))) for S in orbits[r])
                    f.append((cnt * pow(len(orbits[r]), p-2, p)) % p)
                test(f, f"width-{width} pattern {''.join(map(str,pat))}{' (control)' if width == 4 else ''}")
