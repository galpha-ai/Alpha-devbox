"""Experimental continuum Ritz forms for symmetric products of prime moments.
All conclusions are numerical. Arithmetic transfer remains a proof obligation.
"""
from __future__ import annotations
import json,math,time
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import numpy as np
from scipy.special import roots_jacobi,gammaln
from scipy.linalg import eigh
from scipy.optimize import minimize_scalar

@lru_cache(None)
def partitions(xs):
    if not xs:return ((),)
    a,*rest=xs;out=[]
    for blocks in partitions(tuple(rest)):
        out.append(((a,),)+blocks)
        for i in range(len(blocks)):
            out.append(blocks[:i]+((a,)+blocks[i],)+blocks[i+1:])
    return tuple(out)

@lru_cache(None)
def pdmom(a,ks):
    if not ks:return 1.
    s=0.
    for blocks in partitions(tuple(ks)):
        s+=a**len(blocks)*math.prod(math.gamma(sum(b)) for b in blocks)
    return s*math.exp(gammaln(a)-gammaln(a+sum(ks)))

def expand(ks,insertions,n):
    out={}
    for mask in range(1<<len(ks)):
        remain=[];coef=np.ones(n)
        for j,k in enumerate(ks):
            if (mask>>j)&1:coef*=sum(x**k for x in insertions)
            else:remain.append(k)
        key=tuple(sorted(remain));out[key]=out.get(key,0)+coef
    return out

def forms(ell,degree,groups,phi=.5,order=24):
    a=ell**2;D=degree+1;features=[(i,g) for g in groups for i in range(D)]
    G=np.array([[pdmom(a,tuple(sorted(g+h)))/(a+i+j+sum(g)+sum(h)) for j,h in features] for i,g in features])
    x,w=roots_jacobi(order,0,a-1);v=(x+1)/2;vw=w/2**a
    x,w=roots_jacobi(order,0,0);z=(x+1)/2;zw=w/2
    def cross(v,left,right,wt):
        v=v.ravel();left=[x.ravel() for x in left];right=[x.ravel() for x in right];wt=wt.ravel();n=len(v)
        ml=v+sum(left);mr=v+sum(right)
        L=np.array([ml**i for i in range(D)]).T;R=np.array([mr**i for i in range(D)]).T
        el=[expand(g,left,n) for g in groups];er=[expand(g,right,n) for g in groups]
        Q=np.zeros((len(features),len(features)))
        for i,g in enumerate(groups):
            for j,h in enumerate(groups):
                moment=np.zeros(n)
                for kg,cg in el[i].items():
                    for kh,ch in er[j].items():
                        ks=tuple(sorted(kg+kh));moment+=cg*ch*pdmom(a,ks)*v**sum(ks)
                Q[i*D:(i+1)*D,j*D:(j+1)*D]=L.T@((wt*moment)[:,None]*R)
        return Q
    V,X,Y=np.meshgrid(v,z,z,indexing='ij');Wv,Wx,Wy=np.meshgrid(vw,zw,zw,indexing='ij')
    U1=(1-V)*X;U2=(1-V)*(1-X)*Y
    wt=Wv*Wx*Wy*(1-V)**2*(1-X)*(np.pi*phi)**2*np.sinc(phi*U1)*np.sinc(phi*U2)
    M=(cross(V,[],[U1,U2],wt)+cross(V,[U1],[U2],wt))*2*ell**2/np.pi**2
    V,Z=np.meshgrid(v,z,indexing='ij');Wv,Wz=np.meshgrid(vw,zw,indexing='ij');U=(1-V)*Z;wt=Wv*Wz*(1-V)
    M+=cross(V,[],[U],wt*np.pi*phi*np.sinc(phi*U))*abs(1-2*phi)*2*ell/np.pi
    M+=cross(V,[],[],wt*(np.pi*phi)**2*U*np.sinc(phi*U)**2)*2/np.pi**2
    return (M+M.T)/2,G,features

def solve(ell,degree,groups,phi=.5,order=24):
    M,G,features=forms(ell,degree,groups,phi,order);ev,U=eigh(G);keep=ev>ev[-1]*1e-12
    C=U[:,keep]/np.sqrt(ev[keep]);v,x=eigh(C.T@M@C)
    return float(v[-1]-phi*(1-phi)),C@x[:,-1],features,ev,int(sum(keep))

if __name__=='__main__':
    configs=[(4,[(),(2,),(3,),(4,),(2,2)]),(3,[(),(2,),(3,),(4,),(2,2),(2,3),(2,2,2)]),(3,[(),(2,),(3,),(4,),(5,),(2,2),(2,3),(2,4),(3,3),(2,2,2),(2,2,3),(2,2,2,2)])]
    results=[]
    for d,gs in configs:
        t=time.time();opt=minimize_scalar(lambda l:-solve(l,d,gs,order=20)[0],bounds=(1,1.3),method='bounded',options={'xatol':2e-5})
        j,c,f,eg,n=solve(opt.x,d,gs,order=32)
        row={'degree':d,'groups':gs,'ell':float(opt.x),'margin':j,'features':f,'coefs':c.tolist(),'gram_eigen_min':float(eg[0]),'gram_eigen_max':float(eg[-1]),'retained_directions':n,'seconds':time.time()-t}
        print(json.dumps(row),flush=True);results.append(row)
    Path(__file__).with_name('general-prime-feature-results.json').write_text(json.dumps(results,indent=2))
