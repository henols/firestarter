#!/usr/bin/env bash
#
# fresh-clone-fixture.sh
#
# Proves RENAME-03: a clone taken fresh from the milestone tip initialises
# both submodules from the URLs recorded in .gitmodules -- the firmware one
# naming firestarter_fw -- rather than through GitHub's rename redirect.
#
# Per D-04 the superproject is cloned from the LOCAL meta repository over
# file://, while only the submodule leg crosses the network, against the
# real GitHub remotes (git@github.com:henols/firestarter_fw.git and
# git@github.com:henols/firestarter_app.git). This needs no push and does
# not breach the standing operator-gated-push rule -- it is the checkable
# half of RENAME-03; a clone taken from origin cannot be proved until the
# milestone ships.
#
# Usage:
#   bash fresh-clone-fixture.sh                  # clone $META_REF (default below)
#   META_REF=<ref> bash fresh-clone-fixture.sh    # clone a different ref
#   KEEP_CLONE=1 bash fresh-clone-fixture.sh      # leave the scratch tree for inspection
#   SCRATCH_DIR=<dir> bash fresh-clone-fixture.sh # clone into a specific parent dir
#   bash fresh-clone-fixture.sh --help            # print this usage and exit 0
#
# Environment:
#   META_REF     ref to clone from the local meta repository
#                (default: v1.38-repository-rename)
#   KEEP_CLONE   1 = do not remove the scratch tree on exit (default: 0)
#   SCRATCH_DIR  parent directory for the scratch clone
#                (default: a fresh `mktemp -d`); always resolved outside
#                /workspaces so a later `git clean -Xdf` cannot take it
#
# Dependencies: bash, git, mktemp, grep. No package installs.
#
# Failure style: bail-on-first-assertion, in the style of
# .planning/v1.7/phase-33-baseline-hex/check-migration.sh -- a failed clone
# makes every later assertion meaningless, so each check below aborts
# immediately rather than accumulating and reporting at the end.
#
# Exit codes:
#   0  FRESH CLONE OK -- both submodules initialised from the recorded URLs
#   1  a clone or an assertion failed for any other reason
#   2  bad usage (unrecognized argument)
#   3  the one named, expected case: the superproject cloned, but the
#      recorded firmware gitlink commit is not present on the remote yet.
#      This is expected between this phase's gitlink advance (189-03) and
#      the milestone push -- it is the fixture reporting an accurate fact
#      about an unpushed commit, not a regression in the recorded URL.
#
# Re-runnable: this script is idempotent and safe to run again -- each run
# clones into a fresh scratch directory and removes it on exit unless
# KEEP_CLONE=1. Phase 193's GATE-03 must demonstrate the .gitmodules
# history-trap workaround for two clone cases and can extend this fixture
# rather than reinventing it.

set -euo pipefail

# ---------------------------------------------------------------------------
# Argument parsing -- fail-closed on anything unrecognized (run_gates.sh style)
# ---------------------------------------------------------------------------
for arg in "$@"; do
    case "$arg" in
        --help)
            sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *)
            echo "ERROR: unrecognized argument: $arg" >&2
            echo "Usage: bash $0 [--help]" >&2
            exit 2
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Path resolution -- independent of caller's cwd; the meta root is derived
# from SCRIPT_DIR, never hardcoded (the anti-pattern check-migration.sh's
# BASELINE_DIR sets and this fixture deliberately does not copy).
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
META_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
META_REF="${META_REF:-v1.38-repository-rename}"
KEEP_CLONE="${KEEP_CLONE:-0}"

# ---------------------------------------------------------------------------
# Preconditions -- checked before any work, each reporting to stderr
# ---------------------------------------------------------------------------
if ! command -v git >/dev/null 2>&1; then
    echo "ERROR: git is not available on PATH" >&2
    exit 1
fi

if ! git -C "$META_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
    echo "ERROR: derived meta root is not a git repository: $META_ROOT" >&2
    exit 1
fi

