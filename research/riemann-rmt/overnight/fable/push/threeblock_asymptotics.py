"""Symbolic derivation of the expansion tau_N = 2 - 4/(3N^2) + c2/N^4 + O(N^-6) for the symmetric
3-block families, from the Weierstrass representation

   a_N(tau) := d/du q^N_tau(0) = (1/(2 tau)) E[ V cos(V/2) phi_N(V) ],   V ~ N(0, 2 tau),

where q^N_0(u) = cos(u/2) phi_N(u), phi_N odd, phi_N(v) = v + psi_2(v)/N^2 + psi_4(v)/N^4 + ...
(the Gaussian tails |v|>N contribute O(e^{-cN^2}); see push_A_threeblock_limit.md, Prop. 2).
For an odd polynomial psi(v) = sum_k b_k v^{2k+1}:
   E[V^{2k+2} cos(V/2)] = (-1)^{k+1} d^{2k+2}/dt^{2k+2} exp(-tau t^2) |_{t=1/2}.
Then tau_N solves a_N(tau) = 0 and we expand.
"""
import sympy as sp
u,N,tau,t,eps=sp.symbols('u N tau t epsilon',positive=True)

def phi(name):
    a=u/(2*N); b=sp.pi/(2*N)
    if name=='block4odd':  # 2N tan(u/2N)
        return 2*N*sp.tan(a)
    if name=='block33':    # 2N sin(a) cos(a) cos^2(b)/(cos^2 a - sin^2 b), normalised phi'(0)=1
        return 2*N*sp.sin(a)*sp.cos(a)*sp.cos(b)**2/(sp.cos(a)**2-sp.sin(b)**2)
    raise ValueError

def moment_cos(n):
    """E[V^n cos(V/2)], V~N(0,2 tau):  Re E[V^n e^{iV/2}] = Re (-i d/dt)^n e^{-tau t^2} at t=1/2"""
    f=sp.exp(-tau*t**2)
    d=sp.diff(f,t,n)
    val=(-sp.I)**n*d
    return sp.simplify(sp.re(val.subs(t,sp.Rational(1,2))))

for name in ['block4odd','block33']:
    ph=phi(name)
    # expand in eps=1/N: substitute N=1/eps, series in eps to order eps^6
    ser=sp.series(ph.subs(N,1/eps),eps,0,7).removeO()
    ser=sp.expand(ser)
    psi2=ser.coeff(eps,2); psi4=ser.coeff(eps,4)
    assert ser.coeff(eps,0)==u and ser.coeff(eps,1)==0 and ser.coeff(eps,3)==0
    print(name,": phi_N(u) = u + (",psi2,")/N^2 + (",psi4,")/N^4 + O(N^-6)")
    # a_N(tau) = (1/2tau) E[V cos(V/2) phi_N(V)]
    def A_of(poly):
        poly=sp.Poly(sp.expand(poly),u)
        acc=0
        for (k,),c in poly.terms():
            acc+=c*moment_cos(k+1)
        return sp.simplify(acc/(2*tau))
    a0=A_of(u); a2=A_of(psi2); a4=A_of(psi4)
    print("   a_0(tau) =",sp.simplify(a0*sp.exp(tau/4)),"* e^{-tau/4}")
    print("   a_2(tau) =",sp.factor(sp.simplify(a2*sp.exp(tau/4))),"* e^{-tau/4}")
    print("   a_4(tau) =",sp.factor(sp.simplify(a4*sp.exp(tau/4))),"* e^{-tau/4}")
    # solve a0 + eps^2 a2 + eps^4 a4 = 0 with tau = 2 + c1 eps^2 + c2 eps^4
    c1,c2=sp.symbols('c1 c2')
    T=2+c1*eps**2+c2*eps**4
    expr=(a0+eps**2*a2+eps**4*a4).subs(tau,T)*sp.exp(T/4)
    s=sp.series(expr,eps,0,5).removeO()
    e2=sp.simplify(s.coeff(eps,2)); e4=sp.simplify(s.coeff(eps,4))
    sol1=sp.solve(e2,c1)[0]; sol2=sp.solve(e4.subs(c1,sol1),c2)[0]
    print("   c1 =",sol1,"  c2 =",sp.nsimplify(sp.simplify(sol2)),"=",sp.N(sol2,15))
