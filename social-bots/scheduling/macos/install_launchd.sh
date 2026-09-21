#!/usr/bin/env bash
# SB-V07-001 launchd installer for bin/worker_once.py.
#
# Installs com.socialbots.workeronce.plist per lane into
# ~/Library/LaunchAgents/, substituting __PYTHON_EXE__, __REPO_ROOT__,
# __LANE__, __BRANCH__, __SBOTS_HOME__, __LOG_DIR__ and __INTERVAL_SECONDS__
# with real values. StartInterval is rewritten from the template's string
# placeholder to a real <integer> element (launchd requires an integer
# there; the checked-in template keeps it a string so the template file
# itself stays parseable -- see the plist's own comment).
#
# Loading the agent only means launchd is scheduled to try; it is not
# evidence a worker has run -- see ../README.md and ../RUNBOOK.md.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
TEMPLATE="$SCRIPT_DIR/com.socialbots.workeronce.plist"

REPO_ROOT=""
LANE=""
BRANCH=""
INTERVAL_SECONDS=1800
SBOTS_HOME=""
PYTHON_BIN=""
LOG_DIR="$HOME/Library/Logs/social-bots"
UNINSTALL=0

usage() {
    cat <<'EOF'
Usage:
  install_launchd.sh --repo-root PATH --lane LANE --branch BRANCH
                      [--interval-seconds 1800] [--sbots-home PATH]
                      [--python PATH] [--log-dir PATH]

  install_launchd.sh --uninstall --lane LANE
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
        --repo-root) REPO_ROOT="$2"; shift 2 ;;
        --lane) LANE="$2"; shift 2 ;;
        --branch) BRANCH="$2"; shift 2 ;;
        --interval-seconds) INTERVAL_SECONDS="$2"; shift 2 ;;
        --sbots-home) SBOTS_HOME="$2"; shift 2 ;;
        --python) PYTHON_BIN="$2"; shift 2 ;;
        --log-dir) LOG_DIR="$2"; shift 2 ;;
        --uninstall) UNINSTALL=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "unknown argument: $1" >&2; usage; exit 2 ;;
    esac
done

if [ -z "$LANE" ]; then
    echo "--lane is required" >&2
    exit 2
fi

LABEL="com.socialbots.workeronce.${LANE}"
AGENT_DIR="$HOME/Library/LaunchAgents"
AGENT_PATH="$AGENT_DIR/${LABEL}.plist"
UID_GUI="gui/$(id -u)"

bootout_quiet() {
    launchctl bootout "$UID_GUI/$LABEL" >/dev/null 2>&1 \
        || launchctl unload "$AGENT_PATH" >/dev/null 2>&1 \
        || true
}

if [ "$UNINSTALL" -eq 1 ]; then
    bootout_quiet
    rm -f "$AGENT_PATH"
    echo "Uninstalled (or already absent): $LABEL"
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

case "$INTERVAL_SECONDS" in
    ''|*[!0-9]*)
        echo "--interval-seconds must be a positive integer, got '$INTERVAL_SECONDS'" >&2
        exit 2
        ;;
esac

mkdir -p "$AGENT_DIR" "$LOG_DIR"

TMP_PLIST="$(mktemp -t socialbots-workeronce-plist)"
trap 'rm -f "$TMP_PLIST"' EXIT

sed \
    -e "s#<string>__INTERVAL_SECONDS__</string>#<integer>${INTERVAL_SECONDS}</integer>#" \
    -e "s#__PYTHON_EXE__#$PYTHON_BIN#g" \
    -e "s#__REPO_ROOT__#$REPO_ROOT#g" \
    -e "s#__LANE__#$LANE#g" \
    -e "s#__BRANCH__#$BRANCH#g" \
    -e "s#__SBOTS_HOME__#$SBOTS_HOME#g" \
    -e "s#__LOG_DIR__#$LOG_DIR#g" \
    "$TEMPLATE" > "$TMP_PLIST"

# Re-installing: unload the existing instance first (idempotent no-op if
# it was never loaded).
bootout_quiet
cp "$TMP_PLIST" "$AGENT_PATH"

if launchctl bootstrap "$UID_GUI" "$AGENT_PATH" 2>/dev/null; then
    :
else
    # Older macOS without bootstrap/bootout subcommands.
    launchctl load "$AGENT_PATH"
fi

echo "Installed and loaded $LABEL"
echo "Inspect it with:"
echo "  launchctl print $UID_GUI/$LABEL"
echo
echo "Logs:"
echo "  $LOG_DIR/worker-once.${LANE}.out.log"
echo "  $LOG_DIR/worker-once.${LANE}.err.log"
echo
echo "A loaded agent is not evidence a worker ran -- verify with:"
echo "  wc -l social-bots/worker-reports/$LANE/HEARTBEAT_LOG.jsonl"
echo "  wc -l \"$SBOTS_HOME/invocations/index.jsonl\""
