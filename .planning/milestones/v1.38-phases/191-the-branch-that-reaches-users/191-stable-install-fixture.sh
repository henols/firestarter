#!/usr/bin/env bash
#
# 191-stable-install-fixture.sh
#
# Proves STABLE-02's whole claim rests on one observable: redirects == 0.
# The bare-slug and firestarter_fw release endpoints return byte-identical
# bodies (sha256 prefix 219633ebe41126a6, both tag_name 2.0.6) -- the only
# difference is len(r.history), 1 versus 0. A stale 2.0.7 install (still
# carrying the bare slug) passes any resolve-based check identically to a
# repointed one, so an exit code, a version string and an asset URL are all
# compatible with the pre-change state. This script installs the currently
# published stable into a scratch venv, drives it through its own firmware
# API to a live GitHub release asset, and asserts the redirect count -- the
# only thing that can tell the two states apart.
#
# Five checks, run against the live PyPI index and the live GitHub API, no
# bench, no avrdude:
#   0. provenance -- firestarter.__file__/__version__ resolve inside the
#      scratch venv (not a shadowing editable install), the version is a
#      plain release (no prerelease suffix), and PyPI's own JSON confirms
#      both the version and the project's Homepage URL
#   1. release resolution through the installed package's own
#      ConfigManager / FirmwareManager.fetch_latest_release_info
#   2. one real .hex asset downloaded through the package's own
#      _download_firmware_file, format-checked as Intel HEX, then removed
#      by explicit path
#   3. the redirect contract: a positive control (the bare-slug URL, which
#      MUST show exactly one redirect hop -- proof the probe can see a
#      redirect when one exists) and the subject assertion (the installed
#      FIRESTARTER_RELEASE_URL, which MUST show zero)
#   4. a porcelain guard over both git working trees this run touches
#
# This script deliberately contains the unqualified henols/firestarter
# slug as check 3's positive control URL. Phase 192's sweep must read that
# reference as intentional, not as a missed reference to repoint -- the
# same is already true of 190's fixture and 189's fixture. The control's
# expected single redirect hop is a property of the CURRENTLY UNCLAIMED old
# slug: if a later milestone claims henols/firestarter, the control's
# expected reading changes and this script's own positive control must be
# re-measured, not just its subject assertion.
#
# Usage:
#   bash 191-stable-install-fixture.sh                  # run all five checks
#   BOOTSTRAP_PYTHON=<path> bash 191-stable-install-fixture.sh
#   BOARD=uno bash 191-stable-install-fixture.sh
#   EXPECT_VERSION=2.0.9 bash 191-stable-install-fixture.sh
#   KEEP_VENV=1 bash 191-stable-install-fixture.sh      # keep the scratch venv
#   KEEP_DOWNLOAD=1 bash 191-stable-install-fixture.sh  # keep the downloaded .hex
#   bash 191-stable-install-fixture.sh --help           # print this usage and exit 0
#
# Environment:
#   BOOTSTRAP_PYTHON  interpreter used to CREATE the scratch venv
#                     (default: python3 -- the devcontainer default
#                     interpreter, per D-08; this deliberately does NOT
#                     pin py3.11 the way Phase 190's fixture does)
#   BOARD             board name passed to fetch_latest_release_info and
#                     used to derive the expected asset filename
#                     (default: leonardo -- the attached bench board)
#   EXPECT_VERSION    when non-empty, check 0 additionally asserts the
#                     installed version equals this string exactly
#                     (default: empty -- no additional assertion)
#   KEEP_VENV         1 = do not remove the scratch venv root on exit
#                     (default: 0)
#   KEEP_DOWNLOAD     1 = leave the downloaded firmware image in place
#                     instead of removing it by explicit path (default: 0)
#
# Dependencies: bash, git, curl, mktemp, python3 (able to create a venv).
# The one package installed is firestarter itself, from the live PyPI
# index -- no other package is introduced by this script.
#
# Failure style: bail-on-first-assertion, in the style of
# .planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/endpoint-contract-fixture.sh
# -- a failed earlier check makes a later one meaningless, so each check
# aborts immediately with the expectation, the captured output and the
# next action named.
#
# Exit codes:
#   0  STABLE INSTALL CONTRACT OK -- every check passed, including
#      redirects == 0 on the installed release constant
#   1  a check or an assertion failed for any other reason -- including,
#      by design, a run against today's published 2.0.7, which still
#      carries the bare slug and must fail check 3
#   2  bad usage (unrecognized argument)
#   3  the one named, expected non-failure case -- api.github.com or
#      pypi.org is not reachable from this container. This is a network
#      fact, not a URL regression; re-run when connectivity returns.
#
# Re-runnable: this script is idempotent and safe to run again. The venv
# lives under a fresh mktemp -d outside /workspaces, removed by a trap on
# EXIT unless KEEP_VENV=1; the downloaded .hex is removed by explicit path
# unless KEEP_DOWNLOAD=1 -- never with git clean -Xdf, which would also
# take the operator's own ~/.firestarter/config.json and reports/. Two
# runs in parallel are NOT supported: the app writes the downloaded asset
# to a fixed filename under ~/.firestarter and two concurrent runs would
# race on it.
set -euo pipefail

