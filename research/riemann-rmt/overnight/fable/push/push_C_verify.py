"""Task C: independent high-precision verification of N^2 D for given gap patterns.
Method A (ground truth): mpmath polyroots of P_s at dps digits; off-circle indicator
  off(s)=max_j | |z_j(s)|-1 |, and min pairwise root distance; scanned on a tau-grid to check that
  the on-circle set is an interval, then bisection on off(s)>tol.
Method B: moving-bracket extremum tracker (fixes the fixed-initial-bracket flaw of heat_depth*.py):
  track all zeros x_j(s) of Q_s by Newton continuation, and the critical point between each
  consecutive pair; collision = first s where Q_s at a critical point changes sign.
Usage: python push_C_verify.py "1,1,1,1,1,1,1,2,2,9,2,2" [dps] [scan]"""
import mpmath as mp, numpy as np, sys, time

def coeffs(gaps):
    N=len(gaps); M=2*N; sites=np.concatenate([[0],np.cumsum(gaps)[:-1]])
    roots=[mp.expjpi(mp.mpf(2*int(sv))/M) for sv in sites]
    a=[mp.mpc(1)]
    for r in roots:
        new=[mp.mpc(0)]*(len(a)+1)
        for k,c in enumerate(a): new[k+1]+=c; new[k]-=c*r
        a=new
    return a   # a[j] coefficient of z^j, monic

def roots_at(a,s,N):
    c=[a[j]*mp.exp(s*j*(N-j)) for j in range(N+1)]
    return mp.polyroots(c[::-1],maxsteps=200,extraprec=mp.mp.prec)

def off_and_mind(a,s,N):
    r=roots_at(a,s,N)
    off=max(abs(abs(z)-1) for z in r)
    mind=min(abs(r[i]-r[j]) for i in range(N) for j in range(i+1,N))
    return off,mind,r

