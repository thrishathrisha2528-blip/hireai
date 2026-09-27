/* ============================================
   HireAI — Shared Sidebar Component
   Injects sidebar HTML into #sidebarRoot on each page.
   Pass the current page id to highlight the active link.
   ============================================ */

function renderSidebar(activePage) {
  const links = [
    { id: "dashboard", label: "Dashboard", icon: "🏠", href: "dashboard.html" },
    { id: "jobs", label: "Job Descriptions", icon: "📋", href: "jobs.html" },
    { id: "screening", label: "Resume Screening", icon: "📄", href: "screening.html" },
    { id: "candidates", label: "Candidates", icon: "👥", href: "candidates.html" },
  ];

  const linksHtml = links.map(link => `
    <a class="sidebar-link ${link.id === activePage ? 'active' : ''}" href="${link.href}">
      <span>${link.icon}</span>
      <span class="label">${link.label}</span>
    </a>
  `).join("");

  const root = document.getElementById("sidebarRoot");
  if (!root) return;

  // Use the real logged-in user's name/email if available, otherwise fall back to dummy data.
  const realName = localStorage.getItem('hireai_user_name');
  const realEmail = localStorage.getItem('hireai_user_email');
  const displayName = (realName && realName.trim()) ? realName : (realEmail || DUMMY_USER.name);
  const displayRole = (realName || realEmail) ? "HR Recruiter" : DUMMY_USER.role;
  const initials = displayName.split(" ").filter(Boolean).map(n => n[0]).slice(0, 2).join("").toUpperCase();

  root.innerHTML = `
    <aside class="sidebar">
      <div class="sidebar-logo">⚡ <span class="label">HireAI</span></div>
      <nav class="sidebar-nav">
        ${linksHtml}
      </nav>
      <div class="sidebar-footer">
        <div class="flex items-center gap-sm mb-md">
          <div style="width:32px;height:32px;border-radius:50%;background:var(--color-primary-light);color:var(--color-primary);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;">
            ${initials}
          </div>
          <div class="label" style="line-height:1.2;">
            <div style="font-size:13px;font-weight:600;">${displayName}</div>
            <div style="font-size:11px;color:var(--color-text-muted);">${displayRole}</div>
          </div>
        </div>
        <a href="index.html" class="sidebar-link label" onclick="localStorage.removeItem('hireai_logged_in')" style="padding-left:14px;">
          🚪 <span class="label">Logout</span>
        </a>
        <button id="themeToggleBtn" class="theme-toggle" onclick="toggleTheme()">🌙 Dark Mode</button>
      </div>
    </aside>
  `;

  updateThemeToggleLabel();
}