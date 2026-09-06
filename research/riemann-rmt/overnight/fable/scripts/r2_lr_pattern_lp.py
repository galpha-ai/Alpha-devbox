"""r2_lr_pattern_lp.py -- local-pattern LP for lattice-supported bandwidth-one sine mimickers.

Process: stationary 0/1 field xi on sites of (1/M)Z (random uniform shift makes it stationary on R),
P(xi_0 = 1) = 1/M (intensity 1), hard core c = k/M  <=>  q_j := P(xi_0 = xi_j = 1) = 0 for 1 <= j < k.
Spectrum.  With g = M sum_{j!=0} q_j delta_{j/M} and r_j = q_j - 1/M^2 (Poisson summation):
   S(alpha) = (1 - 1/M) + sum_{m!=0} delta_{mM} + M sum_{j!=0} r_j e^{-2 pi i alpha j/M},
so the absolutely-continuous-in-the-fundamental-domain part S_ac is M-periodic, and
   r_j = (1/M^2) int_{-M/2}^{M/2} S_ac(alpha) cos(2 pi alpha j/M) dalpha   (j != 0),
   int_{-M/2}^{M/2} S_ac = M - 1.
Mimicry: S_ac = |alpha| on (-1,1) (mass 1).  Bochner: S_ac >= 0 on [1, M/2].  So the free object is a
nonnegative measure mu on [1, M/2] (symmetric), mass 2 mu([1,M/2)) + mu({M/2}) = M - 2, and
   M^2 q_j = 1 + A_j + int cos(2 pi alpha j/M) dmu_sym(alpha),   A_j = 2 int_0^1 a cos(2 pi a j/M) da.
mu is discretised as atoms on a grid (no tail truncation of r_j is needed: every lattice process,
including AH with its Bragg peaks, is representable up to the grid resolution).
Patterns: probabilities p(w) of admissible 0/1 words w of length W (ones at mutual distance >= k):
sum p = 1, shift-consistency of the (W-1)-marginals, intensity, and q_j = sum_{w: w_0=w_j=1} p(w)
for 1 <= j <= W-1.  For W <= j <= Jmax only 0 <= q_j <= 1/M.  LP minimises the max violation s of the
q_j-equalities (scaled by M^2); feasible iff s* <= tolerance.  mode 'pair' drops the patterns.
Usage: python3 r2_lr_pattern_lp.py M k W [dalpha Jmax_mult mode]
"""
import sys, time, json
import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog

DATA = "/home/user/Alpha-devbox/research/riemann-rmt/overnight/fable/data"

def A_coef(j, M):
    th = j/M
    return np.sin(2*np.pi*th)/(np.pi*th) + (np.cos(2*np.pi*th) - 1)/(2*np.pi**2*th**2)

def admissible(W, k):
    """all sorted tuples of positions in range(W) with consecutive differences >= k"""
    out = [()]
    def rec(prefix, start):
        for p in range(start, W):
            new = prefix + (p,)
            out.append(new)
            rec(new, p + k)
    rec((), 0)
    return out

