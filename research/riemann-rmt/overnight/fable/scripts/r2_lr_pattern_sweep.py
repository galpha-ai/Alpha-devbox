"""r2_lr_pattern_sweep.py -- sweep of the lattice pattern LP over M (pattern mode and pair mode).

For each even M, hard cores k = ceil(M/2)+1, ... are tested until the first infeasible k (s* > 1e-6);
W is the largest window with at most `maxpat` admissible words (count = sum_t C(W-(k-1)(t-1), t)).
Writes r2_lr_pattern_results.jsonl (appended by r2_lr_pattern_lp.solve) and prints a table.
Usage: python3 r2_lr_pattern_sweep.py "8 10 12 16 20 24 30 40 50" maxpat mode
"""
import sys, json, time
from math import comb
sys.path.insert(0, '.')
from r2_lr_pattern_lp import solve, DATA

def npat(W, k):
    tot, t = 0, 0
    while W - (k-1)*(t-1) >= t:
        tot += comb(W - (k-1)*(t-1), t); t += 1
    return tot

def pick_W(k, maxpat, Wmax=400):
    W = k
    while W + 1 <= Wmax and npat(W + 1, k) <= maxpat: W += 1
    return W

if __name__ == "__main__":
    Ms = [int(v) for v in sys.argv[1].split()]
    maxpat = int(sys.argv[2]); mode = sys.argv[3]
    dal = float(sys.argv[4]) if len(sys.argv) > 4 else 0.01
    rows = []
    for M in Ms:
        k = M//2 + 1
        while True:
            W = pick_W(k, maxpat) if mode == 'pattern' else 2*k
            t0 = time.time()
            out = solve(M, k, W, dal=dal, Jmax_mult=8, mode=mode)
            with open(f"{DATA}/r2_lr_pattern_results.jsonl", "a") as f: f.write(json.dumps(out) + "\n")
            feas = out['s'] <= 1e-6
            print(f"M={M:3d} k={k:3d} c={k/M:.4f} W={W:3d} ({W/M:.2f} spacings) nP={out['info']['nP']:7d} "
                  f"nvar={out['info']['nvar']:7d} s*={out['s']:.3e} {'FEAS' if feas else 'infeasible'} "
                  f"solve={out['info']['solve_s']:.1f}s", flush=True)
            if not feas:
                rows.append((M, k-1, (k-1)/M, k, k/M, W)); break
            k += 1
            if k > M: break
    print("\nsummary (mode=%s, maxpat=%d): largest feasible c and first infeasible c" % (mode, maxpat))
    for M, kf, cf, ki, ci, W in rows:
        print(f"  M={M:3d}: feasible up to c={kf}/{M}={cf:.4f}, infeasible at c={ki}/{M}={ci:.4f}  (W={W})")
