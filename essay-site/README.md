# The Embodiment Awakening — Essay Site

A minimal, self-contained static site for the *Embodiment Awakening* essay
series, in the spirit of [situational-awareness.ai](https://situational-awareness.ai/):
text-first, a sticky table-of-contents sidebar, no JS framework, no build
dependencies.

## Pages (generated)

| File | Source markdown | Content |
|---|---|---|
| `index.html` | `physical-intelligence-2030.en.md` | **Part I — Roadmap** (technology + investment map) |
| `frontiers.html` | `new-verbs-and-recursive-robotics.en.md` | **Part II — Frontiers** (new verbs, robots building robots) |
| `critique.html` | `robotics-critique-timing-risk.md` | **Part III — Critique** (timing red-team) |
| `zh.html` | `physical-intelligence-2030.md` | Chinese original of Part I |

Each masthead carries a series nav (Part I / II / III) plus an EN/中文 link.

- `build.mjs` — dependency-free generator (markdown → self-contained HTML,
  with tables, code blocks, and a TOC).

## Regenerate

After editing any source markdown under `docs/essays/`, rebuild:

```bash
node essay-site/build.mjs
```

It re-reads the source markdown and overwrites the four HTML files. Commit both
the sources and the regenerated HTML.

## Host it

Every page is fully self-contained (CSS inlined, no external requests), so any
static host works:

- **GitHub Pages** — `.github/workflows/essay-site.yml` publishes this folder on
  pushes to `main`. One-time setup (repo admin, once): **Settings → Pages →
  Build and deployment → Source: "GitHub Actions"** — this org's Actions token
  cannot self-enable Pages, so the toggle is manual. After that, every push to
  `main` that touches the essays or site redeploys to
  `https://galpha-ai.github.io/Alpha-devbox/`. To publish from a feature branch
  before merging, run the workflow manually (Actions → "Publish essay site" →
  Run workflow → pick the branch).
- **Locally** — open `essay-site/index.html`, or serve the folder:
  `python3 -m http.server -d essay-site` then visit `http://localhost:8000`.
