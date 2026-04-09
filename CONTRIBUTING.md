# Contributing to Devbox Agent

Thank you for your interest in contributing to Devbox Agent. Contributions of all kinds are welcome, including bug reports, feature requests, documentation improvements, and code changes.

## Code of Conduct

We are committed to providing a welcoming and respectful environment for everyone. Be kind, constructive, and professional in all interactions. Harassment, discrimination, and disruptive behavior will not be tolerated.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/<your-username>/devbox-agent.git`
3. Install dependencies: `npm install`
4. Create a branch: `git checkout -b feat/your-feature`

## Development Setup

- Node.js >= 20
- `npm install` to install controller dependencies
- `cd container/agent-runner && npm install` to install runner dependencies
- `npm run dev` to start the controller locally
- `npm test` to run tests

## Project Structure

- `src/` — Controller process
- `container/` — Runner process (runs inside containers)
- `agents/` — Agent definitions
- `k8s/` — Kubernetes manifests
- `docs/` — Documentation

## Making Changes

- Follow existing code style (Prettier is enforced via pre-commit hook)
- Write tests for new functionality
- Update `docs/architecture.md` if you change architecture
- Keep commits focused and well-described

## Pull Request Process

1. Ensure tests pass: `npm test`
2. Ensure types check: `npm run typecheck`
3. Ensure formatting: `npm run format:check`
4. Update documentation if needed
5. Submit a PR with a clear description of what changed and why
6. Address review feedback promptly

## Reporting Issues

Use GitHub Issues. Please include:

- What happened
- What you expected to happen
- Steps to reproduce
- Environment details (OS, Node.js version, Kubernetes version)

## License

All contributions are licensed under AGPL-3.0, the same license as the project.
