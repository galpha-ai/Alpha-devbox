"""Monte Carlo for CUE(N): P(N^2 D > pi^2/8) and P(N^2 D > 1.0), against the extreme-gap prediction exp(-pi^2 N/72)."""
import sys, numpy as np
from flint import acb, arb, acb_poly, ctx
ctx.prec = 200
rng = np.random.default_rng(20261113)
def haar_angles(N):
    Z = (rng.standard_normal((N, N)) + 1j*rng.standard_normal((N, N)))/np.sqrt(2)
    Q, R = np.linalg.qr(Z); Q = Q * (np.diag(R)/np.abs(np.diag(R)))
    return np.angle(np.linalg.eigvals(Q))
def survival(th, s):
    N = len(th)
    P = acb_poly([1])
    for t in th: P = P * acb_poly([-(acb(0, arb(float(t))).exp()), 1])
    lam = arb(s).exp()
    a = [P[j] * lam**(j*(N-j)) for j in range(N+1)]
    try: roots = acb_poly(a).roots()
    except Exception: return None
    if len(roots) != N: return None
    for z in roots:
        if (abs(z) - 1) != 0: return False
    refl = [1/z.conjugate() for z in roots]
    return True if all((abs(refl[k]-roots[j]) != 0) for k in range(N) for j in range(N) if j != k) else None
N = int(sys.argv[1]); samples = int(sys.argv[2])
thresholds = [np.pi**2/8, 1.0, 0.5]
counts = {t: 0 for t in thresholds}; inconclusive = 0
for _ in range(samples):
    th = haar_angles(N)
    for t in thresholds:
        r = survival(th, t/N**2)
        if r is None: inconclusive += 1; break
        if r: counts[t] += 1
for t in thresholds:
    print(f"CUE({N}), {samples} samples: P(N^2 D > {t:.4f}) = {counts[t]/samples:.4f}   [extreme-gap prediction exp(-pi^2 N/72 * (8t/pi^2)^(3/2)) = {np.exp(-np.pi**2*N/72*(8*t/np.pi**2)**1.5):.4f}]")
print("inconclusive:", inconclusive)
