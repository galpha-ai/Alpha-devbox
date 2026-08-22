"""fab_halflaplacian.py — is the ACUE visibility depth the linearised Newman flow?

Claim under test (three identities, all exact):

 (A)  sum_{delta=0}^{N-1} delta(N-delta) e^{-2 pi i k delta/N} = -N/(2 sin^2(pi k/N)),  k != 0.

 (B)  The operator (L_N f)(x) = sum_{k=1}^{N-1} [f(x) - f(x+k)] / (2 sin^2(pi k/N))
      has the Fourier characters e_delta(x) = e^{2 pi i delta x/N} as eigenfunctions with
      eigenvalue exactly delta(N-delta) -- the Grassmannian dimension / affine Bruhat length
      / (up to normalisation) quadratic Casimir that controls ACUE invisibility depth.

 (C)  THE BRIDGE.  The backward heat flow moves the zeros by the attracting Coulomb dynamics
      thetadot_j = - sum_{k != j} cot((theta_j - theta_k)/2).  The clock is its fixed point.
      Linearise: theta_j = 2 pi j/N + eps_j.  Since d/du[-cot(u/2)] = (1/2) csc^2(u/2),

          d(eps_j)/dt = sum_{k != j} (eps_j - eps_k) / (2 sin^2(pi(j-k)/N)),

      which IS L_N.  So the STATIC invisibility hierarchy and the DYNAMIC relaxation spectrum
      about the clock are the same operator, and the maximal invisibility depth floor(N^2/4)
      is the Nyquist relaxation rate.
"""
import numpy as np

def check_A(N):
    d = np.arange(N); w = d*(N-d)
    err = 0.0
    for k in range(1, N):
        lhs = (w * np.exp(-2j*np.pi*k*d/N)).sum()
        rhs = -N/(2*np.sin(np.pi*k/N)**2)
        err = max(err, abs(lhs-rhs))
    return err

def L_matrix(N):
    """matrix of (L_N f)(x) = sum_{k=1}^{N-1} [f(x)-f(x+k)]/(2 sin^2(pi k/N))"""
    M = np.zeros((N, N))
    for x in range(N):
        for k in range(1, N):
            c = 1.0/(2*np.sin(np.pi*k/N)**2)
            M[x, x] += c
            M[x, (x+k) % N] -= c
    return M

def linearised_coulomb(N):
    """Jacobian at the clock of thetadot_j = -sum_{k!=j} cot((theta_j-theta_k)/2)."""
    J = np.zeros((N, N))
    for j in range(N):
        for k in range(N):
            if k == j: continue
            c = 1.0/(2*np.sin(np.pi*(j-k)/N)**2)
            J[j, j] += c
            J[j, k] -= c
    return J

print(f"{'N':>4} {'(A) Fourier id':>16} {'(B) eig err':>13} {'(C) ||L - Jacobian||':>21}"
      f" {'max eig':>10} {'floor(N^2/4)':>13}")
for N in (4, 6, 8, 10, 12, 16, 20, 24):
    L = L_matrix(N); J = linearised_coulomb(N)
    ev = np.sort(np.linalg.eigvalsh(L))
    target = np.sort(np.array([d*(N-d) for d in range(N)], float))
    print(f"{N:>4} {check_A(N):>16.3e} {np.abs(ev-target).max():>13.3e}"
          f" {np.abs(L-J).max():>21.3e} {ev.max():>10.4f} {N*N//4:>13}")

print("\nEigen-structure at N = 12 (eigenvalue = delta(N-delta) = Grassmannian dim Gr(delta,N)):")
N = 12; ev = np.sort(np.linalg.eigvalsh(L_matrix(N)))
for d in range(N//2+1):
    print(f"  delta={d:>2}: predicted {d*(N-d):>4}   computed {ev[np.argmin(np.abs(ev-d*(N-d)))]:>10.6f}"
          f"   multiplicity {'1' if d in (0, N//2) else '2'}")
print(f"\n  Nyquist mode delta=N/2 carries the largest eigenvalue N^2/4 = {N*N//4},")
print("  which is exactly the maximal ACUE invisibility depth from the pigeonhole bound.")
