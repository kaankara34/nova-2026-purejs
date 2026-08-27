#!/usr/bin/env python3
"""Rebuild the engineering visuals of sections 06-12 (approved copy untouched)."""
import pathlib
import re

P = pathlib.Path('/app/frontend/construction.html')
src = P.read_text(encoding='utf-8')
before = src

D = '&mdash;'
NTS = 'CONCEPTUAL ' + D + ' NOT TO SCALE'

# =====================================================================
# 06 EXECUTION CONTROL — verification points along the construction sequence
# =====================================================================
cells = [(20, 'DOCUMENTATION'), (215, 'PRE-POUR'), (410, 'CONCRETE EXECUTION'),
         (605, 'EARLY AGE'), (800, 'ENCLOSURE'), (995, 'COMPLETION')]
g = []
x = 20
g.append(f'<g data-elstate="0"><path class="hid" d="M{x} 34 H{x+150} V150 H{x} Z" />'
         f'<path class="ln-2" d="M{x+14} 52 H{x+120} M{x+14} 70 H{x+96} M{x+14} 88 H{x+110}" />'
         f'<path class="ln" d="M{x+90} 118 H{x+150} V150 H{x+90} Z" />'
         f'<text x="{x}" y="176">DOCUMENTATION</text></g>')
x = 215
g.append(f'<g data-elstate="1"><path class="fillg" d="M{x} 34 H{x+16} V150 H{x} Z" />'
         f'<path class="fillg" d="M{x+134} 34 H{x+150} V150 H{x+134} Z" />'
         f'<path class="hot" d="M{x+30} 44 V140 M{x+58} 44 V140 M{x+92} 44 V140 M{x+120} 44 V140" />'
         f'<path class="hot" d="M{x+30} 56 H{x+120} M{x+30} 92 H{x+120} M{x+30} 128 H{x+120}" />'
         f'<path class="dim" d="M{x+16} 158 H{x+30} M{x+16} 152 v12 M{x+30} 152 v12" />'
         f'<text x="{x}" y="176">PRE-POUR</text></g>')
x = 410
g.append(f'<g data-elstate="2"><path class="fillg" d="M{x} 34 H{x+16} V150 H{x} Z" />'
         f'<path class="fillg" d="M{x+134} 34 H{x+150} V150 H{x+134} Z" />'
         f'<path class="ln-2" d="M{x+16} 150 H{x+134} M{x+16} 122 H{x+134} M{x+16} 96 H{x+134}" />'
         f'<path class="hot" d="M{x+75} 18 V44 m0 0 l-7 -11 m7 11 l7 -11" />'
         f'<text x="{x}" y="176">CONCRETE EXECUTION</text></g>')
x = 605
g.append(f'<g data-elstate="3"><path class="fillg" d="M{x} 46 H{x+150} V150 H{x} Z" />'
         f'<path class="hid" d="M{x} 36 H{x+150}" />'
         f'<path class="hot" d="M{x+30} 30 v-12 M{x+75} 30 v-12 M{x+120} 30 v-12" />'
         f'<text x="{x}" y="176">EARLY AGE</text></g>')
x = 800
g.append(f'<g data-elstate="4"><path class="fillg" d="M{x+26} 34 H{x+150} V150 H{x+26} Z" />'
         f'<path class="hot" d="M{x+18} 34 V150" /><path class="ln-2" d="M{x+8} 34 V150" />'
         f'<path class="ln-2" d="M{x+8} 52 l10 12 M{x+8} 82 l10 12 M{x+8} 112 l10 12" />'
         f'<path class="warn" d="M{x+60} 88 h34" /><circle class="warn" cx="{x+77}" cy="88" r="7" />'
         f'<text x="{x}" y="176">ENCLOSURE</text></g>')
