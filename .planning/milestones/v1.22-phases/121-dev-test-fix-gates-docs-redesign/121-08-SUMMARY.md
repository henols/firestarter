---
phase: 121-dev-test-fix-gates-docs-redesign
plan: 08
subsystem: testing
tags: [chip_test, database, dev-test, sdp, eeprom28c, ladder-state, DEVTEST-01]

# Dependency graph
requires:
  - phase: 121-06
    provides: OP_WRITE_PARTIAL vocabulary and _MULTI_RUN_OPS/_DESTRUCTIVE_OPS wiring that this plan's erase composition sits alongside
provides:
  - "FLAG_CAN_ERASE cleared for protocol 0x0D (algorithm 13) at the root, in database.py:convert_to_programmer"
  - "derive_plan's generic NA-erase else gains a 0x0D family-fact reason arm, naming the protocol and the 28C family's lack of an erase operation, never the flag"
  - "DEVTEST-01 closed: dev test's 0x0D sweep no longer dispatches a fabricated erase and no longer auto-tags an otherwise-passing chip community-fail"
affects: [121-09, 121-14]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Reversal record pattern (119 D-18, 120 D-20, now 121 D-12): when a policy changes but the underlying fact it was based on remains true, the in-source comment and the inverted test docstring both name the prior claim, the reversing decision id, the reason, and an explicit statement that the old fact was never wrong."

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/database.py
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_database_conversion.py
    - firestarter_app/tests/test_eprom_operations.py
    - firestarter_app/tests/test_chip_test.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "D-12 (from PLAN): root-cause fix at database.py's convert_to_programmer rather than a derive_plan-local 0x0D branch -- widened the existing algo != 5 exclusion to algo not in (5, 13)."
  - "The 0x0D NA-erase reason arm lives inside derive_plan's existing trailing else (alongside flash4/UV), not a new if can_erase branch, matching Pitfall 9's guidance and D-12's intent to route 0x0D through the generic path."
  - "Reason text names the family fact (protocol 0x0D, 28C family has no erase op, page write auto-erases internally) and never the FLAG_CAN_ERASE identifier -- asserted as a runtime substring-absence check, not a source grep."

requirements-completed: [DEVTEST-01]

coverage:
  - id: D1
    description: "Protocol 0x0D chips (all 84) convert with FLAG_CAN_ERASE cleared; 0x07 and 0x05 behaviour unchanged; diff_db.py identity intact"
    requirement: DEVTEST-01
    verification:
      - kind: unit
        ref: "tests/test_database_conversion.py::test_convert_at28c256_flash_eeprom_flag_can_erase_cleared"
        status: pass
      - kind: unit
        ref: "tests/test_database_conversion.py::test_non_5v_page_eeprom_still_has_flag_can_erase (0x07 scope check)"
        status: pass
      - kind: other
        ref: "python3 tools/diff_db.py -- PASS: all 2 changed chips explained (0 new, 0 removed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The NA erase step for a protocol-0x0D chip names the family fact and never the flag mechanism"
    requirement: DEVTEST-01
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_devtest01_0x0d_sweep_erase_is_na_and_erase_eprom_never_called"
        status: pass
    human_judgment: false
  - id: D3
    description: "A full-scope 0x0D sweep no longer dispatches a fabricated erase (operator.erase_eprom never called) and no longer auto-tags community-fail (ladder_state is community-reported)"
    requirement: DEVTEST-01
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_devtest01_0x0d_sweep_erase_is_na_and_erase_eprom_never_called"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_devtest01_0x0d_all_ok_sweep_no_longer_tags_community_fail"
        status: pass
    human_judgment: false
  - id: D4
    description: "Full test suite green at baseline+2, DB/dispatch/coverage/ruff gates all pass"
    verification:
      - kind: other
        ref: "python -m pytest tests/ --tb=short -- 1091 passed in ~48s"
        status: pass
      - kind: other
        ref: "python3 tools/check_dispatch.py -- PASS, 0 dispatch regressions"
        status: pass
      - kind: other
        ref: "ruff check/format --check firestarter/ tests/ -- All checks passed"
        status: pass
    human_judgment: false

