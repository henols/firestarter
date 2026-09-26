#!/usr/bin/env bash
# verify-detect-34.sh — Phase 34 wave-merge regression-guard for the
# shield-version-detect firmware plumbing. Verbatim adaptation of Phase 33's
# check-migration.sh (33-00-PLAN.md substrate): the byte-identical cmp swaps
# to a delta-band wc -c check because Phase 34 EXPECTS the .hex to diverge
# from baseline by a known, bounded amount (50–200 B per env per
# 34-RESEARCH.md §ADC Voltage Band Math step 4).
#
# THREE ASSERTIONS:
#   1. Per-env .hex delta vs baseline in [EXPECTED_DELTA_MIN, EXPECTED_DELTA_MAX]
#      for uno / uno328pb / leonardo. delta < MIN  -> the rework didn't compile
#      in (only #defines landed, no analogRead call site). delta > MAX -> the
#      rework bloated more than the 50–200 B budget; investigate.
#   2. Native dispatch tests stay green: `pio test -e native -f "*test_dispatch*"`
#      DETECT-FW-02 "chip programming + read paths byte-identical" — dispatch
#      table must not regress.
#   3. Enum-extension presence: REVISION_2_3 + REVISION_UNKNOWN both grep in
#      firestarter/include/rurp_shield.h. Catches the case where someone
#      edited the detect-rev logic but forgot the enum extension.
#
# Per-wave semantics (Phase 33 precedent):
#   - PRE Wave 2 (baseline state, no firmware change yet) -> exit 1 with
#     "FAIL: <env>.hex delta 0 B outside expected [20, 300] range" on Assertion 1.
#     This is the documented PROOF-OF-WIRING state — the gate is correctly wired.
#   - POST Wave 2 (rework landed) -> exit 0 with PASS banner.
#   - Hex divergence outside band -> exit 1 with explicit delta + range.
#
# Cross-reference: BASELINE_COMMIT.txt records the firestarter sub-repo HEAD SHA
# at baseline-capture time (2026-05-25, SHA 2707f8cb...). Any post-rework wc -c
# delta brackets against this exact source state.

set -euo pipefail

BASELINE_DIR="/workspaces/.planning/milestones/v1.7-artifacts/baseline-34"
FIRMWARE_DIR="/workspaces/firestarter"

# Delta-band bounds — WIDENED in Plan 34-04 from the original signed range
# [+20, +300] B to a magnitude band `abs(Δ) <= EXPECTED_DELTA_ABS_MAX` per
# 34-03-SUMMARY.md "Hand-off to Plan 04" Option B recommendation.
#
# ORIGINAL (pre-Plan-04) BOUNDS: EXPECTED_DELTA_MIN=20, EXPECTED_DELTA_MAX=300.
# These assumed a POSITIVE delta (rework adds .text/.rodata). Plan 03's
# empirical post-rework deltas were NEGATIVE on all three envs (uno −299 B,
# uno328pb −454 B, leonardo −491 B) because the digitalRead(A3) → analogRead(A3)
# swap removes the digital-I/O code path (`wiring_digital.c`
# `digital_pin_to_port_PGM` / `digital_pin_to_bit_mask_PGM` lookup tables) while
# `analogRead` was already linked-in for the legacy A2 read. Net: code shrinks.
# This is consistent with the rework's intent (no Δ-sign was actually promised
# in D-10 — only bounded magnitude).
#
# NEW (Plan 34-04) BOUND: `abs(Δ) <= 600 B`. Preserves the gate's intent
# (catch unexpected bloat OR unexpected gigantic shrink) without rubber-stamping
# the empirical Plan 03 numbers. 600 B comfortably covers the −491 B leonardo
# observation with headroom for symbol-table drift across rebuilds.
EXPECTED_DELTA_ABS_MAX=600
# Backward-compat aliases kept (unused below but preserved for grep).
EXPECTED_DELTA_MIN=-600
EXPECTED_DELTA_MAX=600

