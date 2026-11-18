# Astra × Claude Code overnight research

User authorized joint autonomous work for eight hours starting **2026-09-05 05:56:56 UTC**, ending approximately **13:56:56 UTC**, and asked that results be pushed to **PR #11**. Do not ask the sleeping user questions.

This directory is the new audited research layer. Historical source files are preserved. No claim here supersedes a source theorem without a written argument or a reproducible counterexample.

## Work allocation

- Astra root: full historical recovery, long Chinese/English Markdown and PDF handoff, theorem/normalization audit, artifact generation, shared-branch integration.
- Yau-flow research agent: Horng-Tzer Yau DBM/reverse heat-flow literature, deterministic circular heat flow, dynamic collision localization and function-field transfer.
- Residual-Gram research agent: Inoue arXiv:2604.05733, independent functional computation, projection saturation, new arithmetic residual directions and density conversion.
- Prime186 research agent: published expanded-support sieve, complete certified margin, support-loss budget and smaller tuple paths.
- Claude Code/Fable: independent adversarial review and additional directions, especially whether the new spectral/Hilbert structures can exceed 0.6725007. Write separate files; challenge hypotheses rather than echoing the narrative.

## Findings already available for peer review

Run `python3 audit_research.py` here with numpy/scipy/sympy/mpmath. It performs 21 bounded numerical/symbolic checks and detects several historical errors; this is not a general theorem prover.

- Original `verify_codex.py`: **39 PASS, 4 FAIL, 1 SKIP**, despite exit status 0. The four failures are the Galerkin angle, its asymptotic coefficient, the charge-filter Fourier phase, and the Wilson periodic-box test. Independent corrected regressions pass.
- Correct Galerkin angle: `acos(1 - 1/(n*n*a_n))`.
- With negative Fourier exponent and `q_x=m_x+m_{x+1}-1`, the multiplier is `1+exp(+pi*i*k/N)`.
- COM modulation at closed balanced degree ≤ N: dimension 0 at N=4, 2 at N=5, 3 at N=6. The stated N≥4 family has a boundary exception.
- Old background endpoint bound fails at `g=.05`, `x=2*pi-.15`: actual difference quotient 133.500132, claimed upper 89.055743. Need the exact difference quotient or a bound over the entire segment and time window.
- Cayley `(lambda-i)/(lambda+i)=exp(i theta)` has `d theta/d lambda=+2/(1+lambda^2)`.
- Lean file has two actual `sorry` lines, but the larger issue is that `depth_ge` concludes only `delta^2/8 <= -log cos(delta/2)` and never mentions D. Its hD premise does not define a collision time.
- ACUE clock mass `2^(1-N)` makes unconditional expected depth infinite at each finite N. Finite means require conditioning/truncation.
- Strong LR2019 AH excludes zero gaps and implies asymptotic half-core. Modern/general AH allowing multiplicity or density-one exceptions is different. Do not blanket-identify all versions; do not infer density-AH rejection from a rare minimum gap.
- 186 has now been read at the original source, unlike the older Fable handoff. The old k49→240 objective is stale. Optimize full support-restored margin in the new sieve, not pure-simplex M_k.
- Historical H2/H3/H4 candidate certificates use high-precision mpmath plus a SAFE factor; the committed code alone does not demonstrate outward interval arithmetic. The H2 tuple's admissibility was independently fully checked, which is only one input of the proof chain.

## Integration protocol

Use separate reports and scripts. Root integrates and pushes normal fast-forward commits to the existing PR branch; never force push. Fetch and inspect before each push because Fable may contribute concurrently. Do not rewrite old papers silently. Include exact hypotheses, primary references, code/data paths, proof status, and failed attempts in each report.

No RH, GUE, AH refutation, sub-186 gap result, or improved 0.6725007 theorem has been established in this overnight run yet.
