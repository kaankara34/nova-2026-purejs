# NOVA Konut — Product Requirements & State

Last updated: 2026-10-27

## Current task — time-limited 29 October homepage modal

### Requirements and implementation — 2026-10-28
- User supplied the Republic Day visual and requested a premium, responsive opening modal on both
  Turkish and English homepages, active from 29 October through 6 November. The top-left **×** and
  **Siteye Giriş/Enter Site** only close the modal.
- Added the supplied source unchanged as
  `frontend/media/images/campaigns/29-ekim-cumhuriyet-bayrami-2026.png`; homepages reference the
  local shared asset rather than an external temporary URL.
- `css/republic-day-modal.css` provides an accessible, premium dark-overlay dialog with responsive
  image sizing, a top-left × close control, one entry action, focus styles and reduced-motion support.
  It only loads on the two homepage files.
- `js/republic-day-modal.js` evaluates the visitor's Europe/Istanbul calendar day and shows only
  between **2026-10-29** and **2026-11-06** (inclusive). It reopens on every homepage refresh in
  that date window, as requested; the ×, entry action or Escape closes only the current display. The
  modal locks background scroll and restores it on close. The platform preview host deliberately
  bypasses the calendar gate for immediate review; production remains date-gated. `?campaign-preview=1`
  is also available as a manual preview path outside the date window.

### Verification
- Static JavaScript syntax validation passed; CSS and campaign image returned HTTP 200 from the
  external preview.
- Browser verification at 1920px showed the supplied visual, loaded image, visible modal,
  initial keyboard focus on “Siteye Giriş”, correct `aria-hidden=false`, and background scroll lock.
  A follow-up verified refresh reopening plus a 390px modal whose image and dialog have identical
  width (no synthetic red side background); the × and entry control close the current display. User
  device/production confirmation remains pending. The normal preview base URL was subsequently
  tested without a query parameter and now opens the modal.
- Follow-up performance optimization: converted the supplied 839,700-byte PNG into a visually
  equivalent 137,488-byte WebP (about 84% smaller). Both homepages preload this WebP at high
  priority and use a PNG fallback only for browsers without WebP support. Preview browser evidence
  confirmed the active image `currentSrc` is the WebP, with its natural 1080px image width intact.
- Follow-up interface simplification: removed the redundant Exit button. A compact, keyboard-accessible
  top-left × now dismisses the modal; the remaining entry action spans the full width.

## Latest task — EDSAA corporate pages, mobile journal cap and native scrollbar

### Requirements and boundaries
- User requested mobile homepage journal3instead of6news items, thin native scrollbar matching
  the site's premium palette (explicitchoice#6b5e43), and minimal bilingual EDSAA company pages.
- Only approved EDSAAH1/intro + original EastWest render and restrained project link. No company
  details beyond supplied facts, invented logo, new forms/sales sections or extra SEO copy.
- Reuse current chrome/menu/cookie/language/theme; real NOVA submenu anchor per language.
  Existing.htmlcanonicalstandard, exact usertitles/descriptions, reciprocals, verified-onlyschema,
  sitemapintegration, preservepreviewnoindex andnoSearchConsole/indexing/rankingclaims.

### Delivered — 2026-10-27
- `frontend/{tr,en}/edsaa.html`, generated statically from the current corporate shell by
  `scripts/build_edsaa.py`; exactapprovedcopy/metadata in `scripts/edsaa_data.py`.
- Existing contactlightheader/footerstyles + isolated `.page-edsaa` styling; maincontent visible
  fromfirstHTML withoutJS/consent. Noforms, only sharedscript.js; enquiryCTAsexistingcontactpage.
- Original1901x1070`media/images/ew/render/ew-render1.webp` unchanged, fullaspect/contain onmobile,
  highpriority/eager and explicitdimensions. NoEDSAAlogo found; typographyonly.
- Bothcanonicallinks usehttps://nova.istanbul/{tr,en}/edsaa.html; correctsame-page languagelinks.
  All68pages haveoneEDSAAentry inUL.submenu[data-id=nova-konut] withsameexistinglinkmarkup.
- JSON-LDAboutPage+EDSAAOrganization; stableTR#organization@id sharedbothlanguages. Parent uses
  onlyknownNova name+homepage because noexistingOrganization@idwasfound. LocalizedOG/Twitter
  rendersnotlogos. Aboutaffiliatesectionabsent: noartificialnewsection orfooteraddition.
- Sitemapbuiltthrough existingmechanism/PAGE_MAPspecialpagehook; nofabricatedlastmod. Only
  productionApacheaddsEDSAAalias301to.html; previewusesadvertisedcanonical.htmlpages. robots.txt
  andpreviewnoindexheader unchanged. serve.jsonsemanticallyunchanged.
- Homepage `news.js` renders3at<=767px/6above, responds tobreakpointchange usingcachedfeed; full
  newsroomlogicunchanged. RootnativeCSSscrollbarthin#6b5e43; noJSscrollwidget ormenulockchange.

### Verification and next steps
-271automatedtests pass (`iteration_70.json`, `pytest/iter70_final.xml`), includingnew11-testEDSAA
  contract and unchangedold66pagecontentapartfromoneNOVAitem. Scopedbuildrerun0changes.
- Actualbrowserchecks confirmedmobile/desktopmenus,languageclickandCDPtouchrelease,news3/6,
  responsive320–1920, originalimage, noforms/overflow, footercontrast andheaderclearance.
- Initialtestfoundwrongmenutagselectorandcopiedcontactform; bothfixedandretested. Latestpages
  contain noform, no#register and noformsinjectionscript. NoAPI ismocked; noexternalintegrationadded.
- ProductionURLs NOTpublished/verifiedlive, SearchConsole NOTused. Owner mustcheckproduction
  HTTP200/robots, submitsitemap/inspectbothURLs andrequestindexingifappropriateafterpublication.
  Noindexing/rankingpromise. Detailedhandoff: `memory/EDSAA_DELIVERY.md`.
- P0:noneconfirmedremaininginthisrequest. P1:userreview+postpublicationSearchConsoleactions.
  P2:monitorEDSAAbrandqueriesafterpublication; oldvideo/mobilephysical-deviceacceptance and
  source-template reconciliation remain separatebacklog. DoNOTfullrebuildstalesourcepages.

## Latest task — recurring mobile perimeter freeze, clearer trace, canonical chrome and favicon

