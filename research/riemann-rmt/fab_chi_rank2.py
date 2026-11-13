"""fab_chi_rank2.py — the marked depth is a rank-2 critical-pair contrast, not a resolvent.

Refined mechanism (colleague's formulation):
   q_j(u) = |<u,v_j>|^2,  c_j = -2/(1+lambda_j^2),
   K_ab = c_a v_a v_a^* - c_b v_b v_b^*   (rank <= 2),   delta'(u) = u^* K_ab u,
   kappa(G) = 8 tau(G)/delta(G)^2   -- a FUNCTIONAL, not a constant -- so
   chi = (kappa*delta/4) delta'  +  (delta^2/8) kappa'(u).
Fitting chi = rho (delta/4) delta' therefore yields rho = kappa + (delta/2)(kappa'/delta'),
which should explain rho ~ 1.72 against kappa ~ 1.28 without any fudge factor.

Experiments: (2) kappa' decomposition, (1) blind rank-2 tomography, (3) null-cone.
"""
import numpy as np, sys
sys.path.insert(0, ".")
from dyn1_core import find_ustar

def angles_evecs(G):
    w, V = np.linalg.eigh(G)
    return np.angle((w-1j)/(w+1j)), w, V

def coeffs(th):
    p = np.array([1.0+0j])
    for t in th: p = np.convolve(p, np.array([1.0, -np.exp(1j*t)]))
    return p[::-1]

def tau_and_gap(G):
    th, w, V = angles_evecs(G)
    a = coeffs(th); u,_,_ = find_ustar(a, len(th))
    s = np.sort(th); order = np.argsort(th)
    g = np.diff(np.concatenate([s, [s[0]+2*np.pi]]))
    i = int(np.argmin(g))
    return u, g[i], order[i], order[(i+1) % len(th)]

def kappa(G):
    t, d, _, _ = tau_and_gap(G); return 8*t/d**2

def dir_deriv(f, G, u, h=1e-5):
    u = u/np.linalg.norm(u); P = np.outer(u, u).real
    return (f(G+h*P) - f(G-h*P))/(2*h)

rng = np.random.default_rng(3); N = 6
lam = np.array([-1.7,-0.6,-0.15,0.4,1.1,2.3])
Q,_ = np.linalg.qr(rng.normal(size=(N,N)))
G = Q@np.diag(lam)@Q.T
th, w, V = angles_evecs(G)
tau0, delta0, ia, ib = tau_and_gap(G)
k0 = 8*tau0/delta0**2
ca, cb = -2/(1+w[ia]**2), -2/(1+w[ib]**2)
print(f"critical pair: eigenvalues {w[ia]:.4f}, {w[ib]:.4f};  gap delta = {delta0:.6f}")
print(f"tau = {tau0:.8f};  kappa = 8 tau/delta^2 = {k0:.6f};  c_a = {ca:.5f}, c_b = {cb:.5f}\n")

print("=== (2) kappa' decomposition: parameter-free prediction vs measurement ===")
print("mark      chi meas   local term    kappa-term   total pred   old rho-fit")
meas, pred, loc = [], [], []
for i in range(10):
    u = rng.normal(size=N); u /= np.linalg.norm(u)
    qa, qb = float((u@V[:,ia])**2), float((u@V[:,ib])**2)
    dp = ca*qa - cb*qb                      # delta'(u) = u* K_ab u
    kp = dir_deriv(kappa, G, u)             # kappa'(u)
    L = k0*delta0/4*dp
    B = delta0**2/8*kp
    m = dir_deriv(lambda X: tau_and_gap(X)[0], G, u)
    old = 1.72*delta0/4*dp
    meas.append(m); pred.append(L+B); loc.append(L)
    print(f"{i:>4} {m:>12.6f} {L:>12.6f} {B:>13.6f} {L+B:>12.6f} {old:>12.6f}")
meas, pred, loc = map(np.array, (meas, pred, loc))
print(f"\n  correlation(meas, local only)      = {np.corrcoef(meas,loc)[0,1]:.8f}"
      f"   slope {float(meas@loc/(loc@loc)):.5f}")
print(f"  correlation(meas, local + kappa')  = {np.corrcoef(meas,pred)[0,1]:.8f}"
      f"   slope {float(meas@pred/(pred@pred)):.5f}   <-- parameter-free")
print(f"  residual norm: local only {np.linalg.norm(meas-loc):.3e},"
      f"  with kappa' {np.linalg.norm(meas-pred):.3e}")

print("\n=== (1) blind rank-2 tomography: recover K from chi(u) alone ===")
m_s = 60
U = rng.normal(size=(m_s, N)); U /= np.linalg.norm(U, axis=1, keepdims=True)
y = np.array([dir_deriv(lambda X: tau_and_gap(X)[0], G, U[k]) for k in range(m_s)])
idx = [(i,j) for i in range(N) for j in range(i, N)]
A = np.array([[ (U[k,i]*U[k,j]*(1 if i==j else 2)) for (i,j) in idx] for k in range(m_s)])
sol,*_ = np.linalg.lstsq(A, y, rcond=None)
K = np.zeros((N,N))
for v,(i,j) in zip(sol, idx): K[i,j] = v; K[j,i] = v
ev = np.sort(np.abs(np.linalg.eigvalsh(K)))[::-1]
print(f"  singular values of recovered K: {np.array2string(ev, precision=5)}")
print(f"  top-2 energy fraction = {(ev[:2]**2).sum()/(ev**2).sum():.6f}   (1.0 = exactly rank 2)")
w2, V2 = np.linalg.eigh(K)
top = V2[:, np.argsort(np.abs(w2))[::-1][:2]]
true = np.column_stack([V[:,ia], V[:,ib]])
sv = np.linalg.svd(top.T @ true, compute_uv=False)
print(f"  principal angles to span(v_a,v_b): {np.degrees(np.arccos(np.clip(sv,0,1)))} degrees")

print("\n=== (3) null cone: marks with c_a q_a = c_b q_b but q_a, q_b != 0 ===")
for t in range(3):
    z = rng.normal(size=N); z -= (z@V[:,ia])*V[:,ia]; z -= (z@V[:,ib])*V[:,ib]
    r = np.sqrt(abs(cb/ca))
    u = r*V[:,ia] + V[:,ib] + 0.3*z/np.linalg.norm(z); u /= np.linalg.norm(u)
    qa, qb = float((u@V[:,ia])**2), float((u@V[:,ib])**2)
    dp = ca*qa - cb*qb
    m = dir_deriv(lambda X: tau_and_gap(X)[0], G, u)
    print(f"  q_a={qa:.5f} q_b={qb:.5f}  delta'={dp:.3e} (nulled)   chi measured = {m:.3e}")
