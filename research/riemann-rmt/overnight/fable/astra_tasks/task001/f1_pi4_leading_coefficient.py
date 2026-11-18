"""Repair-pass addendum (F1 repair, refuter finding on claim F1-3): directly, numerically verify that
Pi_4(1+eps) := sum_p (log p)^4 rho_p(1+eps) (1 - rho_p(1+eps))  has leading coefficient 6a (ONE power of
a), not 6a^2 (two powers), as eps -> 0+, by summing over the ACTUAL primes (no zeta-function shortcut,
unlike f1_sd_expansion.py's h4_zeta_part, which only established the pure-zeta, a-independent "6").

rho_p(s) = 1 - 1/E_p(s), E_p(s) = sum_{e>=1} d_ell(p^e)^2 p^{-es}  (same definitions as f1_common.py /
f1_selberg_delange_expansion.py; NOT modifying either file).

This is a NEW file, written only in this repair pass; it does not modify f1_selberg_delange_expansion.py
or its results/log (which still hardcode m4 = a*a+6*a as a literal, per the refuter's valid finding).
Runs in well under a minute (primes to 2*10^6, five eps values, no large sieve of d_ell(n)/S(n) needed).
"""
from __future__ import annotations
import json, time
from pathlib import Path
import numpy as np
from math import log

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from f1_common import ELL, primes_upto, d_ell_powers

t0 = time.time()
ell = ELL
a = ell * ell
P = 2 * 10 ** 6
emax = 60
ps = primes_upto(P).astype(float)
lp = np.log(ps)
de = d_ell_powers(ell, emax)

def Ep(eps):
    s = 1.0 + eps
    inv_s = ps ** (-s)
    pe = np.ones_like(ps)
    E = np.zeros_like(ps)
    for e in range(1, emax + 1):
        pe = pe * inv_s
        E += de[e] ** 2 * pe
    return E

rows = []
for eps in (1.0, 0.5, 0.25, 0.125, 0.0625):
    E = Ep(eps)
    rho = E / (1.0 + E)
    Pi4 = float(np.sum(lp ** 4 * rho * (1 - rho)))
    Pi2 = float(np.sum(lp ** 2 * rho))
    scaled4 = Pi4 * eps ** 4
    scaled2 = Pi2 * eps ** 2
    rows.append({"eps": eps, "cutoff_e^(1/eps)": float(np.exp(1 / eps)), "Pi4*eps^4": scaled4,
                 "Pi2*eps^2": scaled2, "target_6a": 6 * a, "target_a": a,
                 "ratio_Pi4eps4_over_6a": scaled4 / (6 * a), "ratio_Pi2eps2_over_a": scaled2 / a})
    print(f"eps={eps:7.4f}  Pi4*eps^4={scaled4:9.4f} (target 6a={6*a:.4f}, ratio {scaled4/(6*a):.4f})  "
          f"Pi2*eps^2={scaled2:7.4f} (target a={a:.4f}, ratio {scaled2/a:.4f})  cutoff~e^(1/eps)={np.exp(1/eps):.3e}",
          flush=True)

# Also show what the (wrong) 6a^2 hypothesis would predict, for contrast.
wrong_target = 6 * a * a
out = {
    "purpose": "direct prime-sum (no zeta shortcut) check that Pi_4(1+eps)*eps^4 -> 6a (one power of a), "
               "not 6a^2 (two powers), refuting the .md's original mis-stated prose and closing the gap "
               "the refuter identified (m4's coefficient was previously only a hardcoded literal, never "
               "independently derived by any script for its OWN sake, only for a=6a^2 pattern check).",
    "a": a, "6a": 6 * a, "6a^2_wrong_hypothesis": wrong_target, "P_primes_upto": P, "emax": emax,
    "rows": rows,
    "interpretation": "As eps shrinks (while e^(1/eps) stays within the prime cutoff P so the truncated sum "
                       "still resolves the asymptotic), Pi4*eps^4 should approach 6a=%.4f, not 6a^2=%.4f. "
                       "Pi2*eps^2 is shown alongside as a control: it should approach a=%.4f (already used "
                       "and confirmed elsewhere in the project for kappa1/pi0), confirming the sieve/summation "
                       "method itself is sound." % (6 * a, wrong_target, a),
    "seconds": time.time() - t0,
}
Path(__file__).with_name("f1_pi4_leading_coefficient_results.json").write_text(json.dumps(out, indent=2, default=str))
print("done", f"{time.time()-t0:.1f}s")
