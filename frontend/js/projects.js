/* Projects page — Filter + Form */
(function () {
  'use strict';

  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));

  const filterType = $('#filterType');
  const filterLoc = $('#filterLocation');
  const grid = $('#projectsGrid');
  const empty = $('#pjEmpty');
  const reset = $('#pjReset');

  function applyFilters() {
    if (!grid) return;
    const t = filterType ? filterType.value : 'all';
    const l = filterLoc ? filterLoc.value : 'all';
    let visible = 0;
    $$('.pj-card', grid).forEach(card => {
      const types = (card.dataset.type || '').split(/\s+/);
      const locs = (card.dataset.location || '').split(/\s+/);
      const matchT = t === 'all' || types.includes(t);
      const matchL = l === 'all' || locs.includes(l);
      const show = matchT && matchL;
      card.classList.toggle('hidden', !show);
      if (show) visible++;
    });
    if (empty) empty.hidden = visible > 0;
  }

  if (filterType) filterType.addEventListener('change', applyFilters);
  if (filterLoc) filterLoc.addEventListener('change', applyFilters);
  if (reset) reset.addEventListener('click', () => {
    if (filterType) filterType.value = 'all';
    if (filterLoc) filterLoc.value = 'all';
    applyFilters();
  });

  /* Form submit (UI-only) */
  const form = $('#pjForm');
  if (form) {
    form.addEventListener('submit', e => {
      e.preventDefault();
      const fullname = form.querySelector('[name="fullname"]').value.trim();
      const email = form.querySelector('[name="email"]').value.trim();
      const privacy = form.querySelector('[name="privacy"]').checked;
      if (!fullname || !email || !privacy) {
        alert('Please complete required fields and accept the privacy policy.');
        return;
      }
      alert('Thank you. Your registration has been received.');
      form.reset();
    });
  }

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
