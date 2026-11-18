"""r2_lr_pair_profile.py -- s*(c) profile of the pair LP for several discretisations.

For each grid (X, dx, A, dalpha) prints the minimal slack s*(c) on a fixed c-list, so that the
feasibility wall can be located robustly (threshold crossings at 1e-6, 1e-5, 1e-4, 1e-3) and the
convergence in X, dx, A, dalpha judged.  Usage: python3 r2_lr_pair_profile.py X dx A dalpha
"""
import sys, json, time
import numpy as np
sys.path.insert(0, '.')
from r2_lr_pair_lp import solve
X, dx, A, dal = [float(v) for v in sys.argv[1:5]]
cs = [0.50, 0.505, 0.51, 0.515, 0.5175, 0.52, 0.5225, 0.525, 0.53, 0.54, 0.55, 0.56, 0.58, 0.60, 0.6069, 0.62]
t0 = time.time(); prof = {}
for c in cs:
    r = solve(c, X, dx, A, dal); prof[c] = r['s']
    print(f"X={X} dx={dx} A={A} da={dal}  c={c:.4f}  s*={r['s']:.3e}   ({time.time()-t0:.0f}s)", flush=True)
json.dump(dict(X=X, dx=dx, A=A, dalpha=dal, profile=prof),
          open(f"/home/user/Alpha-devbox/research/riemann-rmt/overnight/fable/data/r2_lr_pair_profile_X{X}_dx{dx}_A{A}_da{dal}.json", "w"), indent=1)
