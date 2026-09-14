#!/usr/bin/env bash
# v1.4-e2e-verify.sh
#
# Post-cut automated verifier for v1.4 E2E-01 sub-criteria.
# Mechanically verifies (a) PyPI pre-release visibility, (c) firmware GitHub Pre-release
# shape, and (d) lockstep version string equality. Optionally probes (e) via
# 'firestarter fw --list --pre' when the beta app is installed locally.
#
# Sub-criteria (b), (e), (f) are HUMAN-UAT items in '20-HUMAN-UAT.md' (D-06) -- they
# require operator interaction with live installs and/or flash hardware and cannot be
# automated by a script.
#
# Usage:
#   bash .planning/v1.4-e2e-verify.sh <BETA_VERSION> [--quick]
#
#   BETA_VERSION  -- PEP 440 pre-release version string, e.g. 0.0.1b1, 3.1.0rc2.
#                    Must match: ^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$
#   --quick       -- Skip Step 4 (the 'firestarter fw --list --pre' probe that requires
#                    the beta app to be installed locally). Default mode runs all 4 steps.
#
# Exit codes:
#   0  All checks passed (or skipped via --quick).
#   1  One or more checks failed; failure summary printed to stderr.
#   2  Bad usage (missing BETA_VERSION or unrecognized flag).

set -euo pipefail

# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------
usage() {
    cat >&2 <<EOF
Usage: bash .planning/v1.4-e2e-verify.sh <BETA_VERSION> [--quick]

  BETA_VERSION  PEP 440 pre-release string, e.g. 0.0.1b1, 3.1.0b2, 3.1.0rc1
                Must match: ^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$
  --quick       Skip Step 4 (firestarter fw --list --pre probe; requires local beta install)

Exit codes: 0=all green, 1=check(s) failed, 2=bad usage
EOF
    exit 2
}

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
BETA_VERSION=""
QUICK_MODE=0

for arg in "$@"; do
    case "$arg" in
        --quick) QUICK_MODE=1 ;;
        --*)
            echo "ERROR: unrecognized flag: $arg" >&2
            usage
            ;;
        *)
            if [ -z "$BETA_VERSION" ]; then
                BETA_VERSION="$arg"
            else
                echo "ERROR: unexpected positional argument: $arg" >&2
                usage
            fi
            ;;
    esac
done

if [ -z "$BETA_VERSION" ]; then
    echo "ERROR: BETA_VERSION is required." >&2
    usage
fi

# ---------------------------------------------------------------------------
# PEP 440 pre-release validation
# ---------------------------------------------------------------------------
BETA_VERSION_RE='^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$'
if ! echo "$BETA_VERSION" | grep -qE "$BETA_VERSION_RE"; then
    echo "ERROR: BETA_VERSION '$BETA_VERSION' does not match PEP 440 pre-release pattern." >&2
    echo "       Accepted examples: 0.0.1b1, 3.1.0b2, 3.1.0rc1" >&2
    echo "       Rejected examples: 3.1.0beta1, 3.1.0-b1, 3.1.0B1, 3.1.0a1, 3.1.0, 3.1.0.post1" >&2
    exit 2
fi

# ---------------------------------------------------------------------------
# Tool prerequisites
# ---------------------------------------------------------------------------
check_tool() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "ERROR: required tool not found: $1" >&2
        echo "       Install $1 and re-run." >&2
        exit 1
    fi
}

check_tool curl
check_tool gh
check_tool jq

if ! gh auth status >/dev/null 2>&1; then
    echo "ERROR: 'gh auth status' failed -- run 'gh auth login' first." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# State tracking
# ---------------------------------------------------------------------------
FAILURES=()
STEP1_RESULT="[SKIP]"
STEP2_RESULT="[SKIP]"
STEP3_RESULT="[SKIP]"
STEP4_RESULT="[SKIP]"

echo "===== E2E VERIFY for BETA_VERSION=$BETA_VERSION ====="
echo ""

# ---------------------------------------------------------------------------
# Step 1 -- PyPI pre-release visibility (sub-criterion a)
# ---------------------------------------------------------------------------
echo "[Step 1] Checking PyPI for $BETA_VERSION ..."
PYPI_CACHE="/tmp/firestarter-pypi.json"
if curl -fsSL "https://pypi.org/pypi/firestarter/json" -o "$PYPI_CACHE"; then
    MATCHED="$(jq -r --arg v "$BETA_VERSION" '.releases | keys[] | select(. == $v)' "$PYPI_CACHE" 2>/dev/null || true)"
    if [ -n "$MATCHED" ]; then
        echo "  [OK] PyPI shows $BETA_VERSION in releases."
        STEP1_RESULT="[PASS]"
    else
        echo "  [FAIL] PyPI does not show $BETA_VERSION in releases." >&2
        STEP1_RESULT="[FAIL]"
        FAILURES+=("Step 1: PyPI does not show $BETA_VERSION in releases (check that the app beta-release workflow completed successfully).")
    fi