# Metrics
duration: ~35min
completed: 2026-07-29
status: complete
---

# Phase 121 Plan 08: Root-Cause SDP Erase-Capability Fix + Family-Fact NA Reason Summary

**Cleared `FLAG_CAN_ERASE` for protocol `0x0D` at `database.py`'s source (D-12), which makes `derive_plan`'s existing generic NA-erase branch fire for free with a new family-fact reason arm — closing DEVTEST-01's host half: the `dev test` sweep no longer fabricates an erase against the 28C family or auto-tags a passing chip `community-fail`.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-07-29T19:08:01Z
- **Tasks:** 3/3
- **Files modified:** 6 (5 in `firestarter_app`, 1 in the meta repo)

## Accomplishments

- `convert_to_programmer`'s `simple_flags` exclusion widened from `algo != 5` to `algo not in (5, 13)`, clearing `FLAG_CAN_ERASE` for all 84 protocol-`0x0D` chips at the root.
- A recorded reversal (Phase 121 D-12, the third this phase after 119 D-18 / 120 D-20) replaces the prior D-03 note that leaving the flag set on `0x0D` was firmware-inert and must stay unchanged.
- `derive_plan` gained a `_PROTOCOL_EEPROM_28C = 0x0D` constant and a family-fact NA-erase reason arm inside its existing trailing `else`, naming protocol `0x0D` and the 28C family's total absence of an erase operation — never `FLAG_CAN_ERASE` by name.
- Two pinned host tests inverted with full reversal-record docstrings; two new sweep legs added proving `operator.erase_eprom` is never called and the resulting `ladder_state` is `community-reported`, not `community-fail`.
- `DEVTEST-01` ticked in `REQUIREMENTS.md` — both halves (firmware, Phase 119; host, this plan) now landed.

## Re-verification of the Blast Radius (recorded verbatim, per Task 1 requirement)

1. **No `chip_database.json` entry carries a `flags` key.** Distinct entry-key set across all 746 entries, enumerated live:
   `{'datasheet', 'electrical', 'part_number', 'pinout', 'programming', 'provenance', 'source', 'support_status', 'unsupported_reason', 'verification_note', 'verification_status'}`
   No `flags` key present — `diff_db.py` identity cannot break by this change.

2. **No firmware native test or `validation_matrix_spec.json` pins the incoming wire flags for `eeprom28c`.** Grepped `firestarter/test/native/avr/test_val_eeprom28c/` (no `flags`/`FLAG_CAN_ERASE` hits), `firestarter/test/native/avr/_shared/validation_matrix.h` (only hit: `{ 0x0D, "eeprom28c", "configure_eeprom28c" }` — a dispatch-family mapping, not a flags pin), and confirmed no `validation_matrix_spec.json` file exists anywhere in the firmware repo.

3. **`serial_comm.py`'s flag read is DEBUG-guarded.** `_log_command_details` reads `command_dict.get("flags", 0)` and every downstream flag-name append is entirely inside `if logger.isEnabledFor(logging.DEBUG):` — confirmed by reading the enclosing conditional (lines ~540-560).

4. **Exactly two host tests asserted the flag/wire value for a `0x0D` part**, confirmed by a repo-wide grep for `flags == 2`, `flags & FLAG_CAN_ERASE`, `"flags": 2`, etc.:
   - `tests/test_database_conversion.py::test_convert_at28c256_flash_eeprom_flag_can_erase` (now inverted/renamed)
   - `tests/test_eprom_operations.py::test_sdp_command_flags_carry_the_db_can_erase_bit` (now inverted/renamed)
   `tests/test_val_wire_5v_page.py`'s pins are `W29C040` (`0x05`) and `W27C512` (`0x07`) — confirmed by reading the file, never `0x0D`. Status after all commits: `git status --porcelain tests/test_val_wire_5v_page.py` is empty.

## Verification Counts