x = 995
g.append(f'<g data-elstate="5"><path class="fillg" d="M{x} 34 H{x+150} V150 H{x} Z" />'
         f'<path class="dim" d="M{x} 162 H{x+150} M{x} 156 v12 M{x+150} 156 v12" />'
         f'<path class="dim" d="M{x-14} 34 V150 M{x-20} 34 h12 M{x-20} 150 h12" />'
         f'<text x="{x}" y="176">COMPLETION</text></g>')

insp_svg = ('<div class="cx-insp-elem"><svg class="cx-dwg" viewBox="0 0 1200 200" role="img" '
            'aria-label="Verification points along the construction sequence, conceptual" '
            'preserveAspectRatio="xMidYMid meet">'
            '<path class="hid" d="M20 26 H1145" />'
            '<text x="20" y="18">VERIFICATION BEFORE WORK IS CONCEALED ' + D + ' CONCEPTUAL SEQUENCE</text>'
            + ''.join(g) + '</svg></div>')

a = src.index('<div class="cx-insp-elem">')
b = src.index('</div>', src.index('</svg>', a)) + 6
src = src[:a] + insp_svg + src[b:]

# element-state labels follow the same six verification points
states = ['Documentation', 'Pre-pour', 'Concrete execution', 'Early age', 'Enclosure', 'Completion']
new_states = ''.join('<div class="cx-insp-state" data-testid="cx-elstate-%d">%s</div>' % (i + 1, s)
                     for i, s in enumerate(states))
a = src.index('<div class="cx-insp-states"')
b = src.index('</div></div>', a) + len('</div></div>')
src = src[:a] + ('<div class="cx-insp-states" data-testid="cx-element-states">%s</div>' % new_states) + src[b:]

# =====================================================================
# 07 WATERPROOFING — continuous functional boundary through a conceptual section
# =====================================================================
wp = f'''<div class="cx-wp-viz"><svg class="cx-dwg" viewBox="0 0 800 660" role="img" aria-label="Continuous waterproofing boundary through a conceptual building section" preserveAspectRatio="xMidYMid meet">
<path class="ln" d="M258 104 V520" />
<path class="ln-2" d="M282 104 V520" />
<path class="ln" d="M258 520 H660 V546 H258 Z" />
<path class="ln-2" d="M282 222 H660 M282 336 H660 M282 440 H660" />
<path class="ln" d="M176 210 H258 M176 210 V196" />
<path class="ln-2" d="M176 222 H258" />
<path class="ln" d="M258 104 H660 V128 H258" />
<path class="ln" d="M240 104 V64 H262 V104" />
<path class="hid" d="M40 336 H258" />
<path class="ln-2" d="M60 352 l-12 16 M96 352 l-12 16 M132 352 l-12 16 M168 352 l-12 16 M204 352 l-12 16 M240 352 l-12 16 M60 402 l-12 16 M96 402 l-12 16 M132 402 l-12 16 M168 402 l-12 16 M204 402 l-12 16 M240 402 l-12 16 M60 452 l-12 16 M96 452 l-12 16 M132 452 l-12 16 M168 452 l-12 16 M204 452 l-12 16 M240 452 l-12 16 M60 502 l-12 16 M96 502 l-12 16 M132 502 l-12 16 M168 502 l-12 16 M204 502 l-12 16 M240 502 l-12 16" />
<path class="ln-2" d="M120 386 H228 m0 0 l-11 -6 m11 6 l-11 6 M120 446 H228 m0 0 l-11 -6 m11 6 l-11 6 M120 496 H228 m0 0 l-11 -6 m11 6 l-11 6" />
<text x="44" y="330">WATER EXPOSURE {D} PROJECT SPECIFIC</text>
<path class="hot" d="M214 546 v22 h-18 l18 18 18 -18 h-18" />
<text x="120" y="600">DRAINAGE / WATERPROOFING RESPONSE</text>
<path class="cx-trace" id="cxTrace" pathLength="1" d="M700 578 H240 V222 H166 V196 H240 V104 H230 V54 H272 V128 H700" />
<g id="cxTraceGap" style="opacity:0"><circle class="warn" cx="240" cy="520" r="13" /><path class="warn" d="M232 512 l16 16 M248 512 l-16 16" /></g>
<circle class="ln" cx="240" cy="520" r="5" /><text x="300" y="512">FOUNDATION / WALL JUNCTION</text>
<text x="300" y="566">FOUNDATION</text>
<path class="hid" d="M240 440 h44" /><text x="300" y="436">CONSTRUCTION JOINT</text>
<circle class="ln" cx="240" cy="392" r="6" /><text x="300" y="388">PENETRATION</text>
<text x="300" y="330">ABOVE-GRADE TRANSITION</text>
<text x="300" y="474">BASEMENT WALL / BELOW-GRADE ZONE</text>
<text x="40" y="190">BALCONY / TERRACE</text>
<text x="40" y="240">UPSTAND / THRESHOLD</text>
<circle class="ln" cx="251" cy="54" r="5" /><text x="300" y="50">TERMINATION</text>
<circle class="ln" cx="600" cy="128" r="6" /><path class="ln-2" d="M600 128 V152" />
<text x="470" y="176">DRAINAGE POINT</text>
<text x="300" y="98">ROOF</text>
<text x="40" y="628">FUNCTIONAL CONTINUITY OF THE WATERPROOFING SYSTEM {D} NOT NECESSARILY A SINGLE MATERIAL</text>
<text x="40" y="648">{NTS} {D} SYSTEM SELECTION AND DETAILING PROJECT SPECIFIC</text>
</svg></div>'''

