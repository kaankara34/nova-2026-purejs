# NOVA — Prioritised backlog

## Current priorities — 2026-10-26 (supersedes historical sections below)
-2026-10-27 currentEDSAA/mobilejournal/scrollbarrequest COMPLETEinpreview:271tests pass.
  P1:visualreview and,afterpublication, realproductionHTTP/indexabilitycheck plusSearchConsole
  sitemap/URLInspection. NoSearchConsoleorindexingresultclaimed. Details:EDSAA_DELIVERY.md.
- P2:monitorEDSAA-brandedqueriesafterpublicationwithoutaddingunapprovedcopy. Existingphysical
  videoacceptance/source-template reconciliation remainindependent,unresolvedhistoricaltasks.
-2026-10-27 latest request complete in preview: recurring mobile bar freeze reproduced/fixed,
 3px bronze+glint, no side-menu switch, supplied favicon, all66pages follow final same-language
  index navbar/footer CONTENT while retaining page styles.256tests pass and30s+ mobile loop test
  passes. P1:user physical-phone confirmation; do not claim physical iOS/Android tests.
- Canonical content maintenance: edit EN/TRindex, run `scripts/sync_site_chrome.py`, preserve page
  palettes. Do not use a full stale i18n rebuild to synchronize chrome.
- Current task implementation: shared hero lifecycle, menu visibility, perimeter transforms,
  optimized header logos and theme-aware switch completed;242regression+10isolated tests pass.
- **P0 verification:** real iOS Safari/Android Chrome app-switch/scroll/BFcache video acceptance
  remains pending. Headless codec/decoder limitations are explicitly documented; do not claim
  physical-device success or add playback-reset workarounds solely for the headless engine.
- P1: user visual acceptance; checklist in `memory/UI_VIDEO_PERFORMANCE_REPORT.md`.
- Latest request implemented: very light flag-only glass pane; desktop action order now enquiry,
  phone/message, then language. Knob and navigation/gesture JS unchanged.170tests passed;12/12
  follow-up short-touch trials passed after an initial unreproduced CDP observation. P1:visual approval.
- Latest user override VERIFIED: OPAQUE neutral opal-glass knob, enlarged24px/18px diameter,
  equal1px gaps, country-specific authentic flag focus in exposed half; unchanged outer geometry.
  `iteration_64.json`,165tests plus CDP touch follow-up. Do not restore translucency or centered
  flag artwork hidden by knob. P1 remains final visual approval; no current P0 defect.
- Latest targeted refinement verified: authentic full-rail flag SVG + clear glossy knob,
  unchanged geometry and nearest-endpoint release (`iteration_63.json`,165tests). Await visual
  approval. Do not restore half-flag windows, hand-drawn flags, matte-grey fill or velocity flick.
- Optional design-protection follow-up: persistent visual regression baseline for the switch.
- Latest follow-up: true circular glass switch with click/drag/swipe and release-only commit is
  implemented and verified (`iteration_62.json`,63 final automated checks). Await user visual and
  physical-device gesture approval; do not restore the old segmented design.
- P0 for branch import + glass language toggle: no remaining blockers; tested and ready for user review.
- P1: user visual approval; user's own Live Server verification remains pending from the earlier task.
- P2: reconcile branch-authored EN/TR HTML with source templates/dictionaries before any full rebuild.
  Current authoritative branch commit is `3a238f1c6ef793f1cd75583ca6f9bbd7bb6a88f9` plus the targeted
  toggle redesign. Do not run the old full i18n build and erase the user's manual edits.
- Existing static form-delivery/legal confirmations remain separate, unmodified work.
- Enhancement candidate: optimize remaining project images for faster mobile browsing.

## Historical backlog (some infrastructure entries below are obsolete)

