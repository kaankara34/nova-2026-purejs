# NOVA Konut — Product Requirements & State

Last updated: 2026-09-19

## Product
Static NOVA Konut marketing website (vanilla HTML/CSS/JS in `/app/frontend`) with a
FastAPI + MongoDB backend (`/app/backend`) that powers **NOVA Journal**, an aggregated
newsroom (homepage strip, `newsroom.html`, `news-detail.html`).

Brand rules: preserve the established NOVA visual language; never change global
header/nav/footer structure, the homepage project grid, project-card badges, sales
language or completed project pages unless explicitly asked.

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

## Current state (2026-06, updated after the promo video / form-mail / floor-plan round)
- **Register Interest e-mail pipeline: BUILT and verified** (`POST /api/enquiries`, 10/10 backend tests, 6/6 form flows). **BLOCKED on the user's nova.istanbul SMTP credentials** — submissions are stored in Mongo with `email_status: smtp_not_configured` until `SMTP_HOST/PORT/SECURITY/USERNAME/PASSWORD` and `MAIL_FROM` are filled in `backend/.env`. `MAIL_TO` is already `iletisim@nova.istanbul`. Read the queue any time with `GET /api/admin/enquiries` + `X-Admin-Token`.
- **Homepage collaborations video:** now the user's promo (`collab-nova.webm` VP9 + `collab-nova.mp4` faststart H.264). Section dimensions untouched (3/1 desktop, 16/10 mobile, `object-fit: cover`) — the 16:9 source is therefore cropped top/bottom by design.
- **East West floor plans:** 3+1 / 4+1 / DUPLEX LOWER replaced with the user's drawings, transparent WebP, all normalised to 1240×1860 so tabs never resize the plan; 4+1 dims its left half; schedules fully in English. **DUPLEX UPPER still shows the old image pending the user's new drawing.**
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
- **P0: SMTP credentials for `iletisim@nova.istanbul`.** Fill `SMTP_HOST`, `SMTP_PORT`,
  `SMTP_SECURITY` (`starttls` for 587 / `ssl` for 465), `SMTP_USERNAME`, `SMTP_PASSWORD` and
  `MAIL_FROM` in `backend/.env`, restart the backend, submit one test form and confirm
  `email_status` flips from `smtp_not_configured` to `sent`. Then configure SPF/DKIM/DMARC with
  the mail host so the notifications are not spam-filed.
- P0: add `GEMINI_API_KEY` secret → run the 15-day synthesis backfill, verify rendered
  detail pages, report pass/fail counts per category.
- P1: DUPLEX UPPER floor plan — the user will send the drawing; process it through
  `scripts/process_ew_plans.py` so it matches the 1240×1860 transparent canvas.
- P1: Kadıköy coverage depends on new KİPTAŞ/press publications; keep monitoring daily.
- P2: durable platform scheduler wired to `POST /api/admin/news/refresh`.
- P2: a MongoDB outbox worker for enquiry e-mail (the current `BackgroundTasks` send is lost if
  the process dies mid-flight; the submission itself is always persisted first).
