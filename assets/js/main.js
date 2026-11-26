/* CRISOSA — language, menu, and the quote form.
   No dependencies. Copy lives in data-es / data-en. */
(function () {
  'use strict';

  var EMAIL = 'ventas@crisosa.com';
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  var STORE = 'crisosa-lang';
  var ATTRS = { ph: 'placeholder', alt: 'alt', label: 'aria-label' };

  function setLang(lang) {
    document.documentElement.lang = lang === 'en' ? 'en' : 'es';
    $$('[data-' + lang + ']').forEach(function (el) {
      el.textContent = el.getAttribute('data-' + lang);
    });
    Object.keys(ATTRS).forEach(function (k) {
      $$('[data-' + lang + '-' + k + ']').forEach(function (el) {
        el.setAttribute(ATTRS[k], el.getAttribute('data-' + lang + '-' + k));
      });
    });
    var t = document.body.getAttribute('data-' + lang + '-doctitle');
    if (t) document.title = t;
    var d = document.body.getAttribute('data-' + lang + '-docdesc');
    var meta = $('meta[name="description"]');
    if (d && meta) meta.setAttribute('content', d);
    $$('.lang button').forEach(function (b) {
      var on = b.getAttribute('data-lang') === lang;
      b.classList.toggle('is-on', on);
      b.setAttribute('aria-pressed', String(on));
    });
    try { localStorage.setItem(STORE, lang); } catch (e) {}
  }

  var saved = null;
  try { saved = localStorage.getItem(STORE); } catch (e) {}
  setLang(saved || ((navigator.language || '').toLowerCase().indexOf('es') === 0 ? 'es' : 'en'));
  $$('.lang button').forEach(function (b) {
    b.addEventListener('click', function () { setLang(b.getAttribute('data-lang')); });
  });

  var menu = $('#menu');
  var trig = $('#mtrig');
  function closeMenu() {
    if (!menu || !trig) return;
    menu.hidden = true;
    trig.setAttribute('aria-expanded', 'false');
  }
  if (menu && trig) {
    trig.addEventListener('click', function () {
      var open = trig.getAttribute('aria-expanded') === 'true';
      menu.hidden = open;
      trig.setAttribute('aria-expanded', String(!open));
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeMenu();
    });
    menu.addEventListener('click', function (e) {
      if (e.target.closest('a')) closeMenu();
    });
  }

  var params = new URLSearchParams(location.search);
  var servicio = params.get('servicio');
  $$('form.quote-form').forEach(function (form) {
    var sel = $('select[name="service"]', form);
    if (servicio && sel && sel.querySelector('option[value="' + servicio + '"]')) sel.value = servicio;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var fd = new FormData(form);
      var lang = document.documentElement.lang === 'en' ? 'en' : 'es';
      var label = sel && sel.selectedOptions.length ? sel.selectedOptions[0].textContent.trim() : (fd.get('service') || '');
      var rows = lang === 'en'
        ? ['Company: ' + (fd.get('company') || ''), 'Contact: ' + (fd.get('name') || ''), 'Email: ' + (fd.get('email') || ''), 'Phone: ' + (fd.get('phone') || ''), 'Service: ' + label, 'm² / pallets / volume: ' + (fd.get('volume') || ''), '', String(fd.get('message') || '')]
        : ['Empresa: ' + (fd.get('company') || ''), 'Contacto: ' + (fd.get('name') || ''), 'Correo: ' + (fd.get('email') || ''), 'Teléfono: ' + (fd.get('phone') || ''), 'Servicio: ' + label, 'm² / tarimas / volumen: ' + (fd.get('volume') || ''), '', String(fd.get('message') || '')];
      var subject = (lang === 'en' ? 'Quote request — ' : 'Solicitud de cotización — ') + label + ' — ' + (fd.get('company') || '');
      var status = $('.form__status', form);
      if (status) status.hidden = false;
      window.location.href = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(rows.join('\n'));
    });
  });

  var yr = $('#yr');
  if (yr) yr.textContent = String(new Date().getFullYear());

  window.CRISOSA = { setLang: setLang };
})();
