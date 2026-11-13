"""Diagnostics (Task C step 2): gap trajectories of the colliding pair for (a) the symmetric 3-block,
(b) the N=12 winner [1^7,2,2,9,2,2], (c) the 7-run [1^6,2^k,8,2^k] at N=63 (local k=3 model ~1.843),
(d) the dislocation. For the critical pair we print g(tau) (units pi/N), the two-body rate -2cot(g/2),
the background bracket B = sum_k [cot(x_b^k/2) - cot(x_a^k/2)] (>=0, Theorem A), and the ratio B/(g S*)."""
import numpy as np
from scipy.integrate import solve_ivp
from push_C_fast import rhs, theta_from_gaps, depth_ode
def analyse(g,label,pair=None,taus=None):
    N=len(g); th0=theta_from_gaps(g); D,ip=depth_ode(th0); 
    if pair is None: pair=ip
    taus=taus if taus is not None else np.linspace(0,0.98*N*N*D,8)
    sol=solve_ivp(rhs,(0,taus[-1]/N**2),th0,method='DOP853',rtol=1e-12,atol=1e-14,dense_output=True)
    print(f"== {label}: N={N}, N^2 D={N*N*D:.8f}, critical pair index {pair} (sites {g[:pair]} -> gap {g[pair]})")
    print("   tau     g/(pi/N)   -2cot(g/2)/N   B/N      B/(g S*)   drift (theta_a'+theta_b')/2 /N")
    for t in taus:
        th=sol.sol(t/N**2); a,b=pair,(pair+1)%N
        gap=(th[b]-th[a])%(2*np.pi); v=rhs(0,th)
        xb=(th[a]-th)%(2*np.pi); xa=(th[b]-th)%(2*np.pi)
        mask=np.ones(N,bool); mask[[a,b]]=False
        B=np.sum(1/np.tan(xb[mask]/2)-1/np.tan(xa[mask]/2))
        Sst=0.5*np.sum(np.maximum(1/np.sin(xb[mask]/2)**2,1/np.sin(xa[mask]/2)**2))
        print(f"  {t:6.3f}  {gap*N/np.pi:9.6f}  {-2/np.tan(gap/2)/N:9.4f}  {B/N:8.4f}  {B/(gap*Sst):8.4f}   {(v[a]+v[b])/2/N:8.4f}")
analyse([1,1]+[2]*30+[4]+[2]*30,"3-block N=63",pair=0)
analyse([1]*7+[2,2,9,2,2],"N=12 winner (8-run, k=2)",pair=0)
analyse([1]*7+[2]*10+[9]+[2]*10,"8-run in clock N=28 (far compensation)",pair=0)
analyse([1]*6+[2]*28+[8]+[2]*28,"7-run in clock N=63",pair=0)
analyse([3,1]+[2]*30,"dislocation N=32",pair=1)
analyse([1]*13+[2,2,2,15,2,2,2],"N=20 (L=14,k=3)",pair=0)
