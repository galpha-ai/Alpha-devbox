"""Exploratory symmetric prime-factor extension of Inoue's continuum form.
Derived insertion formulas, not an independently proved arithmetic theorem.
Coefficients use d_ell(n) times mass polynomials and S_k=sum (log p/log L)^k.
All trial features are symmetric in their prime-factor variables.
"""
from __future__ import annotations
import json,time
from pathlib import Path
import numpy as np
from scipy.special import gamma,roots_jacobi
from scipy.linalg import eigh
from scipy.optimize import minimize_scalar


def pd_moments(a,ks):
    es={0:1.0};e2={}
    for k in ks:
        if k:es[k]=gamma(k)*gamma(a+1)/gamma(a+k)
    for k in ks:
        for l in ks:
            if not k:e2[k,l]=es[l]
            elif not l:e2[k,l]=es[k]
            else:e2[k,l]=(a*gamma(k+l)+a*a*gamma(k)*gamma(l))*gamma(a)/gamma(a+k+l)
    return es,e2


def matrix(phi,ell,degree=4,ks=(0,2,3),order=26):
    a=ell*ell;features=[(i,k) for k in ks for i in range(degree+1)];d=len(features)
    es,e2=pd_moments(a,ks)
    G=np.array([[e2[k,l]/(a+i+j+k+l) for j,l in features] for i,k in features])
    x,w=roots_jacobi(order,0,a-1);v=(x+1)/2;vw=w/2**a
    x,w=roots_jacobi(order,0,0);z=(x+1)/2;zw=w/2
    def expect_cross(v,left,right,wt):
        v=v.ravel();wt=wt.ravel();left=[x.ravel() for x in left];right=[x.ravel() for x in right]
        ml=v+sum(left);mr=v+sum(right)
        al={k:sum(x**k for x in left) if k else np.zeros(len(v)) for k in ks}
        ar={k:sum(x**k for x in right) if k else np.zeros(len(v)) for k in ks}
        Fl=np.array([ml**i*(es[k]*v**k+al[k]) for i,k in features]).T
        Fr=np.array([mr**i*(es[k]*v**k+ar[k]) for i,k in features]).T
        Q=Fl.T@(wt[:,None]*Fr)
        for ik,k in enumerate(ks):
            if not k:continue
            L=np.array([ml**i for i in range(degree+1)]).T
            for il,l in enumerate(ks):
                if not l:continue
                R=np.array([mr**j for j in range(degree+1)]).T
                cov=(e2[k,l]-es[k]*es[l])*v**(k+l)
                Q[ik*(degree+1):(ik+1)*(degree+1),il*(degree+1):(il+1)*(degree+1)]+=L.T@((wt*cov)[:,None]*R)
        return Q
    V,X,Y=np.meshgrid(v,z,z,indexing='ij');Wv,Wx,Wy=np.meshgrid(vw,zw,zw,indexing='ij')
    U1=(1-V)*X;U2=(1-V)*(1-X)*Y
    wt=Wv*Wx*Wy*(1-V)**2*(1-X)*(np.pi*phi)**2*np.sinc(phi*U1)*np.sinc(phi*U2)
    M=(expect_cross(V,[],[U1,U2],wt)+expect_cross(V,[U1],[U2],wt))*2*ell**2/np.pi**2
    V,Z=np.meshgrid(v,z,indexing='ij');Wv,Wz=np.meshgrid(vw,zw,indexing='ij');U=(1-V)*Z;wt=Wv*Wz*(1-V)
    M+=expect_cross(V,[],[U],wt*np.pi*phi*np.sinc(phi*U))*abs(1-2*phi)*2*ell/np.pi
    M+=expect_cross(V,[],[],wt*(np.pi*phi)**2*U*np.sinc(phi*U)**2)*2/np.pi**2
    return (M+M.T)/2,G,features


def solve(ell,phi=.5,degree=4,ks=(0,2,3),order=26):
    M,G,features=matrix(phi,ell,degree,ks,order)
    eg,vg=eigh(G);good=eg>eg[-1]*1e-13
    C=vg[:,good]/np.sqrt(eg[good])
    e,v=eigh(C.T@M@C);vec=C@v[:,-1]
    return float(e[-1]-phi*(1-phi)),vec,features,eg

if __name__=='__main__':
    out=[]
    for ks,d in (((0,),6),((0,2),4),((0,2,3),4),((0,2,3,4),4),((0,2,3,4,5),4)):
        t=time.time();opt=minimize_scalar(lambda l:-solve(l,degree=d,ks=ks,order=22)[0],bounds=(1,1.5),method='bounded',options={'xatol':1e-5})
        j,c,f,eg=solve(opt.x,degree=d,ks=ks,order=36)
        row={'ks':ks,'degree':d,'ell':float(opt.x),'margin':j,'coefs':c.tolist(),'features':f,'gram_eigen_min':float(eg[0]),'gram_condition':float(eg[-1]/eg[0]),'seconds':time.time()-t}
        out.append(row);print(json.dumps(row),flush=True)
    Path(__file__).with_name('prime-feature-results.json').write_text(json.dumps(out,indent=2))
