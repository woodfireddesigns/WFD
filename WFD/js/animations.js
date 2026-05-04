/* js/animations.js — Wood Fired Designs — woodfireddesigns.com */

/**
 * animations.js
 * Responsibilities:
 *   1. Custom cursor (ring + dot, GSAP-powered, desktop only)
 *   2. Hero video parallax (ScrollTrigger scrub)
 *   3. Services rows stagger entrance
 *   4. Proof cards stagger entrance
 *   5. About stats stagger entrance
 *   6. Process steps stagger entrance (slide from right)
 * Requires: GSAP + ScrollTrigger (loaded via CDN before this file)
 */

(function () {
  'use strict';

  // Guard: GSAP must be loaded
  if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;

  gsap.registerPlugin(ScrollTrigger);

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isMobile = window.innerWidth < 768;

  // Refresh ScrollTrigger positions after fonts load
  document.fonts.ready.then(() => ScrollTrigger.refresh());


  // ─── 1. CUSTOM CURSOR ─────────────────────────────────────────
  /*
   * Outer ring tracks with ease — creates a satisfying lag.
   * Inner dot snaps instantly.
   * Both fade in on first mouse move.
   * Scales up 2× on hover over interactive elements.
   * Disabled on mobile (CSS hides elements, JS skips logic).
   */

  if (!isMobile) {
    const cursor    = document.querySelector('.custom-cursor');
    const cursorDot = document.querySelector('.custom-cursor-dot');

    if (cursor && cursorDot) {
      // Animate ring position with lag, dot immediately
      window.addEventListener('mousemove', e => {
        gsap.to(cursor,    { x: e.clientX, y: e.clientY, duration: 0.5, ease: 'power2.out' });
        gsap.to(cursorDot, { x: e.clientX, y: e.clientY, duration: 0.08 });
      });

      // Reveal on first move
      window.addEventListener('mousemove', () => {
        cursor.classList.add('is-active');
        cursorDot.classList.add('is-active');
      }, { once: true });

      // Scale ring on interactive elements
      const interactives = document.querySelectorAll('a, button, .work-row, .services__row, [tabindex="0"]');
      interactives.forEach(el => {
        el.addEventListener('mouseenter', () => {
          gsap.to(cursor, { scale: 2.2, duration: 0.3, ease: 'power2.out' });
        });
        el.addEventListener('mouseleave', () => {
          gsap.to(cursor, { scale: 1, duration: 0.3, ease: 'power2.out' });
        });
      });

      // Hide cursor when leaving window
      document.addEventListener('mouseleave', () => {
        gsap.to([cursor, cursorDot], { opacity: 0, duration: 0.2 });
      });
      document.addEventListener('mouseenter', () => {
        gsap.to([cursor, cursorDot], { opacity: 1, duration: 0.2 });
      });
    }
  }

  // Early exit if user prefers reduced motion — cursor still works, animations skip
  if (prefersReducedMotion) return;


  // ─── 2. HERO VIDEO PARALLAX ───────────────────────────────────
  /*
   * Video wrap moves up at 20% of scroll speed — fire breathes
   * as content scrolls over it, creating cinematic depth.
   */

  const heroVideoWrap = document.querySelector('.hero__video-wrap');
  if (heroVideoWrap) {
    gsap.to(heroVideoWrap, {
      yPercent: -20,
      ease: 'none',
      scrollTrigger: {
        trigger: '#hero',
        start: 'top top',
        end: 'bottom top',
        scrub: true
      }
    });
  }


  // ─── 3. SERVICES ROWS STAGGER ─────────────────────────────────
  /*
   * Rows slide in from left with a stagger — each one landing
   * with authority. Cinematic row-by-row entrance.
   */

  const serviceRows = document.querySelectorAll('.services__row');
  if (serviceRows.length) {
    gsap.fromTo(serviceRows,
      { opacity: 0, x: -40 },
      {
        opacity: 1,
        x: 0,
        duration: 0.65,
        stagger: 0.09,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: '.services__list',
          start: 'top 82%'
        }
      }
    );
  }


  // ─── 4. PROOF CARDS STAGGER ───────────────────────────────────
  /*
   * Cards rise up in stagger — each testimonial landing
   * with deliberate weight.
   */

  const proofCards = document.querySelectorAll('.proof__card');
  if (proofCards.length) {
    gsap.fromTo(proofCards,
      { opacity: 0, y: 60 },
      {
        opacity: 1,
        y: 0,
        duration: 0.85,
        stagger: 0.15,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: '.proof__cards',
          start: 'top 80%'
        }
      }
    );
  }


  // ─── 5. ABOUT STATS STAGGER ───────────────────────────────────
  /*
   * Stats pop in with a short stagger — numbers feel earned.
   */

  const aboutStats = document.querySelectorAll('.about__stat');
  if (aboutStats.length) {
    gsap.fromTo(aboutStats,
      { opacity: 0, y: 30 },
      {
        opacity: 1,
        y: 0,
        duration: 0.6,
        stagger: 0.1,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: '.about__stats',
          start: 'top 84%'
        }
      }
    );
  }


  // ─── 6. PROCESS STEPS STAGGER ─────────────────────────────────
  /*
   * Steps slide in from the right — reads like a numbered
   * timeline being revealed one step at a time.
   */

  const processSteps = document.querySelectorAll('.process__step');
  if (processSteps.length) {
    gsap.fromTo(processSteps,
      { opacity: 0, x: 50 },
      {
        opacity: 1,
        x: 0,
        duration: 0.7,
        stagger: 0.12,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: '.process__right',
          start: 'top 80%'
        }
      }
    );
  }

})();
