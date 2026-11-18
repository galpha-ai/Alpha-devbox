"""Complete enumeration of ACUE rotation orbits for N-subsets of Z/2N, with the finite
de Bruijn-Newman depth D of each orbit (first collision time of the backward heat flow
P_s(z)=sum a_j e^{s j(N-j)} z^j), computed by bisection on the 'all roots on the unit
circle' indicator (self-inversive polynomial: roots leave the circle exactly at a collision).
Also records the ACUE mass |Delta|^2/(2N)^N, gap pattern, Nyquist row |p_N|^2 = (n_even-n_odd)^2,
and Q(0)=sum csc^2, D_force(0)=Q-C_N.
Usage: python acue_depth_enum.py N [outfile.npz]
"""
import sys, itertools, numpy as np, time
from math import comb

def canonical_orbit(C, M):
    # rotation orbit representative (lexicographically smallest tuple over rotations)
    best=None
    for r in range(M):
        t=tuple(sorted(((c+r)%M) for c in C))
        if best is None or t<best: best=t
    return best

def depth_bisect(theta, s_hi=None, tol=1e-13):
    N=len(theta)
    z=np.exp(1j*theta)
    a=np.poly(z)            # coefficients highest degree first: z^N + ... 
    # np.poly returns [1, c1, ..., cN] for z^N + c1 z^{N-1}+...; index i <-> power N-i
    powers=np.arange(N,-1,-1)
    w=powers*(N-powers)     # j(N-j) for power j
    def offcircle(s):
        coef=a*np.exp(s*w)
        r=np.roots(coef)
        return np.max(np.abs(np.abs(r)-1.0))
    # bracket
    lo=0.0
    if s_hi is None:
        s_hi=4.0/N**2
        while offcircle(s_hi)<1e-7: s_hi*=2
        # scan for monotonicity sanity: check a coarse grid below s_hi
    hi=s_hi
    for _ in range(60):
        mid=0.5*(lo+hi)
        if offcircle(mid)>1e-7: hi=mid
        else: lo=mid
        if hi-lo<tol*max(1,hi): break
    return 0.5*(lo+hi)

def main():
    N=int(sys.argv[1]); M=2*N
    out=sys.argv[2] if len(sys.argv)>2 else f"acue_depth_N{N}.npz"
    seen=set(); reps=[]
    for C in itertools.combinations(range(M),N):
        key=canonical_orbit(C,M)
        if key in seen: continue
        seen.add(key); reps.append(key)
    print(f"N={N}: {len(reps)} orbits of {comb(M,N)} configurations", flush=True)
    t0=time.time()
    D=np.zeros(len(reps)); mass=np.zeros(len(reps)); pN2=np.zeros(len(reps)); Q0=np.zeros(len(reps))
    gaps=np.zeros((len(reps),N),dtype=np.int16); orbit_size=np.zeros(len(reps),dtype=np.int32)
    CN=N*(N*N-1)/3
    for i,C in enumerate(reps):
        Cs=np.array(sorted(C))
        theta=2*np.pi*Cs/M
        g=np.diff(np.concatenate([Cs,[Cs[0]+M]]))
        gaps[i]=g
        z=np.exp(1j*theta)
        vd=np.prod([abs(z[j]-z[k])**2 for j in range(N) for k in range(j+1,N)]) if N>1 else 1.0
        mass[i]=vd/M**N
        # orbit size = M / stabiliser
        rots=set(tuple(sorted(((c+r)%M) for c in C)) for r in range(M))
        orbit_size[i]=len(rots)
        pN2[i]=(np.sum((-1)**Cs))**2
        dth=theta[:,None]-theta[None,:]
        iu=np.triu_indices(N,1)
        Q0[i]=2*np.sum(1/np.sin(dth[iu]/2)**2)
        if np.all(g==2):   # clock
            D[i]=np.inf
        else:
            D[i]=depth_bisect(theta)
        if i%2000==0: print(i, time.time()-t0, flush=True)
    tot=np.sum(mass*orbit_size)
    print("total ACUE mass over orbits:", tot)
    np.savez(out, N=N, D=D, mass=mass, pN2=pN2, Q0=Q0, gaps=gaps, orbit_size=orbit_size, CN=CN)
    fin=np.isfinite(D)
    w=mass*orbit_size
    ND=N*N*D[fin]
    print(f"non-clock orbits {fin.sum()}; N^2D min {ND.min():.8f} max {ND.max():.8f} median {np.median(ND):.8f}")
    print(f"ACUE-weighted E[N^2 D | nonclock] = {np.sum(w[fin]*ND)/np.sum(w[fin]):.8f}; clock mass {np.sum(w[~fin]):.6g} (2^(1-N)={2.0**(1-N):.6g})")
    im=np.argmax(ND); jm=np.argmin(ND)
    idx=np.where(fin)[0]
    print("argmax gaps:", gaps[idx[im]].tolist(), " argmin gaps:", gaps[idx[jm]].tolist())
    print("time", time.time()-t0)
main()
