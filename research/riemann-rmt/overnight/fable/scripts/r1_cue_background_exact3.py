#!/usr/bin/env python3
"""
r1_cue_background_exact3.py -- exact finite-N prediction for the third-point law (task A2, section 7).

For a pair of CUE(N) points at -u/2, +u/2 the conditional intensity of a third point at position v
(measured from the MIDPOINT of the pair) is rho_3(-u/2, u/2, v)/rho_2(-u/2, u/2), computed here from
the exact 3x3 and 2x2 sine-kernel determinants (no expansion).  We integrate it over |v| <= c/N and
average over the gap u of the min-gap pair using the Ben Arous-Bourgade density
f(x) = (x^2/(24 pi)) exp(-x^3/(72 pi)) for x = N^{4/3} u (whose first moment is proved in the .md):

   P_pred(N v_mid <= c) = int f(x) dx  int_{|v|<=c/N} rho_3/rho_2 dv,     u = x N^{-4/3}.

Also printed: the leading-order law c^5/(3600 pi), the local log-slope d log P / d log c of the exact
prediction (the "local exponent" that a lower-tail MLE sees), and the same for the nearest-endpoint
variable d_3 = v - u/2 (exponent between 3 and 5 depending on c/(N u)).
Output: ../data/r1_cue_background_exact3.json.   Runtime: seconds.
"""
import json, math, os
import numpy as np
from scipy import integrate

HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data')

def K(n, d):
    return n/(2*math.pi) if abs(d) < 1e-13 else math.sin(n*d/2)/(2*math.pi*math.sin(d/2))

def rho(n, xs):
    return float(np.linalg.det(np.array([[K(n, a-b) for b in xs] for a in xs])))

def cond_intensity(n, u, v):
    """rho_3(-u/2,u/2,v)/rho_2(-u/2,u/2) -- third point at midpoint offset v."""
    r2 = rho(n, [-u/2, u/2])
    return rho(n, [-u/2, u/2, v])/r2

def P_mid(n, u, c):
    """expected number of third points with |v| <= c/N (midpoint distance), given the pair; excludes the
    forbidden zone |v| < u/2 automatically (rho_3 vanishes there only at v = +-u/2; between the two
    points a third point would contradict the min-gap property, so we integrate |v| >= u/2 only)."""
    w = c/n
    if w <= u/2: return 0.0
    val, _ = integrate.quad(lambda v: cond_intensity(n, u, v), u/2, w, limit=200)
    return 2*val

def P_d3(n, u, c):
    """same, nearest-endpoint variable d3 = |v| - u/2 <= c/N."""
    return P_mid(n, u, c + n*u/2)

def bab_density(x): return x*x/(24*math.pi)*math.exp(-x**3/(72*math.pi))

def averaged(n, c, fn):
    val, _ = integrate.quad(lambda x: bab_density(x)*fn(n, x*n**(-4/3), c), 0, 14, limit=100)
    return val

out = {'leading_order_c5_over_3600pi': {str(c): c**5/(3600*math.pi) for c in (1, 2, 3, 4, 5)}}
for n in (64, 128, 256):
    row = {}
    for c in (1, 2, 3, 4, 5):
        pm = averaged(n, c, P_mid); pd = averaged(n, c, P_d3)
        # local log-slopes
        h = 0.05
        sm = (math.log(averaged(n, c*(1+h), P_mid)) - math.log(averaged(n, c*(1-h), P_mid)))/(math.log(1+h)-math.log(1-h))
        sd = (math.log(averaged(n, c*(1+h), P_d3)) - math.log(averaged(n, c*(1-h), P_d3)))/(math.log(1+h)-math.log(1-h))
        row[str(c)] = {'P_mid_exact': pm, 'P_d3_exact': pd, 'local_exponent_mid': sm, 'local_exponent_d3': sd}
        print(f'N={n} c={c}: P(N v_mid<=c) exact={pm:.5f} (leading {c**5/(3600*math.pi):.5f}), local exp {sm:.2f} | '
              f'P(N d3<=c) exact={pd:.5f}, local exp {sd:.2f}', flush=True)
    # also: u -> 0 limit check of the leading constant at c=1: P_mid(n, u->0, 1)*3600 pi -> 1 (up to (N v)^2 corrections)
    row['check_u_to_0_c1_times_3600pi'] = P_mid(n, 1e-4*n**(-4/3), 1.0)*3600*math.pi
    row['check_u_to_0_c0.3_times_3600pi_over_c5'] = P_mid(n, 1e-4*n**(-4/3), 0.3)*3600*math.pi/0.3**5
    print(f'N={n}: u->0 checks (should -> 1 as c -> 0): c=1: {row["check_u_to_0_c1_times_3600pi"]:.4f}, c=0.3: {row["check_u_to_0_c0.3_times_3600pi_over_c5"]:.4f}')
    out[str(n)] = row
with open(os.path.join(DATA, 'r1_cue_background_exact3.json'), 'w') as f: json.dump(out, f, indent=1)
print('saved')
