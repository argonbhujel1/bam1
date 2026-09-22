(function () {
  const canvas = document.getElementById("code-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const lines = [
    "const build = () => deploy();",
    "function createExperience() {",
    "  return design + code;",
    "}",
    "npm run build && ship()",
    "SELECT * FROM projects;",
    "async function scale() {",
    "  await optimize();",
    "}",
    "git commit -m 'ship it'",
    "<BAM Studio />",
    "flex: 1; gap: 1rem;",
    "border-radius: 16px;",
    "export default App;",
    "postgres://neon...",
    "flask run --debug",
    "Cloudinary.upload(file)",
    "def index(): return render()",
    "API_KEY = process.env",
    "margin: 0 auto;",
    "docker compose up",
    "vercel --prod",
  ];
  let w, h, drops = [];
  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
    const cols = Math.max(18, Math.floor(w / 14));
    drops = Array.from({ length: cols }, () => Math.random() * h);
  }
  resize();
  window.addEventListener("resize", resize);
  function frame() {
    // Light background trail — keep soft white wash so text stays readable
    ctx.fillStyle = "rgba(248,250,252,0.06)";
    ctx.fillRect(0, 0, w, h);
    ctx.font = "12px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace";
    drops.forEach((y, i) => {
      const text = lines[(i + Math.floor(y / 18)) % lines.length];
      const x = i * 14;
      ctx.fillStyle = "rgba(2, 132, 199, 0.9)";
      ctx.fillText(text.slice(0, 1), x, y);
      ctx.fillStyle = "rgba(2, 132, 199, 0.55)";
      ctx.fillText(text.slice(1, 26), x + 7, y);
      drops[i] = y > h + 30 ? -Math.random() * 60 : y + 1.1 + (i % 4) * 0.2;
    });
    requestAnimationFrame(frame);
  }
  // initial clear so animation starts visible immediately
  ctx.fillStyle = "rgba(248,250,252,1)";
  ctx.fillRect(0, 0, w, h);
  requestAnimationFrame(frame);
})();
