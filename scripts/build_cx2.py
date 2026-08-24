#!/usr/bin/env python3
"""Rebuild construction.html: technical-documentation experience.
Reuses the existing Nova header / side menu / footer markup verbatim."""
import re, pathlib

SRC = pathlib.Path('/app/frontend/construction.html')
html = SRC.read_text()

head_end = html.index('</aside>') + len('</aside>')
head = html[:head_end]
footer_start = html.index('  <footer class="site-footer">')
footer_end = html.index('</footer>', footer_start) + len('</footer>')
footer = html[footer_start:footer_end]

# --- head adjustments -------------------------------------------------------
head = head.replace(
    '<title>Construction &amp; Engineering | Nova Konut</title>',
    '<title>Construction &amp; Engineering | Nova Konut</title>')
head = re.sub(r'<meta name="description"[^>]*>',
  '<meta name="description" content="Nova Konut construction and engineering methodology: structural system and load path, seismic design under TBDY 2018, ground and foundation interaction, concrete performance, reinforcement detailing, execution control, waterproofing continuity, building envelope, acoustics and building-services coordination." />',
  head)
if 'importmap' not in head:
    head = head.replace('</head>',
      '  <script type="importmap">\n'
      '  { "imports": { "three": "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js" } }\n'
      '  </script>\n</head>')

IMG = './media/images/construction/'


def dwg(view, inner, cls='cx-dwg'):
    return f'<svg class="{cls}" viewBox="{view}" role="img" aria-label="Technical drawing" preserveAspectRatio="xMidYMid meet">{inner}</svg>'


def hatch(y, x0, x1, step=26, dx=-16, dy=20):
    return ''.join(f'<path class="ln-2" d="M{x} {y} l{dx} {dy}" />' for x in range(x0, x1, step))


# =============================== HERO =======================================
hero_grid = ''.join(
    [f'<path pathLength="1" d="M{x} 0 V900" />' for x in (300, 600, 900, 1200, 1500)] +
    [f'<path pathLength="1" d="M0 {y} H1600" />' for y in (180, 360, 540, 720)])

hero = f'''
  <!-- ===================== HERO ===================== -->
  <section class="cx-hero" data-testid="cx-hero">
    <div class="cx-hero-stage">
      <div class="cx-hero-photo cx-hero-fallback">
        <img src="{IMG}rebar-macro.webp" alt="Dense field of deformed reinforcing steel before placement" width="1500" height="2666" decoding="async" />
      </div>
      <canvas class="cx-canvas" id="cxRebarCanvas" data-testid="cx-rebar-canvas" aria-hidden="true"></canvas>
      <svg class="cx-hero-grid" viewBox="0 0 1600 900" preserveAspectRatio="none" aria-hidden="true">{hero_grid}</svg>
      <div class="cx-hero-scrim"></div>
      <div class="cx-hero-copy">
        <span class="cx-hero-kicker"><i></i><span class="cx-lbl cx-lbl--warm">Nova Konut &mdash; Methodology</span></span>
        <h1 class="cx-hero-h1" data-testid="cx-hero-title">Construction &amp; Engineering</h1>
        <p class="cx-hero-claim">Performance is built before it is seen.</p>
        <p class="cx-p">The performance of a residential building is established through a sequence of coordinated engineering decisions &mdash; from ground investigation and structural analysis to reinforcement detailing, concrete execution, waterproofing, building-envelope continuity and services coordination.</p>
        <p class="cx-p cx-p--s">Nova approaches construction as an integrated engineering process in which design intent, material performance and site execution must remain consistent from calculation to completion.</p>
        <div class="cx-hero-foot">
          <span class="cx-cue" data-testid="cx-scroll-cue"><i></i><span class="cx-lbl">Scroll to inspect the structure</span></span>
          <span class="cx-readout"><span class="cx-lbl">Reading</span><b data-testid="cx-hero-readout">Material</b></span>
        </div>
      </div>
    </div>
  </section>
'''

# ========================= STRUCTURAL SYSTEM ================================
ELEMENTS = [
    ("Foundation", "The foundation system transfers gravity and lateral actions from the superstructure into the supporting ground. Its geometry and stiffness are determined from structural demand together with project-specific geotechnical parameters."),
    ("Columns", "Columns primarily form vertical load paths within the structural system. Their dimensions, reinforcement and interaction with beams and slabs are determined through structural analysis and detailing requirements."),
    ("Reinforced-concrete walls", "Structural walls contribute substantial lateral stiffness and strength where required by the structural configuration. Their location, geometry and coupling with the remaining system influence global stiffness, torsional response and displacement distribution."),
    ("Beams", "Beams transfer slab actions to the vertical structural system and participate in frame behaviour where required. Reinforcement detailing must provide the strength, anchorage and ductility assumed in structural analysis."),
    ("Slabs", "Floor systems distribute gravity loads while also acting as diaphragms that transfer in-plane seismic actions between vertical lateral-force-resisting elements."),
    ("Structural core", "Elevator and stair cores may form part of the lateral-force-resisting system where incorporated into the structural model. Their contribution depends on project geometry and the adopted structural solution."),
]
el_rows = ''.join(
    f'<button class="cx-el" data-testid="cx-element-{i+1}" data-el="{i}">'
    f'<span class="cx-idx">{i+1:02d}</span><span class="cx-el-t">{t}</span>'
    f'<span class="cx-el-d">{d}</span></button>'
    for i, (t, d) in enumerate(ELEMENTS))

# one structural model, six isolatable groups
floors = [560, 470, 380, 290, 200, 110]
g_found = ('<g class="cx-gr" data-el="0"><rect class="fillg" x="70" y="612" width="520" height="46" />'
           '<path class="ln" d="M40 658 H620" />' + hatch(662, 60, 640, 26, -16, 20) +
           '<text x="40" y="700">Foundation &mdash; project specific</text></g>')
g_cols = '<g class="cx-gr" data-el="1">' + ''.join(
    f'<rect class="fillg" x="{x}" y="100" width="20" height="512" />' for x in (110, 230, 350, 470)) + \
    '<text x="40" y="94">Columns</text></g>'
