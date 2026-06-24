/* Projects page — Filter + Form */
(function () {
  'use strict';

  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));

  const pills = $$('.pj-pill');
  const grid = $('#projectsGrid');
  const empty = $('#pjEmpty');
  const reset = $('#pjReset');
  let currentFilter = 'all';

  function applyFilters() {
    if (!grid) return;
    let visible = 0;
    $$('.pj-card', grid).forEach(card => {
      const filters = (card.dataset.filter || '').split(/\s+/);
      const show = currentFilter === 'all' || filters.includes(currentFilter);
      card.classList.toggle('hidden', !show);
      if (show) visible++;
    });
    if (empty) empty.hidden = visible > 0;
  }

  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('is-active'));
      pill.classList.add('is-active');
      currentFilter = pill.dataset.filter;
      applyFilters();
    });
  });

  if (reset) reset.addEventListener('click', () => {
    pills.forEach(p => p.classList.toggle('is-active', p.dataset.filter === 'all'));
    currentFilter = 'all';
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
