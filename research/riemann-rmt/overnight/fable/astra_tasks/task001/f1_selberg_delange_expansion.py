"""Three-term Selberg-Delange expansions of the marked sums, compared with exact sieve values (Fable task001 / F1).

Sigma_j(x) = sum_{n<=x} d_ell(n)^2 S~(n)^j / n,   S~(n) = sum_{p|n} (log p)^2  (L-independent; S2 = S~/(log L)^2).
Dirichlet series (exact, from the marked Euler product F(s,theta) = prod_p (1 + e^{theta lambda_p} E_p(s)), differentiated at 0):
  D_0 = F,  D_1 = F * Pi_2,  D_2 = F * (Pi_2^2 + Pi_4),   F = zeta^a G,
  Pi_2 = sum_p (log p)^2 rho_p,  Pi_4 = sum_p (log p)^4 rho_p (1 - rho_p),  rho_p = E_p/(1+E_p),  E_p = sum_{e>=1} d_ell(p^e)^2 p^{-es}.
Laurent data at s = 1 + eps:
  (eps zeta)^a G / C = 1 + kappa_1 eps + kappa_2 eps^2 + ...,   kappa_1 = a gamma_0 + G'/G(1),
  kappa_2 = a^2 gamma_0^2/2 - a (gamma_1 + gamma_0^2/2) + a gamma_0 G'/G + G''/(2G);
  sum_p (log p)^2 p^{-s} = 1/eps^2 + h_2(1) + O(eps),  h_2(1) = -(2 gamma_1 + gamma_0^2) - R_1(1),  R_1 = sum_p sum_{e>=2} e (log p)^2 p^{-e};
  Pi_2 = ell^2/eps^2 + pi_0 + O(eps),   pi_0 = ell^2 h_2(1) + R_2(1),  R_2(1) = sum_p (log p)^2 (rho_p(1) - ell^2/p);
  sum_p (log p)^4 p^{-s} = 6/eps^4 + O(1)  (no eps^-3, eps^-2, eps^-1 terms because -zeta'/zeta has a simple pole).
Hankel/Perron:  sum_{n<=x} f(n)/n = sum_k K_k (log x)^{z-k}/Gamma(z+1-k)  when  sum f(n) n^{-s} = eps^{-z} sum_k K_k eps^k.
Hence (lx = log x)
  Sigma_0 = C [ lx^a/G(a+1) + k1 lx^{a-1}/G(a) + k2 lx^{a-2}/G(a-1) ] + O(lx^{a-3})
  Sigma_1 = C [ l2 lx^{a+2}/G(a+3) + l2 k1 lx^{a+1}/G(a+2) + (l2 k2 + pi_0) lx^a/G(a+1) ] + O(lx^{a-1})
  Sigma_2 = C [ m lx^{a+4}/G(a+5) + m k1 lx^{a+3}/G(a+4) + (m k2 + 2 l2 pi_0) lx^{a+2}/G(a+3) ] + O(lx^{a+1}),   m = ell^4 + 6 ell^2.
The script verifies the Laurent identities numerically with mpmath (Stieltjes constants) and prints the scaled residuals
(exact - k-term prediction) / (C lx^{power of the next term}), which must stabilise if the expansion is right.
Status label: finite numerical check of a proved (recalled Selberg-Delange) asymptotic expansion.  Output: f1_sd_expansion_results.json
"""
from __future__ import annotations
import json, sys, time
from math import gamma, log
from pathlib import Path
import numpy as np
import mpmath as mp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from f1_common import ELL, sieve_d_S, primes_upto, d_ell_powers

mp.mp.dps = 40
ell = ELL; a = ell * ell
P = 10 ** 7
t0 = time.time()

# ---- Laurent coefficients of zeta at s = 1 from Stieltjes constants: eps*zeta(1+eps) = 1 + sum_n (-1)^n gamma_n eps^{n+1}/n!
g = [mp.stieltjes(n) for n in range(5)]
def series_mul(A, B, N):
    return [mp.fsum(A[i] * B[k - i] for i in range(k + 1) if i < len(A) and k - i < len(B)) for k in range(N)]
def series_log1p(u, N):          # log(1+u) for a series u with u[0] = 0
    out = [mp.mpf(0)] * N; pw = [mp.mpf(0)] + u[1:N]
    term = pw[:]
    for k in range(1, N):
        for i in range(N): out[i] += ((-1) ** (k + 1)) * term[i] / k
        term = series_mul(term, pw, N)
    return out
N = 6
ez = [mp.mpf(1)] + [(-1) ** n * g[n] / mp.factorial(n) for n in range(N - 1)]     # eps*zeta series
logez = series_log1p(ez, N)                                                          # c_1 eps + c_2 eps^2 + ...
# -zeta'/zeta = 1/eps - d/deps log(eps zeta) = 1/eps - sum_k k c_k eps^{k-1}
c = logez
h2_zeta_part = -2 * c[2]              # (zeta'/zeta)'(s) = 1/eps^2 + ( -2 c_2 ) + 6 c_3 eps + ...
h4_zeta_part = 24 * c[4]              # (zeta'/zeta)'''(s) = 6/eps^4 + 24 c_4 + O(eps)
# numerical verification of both Laurent identities
def zz1(s): return mp.diff(lambda t: mp.zeta(t, derivative=1) / mp.zeta(t), s)
def zz3(s): return mp.diff(lambda t: mp.zeta(t, derivative=1) / mp.zeta(t), s, 3)
checks = {}
for eps in (mp.mpf('1e-3'), mp.mpf('5e-4')):
    checks[f"(zeta'/zeta)'(1+eps)-1/eps^2 at eps={eps}"] = mp.nstr(zz1(1 + eps) - 1 / eps ** 2, 12)
    checks[f"(zeta'/zeta)'''(1+eps)-6/eps^4 at eps={eps}"] = mp.nstr(zz3(1 + eps) - 6 / eps ** 4, 12)
