"""Independent, bounded audit of the recovered mathematical research.

Run with Python + numpy/scipy/sympy. This is a numerical/algebraic regression
audit, not a proof checker. Original research files are never modified.
"""
from pathlib import Path
from itertools import combinations
from collections import Counter
import hashlib
import json
import math
import time
import numpy as np
import sympy as sp

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "sources/research/riemann-rmt"
if not SRC.exists():
    SRC = ROOT.parents[1]  # Published under riemann-rmt/handoff/astra-2026-09-05.
records = []


def record(name, condition, detail):
    records.append({"name": name, "passed": bool(condition), "detail": detail})
    print(("PASS " if condition else "FAIL ") + name + ": " + str(detail))


def partitions(n, top=None):
    if n == 0:
        yield ()
    else:
        for j in range(min(n, n if top is None else top), 0, -1):
            for rest in partitions(n-j, j):
                yield (j,) + rest


def com_check(n):
    sites = np.array(list(combinations(range(2*n), n)))
    z = np.exp(1j*np.pi*sites/n)
    weights = np.ones(len(sites))
    for i, j in combinations(range(n), 2):
        weights *= np.abs(z[:, i]-z[:, j])**2/(2*n)**(2/(n-1))
    # Independently check the Vandermonde normalization before renormalizing.
    normalization_error = abs(weights.sum()-1)
    weights /= weights.sum()
    com = sites.sum(axis=1) % n
    p = {k: (z**k).sum(axis=1) for k in range(1, n+1)}
    rows = [np.bincount(com, weights=weights, minlength=n)]
    largest = (0.0, None)
    g = 1 + 0.5*np.cos(4*np.pi*np.arange(n)/n)
    for d in range(1, n+1):
        ps = list(partitions(d))
        obs = {lam: np.prod([p[k] for k in lam], axis=0) for lam in ps}
        for lam in ps:
            for nu in ps:
                v = weights*obs[lam]*obs[nu].conj()
                row = np.array([v[com == x].sum() for x in range(n)])
                rows.extend([row.real, row.imag])
                err = abs(row @ (g-1))
                if err > largest[0]:
                    largest = (float(err), [list(lam), list(nu)])
    rank = np.linalg.matrix_rank(np.array(rows), tol=1e-8)
    clock = (np.diff(sites, axis=1) == 2).all(axis=1)
    return {"null_dimension": int(n-rank), "modulation_error": largest,
            "normalization_error": float(normalization_error),
            "clock_mass": float(weights[clock].sum())}


