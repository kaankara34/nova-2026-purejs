/* ==========================================================
   DESIGN page — restrained editorial motion.
   Opacity + small translate reveals, slow image settle,
   smooth anchor navigation and an index that follows the page.
   ========================================================== */
(function () {
  'use strict';

  const gsap = window.gsap;
  const ScrollTrigger = window.ScrollTrigger;
  const root = document.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const hasGsap = !!(gsap && ScrollTrigger);

  /* ---------- index: smooth anchors + active state ---------- */
  const index = document.getElementById('dzIndex');
  if (index) {
    const links = Array.from(index.querySelectorAll('[data-dz-link]'));
    const headerOffset = () => {
      const h = document.querySelector('.site-header');
      const bar = document.querySelector('.utility-bar');
      return (h ? h.offsetHeight : 110) + (bar ? bar.offsetHeight : 0) + 18;
    };
    links.forEach(a => {
      a.addEventListener('click', (e) => {
        const target = document.querySelector(a.getAttribute('href'));
        if (!target) return;
        e.preventDefault();
        const y = target.getBoundingClientRect().top + scrollY - headerOffset();
        scrollTo({ top: y, behavior: reduce ? 'auto' : 'smooth' });
      });
    });
    const sections = links
      .map(a => ({ a, sec: document.querySelector(a.getAttribute('href')) }))
      .filter(o => o.sec)
      .sort((x, y) => x.sec.offsetTop - y.sec.offsetTop);
    const mark = () => {
      const line = scrollY + headerOffset() + 40;
      let active = null;
      sections.forEach(o => { if (o.sec.offsetTop <= line) active = o.a; });
      links.forEach(a => a.classList.toggle('is-on', a === active));
    };
    addEventListener('scroll', mark, { passive: true });
    addEventListener('resize', mark);
    mark();
  }

  if (!hasGsap || reduce) return;

  root.classList.add('dz-js');
  gsap.registerPlugin(ScrollTrigger);

  /* ---------- copy reveals ---------- */
  const groups = new Map();
  document.querySelectorAll('.page-design [data-dz]').forEach(el => {
    const key = el.closest('section') || document.body;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(el);
  });
  groups.forEach(items => {
    gsap.fromTo(items,
      { opacity: 0, y: 22 },
      {
        opacity: 1, y: 0, duration: 1.15, ease: 'power2.out', stagger: 0.09,
        scrollTrigger: { trigger: items[0], start: 'top 88%', once: true }
      });
  });

  /* ---------- images settle in ---------- */
  document.querySelectorAll('.page-design [data-dz-fig]').forEach(fig => {
    const img = fig.querySelector('img');
    if (!img) return;
    gsap.fromTo(img,
      { opacity: 0, scale: 1.035 },
      {
        opacity: 1, scale: 1, duration: 1.4, ease: 'power3.out',
        scrollTrigger: { trigger: fig, start: 'top 92%', once: true }
      });
  });

  addEventListener('load', () => ScrollTrigger.refresh());
})();
