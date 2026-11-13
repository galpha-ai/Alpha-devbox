"""Structural checks of algebraic identities, not analytic asymptotics."""
import json
from pathlib import Path
import numpy as np
from arithmetic_operator import make_A
from inoue_variational import solve
from prime_feature_variational import solve as feature_solve
from general_prime_features import solve as general_solve

rng=np.random.default_rng(20260905)
checks=[]

def check(name,value,tol):
    assert value<tol,(name,value,tol)
    checks.append({'name':name,'residual':float(value),'tolerance':tol})

L=97
r=rng.normal(size=L)+1j*rng.normal(size=L)
g=rng.normal(size=L)+1j*rng.normal(size=L)
a=rng.normal(size=L)+1j*rng.normal(size=L)
def conv(x,y):
    b=np.zeros(L,dtype=complex)
    for k in range(1,L+1):
        for m in range(1,L//k+1):b[k*m-1]+=x[k-1]*y[m-1]
    return b
bg=conv(g,r);ba=conv(a,r);q=np.arange(1,L+1)
lhs=np.real(np.sum((2*bg-ba)*np.conj(ba)/q))
rhs=np.sum(abs(bg)**2/q)-np.sum(abs(ba-bg)**2/q)
check('coefficient-space saturation completion',abs(lhs-rhs),1e-11)
A=make_A(L).toarray();x=r/np.sqrt(q);B=-1j*A
K=A.T@A+(A@A+(A.T)@(A.T))/2
lhs=np.linalg.norm(B@x)**2-np.real(np.vdot(x,B@B@x))
rhs=np.real(np.vdot(x,K@x))
check('arithmetic operator sign and normalization identity',abs(lhs-rhs),1e-11)
X=rng.normal(size=20)+1j*rng.normal(size=20);B0=rng.normal(size=20)+1j*rng.normal(size=20);C=rng.normal(size=20)+1j*rng.normal(size=20)
old=2*np.real(np.vdot(B0,X))-np.linalg.norm(B0)**2
recovered=old+2*np.real(np.vdot(C,X-B0))-np.linalg.norm(C)**2
combined=2*np.real(np.vdot(B0+C,X))-np.linalg.norm(B0+C)**2
check('residual recovery equals combined approximator',abs(recovered-combined),1e-11)
for ell in (1,1.1,1.1763):
    j,_=solve(.5,ell,4,28)
    k,*_=feature_solve(ell,degree=4,ks=(0,),order=28)
    l,*_=general_solve(ell,4,[()],order=28)
    check(f'prime-feature forms reduce to original ell={ell}',max(abs(j-k),abs(j-l)),1e-10)
# Original supplied result compared to independently produced output.
p=Path(__file__).parents[2]
original_path=p/'sources/user-full-context-package/inoue_resonance_probe_results.json'
if not original_path.exists():
    original_path=Path(__file__).with_name('original_inoue_probe_results.json')
orig=json.loads(original_path.read_text())
new=json.loads(Path(__file__).with_name('variational-results.json').read_text())
check('original vs independent baseline',abs(orig['baseline_margin']-new['paper_trial']['48']),1e-12)
check('original vs independent degree14',abs(orig['half_barrier_probes'][-1]['margin']-new['half_boundary'][-1]['margin']),1e-11)
check('original vs independent sign crossing',abs(orig['degree8_numerical_sign_crossing']-new['degree8_zero']),1e-8)
Path(__file__).with_name('algebra-check-results.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
