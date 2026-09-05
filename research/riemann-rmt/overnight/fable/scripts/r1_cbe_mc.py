"""
r1_cbe_mc.py -- Monte Carlo for the circular beta-ensemble (CbetaE), task A3(d).

Samples CbetaE(N) via the Killip-Nenciu CMV / Verblunsky-coefficient model
(Killip-Nenciu, "Matrix models for circular ensembles", IMRN 2004 -- recalled,
not verified online) for beta = 1, 4, validated at beta = 2 against Haar CUE
obtained independently via QR of a complex Ginibre matrix (Mezzadri's phase
correction). For each sample we locate the minimum-gap adjacent pair (a,b) and
compute:

  - delta_min  = the minimum cyclic gap,
  - S*         = (1/2) sum_{k != a,b} csc^2(rho_k/2), rho_k = dist(theta_k,{theta_a,theta_b}),
    exactly the repaired stiffness of r1_theoremB_repair.md Sec. 1 (Lemma 0),
    computed here directly from the definition S* = sum_k (1/2) max(csc^2(x_b^k/2), csc^2(x_a^k/2))
    and cross-checked against the csc^2(rho_k/2) form on every sample.

Killip-Nenciu construction (recalled; not verified online tonight):
  Verblunsky coefficients alpha_0,...,alpha_{N-1}. For j = 0,...,N-2, alpha_j is
  drawn from the disk with density proportional to (1-|alpha|^2)^{c_j - 1},
  c_j := (beta/2)(N-1-j), independent across j and of a uniform phase; alpha_{N-1}
  is uniform on the unit circle (modulus 1). At beta=2 this reduces to the
  classical density (1-|alpha|^2)^{N-2-j} for the Verblunsky coefficients of a
  Haar-random unitary's CMV representation (Killip-Nenciu's beta=2 case), which
  is what the beta=2 validation below tests indirectly (by comparing statistics
  to an independently generated Haar CUE sample).

  The CMV matrix is C = L @ M with
    Theta_j = [[conj(alpha_j), rho_j],[rho_j, -alpha_j]]  (2x2, rho_j = sqrt(1-|alpha_j|^2))
    for j = 0,...,N-2, and Theta_{N-1} := [conj(alpha_{N-1})] (1x1, since rho_{N-1}=0);
    L = direct sum of Theta_j over even j = 0,2,4,...
    M = <1> (+) direct sum of Theta_j over odd j = 1,3,5,...
  (standard OPUC / Simon "Orthogonal Polynomials on the Unit Circle" construction).

Usage: python3 r1_cbe_mc.py [--n-samples 200] [--seed 0]
Writes data/r1_cbe_mc.json and data/r1_cbe_mc.log in the sibling data/ directory.
Designed to run in well under 20 minutes on <=2 cores.
"""
import os, sys, json, time, argparse
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(HERE, "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Killip-Nenciu CMV construction
# ---------------------------------------------------------------------------

def sample_verblunsky(N, beta, rng):
    """alpha_0,...,alpha_{N-1}: alpha_j (j<N-1) in the open disk with density
    propto (1-|a|^2)^{c_j-1}, c_j=(beta/2)(N-1-j); alpha_{N-1} on the unit circle."""
    alphas = np.empty(N, dtype=complex)
    for j in range(N - 1):
        c = 0.5 * beta * (N - 1 - j)
        u = rng.random()
        rho2 = 1.0 - (1.0 - u) ** (1.0 / c)   # P(|alpha|^2 <= t) = 1-(1-t)^c
        r = np.sqrt(max(rho2, 0.0))
        phi = rng.random() * 2 * np.pi
        alphas[j] = r * np.exp(1j * phi)
    phi = rng.random() * 2 * np.pi
    alphas[N - 1] = np.exp(1j * phi)
    return alphas


def build_cmv(alphas):
    """CMV matrix C = L @ M from Verblunsky coefficients alpha_0,...,alpha_{N-1}
    (alpha_{N-1} unimodular)."""
    N = len(alphas)
    rho = np.sqrt(np.maximum(1.0 - np.abs(alphas) ** 2, 0.0))
    rho[-1] = 0.0

    def theta_block(j):
        if j == N - 1:
            return np.array([[np.conj(alphas[j])]], dtype=complex)
        a = alphas[j]
        r = rho[j]
        return np.array([[np.conj(a), r], [r, -a]], dtype=complex)

    def direct_sum(blocks):
        n = sum(b.shape[0] for b in blocks)
        M = np.zeros((n, n), dtype=complex)
        i = 0
        for b in blocks:
            k = b.shape[0]
            M[i:i + k, i:i + k] = b
            i += k
        if i < N:
            # pad with identity if sizes fall short (should not trigger given parity, kept defensively)
            for idx in range(i, N):
                M[idx, idx] = 1.0
        return M

    L_blocks = [theta_block(j) for j in range(0, N, 2)]
    M_blocks = [np.array([[1.0]], dtype=complex)] + [theta_block(j) for j in range(1, N, 2)]

    L = direct_sum(L_blocks)
    M = direct_sum(M_blocks)
    return L @ M


def cbe_angles(N, beta, rng):
    alphas = sample_verblunsky(N, beta, rng)
    C = build_cmv(alphas)
    ev = np.linalg.eigvals(C)
    return np.mod(np.angle(ev), 2 * np.pi)


def haar_cue_angles(N, rng):
    """Independent construction: Haar unitary via QR of complex Ginibre with the
    Mezzadri phase correction, eigenvalues' angles."""
    G = (rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))) / np.sqrt(2.0)
    Q, R = np.linalg.qr(G)
    d = np.diagonal(R)
    ph = d / np.abs(d)
    Q = Q * ph  # column-wise phase correction (Mezzadri 2006)
    ev = np.linalg.eigvals(Q)
    return np.mod(np.angle(ev), 2 * np.pi)


