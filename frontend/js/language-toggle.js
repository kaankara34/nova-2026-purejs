import { bindLanguageGesture } from './language-toggle-gesture.js';

/* Native anchors are the single URL authority; never reconstruct a language path. */
export function initLanguageToggles() {
  document.querySelectorAll('[data-language-toggle="slide-v2"]').forEach(control => {
    const button = control.querySelector('.lang-toggle');
    const links = ['tr', 'en'].map(lang => control.querySelector(`.lang-opt[lang="${lang}"]`));
    const current = control.dataset.language === 'en' ? 1 : 0;
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    let pending = false;
    let navigationTimer;

    function paint(progress) {
      control.style.setProperty('--lang-progress', progress);
    }

    function restore() {
      clearTimeout(navigationTimer);
      pending = false;
      paint(current);
      control.dataset.flagLanguage = current ? 'en' : 'tr';
      button.setAttribute('aria-checked', String(Boolean(current)));
      button.removeAttribute('aria-busy');
    }

    function commit(target) {
      if (pending) return;
      paint(target);
      control.dataset.flagLanguage = target ? 'en' : 'tr';
      if (target === current) return;
      pending = true;
      button.setAttribute('aria-checked', String(Boolean(target)));
      button.setAttribute('aria-busy', 'true');
      // Settle the physical switch after release, then use the existing exact destination.
      navigationTimer = setTimeout(() => window.location.assign(links[target].href),
        reducedMotion.matches ? 0 : 240);
    }

    const cancelGesture = bindLanguageGesture(button, {
      canStart: () => !pending,
      position: () => current,
      preview: paint,
      commit,
      cancel: restore,
      tap: () => commit(1 - current)
    });
    button.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      commit(['ArrowRight', 'End'].includes(event.key) ? 1 : 0);
    });
    // Labels keep native clicks, Ctrl/Cmd-click, link copying and no-JS navigation.
    links.forEach(link => link.addEventListener('click', () => cancelGesture()));
    window.addEventListener('pagehide', () => clearTimeout(navigationTimer));
    window.addEventListener('pageshow', () => { cancelGesture(); restore(); });
    button.disabled = false;
    restore();
  });
}