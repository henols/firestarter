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
# Requirements: bash, python3; ruff for the host module.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FS_ROOT="$SCRIPT_DIR/../../firestarter_fw"
FA_ROOT="$SCRIPT_DIR/../../firestarter_app"
GEN=(python3 "$SCRIPT_DIR/codegen.py" --spec "$SCRIPT_DIR/command_frame.toml")

"${GEN[@]}" --check

mkdir -p "$FS_ROOT/test/native/avr/test_command_decode" "$FA_ROOT/tests/golden"
"${GEN[@]}" --language cpp --target "$FS_ROOT/include/command_frame.h"
"${GEN[@]}" --language cpp-vectors --target "$FS_ROOT/test/native/avr/test_command_decode/command_vectors.h"
"${GEN[@]}" --language python --target "$FA_ROOT/firestarter/command_frame.py"
"${GEN[@]}" --language json-vectors --target "$FA_ROOT/tests/golden/command_vectors.json"

if command -v ruff >/dev/null 2>&1; then
    (cd "$FA_ROOT" && ruff format -q firestarter/command_frame.py)
else
    echo "WARNING: ruff not found -- command_frame.py written WITHOUT normalization." >&2
fi

echo "OK: command frame synced to both sub-repos."