g_walls = '<g class="cx-gr" data-el="2">' + ''.join(
    f'<rect class="fillg" x="{x}" y="100" width="30" height="512" />' for x in (176, 404)) + \
    '<text x="470" y="94">RC walls</text></g>'
g_beams = '<g class="cx-gr" data-el="3">' + ''.join(
    f'<rect class="ln" x="{x}" y="{y-14}" width="120" height="14" />'
    for y in floors for x in (120, 240, 360)) + '</g>'
g_slabs = '<g class="cx-gr" data-el="4">' + ''.join(
    f'<rect class="fillg" x="86" y="{y-22}" width="470" height="8" />' for y in floors) + '</g>'
g_core = ('<g class="cx-gr" data-el="5"><rect class="fillg" x="266" y="100" width="76" height="512" />'
          '<path class="hid" d="M266 100 L342 612 M342 100 L266 612" />'
          '<text x="356" y="330">Structural core</text></g>')
struct_svg = dwg('0 0 660 720', g_slabs + g_beams + g_cols + g_walls + g_core + g_found +
                 '<path class="ln-2" d="M40 100 H620" /><text x="330" y="700">Structural model &mdash; indicative</text>')

structural = f'''
  <!-- ===================== STRUCTURAL SYSTEM ===================== -->
  <section class="cx-sec cx-struct" style="height:600vh" data-testid="cx-section-structural">
    <div class="cx-struct-stage">
      <div class="cx-el-copy">
        <span class="cx-idx">01 / Structure</span>
        <h2 class="cx-h2" style="margin:10px 0 12px">Structural system</h2>
        <p class="cx-p cx-p--s">The structural system is developed as a complete load path rather than as a collection of independent elements. Gravity actions, seismic effects and compatibility between foundations, vertical elements and floor diaphragms are evaluated within the same analytical model.</p>
        <div class="cx-el-list" data-testid="cx-element-list" style="margin-top:14px">{el_rows}</div>
        <p class="cx-note" style="margin-top:12px">No structural system is selected by template. Ground conditions, building geometry, architectural organisation and seismic performance requirements determine the system adopted for each project.</p>
      </div>
      <div class="cx-struct-model">{struct_svg}</div>
    </div>
  </section>
'''

# ============================== SEISMIC =====================================
SEIS_STATES = [
    ("Undeformed model", "Analytical model of mass, stiffness and geometry before lateral action is applied."),
    ("Applied lateral action", "Seismic action derived from site hazard parameters and the adopted design system."),
    ("Deformation shape", "Analytical displacement distribution over the height of the structure."),
    ("Storey drift", "Relative lateral displacement between consecutive floors, evaluated against design limits."),
    ("Base reactions", "Actions transferred through the foundation into the supporting ground."),
]
seis_states = ''.join(
    f'<div class="cx-state" data-testid="cx-seis-state-{i+1}"><span class="cx-idx">{i+1:02d}</span>'
    f'<b>{t}</b><p>{d}</p></div>' for i, (t, d) in enumerate(SEIS_STATES))

SEIS_FACS = [
    ("Seismic hazard", "Ground-motion parameters applicable to the project location."),
    ("Site conditions", "Geotechnical parameters and local soil behaviour relevant to structural design."),
    ("Mass distribution", "Distribution of seismic mass through the building height and plan."),
    ("Stiffness distribution", "Relative stiffness of structural elements governing deformation and force distribution."),
    ("Torsional response", "Relationship between mass distribution and structural stiffness in plan."),
    ("Ductility", "Ability of designated structural mechanisms to sustain inelastic deformation in accordance with the adopted design system."),
    ("Inter-storey drift", "Relative lateral displacement between consecutive floors, controlled within applicable design limits."),
    ("Foundation response", "Transfer of structural actions into the supporting foundation and ground system."),
]
seis_facs = ''.join(
    f'<div class="cx-fac" data-cx-in><span class="cx-idx">{i+1:02d}</span><b>{t}</b><p>{d}</p></div>'
    for i, (t, d) in enumerate(SEIS_FACS))

sf = [520, 430, 340, 250, 160]
frames = ''.join(
    f'<g class="cx-defframe" data-frame="{i}"><rect class="ln" x="150" y="{y}" width="300" height="7" />'
    f'<rect class="ln-2" x="160" y="{y}" width="12" height="90" /><rect class="ln-2" x="428" y="{y}" width="12" height="90" /></g>'
    for i, y in enumerate(reversed(sf)))
arrows = ''.join(
    f'<path class="hot" d="M{60 + i*8} {y+4} h{58 - i*8} m0 0 l-11 -6 m11 6 l-11 6" />' for i, y in enumerate(sf))
drift = ''.join(
    f'<path class="dim" d="M470 {y} h56 M470 {y-4} v8 M526 {y-4} v8" /><text class="t-dim" x="474" y="{y-8}">Drift &mdash; storey {5-i}</text>'
    for i, y in enumerate(sf))
seis_svg = dwg('0 0 620 640',
    f'<g data-sq="0">{frames}<rect class="fillg" x="120" y="560" width="360" height="34" /><path class="ln" d="M40 594 H580" />' + hatch(598, 60, 600, 26, -14, 18) + '<text class="cx-sq0-label" x="40" y="42" style="transition:opacity .5s">Undeformed analytical model</text></g>'
    f'<g data-sq="1">{arrows}<text x="40" y="628">Applied lateral action</text></g>'
    f'<g data-sq="2"><path class="hot" id="cxDefShape" d="M300 560 C 300 470, 316 380, 330 290 C 342 220, 348 186, 352 160" /><path class="hid" d="M300 560 V160" /></g>'
    f'<g data-sq="3">{drift}</g>'
    f'<g data-sq="4"><path class="hot" d="M170 600 v30 M170 630 l-6 -11 M170 630 l6 -11 M430 600 v30 M430 630 l-6 -11 M430 630 l6 -11" /><text x="200" y="628">Base reactions</text></g>')

