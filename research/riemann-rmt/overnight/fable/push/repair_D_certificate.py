"""repair_D_certificate.py -- rigorous dual certificate for a lower bound on W over the
pair-positivity class (repair pass on push_D_last_mile.md, refuter issue 2).

Setting (all limits along subsequences, see push_D_last_mile.md, repaired §2.5):
  F_full = delta_0 + |a| da on (-1,1) + F_out,  F_out >= 0 supported on |a| >= 1 (even).
  W = B + int K dF_out,   K(a) = sinh2 e^{-2|a|} - sinh1 e^{-|a|},  B = 2 int_0^1 K a da.
  Pair positivity: for every nonnegative test function nu (with nuhat decaying),
        int nuhat dF_full >= nu(0) * mu({0}) >= nu(0)   (mu = limit pair measure, mu({0}) >= 1).
  Hence  int nuhat dF_out >= -c[nu],  c[nu] := nuhat(0) - nu(0) + 2 int_0^1 nuhat(a) a da.
  Window bound (nu = sinc^2 (1 - cos 2 pi b x) >= 0):  int (1-|a-b|)_+ dF_full <= 4/3 for all b.
  Certificate: for any nonneg nu,  W >= B - c[nu] - (8/3) sum_{b>=1} sup_{[b-1,b+1]} (nuhat - K)_+ .
  With the GRH floor F_out >= (3/2-|a|) da on (1,3/2):  add  2 int_1^{3/2} (K - nuhat)(3/2-a) da.

Families of nonnegative nu used (all even):
  G(u,s): Gaussian pair  G_s(x-u)+G_s(x+u)          nuhat = 2 cos(2 pi a u) exp(-2 pi^2 s^2 a^2)
  P(c):   16 pi^2 c x^2/(c^2+4 pi^2 x^2)^2          nuhat = (1 - c|a|) e^{-c|a|}
  T(b,e): e sinc^2(e x) (1 - cos 2 pi b x)          nuhat = psi_e(a) - [psi_e(a-b)+psi_e(a+b)]/2,  psi_e=(1-|a|/e)_+
The LP maximises B - sum x_k c_k subject to sum x_k nuhat_k(a_i) <= K(a_i) on a cutting-plane grid,
then the residual (nuhat-K)_+ is bounded rigorously on [1,ALPHA_MAX] by a fine grid plus a second-derivative
(or exact-linearity) bound, and beyond ALPHA_MAX by the Gaussian/exponential tails.

Usage: python3 repair_D_certificate.py validate      (reproduce push_D's truncated LP value by its dual)
       python3 repair_D_certificate.py certify [grh] [sigmas] [umax] [ustep]
"""
import numpy as np, sys, time, json
from scipy.optimize import linprog

s1, s2 = np.sinh(1.0), np.sinh(2.0)
def K(a):
    a = np.abs(a); return s2*np.exp(-2*a) - s1*np.exp(-a)
def Kpp_bound(a):   # |K''| <= 4 s2 e^{-2a} + s1 e^{-a}
    a = np.abs(a); return 4*s2*np.exp(-2*a) + s1*np.exp(-a)
B = 2*(s2*(1-3*np.exp(-2))/4 - s1*(1-2*np.exp(-1)))
_ag=np.linspace(1.0,1.5,400001); _wg=np.full(_ag.size,0.5/(_ag.size-1)); _wg[0]*=0.5; _wg[-1]*=0.5
G_GRH = float(2*np.sum(_wg*K(_ag)*(1.5-_ag)))   # 2 int_1^{3/2} K (3/2-a) da  (K<0 on (alpha_0,3/2): this is NOT push_D's 2 int_1^{alpha_0})

# quadrature on [0,1] (fine composite trapezoid; kinks of the window functions are at multiples of 1/4 -> grid points)
NQ = 200001
aq = np.linspace(0.0, 1.0, NQ); wq = np.full(NQ, 1.0/(NQ-1)); wq[0] *= 0.5; wq[-1] *= 0.5
a_grh = np.linspace(1.0, 1.5, 100001); w_grh = np.full(a_grh.size, 0.5/(a_grh.size-1)); w_grh[0]*=0.5; w_grh[-1]*=0.5

