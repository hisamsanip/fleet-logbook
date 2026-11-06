import numpy as np
from CoolProp.CoolProp import PropsSI
from scipy.integrate import quad
from scipy.optimize import brentq
R=8.314
FL={'CO2':'CO2','H2':'Hydrogen','MeOH':'Methanol','H2O':'Water'}
def cp(s,T): return PropsSI('Cp0molar','T',T,'P',1e5,FL[s])     # J/mol/K ideal gas
def H_ig(s,T,Tref=298.15): return quad(lambda t:cp(s,t),Tref,T)[0]
# ------------- mass balance numbers (kmol/h) from the PDF
n3={'CO2':2170.139,'H2':6944.445}
n4={'CO2':1779.514,'H2':5772.570,'MeOH':390.625,'H2O':390.625}
xi=390.625
# ------------- 1) reaction heat and adiabatic rise
dHf={'CO2':-393.51e3,'H2':0,'MeOH':-200.66e3,'H2O':-241.83e3}
dGf={'CO2':-394.36e3,'H2':0,'MeOH':-161.96e3,'H2O':-228.57e3}
nu={'CO2':-1,'H2':-3,'MeOH':1,'H2O':1}
dH298=sum(nu[s]*dHf[s] for s in nu); dG298=sum(nu[s]*dGf[s] for s in nu)
print(f"dH298={dH298/1e3:.1f} kJ/mol  dG298={dG298/1e3:.1f} kJ/mol")
def dHr(T): return dH298+sum(nu[s]*H_ig(s,T) for s in nu)
def dSr(T):
    dS298=(dH298-dG298)/298.15
    return dS298+sum(nu[s]*quad(lambda t:cp(s,t)/t,298.15,T)[0] for s in nu)
def Kp(T): return np.exp(-(dHr(T)-T*dSr(T))/(R*T))     # bar^-2, ideal gas
Q_rxn=xi*1e3/3600*(-dHr(483.15))/1e6
print(f"Reaction heat released at 210C: {Q_rxn:.2f} MW  (xi={xi} kmol/h)")
def Tad(Tin_C):
    Tin=Tin_C+273.15
    f=lambda T: sum(n4[s]*1e3/3600*quad(lambda t:cp(s,t),Tin,T)[0] for s in n4)+xi*1e3/3600*dHr(Tin)
    return brentq(f,Tin,Tin+400)-273.15
for Tin in [180,200,210,230]:
    print(f"adiabatic: inlet {Tin} C -> outlet {Tad(Tin):.0f} C")
# ------------- 2) equilibrium conversion (methanol reaction only, ideal gas) r=3.2
def Xeq(T_C,P=50.0,r=3.2):
    T=T_C+273.15; K=Kp(T)
    def f(X):
        nC=1-X; nH=r-3*X; nM=X; nW=X; nt=1+r-2*X
        return (nM*nW*nt**2)/(nC*nH**3*P**2)-K
    return brentq(f,1e-9,0.9999)
for T in [200,210,220,230,250,270,287]:
    print(f"equilibrium CO2 conversion (CH3OH reaction only, ideal gas, 50 bar, H2:CO2=3.2) at {T} C: {Xeq(T)*100:.1f}%")
# ------------- 3) duties
def Qgas(n,T1,T2): return sum(n[s]*1e3/3600*quad(lambda t:cp(s,t),T1+273.15,T2+273.15)[0] for s in n)/1e6
print(f"E-101 duty 45->210C (stream 3 gas): {Qgas(n3,45,210):.1f} MW ;  45->230C: {Qgas(n3,45,230):.1f} MW")
# E-102: cool stream 4 from T4 to 45 C, condense MeOH+H2O (treated as ideal gas down to condensation, liquid at 45C)
def Q_E102(T4):
    q=Qgas({'CO2':n4['CO2'],'H2':n4['H2']},45,T4)
    for s in ('MeOH','H2O'):
        Hv=PropsSI('H','T',T4+273.15,'P',1e5,FL[s])           # J/kg ideal-ish vapour
        Hl=PropsSI('H','T',318.15,'Q',0,FL[s])
        MW={'MeOH':32.04,'H2O':18.015}[s]
        q+=n4[s]*1e3/3600*(Hv-Hl)*MW/1000/1e6
    return q
