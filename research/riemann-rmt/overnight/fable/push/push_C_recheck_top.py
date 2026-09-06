"""Re-verify the top-K enumeration values at N=9..12 with Method A (mpmath polyroots, dps=30)."""
import numpy as np, mpmath as mp, sys, time
from push_C_verify import methodA
K=int(sys.argv[1]) if len(sys.argv)>1 else 12
for N in [9,10,11,12]:
    d=np.load(f'acue_depth_N{N}.npz'); D=d['D']; G=d['gaps']; fin=np.isfinite(D); ND=np.where(fin,N*N*D,-np.inf)
    order=np.argsort(-ND)[:K]
    print(f"== N={N}")
    for i in order:
        g=[int(x) for x in G[i]]; t0=time.time()
        tau,ang=methodA(g,dps=30,scan=False)
        # count coincident angles at collision (multiplicity structure)
        angs=[float(x) for x in ang]; mult=[]
        j=0
        while j<N:
            k=j
            while k+1<N and abs(angs[k+1]-angs[j])<1e-6: k+=1
            if k>j: mult.append((round(angs[j]*N/np.pi,4),k-j+1))
            j=k+1
        print(f"  enum {ND[i]:.10f}  polyroots {mp.nstr(tau,14)}  diff {float(tau)-ND[i]:+.2e}  gaps {g}  collisions(site,mult) {mult}  [{time.time()-t0:.1f}s]",flush=True)
