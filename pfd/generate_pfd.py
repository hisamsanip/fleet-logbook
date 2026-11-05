#!/usr/bin/env python3
"""Revised PFD: original layout (measured from the image) + small control valves + T/P stream tags."""
import sys, zlib, base64, urllib.parse
from xml.sax.saxutils import escape

OUT = sys.argv[1]

# ------------------------------------------------------------------ stencils
def stencil(xml):
    enc = urllib.parse.quote(xml, safe="-_.!~*'()")
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    d = c.compress(enc.encode()) + c.flush()
    return "shape=stencil(" + base64.b64encode(d).decode() + ");"

def S(w, h, bg, fg=""):
    """bg = background path(s); fill+stroke is applied to it in the foreground; fg = extra foreground drawing."""
    body = f"<background>{bg}</background><foreground><fillstroke/>{fg}</foreground>"
    return f'<shape name="s" h="{h}" w="{w}" aspect="fixed" strokewidth="inherit">{body}</shape>'

ST = {}
# --- small control valve, horizontal pipe: 26 x 24, pipe centre at y=17
ST["valveH"] = S(26, 24,
    '<path><move x="0" y="10"/><line x="26" y="24"/><line x="26" y="10"/><line x="0" y="24"/><close/></path>',
    '<path><move x="13" y="17"/><line x="13" y="6"/></path><stroke/>'
    '<path><move x="6" y="6"/><arc rx="7" ry="6" x-axis-rotation="0" large-arc-flag="0" sweep-flag="1" x="20" y="6"/><close/></path><fillstroke/>')
# --- small control valve, vertical pipe: 28 x 26, pipe centre at x=21, actuator on the left
ST["valveV"] = S(28, 26,
    '<path><move x="14" y="0"/><line x="28" y="0"/><line x="14" y="26"/><line x="28" y="26"/><close/></path>',
    '<path><move x="21" y="13"/><line x="8" y="13"/></path><stroke/>'
    '<path><move x="8" y="7"/><arc rx="7" ry="6" x-axis-rotation="0" large-arc-flag="0" sweep-flag="0" x="8" y="19"/><close/></path><fillstroke/>')
# --- compressor, flow to the right (lines converge on the right)
ST["comp"] = S(56, 56, '<ellipse x="0" y="0" w="56" h="56"/>',
    '<path><move x="11" y="10"/><line x="50" y="18"/></path><stroke/><path><move x="11" y="46"/><line x="50" y="38"/></path><stroke/>')
# --- source (black left half) / sink (black right half)
ST["termL"] = S(56, 56, '<ellipse x="0" y="0" w="56" h="56"/>',
    '<path><move x="28" y="0"/><arc rx="28" ry="28" x-axis-rotation="0" large-arc-flag="0" sweep-flag="0" x="28" y="56"/><close/></path><fillcolor color="#000000"/><fillstroke/>')
ST["termR"] = S(56, 56, '<ellipse x="0" y="0" w="56" h="56"/>',
    '<path><move x="28" y="0"/><arc rx="28" ry="28" x-axis-rotation="0" large-arc-flag="0" sweep-flag="1" x="28" y="56"/><close/></path><fillcolor color="#000000"/><fillstroke/>')
# --- heat exchanger (circle + zig-zag line), 56 x 56
ZZ = '<path><move x="0" y="28"/><line x="10" y="28"/><line x="19" y="14"/><line x="37" y="42"/><line x="46" y="28"/><line x="56" y="28"/></path><stroke/>'
ST["hx"] = S(56, 56, '<ellipse x="0" y="0" w="56" h="56"/>', ZZ)
# --- heater E-101 (smaller circle d=47 + diagonal arrow), bbox 70 x 66, circle centre (34,31.5)
ST["heater"] = S(70, 66, '<ellipse x="10.5" y="8" w="47" h="47"/>',
    '<path><move x="10.5" y="31.5"/><line x="19" y="31.5"/><line x="26" y="21"/><line x="40" y="42"/><line x="47" y="31.5"/><line x="57.5" y="31.5"/></path><stroke/>'
    '<path><move x="66" y="1"/><line x="3" y="63"/></path><stroke/>'
    '<path><move x="3" y="63"/><line x="15" y="60"/></path><stroke/><path><move x="3" y="63"/><line x="6" y="51"/></path><stroke/>')
# --- vessels (dished ends, tangent line at the bottom)
def vessel(w, h, cap, extra=""):
    path = (f'<path><move x="0" y="{cap}"/><arc rx="{w/2}" ry="{cap}" x-axis-rotation="0" large-arc-flag="0" sweep-flag="1" x="{w}" y="{cap}"/>'
            f'<line x="{w}" y="{h-cap}"/><arc rx="{w/2}" ry="{cap}" x-axis-rotation="0" large-arc-flag="0" sweep-flag="1" x="0" y="{h-cap}"/><close/></path>')
    tang = f'<path><move x="0" y="{h-cap}"/><line x="{w}" y="{h-cap}"/></path><stroke/>'
    return S(w, h, path, tang + extra)
