"""Refuter's re-run of push_D_lp.py with (a) dual extraction, (b) a finer check grid,
(c) a pointwise certificate test.  Same primal model as push_D_lp.py."""
import numpy as np, time, sys, json
from scipy.optimize import linprog
s1, s2 = np.sinh(1), np.sinh(2)
def build_cells(segs):
    lo=[];hi=[]
    for a,b,d in segs:
        e=np.arange(a,b-1e-12,d); lo+=list(e); hi+=list(e+d)
    return np.array(lo),np.array(hi)
def cc_rows(us,lo,hi):
    with np.errstate(divide='ignore', invalid='ignore'):
        cc=(np.sin(2*np.pi*hi[None,:]*us[:,None])-np.sin(2*np.pi*lo[None,:]*us[:,None]))/(np.pi*us[:,None])
    z=(us==0); cc[z,:]=2*(hi-lo)
    sinc2=np.ones_like(us); nz=~z; sinc2[nz]=(np.sin(np.pi*us[nz])/(np.pi*us[nz]))**2
    return cc, sinc2
def solve(segs, goldston, UMAX=400.0, u0=40.0, du0=0.02, ducheck=0.002, nadd=1500, maxit=40, label="", outfile=None):
    lo,hi=build_cells(segs); n=len(lo); mid=(lo+hi)/2; da=hi-lo; A=hi[-1]
    cK = 2*( s2*(np.exp(-2*lo)-np.exp(-2*hi))/2 - s1*(np.exp(-lo)-np.exp(-hi)) )
    Bband = 2*( s2*(1-3*np.exp(-2))/4 - s1*(1-2*np.exp(-1)) )
    tailK = 2*( s2*np.exp(-2*A)/2 - s1*np.exp(-A) )
    lb=np.array([max(0,1.5-mid[i]) if (goldston and mid[i]<=1.5) else 0.0 for i in range(n)])
    bounds=[(lb[i],None) for i in range(n)]
    us=np.arange(0.0,u0+1e-9,du0)
    ucheck=np.arange(ducheck,UMAX+1e-9,ducheck)
    t0=time.time()
    for it in range(maxit):
        cc,sinc2=cc_rows(us,lo,hi)
        b_ub=1-sinc2-cc.sum(axis=1)
        res=linprog(cK,A_ub=-cc,b_ub=b_ub,bounds=bounds,method='highs-ds')
        if res.status!=0:
            print(label,"status",res.status,res.message,flush=True); return None
        x=res.x; W=Bband+res.fun+tailK
        worst=[]; minR=1e9
        for k in range(0,len(ucheck),20000):
            uu=ucheck[k:k+20000]; ccu,s2u=cc_rows(uu,lo,hi)
            R=1-s2u+ccu@(x-1); minR=min(minR,R.min())
            idx=np.argsort(R)[:nadd]; worst+=[(R[i],uu[i]) for i in idx if R[i]<-1e-7]
        worst.sort()
        print(f"{label} it={it} W={W:.6f} ncons={len(us)} minR={minR:.5f} nviol={len(worst)} [{time.time()-t0:.0f}s]",flush=True)
        if minR>=-1e-6: break
        newu=np.array([u for _,u in worst[:nadd]]); us=np.unique(np.concatenate([us,newu]))
    # ---- dual certificate ----
    y=-res.ineqlin.marginals            # >= 0 multipliers of  cc.x >= -b_ub
    z=res.lower.marginals               # >= 0 multipliers of x >= lb
    dual_obj = -(y@b_ub) + z@lb
    print(label,"primal obj",res.fun,"dual obj",dual_obj,"n active duals",(y>1e-12).sum(),flush=True)
    # per-cell dual feasibility  cK - cc^T y = z >= 0
    slack = cK - cc.T@y
    print(label,"min per-cell slack (should be >= -tiny):",slack.min(),flush=True)
    # pointwise certificate g(alpha) = 2K(alpha) - sum_j y_j 2cos(2 pi alpha u_j) on a fine alpha grid
    ua=us[y>1e-12]; ya=y[y>1e-12]
    al=np.arange(1.0005,A,0.001)
    K=lambda a: s2*np.exp(-2*a)-s1*np.exp(-a)
    g=2*K(al) - 2*np.cos(2*np.pi*np.outer(al,ua))@ya
    neg=g<0
    print(label,f"pointwise certificate g: min={g.min():.5f} at alpha={al[g.argmin()]:.4f}; fraction of alpha-grid with g<0: {neg.mean():.4f}; int of negative part={np.trapezoid(np.where(neg,g,0),al):.6f}",flush=True)
    # what a pointwise-valid certificate would give: W >= Bband + tailK + dual_obj + (sum of negative parts x any admissible mass)
    a0=np.log(2*np.cosh(1))
    print(label,"FINAL W=",W," Bband=",Bband," tailK=",tailK,flush=True)
    if outfile:
        json.dump(dict(W=W,minR=minR,x=x.tolist(),lo=lo.tolist(),hi=hi.tolist(),us=us.tolist(),y=y.tolist(),dual_obj=dual_obj,ducheck=ducheck),open(outfile,'w'))
    return W
if __name__=='__main__':
    gold = sys.argv[1]=='1'
    ducheck=float(sys.argv[2]) if len(sys.argv)>2 else 0.002
    segs=[(1,3,0.02),(3,6,0.05),(6,12,0.1)]
    solve(segs,gold,ducheck=ducheck,label=f"gold={gold} ducheck={ducheck}",outfile=f"refute_lp_gold{int(gold)}_dc{ducheck}.json")
    print("DONE",flush=True)
