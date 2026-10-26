/* Pointer gestures only. Navigation and language URLs belong to the controller. */
export function bindLanguageGesture(button, actions) {
  let pointer = null;
  let suppressClickUntil = 0;
  const clamp = value => Math.min(1, Math.max(0, value));

  function endCapture() {
    const id = pointer?.id;
    pointer = null;
    button.classList.remove('is-dragging');
    if (id !== undefined && button.hasPointerCapture(id)) button.releasePointerCapture(id);
  }

  function cancel() {
    if (pointer) suppressClickUntil = performance.now() + 500;
    endCapture();
    actions.cancel();
  }

  button.addEventListener('pointerdown', event => {
    if (!event.isPrimary || event.button !== 0 || !actions.canStart()) return;
    const rail = button.querySelector('.lang-rail').getBoundingClientRect();
    const knob = button.querySelector('.lang-knob').getBoundingClientRect();
    pointer = { id: event.pointerId, x: event.clientX, y: event.clientY,
      start: actions.position(), progress: actions.position(), travel: rail.width - knob.width - 4,
      moved: false };
    button.setPointerCapture(event.pointerId);
  });

  button.addEventListener('pointermove', event => {
    if (!pointer || event.pointerId !== pointer.id) return;
    const dx = event.clientX - pointer.x;
    const dy = event.clientY - pointer.y;
    if (!pointer.moved && Math.abs(dy) > Math.abs(dx) && Math.abs(dy) > 6) {
      cancel(); // Vertical touch scrolling belongs to the page, not the switch.
      return;
    }
    if (Math.abs(dx) >= 4) pointer.moved = true;
    if (!pointer.moved) return;
    event.preventDefault();
    pointer.progress = clamp(pointer.start + dx / pointer.travel);
    button.classList.add('is-dragging');
    actions.preview(pointer.progress);
  });

  button.addEventListener('pointerup', event => {
    if (!pointer || event.pointerId !== pointer.id) return;
    const gesture = pointer;
    endCapture();
    if (!gesture.moved) return; // Native click (including keyboard click) handles a tap.
    suppressClickUntil = performance.now() + 500;
    // Always settle to the nearest endpoint, independent of drag speed.
    const progress = clamp(gesture.start + (event.clientX - gesture.x) / gesture.travel);
    actions.commit(progress >= .5 ? 1 : 0);
  });

  button.addEventListener('click', event => {
    if (event.detail > 0 && performance.now() < suppressClickUntil) {
      event.preventDefault();
      return;
    }
    if (actions.canStart()) actions.tap();
  });
  button.addEventListener('pointercancel', cancel);
  button.addEventListener('lostpointercapture', () => { if (pointer) cancel(); });
  button.addEventListener('keydown', event => {
    if (event.key === 'Escape') cancel();
  });
  window.addEventListener('blur', cancel);
  window.addEventListener('resize', () => { if (pointer) cancel(); });
  return cancel;
}