/* ==========================================================
   NOVA JOURNAL — homepage strip, newsroom index, detail page.
   All data comes from the NOVA backend (/api/news*). No feed is
   ever fetched from the browser. Nodes are built with
   createElement/textContent, never innerHTML.
   ========================================================== */
(function () {
  'use strict';

  const API = document.body.dataset.api || '';
  const FALLBACK_URL = 'data/news-fallback.json';
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
  const LEGAL_CATEGORIES = ['TECHNICAL_AND_LEGAL'];

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

  function categoryLabel(key) {
    return CATEGORY_LABELS[key] || 'Journal';
  }

  function detailHref(item) {
    return 'news-detail.html?slug=' + encodeURIComponent(item.slug);
  }

  function safeExternal(url) {
    return /^https:\/\//i.test(url || '') ? url : '';
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

  async function fallbackItems() {
    try {
      const res = await fetch(FALLBACK_URL, { headers: { Accept: 'application/json' } });
      if (!res.ok) return [];
      const data = await res.json();
      return Array.isArray(data.items) ? data.items : [];
    } catch (err) {
      return [];
    }
  }

  /* ---------------------------------------------------------------- cards */
  function buildCard(item, options) {
    const opts = options || {};
    const card = el('article', 'news-card' + (opts.lead ? ' news-card--lead' : ''));
    card.setAttribute('data-testid', 'news-card');
    card.setAttribute('data-category', item.category);

    const link = el('a', 'news-card-link');
    link.href = detailHref(item);
    link.setAttribute('data-testid', 'news-card-link');

    const image = safeExternal(item.image_url);
    if (image && opts.allowImage !== false) {
      const wrap = el('div', 'img-wrap');
      const img = el('img');
      img.src = image;
      img.alt = item.title;
      img.loading = 'lazy';
      img.decoding = 'async';
      img.width = 800;
      img.height = 500;
      img.addEventListener('error', function () { wrap.remove(); card.classList.add('news-card--text'); }, { once: true });
      wrap.appendChild(img);
      link.appendChild(wrap);
    } else {
      card.classList.add('news-card--text');
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
    link.appendChild(el('span', 'news-source', 'Source · ' + item.source_name));
    card.appendChild(link);

    const external = safeExternal(item.canonical_url || item.source_url);
    if (external) {
      const source = el('a', 'news-source-link', 'Read at source →');
      source.href = external;
      source.target = '_blank';
      source.rel = 'noopener noreferrer';
      source.setAttribute('aria-label', 'Read the original article at ' + item.source_name + ' (opens in a new tab)');
      source.setAttribute('data-testid', 'news-source-link');
      card.appendChild(source);
    }
    return card;
  }

  function renderState(container, message, testid) {
    container.textContent = '';
    const state = el('p', 'news-state', message);
    state.setAttribute('data-news-state', '');
    if (testid) state.setAttribute('data-testid', testid);
    container.appendChild(state);
  }

  /* ---------------------------------------------------------------- homepage */
  async function initHome() {
    const grid = document.getElementById('newsHomeGrid');
    if (!grid) return;
    let items = [];
    let stale = false;
    try {
      const data = await request('/api/news/featured?limit=6');
      items = data.items || [];
    } catch (err) {
      items = await fallbackItems();
      stale = true;
    }
    grid.setAttribute('aria-busy', 'false');
    if (!items.length) {
      renderState(grid, 'No articles are currently available.', 'news-home-empty');
      return;
    }
    grid.textContent = '';
    items.slice(0, 6).forEach(function (item) { grid.appendChild(buildCard(item)); });
    if (stale) {
      const note = el('p', 'news-state news-state--note',
        'The newsroom could not be updated at this time. Previously published items remain available.');
      note.setAttribute('data-testid', 'news-home-fallback-note');
      grid.appendChild(note);
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
    const state = { category: '', search: '', page: 1, pages: 0 };
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
      const timer = setTimeout(function () { controller.abort(); }, 12000);
      try {
        const data = await request('/api/news?' + params.toString(), controller.signal);
        clearTimeout(timer);
        const items = data.items || [];
        state.pages = (data.pagination && data.pagination.pages) || 0;
        if (!append) grid.textContent = '';
        if (!items.length && !append) {
          renderState(grid, 'No articles are currently available in this category.', 'newsroom-empty');
        }
        items.forEach(function (item, index) {
          grid.appendChild(buildCard(item, { lead: !append && state.page === 1 && index === 0 }));
        });
        if (countLabel && data.pagination) {
          countLabel.textContent = data.pagination.total + (data.pagination.total === 1 ? ' article' : ' articles');
        }
        if (moreBtn) {
          const hasMore = !!(data.pagination && data.pagination.has_more);
          moreBtn.hidden = !hasMore;
        }
      } catch (err) {
        clearTimeout(timer);
        if (err.name === 'AbortError') return;
        if (!append) {
          const items = await fallbackItems();
          grid.textContent = '';
          if (items.length) {
            items.forEach(function (item) { grid.appendChild(buildCard(item)); });
            const note = el('p', 'news-state news-state--note',
              'The newsroom could not be updated at this time. Previously published items remain available.');
            note.setAttribute('data-testid', 'newsroom-fallback-note');
            grid.appendChild(note);
          } else {
            renderState(grid, 'The newsroom could not be updated at this time. Please try again shortly.',
              'newsroom-error');
          }
          if (moreBtn) moreBtn.hidden = true;
        }
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
      moreBtn.addEventListener('click', function () {
        state.page += 1;
        load(true);
      });
    }

    window.addEventListener('popstate', function () {
      readUrl();
      syncFilterUI();
      load(false);
    });

    function readUrl() {
      const params = new URLSearchParams(location.search);
      const category = (params.get('category') || '').toUpperCase();
      state.category = CATEGORY_LABELS[category] ? category : '';
      state.search = (params.get('search') || '').slice(0, 80);
      state.page = 1;
      if (searchInput) searchInput.value = state.search;
    }

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
    if (!item) {
      showMissing('This article could not be found.');
      return;
    }

    document.title = item.title + ' | NOVA Journal';
    const setMeta = function (selector, value) {
      const node = document.head.querySelector(selector);
      if (node) node.setAttribute('content', value);
    };
    const shortSummary = item.summary.length > 180 ? item.summary.slice(0, 177) + '…' : item.summary;
    setMeta('meta[name="description"]', shortSummary);
    setMeta('meta[property="og:title"]', item.title + ' | NOVA Journal');
    setMeta('meta[property="og:description"]', shortSummary);
    const canonical = document.head.querySelector('link[rel="canonical"]');
    if (canonical) canonical.href = location.origin + location.pathname + '?slug=' + encodeURIComponent(item.slug);

    document.getElementById('detailCategory').textContent = categoryLabel(item.category);
    const time = document.getElementById('detailDate');
    time.textContent = formatDate(item.published_at);
    time.dateTime = item.published_at;
    document.getElementById('detailTitle').textContent = item.title;
    document.getElementById('detailSource').textContent = 'Source · ' + item.source_name.toUpperCase();
    document.getElementById('detailSummary').textContent = item.summary;

    const originalTitle = document.getElementById('detailOriginalTitle');
    if (item.original_title && item.original_title !== item.title) {
      originalTitle.textContent = 'Original headline: ' + item.original_title;
      originalTitle.hidden = false;
    }

    const image = safeExternal(item.image_url);
    const figure = document.getElementById('detailFigure');
    if (image) {
      const img = figure.querySelector('img');
      img.src = image;
      img.alt = item.title;
      img.addEventListener('error', function () { figure.hidden = true; }, { once: true });
      const credit = figure.querySelector('figcaption');
      credit.textContent = item.image_credit ? 'Image: ' + item.image_credit : 'Image: ' + item.source_name;
      figure.hidden = false;
    }

    const disclaimer = document.getElementById('detailDisclaimer');
    if (LEGAL_CATEGORIES.indexOf(item.category) !== -1) disclaimer.hidden = false;

    const cta = document.getElementById('detailSourceCta');
    const external = safeExternal(item.canonical_url || item.source_url);
    if (external) {
      cta.href = external;
      cta.setAttribute('aria-label', 'Read the original article at ' + item.source_name + ' (opens in a new tab)');
      const label = cta.querySelector('[data-cta-source]');
      if (label) label.textContent = item.source_name;
    } else {
      cta.hidden = true;
    }

    const breadcrumbScript = document.getElementById('detailStructuredData');
    if (breadcrumbScript) {
      breadcrumbScript.textContent = JSON.stringify({
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
    const relatedItems = (data.related || []).filter(function (r) { return r.slug !== item.slug; }).slice(0, 3);
    if (relatedItems.length && relatedGrid) {
      relatedItems.forEach(function (r) { relatedGrid.appendChild(buildCard(r, { allowImage: false })); });
      related.hidden = false;
    }
  }

  initHome();
  initNewsroom();
  initDetail();
})();