# ---------------------------------------------------------------------------
# Argument parsing -- fail-closed on anything unrecognized
# ---------------------------------------------------------------------------
for arg in "$@"; do
    case "$arg" in
        --help)
            sed -n '2,95p' "$0" | sed 's/^# \{0,1\}//'
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
# Environment knobs, all with defaults
# ---------------------------------------------------------------------------
BOOTSTRAP_PYTHON="${BOOTSTRAP_PYTHON:-python3}"
BOARD="${BOARD:-leonardo}"
EXPECT_VERSION="${EXPECT_VERSION:-}"
KEEP_VENV="${KEEP_VENV:-0}"
KEEP_DOWNLOAD="${KEEP_DOWNLOAD:-0}"

# ---------------------------------------------------------------------------
# Path resolution -- independent of caller's cwd; every root is derived from
# SCRIPT_DIR, never hardcoded. The phase directory sits at the same depth
# as 190's and 189's fixtures.
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
META_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
APP_ROOT="$META_ROOT/firestarter_app"
PHASE_DIR="$SCRIPT_DIR"
PHASE_REL="$(realpath --relative-to="$META_ROOT" "$PHASE_DIR")"
FIXTURE_REL="$PHASE_REL/191-stable-install-fixture.sh"
BASELINE_REL="$PHASE_REL/evidence/191-stable-02-fixture-baseline.txt"

# ---------------------------------------------------------------------------
# Preconditions -- checked before any work, each reporting to stderr
# ---------------------------------------------------------------------------
if ! command -v "$BOOTSTRAP_PYTHON" >/dev/null 2>&1; then
    echo "ERROR: BOOTSTRAP_PYTHON is not on PATH: $BOOTSTRAP_PYTHON" >&2
    exit 1
fi

if ! git -C "$META_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
    echo "ERROR: derived meta root is not a git repository: $META_ROOT" >&2
    exit 1
fi

if ! git -C "$APP_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
    echo "ERROR: derived app root is not a git repository: $APP_ROOT" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Transport probe, before any work -- distinguishes "no network" (exit 3)
# from a real check failure. Two probes, because this fixture needs the
# PyPI index as well as the GitHub Releases API; curl's %{http_code} prints
# 000 when the request could not be made at all (DNS, connect, TLS).
# ---------------------------------------------------------------------------
API_PROBE="$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 \
    https://api.github.com/repos/henols/firestarter_fw/releases/latest 2>/dev/null || echo "000")"
if [ "$API_PROBE" = "000" ]; then
    echo "NETWORK UNAVAILABLE: could not reach api.github.com (transport-level failure)." >&2
    echo "This reports the network, not a URL regression. Re-run when connectivity returns." >&2
    exit 3
fi

PYPI_PROBE="$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 \
    https://pypi.org/pypi/firestarter/json 2>/dev/null || echo "000")"
if [ "$PYPI_PROBE" = "000" ]; then
    echo "NETWORK UNAVAILABLE: could not reach pypi.org (transport-level failure)." >&2
    echo "This reports the network, not a URL regression. Re-run when connectivity returns." >&2
    exit 3
fi

# ---------------------------------------------------------------------------
# Scratch bookkeeping -- the venv lives under a fresh mktemp -d, resolved
# outside /workspaces so a later git clean -Xdf cannot take it, removed by
# a trap on EXIT unless KEEP_VENV=1. One mktemp log file per check.
# ---------------------------------------------------------------------------
SCRATCH_ROOT="$(mktemp -d)"
VENV_ROOT="$SCRATCH_ROOT/venv"
export VENV_ROOT
export EXPECT_VERSION
export BOARD

