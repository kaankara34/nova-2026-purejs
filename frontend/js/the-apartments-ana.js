/* ==========================================================
   The Apartments Ana — project page behaviour.
   Same restrained vocabulary as East West: anchor scrolling,
   a floor-plan lightbox and the shared enquiry form pattern.
   ========================================================== */
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* hero: the poster stands in when motion is reduced */
  const video = document.getElementById('anaHeroVideo');
  if (video) {
    if (reduce) {
      video.pause();
      video.removeAttribute('autoplay');
    } else {
      const play = video.play();
      if (play && play.catch) play.catch(() => { /* poster remains */ });
    }
  }

  /* action bar + in-page anchors */
  const headerOffset = () => {
    const head = document.querySelector('.site-header');
    const bar = document.querySelector('.utility-bar');
    return (head ? head.offsetHeight : 110) + (bar ? bar.offsetHeight : 0);
  };
  document.querySelectorAll('[data-ana-scroll]').forEach(el => {
    el.addEventListener('click', e => {
      const target = document.getElementById(el.dataset.anaScroll);
      if (!target) return;
      e.preventDefault();
      scrollTo({
        top: target.getBoundingClientRect().top + scrollY - headerOffset() - 8,
        behavior: reduce ? 'auto' : 'smooth'
      });
    });
  });

  /* floor plan: zoomable lightbox */
  const plan = document.getElementById('anaPlanImg');
  const box = document.getElementById('anaPlansLightbox');
  const boxImg = document.getElementById('anaPlansLightboxImg');
  const close = document.getElementById('anaPlansLightboxClose');
  const expand = document.getElementById('anaPlansExpand');
  if (plan && box && boxImg) {
    /* the viewer is a viewport-level modal: it never adds document height and
       the page underneath is locked at its current scroll position (same
       mechanism as The Residences East West) */
    const open = () => {
      if (box.classList.contains('open')) return;
      boxImg.src = plan.currentSrc || plan.src;
      box.classList.add('open');
      box.setAttribute('aria-hidden', 'false');
      if (window.lockScroll) window.lockScroll();
    };
    const hide = () => {
      if (!box.classList.contains('open')) return;
      box.classList.remove('open');
      box.setAttribute('aria-hidden', 'true');
      if (window.unlockScroll) window.unlockScroll();
    };
    plan.addEventListener('click', open);
    if (expand) expand.addEventListener('click', open);
    if (close) close.addEventListener('click', hide);
    box.addEventListener('click', e => { if (e.target === box) hide(); });
    addEventListener('keydown', e => {
      if (e.key === 'Escape' && box.classList.contains('open')) hide();
    });
  }

  /* location: dark OpenStreetMap with the Ana site plan laid over it */
  const mapEl = document.getElementById('anaMap');
  if (mapEl && window.L) {
    const L = window.L;
    const lat = parseFloat(mapEl.dataset.lat);
    const lng = parseFloat(mapEl.dataset.lng);
    const map = L.map(mapEl, {
      center: [lat, lng],
      zoom: 16,
      scrollWheelZoom: true,
      zoomControl: true,
      attributionControl: true
    });
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    const bounds = L.latLngBounds([lat - 0.0016, lng - 0.0034], [lat + 0.0016, lng + 0.0034]);
    L.marker([lat, lng], {
      icon: L.divIcon({ className: 'ana-map-pin', iconSize: [18, 18], iconAnchor: [9, 9] }),
      title: 'The Apartments Ana'
    }).addTo(map);
    map.fitBounds(bounds);
    /* the card reveals with the section, so re-measure once it is laid out */
    setTimeout(() => map.invalidateSize(), 400);
    addEventListener('resize', () => map.invalidateSize());
  }

  /* floor plan: a single 3+1 residence — both apartments on the typical floor are 3+1 */
  const PLAN = { type: '3+1', gross: '150 m²', net: '112 m²' };

  /* floor plan: print sheet */
  const printBtn = document.getElementById('anaPlansPrint');
  if (printBtn && plan) {
    printBtn.addEventListener('click', () => {
      const win = open('', '_blank');
      if (!win) return;
      win.document.write(
        '<title>The Apartments Ana \u2014 ' + PLAN.type + ' Floor Plan</title>' +
        '<style>@page{size:A4;margin:14mm}body{margin:0;font-family:Montserrat,Arial,sans-serif;text-align:center}' +
        'h1{font-size:14px;letter-spacing:.2em;text-transform:uppercase;margin:0 0 4px}' +
        'p{font-size:11px;letter-spacing:.1em;color:#555;margin:0 0 14px}' +
        'img{max-width:100%;max-height:76vh}</style>' +
        '<h1>The Apartments Ana &mdash; ' + PLAN.type + '</h1>' +
        '<p>' + PLAN.gross + ' gross &nbsp;&middot;&nbsp; ' + PLAN.net + ' net &nbsp;&middot;&nbsp; Kemal Sunal Sokak, Caddebostan</p>' +
        '<img src="' + (plan.currentSrc || plan.src) + '" alt="Floor plan" onload="window.focus();window.print()" />'
      );
      win.document.close();
    });
  }

  /* enquiry form — UI only, same validation pattern as the other project pages */
  const form = document.getElementById('anaEnquireForm');
  const msg = document.getElementById('anaFormMsg');
  if (form && msg) {
    form.addEventListener('submit', e => {
      e.preventDefault();
      const name = form.querySelector('[name="fullname"]').value.trim();
      const email = form.querySelector('[name="email"]').value.trim();
      const privacy = form.querySelector('[name="privacy"]').checked;
      if (!name || !email || !privacy) {
        msg.dataset.state = 'error';
        msg.textContent = 'Please complete your name, email and accept the Privacy Policy.';
        return;
      }
      msg.dataset.state = 'ok';
      msg.textContent = 'Thank you. Your request has been received — we will be in touch shortly.';
      form.reset();
      form.querySelector('[name="project"]').selectedIndex = 0;
    });
  }

  /* parking + arrival + architecture: quiet clip/lift reveal, staggered */
  if (!reduce) {
    const groups = [...document.querySelectorAll('[data-ana-parking-reveal], [data-ana-kulup-reveal], .ana-render-inner')];
    groups.forEach(g => {
      g.classList.add('is-pending');
      [...g.querySelectorAll('.ana-parking-eyebrow, .ana-parking-heading, .ana-parking-body, .ana-parking-figures, .ana-parking-note, .ana-render-eyebrow, .ana-render-title, .ana-render-copy, .ana-kulup-logo-panel, .ana-kulup-eyebrow, .ana-kulup-heading, .ana-kulup-body')]
        .forEach((el, i) => el.style.setProperty('--ana-delay', (0.04 + i * 0.08).toFixed(2) + 's'));
    });
    const io = new IntersectionObserver((entries, obs) => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        e.target.classList.remove('is-pending');
        obs.unobserve(e.target);
      });
    }, { rootMargin: '300px 0px 0px 0px', threshold: 0 });
    groups.forEach(g => io.observe(g));
  }
})();
