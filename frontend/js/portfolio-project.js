/* NOVA portfolio project pages — shared behaviour (pp-*)
   Runs only when the pp- components are present on the page. */
(function () {
  'use strict';

  const root = document.querySelector('.pp-page');
  if (!root) return;

  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));

  /* ---------- one-time reveals ---------- */
  const revealTargets = $$('.pp-reveal, .pp-reveal-media');
  if (revealTargets.length) {
    const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) {
      revealTargets.forEach(el => el.classList.add('is-in'));
    } else {
      const io = new IntersectionObserver(entries => {
        entries.forEach(e => {
          if (!e.isIntersecting) return;
          e.target.classList.add('is-in');
          io.unobserve(e.target);
        });
      }, { threshold: 0, rootMargin: '0px 0px -60px 0px' });
      revealTargets.forEach((el, i) => {
        const group = el.closest('[data-pp-stagger]');
        if (group) {
          const peers = $$('.pp-reveal, .pp-reveal-media', group);
          el.style.setProperty('--pp-delay', (peers.indexOf(el) * 0.09).toFixed(2) + 's');
        } else if (el.dataset.ppDelay) {
          el.style.setProperty('--pp-delay', el.dataset.ppDelay);
        }
        io.observe(el);
        void i;
      });
    }
  }

  /* ---------- gallery lightbox ---------- */
  const box = $('#ppLightbox');
  const items = $$('[data-pp-open]');
  if (box && items.length) {
    const boxImg = $('#ppLightboxImg');
    const meta = $('#ppLightboxMeta');
    const slides = items.map(el => {
      const img = el.querySelector('img');
      const cap = el.querySelector('.pp-media-caption');
      return {
        src: img.currentSrc || img.src,
        alt: img.alt || '',
        caption: cap ? cap.textContent.trim() : ''
      };
    });
    let index = 0;

    const paint = () => {
      const s = slides[index];
      boxImg.src = s.src;
      boxImg.alt = s.alt;
      meta.textContent = (s.caption ? s.caption + ' — ' : '') + (index + 1) + ' / ' + slides.length;
    };
    const open = i => {
      if (box.classList.contains('open')) return;
      index = i;
      paint();
      box.classList.add('open');
      box.setAttribute('aria-hidden', 'false');
      if (window.lockScroll) window.lockScroll();
      $('#ppLightboxClose').focus();
    };
    const hide = () => {
      if (!box.classList.contains('open')) return;
      box.classList.remove('open');
      box.setAttribute('aria-hidden', 'true');
      if (window.unlockScroll) window.unlockScroll();
    };
    const step = d => { index = (index + d + slides.length) % slides.length; paint(); };

    items.forEach((el, i) => {
      el.setAttribute('tabindex', '0');
      el.setAttribute('role', 'button');
      el.addEventListener('click', () => open(i));
      el.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(i); }
      });
    });
    $$('[data-pp-open-all]').forEach(btn => btn.addEventListener('click', () => open(0)));

    $('#ppLightboxClose').addEventListener('click', hide);
    $('#ppLightboxPrev').addEventListener('click', () => step(-1));
    $('#ppLightboxNext').addEventListener('click', () => step(1));
    box.addEventListener('click', e => { if (e.target === box) hide(); });
    addEventListener('keydown', e => {
      if (!box.classList.contains('open')) return;
      if (e.key === 'Escape') hide();
      else if (e.key === 'ArrowLeft') step(-1);
      else if (e.key === 'ArrowRight') step(1);
    });

    if (slides.length < 2) {
      $('#ppLightboxPrev').hidden = true;
      $('#ppLightboxNext').hidden = true;
    }
  }

  /* ---------- enquiry form ---------- */
  const form = $('#ppEnquiryForm');
  if (form) {
    const msg = $('#ppFormMsg');
    form.addEventListener('submit', e => {
      e.preventDefault();
      const name = form.querySelector('[name="fullname"]').value.trim();
      const email = form.querySelector('[name="email"]').value.trim();
      const privacy = form.querySelector('[name="privacy"]').checked;
      if (!name || !email || !privacy) {
        msg.textContent = 'Please complete your name, email and accept the privacy policy.';
        return;
      }
      msg.textContent = 'Thank you. Your request has been received — our team will be in touch.';
      form.reset();
    });
  }

  /* the shared header / bottom-bar REGISTER INTEREST buttons are handled by
     js/script.js, which scrolls to #register — no extra listener needed here */
})();
