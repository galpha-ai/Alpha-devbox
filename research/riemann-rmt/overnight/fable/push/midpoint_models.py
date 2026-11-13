"""Midpoint-insertion local models (push_A, Section 6).

Local model: q_0(u) = p(u) L(u) with L = cos(u/2) (lattice = odd multiples of pi) or L = sin(u/2)
(lattice = even multiples of pi), p a real polynomial whose roots are the inserted midpoints.
Closed form of the heat flow (Prop. 6.1):
    q_tau(u) = e^{-tau/4} Re[ e^{iu/2} P_tau(u + i tau) ]   (cos lattice),
    q_tau(u) = e^{-tau/4} Im[ e^{iu/2} P_tau(u + i tau) ]   (sin lattice),
    P_tau := e^{tau d^2} p  (heat-evolved polynomial, P_tau(w) = E p(w + sqrt(2 tau) Z)).
The local constant tau* = first tau>0 at which q_tau has a real double zero.

Models:
  three  : p = u,            cos lattice   -> tau* = 2 (triple zero at 0), exact
  five   : p = u^2 - pi^2,   sin lattice   (gaps 1,1,1,1: roots 0,+-pi,+-2pi,+-4pi,...)
  two3   : p = u^2 - 4pi^2,  cos lattice   (gaps 1,1,2,1,1: roots +-pi,+-2pi,+-3pi,+-5pi,...)
  seven  : p = u(u^2-4pi^2), cos lattice   (gaps 1^6: roots 0,+-pi,+-2pi,+-3pi,+-5pi,...)
  two3b  : p = u^2 - 9pi^2,  sin lattice   (gaps 1,1,2,2,1,1: roots 0,+-2pi,+-3pi,+-4pi,+-6pi..)
"""
import sympy as sp, mpmath as mp, numpy as np
mp.mp.dps=30
u,tau,w=sp.symbols('u tau w',real=True)

MODELS={
 'three': (u, 'cos'),
 'five' : (u**2-sp.pi**2, 'sin'),
 'two3' : (u**2-4*sp.pi**2, 'cos'),
 'seven': (u*(u**2-4*sp.pi**2), 'cos'),
 'two3b': (u**2-9*sp.pi**2, 'sin'),
 'nine' : (u*(u**2-4*sp.pi**2)*(u**2-16*sp.pi**2), 'cos'),
}

def heat_poly(p):
    """P_tau(w) = E p(w + sqrt(2 tau) Z) = sum_k tau^k p^{(2k)}(w)/k!"""
    P=0; d=p.subs(u,w); k=0
    while d!=0:
        P+=tau**k*d/sp.factorial(k); d=sp.diff(d,w,2); k+=1
    return sp.expand(P)

def q_expr(name):
    p,lat=MODELS[name]
    P=heat_poly(p)
    z=P.subs(w,u+sp.I*tau)
    e=sp.exp(sp.I*u/2)*z
    e=sp.expand(e.rewrite(sp.cos))
    q=sp.re(e) if lat=='cos' else sp.im(e)
    return sp.simplify(sp.exp(-tau/4)*q)

def first_double_zero(name, umax=None, verbose=True):
    q=q_expr(name); qu=sp.diff(q,u); quu=sp.diff(q,u,2)
    f=sp.lambdify((u,tau),q,'mpmath'); fu=sp.lambdify((u,tau),qu,'mpmath'); fuu=sp.lambdify((u,tau),quu,'mpmath')
    # track the real zeros in [0,umax] as tau increases; a collision = the local extremum between two
    # consecutive zeros crossing 0.  We scan tau on a grid, count sign changes on a fine u-grid,
    # and refine the first tau at which the count in [0,umax] drops, by solving q=q_u=0 with findroot.
    umax=umax or 4*mp.pi
    ug=[mp.mpf(i)*umax/4000 for i in range(4001)]
    def zeros_at(t):
        vals=[f(x,t) for x in ug]
        zs=[]
        for i in range(len(ug)-1):
            if vals[i]==0: zs.append(ug[i])
            elif vals[i]*vals[i+1]<0: zs.append(mp.findroot(lambda x:f(x,t),(ug[i],ug[i+1]),solver='bisect'))
        return zs
    z0=zeros_at(mp.mpf('1e-6'))
    n0=len(z0)
    if verbose: print(f"  {name}: zeros in [0,{float(umax):.3f}] at tau=0+ :",[float(z) for z in z0])
    t=mp.mpf('0.05'); h=mp.mpf('0.05'); prev=z0; tprev=mp.mpf(0)
    while True:
        zs=zeros_at(t)
        if len(zs)<n0: break
        prev,tprev=zs,t; t+=h
        if t>6: return None
    # bracket [tprev,t]; identify which adjacent pair (of prev) collapsed: pair whose midpoint has q of the sign of the extremum -> just try all
    best=None
    for i in range(len(prev)-1):
        um=(prev[i]+prev[i+1])/2
        try:
            sol=mp.findroot(lambda x,s:[f(x,s),fu(x,s)],(um,(tprev+t)/2))
            x,s=sol[0],sol[1]
            if tprev-1e-9<=s<=t+1e-9 and abs(fuu(x,s))>0 and (best is None or s<best[1]): best=(x,s,fuu(x,s))
        except Exception as e:
            pass
    # also the triple-zero-at-0 possibility for odd models: q_u(0,tau)=0
    try:
        s0=mp.findroot(lambda s:fu(mp.mpf(0),s),(tprev,t),solver='bisect')
        if tprev<=s0<=t and (best is None or s0<best[1]): best=(mp.mpf(0),s0,mp.mpf(0))
    except Exception: pass
    if verbose and best: print(f"  {name}: first double zero at u*={mp.nstr(best[0],15)}  tau*={mp.nstr(best[1],15)}  q_uu(u*,tau*)={mp.nstr(best[2],6)}")
    return best

if __name__=="__main__":
    for name in ['three','five','two3','seven','two3b']:
        q=q_expr(name); print(name,": q_tau(u) e^{tau/4} =",sp.simplify(q*sp.exp(tau/4)))
        first_double_zero(name)
