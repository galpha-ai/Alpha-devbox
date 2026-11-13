"""Exact re-check of enumeration depths with the extremum-tracking heat solver (only 1-gap pairs matter
for N^2 D < pi^2/2). Usage: python recheck.py N mode  (mode: all | top | sample)"""
import numpy as np, sys, time
from multiprocessing import Pool
from heat_depth import HeatDepth
N=int(sys.argv[1]); mode=sys.argv[2]
d=np.load(f"acue_depth_N{N}.npz"); D=d['D']; g=d['gaps']; fin=np.isfinite(D); ND=np.where(fin,N*N*D,np.nan)
if mode=='all': idx=np.where(fin)[0]
elif mode=='top': idx=np.where((ND>=1.9)|(ND<=1.36))[0]
else:
    rng=np.random.default_rng(0); idx=rng.choice(np.where(fin)[0],2000,replace=False)
def work(i):
    gg=g[i]; sites=np.concatenate([[0],np.cumsum(gg)[:-1]]); theta=2*np.pi*sites/(2*N)
    H=HeatDepth(theta); pairs=[j for j in range(N) if gg[j]==1]
    dd,pr=H.depth(pairs=pairs)
    return i,N*N*dd,pr
t0=time.time()
with Pool(4) as p: res=p.map(work,idx,chunksize=20)
out=np.array([(i,v) for i,v,_ in res]); np.save(f"recheck_N{N}_{mode}.npy",out)
old=ND[out[:,0].astype(int)]; new=out[:,1]
print(f"N={N} mode={mode}: {len(idx)} orbits, time {time.time()-t0:.0f}s; max|old-new|={np.nanmax(np.abs(old-new)):.3e}; n changed>1e-6: {np.sum(np.abs(old-new)>1e-6)}")
print(f"  exact max N^2D={new.max():.8f} gaps={g[int(out[np.argmax(new),0])].tolist()};  exact min={new.min():.8f} gaps={g[int(out[np.argmin(new),0])].tolist()}")
bad=np.argsort(-(old-new))[:5]; print("  largest overestimates (old,new,gaps):",[(round(float(old[b]),5),round(float(new[b]),5),g[int(out[b,0])].tolist()) for b in bad])
