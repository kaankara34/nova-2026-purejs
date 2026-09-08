/* ==========================================================
   The Apartments Taç — project page behaviour.
   Same restrained vocabulary as East West: anchor scrolling,
   a floor-plan lightbox and the shared enquiry form pattern.
   ========================================================== */
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* hero: the poster stands in when motion is reduced */
  const video = document.getElementById('tacHeroVideo');
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
  document.querySelectorAll('[data-tac-scroll]').forEach(el => {
    el.addEventListener('click', e => {
      const target = document.getElementById(el.dataset.tacScroll);
      if (!target) return;
      e.preventDefault();
      scrollTo({
        top: target.getBoundingClientRect().top + scrollY - headerOffset() - 8,
        behavior: reduce ? 'auto' : 'smooth'
      });
    });
  });

  /* floor plan: zoomable lightbox */
  const plan = document.getElementById('tacPlanImg');
  const box = document.getElementById('tacPlansLightbox');
  const boxImg = document.getElementById('tacPlansLightboxImg');
  const close = document.getElementById('tacPlansLightboxClose');
  const expand = document.getElementById('tacPlansExpand');
  if (plan && box && boxImg) {
    const open = () => {
      boxImg.src = plan.currentSrc || plan.src;
      box.classList.add('open');
      box.setAttribute('aria-hidden', 'false');
      boxImg.classList.remove('is-zoomed');
    };
    const hide = () => {
      box.classList.remove('open');
      box.setAttribute('aria-hidden', 'true');
    };
    plan.addEventListener('click', open);
    if (expand) expand.addEventListener('click', open);
    if (close) close.addEventListener('click', hide);
    box.addEventListener('click', e => { if (e.target === box) hide(); });
    boxImg.addEventListener('click', () => boxImg.classList.toggle('is-zoomed'));
    addEventListener('keydown', e => { if (e.key === 'Escape') hide(); });
  }

  /* location: dark OpenStreetMap with the Taç site plan laid over it */
  const mapEl = document.getElementById('tacMap');
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
    L.imageOverlay('./media/images/tac/tac-site-map.webp', bounds, {
      opacity: 0.96,
      interactive: false,
      alt: 'The Apartments Taç site plan on Bağdat Caddesi'
    }).addTo(map);
    L.marker([lat, lng], {
      icon: L.divIcon({ className: 'tac-map-pin', iconSize: [18, 18], iconAnchor: [9, 9] }),
      title: 'The Apartments Taç'
    }).addTo(map);
    map.fitBounds(bounds);
  }

  /* floor plan: print sheet */
  const printBtn = document.getElementById('tacPlansPrint');
  if (printBtn && plan) {
    printBtn.addEventListener('click', () => {
      const win = open('', '_blank');
      if (!win) return;
      win.document.write(
        '<title>The Apartments Ta\u00e7 \u2014 4+1 Floor Plan</title>' +
        '<style>@page{size:A4;margin:14mm}body{margin:0;font-family:Montserrat,Arial,sans-serif;text-align:center}' +
        'h1{font-size:14px;letter-spacing:.2em;text-transform:uppercase;margin:0 0 4px}' +
        'p{font-size:11px;letter-spacing:.1em;color:#555;margin:0 0 14px}' +
        'img{max-width:100%;max-height:76vh}</style>' +
        '<h1>The Apartments Ta\u00e7 &mdash; 4+1</h1>' +
        '<p>190 m\u00b2 gross &nbsp;&middot;&nbsp; 149 m\u00b2 net &nbsp;&middot;&nbsp; Selami\u00e7e\u015fme, Ba\u011fdat Caddesi</p>' +
        '<img src="' + (plan.currentSrc || plan.src) + '" alt="Floor plan" onload="window.focus();window.print()" />'
      );
      win.document.close();
    });
  }

  /* enquiry form — UI only, same validation pattern as the other project pages */
  const form = document.getElementById('tacEnquireForm');
  const msg = document.getElementById('tacFormMsg');
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
})();
