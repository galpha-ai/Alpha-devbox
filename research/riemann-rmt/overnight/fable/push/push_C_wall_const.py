"""Domain-wall constant C* = lim_{L->inf} tau*_L, tau*_L = lim_{N->inf} N^2 D for the symmetric L-run in the
clock with far compensation. For each L compute at N ~ 4L and ~8L (odd/even parity matched), Richardson in 1/N^2,
then fit tau*_L = C* + c1/L + c2/L^2 over the largest L."""
import numpy as np, sys, time
from push_C_fast import depth_ode, theta_from_gaps
Ls=[int(x) for x in sys.argv[1].split(',')]; mult=[int(x) for x in sys.argv[2].split(',')]
res={}
for L in Ls:
    vals=[]
    for m in mult:
        N=m*L; N=N if (N-L)%2==0 else N+1; k=(N-L)//2; g=[1]*(L-1)+[2]*k+[L+1]+[2]*k
        t0=time.time(); d,i=depth_ode(theta_from_gaps(g),rtol=1e-11); vals.append((N,N*N*d)); print(f"  L={L} N={N}: {N*N*d:.8f} [{time.time()-t0:.0f}s]",flush=True)
    (N1,v1),(N2,v2)=vals[-2],vals[-1]
    rich=(v2*N2**2-v1*N1**2)/(N2**2-N1**2)   # eliminate c/N^2
    res[L]=rich; print(f"L={L}: tau*_L (Richardson 1/N^2) = {rich:.8f}",flush=True)
Ls_fit=sorted(res)[-5:]
A=np.array([[1,1/L,1/L**2] for L in Ls_fit]); y=np.array([res[L] for L in Ls_fit])
c=np.linalg.lstsq(A,y,rcond=None)[0]; print(f"fit over L={Ls_fit}: C* = {c[0]:.6f}, c1={c[1]:.4f}, c2={c[2]:.3f}")
A=np.array([[1,1/L] for L in Ls_fit[-3:]]); y=np.array([res[L] for L in Ls_fit[-3:]])
c=np.linalg.lstsq(A,y,rcond=None)[0]; print(f"linear fit over L={Ls_fit[-3:]}: C* = {c[0]:.6f}, c1={c[1]:.4f}")
