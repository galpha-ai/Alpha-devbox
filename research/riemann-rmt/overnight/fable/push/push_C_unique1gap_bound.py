"""Rigorous-constant computation for the unique-1-gap ceiling theorem (Task C, step 3).
Hypotheses: lattice configuration with exactly one gap = pi/N, all other gaps >= 2pi/N.
Chain: (i) Theorem A for every other gap: g_i(s) >= G(s) := 2 arccos(e^s cos(pi/N)) for s < -log cos(pi/N);
 (ii) for the critical pair, g' <= -2cot(g/2) + g S*(s), S* = (1/2) sum_k csc^2(dist_k/2) (mean value theorem, csc^2(y/2)
      monotone on each half of (0,2pi), so the max is at an endpoint);
 (iii) ordering: the j-th point on either side of the pair is at distance >= j G(s) from the nearer endpoint, and
      each point is counted on its shorter side (j G <= pi), so S* <= sum_{j>=1, jG<=pi} csc^2(jG/2);
 (iv) csc^2(y) <= 1/y^2 + 1 on (0,pi/2]  =>  S*(s) <= 2pi^2/(3G^2) + pi/G   [Sbar];
 (v) cot(x) >= 1/x - x/3 - x^3/45 - x^5/472.5·... : we use the elementary bound cot x >= 1/x - x/3 - x^3/40 for 0<x<=1 (checked),
      so -2cot(g/2) <= -4/g + g/3 + g^3/160;
 (vi) y = g^2: y' <= -8 + 2y(1/3 + Sbar(s)) + y^2/80 ;  comparison with the ODE solution Y (Y(0)=pi^2/N^2) gives D <= first zero of Y.
Output: tau_1(N) = N^2 * (first zero of Y) for N = 4..2048 and the N->infinity limit ODE in tau."""
import numpy as np
from scipy.integrate import solve_ivp
# check (v) numerically
import mpmath as mp
mp.mp.dps=30
xs=[mp.mpf(i)/2000 for i in range(1,2001)]
assert all(mp.cot(x) >= 1/x - x/3 - x**3/40 for x in xs), "cot bound fails"      # cot x = 1/x - sum_{n>=1} 2^{2n}|B_{2n}| x^{2n-1}/(2n)!, all terms negative
ys=[mp.pi/2*mp.mpf(i)/2000 for i in range(1,2001)]
assert all(mp.csc(y)**2 <= 1/y**2+1 for y in ys), "csc bound fails"           # csc^2 y - 1/y^2 increases from 1/3 to 1-4/pi^2 on (0,pi/2]
print("elementary bounds (v),(iv) verified on 2000-point grids at 30 digits")
def tau1(N):
    c=np.cos(np.pi/N); smax=-np.log(c)
    def G(s): return 2*np.arccos(min(1.0,np.exp(s)*c))
    def Sbar(s):
        g=G(s); return 2*np.pi**2/(3*g*g)+np.pi/g
    def f(s,Y): return [-8+2*Y[0]*(1/3+Sbar(s))+Y[0]**2/80]
    ev=lambda s,Y: Y[0]; ev.terminal=True; ev.direction=-1
    sol=solve_ivp(f,(0,0.999*smax),[np.pi**2/N**2],method='DOP853',rtol=1e-11,atol=1e-16,events=ev)
    if len(sol.t_events[0])==0: return np.nan
    return N*N*sol.t_events[0][0]
print("N, tau_1(N) = rigorous upper bound on N^2 D for unique-1-gap configurations")
for N in [4,5,6,7,8,9,10,11,12,16,24,32,64,128,256,512,1024,2048]:
    print(f"  N={N:5d}  tau_1 = {tau1(N):.6f}")
# limit ODE in tau: G^2 N^2 -> 4pi^2 (1 - 2 tau/pi^2) ; Sbar/N^2 -> 1/(6(1-2tau/pi^2)) ; y=N^2 g^2/pi^2:
def flim(t,y): return [-8/np.pi**2 + y[0]/(3*(1-2*t/np.pi**2))]
ev=lambda t,y: y[0]; ev.terminal=True; ev.direction=-1
sol=solve_ivp(flim,(0,4.9),[1.0],method='DOP853',rtol=1e-12,atol=1e-14,events=ev)
print(f"  N->inf limit: tau_1(inf) = {sol.t_events[0][0]:.6f}")
# what the same chain gives if the stiffness were frozen at its t=0 value (not rigorous; for comparison)
def ffro(t,y): return [-8/np.pi**2 + y[0]/3]
sol=solve_ivp(ffro,(0,4.9),[1.0],method='DOP853',rtol=1e-12,atol=1e-14,events=ev)
print(f"  (frozen stiffness N^2/6, not rigorous): {sol.t_events[0][0]:.6f};  two-body only: {np.pi**2/8:.6f}")

# ---- fully explicit rigorous version: piecewise-frozen stiffness majorant (no ODE solver) ----
# On [s_i, s_{i+1}]: S*(s) <= Sbar(s_{i+1}) (Sbar increasing since G decreasing), Y^2 <= Y*Y0, so
# Y' <= -8 + kappa_i Y with kappa_i = 2/3 + 2 Sbar(s_{i+1}) + Y0/80  -> exact linear solution on the piece.
def tau1_rig(N,pieces=4000):
    c=np.cos(np.pi/N); smax=-np.log(c); Y0=np.pi**2/N**2
    def G(s): return 2*np.arccos(min(1.0,np.exp(s)*c))
    def Sbar(s): g=G(s); return 2*np.pi**2/(3*g*g)+np.pi/g
    h=0.99*smax/pieces; Y=Y0; s=0.0
    for i in range(pieces):
        kap=2/3+2*Sbar(s+h)+Y0/80
        Ynew=8/kap+(Y-8/kap)*np.exp(kap*h)
        if Ynew<=0:
            # exact zero of the linear solution on this piece
            sz=s+np.log((8/kap)/(8/kap-Y))/kap
            return N*N*sz
        Y=Ynew; s+=h
        if Y>Y0: return np.nan   # would violate the g<=pi/N assumption used in the cot bound
    return np.nan
print("\nRigorous piecewise-frozen majorant (4000 pieces, each piece solved in closed form):")
for N in [8,9,10,12,16,32,64,256,1024]:
    print(f"  N={N:5d}  tau_1^rig = {tau1_rig(N):.6f}")