class Cols:
    """column family container: evaluate nuhat on alpha arrays, costs, second-derivative bounds"""
    def __init__(self):
        self.kind=[]; self.p1=[]; self.p2=[]
    def add(self, kind, p1, p2=0.0):
        self.kind.append(kind); self.p1.append(p1); self.p2.append(p2)
    def finalize(self):
        self.kind=np.array(self.kind); self.p1=np.array(self.p1,float); self.p2=np.array(self.p2,float)
        self.n=len(self.kind)
        self.cost=np.array([self.cost_of(k) for k in range(self.n)])
        self.cost_grh=np.array([2*np.sum(w_grh*self.nuhat_one(k,a_grh)*(1.5-a_grh)) for k in range(self.n)])
    def nuhat_one(self, k, a):
        a=np.abs(np.asarray(a,float)); kind=self.kind[k]; p1=self.p1[k]; p2=self.p2[k]
        if kind=='G':
            return 2*np.cos(2*np.pi*a*p1)*np.exp(-2*np.pi**2*p2**2*a**2)
        if kind=='P':
            return (1-p1*a)*np.exp(-p1*a)
        if kind=='T':
            b,e=p1,p2
            psi=lambda t: np.maximum(0.0,1-np.abs(t)/e)
            return psi(a)-0.5*(psi(a-b)+psi(a+b))
        raise ValueError
    def nu0(self,k):
        kind=self.kind[k]; p1=self.p1[k]; p2=self.p2[k]
        if kind=='G': return 2*np.exp(-p1**2/(2*p2**2))/(p2*np.sqrt(2*np.pi))
        return 0.0
    def cost_of(self,k):
        f=self.nuhat_one(k,aq)
        return float(f[0]) - self.nu0(k) + 2*np.sum(wq*f*aq)
    def matrix(self, a, idx=None):
        idx = np.arange(self.n) if idx is None else idx
        M=np.empty((len(a),len(idx)))
        for j,k in enumerate(idx): M[:,j]=self.nuhat_one(k,a)
        return M
    def tail_penalty(self, ALPHA_MAX):
        """(8/3) sum_{b>ALPHA_MAX} sup_{[b-1,b+1]} (nuhat_k)_+  for the Gaussian columns (P,T columns are <= 0 on the tail):
           linear in x, so it is added to the LP objective; makes the LP account for its own tail."""
        bmax=int(np.ceil(ALPHA_MAX)); bs=np.arange(bmax+1,bmax+400)-1.0
        pen=np.zeros(self.n)
        for k in range(self.n):
            if self.kind[k]=='G': pen[k]=(8/3)*np.sum(2*np.exp(-2*np.pi**2*self.p2[k]**2*bs**2))
        return pen
    def d2_bound(self, k, a):
        """pointwise bound for |nuhat_k''| at |alpha|=a (0 for the piecewise-linear windows away from kinks)"""
        kind=self.kind[k]; p1=self.p1[k]; p2=self.p2[k]
        if kind=='G':
            aa=2*np.pi**2*p2**2
            return 2*np.exp(-aa*a**2)*((2*np.pi*p1+2*aa*a)**2+2*aa)
        if kind=='P':
            return p1**2*np.exp(-p1*a)*np.abs(3-p1*a)
        return 0.0*a

def solve_lp(cols, agrid, margin=0.0, grh=False, method='highs', tailpen=0.0):
    A=cols.matrix(agrid); b=K(agrid)-margin
    c=cols.cost + (cols.cost_grh if grh else 0.0) + tailpen
    res=linprog(c, A_ub=A, b_ub=b, bounds=[(0,None)]*cols.n, method=method,
                options=dict(primal_feasibility_tolerance=1e-10, dual_feasibility_tolerance=1e-10))
    return res

