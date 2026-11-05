"""heat_depth.py runs for the midpoint-insertion families and the asymmetric block4-even family.
Families (gap patterns, units pi/N):
  block4even : [1,1]+2^k+[4]+2^(N-3-k)         N even, removed site N-1 (asymmetric)
  block5     : [1,1,1,1]+2^k+[6]+2^(N-5-k)      5-block (2 midpoints), local model (u^2-pi^2) sin(u/2)
  two3       : [1,1,2,1,1]+2^k+[6]+2^(N-6-k)    two 3-blocks separated by one lattice gap, (u^2-4pi^2)cos(u/2)
  block7     : [1]*6+2^k+[8]+2^(N-7-k)          7-block (3 midpoints), u(u^2-4pi^2)cos(u/2)
  two3b      : [1,1,2,2,1,1]+2^k+[6]+2^(N-7-k)  two 3-blocks separated by two lattice gaps, (u^2-9pi^2) sin(u/2)
usage: python run_families_A.py name [Nmax]
"""
import numpy as np, sys, time
from heat_depth import HeatDepth, gaps_to_theta
def fam(name,N):
    if name=='block4even': assert N%2==0; k=(N-4)//2; g=[1,1]+[2]*k+[4]+[2]*(N-3-k)
    elif name=='block5': k=(N-5)//2; g=[1,1,1,1]+[2]*k+[6]+[2]*(N-5-k)
    elif name=='two3':   k=(N-6)//2; g=[1,1,2,1,1]+[2]*k+[6]+[2]*(N-6-k)
    elif name=='block7': k=(N-7)//2; g=[1]*6+[2]*k+[8]+[2]*(N-7-k)
    elif name=='two3b':  k=(N-7)//2; g=[1,1,2,2,1,1]+[2]*k+[6]+[2]*(N-7-k)
    assert sum(g)==2*N and len(g)==N,(name,N,sum(g),len(g))
    return g
name=sys.argv[1]; Nmax=int(sys.argv[2]) if len(sys.argv)>2 else 128
Ns=[N for N in [16,24,32,48,64,96,128,192,256] if N<=Nmax]
print("==",name,flush=True)
for N in Ns:
    t0=time.time(); g=fam(name,N); H=HeatDepth(gaps_to_theta(g))
    nb=len([x for x in g if x==1])+1
    d,i=H.depth(pairs=list(range(nb+1))+[N-1]); v=N*N*d
    print(f"N={N:4d}  N^2D={v:.12f}  pair={i}  t={time.time()-t0:.1f}s",flush=True)
