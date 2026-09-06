"""Scan the one-hole interface family  [1^{L-1}, 2^{k1}, L+1, 2^{k2}],  N = L + k1 + k2  (run of L sites,
k1 and k2 clock points, one hole of L+1 sites), with the validated ODE solver (Method C)."""
import numpy as np, sys, time
from push_C_fast import depth_ode, theta_from_gaps
Ns=[int(x) for x in sys.argv[1].split(',')]
kmax=int(sys.argv[2]) if len(sys.argv)>2 else 12
asym=(sys.argv[3]=='asym') if len(sys.argv)>3 else False
for N in Ns:
    t0=time.time(); best=(-1,None); rows=[]
    ks=[(k,k) for k in range(0,min(kmax,(N-2)//2)+1)]
    if asym: ks=[(k1,k2) for k1 in range(0,min(kmax,N-2)+1) for k2 in range(k1,min(kmax,N-2)+1) if N-k1-k2>=2]
    for k1,k2 in ks:
        L=N-k1-k2; g=[1]*(L-1)+[2]*k1+[L+1]+[2]*k2; assert sum(g)==2*N and len(g)==N
        d,i=depth_ode(theta_from_gaps(g)); v=N*N*d; rows.append((k1,k2,L,v,i))
        if v>best[0]: best=(v,(k1,k2,L,i))
    line=" ".join(f"k={k1}{'' if k1==k2 else ','+str(k2)}:{v:.6f}" for k1,k2,L,v,i in rows)
    print(f"N={N:3d} best {best[0]:.8f} at (k1,k2,L,pair)={best[1]}  [{time.time()-t0:.0f}s]\n     {line}",flush=True)
