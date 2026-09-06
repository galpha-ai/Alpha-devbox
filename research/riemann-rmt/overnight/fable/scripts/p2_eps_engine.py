# Vendored verbatim from the session scratchpad (earlier P2 agent, k=49/50 work) so that the
# r1_sub186_* scripts are self-contained.  Not modified.

"""P2: epsilon-trick variational problem M_{k,eps} (Polymath8b Thm 3.5 framework).

FRAMEWORK (re-derived from the sieve, see report):
  DHL(k,m+1) holds under EH[theta] if there is symmetric square-integrable
  F supported on (1+eps)*R_k  (R_k = {t in [0,inf)^k : sum t_i <= 1}),
  0 < eps < 1/theta - 1, with
        k * J_k^{1-eps}(F) / I_k(F) > 2m/theta,
  where I_k(F)        = int_{(1+eps)R_k} F^2 dt,
        J_k^{1-eps}(F)= int_{(1-eps)R_{k-1}} ( int_0^infty F dt_k )^2 dt_1..dt_{k-1}.
  With theta = 1/2 (Bombieri-Vinogradov), m=1: need  M_{k,eps} > 4.
  eps = 0 reduces to the pure Maynard-Tao M_k.

REDUCTION TO UNIT SIMPLEX. Put t = (1+eps) u, F(t) = G(u), rho = (1-eps)/(1+eps):
   I = (1+eps)^k Itil(G),  J = (1+eps)^{k+1} Jtil(G),
   Itil(G) = int_{R_k} G^2 du
   Jtil(G) = int_{rho R_{k-1}} ( int_0^{1-P1'} G(u',u) du )^2 du'
   M_{k,eps} = k (1+eps) * Jtil / Itil.

BASIS: G_(a,b) = (1-P1)^a * prod_r P_r^{b_r},  P_r = power sums, r=2..rmax,
       a + sum_r r*b_r <= d.

EXACT INTEGRALS:
  Zint(A, B; n) = int_{R_n} (1-P1)^A prod_r P_r^{B_r} du
                = sum_lam c_lam * count(lam,n) * A! prod(lam_i!) / (n+A+|lam|)!
  where prod_r p_r^{B_r} = sum_lam c_lam m_lam (monomial symmetric basis),
  count(lam,n) = n!/((n-len)! * prod_v mult_v!).

MARGINAL of G_(a,b) w.r.t. u_k, X := 1 - P1' (P1' = power sum of u'):
  int_0^X (X-u)^a u^m du = a! m! /(a+m+1)! * X^{a+m+1}
  => h_(a,b)(u') = sum_{beta<=b} [prod_r C(b_r,beta_r)] * a! m!/(a+m+1)!
                   * X^{a+m+1} prod_r P_r'^{beta_r},  m = sum_r r (b_r - beta_r).

J ENTRY (u' = rho w, w in R_{k-1}, X = (1-rho) + rho(1-Q1), P_r' = rho^r Q_r):
  Jtil[al,be] = sum over term pairs  c1*c2 * rho^{k-1+sum_r r B_r} * S(M, B; rho)
  M = M1+M2, B = beta1+beta2,
  S(M,B;rho) = sum_{j=0}^{M} C(M,j) (1-rho)^{M-j} rho^j Zint(j, B; k-1).

All positive => float accumulation is cancellation-free; exact Fraction path
used for final certification (Rayleigh quotient of a rational vector).
"""
import itertools, math, sys
from fractions import Fraction
from functools import lru_cache
import numpy as np

# ---------------- symmetric function machinery (exact) ----------------

def msym_mult_p(msdict, r, n):
    """Multiply symmetric poly (dict {sorted-desc exponent tuple: coeff}) by p_r,
    in n variables."""
    out = {}
    for lam, c in msdict.items():
        vals = set(lam) | {0}
        for v in vals:
            if v == 0 and len(lam) >= n:
                continue
            # raise one part v -> v+r  (v=0: append new part)
            lst = list(lam)
            if v == 0:
                lst.append(r)
            else:
                lst.remove(v)
                lst.append(v + r)
            mu = tuple(sorted(lst, reverse=True))
            mult = mu.count(v + r)
            out[mu] = out.get(mu, 0) + c * mult
    return {kk: vv for kk, vv in out.items() if vv != 0}

