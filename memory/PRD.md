# PRD — DarGlobal Homepage Clone (Nova Konut)

## Original Problem Statement
Create a pixel-perfect clone of `https://darglobal.co.uk/` homepage using ONLY vanilla HTML/CSS/JS. No frameworks. Match colors, fonts, images, videos, animations, layout and responsive behavior across all device sizes. Homepage only.

## User Language
**Turkish** — Always respond to the user in Turkish.

## Tech Stack
- Vanilla HTML5 / CSS3 / JS (no React, Vue, npm build steps)
- Static site served by `npx serve` on port 3000 (supervisor managed)
- Repo: `https://github.com/kaankara34/nova-2026-purejs`

## Code Architecture
```
/app/frontend/
├── index.html              # Main HTML
├── css/styles.css          # All styling (mobile/iPad/desktop responsive)
├── js/script.js            # Carousel logic, animations
├── media/images/           # Local images & SVG logos
└── media/videos/           # Hero video assets
```

## What's Implemented (latest session — Feb 2026)
- **Project card SVG logos (final, user-supplied set)** — 4 distinct combined logos applied to 4 cards, transparent zemin, krem-altın renkler, sıkı viewBox:
  - Çiftehavuzlar → `EASTWEST_logo-tight.svg` (THE RESIDENCES / EAST WEST)
  - Selamiçeşme → `TAC_logo-tight.svg` (THE APARTMENTS / TAÇ)
  - Göztepe → `ANA_logo-tight.svg` (THE APARTMENTS / ANA) — kart altyazısı "Taç"tan "Ana"ya güncellendi
  - Kalamış → `GUR_logo-tight.svg` (THE APARTMENTS / GÜR)
  - Source SVGs are clean (no white/black bg rects), only fills `#f5f4ee` + `#a8997a`. Tight viewBoxes computed via `getBBox()` so içerik dış boşluksuz oturuyor.
  - **Logo konumu:** Kart merkezi (absolute, top:50% left:50% transform translate(-50%,-50%)). `.name` artık `.info` dışında, doğrudan `.project-card` çocuğu. Konum/etiket altta kalmaya devam.
  - **Boyutlar:** desktop %78 (max 280px), iPad %78 (max 220px), mobile %70 (max 280px), drop-shadow `0 2px 8px rgba(0,0,0,0.55)` (gradient üzerinde okunabilirlik için).
