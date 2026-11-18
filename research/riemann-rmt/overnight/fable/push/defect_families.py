"""Depth N^2 D for explicit local-defect families in the alternating clock, N up to ~120,
via bisection on the off-circle indicator (numpy roots). Families (gap patterns in units pi/N):
  disloc:  [3,1,2,...,2]                 single dislocation (s* = 1.419640342 known)
  block4:  [1,1,2,...,2,4,2,...,2]       3-block, compensating 4-gap diametrically opposite (N odd or even)
  block33: [1,1,2,..,2,3,3,2,..,2]       3-block, compensation split 3,3 opposite (N even)
  block3adj: [3,1,1,2,...,2]             3-block with compensating 3-gap adjacent... (removed neighbour)
  quad:    [1,1,1,2,...,2,5,2,...]       4-block with 5-gap opposite
"""
import numpy as np, sys

def depth_from_gaps(gaps):
    N=len(gaps); M=2*N; assert sum(gaps)==M
    sites=np.concatenate([[0],np.cumsum(gaps)[:-1]])
    theta=2*np.pi*sites/M
    z=np.exp(1j*theta); a=np.poly(z)
    powers=np.arange(N,-1,-1); w=powers*(N-powers)
    def off(s):
        r=np.roots(a*np.exp(s*w)); return np.max(np.abs(np.abs(r)-1))
    lo,hi=0.0,2.5/N**2
    while off(hi)<1e-7: hi*=1.5
    for _ in range(70):
        mid=0.5*(lo+hi)
        if off(mid)>1e-7: hi=mid
        else: lo=mid
        if hi-lo<1e-14*hi: break
    return 0.5*(lo+hi)

def fam(name,N):
    if name=='disloc': g=[3,1]+[2]*(N-2)
    elif name=='block4':
        k=(N-3)//2; g=[1,1]+[2]*k+[4]+[2]*(N-3-k)
    elif name=='block33':
        assert N%2==0; k=(N-4)//2; g=[1,1]+[2]*k+[3,3]+[2]*(N-4-k)
    elif name=='block3adj': g=[3,1,1]+[2]*(N-3)
    elif name=='quad':
        k=(N-4)//2; g=[1,1,1]+[2]*k+[5]+[2]*(N-4-k)
    else: raise ValueError
    assert sum(g)==2*N and len(g)==N, (name,N,sum(g),len(g))
    return g

names=sys.argv[1:] or ['disloc','block4','block33','block3adj','quad']
for name in names:
    print("==",name)
    for N in [6,8,10,12,16,20,24,32,40,48,64,80,100,120]:
        if name=='block33' and N%2: continue
        try:
            g=fam(name,N); D=depth_from_gaps(g); print(f"N={N:4d}  N^2 D = {N*N*D:.10f}", flush=True)
        except AssertionError as e: pass