def build(M, k, W, dal=0.01, Jmax_mult=8, mode='pattern'):
    t0 = time.time()
    # spectral grid on [1, M/2]
    als = np.round(np.arange(1.0, M/2 + 1e-9, dal), 10)
    mult = np.where(np.isclose(als, M/2), 1.0, 2.0)          # symmetric atom counts once at M/2
    nA = len(als)
    Jmax = int(Jmax_mult*M)
    js = np.arange(1, Jmax + 1)
    Cos = np.cos(2*np.pi*np.outer(js, als)/M)*mult[None, :]  # Jmax x nA : int cos dmu_sym per unit atom
    Aj = A_coef(js.astype(float), M)
    rows_eq, rows_ub = [], []           # (coeff dict, rhs)
    if mode == 'pattern':
        pats = admissible(W, k); idx = {p: i for i, p in enumerate(pats)}
        nP = len(pats)
        sub = admissible(W - 1, k); sidx = {p: i for i, p in enumerate(sub)}
        nvar = nP + nA + 1                # p, mu, s
        S = nP + nA
        data, ri, ci, rhs = [], [], [], []
        r = 0
        # sum p = 1
        for i in range(nP): data.append(1.0); ri.append(r); ci.append(i)
        rhs.append(1.0); r += 1
        # intensity
        for p, i in idx.items():
            if p and p[0] == 0: data.append(1.0); ri.append(r); ci.append(i)
        rhs.append(1.0/M); r += 1
        # shift consistency: for each (W-1)-word v: sum_{w: left(w)=v} p - sum_{w: right(w)=v} p = 0
        for p, i in idx.items():
            left = tuple(x for x in p if x <= W - 2)
            right = tuple(x - 1 for x in p if x >= 1)
            data.append(1.0); ri.append(r + sidx[left]); ci.append(i)
            data.append(-1.0); ri.append(r + sidx[right]); ci.append(i)
        rhs.extend([0.0]*len(sub)); r += len(sub)
        Aeq_pat = sp.csr_matrix((data, (ri, ci)), shape=(r, nvar))
        beq_pat = np.array(rhs)
        # q_j equalities (as two inequalities with slack), j = 1..W-1:  M^2 q_j(p) - Cos_j mu - s <= 1 + A_j ; -(...) - s <= -(1+A_j)
        data, ri, ci, rhs = [], [], [], []
        r = 0
        for j in range(1, W):
            cols_p = [idx[p] for p in pats if p and p[0] == 0 and j in p]
            for sgn in (1.0, -1.0):
                for cp in cols_p: data.append(sgn*M*M); ri.append(r); ci.append(cp)
                for ia in range(nA): data.append(-sgn*Cos[j-1, ia]); ri.append(r); ci.append(nP + ia)
                data.append(-1.0); ri.append(r); ci.append(S)
                rhs.append(sgn*(1 + Aj[j-1])); r += 1
        # tail bounds j = W..Jmax:  0 <= 1 + A_j + Cos_j mu <= M
        for j in range(W, Jmax + 1):
            for ia in range(nA): data.append(-Cos[j-1, ia]); ri.append(r); ci.append(nP + ia)
            rhs.append(1 + Aj[j-1]); r += 1
            for ia in range(nA): data.append(Cos[j-1, ia]); ri.append(r); ci.append(nP + ia)
            rhs.append(M - 1 - Aj[j-1]); r += 1
        Aub = sp.csr_matrix((data, (ri, ci)), shape=(r, nvar)); bub = np.array(rhs)
        # mass
        mass = sp.csr_matrix((mult, ([0]*nA, list(range(nP, nP + nA)))), shape=(1, nvar))
        Aeq = sp.vstack([Aeq_pat, mass]).tocsr(); beq = np.concatenate([beq_pat, [M - 2.0]])
        info = dict(nP=nP, nsub=len(sub))
    else:
        # pair mode: variables q_j (j = 1..Jmax) with q_j = 0 for j < k, mu, s
        nvar = Jmax + nA + 1; S = Jmax + nA
        data, ri, ci, rhs = [], [], [], []
        r = 0
        for j in range(1, Jmax + 1):
            for sgn in (1.0, -1.0):
                data.append(sgn*M*M); ri.append(r); ci.append(j - 1)
                for ia in range(nA): data.append(-sgn*Cos[j-1, ia]); ri.append(r); ci.append(Jmax + ia)
                data.append(-1.0); ri.append(r); ci.append(S)
                rhs.append(sgn*(1 + Aj[j-1])); r += 1
        Aub = sp.csr_matrix((data, (ri, ci)), shape=(r, nvar)); bub = np.array(rhs)
        Aeq = sp.csr_matrix((mult, ([0]*nA, list(range(Jmax, Jmax + nA)))), shape=(1, nvar)); beq = np.array([M - 2.0])
        info = dict(nP=0, nsub=0)
        nP = Jmax
    bounds = [(0, None)]*nvar
    if mode == 'pair':
        for j in range(1, Jmax + 1):
            bounds[j-1] = (0, 0) if j < k else (0, 1.0/M)
    cost = np.zeros(nvar); cost[S] = 1.0
    info.update(nA=nA, nvar=nvar, n_ub=Aub.shape[0], n_eq=Aeq.shape[0], build_s=time.time() - t0)
    return cost, Aub, bub, Aeq, beq, bounds, info, S

def solve(M, k, W, dal=0.01, Jmax_mult=8, mode='pattern', want_dual=False):
    cost, Aub, bub, Aeq, beq, bounds, info, S = build(M, k, W, dal, Jmax_mult, mode)
    t0 = time.time()
    res = linprog(cost, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq, bounds=bounds, method='highs',
                  options=dict(presolve=True))
    info['solve_s'] = time.time() - t0; info['status'] = int(res.status)
    s = res.fun if res.status == 0 else np.inf
    out = dict(M=M, k=k, c=k/M, W=W, dal=dal, Jmax_mult=Jmax_mult, mode=mode, s=float(s), info=info)
    if want_dual and res.status == 0:
        out['x'] = res.x; out['dual_ub'] = res.ineqlin.marginals; out['dual_eq'] = res.eqlin.marginals
    return out

if __name__ == "__main__":
    M, k, W = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    dal = float(sys.argv[4]) if len(sys.argv) > 4 else 0.01
    Jm = int(sys.argv[5]) if len(sys.argv) > 5 else 8
    mode = sys.argv[6] if len(sys.argv) > 6 else 'pattern'
    out = solve(M, k, W, dal, Jm, mode)
    print(json.dumps(out))
    with open(f"{DATA}/r2_lr_pattern_results.jsonl", "a") as f:
        f.write(json.dumps(out) + "\n")
