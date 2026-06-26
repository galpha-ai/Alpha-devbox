// Minimal, dependency-free static-site generator for the essay.
// Reads the source markdown and emits a single self-contained index.html
// styled in the spirit of situational-awareness.ai: clean, text-first,
// with a sticky table-of-contents sidebar.
//
//   node essay-site/build.mjs
//
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SRC = join(__dirname, "..", "docs", "essays", "physical-intelligence-2030.md");
const OUT = join(__dirname, "index.html");

const md = readFileSync(SRC, "utf8");

// ---- tiny inline + block markdown renderer (scoped to this essay) ----
const esc = (s) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

const inline = (s) =>
  esc(s)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*(?!\s)(.+?)\*(?!\*)/g, "$1<em>$2</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

const slugify = (s) => {
  // keep CJK, ascii word chars; collapse the rest to hyphens
  return (
    "sec-" +
    s
      .toLowerCase()
      .replace(/[^\p{L}\p{N}]+/gu, "-")
      .replace(/^-+|-+$/g, "")
  );
};

const lines = md.split("\n");
const html = [];
const toc = [];
let i = 0;
let inList = null; // 'ul' | 'ol'

const closeList = () => {
  if (inList) {
    html.push(`</${inList}>`);
    inList = null;
  }
};

while (i < lines.length) {
  let line = lines[i];

  // fenced code block
  if (line.startsWith("```")) {
    closeList();
    const buf = [];
    i++;
    while (i < lines.length && !lines[i].startsWith("```")) {
      buf.push(esc(lines[i]));
      i++;
    }
    i++; // skip closing fence
    html.push(`<pre class="block"><code>${buf.join("\n")}</code></pre>`);
    continue;
  }

  // horizontal rule
  if (/^---+\s*$/.test(line)) {
    closeList();
    html.push("<hr>");
    i++;
    continue;
  }

  // headings
  const h = line.match(/^(#{1,4})\s+(.*)$/);
  if (h) {
    closeList();
    const level = h[1].length;
    const text = h[2].trim();
    if (level === 2 || level === 3) {
      const id = slugify(text) + "-" + html.length;
      toc.push({ level, text, id });
      html.push(`<h${level} id="${id}">${inline(text)}</h${level}>`);
    } else {
      html.push(`<h${level}>${inline(text)}</h${level}>`);
    }
    i++;
    continue;
  }

  // blockquote (may span multiple lines)
  if (line.startsWith(">")) {
    closeList();
    const buf = [];
    while (i < lines.length && lines[i].startsWith(">")) {
      buf.push(lines[i].replace(/^>\s?/, ""));
      i++;
    }
    html.push(`<blockquote>${inline(buf.join(" "))}</blockquote>`);
    continue;
  }

  // ordered list item
  const ol = line.match(/^(\d+)\.\s+(.*)$/);
  if (ol) {
    if (inList !== "ol") {
      closeList();
      html.push("<ol>");
      inList = "ol";
    }
    html.push(`<li>${inline(ol[2])}</li>`);
    i++;
    continue;
  }

  // unordered list item
  const ul = line.match(/^[-*]\s+(.*)$/);
  if (ul) {
    if (inList !== "ul") {
      closeList();
      html.push("<ul>");
      inList = "ul";
    }
    html.push(`<li>${inline(ul[1])}</li>`);
    i++;
    continue;
  }

  // indented continuation of a list item
  if (inList && /^\s{2,}\S/.test(line)) {
    html.push(`<li class="cont">${inline(line.trim())}</li>`);
    i++;
    continue;
  }

  // blank line
  if (line.trim() === "") {
    closeList();
    i++;
    continue;
  }

  // paragraph (accumulate until blank / block boundary)
  closeList();
  const buf = [line];
  i++;
  while (
    i < lines.length &&
    lines[i].trim() !== "" &&
    !/^(#{1,4}\s|>|```|---+\s*$|\d+\.\s|[-*]\s)/.test(lines[i])
  ) {
    buf.push(lines[i]);
    i++;
  }
  html.push(`<p>${inline(buf.join(" "))}</p>`);
}
closeList();

// ---- table of contents ----
const tocHtml = toc
  .map(
    (t) =>
      `<a class="lvl${t.level}" href="#${t.id}">${esc(
        t.text.replace(/\*\*/g, "")
      )}</a>`
  )
  .join("\n");

const page = `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>具身觉醒 · 通往物理智能的未来五年</title>
<meta name="description" content="一篇 Situational-Awareness 风格的判断书：人类如何在五年内把智能装进身体。模型突破、机器人数据、灵巧手、Scaling Law 与稀土瓶颈。">
<style>
:root{
  --bg:#faf8f4; --fg:#1c1b19; --muted:#6b6760; --rule:#e4ded3;
  --accent:#8a5a2b; --link:#9a3b1f; --max:46rem;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0;background:var(--bg);color:var(--fg);
  font-family:Georgia,"Songti SC","Noto Serif CJK SC",ui-serif,serif;
  font-size:19px;line-height:1.75;
  -webkit-font-smoothing:antialiased;
  text-rendering:optimizeLegibility;
}
.wrap{display:grid;grid-template-columns:1fr;max-width:74rem;margin:0 auto;padding:0 1.25rem}
@media(min-width:1100px){
  .wrap{grid-template-columns:16rem minmax(0,var(--max));gap:3.5rem;justify-content:center}
}
/* sidebar TOC */
nav.toc{display:none}
@media(min-width:1100px){
  nav.toc{
    display:block;position:sticky;top:0;align-self:start;
    height:100vh;overflow-y:auto;padding:3.5rem 0 3rem;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans CJK SC",sans-serif;
    font-size:13.5px;line-height:1.5;
  }
  nav.toc .toc-title{
    text-transform:uppercase;letter-spacing:.12em;color:var(--muted);
    font-size:11px;margin-bottom:1rem;
  }
  nav.toc a{display:block;color:var(--muted);text-decoration:none;padding:.2rem 0;border-left:2px solid transparent;padding-left:.75rem}
  nav.toc a:hover{color:var(--fg)}
  nav.toc a.lvl3{padding-left:1.6rem;font-size:12.5px;opacity:.85}
}
/* article */
article{padding:3.5rem 0 6rem;max-width:var(--max)}
header.masthead{border-bottom:1px solid var(--rule);padding-bottom:1.75rem;margin-bottom:2.5rem}
header.masthead .kicker{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  text-transform:uppercase;letter-spacing:.18em;font-size:12px;color:var(--accent);margin-bottom:1rem
}
h1{font-size:2.5rem;line-height:1.18;margin:.2rem 0 .6rem;letter-spacing:-.01em}
header.masthead .sub{color:var(--muted);font-size:1.15rem;font-style:italic;margin:0}
header.masthead .byline{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  font-size:13px;color:var(--muted);margin-top:1.4rem
}
h2{font-size:1.65rem;line-height:1.25;margin:3.2rem 0 1rem;padding-top:1rem;letter-spacing:-.005em}
h3{font-size:1.25rem;margin:2.2rem 0 .8rem;color:#2c2a26}
h4{font-size:1.05rem;margin:1.6rem 0 .6rem;color:var(--muted);
   font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
p{margin:1.1rem 0}
strong{font-weight:700}
a{color:var(--link);text-decoration:underline;text-underline-offset:2px;text-decoration-thickness:.06em}
hr{border:0;border-top:1px solid var(--rule);margin:3rem 0}
blockquote{
  margin:1.8rem 0;padding:.4rem 0 .4rem 1.4rem;border-left:3px solid var(--accent);
  color:#3a352d;font-style:italic;font-size:1.08rem
}
ul,ol{margin:1.1rem 0;padding-left:1.5rem}
li{margin:.45rem 0}
li.cont{list-style:none;margin-left:-.4rem;color:var(--muted);font-size:.96em}
code{
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  font-size:.86em;background:#efeae0;padding:.1em .35em;border-radius:3px
}
pre.block{
  background:#1c1b19;color:#e8e2d6;padding:1.2rem 1.4rem;border-radius:8px;
  overflow-x:auto;font-size:13px;line-height:1.5;margin:1.8rem 0
}
pre.block code{background:none;color:inherit;padding:0;font-size:inherit}
footer{border-top:1px solid var(--rule);margin-top:4rem;padding-top:1.5rem;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  font-size:13px;color:var(--muted)}
::selection{background:#e9d9c2}
</style>
</head>
<body>
<div class="wrap">
<nav class="toc">
  <div class="toc-title">目录</div>
  ${tocHtml}
</nav>
<article>
<header class="masthead">
  <div class="kicker">From Bits to Atoms · 2025–2030</div>
  <h1>具身觉醒</h1>
  <p class="sub">通往物理智能的未来五年 —— 一篇关于人类如何把智能装进身体的判断书</p>
  <div class="byline">2026 · 一份判断书，不是预言</div>
</header>
${html.join("\n")}
<footer>
  © 2026 · 本文为前瞻性判断，预测会错，方向不会。
</footer>
</article>
</div>
</body>
</html>
`;

writeFileSync(OUT, page);
console.log(`Wrote ${OUT} (${(page.length / 1024).toFixed(1)} KB, ${toc.length} TOC entries)`);
