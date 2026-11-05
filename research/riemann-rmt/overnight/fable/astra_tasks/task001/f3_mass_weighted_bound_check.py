"""f3_mass_weighted_bound_check.py -- verify Astra's correction to F3's Cauchy-Schwarz bound.

The original r2_diagonal_operator_spectrum.md claimed the crude Cauchy-Schwarz/number-operator
bound on ||Phi|| is infinite on the mass-<=1-truncated Fock space, using the generic
particle-number bound ||A(g)*psi_n||^2 <= (n+1)||g||^2 ||psi_n||^2 (unbounded n on the truncated
space). Astra's intake review (fable/reviews/pr11-2073028/F3_MASS_CUTOFF_BOUND.md in the new repo)
showed this is wrong: the correct mass-WEIGHTED Cauchy-Schwarz bound gives a finite ||K|| <= 2*B_g^2
with B_g^2 = integral_0^1 |g(u)|^2/u^2 du, using only E<=1 (the mass constraint itself), never
bounding particle number. This script verifies the closed form and the discrete-sum comparison.
"""
import mpmath as mp

mp.mp.dps = 30


def Bg2_exact():
    """B_g^2 = 4*int_0^1 sin^2(pi u/2)/u^2 du = 2*pi*Si(pi) - 4, for g(u)=2 sin(pi u/2)."""
    return 2 * mp.pi * mp.si(mp.pi) - 4


def Bg2_quadrature():
    f = lambda u: 4 * mp.sin(mp.pi * u / 2) ** 2 / u ** 2
    return mp.quad(f, [0, 1])


def BM2(M):
    """Discrete analogue: (1/M) sum_{j=1}^M 4 sin^2(pi u_j/2)/u_j^2, u_j = j/M -- a right Riemann
    sum of a decreasing integrand (sin(x)/x decreasing on (0,pi/2]), hence <= the integral."""
    total = mp.mpf(0)
    for j in range(1, M + 1):
        u = mp.mpf(j) / M
        total += 4 * mp.sin(mp.pi * u / 2) ** 2 / u ** 2
    return total / M


if __name__ == "__main__":
    exact = Bg2_exact()
    quad = Bg2_quadrature()
    print(f"B_g^2 exact closed form (2*pi*Si(pi)-4)     = {exact}")
    print(f"B_g^2 numeric quadrature                     = {quad}")
    print(f"agreement                                    = {float(abs(exact - quad)):.3e}")
    print(f"||K|| <= 2*B_g^2                              = {2 * exact}")
    print()
    print("Discrete right-Riemann-sum check (should increase toward B_g^2 from below, never exceed it):")
    for M in (10, 50, 100, 500, 2000, 10000):
        bm2 = BM2(M)
        print(f"  M={M:>6}: B_M^2 = {float(bm2):.10f}  (<= B_g^2? {bm2 <= exact})  "
              f"2*B_M^2 = {float(2*bm2):.6f}")
    print()
    print(f"Conclusion: ||K|| is finite (<= {float(2*exact):.4f}), correcting the earlier",
          "'literally infinite' claim; the bound is still far above pi^2/2 =",
          f"{float(mp.pi**2/2):.4f}, so it resolves the wall question in neither direction.")
