# Residual Gram arithmetic route: exact saturation, independent reproduction, and symmetric prime-factor trials

Research round 1, 5 September 2026. This note separates exact algebra, certified finite variational integrals, exploratory numerics, and missing arithmetic theorems. No half-gap theorem or famous conjecture was proved in this round.

## 1. Outcome and priority

The supplied Inoue calculation is independently reproducible. Its negative margin at normalized gap `phi=1/2` is not a numerical accident caused by a low polynomial degree. The reproduced degree-14 margin is `-0.015357981703850554`, corresponding to additional normalized log-increment energy `0.3031544076323465`. This is a measured deficit for a particular family, not a universal impossibility theorem.

Three additional conclusions were obtained.

1. The original product-cutoff approximator is exactly saturated in its coefficient Hilbert space. Rewriting the same support with asymmetric factor lengths or additional Gram directions cannot give positive main-term recovery.
2. A new sparse arithmetic operator computes the diagonal main term for **arbitrary resonator coefficients**, not just the divisor-function ansatz. Full eigenvalue searches through one million coefficients remain below the half-gap threshold. These finite searches do not settle the asymptotic extremal problem.
3. A genuine extension of the resonator family, using symmetric statistics of its prime factors, improves the numerical half-gap margin to about `-0.01465473`. This removes only about 4.6% of the original deficit. A simple rational instance of this extension has a rigorously enclosed continuum margin between `-0.01467` and `-0.01465`. Its arithmetic transfer has not been fully written, and its margin is negative.

The significant unresolved node remains a quantitative estimate for residual directions carrying information beyond the already accessible product cutoff, or a substantially different arithmetic resonator that survives the full operator test.

## 2. Source audit and an important historical correction

