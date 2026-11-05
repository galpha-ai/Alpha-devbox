"""DIRECTION 6: the center-of-mass modulation family.

Claim discovered at N=5 (via the moment-code compression of translated Fermi seas):
  q_g(S) = q_ACUE(S) * g(X(S)),  X(S) = sum(S) mod N,
matches ALL balanced moments E[p_lam pbar_nu] = delta z_lam iff
  E_ACUE[g(X)] = 1 and certain Fourier coefficients of g vanish (at N=5: g^(±1)=0).

Test for N = 5,6,7,8: build the linear system on g in R^N, find:
 - which com-frequencies are forced to vanish,
 - affine dimension of the solution space,
 - positivity: dimension/vertices of the polytope of valid g >= 0,
 - hence an ALL-N family of mimickers if dim >= 1 beyond the uniform g = 1.
"""
import numpy as np
from itertools import combinations
from math import pi, factorial
from collections import Counter

def partitions(n):
    def gen(n, maxp):
        if n == 0:
            yield (); return
        for f in range(min(n, maxp), 0, -1):
            for rest in gen(n - f, f):
                yield (f,) + rest
    return list(gen(n, n))
def z_lambda(lam):
    z = 1
    for r_, m_ in Counter(lam).items():
        z *= (r_ ** m_) * factorial(m_)
    return z

for N in (5, 6, 7, 8):
    M = 2 * N
    zeta = np.exp(1j * pi / N)
    configs = list(combinations(range(M), N))
    nC = len(configs)
    qA = np.zeros(nC)
    for i, S in enumerate(configs):
        pr = 1.0
        for x, y in combinations(S, 2):
            pr *= abs(zeta ** x - zeta ** y) ** 2
        qA[i] = pr
    qA /= qA.sum()
    X = np.array([sum(S) % N for S in configs])
    IND = np.array([(X == x).astype(float) for x in range(N)])   # N x nC
    PK = np.zeros((nC, N + 1), complex)
    for i, S in enumerate(configs):
        for k in range(1, N + 1):
            PK[i, k] = sum(zeta ** (k * x) for x in S)
    rows, rhs = [], []
    for d in range(1, N + 1):
        pl = partitions(d)
        Pl = {lam: np.prod([PK[:, p] for p in lam], axis=0) for lam in pl}
        for lam in pl:
            for nu in pl:
                obs = Pl[lam] * np.conj(Pl[nu])
                tgt = z_lambda(lam) if lam == nu else 0.0
                row = IND @ (qA * obs)          # length N (complex)
                for rr, tt in ((row.real, tgt), (row.imag, 0.0)):
                    if np.abs(rr).max() > 1e-11:
                        rows.append(rr); rhs.append(tt)
    rows.append(IND @ qA); rhs.append(1.0)
    A = np.array(rows); b = np.array(rhs)
    # solution affine space: g0 = ones is a solution (ACUE itself)
    g0 = np.ones(N)
    res0 = np.abs(A @ g0 - b).max()
    from scipy.linalg import null_space
    NSg = null_space(A, rcond=1e-10)
    dim = NSg.shape[1]
    print(f"N={N}: com-modulation system: rows={len(rows)}, residual at g=1: {res0:.2e}, "
          f"null dim = {dim}")
    if dim > 0:
        # which Fourier coefficients are free? project Fourier modes onto null space
        for j in range(1, N // 2 + 1):
            cvec = np.cos(2 * pi * j * np.arange(N) / N)
            svec = np.sin(2 * pi * j * np.arange(N) / N)
            pc = np.linalg.norm(NSg.T @ cvec) / max(np.linalg.norm(cvec), 1e-30)
            ps = np.linalg.norm(NSg.T @ svec) / max(np.linalg.norm(svec), 1e-30)
            print(f"    com-frequency j={j}: null-space overlap cos={pc:.3f} sin={ps:.3f} "
                  f"({'FREE' if max(pc,ps)>1e-6 else 'forced zero'})")
        # positivity: g = 1 + u, u in null space; polytope nonempty around 1 => family exists
        # sample extreme scaling in random null directions
        rng = np.random.default_rng(0)
        tmax = []
        for _ in range(200):
            u = NSg @ rng.normal(size=dim); u /= np.abs(u).max()
            # max t with 1 + t u >= 0
            tneg = u < 0
            t = 1.0 / np.abs(u[tneg]).max() if tneg.any() else np.inf
            tmax.append(t)
        print(f"    positivity radius in random null directions: min={min(tmax):.3f}, "
              f"max={max(tmax):.3f}  (family of laws has affine dim {dim})")
        # verify: an extreme modulation is an honest mimicker
        u = NSg[:, 0]
        tneg = u < 0
        t = 0.9 / np.abs(u[tneg]).max()
        g = 1 + t * u
        qg = qA * g[X]
        # check balanced moments directly
        worst = 0.0
        for d in range(1, N + 1):
            pl = partitions(d)
            Pl = {lam: np.prod([PK[:, p] for p in lam], axis=0) for lam in pl}
            for lam in pl:
                for nu in pl:
                    val = qg @ (Pl[lam] * np.conj(Pl[nu]))
                    tgt = z_lambda(lam) if lam == nu else 0.0
                    worst = max(worst, abs(val - tgt))
        print(f"    direct check of a modulated law: sum={qg.sum():.12f}, "
              f"worst balanced-moment error = {worst:.2e}, min g = {g.min():.4f}")
