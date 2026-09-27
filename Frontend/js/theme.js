/* ============================================
   HireAI — Theme Toggle (Light/Dark)
   Applies saved theme on load; toggle button calls toggleTheme().
   ============================================ */

function applyStoredTheme() {
  const saved = localStorage.getItem('hireai_theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('hireai_theme', next);
  updateThemeToggleLabel();
}

function updateThemeToggleLabel() {
  const btn = document.getElementById('themeToggleBtn');
  if (!btn) return;
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  btn.innerHTML = isDark ? '☀️ Light' : '🌙 Dark';
}

// Apply theme immediately (before page paints) to avoid a flash of the wrong theme.
applyStoredTheme();