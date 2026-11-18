"""push_D_lp.py with the support of F-1 extended to (1,AMAX] (F=1 beyond AMAX); cells 0.02/0.05/0.1/0.2; env AMAX, DUCHECK, GOLD, U0, DU0.
   NB: the initial u-grid step must be < 1/(2*AMAX) or cells near alpha = 1/DU0 alias to a constant and the LP is unbounded."""
import sys, os; sys.argv=['x','0']
import push_D_lp as L
A=float(os.environ.get('AMAX','30')); dc=float(os.environ.get('DUCHECK','0.002')); gold=os.environ.get('GOLD','0')=='1'
u0=float(os.environ.get('U0','40')); du0=float(os.environ.get('DU0','0.02'))
segs=[(1,3,0.02),(3,6,0.05),(6,12,0.1),(12,A,0.2)]
W=L.solve(segs,gold,UMAX=400.0,u0=u0,du0=du0,ducheck=dc,nadd=1500,maxit=40,label=f"A={A} dc={dc} gold={int(gold)}",outfile=f"repair_D_lp_A{int(A)}_dc{dc}_gold{int(gold)}.json")
print("DONE W=",W)
