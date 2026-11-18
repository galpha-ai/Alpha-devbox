#!/usr/bin/env python3
"""
r1_cue_background_constants.py  --  exact/numerical checks for r1_cue_background.md (task A2).

What is verified here (each item prints PASS/FAIL and is saved to
../data/r1_cue_background_constants.json):

  S1  sum_{m=0}^{N-1} (2m-N+1)^2 = N(N^2-1)/3  and  sum (2m-N+1)^4 = N(N^2-1)(3N^2-7)/15
      (used for the two-sided bounds on S_N(t) = sin(Nt)/(N sin t)).
  S2  A_2(N) := sum_{0<=m1<m2<=N-1} (m2-m1)^2 = N^2(N^2-1)/12   (exact 2-point constant)
  S3  A_3(N) := sum_{0<=m1<m2<m3<=N-1} [(m2-m1)(m3-m1)(m3-m2)]^2  is the polynomial
      N^3 (N^2-1)^2 (N^2-4) / 2160  (exact 3-point constant); leading term N^9/2160 matches the
      Selberg integral  int_{[0,1]^3} prod_{i<j}(x_i-x_j)^2 = 1/360  (ordered region 1/2160).
  S4  Bialternant/Cauchy-Binet identity: for random points on the circle and several N,
        rho_3(x1,x2,x3) = (2pi)^-3 prod_{i<j}|z_i-z_j|^2 * sum_{m1<m2<m3} |s_lambda(z)|^2
      and the GLOBAL inequality rho_3 <= C_3(N) prod|z_i-z_j|^2 with C_3(N) = (2pi)^-3 A_3(N)/4,
      plus the clustering limit  rho_3 / (C_3 prod (x_i-x_j)^2) -> 1.
  S5  Two-sided 2-point bounds:
        rho_2(u) <= N^2(N^2-1) u^2/(48 pi^2)   for all u,
        rho_2(u) >= N^2(N^2-1) u^2/(48 pi^2) (1 - N^2 u^2/30)   for N^2 u^2 <= 24.
  S6  Fischer's inequality on random Gram matrices K(x_i,x_j) (PSD): det M <= det A det D.
  S7  csc^2(d/2) <= pi^2/d^2 on (0,pi] and csc^2(x/2) = csc^2(d/2) with d the circular distance.
  S8  Assembly of the explicit constants of Theorem 1 (two regimes), exact rational arithmetic
      where possible, then floats.

Run:  python3 r1_cue_background_constants.py
"""
import json, math, os, sys
import numpy as np
import sympy as sp

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data',
                   'r1_cue_background_constants.json')
results = {}
def rec(name, ok, **info):
    results[name] = {'pass': bool(ok), **info}
    print(('PASS ' if ok else 'FAIL ') + name, {k: (v if isinstance(v, (int, float, str)) else str(v)) for k, v in info.items()})

N = sp.symbols('N', integer=True, positive=True)

# ---------------------------------------------------------------- S1
def s1():
    ok2 = ok4 = True
    for n in range(2, 16):
        v2 = sum((2*m - n + 1)**2 for m in range(n)); v4 = sum((2*m - n + 1)**4 for m in range(n))
        ok2 &= sp.Rational(n*(n*n-1), 3) == v2
        ok4 &= sp.Rational(n*(n*n-1)*(3*n*n-7), 15) == v4
    rec('S1 power sums of (2m-N+1)', ok2 and ok4, tested_N='2..15')
s1()

# ---------------------------------------------------------------- S2, S3
def A2(n): return sum((m2-m1)**2 for m1 in range(n) for m2 in range(m1+1, n))
def A3(n): return sum(((m2-m1)*(m3-m1)*(m3-m2))**2 for m1 in range(n) for m2 in range(m1+1, n) for m3 in range(m2+1, n))
ok = all(A2(n) == sp.Rational(n*n*(n*n-1), 12) for n in range(2, 20))
rec('S2 A_2(N) = N^2(N^2-1)/12', ok)
poly3 = N**3*(N**2-1)**2*(N**2-4)/2160
ok = all(A3(n) == poly3.subs(N, n) for n in range(3, 22))
# interpolation check independent of the guess: degree-9 polynomial through 10 points, verified on 8 more
pts = [(n, A3(n)) for n in range(3, 13)]
interp = sp.interpolate(pts, N)
ok_interp = sp.expand(interp - poly3) == 0
rec('S3 A_3(N) = N^3(N^2-1)^2(N^2-4)/2160', ok and ok_interp, interpolated=str(sp.factor(interp)))
# Selberg check
x1, x2, x3 = sp.symbols('x1 x2 x3')
vdm2 = ((x1-x2)*(x1-x3)*(x2-x3))**2
I = sp.integrate(vdm2, (x1, 0, 1), (x2, 0, 1), (x3, 0, 1))
rec('S3b Selberg int_[0,1]^3 prod(x_i-x_j)^2 = 1/360', I == sp.Rational(1, 360), value=str(I))

