"""
r1_lattice_common.py -- shared machinery for the C1 task (simple zeros from correlation data).

Model ("periodic lattice adversary").  P points (zeros, with integer multiplicities m_x >= 0,
sum m_x = P) on the circle Z/L, L = M*P sites, M sites per mean spacing.  Scaled position = x/M,
scaled frequency alpha = k/P for the Fourier mode k in Z/L.  S_k = sum_x m_x e(kx/L).

Pair data ("bandwidth one", Montgomery under RH):   E|S_k|^2 / P = |k|/P   for 0 < |k| < P,
which is the lattice form of  F(alpha) = |alpha| (0 < |alpha| < 1), the k = 0 mode carrying the
mass  E|S_0|^2/P = P  (the delta_0 of the scaled form factor).  Positivity of the form factor:
E|S_k|^2 >= 0 for every k (trivial for a genuine process; a constraint for a *measure* adversary).

Triple data (Rudnick-Sarnak type, band Sum|alpha_i| < 2, CUE value):  E[S_k1 S_k2 S_k3]/P = 0
for k1+k2+k3 = 0, all k_i != 0, |k1|+|k2|+|k3| < 2P.   (Diaconis-Shahshahani: for CUE_P the
balanced moment E[p_lambda conj(p_nu)] = delta_{lambda nu} z_lambda when |lambda|=|nu| <= P; the
partition (k1,k2) never equals (k1+k2), so the moment vanishes.)

Objects.
  nu_d = E sum_x m_x m_{x+d} / P            (pair measure per point; nu_0 = A = E sum m^2 / P)
  T(d,e) = E sum_x m_x m_{x+d} m_{x+e} / P  (triple measure per point; T(0,0) = B = E sum m^3 / P)
  g_k = E #{x : m_x = k} / P                 (multiplicity distribution; sum k g_k = 1)
  simple fraction = g_1.

Levels of relaxation implemented here (all as LPs via scipy/HiGHS, optional SDP via cvxpy):
  L1  pair measure LP        : nu >= 0, pair data, [F >= 0 beyond the band]          -> max A
  L2  L1 + Yamada integrality: Var N(B) >= theta(1-theta) for intervals/unions B     -> max A
  L3  pair+triple tensor LP  : T >= 0, marginals, integrality inequalities, [RS data] -> min g_1
  L4  exact LP over configurations (all multisets), pair data only                    -> min g_1
  L5  exact LP over configurations, pair + RS triple data                             -> min g_1
"""
import itertools
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix, csr_matrix

# ---------------------------------------------------------------- basic index helpers

def rs_triples(P, L, strict=True):
    """All (k1,k2,k3), 0<k1<=k2 (positive), k3=-(k1+k2)<0, with |k1|+|k2|+|k3| < 2P (strict) or <= 2P.
    Every RS-band triple is a permutation/sign-flip of one of these (up to reflection), so imposing
    the real part of E[S_k1 S_k2 S_k3] = 0 on this list is the full RS constraint set for a
    reflection-symmetric law.  Requires M = L/P >= 3 so that no wrap-around (sum k = +-L) occurs."""
    out = []
    lim = 2 * P
    for k1 in range(1, P):
        for k2 in range(k1, P):
            s = 2 * (k1 + k2)
            if (s < lim) if strict else (s <= lim):
                if k1 + k2 < L // 2 + 1:  # keep k3 representable without aliasing
                    out.append((k1, k2, -(k1 + k2)))
    return out


def pair_cos_matrix(L):
    """C[k, d] = cos(2 pi k d / L) for k = 0..L//2, d = 0..L//2, with the multiplicity factor for
    +-d already included: row k gives sum_{d in Z/L} nu_d cos(2 pi k d/L) when applied to the
    half-vector (nu_0, nu_1, ..., nu_{L/2})."""
    H = L // 2
    k = np.arange(H + 1)[:, None]
    d = np.arange(H + 1)[None, :]
    C = np.cos(2 * np.pi * k * d / L)
    mult = np.full(H + 1, 2.0)
    mult[0] = 1.0
    if L % 2 == 0:
        mult[H] = 1.0
    return C * mult[None, :]


