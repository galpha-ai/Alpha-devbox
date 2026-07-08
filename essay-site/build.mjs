// Minimal, dependency-free static-site generator for the essays.
// Reads the source markdown files and emits self-contained HTML pages
// styled in the spirit of situational-awareness.ai: clean, text-first,
// with a sticky table-of-contents sidebar and a zh/en language switch.
//
//   node essay-site/build.mjs
//
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const docs = (f) => join(__dirname, "..", "docs", "essays", f);
const out = (f) => join(__dirname, f);

// ---- tiny inline + block markdown renderer (scoped to these essays) ----
const esc = (s) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

const inline = (s) =>
  esc(s)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*(?!\s)(.+?)\*(?!\*)/g, "$1<em>$2</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

const slugify = (s) =>
  "sec-" +
  s
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, "-")
    .replace(/^-+|-+$/g, "");

// Render markdown body to { html, toc }. Supports headings, lists, blockquote,
// fenced code, hr, tables (pipe), and paragraphs.
function render(md) {
  const lines = md.split("\n");
  const html = [];
  const toc = [];
  let i = 0;
  let inList = null;

  const closeList = () => {
    if (inList) {
      html.push(`</${inList}>`);
      inList = null;
    }
  };

  while (i < lines.length) {
    const line = lines[i];

    // fenced code block
    if (line.startsWith("```")) {
      closeList();
      const buf = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) {
        buf.push(esc(lines[i]));
        i++;
      }
      i++;
      html.push(`<pre class="block"><code>${buf.join("\n")}</code></pre>`);
      continue;
    }

    // table (pipe rows; second row is the --- separator)
    if (
      line.trim().startsWith("|") &&
      i + 1 < lines.length &&
      /^\s*\|[-:\s|]+\|\s*$/.test(lines[i + 1])
    ) {
      closeList();
      const cells = (r) =>
        r
          .trim()
          .replace(/^\||\|$/g, "")
          .split("|")
          .map((c) => c.trim());
      const head = cells(line);
      i += 2;
      const rows = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) {
        rows.push(cells(lines[i]));
        i++;
      }
      const th = head.map((c) => `<th>${inline(c)}</th>`).join("");
      const trs = rows
        .map(
          (r) => `<tr>${r.map((c) => `<td>${inline(c)}</td>`).join("")}</tr>`
        )
        .join("");
      html.push(
        `<div class="tablewrap"><table><thead><tr>${th}</tr></thead><tbody>${trs}</tbody></table></div>`
      );
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

    // blockquote (multi-line)
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

    // ordered list
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

    // unordered list
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

    // paragraph
    closeList();
    const buf = [line];
    i++;
    while (
      i < lines.length &&
      lines[i].trim() !== "" &&
      !/^(#{1,4}\s|>|```|---+\s*$|\d+\.\s|[-*]\s|\|)/.test(lines[i])
    ) {
      buf.push(lines[i]);
      i++;
    }
    html.push(`<p>${inline(buf.join(" "))}</p>`);
  }
  closeList();
  return { html: html.join("\n"), toc };
}

