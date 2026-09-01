# CHANGELOG

## 2026-06 — Contact page additions (contact.html)
- `ct-intro`: added a quiet constructivist SVG art mark (brass arc, dotted slow-orbit ring, sage/brass disc, stone block, hairlines). Respects `prefers-reduced-motion`.
- New Instagram section between `ct-detail` and `ct-loc`: "Latest from Nova" head, `@novakonut` follow link, 4 square tiles (NOVA-generated imagery, all linking to the profile), follow note. 4 columns desktop / 2 columns ≤767px.
  - NOTE: Instagram cannot be scraped (HTTP 403) — tiles use NOVA's own imagery and link out; this is NOT a live feed.
- Register Interest before the footer: the project-page (Martı) split composition rebuilt as scoped `ct-reg` / `ct-form`, retoned to Contact's warm palette (#E8DFD2 ground, ink text, brass italic sub, ink submit). UI-only submit handler in `js/contact.js` (`#ctRegisterForm`) with inline status message.
- Files: `scripts/contact_main.html`, `frontend/css/contact.css`, `frontend/js/contact.js`, regenerated `frontend/contact.html` (448 lines) via `scripts/build_contact.py`.
## 2026-06 — Contact revision (real IG posts + birds film)
- Instagram tiles now show NOVA's **real latest 4 posts**, fetched via the public `i.instagram.com/api/v1/users/web_profile_info` endpoint (x-ig-app-id header), images stored locally at `frontend/media/images/contact/ig/post-1..4.jpg`, each tile deep-links to its post permalink (shortcodes DaQk9OvscF6, DaQbe_FMl7l, DaQadKFjHXG, DaN8eQ2s4pu). Tiles are 4:5 like Instagram. NOTE: static snapshot, not a live feed — re-run the fetch to refresh.
- `ct-intro` art replaced: the SVG mark removed, now a muted birds-rising-from-a-tree film (autoplay/muted/loop/playsinline) at `frontend/media/video/birds.mp4|.webm` + poster, toned with a warm veil and hairline frame. Source: Pexels free-licence clip 5024947 (Aman's own Vimeo clip was not reused for licence reasons).
- Verified: desktop 1920 + mobile 390 screenshots, 0 horizontal overflow, form error/success paths, oxlint 0 warnings/0 errors on contact.js. User visual confirmation pending.
