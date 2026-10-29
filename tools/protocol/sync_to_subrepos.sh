#!/usr/bin/env bash
#
# Firestarter command-frame sync.
#
# Generation happens HERE, in the meta repo, and nowhere else. This script
# regenerates the command-frame layout and the golden vectors from
# command_frame.toml and writes them into the sub-repos. The sub-repos
# receive generated ARTIFACTS only and never regenerate for themselves.
#
# Authoritative source: tools/protocol/{command_frame.toml,codegen.py}
# Firmware artifacts:   firestarter_fw/include/command_frame.h
#                       firestarter_fw/test/native/avr/test_command_decode/command_vectors.h
# Host artifacts:       firestarter_app/firestarter/command_frame.py
#                       firestarter_app/tests/golden/command_vectors.json
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
GEN=(python3 "$SCRIPT_DIR/codegen.py" --spec "$SCRIPT_DIR/command_frame.toml")

VERIFY=0
if [[ "${1:-}" == "--verify" ]]; then
    VERIFY=1
fi

"${GEN[@]}" --check

# Each artifact, as "<language> <path relative to FS_ROOT or FA_ROOT>".
ARTIFACTS=(
    "cpp fw:include/command_frame.h"
    "cpp-vectors fw:test/native/avr/test_command_decode/command_vectors.h"
    "python app:firestarter/command_frame.py"
    "json-vectors app:tests/golden/command_vectors.json"
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
    language="${entry%% *}"
    rel="${entry#* }"
    generated="$out_dir/$(basename "${rel#*:}")"
    "${GEN[@]}" --language "$language" --target "$generated"
    if [[ "$language" == "python" ]]; then
        if command -v ruff >/dev/null 2>&1; then
            # Format from inside the app repo so its ruff config applies.
            (cd "$FA_ROOT" && ruff format -q "$generated")
        else
            echo "WARNING: ruff not found -- command_frame.py is not normalized." >&2
        fi
    fi
    target="$(resolve "$rel")"
    if [[ "$VERIFY" == 1 ]]; then
        if ! diff -q "$generated" "$target" >/dev/null 2>&1; then
            echo "DRIFT: ${rel/:/ } differs from command_frame.toml" >&2
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
    echo "OK: both sub-repos carry the command frame command_frame.toml gives."
    exit 0
fi

echo "OK: command frame synced to both sub-repos."
