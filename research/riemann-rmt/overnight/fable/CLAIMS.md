# Claims ledger (Fable overnight)

Format: `| id | claim | status | file | notes |`. Status in {P, C, R, O}. Refuter votes recorded.

| id | claim | status | file | notes |
|---|---|---|---|---|
| D1.2 | product-ansatz layer-cake bound M_k >= c2^-1 sum_j max(0,1-beta_j)(G(b_j)^2-G(a_j)^2) with chord-Chernoff / one-big-jump / Berry-Esseen tails is valid | P | r1_h2_interval_cert.md §2 | Lemmas 1-6 written out; any tail bound family works |
| D1.3 | M_15856 >= 8.013326752751306578613695503115 (exact rational; C_BE=0.56, elementary Phibar), outward-rounded (arb 200 bits) and cross-checked with mpmath.iv | C | r1_h2_interval_cert.md §3, data/h2_k15856_interval_cert.json | margin 0.01333; reproduces historical JSON bit-for-bit |
| D1.4 | M_15856 >= 8.00677408008999410774 with NO Berry-Esseen input (Markov + convexity only); M_923601 >= 12.00263034990571191492 likewise | C | r1_h2_interval_cert.md §3.2, §3.6 | H2/H3 records need only Maynard + Bombieri-Vinogradov |
| D1.6 | p9_tuple_k15856.npy: 15856 entries, diameter 173438, admissible for all 1847 primes <= 15856 (two implementations) | C | r1_h2_interval_cert.md §4 | prime count confirmed by sympy.primepi |
| D1.7 | committed p9_certify_hp.py is mpmath dps=50 + SAFE=1+1e-30, not outward rounding (Astra audit confirmed); JSON came from an uncommitted arb script, now copied with sha256 | R | r1_h2_interval_cert.md §1.5, scripts/r1_h2_reference_p9_exact_cert_scratchpad_copy.py | repaired by D1.3/D1.4 |
| D1.8 | Maynard/Polymath theorem statements and BE constants are recalled not re-read; arb library trusted; k=923601 tuple not re-verified tonight | O | r1_h2_interval_cert.md §5, §8 | |