- **All 84 protocol-`0x0D` chips** enumerated live against `chip_database.json` and confirmed to convert with the erase-capability bit clear (0 carrying the bit).
- `W27C512` (protocol `0x07`) still converts with the bit **set** (`flags == 2`).
- `W29C040` (protocol `0x05`) still converts with the bit **clear** (`flags == 0`) — the pre-existing exclusion is intact.
- `python3 tools/diff_db.py` → `PASS: all 2 changed chips explained (0 new chips confirmed; 0 chips removed from baseline)`, exit 0. (Identity here means "still exactly 2 explained changes" — the pre-existing PGSZ page-size changes — not zero.)
- `git -C /workspaces/firestarter_app status --porcelain firestarter/data/chip_database.json firestarter/constants.py` — empty, both commits.

## The Rewritten Comment Block (quoted in full, `database.py` around line 570)

```
        # Calculate the simple 'flags' key for the programmer.
        # Canonical erase-capability ground truth (D-01/D-02): set FLAG_CAN_ERASE
        # directly from electrical.type ∈ {"EEPROM","Flash/EEPROM"} rather than the
        # fragile synthetic `info-flags & 0x10` round-trip injected by _map_data.
        # This reads the same canonical field _map_data keys off (line ~434), so the
        # derivation cannot silently drift under a future _map_data refactor. A missing
        # key degrades safely to flag-clear (A1), identical to the old path. RF-01:
        # zero behavioral delta for all chips (the synthetic path already matched).
        #
        # Scope (Phase 121 D-12): algorithms 5 and 13 are excluded from the flag.
        #
        # Algorithm 5 (flash4) — FIX-01a / T-93-CANERASE: flash4 auto-erases per
        # page during the page-write; no separate 12V bulk erase is needed or
        # safe. Setting FLAG_CAN_ERASE for 0x05 routes firmware
        # flash4_write_init → flash4_erase_execute which asserts
        # CTRL_VPP_REGULATOR_ENABLE on a 5V-only chip (12V on a 5V part —
        # hardware-damage hazard). Scope: algorithm==5 only; the 0x07 and
        # 0x0D paths are unaffected by this particular exclusion.
        #
        # Algorithm 13 / protocol 0x0D (AT28C / 28C-family SDP EEPROMs) —
        # Phase 121 D-12: the firmware's configure_eeprom28c handler
        # (firestarter/src/proms/eeprom_28c.cpp) has no erase operation at
        # all, so advertising FLAG_CAN_ERASE for these 84 chips is a false
        # capability statement. DEVTEST-01's `dev test` sweep reads that
        # advertisement and plans a real erase step that reports OK having
        # done nothing, auto-tagging otherwise-passing runs `community-fail`.
        #
        # REVERSAL RECORD (Phase 121 D-12, third recorded reversal this
        # phase after 119 D-18 / 120 D-20): this line previously carried a
        # D-03 note stating that leaving the flag SET on 0x0D was
        # firmware-inert and "must stay unchanged." D-12 REVERSES that
        # POLICY, not the FACT: the 0x0D firmware path genuinely never reads
        # FLAG_CAN_ERASE — that part of the old note remains true — but an
        # inert-but-false capability advertisement is still false, and
        # DEVTEST-01 needs the host to stop making it. Blast radius
        # re-verified before landing this change: no `chip_database.json`
        # entry carries a `flags` key, so `diff_db.py` identity cannot
        # break; no firmware native test and no `validation_matrix_spec.json`
        # family pins the incoming wire flags for `eeprom28c`; the only
        # other host reader of this bit (`serial_comm.py`'s
        # `_log_command_details`) is DEBUG-only logging; and exactly two
        # host tests were pinned to the old value, both inverted in this
        # same plan. One benign behavioural delta: `firestarter erase` on a
        # 0x0D part is now refused one layer earlier, at
        # `eprom_operations.cpp`'s own FLAG_CAN_ERASE precondition, rather
        # than at Phase 119's op-layer NULL-main guard — both paths emit the
        # same `MSG_ERR_NOT_SUPPORTED` wire id, so the observable behaviour
        # over the wire is unchanged.
```

## New Protocol Constant + Reason Arm (`chip_test.py`)

