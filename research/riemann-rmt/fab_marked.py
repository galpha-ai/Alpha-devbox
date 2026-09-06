"""fab_marked.py — isospectral blindness of ordinary Lambda, and the marked repair.

Ordinary Lambda is a function of the characteristic polynomial alone, so for isospectral
G1 = Q G2 Q^T it is identically equal: Lambda cannot see eigenvectors.
Marked deformation:  G_eta = G + eta u u^*,  U_eta = (G_eta - iI)(G_eta + iI)^{-1} (Cayley),
chi(G;u) = d/d_eta [ -Lambda(U_eta) ] at eta=0.
Determinant lemma: det(zI - G - eta uu^*) = det(zI-G)(1 - eta u^*(zI-G)^{-1} u),
so the marked depth is driven by the directional resolvent m_u(z) = u^*(zI-G)^{-1}u.
"""
import numpy as np, sys
sys.path.insert(0, ".")
from dyn1_core import find_ustar

def cayley_angles(G):
    ev = np.linalg.eigvalsh(G)
    return np.angle((ev - 1j) / (ev + 1j))      # eigenangles of the Cayley transform

def coeffs_from_angles(th):
    p = np.array([1.0+0j])
    for t in th: p = np.convolve(p, np.array([1.0, -np.exp(1j*t)]))
    return p[::-1]

def depth_of_G(G):
    th = cayley_angles(G)
    a = coeffs_from_angles(th)
    u,_,_ = find_ustar(a, len(th))
    return u

def chi(G, u, h=1e-5):
    u = u/np.linalg.norm(u)
    P = np.outer(u, u.conj()).real
    return (depth_of_G(G + h*P) - depth_of_G(G - h*P)) / (2*h)

rng = np.random.default_rng(11)
N = 6
# an isospectral pair: same spectrum, different eigenvectors
lam = np.array([-1.7, -0.6, -0.15, 0.4, 1.1, 2.3])
Q1, _ = np.linalg.qr(rng.normal(size=(N, N)))
Q2, _ = np.linalg.qr(rng.normal(size=(N, N)))
G1 = Q1 @ np.diag(lam) @ Q1.T
G2 = Q2 @ np.diag(lam) @ Q2.T
print("isospectral pair: max |spec difference| =",
      float(np.abs(np.sort(np.linalg.eigvalsh(G1)) - np.sort(np.linalg.eigvalsh(G2))).max()))
d1, d2 = depth_of_G(G1), depth_of_G(G2)
print(f"ordinary depth:  tau(G1) = {d1:.12f}   tau(G2) = {d2:.12f}   difference = {abs(d1-d2):.3e}")
print("  => ordinary Lambda is BLIND to this pair (class II).\n")

print("marked susceptibility chi(G;u) for random marks u:")
print(f"{'mark':>6} {'chi(G1;u)':>14} {'chi(G2;u)':>14} {'|difference|':>14}")
seps = []
for i in range(6):
    u = rng.normal(size=N)
    c1, c2 = chi(G1, u), chi(G2, u)
    seps.append(abs(c1-c2))
    print(f"{i:>6} {c1:>14.6f} {c2:>14.6f} {abs(c1-c2):>14.6f}")
print(f"  => marked Lambda SEPARATES the pair; median |difference| = {np.median(seps):.6f}\n")

# does chi blow up as the mark aligns with an ill-conditioned direction?
print("chi vs directional resolvent, mark rotated toward the smallest-|eigenvalue| direction:")
w, V = np.linalg.eigh(G1)
j = int(np.argmin(np.abs(w)))                       # near-null direction: resolvent pathology
ur = rng.normal(size=N); ur /= np.linalg.norm(ur)
print(f"{'align':>7} {'chi':>14} {'m_u(z0)=u*(z0 I-G)^-1 u':>26}")
z0 = 0.0                                            # probe at the ill-conditioned point
for a in [0.0, 0.5, 0.9, 0.99, 0.999, 1.0]:
    u = (1-a)*ur + a*V[:, j]; u /= np.linalg.norm(u)
    m = float(u @ np.linalg.solve(z0*np.eye(N) - G1, u))
    print(f"{a:>7} {chi(G1,u):>14.6f} {m:>26.6f}")
