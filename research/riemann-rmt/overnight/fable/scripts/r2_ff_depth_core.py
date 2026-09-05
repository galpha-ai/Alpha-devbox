"""r2_ff_depth_core.py -- shared machinery for Task B5 (function-field Newman-depth
universality; file overnight/fable/r2_function_field.md).

Conventions (same as depth_scaling_theorem.md): for a monic P(z) = prod_j (z - e^{i theta_j})
= sum_j a_j z^j of degree M, the backward heat flow is P_s(z) = sum_j a_j e^{s j(M-j)} z^j,
s >= 0, and the depth D = first s > 0 at which P_s has a multiple root (= first collision of
the eigenangles, = -Lambda).  P_s stays self-inversive, so a root can leave |z| = 1 only through
a collision; D is therefore detected as the first s at which some root of P_s is off the circle.

Contents
  * exact Haar samplers: U(N) (Mezzadri QR), O(N)/SO(N)/O^-(N) (real QR + column flip),
    USp(2N) (quaternionic Gram-Schmidt: columns v_j and partners w_j = -J conj(v_j)).
  * free-angle extraction with exact symmetrisation, polynomial assembly from real factors.
  * depth solver `depth_from_angles` (bracket from Theorem A + bisection on np.roots) with
    collision-type classification (bulk / edge+ / edge- / multi).
  * ODE cross-check `depth_ode` (theta_j' = -sum_k cot((theta_j-theta_k)/2), stop at a small
    gap, finish with the exact two-body time -log cos(g/2)).
  * closed forms: two-body law, the SO(odd) hard-edge three-body law
    D = (1/2) log(3/(1+2 cos theta)), and the genus-2 (USp(4)) depth via the reduced quadratic
    Q_s(x) = x^2 + A e^{3s} x + (B e^{4s} - 2), x = z + 1/z.
  * Weyl-density rejection samplers for the free angles of USp(4), SO(4), SO(5) (validation).
"""
import numpy as np
from math import pi, log, cos
from scipy.optimize import brentq

OFF_TOL = 1e-6   # off-circle detection threshold; double-precision root error near a double
                 # root is ~sqrt(eps) ~ 1.5e-8; off-circle displacement is ~ c sqrt(s - D),
                 # so the induced bias in D is ~1e-12.

GROUPS = ("U", "USp", "SO_even", "SO_odd", "O_minus")

# ----------------------------------------------------------------------------- samplers
def haar_unitary(n, rng):
    """Mezzadri's recipe: QR of a complex Ginibre matrix, phases of diag(R) fixed."""
    z = (rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))) / np.sqrt(2.0)
    q, r = np.linalg.qr(z)
    d = np.diag(r)
    return q * (d / np.abs(d))


def haar_orthogonal(n, rng):
    z = rng.standard_normal((n, n))
    q, r = np.linalg.qr(z)
    d = np.sign(np.diag(r))
    d[d == 0] = 1.0
    return q * d


def haar_special_orthogonal(n, rng):
    """Haar on SO(n): Haar on O(n), then right-multiply by diag(-1,1,..,1) if det = -1
    (this map O^- -> SO(n) transports Haar to Haar)."""
    q = haar_orthogonal(n, rng)
    if np.linalg.det(q) < 0:
        q = q.copy(); q[:, 0] *= -1.0
    return q


def haar_orthogonal_minus(n, rng):
    """Haar on the det = -1 component O^-(n)."""
    q = haar_orthogonal(n, rng)
    if np.linalg.det(q) > 0:
        q = q.copy(); q[:, 0] *= -1.0
    return q


def symplectic_J(N):
    J = np.zeros((2 * N, 2 * N))
    J[:N, N:] = np.eye(N)
    J[N:, :N] = -np.eye(N)
    return J


def haar_usp(n2, rng):
    """Haar on USp(2N) (n2 = 2N) by quaternionic Gram-Schmidt.
    Columns g_j ~ complex Gaussian in C^{2N}; orthonormalise against all previous v_k and their
    partners w_k = -J conj(v_k); the result U = [v_1..v_N | w_1..w_N] is unitary and commutes
    with the quaternionic structure phi(v) = J conj(v), i.e. U J = J conj(U), hence U^T J U = J.
    Equivariance of the construction under left multiplication by USp(2N) + invariance of the
    quaternion-Gaussian law gives Haar (same argument as Mezzadri's for U(N))."""
    N = n2 // 2
    J = symplectic_J(N)
    G = (rng.standard_normal((n2, N)) + 1j * rng.standard_normal((n2, N))) / np.sqrt(2.0)
    V = np.zeros((n2, N), complex); W = np.zeros((n2, N), complex)
    for j in range(N):
        u = G[:, j].copy()
        for k in range(j):
            u -= (np.vdot(V[:, k], u)) * V[:, k]
            u -= (np.vdot(W[:, k], u)) * W[:, k]
        # second pass for numerical orthogonality
        for k in range(j):
            u -= (np.vdot(V[:, k], u)) * V[:, k]
            u -= (np.vdot(W[:, k], u)) * W[:, k]
        v = u / np.linalg.norm(u)
        V[:, j] = v
        W[:, j] = -J @ np.conj(v)
    return np.hstack([V, W])