else
    echo "  [FAIL] curl to PyPI JSON API failed (network error or HTTP error)." >&2
    STEP1_RESULT="[FAIL]"
    FAILURES+=("Step 1: curl to https://pypi.org/pypi/firestarter/json failed.")
fi

# ---------------------------------------------------------------------------
# Step 2 -- Firmware GitHub Pre-release shape (sub-criterion c)
# ---------------------------------------------------------------------------
echo "[Step 2] Checking firmware GitHub Release for $BETA_VERSION ..."
FW_RELEASE_CACHE="/tmp/firestarter-fw-release.json"
if gh release view "$BETA_VERSION" -R henols/firestarter_fw \
       --json isPrerelease,assets \
       > "$FW_RELEASE_CACHE" 2>/dev/null; then

    STEP2_ISSUES=()

    IS_PRERELEASE="$(jq -r '.isPrerelease' "$FW_RELEASE_CACHE")"
    if [ "$IS_PRERELEASE" != "true" ]; then
        STEP2_ISSUES+=("  isPrerelease is not true (got: $IS_PRERELEASE) -- release must be marked Pre-release.")
    fi

    # gh CLI does NOT expose isLatest in `release view --json` -- fall back to
    # the REST API (repos/.../releases/latest) and compare tag_name. If the
    # "latest" release equals BETA_VERSION, then make_latest is incorrectly
    # set (Pre-release must not be the Latest marker).
    LATEST_TAG="$(gh api "repos/henols/firestarter_fw/releases/latest" --jq '.tag_name' 2>/dev/null || true)"
    if [ "$LATEST_TAG" = "$BETA_VERSION" ]; then
        STEP2_ISSUES+=("  Latest release tag equals $BETA_VERSION -- Pre-release must NOT be marked Latest.")
    fi

    HAS_UNO="$(jq -e '(.assets | map(.name) | any(. == "firestarter_uno.hex"))' "$FW_RELEASE_CACHE" >/dev/null 2>&1 && echo "true" || echo "false")"
    if [ "$HAS_UNO" != "true" ]; then
        STEP2_ISSUES+=("  firestarter_uno.hex not found in release assets.")
    fi

    HAS_LEONARDO="$(jq -e '(.assets | map(.name) | any(. == "firestarter_leonardo.hex"))' "$FW_RELEASE_CACHE" >/dev/null 2>&1 && echo "true" || echo "false")"
    if [ "$HAS_LEONARDO" != "true" ]; then
        STEP2_ISSUES+=("  firestarter_leonardo.hex not found in release assets.")
    fi

    if [ "${#STEP2_ISSUES[@]}" -eq 0 ]; then
        echo "  [OK] isPrerelease=true, latest!=$BETA_VERSION, firestarter_uno.hex + firestarter_leonardo.hex present."
        STEP2_RESULT="[PASS]"
    else
        echo "  [FAIL] Firmware release $BETA_VERSION has issues:" >&2
        for issue in "${STEP2_ISSUES[@]}"; do
            echo "    $issue" >&2
            FAILURES+=("Step 2: $issue")
        done
        STEP2_RESULT="[FAIL]"
    fi
else
    echo "  [FAIL] 'gh release view $BETA_VERSION -R henols/firestarter_fw' failed -- release may not exist yet." >&2
    STEP2_RESULT="[FAIL]"
    FAILURES+=("Step 2: gh release view $BETA_VERSION -R henols/firestarter_fw failed (release not found or network error).")
fi

# ---------------------------------------------------------------------------
# Step 3 -- Lockstep tag equality (sub-criterion d / VER-03)
# ---------------------------------------------------------------------------
echo "[Step 3] Checking lockstep tag equality across both repos ..."
APP_TAG=""
FW_TAG=""
APP_OK=1
FW_OK=1

APP_TAG="$(gh release view "$BETA_VERSION" -R henols/firestarter_app --json tagName -q .tagName 2>/dev/null || true)"
if [ -z "$APP_TAG" ]; then
    echo "  [FAIL] gh release view $BETA_VERSION -R henols/firestarter_app: not found or empty tagName." >&2
    FAILURES+=("Step 3: release $BETA_VERSION not found in henols/firestarter_app.")
    APP_OK=0
