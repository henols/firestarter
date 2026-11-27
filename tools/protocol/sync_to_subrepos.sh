#!/usr/bin/env bash
#
# Firestarter protocol sync: the command frame and the 27C EPROM rows.
#
# Generation happens HERE, in the meta repo, and nowhere else. This script
# regenerates the command-frame layout, the golden vectors and the EPROM
# write-time rows, and writes them into the sub-repos. The sub-repos receive
# generated ARTIFACTS only and never regenerate for themselves.
#
# Authoritative sources: tools/protocol/{command_frame.toml,codegen.py}
#                        tools/protocol/{eprom_rows.toml,eprom_rows.py}
# Firmware artifacts:    firestarter_fw/include/command_frame.h
#                        firestarter_fw/test/native/avr/test_command_decode/command_vectors.h
#                        firestarter_fw/include/eprom_rows.h
# Host artifacts:        firestarter_app/firestarter/command_frame.py
#                        firestarter_app/tests/golden/command_vectors.json
#                        firestarter_app/firestarter/eprom_rows.py
#
# Idempotent: re-running with no upstream change is a no-op.
#
#   sync_to_subrepos.sh            write the artifacts into both sub-repos
#   sync_to_subrepos.sh --verify   write nothing; exit 1 if either sub-repo's
#                                  artifacts differ from what the spec gives
#
# Requirements: bash, python3, diff; ruff for the host module.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FS_ROOT="$SCRIPT_DIR/../../firestarter_fw"
FA_ROOT="$SCRIPT_DIR/../../firestarter_app"
GEN_FRAME=(python3 "$SCRIPT_DIR/codegen.py" --spec "$SCRIPT_DIR/command_frame.toml")
GEN_ROWS=(python3 "$SCRIPT_DIR/eprom_rows.py" --spec "$SCRIPT_DIR/eprom_rows.toml")

VERIFY=0
if [[ "${1:-}" == "--verify" ]]; then
    VERIFY=1
fi

"${GEN_FRAME[@]}" --check
"${GEN_ROWS[@]}" --check

# Each artifact, as "<generator> <language> <path relative to FS_ROOT or FA_ROOT>".
ARTIFACTS=(
    "frame cpp fw:include/command_frame.h"
    "frame cpp-vectors fw:test/native/avr/test_command_decode/command_vectors.h"
    "frame python app:firestarter/command_frame.py"
    "frame json-vectors app:tests/golden/command_vectors.json"
    "rows cpp fw:include/eprom_rows.h"
    "rows python app:firestarter/eprom_rows.py"
)

resolve() {
    case "$1" in
        fw:*) echo "$FS_ROOT/${1#fw:}" ;;
        app:*) echo "$FA_ROOT/${1#app:}" ;;
    esac
}

out_dir="$(mktemp -d)"
trap 'rm -rf "$out_dir"' EXIT

drift=0
for entry in "${ARTIFACTS[@]}"; do
    read -r generator language rel <<<"$entry"
    generated="$out_dir/$(basename "${rel#*:}")"
    if [[ "$generator" == "rows" ]]; then
        "${GEN_ROWS[@]}" --language "$language" --target "$generated"
    else
        "${GEN_FRAME[@]}" --language "$language" --target "$generated"
    fi
    if [[ "$language" == "python" ]]; then
        if command -v ruff >/dev/null 2>&1; then
            # Format from inside the app repo so its ruff config applies.
            (cd "$FA_ROOT" && ruff format -q "$generated")
        else
            echo "WARNING: ruff not found -- $(basename "$generated") is not normalized." >&2
        fi
    fi
    target="$(resolve "$rel")"
    if [[ "$VERIFY" == 1 ]]; then
        if ! diff -q "$generated" "$target" >/dev/null 2>&1; then
            echo "DRIFT: ${rel/:/ } differs from its spec in tools/protocol/" >&2
            drift=1
        fi
    else
        mkdir -p "$(dirname "$target")"
        cp "$generated" "$target"
    fi
done

if [[ "$VERIFY" == 1 ]]; then
    if [[ "$drift" == 1 ]]; then
        echo "Run tools/protocol/sync_to_subrepos.sh, then commit in each sub-repo." >&2
        exit 1
    fi
    echo "OK: both sub-repos carry the command frame and EPROM rows the specs give."
    exit 0
fi

echo "OK: command frame and EPROM rows synced to both sub-repos."