for T4 in [250,280]: print(f"E-102 duty (cool stream 4 from {T4} to 45C incl. condensation): {Q_E102(T4):.1f} MW")
# ------------- 4) compressors (eta 0.75, ideal-gas power law)
def W(g,T1,r,eta=0.75): k=(g-1)/g; return R*T1/k*(r**k-1)/eta   # J/mol per stage
def Pwr(n_kmolh,g,T1_C,P1,P2,st): r=(P2/P1)**(1/st); return n_kmolh*1e3/3600*W(g,T1_C+273.15,r)*st/1e6
print(f"K-101 CO2 399.5 kmol/h 1->50 bar 4 stages: {Pwr(399.523,1.29,40,1,50,4):.2f} MW (first stage from 25C slightly less)")
print(f"K-102 H2 1200.7 kmol/h  1->50 bar 4 stages: {Pwr(1200.738,1.41,40,1,50,4):.2f} MW ;  30->50 bar 1 stage (25C): {Pwr(1200.738,1.41,25,30,50,1):.2f} MW")
print(f"K-103 recycle 7514 kmol/h 49->50 bar: {Pwr(7514.323,1.38,45,49,50,1)*1e3:.0f} kW")
# ------------- 5) reactor volumetric flow & V-101 sizing
n3t=sum(n3.values()); V3=n3t*1e3/3600*R*(210+273.15)/(50e5)      # m3/s ideal
print(f"stream 3 volumetric flow at 210C, 50 bar (ideal): {V3:.2f} m3/s = {V3*3600:.0f} m3/h ;  Nm3/h = {n3t*22.414:.0f}")
for ghsv in [5000,8000,10000]: print(f"  illustrative catalyst volume at GHSV {ghsv} 1/h (Nm3/h per m3): {n3t*22.414/ghsv:.1f} m3")
n5t=7552.084; MW5=89843.76/7552.084; T=318.15; P=49e5
rhoV=P*MW5/1000/(R*T); QV=n5t*1e3/3600*R*T/P
rhoL=880.0; QL=19531.25/rhoL/3600
K=0.07; uv=K*((rhoL-rhoV)/rhoV)**0.5; A=QV/uv; D=(4*A/np.pi)**0.5
print(f"V-101: MW gas {MW5:.1f}, rho_V {rhoV:.1f} kg/m3, Q_V {QV:.2f} m3/s, Q_L {QL*3600:.1f} m3/h; u_max {uv:.2f} m/s -> D = {D:.2f} m (K=0.07 m/s assumed)")
# ------------- 6) T-101 shortcut (NRTL, McCabe-Thiele, CMO)
from thermo import ChemicalConstantsPackage, FlashVL, GibbsExcessLiquid, IdealGas, NRTL
from thermo.interaction_parameters import IPDB
cons,props=ChemicalConstantsPackage.from_IDs(['methanol','water'])
taus=IPDB.get_ip_asymmetric_matrix('ChemSep NRTL',cons.CASs,'bij'); al=IPDB.get_ip_asymmetric_matrix('ChemSep NRTL',cons.CASs,'alphaij')
liq=GibbsExcessLiquid(VaporPressures=props.VaporPressures,HeatCapacityGases=props.HeatCapacityGases,VolumeLiquids=props.VolumeLiquids,
  EnthalpyVaporizations=props.EnthalpyVaporizations,GibbsExcessModel=NRTL(T=350,xs=[.5,.5],tau_bs=taus,alpha_cs=al),equilibrium_basis='Psat',caloric_basis='Psat',T=350,P=1e5,zs=[.5,.5])
gas=IdealGas(HeatCapacityGases=props.HeatCapacityGases,T=350,P=1e5,zs=[.5,.5])
fl=FlashVL(cons,props,liquid=liq,gas=gas)
xs=np.concatenate([[0.0005,0.001,0.002,0.005],np.linspace(0.01,0.99,99),[0.995,0.998,0.9995]])
ys=[]; Ts=[]
for x in xs:
    r_=fl.flash(P=1.2e5,VF=0,zs=[x,1-x]); ys.append(r_.gas.zs[0]); Ts.append(r_.T-273.15)
ys=np.array(ys); Ts=np.array(Ts)
yeq=lambda x: np.interp(x,xs,ys)
xD=390.234/390.928; xB=0.391/390.322; zF=0.5; q=1.015
print(f"xD={xD:.4f} xB={xB:.5f}; T(bubble) at xD {np.interp(xD,xs,Ts):.1f} C, at xB {np.interp(xB,xs,Ts):.1f} C, at feed {np.interp(0.5,xs,Ts):.1f} C")
# minimum reflux: q-line intersect with equilibrium
def qline_x(y): return (q*0 + zF/ (1) ) if False else None
def y_q(x): return q/(q-1)*x - zF/(q-1)
xq=brentq(lambda x: y_q(x)-yeq(x),0.05,0.95); yq=yeq(xq)
# tangent pinch may occur on other side: check max of operating-line slope
Rmin=(xD-yq)/(yq-xq)
# also check pinch against equilibrium curve for tangency (check all x for minimal slope)
slopes=[(xD-yeq(x))/(yeq(x)-x) for x in np.linspace(xq,0.98,200) if yeq(x)>x]
Rmin=max(Rmin,max(slopes))
for fac in [1.2,1.3,1.5]:
    Rr=fac*Rmin
    # step off from top
    x=xD; y=xD; n=0; feed_stage=None; xs_list=[]
    while x>xB and n<200:
        # equilibrium: find x with yeq(x)=y
        x=np.interp(y,ys,xs); n+=1
        if feed_stage is None and x<=xq: feed_stage=n; 
        if feed_stage is None:
            y=Rr/(Rr+1)*x+xD/(Rr+1)
        else:
            # stripping line through (xB,xB) and intersection of rectifying line with q-line
            xi_=( (xD/(Rr+1)) + zF/(q-1)*1 ) / (q/(q-1) - Rr/(Rr+1)) if False else None
            # intersection:
            a=Rr/(Rr+1); b=xD/(Rr+1); xint=(b+zF/(q-1))/(q/(q-1)-a); yint=a*xint+b
            m=(yint-xB)/(xint-xB); y=xB+m*(x-xB)
    D=390.928; Lr=Rr*D; V=(Rr+1)*D
    lamM=35.2e3; Qc=V*1e3/3600*lamM/1e6
    Vp=V-(1-q)*781.25 if q<1 else V+(q-1)*781.25*0  # q~1
    lamW=40.7e3; Qr=(V+(q-1)*781.25)*1e3/3600*lamW/1e6 if False else (V*lamM/lamW+ (q-1)*781.25)*1e3/3600*lamW/1e6
    print(f"R/Rmin={fac}: R={Rr:.2f} (Rmin={Rmin:.2f}) theoretical stages (incl. reboiler) ~ {n}, feed stage from top ~ {feed_stage};  Qc ~ {Qc:.1f} MW, Qr ~ {Qr:.1f} MW")