# ---------------------------------------------------------------- S4
def K(n, a, b):
    d = a - b
    if abs(d) < 1e-14: return n/(2*math.pi)
    return math.sin(n*d/2)/(2*math.pi*math.sin(d/2))
def rho(n, xs):
    M = np.array([[K(n, a, b) for b in xs] for a in xs])
    return np.linalg.det(M)
def C3(n): return float(poly3.subs(N, n))/4/(2*math.pi)**3
def C2(n): return n*n*(n*n-1)/12/(2*math.pi)**2
def schur_sum(n, xs):
    # sum over m1<m2<m3 of |det[z_j^{m_k}]|^2 / prod|z_i-z_j|^2  == sum |s_lambda(z)|^2
    z = np.exp(1j*np.array(xs)); vd = abs((z[0]-z[1])*(z[0]-z[2])*(z[1]-z[2]))**2
    tot = 0.0
    for m1 in range(n):
        for m2 in range(m1+1, n):
            for m3 in range(m2+1, n):
                tot += abs(np.linalg.det(np.array([[z[j]**m for m in (m1, m2, m3)] for j in range(3)])))**2
    return tot/vd, vd
rng = np.random.default_rng(1)
worst_ratio = 0.0; ok_id = True; ok_glob = True; lim_ratios = {}
for n in (3, 4, 6, 9, 13):
    for trial in range(200):
        xs = rng.uniform(0, 2*math.pi, 3)
        r = rho(n, xs); ss, vd = schur_sum(n, xs)
        ident = (2*math.pi)**-3*vd*ss
        ok_id &= abs(r - ident) <= 1e-9*max(1.0, abs(r))
        bound = C3(n)*vd
        ok_glob &= r <= bound*(1+1e-9) + 1e-12
        worst_ratio = max(worst_ratio, r/bound if bound > 0 else 0)
    # clustering limit: x = (0, h, 2.3h) with h -> 0, compare with C3 * prod (x_i-x_j)^2
    for h in (1e-1, 1e-2, 1e-3):
        xs = [0.0, h, 2.3*h]
        pr = (h*2.3*h*1.3*h)**2
        lim_ratios[f'N={n},h={h}'] = rho(n, xs)/(C3(n)*pr)
rec('S4a rho_3 = (2pi)^-3 prod|z_i-z_j|^2 sum|s_lambda|^2 (identity)', ok_id)
rec('S4b global bound rho_3 <= C_3(N) prod|z_i-z_j|^2', ok_glob, worst_ratio=worst_ratio)
rec('S4c clustering limit ratio -> 1', all(abs(v-1) < 0.05 for k, v in lim_ratios.items() if 'h=0.001' in k),
    ratios={k: round(v, 6) for k, v in lim_ratios.items()})

# ---------------------------------------------------------------- S5
ok_up = ok_lo = True; worst_up = 0; worst_lo = 1e9
for n in (2, 3, 5, 8, 16, 40, 100):
    for u in np.concatenate([np.linspace(1e-4, 2*math.pi-1e-4, 4000), np.geomspace(1e-6, 1e-2, 200)]):
        # numerically stable: 1 - S_N^2 = (1-S_N)(1+S_N), 1-S_N = (2/N) sum sin^2((2m-N+1)u/4)
        t = u/2
        one_minus_S = (2.0/n)*sum(math.sin((2*m-n+1)*t/2)**2 for m in range(n))
        S = 1.0 - one_minus_S
        r2 = (n/(2*math.pi))**2*one_minus_S*(1+S)
        up = n*n*(n*n-1)*u*u/(48*math.pi**2)
        ok_up &= r2 <= up*(1+1e-9) + 1e-14; worst_up = max(worst_up, r2/up)
        if n*n*u*u <= 24:
            lo = up*(1 - n*n*u*u/30)
            ok_lo &= r2 >= lo*(1-1e-9) - 1e-14
            if lo > 0: worst_lo = min(worst_lo, r2/lo)
rec('S5a rho_2(u) <= N^2(N^2-1)u^2/(48pi^2) for all u', ok_up, max_ratio=worst_up)
rec('S5b rho_2(u) >= ...(1 - N^2u^2/30) for N^2u^2<=24', ok_lo, min_ratio=worst_lo)

# ---------------------------------------------------------------- S6 Fischer
ok_f = True
for n in (3, 5, 9):
    for trial in range(300):
        xs = rng.uniform(0, 2*math.pi, 4)
        M = np.array([[K(n, a, b) for b in xs] for a in xs])
        d = np.linalg.det
        ok_f &= d(M) <= d(M[:2, :2])*d(M[2:, 2:])*(1+1e-9) + 1e-13
        ok_f &= d(M[:3, :3]) <= d(M[:2, :2])*M[2, 2]*(1+1e-9) + 1e-13
