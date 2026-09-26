#!/usr/bin/env python3
"""Assert that the infoic-xml-protection-flags-research.md note was edited
append-only: the committed (HEAD) version must be an exact prefix of the
current working-tree version. Used by Phase 120 plan 04, Task 3.
"""
import subprocess
import sys

NOTE = ".planning/notes/infoic-xml-protection-flags-research.md"

committed = subprocess.run(
    ["git", "show", f"HEAD:{NOTE}"],
    capture_output=True,
    text=True,
    check=True,
).stdout

with open(NOTE, encoding="utf-8") as f:
    working = f.read()

assert working.startswith(committed), (
    "Working-tree file is NOT a prefix of the committed (HEAD) file — "
    "an existing sentence was changed. Append-only violation."
)
assert len(working) > len(committed), (
    "Working-tree file is identical to HEAD — nothing was appended."
)

print("OK: append-only edit confirmed")
print(f"  committed length: {len(committed)}")
print(f"  working length:   {len(working)}")
print(f"  appended chars:   {len(working) - len(committed)}")
sys.exit(0)
