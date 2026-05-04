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
    document.querySelectorAll(
      '.hero__kicker, .hero__subhead, .hero__ctas, .hero__bottom'
    ).forEach(el => el.classList.add('is-visible'));
    document.querySelectorAll('.hero__headline--echo').forEach(el => {
      el.classList.add('echo-visible');
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

    el.textContent = '';
    // Only set aria-label if the element doesn't already have one
    if (!el.hasAttribute('aria-label')) {
      el.setAttribute('aria-label', rawText);
    }

    words.forEach((word, i) => {
      const outer = document.createElement('span');
      outer.className = 'wr-outer';
      outer.setAttribute('aria-hidden', 'true');

      const inner = document.createElement('span');
      inner.className = 'wr-inner';
      inner.textContent = word;
      // Per-word stagger
      inner.style.transitionDelay = (i * 0.07) + 's';

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
      if (!el.closest('.section-hero')) {
        observer.observe(el);
      }
    });
  }


  // ─── HERO ENTRANCE SEQUENCE ────────────────────────────────────
  /**
   * On page load (not scroll). Sequence:
   *   0.15s — kicker fades in
   *   0.30s — headline words start rising (stagger 0.07s/word)
   *   0.50s — echo headline fades in (opacity 0 → 0.12)
   *   0.95s — subhead fades up (CSS transition-delay handles this)
   *   1.15s — CTAs fade up (CSS transition-delay handles this)
   *   1.40s — bottom labels fade in (CSS transition-delay handles this)
   *
   * The subhead/CTAs/bottom use CSS transition-delay defined in
   * hero.css on their base state — so only .is-visible needs to be
   * added here. No manual setTimeout needed for those elements.
   */

  function triggerHeroReveal() {
    const heroHeadline = document.querySelector('.hero__headline--primary');
    const echoHeadline = document.querySelector('.hero__headline--echo');
    const heroKicker   = document.querySelector('.hero__kicker');
    const heroSubhead  = document.querySelector('.hero__subhead');
    const heroCtas     = document.querySelector('.hero__ctas');
    const heroBottom   = document.querySelector('.hero__bottom');

    // Kicker — fade in first
    if (heroKicker) {
      setTimeout(() => heroKicker.classList.add('is-visible'), 150);
    }

    // Primary headline — offset per-word stagger by 0.3s base delay
    if (heroHeadline) {
      const inners = heroHeadline.querySelectorAll('.wr-inner');
      inners.forEach(inner => {
        const existing = parseFloat(inner.style.transitionDelay) || 0;
        inner.style.transitionDelay = (existing + 0.3) + 's';
      });
      // Single rAF to ensure style is applied before class triggers transition
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          inners.forEach(inner => inner.classList.add('is-visible'));
        });
      });
    }

    // Echo headline
    if (echoHeadline) {
      setTimeout(() => echoHeadline.classList.add('echo-visible'), 500);
    }

    // Subhead, CTAs, bottom — CSS transition-delay on base state
    // handles timing. Just add is-visible and let CSS sequence the rest.
    requestAnimationFrame(() => {
      if (heroSubhead) heroSubhead.classList.add('is-visible');
      if (heroCtas)    heroCtas.classList.add('is-visible');
      if (heroBottom)  heroBottom.classList.add('is-visible');
    });
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
      if (!el.closest('.section-hero')) {
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