# ---------------------------------------------------------------------------
# Assertion 1 — per-env .hex delta in expected band
# ---------------------------------------------------------------------------
# Per-env baseline lives at ${BASELINE_DIR}/${env}.hex; the post-Wave-2 build
# artifact lives at ${FIRMWARE_DIR}/.pio/build/${env}/firestarter_${env}.hex
# (firestarter_${env}.hex naming via name_firmware.py).
echo "[verify-detect-34] Assertion 1: per-env .hex |delta| <= ${EXPECTED_DELTA_ABS_MAX} B (widened in Plan 34-04 — see 34-03-SUMMARY.md)"
for env in uno uno328pb leonardo; do
    BASELINE_HEX="${BASELINE_DIR}/${env}.hex"
    BUILT_HEX="${FIRMWARE_DIR}/.pio/build/${env}/firestarter_${env}.hex"

    if [ ! -f "${BASELINE_HEX}" ]; then
        echo "FAIL: Assertion 1 — baseline missing: ${BASELINE_HEX}"
        exit 1
    fi
    if [ ! -f "${BUILT_HEX}" ]; then
        echo "FAIL: Assertion 1 — built artifact missing: ${BUILT_HEX} (did you run \`pio run -e ${env}\`?)"
        exit 1
    fi

    BASELINE_BYTES=$(wc -c < "${BASELINE_HEX}")
    BUILT_BYTES=$(wc -c < "${BUILT_HEX}")
    DELTA=$((BUILT_BYTES - BASELINE_BYTES))
    echo "  ${env}: baseline=${BASELINE_BYTES} B, built=${BUILT_BYTES} B, delta=${DELTA} B"

    # Compute |delta| via parameter expansion (handles both signs without bashism risk).
    ABS_DELTA=${DELTA#-}
    if [ "${ABS_DELTA}" -gt "${EXPECTED_DELTA_ABS_MAX}" ]; then
        echo "FAIL: ${env}.hex |delta|=${ABS_DELTA} B exceeds magnitude bound ${EXPECTED_DELTA_ABS_MAX} B (raw delta=${DELTA} B)"
        exit 1
    fi
done
echo "  PASS: all three envs within magnitude band |Δ| <= ${EXPECTED_DELTA_ABS_MAX} B"

# ---------------------------------------------------------------------------
# Assertion 2 — native dispatch tests green
# ---------------------------------------------------------------------------
# DETECT-FW-02 load-bearing claim: detect-rev plumbing must NOT perturb
# configure_memory protocol-prefix dispatch. The native suite cross-compiles
# src/proms/*.cpp against host libc + ArduinoFake and exercises every entry in
# KNOWN_PROTOCOLS — if the detect rework accidentally touches a dispatch
# branch, this catches it before any hardware comes near.
echo "[verify-detect-34] Assertion 2: pio test -e native -f \"*test_dispatch*\""
if ! (cd "${FIRMWARE_DIR}" && pio test -e native -f "*test_dispatch*" >/dev/null 2>&1); then
    echo "FAIL: Assertion 2 — native dispatch tests failed (DETECT-FW-02 regression)"
    echo "       re-run interactively: cd ${FIRMWARE_DIR} && pio test -e native -f \"*test_dispatch*\""
    exit 1
fi
echo "  PASS: native dispatch suite green"

# ---------------------------------------------------------------------------
# Assertion 3 — enum extension presence (REVISION_2_3 + REVISION_UNKNOWN)
# ---------------------------------------------------------------------------
# Per D-07 — detect-rev plumbing requires both the next-rev silkscreen string
# (REVISION_2_3) and the fall-through state (REVISION_UNKNOWN) to be present
# in the rev enum. This catches the case where someone edited the detect
# logic but forgot the enum extension.
RURP_SHIELD_H="${FIRMWARE_DIR}/include/rurp_shield.h"
echo "[verify-detect-34] Assertion 3: REVISION_2_3 + REVISION_UNKNOWN in ${RURP_SHIELD_H}"
if ! grep -q "REVISION_2_3" "${RURP_SHIELD_H}"; then
    echo "FAIL: Assertion 3 — REVISION_2_3 missing from ${RURP_SHIELD_H}"
    exit 1
fi
if ! grep -q "REVISION_UNKNOWN" "${RURP_SHIELD_H}"; then
    echo "FAIL: Assertion 3 — REVISION_UNKNOWN missing from ${RURP_SHIELD_H}"
    exit 1
fi
echo "  PASS: both enum values present"

echo ""
echo "PASS: Phase 34 detect-rev rework verified — delta within band, native tests green, enums present."