seismic = f'''
  <!-- ===================== SEISMIC ===================== -->
  <section class="cx-sec cx-seis" style="height:520vh" data-testid="cx-section-seismic">
    <div class="cx-seis-stage">
      <div class="cx-seis-viz">
        {seis_svg}
        <span class="cx-seis-caption cx-lbl cx-lbl--warm" data-testid="cx-seis-disclaimer">Amplified for visualisation &mdash; not to scale</span>
      </div>
      <div>
        <span class="cx-idx">02 / Seismic</span>
        <h2 class="cx-h2" style="margin:10px 0 6px">Seismic design</h2>
        <p class="cx-lbl" style="margin-bottom:12px">Structural response is a system property.</p>
        <p class="cx-p cx-p--s">For projects in Istanbul, seismic actions form a fundamental design condition from the earliest stages of structural development. Structural analysis is carried out using the seismic design framework established by the T&uuml;rkiye Bina Deprem Y&ouml;netmeli&#287;i 2018 and site-specific hazard parameters obtained through the T&uuml;rkiye Deprem Tehlike Haritas&#305;.</p>
        <p class="cx-p cx-p--s" style="margin-top:10px">The purpose of seismic design is not to make a single column, wall or beam independently &ldquo;strong&rdquo;. Global behaviour is governed by the interaction between mass, stiffness, strength, ductility, geometry, foundation conditions and the distribution of lateral-resisting elements throughout the building.</p>
        <div class="cx-state-list" style="margin-top:16px">{seis_states}</div>
      </div>
    </div>
  </section>

  <section class="cx-sec" style="padding-top:0" data-testid="cx-section-seismic-factors">
    <div class="cx-wrap">
      <div class="cx-tickrule"></div>
      <span class="cx-lbl" data-cx-in>Design parameters evaluated together</span>
      <div class="cx-facs" style="margin-top:22px">{seis_facs}</div>
    </div>
  </section>
'''

# ========================= GROUND / FOUNDATION ==============================
STRATA = [
    ("&plusmn;0.00", "Street level", "Site access, ground-level geometry and the interface between landscape, structure and adjoining conditions are established from survey and planning constraints.", 'PROJECT SPECIFIC', None,
     dwg('0 0 620 200', '<path class="ln" pathLength="1" d="M20 120 H600" /><path class="ln-2" pathLength="1" d="M120 120 V70 M200 120 V84 M280 120 V64 M360 120 V78 M440 120 V70 M520 120 V86" /><text x="20" y="112">Ground level / landscape</text>')),
    ("&minus;01 / &minus;n", "Basement levels", "Below-ground levels are organised around parking, plant, circulation and shaft geometry. Their number and depth follow the approved project, not a standard configuration.", 'PROJECT SPECIFIC', f'{IMG}structure-interior.webp',
     dwg('0 0 620 220', '<path class="fillg" pathLength="1" d="M90 20 H530 V110 H90 Z" /><path class="fillg" pathLength="1" d="M90 110 H530 V200 H90 Z" /><text x="106" y="70">Basement level</text><text x="106" y="160">Basement level</text><path class="dim" pathLength="1" d="M60 20 V200 M54 20 h12 M54 200 h12" /><text class="t-dim" x="20" y="118">Depth</text>')),
    ("Retaining", "Retaining system", "Excavation support is selected according to excavation geometry, ground conditions, groundwater and adjacent structures. It is an engineered temporary and permanent works problem, not a formality.", 'PROJECT SPECIFIC', None,
     dwg('0 0 620 200', '<path class="ln" pathLength="1" d="M80 10 V190 M540 10 V190" /><path class="hid" pathLength="1" d="M80 60 H540 M80 120 H540" /><text x="20" y="196">Retaining elements &mdash; system project specific</text>')),
    ("Foundation", "Foundation", "Foundation geometry and stiffness follow from structural demand and geotechnical parameters. Load transfer, settlement behaviour and interaction with the retaining system are assessed together.", 'PROJECT SPECIFIC', f'{IMG}rebar-cage.webp',
     dwg('0 0 620 200', '<path class="hotf" pathLength="1" d="M70 60 H550 V130 H70 Z" /><text x="70" y="50">Foundation system</text><path class="ln" pathLength="1" d="M20 130 H600" />' + hatch(134, 40, 600, 26, -14, 18))),
    ("Strata", "Soil strata", "Stratification and engineering parameters are taken from the geotechnical investigation for the site. Layer sequence and properties differ between developments and are never assumed.", 'PROJECT SPECIFIC', None,
     dwg('0 0 620 240', '<path class="ln" pathLength="1" d="M20 40 H600" /><text x="20" y="62">Stratum &mdash; project specific</text><path class="ln" pathLength="1" d="M20 110 H600" /><text x="20" y="132">Stratum &mdash; project specific</text><path class="ln" pathLength="1" d="M20 180 H600" /><text x="20" y="202">Stratum &mdash; project specific</text>' + hatch(46, 40, 600, 30, -14, 16) + hatch(116, 40, 600, 30, -14, 16))),
    ("Investigation", "Investigation depth", "Ground investigation extends to the depth required for the structural and geotechnical assessment of the specific project. Reported parameters govern design; they are not transferable between sites.", 'PROJECT SPECIFIC', f'{IMG}foundation.webp',
     dwg('0 0 620 200', '<path class="hid" pathLength="1" d="M300 10 V170" /><path class="dim" pathLength="1" d="M240 170 H360" /><text class="t-dim" x="240" y="192">Investigation depth &mdash; project specific</text>')),
]
strata_html = ''
for lvl, title, copy, tag, img, svg in STRATA:
    fig = (f'<div class="cx-stratum-fig"><img src="{img}" alt="{title} construction" loading="lazy" decoding="async" />{svg}</div>'
           if img else f'<div class="cx-stratum-fig" style="background:#131516">{svg}</div>')
    strata_html += (
        f'<div class="cx-stratum" data-level="{lvl}" data-testid="cx-stratum-{title.lower().replace(" ","-")}">'
        f'<div data-cx-in><div class="cx-stratum-head"><span class="cx-idx">{lvl}</span><span class="cx-tag">{tag}</span></div>'
        f'<h3 class="cx-h3">{title}</h3><p class="cx-p cx-p--s" style="margin-top:10px">{copy}</p></div>'
        f'<div data-draw>{fig}</div></div>')

