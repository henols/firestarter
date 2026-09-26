#!/usr/bin/env python3
"""136.1-01 blast-radius proof: chip_database.json's PROV-01 regeneration is additive-only.

Compares a PRE-regen snapshot of chip_database.json (by default, the committed file as it
stood one commit before this plan's regeneration commit) against the POST-regen file (by
default, the working tree's current file) and mechanically asserts:

  1. Same set of manufacturers; for each, the same chip list LENGTH and the same
     part_number sequence, in the same order (T-136.1-02: no chip added, removed, or
     reordered).
  2. For every chip entry, every top-level key OTHER than "programming" is byte-identical
     between PRE and POST (== equality on the parsed JSON value).
  3. Within "programming", every PRE-existing key/value is byte-identical, and the ONLY
     new keys POST may carry are a subset of {protect_off_before, protect_on_after,
     infoic_page_size_raw}.
  4. The two tools/extra_chips.json supplement entries (TEXAS INSTRUMENTS 2516/2532) do
     NOT carry any of the three new keys in POST -- they bypass build_db.py's per-<ic>
     decode loop entirely (VAR-05 / D-10 post-decode merge), so this absence is the
     expected, correct shape, not a gap.

Exits 0 and prints a summary on a clean additive-only diff. Exits non-zero, naming the
first offending entry, on ANY violation -- this script's own non-vacuity obligation
(Nyquist #1 in 136.1-VALIDATION.md) is that it must be capable of failing, not merely of
passing.

Both comparison targets are overridable via env vars so this script stays re-runnable
later as a standing regression proof, not a one-shot with hardcoded temp paths:

  PRE_DB_REF    -- git ref to read the PRE-regen file from (default: HEAD~1)
  PRE_DB_PATH   -- if set, read PRE directly from this file path instead of `git show`
  POST_DB_PATH  -- path to the POST-regen file (default: the working tree's
                   firestarter/data/chip_database.json)
  SUBMODULE_DIR -- the firestarter_app git checkout `git show` runs against
                   (default: /workspaces/firestarter_app)
"""

import json
import os
import subprocess
import sys

_NEW_KEYS = {"protect_off_before", "protect_on_after", "infoic_page_size_raw"}
_SUPPLEMENT_PARTS = {"2516", "2532"}  # TEXAS INSTRUMENTS, tools/extra_chips.json
_SUBMODULE_DIR = os.environ.get("SUBMODULE_DIR", "/workspaces/firestarter_app")
_DEFAULT_POST_PATH = os.path.join(
    _SUBMODULE_DIR, "firestarter", "data", "chip_database.json"
)


