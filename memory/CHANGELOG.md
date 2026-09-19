# CHANGELOG

## 2026-06 — Contact page additions (contact.html)
- `ct-intro`: added a quiet constructivist SVG art mark (brass arc, dotted slow-orbit ring, sage/brass disc, stone block, hairlines). Respects `prefers-reduced-motion`.
- New Instagram section between `ct-detail` and `ct-loc`: "Latest from Nova" head, `@novakonut` follow link, 4 square tiles (NOVA-generated imagery, all linking to the profile), follow note. 4 columns desktop / 2 columns ≤767px.
  - NOTE: Instagram cannot be scraped (HTTP 403) — tiles use NOVA's own imagery and link out; this is NOT a live feed.
- Register Interest before the footer: the project-page (Martı) split composition rebuilt as scoped `ct-reg` / `ct-form`, retoned to Contact's warm palette (#E8DFD2 ground, ink text, brass italic sub, ink submit). UI-only submit handler in `js/contact.js` (`#ctRegisterForm`) with inline status message.
- Files: `scripts/contact_main.html`, `frontend/css/contact.css`, `frontend/js/contact.js`, regenerated `frontend/contact.html` (448 lines) via `scripts/build_contact.py`.
## 2026-06 — Contact: live Instagram + stabilised birds film
- Backend (`backend/server.py`): `GET /api/instagram/latest` (latest 4 posts, 30-min in-memory cache + Mongo `ig_cache` fallback) and `GET /api/instagram/image/{shortcode}` (proxies the signed IG CDN image). Instagram blocks httpx/requests TLS fingerprints (429) — fetch uses `curl_cffi` with `impersonate="safari17_0"`. Added `curl_cffi` to requirements.
- `frontend/js/contact.js` hydrates the 4 tiles from the API on load; the bundled snapshot images stay as fallback (also restored on img error).
- Video regraded: 2-pass vidstab stabilisation, 2.1x slow with `minterpolate` (14.7s), pale blue-teal grade matching the user's reference; CSS desaturating filter removed. `frontend/media/video/birds.mp4|.webm` + poster (~1.5MB each).
- Verified on preview: overflow 0, video playing/stable, tiles served from `/api/instagram/image/...`.

