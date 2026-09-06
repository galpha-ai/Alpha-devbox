"""refute_D_check.py -- independent recomputation for the refutation of push_D_last_mile.md.

Everything here is derived from Astra's definitions (TWO_SCALE_ZETA_TARGET.md eqs (1),(5),(7),(13),(16))
and NOT from push_D's formulas, so agreement is an independent check of push_D's kernel, normalisation
and table constants.  Run:  python3 refute_D_check.py
"""
import mpmath as mp, numpy as np, json, os, sys
mp.mp.dps = 30
one = mp.mpf(1)
s1, s2 = mp.sinh(1), mp.sinh(2)
E = mp.e

def hdr(s): print("\n=== " + s + " ===")

# ------------------------------------------------------------------ A. physical-space definitions
# Astra (16): K_b(x) = 2b/(b^2 + 4 pi^2 x^2), Fourier transform e^{-b|alpha|}; Q(b) = int K_b dmu - 1.
def Kb(b, x): return 2*b/(b**2 + 4*mp.pi**2*x**2)
def sinc(x): return one if x == 0 else mp.sin(mp.pi*x)/(mp.pi*x)

hdr("A. V(b) from the PHYSICAL pair measures (no Poisson summation), vs Astra's closed forms (8),(10),(12)")
def V_sine_phys(b):
    # mu = delta_0 + (1 - sinc^2(x)) dx  ->  Q = K_b(0) + int K_b (1 - sinc^2) dx - 1 = K_b(0) - int K_b sinc^2
    return Kb(b, 0) - mp.quad(lambda x: Kb(b, x)*sinc(x)**2, [-mp.inf, -20, -5, -1, 0, 1, 5, 20, mp.inf])
def V_AH_phys(b, p0=one):
    # mu = delta_0 + (1/2) sum_{k!=0} (1 - sinc^2(k/2)) delta_{k/2}  +  (p0-1) sum_k (-1)^k delta_{k/2}   [Astra (5),(6)]
    # even k=2j (j>=1): 1 - sinc^2(j) = 1 ;  odd k=2j+1 (j>=0): 1 - 4/(pi^2 (2j+1)^2).  (parities summed separately:
    # a single nsum over k mis-extrapolates the parity oscillation by ~1e-5.)
    even = mp.nsum(lambda j: Kb(b, j), [1, mp.inf])
    odd  = mp.nsum(lambda j: (1 - 4/(mp.pi**2*(2*j+1)**2))*Kb(b, j + one/2), [0, mp.inf])
    nuis = (p0-1)*(Kb(b, 0) + 2*mp.nsum(lambda k: (-1)**int(k)*Kb(b, k/mp.mpf(2)), [1, mp.inf]))
    return Kb(b, 0) + even + odd - 1 + nuis      # (1/2)*2*(even+odd)
def V_AH_exact(b):
    # refuter's closed evaluation of the same physical sums by partial fractions:
    # sum_{j>=1} K_b(j) = coth(b/2)/2 - 1/b ; sum_{j>=0} K_b(j+1/2) = tanh(b/2)/2 ;
    # sum_{j>=0} 4/(pi^2(2j+1)^2) K_b(j+1/2) = 1/b - 2 tanh(b/2)/b^2 ;  K_b(0) = 2/b.
    # => V = (coth(b/2)+tanh(b/2))/2 - 1 + 2tanh(b/2)/b^2 = coth(b) - 1 + 2tanh(b/2)/b^2 = 2/(e^{2b}-1) + 2tanh(b/2)/b^2.
    return mp.coth(b) - 1 + 2*mp.tanh(b/2)/b**2
V_sine_closed = lambda b: 2*(1-mp.e**(-b))/b**2
V_AH_closed   = lambda b: 2*mp.tanh(b/2)/b**2 + 2/(mp.e**(2*b)-1)
for b in [one, mp.mpf(2), mp.mpf('0.7')]:
    print(f"b={b}: V_sine phys={V_sine_phys(b)}  closed={V_sine_closed(b)}")
    print(f"      V_AH   phys={V_AH_phys(b)}  closed={V_AH_closed(b)}  partial-fractions={V_AH_exact(b)}")
    p0 = mp.mpf('1.3')
    print(f"      nuisance(p0=1.3) phys={V_AH_phys(b,p0)-V_AH_phys(b)}  Astra(12)=2(p0-1)/sinh b={2*(p0-1)/mp.sinh(b)}")

