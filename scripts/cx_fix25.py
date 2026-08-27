#!/usr/bin/env python3
"""Post-audit fixes: 06 sequence drawing legibility, 08 label geometry,
10 slab openings, 12 note placement."""
import pathlib
import re

P = pathlib.Path('/app/frontend/construction.html')
s = P.read_text(encoding='utf-8')
D = '&mdash;'

# ---------------------------------------------------------------- 06
xs = [20, 270, 520, 770, 1020, 1270]
W = 230
g = []
x = xs[0]
g.append(f'<g data-elstate="0"><path class="hid" d="M{x} 24 H{x+W} V84 H{x} Z" />'
         f'<path class="ln-2" d="M{x+14} 40 H{x+150} M{x+14} 54 H{x+120} M{x+14} 68 H{x+140}" />'
         f'<path class="ln" d="M{x+150} 62 H{x+W} V84 H{x+150} Z" />'
         f'<text x="{x}" y="112">DOCUMENTATION</text></g>')
x = xs[1]
g.append(f'<g data-elstate="1"><path class="fillg" d="M{x} 24 H{x+18} V84 H{x} Z" />'
         f'<path class="fillg" d="M{x+W-18} 24 H{x+W} V84 H{x+W-18} Z" />'
         f'<path class="hot" d="M{x+42} 30 V78 M{x+90} 30 V78 M{x+140} 30 V78 M{x+188} 30 V78" />'
         f'<path class="hot" d="M{x+42} 36 H{x+188} M{x+42} 54 H{x+188} M{x+42} 72 H{x+188}" />'
         f'<path class="dim" d="M{x+18} 92 H{x+42} M{x+18} 87 v10 M{x+42} 87 v10" />'
         f'<text x="{x}" y="112">PRE-POUR</text></g>')
x = xs[2]
g.append(f'<g data-elstate="2"><path class="fillg" d="M{x} 24 H{x+18} V84 H{x} Z" />'
         f'<path class="fillg" d="M{x+W-18} 24 H{x+W} V84 H{x+W-18} Z" />'
         f'<path class="ln-2" d="M{x+18} 84 H{x+W-18} M{x+18} 68 H{x+W-18} M{x+18} 52 H{x+W-18}" />'
         f'<path class="hot" d="M{x+115} 8 V34 m0 0 l-7 -10 m7 10 l7 -10" />'
         f'<text x="{x}" y="112">CONCRETE EXECUTION</text></g>')
x = xs[3]
g.append(f'<g data-elstate="3"><path class="fillg" d="M{x} 40 H{x+W} V84 H{x} Z" />'
         f'<path class="hid" d="M{x} 30 H{x+W}" />'
         f'<path class="hot" d="M{x+50} 26 v-14 M{x+115} 26 v-14 M{x+180} 26 v-14" />'
         f'<text x="{x}" y="112">EARLY AGE</text></g>')
x = xs[4]
g.append(f'<g data-elstate="4"><path class="fillg" d="M{x+34} 24 H{x+W} V84 H{x+34} Z" />'
         f'<path class="hot" d="M{x+24} 24 V84" /><path class="ln-2" d="M{x+10} 24 V84" />'
         f'<path class="ln-2" d="M{x+10} 34 l14 10 M{x+10} 52 l14 10 M{x+10} 70 l14 10" />'
         f'<circle class="warn" cx="{x+120}" cy="54" r="8" /><path class="warn" d="M{x+90} 54 h60" />'
         f'<text x="{x}" y="112">ENCLOSURE</text></g>')
x = xs[5]
g.append(f'<g data-elstate="5"><path class="fillg" d="M{x} 24 H{x+W} V84 H{x} Z" />'
         f'<path class="dim" d="M{x} 94 H{x+W} M{x} 89 v10 M{x+W} 89 v10" />'
         f'<path class="dim" d="M{x-14} 24 V84 M{x-19} 24 h10 M{x-19} 84 h10" />'
         f'<text x="{x}" y="112">COMPLETION</text></g>')

insp = ('<div class="cx-insp-elem"><svg class="cx-dwg" viewBox="0 0 1520 124" role="img" '
        'aria-label="Verification points along the construction sequence, conceptual" '
        'preserveAspectRatio="xMidYMid meet">'
        '<text x="20" y="14">VERIFICATION BEFORE WORK IS CONCEALED ' + D + ' CONCEPTUAL SEQUENCE</text>'
        + ''.join(g) + '</svg></div>')
a = s.index('<div class="cx-insp-elem">')
b = s.index('</div>', s.index('</svg>', a)) + 6
s = s[:a] + insp + s[b:]

# ---------------------------------------------------------------- 08
s = s.replace('viewBox="0 0 720 680"', 'viewBox="0 0 720 706"')
s = s.replace('<text x="40" y="386">* MOISTURE / VAPOUR CONTROL AS APPLICABLE</text>',
              '<text x="40" y="414">* MOISTURE / VAPOUR CONTROL AS APPLICABLE</text>')
s = s.replace('<text x="40" y="440">CRITICAL JUNCTIONS', '<text x="40" y="446">CRITICAL JUNCTIONS')
s = s.replace('<text x="40" y="676">CONCEPTUAL', '<text x="40" y="698">CONCEPTUAL')

# ---------------------------------------------------------------- 10
s = s.replace('<path class="ln" d="M110 156 H570 M110 272 H570 M110 388 H570" />',
              '<path class="ln" d="M110 156 H316 M364 156 H570 M110 272 H316 M364 272 H570 '
              'M110 388 H316 M364 388 H570" />')
s = s.replace('<g><path class="dim" d="M316 156 H364" /><path class="dim" d="M316 388 H364" />'
              '<text x="390" y="152">ENGINEERED OPENING &mdash; PROJECT SPECIFIC</text>'
              '<text x="390" y="404">ENGINEERED OPENING &mdash; PROJECT SPECIFIC</text></g>',
              '<g><path class="dim" d="M316 148 H364 M316 164 H364 M316 264 H364 M316 280 H364 '
              'M316 380 H364 M316 396 H364" />'
              '<text x="390" y="144">ENGINEERED OPENINGS AT EVERY SLAB CROSSING '
              '&mdash; PROJECT SPECIFIC</text></g>')

# ---------------------------------------------------------------- 12
s = s.replace('<text x="640" y="376" text-anchor="end">CONCEPTUAL SYNTHESIS &mdash; NO PERFORMANCE VALUES IMPLIED</text>',
              '<text x="995" y="272" text-anchor="middle">CONCEPTUAL SYNTHESIS &mdash; NO PERFORMANCE VALUES IMPLIED</text>')

P.write_text(s, encoding='utf-8')
print('html fixes applied')
