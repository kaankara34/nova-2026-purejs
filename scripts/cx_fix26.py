#!/usr/bin/env python3
"""Round-2 audit fixes: 06 mobile sequence drawing variant, 12 mobile geometry."""
import pathlib

P = pathlib.Path('/app/frontend/construction.html')
s = P.read_text(encoding='utf-8')
D = '&mdash;'
W = 230


def cell(i):
    """Verification-point cell drawn at the origin: 230 x 60 with its label at y=84."""
    if i == 0:
        return (f'<path class="hid" d="M0 0 H{W} V60 H0 Z" />'
                f'<path class="ln-2" d="M14 16 H150 M14 30 H120 M14 44 H140" />'
                f'<path class="ln" d="M150 38 H{W} V60 H150 Z" />'
                '<text x="0" y="84">DOCUMENTATION</text>')
    if i == 1:
        return ('<path class="fillg" d="M0 0 H18 V60 H0 Z" />'
                f'<path class="fillg" d="M{W-18} 0 H{W} V60 H{W-18} Z" />'
                '<path class="hot" d="M42 6 V54 M90 6 V54 M140 6 V54 M188 6 V54" />'
                '<path class="hot" d="M42 12 H188 M42 30 H188 M42 48 H188" />'
                '<path class="dim" d="M18 68 H42 M18 63 v10 M42 63 v10" />'
                '<text x="0" y="84">PRE-POUR</text>')
    if i == 2:
        return ('<path class="fillg" d="M0 0 H18 V60 H0 Z" />'
                f'<path class="fillg" d="M{W-18} 0 H{W} V60 H{W-18} Z" />'
                f'<path class="ln-2" d="M18 60 H{W-18} M18 44 H{W-18} M18 28 H{W-18}" />'
                '<path class="hot" d="M115 -16 V10 m0 0 l-7 -10 m7 10 l7 -10" />'
                '<text x="0" y="84">CONCRETE EXECUTION</text>')
    if i == 3:
        return (f'<path class="fillg" d="M0 16 H{W} V60 H0 Z" />'
                f'<path class="hid" d="M0 6 H{W}" />'
                '<path class="hot" d="M50 2 v-14 M115 2 v-14 M180 2 v-14" />'
                '<text x="0" y="84">EARLY AGE</text>')
    if i == 4:
        return (f'<path class="fillg" d="M34 0 H{W} V60 H34 Z" />'
                '<path class="hot" d="M24 0 V60" /><path class="ln-2" d="M10 0 V60" />'
                '<path class="ln-2" d="M10 10 l14 10 M10 28 l14 10 M10 46 l14 10" />'
                '<circle class="warn" cx="120" cy="30" r="8" /><path class="warn" d="M90 30 h60" />'
                '<text x="0" y="84">ENCLOSURE</text>')
    return (f'<path class="fillg" d="M0 0 H{W} V60 H0 Z" />'
            f'<path class="dim" d="M0 70 H{W} M0 65 v10 M{W} 65 v10" />'
            '<path class="dim" d="M-14 0 V60 M-19 0 h10 M-19 60 h10" />'
            '<text x="0" y="84">COMPLETION</text>')


head = f'<text x="20" y="14">VERIFICATION BEFORE WORK IS CONCEALED {D} CONCEPTUAL SEQUENCE</text>'

# desktop: one row of six
xs = [20, 270, 520, 770, 1020, 1270]
dsk = ''.join(f'<g data-elstate="{i}" transform="translate({x} 26)">{cell(i)}</g>'
              for i, x in enumerate(xs))
desktop = ('<div class="cx-insp-elem cx-insp-elem--d"><svg class="cx-dwg" viewBox="0 0 1520 124" role="img" '
           'aria-label="Verification points along the construction sequence, conceptual" '
           f'preserveAspectRatio="xMidYMid meet">{head}{dsk}</svg></div>')

# mobile: two columns of three, so the same drawing stays readable
pos = [(20, 40), (280, 40), (20, 170), (280, 170), (20, 300), (280, 300)]
mob = ''.join(f'<g data-elstate="{i}" transform="translate({x} {y})">{cell(i)}</g>'
              for i, (x, y) in enumerate(pos))
mobile = ('<div class="cx-insp-elem cx-insp-elem--m"><svg class="cx-dwg" viewBox="0 0 540 410" role="img" '
          'aria-label="Verification points along the construction sequence, conceptual" '
          f'preserveAspectRatio="xMidYMid meet">{head}{mob}</svg></div>')

a = s.index('<div class="cx-insp-elem"')
b = s.index('</div>', s.index('</svg>', a)) + 6
s = s[:a] + desktop + '\n      ' + mobile + s[b:]

# ---------------------------------------------------------------- 12 mobile geometry
s = s.replace('viewBox="0 0 440 286"', 'viewBox="0 0 440 252"')
s = s.replace('<circle class="hot" cx="220" cy="148" r="6" />', '<circle class="hot" cx="220" cy="132" r="6" />')
s = s.replace('<path class="hot" d="M220 154 V188" />', '<path class="hot" d="M220 138 V162" />')
s = s.replace('<path class="ln" d="M140 188 H300 V238 H140 Z" />', '<path class="ln" d="M140 162 H300 V206 H140 Z" />')
s = s.replace('<text x="220" y="216" text-anchor="middle">COMPLETED BUILDING</text>',
              '<text x="220" y="188" text-anchor="middle">COMPLETED BUILDING</text>')
s = s.replace('<text x="220" y="262" text-anchor="middle">CONCEPTUAL SYNTHESIS</text>',
              '<text x="220" y="228" text-anchor="middle">CONCEPTUAL SYNTHESIS</text>')
s = s.replace('<text x="220" y="280" text-anchor="middle">NO PERFORMANCE VALUES IMPLIED</text>',
              '<text x="220" y="246" text-anchor="middle">NO PERFORMANCE VALUES IMPLIED</text>')
s = s.replace('M292 96 H402 M347 96 L220 148', 'M292 96 H402 M347 96 L220 132')
s = s.replace('M16 96 H126 M71 96 L220 148', 'M16 96 H126 M71 96 L220 132')
s = s.replace('M160 96 H270 M215 96 L220 148', 'M160 96 H270 M215 96 L220 132')

P.write_text(s, encoding='utf-8')
print('06 variants + 12 geometry done')
