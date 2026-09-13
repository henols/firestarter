#!/usr/bin/env bash
#
# endpoint-contract-fixture.sh
#
# Proves criterion 4's "fw resolves a real firmware release end to end
# against the renamed repository" -- and does so with the ONE observable
# that can tell that apart from the pre-change state. `requests` follows
# redirects by default and the bare slug `henols/firestarter` answers with a
# transparent 301 whose body is byte-identical to `henols/firestarter_fw`'s
# (RESEARCH Finding 1). A transcript that only shows a successful resolve
# is compatible with BOTH states. This script asserts `redirects: 0` on
# both API endpoints -- the only reading that distinguishes them.
#
# Four checks (D-14), run against the live GitHub API, no bench, no avrdude:
#   1. stable channel resolves, plus a direct zero-redirect reading of
#      FIRESTARTER_RELEASE_URL and FIRESTARTER_RELEASES_URL
#   2. pre channel resolves against a board it actually carries
#   3. one real .hex downloaded through the package's own
#      _download_firmware_file and format-checked as Intel HEX
#   4. both URL-04 failure modes, for real:
#        4a. asset-less  -- fw --board uno328pb --stable against the live,
#            correctly-named endpoint (only the board identity is
#            simulated -- no programmer is attached)
#        4b. unreachable -- a throwaway child process with the endpoint
#            constants rebound to a nonexistent repository slug
#
# Usage:
#   bash endpoint-contract-fixture.sh                 # run all four checks
#   PYTHON_BIN=<path> bash endpoint-contract-fixture.sh
#   NOPE_SLUG=<slug> bash endpoint-contract-fixture.sh
#   KEEP_DOWNLOAD=1 bash endpoint-contract-fixture.sh # keep the downloaded .hex
#   bash endpoint-contract-fixture.sh --help          # print this usage and exit 0
#
# Environment:
#   PYTHON_BIN     interpreter to drive the checks through
#                  (default: the app working tree's .venv311/bin/python,
#                  derived from SCRIPT_DIR -- this is the same py3.11
#                  interpreter Host CI runs, not the py3.12 devcontainer
#                  default)
#   NOPE_SLUG      a repository name under henols that does not exist,
#                  used to produce check 4b's unreachable case
#                  (default: firestarter-does-not-exist-190)
#   KEEP_DOWNLOAD  1 = leave the downloaded firmware image in place for
#                  inspection instead of removing it by explicit path
#                  (default: 0)
#
# Dependencies: bash, git, curl, mktemp, an interpreter with firestarter,
# requests and click importable. No package installs.
#
# Failure style: bail-on-first-assertion, in the style of
# .planning/phases/189-free-the-name/fresh-clone-fixture.sh -- a failed
# earlier check makes a later one meaningless, so each check aborts
# immediately with the expectation, the pre-state and the next action named.
#
# Exit codes:
#   0  ENDPOINT CONTRACT OK -- both channels resolved with zero redirect
#      hops, a real asset downloaded and format-checked, both URL-04
#      failure modes shown exiting 1 with distinct named messages
#   1  a check or an assertion failed for any other reason
#   2  bad usage (unrecognized argument)
#   3  the one named, expected non-failure case -- api.github.com is not
#      reachable from this container. This is a network fact, not a URL
#      regression; re-run when connectivity returns.
#
# Re-runnable: this script is idempotent and safe to run again. It writes
# nothing into the firestarter_app working tree; the one artefact it
# creates on disk (the downloaded .hex, under the app's own
# ~/.firestarter directory) is removed by explicit path on exit unless
# KEEP_DOWNLOAD=1. Phase 191 re-runs this fixture against the stable it
# cuts; a post-claim milestone re-runs it to watch the 404 arrive
# (RESEARCH "Verification" notes, D-16).

set -euo pipefail

# ---------------------------------------------------------------------------
# Argument parsing -- fail-closed on anything unrecognized
# ---------------------------------------------------------------------------
for arg in "$@"; do
    case "$arg" in
        --help)
            sed -n '2,64p' "$0" | sed 's/^# \{0,1\}//'
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
# Path resolution -- independent of caller's cwd; every root is derived from
# SCRIPT_DIR, never hardcoded.
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
META_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
APP_ROOT="$META_ROOT/firestarter_app"

