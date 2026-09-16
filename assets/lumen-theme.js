(() => {
  'use strict';

  const STORAGE_KEY = 'theme';
  const systemTheme = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

  function savedMode() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved === 'dark' || saved === 'light' ? saved : 'auto';
    } catch (_) {
      return 'auto';
    }
  }

  function effectiveDark(mode = savedMode()) {
    return mode === 'dark' || (mode === 'auto' && !!(systemTheme && systemTheme.matches));
  }

  function updateButton(mode, dark) {
    const button = document.getElementById('themeToggle');
    if (!button) return;
    button.textContent = dark ? '🌙' : '☀️';
    button.dataset.themeMode = mode;
    if (mode === 'auto') {
      button.title = `自动主题：当前为${dark ? '暗色' : '亮色'}；点击临时切换`;
      button.setAttribute('aria-label', button.title);
    } else {
      button.title = `${dark ? '暗色' : '亮色'}模式；点击恢复跟随系统`;
      button.setAttribute('aria-label', button.title);
    }
  }

  function apply() {
    const mode = savedMode();
    const dark = effectiveDark(mode);
    document.documentElement.classList.toggle('dark', dark);
    document.documentElement.dataset.themeMode = mode;
    document.documentElement.style.colorScheme = dark ? 'dark' : 'light';
    updateButton(mode, dark);
  }

  function toggle() {
    const mode = savedMode();
    try {
      if (mode === 'auto') localStorage.setItem(STORAGE_KEY, effectiveDark(mode) ? 'light' : 'dark');
      else localStorage.removeItem(STORAGE_KEY);
    } catch (_) {}
    apply();
  }

  if (systemTheme) {
    const onChange = () => { if (savedMode() === 'auto') apply(); };
    if (systemTheme.addEventListener) systemTheme.addEventListener('change', onChange);
    else if (systemTheme.addListener) systemTheme.addListener(onChange);
  }

  window.LumenTheme = { init: apply, toggle, mode: savedMode };
  apply();
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', apply, { once: true });
})();
