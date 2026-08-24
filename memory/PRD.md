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

## Mercan Bosphorus — slideshow transition: slide → fade-in (Aug 2026)
User changed their mind after the slide-effect implementation: wanted a simple fade-in crossfade instead (1.5s interval). Reverted `.mercan-slide` CSS from the translateX slide (`is-prev`/`is-active` transform states) back to opacity crossfade (`transition: opacity .9s ease`), and simplified `tick()` in `mercan-bosphorus.js` back to plain class toggle (no setTimeout reset dance needed for opacity). Verified via frame-by-frame opacity sampling: ~1.1s hold + 0.9s smooth fade, repeating every ~2s.

## Site-wide CSS/JS caching bug (Aug 2026)
User reported the slideshow speed/slide-effect fix from the previous turn "wasn't applied" even though the code was correct. Root cause: `serve.json` had `Cache-Control: public, max-age=604800` (7 days) on all `.css`/`.js` files — the user's browser was serving its own 7-day-old cached copies of `mercan-bosphorus.css`/`.js` and never re-requested them, so code fixes never reached their browser even though they were correctly deployed server-side (verified via fresh-context Playwright frame-by-frame sampling: 1.5s interval, smooth 0.7s ease-out slide transition, pixel-equal card widths all confirmed working). Fixed by changing `**/*.{css,js}` Cache-Control to `no-cache` in `serve.json` + restarted frontend (supervisor).
**Lesson for next agent:** if a user insists a verified/tested CSS or JS fix "isn't showing" on this static site, check `serve.json` cache headers and ask for a hard refresh (Ctrl/Cmd+Shift+R) before assuming the code itself is wrong — HTML already had `no-cache`, only css/js had the long max-age.

## Mercan Bosphorus — Key Features/Amenities polish round 2 (Aug 2026)
- Slideshow (Wellness & Landscaped Gardens cards): interval 500ms → 1500ms; replaced cross-fade with a horizontal slide transition (incoming slide enters from right, outgoing exits left, `.mercan-slide`/`.is-active`/`.is-prev` transform states in `mercan-bosphorus.css` + rewritten `tick()` in `mercan-bosphorus.js`).
- Fixed a reported 1px width mismatch between feature-card images: `.mercan-features-grid` switched from CSS Grid (`1fr` tracks, which can round sub-pixel differently per column at some viewport widths) to Flexbox with `flex:1 1 0` + `min-width:0`, which is deterministic.
- "All Units Sold" checkmark icon changed from a single tick to a double-check (✓✓) icon — applied identically across all 10 residence pages (shared markup, single sed-based bulk edit) for site-wide sync.
- Amenities list: "Tennis Court" replaced with "Historic Landmark" (with a matching monument/colonnade icon) per user confirmation there's no tennis court on the real Mercan Bosphorus site; also removed the stray "tennis courts" mention from the Key Features lead paragraph.
- Verified via screenshot: equal card widths, slide-in transition working, 1.5s cadence, double-check icon renders correctly, amenities list updated.

## Mercan Bosphorus — Typography harmony fix (Aug 2026)
User correctly flagged that the new Key Features/Amenities titles used a heavy 800-weight uppercase sans font that clashed with the rest of the page's identity (`MERCAN BOSPHORUS` hero + `.mercan-manifesto-title` both use Cormorant Garamond serif, weight 400, letter-spacing 0.03em, natural title-case — not uppercase bold sans). Fixed by matching that exact pattern: section titles → Cormorant Garamond 400 (`Key Features`, `Amenities of Mercan Bosphorus`, title-case not caps), card titles (h3) → Cormorant Garamond 400 smaller size, all lead/body copy → Montserrat 300 `#4a4a4a` (matches `.mercan-manifesto-lead`/`.mercan-intro-body p` exactly), amenity icons → `#1a1a1a` (was gold). Verified via screenshot at 1920px and 390px.
**Lesson for next agent:** before styling any new section on an existing page, grep the page's other section title/lead CSS rules first (font-family/weight/size/letter-spacing/color) and reuse those exact values — don't invent new typography even if it "looks fine" in isolation.

## Mercan Bosphorus — Key Features/Amenities CSS override bug fix (Aug 2026)
User reported the new sections didn't visually match the reference at all (fonts/margins/spacing all off). Root cause: `mercan-bosphorus.css` had a **stale duplicate** `.mercan-features`/`.mercan-manifesto` CSS block further down the file (leftover from an earlier session) that came AFTER my new rules in cascade order — it was silently overriding all new typography/spacing with the old tiny eyebrow-label title, serif lead, and old block layout. Deleted the entire duplicate block. Also tightened fidelity to the reference: Key Features bg → light gray `#f6f5f2`, title → bold 800-weight uppercase Montserrat heading (was a tiny 12px label), lead → sans-serif (was serif), card image ratio → 16:9; Amenities title → bold uppercase, icons → dark/black (was gold-accent, reference uses same color as text), image column now stretches to match text-column height instead of a fixed shorter aspect-ratio. Verified via screenshot at 1920px and 390px — now matches reference proportions closely.
**Lesson for next agent:** always check for duplicate/orphaned CSS blocks later in the same file when new styles don't seem to apply — `grep -n ".mercan-features-title"` (or similar) across the whole CSS file before assuming the issue is in the new rule itself.

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

## About page — Apple-style GSAP scroll animations + colour theming (Aug 2026)
User feedback on the first About rebuild: sections felt "too white/stacked/plain", wanted real GSAP scroll animations (not static), section colours changing as you scroll (Apple-style), and the flat "NOVA" ghost-text watermark in the manifesto section replaced.

