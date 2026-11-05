"""tomo_fiber.py — Round 6, TOMO-Lambda: Lambda-tomography of the ACUE balanced-moment fiber.

Fiber at level N (configs = N-subsets of Z_{2N}, ACUE masses mu from dyn1_core):
  F_N = { q >= 0, sum q = 1, E_q[p_lam conj(p_nu)] = E_mu[...] for all |lam|=|nu|=d <= N }.
All constraint functions are rotation-invariant (balanced => phase zeta^{r(|lam|-|nu|)} = 1),
and Lambda is rotation-invariant, so LP extremes over the full fiber equal LP extremes over
rotation-invariant measures: we work on ORBIT space (q_i = total mass of orbit i).

Outputs per N in tomo_results_N{N}.npz + printed tables:
  - exact fiber dimension (orbit level and config level),
  - LP extremes of E_q[N^2 u*; nonclock], q(clock), and P(N^2 u* > y) sweep,
  - dual/reduced-cost geography (by com-class X = sum S mod N, by nadj),
  - structured subfamilies inside the null space: com-modulation g(X), nadj-tilts,
    (X,nadj) joint tilts, cylinder-invisible directions (orthogonal to all window
    pattern counts up to width w).
"""
import sys, time
import numpy as np
from itertools import combinations
from math import pi, factorial
from collections import Counter
from scipy.optimize import linprog

sys.path.insert(0, "/tmp/claude-0/-home-user-Alpha-devbox/00b3b5f7-f917-5641-a9be-c6a8f38f5cd7/scratchpad")
from dyn1_core import orbit_masses, coeffs, find_ustar

SP = "/tmp/claude-0/-home-user-Alpha-devbox/00b3b5f7-f917-5641-a9be-c6a8f38f5cd7/scratchpad"

def partitions(n):
    def gen(n, maxp):
        if n == 0:
            yield (); return
        for f in range(min(n, maxp), 0, -1):
            for rest in gen(n - f, f):
                yield (f,) + rest
    return list(gen(n, n))

def build_orbit_data(N):
    reps, sizes, mu = orbit_masses(N)
    d = np.load(f"{SP}/dyn1_results_N{N}.npz", allow_pickle=True)
    assert all(tuple(d['reps'][i]) == reps[i] for i in range(len(reps)))
    R = len(reps)
    Xslots = np.array(reps)                          # R x N slot matrix
    P = np.zeros((R, N + 1), complex)
    for k in range(1, N + 1):
        P[:, k] = np.exp(1j * pi * k * Xslots / N).sum(axis=1)
    return reps, sizes, np.array(mu), d, P, Xslots

def build_constraints(N, P):
    """Real constraint rows (Re/Im of balanced moments, deg 1..N) on orbit space."""
    R = P.shape[0]
    rows = []
    meta = []
    for deg in range(1, N + 1):
        pl = partitions(deg)
        Pl = {}
        for lam in pl:
            v = np.ones(R, complex)
            for part in lam:
                v = v * P[:, part]
            Pl[lam] = v
        for i, lam in enumerate(pl):
            for j, nu in enumerate(pl):
                if j < i:
                    continue
                F = Pl[lam] * np.conj(Pl[nu])
                rows.append(F.real); meta.append((deg, lam, nu, 're'))
                if j > i:
                    rows.append(F.imag); meta.append((deg, lam, nu, 'im'))
    A = np.array(rows)
    return A, meta

def numeric_rank(Awith1, name=""):
    s = np.linalg.svd(Awith1, compute_uv=False)
    smax = s[0]
    # spectral-gap detection
    tol = smax * max(Awith1.shape) * np.finfo(float).eps * 100
    r = int((s > tol).sum())
    gap = s[r - 1] / s[r] if r < len(s) else np.inf
    print(f"    [{name}] shape {Awith1.shape}, rank={r}, sigma_r={s[r-1]:.3e}, "
          f"sigma_r+1={(s[r] if r < len(s) else 0):.3e}, gap={gap:.2e}")
    return r, s

def compress(A, b, tol_rel=1e-11):
    """Return independent equality system (A_red, b_red) spanning the same row space."""
    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    r = int((s > s[0] * tol_rel).sum())
    A_red = (s[:r, None] * Vt[:r])
    b_red = U[:, :r].T @ b * s[:r] / s[:r]  # = U_r^T b then scaled consistently:
    b_red = (U[:, :r].T @ b)
    A_red = Vt[:r]
    # scale rows to unit norm (Vt rows already unit norm); b_red = U^T b / s? No:
    # A q = b  <=>  U S Vt q = b <=> S Vt q = U^T b <=> Vt q = S^{-1} U^T b
    b_red = (U[:, :r].T @ b) / s[:r]
    return A_red, b_red, r

def lp(c, A_eq, b_eq, sense=1):
    res = linprog(sense * np.asarray(c), A_eq=A_eq, b_eq=b_eq,
                  bounds=[(0, None)] * A_eq.shape[1], method='highs')
    if res.status != 0:
        return None
    return res

