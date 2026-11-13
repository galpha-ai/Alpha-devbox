"""r2_lr_triangle_cert.py -- the single-test-function (interval-count variance) certificate.

For a stationary intensity-1 process with hard core c and any L <= c, N[0,L] in {0,1}, hence
Var N[0,L] = L - L^2.  Bochner + bandwidth-one sine mimicry give
    Var N[0,L] = int |fhat|^2 dS  >=  int_{|a|<=1} |fhat(a)|^2 |a| da,   f = 1_[0,L],
i.e.  L - L^2 >= V(L) := 2 int_0^1 sin^2(pi L a)/(pi^2 a) da = (gamma + ln(2 pi L) - Ci(2 pi L))/pi^2.
This is the dual certificate T = Lambda_L (triangle of half-width L), phi = L sinc^2(L a) >= 0.
c_tri := the root of L - L^2 = V(L) is an upper bound on mu.  Script computes it to 12 digits.
"""
import mpmath as mp
mp.mp.dps = 30
def V(L):
    return (mp.euler + mp.log(2*mp.pi*L) - mp.ci(2*mp.pi*L))/mp.pi**2
def Vq(L):  # direct quadrature cross-check
    return 2*mp.quad(lambda a: mp.sin(mp.pi*L*a)**2/(mp.pi**2*a), [0, 1])
f = lambda L: L - L**2 - V(L)
root = mp.findroot(f, 0.6)
print("V(0.6) closed form vs quadrature:", V(mp.mpf('0.6')), Vq(mp.mpf('0.6')))
print("root of L - L^2 = V(L):", mp.nstr(root, 15))
print("f(0.606894) =", mp.nstr(f(mp.mpf('0.606894')), 8), " f(0.606895) =", mp.nstr(f(mp.mpf('0.606895')), 8))
# J(c) for T = Lambda_c in the certificate normalisation J = phi(0) - T(0) + 2 int_0^1 a phi(a) da
J = lambda c: c - 1 + 2*mp.quad(lambda a: a*c*(mp.sin(mp.pi*c*a)/(mp.pi*c*a))**2, [0, 1])
print("J(root) =", mp.nstr(J(root), 5), " (should be 0);  J(0.7) =", mp.nstr(J(mp.mpf('0.7')), 6), " J(0.55) =", mp.nstr(J(mp.mpf('0.55')), 6))