if ! git -C "$META_ROOT" rev-parse --verify --quiet "$META_REF" >/dev/null; then
    echo "ERROR: META_REF does not resolve inside $META_ROOT: $META_REF" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Scratch tree -- outside /workspaces (memory hazard: a later `git clean
# -Xdf` aimed at this tree must not be able to take a scratch clone parked
# inside the repository), removed on exit unless KEEP_CLONE=1.
# ---------------------------------------------------------------------------
SCRATCH_PARENT="${SCRATCH_DIR:-$(mktemp -d)}"
mkdir -p "$SCRATCH_PARENT"
CLONE_DIR="$SCRATCH_PARENT/meta-clone"
CLONE_LOG="$(mktemp)"

cleanup() {
    rm -f "$CLONE_LOG"
    if [ "$KEEP_CLONE" != "1" ]; then
        rm -rf "$SCRATCH_PARENT"
    fi
}
trap cleanup EXIT

echo "FRESH CLONE FIXTURE (RENAME-03)"
echo "================================"
echo "meta_source: file://$META_ROOT"
echo "meta_ref: $META_REF"

# ---------------------------------------------------------------------------
# The clone itself -- D-04: superproject over file://, submodules against
# the real remotes. No --reference, no shared object store, no pre-seeded
# submodule directory -- the submodule leg must reach the real remote or
# this run proves nothing.
# ---------------------------------------------------------------------------
CLONE_RC=0
git clone --branch "$META_REF" --recurse-submodules "file://$META_ROOT" "$CLONE_DIR" >"$CLONE_LOG" 2>&1 || CLONE_RC=$?

if [ "$CLONE_RC" -ne 0 ]; then
    # Named case 3: the recorded gitlink commit is not present on the
    # remote yet. These are git's own diagnostic strings for that failure
    # (confirmed present verbatim in this machine's git-submodule--helper
    # binary via `strings`), not a guess.
    if /usr/bin/grep -qE "Direct fetching of that commit failed|reference is not a tree|Server does not allow request for unadvertised object|Unable to checkout .* in submodule path" "$CLONE_LOG"; then
        MISSING_SHA="$(/usr/bin/grep -oE '[0-9a-f]{40}' "$CLONE_LOG" | head -1)"
        echo "clone_result: submodule gitlink commit not present on remote"
        echo "missing_commit: ${MISSING_SHA:-unknown}"
        echo "note: expected between this phase's gitlink advance (189-03) and the milestone push -- not a URL regression"
        echo "--- clone output ---" >&2
        cat "$CLONE_LOG" >&2
        exit 3
    fi
    echo "FAIL: git clone --branch $META_REF --recurse-submodules exited $CLONE_RC" >&2
    echo "--- clone output ---" >&2
    cat "$CLONE_LOG" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Labelled values -- printed before the verdict, read from inside the
# scratch clone, not from /workspaces. An exit code alone cannot
# distinguish "resolved firestarter_fw directly" from "followed a
# redirect"; these lines are what does.
# ---------------------------------------------------------------------------
META_COMMIT="$(git -C "$CLONE_DIR" rev-parse HEAD)"
GITMODULES_URL_FW="$(git -C "$CLONE_DIR" config --file .gitmodules submodule.firestarter.url)"
CONFIG_URL_FW="$(git -C "$CLONE_DIR" config --local submodule.firestarter.url)"
REMOTE_ORIGIN_FW="$(git -C "$CLONE_DIR/firestarter" remote get-url origin)"
REMOTE_ORIGIN_APP="$(git -C "$CLONE_DIR/firestarter_app" remote get-url origin)"
FIRESTARTER_HEAD="$(git -C "$CLONE_DIR/firestarter" rev-parse HEAD)"
FIRESTARTER_APP_HEAD="$(git -C "$CLONE_DIR/firestarter_app" rev-parse HEAD)"

echo "meta_commit: $META_COMMIT"
echo "gitmodules_url(firestarter): $GITMODULES_URL_FW"
echo "config_url(firestarter): $CONFIG_URL_FW"
echo "remote_origin(firestarter): $REMOTE_ORIGIN_FW"
echo "remote_origin(firestarter_app): $REMOTE_ORIGIN_APP"
echo "firestarter_head: $FIRESTARTER_HEAD"
echo "firestarter_app_head: $FIRESTARTER_APP_HEAD"

# ---------------------------------------------------------------------------
# Assertions -- bail on the first failure, each naming what was expected,
# what the pre-state looks like, and what to do next.
# ---------------------------------------------------------------------------

# Assertion 1: both submodule working trees are populated -- `git submodule
# status` prefixes an uninitialised entry with '-'.
SUBMODULE_STATUS="$(git -C "$CLONE_DIR" submodule status)"
UNINIT_COUNT="$(echo "$SUBMODULE_STATUS" | /usr/bin/grep -c '^-' || true)"
if [ "$UNINIT_COUNT" -ne 0 ]; then
    echo "FAIL: Assertion 1 -- $UNINIT_COUNT submodule(s) not initialised in the clone." >&2
    echo "      Expected both 'firestarter' and 'firestarter_app' populated (no leading '-')." >&2
    echo "      git submodule status output:" >&2
    echo "$SUBMODULE_STATUS" >&2
    echo "      Re-run with KEEP_CLONE=1 to inspect $CLONE_DIR." >&2
    exit 1
fi

# Assertion 2: the firmware URL contains firestarter_fw.
if [[ "$REMOTE_ORIGIN_FW" != *firestarter_fw* ]]; then
    echo "FAIL: Assertion 2 -- remote_origin(firestarter) does not name firestarter_fw: $REMOTE_ORIGIN_FW" >&2
    echo "      Expected git@github.com:henols/firestarter_fw.git." >&2
    echo "      Check that .gitmodules was repointed and 'git submodule sync --recursive' ran." >&2
    exit 1
fi

# Assertion 3: the firmware URL does not match the bare-slug discriminator
# (189-PATTERNS.md) -- it must not have resolved through the old name.
BARE_SLUG_PATTERN='henols/firestarter([^_a-zA-Z0-9]|$)'
if echo "$REMOTE_ORIGIN_FW" | /usr/bin/grep -qE "$BARE_SLUG_PATTERN"; then
    echo "FAIL: Assertion 3 -- remote_origin(firestarter) matches the bare-slug discriminator: $REMOTE_ORIGIN_FW" >&2
    echo "      Expected the URL to name firestarter_fw only, not the bare 'firestarter' slug." >&2
    exit 1
fi

# Assertion 4: the host URL still names firestarter_app -- untouched control.
if [[ "$REMOTE_ORIGIN_APP" != *firestarter_app* ]]; then
    echo "FAIL: Assertion 4 -- remote_origin(firestarter_app) does not name firestarter_app: $REMOTE_ORIGIN_APP" >&2
    echo "      Expected git@github.com:henols/firestarter_app.git, unchanged by this phase." >&2
    exit 1
fi

echo ""
echo "FRESH CLONE OK"
exit 0
