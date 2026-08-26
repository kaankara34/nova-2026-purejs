"""Engineering revision of the Construction diagrams:
   - seismic schematic (terminology + interstorey drift + foundation reactions)
   - ground / foundation figures (datum, basement, excavation support, foundation,
     stratigraphy, ground investigation)
   - concrete information layer (phases, parameter groups, standards note)
   Section layout, typography and animation concept are untouched."""
import sys

P = '/app/frontend/construction.html'
s = open(P, encoding='utf-8').read()
n = 0


def rep(old, new):
    global s, n
    if old not in s:
        sys.exit('NOT FOUND: ' + old[:90])
    s = s.replace(old, new, 1)
    n += 1


# ----------------------------------------------------------------- SEISMIC
rep('<text class="cx-sq0-label" x="40" y="42" style="transition:opacity .5s">Undeformed analytical model</text>',
    '<text class="cx-sq0-label" x="40" y="42" style="transition:opacity .5s">Undeformed configuration &mdash; reference</text>')

# seismic action: arrow length varies with height, explicitly schematic
rep('<g data-sq="1"><path class="hot" d="M60 524 h58 m0 0 l-11 -6 m11 6 l-11 6" /><path class="hot" d="M68 434 h50 m0 0 l-11 -6 m11 6 l-11 6" /><path class="hot" d="M76 344 h42 m0 0 l-11 -6 m11 6 l-11 6" /><path class="hot" d="M84 254 h34 m0 0 l-11 -6 m11 6 l-11 6" /><path class="hot" d="M92 164 h26 m0 0 l-11 -6 m11 6 l-11 6" /><text x="40" y="628">Applied lateral action</text></g>',
    '<g data-sq="1">'
    '<path class="hot" d="M92 524 h26 m0 0 l-11 -6 m11 6 l-11 6" />'
    '<path class="hot" d="M82 434 h36 m0 0 l-11 -6 m11 6 l-11 6" />'
    '<path class="hot" d="M70 344 h48 m0 0 l-11 -6 m11 6 l-11 6" />'
    '<path class="hot" d="M58 254 h60 m0 0 l-11 -6 m11 6 l-11 6" />'
    '<path class="hot" d="M44 164 h74 m0 0 l-11 -6 m11 6 l-11 6" />'
    '<path class="hid" d="M92 524 L44 164" />'
    '<text x="40" y="628">Seismic action</text>'
    '<text class="t-dim" x="40" y="646">Schematic &mdash; not a storey-force distribution</text></g>')

# deformed shape label
rep('<g data-sq="2"><path class="hot" id="cxDefShape" d="M300 560 C 300 470, 316 380, 330 290 C 342 220, 348 186, 352 160" /><path class="hid" d="M300 560 V160" /></g>',
    '<g data-sq="2">'
    '<path class="hot" id="cxDefShape" d="M300 560 C 300 470, 316 380, 330 290 C 342 220, 348 186, 352 160" />'
    '<path class="hid" d="M300 560 V160" />'
    '<text class="t-dim" x="196" y="150">Undeformed axis</text>'
    '<text x="360" y="150">Deformed shape</text></g>')

# interstorey drift: relative displacement between consecutive levels
drift = ['<g data-sq="3">'
         '<path class="hid" d="M466 150 V536" />'
         '<text class="t-dim" x="474" y="592">Relative displacement between consecutive levels</text>']
# storey 1 is the lowest level; gauge length is proportional to the relative
# displacement of that storey (amplified, as stated by the section disclaimer)
for y, k, w in ((520, 1, 20), (430, 2, 34), (340, 3, 44), (250, 4, 52), (160, 5, 58)):
    drift.append('<path class="dim" d="M466 %d h%d M466 %d v8 M%d %d v8" />' % (y, w, y - 4, 466 + w, y - 4))
    drift.append('<text class="t-dim" x="474" y="%d">Interstorey drift &mdash; storey %d</text>' % (y - 12, k))
drift.append('</g>')
rep('<g data-sq="3"><path class="dim" d="M470 520 h56 M470 516 v8 M526 516 v8" /><text class="t-dim" x="474" y="512">Drift &mdash; storey 5</text><path class="dim" d="M470 430 h56 M470 426 v8 M526 426 v8" /><text class="t-dim" x="474" y="422">Drift &mdash; storey 4</text><path class="dim" d="M470 340 h56 M470 336 v8 M526 336 v8" /><text class="t-dim" x="474" y="332">Drift &mdash; storey 3</text><path class="dim" d="M470 250 h56 M470 246 v8 M526 246 v8" /><text class="t-dim" x="474" y="242">Drift &mdash; storey 2</text><path class="dim" d="M470 160 h56 M470 156 v8 M526 156 v8" /><text class="t-dim" x="474" y="152">Drift &mdash; storey 1</text></g>',
    ''.join(drift))

