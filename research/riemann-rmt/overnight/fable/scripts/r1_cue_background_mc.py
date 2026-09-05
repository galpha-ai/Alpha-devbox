#!/usr/bin/env python3
"""
r1_cue_background_mc.py -- Monte Carlo for r1_cue_background.md (task A2, CUE background bound).

For N in (64, 128, 256) sample Haar-unitary matrices (QR of a complex Ginibre matrix with the
standard phase correction R -> diag(R)/|diag(R)|), take the eigenangles, and record for each sample:

  delta_min          smallest cyclic gap; (a,b) its endpoints (adjacent)
  S_star             sum_{k != a,b} (1/2) max( csc^2(x_b^k/2), csc^2(x_a^k/2) ),  x_j^k = (theta_j - theta_k) mod 2pi
                     (computed literally from the definition, and cross-checked against the
                     circular-distance form  sum_k (1/2) csc^2(d_k/2),  d_k = dist(theta_k, {theta_a, theta_b}))
  S_old              sum_{k != a,b} (1/2) csc^2(x_b^k/2)   (the un-repaired stiffness, for comparison)
  d3                 min_k d_k  = distance from the min-gap pair to the nearest third point
  d_bulk_share       fraction of S_star carried by points with d_k <= 4/N

Outputs (printed and saved to ../data/r1_cue_background_mc.json, per-sample arrays in
../data/r1_cue_background_mc_samples.npz):
  * S_star/N^2: median, 99th percentile, max; fraction with S_star > N^2 log N; fraction > M N^2 for M=0.5,1
  * N*d3: quantiles; empirical P(N d3 <= c) for c = 1..6 vs the leading-order prediction c^5/(3600 pi);
    lower-tail power-law exponent (MLE on the k smallest values below a threshold, bootstrap CI);
    prediction: exponent 5.
  * N^{4/3} delta_min: empirical survival vs exp(-x^3/(72 pi)) at a few x (Ben Arous-Bourgade limit,
    recalled; the constant 72 pi is fixed by the exact first-moment computation in the .md).
  * ratio S_star/(2/d3^2): how much of S_star is the nearest third point.

Usage: python3 r1_cue_background_mc.py [--quick]     (quick: 1/4 of the sample sizes)
Uses at most 2 BLAS threads.
"""
import os, sys, json, math, time
os.environ.setdefault('OMP_NUM_THREADS', '2'); os.environ.setdefault('OPENBLAS_NUM_THREADS', '2'); os.environ.setdefault('MKL_NUM_THREADS', '2')
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
os.makedirs(DATA, exist_ok=True)
QUICK = '--quick' in sys.argv
SIZES = {64: 4000, 128: 2000, 256: 800}
if QUICK: SIZES = {k: v // 4 for k, v in SIZES.items()}
TWO_PI = 2*math.pi

def haar_unitary(n, rng):
    z = (rng.standard_normal((n, n)) + 1j*rng.standard_normal((n, n)))/math.sqrt(2)
    q, r = np.linalg.qr(z)
    d = np.diag(r); ph = d/np.abs(d)
    return q*ph  # column j multiplied by phase_j  (Mezzadri's correction)

def cue_angles(n, rng):
    ev = np.linalg.eigvals(haar_unitary(n, rng))
    return np.sort(np.angle(ev) % TWO_PI)

def stiffness(theta):
    """Return delta_min, a, b, S_star (literal), S_star (circular form), S_old, d3, near_share."""
    n = len(theta)
    gaps = np.diff(np.append(theta, theta[0] + TWO_PI))       # gap i = theta_{i+1} - theta_i (cyclic)
    i = int(np.argmin(gaps)); delta = float(gaps[i])
    b = i; a = (i + 1) % n                                      # theta_a = theta_b + delta (mod 2pi), a counterclockwise of b
    mask = np.ones(n, bool); mask[[a, b]] = False
    th_k = theta[mask]
    xb = (theta[b] - th_k) % TWO_PI; xa = (theta[a] - th_k) % TWO_PI
    csc2 = lambda x: 1.0/np.sin(x/2)**2
    S_star = float(0.5*np.sum(np.maximum(csc2(xb), csc2(xa))))
    S_old = float(0.5*np.sum(csc2(xb)))
    dist = lambda x: np.minimum(x, TWO_PI - x)
    dk = np.minimum(dist(xb), dist(xa))
    S_circ = float(0.5*np.sum(csc2(dk)))
    d3 = float(dk.min())
    near = float(0.5*np.sum(csc2(dk[dk <= 4.0/n]))/S_star) if S_star > 0 else 0.0
    return delta, a, b, S_star, S_circ, S_old, d3, near

def tail_exponent(y, y0):
    """MLE of alpha in P(Y<=y) ~ (y/y0)^alpha on {y <= y0}; returns (alpha, k)."""
    ys = y[y <= y0]
    k = len(ys)
    if k < 5: return float('nan'), k
    return k/np.sum(np.log(y0/ys)), k

def main():
    rng = np.random.default_rng(20260905)
    summary = {}; arrays = {}
    for n, m in SIZES.items():
        t0 = time.time()
        rec = np.zeros((m, 8))
        for s in range(m):
            th = cue_angles(n, rng)
            rec[s] = stiffness(th)
        delta, S_star, S_circ, S_old, d3, near = rec[:, 0], rec[:, 3], rec[:, 4], rec[:, 5], rec[:, 6], rec[:, 7]
        assert np.allclose(S_star, S_circ, rtol=1e-9), 'wrap-around/circular-distance identity violated'
        A = S_star/n**2; y = n*d3; x = n**(4/3)*delta
        out = {
            'samples': m, 'seconds': round(time.time() - t0, 1),
            'S_star_over_N2': {'median': float(np.median(A)), 'mean': float(A.mean()), 'q90': float(np.quantile(A, .9)),
                               'q99': float(np.quantile(A, .99)), 'max': float(A.max()), 'min': float(A.min())},
            'S_old_over_N2': {'median': float(np.median(S_old/n**2)), 'q99': float(np.quantile(S_old/n**2, .99)),
                              'max': float((S_old/n**2).max())},
            'frac_S_star_gt_N2logN': float(np.mean(S_star > n**2*math.log(n))),
            'logN': math.log(n),
            'frac_S_star_gt_M_N2': {str(M): float(np.mean(A > M)) for M in (0.25, 0.5, 1.0, 2.0)},
            'N_d3_quantiles': {str(q): float(np.quantile(y, q)) for q in (0.001, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9)},
            'P_Nd3_le_c_empirical': {str(c): float(np.mean(y <= c)) for c in (1, 2, 3, 4, 5, 6)},
            'P_Nd3_le_c_prediction_c5_over_3600pi': {str(c): c**5/(3600*math.pi) for c in (1, 2, 3, 4, 5, 6)},
            'share_of_S_star_from_nearest_third_point_2_over_d3sq': {
                'median': float(np.median((2/d3**2)/S_star)), 'q10': float(np.quantile((2/d3**2)/S_star, .1))},
            'share_of_S_star_from_points_within_4_over_N': {'median': float(np.median(near)), 'q90': float(np.quantile(near, .9))},
            'N43_delta_min_survival': {str(xx): {'empirical': float(np.mean(x > xx)), 'BAB_exp(-x^3/72pi)': math.exp(-xx**3/(72*math.pi))}
                                       for xx in (1.0, 2.0, 3.0, 4.0, 5.0)},
            'N43_delta_min_mean': float(x.mean()),
        }
        # lower-tail exponent of N d3 at several thresholds + bootstrap CI at the main one
        te = {}
        for y0 in (2.5, 3.0, 3.5, 4.0):
            al, k = tail_exponent(y, y0); te[str(y0)] = {'alpha_hat': float(al), 'k': int(k)}
        y0 = 3.5
        boots = []
        for _ in range(400):
            yb = rng.choice(y, size=len(y), replace=True); al, k = tail_exponent(yb, y0)
            if not math.isnan(al): boots.append(al)
        te['bootstrap_y0=3.5'] = {'ci90': [float(np.quantile(boots, .05)), float(np.quantile(boots, .95))]} if boots else None
        out['Nd3_lower_tail_exponent_MLE'] = te
        summary[str(n)] = out
        arrays[f'N{n}_delta_min'] = delta; arrays[f'N{n}_S_star'] = S_star; arrays[f'N{n}_S_old'] = S_old; arrays[f'N{n}_d3'] = d3
        print(f'N={n}  m={m}  {out["seconds"]}s  S*/N^2 median={out["S_star_over_N2"]["median"]:.4f} '
              f'q99={out["S_star_over_N2"]["q99"]:.4f} max={out["S_star_over_N2"]["max"]:.4f}  '
              f'frac(S*>N^2 logN)={out["frac_S_star_gt_N2logN"]}  '
              f'Nd3: q01={out["N_d3_quantiles"]["0.01"]:.3f} q10={out["N_d3_quantiles"]["0.1"]:.3f} med={out["N_d3_quantiles"]["0.5"]:.3f}  '
              f'tail alpha(y0=3.5)={te["3.5"]["alpha_hat"]:.2f} (k={te["3.5"]["k"]})', flush=True)
    # pooled tail exponent (N d3 is asymptotically N-free at leading order)
    ypool = np.concatenate([arrays[f'N{n}_d3']*n for n in SIZES])
    pooled = {str(y0): dict(zip(('alpha_hat', 'k'), map(float, tail_exponent(ypool, y0)))) for y0 in (2.0, 2.5, 3.0, 3.5, 4.0)}
    summary['pooled_Nd3_tail_exponent'] = pooled
    summary['pooled_P_Nd3_le_c'] = {str(c): float(np.mean(ypool <= c)) for c in (1, 2, 3, 4, 5, 6)}
    print('pooled tail exponents:', pooled)
    print('pooled P(N d3 <= c):', summary['pooled_P_Nd3_le_c'])
    with open(os.path.join(DATA, 'r1_cue_background_mc.json'), 'w') as f: json.dump(summary, f, indent=1)
    np.savez_compressed(os.path.join(DATA, 'r1_cue_background_mc_samples.npz'), **arrays)
    print('saved to', DATA)

if __name__ == '__main__':
    main()
