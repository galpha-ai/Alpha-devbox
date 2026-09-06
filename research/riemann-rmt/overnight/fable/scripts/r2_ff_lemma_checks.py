"""r2_ff_lemma_checks.py -- numerical checks of the lemmas in overnight/fable/r2_function_field.md.

(a) samplers: unitarity; U^T J U = J for the USp sampler; eigenvalue pairing; KS of the smallest
    free angle against Weyl-density rejection samples (USp(4), SO(4), SO(5), O^-(6)).
(b) transversality identity: at a double root z0 of a self-inversive P,
    d/ds P_s(z0)|_{s=0} = sum_j a_j j(M-j) z0^j  equals  -z0^2 P''(z0)  (Lemma T).
(c) forced roots: P_s(1) = 0 for all s for SO(odd), P_s(+-1) = 0 for O^-; palindromic symmetry
    preserved; mirror symmetry of the flowed root set.
(d) SO(odd) hard-edge law: for the 3-point configuration {1, e^{+-i theta}} the solver returns
    (1/2) log(3/(1+2cos theta)) exactly; with background (SO(2N+1), N = 4) 6D/theta^2 -> 1 as
    theta -> 0 whereas the naive two-body value would be 8D/theta^2 -> 1.
(e) genus 2: closed form (reduced quadratic) vs the general bisection solver on Haar USp(4).
(f) ODE solver vs bisection solver on Haar samples (M up to 33).
(g) continuity demo: D along a one-parameter rotation of a single eigenvalue through a
    simultaneous double collision (corner, but continuous) -- U(6) example.
(h) np.roots conditioning at M = 32..128 (unusable beyond ~40: the ODE solver is primary) and ODE timing.
(i) convergence of the ODE solver in the stopping gap eps.
Outputs a JSON summary to ../data/r2_ff_lemma_checks.json.
"""
import sys, os, json, time
import numpy as np
from math import pi, log, cos
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from r2_ff_depth_core import *
from scipy.stats import ks_2samp

rng = np.random.default_rng(20260905)
res = {}

print("(a) samplers")
J = symplectic_J(3)
U = haar_usp(6, rng)
res["usp_unitarity"] = float(np.max(np.abs(U.conj().T @ U - np.eye(6))))
res["usp_symplectic"] = float(np.max(np.abs(U.T @ J @ U - J)))
res["usp_commute_J"] = float(np.max(np.abs(U @ J - J @ U.conj())))
print(f"   USp(6): |U*U-I| = {res['usp_unitarity']:.2e}, |U^T J U - J| = {res['usp_symplectic']:.2e}, |UJ - J conj(U)| = {res['usp_commute_J']:.2e}")
for group, N in [("USp", 2), ("SO_even", 2), ("SO_odd", 2), ("O_minus", 2)]:
    n = 4000
    A = np.array([free_angles(sample_group(group, N, rng), group, N) for _ in range(n)])
    B = weyl_rejection_sample(group, N, n, rng)
    ks1 = ks_2samp(A[:, 0], B[:, 0]).pvalue
    ks2 = ks_2samp(A[:, 1], B[:, 1]).pvalue
    kss = ks_2samp(A.sum(axis=1), B.sum(axis=1)).pvalue
    res[f"weyl_ks_p_{group}"] = [float(ks1), float(ks2), float(kss)]
    print(f"   {group:8s} rank 2: KS p-values (theta_1, theta_2, theta_1+theta_2) vs Weyl density = {ks1:.3f}, {ks2:.3f}, {kss:.3f}")
# U(N): coefficient second moments E|a_j|^2 = 1 (recalled), spacing law vs sine-kernel Wigner surmise not needed
A = np.array([np.abs(poly_from_angles(free_angles(haar_unitary(6, rng), "U", 6), "U"))**2 for _ in range(4000)])
res["cue_coeff_second_moments"] = A.mean(axis=0).tolist()
print(f"   U(6): E|a_j|^2 = {np.round(A.mean(axis=0), 3)} (all should be 1)")

print("(b) transversality identity  d/ds P_s(z0) = -z0^2 P''(z0) at a double root z0")
worst = 0.0
for trial in range(200):
    M = int(rng.integers(3, 14))
    th = rng.uniform(0, 2 * pi, M - 1)
    th = np.concatenate([th, [th[0]]])           # double root at e^{i th[0]}
    a = poly_from_angles(th, "U")
    z0 = np.exp(1j * th[0])
    j = np.arange(M + 1)
    dsP = np.sum(a * j * (M - j) * z0 ** j)
    P2 = np.sum(a * j * (j - 1) * z0 ** (j - 2))
    err = abs(dsP + z0 ** 2 * P2) / max(1.0, abs(P2))
    worst = max(worst, err)