# foundation reactions: vertical, horizontal and overturning effects
rep('<g data-sq="4"><path class="hot" d="M170 600 v30 M170 630 l-6 -11 M170 630 l6 -11 M430 600 v30 M430 630 l-6 -11 M430 630 l6 -11" /><text x="200" y="628">Base reactions</text></g>',
    '<g data-sq="4">'
    '<path class="hot" d="M170 600 v28 M170 600 l-6 11 M170 600 l6 11 M430 600 v28 M430 600 l-6 11 M430 600 l6 11" />'
    '<path class="hot" d="M300 578 h44 m0 0 l-11 -6 m11 6 l-11 6" />'
    '<path class="hot" d="M232 570 a44 44 0 0 1 40 -12 m0 0 l-10 -6 m10 6 l-9 7" />'
    '<text x="196" y="646">Foundation reactions</text>'
    '<text class="t-dim" x="196" y="664">Vertical, horizontal and overturning effects</text></g>')

# ------------------------------------------------- GROUND 01 — datum / levels
rep('<svg class="cx-dwg" viewBox="0 0 620 200" role="img" aria-label="Technical drawing" preserveAspectRatio="xMidYMid meet"><path class="ln" pathLength="1" d="M20 120 H600" /><path class="ln-2" pathLength="1" d="M120 120 V70 M200 120 V84 M280 120 V64 M360 120 V78 M440 120 V70 M520 120 V86" /><text x="20" y="112">Ground level / landscape</text></svg>',
    '<svg class="cx-dwg" viewBox="0 0 620 210" role="img" aria-label="Technical drawing" preserveAspectRatio="xMidYMid meet">'
    '<path class="hid" pathLength="1" d="M20 96 C 120 88, 180 108, 264 100 C 350 92, 470 112, 600 104" />'
    '<text class="t-dim" x="20" y="88">Existing ground profile &mdash; project specific</text>'
    '<path class="ln" pathLength="1" d="M20 132 H600" />'
    '<text x="20" y="124">Finished ground level &mdash; project specific</text>'
    '<path class="ln-2" pathLength="1" d="M40 136 l-14 16 M92 136 l-14 16 M144 136 l-14 16 M196 136 l-14 16 M248 136 l-14 16 M300 136 l-14 16 M352 136 l-14 16 M404 136 l-14 16 M456 136 l-14 16 M508 136 l-14 16 M560 136 l-14 16" />'
    '<path class="dim" pathLength="1" d="M20 166 H600 M300 158 v16" />'
    '<text class="t-dim" x="20" y="184">Project datum &plusmn;0.00</text>'
    '<path class="ln-2" pathLength="1" d="M232 132 V44 M388 132 V44 M232 44 H388" />'
    '<text class="t-dim" x="240" y="36">Building reference</text></svg>')

# ------------------------------------------------- GROUND 02 — basement depth
rep('<svg class="cx-dwg" viewBox="0 0 620 220" role="img" aria-label="Technical drawing" preserveAspectRatio="xMidYMid meet"><path class="fillg" pathLength="1" d="M90 20 H530 V110 H90 Z" /><path class="fillg" pathLength="1" d="M90 110 H530 V200 H90 Z" /><text x="106" y="70">Basement level</text><text x="106" y="160">Basement level</text><path class="dim" pathLength="1" d="M60 20 V200 M54 20 h12 M54 200 h12" /><text class="t-dim" x="20" y="118">Depth</text></svg>',
    '<svg class="cx-dwg" viewBox="0 0 620 230" role="img" aria-label="Technical drawing" preserveAspectRatio="xMidYMid meet">'
    '<path class="ln" pathLength="1" d="M20 22 H600" />'
    '<text class="t-dim" x="20" y="16">Finished ground level</text>'
    '<path class="fillg" pathLength="1" d="M104 22 H528 V104 H104 Z" />'
    '<path class="fillg" pathLength="1" d="M104 104 H528 V186 H104 Z" />'
    '<text x="120" y="70">B01 &mdash; basement level, project specific</text>'
    '<text x="120" y="152">B0n &mdash; basement level, project specific</text>'
    '<path class="ln" pathLength="1" d="M20 194 H600" />'
    '<text class="t-dim" x="20" y="212">Foundation level &mdash; project specific</text>'
    '<path class="dim" pathLength="1" d="M72 22 V194 M66 22 h12 M66 194 h12" />'
    '<text class="t-dim" x="20" y="112">Excavation / basement depth &mdash; project specific</text></svg>')