### User request (original)
> mobilde bar takılı kaldı yine düzelt, bir de bar biraz daha kalın olsun belli olmuyor ya da belli edici şık premium hareket veya bir animasyon da koyabilirsin bar ilerlerken Side navbar da language switcherı da kaldır desktopta. Ayrıca üçüncü ekteki iconu tab icon olarak koy. Ayrıca hem türkçe hem ingilizce index.html de bulunan navbar ve footer içeriği nihaidir. Diğer sayfalara da bu içerikleri uygula. (içerik dedim, biçim değil(diğer sayfalarda footer farklı renk olabilir sadece içerik değişecek .)

### Findings and implementation — 2026-10-27
- Reproduced the OLD mobile freeze at390px before editing: blur paused the border around960ms;
  a visible scroll without a focus event left it at exactly that time. `focused=false` was a
  mandatory gate even when the document/section were visible. Mobile browser chrome can blur
  without delivering the expected focus return. Prior short tests missed this case.
- `js/east-west-feature.js` now uses a visible-time clock, infinite native transform animations
  and one slideshow callback per5s cycle, not a finish-event dependency. Blur is not a stop gate;
  document visibility/pagehide/offscreen/reduced-motion still pause. Scroll/focus/pageshow/touch
  reconcile actual animation state, including a browser-paused animation. Resize preserves time.
  Initialization guard prevents duplicate layers/listeners. Real desktop hover pause retained.
- `css/styles.css`: same clockwise bronze path#9A8058, now3px instead of2px; restrained5px travelling
  champagne glint and soft glow follow its leading point. Five compositor-only animations.
- Removed the SIDE-MENU language switch on every page (including desktop). Only the existing
  header switch remains; its URLs/click/drag/swipe JS unchanged. The earlier mobile-open-menu rule
  continues to hide the header switch and restore it on close. Language helper cannot reinsert
  the menu control, and supports HTML attribute reordering by parsers.
- **Canonical content rule:** `frontend/en/index.html` and `frontend/tr/index.html` are final
  navbar/footer CONTENT sources for their respective languages. `scripts/sync_site_chrome.py`
  updates only utility/header/mobile actions/sidebar/footer semantic content across66pages,
  preserving destination wrapper/classes/styles, logo variants, CTA behavior and icon styling.
  It does not copy index colors/layout or rebuild the page body. All footer texts/menu destinations,
  social entries, project labels and utility contacts now match the corresponding index.
- Existing wrong-language local footer filenames on the EN index were mapped to the proper EN
  counterpart without changing approved copy. Home menu label became a working native link
  rather than a dead button. Existing language mapping and per-page enquiry behavior retained.
- User-supplied tab icon preserved byte-for-byte as `media/images/nova-tab-original.png`.
  Faithful transparent ring crop with safety padding produced favicon.ico(16/32/48),32/192PNG
  and180Apple touch variants. No AI generation/recolor/redraw. Source/provenance documented in
  `media/images/nova-tab-source.md`; all66pages have portable local icon declarations.

### Verification and remaining work
- `test_reports/iteration_68.json`: mobile emulated390px long run30s+ / six5s cycles; slides and
  trace advance continuously, blur+visible-scroll and pagehide/pageshow recovery pass. Desktop
  hover/resume tested. Physical iOS/Android device confirmation remains unavailable, not claimed.
- Final suite **256 passed** (`test_reports/pytest/iter68_final.xml`). Legacy tests were aligned
  with the explicitly requested one-header-switch contract and approved chrome regions; body/head
  hashes are from the PRE-change snapshot, not blind new-page snapshots. CSS outside perimeter
  remains protected; language link attributes compare to the original header links.
- Additional checks: footer/header classes/styles/dimensions match pre-change pages; no duplicate
  data-testids; only perimeter JS/shared perimeter CSS changed outside the content updates.
  New favicon resources resolve in both serving layouts. Sync and language helper reruns0changes.
- P0 current request: no remaining confirmed failing test. P1: user physical-phone confirmation
  of the previously recurring freeze. Prior video real-device acceptance remains independently
  pending; this task did not modify video behavior. P2: source-template reconciliation before
  any full i18n rebuild and independent form/legal backlog. No unrelated refactor.

## Latest task — UI, hero-video lifecycle, border and critical-header performance

### User requirements and current status (2026-10-26)
- Preserve the site's existing design/responsiveness/content and TR/EN mapping; fix only affected
  areas. Mobile open menu must hide both switches; shared hero recovery on scroll/tab/BFcache/app
  return must avoid source reload/seek, duplicate attempts and overriding intentional pause.
- Smooth the East West perimeter without changing its visual character/speed; prioritize logo
  and icons; keep dark glass and add a page/header-theme-based light neumorphic variant.
- User explicitly requires a short cause/file/solution/test report and no invented device testing.
- Implemented and tested as documented in `memory/UI_VIDEO_PERFORMANCE_REPORT.md`.

### Implemented architecture
- New `js/hero-video.js` is the sole lifecycle owner for the homepage + five hero project types
  in both languages. Shared IntersectionObserver, visibility/pageshow/pagehide/focus/blur,
  deliberate-pause state, single pending play and token cancellation, max3 attempts/activation,
  gesture fallback for NotAllowed, bounded1800ms progress probe. No load/seek/source mutation.
  Probe accepts actual time progression OR an advanced rendered frame; no restart solely because
  WebKit throttled a frame callback. Native loop remains intact. Reduced motion respected.
- Removed duplicate initial video handlers from five project scripts and homepage inline source
  swap/load bootstrap. Homepage renditions use HTML source media conditions instead.
- `script.js` manages `nova-menu-open`; both language controls disappear at the existing <=1100px
  drawer breakpoint and return on close. Desktop untouched. Header scroll reads precede writes
  and are coalesced to one rAF. Explicit pause/resume custom events available for future controls.
- `east-west-feature.js`: four transform-only native animations, clockwise2px#9A8058 perimeter,
  same5s slideshow clock. ResizeObserver only; hidden/offscreen pause, preserved lifecycle state,
  stale touch/scroll-hover cleared. No permanent per-frame SVG dash-offset writes.
- Light skins use existing page-design/page-contact/page-bbl header classes plus explicit
  data-header-theme override, not scroll position alone. All switch geometry/foci/URLs/gesture
  logic retained. Two inherited duplicate aria-current attributes cleaned up.
- Header-only white/dark768px square WebPs preserve original canvas/brand proportions. White
 205905->36456bytes;dark153486->35026bytes. Original PNGs unchanged. Exactly one matching critical
  preload plus eager/high-priority logo; offscreen thumbnail preloads removed. Icons already
  inline SVG: no icon-font issue or icon restyling introduced.
- `scripts/runtime_markup.py` patches66pages idempotently; hooked into the future builder.
  No full rebuild of stale authoring templates. Existing branch/manual content remains authoritative.

### Verification / limits
-242 regression tests +10 isolated lifecycle cases passed. Follow-up real CDP touch emulation
  verified menu hiding/restoration,14px release-only swipe and8px snapback on the light header.
- One cache-disabled Chromium contact run: logo responseEnd370ms, first contentful paint572ms,
  logo+2inline icons visible583.7ms. Sample only, not a production promise or before/after benchmark.
- Chromium runner lacks H.264; MP4-only project decode cannot be certified there. Linux WebKit
  accepted H.264 but displayed independently observed early-clock loops without app play/pause/
  seek/load calls. Do not label these failed media-engine checks as passing physical Safari tests.
- Physical iOS Safari/Android Chrome OS app-switch recovery and real Safari frame-rate testing
  were unavailable. **P0 verification: real-device video sign-off remains pending.** No confirmed
  failing application regression remains. Reports: iteration_66/67, iter67_final.xml and report above.
- P1: user visual/device acceptance. P2: durable visual regression and source-template reconciliation;
  unrelated historical form/legal backlog remains outside this task. Do not rewrite native looping
  or reset playback just to accommodate a headless test engine.

## Previous refinement — subtle flag-only glass pane and rightmost desktop placement

### User requirements
- Keep the existing switch, opaque glossy knob/material/size/travel, flag focal points and URLs.
- Add only a thin, restrained frosted-glass overlay across the flag background: slight softening,
  low-opacity white highlight and subtle depth. Flags must stay recognizable; weaker than knob.
- Desktop order must be **Bilgi talebi → Telefon/Mesaj → TR/EN**, not language between the other
  controls. Preserve header height, mobile appearance, click/drag/swipe and current functionality.

### Implemented — 2026-10-26
- `.lang-rail::before` covers the flag with0.35px backdrop blur, white gradient alpha0.025–0.13
  and subtle inset shading. Decorative and pointer-events:none;z-index0. Knob atz-index1 retains
  exactly the same opaque material/dimensions and is not softened by the overlay. Forced-colors
  mode disables the pane for clarity. No flag SVG or focal geometry changes.
- `place_header_switch_last()` in the existing markup helper moves the SAME header-language
  block after `.icon-links` on all66pages. DOM and keyboard order match the new desktop order.
  No CSS-only visual reorder, positive tabindex or navigation changes. Existing mobile-hidden
  actions mean the visible mobile switch remains in its previous position; menu control unchanged.
- Only matched language-block bytes moved: removing language blocks still yields exactly the
  same page bytes as the baseline. All JavaScript and the rest of shared CSS are unchanged.
- Updater remains idempotent: second run0pages. Full i18n rebuild was not run.

### Verification / remaining work
- `test_reports/iteration_65.json`:170regression tests passed, including new durable
  `tests/test_lang_switch_overlay_order.py` checks. Desktop DOM/visual order, overlay layering,
  native language links, keyboard order and responsive320/390/768/769/800/900/1024/1440/1920 checked.
- Initial agent CDP run reported an inconsistent8px short-touch cancellation. Main-agent follow-up
  could NOT reproduce it: fast single/held/stepped event traces all correct, then12/12 repeated
  short-touch snapbacks across both languages with0/15/40ms timings passed.14px held touch still
  changed language only on release. No gesture-code changes were made; root cause of the first
  emulation observation remains unconfirmed. Keep this evidence if a real-device issue is reported.
- No failing product flow observed in follow-up; no mocked integration or new external service.
- P0:none confirmed. P1:user visual approval. P2:visual-regression coverage and the independent
  authoring-source reconciliation/form/legal backlog remain; do not broaden this visual-only work.

## Previous refinement — opaque opal-glass knob, larger diameter and flag focal points

### Current user requirements (supersede earlier translucency)
- Preserve current switch structure/exterior dimensions, external TR/EN text and header.
- Fully opaque silver-white frosted/liquid-glass knob: no underlying flag or red tint visible;
  retain elegant reflections, soft shadows and depth. Colored annotations are not UI elements.
- Increase circular knob close to rail height with thin equal gaps and no overflow.
- Keep authentic SVG geometry unchanged. TR: knob left, whole crescent+star centered in the
  exposed right area. EN: knob right, Union Jack central pattern balanced in exposed left area.
  Country-specific scale/focus must be derived deliberately, not random cropping/redrawing.
- Keep click, realtime mouse/touch drag, nearest-endpoint settling and exact URL logic.

### Implementation — 2026-10-26
- Only two application source files changed: final language CSS block in `styles.css` and
  measurement of pointer travel in `language-toggle-gesture.js`. All66HTML pages and
  `language-toggle.js` controller remain byte-identical to the prior version.
- Knob diameter now `track-height -2px`:24px inside48x26 rail;18px inside32x20 narrow-tablet rail.
  Left/top0 inside1px border creates equal1px edge gaps. Travel22px/12px, measured directly
  from rail inner width, knob width and inset so pointer displacement remains1:1.
- Opaque neutral#ececec base and fully opaque neutral grey/white gradient, specular highlights,
  white rim and soft depth. No backdrop-filter or transmitted flag colors.
- Original SVG files unchanged. TR white-art bounds x14999.687..55318 in90000-unit viewBox
  determine image scale: full white artwork fits80% of exposed width; its center is placed
  at36px normally/25px on narrow tablets. Exact original red field#e30a17 fills behind knob.
- UK2:1 image is height-fit, with its central cross aligned to exposed-left center12px/7px;
  exact original blue field#012169 continues behind the opaque knob. No symbol deformation.
- Earlier centered-cover and transparency settings below are historical, not current requirements.

### Verified / next actions
- `test_reports/iteration_64.json`:165tests passed (6scope,61dual-root,98static); eight responsive
  widths, unchanged header/label/rail geometry,1px gaps, SVG hashes and page byte integrity checked.
- Pixel comparison of knob interior between TR/EN differed by<=1RGB unit: no flag tint bleed.
- Main-agent follow-up enabled real CDP touch emulation at390px:14px finger move produced14px
  knob move with no navigation while held; release navigated to EN; short8px touch drag snapped
  back without navigation. This resolves the testing agent's initial hasTouch-context limitation.
- No mocked flow, new integration or unresolved issue found in requested scope.
- P0:none. P1:user final visual approval. P2:durable visual-regression baseline; authoring-source
  reconciliation before any full rebuild and the independent historical form/legal backlog.

## Previous refinement — continuous authentic flag background and clear glossy knob

### User request and boundaries
- Preserve the current switch size, external TR/EN positions, header layout and existing URLs.
- Entire oval rail must be covered edge-to-edge by the selected country's authentic SVG flag,
  including continuously beneath the knob. Use centered `background-size: cover` and clipped
  oval corners; never split/scale/redraw the flag according to knob position.
- Obtain trusted SVG originals through web search; no AI-generated or distorted flag geometry.
- Replace matte grey/metallic knob with glossy translucent glass: highlights, luminous rim,
  subtle inner shadow and visible flag beneath; no solid white/grey plastic appearance.
- Keep click and mouse/touch dragging. On release settle to the nearest endpoint; language
  changes only after completing selection. Red/blue screenshot marks are annotations only.

### Implemented 2026-10-26
- Downloaded unmodified, public-domain SVGs from Wikimedia Commons: Turkish flag1200x800 and
  UK1:2 flag1200x600. Local assets `frontend/media/flags/tr.svg` and `gb.svg`; original URLs,
  source specifications and exact SHA-256 hashes recorded in `media/flags/SOURCES.md`.
- `.lang-rail` now has one stationary full-size SVG background with cover/center/no-repeat,
  border-box origin and overflow:hidden. Removed all half-width `.lang-flag-window` elements
  and hand-drawn inline flag vectors from66pages. Selected SVG changes only on commit/restore,
  not during drag; `data-flag-language` tracks the selected background separately from motion.
- `.lang-knob` has transparent base color, low-alpha specular layers, bright rim and highlight
  pseudo-elements,0.7px backdrop blur and subtle depth. Removed the opaque grey base/heavy blur.
- No rail/knob dimensions, label positions, layout slots or surrounding header CSS changed.
- Gesture velocity override removed: final pointerup position alone chooses nearest endpoint.
  Existing click, pointer capture, cancellation, keyboard, history and reduced-motion remain.
- Markup helper remains idempotent using `data-flag-source="wikimedia"`; full i18n rebuild was
  NOT run because branch HTML is still newer than the authoring templates.

### Verification / next steps
- `test_reports/iteration_63.json`:100% requested frontend checks;165pytest checks passed
  (6scope/link +61dual-serving-mode +98static pages). Both SVG hashes match original downloads.
- Browser checks passed for full stationary backgrounds, glass transparency, nearest-endpoint
  release, fast short8px snapback, Escape, keyboard, reduced motion and history restore.
- Eight widths320/390/768/800/900/1024/1440/1920 checked; original rail/knob/header geometry held.
  No mocked flow, new third-party integration or unresolved defect in requested scope.
- P0: none. P1: user visual approval of the two refined areas. P2: maintain a visual-regression
  baseline for this control; branch/source reconciliation and unrelated form/legal backlog remain.

## Previous iteration — true circular glass toggle with release-to-commit gestures

The user's follow-up replaces the earlier segmented design, not the underlying language URLs.
Reference: `https://customer-assets-agu9un31.emergentagent.net/job_darg-clone-1/artifacts/0ba7fd6f31eb14e5_image.png`.
User explicitly chose **Parmağı bırakınca**: commit language only after finger/pointer release.

### Original follow-up request
> Ekte paylaştığım referans görseli incele. Mevcut TR / EN dil seçicisini, bu referanstaki yerleşim mantığını koruyarak yeniden tasarla.
> İstediğim yapı:
> - Gerçek bir **sliding toggle switch** olsun.
> - Switch yatay, oval ve kompakt yapıda olsun.
> - Referanstaki gibi **bayrak switch’in içinde**, knob’un açıkta bıraktığı alanda görünsün.
> - Referanstaki gibi **yuvarlak switch knob’u** sağa-sola kayan ana parça olsun.
> - Sol tarafta **TR**, sağ tarafta **EN** yazsın.
> - Türkiye için **🇹🇷**, İngilizce için **🇬🇧** bayrağı kullan.
> Ama görünüm şu şekilde olsun:
> - Beyaz flat tasarım istemiyorum.
> - Bunun yerine **glassy / liquid glass / frosted glass** estetiğinde olsun.
> - Switch zemini yarı saydam, premium, hafif blur’lu ve sofistike görünsün.
> - Knob da cam hissi veren, yarı saydam, yumuşak highlight’lı ve hafif derinlikli olsun.
> - Genel görünüm Apple kalitesinde, modern, minimal ve lüks dursun.
> - Yeşil ton kullanma; nötr, şık, premium bir cam etkisi kullan.
> Davranış:
> - Sadece click ile değil, **drag / swipe / slide gesture** ile de değişebilsin.
> - Yani kullanıcı knob’u sağa veya sola sürükleyerek dili değiştirebilsin.
> - Click, drag ve swipe davranışları doğal ve akıcı olsun.
> - Geçiş animasyonu smooth, iOS kalitesinde ve fiziksel hissiyatlı olsun.
> Kısıtlar:
> - Mevcut dil değiştirme mantığını koru.
> - URL yönlendirmeleri, TR/EN sayfa eşleşmeleri ve mevcut işlev bozulmasın.
> - Header yüksekliğini, genel hizalamayı ve diğer header elemanlarını bozma.
> - Mobil uyumlu olsun.
> Önemli:
> - Önceki segmented control veya düz buton mantığını kullanma.
> - Referanstaki gibi gerçek bir **toggle switch yerleşimi** istiyorum.
> - Referanstaki bayrak yerleşimini ve knob kullanım mantığını koru, ama tasarımı **glassy premium versiyon** olarak yeniden yorumla.

### Implemented architecture
- External TR/EN native links flank a real oval rail and one circular glass knob. TR selected:
  knob LEFT, Turkish flag exposed RIGHT. EN selected: knob RIGHT, UK flag exposed LEFT.
- `styles.css`: only final language section replaced; neutral dark translucent rail, highlighted
  frosted knob, reduced-motion/forced-color/focus styles. Standard track48x26, circular knob22x22;
  narrow-tablet track32x20 with16px knob. The existing desktop75.25px, mobile88px and narrow-tablet
 28px layout slots remain, without changing parent header styles.
- `scripts/language_toggle_markup.py`: idempotent v2 markup migration inside existing controls on
  66 pages. Original href/hreflang/lang/aria-current preserved. No changes elsewhere in page HTML.
  Old segmented `.lang-indicator` removed. Builder helper retained; full rebuild still prohibited
  until branch/manual source differences have been reconciled.
- `js/script.js` imports `js/language-toggle.js`; controller imports `language-toggle-gesture.js`.
  Local static modules only, no external library/service/storage. Native label links are the sole
  source of navigation URLs and remain usable with JavaScript disabled or module load failure.
- Real Pointer Events/capture support mouse/touch/pen; live drag position, clamping, deliberate
  flick, release-only commit, short/return drag snapback, vertical/cancel/Escape/blur cancellation,
  synthesized-click suppression, pending-navigation guard and back/forward state reset.
- Center switch supports click, Space/Enter, arrows/Home/End; role=switch, aria-checked, pending
  aria-busy. Release settles for240ms before following exact existing href (0ms with reduced motion).

### Verified results and remaining work
- `test_reports/iteration_62.json`: preview browser tests passed for click roundtrip, mouse drag
  and hold/release, partial cancel, right-click no-op, keyboard, reduced motion, history reset,
  real mobile touch swipe via CDP, offcanvas and responsive320/390/768/800/900/1024/1440/1920.
- Final local regression: **63 passed, 0 skipped** (6 content/link scope checks +57 dual-root
  checks including the two new JS modules). XML: `test_reports/pytest/toggle_and_serving_modes_iter62_final.xml`.
  Temporary helper servers were started for this run then stopped; initial skips were resolved.
- Durable baseline fixture added to `tests/fixtures/lang_toggle_baseline_fixture.json`; tests no
  longer depend on the previous branch archive remaining in /tmp. Updater second run changes0 pages.
- Test-only limitation: very rapid public-preview reload sweeps briefly hit edge429 throttling;
  focused browser reruns passed. This is not an application navigation defect or a mocked flow.
- P0 current task: none outstanding. P1: user's visual/gesture approval on their own device;
  previous local Live Server verification remains user-unconfirmed. P2: authoring source reconciliation,
  existing independent form/legal backlog, optional project-image optimization for mobile speed.

## Current source of truth — 2026-10-26

- User requested the latest `tr-destekli-versiyon` branch of
  `https://github.com/kaankara34/nova-2026-purejs` and approved using that version over local
  differences. Imported commit: `3a238f1c6ef793f1cd75583ca6f9bbd7bb6a88f9`.
- Downloaded and compared the exact public branch archive; synchronized 58 updated/new frontend
  files, including six new image assets. Protected environment/platform files were not replaced.
  Backend and existing source scripts already matched the branch.
- **IMPORTANT: this branch contains manual updates to `frontend/en` and `frontend/tr` that are
  newer than `source-pages` and the translation dictionaries. Do NOT run a full i18n rebuild
  until those authoring sources have been reconciled.** The older build/source instructions
  below are historical and must not overwrite this branch's approved content.

### Previous user request (first glass iteration, Turkish)
> https://github.com/kaankara34/nova-2026-purejs/tree/tr-destekli-versiyon bu branchden projenin son halini çek daha sonra Mevcut header'daki TR / EN dil seçicisini, Apple'ın iOS switch tasarımından ilham alan, ancak NOVA'nın premium ve kurumsal kimliğine özgü bir glassmorphism language toggle olarak yeniden tasarla.
> Koyu, yarı saydam, frosted glass yüzey; hafif backdrop blur, ince beyaz kenarlık ve zarif ışık yansımaları kullan. Yeşil renk kullanma.
> Yatay, kompakt ve oval formda olsun. İçerisinde 🇹🇷 TR ve 🇬🇧 EN seçenekleri yan yana bulunsun.
> Aktif dil, yumuşak geçişli, yarı saydam cam görünümlü bir sliding indicator ile vurgulansın.
> Geçiş animasyonu Apple kalitesinde, akıcı ve minimal olsun.
> Mevcut header yüksekliğini, hizalamaları ve diğer elementleri değiştirme. Mobil uyumlu olsun.
> Mevcut dil değiştirme mantığını, URL yönlendirmelerini ve tüm işlevselliği aynen koru. Yalnızca dil seçicinin tasarımını değiştir.
> Sonuç Apple Liquid Glass estetiğinde, gösterişsiz, sofistike ve NOVA'nın lüks mimari kimliğine uygun olmalı.

### First glass iteration — historical implementation and verification
- Dark neutral frosted glass rail, thin white rim, translucent sliding indicator, unchanged
  flag artwork, visible TR/EN labels at every breakpoint. Header and offcanvas share the style.
- Changes restricted to the last language-selector section in `css/styles.css`, language-control
  markup on 66 pages, and a cosmetic arrival-animation helper in `js/script.js`. Native href,
  hreflang, lang, aria-current and navigation behavior remain unchanged. No new integration,
  storage, backend or mocked functionality. Referrer-based animation does not intercept links.
- `scripts/language_toggle_markup.py` patches only existing controls, is idempotent, and is
  also called by the existing builder's selector insertion for future use after source reconciliation.
- Testing agent: `test_reports/iteration_61.json`; 6 targeted + 53 serving-mode + 98 static
  tests passed (157 total). All 66 pages verified byte-identical to branch outside selectors;
  shared CSS before the selector block also byte-identical.
- Follow-up fixed compact hit areas: desktop >=44px wide x48.5px high; phones 44x47px;
  constrained 769–900px tablet controls 28x45.5px (>=24px minimum without moving neighboring
  elements). Expanded areas verified clickable. Reduced-motion CSS specificity corrected and
  verified after real TR->EN navigation. Final targeted regression rerun: 6/6 passed.
- Browser geometry comparison at 320/390/768/800/900/1024/1440/1920 confirmed unchanged header,
  logo, menu, enquiry-button and contact-icon rectangles. No horizontal overflow.
- Baseline-sensitive test `tests/test_lang_toggle_regression.py` currently requires the downloaded
  archive at `/tmp/nova-branch/nova-2026-purejs-<commit>/frontend`; retrieve that exact commit if
  running this comparison in a fresh environment.

### Next actions / boundaries
- P0 (current request): none remaining after verification.
- P1: user visual approval; earlier local VS Code/Live Server issue remains agent-tested but
  not confirmed on the user's machine. cPanel structure/rules were not changed by this work.
- P2: reconcile branch-authored pages with authoring sources before any full regeneration;
  existing form-delivery and legal-confirmation backlog remains outside this visual-only task.
- Suggested future enhancement: optimize remaining project images for faster mobile browsing.

## Product
Static NOVA Konut marketing website (vanilla HTML/CSS/JS in `/app/frontend`). **Since
2026-06-25 the site is frontend-only:** NOVA Journal reads pre-generated JSON committed by
GitHub Actions in the separate `kaankara34/nova-news-feed` repository. The Python news
backend (FastAPI + MongoDB + Gemini) has been removed. The remaining `/app/backend`
(`server.py`, `enquiries.py`) only serves the Register-Interest form + Instagram strip and is
NOT required to publish the site to cPanel.

Brand rules: preserve the established NOVA visual language; never change global
header/nav/footer structure, the homepage project grid, project-card badges, sales
language or completed project pages unless explicitly asked.

## News architecture (static)
- Feeds: `https://raw.githubusercontent.com/kaankara34/nova-news-feed/main/data/news-en.json`
  and `.../news-tr.json`. GitHub Actions generates and commits them; the browser only GETs
  the committed file (normal browser caching, no `no-store`).
- `frontend/js/news.js` is the single loader/renderer (homepage strip, `newsroom.html`,
  `news-detail.html?id=<article.id>`), validates the payload, caches the last valid feed in
  `localStorage` per language (`nova-news-feed:en` / `:tr`, 30-minute TTL then background
  refresh), renders with `createElement`/`textContent` only, falls back to the NOVA category
  covers in `media/news/fallback/` on a missing or failing image, filters/searches in memory
  (no refetch on filter change) and shows “News is temporarily unavailable.” /
  “Haberler geçici olarak kullanılamıyor.” when there is no valid cache.
- Language comes from `document.documentElement.lang` (`tr*` → Turkish feed, else English).


## Architecture
- Frontend: static pages, `css/styles.css` (global + East West feature), `css/newsroom.css`
  (journal + Get in Touch), `js/news.js` (journal rendering), `js/east-west-feature.js`
  (East West carousel + perimeter progress), `js/architects.js` (architect marquee).
- Backend `news/` package:
  - `sources.py` — verified feed allowlist, institutional crawl targets, disabled list with
    the observed reason for each publisher, category minimum.
  - `ingest.py` — refresh orchestration, lock, 15-day window, dedupe, excerpt, lifecycle,
    reprocessing, featured selection + homepage snapshot.
  - `extract.py` — robots-aware article fetch + text/date/image extraction (JSON-LD, OG,
    Twitter).
  - `crawl.py` — robots-aware listing crawler for institutions without feeds (KİPTAŞ).
  - `filters.py` — relevance scoring and multi-category classification (strict Kadıköy rule).
  - `editorial.py` — hard subject exclusions, TECHNICAL & LEGAL scope test, editorial tone
    and brand-safety verdict.
  - `ai.py` — the only Gemini integration point: model/key from env, persistent daily
    request/token budgets, bounded backoff, long-form synthesis quality gate.
  - `images.py` — image validation (min 1000×550), local WebP derivatives, category covers.
  - `validate.py` — editorial casing normalisation, all-caps de-shouting, source URL checks.
  - `api.py` — public cached endpoints + protected refresh/synthesise/health endpoints.
- Scheduler: APScheduler cron 06:00 Europe/Istanbul in-process, plus the protected
  `POST /api/admin/news/refresh` endpoint for a durable platform scheduler (lock-guarded).

## Editorial rules in force
- Rolling public window: 15 days on `published_at`; enforced in the database query.
- Lifecycle: `pending_editorial → generating → published`, with `needs_review`,
  `quality_failed`, `insufficient_source`, `source_invalid`, `rejected`, `expired`.
- A detail page is only published with a stored body ≥ `NEWS_MIN_BODY_WORDS` (600).
- Card excerpt 45–75 words, whole sentences, no merged words, no slicing.
- Image precedence: feed media → enclosure → JSON-LD → Open Graph → Twitter → NOVA
  category cover (disclosed only when the fallback is used).
- Hard-excluded subjects (livestock, agriculture, food, veterinary, sport, entertainment,
  unrelated transport/consumer/legal) are rejected before any AI call.
- CONSTRUCTION accepts positive/constructive framing and genuine technical developments;
  decline/crisis/collapse framing is excluded, never rewritten.
- Kadıköy requires district-level context; the category stays empty rather than padded.

## Environment keys (values never in code)
`MONGO_URL`, `DB_NAME`, `CORS_ORIGINS`, `NEWS_ADMIN_TOKEN`, `NEWS_INGEST_ENABLED`,
`NEWS_WINDOW_DAYS`, `NEWS_REFRESH_HOUR`, `NEWS_REFRESH_MINUTE`, `NEWS_SYNTHESIS_PER_RUN`,
`NEWS_PUBLISH_WITHOUT_AI` (false), `NEWS_MIN_BODY_WORDS`, `NEWS_MAX_BODY_WORDS`,
`GEMINI_API_KEY` (to be added through the platform secret manager), `GEMINI_MODEL`
(`gemini-2.5-flash-lite`), `GEMINI_DAILY_REQUEST_LIMIT`, `GEMINI_DAILY_INPUT_TOKEN_LIMIT`,
`GEMINI_DAILY_OUTPUT_TOKEN_LIMIT`, `GEMINI_MAX_CONCURRENCY`, `GEMINI_REQUEST_TIMEOUT_SECONDS`.

## Current state (2026-06-25 — static conversion + contained intro-video hero)
- **News backend removed.** Deleted `backend/news/` (12 modules incl. `ai.py` Gemini
  integration), `backend/tests/test_ingestion_gating.py`, `backend/tests/test_newsroom_api.py`,
  `scripts/probe_feeds.py`, the APScheduler job and the `/api/news*` routes from
  `backend/server.py`, plus `frontend/data/news-featured.json` / `news-fallback.json`.
  No `GEMINI_API_KEY`, no Gemini/Mongo/news code anywhere in the project; no API key in
  frontend code. `frontend/` is deployable to cPanel `public_html` as-is.
- **Homepage intro video:** the user's promo (`WEB_PROMO (1).mp4`, 1926×1080, 44.5s, 22.6MB)
  is now the hero. Renditions in `frontend/media/videos/`: `hero-nova-960.mp4` (3.3MB),
  `hero-nova-1280.mp4` (6.4MB), `hero-nova-1600.mp4` (7.6MB), `hero-nova-1280.webm` (5.4MB,
  codec fallback), `hero-nova-poster.webp` (56KB). Original kept at
  `/app/media-source/WEB_PROMO-original.mp4` (outside the deployable folder).
- **Hero geometry:** `.hero` is contained — `margin-top: calc(var(--utility-h) + var(--header-h))`,
  `height: clamp(540px,62vh,720px)` desktop / `clamp(480px,58svh,640px)` ≤1024 /
  `clamp(410px,58svh,560px)` ≤768, with a centred downward triangle produced by a `clip-path`
  polygon (`--notch-width/--notch-height`). The overlaid NOVA logo (`.hero-brand`,
  `.big-logo`, `.hero-brand-mark`), the overlaid `BUILD BEYOND LIVING` line (`.hero-tagline`
  with its rules) and the `heroRise` animation were deleted from the DOM and CSS — the header
  logo and the white-section BBL heading are untouched. The homepage header is now always
  solid (`.hero` removed from the transparency selector in `js/script.js`).
- **Register Interest e-mail pipeline** still exists in `backend/enquiries.py` but is a
  server feature: on static cPanel hosting the forms will POST to a non-existent `/api`
  endpoint until a static form service (Formspree/Netlify Forms) or a mail script is wired.
- East West floor plans, projects filters, Taç hero, navigation/contact cleanup: unchanged
  (see CHANGELOG).

- **Register Interest e-mail pipeline: BUILT and verified** (`POST /api/enquiries`, 10/10 backend tests, 6/6 form flows). **BLOCKED on the user's nova.istanbul SMTP credentials** — submissions are stored in Mongo with `email_status: smtp_not_configured` until `SMTP_HOST/PORT/SECURITY/USERNAME/PASSWORD` and `MAIL_FROM` are filled in `backend/.env`. `MAIL_TO` is already `iletisim@nova.istanbul`. Read the queue any time with `GET /api/admin/enquiries` + `X-Admin-Token`.
- **Homepage collaborations video:** now the user's promo (`collab-nova.webm` VP9 + `collab-nova.mp4` faststart H.264). Section dimensions untouched (3/1 desktop, 16/10 mobile, `object-fit: cover`) — the 16:9 source is therefore cropped top/bottom by design.
- **East West floor-plan section:** left at its original generous height — the compaction pass was reverted at the user's request (section ~1395px at 1440×900, plan 597×896). Do not re-apply it unless asked.
- **`projects.html` filters:** seven English filters (`ALL`, `RESIDENTIAL`, `MIXED USE`, `OFFICE / COMMERCIAL`, `FUTURE PROJECTS`, `ONGOING PROJECTS`, `COMPLETED PROJECTS`). Type and status are independent `data-project-type` / `data-project-status` attributes plus a `data-project-slug`; no text matching, no Turkish strings, `KONAKLAMA` fully removed. 14 cards: 3 ongoing (East West/Taç/Ana), 1 future (Finance Nova, mixed-use), 10 completed; 8 residential, 2 mixed-use, 4 office-commercial.
- **East West DOWNLOAD BROCHURE** serves `media/docs/the-residences-east-west-brochure.pdf` (the user's printed catalogue).
- **The Apartments Taç hero** is now the aerial construction still (`media/images/tac/tac-construction-aerial.webp` + 1280px variant) with the premium dark filter, vignette scrim and a slow drift; the old hero video and `media/video/` were deleted.
- **East West floor plans:** EAST and WEST both complete with the user's own drawings (8 transparent WebP files, all 1240×1860, identical render box). Shared circulation excluded; Fire Lobby counted inside the apartment. Header reads **TOTAL AREA** and sums **every** listed row including balconies: EAST 3+1 142.50 m², 4+1 142.16, duplex 224.27; WEST 3+1 138.40, 4+1 138.06, duplex 217.48. 4+1 dims its left half. Plan data lives in `js/ew-plans-data.js`.
- **Site-wide navigation, contact and Dar Global cleanup: DONE and verified** (iteration_53.json, frontend 100%). TAÇ/ANA menu destinations on all 25 non-index pages, featured menu cards, VIEW ALL/PORTFOLIO/NEWSROOM, dead ANATOLIAN/EUROPEAN SIDE entries removed, "The Apartments Gür" card deleted, every Instagram link → instagram.com/novakonut/, homepage hero Dar Global wordmark + "LIVE ALL IN" + broken `cdn.Nova.co.uk` images replaced with the NOVA logo / "BUILD BEYOND LIVING" / local renders, east-west "Premiere Edition COLLECTION" badge replaced, footer geography columns replaced with NOVA's three projects on all 26 pages (design preserved), all 17 register forms reduced to the three current projects, Escape/aria-expanded/focus-return on the side menu, touch targets ≥44px, no horizontal overflow at 1440/1280/1024/768/430/390/844×390.
- The site has **no `sms:` link anywhere** — there is no SMS button in the design. WhatsApp is the messaging destination.
- East West homepage feature: contained (panel 540px desktop), 5s slide duration, 600ms crossfade, SVG perimeter progress on the same timer, mobile 779px @390 and 841px @430.
- Get in Touch styled on `newsroom.html` and `news-detail.html`.
- Newsroom database: 148 `pending_editorial`, 10 `insufficient_source`, 1 `needs_review`,
  4 `rejected` (1 irrelevant livestock, 3 brand-unsafe negative). 0 published — every
  article is waiting for the Gemini long-form synthesis.
- Images: 112 authentic cached vs 51 NOVA covers across stored records.
- `/app/clean-site/` is an unserved reference scaffold and still contains the original Dar Global
  markup, old phone numbers and a `lang-switch`. It is not part of the published site; delete it
  if it ever risks being served.

## Backlog
- **P0: static form delivery.** The Register Interest forms still POST to `/api/enquiries`
  (Python). For cPanel, wire them to a static form service or a small PHP mail handler, or
  keep the FastAPI service on a separate host.
- P1: Turkish site version — the news loader already switches on `document.documentElement.lang`,
  so only the page copy/language toggle is missing.
- P2: WebP/AVIF sweep and lazy-loading audit for the remaining project renders.
- **P0: SMTP credentials for `iletisim@nova.istanbul`.** Fill `SMTP_HOST`, `SMTP_PORT`,
  `SMTP_SECURITY` (`starttls` for 587 / `ssl` for 465), `SMTP_USERNAME`, `SMTP_PASSWORD` and
  `MAIL_FROM` in `backend/.env`, restart the backend, submit one test form and confirm
  `email_status` flips from `smtp_not_configured` to `sent`. Then configure SPF/DKIM/DMARC with
  the mail host so the notifications are not spam-filed.
- P0: add `GEMINI_API_KEY` secret → run the 15-day synthesis backfill, verify rendered
  detail pages, report pass/fail counts per category.
- P2: durable platform scheduler wired to `POST /api/admin/news/refresh`.
- P1: Kadıköy coverage depends on new KİPTAŞ/press publications; keep monitoring daily.
- P2: durable platform scheduler wired to `POST /api/admin/news/refresh`.
- P2: a MongoDB outbox worker for enquiry e-mail (the current `BackgroundTasks` send is lost if
  the process dies mid-flight; the submission itself is always persisted first).

## 2026-06-28 — Speak Up & Careers interfaces, footer/nav restructure, legal notices

Implemented (frontend only, tested — `test_reports/iteration_56.json`, frontend 100%):
- `frontend/anonymous-reporting.html` + `js/speak-up.js` — Speak Up confidential reporting interface.
- `frontend/careers.html` + `js/careers.js` — Construction Site Manager (Architect) application interface.
- `frontend/css/action-pages.css` — shared styling for both.
- Footer restructured on all 31 static pages; CAREERS / SPEAK UP added to the side menu; `Get in Touch` → `index.html#register`.
- `privacy-notice.html`, `cookie-notice.html`, `ethical-principles.html` rewritten via `scripts/build_legal_pages.py`; technical provider inventory kept internally in `memory/technical-inventory.md`.
- Cookie banner is informational only; storage key `nova_cookie_notice_dismissed`.

### NOT built — explicit product boundary
Both new forms are interfaces, not systems. They send nothing, store nothing and show an
explicit "not sent / not saved" notice. Do not wire them to a backend or show a success
state without the user's approval and a real secure pipeline.

### Backlog added by this work
- **P0 — Speak Up backend.** Requires a defined reporting workflow, access control, confidentiality
  model, investigation/escalation procedure, retention schedule and secure attachment scanning +
  storage before any submission channel is enabled. Reference IDs only if genuinely generated.
- **P0 — Careers backend.** Secure CV object storage, file scanning, recipient list, retention
  schedule and an applicant privacy notice matching the actual processing.
- **P0 — NOVA/legal confirmations still open:** hosting & e-mail provider locations and whether they
  involve cross-border transfer; the Article 9 lawful transfer condition/safeguard actually relied on;
  applicant and reporter data recipients, systems and retention periods; whether an actual anonymous
  channel will exist. Legal compliance is NOT claimed anywhere on the site.
- **P1** — reduce avoidable third-party requests (self-host typefaces and the animation library) to
  shrink the cross-border transfer surface described in the Privacy Notice.
- **P2** — the duplicated header/side-menu/footer markup across 31 files drifted again
  (`construction.html`). A build-time partial + a CI grep gate for banned strings is overdue.


## 2026-09-29 — Careers split, Applicant Privacy Notice, Speak Up refinement, cookie banner removed

New URLs: `construction-site-manager-architect.html`, `applicant-privacy-notice.html`.
Changed: `careers.html` (landing only), `anonymous-reporting.html`, `privacy-notice.html`,
`cookie-notice.html`, `ethical-principles.html`, `index.html`, `js/script.js`, `js/careers.js`,
`js/speak-up.js`, `css/action-pages.css`, `scripts/build_action_pages.py`,
`scripts/build_legal_pages.py`. Tested: `test_reports/iteration_57.json` (frontend 100%).

### Product boundary — unchanged and deliberate
Both forms are complete, visible front ends with a single isolated submission adapter each
(`submitApplication()` / `submitReport()`), endpoint `null`. They transmit nothing, store nothing
and never show a success state. No visitor-facing page explains this. Do not add an endpoint, a
success message or storage without the user's approval and a real receiving service.

### P0 — backends to connect
- **Careers**: secure receiving service + CV object storage with virus scanning, recipient list,
  retention schedule. Set `APPLICATION_ENDPOINT` in `js/careers.js` only.
- **Speak Up**: defined reporting workflow, access control, confidentiality model, investigation
  and escalation procedure, retention schedule, attachment scanning. Set `REPORT_ENDPOINT` in
  `js/speak-up.js` only. Introduce acknowledgement/reference IDs only if genuinely generated.
- **Register Interest** forms still POST to `/api/enquiries` (FastAPI) — needs a static-hosting
  solution for cPanel.

### P0 — items NOVA must verify (see `memory/technical-inventory.md` §Open questions)
Hosting and mailbox provider locations; Article 9 condition/safeguard per overseas connection;
retention periods for enquiries, reports and applications; who receives Speak Up reports; whether
a talent-pool retention period (and separate explicit consent) is wanted; whether the production
host injects its own scripts or cookies. Legal compliance is NOT claimed anywhere on the site.

### P1 / P2
- P1: self-host typefaces and the animation library to shrink the cross-border request surface.
- P2: build-time partial for header/side-menu/footer + CI grep gate (markup has drifted twice).

### 2026-09-29 (correction) — cookie banner is IN SCOPE and must stay
The informational cookie banner on `index.html` was removed in error and has been restored with
the user's concise copy. Do not remove it again. `nova_cookie_notice_dismissed` is a dismissal
flag only — never treat or describe it as a consent record, and never reuse it for marketing.
The public Privacy Notice and Cookie Notice are back to their pre-29-September text; do not
rewrite them again without an explicit request.

## 2026-10-02 — Bilingual site: Turkish default (`/tr/`) + English (`/en/`)

The site is now a complete two-language static website. **Turkish is the default language.**

### Source of truth
- `/app/source-pages/*.html` — the approved English pages. **These are the only place English
  copy is edited.** They are not served.
- `/app/scripts/i18n_tr/*.json` — the Turkish dictionaries (2061 entries). **The only place
  Turkish copy is edited.** Build-time only; the browser never requests them.
- `python3 scripts/build_i18n.py` — regenerates `frontend/en/` (33 pages), `frontend/tr/`
  (33 pages), `sitemap.xml`, `robots.txt`, `.htaccess` and the `serve.json` redirects.
  **Never hand-edit files inside `frontend/en/` or `frontend/tr/` — they are overwritten.**
- `python3 scripts/i18n_report.py` — untranslated-string report (must stay at 0).
- `python3 scripts/i18n_audit.py` — full static audit (must stay at 0 problems).
- `python3 -m pytest tests/test_static_pages.py` — 98 HTTP/content checks.

### Hard rules
- No runtime translation: no framework, no i18n library, no JSON fetch, no JS text swapping.
  Turkish text is static HTML.
- The English site must stay unchanged in meaning, layout, visuals and interactions. The audit
  compares `/en/` visible text against the sources; it must report 0 differences.
- Protected project names, never translated or re-slugged: **The Residences East West**,
  **The Apartments Taç**, **The Apartments Ana**. Brand-like and unchanged: Mercan Bosphorus,
  Nisbetiye On, Falcon Plaza, Finance Nova, Build Beyond Living, Martı / Bahar / Doğan /
  Mehtap Residence.
- Turkish slugs are ASCII-safe. Pages that exist in `PAGE_MAP` in `build_i18n.py` are the
  complete, deliberate URL map — add new pages there, in both languages.
- Asset references in generated pages must resolve from both supported serving modes:
  `../css`, `../js`, and `../media`. `portable_assets()` handles generated HTML. Shared
  JavaScript that creates URLs must derive the site root from `document.baseURI` (see
  `js/materials3d.js`, `js/ew-plans-data.js`, `js/news.js`) rather than starting paths with `/`.
- The language selector must always open the **same page** in the other language.
- `serve.json` needs the explicit `/tr`, `/tr/`, `/en`, `/en/` redirects — without them
  `serve` returns a directory listing. `routing()` generates them.

### Status
Complete and verified: 0 untranslated strings, 0 audit problems, 0 English differences,
98/98 pytest, 0 4xx across all 66 pages, `test_reports/iteration_59.json` frontend 100%.

### Still open (unchanged by this work)
- P0: Register Interest / Careers / Speak Up form delivery — all three remain honest
  frontend-only adapters that transmit nothing and never show a success state.
- P0: NOVA legal confirmations listed in `memory/technical-inventory.md` §Open questions.
- P1: production `.htaccess` verification on Turhost, sitemap submission for both languages.

## 2026-10-08 — VS Code Live Server local document root

- Generated HTML now uses portable `../css`, `../js`, `../media`, `../tr`, and `../en` paths.
  Pages therefore work both when VS Code serves the repository as `/frontend/...` and when
  cPanel serves the contents of `frontend/` directly from `public_html/` as `/tr/...`.
- Dynamic paths in `news.js`, `materials3d.js`, and `ew-plans-data.js` derive the correct site
  root from `document.baseURI`, preserving news routes, fallback covers, design textures, and
  East West floor plans in both environments.
- No committed VS Code Live Server root override is used. This is deliberate: forcing
  `/frontend` breaks when the developer has already opened `frontend/` as the workspace.
  Portable page paths support both workspace choices without editor-specific configuration.
- Verification: build generated 33 EN + 33 TR pages; 0 untranslated strings, 0 audit problems,
  ESLint passed, dual-root regression 53/53 passed, existing static suite 98/98 passed, and
  Playwright flows passed in both modes (`test_reports/iteration_60.json`).
