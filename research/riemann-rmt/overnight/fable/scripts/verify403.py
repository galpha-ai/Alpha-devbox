"""Independent replay of the exact fibre dimension on rotation orbits.
Lower bound: modular rank of the balanced power-sum rows on orbit representatives (fresh primes).
Upper bound: number of distinct N-residue sets E = {nu_j + N-1-j mod 2N} over admissible weights nu.
"""
import sys, itertools, numpy as np
from math import comb, gcd

def partitions(n, m=None):
    if m is None: m = n
    if n == 0: yield (); return
    for f in range(min(n, m), 0, -1):
        for rest in partitions(n - f, f): yield (f,) + rest

def phi(n): return sum(1 for k in range(1, n+1) if gcd(k, n) == 1)

def orbit_reps(N):
    M = 2*N; reps = {}
    for S in itertools.combinations(range(M), N):
        best = min(tuple(sorted((x + r) % M for x in S)) for r in range(M))
        reps[best] = reps.get(best, 0) + 1
    return reps  # canonical rep -> orbit size

def upper_bound(N):
    E_sets = set()
    for d in range(N+1):
        P = list(partitions(d))
        for p in P:
            for q in P:
                if len(p) + len(q) > N: continue
                nu = p + (0,)*(N-len(p)-len(q)) + tuple(-v for v in reversed(q))
                E = tuple(sorted((nu[i] + N-1-i) % (2*N) for i in range(N)))
                if len(set(E)) == N: E_sets.add(E)
    return len(E_sets)

def rank_mod(A, p):
    A = A.copy() % p; r = 0; rows, cols = A.shape
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if A[i, c]: piv = i; break
        if piv is None: continue
        A[[r, piv]] = A[[piv, r]]
        inv = pow(int(A[r, c]), p-2, p)
        A[r] = (A[r] * inv) % p
        nz = np.nonzero(A[:, c])[0]
        for i in nz:
            if i != r: A[i] = (A[i] - A[i, c] * A[r]) % p
        r += 1
        if r == rows: break
    return r

def prim_root_2N(p, N):
    M = 2*N; assert (p-1) % M == 0
    for g in range(2, p):
        w = pow(g, (p-1)//M, p)
        if all(pow(w, k, p) != 1 for k in range(1, M)): return w
    raise RuntimeError

def modular_rank(N, p, reps):
    M = 2*N; w = prim_root_2N(p, N)
    rep_list = list(reps.keys())
    # power sums p_k(S) for k = -N..N on each rep, mod p
    PS = {}
    for k in range(-N, N+1):
        PS[k] = np.array([sum(pow(w, (k*x) % M, p) for x in S) % p for S in rep_list], dtype=np.int64)
    rows = []
    for d in range(N+1):
        P = list(partitions(d))
        for lam in P:
            for mu in P:
                v = np.ones(len(rep_list), dtype=np.int64)
                for a in lam: v = (v * PS[a]) % p
                for b in mu: v = (v * PS[-b]) % p
                rows.append(v)
    A = np.array(rows, dtype=np.int64)
    return rank_mod(A, p), A.shape

for N in [int(a) for a in sys.argv[1:]] or [5, 6, 7, 8]:
    M = 2*N
    burn = sum(phi(dd) * comb(M//dd, N//dd) for dd in range(1, M+1) if M % dd == 0 and N % dd == 0) // M
    reps = orbit_reps(N)
    ub = upper_bound(N)
    out = [f"N={N}: orbits enumerated={len(reps)} burnside={burn}  upper-bound |E|={ub}"]
    for p in [q for q in range(M*2+1, 5000, M) if all(q % r for r in range(2, int(q**0.5)+1))][:2]:
        rk, shape = modular_rank(N, p, reps)
        out.append(f"   prime {p}: rows x orbits = {shape}, modular rank = {rk}  -> affine dim = {len(reps)-rk}")
    print("\n".join(out), flush=True)
