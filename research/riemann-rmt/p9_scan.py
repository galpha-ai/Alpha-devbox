#!/usr/bin/env python3
"""P9 scan driver: find minimal k with certified M_k (or capped variant) > threshold."""
import numpy as np
import json, sys, time
from p9_mk_engine import optimize_parametric, eval_params, make_grid, param_g, certified_bound

CACHE = {}

def best_cert(k, cap=None, n=240, nstart=2):
    key = (k, None if cap is None else round(cap, 6), n)
    if key in CACHE:
        return CACHE[key]
    L = np.log(k)
    starts = []
    base = np.array([np.log(max(L - 2.7, 1.0)), L - 3.0, np.log(1.2), np.log(2.0)])
    starts.append(base)
    starts.append(base + np.array([0.05, 0.6, 0.3, -0.3]))
    starts.append(base + np.array([-0.05, -0.6, 0.5, 0.5]))
    if cap is not None:
        for s in starts:
            s[1] = min(s[1], np.log(0.55 * cap))
            s[3] = min(s[3], np.log(1.8))
    best = (-1, None)
    for s in starts[:nstart]:
        try:
            v, x = optimize_parametric(k, cap=cap, n=n, x0=s)
        except Exception as e:
            continue
        if v > best[0]:
            best = (v, x)
    CACHE[key] = best
    return best


def min_k_pure(thresh, klo, khi, n=240):
    """bisect minimal k with certified > thresh (monotone in k, empirically)."""
    vlo = best_cert(klo, n=n)[0]
    vhi = best_cert(khi, n=n)[0]
    print(f"bracket: k={klo}: {vlo:.4f}, k={khi}: {vhi:.4f} (thresh {thresh})")
    assert vhi > thresh, "khi too small"
    if vlo > thresh:
        print("klo already passes!"); return klo
    while khi - klo > max(2, klo // 2000):
        km = (klo + khi) // 2
        vm = best_cert(km, n=n)[0]
        print(f"  k={km}: certified {vm:.5f} {'PASS' if vm>thresh else 'fail'}")
        if vm > thresh:
            khi = km
        else:
            klo = km
    return khi


def min_k_deligne(m, klo, khi, n=240, ndelta=5):
    """Deligne/MPZ route: maximize over (varpi,delta): 600varpi+180delta<7,
    threshold m/(1/4+varpi), cap alpha = delta/(1/4+varpi) (t-units) -> T <= alpha*k."""
    def passes(k):
        # scan delta grid; small safety eps on the constraint line
        for dl in np.linspace(0.008, 0.033, ndelta):
            varpi = (7.0 - 180.0 * dl) / 600.0 * (1 - 1e-9)
            if varpi <= 0: continue
            th = m / (0.25 + varpi)
            alpha = dl / (0.25 + varpi)
            v = best_cert(k, cap=alpha * k, n=n)[0]
            if v > th:
                return True, dl, varpi, v, th
        return False, None, None, None, None
    ok, *info = passes(khi)
    print(f"khi={khi}: {ok} {info}")
    assert ok
    ok_lo, *_ = passes(klo)
    if ok_lo:
        print("klo passes!"); return klo
    while khi - klo > max(2, klo // 2000):
        km = (klo + khi) // 2
        ok, dl, varpi, v, th = passes(km)
        print(f"  k={km}: {'PASS' if ok else 'fail'}" + (f" (delta={dl:.4f}, varpi={varpi:.5f}, cert {v:.4f} > {th:.4f})" if ok else ""))
        if ok:
            khi = km
        else:
            klo = km
    return khi


if __name__ == "__main__":
    mode = sys.argv[1]
    t0 = time.time()
    if mode == "pure2":
        k = min_k_pure(8.0 + 1e-6, 15000, 35410)
        print(f"MINIMAL k (pure BV, m=2): {k}")
    elif mode == "del2":
        k = min_k_deligne(2, 12000, 30000)
        print(f"MINIMAL k (Deligne, m=2): {k}")
    elif mode == "pure3":
        k = min_k_pure(12.0 + 1e-6, 500000, 1649821)
        print(f"MINIMAL k (pure BV, m=3): {k}")
    elif mode == "del3":
        k = min_k_deligne(3, 400000, 1400000)
        print(f"MINIMAL k (Deligne, m=3): {k}")
    elif mode == "single":
        k = int(sys.argv[2]); cap = None if len(sys.argv) < 4 else float(sys.argv[3])
        v, x = best_cert(k, cap=cap)
        print(f"k={k} cap={cap}: certified {v:.6f} (deficit {np.log(k)-v:.4f}) params {np.exp(x)}")
    print(f"time {time.time()-t0:.1f}s")
