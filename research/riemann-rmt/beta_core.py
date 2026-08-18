"""beta_core.py — CβE samplers (Killip–Nenciu CMV) + tracked Λ solver.

Reuses dyn2_core's validated ODE / coefficient-bisection Λ solvers.

Killip–Nenciu (IMRN 2004, Thm 1): the CMV matrix built from independent
Verblunsky coefficients alpha_k ~ Theta_{nu_k}, nu_k = beta*(n-k-1)+1 for
k = 0..n-2 (rotationally invariant on the disk, |alpha_k|^2 ~ Beta(1, beta*(n-k-1)/2))
and alpha_{n-1} uniform on the unit circle, has eigenvalue density
    prop. to prod_{j<k} |e^{i th_j} - e^{i th_k}|^beta   (CbetaE).
beta = 2 must reproduce CUE.
"""
import numpy as np
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dyn2_core import (haar_unitary, haar_eigenangles, adjacent_gaps,
                       _rhs, _rk4_step, neg_lambda_ode, neg_lambda_coeff)

# ------------------------------------------------------------- CbetaE sampler


def kn_verblunsky(N, beta, rng):
    """Independent Verblunsky coefficients for CbetaE(N)."""
    alpha = np.zeros(N, dtype=np.complex128)
    k = np.arange(N - 1)
    s = 0.5 * beta * (N - 1 - k)              # Beta(1, s) for |alpha_k|^2
    r2 = rng.beta(1.0, s)
    ph = np.exp(2j * np.pi * rng.random(N - 1))
    alpha[:N - 1] = np.sqrt(r2) * ph
    alpha[N - 1] = np.exp(2j * np.pi * rng.random())
    return alpha


def cmv_matrix(alpha):
    """CMV matrix C = L M from Verblunsky coefficients (|alpha[-1]| = 1)."""
    N = alpha.size
    rho = np.sqrt(np.clip(1.0 - np.abs(alpha) ** 2, 0.0, None))
    L = np.zeros((N, N), dtype=np.complex128)
    M = np.zeros((N, N), dtype=np.complex128)

    def put(A, k):
        if k == N - 1:                        # boundary 1x1 block
            A[k, k] = np.conj(alpha[k])
        else:
            a, r = alpha[k], rho[k]
            A[k, k] = np.conj(a); A[k, k + 1] = r
            A[k + 1, k] = r;      A[k + 1, k + 1] = -a

    for k in range(0, N, 2):
        put(L, k)
    M[0, 0] = 1.0
    for k in range(1, N, 2):
        put(M, k)
    return L @ M


def cbe_eigenangles(N, beta, rng):
    """Sorted eigenangles of one CbetaE(N) draw (Killip–Nenciu)."""
    C = cmv_matrix(kn_verblunsky(N, beta, rng))
    th = np.sort(np.angle(np.linalg.eigvals(C)))
    return th


def coe_eigenangles(N, rng):
    """Direct COE draw: U = V V^T, V Haar unitary (beta = 1)."""
    V = haar_unitary(N, rng)
    U = V @ V.T
    th = np.sort(np.angle(np.linalg.eigvals(U)))
    return th


# --------------------------------------------------- tracked ODE Lambda solver


def neg_lambda_ode_tracked(th0, c=0.02, g_stop=1e-6, t_cap=50.0):
    """Same as dyn2_core.neg_lambda_ode but also returns the index of the
    colliding adjacent pair (gap i = between sorted points i, i+1 mod N).
    Points never cross before the first collision, so the argmin gap at the
    stopping time identifies the colliding pair in the initial ordering."""
    th = np.array(th0, dtype=np.float64)
    N = th.size
    t = 0.0
    g = adjacent_gaps(th)
    gmin = g.min()
    while gmin > g_stop:
        dt = c * gmin * gmin
        for _ in range(60):
            th_new = _rk4_step(th, dt)
            g_new = adjacent_gaps(th_new)
            gm_new = g_new.min()
            if gm_new > 0.0:
                break
            dt *= 0.5
        else:
            raise RuntimeError("step-size underflow")
        th, g, gmin = th_new, g_new, gm_new
        t += dt
        if t > t_cap:
            raise RuntimeError("t_cap exceeded")
    idx = int(np.argmin(g))
    return t + (-np.log(np.cos(0.5 * gmin))), idx


def sample_record_beta(N, beta, rng):
    """One CbetaE draw -> (neg_lambda, dmin, d2, localized_flag)."""
    th = cbe_eigenangles(N, beta, rng)
    g = adjacent_gaps(th)
    order = np.argsort(g)
    dmin, d2 = g[order[0]], g[order[1]]
    nl, idx = neg_lambda_ode_tracked(th)
    return nl, dmin, d2, 1.0 if idx == order[0] else 0.0
