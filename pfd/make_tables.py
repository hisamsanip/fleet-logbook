import sys, re, html as H, xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
SRC='/root/.claude/uploads/b17c5b5f-7ccf-5f32-a761-99170dfdbfdb/2853ea2c-methanol_PFD_revised.drawio'
OUT=sys.argv[1]
# ---- reuse the stencil definitions of the PFD generator
code=open('gen2.py').read()
code=code[:code.index('STY = {k: stencil(v)')]+'STY = {k: stencil(v) for k, v in ST.items()}\n'
ns={}; sys.argv=['x','/dev/null']; exec(code,ns); STY=ns['STY']
tree=ET.parse(SRC); root=tree.getroot().find('.//root')
model=tree.getroot().find('.//mxGraphModel'); model.set('pageHeight','1700'); model.set('pageWidth','2100')
n=[0]
def nid(p): n[0]+=1; return f"{p}{n[0]}"
def q(s): return escape(s,{'"':'&quot;'})
FONT="fontFamily=Helvetica;"; BASE="html=1;whiteSpace=wrap;fillColor=#ffffff;strokeColor=#000000;strokeWidth=1;"
def add(xml): root.append(ET.fromstring(xml))
def vert(style,x,y,w,h,val='',idp='kv_'):
    add(f'<mxCell id="{nid(idp)}" value="{q(val)}" style="{style}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
def text(x,y,w,h,val,size=9,align="left",color="#000000",bold=False,valign="middle"):
    vert(f"text;html=1;whiteSpace=wrap;align={align};verticalAlign={valign};resizable=0;points=[];fontSize={size};fontColor={color};fillColor=none;strokeColor=none;{FONT}spacing=0;"+("fontStyle=1;" if bold else ""),x,y,w,h,val,'kt_')
def line(a,b,color="#000000",arrow=False,w=1):
    add(f'<mxCell id="{nid("kl_")}" style="html=1;rounded=0;endArrow={"classic" if arrow else "none"};endFill=1;endSize=5;strokeWidth={w};strokeColor={color};" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="{a[0]}" y="{a[1]}" as="sourcePoint"/><mxPoint x="{b[0]}" y="{b[1]}" as="targetPoint"/></mxGeometry></mxCell>')
def box(x,y,w,h,val,fill="#ffffff",size=9):
    vert(f"text;html=1;whiteSpace=wrap;overflow=hidden;align=left;verticalAlign=top;fillColor={fill};strokeColor=#666666;spacing=6;{FONT}fontSize={size};",x,y,w,h,val,'kb_')
RED,GRN="#C00000","#007A33"
def fail(p): return f'<b><font color="{RED if p=="FC" else GRN}">{p}</font></b>'
def table(x,y,w,h,title,header,rows,note='',size=9):
    th=''.join(f'<th style="border:1px solid #777;background:#DDE6F2;padding:2px 4px;text-align:left;">{c}</th>' for c in header)
    tr=''.join('<tr>'+''.join(f'<td style="border:1px solid #bbb;padding:2px 4px;vertical-align:top;">{c}</td>' for c in r)+'</tr>' for r in rows)
    box(x,y,w,h,f'<b style="font-size:11px;">{title}</b><br><table style="border-collapse:collapse;width:100%;font-size:{size}px;" cellpadding="2"><tr>{th}</tr>{tr}</table>'+(f'<div style="font-size:8px;margin-top:3px;">{note}</div>' if note else ''),size=size)

# ============================== KEY ==============================
KY=870; KW=2040; KH=195
box(20,KY,KW,KH,'<b style="font-size:12px;">KEY / IDENTIFICATION</b>')
TW,TH=50,14
TST=f"html=1;whiteSpace=wrap;fillColor=#ffffff;strokeColor=#000000;strokeWidth=1;fontSize=8;fontColor=#000000;spacing=0;{FONT}"
# col A: stream identification
text(40,KY+28,300,14,'<b>Stream identification</b>',9)
vert(BASE+f"shape=rhombus;fontSize=9;fontColor=#000000;spacing=0;{FONT}",44,KY+50,22,22,'n')
text(78,KY+50,300,22,'Stream number n (see Table 1)',9)
vert(TST,40,KY+82,TW,TH,'T °C'); text(98,KY+80,300,18,'Temperature (rectangle), °C',9)
vert(TST+"shape=trapezoid;perimeter=trapezoidPerimeter;fixedSize=1;size=5;",40,KY+104,TW,TH,'P bar'); text(98,KY+102,300,18,'Pressure (trapezoid), bar',9)
text(40,KY+126,380,40,'A T / P pair without a diamond marks an unnumbered line (see Table 2).<br>Tags are above/below a line, or beside a vertical line.',8)
# col B: valves
bx=430
text(bx,KY+28,300,14,'<b>Control valves</b>',9)
vert(BASE+STY['valveH'],bx+4,KY+46,26,24,'')
text(bx+40,KY+44,330,30,'Small control valve with diaphragm actuator (the original PCV-101 keeps its larger bowtie symbol)',8)
text(bx,KY+82,380,14,f'{fail("FC")} = fails closed (valve shuts on loss of air / signal)',8)
text(bx,KY+98,380,14,f'{fail("FO")} = fails open (valve opens on loss of air / signal)',8)
text(bx,KY+118,390,50,'Tag prefix: <b>FCV</b> flow, <b>LCV</b> level, <b>PCV</b> pressure, <b>TCV</b> temperature (control valve on a utility line). Number = loop number (TCV-102 is not used).',8)
# col C: lines / utilities
cx=860
text(cx,KY+28,300,14,'<b>Lines and utilities</b>',9)
line((cx+4,KY+58),(cx+54,KY+58),arrow=True); text(cx+62,KY+50,320,16,'Process line, arrow = flow direction',8)
line((cx+4,KY+80),(cx+54,KY+80),color="#A93226",arrow=True); text(cx+62,KY+72,330,16,'<font color="#A93226">Steam: HPS 41 bar, 254 °C (E-101); LPS 5 barg, 160 °C (E-103, E-105)</font>',8)
line((cx+4,KY+102),(cx+54,KY+102),color="#1F618D",arrow=True); text(cx+62,KY+94,330,16,'<font color="#1F618D">Cooling water 30 → 40 °C (E-102, E-104)</font>',8)
text(cx,KY+118,400,50,'Feed terminals: black left half (CO2, H2). Product terminals: black right half (Methanol, Water). Purge (stream 10) goes to flare / H2 recovery.',8)
# col D: equipment symbols
ex=1290
text(ex,KY+28,700,14,'<b>Equipment symbols and tag prefixes</b>',9)
def sym(kind,x,y,w,h,label):
    vert(BASE+STY[kind],x,y,w,h,''); text(x-20,y+h+2,w+40,24,label,8,align="center",valign="top")
sym('comp',ex,KY+48,40,40,'K-<br>compressor'); sym('mixer',ex+60,KY+53,70,26,'MX-<br>static mixer')
sym('reactor',ex+150,KY+40,22,70,'R-<br>reactor'); sym('vessel',ex+200,KY+40,22,70,'V-<br>flash vessel')
sym('column',ex+250,KY+40,21,70,'T-<br>column'); sym('hx',ex+300,KY+48,40,40,'E-<br>exchanger')
sym('heater',ex+360,KY+44,50,47,'E-101<br>heater'); sym('pump',ex+435,KY+47,40,41,'P-<br>pump')
sym('termL',ex+500,KY+48,40,40,'feed<br>terminal'); sym('termR',ex+560,KY+48,40,40,'product<br>terminal')
text(ex,KY+128,720,60,'Equipment tags: K-101 CO2 compressor, K-102 H2 compressor, K-103 recycle compressor, MX-101 mixer, R-101 reactor, V-101 flash vessel, T-101 column, E-101 reactor preheater, E-102 reactor cooler/condenser, E-103 column feed preheater, E-104 overhead condenser, E-105 reboiler, P-102 methanol product pump, P-103 waste water pump.',8)

# ============================== TABLE 1: stream table ==============================
T1Y=KY+KH+15
f=lambda v: f'{v:,.1f}' if v else '-'
S=[ # no, desc, from->to, T, P, phase, CO2,H2,MeOH,H2O, tot, mass, remark
 ('1','Fresh CO2','source → K-101','25','1','Vapor',399.523,0,0,0,399.523,17579.01,'Ambient supply (assumed)'),
 ('2','Fresh H2','source → K-102','25','30','Vapor',0,1200.738,0,0,1200.738,2401.48,'Supply pressure assumed'),
 ('3','Reactor feed','MX-101 → E-101','56','50','Vapor',2170.139,6944.445,0,0,9114.584,109375.01,'Fresh gas 149 / 89 °C + recycle 45 °C (energy balance); H2:CO2 = 3.2'),
 ('4','Reactor effluent','R-101 → E-102','308','50','Vapor',1779.514,5772.570,390.625,390.625,8333.334,109375.01,'Adiabatic estimate from 230 °C inlet *'),
 ('5','V-101 vapour','V-101 → purge / K-103','45','49','Vapor',1779.514,5772.570,0,0,7552.084,89843.76,'Sharp split (mass balance assumption 8)'),
 ('6','Recycle gas','K-103 → MX-101','45','50','Vapor',1770.616,5743.707,0,0,7514.323,89394.52,'99.5 % of stream 5; K-103 covers loop pressure drop'),
 ('7','V-101 liquid','V-101 → T-101','45','49','Liquid',0,0,390.625,390.625,781.250,19531.25,'Before LCV-101; CH3OH:H2O = 1:1'),
 ('8','Water (bottoms)','T-101 → P-103, product','105','1.2','Liquid',0,0,0.391,389.931,390.322,7031.27,'Boiling point at 1.2 bar; 0.18 wt% CH3OH'),
 ('9','Methanol (distillate)','T-101 → P-102, product','69','1.2','Vapor',0,0,390.234,0.694,390.928,12499.98,'T, P at T-101 top (dew point); flow = net product; 99.9 wt%'),
 ('10','Purge','V-101 gas → flare','45','49','Vapor',8.898,28.863,0,0,37.761,449.24,'0.5 % of stream 5'),
]
rows=[[a,b,c,d,e,fp]+[f(x) for x in (g,h,i,j,k)]+[f'{m:,.0f}',r] for (a,b,c,d,e,fp,g,h,i,j,k,m,r) in S]
table(20,T1Y,1330,235,'TABLE 1 - STREAM TABLE (flows from the mass balance, T and P from the PFD tags)',
      ['No.','Description','From → To','T (°C)','P (bar)','Phase','CO2 (kmol/h)','H2 (kmol/h)','CH3OH (kmol/h)','H2O (kmol/h)','Total (kmol/h)','Mass (kg/h)','Remark'],rows,
      '* At 308 °C, 50 bar and H2:CO2 = 3.2 the equilibrium CO2 conversion is only about 13 %, below the 18 % per pass used in the mass balance: the reactor needs cooling or a lower inlet temperature.')
# ============================== TABLE 2: other line conditions ==============================
rows2=[
 ['After K-101','1','149','50','4 stages, intercoolers to 45 °C, no aftercooler (calculated, η = 0.75)'],
 ['After K-102','2','89','50','1 stage, 30 → 50 bar (calculated, η = 0.75)'],
 ['Reactor inlet (E-101 out)','3','230','50','HPS 41 bar heats stream 3 (about 14 MW, estimate)'],
 ['E-102 outlet (before PCV-101)','4','45','50','Cooling water; PCV-101 then drops to 49 bar'],
 ['Column feed (after FCV-104)','7','70','1.2','Below its boiling point (77 °C, NRTL estimate); 1.2 bar = column pressure'],
]
table(1370,T1Y,690,150,'TABLE 2 - OTHER LINE CONDITIONS (tags without a stream number)',['Line','Flow as stream','T (°C)','P (bar)','Basis'],rows2)

# ============================== TABLE 3: control valve schedule ==============================
T3Y=T1Y+250
V=[
 ('FCV-101','CO2 feed, after K-101','CO2','17,579 (399.5 kmol/h)','149','50','flow','FC','Stops the CO2 feed on failure; the H2 feed stops with it, so the 3:1 ratio is kept.'),
 ('FCV-102','H2 feed, after K-102','H2','2,401 (1,200.7 kmol/h)','89','50','flow','FC','Same as FCV-101: no reactants fed without control.'),
 ('PCV-101','E-102 → V-101 (original valve)','CO2, H2, CH3OH, H2O','109,375','45','50 → 49','pressure','FO','Opens on failure so the reactor loop cannot be over-pressured by a closed valve.'),
 ('FCV-103','Purge (stream 10), V-101 gas → flare','CO2, H2','449 (37.8 kmol/h)','45','49 → flare','flow','FC','Keeps flammable H2 in the plant; over-pressure is covered by a relief valve (not drawn).'),
 ('LCV-101','V-101 bottoms → E-103 (stream 7)','CH3OH, H2O, dissolved gas','19,531','45','49 → above 1.2','level','FC','Closes so 49 bar gas cannot blow through into the column system.'),
 ('FCV-104','E-103 → T-101 feed','CH3OH, H2O','19,531','70','above 1.2 → 1.2','flow','FC','Stops feeding the column on failure (avoids flooding).'),
 ('FCV-105','Reflux to T-101','CH3OH','about 12,400 (R ≈ 1.0 estimate)','not tagged','1.2','flow','FO','Keeps reflux so the overhead temperature cannot rise.'),
 ('FCV-106','Methanol product (stream 9)','CH3OH, 0.1 wt% H2O','12,500','not tagged','1.2 → product','flow','FC','Closes to keep inventory; condensate then goes to reflux.'),
 ('LCV-102','Water product (stream 8)','H2O, 0.18 wt% CH3OH','7,031','105','1.2 → product','level','FC','Keeps the sump level and protects P-103 from running dry.'),
 ('TCV-101','HPS to E-101','Steam','about 30 t/h (14 MW, est.)','254','41 bar','temperature','FC','Stops heating on failure so the reactor feed cannot overheat.'),
 ('TCV-103','Cooling water to E-102','Water','about 2,500 t/h (29 MW, est.)','30 → 40','-','temperature','FO','Maximum cooling on failure: hot gas must not reach V-101.'),
 ('TCV-104','LPS to E-103','Steam','about 0.7 t/h (0.4 MW, est.)','160','5 barg','temperature','FC','Stops heating on failure.'),
 ('TCV-105','Cooling water to E-104','Water','about 650 t/h (7.6 MW, est.)','30 → 40','-','temperature','FO','Loss of condensation would over-pressure T-101.'),
 ('TCV-106','LPS to E-105','Steam','about 13.5 t/h (7.8 MW, est.)','160','5 barg','temperature','FC','Stops boil-up on failure (avoids column flooding / over-pressure).'),
]
rows3=[[a,b,c,d,e,fp,g,fail(h),r] for (a,b,c,d,e,fp,g,h,r) in V]
table(20,T3Y,2040,305,'TABLE 3 - CONTROL VALVE SCHEDULE',['Tag','Location / service','Fluid','Flow (kg/h)','T (°C)','P (bar)','Controls','Fail','Reason for fail position'],rows3,
      'Flows of streams 1-10 are from the mass balance. Utility flows, reflux and the E-101 / E-102 / E-104 / E-105 duties are estimates (ideal-gas heat capacities, shortcut column model): confirm by simulation. "not tagged" = no temperature is given on the PFD. TCV-102 is intentionally unused.')
tree.write(OUT,encoding='utf-8',xml_declaration=False)
print('ok',OUT)
