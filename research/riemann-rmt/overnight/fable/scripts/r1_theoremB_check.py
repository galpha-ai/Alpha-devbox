#!/usr/bin/env python3
"""r1_theoremB_check.py -- numerics for the repaired Theorem B (Fable overnight, task A1).

Conventions (as in research/riemann-rmt/depth_scaling_theorem.md): roots e^{i theta_j},
flow P_s(z) = sum_j a_j e^{s j(N-j)} z^j with s >= 0, root ODE
    theta_j' = - sum_{k != j} cot((theta_j - theta_k)/2),
depth D = first collision time.  For the minimum-gap pair (a,b) (theta_a = theta_b + g,
a counter-clockwise of b) and k != a,b:  x_j^k = (theta_j - theta_k) mod 2pi in (0,2pi),
x_a^k = x_b^k + g;  y_k = 2pi - x_a^k (ccw arc a -> k),  w_k = x_b^k (ccw arc k -> b),
rho_k = min(y_k, w_k) = dist(theta_k, {theta_a, theta_b}).

What it does
------------
1. Reproduces Astra's counterexample to the old endpoint bound (g = .05, x_b = 2pi - .15).
2. Samples CUE (Haar unitary = QR of complex Ginibre with the Mezzadri phase fix) at
   N = 16, 32, 64 and ACUE-type lattice configurations (random non-clock N-subsets of the
   2N-th roots of unity, plus the single-dislocation configuration), and for the min-gap
   pair computes
     B       = sum_k [cot(x_b^k/2) - cot(x_a^k/2)]                 (exact background bracket, >= 0)
     B_exact = sin(g/2) sum_k 1/(sin(x_b^k/2) sin(x_a^k/2))         (must equal B)
     S_old   = sum_k 1/2 csc^2(x_b^k/2)                              (old, wrong)
     S*      = sum_k 1/2 max(csc^2(x_b^k/2), csc^2(x_a^k/2))         (repaired)
     S_avg   = sum_k 1/4 (csc^2(x_b^k/2) + csc^2(x_a^k/2))           (AM-GM refinement)
     S_exact = sum_k 1/2 / (sin(x_b^k/2) sin(x_a^k/2))               (B = 2 sin(g/2) S_exact)
   and reports how often B <= g S_old fails and that B <= g S_exact <= g S_avg <= g S* never fails.
3. Integrates the root ODE with scipy.solve_ivp (DOP853, rtol 1e-12, terminal event at min gap = 1e-5 delta,
   then adds the exact two-body residual -log cos(g_end/2)) to get D; cross-checks with the
   polynomial method dyn1_core.find_ustar (first root leaving the unit circle; double precision,
   usable only for N <= 32) and with a 40-digit mpmath bracket certificate (all roots on the circle at
   D(1-rel), a root off the circle at D(1+rel)) for the first --n-cert samples; compares D with
   delta^2/8, -log cos(delta/2) and the repaired closed form
       T(mu) = -log(1 - mu delta^2/4) / (2 mu),   mu = A N^2 + kappa_0,  kappa_0 = kappa(delta/2),
       kappa(x) = (1 - x cot x)/x^2,
   for A N^2 = S*(0) (empirical), 2 S*(0) (rigorous under the window lemma) and
   sup_{window} S*(s) (must always bound D).
4. Records max_s S*(s)/S*(0) over the window, the second-smallest gap ratio g_(2)/delta, the
   one-sided density constant C_emp = max_n n/(N y_(n)) (both sides) and tests the window
   lemma's sufficient condition  sqrt(2) C N delta <= 1 - 1/sqrt(2).
5. An adversarial 3-cluster example where S*(s)/S*(0) exceeds 2 (hypothesis violated).

Usage:  python3 r1_theoremB_check.py [--n-cue 300] [--n-acue 100] [--seed 1] [--quick]
Output: ../data/r1_theoremB_check.json (summary + per-sample records); tables on stdout.
"""
import argparse, json, math, os, sys, time
import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
RR = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(RR, 'riemann-impostors', 'counterexamples'))
import dyn1_core  # noqa: E402

TWO_PI = 2 * math.pi
ETA_STAR = 1 - 1 / math.sqrt(2)        # 0.2929: relative shrinkage allowed for a factor-2 growth of S*


