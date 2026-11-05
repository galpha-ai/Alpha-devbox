"""Large-N scans with the ODE solver.
mode=runs:  symmetric L-run in the clock with far compensation [1^{L-1}, 2^k, L+1, 2^k], k=(N-L)/2, N large:
            gives the local-model value tau*_L = lim N^2 D.
mode=iface: interface family [1^{L-1}, 2^k, L+1, 2^k] at N with k in [kmin,kmax] (macroscopic buffers)."""
import numpy as np, sys, time
from push_C_fast import depth_ode, theta_from_gaps
mode=sys.argv[1]
if mode=='runs':
    Ns=[int(x) for x in sys.argv[2].split(',')]; Ls=[int(x) for x in sys.argv[3].split(',')]
    for L in Ls:
        line=f"L={L:2d}:"
        for N0 in Ns:
            N=N0 if (N0-L)%2==0 else N0+1; k=(N-L)//2; g=[1]*(L-1)+[2]*k+[L+1]+[2]*k
            t0=time.time(); d,i=depth_ode(theta_from_gaps(g),rtol=1e-11); line+=f"  N={N}: {N*N*d:.7f} (pair {i}, {time.time()-t0:.0f}s)"
        print(line,flush=True)
else:
    Ns=[int(x) for x in sys.argv[2].split(',')]; fr=[float(x) for x in sys.argv[3].split(',')]  # k range as fractions of N
    for N in Ns:
        t0=time.time(); rows=[]
        for k in range(int(fr[0]*N),int(fr[1]*N)+1):
            L=N-2*k; g=[1]*(L-1)+[2]*k+[L+1]+[2]*k
            d,i=depth_ode(theta_from_gaps(g),rtol=1e-11); rows.append((k,N*N*d,i))
        kb,vb,ib=max(rows,key=lambda r:r[1])
        print(f"N={N:4d} best {vb:.7f} at k={kb} (k/N={kb/N:.3f}, L={N-2*kb}, pair {ib})  [{time.time()-t0:.0f}s]\n     "+" ".join(f"k={k}:{v:.6f}" for k,v,i in rows),flush=True)