CHECK0_LOG="$(mktemp)"
CHECK1_LOG="$(mktemp)"
CHECK2_LOG="$(mktemp)"
CHECK3_LOG="$(mktemp)"

cleanup() {
    rm -f "$CHECK0_LOG" "$CHECK1_LOG" "$CHECK2_LOG" "$CHECK3_LOG"
    if [ "$KEEP_VENV" != "1" ]; then
        rm -rf "$SCRATCH_ROOT"
    fi
}
trap cleanup EXIT

echo "STABLE INSTALL FIXTURE (STABLE-02)"
echo "===================================="
echo "bootstrap_python: $BOOTSTRAP_PYTHON"
echo "board: $BOARD"
echo "meta_root: $META_ROOT"
echo "app_root: $APP_ROOT"
echo ""

"$BOOTSTRAP_PYTHON" -m venv "$VENV_ROOT"
VENV_PYTHON="$VENV_ROOT/bin/python"
echo "venv_root: $VENV_ROOT"
echo "venv_python: $VENV_PYTHON"
echo ""

# ---------------------------------------------------------------------------
# Install -- no --pre, no local install path, no version pin (D-08).
# --no-cache-dir is load-bearing: a post-publish re-run must resolve the
# live index rather than a cached wheel from a pre-publish run.
# ---------------------------------------------------------------------------
echo "--- Installing firestarter (--no-cache-dir, live index) ---"
"$VENV_ROOT/bin/pip" install --no-cache-dir --disable-pip-version-check firestarter
echo ""

# Every python child below is invoked with -P (PYTHONSAFEPATH, 3.11+).
# Without it Python prepends the caller's cwd to sys.path; when that cwd is
# /workspaces (the meta repo), the sibling firestarter/ FIRMWARE submodule
# forms a namespace package that shadows the real, pip-installed host
# package before its actual finder is ever consulted.

# ---------------------------------------------------------------------------
# Check 0: provenance, first, before anything else (D-08). An editable
# install in a sibling tree can shadow the PyPI package; a shadowed run
# would produce a perfect, meaningless transcript. Also asserts a plain
# release version (no prerelease suffix) and cross-checks PyPI's own JSON.
# ---------------------------------------------------------------------------
echo "--- Check 0: provenance + PyPI cross-check ---"
if ! "$VENV_PYTHON" -P <<'PYEOF' >"$CHECK0_LOG" 2>&1
import os
import re

import requests

import firestarter
from firestarter.constants import FIRESTARTER_RELEASE_URL

venv_root = os.environ["VENV_ROOT"]
expect_version = os.environ.get("EXPECT_VERSION", "")

installed_file = firestarter.__file__
installed_version = firestarter.__version__

print(f"installed_file: {installed_file}")
print(f"installed_version: {installed_version}")
print(f"installed_release_url: {FIRESTARTER_RELEASE_URL}")

assert installed_file.startswith(venv_root), (
    f"installed_file does not resolve inside the scratch venv ({venv_root}): {installed_file}"
)
assert re.match(r"^\d+\.\d+\.\d+$", installed_version), (
    f"installed_version is not a plain N.N.N release (a prerelease would fail STABLE-02): {installed_version}"
)
if expect_version:
    assert installed_version == expect_version, (
        f"installed_version {installed_version} does not match EXPECT_VERSION {expect_version}"
    )

resp = requests.get("https://pypi.org/pypi/firestarter/json", timeout=10)
resp.raise_for_status()
pypi_data = resp.json()
pypi_latest_stable = pypi_data["info"]["version"]
pypi_homepage = pypi_data["info"]["project_urls"]["Homepage"]

print(f"pypi_latest_stable: {pypi_latest_stable}")
print(f"pypi_homepage: {pypi_homepage}")

assert pypi_latest_stable == installed_version, (
    f"pip resolved {installed_version} but PyPI's current index reports {pypi_latest_stable} -- "
    "a stale or cached artefact may have been installed"
)
assert pypi_homepage == "https://github.com/henols/firestarter_app", (
    f"pypi_homepage does not match the expected project URL: {pypi_homepage}"
)

