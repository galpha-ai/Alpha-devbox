"""Task C step (1): tabulate max N^2 D, argmax gap pattern, top-10 per N from the complete
ACUE orbit enumerations acue_depth_N{4..12}.npz. Also lists where the symmetric 3-block sits,
and the value of |p_N|^2 for the top configurations."""
import numpy as np, sys
def canon(g):
    """dihedral-canonical gap pattern (lexicographically smallest rotation of g or reversed g)"""
    g=list(map(int,g)); N=len(g); best=None
    for h in (g,g[::-1]):
        for r in range(N):
            t=tuple(h[r:]+h[:r])
            if best is None or t<best: best=t
    return best
def is_3block(g):
    """symmetric 3-block: gaps [1,1] once, all other gaps 2 except a single 4 or a pair 3,3 diametrically opposite"""
    c=canon(g); N=len(c)
    k=(N-3)//2
    fam4=tuple([1,1]+[2]*k+[4]+[2]*(N-3-k))
    fam33=tuple([1,1]+[2]*((N-4)//2)+[3,3]+[2]*(N-4-(N-4)//2)) if N%2==0 else None
    return canon(fam4)==c or (fam33 is not None and canon(fam33)==c)
rows=[]
for N in range(4,13):
    d=np.load(f'acue_depth_N{N}.npz'); D=d['D']; G=d['gaps']; p=d['pN2']; fin=np.isfinite(D)
    ND=np.where(fin,N*N*D,-np.inf)
    order=np.argsort(-ND)
    print(f"\n===== N={N}: {fin.sum()} non-clock orbits; max N^2D = {ND[order[0]]:.10f}")
    # 3-block family value
    k=(N-3)//2; fam4=[1,1]+[2]*k+[4]+[2]*(N-3-k)
    fams={'block4':fam4}
    if N%2==0: fams['block33']=[1,1]+[2]*((N-4)//2)+[3,3]+[2]*(N-4-(N-4)//2)
    vals={}
    for name,f in fams.items():
        cf=canon(f)
        for i in range(len(G)):
            if canon(G[i])==cf: vals[name]=(ND[i],int(p[i])); break
    print("  symmetric 3-block values:",{k:(round(v[0],10),v[1]) for k,v in vals.items()})
    print("  rank  N^2D          |p_N|^2  gaps")
    for r,i in enumerate(order[:10]):
        tag=" <-- 3-block" if is_3block(G[i]) else ""
        print(f"  {r+1:3d}  {ND[i]:.10f}  {int(p[i]):4d}  {list(map(int,G[i]))}{tag}")
    # count above 2, above 1.99
    print(f"  #orbits with N^2D>=2: {np.sum(ND>=2)};  >=1.99: {np.sum(ND>=1.99)};  >=1.95: {np.sum(ND>=1.95)}")
    rows.append((N,ND[order[0]],list(map(int,G[order[0]])),vals))
print("\nSummary: N, max N^2D, argmax gaps, 3-block values")
for r in rows: print(r)
