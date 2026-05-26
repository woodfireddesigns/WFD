/* js/gallery.js — Wood Fired Designs — woodfireddesigns.com
   ─────────────────────────────────────────────────────────────
   Full-screen slideshow. Auto-advances every 5s.
   Crossfade + Ken Burns (CSS). Dot nav, arrow nav,
   keyboard nav, touch swipe.
   ───────────────────────────────────────────────────────────── */

(function () {
  'use strict';

  const INTERVAL   = 5000; // ms per slide
  const FADE_MS    = 1000; // must match CSS transition duration

  function initGallery() {
    const section     = document.querySelector('.section-gallery');
    if (!section) return;

    const slides      = Array.from(section.querySelectorAll('.gallery__slide'));
    const dots        = Array.from(section.querySelectorAll('.gallery__dot'));
    const prevBtn     = section.querySelector('.gallery__arrow--prev');
    const nextBtn     = section.querySelector('.gallery__arrow--next');
    const progressBar = section.querySelector('.gallery__progress-bar');
    const counterCur  = section.querySelector('.gallery__counter-current');
    const counterTot  = section.querySelector('.gallery__counter-total');

    if (!slides.length) return;

    let current   = 0;
    let timer     = null;
    let progTimer = null;
    let isTransitioning = false;

    /* ── Set total counter ──────────────────────────────────── */
    if (counterTot) counterTot.textContent = slides.length;

    /* ── Go to slide ────────────────────────────────────────── */
    function goTo(index, direction) {
      if (isTransitioning) return;
      if (index === current) return;

      isTransitioning = true;

      /* Remove active from current */
      slides[current].classList.remove('is-active');
      slides[current].classList.add('is-prev');
      dots[current] && dots[current].classList.remove('is-active');

      current = (index + slides.length) % slides.length;

      /* Activate new slide */
      slides[current].classList.add('is-active');
      slides[current].classList.remove('is-prev');
      dots[current] && dots[current].classList.add('is-active');

      /* Update counter */
      if (counterCur) counterCur.textContent = current + 1;

      /* Clean up prev class after transition */
      setTimeout(function () {
        slides.forEach(function (s) { s.classList.remove('is-prev'); });
        isTransitioning = false;
      }, FADE_MS);

      /* Restart progress bar */
      resetProgress();
    }

    function next() { goTo(current + 1); }
    function prev() { goTo(current - 1); }

    /* ── Progress bar ───────────────────────────────────────── */
    function resetProgress() {
      if (!progressBar) return;
      clearTimeout(progTimer);

      /* Reset */
      progressBar.style.transition = 'none';
      progressBar.style.width = '0%';
      progressBar.classList.remove('is-running');

      /* Re-trigger paint then animate */
      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          progressBar.style.transition = 'width ' + INTERVAL + 'ms linear';
          progressBar.style.width = '100%';
          progressBar.classList.add('is-running');
        });
      });
    }

    /* ── Auto-advance ───────────────────────────────────────── */
    function startAuto() {
      clearInterval(timer);
      timer = setInterval(next, INTERVAL);
    }

    function stopAuto() {
      clearInterval(timer);
      if (progressBar) {
        const computed = parseFloat(getComputedStyle(progressBar).width);
        const total    = parseFloat(getComputedStyle(progressBar.parentElement).width);
        progressBar.style.transition = 'none';
        progressBar.style.width = (computed / total * 100) + '%';
        progressBar.classList.remove('is-running');
      }
    }

    /* ── Pause on hover ─────────────────────────────────────── */
    section.addEventListener('mouseenter', stopAuto);
    section.addEventListener('mouseleave', function () {
      startAuto();
      resetProgress();
    });

    /* ── Arrow buttons ──────────────────────────────────────── */
    if (prevBtn) prevBtn.addEventListener('click', function () {
      stopAuto(); prev(); startAuto();
    });
    if (nextBtn) nextBtn.addEventListener('click', function () {
      stopAuto(); next(); startAuto();
    });

    /* ── Dot buttons ────────────────────────────────────────── */
    dots.forEach(function (dot, i) {
      dot.addEventListener('click', function () {
        stopAuto(); goTo(i); startAuto();
      });
    });

    /* ── Keyboard ───────────────────────────────────────────── */
    document.addEventListener('keydown', function (e) {
      /* Only hijack arrow keys when gallery is in view */
      const rect = section.getBoundingClientRect();
      const inView = rect.top < window.innerHeight && rect.bottom > 0;
      if (!inView) return;

      if (e.key === 'ArrowLeft')  { stopAuto(); prev(); startAuto(); }
      if (e.key === 'ArrowRight') { stopAuto(); next(); startAuto(); }
    });

    /* ── Touch swipe ────────────────────────────────────────── */
    let touchStartX = 0;
    let touchStartY = 0;

    section.addEventListener('touchstart', function (e) {
      touchStartX = e.touches[0].clientX;
      touchStartY = e.touches[0].clientY;
    }, { passive: true });

    section.addEventListener('touchend', function (e) {
      const dx = e.changedTouches[0].clientX - touchStartX;
      const dy = e.changedTouches[0].clientY - touchStartY;
      if (Math.abs(dx) < 40 || Math.abs(dy) > Math.abs(dx)) return;
      stopAuto();
      if (dx < 0) next(); else prev();
      startAuto();
    }, { passive: true });

    /* ── Init ───────────────────────────────────────────────── */
    slides[0].classList.add('is-active');
    dots[0] && dots[0].classList.add('is-active');
    if (counterCur) counterCur.textContent = 1;
    startAuto();
    resetProgress();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGallery);
  } else {
    initGallery();
  }
})();
