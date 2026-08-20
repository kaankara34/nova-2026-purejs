/* Team page — staggered card reveal on scroll (CSS transitions, no GSAP) */
(function () {
  'use strict';

  const cards = document.querySelectorAll('.tm-card');
  if (!cards.length) return;

  if (!('IntersectionObserver' in window)) {
    cards.forEach(c => c.classList.add('is-visible'));
    return;
  }

  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const group = entry.target.closest('.tm-grid');
      const index = group ? [...group.children].indexOf(entry.target) : 0;
      entry.target.style.transitionDelay = (index % 4) * 80 + 'ms';
      entry.target.classList.add('is-visible');
      io.unobserve(entry.target);
    });
  }, { rootMargin: '0px 0px -12% 0px', threshold: 0.12 });

  cards.forEach(card => io.observe(card));
})();