const STYLE = `
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
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;
}
.wrap{display:grid;grid-template-columns:1fr;max-width:74rem;margin:0 auto;padding:0 1.25rem}
@media(min-width:1100px){
  .wrap{grid-template-columns:16rem minmax(0,var(--max));gap:3.5rem;justify-content:center}
}
nav.toc{display:none}
@media(min-width:1100px){
  nav.toc{
    display:block;position:sticky;top:0;align-self:start;
    height:100vh;overflow-y:auto;padding:3.5rem 0 3rem;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans CJK SC",sans-serif;
    font-size:13.5px;line-height:1.5;
  }
  nav.toc .toc-title{text-transform:uppercase;letter-spacing:.12em;color:var(--muted);font-size:11px;margin-bottom:1rem}
  nav.toc a{display:block;color:var(--muted);text-decoration:none;padding:.2rem 0;border-left:2px solid transparent;padding-left:.75rem}
  nav.toc a:hover{color:var(--fg)}
  nav.toc a.lvl3{padding-left:1.6rem;font-size:12.5px;opacity:.85}
}
article{padding:3.5rem 0 6rem;max-width:var(--max)}
header.masthead{border-bottom:1px solid var(--rule);padding-bottom:1.75rem;margin-bottom:2.5rem}
.topbar{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:1rem;gap:1rem;flex-wrap:wrap}
.kicker{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;text-transform:uppercase;letter-spacing:.18em;font-size:12px;color:var(--accent)}
.langswitch{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:12.5px}
.langswitch a{color:var(--muted);text-decoration:none;padding:.1rem .35rem}
.langswitch a.active{color:var(--fg);font-weight:700;border-bottom:2px solid var(--accent)}
.langswitch a:hover{color:var(--fg)}
.langswitch .navsep{color:var(--rule);padding:0 .2rem}
h1{font-size:2.5rem;line-height:1.18;margin:.2rem 0 .6rem;letter-spacing:-.01em}
.sub{color:var(--muted);font-size:1.15rem;font-style:italic;margin:0}
.byline{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:13px;color:var(--muted);margin-top:1.4rem}
.byline a{color:var(--link)}
h2{font-size:1.65rem;line-height:1.25;margin:3.2rem 0 1rem;padding-top:1rem;letter-spacing:-.005em}
h3{font-size:1.25rem;margin:2.2rem 0 .8rem;color:#2c2a26}
h4{font-size:1.05rem;margin:1.6rem 0 .6rem;color:var(--muted);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
p{margin:1.1rem 0}
strong{font-weight:700}
a{color:var(--link);text-decoration:underline;text-underline-offset:2px;text-decoration-thickness:.06em}
hr{border:0;border-top:1px solid var(--rule);margin:3rem 0}
blockquote{margin:1.8rem 0;padding:.4rem 0 .4rem 1.4rem;border-left:3px solid var(--accent);color:#3a352d;font-style:italic;font-size:1.08rem}
ul,ol{margin:1.1rem 0;padding-left:1.5rem}
li{margin:.45rem 0}
li.cont{list-style:none;margin-left:-.4rem;color:var(--muted);font-size:.96em}
code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.86em;background:#efeae0;padding:.1em .35em;border-radius:3px}
pre.block{background:#1c1b19;color:#e8e2d6;padding:1.2rem 1.4rem;border-radius:8px;overflow-x:auto;font-size:13px;line-height:1.5;margin:1.8rem 0}
pre.block code{background:none;color:inherit;padding:0;font-size:inherit}
.tablewrap{overflow-x:auto;margin:1.8rem 0}
table{border-collapse:collapse;width:100%;font-size:.9rem;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans CJK SC",sans-serif}
th,td{text-align:left;padding:.55rem .7rem;border-bottom:1px solid var(--rule);vertical-align:top}
th{color:var(--accent);font-size:.78rem;text-transform:uppercase;letter-spacing:.04em}
footer{border-top:1px solid var(--rule);margin-top:4rem;padding-top:1.5rem;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:13px;color:var(--muted)}
footer a{color:var(--link)}
::selection{background:#e9d9c2}
`;

// Series navigation across the parts, plus a language link.
const SERIES = [
  { file: "index.html", label: "I · Roadmap" },
  { file: "frontiers.html", label: "II · Frontiers" },
  { file: "markets.html", label: "III · Markets" },
  { file: "critique.html", label: "IV · Critique" },
];

function seriesNav(currentFile) {
  const parts = SERIES.map(
    (p) =>
      `<a href="${p.file}"${p.file === currentFile ? ' class="active"' : ""}>${p.label}</a>`
  ).join("");
  const langLink =
    currentFile === "zh.html"
      ? `<a href="index.html">EN</a>`
      : `<a href="zh.html">中文</a>`;
  return `${parts}<span class="navsep">·</span>${langLink}`;
}

function page(cfg, pages) {
  const { html, toc } = render(readFileSync(cfg.src, "utf8"));
  const tocHtml = toc
    .map(
      (t) =>
        `<a class="lvl${t.level}" href="#${t.id}">${esc(
          t.text.replace(/\*\*/g, "")
        )}</a>`
    )
    .join("\n");

  return `<!doctype html>
<html lang="${cfg.htmlLang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${cfg.title}</title>
<meta name="description" content="${cfg.desc}">
<style>${STYLE}</style>
</head>
<body>
<div class="wrap">
<nav class="toc">
  <div class="toc-title">${cfg.tocTitle}</div>
  ${tocHtml}
</nav>
<article>
<header class="masthead">
  <div class="topbar">
    <span class="kicker">${cfg.kicker}</span>
    <span class="langswitch">${seriesNav(cfg.file)}</span>
  </div>
  <h1>${cfg.h1}</h1>
  <p class="sub">${cfg.sub}</p>
  <div class="byline">${cfg.byline}</div>
</header>
${html}
<footer>${cfg.footer}</footer>
</article>
</div>
</body>
</html>
`;
}

