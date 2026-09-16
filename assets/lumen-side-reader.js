(() => {
  'use strict';

  const STORAGE_KEY = 'lumen-side-reading-progress-v1';
  const story = document.getElementById('hongying-story');
  const content = story && story.querySelector('.side-story-content');
  if (!story || !content) return;

  const children = Array.from(content.children);
  const headings = children.filter((node) => node.matches('.side-story-heading[id]'));
  const chapters = headings.map((heading, index) => {
    const start = children.indexOf(heading);
    const next = headings[index + 1];
    const end = next ? children.indexOf(next) : children.length;
    return { id: heading.id, title: heading.textContent.trim(), nodes: children.slice(start, end) };
  });
  if (!chapters.length) return;

  const byId = new Map(chapters.map((chapter, index) => [chapter.id, { chapter, index }]));
  const toolbar = document.createElement('section');
  toolbar.className = 'side-reader-toolbar';
  toolbar.hidden = true;
  toolbar.setAttribute('aria-label', '时空遗闻阅读控制');
  toolbar.innerHTML = '<button type="button" data-side-overview>← 遗闻目录</button><div class="side-reader-location" aria-live="polite"><span>时空遗闻 · 鸿荧</span><strong data-side-position></strong></div><div class="side-reader-actions"><button type="button" data-side-toc>目录</button><button type="button" data-side-prev>上一节</button><button type="button" data-side-next>下一节</button></div><div class="side-reader-progress"><span></span></div>';
  story.appendChild(toolbar);

  let currentIndex = -1;
  let saveFrame = 0;
  let pageNav = null;
  let touchStart = null;

  const previousButton = toolbar.querySelector('[data-side-prev]');
  const nextButton = toolbar.querySelector('[data-side-next]');
  const positionLabel = toolbar.querySelector('[data-side-position]');
  const progressBar = toolbar.querySelector('.side-reader-progress span');

  function readProgress() {
    try {
      const value = JSON.parse(localStorage.getItem(STORAGE_KEY));
      if (value && byId.has(value.chapterId)) return value;
    } catch (_) {}
    return null;
  }

  function readingStart(chapter) {
    const heading = chapter.nodes[0];
    const toolbarBottom = toolbar.getBoundingClientRect().bottom + 12;
    return heading.getBoundingClientRect().top + window.scrollY - toolbarBottom;
  }

  function scrollData() {
    if (currentIndex < 0) return { ratio: 0 };
    const start = readingStart(chapters[currentIndex]);
    const end = content.getBoundingClientRect().bottom + window.scrollY - window.innerHeight + 24;
    const range = Math.max(1, end - start);
    return { start, range, ratio: Math.max(0, Math.min(1, (window.scrollY - start) / range)) };
  }

  function saveProgress() {
    if (currentIndex < 0 || !story.open) return;
    const data = scrollData();
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ chapterId: chapters[currentIndex].id, ratio: data.ratio, updatedAt: Date.now() }));
    } catch (_) {}
    progressBar.style.width = `${((currentIndex + data.ratio) / chapters.length) * 100}%`;
  }

  function ensurePageNav() {
    if (pageNav) return pageNav;
    pageNav = document.createElement('nav');
    pageNav.className = 'side-reader-page-nav';
    pageNav.setAttribute('aria-label', '时空遗闻翻页');
    pageNav.innerHTML = '<button type="button" data-side-page-prev>← 上一节</button><span class="side-reader-page-count"></span><button type="button" data-side-page-next>下一节 →</button>';
    pageNav.querySelector('[data-side-page-prev]').addEventListener('click', () => turn(-1));
    pageNav.querySelector('[data-side-page-next]').addEventListener('click', () => turn(1));
    return pageNav;
  }

  function updateControls() {
    previousButton.disabled = currentIndex === 0;
    nextButton.disabled = currentIndex === chapters.length - 1;
    positionLabel.textContent = `第 ${currentIndex + 1} / ${chapters.length} 节`;
    const nav = ensurePageNav();
    nav.querySelector('[data-side-page-prev]').disabled = previousButton.disabled;
    nav.querySelector('[data-side-page-next]').disabled = nextButton.disabled;
    nav.querySelector('.side-reader-page-count').textContent = `${currentIndex + 1} / ${chapters.length}`;
  }

  function setSidebarState(id) {
    document.querySelectorAll('#side-hongying-nav .chap-link, .side-story-toc-grid a').forEach((link) => {
      link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
    });
    const group = document.getElementById('g-side');
    const list = document.getElementById('side-hongying-nav');
    if (group) group.classList.remove('collapsed');
    if (list) list.classList.remove('collapsed');
  }

  function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sideBackdrop');
    if (sidebar) sidebar.classList.remove('open');
    if (backdrop) backdrop.classList.remove('show');
  }

  function openChapter(id, options = {}) {
    const found = byId.get(id);
    if (!found) return false;
    currentIndex = found.index;
    story.open = true;
    story.classList.add('side-reader-reading');
    toolbar.hidden = false;
    Array.from(content.children).forEach((node) => node.classList.add('side-reader-hidden-node'));
    found.chapter.nodes.forEach((node) => node.classList.remove('side-reader-hidden-node'));
    const nav = ensurePageNav();
    nav.classList.remove('side-reader-hidden-node');
    content.appendChild(nav);
    updateControls();
    setSidebarState(id);

    const historyMode = options.history || 'push';
    if (historyMode === 'push') history.pushState({ sideChapter: id }, '', `#${id}`);
    else if (historyMode === 'replace') history.replaceState({ sideChapter: id }, '', `#${id}`);

    requestAnimationFrame(() => requestAnimationFrame(() => {
      const start = readingStart(found.chapter);
      const end = content.getBoundingClientRect().bottom + window.scrollY - window.innerHeight + 24;
      const range = Math.max(1, end - start);
      const ratio = Math.max(0, Math.min(1, Number(options.ratio) || 0));
      window.scrollTo(0, Math.max(0, start + ratio * range));
      saveProgress();
    }));
    closeSidebar();
    return true;
  }

  function openSavedOrFirst(historyMode = 'replace') {
    const saved = readProgress();
    openChapter(saved ? saved.chapterId : chapters[0].id, { ratio: saved ? saved.ratio : 0, history: historyMode });
  }

  function turn(delta) {
    const target = currentIndex + delta;
    if (target < 0 || target >= chapters.length) return;
    openChapter(chapters[target].id, { history: 'push' });
  }

  function showOverview() {
    story.classList.remove('side-reader-reading');
    toolbar.hidden = true;
    story.open = false;
    history.pushState({ sideOverview: true }, '', '#char-bg');
    const directory = document.getElementById('side-directory');
    if (directory) directory.scrollIntoView({ behavior: 'auto', block: 'start' });
    closeSidebar();
  }

  previousButton.addEventListener('click', () => turn(-1));
  nextButton.addEventListener('click', () => turn(1));
  toolbar.querySelector('[data-side-overview]').addEventListener('click', showOverview);
  toolbar.querySelector('[data-side-toc]').addEventListener('click', () => {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sideBackdrop');
    if (sidebar) sidebar.classList.add('open');
    if (backdrop) backdrop.classList.add('show');
  });

  document.querySelectorAll('a[href^="#hongying-ch"]').forEach((link) => {
    const id = link.getAttribute('href').slice(1);
    if (!byId.has(id)) return;
    link.addEventListener('click', (event) => {
      event.preventDefault();
      openChapter(id, { history: 'push' });
    });
  });
  document.querySelectorAll('a[href="#hongying-story"]').forEach((link) => {
    link.addEventListener('click', (event) => {
      event.preventDefault();
      openSavedOrFirst('push');
    });
  });

  story.addEventListener('toggle', () => {
    if (story.open && currentIndex < 0) openSavedOrFirst('replace');
    if (!story.open) { story.classList.remove('side-reader-reading'); toolbar.hidden = true; }
  });
  window.addEventListener('scroll', () => {
    if (currentIndex < 0 || !story.open || saveFrame) return;
    saveFrame = requestAnimationFrame(() => { saveFrame = 0; saveProgress(); });
  }, { passive: true });
  window.addEventListener('pagehide', saveProgress);
  window.addEventListener('popstate', () => {
    const id = location.hash.slice(1);
    if (byId.has(id)) openChapter(id, { history: 'none' });
    else if (id === 'hongying-story') openSavedOrFirst('none');
    else { story.classList.remove('side-reader-reading'); toolbar.hidden = true; }
  });
  window.addEventListener('keydown', (event) => {
    if (currentIndex < 0 || !story.open || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    const target = event.target;
    if (target && (target.matches('input, textarea, select, button') || target.isContentEditable)) return;
    if (event.key === 'ArrowLeft') { event.preventDefault(); turn(-1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); turn(1); }
  });
  document.addEventListener('touchstart', (event) => {
    if (currentIndex < 0 || !story.open || event.touches.length !== 1) return;
    const touch = event.touches[0];
    touchStart = { x: touch.clientX, y: touch.clientY };
  }, { passive: true });
  document.addEventListener('touchend', (event) => {
    if (!touchStart || currentIndex < 0 || !story.open || !event.changedTouches.length) { touchStart = null; return; }
    const touch = event.changedTouches[0];
    const dx = touch.clientX - touchStart.x;
    const dy = touch.clientY - touchStart.y;
    touchStart = null;
    if (Math.abs(dx) < 80 || Math.abs(dx) < Math.abs(dy) * 1.35) return;
    turn(dx < 0 ? 1 : -1);
  }, { passive: true });

  window.LumenSideReader = { open: (id) => openChapter(id, { history: 'push' }) };
  const requested = location.hash.slice(1);
  if (byId.has(requested)) openChapter(requested, { history: 'replace' });
  else if (requested === 'hongying-story') openSavedOrFirst('replace');
  else if (readProgress()) openSavedOrFirst('replace');
})();
