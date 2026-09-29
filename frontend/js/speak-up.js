/* ==========================================================
   NOVA — Speak Up report form

   REPORT_ENDPOINT is the single integration point: set it to the API URL and
   the adapter below posts the report as multipart/form-data. While it is null
   nothing is transmitted, nothing is written to localStorage, sessionStorage
   or the console, and no success state is shown.
   ========================================================== */
(function () {
  'use strict';

  const REPORT_ENDPOINT = null; // set to the API URL once the backend exists
  const NOT_AVAILABLE =
    'Online reporting is temporarily unavailable. Your report has not been sent.';
  const MAX_FILE_BYTES = 10 * 1024 * 1024;
  const ALLOWED = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'];

  const form = document.getElementById('reportFormEl');
  if (!form) return;

  const category = document.getElementById('reportCategory');
  const description = document.getElementById('reportDescription');
  const counter = document.getElementById('reportDescriptionCount');
  const fileInput = document.getElementById('reportFile');
  const fileName = document.getElementById('reportFileName');
  const fileRemove = document.getElementById('reportFileRemove');
  const summary = document.getElementById('reportErrorSummary');
  const result = document.getElementById('reportResult');
  const submitBtn = document.getElementById('reportSubmit');

  /* ---------------------------------------------------------- adapter */
  function collect() {
    const ongoing = form.querySelector('input[name="ongoing"]:checked');
    return {
      category: category.value,
      description: description.value.trim(),
      incidentDate: document.getElementById('reportDate').value,
      location: document.getElementById('reportLocation').value.trim(),
      ongoing: ongoing ? ongoing.value : '',
      involved: document.getElementById('reportInvolved').value.trim(),
      contact: document.getElementById('reportContact').value.trim(),
      attachment: fileInput.files[0] || null
    };
  }

  function submitReport(report) {
    if (!REPORT_ENDPOINT) {
      const err = new Error(NOT_AVAILABLE);
      err.code = 'CHANNEL_NOT_AVAILABLE';
      return Promise.reject(err);
    }
    const body = new FormData();
    Object.keys(report).forEach(function (key) {
      if (key === 'attachment') return;
      if (report[key]) body.append(key, report[key]);
    });
    if (report.attachment) body.append('attachment', report.attachment);
    return fetch(REPORT_ENDPOINT, { method: 'POST', body: body }).then(function (response) {
      if (!response.ok) throw new Error('SUBMIT_FAILED');
      return response.json();
    });
  }

  /* ---------------------------------------------------------- helpers */
  function setError(field, errorId, message) {
    const node = document.getElementById(errorId);
    if (message) {
      field.setAttribute('aria-invalid', 'true');
      field.setAttribute('aria-describedby', errorId);
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

  function fileError() {
    const file = fileInput.files[0];
    if (!file) return '';
    const ext = (file.name.split('.').pop() || '').toLowerCase();
    if (ALLOWED.indexOf(ext) === -1) {
      return 'Please choose a PDF, JPG, PNG, DOC or DOCX file.';
    }
    if (file.size > MAX_FILE_BYTES) {
      return 'The file is larger than 10 MB. Please choose a smaller file.';
    }
    return '';
  }

  function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(0) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  function validate() {
    const errors = [];
    if (!category.value) {
      setError(category, 'reportCategoryError', 'Please choose a category.');
      errors.push({ id: 'reportCategory', message: 'Choose a category for the concern.' });
    } else {
      setError(category, 'reportCategoryError', '');
    }

    const text = description.value.trim();
    if (text.length < 60) {
      setError(description, 'reportDescriptionError',
        'Please describe the concern in at least 60 characters (currently ' + text.length + ').');
      errors.push({ id: 'reportDescription', message: 'Describe the concern in more detail.' });
    } else {
      setError(description, 'reportDescriptionError', '');
    }

    const fileMessage = fileError();
    if (fileMessage) {
      setError(fileInput, 'reportFileError', fileMessage);
      errors.push({ id: 'reportFile', message: fileMessage });
    } else {
      setError(fileInput, 'reportFileError', '');
    }

    showSummary(errors);
    return errors.length === 0;
  }

  /* ---------------------------------------------------------- events */
  function updateCounter() {
    counter.textContent = description.value.length.toLocaleString('en-GB') + ' / 5,000 characters';
  }
  description.addEventListener('input', updateCounter);
  updateCounter();

  fileInput.addEventListener('change', function () {
    const file = fileInput.files[0];
    if (!file) {
      fileName.textContent = 'No file selected';
      fileRemove.hidden = true;
      setError(fileInput, 'reportFileError', '');
      return;
    }
    fileName.textContent = file.name + ' · ' + formatSize(file.size);
    fileRemove.hidden = false;
    setError(fileInput, 'reportFileError', fileError());
  });

  fileRemove.addEventListener('click', function () {
    fileInput.value = '';
    fileName.textContent = 'No file selected';
    fileRemove.hidden = true;
    setError(fileInput, 'reportFileError', '');
    fileInput.focus();
  });

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    if (!validate()) {
      showResult('Please complete the highlighted fields before submitting.', 'error');
      return;
    }
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting…';
    submitReport(collect()).then(function () {
      submitBtn.textContent = 'Submit report';
      submitBtn.disabled = false;
      showResult('Your report has been received.', 'ok');
      form.reset();
      updateCounter();
    }).catch(function (error) {
      submitBtn.textContent = 'Submit report';
      submitBtn.disabled = false;
      showResult(error && error.code === 'CHANNEL_NOT_AVAILABLE'
        ? NOT_AVAILABLE
        : 'The report could not be submitted. Please try again later.',
        'error');
    });
  });
})();
