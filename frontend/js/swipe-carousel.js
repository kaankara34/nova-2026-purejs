/* ================================================================
   NovaSwiper — Instagram-style finger-tracking horizontal carousel
   Physics-based: image follows finger in realtime, snaps to next/prev
   on release using velocity + distance threshold (with spring ease-out).

   Usage:
     const swiper = new NovaSwiper(viewportEl, {
       loop: true,           // wrap around edges (default false)
       threshold: 0.20,      // fraction of viewport width to trigger snap
       ease: 'cubic-bezier(.2,.7,.2,1)',
       duration: 380,        // settle duration ms
       onChange: (i) => {},  // called continuously as index changes
       onSettle: (i) => {}   // called when snap animation completes
     });
     swiper.setIndex(0, { animate: false });
     swiper.next(); swiper.prev(); swiper.goTo(2);
     swiper.getIndex();
     swiper.destroy();

   Expected DOM:
     <div class="viewport">                 <-- receives pointer events
       <div class="nova-track">             <-- data-nova-track element
         <div class="nova-slide">...</div>
         <div class="nova-slide">...</div>
       </div>
     </div>
================================================================ */
(function (root) {
  'use strict';

  function NovaSwiper(viewportEl, opts) {
    this.viewport = viewportEl;
    this.track = viewportEl.querySelector('[data-nova-track]') || viewportEl.firstElementChild;
    this.opts = Object.assign({
      loop: false,             // enable wrap-around by index math (with jump at edges)
      clones: false,           // (loop only) inject cloned slides for a seamless infinite feel
      threshold: 0.20,
      velocityThreshold: 0.35, // px/ms
      ease: 'cubic-bezier(.2,.7,.2,1)',
      duration: 380,
      onChange: null,
      onSettle: null
    }, opts || {});
    // Clones only makes sense when looping
    if (this.opts.clones) this.opts.loop = true;

    this.realSlides = Array.from(this.track.children);
    this.realCount = this.realSlides.length;
    this._injectClones();
    this.slides = Array.from(this.track.children);   // may include clones

    this.currentIdx = 0;         // "internal" index into this.slides
    this.trackW = 0;
    this._dragging = false;
    this._pointerId = null;
    this._startX = 0;
    this._startY = 0;
    this._lastX = 0;
    this._lastT = 0;
    this._velocity = 0;
    this._baseTranslate = 0;
    this._didDrag = false;
    this._axisLocked = null;

    this._onDown = this._onDown.bind(this);
    this._onMove = this._onMove.bind(this);
    this._onUp = this._onUp.bind(this);
    this._onCancel = this._onCancel.bind(this);
    this._onResize = this._onResize.bind(this);
    this._onDragStart = function (e) { e.preventDefault(); };

    this._setupStyles();
    this._bind();
    this._measure();
    // Start on real slide 0 (which is internal index 1 when clones are active)
    this.setIndex(this._realToInternal(0), { animate: false, silent: true });
  }

  /* When clones mode is on, prepend a clone of the last real slide and
     append a clone of the first, so dragging past either edge shows a
     continuous image. After the transition settles on a clone we silently
     jump to the mirrored real slide, giving the "infinite one-direction
     swipe" experience the user expects. */
  NovaSwiper.prototype._injectClones = function () {
    if (!this.opts.clones || this.realCount < 2) return;
    var first = this.realSlides[0].cloneNode(true);
    var last  = this.realSlides[this.realCount - 1].cloneNode(true);
    first.setAttribute('data-clone', 'first');
    last.setAttribute('data-clone', 'last');
    this.track.appendChild(first);
    this.track.insertBefore(last, this.track.firstChild);
  };

  NovaSwiper.prototype._realToInternal = function (realIdx) {
    return this.opts.clones ? realIdx + 1 : realIdx;
  };
  NovaSwiper.prototype._internalToReal = function (internalIdx) {
    if (!this.opts.clones) return internalIdx;
    var n = this.realCount;
    if (internalIdx === 0) return n - 1;      // left clone → last real
    if (internalIdx === n + 1) return 0;      // right clone → first real
    return internalIdx - 1;
  };

  NovaSwiper.prototype._setupStyles = function () {
    // Force horizontal flex track
    this.viewport.style.overflow = 'hidden';
    this.viewport.style.touchAction = 'pan-y';        // let vertical scroll pass, we capture horizontal
    this.viewport.style.userSelect = 'none';
    this.viewport.style.webkitUserSelect = 'none';
    this.viewport.style.cursor = 'grab';
    this.viewport.style.webkitTapHighlightColor = 'transparent';

    this.track.style.display = 'flex';
    this.track.style.flexWrap = 'nowrap';
    this.track.style.willChange = 'transform';
    this.track.style.transform = 'translate3d(0,0,0)';
    this.track.style.transition = 'none';

    this.slides.forEach(function (s) {
      s.style.flex = '0 0 100%';
      s.style.width = '100%';
      s.style.userSelect = 'none';
      s.style.webkitUserSelect = 'none';
      var imgs = s.querySelectorAll('img');
      Array.prototype.forEach.call(imgs, function (im) {
        im.setAttribute('draggable', 'false');
        im.addEventListener('dragstart', function (e) { e.preventDefault(); });
      });
    });
  };

  NovaSwiper.prototype._bind = function () {
    if (!window.PointerEvent) return;
    this.viewport.addEventListener('pointerdown', this._onDown, { passive: false });
    this.viewport.addEventListener('pointermove', this._onMove, { passive: false });
    this.viewport.addEventListener('pointerup', this._onUp);
    this.viewport.addEventListener('pointercancel', this._onCancel);
    // Swallow the synthetic click that follows a drag gesture so callers
    // that listen for click on the viewport (e.g. to open a lightbox) do
    // not fire when the user was actually swiping.
    var self = this;
    this._onClickCapture = function (e) {
      if (self._didDrag) {
        e.preventDefault();
        e.stopPropagation();
        self._didDrag = false;
      }
    };
    this.viewport.addEventListener('click', this._onClickCapture, true);
    window.addEventListener('resize', this._onResize);
  };

  NovaSwiper.prototype._measure = function () {
    this.trackW = this.viewport.getBoundingClientRect().width;
  };

  NovaSwiper.prototype._onResize = function () {
    var wasIdx = this.currentIdx;
    this._measure();
    this.setIndex(wasIdx, { animate: false });
  };

  NovaSwiper.prototype._setTranslate = function (x, animate) {
    var t = this.track;
    t.style.transition = animate
      ? ('transform ' + this.opts.duration + 'ms ' + this.opts.ease)
      : 'none';
    t.style.transform = 'translate3d(' + x + 'px, 0, 0)';
  };

  NovaSwiper.prototype._indexTranslate = function (i) {
    return -i * this.trackW;
  };

  NovaSwiper.prototype.setIndex = function (i, opts) {
    opts = opts || {};
    var len = this.slides.length;
    var animate = opts.animate !== false;

    if (!this.opts.loop) {
      i = Math.max(0, Math.min(len - 1, i));
    } else if (this.opts.clones) {
      // Allow drifting into the clone slots; snap-back happens after settle
      i = Math.max(0, Math.min(len - 1, i));
    } else {
      // Loop by modular arithmetic (produces a visible jump at wrap points).
      i = ((i % len) + len) % len;
    }

    var prev = this.currentIdx;
    this.currentIdx = i;
    this._setTranslate(this._indexTranslate(i), animate);

    var realIdx = this._internalToReal(i);
    var prevReal = this._internalToReal(prev);
    if (typeof this.opts.onChange === 'function' && !opts.silent && prevReal !== realIdx) {
      this.opts.onChange(realIdx);
    }

    var self = this;
    clearTimeout(this._settleT);
    if (animate) {
      this._settleT = setTimeout(function () { self._onSettleEnd(opts); }, this.opts.duration);
    } else {
      // Immediate mode — still normalise clone positions
      this._onSettleEnd(opts);
    }
  };

  /* Called when a transition animation finishes. If we ended on a cloned
     edge slide, silently jump to its real counterpart so the next drag
     continues seamlessly. */
  NovaSwiper.prototype._onSettleEnd = function (opts) {
    opts = opts || {};
    if (this.opts.clones) {
      var n = this.realCount;
      if (this.currentIdx === 0) {                 // left clone → jump to last real
        this.currentIdx = n;
        this._setTranslate(this._indexTranslate(n), false);
      } else if (this.currentIdx === n + 1) {      // right clone → jump to first real
        this.currentIdx = 1;
        this._setTranslate(this._indexTranslate(1), false);
      }
    }
    var realIdx = this._internalToReal(this.currentIdx);
    if (typeof this.opts.onSettle === 'function' && !opts.silent) this.opts.onSettle(realIdx);
  };

  NovaSwiper.prototype.next = function () { this.setIndex(this.currentIdx + 1); };
  NovaSwiper.prototype.prev = function () { this.setIndex(this.currentIdx - 1); };
  NovaSwiper.prototype.goTo = function (realIdx, animate) {
    this.setIndex(this._realToInternal(realIdx), { animate: animate !== false });
  };
  NovaSwiper.prototype.getIndex = function () { return this._internalToReal(this.currentIdx); };
  NovaSwiper.prototype.length = function () { return this.realCount; };

  NovaSwiper.prototype._onDown = function (e) {
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    this._dragging = true;
    this._didDrag = false;
    this._axisLocked = null;
    this._pointerId = e.pointerId;
    this._startX = this._lastX = e.clientX;
    this._startY = e.clientY;
    this._lastT = performance.now();
    this._velocity = 0;
    this._baseTranslate = this._indexTranslate(this.currentIdx);
    this._measure();
    this._setTranslate(this._baseTranslate, false);
    try { this.viewport.setPointerCapture(e.pointerId); } catch (_) { /* noop */ }
    this.viewport.style.cursor = 'grabbing';
  };

  NovaSwiper.prototype._onMove = function (e) {
    if (!this._dragging || e.pointerId !== this._pointerId) return;
    var dx = e.clientX - this._startX;
    var dy = e.clientY - this._startY;

    // Lock the axis on first ~6px of movement
    if (!this._axisLocked) {
      if (Math.abs(dx) < 6 && Math.abs(dy) < 6) return;
      this._axisLocked = Math.abs(dx) > Math.abs(dy) ? 'x' : 'y';
      if (this._axisLocked === 'y') {
        // Give control back to native scroll
        this._dragging = false;
        this._pointerId = null;
        this.viewport.style.cursor = 'grab';
        return;
      }
    }
    if (this._axisLocked !== 'x') return;

    e.preventDefault();
    this._didDrag = true;

    var now = performance.now();
    var dt = Math.max(1, now - this._lastT);
    this._velocity = 0.7 * this._velocity + 0.3 * ((e.clientX - this._lastX) / dt);
    this._lastX = e.clientX;
    this._lastT = now;

    var t = this._baseTranslate + dx;
    // Rubber-band at edges when not looping
    if (!this.opts.loop) {
      var min = this._indexTranslate(this.slides.length - 1);
      var max = 0;
      if (t > max) t = max + (t - max) * 0.35;
      else if (t < min) t = min + (t - min) * 0.35;
    }
    this._setTranslate(t, false);
  };

  NovaSwiper.prototype._onUp = function (e) {
    if (!this._dragging || e.pointerId !== this._pointerId) return;
    this._dragging = false;
    this._pointerId = null;
    this.viewport.style.cursor = 'grab';

    if (!this._didDrag) return; // treat as tap

    var dx = e.clientX - this._startX;
    var w = this.trackW;
    var dir = 0;
    var velThresh = this.opts.velocityThreshold;
    var moved = Math.abs(dx);
    // Strong flick → advance regardless of distance
    if (this._velocity < -velThresh && dx < -10) dir = 1;
    else if (this._velocity > velThresh && dx > 10) dir = -1;
    else if (moved > w * this.opts.threshold) dir = dx < 0 ? 1 : -1;
    else dir = 0;

    var nextIdx = this.currentIdx + dir;
    this.setIndex(nextIdx);
  };

  NovaSwiper.prototype._onCancel = function () {
    if (!this._dragging) return;
    this._dragging = false;
    this._pointerId = null;
    this._didDrag = false;
    this.viewport.style.cursor = 'grab';
    this.setIndex(this.currentIdx);
  };

  NovaSwiper.prototype.destroy = function () {
    if (!window.PointerEvent) return;
    this.viewport.removeEventListener('pointerdown', this._onDown);
    this.viewport.removeEventListener('pointermove', this._onMove);
    this.viewport.removeEventListener('pointerup', this._onUp);
    this.viewport.removeEventListener('pointercancel', this._onCancel);
    if (this._onClickCapture) this.viewport.removeEventListener('click', this._onClickCapture, true);
    window.removeEventListener('resize', this._onResize);
    this.track.style.transition = 'none';
    this.track.style.transform = '';
    this.track.style.willChange = '';
    clearTimeout(this._settleT);
  };

  /**
   * Rebuild the track's slides list (call when slide DOM changes).
   * Preserves the current real index (clamped).
   */
  NovaSwiper.prototype.refresh = function () {
    // Remove any previously injected clones and rebuild fresh
    var clones = this.track.querySelectorAll('[data-clone]');
    Array.prototype.forEach.call(clones, function (c) { c.parentNode.removeChild(c); });
    this.realSlides = Array.from(this.track.children);
    this.realCount = this.realSlides.length;
    this._injectClones();
    this.slides = Array.from(this.track.children);
    this._setupStyles();
    this._measure();
    var realIdx = Math.min(this._internalToReal(this.currentIdx), this.realCount - 1);
    if (realIdx < 0) realIdx = 0;
    this.setIndex(this._realToInternal(realIdx), { animate: false, silent: true });
  };

  root.NovaSwiper = NovaSwiper;
})(window);
