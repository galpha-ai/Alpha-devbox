"""Exact checks for the symmetric 3-block families (push_A).

Families (units pi/N on Z/2N; alternating clock = odd sites = roots of z^N+1):
  block4odd : N odd,  P(z) = (z^N+1)(z-1)/(z+1)            gaps [1,1,2,..,2,4,2,..,2], 4-gap centred at angle pi
  block4even: N even, P(z) = (z^N+1)(z-1)/(z+w), w=e^{i pi/N} gaps [1,1,2,..,2,4,2,..,2]  (asymmetric: removed site N+1)
  block33   : N even, P(z) = (z^N+1)(z^2-1)/(z^2+2cos(pi/N)z+1) gaps [1,1,2,..,3,3,..,2]  (symmetric)

Checks:
 (1) closed form of Q_0(x)=prod sin((x-theta_j)/2) against the product;
 (2) coefficients a_j of P(z) against numpy.poly;
 (3) for the symmetric families, D = first zero of F_N(s) = P_s'(1) = sum_j j a_j e^{s j (N-j)}
     against the enumeration files (N<=12) and heat_depth.py;
 (4) high-precision tau_N = N^2 D_N for N up to 4096 via mpmath, and the fit tau_N = 2 - 4/(3N^2) + c2/N^4.
"""
import numpy as np, mpmath as mp, sys, time

def theta_from_gaps(g):
    N=len(g); sites=np.concatenate([[0],np.cumsum(g)[:-1]]); return 2*np.pi*sites/(2*N)

def gaps(name,N):
    if name=='block4odd':
        assert N%2==1; k=(N-3)//2; return [1,1]+[2]*k+[4]+[2]*(N-3-k)
    if name=='block4even':
        assert N%2==0; k=(N-4)//2; return [1,1]+[2]*k+[4]+[2]*(N-3-k)
    if name=='block33':
        assert N%2==0; k=(N-4)//2; return [1,1]+[2]*k+[3,3]+[2]*(N-4-k)
    raise ValueError

def coeffs_exact(name,N):
    """a_0..a_N (increasing powers) of P(z), from the closed forms."""
    j=np.arange(N+1)
    if name=='block4odd':
        a=-2.0*(-1.0)**j; a[0]=-1.0; a[N]=1.0
        return a.astype(complex)
    if name=='block4even':
        # gap-list convention: removed site is N-1, i.e. root -conj(w); P(z)=(z^N+1)(z-1)/(z+conj(w))
        w=np.exp(1j*np.pi/N); wb=np.conj(w)
        a=np.zeros(N+1,complex)
        a[N]=1; a[0]=-w
        jj=np.arange(1,N)
        a[1:N]=-(1+wb)*(-1.0)**jj*np.exp(1j*np.pi*(jj+1)/N)
        return a
    if name=='block33':
        s=np.sin(np.pi/N); k=np.arange(N-1)
        r=np.zeros(N+1); r[:N-1]=(-1.0)**k*np.sin((k+1)*np.pi/N)/s   # R(z)=(z^N+1)/(z^2+2cz+1), deg N-2
        a=np.zeros(N+1)
        a[2:]+=r[:N-1]; a-=r                                          # P=(z^2-1)R
        return a.astype(complex)
    raise ValueError

def Q0_closed(name,N,x):
    if name=='block4odd':  return 2.0**(1-N)*np.cos(N*x/2)*np.tan(x/2)
    if name=='block4even': return -2.0**(1-N)*np.cos(N*x/2)*np.sin(x/2)/np.cos((x+np.pi/N)/2)   # removed root at angle pi-pi/N
    if name=='block33':    return -2.0**(1-N)*np.cos(N*x/2)*np.sin(x/2)*np.cos(x/2)/(np.cos((x-np.pi/N)/2)*np.cos((x+np.pi/N)/2))

def check_closed_forms():
    print("== (1),(2): closed forms of Q_0 and of the coefficients")
    for name,N in [('block4odd',7),('block4odd',11),('block4even',8),('block4even',12),('block33',8),('block33',12)]:
        th=theta_from_gaps(gaps(name,N))-np.pi/N
        # gap list starts at site 0 with the block on sites 0,1,2: the added root is site 1 -> rotate by -pi/N
        x=np.linspace(0.05,2*np.pi-0.05,997)
        Qp=np.ones_like(x)
        for t in th: Qp*=np.sin((x-t)/2)
        Qc=Q0_closed(name,N,x)
        e1=min(np.max(np.abs(Qp-Qc)),np.max(np.abs(Qp+Qc)))/np.max(np.abs(Qp))   # prod sin((x-th)/2) is defined up to sign (th mod 2pi)
        z=np.exp(1j*th); a_np=np.poly(z)[::-1]      # increasing powers (roots rotated so added root = 1)
        a_ex=coeffs_exact(name,N)
        e2=np.max(np.abs(a_np-a_ex))
        print(f"  {name:10s} N={N:3d}  rel.err Q0 = {e1:.2e}   max|a_j - a_j^exact| = {e2:.2e}")

def F_of_s(a,N,s):
    j=np.arange(N+1); return np.real(np.sum(j*a*np.exp(s*j*(N-j))))

