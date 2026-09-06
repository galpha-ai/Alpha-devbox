"""High-N depth solver for circle-rooted configurations via the scalar heat flow.
Q_0(x)=prod_j sin((x-theta_j)/2) has Fourier modes m=j-N/2 (half-integers if N odd); the
coefficient flow P_s multiplies mode m by exp(s(N^2/4-m^2)). Collision = first s at which
Q_s acquires a double zero = the local extremum of Q_s between the two merging zeros crosses 0.
We track the extremum between the zeros at theta[i] and theta[i+1] (pair index i) by Newton
on Q_s', and solve h(s)=Q_s(x_ext(s))=0 by Brent/bisection. Also returns the pair.
"""
import numpy as np
from scipy.optimize import brentq

class HeatDepth:
    def __init__(self, theta, K=None):
        theta=np.asarray(theta,float); self.theta=np.sort(theta % (2*np.pi)); N=len(theta); self.N=N
        # Q_0 on a grid of size 2K >= 2N+2 points on [0,4pi) (period 4pi if N odd), use period 4pi always
        K = K or max(4*N, 64)
        x=np.arange(2*K)*(4*np.pi/(2*K))
        Q=np.ones_like(x)
        for t in self.theta: Q*=np.sin((x-t)/2)
        c=np.fft.fft(Q)/(2*K)                # Q(x)=sum_k c_k e^{i k x/2}, k integer (half-integer modes in x)
        k=np.fft.fftfreq(2*K,1/(2*K))       # integer k; mode m=k/2
        keep=np.abs(k)<=N+1
        self.k=k[keep]; self.c=c[keep]; self.m=self.k/2
        self.w=N*N/4-self.m**2
    def Qs(self,x,s,deriv=0):
        ph=np.exp(1j*np.outer(np.atleast_1d(x),self.m))*np.exp(s*self.w)
        if deriv==1: ph=ph*(1j*self.m)
        if deriv==2: ph=ph*(-(self.m**2))
        return np.real(ph@self.c)
    def extremum(self,s,x0):
        x=x0
        for _ in range(60):
            d1=self.Qs(x,s,1)[0]; d2=self.Qs(x,s,2)[0]
            dx=-d1/d2; x=x+dx
            if abs(dx)<1e-15: break
        return x
    def depth_pair(self,i):
        th=self.theta; N=self.N
        a=th[i]; b=th[(i+1)%N] + (2*np.pi if i==N-1 else 0)
        x0=0.5*(a+b); sg=np.sign(self.Qs(x0,0.0)[0])
        state={'x':x0}
        def good(s):
            # returns (ok, h): ok=False once the extremum between a,b has vanished or crossed zero
            x=state['x']
            for _ in range(80):
                d1=self.Qs(x,s,1)[0]; d2=self.Qs(x,s,2)[0]
                if d2==0 or not np.isfinite(d2): return False,0.0
                dx=-d1/d2; x=x+dx
                if not (a<x<b): return False,0.0
                if abs(dx)<1e-15: break
            d2=self.Qs(x,s,2)[0]
            if np.sign(d2)==sg: return False,0.0      # wrong curvature: extremum lost
            h=self.Qs(x,s)[0]*sg
            if h<=0: return False,h
            state['x']=x; return True,h
        s=0.0; ds=0.02/N**2; ok,_=good(0.0)
        assert ok
        while True:
            s2=s+ds; ok,_=good(s2)
            if not ok: break
            s=s2
        lo,hi=s,s2
        for _ in range(200):
            mid=0.5*(lo+hi)
            ok,_=good(mid)
            if ok: lo=mid
            else: hi=mid
            if hi-lo<1e-15*hi: break
        return 0.5*(lo+hi)

    def depth(self,pairs=None):
        pairs = range(self.N) if pairs is None else pairs
        best=(np.inf,None)
        for i in pairs:
            try: d=self.depth_pair(i)
            except Exception: continue
            if d<best[0]: best=(d,i)
        return best

def gaps_to_theta(g):
    N=len(g); sites=np.concatenate([[0],np.cumsum(g)[:-1]]); return 2*np.pi*sites/(2*N)

if __name__=="__main__":
    import sys
    # sanity vs the bisection solver at small N
    for g in ([3,1,2,2,2,2],[1,1,2,3,3,2],[1,1,2,2,3,3,2,2]):
        H=HeatDepth(gaps_to_theta(g)); N=len(g)
        d,i=H.depth(pairs=[0,1,N-1]); print(g, "N^2D=",N*N*d, "pair",i)
