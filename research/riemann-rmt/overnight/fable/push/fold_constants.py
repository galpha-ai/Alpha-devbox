"""First-order finite-N correction for midpoint-insertion families whose local collision is a
non-degenerate fold (q = q_u = 0, q_uu != 0 at (u*,tau*)).

q^N_0(u) = L(u) Phi_N(u),  Phi_N = p + psi/N^2 + O(N^-4)  (exact Phi_N from the closed form of Q_0),
q^N_tau = q_tau + N^-2 r_tau + O(N^-4),  r_tau = e^{tau d^2}[L psi] = e^{-tau/4} (Re|Im)[e^{iu/2} Psi_tau(u+i tau)].
Since d/dtau q = d^2/du^2 q, the extremum value h(tau) between the colliding pair satisfies h'(tau*) = q_uu(u*,tau*),
so   tau_N = tau* - N^-2 r_{tau*}(u*)/q_uu(u*,tau*) + O(N^-4)          (Prop. 6.3).

Families (compensation symmetric about the antipode; parity of N as indicated):
  five  (N odd):  L=sin, p=u^2-pi^2,       Phi_N=(2N)^2 (sin^2 a - sin^2 b)/(cos^2 a - sin^2 b),        a=u/2N, b=pi/2N
  two3  (N even): L=cos, p=u^2-4pi^2,      Phi_N=(2N)^2 (sin^2 a - sin^2 2b)/(cos^2 a - sin^2 b)
  seven (N odd):  L=cos, p=u(u^2-4pi^2),   Phi_N=(2N)^3 sin a (sin^2 a - sin^2 2b)/(cos a cos(a-2b) cos(a+2b))
  five_even (N even): L=sin, p=u^2-pi^2,   removed sites N-2,N:  Phi_N=(2N)^2 (sin^2 a - sin^2 b)/(cos a cos(a+2b))
"""
import sympy as sp, mpmath as mp
import midpoint_models as M
u,tau,w=M.u,M.tau,M.w
N,eps=sp.symbols('N epsilon',positive=True)
a=u/(2*N); b=sp.pi/(2*N)
FAM={
 'five' :('five', (2*N)**2*(sp.sin(a)**2-sp.sin(b)**2)/(sp.cos(a)**2-sp.sin(b)**2)),
 'two3' :('two3', (2*N)**2*(sp.sin(a)**2-sp.sin(2*b)**2)/(sp.cos(a)**2-sp.sin(b)**2)),
 'seven':('seven',(2*N)**3*sp.sin(a)*(sp.sin(a)**2-sp.sin(2*b)**2)/(sp.cos(a)*sp.cos(a-2*b)*sp.cos(a+2*b))),
 'five_even':('five',(2*N)**2*(sp.sin(a)**2-sp.sin(b)**2)/(sp.cos(a)*sp.cos(a+2*b))),
}
FOLD={'five':(sp.pi,2),'two3':(2*sp.pi,2),'seven':(mp.mpf('5.9643126848125'),mp.mpf('2.03812605359085'))}
mp.mp.dps=20
for fam,(model,Phi) in FAM.items():
    p,lat=M.MODELS[model]
    ser=sp.expand(sp.series(Phi.subs(N,1/eps),eps,0,3).removeO())
    c0=sp.expand(ser.coeff(eps,0)-p); c1=sp.expand(ser.coeff(eps,1))
    if c0!=0 or c1!=0: print("   [series check]",fam,": eps^0 - p =",c0,"  eps^1 =",c1)
    psi=sp.expand(ser.coeff(eps,2))
    Psi=M.heat_poly(psi)                      # e^{tau d^2} psi, in w
    z=sp.expand((sp.exp(sp.I*u/2)*Psi.subs(w,u+sp.I*tau)).rewrite(sp.cos))
    r=sp.exp(-tau/4)*(sp.re(z) if lat=='cos' else sp.im(z))
    q=M.q_expr(model); quu=sp.diff(q,u,2)
    us,ts=FOLD[model]
    rv=sp.N(r.subs({u:us,tau:ts}),15); qv=sp.N(quu.subs({u:us,tau:ts}),15)
    print(f"{fam:10s} psi(u) = {psi}")
    print(f"           r_tau*(u*) = {rv}   q_uu(u*,tau*) = {qv}   =>  N^2 (tau_N - tau*) -> {sp.N(-rv/qv,10)}")
