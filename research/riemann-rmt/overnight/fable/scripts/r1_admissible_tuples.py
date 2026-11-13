#!/usr/bin/env python3
"""r1_admissible_tuples.py -- admissible k-tuple UPPER bounds on H(k) for k = 38, 39, 40 (task D2b).

Method (Schinzel-type sieve + simulated annealing over the sieve pattern):
  * every admissible k-tuple (k >= 2) is monochromatic mod 2, so search among even offsets 0,2,..,D;
  * a "sieve pattern" chooses one residue class r_p mod p to AVOID for every odd prime p <= k;
    the survivors {2i : 2i mod p != r_p for all p} form an admissible set (for p > k admissibility
    is automatic since a k-set cannot cover p > k classes);
  * for a target diameter D we maximise the number of survivors in [0, D] over patterns by simulated
    annealing; >= k survivors  =>  H(k) <= D (take any k of them; the diameter is <= D).
  * D is decreased until the search fails within its budget; the smallest D reached is the bound.
Every reported tuple is re-verified by an independent brute-force admissibility check (all primes
p <= max element).  The repo's exhaustive witnesses (scratchpad p4_payoff_table.txt: 176/182/186)
and the audit's "published 40-tuple" are verified with the same checker.

Output: ../data/r1_admissible_tuples.json.  Usage: python3 r1_admissible_tuples.py [seed]
"""
import sys, os, json, math, random, time
import numpy as np
from sympy import primerange, isprime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

def is_admissible(tup):
    """Brute force: for every prime p <= max(tup), some residue class mod p is missed."""
    tup = sorted(set(int(v) for v in tup))
    top = max(tup)
    bad = []
    for p in primerange(2, top + 1):
        if len(set(v % p for v in tup)) == p:
            bad.append(int(p))
    return (len(bad) == 0), bad

def search(k, D, iters=60000, seed=0, T0=1.0):
    """SA over sieve patterns; returns a list of >= k survivors in [0, D] or None."""
    rng = random.Random(seed)
    n = D // 2 + 1
    vals = np.arange(n) * 2
    primes = [int(p) for p in primerange(3, k + 1)]
    classes = {p: vals % p for p in primes}
    # greedy init: for each prime pick the class killing fewest current survivors
    kills = np.zeros(n, dtype=np.int32)
    pat = {}
    for p in primes:
        alive = kills == 0
        cnt = np.bincount(classes[p][alive], minlength=p)
        r = int(np.argmin(cnt))
        pat[p] = r
        kills[classes[p] == r] += 1
    cur = int(np.sum(kills == 0))
    best, best_kills = cur, kills.copy()
    T = T0
    for it in range(iters):
        p = rng.choice(primes)
        r_old = pat[p]
        r_new = rng.randrange(p)
        if r_new == r_old:
            continue
        kills[classes[p] == r_old] -= 1
        kills[classes[p] == r_new] += 1
        new = int(np.sum(kills == 0))
        if new >= cur or rng.random() < math.exp((new - cur) / T):
            cur = new; pat[p] = r_new
            if cur > best:
                best, best_kills = cur, kills.copy()
                if best >= k:
                    break
        else:
            kills[classes[p] == r_new] -= 1
            kills[classes[p] == r_old] += 1
        T = max(0.15, T0 * (1 - it / iters))
    if best >= k:
        surv = vals[best_kills == 0]
        # choose the narrowest window of k consecutive survivors
        w = surv[k - 1:] - surv[:len(surv) - k + 1]
        j = int(np.argmin(w))
        tup = [int(v - surv[j]) for v in surv[j:j + k]]
        ok, bad = is_admissible(tup)
        assert ok, bad
        return tup
    return None

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    out = {"method": "Schinzel sieve pattern + simulated annealing; brute-force verification",
           "results": {}}
    # 1. verify repo witnesses (scratchpad p4_payoff_table.txt) and the audit's published 40-tuple
    witnesses = {
        38: [0,6,8,14,18,20,24,30,36,38,44,48,50,56,60,66,74,78,80,84,86,90,104,108,114,116,126,128,134,140,144,150,156,158,168,170,174,176],
        39: [0,2,6,8,12,20,26,30,36,38,42,48,50,56,62,66,68,72,78,80,90,92,108,110,126,128,132,138,140,146,150,152,156,162,168,170,176,180,182],
        40: [0,4,6,10,16,18,24,28,30,34,40,46,48,54,60,66,70,76,84,88,94,96,100,108,114,118,126,130,136,138,144,150,154,156,160,166,174,180,184,186],
    }
    audit40 = [0,2,6,12,20,26,30,32,36,42,48,50,56,60,68,72,78,86,90,92,98,102,110,116,120,126,132,138,140,146,152,156,158,162,168,170,176,180,182,186]
    out["repo_witnesses"] = {}
    for k, t in witnesses.items():
        ok, bad = is_admissible(t)
        out["repo_witnesses"][str(k)] = {"len": len(t), "diameter": max(t) - min(t), "admissible": ok, "bad_primes": bad}
        print(f"repo witness k={k}: len={len(t)} diam={max(t)-min(t)} admissible={ok} {bad}")
    ok, bad = is_admissible(audit40)
    out["audit_published_40_tuple"] = {"len": len(audit40), "diameter": max(audit40) - min(audit40), "admissible": ok, "bad_primes": bad}
    print(f"audit 'published 40-tuple': len={len(audit40)} diam={max(audit40)-min(audit40)} admissible={ok} {bad}")
    # 2. own search
    for k in (38, 39, 40):
        t0 = time.time()
        D = 2 * (k * 5)          # generous start
        found = None
        D_best = None
        # first find any solution quickly, then descend
        while D >= 2:
            tup = None
            for s in range(6):
                tup = search(k, D, iters=40000, seed=seed * 1000 + s + D)
                if tup is not None:
                    break
            if tup is None:
                break
            found, D_best = tup, max(tup) - min(tup)
            D = D_best - 2
        ok, bad = is_admissible(found)
        out["results"][str(k)] = {"H_upper": D_best, "tuple": found, "verified_admissible": ok,
                                  "bad_primes": bad, "seconds": round(time.time() - t0, 1)}
        print(f"k={k}: H({k}) <= {D_best}  (search failed at D={D_best-2} within budget)  verified={ok}  [{time.time()-t0:.0f}s]")
        print("   tuple:", found)
    json.dump(out, open(os.path.join(DATA, "r1_admissible_tuples.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
