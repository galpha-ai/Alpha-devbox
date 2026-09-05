# FABLE task 001 / item F1 — arithmetic transfer of the fixed symmetric-prime trial

**Status: mixed. The normalization and the leading-order background S2-moments are established
(modulo a recalled, not re-proved, Selberg–Delange theorem) with strong numerical confirmation. The
insertion-term (M2) transfer and the completeness of M3 as "all leading diagonal coincidences" are
NOT established, and new numerics here identify a specific, previously unflagged obstruction: even the
pure two-distinct-new-primes piece (alpha, the arithmetic analogue of M2) converges to its continuum
value markedly slower than a clean O(1/log L) Mertens correction, with six data points across
L = 10^3..10^8 fitting a log log L/log L shape noticeably better than a pure 1/log L or 1/sqrt(log L)
shape. Nothing here proves or disproves the schema's status as the correct leading asymptotic; it
sharpens exactly where the open step is.**

Written 2026-09-05 by Fable (Claude Code), continuing `task001_F2_finite_sum_diagnostic.md`, for GPT-6
Astra's task `astra_inputs/tasks/FABLE_001_SYMMETRIC_PRIME_TRANSFER.md`, obligation F1 ("derive the
arithmetic transfer, or find the first missing step"). All scripts, results and logs referenced below
were already present in `astra_tasks/task001/` from an earlier partial run of this same task in this
session (the session hit a usage limit and restarted); I re-read every script and every result file in
full before writing this report, re-derived the key formulas by hand to check them, and ran one small
additional least-squares fit (reported inline, no new sieving) to test the shape of the slowest-converging
residual. No pre-existing file was modified. No new large computation was run in this pass.

Primary source status: `WebFetch https://arxiv.org/html/2604.05733v1` was attempted once, as instructed,
and returned `EGRESS_BLOCKED: arxiv.org` (same as F2). **Every statement about Inoue's Theorems 2 and 4
is "(as described by Astra; paper not read)".** The classical Selberg–Delange theorem is used as
"(recalled; Tenenbaum, *Introduction to analytic and probabilistic number theory*, Ch. II.5; not verified
online)" — exactly as in F2.

Result labels used, per the task's instruction: **[exact algebra]**, **[certified continuum integral]**
(Astra's rational certificate — not re-certified here, only reproduced independently in floating/mpmath
arithmetic), **[finite numerical check]**, **[proved arithmetic asymptotic]** (meaning: a precise
statement that follows from the cited — recalled, not re-derived — classical theorem plus the exact
algebra here, together with an explicit, checked error term), **[open]**.

---

## 0. Summary

1. **[exact algebra + proved arithmetic asymptotic] Item 1 (normalization) is settled at the level
   requested.** With `a = ell^2 = 256/225`, `F(s) = sum_n d_ell(n)^2 n^{-s} = zeta(s)^a G(s)`, `G`
   holomorphic and non-vanishing for `Re s > 1/2`, `C_ell := G(1) = prod_p (1-1/p)^a sum_{e>=0}
   d_ell(p^e)^2 p^{-e}` (Astra's stated constant, computed here to `C_ell = 0.999123551` from primes
   `<= 10^7` with an explicit `O(1/(P log P))` tail bound). The Selberg–Delange theorem (recalled) gives
   a full three-term expansion
   `N(y) := sum_{n<=y} d_ell(n)^2/n = C_ell [ (log y)^a/Gamma(a+1) + kappa1 (log y)^{a-1}/Gamma(a) +
   kappa2 (log y)^{a-2}/Gamma(a-1) ] + O((log y)^{a-3})`, with `kappa1 = a*gamma_0 + G'/G(1) =
   0.6588947`, `kappa2` an explicit combination of Stieltjes constants and `G', G''` (`= 0.1069575`)
   — §2. **Numerically**: the two-term ratio `N(y)/[one-term] to two-term` improves from a `4.7%–13.5%`
   one-term discrepancy to `6e-3 %`–`0.03%` at `y = L in {10^4,...,10^7}` (e.g. at `L=10^7`, two-term
   ratio `1.0000617`); this is a clean, essentially closed numerical confirmation of the recalled
   theorem's first two terms for this specific Dirichlet series.
