"""r1_fibre_depth_separation.py -- does the depth (or the marked depth) separate ACUE from every element of the
CUE-moment fibre?  (Fable cluster E, task C2, constructive test.)

Setting.  F_N = {q >= 0 on N-subsets of Z_{2N}, sum q = 1, E_q[p_lam conj(p_nu)] = E_ACUE[...] for all |lam|=|nu|<=N}.
All constraints and all statistics considered are rotation-invariant, so we work on rotation-orbit space (as in
riemann-impostors/counterexamples/fibre_tomography.py).  The reflection C -> -C acts on orbits; the fibre tangent
space NS splits into a reflection-symmetric part (dim d_sym) and a chiral part (dim d_chi).

Results printed per N:
  1. fibre dims d, d_sym, d_chi  (N = 5..8; spectral-gap rank detection).
  2. [P, verified] For a chiral direction h, q_eps = mu(1 + eps h) is an honest fibre element (positivity radius,
     moment residual) and the law of N^2(-Lambda) (values + clock atom) under q_eps is IDENTICAL to ACUE's: TV = 0.
     The same holds for every dihedral-invariant statistic.  (N = 6, 7, 8)
  3. Is tau injective on reflection classes of non-clock orbits?  Number of distinct values, minimal separation
     between distinct classes, and rank of the 'law map'  (level-set indicator) * diag(mu) * NS_sym  vs d_sym.
  4. How many depth functionals pin the symmetric fibre: dims of the sub-fibre invisible to (clock atom),
     (atom, E[tau]), (atom, E[tau], E[tau^2]), ... up to the full law.
  5. Marked depth on spectral measures (N = 6, 7): with a conjugation-invariant (Haar) lift, the law of the
     rotation-covariant marked depth chi~ given the configuration is that of <grad tau, q>, q ~ Dirichlet(1,..,1);
     its Haar moments are the functionals  G2 = |grad tau|^2 (even under reflection) and G3 = sum_j (d_j tau)^3
     (odd).  We compute grad tau on every non-clock orbit (flagging kinks = tied first collisions), verify the
     parities, and test whether G3 sees the chiral fibre (rank of G3 * diag(mu) * NS_chi) and whether an odd
     STATIC observable of degree N+1 does too.

Run:  python3 r1_fibre_depth_separation.py  [N ...]      (default 5 6 7 8; ~1-3 minutes)
Data: writes ../data/r1_fibre_N{N}.npz  (null space, reflection map, tau, gradients).
"""
import sys, time
import numpy as np
from itertools import combinations
from math import pi
RR = "/home/user/Alpha-devbox/research/riemann-rmt"
sys.path.insert(0, f"{RR}/riemann-impostors/counterexamples")
from dyn1_core import orbit_masses, coeffs, find_ustar
DATA = f"{RR}/riemann-impostors/data"
OUT = f"{RR}/overnight/fable/data"

def partitions(n):
    def gen(n, maxp):
        if n == 0:
            yield (); return
        for f in range(min(n, maxp), 0, -1):
            for rest in gen(n - f, f):
                yield (f,) + rest
    return list(gen(n, n))

def canon(slots, M):
    full = (1 << M) - 1
    mask = 0
    for x in slots: mask |= 1 << x
    m, best = mask, mask
    for _ in range(M - 1):
        m = ((m << 1) & full) | (m >> (M - 1))
        if m < best: best = m
    return tuple(x for x in range(M) if (best >> x) & 1)

def rank_gap(A, name):
    s = np.linalg.svd(A, compute_uv=False)
    tol = s[0] * max(A.shape) * np.finfo(float).eps * 100
    r = int((s > tol).sum())
    gap = s[r - 1] / s[r] if r < len(s) else np.inf
    print(f"    [{name}] shape {A.shape} rank {r}  (sigma_r={s[r-1]:.2e}, sigma_r+1={(s[r] if r<len(s) else 0):.2e}, gap {gap:.1e})")
    return r

def rank_tol(A, rel=1e-9):
    if A.size == 0: return 0
    s = np.linalg.svd(A, compute_uv=False)
    return int((s > s[0] * rel).sum()) if s[0] > 0 else 0

