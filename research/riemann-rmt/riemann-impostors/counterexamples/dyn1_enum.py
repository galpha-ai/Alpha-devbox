"""dyn1_enum: exact enumeration of Newman depth over ACUE rotation orbits, N=3..10.
Saves per-orbit results to dyn1_results_N{N}.npz."""
import sys, time, json
import numpy as np
from math import pi
sys.path.insert(0, "/tmp/claude-0/-home-user-Alpha-devbox/00b3b5f7-f917-5641-a9be-c6a8f38f5cd7/scratchpad")
from dyn1_core import (orbits, orbit_masses, coeffs, is_clock, find_ustar,
                       colliding_pair, slot_gaps)

OUT = "/tmp/claude-0/-home-user-Alpha-devbox/00b3b5f7-f917-5641-a9be-c6a8f38f5cd7/scratchpad"

def run(N):
    t0 = time.time()
    reps, sizes, mu = orbit_masses(N)
    R = len(reps)
    tot = mu.sum()
    ustars = np.full(R, np.nan)
    gapcol = np.zeros(R, int)          # slot separation of the colliding pair
    nadj = np.zeros(R, int)            # number of minimal (1-slot) gaps in config
    mingap_slots = np.zeros(R, int)    # minimal slot gap of config
    clockmask = np.zeros(R, bool)
    warns = 0
    for i, rep in enumerate(reps):
        a = coeffs(rep, N)
        g = slot_gaps(rep, N)
        mingap_slots[i] = g.min()
        nadj[i] = int((g == g.min()).sum()) if g.min() == 1 else int((g == 1).sum())
        nadj[i] = int((g == 1).sum())
        if is_clock(a, N):
            clockmask[i] = True
            continue
        u, u_lo, u_hi = find_ustar(a, N)
        if u is None:
            print(f"  N={N} rep={rep}: NO COLLISION by cap (flagged)")
            continue
        ustars[i] = u
        xa, xb, gap, gsize, warn = colliding_pair(a, N, rep, u_lo)
        gapcol[i] = gap
        warns += warn
    np.savez(f"{OUT}/dyn1_results_N{N}.npz",
             reps=np.array([list(r) for r in reps]), sizes=sizes, mu=mu,
             ustars=ustars, gapcol=gapcol, nadj=nadj,
             mingap_slots=mingap_slots, clockmask=clockmask)
    nclock = int(clockmask.sum())
    clockprob = mu[clockmask].sum()
    print(f"N={N}: R={R} orbits, sum(mu)={tot:.15f}, clock orbits={nclock}, "
          f"clock prob={clockprob:.15e} vs 2^(1-N)={2.0**(1-N):.15e}, "
          f"tracking warns={warns}, time={time.time()-t0:.1f}s")

if __name__ == "__main__":
    Ns = [int(x) for x in sys.argv[1:]] or list(range(3, 11))
    for N in Ns:
        run(N)
