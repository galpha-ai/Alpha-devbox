#!/usr/bin/env python3
"""Independent floating quadrature of Astra's *stipulated* continuum schema
(FABLE_001, section "Proposed continuum schema to challenge") for several trials.

This script does NOT prove anything about zeta zeros.  It evaluates, by Gauss
quadrature, the continuum margin

    J = (M2 + M3)/I - 1/4        (phi = 1/2, a = ell^2)

with
    I  = int_0^1 v^(a-1) E_v[H^2] dv
    M3 = (2/pi^2)      int_{v+u<=1}   v^(a-1) sin^2(pi u/2)/u * E_v[H(v,S)^2]
    M2 = (2 ell^2/pi^2) int_{v+u+w<=1} v^(a-1) k(u) k(w) *
            E_v[ H(v,S) H(v+u+w, S+u^2+w^2) + H(v+u, S+u^2) H(v+w, S+w^2) ]
    k(u) = sin(pi u/2)/u,   E_v[S] = v^2/(a+1),  E_v[S^2] = (a+6) v^4/((a+1)(a+2)(a+3)).

Trials (H = f(v) + g(v) S, S = S2 feature):
  fixed     : ell = 16/15, Astra's rational f, g          (target -0.0146623754733690)
  massonly  : ell = 16/15, f only (g = 0)
  one       : ell = 16/15, H = 1
  one_ell1  : ell = 1,     H = 1   (d_1 = 1, x_n = 1/sqrt n)
  deg14     : ell = 1.1762950385645021, f = Astra's degree-14 Jacobi optimum, g = 0
              (target -0.015357981703850554; coefficients read from
               astra_inputs/research/residual-gram/variational-results.json)

Parametrisation (chosen to differ from Astra's scripts): the two inserted masses
are written u = sigma*tau, w = sigma*(1-tau), sigma = (1-v)*s, Jacobian
(1-v)^2 s; v uses Gauss-Jacobi with weight v^(a-1); s, tau, and the M3 variable
use Gauss-Legendre.  Convergence is reported for three quadrature orders.

Output: f2_continuum_results.json next to this file.
Run:    OPENBLAS_NUM_THREADS=1 python3 f2_continuum.py
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from scipy.special import roots_jacobi, roots_legendre, eval_jacobi

HERE = Path(__file__).resolve().parent
ASTRA = HERE.parents[1] / "astra_inputs" / "research" / "residual-gram"


def f_fixed(v):
    return (145 + 3*v - 116*v**2 + 71*v**3 - 6*v**4) / 100


def g_fixed(v):
    return (-563 + 1682*v - 2479*v**2 + 1751*v**3 - 488*v**4) / 100


def deg14_trial():
    data = json.loads((ASTRA / "variational-results.json").read_text())
    entry = [e for e in data["half_boundary"] if e["degree"] == 14][0]
    ell = entry["ell"]
    a = ell*ell
    c = np.array(entry["jacobi_coefficients"])

    def f(v):
        v = np.asarray(v, dtype=float)
        return sum(c[j]*np.sqrt(2*j + a)*eval_jacobi(j, 0, a - 1, 2*v - 1) for j in range(len(c)))
    return ell, f, entry["margin"]


def moments(a, v):
    m1 = v**2/(a + 1)
    m2 = (a + 6)*v**4/((a + 1)*(a + 2)*(a + 3))
    return m1, m2


def expect_product(a, v, f1, g1, c1, f2, g2, c2):
    """E_v[(f1 + g1 (S + c1)) (f2 + g2 (S + c2))] with S the background feature."""
    m1, m2 = moments(a, v)
    return f1*f2 + f1*g2*(m1 + c2) + g1*f2*(m1 + c1) + g1*g2*(m2 + (c1 + c2)*m1 + c1*c2)


def kernel(u):
    # sin(pi u/2)/u, finite at 0
    return (np.pi/2)*np.sinc(u/2)


def continuum_margin(ell, f, g, order):
    a = ell*ell
    xj, wj = roots_jacobi(order, 0.0, a - 1.0)
    v = (xj + 1)/2
    wv = wj/2**a                      # int_0^1 F v^(a-1) dv = sum wv F(v)
    xl, wl = roots_legendre(order)
    s = (xl + 1)/2
    ws = wl/2

    # I
    I = np.sum(wv*expect_product(a, v, f(v), g(v), 0.0, f(v), g(v), 0.0))

    # M3: u = (1-v) s
    V, Sg = np.meshgrid(v, s, indexing="ij")
    W = wv[:, None]*ws[None, :]*(1 - V)
    U = (1 - V)*Sg
    k3 = U*(np.pi/2)**2*np.sinc(U/2)**2          # sin^2(pi u/2)/u
    M3 = (2/np.pi**2)*np.sum(W*k3*expect_product(a, V, f(V), g(V), 0.0, f(V), g(V), 0.0))

    # M2: sigma = (1-v) s, u = sigma tau, w = sigma (1-tau); du dw = sigma dsigma dtau
    V, Sg, T = np.meshgrid(v, s, s, indexing="ij")
    W = wv[:, None, None]*ws[None, :, None]*ws[None, None, :]*(1 - V)**2*Sg
    Sig = (1 - V)*Sg
    U = Sig*T
    Wd = Sig*(1 - T)
    K = kernel(U)*kernel(Wd)
    term_a = expect_product(a, V, f(V), g(V), 0.0, f(V + U + Wd), g(V + U + Wd), U**2 + Wd**2)
    term_b = expect_product(a, V, f(V + U), g(V + U), U**2, f(V + Wd), g(V + Wd), Wd**2)
    M2a = (2*ell**2/np.pi**2)*np.sum(W*K*term_a)
    M2b = (2*ell**2/np.pi**2)*np.sum(W*K*term_b)
    M2 = M2a + M2b
    return {"I": float(I), "M2a": float(M2a), "M2b": float(M2b), "M2": float(M2), "M3": float(M3),
            "M_over_I": float((M2 + M3)/I), "J": float((M2 + M3)/I - 0.25),
            "lambda_equiv": float(2*np.pi**2*(M2 + M3)/I)}


def main():
    zero = lambda v: np.zeros_like(np.asarray(v, dtype=float))
    one = lambda v: np.ones_like(np.asarray(v, dtype=float))
    ell14, f14, target14 = deg14_trial()
    trials = {
        "fixed": (16/15, f_fixed, g_fixed, -0.014662375473368985),
        "massonly": (16/15, f_fixed, zero, None),
        "one": (16/15, one, zero, None),
        "one_ell1": (1.0, one, zero, None),
        "deg14": (ell14, f14, zero, target14),
    }
    out = {"status": "floating Gauss quadrature of the stipulated continuum schema; not a certificate, not an arithmetic theorem",
           "trials": {}}
    for name, (ell, f, g, target) in trials.items():
        res = {}
        for order in (24, 40, 64):
            res[str(order)] = continuum_margin(ell, f, g, order)
        rec = {"ell": ell, "a": ell*ell, "by_order": res, "J": res["64"]["J"],
               "order_spread_40_64": abs(res["40"]["J"] - res["64"]["J"]),
               "pieces_order64": res["64"], "astra_target": target,
               "diff_vs_astra_target": (None if target is None else res["64"]["J"] - target)}
        out["trials"][name] = rec
        print(f"{name:9s} ell={ell:.10f}  J={res['64']['J']:+.15f}  spread(40,64)={rec['order_spread_40_64']:.1e}"
              + ("" if target is None else f"  target={target:+.15f} diff={rec['diff_vs_astra_target']:+.2e}"), flush=True)
    (HERE / "f2_continuum_results.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