checks["predicted limits"] = {"-2c2 = -(2 gamma_1 + gamma_0^2)": mp.nstr(h2_zeta_part, 12), "24 c4": mp.nstr(h4_zeta_part, 12),
                              "check -(2g1+g0^2)": mp.nstr(-(2 * g[1] + g[0] ** 2), 12)}
print("Laurent checks:", json.dumps(checks, indent=1), flush=True)

# ---- prime sums for G'/G, G''/G, R_1, R_2 (primes <= P)
ps = primes_upto(P).astype(float); lp = np.log(ps); inv = 1 / ps
de = d_ell_powers(ell, 90)
E = np.zeros_like(ps); E1 = np.zeros_like(ps); E2 = np.zeros_like(ps); R1 = 0.0
pe = np.ones_like(ps)
for e in range(1, 91):
    pe = pe * inv; term = de[e] ** 2 * pe
    E += term; E1 += e * term; E2 += e * e * term
    if e >= 2:
        R1 += float(np.sum(e * lp ** 2 * pe))            # sum_p sum_{e>=2} e (log p)^2 p^-e
Ap1 = a * lp / (ps - 1) - lp * E1 / (1 + E)                                   # A_p'(1)
Ap2 = -a * lp ** 2 * inv / (1 - inv) ** 2 + (lp ** 2 * E2 * (1 + E) - lp ** 2 * E1 ** 2) / (1 + E) ** 2   # A_p''(1)
GpG = float(np.sum(Ap1)); logG2 = float(np.sum(Ap2)); GppG = logG2 + GpG ** 2
rho = E / (1 + E)
R2 = float(np.sum(lp ** 2 * (rho - a * inv)))
logC = float(np.sum(a * np.log1p(-inv) + np.log1p(E))); C = float(np.exp(logC))
g0, g1 = float(g[0]), float(g[1])
k1 = a * g0 + GpG
k2 = a * a * g0 ** 2 / 2 - a * (g1 + g0 ** 2 / 2) + a * g0 * GpG + GppG / 2
h2 = float(h2_zeta_part) - R1
pi0 = a * h2 + R2
m4 = a * a + 6 * a
consts = {"C": C, "GpG": GpG, "GppG": GppG, "kappa1": k1, "kappa2": k2, "R1": R1, "R2": R2, "h2(1)": h2, "pi0": pi0,
          "gamma0": g0, "gamma1": g1, "P": P}
print("constants:", json.dumps(consts, indent=1), flush=True)

# ---- exact sums
X = 10 ** 7
d, St = sieve_d_S(X, ell)
n = np.arange(X + 1, dtype=float)
w0 = np.zeros(X + 1); w0[1:] = d[1:] ** 2 / n[1:]
w1 = w0 * St; w2 = w1 * St
rows = []
for x in (10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7):
    lx = log(x)
    s0 = float(np.sum(w0[:x + 1])); s1 = float(np.sum(w1[:x + 1])); s2 = float(np.sum(w2[:x + 1]))
    p0 = [C * lx ** a / gamma(a + 1), C * k1 * lx ** (a - 1) / gamma(a), C * k2 * lx ** (a - 2) / gamma(a - 1)]
    p1 = [C * a * lx ** (a + 2) / gamma(a + 3), C * a * k1 * lx ** (a + 1) / gamma(a + 2), C * (a * k2 + pi0) * lx ** a / gamma(a + 1)]
    p2 = [C * m4 * lx ** (a + 4) / gamma(a + 5), C * m4 * k1 * lx ** (a + 3) / gamma(a + 4), C * (m4 * k2 + 2 * a * pi0) * lx ** (a + 2) / gamma(a + 3)]
    row = {"x": x, "log_x": lx}
    for j, (s, p) in enumerate(((s0, p0), (s1, p1), (s2, p2))):
        pw = a + 2 * j
        row[f"Sigma{j}"] = s
        for k in (1, 2, 3):
            pred = sum(p[:k]); row[f"S{j}_rel_err_{k}term"] = s / pred - 1
            row[f"S{j}_scaled_resid_{k}term"] = (s - pred) / (C * lx ** (pw - k))     # should approach the next coefficient
    rows.append(row)
    print(f"x=10^{round(lx/log(10))}: " + " | ".join(
        f"S{j}: rel1 {row[f'S{j}_rel_err_1term']:+.4f} rel2 {row[f'S{j}_rel_err_2term']:+.5f} rel3 {row[f'S{j}_rel_err_3term']:+.6f}"
        f" scaled3 {row[f'S{j}_scaled_resid_3term']:+.4f}" for j in range(3)), flush=True)
out = {"constants": consts, "laurent_checks": checks, "rows": rows, "seconds": time.time() - t0,
       "next_coefficients_expected": "scaled_resid_3term should tend to the 4th Laurent/Hankel coefficient (a constant), i.e. relative error O((log x)^-3)"}
Path(__file__).with_name("f1_sd_expansion_results.json").write_text(json.dumps(out, indent=2, default=str))
print("done", f"{time.time()-t0:.1f}s")
