/* ==========================================================
   NOVA — Careers application form

   APPLICATION_ENDPOINT is the single integration point: set it to the API URL
   and the adapter below posts the application and CV as multipart/form-data.
   While it is null nothing is transmitted, nothing is written to browser
   storage and no success state is shown.
   ========================================================== */
(function () {
  'use strict';

  const APPLICATION_ENDPOINT = null; // set to the API URL once the backend exists
  const NOT_AVAILABLE =
    'Online submission is temporarily unavailable. Your application has not been sent. Please apply by email.';
  const MAX_CV_BYTES = 10 * 1024 * 1024;
  const ALLOWED = ['pdf', 'doc', 'docx'];

  const form = document.getElementById('careersFormEl');
  if (!form) return;

  const fields = {
    fullName: document.getElementById('appName'),
    email: document.getElementById('appEmail'),
    phone: document.getElementById('appPhone'),
    city: document.getElementById('appCity'),
    years: document.getElementById('appYears'),
    experience: document.getElementById('appExperience'),
    privacy: document.getElementById('appPrivacy')
  };
  const cvInput = document.getElementById('appCv');
  const cvName = document.getElementById('appCvName');
  const cvRemove = document.getElementById('appCvRemove');
  const counter = document.getElementById('appExperienceCount');
  const summary = document.getElementById('careersErrorSummary');
  const result = document.getElementById('careersResult');
  const submitBtn = document.getElementById('careersSubmit');

  /* ---------------------------------------------------------- adapter */
  function collect() {
    return {
      fullName: fields.fullName.value.trim(),
      email: fields.email.value.trim(),
      phone: fields.phone.value.trim(),
      city: fields.city.value.trim(),
      position: document.getElementById('appPosition').value,
      years: fields.years.value,
      experience: fields.experience.value.trim(),
      cv: cvInput.files[0] || null
    };
  }

  function submitApplication(application) {
    if (!APPLICATION_ENDPOINT) {
      const err = new Error(NOT_AVAILABLE);
      err.code = 'APPLICATIONS_NOT_AVAILABLE';
      return Promise.reject(err);
    }
    const body = new FormData();
    Object.keys(application).forEach(function (key) {
      if (key === 'cv') return;
      if (application[key]) body.append(key, application[key]);
    });
    if (application.cv) body.append('cv', application.cv);
    return fetch(APPLICATION_ENDPOINT, { method: 'POST', body: body }).then(function (response) {
      if (!response.ok) throw new Error('SUBMIT_FAILED');
      return response.json();
    });
  }

  /* ---------------------------------------------------------- helpers */
  function setError(field, errorId, message) {
    const node = document.getElementById(errorId);
    if (message) {
      field.setAttribute('aria-invalid', 'true');
      node.textContent = message;
      node.hidden = false;
    } else {
      field.removeAttribute('aria-invalid');
      node.textContent = '';
      node.hidden = true;
    }
  }

  function showSummary(errors) {
    summary.textContent = '';
    if (!errors.length) {
      summary.hidden = true;
      return;
    }
    const title = document.createElement('h3');
    title.textContent = errors.length === 1
      ? 'One field needs your attention'
      : errors.length + ' fields need your attention';
    const list = document.createElement('ul');
    errors.forEach(function (item) {
      const li = document.createElement('li');
      const link = document.createElement('a');
      link.href = '#' + item.id;
      link.textContent = item.message;
      link.addEventListener('click', function (event) {
        event.preventDefault();
        document.getElementById(item.id).focus();
      });
      li.appendChild(link);
      list.appendChild(li);
    });
    summary.appendChild(title);
    summary.appendChild(list);
    summary.hidden = false;
    summary.focus();
  }

  function showResult(message, state) {
    result.textContent = message;
    result.className = 'form-result' + (state ? ' is-' + state : '');
    result.hidden = false;
  }

  function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(0) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  function cvError() {
    const file = cvInput.files[0];
    if (!file) return 'Please attach your CV as a PDF, DOC or DOCX file.';
    const ext = (file.name.split('.').pop() || '').toLowerCase();
    if (ALLOWED.indexOf(ext) === -1) return 'Please choose a PDF, DOC or DOCX file.';
    if (file.size > MAX_CV_BYTES) return 'The file is larger than 10 MB. Please choose a smaller file.';
    return '';
  }

  function validate() {
    const errors = [];
    const check = function (field, errorId, message, summaryText, valid) {
      if (!valid) {
        setError(field, errorId, message);
        errors.push({ id: field.id, message: summaryText });
      } else {
        setError(field, errorId, '');
      }
    };

    check(fields.fullName, 'appNameError', 'Please enter your full name.',
      'Enter your full name.', fields.fullName.value.trim().length >= 3);
    check(fields.email, 'appEmailError', 'Please enter a valid e-mail address.',
      'Enter a valid e-mail address.', /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(fields.email.value.trim()));
    check(fields.phone, 'appPhoneError', 'Please enter a telephone number we can reach you on.',
      'Enter your telephone number.', fields.phone.value.replace(/[^0-9]/g, '').length >= 7);
    check(fields.city, 'appCityError', 'Please enter the city you live in.',
      'Enter your city.', fields.city.value.trim().length >= 2);

    const years = Number(fields.years.value);
    check(fields.years, 'appYearsError', 'Please enter your years of active site experience (0–60).',
      'Enter your years of site experience.',
      fields.years.value !== '' && !Number.isNaN(years) && years >= 0 && years <= 60);

    const experience = fields.experience.value.trim();
    check(fields.experience, 'appExperienceError',
      'Please describe your relevant projects in at least 80 characters (currently ' + experience.length + ').',
      'Describe your relevant projects and responsibilities.', experience.length >= 80);

    const cvMessage = cvError();
    if (cvMessage) {
      setError(cvInput, 'appCvError', cvMessage);
      errors.push({ id: 'appCv', message: cvMessage });
    } else {
      setError(cvInput, 'appCvError', '');
    }

    check(fields.privacy, 'appPrivacyError',
      'Please confirm that you have read the Applicant Privacy Notice.',
      'Confirm that you have read the Applicant Privacy Notice.', fields.privacy.checked);

    showSummary(errors);
    return errors.length === 0;
  }

  /* ---------------------------------------------------------- events */
  function updateCounter() {
    counter.textContent = fields.experience.value.length.toLocaleString('en-GB') + ' / 2,000 characters';
  }
  fields.experience.addEventListener('input', updateCounter);
  updateCounter();

  cvInput.addEventListener('change', function () {
    const file = cvInput.files[0];
    if (!file) {
      cvName.textContent = 'No file selected';
      cvRemove.hidden = true;
      return;
    }
    cvName.textContent = file.name + ' · ' + formatSize(file.size);
    cvRemove.hidden = false;
    const message = cvError();
    setError(cvInput, 'appCvError', message === 'Please attach your CV as a PDF, DOC or DOCX file.' ? '' : message);
  });

  cvRemove.addEventListener('click', function () {
    cvInput.value = '';
    cvName.textContent = 'No file selected';
    cvRemove.hidden = true;
    setError(cvInput, 'appCvError', '');
    cvInput.focus();
  });

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    if (!validate()) {
      showResult('Please complete the highlighted fields before submitting.', 'error');
      return;
    }
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting…';
    submitApplication(collect()).then(function () {
      submitBtn.textContent = 'Submit application';
      submitBtn.disabled = false;
      showResult('Your application has been received.', 'ok');
      form.reset();
      cvName.textContent = 'No file selected';
      cvRemove.hidden = true;
      updateCounter();
    }).catch(function (error) {
      submitBtn.textContent = 'Submit application';
      submitBtn.disabled = false;
      showResult(error && error.code === 'APPLICATIONS_NOT_AVAILABLE'
        ? NOT_AVAILABLE
        : 'The application could not be submitted. Please try again later or apply by email.',
        'error');
    });
  });
})();
