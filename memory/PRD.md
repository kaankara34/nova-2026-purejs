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