ST["vessel"] = vessel(47, 144, 12)
hatch = ""
for c in range(0, 200, 11):       # '/' hatch inside bed region y in [40,100]
    x0 = max(0, c - 100); x1 = min(47, c - 40)
    if x1 > x0 and c - 40 > 0:
        hatch += f'<path><move x="{x0}" y="{c-x0}"/><line x="{x1}" y="{c-x1}"/></path><stroke/>'
ST["reactor"] = vessel(47, 142, 12,
    '<path><move x="0" y="40"/><line x="47" y="40"/></path><stroke/><path><move x="0" y="100"/><line x="47" y="100"/></path><stroke/>' + hatch)
trays = '<dashed dashed="1"/><dashpattern pattern="3 2"/>' + "".join(
    f'<path><move x="0" y="{y}"/><line x="45" y="{y}"/></path><stroke/>' for y in range(24, 122, 9))
ST["column"] = vessel(45, 142, 12, trays)
# --- mixer with 3 saw teeth, 138 x 51
saw = ""
for i in range(3):
    x0 = 10 + i*43; x1 = x0 + 33
    saw += (f'<path><move x="{x0}" y="8"/><line x="{x1}" y="43"/></path><stroke/>'
            f'<path><move x="{x0}" y="8"/><line x="{x0}" y="22"/></path><stroke/>'
            f'<path><move x="{x1}" y="43"/><line x="{x1}" y="28"/></path><stroke/>')
ST["mixer"] = S(138, 51, '<rect x="0" y="0" w="138" h="51"/>', saw)
# --- centrifugal pump with base: 55 x 56; inlet (0,26), nozzle outlet (55,10)
ST["pump"] = S(55, 56, '<ellipse x="0" y="4" w="44" h="44"/>',
    '<path><move x="22" y="4"/><line x="22" y="1"/><line x="55" y="1"/><line x="55" y="14"/><line x="42" y="14"/></path><stroke/>'
    '<ellipse x="16" y="20" w="12" h="12"/><fillstroke/>'
    '<path><move x="4" y="56"/><line x="12" y="47"/><line x="32" y="47"/><line x="40" y="56"/><close/></path><stroke/>')
# --- bowtie of the ORIGINAL valve (unchanged), 55 x 31
ST["valveOrig"] = S(55, 31, '<path><move x="0" y="0"/><line x="55" y="31"/><line x="55" y="0"/><line x="0" y="31"/><close/></path>')

STY = {k: stencil(v) for k, v in ST.items()}

# ------------------------------------------------------------------ model helpers
cells, edges, nodes = [], [], {}
_n = [0]
def nid(p):
    _n[0] += 1
    return f"{p}{_n[0]}"
def q(s):  return escape(s, {'"': '&quot;'})
BASE = "html=1;whiteSpace=wrap;fillColor=#ffffff;strokeColor=#000000;strokeWidth=1;"
FONT = "fontFamily=Helvetica;"

def vertex(id_, x, y, w, h, style, value=""):
    nodes[id_] = (x, y, w, h)
    cells.append(f'<mxCell id="{id_}" value="{q(value)}" style="{style}" vertex="1" parent="1">'
                 f'<mxGeometry x="{x:.2f}" y="{y:.2f}" width="{w}" height="{h}" as="geometry"/></mxCell>')

def text(x, y, w, h, value, size=11, align="center", color="#000000", bold=False, valign="middle"):
    id_ = nid("tx_")
    st = (f"text;html=1;whiteSpace=wrap;align={align};verticalAlign={valign};resizable=0;points=[];fontSize={size};"
          f"fontColor={color};fillColor=none;strokeColor=none;{FONT}spacing=0;" + ("fontStyle=1;" if bold else ""))
    cells.append(f'<mxCell id="{id_}" value="{q(value)}" style="{st}" vertex="1" parent="1">'
                 f'<mxGeometry x="{x:.2f}" y="{y:.2f}" width="{w}" height="{h}" as="geometry"/></mxCell>')

def frac(id_, pt):
    x, y, w, h = nodes[id_]
    return ((pt[0] - x) / w, (pt[1] - y) / h)

