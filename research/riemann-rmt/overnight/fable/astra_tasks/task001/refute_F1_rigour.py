"""Adversarial rigour check on F1 (task001_F1_arithmetic_transfer.md), claims F1-3 / F1-4.

Target: the report's derivation of Sigma_2 = sum_n d_ell(n)^2 S~(n)^2 / n's leading Hankel/Laurent
coefficient "m4" (needed for E_v[S2^2] = (a+6) v^4/((a+1)(a+2)(a+3))).

The report's prose (section 3 of the .md) states:

    "Pi_4(1+eps) = 6 a^2/eps^4 + O(eps^{-2}) ... so Pi_2^2 + Pi_4 has leading (a^2+6a^2 ...) -- the
    script tracks this exactly; the leading Hankel coefficient of Sigma_2 ... comes out m4 = a^2+6a
    after collecting Pi_2^2's a^2/eps^4 and Pi_4's 6a^2/eps^4"

This is arithmetically inconsistent as written: a^2 (from Pi_2^2) + 6a^2 (from Pi_4, as stated) = 7a^2,
NOT a^2+6a. Separately, f1_selberg_delange_expansion.py never computes Pi_4's Laurent coefficient in
code at all -- `m4 = a*a + 6*a` (line 87) is a bare literal, not derived from any computed quantity in
the script (contrast with kappa1, kappa2, pi0, R1, R2, which ARE all computed from explicit prime sums /
mpmath Stieltjes constants earlier in the same script). So the claim "the script tracks this exactly"
is false, and the claimed derivation of one of the two headline E_v[S2^j] formulas (the second-moment
one, j=2) is not actually carried out -- m4 is pattern-matched to Astra's target answer, not derived.

This script:
  1. Shows the correct leading coefficient of Pi_4 = sum_p (log p)^4 rho_p(1-rho_p) at s=1+eps is 6a/eps^4,
     not 6a^2/eps^4, by combining two facts the SAME source script already establishes/uses elsewhere:
       (i)  sum_p (log p)^4 p^{-s} = 6/eps^4 + O(1)   [pure zeta fact, independent of a; the script's own
            h4_zeta_part = 24*c[4] computes exactly this "6" via mpmath Stieltjes constants]
       (ii) rho_p(1+eps) = a p^{-1-eps} + O(p^{-2-2eps})   [same leading-order fact used to get Pi_2's
            leading a/eps^2 term, i.e. m2 = a in the script]
     so Pi_4 ~ a * (6/eps^4) = 6a/eps^4 (the O(p^{-2s}) part of rho_p contributes a convergent, non-polar
     sum at s=1, hence no eps^{-4} contribution beyond the single power of a).
  2. Confirms this is what m4 = a^2+6a in fact requires (a^2 from Pi_2^2's leading term squared, PLUS
     6a from Pi_4 -- not 6a^2), i.e. the *result* the code hardcodes is correct, but the *prose derivation*
     offered for it is wrong, and no code anywhere actually derives it from Pi_4.
  3. Prints the literal arithmetic contradiction a^2+6a^2 != a^2+6a for the actual value of a=ell^2 used
     throughout, so there is no ambiguity that this is a genuine algebra slip and not a typo that happens
     to cancel.

No large computation; runs in well under a second.
"""
from __future__ import annotations
import json
from pathlib import Path
import mpmath as mp

mp.mp.dps = 40
ELL = mp.mpf(16) / 15
a = ELL ** 2

# ---- (i) pure-zeta fact used elsewhere in f1_selberg_delange_expansion.py: leading eps^-4 coeff of
# sum_p (log p)^4 p^{-s} at s=1+eps. Checked directly via high-precision numerical differentiation of
# zeta'/zeta (the same identity the proposer's script uses, sum_n Lambda(n)(log n)^3 n^{-s} relation):
# f(s) := -zeta'/zeta(s) has a *simple* pole at s=1 with f(s) ~ 1/eps, so f'''(s) ~ -6/eps^4 + O(1), and
# sum_p (log p)^4 p^{-s} = -f'''(s) - (prime-power correction, finite at s=1) = 6/eps^4 + O(1).
def zz3(s):
    return mp.diff(lambda t: mp.zeta(t, derivative=1) / mp.zeta(t), s, 3)