def methodA(gaps,dps=50,tol=None,scan=True,tau_max=2.6,ntau=53):
    mp.mp.dps=dps; N=len(gaps); a=coeffs(gaps); tol=tol or mp.mpf(10)**(-dps//2)
    Nm=mp.mpf(N)
    if scan:
        print("  tau      off(s)        min|z_i-z_j|")
        for t in np.linspace(0,tau_max,ntau):
            off,mind,_=off_and_mind(a,mp.mpf(t)/Nm**2,N)
            print(f"  {t:6.3f}  {mp.nstr(off,5):>12s}  {mp.nstr(mind,8)}")
    # bracket: first grid tau with off>tol
    lo=mp.mpf(0); hi=None; t=mp.mpf('0.05')
    while True:
        off,_,_=off_and_mind(a,t/Nm**2,N)
        if off>tol: hi=t; break
        lo=t; t+=mp.mpf('0.05')
    for _ in range(300):
        mid=(lo+hi)/2
        off,_,_=off_and_mind(a,mid/Nm**2,N)
        if off>tol: hi=mid
        else: lo=mid
        if hi-lo<mp.mpf(10)**(-(dps//2-4))*hi: break
    tau=(lo+hi)/2
    # identify colliding pair at hi
    _,_,r=off_and_mind(a,hi/Nm**2,N)
    ang=sorted([mp.arg(z)%(2*mp.pi) for z in r]); 
    return tau,ang

class Tracker:
    """Q_s(x)=Re sum_m c_m e^{i m x} e^{s(N^2/4-m^2)}; zeros tracked by Newton with moving brackets."""
    def __init__(self,gaps,dps=40):
        mp.mp.dps=dps; N=len(gaps); self.N=N; M=2*N
        sites=np.concatenate([[0],np.cumsum(gaps)[:-1]]); theta=[2*mp.pi*int(sv)/M for sv in sites]
        coef=[mp.mpc(1)]
        for t in theta:
            r=mp.expj(t); new=[mp.mpc(0)]*(len(coef)+1)
            for k,c in enumerate(coef): new[k+1]+=c; new[k]-=c*r
            coef=new
        pref=mp.expj(-sum(theta)/2)/(2j)**N
        self.m=[mp.mpf(k)-mp.mpf(N)/2 for k in range(N+1)]
        self.c=[pref*coef[k] for k in range(N+1)]
        self.w=[mp.mpf(N)**2/4-mm**2 for mm in self.m]
        self.theta=theta
    def Q(self,x,s,d=0):
        tot=mp.mpc(0)
        for c,mm,w in zip(self.c,self.m,self.w):
            f=c*mp.exp(s*w)*mp.expj(mm*x)
            if d==1: f*=1j*mm
            elif d==2: f*=-(mm**2)
            tot+=f
        return mp.re(tot)
    def newton(self,x,s,d,lo,hi,it=80):
        # find zero of Q^{(d)} near x, staying in (lo,hi); return None if it escapes
        for _ in range(it):
            f=self.Q(x,s,d); fp=self.Q(x,s,d+1)
            if fp==0: return None
            dx=-f/fp; x=x+dx
            if not (lo<x<hi): return None
            if abs(dx)<mp.mpf(10)**(-mp.mp.dps+6): break
        return x
    def state_at(self,s,zeros):
        """update zeros at time s by Newton (bracketed by midpoints with neighbours); return zeros, and
        the extremum values h_i = sign * Q_s(critical point between zeros i,i+1); None if failure."""
        N=self.N; z=list(zeros)
        newz=[]
        for i in range(N):
            lo=(z[i-1]+z[i])/2 if i>0 else (z[N-1]-2*mp.pi+z[0])/2
            hi=(z[i]+z[i+1])/2 if i<N-1 else (z[N-1]+z[0]+2*mp.pi)/2
            x=self.newton(z[i],s,0,lo,hi)
            if x is None: return None,None
            newz.append(x)
        return newz,None
    def depth(self,ds_frac=0.01,tau_max=6,verbose=False):
        """continuation in s; at each step verify all N zeros still tracked, and compute for each
        consecutive pair the extremum value h_i; the first pair whose h_i would cross 0 gives D."""
        N=self.N; s=mp.mpf(0); ds=mp.mpf(ds_frac)/N**2
        zeros=list(self.theta)
        # signs of Q_0 at the midpoints
        mids=[(zeros[i]+(zeros[i+1] if i<N-1 else zeros[0]+2*mp.pi))/2 for i in range(N)]
        sg=[mp.sign(self.Q(x,mp.mpf(0))) for x in mids]
        def hvals(s,zeros):
            hs=[]
            for i in range(N):
                a=zeros[i]; b=zeros[i+1] if i<N-1 else zeros[0]+2*mp.pi
                x=self.newton((a+b)/2,s,1,a,b)
                if x is None: return None
                hs.append(self.Q(x,s)*sg[i])
            return hs
        h_prev=hvals(s,zeros); assert h_prev is not None and min(h_prev)>0
        while s<tau_max/N**2:
            s2=s+ds
            z2,_=self.state_at(s2,zeros)
            h2=hvals(s2,z2) if z2 is not None else None
            if z2 is None or h2 is None or min(h2)<=0: break
            s,zeros,h_prev=s2,z2,h2
        # bisection between s and s2 using the tracked state at s as the starting point
        lo,hi=s,s2
        for _ in range(200):
            mid=(lo+hi)/2
            zm,_=self.state_at(mid,zeros)
            hm=hvals(mid,zm) if zm is not None else None
            if zm is not None and hm is not None and min(hm)>0: lo=mid; zeros=zm
            else: hi=mid
            if hi-lo<mp.mpf(10)**(-(mp.mp.dps//2))*hi: break
        # colliding pair = argmin h at lo
        hl=hvals(lo,zeros); i=int(np.argmin([float(x) for x in hl]))
        return (lo+hi)/2, i, zeros

if __name__=="__main__":
    gaps=[int(x) for x in sys.argv[1].split(',')]; dps=int(sys.argv[2]) if len(sys.argv)>2 else 50
    scan=(sys.argv[3]=='scan') if len(sys.argv)>3 else True
    N=len(gaps); assert sum(gaps)==2*N
    t0=time.time(); tau,ang=methodA(gaps,dps=dps,scan=scan)
    print(f"Method A (polyroots, dps={dps}): N={N} gaps={gaps}  N^2 D = {mp.nstr(tau,20)}   [{time.time()-t0:.1f}s]")
    print("  root angles just after collision (units pi/N):", [mp.nstr(x*N/mp.pi,6) for x in ang])
    t0=time.time(); T=Tracker(gaps,dps=min(dps,40)); d,i,z=T.depth()
    print(f"Method B (moving-bracket tracker): N^2 D = {mp.nstr(N*N*d,20)}  colliding pair index {i} (zeros {mp.nstr(z[i]*N/mp.pi,6)},{mp.nstr(z[(i+1)%N]*N/mp.pi,6)} in units pi/N)   [{time.time()-t0:.1f}s]")
