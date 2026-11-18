"""Local-model depth for midpoint-insertion defects in the infinite alternating lattice.
Lattice zeros at odd multiples of pi (cos(u/2)); inserted roots a_i (even multiples of pi).
q_tau(u) = e^{-tau/4} Re[ e^{iu/2} P_tau(u + i tau) ],  P_tau = e^{tau d^2} p,  p(u)=prod(u-a_i).
Collision time tau* = first tau with a double zero; found by tracking the extremum of q between
consecutive zeros (continuation + bisection). Zeros initially: a_i and odd multiples of pi."""
import mpmath as mp
mp.mp.dps=30
def heat_poly(p_coeffs, tau):
    # p = sum c_k u^k ; e^{tau d^2} p = sum_k c_k sum_j tau^j/j! * (k)_(2j) u^{k-2j}
    n=len(p_coeffs)-1; out=[mp.mpf(0)]*(n+1)
    for k,c in enumerate(p_coeffs):
        if c==0: continue
        j=0
        while k-2*j>=0:
            coef=c*tau**j/mp.factorial(j)*mp.ff(k,2*j)
            out[k-2*j]+=coef; j+=1
    return out
def q(u,tau,p,d=0):
    P=heat_poly(p,tau); z=u+1j*tau
    val=sum(c*z**k for k,c in enumerate(P))
    f=lambda uu: mp.re(mp.expj(uu/2)*sum(c*(uu+1j*tau)**k for k,c in enumerate(P)))
    if d==0: return f(u)
    return mp.diff(f,u,d)
def tau_star(added, tau_max=6, ds=0.02):
    # polynomial with roots at added points
    p=[mp.mpf(1)]
    for a in added:
        new=[mp.mpf(0)]*(len(p)+1)
        for k,c in enumerate(p): new[k+1]+=c; new[k]-=c*a
        p=new
    zeros=sorted(list(added)+[m*mp.pi for m in range(-2*len(added)-5, 2*len(added)+6, 2) if m%2])  # odd multiples
    zeros=sorted(set(zeros))
    best=(mp.inf,None)
    for i in range(len(zeros)-1):
        a,b=zeros[i],zeros[i+1]
        if b-a>3*mp.pi: continue
        x0=(a+b)/2; sg=mp.sign(q(x0,mp.mpf(0),p))
        st={'x':x0}
        def good(t):
            x=st['x']
            for _ in range(60):
                d1=q(x,t,p,1); d2=q(x,t,p,2)
                if d2==0: return False
                dx=-d1/d2; x=x+dx
                if not (a<x<b): return False
                if abs(dx)<mp.mpf(10)**-20: break
            if mp.sign(q(x,t,p,2))==sg: return False
            if q(x,t,p)*sg<=0: return False
            st['x']=x; return True
        t=mp.mpf(0)
        if not good(t): continue
        ok=True
        while t<tau_max:
            t2=t+ds
            if not good(t2): ok=False; break
            t=t2
        if not ok:
            lo,hi=t,t2
            for _ in range(80):
                mid=(lo+hi)/2
                if good(mid): lo=mid
                else: hi=mid
                if hi-lo<mp.mpf(10)**-18: break
            tt=(lo+hi)/2
            if tt<best[0]: best=(tt,(mp.nstr(a,5),mp.nstr(b,5)))
    return best
if __name__=="__main__":
    for k in range(1,7):
        added=[2*m*mp.pi for m in range(-(k-1)//2, (k-1)//2+1)] if k%2 else [(2*m+1)*mp.pi for m in range(-k//2,k//2)]
        # k odd: added at 0, ±2pi,... (block length 2k+1 centred at inserted root); k even: use shifted lattice? keep simple: only odd k
        if k%2==0: added=[2*m*mp.pi for m in range(-k//2+1, k//2+1)]  # k consecutive even multiples: -.., 0, 2pi.. (asymmetric)
        ts,pair=tau_star(added)
        print(f"k={k} inserted={[mp.nstr(a/mp.pi,3)+'pi' for a in added]}  block length {2*k+1}: tau*={mp.nstr(ts,15)} colliding pair {pair}", flush=True)