PYTHON_BIN="${PYTHON_BIN:-$APP_ROOT/.venv311/bin/python}"
NOPE_SLUG="${NOPE_SLUG:-firestarter-does-not-exist-190}"
KEEP_DOWNLOAD="${KEEP_DOWNLOAD:-0}"

# ---------------------------------------------------------------------------
# Preconditions -- checked before any work, each reporting to stderr
# ---------------------------------------------------------------------------
if [ ! -x "$PYTHON_BIN" ]; then
    echo "ERROR: PYTHON_BIN is not an executable file: $PYTHON_BIN" >&2
    echo "       Expected the app working tree's .venv311 (Python 3.11) or an override." >&2
    exit 1
fi

if ! "$PYTHON_BIN" -P -c "import firestarter, requests, click" >/dev/null 2>&1; then
    echo "ERROR: $PYTHON_BIN cannot import firestarter, requests and click." >&2
    echo "       Expected an environment with the app installed editable (.venv311)." >&2
    exit 1
fi

if ! git -C "$APP_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
    echo "ERROR: derived app root is not a git repository: $APP_ROOT" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Reachability probe -- transport-level failure only, never an HTTP status.
# curl's %{http_code} prints 000 when the request could not be made at all
# (DNS, connect, TLS); any real HTTP status (200, 404, ...) means the
# endpoint IS reachable and any failure from here on is a real one.
# ---------------------------------------------------------------------------
PROBE_CODE="$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 \
    https://api.github.com/repos/henols/firestarter_fw/releases/latest 2>/dev/null || echo "000")"
if [ "$PROBE_CODE" = "000" ]; then
    echo "NETWORK UNAVAILABLE: could not reach api.github.com (transport-level failure)." >&2
    echo "This reports the network, not a URL regression. Re-run when connectivity returns." >&2
    exit 3
fi

# ---------------------------------------------------------------------------
# Scratch bookkeeping -- per-check logs live outside the repository via
# mktemp, removed on exit. The one artefact NOT cleaned up here is the
# downloaded firmware image, which check 3 removes explicitly by path
# unless KEEP_DOWNLOAD=1.
# ---------------------------------------------------------------------------
CHECK1_LOG="$(mktemp)"
CHECK2_LOG="$(mktemp)"
CHECK3_LOG="$(mktemp)"
CHECK4A_LOG="$(mktemp)"
CHECK4B_LOG="$(mktemp)"

cleanup() {
    rm -f "$CHECK1_LOG" "$CHECK2_LOG" "$CHECK3_LOG" "$CHECK4A_LOG" "$CHECK4B_LOG"
}
trap cleanup EXIT

echo "ENDPOINT CONTRACT FIXTURE (URL-01 / URL-03 / URL-04)"
echo "====================================================="
echo "python_bin: $PYTHON_BIN"
echo "app_root: $APP_ROOT"
echo "nope_slug: $NOPE_SLUG"
echo ""

# Every child interpreter below is invoked with `-P` (PYTHONSAFEPATH,
# available on 3.11+). Without it, Python prepends the caller's cwd to
# sys.path; when that cwd is /workspaces (the meta repo), the sibling
# `firestarter/` FIRMWARE submodule -- a bare directory with no
# __init__.py -- forms a namespace package that shadows the real,
# editable-installed `firestarter` HOST package before its actual finder is
# ever consulted, and every import below fails with "cannot import name
# '__version__' from 'firestarter' (unknown location)". `-P` stops Python
# from adding the cwd at all, so every check below is correct regardless of
# the caller's working directory.
#
# ---------------------------------------------------------------------------
# Check 1: stable channel, plus the load-bearing zero-redirect reading of
# both API endpoints. Without this second half the transcript is compatible
# with the pre-change state (Finding 1) and proves nothing about URL-01.
# ---------------------------------------------------------------------------
echo "--- Check 1: stable channel ---"
if ! "$PYTHON_BIN" -P <<'PYEOF' >"$CHECK1_LOG" 2>&1
import requests
from firestarter.firmware import FirmwareManager, FIRESTARTER_RELEASE_URL, FIRESTARTER_RELEASES_URL