print("CHECK0 OK")
PYEOF
then
    echo "FAIL: Check 0 (provenance + PyPI cross-check) -- python child failed." >&2
    echo "      Expected: installed_file inside the scratch venv, a plain N.N.N" >&2
    echo "      installed_version, and PyPI's info.version/info.project_urls.Homepage" >&2
    echo "      matching the installed artefact." >&2
    echo "      Output:" >&2
    cat "$CHECK0_LOG" >&2
    exit 1
fi
cat "$CHECK0_LOG"
/usr/bin/grep -qFe "CHECK0 OK" "$CHECK0_LOG" || {
    echo "FAIL: Check 0 completed without printing its verdict token." >&2
    exit 1
}

# ---------------------------------------------------------------------------
# Check 1: release resolution through the installed package's own API --
# ConfigManager() (no arguments) and FirmwareManager(config_manager)
# (positional; there is no channel parameter anywhere on origin/main).
# ---------------------------------------------------------------------------
echo ""
echo "--- Check 1: release resolution through the installed package's own API ---"
if ! "$VENV_PYTHON" -P <<'PYEOF' >"$CHECK1_LOG" 2>&1
import os

from firestarter.config import ConfigManager
from firestarter.firmware import FirmwareManager

board = os.environ.get("BOARD", "leonardo")

config_manager = ConfigManager()
firmware_manager = FirmwareManager(config_manager)
latest_version, download_url = firmware_manager.fetch_latest_release_info(board=board)

print(f"board: {board}")
print(f"latest_version: {latest_version}")
print(f"download_url: {download_url}")

assert latest_version is not None, "fetch_latest_release_info returned None for latest_version"
assert download_url is not None, "fetch_latest_release_info returned None for download_url"
assert download_url.endswith(f"firestarter_{board}.hex"), (
    f"download_url does not end with firestarter_{board}.hex: {download_url}"
)

print("CHECK1 OK")
PYEOF
then
    echo "FAIL: Check 1 (release resolution) -- python child failed." >&2
    echo "      Expected: a non-empty latest_version and a download_url ending in" >&2
    echo "      firestarter_${BOARD}.hex, resolved through ConfigManager/FirmwareManager." >&2
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
# Check 2: one real asset, downloaded through the package's own
# _download_firmware_file (it returns a path or None -- it does not raise),
# then format-checked as Intel HEX and removed by explicit path.
# ---------------------------------------------------------------------------
echo ""
echo "--- Check 2: asset download and format check ---"
if ! "$VENV_PYTHON" -P <<'PYEOF' >"$CHECK2_LOG" 2>&1
import os

from firestarter.config import ConfigManager
from firestarter.firmware import FirmwareManager

board = os.environ.get("BOARD", "leonardo")

config_manager = ConfigManager()
firmware_manager = FirmwareManager(config_manager)
latest_version, download_url = firmware_manager.fetch_latest_release_info(board=board)
assert download_url, f"no download_url resolved for board {board}"

hex_path = firmware_manager._download_firmware_file(download_url)
assert hex_path is not None, "_download_firmware_file returned None"

with open(hex_path, "rb") as f:
    content = f.read()

print(f"hex_path: {hex_path}")
print(f"hex_bytes: {len(content)}")

assert len(content) > 0, "downloaded firmware file is empty"

hex_first_char = chr(content[0])
print(f"hex_first_char: {hex_first_char}")
assert hex_first_char == ":", (
    f"first byte of the downloaded file is not the Intel HEX record mark ':': {hex_first_char!r}"
)

print("CHECK2 OK")
PYEOF
then
    echo "FAIL: Check 2 (asset download) -- python child failed." >&2
    echo "      Expected: a non-empty downloaded file whose first byte is ':'" >&2
    echo "      (the Intel HEX record mark)." >&2
    echo "      Output:" >&2
    cat "$CHECK2_LOG" >&2
    exit 1
fi
cat "$CHECK2_LOG"
/usr/bin/grep -qFe "CHECK2 OK" "$CHECK2_LOG" || {
    echo "FAIL: Check 2 completed without printing its verdict token." >&2
    exit 1
}