def interval_pair_counts(L, ell):
    """n_B(d) for B = {0,...,ell-1} on Z/L: number of ordered pairs (x,y) in B^2 with y-x = d mod L,
    returned as a half-vector over d = 0..L//2 (pairs at +-d merged)."""
    H = L // 2
    n = np.zeros(L)
    for d in range(-(ell - 1), ell):
        n[d % L] += ell - abs(d)
    half = np.zeros(H + 1)
    half[0] = n[0]
    for d in range(1, H + 1):
        half[d] = n[d] + (n[L - d] if d != L - d else 0.0)
    return half


def set_pair_counts(L, B):
    """n_B(d) half-vector for an arbitrary subset B of Z/L."""
    H = L // 2
    n = np.zeros(L)
    B = list(B)
    for x in B:
        for y in B:
            n[(y - x) % L] += 1
    half = np.zeros(H + 1)
    half[0] = n[0]
    for d in range(1, H + 1):
        half[d] = n[d] + (n[L - d] if d != L - d else 0.0)
    return half


# ---------------------------------------------------------------- L1 / L2: pair measure LP

def pair_lp(P, M, positivity=True, yamada=False, yamada_unions=0, edge_closed=False,
            extra_rows=None, return_res=False):
    """max A over half-vectors nu = (nu_0..nu_{L/2}) >= 0 with
        sum_d nu_d cos(2 pi k d/L) = k/P   (1 <= k <= P-1; also k = P if edge_closed)
        sum_d nu_d                 = P     (k = 0)
        sum_d nu_d cos(...)        >= 0    (P <= k <= L/2)      if positivity
        Yamada: for intervals B (and optionally unions of two intervals) with N = N(B):
                E N^2 - (2j+1) E N + j(j+1) >= 0, j = floor(E N), E N = |B|/M,
                E N^2 = (P/L) sum_d n_B(d) nu_d.
    Returns dict with A (=max), delta = 2 - A, and the dual certificate (multipliers)."""
    L = M * P
    H = L // 2
    nvar = H + 1
    C = pair_cos_matrix(L)
    # equalities
    kmax_eq = P if edge_closed else P - 1
    A_eq = C[0:kmax_eq + 1, :]
    b_eq = np.arange(kmax_eq + 1) / P
    b_eq[0] = P
    # inequalities  (linprog uses A_ub x <= b_ub)
    rows, rhs = [], []
    if positivity:
        for k in range(kmax_eq + 1, H + 1):
            rows.append(-C[k, :]); rhs.append(0.0)
    if yamada:
        sets = [list(range(ell)) for ell in range(1, L)]
        if yamada_unions:
            # unions of two intervals of equal length a, separated by gap: [0,a) U [a+gap, 2a+gap)
            for a in range(1, min(yamada_unions, L // 4) + 1):
                for gap in range(1, min(3 * M, L - 2 * a)):
                    sets.append(list(range(a)) + list(range(a + gap, 2 * a + gap)))
        for B in sets:
            nB = set_pair_counts(L, B) if len(B) != B[-1] + 1 else interval_pair_counts(L, len(B))
            EN = len(B) / M
            j = int(np.floor(EN + 1e-12))
            # (P/L) nB . nu - (2j+1) EN + j(j+1) >= 0  ->  -(P/L) nB . nu <= -(2j+1)EN + j(j+1)
            rows.append(-(P / L) * nB); rhs.append(-(2 * j + 1) * EN + j * (j + 1))
    if extra_rows is not None:
        for r, b in extra_rows:
            rows.append(r); rhs.append(b)
    A_ub = np.array(rows) if rows else None
    b_ub = np.array(rhs) if rows else None
    c = np.zeros(nvar); c[0] = -1.0      # maximize nu_0 = A
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
    if res.status != 0:
        raise RuntimeError(f"pair_lp failed: {res.message}")
    A = -res.fun
    out = dict(P=P, M=M, L=L, A=A, delta=2 - A, nu=res.x, eq_marg=res.eqlin.marginals,
               ineq_marg=(res.ineqlin.marginals if rows else None), n_ineq=len(rows))
    if return_res:
        out["res"] = res
    return out


# ---------------------------------------------------------------- L3: triple tensor LP

def triple_orbits(L):
    """Orbits of ordered pairs (d,e) in (Z/L)^2 under the symmetries of T(d,e)=E sum_x m_x m_{x+d} m_{x+e}/P:
    (d,e)->(e,d), (d,e)->(-d,e-d) [re-basing], and reflection (d,e)->(-d,-e).  Returns idx[d,e] and
    the number of orbits."""
    idx = -np.ones((L, L), dtype=int)
    reps = []
    for d in range(L):
        for e in range(L):
            if idx[d, e] >= 0:
                continue
            pts = [0, d, e]
            forms = set()
            for base in pts:
                rel = sorted(((p - base) % L) for p in pts)  # includes 0
                a, b = rel[1], rel[2]
                forms.add((a, b)); forms.add((b, a))
                forms.add(((-a) % L, (-b) % L)); forms.add(((-b) % L, (-a) % L))
            # close under re-basing of reflected forms as well
            closed = set()
            stack = list(forms)
            while stack:
                a, b = stack.pop()
                if (a, b) in closed:
                    continue
                closed.add((a, b))
                for na, nb in [(b, a), ((-a) % L, (b - a) % L), ((-b) % L, (a - b) % L),
                               ((-a) % L, (-b) % L)]:
                    if (na, nb) not in closed:
                        stack.append((na, nb))
            o = len(reps)
            for a, b in closed:
                idx[a, b] = o
            reps.append(min(closed))
    return idx, len(reps)


def triple_lp(P, M, rs_data=True, yamada=True, sdp=False, positivity=True, verbose=False,
              extra_integrality=True, triple_yamada=True):
    """min g_1 over (nu, T, g, A, B) subject to the L3 constraints.  If sdp=True the localized
    moment matrices [[1, E m_x],[E m_x', E m_x m_x']] >= 0 and [[E m_0, E m_0 m_x],[., E m_0 m_x m_x']] >= 0
    are added and the problem is solved with cvxpy/Clarabel."""
    L = M * P
    H = L // 2
    idx, nT = triple_orbits(L)
    # variable layout: nu[0..H], T[0..nT-1], g[1..P] (index k-1)
    n_nu, n_g = H + 1, P
    off_T = n_nu
    off_g = n_nu + nT
    nvar = off_g + n_g
    Cpair = pair_cos_matrix(L)
    eq_rows, eq_rhs = [], []
    ub_rows, ub_rhs = [], []

    def row():
        return np.zeros(nvar)

    # pair data
    for k in range(0, P):
        r = row(); r[:n_nu] = Cpair[k]
        eq_rows.append(r); eq_rhs.append(P if k == 0 else k / P)
    if positivity:
        for k in range(P, H + 1):
            r = row(); r[:n_nu] = -Cpair[k]
            ub_rows.append(r); ub_rhs.append(0.0)
    # marginals: sum_e T(d,e) = P nu_d  for d = 0..H
    for d in range(H + 1):
        r = row()
        for e in range(L):
            r[off_T + idx[d, e]] += 1.0
        r[d] -= P
        eq_rows.append(r); eq_rhs.append(0.0)
    # multiplicity distribution: sum k g_k = 1 ; sum k^2 g_k = nu_0 ; sum k^3 g_k = T(0,0)
    r = row(); r[off_g:off_g + n_g] = np.arange(1, P + 1); eq_rows.append(r); eq_rhs.append(1.0)
    r = row(); r[off_g:off_g + n_g] = np.arange(1, P + 1) ** 2; r[0] -= 1; eq_rows.append(r); eq_rhs.append(0.0)
    r = row(); r[off_g:off_g + n_g] = np.arange(1, P + 1) ** 3; r[off_T + idx[0, 0]] -= 1; eq_rows.append(r); eq_rhs.append(0.0)
    # RS triple data (real parts)
    trip = rs_triples(P, L) if rs_data else []
    for (k1, k2, k3) in trip:
        r = row()
        for d in range(L):
            for e in range(L):
                r[off_T + idx[d, e]] += np.cos(2 * np.pi * (k2 * d + k3 * e) / L)
        eq_rows.append(r); eq_rhs.append(0.0)
    if extra_integrality:
        # E sum m_x (m_x - 1) m_{x+d} >= 0  :  T(0,d) - nu_d >= 0
        # E sum (m_x-1)(m_x-2) m_{x+d} >= 0 :  T(0,d) - 3 nu_d + 2 >= 0
        for d in range(H + 1):
            r = row(); r[off_T + idx[0, d]] -= 1; r[d] += 1; ub_rows.append(r); ub_rhs.append(0.0)
            r = row(); r[off_T + idx[0, d]] -= 1; r[d] += 3; ub_rows.append(r); ub_rhs.append(2.0)
    if yamada:
        for ell in range(1, L):
            B = list(range(ell))
            nB = interval_pair_counts(L, ell)
            EN = ell / M
            j = int(np.floor(EN + 1e-12))
            r = row(); r[:n_nu] = -(P / L) * nB
            ub_rows.append(r); ub_rhs.append(-(2 * j + 1) * EN + j * (j + 1))
            if triple_yamada:
                # E N(N-1)(N-2) >= 0 and E N (N-j)(N-j-1) >= 0 for j >= 1 with N = N(B):
                # E N^3 = (P/L) sum_{x,y,z in B} T(y-x, z-x)
                r3 = row()
                for x in B:
                    for y in B:
                        for z in B:
                            r3[off_T + idx[(y - x) % L, (z - x) % L]] += P / L
                r2 = row(); r2[:n_nu] = (P / L) * nB
                # N^3 - 3N^2 + 2N >= 0
                r = -(r3 - 3 * r2); ub_rows.append(r); ub_rhs.append(2 * EN)
                for jj in range(1, j + 2):
                    # N (N-jj)(N-jj-1) = N^3 - (2jj+1) N^2 + jj(jj+1) N >= 0
                    r = -(r3 - (2 * jj + 1) * r2); ub_rows.append(r); ub_rhs.append(jj * (jj + 1) * EN)
    A_eq = np.array(eq_rows); b_eq = np.array(eq_rhs)
    A_ub = np.array(ub_rows) if ub_rows else None; b_ub = np.array(ub_rhs) if ub_rows else None
    c = np.zeros(nvar); c[off_g] = 1.0   # min g_1
    if not sdp:
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
        if res.status != 0:
            raise RuntimeError(f"triple_lp failed: {res.message}")
        x = res.x
        return dict(P=P, M=M, L=L, value=res.fun, A=x[0], B=x[off_T + idx[0, 0]], g=x[off_g:], nT=nT,
                    n_eq=len(eq_rows), n_ub=len(ub_rows), rs=len(trip))
    import cvxpy as cp
    x = cp.Variable(nvar, nonneg=True)
    cons = [A_eq @ x == b_eq]
    if A_ub is not None:
        cons.append(A_ub @ x <= b_ub)
    # moment matrix 1: [[1, E m_x],[E m_x', E m_x m_x']]  (E m_x = 1/M, E m_x m_x' = (P/L) nu_{x'-x})
    nu_full = cp.hstack([x[min(d, L - d)] for d in range(L)])
    Mat1 = [[cp.Constant(1.0)] + [cp.Constant(1.0 / M)] * L]
    # build as expression via known linear maps
    # Gram G[x,x'] = (P/L) nu_{(x'-x) mod L}
    G = cp.vstack([cp.hstack([(P / L) * x[min((xp - xx) % L, L - (xp - xx) % L)] for xp in range(L)]) for xx in range(L)])
    top = cp.hstack([cp.Constant(np.array([[1.0]])), cp.Constant(np.full((1, L), 1.0 / M))])
    bottom = cp.hstack([cp.Constant(np.full((L, 1), 1.0 / M)), G])
    M1 = cp.vstack([top, bottom])
    cons.append(M1 >> 0)
    # localized by m_0 >= 0: [[E m_0, E m_0 m_x],[E m_0 m_x', E m_0 m_x m_x']]
    #   E m_0 = 1/M ; E m_0 m_x = (P/L) nu_x ; E m_0 m_x m_x' = (P/L) T(x, x')
    TT = cp.vstack([cp.hstack([(P / L) * x[off_T + idx[xx, xp]] for xp in range(L)]) for xx in range(L)])
    top2 = cp.hstack([cp.Constant(np.array([[1.0 / M]])), cp.reshape((P / L) * nu_full, (1, L), order="C")])
    bottom2 = cp.hstack([cp.reshape((P / L) * nu_full, (L, 1), order="C"), TT])
    M2 = cp.vstack([top2, bottom2])
    cons.append(M2 >> 0)
    prob = cp.Problem(cp.Minimize(c @ x), cons)
    prob.solve(solver=cp.CLARABEL, verbose=verbose)
    if prob.status not in ("optimal", "optimal_inaccurate"):
        raise RuntimeError(f"triple SDP failed: {prob.status}")
    xv = x.value
    return dict(P=P, M=M, L=L, value=prob.value, A=xv[0], B=xv[off_T + idx[0, 0]], g=xv[off_g:], nT=nT,
                n_eq=len(eq_rows), n_ub=len(ub_rows), rs=len(trip), status=prob.status)


# ---------------------------------------------------------------- L4 / L5: exact LP over configurations

def enumerate_stats(P, M, chunk=400_000, max_mult=None, verbose=True):
    """Enumerate all multisets of P sites on Z/L (L = M P), i.e. all m in Z_{>=0}^L with sum m = P,
    and return the deduplicated table of (pair form factor F(k), k=1..P-1 ; RS triple moments ;
    simple fraction s ; A ; B).  Deduplication keeps, for each distinct constraint column, the
    minimal simple fraction (only that column can be used by the minimizing LP).
    Returns dict with arrays: cols (n x (P-1+n_rs)), s, A, B, n_configs, keys."""
    L = M * P
    trip = rs_triples(P, L)
    n_rs = len(trip)
    gen = itertools.combinations_with_replacement(range(L), P)
    n_total = 0
    tables = {}
    kk = np.arange(1, P)
    while True:
        buf = np.fromiter(itertools.chain.from_iterable(itertools.islice(gen, chunk)), dtype=np.int16)
        if buf.size == 0:
            break
        nconf = buf.size // P
        buf = buf.reshape(nconf, P)
        n_total += nconf
        if max_mult is not None:
            pass
        rows = np.repeat(np.arange(nconf), P)
        m = np.bincount(rows * L + buf.ravel(), minlength=nconf * L).reshape(nconf, L).astype(np.float64)
        S = np.fft.fft(m, axis=1)              # S[:, k], k = 0..L-1
        F = (np.abs(S[:, 1:P]) ** 2) / P       # F(k), k=1..P-1
        cols = [F]
        if n_rs:
            R = np.empty((nconf, n_rs))
            for i, (k1, k2, k3) in enumerate(trip):
                R[:, i] = np.real(S[:, k1] * S[:, k2] * S[:, k3 % L]) / P
            cols.append(R)
        cols = np.hstack(cols)
        s = (m == 1).sum(axis=1) / P
        A = (m ** 2).sum(axis=1) / P
        B = (m ** 3).sum(axis=1) / P
        key = np.round(cols, 9)
        # dedup within chunk keeping min s
        order = np.lexsort(np.vstack([s, key.T[::-1]]))  # sort by key then s
        key_s = key[order]
        uniq_mask = np.ones(nconf, dtype=bool)
        uniq_mask[1:] = np.any(key_s[1:] != key_s[:-1], axis=1)
        sel = order[uniq_mask]
        for j in sel:
            kt = tuple(key[j])
            if kt not in tables or s[j] < tables[kt][0]:
                tables[kt] = (s[j], A[j], B[j])
        if verbose:
            print(f"  enumerated {n_total} configurations, {len(tables)} distinct columns", flush=True)
    keys = np.array(list(tables.keys()))
    vals = np.array(list(tables.values()))
    return dict(P=P, M=M, L=L, cols=keys, s=vals[:, 0], A=vals[:, 1], B=vals[:, 2], n_configs=n_total,
                trip=trip, n_rs=n_rs)


def exact_lp(stats, use_rs=True, edge_closed=False):
    """min E s over probability vectors on the deduplicated columns with pair data (and RS data)."""
    P = stats["P"]
    cols = stats["cols"]
    n = cols.shape[0]
    Aeq = [np.ones(n)]
    beq = [1.0]
    for k in range(1, P):
        Aeq.append(cols[:, k - 1]); beq.append(k / P)
    if use_rs:
        for i in range(stats["n_rs"]):
            Aeq.append(cols[:, P - 1 + i]); beq.append(0.0)
    A_eq = np.array(Aeq); b_eq = np.array(beq)
    res = linprog(stats["s"], A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
    if res.status != 0:
        return dict(status=res.status, message=res.message, value=np.nan)
    pi = res.x
    return dict(status=0, value=res.fun, A=float(pi @ stats["A"]), B=float(pi @ stats["B"]),
                support=int((pi > 1e-9).sum()), pi=pi)