ground = f'''
  <!-- ===================== GROUND / FOUNDATION ===================== -->
  <section class="cx-sec cx-cut" data-testid="cx-section-ground">
    <div class="cx-wrap">
      <div class="cx-sechead">
        <div>
          <span class="cx-idx" data-cx-in>03 / Ground</span>
          <h2 class="cx-h2" data-cx-in style="margin-top:12px">Ground / foundation interaction</h2>
        </div>
        <div>
          <p class="cx-p" data-cx-in>Foundation design begins with the geotechnical model of the site. Soil stratification, groundwater conditions, excavation geometry and engineering parameters obtained from ground investigation influence the foundation solution and below-ground construction strategy.</p>
          <p class="cx-p cx-p--s" data-cx-in style="margin-top:12px">Structural loads and geotechnical response are therefore considered as connected design problems rather than independent disciplines.</p>
        </div>
      </div>
      <div class="cx-tickrule"></div>
      <div class="cx-cut-inner">
        <div class="cx-depth"><span class="cx-lbl">Section &mdash; level</span><b data-testid="cx-depth-readout">&plusmn;0.00</b><span class="cx-lbl">Downward</span></div>
        <div class="cx-strata">{strata_html}</div>
      </div>
      <div class="cx-hatch" style="margin-top:22px"></div>
      <p class="cx-note" style="margin-top:18px">Depths, strata, groundwater conditions and foundation systems are project specific and defined by the geotechnical and structural documentation for each development.</p>
    </div>
  </section>
'''

# ============================== CONCRETE ====================================
CONC = [
    ("Specification", "Concrete requirements are defined according to structural design, exposure conditions and applicable standards."),
    ("Production &amp; conformity", "Production consistency and conformity are controlled under the applicable concrete specification framework."),
    ("Delivery", "Concrete characteristics at delivery must remain compatible with the specified placement requirements."),
    ("Placement", "Concrete is placed using a sequence appropriate to element geometry and reinforcement density."),
    ("Compaction", "Mechanical compaction reduces entrapped air and assists complete encapsulation of reinforcement without inducing segregation."),
    ("Curing", "Early-age moisture and temperature conditions are controlled to support hydration, strength development and durability."),
    ("Inspection", "Completed elements are inspected for execution quality and conformity with the intended geometry and detailing."),
]
conc_cards = ''.join(
    f'<div class="cx-stepcard" data-testid="cx-concrete-step-{i+1}"><span class="cx-idx">{i+1:02d}</span><b>{t}</b><p>{d}</p></div>'
    for i, (t, d) in enumerate(CONC))

concrete = f'''
  <!-- ===================== CONCRETE ===================== -->
  <section class="cx-conc" style="height:520vh" data-testid="cx-section-concrete">
    <div class="cx-flow-stage">
      <div class="cx-flow-head">
        <span class="cx-idx">04 / Material</span>
        <h2 class="cx-h2">Concrete performance</h2>
        <p class="cx-p cx-p--s">Specified compressive strength is only one parameter governing reinforced-concrete performance. The completed element is also affected by concrete composition, production conformity, workability, transportation time, placement sequence, compaction, curing, reinforcement congestion, concrete cover and environmental exposure.</p>
        <p class="cx-p cx-p--s">Concrete must therefore be considered as both a designed material and an executed construction process.</p>
      </div>
      <div class="cx-track">
        <div class="cx-track-line"></div>
        <div class="cx-rail" data-testid="cx-concrete-rail">{conc_cards}</div>
      </div>
      <div class="cx-flow-band"><img src="{IMG}concrete-ascast.webp" alt="As-cast reinforced-concrete surface showing formwork tie positions" loading="lazy" decoding="async" /></div>
      <div class="cx-flow-head"><p class="cx-note">Concrete specification, production and conformity are governed through TS EN 206 together with the applicable complementary national requirements. Project-specific structural documents define the required concrete class and execution criteria.</p></div>
    </div>
  </section>
'''

# ============================ REINFORCEMENT =================================
PRIN = [
    ("Continuity", "Reinforcement paths are detailed to maintain the intended transfer of internal forces between adjoining structural regions."),
    ("Anchorage", "Bars require adequate anchorage so that calculated forces can be transferred between reinforcement and surrounding concrete."),
    ("Lap &amp; connection regions", "Splices are positioned and detailed according to structural demand and the applicable design requirements."),
    ("Confinement", "Transverse reinforcement controls concrete confinement and contributes to shear resistance and ductile structural behaviour in designated regions."),
    ("Spacing", "Clear spacing must permit correct placement and compaction of concrete while maintaining the reinforcement arrangement required by design."),
    ("Concrete cover", "Cover separates reinforcement from the exposed surface and contributes to durability, fire performance and bond behaviour."),
]
prin_rows = ''.join(
    f'<div class="cx-prin" data-testid="cx-principle-{i+1}"><span class="cx-idx">A.{i+1:02d}</span><b>{t}</b><p>{d}</p></div>'
    for i, (t, d) in enumerate(PRIN))

rebar_sec = f'''
  <!-- ===================== REINFORCEMENT ===================== -->
  <section class="cx-cage" style="height:640vh" data-testid="cx-section-reinforcement">
    <div class="cx-cage-stage">
      <div>
        <span class="cx-idx">05 / Detailing</span>
        <h2 class="cx-h2" style="margin:10px 0 12px">Reinforcement detailing</h2>
        <p class="cx-p cx-p--s">Reinforcement detailing converts analytical force demand into a buildable structural system. Bar diameter alone does not define reinforcement performance; continuity, anchorage, development length, lap locations, confinement, spacing, concrete cover and constructability must work together.</p>
        <div class="cx-prin-list" style="margin-top:14px" data-testid="cx-principle-list">{prin_rows}</div>
        <p class="cx-note" style="margin-top:12px">Model shown for explanation of detailing principles. Bar diameters, spacing, lap lengths and cover are defined exclusively by project structural documentation.</p>
      </div>
      <div class="cx-cage-viz">
        <canvas class="cx-canvas" id="cxCageCanvas" data-testid="cx-cage-canvas" aria-hidden="true"></canvas>
        <div class="cx-cage-fallback"><img src="{IMG}rebar-cage.webp" alt="Reinforcement cage inside formwork before concrete placement" loading="lazy" decoding="async" /></div>
      </div>
    </div>
  </section>
'''