def edge(src=None, sp=None, tgt=None, tp=None, via=(), arrow=False, color="#000000", w=1, fsrc=None, ftgt=None, endsize=5):
    id_ = nid("ed_")
    st = f"html=1;rounded=0;endArrow={'classic' if arrow else 'none'};endFill=1;endSize={endsize};strokeWidth={w};strokeColor={color};"
    attrs = ""
    if src:
        fx, fy = frac(src, sp); st += f"exitX={fx:.4f};exitY={fy:.4f};exitDx=0;exitDy=0;exitPerimeter=0;"; attrs += f' source="{src}"'
    if tgt:
        fx, fy = frac(tgt, tp); st += f"entryX={fx:.4f};entryY={fy:.4f};entryDx=0;entryDy=0;entryPerimeter=0;"; attrs += f' target="{tgt}"'
    g = ""
    if not src: g += f'<mxPoint x="{fsrc[0]}" y="{fsrc[1]}" as="sourcePoint"/>'
    if not tgt: g += f'<mxPoint x="{ftgt[0]}" y="{ftgt[1]}" as="targetPoint"/>'
    if via: g += '<Array as="points">' + "".join(f'<mxPoint x="{a}" y="{b}"/>' for a, b in via) + '</Array>'
    edges.append(f'<mxCell id="{id_}" style="{st}" edge="1" parent="1"{attrs}><mxGeometry relative="1" as="geometry">{g}</mxGeometry></mxCell>')

# --- equipment (placed by measured centre / top-left) ---
def at(id_, kind, cx, cy, w, h, label_style=""):
    vertex(id_, cx - w/2, cy - h/2, w, h, BASE + STY[kind] + label_style)
def P(id_, fx, fy):     # absolute point from fractional position inside node
    x, y, w, h = nodes[id_]; return (x + fx*w, y + fy*h)
def L(i): x,y,w,h = nodes[i]; return (x, y + h/2)
def R(i): x,y,w,h = nodes[i]; return (x + w, y + h/2)
def T(i): x,y,w,h = nodes[i]; return (x + w/2, y)
def B(i): x,y,w,h = nodes[i]; return (x + w/2, y + h)
def C(i): x,y,w,h = nodes[i]; return (x + w/2, y + h/2)

def diamond(id_, cx, cy, label):
    vertex(id_, cx - 11, cy - 11, 22, 22, BASE + f"shape=rhombus;fontSize=9;fontColor=#000000;spacing=0;{FONT}", str(label))
def junction(id_, cx, cy):
    vertex(id_, cx - 1, cy - 1, 2, 2, "ellipse;html=1;fillColor=none;strokeColor=none;")

# valves: small control valves
def valveH(id_, cx, py):         # pipe centre line y=py ; cell 26x24, pipe at y+17
    vertex(id_, cx - 13, py - 17, 26, 24, BASE + STY["valveH"])
def vl(i): x,y,w,h = nodes[i]; return (x, y + 17)
def vr(i): x,y,w,h = nodes[i]; return (x + w, y + 17)
def valveV(id_, px, cy):         # pipe centre line x=px ; cell 28x26, pipe at x+21
    vertex(id_, px - 21, cy - 13, 28, 26, BASE + STY["valveV"])
def vt(i): x,y,w,h = nodes[i]; return (x + 21, y)
def vb(i): x,y,w,h = nodes[i]; return (x + 21, y + h)

RED, GRN = "#C00000", "#007A33"
def vtag(tag, pos):
    col = RED if pos == "FC" else GRN
    return f'{tag}<br><b><font color="{col}">{pos}</font></b>'

# ------------------------------------------------------------------ HEADER ROW (as original)
hdr = [(143, "K-101<br>Feed Compressor<br>for CO2"), (253, "K-102<br>Feed Compressor<br>for H2"), (363, "K-103<br>Recycle<br>Compressor"),
       (474, "MX-101<br>Process Mixer"), (585, "R-101<br>Methanol Synthesis<br>Reactor"), (696, "V-101<br>Vapor-Liquid<br>Separator"),
       (817, "T-101<br>Methanol Distillation<br>Column"), (948, "E-101<br>Reactor Preheater"), (1071, "E-102<br>Reactor Condenser"),
       (1198, "E-103<br>Distillation Column<br>Feed Preheater"), (1326, "E-104<br>Overhead<br>Condenser"), (1452, "E-105<br>Reboiler"),
       (1579, "P-101<br>Distillation Column<br>Feed Pump"), (1707, "P-102<br>Methanol Product<br>Pump"), (1834, "P-103<br>Waste Water Pump")]
for cx, t in hdr:
    text(cx - 60, 8, 120, 44, t, size=9, valign="top")