# ---------------------------------------------------------------------------
# min-gap pair and stiffness S*
# ---------------------------------------------------------------------------

def min_gap_and_sstar(theta):
    """theta: array of N angles in [0,2pi). Returns (delta_min, S_star, S_star_check)."""
    N = len(theta)
    order = np.argsort(theta)
    th = theta[order]
    gaps = np.empty(N)
    gaps[:-1] = th[1:] - th[:-1]
    gaps[-1] = 2 * np.pi - th[-1] + th[0]
    i0 = int(np.argmin(gaps))
    delta = gaps[i0]
    ia, ib = order[i0], order[(i0 + 1) % N]  # b is "before" a in the sorted cyclic order convention below
    theta_a = theta[ia]
    theta_b = theta[ib]
    # x_b^k = (theta_b - theta_k) mod 2pi ; x_a^k = (theta_a - theta_k) mod 2pi  (either convention works
    # for S*, which is symmetric in the labelling -- we use the definition directly).
    mask = np.ones(N, dtype=bool)
    mask[ia] = False
    mask[ib] = False
    thk = theta[mask]
    xb = np.mod(thk - theta_b, 2 * np.pi)
    xb = np.where(xb == 0, 1e-300, xb)
    xa = np.mod(thk - theta_a, 2 * np.pi)
    xa = np.where(xa == 0, 1e-300, xa)
    S_star = 0.5 * np.sum(np.maximum(1.0 / np.sin(xb / 2) ** 2, 1.0 / np.sin(xa / 2) ** 2))
    # cross-check via rho_k = dist(theta_k, {theta_a,theta_b})
    d_a = np.minimum(xa, 2 * np.pi - xa)
    d_b = np.minimum(xb, 2 * np.pi - xb)
    rho = np.minimum(d_a, d_b)
    S_star_check = 0.5 * np.sum(1.0 / np.sin(rho / 2) ** 2)
    return delta, S_star, S_star_check


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def run_ensemble(kind, N, beta, n_samples, rng):
    deltas = np.empty(n_samples)
    sstars = np.empty(n_samples)
    max_check_err = 0.0
    for i in range(n_samples):
        if kind == "cbe":
            th = cbe_angles(N, beta, rng)
        elif kind == "cue_ginibre":
            th = haar_cue_angles(N, rng)
        else:
            raise ValueError(kind)
        d, s, scheck = min_gap_and_sstar(th)
        deltas[i] = d
        sstars[i] = s
        rel = abs(s - scheck) / max(s, 1e-30)
        max_check_err = max(max_check_err, rel)
    return deltas, sstars, max_check_err


