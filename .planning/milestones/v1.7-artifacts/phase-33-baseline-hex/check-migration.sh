#!/usr/bin/env bash
#
# Phase 33 wave-merge regression-guard for the silkscreen-label → code-alias
# migration. Wraps three assertions:
#
#   Assertion 1: grep-zero for the 8 old shield-net names in firestarter
#                source (include/ src/ test/) using word boundaries.
#                Comment-line `//`-prefixed hits are filtered out so historical
#                comment refresh has flexibility (CONTEXT D-?? / Open Q4).
#   Assertion 2: REV_[12]_* prefix family fully removed (Pitfall 3) — except
#                `REVISION_*` enum values which are NOT renamed per D-03.
#   Assertion 3: post-rename .hex byte-identical (cmp) against the captured
#                pre-rename baseline for all three AVR envs (uno / uno328pb /
#                leonardo) — GATE-1.7 ALIAS-03 non-regression gate.
#
# Pre-Wave-1: Assertion 1 will FAIL (the old names still exist — that's the
# load-bearing proof that the gate is wired correctly).
# Post-Wave-3: all 3 assertions PASS — prints "PASS: alias migration verified
# clean".
#
# Baseline captured by phase-33 plan 33-00. The baseline .hex files + the
# BASELINE_COMMIT.txt live alongside this script under .planning/milestones/v1.7-artifacts/ and are
# gitignored (Phase 31 D-11).

set -euo pipefail

# Baseline lives under .planning/milestones/v1.7-artifacts/phase-33-baseline-hex/ (gitignored per Phase 31 D-11).
BASELINE_DIR="/workspaces/.planning/milestones/v1.7-artifacts/phase-33-baseline-hex"
FIRMWARE_DIR="/workspaces/firestarter"
INCLUDE_DIR="${FIRMWARE_DIR}/include"
SRC_DIR="${FIRMWARE_DIR}/src"
TEST_DIR="${FIRMWARE_DIR}/test"

# --- Assertion 1: 8 old shield-net names must be gone from firmware source.
# Word boundaries (\b...\b) avoid false positives on the comment "CONTROL
# REGISTER" header where REGULATOR is a substring of a header phrase but not
# the bare token (Pitfall 8 / Pattern H).
# Comment-line filter strips '//'-prefixed-content hits so a stray historical
# doc-line comment does not block the gate (Open Q4).
OLD_NAMES_HITS=$( { grep -rn '\b\(VPE_ENABLE\|VPE_TO_VPP\|P1_VPP_ENABLE\|A9_VPP_ENABLE\|READ_WRITE\|REGULATOR\|HARDWARE_REVISION_PIN\|VOLTAGE_MEASURE_PIN\)\b' "${INCLUDE_DIR}/" "${SRC_DIR}/" "${TEST_DIR}/" 2>/dev/null || true; } | { grep -v '^[^:]*:[0-9]*:[[:space:]]*//' || true; } | wc -l)

if [ "${OLD_NAMES_HITS}" -ne 0 ]; then
    echo "FAIL: Assertion 1 — found ${OLD_NAMES_HITS} non-comment references to the 8 old shield-net names in firmware source."
    echo "      Expected 0 post-rename. Pre-rename this is the baseline (≥86 hits per RESEARCH.md)."
    echo "      Re-run after Wave 3 lands the call-site sweep."
    exit 1
fi

# --- Assertion 2: REV_[12]_* prefix family must be removed (Pitfall 3).
# Exclude `REVISION_*` enum values which are NOT renamed per D-03.
REV_HITS=$( { grep -rn 'REV_[12]_' "${INCLUDE_DIR}/" "${SRC_DIR}/" 2>/dev/null || true; } | { grep -v 'REVISION_' || true; } | wc -l)

if [ "${REV_HITS}" -ne 0 ]; then
    echo "FAIL: Assertion 2 — found ${REV_HITS} references to the REV_[12]_* prefix family in firmware source."
    echo "      Expected 0 post-rename (REVISION_* enum values excluded per D-03)."
    exit 1
fi

# --- Assertion 3: post-rename .hex must be byte-identical to baseline for
# every AVR env — GATE-1.7 ALIAS-03 load-bearing gate.
for env in uno uno328pb leonardo; do
    BASELINE_HEX="${BASELINE_DIR}/${env}.hex"
    BUILT_HEX="${FIRMWARE_DIR}/.pio/build/${env}/firestarter_${env}.hex"

    if [ ! -f "${BASELINE_HEX}" ]; then
        echo "FAIL: Assertion 3 — baseline hex missing for ${env} (${BASELINE_HEX})."
        echo "      Re-run phase-33 plan 33-00 to recapture the pre-rename baseline."
        exit 1
    fi

    if [ ! -f "${BUILT_HEX}" ]; then
        echo "FAIL: Assertion 3 — post-rename build artifact missing for ${env} (${BUILT_HEX})."
        echo "      Run 'cd /workspaces/firestarter && pio run -e ${env}' before re-checking."
        exit 1
    fi

    # cmp against .planning/milestones/v1.7-artifacts/phase-33-baseline-hex/${env}.hex
    if ! cmp -s "${BASELINE_HEX}" "${BUILT_HEX}"; then
        echo "FAIL: ${env}.hex diverged from baseline"
        echo "      baseline: ${BASELINE_HEX} ($(wc -c < "${BASELINE_HEX}") B)"
        echo "      built:    ${BUILT_HEX} ($(wc -c < "${BUILT_HEX}") B)"
        echo "      diff (first 20 byte positions): $(cmp -l "${BASELINE_HEX}" "${BUILT_HEX}" 2>/dev/null | head -20)"
        exit 1
    fi
done

echo "PASS: alias migration verified clean"