def sample_group(group, N, rng):
    """One Haar sample of the group of rank N (N free eigenangles)."""
    if group == "U":
        return haar_unitary(N, rng)
    if group == "USp":
        return haar_usp(2 * N, rng)
    if group == "SO_even":
        return haar_special_orthogonal(2 * N, rng)
    if group == "SO_odd":
        return haar_special_orthogonal(2 * N + 1, rng)
    if group == "O_minus":
        return haar_orthogonal_minus(2 * N + 2, rng)
    raise ValueError(group)


def matrix_size(group, N):
    return {"U": N, "USp": 2 * N, "SO_even": 2 * N, "SO_odd": 2 * N + 1, "O_minus": 2 * N + 2}[group]


# ----------------------------------------------------------------------------- angles
def free_angles(U, group, N, tol=1e-9):
    """Free eigenangles.  'U': all N angles in [0, 2pi), sorted.  Symmetric classes: the N
    angles in (0, pi) (positive imaginary part), sorted; forced eigenvalues +-1 are dropped."""
    ang = np.angle(np.linalg.eigvals(U))
    if group == "U":
        return np.sort(ang % (2 * pi))
    pos = ang[(ang > tol) & (ang < pi - tol)]
    pos = np.sort(pos)
    if len(pos) != N:
        raise RuntimeError(f"expected {N} free angles, got {len(pos)} for {group}")
    return pos


def full_angles(free, group):
    """All eigenangles on the circle, sorted in [0, 2pi)."""
    free = np.asarray(free, float)
    if group == "U":
        return np.sort(free % (2 * pi))
    th = np.concatenate([free, -free])
    if group == "SO_odd":
        th = np.concatenate([th, [0.0]])
    if group == "O_minus":
        th = np.concatenate([th, [0.0, pi]])
    return np.sort(th % (2 * pi))


def poly_from_angles(free, group):
    """Ascending coefficients a_0..a_M of the monic P(z) = prod (z - e^{i theta}) over the full
    configuration.  Symmetric classes are assembled from real quadratic factors
    z^2 - 2 cos(theta) z + 1 (and z -+ 1), so the coefficients are exactly real and exactly
    (anti-)palindromic."""
    free = np.asarray(free, float)
    if group == "U":
        a = np.array([1.0 + 0j])
        for t in free:
            a = np.convolve(a, np.array([-np.exp(1j * t), 1.0]))
        return a
    a = np.array([1.0])
    for t in free:
        a = np.convolve(a, np.array([1.0, -2.0 * np.cos(t), 1.0]))
    if group == "SO_odd":
        a = np.convolve(a, np.array([-1.0, 1.0]))
    if group == "O_minus":
        a = np.convolve(a, np.array([-1.0, 0.0, 1.0]))
    return a.astype(complex)


def min_circular_gap(th_full):
    s = np.sort(np.asarray(th_full) % (2 * pi))
    g = np.diff(np.concatenate([s, [s[0] + 2 * pi]]))
    return float(g.min()), int(np.argmin(g)), g


# ----------------------------------------------------------------------------- flow / roots
def flowed_coeffs(a, s):
    M = len(a) - 1
    j = np.arange(M + 1)
    w = j * (M - j)
    absa = np.abs(a)
    nz = absa > 0
    logmag = np.full(M + 1, -np.inf)
    logmag[nz] = np.log(absa[nz]) + s * w[nz]
    shift = logmag[nz].max()
    c = np.zeros(M + 1, complex)
    c[nz] = (a[nz] / absa[nz]) * np.exp(logmag[nz] - shift)
    return c


def roots_at(a, s):
    c = flowed_coeffs(a, s)
    return np.roots(c[::-1])


def offcircle(a, s):
    r = roots_at(a, s)
    if len(r) < len(a) - 1:
        return np.inf, r
    return float(np.max(np.abs(np.abs(r) - 1.0))), r


def two_body_time(g):
    """-log cos(g/2): exact collision time of an isolated pair at gap g (Lemma 2)."""
    return -log(cos(g / 2.0))


