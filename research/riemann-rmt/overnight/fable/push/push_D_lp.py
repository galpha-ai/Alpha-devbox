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
def solve(segs, goldston, UMAX=400.0, u0=40.0, du0=0.02, ducheck=0.002, nadd=1500, maxit=30, method='highs-ipm', label="", outfile=None):
    lo,hi=build_cells(segs); n=len(lo); mid=(lo+hi)/2; da=hi-lo; A=hi[-1]
    cK = 2*( s2*(np.exp(-2*lo)-np.exp(-2*hi))/2 - s1*(np.exp(-lo)-np.exp(-hi)) )
    Bband = 2*( s2*(1-3*np.exp(-2))/4 - s1*(1-2*np.exp(-1)) )
    tailK = 2*( s2*np.exp(-2*A)/2 - s1*np.exp(-A) )
    bounds=[(max(0,1.5-mid[i]) if (goldston and mid[i]<=1.5) else 0, None) for i in range(n)]
    us=np.arange(0.0,u0+1e-9,du0)
    ucheck=np.arange(ducheck,UMAX+1e-9,ducheck)
    t0=time.time(); hist=[]
    for it in range(maxit):
        cc,sinc2=cc_rows(us,lo,hi)
        res=linprog(cK,A_ub=-cc,b_ub=1-sinc2-cc.sum(axis=1),bounds=bounds,method=method)
        if res.status!=0:
            print(label,"status",res.status,res.message,flush=True); return None
        x=res.x; W=Bband+res.fun+tailK
        worst=[]; minR=1e9
        for k in range(0,len(ucheck),20000):
            uu=ucheck[k:k+20000]; ccu,s2u=cc_rows(uu,lo,hi)
            R=1-s2u+ccu@(x-1); minR=min(minR,R.min())
            idx=np.argsort(R)[:nadd]; worst+=[(R[i],uu[i]) for i in idx if R[i]<-1e-7]
        worst.sort(); hist.append((W,minR,len(us)))
        print(f"{label} it={it} W={W:.6f} ncons={len(us)} minR={minR:.4f} nviol={len(worst)} [{time.time()-t0:.0f}s]",flush=True)
        if outfile: json.dump(dict(W=W,minR=minR,x=x.tolist(),lo=lo.tolist(),hi=hi.tolist(),ncons=len(us),it=it,hist=hist),open(outfile,'w'))
        if minR>=-1e-6: break
        newu=np.array([u for _,u in worst[:nadd]]); us=np.unique(np.concatenate([us,newu]))
    a0=np.log(2*np.cosh(1)); sel=mid>a0
    print(label,"FINAL W=",W," 2int_{a0}^A K F* =",(cK[sel]*x[sel]).sum()," 2int_1^{a0} K F* =",(cK[~sel]*x[~sel]).sum(),flush=True)
    order=np.argsort(-x*da)[:12]
    print(label,"largest cell masses (alpha, mass):",[(round(mid[i],3),round(x[i]*da[i],3)) for i in order],flush=True)
    print(label,"F* at 1.05,1.3,1.6,1.9,2.5,3,5,8:",[round(x[np.argmin(abs(mid-a))],3) for a in [1.05,1.3,1.6,1.9,2.5,3,5,8]],flush=True)
    return W
if __name__=='__main__':
    gold = sys.argv[1]=='1'
    segs=[(1,3,0.02),(3,6,0.05),(6,12,0.1)]
    solve(segs,gold,label=f"gold={gold}",outfile=f"lp4_gold{int(gold)}.json")
    print("DONE",flush=True)
