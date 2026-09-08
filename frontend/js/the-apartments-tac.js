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
    L.marker([lat, lng], {
      icon: L.divIcon({ className: 'tac-map-pin', iconSize: [18, 18], iconAnchor: [9, 9] }),
      title: 'The Apartments Taç'
    }).addTo(map);
    map.fitBounds(bounds);
  }

  /* floor plan: 3+1 / 4+1 tabs — the left half of the drawing is the 3+1
     residence, the right half the 4+1; the inactive side is dimmed. */
  const PLANS = {
    '3+1': {
      gross: '155 m²',
      net: '127 m²',
      rooms: [
        ['Living Room', '39.33 m²'],
        ['Master Bedroom', '20.22 m²'],
        ['Bedroom', '12.05 m²'],
        ['Bedroom', '11.84 m²'],
        ['Kitchen', '13.29 m²'],
        ['Balcony', '7.11 m²']
      ],
      copy: 'At 127 m² net, the 3+1 plan keeps the same generous living room and master suite, with two further bedrooms organised off a clear circulation core.'
    },
    '4+1': {
      gross: '190 m²',
      net: '149 m²',
      rooms: [
        ['Living Room', '39.33 m²'],
        ['Master Bedroom', '20.22 m²'],
        ['Bedroom', '12.05 m²'],
        ['Bedroom', '11.84 m²'],
        ['Bedroom', '9.86 m²'],
        ['Kitchen', '13.29 m²'],
        ['Balcony', '7.11 m²']
      ],
      copy: 'At 149 m² net, the plan provides the dimensions required for a genuine 4+1 residence. Living, private and service areas are organised through clear circulation, allowing the scale of the home to remain useful rather than merely numerical.'
    }
  };
  const panel = document.getElementById('tacPlanPanel');
  const tabs = [...document.querySelectorAll('.tac-plans-tab[data-plan]')];
  const rowsEl = document.getElementById('tacPlanRows');
  const titleEl = document.getElementById('tacPlanTitle');
  const copyEl = document.getElementById('tacPlanCopy');
  if (panel && tabs.length && rowsEl && titleEl && copyEl) {
    const render = key => {
      const data = PLANS[key];
      panel.dataset.active = key;
      panel.setAttribute('aria-labelledby', key === '3+1' ? 'tacTab3' : 'tacTab4');
      titleEl.textContent = key;
      copyEl.textContent = data.copy;
      rowsEl.innerHTML =
        '<div class="tac-plans-row tac-plans-row--total"><span>Gross Area</span>' +
        '<span class="tac-plans-val">' + data.gross + '</span></div>' +
        '<div class="tac-plans-row"><span>Net Area</span>' +
        '<span class="tac-plans-val">' + data.net + '</span></div>' +
        data.rooms.map((r, n) =>
          '<div class="tac-plans-row"><span><em>' + (n + 1) + '.</em> ' + r[0] + '</span>' +
          '<span class="tac-plans-val">' + r[1] + '</span></div>').join('');
      tabs.forEach(t => {
        const on = t.dataset.plan === key;
        t.classList.toggle('active', on);
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
      });
      if (plan) plan.alt = 'The Apartments Taç — ' + key + ' residence floor plan';
    };
    tabs.forEach((t, i) => {
      t.addEventListener('click', () => render(t.dataset.plan));
      t.addEventListener('keydown', e => {
        if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
        e.preventDefault();
        const next = tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
        render(next.dataset.plan);
        next.focus();
      });
    });
    render('4+1');
  }

  /* floor plan: print sheet */
  const printBtn = document.getElementById('tacPlansPrint');
  if (printBtn && plan) {
    printBtn.addEventListener('click', () => {
      const win = open('', '_blank');
      if (!win) return;
      const key = (panel && panel.dataset.active) || '4+1';
      const d = PLANS[key];
      win.document.write(
        '<title>The Apartments Ta\u00e7 \u2014 4+1 Floor Plan</title>' +
        '<style>@page{size:A4;margin:14mm}body{margin:0;font-family:Montserrat,Arial,sans-serif;text-align:center}' +
        'h1{font-size:14px;letter-spacing:.2em;text-transform:uppercase;margin:0 0 4px}' +
        'p{font-size:11px;letter-spacing:.1em;color:#555;margin:0 0 14px}' +
        'img{max-width:100%;max-height:76vh}</style>' +
        '<h1>The Apartments Ta\u00e7 &mdash; ' + key + '</h1>' +
        '<p>' + d.gross + ' gross &nbsp;&middot;&nbsp; ' + d.net + ' net &nbsp;&middot;&nbsp; Selami\u00e7e\u015fme, Ba\u011fdat Caddesi</p>' +
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
