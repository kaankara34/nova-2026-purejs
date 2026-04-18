/* DarGlobal Clone - Interactions */
(function () {
  'use strict';

  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));

  /* ========== Side Menu ========== */
  const menu = $('#sideMenu');
  const overlay = $('#sideMenuOverlay');
  const openBtn = $('#menuToggle');
  const closeBtn = $('#menuClose');

  function openMenu() {
    menu.classList.add('open');
    overlay.classList.add('show');
    document.body.style.overflow = 'hidden';
  }
  function closeMenu() {
    menu.classList.remove('open');
    overlay.classList.remove('show');
    document.body.style.overflow = '';
  }
  openBtn && openBtn.addEventListener('click', openMenu);
  closeBtn && closeBtn.addEventListener('click', closeMenu);
  overlay && overlay.addEventListener('click', closeMenu);
  $$('.side-menu-nav a').forEach(a => a.addEventListener('click', closeMenu));

  /* ========== Header transparency on scroll ========== */
  const header = $('.site-header');
  const heroEl = $('.hero');
  function onScroll() {
    if (!heroEl || !header) return;
    const heroBottom = heroEl.getBoundingClientRect().bottom;
    if (heroBottom > 100) header.classList.add('transparent');
    else header.classList.remove('transparent');
  }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ========== Hero slideshow (Ken Burns) ========== */
  const slides = $$('.hero-media .slide');
  let idx = 0;
  if (slides.length) {
    slides[0].classList.add('active');
    setInterval(() => {
      slides[idx].classList.remove('active');
      idx = (idx + 1) % slides.length;
      slides[idx].classList.add('active');
    }, 5500);
  }

  /* ========== Reveal-on-scroll animations ========== */
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('in-view');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });

  $$('.reveal-up, .reveal-fade, .reveal-stagger').forEach(el => io.observe(el));

  /* ========== Trump collab video (autoplay on load) ========== */
  const muteBtn = $('#collabMute');
  const vid = $('#collabVid');
  
  // Auto-start video when visible
  if (vid) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          vid.play().catch(() => {});
        }
      });
    }, { threshold: 0.5 });
    observer.observe(vid);
  }
  
  if (muteBtn && vid) {
    muteBtn.addEventListener('click', () => {
      vid.muted = !vid.muted;
      muteBtn.setAttribute('data-muted', vid.muted ? 'true' : 'false');
      muteBtn.innerHTML = vid.muted ? iconMute() : iconSound();
    });
  }
  function iconMute() {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="9" x2="17" y2="15"></line><line x1="17" y1="9" x2="23" y2="15"></line></svg>';
  }
  function iconSound() {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>';
  }

  /* ========== Cookie banner ========== */
  const cookie = $('#cookieBanner');
  if (cookie) {
    if (!localStorage.getItem('dg_cookie_ok')) {
      setTimeout(() => cookie.classList.add('show'), 800);
    }
    const accept = () => { localStorage.setItem('dg_cookie_ok', '1'); cookie.classList.remove('show'); };
    $('#cookieAccept')?.addEventListener('click', accept);
    $('#cookieClose')?.addEventListener('click', accept);
  }

  /* ========== Smooth scroll-down button in hero ========== */
  $('#heroScroll')?.addEventListener('click', () => {
    const next = $('#liveAllIn');
    if (next) next.scrollIntoView({ behavior: 'smooth' });
  });

  /* ========== Register form (mock) ========== */
  $('#registerForm')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button.submit');
    const original = btn.textContent;
    btn.textContent = 'THANK YOU — WE WILL BE IN TOUCH';
    btn.disabled = true;
    btn.style.background = '#e0cfa5';
    btn.style.color = '#5a2c30';
    setTimeout(() => {
      btn.textContent = original;
      btn.disabled = false;
      btn.style.background = '';
      btn.style.color = '';
      e.target.reset();
    }, 3200);
  });

  /* ========== Register Interest button scrolls to form ========== */
  $$('[data-scroll="register"]').forEach(b => b.addEventListener('click', (e) => {
    e.preventDefault();
    $('#register')?.scrollIntoView({ behavior: 'smooth' });
    closeMenu();
  }));

  /* ========== Footer Accordion (Mobile Only) ========== */
  function initFooterAccordion() {
    const footerCols = $$('.footer-col');
    
    // Open first accordion on mobile by default
    if (window.innerWidth <= 768 && footerCols.length > 0) {
      footerCols[0].classList.add('active');
    }
    
    footerCols.forEach(col => {
      const heading = col.querySelector('h3');
      if (heading) {
        heading.addEventListener('click', () => {
          // Only work on mobile (<=768px)
          if (window.innerWidth <= 768) {
            const isActive = col.classList.contains('active');
            
            // Close all accordions
            footerCols.forEach(c => c.classList.remove('active'));
            
            // Toggle current
            if (!isActive) {
              col.classList.add('active');
            }
          }
        });
      }
    });
  }
  
  initFooterAccordion();
  
  // Re-init on window resize
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      const footerCols = $$('.footer-col');
      if (window.innerWidth > 768) {
        footerCols.forEach(c => c.classList.remove('active'));
      } else if (window.innerWidth <= 768 && footerCols.length > 0) {
        // Open first on mobile after resize
        if (!$$('.footer-col.active').length) {
          footerCols[0].classList.add('active');
        }
      }
    }, 250);
  });

})();