# ------------------------------------------------------------------ EQUIPMENT (original positions)
YC, YH, YM = 335.5, 597, 471.5
at("src_co2", "termL", 43, YC, 56, 56);  at("src_h2", "termL", 43, YH, 56, 56)
diamond("s1", 103, YC, 1); diamond("s2", 103, YH, 2)
at("k101", "comp", 167.5, YC, 56, 56); at("k102", "comp", 167.5, YH, 56, 56)
junction("jf", 233, YM); junction("jr", 263.3, YM)
vertex("mx101", 299.5, 446, 138, 51, BASE + STY["mixer"])
diamond("s3", 480.5, YM, 3)
vertex("e101", 520, 440, 70, 66, BASE + STY["heater"])          # circle centre (554,471.5)
E101_L, E101_R = (530.5, YM), (577.5, YM)
vertex("r101", 652, 402, 47, 142, BASE + STY["reactor"])
diamond("s4", 759.5, YM, 4)
at("e102", "hx", 841, YM, 56, 56)
vertex("pcv101", 961, 456, 55, 31, BASE + STY["valveOrig"])     # ORIGINAL valve, unchanged
vertex("v101", 1092, 400, 47, 144, BASE + STY["vessel"])
# recycle / purge
at("k103", "comp", 902.7, 238, 56, 56, "flipH=1;")
junction("jp", 1115.7, 278)
diamond("s5", 1116, 334, 5); diamond("s6", 263.3, 319, 6)
# liquid train
diamond("s7", 1116, 587, 7)
at("e103", "hx", 1222.5, 647, 56, 56)
vertex("p101", 1343, 621, 55, 56, BASE + STY["pump"])            # inlet y=647
vertex("t101", 1505, 559, 45, 142, BASE + STY["column"])
# overhead
diamond("s8", 1597, 485, 8)
at("e104", "hx", 1690.5, 485, 56, 56)
junction("jref", 1758, 485)
vertex("p102", 1796, 459, 55, 56, BASE + STY["pump"])            # inlet y=485
at("snk_meoh", "termR", 1956, 485, 56, 56)
# bottoms
diamond("s9", 1597.5, 767, 9)
at("e105", "hx", 1690.5, 767, 56, 56)
junction("jb", 1758, 767)
vertex("p103", 1796, 741, 55, 56, BASE + STY["pump"])            # inlet y=767
at("snk_w", "termR", 1956, 767, 56, 56)

def pin(i): x,y,w,h = nodes[i]; return (x, y + 26)
def pout(i): x,y,w,h = nodes[i]; return (x + w, y + 10)

# ------------------------------------------------------------------ valves (new)
valveV("fcv101", 233, 378)
valveV("fcv102", 233, 556)
valveH("fcv103", 1230, 278)
valveV("lcv101", 1116, 623)
valveH("fcv104", 1478, 631)
valveH("fcv105", 1650, 600)
valveH("fcv106", 1900, 485)
valveH("lcv102", 1900, 767)

# ------------------------------------------------------------------ PIPES (as original routing, split at valves/junctions)
edge("src_co2", R("src_co2"), "s1", P("s1", 0, .5))
edge("s1", P("s1", 1, .5), "k101", L("k101"), arrow=True)
edge("k101", R("k101"), "fcv101", vt("fcv101"), via=[(233, YC)])
edge("fcv101", vb("fcv101"), "jf", C("jf"))
edge("src_h2", R("src_h2"), "s2", P("s2", 0, .5))
edge("s2", P("s2", 1, .5), "k102", L("k102"), arrow=True)
edge("k102", R("k102"), "fcv102", vb("fcv102"), via=[(233, YH)])
edge("fcv102", vt("fcv102"), "jf", C("jf"))
edge("jf", C("jf"), "jr", C("jr"))
edge("jr", C("jr"), "mx101", L("mx101"), arrow=True)
edge("mx101", R("mx101"), "s3", P("s3", 0, .5))
edge("s3", P("s3", 1, .5), "e101", E101_L, arrow=True)
edge("e101", E101_R, "r101", (652, YM), arrow=True)
edge("r101", (699, YM), "s4", P("s4", 0, .5))
edge("s4", P("s4", 1, .5), "e102", L("e102"), arrow=True)
edge("e102", R("e102"), "pcv101", (961, YM), arrow=True)
edge("pcv101", (1016, YM), "v101", (1092, YM), arrow=True)
# recycle
edge("v101", (1115.5, 400), "s5", B("s5"))
edge("s5", T("s5"), "jp", C("jp"))
edge("jp", C("jp"), "k103", R("k103"), via=[(1115.7, 238)], arrow=True)
edge("k103", L("k103"), "s6", T("s6"), via=[(263.3, 238)])
edge("s6", B("s6"), "jr", C("jr"), arrow=True)
# purge
edge("jp", C("jp"), "fcv103", vl("fcv103"))
edge("fcv103", vr("fcv103"), None, None, ftgt=(1342, 278), arrow=True)
text(1347, 268, 40, 20, "purge", size=9, align="left")
# liquid train
edge("v101", (1115.5, 544), "s7", T("s7"))
edge("s7", B("s7"), "lcv101", vt("lcv101"))
edge("lcv101", vb("lcv101"), "e103", L("e103"), via=[(1116, 647)], arrow=True)
edge("e103", R("e103"), "p101", pin("p101"), arrow=True)
edge("p101", pout("p101"), "fcv104", vl("fcv104"))
edge("fcv104", vr("fcv104"), "t101", (1505, 631), arrow=True)
# overhead
edge("t101", (1527.5, 559), "s8", P("s8", 0, .5), via=[(1527.5, 485)])
edge("s8", P("s8", 1, .5), "e104", L("e104"), arrow=True)
edge("e104", R("e104"), "jref", C("jref"))
edge("jref", C("jref"), "p102", pin("p102"), arrow=True)
edge("p102", pout("p102"), "fcv106", vl("fcv106"), via=[(1861, 469), (1861, 485)])
edge("fcv106", vr("fcv106"), "snk_meoh", L("snk_meoh"), arrow=True)
edge("jref", C("jref"), "fcv105", vr("fcv105"), via=[(1758, 600)])
edge("fcv105", vl("fcv105"), "t101", (1550, 600), arrow=True)
# bottoms
edge("t101", (1527.5, 701), "s9", P("s9", 0, .5), via=[(1527.5, 767)])
edge("s9", P("s9", 1, .5), "e105", L("e105"), arrow=True)
edge("e105", R("e105"), "jb", C("jb"))
edge("jb", C("jb"), "p103", pin("p103"), arrow=True)
edge("p103", pout("p103"), "lcv102", vl("lcv102"), via=[(1861, 751), (1861, 767)])
edge("lcv102", vr("lcv102"), "snk_w", L("snk_w"), arrow=True)
edge("jb", C("jb"), "t101", (1550, 631), via=[(1758, 631)], arrow=True)