# =========================== EXECUTION CONTROL ==============================
EXEC = [
    ("Pre-pour control", ["approved structural drawings and reinforcement schedules", "reinforcement arrangement", "anchorage and lap zones", "concrete cover", "embedded elements and penetrations", "formwork dimensions and stability", "axes and levels", "accessibility for placement and compaction"]),
    ("Concrete placement", ["delivery conformity", "placement sequence", "continuity of supply", "layer depth", "compaction", "site and weather conditions", "sampling and records where required"]),
    ("Early age", ["curing", "protection", "formwork removal criteria", "surface inspection", "dimensional verification"]),
    ("Enclosure", ["waterproofing continuity", "fa&ccedil;ade interfaces", "insulation continuity", "glazing junctions", "service penetrations", "drainage interfaces"]),
    ("Completion", ["installation checks", "finishes", "commissioning where applicable", "snagging", "rectification", "handover control"]),
]
exec_cols = ''.join(
    f'<div class="cx-insp-col" data-testid="cx-control-{i+1}"><span class="cx-idx">C.{i+1:02d}</span>'
    f'<h3 class="cx-h3">{t}</h3><ul>' + ''.join(f'<li>{x}</li>' for x in items) + '</ul></div>'
    for i, (t, items) in enumerate(EXEC))
ELSTATES = ["Drawing", "Reinforcement", "Formwork", "Concrete", "Enclosure", "Completion"]
el_state_tabs = ''.join(f'<div class="cx-insp-state" data-testid="cx-elstate-{i+1}">{s}</div>' for i, s in enumerate(ELSTATES))
elem_svg = dwg('0 0 1200 200',
    '<g data-elstate="0"><path class="hid" d="M40 40 H210 V170 H40 Z" /><text x="40" y="192">Drawing</text></g>'
    '<g data-elstate="1"><path class="ln" d="M240 40 H410 V170 H240 Z" /><path class="hot" d="M258 56 V154 M300 56 V154 M350 56 V154 M392 56 V154 M258 70 H392 M258 110 H392 M258 150 H392" /><text x="240" y="192">Reinforcement</text></g>'
    '<g data-elstate="2"><path class="fillg" d="M440 30 H470 V180 H440 Z" /><path class="fillg" d="M580 30 H610 V180 H580 Z" /><path class="ln" d="M470 40 H580 V170 H470 Z" /><text x="440" y="192">Formwork</text></g>'
    '<g data-elstate="3"><path class="fillg" d="M660 40 H830 V170 H660 Z" /><path class="hot" d="M745 14 v20 m0 0 l-6 -10 m6 10 l6 -10" /><text x="660" y="192">Concrete</text></g>'
    '<g data-elstate="4"><path class="ln" d="M860 40 H1030 V170 H860 Z" /><path class="ln-2" d="M872 40 V170 M884 40 V170" /><text x="860" y="192">Enclosure</text></g>'
    '<g data-elstate="5"><path class="fillg" d="M1060 40 H1170 V170 H1060 Z" /><path class="dim" d="M1060 186 H1170 M1060 180 v12 M1170 180 v12" /><text x="1060" y="30">Completion</text></g>')

execution = f'''
  <!-- ===================== EXECUTION CONTROL ===================== -->
  <section class="cx-insp" style="height:560vh" data-testid="cx-section-execution">
    <div class="cx-insp-stage">
      <div class="cx-insp-head">
        <span class="cx-idx">06 / Control</span>
        <h2 class="cx-h2">Execution control</h2>
        <p class="cx-p cx-p--s">Quality assurance is most effective before work becomes concealed. Inspection therefore follows the construction sequence, with control points established before, during and after critical operations.</p>
      </div>
      <div class="cx-insp-elem">{elem_svg}</div>
      <div class="cx-insp-bar"><div class="cx-insp-states" data-testid="cx-element-states">{el_state_tabs}</div></div>
      <div class="cx-insp-rail" data-testid="cx-inspection-rail">{exec_cols}</div>
    </div>
  </section>
'''

# ============================ WATERPROOFING =================================
WP_NODES = [
    ("Foundation", "Membrane continuity begins below the structure, including the interface with the retaining system."),
    ("Basement wall", "Buried walls are treated as a continuous surface, with construction joints resolved as part of the system."),
    ("Fa&ccedil;ade junction", "Above-grade transitions, fixings and penetrations must not interrupt the boundary."),
    ("Balcony / terrace", "Falls, upstands, thresholds and drainage are coordinated with the interior floor build-up."),
    ("Roof", "The boundary closes at roof level, completing an uninterrupted envelope around the building."),
]
wp_nodes = ''.join(
    f'<div class="cx-wp-node" data-testid="cx-wp-node-{i+1}"><span class="cx-idx">{i+1:02d}</span><b>{t}</b><p>{d}</p></div>'
    for i, (t, d) in enumerate(WP_NODES))
wp_path = 'M60 470 H140 V150 H520 V470 H600'
wp_svg = dwg('0 0 660 560',
    '<path class="ln" d="M140 150 H520 V470 H140 Z" /><path class="ln-2" d="M140 230 H520 M140 310 H520 M140 390 H520" />'
    '<path class="ln" d="M520 310 H586 V330" /><path class="hid" d="M40 470 H140 M520 470 H620" />'
    + hatch(494, 50, 620, 26, -14, 18) +
    f'<path class="cx-trace" id="cxTrace" pathLength="1" d="{wp_path}" />'
    '<g id="cxTraceGap" style="opacity:0"><circle class="warn" cx="520" cy="310" r="13" /><path class="warn" d="M512 302 l16 16 M528 302 l-16 16" /></g>'
    '<text x="40" y="530">Continuous waterproofing boundary &mdash; indicative section</text>')

