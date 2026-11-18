#!/usr/bin/env python3
"""
r1_h2_crosscheck.py -- Fable overnight, task D1.

Cross-checks between the new certificate (data/h2_k15856_interval_cert.json, produced by
r1_h2_interval_cert.py) and the historical record files:
  * research/riemann-rmt/p9_exact_cert_k15856.json      (historical arb certificate, committed)
  * data/h2_k15856_replay_arb.json                       (tonight's replay of the uncommitted arb script)
Compares the certified number, the per-node beta upper bounds (399 nodes) and the strategy split,
and prints the exact rational of the Chernoff-only (Berry-Esseen-free) certificate.
"""
import json
import sys
from fractions import Fraction as Fr

RR = "/home/user/Alpha-devbox/research/riemann-rmt"
new = json.load(open(f"{RR}/overnight/fable/data/h2_k15856_interval_cert.json"))
old = json.load(open(f"{RR}/p9_exact_cert_k15856.json"))
rep = json.load(open(f"{RR}/overnight/fable/data/h2_k15856_replay_arb.json"))

print("historical JSON certificate_lower_bound :", repr(old["certificate_lower_bound"]))
print("tonight's replay of the arb script       :", repr(rep["certificate_lower_bound"]))
for name, b in new["backends"].items():
    print(f"new [{name}]: lo={b['cert_lo_dec_down']} hi={b['cert_hi_dec_up']} PASS={b['PASS']}")
    lo = Fr(b["cert_lo_exact"])
    print("   exact rational numerator bits", lo.numerator.bit_length(), "denominator bits", lo.denominator.bit_length())
    print("   float(lo) =", repr(float(lo)), " float(lo) == historical:", float(lo) == old["certificate_lower_bound"])

# per-node comparison (arb backend)
arb = new["backends"]["python-flint arb (ball arithmetic)"]
chain_new, chain_old = arb["node_chain"], old["node_chain"]
assert len(chain_new) == len(chain_old) == 399
maxdiff, nbe_new, nbe_old, nsame = 0.0, 0, 0, 0
for a, b in zip(chain_new, chain_old):
    assert abs(a["u"] - b["u"]) < 1e-12
    maxdiff = max(maxdiff, abs(a["beta_ub"] - b["beta_ub"]))
    nbe_new += a["strategy"].startswith("BE")
    nbe_old += b["strategy"].startswith("BE")
    nsame += (a["strategy"].startswith("BE") == b["strategy"].startswith("BE"))
print(f"per-node beta_ub: max |new - old| = {maxdiff:.3e}; BE nodes new={nbe_new} old={nbe_old}; same class at {nsame}/399 nodes")
print("nodes with w=0 (beta_ub >= 1):", sum(1 for a in chain_new if a["w_lo"] == 0.0))
print("last node with positive weight: u =", max(a["u"] for a in chain_new if a["w_lo"] > 0))
print("Chernoff-only variant:", arb["variants"]["Chernoff_only_no_BE"])
print("erfc variant (arb only):", arb["variants"].get("C_BE=0.56_with_rigorous_erfc_Phibar"))
print("tuple:", {k: v for k, v in new["tuple"].items() if k not in ("file",)})
