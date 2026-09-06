"""The domain-wall local model and its constant C*.
Semi-infinite run (all sites u = 0,-pi,-2pi,...) adjoining the alternating clock (u = pi, 3pi, 5pi, ...):
   q_0(u) = cos(u/2) / Gamma(u/(2 pi))          [zeros: odd multiples of pi, and 0,-2pi,-4pi,...]
Heat flow: q_tau(u) = e^{-tau/4} Re[ e^{iu/2} G_tau(u + i tau) ],  G_tau = e^{tau d^2} (1/Gamma(./2pi)),
and by Hankel's formula 1/Gamma(z) = (1/2 pi i) int_C e^t t^{-z} dt, mode t^{-z} = e^{-z ln t} flows to
e^{tau (ln t)^2/(4 pi^2)} e^{-z ln t}, so
   G_tau(w) = (1/2 pi i) int_C exp( t + tau (ln t)^2/(4pi^2) - (w/2pi) ln t ) dt      (contour: |t|=1 circle + rays).
C* = first tau at which q_tau acquires a double zero (edge pair (0,pi) of the run).
Checks: tau=0 reproduces 1/Gamma; the constant is compared with the lattice extrapolation (push_C_wall_const.py)."""
import mpmath as mp, numpy as np, sys, time
mp.mp.dps=20
def G(w,tau):
    tau=mp.mpf(tau); w=mp.mpc(w)
    def f(t,lnt): return mp.exp(t+tau*lnt**2/(4*mp.pi**2)-(w/(2*mp.pi))*lnt)
    ray=mp.quad(lambda x: f(-x,mp.log(x)-1j*mp.pi)-f(-x,mp.log(x)+1j*mp.pi),[1,4,16,64,mp.inf])
    circ=mp.quad(lambda ph: f(mp.expj(ph),1j*ph)*1j*mp.expj(ph),[-mp.pi,0,mp.pi])
    return (ray+circ)/(2j*mp.pi)
def q(u,tau): return mp.re(mp.expj(u/2)*G(u+1j*tau,tau))*mp.exp(-tau/4)
# check tau=0
for z in [0.3,-1.7,2.5+0.4j]:
    print(f"check 1/Gamma({z}): Hankel {mp.nstr(G(2*mp.pi*z,0),12)}  exact {mp.nstr(1/mp.gamma(z),12)}")
# zero counting on [-3pi, 5pi] and tracking of the edge pair (0,pi)
def zeros(tau,lo=-3*mp.pi,hi=5*mp.pi,n=400):
    xs=[lo+(hi-lo)*i/n for i in range(n+1)]; vs=[q(x,tau) for x in xs]; zs=[]
    for i in range(n):
        if vs[i]*vs[i+1]<0: zs.append(mp.findroot(lambda x:q(x,tau),(xs[i],xs[i+1]),solver='bisect',tol=1e-12))
    return zs
t0=time.time()
for tau in [0,1.0,1.5,2.0,2.05,2.1,2.12,2.15]:
    zs=zeros(tau); print(f"tau={tau}: {len(zs)} zeros in [-3pi,5pi]: {[mp.nstr(z/mp.pi,5) for z in zs]}  [{time.time()-t0:.0f}s]",flush=True)
# refine C*: the edge pair are the two zeros that start at 0 and pi; h(tau)=q at the extremum between them.
def h(tau):
    zs=zeros(tau,lo=-0.5*mp.pi,hi=1.5*mp.pi,n=60)
    # the pair = the two zeros closest to (0,pi) at this tau; there should be exactly 2 zeros in (-pi/2, 3pi/2) before collision
    if len(zs)<2: return -1
    a,b=zs[0],zs[1]
    x=mp.findroot(lambda x: mp.diff(lambda y:q(y,tau),x),(a+b)/2)
    return abs(q(x,tau))
# bracket by zero count then bisection on the count
lo,hi=mp.mpf(2.10),mp.mpf(2.13)
for it in range(22):
    mid=(lo+hi)/2; n=len(zeros(mid,lo=-0.5*mp.pi,hi=1.5*mp.pi,n=80))
    if n>=2: lo=mid
    else: hi=mid
    print(f"  bisect: tau in [{mp.nstr(lo,10)},{mp.nstr(hi,10)}]  (zeros in (-pi/2,3pi/2) at mid: {n})  [{time.time()-t0:.0f}s]",flush=True)
print(f"C* (domain-wall constant, Gamma model) = {mp.nstr((lo+hi)/2,9)}")
