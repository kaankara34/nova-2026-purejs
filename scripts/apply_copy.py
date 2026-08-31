"""One-off: replace visible copy in scripts/design_main.html by line, structure untouched."""
import pathlib

p = pathlib.Path(__file__).parent / "design_main.html"
lines = p.read_text(encoding="utf-8").split("\n")

new = {
9: '          <h1 class="dz-h1" data-dz>Architecture shaped by <br />proportion.</h1>',
20: '          <p class="dz-lead" data-dz>A residence is defined long before its finishes are selected. It begins with proportion, orientation, daylight, circulation and the relationship between one space and the next. At Nova, these fundamentals establish the framework from which every architectural decision develops.</p>',
21: '          <p class="dz-p" data-dz>Plans are shaped around the way spaces are actually inhabited — balancing openness with privacy, generous daylight with thermal comfort, and architectural clarity with the practical rhythms of everyday life.</p>',
31: '          <h2 class="dz-h2" id="dz-t-architecture" data-dz>Architecture with <br />purpose.</h2>',
32: '          <p class="dz-p" data-dz>Architecture at Nova is developed through proportion, structural logic, spatial sequence and long-term usability. Rather than relying on visual excess, each building is resolved through disciplined geometry, efficient circulation and a measured relationship between interior, façade and urban context.</p>',
33: '          <p class="dz-p" data-dz>Façades respond to orientation, scale, privacy and environmental exposure. Inside, layouts prioritise usable dimensions, clear circulation and natural light. The objective is architecture that remains functional, relevant and visually composed long after completion.</p>',
73: '          <p class="dz-p" data-dz>Residential planning begins with the relationship between spaces rather than room dimensions in isolation. Sightlines, circulation routes, furniture zones, thresholds and transitions are considered collectively so the plan functions as a coherent whole.</p>',
74: '          <p class="dz-p" data-dz>Living spaces are given continuity while private areas retain separation and acoustic calm. Structural grids, service zones and architectural planning are coordinated from the outset to reduce unnecessary compromise in the finished residence.</p>',
89: '          <p class="dz-statement dz-statement--s" data-dz>The result is architecture that feels intuitive rather than imposed.</p>',
110: '          <p class="dz-p" data-dz>Natural light is treated as part of the architecture itself. Window proportions, façade openings, room depths and orientation are developed together to create interiors that respond naturally to changing daylight conditions throughout the day.</p>',
111: '          <p class="dz-p" data-dz>Rather than maximising glazing indiscriminately, openings are considered according to view, privacy, solar exposure and thermal comfort. After dark, integrated architectural lighting continues the same hierarchy through concealed coves, joinery lighting and precisely directed illumination.</p>',
121: '        <h2 class="dz-h2" id="dz-t-materials" data-dz>Materials selected for <br />performance and character.</h2>',
131: '          <p class="dz-p" data-dz>Material selection is guided by durability, tactile quality and architectural coherence rather than novelty. Natural stone, timber, metal, leather and glass are considered not only for their appearance at completion, but also for their behaviour, maintenance requirements and ageing characteristics over time.</p>',
132: '          <p class="dz-p" data-dz>Grain direction, vein matching, junctions, tolerances and transitions between materials receive the same attention as the materials themselves. A controlled palette, precisely detailed, creates greater depth than an accumulation of unrelated finishes.</p>',
160: '          <h2 class="dz-h2 dz-h2--s" id="dz-t-interiors" data-dz>Layered interiors, <br />precisely resolved.</h2>',
161: '          <p class="dz-p" data-dz>Nova interiors are developed as a continuation of the architecture rather than as an independent decorative layer. Wall panelling, bespoke joinery, lighting, material transitions and service interfaces are coordinated to preserve visual continuity throughout the residence.</p>',
162: '          <p class="dz-p" data-dz>The material palette remains controlled but deliberately rich — timber, stone, metal, leather and textile surfaces are composed through proportion, contrast and texture rather than decorative excess. Furniture, artwork and collected objects form part of the spatial composition, adding character without competing with the architecture.</p>',
163: '          <p class="dz-p" data-dz>A home should reveal its quality gradually — through the way a door closes, the alignment of a joint, the depth of a reveal, the weight of a handle or the texture of a surface.</p>',
186: '          <p class="dz-p" data-dz>Shadow gaps, thresholds, joinery reveals, panel junctions, ironmongery, integrated ventilation elements and concealed services are resolved as part of a single architectural language. These details are deliberately restrained, but collectively they determine how complete, durable and coherent a residence feels in daily use.</p>',
199: '          <p class="dz-p" data-dz>Landscape is developed as an extension of the residential composition. Terraces, courtyards, arrival sequences, boundaries and exterior living areas are coordinated with the architecture so that planting, paving and built elements continue the spatial language beyond the building envelope.</p>',
200: '          <p class="dz-p" data-dz>Sculptural trees, layered evergreen planting and carefully selected seasonal species establish privacy, visual depth and a mature residential character without relying on ornamental excess.</p>',
215: '        <p class="dz-statement dz-statement--s dz-land-note" data-dz>The relationship between architecture and landscape should feel integrated rather than applied.</p>',
225: '          <p class="dz-p" data-dz>Residential architecture does not exist independently of its surroundings. Scale, orientation, neighbouring structures, street character, mature vegetation, daylight conditions and long-distance views all influence the architectural response.</p>',
226: '          <p class="dz-p" data-dz>Within Istanbul\'s established residential districts — including Bağdat Caddesi and its surrounding neighbourhoods — new architecture must respond to contemporary residential expectations while maintaining a measured relationship with the existing urban fabric.</p>',
227: '          <p class="dz-p" data-dz>At Nova, context is treated as a design parameter rather than a backdrop.</p>',
248: '            <p class="dz-p">Site conditions, orientation, planning constraints and surrounding urban characteristics establish the first design parameters.</p>',
253: '            <p class="dz-p">Structural geometry, spatial hierarchy and circulation are developed as a coordinated architectural framework.</p>',
258: '            <p class="dz-p">Material systems are selected according to performance, durability, tactility and architectural coherence — including timber grain, stone selection, metal finish and surface behaviour.</p>',
263: '            <p class="dz-p">Architecture, structure, façade systems, interiors and building services are coordinated together before execution.</p>',
268: '            <p class="dz-p">Critical junctions and interfaces are refined through drawings, material samples, mock-ups and site review.</p>',
282: '          <p class="dz-p" data-dz>Architectural intent depends on control throughout construction. Dimensions, interfaces, substrates, tolerances and material junctions are therefore reviewed not as isolated finishing elements, but as interconnected parts of the complete design.</p>',
283: '          <p class="dz-p" data-dz>Mock-ups, samples and site coordination are used where necessary to verify colour, texture, grain direction, material interfaces and workmanship before final execution.</p>',
284: '          <p class="dz-p" data-dz>The objective is simple: what is resolved in the design must remain resolved in the built work.</p>',
295: '        <h2 class="dz-statement dz-statement--m" id="dz-t-end" data-dz>Design quality depends on <br />technical discipline.</h2>',
297: '          <p class="dz-p" data-dz>Architecture, structure, building envelope, waterproofing, mechanical and electrical systems must ultimately operate as a coordinated whole. For Nova, design quality is therefore inseparable from engineering, constructability and execution control.</p>',
}

for ln, text in new.items():
    old = lines[ln - 1]
    tag_old = old.strip().split(">")[0]
    tag_new = text.strip().split(">")[0]
    assert tag_old == tag_new, f"line {ln}: opening tag changed\n{tag_old}\n{tag_new}"
    lines[ln - 1] = text

p.write_text("\n".join(lines), encoding="utf-8")
print("replaced", len(new), "lines")