def certify(cols, x, ALPHA_MAX, h=1e-4, grh=False, verbose=True):
    """rigorous accounting of the residual (nuhat-K)_+ on [1,ALPHA_MAX] and beyond; returns certified bound."""
    act=np.where(x>1e-13)[0]; xa=x[act]
    ng=int(round((ALPHA_MAX-1)/h))+1; a=1+h*np.arange(ng)
    # evaluate f = nuhat - K on the fine grid in chunks
    f=np.empty(ng)
    for k0 in range(0,ng,200000):
        aa=a[k0:k0+200000]; f[k0:k0+200000]=cols.matrix(aa,act)@xa - K(aa)
    # per-window sup of f_+ including the interpolation correction (h^2/8) sup|f_smooth''|
    total=0.0; rows=[]
    bmax=int(np.ceil(ALPHA_MAX))
    for bwin in range(1,bmax+1):
        lo=max(1.0,bwin-1); hi=min(ALPHA_MAX,bwin+1)
        i0=int(round((lo-1)/h)); i1=int(round((hi-1)/h))
        fw=f[i0:i1+1]; m=max(0.0,fw.max())
        d2=Kpp_bound(lo)+sum(xa[j]*cols.d2_bound(act[j],lo) for j in range(len(act)))   # sup over window (decreasing in a)
        corr=h*h/8*d2
        supw=m+corr if (m>0 or corr>0) else 0.0
        # if f<= -corr everywhere on the window, the interpolation cannot make it positive
        if fw.max()+corr<=0: supw=0.0
        rows.append((bwin,fw.max(),corr,supw)); total+=supw
    # beyond ALPHA_MAX: nuhat_+ <= sum_G 2x e^{-2pi^2 s^2 a^2} (P and T columns are <= 0 there), |K| <= s1 e^{-a}
    tail=0.0
    for bwin in range(bmax+1,bmax+400):
        aa=bwin-1
        amp=sum(xa[j]*2*np.exp(-2*np.pi**2*cols.p2[act[j]]**2*aa**2) for j in range(len(act)) if cols.kind[act[j]]=='G')
        tail+=amp+s1*np.exp(-aa)
    cost=float(cols.cost@x); costg=float(cols.cost_grh@x) if grh else 0.0
    bound=B - cost - (8/3)*(total+tail) + (G_GRH - costg if grh else 0.0)
    if verbose:
        print(f"  LP value (B - cost{' + GRH term' if grh else ''}) = {B-cost+(G_GRH-costg if grh else 0):.9f}")
        print(f"  residual: max f on fine grid = {f.max():.3e}; sum over windows of sup (nuhat-K)_+ = {total:.3e}; beyond {ALPHA_MAX}: {tail:.3e}")
        print(f"  window penalty (8/3)*sum = {(8/3)*(total+tail):.3e}")
        print(f"  CERTIFIED LOWER BOUND W >= {bound:.9f}")
        worst=sorted(rows,key=lambda r:-r[3])[:6]
        print("  worst windows (b, max f, corr, sup):",[(r[0],f"{r[1]:.2e}",f"{r[2]:.2e}",f"{r[3]:.2e}") for r in worst])
    return bound, dict(cost=cost, total=total, tail=tail, fmax=float(f.max()), nact=int(len(act)))

def cutting_planes(cols, a_init, a_check, grh=False, margin=0.0, maxit=25, nadd=3000, tol=2e-8, label="", tailpen=0.0):
    agrid=a_init.copy(); t0=time.time(); res=None
    for it in range(maxit):
        agrid_used=agrid.copy()
        res=solve_lp(cols,agrid,margin=margin,grh=grh,tailpen=tailpen)
        if res.status!=0: print(label,"LP status",res.status,res.message); return None,None
        x=res.x; act=np.where(x>1e-13)[0]
        # violations on the check grid
        worst=[]; vmax=-1e9
        for k0 in range(0,len(a_check),200000):
            aa=a_check[k0:k0+200000]; v=cols.matrix(aa,act)@x[act]-K(aa)+margin
            vmax=max(vmax,v.max()); idx=np.argsort(-v)[:nadd]; worst+=[(v[i],aa[i]) for i in idx if v[i]>tol]
        worst.sort(reverse=True)
        val=B-res.fun if not grh else B+G_GRH-res.fun     # includes the tail penalty
        print(f"{label} it={it} LPvalue(incl. tail pen)={val:.7f} nrows={len(agrid)} nactive={len(act)} maxviol={vmax:.2e} nviol={len(worst)} [{time.time()-t0:.0f}s]",flush=True)
        if vmax<=tol: break
        agrid=np.unique(np.concatenate([agrid,np.array([u for _,u in worst[:nadd]])]))
    return res, agrid_used

