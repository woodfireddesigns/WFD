/* js/reveals.js — Wood Fired Designs — woodfireddesigns.com */

/**
 * reveals.js
 * Word reveal system + scroll animation engine.
 * No dependencies. Vanilla JS only.
 */

(function () {
  'use strict';

  // ─── REDUCED MOTION ─────────────────────────────────────────────
  const prefersReducedMotion = window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  ).matches;

  if (prefersReducedMotion) {
    // Show everything immediately and bail
    document.querySelectorAll('.scroll-reveal').forEach(el => {
      el.classList.add('is-visible');
    });
    document.querySelectorAll('.word-reveal').forEach(el => {
      // Leave text intact — no splitting, no animation
      el.querySelectorAll('.wr-inner').forEach(i => i.classList.add('is-visible'));
    });
    return;
  }


  // ─── WORD REVEAL SYSTEM ─────────────────────────────────────────
  /**
   * Splits .word-reveal elements into per-word spans.
   * Each word: <span class="wr-outer"><span class="wr-inner">word</span></span>
   * Outer: overflow hidden. Inner: starts translateY(110%), rises to 0.
   * Stagger: 0.07s per word index.
   * data-reveal-offset: base delay added on top of per-word stagger.
   * aria-label set on parent so screen readers read original text.
   */

  function buildWordReveal(el) {
    const rawText = el.textContent.trim();
    if (!rawText) return;

    const words = rawText.split(/\s+/);
    const isFire = el.classList.contains('word-reveal--fire');
    const stagger = isFire ? 0.10 : 0.07;

    el.textContent = '';
    // Only set aria-label if the element doesn't already have one
    if (!el.hasAttribute('aria-label')) {
      el.setAttribute('aria-label', rawText);
    }

    // For fire variant, accent the last N words by marking their outers
    const accentFrom = isFire ? el.dataset.accentFrom : null;
    const accentIndex = accentFrom != null
      ? parseInt(accentFrom, 10)
      : (isFire ? Math.ceil(words.length / 2) : -1);

    words.forEach((word, i) => {
      const outer = document.createElement('span');
      outer.className = 'wr-outer';
      outer.setAttribute('aria-hidden', 'true');
      if (isFire && i >= accentIndex) {
        outer.classList.add('wr-outer--accent');
      }

      const inner = document.createElement('span');
      inner.className = 'wr-inner';
      inner.textContent = word;
      // Per-word stagger
      inner.style.transitionDelay = (i * stagger) + 's';

      outer.appendChild(inner);
      el.appendChild(outer);

      if (i < words.length - 1) {
        el.appendChild(document.createTextNode(' '));
      }
    });
  }

  function initWordReveals() {
    document.querySelectorAll('.word-reveal').forEach(buildWordReveal);
  }


  // ─── WORD REVEAL OBSERVER ───────────────────────────────────────
  /**
   * Observes each .word-reveal element.
   * On viewport entry: adds .is-visible to all .wr-inner children.
   * Supports data-reveal-offset="N" to delay entire element's words
   * by N seconds on top of per-word stagger — used for multi-line
   * reveals (e.g. manifesto second line).
   * Hero headline is excluded — triggered separately on load.
   */

  function observeWordReveals() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;

          const el = entry.target;
          const baseOffset = parseFloat(el.dataset.revealOffset) || 0;
          const inners = el.querySelectorAll('.wr-inner');

          inners.forEach(inner => {
            if (baseOffset > 0) {
              const existing = parseFloat(inner.style.transitionDelay) || 0;
              inner.style.transitionDelay = (existing + baseOffset) + 's';
            }
            inner.classList.add('is-visible');
          });

          observer.unobserve(el);
        });
      },
      { threshold: 0.15, rootMargin: '0px 0px -8% 0px' }
    );

    // Observe all word-reveals EXCEPT the hero primary headline (load-triggered)
    document.querySelectorAll('.word-reveal').forEach(el => {
      if (!el.closest('.hero-seq')) {
        observer.observe(el);
      }
    });
  }


  function triggerHeroReveal() {
    // Hero sequence panels are controlled by GSAP in scroll-sequence.js.
    // Nothing to trigger here — scroll-sequence.js handles panel visibility.
  }


  // ─── SCROLL REVEAL ──────────────────────────────────────────────
  /**
   * .scroll-reveal elements: opacity 0, translateY(space-lg) in base.css
   * IntersectionObserver adds .is-visible.
   * .stagger-group children get increasing transition-delay via JS.
   * Hero elements excluded — they use the hero entrance sequence above.
   */

  function applyStaggerDelays() {
    document.querySelectorAll('.stagger-group').forEach(group => {
      group.querySelectorAll('.scroll-reveal').forEach((child, i) => {
        child.style.transitionDelay = (i * 0.08) + 's';
      });
    });
  }

  function observeScrollReveals() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -8% 0px' }
    );

    document.querySelectorAll('.scroll-reveal').forEach(el => {
      // Skip any element inside the hero — those animate on load
      if (!el.closest('.hero-seq')) {
        observer.observe(el);
      }
    });
  }


  // ─── INIT ────────────────────────────────────────────────────────

  function init() {
    initWordReveals();       // Build word spans first
    applyStaggerDelays();    // Set stagger delays on stagger groups
    observeWordReveals();    // Watch scroll-based word reveals
    observeScrollReveals();  // Watch general scroll reveals
    triggerHeroReveal();     // Fire hero sequence immediately
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