def main():
    started = time.monotonic()
    qstar = .5+1/math.sqrt(2)/math.tan(1/math.sqrt(2))
    errs = []
    for n in (2, 3, 5, 8, 13, 21, 40, 80):
        h = 1/n
        a = 1+1/(3*n*n)
        mat = h*a*np.eye(n)+h**3*np.abs(np.subtract.outer(np.arange(n), np.arange(n)))
        v = np.linalg.solve(mat, np.ones(n))
        v /= h*v.sum()
        theta = math.acos(1-1/(n*n*a))
        closed = .5+a*n/2*math.sin(theta)/math.tan(n*theta/2)
        errs.append(abs(float(v@mat@v)-closed))
    record("Corrected Galerkin angle", max(errs)<1e-11, {"max_error":max(errs)})
    import mpmath as mp
    with mp.workdps(60):
        t=1/mp.sqrt(2); q=.5+t/mp.tan(t)
        c=(1/mp.sin(t)**2-mp.sqrt(2)/mp.tan(t))/24
        residuals=[]
        for n in (50,100,200,400):
            a=1+mp.mpf(1)/(3*n*n); theta=mp.acos(1-1/(n*n*a))
            qn=mp.mpf('.5')+a*n/2*mp.sin(theta)/mp.tan(n*theta/2)
            residuals.append(float((qn-q-c/n**2)*n**4))
    record("Galerkin second-order coefficient", abs(residuals[-1]-residuals[-2])<1e-6,
           {"n4_residuals":residuals,"delta_MT":2-qstar})
    rng=np.random.default_rng(20260904)
    errors=[]
    for n in (3,4,7,11):
        for _ in range(30):
            m=rng.multinomial(n,np.ones(2*n)/(2*n))
            q=m+np.roll(m,-1)-1
            for k in range(1,n):
                phase=np.exp(-1j*np.pi*k*np.arange(2*n)/n)
                errors.append(abs(q@phase-(1+np.exp(1j*np.pi*k/n))*(m@phase)))
    record("Charge filter with negative Fourier convention", max(errors)<1e-10,{"max_error":float(max(errors))})
    # Open rectangular graph: all non-backtracking closed 4-walks are plaquettes.
    n1,n2=4,5
    phx=rng.uniform(-np.pi,np.pi,(n1-1,n2)); phy=rng.uniform(-np.pi,np.pi,(n1,n2-1))
    def adjacency(flat):
        a=np.zeros((n1*n2,n1*n2),complex)
        for x in range(n1):
            for y in range(n2):
                for dx,dy in ((1,0),(0,1)):
                    if x+dx>=n1 or y+dy>=n2: continue
                    p=0 if flat else (phx[x,y] if dx else phy[x,y])
                    i=x*n2+y;j=(x+dx)*n2+y+dy
                    a[i,j]=np.exp(1j*p);a[j,i]=a[i,j].conjugate()
        return a
    a=adjacency(False);f=adjacency(True)
    lhs=np.trace(np.linalg.matrix_power(f,4)-np.linalg.matrix_power(a,4)).real
    rhs=16*sum(math.sin((phx[x,y]+phy[x+1,y]-phx[x,y+1]-phy[x,y])/2)**2
               for x in range(n1-1) for y in range(n2-1))
    record("Wilson trace on open box", abs(lhs-rhs)<1e-10,{"lhs":float(lhs),"rhs":float(rhs)})
    # Detect endpoint estimate failure even when g is a shortest gap.
    g=.05; xb=2*np.pi-.15
    background=(1/math.tan(xb/2)-1/math.tan((xb+g)/2))/g
    old_bound=.5/math.sin(xb/2)**2
    exact=math.sin(g/2)/(g*math.sin(xb/2)*math.sin((xb+g)/2))
    record("Counterexample to old background endpoint bound",background>old_bound and abs(background-exact)<1e-10,
           {"g":g,"xb":xb,"background":background,"old_upper_bound":old_bound,"correct_exact":exact})
    lam=sp.symbols('lam',real=True)
    cayley=(lam-sp.I)/(lam+sp.I)
    phase_derivative=sp.simplify(sp.diff(cayley,lam)/cayley/sp.I)
    record("Cayley phase derivative sign",sp.simplify(phase_derivative-2/(1+lam**2))==0,{"derivative":str(phase_derivative)})
    for n in (4,5,6):
        result=com_check(n)
        expected_dim=0 if n==4 else n-3
        record(f"COM modulation dimension N={n}",result['null_dimension']==expected_dim,result)
        record(f"ACUE clock mass N={n}",abs(result['clock_mass']-2**(1-n))<1e-11,
               {"measured":result['clock_mass'],"expected":2**(1-n)})
        record(f"Frequency-two COM test N={n}",result['modulation_error'][0]>.1 if n==4 else result['modulation_error'][0]<1e-8,
               result['modulation_error'])
    tuple186=np.array([0,2,6,12,20,26,30,32,36,42,48,50,56,60,68,72,78,86,90,92,98,102,110,116,120,126,132,138,140,146,152,156,158,162,168,170,176,180,182,186])
    for label,values in (("Published 40-tuple",tuple186),("Historical H2 tuple",np.load(SRC/'p9_tuple_k15856.npy'))):
        k=len(values);bad=[]
        for p in sp.primerange(2,k+1):
            if len(np.unique(values%p))==p:bad.append(int(p))
        record(label+" admissibility",not bad and len(np.unique(values))==k,
               {"k":k,"diameter":int(values.max()-values.min()),"bad_primes":bad,"all_primes_up_to_k_checked":True})
    lean=(SRC/'lean/DepthComparison.lean').read_text()
    actual_sorry=sum(1 for line in lean.splitlines() if line.strip()=='sorry')
    depth_statement=lean.split('theorem depth_ge',1)[1].split(':=',1)[0]
    conclusion=depth_statement.rsplit(':',1)[-1]
    record("Lean audit detects two actual sorry placeholders",actual_sorry==2,{"actual_sorry_lines":actual_sorry})
    record("Lean depth_ge omits D in conclusion",'D' not in conclusion,{"conclusion":conclusion.strip()})
    original_path=ROOT/'tmp/verify-codex-original.log'
    if not original_path.exists():
        original_path=ROOT/'verify-codex-original.log'
    original=original_path.read_text()
    counts={s:sum(line.startswith(s+' ') for line in original.splitlines()) for s in ('PASS','FAIL','SKIP')}
    record("Original verification log preserved",counts['FAIL']==4 and counts['SKIP']==1,counts)
    # Signed debt price is exactly greater than 2; it is not a threshold below 1.
    beta=sp.Rational(23051796480,10991046857)
    record("Signed critical price exact comparison",beta>2,{"beta_exact":str(beta),"beta_decimal":float(beta)})
    summary={"scope":"Bounded independent audit; no zeta or prime-gap proof certified", "checks":records,
             "elapsed_seconds":time.monotonic()-started,"all_passed":all(r['passed'] for r in records)}
    (ROOT/'audit_results.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({"checks":len(records),"all_passed":summary['all_passed'],"elapsed_seconds":summary['elapsed_seconds']}))
    if not summary['all_passed']: raise SystemExit(1)


if __name__=='__main__':
    main()
