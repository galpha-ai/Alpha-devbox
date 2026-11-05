"""
r1_cbe_seed_sweep.py -- multi-seed robustness check for the delta_min exponent fit
reported in r1_cbe_background.md Sec 6 (task A3, repair pass).

Written during the REPAIR of r1_cbe_background.md in response to an independent
refuter's finding that the file's Sec 6 "Reading" paragraph drew a directional
conclusion ("convergence gets slower as beta grows") from a single seed=42,
two-point (N=64->128) exponent fit, and that a multi-seed sweep reverses the
apparent ranking. This script reruns the identical two-point fit
(run_ensemble from r1_cbe_mc.py, same N's, same n_samples=250) across 8 fresh
seeds (1..8, disjoint from the original seed=42 run) for beta in {1,4} and
reports the seed-to-seed spread, confirming or refuting the claim.

Usage: python3 r1_cbe_seed_sweep.py
Writes data/r1_cbe_seed_sweep.json and data/r1_cbe_seed_sweep.log.
Runtime: ~70s on one core (8 seeds x 2 betas x 2 Ns x 250 samples).
"""
import os, sys, json, time
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(HERE, "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)
sys.path.insert(0, HERE)

import numpy as np
from r1_cbe_mc import run_ensemble  # reuses the exact same sampler/estimator, no reimplementation

Ns = [64, 128]
betas = [1.0, 4.0]
seeds = [1, 2, 3, 4, 5, 6, 7, 8]
n_samples = 250

def main():
    t0 = time.time()
    log_lines = []
    def log(s):
        print(s)
        log_lines.append(s)

    log(f"# r1_cbe_seed_sweep.py: Ns={Ns} betas={betas} seeds={seeds} n_samples={n_samples}")
    per_beta = {b: [] for b in betas}
    rows = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        for beta in betas:
            med = {}
            for N in Ns:
                d, s, err = run_ensemble("cbe", N, beta, n_samples, rng)
                med[N] = float(np.median(d))
            p_fit = -(np.log(med[Ns[-1]]) - np.log(med[Ns[0]])) / (np.log(Ns[-1]) - np.log(Ns[0]))
            p_pred = 1.0 + 1.0 / (beta + 1.0)
            per_beta[beta].append(p_fit)
            rows.append({"seed": seed, "beta": beta, "p_fit": p_fit, "p_pred": p_pred})
            log(f"seed={seed} beta={beta} p_fit={p_fit:.4f} p_pred={p_pred:.4f} dev={p_fit-p_pred:+.4f}")

    summary = {}
    for beta in betas:
        arr = np.array(per_beta[beta])
        p_pred = 1.0 + 1.0 / (beta + 1.0)
        summary[str(beta)] = {
            "mean_p_fit": float(arr.mean()),
            "std_p_fit": float(arr.std()),
            "mean_abs_dev": float(np.mean(np.abs(arr - p_pred))),
            "range": [float(arr.min()), float(arr.max())],
            "p_pred": p_pred,
        }
        log(f"beta={beta}: mean p_fit={arr.mean():.4f} std={arr.std():.4f} "
            f"mean|dev|={np.mean(np.abs(arr-p_pred)):.4f} range=[{arr.min():.4f},{arr.max():.4f}]")

    elapsed = time.time() - t0
    log(f"\ntotal wall time: {elapsed:.1f} s")
    out = {"rows": rows, "summary": summary, "meta": {"Ns": Ns, "betas": betas, "seeds": seeds, "n_samples": n_samples}}
    with open(os.path.join(DATA_DIR, "r1_cbe_seed_sweep.json"), "w") as f:
        json.dump(out, f, indent=2)
    with open(os.path.join(DATA_DIR, "r1_cbe_seed_sweep.log"), "w") as f:
        f.write("\n".join(log_lines) + "\n")

if __name__ == "__main__":
    main()
