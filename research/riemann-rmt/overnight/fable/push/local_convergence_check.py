"""Numerical check of Proposition 2 (push_A): for the symmetric 3-block families
   q^N_tau(u) := kappa_N e^{-tau/4}... normalised so that q^N_0(u) = cos(u/2) phi_N(u), phi_N'(0)=1,
   q^N_tau(u) = q_tau(u) + N^{-2} r_tau(u) + O(N^{-4}),  q_tau = e^{-tau/4}(u cos(u/2) - tau sin(u/2)),
   r_tau = e^{tau d^2}[cos(u/2) u^3/12] = e^{-tau/4} Re[e^{iu/2} P(u+i tau)]/12,  P = e^{tau d^2} u^3 = w^3 + 6 tau w.
q^N_tau is evaluated exactly from the Fourier coefficients (heat_depth's representation)."""
import numpy as np
from heat_depth import HeatDepth, gaps_to_theta
from threeblock_exact import gaps
def q_lim(u,t): return np.exp(-t/4)*(u*np.cos(u/2)-t*np.sin(u/2))
def r_lim(u,t):
    w=u+1j*t; P=w**3+6*t*w
    return np.exp(-t/4)*np.real(np.exp(1j*u/2)*P)/12
us=np.linspace(-2*np.pi,2*np.pi,161)
for name in ['block4odd','block33']:
    print("==",name)
    for N in ([17,33,65,129,257] if name=='block4odd' else [16,32,64,128,256]):
        th=gaps_to_theta(gaps(name,N))-np.pi/N     # added root at angle 0
        H=HeatDepth(th)
        # normalisation: q^N_0(u) = c * Q_0(u/N) with c chosen so that d/du q^N_0(0)=1
        d0=H.Qs(np.array([0.0]),0.0,1)[0]/N        # d/du Q_0(u/N) at 0
        c=1.0/d0
        e1=0; e2=0
        for t in [0.0,0.5,1.0,1.5,2.0,2.5,3.0]:
            s=t/N**2
            qN=c*np.exp(-t/4)*H.Qs(us/N,s)          # Q_s = e^{sN^2/4} e^{s d_x^2} Q_0  ->  q^N_tau = c e^{-tau/4} Q_s(u/N)
            e1=max(e1,np.max(np.abs(qN-q_lim(us,t))))
            e2=max(e2,np.max(np.abs(qN-q_lim(us,t)-r_lim(us,t)/N**2)))
        print(f"  N={N:4d}  max|q^N-q| = {e1:.3e}  (N^2 x = {e1*N**2:.4f})   max|q^N-q-r/N^2| = {e2:.3e}  (N^4 x = {e2*N**4:.3f})")
