#!/usr/bin/env python3
"""Replace Construction sections 05-12 with the approved final copy.
Existing visuals (SVG / canvas / images) are extracted from the current page
and re-inserted unchanged."""
import re
import pathlib

P = pathlib.Path('/app/frontend/construction.html')
src = P.read_text(encoding='utf-8')


def slice_between(start_sub, end_sub, after=0):
    a = src.index(start_sub, after)
    b = src.index(end_sub, a)
    return src[a:b].rstrip('\n')


def line_with(sub):
    a = src.index(sub)
    s = src.rindex('\n', 0, a) + 1
    e = src.index('\n', a)
    return src[s:e].strip()


# ---------- extract existing visual blocks (unchanged) ----------
cage_viz = slice_between('<div class="cx-cage-viz">', '\n    </div>\n  </section>')
insp_elem = line_with('class="cx-insp-elem"')
insp_bar = line_with('class="cx-insp-bar"')
wp_viz = line_with('class="cx-wp-viz"')
env_fig = slice_between('<div class="cx-det-fig"', '\n        <div class="cx-layerlist">')
plots = line_with('class="cx-plots"')
plots = re.sub(r'<p class="cx-p cx-p--s">.*?</p>', '', plots)
mep_viz = slice_between('<div class="cx-mep-viz">', '\n        <div class="cx-mep-side">')
mep_photo = line_with('class="cx-mep-photo"')
fin_photo = line_with('class="cx-final-photo"')
fin_dwg = line_with('class="cx-final-dwg"')
fin_scrim = line_with('class="cx-final-scrim"')

for name, blk in [('cage_viz', cage_viz), ('insp_elem', insp_elem), ('wp_viz', wp_viz),
                  ('env_fig', env_fig), ('mep_viz', mep_viz), ('fin_dwg', fin_dwg)]:
    assert '<svg' in blk or 'canvas' in blk, name

# ---------- helpers ----------
def prin(idx, tid, title, paras):
    body = ''.join('<p>%s</p>' % p for p in paras)
    return ('<div class="cx-prin" data-testid="%s"><span class="cx-idx">%s</span><b>%s</b>'
            '<div class="cx-prin-d">%s</div></div>' % (tid, idx, title, body))


def node(idx, tid, title, paras):
    body = ''.join('<p>%s</p>' % p for p in paras)
    return ('<div class="cx-wp-node" data-testid="%s"><span class="cx-idx">%s</span><b>%s</b>'
            '<div class="cx-wp-node-d">%s</div></div>' % (tid, idx, title, body))


def col(idx, tid, title, lead, listlead, bullets, close=None):
    out = ['<div class="cx-insp-col" data-testid="%s"><span class="cx-idx">%s</span>'
           '<h3 class="cx-h3">%s</h3>' % (tid, idx, title)]
    out.append('<p class="cx-p cx-p--s">%s</p>' % lead)
    if listlead:
        out.append('<p class="cx-p cx-p--s cx-insp-lead">%s</p>' % listlead)
    if bullets:
        out.append('<ul>' + ''.join('<li>%s</li>' % b for b in bullets) + '</ul>')
    if close:
        out.append('<p class="cx-p cx-p--s" style="margin-top:8px">%s</p>' % close)
    out.append('</div>')
    return ''.join(out)


def layer(idx, title, paras, cls='cx-layer'):
    body = ''.join('<p>%s</p>' % p for p in paras)
    return ('<div class="%s" data-cx-in><span class="cx-idx">%s</span><b>%s</b>%s</div>'
            % (cls, idx, title, body))


def grp(title, paras):
    body = ''.join('<p>%s</p>' % p for p in paras)
    return '<div class="cx-fac cx-fac--nx" data-cx-in><b>%s</b>%s</div>' % (title, body)


def reg(i, ref, name, scope):
    nm = '<div class="cx-reg-name">%s</div>' % name if name else ''
    return ('<div class="cx-reg-row" data-testid="cx-reg-row-%d"><div class="cx-reg-h">'
            '<div class="cx-reg-ref">%s</div>%s</div>'
            '<div class="cx-reg-scope">%s</div></div>' % (i, ref, nm, scope))


