"""Empirical bracket ratio beta(tau) = B(s)/(N^2 g(s)) for the critical pair (needed for the conditional
theorem: N^2 D <= first zero of Y' = -8/pi^2 + 2 beta_max(tau) Y), along the extremal family at N=64,128,256
(optimal L) and for the 3-block, and the tau_2 predicted by the empirical envelope."""
import numpy as np
from scipy.integrate import solve_ivp
from push_C_fast import rhs, theta_from_gaps, depth_ode
def beta_curve(g,pair,npts=60):
    N=len(g); th0=theta_from_gaps(g); D,ip=depth_ode(th0)
    sol=solve_ivp(rhs,(0,0.999*D),th0,method='DOP853',rtol=1e-12,atol=1e-14,dense_output=True)
    taus=np.linspace(0,0.999*N*N*D,npts); out=[]
    for t in taus:
        th=sol.sol(t/N**2); a,b=pair,(pair+1)%N; gap=(th[b]-th[a])%(2*np.pi)
        xb=(th[a]-th)%(2*np.pi); xa=(th[b]-th)%(2*np.pi); m=np.ones(N,bool); m[[a,b]]=False
        B=np.sum(1/np.tan(xb[m]/2)-1/np.tan(xa[m]/2)); out.append((t,gap*N/np.pi,B/(N*N*gap)))
    return N*N*D,np.array(out)
fams={'3-block N=257':([1,1]+[2]*127+[4]+[2]*127,0),'wall N=64 L=34':([1]*33+[2]*15+[35]+[2]*15,0),
      'wall N=128 L=66':([1]*65+[2]*31+[67]+[2]*31,0),'wall N=256 L=130':([1]*129+[2]*63+[131]+[2]*63,0)}
env={}
for k,(g,p) in fams.items():
    v,c=beta_curve(g,p); env[k]=c
    print(f"== {k}: N^2D={v:.6f}");  print("   tau    g/(pi/N)   beta=B/(N^2 g)")
    for t,gg,b in c[::6]: print(f"  {t:6.3f}  {gg:8.5f}  {b:8.5f}")
# conditional theorem: Y' = -8/pi^2 + 2 beta(tau) Y, Y(0)=1, with beta from the N=256 wall curve (interpolated)
c=env['wall N=256 L=130']; tt=c[:,0]; bb=c[:,2]
def f(t,y): return [-8/np.pi**2+2*np.interp(t,tt,bb)*y[0]]
ev=lambda t,y:y[0]; ev.terminal=True; ev.direction=-1
sol=solve_ivp(f,(0,tt[-1]),[1.0],method='DOP853',rtol=1e-11,atol=1e-14,events=ev,dense_output=True)
print(f"Y-ODE with the empirical beta(tau) of the N=256 wall: Y at tau_end={tt[-1]:.4f} is {sol.y[0][-1]:.5f}; zero event: {sol.t_events[0]}")
print("(Y should reach 0 exactly at N^2D if the mean-value-type inequality were an equality; the gap between the Y-zero and N^2D measures the loss in B<=g S*, here none since beta is the exact ratio.)")
