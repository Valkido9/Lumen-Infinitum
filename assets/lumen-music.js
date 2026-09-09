/* Context-aware soundtrack for story regions. */
(() => {
  const zones = Array.from(document.querySelectorAll('[data-music-src]'));
  if (!zones.length) return;

  const audio = new Audio();
  audio.loop = true;
  audio.preload = 'auto';
  const MASTER_VOLUME = 0.35;
  const PROGRESS_KEY = 'lumen-music-progress-v1';
  let activeZone = null;
  let activeTrackKey = '';
  let pendingResumeTime = null;
  let lastProgressWrite = 0;
  let fadeFrame = 0;
  let transitionId = 0;
  let userPaused = localStorage.getItem('lumen-music-muted') === '1';
  let autoplayBlocked = false;
  let blockedClickArmed = false;

  function keyFor(src) {
    try { return new URL(src, document.baseURI).pathname; }
    catch (_) { return src; }
  }

  function readProgress(key) {
    try {
      const value = JSON.parse(localStorage.getItem(PROGRESS_KEY) || '{}')[key];
      return Number.isFinite(value) && value >= 0 ? value : 0;
    } catch (_) { return 0; }
  }

  function writeProgress(key, value) {
    if (!key || !Number.isFinite(value) || value < 0) return;
    try {
      const saved = JSON.parse(localStorage.getItem(PROGRESS_KEY) || '{}');
      saved[key] = value;
      localStorage.setItem(PROGRESS_KEY, JSON.stringify(saved));
    } catch (_) {}
  }

  function saveProgress(force = false) {
    if (!activeTrackKey || !Number.isFinite(audio.currentTime)) return;
    const now = performance.now();
    if (!force && now - lastProgressWrite < 1000) return;
    lastProgressWrite = now;
    writeProgress(activeTrackKey, audio.currentTime);
  }

  function restoreProgress() {
    if (pendingResumeTime == null || audio.readyState === 0) return;
    let position = pendingResumeTime;
    if (Number.isFinite(audio.duration) && audio.duration > 0) position %= audio.duration;
    try {
      audio.currentTime = position;
      pendingResumeTime = null;
    } catch (_) {}
  }

  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'music-toggle';
  document.body.append(button);

  function updateButton() {
    button.classList.toggle('muted', userPaused);
    button.classList.toggle('blocked', autoplayBlocked && !userPaused);
    button.textContent = userPaused ? '🔇' : '🔊';
    button.title = userPaused || autoplayBlocked ? '播放背景音乐' : '静音背景音乐';
    button.setAttribute('aria-label', button.title);
    button.setAttribute('aria-pressed', String(userPaused));
    button.dataset.state = userPaused ? 'muted' : autoplayBlocked ? 'blocked' : (!audio.paused && activeZone ? 'playing' : 'stopped');
  }

  function cancelFade() {
    if (fadeFrame) cancelAnimationFrame(fadeFrame);
    fadeFrame = 0;
  }

  function fadeTo(target, duration, done) {
    cancelFade();
    const start = audio.volume;
    const began = performance.now();
    if (!duration) {
      audio.volume = target;
      if (done) done();
      return;
    }
    const step = now => {
      const progress = Math.min(1, (now - began) / duration);
      audio.volume = start + (target - start) * progress;
      if (progress < 1) fadeFrame = requestAnimationFrame(step);
      else {
        fadeFrame = 0;
        if (done) done();
      }
    };
    fadeFrame = requestAnimationFrame(step);
  }

  async function beginZone(zone, id) {
    if (!zone || userPaused || document.hidden || id !== transitionId) return;
    const src = new URL(zone.dataset.musicSrc, document.baseURI).href;
    const instant = zone.dataset.musicMode === 'instant';
    if (audio.src !== src) {
      saveProgress(true);
      activeTrackKey = keyFor(src);
      pendingResumeTime = readProgress(activeTrackKey);
      audio.src = src;
      restoreProgress();
    }
    audio.volume = instant ? MASTER_VOLUME : 0;
    try {
      await audio.play();
      autoplayBlocked = false;
      updateButton();
      if (!instant && id === transitionId) fadeTo(MASTER_VOLUME, 1400);
    } catch (_) {
      autoplayBlocked = true;
      updateButton();
    }
  }

  function changeZone(zone) {
    if (zone === activeZone) {
      if (zone && !userPaused && audio.paused && !document.hidden) beginZone(zone, transitionId);
      return;
    }
    activeZone = zone;
    const id = ++transitionId;
    const next = () => {
      saveProgress(true);
      audio.pause();
      updateButton();
      if (zone) beginZone(zone, id);
    };
    if (!audio.paused && audio.volume > 0) fadeTo(0, 850, next);
    else next();
  }

  function findZone() {
    // The cinematic opening owns its audio clock until the reader enters.
    if (document.documentElement.classList.contains('cinema-locked')) return null;
    const focusY = innerHeight * 0.5;
    let best = null;
    let bestOverlap = 0;
    zones.forEach(zone => {
      if (zone.matches('details') && !zone.open) return;
      const rect = zone.getBoundingClientRect();
      if (rect.top <= focusY && rect.bottom >= focusY) {
        best = zone;
        bestOverlap = Infinity;
        return;
      }
      const overlap = Math.max(0, Math.min(rect.bottom, innerHeight) - Math.max(rect.top, 0));
      if (bestOverlap !== Infinity && overlap > bestOverlap && overlap >= Math.min(160, innerHeight * 0.25)) {
        best = zone;
        bestOverlap = overlap;
      }
    });
    return best;
  }

  let scheduled = false;
  function syncZone() {
    scheduled = false;
    changeZone(findZone());
  }
  function scheduleSync() {
    if (!scheduled) {
      scheduled = true;
      requestAnimationFrame(syncZone);
    }
  }

  button.addEventListener('pointerdown', () => {
    blockedClickArmed = autoplayBlocked && !userPaused;
  });
  button.addEventListener('click', () => {
    if (blockedClickArmed) {
      blockedClickArmed = false;
      autoplayBlocked = false;
      activeZone = null;
      syncZone();
      return;
    }
    userPaused = !userPaused;
    localStorage.setItem('lumen-music-muted', userPaused ? '1' : '0');
    autoplayBlocked = false;
    if (userPaused) {
      ++transitionId;
      fadeTo(0, 500, () => { saveProgress(true); audio.pause(); updateButton(); });
    } else {
      activeZone = null;
      syncZone();
    }
    updateButton();
  });

  function unlock() {
    if (!userPaused && activeZone && audio.paused) beginZone(activeZone, transitionId);
  }
  document.addEventListener('pointerdown', unlock, { once: true, capture: true });
  document.addEventListener('keydown', unlock, { once: true, capture: true });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      cancelFade();
      saveProgress(true);
      audio.pause();
      updateButton();
    } else {
      activeZone = null;
      syncZone();
    }
  });
  zones.filter(zone => zone.matches('details')).forEach(zone => zone.addEventListener('toggle', scheduleSync));
  audio.addEventListener('loadedmetadata', restoreProgress);
  audio.addEventListener('timeupdate', () => saveProgress(false));
  addEventListener('pagehide', () => saveProgress(true));
  addEventListener('scroll', scheduleSync, { passive: true });
  addEventListener('resize', scheduleSync);
  updateButton();
  syncZone();
})();