The primary source is [Shota Inoue, arXiv:2604.05733v1](https://arxiv.org/html/2604.05733v1). It introduces a weighted second factorial moment of short-interval zero counts and proves, under RH, `mu<0.50895`. Its Theorem 4 allows arbitrary arithmetic coefficients under a product cutoff `L<=T/(log T)^2`; Theorem 2 specializes the coefficients to a divisor-function family. Zeros are counted with multiplicity. The displayed numerical trial is `phi=.508949`, `ell=1.15`, `f(v)=1-.7v`.

The old claim `mu<=.50412`, cited in the 2019 Lagarias–Rodgers paper, is **not a valid current record**. [Goldston–Turnage-Butterbaugh, arXiv:1904.06001v2](https://arxiv.org/abs/1904.06001) was withdrawn on 11 November 2019: its generalized weights had to be symmetric in all their variables, invalidating the claimed calculation. This is directly relevant to the search below: every new prime-factor feature is explicitly symmetric.

The user's original `inoue_resonance_probe.py` and JSON became available after this round's independent implementation had already been run. Comparing those exact originals with the new code gives agreement within `1e-12` for the published trial and within `1e-11` for the degree-14 margin. The independently found finite-dimensional sign crossing differs by less than `2e-11`.

## 3. Exact coefficient-space saturation theorem

Fix a cutoff `L`, a resonator coefficient sequence `r`, and a log-increment coefficient sequence `g`. For any approximator coefficients `a`, put

\[
b_a(q)=\sum_{km=q}a(k)r(m),\qquad
b_g(q)=\sum_{km=q}g(k)r(m),\qquad q\le L.
\]

Equip coefficient vectors with

\[
\langle b,c\rangle_L=\sum_{q\le L}\frac{\overline{b(q)}c(q)}q.
\]

Then the approximator-dependent diagonal main term satisfies the exact identity

\[
2\operatorname{Re}\langle b_a,b_g\rangle_L-\|b_a\|_L^2
=\|b_g\|_L^2-\|b_a-b_g\|_L^2.
\tag{S1}
\]

Consequently `a=g` is a global maximizer of this main term for the fixed `r,L`. The maximizer need not be unique in `a` if the convolution map has a kernel, but its image `b_a=b_g` is unique.

This is an identity in a finite coefficient Hilbert space. It should not be described as exact orthogonal projection in the time-domain Gaussian Hilbert space at finite `T`: that Gram matrix has small non-diagonal entries. The arithmetic theorem gives the passage from the latter to the diagonal main term and an error estimate.

Suppose a new direction `C` has coefficients supported on the **same** product set `q<=L`. The main-term inner product of `C` with the discarded residual is zero. Its recovery term therefore equals `-||C||_L^2`, which is nonpositive. A change of basis, a more complicated inverse Gram, a nonlinear parameterization of `a`, or repeated completion of squares does not change this fact.

There is also the exact time-domain identity

\[
\begin{aligned}
&2\operatorname{Re}\langle B_0,X\rangle-\|B_0\|^2
+2\operatorname{Re}\langle C,X-B_0\rangle-\|C\|^2\\
&\hspace{2cm}=2\operatorname{Re}\langle B_0+C,X\rangle-\|B_0+C\|^2.
\end{aligned}
\tag{S2}
\]

Thus “residual recovery” has not by itself enlarged the theorem: it is a larger approximator. Its value lies in designing a larger approximator whose mixed terms remain accessible.

### The asymmetric-length caveat

Theorem 4 already permits setting `r(n)=0` for `n>L0` while retaining product cutoff `L>L0`. Therefore changing the relative factor lengths strictly inside the old product region is already contained in the original general theorem. It may improve a restricted trial family, but it is not a new arithmetic input. The useful analogy with the prime-gap 186 proof starts only when the **actual accessible mixed products** exceed what this theorem already controls.

## 4. Robust inverse-Gram certificate and the missing quantities

For candidate residual directions `C_1,...,C_m`, define

\[
G_{ij}=\langle C_i,C_j\rangle,
\qquad b_i=\langle C_i,X-B_0\rangle.
\]

The recovery for a fixed coefficient vector `c` is

\[
\Delta(c)=2\operatorname{Re}(c^*b)-c^*Gc.
\tag{G1}
\]

If estimates `bhat,Ghat` have bounds

\[
|b_i-\widehat b_i|\le\epsilon_i,
\qquad |G_{ij}-\widehat G_{ij}|\le E_{ij},
\]

then the elementary certified lower bound is

\[
\Delta(c)\ge 2\operatorname{Re}(c^*\widehat b)-c^*\widehat Gc
-2\sum_i|c_i|\epsilon_i
-\sum_{i,j}|c_i||c_j|E_{ij}.
\tag{G2}
\]

An explicit rational `c` and entrywise enclosures suffice. Matrix inversion and a numerical condition number are not part of the final certificate. Singular Gram matrices cause no difficulty for (G2).

For the reproduced one-variable baseline, the additional gain must exceed approximately `0.3031544077` after division by the resonator norm. A design goal `0.31` allows only a modest error budget; it is not a universal lower bound on the energy needed by other methods.

Rank, trace, and Hilbert–Schmidt norm are insufficient to determine this recovery. For example the same rational matrix `diag(1,4)` gives optimal recovery `1` for `b=(1,0)` and `1/4` for `b=(0,1)`. This is the precise location where directional information matters.

### What a genuinely longer direction requires

For Gaussian packet width `W=T/log T`, the transformed weight is significant when

\[
|\log(km/q)|\lesssim W^{-1}.
\]

At a product scale `M=T^(1+eta)`, this retains additive differences of size roughly `M/W`, rather than only the exact equation `km=q`. The mixed moment contains prime-power coefficients `g(k)`, resonator coefficients `r(m)`, coefficients of `C(q)`, and a nontrivial oscillatory phase determined by the packet center. No estimate for generic arithmetic progressions automatically supplies this shifted multiplicative correlation. A proposed well-factorable or Type-II argument must state the actual variables, modulus, frequency range, coefficient norms, and total error after summing every direction.

## 5. A rigorous obstruction to a naive sparse long-support strategy

The following statement is elementary but useful for support design.

**Sparse-tail lemma.** Let `eta>0`, `M=T^(1+eta)`, and `W=T/log T`. Let a set `S` in `[M,2M]` have pairwise logarithmic spacing at least `c/W`, for some fixed `c>0`. Suppose coefficients satisfy `|b(q)|<=C_epsilon q^epsilon` for every fixed positive epsilon. Then

\[
\sum_{q\in S}\frac{|b(q)|^2}{q}=o(1).
\tag{ST}
\]

Indeed, the logarithmic interval has length `log 2`, so `|S|<=1+W log(2)/c`. The displayed sum is at most a constant times `W M^(-1+2epsilon)`. Choosing `2epsilon(1+eta)<eta` proves the claim. The same conclusion holds relative to a normalizing resonator norm that is bounded below by `T^(-o(1))`.

This applies to the usual fixed divisor-polynomial resonator coefficients. It rules out obtaining fixed recovery simply by selecting a very sparse, trivially separated portion of a genuinely long dyadic tail and then using its diagonal coefficient energy. It does **not** rule out dense structured supports, substantial off-diagonal mixed information, or different coefficient classes with quantitatively stronger concentration.

## 6. Independent reproduction of the original variational calculation

The new implementation uses a different simplex parameterization from the supplied original: the background mass `v` is the outside Gauss–Jacobi variable, and inserted masses occupy its complementary simplex. The basis

\[
\psi_j(v)=\sqrt{2j+\ell^2}\,P_j^{(0,\ell^2-1)}(2v-1)
\]

is orthonormal for `v^(ell^2-1)dv`. Its norm matrix is the identity. This avoids unstable monomial inversion in the original one-variable calculation.

| Trial | ell | Half-gap margin |
|---|---:|---:|
| Degree 2 | 1.1720511457 | -0.01539943397962 |
| Degree 6 | 1.1762949914 | -0.01535798218167 |
| Degree 14 | 1.1762950386 | -0.01535798170385 |

The published linear trial gives `1.487161813351623e-5` at quadrature order 48. Orders 20, 32, and 48 agree to approximately `2e-15`. The degree-8 numerical zero is `0.5088369010687765`.

None of these floating calculations bounds all continuous functions or all `ell>=1`. Raising the polynomial degree is not an independent arithmetic theorem. The exact saturation theorem in §3 concerns a different variable, namely the approximator with the resonator fixed; it does not imply that the resonator family is globally optimal.

## 7. An exact arithmetic operator for arbitrary resonator coefficients

At `phi=1/2`, the leading linear term vanishes. Put `x_n=r(n)/sqrt(n)`. Define a real sparse creation operator `A` by

\[
A_{qm,m}=\frac{2\sin(\tfrac h2\log q)}{e\sqrt q}
\quad\text{when }q=p^e,\quad qm\le L,
\]

and zero otherwise. Here `h=pi/log T`; the exploratory runs set `log L/log T=1`, the limiting boundary of the admissible range. Since `g(q)=-2i sin((h/2)log q)/e`, the complex convolution operator is `B=-iA`.

The approximator term is `||Bx||^2`, and the holomorphic correction is `Re<x,B^2x>`. Therefore the exact diagonal main-term matrix is

\[
K_L=A^*A+\frac{A^2+(A^*)^2}{2}.
\tag{A1}
\]

Its maximal normalized half-gap margin is

\[
\frac{\lambda_{\max}(K_L)}{2\pi^2}-\frac14.
\tag{A2}
\]

All coefficients of `K_L` are nonnegative at this parameter, so a real nonnegative Perron vector suffices for the extremal Rayleigh quotient. This is a substantially larger search space than the one-variable divisor family.

| L | largest eigenvalue of K | margin | eigenvector residual norm |
|---:|---:|---:|---:|
| 1,000 | 3.9492871367 | -0.0499267764 | 3.0e-11 |
| 10,000 | 4.1058670454 | -0.0419943455 | 4.6e-15 |
| 100,000 | 4.2052553801 | -0.0369592737 | 2.0e-13 |
| 1,000,000 | 4.2738969159 | -0.0334818529 | 3.1e-12 |

The threshold needed at the boundary is `pi^2/2`, approximately `4.9348022`. The full matrix at `L=10^6` has 3,626,619 nonzero entries in `A`. Its sparse operator implementation avoids materializing `K`.

These are finite experiments. The choice `log L/log T=1` is an asymptotic model, not an admissible finite theorem with `L=T`. An eigenvector for one finite `L` cannot be frozen and used as `T` tends to infinity. No extrapolated limit is claimed, and no global no-go follows from these negative eigenvalues.

A useful next question is whether

\[
K_L=\tfrac12(A+A^*)^2+\tfrac12[A^*,A]
\]

admits a positive comparison or a Hardy-type bound uniformly in `L`. A proof that the normalized limiting norm is at most `1/4` would close the entire diagonal method, rather than merely one family of weights. Such a proof has not been obtained.

## 8. A genuinely broader family: symmetric prime-factor statistics

The finite arithmetic eigenvector search motivates coefficients of the form

\[
r(n)=d_\ell(n)H\big(v,S_2(n),S_3(n),\ldots\big),
\quad v=\frac{\log n}{\log L},
\quad S_k(n)=\sum_{p\mid n}\left(\frac{\log p}{\log L}\right)^k.
\tag{PF1}
\]

A Liouville sign can be included when the sign of the linear term calls for it. At the half-gap boundary the quadratic terms do not distinguish that sign. Every `S_k` and every polynomial in these variables is symmetric in the prime factors. These features do not repeat the unsymmetric-weight error in the withdrawn 2019 calculation.

For the continuum experiment, use a background mass `v` and its scaled Poisson–Dirichlet prime-factor partition with parameter `a=ell^2`. Its relevant moments are

\[
\mathbb E S_k=\frac{\Gamma(k)\Gamma(a+1)}{\Gamma(a+k)}v^k,
\]

and

\[
\mathbb E S_kS_l=
\frac{\Gamma(a)[a\Gamma(k+l)+a^2\Gamma(k)\Gamma(l)]}{\Gamma(a+k+l)}v^{k+l}.
\tag{PF2}
\]

More generally, for a list `k_1,...,k_s`,

\[
\mathbb E\prod_{j=1}^sS_{k_j}
=\frac{\Gamma(a)}{\Gamma(a+\sum_j k_j)}v^{\sum_jk_j}
\sum_{\pi}a^{|\pi|}\prod_{B\in\pi}\Gamma\!\left(\sum_{j\in B}k_j\right),
\tag{PF3}
\]

where the sum runs over set partitions of the labeled factors. Adding a prime of logarithmic size `u` replaces `(v,S_k)` by `(v+u,S_k+u^k)`. This gives explicit Gram and quadratic-form integrals for each symmetric feature polynomial.

The calculation reduces exactly to the independently reproduced Inoue form when `H` depends only on `v`; this reduction was checked at three different values of `ell` and by two independently written feature implementations.

| Symmetric features, each with a small mass polynomial | optimized ell | numerical margin at phi=1/2 |
|---|---:|---:|
| 1 only, degree 6 | 1.176295 | -0.0153579822 |
| 1, S2, degree 4 | 1.065285 | -0.0146618161 |
| 1, S2, S3, degree 4 | 1.077117 | -0.0146563150 |
| 1, S2, S3, S4, degree 4 | 1.081082 | -0.0146551195 |
| 12 groups including S2 squared, S2 S3, S2 cubed, S2 fourth power | 1.079948 | -0.0146547256 |

The richer Gram matrices become ill-conditioned. Directions below an explicit eigenvalue cutoff were discarded. Therefore the last decimals and any inference of saturation in this expanded family are exploratory only. The main robust conclusion is that these particular natural extra arithmetic features recover a small fraction of the deficit, far less than required to cross `1/2`.

### Arithmetic status of this extension

The displayed partition moments define a coherent continuum calculation. To turn it into a zeta theorem one must prove the corresponding asymptotics for weighted integer sums, including repeated-prime terms, coincidences between inserted primes and the background integer, the short-background range, and the errors after normalizing by the resonator norm. The original theorem handles arbitrary `r`, but it does not automatically supply this new explicit asymptotic evaluation. No such transfer is claimed as completed here.

## 9. An exact rational certificate for one expanded continuum trial

To avoid trusting the ill-conditioned optimizers, a simple trial was rounded to rational coefficients. Take `ell=16/15` and

\[
H(v,S_2)=f(v)+g(v)S_2,
\]

with

\[
f(v)=\frac{145+3v-116v^2+71v^3-6v^4}{100},
\]

\[
g(v)=\frac{-563+1682v-2479v^2+1751v^3-488v^4}{100}.
\]

The script `rational_trial_certificate.py` proves, by rational arithmetic, that its continuum half-gap margin lies in

\[
-\frac{1467}{100000}<\mathcal J< -\frac{1465}{100000}.
\tag{RC}
\]

A much tighter outward enclosure is stored in the JSON certificate; its decimal presentation is approximately

`[-0.014662375473368995, -0.014662375473368974]`.

The method is completely explicit:

* Machin's formula and alternating arctangent series give rational lower and upper bounds for pi.
* Sine and cosine are replaced by finite Taylor polynomials with explicit remainder bounds on the simplex.
* The symmetric feature expectations are rational because `ell^2=256/225` and all moment degrees are integers.
* Every simplex monomial integral is a factorial divided by a finite product of rational numbers.
* The numerator and positive denominator are enclosed before division. Final assertions compare exact rational numbers.

During development, an off-by-one error in a simplex beta denominator was caught by disagreement with the independent floating integral, then corrected. Explicit constant-monomial identities are now asserted in the certificate script. The final run succeeds. This history is preserved to make clear why multiple forms of verification matter.

The certificate proves a statement about **one explicit continuum trial**, not a global upper bound and not an arithmetic half-gap improvement. In particular a negative trial is not a proof that the entire method fails.

## 10. AH, multiplicity, and positive-density targets

There are several different statements called the Alternative Hypothesis.

[The 2019 Lagarias–Rodgers formulation](https://arxiv.org/abs/1905.12123), Conjecture 2.2, explicitly takes the limiting consecutive-gap values in `{1/2,1,3/2,...}`, excluding zero, for all sufficiently large indices. A theorem `liminf g_n<1/2` would refute this strong formulation. It is incorrect to say that this particular source allows zero gaps.

[Baluyot–Goldston–Suriajaya–Turnage-Butterbaugh 2025](https://arxiv.org/abs/2508.10857) studies a formulation that does not assume simplicity. For that broader setting, repeated zeros or gaps tending to zero require separate treatment. A small-gap theorem counting multiplicity may detect only those zeros. A statement allowing a density-zero exceptional set is also not contradicted merely by infinitely many exceptional gaps.

A robust target is a positive density of pair separations in a fixed interval whose closure avoids every permitted half-integer, together with whichever local-count control is needed to translate pair information into adjacent-gap information. A positive proportion of weighted factorial moment is not automatically an unweighted positive proportion: the resonator could concentrate on a negligible set of heights.

For an unweighted count there is a useful exact detector. Write

\[
Q(h)=\int N_h(t)(N_h(t)-1)\,dt
=2\sum_{i<j}(h-|\gamma_i-\gamma_j|)_+
\]

when boundary terms are absent or handled explicitly. For `0<h0<h1<h2` in arithmetic progression,

\[
Q(h_2)-2Q(h_1)+Q(h_0)
\]

has a nonnegative triangular pair kernel supported in `[h0,h2]`, with value zero at separation zero. Thus it removes the direct multiplicity atom exactly. A smooth nonconstant arithmetic weight changes the kernel and must be analyzed rather than silently canceled. Also a close nonadjacent pair need not give an adjacent gap bounded away from zero without local cluster control. This detector is a possible way to formulate a stronger arithmetic target; its positivity has not been proved from the available zeta estimates.

## 11. Artifacts and reproducibility

All files are in `research-round1/residual-gram/`, separate from the recovered original source tree.

* `inoue_variational.py`, `variational-results.json`: independent one-variable reproduction.
* `arithmetic_operator.py`, `arithmetic-results.json`, `arithmetic-eigenvector.npz`: arbitrary-coefficient sparse arithmetic search through `L=10^6`.
* `prime_feature_variational.py`, `prime-feature-results.json`: linear symmetric prime-factor features.
* `general_prime_features.py`, `general-prime-feature-results.json`: products of symmetric prime moments.
* `rational_trial_certificate.py`, `rational-trial-certificate.json`: exact rational continuum-integral certificate.
* `check_algebra.py`, `algebra-check-results.json`: structural completion-of-squares identities, operator sign check, reduction of both feature implementations to the original form, and comparison against the now recovered original result file.
* `inoue-paper.html`: retrieved primary-paper snapshot for formula checking.
* `*-run.log`: execution records.

Commands used:

```text
OPENBLAS_NUM_THREADS=1 python3 research-round1/residual-gram/inoue_variational.py
OPENBLAS_NUM_THREADS=1 python3 research-round1/residual-gram/arithmetic_operator.py
OPENBLAS_NUM_THREADS=1 python3 research-round1/residual-gram/prime_feature_variational.py
OPENBLAS_NUM_THREADS=1 python3 research-round1/residual-gram/general_prime_features.py
python3 research-round1/residual-gram/rational_trial_certificate.py
OPENBLAS_NUM_THREADS=1 python3 research-round1/residual-gram/check_algebra.py
```

The algebra test suite is not a proof assistant. The rational certificate's stated finite integral inequality is exact rational computation with explicit analytic remainder estimates. The spectral searches and their optimizer outputs remain numerical.

## 12. Recommended next bounded attack

First investigate a uniform upper or a counterexample for the full arithmetic operator (A1), including its commutator structure and the shape of finite Perron vectors. This is the quickest way to tell whether more elaborate resonators inside the old product region can matter at all. A uniform upper would justify making genuine long-support mixed moments the primary target; a counterexample would identify a more concrete family to analyze.

In parallel with that mathematical question, specify one dense residual coefficient family and compute its exact near-diagonal product conditions. The theorem request must be an explicit sum with an explicit normalization and error target. It should not merely say “apply Guth–Maynard,” “use a Yau flow,” or “recover the residual Gram.” The measured margin supplies a useful numerical target, but the required new arithmetic input remains the central unresolved issue.