fm = FirmwareManager(config_manager=None)
version, asset_url = fm.fetch_release_info(channel="stable", board="uno")
print("channel: stable")
print("board: uno")
print(f"version: {version}")
print(f"asset_url: {asset_url}")
assert version, "expected a non-empty stable version"
assert asset_url and "henols/firestarter_fw" in asset_url, (
    f"asset_url does not name the renamed repository: {asset_url}"
)

for label, url in (
    ("FIRESTARTER_RELEASE_URL", FIRESTARTER_RELEASE_URL),
    ("FIRESTARTER_RELEASES_URL", FIRESTARTER_RELEASES_URL),
):
    r = requests.get(url, timeout=10)
    print(f"requested: {url}")
    print(f"resolved: {r.url}")
    print(f"status: {r.status_code}")
    print(f"redirects: {len(r.history)}")
    assert len(r.history) == 0, f"{label} followed {len(r.history)} redirect(s) -> {r.url}"
    assert r.url == url, f"{label} resolved to a different URL than requested: {r.url}"

print("CHECK1 OK")
PYEOF
then
    echo "FAIL: Check 1 (stable channel) -- python child failed." >&2
    echo "      Expected: a non-empty stable version, an asset_url naming" >&2
    echo "      henols/firestarter_fw, and redirects: 0 on both API endpoints." >&2
    echo "      Output:" >&2
    cat "$CHECK1_LOG" >&2
    exit 1
fi
cat "$CHECK1_LOG"
/usr/bin/grep -qFe "CHECK1 OK" "$CHECK1_LOG" || {
    echo "FAIL: Check 1 completed without printing its verdict token." >&2
    exit 1
}

# ---------------------------------------------------------------------------
# Check 2: pre channel, against a board the pre channel actually carries
# (uno328pb -- pre 3.0.0b29 ships it; stable 2.0.6 does not).
# ---------------------------------------------------------------------------
echo ""
echo "--- Check 2: pre channel ---"
if ! "$PYTHON_BIN" -P <<'PYEOF' >"$CHECK2_LOG" 2>&1
from firestarter.firmware import FirmwareManager

fm = FirmwareManager(config_manager=None)
version, asset_url = fm.fetch_release_info(channel="pre", board="uno328pb")
print("channel: pre")
print("board: uno328pb")
print(f"version: {version}")
print(f"asset_url: {asset_url}")
assert version, "expected a non-empty pre-release version"
assert asset_url and "henols/firestarter_fw" in asset_url, (
    f"asset_url does not name the renamed repository: {asset_url}"
)
print("CHECK2 OK")
PYEOF
then
    echo "FAIL: Check 2 (pre channel) -- python child failed." >&2
    echo "      Expected: a non-empty pre-release version and an asset_url" >&2
    echo "      naming henols/firestarter_fw for board uno328pb." >&2
    echo "      Output:" >&2
    cat "$CHECK2_LOG" >&2
    exit 1
fi
cat "$CHECK2_LOG"
/usr/bin/grep -qFe "CHECK2 OK" "$CHECK2_LOG" || {
    echo "FAIL: Check 2 completed without printing its verdict token." >&2
    exit 1
}

# ---------------------------------------------------------------------------
# Check 3: one real asset, downloaded through the package's own download
# helper (not a hand-rolled requests.get -- D-14 names this helper
# specifically), then format-checked as Intel HEX. Redirect-freedom is
# deliberately NOT asserted here: the asset download legitimately redirects
# to a release-assets host, and asserting otherwise would fail this check
# for an unrelated and correct reason (Finding 1 consequence 3).
# ---------------------------------------------------------------------------
echo ""
echo "--- Check 3: real asset download ---"
if ! "$PYTHON_BIN" -P <<'PYEOF' >"$CHECK3_LOG" 2>&1
from firestarter.firmware import FirmwareManager

fm = FirmwareManager(config_manager=None)
version, asset_url = fm.fetch_release_info(channel="stable", board="uno")
assert asset_url, "no asset_url resolved for board uno on the stable channel"

hex_path = fm._download_firmware_file(asset_url)
assert hex_path, "_download_firmware_file returned None"

with open(hex_path, "rb") as f:
    content = f.read()
lines = content.decode("ascii").splitlines()
non_empty = [ln for ln in lines if ln.strip()]

