# Publishing this directory as a standalone repository

Repository creation was not possible from the authoring session (the GitHub App integration
returned `403 Resource not accessible by integration` for both the personal account and the
`galpha-ai` organization — it lacks repo-creation permission). This directory is therefore
structured as a complete standalone repo. To publish it:

1. Create an empty repository in the GitHub UI (e.g. `riemann-impostors`, no README).
2. From a checkout of `Alpha-devbox` on the `claude/riemann-zeta-random-matrix-udxp3f` branch:

```bash
git subtree split --prefix=research/riemann-rmt/riemann-impostors -b riemann-impostors-main
git push git@github.com:QingyunSun/riemann-impostors.git riemann-impostors-main:main
```

(or simply copy the directory into a fresh `git init` and push).