@lru_cache(maxsize=None)
def p_expansion(B, n):
    """m-basis expansion of prod_r p_{r}^{B[r-2]} (B tuple, r = 2..) in n vars."""
    d = {(): 1}
    for i, br in enumerate(B):
        r = i + 2
        for _ in range(br):
            d = msym_mult_p(d, r, n)
    return tuple(d.items())

@lru_cache(maxsize=None)
def count_lam(lam, n):
    l = len(lam)
    if l > n:
        return 0
    c = 1
    # n!/(n-l)!
    for i in range(l):
        c *= (n - i)
    mults = {}
    for v in lam:
        mults[v] = mults.get(v, 0) + 1
    for v, m in mults.items():
        c //= math.factorial(m)
    return c

@lru_cache(maxsize=None)
def Zint_f(A, B, n):
    """Float version of Zint (positive sum, no cancellation)."""
    tot = 0.0
    fA = math.factorial(A)
    for lam, c in p_expansion(B, n):
        cnt = count_lam(lam, n)
        if cnt == 0:
            continue
        num = fA * cnt * c
        for v in lam:
            num *= math.factorial(v)
        tot += num / math.factorial(n + A + sum(lam))
    return tot

@lru_cache(maxsize=None)
def Zint(A, B, n):
    """int_{R_n} (1-P1)^A prod_r P_r^{B_r} du  (exact Fraction)."""
    tot = Fraction(0)
    fA = math.factorial(A)
    for lam, c in p_expansion(B, n):
        cnt = count_lam(lam, n)
        if cnt == 0:
            continue
        num = fA * cnt * c
        for v in lam:
            num *= math.factorial(v)
        tot += Fraction(num, math.factorial(n + A + sum(lam)))
    return tot

# ---------------- basis ----------------

