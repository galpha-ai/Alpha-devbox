"""dyn1_core: machinery for finite de Bruijn-Newman depth of ACUE configurations.

Setup: N points among the 2N-th roots of unity (slots x in {0..2N-1}, point = zeta^x,
zeta = e^{i pi/N}).  P(z) = prod(1 - z_j z) = sum a_j z^j.  Backward circle heat flow:
P_u(z) = sum a_j e^{u j(N-j)} z^j, u = log r >= 0.  While P_u is collision-free its
roots stay on the unit circle (self-inversive, roots leave only in reciprocal pairs
after a collision), so the first discriminant zero u* = -Lambda is detected as the
first u where any root leaves |z|=1.
"""
import numpy as np
from itertools import combinations
from math import pi, sin, log

OFF_TOL = 1e-6   # off-circle detection threshold (double-precision noise near a
                 # double root is ~sqrt(eps)~1.5e-8, so 1e-6 has a 60x margin;
                 # since offcircle ~ c*sqrt(u-u*), the induced bias in u* is ~1e-12)


def orbits(N):
    """Rotation orbits of N-subsets of Z_{2N}. Returns list of (rep_tuple, orbit_size).
    rep = lexicographically-least bitmask rotation, decoded to sorted slot tuple."""
    M = 2 * N
    full = (1 << M) - 1
    seen = {}
    for C in combinations(range(M), N):
        mask = 0
        for x in C:
            mask |= 1 << x
        m, best = mask, mask
        for _ in range(M - 1):
            m = ((m << 1) & full) | (m >> (M - 1))
            if m < best:
                best = m
        seen[best] = seen.get(best, 0) + 1
    out = []
    for rep_mask in sorted(seen):
        rep = tuple(x for x in range(M) if (rep_mask >> x) & 1)
        out.append((rep, seen[rep_mask]))
    return out


def vandermonde_sq(rep, N):
    """|Delta|^2 = prod_{a<b} |zeta^{x_a}-zeta^{x_b}|^2 = prod 4 sin^2(pi d/(2N))."""
    pr = 1.0
    for a, b in combinations(rep, 2):
        pr *= 4.0 * sin(pi * (b - a) / (2 * N)) ** 2
    return pr


def orbit_masses(N):
    """(reps, sizes, mu) with mu_i = size_i*|Delta(rep_i)|^2 / (2N)^N.
    Cauchy-Binet: sum over all N-subsets of |Delta|^2 = det(A A*) = (2N)^N, so mu
    sums to exactly 1 (checked numerically by caller)."""
    obs = orbits(N)
    reps = [r for r, s in obs]
    sizes = np.array([s for r, s in obs])
    mass = np.array([s * vandermonde_sq(r, N) for r, s in obs])
    Z = float(2 * N) ** N
    return reps, sizes, mass / Z


def coeffs(rep, N):
    """a_j of P(z) = prod_x (1 - zeta^x z), ascending order, length N+1, a_0 = 1."""
    zeta = np.exp(1j * pi / N)
    a = np.zeros(N + 1, complex)
    a[0] = 1.0
    for k, x in enumerate(rep):
        z = zeta ** x
        a[1:k + 2] = a[1:k + 2] - z * a[:k + 1]
    return a


def is_clock(a, N):
    return np.all(np.abs(a[1:N]) < 1e-10)


def flowed_roots(a, u, N):
    """Roots of P_u; log-scaled to avoid overflow for large u. Returns complex array
    (may be shorter than N if leading/trailing coefficients underflow, i.e. roots at
    0/infinity -- that only happens far past collision)."""
    w = np.arange(N + 1) * (N - np.arange(N + 1))
    absa = np.abs(a)
    logmag = np.where(absa > 0, np.log(np.maximum(absa, 1e-300)) + u * w, -np.inf)
    shift = logmag.max()
    c = np.zeros(N + 1, complex)
    nz = absa > 0
    c[nz] = (a[nz] / absa[nz]) * np.exp(logmag[nz] - shift)
    return np.roots(c[::-1])


def offcircle(a, u, N):
    r = flowed_roots(a, u, N)
    if len(r) < N:
        return np.inf
    return np.max(np.abs(np.abs(r) - 1.0))


def find_ustar(a, N, u_cap=60.0):
    """First u with a root off the unit circle (= first collision = -Lambda).
    Returns (ustar, u_lo, u_hi) or (None,...) if no collision by u_cap."""
    if is_clock(a, N):
        return None, None, None
    u_lo, u_hi = 0.0, 1e-4
    while offcircle(a, u_hi, N) <= OFF_TOL:
        u_lo = u_hi
        u_hi *= 2.0
        if u_hi > u_cap:
            return None, u_lo, None
    for _ in range(90):
        um = 0.5 * (u_lo + u_hi)
        if um == u_lo or um == u_hi:
            break
        if offcircle(a, um, N) > OFF_TOL:
            u_hi = um
        else:
            u_lo = um
    return 0.5 * (u_lo + u_hi), u_lo, u_hi


def min_circular_gap(angles):
    s = np.sort(angles)
    g = np.diff(np.concatenate([s, [s[0] + 2 * pi]]))
    return g.min()


def colliding_pair(a, N, rep, u_lo, nsteps=150):
    """Track roots by continuation from u=0 to u_lo (just below collision); return
    (label_a, label_b, gap_slots): original slots of the colliding pair and their
    original cyclic slot separation. Root order on the circle cannot change before
    the first collision, so cyclic-shift alignment of sorted angles is exact."""
    M = 2 * N
    ang0 = np.array([(-pi * x / N) % (2 * pi) for x in rep])
    order = np.argsort(ang0)
    labels = [rep[i] for i in order]
    prev = np.sort(ang0)
    warn = False
    for u in np.linspace(0, u_lo, nsteps + 1)[1:]:
        r = flowed_roots(a, u, N)
        ang = np.sort(np.angle(r) % (2 * pi))
        best_k, best_s = 0, np.inf
        for k in range(N):
            d = np.abs(ang - np.roll(prev, -k))
            d = np.minimum(d, 2 * pi - d)
            s = d.sum()
            if s < best_s:
                best_s, best_k = s, k
        if best_s / N > 0.5 * min_circular_gap(prev):
            warn = True
        labels = labels[best_k:] + labels[:best_k]
        prev = ang
    g = np.diff(np.concatenate([prev, [prev[0] + 2 * pi]]))
    i = int(np.argmin(g))
    xa, xb = labels[i], labels[(i + 1) % N]
    d1, d2 = (xa - xb) % M, (xb - xa) % M
    # colliding roots must be consecutive in the config's cyclic order: pick the
    # separation direction containing no other config point
    s = set(rep)
    def clean(x, d):
        return all(((x + t) % M) not in s for t in range(1, d))
    if clean(xb, d1) and not clean(xa, d2):
        gap = d1
    elif clean(xa, d2) and not clean(xb, d1):
        gap = d2
    else:
        gap = min(d1, d2)
    return xa, xb, gap, g[i], warn


def slot_gaps(rep, N):
    """Cyclic slot gaps of the config (multiples of pi/N in angle)."""
    M = 2 * N
    x = np.array(rep)
    return np.diff(np.concatenate([x, [x[0] + M]]))


def weighted_quantile(v, w, qs):
    idx = np.argsort(v)
    v, w = np.asarray(v)[idx], np.asarray(w)[idx]
    cw = np.cumsum(w) / w.sum()
    return [float(v[np.searchsorted(cw, q, side='left').clip(0, len(v) - 1)])
            for q in qs]
