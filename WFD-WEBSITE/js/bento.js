/* js/bento.js — Wood Fired Designs — woodfireddesigns.com
   ─────────────────────────────────────────────────────────────
   Bento grid interactions:
   - Hover/focus: play video, fade out poster
   - Leave: pause + reset video, fade in poster
   - Touch: tap to play/pause (mobile)
   - Respects prefers-reduced-motion
   ───────────────────────────────────────────────────────────── */

(function () {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function initBento() {
    const cards = document.querySelectorAll('.bento-card');
    if (!cards.length) return;

    cards.forEach(function (card) {
      const video  = card.querySelector('.bento-card__video');
      const hasVideo = video && video.querySelector('source[src]:not([src=""])');

      function startVideo() {
        if (!video || prefersReducedMotion) return;
        if (!hasVideo) return;

        video.play().then(function () {
          card.classList.add('is-playing');
        }).catch(function () {
          // Autoplay blocked — poster stays visible
        });
      }

      function stopVideo() {
        if (!video) return;
        card.classList.remove('is-playing');
        video.pause();
        // Small delay before resetting so fade-out completes
        setTimeout(function () {
          video.currentTime = 0;
        }, 350);
      }

      /* ── Mouse / pointer ─────────────────────────────────── */
      card.addEventListener('mouseenter', startVideo);
      card.addEventListener('mouseleave', stopVideo);

      /* ── Keyboard focus ──────────────────────────────────── */
      card.addEventListener('focusin', startVideo);
      card.addEventListener('focusout', stopVideo);

      /* ── Touch (mobile) ──────────────────────────────────── */
      let touchPlaying = false;

      card.addEventListener('touchstart', function (e) {
        if (!hasVideo) return;
        e.preventDefault();
        if (touchPlaying) {
          stopVideo();
          touchPlaying = false;
        } else {
          startVideo();
          touchPlaying = true;
        }
      }, { passive: false });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBento);
  } else {
    initBento();
  }
})();