waterproofing = f'''
  <!-- ===================== WATERPROOFING ===================== -->
  <section class="cx-wp" style="height:480vh" data-testid="cx-section-waterproofing">
    <div class="cx-wp-stage">
      <div>
        <span class="cx-idx">07 / Envelope integrity</span>
        <h2 class="cx-h2" style="margin:10px 0 12px">Continuity of waterproofing</h2>
        <p class="cx-p cx-p--s">Waterproofing performance depends on continuity across surfaces, junctions, penetrations and changes in geometry. A membrane with high material performance cannot compensate for an unresolved termination or discontinuous interface.</p>
        <p class="cx-p cx-p--s" style="margin-top:10px">Below-grade walls, foundations, roofs, terraces, balconies and wet areas therefore require coordinated detailing of membrane continuity, drainage, thresholds, penetrations and construction joints.</p>
        <div class="cx-wp-nodes" style="margin-top:14px">{wp_nodes}</div>
        <p class="cx-wp-flag" data-testid="cx-wp-flag" style="margin-top:10px">Discontinuity at junction &mdash; detail unresolved</p>
        <p class="cx-note" style="margin-top:10px">Design and application must comply with the applicable requirements of the Binalarda Su Yal&#305;t&#305;m&#305; Y&ouml;netmeli&#287;i and the project-specific waterproofing system.</p>
      </div>
      <div class="cx-wp-viz">{wp_svg}</div>
    </div>
  </section>
'''

# ============================== ENVELOPE ====================================
ENV = [
    ("Thermal continuity", "Insulation strategy is coordinated to minimise unintended thermal discontinuities at junctions."),
    ("Moisture control", "Waterproofing, drainage and vapour behaviour are evaluated as part of the complete wall or roof build-up."),
    ("Fa&ccedil;ade interfaces", "Connections between structure, fa&ccedil;ade systems, glazing, thresholds and penetrations are treated as critical detailing zones."),
    ("Glazing", "Glass and framing performance are selected according to project-specific architectural, thermal, acoustic and environmental requirements."),
    ("Durability", "Exposure, material compatibility, drainage and maintenance access influence long-term envelope performance."),
]
env_rows = ''.join(
    f'<div class="cx-layer" data-cx-in><span class="cx-idx">L.{i+1:02d}</span><b>{t}</b><p>{d}</p></div>'
    for i, (t, d) in enumerate(ENV))
# macro detail: layers offset by a few units only, dimension annotations
lx = [180, 236, 292, 340, 392]
lw = [46, 46, 38, 32, 26]
lnames = ['Structural backing', 'Insulation layer', 'Moisture control', 'Cavity / fixing zone', 'External skin']
env_layers = ''.join(
    f'<g><rect class="fillg" x="{x}" y="60" width="{w}" height="360" /><path class="ln-2" d="M{x+w/2} 60 V420" />'
    f'<path class="dim" pathLength="1" d="M{x} 446 H{x+w} M{x} 440 v12 M{x+w} 440 v12" />'
    f'<text class="t-dim" x="{x + w/2 - 8}" y="470">L.0{i+1}</text></g>'
    for i, (x, w, n) in enumerate(zip(lx, lw, lnames)))
env_svg = dwg('0 0 620 560',
    '<path class="hid" d="M60 60 H560 M60 420 H560" />' + env_layers +
    '<path class="dim" pathLength="1" d="M120 60 V420 M114 60 h12 M114 420 h12" />'
    '<text class="t-dim" x="40" y="240">Assembly</text>'
    '<text x="60" y="40">Wall detail &mdash; indicative sequence, 1:5 reference</text>')

envelope = f'''
  <!-- ===================== ENVELOPE ===================== -->
  <section class="cx-sec cx-light" data-testid="cx-section-envelope">
    <div class="cx-wrap">
      <div class="cx-sechead">
        <div>
          <span class="cx-idx" data-cx-in>08 / Envelope</span>
          <h2 class="cx-h2" data-cx-in style="margin-top:12px">Building envelope performance</h2>
        </div>
        <p class="cx-p" data-cx-in>The building envelope controls the exchange of heat, moisture, air, sound and solar energy between interior and exterior conditions. Its performance depends not only on individual products but on the continuity of the complete assembly.</p>
      </div>
      <div class="cx-tickrule"></div>
      <div class="cx-det">
        <div class="cx-det-fig" data-draw data-start="top 82%" data-end="bottom 55%">
          {env_svg}
          <div class="cx-det-scale"><span class="cx-lbl">Macro detail</span><span class="cx-lbl">Layer sequence indicative</span></div>
        </div>
        <div class="cx-layerlist">{env_rows}
          <p class="cx-note" style="margin-top:16px">Materials, thicknesses and performance values are defined by project-specific specifications together with the applicable requirements of the Binalarda Enerji Performans&#305; Y&ouml;netmeli&#287;i and construction-product performance legislation.</p>
        </div>
      </div>
    </div>
  </section>
'''

# ============================== ACOUSTICS ===================================
PLOTS = [
    ("airborne", "Airborne sound", "Speech and media transmitted through air and through the separating assembly.",
     'M0 60 C 40 20, 80 100, 120 60 C 160 20, 200 100, 240 60 C 280 20, 320 100, 360 60 C 400 20, 440 100, 480 60'),
    ("impact", "Impact sound", "Footfall and impacts transmitted through floor build-ups and junctions.",
     'M0 60 H40 L52 12 L64 108 L76 40 L88 76 L100 60 H180 L192 20 L204 100 L216 46 L228 70 L240 60 H320 L332 24 L344 96 L356 50 L368 68 L380 60 H480'),
    ("structure", "Structure-borne sound", "Vibration transmitted through the structural system itself.",
     'M0 60 C 30 46, 60 74, 90 60 C 120 46, 150 74, 180 60 C 210 48, 240 72, 270 60 C 300 50, 330 70, 360 60 C 390 52, 420 68, 450 60 C 465 57, 472 62, 480 60'),
    ("service", "Service noise", "Equipment, ducts, risers and drainage routed close to living spaces.",
     'M0 60 L20 44 L34 76 L50 40 L66 80 L82 48 L98 72 L114 44 L130 78 L146 46 L162 74 L178 42 L194 80 L210 48 L226 72 L242 44 L258 78 L274 46 L290 74 L306 42 L322 80 L338 48 L354 72 L370 44 L386 78 L402 46 L418 74 L434 44 L450 78 L466 50 L480 60'),
]
plots = ''.join(
    f'<div class="cx-plot" data-plot="{k}" data-testid="cx-plot-{k}"><span class="cx-lbl">{t}</span>'
    f'<svg viewBox="0 0 480 120" preserveAspectRatio="none" aria-hidden="true">'
    f'<path class="base" d="M0 60 H480" /><path class="sig" d="{d}" /></svg>'
    f'<p class="cx-p cx-p--s">{desc}</p></div>'
    for k, t, desc, d in PLOTS)