def _load_pre() -> dict:
    pre_path = os.environ.get("PRE_DB_PATH")
    if pre_path:
        with open(pre_path) as f:
            return json.load(f)
    pre_ref = os.environ.get("PRE_DB_REF", "HEAD~1")
    result = subprocess.run(
        ["git", "-C", _SUBMODULE_DIR, "show", f"{pre_ref}:firestarter/data/chip_database.json"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def _load_post() -> dict:
    post_path = os.environ.get("POST_DB_PATH", _DEFAULT_POST_PATH)
    with open(post_path) as f:
        return json.load(f)


def main() -> int:
    pre = _load_pre()
    post = _load_post()

    violations: list[str] = []
    entries_compared = 0
    entries_gained_keys = 0
    supplement_seen: dict[str, bool] = {p: False for p in _SUPPLEMENT_PARTS}

    pre_mfrs = set(pre.keys())
    post_mfrs = set(post.keys())
    if pre_mfrs != post_mfrs:
        added = post_mfrs - pre_mfrs
        removed = pre_mfrs - post_mfrs
        violations.append(
            f"MANUFACTURER SET CHANGED: added={sorted(added)} removed={sorted(removed)}"
        )

    for mfr in sorted(pre_mfrs & post_mfrs):
        pre_list = pre[mfr]
        post_list = post[mfr]
        if not isinstance(pre_list, list) or not isinstance(post_list, list):
            continue

        if len(pre_list) != len(post_list):
            violations.append(
                f"{mfr}: chip-list length changed {len(pre_list)} -> {len(post_list)}"
            )
            continue

        pre_names = [c.get("part_number") for c in pre_list]
        post_names = [c.get("part_number") for c in post_list]
        if pre_names != post_names:
            violations.append(
                f"{mfr}: part_number sequence changed (order or identity) -- "
                f"first divergence at index "
                f"{next((i for i, (a, b) in enumerate(zip(pre_names, post_names)) if a != b), '?')}"
            )
            continue

        for pre_entry, post_entry in zip(pre_list, post_list):
            entries_compared += 1
            part_number = post_entry.get("part_number", "<unknown>")

            for key in pre_entry:
                if key == "programming":
                    continue
                if key not in post_entry:
                    violations.append(f"{mfr}/{part_number}: top-level key '{key}' MISSING post-regen")
                    continue
                if pre_entry[key] != post_entry[key]:
                    violations.append(
                        f"{mfr}/{part_number}: top-level key '{key}' CHANGED "
                        f"{pre_entry[key]!r} -> {post_entry[key]!r}"
                    )
            for key in post_entry:
                if key == "programming":
                    continue
                if key not in pre_entry:
                    violations.append(f"{mfr}/{part_number}: NEW top-level key '{key}' (only 'programming' may gain keys)")

            pre_prog = pre_entry.get("programming", {})
            post_prog = post_entry.get("programming", {})

            for key in pre_prog:
                if key not in post_prog:
                    violations.append(
                        f"{mfr}/{part_number}: programming.'{key}' MISSING post-regen"
                    )
                    continue
                if pre_prog[key] != post_prog[key]:
                    violations.append(
                        f"{mfr}/{part_number}: programming.'{key}' CHANGED "
                        f"{pre_prog[key]!r} -> {post_prog[key]!r}"
                    )

            new_keys_here = set(post_prog) - set(pre_prog)
            if new_keys_here:
                if not new_keys_here.issubset(_NEW_KEYS):
                    violations.append(
                        f"{mfr}/{part_number}: unexpected new programming key(s) "
                        f"{sorted(new_keys_here - _NEW_KEYS)} (only {sorted(_NEW_KEYS)} permitted)"
                    )
                else:
                    entries_gained_keys += 1

            # Supplement-entry check: these two carry algorithm 11 and MUST NOT
            # gain any of the three new keys (they bypass the decode loop).
            for supplement_part in _SUPPLEMENT_PARTS:
                if part_number == supplement_part:
                    supplement_seen[supplement_part] = True
                    leaked = new_keys_here & _NEW_KEYS
                    if leaked:
                        violations.append(
                            f"{mfr}/{part_number}: SUPPLEMENT entry gained decode key(s) "
                            f"{sorted(leaked)} -- extra_chips.json entries must never carry these"
                        )

    for part_number, seen in supplement_seen.items():
        if not seen:
            violations.append(
                f"SUPPLEMENT entry '{part_number}' (TEXAS INSTRUMENTS) not found in POST -- "
                "expected present (VAR-05 supplement), cannot confirm it lacks the new keys"
            )

    print("=" * 78)
    print("136.1-01 BLAST-RADIUS PROOF -- chip_database.json regeneration, additive-only")
    print("=" * 78)
    print(f"Total chip entries compared:        {entries_compared}")
    print(f"Entries that gained new key(s):      {entries_gained_keys}")
    print(
        "Supplement entries (TEXAS INSTRUMENTS 2516/2532) confirmed present, "
        f"WITHOUT new keys: {sorted(p for p, seen in supplement_seen.items() if seen)}"
    )
    print()

    if violations:
        print(f"VIOLATIONS: {len(violations)}")
        for v in violations:
            print(f"  - {v}")
        print()
        print("RESULT: FAIL -- diff is NOT additive-only. Do not force this through.")
        return 1

    print("VIOLATIONS: 0")
    print("RESULT: PASS -- diff is additive-only (only the three named keys added).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
