/* Homepage-only, time-limited 29 October campaign modal. */
(function initRepublicDayModal() {
  'use strict';

  const modal = document.querySelector('[data-republic-day-modal]');
  if (!modal) return;

  const sessionKey = 'nova-republic-day-modal-2026-dismissed';
  const previewMode = new URLSearchParams(window.location.search).get('campaign-preview') === '1';
  const exitButton = modal.querySelector('[data-republic-day-exit]');
  const enterButton = modal.querySelector('[data-republic-day-enter]');
  let scrollLocked = false;

  function istanbulDateStamp() {
    const parts = new Intl.DateTimeFormat('en-CA', {
      timeZone: 'Europe/Istanbul', year: 'numeric', month: '2-digit', day: '2-digit'
    }).formatToParts(new Date());
    const value = type => parts.find(part => part.type === type).value;
    return Number(`${value('year')}${value('month')}${value('day')}`);
  }

  function campaignIsLive() {
    const today = istanbulDateStamp();
    return today >= 20261029 && today <= 20261106;
  }

  function wasDismissed() {
    try {
      return window.sessionStorage.getItem(sessionKey) === 'true';
    } catch (_) {
      return false;
    }
  }

  function dismissModal() {
    modal.classList.remove('republic-day-modal--visible');
    modal.setAttribute('aria-hidden', 'true');
    if (scrollLocked && typeof window.unlockScroll === 'function') {
      window.unlockScroll();
      scrollLocked = false;
    }
    try {
      window.sessionStorage.setItem(sessionKey, 'true');
    } catch (_) {
      /* The campaign remains usable if session storage is unavailable. */
    }
    window.setTimeout(() => { modal.hidden = true; }, 360);
  }

  function openModal() {
    modal.hidden = false;
    modal.setAttribute('aria-hidden', 'false');
    if (typeof window.lockScroll === 'function') {
      window.lockScroll();
      scrollLocked = true;
    }
    requestAnimationFrame(() => modal.classList.add('republic-day-modal--visible'));
    enterButton?.focus();
  }

  if (!previewMode && (!campaignIsLive() || wasDismissed())) return;

  exitButton?.addEventListener('click', dismissModal);
  enterButton?.addEventListener('click', dismissModal);
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !modal.hidden) dismissModal();
  });
  openModal();
})();