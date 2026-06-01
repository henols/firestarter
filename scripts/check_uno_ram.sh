#!/usr/bin/env bash
# check_uno_ram.sh — scripted Uno RAM-ceiling assertion (FRAME-03 gate)
#
# Phase 50 Plan 01 — automates the FRAME-03 build-report check.
#
# Runs `pio run -e uno`, parses the linker RAM report line:
#   RAM:   [=======   ]  73.4% (used N bytes from M bytes)
# computes free RAM = M - N, and fails (exit 1) if free RAM < RAM_FLOOR.
#
# Usage:
#   bash scripts/check_uno_ram.sh          # from repo root
#   cd firestarter && bash scripts/check_uno_ram.sh
#
# Exit codes:
#   0  — free RAM >= RAM_FLOOR (baseline passes)
#   1  — free RAM < RAM_FLOOR (regression detected)
#   2  — could not parse the RAM line from build output

set -euo pipefail

# ---------------------------------------------------------------------------
# Baseline floor (Phase-49 / 2026-06-01 measurement: 1503 B used / 2048 B total)
# Change only when the accepted baseline changes after a deliberate Plan 04
# post-change measurement confirms the new floor is still safe.
# ---------------------------------------------------------------------------
RAM_FLOOR=545   # minimum acceptable free RAM in bytes (Phase-49 baseline ceiling)

# ---------------------------------------------------------------------------
# Run the Uno firmware build and capture its output
# ---------------------------------------------------------------------------
echo "[check_uno_ram] Running: pio run -e uno ..."
BUILD_OUTPUT="$(pio run -e uno 2>&1)"

# ---------------------------------------------------------------------------
# Parse the RAM report line:
#   RAM:   [== ]  73.4% (used 1503 bytes from 2048 bytes)
# We extract the two numbers after "used" and "from".
# ---------------------------------------------------------------------------
RAM_LINE="$(echo "$BUILD_OUTPUT" | grep -E '^RAM:')"

if [ -z "$RAM_LINE" ]; then
    echo "[check_uno_ram] ERROR: could not find 'RAM:' line in pio output."
    echo "$BUILD_OUTPUT" | tail -20
    exit 2
fi

echo "[check_uno_ram] Parsed RAM line: $RAM_LINE"

# Extract N (used bytes) and M (total bytes) using grep+sed
# RAM line format: "RAM:   [=======   ]  73.4% (used 1503 bytes from 2048 bytes)"
USED_BYTES="$(echo "$RAM_LINE" | grep -o 'used [0-9]* bytes' | grep -o '[0-9]*')"
TOTAL_BYTES="$(echo "$RAM_LINE" | grep -o 'from [0-9]* bytes' | grep -o '[0-9]*')"

if [ -z "$USED_BYTES" ] || [ -z "$TOTAL_BYTES" ]; then
    echo "[check_uno_ram] ERROR: could not parse used/total bytes from RAM line."
    echo "  RAM line was: $RAM_LINE"
    exit 2
fi

FREE_BYTES=$(( TOTAL_BYTES - USED_BYTES ))

echo "[check_uno_ram] RAM: used=${USED_BYTES} B, total=${TOTAL_BYTES} B, free=${FREE_BYTES} B"
echo "[check_uno_ram] Floor: ${RAM_FLOOR} B"

if [ "$FREE_BYTES" -lt "$RAM_FLOOR" ]; then
    echo "[check_uno_ram] FAIL: free RAM ${FREE_BYTES} B < floor ${RAM_FLOOR} B"
    echo "[check_uno_ram] The COBS streaming encoder/decoder must not materialize a second ~512 B buffer."
    echo "[check_uno_ram] Investigate any new static allocation added since the Phase-49 baseline."
    exit 1
fi

echo "[check_uno_ram] PASS: free RAM ${FREE_BYTES} B >= floor ${RAM_FLOOR} B"
exit 0
