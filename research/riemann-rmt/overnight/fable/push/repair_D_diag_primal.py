"""Diagnostic: primal minimiser of the damped-dual LP (atoms at the alpha grid) and its exact pair-positivity R(u)."""
import numpy as np, time, sys
import repair_D_certificate as R
sig=tuple(float(t) for t in sys.argv[1].split(',')); umax=float(sys.argv[2]); ustep=float(sys.argv[3])
cols=R.build(sig,umax,ustep)
a_init=np.unique(np.concatenate([np.arange(1.0,16.0+1e-9,0.02),np.arange(16.0,60.0+1e-9,0.1)]))
a_check=np.arange(1.0,60.0+1e-9,0.001)
res,agrid=R.cutting_planes(cols,a_init,a_check,grh=False,maxit=6,nadd=1500,label=f"diag{sig}")
lam=-res.ineqlin.marginals; al=agrid
print("primal (two-sided) mass Σλ =",lam.sum()," B+Σλ K =",R.B+lam@R.K(al)," dual value B-c.x =",R.B-res.fun)
for lo,hi in [(1,1.5),(1.5,2),(2,3),(3,5),(5,8),(8,12),(12,16),(16,20),(20,30),(30,60)]:
    sel=(al>=lo)&(al<hi); print(f"  mass on [{lo},{hi}): {lam[sel].sum():.4f}   K-weighted: {(lam[sel]*R.K(al[sel])).sum():+.5f}")
big=np.argsort(-lam)[:12]; print("  largest atoms (alpha,mass):",[(round(al[i],3),round(lam[i],4)) for i in big])
# exact R(u) of this F_out (finite even measure, no density beyond): R(u)=1-sinc^2(u)+sin(2πu)/(πu)+Σλ cos(2π α u)
act=lam>1e-12; la=lam[act]; aa=al[act]
u=np.arange(0.001,400.0001,0.001); Rmin=1e9; umin=None
for k0 in range(0,len(u),20000):
    uu=u[k0:k0+20000]
    Rv=1-(np.sin(np.pi*uu)/(np.pi*uu))**2+np.sin(2*np.pi*uu)/(np.pi*uu)+np.cos(2*np.pi*np.outer(uu,aa))@la
    i=Rv.argmin()
    if Rv[i]<Rmin: Rmin=Rv[i]; umin=uu[i]
print(f"  exact pair density of the primal minimiser: min R(u) on (0,400] = {Rmin:.4f} at u={umin:.3f}  (>=0 would mean the minimiser is pair-positive)")
# smoothed R at the LP's own test points should be >= 0: check a few