assert non_empty, "downloaded file has no non-empty lines"
assert all(ln.startswith(":") for ln in non_empty), (
    "not every non-empty line begins with ':' -- not Intel HEX"
)
assert non_empty[-1].strip() == ":00000001FF", (
    f"final record is not the Intel HEX EOF record: {non_empty[-1]!r}"
)

print(f"hex_path: {hex_path}")
print(f"hex_bytes: {len(content)}")
print(f"hex_first_line: {non_empty[0]}")
print(f"hex_eof: {non_empty[-1]}")
print("CHECK3 OK")
PYEOF
then
    echo "FAIL: Check 3 (real asset download) -- python child failed." >&2
    echo "      Expected: a non-empty download whose every line starts with ':'" >&2
    echo "      and whose final record is the Intel HEX EOF record ':00000001FF'." >&2
    echo "      Output:" >&2
    cat "$CHECK3_LOG" >&2
    exit 1
fi
cat "$CHECK3_LOG"
/usr/bin/grep -qFe "CHECK3 OK" "$CHECK3_LOG" || {
    echo "FAIL: Check 3 completed without printing its verdict token." >&2
    exit 1
}

# Remove the downloaded image by explicit path -- never the directory it
# sits in, which also holds the app's own config.json and reports/.
HEX_PATH="$(/usr/bin/grep '^hex_path: ' "$CHECK3_LOG" | sed 's/^hex_path: //')"
if [ "$KEEP_DOWNLOAD" != "1" ]; then
    if [ -n "$HEX_PATH" ] && [ -f "$HEX_PATH" ]; then
        rm -f -- "$HEX_PATH"
        echo "removed_download: $HEX_PATH"
    fi
else
    echo "kept_download: $HEX_PATH (KEEP_DOWNLOAD=1)"
fi

# ---------------------------------------------------------------------------
# Check 4a: the asset-less URL-04 failure, for real. Only the board-identity
# seam is simulated (no programmer is attached and the milestone requires
# no bench); the release resolution runs live against the real,
# correctly-named endpoint. Stable 2.0.6 genuinely carries no uno328pb
# asset (D-15), so this is a real "no asset for this board" result, not a
# mocked one.
# ---------------------------------------------------------------------------
echo ""
echo "--- Check 4a: asset-less failure (fw --board uno328pb --stable) ---"
if ! "$PYTHON_BIN" -P <<'PYEOF' >"$CHECK4A_LOG" 2>&1
from unittest.mock import patch

from click.testing import CliRunner

from firestarter.cli_handlers import cli
from firestarter.firmware import FirmwareManager

print(
    "simulated: board identity (uno328pb) only -- no programmer is attached and "
    "the milestone states Bench: none. Release resolution below is LIVE against "
    "henols/firestarter_fw."
)

with patch.object(
    FirmwareManager,
    "check_current_firmware",
    lambda self, **kwargs: ("/dev/ttyACM0", "3.1.0", "uno328pb"),
):
    # No obj= kwarg: this is what makes _setup_logging install the production
    # log handler, so logger.error routes to stdout exactly as a real
    # invocation does (RESEARCH Finding 5).
    result = CliRunner().invoke(cli, ["fw", "--board", "uno328pb", "--stable"])

print("case: asset-less")
print(f"exit_code: {result.exit_code}")
one_line = " | ".join(ln for ln in result.output.splitlines() if ln.strip())
print(f"message: {one_line}")

assert result.exit_code == 1, f"expected exit 1, got {result.exit_code}"
assert "uno328pb" in result.output, "message does not name the board"
assert "henols/firestarter_fw" in result.output, "message does not name the renamed endpoint"
assert "already up to date" not in result.output, (
    "message is not distinguishable from the already-up-to-date wording"
)
print("CHECK4A OK")
PYEOF
then
    echo "FAIL: Check 4a (asset-less failure) -- python child failed." >&2
    echo "      Expected: exit 1, with the message naming both 'uno328pb' and" >&2
    echo "      an endpoint containing henols/firestarter_fw." >&2
    echo "      Output:" >&2
    cat "$CHECK4A_LOG" >&2
    exit 1
fi
cat "$CHECK4A_LOG"
/usr/bin/grep -qFe "CHECK4A OK" "$CHECK4A_LOG" || {
    echo "FAIL: Check 4a completed without printing its verdict token." >&2
    exit 1
}

