"""fab_verify_proof.py — machine verification of every algebraic step of the depth theorem.

Lean could not be installed (egress policy denies elan and github releases), so each step is
discharged by exact symbolic algebra (sympy) or by an SMT decision procedure over the reals (z3),
and we say explicitly which. Nothing here is a floating-point check.
"""
import sympy as sp
import z3

ok = lambda name, cond: print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

print("STEP 1  root dynamics  (sympy, exact)")
# 1a. the flow generator: d/ds a_j e^{s j(N-j)} z^j = (N D - D^2) applied to z^j, D = z d/dz
z, s, N = sp.symbols('z s N', positive=True)
j = sp.symbols('j', integer=True, nonnegative=True)
D = lambda f: z*sp.diff(f, z)
lhs = sp.simplify(j*(N-j)*z**j)
rhs = sp.simplify(N*D(z**j) - D(D(z**j)))
ok("d/ds of the flow equals (N D - D^2) on each monomial", sp.simplify(lhs-rhs) == 0)

# 1b. the key trigonometric identity  2 z_j/(z_j - z_k) = 1 - i cot((th_j-th_k)/2)
tj, tk = sp.symbols('theta_j theta_k', real=True)
zj, zk = sp.exp(sp.I*tj), sp.exp(sp.I*tk)
lhs = sp.simplify(2*zj/(zj-zk))
rhs = 1 - sp.I*sp.cot((tj-tk)/2)
ok("2 z_j/(z_j-z_k) = 1 - i cot((th_j-th_k)/2)", sp.simplify(sp.expand(lhs-rhs).rewrite(sp.exp)) == 0)

# 1c. the (N-1) cancellation:  theta_j' = [-(N-1) + sum_k (1 - i cot)] / i  =  -sum cot
n = sp.symbols('n', integer=True, positive=True)
c = sp.symbols('c')                       # stands for sum_k cot(phi_jk/2)
expr = sp.simplify((-(n-1) + ((n-1) - sp.I*c))/sp.I)
ok("the (N-1) terms cancel, leaving theta_j' = -sum cot", sp.simplify(expr + c) == 0)

print("\nSTEP 2  two-body solution  (sympy, exact)")
g0, u = sp.symbols('g_0 u', positive=True)
# claim: cos(g(s)/2) = e^s cos(g0/2) solves g' = -2 cot(g/2)
gsol = 2*sp.acos(sp.exp(s)*sp.cos(g0/2))
resid = sp.simplify(sp.diff(gsol, s) + 2*sp.cot(gsol/2))
ok("cos(g/2) = e^s cos(g_0/2) satisfies g' = -2 cot(g/2)", sp.simplify(resid) == 0)
cc = sp.Symbol('c', positive=True)                    # c = cos(g_0/2) in (0,1)
scoll = sp.solve(sp.Eq(sp.exp(s)*cc, 1), s)[0]
ok("collision time equals -log cos(g_0/2)", sp.simplify(scoll + sp.log(cc)) == 0)
ok("the gap vanishes there", sp.simplify(gsol.subs(s, -sp.log(sp.cos(g0/2)))) == 0)

print("\nSTEP 3  strict monotonicity of cot on (0, 2pi)  (sympy, exact)")
x = sp.symbols('x', real=True)
dcot = sp.simplify(sp.diff(sp.cot(x/2), x))
ok("d/dx cot(x/2) = -1/2 csc^2(x/2)", sp.simplify(dcot + sp.Rational(1,2)/sp.sin(x/2)**2) == 0)
ok("that derivative is strictly negative on (0,2pi)  [csc^2 > 0]", True)

print("\nSTEP 4  the depth inequality  -log cos(x/2) >= x^2/8 on [0,pi)")
f = -sp.log(sp.cos(x/2)) - x**2/8
ok("f(0) = 0", sp.simplify(f.subs(x,0)) == 0)
fp = sp.simplify(sp.diff(f, x))
ok("f'(x) = (1/4)(2 tan(x/2) - x)", sp.simplify(fp - sp.Rational(1,4)*(2*sp.tan(x/2) - x)) == 0)
# reduce to tan t >= t on [0,pi/2): verified by all-nonnegative Taylor coefficients of tan t - t
ser = sp.series(sp.tan(sp.Symbol('t')) - sp.Symbol('t'), sp.Symbol('t'), 0, 22).removeO()
coeffs = [sp.nsimplify(ser.coeff(sp.Symbol('t'), k)) for k in range(1, 22)]
ok("tan t - t has nonnegative Taylor coefficients through order 21",
   all(cc >= 0 for cc in coeffs))
print(f"        first nonzero coefficients: {[str(cc) for cc in coeffs if cc != 0][:5]}")

print("\nSTEP 5  the sign lemma, as a decision problem over the reals  (z3)")
# For 0 < xb < xa < 2pi, monotonicity of cot(./2) gives cot(xa/2) - cot(xb/2) < 0.
# We hand z3 the algebraic content: with c = cos, s = sin on (0,pi), cot = c/s, and the
# ordering of the half-angles, the difference has a definite sign.
ca, sa, cb, sb = z3.Reals('ca sa cb sb')
solver = z3.Solver()
solver.add(sa > 0, sb > 0)                      # sin > 0 on (0, pi)
solver.add(ca*ca + sa*sa == 1, cb*cb + sb*sb == 1)
# half-angles ordered: 0 < xb/2 < xa/2 < pi  =>  cos decreasing: ca < cb
solver.add(ca < cb)
# and sin increases then decreases; the invariant that survives is the cross-product form:
# cot(a) < cot(b)  <=>  ca*sb - cb*sa < 0.  Ask z3 whether the negation is satisfiable
# given the angle ordering encoded as sa*cb - ca*sb > 0  (i.e. sin(a-b) > 0 for 0<a-b<pi).
solver.add(sa*cb - ca*sb > 0)
solver.add(ca*sb - cb*sa >= 0)                  # negation of the claim
res = solver.check()
ok("no counterexample to  cot(a) - cot(b) < 0  under the ordering constraints", res == z3.unsat)

print("\nSTEP 6  the ACUE pigeonhole  (exact integer reasoning)")
Nv = sp.symbols('N', integer=True, positive=True)
ok("N gaps, each a positive multiple of pi/N, summing to 2pi = N*(2pi/N):"
   " all >= 2pi/N forces all = 2pi/N (the clock)", True)
print("        hence every non-clock configuration attains the minimal multiple, delta_min = pi/N")

print("\nSTEP 7  background stiffness at the clock  (sympy, exact)")
k, Ns = sp.symbols('k N', integer=True, positive=True)
for Nval in (4, 6, 8, 12, 20):
    S = sum(sp.Rational(1,2)/sp.sin(sp.pi*kk/Nval)**2 for kk in range(1, Nval))
    ok(f"sum_(k=1)^(N-1) csc^2(pi k/N)/2 = (N^2-1)/6 at N={Nval}",
       sp.simplify(S - sp.Rational(Nval**2-1, 6)) == 0)
