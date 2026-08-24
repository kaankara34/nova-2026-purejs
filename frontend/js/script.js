

/* DarGlobal Clone - Interactions */

/* ========== GLOBAL scroll-lock (used by every lightbox / modal) =========
   `document.body.style.overflow='hidden'` alone is unreliable — iOS Safari
   and Android Chrome will still scroll the html element and rubber-band the
   viewport. This utility locks the body with `position: fixed` while saving
   the current scrollY so we can restore it exactly on unlock. */
(function () {
  let lockDepth = 0;
  let savedY = 0;
  window.lockScroll = function lockScroll() {
    if (lockDepth++ > 0) return;                // already locked
    savedY = window.scrollY || window.pageYOffset || 0;
    document.body.style.top = `-${savedY}px`;
    document.documentElement.classList.add('no-scroll');
    document.body.classList.add('no-scroll');
  };
  window.unlockScroll = function unlockScroll() {
    if (lockDepth === 0) return;
    if (--lockDepth > 0) return;                // still nested-locked
    /* Cache first, then clear styles, then restore in the *next* frame so
       the browser has committed the reflow (body back to static, page height
       recalculated) before we scroll back — otherwise the scroll can be
       clamped to a smaller pre-reflow document height. */
    const y = savedY;
    document.documentElement.classList.remove('no-scroll');
    document.body.classList.remove('no-scroll');
    document.body.style.top = '';
    /* html has `scroll-behavior: smooth` globally — window.scrollTo() would
       otherwise animate from 0 up to y, visibly scrolling the page from the
       top back down. Force an instant jump, then restore smooth scrolling. */
    const html = document.documentElement;
    const prevBehavior = html.style.scrollBehavior;
    html.style.scrollBehavior = 'auto';
    /* Immediate + rAF: covers both fast browsers and iOS Safari. */
    window.scrollTo(0, y);
    requestAnimationFrame(() => {
      window.scrollTo(0, y);
      html.style.scrollBehavior = prevBehavior;
    });
  };
})();

