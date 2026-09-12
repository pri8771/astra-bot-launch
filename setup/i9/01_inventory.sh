#!/bin/bash
# Read-only machine checks; the only writes are local reports.
set -eu
umask 077
if [ "$#" -gt 1 ]; then printf 'Usage: /bin/bash 01_inventory.sh [absolute-workspace-path]\n' >&2; exit 64; fi
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
run=$(/usr/bin/mktemp -d "$workspace/reports/inventory-$(/bin/date -u +%Y%m%dT%H%M%SZ).XXXXXX")
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
say 'Inventory of the Mac running this script; target i9 identity is not assumed.'
say 'Role: staging / secondary fallback. R730 remains primary; Windows is first fallback.'
say "UTC: $(/bin/date -u +%Y-%m-%dT%H:%M:%SZ)"
say "macOS: $(/usr/bin/sw_vers -productVersion) ($(/usr/bin/sw_vers -buildVersion))"
say "Architecture: $(/usr/bin/uname -m)"
cpu=$(/usr/sbin/sysctl -n machdep.cpu.brand_string 2>/dev/null || true)
say "CPU: ${cpu:-not available}"
memory=$(/usr/sbin/sysctl -n hw.memsize 2>/dev/null || true)
say "Physical memory bytes: ${memory:-not available}"
free_kib=$(/bin/df -Pk "$workspace" | /usr/bin/awk 'NR == 2 {print $4}')
say "Workspace filesystem free KiB: ${free_kib:-not available}"
gpu=$(/usr/sbin/system_profiler SPDisplaysDataType -detailLevel mini -timeout 15 2>/dev/null | /usr/bin/awk '/Chipset Model:/ {sub(/^[[:space:]]*Chipset Model:[[:space:]]*/, ""); print}' || true)
say "GPU chipset names: ${gpu:-not available}"
developer_dir=$(/usr/bin/xcode-select -p 2>/dev/null || true)
if [ -n "$developer_dir" ] && [ -x "$developer_dir/usr/bin/git" ]; then
  say 'Apple developer tools / usable Git binary: present (not invoked).'
else
  say 'FOLLOW-UP: owner runs /usr/bin/xcode-select --install, completes Apple installation, then reruns. No installer was opened.'
fi
for cli in git gh node npm codex claude cursor code docker ollama openclaw; do
  if command -v "$cli" >/dev/null 2>&1; then say "CLI $cli: present on PATH (not executed)"; else say "CLI $cli: absent on PATH"; fi
done
for app in Cursor 'Visual Studio Code' Codex Claude Antigravity TeamViewer; do
  if [ -d "/Applications/$app.app" ] || [ -d "$HOME/Applications/$app.app" ]; then say "App $app: present"; else say "App $app: not found in standard Applications locations"; fi
done
say 'Missing optional apps/CLIs do not require installation for document review; use an existing editor. No runtime was tested.'
say 'Stop after this inventory. The i9 is low priority; workspace preparation and verification remain optional/deferred until immediately useful.'
