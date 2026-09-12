#!/bin/bash
# Local directory preparation. Only --clone permits one network clone.
set -eu
umask 077
clone=no
if [ "${1:-}" = --clone ]; then clone=yes; shift; fi
if [ "$#" -gt 1 ]; then printf 'Usage: /bin/bash 02_prepare_workspace.sh [--clone] [absolute-workspace-path]\n' >&2; exit 64; fi
if [ "$(/usr/bin/uname -s)" != Darwin ]; then printf 'STOP: macOS is required; nothing was created.\n' >&2; exit 1; fi
workspace=${1:-"$HOME/Astra-i9-staging"}
case "$workspace" in /*) ;; *) printf 'STOP: use an absolute local workspace path.\n' >&2; exit 64;; esac
case "$workspace" in /|*$'\n'*) printf 'STOP: unsuitable workspace path.\n' >&2; exit 64;; esac
case "$workspace/" in *"/../"*|*"/./"*) printf 'STOP: do not use dot path components.\n' >&2; exit 64;; esac
while [ "${workspace%/}" != "$workspace" ]; do workspace=${workspace%/}; done
[ -n "$workspace" ] || { printf 'STOP: root is not a workspace.\n' >&2; exit 64; }
ancestor=$workspace
existing_parent=
while [ "$ancestor" != / ]; do
  if [ -L "$ancestor" ] || { [ -e "$ancestor" ] && [ ! -d "$ancestor" ]; }; then
    printf 'STOP: a workspace ancestor is a symlink or non-directory.\n' >&2; exit 1
  fi
  if [ -z "$existing_parent" ] && [ -d "$ancestor" ]; then existing_parent=$ancestor; fi
  ancestor=$(/usr/bin/dirname "$ancestor")
done
existing_parent=${existing_parent:-/}
if ! /bin/df -l -P "$existing_parent" | /usr/bin/awk 'END {exit (NR < 2)}'; then
  printf 'STOP: choose a local mounted filesystem for the workspace.\n' >&2; exit 1
fi
for path in "$workspace" "$workspace/reports" "$workspace/repos" "$workspace/work" "$workspace/state"; do
  if [ -L "$path" ] || { [ -e "$path" ] && [ ! -d "$path" ]; }; then
    printf 'STOP: a workspace path is a symlink or a non-directory.\n' >&2; exit 1
  fi
done
/bin/mkdir -p "$workspace/reports" "$workspace/repos" "$workspace/work" "$workspace/state"
run=$(/usr/bin/mktemp -d "$workspace/reports/prepare-$(/bin/date -u +%Y%m%dT%H%M%SZ).XXXXXX")
pending="$run/report.pending"
: > "$pending"
finish() {
  rc=$?
  trap - EXIT
  # Also clean up helper children if the owner interrupts an optional clone.
  for child_group in "${clone_pid:-}" "${watchdog_pid:-}"; do
    if [ -n "$child_group" ]; then kill -KILL -- "-$child_group" 2>/dev/null || true; fi
  done
  printf 'Exit code: %s\n' "$rc" >> "$pending"
  /bin/mv "$pending" "$run/report.txt"
  printf 'Local report: %s\n' "$run/report.txt"
  exit "$rc"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
say() { printf '%s\n' "$*" | /usr/bin/tee -a "$pending"; }
say "Local workspace directories prepared: $workspace"
say 'Role: staging / secondary fallback; no services or schedules were started.'
repo="$workspace/repos/astra-bot-launch"
url=https://github.com/pri8771/astra-bot-launch
developer_dir=$(/usr/bin/xcode-select -p 2>/dev/null || true)
if [ -z "$developer_dir" ] || [ ! -x "$developer_dir/usr/bin/git" ]; then
  say 'FOLLOW-UP: owner runs /usr/bin/xcode-select --install, completes Apple installation, then reruns. No installer was opened.'
  exit 2
fi
git_bin="$developer_dir/usr/bin/git"
filter_args=()
disable_filters() {
  filter_args=()
  while IFS= read -r -d '' key; do
    case "$key" in *.required) filter_args+=(-c "$key=false");; *) filter_args+=(-c "$key=");; esac
  done < <("$git_bin" -C "$1" config --null --name-only --get-regexp '^filter\..*\.(clean|smudge|process|required)$' 2>/dev/null || true)
}
git_local() { "$git_bin" -c core.fsmonitor=false -c core.hooksPath=/dev/null "${filter_args[@]}" "$@"; }
verify_repo() {
  if [ -L "$repo" ] || [ ! -d "$repo/.git" ] || [ -L "$repo/.git" ]; then
    say 'STOP: target exists but is not a standalone non-symlink Git checkout. It was preserved.'; return 1
  fi
  if [ -e "$repo/.gitmodules" ]; then say 'STOP: submodule checkout requires separate review; it was preserved.'; return 1; fi
  disable_filters "$repo"
  origin=$(git_local -C "$repo" remote get-url origin 2>/dev/null || true)
  case "$origin" in "$url"|"$url.git") ;; *) say 'STOP: origin is not the expected credential-free HTTPS repository URL. It was preserved.'; return 1;; esac
  if ! dirty=$(GIT_OPTIONAL_LOCKS=0 git_local -C "$repo" status --porcelain --untracked-files=normal 2>/dev/null); then
    say 'STOP: cannot inspect the checkout safely. It was preserved.'; return 1
  fi
  if [ -n "$dirty" ]; then say 'STOP: checkout has local changes/untracked files. It was preserved; use another workspace or review those changes manually.'; return 1; fi
  say 'Expected repository exists and is clean. No pull, reset, checkout, or remote update was performed.'
}
if [ -e "$repo" ] || [ -L "$repo" ]; then verify_repo; exit 0; fi
if [ "$clone" != yes ]; then
  say 'Repository absent. Directory preparation is complete; no network access was attempted.'
  say 'FOLLOW-UP: when this Mac already has GitHub access, rerun this script with --clone and the same workspace path.'
  exit 0
fi
say 'Attempting one bounded clone using this Mac existing Git authentication.'
disable_filters "$workspace/repos"
export GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/usr/bin/false SSH_ASKPASS=/usr/bin/false
export GCM_INTERACTIVE=never GCM_GUI_PROMPT=0
# Job control gives Git and credential-helper children their own process group.
# A timeout terminates that group, so an unavailable helper cannot block this script.
set -m
git_local -c credential.interactive=false -c core.askPass=/usr/bin/false \
  -c init.templateDir= -c http.lowSpeedLimit=1 \
  -c http.lowSpeedTime=30 clone --quiet -- "$url" "$repo" >/dev/null 2>&1 &
clone_pid=$!
(
  /bin/sleep 45
  if kill -0 "$clone_pid" 2>/dev/null; then
    : > "$run/clone-timeout"
    kill -TERM -- "-$clone_pid" 2>/dev/null || true
    /bin/sleep 2
    kill -KILL -- "-$clone_pid" 2>/dev/null || true
  fi
) >/dev/null 2>&1 &
watchdog_pid=$!
clone_rc=0
wait "$clone_pid" || clone_rc=$?
kill -TERM -- "-$watchdog_pid" 2>/dev/null || true
wait "$watchdog_pid" 2>/dev/null || true
set +m
if [ "$clone_rc" -ne 0 ]; then
  say 'FOLLOW-UP: clone failed or timed out. In this Mac existing GitHub/IDE account flow, complete sign-in and confirm access to pri8771/astra-bot-launch; then retry.'
  say 'No credentials or raw Git errors were saved. Any partial checkout was preserved; inspect it or choose a fresh workspace before retrying.'
  exit 2
fi
verify_repo
say 'Clone complete. Run 03_verify.sh before reviewing the portable document packet.'
