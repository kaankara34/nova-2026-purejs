/* Shared Register Interest / enquiry submission.
   Wires every form on the page that has fullname + email fields and POSTs it
   to the backend, which persists it and emails iletisim@nova.istanbul. */
(function () {
  'use strict';

  var API = (window.NOVA_API_BASE || '') + '/api/enquiries';

  function findMessageEl(form) {
    var existing = form.querySelector('[data-nova-form-msg]');
    if (existing) return existing;
    var el = document.createElement('p');
    el.setAttribute('data-nova-form-msg', '');
    el.setAttribute('role', 'status');
    el.setAttribute('aria-live', 'polite');
    el.dataset.testid = 'enquiry-form-message';
    form.appendChild(el);
    return el;
  }

  function addHoneypot(form) {
    if (form.querySelector('[name="website"]')) return;
    var hp = document.createElement('input');
    hp.type = 'text';
    hp.name = 'website';
    hp.tabIndex = -1;
    hp.autocomplete = 'off';
    hp.setAttribute('aria-hidden', 'true');
    hp.style.cssText = 'position:absolute;left:-10000px;width:1px;height:1px;opacity:0';
    form.appendChild(hp);
  }

  function value(form, name) {
    var el = form.querySelector('[name="' + name + '"]');
    if (!el) return '';
    if (el.type === 'checkbox') return el.checked;
    return (el.value || '').trim();
  }

  function submitButton(form) {
    return form.querySelector('button[type="submit"], button.submit, button:not([type="button"])');
  }

  function wire(form) {
    if (form.dataset.novaFormWired) return;
    form.dataset.novaFormWired = '1';
    addHoneypot(form);
    var msg = findMessageEl(form);

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var payload = {
        fullname: value(form, 'fullname'),
        email: value(form, 'email'),
        code: value(form, 'code'),
        phone: value(form, 'phone'),
        project: value(form, 'project'),
        source: value(form, 'source'),
        comments: value(form, 'comments'),
        news: !!value(form, 'news'),
        privacy: !!value(form, 'privacy'),
        website: value(form, 'website'),
        page: location.pathname.replace(/^\//, '') || 'index.html'
      };

      if (payload.fullname.length < 2 || !payload.email) {
        msg.dataset.state = 'error';
        msg.textContent = 'Please enter your full name and email address.';
        return;
      }
      if (form.querySelector('[name="privacy"]') && !payload.privacy) {
        msg.dataset.state = 'error';
        msg.textContent = 'Please accept the Privacy Policy to continue.';
        return;
      }

      var btn = submitButton(form);
      var label = btn ? btn.textContent : '';
      if (btn) {
        btn.disabled = true;
        btn.textContent = 'SENDING…';
      }
      msg.dataset.state = 'pending';
      msg.textContent = 'Sending your request…';

      fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(function (res) {
          if (res.ok) {
            msg.dataset.state = 'ok';
            msg.textContent = 'Thank you. Your request has reached our sales team — we will be in touch shortly.';
            form.reset();
          } else if (res.status === 429) {
            msg.dataset.state = 'error';
            msg.textContent = 'Too many submissions from this connection. Please try again in a minute.';
          } else {
            msg.dataset.state = 'error';
            msg.textContent = 'We could not send your request. Please call +90 (533) 506 1972 or email iletisim@nova.istanbul.';
          }
        })
        .catch(function () {
          msg.dataset.state = 'error';
          msg.textContent = 'We could not reach our servers. Please call +90 (533) 506 1972 or email iletisim@nova.istanbul.';
        })
        .then(function () {
          if (btn) {
            btn.disabled = false;
            btn.textContent = label;
          }
        });
    });
  }

  function init() {
    Array.prototype.forEach.call(document.querySelectorAll('form'), function (form) {
      if (form.querySelector('[name="fullname"]') && form.querySelector('[name="email"]')) wire(form);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
