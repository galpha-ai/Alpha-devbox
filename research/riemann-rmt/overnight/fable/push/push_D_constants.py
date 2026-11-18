import mpmath as mp
mp.mp.dps = 30
s1, s2 = mp.sinh(1), mp.sinh(2)
K = lambda a: s2*mp.e**(-2*abs(a)) - s1*mp.e**(-abs(a))
a0 = mp.log(2*mp.cosh(1))
print("alpha_0 = log(2cosh1) =", a0)
# check sign change
print("K(a0) =", K(a0))
# W[F] = int_{-inf}^{inf} K F = 2 int_0^inf K F (F even)
def W(F, pieces):
    return 2*sum(mp.quad(lambda a: K(a)*F(a), p) for p in pieces)
# GUE
F_gue = lambda a: min(a,1)
W_gue = 2*(mp.quad(lambda a: K(a)*a,[0,1]) + mp.quad(lambda a: K(a),[1,mp.inf]))
print("W_GUE numeric =", W_gue)
W_gue_closed = mp.e**2/4 - mp.e + mp.mpf(3)/4 + 1/mp.e - mp.mpf(5)/(4*mp.e**2) + 1/(4*mp.e**4)
print("W_GUE closed (Astra eq 15) =", W_gue_closed)
# GGM check: I_T(c)/(T log^2 T) -> int_0^inf e^{-2c a} F(a) da; sine: (1-e^{-2c})/(4c^2)
for c in [mp.mpf(1), mp.mpf(1)/2]:
    print("c=",c," int_0^inf e^{-2ca} min(a,1) =", mp.quad(lambda a: mp.e**(-2*c*a)*min(a,1),[0,1,mp.inf]), " (1-e^{-2c})/(4c^2)=", (1-mp.e**(-2*c))/(4*c**2))
Wg2 = 2*(s2*(1-mp.e**-2)/4 - s1*(1-mp.e**-1))
print("W_GUE via GGM form =", Wg2)
# AH: continuous part dist(a,2Z) plus unit atoms at 2m, m != 0
dist = lambda a: abs(a - 2*mp.nint(a/2))
W_ah_cont = 2*mp.quad(lambda a: K(a)*dist(a), [0,1,2,3,4,5,6,7,8,10,14,20,mp.inf])
W_ah_atoms = 2*mp.nsum(lambda m: K(2*m), [1, mp.inf])
print("W_AH continuous part =", W_ah_cont)
print("W_AH atoms part      =", W_ah_atoms, "  e^-2 - e^-1 =", mp.e**-2 - mp.e**-1)
W_ah = W_ah_cont + W_ah_atoms
print("W_AH total =", W_ah)
W_ah_closed = mp.e**2/4 + mp.mpf(5)/(4*mp.e**2) - mp.e - 2/mp.e + mp.mpf(3)/2
print("W_AH closed (Astra eq 15) =", W_ah_closed)
print("W_GUE - W_AH =", W_gue - W_ah, "  1/16 - W_AH =", mp.mpf(1)/16 - W_ah)
# band part B
B = 2*mp.quad(lambda a: K(a)*a,[0,1])
print("B (band, |a|<=1) =", B)
# tail integrals
G_gold = 2*mp.quad(lambda a: K(a)*(mp.mpf(3)/2-a),[1,a0])
G_gue = 2*mp.quad(lambda a: K(a),[1,a0])
G_ah = 2*mp.quad(lambda a: K(a)*(2-a),[1,a0])
Tneg = 2*mp.quad(lambda a: K(a),[a0,mp.inf])
print("2 int_1^a0 K (3/2-a)  [Goldston floor] =", G_gold)
print("2 int_1^a0 K * 1      [GUE]            =", G_gue)
print("2 int_1^a0 K (2-a)    [AH]             =", G_ah)
print("2 int_{a0}^inf K      (=-tanh(1)/2)    =", Tneg, -mp.tanh(1)/2)
# AH's negative-region mass: 2 int_{a0}^inf K F_AH
T_ah = W_ah - B - G_ah
T_gue = W_gue - B - G_gue
print("2 int_{a0}^inf K F_AH  =", T_ah)
print("2 int_{a0}^inf K F_GUE =", T_gue)
# required: B + G + Tail >= 1/16  -> Tail >= 1/16 - B - G
print("needed tail  (with Goldston floor on (1,a0)): 2 int_{a0}^inf K F >= ", mp.mpf(1)/16 - B - G_gold)
print("needed tail  (with F>=0 only on (1,a0)):      2 int_{a0}^inf K F >= ", mp.mpf(1)/16 - B)
# cap u on (a0,inf): tail = u*Tneg ; threshold u*
print("u* with Goldston floor =", (mp.mpf(1)/16 - B - G_gold)/Tneg)
print("u* with F>=0 floor     =", (mp.mpf(1)/16 - B)/Tneg)
print("W with F=3/2-a on (1,a0), F=1 beyond =", B+G_gold+Tneg)
print("W with F=0 on (1,a0), F=1 beyond     =", B+Tneg)
# effective average density of AH in the negative region weighted by |K|
print("AH effective |K|-weighted average F on (a0,inf) =", T_ah/Tneg)
print("GUE effective                                    =", T_gue/Tneg)
# Round 8: 1/16 - B, sine tail
print("1/16 - B =", mp.mpf(1)/16 - B, "  sine residual W_GUE - B =", W_gue - B, "  AH residual =", W_ah - B)
# physical kernel k(u) nonnegativity check
k = lambda u: s2*4/(4+4*mp.pi**2*u**2) - s1*2/(1+4*mp.pi**2*u**2)
print("k(0)=",k(0)," k(0.3)=",k(mp.mpf('0.3'))," k(2)=",k(2), " min over grid:", min(k(mp.mpf(i)/50) for i in range(0,500)))
print("K(0) = sinh2 - sinh1 =", K(0), " int k du = K(0)? ", mp.quad(k,[-mp.inf,mp.inf]))
print("trivial physical bound: W >= k(0)-K(0) =", k(0)-K(0), " = -sinh(1)?", -s1)
