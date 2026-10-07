/* ==========================================================
   NOVA JOURNAL — homepage strip, newsroom index, detail page.
   Fully static: the browser reads the pre-generated JSON feeds
   committed to the nova-news-feed repository by GitHub Actions.
   No backend, no API key, no server process.
   Nodes are built with createElement/textContent only.
   ========================================================== */
(function () {
  'use strict';

  const NEWS_FEEDS = {
    tr: 'https://raw.githubusercontent.com/kaankara34/nova-news-feed/main/data/news-tr.json',
    en: 'https://raw.githubusercontent.com/kaankara34/nova-news-feed/main/data/news-en.json'
  };
  const CACHE_PREFIX = 'nova-news-feed:';
  const CACHE_TTL = 30 * 60 * 1000;
  const REQUEST_TIMEOUT = 8000;

  const CATEGORY_LABELS = {
    ART: 'Art & Exhibitions',
    EXHIBITIONS: 'Exhibitions',
    GALLERIES_AND_MUSEUMS: 'Galleries & Museums',
    ARCHITECTURE_AND_DESIGN: 'Architecture & Design',
    CONSTRUCTION: 'Construction',
    URBAN_TRANSFORMATION: 'Urban Transformation',
    KADIKOY: 'Kadıköy',
    TECHNICAL_AND_LEGAL: 'Technical & Legal',
    FASHION_AND_LUXURY: 'Fashion & Luxury'
  };
  const CATEGORY_LABELS_TR = {
    ART: 'Sanat ve Sergiler',
    EXHIBITIONS: 'Sergiler',
    GALLERIES_AND_MUSEUMS: 'Galeriler ve Müzeler',
    ARCHITECTURE_AND_DESIGN: 'Mimarlık ve Tasarım',
    CONSTRUCTION: 'İnşaat',
    URBAN_TRANSFORMATION: 'Kentsel Dönüşüm',
    KADIKOY: 'Kadıköy',
    TECHNICAL_AND_LEGAL: 'Teknik ve Hukuki',
    FASHION_AND_LUXURY: 'Moda ve Lüks'
  };
  const FALLBACK_SLUGS = {
    ART: 'art',
    EXHIBITIONS: 'exhibitions',
    GALLERIES_AND_MUSEUMS: 'galleries-and-museums',
    ARCHITECTURE_AND_DESIGN: 'architecture-and-design',
    CONSTRUCTION: 'construction',
    URBAN_TRANSFORMATION: 'urban-transformation',
    KADIKOY: 'kadikoy',
    TECHNICAL_AND_LEGAL: 'technical-and-legal',
    FASHION_AND_LUXURY: 'architecture-and-design'
  };
  const MESSAGES = {
    en: {
      unavailable: 'News is temporarily unavailable.',
      empty: 'No articles are currently available in this category.',
      loading: 'Loading articles…',
      missing: 'This article could not be found.',
      source: 'Source · ',
      originalHeadline: 'Original headline: ',
      imageCredit: 'Image: ',
      fallbackCaption: 'NOVA Journal category cover — not a photograph of the reported event.',
      regionTr: 'Türkiye',
      regionIntl: 'International',
      coverAlt: ' — NOVA Journal category cover'
    },
    tr: {
      unavailable: 'Haberler geçici olarak kullanılamıyor.',
      empty: 'Bu kategoride şu anda görüntülenecek haber bulunmuyor.',
      loading: 'Haberler yükleniyor…',
      missing: 'Bu haber bulunamadı.',
      source: 'Kaynak · ',
      originalHeadline: 'Özgün başlık: ',
      imageCredit: 'Görsel: ',
      fallbackCaption: 'NOVA Journal kategori görseli — haberde aktarılan olayın fotoğrafı değildir.',
      regionTr: 'Türkiye',
      regionIntl: 'Uluslararası',
      coverAlt: ' — NOVA Journal kategori görseli'
    }
  };

  /* ---------------------------------------------------------------- language */
  function currentLanguage() {
    const raw = document.documentElement.getAttribute('lang') ||
      document.body.dataset.lang || 'en';
    return String(raw).toLowerCase().indexOf('tr') === 0 ? 'tr' : 'en';
  }
  const LANG = currentLanguage();
  const T = MESSAGES[LANG] || MESSAGES.en;

  /* ---------------------------------------------------------------- helpers */
  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  function normaliseCategory(value) {
    const raw = String(value || '').trim();
    if (!raw) return 'ART';
    const key = raw.toUpperCase().replace(/&/g, 'AND').replace(/[^A-Z0-9]+/g, '_')
      .replace(/^_|_$/g, '');
    if (CATEGORY_LABELS[key]) return key;
    const flat = function (s) { return String(s).toLowerCase().replace(/[^a-z0-9ıçğöşü]+/g, ''); };
    const target = flat(raw);
    const match = Object.keys(CATEGORY_LABELS).filter(function (candidate) {
      return flat(CATEGORY_LABELS[candidate]) === target;
    })[0];
    if (match) return match;
    if (key === 'ART_AND_EXHIBITIONS') return 'ART';
    return 'ART';
  }

  const DISPLAY_LABELS = LANG === 'tr' ? CATEGORY_LABELS_TR : CATEGORY_LABELS;
  const categoryLabel = function (key) { return DISPLAY_LABELS[key] || 'Journal'; };

  function formatDate(value) {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return '';
    return date.toLocaleDateString(LANG === 'tr' ? 'tr-TR' : 'en-GB',
      { day: 'numeric', month: 'short', year: 'numeric' });
  }

  const safeExternal = function (url) { return /^https:\/\//i.test(url || '') ? url : ''; };
  const PAGES = LANG === 'tr'
    ? { home: '/tr/index.html', journal: '/tr/medya.html', detail: '/tr/haber.html' }
    : { home: '/en/index.html', journal: '/en/newsroom.html', detail: '/en/news-detail.html' };
  const detailHref = function (item) { return PAGES.detail + '?id=' + encodeURIComponent(item.id); };

  function fallbackCover(category, variant) {
    return '/media/news/fallback/' + (FALLBACK_SLUGS[category] || 'art') + '-' + variant + '.webp';
  }

  function remoteImage(item) {
    const url = String(item.image || '').trim();
    return /^https?:\/\//i.test(url) ? url : '';
  }

  /* ---------------------------------------------------------------- normalise */
  function normaliseArticle(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const id = String(raw.id || '').trim();
    const title = String(raw.title || raw.originalTitle || '').trim();
    if (!id || !title) return null;
    const category = normaliseCategory(raw.category);
    return {
      id: id,
      category: category,
      categoryLabel: categoryLabel(category),
      title: title,
      originalTitle: String(raw.originalTitle || '').trim(),
      excerpt: String(raw.excerpt || '').trim(),
      content: String(raw.content || '').trim(),
      source: String(raw.source || '').trim(),
      sourceDomain: String(raw.sourceDomain || '').trim(),
      publishedAt: String(raw.publishedAt || '').trim(),
      url: safeExternal(raw.url),
      image: remoteImage(raw),
      contentMode: String(raw.contentMode || '').trim(),
      editorialScore: raw.editorialScore,
      technicalValue: raw.technicalValue,
      brandFit: raw.brandFit
    };
  }

  function normaliseFeed(payload) {
    if (!payload || !Array.isArray(payload.articles)) return null;
    const articles = payload.articles.map(normaliseArticle).filter(Boolean);
    if (!articles.length) return null;
    articles.sort(function (a, b) {
      return new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime();
    });
    return { generatedAt: payload.generatedAt || '', articles: articles };
  }

  /* ---------------------------------------------------------------- transport */
  function readCache(language) {
    try {
      const raw = window.localStorage.getItem(CACHE_PREFIX + language);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      const feed = normaliseFeed(parsed && parsed.feed);
      if (!feed) return null;
      return { feed: feed, savedAt: Number(parsed.savedAt) || 0 };
    } catch (err) {
      return null;
    }
  }

  function writeCache(language, payload) {
    try {
      window.localStorage.setItem(CACHE_PREFIX + language,
        JSON.stringify({ savedAt: Date.now(), feed: payload }));
    } catch (err) { /* storage unavailable or full — cache is optional */ }
  }

  let networkPromise = null;
  function fetchFeed(language) {
    if (networkPromise) return networkPromise;
    const controller = new AbortController();
    const timer = setTimeout(function () { controller.abort(); }, REQUEST_TIMEOUT);
    networkPromise = fetch(NEWS_FEEDS[language] || NEWS_FEEDS.en, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal: controller.signal
    }).then(function (response) {
      if (!response.ok) throw new Error('News feed request failed with status ' + response.status);
      return response.json();
    }).then(function (payload) {
      const feed = normaliseFeed(payload);
      if (!feed) throw new Error('Invalid news feed structure');
      writeCache(language, payload);
      return feed;
    }).finally(function () {
      clearTimeout(timer);
      networkPromise = null;
    });
    return networkPromise;
  }

  /* Resolve the feed for the current language.
     onData may be called twice: once from a valid cache, once after refresh.
     The third argument tells the consumer whether a refresh is still pending. */
  function loadFeed(onData, onError) {
    const cached = readCache(LANG);
    const refreshing = !cached || (Date.now() - cached.savedAt >= CACHE_TTL);
    let served = false;
    if (cached) {
      served = true;
      onData(cached.feed, true, refreshing);
      if (!refreshing) return;
    }
    fetchFeed(LANG).then(function (feed) {
      onData(feed, false, false);
    }).catch(function () {
      if (!served && onError) onError();
    });
  }

  /* ---------------------------------------------------------------- cards */
  function attachImage(link, item, variant, eager) {
    const wrap = el('div', 'img-wrap');
    const img = el('img');
    const remote = item.image;
    const local = fallbackCover(item.category, variant);
    img.src = remote || local;
    img.alt = remote ? item.title : item.categoryLabel + T.coverAlt;
    img.loading = eager ? 'eager' : 'lazy';
    img.decoding = 'async';
    img.width = variant === 'detail' ? 1600 : 1200;
    img.height = variant === 'detail' ? 900 : 750;
    img.addEventListener('error', function () {
      if (img.dataset.fallbackApplied) return;
      img.dataset.fallbackApplied = '1';
      img.src = local;
      img.alt = item.categoryLabel + T.coverAlt;
    }, { once: true });
    img.addEventListener('load', function () { wrap.classList.add('is-loaded'); }, { once: true });
    wrap.appendChild(img);
    link.appendChild(wrap);
    return img;
  }

  function buildCard(item, options) {
    const opts = options || {};
    const card = el('article', 'news-card');
    card.setAttribute('data-testid', 'news-card');
    card.setAttribute('data-category', item.category);
    card.setAttribute('data-image-kind', item.image ? 'remote' : 'fallback');

    const link = el('a', 'news-card-link');
    link.href = detailHref(item);
    link.setAttribute('data-testid', 'news-card-link');

    if (opts.showImage !== false) attachImage(link, item, 'card', !!opts.eager);

    const meta = el('div', 'news-meta');
    meta.appendChild(el('span', 'news-category', item.categoryLabel));
    meta.appendChild(el('span', 'news-meta-sep', '·'));
    const time = el('time', 'date', formatDate(item.publishedAt));
    time.dateTime = item.publishedAt;
    meta.appendChild(time);
    link.appendChild(meta);

    link.appendChild(el('h3', 'title', item.title));
    link.appendChild(el('p', 'excerpt', item.excerpt));

    const foot = el('div', 'news-foot');
    foot.appendChild(el('span', 'news-source', 'Source · ' + (item.source || item.sourceDomain)));
    foot.appendChild(el('span', 'news-more', LANG === 'tr' ? 'Devamını oku →' : 'Read more →'));
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

  /* ---------------------------------------------------------------- homepage */
  function initHome() {
    const grid = document.getElementById('newsHomeGrid');
    if (!grid) return;
    let requested = false;

    function render(feed) {
      grid.textContent = '';
      feed.articles.slice(0, 6).forEach(function (item, i) {
        grid.appendChild(buildCard(item, { eager: i < 3 }));
      });
      grid.setAttribute('aria-busy', 'false');
    }

    function hydrate() {
      if (requested) return;
      requested = true;
      loadFeed(render, function () {
        renderState(grid, T.unavailable, 'news-home-empty');
        grid.setAttribute('aria-busy', 'false');
      });
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
    const PAGE_SIZE = 12;
    const state = { category: '', search: '', page: 1 };
    let articles = [];
    let loaded = false;
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

    function matches(item) {
      if (state.category && item.category !== state.category) return false;
      if (!state.search) return true;
      const needle = state.search.toLowerCase();
      return (item.title + ' ' + item.excerpt + ' ' + item.source).toLowerCase()
        .indexOf(needle) !== -1;
    }

    function render() {
      if (!loaded) return;
      const visible = articles.filter(matches);
      const shown = visible.slice(0, state.page * PAGE_SIZE);
      grid.textContent = '';
      if (!shown.length) {
        renderState(grid, T.empty, 'newsroom-empty');
      } else {
        shown.forEach(function (item, i) {
          grid.appendChild(buildCard(item, { eager: i < 3 }));
        });
      }
      if (countLabel) {
        countLabel.textContent = LANG === 'tr'
          ? visible.length + ' haber'
          : visible.length + (visible.length === 1 ? ' article' : ' articles');
      }
      if (moreBtn) moreBtn.hidden = shown.length >= visible.length;
      grid.setAttribute('aria-busy', 'false');
    }

    filters.forEach(function (btn) {
      btn.addEventListener('click', function () {
        state.category = btn.dataset.newsFilter || '';
        state.page = 1;
        syncFilterUI();
        updateUrl();
        render();
      });
    });

    if (searchInput) {
      searchInput.addEventListener('input', function () {
        clearTimeout(debounce);
        debounce = setTimeout(function () {
          state.search = searchInput.value.trim().slice(0, 80);
          state.page = 1;
          updateUrl();
          render();
        }, 250);
      });
    }

    if (moreBtn) {
      moreBtn.addEventListener('click', function () { state.page += 1; render(); });
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
      render();
    });

    readUrl();
    syncFilterUI();
    renderState(grid, T.loading, 'newsroom-loading');

    loadFeed(function (feed) {
      articles = feed.articles;
      loaded = true;
      render();
    }, function () {
      renderState(grid, T.unavailable, 'newsroom-error');
      grid.setAttribute('aria-busy', 'false');
      if (moreBtn) moreBtn.hidden = true;
    });
  }

  /* ---------------------------------------------------------------- detail */
  function initDetail() {
    const root = document.getElementById('newsDetail');
    if (!root) return;
    const params = new URLSearchParams(location.search);
    const wanted = (params.get('id') || params.get('slug') || '').trim();
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

    if (!/^[A-Za-z0-9._-]{3,160}$/.test(wanted)) {
      showMissing(T.missing);
      return;
    }

    function setText(id, value) {
      const node = document.getElementById(id);
      if (node) node.textContent = value;
    }

    function paragraphs(text) {
      const blocks = String(text || '')
        .split(/\n{2,}|\r\n\r\n/)
        .map(function (block) { return block.replace(/\s+/g, ' ').trim(); })
        .filter(Boolean);
      if (blocks.length > 1) return blocks;
      const single = blocks[0] || '';
      if (single.length < 420) return blocks;
      const sentences = single.split(/(?<=[.!?])\s+/);
      const grouped = [];
      let buffer = [];
      sentences.forEach(function (sentence, index) {
        buffer.push(sentence);
        if (buffer.length === 3 || index === sentences.length - 1) {
          const paragraph = buffer.join(' ').trim();
          if (paragraph) grouped.push(paragraph);
          buffer = [];
        }
      });
      return grouped;
    }

    function render(feed) {
      const item = feed.articles.filter(function (a) { return a.id === wanted; })[0];
      if (!item) { showMissing(T.missing); return; }

      document.title = item.title + ' | NOVA Journal';
      const summary = item.excerpt.length > 180 ? item.excerpt.slice(0, 177) + '…' : item.excerpt;
      const setMeta = function (selector, value) {
        const node = document.head.querySelector(selector);
        if (node) node.setAttribute('content', value);
      };
      setMeta('meta[name="description"]', summary);
      setMeta('meta[property="og:title"]', item.title + ' | NOVA Journal');
      setMeta('meta[property="og:description"]', summary);
      const canonical = document.head.querySelector('link[rel="canonical"]');
      if (canonical) {
        canonical.href = location.origin + location.pathname + '?id=' + encodeURIComponent(item.id);
      }

      setText('detailCategory', item.categoryLabel);
      const time = document.getElementById('detailDate');
      if (time) {
        time.textContent = formatDate(item.publishedAt);
        time.dateTime = item.publishedAt;
      }
      setText('detailTitle', item.title);
      setText('detailSource', T.source + (item.source || item.sourceDomain).toUpperCase());

      const originalTitle = document.getElementById('detailOriginalTitle');
      if (originalTitle && item.originalTitle && item.originalTitle !== item.title) {
        originalTitle.textContent = T.originalHeadline + item.originalTitle;
        originalTitle.hidden = false;
      }

      const figure = document.getElementById('detailFigure');
      if (figure) {
        const placeholder = figure.querySelector('img');
        if (placeholder) placeholder.remove();
        const host = el('div');
        attachImage(host, item, 'detail', true);
        const wrap = host.firstChild;
        const img = wrap.querySelector('img');
        figure.insertBefore(img, figure.firstChild);
        figure.classList.toggle('nd-figure--fallback', !item.image);
        const caption = figure.querySelector('figcaption');
        if (caption) {
          caption.textContent = item.image
            ? T.imageCredit + (item.source || item.sourceDomain)
            : T.fallbackCaption;
        }
        figure.hidden = false;
      }

      const standfirstHost = document.getElementById('detailStandfirst');
      const bodyHost = document.getElementById('detailBody');
      const blocks = paragraphs(item.content);
      if (standfirstHost) {
        standfirstHost.textContent = item.excerpt;
        standfirstHost.hidden = !item.excerpt;
      }
      if (bodyHost) {
        bodyHost.textContent = '';
        (blocks.length ? blocks : [item.excerpt]).forEach(function (text) {
          if (text) bodyHost.appendChild(el('p', 'nd-paragraph', text));
        });
      }

      setText('factPublisher', item.source || item.sourceDomain);
      setText('factPublished', formatDate(item.publishedAt));
      setText('factCategory', item.categoryLabel);
      const region = /\.tr$|^(t24|ntv|haberturk|hurriyet|milliyet|sozcu)\./i.test(item.sourceDomain)
        ? T.regionTr : T.regionIntl;
      setText('factRegion', region);

      if (item.category === 'TECHNICAL_AND_LEGAL') {
        const disclaimer = document.getElementById('detailDisclaimer');
        if (disclaimer) disclaimer.hidden = false;
      }

      const cta = document.getElementById('detailSourceCta');
      if (cta) {
        if (item.url) {
          cta.href = item.url;
          cta.target = '_blank';
          cta.rel = 'noopener noreferrer';
          cta.setAttribute('aria-label',
            'Read the original article at ' + (item.source || item.sourceDomain) + ' (opens in a new tab)');
          const label = cta.parentNode.querySelector('[data-cta-source]');
          if (label) label.textContent = item.source || item.sourceDomain;
        } else {
          cta.hidden = true;
        }
      }

      const structured = document.getElementById('detailStructuredData');
      if (structured) {
        structured.textContent = JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'WebPage',
          name: item.title,
          description: summary,
          isBasedOn: item.url || undefined,
          breadcrumb: {
            '@type': 'BreadcrumbList',
            itemListElement: [
              { '@type': 'ListItem', position: 1, name: 'Home', item: PAGES.home },
              { '@type': 'ListItem', position: 2, name: 'NOVA Journal', item: PAGES.journal },
              { '@type': 'ListItem', position: 3, name: item.title }
            ]
          }
        });
      }

      if (article) article.hidden = false;

      if (relatedGrid && related) {
        relatedGrid.textContent = '';
        const relatedItems = feed.articles.filter(function (a) {
          return a.id !== item.id && a.category === item.category;
        }).slice(0, 3);
        const fill = relatedItems.length
          ? relatedItems
          : feed.articles.filter(function (a) { return a.id !== item.id; }).slice(0, 3);
        if (fill.length) {
          fill.forEach(function (r) { relatedGrid.appendChild(buildCard(r)); });
          related.hidden = false;
        }
      }
    }

    loadFeed(function (feed, fromCache, refreshing) {
      const found = feed.articles.some(function (a) { return a.id === wanted; });
      if (fromCache && refreshing && !found) return;
      render(feed);
    }, function () {
      showMissing(T.unavailable);
    });
  }

  initHome();
  initNewsroom();
  initDetail();
})();
