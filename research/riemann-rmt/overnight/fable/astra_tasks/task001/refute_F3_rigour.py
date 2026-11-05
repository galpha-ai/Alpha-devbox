#!/usr/bin/env python3
"""Refuter script for F3: check the sign/ordering of the K = (1/2)Phi^2 -/+ (1/2)[A,A^T]
identity, comparing the report's claimed sign to the actual task/F2 literal formula
K_L = A^T A + (A^2+(A^T)^2)/2, using the exact same discretized bosonic-Fock construction
as f3_fock_spectrum.py (copied inline, small M for a fast, exact check)."""
import math
import numpy as np

def enumerate_partitions(M):
    keys = []
    def rec(max_part, remaining, current):
        if max_part == 0:
            keys.append(tuple(current)); return
        max_mult = remaining // max_part
        for mult in range(max_mult, -1, -1):
            if mult > 0: current.append((max_part, mult))
            rec(max_part - 1, remaining - mult * max_part, current)
            if mult > 0: current.pop()
    rec(M, M, [])
    masses = [sum(part*mult for part, mult in k) for k in keys]
    return keys, masses

def build(M):
    keys, masses = enumerate_partitions(M)
    N = len(keys)
    index = {k: i for i, k in enumerate(keys)}
    dicts = [dict(k) for k in keys]
    g = lambda j: 2.0*math.sin(math.pi*(j/M)/2.0)/math.sqrt(j)
    Acre = np.zeros((N, N))
    for i in range(N):
        d = dicts[i]; m = masses[i]; budget = M - m
        if budget <= 0: continue
        for j in range(1, budget+1):
            old = d.get(j, 0)
            d[j] = old+1
            newkey = tuple(sorted(d.items(), reverse=True))
            if old == 0: del d[j]
            else: d[j] = old
            newidx = index[newkey]
            Acre[newidx, i] = g(j)*math.sqrt(old+1)
    return Acre

M = 6
A = build(M)          # "Acre" = creation, FABLE/task convention
AT = A.T               # "Aann" = annihilation
N = A.shape[0]
Phi = A + AT

# Literal task/F2/f3-code formula:
K_L = AT @ A + 0.5*(A @ A + AT @ AT)

# Two candidate abstract identities:
comm_A_AT = A @ AT - AT @ A     # [A, A^T]  (FABLE order, A=creation first)
cand_minus = 0.5*(Phi @ Phi) - 0.5*comm_A_AT
cand_plus  = 0.5*(Phi @ Phi) + 0.5*comm_A_AT

err_minus = np.abs(K_L - cand_minus).max()
err_plus  = np.abs(K_L - cand_plus).max()
print(f"M={M}, dim={N}")
print("max|K_L - [(1/2)Phi^2 - (1/2)[A,A^T]]| =", err_minus)
print("max|K_L - [(1/2)Phi^2 + (1/2)[A,A^T]]| =", err_plus)

# Now the report's own claimed identity, in ITS physics convention (A_phys=annihilate=AT,
# A*_phys=create=A), literally: K_report := A*A_phys-order + (A^2+A*^2)/2 with "A*A" meaning
# apply-A-first-then-A* (standard operator-product convention), i.e. Acre @ Aann = A @ AT:
K_report_physics = (A @ AT) + 0.5*(A @ A + AT @ AT)
err_report_vs_task = np.abs(K_L - K_report_physics).max()
print("max|K_L - K_report(physics A*A=A@AT convention)| =", err_report_vs_task)

# report's claimed formula for K_report: (1/2)Phi^2 - (1/2)[A,A*]_physics, where
# [A,A*]_physics = AT@A - A@AT (physics commutator convention, A=annihilate=AT literally first)
comm_physics = AT @ A - A @ AT
cand_report_formula = 0.5*(Phi@Phi) - 0.5*comm_physics
err_selfcheck = np.abs(K_report_physics - cand_report_formula).max()
print("self-check: max|K_report_physics - [(1/2)Phi^2-(1/2)[A,A*]_physics]| =", err_selfcheck,
      "(should be ~0: report's OWN identity is internally correct for K_report)")

# c(v)-type diagonal check: is the commutator [A,A^T] actually diagonal in mass (as claimed,
# a function only of v)? Check on mass eigenspaces.
masses = np.array([sum(p*mlt for p, mlt in k) for k in enumerate_partitions(M)[0]])
print()
print("Is comm_A_AT diagonal-in-mass? off-block max abs entry:",
      np.abs(comm_A_AT[np.subtract.outer(masses, masses) != 0]).max() if N>1 else 0.0)
for v in sorted(set(masses.tolist())):
    idx = np.where(masses == v)[0]
    block = comm_A_AT[np.ix_(idx, idx)]
    # should be scalar*Identity on this block if report's c(v) picture is right
    diag = np.diag(block)
    offdiag_max = np.abs(block - np.diag(diag)).max() if len(idx) > 1 else 0.0
    diag_spread = diag.max() - diag.min() if len(diag) > 0 else 0.0
    print(f"  v={v}: block dim={len(idx)}, diag spread={diag_spread:.3e}, offdiag max={offdiag_max:.3e}, "
          f"mean diag = {diag.mean():.6f}")

print()
print("=== Larger M check (M=12) to confirm the non-scalar-c(v) effect is not a tiny-M artifact ===")
M2 = 12
A2 = build(M2); AT2 = A2.T
comm2 = A2 @ AT2 - AT2 @ A2
keys2, masses2 = enumerate_partitions(M2)
masses2 = np.array(masses2)
for v in [4, 6, 8, 10]:
    idx = np.where(masses2 == v)[0]
    if len(idx) < 2: continue
    diag = np.diag(comm2[np.ix_(idx, idx)])
    print(f"  M={M2}, v={v}: n_states={len(idx)}, diag min={diag.min():.4f} max={diag.max():.4f} "
          f"spread/mean={(diag.max()-diag.min())/abs(diag.mean()):.3f}")