// ---- page configs ----
const EN_KICKER = "The Embodiment Awakening · 2025–2030";
const EN_FOOTER =
  "© 2026 · A forward-looking judgment, not a prophecy. Part I · Part II · Part III.";

const PAGES = [
  {
    file: "index.html",
    out: out("index.html"),
    src: docs("physical-intelligence-2030.en.md"),
    htmlLang: "en",
    title: "The Embodiment Awakening · A Roadmap for the Robotics Decade",
    desc:
      "A Situational-Awareness-style roadmap for physical intelligence, 2025–2030: the planner→cerebellum architecture, the ego-centric data bet, scaling-law math, robot hardware (motors, reducers, drive control), and a one-to-one investment map with tickers.",
    tocTitle: "Part I · Roadmap",
    kicker: EN_KICKER,
    h1: "The Embodiment Awakening",
    sub: "A roadmap for the robotics decade — from bits to atoms, 2025–2030. The technology; the market map and the critique follow as Parts III and IV.",
    byline: "Part I of IV · 2026 · a judgment call, not a prophecy",
    footer: EN_FOOTER,
  },
  {
    file: "frontiers.html",
    out: out("frontiers.html"),
    src: docs("new-verbs-and-recursive-robotics.en.md"),
    htmlLang: "en",
    title: "New Verbs and Self-Replication · The Embodiment Awakening II",
    desc:
      "Part II: when robots learn a genuinely new verb (out-of-distribution tasks) and when robots start building robots — a closure-degree framework, the chip lock, and why physical takeoff is soft.",
    tocTitle: "Part II · Frontiers",
    kicker: EN_KICKER,
    h1: "New Verbs and Self-Replication",
    sub: "Two longer-horizon phase transitions: inventing new skills, and robots building robots.",
    byline: "Part II of IV · 2026 · a judgment call, not a prophecy",
    footer: EN_FOOTER,
  },
  {
    file: "markets.html",
    out: out("markets.html"),
    src: docs("public-markets-map.md"),
    htmlLang: "en",
    title: "The Public-Markets Map · The Embodiment Awakening III",
    desc:
      "Part III: each technical thesis mapped to listed companies — a barbell of data/verification and actuator choke points (reducers, roller screws, magnets, grinding machines), a consolidated ticker table, and a quarterly dashboard. Not investment advice.",
    tocTitle: "Part III · Markets",
    kicker: EN_KICKER,
    h1: "The Public-Markets Map",
    sub: "Each technical thesis mapped to where value accrues — expressed through listed companies. Research analysis, not investment advice.",
    byline: "Part III of IV · 2026 · research analysis, not investment advice",
    footer: EN_FOOTER,
  },
  {
    file: "critique.html",
    out: out("critique.html"),
    src: docs("robotics-critique-timing-risk.md"),
    htmlLang: "en",
    title: "The Case Against This Timeline · The Embodiment Awakening III",
    desc:
      "Part III: a red-team of the roadmap — the self-driving analogy, the reliability chasm, an assumption-by-assumption risk table, and the funding winter that can bury correct theses in the middle.",
    tocTitle: "Part IV · Critique",
    kicker: EN_KICKER,
    h1: "The Case Against This Timeline",
    sub: "A red-team of the roadmap — where the bet goes wrong, especially on timing.",
    byline: "Part IV of IV · 2026 · written against Part I",
    footer: EN_FOOTER,
  },
  {
    file: "zh.html",
    out: out("zh.html"),
    src: docs("physical-intelligence-2030.md"),
    htmlLang: "zh-CN",
    title: "具身觉醒 · 通往物理智能的未来五年（中文原版）",
    desc:
      "《具身觉醒》中文原版：模型突破、机器人数据、灵巧手、Scaling Law 与稀土瓶颈。",
    tocTitle: "中文原版 · 目录",
    kicker: "具身觉醒 · 2025–2030",
    h1: "具身觉醒",
    sub: "通往物理智能的未来五年 —— 一篇关于人类如何把智能装进身体的判断书（中文原版，英文系列见 EN）",
    byline: "中文原版 · 2026 · 一份判断书，不是预言",
    footer: "© 2026 · 本文为前瞻性判断，预测会错，方向不会。英文系列见 EN。",
  },
];

for (const cfg of PAGES) {
  const out = page(cfg, PAGES);
  writeFileSync(cfg.out, out);
  console.log(`Wrote ${cfg.out} (${(out.length / 1024).toFixed(1)} KB)`);
}
