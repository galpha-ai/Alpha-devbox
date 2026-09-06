import mpmath as mp, sys, time
from heat_depth_mp import HeatDepthMP, gaps_to_theta
def runL(N,L):
    k=(N-L)//2; g=[1]*(L-1)+[2]*k+[L+1]+[2]*k; assert sum(g)==2*N and len(g)==N; return g
for L in [4,6,8,7,10]:
    for N in [32,48,64]:
        if (N-L)%2: N+=1
        t0=time.time(); H=HeatDepthMP(gaps_to_theta(runL(N,L)),dps=50)
        d,i=H.depth(range(L-1)); print(f"L={L} N={N} N^2D={mp.nstr(N*N*d,12)} pair={i} t={time.time()-t0:.0f}s",flush=True)
