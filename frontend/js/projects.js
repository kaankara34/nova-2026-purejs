/* Projects page — Filter + Form */
(function () {
  'use strict';

  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));

  const pills = $$('.pj-pill');
  const grid = $('#projectsGrid');
  const empty = $('#pjEmpty');
  const reset = $('#pjReset');
  let currentKind = 'all';
  let currentValue = 'all';

  function matches(card) {
    if (currentKind === 'all') return true;
    if (currentKind === 'type') return card.dataset.projectType === currentValue;
    return card.dataset.projectStatus === currentValue;
  }

  function applyFilters() {
    if (!grid) return;
    let visible = 0;
    $$('.pj-card', grid).forEach(card => {
      const show = matches(card);
      card.classList.toggle('hidden', !show);
      if (show) visible++;
    });
    if (empty) empty.hidden = visible > 0;
  }

  function activate(pill) {
    pills.forEach(p => {
      const on = p === pill;
      p.classList.toggle('is-active', on);
      p.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    currentKind = pill.dataset.filterKind;
    currentValue = pill.dataset.filterValue;
    applyFilters();
  }

  pills.forEach(pill => pill.addEventListener('click', () => activate(pill)));

  if (reset) reset.addEventListener('click', () => {
    const all = pills.find(p => p.dataset.filterKind === 'all');
    if (all) activate(all);
  });

  applyFilters();

  /* Smooth scroll for [data-scroll] buttons */
  $$('[data-scroll]').forEach(btn => {
    btn.addEventListener('click', e => {
      const target = btn.dataset.scroll;
      const el = document.getElementById(target);
      if (el) {
        e.preventDefault();
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
})();
