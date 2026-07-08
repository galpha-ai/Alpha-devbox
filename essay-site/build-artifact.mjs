// Builds a single self-contained, tabbed page containing all parts of the
// series — for hosting as one link (e.g. a Claude Artifact) that opens well on
// a phone. Output is CONTENT-ONLY (no <!doctype>/<html>/<head>/<body>): a
// <style> block, the markup, and an inline <script>, suitable for the Artifact
// wrapper. Reuses the same tiny markdown renderer as build.mjs.
//
//   node essay-site/build-artifact.mjs
//
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const docs = (f) => join(__dirname, "..", "docs", "essays", f);
const OUT = join(__dirname, "artifact.html");

const esc = (s) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const inline = (s) =>
  esc(s)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*(?!\s)(.+?)\*(?!\*)/g, "$1<em>$2</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

function render(md) {
  const lines = md.split("\n");
  const html = [];
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
    if (line.startsWith("```")) {
      closeList();
      const buf = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) buf.push(esc(lines[i++]));
      i++;
      html.push(`<pre class="term"><code>${buf.join("\n")}</code></pre>`);
      continue;
    }
    if (
      line.trim().startsWith("|") &&
      i + 1 < lines.length &&
      /^\s*\|[-:\s|]+\|\s*$/.test(lines[i + 1])
    ) {
      closeList();
      const cells = (r) =>
        r.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
      const head = cells(line);
      i += 2;
      const rows = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) rows.push(cells(lines[i++]));
      const th = head.map((c) => `<th>${inline(c)}</th>`).join("");
      const trs = rows
        .map((r) => `<tr>${r.map((c) => `<td>${inline(c)}</td>`).join("")}</tr>`)
        .join("");
      html.push(
        `<div class="tablewrap"><table><thead><tr>${th}</tr></thead><tbody>${trs}</tbody></table></div>`
      );
      continue;
    }
    if (/^---+\s*$/.test(line)) {
      closeList();
      html.push('<hr>');
      i++;
      continue;
    }
    const h = line.match(/^(#{1,4})\s+(.*)$/);
    if (h) {
      closeList();
      const lvl = h[1].length;
      html.push(`<h${lvl}>${inline(h[2].trim())}</h${lvl}>`);
      i++;
      continue;
    }
    if (line.startsWith(">")) {
      closeList();
      const buf = [];
      while (i < lines.length && lines[i].startsWith(">")) buf.push(lines[i++].replace(/^>\s?/, ""));
      html.push(`<blockquote>${inline(buf.join(" "))}</blockquote>`);
      continue;
    }
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
    if (inList && /^\s{2,}\S/.test(line)) {
      html.push(`<li class="cont">${inline(line.trim())}</li>`);
      i++;
      continue;
    }
    if (line.trim() === "") {
      closeList();
      i++;
      continue;
    }
    closeList();
    const buf = [line];
    i++;
    while (
      i < lines.length &&
      lines[i].trim() !== "" &&
      !/^(#{1,4}\s|>|```|---+\s*$|\d+\.\s|[-*]\s|\|)/.test(lines[i])
    ) buf.push(lines[i++]);
    html.push(`<p>${inline(buf.join(" "))}</p>`);
  }
  closeList();
  return html.join("\n");
}

// Strip the leading H1 + metadata block from a doc body, because the masthead
// renders the title itself. Cut everything up to and including the first "---"
// rule so the article flows straight into its intro (no leading empty band).
function stripLede(md) {
  const m = md.match(/\n---+[ \t]*\n/);
  return m ? md.slice(m.index + m[0].length) : md;
}

const PARTS = [
  {
    id: "p1",
    tab: "I · Roadmap",
    eyebrow: "Part I — Roadmap",
    h1: "The Embodiment Awakening",
    sub: "A roadmap for the robotics decade — from bits to atoms, 2025–2030. Section One is the technology; Section Two maps each thesis to tradable exposure.",
    src: "physical-intelligence-2030.en.md",
  },
  {
    id: "p2",
    tab: "II · Frontiers",
    eyebrow: "Part II — Frontiers",
    h1: "New Verbs and Self-Replication",
    sub: "Two longer-horizon phase transitions: inventing new skills, and robots building robots.",
    src: "new-verbs-and-recursive-robotics.en.md",
  },
  {
    id: "p3",
    tab: "III · Markets",
    eyebrow: "Part III — Public-Markets Map",
    h1: "The Public-Markets Map",
    sub: "Each technical thesis mapped to listed companies. Research analysis, not investment advice.",
    src: "public-markets-map.md",
  },
  {
    id: "p4",
    tab: "IV · Critique",
    eyebrow: "Part IV — Critique",
    h1: "The Case Against This Timeline",
    sub: "A red-team of the roadmap — where the bet goes wrong, especially on timing.",
    src: "robotics-critique-timing-risk.md",
    warn: true,
  },
  {
    id: "zh",
    tab: "中文",
    eyebrow: "中文原版 — Part I",
    h1: "具身觉醒",
    sub: "通往物理智能的未来五年 —— 一份判断书。英文系列见上方标签页。",
    src: "physical-intelligence-2030.md",
    zh: true,
  },
];

const STYLE = `
:root{
  --paper:#ECEEEF; --panel:#F4F5F6; --ink:#15181B; --muted:#59626A;
  --rule:#D3D8DB; --accent:#1B4A6B; --bright:#2E7FB8; --warn:#A63A2A;
  --term:#14181B; --term-ink:#D8E3E8; --term-dim:#6E8894;
  --serif:"Charter","Iowan Old Style","Palatino",Georgia,"Times New Roman",ui-serif,serif;
  --sans:-apple-system,BlinkMacSystemFont,"Helvetica Neue","Segoe UI",Roboto,system-ui,sans-serif;
  --mono:ui-monospace,"SF Mono","SFMono-Regular",Menlo,Consolas,monospace;
}
*{box-sizing:border-box}
.ea-root{background:var(--paper);color:var(--ink);
  font-family:var(--serif);font-size:18px;line-height:1.72;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;
  -webkit-text-size-adjust:100%;}
.ea-root ::selection{background:#cfe0ec}
/* progress hairline */
.ea-progress{position:fixed;top:0;left:0;height:2px;width:0;z-index:60;
  background:var(--bright);transition:width .06s linear}
/* top bar */
.ea-bar{position:sticky;top:0;z-index:50;background:rgba(236,238,239,.92);
  backdrop-filter:saturate(1.4) blur(8px);border-bottom:1px solid var(--rule)}
.ea-bar-in{max-width:44rem;margin:0 auto;padding:.55rem 1.1rem;
  display:flex;align-items:center;gap:1rem;justify-content:space-between}
.ea-brand{font-family:var(--mono);font-size:11px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--accent);white-space:nowrap}
.ea-tabs{display:flex;gap:.15rem;overflow-x:auto;scrollbar-width:none}
.ea-tabs::-webkit-scrollbar{display:none}
.ea-tab{font-family:var(--sans);font-size:12.5px;font-weight:600;
  color:var(--muted);background:none;border:0;cursor:pointer;
  padding:.35rem .5rem;border-radius:6px;white-space:nowrap;
  border-bottom:2px solid transparent}
.ea-tab:hover{color:var(--ink)}
.ea-tab.active{color:var(--accent);border-bottom-color:var(--accent)}
.ea-tab:focus-visible{outline:2px solid var(--bright);outline-offset:2px}
/* panels */
.ea-wrap{max-width:44rem;margin:0 auto;padding:0 1.1rem}
.ea-panel{display:none;padding:2.4rem 0 5rem;animation:ea-fade .28s ease}
.ea-panel.active{display:block}
@media(prefers-reduced-motion:reduce){.ea-panel{animation:none}}
@keyframes ea-fade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
/* masthead */
.ea-mast{border-bottom:1px solid var(--rule);padding-bottom:1.6rem;
  margin-bottom:2.2rem;padding-top:1.4rem}
.ea-eyebrow{font-family:var(--mono);font-size:11.5px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--accent);
  display:inline-block;padding-bottom:.5rem;margin-bottom:.9rem;
  border-bottom:2px solid var(--accent)}
.ea-h1{font-family:var(--sans);font-weight:800;letter-spacing:-.021em;
  font-size:clamp(2rem,7vw,2.9rem);line-height:1.08;margin:.1rem 0 .6rem;
  text-wrap:balance}
.ea-sub{font-family:var(--serif);font-style:italic;color:var(--muted);
  font-size:1.06rem;line-height:1.5;margin:0;max-width:34rem}
/* article typography */
.ea-body{max-width:40rem}
.ea-body h1{display:none}
.ea-body h2{font-family:var(--sans);font-weight:750;letter-spacing:-.014em;
  font-size:1.5rem;line-height:1.18;margin:2.9rem 0 .9rem;text-wrap:balance;
  padding-top:.9rem;border-top:1px solid var(--rule)}
.ea-body h3{font-family:var(--sans);font-weight:700;font-size:1.16rem;
  margin:1.9rem 0 .6rem;color:#232a30;letter-spacing:-.01em}
.ea-body h4{font-family:var(--mono);text-transform:uppercase;letter-spacing:.06em;
  font-size:.82rem;color:var(--muted);margin:1.5rem 0 .5rem}
.ea-body p{margin:1.05rem 0}
.ea-body strong{font-weight:700}
.ea-body em{font-style:italic}
.ea-body a{color:var(--accent);text-decoration:underline;
  text-underline-offset:2px;text-decoration-thickness:.06em}
.ea-body a:hover{color:var(--bright)}
.ea-body hr{border:0;border-top:1px solid var(--rule);margin:2.6rem 0}
.ea-body blockquote{margin:1.7rem 0;padding:.5rem 0 .5rem 1.3rem;
  border-left:3px solid var(--accent);font-style:italic;color:#2b333a;
  font-size:1.05rem}
.ea-body ul,.ea-body ol{margin:1.05rem 0;padding-left:1.4rem}
.ea-body li{margin:.4rem 0}
.ea-body li.cont{list-style:none;margin-left:-.3rem;color:var(--muted);font-size:.95em}
.ea-body code{font-family:var(--mono);font-size:.85em;
  background:#dfe4e7;color:#1c2529;padding:.1em .34em;border-radius:4px}
/* terminal cards for math/diagrams */
.ea-body pre.term{font-family:var(--mono);background:var(--term);color:var(--term-ink);
  font-size:12.5px;line-height:1.55;padding:1.05rem 1.15rem;border-radius:9px;
  overflow-x:auto;margin:1.7rem 0;border:1px solid #23303a;
  box-shadow:0 1px 0 rgba(255,255,255,.4)}
.ea-body pre.term code{background:none;color:inherit;padding:0;font-size:inherit}
/* data tables */
.ea-body .tablewrap{overflow-x:auto;margin:1.7rem 0;
  border:1px solid var(--rule);border-radius:9px}
.ea-body table{border-collapse:collapse;width:100%;
  font-family:var(--sans);font-size:.86rem;font-variant-numeric:tabular-nums}
.ea-body th,.ea-body td{text-align:left;padding:.55rem .7rem;
  border-bottom:1px solid var(--rule);vertical-align:top}
.ea-body thead th{background:#e3e7e9;color:var(--accent);
  font-family:var(--mono);font-size:.72rem;text-transform:uppercase;
  letter-spacing:.04em;position:sticky;top:0}
.ea-body tbody tr:last-child td{border-bottom:0}
.ea-body td code{background:#e7ebed}
.ea-foot{margin-top:3rem;padding-top:1.2rem;border-top:1px solid var(--rule);
  font-family:var(--mono);font-size:11.5px;letter-spacing:.03em;color:var(--muted)}
/* Part III wears the warning accent */
.ea-panel.warn{--accent:var(--warn);--bright:#c85a45}
/* CJK gets a system serif that renders on iOS */
.ea-panel.zh{--serif:"Songti SC","Noto Serif CJK SC",Georgia,ui-serif,serif}
`;

const panels = PARTS.map((p) => {
  const md = readFileSync(docs(p.src), "utf8");
  const body = render(stripLede(md));
  const cls = `ea-panel${p.id === "p1" ? " active" : ""}${p.warn ? " warn" : ""}${p.zh ? " zh" : ""}`;
  return `<section id="${p.id}" class="${cls}" role="tabpanel" aria-label="${esc(p.tab)}">
  <div class="ea-wrap">
    <header class="ea-mast">
      <div class="ea-eyebrow">${esc(p.eyebrow)}</div>
      <h1 class="ea-h1">${esc(p.h1)}</h1>
      <p class="ea-sub">${esc(p.sub)}</p>
    </header>
    <div class="ea-body">${body}
      <div class="ea-foot">The Embodiment Awakening · 2026 · a judgment call, not a prophecy</div>
    </div>
  </div>
</section>`;
}).join("\n");

const tabs = PARTS.map(
  (p) =>
    `<button class="ea-tab${p.id === "p1" ? " active" : ""}" role="tab" data-tab="${p.id}"${
      p.id === "p1" ? ' aria-selected="true"' : ' aria-selected="false"'
    }>${esc(p.tab)}</button>`
).join("");

const SCRIPT = `
(function(){
  var root=document.currentScript.closest('.ea-root')||document;
  var tabs=root.querySelectorAll('.ea-tab');
  var panels=root.querySelectorAll('.ea-panel');
  var bar=root.querySelector('.ea-progress');
  function show(id){
    panels.forEach(function(p){p.classList.toggle('active',p.id===id);});
    tabs.forEach(function(t){var on=t.dataset.tab===id;
      t.classList.toggle('active',on);t.setAttribute('aria-selected',on?'true':'false');});
    window.scrollTo({top:0,behavior:'instant' in window?'instant':'auto'});
    if(location.hash.slice(1)!==id) history.replaceState(null,'','#'+id);
  }
  tabs.forEach(function(t){t.addEventListener('click',function(){show(t.dataset.tab);});});
  function onScroll(){
    var h=document.documentElement;
    var max=h.scrollHeight-h.clientHeight;
    bar.style.width=(max>0?(h.scrollTop/max*100):0)+'%';
  }
  window.addEventListener('scroll',onScroll,{passive:true});
  onScroll();
  var init=location.hash.slice(1);
  if(init && root.querySelector('#'+CSS.escape(init))) show(init);
})();
`;

const fragment = `<title>The Embodiment Awakening</title>
<style>${STYLE}</style>
<div class="ea-root">
  <div class="ea-progress" id="ea-progress"></div>
  <div class="ea-bar">
    <div class="ea-bar-in">
      <span class="ea-brand">Embodiment&nbsp;Awakening</span>
      <nav class="ea-tabs" role="tablist" aria-label="Parts">${tabs}</nav>
    </div>
  </div>
  ${panels}
  <script>${SCRIPT}</script>
</div>`;

writeFileSync(OUT, fragment);
console.log(`Wrote ${OUT} (${(fragment.length / 1024).toFixed(1)} KB)`);
