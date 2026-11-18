"""fab_lemma1.py — proof-check of the two-body comparison theorem.

THEOREM A (claim).  Under the depth flow, every adjacent gap satisfies
        g' >= -2 cot(g/2),
so each gap dominates the pure two-body solution, and therefore
        -Lambda >= -log cos(delta_min/2) >= delta_min^2/8,   i.e.  rho >= 1.

Proof idea: theta_j' = -sum_{k != j} cot((theta_j-theta_k)/2).  For an ADJACENT pair (a,b)
(no root strictly inside the short arc from b to a) and any other root k, setting
x_j^k = (theta_j - theta_k) mod 2pi in (0,2pi), one has x_b^k < x_a^k = x_b^k + g, and
cot(x/2) is strictly decreasing on (0,2pi).  Hence every bracket
cot(x_a/2) - cot(x_b/2) < 0 and it enters g' with a MINUS sign, so it slows the collapse.

Checks below: (i) the sign claim on random and lattice configurations; (ii) the resulting
inequality -Lambda >= -log cos(delta_min/2) on every dataset we have.
"""
import numpy as np, sys
sys.path.insert(0, ".")
from dyn1_core import find_ustar, coeffs

def gap_derivative_terms(th, ia, ib):
    """returns (two-body term, list of background contributions to g')"""
    N = len(th)
    g = (th[ia] - th[ib]) % (2*np.pi)
    two = -2/np.tan(g/2)
    bg = []
    for k in range(N):
        if k in (ia, ib): continue
        xa = (th[ia]-th[k]) % (2*np.pi)
        xb = (th[ib]-th[k]) % (2*np.pi)
        bg.append(-(1/np.tan(xa/2) - 1/np.tan(xb/2)))
    return two, np.array(bg)

rng = np.random.default_rng(5)
print("(i) sign claim: every background contribution to g' must be POSITIVE (slows collapse)")
bad = 0; tot = 0
for trial in range(400):
    N = rng.integers(3, 12)
    th = np.sort(rng.uniform(0, 2*np.pi, N))
    gaps = np.diff(np.concatenate([th, [th[0]+2*np.pi]]))
    i = int(np.argmin(gaps))                    # adjacent pair (i, i+1)
    ia, ib = (i+1) % N, i
    two, bg = gap_derivative_terms(th, ia, ib)
    tot += len(bg); bad += int((bg < -1e-12).sum())
print(f"    random configs: {tot} background terms, {bad} negative  -> claim {'HOLDS' if bad==0 else 'FAILS'}")
bad = 0; tot = 0
for N in range(3, 12):
    for trial in range(200):
        idx = np.sort(rng.choice(2*N, N, replace=False))
        th = np.pi*idx/N
        gaps = np.diff(np.concatenate([th, [th[0]+2*np.pi]]))
        i = int(np.argmin(gaps)); ia, ib = (i+1) % N, i
        two, bg = gap_derivative_terms(th, ia, ib)
        tot += len(bg); bad += int((bg < -1e-12).sum())
print(f"    ACUE lattice  : {tot} background terms, {bad} negative  -> claim {'HOLDS' if bad==0 else 'FAILS'}")

print("\n(ii) the resulting inequality  -Lambda >= -log cos(delta_min/2)  on all datasets")
print(f"{'dataset':>22} {'samples':>9} {'min of (-Lambda)/(-log cos)':>28} {'verdict':>9}")
for N in (6, 8, 10):
    d = np.load(f"dyn1_results_N{N}.npz")
    m = ~d['clockmask']
    ratios = []
    reps, ust = d['reps'][m], d['ustars'][m]
    for rep, u in zip(reps, ust):
        th = np.sort(np.pi*np.array(rep)/N)
        gaps = np.diff(np.concatenate([th, [th[0]+2*np.pi]]))
        lb = -np.log(np.cos(gaps.min()/2))
        ratios.append(u/lb)
    ratios = np.array(ratios)
    print(f"{'ACUE exact N='+str(N):>22} {len(ratios):>9} {ratios.min():>28.10f} "
          f"{'OK' if ratios.min() >= 1-1e-9 else 'VIOLATED':>9}")
for N in (16, 64, 256):
    try: d = np.load(f"dyn2_data_N{N}.npz")
    except FileNotFoundError: continue
    nl, dm = d['neglam'], d['dmin']
    ok = np.isfinite(nl) & (nl > 0) & (dm > 0)
    r = nl[ok] / (-np.log(np.cos(dm[ok]/2)))
    print(f"{'CUE MC N='+str(N):>22} {ok.sum():>9} {r.min():>28.10f} "
          f"{'OK' if r.min() >= 1-1e-6 else 'VIOLATED':>9}")
