/* js/scroll-sequence.js — Wood Fired Designs — woodfireddesigns.com
   ─────────────────────────────────────────────────────────────
   Three-panel scroll sequence. The .hero-seq is CSS-sticky to
   the top; .hero-seq-scroll provides 300vh of scroll distance.
   GSAP ScrollTrigger scrubs a timeline that crossfades panels.
   ───────────────────────────────────────────────────────────── */

(function () {
  'use strict';

  /* Wait for GSAP (deferred) + DOM */
  function ready(fn) {
    if (document.readyState !== 'loading') {
      window.requestAnimationFrame(fn);
    } else {
      document.addEventListener('DOMContentLoaded', fn);
    }
  }

  ready(function () {
    /* Bail if GSAP / ScrollTrigger not available */
    if (!window.gsap || !window.ScrollTrigger) {
      console.warn('[scroll-sequence] GSAP or ScrollTrigger not found.');
      return;
    }

    gsap.registerPlugin(ScrollTrigger);

    const scroll  = document.querySelector('.hero-seq-scroll');
    const p1      = document.getElementById('seq-p1');
    const p2      = document.getElementById('seq-p2');
    const p3      = document.getElementById('seq-p3');
    const seq     = document.getElementById('hero-sequence');
    const dots    = document.querySelectorAll('.hero-seq__dot');

    if (!scroll || !p1 || !p2 || !p3) return;

    /* ── Initial states ─────────────────────────────────────── */
    gsap.set(p1, { opacity: 1, y: 0 });
    gsap.set(p2, { opacity: 0, y: 60 });
    gsap.set(p3, { opacity: 0, y: 60 });

    /* ── Dot helper ─────────────────────────────────────────── */
    function setDot(index) {
      dots.forEach(function (d, i) {
        d.classList.toggle('is-active', i === index);
      });
      if (seq) seq.classList.toggle('at-panel-3', index === 2);
    }

    /* ── GSAP timeline scrubbed to scroll ───────────────────── */
    /* Total timeline units: 1 hold + 0.6 transition × 2 + 1 hold × 2 = ~4.2
       ScrollTrigger maps start→end onto 0→1 progress.          */

    const HOLD     = 1;    /* pause duration per panel */
    const FADE_OUT = 0.45; /* panel exit duration */
    const FADE_IN  = 0.45; /* panel enter duration */
    const OVERLAP  = 0.1;  /* how much enter overlaps exit */

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: scroll,
        start: 'top top',
        end:   'bottom bottom',
        scrub: 1.4,          /* higher = smoother scrub lag */
        onUpdate: function (self) {
          const p = self.progress;
          if      (p < 0.35) setDot(0);
          else if (p < 0.70) setDot(1);
          else               setDot(2);
        },
      },
    });

    tl
      /* ── Hold panel 1 ──────────────────────────────────── */
      .to({}, { duration: HOLD })

      /* ── P1 → P2 ────────────────────────────────────────── */
      .to(p1, {
        opacity: 0,
        y: -60,
        duration: FADE_OUT,
        ease: 'power2.in',
      })
      .fromTo(p2,
        { opacity: 0, y: 60 },
        { opacity: 1, y: 0, duration: FADE_IN, ease: 'power2.out' },
        '<' + OVERLAP
      )

      /* ── Hold panel 2 ──────────────────────────────────── */
      .to({}, { duration: HOLD })

      /* ── P2 → P3 ────────────────────────────────────────── */
      .to(p2, {
        opacity: 0,
        y: -60,
        duration: FADE_OUT,
        ease: 'power2.in',
      })
      .fromTo(p3,
        { opacity: 0, y: 60 },
        { opacity: 1, y: 0, duration: FADE_IN, ease: 'power2.out' },
        '<' + OVERLAP
      )

      /* ── Hold panel 3 ──────────────────────────────────── */
      .to({}, { duration: HOLD });

    /* ── Stat counter animation (panel 3) ───────────────────── */
    /* Fires once when panel 3 scrolls into view.              */
    const statEls = document.querySelectorAll('.hero-seq__stat-num[data-target]');

    if (statEls.length) {
      ScrollTrigger.create({
        trigger: scroll,
        start: 'bottom 120%', /* roughly when panel 3 becomes active */
        once: true,
        onEnter: function () {
          statEls.forEach(function (el, i) {
            const target = parseFloat(el.dataset.target) || 0;
            gsap.fromTo(
              el,
              { innerText: 0 },
              {
                innerText: target,
                duration: 1.8,
                delay: i * 0.15,
                ease: 'power2.out',
                snap: { innerText: 1 },
                onUpdate: function () {
                  el.textContent = Math.round(parseFloat(el.textContent));
                },
              }
            );
          });
        },
      });
    }
  });
})();
