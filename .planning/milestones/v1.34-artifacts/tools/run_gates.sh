#!/usr/bin/env bash
#
# run_gates.sh -- the full host-side gate suite for Phase 160 (RIG-01..05), and the
# per-wave-merge gate for Phases 161-166.
#
# WHAT THIS RUNS
# ---------------
#   1. Discovery: every *.py under .planning/milestones/v1.34-artifacts/tools/, asserting each one advertises a
#      --selftest mode, then running it. A tool that does not advertise --selftest is a
#      FAILURE of this suite, never a silent skip -- that is what keeps the discovery
#      honest as later phases add tools.
#   2. Live gates (skipped entirely under --quick, see below):
#        a. check_rebuild.py   -- committed images/ self-check against SHA256SUMS.txt
#        b. check_arms.py      -- both live host arms against the recorded config-dir SHA
#        c. render_steps.py    -- the SC#3 empty-step-list diff (--arm control vs --arm v133),
#                                  now covering BOTH sections (--section P and --section C,
#                                  Phase 162 Plan 04) inside this one gate -- not an eighth gate
#        d. render_evidence.py --check -- bench/EVIDENCE.md against a fresh render
#        e. gate_record.py     -- bench/EVIDENCE.jsonl's own record-shape gate
#        f. render_chip_evidence.py --check -- bench/CHIP-EVIDENCE.md against a fresh render
#        g. gate_record.py (CHIP-EVIDENCE.jsonl) -- bench/CHIP-EVIDENCE.jsonl's own record-shape gate
#
# FAILURE STYLE
# --------------
# Accumulate-then-report: every gate runs regardless of an earlier gate's failure, a
# summary lists every failed gate by name at the end, and the script exits 1 if one or
# more failed. This differs from .planning/milestones/v1.7-artifacts/phase-33-baseline-hex/check-migration.sh's
# bail-on-first-assertion style -- stated here because the two in-repo precedents differ
# and a reader should not have to infer which one this script follows.
#
# WHAT THIS SUITE CANNOT AUTOMATE
# ---------------------------------
# Two falsification tests cannot be automated by this script and are phase-gate items
# verified elsewhere instead, because both require either a physical board or a party
# with no session memory:
#   - The deliberate wrong-arm cross-flash on all three targets (D-03) -- requires a real
#     board's independent read-back to disagree with the wrong hex. Verified live on the
#     bench in plans 08-10.
#   - The fresh-context record reconstruction (RIG-05's actual claim, "a cell can be
#     re-run from the written record alone") -- requires an agent with no memory of how
#     the record was produced. Verified in plan 13.
# A green run of this script is proof the SUBSTRATE is sound; it is not proof the PHASE is
# done -- that is exactly the gap Phase 160's earlier gate-suite mistake (a suite that
# discovered nothing and exited 0) taught this project to name explicitly rather than
# leave implicit.
#
# --quick
# -------
# Skips ONLY the live gates that need the two host arms or the committed images
# (check_rebuild.py and check_arms.py). Every tool's --selftest still runs in full, and
# render_steps.py / render_evidence.py --check / gate_record.py still run (none of the
# three touches an arm binary or an image file). A --quick green is NOT a full green --
# it never asserts the arms are still correctly pinned or the images still match their
# manifest.
#
# Exit codes
# ----------
#   0  all gates passed (or were skipped under --quick)
#   1  one or more gates failed
#   2  bad usage, or discovery found zero tools / the tools directory does not exist
#
# Usage: bash .planning/milestones/v1.34-artifacts/tools/run_gates.sh [--quick]

set -euo pipefail

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
QUICK=0
for arg in "$@"; do
    case "$arg" in
        --quick) QUICK=1 ;;
        *)
            echo "ERROR: unrecognized argument: $arg" >&2
            echo "Usage: bash $0 [--quick]" >&2
            exit 2
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Path resolution -- independent of caller's cwd
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="$SCRIPT_DIR"
MILESTONE_DIR="$(dirname "$TOOLS_DIR")"
BENCH_DIR="$MILESTONE_DIR/bench"
PINS_FILE="$MILESTONE_DIR/rig-pins.json"
PROVENANCE_FILE="$MILESTONE_DIR/arms-provenance.json"
PROCEDURE_FILE="$MILESTONE_DIR/PROCEDURE.md"

FAILURES=()
SELFTEST_COUNT=0

# ---------------------------------------------------------------------------
# Fail-closed discovery
# ---------------------------------------------------------------------------
if [ ! -d "$TOOLS_DIR" ]; then
    echo "FAIL: tools directory does not exist: $TOOLS_DIR" >&2
    exit 2
fi

PY_TOOLS=()
while IFS= read -r -d '' f; do
    PY_TOOLS+=("$f")
