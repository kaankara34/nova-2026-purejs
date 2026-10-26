# NOVA — UI, hero video and performance verification

Date: 2026-10-26. Scope: existing static EN/TR site; no redesign, deployment, authentication or backend changes.

## Findings and targeted changes

| Area | Code-level finding | Implemented change |
|---|---|---|
| Mobile menu | Header and offcanvas both rendered language controls; neither followed the open drawer state. | `nova-menu-open` follows the existing menu controller. At its existing <=1100px mobile/tablet breakpoint, both controls have `display:none`; closing restores them. Desktop stays unchanged. Duplicate menu opens cannot increment the scroll lock again. |
| Hero video | Homepage swapped an already discovered source and called `load()`. Project scripts each attempted `play()` on initial data/canplay and duplicated pointer/touch fallback listeners; no common viewport/tab/BFcache recovery owner. | One `hero-video.js` manager for the homepage and all five project hero templates in both languages. Shared IntersectionObserver and visibility/pageshow/pagehide/focus/blur lifecycle, deliberate-pause state, in-flight request tokens, caught play rejections, at most3 attempts per activation and a bounded1800ms progress probe. No source mutation, load or seek. Browser selects homepage renditions through source media conditions. |
| Border | SVG dash offset written on every rAF; offscreen polling continued. Touch/synthetic hover could retain the pause flag, and header scroll handling mixed reads/writes on every scroll event. | Four compositor-friendly transform edges, native Web Animations, same clockwise path,2px line,#9A8058 and5s cycle. ResizeObserver measures only on resizing; offscreen/hidden pause and BFcache/focus resume retain progress. Real mouse hover retained, stale hover cleared on scrolling/return. Header work coalesced into one rAF with geometry read before writes. |
| Logo/icons | Header used2000x2000 PNGs, no explicit fetch priority and no logo preload; three offscreen menu image preloads competed early. Icons already were inline SVG, not an icon font. | Separate768x768 header WebPs preserving the square canvas/brand proportions; originals unchanged. Matching single image preload, eager loading, high fetch priority, explicit dimensions, synchronous small-image decode. Competing menu thumbnail preloads removed. SVG icons and their design left intact. |
| Theme | Switch colors/material were fixed white/dark-glass even on the site's light headers. | Existing `.page-design`, `.page-contact`, `.page-bbl` header themes supply scoped neumorphic skin variables. Explicit `data-header-theme="light|dark"` is also supported. Dark defaults, flag artwork/focus, circle dimensions, native mappings and gesture code retained. |

Two inherited duplicate `aria-current` attributes (`en/build-beyond-living.html` and `tr/muhendislik.html`) were also deduplicated without changing their values or language links.

## Changed application files

- `frontend/js/script.js`: menu state, coalesced header scroll and shared video import.
- `frontend/js/hero-video.js`: new shared hero lifecycle owner.
- `frontend/js/east-west-feature.js`: perimeter/slideshow lifecycle.
- `frontend/js/{east-west,bahar-residence,marti-residence,mercan-bosphorus,the-apartments-ana}.js`: removed only the old, competing hero playback bootstrap.
- `frontend/css/styles.css`: perimeter transforms, mobile menu visibility and theme-aware switch skin.
- `frontend/media/images/nova-logo-header.webp`, `nova-logo-dark-header.webp`: optimized header-only variants; original PNGs retained.
- `frontend/en/*.html`, `frontend/tr/*.html` (33+33): surgical header metadata/assets, hero markers and homepage responsive sources/bootstrap cleanup. Other branch-authored content not regenerated.
- `scripts/runtime_markup.py`: idempotent scoped update helper; `scripts/build_i18n.py` hooks it for future authorized builds.
- `scripts/language_toggle_markup.py`: duplicate-ARIA cleanup.
- Regression tests/fixtures and memory documentation updated separately.

## Measured asset and cold-render results

