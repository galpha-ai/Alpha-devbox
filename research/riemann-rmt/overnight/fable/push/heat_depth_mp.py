"""mpmath version of heat_depth.py for configurations with long runs (severe cancellation).
Q_0(x)=prod sin((x-theta_j)/2) = sum_m c_m e^{i m x}, m in j-N/2; coefficients from the exact
polynomial product; flow multiplies mode m by exp(s(N^2/4-m^2)). Depth of pair i = first s with
the extremum of Q_s between theta_i,theta_{i+1} crossing zero (continuation + bisection)."""
import mpmath as mp, numpy as np

class HeatDepthMP:
    def __init__(self, theta, dps=60):
        mp.mp.dps=dps; self.dps=dps
        theta=sorted([mp.mpf(t) for t in theta]); self.theta=theta; N=len(theta); self.N=N
        # prod_j sin((x-t_j)/2) = prod_j (e^{i(x-t_j)/2} - e^{-i(x-t_j)/2})/(2i)
        # = (2i)^{-N} e^{-iNx/2} prod_j (e^{ix} - e^{i t_j}) e^{-i t_j/2}
        coef=[mp.mpc(1)]
        for t in theta:
            r=mp.expj(t); new=[mp.mpc(0)]*(len(coef)+1)
            for k,c in enumerate(coef):
                new[k+1]+=c; new[k]-=c*r
            coef=new                     # coef[k] = coefficient of e^{ikx}
        pref=mp.expj(-sum(theta)/2)/(2j)**N
        self.m=[mp.mpf(k)-mp.mpf(N)/2 for k in range(N+1)]
        self.c=[pref*coef[k] for k in range(N+1)]
        self.w=[mp.mpf(N)**2/4-mm**2 for mm in self.m]
    def Q(self,x,s,d=0):
        tot=mp.mpc(0)
        for c,mm,w in zip(self.c,self.m,self.w):
            f=c*mp.exp(s*w)*mp.expj(mm*x)
            if d==1: f*=1j*mm
            elif d==2: f*=-(mm**2)
            tot+=f
        return mp.re(tot)
    def depth_pair(self,i,ds_frac=0.02):
        th=self.theta; N=self.N
        a=th[i]; b=th[(i+1)%N]+(2*mp.pi if i==N-1 else 0)
        x0=(a+b)/2; sg=mp.sign(self.Q(x0,0))
        state={'x':x0}
        def good(s):
            x=state['x']
            for _ in range(100):
                d1=self.Q(x,s,1); d2=self.Q(x,s,2)
                if d2==0: return False
                dx=-d1/d2; x=x+dx
                if not (a<x<b): return False
                if abs(dx)<mp.mpf(10)**(-self.dps+8): break
            if mp.sign(self.Q(x,s,2))==sg: return False
            if self.Q(x,s)*sg<=0: return False
            state['x']=x; return True
        s=mp.mpf(0); ds=mp.mpf(ds_frac)/N**2
        assert good(s)
        while True:
            s2=s+ds
            if not good(s2): break
            s=s2
        lo,hi=s,s2
        for _ in range(200):
            mid=(lo+hi)/2
            if good(mid): lo=mid
            else: hi=mid
            if hi-lo<mp.mpf(10)**(-min(self.dps-10,30))*hi: break
        return (lo+hi)/2
    def depth(self,pairs):
        best=(mp.inf,None)
        for i in pairs:
            try: d=self.depth_pair(i)
            except Exception as e: continue
            if d<best[0]: best=(d,i)
        return best

def gaps_to_theta(g):
    N=len(g); sites=np.concatenate([[0],np.cumsum(g)[:-1]]); return [2*mp.pi*int(sv)/(2*N) for sv in sites]

if __name__=="__main__":
    import sys
    # test: N=12 argmax [1^7,2,2,9,2,2] should give 2.00001772
    g=[1]*7+[2,2,9,2,2]; H=HeatDepthMP(gaps_to_theta(g),dps=50); N=12
    d,i=H.depth(range(8)); print("N=12 run8:", N*N*d, "pair", i)
