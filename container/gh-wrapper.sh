#!/bin/bash
set -euo pipefail

REAL_GH_BIN="${DEVBOX_REAL_GH_BIN:-/usr/bin/gh}"
TOKENS_FILE="${DEVBOX_GH_TOKENS_FILE:-/tmp/.gh-tokens.json}"

extract_owner_from_repo_selector() {
  local repo="${1:-}"
  local seg1=""
  local seg2=""
  local seg3=""

  [ -n "${repo}" ] || return 1

  case "${repo}" in
    git@github.com:*)
      repo="${repo#git@github.com:}"
      ;;
    ssh://git@github.com/*)
      repo="${repo#ssh://git@github.com/}"
      ;;
    https://*@github.com/*)
      repo="${repo#*@github.com/}"
      ;;
    https://github.com/*)
      repo="${repo#https://github.com/}"
      ;;
    http://github.com/*)
      repo="${repo#http://github.com/}"
      ;;
  esac

  IFS='/' read -r seg1 seg2 seg3 _ <<<"${repo}"

  if [ -n "${seg3}" ]; then
    printf '%s' "${seg2}" | tr '[:upper:]' '[:lower:]'
    return 0
  fi

  if [ -n "${seg1}" ] && [ -n "${seg2}" ]; then
    printf '%s' "${seg1}" | tr '[:upper:]' '[:lower:]'
    return 0
  fi

  return 1
}

extract_owner_from_args() {
  local expects_repo_arg="false"
  local arg=""

  for arg in "$@"; do
    if [ "${expects_repo_arg}" = "true" ]; then
      extract_owner_from_repo_selector "${arg}"
      return 0
    fi

    case "${arg}" in
      --repo|-R)
        expects_repo_arg="true"
        ;;
      --repo=*|-R=*)
        extract_owner_from_repo_selector "${arg#*=}"
        return 0
        ;;
    esac
  done

  if [ -n "${GH_REPO:-}" ]; then
    extract_owner_from_repo_selector "${GH_REPO}"
    return 0
  fi

  return 1
}

extract_owner_from_git_remote() {
  local remote_url=""

  remote_url="$(git remote get-url origin 2>/dev/null || true)"
  [ -n "${remote_url}" ] || return 1

  extract_owner_from_repo_selector "${remote_url}"
}

select_token_for_owner() {
  local owner="$1"

  [ -n "${owner}" ] || return 1
  [ -f "${TOKENS_FILE}" ] || return 1
  command -v jq >/dev/null 2>&1 || return 1

  jq -r --arg owner "${owner}" '.[$owner] // empty' "${TOKENS_FILE}" 2>/dev/null
}

owner=""
token=""

if owner="$(extract_owner_from_args "$@" 2>/dev/null)"; then
  :
elif owner="$(extract_owner_from_git_remote 2>/dev/null)"; then
  :
else
  owner=""
fi

if [ -n "${owner}" ]; then
  token="$(select_token_for_owner "${owner}" || true)"
  if [ -n "${token}" ]; then
    export GH_TOKEN="${token}"
    export GITHUB_TOKEN="${token}"
  fi
fi

exec "${REAL_GH_BIN}" "$@"