# =========================================================
# 05 / Detailing
# =========================================================
S05 = '''  <!-- ===================== REINFORCEMENT ===================== -->
  <section class="cx-cage" style="height:680vh" data-testid="cx-section-reinforcement">
    <div class="cx-cage-stage">
      <div class="cx-copywin"><div class="cx-copymove">
        <span class="cx-idx">05 / Detailing</span>
        <h2 class="cx-h2" style="margin:10px 0 10px">Reinforcement detailing</h2>
        <p class="cx-lbl" style="margin:0 0 10px">Structural performance depends on how calculated resistance is physically detailed.</p>
        <p class="cx-p cx-p--s">Reinforcement detailing translates the internal forces and deformation demands obtained from structural analysis into a constructible reinforced-concrete system. Bar area or diameter alone does not define structural performance. Continuity, development and anchorage, lap and mechanical connection regions, transverse reinforcement, confinement, bar spacing, concrete cover and the interaction between reinforcement and concrete must be resolved as an integrated detailing system.</p>
        <p class="cx-p cx-p--s" style="margin-top:9px">Under seismic actions, detailing assumes particular importance in regions where significant cyclic deformation and force transfer are expected. Longitudinal and transverse reinforcement are therefore arranged not only to provide the required resistance, but also to support the deformation capacity, confinement, shear resistance and force-transfer mechanisms assumed in structural design.</p>
        <div class="cx-prin-list" style="margin-top:14px" data-testid="cx-principle-list">__PRIN__</div>
        <div class="cx-endnote" style="margin-top:14px" data-testid="cx-seismic-detailing-principle">
          <span class="cx-lbl cx-lbl--warm">Seismic detailing principle</span>
          <p class="cx-note" style="margin-top:6px">For reinforced-concrete structures designed within the Turkish seismic framework, detailing is developed in accordance with the applicable provisions of TBDY 2018, together with the relevant requirements of TS 500, TS 708 and TS EN 13670.</p>
          <p class="cx-note" style="margin-top:6px">The model shown is conceptual. Bar diameters, reinforcement ratios, spacing, confinement regions, anchorage lengths, splice positions and concrete cover are defined exclusively by the approved structural design and project-specific detailing.</p>
        </div>
      </div></div>
      __VIZ__
    </div>
  </section>'''

PRIN = ''.join([
    prin('A.01', 'cx-principle-1', 'Continuity &amp; load transfer', [
        'Reinforcement is arranged to maintain the intended transfer of tensile, compressive and shear-related actions between adjoining structural regions.',
        'Changes in member geometry, intersections between structural elements and discontinuities in reinforcement require explicit detailing so that the load path assumed in analysis can be physically developed in the completed structure.']),
    prin('A.02', 'cx-principle-2', 'Development &amp; anchorage', [
        'Reinforcing bars require sufficient development and anchorage to transfer force between steel and surrounding concrete through bond.',
        'Required anchorage geometry and development length depend on parameters including bar diameter, reinforcement type, concrete properties, stress condition, confinement and the applicable reinforced-concrete detailing provisions.',
        'Anchorage must therefore be resolved as part of the structural force-transfer mechanism rather than treated as a geometric termination of reinforcement.']),
    prin('A.03', 'cx-principle-3', 'Splices &amp; connection regions', [
        'Lap splices, mechanical couplers and welded connections, where permitted, are positioned and detailed according to the force demand and applicable structural requirements.',
        'Connection regions are selected so that reinforcement continuity is maintained without creating inappropriate concentrations of discontinuity or compromising the intended deformation mechanism of the structural element.',
        'Splice type, location and length are consequently project-specific and cannot be defined independently of the structural design.']),
    prin('A.04', 'cx-principle-4', 'Transverse reinforcement &amp; confinement', [
        'Transverse reinforcement performs multiple structural functions, including confinement of the concrete core, restraint of longitudinal reinforcement, contribution to shear resistance and support of ductile behaviour in designated critical regions.',
        'In columns and other regions subject to seismic detailing requirements, transverse reinforcement geometry and spacing vary according to the structural role and demand of the region. Column end regions, beam-column joints and other critical zones may therefore require substantially different detailing from less critical regions of the same member.']),
    prin('A.05', 'cx-principle-5', 'Spacing &amp; constructability', [
        'Reinforcement spacing must satisfy both structural requirements and the physical requirements of concrete construction.',
        'Clear distances between bars must allow reinforcement to be positioned within tolerance while permitting concrete to flow around the reinforcement and allowing effective placement and consolidation.',
        'High reinforcement density is therefore treated as a constructability condition as well as a structural detailing problem.']),
    prin('A.06', 'cx-principle-6', 'Concrete cover', [
        'Concrete cover establishes the position of reinforcement relative to the concrete surface and contributes to durability, bond, fire performance and dimensional control.',
        'Required cover depends on the structural element, reinforcement type, environmental exposure, execution tolerance and applicable design requirements.',
        'Cover is therefore controlled through both design documentation and site execution rather than treated as a nominal geometric allowance.']),
])
S05 = S05.replace('__PRIN__', PRIN).replace('__VIZ__', cage_viz.strip())