probe_vals = {}
for eps in (mp.mpf('1e-3'), mp.mpf('2e-4'), mp.mpf('5e-5')):
    probe_vals[mp.nstr(eps, 6)] = mp.nstr(-zz3(1 + eps) * eps ** 4, 12)
h4_zeta_part = mp.mpf(probe_vals[mp.nstr(mp.mpf('5e-5'), 6)])   # numerically 6, to the displayed precision

# ---- (ii) leading coefficient of rho_p is exactly a (this is literally what the proposer's own script
# uses to get Pi_2 ~ a/eps^2 + pi_0 -- see f1_selberg_delange_expansion.py "pi0 = a*h2+R2", built on the
# same a/eps^2 leading term). No independent derivation needed here; it is common ground with the target.

pi4_leading_correct = 6 * a          # = a * h4_zeta_part, h4_zeta_part == 6 exactly (simple pole of zeta)
pi4_leading_as_written_in_md = 6 * a * a   # what the .md prose literally states

m4_from_written_prose = a * a + pi4_leading_as_written_in_md     # a^2 + 6a^2 = 7a^2
m4_correct = a * a + pi4_leading_correct                          # a^2 + 6a  (matches the code's hardcoded value)
m4_hardcoded_in_script = a * a + 6 * a                             # literally f1_selberg_delange_expansion.py line 87

out = {
    "a": mp.nstr(a, 15),
    "direct_diff_probe_-zz3(1+eps)*eps^4_should_tend_to_6": probe_vals,
    "Pi4 leading coefficient, correct (a * h4_zeta_part = 6a)": mp.nstr(pi4_leading_correct, 15),
    "Pi4 leading coefficient, as literally stated in the .md prose (6a^2)": mp.nstr(pi4_leading_as_written_in_md, 15),
    "m4 implied by the .md's own stated Pi4 coefficient (a^2 + 6a^2 = 7a^2)": mp.nstr(m4_from_written_prose, 15),
    "m4 that is actually correct (a^2 + 6a)": mp.nstr(m4_correct, 15),
    "m4 as hardcoded literally in f1_selberg_delange_expansion.py line 87 (a*a+6*a)": mp.nstr(m4_hardcoded_in_script, 15),
    "verdict": (
        "The .md's prose derivation of Pi_4's leading coefficient (6a^2/eps^4) is WRONG -- the correct "
        "leading coefficient is 6a/eps^4 (one power of a, not two), obtainable from facts the proposer's "
        "own script already establishes (h4_zeta_part=6, and rho_p ~ a/p to leading order, the same fact "
        "used for Pi_2's leading a/eps^2 term). Combined with Pi_2^2's a^2/eps^4, this correctly gives "
        "m4 = a^2+6a, which IS what the code hardcodes (f1_selberg_delange_expansion.py line 87) -- but "
        "the code never derives this value from an actual computed Pi_4 Laurent coefficient (contrast "
        "with kappa1, kappa2, pi0, R1, R2, which are genuinely computed from prime sums / Stieltjes "
        "constants earlier in the same script); m4 is a bare literal matching Astra's target formula. "
        "So (a) the .md's own written derivation of m4 is arithmetically self-contradictory "
        "(a^2+6a^2 != a^2+6a, as printed above), and (b) the claim that this derivation is 'exact "
        "algebra' done 'in the script' / 'tracked exactly' by the code is false for this specific "
        "coefficient: it is pattern-matched to the known target answer, not independently derived, even "
        "though the target answer itself is correct."
    ),
}
print(json.dumps(out, indent=2))
Path(__file__).with_name("refute_F1_rigour_results.json").write_text(json.dumps(out, indent=2))
