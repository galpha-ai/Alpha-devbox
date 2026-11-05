"""Independent polyroots check (Method A, dps=60) of the 7-run in a clock at N=63 and the 9-run at N=65,
which the ODE solver puts at 2.037 / ? while local_models.py (fixed-bracket tracker) claimed 1.843 / 1.741."""
import mpmath as mp, time
from push_C_verify import methodA
for g,label in [([1]*6+[2]*28+[8]+[2]*28,"7-run N=63"),([1]*8+[2]*28+[10]+[2]*28,"9-run N=65")]:
    N=len(g); assert sum(g)==2*N
    t0=time.time(); tau,ang=methodA(g,dps=60,scan=False)
    print(f"{label}: Method A N^2 D = {mp.nstr(tau,15)}  [{time.time()-t0:.0f}s]",flush=True)
