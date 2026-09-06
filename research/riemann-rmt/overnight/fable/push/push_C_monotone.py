"""Monotonicity tests (Task C step 2): does adding roots to a configuration (same background) slow or
speed the first collision?  Clock N=64 (odd sites of Z/128) plus added roots at even sites A, with the
compensating hole placed diametrically opposite (remove |A| clock sites around site 64+...)."""
import numpy as np
from push_C_fast import depth_ode
N=64; M=2*N
def config(added):
    clock=set(range(1,M,2)); A=set(added); n=len(A)
    # remove n clock sites centred opposite (near site 64), symmetric
    rem=[]; c=M//2+1  # odd site 65
    order=[c]+[x for j in range(1,N) for x in (c-2*j,c+2*j)]
    for x in order:
        x%=M
        if x in clock and x not in rem and len(rem)<n: rem.append(x)
    S=sorted((clock-set(rem))|A); assert len(S)==N, (len(S),N)
    th=2*np.pi*np.array(S)/M; d,i=depth_ode(th); return N*N*d, S[i], S[(i+1)%N]
tests={'3-block {0}':[0],'5-block {0,2}':[0,2],'7-block {0,2,4}':[0,2,4],'9-block {0,2,4,6}':[0,2,4,6],
       'two 3-blocks {0,4}':[0,4],'{0,6}':[0,6],'{0,8}':[0,8],'{0,12}':[0,12],'{0,20}':[0,20],
       '{0,2,6}':[0,2,6],'{0,2,8}':[0,2,8],'{0,4,8}':[0,4,8],'{0,2,4,8}':[0,2,4,8],'{0,2,6,8}':[0,2,6,8]}
for k,v in tests.items():
    val,a,b=config(v); print(f"{k:22s}: N^2 D = {val:.6f}   colliding pair sites ({a},{b})")
