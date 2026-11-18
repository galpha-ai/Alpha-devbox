"""Independent replay of Astra's N=11 protected-survival separation (own code, no external modules).
Claims checked: 16159 dihedral orbits of 11-subsets of Z/22; 1489 complementary transfer pairs with equal
sorted-gap histograms; protected (balanced trace) rows on the transfers have modular rank 964 (two primes);
the survival row at s = log(85/84) raises the rank to 965; survivors 324 / 443; signed counts 137/1096/256;
involution fixed-set counts on the alternant index set: 3956, 106, 22, 184 -> (3956+106-22-184)/4 = 964."""
import itertools, sys, time, numpy as np
from collections import Counter
from flint import acb, arb, acb_poly, ctx
N = 11; M = 2*N
t0 = time.time()
def log(*a): print(f"[{time.time()-t0:7.1f}s]", *a, flush=True)

# ---- 1. dihedral orbits -------------------------------------------------------------
def canon(S):
    best = None
    for sgn in (1, -1):
        for r in range(M):
            t = tuple(sorted((sgn*x + r) % M for x in S))
            if best is None or t < best: best = t
    return best
reps = {}
for S in itertools.combinations(range(M), N):
    c = canon(S); reps[c] = reps.get(c, 0) + 1
rep_list = sorted(reps); idx = {r: i for i, r in enumerate(rep_list)}
log("dihedral orbits:", len(rep_list), "(expect 16159)")

def gaps(S):
    s = sorted(S); return tuple(sorted((s[(i+1) % N] - s[i]) % M for i in range(N)))
pairs = []
for A in rep_list:
    Bc = canon([x for x in range(M) if x not in A])
    if Bc != A and A < Bc and gaps(A) == gaps(Bc): pairs.append((A, Bc))
log("transfer pairs:", len(pairs), "(expect 1489)")
A_side = [a for a, b in pairs]; B_side = [b for a, b in pairs]
configs = A_side + B_side; T = len(pairs)

# ---- 2. protected rows mod p ----------------------------------------------------------
def partitions(n, m=None):
    if m is None: m = n
    if n == 0: yield (); return
    for f in range(min(n, m), 0, -1):
        for rest in partitions(n - f, f): yield (f,) + rest
