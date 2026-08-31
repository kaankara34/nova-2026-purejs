/* ==========================================================
   BUILD BEYOND LIVING — living with Nova.
   Quiet reveals, an ivory header after the hero, and the
   Nova Membership stage that follows the reader.
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

  /* ---------- in-page links ---------- */
  document.querySelectorAll('.page-bbl a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const target = document.querySelector(a.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      const header = document.querySelector('.site-header');
      const y = target.getBoundingClientRect().top + scrollY - ((header ? header.offsetHeight : 110) + 18);
      scrollTo({ top: Math.max(0, y), behavior: reduce ? 'auto' : 'smooth' });
    });
  });

  /* ---------- Nova Membership: the screen follows the reader ---------- */
  const stage = document.querySelector('.bb-mem-stage');
  const feats = Array.from(document.querySelectorAll('.bb-feat'));
  const screens = Array.from(document.querySelectorAll('.bb-phone--stage .bb-scr'));
  if (stage && feats.length && screens.length) {
    const narrow = matchMedia('(max-width: 767px)');
    let current = -1;
    const sync = () => {
      const s = stage.getBoundingClientRect();
      const line = narrow.matches ? s.bottom + 40 : s.top + s.height * 0.5;
      let next = 0;
      feats.forEach((f, i) => { if (f.getBoundingClientRect().top <= line) next = i; });
      if (next === current) return;
      current = next;
      feats.forEach((f, i) => f.classList.toggle('is-active', i === next));
      screens.forEach((sc, i) => sc.classList.toggle('is-on', i === next));
    };
    addEventListener('scroll', sync, { passive: true });
    addEventListener('resize', sync);
    sync();
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
      { opacity: 0, y: 26 },
      {
        opacity: 1, y: 0, duration: 1.2, ease: 'power2.out', stagger: 0.1,
        scrollTrigger: { trigger: items[0], start: 'top 88%', once: true }
      });
  });

  /* ---------- a line that lands a beat later ---------- */
  document.querySelectorAll('.page-bbl [data-bb-late]').forEach(el => {
    gsap.fromTo(el,
      { opacity: 0, y: 22 },
      {
        opacity: 1, y: 0, duration: 1.3, delay: 0.5, ease: 'power2.out',
        scrollTrigger: { trigger: el, start: 'top 90%', once: true }
      });
  });

  /* ---------- images settle in behind a soft clip ---------- */
  document.querySelectorAll('.page-bbl [data-bb-fig]').forEach(fig => {
    const img = fig.querySelector('img');
    if (!img) return;
    gsap.fromTo(img,
      { opacity: 0, scale: 1.035, clipPath: 'inset(6% 0% 6% 0%)' },
      {
        opacity: 1, scale: 1, clipPath: 'inset(0% 0% 0% 0%)',
        duration: 1.3, ease: 'power3.out',
        scrollTrigger: { trigger: fig, start: 'top 92%', once: true }
      });
  });

  /* ---------- the phone arrives once ---------- */
  const introPhone = document.querySelector('[data-bb-phone]');
  if (introPhone) {
    gsap.fromTo(introPhone,
      { opacity: 0, y: 34 },
      {
        opacity: 1, y: 0, duration: 1.3, ease: 'power2.out',
        scrollTrigger: { trigger: introPhone, start: 'top 88%', once: true }
      });
  }

  addEventListener('load', () => ScrollTrigger.refresh());
})();