# ----------------------------------------------------------------------------- sampling
def haar_unitary(N, rng):
    Z = (rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))) / math.sqrt(2)
    Q, R = np.linalg.qr(Z)
    d = np.diag(R)
    return Q * (d / np.abs(d))[None, :]


def cue_angles(N, rng):
    ev = np.linalg.eigvals(haar_unitary(N, rng))
    return np.sort(np.angle(ev) % TWO_PI)


def acue_random_slots(N, rng):
    while True:
        slots = np.sort(rng.choice(2 * N, N, replace=False))
        if not np.all(np.diff(np.concatenate([slots, [slots[0] + 2 * N]])) == 2):
            return slots


def dislocation_slots(N):
    return np.array([1] + [2 * j for j in range(1, N)])


def slots_to_angles(slots, N):
    return np.sort((math.pi * np.asarray(slots) / N) % TWO_PI)


# ----------------------------------------------------------------------------- pair statistics
def cyc_gaps(th):
    return np.diff(np.concatenate([th, [th[0] + TWO_PI]]))


def kappa(x):
    """kappa(x) = (1 - x cot x)/x^2, increasing on (0,pi), kappa(0+) = 1/3, kappa(pi/2) = 4/pi^2."""
    return (1 - x / math.tan(x)) / x ** 2


def T_bound(mu, delta):
    """Repaired closed form  T(mu) = -log(1 - mu delta^2/4)/(2 mu);  +inf if mu delta^2 >= 4."""
    y = mu * delta ** 2 / 4
    if y >= 1:
        return math.inf
    return -math.log1p(-y) / (2 * mu)


def pair_stats(th, b=None):
    """th sorted ascending. Statistics of the adjacent pair (b, a = b+1); default b = argmin gap."""
    N = len(th)
    gaps = cyc_gaps(th)
    if b is None:
        b = int(np.argmin(gaps))
    a = (b + 1) % N
    g = float(gaps[b])
    mask = np.ones(N, bool)
    mask[[a, b]] = False
    tk = th[mask]
    xa = (th[a] - tk) % TWO_PI
    xb = (th[b] - tk) % TWO_PI
    assert np.all((xa > 0) & (xa < TWO_PI) & (xb > 0) & (xb < TWO_PI))
    assert np.max(np.abs(xa - xb - g)) < 1e-9, "x_a^k = x_b^k + g fails"
    y = TWO_PI - xa
    w = xb
    rho = np.minimum(y, w)
    csc2 = lambda x: 1.0 / np.sin(x / 2) ** 2
    B = float(np.sum(1 / np.tan(xb / 2) - 1 / np.tan(xa / 2)))
    B_exact = float(math.sin(g / 2) * np.sum(1 / (np.sin(xb / 2) * np.sin(xa / 2))))
    S_old = float(0.5 * np.sum(csc2(xb)))
    S_star = float(0.5 * np.sum(np.maximum(csc2(xb), csc2(xa))))
    S_star_rho = float(0.5 * np.sum(csc2(rho)))          # identity S* = 1/2 sum csc^2(rho_k/2)
    S_avg = float(0.25 * np.sum(csc2(xb) + csc2(xa)))
    S_exact = float(0.5 * np.sum(1 / (np.sin(xb / 2) * np.sin(xa / 2))))
    r = float(rho.min())
    n = np.arange(1, N - 1)
    C_emp = float(max((n / (N * np.sort(y))).max(), (n / (N * np.sort(w))).max()))
    g2 = float(np.sort(gaps)[1])
    return dict(a=a, b=b, g=g, B=B, B_exact=B_exact, S_old=S_old, S_star=S_star, S_star_rho=S_star_rho,
                S_avg=S_avg, S_exact=S_exact, r=r, C_emp=C_emp, g2=g2)


def S_star_of(th, a, b):
    N = len(th)
    mask = np.ones(N, bool)
    mask[[a, b]] = False
    tk = th[mask]
    xa = (th[a] - tk) % TWO_PI
    xb = (th[b] - tk) % TWO_PI
    return float(0.5 * np.sum(np.maximum(1 / np.sin(xb / 2) ** 2, 1 / np.sin(xa / 2) ** 2)))


# ----------------------------------------------------------------------------- dynamics
def rhs(s, th):
    d = th[:, None] - th[None, :]
    np.fill_diagonal(d, math.pi)          # cot(pi/2) = 0 -> the diagonal drops out
    return -np.sum(1 / np.tan(d / 2), axis=1)