# ------------------------------------------------------------------ original labels
def lab(cx, cy, t, w=60, size=10, bold=False): text(cx - w/2, cy - 8, w, 16, t, size=size, bold=bold)
lab(43, 373, "CO2"); lab(43, 636, "H2"); lab(167, 375, "K-101"); lab(167, 636, "K-102")
lab(362, 514, "MX-101"); lab(554, 512, "E-101"); lab(675, 560, "R-101"); lab(841, 510, "E-102")
lab(903, 273, "K-103", bold=True); lab(1143, 553, "V-101"); lab(1222, 685, "E-103"); lab(1371, 693, "P-101")
lab(1550, 713, "T-101"); lab(1690, 525, "E-104"); lab(1822, 524, "P-102"); lab(1956, 523, "Methanol", 70)
lab(1690, 805, "E-105"); lab(1822, 807, "P-103"); lab(1956, 807, "Water")

# ------------------------------------------------------------------ valve tags (new)
def tag_above(vid, tag, pos):
    x, y, w, h = nodes[vid]; text(x + w/2 - 28, y - 22, 56, 22, vtag(tag, pos), size=8)
def tag_right(vid, tag, pos, dx=4):
    x, y, w, h = nodes[vid]; text(x + w + dx, y + h/2 - 11, 50, 22, vtag(tag, pos), size=8, align="left")
tag_above("fcv103", "FCV-103", "FC"); tag_above("fcv104", "FCV-104", "FC"); tag_above("fcv105", "FCV-105", "FO")
tag_above("fcv106", "FCV-106", "FC"); tag_above("lcv102", "LCV-102", "FC")
tag_right("fcv101", "FCV-101", "FC"); tag_right("fcv102", "FCV-102", "FC"); tag_right("lcv101", "LCV-101", "FC")
# original valve: keep the bowtie as is, only add actuator (stem + dome) and tag
text(988.5 - 28, 456 - 48, 56, 22, vtag("PCV-101", "FO"), size=8)
edge(None, None, None, None, fsrc=(988.5, 471.5), ftgt=(988.5, 449), w=1)
DOME = stencil(S(16, 9, '<path><move x="0" y="9"/><arc rx="8" ry="9" x-axis-rotation="0" large-arc-flag="0" sweep-flag="1" x="16" y="9"/><close/></path>'))
vertex("pcv_dome", 988.5 - 8, 440, 16, 9, BASE + DOME)

# ------------------------------------------------------------------ utility stubs with TCV (new)
UC = {"HPS": "#A93226", "LPS": "#A93226", "CW": "#1F618D", "BFW": "#117A65"}
def stub(vid, eq, px, y0, vcy, port, label, tag, pos, utility):
    col = UC[utility]
    valveV(vid, px, vcy)
    edge(None, None, vid, vt(vid), fsrc=(px, y0), color=col)
    edge(vid, vb(vid), eq, port, color=col, arrow=True)
    text(px - 35, y0 - 16, 70, 14, label, size=8, color=col)
    tag_right(vid, tag, pos)
