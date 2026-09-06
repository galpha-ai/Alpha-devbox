"""fab_parity_sectors.py — does the Newman depth separate the PARITY SECTORS?

The strongest known static escape inside the ACUE fibre (Sun-GPT5.6SOL-Fable,
"Finite All-Depth Escape at the Nyquist Boundary"):

    q_N^{\pm}(C) = mu_N(C) * ( 1 +/- (-1)^{sum_{x in C} x} )

are rotation-invariant, MUTUALLY SINGULAR, agree on every complete binary marginal on
at most N-1 sites, and match every balanced trace moment of degree d < N^2/4 -- far
beyond the degree <= N algebra that our freezing theorem covers.

Test: is the finite de Bruijn-Newman depth Lambda blind to them too?
Everything below is exact: the enumeration carries exact Vandermonde masses and the
slot-sum parity is an integer.
"""
import numpy as np
SP="."
PI2_8 = np.pi**2/8

print("parity sectors q^+/q^- of the ACUE fibre, tested by the Newman depth\n")
print(f"{'N':>3} {'orbits +':>9} {'orbits -':>9} {'clock in +':>11} {'clock in -':>11}"
      f" {'E+[N^2(-L)]':>13} {'E-[N^2(-L)]':>13} {'difference':>12}")
for N in range(4, 11):
    d = np.load(f"{SP}/dyn1_results_N{N}.npz")
    reps, mu, ust, ck = d['reps'], d['mu'], d['ustars'], d['clockmask']
    par = reps.sum(axis=1) % 2                      # slot-sum parity, exact integer
    out = {}
    for tag, sel in (("+", par == 0), ("-", par == 1)):
        w = mu[sel]
        tot = w.sum()
        clk = mu[sel & ck].sum() / tot if tot > 0 else np.nan
        nc = sel & ~ck
        wn = mu[nc] / mu[nc].sum()
        out[tag] = (int(sel.sum()), clk, float((N*N*ust[nc]) @ wn), tot)
    (n1, c1, e1, t1), (n2, c2, e2, t2) = out["+"], out["-"]
    print(f"{N:>3} {n1:>9} {n2:>9} {c1:>11.6f} {c2:>11.6f} {e1:>13.7f} {e2:>13.7f} {e1-e2:>12.2e}")
    if N == 8:
        # distributional comparison in the non-clock part
        for tag, sel in (("+", par == 0), ("-", par == 1)):
            nc = sel & ~ck
            w = mu[nc] / mu[nc].sum(); x = N*N*ust[nc]
            o = np.argsort(x); cw = np.cumsum(w[o])
            q = [x[o][np.searchsorted(cw, p)] for p in (0.1, 0.25, 0.5, 0.75, 0.9)]
            print(f"      sector {tag}: quantiles(10/25/50/75/90) = "
                  + " ".join(f"{v:.6f}" for v in q))
print("\ntotal ACUE mass in each sector (should be 1/2 each by symmetry):")
for N in (6, 8, 10):
    d = np.load(f"{SP}/dyn1_results_N{N}.npz")
    par = d['reps'].sum(axis=1) % 2
    print(f"  N={N}: mass(+) = {d['mu'][par==0].sum():.10f}, mass(-) = {d['mu'][par==1].sum():.10f}")