def depth_ode(th0, a, b, eps_rel=1e-5, rtol=1e-12, atol=1e-15, horizon_factor=10.0):
    """Depth by integrating the root ODE.  Returns (D, S*_sup over accepted steps, S*_end, n_steps,
    colliding_pair_is_ab)."""
    delta = float(cyc_gaps(th0).min())
    eps = eps_rel * delta

    def ev(s, th):
        return cyc_gaps(th).min() - eps
    ev.terminal = True
    ev.direction = -1
    sol = solve_ivp(rhs, (0.0, horizon_factor * delta ** 2), th0, method='DOP853',
                    rtol=rtol, atol=atol, events=ev)
    if len(sol.t_events[0]) == 0:
        return math.nan, math.nan, math.nan, len(sol.t), False
    th_end = sol.y_events[0][0]
    gaps_end = cyc_gaps(th_end)
    g_end = gaps_end.min()
    D = float(sol.t_events[0][0] - math.log(math.cos(g_end / 2)))
    Ss = [S_star_of(sol.y[:, i], a, b) for i in range(sol.y.shape[1])]
    S_end = S_star_of(th_end, a, b)
    S_sup = max(max(Ss), S_end)
    ab_first = int(np.argmin(gaps_end)) == b
    return D, S_sup, S_end, len(sol.t), ab_first


def depth_poly(th0):
    """Depth by the polynomial method of dyn1_core (first root off the unit circle).
    np.poly gives prod(z - z_j) in descending powers = prod(1 - z_j z) in ascending powers."""
    coef = np.poly(np.exp(1j * th0))
    N = len(th0)
    off0 = dyn1_core.offcircle(coef, 0.0, N)
    us, lo, hi = dyn1_core.find_ustar(coef, N)
    return (math.nan if us is None else float(us)), float(off0)


def mp_offcircle(th, u, dps=40):
    """High-precision check: max_j | |z_j(u)| - 1 | over the roots of P_u, coefficients built exactly
    (at dps digits) from the given angles.  Before the first collision this is 0 (self-inversive)."""
    import mpmath as mp
    with mp.workdps(dps):
        z = [mp.expjpi(mp.mpf(t) / mp.pi) for t in th]
        a = [mp.mpc(1)]
        for zj in z:
            a = [(a[k] if k < len(a) else 0) - zj * (a[k - 1] if k >= 1 else 0) for k in range(len(a) + 1)]
        n = len(th)
        # NOTE: the exponent must be formed in mp arithmetic with the exact integer j(n-j): the double
        # product (u*j)*(n-j) differs from (u*(n-j))*j by an ulp, which breaks the self-inversive
        # symmetry of P_u at the 1e-11 level and (divided by |P'| ~ 1e-8 at a lattice cluster) throws
        # roots 1e-4 off the circle.  This was the cause of two spurious certificate failures.
        um = mp.mpf(u)
        c = [a[j] * mp.exp(um * (j * (n - j))) for j in range(n + 1)]
        roots, err = mp.polyroots(c[::-1], maxsteps=400, extraprec=200, error=True)
        return float(max(abs(abs(r) - 1) for r in roots)), float(err)


def mp_bracket_certificate(th, D, rels=(1e-6, 1e-5, 1e-4), dps=40):
    """Certificate that the true depth lies in [D(1-rel), D(1+rel)]: every root on the circle at the
    lower end (off < 1e-20) and some root off the circle at the upper end (off > 1e-8).  Tries the
    relative widths in `rels` in order and reports the first that certifies."""
    out = None
    for rel in rels:
        off_lo, err_lo = mp_offcircle(th, D * (1 - rel), dps)
        off_hi, err_hi = mp_offcircle(th, D * (1 + rel), dps)
        out = dict(rel=rel, off_lo=off_lo, off_hi=off_hi, polyroots_err=max(err_lo, err_hi),
                   certified=(off_lo < 1e-20 and off_hi > 1e-8))
        if out['certified']:
            break
    return out


