(function () {
  // Light theme only — dark mode disabled
  function applyLight() {
    const root = document.documentElement;
    root.setAttribute("data-theme", "light");
    root.style.setProperty("--color-bg", "#f8fafc");
    root.style.setProperty("--color-bg-deep", "#f1f5f9");
    root.style.setProperty("--color-surface", "#ffffff");
    root.style.setProperty("--color-surface-2", "#f1f5f9");
    root.style.setProperty("--color-text", "#0f172a");
    root.style.setProperty("--color-muted", "#64748b");
    root.style.setProperty("--color-primary", "#0284c7");
    root.style.setProperty("--color-secondary", "#6366f1");
    root.style.setProperty("--color-border", "rgba(2,132,199,0.25)");
    root.style.setProperty("--color-accent", "#0ea5e9");
    try { localStorage.removeItem("bam-theme"); } catch (e) {}
  }
  applyLight();
  document.addEventListener("DOMContentLoaded", () => {
    applyLight();
    document.querySelectorAll(".btn").forEach(btn => {
      btn.addEventListener("pointerdown", (e) => {
        const r = btn.getBoundingClientRect();
        btn.style.setProperty("--x", ((e.clientX - r.left) / r.width * 100) + "%");
        btn.style.setProperty("--y", ((e.clientY - r.top) / r.height * 100) + "%");
      });
    });
  });
})();
