/* ==========================================================
   CONTACT — one quiet reveal per block, nothing else.
   ========================================================== */
(function () {
  'use strict';

  /* instagram — always show the latest four posts, static tiles are the fallback */
  const igGrid = document.querySelector('.ct-ig-grid');
  if (igGrid) {
    const base = document.body.dataset.api || '';
    fetch(`${base}/api/instagram/latest`)
      .then(r => (r.ok ? r.json() : Promise.reject(new Error(r.status))))
      .then(data => {
        const tiles = igGrid.querySelectorAll('.ct-ig-tile');
        (data.posts || []).slice(0, tiles.length).forEach((post, i) => {
          const tile = tiles[i];
          const img = tile.querySelector('img');
          const snapshot = img.getAttribute('src');
          tile.href = post.permalink;
          tile.setAttribute('aria-label', `Instagram post: ${post.caption || 'Nova Konut'}`);
          img.alt = post.caption || 'Nova Konut Instagram post';
          img.addEventListener('error', () => { img.src = snapshot; }, { once: true });
          img.src = `${base}${post.image}`;
        });
      })
      .catch(() => { /* keep the bundled snapshot */ });
  }

  const gsap = window.gsap;
  const ScrollTrigger = window.ScrollTrigger;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* register interest — UI only, same behaviour as the project pages */
  const form = document.getElementById('ctRegisterForm');
  if (form) {
    const msg = document.createElement('p');
    msg.className = 'ct-form-msg';
    msg.setAttribute('role', 'status');
    msg.dataset.testid = 'contact-register-message';
    form.appendChild(msg);
    form.addEventListener('submit', e => {
      e.preventDefault();
      const name = form.querySelector('[name="fullname"]').value.trim();
      const email = form.querySelector('[name="email"]').value.trim();
      const privacy = form.querySelector('[name="privacy"]').checked;
      if (!name || !email || !privacy) {
        msg.dataset.state = 'error';
        msg.textContent = 'Please complete your name, email and accept the Privacy Policy.';
        return;
      }
      msg.dataset.state = 'ok';
      msg.textContent = 'Thank you. Your interest has been registered — we will be in touch.';
      form.reset();
    });
  }

  if (!gsap || !ScrollTrigger || reduce) return;

  document.documentElement.classList.add('ct-js');
  gsap.registerPlugin(ScrollTrigger);

  const groups = new Map();
  document.querySelectorAll('.page-contact [data-ct]').forEach(el => {
    const key = el.closest('section') || document.body;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(el);
  });
  groups.forEach(items => {
    gsap.fromTo(items,
      { opacity: 0, y: 14 },
      {
        opacity: 1, y: 0, duration: .8, ease: 'power2.out', stagger: 0.08,
        scrollTrigger: { trigger: items[0], start: 'top 94%', once: true }
      });
  });

  addEventListener('load', () => ScrollTrigger.refresh());
})();