| Header asset | Previous PNG | New WebP |
|---|---:|---:|
| White logo |205,905 bytes |36,456 bytes (~82% smaller) |
| Dark logo |153,486 bytes |35,026 bytes (~77% smaller) |

One cache-disabled Chromium run of `/en/contact.html`,1920x800:
- Logo request began175.8ms after navigation and finished370.0ms; initiator was the preload link.
- First contentful paint572.0ms.
- Logo and both inline contact SVG icons observed visible at583.7ms, with the logo complete and768px intrinsic width.
- These are sample timings, NOT production guarantees or a measured before/after speed comparison.
- Evidence: `/root/.emergent/automation_output/20261026_174309_3266558c4ee8/console_20261026_174309.log`.

## Passing verification

-242 automated regression checks:66page content/link coverage, header asset checks, both static serving roots, source paths, ARIA and language behavior constraints. Final XML: `test_reports/pytest/iter67_final.xml`.
-10 isolated lifecycle cases: duplicate initialization/listeners,3-attempt budget, single pending play, gesture-gated NotAllowed rejection, late promise tokens, background/restore, deliberate pause, reduced motion, no load/seek/source changes, and clock OR genuinely advanced frame progress. See `tests/hero_video_lifecycle_isolated.mjs` and `test_reports/iter67_hero_lifecycle.txt`.
- Browser checks: mobile and desktop menu behavior, dark and all three light header themes, explicit theme override, preserved layout/flag focus, keyboard/click/mouse drag, and border progress/visibility resume.
- Follow-up CDP touch at390x844: touch opens menu and hides BOTH switches with no bounding/hit boxes; close restores identical rail position;14px swipe follows the finger without navigating while held, commits to the exact existing TR URL on release;8px swipe snaps back. No horizontal overflow. This is touchscreen emulation, not a physical Android/iPhone test.
- Touch evidence: `/root/.emergent/automation_output/20261026_174129_d7b6ed73ef50/console_20261026_174129.log`.
- Chromium homepage WebM fallback visibly advanced after scrolling out and returning, without an application-driven reset.

## Media-engine limitations — NOT reported as passing device tests

- Physical iPhone/iPad Safari OS app switching and physical Android Chrome were unavailable. No claim of physical-device sign-off is made.
- The supplied Chromium test build reports an empty H.264 capability and leaves MP4-only project videos at readyState0. Its homepage WebM path works. This limits MP4 playback validation in that runner, not proof that real Chrome/Safari lacks H.264.
- An isolated Linux WebKit/GStreamer environment was installed for additional verification (testing only; no app dependency added). It accepted H.264 but some MP4 clocks jumped back after ~2–3s despite correct9–75s metadata/full buffers. Instrumentation observed no play/pause/seek/load/src call at a representative jump. The issue also occurred outside manager intervention. This is not evidence that physical Apple Safari behaves the same way.
- The manager's original strict frame-callback probe was made conservative: actual clock progress OR an advanced presented frame proves healthy playback, since WebKit can throttle frame callbacks. A missing callback alone no longer interrupts healthy playback.
- No native loop removal, forced currentTime reset, mass transcoding or source workaround was added merely to satisfy a limited headless media engine.
- Real Safari GPU/FPS smoothness and OS-suspension recovery remain device acceptance checks, not measured successes.

## Device acceptance checklist / next action

1. On real iOS Safari and Android Chrome, open homepage and each video hero project in EN/TR; wait for genuine playback.
2. Scroll below hero, switch apps for20–60s, return and scroll to hero. Confirm advancing frames and continuation rather than an application reset.
3. Repeat with browser Back/Forward and tab visibility changes. Confirm a deliberate pause is not overridden.
4. Check border progress during scrolling/background return, menu switch hiding, and both light/dark switch gestures.

Implementation has no currently confirmed failing application test. Critical real-device video sign-off remains pending. Suggested later hardening: preserve the visual/interaction baseline in automated regression; do not perform unrelated CSS refactoring as part of this task.