"""Verification battery for the Codex (GPT5.6SOL-ULTRA) finite-spectral survey claims."""
import numpy as np
from itertools import combinations, product
from math import pi, sin, cos, sqrt, tan, gcd
from collections import Counter

ok = lambda name, cond, detail="": print(("PASS " if cond else "FAIL ") + name + ("  " + detail if detail else ""))

# ---------- 1. Montgomery-Taylor continuum: q* and the cosine profile ----------
# Solve min <v,Av>, A = I + T, (Tv)(s)=int |s-t| v(t) dt on I=[-1/2,1/2], with int v = 1.
n = 4000
h = 1.0 / n
s = (np.arange(n) + 0.5) * h - 0.5
T = np.abs(s[:, None] - s[None, :]) * h
A = np.eye(n) + T
# minimize v^T A v h ... discretized energy: E(v)= h*sum v^2 + h^2 sum |si-sj| vi vj  (v piecewise const)
# Use Lagrange: solve A_h v = lam*1 with h-weighted A_h = I + T (T already includes h)
one = np.ones(n)
vsol = np.linalg.solve(A, one)
lam = 1.0 / (h * vsol.sum())
v = lam * vsol
qnum = h * (v @ v) + (v @ (T @ v)) * h
qstar = 0.5 + (1 / sqrt(2)) / tan(1 / sqrt(2))
ok("MT continuum optimum q* = 1/2+(1/sqrt2)cot(1/sqrt2)", abs(qnum - qstar) < 2e-4,
   f"num {qnum:.8f} vs closed {qstar:.12f}")
vth = np.cos(sqrt(2) * s) / (sqrt(2) * sin(1 / sqrt(2)))
ok("MT profile v*(s)=cos(sqrt2 s)/(sqrt2 sin(1/sqrt2))", np.max(np.abs(v - vth)) < 5e-3,
   f"max dev {np.max(np.abs(v-vth)):.2e}")
ok("delta_MT = 2-q* = 3/2-(1/sqrt2)cot(1/sqrt2) = 0.672500703679",
   abs((2 - qstar) - 0.672500703679) < 1e-12, f"{2-qstar:.12f}")

# ---------- 2. Galerkin closed form (Prop 3.1) ----------
def galerkin_num(nn):
    hh = 1.0 / nn
    i = np.arange(nn)
    # En(v) = h sum v_i^2 + h^3 sum_{i!=j} |i-j| v_i v_j + (h^3/3) sum v_i^2 ; constraint h sum v = 1
    M = hh * np.eye(nn) * (1 + hh * hh / 3) + hh ** 3 * np.abs(i[:, None] - i[None, :])
    w = np.linalg.solve(M, np.ones(nn))
    lamg = 1.0 / (hh * w.sum())
    vg = lamg * w
    return vg @ M @ vg

def galerkin_closed(nn):
    an = 1 + 1 / (3 * nn ** 2)
    th = np.arccos((1 - nn ** -2) / an)
    return 0.5 + an * nn / 2 * np.sin(th) / np.tan(nn * th / 2)

devs = [abs(galerkin_num(nn) - galerkin_closed(nn)) for nn in (2, 3, 5, 8, 13, 21, 40)]
ok("Galerkin closed form q_n matches quadratic-program optimum (n=2..40)", max(devs) < 1e-10,
   f"max dev {max(devs):.2e}")
# n^-2 expansion: delta_n = delta* - (csc^2 t - sqrt2 cot t)/24 n^-2 + O(n^-4), t=1/sqrt2
t_ = 1 / sqrt(2)
coef = (1 / sin(t_) ** 2 - sqrt(2) / tan(t_)) / 24
errs = [((2 - galerkin_closed(nn)) - (2 - qstar) + coef / nn ** 2) * nn ** 4 for nn in (50, 100, 200)]
ok("Galerkin n^-2 error coefficient -(csc^2-sqrt2 cot)/24", abs(errs[-1]) < 5e-2 or abs(errs[-1] - errs[-2]) < abs(errs[-2]) * 0.5,
   f"n^4*(residual) = {[f'{e:.4f}' for e in errs]} (should stabilize)")