# =========================================================
# 06 / Control
# =========================================================
COLS = ''.join([
    col('C.01', 'cx-control-1', 'Document &amp; setting-out control',
        'Before execution, the applicable approved drawings, details, schedules and technical specifications are coordinated with site geometry.',
        'Control includes, as applicable:',
        ['structural drawings and reinforcement schedules', 'architectural and services interfaces',
         'structural axes and reference levels', 'dimensions and openings',
         'embedded components and penetrations', 'construction and movement joints',
         'project-specific execution requirements']),
    col('C.02', 'cx-control-2', 'Pre-pour structural control',
        'Before concrete placement, reinforcement and formwork conditions are verified while corrective action remains possible.',
        'Control includes, as applicable:',
        ['reinforcement arrangement and continuity', 'bar diameters and quantities',
         'anchorage and splice regions', 'transverse reinforcement and confinement',
         'reinforcement spacing and congestion', 'concrete cover and spacers',
         'embedded elements and sleeves', 'formwork geometry and stability',
         'construction-joint preparation', 'accessibility for placement and consolidation']),
    col('C.03', 'cx-control-3', 'Concrete execution',
        'During concrete placement, the objective is to preserve the specified fresh-concrete properties and achieve continuous, adequately consolidated concrete throughout the element.',
        'Control includes, as applicable:',
        ['delivery documentation and conformity', 'fresh-concrete condition', 'placement sequence',
         'continuity of supply', 'layer thickness and placement method',
         'consolidation access and procedure', 'environmental and weather conditions',
         'sampling, testing and execution records where required']),
    col('C.04', 'cx-control-4', 'Early-age control',
        'Concrete remains sensitive to execution conditions after placement.',
        'Early-age control therefore considers:',
        ['curing and moisture retention', 'temperature and environmental exposure',
         'protection from premature drying or damage', 'formwork and support removal criteria',
         'surface condition', 'dimensional conformity',
         'identified execution defects and their engineering assessment where required']),
    col('C.05', 'cx-control-5', 'Enclosure &amp; interface control',
        'Building-envelope performance is controlled at interfaces before subsequent work conceals them.',
        'Verification includes, as applicable:',
        ['waterproofing continuity', 'terminations and upstands', 'fa&ccedil;ade interfaces',
         'thermal-insulation continuity', 'glazing interfaces', 'penetrations', 'drainage paths',
         'construction and movement joints', 'protection of completed waterproofing layers']),
    col('C.06', 'cx-control-6', 'Completion &amp; verification',
        'Completion control verifies that the constructed system corresponds to the intended technical configuration.',
        'This may include:',
        ['installation verification', 'functional testing',
         'commissioning of building systems where applicable', 'dimensional and visual inspections',
         'rectification of identified nonconformities', 'completion records',
         'handover documentation']),
])