## P0 — production requirements for the newsroom
- **Real production scheduler.** In this preview the 6-hour ingestion runs inside the
  supervisor-managed FastAPI process (APScheduler, Europe/Istanbul). On the production host either
  (a) keep a single always-on backend process (the in-process scheduler then works as-is), or
  (b) disable it with `NEWS_INGEST_ENABLED=false` and call
  `POST /api/admin/news/refresh` with the `X-Admin-Token` header from an external cron
  (`0 */6 * * *`, Europe/Istanbul). With more than one web replica, option (b) is required to avoid
  duplicate runs. **Not yet verified in production.**
- **Persistent MongoDB** for `news_items` / `news_sources` / `news_runs` in the deployed environment.
- **Rotate `NEWS_ADMIN_TOKEN`** for production and keep it out of Git.
- Optional: set `GEMINI_API_KEY` (free tier) to switch summaries from the deterministic fallback to
  reviewed AI summaries; `NEWS_AI_MAX_REQUESTS_PER_RUN` protects the quota.

## P1
- Turkish official sources still have no lawful feed (Resmî Gazete, Kadıköy Belediyesi, İBB, Çevre ve
  Şehircilik Bakanlığı, Kentsel Dönüşüm Başkanlığı). Revisit periodically or obtain permission /
  a licensed API before enabling them; they must stay disabled until then.
- Kadıköy and URBAN_TRANSFORMATION categories currently have no matching items because no enabled
  source published one — worth adding a permitted Turkish urban-policy publisher.
- Editorial moderation view (`status: pending/rejected/archived` already exists in the data model)
  so an editor can hold or drop an item before it appears publicly.
- Social-crawler SEO for `news-detail.html?slug=…` needs server-side rendering or prerendering; the
  page updates its metadata client-side today.

## P2
- The duplicated header / side-menu / footer markup across 26 HTML files has already drifted twice
  (`construction.html` + `leed.html` footers). Worth a build-time include or partial, plus a CI grep
  gate for the banned strings: `LIVE ALL IN`, `DAR GLOBAL`, `DARGLOBAL`, `PREMIERE EDITION`,
  `Luxury Villas`, `api.whatsapp.com`, `tel:+12127151067`, `tel:+908502000000`.
- Remaining `href="#"` placeholders that are not brand issues: footer `AGENT CONNECT`,
  `INVESTOR RELATIONS`, `BLOGS`, `PRESS`, `CAREERS`, `Get in Touch`, `Why Invest`,
  `Data Privacy Statement`, `TERMS AND CONDITIONS`, side-menu `BOARD`, and the Facebook / Twitter /
  LinkedIn / Linktree social icons (no NOVA accounts supplied yet). Need real destinations from the
  client.
- `projects.html` still lists "The Apartments Gür" in no card (deleted) but the project itself has
  no page — confirm whether it is a real future project.
- `newsroom.html` could gain an RSS/Atom feed of NOVA's own selections.

## Done (do not re-open)
- Global navigation NEWSROOM → `newsroom.html` and PORTFOLIO → `projects.html` on all 26 pages.
- Homepage hero Dar Global identity, the three Dar Global hero images and the "DISCOVER DARGLOBAL"
  band: all replaced with NOVA content (June 2026).
- Footer link lists and every register-form project option list: now NOVA-only (June 2026).


## DONE — Turkish localisation (completed 2026-10-02)
All 33 TR pages are fully localised; `scripts/i18n_report.py` reports 0 untranslated words and
`scripts/i18n_audit.py` reports 0 problems. Do not re-open. To change Turkish copy, edit the
matching entry in `scripts/i18n_tr/*.json` and re-run `python3 scripts/build_i18n.py`.
To change English copy, edit the page in `/app/source-pages/` and rebuild.

## P1 — bilingual follow-ups
- Production verification on Turhost/cPanel: confirm `mod_rewrite` is enabled and
  `frontend/.htaccess` sits in the document root, then check `/` → `/tr/` and a legacy URL such
  as `/projects.html` → `/en/projects.html` on the live host.
- Submit the new `sitemap.xml` (66 URLs) to Search Console for both language versions.
- Turkish news feed: `news-tr.json` content is produced by the external GitHub Actions
  repository — confirm the Turkish feed is being published as expected.