a = src.index('<div class="cx-wp-viz">')
b = src.index('</div>', src.index('</svg>', a)) + 6
src = src[:a] + wp + src[b:]

# =====================================================================
# 08 ENVELOPE — control layers + junctions + thermal continuity
# =====================================================================
bands = [(150, 34, 'WEATHER'), (184, 74, 'THERMAL'), (258, 16, 'AIR'),
         (274, 22, 'VAPOUR*'), (296, 62, 'STRUCTURE'), (358, 26, 'FINISH')]
bs = []
for i, (bx, bw, nm) in enumerate(bands):
    y = 300 if i % 2 == 0 else 320
    bs.append(f'<rect class="fillg" x="{bx}" y="96" width="{bw}" height="180" />'
              f'<path class="ln-2" d="M{bx + bw/2:.0f} 96 V276" />'
              f'<path class="dim" pathLength="1" d="M{bx} 286 H{bx+bw} M{bx} 280 v12 M{bx+bw} 280 v12" />'
              f'<text class="t-dim" x="{bx}" y="{y}">{nm}</text>')

env = f'''<div class="cx-det-fig" data-draw data-start="top 82%" data-end="bottom 55%">
<svg class="cx-dwg" viewBox="0 0 700 640" role="img" aria-label="Conceptual envelope control layers and junctions" preserveAspectRatio="xMidYMid meet">
<text x="60" y="40">CONTROL LAYERS {D} CONCEPTUAL; SEQUENCE PROJECT SPECIFIC</text>
<path class="hid" d="M60 96 H660 M60 276 H660" />
{''.join(bs)}
<text x="60" y="352">* MOISTURE / VAPOUR CONTROL AS APPLICABLE</text>
<text x="440" y="188">EXTERIOR</text><text x="440" y="212">INTERIOR</text>
<path class="hid" d="M420 96 H660 M420 276 H660" />
<path class="ln-2" d="M470 150 H520 m0 0 l-9 -5 m9 5 l-9 5" /><text x="530" y="154">HEAT / MOISTURE / AIR</text>
<text x="60" y="404">CRITICAL JUNCTIONS {D} CONTINUITY OF THE CONTROL LAYERS</text>
<path class="ln" d="M150 424 V616" /><path class="ln-2" d="M176 424 V616" />
<path class="ln" d="M176 470 H430 M176 530 H430" />
<path class="ln" d="M96 470 H150 M96 470 V456" />
<path class="ln" d="M150 424 H430 V440 H176" />
<path class="ln" d="M134 424 V400 H162 V424" />
<path class="ln" d="M176 586 H430" /><path class="hid" d="M96 616 H430" />
<path class="ln-2" d="M240 530 H300 V470" />
<circle class="ln" cx="163" cy="470" r="6" /><text x="446" y="466">SLAB EDGE</text>
<circle class="ln" cx="120" cy="470" r="6" /><text x="20" y="450">BALCONY</text>
<circle class="ln" cx="163" cy="530" r="6" /><text x="446" y="526">WINDOW PERIMETER</text>
<circle class="ln" cx="148" cy="412" r="6" /><text x="446" y="418">PARAPET / ROOF TRANSITION</text>
<circle class="ln" cx="163" cy="586" r="6" /><text x="446" y="582">FOUNDATION / FA&Ccedil;ADE</text>
<circle class="ln" cx="300" cy="500" r="6" /><text x="446" y="614">SERVICE PENETRATION</text>
<path class="hot" d="M163 400 V424 V470 V530 V586 V616" />
<text x="20" y="392">THERMAL CONTINUITY</text>
<text x="60" y="636">{NTS} {D} PERFORMANCE VALUES DEFINED BY PROJECT DOCUMENTATION</text>
</svg>
<div class="cx-det-scale"><span class="cx-lbl">Macro detail</span><span class="cx-lbl">Layer sequence project specific</span></div>
</div>'''

