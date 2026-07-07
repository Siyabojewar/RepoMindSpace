// mobile-nav.js – Injects hamburger toggle + sidebar overlay on all app pages

(function () {
  'use strict';

  function init() {
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar) return; // not an app page (e.g. login/register)

    // ── 1. Create hamburger toggle ──────────────────────────────────────
    const toggle = document.createElement('button');
    toggle.id = 'mobileSidebarToggle';
    toggle.setAttribute('aria-label', 'Open navigation menu');
    toggle.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
           stroke="currentColor" stroke-width="2.5"
           stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="6"  x2="21" y2="6"/>
        <line x1="3" y1="12" x2="21" y2="12"/>
        <line x1="3" y1="18" x2="21" y2="18"/>
      </svg>`;
    document.body.appendChild(toggle);

    // ── 2. Create overlay ───────────────────────────────────────────────
    const overlay = document.createElement('div');
    overlay.id = 'sidebarOverlay';
    document.body.appendChild(overlay);

    // ── 3. Toggle logic ─────────────────────────────────────────────────
    function openSidebar() {
      sidebar.classList.add('is-open');
      overlay.classList.add('is-visible');
      toggle.setAttribute('aria-expanded', 'true');
      toggle.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
             stroke="currentColor" stroke-width="2.5"
             stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6"  x2="6" y2="18"/>
          <line x1="6"  y1="6"  x2="18" y2="18"/>
        </svg>`;
    }

    function closeSidebar() {
      sidebar.classList.remove('is-open');
      overlay.classList.remove('is-visible');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
             stroke="currentColor" stroke-width="2.5"
             stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="6"  x2="21" y2="6"/>
          <line x1="3" y1="12" x2="21" y2="12"/>
          <line x1="3" y1="18" x2="21" y2="18"/>
        </svg>`;
    }

    toggle.addEventListener('click', () => {
      if (sidebar.classList.contains('is-open')) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });

    overlay.addEventListener('click', closeSidebar);

    // Close on ESC key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeSidebar();
    });

    // Close sidebar when a nav link is clicked on mobile
    sidebar.querySelectorAll('.sidebar-link').forEach(link => {
      link.addEventListener('click', () => {
        if (window.innerWidth <= 1024) closeSidebar();
      });
    });

    // ── 4. Resize guard – reset state on desktop ────────────────────────
    const mq = window.matchMedia('(min-width: 1025px)');
    mq.addEventListener('change', (e) => {
      if (e.matches) closeSidebar();
    });
  }

  // Run after DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