def balanced_rows(P, N, degs):
    """real rows (Re, Im) of E[p_lam conj p_nu] on orbit space for |lam|=|nu| in degs; returns rows, and the odd (Im) rows."""
    R = P.shape[0]; rows, odd = [], []
    for deg in degs:
        pl = partitions(deg)
        Pl = {}
        for lam in pl:
            v = np.ones(R, complex)
            for part in lam: v = v * P[:, part]
            Pl[lam] = v
        for i, lam in enumerate(pl):
            for j, nu in enumerate(pl):
                if j < i: continue
                F = Pl[lam] * np.conj(Pl[nu])
                rows.append(F.real)
                if j > i:
                    rows.append(F.imag); odd.append(F.imag)
    return np.array(rows), np.array(odd)

def tau_angles(th):
    p = np.array([1.0 + 0j])
    for t in th: p = np.convolve(p, np.array([1.0, -np.exp(1j * t)]))
    return find_ustar(p[::-1], len(th))[0]

def grad_tau(th, h=1e-5):
    """central gradient + kink detection (one-sided derivatives disagree)"""
    n = len(th); g = np.zeros(n); kink = False
    t0 = tau_angles(th)
    for j in range(n):
        tp = th.copy(); tp[j] += h; tm = th.copy(); tm[j] -= h
        fp, fm = tau_angles(tp), tau_angles(tm)
        g[j] = (fp - fm) / (2 * h)
        if abs((fp - t0) - (t0 - fm)) > 20 * h * max(abs(g[j]), 1e-3) + 1e-8:
            kink = True
    return g, kink

def law_matrix(val, clockmask, ndig=9):
    """level-set indicator matrix T (levels x orbits): the law of N^2 tau (clock = its own level)."""
    key = np.where(clockmask, np.inf, np.round(val, ndig))
    levels = sorted(set(key.tolist()))
    T = np.array([(key == lv).astype(float) for lv in levels])
    return T, levels

