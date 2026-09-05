"""r1_cue_forced_gap.py -- one forced gap in a random CUE background: the threshold lambda*.

For each sample:
  1. draw N Haar-unitary eigenangles (QR of complex Ginibre with phase correction);
  2. pick a uniformly random adjacent pair whose normalised gap lambda_0 = gap*N/(2 pi) is >= 0.7;
  3. move the two points symmetrically about their midpoint so their gap is lambda*2pi/N
     (lambda <= lambda_0, so the two outer gaps only grow);
  4. compute D_pair(lambda) := first flow time s at which either member of the forced pair leaves
     the unit circle (= collides with something), under the full coefficient flow
     P_s(z) = sum_j a_j e^{s j(N-j)} z^j, with the roots tracked by continuation (np.roots +
     linear assignment, adaptive step).  Other pairs may -- and in a CUE background usually do --
     collide before the forced pair; they leave the circle as reciprocal pairs and keep acting on
     the forced pair.  This is the circle analogue of the zeta-side "local depth with collisions
     elsewhere" (r1_levelB_barrier.md, part (a)).
  5. lambda* := the gap at which N^2 D_pair = pi^2/8 (Brent on [0.25, min(0.70, lambda_0)]).

Recorded per sample: lambda_0, lambda*, N^2 D_pair at lambda = 0.5 and 0.45, the number of
collisions elsewhere before D_pair(lambda*), the pair's background stiffness S/N^2 at s = 0
(S = sum_k (1/2) csc^2(x_b^k/2)), the smallest other gap (normalised), and whether the
two-body lower bound D >= -log cos(g/2) (Theorem A, valid on the circle only while all
roots are on the circle) is violated once other pairs have collided.

Usage: python3 r1_cue_forced_gap.py [N] [samples] [seed]   (default 64 220 1)
Writes ../data/r1_cue_forced_gap_N{N}.json
"""
import json
import os
import sys
import time
from math import pi, cos, log

import mpmath as mp
import numpy as np
from scipy.optimize import brentq, linear_sum_assignment

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PI2_8 = pi ** 2 / 8
OFF_TOL = 1e-7


def sample_cue_angles(N, rng):
    G = (rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))) / np.sqrt(2)
    Q, R = np.linalg.qr(G)
    d = np.diag(R)
    Q = Q * (d / np.abs(d))
    ev = np.linalg.eigvals(Q)
    return np.sort(np.angle(ev))


def force_gap(th, i, lam):
    """Return angles with the adjacent pair (i, i+1 mod N) set to normalised gap lam
    symmetrically about its midpoint. th sorted in (-pi, pi]."""
    N = len(th)
    Delta = 2 * pi / N
    j = (i + 1) % N
    a, b = th[i], th[j]
    if j == 0:
        b += 2 * pi
    mid = 0.5 * (a + b)
    out = th.copy()
    out[i] = mid - lam * Delta / 2
    out[j] = mid + lam * Delta / 2
    out = (out + pi) % (2 * pi) - pi
    return out


def mp_poly_descending(th, dps=50):
    """Coefficients of prod_j (z - e^{i th_j}), descending, built in dps-digit arithmetic and cast
    to complex128.  (np.poly is unusable here: the sequential convolution over 64 unit-circle
    roots passes through partial products with coefficients ~2^64 that cancel to O(1), leaving
    O(1) absolute errors -- |P(z_j)| ~ 1.8 was observed at N = 64.)"""
    with mp.workdps(dps):
        a = [mp.mpc(1)]
        for t in th:
            z = mp.expj(mp.mpf(float(t)))
            a = [mp.mpc(0)] + a                       # ascending: multiply by (z - root)
            for k in range(len(a) - 1):
                a[k] -= z * a[k + 1]
        return np.array([complex(x) for x in a[::-1]])


