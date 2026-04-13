#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

for env_file in .env .env.local .env.web-local; do
  if [[ -f "$env_file" ]]; then
    echo "Loading $env_file"
    set -a
    # shellcheck disable=SC1090
    source "$env_file"
    set +a
  fi
done

[[ -n "${ANTHROPIC_API_KEY:-}${CLAUDE_CODE_USE_VERTEX:-}${CLAUDE_CODE_USE_BEDROCK:-}" ]] \
  && unset ANTHROPIC_AUTH_TOKEN CLAUDE_CODE_OAUTH_TOKEN

if [[ -z "${ANTHROPIC_API_KEY:-}" && -z "${CLAUDE_CODE_OAUTH_TOKEN:-}" && -z "${CLAUDE_CODE_USE_VERTEX:-}" && -z "${CLAUDE_CODE_USE_BEDROCK:-}" ]]; then
  echo "Missing Claude credentials. Set one of: ANTHROPIC_API_KEY, CLAUDE_CODE_OAUTH_TOKEN, CLAUDE_CODE_USE_VERTEX=1, or CLAUDE_CODE_USE_BEDROCK=1 in .env/.env.local before running dev:web-local." >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "Docker is not running. Start Docker first, then re-run npm run dev:web-local." >&2
  exit 1
fi

if [[ -z "${DEVBOX_GIT_AUTH_TOKEN:-}" && -z "${GITHUB_TOKEN:-}" && -z "${GH_TOKEN:-}" ]]; then
  GH_BIN="$(command -v gh 2>/dev/null || true)"
  if [[ -z "$GH_BIN" ]]; then
    for candidate in /opt/homebrew/bin/gh /usr/local/bin/gh; do
      if [[ -x "$candidate" ]]; then
        GH_BIN="$candidate"
        break
      fi
    done
  fi

  if [[ -n "$GH_BIN" ]]; then
    if DEVBOX_GIT_AUTH_TOKEN="$("$GH_BIN" auth token 2>/dev/null)"; then
      export DEVBOX_GIT_AUTH_TOKEN
      export GH_TOKEN="${GH_TOKEN:-$DEVBOX_GIT_AUTH_TOKEN}"
      echo "Using gh auth token for private repo seeding."
    fi
  fi
fi

DATA_ROOT="${DEVBOX_DATA_ROOT:-$ROOT/.devbox-local}"
export DEVBOX_DATA_ROOT="$DATA_ROOT"
BACKEND_URL="${DEVBOX_WEB_URL:-http://127.0.0.1:18092}"
FRONTEND_URL="${DEVBOX_FRONTEND_URL:-http://127.0.0.1:5175/}"
BACKEND_PORT="${BACKEND_URL##*:}"
BACKEND_PORT="${BACKEND_PORT%%/*}"
FRONTEND_PORT="${FRONTEND_URL#http://127.0.0.1:}"
FRONTEND_PORT="${FRONTEND_PORT%%/*}"

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

echo "Refreshing devbox-runner:latest ..."
docker build -t devbox-runner:latest -f docker/runner.Dockerfile .

kill_listener_on_port() {
  local port="$1"
  local pids
  pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "$pids" ]]; then
    echo "Stopping existing listener(s) on port $port: $pids"
    kill $pids >/dev/null 2>&1 || true
    sleep 1
  fi
}

kill_listener_on_port "$BACKEND_PORT"
kill_listener_on_port "$FRONTEND_PORT"

pkill -f 'tsx src/index.ts --config config.web-local.yaml' >/dev/null 2>&1 || true
pkill -f 'frontend run dev -- --host 127.0.0.1 --port 5175' >/dev/null 2>&1 || true
docker ps -aq --filter 'name=^devbox-' | xargs -r docker rm -f >/dev/null 2>&1 || true

echo "Starting backend on $BACKEND_URL ..."
npm run dev:server &
BACKEND_PID=$!
FRONTEND_PID=""

cleanup() {
  kill "$BACKEND_PID" "$FRONTEND_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

wait_for_url() {
  local url="$1"
  local label="$2"

  for _ in $(seq 1 30); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done

  echo "$label did not become ready at $url" >&2
  return 1
}

wait_for_url "$BACKEND_URL/api/devbox/health" "Backend"

echo "Starting frontend on $FRONTEND_URL ..."
VITE_THESIS_DEVBOX_PROXY_TARGET="$BACKEND_URL" \
  npm --prefix frontend run dev -- --host 127.0.0.1 --port 5175 &
FRONTEND_PID=$!

wait_for_url "$FRONTEND_URL" "Frontend"

echo
echo "Devbox local web is running:"
echo "  Frontend: $FRONTEND_URL"
echo "  Backend:  $BACKEND_URL/api/devbox/health"
echo
echo "Press Ctrl+C to stop both services."

wait "$FRONTEND_PID"
