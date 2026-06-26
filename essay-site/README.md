# 具身觉醒 — Essay Site

A minimal, self-contained static site for the essay
[`docs/essays/physical-intelligence-2030.md`](../docs/essays/physical-intelligence-2030.md),
in the spirit of [situational-awareness.ai](https://situational-awareness.ai/):
text-first, a sticky table-of-contents sidebar, no JS framework, no build
dependencies.

## Files

- `index.html` — generated Chinese page (open directly in a browser).
- `en.html` — generated English page. A 中文 / EN switch sits in each masthead.
- `build.mjs` — dependency-free generator that converts the source markdown
  (`physical-intelligence-2030.md` and `physical-intelligence-2030.en.md`)
  into both pages.

## Regenerate

After editing the source essay, rebuild the page:

```bash
node essay-site/build.mjs
```

This re-reads `docs/essays/physical-intelligence-2030.md` and overwrites
`essay-site/index.html`. Commit both the source and the regenerated HTML.

## Host it

`index.html` is fully self-contained (CSS inlined, no external requests), so any
static host works:

- **GitHub Pages** — `.github/workflows/essay-site.yml` publishes this folder
  automatically. One-time setup: repo **Settings → Pages → Build and deployment
  → Source: "GitHub Actions"**. After that, every push that touches the essay or
  site redeploys it. The workflow is wired to run on both `main` and the
  `claude/robotics-future-essay-18rtk8` branch, so it can go live before the PR
  is merged. Live URL: `https://galpha-ai.github.io/Alpha-devbox/`.
- **Locally** — open `essay-site/index.html`, or serve the folder:
  `python3 -m http.server -d essay-site` then visit `http://localhost:8000`.