hdr("B. W = sinh2 V(2) - sinh1 V(1)  [Astra (13)]  and its Fourier form int K F with K = sinh2 e^{-2|a|} - sinh1 e^{-|a|}")
W_GUE = s2*V_sine_closed(2) - s1*V_sine_closed(1)
W_AH  = s2*V_AH_closed(2)   - s1*V_AH_closed(1)
W_AH_p0 = s2*V_AH_phys(mp.mpf(2), mp.mpf('1.29')) - s1*V_AH_phys(one, mp.mpf('1.29'))
print("W_GUE =", W_GUE, "  Astra(15):", E**2/4 - E + mp.mpf(3)/4 + 1/E - mp.mpf(5)/(4*E**2) + 1/(4*E**4))
print("W_AH  =", W_AH,  "  Astra(15):", E**2/4 + mp.mpf(5)/(4*E**2) - E - 2/E + mp.mpf(3)/2)
print("W_AH with p0=1.29 (physical sums):", W_AH_p0, "  (p0-independence check)")
print("1/16 - W_AH =", one/16 - W_AH, "   W_GUE - W_AH =", W_GUE - W_AH, "  Astra(14) H(2)-H(1):",
      ((1-E**-2)**2/4 - E**-2) - ((1-E**-1)**2 - E**-1))
K = lambda a: s2*mp.e**(-2*abs(a)) - s1*mp.e**(-abs(a))
a0 = mp.log(2*mp.cosh(1))
print("alpha_0 = log(2 cosh 1) =", a0, "  K(alpha_0) =", K(a0))
# Fourier-side recomputation of W_GUE and W_AH from the spectral measures
dist = lambda a: abs(a - 2*mp.nint(a/2))
W_GUE_F = 2*(mp.quad(lambda a: K(a)*a, [0, 1]) + mp.quad(K, [1, mp.inf]))
W_AH_F  = 2*mp.quad(lambda a: K(a)*dist(a), [0,1,2,3,4,5,6,7,8,10,14,20,mp.inf]) + 2*mp.nsum(lambda m: K(2*m), [1, mp.inf])
print("Fourier side: W_GUE =", W_GUE_F, " W_AH =", W_AH_F)
print("odd-atom (p0 nuisance) weight  2 sum_{m>=0} K(2m+1) =", 2*mp.nsum(lambda m: K(2*m+1), [0, mp.inf]), " (must be 0)")

hdr("C. GGM constant and the c-normalisation  I_T(c) ~ T log^2 T * int_0^inf e^{-2 c a} F(a) da")
for c in [one, one/2]:
    print(f"c={c}: int_0^inf e^(-2ca) min(a,1) da = {mp.quad(lambda a: mp.e**(-2*c*a)*min(a,1),[0,1,mp.inf])}  vs (1-e^(-2c))/(4c^2) = {(1-mp.e**(-2*c))/(4*c**2)}  vs V_sine(2c)/2 = {V_sine_closed(2*c)/2}")
print("W_GUE via 2[sinh2 (1-e^-2)/4 - sinh1 (1-e^-1)] =", 2*(s2*(1-E**-2)/4 - s1*(1-E**-1)))

hdr("D. push_D table constants, recomputed")
B = 2*mp.quad(lambda a: K(a)*a, [0, 1])
B_closed = 2*(s2*(1-3*E**-2)/4 - s1*(1-2*E**-1))
G_gold = 2*mp.quad(lambda a: K(a)*(mp.mpf(3)/2 - a), [1, a0])
G_gue  = 2*mp.quad(K, [1, a0])
G_ah   = 2*mp.quad(lambda a: K(a)*(2 - a), [1, a0])
Tneg   = 2*mp.quad(K, [a0, mp.inf])
atoms  = 2*mp.nsum(lambda m: K(2*m), [1, mp.inf])
cont   = W_AH_F - atoms
T_ah   = W_AH - B - G_ah
T_ah_cont = T_ah - atoms
print("B =", B, " closed:", B_closed)
print("2int_1^a0 K(3/2-a) =", G_gold, "  2int_1^a0 K =", G_gue, "  2int_1^a0 K(2-a) =", G_ah)
print("2int_{a0}^inf K =", Tneg, "  = -tanh(1)/2 ?", -mp.tanh(1)/2)
print("AH atoms 2 sum K(2m) =", atoms, "  = e^-2 - e^-1 ?", E**-2 - E**-1)
print("AH continuous part of W =", cont, "  AH tail =", T_ah, " = cont", T_ah_cont, "+ atoms", atoms)
print("W_GUE - B =", W_GUE - B, "  W_AH - B =", W_AH - B, "  1/16 - B =", one/16 - B)
print("needed tail with Goldston floor:", one/16 - B - G_gold, "  without:", one/16 - B)
print("u* (Goldston) =", (one/16 - B - G_gold)/Tneg, "  u* (no Goldston) =", (one/16 - B)/Tneg,
      "  AH |K|-average =", T_ah/Tneg, "  GUE =", (W_GUE - B - G_gue)/Tneg)
print("cap F<=1 on (a0,inf), floor 0 on (1,a0): W =", B + Tneg, "   with Goldston floor:", B + G_gold + Tneg)
print("2|K(2)| =", 2*abs(K(2)), "  fraction of |K|-weight on (a0,2.5]:", 2*mp.quad(lambda a: -K(a), [a0, mp.mpf('2.5')])/(-Tneg))
print("decomposition of W_GUE - W_AH: (1,a0):", G_gue - G_ah, "  tail cont:", (W_GUE-B-G_gue) - T_ah_cont, "  atoms:", -atoms,
      "  total:", (G_gue-G_ah) + (W_GUE-B-G_gue) - T_ah_cont - atoms)

