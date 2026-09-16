(() => {
  'use strict';

  const STORAGE_KEY = 'lumen-side-reading-progress-v2';
  const LEGACY_KEY = 'lumen-side-reading-progress-v1';
  const stories = Array.from(document.querySelectorAll('.side-story-article'));
  if (!stories.length) return;

  let active = null;
  let saveFrame = 0;
  let touchStart = null;
  const controllers = [];
  const chapterLookup = new Map();

  function readState() {
    try {
      const value = JSON.parse(localStorage.getItem(STORAGE_KEY));
      if (value && value.stories) return value;
    } catch (_) {}
    try {
      const legacy = JSON.parse(localStorage.getItem(LEGACY_KEY));
      if (legacy && legacy.chapterId) {
        return { lastStoryId: 'hongying-story', stories: { 'hongying-story': legacy } };
      }
    } catch (_) {}
    return { lastStoryId: '', stories: {} };
  }

  function writeState(state) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (_) {}
  }

  function storyProgress(controller) {
    const state = readState();
    const progress = state.stories[controller.story.id];
    return progress && controller.byId.has(progress.chapterId) ? progress : null;
  }

  function buildController(story) {
    const content = story.querySelector('.side-story-content');
    if (!content) return null;
    const children = Array.from(content.children);
    const headings = children.filter((node) => node.matches('.side-story-heading[id]'));
    if (!headings.length) return null;
    const chapters = headings.map((heading, index) => {
      const start = children.indexOf(heading);
      const next = headings[index + 1];
      const end = next ? children.indexOf(next) : children.length;
      return { id: heading.id, title: heading.textContent.trim(), nodes: children.slice(start, end) };
    });
    const byId = new Map(chapters.map((chapter, index) => [chapter.id, { chapter, index }]));
    const title = story.querySelector('.side-story-hero h2')?.textContent.trim() || '时空遗闻';
    const toolbar = document.createElement('section');
    toolbar.className = 'side-reader-toolbar';
    toolbar.hidden = true;
    toolbar.setAttribute('aria-label', `${title}阅读控制`);
    toolbar.innerHTML = `<button type="button" data-side-overview>← 遗闻目录</button><div class="side-reader-location" aria-live="polite"><span>${title}</span><strong data-side-position></strong></div><div class="side-reader-actions"><button type="button" data-side-toc>目录</button><button type="button" data-side-prev>上一节</button><button type="button" data-side-next>下一节</button></div><div class="side-reader-progress"><span></span></div>`;
    story.appendChild(toolbar);
    const controller = {
      story, content, chapters, byId, toolbar, title, currentIndex: -1, pageNav: null,
      previousButton: toolbar.querySelector('[data-side-prev]'),
      nextButton: toolbar.querySelector('[data-side-next]'),
      positionLabel: toolbar.querySelector('[data-side-position]'),
      progressBar: toolbar.querySelector('.side-reader-progress span')
    };
    chapters.forEach((chapter) => chapterLookup.set(chapter.id, controller));
    return controller;
  }

  function readingStart(controller, chapter) {
    const heading = chapter.nodes[0];
    const toolbarBottom = controller.toolbar.getBoundingClientRect().bottom + 12;
    return heading.getBoundingClientRect().top + window.scrollY - toolbarBottom;
  }

  function scrollData(controller) {
    if (controller.currentIndex < 0) return { ratio: 0 };
    const start = readingStart(controller, controller.chapters[controller.currentIndex]);
    const end = controller.content.getBoundingClientRect().bottom + window.scrollY - window.innerHeight + 24;
    const range = Math.max(1, end - start);
    return { start, range, ratio: Math.max(0, Math.min(1, (window.scrollY - start) / range)) };
  }

  function saveProgress() {
    if (!active || active.currentIndex < 0 || !active.story.open) return;
    const data = scrollData(active);
    const state = readState();
    state.lastStoryId = active.story.id;
    state.stories[active.story.id] = {
      chapterId: active.chapters[active.currentIndex].id,
      ratio: data.ratio,
      updatedAt: Date.now()
    };
    writeState(state);
    active.progressBar.style.width = `${((active.currentIndex + data.ratio) / active.chapters.length) * 100}%`;
  }

  function ensurePageNav(controller) {
    if (controller.pageNav) return controller.pageNav;
    const nav = document.createElement('nav');
    nav.className = 'side-reader-page-nav';
    nav.setAttribute('aria-label', `${controller.title}翻页`);
    nav.innerHTML = '<button type="button" data-side-page-prev>← 上一节</button><span class="side-reader-page-count"></span><button type="button" data-side-page-next>下一节 →</button>';
    nav.querySelector('[data-side-page-prev]').addEventListener('click', () => turn(controller, -1));
    nav.querySelector('[data-side-page-next]').addEventListener('click', () => turn(controller, 1));
    controller.pageNav = nav;
    return nav;
  }

  function updateControls(controller) {
    controller.previousButton.disabled = controller.currentIndex === 0;
    controller.nextButton.disabled = controller.currentIndex === controller.chapters.length - 1;
    controller.positionLabel.textContent = `${controller.chapters[controller.currentIndex].title} · ${controller.currentIndex + 1} / ${controller.chapters.length}`;
    const nav = ensurePageNav(controller);
    nav.querySelector('[data-side-page-prev]').disabled = controller.previousButton.disabled;
    nav.querySelector('[data-side-page-next]').disabled = controller.nextButton.disabled;
    nav.querySelector('.side-reader-page-count').textContent = `${controller.currentIndex + 1} / ${controller.chapters.length}`;
  }

  function setSidebarState(id) {
    document.querySelectorAll('#sidebar .chap-link, .side-story-toc-grid a').forEach((link) => {
      link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
    });
    document.getElementById('g-side')?.classList.remove('collapsed');
    const sideLink = document.querySelector(`#sidebar a[href="#${id}"]`);
    sideLink?.closest('.side-vol')?.classList.remove('collapsed');
  }

  function closeSidebar() {
    document.getElementById('sidebar')?.classList.remove('open');
    document.getElementById('sideBackdrop')?.classList.remove('show');
  }

  function deactivateOthers(controller) {
    controllers.forEach((other) => {
      if (other === controller) return;
      other.story.classList.remove('side-reader-reading');
      other.toolbar.hidden = true;
      if (other.story.open) other.story.open = false;
    });
  }

  function openChapter(controller, id, options = {}) {
    const found = controller.byId.get(id);
    if (!found) return false;
    if (active && active !== controller) saveProgress();
    deactivateOthers(controller);
    active = controller;
    controller.currentIndex = found.index;
    controller.story.open = true;
    controller.story.classList.add('side-reader-reading');
    controller.toolbar.hidden = false;
    Array.from(controller.content.children).forEach((node) => node.classList.add('side-reader-hidden-node'));
    found.chapter.nodes.forEach((node) => node.classList.remove('side-reader-hidden-node'));
    const nav = ensurePageNav(controller);
    nav.classList.remove('side-reader-hidden-node');
    controller.content.appendChild(nav);
    updateControls(controller);
    setSidebarState(id);

    const historyMode = options.history || 'push';
    if (historyMode === 'push') history.pushState({ sideChapter: id }, '', `#${id}`);
    else if (historyMode === 'replace') history.replaceState({ sideChapter: id }, '', `#${id}`);

    requestAnimationFrame(() => requestAnimationFrame(() => {
      const start = readingStart(controller, found.chapter);
      const end = controller.content.getBoundingClientRect().bottom + window.scrollY - window.innerHeight + 24;
      const range = Math.max(1, end - start);
      const ratio = Math.max(0, Math.min(1, Number(options.ratio) || 0));
      window.scrollTo(0, Math.max(0, start + ratio * range));
      saveProgress();
    }));
    closeSidebar();
    return true;
  }

  function openSavedOrFirst(controller, historyMode = 'replace') {
    const saved = storyProgress(controller);
    openChapter(controller, saved ? saved.chapterId : controller.chapters[0].id, {
      ratio: saved ? saved.ratio : 0,
      history: historyMode
    });
  }

  function turn(controller, delta) {
    const target = controller.currentIndex + delta;
    if (target < 0 || target >= controller.chapters.length) return;
    openChapter(controller, controller.chapters[target].id, { history: 'push' });
  }

  function showOverview(controller) {
    saveProgress();
    controller.story.classList.remove('side-reader-reading');
    controller.toolbar.hidden = true;
    controller.story.open = false;
    if (active === controller) active = null;
    history.pushState({ sideOverview: true }, '', '#side-directory');
    document.getElementById('side-directory')?.scrollIntoView({ behavior: 'auto', block: 'start' });
    closeSidebar();
  }

  stories.forEach((story) => {
    const controller = buildController(story);
    if (!controller) return;
    controllers.push(controller);
    controller.previousButton.addEventListener('click', () => turn(controller, -1));
    controller.nextButton.addEventListener('click', () => turn(controller, 1));
    controller.toolbar.querySelector('[data-side-overview]').addEventListener('click', () => showOverview(controller));
    controller.toolbar.querySelector('[data-side-toc]').addEventListener('click', () => {
      document.getElementById('sidebar')?.classList.add('open');
      document.getElementById('sideBackdrop')?.classList.add('show');
    });
    controller.story.addEventListener('toggle', () => {
      if (controller.story.open && controller.currentIndex < 0) openSavedOrFirst(controller, 'replace');
      if (!controller.story.open) {
        controller.story.classList.remove('side-reader-reading');
        controller.toolbar.hidden = true;
        if (active === controller) active = null;
      }
    });
  });

  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    const id = link.getAttribute('href').slice(1);
    const chapterController = chapterLookup.get(id);
    const storyController = controllers.find((item) => item.story.id === id);
    if (chapterController) {
      link.addEventListener('click', (event) => {
        event.preventDefault();
        openChapter(chapterController, id, { history: 'push' });
      });
    } else if (storyController) {
      link.addEventListener('click', (event) => {
        event.preventDefault();
        openSavedOrFirst(storyController, 'push');
      });
    }
  });

  window.addEventListener('scroll', () => {
    if (!active || active.currentIndex < 0 || !active.story.open || saveFrame) return;
    saveFrame = requestAnimationFrame(() => { saveFrame = 0; saveProgress(); });
  }, { passive: true });
  window.addEventListener('pagehide', saveProgress);
  window.addEventListener('popstate', () => {
    const id = location.hash.slice(1);
    const chapterController = chapterLookup.get(id);
    const storyController = controllers.find((item) => item.story.id === id);
    if (chapterController) openChapter(chapterController, id, { history: 'none' });
    else if (storyController) openSavedOrFirst(storyController, 'none');
    else if (active) {
      active.story.classList.remove('side-reader-reading');
      active.toolbar.hidden = true;
      active = null;
    }
  });
  window.addEventListener('keydown', (event) => {
    if (!active || active.currentIndex < 0 || !active.story.open || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    const target = event.target;
    if (target && (target.matches('input, textarea, select, button') || target.isContentEditable)) return;
    if (event.key === 'ArrowLeft') { event.preventDefault(); turn(active, -1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); turn(active, 1); }
  });
  document.addEventListener('touchstart', (event) => {
    if (!active || active.currentIndex < 0 || !active.story.open || event.touches.length !== 1) return;
    const touch = event.touches[0];
    touchStart = { x: touch.clientX, y: touch.clientY };
  }, { passive: true });
  document.addEventListener('touchend', (event) => {
    if (!touchStart || !active || active.currentIndex < 0 || !active.story.open || !event.changedTouches.length) { touchStart = null; return; }
    const touch = event.changedTouches[0];
    const dx = touch.clientX - touchStart.x;
    const dy = touch.clientY - touchStart.y;
    touchStart = null;
    if (Math.abs(dx) < 80 || Math.abs(dx) < Math.abs(dy) * 1.35) return;
    turn(active, dx < 0 ? 1 : -1);
  }, { passive: true });

  window.LumenSideReader = {
    open: (id) => {
      const controller = chapterLookup.get(id);
      return controller ? openChapter(controller, id, { history: 'push' }) : false;
    }
  };

  const requested = location.hash.slice(1);
  const requestedChapter = chapterLookup.get(requested);
  const requestedStory = controllers.find((item) => item.story.id === requested);
  if (requestedChapter) openChapter(requestedChapter, requested, { history: 'replace' });
  else if (requestedStory) openSavedOrFirst(requestedStory, 'replace');
  else {
    const state = readState();
    const last = controllers.find((item) => item.story.id === state.lastStoryId);
    if (last && storyProgress(last)) openSavedOrFirst(last, 'replace');
  }
})();