# --------------------------------- GROUND 03 — excavation support (system neutral)
rep('<svg class="cx-dwg" viewBox="0 0 620 200" role="img" aria-label="Technical drawing" preserveAspectRatio="xMidYMid meet"><path class="ln" pathLength="1" d="M80 10 V190 M540 10 V190" /><path class="hid" pathLength="1" d="M80 60 H540 M80 120 H540" /><text x="20" y="196">Retaining elements &mdash; system project specific</text></svg>',
    '<svg class="cx-dwg" viewBox="0 0 620 240" role="img" aria-label="Technical drawing" preserveAspectRatio="xMidYMid meet">'
    '<path class="ln" pathLength="1" d="M20 46 H150" />'
    '<text class="t-dim" x="20" y="38">Existing ground</text>'
    '<path class="ln-2" pathLength="1" d="M36 50 l-12 14 M74 50 l-12 14 M112 50 l-12 14 M150 50 l-12 14" />'
    '<path class="fillg" pathLength="1" d="M20 64 H150 V214 H20 Z" />'
    '<text class="t-dim" x="30" y="140">Retained ground</text>'
    '<path class="ln" pathLength="1" d="M162 46 V214 M172 46 V214" />'
    '<text class="t-dim" x="182" y="60">Excavation support system &mdash; project specific</text>'
    '<path class="hot" pathLength="1" d="M182 116 h40 m0 0 l-11 -6 m11 6 l-11 6" />'
    '<path class="hot" pathLength="1" d="M182 156 h40 m0 0 l-11 -6 m11 6 l-11 6" />'
    '<text class="t-dim" x="230" y="140">Ground and groundwater actions</text>'
    '<path class="ln" pathLength="1" d="M172 214 H600" />'
    '<text class="t-dim" x="430" y="232">Excavation / foundation level</text>'
    '<path class="hid" pathLength="1" d="M172 176 H600" />'
    '<text class="t-dim" x="430" y="170">Groundwater &mdash; if encountered</text>'
    '<path class="ln-2" pathLength="1" d="M330 60 V26 M470 60 V26 M330 26 H470 M330 60 H470" />'
    '<text class="t-dim" x="330" y="18">Adjacent structure / property &mdash; where applicable</text>'
    '<path class="ln-2" pathLength="1" d="M330 60 H600" /></svg>')

# ------------------------------------------------- GROUND 04 — foundation system
rep('<img src="./media/images/construction/rebar-cage.webp" alt="Foundation construction" loading="lazy" decoding="async" />',
    '<img src="./media/images/construction/foundation-mat.webp" alt="Foundation reinforcement before concrete placement" loading="lazy" decoding="async" />')
rep('<path class="hotf" pathLength="1" d="M70 60 H550 V130 H70 Z" /><text x="70" y="50">Foundation system</text><path class="ln" pathLength="1" d="M20 130 H600" />',
    '<path class="hot" pathLength="1" d="M150 14 v30 m0 0 l-6 -11 m6 11 l6 -11 M310 14 v30 m0 0 l-6 -11 m6 11 l6 -11 M470 14 v30 m0 0 l-6 -11 m6 11 l6 -11" />'
    '<path class="hot" pathLength="1" d="M196 30 h40 m0 0 l-11 -6 m11 6 l-11 6" />'
    '<path class="hot" pathLength="1" d="M368 34 a40 40 0 0 1 38 -12 m0 0 l-10 -6 m10 6 l-9 7" />'
    '<text x="20" y="26">Structural actions &mdash; vertical, horizontal, moments</text>'
    '<path class="hotf" pathLength="1" d="M70 60 H550 V130 H70 Z" />'
    '<text x="70" y="52">Foundation system &mdash; project specific</text>'
    '<text class="t-dim" x="70" y="170">Supporting ground</text>'
    '<path class="ln" pathLength="1" d="M20 130 H600" />')

# ------------------------------------------------- GROUND 05 — stratigraphy
rep('<text x="20" y="62">Stratum &mdash; project specific</text>',
    '<text x="20" y="62">Stratum &mdash; project specific</text>'
    '<path class="hid" pathLength="1" d="M470 30 V232 M462 60 h16 M462 130 h16 M462 200 h16" />'
    '<text class="t-dim" x="484" y="36">Borehole / investigation axis</text>'
    '<path class="dim" pathLength="1" d="M180 88 H340 M196 94 H324 M212 100 H308" />'
    '<text class="t-dim" x="180" y="82">Groundwater &mdash; if encountered</text>')