acoustics = f'''
  <!-- ===================== ACOUSTICS ===================== -->
  <section class="cx-sec cx-light" style="padding-top:0" data-testid="cx-section-acoustics">
    <div class="cx-wrap">
      <div class="cx-hr"></div>
      <div class="cx-sechead">
        <div>
          <span class="cx-idx" data-cx-in>09 / Acoustics</span>
          <h2 class="cx-h2" data-cx-in style="margin-top:12px">Acoustic performance</h2>
        </div>
        <div>
          <p class="cx-p" data-cx-in>Residential acoustic performance is determined by complete construction assemblies rather than individual materials. Wall and floor build-ups, junctions, fa&ccedil;ade openings, service penetrations and mechanical equipment all affect airborne, impact and structure-borne sound transmission.</p>
          <p class="cx-p cx-p--s" data-cx-in style="margin-top:12px">Acoustic design must therefore be coordinated between architecture, building services and construction detailing.</p>
        </div>
      </div>
      <div class="cx-plots" style="margin-top:clamp(26px,4vh,52px)">{plots}</div>
      <p class="cx-note" style="margin-top:26px">Requirements follow the Binalar&#305;n G&uuml;r&uuml;lt&uuml;ye Kar&#351;&#305; Korunmas&#305; Hakk&#305;nda Y&ouml;netmelik. Performance values are properties of the executed assembly and are defined by project-specific acoustic documentation.</p>
    </div>
  </section>
'''

# ================================= MEP ======================================
MEP_LAYERS = ["Structure", "Architecture", "HVAC", "Electrical", "Water", "Drainage"]
mep_tabs = ''.join(
    f'<button class="cx-mep-tab" data-testid="cx-mep-tab-{n.lower()}">{n}</button>' for n in MEP_LAYERS)
mep_geo = {
 "Structure": '<path class="ln" d="M110 40 H510 V470 H110 Z" /><path class="ln" d="M110 140 H510 M110 240 H510 M110 340 H510" /><path class="ln" d="M286 40 H334 V470 H286 Z" />',
 "Architecture": '<path class="ln" d="M150 60 H270 V130 H150 Z M360 60 H470 V130 H360 Z M150 160 H270 V230 H150 Z M360 160 H470 V230 H360 Z M150 260 H270 V330 H150 Z M360 260 H470 V330 H360 Z M150 360 H470 V450 H150 Z" />',
 "HVAC": '<path class="ln" d="M310 450 V70" /><path class="ln" d="M310 100 H460 M310 200 H460 M310 300 H460 M310 400 H460" /><path class="ln" d="M460 100 V400" />',
 "Electrical": '<path class="ln" d="M300 450 V70" /><path class="ln" d="M300 120 H170 M300 220 H170 M300 320 H170 M300 420 H170" /><path class="ln" d="M170 120 V420" />',
 "Water": '<path class="ln" d="M320 450 V80" /><path class="ln" d="M320 150 H430 M320 250 H430 M320 350 H430" />',
 "Drainage": '<path class="ln" d="M300 80 V450" /><path class="ln" d="M300 170 H200 M300 270 H200 M300 370 H200" /><path class="ln" d="M200 170 V450" />',
}
mep_svg = dwg('0 0 620 520',
    ''.join(f'<g class="cx-mep-layer{" is-base" if n=="Structure" else ""}" data-testid="cx-mep-layer-{n.lower()}">{mep_geo[n]}</g>' for n in MEP_LAYERS) +
    '<text x="110" y="30">Coordination model &mdash; vertical shaft and horizontal distribution</text>'
    '<text x="110" y="502">Routes indicative &mdash; coordinated with structure and architecture per project</text>')

mep = f'''
  <!-- ===================== MEP ===================== -->
  <section class="cx-sec" data-testid="cx-section-mep">
    <div class="cx-wrap">
      <div class="cx-sechead">
        <div>
          <span class="cx-idx" data-cx-in>10 / Coordination</span>
          <h2 class="cx-h2" data-cx-in style="margin-top:12px">Building services coordination</h2>
        </div>
        <div>
          <p class="cx-p" data-cx-in>Mechanical, electrical and plumbing systems are spatial systems. Their routes, shafts, access zones, penetrations and equipment requirements must therefore be coordinated with architectural planning and structural design before construction.</p>
          <p class="cx-p cx-p--s" data-cx-in style="margin-top:12px">Late coordination creates unnecessary penetrations, reduced serviceability and conflicts between disciplines. Early coordination preserves both technical performance and architectural intent.</p>
        </div>
      </div>
      <div class="cx-tickrule"></div>
      <div class="cx-mep">
        <div class="cx-mep-viz">
          <div class="cx-mep-tabs" data-testid="cx-mep-tabs">{mep_tabs}</div>
          {mep_svg}
        </div>
        <div class="cx-mep-side">
          <div class="cx-mep-photo"><img src="{IMG}services-riser.webp" alt="Mechanical risers installed within a concrete service shaft" loading="lazy" decoding="async" /></div>
          <p class="cx-p cx-p--s">Shaft geometry, access zones and penetration positions are fixed early so that structural elements, fire compartmentation and architectural layouts remain consistent with the installed systems.</p>
        </div>
      </div>
    </div>
  </section>
'''