- iPad carousel touch/mouse logic + horizontal progress bar (#6F6243).
- Register Interest section recolored (`#4F6B57` bg, `#D6E3EB` text).
- Desktop project grid gap 22px; iPad cards 5:6 ratio + 30% smaller landscape, 1.5× portrait.
- AIDA mobile re-stacked (image top → logo overlay → text/button below).
- Mobile bottom CTA bar: 2-second repeating shine animation.
- Cookie banner z-index 200 (over mobile bottom bar).
- News section: 2×2 grid on tablet/mobile.

## Pending / Backlog
### P1
- Pixel-perfect padding/margin/font-size audit, section by section vs `darglobal.co.uk` (Hero → AIDA → Projects → News → Register Interest). Incremental, no global changes.

### P2 (only if requested)
- Inner pages (Projects detail, About, etc.).

## Design Tokens (in use)
- Gold accent: `#a8997a`, `#e0cfa5`, `#f5e9d2`
- Carousel progress: `#6F6243`
- Register Interest bg: `#4F6B57`, text `#D6E3EB`
- Serif: `var(--font-serif)`

## Critical Notes for Future Agents
- **Vanilla only.** No React, no build steps, no npm install of frameworks.
- **Turkish only** when communicating with the user.
- **Incremental** UI changes — user rejects broad/global CSS edits.
- Always test with `mcp_screenshot_tool` after visual changes.
- Preview URL: `https://darg-clone-1.preview.emergentagent.com` (no `frontend/.env`; this URL comes from the env var `preview_endpoint`).
- Git pulls from `kaankara34/nova-2026-purejs` may need direct URL fetch+merge (not plain `git pull`).

## Session — May 2026 (East West Project Page)

### New page: `/east-west.html`
Structural clone of darglobal.co.uk/trump-plaza/executive-residences with Nova-themed placeholder content. User explicitly chose "Option B - Structural Clone".

**Sections built (top → bottom):**
1. **Hero** — Full-screen background image, gold ken-burns animation, "THE RESIDENCES EAST WEST" title (Cormorant Garamond), tagline, sub-text. Top-right pills: "Download Brochure" / "BOOK UNIT". Bottom-right "Gallery" trigger.
2. **Gallery** — 3-image grid (1 large + 2 small), hover zoom, "VIEW ALL" → lightbox.
3. **Property Specs** — 6-column table (Property Type, Unit Type, Features, Area SQM, Status, Expected Completion). Collapses to 3-col tablet, 2-col mobile.
4. **The Club at East West** — Hero image + heading + description, then 4-col amenities grid (10 tiles: golf simulator, spa, coffee lounge, pools, recovery, fine dining, cigar lounge, members lounges, performance space, day care).
5. **Why Invest in Istanbul** — 11 numbered investment reasons (Turkey/Istanbul context — citizenship by investment, Bağdat Caddesi, etc.) + sticky side image.
6. **Location** — Title + lead + description + brochure preview image + map card with address (Çiftehavuzlar, Bağdat Caddesi).
7. **Enquire Now Form** — Full Name, Code+Phone, Email, Project select, Source select, Privacy/Newsletter checkboxes, Submit (UI-only).

### Files added
- `/app/frontend/east-west.html` (full page, ~25KB)
- `/app/frontend/css/east-west.css` (page-specific styles, ~18KB)
- `/app/frontend/js/east-west.js` (lightbox gallery + form handler, ~3KB)
- `/app/frontend/serve.json` (rewrites `/east-west` → `/east-west.html`, disables clean URL redirects)

### Wired up
- Homepage project card: "THE RESIDENCES EAST WEST" → links to `east-west.html`
- Mega menu sub-accordion: same link
- Shared navbar, side-menu, mobile-bottom-bar, footer reused 1:1

### Responsive verified (screenshots)
- Desktop (1920px): 6-col specs, 4-col amenities, 2-col form, sticky image in invest
- iPad (1024px): 3-col specs, 3-col amenities, single-col invest+club
- Mobile (430px): 1-col gallery, 2-col specs/amenities, stacked form fields, map info overlays at bottom

### Other UI tweaks this session
- Section titles (`LATEST LUXURY...`, `EXCLUSIVE COLLABORATIONS`, `ARTICLES & NEWS`) → Cormorant Garamond 23px, letter-spacing 0.02em, weight 700 (added 700 to Google Fonts link)
- `BUILD BEYOND LIVING` menu item → Cormorant Garamond 16px, weight 600
- Side-menu footer brand block: nOva logo + "BUILD BEYOND LIVING" tagline; full-width horizontal divider on mobile via negative-margin trick
- Side-menu footer absolutely positioned to initial panel (420px) so center stays fixed across menu expansion states
- Custom always-visible gold scrollbar (`#6f6243`) on `.col-projects` via custom div overlay (Chromium native scrollbar wasn't reliable)
- Mobile mega menu (≤1100px): submenu now slides in from right with back-arrow header, accordion sub-items inline (darglobal-style)



## Session — Feb 2026 (Martı Residence Project Page)

### New page: `/marti-residence.html`
Structural adaptation of DarGlobal's **Trump International Hotel & Tower Dubai** page, using the East-West shell (shared navbar / utility bar / footer / mobile bottom bar / side menu). English copy, generic luxury-residence tone; placeholder images (user will supply real assets later).

**Sections built (top → bottom):**
1. **Utility bar + Header + Mobile bottom bar + Side menu** — Identical to East-West; side menu ISTANBUL sub-accordion updated to include a Martı Residence entry pointing to `marti-residence.html`.
2. **Hero** — Full-viewport static image (marti-cover-xl.png) with the standard `.ew-gallery-trigger` (kept `display:none` like East-West).
3. **Action strip** — GALLERY + BOOK UNIT + DOWNLOAD BROCHURE.
4. **Intro** — Cormorant title "Martı Residence" + location "Suadiye, Istanbul" + tagline + sub-copy.
5. **Gallery slider** — 8-slide `.ew-slider` (auto-play + arrows + progress dots + swipe/drag) driving the same `#ewLightbox`.
6. **Property Specs** — 6-item grid (property type, unit type, status, areas 115–340 sqm, expected completion Dec 2028, featuring: sea views).
7. **Manifesto — "A New Standard On The Coast."** — Trump-Dubai-style "Challenge Everything" block: title + lead paragraph + 3-image grid (hover zoom) + "View All Images" opens gallery lightbox.
8. **Key Features (Three Worlds)** — Three alternating image/text blocks: The Martı Residences, The Martı Marina Club, The Waterfront Retreat.
9. **Amenities** — Club hero image/heading (`.ew-club`) + 10-tile amenities grid.
10. **Typical Apartments** — 4 tabs (2+1, 3+1, 4+1, PENTHOUSE) with Martı-specific plan data, prev/next arrows, expand-to-lightbox, and A4 download branded "MARTI RESIDENCE — SUADIYE". No EAST/WEST tower toggle (only one tower).
11. **Investment — "A Life Authored On The Coast"** — 11 numbered items alongside image.
12. **Location** — Title + lead + description + OpenStreetMap iframe centered on Suadiye (40.960°N / 29.080°E) + Google Maps link + address card.
13. **Nearby** — 10 nearby-place cards (Bağdat Avenue, Suadiye Waterfront, Kalamış Marina, Marmaray, Göztepe Park, Fenerbahçe, Akasya, Emaar, Eurasia Tunnel, Zorlu Center) with recomputed distances from Suadiye.
14. **FAQ** — 8-question accordion with `+`/`–` icon flip + gold accent color on open + single-open behaviour (opening one closes the previous).
15. **Register Your Interest** — Enquire form with Martı Residence pre-selected in project dropdown; submit validation (Full Name + Email + privacy required).
16. **Footer** — Identical to East-West; "Discover Luxury Properties" list adds Martı Residence link.

### Files added
- `/app/frontend/marti-residence.html` (full page, all sections)
- `/app/frontend/css/marti-residence.css` (hero-still, intro title, manifesto grid, three-worlds features, FAQ accordion, enquire lead — loaded on top of `east-west.css` so all `.ew-*` layout classes are reused for free)
- `/app/frontend/js/marti-residence.js` (gallery + slider + swipe + Martı-specific PLANS array + FAQ single-open accordion + A4 print branded for Martı)

### Files updated
- `/app/frontend/projects.html` — Martı Residence card now links to `marti-residence.html`.
- `/app/frontend/serve.json` — added rewrite `/marti-residence → /marti-residence.html`.

### Placeholder / to be replaced by user
- Hero image (marti-cover-xl.png used for now — no dedicated hero video yet).
- All gallery, amenity, manifesto and three-worlds imagery are reused East-West renders/photos as temporary placeholders.
- Floor plan images point to East-West artifact URLs; unit m² figures are illustrative until real Martı data is supplied.
- Nearby-place distances are estimates from Suadiye coordinates — verify with real address.

### Testing (iteration_7.json)
- Frontend regression PASS at ~92%. All interactions verified: gallery lightbox open/close/keyboard/prev-next, action-strip buttons, plan tab switching + arrows + expand, FAQ single-open accordion, form validation (empty + no-privacy rejected; valid submit → Thank-you alert), mobile 375×800 has no horizontal overflow and three-worlds blocks stack single-column, no JS console errors.
- Known non-issues: `.ew-gallery-trigger` `display:none` (intentional, same as East-West — action strip is the primary gallery entry). Clean-route `/marti-residence` returns index at the ingress level (pre-existing platform behaviour, identical to `/east-west` and `/projects`); `.html` URLs work.

### Post-review redesign (Feb 2026) — reference-driven visual identity
User feedback: the first Martı build looked too much like East-West. Rebuilt three signature sections to match the DarGlobal Trump Dubai / Da Vinci Tower editorial language while keeping the shared shell:
- **Intro** → replaced small East-West-style intro with a full editorial block: massive all-caps display title `MARTI RESIDENCE, BY THE SEA` (Cormorant Garamond, clamp 52-128px), gold pipe-separated location `SUADIYE  |  ISTANBUL, TÜRKİYE`, two centred editorial paragraphs.
- **Property Specs** → replaced 6-across grid with a 3-column × 2-row editorial grid: gold `#a69168` uppercase labels + Cormorant value + `#eae4d3` horizontal rule between rows (mirrors reference exactly). Collapses to 2-col on tablet and 1-col on small mobile.
- **Register Your Interest** → completely rebuilt on a deep burgundy `#4a1e26` background with vignette gradient. Split layout: LEFT column is a three-line massive title (`REGISTER` / `YOUR` / `INTEREST`) stacked with a lead paragraph. RIGHT column is a minimal underline-only form (transparent inputs, cream underline that brightens on focus), added an `Additional Comments` textarea, custom SVG chevrons on selects, custom cream check-tick on burgundy checkboxes, and a cream `REGISTER INTEREST` submit button. All prior `.ew-enquire` / `.marti-enquire-lead` styles removed.

## Pending / Backlog (updated Feb 2026)

### Recent fix (Feb 2026)
- **Mobile status-badge alignment** on Martı + 9 clone pages (bahar, mehtap, dogan, mercan-bosphorus, nisbetiye-on, falcon-plaza, falcon-logistic, konelsis-center, gebze-osb-management). Rebuilt the `<520px` block using CSS Grid inside `.[prefix]-status` so the icon sits on row 1 aligned with the primary label (ALL UNITS SOLD / COMPLETED PROJECT), and the sub-caption ("Fully subscribed" / "Delivered 2019") spans both columns centred on row 2. `.[prefix]-status-text` uses `display: contents` so its children become direct grid items. Vertical gap between the two status badges increased to 24px. Verified visually at 390px and 320px. Propagated with `/tmp/sync_status_fix.py`.

### P0
- None open — page functional and tested.

### P1
- Replace Martı placeholder assets with real renders, interior images, amenity photos, hero video, and real floor plan drawings when the user supplies them.
- Update Martı floor plan net/gross m² and room breakdowns in `js/marti-residence.js` PLANS array with real project data.
- Update East-West A4 print net/gross m² values with real project data in `js/east-west.js` (still using placeholder metrics from earlier session).

### P2
- Additional project pages (Mehtap, Mercan, Doğan, Bahar) built from the same shared East-West/Martı shell.
- Verify nearby-place distances and content with real client data.
- Cross-browser A4 print/PDF test (Chrome / Safari / Edge) for both East-West and Martı floor-plan download.

## Bug fix: menu/lightbox close scroll-jump (Aug 2026)
Root cause: `html { scroll-behavior: smooth }` in `styles.css` made `window.unlockScroll()`'s `window.scrollTo(0, y)` animate from the top instead of jumping instantly, causing a visible "jump to top then scroll back down" every time `menuClose`/`ewLightboxClose` (or any modal close) fired. Fixed once in the shared `window.unlockScroll()` in `js/script.js`: temporarily sets `documentElement.style.scrollBehavior = 'auto'` before the restore scroll, then restores it. Applies automatically to all 13 pages (all load `js/script.js`). Verified via frame-by-frame `scrollY` sampling on east-west.html and mercan-bosphorus.html — no more animation ramp.

**Pending user decision:** user asked whether media quality was reduced during the perf cleanup. Answered: Bahar/Mercan/Martı hero videos = zero quality loss (pure remux/copy). East-West hero video was re-encoded at CRF 27 (visually lossless but not bit-identical) to shave extra size. Offered a lossless remux-only alternative (26.5MB vs current 24.3MB) — awaiting user's choice (kept as-is vs swap to lossless).

## Mercan Bosphorus — Key Features + Amenities redesign (Aug 2026)
User provided DarGlobal reference screenshots (desktop + mobile) for a "KEY FEATURES" 3-card grid and a new "AMENITIES OF ..." split section, asked to convert `mercan-bosphorus.html`'s existing Key Features block to this format and add a new Amenities section below it, reusing content already present on the page.
- **Key Features**: replaced the 3 alternating image/text blocks with a `.mercan-features-grid` of 3 cards (image top, bold title, description) — desktop = 3-col grid, mobile (<900px) = horizontal scroll-snap peek-carousel with dot indicators synced via scroll listener in `mercan-bosphorus.js`. Same 3 existing feature texts reused (fixed a pre-existing typo: "oughtfully" → "Thoughtfully"). Slideshow images (`.mercan-slideshow`/`.mercan-slide`) and lightbox-tile behavior (`.mercan-features-img img` selector) untouched/still work.
- **Amenities** (new section): title + lead + a 14-item icon+label list (all real Mercan amenities pulled from the existing features lead paragraph: pools, gym, boxing ring, basketball/tennis courts, sauna, steam room, Turkish bath, gardens, 24/7 security, parking, storage, backup power) with hand-authored minimalist line-icon SVGs, 2-col on desktop next to a large image (`mercan-fitness2.webp`), single-col list with an overlapping white card-over-image treatment on mobile (matches reference's card-overlap style).
- Verified via screenshot at desktop (1920px) and mobile (390px): both sections render correctly, mobile carousel dots sync on scroll, mobile amenities overlap-card renders with shadow as intended, no new console errors.

## Site-wide performance & unused-resource cleanup (Aug 2026)

**Root cause found:** all 4 hero videos on the site (`ew-hero-web.mp4`, `bahar-2k-web.mp4`, `mercan-2k-web.mp4`, `marti-video.mp4` — the last one shared by the 7 unfinished clone pages) had their MP4 `moov` atom positioned at the END of the file instead of the front. This forces the browser to buffer almost the entire file before it can read metadata and start playback — the real cause of the slow hero-video start reported by the user.

**Fixes applied (propagated identically to all 10 residence pages + east-west.html):**
- Remuxed all 4 hero videos with `ffmpeg -movflags +faststart` (lossless, `-c:v copy`) so metadata loads first and playback can start almost immediately.
- Stripped the unused (muted, autoplay) audio tracks from all 4 videos — extra bytes with zero playback benefit.
- East-West hero video was additionally re-encoded (CRF 27) and moved from the external `customer-assets.emergentagent.com` CDN to local `/media/images/east-west/videos/ew-hero-web.mp4` (27.7MB → 24.3MB, now same-origin, cached via `serve.json`).
- Generated a lightweight WebP poster frame for every hero video (`<video poster="...">` + matching `<link rel="preload" as="image">` in `<head>`) so the first frame paints instantly instead of a blank/black box while the video buffers.
- Removed the now-unused `<link rel="preconnect" href="https://customer-assets.emergentagent.com">` from `east-west.html`.
- Localized the East-West intro logo image (was on a second external domain `customer-assets-agu9un31.emergentagent.net`) to `media/images/east-west/ew-intro-logo.webp` (21KB PNG → 6KB WebP, same-origin now).
- Fixed an orphan `<link rel="preload">` on `index.html` pointing to `menu-thumbs/tac-ai-render.webp`, which is never used on that page (the page actually renders `tac-new-render.webp` for that card) — corrected the preload target so the browser stops fetching a file it never rendered.
- Deleted 7 fully orphaned pre-WebP-conversion originals with zero references anywhere in the codebase (~30MB): `tac-ai-render.jpg`, `mehtap-cover.png`, `dogubati_render.png`, `marti-cover-xl.png`, `east-west.png`, `residences_cover.png`, `east-west-cover.png`.

**Verified:** all new/moved asset URLs return HTTP 200 via curl through the live preview domain; `ffprobe` confirms `moov` now sits immediately after `ftyp` (before `mdat`) on all 4 videos; screenshots of `east-west.html`, `mercan-bosphorus.html` and a clone (`falcon-plaza.html`) show correct hero rendering with no visual regression.

**Note for next agent:** `index.html`'s main rotating hero background still points to 3 images on the original reference domain `cdn.darglobal.co.uk` (DarGlobal's own CDN, e.g. `OMA_05_Cliffhanger_room...png`). These are actively used (not orphaned) so they were left untouched, but they are third-party branded reference images on a live Nova Konut page — flag to user before replacing with real Nova assets.
- Known env quirk: the screenshot tool's headless Chromium in this sandbox cannot decode ANY local H.264 mp4 (readyState stays 0 even for a video untouched in this session, e.g. `collab-video.mp4`) — this is a sandbox codec limitation, not a real regression. Rely on `ffprobe`/curl range-request checks + visual screenshot of the page (not direct video-state JS checks) to validate video fixes in this environment.