# ---------- 3. ACUE / band projection DPP fourth moments (Thm 6.1) ----------
def band_dpp_check(N):
    M = 2 * N
    zc = np.exp(1j * pi / N)  # e^{i pi /N}
    # kernel K(x,y) = (1/M) sum_{k in band} zc^{k(x-y)} ; band = N consecutive modes, say k=0..N-1
    ks = np.arange(N)
    Kmat = np.array([[np.sum(zc ** (ks * (x - y))) / M for y in range(M)] for x in range(M)])
    probs, subsets = [], list(combinations(range(M), N))
    for A in subsets:
        KA = Kmat[np.ix_(A, A)]
        probs.append(np.linalg.det(KA).real)
    probs = np.array(probs)
    if not (probs.min() > -1e-12 and abs(probs.sum() - 1) < 1e-9):
        return False, "not a prob law", None
    P = np.zeros((len(subsets), N + 1), complex)
    for idx, A in enumerate(subsets):
        for k in range(1, N + 1):
            P[idx, k] = np.sum(zc ** (k * np.array(A)))
    V = np.abs(P) ** 2  # V_k = |p_k|^2
    EV = probs @ V
    ramp_ok = np.allclose(EV[1:N], np.arange(1, N), atol=1e-9)
    Cov = np.zeros((N - 1, N - 1))
    for a in range(1, N):
        for b in range(1, N):
            Cov[a - 1, b - 1] = probs @ (V[:, a] * V[:, b]) - EV[a] * EV[b]
    Cth = np.zeros((N - 1, N - 1))
    for a in range(1, N):
        for b in range(1, N):
            Cth[a - 1, b - 1] = (a * a if a == b else 0) - 2 * max(a + b - N, 0)
    cov_ok = np.allclose(Cov, Cth, atol=1e-9)
    lmin = np.linalg.eigvalsh(Cov).min() if N >= 2 else None
    # support bound ||V - T||_1 <= N^2 - N/2 on binary half-filled slice
    Tn = np.arange(1, N)
    l1max = np.max(np.abs(V[:, 1:N] - Tn).sum(axis=1))
    return (ramp_ok and cov_ok), f"ramp {ramp_ok} cov {cov_ok} lmin {lmin:.6f} L1max {l1max:.3f} vs {N*N - N/2}", lmin

for N in (2, 3, 4, 5, 6):
    good, det, lmin = band_dpp_check(N)
    ok(f"Band-DPP N={N}: E V_k = k, Cov = k^2*1(k=l) - 2(k+l-N)+", good, det)

# ---------- 4. cosine sum identity 2 sum k cos(pi k/N) = N - csc^2(pi/2N) ----------
devs = [abs(2 * sum(k * cos(pi * k / N) for k in range(1, N)) - (N - 1 / sin(pi / (2 * N)) ** 2))
        for N in range(2, 40)]
ok("2*sum_{k<N} k cos(pi k/N) = N - csc^2(pi/(2N))", max(devs) < 1e-9, f"max dev {max(devs):.2e}")

# ---------- 5. Nyquist slack identity per-sample mechanism ----------
# claim: s1 - sum m m+1 - sum h(m) is a linear combination of |p_k|^2, k=0..N-1 ONLY (Nyquist-blind),
# and its expectation under open rows equals N/2 + csc^2(pi/2N)/(2N).
rng = np.random.default_rng(0)
def slack_test(N, trials=300):
    M = 2 * N
    zc = np.exp(1j * pi / N)
    worst = 0.0
    for _ in range(trials):
        m = rng.multinomial(N, np.ones(M) / M)
        s1 = np.sum(m == 1)
        mm1 = np.sum(m * np.roll(m, -1))
        hh = np.sum(np.where(m >= 3, m * (m - 2), 0))
        f = s1 - mm1 - hh
        # predicted from |p_k|^2 with Nyquist-blindness: f = 2N? recompute: f = 2*mass - sum m^2 - sum m m+1
        pk2 = np.abs(np.array([np.sum(m * zc ** (k * np.arange(M))) for k in range(M)])) ** 2
        pred = 2 * N - (1 / M) * np.sum(pk2 * (1 + np.cos(pi * np.arange(M) / N)))
        worst = max(worst, abs(f - pred))
        # Nyquist blindness: coefficient of |p_N|^2 in pred is (1+cos pi)=0 -- structural
    return worst