def summarize(deltas, sstars, N):
    return {
        "n": len(deltas),
        "delta_min_median": float(np.median(deltas)),
        "delta_min_mean": float(np.mean(deltas)),
        "N_delta_median_x_Npow": None,  # filled by caller with the right exponent
        "Sstar_over_N2_median": float(np.median(sstars) / N ** 2),
        "Sstar_over_N2_q99": float(np.percentile(sstars, 99) / N ** 2),
        "Sstar_over_N2_max": float(np.max(sstars) / N ** 2),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-samples", type=int, default=200)
    ap.add_argument("--n-samples-val", type=int, default=150)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--Ns", type=int, nargs="+", default=[64, 128])
    ap.add_argument("--betas", type=float, nargs="+", default=[1.0, 4.0])
    ap.add_argument("--val-N", type=int, default=64)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    log_lines = []

    def log(s):
        print(s)
        log_lines.append(s)

    t0 = time.time()
    log(f"# r1_cbe_mc.py run, seed={args.seed}, n_samples={args.n_samples}, "
        f"Ns={args.Ns}, betas={args.betas}, val_N={args.val_N}, n_samples_val={args.n_samples_val}")

    results = {"beta_ensembles": {}, "beta2_validation": {}, "meta": vars(args)}

    # --- beta=2 validation: CMV Killip-Nenciu vs independent Haar CUE (Ginibre QR) ---
    N = args.val_N
    d_cmv, s_cmv, err_cmv = run_ensemble("cbe", N, 2.0, args.n_samples_val, rng)
    d_hcue, s_hcue, _ = run_ensemble("cue_ginibre", N, None, args.n_samples_val, rng)
    log(f"\n== beta=2 validation at N={N} (n={args.n_samples_val} each) ==")
    log(f"CMV(beta=2)      : delta_min median={np.median(d_cmv):.6g}  Sstar/N^2 median={np.median(s_cmv)/N**2:.6g}"
        f"  q99={np.percentile(s_cmv,99)/N**2:.6g}  max Sstar def-check rel err={err_cmv:.2e}")
    log(f"Haar CUE (Ginibre): delta_min median={np.median(d_hcue):.6g}  Sstar/N^2 median={np.median(s_hcue)/N**2:.6g}"
        f"  q99={np.percentile(s_hcue,99)/N**2:.6g}")
    # KS-type simple comparison on delta_min and Sstar (two-sample Kolmogorov-Smirnov via scipy)
    from scipy import stats as spstats
    ks_delta = spstats.ks_2samp(d_cmv, d_hcue)
    ks_s = spstats.ks_2samp(s_cmv, s_hcue)
    log(f"KS test delta_min (CMV vs Ginibre-QR CUE): stat={ks_delta.statistic:.4f} p={ks_delta.pvalue:.4f}")
    log(f"KS test Sstar     (CMV vs Ginibre-QR CUE): stat={ks_s.statistic:.4f} p={ks_s.pvalue:.4f}")
    results["beta2_validation"] = {
        "N": N,
        "n_samples": args.n_samples_val,
        "cmv_delta_median": float(np.median(d_cmv)),
        "ginibre_delta_median": float(np.median(d_hcue)),
        "cmv_Sstar_over_N2_median": float(np.median(s_cmv) / N ** 2),
        "ginibre_Sstar_over_N2_median": float(np.median(s_hcue) / N ** 2),
        "cmv_Sstar_over_N2_q99": float(np.percentile(s_cmv, 99) / N ** 2),
        "ginibre_Sstar_over_N2_q99": float(np.percentile(s_hcue, 99) / N ** 2),
        "Sstar_definition_check_max_rel_err": err_cmv,
        "ks_delta_stat": float(ks_delta.statistic), "ks_delta_p": float(ks_delta.pvalue),
        "ks_Sstar_stat": float(ks_s.statistic), "ks_Sstar_p": float(ks_s.pvalue),
    }

    # --- main beta=1,4 runs at N=64,128 ---
    for beta in args.betas:
        results["beta_ensembles"][str(beta)] = {}
        median_deltas = {}
        for N in args.Ns:
            d, s, err = run_ensemble("cbe", N, beta, args.n_samples, rng)
            summ = summarize(d, s, N)
            summ["Sstar_def_check_max_rel_err"] = err
            results["beta_ensembles"][str(beta)][str(N)] = summ
            median_deltas[N] = summ["delta_min_median"]
            log(f"\nbeta={beta}  N={N}  n={args.n_samples}")
            log(f"  delta_min: median={summ['delta_min_median']:.6g}  mean={summ['delta_min_mean']:.6g}")
            log(f"  Sstar/N^2: median={summ['Sstar_over_N2_median']:.6g}  q99={summ['Sstar_over_N2_q99']:.6g}"
                f"  max={summ['Sstar_over_N2_max']:.6g}")
            log(f"  Sstar definition-check max rel err (max/csc^2-rho form): {err:.2e}")

        # exponent fit from the two N values: delta_min ~ N^{-p}, p fit from log-log slope
        Ns_sorted = sorted(median_deltas)
        if len(Ns_sorted) >= 2:
            N1, N2 = Ns_sorted[0], Ns_sorted[-1]
            p_fit = -(np.log(median_deltas[N2]) - np.log(median_deltas[N1])) / (np.log(N2) - np.log(N1))
            p_pred = 1.0 + 1.0 / (beta + 1.0)
            log(f"  fitted exponent p (delta_min ~ N^-p) from N={N1}->{N2}: {p_fit:.4f}  "
                f"(predicted {p_pred:.4f} = 1+1/(beta+1))")
            results["beta_ensembles"][str(beta)]["exponent_fit"] = {
                "N_lo": N1, "N_hi": N2, "p_fit": float(p_fit), "p_predicted": p_pred,
            }

    elapsed = time.time() - t0
    log(f"\ntotal wall time: {elapsed:.1f} s")

    with open(os.path.join(DATA_DIR, "r1_cbe_mc.json"), "w") as f:
        json.dump(results, f, indent=2)
    with open(os.path.join(DATA_DIR, "r1_cbe_mc.log"), "w") as f:
        f.write("\n".join(log_lines) + "\n")


if __name__ == "__main__":
    main()
