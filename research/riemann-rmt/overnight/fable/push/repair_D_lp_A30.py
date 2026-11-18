"""push_D_lp.py with the support of F-1 extended to (1,30] (F=1 beyond 30), same cells/cutting planes; RH-only (gold=0)."""
import sys; sys.argv=['x','0']
import push_D_lp as L
import numpy as np
A=float(__import__('os').environ.get('AMAX','30'))
segs=[(1,3,0.02),(3,6,0.05),(6,12,0.1),(12,A,0.2)]
W=L.solve(segs,False,UMAX=400.0,u0=40.0,du0=0.02,ducheck=0.002,nadd=1500,maxit=30,label=f"A={A} gold=0",outfile=f"repair_D_lp_A{int(A)}_gold0.json")
print("DONE W=",W)
