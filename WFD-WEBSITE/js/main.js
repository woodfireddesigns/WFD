/* js/main.js — Wood Fired Designs */

(function () {
  'use strict';

  // ─── NAV ──────────────────────────────────────────────────────

  var H   = document.getElementById('H');
  var Btn = document.getElementById('H-btn');
  var M   = document.getElementById('M');
  var open = false;

  window.addEventListener('scroll', function () {
    if (H) H.classList.toggle('solid', window.scrollY > 10);
  }, { passive: true });
  if (H) H.classList.toggle('solid', window.scrollY > 10);

  function openMenu() {
    open = true;
    M.removeAttribute('hidden');
    H.classList.add('open');
    Btn.setAttribute('aria-expanded', 'true');
  }

  function closeMenu() {
    open = false;
    M.setAttribute('hidden', '');
    H.classList.remove('open');
    Btn.setAttribute('aria-expanded', 'false');
  }

  if (Btn) Btn.addEventListener('click', function () { open ? closeMenu() : openMenu(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenu(); });

  M && M.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () {
      var t = document.querySelector(a.getAttribute('href'));
      closeMenu();
      if (t) setTimeout(function () {
        window.scrollTo({ top: t.getBoundingClientRect().top + window.scrollY - 80, behavior: 'smooth' });
      }, 50);
    });
  });


  // ─── SMOOTH SCROLL ────────────────────────────────────────────

  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    if (link.closest('#M')) return;
    link.addEventListener('click', function (e) {
      var hash = this.getAttribute('href');
      if (!hash || hash === '#') return;
      var target = document.querySelector(hash);
      if (!target) return;
      e.preventDefault();
      window.scrollTo({
        top: target.getBoundingClientRect().top + window.scrollY - 80,
        behavior: 'smooth'
      });
    });
  });


  // ─── SCROLL-TO-TOP ────────────────────────────────────────────

  const scrollTopBtn = document.getElementById('scroll-top-btn');

  if (scrollTopBtn) {
    window.addEventListener('scroll', function () {
      scrollTopBtn.classList.toggle('is-visible', window.scrollY > 400);
    }, { passive: true });

    scrollTopBtn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }


  // ─── HERO VIDEO FALLBACK ──────────────────────────────────────

  const heroVideo = document.getElementById('hero-video');
  if (heroVideo) {
    heroVideo.addEventListener('error', function () {
      heroVideo.style.display = 'none';
    }, { once: true });
  }


  // ─── MAGNETIC BUTTONS ────────────────────────────────────────

  document.querySelectorAll('.btn--accent').forEach(function (btn) {
    btn.addEventListener('mousemove', function (e) {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      btn.style.transform = 'translate(' + (x * 0.15) + 'px, ' + (y * 0.25) + 'px)';
    });
    btn.addEventListener('mouseleave', function () {
      btn.style.transform = '';
    });
  });


  // ─── STAT COUNTERS ────────────────────────────────────────────

  const statEls = document.querySelectorAll('.hero-seq__stat-num[data-target]');

  if (statEls.length) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const target = parseInt(el.dataset.target, 10);
        const duration = 1200;
        const start = performance.now();
        function tick(now) {
          const t = Math.min((now - start) / duration, 1);
          const ease = 1 - Math.pow(1 - t, 3);
          el.textContent = Math.round(ease * target) + (el.dataset.suffix || '');
          if (t < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
        observer.unobserve(el);
      });
    }, { threshold: 0.5 });

    statEls.forEach(function (el) { observer.observe(el); });
  }

})();
