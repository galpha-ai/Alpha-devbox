"""fab_disloc.py — verify the single-dislocation constant against our exact enumeration.

Colleague's configuration: alternating clock {e^{i(2j+1)pi/N}} (= roots of z^N+1), delete
r_N = e^{-i pi/N}, insert 1.  P_N(z) = (z-1)(z^N+1)/(z-r_N).  Gap pattern 1,2,...,2,3 in
half-lattice units.  In our 2N-th-root index coordinates (point j = exp(i pi j / N)):
alternating clock = odd indices; delete 2N-1; insert 0  =>  S = {0, 1, 3, 5, ..., 2N-3}.
Claim: N^2(-Lambda) -> s* = 1.41964034...   (equivalently rho = 8N^2(-L)/pi^2 -> 1.150700...)

Also: the ensemble median question.  Our exact enumeration (all orbits, ACUE-weighted) gives
the conditional median of N^2(-Lambda); the colleague's table (N<=7) is monotone increasing
toward s*.  Check whether the median keeps rising or turns around at larger N -- i.e. whether
s* is the ensemble limit or just the value of one (initially dominant) configuration.
"""
import sys, numpy as np
sys.path.insert(0, "/tmp/claude-0/-home-user-Alpha-devbox/00b3b5f7-f917-5641-a9be-c6a8f38f5cd7/scratchpad")
SP = "/tmp/claude-0/-home-user-Alpha-devbox/00b3b5f7-f917-5641-a9be-c6a8f38f5cd7/scratchpad"
from dyn1_core import neg_lambda_of_config          # validated solver from the ACUE round

PI2_8 = np.pi ** 2 / 8


def disloc(N):
    """S = {0,1,3,5,...,2N-3} as indices into the 2N-th roots of unity."""
    return tuple([0] + list(range(1, 2 * N - 2, 2)))


def kfam(N, sep):
    """k=1 family: alternating clock with ONE defect pair at separation `sep`.
    sep=1 is the colleague's adjacent dislocation; larger sep separates the two defects."""
    base = list(range(1, 2 * N, 2))          # odd = alternating clock
    base.remove(2 * N - 1)
    ins = 0 if sep == 1 else (2 * sep - 2)
    if ins in base:
        return None
    return tuple(sorted(base + [ins]))


if __name__ == "__main__":
    print("=== single-dislocation configuration S = {0,1,3,...,2N-3} ===")
    print(f"{'N':>4} {'-Lambda':>16} {'N^2(-L)':>14} {'rho=8N^2L/pi^2':>16}")
    vals = []
    for N in range(3, 19):
        S = disloc(N)
        assert len(S) == N, (N, S)
        nl = neg_lambda_of_config(S, N)
        v = N * N * nl
        vals.append((N, v))
        print(f"{N:>4} {nl:>16.10f} {v:>14.8f} {v / PI2_8:>16.8f}")
    # Richardson extrapolation in 1/N^2 on the last few
    ns = np.array([n for n, _ in vals[-6:]], float)
    vs = np.array([v for _, v in vals[-6:]])
    A = np.vstack([np.ones_like(ns), ns ** -1, ns ** -2]).T
    coef, *_ = np.linalg.lstsq(A, vs, rcond=None)
    print(f"\nextrapolated limit (fit a0 + a1/N + a2/N^2): {coef[0]:.8f}"
          f"   [colleague s* = 1.41964034]  diff = {coef[0]-1.41964034:+.2e}")

    print("\n=== k=1 defect family: dependence on defect separation (N=12) ===")
    N = 12
    for sep in range(1, 7):
        S = kfam(N, sep)
        if S is None or len(S) != N:
            continue
        nl = neg_lambda_of_config(S, N)
        v = N * N * nl
        print(f"  sep={sep}: N^2(-L)={v:.8f}  rho={v/PI2_8:.8f}")

    print("\n=== ensemble conditional median of N^2(-Lambda) from exact enumeration ===")
    print(f"{'N':>4} {'orbits':>8} {'median':>14} {'mean':>14}")
    for N in range(3, 11):
        try:
            d = np.load(f"{SP}/dyn1_results_N{N}.npz")
        except FileNotFoundError:
            continue
        keys = list(d.keys())
        nl = d["neglam"] if "neglam" in keys else d[keys[0]]
        mu = d["mu"] if "mu" in keys else None
        finite = np.isfinite(nl) & (nl > 0)
        x = (N * N) * nl[finite]
        if mu is not None:
            w = mu[finite] / mu[finite].sum()
            o = np.argsort(x)
            c = np.cumsum(w[o])
            med = x[o][np.searchsorted(c, 0.5)]
            mean = float(x @ w)
        else:
            med, mean = float(np.median(x)), float(x.mean())
        print(f"{N:>4} {finite.sum():>8} {med:>14.8f} {mean:>14.8f}")