res["transversality_identity_worst_rel_err"] = float(worst)
print(f"   worst relative error over 200 random self-inversive P with a double root: {worst:.2e}")
# and the corollary: (z_a - z_b)^2 ~ 8 z0^2 (s - s0): check on the two-body problem numerically
g0 = 0.7; D2 = two_body_time(g0)
a = poly_from_angles(np.array([0.0, g0]), "U")
for h in (1e-6, 1e-8):
    r = roots_at(a, D2 + h)
    q = (r[0] - r[1]) ** 2 / (8 * np.exp(1j * g0) * h)   # z0 = e^{i g0/2}, z0^2 = e^{i g0}
    print(f"   two-body: (z_a-z_b)^2 / (8 z0^2 (s-D)) at s = D+{h:.0e}: {q:.6f}  (-> 1)")
res["radial_branching_ratio_1e-8"] = [float(q.real), float(q.imag)]

print("(c) forced roots and symmetry under the flow")
th = np.sort(rng.uniform(0.05, pi - 0.05, 5))
a_odd = poly_from_angles(th, "SO_odd"); a_om = poly_from_angles(th, "O_minus"); a_sp = poly_from_angles(th, "USp")
vals = []
for s in (0.0, 0.01, 0.1, 0.5):
    c = flowed_coeffs(a_odd, s); vals.append(abs(np.polyval(c[::-1], 1.0)) / np.abs(c).max())
    c = flowed_coeffs(a_om, s); vals.append(abs(np.polyval(c[::-1], 1.0)) / np.abs(c).max()); vals.append(abs(np.polyval(c[::-1], -1.0)) / np.abs(c).max())
    c = flowed_coeffs(a_sp, s); vals.append(np.max(np.abs(c - c[::-1])) / np.abs(c).max()); vals.append(np.max(np.abs(c.imag)))
res["forced_root_and_symmetry_worst"] = float(max(vals))
print(f"   worst |P_s(+-1)|/max|c| (forced) and palindromic/real defects: {max(vals):.2e}")
r = roots_at(a_sp, 0.3 * depth_from_angles(th, 'USp', classify=False)['D'])
mirror_defect = max(np.min(np.abs(np.conj(z) - r)) for z in r)
res["mirror_defect"] = float(mirror_defect)
print(f"   mirror symmetry of the flowed USp root set (max over roots of dist(conj z, root set)): {mirror_defect:.2e}")

print("(d) SO(odd) hard-edge three-body law")
rows = []
for theta in (1.0, 0.5, 0.2, 0.1, 0.05):
    d = depth_from_angles(np.array([theta]), "SO_odd", classify=False)["D"]
    ex = hard_edge_three_body(theta)
    rows.append((theta, d, ex, d / ex))
    print(f"   {{1, e^(+-i{theta})}}: solver D = {d:.12f}, (1/2)log(3/(1+2cos)) = {ex:.12f}, ratio = {d/ex:.10f}")
res["hard_edge_3body"] = rows
print("   with background, SO(9) (N=4): a mirror pair at +-theta near the forced root, three others at 1.2, 1.9, 2.6")
rows = []
for theta in (0.2, 0.1, 0.05, 0.025, 0.0125):
    fr = np.array([theta, 1.2, 1.9, 2.6])
    o = depth_from_angles(fr, "SO_odd")
    rows.append((theta, o["D"], 6 * o["D"] / theta ** 2, 8 * o["D"] / theta ** 2, o["ctype"]))
    print(f"   theta={theta:<7}: D={o['D']:.6e}  6D/theta^2={6*o['D']/theta**2:.5f} (->1 hard edge)   8D/theta^2={8*o['D']/theta**2:.5f} (bulk law would ->1)  type={o['ctype']}")
res["hard_edge_with_background"] = rows
print("   USp(8) (no forced root): mirror pair at +-theta -> gap 2 theta, two-body law: 8D/(2theta)^2 = 2D/theta^2 -> 1")
rows = []
for theta in (0.2, 0.1, 0.05, 0.025):
    fr = np.array([theta, 1.2, 1.9, 2.6])
    o = depth_from_angles(fr, "USp")
    rows.append((theta, o["D"], 2 * o["D"] / theta ** 2, o["ctype"]))
    print(f"   theta={theta:<7}: D={o['D']:.6e}  2D/theta^2={2*o['D']/theta**2:.5f}  type={o['ctype']}")
res["usp_edge_pair"] = rows