`_PROTOCOL_EEPROM_28C = 0x0D` defined once at line 270 (beside `_PROTOCOL_FLASH4`), used by name at line 554 in the new `elif` arm:

```python
        elif protocol == _PROTOCOL_EEPROM_28C:
            # Phase 121 D-12 deliberately routes protocol 0x0D through this
            # generic else (no 0x0D-local supported/unsupported branch was
            # added) -- but the generic fallback's flag-keyed wording below
            # names an internal mechanism, not a fact a community tester can
            # act on. DEVTEST-01 requires the FAMILY FACT: protocol 0x0D and
            # the 28C family simply has no erase operation, ever -- never
            # the flag name.
            reason = (
                "protocol 0x0D (28C family) has no erase operation; "
                "each page write auto-erases internally"
            )
```

Confirmed behaviourally: `derive_plan("AT28C256", db, write_scope="full")`'s erase step is `supported=False` with `reason == "protocol 0x0D (28C family) has no erase operation; each page write auto-erases internally"` — contains `0x0D`, does not contain `FLAG_CAN_ERASE`. The flash4 (`W29C040`) and UV (`M27C512`) arms are unchanged (`"flash4 (0x05) auto-erases per page; no separate erase op"` / `"UV-EPROM has no electrical erase (UV light only)"`).

## Both Inverted Docstrings (quoted in full)

**`tests/test_database_conversion.py::test_convert_at28c256_flash_eeprom_flag_can_erase_cleared`:**
```
REVERSAL RECORD (Phase 121 D-12): this test previously asserted AT28C256
(Flash/EEPROM, routed to 0x0D) carried FLAG_CAN_ERASE, on the claim that the
flag is firmware-inert on the 0x0D configure_eeprom28c path (D-03) and
therefore safe to leave set.

D-12 reverses that POLICY, not the fact: configure_eeprom28c genuinely
never reads FLAG_CAN_ERASE -- the D-03 firmware-inertness claim was never
wrong. What changed is that an inert-but-false capability advertisement is
still false, and DEVTEST-01's `dev test` sweep reads that advertisement and
plans a real erase step that reports OK having done nothing. D-12 clears
the flag for protocol 0x0D at the source (`database.py`), so this test now
asserts the bit is CLEAR.
```

**`tests/test_eprom_operations.py::test_sdp_command_flags_do_not_carry_the_db_can_erase_bit`:**
```
REVERSAL RECORD (Phase 121 D-12): this test previously asserted the
composed command_dict["flags"] for an at28c256 input is 2
(FLAG_CAN_ERASE), NOT 0 -- on the claim that
`database.py`'s (former) `algo != 5` exclusion set FLAG_CAN_ERASE
(0x02) for every EEPROM / Flash-EEPROM part with algorithm != 5,
including all 84 protocol-0x0D chips, and that this was safe because
configure_eeprom28c never reads the bit (firmware-inert).

D-12 reverses that POLICY, not the fact: configure_eeprom28c still
never reads FLAG_CAN_ERASE -- the firmware-inertness claim was never
wrong. What changed is that an inert-but-false capability
advertisement is still false: DEVTEST-01's `dev test` sweep reads it
and plans a real erase step that reports OK having done nothing.
`database.py` now excludes algorithm 13 (0x0D) as well as 5, so the
wire flags for at28c256 are 0, not 2. This leg now exists to catch a
regression the other way -- a future reader must not reintroduce the
bit for 0x0D.
```

Both were kept routing through the real `resolve_chip`/`convert_to_programmer` path (the `_at28c256_programmer_dict()` helper is unchanged) — genuine inversions, not hardcoded fixtures.

## Task Commits

Each task was committed atomically in the `firestarter_app` submodule (branch `v1.22-at28c-software-data-protection-lifecycle`):

1. **Task 1: Re-verify the blast radius, then clear the erase-capability flag for protocol 0x0D** — `8e02128` (fix)
2. **Task 2: Give the NA erase step a family-fact reason on protocol 0x0D** — `80c1e48` (feat)
3. **Task 3: Invert the two deliberately-pinned host tests and add the DEVTEST-01 sweep legs** — `e40d5dd` (test)

