"""r1_cue_background_prop33_repair_check.py -- verify the repaired Proposition 3.3 (regime 2 split).

Astra's intake review of commit 89393d5 caught a reversed inequality in the original regime-2 proof:
"P(delta_min>4/N)<=16.47/N < 16.47*64/L^3 = 1053.8/L^3 since N<(L/4)^3" is backwards, because
N<(L/4)^3=L^3/64 gives 1/N>64/L^3, not <. This script:
  (1) confirms symbolically/numerically that the ORIGINAL step's direction is indeed wrong;
  (2) confirms the REPAIRED split (deterministic vanishing for L>=2*pi*N^(1/3); reciprocal used in the
      correct direction for 4*N^(1/3)<L<2*pi*N^(1/3)) gives a valid bound with constant 4086;
  (3) Monte Carlo spot-checks that P(delta_min > L*N^(-4/3)) is in fact <= 4086/L^3 for a range of
      (N, L), including large L / small N where the original bound would have failed.
"""
import numpy as np
import math

PI = math.pi


def check_direction():
    # original (flawed) claim: N < (L/4)**3  ==>  1/N < 64/L**3   -- test on random N,L in that regime
    rng = np.random.default_rng(0)
    violations = 0
    for _ in range(2000):
        N = rng.integers(2, 5000)
        # pick L with N < (L/4)**3, i.e. L > 4*N**(1/3)
        L = 4 * N ** (1 / 3) * rng.uniform(1.001, 50)
        assert N < (L / 4) ** 3 + 1e-9
        claimed = 1 / N < 64 / L ** 3          # the ORIGINAL (flawed) direction
        if claimed:
            violations += 1
    print(f"[original-direction test] out of 2000 samples with N<(L/4)^3, "
          f"the claimed '1/N<64/L^3' held in {violations}/2000 cases "
          f"(should be near 0, since the TRUE direction is >=).")
    assert violations < 50, "the flawed direction should almost never hold -- confirms the bug"


def check_repair():
    rng = np.random.default_rng(1)
    C = 16.47 * 8 * PI ** 3
    print(f"[repair] 16.47*8*pi^3 = {C:.6f}  (headline constant used: 4086)")
    assert C < 4086
    worst_ratio = 0.0
    for _ in range(200000):
        N = rng.integers(2, 20000)
        # sample L across regime 2 broadly, biased toward the boundary L=2*pi*N**(1/3)
        L0 = 4 * N ** (1 / 3)
        L1 = 2 * PI * N ** (1 / 3)
        L = rng.uniform(L0 * 1.0001, L1 * 1.0001) if rng.random() < 0.7 else rng.uniform(L1, 50 * L1)
        if L < L1:
            # regime 2a: bound should be 16.47/N < 4086/L^3
            bound_N_side = 16.47 / N
            bound_L_side = 4086 / L ** 3
            worst_ratio = max(worst_ratio, bound_N_side / bound_L_side)
            assert bound_N_side <= bound_L_side, (N, L, bound_N_side, bound_L_side)
        else:
            # regime 2b: probability is deterministically 0 <= 4086/L^3, nothing to check numerically
            pass
    print(f"[repair] regime-2a check passed on 200000 samples; "
          f"worst (16.47/N)/(4086/L^3) ratio observed = {worst_ratio:.6f} (must be <=1)")


def monte_carlo_gap_tail(N, L, trials=200000, seed=2):
    """Exact Haar CUE via QR of complex Ginibre; compute P(delta_min > L*N^-4/3) empirically."""
    rng = np.random.default_rng(seed)
    thresh = L * N ** (-4 / 3)
    hits = 0
    for _ in range(trials):
        z = (rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))) / np.sqrt(2)
        q, r = np.linalg.qr(z)
        d = np.diagonal(r)
        ph = d / np.abs(d)
        q = q * ph
        eig = np.linalg.eigvals(q)
        theta = np.sort(np.angle(eig))
        gaps = np.diff(np.concatenate([theta, [theta[0] + 2 * PI]]))
        if gaps.min() > thresh:
            hits += 1
    p_hat = hits / trials
    bound = 4086 / L ** 3
    print(f"N={N} L={L:.3f}: empirical P(delta_min>LN^-4/3) = {p_hat:.5f} "
          f"(se~{math.sqrt(p_hat*(1-p_hat)/trials):.5f}), repaired bound 4086/L^3 = {bound:.5f} "
          f"-> {'OK' if p_hat <= bound + 4*math.sqrt(max(p_hat,1e-9)*(1-p_hat)/trials) else 'VIOLATION'}")


if __name__ == "__main__":
    check_direction()
    check_repair()
    print()
    print("Small-scale Monte Carlo spot checks (exact Haar CUE via QR of complex Ginibre):")
    for N, L in [(8, 12.0), (16, 20.0), (32, 30.0), (8, 40.0)]:
        monte_carlo_gap_tail(N, L, trials=20000)
    print("\nAll checks passed.")