def prim_root(p):
    for g in range(2, p):
        w = pow(g, (p-1)//M, p)
        if all(pow(w, k, p) != 1 for k in range(1, M)): return w
def rank_mod(A, p):
    A = A.copy() % p; r = 0; rows, cols = A.shape
    for c in range(cols):
        col = A[r:, c]; nzr = np.nonzero(col)[0]
        if len(nzr) == 0: continue
        piv = r + nzr[0]
        if piv != r: A[[r, piv]] = A[[piv, r]]
        A[r] = (A[r] * pow(int(A[r, c]), p-2, p)) % p
        nz = np.nonzero(A[:, c])[0]; nz = nz[nz != r]
        if len(nz): A[nz] = (A[nz] - np.outer(A[nz, c], A[r])) % p
        r += 1
        if r == rows: break
    return r
def protected_matrix(p):
    w = prim_root(p)
    PS = {k: np.array([sum(pow(w, (k*x) % M, p) for x in S) % p for S in configs], dtype=np.int64) for k in range(-N, N+1)}
    rows = []
    for d in range(N+1):
        P = list(partitions(d))
        for i, lam in enumerate(P):
            for mu in P[i:]:
                v = np.ones(len(configs), dtype=np.int64)
                for a in lam: v = (v * PS[a]) % p
                for b in mu: v = (v * PS[-b]) % p
                vb = np.ones(len(configs), dtype=np.int64)        # conjugate: p_mu pbar_lam
                for a in mu: vb = (vb * PS[a]) % p
                for b in lam: vb = (vb * PS[-b]) % p
                tot = (v + vb) % p                                   # 2 Re
                rows.append((tot[T:] - tot[:T]) % p)                 # Delta_i = f(B_i) - f(A_i)
    return np.array(rows, dtype=np.int64)

# ---- 3. survival row at s = log(85/84), certified ----------------------------------------
ctx.prec = 260
zeta = (acb(0, arb.pi()/N)).exp()
lam_s = arb(85)/84
def poly_coeffs(S):
    P = acb_poly([1])
    for x in S: P = P * acb_poly([-(zeta**x), 1])
    c = [P[j] for j in range(N+1)]
    return [c[j] * lam_s**(j*(N-j)) for j in range(N+1)]
def classify(S):
    """+1: certified survival (11 simple unit-circle roots at time s); 0: certified collision before s; None: inconclusive."""
    a = poly_coeffs(S)
    eps = a[0]  # a_N = 1
    cph = (1/eps).sqrt()
    def Q(th):   # real trigonometric form, exact real part (antiperiodic for odd N)
        th = arb(th)
        return (cph * sum(a[j] * (acb(0, th*(arb(2*j-N)/2))).exp() for j in range(N+1))).real
    # (i) certified sign changes at midpoints between numerically located root angles
    af = np.array([complex(x) for x in a][::-1])
    ang = np.sort(np.angle(np.roots(af)) % (2*np.pi))
    mids = [(ang[k] + (ang[(k+1) % N] + (2*np.pi if k == N-1 else 0)))/2 for k in range(N)]
    pts = [arb(m) for m in mids] + [arb(mids[0]) + 2*arb.pi()]
    q = [Q(t) for t in pts]
    if all(((q[k] > 0 and q[k+1] < 0) or (q[k] < 0 and q[k+1] > 0)) for k in range(N)):
        return 1
    # (ii) certified isolated roots: off-circle ball => collision happened; reflection-disjointness => all on circle
    try:
        roots = acb_poly(a).roots()
    except Exception:
        return None
    if len(roots) != N: return None
    for z in roots:
        if (abs(z) - 1) != 0:
            return 0
    refl = [1/z.conjugate() for z in roots]
    def disjoint(u, v):
        return (abs(u - v) != 0)
    if all(disjoint(refl[k], roots[j]) for k in range(N) for j in range(N) if j != k):
        return 1
    return None
surv = []
for S in configs: surv.append(classify(S))
inconclusive = sum(1 for v in surv if v is None)
sA = sum(1 for v in surv[:T] if v == 1); sB = sum(1 for v in surv[T:] if v == 1)
log("survivors A-side / B-side:", sA, sB, "(expect 324 / 443); inconclusive:", inconclusive)
d = np.array([(surv[T+i] or 0) - (surv[i] or 0) for i in range(T)], dtype=np.int64)
log("signed counts -1/0/+1:", Counter(d.tolist()), "(expect 137/1096/256)")

# ---- 4. ranks ----------------------------------------------------------------------------
for p in (331, 463):
    Mp = protected_matrix(p)
    rk = rank_mod(Mp, p)
    rk2 = rank_mod(np.vstack([Mp, d % p]), p)
    log(f"prime {p}: protected rows {Mp.shape}, rank {rk} (expect 964); augmented rank {rk2} (expect 965)")

# ---- 5. involution fixed sets on the alternant index set E --------------------------------
Es = set()
for dd in range(N+1):
    P = list(partitions(dd))
    for pp in P:
        for q in P:
            if len(pp)+len(q) > N: continue
            nu = pp + (0,)*(N-len(pp)-len(q)) + tuple(-v for v in reversed(q))
            E = tuple(sorted((nu[i] + N-1-i) % M for i in range(N)))
            if len(set(E)) == N: Es.add(E)
R = lambda E: tuple(sorted((N-1-e) % M for e in E))
C = lambda E: tuple(sorted((M-1-x) % M for x in range(M) if x not in E))
fix = [len(Es), sum(R(E)==E for E in Es), sum(C(E)==E for E in Es), sum(R(C(E))==E for E in Es)]
log("|E| and fixed sets of R, C, RC:", fix, "(expect 3956,106,22,184); bound", (fix[0]+fix[1]-fix[2]-fix[3])/4)
