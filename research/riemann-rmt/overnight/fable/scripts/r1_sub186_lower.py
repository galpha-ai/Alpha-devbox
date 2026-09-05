#!/usr/bin/env python3
"""r1_sub186_lower.py -- LOWER bounds for M_k and M_{k,eps} at k = 38, 39, 40.

Galerkin (Rayleigh-Ritz) lower bounds in the symmetric-polynomial basis
    G_(a,b) = (1-P1)^a prod_r P_r^{b_r},   a + sum_r r b_r <= d,
on the unit simplex after the rescaling t = (1+eps) u (see p2_eps_engine.py docstring):
    M_{k,eps} = k (1+eps) sup_G Jtil_rho(G)/Itil(G),  rho = (1-eps)/(1+eps).
Any vector x gives the rigorous lower bound  k(1+eps) x^T J x / x^T I x  when the quotient is
evaluated in EXACT rational arithmetic (p2_eps_engine.Engine.certify_fast).  Floating point is used
only to find x.  eps = 0 is the pure Maynard-Tao M_k.

Stages (all results appended to ../data/r1_sub186_lower.json):
  1. float scan: d=14 full basis, k in {38,39,40}, eps in a grid (float eigen-solve, condition cut);
  2. exact certification of the float vectors (best eps per k, plus eps = 0);
  3. optional arb shift-invert refinement (p2_arb_audit-style) if time permits (--hp).

Usage: python3 r1_sub186_lower.py [--d 14] [--hp]
"""
import sys, os, json, time, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np
from fractions import Fraction
from p2_eps_engine import Engine

DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(DATA, "r1_sub186_lower.json")

def load():
    if os.path.exists(OUT):
        return json.load(open(OUT))
    return {"runs": []}

def save(db):
    json.dump(db, open(OUT, "w"), indent=1)

def main():
    d = 14
    if "--d" in sys.argv:
        d = int(sys.argv[sys.argv.index("--d") + 1])
    ks = [38, 39, 40]
    eps_list = [Fraction(0), Fraction(1, 60), Fraction(1, 45), Fraction(1, 35), Fraction(1, 28),
                Fraction(1, 22), Fraction(1, 17), Fraction(1, 12)]
    db = load()
    t0 = time.time()
    E0 = Engine(ks[0], d, d)
    print(f"d={d} full basis n={E0.n}", flush=True)
    E0.build_J_structure()
    print(f"structure built [{time.time()-t0:.0f}s]", flush=True)
    engines = {}
    for k in ks:
        E = Engine(k, d, d)
        E._coo, E.pairs, E._keys = E0._coo, E0.pairs, E0._keys
        engines[k] = E
    best = {}
    for k in ks:
        E = engines[k]
        I = E.I_matrix()
        print(f"k={k}: I built [{time.time()-t0:.0f}s]", flush=True)
        for eps in eps_list:
            M, x = E.M_value(eps, I=I, return_vec=True)
            vecfile = os.path.join(DATA, f"r1_vec_k{k}_d{d}_e{eps.denominator if eps else 0}.npy")
            np.save(vecfile, x)
            rec = {"k": k, "d": d, "basis_dim": E.n, "eps": str(eps), "M_float": float(M),
                   "vec": os.path.basename(vecfile), "stage": "float"}
            db["runs"].append(rec); save(db)
            print(f"  k={k} eps={eps}: M_float = {M:.6f}  [{time.time()-t0:.0f}s]", flush=True)
            if eps != 0 and (k not in best or M > best[k][0]):
                best[k] = (M, eps, x)
    # stage 2: exact certification (pure eps=0 and best eps)
    for k in ks:
        E = engines[k]
        for tag, eps in [("pure", Fraction(0)), ("best", best[k][1])]:
            x = np.load(os.path.join(DATA, f"r1_vec_k{k}_d{d}_e{eps.denominator if eps else 0}.npy"))
            Mc, Mf = E.certify_fast(eps, x, keep=0, verbose=True)
            rec = {"k": k, "d": d, "basis_dim": E.n, "eps": str(eps), "M_certified_exact": str(Mc),
                   "M_certified_float": Mf, "stage": "exact-rational certificate", "tag": tag}
            db["runs"].append(rec); save(db)
            print(f"  CERT k={k} eps={eps} ({tag}): M >= {Mf:.9f}  [{time.time()-t0:.0f}s]", flush=True)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
