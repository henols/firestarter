#!/usr/bin/env bash
# v1.8-archive.sh
#
# Milestone close cleanup: move v1.8 phase directories (36-* through 43-*) to
# .planning/milestones/v1.8-phases/ as the final milestone close step.
#
# Run AFTER all 6 HUMAN-UAT tests pass and the verifier script exits 0.
# Mirrors the v1.6 cleanup pattern documented in .planning/milestones/v1.6-phases/30-documentation-milestone-close/30-02-PLAN.md (v1.4/v1.5/v1.6/v1.7 archive pattern).
#
# Usage:
#   bash .planning/milestones/v1.8-archive.sh [--dry-run]
#
#   --dry-run  Print the planned mv commands without executing them. Exits 0.
#              Use this to preview what will be moved before committing.
#
# Exit codes:
#   0  Success (moves completed, or dry-run preview printed, or nothing to do).
#   1  Pre-flight error (destination non-empty, or expected source dirs missing).
#   2  Bad usage (unrecognized argument).
#
# Idempotence: if .planning/milestones/v1.8-phases/ already contains the target
# directories, this script aborts with a clear message rather than overwriting or
# merging. Run with --dry-run first if unsure.
#
# Safety: source directories are enumerated EXPLICITLY per phase number (not via a
# single wide glob like 3[6-9]-* 4[0-3]-* or phases/* which could accidentally capture paused v1.3
# phase dirs, milestone dirs, or future phases beyond 43). Per T-43-12 mitigation.

set -euo pipefail

# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------
usage() {
    cat >&2 <<EOF
Usage: bash .planning/milestones/v1.8-archive.sh [--dry-run]

  --dry-run  Preview the mv commands without executing them.

Exit codes: 0=success/dry-run, 1=pre-flight error, 2=bad usage
EOF
    exit 2
}

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
DRY_RUN=0

for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=1 ;;
        *)
            echo "ERROR: unrecognized argument: $arg" >&2
            usage
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Path computation
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# This script lives in .planning/ -- parent is meta-repo root.
META_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PHASES_DIR="$META_ROOT/.planning/phases"
DEST="$META_ROOT/.planning/milestones/v1.8-phases"

# Explicit per-phase glob enumeration -- NOT a single "3[6-9]-* 4[0-3]-*" glob.
# Each array entry expands to zero or more directories at pre-flight time.
# T-43-12 mitigation: explicit enumeration prevents accidental capture of
# paused v1.3 phases (11-*, 12-*) or future phases (44+, from v1.9).
PHASE_GLOBS=(
    "$PHASES_DIR/36-"*
    "$PHASES_DIR/37-"*
    "$PHASES_DIR/38-"*
    "$PHASES_DIR/39-"*
    "$PHASES_DIR/40-"*
    "$PHASES_DIR/41-"*
    "$PHASES_DIR/42-"*
    "$PHASES_DIR/43-"*
)

# Collect the directories that actually exist (filter out unexpanded glob tokens).
SRC_DIRS=()
for entry in "${PHASE_GLOBS[@]}"; do
    if [ -d "$entry" ]; then
        SRC_DIRS+=("$entry")
    fi
done

# ---------------------------------------------------------------------------
# Pre-flight: at least one source directory must exist
# ---------------------------------------------------------------------------
if [ "${#SRC_DIRS[@]}" -eq 0 ]; then
    echo "ERROR: No phase directories matching 36-* through 43-* found under $PHASES_DIR." >&2
    echo "       Have they already been archived? Check: $DEST" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Pre-flight: destination must not already be non-empty
# ---------------------------------------------------------------------------
if [ -d "$DEST" ] && [ -n "$(ls -A "$DEST" 2>/dev/null)" ]; then
    echo "ERROR: Destination already exists and is non-empty -- refusing to overwrite." >&2
    echo "       Inspect: $DEST" >&2
    echo "       If a previous archive run completed, there is nothing to do." >&2
    echo "       If you want to re-archive, manually empty $DEST first." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Dry-run: preview without executing
# ---------------------------------------------------------------------------
if [ "$DRY_RUN" -eq 1 ]; then
    echo "[dry-run] mkdir -p $DEST"
    for d in "${SRC_DIRS[@]}"; do
        echo "[dry-run] mv $d $DEST/"
    done
    echo ""
    echo "[dry-run] No changes made. ${#SRC_DIRS[@]} phase director(ies) would be archived."
    exit 0
fi

# ---------------------------------------------------------------------------
# Live run: create destination and move each phase directory
# ---------------------------------------------------------------------------
mkdir -p "$DEST"

MOVED=0
for d in "${SRC_DIRS[@]}"; do
    basename_d="$(basename "$d")"
    mv "$d" "$DEST/"
    echo "moved: $basename_d"
    MOVED=$((MOVED + 1))
done

echo ""
echo "Archived $MOVED phase director(ies) to .planning/milestones/v1.8-phases/"
echo ""
echo "Next steps:"
echo "  1. Commit the directory move (along with ROADMAP collapse + new v1.8-REQUIREMENTS.md from Subtasks 2C + 2D):"
echo "       git add -A .planning/phases .planning/milestones/v1.8-phases/ .planning/ROADMAP.md .planning/milestones/v1.8-REQUIREMENTS.md .planning/milestones/v1.8-archive.sh"
echo "       git commit -m 'chore(43-02): archive v1.8 phase directories + collapse ROADMAP + create REQUIREMENTS archive (DOC-02)'"
echo "  2. Verify Plan 43-01 ship-state flips landed (MILESTONES.md v1.8 entry + PROJECT.md ship line + README + CLAUDE.md Architecture)."
echo "  3. Proceed to Plan 43-03 (operator-authorized HUMAN-UAT: real-hardware GATE-1.8a witness + sub-repo + meta-repo branch promotion)."
exit 0
