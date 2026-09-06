"""beta_run.py — CbetaE scaling runs for the Dynamic Newman Universality test.

Saves beta_data_b{beta}_N{N}.npz with neglam, dmin, d2, loc (localization flag:
1 if first collision pair == initially minimal gap pair).
Usage: python3 beta_run.py <beta>
"""
import numpy as np
import os, sys, time
from multiprocessing import Pool

os.environ.setdefault("OMP_NUM_THREADS", "1")
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)

PLAN = [(8, 3000), (16, 3000), (32, 2000), (64, 1500), (128, 800), (256, 300)]


def worker(args):
    N, beta, seed, count = args
    from beta_core import sample_record_beta
    rng = np.random.default_rng(seed)
    out = np.empty((count, 4))
    for i in range(count):
        out[i] = sample_record_beta(N, beta, rng)
    return out


def main(beta):
    nproc = 4
    for N, M in PLAN:
        fn = os.path.join(SP, f"beta_data_b{int(beta)}_N{N}.npz")
        if os.path.exists(fn):
            print(f"skip N={N} (exists)"); continue
        t0 = time.time()
        chunks = [M // nproc + (1 if i < M % nproc else 0) for i in range(nproc)]
        args = [(N, beta, 918_000 + 1000 * int(beta) + 10 * N + i, c)
                for i, c in enumerate(chunks)]
        with Pool(nproc) as p:
            res = np.vstack(p.map(worker, args))
        np.savez(fn, neglam=res[:, 0], dmin=res[:, 1], d2=res[:, 2], loc=res[:, 3])
        med = np.median(res[:, 0])
        print(f"beta={beta} N={N}: {M} samples in {time.time()-t0:.0f}s  "
              f"med(-L)={med:.4e}  loc={res[:,3].mean():.3f}", flush=True)


if __name__ == "__main__":
    main(float(sys.argv[1]))
