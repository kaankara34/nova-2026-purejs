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
  - CSS `.project-card .name .project-name-logo`: width 70%/240px desktop, 78%/200px iPad, 62%/240px mobile, drop-shadow.
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