S06 = '''  <!-- ===================== EXECUTION CONTROL ===================== -->
  <section class="cx-insp" style="height:660vh" data-testid="cx-section-execution">
    <div class="cx-insp-stage">
      <div class="cx-insp-head">
        <span class="cx-idx">06 / Control</span>
        <h2 class="cx-h2">Execution control</h2>
        <p class="cx-lbl" style="margin:2px 0 6px">Design intent must remain verifiable during construction.</p>
        <p class="cx-p cx-p--s">Structural and building-performance requirements cannot be verified only after construction is complete. Many critical conditions become concealed as work progresses; reinforcement is enclosed by concrete, waterproofing is covered by subsequent layers and service penetrations become embedded within finished assemblies.</p>
        <p class="cx-p cx-p--s">Execution control is therefore organised around the construction sequence, with verification carried out at stages where geometry, materials, interfaces and workmanship remain accessible for inspection.</p>
      </div>
      __ELEM__
      __BAR__
      <div class="cx-insp-rail" data-testid="cx-inspection-rail">__COLS__</div>
      <p class="cx-note cx-insp-close" data-testid="cx-execution-close">Inspection is therefore treated as a continuous verification process rather than a final visual check.</p>
    </div>
  </section>'''
S06 = (S06.replace('__ELEM__', insp_elem).replace('__BAR__', insp_bar)
       .replace('__COLS__', COLS))

# =========================================================
# 07 / Waterproofing
# =========================================================
NODES = ''.join([
    node('01', 'cx-wp-node-1', 'Below-grade foundation interface', [
        'Waterproofing below and around the below-grade structure is developed according to the applicable water exposure, foundation configuration, groundwater conditions and construction sequence.',
        'Continuity must be maintained between horizontal and vertical waterproofing zones and at interfaces with foundations, basement walls and excavation-support conditions.']),
    node('02', 'cx-wp-node-2', 'Basement walls &amp; joints', [
        'Below-grade walls are treated as part of a continuous water-management system.',
        'Construction joints, movement joints, penetrations and wall-to-foundation interfaces require coordinated detailing because these discontinuities constitute critical potential leakage paths.']),
    node('03', 'cx-wp-node-3', 'Penetrations &amp; terminations', [
        'Pipes, sleeves, fixings, fa&ccedil;ade interfaces and other penetrations interrupt otherwise continuous surfaces.',
        'Each penetration and termination must therefore be resolved with a compatible waterproofing detail rather than treated as an independent installation.']),
    node('04', 'cx-wp-node-4', 'Balconies &amp; terraces', [
        'Balconies and terraces require coordinated control of waterproofing, falls, drainage, thresholds, upstands and fa&ccedil;ade interfaces.',
        'Surface geometry must direct water toward the intended drainage system without creating unintended ponding or vulnerable transitions at internal floor levels.']),
    node('05', 'cx-wp-node-5', 'Roof systems', [
        'Roof waterproofing is developed as a continuous system incorporating the roof field, perimeter details, upstands, penetrations and drainage points.',
        'The completed boundary must remain continuous while accommodating the environmental and dimensional conditions applicable to the roof assembly.']),
])

S07 = '''  <!-- ===================== WATERPROOFING ===================== -->
  <section class="cx-wp" style="height:560vh" data-testid="cx-section-waterproofing">
    <div class="cx-wp-stage">
      <div class="cx-copywin"><div class="cx-copymove">
        <span class="cx-idx">07 / Waterproofing</span>
        <h2 class="cx-h2" style="margin:10px 0 10px">Waterproofing continuity</h2>
        <p class="cx-lbl" style="margin:0 0 10px">Waterproofing is a continuous boundary, not an isolated material layer.</p>
        <p class="cx-p cx-p--s">Waterproofing performance depends on the continuity of the complete system across horizontal and vertical surfaces, construction joints, movement joints, penetrations, terminations, thresholds and changes in geometry.</p>
        <p class="cx-p cx-p--s" style="margin-top:9px">Material performance alone cannot compensate for a discontinuity in detailing or execution. Water pressure, drainage conditions, substrate movement, interface geometry and the compatibility of adjoining materials must therefore be considered together.</p>
        <div class="cx-wp-nodes" style="margin-top:14px">__NODES__</div>
        <p class="cx-wp-flag" data-testid="cx-wp-flag" style="margin-top:10px">Discontinuity at junction &mdash; detail unresolved</p>
        <div class="cx-endnote" style="margin-top:10px" data-testid="cx-water-management-principle">
          <span class="cx-lbl cx-lbl--warm">Water management principle</span>
          <p class="cx-note" style="margin-top:6px">Waterproofing design and execution are developed in accordance with the applicable requirements of the Binalarda Su Yal\u0131t\u0131m\u0131 Y\u00f6netmeli\u011fi, relevant standards, project-specific exposure conditions and the selected waterproofing system.</p>
          <p class="cx-note" style="margin-top:6px">System selection and detailing consider the relationship between water exposure, drainage, substrate, structural movement, penetrations and material compatibility.</p>
        </div>
      </div></div>
      __VIZ__
    </div>
  </section>'''