class PairFlow:
    """Coefficient flow of prod(z - e^{i th_j}) with root tracking of a designated pair."""

    def __init__(self, th, ia, ib):
        self.N = N = len(th)
        self.z0 = np.exp(1j * th)
        self.c = mp_poly_descending(th)                # descending: c[k] is coeff of z^{N-k}
        k = np.arange(N + 1)
        self.w = (N - k) * k                            # weight j(N-j) with j = N-k
        self.ia, self.ib = ia, ib

    def roots(self, s):
        return np.roots(self.c * np.exp(s * self.w))

    def pair_depth(self, s_guess):
        N = self.N
        pos = self.z0.copy()
        s = 0.0
        ds = s_guess / 40.0
        ia, ib = self.ia, self.ib
        n_steps = 0
        while True:
            r = self.roots(s + ds)
            cost = np.abs(r[:, None] - pos[None, :])
            row, col = linear_sum_assignment(cost)
            new = np.empty_like(pos)
            new[col] = r[row]
            disp = np.abs(new - pos)
            # step control on the tracked pair only: its displacement must stay well below its
            # nearest-other-root distance, and its assigned roots must be the nearest roots to
            # the previous positions (identity check).  Other roots may be mis-labelled by a large
            # step; only the label-free count of off-circle roots is used for them.
            da = np.abs(pos - pos[ia]); da[ia] = np.inf
            db = np.abs(pos - pos[ib]); db[ib] = np.inf
            nna, nnb = da.min(), db.min()
            ok = (disp[ia] <= 0.25 * nna and disp[ib] <= 0.25 * nnb
                  and new[ia] == r[np.argmin(np.abs(r - pos[ia]))]
                  and new[ib] == r[np.argmin(np.abs(r - pos[ib]))])
            if not ok and ds > 1e-14:
                ds *= 0.5
                continue
            off = np.abs(np.abs(new) - 1.0) > OFF_TOL
            if off[ia] or off[ib]:
                lo, hi = s, s + ds
                break
            pos = new
            s += ds
            n_steps += 1
            if disp[ia] < 0.05 * nna and disp[ib] < 0.05 * nnb:
                ds *= 1.5
            if n_steps > 200000:
                raise RuntimeError("tracking did not terminate")
        # bisection: roots nearest to the last on-circle positions of the pair
        pa, pb = pos[ia], pos[ib]
        n_off_other = int(np.sum(np.abs(np.abs(pos) - 1.0) > OFF_TOL)) // 2
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            r = self.roots(mid)
            ra = r[np.argmin(np.abs(r - pa))]
            rb = r[np.argmin(np.abs(r - pb))]
            if abs(abs(ra) - 1) > OFF_TOL or abs(abs(rb) - 1) > OFF_TOL:
                hi = mid
            else:
                lo = mid
            if hi - lo < 1e-12 * max(hi, 1e-30):
                break
        return 0.5 * (lo + hi), n_off_other


def stiffness(th, ia, ib):
    """S = sum_{k != a,b} (1/2) csc^2(x_b^k/2), x_b^k = (th_b - th_k) mod 2pi."""
    N = len(th)
    mask = np.ones(N, bool)
    mask[[ia, ib]] = False
    x = (th[ib] - th[mask]) % (2 * pi)
    return float(np.sum(0.5 / np.sin(0.5 * x) ** 2))


def run(N, n_samples, seed):
    rng = np.random.default_rng(seed)
    Delta = 2 * pi / N
    rows = []
    t0 = time.time()
    while len(rows) < n_samples:
        th = sample_cue_angles(N, rng)
        gaps = np.diff(np.concatenate([th, [th[0] + 2 * pi]])) / Delta
        cand = np.where(gaps >= 0.7)[0]
        if not cand.size:
            continue
        i = int(rng.choice(cand))
        j = (i + 1) % N
        lam0 = float(gaps[i])
        other_min = float(np.min(np.delete(gaps, i)))

        def n2d(lam):
            th_l = force_gap(th, i, lam)
            # after force_gap the array may be unsorted / wrapped; indices i, j are still the pair
            pf = PairFlow(th_l, i, j)
            g = lam * Delta
            D, n_off = pf.pair_depth(-log(cos(g / 2)))
            return N * N * D, n_off

        rec = {"lam0": lam0, "other_min_gap": other_min,
               "S_over_N2_at_0.5": stiffness(force_gap(th, i, 0.5), i, j) / N ** 2}
        v05, n05 = n2d(0.5)
        v045, n045 = n2d(0.45)
        rec["N2D_at_0.5"] = v05
        rec["n_early_at_0.5"] = n05
        rec["N2D_at_0.45"] = v045
        rec["n_early_at_0.45"] = n045
        rec["two_body_bound_violated_at_0.5"] = bool(v05 < N * N * (-log(cos(0.5 * Delta / 2))) * (1 - 1e-9))
        rec["two_body_bound_violated_at_0.45"] = bool(v045 < N * N * (-log(cos(0.45 * Delta / 2))) * (1 - 1e-9))
        # bracket lambda*: usually in [0.45, 0.5]
        if v045 <= PI2_8 <= v05:
            a, b, fa, fb = 0.45, 0.5, v045 - PI2_8, v05 - PI2_8
        elif v05 < PI2_8:
            b = min(0.70, lam0)
            fb = n2d(b)[0] - PI2_8
            a, fa = 0.5, v05 - PI2_8
        else:
            a = 0.30
            fa = n2d(a)[0] - PI2_8
            b, fb = 0.45, v045 - PI2_8
        if fa > 0:
            rec["lam_star"] = None
            rec["censored"] = "below"
        elif fb < 0:
            rec["lam_star"] = None
            rec["censored"] = "above"
        else:
            ls = brentq(lambda l: n2d(l)[0] - PI2_8, a, b, xtol=3e-4)
            rec["lam_star"] = float(ls)
            rec["censored"] = None
            rec["n_early_at_star"] = n2d(ls)[1]
        rows.append(rec)
        if len(rows) % 20 == 0:
            done = [r["lam_star"] for r in rows if r["lam_star"] is not None]
            print(f"  {len(rows):4d} samples, {time.time() - t0:6.1f}s, "
                  f"lambda* median so far {np.median(done):.4f}", flush=True)
    return rows


