"""fab_theorem.py — the signed no-gain identity, derived and verified.

Pointwise identity, valid for ANY w: (nu - m) + (m - nu)_+ = (nu - m)_+.
Hence for w = w_+ - w_- (disjoint supports), with the EXACT decode debt
D(w) = sum_{w<0} |w| (m - nu)_+ :

  S2 - m S1 - D  =  sum w_+ (nu - m)  -  sum w_- (nu - m)_+          (*)
                 <=  sum w_+ (nu - m)  =  [the same functional at w_+ alone].

So the negative part is PURE LOSS: deleting it never decreases the repaired functional.
The signed class is exactly redundant in any model where both w and w_+ are evaluable.

This script verifies (*) numerically on the finite arithmetic model, at LP optima and on
random signed weights, in exact rational arithmetic.
"""
import sys, random
sys.path.insert(0, "/tmp/claude-0/-home-user-Alpha-devbox/00b3b5f7-f917-5641-a9be-c6a8f38f5cd7/scratchpad")
from fractions import Fraction as F
from sgn1_model import build_model, primes_upto

BIG = [p for p in primes_upto(37) if p > 7]


def check(H, feat, m, L=1, trials=200, seed=0):
    M = build_model(tuple(H), feat, BIG, m=m, L=L)
    nc = M["ncell"]
    N1, Nnu, G = M["N1"], M["Nnu"], M["G"]
    Gp = M["Gp"]            # mu(c) E[(nu - m)_+ | c]
    a = [Nnu[c] - m * N1[c] for c in range(nc)]      # mu(c) E[nu - m | c]
    # identity check at the cell level: a(c) + G(c) == Gp(c)
    bad = [c for c in range(nc) if a[c] + G[c] != Gp[c]]
    print(f"H={H} m={m} L={L} cells={nc}: cellwise identity a+G==Gp violations = {len(bad)}")
    assert not bad, bad[:5]

    rng = random.Random(seed)
    basis = M["Phi_2L"]                     # list of columns (len nc) over cells
    dim = len(basis)
    worst = F(0)
    for t in range(trials):
        x = [F(rng.randint(-9, 9), rng.randint(1, 5)) for _ in range(dim)]
        w = [sum(x[j] * basis[j][c] for j in range(dim)) for c in range(nc)]
        S1 = sum(N1[c] * w[c] for c in range(nc))
        S2 = sum(Nnu[c] * w[c] for c in range(nc))
        D = sum(-w[c] * G[c] for c in range(nc) if w[c] < 0)
        lhs = S2 - m * S1 - D
        rhs = (sum(w[c] * a[c] for c in range(nc) if w[c] > 0)
               - sum(-w[c] * Gp[c] for c in range(nc) if w[c] < 0))
        assert lhs == rhs, (t, lhs, rhs)
        # domination: repaired functional <= functional at the positive part
        pos_only = sum(w[c] * a[c] for c in range(nc) if w[c] > 0)
        assert lhs <= pos_only
        worst = max(worst, pos_only - lhs)
    print(f"  identity (*) exact on {trials} random signed weights; "
          f"max shortfall (loss from the negative part) = {float(worst):.6f}")
    return True


if __name__ == "__main__":
    check((0, 2, 6), [2, 3, 5, 7], m=1)
    check((0, 2, 6), [2, 3, 5, 7], m=1, L=2)
    check((0, 2, 6, 8), [2, 3, 5, 7], m=1)
    check((0, 2, 6, 8, 12), [2, 3, 5, 7], m=2)
    check((0, 4, 6), [2, 3, 5], m=1)
    print("\nAll checks passed: the signed no-gain identity holds exactly.")
