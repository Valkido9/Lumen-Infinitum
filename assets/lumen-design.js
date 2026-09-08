/* Shared archive navigation and reading progress. */
(() => {
  const progress = document.createElement('div');
  progress.className = 'reading-progress';
  progress.setAttribute('aria-hidden', 'true');
  document.body.append(progress);
  const updateProgress = () => {
    const start = 0;
    const total = document.documentElement.scrollHeight - innerHeight - start;
    progress.style.width = `${Math.max(0, Math.min(100, (scrollY - start) / Math.max(1, total) * 100))}%`;
  };
  addEventListener('scroll', updateProgress, {passive:true});
  addEventListener('resize', updateProgress);
  updateProgress();
  document.querySelectorAll('.header nav a').forEach(a => {
    if(a.classList.contains('active')) a.setAttribute('aria-current','page');
  });
})();
