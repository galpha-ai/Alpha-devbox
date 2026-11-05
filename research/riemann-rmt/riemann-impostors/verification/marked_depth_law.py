"""fab_chi_law.py — the correct law for the marked susceptibility.

Conjecture under test: chi is NOT driven by the size of the resolvent u^*(zI-G)^{-1}u,
but by the DIFFERENTIAL alignment of the mark with the two eigenvectors of the pair that
collides first.  Derivation: rank-one perturbation moves lambda_j by eta|<u,v_j>|^2;
Cayley sends lambda -> theta with dtheta/dlambda = -2/(1+lambda^2); locally -Lambda = delta^2/8
for the critical gap delta.  Hence

    chi = d(-Lambda)/d eta  ~  (delta/4) * ( c_a |<u,v_a>|^2 - c_b |<u,v_b>|^2 ),
    c_j = -2/(1+lambda_j^2),   (a,b) = the colliding pair.

So the mark must break the SYMMETRY of the critical pair; a mark aligned with any other
eigenvector -- however ill-conditioned the resolvent there -- barely moves the depth.
"""
import numpy as np, sys
sys.path.insert(0, ".")
from dyn1_core import find_ustar

def cayley_angles_vecs(G):
    w, V = np.linalg.eigh(G)
    return np.angle((w - 1j)/(w + 1j)), w, V

def coeffs_from_angles(th):
    p = np.array([1.0+0j])
    for t in th: p = np.convolve(p, np.array([1.0, -np.exp(1j*t)]))
    return p[::-1]

def depth_of_G(G):
    th,_,_ = cayley_angles_vecs(G)
    a = coeffs_from_angles(th); u,_,_ = find_ustar(a, len(th)); return u

def chi(G, u, h=1e-5):
    u = u/np.linalg.norm(u); P = np.outer(u,u).real
    return (depth_of_G(G+h*P) - depth_of_G(G-h*P))/(2*h)

def critical_pair(th):
    N=len(th); s=np.sort(th); order=np.argsort(th)
    gaps=np.diff(np.concatenate([s,[s[0]+2*np.pi]]))
    i=int(np.argmin(gaps))
    return order[i], order[(i+1)%N], gaps[i]

rng = np.random.default_rng(3)
N=6
lam=np.array([-1.7,-0.6,-0.15,0.4,1.1,2.3])
Q,_=np.linalg.qr(rng.normal(size=(N,N)))
G=Q@np.diag(lam)@Q.T
th,w,V = cayley_angles_vecs(G)
a,b,delta = critical_pair(th)
print(f"critical (closest) pair: eigen-indices {a},{b}; eigenvalues {w[a]:.4f},{w[b]:.4f}; gap delta={delta:.6f}")
print(f"depth tau={depth_of_G(G):.8f}   delta^2/8={delta**2/8:.8f}   ratio={depth_of_G(G)/(delta**2/8):.4f}\n")

ca, cb = -2/(1+w[a]**2), -2/(1+w[b]**2)
print(f"{'mark':>5} {'chi (measured)':>16} {'predicted':>14} {'ratio':>9} {'|<u,va>|^2':>11} {'|<u,vb>|^2':>11}")
meas, pred = [], []
for i in range(10):
    u = rng.normal(size=N); u/=np.linalg.norm(u)
    oa, ob = float((u@V[:,a])**2), float((u@V[:,b])**2)
    p = (delta/4)*(ca*oa - cb*ob)
    m = chi(G,u)
    meas.append(m); pred.append(p)
    print(f"{i:>5} {m:>16.6f} {p:>14.6f} {m/p if abs(p)>1e-9 else float('nan'):>9.4f} {oa:>11.5f} {ob:>11.5f}")
meas=np.array(meas); pred=np.array(pred)
print(f"\ncorrelation(measured, predicted) = {np.corrcoef(meas,pred)[0,1]:.8f}")
print(f"best-fit slope = {float(np.dot(meas,pred)/np.dot(pred,pred)):.6f}   (1.0 = exact law)")
# control: a mark orthogonal to BOTH critical eigenvectors should give chi ~ 0
u = rng.normal(size=N)
for vv in (V[:,a], V[:,b]): u = u - (u@vv)*vv
u/=np.linalg.norm(u)
print(f"\ncontrol: mark orthogonal to both critical eigenvectors -> chi = {chi(G,u):.3e} (predicted 0)")
