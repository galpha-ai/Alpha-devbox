#!/bin/bash
set -euo pipefail

SESSION_DIR="/session"
WORKSPACE_ROOT="/workspace"
SEED_MANIFEST="${SESSION_DIR}/seed-manifest.json"
RUN_DIR="${DEVBOX_RUN_DIR:?DEVBOX_RUN_DIR is required}"
INPUT_JSON="${RUN_DIR}/input.json"
GH_TOKENS_FILE="/tmp/.gh-tokens.json"
export HOME="${HOME:-${WORKSPACE_ROOT}/.home}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"
export GIT_CONFIG_GLOBAL="${GIT_CONFIG_GLOBAL:-${HOME}/.gitconfig}"
GIT_AUTH_TOKEN=""
GIT_AUTH_TOKENS_JSON=""

# Read controller-provided input first so seeding can use ephemeral git auth
# secrets.

if [ -f "${INPUT_JSON}" ] && command -v jq >/dev/null 2>&1; then
  GIT_AUTH_TOKEN="$(jq -r '.secrets.DEVBOX_GIT_AUTH_TOKEN // empty' "${INPUT_JSON}" 2>/dev/null || true)"
  GIT_AUTH_TOKENS_JSON="$(jq -c '
    .secrets.DEVBOX_GIT_AUTH_TOKENS // empty
    | if type == "string" then (fromjson? // empty) else . end
  ' "${INPUT_JSON}" 2>/dev/null || true)"
fi

if [ -n "${GIT_AUTH_TOKENS_JSON}" ]; then
  umask 077
  printf '%s' "${GIT_AUTH_TOKENS_JSON}" > "${GH_TOKENS_FILE}"
else
  rm -f "${GH_TOKENS_FILE}"
fi

extract_github_owner_from_source() {
  local source="$1"
  case "${source}" in
    git@github.com:*)
      local rest="${source#git@github.com:}"
      printf '%s' "${rest%%/*}" | tr '[:upper:]' '[:lower:]'
      return 0
      ;;
    ssh://git@github.com/*)
      local rest="${source#ssh://git@github.com/}"
      printf '%s' "${rest%%/*}" | tr '[:upper:]' '[:lower:]'
      return 0
      ;;
    https://*@github.com/*)
      local rest="${source#*@github.com/}"
      printf '%s' "${rest%%/*}" | tr '[:upper:]' '[:lower:]'
      return 0
      ;;
    https://github.com/*)
      local rest="${source#https://github.com/}"
      printf '%s' "${rest%%/*}" | tr '[:upper:]' '[:lower:]'
      return 0
      ;;
    http://github.com/*)
      local rest="${source#http://github.com/}"
      printf '%s' "${rest%%/*}" | tr '[:upper:]' '[:lower:]'
      return 0
      ;;
  esac
  return 1
}

rewrite_github_source_with_token() {
  local source="$1"
  local token="$2"
  case "${source}" in
    git@github.com:*)
      local repo_path="${source#git@github.com:}"
      printf 'https://x-access-token:%s@github.com/%s' "${token}" "${repo_path}"
      return 0
      ;;
    ssh://git@github.com/*)
      local repo_path="${source#ssh://git@github.com/}"
      printf 'https://x-access-token:%s@github.com/%s' "${token}" "${repo_path}"
      return 0
      ;;
    https://*@github.com/*)
      local repo_path="${source#*@github.com/}"
      printf 'https://x-access-token:%s@github.com/%s' "${token}" "${repo_path}"
      return 0
      ;;
    https://github.com/*)
      local repo_path="${source#https://github.com/}"
      printf 'https://x-access-token:%s@github.com/%s' "${token}" "${repo_path}"
      return 0
      ;;
    http://github.com/*)
      local repo_path="${source#http://github.com/}"
      printf 'https://x-access-token:%s@github.com/%s' "${token}" "${repo_path}"
      return 0
      ;;
  esac
  return 1
}

# All bind-mounted directories (session, workspace, ipc/*) are pre-created on
# the host by container-runner.ts before the container starts. No mkdir needed
# here.
mkdir -p "${HOME}" "${XDG_CONFIG_HOME}/git"