# ---------------------------------------------------------------------------
# Check 4b: the unreachable URL-04 failure, for real, in a throwaway child
# process. The endpoint constants are rebound on firestarter.firmware AND
# firestarter.cli_handlers -- NOT on firestarter.constants, which has no
# effect on names already imported by value (RESEARCH Pitfall 7). Both
# modules import the constant by name at their own module scope, so both
# bindings must be rebound for the printed message to actually name the
# nonexistent endpoint rather than the real one.
# ---------------------------------------------------------------------------
echo ""
echo "--- Check 4b: unreachable endpoint (fw --list) ---"
if ! NOPE_SLUG="$NOPE_SLUG" "$PYTHON_BIN" -P <<'PYEOF' >"$CHECK4B_LOG" 2>&1
import os

import firestarter.cli_handlers as C
import firestarter.firmware as F
from click.testing import CliRunner

nope_slug = os.environ["NOPE_SLUG"]
nope_url = f"https://api.github.com/repos/henols/{nope_slug}/releases"

# Rebind on the modules that hold the already-imported names, not on
# firestarter.constants (Pitfall 7). Both the network-calling module
# (firmware) and the message-printing module (cli_handlers) import this
# name independently.
F.FIRESTARTER_RELEASES_URL = nope_url
C.FIRESTARTER_RELEASES_URL = nope_url

result = CliRunner().invoke(C.cli, ["fw", "--list"])

print("case: unreachable")
print(f"nope_url: {nope_url}")
print(f"exit_code: {result.exit_code}")
stdout_one_line = " | ".join(ln for ln in result.stdout.splitlines() if ln.strip())
stderr_one_line = " | ".join(ln for ln in result.stderr.splitlines() if ln.strip())
print(f"stdout: {stdout_one_line}")
print(f"message: {stderr_one_line}")

assert result.exit_code == 1, f"expected exit 1, got {result.exit_code}"
assert nope_url in result.stderr, "stderr does not name the nonexistent endpoint"
assert "[" not in result.stdout and "null" not in result.stdout, (
    "a JSON document appeared on stdout on the failure path"
)
assert "already up to date" not in result.stderr, (
    "message is not distinguishable from the already-up-to-date wording"
)
print("CHECK4B OK")
PYEOF
then
    echo "FAIL: Check 4b (unreachable endpoint) -- python child failed." >&2
    echo "      Expected: exit 1, stderr naming the nonexistent endpoint," >&2
    echo "      and no JSON document ('[' or 'null') on stdout." >&2
    echo "      Output:" >&2
    cat "$CHECK4B_LOG" >&2
    exit 1
fi
cat "$CHECK4B_LOG"
/usr/bin/grep -qFe "CHECK4B OK" "$CHECK4B_LOG" || {
    echo "FAIL: Check 4b completed without printing its verdict token." >&2
    exit 1
}

# ---------------------------------------------------------------------------
# Cross-check: the two failure messages must differ from each other, and
# neither may be mistakable for the already-up-to-date wording. This is
# criterion 3's "not mistakable for" made checkable across both cases.
# ---------------------------------------------------------------------------
echo ""
echo "--- Cross-check: the two failure messages differ ---"
MSG_4A="$(/usr/bin/grep '^message: ' "$CHECK4A_LOG" | sed 's/^message: //')"
MSG_4B="$(/usr/bin/grep '^message: ' "$CHECK4B_LOG" | sed 's/^message: //')"
if [ "$MSG_4A" = "$MSG_4B" ]; then
    echo "FAIL: the asset-less and unreachable messages are identical." >&2
    echo "      message: $MSG_4A" >&2
    exit 1
fi
echo "case_4a_message differs from case_4b_message: yes"

# ---------------------------------------------------------------------------
# Verify the app repository was left untouched by every check above.
# ---------------------------------------------------------------------------
APP_STATUS="$(git -C "$APP_ROOT" status --porcelain)"
if [ -n "$APP_STATUS" ]; then
    echo "FAIL: firestarter_app working tree is dirty after the checks ran." >&2
    echo "$APP_STATUS" >&2
    exit 1
fi
echo "app_repo_porcelain: clean"

echo ""
echo "ENDPOINT CONTRACT OK"
exit 0
