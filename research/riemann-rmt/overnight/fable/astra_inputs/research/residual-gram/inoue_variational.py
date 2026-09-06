"""Independent floating quadrature of Inoue (2026), Theorem 2.
No interval certification. Jacobi polynomial Rayleigh-Ritz subspaces only.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from scipy.special import roots_jacobi, eval_jacobi
from scipy.linalg import eigh
from scipy.optimize import minimize_scalar, brentq


def basis(x, degree, a):
    x=np.asarray(x).ravel()
    return np.array([np.sqrt(2*n+a)*eval_jacobi(n,0,a-1,2*x-1) for n in range(degree+1)]).T


def matrices(phi:float, ell:float, degree:int, order:int=32):
    a=ell*ell
    vx,vw=roots_jacobi(order,0,a-1)
    v=(vx+1)/2; vw=vw/(2**a)
    zx,zw=roots_jacobi(order,0,0); z=(zx+1)/2; zw=zw/2
    # Triple simplex parametrization (v,u1,u2).
    V,X,Y=np.meshgrid(v,z,z,indexing='ij')
    Wv,Wx,Wy=np.meshgrid(vw,zw,zw,indexing='ij')
    U1=(1-V)*X; U2=(1-V)*(1-X)*Y
    wt=(Wv*Wx*Wy*(1-V)**2*(1-X)*np.pi**2*phi**2*np.sinc(phi*U1)*np.sinc(phi*U2)).ravel()
    F0=basis(V,degree,a); F1=basis(V+U1,degree,a)
    F2=basis(V+U2,degree,a); F12=basis(V+U1+U2,degree,a)
    M2=(F0.T@(wt[:,None]*F12)+F1.T@(wt[:,None]*F2))*2*ell**2/np.pi**2
    # Two-variable terms.
    V,Z=np.meshgrid(v,z,indexing='ij'); Wv,Wz=np.meshgrid(vw,zw,indexing='ij')
    U=(1-V)*Z; W=Wv*Wz*(1-V)
    F0=basis(V,degree,a); F1=basis(V+U,degree,a)
    wt=(W*np.pi*phi*np.sinc(phi*U)).ravel()
    M1=F0.T@(wt[:,None]*F1)*(abs(1-2*phi)*2*ell/np.pi)
    wt=(W*(np.pi*phi)**2*U*np.sinc(phi*U)**2).ravel()
    M3=F0.T@(wt[:,None]*F0)*2/np.pi**2
    M=M1+M2+M3
    return (M+M.T)/2


def solve(phi,ell,degree,order=32):
    M=matrices(phi,ell,degree,order)
    eigs,vecs=eigh(M)
    return eigs[-1]-phi*(1-phi),vecs[:,-1]


def paper_trial(order):
    ell=1.15; phi=.508949; a=ell*ell
    x,w=roots_jacobi(24,0,a-1); x=(x+1)/2; w=w/2**a
    c=basis(x,1,a).T@(w*(1-.7*x))
    M=matrices(phi,ell,1,order)
    return float(c@M@c/(c@c)-phi*(1-phi))


def main():
    out={'status':'floating numerical experiment; not a proof','paper_trial':{},'half_boundary':[]}
    for q in (20,32,48):
        out['paper_trial'][str(q)]=paper_trial(q)
        print('paper',q,out['paper_trial'][str(q)],flush=True)
    for d in (2,6,14):
        opt=minimize_scalar(lambda ell:-solve(.5,ell,d,28)[0],bounds=(1,2.2),method='bounded',options={'xatol':1e-7})
        j,vec=solve(.5,opt.x,d,48)
        entry={'degree':d,'ell':float(opt.x),'margin':float(j),'gram_energy_deficit':float(-j*2*np.pi**2),'jacobi_coefficients':vec.tolist()}
        out['half_boundary'].append(entry)
        print('half',entry,flush=True)
    # Search a finite-dimensional zero; the resulting improvement is only diagnostic.
    def best(phi):
        opt=minimize_scalar(lambda ell:-solve(phi,ell,8,28)[0],bounds=(1.05,1.3),method='bounded',options={'xatol':2e-6})
        return -opt.fun
    crossing=brentq(best,.508,.510,xtol=2e-9)
    out['degree8_zero']=float(crossing)
    print('crossing',crossing,flush=True)
    Path(__file__).with_name('variational-results.json').write_text(json.dumps(out,indent=2))

if __name__=='__main__':main()
