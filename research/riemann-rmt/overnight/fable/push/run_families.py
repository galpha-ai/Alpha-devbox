import numpy as np, sys, time
from heat_depth import HeatDepth, gaps_to_theta
def fam(name,N):
    if name=='disloc': g=[3,1]+[2]*(N-2)
    elif name=='block4': k=(N-3)//2; g=[1,1]+[2]*k+[4]+[2]*(N-3-k)
    elif name=='block33': k=(N-4)//2; g=[1,1]+[2]*k+[3,3]+[2]*(N-4-k)
    elif name=='block_3adj3': g=[3,1,1,3]+[2]*(N-4)
    elif name=='block_4adj': g=[4,1,1]+[2]*(N-3)
    elif name=='quad5': k=(N-4)//2; g=[1,1,1]+[2]*k+[5]+[2]*(N-4-k)
    elif name=='block5': k=(N-5)//2; g=[1,1,1,1]+[2]*k+[6]+[2]*(N-5-k)
    elif name=='halfblock': g=[1]*(N-1)+[N+1]
    elif name=='pair_far': # two separate dislocations opposite: [3,1,2..2,3,1,2..2]
        k=(N-4)//2; g=[3,1]+[2]*k+[3,1]+[2]*(N-4-k)
    assert sum(g)==2*N and len(g)==N
    return g
Ns=[8,12,16,24,32,48,64,96,128,192,256,384]
for name in sys.argv[1:]:
    print("==",name,flush=True); prev=None
    for N in Ns:
        if name=='block33' and N%2: continue
        t0=time.time(); g=fam(name,N); H=HeatDepth(gaps_to_theta(g))
        d,i=H.depth(pairs=[0,1,2,N-1]); v=N*N*d
        print(f"N={N:4d}  N^2D={v:.12f}  pair={i}  t={time.time()-t0:.1f}s",flush=True)
