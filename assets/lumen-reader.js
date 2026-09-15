(() => {
  'use strict';

  const STORAGE_KEY = 'lumen-reading-progress-v2';
  const body = document.body;
  const toolbar = document.getElementById('readerToolbar');
  const chapterBodies = Array.from(document.querySelectorAll('#main-content > .chapter-body'));
  if (!toolbar || !chapterBodies.length) return;

  const chapters = [];
  chapterBodies.forEach((container) => {
    const children = Array.from(container.children);
    const headings = children.filter((node) => node.matches('.chapter-heading[id]'));
    headings.forEach((heading, localIndex) => {
      const start = children.indexOf(heading);
      const nextHeading = headings[localIndex + 1];
      const end = nextHeading ? children.indexOf(nextHeading) : children.length;
      chapters.push({
        id: heading.id,
        title: heading.textContent.trim(),
        volume: heading.id.startsWith('pro-') ? '序幕 · 异世的呼唤' : '第一卷 · 星兆之海',
        container,
        nodes: children.slice(start, end)
      });
    });
  });

  if (!chapters.length) return;
  const byId = new Map(chapters.map((chapter, index) => [chapter.id, { chapter, index }]));
  const volumeLabel = document.getElementById('readerVolume');
  const positionLabel = document.getElementById('readerPosition');
  const progressBar = document.getElementById('readerProgressBar');
  const previousButton = document.getElementById('readerPrevBtn');
  const nextButton = document.getElementById('readerNextBtn');
  const tocButton = document.getElementById('readerTocBtn');
  const overviewButton = document.getElementById('readerOverviewBtn');
  let currentIndex = -1;
  let saveFrame = 0;
  let pageNav = null;
  let touchStart = null;

  function readProgress() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
      if (saved && byId.has(saved.chapterId)) return saved;
    } catch (_) {}
    return null;
  }

  function chapterScrollData() {
    if (currentIndex < 0) return { ratio: 0 };
    const container = chapters[currentIndex].container;
    const top = container.getBoundingClientRect().top + window.scrollY;
    const range = Math.max(1, container.offsetHeight - window.innerHeight * .62);
    return { ratio: Math.max(0, Math.min(1, (window.scrollY - top) / range)), top, range };
  }

  function saveProgress() {
    if (currentIndex < 0) return;
    const data = chapterScrollData();
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        chapterId: chapters[currentIndex].id,
        ratio: data.ratio,
        updatedAt: Date.now()
      }));
    } catch (_) {}
    const overall = ((currentIndex + data.ratio) / chapters.length) * 100;
    progressBar.style.width = `${Math.max(0, Math.min(100, overall))}%`;
  }

  function setSidebarState(id) {
    document.querySelectorAll('.sidebar .chap-link').forEach((link) => {
      link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
    });
    const active = document.querySelector(`.sidebar .chap-link[href="#${CSS.escape(id)}"]`);
    if (!active) return;
    const volume = active.closest('.side-vol');
    const group = active.closest('.side-group');
    if (volume) volume.classList.remove('collapsed');
    if (group) group.classList.remove('collapsed');
  }

  function ensurePageNav() {
    if (pageNav) return pageNav;
    pageNav = document.createElement('nav');
    pageNav.className = 'reader-page-nav';
    pageNav.setAttribute('aria-label', '章节翻页');
    pageNav.innerHTML = '<button type="button" data-reader-prev>← 上一章</button><span class="reader-page-count"></span><button type="button" data-reader-next>下一章 →</button>';
    pageNav.querySelector('[data-reader-prev]').addEventListener('click', () => turn(-1));
    pageNav.querySelector('[data-reader-next]').addEventListener('click', () => turn(1));
    return pageNav;
  }

  function updateControls() {
    const chapter = chapters[currentIndex];
    volumeLabel.textContent = chapter.volume;
    positionLabel.textContent = `第 ${currentIndex + 1} / ${chapters.length} 章`;
    previousButton.disabled = currentIndex === 0;
    nextButton.disabled = currentIndex === chapters.length - 1;
    const nav = ensurePageNav();
    nav.querySelector('[data-reader-prev]').disabled = previousButton.disabled;
    nav.querySelector('[data-reader-next]').disabled = nextButton.disabled;
    nav.querySelector('.reader-page-count').textContent = `${currentIndex + 1} / ${chapters.length}`;
  }

  function openChapter(id, options = {}) {
    const found = byId.get(id);
    if (!found) return false;
    currentIndex = found.index;
    body.classList.remove('reader-overview');
    body.classList.add('reader-reading');
    toolbar.hidden = false;

    chapterBodies.forEach((container) => {
      container.classList.remove('reader-current-body');
      Array.from(container.children).forEach((node) => node.classList.add('reader-hidden-node'));
    });
    found.chapter.container.classList.add('reader-current-body');
    found.chapter.nodes.forEach((node) => node.classList.remove('reader-hidden-node'));
    const nav = ensurePageNav();
    nav.classList.remove('reader-hidden-node');
    found.chapter.container.appendChild(nav);

    updateControls();
    setSidebarState(id);
    const historyMode = options.history || 'push';
    if (historyMode === 'push') history.pushState({ readerChapter: id }, '', `#${id}`);
    else if (historyMode === 'replace') history.replaceState({ readerChapter: id }, '', `#${id}`);

    requestAnimationFrame(() => {
      const container = found.chapter.container;
      const top = container.getBoundingClientRect().top + window.scrollY;
      const ratio = Math.max(0, Math.min(1, Number(options.ratio) || 0));
      const range = Math.max(1, container.offsetHeight - window.innerHeight * .62);
      window.scrollTo({ top: Math.max(0, top + ratio * range - 8), behavior: options.smooth ? 'smooth' : 'instant' });
      saveProgress();
    });
    closeSidebar();
    return true;
  }

  function showOverview(options = {}) {
    currentIndex = -1;
    body.classList.remove('reader-reading');
    body.classList.add('reader-overview');
    toolbar.hidden = true;
    chapterBodies.forEach((container) => container.classList.remove('reader-current-body'));
    document.querySelectorAll('.sidebar .chap-link').forEach((link) => link.classList.remove('active'));
    if (options.history !== false) history.pushState({ readerOverview: true }, '', `${location.pathname}${location.search}#story`);
    const hero = document.getElementById('story');
    if (hero) hero.scrollIntoView({ behavior: options.smooth ? 'smooth' : 'instant', block: 'start' });
    closeSidebar();
  }

  function turn(delta) {
    if (currentIndex < 0) return;
    const target = currentIndex + delta;
    if (target < 0 || target >= chapters.length) return;
    openChapter(chapters[target].id, { smooth: false, history: 'push' });
  }

  function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sideBackdrop');
    if (sidebar) sidebar.classList.remove('open');
    if (backdrop) backdrop.classList.remove('show');
  }

  function openSavedOrFirst() {
    const saved = readProgress();
    openChapter(saved ? saved.chapterId : chapters[0].id, {
      ratio: saved ? saved.ratio : 0,
      history: 'replace'
    });
  }

  previousButton.addEventListener('click', () => turn(-1));
  nextButton.addEventListener('click', () => turn(1));
  overviewButton.addEventListener('click', () => showOverview({ smooth: true }));
  tocButton.addEventListener('click', () => {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sideBackdrop');
    if (sidebar) sidebar.classList.add('open');
    if (backdrop) backdrop.classList.add('show');
  });

  document.querySelectorAll('.sidebar a[href^="#"]').forEach((link) => {
    const id = link.getAttribute('href').slice(1);
    if (!byId.has(id)) return;
    link.addEventListener('click', (event) => {
      event.preventDefault();
      openChapter(id, { history: 'push' });
    });
  });

  const storyGateway = document.querySelector('.home-section-link[href="#story-main"]');
  if (storyGateway) {
    storyGateway.addEventListener('click', (event) => {
      event.preventDefault();
      openSavedOrFirst();
    });
  }

  window.addEventListener('scroll', () => {
    if (currentIndex < 0 || saveFrame) return;
    saveFrame = requestAnimationFrame(() => { saveFrame = 0; saveProgress(); });
  }, { passive: true });
  window.addEventListener('pagehide', saveProgress);
  window.addEventListener('keydown', (event) => {
    if (currentIndex < 0 || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    const target = event.target;
    if (target && (target.matches('input, textarea, select, button') || target.isContentEditable)) return;
    if (document.querySelector('.modal-overlay.show, .char-drawer.show, .ann-popup')) return;
    if (event.key === 'ArrowLeft') { event.preventDefault(); turn(-1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); turn(1); }
  });
  document.addEventListener('touchstart', (event) => {
    if (currentIndex < 0 || event.touches.length !== 1) return;
    const touch = event.touches[0];
    touchStart = { x: touch.clientX, y: touch.clientY };
  }, { passive: true });
  document.addEventListener('touchend', (event) => {
    if (!touchStart || currentIndex < 0 || !event.changedTouches.length) { touchStart = null; return; }
    const touch = event.changedTouches[0];
    const dx = touch.clientX - touchStart.x;
    const dy = touch.clientY - touchStart.y;
    touchStart = null;
    if (Math.abs(dx) < 80 || Math.abs(dx) < Math.abs(dy) * 1.35) return;
    turn(dx < 0 ? 1 : -1);
  }, { passive: true });
  window.addEventListener('popstate', () => {
    const id = location.hash.slice(1);
    if (byId.has(id)) openChapter(id, { history: 'none' });
    else showOverview({ history: false });
  });

  window.LumenReader = { open: (id) => openChapter(id, { history: 'push' }), overview: showOverview };
  body.classList.add('reader-ready', 'reader-overview');

  const requested = location.hash.slice(1);
  const initialize = () => {
    if (byId.has(requested)) openChapter(requested, { history: 'replace' });
    else if (requested === 'story-main') openSavedOrFirst();
    else {
      const saved = readProgress();
      if (saved) openChapter(saved.chapterId, { ratio: saved.ratio, history: 'replace' });
    }
  };
  if (body.classList.contains('at-opening')) window.addEventListener('lumen:opening-dismissed', initialize, { once: true });
  else initialize();
})();
