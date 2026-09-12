#!/bin/bash
# Local readiness checks only: no network, model/API, job, or service calls.
set -eu
umask 077
if [ "$#" -gt 1 ]; then printf 'Usage: /bin/bash 03_verify.sh [absolute-workspace-path]\n' >&2; exit 64; fi
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
for path in "$workspace" "$workspace/reports"; do
  if [ -L "$path" ] || { [ -e "$path" ] && [ ! -d "$path" ]; }; then
    printf 'STOP: workspace/report path is a symlink or a non-directory.\n' >&2; exit 1
  fi
done
/bin/mkdir -p "$workspace/reports"
run=$(/usr/bin/mktemp -d "$workspace/reports/verify-$(/bin/date -u +%Y%m%dT%H%M%SZ).XXXXXX")
pending="$run/report.pending"
: > "$pending"
finish() {
  rc=$?
  trap - EXIT
  printf 'Exit code: %s\n' "$rc" >> "$pending"
  /bin/mv "$pending" "$run/report.txt"
  printf 'Local report: %s\n' "$run/report.txt"
  exit "$rc"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
say() { printf '%s\n' "$*" | /usr/bin/tee -a "$pending"; }
say 'Verification scope: local staging files and document checkout only.'
say "macOS $(/usr/bin/sw_vers -productVersion); architecture $(/usr/bin/uname -m)."
say 'Owner prerequisite: confirm this is the intended always-on i9 Mac using its own screen/inventory; architecture alone does not confirm host identity.'
say 'This check makes no claim about R730/Windows reachability, available models, runtime health, credentials, or failover readiness.'
missing=0
for name in repos work state; do
  if [ -d "$workspace/$name" ] && [ ! -L "$workspace/$name" ]; then say "Directory $name: present"; else say "FOLLOW-UP: directory $name missing/unsafe; run 02_prepare_workspace.sh or choose a new workspace."; missing=1; fi
done
developer_dir=$(/usr/bin/xcode-select -p 2>/dev/null || true)
if [ -z "$developer_dir" ] || [ ! -x "$developer_dir/usr/bin/git" ]; then
  say 'FOLLOW-UP: owner runs /usr/bin/xcode-select --install, completes Apple installation, then reruns. No installer was opened.'
  exit 2
fi
git_bin="$developer_dir/usr/bin/git"
repo="$workspace/repos/astra-bot-launch"
if [ ! -d "$repo/.git" ] || [ -L "$repo" ] || [ -L "$repo/.git" ] || [ -L "$workspace/repos" ]; then
  say 'FOLLOW-UP: expected standalone checkout absent/unsafe. After existing GitHub sign-in is ready, run 02_prepare_workspace.sh --clone, or use a new workspace.'
  exit 2
fi
if [ -e "$repo/.gitmodules" ]; then say 'FOLLOW-UP: submodule checkout requires separate review; no inspection helpers were run.'; exit 2; fi
filter_args=()
while IFS= read -r -d '' key; do
  case "$key" in *.required) filter_args+=(-c "$key=false");; *) filter_args+=(-c "$key=");; esac
done < <("$git_bin" -C "$repo" config --null --name-only --get-regexp '^filter\..*\.(clean|smudge|process|required)$' 2>/dev/null || true)
git_local() { "$git_bin" -c core.fsmonitor=false -c core.hooksPath=/dev/null "${filter_args[@]}" "$@"; }
origin=$(git_local -C "$repo" remote get-url origin 2>/dev/null || true)
case "$origin" in https://github.com/pri8771/astra-bot-launch|https://github.com/pri8771/astra-bot-launch.git) say 'Repository origin: expected credential-free HTTPS URL';; *) say 'FOLLOW-UP: unexpected repository origin; inspect locally or choose a new workspace. URL omitted.'; missing=1;; esac
if dirty=$(GIT_OPTIONAL_LOCKS=0 git_local -C "$repo" status --porcelain --untracked-files=normal 2>/dev/null); then
  if [ -z "$dirty" ]; then say 'Checkout: clean'; else say 'FOLLOW-UP: checkout contains changes/untracked files; review manually. No files changed.'; missing=1; fi
else say 'FOLLOW-UP: cannot inspect checkout; review locally.'; missing=1; fi
if git_local -C "$repo" rev-parse --verify HEAD >/dev/null 2>&1; then
  say "Local commit: $(git_local -C "$repo" rev-parse HEAD)"
else say 'FOLLOW-UP: checkout has no readable commit.'; missing=1; fi
for doc in focus/kai-pri-lipi/README.md WAVE_STATUS.md focus/kai-pri-lipi/OWNER_DIRECTION.md; do
  if [ -f "$repo/$doc" ] && [ ! -L "$repo/$doc" ]; then say "Document available: $doc"; else say "FOLLOW-UP: $doc is absent from this checkout; obtain the current portable document packet from the coordinator. No automatic pull attempted."; missing=1; fi
done
if [ "$missing" -ne 0 ]; then say 'RESULT: staging review has outstanding follow-ups.'; exit 2; fi
say 'RESULT: local files are ready for document review, subject to owner confirming this is the intended i9.'
say 'Open this checkout in an existing IDE and read focus/kai-pri-lipi/README.md, then WAVE_STATUS.md. Host-level activation remains a separate decision.'