def main(N):
    t0 = time.time()
    print("=" * 96); print(f"N = {N}")
    M = 2 * N
    reps, sizes, mu = orbit_masses(N)
    d = np.load(f"{DATA}/dyn1_results_N{N}.npz", allow_pickle=True)
    assert all(tuple(d['reps'][i]) == reps[i] for i in range(len(reps)))
    R = len(reps); mu = np.array(mu)
    clock = d['clockmask']; ust = d['ustars']
    val = N * N * ust
    idx = {r: i for i, r in enumerate(reps)}
    refl = np.array([idx[canon([(-x) % M for x in r], M)] for r in reps])
    Rm = np.zeros((R, R)); Rm[np.arange(R), refl] = 1.0          # (Rm v)_i = v_{refl(i)}
    assert np.allclose(mu[refl], mu) and np.allclose(np.where(clock, 0, val)[refl], np.where(clock, 0, val), atol=1e-9)
    nself = int((refl == np.arange(R)).sum())
    # ---- 1. fibre and its split
    Xs = np.array(reps)
    P = np.zeros((R, N + 2), complex)
    for k in range(1, N + 2): P[:, k] = np.exp(1j * pi * k * Xs / N).sum(axis=1)   # p_1..p_{N+1}
    A, _ = balanced_rows(P, N, range(1, N + 1))
    A = A / np.linalg.norm(A, axis=1, keepdims=True)          # row scaling does not change the null space
    Afull = np.vstack([A, np.ones((1, R)) / np.sqrt(R)])
    r = rank_gap(Afull, "balanced deg<=N + normalisation")
    _, sv, Vt = np.linalg.svd(Afull, full_matrices=True)
    NS = Vt[r:].T; dim = NS.shape[1]
    assert np.abs(Afull @ NS).max() < 1e-8, np.abs(Afull @ NS).max()
    Psym = (NS + Rm @ NS) / 2; Pchi = (NS - Rm @ NS) / 2
    d_sym, d_chi = rank_tol(Psym), rank_tol(Pchi)
    # orthonormal bases of the two parts
    def colspace(B, rk):
        if rk == 0: return np.zeros((R, 0))
        U, s, _ = np.linalg.svd(B, full_matrices=False); return U[:, :rk]
    NSs, NSc = colspace(Psym, d_sym), colspace(Pchi, d_chi)
    print(f"  orbits R={R} (self-mirror {nself}), fibre dim = {dim} = d_sym {d_sym} + d_chi {d_chi}")
    # ---- 2. chiral impostor is blind to the depth law
    T, levels = law_matrix(val, clock)
    nlev = len(levels) - 1
    if d_chi > 0:
        rng = np.random.default_rng(0)
        v = NSc @ (NSc.T @ (mu * rng.normal(size=R))); h = v / mu        # projection of a mu-weighted vector on the chiral space
        eps = 0.9 / max(-h.min(), 1e-300)
        q = mu * (1 + eps * h)
        assert q.min() > 0 and abs(q.sum() - 1) < 1e-12
        res = np.abs(A @ q - A @ mu).max()
        tv = 0.5 * np.abs(T @ q - T @ mu).sum()
        Enc = lambda w: (w[~clock] @ val[~clock]) / w[~clock].sum()
        print(f"  chiral impostor q = mu(1+eps h), eps = {eps:.4f} (0.9 x positivity radius): min q/mu = {(q/mu).min():.4f}, "
              f"max |q-mu|/mu = {np.abs(q/mu-1).max():.4f}, moment residual {res:.1e}, TV(q, mu) = {0.5*np.abs(q-mu).sum():.4f}")
        print(f"     law of N^2(-Lambda): TV(law_q, law_mu) = {tv:.2e}; clock atom {q[clock].sum():.6f} vs {mu[clock].sum():.6f}; "
              f"E[N^2 tau|nc] {Enc(q):.10f} vs {Enc(mu):.10f}   -> the depth is exactly blind")
    # ---- 2b. closed-form chiral impostors: q = mu (1 + eps Im det(U)^{2k}),  det(U_C)^{2k} = e^{2 pi i k X/N}, X = sum(C)
    Xc = np.array([sum(r) for r in reps])
    for k in range(1, N // 2 + 1):
        s_k = np.sin(2 * pi * k * Xc / N)                       # Im det^{2k}: rotation-invariant, reflection-odd
        if np.abs(s_k).max() < 1e-12: continue                # k = N/2: det^N is real
        v = mu * s_k
        inf = np.abs(A @ v).max() < 1e-10                      # in the fibre?
        chi = np.abs(v[refl] + v).max() < 1e-12
        q = mu * (1 + 0.9 * s_k)
        tvq = 0.5 * np.abs(q - mu).sum(); tvl = 0.5 * np.abs(T @ q - T @ mu).sum()
        print(f"  det-type direction Im det^{2*k} (k={k}): in fibre {inf} (|A v|max={np.abs(A@v).max():.1e}, predicted iff k(N-k)={k*(N-k)} > N), "
              f"chiral {chi}; q=mu(1+0.9 Im det^{2*k}): TV(q,mu)={tvq:.4f}, TV of tau-laws={tvl:.1e}")
    # ---- 3. injectivity of tau on reflection classes
    nc = ~clock
    cls = {}
    for i in np.where(nc)[0]:
        key = min(i, refl[i]); cls.setdefault(key, []).append(i)
    classes = list(cls.values())
    cvals = np.array([val[c[0]] for c in classes])
    o = np.argsort(cvals); dv = np.diff(cvals[o])
    coinc = [(classes[o[i]], classes[o[i+1]], cvals[o[i]]) for i in range(len(dv)) if dv[i] < 1e-9]
    print(f"  non-clock reflection classes: {len(classes)}; distinct N^2 tau levels: {nlev}; "
          f"min separation between classes {dv[dv>=1e-9].min() if (dv>=1e-9).any() else 0:.2e}; coincidences (<1e-9): {len(coinc)}")
    for a, b, vv in coinc[:6]:
        print(f"     tie at N^2 tau = {vv:.9f}: orbits {[tuple(reps[i]) for i in a]} vs {[tuple(reps[i]) for i in b]}")
    Lmap = T @ NSs                                 # law map restricted to symmetric directions (NS lives in delta-q space)
    rk_law_sym = rank_tol(Lmap, 1e-8)
    rk_law_all = rank_tol(T @ NS, 1e-8)
    print(f"  rank of law map on symmetric fibre = {rk_law_sym} / {d_sym}  ({'INJECTIVE: the law of tau pins the symmetric fibre' if rk_law_sym == d_sym else 'NOT injective'});"
          f"  on the full fibre = {rk_law_all} / {dim}  (chiral part invisible: {dim - rk_law_all} dims)")
    # ---- 4. how many depth functionals
    vnc = np.where(clock, 0.0, val)
    lo_, hi_ = vnc[nc].min(), vnc[nc].max()
    x = np.where(nc, (2 * vnc - lo_ - hi_) / (hi_ - lo_), 0.0)       # non-clock values mapped to [-1,1] (Chebyshev basis stays bounded)
    rows = [clock.astype(float)]
    names = ["atom"]
    invis = []
    # Chebyshev-type polynomials in x (same row space as power moments)
    polys = [np.ones(R), x.copy()]
    for k in range(2, 30): polys.append(2 * x * polys[-1] - polys[-2])
    for m in range(0, 30):
        if m > 0:
            rows.append(np.where(nc, polys[m], 0.0)); names.append(f"E[tau^{m}]")
        Fm = np.array(rows) @ NSs
        invis.append(d_sym - rank_tol(Fm, 1e-10))
        if invis[-1] == 0: break
    print(f"  dims of symmetric sub-fibre invisible to (atom, E tau, ..., E tau^m), m=0..: {invis}")
    if invis[-1] == 0:
        print(f"     -> atom + {len(invis)-1} power moments = {len(invis)} functionals pin the symmetric fibre (d_sym = {d_sym}: {'generic count, no saving' if len(invis)==d_sym else 'fewer than generic'})")
    else:
        print(f"     -> one dimension per moment (generic); {invis[-1]} dims still invisible at the 30-moment cap, so d_sym = {d_sym} functionals would be needed")
    # ---- 5. marked depth as gradient functionals
    G2 = np.zeros(R); G3 = np.zeros(R); kinks = np.zeros(R, bool); gsum = np.zeros(R)
    if N <= 7:
        for i in np.where(nc)[0]:
            th = np.array([pi * xx / N for xx in reps[i]])
            g, kink = grad_tau(th)
            G2[i] = g @ g; G3[i] = (g ** 3).sum(); kinks[i] = kink; gsum[i] = g.sum()
        print(f"  grad tau on {nc.sum()} non-clock orbits: kinks (tied first collision) on {kinks.sum()} orbits "
              f"(of which self-mirror {int((kinks & (refl == np.arange(R))).sum())}); max |sum_j d_j tau| = {np.abs(gsum[~kinks]).max():.1e} (rotation invariance)")
        ok2 = np.abs(G2[refl] - G2)[~kinks & ~kinks[refl]].max(); ok3 = np.abs(G3[refl] + G3)[~kinks & ~kinks[refl]].max()
        print(f"     parity check: |G2(refl) - G2| <= {ok2:.1e} (even), |G3(refl) + G3| <= {ok3:.1e} (odd)")
        G3s = np.where(kinks, 0.0, G3); G2s = np.where(kinks, 0.0, G2)
        rk3 = rank_tol(G3s[None, :] @ NSc, 1e-8) if d_chi > 0 else 0
        print(f"     does the Haar 3rd moment of the covariant marked depth (G3 = sum (d_j tau)^3, odd) see the chiral fibre? rank {rk3} (of at most 1) on d_chi = {d_chi}")
        if d_chi > 0 and rk3 > 0:
            dq = G3s @ NSc; k = np.argmax(np.abs(dq))
            v = NSc[:, k]; h = v / mu; eps = 0.9 / max(-h.min(), 1e-300); q = mu * (1 + eps * h)
            print(f"        explicit chiral impostor: E_q[G3;nc] - E_mu[G3;nc] = {(q-mu) @ G3s:+.3e}  while TV of tau-laws = {0.5*np.abs(T@q - T@mu).sum():.1e}")
        # static odd observable of degree N+1
        _, odd = balanced_rows(P, N, [N + 1])
        rk_odd = rank_tol(odd @ NSc, 1e-8) if d_chi > 0 else 0
        rk_ev = rank_tol(A @ NSc, 1e-8) if d_chi > 0 else 0
        print(f"     for comparison: odd balanced moments of degree N+1 see {rk_odd} of the {d_chi} chiral dims (degree<=N moments see {rk_ev}: must be 0 by construction)")
        # does G2 add anything beyond the law on the symmetric part? (only meaningful if law not injective)
        rkG2 = rank_tol(np.vstack([T, G2s[None, :]]) @ NSs, 1e-8)
        print(f"     rank of (law, G2) on symmetric fibre = {rkG2} / {d_sym}")
    np.savez(f"{OUT}/r1_fibre_N{N}.npz", NS=NS, NSs=NSs, NSc=NSc, refl=refl, mu=mu, val=val, clock=clock,
             G2=G2, G3=G3, kinks=kinks, reps=np.array(reps), levels=np.array(levels[:-1]))
    print(f"  [N={N}: {time.time()-t0:.1f} s]")

if __name__ == "__main__":
    for N in [int(a) for a in sys.argv[1:]] or [5, 6, 7, 8]:
        main(N)