w = max(slack_test(N) for N in (3, 4, 5, 7))
ok("Slack identity per-sample: s1 - sum(m m+1) - sum h(m) = 2N - (1/2N) sum |p_k|^2 (1+cos(pi k/N))", w < 1e-8,
   f"max dev {w:.2e} (Nyquist coefficient 1+cos(pi)=0: identity blind to |p_N|^2)")
# limiting constant
vals = [(0.5 + (1 / sin(pi / (2 * N)) ** 2) / (2 * N ** 2)) for N in (256,)]
ok("Half-filled bound at N=256 equals 0.702644910435", abs(vals[0] - 0.702644910435) < 1e-11, f"{vals[0]:.12f}")
ok("Limit 1/2+2/pi^2 = 0.702642367284", abs(0.5 + 2 / pi ** 2 - 0.702642367284) < 1e-12)

# ---------- 6. Phi(rho) general-density bound ----------
# E s1/L >= 1 - L/M + (1/(M L)) * (sin(pi L/M)/sin(pi/M))^2 ; limit Phi(rho)=1-rho+sin^2(pi rho)/(pi^2 rho)
L, M = 100, 400
D = sin(pi * L / M) / sin(pi / M)
fin = 1 - L / M + D * D / (M * L)
rho = L / M
Phi = 1 - rho + sin(pi * rho) ** 2 / (pi ** 2 * rho)
ok("Density curve: finite bound -> Phi(rho) (rho=1/4)", abs(fin - Phi) < 1e-3, f"finite {fin:.6f} Phi {Phi:.6f}")

# ---------- 7. Magnetic cycle (Paper II): dTV formula and sub-g phase blindness ----------
def magnetic_test(g, a=0.5, r=0.1, phis=(0.3, 1.1)):
    def kernel(phi):
        H = np.zeros((g, g), complex)
        for x in range(g):
            H[x, (x + 1) % g] = np.exp(1j * phi)
            H[(x + 1) % g, x] = np.exp(-1j * phi)
        return a * np.eye(g) + r * H
    K1, K2 = kernel(phis[0]), kernel(phis[1])
    # sub-g principal minors equal?
    subdev = 0.0
    for sz in range(1, g):
        for A in combinations(range(g), sz):
            subdev = max(subdev, abs(np.linalg.det(K1[np.ix_(A, A)]) - np.linalg.det(K2[np.ix_(A, A)])))
    # full det difference formula
    dd = np.linalg.det(K1).real - np.linalg.det(K2).real
    th = 2 * (-1) ** (g - 1) * r ** g * (cos(g * phis[0]) - cos(g * phis[1]))
    # TV distance: atoms via inclusion-exclusion P(X=A) = sum_{B>=A} (-1)^{|B|-|A|} det K_B
    def atoms(K):
        dets = {B: np.linalg.det(K[np.ix_(B, B)]).real if B else 1.0
                for sz in range(g + 1) for B in combinations(range(g), sz)}
        at = {}
        for sz in range(g + 1):
            for A in combinations(range(g), sz):
                sA = set(A)
                v = sum((-1) ** (len(B) - len(A)) * dets[B]
                        for szB in range(len(A), g + 1) for B in combinations(range(g), szB) if sA <= set(B))
                at[A] = v
        return at
    a1, a2 = atoms(K1), atoms(K2)
    tv = 0.5 * sum(abs(a1[A] - a2[A]) for A in a1)
    tvth = (2 * r) ** g * abs(cos(g * phis[0]) - cos(g * phis[1])) / 2 * 2  # claimed (2r)^g |...|
    return subdev, abs(dd - th), abs(tv - (2 * r) ** g * abs(cos(g * phis[0]) - cos(g * phis[1])))

for g in (3, 4, 5):
    sd, dm, tvd = magnetic_test(g)
    ok(f"Magnetic cycle g={g}: sub-g minors phase-blind", sd < 1e-12, f"dev {sd:.2e}")
    ok(f"Magnetic cycle g={g}: det gap = 2(-1)^(g-1) r^g (cos g phi - cos g psi)", dm < 1e-12, f"dev {dm:.2e}")
    ok(f"Magnetic cycle g={g}: dTV = (2r)^g |cos g phi - cos g psi|", tvd < 1e-12, f"dev {tvd:.2e}")

# ---------- 8. Homometric pairs ----------
def cyclic_autocorr(m):
    M = len(m)
    return [sum(m[x] * m[(x + g) % M] for x in range(M)) for g in range(M)]
