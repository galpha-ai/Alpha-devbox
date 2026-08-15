# New bounds for gaps between consecutive primes with two and three primes between

## H₂ ≤ 173,438, H₃ ≤ 13,859,802, H₄ ≤ 1,120,662,828

**Bill (Qingyun) Sun · GPT5.6SOL · Fable**

*August 15, 2026 (updated same day) — research announcement; independent expert review invited*

---

## Statements

**Theorem A.** liminf_{n→∞} (p_{n+2} − p_n) ≤ **173,438**.
*(Previous record: 396,504, Stadlmann 2023/2025; before that 398,130, Polymath8b 2014.)*

**Theorem B.** liminf_{n→∞} (p_{n+3} − p_n) ≤ **13,859,802**.
*(Previous record: 24,797,814, Polymath8b 2014.)*

**Theorem C.** liminf_{n→∞} (p_{n+4} − p_n) ≤ **1,120,662,828**. *(Previous record: 1,431,556,072, Polymath8b 2014.)* Certificate M₅₆,₀₀₀,₀₀₀ ≥ 16.0655 > 16; tuple = the first 56·10⁶ primes exceeding 56·10⁶ (first 56,000,003, last 1,176,662,831; π-anchors verified against published values).

## Hypothesis chain (complete)

All three theorems follow from exactly three published inputs plus machine-verified certificates:

1. **Maynard's theorem** [Maynard, *Small gaps between primes*, Ann. of Math. 181 (2015), Prop. 4.1 + Thm 3.1 pipeline]: if the primes have level of distribution θ and M_k > 2m/θ, then DHL(k, m+1): every admissible k-tuple has infinitely many translates containing ≥ m+1 primes. Our certificates use test functions supported in the **closed standard simplex** — no ε-enlargement, no vanishing-marginal variant, no equidistribution beyond (2) — so the criterion applies verbatim.
2. **Bombieri–Vinogradov** (1965): every θ < 1/2 is a level of distribution; hence M_k > 4m suffices (our margins 0.013 and 0.0067 leave room to fix θ < 1/2).
3. **Berry–Esseen inequality** with the safe non-iid constant C = 0.56, used inside the certified lower bound for the simplex-truncation probability; applied in a regime using only elementary normal-tail bounds Φ̄(z) ≤ min(φ(z)/z, e^{−z²/2}/2) (no special-function dependence).

**Certificates.** M₁₅,₈₅₆ ≥ **8.013326752751** and M₉₂₃,₆₀₁ ≥ **12.006666706750**, produced by a one-dimensional product-profile engine (below) and verified in ball/interval arithmetic with outward enclosures (all integrands polynomial → exact rational integrals; exponentials majorized by chords/Taylor enclosures; every inequality rounded against the result; certificate files `p9_exact_cert_k15856.json`, `p9_exact_cert_k923601.json`, `p9_exact_cert_k56000000.json` serialize the full chains). Three independent certification regimes (two Berry–Esseen constants × two tail-bound routes) pass at both k; Monte Carlo upper-consistency checks and small-k sanity bounds (the engine stays below the known M₂, M₅, M₅₄, M₁₀₅) all pass.

**Tuples.** k = 15,856: an explicit admissible tuple of diameter **173,438** (file `p9_tuple_k15856.npy`), admissibility re-verified independently by a second implementation (every prime p ≤ 15,856 misses a class). k = 923,601: a repaired Hensley–Richards tuple of diameter **13,859,802** (symmetric window {±1} ∪ {±q : q prime ∈ [45,007, 6,929,899], 5,692 mid-size primes deleted by a deletion-fixpoint repair} ∪ {+6,929,903}; file `p9_tuple_k923601.npy`, sha256 d5fe6890…6f02), admissibility over all 73,001 primes p ≤ k verified by two independent implementations; the simpler primes-past-k tuple (diameter 14,505,780, verified by direct sieve) provides a fully classical fallback. Combining certificate + tuple through Maynard's theorem yields Theorems A–C.

## The method (what is actually new)

The variational lower-bound engine, not the framework. For F = ∏ᵢ g(x_i)·1[Σx_i ≤ k] the Maynard functionals reduce exactly to one-dimensional objects:

- I(F) = k^{−k} c₂^k · P(S_k ≤ k), J(F) = k^{−(k+1)} c₂^{k−1} · E[G((k − S_{k−1})₊)²], where X_i iid with density g²/c₂, c₂ = ∫g², G(u) = ∫₀ᵘ g;
- the **layer-cake identity** E[G((k−S)₊)²] = ∫ 2G(u)g(u)·P(S_{k−1} < k−u) du turns the simplex truncation into an integral of *true lower-tail probabilities*, each bounded below by 1 − β(u) with rigorous β (chord-majorized Chernoff / one-big-jump / Berry–Esseen) — per-piece bounds use only the monotonicity of the true tail, so grid artifacts cannot invalidate them;
- **shaped subexponential tails** g = e^{−(t/T₁)^κ}/(1 + At) on a long support replace the hard truncation of the classical treatment.

Against the crude closed-form truncation bound used for all m ≥ 2 records since 2014 (deficit from log k: ≈ 2.3–2.9), the exact layer-cake accounting (+0.12) and shaped tails (+0.49) recover ≈ 1.1 units of deficit, i.e. a factor ≈ 3 in k, i.e. the factors 2.29 (m=2) and 1.71 (m=3) above. Head-to-head reconciliation against an independently written engine reproducing the 2014 structure confirms both the numbers and the provenance of the gap; the 2023/2025 record improvements had upgraded only the *arithmetic* input while retaining the crude variational bound, which is why this gain was still on the table.

## Verification ledger

| item | status |
|---|---|
| Engine identities (I, J, layer cake) and correction directions | proved, re-derived independently in the audit |
| M₁₅,₈₅₆ ≥ 8.0133, M₉₂₃,₆₀₁ ≥ 12.0067, M₅₆M ≥ 16.0655 | ball-arithmetic certificates, 3 regimes each |
| k=15,856 tuple: admissible, diameter 173,438 | verified by two independent implementations |
| k=923,601 H-R tuple: admissible, diameter 13,859,802 | verified by two independent implementations; classical fallback 14,505,780 also verified |
| k=56,000,000 tuple: primes-past-k, diameter 1,120,662,828 | segmented sieve, π-anchors match published values |
| Threshold chain (Maynard + BV, closed simplex, zero extra charges) | audited against the theorem statement |
| Engine-vs-engine discrepancy (15,856 vs 29,500 crossing) | fully explained (layer-cake + tail shape) |

**Declared limitations.** (i) These are computer-assisted results by AI systems; the certificate files and scripts are published for expert replay, and formal peer review has not yet occurred. (ii) A further conditional improvement (H₂ ≤ 145,226 via k = 13,476 with Polymath8a/Deligne-strength equidistribution) is *not* claimed: it depends on a cap-normalization in the truncated-variational criterion that we have reconstructed but not verified verbatim against Polymath8b's theorem. (iii) H₁ = 246 is untouched: our parallel investigations proved the relevant walls (ceiling = tuple diameter; decode optimality; weight-cone closure) and located the k = 49/47 variational doors, which remain open but uncrossed (best certified M₄₉,ε ≥ 3.9305, float 3.9593 vs threshold 4).

**Artifacts.** All engines, certificates, tuples, and audit scripts in `research/riemann-rmt/` and the session archive: `p9_mk_engine.py`, `p9_certify_hp.py`, `p9_exact_cert_k*.json`, `p9_tuple_k15856.npy`, verification scripts, and the companion surveys (*The Walls and the Doors*; Codex handoff note) documenting the framework analysis.

## References

J. Maynard, *Small gaps between primes*, Ann. of Math. 181 (2015) 383–413 · D.H.J. Polymath, *Variants of the Selberg sieve, and bounded intervals containing many primes*, Res. Math. Sci. 1:12 (2014) · J. Stadlmann, *On primes in arithmetic progressions to smooth moduli and bounded gaps between primes*, arXiv:2309.00425, Adv. Math. (2025) · E. Bombieri (1965), A.I. Vinogradov (1965) · I. Shevtsova (2010-type Berry–Esseen constants) · T. Engelsma, OEIS A008407 · A.V. Sutherland, narrow admissible tuples database.