S07 = S07.replace('__NODES__', NODES).replace('__VIZ__', wp_viz)

# =========================================================
# 08 / Envelope
# =========================================================
LAYERS = ''.join([
    layer('L.01', 'Thermal continuity', [
        'Thermal insulation is developed as a continuous layer wherever practicable, with particular attention to interfaces between fa&ccedil;ades, slabs, balconies, roofs, foundations, openings and structural elements.',
        'Geometric and material discontinuities are evaluated because localised thermal bridging can increase heat transfer and alter internal surface temperatures.']),
    layer('L.02', 'Moisture &amp; condensation control', [
        'Moisture control considers both liquid-water exposure and water-vapour behaviour within the building assembly.',
        'Layer sequence, drainage, vapour resistance, internal and external environmental conditions and local surface temperatures influence the risk of moisture accumulation and condensation.']),
    layer('L.03', 'Air &amp; weather boundaries', [
        'The continuity of air-control and weather-resisting layers is coordinated across joints, fa&ccedil;ade interfaces, windows, doors and penetrations.',
        'Uncontrolled air leakage can influence energy performance, thermal comfort, moisture transport and acoustic behaviour and is therefore considered as an assembly-level property.']),
    layer('L.04', 'Glazing &amp; openings', [
        'Glazing and framing systems are selected according to project-specific thermal, solar, acoustic, structural and environmental requirements.',
        'Their performance depends on the complete opening assembly, including glass composition, framing, spacers, seals, installation tolerances and interfaces with the surrounding envelope.']),
    layer('L.05', 'Interface engineering', [
        'Transitions between different systems are treated as critical technical zones.',
        'Structure-to-fa&ccedil;ade connections, parapets, roof edges, thresholds, glazing junctions, service penetrations and waterproofing terminations require coordinated details capable of maintaining the intended environmental-control layers.']),
    layer('L.06', 'Durability &amp; maintainability', [
        'Long-term envelope performance depends on environmental exposure, material compatibility, drainage, movement accommodation, workmanship and access for inspection and maintenance.',
        'Durability is therefore considered at both material and assembly level.']),
])

S08 = '''  <!-- ===================== ENVELOPE ===================== -->
  <section class="cx-sec cx-light" data-testid="cx-section-envelope">
    <div class="cx-wrap">
      <div class="cx-sechead">
        <div>
          <span class="cx-idx" data-cx-in>08 / Envelope</span>
          <h2 class="cx-h2" data-cx-in style="margin-top:12px">Building envelope performance</h2>
        </div>
        <div>
          <p class="cx-lbl" data-cx-in>The building envelope functions as a coupled environmental control system.</p>
          <p class="cx-p" data-cx-in style="margin-top:12px">The envelope regulates the transfer of heat, moisture, air, sound and solar energy between internal and external environments. Its behaviour is determined by the combined performance of opaque construction, glazing, interfaces, penetrations and junctions rather than by the nominal properties of individual products considered in isolation.</p>
          <p class="cx-p cx-p--s" data-cx-in style="margin-top:12px">Performance therefore depends on continuity between thermal, moisture, air-control and weather-protection layers across the complete building boundary.</p>
        </div>
      </div>
      <div class="cx-tickrule"></div>
      <div class="cx-det">
        __FIG__
        <div class="cx-layerlist">__LAYERS__
          <p class="cx-note" style="margin-top:16px" data-testid="cx-envelope-note">Envelope design is developed within the applicable requirements of the Binalarda Enerji Performans\u0131 Y\u00f6netmeli\u011fi, TS 825, applicable product standards and project-specific architectural and engineering performance criteria.</p>
        </div>
      </div>
    </div>
  </section>'''