a = src.index('<div class="cx-det-fig"')
b = src.index('\n        <div class="cx-layerlist">')
src = src[:a] + env + src[b:]

# =====================================================================
# 09 ACOUSTICS — transmission-path schematics (source -> path -> assembly -> receiver)
# =====================================================================
def plot(slug, tid, idx, title, body):
    return (f'<div class="cx-plot" data-plot="{slug}" data-testid="{tid}">'
            f'<span class="cx-lbl">{idx} &middot; {title}</span>'
            f'<svg class="cx-dwg cx-tp" viewBox="0 0 480 190" role="img" aria-label="{title} transmission path, conceptual" preserveAspectRatio="xMidYMid meet">{body}</svg></div>')

rooms = ('<path class="ln" d="M30 40 H220 V150 H30 Z" /><path class="ln" d="M260 40 H450 V150 H260 Z" />'
         '<path class="fillg" d="M220 40 H260 V150 H220 Z" />')
plots = ''.join([
    plot('airborne', 'cx-plot-airborne', '01', 'Airborne sound',
         rooms +
         '<circle class="hot" cx="80" cy="95" r="7" /><path class="hot" d="M96 95 H214 m0 0 l-10 -6 m10 6 l-10 6" />'
         '<path class="cx-tp-p" d="M262 95 H438 m0 0 l-10 -6 m10 6 l-10 6" />'
         '<text x="30" y="30">SOURCE</text><text x="196" y="30">ASSEMBLY</text><text x="380" y="30">RECEIVER</text>'
         '<text x="30" y="176">AIRBORNE PATH THROUGH THE SEPARATING ASSEMBLY</text>'),
    plot('impact', 'cx-plot-impact', '02', 'Impact sound',
         '<path class="ln" d="M30 30 H450 V86 H30 Z" /><path class="ln" d="M30 86 H450 V160 H30 Z" />'
         '<path class="fillg" d="M30 76 H450 V96 H30 Z" />'
         '<path class="hot" d="M150 20 V66 m0 0 l-7 -11 m7 11 l7 -11" /><circle class="hot" cx="150" cy="72" r="5" />'
         '<path class="cx-tp-p" d="M150 96 V140 m0 0 l-6 -10 m6 10 l6 -10" /><path class="cx-tp-p" d="M150 86 H330 V132" />'
         '<text x="30" y="18">IMPACT ON FLOOR</text><text x="330" y="70">FLOOR ASSEMBLY / STRUCTURE</text>'
         '<text x="30" y="182">RECEIVING SPACE BELOW AND ADJOINING</text>'),
    plot('flanking', 'cx-plot-flanking', '03', 'Flanking transmission',
         rooms +
         '<path class="ln" d="M30 150 H450" /><path class="fillg" d="M30 150 H450 V166 H30 Z" />'
         '<circle class="hot" cx="80" cy="90" r="7" />'
         '<path class="cx-tp-p" d="M80 104 V158 H400 V104" />'
         '<path class="hid" d="M96 90 H214" />'
         '<text x="30" y="30">SOURCE</text><text x="196" y="30">SEPARATING ELEMENT</text><text x="380" y="30">RECEIVER</text>'
         '<text x="30" y="186">FLANKING PATH THROUGH CONNECTED CONSTRUCTION</text>'),
    plot('structure', 'cx-plot-structure', '04', 'Structure-borne vibration',
         '<path class="ln" d="M30 46 H450 V62 H30 Z" /><path class="ln" d="M30 138 H450 V154 H30 Z" />'
         '<path class="ln" d="M120 62 V138 M360 62 V138" />'
         '<path class="fillg" d="M84 22 H156 V46 H84 Z" />'
         '<path class="hot" d="M120 46 V62" />'
         '<path class="cx-tp-p" d="M120 62 V138 H360 V70" />'
         '<path class="cx-tp-p" d="M360 70 H420 m0 0 l-10 -5 m10 5 l-10 5" />'
         '<text x="84" y="16">EXCITATION AT SUPPORT</text><text x="30" y="106">STRUCTURAL PATH</text>'
         '<text x="330" y="106">RADIATED IN RECEIVER</text>'
         '<text x="30" y="182">VIBRATION PROPAGATING THROUGH STRUCTURAL ELEMENTS</text>'),
    plot('service', 'cx-plot-service', '05', 'Building-services noise',
         '<path class="ln" d="M30 40 H190 V150 H30 Z" /><path class="fillg" d="M190 40 H250 V150 H190 Z" />'
         '<path class="ln" d="M250 40 H450 V150 H250 Z" />'
         '<path class="hot" d="M212 40 V150 M228 40 V150" />'
         '<circle class="hot" cx="220" cy="70" r="8" />'
         '<path class="cx-tp-p" d="M212 96 H60 m0 0 l10 -5 m-10 5 l10 5" />'
         '<path class="cx-tp-p" d="M228 120 H430 m0 0 l-10 -5 m10 5 l-10 5" />'
         '<text x="180" y="30">SHAFT / RISER</text><text x="30" y="30">OCCUPIED SPACE</text>'
         '<text x="330" y="30">OCCUPIED SPACE</text>'
         '<text x="30" y="176">AIRBORNE AND STRUCTURE-BORNE PATHS FROM EQUIPMENT AND PIPEWORK</text>'),
])
plots = ('<div class="cx-plots" style="margin-top:clamp(26px,4vh,52px)">' + plots +
         '</div><p class="cx-lbl" style="margin-top:14px">SOURCE ' + D + ' TRANSMISSION PATH ' + D +
         ' ASSEMBLY / JUNCTION ' + D + ' RECEIVER &middot; ' + NTS + '</p>')