**Plan metadata:** committed in the meta repo alongside this SUMMARY (see final commit).

## Files Created/Modified

- `firestarter_app/firestarter/database.py` — widened `simple_flags` exclusion to `algo not in (5, 13)`; comment block rewritten as a full reversal record.
- `firestarter_app/firestarter/chip_test.py` — added `_PROTOCOL_EEPROM_28C = 0x0D` constant and a family-fact NA-erase reason arm inside `derive_plan`'s trailing `else`.
- `firestarter_app/tests/test_database_conversion.py` — inverted the AT28C256 flag pin (renamed, reversal docstring).
- `firestarter_app/tests/test_eprom_operations.py` — inverted the SDP command-flags wire pin (renamed, reversal docstring).
- `firestarter_app/tests/test_chip_test.py` — added two DEVTEST-01 sweep legs (erase-NA + never-called; ladder-state proof).
- `.planning/REQUIREMENTS.md` — `DEVTEST-01` checkbox ticked, traceability row updated to `Complete`. Confirmed via `git diff` that no other requirement row changed.

## Decisions Made

- Root-cause fix at `database.py` (D-12) over a `derive_plan`-local `0x0D` branch, per the plan's mandate — this makes the existing generic NA-erase path fire "for free" and keeps the capability-truth single-sourced at the DB-transform layer.
- Reason text deliberately omits the `FLAG_CAN_ERASE` identifier so a community tester reading a `dev test` report can act on the family fact rather than an internal mechanism name.

## Deviations from Plan

None from the plan's substantive requirements. One process note:

**[Rule 3-adjacent, cosmetic] `ruff format` reformatted one test's function signature.** Task 3's renamed test function (`test_convert_at28c256_flash_eeprom_flag_can_erase_cleared`) produced a line exceeding ruff's wrap width; `ruff format` (not `--check`) was run against that single file to wrap the signature onto multiple lines — a pure formatting change, no logic altered, verified by re-running the full suite (still 1091 passed) and `ruff format --check` (all files formatted). Committed as part of Task 3's commit.

## Out-of-Scope Discovery (logged, not fixed)

Logged to `.planning/phases/121-dev-test-fix-gates-docs-redesign/deferred-items.md`: `git -C /workspaces/firestarter status --porcelain` shows an untracked `firestarter/include/messages.h` inside the firmware submodule. This plan makes zero edits under `/workspaces/firestarter` (per its own objective statement) and this file predates this plan's execution — flagged for whichever session owns firmware working-tree hygiene rather than fixed here, per the scope-boundary rule (pre-existing, unrelated to this plan's task).

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `DEVTEST-01` is fully closed (both firmware and host halves landed); `dev test` sweeps against protocol-`0x0D` chips are now truthful about erase capability end to end.
- Plan `121-09` (CLI `dev test` flag removal / UV consent gate) and later plans in this wave can proceed without any dependency on this plan's remaining work — none is outstanding.
- Plan `121-14`'s final non-regression sweep should re-confirm `python3 tools/diff_db.py` and `python3 tools/check_dispatch.py` stay green, since both were exercised here.

## Self-Check: PASSED

- `firestarter_app/firestarter/database.py` — FOUND, modified as described.
- `firestarter_app/firestarter/chip_test.py` — FOUND, modified as described.
- `firestarter_app/tests/test_database_conversion.py` — FOUND, modified as described.
- `firestarter_app/tests/test_eprom_operations.py` — FOUND, modified as described.
- `firestarter_app/tests/test_chip_test.py` — FOUND, modified as described.
- Commit `8e02128` — FOUND in `firestarter_app` log.
- Commit `80c1e48` — FOUND in `firestarter_app` log.
- Commit `e40d5dd` — FOUND in `firestarter_app` log.

---
*Phase: 121-dev-test-fix-gates-docs-redesign*
*Completed: 2026-07-29*

## Self-Check: PASSED

All modified files confirmed present on disk; all four commit hashes (`8e02128`, `80c1e48`, `e40d5dd` in `firestarter_app`; `ab1a17a` in the meta repo) confirmed present in their respective repos' `git log --oneline --all`.