S08 = S08.replace('__FIG__', env_fig.strip()).replace('__LAYERS__', LAYERS)

# =========================================================
# 09 / Acoustics
# =========================================================
ACO = ''.join([
    layer('A.01', 'Airborne sound insulation', [
        'Airborne sound generated by speech, media and other sources can be transmitted through separating walls, floors, fa&ccedil;ades, doors and indirect flanking paths.',
        'Acoustic separation therefore depends on the complete construction assembly and its interfaces.']),
    layer('A.02', 'Impact sound', [
        'Footfall and other direct impacts generate vibration within floor assemblies and the supporting structure.',
        'Floor build-up, resilient layers, junction details and structural continuity influence the resulting impact-sound transmission to adjoining spaces.']),
    layer('A.03', 'Flanking transmission', [
        'Sound may bypass the principal separating element through adjoining floors, walls, fa&ccedil;ades, ceilings or structural connections.',
        'Junction design is therefore integral to acoustic performance and cannot be evaluated solely from the laboratory rating of the separating element.']),
    layer('A.04', 'Structure-borne vibration', [
        'Mechanical excitation can propagate through reinforced-concrete and other structural elements before being radiated as sound elsewhere in the building.',
        'Equipment supports, structural connections and isolation measures are therefore coordinated according to the nature of the vibration source.']),
    layer('A.05', 'Building-services noise', [
        'Mechanical equipment, pumps, fans, ducts, pipes, drainage stacks and risers can generate both airborne and structure-borne noise.',
        'Equipment location, routing, isolation, shaft construction and penetration detailing are coordinated with the acoustic requirements of adjacent occupied spaces.']),
])

S09 = '''  <!-- ===================== ACOUSTICS ===================== -->
  <section class="cx-sec cx-light" style="padding-top:0" data-testid="cx-section-acoustics">
    <div class="cx-wrap">
      <div class="cx-hr"></div>
      <div class="cx-sechead">
        <div>
          <span class="cx-idx" data-cx-in>09 / Acoustics</span>
          <h2 class="cx-h2" data-cx-in style="margin-top:12px">Acoustic performance</h2>
        </div>
        <div>
          <p class="cx-lbl" data-cx-in>Acoustic performance is an assembly and transmission-path property.</p>
          <p class="cx-p" data-cx-in style="margin-top:12px">Sound transmission through residential buildings is governed by complete wall, floor, ceiling and fa&ccedil;ade assemblies together with their junctions, openings, penetrations and connections to the structural system.</p>
          <p class="cx-p cx-p--s" data-cx-in style="margin-top:12px">Nominal performance of an individual material cannot therefore be interpreted as the acoustic performance of the completed construction.</p>
        </div>
      </div>
      __PLOTS__
      <div class="cx-alist" data-testid="cx-acoustic-list">__ACO__</div>
      <p class="cx-note" style="margin-top:26px" data-testid="cx-acoustics-note">Acoustic design is developed within the applicable requirements of the Binalar\u0131n G\u00fcr\u00fclt\u00fcye Kar\u015f\u0131 Korunmas\u0131 Hakk\u0131nda Y\u00f6netmelik and project-specific acoustic design criteria. Required performance is associated with the completed construction and its transmission paths rather than with individual materials in isolation.</p>
    </div>
  </section>'''
S09 = S09.replace('__PLOTS__', plots).replace('__ACO__', ACO)