a = src.index('<div class="cx-plots"')
b = src.index('</div></div>', a) + len('</div></div>')
src = src[:a] + plots + src[b:]

# =====================================================================
# 10 MEP — coordinated shaft zone, engineered openings, compartmentation
# =====================================================================
mep = f'''<div class="cx-mep-viz">
          <div class="cx-mep-tabs" data-testid="cx-mep-tabs"><button class="cx-mep-tab" data-testid="cx-mep-tab-structure">Structure</button><button class="cx-mep-tab" data-testid="cx-mep-tab-architecture">Architecture</button><button class="cx-mep-tab" data-testid="cx-mep-tab-hvac">HVAC</button><button class="cx-mep-tab" data-testid="cx-mep-tab-electrical">Electrical</button><button class="cx-mep-tab" data-testid="cx-mep-tab-water">Water</button><button class="cx-mep-tab" data-testid="cx-mep-tab-drainage">Drainage</button><button class="cx-mep-tab" data-testid="cx-mep-tab-fire">Fire &amp; life safety</button></div>
          <svg class="cx-dwg" viewBox="0 0 680 560" role="img" aria-label="Conceptual services coordination around a coordinated shaft zone" preserveAspectRatio="xMidYMid meet">
<text x="110" y="26">COORDINATION MODEL {D} COORDINATED SHAFT ZONE AND HORIZONTAL DISTRIBUTION</text>
<g class="cx-mep-layer is-base" data-testid="cx-mep-layer-structure"><path class="ln" d="M110 40 H570 V500 H110 Z" /><path class="ln" d="M110 156 H570 M110 272 H570 M110 388 H570" /><path class="fillg" d="M110 40 H140 V500 H110 Z" /><path class="fillg" d="M540 40 H570 V500 H540 Z" /><text x="110" y="524">STRUCTURE {D} COLUMNS, SLABS AND BEAMS; NO UNPLANNED PENETRATIONS</text></g>
<g class="cx-mep-layer" data-testid="cx-mep-layer-architecture"><path class="ln" d="M156 56 H300 V140 H156 Z M380 56 H524 V140 H380 Z M156 172 H300 V256 H156 Z M380 172 H524 V256 H380 Z M156 288 H300 V372 H156 Z M380 288 H524 V372 H380 Z M156 404 H524 V484 H156 Z" /><text x="110" y="524">ARCHITECTURE {D} OCCUPIED SPACES, ACCESS AND MAINTENANCE ZONES</text></g>
<path class="hid" d="M316 40 V500 M364 40 V500" /><text x="300" y="34">COORDINATED SHAFT ZONE</text>
<g class="cx-mep-layer" data-testid="cx-mep-layer-hvac"><path class="ln" d="M324 490 V60" /><path class="ln" d="M324 120 H500 M324 236 H500 M324 352 H500" /><path class="ln-2" d="M364 120 H380 V104 H364 Z M364 236 H380 V220 H364 Z" /><text x="110" y="524">HVAC {D} DUCT ROUTES WITHIN THE COORDINATED ZONE AND BELOW SLAB SOFFIT</text></g>
<g class="cx-mep-layer" data-testid="cx-mep-layer-electrical"><path class="ln" d="M334 490 V60" /><path class="ln" d="M334 138 H180 M334 254 H180 M334 370 H180" /><path class="ln-2" d="M316 138 H300 V122 H316 Z" /><text x="110" y="524">ELECTRICAL {D} CONTAINMENT AND RISERS COORDINATED WITH FIRE-SAFETY ZONES</text></g>
<g class="cx-mep-layer" data-testid="cx-mep-layer-water"><path class="ln" d="M344 490 V70" /><path class="ln" d="M344 100 H470 M344 216 H470 M344 332 H470" /><text x="110" y="524">WATER {D} DISTRIBUTION, PLANT AND ACCESS ZONES</text></g>
<g class="cx-mep-layer" data-testid="cx-mep-layer-drainage"><path class="ln" d="M356 70 V490" /><path class="ln" d="M356 186 H210 M356 302 H210 M356 418 H210" /><path class="ln-2" d="M210 186 V240 M210 302 V356" /><text x="110" y="524">DRAINAGE {D} GRAVITY STACKS AND FALLS COORDINATED WITH STRUCTURAL ZONES</text></g>
<g class="cx-mep-layer" data-testid="cx-mep-layer-fire"><path class="warn" d="M110 272 H316 M364 272 H570" /><path class="warn" d="M316 262 H364 V282 H316 Z" /><circle class="warn" cx="340" cy="272" r="5" /><text x="110" y="252">FIRE COMPARTMENT BOUNDARY</text><text x="380" y="292">FIRESTOP / COMPARTMENTATION INTERFACE</text><text x="110" y="524">FIRE &amp; LIFE-SAFETY INTERFACES {D} SERVICE PENETRATIONS THROUGH FIRE-RESISTING CONSTRUCTION</text></g>
<g><path class="dim" d="M316 156 H364" /><path class="dim" d="M316 388 H364" /><text x="390" y="152">ENGINEERED OPENING {D} PROJECT SPECIFIC</text><text x="390" y="404">ENGINEERED OPENING {D} PROJECT SPECIFIC</text></g>
<text x="110" y="546">{NTS} {D} ROUTES, OPENINGS AND ZONES DEFINED BY PROJECT COORDINATION</text>
          </svg>
        </div>'''

