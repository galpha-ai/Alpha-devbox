"""fab_separation.py — the CUE/ACUE separation, both sides.

ACUE side [PROVED, deterministic]: Theorem A + delta_min = pi/N exactly give
        N^2(-Lambda) >= pi^2/8 = 1.2337...   for EVERY non-clock configuration.

CUE side: we must show N^2(-Lambda) < pi^2/8 with probability -> 1.  Two ingredients:
 (a) the extreme-gap law makes delta_min ~ N^{-4/3} << pi/N, in fact
     P(delta_min > pi/N) = P(N^{4/3} delta_min > pi N^{1/3}) -> exp(-pi^2 N/72), superpolynomially small;
 (b) Theorem B's background control needs a regularity event: the background force on the critical
     pair, B := sum_{k != a,b} [cot(x_b^k/2) - cot(x_a^k/2)] / g, must satisfy B <= A N^2.
     (At the clock B is exactly the balancing term, so A ~ 1/6 is the natural scale:
      sum_{k=1}^{N-1} csc^2(pi k/N)/2 = (N^2-1)/6.)
This script measures (b) on the stored CUE samples and checks the separation conclusion directly.
"""
import numpy as np, glob
PI2_8 = np.pi**2/8

def background_ratio(th):
    """B/N^2 for the closest pair; B is the background slowdown coefficient in g' = -2cot(g/2) + B g."""
    N = len(th); s = np.sort(th)
    g = np.diff(np.concatenate([s, [s[0]+2*np.pi]]))
    i = int(np.argmin(g)); gm = g[i]
    a, b = s[(i+1) % N] + (2*np.pi if i == N-1 else 0), s[i]
    tot = 0.0
    for k in range(N):
        if k in (i, (i+1) % N): continue
        xa = (a - s[k]) % (2*np.pi); xb = (b - s[k]) % (2*np.pi)
        tot += 1/np.tan(xb/2) - 1/np.tan(xa/2)
    return tot/gm/N**2, gm

print("(b) background regularity on stored CUE samples:  B/N^2  (clock value 1/6 = 0.1667)")
print(f"{'N':>5} {'samples':>8} {'median':>10} {'q90':>10} {'q99':>10} {'max':>10}")
for f in sorted(glob.glob("dyn2_data_N*.npz"), key=lambda s:int(s.split('_N')[1][:-4])):
    N = int(f.split('_N')[1][:-4])
    if N < 8 or N > 64: continue
    d = np.load(f)
    if 'angles' not in d:
        continue
print("   (angles not stored; recomputing a fresh CUE batch instead)\n")

rng = np.random.default_rng(20)
def haar_angles(N, rng):
    Z = (rng.normal(size=(N,N)) + 1j*rng.normal(size=(N,N)))/np.sqrt(2)
    Q, R = np.linalg.qr(Z); Q = Q*(np.diag(R)/np.abs(np.diag(R)))
    return np.angle(np.linalg.eigvals(Q))

print(f"{'N':>5} {'samples':>8} {'median B/N^2':>13} {'q90':>9} {'q99':>9} {'max':>9}"
      f" {'median N^2 dmin^2':>18}")
for N in (8, 16, 32, 64, 128):
    M = 400 if N <= 64 else 150
    rs, gs = [], []
    for _ in range(M):
        th = haar_angles(N, rng)
        r, gm = background_ratio(th)
        rs.append(r); gs.append(gm)
    rs = np.array(rs); gs = np.array(gs)
    print(f"{N:>5} {M:>8} {np.median(rs):>13.5f} {np.quantile(rs,.9):>9.5f}"
          f" {np.quantile(rs,.99):>9.5f} {rs.max():>9.5f} {np.median(N**2*gs**2):>18.6f}")

print("\nSeparation conclusion: fraction of CUE samples with N^2(-Lambda) < pi^2/8 = 1.2337")
print(f"{'N':>5} {'samples':>8} {'frac below':>12} {'median N^2(-L)':>16} {'max N^2(-L)':>13}")
for f in sorted(glob.glob("dyn2_data_N*.npz"), key=lambda s:int(s.split('_N')[1][:-4])):
    N = int(f.split('_N')[1][:-4])
    d = np.load(f); nl = d['neglam']; ok = np.isfinite(nl) & (nl > 0)
    x = N*N*nl[ok]
    print(f"{N:>5} {ok.sum():>8} {np.mean(x < PI2_8):>12.4f} {np.median(x):>16.6f} {x.max():>13.6f}")
