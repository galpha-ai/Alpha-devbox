"""fab_lr_bridge.py — the Lagarias-Rodgers hard core and the Newman depth are the same
coordinate, and the conversion constant is exact.

LR:  mu = sup{ c : exists X in T_1 (bandwidth-one sine mimicker) with min spacing >= c },
     mean spacing normalised to 1.  Proved 1/2 <= mu <= 0.606894...
Us:  -Lambda = rho * delta_min^2 / 8,  rho >= 1 the background (Coulomb) delay factor.

On the circle with N points, mean angular spacing 2*pi/N, a hard core of c mean-spacings is
delta_min = 2*pi*c/N, hence

        N^2 (-Lambda)  =  rho * (2 pi c)^2 / 8  =  rho * pi^2 c^2 / 2.

c = 1/2 (the LR half-lattice = ACUE) gives  N^2(-Lambda) = rho * pi^2/8,  pi^2/8 = 1.2337...
So the whole ACUE depth law is the LR hard core, read in a different coordinate.
This script checks the identity on our exact enumeration and pins the extremal rho's.
"""
import numpy as np, sys
sys.path.insert(0, ".")
from dyn1_core import coeffs, find_ustar
SP="."
PI2_8 = np.pi**2/8

print(f"conversion:  N^2(-Lambda) = rho * pi^2 c^2 / 2 ;   at c=1/2:  rho * {PI2_8:.10f}\n")
print("ACUE exact enumeration: min / median / max of N^2(-Lambda), and the implied rho")
print(f"{'N':>3} {'min':>11} {'rho_min':>9} {'median':>11} {'rho_med':>9} {'max':>11} {'rho_max':>9}")
for N in range(3,11):
    d=np.load(f"{SP}/dyn1_results_N{N}.npz")
    m=~d['clockmask']; x=(N*N)*d['ustars'][m]; w=d['mu'][m]/d['mu'][m].sum()
    o=np.argsort(x); cw=np.cumsum(w[o]); med=x[o][np.searchsorted(cw,0.5)]
    print(f"{N:>3} {x.min():>11.6f} {x.min()/PI2_8:>9.5f} {med:>11.6f} {med/PI2_8:>9.5f}"
          f" {x.max():>11.6f} {x.max()/PI2_8:>9.5f}")

# the extremal families, pushed to larger N
def depth(idx,N):
    a=coeffs(np.array(sorted(idx)),N); u,_,_=find_ustar(a,N); return u
def twoblock(N):   # {0..N-3} u {N+3,N+4}: the observed minimiser family
    return list(range(0,N-2))+[N+3,N+4]
print("\nminimising family  {0..N-3} u {N+3,N+4}  (dyn1's argmin):")
print(f"{'N':>3} {'N^2(-Lambda)':>15} {'rho':>10}")
vals=[]
for N in range(6,19):
    idx=twoblock(N)
    if len(set(idx))!=N or max(idx)>=2*N: continue
    v=N*N*depth(idx,N); vals.append((N,v))
    print(f"{N:>3} {v:>15.8f} {v/PI2_8:>10.6f}")
ns=np.array([n for n,_ in vals[-6:]],float); vs=np.array([v for _,v in vals[-6:]])
A=np.vstack([np.ones_like(ns),ns**-1,ns**-2]).T; c,*_=np.linalg.lstsq(A,vs,rcond=None)
print(f"  extrapolated min  -> N^2(-Lambda) = {c[0]:.7f}   rho_min = {c[0]/PI2_8:.6f}")
print(f"  (pi^2/8 = {PI2_8:.7f} would be rho_min = 1 exactly)")