# =========================================================
# 10 / Coordination
# =========================================================
GRPS = ''.join([
    grp('Structure', [
        'Penetrations, openings, sleeves and embedded components are coordinated with the structural design before execution.',
        'Uncontrolled cutting or drilling of structural elements after construction is not treated as an acceptable substitute for multidisciplinary coordination.']),
    grp('HVAC', [
        'Duct routes, equipment locations, fresh-air and exhaust paths, condensate drainage, access requirements and vibration interfaces are coordinated with the architecture and structure.']),
    grp('Electrical', [
        'Cable routes, containment, distribution equipment, risers and embedded components are integrated with the spatial and fire-safety requirements of the building.']),
    grp('Water', [
        'Domestic-water distribution, plant, valves and access zones are coordinated to maintain installation accessibility and minimise conflicts with structural and architectural systems.']),
    grp('Drainage', [
        'Gravity drainage requires particular attention to slopes, vertical stacks, connection geometry, acoustic treatment, penetrations and coordination with structural floor zones.']),
    grp('Fire &amp; life-safety interfaces', [
        'Service penetrations through fire-resisting construction require coordinated treatment so that the intended compartmentation and fire resistance of the assembly are preserved.']),
])

S10 = '''  <!-- ===================== MEP ===================== -->
  <section class="cx-sec" data-testid="cx-section-mep">
    <div class="cx-wrap">
      <div class="cx-sechead">
        <div>
          <span class="cx-idx" data-cx-in>10 / Coordination</span>
          <h2 class="cx-h2" data-cx-in style="margin-top:12px">Building services coordination</h2>
        </div>
        <div>
          <p class="cx-lbl" data-cx-in>Building services are integrated spatial and performance systems.</p>
          <p class="cx-p" data-cx-in style="margin-top:12px">Mechanical, electrical, plumbing, fire-safety and communication systems require defined routes, shafts, equipment zones, maintenance clearances and penetrations throughout the building.</p>
          <p class="cx-p cx-p--s" data-cx-in style="margin-top:12px">These requirements are coordinated with the architectural and structural systems before construction so that service distribution does not compromise structural elements, fire compartmentation, waterproofing, acoustic separation or maintainability.</p>
        </div>
      </div>
      <div class="cx-tickrule"></div>
      <div class="cx-mep">
        __VIZ__
        <div class="cx-mep-side">
          __PHOTO__
        </div>
      </div>
      <div class="cx-facs cx-coordlist" style="margin-top:clamp(24px,3.4vh,50px)" data-testid="cx-coordination-list">__GRPS__</div>
      <div class="cx-endnote" style="margin-top:clamp(20px,2.6vh,34px)" data-testid="cx-coordination-principle">
        <span class="cx-lbl cx-lbl--warm">Coordination principle</span>
        <p class="cx-note" style="margin-top:8px">The objective of multidisciplinary coordination is not merely geometric clash avoidance. It is to maintain the structural, environmental, acoustic, fire-safety and operational performance of the building while preserving access for installation, inspection and maintenance.</p>
      </div>
    </div>
  </section>'''
S10 = (S10.replace('__VIZ__', mep_viz.strip()).replace('__PHOTO__', mep_photo)
       .replace('__GRPS__', GRPS))

# =========================================================
# 11 / Reference
# =========================================================
REGS = ''.join([
    reg(1, 'TBDY 2018', 'T\u00fcrkiye Bina Deprem Y\u00f6netmeli\u011fi',
        'Governing seismic-design framework for buildings in T\u00fcrkiye.'),
    reg(2, 'T\u00fcrkiye Deprem Tehlike Haritas\u0131', '',
        'Site-dependent seismic hazard parameters forming part of the seismic-design input.'),
    reg(3, 'TS 500', 'Betonarme Yap\u0131lar\u0131n Tasar\u0131m ve Yap\u0131m Kurallar\u0131',
        'General reinforced-concrete structural design and detailing provisions, applied together with the specific requirements of TBDY 2018.'),
    reg(4, 'TS 708', 'Betonarme i\u00e7in Donat\u0131 \u00c7eli\u011fi',
        'Requirements applicable to reinforcing steels used in reinforced-concrete construction.'),
    reg(5, 'TS EN 13670', 'Execution of Concrete Structures',
        'Execution requirements applicable to concrete structures together with project-specific execution documentation.'),
    reg(6, 'TS EN 206+A2 / TS 13515', 'Concrete &mdash; Specification, Performance, Production and Conformity / Complementary National Requirements',
        'Framework governing concrete specification, production, performance and conformity within the applicable Turkish implementation.'),
    reg(7, 'Binalarda Su Yal\u0131t\u0131m\u0131 Y\u00f6netmeli\u011fi', '',
        'Requirements governing waterproofing design and execution for applicable building elements and exposure conditions.'),
    reg(8, 'Binalar\u0131n G\u00fcr\u00fclt\u00fcye Kar\u015f\u0131 Korunmas\u0131 Hakk\u0131nda Y\u00f6netmelik', '',
        'Regulatory framework for acoustic protection and building acoustic performance.'),
    reg(9, 'Binalarda Enerji Performans\u0131 Y\u00f6netmeli\u011fi / TS 825', '',
        'Framework governing building energy performance and thermal-envelope requirements.'),
    reg(10, 'Binalar\u0131n Yang\u0131ndan Korunmas\u0131 Hakk\u0131nda Y\u00f6netmelik', '',
        'Fire-safety requirements including compartmentation, escape, fire resistance and building-services interfaces.'),
    reg(11, 'Planl\u0131 Alanlar \u0130mar Y\u00f6netmeli\u011fi', '',
        'Applicable planning and building-development provisions within its regulatory scope.'),
])

