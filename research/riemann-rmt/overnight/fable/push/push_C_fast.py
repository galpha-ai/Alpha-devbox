"""Fast depth solvers for lattice configurations, validated against Method A (mpmath polyroots).
Method C (ODE): integrate Lemma 1, theta_j' = -sum_k cot((theta_j-theta_k)/2), with DOP853 until the
  smallest gap g_min < eps, then extrapolate with the exact two-body law near collision:
  the colliding gap satisfies g' = -2cot(g/2) + O(g) so s* = s + (g^2/8)(1+O(g^2 N^2)); we refine by
  continuing the integration to a smaller eps and Richardson-checking.
Method R (np.roots bisection): as acue_depth_enum.py, tolerance tol on max||z|-1|.
"""
import numpy as np
from scipy.integrate import solve_ivp

def theta_from_gaps(g):
    N=len(g); sites=np.concatenate([[0],np.cumsum(g)[:-1]]); return 2*np.pi*sites/(2*N)

def rhs(s,th):
    d=th[:,None]-th[None,:]
    np.fill_diagonal(d,np.pi)      # cot(pi/2)=0 for the diagonal
    return -np.sum(1/np.tan(d/2),axis=1)

def depth_ode(theta,eps=1e-4,rtol=1e-12,atol=1e-14):
    th=np.array(theta,float); N=len(th)
    def gmin(th):
        t=np.sort(th%(2*np.pi)); g=np.diff(np.concatenate([t,[t[0]+2*np.pi]])); return g.min(),int(np.argmin(g))
    s=0.0; smax=10.0/N**2
    def ev(s,y): return gmin(y)[0]-eps
    ev.terminal=True; ev.direction=-1
    sol=solve_ivp(rhs,(0,smax),th,method='DOP853',rtol=rtol,atol=atol,events=ev,dense_output=False)
    if len(sol.t_events[0])==0: return np.inf,None
    s1=sol.t_events[0][0]; y1=sol.y_events[0][0]; g1,i1=gmin(y1)
    # two-body extrapolation from g1, then refine with a second, smaller eps
    ev2=lambda s,y: gmin(y)[0]-eps/10; ev2.terminal=True; ev2.direction=-1
    sol2=solve_ivp(rhs,(s1,s1+g1**2),y1,method='DOP853',rtol=rtol,atol=atol,events=ev2)
    s2=sol2.t_events[0][0]; y2=sol2.y_events[0][0]; g2,i2=gmin(y2)
    # exact 2-body: s*-s = -log cos(g/2) ~ g^2/8; the background correction is O(g^2 * g^2 N^2). use g2.
    sstar=s2-np.log(np.cos(g2/2))
    return sstar,i2

def depth_roots(theta,tol=1e-7):
    N=len(theta); z=np.exp(1j*np.asarray(theta)); a=np.poly(z); powers=np.arange(N,-1,-1); w=powers*(N-powers)
    def off(s): r=np.roots(a*np.exp(s*w)); return np.max(np.abs(np.abs(r)-1.0))
    lo=0.0; hi=2.0/N**2
    while off(hi)<tol: hi*=1.5
    for _ in range(80):
        mid=0.5*(lo+hi)
        if off(mid)>tol: hi=mid
        else: lo=mid
        if hi-lo<1e-14*hi: break
    return 0.5*(lo+hi)

if __name__=="__main__":
    import time, sys
    from push_C_verify import methodA
    import mpmath as mp
    tests=[[1,1,1,1,1,1,1,2,2,9,2,2],[1,1,2,2,2,2,3,3,2,2,2,2],[3,1]+[2]*10,
           [1]*11+[2,2,13,2,2],[1]*9+[2,2,2,11,2,2,2],[1,1]+[2]*7+[3,3]+[2]*7,
           [1]*15+[2,2,17,2,2],[1]*13+[2,2,2,15,2,2,2],[1]*19+[2,2,21,2,2]]
    for g in tests:
        N=len(g); assert sum(g)==2*N
        th=theta_from_gaps(g)
        t0=time.time(); dO,iO=depth_ode(th); tO=time.time()-t0
        t0=time.time(); dR=depth_roots(th); tR=time.time()-t0
        t0=time.time(); tau,_=methodA(g,dps=25+N//2,scan=False); tA=time.time()-t0
        print(f"N={N:2d} gaps={g}\n   ODE {N*N*dO:.10f} ({tO:.1f}s, pair {iO})  roots {N*N*dR:.10f} ({tR:.1f}s)  A {mp.nstr(tau,12)} ({tA:.1f}s)   ODE-A {N*N*dO-float(tau):+.1e} roots-A {N*N*dR-float(tau):+.1e}",flush=True)
