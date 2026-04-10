#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

DATA_ROOT="${DEVBOX_DATA_ROOT:-$ROOT/.devbox-local}"
export DEVBOX_DATA_ROOT="$DATA_ROOT"

if [[ "${DEVBOX_WEB_CLEAN:-1}" == "1" ]]; then
  rm -rf "$DATA_ROOT"
fi
mkdir -p "$DATA_ROOT"

if [[ ! -d node_modules ]]; then
  npm install
fi

if [[ ! -d frontend/node_modules ]]; then
  npm --prefix frontend install
fi

docker image inspect devbox-runner:latest >/dev/null 2>&1 || \
  docker build -t devbox-runner:latest -f docker/runner.Dockerfile .

pkill -f 'tsx src/index.ts --config config.web-local.yaml' >/dev/null 2>&1 || true
pkill -f 'frontend run dev -- --host 127.0.0.1 --port 5175' >/dev/null 2>&1 || true

echo "Starting backend on http://localhost:8092 ..."
npm run dev -- --config config.web-local.yaml &
BACKEND_PID=$!

cleanup() {
  kill "$BACKEND_PID" "$FRONTEND_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

for _ in $(seq 1 30); do
  if curl -fsS http://localhost:8092/api/devbox/health >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo "Starting frontend on http://127.0.0.1:5175/thesis ..."
DEVBOX_FRONTEND_PROXY_TARGET=http://localhost:8092 \
  npm --prefix frontend run dev -- --host 127.0.0.1 --port 5175 &
FRONTEND_PID=$!

echo
echo "Devbox local web is running:"
echo "  Frontend: http://127.0.0.1:5175/thesis"
echo "  Backend:  http://localhost:8092/api/devbox/health"
echo
echo "Press Ctrl+C to stop both services."

wait "$FRONTEND_PID"
