#!/usr/bin/env python3
"""
Exploratory spectral optimization of Inoue, arXiv:2604.05733, Theorem 2.

Source: https://arxiv.org/pdf/2604.05733, page 4 (PDF index 3).
This is NOT an interval-arithmetic certificate, a proof of a global optimum,
or a proof of a new bound on zeta zeros. It optimizes a finite polynomial
trial space and a bounded ell interval, using floating-point quadrature.

Requirements: numpy scipy threadpoolctl
Run: python inoue_resonance_probe.py --output inoue_probe.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
from scipy.special import roots_jacobi, eval_jacobi
from scipy.linalg import eigh
from scipy.optimize import minimize_scalar, brentq
from threadpoolctl import threadpool_limits


def gauss01(n: int, alpha: float = 0.0, beta: float = 0.0):
    """Quadrature for integral_0^1 f(x)(1-x)^alpha x^beta dx."""
    x, w = roots_jacobi(n, alpha, beta)
    return (x + 1) / 2, w / 2**(alpha + beta + 1)


def basis(x, degree: int, a: float):
    """Orthonormal Jacobi basis for weight x^a on [0,1]."""
    x = np.asarray(x).ravel()
    return np.stack([
        np.sqrt(2*j + a + 1) * eval_jacobi(j, 0, a, 2*x-1)
        for j in range(degree+1)
    ], axis=1)


def matrix(phi: float, ell: float, degree: int = 6, q: int = 24):
    """Symmetric matrix of M_{ell,f}(phi); I_f(ell) is identity in this basis."""
    if not (0 < phi < 1 and ell >= 1 and degree >= 0 and q > degree):
        raise ValueError("Need 0<phi<1, ell>=1, degree>=0, and q>degree.")
    a = ell*ell - 1
    r, wr = gauss01(q, 0, a)
    u, wu = gauss01(q, a+1, 0)
    u = u[:, None]
    v = (1-u)*r[None, :]
    w = wu[:, None]*wr[None, :]
    A, B = basis(v, degree, a), basis(v+u, degree, a)
    k = np.pi*phi*np.sinc(phi*u)
    M1 = A.T @ ((w*k).ravel()[:, None]*B)
    M1 = (M1+M1.T)/2
    k2 = (np.pi*phi)**2*u*np.sinc(phi*u)**2
    M3 = A.T @ ((w*k2).ravel()[:, None]*A)

    u1, w1 = gauss01(q, a+2, 0)
    s, w2 = gauss01(q, a+1, 0)
    U, S, R = u1[:, None, None], s[None, :, None], r[None, None, :]
    U2 = (1-U)*S
    V = (1-U)*(1-S)*R
    W = w1[:, None, None]*w2[None, :, None]*wr[None, None, :]
    K1, K2 = np.pi*phi*np.sinc(phi*U), np.pi*phi*np.sinc(phi*U2)
    weight = (W*K1*K2).ravel()
    A = basis(V, degree, a)
    B = basis(V+U+U2, degree, a)
    C = basis(V+U, degree, a)
    D = basis(V+U2, degree, a)
    M2 = A.T @ (weight[:, None]*B) + C.T @ (weight[:, None]*D)
    M2 = (M2+M2.T)/2
    return (abs(1-2*phi)*2/np.pi*ell*M1
            + 2/np.pi**2*ell**2*M2 + 2/np.pi**2*M3)


def optimize(phi: float, degree: int = 6, q: int = 24):
    """Bounded scalar numerical optimization; no certified global optimality."""
    result = minimize_scalar(
        lambda ell: -eigh(matrix(phi, ell, degree, q),
                          eigvals_only=True)[-1],
        bounds=(1.0, 2.2), method="bounded",
        options={"xatol": 2e-8}
    )
    if not result.success:
        raise RuntimeError(result.message)
    return dict(phi=phi, degree=degree, quadrature_order=q,
                ell=float(result.x),
                margin=float(-result.fun-phi*(1-phi)))


def run():
    with threadpool_limits(limits=1):
        phi, ell, q, degree = .508949, 1.15, 24, 6
        M = matrix(phi, ell, degree, q)
        x, w = gauss01(60, 0, ell*ell-1)
        c = basis(x, degree, ell*ell-1).T @ (w*(1-.7*x))
        baseline = float(c@M@c/(c@c)-phi*(1-phi))
        if abs(baseline-1.48716181318e-5) > 1e-9:
            raise RuntimeError("Published linear-trial reproduction failed.")
        half = [optimize(.5, d, qn) for d, qn in
                [(2,18),(4,20),(6,24),(10,28),(14,34)]]
        probe = [optimize(p,8,26) for p in [.508949,.5088,.505,.5,.499]]
        threshold = brentq(
            lambda p: optimize(p,8,26)["margin"], .5087,.509,
            xtol=1e-10
        )
        grid = [
            dict(ell=e,
                 margin=float(eigh(matrix(.5,e,10,30),
                                   eigvals_only=True)[-1]-.25))
            for e in [1.,1.1,1.175,1.3,1.6,2.,3.,4.,6.]
        ]
    return {
        "status": "exploratory floating-point calculation; NOT a theorem",
        "source": "Inoue arXiv:2604.05733, Theorem 2",
        "objective": "M_{ell,f}(phi)/I_f(ell) - phi*(1-phi)",
        "trial_space": "real polynomials of the recorded degree",
        "ell_optimization_interval": [1.0,2.2],
        "baseline_phi": phi,
        "baseline_ell": ell,
        "baseline_f": "1 - 0.7*x",
        "baseline_margin": baseline,
        "half_barrier_probes": half,
        "other_phi_probes": probe,
        "ell_grid_at_half": grid,
        "degree8_numerical_sign_crossing": float(threshold),
        "additional_normalized_log_increment_energy_at_half":
            float(-half[-1]["margin"]*2*np.pi**2),
        "limitations": [
            "No rigorous quadrature-error bounds.",
            "No certified optimization over all ell>=1.",
            "No upper bound over all continuous bounded-variation functions.",
            "No proof that a proposed extended-support arithmetic estimate holds.",
            "The small numerical sign crossing is not claimed as a new theorem."
        ]
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("inoue_probe.json"))
    args = parser.parse_args()
    result = run()
    args.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