**Implemented (`about.html`/`css/about.css`/`js/about.js`):**
- Fixed top scroll-progress bar (`#abScrollProgress`, vanilla JS, no GSAP dependency — works even if GSAP fails).
- Manifesto ghost text → animated SVG compass/globe motif (`.ab-manifesto-orbit`, reuses the site's existing globe icon language), continuous slow rotation + scroll-scrub scale/opacity breathing.
- All 12 major sections carry `data-theme="#hex"`; GSAP ScrollTrigger updates `document.body` background-color + `<meta name=theme-color>` to the active section's colour as you scroll (mobile browser-chrome tinting + overscroll-bounce colour match). Theme is also applied immediately on load (first section), not just on first scroll toggle.
- "Living background": 6 flat-colour sections (discover/manifesto/quote/split-gray/leed/collab) get a subtle scrub-driven `backgroundColor` tween so their own tone visibly deepens as you scroll through them.
- Word-by-word stagger reveal (`.gs-words`/`.gs-word`) for the manifesto lead paragraph — JS splits into word spans separated by real text-node spaces (kept copy/paste + screen-reader safe, no CSS margin hack).
- LEED image reveal changed from one-shot duration tween to scroll-scrubbed clip-path wipe.
- **Robustness fix (was a real bug):** `revealStatic()` fallback now runs whenever GSAP/ScrollTrigger fails to load OR `prefers-reduced-motion` is set, BEFORE any early return — previously the whole page could render blank (opacity:0 stuck) if the GSAP CDN was unreachable. Also sets stat number to final value (`10+`) instead of leaving literal `0`.
- Image swaps: `about_trust.webp` replaced twice (final version = muted dusk/pink-sky glass-balcony facade, low saturation, matches gold/cream palette); `about_cta1.webp` replaced with a warm luxury living-room interior.
- `.ab-partner` (Partner With Nova CTA) contrast fixed: image opacity .28→.22, added `::before` dark gradient overlay, body-copy colour bumped to `rgba(255,255,255,.94)`.
- `.ab-stats-overlay` darkened slightly (`.62`→`.72` alpha) for label contrast over the bridge photo.
- Footer "ABOUT NOVA" links (`href="#"`) fixed to `about.html` on all 10 other pages (bahar/dogan/east-west/falcon-logistic/falcon-plaza/gebze-osb-management/konelsis-center/marti-residence/mehtap-residence/mercan-bosphorus) — now consistent with the side-menu link.
- Bugs caught+fixed mid-session: `.ab-final-title` two `.gs-line` spans rendered on one line with no space (missing `display:block`, fixed); word-stagger split initially used trailing-space-inside-inline-block which visually collapsed all spacing (fixed by inserting real sibling text nodes between word spans).

**Tested:** `testing_agent` 3 passes (`iteration_8` pre-GSAP baseline, `iteration_9` found 1 HIGH + 4 MEDIUM/LOW + 3 design nits, `iteration_10` re-verified all 6 targeted fixes = 100% pass). Two trivial LOW nits from iteration_10 (theme-init ordering vs GSAP guard, partner body-copy contrast) were also fixed post-report and screenshot-verified (zero console errors, theme-color = `#0a0a0a` on load, GSAP-blocked fallback fully visible with `10+` stat).

**Pending user verification:** user has not yet seen the final live version — flag for their review next session.

## GitHub pull merged (Aug 2026) — user's direct edits to about.html
User edited `about.html`/`css/about.css` directly on GitHub (`kaankara34/nova-2026-purejs`, commit `1c0526c "about some arrangement"`) and asked to pull it in. Fast-forwarded cleanly (local `main` was an ancestor, no conflicts): removed mobile-bottom-bar from about.html, removed `.ab-quote`/`.ab-stats`/`.ab-trust-badge`/eyebrow labels/`.ab-partner` CTA section, rewrote most section copy with real Nova Konut brand voice (founding 2000, TBDY 2018/TS 500/TS 498/TS EN 206 engineering codes, etc.), merged discover title to one line, added a new `.ab-collab`-styled "Nova Description" block after the hero.
**Known gap introduced by this edit (not fixed — flagging, not user's explicit ask yet):** the entire `#register`/`#abForm` "Register Your Interest" section was deleted from `about.html`, but the header "REGISTER INTEREST" button and final-CTA "GET IN TOUCH" button still have `data-scroll="register"` — clicking them now does nothing (silently no-ops via `$('#register')?.scrollIntoView()` in `script.js`, no crash but a dead-end UX). Ask user whether to re-add a register section/anchor to about.html, or point those two buttons elsewhere (e.g. `index.html#register` or a mailto/WhatsApp action).

## About page — corporate/visual refinement pass (Jun 2026)
User feedback (5 screenshots): discover section invisible until scroll on desktop + globe icon irrelevant, dark serif intro section needed to look heavier/corporate, Build Beyond Living reveal too slow, LEED clip reveal intermittent, Engineered/Trust images off-brand, hero image too weak for a corporate about page, font sizes inconsistent between sections. Copy must not change.

**Implemented (`about.html` / `css/about.css` / `js/about.js`):**
- `.ab-discover`: all `gs-*` animation classes removed → always visible (no scroll dependency). Globe SVG replaced with a 64px gold hairline rule; layout changed from centered stack to asymmetric 2-column grid (serif title left, body right behind a vertical hairline), left-aligned glow. Mobile stacks with a top hairline.
- New `.ab-story` section (replaces `.ab-collab`+`.ab-nova-description` reuse for the dark intro band): copy split into 3 real `<p>` (wording untouched), gold hairline+diamond dividers top/bottom, faint 96px gold grid texture masked radially, serif drop-cap on the first paragraph, tighter measure (1000px).
- Unified type scale tokens on `body.page-about` (`--ab-fs-display`, `--ab-fs-h2`, `--ab-fs-kicker`, `--ab-fs-body:16px`, `--ab-lh-body:1.85`) applied to discover/vision/final (display), leed/split/collab (h2), manifesto kicker, and every body paragraph — removes the 15px/16px + 42/44/58/62px inconsistencies.
- Manifesto word reveal sped up + smoothed: duration 0.6→0.38, stagger 0.018→0.006, ease power2.out, start `top 92%` (total ~1.85s → ~0.8s).
- LEED clip reveal kept scroll-scrubbed but made reliable: explicit `gsap.set` initial clip, `scrub: 0.4`, `invalidateOnRefresh: true`, plus `ScrollTrigger.refresh()` on window load, on each late-loading `<img>` load and on `document.fonts.ready` (root cause: lazy images resizing layout after triggers were measured).
- Images (Unsplash/Pexels stock, per user choice): hero → Istanbul Levent tower skyline at sunset (`about_hero.webp`); Engineered To Endure → monochrome structural concrete geometry (`about_engineering.webp`, new); Built On Trust → sharp black/white residential tower facade (`about_trust.webp`). Deleted now-unused `about_life.webp`.

**Verified by screenshot automation:** discover title visible at load (opacity 1, no scroll), story section renders 3 paragraphs + drop cap + dividers (desktop & 390px mobile), LEED clip-path progresses 100%→0% while scrolling and lands at `inset(0 0 0%)`, manifesto last word reaches opacity ~1 within ~1s, new images render un-cropped, zero console errors.
**Pending user verification.** Still open from previous session: dead `data-scroll="register"` buttons on about.html (`#register` section was removed upstream) — user has not answered yet.

### About refinement follow-up (Jun 2026, same session)
- Scroll-progress bar removed entirely (HTML div, CSS `.ab-scroll-progress`, JS updater) per user request.
- LEED clip reveal made much slower/perceptible: trigger range widened to `start: 'top bottom'` → `end: 'bottom 35%'` with `scrub: 1.2` (verified progressing 84%→20% across ~1150px of scroll).
- Discover heading reworked: short gold dash replaced by a gold diamond ornament flanked by fading hairlines; title split (copy unchanged) into a sans `DISCOVER` kicker (12px / 0.34em) + large serif `Nova Konut` with a warm dark→gold text gradient and a fading gold hairline underline beneath the head block.
- User rejected the decorative ornaments ("kıro"): discover diamond/hairline mark, gold gradient text and underline all removed → now purely typographic (small muted sans `DISCOVER` kicker + solid serif `Nova Konut`, tighter tracking), glow reduced to .06 alpha. Story band dividers simplified to a single 1px `rgba(255,255,255,.13)` rule (diamond + gradient lines dropped).
- Engineered To Endure / Built On Trust images: new `.gs-img-drift` treatment — scroll-scrubbed (0.9) scale 1.18→1.10 + yPercent 3→-3 drift, geometry chosen so the drift never exposes container edges. Verified transform changes across scroll.

## Team page (`team.html`) — new, Jun 2026
Reference: https://www.rsd.com.tr/ekibimiz (analysed via crawl). User choices: placeholder team data for now (to be replaced on GitHub), no photos → initials monogram, English copy, same 4 department groups as RSD, linked only from side menu NOVA KONUT > TEAM.

**Built:**
- `/app/frontend/team.html` — generated by `/app/scripts/build_team.py`, which slices the utility bar + header + side menu + get-in-touch strip + footer straight out of `about.html` so site chrome stays byte-identical; team data lives as a Python list in that script (regenerate after editing). Header uses the default dark `.site-header` (no `transparent`) since the page has no hero image; header REGISTER INTEREST is an `<a href="index.html#register">` (avoids the dead `data-scroll="register"` problem).
- `/app/frontend/css/team.css` — old-money palette on `body.page-team` (ivory `#f4f1ea`, graphite `#1b1a17`, muted gold `#9a8253`, hairline `rgba(27,26,23,.14)`), intro block (eyebrow / serif h1 / lead), department groups as `220px + 1fr` grid with sticky label, 2-col hairline-separated card grid, monogram circle, responsive at 1024px (label static) and 700px (single column), reduced-motion guard.
- `/app/frontend/js/team.js` — IntersectionObserver adds `.is-visible` with 70ms staggered `transition-delay` (no GSAP on this page).
- Side-menu `TEAM` link pointed to `team.html` on all 14 pages.

**Tested:** `testing_agent` iteration_11 → frontend 100%, zero console errors, 15/15 cards reveal on desktop + mobile, no horizontal overflow, menu navigation verified from index/about/east-west, plus About page regressions (no progress bar, discover static, LEED scrub 100%→0%, split-image drift) all pass. One cosmetic nit reported (ragged divider on odd last row) fixed afterwards with `.tm-card:last-child:nth-child(odd){grid-column:1/-1}` and screenshot-verified.
- Team layout v2 (user request, BLG-style reference screenshot): page background changed to warm grey `#efeeec`; cards restructured into a single uniform grid — square graphite tile (aspect-ratio 1/1, radial charcoal gradient + inset hairline) with a large serif monogram, then serif name, uppercase letterspaced role and mail beneath, centered. Fixed column counts: 4 (desktop) / 3 (<=1100px) / 2 (<=760px). Department heading moved from a sticky side column to a full-width `01 MANAGEMENT` rule above each grid. Reveal stagger now row-based (`index % 4 * 80ms`).
- Intro moved into `.tm-hero`: full-bleed AI-generated abstract oil-painting backdrop (`media/images/team/team_art.webp`, charcoal/ivory/bronze impasto) with a dark gradient scrim and white type — emphasises the artistic/corporate positioning. Generator script `/app/scripts/build_team.py` now also patches the header (non-transparent) + REGISTER INTEREST anchor, so regeneration is safe.
- Team v3: real team data pulled from https://nova.istanbul/ekip.html (Osman Kara — Chairman; Ömer Kara, Prof. Dr. Yalçın Şahin, Gürcan Ayaz — Board Members; Merve Afşin — Architect; Bartu Kara — Interior Architect; Kaan Kara — Civil Engineer; Yunus Çay — Head of Accounting; Oğuz Çavuşoğlu — Legal Counsel) grouped as Management / Architecture & Design / Construction & Engineering / Finance & Legal. The source site publishes no e-mail addresses, so the `.tm-mail` element was removed rather than inventing addresses (`team-mail-*` testids no longer exist). Tiles halved (`width: min(58%, 132px)`, 108px on mobile) and recoloured to a soft sand gradient (#e9e4d9→#d5cdbc) with a bronze serif monogram instead of the dark graphite tile.
- Team v4: mail line re-added under each card as `firstname@nova.istanbul` (ASCII-normalised first names — ASSUMED pattern, the source site publishes no addresses; user must confirm). Mobile (<=760px) type scale reduced: hero title 30px, lead 13.5px, eyebrow 9.5px, name 16px, role 9.5px, mail 10.5px, tile 96px.

### Team v5 — upstream pull + mail/animation removal (Jun 2026)
- Fast-forwarded `upstream/main` `1c0526c..0bf07cf "team updated"` (only `frontend/team.html` changed, 49+/19-): title/eyebrow now "Organization / Professional Team" with a longer lead, 5 new people added (Edip Saatcıoğlu, Ahmet Göktuğ Paksoy, Çamoğlu Mimarlık, Mesut Yavuz, Yasin Kırkıl) → 14 cards, and the Construction & Engineering group was moved above Architecture & Design.
- `team.html` is now hand-maintained by the user on GitHub, so the generator `/app/scripts/build_team.py` was DELETED (regenerating it would have wiped the user's edits). Edit `team.html` directly from now on.
- Per user request: all 14 `.tm-mail` links removed and the card reveal animation removed (`js/team.js` deleted + script tag removed, `.tm-card` opacity/transform/transition dropped from `css/team.css`).
- Also fixed while there: monograms that no longer matched the pasted names (Mesut Yavuz → MY, Yasin Kırkıl → YK) and duplicated `data-testid="team-card-*-1"` values renumbered per group.
- **Flag for user:** upstream group indices now read 01 Management, 03 Construction & Engineering, 02 Architecture & Design, 04 Finance & Legal — the numbers no longer follow the visual order (left untouched, awaiting the user's call).

## Team page — card grid replaced with org-chart network (Aug 2026)
User disliked the square-card/monogram layout; requested a "chic linear structure with names linked to each other". Routed through `design_agent` (choices: org-chart/network with connecting lines, no monogram tiles — pure typographic nodes, same 4 department groups/order kept).

**Implemented (`team.html` / `css/team.css`):**
- Removed `.tm-grid`/`.tm-card`/`.tm-tile`/`.tm-monogram`/`.tm-name`/`.tm-role` entirely. Each department now renders `.tm-network` (CSS grid, `style="--count:N"`) with a `.tm-network-trunk` (vertical line dropping from the group header's hairline) joining a `.tm-network-spine` (horizontal line) that branches into a `.tm-node::before` vertical drop + `.tm-node-dot` (bronze dot) + serif name + uppercase role for each person — a true org-chart/network tree, zero cards/boxes/avatars.
- Fixed a long-standing flagged inconsistency while rewriting: department indices are now sequential 01→04 matching visual order (was 01/03/02/04 from an earlier upstream pull).
- Mobile (≤900px, widened from 760px per testing feedback to avoid cramped 4-col text wrapping): collapses to a single continuous vertical bronze/hairline timeline with short horizontal stubs + dots, name/role left-aligned.
- Hover: dot scales 1.6×, drop-line + name tint to bronze `#9a8253`.

**Tested:** `testing_agent` iteration_13 → 95%, all 4 groups + mobile timeline verified across 1920/1024/768/761/390px, testids intact, zero console errors, shared chrome unaffected. One MEDIUM bug found (`.tm-network-spine` endpoint calc wasn't gap-aware, leaving a 9-11px visual gap before the last node) — fixed post-report with a proper `calc((100% - (count-1)*gap)/count/2)` formula; also bumped drop-line alpha .16→.22 for legibility per the report's polish note. Not re-verified by testing_agent after this last CSS-only fix (self-verified via computed geometry formula + screenshot).

**Follow-up refinements (same session):**
- User: "Osman Kara en üstte olmalı" → Management's chair (Osman Kara) promoted to its own lead row above the other 3 board members, connected via a vertical trunk → horizontal spine → 3 drops, forming a proper 2-tier hierarchy. `testing_agent` iteration_14 → 100% pass (desktop/tablet/mobile geometry, stray-line bug fixed via `.tm-node--chair::before{display:none}` desktop / `display:block` mobile, zero overflow, zero console errors). One cosmetic-only note left unaddressed per report (short dangling spine stub on the left for the 3 single-row departments, flagged as "no action strictly required").
- User: "Osman Kara ... CENTER da olmalı" (must be centered above the 3, not left-aligned) → switched `.tm-network-root` to a centering flex column (`align-items:center`) and both trunk spans to `left:50%`, removed the left-align override on `.tm-node--chair` so it inherits the default centered `.tm-node` style; mobile timeline unaffected (still left-aligned single column, governed by the existing `@media (max-width:900px)` override which was untouched). Self-verified via desktop screenshot (chair now sits centered exactly above the middle of the 3-member row); not re-run through testing_agent (small CSS alignment change on top of an already-100%-passed structure).
- User: 3 more polish requests in one message — (1) chair's trunk should be "glued" to the group-header's divider line with zero gap; (2) Yalçın Şahin's (middle board member, x-aligned with chair) drop-line looked abnormally long because the chair's down-trunk and his own node drop-line are perfectly colinear at the shared 50% x-position, visually merging into one long line unlike Ömer Kara/Gürcan Ayaz; (3) shrink the whole chart a bit. Fixed: removed `.tm-group-head`'s `margin-bottom` (was clamp 28-44px) to 0 so the trunk is now the only visible spacing, glued flush to the header rule; added a small bronze junction dot (`.tm-network-tier .tm-network-spine::after`) at the spine's 50% midpoint to visually cap/break the chair-trunk-to-middle-node line so it reads the same short length as the other two members; scaled down trunk/spine/drop heights (26→22px), gaps (28→22px desktop, 20→18/16px tablet/mobile), name/role font-sizes, dot sizes, and inter-group spacing (`.tm-group + .tm-group` 56-96px → 44-76px) throughout `css/team.css`. Self-verified via desktop screenshot; mobile media-query values scaled proportionally but not re-verified live (tool limitation in this session, same structural logic already passed in iteration_14).

## Partners page (`partners.html`) — new, Aug 2026
Reference layout: https://www.bilgiliholding.com/partnerler (heading style with bottom-border rule, plain logo grid, dark image-overlay cards with name captions). Real data pulled via crawl from https://nova.istanbul/partnerler.html. User choices: only the 2 categories that exist in Nova's real source (Architects and Designers = 7 entries as dark-overlay image cards; Financial Institutions = 12 logos as a plain grid) — the extra Bilgili categories (Marka Partnerleri, İş Geliştirme Partnerleri) were skipped since Nova has no data for them. English copy. Title/lead copied verbatim from nova.istanbul ("Partners" / "Innovative structures at the intersection of art and technology."). All 19 images downloaded locally to `media/images/partners/*.webp` (ASCII-safe names), resized (financial logos → max-height 200px, architect photos → max-side 700px; originals were up to 3840×2160 and were the cause of a screenshot-tool-only decode flakiness — confirmed by testing_agent as NOT a real bug, real browser `naturalWidth`/`complete` checks all passed).

**Built:**
- `/app/frontend/partners.html` — cloned shell from `team.html` (utility bar/header/side-menu/footer/Get-In-Touch strip byte-identical for site-wide consistency).
- `/app/frontend/css/partners.css` — `.pt-heading` (Bilgili-style bottom-border rule), `.pt-arch-grid`/`.pt-arch-card` (dark square tiles, image at 50% opacity + bottom gradient scrim for caption legibility, white name label), `.pt-logo-grid`/`.pt-logo-cell` (plain contain-fit logo grid), responsive at 1100px/760px.
- Linked the pre-existing dead `href="#"` **PARTNERS** side-menu item to `partners.html` on **all 15 pages** (was a no-op link before, per user's explicit request to reuse the existing nav entry instead of adding a new one).
- `serve.json` — added `/partners` → `/partners.html` rewrite.

**Known source-data quirk (not an implementation bug):** two financial logos' alt-text/testid don't match their visual branding — this mirrors nova.istanbul's own live site (`tp-logo.png` labeled "Türkiye Petrolleri" actually shows "Tera Portföy"; `PB.jpg` labeled "Private Banking" actually shows "Postbank"). Not visible to end users since the Financial Institutions grid shows no caption text (matches Bilgili reference). Flagged, not silently "fixed", since the ask was to mirror the source exactly.

**Tested:** `testing_agent` iteration_12 → 100% of tested flows passed: page shell/intro/both sections render, all 19 images decode with valid `naturalWidth`, zero horizontal overflow at 1920/1024/390, side-menu open/close, PARTNERS link verified from all 15 other pages, REGISTER INTEREST → `index.html#register`, zero console errors. Two cosmetic nits from the report were fixed post-test: added a bottom gradient scrim behind architect card captions (contrast fix) and changed the 7 architect cards from dead `<a href="#">` to plain `<div>` (were non-functional links).

### Partners spacing/sizing polish (Aug 2026)
User: architect-card row gap too tight, finance logos look visually inconsistent in size, shrink each finance logo 20%, increase gap between finance logos, mobile architect/designer images too large (shrink 30%).
- `.pt-arch-grid` gap 4px → 20px desktop, mobile breakpoint switched from 2-col/3px gap to **3-col/10px gap** (≈30% smaller card per the 2→3 column math, matches the ask without leaving dead grid space).
- `.pt-logo-cell img`: was `max-height:50px` (images smaller than 50px, e.g. `turkiye-petrolleri.webp` native 105×36, were never upscaled → looked visibly smaller than the rest). Changed to a **fixed `height:40px`** (20% smaller than the old 50px cap) so every logo renders at the identical visual height regardless of source resolution. Mobile: fixed `height:30px` (also -20% from the old 38px cap).
- `.pt-logo-grid` gap `36px 24px` → `56px 44px` desktop, mobile `26px 16px` → `40px 22px`.
- Verified via screenshot at 1920px and 390px: architect cards have visible spacing (3-up on mobile, smaller footprint), all 12 finance logos render at uniform height, zero horizontal overflow both sizes.

### Yapı Kredi logo size fix (Aug 2026)
User reported Yapı Kredi still looked smaller than the other 11 finance logos on both desktop and mobile after the previous resize. Root cause: the source file `yapi-kredi.webp` had a 355×200 canvas but the actual logo mark only occupied a 355×66 band in the middle (67px of transparent padding above and below) — scaling by the fixed `height:40px` (based on the full canvas) rendered the visible mark at only ~13px tall. Fixed by trimming the source image to its real content bounding box (`PIL.Image.getbbox()` + 6px margin, now 355×78) so it scales identically to the other logos. No CSS change needed. Verified via screenshot: Yapı Kredi now matches the visual weight of the surrounding logos at 1920px and 390px.

## GitHub pull merged (Aug 2026) — user's direct edits, commit `6951353 "team fixed"`
Fast-forwarded cleanly (local `main` was an ancestor of `upstream/main`, no conflicts). Changes:
- `team.html`: hero title "Professional Team" → "LEADERSHIP & TEAM", eyebrow ("Organization") removed, lead paragraph shortened.
- `partners.html`: breadcrumb ("Home / Partners") removed from the intro.
- `partners.css`: page background `#ffffff` → `#EFEEEC` (warm grey, matches team.css), `.pt-main` bottom padding 100px→80px, added `.pt-title{padding-top:40px}` and a `@media(max-width:767px){body{padding-bottom:0}}` rule.
- `team.css`: same mobile `body{padding-bottom:0}` rule added at 767px.
Verified via screenshot at 1920px and 390px: both pages render correctly, org-chart/frame geometry from the previous session unaffected, zero horizontal overflow.

### Team org-chart v3 — geometry cleanup (Jun 2026)
User: "Çok saçma çizgi bağlantıları... Yalçın Şahin'in üzerindeki nokta ne alaka? Düzgün, estetik, mantıklı, tutarlı bir chart — saçma yatay çizgiler ve bağlantılar yapma."
- Removed ALL `.tm-network-trunk` spans from `team.html` (left-edge dangling trunks on non-rooted groups, up/down trunks around the chairman) and the gold junction dot (`.tm-network-spine::after`) that floated above Yalçın Şahin.
- New geometry in `css/team.css`: spine now spans EXACTLY from first to last node centre (`left/right: calc(var(--tm-col)/2)` where `--tm-col = (100% - (N-1)*gap)/N`), uniform 26px vertical drops (`--tm-drop`) from spine to each node dot. Chairman: centred node with a single 26px drop (`.tm-network-root::after`) into the tier spine — classic symmetric org chart, no stray marks. Removed the connector between the group-header divider and the chart (chart is self-contained, `margin-top: 34px`).
- Mobile (<=900px): unchanged vertical timeline; added `.tm-network-root::after { content: none }` guard (display:contents would otherwise leak the pseudo-element).
- Verified via JS geometry probe: spine endpoints == first/last node centres to <0.02px in all 4 groups; drops uniform 26px; overflow 0 desktop & 390px mobile. Agent-tested (screenshots + DOM probe), not yet user-confirmed.

### Team org-chart v4 — chairman connector + member frames + true-responsive tree (Aug 2026)
User marked an annotated screenshot: (1) red circle — Osman Kara's dot floated with no line touching it from above (unlike the board members, whose dots touch the spine above them); (2) purple X — the chairman's trunk was perfectly colinear with Yalçın Şahin's own drop line through the spine, reading as one continuous line "passing through" the horizontal spine instead of a clean branch; (3) asked for every member to sit in a simple linear (hairline) frame; (4) asked mobile to keep the exact same hierarchy shape as desktop, just scaled down — not switch to a vertical timeline list.
- **Chairman connector**: `.tm-network-root::after` (old trunk down into the tier) removed entirely. Added `.tm-network-root::before`, a vertical line spanning the existing `--tm-header-gap` (34px desktop) from the group-header divider straight down to the chairman's dot — dot now visibly touches a line above it, same visual language as every other node.
- **Removed the crossing illusion**: the 3 board members (Ömer/Yalçın/Gürcan) now form their own fully self-contained spine block below the chairman (own `margin-bottom: 44px` gap, no line at all connecting down from the chairman) — identical pattern to the other 3 non-rooted department groups, so there is no more colinear trunk+drop reading as one pass-through line.
- **Linear frames**: every one of the 14 `.tm-node`s now wraps name+role in a new `.tm-node-frame` div — 1px hairline border (`var(--tm-line)`), padding, sharp corners, border tints gold on hover. Dot sits above the frame, touching the connecting line; `team.html` updated at all 14 places.
- **True-responsive tree**: replaced the old `@media (max-width:900px)` block-layout/vertical-timeline override with pure geometry scaling — `.tm-network` stays `display:grid` at every width; `--tm-gap`/`--tm-drop`/`--tm-header-gap`/font-sizes/frame padding/dot size all shrink through 1100 → 900 → 680 → 460px breakpoints. Same tree/spine/frame shape at 1920, 1024, 768, 390 and 320px, just proportionally smaller (names wrap to 2 lines where needed on the 4-column Finance & Legal group at narrow widths).
- **Verified (self-tested via screenshot + JS overflow probe, testing_agent not invoked for this CSS/HTML-only change):** zero horizontal overflow at 1920/1024/768/390/320px, zero console errors, chairman dot/frame connects cleanly to the header divider, board-members spine self-contained with no crossing line, all 14 frames render, mobile hierarchy visually identical in shape to desktop just scaled down.
- **Not yet user-confirmed** — awaiting the user's visual review of this specific fix before considering the org-chart topic closed.


---

## LEED / Sustainability page — "Build Beyond Living" (Aug 2026, this session)

**User brief:** an exceptionally premium, immersive, technically sophisticated LEED / sustainability page that must NOT look like a corporate ESG page or a stack of cards — "an interactive architectural film controlled by scrolling". Cinematic, engineering-led, luxury architectural editorial. GSAP + ScrollTrigger + Three.js/WebGL, pinned stage, scroll scrubbing, camera interpolation, exploded-view, masked reveals, spatial typography. No eco clichés (no green gradients, floating leaves, glowing icons).

**User choices (ask_human):**
1. Procedural Three.js architecture (no GLB asset) — chosen over photo-parallax or a user-supplied model.
2. No verified sustainability data available → **zero numeric claims**, qualitative engineering language only.
3. No project-specific certification example; never state "LEED Certified".
4. Wire only the side-menu **LEED** link to the new page (BUILD BEYOND LIVING menu item left as-is).

**Files added**
- `frontend/leed.html` — 9 chapters inside one sticky "film" stage; every animated element carries `data-lx="in0 in1 out0 out1"` (scroll-progress fade window).
- `frontend/css/leed.css` — `.lx-*` design system (ink #07090a / paper #f1eee8 / gold #a08660), sticky stage, chapter grid, leader-line legend, hotspots, site-plan, LEED typographic composition, mobile overrides, and a full `.lx-static` editorial fallback.
- `frontend/js/leed.js` — ES module, `three@0.180.0` via importmap + GSAP 3.15 CDN. Procedural building (13 floors desktop / 9 low-power): structure, envelope/insulation, mullion grid (single InstancedMesh), glass façade + shading fins, mechanical plant, water risers/tanks, landscape podium with cypress planting, 192-instance night window lights, custom additive flow shaders for energy + water paths. Keyframed camera (13 keys), yaw, explode factor, day→night, flow intensities. rAF gated by IntersectionObserver on the stage + `visibilitychange`; renders only when progress moved or a flow is active.
- `frontend/media/images/leed/` — `material-facade.webp`, `material-texture.webp`, `interior-daylight.webp`, `landscape-aerial.webp` (downloaded + re-encoded locally, no CDN images).

**Narrative (scroll progress ranges)** 01 approach 0–0.10 · 02 systems exploded 0.11–0.27 (7 sequential leader-line annotations, one focused line at a time) · 03 decarbonization 0.28–0.39 (night + energy flows) · 04 water 0.41–0.51 (roof/landscape, translucent flows) · 05 material intelligence 0.53–0.63 (macro façade photo + 5 interactive annotations) · 06 quality of life 0.65–0.75 (interior, daylight sweep, dust motes, acoustic rings) · 07 ecological conservation 0.77–0.86 (site-plan linework draws, then cross-fades to landscape aerial) · 08 LEED framework 0.88–0.95 (typographic composition of the v5 impact areas + accuracy disclosure) · 09 reassembly 0.96–1.0 ("Sustainability, built into the architecture.").

**Other changes:** side-menu LEED link → `leed.html` (+ `data-testid="menu-link-leed"`) across all 17 pages; `serve.json` rewrite `/leed → /leed.html`.

**Testing:** `testing_agent` iteration_15 → 92% frontend. Fixed after report: missing `labelsWrap` declaration in the reduced-motion branch (found+fixed by tester), mobile hotspot panels clamped inside 390px, rail now fades via a ScrollTrigger on `.lx-closing`, closing LEED mark eager-loaded + inverted (source PNG is near-black), chapter-07 contrast raised. Self-verified after: mobile hotspot geometry, rail `is-off`, desktop hero/systems, zero horizontal overflow at 1920/1440/1024/768/390.

**Known open item (pre-existing, NOT fixed):** `frontend/package.json` start script uses `npx serve -s .` — the `-s` (SPA) flag overrides `serve.json` rewrites, so ALL clean URLs (`/leed`, `/projects`, `/partners`, `/east-west`…) serve `index.html`. The `.html` URLs used by every link work fine. Removing `-s` would fix clean URLs site-wide — left untouched because it changes global serving behaviour beyond this task's scope.

**Not yet user-confirmed** — awaiting the user's visual review of the film.

### LEED page refinement pass (Aug 2026) — discoverability, pacing, contrast, interaction clarity

User asked to keep the visual direction and refine 7 points. Implemented:

1. **Scroll discoverability** — hero cue rebuilt: hairline mouse-wheel glyph with a travelling bead + animated vertical line + "Scroll to explore". If the visitor has not moved after 2.6 s, `.lx-cue.is-nudge` amplifies it (brighter, gentle vertical bob); the first wheel/scroll/touch event removes it and the cue fades out with scroll.
2. **Reading pace** — `js/leed.js` now warps scroll time: `SEG`/`WARP`/`warp()`/`unwarp()` map the scrollbar to the narrative timeline non-linearly, so reading passages receive 2–3.6x the physical scroll of cinematic transitions. Film grew 1000vh → **1800vh** desktop / 900vh → **1400vh** mobile. All item fade windows were shortened to ~0.005 narrative units and staggers widened, so each statement holds at full opacity for ~300 px of scrolling (measured: 440 px between statement onsets in ch02, ~124 px of that is the fade). Rail navigation uses `unwarp()` so buttons still land on their chapter.
3. **Contrast in ch02** — new keyed `studio` factor grades the WebGL environment from daylight to a graphite studio (`0x1e2226`) as the technical annotations appear (hemisphere light −38 %, sun +28 % for crisper model sculpting, fog and exposure follow). Plus localised `.lx-ch1::before` / `.lx-ch2::before` edge gradients (no opaque boxes). Measured mean luminance behind the heading: 25/255 with `rgb(241,238,232)` type.
4. **Hotspots** — hairline inspection frame + slow double concentric ripple, `cursor: crosshair`, dot/frame scale on hover, "Inspect" micro-label on hover (desktop) / persistent "Tap" label (touch), gold active state that persists after click, and the first point (`leed-hotspot-durability`) auto-demonstrates itself on entering the chapter.
5. **Guidance elsewhere** — rail reveals all chapter names on hover (active keeps emphasis), "Select an impact area" hint beside the LEED impact list with `cursor:pointer` + sliding gold rule, animated tick on every hint, and for touch/tablet a 2 px gold top progress bar (`.lx-mobar`) plus a live chapter indicator (`.lx-mochap`, e.g. "05 · Material").
6. **Rhythm** — cinematic transitions stay fluid (weight 1.6), reading passages hold (2.6–3.6), hero and final statement get long holds.
7. **Desktop / mobile split** — leader lines + right-column legend only ≥901 px; stacked bottom legend ≤900 px; hotspot panels flipped/clamped inside the stage in the 761–1100 px band; portrait viewports get an automatic camera distance multiplier (`1.05/aspect`, capped 1.9).

**Testing:** `testing_agent` iteration_16 (92%) → both action items fixed afterwards (tablet hotspot clipping, reading hold now ~316 px effective). Self-verified after the fix: tablet panels inside 1024 px, reading-hold measurement, chapters 04/06/08/09 resolving at their new ranges, zero horizontal overflow at 1920/1440/1024/768/390, reduced-motion static fallback (localised gradients suppressed there).

**Mobile polish round (Aug 2026, user-reported):** (1) site-plan linework was crossing the ch07 typography on phones — the SVG is now confined to a central band (`inset: 25% 0 31%` with `width/height:auto`, grid lines hidden); (2) two hotspot panels could show at once on touch because of sticky `:hover` — all hotspot hover states moved inside `@media (hover:hover) and (pointer:fine)`, and on desktop hovering a point now hides the previously opened one; (3) the "Tap" micro-label sat inside the ripple ring — moved to `top:32px`/7px and mobile hotspot `--hy` values re-spaced (37/48/59/68/77 %) so an open panel never meets the heading or the bottom hint (hotspot coordinates moved from inline `style` to CSS so responsive overrides can win); (4) the mobile progress bar moved from above the navbar to the bottom edge of the viewport, along the scroll axis.

**LEED micro-tweaks (user, Aug 2026):** header is now fully transparent on the LEED page (desktop + mobile, `background: transparent; backdrop-filter: none`, also overriding `.site-header.transparent`); on ≤760px the hero scroll cue moved to the top of the hero (`.lx-ch1` rows `auto 1fr` + `.lx-cue { order: -1 }`); the vertical hairlines beside the Material Intelligence annotations were removed (`.lx-hot-body` border-left/right = 0, including the flipped tablet/mobile variants).

---

## Construction & Engineering page — `construction.html` (Aug 2026) — SHIPPED, agent-tested (not yet user-confirmed)

**Goal:** "The quality of a Nova residence is determined long before the finishes are installed." Premium, technically accurate engineering page — engineering information first, animation second. No fabricated numbers, strength classes, test results, seismic-safety or certification claims; no statement that all Nova buildings share one structural/foundation system.

**User choices (ask_human):** high-quality real reinforced-concrete stock photography (no hard-hat cliché), optimised locally; side-menu **CONSTRUCTION** → `construction.html`; **DESIGN** left untouched (`href="#"`).

**Files**
- `frontend/construction.html` — hero + 13 sections + final (generated once via `scripts/build_construction.py`; later edits made directly in the HTML, so regenerate with care).
- `frontend/css/construction.css` — `.cx-*` system: paper #f3f1ec / ink #0d0f10 / accent #9c8259, alternating light editorial + dark technical sections, vh-aware type inside pinned stages, `.cx-static` reduced-motion fallback.
- `frontend/js/construction.js` — GSAP 3.15 + ScrollTrigger: hero envelope-removal scrub, 5 pinned step sequences (`gsap.matchMedia('(min-width:1201px)')`), scroll-drawn SVG linework, annotation pins, construction-log index, stage crossfade.
- `frontend/media/images/construction/` — `frame-hero.webp`, `frame-detail.webp`, `rebar-macro.webp`, `rebar-grid.webp`, `formwork.webp`, `foundation.webp`.

**Narrative:** 01 hero (completed architecture → reinforced-concrete frame) · 02 structure before surface · 03 designed for Istanbul (seismic) + parameter list · 04 ground & foundation · 05 concrete as a system · 06 reinforcement detailing (annotated photo + 6 pins) · 07 quality control log (5 stages) · 08 waterproofing continuity · 09 envelope explode · 10 acoustics · 11 building services · 12 structure→residence crossfade · 13 engineering framework (TBDY 2018, Türkiye Deprem Tehlike Haritaları, TS 500, TS EN 206 + TS 13515, reinforcing-steel standard, Yapı Malzemeleri Yönetmeliği, Binalarda Su Yalıtımı / Gürültüye Karşı Korunma / Enerji Performansı / Yangından Korunma yönetmelikleri, Planlı Alanlar İmar Yönetmeliği) + project-specific disclaimer · final statement.

**Fixes after `testing_agent` iteration_17 (all verified in iteration_18 — 100 % of 10 checks, zero console errors):**
1. Header was forced transparent page-wide → invisible logo/CTA over light sections. Now transparent only over the hero (`.cx-hero` added to the `heroEl` selector in `js/script.js`).
2. Pinned copy overflowed the stage → vh-aware type/padding scaling plus **static un-pinned chapters at ≤1200px** (all steps and descriptions visible, drawing above copy).
3. Section 12 lead was near-black on dark imagery → explicit light colour + stronger dual-axis scrim.
4. Section 06 pins highlighted nothing → annotation SVG now has `<g data-pin="1..6">`, `light()` helper, first pin open **and** lit on load.
5. Reduced motion hid all scroll-drawn strokes → inline `strokeDashoffset = 0` in the reduce branch.
6. Section 09 `--dx` was dead → `.cx-part[data-dx].is-lit { transform: translateX(var(--dx)) }`.
7. Log-index off-by-one → entry ScrollTriggers moved to `top 30% / bottom 30%`; hero state label retimed (0.3 / 0.62).

**Open backlog (unchanged priorities):** P0 Team org-chart user approval · P0 About CTA target decision · P1 Mercan slideshow pacing, East-West hero video quality, replace DarGlobal CDN images in index hero, populate cloned project pages · P2 East-West floor-plan m² values, PDF checks, sold-out indicators.

---

## Construction & Engineering — full rebuild as technical documentation (Jun 2026) — SHIPPED, agent-tested + testing_agent verified

**User brief:** the previous version felt too editorial and reused the LEED page grammar. Rebuild it as *structural engineering + architectural detailing + construction laboratory + technical documentation*, with its own typographic and motion identity. Hard rules: Montserrat only (no Cormorant in page content); no East West project imagery anywhere on the page; every section gets its own interaction model (no repeated hero→heading→paragraph→pinned visual pattern); no fabricated data (concrete classes, bar diameters, drift ratios, soil classes, U-values, dB, test/lab results, safety or certification claims); no "earthquake-proof"/"soundproof" wording; regulation names stay in Turkish.

**Structure (12 chapters + hero + final), each with a different model**
1. Hero — dense deformed-steel photography + **three.js ribbed rebar bars** rotating about their own axes on scrub (0°→~250°), moving key light, readout Material → Geometry → Structural function, cue "Scroll to inspect the structure".
2. Structural system — one structural model, six isolatable groups (foundation / columns / RC walls / beams / slabs / core); labels are also navigation into the pinned range; non-selected elements dim to wireframe.
3. Seismic design — analysis states: undeformed → applied lateral action → amplified deformation shape → storey-drift markers → base reactions, with "Amplified for visualisation — not to scale"; plus an 8-row design-parameter index (no cards).
4. Ground / foundation — **not pinned**: a physical vertical cutaway (street level → basements → retaining → foundation → strata → investigation depth) with a sticky depth readout and PROJECT SPECIFIC tags.
5. Concrete performance — pinned **horizontal process timeline** (7 steps) with an as-cast concrete band; TS EN 206 note, no strength class.
6. Reinforcement detailing — **three.js cage assembly**: single bar rotating → four longitudinal bars enter → stirrups assemble → cage → transparent concrete volume → element, synced with 6 detailing principles.
7. Execution control — pinned **horizontal inspection strip** with an element-state chain Drawing → Reinforcement → Formwork → Concrete → Enclosure → Completion.
8. Waterproofing — one continuous trace around a section; a discontinuity appears in the warning state mid-sequence and then resolves.
9. Building envelope — macro 1:5-style exploded detail with dimension lines (split layout, not full screen).
10. Acoustics — four distinct waveform behaviours (airborne / impact / structure-borne / service).
11. MEP coordination — six switchable monochrome layers with one accent, plus a real service-riser photograph.
12. Technical framework — **drawing register / specification index** with a title block (TBDY 2018, Türkiye Deprem Tehlike Haritası, TS 500, TS EN 206 + national complement, Su Yalıtımı, Gürültü, Enerji Performansı, Yangın, Planlı Alanlar İmar Yönetmeliği) + verification note.
13. Final — technical layers align, then dissolve into a completed Nova building (Mercan Bosphorus photograph). "Calculated. Coordinated. Constructed."

**Files:** `frontend/construction.html` (generated by `scripts/build_cx2.py`), `frontend/css/construction.css` (full rewrite: Montserrat system, drawing conventions `.ln/.hid/.dim/.hot`, engineering grids and measurement ticks), `frontend/js/construction.js` (ES module: three.js `rebar()` / `stirrup()` builders, hero scrub, `stateDriver()`, `horizontal()` via `gsap.matchMedia`, waterproofing trace, MEP tabs, final dissolve). New construction imagery: `rebar-cage`, `rebar-field`, `concrete-ascast`, `structure-interior`, `services-riser`, `services-soffit` (+ existing frame/rebar/formwork/foundation set). **No East West asset is referenced by the page content.**

**Mobile / tablet (≤1200px):** pinned sequences become static vertical chapters, horizontal rails are not translated, 3D cage still renders at 390px, drawing annotations scaled up (13px tablet / 15px phone in-viewBox).

**Verification:** `testing_agent` iteration_19 — 100 % of 13 feature areas functional, zero console errors, zero horizontal overflow at 1920/1440/1280/1024/768/390, Turkish glyphs correct, no forbidden claims or fabricated values. Follow-up fixes after the report: light-section gold/footnote contrast raised, "Undeformed analytical model" caption now dims once deformation is active, thinner stirrup tube + raised camera so the cage reads as closed hoops, tablet annotation size, cached horizontal span + matchMedia re-init on resize.

**Note:** the shared side menu still contains the global East West navigation entry and its thumbnail (brand-wide navigation, not page imagery) — left untouched by design.
