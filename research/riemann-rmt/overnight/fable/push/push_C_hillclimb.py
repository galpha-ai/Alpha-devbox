"""Stochastic hill-climb over ALL gap patterns (compositions of 2N into N positive parts, up to
rotation) at given N, maximising N^2 D with the ODE solver. Moves: transfer one unit from gap i to gap j
(keeping all gaps >= 1), or swap two gaps. Restarts from random compositions and from the interface family."""
import numpy as np, sys, time
from push_C_fast import depth_ode, theta_from_gaps
N=int(sys.argv[1]); restarts=int(sys.argv[2]); steps=int(sys.argv[3]); seed=int(sys.argv[4]) if len(sys.argv)>4 else 0
rng=np.random.default_rng(seed)
def canon(g):
    g=list(map(int,g)); best=None
    for h in (g,g[::-1]):
        for r in range(N):
            t=tuple(h[r:]+h[:r])
            if best is None or t<best: best=t
    return best
cache={}
def val(g):
    c=canon(g)
    if c in cache: return cache[c]
    if all(x==2 for x in c): v=np.inf
    else:
        d,i=depth_ode(theta_from_gaps(list(c))); v=N*N*d
    cache[c]=v; return v
def random_comp():
    cuts=np.sort(rng.choice(np.arange(1,2*N),N-1,replace=False)); parts=np.diff(np.concatenate([[0],cuts,[2*N]])); return list(map(int,parts))
def mutate(g):
    g=list(g)
    if rng.random()<0.7:
        i,j=rng.choice(N,2,replace=False)
        if g[i]>=2: g[i]-=1; g[j]+=1
    else:
        i,j=rng.choice(N,2,replace=False); g[i],g[j]=g[j],g[i]
    return g
t0=time.time(); gbest=(-1,None)
for r in range(restarts):
    if r==0:
        k=max(1,int(round(np.sqrt(N)/1.3))); L=N-2*k; g=[1]*(L-1)+[2]*k+[L+1]+[2]*k
    else: g=random_comp()
    v=val(g); T=0.02
    for st in range(steps):
        g2=mutate(g); v2=val(g2)
        if v2>=v or rng.random()<np.exp((v2-v)/T): g,v=g2,v2
        if v>gbest[0] and np.isfinite(v): gbest=(v,canon(g))
    print(f"restart {r}: local best {v:.6f} {canon(g)};  global best {gbest[0]:.8f} {gbest[1]}  [{time.time()-t0:.0f}s, {len(cache)} evals]",flush=True)
top=sorted([(v,c) for c,v in cache.items() if np.isfinite(v)],reverse=True)[:15]
print("TOP 15 found:")
for v,c in top: print(f"  {v:.8f} {list(c)}")
