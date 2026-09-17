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
- Global navigation still points NEWSROOM at `index.html#news`; changing it to `newsroom.html` was
  deliberately skipped because the shared header/nav is out of scope. Needs a decision.

## P2
- Homepage hero, the three DarGlobal hero images and the "DISCOVER DARGLOBAL" section are still
  DarGlobal placeholders (explicitly out of scope in the June 2026 task).
- Footer link lists and the register-form project options still contain DarGlobal-era content.
- `newsroom.html` could gain an RSS/Atom feed of NOVA's own selections.