def depth_symmetric_float(name,N):
    """first zero of F_N(s)=P_s'(1), double precision, bisection on sign change (F_N(0)=P'(1) != 0)."""
    a=coeffs_exact(name,N)
    s0=0.0; f0=F_of_s(a,N,0.0); ds=0.01/N**2; s=ds
    while np.sign(F_of_s(a,N,s))==np.sign(f0): s+=ds
    lo,hi=s-ds,s
    for _ in range(100):
        mid=0.5*(lo+hi)
        if np.sign(F_of_s(a,N,mid))==np.sign(f0): lo=mid
        else: hi=mid
        if hi-lo<1e-16*hi: break
    return 0.5*(lo+hi)

def depth_symmetric_mp(name,N,dps=40):
    """tau_N = N^2 D_N to high precision for the symmetric families, using the m-form
       F(tau) = sum_{m} m c_m e^{-tau m^2/N^2}  (m = j - N/2), c_m = a_{m+N/2}."""
    mp.mp.dps=dps
    Nm=mp.mpf(N)
    if name=='block4odd':
        # F(s) = N - 2 sum_{j=1}^{N-1} (-1)^j j e^{s j(N-j)};  divide by e^{sN^2/4}
        def F(tau):
            s=tau/Nm**2
            acc=mp.mpf(N)*mp.exp(-tau/4)
            for j in range(1,N):
                m=mp.mpf(j)-Nm/2
                acc-=2*(-1)**j*j*mp.exp(-tau*m*m/Nm**2)
            return acc
    elif name=='block33':
        sN=mp.sin(mp.pi/Nm)
        r=[(-1)**k*mp.sin((k+1)*mp.pi/Nm)/sN for k in range(N-1)]+[mp.mpf(0),mp.mpf(0)]
        a=[(r[j-2] if j>=2 else mp.mpf(0))-r[j] for j in range(N+1)]
        def F(tau):
            acc=mp.mpf(0)
            for j in range(N+1):
                if a[j]==0: continue
                m=mp.mpf(j)-Nm/2
                acc+=j*a[j]*mp.exp(-tau*m*m/Nm**2)
            return acc
    else: raise ValueError
    # first zero in tau: scan then findroot
    f0=F(mp.mpf(0)); t=mp.mpf('0.05'); h=mp.mpf('0.05')
    while mp.sign(F(t))==mp.sign(f0): t+=h
    return mp.findroot(F,(t-h,t),solver='anderson')

if __name__=="__main__":
    check_closed_forms()
    print("== (3): D from first zero of P_s'(1) vs enumeration files (N<=12)")
    for N in [6,8,10,12]:
        d=np.load(f'acue_depth_N{N}.npz'); G=d['gaps']; D=d['D']
        def find(pat):
            for i,g in enumerate(G):
                g=list(g)
                for r in range(N):
                    if g[r:]+g[:r]==pat: return i
        i=find(gaps('block33',N)); Denum=N*N*D[i]
        Dex=N*N*depth_symmetric_float('block33',N)
        print(f"  block33 N={N:2d}: enumeration N^2D={Denum:.10f}  exact-F zero N^2D={Dex:.10f}  diff={Denum-Dex:.1e}")
    for N in [5,7,9,11]:
        d=np.load(f'acue_depth_N{N}.npz'); G=d['gaps']; D=d['D']
        def find(pat):
            for i,g in enumerate(G):
                g=list(g)
                for r in range(N):
                    if g[r:]+g[:r]==pat: return i
        i=find(gaps('block4odd',N)); Denum=N*N*D[i]
        Dex=N*N*depth_symmetric_float('block4odd',N)
        print(f"  block4odd N={N:2d}: enumeration N^2D={Denum:.10f}  exact-F zero N^2D={Dex:.10f}  diff={Denum-Dex:.1e}")
    print("== (3b): vs heat_depth.py (independent solver) at N=32,33,64,65")
    from heat_depth import HeatDepth
    for name,N in [('block33',32),('block4odd',33),('block33',64),('block4odd',65)]:
        H=HeatDepth(theta_from_gaps(gaps(name,N))); dh,i=H.depth(pairs=[0,N-1]);
        print(f"  {name:10s} N={N:3d}: heat_depth N^2D={N*N*dh:.12f}  exact-F N^2D={N*N*depth_symmetric_float(name,N):.12f}")
    print("== (4): high precision tau_N and the expansion 2 - 4/(3N^2) + c2/N^4")
    for name in ['block33','block4odd']:
        print(" ",name)
        rows=[]
        Ns=[16,32,64,128,256,512,1024,2048] if name=='block33' else [17,33,65,129,257,513,1025,2049]
        for N in Ns:
            t0=time.time(); tau=depth_symmetric_mp(name,N,dps=30)
            c1=(tau-2)*N**2; c2=((tau-2)*N**2+mp.mpf(4)/3)*N**2
            rows.append((N,tau,c1,c2))
            print(f"    N={N:5d}  tau_N={mp.nstr(tau,18)}  N^2(tau-2)={mp.nstr(c1,12)}  N^4(tau-2+4/(3N^2))={mp.nstr(c2,10)}   [{time.time()-t0:.1f}s]",flush=True)