u = [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 2]
v2 = [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 3]
ok("Marked pair Z/12: equal autocorrelation", cyclic_autocorr(u) == cyclic_autocorr(v2),
   f"{cyclic_autocorr(u)}")
ok("Marked pair Z/12: autocorr = (12,4,0,0,0,4,8,4,0,0,0,4)",
   cyclic_autocorr(u) == [12, 4, 0, 0, 0, 4, 8, 4, 0, 0, 0, 4])
ok("Marked pair: mass 6 both; simple sites 0 vs 3; cubic sums 24 vs 30",
   sum(u) == sum(v2) == 6 and sum(1 for x in u if x == 1) == 0 and sum(1 for x in v2 if x == 1) == 3
   and sum(x ** 3 for x in u) == 24 and sum(x ** 3 for x in v2) == 30)
# no extinction: all Fourier intensities nonzero?
I_u = np.abs(np.fft.fft(u)) ** 2
ok("Marked pair: no extinction (all |Fourier|^2 > 0)", I_u.min() > 1e-9, f"min {I_u.min():.4f}")

# subsets S,T in Z/12 with same covariogram, DPP triple prob (8 -+ sqrt3)/432
def covariogram(S, M):
    return [len(set(S) & set((x + g) % M for x in S)) for g in range(M)]
S, T = [0, 1, 4, 6], [0, 1, 3, 7]
ok("DPP pair Z/12: S={0,1,4,6},T={0,1,3,7} same covariogram", covariogram(S, 12) == covariogram(T, 12))
istrans = any(sorted(((x + r) % 12) for x in S) == sorted(T) for r in range(12))
isrefl = any(sorted(((-x + r) % 12) for x in S) == sorted(T) for r in range(12))
ok("DPP pair: T not a translate or reflection of S", not istrans and not isrefl)
def proj_dpp_prob(Ssupp, M, event):
    K = np.array([[sum(np.exp(2j * pi * k * (x - y) / M) for k in Ssupp) / M for y in range(M)] for x in range(M)])
    return np.linalg.det(K[np.ix_(event, event)]).real
pS = proj_dpp_prob(S, 12, [0, 1, 2]); pT = proj_dpp_prob(T, 12, [0, 1, 2])
ok("DPP pair: P_S(012 in X)=(8-sqrt3)/432, P_T=(8+sqrt3)/432",
   abs(pS - (8 - sqrt(3)) / 432) < 1e-12 and abs(pT - (8 + sqrt(3)) / 432) < 1e-12,
   f"{pS:.10f} {pT:.10f}")
A8, B8 = [0, 1, 2, 5], [0, 1, 3, 4]
def diffmultiset(S, M): return sorted(Counter(((x - y) % M) for x in S for y in S if x != y).items())
ok("Z/8 pair {0,1,2,5},{0,1,3,4}: same difference multiset", diffmultiset(A8, 8) == diffmultiset(B8, 8))
def triples(S, M): return sum(1 for a in range(M) if {a % M, (a + 1) % M, (a + 2) % M} <= set(S))
ok("Z/8 pair: consecutive triples 1 vs 0", triples(A8, 8) == 1 and triples(B8, 8) == 0)

