/* ==========================================================
   CONTACT — one quiet reveal per block, nothing else.
   ========================================================== */
(function () {
  'use strict';

  const gsap = window.gsap;
  const ScrollTrigger = window.ScrollTrigger;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
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
