"""Does the det-tilt impostor family change LOCAL pattern probabilities as N grows?
coupling(k, w-pattern) = E_ACUE[e^{2 pi i k X/N} 1_pattern] / P(pattern), k=2..N-2, patterns = occupancy of sites 0..w-1.
Also: ACUE fraction of gaps equal to 1 (dimers) vs the discrete-sine value 1/2 - 2/pi^2."""
import itertools, numpy as np, sys
for N in [int(a) for a in sys.argv[1:]] or [8, 10, 12]:
    M = 2*N
    S = np.array(list(itertools.combinations(range(M), N)), dtype=np.int16)
    zeta = np.exp(1j*np.pi/N)
    tab = np.abs(zeta**np.arange(M)[:,None] - zeta**np.arange(M)[None,:])**2
    w = np.ones(len(S))
    for i in range(N):
        for j in range(i+1, N):
            w *= tab[S[:,i], S[:,j]]
    w /= w.sum()
    X = S.sum(axis=1) % N
    occ = np.zeros((len(S), M), dtype=bool)
    occ[np.arange(len(S))[:,None], S] = True
    # dimer fraction
    adj = sum(occ[:, x] & occ[:, (x+1) % M] for x in range(M))
    print(f"N={N}: E[#gaps=1]/N = {(w*adj).sum()/N:.6f}   (discrete-sine limit 1/2-2/pi^2 = {0.5-2/np.pi**2:.6f});  X uniform? max|P(X=x)-1/N| = {max(abs((w*(X==x)).sum()-1/N) for x in range(N)):.2e}")
    for width in (3, 4):
        worst = 0.0; arg = None
        for pat in itertools.product([0,1], repeat=width):
            ind = np.all(occ[:, :width] == np.array(pat, bool), axis=1)
            pp = (w*ind).sum()
            if pp < 1e-12: continue
            for k in range(2, N-1):
                c = (w*ind*np.exp(2j*np.pi*k*X/N)).sum()/pp
                if abs(c) > worst: worst, arg = abs(c), (k, pat)
        print(f"   width {width}: max_k,pattern |E[e^(2 pi i k X/N) | pattern]| = {worst:.4e}  at k,pattern={arg}")