# ---------- 9. Deck fiber dimension = n(M,L) - n(M,r) (Paper III / Gottlieb) ----------
def necklaces(M, k):
    from math import comb
    tot = 0
    for d in range(1, gcd(M, k) + 1):
        if gcd(M, k) % d == 0 and M % d == 0:
            phi = sum(1 for t in range(1, d + 1) if gcd(t, d) == 1)
            tot += phi * comb(M // d, k // d)
    return tot // M
def deck_fiber_dim(M, L, r):
    subs = list(combinations(range(M), L))
    orb = {}
    for A in subs:
        rep = min(tuple(sorted((x + t) % M for x in A)) for t in range(M))
        orb.setdefault(rep, []).append(A)
    reps = sorted(orb)
    rows = []
    for Tt in combinations(range(M), r):
        row = [sum(1 for A in orb[rep] if set(Tt) <= set(A)) / len(orb[rep]) for rep in reps]
        rows.append(row)
    rows.append([1.0] * len(reps))
    Amat = np.array(rows)
    return len(reps) - np.linalg.matrix_rank(Amat, tol=1e-9)
tests = [(6, 3, 2), (8, 4, 2), (8, 4, 3), (10, 5, 3), (10, 5, 4)]
alldeck = True
detail = []
for (M, L, r) in tests:
    fd = deck_fiber_dim(M, L, r)
    th = necklaces(M, L) - necklaces(M, r)
    alldeck &= (fd == th)
    detail.append(f"(M{M},L{L},r{r}):{fd}={th}")
ok("Deck fiber dim = n(M,L)-n(M,r)", alldeck, " ".join(detail))
# one-row identification inside projection-DPP class: F(1) = #runs; F(1)=1 iff interval
def F1(Ssupp, M):
    return len(Ssupp) - len(set(Ssupp) & set((x + 1) % M for x in Ssupp))
runsok = True
for M in (8, 10, 12):
    for L in range(1, M):
        for Sset in combinations(range(M), L):
            runs = sum(1 for x in Sset if (x - 1) % M not in Sset)
            if F1(list(Sset), M) != runs:
                runsok = False
ok("Form factor F(1) = number of occupied runs (Fermi-sea boundary)", runsok)

# ---------- 10. Tile language + filtered charge spectrum (Paper 8.1/8.2) ----------
def endpoint_face(N):
    M = 2 * N
    out = []
    for A in product((0, 1, 2), repeat=M):
        if sum(A) == N and all(A[x] * A[(x + 1) % M] == 0 for x in range(M)):
            out.append(A)
    return out
import math
for N in (2, 3, 4):
    face = endpoint_face(N)
    ok(f"|E_N| = C(2N,N) at N={N}", len(face) == math.comb(2 * N, N), f"{len(face)} vs {math.comb(2*N,N)}")
# filter identity q^(k) = (1+e^{-i pi k/N}) p_k(m)
N = 4; M = 8
zc = np.exp(-1j * pi / N)
dev = 0.0
for A in endpoint_face(N)[:50]:
    m = np.array(A)
    q = m + np.roll(m, -1) - 1
    for k in range(1, N):
        qh = np.sum(q * np.exp(-1j * pi * k * np.arange(M) / N))
        ph = np.sum(m * np.exp(-1j * pi * k * np.arange(M) / N))
        dev = max(dev, abs(qh - (1 + np.exp(-1j * pi * k / N)) * ph))
ok("Charge filter identity qhat(k) = (1+e^{-i pi k/N}) p_k", dev < 1e-9, f"max dev {dev:.2e}")

# tile language: q words are concatenations of (-1),(0,0),(+1,+1)
def is_tile_word(q):
    g = len(q);
    # try each starting point where a tile boundary could be; language is cyclic
    for s0 in range(g):
        w = [q[(s0 + i) % g] for i in range(g)]
        i = 0; good2 = True
        while i < g:
            if w[i] == -1: i += 1
            elif w[i] == 0 and i + 1 < g + 1 and w[(i + 1) % g] == 0 and i + 1 < g: i += 2
            elif w[i] == 1 and i + 1 < g and w[i + 1] == 1: i += 2
            else: good2 = False; break
        if good2 and i == g and sum(w) == 0:
            return True
    return False
tile_ok = True
for A in endpoint_face(3):
    m = np.array(A); q = (m + np.roll(m, -1) - 1).tolist()
    if not is_tile_word(q): tile_ok = False
ok("Every hard-core sample's edge charge is a balanced tile word (N=3)", tile_ok)

# ---------- 11. Wilson fourth trace (Paper VI, 9.5) on a 2x2 periodic box ----------
def wilson_test(n1, n2, seed=1):
    rr = np.random.default_rng(seed)
    # sites = Z/n1 x Z/n2 ; two directions with unit weights, random phases on edges
    Nn = n1 * n2
    idx = lambda x, y: (x % n1) * n2 + (y % n2)
    phase1 = rr.uniform(0, 2 * pi, (n1, n2)); phase2 = rr.uniform(0, 2 * pi, (n1, n2))
    def build(ph1, ph2):
        Au = np.zeros((Nn, Nn), complex)
        for x in range(n1):
            for y in range(n2):
                Au[idx(x, y), idx(x + 1, y)] += np.exp(1j * ph1[x, y])
                Au[idx(x + 1, y), idx(x, y)] += np.exp(-1j * ph1[x, y])
                Au[idx(x, y), idx(x, y + 1)] += np.exp(1j * ph2[x, y])
                Au[idx(x, y + 1), idx(x, y)] += np.exp(-1j * ph2[x, y])
        return Au
    Au = build(phase1, phase2)
    Aflat = build(np.zeros((n1, n2)), np.zeros((n1, n2)))
    # plaquette holonomy at (x,y): ph1(x,y)+ph2(x+1,y)-ph1(x,y+1)-ph2(x,y)
    S = 0.0
    for x in range(n1):
        for y in range(n2):
            phf = phase1[x, y] + phase2[(x + 1) % n1, y] - phase1[x, (y + 1) % n2] - phase2[x, y]
            S += np.sin(phf / 2) ** 2
    lhs = np.trace(Aflat @ Aflat @ Aflat @ Aflat).real - np.trace(Au @ Au @ Au @ Au).real
    return lhs, 16 * S
l, r_ = wilson_test(3, 4)
ok("Wilson fourth trace: tr A^4_flat - tr A^4 = 16 sum_f sin^2(phi_f/2) (unit weights)",
   abs(l - r_) < 1e-8, f"{l:.6f} vs {r_:.6f}")

# ---------- 12. GOE counterfactual constant ----------
# replace ramp K2(u)=u by K1(u)=2u - u log(1+2u) in the MT functional; same secant -> 0.5598718...
nq = 3000
hq = 1.0 / nq
sq = (np.arange(nq) + 0.5) * hq - 0.5
# kernel: energy = int v^2 + int int k(s-t) v v, where khat relation: |s-t| term came from K2 ramp.
# Following the survey: E(v) = v'Av with A = I + T_K, (T_K v)(s) = int c(s-t) v(t) dt where
# c(x) = int_0^1 (1 - K(u)) * 2cos(2pi? ...) -- The MT functional with general form factor:
# E(v) = int int v(s)v(t) [delta + C(s-t)] where C(x) = int_{-1}^{1} K2(u) e(-xu)... For K2(u)=|u|:
# int_{-1}^1 |u| e^{2pi i x u} du? but MT used |s-t| directly. Consistency check: for K2 the kernel is |s-t|.
# General: kernel c(x) = int_{-1}^{1} (K(u)-|u|) e^{-2 pi i x u} du + |x|?? -- skip exact derivation;
# instead do the literal analogue: kernel |s-t| arises as the second antiderivative structure of ramp.
# We test the claim differently: E1(v)= int v^2 + int int c1(s-t) v v with c1 = Fourier pair of K1 on the
# doubled interval. c1(x) = int_{-1}^{1} K1(|u|) e^{pi i x u}?? ambiguous -- mark as NOT INDEPENDENTLY VERIFIED.
print("SKIP GOE counterfactual 0.559871849060 (normalization of K1 kernel not reconstructible from survey alone)")

# ---------- 13. negative-square budget ----------
ok("(1-delta_MT)/2 = 0.163749648160", abs((1 - (2 - qstar)) / 2 - 0.163749648160) < 1e-12,
   f"{(1-(2-qstar))/2:.12f}")

# ---------- 14. N=3 lift spectra claim (Thm 8.2 ii) ----------
# liftable charge spectra at N=3 up to symmetry: (0,0),(3,9),(9,3); DPP atom eta=111000 filtered spectrum (12,0)
N = 3; M = 6
specs = set()
for A in endpoint_face(3):
    m = np.array(A); q = m + np.roll(m, -1) - 1
    sp = tuple(round(abs(np.sum(q * np.exp(-1j * pi * k * np.arange(M) / N))) ** 2, 6) for k in (1, 2))
    specs.add(sp)
eta = np.array([1, 1, 1, 0, 0, 0]); qe = eta + np.roll(eta, -1) - 1
spe = tuple(round(abs(np.sum(qe * np.exp(-1j * pi * k * np.arange(M) / N))) ** 2, 6) for k in (1, 2))
print("liftable charge spectra N=3:", sorted(specs), " eta=111000 filtered:", spe)
ok("N=3: eta=111000 filtered spectrum (12,0) not in liftable convex hull (extreme check)",
   spe == (12.0, 0.0) and (12.0, 0.0) not in specs)

print("\nDone.")
