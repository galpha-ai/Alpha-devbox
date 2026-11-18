import sys, json, time
sys.path.insert(0, "/tmp/claude-0/-home-user-Alpha-devbox/00b3b5f7-f917-5641-a9be-c6a8f38f5cd7/scratchpad")
from fractions import Fraction as F
from sgn1_model import build_model, primes_upto
from sgn1_lp import simplex, verify_certificate, assemble_val_beta

BIG = [p for p in primes_upto(37) if p > 7]
M = build_model((0, 2, 6), [2, 3, 5, 7], BIG, m=1, L=1)
res = {}

def exact_at(beta, tag):
    t0 = time.time()
    A, b, c, dec = assemble_val_beta(M, beta)
    st, x, obj, y = simplex(A, b, c)
    out = dict(beta=str(beta), status=st)
    if st == "optimal":
        verify_certificate(A, b, c, x, y)
        w, (S, D) = dec(x)
        out.update(val=str(-obj), val_f=float(-obj), Phi=str(S), Phi_f=float(S),
                   D=str(D), D_f=float(D),
                   nneg=sum(1 for v in w if v < 0), certified=True)
    print(tag, out.get("val_f"), out["status"], f"{time.time()-t0:.1f}s")
    res[tag] = out
    return out

# positive class, exact
t0 = time.time()
A, b, c, dec = assemble_val_beta(M, F(0), pos_only=True)
st, x, obj, y = simplex(A, b, c)
verify_certificate(A, b, c, x, y)
res["val_pos"] = dict(status=st, val=str(-obj), val_f=float(-obj), certified=True)
print("val_pos exact:", -obj, float(-obj), f"{time.time()-t0:.1f}s")

o1 = exact_at(F(207, 100), "signed_2.07")     # inside window
o2 = exact_at(F(43, 20), "plateau_2.15")      # plateau
o3 = exact_at(F(2), "beta_2")                 # expect unbounded
# exact breakpoint from the two certified lines: val_pos = Phi1 - beta* D1
if o1["status"] == "optimal":
    Phi1, D1 = F(o1["Phi"]), F(o1["D"])
    vpos = F(res["val_pos"]["val"])
    bstar = (Phi1 - vpos) / D1
    res["beta_star"] = dict(exact=str(bstar), float=float(bstar))
    print("beta* exact =", bstar, float(bstar))
    # verify: just left/right of beta*
    eps = F(1, 1000)
    oL = exact_at(bstar - eps, "left_of_bstar")
    oR = exact_at(bstar + eps, "right_of_bstar")
    print("left val vs plateau:", oL["val_f"], ">", float(vpos), oL["val_f"] > float(vpos))
    print("right val == plateau:", oR["val"] == res["val_pos"]["val"])
json.dump(res, open("sgn1_t1_exact.json", "w"), indent=1)
print("saved sgn1_t1_exact.json")