# Remove the downloaded image by explicit path -- never the directory it
# sits in, which also holds the operator's own config.json and reports/.
HEX_PATH="$(/usr/bin/grep '^hex_path: ' "$CHECK2_LOG" | sed 's/^hex_path: //')"
if [ "$KEEP_DOWNLOAD" != "1" ]; then
    if [ -n "$HEX_PATH" ] && [ -f "$HEX_PATH" ]; then
        rm -f -- "$HEX_PATH"
        echo "removed_download: $HEX_PATH"
    fi
else
    echo "kept_download: $HEX_PATH (KEEP_DOWNLOAD=1)"
fi

# ---------------------------------------------------------------------------
# Check 3: the redirect contract, last, control first. Per D-07 this is the
# whole substance of the fixture -- the two endpoints return byte-identical
# bodies, so only the redirect count distinguishes the pre-change state
# from the repointed one. The control is printed BEFORE the subject
# assertion so a red run still carries it.
# ---------------------------------------------------------------------------
echo ""
echo "--- Check 3: the redirect contract (control, then subject) ---"
if ! "$VENV_PYTHON" -P <<'PYEOF' >"$CHECK3_LOG" 2>&1
import requests

from firestarter.constants import FIRESTARTER_RELEASE_URL

control_url = "https://api.github.com/repos/henols/firestarter/releases/latest"
r_control = requests.get(control_url, timeout=10)
print(f"control_url: {control_url}")
print(f"control_redirects: {len(r_control.history)}")
assert len(r_control.history) == 1, (
    f"control observed {len(r_control.history)} redirect hop(s), expected exactly 1 -- "
    "the probe cannot see a redirect it exists to detect"
)

subject_url = FIRESTARTER_RELEASE_URL
r_subject = requests.get(subject_url, timeout=10)
print(f"subject_url: {subject_url}")
print(f"subject_status: {r_subject.status_code}")
print(f"subject_redirects: {len(r_subject.history)}")

assert len(r_subject.history) == 0, (
    f"FIRESTARTER_RELEASE_URL followed {len(r_subject.history)} redirect(s) -> {r_subject.url} -- "
    "the installed constant still carries the unclaimed bare slug"
)
assert r_subject.url == subject_url, (
    f"subject resolved to a different URL than requested: {r_subject.url}"
)

print("CHECK3 OK")
PYEOF
then
    echo "FAIL: Check 3 (redirect contract) -- python child failed." >&2
    echo "      Expected: control_redirects == 1 (proves the probe can see a" >&2
    echo "      redirect when one exists) AND subject_redirects == 0 (proves the" >&2
    echo "      installed FIRESTARTER_RELEASE_URL no longer carries the bare slug)." >&2
    echo "      Output:" >&2
    cat "$CHECK3_LOG" >&2
    exit 1
fi
cat "$CHECK3_LOG"
/usr/bin/grep -qFe "CHECK3 OK" "$CHECK3_LOG" || {
    echo "FAIL: Check 3 completed without printing its verdict token." >&2
    exit 1
}

# ---------------------------------------------------------------------------
# Check 4: porcelain guard -- verifies this run touched neither the app
# working tree nor anything in the phase directory beyond the fixture and
# its baseline transcript (both expected, whether still untracked from
# Task 1's own run or already committed by Task 2).
# ---------------------------------------------------------------------------
echo ""
echo "--- Check 4: porcelain guard ---"
APP_STATUS="$(git -C "$APP_ROOT" status --porcelain)"
if [ -n "$APP_STATUS" ]; then
    echo "FAIL: firestarter_app working tree is dirty after the checks ran." >&2
    echo "$APP_STATUS" >&2
    exit 1
fi
echo "app_repo_porcelain: clean"

META_STATUS="$(git -C "$META_ROOT" status --porcelain -- "$PHASE_DIR")"
UNEXPECTED="$(printf '%s\n' "$META_STATUS" | /usr/bin/grep -vFe "$FIXTURE_REL" | /usr/bin/grep -vFe "$BASELINE_REL" | /usr/bin/grep -v '^[[:space:]]*$' || true)"
if [ -n "$UNEXPECTED" ]; then
    echo "FAIL: unexpected change(s) in the phase directory beyond the fixture and its baseline:" >&2
    echo "$UNEXPECTED" >&2
    exit 1
fi
echo "CHECK4 OK"

echo ""
echo "STABLE INSTALL CONTRACT OK"
exit 0