def summarise(rows, N):
    ls = np.array([r["lam_star"] for r in rows if r["lam_star"] is not None])
    cens_above = sum(1 for r in rows if r["censored"] == "above")
    cens_below = sum(1 for r in rows if r["censored"] == "below")
    clean = np.array([r["lam_star"] for r in rows if r["lam_star"] is not None and r.get("n_early_at_star", 0) == 0])
    v05 = np.array([r["N2D_at_0.5"] for r in rows])
    v045 = np.array([r["N2D_at_0.45"] for r in rows])
    viol = sum(1 for r in rows if r["two_body_bound_violated_at_0.5"])
    n_early = np.array([r["n_early_at_0.5"] for r in rows])
    q = lambda a, p: float(np.quantile(a, p)) if a.size else None
    summ = {
        "N": N, "samples": len(rows), "censored_above": cens_above, "censored_below": cens_below,
        "lambda_star": {"n": int(ls.size), "mean": float(ls.mean()), "sd": float(ls.std()),
                        "min": float(ls.min()), "q05": q(ls, .05), "q25": q(ls, .25),
                        "median": q(ls, .5), "q75": q(ls, .75), "q95": q(ls, .95), "max": float(ls.max())},
        "lambda_star_clean_no_early_collision": {"n": int(clean.size),
                                                 "mean": float(clean.mean()) if clean.size else None,
                                                 "median": q(clean, .5), "min": float(clean.min()) if clean.size else None,
                                                 "max": float(clean.max()) if clean.size else None},
        "N2D_at_lambda_0.5": {"mean": float(v05.mean()), "median": float(np.median(v05)),
                              "min": float(v05.min()), "max": float(v05.max()),
                              "frac_below_pi2_8": float(np.mean(v05 < PI2_8)),
                              "rho_median": float(np.median(v05) / (pi ** 2 * 0.25 / 2))},
        "N2D_at_lambda_0.45": {"mean": float(v045.mean()), "median": float(np.median(v045)),
                               "frac_below_pi2_8": float(np.mean(v045 < PI2_8))},
        "frac_with_earlier_collision_elsewhere_at_0.5": float(np.mean(n_early > 0)),
        "mean_n_earlier_collisions_at_0.5": float(n_early.mean()),
        "two_body_bound_violations_at_0.5": viol,
        "S_over_N2_median": float(np.median([r["S_over_N2_at_0.5"] for r in rows])),
    }
    return summ


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    n_samples = int(sys.argv[2]) if len(sys.argv) > 2 else 220
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    print(f"N={N} samples={n_samples} seed={seed}")
    rows = run(N, n_samples, seed)
    summ = summarise(rows, N)
    print(json.dumps(summ, indent=1))
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, f"r1_cue_forced_gap_N{N}.json"), "w") as fh:
        json.dump({"summary": summ, "rows": rows}, fh, indent=1)
    print("wrote", os.path.join(DATA, f"r1_cue_forced_gap_N{N}.json"))