stub("tcv101", "e101", 554.2, 385, 418, (554.2, 448), "HPS 50 bar, 264 °C", "TCV-101", "FC", "HPS")
stub("tcv102", "r101", 675.5, 330, 366, T("r101"), "BFW (cooling)", "TCV-102", "FO", "BFW")
stub("tcv103", "e102", 841, 385, 414, T("e102"), "CW", "TCV-103", "FO", "CW")
stub("tcv104", "e103", 1222.5, 560, 589, T("e103"), "LPS", "TCV-104", "FC", "LPS")
stub("tcv105", "e104", 1690.5, 395, 425, T("e104"), "CW", "TCV-105", "FO", "CW")
stub("tcv106", "e105", 1690.5, 680, 710, T("e105"), "LPS", "TCV-106", "FC", "LPS")

# ------------------------------------------------------------------ T / P stream tags (symbols from the key)
TW, TH = 50, 14
TST = f"html=1;whiteSpace=wrap;fillColor=#ffffff;strokeColor=#000000;strokeWidth=1;fontSize=8;fontColor=#000000;spacing=0;{FONT}"
def tbox(cx, cy, val):
    vertex(nid("T_"), cx - TW/2, cy - TH/2, TW, TH, TST, val)
    return nodes_last()
def nodes_last(): return list(nodes)[-1]
def pbox(cx, cy, val):
    vertex(nid("P_"), cx - TW/2, cy - TH/2, TW, TH, TST + "shape=trapezoid;perimeter=trapezoidPerimeter;fixedSize=1;size=5;", val)
    return nodes_last()
def leader(p0, p1):
    edge(None, None, None, None, fsrc=p0, ftgt=p1, w=0.75)
def tp_above(cx, cy_line, t, p, off=10):
    """stack above a line: leader -> P trapezoid (bottom) ; T rectangle on top"""
    yp = cy_line - off - TH/2
    leader((cx, cy_line), (cx, yp + TH/2))
    pbox(cx, yp, p)
    yt = yp - TH - 3
    leader((cx, yp - TH/2), (cx, yt + TH/2))
    tbox(cx, yt, t)
def tp_below(cx, cy_line, t, p, off=10):
    yt = cy_line + off + TH/2
    leader((cx, cy_line), (cx, yt - TH/2))
    tbox(cx, yt, t)
    yp = yt + TH + 3
    leader((cx, yt + TH/2), (cx, yp - TH/2))
    pbox(cx, yp, p)
def tp_side(x_line, cy, t, p, side=1, off=14, start=0):
    """stack beside a vertical line at x_line (side=+1 right, -1 left)"""
    xb = x_line + side * (off + TW/2)
    leader((x_line + side*start, cy), (x_line + side*off, cy))
    leader((x_line + side*off, cy - TH/2 - 1.5), (x_line + side*off, cy + TH/2 + 1.5))
    tbox(xb, cy - TH/2 - 1.5, t)
    pbox(xb, cy + TH/2 + 1.5, p)

# numbered streams: T rectangle on top, P trapezoid below
tp_above(103, YC - 11, "25 °C", "1 bar", off=6)
tp_above(103, YH - 11, "25 °C", "1 bar", off=6)
tp_above(480.5, YM - 11, "45 °C", "50 bar", off=6)
tp_above(759.5, YM - 11, "250 °C", "50 bar", off=6)
tp_side(1116.7, 334, "45 °C", "50 bar", side=1, off=24, start=11)
tp_side(263.3, 319, "45 °C", "50 bar", side=1, off=24, start=11)
tp_side(1116.7, 587, "45 °C", "50 bar", side=1, off=24, start=11)
tp_above(1597, 485 - 11, "69 °C", "1.2 bar", off=6)
tp_below(1597.5, 767 + 11, "105 °C", "1.2 bar", off=6)
# unnumbered key points
tp_side(233, 425, "40 °C", "50 bar", side=-1)            # K-101 discharge (after last cooler)
tp_side(233, 512, "40 °C", "50 bar", side=-1)            # K-102 discharge
tp_above(615, YM, "250 °C", "50 bar", off=10)            # reactor inlet = E-101 outlet
tp_above(915, YM, "45 °C", "50 bar", off=10)             # E-102 outlet
tp_above(1417, 631, "70 °C", "1.2 bar", off=14)          # column feed

