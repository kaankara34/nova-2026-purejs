#!/usr/bin/env python3
"""Refine the section 08 envelope control-layer figure (legibility + hierarchy)."""
import pathlib

P = pathlib.Path('/app/frontend/construction.html')
s = P.read_text(encoding='utf-8')
D = '&mdash;'

bands = [(140, 36, 'WEATHER'), (176, 80, 'THERMAL'), (256, 16, 'AIR'),
         (272, 24, 'VAPOUR*'), (296, 84, 'STRUCTURE'), (380, 24, 'FINISH')]
b = []
for i, (bx, bw, nm) in enumerate(bands):
    b.append(f'<rect class="fillg" x="{bx}" y="100" width="{bw}" height="180" />')
    cx = bx + bw / 2
    if nm == 'THERMAL':
        b.append('<path class="ln-2" d="' + ' '.join(
            f'M{bx + k} 280 l40 -40' for k in range(-32, bw, 22)) + '" />')
    elif nm == 'STRUCTURE':
        b.append('<path class="ln-2" d="' + ' '.join(
            f'M{bx + k} 280 l40 -40 M{bx + k} 100 l40 40' for k in range(-32, bw, 26)) + '" />')
    elif nm == 'AIR':
        b.append(f'<path class="hid" d="M{cx:.0f} 100 V280" />')
    elif nm == 'VAPOUR*':
        b.append(f'<path class="hid" d="M{cx:.0f} 100 V280" stroke-dasharray="2 5" />')
    b.append(f'<text class="t-dim" transform="rotate(-90 {cx:.0f} 296)" x="{cx:.0f}" y="296" text-anchor="end">{nm}</text>')

fig = f'''<div class="cx-det-fig" data-draw data-start="top 82%" data-end="bottom 55%">
<svg class="cx-dwg" viewBox="0 0 720 680" role="img" aria-label="Conceptual envelope control layers and critical junctions" preserveAspectRatio="xMidYMid meet">
<text x="40" y="44">CONTROL LAYERS {D} CONCEPTUAL; SEQUENCE PROJECT SPECIFIC</text>
<path class="hid" d="M40 100 H140 M404 100 H700 M40 280 H140 M404 280 H700" />
{''.join(b)}
<path class="dim" pathLength="1" d="M140 292 H404 M140 286 v12 M404 286 v12" />
<text class="t-dim" x="418" y="296">ASSEMBLY {D} PROJECT SPECIFIC</text>
<text x="470" y="126">EXTERIOR</text><text x="470" y="272">INTERIOR</text>
<path class="ln-2" d="M470 170 H540 m0 0 l-9 -5 m9 5 l-9 5" /><text x="470" y="160">HEAT / MOISTURE / AIR</text>
<text x="40" y="386">* MOISTURE / VAPOUR CONTROL AS APPLICABLE</text>
<text x="40" y="440">CRITICAL JUNCTIONS {D} CONTINUITY OF THE CONTROL LAYERS</text>
<path class="ln" d="M180 486 V664 M206 486 V664" />
<path class="ln" d="M206 546 H430 M206 556 H430" />
<path class="ln" d="M206 620 H430" />
<path class="ln" d="M168 470 H212 V486" />
<path class="ln" d="M120 546 H180 M120 546 V534 M120 556 H180" />
<path class="hid" d="M180 664 H430" />
<path class="ln-2" d="M300 620 V590 H206" />
<path class="hot" d="M193 470 V540 H146 V550 H193 V664" />
<text x="40" y="466">THERMAL CONTINUITY</text>
<circle class="ln" cx="193" cy="478" r="6" /><text x="450" y="474">PARAPET / ROOF TRANSITION</text>
<circle class="ln" cx="193" cy="546" r="6" /><text x="450" y="542">SLAB EDGE</text>
<circle class="ln" cx="146" cy="548" r="6" /><text x="40" y="528">BALCONY</text>
<circle class="ln" cx="193" cy="620" r="6" /><text x="450" y="616">WINDOW PERIMETER</text>
<circle class="ln" cx="206" cy="590" r="6" /><text x="450" y="586">SERVICE PENETRATION</text>
<circle class="ln" cx="193" cy="660" r="6" /><text x="450" y="662">FOUNDATION / FA&Ccedil;ADE</text>
<text x="40" y="676">{('CONCEPTUAL ' + D + ' NOT TO SCALE')} {D} PERFORMANCE VALUES DEFINED BY PROJECT DOCUMENTATION</text>
</svg>
<div class="cx-det-scale"><span class="cx-lbl">Macro detail</span><span class="cx-lbl">Layer sequence project specific</span></div>
</div>'''

a = s.index('<div class="cx-det-fig"')
z = s.index('\n        <div class="cx-layerlist">')
P.write_text(s[:a] + fig + s[z:], encoding='utf-8')
print('08 figure refined')