hdr("E. physical kernel k(u) = inverse FT of K; nonnegativity; trivial bound")
k = lambda u: s2*4/(4+4*mp.pi**2*u**2) - s1*2/(1+4*mp.pi**2*u**2)
print("k(0)=", k(0), " = sinh2 - 2 sinh1 =", s2 - 2*s1, "  K(0) = sinh2 - sinh1 =", K(0), "  int k du =", mp.quad(k, [-mp.inf, mp.inf]))
# exact condition: k(u) >= 0  <=>  (sinh2 - 2 sinh1) + pi^2 u^2 (4 sinh2 - 2 sinh1) >= 0  (always, both terms >= 0)
print("k>=0 condition, correct form: constant term", s2 - 2*s1, ">=0 and u^2-coefficient", mp.pi**2*(4*s2 - 2*s1), ">0")
print("push_D's displayed condition '4pi^2u^2(sinh2 - sinh1) >= 2 sinh1(2-2cosh1)': LHS coef", 4*mp.pi**2*(s2-s1), " RHS", 2*s1*(2-2*mp.cosh(1)),
      " -> conclusion true but the algebra differs from the cross-multiplied inequality")
print("min k on grid:", min(k(mp.mpf(i)/100) for i in range(0, 2000)), "  k(0) - K(0) = -sinh1 ?", k(0) - K(0), -s1)

hdr("F. Goldston/GGOS floor and F_AH; the AH family with p0 in [1, 3/2-2/pi^2]")
print("min over [1,3/2] of F_AH - (3/2-|a|) = min (2-a)-(3/2-a) = 1/2 > 0 : trivially satisfied")
print("p0 range upper end 3/2 - 2/pi^2 =", mp.mpf(3)/2 - 2/mp.pi**2, "; odd-atom mass 2(p0-1) up to", 2*(mp.mpf(3)/2 - 2/mp.pi**2 - 1))

# ------------------------------------------------------------------ G. push_D LP minimisers
hdr("G. push_D LP minimisers (push_D_lp_gold{0,1}.json): feasibility off-grid and beyond u=400, W recomputed")
here = os.path.dirname(os.path.abspath(__file__))
s1f, s2f = np.sinh(1), np.sinh(2)
def Rfun(u, x, lo, hi):
    cc = (np.sin(2*np.pi*hi*u) - np.sin(2*np.pi*lo*u))/(np.pi*u)
    return 1 - (np.sin(np.pi*u)/(np.pi*u))**2 + cc@(x-1)
for f in ["push_D_lp_gold0.json", "push_D_lp_gold1.json"]:
    p = os.path.join(here, f)
    if not os.path.exists(p): print("missing", p); continue
    d = json.load(open(p)); x = np.array(d['x']); lo = np.array(d['lo']); hi = np.array(d['hi']); da = hi - lo; A = hi[-1]
    cK = 2*(s2f*(np.exp(-2*lo)-np.exp(-2*hi))/2 - s1f*(np.exp(-lo)-np.exp(-hi)))
    Bb = 2*(s2f*(1-3*np.exp(-2))/4 - s1f*(1-2*np.exp(-1))); tK = 2*(s2f*np.exp(-2*A)/2 - s1f*np.exp(-A))
    W = Bb + cK@x + tK
    print(f"{f}: reported W={d['W']:.6f} recomputed W={W:.6f}; cells={len(x)} widths={sorted(set(np.round(da,3)))} (push_D text says 0.01/0.02/0.05)")
    ug = np.arange(0.002, 400.0001, 0.002); Rg = np.array([Rfun(u, x, lo, hi) for u in ug])
    uo = np.arange(0.001, 400.0001, 0.002); Ro = np.array([Rfun(u, x, lo, hi) for u in uo])   # midpoints of the check grid
    print(f"   min R on the 0.002 check grid: {Rg.min():.2e};  min R at grid MIDPOINTS: {Ro.min():.2e} at u={uo[Ro.argmin()]:.4f}")
    bound400 = (np.abs(x-1)*np.minimum(2*da, 2/(np.pi*400))).sum()
    print(f"   u>400: |sum (x-1) cc(u)| <= {bound400:.3f} < 1 - 1/(pi*400)^2, so R>0 for all u>400 (rigorous 1/u bound)")
    # atoms & Kronecker: total mass in cells with x*da > 0.1
    big = x*da > 0.1
    print(f"   total mass on (1,12]: {(x*da).sum():.3f}; mass in 'near-atom' cells (>0.1): {(x*da)[big].sum():.3f} in {big.sum()} cells")
print("\nDone.")
