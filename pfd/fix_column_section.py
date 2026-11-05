import xml.etree.ElementTree as ET, html, copy, sys
SRC='/root/.claude/uploads/b17c5b5f-7ccf-5f32-a761-99170dfdbfdb/3f09e98d-methanol_PFD_revised.drawio'
OUT=sys.argv[1]
tree=ET.parse(SRC); root=tree.getroot().find('.//root')
cells={c.get('id'):c for c in root.iter('mxCell')}
def geo(i):
    g=cells[i].find('mxGeometry'); return [float(g.get(k)) for k in ('x','y','width','height')]
def setgeo(i,x=None,y=None):
    g=cells[i].find('mxGeometry')
    if x is not None: g.set('x',str(x))
    if y is not None: g.set('y',str(y))
def frac(i,pt):
    x,y,w,h=geo(i); return ((pt[0]-x)/w,(pt[1]-y)/h)
# --- remove the edges that are re-routed
for i in ['ed_49','ed_50','ed_51','ed_53','ed_54','ed_56','ed_57','ed_58','ed_61']:
    root.remove(cells.pop(i))
# --- move junctions / valve / tag
setgeo('jref',x=1860,y=484)      # reflux/product tee now AFTER P-102 -> centre (1861,485)
setgeo('jb',x=1639,y=766)        # product tee now BEFORE the reboiler -> centre (1640,767)
setgeo('fcv105',y=568)           # reflux enters the top-tray region (y=585)
setgeo('tx_83',y=546)
cells={c.get('id'):c for c in root.iter('mxCell')}
n=[900]
def eid():
    n[0]+=1; return f"fx_{n[0]}"
def edge(src,sp,tgt,tp,via=(),arrow=False):
    st=f"html=1;rounded=0;endArrow={'classic' if arrow else 'none'};endFill=1;endSize=5;strokeWidth=1;strokeColor=#000000;"
    fx,fy=frac(src,sp); st+=f"exitX={fx:.4f};exitY={fy:.4f};exitDx=0;exitDy=0;exitPerimeter=0;"
    fx,fy=frac(tgt,tp); st+=f"entryX={fx:.4f};entryY={fy:.4f};entryDx=0;entryDy=0;entryPerimeter=0;"
    pts=''.join(f'<mxPoint x="{a}" y="{b}"/>' for a,b in via)
    arr=f'<Array as="points">{pts}</Array>' if via else ''
    root.append(ET.fromstring(f'<mxCell id="{eid()}" style="{st}" edge="1" parent="1" source="{src}" target="{tgt}"><mxGeometry relative="1" as="geometry">{arr}</mxGeometry></mxCell>'))
def R(i): x,y,w,h=geo(i); return (x+w,y+h/2)
def L(i): x,y,w,h=geo(i); return (x,y+h/2)
def C(i): x,y,w,h=geo(i); return (x+w/2,y+h/2)
def pin(i): x,y,w,h=geo(i); return (x,y+26)
def pout(i): x,y,w,h=geo(i); return (x+w,y+10)
def vl(i): x,y,w,h=geo(i); return (x,y+17)
def vr(i): x,y,w,h=geo(i); return (x+w,y+17)
# --- overhead: E-104 -> P-102 -> tee -> product / reflux (reflux taken after the pump)
edge('e104',R('e104'),'p102',pin('p102'),arrow=True)
edge('p102',pout('p102'),'jref',C('jref'),via=[(1861,469)])
edge('jref',C('jref'),'fcv106',vl('fcv106'))
edge('jref',C('jref'),'fcv105',vr('fcv105'),via=[(1861,585)])
edge('fcv105',vl('fcv105'),'t101',(1550,585),arrow=True)
# --- bottoms: product tee BEFORE the reboiler; reboiler loop returns to the column
edge('s9',R('s9'),'jb',C('jb'))
edge('jb',C('jb'),'e105',L('e105'),arrow=True)
edge('e105',R('e105'),'t101',(1550,631),via=[(1757,767),(1757,631)],arrow=True)
edge('jb',C('jb'),'p103',pin('p103'),via=[(1640,850),(1780,850),(1780,767)],arrow=True)
# --- E-104 outlet tag (T on top, P below), copied from existing non-red tag cells
def clone(src_id,new_id,x,y,val):
    c=copy.deepcopy(cells[src_id]); c.set('id',new_id); c.set('value',val)
    g=c.find('mxGeometry'); g.set('x',str(x)); g.set('y',str(y)); root.append(c)
clone('T_130','fx_T1',1732,444,'60 °C'); clone('P_128','fx_P1',1732,461,'1.2 bar')
def leader(a,b):
    c=copy.deepcopy(cells['ed_127']); c.set('id',eid()); g=c.find('mxGeometry')
    for p in g.iter('mxPoint'):
        if p.get('as')=='sourcePoint': p.set('x',str(a[0])); p.set('y',str(a[1]))
        if p.get('as')=='targetPoint': p.set('x',str(b[0])); p.set('y',str(b[1]))
    root.append(c)
leader((1757,485),(1757,475)); leader((1757,461),(1757,458))
# --- notes: append a short, accurate paragraph
b=cells['bx_178']; v=html.unescape(b.get('value'))
add=("<br><b>[Column section, corrected]</b> E-104 condensate leaves at 60 °C (assumed 9 K sub-cooling): methanol vapour pressure at 60 °C is 0.85 bar (CoolProp) against 1.2 bar, "
     "leaving about 0.35 bar (≈ 4.8 m of methanol) of margin for P-102 before suction losses. Reflux is taken after P-102 (it needs pressure to return to a column at 1.2 bar) and enters at the top tray. "
     "The water product is drawn from the sump before the reboiler; E-105 only feeds the boil-up loop back to the column. P-103 pumps boiling water at 1.2 bar, so it needs static head (elevated column) for NPSH. "
     "CO2/H2 dissolved in stream 7 are not condensed by E-104: remove them upstream (degassing drum) or add a vent.")
b.set('value', v.replace('</div>','')+add if False else v+add)
g=b.find('mxGeometry'); g.set('height',str(float(g.get('height'))+45))
tree.write(OUT,encoding='utf-8',xml_declaration=False)
print("ok")
