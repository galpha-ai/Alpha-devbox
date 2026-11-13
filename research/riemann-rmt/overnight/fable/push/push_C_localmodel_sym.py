"""Symbolic facts about the local models of k added consecutive midpoints in the alternating lattice.
p_k(u) = prod_{j=0}^{k-1} (u - 2 pi j);  P_tau = e^{tau d^2} p_k;  q_tau(u) = e^{-tau/4} Re[e^{iu/2} P_tau(u+i tau)].
(1) q_tau(0) = e^{-tau/4} Re P_tau(i tau): check divisibility by tau(tau-2) for k=1..7.
(2) q_tau'(0): check whether it vanishes at tau=2 (double zero at the block edge u=0 at tau=2).
(3) k=2 (5-block) explicit: zeros of q_tau near u=0 for tau<2 and the double zero at tau=2; plus a
    numerical check that no other double zero occurs for tau<2 (resultant-free: track all zeros)."""
import sympy as sp
u,tau=sp.symbols('u tau',real=True)
def heat(p,t):
    # e^{t d^2} p = sum_j t^j/j! p^{(2j)}
    out=0; d=p; j=0
    while d!=0:
        out+=t**j/sp.factorial(j)*d; d=sp.diff(d,u,2); j+=1
    return sp.expand(out)
for k in range(1,8):
    p=sp.prod([(u-2*sp.pi*j) for j in range(k)])
    P=heat(p,tau)
    z=sp.expand(P.subs(u,sp.I*tau))
    re=sp.simplify(sp.re(z)); im=sp.simplify(sp.im(z))
    # q'(0) = e^{-tau/4} Re[ (i/2) P(i tau) + P'(i tau) ]
    dP=sp.diff(P,u)
    q1=sp.simplify(sp.re(sp.I/2*z+sp.expand(dP.subs(u,sp.I*tau))))
    print(f"k={k}: q(0)*e^(tau/4) = {sp.factor(re)}")
    print(f"       q'(0)*e^(tau/4) = {sp.factor(q1)}   -> at tau=2: {sp.simplify(q1.subs(tau,2))}")
# (3) k=2 explicit
P2=heat(u*(u-2*sp.pi),tau)
q2=sp.simplify(sp.re(sp.expand(sp.exp(sp.I*u/2)*P2.subs(u,u+sp.I*tau)).rewrite(sp.cos)))
print("k=2: q_tau(u) e^{tau/4} =",sp.simplify(q2))
print("k=2: q_2(u) e^{1/2} =",sp.simplify(q2.subs(tau,2)), "; series at u=0:",sp.series(q2.subs(tau,2),u,0,4))