a = src.index('<div class="cx-mep-viz">')
b = src.index('\n        <div class="cx-mep-side">')
src = src[:a] + mep + src[b:]

# =====================================================================
# 11 REFERENCE — discipline grouping (approved names/descriptions verbatim)
# =====================================================================
rows = {}
for m in re.finditer(r'<div class="cx-reg-row" data-testid="cx-reg-row-(\d+)">.*?<div class="cx-reg-scope">.*?</div></div>', src, re.S):
    rows[int(m.group(1))] = m.group(0)
assert len(rows) == 11, len(rows)

groups = [('Structure', [1, 2, 3, 4, 5]), ('Concrete', [6]), ('Waterproofing', [7]),
          ('Energy / envelope', [9]), ('Acoustics', [8]), ('Fire', [10]), ('Planning / building', [11])]
out = []
for name, ids in groups:
    out.append('<div class="cx-reg-group"><span>%s</span><span class="cx-lbl">Applicable current edition</span></div>' % name)
    out.extend(rows[i] for i in ids)

a = src.index('<div class="cx-reg" data-testid="cx-register">')
b = src.index('</div>\n      <p class="cx-note"', a)
src = src[:a] + '<div class="cx-reg" data-testid="cx-register">' + ''.join(out) + src[b:]

# =====================================================================
# 12 RESULT — minimal convergence overlay
# =====================================================================
disc = ['Ground', 'Structure', 'Materials', 'Detailing', 'Execution',
        'Waterproofing', 'Envelope', 'Acoustics', 'Building services']
