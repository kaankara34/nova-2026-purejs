# NOVA — Prioritised backlog (updated 2026-06)

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