# ----------------------------------------------------------------------------- one sample
def analyse(th, label, N, want_poly=True):
    ps = pair_stats(th)
    a, b, g = ps['a'], ps['b'], ps['g']
    delta = g
    k0 = kappa(delta / 2)
    D, S_sup, S_end, nsteps, ab_first = depth_ode(th, a, b)
    Dp, off0 = depth_poly(th) if (want_poly and N <= 32) else (math.nan, math.nan)
    rec = dict(label=label, N=N, delta=delta, g2=ps['g2'], r=ps['r'], C_emp=ps['C_emp'],
               B=ps['B'], B_exact=ps['B_exact'], S_old=ps['S_old'], S_star=ps['S_star'],
               S_star_rho=ps['S_star_rho'], S_avg=ps['S_avg'], S_exact=ps['S_exact'],
               kappa0=k0, D_ode=D, D_poly=Dp, off0=off0, S_sup=S_sup, S_end=S_end,
               n_steps=nsteps, ab_first=ab_first,
               lb_two_body=-math.log(math.cos(delta / 2)), lb_quadratic=delta ** 2 / 8,
               T_emp=T_bound(ps['S_star'] + k0, delta),
               T_rig=T_bound(2 * ps['S_star'] + k0, delta),
               T_sup=T_bound((S_sup if np.isfinite(S_sup) else math.inf) + k0, delta),
               H1=(ps['g2'] >= 2 * delta),
               HC=(math.sqrt(2) * ps['C_emp'] * N * delta <= ETA_STAR))
    return rec


# ----------------------------------------------------------------------------- summaries
def q(v, p):
    v = np.asarray([x for x in v if np.isfinite(x)])
    return float(np.quantile(v, p)) if len(v) else math.nan