S11 = '''  <!-- ===================== TECHNICAL FRAMEWORK ===================== -->
  <section class="cx-sec cx-light" data-testid="cx-section-framework">
    <div class="cx-wrap">
      <div class="cx-sechead">
        <div>
          <span class="cx-idx" data-cx-in>11 / Reference</span>
          <h2 class="cx-h2" data-cx-in style="margin-top:12px">Technical framework</h2>
        </div>
        <p class="cx-p" data-cx-in>Project design and construction are developed within the regulatory and technical framework applicable in T&uuml;rkiye. Applicable requirements depend on building characteristics, site conditions, structural system, project approval date and the technical scope of each discipline.</p>
      </div>
      <div class="cx-tickrule"></div>
      <div class="cx-reg" data-testid="cx-register">__REGS__</div>
      <p class="cx-note" style="margin-top:20px" data-testid="cx-framework-note">The applicable editions, amendments, referenced standards, project-specific technical specifications and approval requirements are verified separately by the responsible design and engineering disciplines for each development.</p>
    </div>
  </section>'''
S11 = S11.replace('__REGS__', REGS)

# =========================================================
# 12 / Result
# =========================================================
S12 = '''  <!-- ===================== FINAL ===================== -->
  <section class="cx-final" data-testid="cx-final">
    <div class="cx-final-stage">
      __PHOTO__
      __DWG__
      __SCRIM__
      <div class="cx-final-copy">
        <span class="cx-lbl cx-lbl--warm">12 / Result</span>
        <h2 class="cx-h1" data-testid="cx-final-title">Calculated. Detailed. Coordinated. Constructed.</h2>
        <p class="cx-p">A completed building is the physical result of engineering decisions that progressively become concealed during construction.</p>
        <p class="cx-p cx-p--s">Ground conditions, structural analysis, reinforcement detailing, material specification, concrete execution, waterproofing continuity, envelope interfaces, acoustic assemblies and building-services coordination must therefore remain consistent through design, construction and verification.</p>
        <p class="cx-p cx-p--s">Performance is not created by any single material or structural element. It emerges from the compatibility of the complete system &mdash; from the assumptions established in analysis to the details ultimately executed on site.</p>
        <div class="cx-sign"><b>Nova Konut</b><span>Construction &amp; Engineering</span></div>
      </div>
    </div>
  </section>'''
S12 = (S12.replace('__PHOTO__', fin_photo).replace('__DWG__', fin_dwg)
       .replace('__SCRIM__', fin_scrim))

# ---------- assemble ----------
new_block = '\n\n'.join([S05, S06, S07, S08, S09, S10, S11, S12]) + '\n\n'


def esc(s):
    out = []
    for ch in s:
        out.append(ch if ord(ch) < 128 else '&#%d;' % ord(ch))
    return ''.join(out)


new_block = esc(new_block)

start = src.index('  <!-- ===================== REINFORCEMENT ===================== -->')
end = src.index('  <footer class="site-footer">')
out = src[:start] + new_block + src[end:]
P.write_text(out, encoding='utf-8')
print('sections 05-12 replaced; bytes %d -> %d' % (len(src), len(out)))
