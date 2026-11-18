(() => {
  'use strict';
  const articles = [...document.querySelectorAll('.publication')];
  const filters = [...document.querySelectorAll('[data-filter]')];
  const videos = [...document.querySelectorAll('.publication-media video')];
  const visibleVideos = new Set();

  function setFilter(filter) {
    for (const article of articles) {
      article.hidden = filter === 'selected' && article.dataset.selected !== 'true';
    }
    for (const group of document.querySelectorAll('.publication-year')) {
      group.hidden = !group.querySelector('.publication:not([hidden])');
    }
    for (const button of filters) button.setAttribute('aria-pressed', String(button.dataset.filter === filter));
    videos.forEach(updateVideoPlayback);
  }
  for (const button of filters) button.addEventListener('click', () => setFilter(button.dataset.filter));
  setFilter('selected');

  for (const button of document.querySelectorAll('[data-preview-switch]')) {
    let lastPointerType = '';
    const showAlternate = show => {
      button.dataset.showAlternate = String(show);
      button.setAttribute('aria-pressed', String(show));
    };
    button.addEventListener('pointerenter', event => {
      lastPointerType = event.pointerType;
      if (event.pointerType === 'mouse') showAlternate(true);
    });
    button.addEventListener('pointerdown', event => {
      lastPointerType = event.pointerType;
    });
    button.addEventListener('pointerleave', event => {
      if (event.pointerType === 'mouse') showAlternate(false);
    });
    button.addEventListener('pointercancel', () => showAlternate(false));
    button.addEventListener('blur', () => showAlternate(false));
    button.addEventListener('click', event => {
      // Mouse hovering owns its preview; touch and keyboard activation toggle it.
      if (event.detail > 0 && lastPointerType === 'mouse') return;
      showAlternate(button.dataset.showAlternate !== 'true');
    });
  }

  function updateVideoPlayback(video) {
    if (!document.hidden && !video.closest('.publication').hidden && visibleVideos.has(video)) {
      if (!video.getAttribute('src')) video.src = video.dataset.src;
      video.play().catch(() => {});
    } else {
      video.pause();
    }
  }
  for (const video of videos) video.muted = true;
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (entry.isIntersecting) visibleVideos.add(entry.target);
        else visibleVideos.delete(entry.target);
        updateVideoPlayback(entry.target);
      }
    }, { rootMargin: '80px 0px', threshold: .05 });
    videos.forEach(video => observer.observe(video));
  } else {
    videos.forEach(video => visibleVideos.add(video));
    videos.forEach(updateVideoPlayback);
  }
  document.addEventListener('visibilitychange', () => videos.forEach(updateVideoPlayback));

  const navLinks = [...document.querySelectorAll('.nav-links a')];
  const sections = navLinks.map(link => document.querySelector(link.getAttribute('href')));
  let scheduled = false;
  function updateNavigation() {
    const threshold = Math.min(window.innerHeight * .28, 160);
    let current = sections[0];
    for (const section of sections) if (section.getBoundingClientRect().top <= threshold) current = section;
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 5) current = sections.at(-1);
    navLinks.forEach(link => {
      if (link.getAttribute('href') === `#${current.id}`) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    scheduled = false;
  }
  window.addEventListener('scroll', () => {
    if (!scheduled) { scheduled = true; window.requestAnimationFrame(updateNavigation); }
  }, { passive: true });
  window.addEventListener('resize', updateNavigation);
  updateNavigation();
})();
