/* ==========================================================
   CONSTRUCTION — scroll-driven engineering narrative
   GSAP ScrollTrigger. Engineering information first, animation second.
   ========================================================== */
(function () {
  const body = document.body;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const hasGSAP = !!(window.gsap && window.ScrollTrigger);
  const clamp = (v, a, b) => v < a ? a : (v > b ? b : v);

  /* ---------- always-on: annotation pins ---------- */
  document.querySelectorAll('[data-cx-pins]').forEach(group => {
    const pins = Array.from(group.querySelectorAll('.cx-pin'));
    const svg = document.querySelector(group.dataset.cxPins);
    const light = id => {
      if (!svg) return;
      svg.querySelectorAll('[data-pin]').forEach(el => el.classList.toggle('is-lit', el.dataset.pin === id));
    };
    pins.forEach(p => p.addEventListener('click', () => {
      const open = p.classList.contains('is-open');
      pins.forEach(o => { o.classList.remove('is-open'); o.setAttribute('aria-expanded', 'false'); });
      if (!open) { p.classList.add('is-open'); p.setAttribute('aria-expanded', 'true'); }
      light(open ? null : p.dataset.pin);
    }));
    if (pins[0]) {
      pins[0].classList.add('is-open');
      pins[0].setAttribute('aria-expanded', 'true');
      light(pins[0].dataset.pin);
    }
  });

  /* ---------- always-on: construction log index ---------- */
  const logIndex = Array.from(document.querySelectorAll('.cx-log-index button'));
  const logEntries = Array.from(document.querySelectorAll('.cx-log-entry'));
  logIndex.forEach((b, i) => b.addEventListener('click', () => {
    if (logEntries[i]) window.scrollTo({ top: logEntries[i].getBoundingClientRect().top + window.scrollY - 160, behavior: 'smooth' });
  }));

  if (reduce || !hasGSAP) {
    body.classList.add('cx-static');
    document.querySelectorAll('[data-cx-fade]').forEach(el => el.classList.add('is-in'));
    document.querySelectorAll('[data-cx-draw] [pathLength]').forEach(el => { el.style.strokeDashoffset = '0'; });
    logIndex.forEach(b => b.classList.add('is-on'));
    return;
  }

  gsap.registerPlugin(ScrollTrigger);

  /* ---------- reveals ---------- */
  document.querySelectorAll('[data-cx-stagger]').forEach(group => {
    Array.from(group.children).forEach((child, i) => {
      if (child.hasAttribute('data-cx-fade')) child.style.transitionDelay = (i * 0.085).toFixed(3) + 's';
    });
  });
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -12% 0px', threshold: 0.12 });
  document.querySelectorAll('[data-cx-fade], .cx-wave').forEach(el => io.observe(el));

  /* ---------- scroll-drawn linework ---------- */
  document.querySelectorAll('[data-cx-draw]').forEach(host => {
    const paths = Array.from(host.querySelectorAll('[pathLength]'));
    if (!paths.length) return;
    const seq = host.dataset.cxDraw === 'sequential';
    ScrollTrigger.create({
      trigger: host,
      start: host.dataset.cxStart || 'top 82%',
      end: host.dataset.cxEnd || 'bottom 60%',
      scrub: 0.6,
      onUpdate: self => {
        const p = self.progress;
        const n = paths.length;
        for (let i = 0; i < n; i++) {
          let local = p;
          if (seq) {
            const w = 1 / n, s = i * w * 0.86;
            local = clamp((p - s) / w, 0, 1);
          }
          paths[i].style.strokeDashoffset = (1 - local).toFixed(4);
        }
      }
    });
  });

  /* ---------- subtle parallax ---------- */
  document.querySelectorAll('[data-cx-parallax]').forEach(el => {
    const amt = parseFloat(el.dataset.cxParallax) || 0.08;
    gsap.fromTo(el, { yPercent: -amt * 100 }, {
      yPercent: amt * 100, ease: 'none',
      scrollTrigger: { trigger: el.parentElement, start: 'top bottom', end: 'bottom top', scrub: true }
    });
  });

  /* ---------- 01 hero: finished architecture -> structural frame ---------- */
  const hero = document.querySelector('.cx-hero');
  if (hero) {
    const finish = hero.querySelector('.cx-hero-layer--finish');
    const frame = hero.querySelector('.cx-hero-layer--frame');
    const grid = hero.querySelectorAll('.cx-hero-grid [pathLength]');
    const state = hero.querySelector('.cx-hero-state');
    const cue = hero.querySelector('.cx-cue');
    const labels = ['Completed architecture', 'Envelope removed', 'Reinforced-concrete frame'];
    let lastLabel = -1;
    ScrollTrigger.create({
      trigger: hero, start: 'top top', end: 'bottom bottom', scrub: 0.5,
      onUpdate: self => {
        const p = self.progress;
        const t = clamp(p / 0.62, 0, 1);
        finish.style.opacity = (1 - t).toFixed(3);
        finish.style.transform = 'scale(' + (1 + t * 0.05).toFixed(4) + ')';
        frame.style.transform = 'scale(' + (1.08 - t * 0.08).toFixed(4) + ')';
        const d = clamp((p - 0.24) / 0.5, 0, 1);
        grid.forEach((g, i) => {
          const local = clamp((d - (i / grid.length) * 0.6) / 0.45, 0, 1);
          g.style.strokeDashoffset = (1 - local).toFixed(4);
        });
        if (cue) cue.style.opacity = (1 - clamp(p / 0.14, 0, 1)).toFixed(3);
        const li = p < 0.3 ? 0 : (p < 0.62 ? 1 : 2);
        if (li !== lastLabel && state) { lastLabel = li; state.textContent = labels[li]; }
      }
    });
  }

  /* ---------- pinned step sequences (desktop only; static chapters at 1200px and below) ---------- */
  gsap.matchMedia().add('(min-width: 1201px)', () => {
    document.querySelectorAll('[data-cx-steps]').forEach(seq => {
      const steps = Array.from(seq.querySelectorAll('.cx-step'));
      const parts = Array.from(seq.querySelectorAll('.cx-part'));
      const single = seq.dataset.cxMode === 'single';
      const n = steps.length || 1;
      let last = -1;
      ScrollTrigger.create({
        trigger: seq, start: 'top top', end: 'bottom bottom', scrub: true,
        onUpdate: self => {
          const idx = clamp(Math.floor(self.progress * n * 1.02), 0, n - 1);
          if (idx === last) return;
          last = idx;
          steps.forEach((s, i) => s.classList.toggle('is-on', i === idx));
          parts.forEach(pt => {
            const i = parseInt(pt.dataset.part, 10);
            pt.classList.toggle('is-lit', single ? i === idx : i <= idx);
          });
        }
      });
    });
    return () => document.querySelectorAll('.cx-step.is-on, .cx-part.is-lit')
      .forEach(el => el.classList.remove('is-on', 'is-lit'));
  });

  /* ---------- 12 stage crossfade ---------- */
  const xf = document.querySelector('.cx-xfade');
  if (xf) {
    const layers = Array.from(xf.querySelectorAll('.cx-xfade-layer'));
    const tags = Array.from(xf.querySelectorAll('.cx-xfade-stages span'));
    ScrollTrigger.create({
      trigger: xf, start: 'top top', end: 'bottom bottom', scrub: 0.4,
      onUpdate: self => {
        const p = self.progress * (layers.length - 1);
        layers.forEach((l, i) => {
          const a = clamp(1 - Math.abs(p - i), 0, 1);
          l.style.opacity = (i === 0 && p < 0 ? 1 : a).toFixed(3);
        });
        const idx = clamp(Math.round(p), 0, tags.length - 1);
        tags.forEach((t, i) => t.classList.toggle('is-on', i === idx));
      }
    });
  }

  /* ---------- log index highlight ---------- */
  logEntries.forEach((entry, i) => {
    ScrollTrigger.create({
      trigger: entry, start: 'top 30%', end: 'bottom 30%',
      onToggle: self => { if (self.isActive) logIndex.forEach((b, j) => b.classList.toggle('is-on', j === i)); }
    });
  });

  ScrollTrigger.refresh();
})();