def basis(d, rmax):
    """List of (a, bvec) with a + sum r b_r <= d."""
    out = []
    def rec(r, rem, bv):
        if r > rmax:
            for a in range(rem + 1):
                out.append((a, tuple(bv)))
            return
        for br in range(rem // r + 1):
            rec(r + 1, rem - r * br, bv + [br])
    rec(2, d, [])
    return out

def marginal_terms(a, b):
    """List of (M, beta_tuple, coeff Fraction) for h_(a,b)."""
    terms = []
    ranges = [range(br + 1) for br in b]
    fa = math.factorial(a)
    for beta in itertools.product(*ranges):
        m = sum((i + 2) * (b[i] - beta[i]) for i in range(len(b)))
        cb = 1
        for i in range(len(b)):
            cb *= math.comb(b[i], beta[i])
        coeff = Fraction(cb * fa * math.factorial(m), math.factorial(a + m + 1))
        terms.append((a + m + 1, beta, coeff))
    return terms

# ---------------- assembly ----------------

class Engine:
    def __init__(self, k, d, rmax):
        self.k, self.d, self.rmax = k, d, rmax
        self.bas = basis(d, rmax)
        self.n = len(self.bas)
        self.mterms = [marginal_terms(a, b) for (a, b) in self.bas]
        self._coo = None      # (rows, keyids, floatvals) ; entry list self.pairs
        self._keys = None

    # ----- I matrix (float, exact path available) -----
    def I_entry_exact(self, al, be):
        a1, b1 = self.bas[al]; a2, b2 = self.bas[be]
        B = tuple(x + y for x, y in zip(b1, b2))
        return Zint(a1 + a2, B, self.k)

    def I_matrix(self):
        n = self.n
        I = np.zeros((n, n))
        for al in range(n):
            a1, b1 = self.bas[al]
            for be in range(al, n):
                a2, b2 = self.bas[be]
                B = tuple(x + y for x, y in zip(b1, b2))
                v = Zint_f(a1 + a2, B, self.k)
                I[al, be] = I[be, al] = v
        return I

    # ----- J: eps-independent COO structure -----
    def build_J_structure(self):
        keyid = {}
        keys = []
        rows, cols, vals = [], [], []
        pairs = []
        n = self.n
        # float term lists (scan path only; certification recomputes exactly)
        fterms = [[(M, beta, float(c)) for (M, beta, c) in t] for t in self.mterms]
        for al in range(n):
            t1 = fterms[al]
            for be in range(al, n):
                t2 = fterms[be]
                pidx = len(pairs)
                pairs.append((al, be))
                acc = {}
                for (M1, beta1, c1) in t1:
                    for (M2, beta2, c2) in t2:
                        key = (M1 + M2, tuple(x + y for x, y in zip(beta1, beta2)))
                        acc[key] = acc.get(key, 0.0) + c1 * c2
                for key, c in acc.items():
                    ki = keyid.get(key)
                    if ki is None:
                        ki = keyid[key] = len(keys)
                        keys.append(key)
                    rows.append(pidx)
                    cols.append(ki)
                    vals.append(c)
        from scipy.sparse import coo_matrix
        self._keys = keys
        self.pairs = pairs
        self._coo = coo_matrix((vals, (rows, cols)),
                               shape=(len(pairs), len(keys))).tocsr()

    def S_vector(self, eps):
        """Vector over keys of rho^{k-1+sum r B_r} * S(M,B;rho), floats."""
        k = self.k
        rho = float((1 - Fraction(eps)) / (1 + Fraction(eps))) if eps else 1.0
        one_m_rho = 1.0 - rho
        out = np.zeros(len(self._keys))
        # cache powers (floats; positive sums, no cancellation)
        maxM = max(K[0] for K in self._keys)
        rpow = [rho ** i for i in range(maxM + k + 3 * self.d + 4)]
        ompow = [one_m_rho ** i for i in range(maxM + 1)]
        Scache = {}
        for idx, (M, B) in enumerate(self._keys):
            key = (M, B)
            if key not in Scache:
                s = 0.0
                for j in range(M + 1):
                    z = Zint_f(j, B, k - 1)
                    if z:
                        s += math.comb(M, j) * ompow[M - j] * rpow[j] * z
                Scache[key] = s
            srb = sum((i + 2) * B[i] for i in range(len(B)))
            out[idx] = Scache[key] * rpow[k - 1 + srb]
        return out

    def J_matrix(self, eps):
        if self._coo is None:
            self.build_J_structure()
        s = self.S_vector(eps)
        flat = self._coo.dot(s)
        n = self.n
        J = np.zeros((n, n))
        for pidx, (al, be) in enumerate(self.pairs):
            J[al, be] = J[be, al] = flat[pidx]
        return J

    # ----- solve -----
    def M_value(self, eps, I=None, return_vec=False, cond_cut=1e-13):
        from scipy.linalg import eigh
        if I is None:
            I = self.I_matrix()
        J = self.J_matrix(eps)
        dg = np.sqrt(np.diag(I))
        Dn = 1.0 / dg
        In = I * Dn[:, None] * Dn[None, :]
        Jn = J * Dn[:, None] * Dn[None, :]
        # project out near-null directions of In (keeps rigorous lower bound)
        w, V = np.linalg.eigh(In)
        keep = w > cond_cut * w[-1]
        Vk = V[:, keep] / np.sqrt(w[keep])[None, :]
        A = Vk.T @ Jn @ Vk
        A = 0.5 * (A + A.T)
        ev, evec = np.linalg.eigh(A)
        lam = ev[-1]
        Mval = self.k * (1 + eps) * lam
        if return_vec:
            x = Vk @ evec[:, -1]
            x = x * Dn  # back to original basis coords
            return Mval, x
        return Mval

    # ----- exact certification -----
    def J_entry_exact(self, al, be, eps):
        k = self.k
        rho = (1 - Fraction(eps)) / (1 + Fraction(eps))
        tot = Fraction(0)
        for (M1, beta1, c1) in self.mterms[al]:
            for (M2, beta2, c2) in self.mterms[be]:
                M = M1 + M2
                B = tuple(x + y for x, y in zip(beta1, beta2))
                s = Fraction(0)
                for j in range(M + 1):
                    z = Zint(j, B, k - 1)
                    if z:
                        s += math.comb(M, j) * (1 - rho) ** (M - j) * rho ** j * z
                srb = sum((i + 2) * B[i] for i in range(len(B)))
                tot += c1 * c2 * rho ** (k - 1 + srb) * s
        return tot

    def certify_fast(self, eps, x, keep=200, den=2 ** 30, verbose=False):
        """Certified exact lower bound on M_{k,eps}: exact Rayleigh quotient of
        x truncated to its `keep` largest components (in I-normalized size).
        Any vector gives a valid lower bound. Returns (Fraction, float)."""
        import numpy as np
        k = self.k
        epsF = Fraction(eps)
        rho = (1 - epsF) / (1 + epsF)
        # exact binary conversion of every nonzero component (keep <=0: keep all)
        if keep and keep < self.n:
            diag = np.array([float(self.I_entry_exact(i, i)) for i in range(self.n)])
            score = np.abs(np.asarray(x)) * np.sqrt(diag)
            sel = set(int(i) for i in np.argsort(-score)[:keep])
        else:
            sel = set(range(self.n))
        xr = {i: Fraction(float(x[i])) for i in sel if x[i] != 0}
        idx = sorted(xr.keys())
        # exact S memo
        maxM = 2 * (self.d + 1)
        rpow = [rho ** i for i in range(maxM + k + 3 * self.d + 6)]
        ompow = [(1 - rho) ** i for i in range(maxM + 2)]
        Sm = {}
        def Sval(M, B):
            key = (M, B)
            if key not in Sm:
                s = Fraction(0)
                for j in range(M + 1):
                    z = Zint(j, B, k - 1)
                    if z:
                        s += math.comb(M, j) * ompow[M - j] * rpow[j] * z
                Sm[key] = s
            return Sm[key]
        num = Fraction(0); dnm = Fraction(0)
        for ii, al in enumerate(idx):
            for be in idx[ii:]:
                mult = 1 if al == be else 2
                cxx = mult * xr[al] * xr[be]
                # exact J entry
                jent = Fraction(0)
                for (M1, beta1, c1) in self.mterms[al]:
                    for (M2, beta2, c2) in self.mterms[be]:
                        B = tuple(a + b for a, b in zip(beta1, beta2))
                        srb = sum((i + 2) * B[i] for i in range(len(B)))
                        jent += c1 * c2 * rpow[k - 1 + srb] * Sval(M1 + M2, B)
                num += cxx * jent
                dnm += cxx * self.I_entry_exact(al, be)
        Mcert = k * (1 + epsF) * num / dnm
        if verbose:
            print(f"certify: kept {len(idx)} comps, M >= {float(Mcert):.8f}")
        return Mcert, float(Mcert)

    def certify(self, eps, x, den=2 ** 30):
        """Exact rational Rayleigh quotient k(1+eps) x^T J x / x^T I x
        for x rounded to rationals with denominator den. Returns Fraction."""
        xr = [Fraction(int(round(xi * den)), den) for xi in x]
        num = Fraction(0); dnm = Fraction(0)
        n = self.n
        for al in range(n):
            if xr[al] == 0:
                continue
            for be in range(al, n):
                if xr[be] == 0:
                    continue
                mult = 1 if al == be else 2
                num += mult * xr[al] * xr[be] * self.J_entry_exact(al, be, eps)
                dnm += mult * xr[al] * xr[be] * self.I_entry_exact(al, be)
        return self.k * (1 + Fraction(eps)) * num / dnm