def depth_from_angles(free, group, tol=OFF_TOL, rel=1e-11, s_cap=60.0, classify=True):
    """Depth of the configuration with the given free angles.
    Returns a dict with D (np.inf if no collision by s_cap), the bracket, the baseline
    off-circle error at s = 0, delta_min, Theorem A's bound thA = -log cos(delta_min/2),
    rho = D/thA, and (if classify) the collision type and the index of the initial adjacent
    gap that closed."""
    a = poly_from_angles(free, group)
    thf = full_angles(free, group)
    M = len(thf)
    dmin, imin, gaps = min_circular_gap(thf)
    out = dict(M=M, delta_min=dmin, imin=imin)
    base, _ = offcircle(a, 0.0)
    out["base_off"] = base
    if base > tol:
        out.update(D=np.nan, note="ill-conditioned at s=0")
        return out
    thA = two_body_time(dmin)
    out["thA"] = thA
    lo, hi = 0.0, thA
    o, _ = offcircle(a, hi)
    while o <= tol:
        lo = hi
        hi *= 1.25
        if hi > s_cap:
            out.update(D=np.inf, lo=lo, hi=np.inf, rho=np.inf, ctype="none")
            return out
        o, _ = offcircle(a, hi)
    it = 0
    while hi - lo > rel * hi and it < 200:
        mid = 0.5 * (lo + hi)
        if mid <= lo or mid >= hi:
            break
        o, _ = offcircle(a, mid)
        if o > tol:
            hi = mid
        else:
            lo = mid
        it += 1
    D = 0.5 * (lo + hi)
    out.update(D=D, lo=lo, hi=hi, iters=it, rho=D / thA)
    if classify:
        s_probe = D * (1.0 + 1e-4) + 1e-14
        o, r = offcircle(a, s_probe)
        off = r[np.abs(np.abs(r) - 1.0) > tol]
        n_off = len(off)
        out["n_off"] = n_off
        if n_off == 0:
            out["ctype"] = "unresolved"
        else:
            ang = np.angle(off) % (2 * pi)
            alpha = float(np.angle(np.mean(np.exp(1j * ang))) % (2 * pi))
            out["alpha"] = alpha
            if group == "U":
                out["ctype"] = "bulk" if n_off == 2 else "multi"
            else:
                near_p = min(alpha, 2 * pi - alpha) < 1e-3
                near_m = abs(alpha - pi) < 1e-3
                if n_off == 2 and near_p:
                    out["ctype"] = "edge+"
                elif n_off == 2 and near_m:
                    out["ctype"] = "edge-"
                elif n_off == 4 and not (near_p or near_m):
                    out["ctype"] = "bulk"
                else:
                    out["ctype"] = "multi"
            # which initial adjacent gap contains alpha?
            sfull = np.sort(thf)
            k = int(np.searchsorted(sfull, alpha, side="right") - 1) % M
            out["gap_index"] = k
            out["gap_initial"] = float(gaps[k])
            out["is_min_gap"] = bool(k == imin)
    return out


# ----------------------------------------------------------------------------- ODE cross-check
def depth_ode(free, group, eps_rel=2e-3, rtol=1e-10, atol=1e-13):
    """Integrate theta_j' = -sum_{k != j} cot((theta_j - theta_k)/2) from the full configuration
    until the smallest cyclic gap reaches eps = eps_rel * (2 pi / M); then add the exact two-body
    remainder -log cos(g/2).  The neglected background correction to the remainder is
    O(S* g^2) * remainder, i.e. relative O(M^2 eps^2)."""
    from scipy.integrate import solve_ivp
    th0 = full_angles(free, group)
    M = len(th0)
    eps = eps_rel * 2 * pi / M
    mask = ~np.eye(M, dtype=bool)

    def rhs(t, th):
        d = th[:, None] - th[None, :]
        c = np.zeros_like(d)
        c[mask] = 1.0 / np.tan(0.5 * d[mask])
        return -c.sum(axis=1)

    def gap(th):
        s = np.sort(th)
        return float(np.min(np.diff(np.concatenate([s, [s[0] + 2 * pi]]))))

    def event(t, th):
        return gap(th) - eps
    event.terminal = True
    event.direction = -1
    dmin = gap(th0)
    T = 4.0 * two_body_time(dmin) + 1e-3
    sol = solve_ivp(rhs, (0.0, T), th0, method="DOP853", events=event, rtol=rtol, atol=atol)
    if len(sol.t_events[0]) == 0:
        return np.nan, sol
    t1 = float(sol.t_events[0][0])
    th1 = sol.y_events[0][0]
    g1 = gap(th1)
    return t1 + two_body_time(g1), sol


# ----------------------------------------------------------------------------- closed forms
def hard_edge_three_body(theta):
    """SO(odd) hard edge: forced root at 1 and mirror pair e^{+-i theta}.  The gap g = theta obeys
    g' = -cot(g/2) - cot(g) = -(1+2cos g)/sin g, so 1 + 2 cos g(s) = e^{2s}(1 + 2 cos theta) and
    the triple collision at z = 1 happens at D = (1/2) log(3/(1 + 2 cos theta)) ~ theta^2/6."""
    return 0.5 * log(3.0 / (1.0 + 2.0 * cos(theta)))