# ------------------------------------------------------------------ KEY + TABLES (below the PFD)
def box(x, y, w, h, html, fill="#ffffff", stroke="#888888", size=10, valign="top", align="left"):
    cells.append(f'<mxCell id="{nid("bx_")}" value="{q(html)}" style="text;html=1;whiteSpace=wrap;overflow=hidden;align={align};verticalAlign={valign};'
                 f'fillColor={fill};strokeColor={stroke};spacing=6;{FONT}fontSize={size};" vertex="1" parent="1">'
                 f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')

KY = 860
box(20, KY, 860, 120,
    "<b>KEY</b>", size=10)
# key symbols
diamond("k_d", 52, KY + 38, "n"); text(70, KY + 29, 330, 18, "Stream identification (stream number n)", size=9, align="left")
vertex("k_t", 41, KY + 54, TW, TH, TST, "T °C"); text(98, KY + 52, 300, 18, "Temperature (rectangle)", size=9, align="left")
vertex("k_p", 41, KY + 76, TW, TH, TST + "shape=trapezoid;perimeter=trapezoidPerimeter;fixedSize=1;size=5;", "P bar"); text(98, KY + 74, 300, 18, "Pressure (trapezoid)", size=9, align="left")
valveH("k_v", 430, KY + 52)
text(450, KY + 22, 420, 90,
     "Small control valve with diaphragm actuator. <b><font color='#C00000'>FC</font></b> = fails closed, <b><font color='#007A33'>FO</font></b> = fails open. "
     "FCV flow, PCV pressure, LCV level, TCV temperature.<br>"
     "Utility lines: <font color='#A93226'>steam (HPS 50 bar, 264 °C; LPS 5 barg, 160 °C)</font>, <font color='#1F618D'>cooling water 30 → 40 °C</font>, "
     "<font color='#117A65'>boiler feed water</font>.<br>Tags without a stream number mark unnumbered lines (design basis, to be confirmed by simulation).",
     size=9, align="left", valign="top")

def table(x, y, w, h, title, header, rows, size=9):
    th = "".join(f'<th style="border:1px solid #888;background:#DDE6F2;padding:2px 4px;text-align:left;">{c}</th>' for c in header)
    tr = "".join("<tr>" + "".join(f'<td style="border:1px solid #bbb;padding:2px 4px;vertical-align:top;">{c}</td>' for c in r) + "</tr>" for r in rows)
    html = f'<b style="font-size:11px;">{title}</b><br><table style="border-collapse:collapse;width:100%;font-size:{size}px;" cellpadding="2"><tr>{th}</tr>{tr}</table>'
    box(x, y, w, h, html, size=size)

streams = [
 ("1", "CO2 feed", "25", "1", "Vapor", "CO2", "Ambient supply (assumed)"),
 ("2", "H2 feed", "25", "1", "Vapor", "H2", "Ambient supply (assumed; change if your H2 is pressurised)"),
 ("3", "MX-101 outlet", "45", "50", "Vapor", "H2, CO2, CO", "Fresh gas 40 °C + recycle 45 °C; E-101 heats it to 250 °C"),
 ("4", "R-101 effluent", "250", "50", "Vapor", "H2, CO2, CH3OH, H2O, CO", "Reactor cooled (BFW) to hold 250 °C; loop pressure drop neglected"),
 ("5", "V-101 overhead", "45", "50", "Vapor", "H2, CO2, CO", "E-102 cools with cooling water (45 °C is above the 40 °C limit)"),
 ("6", "Recycle (K-103 out)", "45", "50", "Vapor", "H2, CO2, CO", "Pressure drop neglected, so same as stream 5"),
 ("7", "V-101 bottoms", "45", "50", "Liquid", "CH3OH, H2O, dissolved gas", "Throttled by LCV-101 to the column pressure"),
 ("8", "T-101 overhead", "69", "1.2", "Vapor", "CH3OH", "Boiling point of CH3OH at 1.2 bar"),
 ("9", "T-101 bottoms", "105", "1.2", "Liquid", "H2O", "Boiling point of water at 1.2 bar"),
]
table(20, KY + 135, 860, 195, "STREAM TABLE (design basis)", ["#", "Stream", "T (°C)", "P (bar)", "Phase", "Main components", "Remark"], streams)

valves = [
 ("FCV-101", "CO2 feed (K-101 discharge)", "FC", "Stop feeding reactants on air failure."),
 ("FCV-102", "H2 feed (K-102 discharge)", "FC", "Same; both feeds close together (H2:CO2 ratio kept)."),
 ("PCV-101", "Reactor loop → V-101 (original valve)", "FO", "Loop pressure control; must not over-pressure the loop."),
 ("FCV-103", "Purge from V-101", "FC", "Keep H2/flammable gas in; PSV covers over-pressure."),
 ("LCV-101", "V-101 liquid → column (50 → 1.2 bar)", "FC", "Throttles the liquid to column pressure; closes so 50 bar gas cannot blow into the column."),
 ("FCV-104", "T-101 feed", "FC", "Stop feeding the column on failure (avoid flooding)."),
 ("FCV-105", "T-101 reflux", "FO", "Keep reflux so overhead temperature cannot rise."),
 ("FCV-106", "Methanol product", "FC", "Keep inventory; reflux takes the whole condensate."),
 ("LCV-102", "T-101 bottoms water", "FC", "Keep sump level; protect P-103."),
 ("TCV-101", "E-101 HPS", "FC", "Loss of control must not overheat the catalyst feed."),
 ("TCV-102", "R-101 BFW cooling", "FO", "Exothermic reactor: maximum cooling on failure (no runaway)."),
 ("TCV-103", "E-102 cooling water", "FO", "Loss of cooling must not send hot gas to V-101."),
 ("TCV-104", "E-103 LPS", "FC", "Stop heating on failure."),
 ("TCV-105", "E-104 cooling water", "FO", "Loss of condensation would over-pressure T-101."),
 ("TCV-106", "E-105 LPS", "FC", "Stop heating on failure."),
]
vrows = [(a, b, f'<b><font color="{RED if c == "FC" else GRN}">{c}</font></b>', d) for a, b, c, d in valves]
table(900, KY, 1080, 290, "CONTROL VALVE SCHEDULE", ["Tag", "Service", "Fail", "Reason"], vrows)

notes = (
 "<b style='font-size:11px;'>DESIGN BASIS (Chapter 5 heuristics + literature)</b><br>"
 "<b>Heuristics:</b> prefer 1 &lt; P &lt; 10 bar and 40 &lt; T &lt; 260 °C; T &gt; 250 °C needs a fired heater / molten salt; T &gt; 400 °C special MoC; T &lt; 40 °C needs refrigeration "
 "(use cooling water 30 → 40 °C); P &gt; 10 bar needs thick walls; compressor Pout/Pin &gt; 3 → multistage with intercoolers; a valve with large ΔP is acceptable for control or when a liquid is throttled (Table 6.4).<br>"
 "<b>Pressure:</b> the whole synthesis loop (streams 3-7, R-101, V-101) is taken at 50 bar; pressure drops in exchangers, reactor, valve and piping are neglected at PFD level (a simulation gives them). "
 "T-101 is at 1.2 bar (just above atmospheric: inside 1-10 bar, no vacuum), tray pressure drop neglected. The only large pressure reduction is at LCV-101 (50 → 1.2 bar), because the liquid must enter the column at column pressure.<br>"
 "<b>R-101 250 °C, 50 bar</b> (special concern: high pressure). CO2 + 3H2 → CH3OH + H2O, 4 → 2 mol, exothermic (≈ -49.5 kJ/mol): pressure raises equilibrium conversion and rate (Table 6.2); "
 "Cu/ZnO/Al2O3 works at about 200-300 °C. The bed is cooled with BFW to stay at 250 °C, so the feed is heated directly to 250 °C.<br>"
 "<b>E-101:</b> 45 → 250 °C with HPS at 50 bar (264 °C, top of the 250-265 °C range in the notes): approach 14 °C, LMTD ≈ 74 °C. 250 °C is the highest temperature HPS can give; above it a fired heater would be needed (about 10 times the cost of an exchanger, slide 8).<br>"
 "<b>K-101, K-102:</b> 1 → 50 bar, ratio 50 &gt; 3, so 4 stages (ratio 2.66 each) with intercoolers back to 40 °C. Without intercooling a single stage would reach about 445 °C (CO2) and 657 °C (H2). "
 "Last-stage discharge without a final cooler: about 143 °C (CO2) and 177 °C (H2) (adiabatic, isentropic efficiency 0.75); the diagram assumes the last stage is also cooled to 40 °C.<br>"
 "<b>E-102 / V-101:</b> cooled to 45 °C with cooling water, no refrigeration. <b>T-101:</b> condenser on cooling water, reboiler on LPS. Reflux is taken before P-102, as in the original PFD. "
 "The liquid from V-101 contains dissolved CO2/H2 that will flash at LCV-101: consider a degassing drum.<br>"
 "<b>References:</b> (1) CPE604 Chapter 5 notes (Turton et al., Analysis, Synthesis and Design of Chemical Processes, 4th ed., Ch. 6; slide 19 compressor example). (2) Van-Dal and Bouallou, J. Cleaner Prod. 57 (2013) 38-45. "
 "(3) Cu/ZnO/Al2O3 experiments at 200-230 °C, 50-80 bar (UCM, PSA reactor for methanol-enhanced production via CO2 hydrogenation). (4) US 9,133,074: 150-300 °C, preferably 200-300 °C. "
 "LPS 5 barg / 160 °C typical (Turton Table 8.3).<br>"
 "<font color='#C00000'><b>Values not taken from the lecture notes are assumptions: confirm with a simulation and equipment sizing.</b></font>"
)
box(20, KY + 345, 1960, 150, notes, fill="#FFFBE6", size=9)

# ------------------------------------------------------------------ OUTPUT
xml = ('<mxfile host="app.diagrams.net" version="24.0.0"><diagram id="pfd1" name="PFD - Methanol from CO2">'
       '<mxGraphModel dx="1600" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" '
       'pageScale="1" pageWidth="2100" pageHeight="1400" math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
       + "".join(cells) + "".join(edges) + '</root></mxGraphModel></diagram></mxfile>')
open(OUT, "w", encoding="utf-8").write(xml)
print("wrote", OUT, len(xml), len(cells), "vertices", len(edges), "edges")
