"""Robust depth solver built on heat_depth.HeatDepth's exact Fourier representation of Q_s.

heat_depth.HeatDepth.depth_pair rejects the tracked extremum as soon as it leaves the *initial*
interval (theta_i, theta_{i+1}); for defects whose roots drift (e.g. the outer gap of a 7-block, whose
two roots both move towards the block centre) this fires long before the collision and returns a
spurious, too small, depth (block7: 1.843 instead of 2.038).  Here the pair's zeros are tracked
themselves (grid scan + bisection in x at each s) and the extremum is bracketed by the *current*
zeros.  D = first s at which the number of real zeros of Q_s in the window drops.

window: (x_lo, x_hi) in radians, must contain the colliding pair and no zero on its boundary
        for s in [0, D]; pass None to use the whole circle [0, 2pi).
"""
import numpy as np
from heat_depth import HeatDepth, gaps_to_theta

def zeros_in_window(H, s, xlo, xhi, M):
    xs=np.linspace(xlo,xhi,M+1); v=H.Qs(xs,s)
    idx=np.where(v[:-1]*v[1:]<0)[0]
    zs=[]
    for i in idx:
        a,b=xs[i],xs[i+1]; fa=v[i]
        for _ in range(50):
            m=0.5*(a+b); fm=H.Qs(np.array([m]),s)[0]
            if fm==0: a=b=m; break
            if np.sign(fm)==np.sign(fa): a,fa=m,fm
            else: b=m
        zs.append(0.5*(a+b))
    return np.array(zs)

def depth_robust(H, window=None, pts_per_gap=64, dtau=0.02, verbose=False):
    N=H.N
    xlo,xhi=(0.0,2*np.pi) if window is None else window
    M=int(pts_per_gap*(xhi-xlo)/(np.pi/N))+1
    z0=zeros_in_window(H,0.0,xlo,xhi,M); n0=len(z0)
    ds=dtau/N**2; s=0.0; zs=z0
    while True:
        s2=s+ds; z2=zeros_in_window(H,s2,xlo,xhi,M)
        if len(z2)<n0: break
        s,zs=s2,z2
        if s>20.0/N**2: raise RuntimeError("no collision found before tau=20")
    # closest adjacent pair at s (last good time)
    g=np.diff(zs); i=int(np.argmin(g)); a,b=zs[i],zs[i+1]
    x0=0.5*(a+b); sg=np.sign(H.Qs(np.array([x0]),s)[0])
    state={'x':x0,'a':a,'b':b}
    def good(t):
        x=state['x']; a,b=state['a'],state['b']; w=max(b-a,0.25*np.pi/N)   # never reject on a sub-quarter-gap bracket
        for _ in range(80):
            d1=H.Qs(np.array([x]),t,1)[0]; d2=H.Qs(np.array([x]),t,2)[0]
            if d2==0 or not np.isfinite(d2): return False
            dx=-d1/d2; x+=dx
            if not (a-w<x<b+w): return False
            if abs(dx)<1e-15: break
        d2=H.Qs(np.array([x]),t,2)[0]
        if np.sign(d2)==sg: return False
        h=H.Qs(np.array([x]),t)[0]*sg
        if h<=0: return False
        # update bracket to the current zeros around x (keep the old bracket if they are below grid resolution)
        zz=zeros_in_window(H,t,max(xlo,x-2*w),min(xhi,x+2*w),256)
        left=zz[zz<x]; right=zz[zz>x]
        state['x']=x
        if len(left) and len(right): state['a']=left.max(); state['b']=right.min()
        return True
    lo,hi=s,s2
    assert good(lo)
    for _ in range(200):
        mid=0.5*(lo+hi)
        if good(mid): lo=mid
        else: hi=mid
        if hi-lo<1e-14*hi: break
    if verbose: print(f"  collision of pair at x=({state['a']:.6f},{state['b']:.6f}), extremum x={state['x']:.6f}")
    return 0.5*(lo+hi)

if __name__=="__main__":
    import sys, time
    def fam(name,N):
        if name=='block7': k=(N-7)//2; g=[1]*6+[2]*k+[8]+[2]*(N-7-k)
        elif name=='block5': k=(N-5)//2; g=[1,1,1,1]+[2]*k+[6]+[2]*(N-5-k)
        elif name=='two3': k=(N-6)//2; g=[1,1,2,1,1]+[2]*k+[6]+[2]*(N-6-k)
        elif name=='block33': k=(N-4)//2; g=[1,1]+[2]*k+[3,3]+[2]*(N-4-k)
        elif name=='block9': k=(N-9)//2; g=[1]*8+[2]*k+[10]+[2]*(N-9-k)
        elif name=='block11': k=(N-11)//2; g=[1]*10+[2]*k+[12]+[2]*(N-11-k)
        assert sum(g)==2*N and len(g)==N
        return g
    name=sys.argv[1]; Ns=[int(x) for x in sys.argv[2:]] or [16,24,32,48,64,96,128]
    print("==",name,"(robust solver)",flush=True)
    for N in Ns:
        t0=time.time(); g=fam(name,N); H=HeatDepth(gaps_to_theta(g))
        nb=len([x for x in g if x==1])+1           # block sites 0..nb-1
        win=(-3*np.pi/N, (nb+2)*np.pi/N)            # block plus 1.5 lattice gaps on each side (mod 2pi handled by Qs periodicity)
        d=depth_robust(H,window=win,verbose=True)
        print(f"N={N:4d}  N^2D={N*N*d:.12f}  t={time.time()-t0:.1f}s",flush=True)