fi

FW_TAG="$(gh release view "$BETA_VERSION" -R henols/firestarter_fw --json tagName -q .tagName 2>/dev/null || true)"
if [ -z "$FW_TAG" ]; then
    echo "  [FAIL] gh release view $BETA_VERSION -R henols/firestarter_fw: not found or empty tagName." >&2
    FAILURES+=("Step 3: release $BETA_VERSION not found in henols/firestarter_fw.")
    FW_OK=0
fi

if [ "$APP_OK" -eq 1 ] && [ "$FW_OK" -eq 1 ]; then
    if [ "$APP_TAG" = "$FW_TAG" ] && [ "$APP_TAG" = "$BETA_VERSION" ]; then
        echo "  [OK] app tag=$APP_TAG, fw tag=$FW_TAG -- byte-identical to BETA_VERSION."
        STEP3_RESULT="[PASS]"
    else
        echo "  [FAIL] Tag mismatch: app=$APP_TAG fw=$FW_TAG expected=$BETA_VERSION" >&2
        STEP3_RESULT="[FAIL]"
        FAILURES+=("Step 3: tag mismatch -- app=$APP_TAG fw=$FW_TAG expected=$BETA_VERSION (VER-03 lockstep violated).")
    fi
else
    STEP3_RESULT="[FAIL]"
fi

# ---------------------------------------------------------------------------
# Step 4 -- Local beta-app firmware listing probe (sub-criterion e dry-run)
# ---------------------------------------------------------------------------
echo "[Step 4] Checking local firestarter fw --list --pre ..."
if [ "$QUICK_MODE" -eq 1 ]; then
    echo "  [skip] Step 4 (firestarter fw --list) per --quick flag."
    STEP4_RESULT="[SKIP]"
else
    if ! command -v firestarter >/dev/null 2>&1; then
        echo "  [NOTE] 'firestarter' is not installed in this environment."
        echo "         To run Step 4, install the beta app first:"
        echo "           python3 -m venv /tmp/e2e-beta && source /tmp/e2e-beta/bin/activate"
        echo "           pip install --pre firestarter==$BETA_VERSION"
        echo "         Then re-run this script (without --quick)."
        echo "         Or pass --quick to skip this step."
        STEP4_RESULT="[NOTE]"
    else
        FW_LIST_CACHE="/tmp/firestarter-fw-list.txt"
        if firestarter fw --list --pre 2>&1 | tee "$FW_LIST_CACHE" >/dev/null; then
            if grep -q "$BETA_VERSION" "$FW_LIST_CACHE"; then
                echo "  [OK] 'firestarter fw --list --pre' output contains $BETA_VERSION."
                STEP4_RESULT="[PASS]"
            else
                echo "  [FAIL] 'firestarter fw --list --pre' did not show $BETA_VERSION in output." >&2
                STEP4_RESULT="[FAIL]"
                FAILURES+=("Step 4: 'firestarter fw --list --pre' output did not contain $BETA_VERSION.")
            fi
        else
            echo "  [FAIL] 'firestarter fw --list --pre' exited with a non-zero status." >&2
            STEP4_RESULT="[FAIL]"
            FAILURES+=("Step 4: 'firestarter fw --list --pre' command failed (non-zero exit).")
        fi
    fi
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "===== E2E VERIFY SUMMARY ====="
echo "  Step 1 (PyPI visibility      -- sub-criterion a): $STEP1_RESULT"
echo "  Step 2 (FW GitHub Pre-release -- sub-criterion c): $STEP2_RESULT"
echo "  Step 3 (Lockstep tag equality -- sub-criterion d): $STEP3_RESULT"
echo "  Step 4 (fw --list --pre probe -- sub-criterion e): $STEP4_RESULT"
echo ""

if [ "${#FAILURES[@]}" -eq 0 ]; then
    echo "ALL CHECKS PASSED for BETA_VERSION=$BETA_VERSION"
    echo ""
    echo "Next: walk through .planning/phases/20-end-to-end-smoke-test-milestone-close/20-HUMAN-UAT.md"
    echo "and mark each test result (sub-criteria b, e, f require operator install + hardware steps)."
    exit 0
else
    echo "FAILURES (${#FAILURES[@]}):" >&2
    for failure in "${FAILURES[@]}"; do
        echo "  - $failure" >&2
    done
    echo "" >&2
    echo "Fix the above issues and re-run to confirm all checks pass before proceeding to HUMAN-UAT.md." >&2
    exit 1
fi
