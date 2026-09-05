"""Finite arithmetic Rayleigh search for the exact diagonal main term.
These finite L eigenvalues are exploratory, not uniform asymptotics or certificates.
At phi=1/2 define B=-iA; then the main-term operator is A*A+Re(A^2).
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import LinearOperator,eigsh

def prime_powers(L):
    mask=np.ones(L+1,dtype=bool);mask[:2]=False
    for p in range(2,int(np.sqrt(L))+1):
        if mask[p]:mask[p*p::p]=False
    for p in np.flatnonzero(mask):
        q=int(p);e=1
        while q<=L:
            yield q,e
            if q>L//int(p):break
            q*=int(p);e+=1

def make_A(L,phi=.5,theta=1):
    rows=[];cols=[];values=[]
    for q,e in prime_powers(L):
        m=np.arange(1,L//q+1)
        rows.append(q*m-1);cols.append(m-1)
        w=2*np.sin(np.pi*phi*theta*np.log(q)/np.log(L))/(e*np.sqrt(q))
        values.append(np.full(len(m),w))
    return csr_matrix((np.concatenate(values),(np.concatenate(rows),np.concatenate(cols))),shape=(L,L))

def solve(L,theta=1):
    t=time.time();A=make_A(L,theta=theta);At=A.T
    def mv(x):
        ax=A@x;atx=At@x
        return At@ax+.5*(A@ax+At@atx)
    K=LinearOperator((L,L),matvec=mv,dtype=np.float64)
    # Positive PF vector; no stochastic initialization.
    val,vec=eigsh(K,k=1,which='LA',v0=np.ones(L),tol=1e-10,maxiter=2000)
    x=vec[:,0];x*=np.sign(x[0]);ev=val[0]
    res=np.linalg.norm(mv(x)-ev*x)
    return {'L':L,'theta':theta,'eigenvalue':float(ev),'margin':float(ev/(2*np.pi**2)-.25),'residual_l2':float(res),'nnz':A.nnz,'seconds':time.time()-t},x

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--lengths',default='1000,3000,10000,30000,100000,300000,1000000');p.add_argument('--theta',type=float,default=1);a=p.parse_args()
    results=[]
    for L in map(int,a.lengths.split(',')):
        r,x=solve(L,a.theta);results.append(r);print(json.dumps(r),flush=True)
        if L==max(map(int,a.lengths.split(','))):np.savez_compressed(Path(__file__).with_name('arithmetic-eigenvector.npz'),L=L,theta=a.theta,x=x)
    Path(__file__).with_name('arithmetic-results.json').write_text(json.dumps(results,indent=2))