(function () {
  'use strict';

  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));

  /* ========== Side Menu — 3-column expanding ========== */
  const menu = $('#sideMenu');
  const overlay = $('#sideMenuOverlay');
  const openBtn = $('#menuToggle');
  const closeBtn = $('#menuClose');
  const subBackBtn = $('#colSubBack');
  const subTitleEl = $('#colSubTitle');

  const MOBILE_BP = 1100;
  const isMobile = () => window.innerWidth <= MOBILE_BP;

  function resetMenuState() {
    menu.classList.remove('expanded-1', 'expanded-2', 'sub-open');
    $$('.col-main .menu-item').forEach(it => it.classList.remove('active'));
    $$('.col-sub .submenu').forEach(s => s.classList.remove('active'));
    $$('.col-sub .submenu li.has-projects').forEach(li => { li.classList.remove('active'); li.classList.remove('expanded'); });
    $$('.col-projects .projects-preview').forEach(p => p.classList.remove('active'));
    if (subTitleEl) subTitleEl.textContent = '';
  }

  function openMenu() {
    menu.classList.add('open');
    overlay.classList.add('show');
    window.lockScroll();
  }
  function closeMenu() {
    menu.classList.remove('open');
    overlay.classList.remove('show');
    window.unlockScroll();
    setTimeout(resetMenuState, 500);
  }
  openBtn && openBtn.addEventListener('click', openMenu);
  closeBtn && closeBtn.addEventListener('click', closeMenu);
  overlay && overlay.addEventListener('click', closeMenu);

  // Back button (mobile): close sub-panel and return to main
  subBackBtn && subBackBtn.addEventListener('click', () => {
    menu.classList.remove('sub-open');
    $$('.col-main .menu-item').forEach(it => it.classList.remove('active'));
    $$('.col-sub .submenu li.has-projects').forEach(li => li.classList.remove('expanded'));
  });

  // Main menu items: HOVER (desktop) / CLICK (mobile) to reveal submenu
  let hoverTimer = null;
  $$('.col-main .menu-item').forEach(item => {
    const link = item.querySelector('.menu-link');
    if (!link) return;
    const target = item.dataset.target;

    const showSub = () => {
      if (!item.classList.contains('has-sub') || !target) return;
      clearTimeout(hoverTimer);
      $$('.col-main .menu-item').forEach(it => it.classList.remove('active'));
      $$('.col-sub .submenu').forEach(s => s.classList.remove('active'));
      $$('.col-sub .submenu li.has-projects').forEach(li => { li.classList.remove('active'); li.classList.remove('expanded'); });
      $$('.col-projects .projects-preview').forEach(p => p.classList.remove('active'));
      item.classList.add('active');
      const sub = $('.col-sub .submenu[data-id="' + target + '"]');
      if (sub) {
        sub.classList.add('active');
        if (subTitleEl) subTitleEl.textContent = sub.dataset.title || '';
      }
      if (isMobile()) {
        menu.classList.add('sub-open');
        menu.classList.remove('expanded-1', 'expanded-2');
      } else {
        menu.classList.add('expanded-1');
        menu.classList.remove('expanded-2');
      }
    };

    // Desktop: hover opens
    item.addEventListener('mouseenter', () => {
      if (!isMobile()) showSub();
    });

    // Click: works on both, but mobile uses slide-in
    link.addEventListener('click', e => {
      if (item.classList.contains('has-sub') && target) {
        e.preventDefault();
        showSub();
      } else {
        closeMenu();
      }
    });
  });

  // Submenu items with projects:
  //  - Desktop: hover/click reveals 3rd column (image cards)
  //  - Mobile: click toggles inline accordion
  $$('.col-sub .submenu li.has-projects').forEach(li => {
    const a = li.querySelector('a');
    const revealDesktop = () => {
      $$('.col-sub .submenu li.has-projects').forEach(x => x.classList.remove('active'));
      $$('.col-projects .projects-preview').forEach(p => p.classList.remove('active'));
      li.classList.add('active');
      const id = li.dataset.projects;
      const preview = $('.col-projects .projects-preview[data-id="' + id + '"]');
      if (preview) preview.classList.add('active');
      menu.classList.add('expanded-2');
    };
    const toggleMobile = () => {
      const wasExpanded = li.classList.contains('expanded');
      $$('.col-sub .submenu li.has-projects').forEach(x => x.classList.remove('expanded'));
      if (!wasExpanded) li.classList.add('expanded');
    };
    li.addEventListener('mouseenter', () => { if (!isMobile()) revealDesktop(); });
    if (a) {
      a.addEventListener('click', e => {
        e.preventDefault();
        if (isMobile()) toggleMobile();
        else revealDesktop();
      });
    }
  });

  // Plain submenu links without projects: close menu on click
  $$('.col-sub .submenu li:not(.has-projects) a').forEach(a => {
    a.addEventListener('click', closeMenu);
  });
  $$('.col-projects .proj-card').forEach(c => c.addEventListener('click', closeMenu));

  /* ========== Custom always-visible GOLD scrollbar for col-projects ========== */
  const colProj = $('.col-projects');
  const sbTrack = $('#colProjectsSb');
  const sbThumb = $('#colProjectsSbThumb');

  function updateColProjScrollbar() {
    if (!colProj || !sbThumb || !sbTrack) return;
    const sh = colProj.scrollHeight;
    const ch = colProj.clientHeight;
    if (sh <= ch) {
      sbThumb.style.height = '0px';
      sbThumb.style.top = '0px';
      sbTrack.style.display = 'none';
      return;
    }
    sbTrack.style.display = 'block';
    const ratio = ch / sh;
    const thumbH = Math.max(40, ch * ratio);
    const maxScroll = sh - ch;
    const thumbTop = maxScroll > 0
      ? (colProj.scrollTop / maxScroll) * (ch - thumbH)
      : 0;
    sbThumb.style.height = thumbH + 'px';
    sbThumb.style.top = thumbTop + 'px';
    // align track to col-projects bounding box (within side-menu-grid)
    const grid = sbTrack.parentElement;
    if (grid) {
      const gRect = grid.getBoundingClientRect();
      const cRect = colProj.getBoundingClientRect();
      sbTrack.style.top = (cRect.top - gRect.top) + 'px';
      sbTrack.style.height = cRect.height + 'px';
    }
  }

  if (colProj && sbThumb && sbTrack) {
    colProj.addEventListener('scroll', updateColProjScrollbar, { passive: true });
    window.addEventListener('resize', updateColProjScrollbar);
    // Re-measure when the menu expands to column 3 (images may still be loading)
    const sm = $('#sideMenu');
    if (sm) {
      const mo = new MutationObserver(() => {
        if (sm.classList.contains('expanded-2')) {
          requestAnimationFrame(updateColProjScrollbar);
          setTimeout(updateColProjScrollbar, 250);
          setTimeout(updateColProjScrollbar, 600);
        }
      });
      mo.observe(sm, { attributes: true, attributeFilter: ['class'] });
    }
    // Recalc once images inside col-projects load
    $$('.col-projects img').forEach(img => {
      if (img.complete) return;
      img.addEventListener('load', updateColProjScrollbar);
    });
    updateColProjScrollbar();

    // Drag-to-scroll on thumb
    let dragging = false;
    let dragStartY = 0;
    let dragStartScroll = 0;
    sbThumb.addEventListener('mousedown', e => {
      dragging = true;
      dragStartY = e.clientY;
      dragStartScroll = colProj.scrollTop;
      document.body.style.userSelect = 'none';
      e.preventDefault();
    });
    document.addEventListener('mousemove', e => {
      if (!dragging) return;
      const ch = colProj.clientHeight;
      const sh = colProj.scrollHeight;
      const maxScroll = sh - ch;
      const thumbH = sbThumb.offsetHeight;
      const scrollableArea = ch - thumbH;
      if (scrollableArea <= 0) return;
      const delta = (e.clientY - dragStartY) / scrollableArea * maxScroll;
      colProj.scrollTop = dragStartScroll + delta;
    });
    document.addEventListener('mouseup', () => {
      if (dragging) {
        dragging = false;
        document.body.style.userSelect = '';
      }
    });
    // Click on track jumps thumb
    sbTrack.addEventListener('mousedown', e => {
      if (e.target === sbThumb) return;
      const trackRect = sbTrack.getBoundingClientRect();
      const clickY = e.clientY - trackRect.top;
      const thumbH = sbThumb.offsetHeight;
      const ch = colProj.clientHeight;
      const sh = colProj.scrollHeight;
      const ratio = (clickY - thumbH / 2) / (ch - thumbH);
      colProj.scrollTop = Math.max(0, Math.min(sh - ch, ratio * (sh - ch)));
    });
  }

  /* ========== Header transparency on scroll ========== */
  const header = $('.site-header');
  const utilityBar = $('.utility-bar');
  const heroEl = $('.hero, .pj-hero, .ew-hero, .cx-hero');
  function onScroll() {
    // Hide utility bar when scrolled down past 40px
    if (utilityBar) {
      if (window.scrollY > 40) {
        utilityBar.classList.add('hidden');
        if (header) header.classList.add('bar-hidden');
      } else {
        utilityBar.classList.remove('hidden');
        if (header) header.classList.remove('bar-hidden');
      }
    }
    if (!header) return;
    if (!heroEl) {
      // No hero on this page — header is always solid
      header.classList.remove('transparent');
      return;
    }
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
    /* threshold 0 + negative rootMargin: fires as soon as ANY pixel of the
       element enters the viewport (60px above the fold). This handles tall
       sections (huge image grids) which never satisfy a percentage threshold. */
  }, { threshold: 0, rootMargin: '0px 0px -60px 0px' });

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

  /* ========== Projects Carousel ========== */
  function initProjectsCarousel() {
    const carousel = $('#projectsCarousel');
    const wrapper = $('.projects-carousel-wrapper');
    const progressBar = $('#carouselProgress');
    
    if (!carousel || !wrapper) return;

    const cards = $$('.project-card', carousel);
    let currentIndex = 0;
    let autoplayInterval;
    let isCarouselEnabled = false;

    function updateItemsPerView() {
      const width = window.innerWidth;
      
      // Disable carousel on desktop (>1366px) and mobile (<768px)
      if (width > 1366 || width < 768) {
        isCarouselEnabled = false;
        return false;
      }
      
      // Enable carousel on tablets/iPad (768px - 1366px)
      isCarouselEnabled = true;
      return true;
    }

    function getTotalSlides() {
      // Total individual cards (not pages)
      return cards.length;
    }

    function updateCarousel(smooth = true) {
      if (!updateItemsPerView()) {
        carousel.style.transform = '';
        carousel.style.transition = '';
        if (progressBar) progressBar.style.width = '0%';
        return;
      }

      const cardWidth = cards[0]?.offsetWidth || 0;
      const gap = 24;
      const totalSlides = getTotalSlides();
      const containerWidth = wrapper.offsetWidth;
      const totalWidth = cardWidth * totalSlides + gap * (totalSlides - 1);
      
      // Maksimum kaydırma miktarı (negatif değer)
      const minTranslate = Math.min(0, containerWidth - totalWidth);
      const scrollableWidth = Math.abs(minTranslate);
      const maxIndex = scrollableWidth > 0 ? Math.ceil(scrollableWidth / (cardWidth + gap)) : 0;
      
      // currentIndex'i clamp et
      currentIndex = Math.max(0, Math.min(currentIndex, maxIndex));
      
      // currentIndex'e göre offset hesapla (negatif)
      let offset = -(currentIndex * (cardWidth + gap));
      
      // Offset'i minTranslate ile sınırla (daha fazla sola gitmemesi için)
      offset = Math.max(offset, minTranslate);
      
      // Smooth slow transition (marquee gibi)
      carousel.style.transition = smooth ? 'transform 2s cubic-bezier(0.25, 0.1, 0.25, 1)' : 'none';
      carousel.style.transform = `translate3d(${offset}px, 0, 0)`;

      updateProgressBar();
    }

    function updateProgressBar() {
      if (!progressBar || !isCarouselEnabled) return;
      
      const containerWidth = wrapper.offsetWidth;
      const cardWidth = cards[0]?.offsetWidth || 0;
      const gap = 24;
      const totalWidth = cardWidth * cards.length + gap * (cards.length - 1);
      const scrollableWidth = Math.max(0, totalWidth - containerWidth);
      
      if (scrollableWidth === 0) {
        progressBar.style.width = '100%';
        return;
      }
      
      // Mevcut scroll pozisyonunu al
      const currentOffset = currentIndex * (cardWidth + gap);
      const progress = (currentOffset / scrollableWidth) * 100;
      const clampedProgress = Math.max(0, Math.min(100, progress));
      
      progressBar.style.width = `${clampedProgress}%`;
    }

    function nextSlide() {
      if (!isCarouselEnabled) return;
      const totalSlides = getTotalSlides();
      const cardWidth = cards[0]?.offsetWidth || 0;
      const gap = 24;
      const containerWidth = wrapper.offsetWidth;
      const totalWidth = cardWidth * totalSlides + gap * (totalSlides - 1);
      const scrollableWidth = Math.max(0, totalWidth - containerWidth);
      const maxIndex = scrollableWidth > 0 ? Math.ceil(scrollableWidth / (cardWidth + gap)) : 0;
      
      // Birer birer ilerle
      if (currentIndex < maxIndex) {
        currentIndex++;
      } else {
        // Son karta gelince başa dön
        currentIndex = 0;
      }
      
      updateCarousel();
    }

    function startAutoplay() {
      if (isCarouselEnabled) {
        // Daha yavaş otomatik geçiş (5 saniye)
        autoplayInterval = setInterval(nextSlide, 5000);
      }
    }

    function stopAutoplay() {
      if (autoplayInterval) {
        clearInterval(autoplayInterval);
        autoplayInterval = null;
      }
    }

    function resetAutoplay() {
      stopAutoplay();
      startAutoplay();
    }

    // Pause on hover
    wrapper.addEventListener('mouseenter', () => {
      if (isCarouselEnabled) stopAutoplay();
    });
    
    wrapper.addEventListener('mouseleave', () => {
      if (isCarouselEnabled) startAutoplay();
    });

    // Touch swipe with smooth scroll
    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let isDragging = false;
    let isHorizontalSwipe = false;
    let currentTranslate = 0;
    let startTranslate = 0;
    let animationID = null;

    carousel.addEventListener('touchstart', (e) => {
      if (!isCarouselEnabled) return;
      touchStartX = e.touches[0].clientX;
      touchStartY = e.touches[0].clientY;
      isDragging = false;
      isHorizontalSwipe = false;
      stopAutoplay();
      
      const style = window.getComputedStyle(carousel);
      const matrix = new DOMMatrix(style.transform);
      currentTranslate = matrix.m41;
      startTranslate = currentTranslate;
    });

    carousel.addEventListener('touchmove', (e) => {
      if (!isCarouselEnabled) return;
      
      const touchCurrentX = e.touches[0].clientX;
      const touchCurrentY = e.touches[0].clientY;
      
      const diffX = Math.abs(touchCurrentX - touchStartX);
      const diffY = Math.abs(touchCurrentY - touchStartY);
      
      if (!isDragging && !isHorizontalSwipe) {
        if (diffX > 15 || diffY > 15) {
          isHorizontalSwipe = diffX > diffY;
          if (isHorizontalSwipe) {
            isDragging = true;
            carousel.style.transition = 'none';
          }
        }
      }
      
      if (isDragging && isHorizontalSwipe) {
        e.preventDefault();
        
        touchEndX = touchCurrentX;
        const diff = touchEndX - touchStartX;
        
        const containerWidth = wrapper.offsetWidth;
        const cardWidth = cards[0]?.offsetWidth || 0;
        const gap = 24;
        const totalWidth = cardWidth * cards.length + gap * (cards.length - 1);
        const maxTranslate = 0;
        const minTranslate = Math.min(0, containerWidth - totalWidth);
        
        let newTranslate = startTranslate + diff;
        newTranslate = Math.max(minTranslate, Math.min(maxTranslate, newTranslate));
        
        if (animationID) cancelAnimationFrame(animationID);
        animationID = requestAnimationFrame(() => {
          carousel.style.transform = `translate3d(${newTranslate}px, 0, 0)`;
          
          // Update progress bar real-time
          const progress = Math.abs(newTranslate) / Math.abs(minTranslate) * 100;
          if (progressBar) progressBar.style.width = `${Math.min(100, progress)}%`;
        });
      }
    }, { passive: false });

    carousel.addEventListener('touchend', (e) => {
      if (!isCarouselEnabled) return;
      
      if (isDragging) {
        isDragging = false;
        carousel.style.transition = 'transform 2s cubic-bezier(0.25, 0.1, 0.25, 1)';
        
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;
        const totalSlides = getTotalSlides();
        const cardWidth = cards[0]?.offsetWidth || 0;
        const gap = 24;
        const containerWidth = wrapper.offsetWidth;
        const totalWidth = cardWidth * totalSlides + gap * (totalSlides - 1);
        const scrollableWidth = Math.max(0, totalWidth - containerWidth);
        const maxIndex = scrollableWidth > 0 ? Math.ceil(scrollableWidth / (cardWidth + gap)) : 0;
        
        if (Math.abs(diff) > swipeThreshold) {
          if (diff > 0) {
            currentIndex = Math.min(currentIndex + 1, maxIndex);
          } else {
            currentIndex = Math.max(currentIndex - 1, 0);
          }
        }
        
        updateCarousel();
      }
      
      resetAutoplay();
    });

    // Window resize handler
    let resizeTimeout;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        const wasEnabled = isCarouselEnabled;
        const nowEnabled = updateItemsPerView();
        
        if (!nowEnabled && wasEnabled) {
          stopAutoplay();
          carousel.style.transform = '';
          carousel.style.transition = '';
          if (progressBar) progressBar.style.width = '0%';
        } else if (nowEnabled && !wasEnabled) {
          currentIndex = 0;
          updateCarousel(false);
          startAutoplay();
        } else if (nowEnabled) {
          currentIndex = 0;
          updateCarousel(false);
          stopAutoplay();
          startAutoplay();
        }
      }, 250);
    });

    // Initialize
    if (updateItemsPerView()) {
      updateCarousel(false);
      startAutoplay();
    }
  }

  initProjectsCarousel();

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
