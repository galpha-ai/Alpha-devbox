# 具身觉醒 — Essay Site

A minimal, self-contained static site for the essay
[`docs/essays/physical-intelligence-2030.md`](../docs/essays/physical-intelligence-2030.md),
in the spirit of [situational-awareness.ai](https://situational-awareness.ai/):
text-first, a sticky table-of-contents sidebar, no JS framework, no build
dependencies.

## Files

- `index.html` — the generated, self-contained page (open it directly in a browser).
- `build.mjs` — dependency-free generator that converts the source markdown to `index.html`.

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

- **GitHub Pages** — a workflow at `.github/workflows/essay-site.yml` publishes
  this folder automatically on pushes to the default branch (enable Pages →
  "GitHub Actions" in repo settings).
- **Locally** — just open `essay-site/index.html`, or serve the folder:
  `python3 -m http.server -d essay-site`.
