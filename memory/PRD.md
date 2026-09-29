# NOVA Konut — Product Requirements & State

Last updated: 2026-09-19

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