rep('<path class="ln" pathLength="1" d="M20 40 H600" />',
    '<path class="ln" pathLength="1" d="M20 40 H600" /><text class="t-dim" x="20" y="32">Ground surface</text>')

# ------------------------------------------------- GROUND 06 — investigation
rep('<img src="./media/images/construction/foundation.webp" alt="Investigation depth construction" loading="lazy" decoding="async" />',
    '<img src="./media/images/construction/ground-investigation.webp" alt="Geotechnical drilling rig during ground investigation" loading="lazy" decoding="async" />')
rep('<path class="hid" pathLength="1" d="M300 10 V170" /><path class="dim" pathLength="1" d="M240 170 H360" /><text class="t-dim" x="240" y="192">Investigation depth &mdash; project specific</text>',
    '<path class="ln" pathLength="1" d="M20 30 H600" />'
    '<text class="t-dim" x="20" y="24">Ground level</text>'
    '<path class="hid" pathLength="1" d="M300 30 V172 M292 70 h16 M292 110 h16 M292 150 h16" />'
    '<text class="t-dim" x="316" y="60">Borehole / investigation</text>'
    '<path class="dim" pathLength="1" d="M250 30 V172 M244 30 h12 M244 172 h12" />'
    '<text class="t-dim" x="20" y="192">Investigation depth &mdash; project specific, governed by the zone of ground influence</text>')

# ------------------------------------------------------------------ CONCRETE
rep('<h2 class="cx-h2">Concrete performance</h2>\n        <p class="cx-p cx-p--s">Specified compressive strength',
    '<h2 class="cx-h2">Concrete performance</h2>\n        <p class="cx-lbl" style="margin:2px 0 8px">Concrete performance extends beyond compressive strength.</p>\n        <p class="cx-p cx-p--s">Specified compressive strength')

rep('<div class="cx-flow-band"><img src="./media/images/construction/concrete-ascast.webp" alt="As-cast reinforced-concrete surface showing formwork tie positions" loading="lazy" decoding="async" /></div>',
    '<div class="cx-flow-band"><img src="./media/images/construction/concrete-ascast.webp" alt="As-cast reinforced-concrete surface showing formwork tie positions" loading="lazy" decoding="async" />'
    '<div class="cx-bandov" data-testid="cx-concrete-overlay">'
    '<span class="cx-phase" data-phase="0">Specified material</span>'
    '<span class="cx-phase" data-phase="1">Fresh concrete</span>'
    '<span class="cx-phase" data-phase="2">Execution</span>'
    '<span class="cx-phase" data-phase="3">Early-age development</span>'
    '<span class="cx-phase" data-phase="4">Hardened concrete</span>'
    '<span class="cx-phase" data-phase="5">Verified performance</span>'
    '</div></div>')

rep('<div class="cx-flow-head"><p class="cx-note">Concrete specification, production and conformity are governed through TS EN 206 together with the applicable complementary national requirements. Project-specific structural documents define the required concrete class and execution criteria.</p></div>',
    '<div class="cx-flow-head">'
    '<div class="cx-pgroups" data-testid="cx-concrete-parameters">'
    '<div><span class="cx-lbl cx-lbl--warm">Input parameters</span>'
    '<span class="cx-plist">Strength class &middot; Exposure conditions &middot; Consistency &middot; Constituent materials</span></div>'
    '<div><span class="cx-lbl cx-lbl--warm">Execution parameters</span>'
    '<span class="cx-plist">Delivery &middot; Placement &middot; Consolidation &middot; Curing</span></div>'
    '<div><span class="cx-lbl cx-lbl--warm">Performance / verification</span>'
    '<span class="cx-plist">Mechanical properties &middot; Surface integrity &middot; Durability &middot; Conformity</span></div>'
    '<div class="cx-pout"><span class="cx-lbl">Resulting performance</span>'
    '<span class="cx-plist">Strength &middot; Serviceability &middot; Durability</span></div>'
    '</div>'
    '<p class="cx-note"><b>Material &rarr; execution &rarr; performance.</b> Concrete specification, production and conformity are governed by TS EN 206+A2 together with the applicable provisions of TS 13515, its complementary national standard in T&uuml;rkiye. Project-specific structural documents and applicable execution requirements define the concrete classes, exposure conditions, detailing and construction criteria relevant to each structural element.</p></div>')

open(P, 'w', encoding='utf-8').write(s)
print('engineering revision applied,', n, 'edits; len', len(s))