done < <(find "$TOOLS_DIR" -maxdepth 1 -name '*.py' -print0 | sort -z)

if [ "${#PY_TOOLS[@]}" -eq 0 ]; then
    echo "FAIL: discovery found zero *.py files under $TOOLS_DIR -- a suite that finds nothing must fail, not pass" >&2
    exit 2
fi

echo "===== run_gates.sh: discovered ${#PY_TOOLS[@]} tool(s) under $TOOLS_DIR ====="

# ---------------------------------------------------------------------------
# Step 1 -- every tool's --selftest (always runs, even under --quick)
# ---------------------------------------------------------------------------
for tool in "${PY_TOOLS[@]}"; do
    name="$(basename "$tool")"
    if ! grep -q -- '"--selftest"' "$tool"; then
        echo "FAIL: $name does not advertise a --selftest mode" >&2
        FAILURES+=("$name: does not advertise a --selftest mode")
        continue
    fi
    echo "--- selftest: $name ---"
    if python3 "$tool" --selftest; then
        SELFTEST_COUNT=$((SELFTEST_COUNT + 1))
        echo "selftest PASS: $name"
    else
        FAILURES+=("$name: --selftest exited non-zero")
        echo "selftest FAIL: $name" >&2
    fi
done

# ---------------------------------------------------------------------------
# Step 2 -- live gates (skipped under --quick)
# ---------------------------------------------------------------------------
if [ "$QUICK" -eq 1 ]; then
    echo "===== --quick: skipping check_rebuild.py (needs committed images) and check_arms.py (needs the two live host arms) ====="
else
    echo "--- live gate: check_rebuild.py (committed images self-check) ---"
    if python3 "$TOOLS_DIR/check_rebuild.py"; then
        echo "live gate PASS: check_rebuild.py"
    else
        FAILURES+=("check_rebuild.py: images/ self-check against SHA256SUMS.txt failed")
        echo "live gate FAIL: check_rebuild.py" >&2
    fi

    echo "--- live gate: check_arms.py (both live host arms) ---"
    EXPECT_CONFIG_SHA=""
    if [ -f "$PROVENANCE_FILE" ]; then
        EXPECT_CONFIG_SHA="$(python3 -c "
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    print(d.get('config_dir_sha', ''))
except Exception:
    print('')
" "$PROVENANCE_FILE")"
    fi
    if [ -n "$EXPECT_CONFIG_SHA" ]; then
        CHECK_ARMS_ARGS=(--pins "$PINS_FILE" --expect-config-sha "$EXPECT_CONFIG_SHA")
    else
        CHECK_ARMS_ARGS=(--pins "$PINS_FILE")
    fi
    if python3 "$TOOLS_DIR/check_arms.py" "${CHECK_ARMS_ARGS[@]}"; then
        echo "live gate PASS: check_arms.py"
    else
        FAILURES+=("check_arms.py: live arm verification failed")
        echo "live gate FAIL: check_arms.py" >&2
    fi
fi

echo "--- live gate: render_steps.py (SC#3 empty-step-list diff, control vs v133, sections P and C) ---"
# Amendment 4 / Phase 162 Plan 04: PROCEDURE.md gained a second, independent step-list section
# ('## Chip-sweep step list', ids C-01..C-09) alongside the original '## Step list' ('P-NN').
# This block now renders and diffs BOTH sections -- four renders total, control and v133 for
# each of P and C -- inside this ONE gate (PD-2: the suite target stays at 7 live gates, never
# an eighth). The three ordered conditions (non-zero exit, empty render, non-empty diff) are
# unchanged and are applied per section; every failure message names which section failed.
RENDER_STEPS_OK=1
RENDER_STEPS_SUMMARY=""
RENDER_STEPS_FAIL_MSGS=()
for SECTION in P C; do
    CONTROL_RENDER="$(mktemp)"
    V133_RENDER="$(mktemp)"
    CONTROL_RC=0
    V133_RC=0
    python3 "$TOOLS_DIR/render_steps.py" --arm control --procedure "$PROCEDURE_FILE" --section "$SECTION" > "$CONTROL_RENDER" || CONTROL_RC=$?
    python3 "$TOOLS_DIR/render_steps.py" --arm v133 --procedure "$PROCEDURE_FILE" --section "$SECTION" > "$V133_RENDER" || V133_RC=$?
    CONTROL_LINES="$(wc -l < "$CONTROL_RENDER")"
    V133_LINES="$(wc -l < "$V133_RENDER")"
    if [ "$CONTROL_RC" -ne 0 ] || [ "$V133_RC" -ne 0 ]; then
        RENDER_STEPS_OK=0
        RENDER_STEPS_FAIL_MSGS+=("section $SECTION exited non-zero (control_rc=$CONTROL_RC v133_rc=$V133_RC)")
        echo "live gate FAIL: render_steps.py -- section $SECTION exited non-zero (control_rc=$CONTROL_RC v133_rc=$V133_RC)" >&2
    elif [ "$CONTROL_LINES" -eq 0 ] || [ "$V133_LINES" -eq 0 ]; then
        RENDER_STEPS_OK=0
        RENDER_STEPS_FAIL_MSGS+=("section $SECTION: at least one arm's render was empty (control=$CONTROL_LINES v133=$V133_LINES lines)")
        echo "live gate FAIL: render_steps.py -- section $SECTION empty render (control=$CONTROL_LINES v133=$V133_LINES lines)" >&2
    elif diff -u "$CONTROL_RENDER" "$V133_RENDER" > /dev/null; then
        RENDER_STEPS_SUMMARY="${RENDER_STEPS_SUMMARY}section $SECTION: diff empty, control=$CONTROL_LINES v133=$V133_LINES lines; "
    else
        RENDER_STEPS_OK=0
        RENDER_STEPS_FAIL_MSGS+=("section $SECTION: control vs v133 render diff is non-empty")
        echo "live gate FAIL: render_steps.py -- section $SECTION non-empty diff:" >&2
        diff -u "$CONTROL_RENDER" "$V133_RENDER" >&2 || true
    fi
    rm -f "$CONTROL_RENDER" "$V133_RENDER"