# ========================= TECHNICAL FRAMEWORK ==============================
REG = [
    ("TBDY 2018", "T&uuml;rkiye Bina Deprem Y&ouml;netmeli&#287;i", "Seismic design framework for buildings in T&uuml;rkiye."),
    ("Hazard maps", "T&uuml;rkiye Deprem Tehlike Haritas&#305;", "Site-dependent seismic hazard parameters used as input to structural design."),
    ("TS 500", "Betonarme yap&#305;lar&#305;n tasar&#305;m ve yap&#305;m kurallar&#305;", "Reinforced-concrete design and construction requirements in its applicable current edition."),
    ("TS EN 206", "TS EN 206 + applicable national complementary standard", "Concrete specification, performance, production and conformity."),
    ("Su yal&#305;t&#305;m&#305;", "Binalarda Su Yal&#305;t&#305;m&#305; Y&ouml;netmeli&#287;i", "Building waterproofing requirements."),
    ("G&uuml;r&uuml;lt&uuml;", "Binalar&#305;n G&uuml;r&uuml;lt&uuml;ye Kar&#351;&#305; Korunmas&#305; Hakk&#305;nda Y&ouml;netmelik", "Building acoustic-performance requirements."),
    ("Enerji", "Binalarda Enerji Performans&#305; Y&ouml;netmeli&#287;i", "Energy-performance requirements for buildings and building systems."),
    ("Yang&#305;n", "Binalar&#305;n Yang&#305;ndan Korunmas&#305; Hakk&#305;nda Y&ouml;netmelik", "Fire-safety, compartmentation and means-of-escape requirements."),
    ("&#304;mar", "Planl&#305; Alanlar &#304;mar Y&ouml;netmeli&#287;i", "Applicable planning and building-development framework."),
]
reg_rows = ''.join(
    f'<div class="cx-reg-row" data-testid="cx-reg-row-{i+1}"><div class="cx-reg-ref">{r}</div>'
    f'<div class="cx-reg-name">{n}</div><div class="cx-reg-scope">{s}</div></div>'
    for i, (r, n, s) in enumerate(REG))

framework = f'''
  <!-- ===================== TECHNICAL FRAMEWORK ===================== -->
  <section class="cx-sec cx-light" data-testid="cx-section-framework">
    <div class="cx-wrap">
      <div class="cx-sechead">
        <div>
          <span class="cx-idx" data-cx-in>11 / Reference</span>
          <h2 class="cx-h2" data-cx-in style="margin-top:12px">Technical framework</h2>
        </div>
        <p class="cx-p" data-cx-in>Project design and construction are developed within the regulatory and technical framework applicable in T&uuml;rkiye. The governing requirements depend on project type, approval date, site conditions and project-specific documentation.</p>
      </div>
      <div class="cx-tickrule"></div>
      <div class="cx-reg" data-testid="cx-register">
        <div class="cx-reg-title">
          <div><span>Register</span><b>Design &amp; construction references</b></div>
          <div><span>Discipline</span><b>Structural / envelope / services</b></div>
          <div><span>Status</span><b>Applicable current editions</b></div>
        </div>
        {reg_rows}
      </div>
      <p class="cx-note" style="margin-top:20px" data-testid="cx-framework-note">The latest applicable editions, amendments and project-specific approval requirements must be verified by the relevant design and engineering disciplines for each development.</p>
    </div>
  </section>
'''

# ================================ FINAL =====================================
final_svg = dwg('0 0 1100 620',
    '<g class="cx-fl" data-fl="0"><path class="ln" d="M200 120 H900 V520 H200 Z" /><path class="ln" d="M200 220 H900 M200 320 H900 M200 420 H900" /><path class="ln" d="M330 120 V520 M550 120 V520 M770 120 V520" /><text x="200" y="106">Structural linework</text></g>'
    '<g class="cx-fl" data-fl="1"><path class="hot" d="M360 150 V490 M420 150 V490 M480 150 V490" /><path class="hot" d="M360 190 H480 M360 270 H480 M360 350 H480 M360 430 H480" /><text x="360" y="140">Reinforcement geometry</text></g>'
    '<g class="cx-fl" data-fl="2"><path class="ln-2" d="M620 150 H700 V490 H620 Z" /><path class="dim" d="M620 512 H700 M620 506 v12 M700 506 v12" /><text class="t-dim" x="620" y="536">Fa&ccedil;ade section</text></g>'
    '<g class="cx-fl" data-fl="3"><path class="ln" d="M550 500 V160" /><path class="ln" d="M550 200 H840 M550 300 H840 M550 400 H840" /><text x="760" y="150">Service routes</text></g>')

final = f'''
  <!-- ===================== FINAL ===================== -->
  <section class="cx-final" data-testid="cx-final">
    <div class="cx-final-stage">
      <div class="cx-final-photo"><img src="./media/images/mercan/mercan-dis1.webp" alt="Completed Nova Konut residential building" loading="lazy" decoding="async" /></div>
      <div class="cx-final-dwg">{final_svg}</div>
      <div class="cx-final-scrim"></div>
      <div class="cx-final-copy">
        <span class="cx-lbl cx-lbl--warm">12 / Result</span>
        <h2 class="cx-h1" data-testid="cx-final-title">Calculated. Coordinated. Constructed.</h2>
        <p class="cx-p">A completed residence is the visible result of thousands of decisions that are no longer visible after handover. Structural analysis, detailing, material selection, construction sequence and inspection must remain coordinated throughout the process for the building to perform as designed.</p>
        <div class="cx-sign"><b>Nova Konut</b><span>Construction &amp; Engineering</span></div>
      </div>
    </div>
  </section>
'''

scripts = '''
  <script src="js/script.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/ScrollTrigger.min.js"></script>
  <script type="module" src="js/construction.js"></script>
</body>
</html>
'''

out = (head + '\n' + hero + structural + seismic + ground + concrete + rebar_sec +
       execution + waterproofing + envelope + acoustics + mep + framework + final +
       '\n' + footer + '\n' + scripts)

SRC.write_text(out)
print('written', len(out), 'chars')
print('east-west refs:', out.lower().count('east-west'), out.count('/ew/'))
print('sections:', out.count('data-testid="cx-section') + 3)
print('header/footer present:', 'site-header' in out, 'site-footer' in out, 'construction.html' in out)