node = (760, 300)
strands = [[], [], []]
for i, d in enumerate(disc):
    y = 90 + i * 52
    seg = (f'<text x="150" y="{y+4}">{d.upper()}</text>'
           f'<path class="ln-2" d="M330 {y} H470 L{node[0]-40} {node[1]}" />'
           f'<circle class="ln" cx="330" cy="{y}" r="4" />')
    strands[i // 3].append(seg)
fin = ('<div class="cx-final-dwg"><svg class="cx-dwg" viewBox="0 0 1100 620" role="img" '
       'aria-label="Conceptual convergence of the engineering disciplines into the completed building" '
       'preserveAspectRatio="xMidYMid meet">'
       + ''.join('<g class="cx-fl" data-fl="%d">%s</g>' % (i, ''.join(s)) for i, s in enumerate(strands))
       + f'<g class="cx-fl" data-fl="3"><circle class="hot" cx="{node[0]-40}" cy="{node[1]}" r="7" />'
         f'<path class="hot" d="M{node[0]-33} {node[1]} H900" />'
         f'<path class="ln" d="M900 {node[1]-70} H1040 V{node[1]+70} H900 Z" />'
         f'<text x="900" y="{node[1]-86}">COMPLETED BUILDING</text>'
         f'<text x="150" y="580">CONCEPTUAL SYNTHESIS {D} NO PERFORMANCE VALUES IMPLIED</text></g>'
       + '</svg></div>')

a = src.index('<div class="cx-final-dwg">')
b = src.index('</div>', src.index('</svg>', a)) + 6
src = src[:a] + fin + src[b:]

P.write_text(src, encoding='utf-8')
print('visuals rebuilt: %d -> %d bytes' % (len(before), len(src)))
