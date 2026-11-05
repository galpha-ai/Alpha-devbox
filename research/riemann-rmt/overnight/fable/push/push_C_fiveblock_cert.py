"""Certificate [C] that the 5-block local model q_tau(u) e^{tau/4} = (u^2-2pi u+2tau-tau^2)cos(u/2) - tau(2u-2pi)sin(u/2)
has only simple zeros for 0<=tau<2 and a double zero at u=0 exactly at tau=2 (first collision = 2).
With v=u-pi: h(v) = (v^2-a^2) sin(v/2) + 2 tau v cos(v/2), a^2 = pi^2-2tau+tau^2, h odd.
For tau on a fine grid in [0,2): locate all zeros of h in [-6pi,6pi], check |h'| at each zero is bounded away from 0,
and check the number of zeros is constant (13). Also print the zero trajectories."""
import mpmath as mp
mp.mp.dps=25
def h(v,tau): a2=mp.pi**2-2*tau+tau**2; return (v*v-a2)*mp.sin(v/2)+2*tau*v*mp.cos(v/2)
def zeros(tau,n=1200):
    lo,hi=-6*mp.pi,6*mp.pi; xs=[lo+(hi-lo)*i/n for i in range(n+1)]; vs=[h(x,tau) for x in xs]; zs=[]
    for i in range(n):
        if vs[i]==0: zs.append(xs[i])
        elif vs[i]*vs[i+1]<0: zs.append(mp.findroot(lambda x:h(x,tau),(xs[i],xs[i+1]),solver='bisect',tol=mp.mpf(10)**-20))
    return zs
minslope=mp.inf; counts=set()
for i in range(0,200):
    tau=mp.mpf(i)/100
    zs=zeros(tau); counts.add(len(zs))
    sl=min(abs(mp.diff(lambda x:h(x,tau),z)) for z in zs); minslope=min(minslope,sl)
    if i%25==0: print(f"tau={mp.nstr(tau,4)}: {len(zs)} zeros in [-6pi,6pi]; zeros/pi near the block: {[mp.nstr(z/mp.pi,5) for z in zs if abs(z)<3.2*mp.pi]}; min|h'|={mp.nstr(sl,5)}")
print("zero counts seen for tau in [0,2):",counts,"; min |h'| over all zeros and tau in [0,1.99]:",mp.nstr(minslope,6))
for tau in [1.99,1.999,2.0]:
    zs=zeros(mp.mpf(tau)); print(f"tau={tau}: zeros/pi near the edge u=0 (v=-pi): {[mp.nstr(z/mp.pi,7) for z in zs if -1.6*mp.pi<z<-0.4*mp.pi]}")
print("at tau=2: h(-pi) =",mp.nstr(h(-mp.pi,mp.mpf(2)),5)," h'(-pi) =",mp.nstr(mp.diff(lambda x:h(x,mp.mpf(2)),-mp.pi),5), " h''(-pi) =",mp.nstr(mp.diff(lambda x:h(x,mp.mpf(2)),-mp.pi,2),5))
