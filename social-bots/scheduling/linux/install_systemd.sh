#!/usr/bin/env bash
# SB-V07-001 systemd installer for bin/worker_once.py.
#
# Installs the social-bots-worker-once@.service / .timer template pair,
# substituting __REPO_ROOT__, __PYTHON_EXE__, __BRANCH__, __SBOTS_HOME__ and
# __INTERVAL__ with real values, then enables the timer for one lane
# instance. Default target is the calling user's systemd user manager
# (~/.config/systemd/user); pass --system to install to
# /etc/systemd/system instead (requires sudo).
#
# A successful install only means the timer is scheduled. It is not
# evidence that the worker has run or will run correctly -- see
# ../README.md and ../RUNBOOK.md for how to confirm real invocations.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

MODE="user"
INTERVAL="30min"
UNINSTALL=0
REPO_ROOT=""
LANE=""
BRANCH=""
SBOTS_HOME=""
PYTHON_BIN=""

usage() {
    cat <<'EOF'
Usage:
  install_systemd.sh --repo-root PATH --lane LANE --branch BRANCH
                      [--interval 30min] [--sbots-home PATH] [--python PATH]
                      [--user | --system]

  install_systemd.sh --uninstall --lane LANE [--user | --system]

--user is the default (installs to ~/.config/systemd/user).
--system installs to /etc/systemd/system via sudo.
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
        --repo-root) REPO_ROOT="$2"; shift 2 ;;
        --lane) LANE="$2"; shift 2 ;;
        --branch) BRANCH="$2"; shift 2 ;;
        --interval) INTERVAL="$2"; shift 2 ;;
        --sbots-home) SBOTS_HOME="$2"; shift 2 ;;
        --python) PYTHON_BIN="$2"; shift 2 ;;
        --user) MODE="user"; shift ;;
        --system) MODE="system"; shift ;;
        --uninstall) UNINSTALL=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "unknown argument: $1" >&2; usage; exit 2 ;;
    esac
done

if [ -z "$LANE" ]; then
    echo "--lane is required" >&2
    exit 2
fi

SERVICE_TEMPLATE="social-bots-worker-once@.service"
TIMER_TEMPLATE="social-bots-worker-once@.timer"
SERVICE_UNIT="social-bots-worker-once@${LANE}.service"
TIMER_UNIT="social-bots-worker-once@${LANE}.timer"

if [ "$MODE" = "user" ]; then
    UNIT_DIR="$HOME/.config/systemd/user"
    SYSTEMCTL=(systemctl --user)
    AS_ROOT=()
else
    UNIT_DIR="/etc/systemd/system"
    SYSTEMCTL=(sudo systemctl)
    AS_ROOT=(sudo)
fi

if [ "$UNINSTALL" -eq 1 ]; then
    "${SYSTEMCTL[@]}" disable --now "$TIMER_UNIT" >/dev/null 2>&1 || true
    "${AS_ROOT[@]}" rm -f "$UNIT_DIR/$SERVICE_TEMPLATE" "$UNIT_DIR/$TIMER_TEMPLATE"
    "${SYSTEMCTL[@]}" daemon-reload || true
    echo "Uninstalled (or already absent): $TIMER_UNIT"
    exit 0
fi

if [ -z "$REPO_ROOT" ]; then
    echo "--repo-root is required" >&2
    exit 2
fi
if [ -z "$BRANCH" ]; then
    echo "--branch is required" >&2
    exit 2
fi

REPO_ROOT="$(cd -- "$REPO_ROOT" >/dev/null 2>&1 && pwd)"
ENTRYPOINT="$REPO_ROOT/social-bots/bin/worker_once.py"
if [ ! -f "$ENTRYPOINT" ]; then
    echo "Entrypoint not found at '$ENTRYPOINT'." >&2
    echo "--repo-root must be the git checkout root (it must contain social-bots/bin/worker_once.py)." >&2
    exit 1
fi

if [ -z "$SBOTS_HOME" ]; then
    SBOTS_HOME="$REPO_ROOT/social-bots"
fi

if [ -z "$PYTHON_BIN" ]; then
    PYTHON_BIN="$(command -v python3 || true)"
    if [ -z "$PYTHON_BIN" ]; then
        echo "python3 not found on PATH; pass --python explicitly." >&2
        exit 1
    fi
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

sed \
    -e "s#__REPO_ROOT__#$REPO_ROOT#g" \
    -e "s#__PYTHON_EXE__#$PYTHON_BIN#g" \
    -e "s#__BRANCH__#$BRANCH#g" \
    -e "s#__SBOTS_HOME__#$SBOTS_HOME#g" \
    "$SCRIPT_DIR/$SERVICE_TEMPLATE" > "$TMP_DIR/$SERVICE_TEMPLATE"

sed \
    -e "s#__INTERVAL__#$INTERVAL#g" \
    "$SCRIPT_DIR/$TIMER_TEMPLATE" > "$TMP_DIR/$TIMER_TEMPLATE"

"${AS_ROOT[@]}" mkdir -p "$UNIT_DIR"
"${AS_ROOT[@]}" cp "$TMP_DIR/$SERVICE_TEMPLATE" "$UNIT_DIR/$SERVICE_TEMPLATE"
"${AS_ROOT[@]}" cp "$TMP_DIR/$TIMER_TEMPLATE" "$UNIT_DIR/$TIMER_TEMPLATE"

"${SYSTEMCTL[@]}" daemon-reload
"${SYSTEMCTL[@]}" enable --now "$TIMER_UNIT"

echo "Installed and enabled $TIMER_UNIT"
"${SYSTEMCTL[@]}" list-timers "social-bots-worker-once@*" || true

JOURNAL_FLAG=""
if [ "$MODE" = "user" ]; then
    JOURNAL_FLAG="--user"
fi
echo
echo "Read real invocation exit codes (0/3/5 benign, 1/2 failure) with:"
echo "  journalctl $JOURNAL_FLAG -u $SERVICE_UNIT -n 50"
echo
echo "A running timer is not evidence a worker ran -- verify with:"
echo "  wc -l social-bots/worker-reports/$LANE/HEARTBEAT_LOG.jsonl"
echo "  wc -l \"$SBOTS_HOME/invocations/index.jsonl\""