def summarise(recs):
    out = {}
    N = recs[0]['N']
    n = len(recs)
    g = np.array([r['delta'] for r in recs])
    B = np.array([r['B'] for r in recs])
    Bx = np.array([r['B_exact'] for r in recs])
    So = np.array([r['S_old'] for r in recs]); Ss = np.array([r['S_star'] for r in recs])
    Sr = np.array([r['S_star_rho'] for r in recs]); Sa = np.array([r['S_avg'] for r in recs])
    Se = np.array([r['S_exact'] for r in recs])
    out['n'] = n
    out['identity_B_exact_maxrelerr'] = float(np.max(np.abs(B - Bx) / B))
    out['identity_Sstar_rho_maxrelerr'] = float(np.max(np.abs(Ss - Sr) / Ss))
    out['frac_old_fails'] = float(np.mean(B > g * So * (1 + 1e-12)))
    out['max_B_over_gSold'] = float(np.max(B / (g * So)))
    out['frac_star_fails'] = float(np.mean(B > g * Ss * (1 + 1e-12)))
    out['min_gSstar_over_B'] = float(np.min(g * Ss / B))
    out['frac_avg_fails'] = float(np.mean(B > g * Sa * (1 + 1e-12)))
    out['min_gSavg_over_B'] = float(np.min(g * Sa / B))
    out['min_gSexact_over_B'] = float(np.min(g * Se / B))
    out['Sstar_over_N2'] = dict(median=q(Ss / N ** 2, .5), q99=q(Ss / N ** 2, .99), max=float(np.max(Ss / N ** 2)))
    out['Sold_over_N2_median'] = q(So / N ** 2, .5)
    D = np.array([r['D_ode'] for r in recs]); Dp = np.array([r['D_poly'] for r in recs])
    ok = np.isfinite(D)
    out['n_D_ode'] = int(ok.sum())
    okp = ok & np.isfinite(Dp)
    out['n_D_poly'] = int(okp.sum())
    out['max_rel_disc_ode_poly'] = float(np.max(np.abs(D[okp] - Dp[okp]) / D[okp])) if okp.any() else math.nan
    out['median_rel_disc_ode_poly'] = q(np.abs(D[okp] - Dp[okp]) / D[okp], .5) if okp.any() else math.nan
    lb2 = np.array([r['lb_two_body'] for r in recs]); lbq = np.array([r['lb_quadratic'] for r in recs])
    out['D_over_quadratic'] = dict(min=float(np.min(D[ok] / lbq[ok])), median=q(D[ok] / lbq[ok], .5), max=float(np.max(D[ok] / lbq[ok])))
    out['D_over_twobody'] = dict(min=float(np.min(D[ok] / lb2[ok])), median=q(D[ok] / lb2[ok], .5), max=float(np.max(D[ok] / lb2[ok])))
    out['N2delta2'] = dict(median=q(N ** 2 * g ** 2, .5), max=float(np.max(N ** 2 * g ** 2)))
    for key in ('T_emp', 'T_rig', 'T_sup'):
        T = np.array([r[key] for r in recs])
        fin = ok & np.isfinite(T)
        out[key] = dict(frac_vacuous=float(np.mean(~np.isfinite(T[ok]))),
                        frac_violated=float(np.mean(D[fin] > T[fin] * (1 + 1e-9))) if fin.any() else math.nan,
                        min_T_over_D=float(np.min(T[fin] / D[fin])) if fin.any() else math.nan,
                        median_T_over_D=q(T[fin] / D[fin], .5) if fin.any() else math.nan,
                        max_T_over_D=float(np.max(T[fin] / D[fin])) if fin.any() else math.nan)
    ratio = np.array([r['S_sup'] / r['S_star'] for r in recs])
    out['Ssup_over_S0'] = dict(median=q(ratio[ok], .5), q90=q(ratio[ok], .9), max=float(np.max(ratio[ok])),
                               frac_gt_2=float(np.mean(ratio[ok] > 2)))
    H1 = np.array([r['H1'] for r in recs]); HC = np.array([r['HC'] for r in recs])
    out['frac_H1'] = float(np.mean(H1)); out['frac_HC'] = float(np.mean(HC))
    out['max_ratio_given_H1'] = float(np.max(ratio[ok & H1])) if (ok & H1).any() else math.nan
    out['max_ratio_given_HC'] = float(np.max(ratio[ok & HC])) if (ok & HC).any() else math.nan
    out['frac_ab_first'] = float(np.mean([r['ab_first'] for r in recs if np.isfinite(r['D_ode'])]))
    out['C_emp'] = dict(median=q([r['C_emp'] for r in recs], .5), q90=q([r['C_emp'] for r in recs], .9), max=float(np.max([r['C_emp'] for r in recs])))
    out['g2_over_delta_median'] = q([r['g2'] / r['delta'] for r in recs], .5)
    out['Nr'] = dict(median=q([N * r['r'] for r in recs], .5), min=float(np.min([N * r['r'] for r in recs])))
    out['n_steps_median'] = q([r['n_steps'] for r in recs], .5)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n-cue', type=int, default=300)
    ap.add_argument('--n-acue', type=int, default=100)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--quick', action='store_true')
    ap.add_argument('--n-cert', type=int, default=5, help='samples per ensemble given the mpmath bracket certificate')
    ap.add_argument('--out', default=os.path.join(HERE, '..', 'data', 'r1_theoremB_check.json'))
    args = ap.parse_args()
    if args.quick:
        args.n_cue, args.n_acue, args.n_cert = 20, 10, 1
    rng = np.random.default_rng(args.seed)
    t0 = time.time()
    results = {'args': vars(args), 'summaries': {}, 'records': [], 'special': {}}

    # 1. Astra's counterexample
    g, xb = .05, TWO_PI - .15
    quot = (1 / math.tan(xb / 2) - 1 / math.tan((xb + g) / 2)) / g
    old = .5 / math.sin(xb / 2) ** 2
    new = .5 * max(1 / math.sin(xb / 2) ** 2, 1 / math.sin((xb + g) / 2) ** 2)
    avg = .25 * (1 / math.sin(xb / 2) ** 2 + 1 / math.sin((xb + g) / 2) ** 2)
    exact = math.sin(g / 2) / (g * math.sin(xb / 2) * math.sin((xb + g) / 2))
    results['special']['astra_counterexample'] = dict(g=g, xb=xb, difference_quotient=quot, old_bound=old,
                                                     star_bound=new, avg_bound=avg, exact_identity=exact)
    print(f"[1] Astra counterexample: quotient={quot:.6f}  old={old:.6f} (FAILS)  S*-term={new:.6f}  "
          f"S_avg-term={avg:.6f}  identity={exact:.6f}  |quot-identity|={abs(quot-exact):.2e}")

    # 2-4. ensembles
    plan = [('CUE', N, args.n_cue) for N in (16, 32, 64)] + [('ACUE', N, args.n_acue) for N in (16, 32, 64)]
    for ens, N, n in plan:
        recs = []
        t1 = time.time()
        for i in range(n):
            if ens == 'CUE':
                th = cue_angles(N, rng)
            else:
                th = slots_to_angles(acue_random_slots(N, rng), rng and N)
            rec = analyse(th, ens, N)
            if i < args.n_cert and np.isfinite(rec['D_ode']):
                ps = pair_stats(th)
                D_tight = depth_ode(th, ps['a'], ps['b'], eps_rel=1e-6, rtol=1e-13, atol=1e-16)[0]
                rec['D_tight_reldiff'] = abs(D_tight - rec['D_ode']) / rec['D_ode']
                rec['mp_cert'] = mp_bracket_certificate(th, rec['D_ode'])
            recs.append(rec)
        s = summarise(recs)
        cert = [r for r in recs if 'mp_cert' in r]
        s['n_cert'] = len(cert)
        s['cert_all_pass'] = bool(all(r['mp_cert']['certified'] for r in cert)) if cert else None
        s['cert_max_off_lo'] = float(max(r['mp_cert']['off_lo'] for r in cert)) if cert else None
        s['cert_min_off_hi'] = float(min(r['mp_cert']['off_hi'] for r in cert)) if cert else None
        s['tight_max_reldiff'] = float(max(r['D_tight_reldiff'] for r in cert)) if cert else None
        s['cert_max_rel'] = float(max(r['mp_cert']['rel'] for r in cert)) if cert else None
        s['seconds'] = time.time() - t1
        results['summaries'][f'{ens}_N{N}'] = s
        results['records'].extend(recs)
        print(f"[{ens} N={N} n={n}] done in {s['seconds']:.0f}s: old-bound fails {100*s['frac_old_fails']:.1f}% "
              f"(max B/gS_old={s['max_B_over_gSold']:.3f}); S* fails {100*s['frac_star_fails']:.2f}% "
              f"(min gS*/B={s['min_gSstar_over_B']:.3f}); D/(d^2/8) med={s['D_over_quadratic']['median']:.5f} "
              f"max={s['D_over_quadratic']['max']:.5f}; T_sup/D min={s['T_sup']['min_T_over_D']:.5f}; "
              f"S_sup/S0 max={s['Ssup_over_S0']['max']:.3f}; ode/poly disc max={s['max_rel_disc_ode_poly']:.1e}; "
              f"cert {s['n_cert']} pass={s['cert_all_pass']} (rel<={s['cert_max_rel']:.0e}) off_lo<={s['cert_max_off_lo']:.1e} off_hi>={s['cert_min_off_hi']:.1e} "
              f"tight-tol reldiff<={s['tight_max_reldiff']:.1e}")

    # single dislocation
    disl = []
    for N in (8, 16, 32, 64):
        th = slots_to_angles(dislocation_slots(N), N)
        rec = analyse(th, 'DISLOC', N)
        rec['N2D'] = N ** 2 * rec['D_ode']
        rec['mp_cert'] = mp_bracket_certificate(th, rec['D_ode'])
        disl.append(rec)
        print(f"[DISLOC N={N}] N^2 D={rec['N2D']:.6f}  D/(pi^2/8N^2)={rec['D_ode']/(math.pi**2/8/N**2):.5f}  "
              f"S*/N^2={rec['S_star']/N**2:.4f}  S_sup/S0={rec['S_sup']/rec['S_star']:.3f}  "
              f"mu_emp d^2={ (rec['S_star']+rec['kappa0'])*rec['delta']**2:.3f}  T_emp/D={rec['T_emp']/rec['D_ode']:.4f}  "
              f"T_sup/D={rec['T_sup']/rec['D_ode']:.4f}  mp-cert(1e-6)={rec['mp_cert']['certified']}")
    results['special']['dislocation'] = disl

    # 5. adversarial 3-clusters: min pair (0, delta), third point at (1+t) delta beyond a, N = 8
    N = 8; delta = 0.02
    cl = []
    for t in (0.2, 0.05, 0.01):
        th = np.sort(np.array([0.0, delta, (2 + t) * delta, 1.5, 2.5, 3.5, 4.5, 5.5]))
        rec = analyse(th, 'CLUSTER3', N)
        rec['third_gap_over_delta'] = 1 + t
        rec['note'] = 'g2/delta < 2: window-lemma hypothesis violated; S* may grow by more than 2'
        cl.append(rec)
        print(f"[CLUSTER3 g2={1+t:.2f}delta] D/(d^2/8)={rec['D_ode']/rec['lb_quadratic']:.4f}, "
              f"S_sup/S0={rec['S_sup']/rec['S_star']:.3f}, ab collides first: {rec['ab_first']}, "
              f"T_emp/D={rec['T_emp']/rec['D_ode']:.4f}, T_rig/D={rec['T_rig']/rec['D_ode']:.4f}, T_sup/D={rec['T_sup']/rec['D_ode']:.4f}")
    results['special']['cluster3'] = cl

    results['total_seconds'] = time.time() - t0
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating, float)):
            return None if not np.isfinite(o) else float(o)
        return o
    with open(args.out, 'w') as f:
        json.dump(clean(results), f, indent=1)
    print(f"wrote {os.path.abspath(args.out)}  ({results['total_seconds']:.0f}s)")

    # tables
    print("\nTABLE 1  background bracket at s=0 (min-gap pair)")
    print(f"{'ensemble':>10} {'n':>4} {'old fails':>10} {'max B/gS_old':>13} {'S* fails':>9} {'min gS*/B':>10} "
          f"{'min gS_avg/B':>13} {'min gS_ex/B':>12} {'|B-B_ex|/B':>11} {'med S*/N^2':>11} {'med S_old/N^2':>13}")
    for key, s in results['summaries'].items():
        print(f"{key:>10} {s['n']:>4} {100*s['frac_old_fails']:>9.1f}% {s['max_B_over_gSold']:>13.4f} "
              f"{100*s['frac_star_fails']:>8.2f}% {s['min_gSstar_over_B']:>10.4f} {s['min_gSavg_over_B']:>13.4f} "
              f"{s['min_gSexact_over_B']:>12.6f} {s['identity_B_exact_maxrelerr']:>11.1e} "
              f"{s['Sstar_over_N2']['median']:>11.4f} {s['Sold_over_N2_median']:>13.4f}")
    print("\nTABLE 2  depth D (ODE) vs bounds")
    print(f"{'ensemble':>10} {'n':>4} {'ode/poly':>9} {'mp-cert':>8} {'tight':>8} {'D/(d^2/8) min':>14} {'median':>8} {'max':>8} "
          f"{'D/(-logcos) min':>16} {'med N^2d^2':>11} {'T_emp/D min':>12} {'vac':>5} {'T_rig/D min':>12} {'vac':>5} "
          f"{'T_sup/D min':>12} {'viol':>5}")
    for key, s in results['summaries'].items():
        print(f"{key:>10} {s['n']:>4} {s['max_rel_disc_ode_poly']:>9.1e} "
              f"{str(s['n_cert'])+('/ok' if s['cert_all_pass'] else '/FAIL'):>8} {s['tight_max_reldiff']:>8.1e} "
              f"{s['D_over_quadratic']['min']:>14.5f} "
              f"{s['D_over_quadratic']['median']:>8.5f} {s['D_over_quadratic']['max']:>8.5f} "
              f"{s['D_over_twobody']['min']:>16.6f} {s['N2delta2']['median']:>11.4f} "
              f"{s['T_emp']['min_T_over_D']:>12.5f} {100*s['T_emp']['frac_vacuous']:>4.0f}% "
              f"{s['T_rig']['min_T_over_D']:>12.5f} {100*s['T_rig']['frac_vacuous']:>4.0f}% "
              f"{s['T_sup']['min_T_over_D']:>12.5f} {100*s['T_sup']['frac_violated']:>4.0f}%")
    print("\nTABLE 3  window growth of S* and the lemma's hypotheses")
    print(f"{'ensemble':>10} {'n':>4} {'S_sup/S0 med':>13} {'q90':>7} {'max':>7} {'frac>2':>7} {'frac H1':>8} "
          f"{'max|H1':>8} {'frac HC':>8} {'max|HC':>8} {'med g2/d':>9} {'med C':>7} {'max C':>7} {'med Nr':>7} {'ab first':>9}")
    for key, s in results['summaries'].items():
        print(f"{key:>10} {s['n']:>4} {s['Ssup_over_S0']['median']:>13.4f} {s['Ssup_over_S0']['q90']:>7.3f} "
              f"{s['Ssup_over_S0']['max']:>7.3f} {100*s['Ssup_over_S0']['frac_gt_2']:>6.1f}% {100*s['frac_H1']:>7.1f}% "
              f"{s['max_ratio_given_H1']:>8.3f} {100*s['frac_HC']:>7.1f}% {s['max_ratio_given_HC']:>8.3f} "
              f"{s['g2_over_delta_median']:>9.3f} {s['C_emp']['median']:>7.3f} {s['C_emp']['max']:>7.3f} "
              f"{s['Nr']['median']:>7.3f} {100*s['frac_ab_first']:>8.1f}%")


if __name__ == '__main__':
    main()
