"""Structured search over macroscopic profiles at N (Task C step 1/5): symmetric gap patterns built from
segments [1^{a}] + [g1^{b1}] + [g2^{b2}] + [hole] + [g2^{b2}] + [g1^{b1}]  (run, two buffer types with gap
values in {2,3,4}, a single hole), plus two-run profiles [1^a, 2^b, hole, 2^b, 1^a, 2^b, hole, 2^b].
Exhaustive over a grid, ODE solver. Reports the top 12 and the best one-hole run|clock|hole value."""
import numpy as np, sys, time, itertools
from push_C_fast import depth_ode, theta_from_gaps
N=int(sys.argv[1]); t0=time.time(); results=[]
def ev(g,label):
    if sum(g)!=2*N or len(g)!=N or min(g)<1: return
    d,i=depth_ode(theta_from_gaps(g),rtol=1e-10); results.append((N*N*d,label,g))
# one hole, two buffer types
for a in range(2,N):                      # run of a sites (a-1 unit gaps)
    for g1,g2 in [(2,2),(2,3),(3,2),(2,4),(3,3),(4,2),(3,4),(4,3)]:
        for b1 in range(0,N):
            for b2 in range(0,N):
                n=(a-1)+2*b1+2*b2+1
                if n!=N: continue
                hole=2*N-(a-1)-2*(g1*b1+g2*b2)
                if hole<1: continue
                g=[1]*(a-1)+[g1]*b1+[g2]*b2+[hole]+[g2]*b2+[g1]*b1
                ev(g,f"run{a}|{g1}^{b1}|{g2}^{b2}|hole{hole}")
# two runs with two holes (symmetric)
for a in range(2,N//2+1):
    for b in range(0,N//2):
        n=2*((a-1)+2*b+1)
        if n!=N: continue
        hole=(2*N-2*(a-1)-8*b)//2
        if hole<1 or 2*hole!=2*N-2*(a-1)-8*b: continue
        g=([1]*(a-1)+[2]*b+[hole]+[2]*b)*2
        ev(g,f"2x(run{a}|2^{b}|hole{hole})")
results.sort(key=lambda r:-r[0])
print(f"N={N}: {len(results)} profiles evaluated in {time.time()-t0:.0f}s. Top 12:")
for v,l,g in results[:12]: print(f"  {v:.6f}  {l}")
