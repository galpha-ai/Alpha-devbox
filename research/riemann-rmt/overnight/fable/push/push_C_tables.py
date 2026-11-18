"""Task C steps (1),(4): structure-class tables and the Nyquist scatter from acue_depth_N*.npz.
Classes: L = longest run of consecutive occupied sites (= longest run of 1-gaps + 1);
 'unique1' = exactly one 1-gap; 'isolated' = no two adjacent 1-gaps (all runs have L<=2)."""
import numpy as np
def longest_run(g):
    g=list(g); N=len(g); gg=g+g; best=0; cur=0
    for x in gg:
        if x==1: cur+=1; best=max(best,cur)
        else: cur=0
    if best>=N: best=N-1
    return best+1   # number of consecutive occupied sites
print("Table 1: max N^2D by (N, longest occupied run L); entries: max N^2D [argmax gaps]")
for N in range(4,13):
    d=np.load(f'acue_depth_N{N}.npz'); D=d['D']; G=d['gaps']; fin=np.isfinite(D); ND=np.where(fin,N*N*D,-np.inf)
    Ls=np.array([longest_run(g) for g in G])
    line=f"N={N:2d}: "
    for L in range(2,N+1):
        m=(Ls==L)&fin
        if m.sum()==0: continue
        i=np.where(m)[0][np.argmax(ND[m])]
        line+=f" L={L}:{ND[i]:.5f}"
    print(line)
print("\nTable 2: max N^2D on structure classes")
print(" N   unique 1-gap [gaps]            isolated 1-gaps (L<=2) [gaps]        L=3 (3-blocks) [gaps]        L>=4 [gaps]")
for N in range(4,13):
    d=np.load(f'acue_depth_N{N}.npz'); D=d['D']; G=d['gaps']; fin=np.isfinite(D); ND=np.where(fin,N*N*D,-np.inf)
    n1=np.array([np.sum(np.array(g)==1) for g in G]); Ls=np.array([longest_run(g) for g in G])
    def mx(m):
        m=m&fin
        if m.sum()==0: return "   -   "
        i=np.where(m)[0][np.argmax(ND[m])]; return f"{ND[i]:.5f} {list(map(int,G[i]))}"
    print(f"{N:2d}  {mx(n1==1):34s} {mx(Ls<=2):36s} {mx(Ls==3):30s} {mx(Ls>=4)}")
print("\nTable 3: Nyquist row.  For each N: max N^2D as a function of |p_N|^2 (parity imbalance^2), and the ACUE-mass-weighted mean")
for N in range(4,13):
    d=np.load(f'acue_depth_N{N}.npz'); D=d['D']; G=d['gaps']; p=d['pN2'].astype(int); fin=np.isfinite(D); ND=np.where(fin,N*N*D,-np.inf)
    w=d['mass']*d['orbit_size']
    vals=sorted(set(p[fin]))
    line=f"N={N:2d}: "
    for v in vals:
        m=(p==v)&fin
        line+=f" p2={v}: max {ND[m].max():.4f} mean {np.sum(w[m]*ND[m])/np.sum(w[m]):.4f} n={m.sum()} |"
    print(line)
print("\nTable 4: correlation of N^2D with |p_N|^2/N^2 and with Q0/N^3 over non-clock orbits (Pearson, Spearman)")
from scipy.stats import spearmanr, pearsonr
for N in range(4,13):
    d=np.load(f'acue_depth_N{N}.npz'); D=d['D']; p=d['pN2']; Q=d['Q0']; fin=np.isfinite(D); ND=N*N*D[fin]
    x=p[fin]/N**2; y=Q[fin]/N**3
    print(f"N={N:2d}: corr(N^2D,|p_N|^2/N^2): pearson {pearsonr(ND,x)[0]:+.3f} spearman {spearmanr(ND,x)[0]:+.3f};  corr(N^2D,Q0/N^3): pearson {pearsonr(ND,y)[0]:+.3f} spearman {spearmanr(ND,y)[0]:+.3f}; |p_N|^2 of argmax = {int(p[fin][np.argmax(ND)])}, of the 3-block: see Table 1")
print("\nTable 5: upper envelope: for N=12, sorted by |p_N|^2, the max N^2D; and the max N^2D among |p_N|^2=0 vs >0")
N=12; d=np.load(f'acue_depth_N{N}.npz'); D=d['D']; p=d['pN2'].astype(int); G=d['gaps']; fin=np.isfinite(D); ND=np.where(fin,N*N*D,-np.inf)
for v in sorted(set(p[fin])):
    m=(p==v)&fin; i=np.where(m)[0][np.argmax(ND[m])]
    print(f"  |p_N|^2={v:3d}: max N^2D {ND[i]:.6f} {list(map(int,G[i]))}   min N^2D {ND[m].min():.6f}")