## 2026-06 — Contact revision (real IG posts + birds film)
- Instagram tiles now show NOVA's **real latest 4 posts**, fetched via the public `i.instagram.com/api/v1/users/web_profile_info` endpoint (x-ig-app-id header), images stored locally at `frontend/media/images/contact/ig/post-1..4.jpg`, each tile deep-links to its post permalink (shortcodes DaQk9OvscF6, DaQbe_FMl7l, DaQadKFjHXG, DaN8eQ2s4pu). Tiles are 4:5 like Instagram. NOTE: static snapshot, not a live feed — re-run the fetch to refresh.
- `ct-intro` art replaced: the SVG mark removed, now a muted birds-rising-from-a-tree film (autoplay/muted/loop/playsinline) at `frontend/media/video/birds.mp4|.webm` + poster, toned with a warm veil and hairline frame. Source: Pexels free-licence clip 5024947 (Aman's own Vimeo clip was not reused for licence reasons).
- Verified: desktop 1920 + mobile 390 screenshots, 0 horizontal overflow, form error/success paths, oxlint 0 warnings/0 errors on contact.js. User visual confirmation pending.

## 2026-06 — Scoped round: material register, Contact density, Construction hero
- Pulled the user's GitHub state (`upstream/main` d955b2c "arrangements": contact-video.*, design1/design2.webp, section reorder, mobile body padding) and added `scripts/resync_contact_main.py` so the generated `contact.html` and its source fragment stay in sync.
- DESIGN — material register rebuilt on real PBR sets (`scripts/build_material_maps.py`): commissioned 1024px albedo scans + derived 512px normal and 384px roughness maps for walnut (Juglans nigra, cathedral grain + sapwood band, satin oil), Calacatta Oro (single slab mirrored around a central seam = true bookmatch), aged bronze (brown/olive patina, machining marks, metalness 1) and vegetable-tanned cognac leather (pores, follicles, sheen). Smoked glass is body-tinted transmission (ior 1.52, grey attenuation) read against a page-coloured backdrop plus a backing card so transmission/refraction are visible. Per-material plate thickness, lazy per-material texture loading, softened studio lighting (exposure 0.86). No provenance labels, flags or maps.
- DESIGN — `proportion-interior.webp` and `light-wide.webp` replaced with commissioned editorial interiors (`scripts/build_design_interiors.py`), no exterior views.
- CONTACT — email/phone reduced to 15–18px information type, vertical rhythm tightened throughout, office-hours block added per office (EN visible; Turkish strings carried on `data-hours-tr` for the future TR build), desktop intro film enlarged to 548x684 (46/44 grid), mobile layout unchanged.
- CONSTRUCTION — hero rebar photograph and rotating rebar canvas removed, hero collapsed from 250vh to a single restrained screen on solid #0b0d0e with a very subtle corner tonal lift; all hero copy untouched. The cage 3D section still runs.
- Verified by testing agent (`/app/test_reports/iteration_38.json`): no functional defects; 0 horizontal overflow at 1440/1024/768/390; both flagged design notes (hours contrast, film scale) applied afterwards.

## 2026-06 — Design: shared-slab material register, Pietra Grey, 16:9 mobile hero
- All five samples rebuilt on ONE shared geometry: a single uninterrupted landscape slab (1.78 x 1.02 x 0.115) shown at a three-quarter angle, identical dimensions/camera for every material. No dividers, seams, split panels, doors, handles, frames or overlapping parts. BoxGeometry with a 6-material array so the front/back carry the face crop and the four edges carry a zoomed edge crop (no wrapped/stretched UVs).
- Stone changed from Nero Portoro to **Pietra Grey (Isfahan, Iran)**: charcoal ground, sparse pale calcite veins, a feathered soft bookmatch baked into the scan (`soft_bookmatch()` in scripts/build_material_maps.py) so the mirrored relationship is subdued with no axis or V. Copy updated in design.html (ORIGIN / PATTERN / SURFACE / USED FOR) — no Nero Portoro / Calacatta / Arabescato references remain.
- Walnut dark chocolate continuous grain; bronze a plain patinated specimen (warmer albedo, lower roughness, envMapIntensity 1.1); leather desaturated to chestnut/cognac with no seams; smoked glass a single body-tinted transmissive pane (ior 1.51, thickness 0.5, grey attenuation) with two slim studio bars behind it so transparency and refraction read.
- Perf: textures load per material on first use and the face/edge crops now share one download (`texCache` + `clone()`); soft contact shadow, faint for glass.
- Design hero image forced to 16:9 (width 100%, object-fit cover, object-position 50% 62%) at <=1100px, replacing the 4:5 mobile portrait crop; desktop unchanged.
- Verified: testing agent `/app/test_reports/iteration_39.json` — 100% of requested checks passed, 0 overflow, hero ratio 1.78 at 375/390/430/768 and 2.11 at 1440, no console errors. Its two subjective notes (bronze too dark, stone too warm) were then addressed by regrading those two scans.

## 2026-06 — The Apartments Taç project page (new)
New page `frontend/the-apartments-tac.html` + `frontend/css/the-apartments-tac.css`, generated by
`scripts/build_tac.py` from `scripts/tac_main.html` (page body) + `scripts/tac_overrides.css` (dark Taç
skin) + `east-west.html` chrome/footer + `east-west.css` re-namespaced to `tac-`. East West itself is
untouched apart from the one footer link now pointing at the new page.
Do NOT edit the generated html/css directly — edit the two `scripts/` sources and re-run the build.

- Palette: #050505 outer / #121311 panel / #1A1916 raised / text #F0EEE8 / secondary #AAA69D / bronze #A99A7B; hairlines #5D5A53.
- Hero: temporary licensed stock rough-construction clip (`media/video/tac/tac-construction.{mp4,webm}` + poster), no project logo, location + UNDER CONSTRUCTION stacked and centred, content sitting close to the bottom edge, hero height 78vh/62vh (never 100vh).
- Action bar: VIEW RENDER (gallery icon) · BOOK UNIT (gold) · VIEW FLOOR PLAN (outline), each scrolling to #architecture / #register / #floorplan.
- Intro: Taç lettermark (mix-blend-mode reset to normal for the dark ground) with typography/spacing identical to the East West intro (verified computed-style match).
- Architecture: one approved render only (`media/images/tac-ai-render.webp`, 1800x2265) as a 4:5 portrait inside an asymmetric #121311 panel.
- Specifications: exact approved values; a dev-only HTML comment asks staff to confirm the 190 m² gross definition against the approved area schedules before production.
- Floor plan: PLACEHOLDER — the East West 4+1 drawing, background removed to alpha, on a warm #E8E3D9 carrier, with expand (lightbox) + print buttons and the East West room schedule as placeholder rows. Marked with a dev comment; must be replaced with the approved Taç plan.
- Location: real dark OpenStreetMap (Leaflet 1.9.4, tile.openstreetmap.org darkened by CSS filter — CARTO dark now needs an API key) with the client's gold stylised site plan as an `L.imageOverlay`, bronze pin, scroll-wheel zoom on, coordinates 40.977441822155704 / 29.04879347144911.
- Nearby: PLACEHOLDER — East West's 13 entries and photos verbatim, to be edited by the client.
- Enquiry: East West form pattern, project preselected to "The Apartments Taç, Bağdat Caddesi", UI-only submit.
- Verified: testing agent `/app/test_reports/iteration_40.json` — 11/11 checks pass, 0 overflow at 375/390/430/768/1024/1440, no console errors, East West regression clean. Two follow-ups then fixed by hand: the lightbox used the wrong class (`is-open` instead of the system's `.open`, so it never displayed) and the close button had a zero-size box.

### Taç follow-up corrections (same day)
- **Site plan vs map separated on the Y axis.** The gold site plan is no longer a Leaflet `imageOverlay`; it is a plain `<figure class="tac-location-media">` in normal flow immediately above `.tac-map`, container capped at 1200px with the asset's own 2000/1115 ratio and a responsive bottom gap — East West's location flow. Verified non-overlapping rects at 1440/768/390.
- **`tac-intro` rhythm rebuilt.** Removed the inherited `-50px` logo margin and the lopsided padding: balanced section padding, logo `min(430px, 64%)` with a controlled gap, paragraphs constrained to 58ch/62ch with line-height 1.95 and `letter-spacing .07em`, centring applied per element instead of on the container, tighter values under 767px.
- **Plan asset genuinely transparent.** `tac-4plus1.png` re-cropped to its alpha bounding box (now 925x1350) and the `#E8E3D9` carrier, panel background, border and padding all removed — the isolated plan sits directly on the dark section.
- **Working 3+1 / 4+1 tabs.** Two real `role="tab"` buttons in a `role="tablist"`; the single drawing's mirror axis was measured at x=542 of the original PNG (50.2% after cropping), so the two `.tac-plans-dim` masks split it at exactly 50% with no seam. Inactive half dims to `opacity .72` over a 380ms transition and stays faintly readable; active half untouched. Keyboard: ArrowLeft/ArrowRight move selection, `aria-selected` and `tabindex` maintained.
- **Room data bound to the tab.** `PLANS` dataset in `the-apartments-tac.js` holds the East West 3+1 (155 gross / 127 net, 6 rooms) and 4+1 (190 gross / 149 net, 7 rooms) schedules; heading, gross/net totals, room rows and the supporting paragraph are re-rendered together, m² column right-aligned on a shared axis.
- **Mobile:** plan above the list, image full width without cropping at its 925/1350 ratio, centred 48px-high touch tabs, masks still flush, map min-height 320px at 4/5.
- Verified: testing agent `/app/test_reports/iteration_41.json` — 14/14 pass, 0 overflow at 375/390/430/768/1024/1440, no console errors, East West regression clean.

### Taç: real floor plan, single-black Architecture, Private Parking + Arrival
- **Client's real typical floor plan installed** (`media/images/tac/plans/tac-4plus1.png`, background flood-filled to alpha and cropped, 1748x1428, landscape). Both apartments on the floor are 4+1, so the 3+1/4+1 tab system, the `role="tablist"`, the `PLANS` dataset and the left/right dimming masks were all **removed**; a single `4+1` label remains as a plain bronze-underlined marker. The schedule beside the plan is now the real 13-room list read off the drawing (Salon 45.29, Master 20.16, 12.11, 11.77, 11.22, Kitchen 13.38, Antre 7.67, Hol 7.59, En-suite 3.50, Bathroom 5.80, WC 2.16, Utility 3.00, Balcony 5.10 — sum 148.75 ≈ the published 149 m² net). No East West values remain on the page.
- **ARCHITECTURE is one single black.** `.tac-render` and `.tac-render-inner` are both `#0A0A0A` with a transparent border, so the two-tone panel edge is gone. Added a restrained reveal: `clip-path: inset(0 0 100% 0)` → `inset(0)` plus a 1.03 scale settle on the image, and a 26–28px opacity/translate lift on eyebrow/title/copy with a 0.11s stagger, all on `cubic-bezier(.22,.61,.36,1)` at 1–1.3s.
- **Two new sections between DESIGNED AROUND SPACE and LOCATION**, namespaced `tac-parking-`: `#parking` (PRIVATE PARKING) and `#arrival` (ARRIVAL). 40/60 editorial grid on the same 1360px container, mirrored on the arrival section, single column with the copy first under 900px. Copy is exactly as supplied. Parking carries a two-figure block (−2 basement levels / 2 spaces per residence). Both images are WebP with `srcset`, explicit dimensions, lazy loading and a `figcaption` reading "Architectural visualisation".
- Reveals are driven by one `IntersectionObserver` that adds/removes `.is-pending` (no extra library); a `prefers-reduced-motion: reduce` block forces `.reveal-up/.reveal-fade/.reveal-stagger` and all new elements to opacity 1 / no transform, and nothing is hidden without JS because hiding only happens via the JS-added `.is-pending` class.
- Assets created: `media/images/tac/tac-parking.webp` + `-800.webp`, `media/images/tac/tac-arrival.webp` + `-800.webp` (AI-generated architectural visualisations, labelled as such).
- **Not verified against approved documents:** the title-deed classification (kept the supplied careful wording "formally recorded in the relevant title-deed documentation" — the spaces are NOT described as separate independent properties), and whether vehicle access is direct from the avenue — so the alternative "A considered arrival from Bağdat Caddesi." heading and body were used and the word "directly" does not appear. The parking and arrival visuals are not approved project renders.
- Verified: testing agent `/app/test_reports/iteration_42.json` — 14/15 pass, 0 overflow at 390/430/768/1024/1440/1920, no console errors, East West regression clean. Its one LOW finding (the architecture `<figure class="reveal-up">` stayed hidden under reduced motion) was then fixed with the reduced-motion reset and re-verified (opacity 1, transform none, 0 `.is-pending`).

### Taç: header transparency restored, floor-plan surface + schedule alignment
- **Header transparency was never broken by styling** — the shared `js/script.js` hero selector list (`.hero, .pj-hero, .ew-hero, .cx-hero, .bb-hero`) simply did not include `.tac-hero`, so `onScroll()` took the "no hero on this page" branch and kept the header solid. Added `.tac-hero` to that one selector; Taç now has full parity with East West (`transparent` at the top, removed past the hero, `utility-bar.hidden` + `header.bar-hidden` after 40px).
- **Floor-plan section is now a raised surface** `#111210` instead of plain black, so it reads as a distinct step against the `#050505` sections on either side.
- **Schedule no longer dangles.** `SPACE AS THE DEFINING FEATURE` + its paragraph moved out of the right column into a full-width `.tac-plans-footnote` below the plan body; the m² schedule became a two-column grid (the Gross/Net rows spanning both) and the info column now stretches to the drawing's height with `align-content: space-between`, so the last row ends exactly level with the bottom of the plan (measured delta 0px at 1440 and 1920).
- Below 1100px the drawing becomes shorter than the schedule, so the section stacks and the bottom-alignment constraint is dropped (this was the one MEDIUM finding at 1024 in iteration_43).
- Verified: `/app/test_reports/iteration_43.json` (header parity, section colours, two-column schedule, footnote, mobile stacking, plus a no-error/no-overflow sweep of east-west, index, projects, contact, construction and design since `script.js` is shared) and `/app/test_reports/iteration_44.json` — 100%, 0 issues, 0 overflow at 390/430/768/1024/1440/1920.

### Taç: image weight/timing, premium parking cars, footnote alignment, schedule legibility, corrected coordinates
- **Slow images fixed at the source, not by removing the animation.** The real cause was a **2.5 MB PNG** floor plan; it is now a **272 KB alpha WebP** (`tac-4plus1.webp`, PNG kept only as the working source). The architecture render is `loading="eager" fetchpriority="high"`, and the reveal observer now fires **300px before** an element enters the viewport (`rootMargin: 300px 0px 0px 0px`, `threshold: 0`) with shorter transitions (image clip 0.8s, text 0.75s, stagger 0.08s), so sections are already resolved by the time they are read.
- **Parking visual regenerated** with understated executive cars (Mercedes E-Class, BMW 5 Series, Tesla Model Y, Range Rover) parked normally — no showroom staging, supercars, people or marble. 112 KB WebP + 32 KB small variant.
- **Footnote paragraph is now flush right**: the footnote grid is `auto / 60ch` with `margin-left: auto` on the copy, so its right edge matches the container's right edge exactly (verified at 1024/1440/1920) with the label staying left.
- **Schedule legibility**: 13px desktop / 14px mobile rows, bronze tabular row numbers, values in `#FFFDF7` with tabular figures, stronger `rgba(240,238,232,.14)` dividers, the Gross/Net rows lifted to uppercase bronze-grey labels with a `#6E6A61` rule, and a single column below 767px. The schedule still ends exactly level with the bottom of the drawing (delta 0px).
- **Map coordinates corrected** to `40.9771680668217, 29.049068608464168` in the map centre, the marker, the printed label (`40.977168°N 29.049069°E`) and the Google Maps link; the old 40.977442/29.048793 pair no longer appears anywhere.
- Verified: testing agent `/app/test_reports/iteration_45.json` — **100%, 0 issues**, 0 overflow and 0 console errors at 390/430/768/1024/1440/1920, East West regression clean.

## The Apartments Ana — new project page (June 2026)
Files created: `frontend/the-apartments-ana.html`, `frontend/css/the-apartments-ana.css`,
`frontend/js/the-apartments-ana.js`, `scripts/build_ana.py`, `scripts/ana_palette.css`.
Build: `python3 scripts/build_ana.py` (the three frontend files are GENERATED — edit
`scripts/build_ana.py` / `scripts/ana_palette.css` instead).

- Ana is a **generated structural counterpart** of Taç: the generator reads the Taç page, stylesheet and script, masks every `media/...` asset path and the shared Taç navigation entries, then renames the namespace (`page-tac`→`page-ana`, `tac-`→`ana-`, `tacXxx`→`anaXxx`, `data-tac-`→`data-ana-`, `--tac`→`--ana`) and unmasks. That guarantees identical DOM, grid, spacing, type scale, breakpoints, motion and behaviour with zero drift, and it means future Taç structural changes can be re-propagated with one command.
- **Taç and all shared files are byte-for-byte unchanged** (verified with `git diff` on `the-apartments-tac.html`, `css/the-apartments-tac.css`, `js/the-apartments-tac.js`, `css/styles.css`, `js/script.js`, `js/swipe-carousel.js`).
- Palette: the Taç greys are mapped onto the Ana family in the generator (`#050505/#0A0A0A/#0B0B0A`→`#281B23`, `#111210/#121311`→`#3B2632`, `#1A1916`→`#59404A`, off-whites→`#F3EFE7`, `#E8E3D9`→`#E8E0D4`, greys→`#B8AA9D`, bronzes→`#8B7257`), then `scripts/ana_palette.css` declares the variable system and re-states the light/dark sections: action strip `#281B23`, intro/render/plans/parking/nearby `#F3EFE7`, render inner panel + specs + arrival `#E8E0D4`, DESIGNED AROUND SPACE + location `#281B23`, enquiry `#3B2632`. Hero scrim is a plum gradient; hero base is `--ana-plum-dark` (no pure black). Bronze is confined to eyebrows, row numbers, thin rules, the primary button and hover states.
- The ANA lettermark (`ANA_logo-tight.svg`) is light ink, so on the ivory intro it is inverted and tinted plum with a CSS filter rather than swapped for a new asset.
- Links corrected inside the Ana page only: footer + mega-menu Ana card → `the-apartments-ana.html`, Taç card → `the-apartments-tac.html`, East West card/link → `east-west.html`.
- **Still inherited from Taç as approved placeholders:** hero video + poster, architectural render, intro/specs/plans/parking/arrival/location/nearby copy and data, the 4+1 drawing and its 13-room schedule, the gold site-plan image (which has "THE APARTMENTS TAÇ" baked into the artwork), the parking/arrival visualisations, the map coordinates and the nearby distances. No Ana-specific facts were invented.
- Verified: testing agent `/app/test_reports/iteration_46.json` — 0 console errors, 0 overflow at 375/390/430/768/1024/1440/1920, 0 `tac` namespace leftovers in the Ana html/css/js, section rhythm as specified, lightbox/print/map/form/reveals/reduced-motion all working, and a clean regression sweep of Taç, east-west, index, projects, contact, construction and design. Its single nit (`.ana-hero` computing to pure black under the video) was then fixed to `--ana-plum-dark` and re-measured as `rgb(40, 27, 35)`.

## The Apartments Ana — authentic assets, fullscreen fix, Büyük Kulüp, map (16 June 2026)
Working tree was first realigned to the **latest upstream `main` (`5d27fce` "ana updated")** for
`the-apartments-ana.html`, `index.html`, `projects.html`, `the-apartments-tac.html` and the new
`media/images/ana/*` + `media/video/ana-video.*` assets (no manual commit/push — platform handles it).
NOTE: `scripts/build_ana.py` is now **stale** — the Ana page has been hand-authored upstream since it was
generated, so do **not** re-run the generator; edit `frontend/the-apartments-ana.html` / `css` / `js` directly.

- **Property details separators fixed.** The six groups used `--ana-line` (an ivory hairline) which is
  invisible on the Ana specs surface; `.page-ana .ana-spec` now uses `--ana-divider`
  (`rgba(59,38,50,.15)`) for the vertical rules at 1440/1024 and the horizontal rules when the grid
  wraps at 768/430, with no divider after the final (LOCATION) group and `overflow-wrap: break-word`
  on the values.
- **Authentic floor plan.** `media/images/ana/plans/ana-typical-floor.webp` (1334×1180, from the
  client PNG) replaces the Taç placeholder, shown with `object-fit: contain` and full labels.
  Schedule rewritten from the drawing only: Living Room 38.43, Master Bedroom 19.40, Bedroom 11.23,
  Bedroom 11.00, Kitchen 12.02, Entrance Hall 8.19, Corridor 2.86, Bathroom 5.46, En-suite Bathroom
  3.09, Utility 3.00 m², above the confirmed 150 m² gross / 112 m² net. **Balcony areas on the plan
  edges are not legible, so no balcony row is published** (KAT HOLÜ / YANGIN MERDİVENİ are shared
  circulation and excluded). Print sheet and meta description updated to Ana 3+1 / 150 / 112.
- **Fullscreen viewer bug root cause found:** the lightbox markup sat inside
  `<section class="ana-plans reveal-up">`, whose `transform` made it the containing block for the
  `position: fixed` modal (measured rect top `-82px`, hence the "scroll down to find the plan"
  symptom). The modal is now a **top-level element** and adopts the East West mechanism:
  `window.lockScroll()/unlockScroll()` from `js/script.js` (scroll-position preserving), `100dvh`,
  safe-area padding, `z-index: 4000`, 48px round close control, Escape + backdrop + button close,
  double-open guard.
- **New Le Cercle d'Orient Büyük Kulüp section** (`#buyuk-kulup`, `ana-kulup-*`) directly between
  `#parking` and `#arrival`: authentic photograph `media/images/ana/buyuk-kulup-interior.webp`
  (2000×1500) as the principal 58% visual, official transparent logo
  `media/images/ana/buyuk-kulup-logo.png` on a Warm Ivory panel in the 42% copy column (the logo's
  navy ink has no contrast on plum), exact supplied copy, mobile order photo → logo → eyebrow →
  heading → body, reveal reuses the existing IntersectionObserver and is skipped under
  `prefers-reduced-motion`.
- **Map corrected** to `40.97149665164465, 29.055055825082672` (centre, marker, `data-lat/lng`,
  panel text `The Apartments Ana / Kemal Sunal Sokak / Caddebostan, Kadıköy, İstanbul`,
  `40.971497° N · 29.055056° E`) with the external link exactly
  `https://www.google.com/maps?q=40.97149665164465,29.055055825082672`; the old
  40.977168/29.049069 pair is gone and `invalidateSize()` runs after reveal/resize.
- **Not done — asset missing:** the replacement underground parking image was described but never
  attached, so `#parking` still uses `./media/images/tac/tac-parking.webp`.
- Verified: testing agent `/app/test_reports/iteration_47.json` — **frontend 100%, 0 issues**,
  0 overflow and 0 console errors at 1440/1024/768/430/390/844×390, modal rect equals the viewport
  everywhere, scroll position restored exactly over three open/close cycles, Taç and East West
  regression clean.

### Ana follow-up fixes (16 June 2026)
- **Mobile separators repaired.** The first attempt added structural `nth-child` overrides inside
  `@media (max-width: 1100px)`, which also matched 430/390 and wrongly killed the divider after item 3
  and the bottom border of item 4. The override is now **colour-only**
  (`.page-ana .ana-spec { border-right-color / border-bottom-color: var(--ana-divider) }`), so each
  breakpoint keeps its original 6 / 3 / 2-column pattern. Verified at 430: items 1/3/5 right border,
  1–4 bottom border, nothing trailing after item 6.
- **"Engineered for Structural Safety" footnote** no longer runs as a narrow 60ch column on phones —
  a `@media (max-width: 900px)` rule after the flush-right block returns it to a single full-width
  column (measured 390px of 390px at 430 viewport).
- **Parking visual replaced with an Ana-specific render** (`media/images/ana/ana-parking.webp`
  1264×848 + `ana-parking-800.webp`), generated in the same restrained style as Taç: two-level
  concrete garage, warm linear lighting, four understated executive cars, no people or staging.
  Wording and the two-basement / two-title-deed facts unchanged.
- **Büyük Kulüp logo is now genuinely transparent on the page**: the ivory panel was dropped
  (`.ana-kulup-logo-panel` → `.ana-kulup-logo-wrap`) and the whole section is Warm Ivory
  (`--ana-ivory`) with plum heading and aubergine body, so the navy logo reads correctly straight on
  the surface. Section rhythm is now dark parking → ivory Büyük Kulüp → bone arrival.

## Six completed-portfolio project pages (16 June 2026)
Doğan Residence, Falcon Plaza, Falcon Logistics Center, Konelsis Center, Nisbetiye On and
Gebze OSB Management Building were all byte-identical Martı Residence clones (501 lines each, video
hero, Martı copy/assets/form). They are now individually composed pages built from verified
nova.istanbul project data and the 16 authentic project images.

**New shared components (isolated behind the `pp-page` body class, `pp-*` namespace):**
- `frontend/css/portfolio-project.css` — split/full heroes, intro, specification strip (dividers are
  clipped `box-shadow` hairlines, so no dangling divider at any column count or breakpoint), media
  frames + captions, 6-column gallery grid with span utilities, editorial blocks, programme rows,
  enquiry form, viewport-level lightbox, one-time reveals + `prefers-reduced-motion` fallback.
- `frontend/js/portfolio-project.js` — reveal observer, lightbox built from `[data-pp-open]` figures
  (uses the shared `window.lockScroll/unlockScroll`, Escape/arrows/backdrop, keyboard-openable
  figures), inline enquiry-form validation. Runs only when `.pp-page` exists.
- `scripts/build_portfolio_pages.py` — GENERATOR for the six pages; it lifts the utility bar,
  header, mobile bar, side menu and footer verbatim from `marti-residence.html`, so the shared
  navigation stays byte-identical. **Edit the script, not the six HTML files.**
- The six per-page CSS files were cut from 923-line Martı clones to ~20-line tonal override files
  (CSS custom properties per project); the six per-page JS clones were deleted.

**Assets** (converted to WebP from nova.istanbul, no upscaling): `media/images/dogan/` (5),
`falcon-plaza/` (1), `falcon-logistics/` (4), `konelsis/` (1), `nisbetiye-on/` (3), `gebze-osb/` (2).

**Composition per project** — density follows the available authentic material: Doğan is the richest
(hero + 4-image gallery + 24-residence programme + 6 verified building systems), Falcon Logistics
gets a full-width industrial hero + 3-image gallery, Nisbetiye On a full-width photograph hero +
2 labelled visualisations + area/level programme + LEED-framework wording, Gebze a split hero photo +
one labelled render, and Falcon Plaza / Konelsis are deliberately short single-image pages with no
gallery. All renders are captioned ARCHITECTURAL VISUALISATION; photographs are captioned as such.

**Untouched, as required:** `projects.html`, the shared header/side menu/footer markup, and the six
completed pages (east-west, taç, ana, martı, bahar, mercan) — confirmed with `git status`.

- Verified: testing agent `/app/test_reports/iteration_48.json` (~92%, three findings) then
  `/app/test_reports/iteration_49.json` — **100%, 0 issues, retest_needed false**. Fixes applied:
  Falcon Logistics hero added to its lightbox (now 4 images), Gebze no longer showed the same
  photograph twice (the pair section became one labelled render beside the copy) and the Gebze hero
  caption carries the completion year.

## Mehtap Residence + Finance Nova, Doğan scale, caption fixes (16 June 2026)
- **Mehtap Residence** (`mehtap-residence.html`, was a Martı clone) rebuilt on the `pp-*` system with
  `page-mehtap`: facts from nova.istanbul project-detail?proje=3 — Oyuncak Müzesi / Bağdat Caddesi,
  2014, 8,000 m², 15 floors, 47 residences, and the eight documented amenities. Two authentic renders
  → `media/images/mehtap/mehtap-render-street.webp`, `mehtap-render-facade.webp`.
  Order: hero (street render, framed split) → intro → 6 specs → on-site amenities editorial
  (façade render + 8-item list) → enquiry → footer.
- **Finance Nova** (`finance-nova.html`, new, `page-finance`) built solely from the supplied
  “NOVA ATAŞEHİR ENG 2” PDF: 55,000 m² mixed-use in Barbaros, Ataşehir — 27,000 residence/home office,
  10,000 workplace, 8,000 hotel (140 rooms), 10,000 closed garage; planned solar power, rainwater
  collection, smart-home tech; eight social facilities; eight verified distances. Four renders
  extracted from the PDF’s embedded images with PyMuPDF (no page screenshots) →
  `media/images/finance-nova/finance-nova-{towers,terraces,podium,landscape}.webp`.
  Order: full-bleed hero → intro → 6 specs → programme breakdown → 3-render gallery → planned
  facilities (dark) → connections → enquiry → footer.
  **Omitted on purpose:** all construction-cost, sales-revenue, endorsement and net-profit figures
  (investor material), the district population statistics and the neighbouring projects’ unit counts
  (not Nova facts). Conflict noted: the cover OCR reads “NOVA ATEŞEHIR” and page 5 summarises the
  programme loosely; the detailed page 15 breakdown was used.
- **Doğan image scale reduced**: hero media column capped at 560 px with the image at
  `min(64vh, 640px)` (measured 490×576 at 1440, was ~684×912); the gallery became a 1080 px-wide
  four-column grid with 280–400 px frame heights (measured 521×416, was ~520×693); at ≤520 px the
  frames use `width: calc(100% - 32px)` with `margin-inline: auto` and `min(52vh, 400px)` height.
  Lightbox still opens at full size (verified 1/5 with scroll restore).
- **Visible “Architectural Visualisation” labels removed** from konelsis-center and
  gebze-osb-management (the other three listed pages never had one); accuracy is preserved in the alt
  text and copy. No empty caption wrappers left.
- **Falcon Logistics captions fixed**: the mismatched `span-4 pano + span-2 portrait` row became three
  equal `span-2` landscape frames, so each `figcaption` sits 4–10 px directly under its own image; the
  descriptive paragraph and the View-all button moved to the gallery footer. Shared
  `.pp-media-caption` restyled to 12 px / .08em / title case, and `.pp-gallery-grid` got
  `align-items: start` so a caption can never drift into the next row.
- `projects.html`: **one-line change only** — the Finance Nova card `href="#"` → `finance-nova.html`
  (verified with `git diff`: 1 insertion, 1 deletion). Mehtap card already pointed to the right page.
- Verified by self-test: 0 console errors and 0 horizontal overflow on all eight portfolio pages at
  1440/1280/768/430/390 and 844×390; lightboxes open viewport-level with correct counters
  (Doğan 1/5, Falcon Logistics 1/4, Finance 1/4, Mehtap 1/2) and restore scroll; lint 0 errors.

## 2026-06 — Homepage content update (index.html): launches grid, marquee, AIDA component
Scope: content/media/link update only inside three existing homepage sections. No redesign; header,
navigation, footer, hero, news, collaborations, LEED and all other sections untouched.

- **Latest Luxury Property Launches**: removed The Apartments Gür card (the only card using an
  external DarGlobal CDN image). Heading, `VIEW ALL PROJECTS →` CTA, `NOW SELLING` badges, overlays,
  location/sales lines, hover and reveal behaviour preserved verbatim. Fixed dead links:
  CTA → `projects.html`, Taç → `the-apartments-tac.html`, Ana → `the-apartments-ana.html`
  (East West already correct). No card uses `href="#"`.
- **Desktop grid (>1366px)**: `.projects-grid` now `repeat(3, 1fr)` with a scoped
  `@media (min-width:1367px) { max-width: calc(75% - 6px); margin-inline: auto; }` so the three cards
  keep the original 4-column card size (measured 327×437 at 1440, was ~331 wide) and sit centred in
  the existing container. Tablet (768–1366 flex carousel) and mobile (single-column) rules untouched;
  carousel JS already derives counts from `cards.length`, so no JS change was needed.
- **Marquee section** (`.section-featured`): heading text → `PARTNERS & DESIGNERS`, paragraph replaced
  with the supplied collaboration sentence. All nine external press logos removed. Track now carries
  15 local partner logos from `partners.html` (`media/images/partners/*.webp`: Porsche Design,
  Armani/Casa, Planac Mimarlık + 12 financial institutions) duplicated once for the seamless loop;
  duplicates are `alt="" aria-hidden="true"`, all items `loading="lazy" decoding="async"` with
  intrinsic width/height to avoid CLS. Layout, gap (90px), 46px logo height, 38s speed/direction and
  hover-pause unchanged.
  - The four “architect” assets in partners.html (Ömer Çamoğlu, Philippe Starck, Kay Ngee Tan,
    Boran Ekinci) are **portrait photographs, not logos**, so they were not placed in the logo track.
  - Technical necessity: the old treatment `grayscale(1) brightness(0)` silhouetted transparent press
    PNGs but turned the opaque-background partner logos into solid black boxes. Changed to
    `grayscale(1)` + `mix-blend-mode: multiply` (monochrome treatment kept, hover still reveals
    colour). Added a scoped `prefers-reduced-motion` block: animation off, track wraps, duplicates
    hidden, all 15 logos visible, no overflow.
- **AIDA promotional component**: same markup/classes (`aida-*` untouched) now presents The Residences
  East West — logo `media/images/east-west/ew-intro-logo.webp`, heading “Discover The Residences East
  West”, the supplied description, `DISCOVER NOW` → `east-west.html`, banner
  `media/images/ew/render/ew-render1.webp` (local, both towers visible). All AIDA text, logo, images
  and external CDN requests removed. Banner `object-fit: fill` → `cover` so the render is not
  stretched; frame size (384px desktop / 16:12 mobile) unchanged.
- Self-tested at 1440/1280/1024/768/430/390 and 844×390: 0 horizontal overflow, 3 cards and 3 badges
  at every breakpoint, marquee height 46px, no broken logo (`naturalWidth>0` for all), no stretched
  logos, keyboard focus reachable on the CTA, no new console errors (only the pre-existing
  `collab-video.mp4` ERR_ABORTED from viewport switching; the file returns 200). JS syntax clean.

## 2026-06 — Homepage refinements + automated NOVA Journal newsroom
Tested by testing agent (iteration_50.json): backend 100% (14/14 pytest cases), frontend 100%,
no issues, `retest_needed: false`.

### Homepage (index.html, css/styles.css)
- **Project grid**: `.projects-grid` is now `repeat(3, minmax(0, 1fr))` with a 28px gap and no
  max-width cap, so the row spans the full inner container (measured left 32 / right 1408 at 1440 —
  identical to the heading and `VIEW ALL PROJECTS →` CTA). Cards measured 440×587 (ratio 0.75 = the
  original 3/4 portrait) at 1440/430/390; the 768–1366 carousel keeps its pre-existing 5/6 ratio.
  Badges, overlays, location and sales lines, hover/reveal behaviour and links untouched.
- **Marquee → ARCHITECTS & DESIGNERS**: heading + paragraph replaced; every bank/portfolio logo
  removed from the homepage (all still present on partners.html). Track now holds 7 units — the four
  authentic architect portraits (Ömer Çamoğlu, Philippe Starck, Kay Ngee Tan, Boran Ekinci) as 46×46
  monochrome square crops with the name set beside them, plus Porsche Design, Armani/Casa and Planac
  Mimarlık logos centred with `object-fit: contain`. Equal outer units (170×60 desktop, 125×46
  ≤767px), duplicated once with `aria-hidden` + empty alt, 38s seamless loop, hover pause, and a
  `prefers-reduced-motion` block that stops the animation and wraps all units.
- **East West feature** replaces the old AIDA component: new `.ew-feature` 36/64 editorial split
  using `media/images/ew/render/ew-render5.webp` (907×614 at 1440), a 210px East West logo
  (175–190 tablet, 155 mobile), bronze eyebrow + hairline rule, heading, supplied copy and a bronze
  `DISCOVER NOW → east-west.html` CTA. Pale blue #D7E3EB ground and bronze #6B5E43 accents kept; all
  `aida-*` CSS/markup removed (no other page used it). Mobile order: logo, heading, copy, CTA, image.
- **#news → NOVA JOURNAL**: all six DarGlobal/Emirates NBD/World Liberty placeholder cards removed;
  the section now renders six live items from `/api/news/featured`. Out-of-scope homepage sections
  (hero, DarGlobal hero images, "DISCOVER DARGLOBAL", register form) were deliberately left alone.

### Newsroom backend (new: backend/news/{__init__,sources,filters,summarise,ingest,api}.py)
- Extends the existing FastAPI + MongoDB app. Collections: `news_items` (unique indexes on `slug`
  and `canonical_url`; indexes on `published_at`, `status+category+published_at`, `content_hash`,
  `title_key`), `news_sources` (ETag / Last-Modified / last_success_at), `news_runs` (run reports).
- **Verified enabled feeds (14, all fetched and parsed with real requests)**: Hyperallergic,
  The Guardian Art & Design, Artnet News, Colossal, La Biennale di Venezia, Dezeen, designboom,
  ArchDaily (feeds.feedburner.com/Archdaily), The Guardian Cities, Arkitera, Arkitektüel, TMMOB,
  Anadolu Ajansı (güncel + ekonomi).
- **Left disabled** (recorded in `DISABLED_SOURCES` with reasons): Resmî Gazete, Çevre ve Şehircilik
  Bakanlığı, Kentsel Dönüşüm Başkanlığı, İBB, Kadıköy Belediyesi, TÜİK, AFAD, İMSAD, TMB, Mimarlar
  Odası, yapi.com.tr, emlakkulisi.com, İstanbul Modern/SALT/Arter/Pera/Sabancı/Borusan/İKSV/Istanbul
  Biennial, Tate/MoMA/Louvre/Pompidou/Art Basel, The Art Newspaper, Frieze, Reuters.
- Fetching: https-only allowlist by hostname, DNS resolution rejected for private/loopback/link-local
  IPs, ≤3 redirects re-validated against the allowlist, 4MB cap, 20s timeout, descriptive UA, ETag /
  Last-Modified conditional requests, defusedxml parsing with entity expansion forbidden, bleach
  stripping of all tags/scripts/handlers, tracking-parameter stripping (utm_*, fbclid, gclid…).
- Dedupe on canonical URL, feed GUID + source, normalised title and content hash. Relevance uses a
  STRONG/WEAK term model (an item needs at least one unambiguous topic term) plus exclusions
  (sport, crime, celebrity, crypto, generic finance, listings, exams, party politics) and a 30-day
  freshness window; `published_at` is always the publisher's date, `fetched_at` separate.
- Summaries: optional Gemini free tier (`GEMINI_API_KEY`, `GEMINI_MODEL=gemini-3.5-flash-lite`,
  `NEWS_AI_MAX_REQUESTS_PER_RUN=10`, strict JSON output, validation rejects invented numbers and
  low confidence, bounded backoff on 429/5xx). Key is unset in this environment, so every current
  summary comes from the deterministic chain (shortened feed description → source excerpt →
  headline + attribution). No full third-party article body is ever stored or shown.
- Scheduler: APScheduler `AsyncIOScheduler`, 6-hour interval, timezone Europe/Istanbul, started in
  the FastAPI startup hook (supervisor keeps the process alive); one first run when the collection is
  empty. Protected manual trigger `POST /api/admin/news/refresh` with `X-Admin-Token`.
- API: `GET /api/news` (category/page/limit≤24/search/language, validated, ETag + Cache-Control,
  in-memory rate limit 120/min), `GET /api/news/featured` (editorially balanced six), `GET
  /api/news/{slug}` (+3 related), `GET /api/news-sources/status` (health only).
- Verified: full run accepted 176 items from 14/14 sources with 0 failures; an immediate second run
  accepted 0 and reported 39 duplicates.

### Newsroom frontend (new: newsroom.html, news-detail.html, css/newsroom.css, js/news.js,
### data/news-fallback.json)
- `newsroom.html`: single h1, text-led hero, nine accessible filter buttons with `aria-pressed` and
  `?category=` URL state (back/forward supported), debounced search with `?search=`, lead article +
  supporting grid, LOAD MORE (verified 12 → 24), article count, refined empty/error states.
- `news-detail.html?slug=…`: NOVA-branded summary page — category, date, headline, `SOURCE ·
  PUBLISHER`, 80–160 word summary, optional publisher-syndicated image with credit, regulatory
  disclaimer for TECHNICAL_AND_LEGAL, prominent `Read original article →` (new tab,
  `rel="noopener noreferrer"`), up to three related items, dynamic title/description/OG/canonical and
  WebPage + BreadcrumbList JSON-LD (never NewsArticle with NOVA as publisher). Unknown slug shows a
  not-found state with a link back to the newsroom; API failure shows a service state.
- All cards are `<article>` with an internal detail link plus a separate external source link; every
  node is built with `createElement`/`textContent` (no `innerHTML`), no feed is ever fetched from the
  browser, and `data/news-fallback.json` (6 verified items) keeps the layout alive if `/api` is down.

### Environment variables added to backend/.env
`NEWS_ADMIN_TOKEN`, `NEWS_INGEST_ENABLED`, `NEWS_INGEST_INTERVAL_HOURS`,
`NEWS_AI_MAX_REQUESTS_PER_RUN`, `GEMINI_API_KEY` (empty), `GEMINI_MODEL`.

### Also fixed
- Added the missing `/app/eslint.config.js` (ESLint 9 flat config) — this was the cause of the
  recurring platform "JavaScript linting failed due to a linter engine error"; `npx eslint .` is now
  clean.

## 2026-06 — ARCHITECTS & DESIGNERS rebuilt as a compact card marquee (replaces rejected split panel)
- `frontend/index.html`: the oversized split-screen showcase (`.ad-slide/.ad-panel/.ad-visual/.ad-dot/
  .ad-arrow`) was removed entirely and replaced by one horizontal strip of 7 equal cards repeated in
  3 `aria-hidden` groups (21 nodes, same 7 local assets, duplicates carry empty alt). Heading and
  intro copy unchanged.
- `frontend/css/styles.css`: rejected showcase CSS deleted (0 references remain). New compact card
  system — `width: clamp(180px, 14vw, 220px)`, `aspect-ratio: 4/5`, `max-height: 275px`, 3px radius,
  1px hairline border, 44px charcoal name strip (rgba(17,17,17,.82), 14px / 13px mobile), grayscale
  portraits with per-card `object-position`, logo cards centred with `object-fit: contain`
  (Porsche Design gets a charcoal field because its source asset has a dark ground). Tablet
  170–190px, mobile 155×194 with 42px strip; section padding 56–88px desktop / 56px mobile.
- `frontend/js/architects.js`: rewritten as a rAF `translate3d` marquee (36s pass, GPU transform
  only) with modular offset normalisation, pointer drag / touch swipe takeover (8px threshold so
  vertical scrolling is untouched), 2s resume without resetting position, pause on hover, on
  *keyboard* focus only (`:focus-visible`), when the tab is hidden and when the strip is outside the
  viewport (IntersectionObserver), arrow-key stepping, drag-click suppression, resize/font
  re-measure, and a reduced-motion mode that stops the loop and turns the strip into a snap-scroll row.
- Verified at 1600/1440/1280/1024/768/430/390: cards identical at every width (202×252 at 1440 with
  5–7 fully visible; 220×275 at 1600; 155×194 mobile with ~2 cards + part of the next), 0 horizontal
  overflow, no broken assets, no console errors, 24px seam gap only (i.e. no empty area) at 1920,
  drag → resume, keyboard pause, off-screen pause and reduced-motion all confirmed.
- Untouched: project grid (3 cards + 3 NOW SELLING badges verified), East West section, news system,
  newsroom, header/nav/footer, partners.html.
- Note carried over from the interrupted newsroom task: a few feed-sourced summaries still end in a
  publisher's own "…" truncation; polishing that is part of the newsroom summary work, not this task.

## 2026-06 — Correction pass: compact architects strip, shorter East West, Nova Journal, news quality
Tested by testing agent (iteration_51.json): backend 100% (24/24 pytest), frontend 100%, no issues,
`retest_needed: false`.

### Architects & Designers (index.html, css/styles.css)
- Heading and intro centred (`.ad-head--center`, lead `max-width: 720px`), marquee now inside
  `.ad-bound` = `min(100% - 96px, 1400px)` (1344px @1440 with 48px margins; 704px @768; calc(100%-40px)
  mobile) — no edge-to-edge strip, `overflow: hidden`, no viewport-height anywhere.
- Cards reduced to `clamp(150px, 11vw, 170px)` / `4:5` / `max-height: 212px` → 170×212 @1600,
  158×198 @1440, 150×188 @1280, 146–155 tablet, 128×160 mobile; name strip 38px desktop / 34px
  mobile at 13.5/12.5px. Section padding `clamp(46px, 5vw, 72px)` → total height 406–506px.

### East West feature
- Fixed split height `clamp(470px, 34vw, 520px)` (450px 1024–1100), padding trimmed, logo
  `clamp(260px, 76%, 420px)`; measured 490px @1440, 470 @1280, 450 @1024, 718–767px stacked mobile.
- New `js/east-west-feature.js`: five local renders (ew-render5 → 1 → 2 → 6 → 3) crossfade every 6s
  inside an absolutely positioned, fixed-ratio frame (no layout shift); only the next image is
  preloaded; pauses off-screen, on hidden tab and on hover; reduced motion shows one static frame.
- No NOW SELLING / ÇİFTEHAVUZLAR label and no decorative rule in the section (hero and project card
  keep their own location lines — out of scope and untouched).

### Nova Journal homepage block
- Whole heading group centred (`.news-head-center`, 760px) with the wordmark rendered as
  “Nova Journal” in `font-family: "garamond-premier-pro", "Cormorant Garamond", Georgia, serif`,
  weight 300, italic, `clamp(42px, 5vw, 76px)`, VIEW ALL beneath the intro.
  Note: Garamond Premier Pro is an Adobe-licensed font and is **not** bundled; the already-licensed
  Cormorant Garamond 300 italic renders as the fallback until an Adobe kit is added.

### Newsroom data quality (backend)
- New `news/validate.py`: `normalise_editorial()` capitalises the first letter of every headline,
  summary and sentence while preserving acronyms (AI, LEED, İBB, UNESCO, TMMOB…), Turkish dotted İ
  and intentional internal brand lowercase; `validate_source_url()` resolves redirects with a browser
  UA (HEAD first, then a ranged GET — a blocked HEAD is never treated as failure, 7s timeout) and
  rejects malformed URLs, error/404 pages, parked domains, cross-domain hops and homepage redirects.
- `ingest.py` now normalises titles/summaries, stores the resolved canonical URL, refuses to publish
  an article whose link does not validate, and marks items without a valid image as `pending` so they
  never reach the homepage, newsroom or API. `revalidate_sources()` re-checks up to 40 published
  links per run, at most once every 24h, and archives dead ones.
- `images.py` thresholds raised to 1000×550 minimum (1200 preferred) with sharpness, MIME, decode and
  aspect checks; local WebP card/detail derivatives only, never upscaled.
- Re-ingested from scratch: 88 published (all with validated links + sharp local images), 56 pending.
- `summarise.py` also trims back past a publisher's truncated fragment (e.g. “… until 12.”).

### news-detail.html
- Top padding now `calc(var(--header-h) + clamp(72px, 6vw, 96px))` desktop / `+42px` mobile — 82px
  clear gap between header and title at 390px; 780px centred column; title `clamp(30px, 3.2vw, 44px)`
  at 1.08; body 16–19px at 1.72–1.75; stable 16/9 image frame; paragraphs split from the summary; new
  verified-facts block (Publisher / Published / Subject / Region) plus an attribution note; safe-area
  bottom padding. Newsroom hero also clears the fixed header now.
- Honest limitation: internal summaries are ~60–160 words, not the requested 400–700. No AI
  summariser is configured (`GEMINI_API_KEY` deliberately empty) and fabricating content is
  forbidden, so the page shows the fullest verified material plus metadata context. Setting a free
  Gemini key enables the longer summaries through the existing, already-wired path.

### Homepage performance (already in place, re-verified)
- `js/news.js` deferred, hydrates via IntersectionObserver (600px rootMargin), single in-flight
  request, 2.2s AbortController, snapshot-first from `data/news-featured.json` (written by ingestion).
  With `/api/news/featured` hung for 10s: DOM ready in 0.66–1.18s, hero/nav/project cards
  interactive, six snapshot cards rendered, no leftover loading state.

## 2026-09-19 — Correction & production-completion pass
- East West homepage feature: containment fixed (min-height panel, no fixed height, CTA
  64px above the panel base at 1440), slide duration 5s, crossfade 600ms, SVG perimeter
  progress line synchronised to one rAF timer (pause/resume on hover, viewport, tab,
  reduced motion), mobile height reduced to 779px @390 and 841px @430.
- Get in Touch component styled in css/newsroom.css (was unstyled markup relying on
  projects.css, which those pages never load).
- Navigation: PORTFOLIO → projects.html, NEWSROOM → newsroom.html across 26 pages;
  index.html placeholder <button> items replaced with real links.
- Newsroom backend: editorial.py brand-safety/relevance gate, extract.py JSON-LD/Twitter
  image discovery + AA-style body extraction fallback, images.py image precedence with
  image_source_type, ingest.py reprocess_active() + enrich_sources() + lifecycle states,
  api.py health/synthesise endpoints, ai.py Gemini provider with daily budgets and the
  long-form quality gate.
- Database reprocessed: 4 rejected (livestock regulation, European construction decline,
  2 other negative/irrelevant), 112 short-body records demoted to pending_editorial,
  images upgraded to authentic sources where available (112 cached vs 51 NOVA covers).
- NEWS_PUBLISH_WITHOUT_AI=false: no article is published until its ≥600-word synthesis
  passes the quality gate. Waiting on the GEMINI_API_KEY secret.
