(function () {
  function init() {
    const canvas = document.getElementById("hero-code-canvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const parent = canvas.parentElement;
    const lines = [
      "const build = () => deploy();",
      "function create() {",
      "  return design + code;",
      "}",
      "npm run build && ship()",
      "SELECT * FROM projects;",
      "async function scale() {",
      "  await optimize();",
      "}",
      "git commit -m 'ship'",
      "<BAM Studio />",
      "flex: 1; gap: 1rem;",
      "border-radius: 16px;",
      "export default App;",
      "flask run --debug",
      "vercel --prod",
      "Cloudinary.upload()",
      "postgres://neon",
    ];
    let w, h, drops = [];
    function resize() {
      const r = parent.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      const cssW = Math.max(280, r.width || 400);
      const cssH = Math.max(210, r.height || 300);
      w = canvas.width = Math.floor(cssW * dpr);
      h = canvas.height = Math.floor(cssH * dpr);
      canvas.style.width = cssW + "px";
      canvas.style.height = cssH + "px";
      const colW = 13 * dpr;
      const cols = Math.max(12, Math.floor(w / colW));
      drops = Array.from({ length: cols }, () => Math.random() * h);
    }
    resize();
    window.addEventListener("resize", resize);
    // solid base
    function frame() {
      const dpr = window.devicePixelRatio || 1;
      ctx.fillStyle = "rgba(7, 17, 29, 0.18)";
      ctx.fillRect(0, 0, w, h);
      ctx.font = (11 * dpr) + "px ui-monospace, Menlo, Consolas, monospace";
      const colW = 13 * dpr;
      drops.forEach((y, i) => {
        const text = lines[(i + Math.floor(y / (15 * dpr))) % lines.length];
        const x = i * colW;
        ctx.fillStyle = "rgba(56, 189, 248, 1)";
        ctx.fillText(text.charAt(0), x, y);
        ctx.fillStyle = "rgba(56, 189, 248, 0.45)";
        ctx.fillText(text.slice(1, 20), x + 8 * dpr, y);
        drops[i] = y > h + 30 ? -Math.random() * 50 : y + (1.15 + (i % 4) * 0.2) * dpr;
      });
      requestAnimationFrame(frame);
    }
    ctx.fillStyle = "#07111d";
    ctx.fillRect(0, 0, w, h);
    requestAnimationFrame(frame);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