# Seed local workspace once per session workspace so subsequent turns reuse
# build artifacts.
if [ ! -f "${WORKSPACE_ROOT}/.seeded" ]; then
  if [ -f "${SEED_MANIFEST}" ] && command -v jq >/dev/null 2>&1; then
    repo_count="$(jq '.repos | length' "${SEED_MANIFEST}" 2>/dev/null || echo 0)"
    idx=0
    while [ "${idx}" -lt "${repo_count}" ]; do
      name="$(jq -r ".repos[${idx}].name // \"\"" "${SEED_MANIFEST}")"
      source="$(jq -r ".repos[${idx}].source // \"\"" "${SEED_MANIFEST}")"
      ref="$(jq -r ".repos[${idx}].ref // empty" "${SEED_MANIFEST}")"
      safe_name="$(printf '%s' "${name}" | sed 's/[^A-Za-z0-9._-]/-/g')"
      if [ -z "${safe_name}" ]; then
        safe_name="repo-$((idx + 1))"
      fi
      target="${WORKSPACE_ROOT}/${safe_name}"

      if [ -n "${source}" ]; then
        rm -rf "${target}"
        clone_source="${source}"
        repo_token=""
        if [ -n "${GIT_AUTH_TOKENS_JSON}" ] && command -v jq >/dev/null 2>&1; then
          if repo_owner="$(extract_github_owner_from_source "${source}")"; then
            repo_token="$(printf '%s' "${GIT_AUTH_TOKENS_JSON}" | jq -r --arg owner "${repo_owner}" '.[$owner] // empty' 2>/dev/null || true)"
          fi
        fi
        if [ -z "${repo_token}" ]; then
          repo_token="${GIT_AUTH_TOKEN}"
        fi
        if [ -n "${repo_token}" ]; then
          if rewritten_source="$(rewrite_github_source_with_token "${source}" "${repo_token}")"; then
            clone_source="${rewritten_source}"
          fi
        fi
        if [ -n "${ref}" ]; then
          git clone --branch "${ref}" --single-branch "${clone_source}" "${target}"
        else
          git clone "${clone_source}" "${target}"
        fi
      fi

      idx=$((idx + 1))
    done
  fi

  touch "${WORKSPACE_ROOT}/.seeded"
fi

# Refresh git remote URLs with fresh token on every session start.
# Workspace may be reused across sessions, but GitHub App installation tokens
# expire after 1 hour, so remote URLs from previous sessions become stale.
if [ -n "${GIT_AUTH_TOKEN}" ] || [ -n "${GIT_AUTH_TOKENS_JSON}" ]; then
  for repo_dir in "${WORKSPACE_ROOT}"/*/; do
    [ -d "${repo_dir}/.git" ] || continue
    current_url="$(git -C "${repo_dir}" remote get-url origin 2>/dev/null || true)"
    [ -n "${current_url}" ] || continue

    repo_token=""
    if [ -n "${GIT_AUTH_TOKENS_JSON}" ] && command -v jq >/dev/null 2>&1; then
      if repo_owner="$(extract_github_owner_from_source "${current_url}")"; then
        repo_token="$(printf '%s' "${GIT_AUTH_TOKENS_JSON}" | jq -r --arg owner "${repo_owner}" '.[$owner] // empty' 2>/dev/null || true)"
      fi
    fi
    if [ -z "${repo_token}" ]; then
      repo_token="${GIT_AUTH_TOKEN}"
    fi

    if [ -n "${repo_token}" ]; then
      if new_url="$(rewrite_github_source_with_token "${current_url}" "${repo_token}")"; then
        git -C "${repo_dir}" remote set-url origin "${new_url}"
      fi
    fi
  done
fi

# Export GH_TOKEN for gh CLI as a fallback when no owner-specific token is
# available. The gh wrapper in /usr/local/bin/gh prefers a repo-scoped token
# from ${GH_TOKENS_FILE} when it can resolve the target owner.
if [ -n "${GIT_AUTH_TOKEN}" ]; then
  export GH_TOKEN="${GIT_AUTH_TOKEN}"
fi

# Set git author to Claude.
git config --global user.name "Claude"
git config --global user.email "noreply@anthropic.com"

# Run the pre-built agent-runner directly from the image.
WORKSPACE_DIR="${WORKSPACE_ROOT}" DEVBOX_RUN_DIR="${RUN_DIR}" node /app/dist/index.js
