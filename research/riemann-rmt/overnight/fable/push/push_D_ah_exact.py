import mpmath as mp
mp.mp.dps=30
s1,s2=mp.sinh(1),mp.sinh(2)
K=lambda a: s2*mp.e**(-2*a)-s1*mp.e**(-a)
# continuous part: 2*sum_m [ int_{2m}^{2m+1} K (a-2m) + int_{2m+1}^{2m+2} K (2m+2-a) ]
def piece(m):
    m=int(m)
    return mp.quad(lambda a: K(a)*(a-2*m),[2*m,2*m+1]) + mp.quad(lambda a: K(a)*(2*m+2-a),[2*m+1,2*m+2])
cont = 2*mp.nsum(piece,[0,mp.inf])
atoms = 2*mp.nsum(lambda m: K(2*m),[1,mp.inf])
print("W_AH cont  =",cont)
print("W_AH atoms =",atoms, " = e^-2-e^-1 =", mp.e**-2-mp.e**-1)
print("W_AH       =",cont+atoms)
print("closed     =",mp.e**2/4+mp.mpf(5)/(4*mp.e**2)-mp.e-2/mp.e+mp.mpf(3)/2)
a0=mp.log(2*mp.cosh(1))
# tail pieces on (a0,inf) for AH continuous vs GUE
dist=lambda a: abs(a-2*mp.nint(a/2))
cont_tail = 2*(mp.quad(lambda a:K(a)*dist(a),[a0,2]) + mp.nsum(lambda m: mp.quad(lambda a:K(a)*dist(a),[2*int(m),2*int(m)+1])+mp.quad(lambda a:K(a)*dist(a),[2*int(m)+1,2*int(m)+2]),[1,mp.inf]))
print("AH continuous tail 2int_{a0}^inf K dist =",cont_tail, "  GUE tail:", -mp.tanh(1)/2, "  AH total tail:", cont_tail+atoms)
print("AH cont tail - GUE tail =", cont_tail+mp.tanh(1)/2, " atoms:", atoms, " net:", cont_tail+atoms+mp.tanh(1)/2)
# W_AH - W_GUE decomposition on (1,a0)
print("2int_1^a0 K(2-a) - 2int_1^a0 K =", 2*mp.quad(lambda a:K(a)*(1-a),[1,a0]))