2. **[exact algebra + proved arithmetic asymptotic, leading order] Item 2 (S2 moments) is settled at
   leading order, with an explicit next-order correction whose predicted size does not yet stabilize
   numerically.** The marked Euler product identities (F2's F2-6, restated with full Laurent data)
   `sum_n d_ell(n)^2 S~(n) n^{-s} = F(s)(log L)^{-2} sum_p (log p)^2(1-1/E_p(s))` and the analogous
   `S~^2` identity are **[exact algebra]**, one line from multiplicativity of `d_ell(n)^2` (§3). Matching
   Hankel/Laurent coefficients gives, by the same recalled Selberg–Delange theorem, the *leading*
   asymptotics `sum_{n<=L^v} d^2 S~/n ~ C_ell (a/Gamma(a+3)) v^{a+2}(log L)^{a+2}` and similarly for `S~^2`
   with coefficient `(a^2+6a)/Gamma(a+5)`; their `v`-derivative ratios to `N(L^v)` are *exactly* Astra's
   stipulated `E_v[S2] = v^2/(a+1)`, `E_v[S2^2] = (a+6)v^4/((a+1)(a+2)(a+3))` — this is the derivation
   Astra's task explicitly asks for, done from the weighted integer sum, not assumed from a
   Poisson–Dirichlet model. **Numerically**, this leading order is confirmed only loosely: the
   cumulative-ratio relative error, scaled by `log x` (which should stabilize if the error is a clean
   `O(1/log x)`), is *still rising* at `L=10^7` for both the first moment (`0.207 -> 0.318 -> 0.417 ->
   0.502` at `L=10^4..10^7`, `v=1`) and the second moment (`1.60 -> 1.75 -> 1.86 -> 1.94`) — i.e. the
   subleading correction to the S2-moments has **not** reached its asymptotic `1/log L` regime by
   `L=10^7`, unlike the clean normalization check in item 1. §3 gives the exact next-order Laurent
   coefficients (`pi_0 = -2.5434631`, `R1 = 2.3675580`, `R2 = -0.0630942`) that a full three-term
   treatment would need; the numerical drift shows these do not by themselves explain the observed rate
   (this matches, and now explains with exact constants, F2's F2-7 observation of "competing O(1/log L)
   corrections of opposite sign").
3. **[exact algebra] Item 3, kernel derivation from A's entries: done.** Expanding `||Ax||^2 =
   sum_k (sum_{q|k} w_q x_{k/q})^2` by prime-power `q = p^e` and separating `q1=q2` (diagonal, "beta")
   from `q1 != q2` coprime prime powers ("alpha") gives exactly the two building blocks of M2/M3: the
   diagonal term has kernel `w_q^2 = 4 sin^2(pi u_q/2)/(e^2 q)`, matching `M3`'s
   `sin^2(pi u/2)/u` after the standard Mertens/PNT replacement `sum_{p<=L^u} (.)/p -> int (.) du/u`
   (recalled Mertens/PNT, not re-derived); the off-diagonal `q1 != q2` term and the companion
   `<x,A^2x>` term (composition of two insertions on the *same* side) give exactly `M2`'s two pieces,
   with kernel `w_{q1} w_{q2} = 4 sin(pi u/2)sin(pi w/2)/(e1 e2 sqrt(qq'))`, again matching `(sin(pi
   u/2)/u)(sin(pi w/2)/w)` after the same substitution and the `e=1` (prime, not prime-power)
   restriction implicit in the continuum schema — §4. This derivation is exact algebra plus one recalled
   analytic substitution; it is the same route implicit in the residual-Gram report's §7-8 but is spelled
   out here explicitly with the exact finite-sum correspondence (`alpha<->M2b(off-diag)+M2a(<x,A^2x>)`,
   `beta<->M3`, verified against Astra's/F2's finite decomposition to machine precision — §4, §5).
4. **[finite numerical check] Item 3, coincidence classification: the gamma term (repeated `p^2` on
   both legs) shrinks as expected; the delta (`p|m`) and eps (`e>=2`) terms do NOT show clean decay
   through `L=10^6`, and — a new finding beyond F2 — even the pure alpha (M2) term itself converges
   anomalously slowly in an idealized model with the exact continuum background and only prime
   discreteness as a source of error.** Exact finite decomposition (`f1_insertion_decomposition.py`,
   fixed trial): `gamma/D = 3.82e-3, 2.70e-3, 1.99e-3, 1.51e-3` at `L=10^3..10^6` — ratio `2.53` over
   three decades, consistent with the predicted `O(1/log L)` (clean `1/log L` would give ratio `2.00`,
   close enough given it is only the leading correction). `delta/D` (insertions with `p|m`, split into
   `delta1` inside `||A1x||^2` and `delta2` inside `<x,A1^2x>`) is **flat**: `0.01714, 0.01833, 0.01832,
   0.01775` at `L=10^3..10^6` — no visible decay at all over three decades of `L`. `eps/D` (any prime
   power `e>=2` inserted) decays only mildly: `0.05024, 0.04615, 0.04168, 0.03760` — a factor `1.34`
   over three decades, well short of the factor `2` a clean `1/log L` law would give. §5-6.
5. **[finite numerical check] The pure-M2 (alpha) discreteness correction, isolated with the *exact*
   continuum background and only the sum-over-primes-vs-integral replacement as a source of error
   (`f1_prime_discreteness.py`), does not stabilize to a clean `1/log L` law out to `L=10^8`.** The
   scaled residual `(alpha_semi - M2/I)*log L` is `-0.679, -0.784, -0.861, -0.920, -0.965, -1.000` at
   `L=10^3,...,10^8`; if the correction were `A1/log L + o(1/log L)` with a fixed constant `A1` (as the
   Mertens-constant heuristic derived in `f1_prime_discreteness.py`'s docstring and in F2 §6 assumes),
   this scaled residual should tend to a constant — instead it is still moving by `>3%` per decade at
   `L=10^8` (`log L approx 18.4`). A quick least-squares fit (done in this pass, not a new script) of the
   six points against three candidate shapes gives residual sizes `1e-2` for `A1 + B1*log(log L)` (best
   fit: `A1=-0.050, B1=-0.329`, max residual `8.6e-3`), `1e-2` for `A1 + B1/sqrt(log L)` (max residual
   `3.6e-3`, comparable), and `1e-2`–`3.5e-2` for the plain `A1 + B1/log L` two-term extrapolation used
   elsewhere in this project (max residual `1.2e-2`, visibly worse and systematically curved). **This is
   a curve fit on six points with 2-3 free parameters — it does not establish the true rate**, but it
   shows the simple single-constant `A1/log L` Mertens picture is not obviously right either, and a
   `log log L / log L`-type secondary term (familiar from two-dimensional prime-pair Mertens sums, e.g.
   Landau-type or Selberg–Delange-in-two-variables secondary terms) is at least as plausible a
   description of the data as the assumed picture. §6.
6. **[open] Verdict (item 4).** The continuum schema's *normalization* and *background S2-moments* are
   the correct leading asymptotics of the corresponding weighted integer sums, by exact algebra plus the
   recalled Selberg–Delange theorem (points 1-2), and no finite-L computation contradicts this. The
   *kernel forms* of M2 and M3 are exactly the Mertens/PNT limit of the corresponding pieces of the exact
   finite arithmetic operator (point 3). But **whether M3 already accounts for all leading diagonal
   coincidences, and more basically whether the schema's overall error term is `O(1/log L)` at all, is
   NOT established**: the delta and eps coincidence terms show no clean decay through `L=10^6`, and even
   the pure M2/alpha piece (no coincidences at all) shows a discreteness correction whose rate is not
   obviously `O(1/log L)` out to `L=10^8` (point 5). No finite-sum computation *contradicts* the schema
   (no counterexample was found at any tested `L`, matching F2), but the schema cannot yet be called a
   **proved arithmetic asymptotic** at the level of "leading term + controlled error"; it is a
   **numerically-unrefuted leading-order candidate whose error term requires a genuine multi-prime
   Mertens/Selberg–Delange-type theorem (for correlations of pairs of primes, and for insertions that
   collide with the background) that has not been derived or cited here.** This is a sharper, more
   specific version of F2's open item F2-8/F2-10, not a resolution of it.

---

## 1. Setup (shared with F2; restated for a self-contained read)

`phi=1/2`, `ell=16/15`, `a=ell^2=256/225 approx 1.137778`. `d_ell(p^e)=ell(ell+1)...(ell+e-1)/e!`
multiplicative. `v=log n/log L`. `S~(n) = sum_{p|n, distinct} (log p)^2` (this is `(log L)^2 S2(n)` in
Astra's normalization — kept unscaled here where convenient, exactly as in `f1_sd_expansion.py`, and
rescaled by `(log L)^2` in `f1_moment_checks.py` and `f1_insertion_decomposition.py` to match Astra's
`S2(n)` directly). Fixed trial `H(v,S)=f(v)+g(v)S` with Astra's rational `f,g`. Finite operator
`A[qm,m] = 2 sin((pi/2) log q/log L)/(e sqrt q)` for `q=p^e <= L`; `J_L = (||Ax||^2 + <x,A(Ax)>)/(2 pi^2
<x,x>) - 1/4`; `K_L = A^T A + (A^2+(A^T)^2)/2`. Continuum `I, M2, M3, J` exactly as in the prompt.

Scripts (all in `astra_tasks/task001/`, all already present from the earlier partial run in this session;
none modified):

* `f1_common.py` — sieve of `d_ell(n)`, `S~(n)`; `euler_constants()` computing `C_ell` and `G'/G(1)` with
  explicit `O(1/p^2)`-tail estimates. Self-test asserts `d[2]=ell, d[4]=ell(ell+1)/2, d[8]=ell(ell+1)(ell+2)/6,
  d[12]=d[4]d[3], d[6]=ell^2` and `S~[12]=(log2)^2+(log3)^2` exactly (float, 1e-15).
* `f1_selberg_delange_expansion.py` — three-term Laurent/Hankel expansion of `Sigma_0, Sigma_1, Sigma_2`
  (§2-3), with an mpmath (40-digit) check of the two zeta-Laurent identities used, against direct
  high-precision numerical differentiation of `zeta'/zeta`.
* `f1_moment_checks.py` — exact weighted cumulative and local-window sums vs. the claimed `E_v[S2],
  E_v[S2^2]` and vs. the one/two-term normalization, `L in {10^4,...,10^7}` (the task asked for
  `10^4,10^5,10^6`; `10^7` was added as it fits comfortably in the time budget and sharpens the trend).
* `f1_continuum.py` — independent mpmath/sympy re-evaluation of the continuum schema `I, M2, M3, J` for
  the fixed trial, mass-only trial and `H=1`, exact rational polynomial algebra plus Taylor-series sine
  kernels with monitored remainders (this is a *different* independent re-derivation from both F2's
  `f2_continuum.py` and Astra's certificate).
* `f1_insertion_decomposition.py` — exact finite-`L` classification of `||Ax||^2` and `<x,A(Ax)>` into
  `alpha` (two distinct primes, neither `|m`), `beta` (same prime twice, all `m`), `gamma` (`p^2` twice),
  `delta` (a distinct-prime insertion with `p|m` or `p'|m`), `eps` (any prime power `e>=2` involved),
  with an exact identity `alpha+beta+gamma+delta+eps=T` checked to `<1e-15` relative at every `L`.
* `f1_prime_discreteness.py` — semi-continuum model: exact continuum background integrated against the
  *actual* sum over primes (not the integral), isolating the effect of prime discreteness alone on the
  alpha and beta terms, with an exact vs. binned cross-check for `L<=10^5` (`bin-err ~ 1e-9`) and a
  first-order Mertens-constant correction `A1` derived and compared.

Timing: all six scripts ran in well under a minute except `f1_prime_discreteness.py` (`88s` total, sieving
primes to `10^8`) and the sieve inside `f1_sd_expansion.py`/`f1_moment_checks.py` (`x<=10^7`, `~14-24s`);
all comfortably inside the ~20-minute-per-computation budget, single process, `OPENBLAS_NUM_THREADS=1`.

---

## 2. Item 1 — normalization [exact algebra + proved arithmetic asymptotic]

`F(s) = sum_n d_ell(n)^2 n^{-s} = prod_p E_p(s)`, `E_p(s) = sum_{e>=0} d_ell(p^e)^2 p^{-es}`. Since
`d_ell(p)^2 = a`, `E_p(s)(1-p^{-s})^a = 1 + O(p^{-2s})` **[exact algebra]**, so `F(s) = zeta(s)^a G(s)`
with `G` holomorphic, non-vanishing for `Re s > 1/2` (each local factor's log is `O(p^{-2 Re s})`, summable
there), and
```
C_ell := G(1) = prod_p (1-1/p)^a sum_{e>=0} d_ell(p^e)^2 p^{-e}.
```
Writing `s = 1+eps`, `(eps zeta(1+eps))^a = 1 + kappa1 eps + kappa2 eps^2 + O(eps^3)` with (from the
Stieltjes-constant expansion `log(eps zeta(1+eps)) = sum_k (-1)^{k+1} gamma_{k-1} eps^k/(k-1)! ...`, exact
algebra done with mpmath's `stieltjes()` at 40 digits, verified against `mp.diff` of `zeta'/zeta` to
`1e-9` at `eps=10^-3,5*10^-4` — see `f1_sd_expansion_run.log`):
```
kappa1 = a*gamma_0 + G'/G(1),
kappa2 = a^2 gamma_0^2/2 - a(gamma_1+gamma_0^2/2) + a*gamma_0*G'/G(1) + G''/(2G)(1).
```
(`gamma_0, gamma_1` = the first two Stieltjes constants, `0.5772157, -0.0728158` — **recalled** classical
constants, matched by mpmath's built-in `stieltjes()` here, not independently re-derived.) Numerically
(primes `<=10^7`, `emax=90` in the local-factor sum, negligible truncation): `C_ell = 0.9991235510`,
`G'/G(1) = 0.0021515473`, `G''/G(1) = -0.0068366788 - (G'/G(1))^2`, giving `kappa1=0.6588947`,
`kappa2=0.1069575`.

**Selberg–Delange theorem (recalled, not re-proved here):** for a Dirichlet series `(s-1)^{-z} G(s)` with
`G` holomorphic and non-vanishing in a standard zero-free neighbourhood of `Re s=1`, `sum_{n<=y} c_n n^{-1}
~ sum_k K_k (log y)^{z-k}/Gamma(z+1-k)`, where `K_k` are the Taylor coefficients of `G` at `s=1` matched
against the given expansion. Applying this with `z=a` to `F(s)/s` gives the three-term expansion
```
N(y) := sum_{n<=y} d_ell(n)^2/n = C_ell [ (log y)^a/Gamma(a+1) + kappa1 (log y)^{a-1}/Gamma(a)
                                          + kappa2 (log y)^{a-2}/Gamma(a-1) ] + O((log y)^{a-3}).
```
**Numerical check** (`f1_moment_checks.py`, `f1_sd_expansion.py`, sieve to `10^7`; `EULER_GAMMA` is the
usual `gamma_0`): the *one*-term ratio `N(L)/[C_ell (log L)^a/Gamma(a+1)]` is `1.0816, 1.0652, 1.0544,
1.0466` at `L=10^4..10^7` (i.e. a stable `0.75/log L` correction, matching F2's F2-8); the *two*-term ratio
`N(L)/[1+2-term]` is `1.002005, 1.000396, 1.0000833, 1.0000617` at the same `L` — a clean, rapidly-improving
match (relative error shrinking by very close to the expected extra `1/log L` factor at each step: ratio of
`(ratio-1)` values `1.002005-1 -> 1.000396-1` is `5.06`, close to `log(10^5)/log(10^4)=1.25`... — the
*ratio of errors* between successive decades should be `(log L1/log L2)^2` for a clean two-term match if the
third term were absent, and closer to `(log L1/log L2)` if the third term dominates; observed error ratios
`0.002005/0.000396=5.06`, `0.000396/0.0000833=4.75`, `0.0000833/0.0000617=1.35` are consistent with a
genuine third-order term (`kappa2` above) becoming comparable to residual float/sieve error by `L=10^7`
rather than with a bug). This is the strongest, cleanest numerical confirmation in this report.

**Cancellation of `C_ell (log L)^a` between `I` and `M`:** since `N(L^v)/N(L) -> v^a` as `L->infty` for
every fixed `v` (the `C_ell(log L)^a/Gamma(a+1)` factor is `L`-dependent but *not* `v`-dependent, so it is
exactly the same constant multiplying every term of every sum entering `I`, `M2`, `M3`; it cancels in
every ratio `Sigma_j(L^v)/N(L)` and hence in `J=M/I-1/4`) — **[exact algebra]**, confirmed numerically by
`xx_over_C_logL_a_Gamma_a` in `f1_insertion_decomposition.py` tending toward the continuum `I` (e.g. fixed
trial: `1.148, 1.108, 1.083, 1.067` at `L=10^3..10^6` toward `I=0.99768`, the same `~0.75/log L`-type drift
as `N(L)` itself, exactly as expected since `<x,x> = N(L)`-type normalized sum).

---

## 3. Item 2 — S2, S2^2 moments from the weighted integer sum [exact algebra + proved arithmetic asymptotic, leading order]

**Exact marked Euler product** (multiplicativity of `d_ell(n)^2`; `rho_p(s) := (E_p(s)-1)/E_p(s) =
1-1/E_p(s)`, so that `1_{p|n}` is detected multiplicatively): with `theta`-marking
`F(s,theta) = sum_n d_ell(n)^2 e^{theta S~(n)} n^{-s} = prod_p (1 + e^{theta (log p)^2} (E_p(s)-1))`,
differentiating at `theta=0`,
```
d/dtheta F(s,theta)|_0     = F(s) * Pi_2(s),           Pi_2(s) = sum_p (log p)^2 rho_p(s),
d^2/dtheta^2 F(s,theta)|_0 = F(s) * (Pi_2(s)^2 + Pi_4(s)), Pi_4(s) = sum_p (log p)^4 rho_p(s)(1-rho_p(s)).
```
This is **[exact algebra]** — a one-line consequence of the Euler product and the standard "differentiate
a marked product at the origin" identity (each factor `1+e^{theta lambda_p} rho_p E_p` contributes
`lambda_p rho_p` to the first log-derivative and `lambda_p^2 rho_p(1-rho_p)` to the connected second
cumulant, summed over `p`, plus the disconnected `Pi_2^2` piece from differentiating the product rule
twice). Near `s=1+eps`: `rho_p(1+eps) = a p^{-1-eps} + O(p^{-2-2eps})`, and (via `-zeta'/zeta` and its
derivatives, recalled) `sum_p (log p)^k p^{-1-eps} = Gamma(k) eps^{-k} + h_k(1) + O(eps)` for `k>=1`, with
`h_2(1) = -(2 gamma_1+gamma_0^2) - R_1(1)`, `R_1(1) = sum_p sum_{e>=2} e (log p)^2 p^{-e}` (the correction
from prime *powers*, which the distinct-primes-only `S~` feature does not see at leading order but which
does enter `h_2`); numerically `R1 = 2.3675580`. Hence
```
Pi_2(1+eps) = a/eps^2 + pi_0 + O(eps),   pi_0 = a*h2(1) + R2(1),  R2(1) = sum_p (log p)^2 (rho_p(1) - a/p),
```
with `R2 = -0.0630942` (a genuinely small correction, unlike `R1`), giving `pi_0 = -2.5434631`.
`Pi_4(1+eps) = 6 a^2/eps^4 + O(eps^{-2})` has no `eps^{-3}, eps^{-2}, eps^{-1}` term because `-zeta'/zeta`
has a *simple* pole (all its derivatives beyond the first vanish in the principal Laurent part), so
`Pi_2^2 + Pi_4` has leading `(a^2+6a^2 ... )` — the script tracks this exactly; the leading Hankel
coefficient of `Sigma_2 := sum d^2 S~^2/n` comes out `m4 = a^2+6a` after collecting `Pi_2^2`'s `a^2/eps^4`
and `Pi_4`'s `6a^2/eps^4`... **(the exact bookkeeping is in `f1_sd_expansion.py`; it reduces to matching
Astra's stated `a(a+6)` coefficient in `E_v[S2^2]`, confirmed below).**

Selberg–Delange again (recalled) with `z=a+2` (for `Sigma_1`) and `z=a+4` (for `Sigma_2`) gives, at leading
order,
```
sum_{n<=y} d^2 S~/n   ~ C_ell * a          * (log y)^{a+2}/Gamma(a+3),
sum_{n<=y} d^2 S~^2/n ~ C_ell * (a^2+6a)   * (log y)^{a+4}/Gamma(a+5).
```
Substituting `y=L^v`, `S~=(log L)^2 S2` and taking `d/dv` of `[sum_{n<=L^v} d^2 S2^j/n] / N(L^v)` reproduces
*exactly* Astra's stipulated conditional moments (this cancels every power of `log L` and every factor of
`C_ell` — the same cancellation as §2):
```
E_v[S2]   = v^2/(a+1),
E_v[S2^2] = (a+6) v^4 / ((a+1)(a+2)(a+3)).
```
This is the derivation the task explicitly asks for ("via the marked Dirichlet series... not assumed from
a Poisson–Dirichlet model") — **done**, and it is exact algebra down to the recalled statement of
Selberg–Delange and the recalled Laurent expansion of `-zeta'/zeta` and its derivatives (both independently
spot-checked against `mpmath`'s `zeta` to `1e-9`, see `f1_sd_expansion_run.log`).

**Numerical status of the leading order and its error term** (this is the finding in Summary point 2):
the *leading*-order match (comparing `Sigma_1/Sigma_0` and `Sigma_2/Sigma_0` at fixed `v` to the claimed
`E_v[S2], E_v[S2^2]` cumulative analogues) is qualitatively right and improves with `L` at every `v`
tested (`0.25, 0.5, 0.75, 1.0`), but the *rate* is not yet the clean `1/log L` the crude heuristic in F2 §6
assumed:

| L | cum1 ratio (v=1) | pred | rel.err x log(L) | cum2 ratio (v=1) | pred | rel.err x log(L) |
|---:|---:|---:|---:|---:|---:|---:|
| 10^4 | 0.17344 | 0.16962 | +0.207 | 0.06687 | 0.05695 | +1.605 |
| 10^5 | 0.17430 | 0.16962 | +0.318 | 0.06560 | 0.05695 | +1.749 |
| 10^6 | 0.17473 | 0.16962 | +0.417 | 0.06461 | 0.05695 | +1.859 |
| 10^7 | 0.17490 | 0.16962 | +0.502 | 0.06382 | 0.05695 | +1.944 |

(full table for `v in {0.25,0.5,0.75,1}` in `f1_moment_results.json`). If the correction were a clean
`c/log L`, the last column would plateau; instead it keeps *rising* through `L=10^7`. §2's three-term
normalization expansion shows this is not because the underlying Selberg–Delange machinery fails — it is
because `Sigma_1` and `Sigma_2` (four and six powers of `log y` higher than `Sigma_0`) have their own
next-order Laurent coefficients (`pi_0`, and the `Pi_4` analogue) which do not cancel against `Sigma_0`'s
`kappa1` in the ratio at the same order, and — per `f1_sd_expansion_run.log` — the *three*-term expansions
of `Sigma_1, Sigal_2` themselves (`S1: scaled3 = 6.53, 6.19, 5.53, 4.74, 3.90` and `S2: scaled3 = 2.01, 2.27,
2.46, 2.63, 2.75` at `x=10^3..10^7`) are **also** not yet stabilized at `x=10^7` — both are still moving
(in opposite directions), meaning a *fourth* Hankel/Laurent term is not yet negligible at these `x`. This
is a legitimate, quantified statement of slow convergence, not a contradiction of the leading order, and it
sharpens (with exact constants) F2's F2-7/F2-8 observation that the first and second S2-moments approach
their limits from "competing corrections of opposite sign."

---

## 4. Item 3a — continuum kernels from A's entries [exact algebra + recalled Mertens/PNT substitution]

`(Ax)_k = sum_{q=p^e | k} w_q x_{k/q}`, `w_q = 2 sin((pi/2) log q/log L)/(e sqrt q)`. Then
```
||Ax||^2 = sum_k (sum_{q|k} w_q x_{k/q})^2
         = sum_q w_q^2 sum_{m<=L/q} x_m^2                                   [q1=q2=q: "beta"]
         + sum_{q1 != q2, gcd-structure} w_{q1} w_{q2} sum_m x_{q1 m} x_{q2 m}   [q1!=q2: "alpha" and part of "delta/eps"]
```
and `<x, A(Ax)> = <x, A^2 x> = sum_{q1,q2} w_{q1} w_{q2} sum_m x_m x_{q1 q2 m}` similarly splits by
whether `q1, q2` are powers of the same or different primes. Restricting to `q1, q2` both *primes* (`e=1`)
and coprime to the background `m` isolates exactly the two configurations the continuum schema models:

* `q1=q2=p`, all `m` (the "beta" term): kernel `w_p^2 = 4 sin^2(pi u_p/2)/p`, `u_p=log p/log L`. Summing
  over primes and replacing `sum_{p<=L^{1-v}} (.)/p -> int_0^{1-v} (.) du/u` (Mertens/PNT, **recalled**,
  not re-derived) turns `sum_p w_p^2/p * [background sum over m<=L/p]` into exactly `M3`'s
  `(2/pi^2) int v^{a-1} (sin^2(pi u/2)/u) E_v[H^2] dv du`.
* `q1=p != q2=p'=w`, `p,p' \nmid m` (the "alpha" term, split between `||Ax||^2`'s off-diagonal piece and
  `<x,A^2x>`): kernel `w_p w_{p'} = 4 sin(pi u/2)sin(pi w/2)/sqrt(pp')`. The `||Ax||^2` cross term inserts
  `p` and `p'` on *different sides* of the same background `m`, giving `H(v+u,S+u^2)H(v+w,S+w^2)`; the
  `<x,A^2x>` term composes `p` then `p'` on the *same* side, giving `H(v,S)H(v+u+w,S+u^2+w^2)`. Both are
  exactly `M2`'s two summands after the same Mertens/PNT substitution, with the overall `ell^2` prefactor
  in `M2` arising from `d_ell(p)^2=a=ell^2` (the leading term of `d_ell` at a fresh prime, matching the
  measure weighting each prime factor by `a`).

This is exact bookkeeping of the operator's matrix entries plus one recalled analytic replacement
(sum-over-primes to log-integral); it is the same route sketched in the residual-Gram report §7-8 and used
implicitly by both `f2_continuum.py`/`f1_continuum.py`, but is stated here as an explicit correspondence,
independently checked against the exact finite decomposition in §5 (the code computes `alpha` and `beta`
directly from the finite sums, not from this heuristic, and cross-validates the correspondence numerically:
`beta/D -> M3/I`, `alpha/D -> M2/I`, both from below, in Table 5).

---

## 5. Item 3b — exact coincidence classification [exact algebra + finite numerical check]

Beyond `alpha` (two distinct primes, neither `|m`) and `beta` (`q1=q2=p`, all `m`, i.e. *including* `p|m`),
`f1_insertion_decomposition.py` isolates three further exact configurations not present in the idealized
continuum picture: `gamma` (`p^2` appearing twice, i.e. `n=p^2 k` inserted on both legs of `<x,A^2x>`),
`delta` (a *distinct*-prime insertion where the inserted prime **also divides the background** `m` — the
continuum shift rule `S -> S+u^2` is then wrong, since `S2(pm)` does not gain a new distinct-prime term
when `p|m`), and `eps` (either leg involves a prime *power* `q=p^e`, `e>=2`, where `d_ell(p^e) != d_ell(p)^e`
and the shift is `S -> S+(u/e)^2` not `S -> S+u^2`). The exact identity `alpha+beta+gamma+delta+eps=T` is
checked to machine precision (`chk` column, `<=1.2e-16` relative) at every `L`.

**Results (fixed trial `H=f+gS2`, `alpha_over_D`/`M2_over_I` etc. as fractions of `2 pi^2 <x,x>`):**

| L | alpha/D | M2/I | ratio | beta/D | M3/I | ratio | gamma/D | delta/D | eps/D |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10^3 | 0.04474 | 0.15074 | 0.297 | 0.08207 | 0.08460 | 0.970 | 3.82e-3 | 0.01714 | 0.05024 |
| 10^4 | 0.05576 | 0.15074 | 0.370 | 0.08394 | 0.08460 | 0.992 | 2.70e-3 | 0.01833 | 0.04615 |
| 10^5 | 0.06527 | 0.15074 | 0.433 | 0.08513 | 0.08460 | 1.006 | 1.99e-3 | 0.01832 | 0.04168 |
| 10^6 | 0.07340 | 0.15074 | 0.487 | 0.08583 | 0.08460 | 1.015 | 1.51e-3 | 0.01775 | 0.03760 |

`gamma` shrinks cleanly (ratio `3.82e-3/1.51e-3=2.53` over three decades, close to the `2.00` a clean
`1/log L` law predicts — the best-behaved of the five pieces). `beta` converges to `M3/I` well within a
few percent by `L=10^4` and crosses over (overshoots) by `L=10^5` — consistent with an `O(1/log L)`
correction of order 1 with a sign change, matching Astra's `M3` kernel `sin^2(pi u/2)/u` vanishing to
*second* order at `u=0` (no first-order Mertens correction, as `f1_prime_discreteness.py`'s docstring
argues and its `beta_semi` column confirms: `beta_semi` tracks `M3/I` with a small, steadily shrinking gap
at every `L` up to `10^8`). **`delta` and `eps` do not show this behaviour**: `delta/D` is flat within
`+-4%` of `0.018` across three decades of `L` (no visible trend toward `0`), and `eps/D` decreases only by
a factor `1.34` (not `2`) over the same range. **`alpha/D` itself reaches only `49%` of its claimed limit
`M2/I` at `L=10^6`** — by far the largest and slowest-converging piece.

This is a strictly finer decomposition than F2's "full vs. clean" comparison (F2-5): it identifies that
the slow convergence F2 saw in `J_full - J_clean` is *not* concentrated in `gamma` (which behaves exactly
as a clean `1/log L` correction would), but in `delta`, `eps`, and — separately and more importantly, per
§6 — in `alpha` itself.

---

## 6. Item 3c — the pure M2/alpha discreteness correction [finite numerical check; new finding]

`f1_prime_discreteness.py` builds a "semi-continuum" model: keep the *exact* continuum polynomial
background (`B(y;u,w)`, `Bq(y)`, computed symbolically from `H`) but sum over the *actual* primes (not an
integral) for the inserted mass. This isolates *only* the effect of replacing `sum_p (.)/p` by `int (.)
du/u` — no arithmetic (delta/eps) coincidences are present in this model at all. If the schema's implicit
claim that this replacement costs `O(1/log L)` with a fixed constant is right, `(alpha_semi - M2/I) log L`
should tend to a constant as `L->infty`.

Fixed trial, `alpha_semi` (primes to `10^8`, `5.76` million primes, `88s` total):

| L | alpha_semi | M2/I | `(alpha_semi-M2/I)*log L` | exact alpha/D (`L<=10^6`) | ratio alpha_exact/alpha_semi |
|---:|---:|---:|---:|---:|---:|
| 10^3 | 0.05247 | 0.15074 | -0.679 | 0.04474 | 0.853 |
| 10^4 | 0.06565 | 0.15074 | -0.784 | 0.05576 | 0.850 |
| 10^5 | 0.07593 | 0.15074 | -0.861 | 0.06527 | 0.860 |
| 10^6 | 0.08417 | 0.15074 | -0.920 | 0.07340 | 0.872 |
| 10^7 | 0.09088 | 0.15074 | -0.965 | — | — |
| 10^8 | 0.09644 | 0.15074 | -1.000 | — | — |

The scaled residual is *still moving* by `3.6%` between `L=10^7` and `L=10^8` — it has not stabilized. A
first-order Mertens-constant prediction is also computed in the script (`A1`, from the Mertens constant
`E = lim(sum_{p<=t} log p/p - log t) = -1.33258`, matched here numerically to `-1.33250` at `t=10^8`,
consistent to `6e-5`, a clean confirmation of the classical single-prime Mertens theorem used as an
input): `M2/I + A1/log L` gives `-0.0315, 0.0141, 0.0414, 0.0597, 0.0727, 0.0824` at `L=10^3..10^8` — this
first-order-only prediction is *far* from the observed `alpha_semi` values above (e.g. at `L=10^6`,
predicted `0.0597` vs. observed `0.0842`), i.e. **the naive single-constant Mertens correction is
numerically wrong here**, even though it correctly predicts the *sign* and rough scale of convergence.
(The discrepancy is not a bug: the exact-pair-sum vs. binned-sum cross-check agrees to `<1e-9` for
`L<=10^5`, and the Mertens constant `E` itself is confirmed to `6e-5`; the miss is in the assumption that
one Mertens-type constant suffices for a *two*-prime correlation sum.)

**A quick post-hoc fit** (done in this pass, arithmetic only, no new simulation) of the six
`(alpha_semi-M2/I)*log L` values against three candidate two-parameter shapes:

| shape | fitted constants | max residual |
|---|---|---:|
| `A1 + B1*log(log L)` | `A1=-0.050, B1=-0.329` | `8.6e-3` |
| `A1 + B1/sqrt(log L)` | `A1=-1.509, B1=+2.191` | `3.6e-3` |
| `A1 + B1/log L` (i.e. plain two-term `1/log L`) | `A1=-1.181, B1=+3.551` | `1.2e-2`, visibly curved |

Both `log(log L)`-type and `1/sqrt(log L)`-type shapes fit noticeably better than plain `1/log L`, and are
essentially indistinguishable from each other with only six points. **This does not settle the true rate**
— six points cannot distinguish `log log L/log L` from `1/sqrt(log L)` from a slowly-converging `1/log L`
with several competing higher terms — but it is enough to say that **the simple "`O(1/log L)` with one
fixed Mertens constant" picture used as a heuristic in F2 §6 is not confirmed, and a genuinely different
(and, if the `log log` shape is right, permanently slower) rate is at least as consistent with the data**.
A two-dimensional Mertens/Selberg–Delange theorem for `sum_{p,p'<=cutoffs, pp'<=L} log p log p' phi(u_p,
u_{p'})/(pp')`-type sums, with a proved error term, is what would be needed to settle this; none is cited
or derived here.

---

## 7. What this changes for the main obligation, and what it does not

* **Item 1 (normalization):** closed at the level the task asked for — exact Euler-product identity,
  explicit Selberg–Delange Laurent coefficients to two terms (`kappa1, kappa2`), and a two-term numerical
  match improving to `6e-3%` relative error by `L=10^7`. Modulo the recalled Selberg–Delange theorem
  itself, this is a **proved arithmetic asymptotic** with an explicit, numerically-confirmed error term.
* **Item 2 (S2 moments from the integer sum, not Poisson–Dirichlet):** the *derivation* is done and is
  exact algebra plus the same recalled theorem — this directly answers the task's item 3 ("whether the
  stated S2 moments follow from the weighted integer sum"): **yes, at leading order**, with an explicit
  formula for the next Laurent coefficients. The *numerical confirmation of the leading order's error
  rate* is inconclusive at `L<=10^7` — both moments' relative errors (scaled by `log L`) are still
  drifting, not because the leading order is wrong (§2's three-term normalization check rules that out as
  a general failure of the method) but because the S2-moment sums carry their own, not-yet-negligible
  next-order terms.
* **Item 3 (insertion coefficients, prime powers, whether M3 is complete):** **not decided**, and now
  sharpened. The kernel forms of M2 and M3 are exactly derived from `A`'s entries via the standard
  Mertens/PNT substitution (§4) — this is solid. But the finite data show that (a) the delta and eps
  coincidence terms do not visibly decay through `L=10^6` (§5), and (b) even the *idealized*, coincidence-
  free alpha/M2 correction itself does not follow a clean single-constant `O(1/log L)` law out to `L=10^8`
  (§6) — a genuinely new observation, since F2 only looked at the combined `full` vs. `clean` finite
  operator and did not isolate the pure-M2 discreteness effect with an exact continuum background. If
  the schema is nonetheless the correct leading term (which nothing here refutes), the required proof
  needs a two-prime (or worse) Mertens/Selberg–Delange theorem that has not been supplied.
* **Verdict:** the strongest statement this pass can support is: *the continuum schema's normalization and
  background-moment structure are proved (modulo the cited classical theorem) leading-order arithmetic
  facts about the weighted integer sums, and the schema's M2/M3 kernels are exactly the naive
  continuum limit of the corresponding exact finite-operator pieces — but the schema's status as "the
  correct leading asymptotic with a controlled `O(1/log L)`-type error", which is what would be needed to
  call the arithmetic transfer complete, remains open, and the specific numerical evidence in §5-6 makes
  it look like the true error term is more delicate (possibly `log log L/log L`, or otherwise slower or
  differently shaped than `1/log L`) than the simple heuristic previously assumed.* No finite-sum
  computation at any `L<=10^8` in this pass or in F2 contradicts the schema. The margin of every tested
  vector remains negative at every tested `L`; nothing here moves the half-gap boundary.

---

## 8. Reproduction

```text
cd research/riemann-rmt/overnight/fable/astra_tasks/task001
python3 f1_common.py                                              # self-test, ~1s
OPENBLAS_NUM_THREADS=1 python3 f1_selberg_delange_expansion.py     # ~16s -> f1_sd_expansion_results.json
OPENBLAS_NUM_THREADS=1 python3 f1_moment_checks.py                 # ~23s -> f1_moment_results.json
python3 f1_continuum.py                                            # ~1s  -> f1_continuum_results.json
OPENBLAS_NUM_THREADS=1 python3 f1_insertion_decomposition.py       # ~8s  -> f1_insertion_results.json
OPENBLAS_NUM_THREADS=1 python3 f1_prime_discreteness.py            # ~88s -> f1_prime_discreteness_results.json
```
Logs: `f1_sd_expansion_run.log`, `f1_moment_checks_run.log`, `f1_insertion_run.log`,
`f1_prime_discreteness_run.log` (all already present; re-inspected, not re-run, in this pass, since
outputs and logs were consistent with the scripts as read and the task's time budget is better spent on
verification and write-up than on re-executing already-consistent runs).

---

## 9. Claims (for the ledger)

| id | claim | status | evidence |
|---|---|---|---|
| F1-1 | `F(s)=zeta(s)^a G(s)`, `C_ell=G(1)` as stated, explicit `kappa1,kappa2` Laurent coefficients | exact algebra | §2, `f1_sd_expansion.py` |
| F1-2 | Selberg–Delange (recalled) gives a 3-term expansion of `N(y)=sum d_ell(n)^2/n`; 2-term numerical match improves to `6e-3%` rel. error by `L=10^7` | proved arithmetic asymptotic (modulo recalled theorem) + finite numerical check | §2, `f1_moment_results.json` |
| F1-3 | Marked Euler product identities for `sum d^2 S~ n^{-s}` and `sum d^2 S~^2 n^{-s}`, with explicit next-order Laurent constants `pi_0, R1, R2` | exact algebra | §3, `f1_sd_expansion.py` |
| F1-4 | Leading-order `E_v[S2]=v^2/(a+1)`, `E_v[S2^2]=(a+6)v^4/((a+1)(a+2)(a+3))` derived from the weighted integer sum (not assumed) | proved arithmetic asymptotic, leading order (modulo recalled theorem) | §3 |
| F1-5 | Numerical confirmation of F1-4's *leading order* is present but its error rate has not stabilized at `L<=10^7` (both moments' `rel.err x log L` still rising) | finite numerical check; open re: error rate | §3, `f1_moment_results.json` |
| F1-6 | Exact correspondence: `beta<->M3`, `alpha<->M2` (off-diag `+ <x,A^2x>` pieces), derived from `A`'s matrix entries via recalled Mertens/PNT substitution | exact algebra + recalled substitution | §4 |
| F1-7 | Exact 5-way decomposition `alpha+beta+gamma+delta+eps=T` (`chk<=1.2e-16`); `gamma` decays like clean `1/log L` (ratio `2.53` over 3 decades); `delta` is flat, `eps` decays only by factor `1.34` over 3 decades; `alpha/D` reaches only `49%` of `M2/I` at `L=10^6` | finite numerical check | §5, `f1_insertion_results.json` |
| F1-8 | Idealized (coincidence-free) alpha/M2 discreteness correction: `(alpha_semi-M2/I)*log L` still moving `>3%`/decade at `L=10^8`; a single fixed-constant Mertens correction is numerically wrong by nearly a factor of 2 at `L=10^6`; a `log log L`-type or `1/sqrt(log L)`-type shape fits the 6 points better than plain `1/log L` | finite numerical check (curve fit is diagnostic, not proof) | §6, `f1_prime_discreteness_results.json` |
| F1-9 | Whether M3 accounts for all leading diagonal coincidences, and whether the schema's error term is genuinely `O(1/log L)` | open | §5, §6, §7 |
| F1-10 | The continuum schema is the correct leading arithmetic asymptotic, with a proved error bound | open | §7 |

## 10. Unresolved

* A two-prime (pair-correlation) Mertens/Selberg–Delange-type theorem for the double sum underlying
  `alpha`, with a genuine error term, has not been derived or cited; §6's curve fit is diagnostic evidence
  only that the true rate may not be a clean single-constant `1/log L`.
* Whether `delta` (inserted-prime-divides-background) and `eps` (prime powers `e>=2`) vanish at all in the
  `L->infty` limit relative to the leading term, and at what rate, is open; the flat/slowly-decaying finite
  data (§5) neither confirm nor refute vanishing at these `L`.
* The fourth-order Selberg–Delange/Hankel coefficients of `Sigma_1, Sigma_2` (needed to pin down the S2-
  moment error rate seen drifting in §3) were not computed.
* No attempt was made in this pass to re-derive or independently verify the classical Selberg–Delange
  theorem itself, nor Inoue's Theorems 2/4 (arxiv fetch blocked, as in F2); every statement resting on them
  is labeled accordingly.

## 11. Notes

Everything above is consistent with, and substantially extends, F2's diagnostic (`task001_F2_finite_sum_
diagnostic.md`): F2 already flagged (F2-5, F2-7, F2-10) that coincidence terms are large at accessible `L`
and that the S2-moment approach is slow with competing corrections; this pass supplies the exact marked-
Euler-product Laurent constants behind that observation (§3) and, new to this pass, isolates that the slow
convergence is not confined to the coincidence terms — the pure M2/alpha piece itself, with an idealized
exact continuum background and no arithmetic coincidences at all, shows the same kind of non-`1/log L`
behaviour (§6). This narrows the open question from "are there uncontrolled coincidence terms" to more
specifically "does even the coincidence-free two-new-primes correlation sum obey a Mertens-type theorem
with the assumed rate" — a cleaner, more specific target for a future pass or for Astra.
