/* js/case-study.js — Wood Fired Designs
   Reads ?slug= from the URL, finds the matching entry in
   window.CASE_STUDIES (data/case-studies.js), and renders
   case-study.html from it. */

(function () {
  'use strict';

  var studies = window.CASE_STUDIES || [];
  var params = new URLSearchParams(window.location.search);
  var slug = params.get('slug');
  var study = studies.find(function (s) { return s.slug === slug; });

  if (!study) {
    window.location.replace('index.html#work');
    return;
  }

  function el(html) {
    var t = document.createElement('template');
    t.innerHTML = html.trim();
    return t.content.firstElementChild;
  }

  function mediaMarkup(media, opts) {
    opts = opts || {};
    var cls = opts.cls || '';
    if (media.type === 'video') {
      return '<video class="' + cls + '" autoplay muted loop playsinline preload="metadata" poster="' + media.poster + '">' +
        '<source src="' + media.src + '" type="video/mp4"></video>';
    }
    return '<img class="' + cls + '" src="' + media.src + '" alt="' + (opts.alt || '') + '" loading="' + (opts.eager ? 'eager' : 'lazy') + '" decoding="async">';
  }

  // ── Document head ──────────────────────────────────────────
  document.title = study.title + ' — Wood Fired Designs';
  var descEl = document.getElementById('cs-doc-desc');
  if (descEl) descEl.setAttribute('content', study.blurb.slice(0, 155));
  var canon = document.getElementById('cs-canonical');
  if (canon) canon.setAttribute('href', 'https://woodfireddesigns.com/case-study.html?slug=' + study.slug);

  // ── Hero ────────────────────────────────────────────────────
  document.getElementById('cs-hero-media').innerHTML =
    mediaMarkup(study.cover, { cls: '', alt: study.title, eager: true });

  document.getElementById('cs-kicker').textContent =
    study.passionProject ? '/ Passion Project' : '/ Case Study';
  document.getElementById('cs-title').textContent = study.title;

  var tagsWrap = document.getElementById('cs-tags');
  (study.tags || []).forEach(function (tag) {
    var span = document.createElement('span');
    span.className = 'cs-tag' + (study.passionProject ? ' cs-tag--passion' : '');
    span.textContent = tag;
    tagsWrap.appendChild(span);
  });

  // ── Disclaimer ──────────────────────────────────────────────
  if (study.passionProject && study.disclaimer) {
    var disc = document.getElementById('cs-disclaimer');
    disc.hidden = false;
    document.getElementById('cs-disclaimer-text').textContent = study.disclaimer;
  }

  // ── Summary ─────────────────────────────────────────────────
  document.getElementById('cs-blurb').textContent = study.blurb;
  document.getElementById('cs-client').textContent = study.client;
  document.getElementById('cs-year').textContent = study.year;

  // ── Gallery ─────────────────────────────────────────────────
  var galleryWrap = document.getElementById('cs-gallery');
  (study.gallery || []).forEach(function (item) {
    var fig = document.createElement('figure');
    fig.className = 'cs-gallery__item';
    fig.innerHTML = mediaMarkup(item, { alt: item.alt || study.title });
    galleryWrap.appendChild(fig);
  });

  // ── More work ───────────────────────────────────────────────
  var moreWrap = document.getElementById('cs-more-grid');
  var others = studies.filter(function (s) { return s.slug !== study.slug; });
  // Shuffle lightly by rotating from current index so it varies per page
  var startIdx = studies.indexOf(study);
  var ordered = others.slice(startIdx).concat(others.slice(0, startIdx));
  ordered.slice(0, 3).forEach(function (s) {
    var card = el(
      '<a class="cs-more__card" href="case-study.html?slug=' + s.slug + '">' +
        '<img src="' + s.cover.poster + '" alt="' + s.title + '" loading="lazy" decoding="async">' +
        '<span class="cs-more__card-label">' + s.title + '</span>' +
      '</a>'
    );
    moreWrap.appendChild(card);
  });
})();
