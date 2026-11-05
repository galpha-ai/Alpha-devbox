import numpy as np, sys, time
from heat_depth import HeatDepth, gaps_to_theta
# symmetric run of L consecutive sites in the alternating clock, compensation gap L+1 opposite
def runL(N,L):
    assert (N-L)%2==0; k=(N-L)//2; g=[1]*(L-1)+[2]*k+[L+1]+[2]*k; assert sum(g)==2*N and len(g)==N; return g
Ls=[int(x) for x in sys.argv[1].split(',')]; Ns=[int(x) for x in sys.argv[2].split(',')]
for L in Ls:
    print("== L",L,flush=True)
    for N in Ns:
        if (N-L)%2: N+=1
        t0=time.time(); g=runL(N,L); H=HeatDepth(gaps_to_theta(g))
        # candidate pairs: all run gaps (indices 0..L-2) 
        d,i=H.depth(pairs=list(range(L-1))); print(f"L={L} N={N} N^2D={N*N*d:.10f} pair={i} t={time.time()-t0:.1f}s",flush=True)
