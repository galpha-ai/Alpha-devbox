"""Polyroots (Method A, dps=60) check of the ODE value for the wall configuration at N=128, L=66, k=31 (ODE: 2.1035866)."""
import mpmath as mp, time
from push_C_verify import methodA
g=[1]*65+[2]*31+[67]+[2]*31; N=len(g); assert sum(g)==2*N
t0=time.time(); tau,ang=methodA(g,dps=60,scan=False)
print(f"wall N=128 L=66: Method A N^2 D = {mp.nstr(tau,14)}  (ODE: 2.1035866)  [{time.time()-t0:.0f}s]",flush=True)