print("(e) genus 2: closed form vs general solver on 300 Haar USp(4) samples")
worst = 0.0; types_agree = 0; n = 300
for _ in range(n):
    fr = free_angles(haar_usp(4, rng), "USp", 2)
    Dc, tc = depth_usp4_closed_form(fr[0], fr[1])
    o = depth_from_angles(fr, "USp")
    worst = max(worst, abs(Dc - o["D"]) / Dc)
    types_agree += int(tc == o["ctype"])
res["genus2_closed_form_worst_rel_err"] = float(worst); res["genus2_type_agreement"] = types_agree / n
print(f"   worst relative difference {worst:.2e}; collision-type agreement {types_agree}/{n}")

print("(f) ODE cross-check vs bisection")
rows = []
for group, N in [("U", 8), ("U", 32), ("USp", 8), ("SO_even", 16), ("SO_odd", 16)]:
    for _ in range(3):
        fr = free_angles(sample_group(group, N, rng), group, N)
        o = depth_from_angles(fr, group, classify=False)
        t0 = time.time(); oo = depth_ode(fr, group); Do = oo["D"]; t1 = time.time()
        rows.append((group, N, o["D"], Do, abs(Do - o["D"]) / o["D"]))
        print(f"   {group:8s} N={N:3d}: bisection D={o['D']:.10e}  ODE D={Do:.10e}  rel diff={abs(Do-o['D'])/o['D']:.2e}  (ODE {t1-t0:.1f}s, {oo['nfev']} evals, type {oo['ctype']})")
res["ode_vs_bisection"] = rows

print("(g) continuity demo in U(6): rotate one eigenvalue through a reflection-symmetric double-collision configuration")
# reflection-symmetric {+-1.0, +-1.3, +-2.9}: the pairs (1.0,1.3) and (-1.3,-1.0) collide simultaneously by symmetry.
base = np.array([1.0, 1.3, 2.9, -2.9, -1.3, -1.0])
vals = []
for dphi in np.linspace(-0.02, 0.02, 41):
    fr = base.copy(); fr[1] = 1.3 + dphi
    vals.append(depth_from_angles(fr, "U", classify=False)["D"])
vals = np.array(vals)
jumps = np.max(np.abs(np.diff(vals)))
res["continuity_demo_max_jump"] = float(jumps); res["continuity_demo_D"] = vals.tolist()
print(f"   D(phi) on 41 points across the double collision: max |D(phi_{{k+1}})-D(phi_k)| = {jumps:.2e} (step 0.001);")
print(f"   D at the corner = {vals[20]:.8f}; one-sided slopes: left {np.diff(vals)[19]/0.001:.4f}, right {np.diff(vals)[20]/0.001:.4f}  (a corner = continuous, not differentiable)")

print("(h) np.roots conditioning (baseline off-circle error at s = 0) and ODE timing")
for group, N in [("U", 32), ("U", 64), ("USp", 32), ("USp", 64)]:
    b = []
    for _ in range(20):
        fr = free_angles(sample_group(group, N, rng), group, N)
        b.append(offcircle(poly_from_angles(fr, group), 0.0)[0])
    res[f"base_off_median_{group}_{N}"] = float(np.median(b))
    print(f"   {group:8s} N={N:3d} (M={matrix_size(group,N):3d}): median baseline off-circle error of np.roots = {np.median(b):.1e}  ({'usable' if np.median(b) < OFF_TOL else 'UNUSABLE -> ODE solver'})")
for group, N in [("U", 64), ("USp", 64), ("USp", 128)]:
    fr = free_angles(sample_group(group, N, rng), group, N)
    t0 = time.time(); o = depth_ode(fr, group); t1 = time.time()
    print(f"   ODE {group:8s} N={N:3d} (M={o['M']:3d}): {t1-t0:.2f} s, nfev={o['nfev']}, type={o['ctype']}, rho={o['rho']:.5f}")
    res[f"timing_ode_{group}_{N}"] = t1 - t0
print("(i) ODE remainder convergence: eps_rel = 2e-3, 5e-4, 1e-4 on 3 samples (U(32), SO_odd(16))")
for group, N in [("U", 32), ("SO_odd", 16)]:
    fr = free_angles(sample_group(group, N, rng), group, N)
    Ds = [depth_ode(fr, group, eps_rel=e)["D"] for e in (2e-3, 5e-4, 1e-4)]
    print(f"   {group:8s} N={N}: D = {Ds[0]:.12e}, {Ds[1]:.12e}, {Ds[2]:.12e}; rel spread {np.ptp(Ds)/Ds[2]:.1e}")
    res[f"ode_eps_convergence_{group}_{N}"] = float(np.ptp(Ds) / Ds[2])

with open(os.path.join(HERE, "..", "data", "r2_ff_lemma_checks.json"), "w") as f:
    json.dump(res, f, indent=1, default=float)
print("saved ../data/r2_ff_lemma_checks.json")
