#!/usr/bin/env python3
"""P9: construct admissible k-tuples of small diameter (greedy sieve).

Method: on [0,N], for each prime p <= k in increasing order, delete the
residue class with the fewest surviving elements (no deletion needed if some
class is already empty). The surviving set is admissible for every p <= k by
construction (chosen class stays empty); for p > k (and p > diameter)
admissibility is automatic. Then take the k consecutive survivors of minimal
diameter. Independent verification pass included.
"""
import numpy as np
import sys


def primes_upto(n):
    sieve = np.ones(n + 1, dtype=bool)
    sieve[:2] = False
    for p in range(2, int(n ** 0.5) + 1):
        if sieve[p]:
            sieve[p * p:: p] = False
    return np.flatnonzero(sieve)


def greedy_tuple(k, N, seed=None, jitter=0.0):
    rng = np.random.default_rng(seed)
    surv = np.ones(N + 1, dtype=bool)
    pr = primes_upto(k)
    for p in pr:
        pos = np.flatnonzero(surv)
        cnt = np.bincount(pos % p, minlength=p)
        if cnt.min() == 0:
            continue  # already admissible mod p
        if jitter > 0:
            # randomized near-greedy: pick among classes within (1+jitter)*min
            cand = np.flatnonzero(cnt <= cnt.min() * (1 + jitter) + 0.5)
            c = rng.choice(cand)
        else:
            c = int(np.argmin(cnt))
        surv[np.arange(c, N + 1, p)] = False
    pos = np.flatnonzero(surv)
    if len(pos) < k:
        return None, len(pos)
    diams = pos[k - 1:] - pos[: len(pos) - k + 1]
    i = int(np.argmin(diams))
    return pos[i: i + k], len(pos)


def verify_admissible(tup, k):
    """exact check: for every prime p <= k, residues covered < p."""
    pr = primes_upto(k)
    for p in pr:
        if len(np.unique(tup % p)) >= p:
            return False, p
    return True, None


def primes_past_k(k):
    """rigorous fallback: first k primes > k. Returns diameter."""
    import sympy
    # estimate upper end
    import math
    n_needed = k
    lo = k + 1
    # segmented sieve up to generous bound
    ub = int(k * (math.log(k) + math.log(math.log(k)) + 1.2)) + 100
    while True:
        sieve = np.ones(ub + 1, dtype=bool)
        sieve[:2] = False
        for p in range(2, int(ub ** 0.5) + 1):
            if sieve[p]:
                sieve[p * p:: p] = False
        pl = np.flatnonzero(sieve)
        pl = pl[pl > k]
        if len(pl) >= k:
            return pl[k - 1] - pl[0], (pl[0], pl[k - 1])
        ub = int(ub * 1.2)


if __name__ == "__main__":
    k = int(sys.argv[1])
    N = int(sys.argv[2]) if len(sys.argv) > 2 else int(k * (np.log(k) + 1.1) * 1.12)
    tup, nsurv = greedy_tuple(k, N)
    if tup is None:
        print(f"k={k}: N={N} too small, only {nsurv} survivors")
        sys.exit(1)
    D = int(tup[-1] - tup[0])
    ok, badp = verify_admissible(tup, k)
    print(f"k={k}: N={N}, survivors={nsurv}, greedy diameter H <= {D}, admissible={ok}" + ("" if ok else f" VIOLATION p={badp}"))


def refined_tuple(k, N=None, rounds=4, margin_frac=0.02, verbose=False):
    """Greedy + window-targeted iterative re-choice of residue classes.
    Maintains cnt[i] = number of chosen classes covering i; survivor iff cnt==0."""
    if N is None:
        N = int(k * (np.log(k) + 1.1) * 1.18)
    pr = primes_upto(k)
    cnt = np.zeros(N + 1, dtype=np.int16)
    choice = {}
    # initial greedy (ascending)
    for p in pr:
        alive = np.flatnonzero(cnt == 0)
        c_cnt = np.bincount(alive % p, minlength=p)
        c = int(np.argmin(c_cnt))
        choice[p] = c
        if c_cnt[c] > 0 or True:
            cnt[c::p] += 1
    def best_window():
        pos = np.flatnonzero(cnt == 0)
        if len(pos) < k:
            return None, None, pos
        d = pos[k - 1:] - pos[: len(pos) - k + 1]
        i = int(np.argmin(d))
        return pos[i], pos[i + k - 1], pos
    lo, hi, pos = best_window()
    if lo is None:
        raise RuntimeError(f"not enough survivors: {len(pos)} < {k}")
    if verbose:
        print(f"initial greedy: D = {hi-lo}, survivors {len(pos)}")
    for r in range(rounds):
        m = int((hi - lo) * margin_frac) + 500
        rlo, rhi = max(0, lo - m), min(N, hi + m)
        for p in pr:
            c_old = choice[p]
            cnt[c_old::p] -= 1
            reg = cnt[rlo:rhi + 1]
            alive = np.flatnonzero(reg == 0) + rlo
            c_cnt = np.bincount(alive % p, minlength=p)
            c = int(np.argmin(c_cnt))
            # keep old if equal (stability)
            if c_cnt[c] == c_cnt[c_old]:
                c = c_old
            choice[p] = c
            cnt[c::p] += 1
        lo2, hi2, pos = best_window()
        if lo2 is None:
            raise RuntimeError("lost survivors during refine")
        if verbose:
            print(f"round {r}: D = {hi2-lo2}, survivors {len(pos)}")
        lo, hi = lo2, hi2
    tup = np.flatnonzero(cnt == 0)
    i = np.searchsorted(tup, lo)
    tup = tup[i:i + k]
    return tup


def hensley_richards(k, mrange=None, verbose=False):
    """H-R tuple: {+-1} u {+-p_{m+1..m+n}}, n = k/2-1 (k even). Exact admissibility
    check for all p <= k; scan m, return best (D, m, tuple)."""
    assert k % 2 == 0 or True
    n = (k - 2) // 2  # primes per side; total = 2n+2 (k or k-1... handle below)
    # generous prime list
    import math
    ub = int((n + 3000) * (math.log(n + 3000) + math.log(math.log(n + 3000)))) + 1000
    pl = primes_upto(ub)
    pr_small = primes_upto(k)
    best = None
    if mrange is None:
        mrange = range(0, 2000, 25)
    for m in mrange:
        side = pl[m: m + n]
        if len(side) < n:
            break
        tup = np.concatenate([-side[::-1], [-1, 1], side])
        if len(tup) > k:
            tup = tup[:k]
        D = int(tup[-1] - tup[0])
        if best is not None and D >= best[0]:
            continue
        ok = True
        for p in pr_small:
            r = np.unique(np.mod(tup, p))
            if len(r) >= p:
                ok = False
                break
        if ok:
            best = (D, m, tup)
            if verbose:
                print(f"  m={m}: ADMISSIBLE D={D}")
        elif verbose and m % 200 == 0:
            print(f"  m={m}: fails at p={p}, D would be {D}")
    return best
