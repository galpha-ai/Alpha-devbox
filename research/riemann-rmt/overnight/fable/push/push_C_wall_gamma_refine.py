"""Refine C* in the Gamma (domain-wall) model by extremum tracking: between the two zeros of the edge pair, find the
critical point x_c(tau) of q_tau by Newton (derivatives by differentiating the Hankel integral), and solve
h(tau) = q_tau(x_c(tau)) = 0 by secant. The sign-change grid of push_C_wall_gamma.py misses the pair once its gap is
below the grid spacing, so its value 2.11445 is low by about g^2/8 ~ 2e-4."""
import mpmath as mp, time
mp.mp.dps=20
def Gn(w,tau,n):
    tau=mp.mpf(tau); w=mp.mpc(w)
    def f(t,lnt): return (-lnt/(2*mp.pi))**n*mp.exp(t+tau*lnt**2/(4*mp.pi**2)-(w/(2*mp.pi))*lnt)
    ray=mp.quad(lambda x: f(-x,mp.log(x)-1j*mp.pi)-f(-x,mp.log(x)+1j*mp.pi),[1,4,16,64,mp.inf])
    circ=mp.quad(lambda ph: f(mp.expj(ph),1j*ph)*1j*mp.expj(ph),[-mp.pi,0,mp.pi])
    return (ray+circ)/(2j*mp.pi)
def q_derivs(u,tau):
    w=u+1j*tau; G0,G1,G2=Gn(w,tau,0),Gn(w,tau,1),Gn(w,tau,2); e=mp.expj(u/2)*mp.exp(-tau/4)
    return mp.re(e*G0), mp.re(e*(1j*G0/2+G1)), mp.re(e*(-G0/4+1j*G1+G2))
def h(tau,x0):
    x=x0
    for _ in range(30):
        q0,q1,q2=q_derivs(x,tau); dx=-q1/q2; x+=dx
        if abs(dx)<1e-12: break
    q0,q1,q2=q_derivs(x,tau)
    return q0,x
t0=time.time()
# check derivative formulas by finite differences at one point
u0,t1=mp.mpf('0.3'),mp.mpf('2.1')
q0,q1,q2=q_derivs(u0,t1); fd1=mp.diff(lambda x:q_derivs(x,t1)[0],u0); fd2=mp.diff(lambda x:q_derivs(x,t1)[0],u0,2)
print("derivative check:",mp.nstr(q1,10),mp.nstr(fd1,10),"|",mp.nstr(q2,10),mp.nstr(fd2,10),flush=True)
x=mp.mpf('0.3')   # between the pair zeros (0.043pi, 0.152pi at tau=2.1)
ta,tb=mp.mpf('2.1140'),mp.mpf('2.1150')
ha,x=h(ta,x); print(f"tau={ta}: h={mp.nstr(ha,8)} at x={mp.nstr(x,8)}  [{time.time()-t0:.0f}s]",flush=True)
hb,x=h(tb,x); print(f"tau={tb}: h={mp.nstr(hb,8)} at x={mp.nstr(x,8)}  [{time.time()-t0:.0f}s]",flush=True)
for it in range(8):
    tc=tb-hb*(tb-ta)/(hb-ha); hc,x=h(tc,x)
    print(f"secant {it}: tau={mp.nstr(tc,12)} h={mp.nstr(hc,6)} x_c={mp.nstr(x,8)} (x_c/pi={mp.nstr(x/mp.pi,6)})  [{time.time()-t0:.0f}s]",flush=True)
    ta,ha,tb,hb=tb,hb,tc,hc
    if abs(hc)<1e-14: break
print("C* (Gamma model, extremum method) =",mp.nstr(tb,11))
