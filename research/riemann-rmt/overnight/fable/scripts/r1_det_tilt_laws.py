"""r1_det_tilt_laws.py -- the determinant-tilt family q = mu (1 + eps Re/Im det(U_C)^{2k}) and the depth law.

Uses ../data/r1_fibre_N{N}.npz written by r1_fibre_depth_separation.py.  For each k = 1..N/2 and both the
symmetric (cos) and chiral (sin) tilt, reports: membership in the fibre (predicted iff k(N-k) > N, i.e. 2<=k<=N-2),
TV(q, mu), and TV between the laws of N^2(-Lambda) (clock atom + values) under q and under mu, plus the shift of
the clock atom and of E[N^2 tau | non-clock].  Shows that the symmetric members are 'Class I' (caught by the depth
law) while the chiral members are exactly invisible.   Run: python3 r1_det_tilt_laws.py
"""
import sys, numpy as np
from math import pi
from itertools import combinations
RR = "/home/user/Alpha-devbox/research/riemann-rmt"
sys.path.insert(0, f"{RR}/riemann-impostors/counterexamples")
def partitions(n):
    def gen(n, maxp):
        if n == 0:
            yield (); return
        for f in range(min(n, maxp), 0, -1):
            for rest in gen(n - f, f):
                yield (f,) + rest
    return list(gen(n, n))
print(f"{'N':>2} {'k':>2} {'k(N-k)':>6} {'type':>4} {'in fibre':>8} {'TV(q,mu)':>9} {'TV tau-laws':>11} {'atom(q)':>9} {'atom(mu)':>9} {'E_q[N^2tau|nc]':>14} {'E_mu':>10}")
for N in (5, 6, 7, 8):
    d = np.load(f"{RR}/overnight/fable/data/r1_fibre_N{N}.npz", allow_pickle=True)
    mu, val, clock, reps = d['mu'], d['val'], d['clock'], d['reps']
    R = len(mu); X = reps.sum(axis=1)
    P = np.zeros((R, N + 1), complex)
    for kk in range(1, N + 1): P[:, kk] = np.exp(1j * pi * kk * reps / N).sum(axis=1)
    rows = []
    for deg in range(1, N + 1):
        pl = partitions(deg)
        Pl = {lam: np.prod([P[:, p] for p in lam], axis=0) for lam in pl}
        for lam in pl:
            for nu in pl:
                F = Pl[lam] * np.conj(Pl[nu]); rows += [F.real, F.imag]
    A = np.array(rows); nrm = np.linalg.norm(A, axis=1)
    A = A[nrm > 1e-9 * nrm.max()]                       # drop identically-zero rows (e.g. Im|p_1|^{2N}) by a RELATIVE threshold
    A /= np.linalg.norm(A, axis=1, keepdims=True)
    key = np.where(clock, np.inf, np.round(val, 9)); levels = sorted(set(key.tolist()))
    T = np.array([(key == lv).astype(float) for lv in levels])
    nc = ~clock
    for k in range(1, N // 2 + 1):
        for typ, fn in (("cos", np.cos), ("sin", np.sin)):
            s = fn(2 * pi * k * X / N)
            if np.abs(s).max() < 1e-12: continue
            v = mu * s; inf = np.abs(A @ v).max() < 1e-10
            eps = 0.9 / max(-s.min(), 1e-300) if s.min() < 0 else 0.9
            q = mu * (1 + eps * s); q /= q.sum()
            tvq = 0.5 * np.abs(q - mu).sum(); tvl = 0.5 * np.abs(T @ q - T @ mu).sum()
            Eq = (q[nc] @ val[nc]) / q[nc].sum(); Em = (mu[nc] @ val[nc]) / mu[nc].sum()
            print(f"{N:>2} {k:>2} {k*(N-k):>6} {typ:>4} {str(inf):>8} {tvq:>9.4f} {tvl:>11.2e} {q[clock].sum():>9.5f} {mu[clock].sum():>9.5f} {Eq:>14.7f} {Em:>10.7f}")