done
if [ "$RENDER_STEPS_OK" -eq 1 ]; then
    echo "live gate PASS: render_steps.py -- ${RENDER_STEPS_SUMMARY}"
else
    FAILURES+=("render_steps.py: ${RENDER_STEPS_FAIL_MSGS[*]}")
fi

echo "--- live gate: render_evidence.py --check (bench/EVIDENCE.md vs a fresh render) ---"
if python3 "$TOOLS_DIR/render_evidence.py" --jsonl "$BENCH_DIR/EVIDENCE.jsonl" --target "$BENCH_DIR/EVIDENCE.md" --check; then
    echo "live gate PASS: render_evidence.py --check"
else
    FAILURES+=("render_evidence.py --check: bench/EVIDENCE.md diverges from a fresh render")
    echo "live gate FAIL: render_evidence.py --check" >&2
fi

echo "--- live gate: gate_record.py (bench/EVIDENCE.jsonl record-shape gate) ---"
if python3 "$TOOLS_DIR/gate_record.py" --jsonl "$BENCH_DIR/EVIDENCE.jsonl" --pins "$PINS_FILE"; then
    echo "live gate PASS: gate_record.py"
else
    FAILURES+=("gate_record.py: bench/EVIDENCE.jsonl failed its own record-shape gate")
    echo "live gate FAIL: gate_record.py" >&2
fi

echo "--- live gate: render_chip_evidence.py --check (bench/CHIP-EVIDENCE.md vs a fresh render) ---"
if python3 "$TOOLS_DIR/render_chip_evidence.py" --jsonl "$BENCH_DIR/CHIP-EVIDENCE.jsonl" --target "$BENCH_DIR/CHIP-EVIDENCE.md" --check; then
    echo "live gate PASS: render_chip_evidence.py --check"
else
    FAILURES+=("render_chip_evidence.py --check: bench/CHIP-EVIDENCE.md diverges from a fresh render -- hand-edit suspected")
    echo "live gate FAIL: render_chip_evidence.py --check" >&2
fi

echo "--- live gate: gate_record.py (bench/CHIP-EVIDENCE.jsonl record-shape gate) ---"
if python3 "$TOOLS_DIR/gate_record.py" --jsonl "$BENCH_DIR/CHIP-EVIDENCE.jsonl" --pins "$PINS_FILE"; then
    echo "live gate PASS: gate_record.py (CHIP-EVIDENCE.jsonl)"
else
    FAILURES+=("gate_record.py (CHIP-EVIDENCE.jsonl): bench/CHIP-EVIDENCE.jsonl failed its own record-shape gate")
    echo "live gate FAIL: gate_record.py (CHIP-EVIDENCE.jsonl)" >&2
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "===== run_gates.sh SUMMARY ====="
echo "  tool self-tests run: $SELFTEST_COUNT / ${#PY_TOOLS[@]}"
if [ "$QUICK" -eq 1 ]; then
    echo "  mode: --quick (check_rebuild.py and check_arms.py skipped)"
else
    echo "  mode: full"
fi

if [ "${#FAILURES[@]}" -eq 0 ]; then
    echo "ALL GATES PASSED"
    exit 0
else
    echo "FAILURES (${#FAILURES[@]}):" >&2
    for f in "${FAILURES[@]}"; do
        echo "  - $f" >&2
    done
    exit 1
fi
