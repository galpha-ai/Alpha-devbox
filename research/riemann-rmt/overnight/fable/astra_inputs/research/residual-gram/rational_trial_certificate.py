"""Exact rational enclosure of one symmetric-prime-feature continuum trial.
This certifies the finite variational integral, NOT its arithmetic transfer.
Uses Machin's formula with alternating rational bounds and sine/cosine remainders.
"""
from __future__ import annotations
from fractions import Fraction as F
from functools import lru_cache
from math import factorial
from pathlib import Path
import json
import sympy as sp


def atan_bounds(q,n):
    val=sum((F((-1)**j,(2*j+1)*q**(2*j+1)) for j in range(n)),F())
    nxt=F((-1)**n,(2*n+1)*q**(2*n+1))
    return min(val,val+nxt),max(val,val+nxt)

lo5,hi5=atan_bounds(5,45);lo239,hi239=atan_bounds(239,15)
PI=(16*lo5-4*hi239,16*hi5-4*lo239)
ell=F(16,15);a=ell**2
v,u,w,S=sp.symbols('v u w S')
f=(145+3*v-116*v**2+71*v**3-6*v**4)/100
g=(-563+1682*v-2479*v**2+1751*v**3-488*v**4)/100
H=f+g*S
mu2=1/(a+1);mu22=(a+6)/((a+1)*(a+2)*(a+3))

def avg(expr):
    poly=sp.Poly(sp.expand(expr),S)
    return sp.expand(sum(c*{0:1,1:sp.Rational(mu2.numerator,mu2.denominator)*v**2,2:sp.Rational(mu22.numerator,mu22.denominator)*v**4}[k[0]] for k,c in poly.terms()))

def shift(*xs):return H.subs({v:v+sum(xs),S:S+sum(x*x for x in xs)},simultaneous=True)
P=sp.Poly(avg(H*shift(u,w)+shift(u)*shift(w)),v,u,w)
J=sp.Poly(avg(H*H),v)
terms=[(k,F(c)) for k,c in P.terms()]
jn=[(k[0],F(c)) for k,c in J.terms()]

@lru_cache(None)
def simplex(k,p,q):
    ans=F(factorial(p)*factorial(q),1)
    for j in range(p+q+3):ans/=a+k+j
    return ans

@lru_cache(None)
def triangle(k,p):
    ans=F(factorial(p),1)
    for j in range(p+2):ans/=a+k+j
    return ans


def scale_interval(coef,lo,hi):return (coef*lo,coef*hi) if coef>=0 else (coef*hi,coef*lo)

def add_interval(acc,b):return acc[0]+b[0],acc[1]+b[1]

norm=sum((c/(a+k) for k,c in jn),F())
assert norm>0
q2=(F(),F());N=10
for n in range(N+1):
    for m in range(N+1):
        integ=sum((c*simplex(k,p+2*n,q+2*m) for (k,p,q),c in terms),F())
        coef=ell**2*F((-1)**(n+m),2*2**(2*n+2*m)*factorial(2*n+1)*factorial(2*m+1))*integ
        q2=add_interval(q2,scale_interval(coef,PI[0]**(2*n+2*m),PI[1]**(2*n+2*m)))
absP=sum((abs(c)*simplex(k,p,q) for (k,p,q),c in terms),F())
R=(PI[1]/2)**(2*N+2)/factorial(2*N+3)
err2=ell**2/2*(2*R+R*R)*absP
q2=(q2[0]-err2,q2[1]+err2)
q3=(F(),F());NC=13
for n in range(1,NC+1):
    integ=sum((c*triangle(k,2*n-1) for k,c in jn),F())
    coef=F((-1)**(n+1),factorial(2*n))*integ
    q3=add_interval(q3,scale_interval(coef,PI[0]**(2*n-2),PI[1]**(2*n-2)))
err3=PI[1]**(2*NC)/factorial(2*NC+2)*sum((abs(c)*triangle(k,2*NC+1) for k,c in jn),F())
q3=(q3[0]-err3,q3[1]+err3)
margin=((q2[0]+q3[0])/norm-F(1,4),(q2[1]+q3[1])/norm-F(1,4))
# Exact claims; the trial improves the baseline but does not cross one half.
print('margin',float(margin[0]),float(margin[1]),flush=True)
assert F(-1467,100000)<margin[0]<margin[1]<F(-1465,100000)
scale=10**60
cert_margin=(F(margin[0].numerator*scale//margin[0].denominator,scale),F(-((-margin[1].numerator*scale)//margin[1].denominator),scale))
assert cert_margin[0]<=margin[0]<margin[1]<=cert_margin[1]
assert simplex(0,0,0)==1/(a*(a+1)*(a+2))
assert triangle(0,0)==1/(a*(a+1))
result={'status':'Exact rational continuum-integral certificate; arithmetic transfer NOT certified','ell':'16/15','f':'(145+3v-116v^2+71v^3-6v^4)/100','g':'(-563+1682v-2479v^2+1751v^3-488v^4)/100','feature':'H=f(v)+g(v) S2','norm':str(norm),'margin_enclosure_float':[float(x) for x in margin],'margin_enclosure_exact':[str(x) for x in cert_margin],'pi_enclosure_exact':[str(x) for x in PI],'taylor_error_abs_float':[float(err2),float(err3)],'asserted_rational_interval':['-1467/100000','-1465/100000']}
Path(__file__).with_name('rational-trial-certificate.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if not k.endswith('_exact')},indent=2))
