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

  /* ========== Projects Carousel ========== */
  function initProjectsCarousel() {
    const carousel = $('#projectsCarousel');
    const wrapper = $('.projects-carousel-wrapper');
    const dotsContainer = $('#carouselDots');
    
    if (!carousel || !wrapper) return;

    const cards = $$('.project-card', carousel);
    let currentIndex = 0;
    let itemsPerView = 2;
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
      itemsPerView = 2;
      return true;
    }

    function getTotalPages() {
      return Math.ceil(cards.length / itemsPerView);
    }

    function updateCarousel(smooth = true) {
      if (!updateItemsPerView()) {
        carousel.style.transform = '';
        carousel.style.transition = '';
        return;
      }

      const cardWidth = cards[0]?.offsetWidth || 0;
      const gap = 24;
      const totalPages = getTotalPages();
      
      // Clamp currentIndex to valid range
      currentIndex = Math.max(0, Math.min(currentIndex, totalPages - 1));
      
      // Calculate offset correctly
      const offset = currentIndex * (cardWidth + gap) * itemsPerView;
      
      // Smoother and faster transition
      carousel.style.transition = smooth ? 'transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)' : 'none';
      carousel.style.transform = `translate3d(-${offset}px, 0, 0)`;
    }

    function createDots() {
      // Dots removed - no longer needed
      return;
    }

    function updateDots() {
      // Dots removed - no longer needed
      return;
    }

    function nextSlide() {
      if (!isCarouselEnabled) return;
      const totalPages = getTotalPages();
      currentIndex = (currentIndex + 1) % totalPages;
      updateCarousel();
    }

    function startAutoplay() {
      if (isCarouselEnabled) {
        autoplayInterval = setInterval(nextSlide, 4500); // Faster: 4.5 seconds
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

    // Pause autoplay on hover (only if carousel enabled)
    wrapper.addEventListener('mouseenter', () => {
      if (isCarouselEnabled) stopAutoplay();
    });
    
    wrapper.addEventListener('mouseleave', () => {
      if (isCarouselEnabled) startAutoplay();
    });

    // Touch swipe with improved vertical scroll and better boundaries
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
      
      // Get current translate value
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
      
      // Only start dragging if horizontal movement is clear (threshold: 15px)
      if (!isDragging && !isHorizontalSwipe) {
        if (diffX > 15 || diffY > 15) {
          isHorizontalSwipe = diffX > diffY;
          if (isHorizontalSwipe) {
            isDragging = true;
            carousel.style.transition = 'none';
          }
        }
      }
      
      // Only prevent scroll if definitely horizontal swipe
      if (isDragging && isHorizontalSwipe) {
        e.preventDefault();
        
        touchEndX = touchCurrentX;
        const diff = touchEndX - touchStartX;
        
        // Calculate boundaries
        const containerWidth = wrapper.offsetWidth;
        const totalWidth = (cards[0]?.offsetWidth || 0) * cards.length + 24 * (cards.length - 1);
        const maxTranslate = 0;
        const minTranslate = Math.min(0, containerWidth - totalWidth);
        
        // Real-time dragging with strict boundaries
        let newTranslate = startTranslate + diff;
        newTranslate = Math.max(minTranslate, Math.min(maxTranslate, newTranslate));
        
        // Apply transform with RAF
        if (animationID) cancelAnimationFrame(animationID);
        animationID = requestAnimationFrame(() => {
          carousel.style.transform = `translate3d(${newTranslate}px, 0, 0)`;
        });
      }
    }, { passive: false });

    carousel.addEventListener('touchend', (e) => {
      if (!isCarouselEnabled) return;
      
      if (isDragging) {
        isDragging = false;
        carousel.style.transition = 'transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
        handleSwipe();
      }
      
      resetAutoplay();
    });

    function handleSwipe() {
      const swipeThreshold = 60;
      const diff = touchStartX - touchEndX;
      const totalPages = getTotalPages();
      
      if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
          currentIndex = Math.min(currentIndex + 1, totalPages - 1);
        } else {
          currentIndex = Math.max(currentIndex - 1, 0);
        }
      }
      
      updateCarousel();
    }

    // Window resize handler
    let resizeTimeout;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        const wasEnabled = isCarouselEnabled;
        const nowEnabled = updateItemsPerView();
        
        if (!nowEnabled && wasEnabled) {
          // Carousel disabled (desktop or mobile)
          stopAutoplay();
          carousel.style.transform = '';
          carousel.style.transition = '';
          if (dotsContainer) dotsContainer.innerHTML = '';
        } else if (nowEnabled && !wasEnabled) {
          // Carousel enabled (tablet)
          currentIndex = 0;
          createDots();
          updateCarousel(false);
          startAutoplay();
        } else if (nowEnabled) {
          // Still carousel, just resize
          currentIndex = 0;
          createDots();
          updateCarousel(false);
          stopAutoplay();
          startAutoplay();
        }
      }, 250);
    });

    // Initialize
    if (updateItemsPerView()) {
      createDots();
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
