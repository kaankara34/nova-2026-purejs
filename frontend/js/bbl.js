/* ==========================================================
   BUILD BEYOND LIVING — quiet editorial motion.
   Opacity + small translate reveals, slow image settle,
   an ivory header once the reader leaves the hero.
   ========================================================== */
(function () {
  'use strict';

  const gsap = window.gsap;
  const ScrollTrigger = window.ScrollTrigger;
  const root = document.documentElement;
  const body = document.body;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const hasGsap = !!(gsap && ScrollTrigger);
  const hero = document.querySelector('.bb-hero');

  /* ---------- header ground: transparent over the hero, ivory after ---------- */
  if (hero) {
    const lit = () => body.classList.toggle('bbl-lit', hero.getBoundingClientRect().bottom <= 100);
    addEventListener('scroll', lit, { passive: true });
    addEventListener('resize', lit);
    lit();
    requestAnimationFrame(() => hero.classList.add('is-in'));
  }

  /* ---------- scroll cue ---------- */
  const cue = document.querySelector('.bb-cue');
  if (cue) {
    cue.addEventListener('click', (e) => {
      const target = document.querySelector(cue.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      const header = document.querySelector('.site-header');
      const y = target.getBoundingClientRect().top + scrollY - ((header ? header.offsetHeight : 110) + 18);
      scrollTo({ top: y, behavior: reduce ? 'auto' : 'smooth' });
    });
  }

  if (!hasGsap || reduce) return;

  root.classList.add('bb-js');
  gsap.registerPlugin(ScrollTrigger);

  /* ---------- copy reveals, one group per section ---------- */
  const groups = new Map();
  document.querySelectorAll('.page-bbl [data-bb]').forEach(el => {
    const key = el.closest('section') || body;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(el);
  });
  groups.forEach(items => {
    gsap.fromTo(items,
      { opacity: 0, y: 24 },
      {
        opacity: 1, y: 0, duration: 1.2, ease: 'power2.out', stagger: 0.1,
        scrollTrigger: { trigger: items[0], start: 'top 88%', once: true }
      });
  });

  /* ---------- a line that lands a beat later ---------- */
  document.querySelectorAll('.page-bbl [data-bb-late]').forEach(el => {
    gsap.fromTo(el,
      { opacity: 0, y: 20 },
      {
        opacity: 1, y: 0, duration: 1.3, delay: 0.55, ease: 'power2.out',
        scrollTrigger: { trigger: el, start: 'top 90%', once: true }
      });
  });

  /* ---------- images settle in ---------- */
  document.querySelectorAll('.page-bbl [data-bb-fig]').forEach(fig => {
    const img = fig.querySelector('img');
    if (!img) return;
    gsap.fromTo(img,
      { opacity: 0, scale: 1.03 },
      {
        opacity: 1, scale: 1, duration: 1.4, ease: 'power3.out',
        scrollTrigger: { trigger: fig, start: 'top 92%', once: true }
      });
  });

  addEventListener('load', () => ScrollTrigger.refresh());
})();