# ----------------------------------------------------------------------------------------------------
def validate():
    """Dual of push_D's truncated LP (F=1 beyond A=12, point tests at u_j, constraint on [1,12] only):
       value = B + tailK - sum y_j [1 - sinc^2(u_j)] + 2 sum y_j int_1^A cos(2 pi a u_j) da,  s.t. sum y_j cos(2 pi a u_j) <= K(a) on [1,12].
       This is NOT rigorous for the untruncated class; it only checks normalisations against push_D_lp_gold0.log (0.020696)."""
    A=12.0; tailK=2*(s2*np.exp(-2*A)/2 - s1*np.exp(-A))
    us=np.arange(0.02,40.0001,0.02)
    sinc2=(np.sin(np.pi*us)/(np.pi*us))**2
    cost=(1-sinc2) - (np.sin(2*np.pi*A*us)-np.sin(2*np.pi*us))/(np.pi*us)
    for grh in (False,True):
        costg = 2*np.array([np.sum(w_grh*np.cos(2*np.pi*a_grh*u)*(1.5-a_grh)) for u in us]) if grh else 0.0
        agrid=np.arange(1.0,A+1e-9,0.01); acheck=np.arange(1.0,A+1e-9,0.0005)
        t0=time.time()
        for it in range(30):
            M=np.cos(2*np.pi*np.outer(agrid,us))
            res=linprog(cost+costg, A_ub=M, b_ub=K(agrid), bounds=[(0,None)]*len(us), method='highs',
                        options=dict(primal_feasibility_tolerance=1e-10, dual_feasibility_tolerance=1e-10))
            y=res.x; act=y>1e-13
            v=np.cos(2*np.pi*np.outer(acheck,us[act]))@y[act]-K(acheck)
            val=B+tailK-res.fun+(G_GRH if grh else 0)
            print(f"validate grh={grh} it={it} value={val:.7f} nrows={len(agrid)} nact={act.sum()} maxviol={v.max():.2e} [{time.time()-t0:.0f}s]",flush=True)
            np.save(f"repair_D_validate_y_grh{int(grh)}.npy",np.stack([us[act],y[act]]))
            if v.max()<2e-8: break
            idx=np.argsort(-v)[:2000]; agrid=np.unique(np.concatenate([agrid,acheck[idx[v[idx]>2e-8]]]))
        print(f"validate grh={grh}: dual value {val:.7f}  (push_D primal: {'0.023579' if grh else '0.020696'}); active u's:",np.round(us[act],3)[:40],"...")
        np.save(f"repair_D_validate_y_grh{int(grh)}.npy",np.stack([us[act],y[act]]))

def build(sigmas, umax, ustep, cs=(0.05,0.1,0.15,0.2,0.3,0.4,0.5,0.7,1.0,1.5,2.0), bmax=60):
    cols=Cols()
    us=np.arange(ustep,umax+1e-9,ustep)
    for s in sigmas:
        for u in us: cols.add('G',u,s)
    for c in cs: cols.add('P',c)
    for b in np.arange(1.0,bmax+0.001,0.5): cols.add('T',b,1.0)
    for b in np.arange(1.0,20.001,0.25): cols.add('T',b,0.5)
    cols.finalize(); return cols

def run_certify(grh, sigmas, umax, ustep, ALPHA_MAX=60.0, margin=0.0, tag=""):
    cols=build(sigmas,umax,ustep)
    print(f"columns: {cols.n} (sigmas={sigmas}, u<= {umax} step {ustep}); grh={grh}",flush=True)
    a_init=np.unique(np.concatenate([np.arange(1.0,16.0+1e-9,0.01),np.arange(16.0,ALPHA_MAX+1e-9,0.05)]))
    a_check=np.arange(1.0,ALPHA_MAX+1e-9,0.0005)
    tailpen=cols.tail_penalty(ALPHA_MAX)
    res,agrid=cutting_planes(cols,a_init,a_check,grh=grh,margin=margin,label=f"certify{tag} grh={grh}",tailpen=tailpen)
    if res is None: return
    x=res.x
    bound,info=certify(cols,x,ALPHA_MAX,h=1e-4,grh=grh)
    act=np.where(x>1e-13)[0]
    summ={}
    for kind in ('G','P','T'):
        sel=[k for k in act if cols.kind[k]==kind]
        summ[kind]=dict(n=len(sel),weight=float(sum(x[k] for k in sel)),cost=float(sum(x[k]*cols.cost[k] for k in sel)))
    print("  column usage:",summ)
    bysig={s:float(sum(x[k] for k in act if cols.kind[k]=='G' and abs(cols.p2[k]-s)<1e-12)) for s in sigmas}
    print("  Gaussian weight by sigma:",bysig)
    top=sorted(act,key=lambda k:-x[k])[:15]
    print("  largest columns:",[(cols.kind[k],round(cols.p1[k],3),round(cols.p2[k],3),round(x[k],5)) for k in top])
    out=dict(grh=grh,sigmas=list(sigmas),umax=umax,ustep=ustep,ALPHA_MAX=ALPHA_MAX,bound=bound,info=info,
             active=[(str(cols.kind[k]),float(cols.p1[k]),float(cols.p2[k]),float(x[k])) for k in act])
    json.dump(out,open(f"repair_D_cert_grh{int(grh)}{tag}.json","w"))
    return bound

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='validate': validate()
    elif mode=='certify':
        grh = (len(sys.argv)>2 and sys.argv[2]=='grh')
        sigmas=tuple(float(t) for t in sys.argv[3].split(',')) if len(sys.argv)>3 else (0.03,0.05,0.08)
        umax=float(sys.argv[4]) if len(sys.argv)>4 else 40.0
        ustep=float(sys.argv[5]) if len(sys.argv)>5 else 0.02
        tag=sys.argv[6] if len(sys.argv)>6 else ""
        run_certify(grh,sigmas,umax,ustep,tag=tag)