def law_summary(q, val, clockmask, label, y_ref=None):
    """val = N^2 u* (nan on clocks). Returns dict."""
    nc = ~clockmask
    qc = q[clockmask].sum()
    m = q[nc] @ val[nc]
    return dict(label=label, clock=qc, Enc=m)

def tv_law(q1, q2, val, clockmask):
    """TV distance between pushforward laws of N^2 u* (clocks = atom at +inf)."""
    key = np.where(clockmask, np.inf, np.round(val, 9))
    uniq = {}
    for k, a, b in zip(key, q1, q2):
        d = uniq.setdefault(k, [0.0, 0.0]); d[0] += a; d[1] += b
    return 0.5 * sum(abs(a - b) for a, b in uniq.values())

def main(N, ysweep=True, ystep=0.01):
    t0 = time.time()
    print("=" * 88)
    print(f"N = {N}")
    reps, sizes, mu, d, P, Xslots = build_orbit_data(N)
    R = len(reps)
    clockmask = d['clockmask']
    ustars = d['ustars']
    nadj = d['nadj']
    val = N * N * ustars                     # N^2 (-Lambda), nan on clock
    val_f = np.where(clockmask, 0.0, val)    # for linear objectives restricted to nonclock
    Xcom = np.array([sum(rep) % N for rep in reps])

    # spot-check ustars against recompute
    rng = np.random.default_rng(1)
    for i in rng.choice(np.where(~clockmask)[0], 3, replace=False):
        us, _, _ = find_ustar(coeffs(reps[i], N), N)
        assert abs(us - ustars[i]) < 1e-8, (i, us, ustars[i])
    print("  ustar spot-check vs recompute: OK (3 orbits, <1e-8)")

    A, meta = build_constraints(N, P)
    b = A @ mu
    ones = np.ones((1, R))
    Afull = np.vstack([A, ones])
    bfull = np.concatenate([b, [1.0]])

    # ---- 1. fiber dimension ----
    r_named, s = numeric_rank(Afull, name=f"balanced deg<=N + normalization")
    nC = 1
    from math import comb
    nC = comb(2 * N, N)
    dim_orbit = R - r_named
    dim_config = nC - R + dim_orbit
    print(f"  ORBIT-level fiber affine dim = {R} - {r_named} = {dim_orbit}")
    print(f"  CONFIG-level fiber affine dim = C({2*N},{N}) - rank = {nC} - {r_named} "
          f"- (intra-orbit {nC - R}) split: {dim_config} total "
          f"({nC - R} trivial intra-orbit + {dim_orbit} orbit-level)")

    # null-space basis (orbit level)
    _, sv, Vt = np.linalg.svd(Afull, full_matrices=True)
    NS = Vt[r_named:].T                       # R x dim_orbit
    # com-modulation subfamily: q = mu * g(X), sum mu g = 1 -> h = g-1: A(mu h(X)) = 0
    IndX = np.array([(Xcom == x).astype(float) for x in range(N)]).T   # R x N
    MX = Afull @ (mu[:, None] * IndX)
    rX = np.linalg.matrix_rank(MX, tol=np.abs(MX).max() * 1e-10)
    dim_com = N - rX
    # nadj-tilt subfamily
    nvals = sorted(set(nadj[~clockmask]))
    IndA = np.array([((nadj == a) & ~clockmask).astype(float) for a in nvals]).T
    IndA = np.hstack([IndA, clockmask[:, None].astype(float)])
    MA = Afull @ (mu[:, None] * IndA)
    rA = np.linalg.matrix_rank(MA, tol=np.abs(MA).max() * 1e-10)
    dim_nadj = IndA.shape[1] - rA
    # joint (X, nadj)
    cls = {}
    for i in range(R):
        cls.setdefault((Xcom[i], int(nadj[i]), bool(clockmask[i])), []).append(i)
    IndJ = np.zeros((R, len(cls)))
    for j, (k, ii) in enumerate(cls.items()):
        IndJ[ii, j] = 1.0
    MJ = Afull @ (mu[:, None] * IndJ)
    rJ = np.linalg.matrix_rank(MJ, tol=np.abs(MJ).max() * 1e-10)
    dim_joint = IndJ.shape[1] - rJ
    print(f"  structured null subfamilies: com-modulation g(X): dim {dim_com} "
          f"(of full {dim_orbit}); nadj-tilt: dim {dim_nadj}; joint (X,nadj): dim {dim_joint}")

    # which com frequencies are free (project Fourier modes of g on null space of MX)
    if dim_com > 0:
        _, _, VtX = np.linalg.svd(MX)
        NSX = VtX[rX:].T   # N x dim_com  (h coefficients per X-class)
        for jf in range(1, N // 2 + 1):
            cvec = np.cos(2 * pi * jf * np.arange(N) / N)
            svec = np.sin(2 * pi * jf * np.arange(N) / N)
            pc = np.linalg.norm(NSX.T @ cvec) / np.linalg.norm(cvec)
            ps = np.linalg.norm(NSX.T @ svec) / max(np.linalg.norm(svec), 1e-30)
            print(f"    com-frequency j={jf}: overlap cos={pc:.3f} sin={ps:.3f} "
                  f"({'FREE' if max(pc, ps) > 1e-6 else 'forced zero'})")

    # ---- cylinder-invisible directions ----
    # window pattern counts C_b(S), b in {0,1}^w, w = 2..min(6, 2N): rotation-invariant.
    occ = np.zeros((R, 2 * N))
    for i, rep in enumerate(reps):
        occ[i, list(rep)] = 1.0
    cyl_dims = {}
    prevrows = [np.ones(R)]
    for w in range(2, 7):
        rows = []
        for bpat in range(2 ** w):
            bits = [(bpat >> t) & 1 for t in range(w)]
            cnt = np.zeros(R)
            for s0 in range(2 * N):
                m = np.ones(R, bool)
                for t, bt in enumerate(bits):
                    col = occ[:, (s0 + t) % (2 * N)]
                    m &= (col == bt)
                cnt += m
            rows.append(cnt)
        Cw = np.array(rows)
        p = Cw @ NS                     # patterns x nulldim
        rw = np.linalg.matrix_rank(p, tol=max(np.abs(p).max(), 1e-300) * 1e-9) if dim_orbit else 0
        cyl_dims[w] = dim_orbit - rw
        print(f"    cylinder width {w}: null directions invisible to ALL width-<= {w} "
              f"pattern counts: dim {cyl_dims[w]}")

    # ---- 2. LP extremes ----
    A_red, b_red, rr = compress(Afull, bfull)
    assert rr == r_named, (rr, r_named)
    # feasibility of mu
    assert np.abs(A_red @ mu - b_red).max() < 1e-9

    results = {}
    duals = {}
    for name, c, sense in [
        ("E_nc_min", val_f, +1), ("E_nc_max", val_f, -1),
        ("clock_min", clockmask.astype(float), +1),
        ("clock_max", clockmask.astype(float), -1),
    ]:
        res = lp(c, A_red, b_red, sense=1 if sense > 0 else -1)
        v = res.fun * (1 if sense > 0 else -1)
        q = res.x
        redcost = (np.asarray(c) * (1 if sense > 0 else -1)) - A_red.T @ res.eqlin.marginals
        results[name] = (v, q)
        duals[name] = redcost * (1 if sense > 0 else -1)
        supp = int((q > 1e-10).sum())
        print(f"  LP {name:9s}: value = {v:.10f}   support {supp} orbits  "
              f"q(clock)={q[clockmask].sum():.6f}")

    acue_E = mu[~clockmask] @ val[~clockmask]
    acue_clock = mu[clockmask].sum()
    print(f"  ACUE reference: E[N^2 u*; nonclock] = {acue_E:.10f}, q(clock) = {acue_clock:.10f} "
          f"(= 2^(1-N) = {2.0**(1-N):.10f})")

    # ---- 3. y-sweep envelope ----
    ys, lo, hi = [], [], []
    if ysweep:
        ygrid = np.arange(1.30, 2.0001, ystep)
        for y in ygrid:
            ind = np.where(clockmask, 1.0, (val_f > y).astype(float))  # clocks: +inf > y
            r1 = lp(ind, A_red, b_red)
            r2 = lp(-ind, A_red, b_red)
            ys.append(y); lo.append(r1.fun); hi.append(-r2.fun)
        ys = np.array(ys); lo = np.array(lo); hi = np.array(hi)
        acue_surv = np.array([mu[clockmask].sum() + mu[(~clockmask) & (val_f > y)].sum()
                              for y in ys])
        gap = hi - lo
        print(f"  y-sweep envelope: sup gap = {gap.max():.6f} at y = {ys[gap.argmax()]:.3f}; "
              f"integral gap = {np.trapezoid(gap, ys):.6f}")
    # save
    np.savez(f"{SP}/tomo_results_N{N}.npz",
             dim_orbit=dim_orbit, dim_config=dim_config, rank=r_named,
             dim_com=dim_com, dim_nadj=dim_nadj, dim_joint=dim_joint,
             cyl_dims=np.array([cyl_dims.get(w, -1) for w in range(2, 7)]),
             E_nc_min=results["E_nc_min"][0], E_nc_max=results["E_nc_max"][0],
             clock_min=results["clock_min"][0], clock_max=results["clock_max"][0],
             q_Emin=results["E_nc_min"][1], q_Emax=results["E_nc_max"][1],
             q_clockmin=results["clock_min"][1], q_clockmax=results["clock_max"][1],
             rc_Emin=duals["E_nc_min"], rc_Emax=duals["E_nc_max"],
             ys=np.array(ys), lo=np.array(lo), hi=np.array(hi),
             acue_E=acue_E, mu=mu, val=np.where(clockmask, np.nan, val),
             clockmask=clockmask, nadj=nadj, Xcom=Xcom, NSshape=NS.shape,
             acue_surv=acue_surv if ysweep else np.array([]))
    np.save(f"{SP}/tomo_NS_N{N}.npy", NS)
    print(f"  [N={N} done in {time.time()-t0:.1f} s]")
    return None

if __name__ == "__main__":
    for N in [int(x) for x in sys.argv[1:]] or [6, 8, 10]:
        main(N)
