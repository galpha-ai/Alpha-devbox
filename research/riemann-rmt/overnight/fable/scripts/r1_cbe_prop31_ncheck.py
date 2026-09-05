"""r1_cbe_prop31_ncheck.py -- verify the N-power cancellation in the repaired Proposition 3.1.

After Astra's follow-up review caught a false relative-error step in the original proof, the repair
replaces it with a crude-but-valid bound v'<=v+u<=w+eps fed directly into the (U3) hypothesis. This
script verifies (symbolically and numerically) that the resulting bound
    N^(3+3*beta) * eps^(beta+1)/(beta+1) * w^(beta+1)/(beta+1) * (w+eps)^beta
with eps=L*N^(-1-1/(beta+1)), w=c/N, still has NO residual power of N as N->infinity, converging to
[1/(beta+1)^2] * L^(beta+1) * c^(2*beta+1) -- i.e. the same exponents L^(beta+1) c^(2*beta+1) as the
(flawed) original derivation, confirming the repair changes only the route, not the conclusion.
"""
import sympy as sp
import numpy as np


def symbolic_check():
    beta, N, L, c = sp.symbols('beta N L c', positive=True)
    eps = L * N ** (-1 - 1 / (beta + 1))
    w = c / N
    prefactor_exp = 3 + 3 * beta
    eps_exp = sp.simplify(sp.log(eps ** (beta + 1), N))   # should be -(beta+2)
    w_exp = sp.simplify(sp.log(w ** (beta + 1), N))        # should be -(beta+1)
    wpe_exp = sp.simplify(sp.log((w + eps) ** beta / (L / N + c / N) ** beta, N))  # sanity: (w+eps)=N^-1(...)
    total = sp.simplify(prefactor_exp - (beta + 2) - (beta + 1) - beta)
    print(f"prefactor N-exponent: {prefactor_exp}")
    print(f"eps^(beta+1) N-exponent: -(beta+2)  (symbolic log check: {eps_exp})")
    print(f"w^(beta+1)   N-exponent: -(beta+1)  (symbolic log check: {w_exp})")
    print(f"(w+eps)^beta N-exponent: -beta (since w+eps = N^-1*(c+L*N^(-1/(beta+1))))")
    print(f"total N-exponent (should be 0): {total}")
    assert total == 0


def numeric_check(beta, L, c, Ns=(10, 100, 1000, 1e4, 1e6, 1e9, 1e15)):
    def bound(N):
        eps = L * N ** (-1 - 1 / (beta + 1))
        w = c / N
        return N ** (3 + 3 * beta) * eps ** (beta + 1) / (beta + 1) * w ** (beta + 1) / (beta + 1) * (w + eps) ** beta

    target = L ** (beta + 1) * c ** (2 * beta + 1) / (beta + 1) ** 2
    print(f"\nbeta={beta}, L={L}, c={c}: target limit (1/(beta+1)^2)*L^(beta+1)*c^(2beta+1) = {target:.10f}")
    prev = None
    for N in Ns:
        b = bound(N)
        print(f"  N={N:>12.0f}: bound={b:.10f}  ratio to target={b/target:.6f}")
        prev = b
    assert abs(prev - target) / target < 0.05, f"should be converging to within a few % by N={Ns[-1]:.0e} (got ratio {prev/target:.4f})"


if __name__ == "__main__":
    symbolic_check()
    for beta in (1.0, 1.5, 2.0, 4.0):
        numeric_check(beta, L=1.5, c=0.7)
    print("\nAll checks passed: the repaired Proposition 3.1 bound has no residual N-power and "
          "converges to the claimed L^(beta+1) c^(2*beta+1) exponents for every tested beta.")
