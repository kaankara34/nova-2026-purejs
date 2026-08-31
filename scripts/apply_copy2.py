"""One-off: second copy pass on scripts/design_main.html — text nodes only, structure untouched."""
import pathlib

p = pathlib.Path(__file__).parent / "design_main.html"
lines = p.read_text(encoding="utf-8").split("\n")

new = {
9: '          <h1 class="dz-h1" data-dz>Architecture begins with <br />proportion.</h1>',
20: '          <p class="dz-lead" data-dz>A residence starts with the plan. Proportion, orientation, daylight and the way one room connects to the next all come before finishes are chosen. These early decisions shape the character of the home and guide the rest of the design.</p>',
21: '          <p class="dz-p" data-dz>We plan around daily life. Living areas need openness, private rooms need separation, and circulation should feel natural. Good architecture should make these things feel effortless.</p>',
31: '          <h2 class="dz-h2" id="dz-t-architecture" data-dz>Architecture with <br />purpose.</h2>',
32: '          <p class="dz-p" data-dz>At Nova, architecture starts with clear planning and sound proportions. Structure, circulation, façade and interior space are developed together so that the building works as a whole.</p>',
33: '          <p class="dz-p" data-dz>The façade is shaped by scale, orientation, privacy and the character of its setting. Inside, plans focus on usable room sizes, clear movement and natural light. The aim is simple: homes that still feel right years after they are built.</p>',
73: '          <p class="dz-p" data-dz>Room size matters, but the relationship between rooms matters just as much. Sightlines, circulation, furniture placement, thresholds and transitions are worked through together so that the plan feels clear and connected.</p>',
74: '          <p class="dz-p" data-dz>Living spaces are kept open where it makes sense, while bedrooms and quieter areas retain privacy. Structure, service zones and architectural planning are coordinated early so the finished home is not shaped by last-minute compromises.</p>',
89: '          <p class="dz-statement dz-statement--s" data-dz>The result is a home that feels natural to move through.</p>',
110: '          <p class="dz-p" data-dz>Daylight changes a room throughout the day, so window size, orientation, room depth and façade openings are considered together from the start.</p>',
111: '          <p class="dz-p" data-dz>More glass is not always better. Views, privacy, solar gain and comfort all affect where and how openings are placed. In the evening, concealed lighting, joinery lighting and focused task lighting continue the same atmosphere without overwhelming the space.</p>',
112: '          <p class="dz-statement dz-statement--s" data-dz>A well-lit room should feel comfortable at every hour.</p>',
121: '        <h2 class="dz-h2" id="dz-t-materials" data-dz>Materials chosen <br />to last.</h2>',
131: '          <p class="dz-p" data-dz>We choose materials for how they look, how they feel and how they perform in daily use. Stone, timber, metal, leather and glass all age differently, and that matters just as much as their appearance on the day a home is completed.</p>',
132: '          <p class="dz-p" data-dz>Details such as timber grain, stone veining, joints and material transitions are resolved carefully. A small number of well-chosen materials usually creates a stronger interior than a long list of finishes competing for attention.</p>',
146: '        <p class="dz-statement dz-statement--s dz-mat-note" data-dz>Quality is often easiest to see where two materials meet.</p>',
160: '          <h2 class="dz-h2 dz-h2--s" id="dz-t-interiors" data-dz>Warm interiors, carefully <br />resolved.</h2>',
161: '          <p class="dz-p" data-dz>The interior is designed together with the architecture. Wall panelling, built-in joinery, lighting, material transitions and service details are coordinated from the beginning so that the rooms feel complete, not assembled in layers afterwards.</p>',
162: '          <p class="dz-p" data-dz>The palette is warm and controlled. Timber, stone, metal, leather and textiles bring depth without making the space feel busy. Furniture, artwork and objects give a home personality; they should sit naturally within the architecture, not fight against it.</p>',
163: '          <p class="dz-p" data-dz>Good quality often appears in small moments — how a door closes, where two panels align, the weight of a handle, the depth of a reveal or the feel of a surface.</p>',
172: '        <h2 class="dz-statement dz-statement--l" id="dz-t-detail" data-dz>The smallest details often say <br />the most.</h2>',
186: '          <p class="dz-p" data-dz>Shadow gaps, thresholds, joinery lines, metalwork, integrated vents and concealed services are all worked through before the space is finished. None of these details needs to draw attention to itself; when they are done properly, the room simply feels more complete.</p>',
196: '          <h2 class="dz-h2" id="dz-t-landscape" data-dz>Architecture continues <br />outside.</h2>',
199: '          <p class="dz-p" data-dz>Landscape is part of the way a residence is experienced. Entrances, terraces, courtyards, planting and outdoor seating are planned together with the building so the transition between inside and outside feels natural.</p>',
200: '          <p class="dz-p" data-dz>Mature trees, evergreen planting and seasonal species are selected to give privacy, shade and depth. The landscape should feel established, not decorative.</p>',
215: '        <p class="dz-statement dz-statement--s dz-land-note" data-dz>Architecture and landscape should belong to the same place.</p>',
225: '          <p class="dz-p" data-dz>Every project begins with its surroundings. The street, neighbouring buildings, orientation, vegetation, views and daylight all have an effect on the final design.</p>',
226: '          <p class="dz-p" data-dz>This matters especially in established residential areas such as Bağdat Caddesi and its surrounding neighbourhoods. New buildings need to meet contemporary expectations without ignoring the scale and character of the streets they become part of.</p>',
227: '          <p class="dz-p" data-dz>A building should respond to where it stands.</p>',
248: '            <p class="dz-p">Site conditions, orientation, planning rules and the surrounding neighbourhood set the starting point.</p>',
253: '            <p class="dz-p">Room relationships, circulation and structural geometry are developed together as one plan.</p>',
258: '            <p class="dz-p">Materials are chosen for quality, durability, texture and how well they work together in the finished space.</p>',
263: '            <p class="dz-p">Architecture, structure, façade, interiors and building services are coordinated before construction moves forward.</p>',
268: '            <p class="dz-p">Key junctions are checked through drawings, samples, mock-ups and site review before final installation.</p>',
279: '          <h2 class="dz-h2" id="dz-t-craft" data-dz>A design is only as good as <br />the way it is built.</h2>',
282: '          <p class="dz-p" data-dz>Good drawings are not enough on their own. Dimensions, substrates, tolerances and material junctions all need to be checked during construction so that the original design is not lost on site.</p>',
283: '          <p class="dz-p" data-dz>Samples and mock-ups are used where needed to review colour, texture, grain direction and the way materials meet before final installation.</p>',
284: '          <p class="dz-p" data-dz>What is resolved on paper should still be resolved when the building is finished.</p>',
295: '        <h2 class="dz-statement dz-statement--m" id="dz-t-end" data-dz>Design and construction <br />belong together.</h2>',
297: '          <p class="dz-p" data-dz>Architecture only works when structure, façade, waterproofing and building services are properly coordinated behind it. For Nova, design quality is closely tied to how accurately the project is engineered and built.</p>',
}

for ln, text in new.items():
    old = lines[ln - 1]
    assert old.strip().split(">")[0] == text.strip().split(">")[0], f"line {ln} tag mismatch"
    lines[ln - 1] = text

p.write_text("\n".join(lines), encoding="utf-8")
print("replaced", len(new), "lines")
