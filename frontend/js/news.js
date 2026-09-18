/* ==========================================================
   NOVA JOURNAL — homepage strip, newsroom index, detail page.
   Data only ever comes from the NOVA backend (/api/news*) or the
   pre-generated local snapshot. The browser never contacts a
   publisher feed. Nodes are built with createElement/textContent.
   ========================================================== */
(function () {
  'use strict';

  const API = document.body.dataset.api || '';
  const SNAPSHOT_URL = 'data/news-featured.json';
  const REQUEST_TIMEOUT = 2200;
  const CATEGORY_LABELS = {
    ART: 'Art',
    EXHIBITIONS: 'Exhibitions',
    GALLERIES_AND_MUSEUMS: 'Galleries & Museums',
    ARCHITECTURE_AND_DESIGN: 'Architecture & Design',
    CONSTRUCTION: 'Construction',
    URBAN_TRANSFORMATION: 'Urban Transformation',
    KADIKOY: 'Kadıköy',
    TECHNICAL_AND_LEGAL: 'Technical & Legal'
  };

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  function formatDate(value) {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return '';
    return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
  }

  const categoryLabel = function (key) { return CATEGORY_LABELS[key] || 'Journal'; };
  const detailHref = function (item) { return 'news-detail.html?slug=' + encodeURIComponent(item.slug); };
  const safeExternal = function (url) { return /^https:\/\//i.test(url || '') ? url : ''; };

  function fallbackCover(category, variant) {
    const slug = String(category || 'ART').toLowerCase().replace(/_/g, '-');
    return 'media/news/fallback/' + slug + '-' + variant + '.webp';
  }

  function cardImage(item) {
    return item.image_card || fallbackCover(item.category, 'card');
  }

  function detailImage(item) {
    return item.image_detail || fallbackCover(item.category, 'detail');
  }

  async function request(path, signal) {
    const res = await fetch(API + path, { signal, headers: { Accept: 'application/json' } });
    if (!res.ok) {
      const error = new Error('status ' + res.status);
      error.status = res.status;
      throw error;
    }
    return res.json();
  }

  function timedRequest(path) {
    const controller = new AbortController();
    const timer = setTimeout(function () { controller.abort(); }, REQUEST_TIMEOUT);
    return request(path, controller.signal).finally(function () { clearTimeout(timer); });
  }

  let snapshotPromise = null;
  function snapshot() {
    if (!snapshotPromise) {
      snapshotPromise = fetch(SNAPSHOT_URL, { headers: { Accept: 'application/json' } })
        .then(function (res) { return res.ok ? res.json() : { items: [] }; })
        .then(function (data) { return Array.isArray(data.items) ? data.items : []; })
        .catch(function () { return []; });
    }
    return snapshotPromise;
  }

  /* ---------------------------------------------------------------- cards */
  function buildCard(item, options) {
    const opts = options || {};
    const card = el('article', 'news-card');
    card.setAttribute('data-testid', 'news-card');
    card.setAttribute('data-category', item.category);
    card.setAttribute('data-image-kind', item.image_kind || 'fallback');

    const link = el('a', 'news-card-link');
    link.href = detailHref(item);
    link.setAttribute('data-testid', 'news-card-link');

    if (opts.showImage !== false) {
      const wrap = el('div', 'img-wrap');
      const img = el('img');
      img.src = cardImage(item);
      img.alt = item.image_kind === 'cached'
        ? item.title
        : categoryLabel(item.category) + ' — NOVA Journal category cover';
      img.loading = opts.eager ? 'eager' : 'lazy';
      img.decoding = 'async';
      img.width = item.image_card_width || 1200;
      img.height = item.image_card_height || 750;
      img.addEventListener('error', function () {
        if (img.dataset.fallbackApplied) return;
        img.dataset.fallbackApplied = '1';
        img.src = fallbackCover(item.category, 'card');
        img.alt = categoryLabel(item.category) + ' — NOVA Journal category cover';
      }, { once: true });
      img.addEventListener('load', function () { wrap.classList.add('is-loaded'); }, { once: true });
      wrap.appendChild(img);
      link.appendChild(wrap);
    }

    const meta = el('div', 'news-meta');
    meta.appendChild(el('span', 'news-category', categoryLabel(item.category)));
    meta.appendChild(el('span', 'news-meta-sep', '·'));
    const time = el('time', 'date', formatDate(item.published_at));
    time.dateTime = item.published_at;
    meta.appendChild(time);
    link.appendChild(meta);

    link.appendChild(el('h3', 'title', item.title));
    link.appendChild(el('p', 'excerpt', item.summary));

    const foot = el('div', 'news-foot');
    foot.appendChild(el('span', 'news-source', 'Source · ' + item.source_name));
    foot.appendChild(el('span', 'news-more', 'Read more →'));
    link.appendChild(foot);

    card.appendChild(link);
    return card;
  }

  function renderState(container, message, testid) {
    container.textContent = '';
    const state = el('p', 'news-state', message);
    state.setAttribute('data-news-state', '');
    if (testid) state.setAttribute('data-testid', testid);
    container.appendChild(state);
  }

  function renderInto(grid, items, opts) {
    grid.textContent = '';
    items.forEach(function (item, i) {
      grid.appendChild(buildCard(item, { eager: !!(opts && opts.eager) && i < 3 }));
    });
  }

  /* ---------------------------------------------------------------- homepage */
  function initHome() {
    const grid = document.getElementById('newsHomeGrid');
    if (!grid) return;
    let requested = false;

    async function hydrate() {
      if (requested) return;
      requested = true;

      const cached = await snapshot();
      if (cached.length) {
        renderInto(grid, cached.slice(0, 6));
        grid.setAttribute('aria-busy', 'false');
      }

      try {
        const data = await timedRequest('/api/news/featured?limit=6');
        const items = (data.items || []).slice(0, 6);
        if (items.length) renderInto(grid, items);
      } catch (err) {
        if (!cached.length) {
          renderState(grid, 'The newsroom could not be updated at this time. Please try again shortly.',
            'news-home-empty');
        }
      } finally {
        grid.setAttribute('aria-busy', 'false');
      }
    }

    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) { io.disconnect(); hydrate(); }
        });
      }, { rootMargin: '600px 0px' });
      io.observe(grid);
    } else {
      hydrate();
    }
  }

  /* ---------------------------------------------------------------- newsroom */
  function initNewsroom() {
    const grid = document.getElementById('newsroomGrid');
    if (!grid) return;
    const filters = document.querySelectorAll('[data-news-filter]');
    const moreBtn = document.getElementById('newsroomMore');
    const searchInput = document.getElementById('newsroomSearch');
    const countLabel = document.getElementById('newsroomCount');
    const state = { category: '', search: '', page: 1 };
    let controller = null;
    let debounce = null;

    function syncFilterUI() {
      filters.forEach(function (btn) {
        const active = (btn.dataset.newsFilter || '') === state.category;
        btn.classList.toggle('is-active', active);
        btn.setAttribute('aria-pressed', active ? 'true' : 'false');
      });
    }

    function updateUrl() {
      const params = new URLSearchParams();
      if (state.category) params.set('category', state.category);
      if (state.search) params.set('search', state.search);
      const query = params.toString();
      history.replaceState({ category: state.category, search: state.search }, '',
        query ? '?' + query : location.pathname);
    }

    async function load(append) {
      if (controller) controller.abort();
      controller = new AbortController();
      const params = new URLSearchParams({ page: String(state.page), limit: '12' });
      if (state.category) params.set('category', state.category);
      if (state.search) params.set('search', state.search);
      if (!append) {
        grid.setAttribute('aria-busy', 'true');
        renderState(grid, 'Loading articles…', 'newsroom-loading');
      }
      const timer = setTimeout(function () { controller.abort(); }, 8000);
      try {
        const data = await request('/api/news?' + params.toString(), controller.signal);
        clearTimeout(timer);
        const items = data.items || [];
        if (!append) grid.textContent = '';
        if (!items.length && !append) {
          renderState(grid, 'No articles are currently available in this category.', 'newsroom-empty');
        }
        items.forEach(function (item, i) {
          grid.appendChild(buildCard(item, { eager: !append && state.page === 1 && i < 3 }));
        });
        if (countLabel && data.pagination) {
          countLabel.textContent = data.pagination.total +
            (data.pagination.total === 1 ? ' article' : ' articles');
        }
        if (moreBtn) moreBtn.hidden = !(data.pagination && data.pagination.has_more);
      } catch (err) {
        clearTimeout(timer);
        if (err.name === 'AbortError' || append) return;
        const cached = await snapshot();
        grid.textContent = '';
        if (cached.length) {
          cached.forEach(function (item) { grid.appendChild(buildCard(item)); });
          const note = el('p', 'news-state news-state--note',
            'The newsroom could not be updated at this time. Previously published items remain available.');
          note.setAttribute('data-testid', 'newsroom-fallback-note');
          grid.appendChild(note);
        } else {
          renderState(grid, 'The newsroom could not be updated at this time. Please try again shortly.',
            'newsroom-error');
        }
        if (moreBtn) moreBtn.hidden = true;
      } finally {
        grid.setAttribute('aria-busy', 'false');
      }
    }

    filters.forEach(function (btn) {
      btn.addEventListener('click', function () {
        state.category = btn.dataset.newsFilter || '';
        state.page = 1;
        syncFilterUI();
        updateUrl();
        load(false);
      });
    });

    if (searchInput) {
      searchInput.addEventListener('input', function () {
        clearTimeout(debounce);
        debounce = setTimeout(function () {
          state.search = searchInput.value.trim().slice(0, 80);
          state.page = 1;
          updateUrl();
          load(false);
        }, 350);
      });
    }

    if (moreBtn) {
      moreBtn.addEventListener('click', function () { state.page += 1; load(true); });
    }

    function readUrl() {
      const params = new URLSearchParams(location.search);
      const category = (params.get('category') || '').toUpperCase();
      state.category = CATEGORY_LABELS[category] ? category : '';
      state.search = (params.get('search') || '').slice(0, 80);
      state.page = 1;
      if (searchInput) searchInput.value = state.search;
    }

    window.addEventListener('popstate', function () {
      readUrl();
      syncFilterUI();
      load(false);
    });

    readUrl();
    syncFilterUI();
    load(false);
  }

  /* ---------------------------------------------------------------- detail */
  async function initDetail() {
    const root = document.getElementById('newsDetail');
    if (!root) return;
    const slug = (new URLSearchParams(location.search).get('slug') || '').trim();
    const article = document.getElementById('newsDetailArticle');
    const missing = document.getElementById('newsDetailMissing');
    const related = document.getElementById('newsDetailRelated');
    const relatedGrid = document.getElementById('newsDetailRelatedGrid');

    function showMissing(message) {
      if (article) article.hidden = true;
      if (related) related.hidden = true;
      if (missing) {
        missing.hidden = false;
        const text = missing.querySelector('[data-missing-text]');
        if (text && message) text.textContent = message;
      }
    }

    if (!/^[a-z0-9-]{3,120}$/.test(slug)) {
      showMissing('This article could not be found.');
      return;
    }

    let data;
    try {
      data = await request('/api/news/' + encodeURIComponent(slug));
    } catch (err) {
      showMissing(err.status === 404
        ? 'This article could not be found. It may have been archived.'
        : 'The newsroom is temporarily unavailable. Previously published items remain available in the newsroom.');
      return;
    }
    const item = data.item;
    if (!item) { showMissing('This article could not be found.'); return; }

    document.title = item.title + ' | NOVA Journal';
    const shortSummary = item.summary.length > 180 ? item.summary.slice(0, 177) + '…' : item.summary;
    const setMeta = function (selector, value) {
      const node = document.head.querySelector(selector);
      if (node) node.setAttribute('content', value);
    };
    setMeta('meta[name="description"]', shortSummary);
    setMeta('meta[property="og:title"]', item.title + ' | NOVA Journal');
    setMeta('meta[property="og:description"]', shortSummary);
    setMeta('meta[property="og:image"]', location.origin + '/' + detailImage(item));
    const canonical = document.head.querySelector('link[rel="canonical"]');
    if (canonical) {
      canonical.href = location.origin + location.pathname + '?slug=' + encodeURIComponent(item.slug);
    }

    document.getElementById('detailCategory').textContent = categoryLabel(item.category);
    const time = document.getElementById('detailDate');
    time.textContent = formatDate(item.published_at);
    time.dateTime = item.published_at;
    document.getElementById('detailTitle').textContent = item.title;
    document.getElementById('detailSource').textContent = 'Source · ' + item.source_name.toUpperCase();

    const originalTitle = document.getElementById('detailOriginalTitle');
    if (item.original_title && item.original_title !== item.title) {
      originalTitle.textContent = 'Original headline: ' + item.original_title;
      originalTitle.hidden = false;
    }

    const figure = document.getElementById('detailFigure');
    const img = figure.querySelector('img');
    img.src = detailImage(item);
    img.width = item.image_detail_width || 1600;
    img.height = item.image_detail_height || 900;
    img.alt = item.image_kind === 'cached'
      ? item.title
      : categoryLabel(item.category) + ' — NOVA Journal category cover';
    img.addEventListener('error', function () {
      if (img.dataset.fallbackApplied) return;
      img.dataset.fallbackApplied = '1';
      img.src = fallbackCover(item.category, 'detail');
      img.alt = categoryLabel(item.category) + ' — NOVA Journal category cover';
    }, { once: true });
    figure.classList.toggle('nd-figure--fallback', item.image_kind !== 'cached');
    figure.querySelector('figcaption').textContent = item.image_kind === 'cached'
      ? 'Image: ' + (item.image_credit || item.source_name)
      : 'NOVA Journal category cover — not a photograph of the reported event.';
    figure.hidden = false;

    const summaryHost = document.getElementById('detailSummary');
    summaryHost.textContent = '';
    const sentences = item.summary.split(/(?<=[.!?])\s+/);
    const chunks = [];
    const perChunk = sentences.length > 4 ? Math.ceil(sentences.length / 2) : sentences.length;
    for (let i = 0; i < sentences.length; i += perChunk) {
      chunks.push(sentences.slice(i, i + perChunk).join(' '));
    }
    chunks.forEach(function (chunk) {
      if (chunk.trim()) summaryHost.appendChild(el('p', 'nd-paragraph', chunk.trim()));
    });

    if (item.category === 'TECHNICAL_AND_LEGAL') {
      document.getElementById('detailDisclaimer').hidden = false;
    }

    const cta = document.getElementById('detailSourceCta');
    const external = safeExternal(item.canonical_url || item.source_url);
    if (external) {
      cta.href = external;
      cta.setAttribute('aria-label', 'Read the original article at ' + item.source_name + ' (opens in a new tab)');
      const label = cta.parentNode.querySelector('[data-cta-source]');
      if (label) label.textContent = item.source_name;
    } else {
      cta.hidden = true;
    }

    const structured = document.getElementById('detailStructuredData');
    if (structured) {
      structured.textContent = JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'WebPage',
        name: item.title,
        description: shortSummary,
        isBasedOn: external || undefined,
        breadcrumb: {
          '@type': 'BreadcrumbList',
          itemListElement: [
            { '@type': 'ListItem', position: 1, name: 'Home', item: 'index.html' },
            { '@type': 'ListItem', position: 2, name: 'NOVA Journal', item: 'newsroom.html' },
            { '@type': 'ListItem', position: 3, name: item.title }
          ]
        }
      });
    }

    article.hidden = false;
    const relatedItems = (data.related || [])
      .filter(function (r) { return r.slug !== item.slug; })
      .slice(0, 3);
    if (relatedItems.length && relatedGrid) {
      relatedItems.forEach(function (r) { relatedGrid.appendChild(buildCard(r)); });
      related.hidden = false;
    }
  }

  initHome();
  initNewsroom();
  initDetail();
})();
