#!/usr/bin/env bash
#
# Firestarter v1.2 catalog sync.
#
# Generation happens HERE, in the meta repo, and nowhere else. This script
# regenerates messages.h (firmware) and messages.py (host) from the canonical
# catalog and writes them into the sub-repos. The sub-repos receive generated
# ARTIFACTS only -- they do not carry codegen.py or messages.toml, and must
# never regenerate for themselves.
#
# Authoritative source: tools/catalog/{messages.toml,codegen.py}
# Generated firmware artifact: firestarter/include/messages.h
# Generated host artifact:     firestarter_app/firestarter/messages.py
#
# Idempotent: re-running with no upstream change is a no-op.
# Run after every catalog or codegen edit.
#
# Requirements: bash, cp, diff, python3, mktemp; ruff for the host artifact.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
META_REPO_CATALOG="$SCRIPT_DIR"
FS_ROOT="$META_REPO_CATALOG/../../firestarter"
FA_ROOT="$META_REPO_CATALOG/../../firestarter_app"

for f in messages.toml codegen.py; do
    if [[ ! -f "$META_REPO_CATALOG/$f" ]]; then
        echo "ERROR: canonical source missing: $META_REPO_CATALOG/$f" >&2
        exit 1
    fi
done

# ---------------------------------------------------------------------------
# Firmware artifact: firestarter/include/messages.h
# ---------------------------------------------------------------------------
echo "Regenerating firestarter/include/messages.h ..."
tmp_h="$(mktemp)"
trap 'rm -f "$tmp_h" "${tmp_py:-}"' EXIT
python3 "$META_REPO_CATALOG/codegen.py" \
    --catalog "$META_REPO_CATALOG/messages.toml" \
    --language cpp \
    --target "$tmp_h"
cp "$tmp_h" "$FS_ROOT/include/messages.h"

if diff -q "$tmp_h" "$FS_ROOT/include/messages.h" >/dev/null 2>&1; then
    echo "  OK: firestarter/include/messages.h regenerated."
else
    echo "ERROR: regenerated messages.h did not land at $FS_ROOT/include/messages.h" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Host artifact: firestarter_app/firestarter/messages.py
#
# The committed file is ruff-normalized like all host source, so the raw
# codegen text is normalized here before landing. Skipping this step is what
# makes a later `git diff` report drift that is purely formatting.
# ---------------------------------------------------------------------------
echo "Regenerating firestarter_app/firestarter/messages.py ..."
tmp_py="$(mktemp)"
python3 "$META_REPO_CATALOG/codegen.py" \
    --catalog "$META_REPO_CATALOG/messages.toml" \
    --language python \
    --target "$tmp_py"
cp "$tmp_py" "$FA_ROOT/firestarter/messages.py"

if command -v ruff >/dev/null 2>&1; then
    (cd "$FA_ROOT" && ruff format -q firestarter/messages.py && ruff check -q --add-noqa firestarter/messages.py)
    echo "  OK: firestarter_app/firestarter/messages.py regenerated and ruff-normalized."
else
    echo "WARNING: ruff not found -- messages.py written WITHOUT normalization." >&2
    echo "         Install ruff and re-run, or the committed file will show formatting drift." >&2
fi

echo "OK: catalog synced to both sub-repos."
