/* MODURA reveal.js &mdash; scroll animations + mobile nav */
(function () {
  'use strict';

  // === Scroll Reveal ===
  const revealEls = document.querySelectorAll('[data-reveal]');
  if (revealEls.length > 0 && 'IntersectionObserver' in window) {
    const obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });
    revealEls.forEach(function (el) { obs.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('is-visible'); });
  }

  // === Sticky Nav Shadow ===
  const nav = document.querySelector('[data-nav]');
  if (nav) {
    var lastScroll = 0;
    window.addEventListener('scroll', function () {
      var s = window.scrollY;
      if (s > 10) { nav.classList.add('nav-scrolled'); }
      else { nav.classList.remove('nav-scrolled'); }
      lastScroll = s;
    }, { passive: true });
  }

  // === Mobile Nav Toggle ===
  const navToggle = document.querySelector('[data-nav-toggle]');
  const navMenu = document.querySelector('[data-nav-menu]');
  if (navToggle && navMenu) {
    navToggle.addEventListener('click', function () {
      navMenu.classList.toggle('nav-menu-open');
      navToggle.classList.toggle('is-active');
    });
    // Close on link click (but not on dropdown toggles)
    navMenu.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        if (link.classList.contains('nav-dropdown-toggle')) return;
        navMenu.classList.remove('nav-menu-open');
        navToggle.classList.remove('is-active');
      });
    });
  }

  // === Dropdown Menus (desktop: hover+delay, mobile: click) ===
  var dropdowns = document.querySelectorAll('[data-nav-dropdown]');
  var isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  var hoverTimer = null;
  var activeDropdown = null;

  function openDropdown(dd) {
    if (activeDropdown && activeDropdown !== dd) {
      activeDropdown.classList.remove('open');
    }
    dd.classList.add('open');
    activeDropdown = dd;
  }

  function closeDropdown(dd) {
    dd.classList.remove('open');
    if (activeDropdown === dd) activeDropdown = null;
  }

  function closeAllDropdowns() {
    dropdowns.forEach(function (dd) { dd.classList.remove('open'); });
    activeDropdown = null;
  }

  dropdowns.forEach(function (dd) {
    var toggle = dd.querySelector('.nav-dropdown-toggle');

    if (!isTouch) {
      // Desktop: hover with 300ms delay
      dd.addEventListener('mouseenter', function () {
        clearTimeout(hoverTimer);
        hoverTimer = setTimeout(function () { openDropdown(dd); }, 300);
      });
      dd.addEventListener('mouseleave', function () {
        clearTimeout(hoverTimer);
        hoverTimer = setTimeout(function () { closeDropdown(dd); }, 300);
      });
    }

    // Mobile + desktop fallback: click toggle
    if (toggle) {
      toggle.addEventListener('click', function (e) {
        if (isTouch || window.innerWidth <= 768) {
          e.preventDefault();
          if (dd.classList.contains('open')) {
            closeDropdown(dd);
          } else {
            openDropdown(dd);
          }
        }
      });
    }
  });

  // Close dropdowns on outside click
  document.addEventListener('click', function (e) {
    var inside = false;
    dropdowns.forEach(function (dd) {
      if (dd.contains(e.target)) inside = true;
    });
    if (!inside) closeAllDropdowns();
  });

  // Close dropdowns on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeAllDropdowns();
  });

  // === Counter Animation ===
  const counters = document.querySelectorAll('[data-counter]');
  if (counters.length > 0 && 'IntersectionObserver' in window) {
    var counterObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var el = entry.target;
          var target = parseInt(el.getAttribute('data-counter'), 10);
          var suffix = el.getAttribute('data-suffix') || '';
          var duration = 1600;
          var start = 0;
          var startTime = null;
          function animate(ts) {
            if (!startTime) startTime = ts;
            var progress = Math.min((ts - startTime) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            var current = Math.floor(start + (target - start) * eased);
            el.textContent = current.toLocaleString('en-US') + suffix;
            if (progress < 1) { requestAnimationFrame(animate); }
          }
          requestAnimationFrame(animate);
          counterObs.unobserve(el);
        }
      });
    }, { threshold: 0.5 });
    counters.forEach(function (el) { counterObs.observe(el); });
  }

  // === Smooth Scroll for Anchor Links ===
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var href = this.getAttribute('href');
      if (href.length > 1) {
        var target = document.querySelector(href);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });
  });
})();
