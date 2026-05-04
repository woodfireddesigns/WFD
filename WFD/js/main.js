/* js/main.js — Wood Fired Designs — woodfireddesigns.com */

/**
 * main.js
 * Responsibilities:
 *   1. Nav scroll behavior (transparent → solid at 60px)
 *   2. Nav dark/light state (inverse text over hero video)
 *   3. Nav overlay toggle (hamburger, close, escape, outside click)
 *   4. Stat counters (IntersectionObserver + rAF ease-out)
 *   5. Anchor smooth scroll (with nav offset + overlay close)
 *   6. Scroll-to-top button (appears at 400px)
 *   7. Hero video swap (mobile breakpoint)
 * No dependencies. Vanilla JS only.
 */

(function () {
  'use strict';

  // ─── 1. NAV SCROLL BEHAVIOR ───────────────────────────────────

  const siteNav = document.getElementById('site-nav');

  function updateNavScroll() {
    if (!siteNav) return;
    siteNav.classList.toggle('nav--scrolled', window.scrollY > 60);
  }

  updateNavScroll();
  window.addEventListener('scroll', updateNavScroll, { passive: true });


  // ─── 2. NAV DARK / LIGHT STATE ────────────────────────────────
  /*
   * While the hero section is still visible and we haven't scrolled
   * past 60px, nav text should invert (readable over dark video).
   * Once scrolled, nav gains background — normal text color resumes.
   */

  if (siteNav) {
    const heroSection = document.getElementById('hero');

    function updateNavDarkState() {
      if (!heroSection) return;
      const heroBottom = heroSection.getBoundingClientRect().bottom;
      const onDark = heroBottom > 80 && window.scrollY < 60;
      siteNav.classList.toggle('nav--on-dark', onDark);
    }

    updateNavDarkState();
    window.addEventListener('scroll', updateNavDarkState, { passive: true });
  }


  // ─── 3. NAV OVERLAY TOGGLE ────────────────────────────────────

  const hamburger     = document.getElementById('nav-hamburger');
  const navOverlay    = document.getElementById('nav-overlay');
  const overlayItems  = document.querySelectorAll('.overlay-link__item');

  function openNav() {
    document.body.classList.add('nav--open');
    if (hamburger) {
      hamburger.setAttribute('aria-expanded', 'true');
      hamburger.setAttribute('aria-label', 'Close menu');
    }
    // Stagger overlay items in
    overlayItems.forEach((item, i) => {
      item.style.transitionDelay = (i * 0.08) + 's';
    });
  }

  function closeNav() {
    document.body.classList.remove('nav--open');
    if (hamburger) {
      hamburger.setAttribute('aria-expanded', 'false');
      hamburger.setAttribute('aria-label', 'Open menu');
    }
    // Reset delays so next open re-staggers from zero
    overlayItems.forEach(item => {
      item.style.transitionDelay = '0s';
    });
  }

  if (hamburger) {
    hamburger.addEventListener('click', () => {
      document.body.classList.contains('nav--open') ? closeNav() : openNav();
    });
  }

  // Close on overlay background click
  if (navOverlay) {
    navOverlay.addEventListener('click', e => {
      if (e.target === navOverlay) closeNav();
    });
  }

  // Close on Escape
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && document.body.classList.contains('nav--open')) {
      closeNav();
    }
  });

  // Close on overlay link click
  document.querySelectorAll('[data-overlay-link]').forEach(link => {
    link.addEventListener('click', closeNav);
  });


  // ─── 4. STAT COUNTERS ─────────────────────────────────────────
  /*
   * Each .stat-number element has data-target="N".
   * On viewport entry: count from 0 to N over 1200ms with ease-out.
   * Uses rAF for smooth animation.
   */

  function easeOutQuart(t) {
    return 1 - Math.pow(1 - t, 4);
  }

  function runCounter(el) {
    const target   = parseInt(el.getAttribute('data-target'), 10);
    const duration = 1200;
    let start      = null;

    function step(ts) {
      if (!start) start = ts;
      const elapsed  = ts - start;
      const progress = Math.min(elapsed / duration, 1);
      el.textContent = Math.round(easeOutQuart(progress) * target);
      if (progress < 1) requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
  }

  const counterObserver = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          runCounter(entry.target);
          counterObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.6 }
  );

  document.querySelectorAll('.stat-number').forEach(el => {
    counterObserver.observe(el);
  });


  // ─── 5. ANCHOR SMOOTH SCROLL ──────────────────────────────────

  const NAV_HEIGHT = 80;

  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', function (e) {
      const hash = this.getAttribute('href');
      if (!hash || hash === '#') return;

      const target = document.querySelector(hash);
      if (!target) return;

      e.preventDefault();

      const scroll = () => {
        const top = target.getBoundingClientRect().top + window.scrollY - NAV_HEIGHT;
        window.scrollTo({ top, behavior: 'smooth' });
      };

      if (document.body.classList.contains('nav--open')) {
        closeNav();
        // Brief delay lets overlay begin closing before scroll fires
        setTimeout(scroll, 320);
      } else {
        scroll();
      }
    });
  });


  // ─── 6. SCROLL-TO-TOP BUTTON ──────────────────────────────────

  const scrollTopBtn = document.getElementById('scroll-top-btn');

  function updateScrollTopBtn() {
    if (!scrollTopBtn) return;
    scrollTopBtn.classList.toggle('is-visible', window.scrollY > 400);
  }

  window.addEventListener('scroll', updateScrollTopBtn, { passive: true });

  if (scrollTopBtn) {
    scrollTopBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }


  // ─── 7. HERO VIDEO FALLBACK ───────────────────────────────────
  // If video fails to load entirely, poster remains visible (browser default)

  const heroVideo = document.getElementById('hero-video');

  if (heroVideo) {
    heroVideo.addEventListener('error', () => {
      heroVideo.style.display = 'none';
    }, { once: true });
  }


  // ─── 8. MAGNETIC BUTTONS ──────────────────────────────────────
  /*
   * When cursor comes within ~80px of a .btn--accent button,
   * the button subtly shifts toward the cursor (max 8px movement).
   * On mouseleave it snaps back via CSS transition on transform.
   */

  const magnetBtns = document.querySelectorAll('.btn--accent');

  magnetBtns.forEach(btn => {
    btn.addEventListener('mousemove', e => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      btn.style.transform = `translate(${x * 0.15}px, ${y * 0.25}px)`;
    });
    btn.addEventListener('mouseleave', () => {
      btn.style.transform = '';
    });
  });

})();