def first_zero(f, s_max, n_grid=4000):
    """First positive zero of a continuous f with f(0) != 0, by a sign scan + brentq."""
    s = np.linspace(0.0, s_max, n_grid + 1)
    v = np.array([f(x) for x in s])
    sgn0 = np.sign(v[0])
    idx = np.where(np.sign(v) != sgn0)[0]
    if len(idx) == 0:
        return np.inf
    k = idx[0]
    return brentq(f, s[k - 1], s[k], xtol=1e-15, rtol=1e-14, maxiter=200)


def depth_usp4_closed_form(phi1, phi2, s_max=8.0):
    """Genus 2: P(z) = (z^2-2c1 z+1)(z^2-2c2 z+1) = z^4 + A z^3 + B z^2 + A z + 1 with
    A = -2(c1+c2), B = 2 + 4 c1 c2; weights j(4-j) = 0,3,4,3,0, so with x = z + 1/z
    Q_s(x) = x^2 + A e^{3s} x + (B e^{4s} - 2).  Bulk collision: disc Q_s = 0;
    edge at +1: Q_s(2) = 0; edge at -1: Q_s(-2) = 0.  D = the first of these times.
    Returns (D, type)."""
    c1, c2 = cos(phi1), cos(phi2)
    A = -2.0 * (c1 + c2); B = 2.0 + 4.0 * c1 * c2
    fb = lambda s: A * A * np.exp(6 * s) - 4.0 * (B * np.exp(4 * s) - 2.0)
    fp = lambda s: 2.0 + 2.0 * A * np.exp(3 * s) + B * np.exp(4 * s)
    fm = lambda s: 2.0 - 2.0 * A * np.exp(3 * s) + B * np.exp(4 * s)
    cands = [(first_zero(fb, s_max), "bulk"), (first_zero(fp, s_max), "edge+"), (first_zero(fm, s_max), "edge-")]
    return min(cands, key=lambda t: t[0])


# ----------------------------------------------------------------------------- Weyl densities
def weyl_density(free, group):
    """Unnormalised Weyl density of the free angles (theta in (0,pi)^N) for the symmetric classes
    (recalled: USp(2N) prod_{j<k}(cos th_j - cos th_k)^2 prod sin^2 th_j; SO(2N) prod_{j<k}(...)^2;
    SO(2N+1) prod_{j<k}(...)^2 prod sin^2(th_j/2); O^-(2N+2) prod_{j<k}(...)^2 prod cos^2(th_j/2))."""
    th = np.asarray(free, float)
    c = np.cos(th)
    N = len(th)
    v = 1.0
    for j in range(N):
        for k in range(j + 1, N):
            v *= (c[j] - c[k]) ** 2
    if group == "USp":
        v *= np.prod(np.sin(th) ** 2)
    elif group == "SO_odd":
        v *= np.prod(np.sin(th / 2) ** 2)
    elif group == "O_minus":
        v *= np.prod(np.cos(th / 2) ** 2)
    return v


def weyl_rejection_sample(group, N, n, rng, bound=None):
    """Rejection sampling of the free angles from the Weyl density (only sensible for small N)."""
    if bound is None:
        bound = 4.0 ** (N * (N - 1) // 2)
    out = []
    while len(out) < n:
        th = rng.uniform(0, pi, size=(4 * n, N))
        c = np.cos(th)
        v = np.ones(4 * n)
        for j in range(N):
            for k in range(j + 1, N):
                v *= (c[:, j] - c[:, k]) ** 2
        if group == "USp":
            v *= np.prod(np.sin(th) ** 2, axis=1)
        elif group == "SO_odd":
            v *= np.prod(np.sin(th / 2) ** 2, axis=1)
        elif group == "O_minus":
            v *= np.prod(np.cos(th / 2) ** 2, axis=1)
        acc = rng.uniform(0, bound, size=4 * n) < v
        out.extend(list(np.sort(th[acc], axis=1)))
    return np.array(out[:n])


# ----------------------------------------------------------------------------- CUE limit law
def cue_G2_cdf(y):
    """P(G^2 <= y) with P(G > x) = exp(-x^3/(72 pi)) (Ben Arous-Bourgade law for CUE(N):
    8 N^{8/3} D -> G^2, depth_scaling_theorem.md Thm (ii))."""
    y = np.asarray(y, float)
    return 1.0 - np.exp(-np.maximum(y, 0.0) ** 1.5 / (72.0 * pi))


def ks_against_cdf(sample, cdf):
    x = np.sort(np.asarray(sample, float))
    n = len(x)
    F = cdf(x)
    d_plus = np.max(np.arange(1, n + 1) / n - F)
    d_minus = np.max(F - np.arange(0, n) / n)
    return float(max(d_plus, d_minus))