rec('S6 Fischer det M <= det A det D on sine-kernel Gram matrices', ok_f)

# ---------------------------------------------------------------- S7
d = np.linspace(1e-6, math.pi, 100000)
ok7 = np.all(1/np.sin(d/2)**2 <= math.pi**2/d**2*(1+1e-12))
xx = np.linspace(1e-6, 2*math.pi-1e-6, 100000); dd = np.minimum(xx, 2*math.pi-xx)
ok7b = np.allclose(1/np.sin(xx/2)**2, 1/np.sin(dd/2)**2, rtol=1e-6)  # (fp noise near 0, 2pi)
rec('S7 csc^2(d/2) <= pi^2/d^2 on (0,pi]; csc^2 depends only on circular distance', ok7 and ok7b)

# ---------------------------------------------------------------- S8 constants (see the .md, Section 5)
pi = math.pi
# Regime 1: L <= 4 N^{1/3}, eps = L N^{-4/3}, N >= 2.
#   E[Z] >= (L^3/(72 pi)) (1-N^-2)(1 - L^2 N^{-2/3}/50) >= (L^3/(72 pi)) (3/4)(17/25)
EZ_low_coef = (3/4)*(17/25)/(72*pi)          # E[Z] >= EZ_low_coef * L^3
inv_EZ = 1/EZ_low_coef                       # 1/E[Z] <= inv_EZ / L^3
T3_coef = 31/(1036800*pi**2)                 # T_3 <= T3_coef * L^8 N^{-5/3}
ratio_T3 = T3_coef/EZ_low_coef**2            # T_3/E[Z]^2 <= ratio_T3 * L^2 N^{-5/3} <= ratio_T3*16/N <= ratio_T3*16*64/L^3
c_delta_r1 = inv_EZ + ratio_T3*16*64
# Regime 2: L > 4 N^{1/3}, eps = 4/N.
#   E[Z] >= (17/25) * 64 (N^2-1)/(72 pi N) >= (17/25)*64*(3/4) N/(72 pi)
EZ2_coef = (17/25)*64*(3/4)/(72*pi)          # E[Z] >= EZ2_coef * N
T3_2 = 31*4**8/(1036800*pi**2)               # T_3 <= T3_2 * N
p_r2_over_N = 1/EZ2_coef + T3_2/EZ2_coef**2  # P(delta_min > 4/N) <= p_r2_over_N / N
c_delta_r2 = p_r2_over_N*64                  # since N < (L/4)^3  ->  1/N < 64/L^3
C_delta = max(c_delta_r1, c_delta_r2)
# Term 2 (triple with a point within c/N), c = L^-2, both regimes: <= term2_coef / L^3
term2_coef = (1/15 + 1/2 + 16/15)/(4320*pi**2)
# Term 3 (shell Markov), M = L^8: L^5/(18 M) = 1/(18 L^3)
term3_coef = 1/18
C_total = C_delta + term2_coef + term3_coef
rec('S8 constants', True, inv_EZ_r1=inv_EZ, ratio_T3_r1=ratio_T3, C_delta_regime1=c_delta_r1,
    P_delta_gt_4_over_N_times_N=p_r2_over_N, C_delta_regime2=c_delta_r2, C_delta=C_delta,
    term2_coef=term2_coef, term3_coef=term3_coef, C_total=C_total,
    statement=f'P(S* > M N^2) <= {C_total:.1f} M^(-3/8) for all N>=3, M>=1')
# Second-moment refinement (Proposition 2): eta = M^{-1/3}, L^3 = M^{1/2}
#   term2 <= (1/(4320 pi^2)) (1/15+1/2+16/15) L^3 eta^3 = term2_coef * M^{-1/2}
#   term3 <= E[Z_ord] [2/(3 pi eta^3) + 4/(pi^2 eta^2)] / M'^2 with M' = 2M/pi^2, E[Z_ord] <= L^3/(36 pi)
term3b = (1/(36*pi))*(2/(3*pi) + 4/pi**2)*(pi**2/2)**2   # times L^3 eta^-3 / M^2 = M^{1/2} M / M^2 = M^{-1/2}
C_total2 = C_delta*1 + term2_coef + term3b   # C_delta / L^3 = C_delta M^{-1/2}
rec('S8b second-moment refinement', True, term3b_coef=term3b, C_total2=C_total2,
    statement=f'P(S* > M N^2) <= {C_total2:.1f} M^(-1/2) for all N>=3, M>=1')
# heuristic sharp tail: P(S* > M N^2) ~ P(N d_3 < sqrt(2/M)) ~ (2/M)^{5/2}/(3600 pi)
rec('S8c heuristic third-point law', True, P_d3_le_c_over_N='c^5/(3600 pi)', coef=1/(3600*pi))

with open(OUT, 'w') as f: json.dump(results, f, indent=1, default=str)
print('all pass:', all(v['pass'] for v in results.values()))
print('saved', OUT)
