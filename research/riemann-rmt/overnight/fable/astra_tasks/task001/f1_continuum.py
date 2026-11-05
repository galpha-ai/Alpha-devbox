"""Independent high-precision evaluation of the continuum schema of the fixed trial (Fable task001 / F1).

  I  = int_0^1 v^{a-1} E_v[H^2] dv
  M2 = (2 ell^2/pi^2) int_{v,u,w>=0, v+u+w<=1} v^{a-1} (sin(pi u/2)/u)(sin(pi w/2)/w)
                       E_v[ H(v,S)H(v+u+w,S+u^2+w^2) + H(v+u,S+u^2)H(v+w,S+w^2) ] dv du dw
  M3 = (2/pi^2) int_{v,u>=0, v+u<=1} v^{a-1} (sin^2(pi u/2)/u) E_v[H(v,S)^2] dv du
  E_v[S] = v^2/(a+1),  E_v[S^2] = (a+6) v^4/((a+1)(a+2)(a+3)),  J = (M2+M3)/I - 1/4.

Method (my own code, same mathematical route as Astra's rational certificate but in mpmath at 40 digits):
exact rational polynomial expansion in (v,u,w) with sympy, Taylor series of the sine kernels with
explicit remainder monitoring, Dirichlet (simplex) monomial integrals Gamma(al)Gamma(be)Gamma(ga)/Gamma(al+be+ga+1).
Status label: finite numerical check (floating cross-check of a certified continuum integral).
Evaluated for the fixed trial H = f + g S, for H = f (mass-only, g = 0) and for H = 1 (pure d_ell).
Output: f1_continuum_results.json
"""
from __future__ import annotations
import json
from pathlib import Path
import sympy as sp
import mpmath as mp

mp.mp.dps = 40
v, u, w, S = sp.symbols('v u w S')
ell = sp.Rational(16, 15)
a = ell ** 2
mu1 = 1 / (a + 1)
mu2 = (a + 6) / ((a + 1) * (a + 2) * (a + 3))
f_poly = (145 + 3 * v - 116 * v ** 2 + 71 * v ** 3 - 6 * v ** 4) / 100
g_poly = (-563 + 1682 * v - 2479 * v ** 2 + 1751 * v ** 3 - 488 * v ** 4) / 100
A = mp.mpf(a.p) / a.q
PI = mp.pi


def q2mp(c):
    c = sp.Rational(c)
    return mp.mpf(c.p) / c.q


def avg(expr):
    """Replace S -> E_v[S], S^2 -> E_v[S^2] after expanding (joint moments of the same background)."""
    poly = sp.Poly(sp.expand(expr), S)
    out = 0
    for (k,), c in poly.terms():
        assert k <= 2
        out += c * {0: 1, 1: mu1 * v ** 2, 2: mu2 * v ** 4}[k]
    return sp.expand(out)


def simplex3(al, be, ga):
    return mp.gamma(al) * mp.gamma(be) * mp.gamma(ga) / mp.gamma(al + be + ga + 1)


def simplex2(al, be):
    return mp.gamma(al) * mp.gamma(be) / mp.gamma(al + be + 1)


def schema(H, N2=14, N3=16):
    def shift(*xs):
        return H.subs({v: v + sum(xs), S: S + sum(x * x for x in xs)}, simultaneous=True)
    P = sp.Poly(avg(H * shift(u, w) + shift(u) * shift(w)), v, u, w)
    Q = sp.Poly(avg(H * H), v)
    Qt = [(k, q2mp(c)) for (k,), c in Q.terms()]
    Pt = [((k, i, j), q2mp(c)) for (k, i, j), c in P.terms()]
    I = mp.fsum(c / (A + k) for k, c in Qt)
    # M3: sin^2(pi u/2)/u = sum_{n>=1} (-1)^{n+1} pi^{2n} u^{2n-1} / (2 (2n)!)
    M3 = mp.mpf(0); last3 = None
    for n in range(1, N3 + 1):
        coef = (-1) ** (n + 1) * PI ** (2 * n) / (2 * mp.factorial(2 * n))
        integ = mp.fsum(c * simplex2(A + k, 2 * n) for k, c in Qt)
        last3 = coef * integ
        M3 += last3
    M3 *= 2 / PI ** 2
    # M2: sin(pi u/2)/u = sum_n (-1)^n (pi/2)^{2n+1} u^{2n}/(2n+1)!
    M2 = mp.mpf(0); last2 = mp.mpf(0)
    for n in range(N2 + 1):
        cn = (-1) ** n * (PI / 2) ** (2 * n + 1) / mp.factorial(2 * n + 1)
        for m in range(N2 + 1):
            cm = (-1) ** m * (PI / 2) ** (2 * m + 1) / mp.factorial(2 * m + 1)
            integ = mp.fsum(c * simplex3(A + k, i + 2 * n + 1, j + 2 * m + 1) for (k, i, j), c in Pt)
            term = cn * cm * integ
            if n == N2 or m == N2:
                last2 = max(last2, abs(term))
            M2 += term
    M2 *= 2 * ell ** 2 / PI ** 2
    return {"I": I, "M2": M2, "M3": M3, "M2_over_I": M2 / I, "M3_over_I": M3 / I,
            "J": (M2 + M3) / I - mp.mpf(1) / 4, "last_M3_term": abs(last3), "max_last_M2_term": last2}


def fmt(d):
    return {k: mp.nstr(val, 22) for k, val in d.items()}


if __name__ == "__main__":
    out = {"ell": "16/15", "a": str(a), "mu1": str(mu1), "mu2": str(mu2), "dps": mp.mp.dps}
    trials = {"trial_f_plus_gS": f_poly + g_poly * S, "mass_only_f": f_poly, "H_equals_1": sp.Integer(1)}
    for name, H in trials.items():
        res = schema(H)
        out[name] = fmt(res)
        print(name, json.dumps(out[name], indent=1))
    cert = [-0.014662375473368995, -0.014662375473368974]
    Jt = mp.mpf(out["trial_f_plus_gS"]["J"])
    out["astra_certificate_enclosure"] = cert
    out["trial_J_inside_certificate"] = bool(cert[0] <= float(Jt) <= cert[1])
    print("trial J =", mp.nstr(Jt, 20), " inside Astra enclosure:", out["trial_J_inside_certificate"])
    Path(__file__).with_name("f1_continuum_results.json").write_text(json.dumps(out, indent=2))
