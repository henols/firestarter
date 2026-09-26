---
phase: 182-jp5-destructive-operation-gate
plan: 01
subsystem: safety-gate
tags: [safety-gate, pinout, cli-refusal, tty, python, jp5, a19]

requires:
  - phase: 182-jp5-destructive-operation-gate (context/research)
    provides: D-01..D-15 decisions, the SAFE-03 six-link evidence chain, the verbatim DIP32_27C801 JSON
provides:
  - "firestarter/data/pinouts.json: DIP32_27C801 layout (A19 on pin 1, VPP/OE shared on pin 24)"
  - "firestarter/jp5_gate.py: the derived affected-part predicate and the write/erase refusal+prompt policy"
  - "firestarter/exceptions.py: Pin1HazardRefusedError"
  - "eprom_operations.py write_eprom/erase_eprom: unconditional pin1_hazard_acknowledged guard before _operation_context"
  - "cli_handlers.py write/erase commands: confirm_or_refuse arm, force-flag untouched by the gate"
  - "tests/test_jp5_gate.py: 40 tests across pure policy, real-database coupling, operator integration, off-TTY, and SAFE-01 derivation proof"
affects: [182-02, 182-03, 182-06, 185]

actuals:
  tokens: 7400
  tasks: 3
  commits: 8

tech-stack:
  added: []
  patterns:
    - "jp5_gate.py copies serial_comm._validate_hardware_revision's five properties: no I/O, no environment reads, early return on out-of-scope, fail-closed on absent evidence, and a message naming pin/mechanism/refusal/damage/escape"
    - "confirm_or_refuse follows submit.py's isatty_fn=None / confirm_fn=Confirm.ask default-through pattern"
    - "cli_handlers.py imports jp5_gate module-qualified (from firestarter import jp5_gate), matching the existing sdp_honesty/transport_counters precedent, not a from-import of the function"

key-files:
  created:
    - firestarter_app/firestarter/jp5_gate.py
    - firestarter_app/tests/test_jp5_gate.py
  modified:
    - firestarter_app/firestarter/data/pinouts.json
    - firestarter_app/firestarter/exceptions.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/firestarter/cli_handlers.py

key-decisions:
  - "D-05 resolution recorded here as this plan's premise, not re-derived: the SAFE-03 six-link evidence chain (JP5 bridged-by-default -> Rev 2.x control bit 0x08 is both CTRL_VPP_P1_ENABLE and CTRL_ADDRESS_LINE_18 -> socket pin 1 is bus line 21 -> bus line 21 sits inside the address mask mem_util_calculate_top_address_register drives -> the map fix relocates the hazard onto A19 rather than removing it -> write/erase are the damage-capable operations) means the gate ships, scoped to write and erase. SAFE-02 and SAFE-04 are NOT retired."
  - "Option B taken on _is_interactive (D-05/RESEARCH cross-phase hazard): jp5_gate.py carries its own injectable isatty_fn and never imports or calls cli_handlers._is_interactive, which Phase 185's CLAIM-07 deletes. Keeps the two phases decoupled and avoids reviving a symbol another phase in the same milestone is deleting."
  - "GATED_ADDRESS_BIT uses >= 19, not ==19, because address-bit index is a genuinely ordered scale. Measured against the shipped database via the derived structural/gated sets (test_jp5_gate.py): exactly one pinout key sits at bit 19 (DIP32_27C801) and exactly one at bit 18 (DIP32_SST39SF040, covering 255 shipped chip rows via chip_database.json — confirmed by count, not asserted). No pinout key sits above bit 19. The A18 remainder is recorded as deliberately not gated (D-06: correctness ceiling, not damage-capable on protocol 0x06's firmware path) and is NOT this plan's concern."
  - "Assumption A1 (unresolved, SAFE-03): the VPE rail level with CTRL_VPP_REGULATOR_ENABLE clear is inferred, not measured. This plan's write/erase scope rests on it. If the rail is boosted, read/verify/blank would join the damage-capable set. Plan 06 carries the operator DMM probe (VPE at J6 pin 4, regulator off) that settles it either way."
  - "chip_database.json currently has ZERO rows on DIP32_27C801 (confirmed by count) -- this plan authors the pinout layout and wires the gate mechanism, but does not touch tools/build_db.py's resolve_pinout_key. The eight 8 Mbit rows still resolve to DIP32_STD until Plan 02 (depends_on: [182-01]) fixes the generator's variant_lo dispatch and regenerates the database. This is the planned dependency order (D-01 authors the layout key so SAFE-01's wording is literally satisfiable; D-02 is a separate generator fix), not a gap in this plan."
  - "firestarter info will still print JP4 = Closed for the eight 8 Mbit parts after this plan -- the pin-count-keyed jumper derivation in ic_layout.py is untouched here. That is the D-09 phase's job (shield photographs, per-revision jumper tables, the info jumper-block rewrite), not a Phase 182 regression."

patterns-established:
  - "Damage-capable operation set as a frozenset constant (DAMAGE_CAPABLE_OPERATIONS), checked before any hazard evaluation runs, so D-06 scope (write/erase only, never read/verify/blank/id) is a single early-return rather than scattered conditionals."
  - "Derived-set proof pattern (test_jp5_gate.py's _derived_sets helper): iterate db.pin_maps, derive pin_count from the key prefix, call get_bus_config, and assert set equality -- never a literal part-number or pinout-key list in the test or the source."

requirements-completed: [SAFE-01, SAFE-02, SAFE-04]

coverage:
  - id: D1
    description: "A write on a part whose pin map puts A19 (or higher) on socket pin 1 refuses off-TTY before the serial link opens, naming the JP5 hazard"
    requirement: "SAFE-02"
    verification:
      - kind: unit
        ref: "tests/test_jp5_gate.py#test_write_eprom_on_affected_chip_refuses_before_operation_context"
        status: pass
      - kind: unit
        ref: "tests/test_jp5_gate.py#test_confirm_or_refuse_off_tty_returns_false_and_never_calls_confirm_fn"
        status: pass
    human_judgment: false
  - id: D2
    description: "Erase gets the identical gate on the identical terms as write; read/verify/blank/id are provably untouched (D-06 scope)"
    requirement: "SAFE-02"
    verification:
      - kind: unit
        ref: "tests/test_jp5_gate.py#test_erase_eprom_on_affected_chip_refuses_before_operation_context"
        status: pass
      - kind: unit
        ref: "tests/test_jp5_gate.py#test_confirm_or_refuse_d06_scope_returns_true_with_no_hazard_printed"
        status: pass
      - kind: unit
        ref: "tests/test_jp5_gate.py#test_cli_erase_with_force_on_affected_part_still_refuses_off_tty"
        status: pass
    human_judgment: false
  - id: D3
    description: "A non-interactive invocation never proceeds by default; -f/--force neither satisfies nor bypasses the gate; the affected-part set is derived from pinouts.json, not hand-listed"
    requirement: "SAFE-04, SAFE-01"
    verification:
      - kind: unit
        ref: "tests/test_jp5_gate.py#test_synthetic_pin_map_with_pin1_at_index19_appears_in_the_affected_set"
        status: pass
      - kind: unit
        ref: "tests/test_jp5_gate.py#test_structural_set_over_the_real_shipped_data_is_exactly_two_keys"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-09-10
status: complete
---

# Phase 182 Plan 01: JP5/A19 Socket-Pin-1 Destructive-Operation Gate Summary

**Write and erase now refuse before the serial link opens on any part whose pin map puts A19+ on socket pin 1, unless a human answered yes in this invocation — the affected-part set is derived from `pinouts.json` through `EpromDatabase.get_bus_config`, never hand-listed.**

## Performance

- **Duration:** ~55 min
- **Tasks:** 3 (all `type="tracer"`/`type="auto"`, `tdd="true"`)
- **Files modified:** 6 (2 created, 4 modified) in `firestarter_app`, plus 4 meta gitlink-advance commits

## Accomplishments

- Authored the `DIP32_27C801` pinout layout in `pinouts.json` (A19 on pin 1, VPP shared with `/OE` on pin 24), matching the RESEARCH's verbatim JSON and one-rom's datasheet-verified pin table. Resolved bus confirmed against the real shipped data: `[0..16, 20, 22, 21]`, index 19 == `pin_conversions[32][1]`, no `vpp-pin` key (dropped by the existing `ROM_OE` collision rule).
- Built `firestarter/jp5_gate.py`: `socket_pin1_address_bit`/`is_affected` (pure, index-based, fail-closed on absent evidence), `require_acknowledged` (the unconditional operator-layer guard), and `confirm_or_refuse` (the CLI-boundary off-TTY-refusing prompt, never default-yes).
- Added `Pin1HazardRefusedError` to `exceptions.py` (subclass of `HardwareOperationError`, not `HardwareRevisionUnsupportedError` — this is not a shield-revision problem) and wired it into `map_typed_errors` ahead of the generic `HardwareOperationError` arm.
- Wired `write_eprom` and `erase_eprom` in `eprom_operations.py` with a `pin1_hazard_acknowledged: bool = False` keyword and an unconditional `require_acknowledged` call before `_operation_context` opens the link — the default-False is what makes `dev test` and every other caller refuse with no special case.
- Wired the `write` and `erase` CLI commands in `cli_handlers.py` with a `confirm_or_refuse` arm; declining exits 1 before the operator call. `-f`/`--force` appears nowhere in the gate path (grep-verified).
- Proved the affected-part set is derived, not listed: a synthetic pin map merged through `_merge_pin_maps` with no source edit enters/exits the gated set correctly; the module carries no literal 8 Mbit part-number string (grep-verified); the structural/gated sets over real shipped data are exact set equalities (`{DIP32_SST39SF040, DIP32_27C801}` structural, `{DIP32_27C801}` gated).
- `tests/test_jp5_gate.py`: 40 tests, all passing. Plan-level verification suite (`test_jp5_gate.py` + `test_eprom_database.py` + `test_hw_revision_gate.py` + `test_submit.py`) — 202 passed. `ruff check`/`format --check` clean on `firestarter/` and `tests/`. `mypy firestarter/jp5_gate.py` clean. `check_mypy_watermark.py` — 35/35, no regression.

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule, with a matching meta gitlink-advance commit in `/workspaces`:

1. **Task 1: end-to-end write-side gate** — `9f18fd6` (feat) — pinouts.json, jp5_gate.py, exceptions.py, eprom_operations.py, cli_handlers.py, test_jp5_gate.py
2. **Task 2: expand to erase** — `193cb07` (feat) — eprom_operations.py, cli_handlers.py, test_jp5_gate.py
3. **[Deviation, Rule 1] jp5_gate.py docstring part-number leak fix** — `dc5e6fd` (fix) — see Deviations below
4. **Task 3: SAFE-01 derivation proof** — `8c8f11e` (test) — test_jp5_gate.py only (confirmed zero `firestarter/` diff)

**Meta gitlink advances:** `33292ce8`, `0dfc4f5d`, `ed517f09`, `7597d26e` (one per submodule commit above, same order).

_TDD note: tasks carried `tdd="true"` but each commit already bundled its test file with the corresponding source change (the plan's `<action>` specifies "wire ONE path" across all layers per task, not a separated red/green/refactor sequence) — this matches the plan's own task shape, not a deviation._

## Files Created/Modified

- `firestarter_app/firestarter/data/pinouts.json` — added `DIP32_27C801` layout
- `firestarter_app/firestarter/jp5_gate.py` — new policy module (created)
- `firestarter_app/firestarter/exceptions.py` — added `Pin1HazardRefusedError`
- `firestarter_app/firestarter/eprom_operations.py` — `pin1_hazard_acknowledged` kwarg + guard on `write_eprom`/`erase_eprom`
- `firestarter_app/firestarter/cli_handlers.py` — `confirm_or_refuse` arm on `write`/`erase`; `jp5_gate` module-qualified import
- `firestarter_app/tests/test_jp5_gate.py` — new test module (created), 40 tests

## Decisions Made

See `key-decisions` in the frontmatter for full detail. Summary:

- **D-05 ships the gate** — recorded as this plan's premise (resolved during 182-CONTEXT/182-RESEARCH, not re-derived here): the six-link SAFE-03 evidence chain confirms the pin-map fix relocates the hazard onto A19 rather than removing it, so SAFE-02/SAFE-04 stay live and the gate is scoped to write and erase (D-06).
- **Option B on `_is_interactive`** — `jp5_gate.py` carries its own `isatty_fn`, never touching the symbol Phase 185's CLAIM-07 deletes.
- **`GATED_ADDRESS_BIT >= 19`** — measured via the derived structural/gated sets: exactly one pinout key at bit 19, exactly one at bit 18 (255 shipped rows, deliberately not gated per D-06), none above 19.
- **`chip_database.json` still has zero rows on `DIP32_27C801`** — expected, by design. This plan authors the layout key and wires the gate; Plan 02 (`depends_on: [182-01]`) fixes `resolve_pinout_key`'s generator dispatch and regenerates the database, which is what actually moves the eight 8 Mbit chip rows onto this pinout.
- **`firestarter info` still prints JP4 = Closed for the eight parts** — `ic_layout.py`'s jumper derivation is untouched; that's the D-09 phase's job, not a Phase 182 regression.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `jp5_gate.py`'s module docstring named a literal part number, breaking its own SAFE-01 no-hand-list verification**
- **Found during:** Task 3, running the plan's own verify command (`git grep -e AM27C080 -e ... -e M27C801 -- firestarter/jp5_gate.py; test $? -ne 0`)
- **Issue:** Task 1's module docstring described the affected class as "the 8 Mbit 27C080/M27C801 class", and the substring `M27C801` matched Task 3's own forbidden-part-number grep — a check that exists precisely to prove the module carries no hand-written affected-part list. The prose was descriptive, not a list, but the grep can't tell the difference, and the check exists for a real reason (a hand-list is exactly the SAFE-01 failure mode).
- **Fix:** Reworded the sentence to name the pinout key (`DIP32_27C801`) instead of a part number. No behavior change — the predicate was already derived, never listed; only the prose tripped the guard.
- **Files modified:** `firestarter_app/firestarter/jp5_gate.py`
- **Verification:** `git grep` over the six forbidden substrings now exits 1 (no match); `ruff`/`mypy`/pytest all still clean.
- **Committed in:** `dc5e6fd` (separate commit, kept ahead of Task 3's test-only commit so Task 3's own `firestarter/` diff stays literally empty per its acceptance criterion)

**2. [Rule 1 - Bug] cli_handlers.py's `confirm_or_refuse` import restructured to module-qualified**
- **Found during:** Task 2, checking the acceptance criterion "`confirm_or_refuse` appears on exactly two lines in cli_handlers.py"
- **Issue:** `from firestarter.jp5_gate import confirm_or_refuse` at the top of the file is itself a line containing the string `confirm_or_refuse`, producing three matches (import + 2 call sites) against a criterion that requires exactly two.
- **Fix:** Switched to `from firestarter import jp5_gate` (module-qualified), matching the file's own existing precedent (`sdp_honesty`, `transport_counters` are imported the same way), and call sites became `jp5_gate.confirm_or_refuse(...)`.
- **Files modified:** `firestarter_app/firestarter/cli_handlers.py`
- **Verification:** `git grep -n confirm_or_refuse -- firestarter/cli_handlers.py` now returns exactly two lines; full CLI/write/erase regression (372 tests) still green.
- **Committed in:** `193cb07` (Task 2's own commit — caught before commit, not a follow-up fix)

**3. [Non-code] Section-divider `#` comments stripped from the newly authored test file**
- **Found during:** Authoring `test_jp5_gate.py`, following `test_hw_revision_gate.py`'s established `# ---` numbered-section convention (which the plan's own read_first cites as "the module layout to copy")
- **Issue:** `/workspaces/CLAUDE.md`'s hard rule ("no comments in product source... covers everything under firestarter/ and firestarter_app/") is broader than "product source" alone and does not carve out an exception for tests, unlike the extensive precedent of `#` comments already present throughout the existing test suite.
- **Fix:** Did not add any `#` comment to `test_jp5_gate.py`. The five numbered sections are described in the module docstring's numbered list instead of `# ---` dividers. `jp5_gate.py` and `exceptions.py` (the two files created from scratch) also carry zero `#` comments.
- **Files affected:** `firestarter_app/tests/test_jp5_gate.py` (no comments added, by omission — not a code change to revert)
- **Verification:** `grep -n '#' firestarter/jp5_gate.py tests/test_jp5_gate.py firestarter/exceptions.py` returns nothing.

---

**Total deviations:** 3 (2 Rule-1 bug fixes, 1 non-code convention deviation from the plan's own cited precedent). **Impact on plan:** None of the three altered scope or behavior; all three are either mechanical grep-criterion fixes or a stricter-than-precedent application of the project's standing no-comments rule.

## Issues Encountered

None beyond the deviations above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plan 02 (`depends_on: [182-01]`) can now fix `resolve_pinout_key`'s generator dispatch and regenerate `chip_database.json`, which will move the eight 8 Mbit chip rows onto `DIP32_27C801` — the gate mechanism built here is already wired and waiting for real chip rows to reach it.
- Plan 06 carries the operator DMM probe that resolves Assumption A1 (VPE rail level with the regulator clear) — until then, the write/erase-only scope this plan ships rests on an inferred, not measured, premise.
- `firestarter info`'s JP4 = Closed display for the eight parts is unchanged and is explicitly the D-09 phase's job, not a blocker here.
- No blockers for Plan 02, 03, or 06.

---
*Phase: 182-jp5-destructive-operation-gate*
*Completed: 2026-09-10*

## Self-Check: PASSED

All key files found on disk (jp5_gate.py, test_jp5_gate.py, pinouts.json, exceptions.py,
eprom_operations.py, cli_handlers.py). All 8 commits (4 submodule + 4 meta gitlink-advance)
verified present in `git log --oneline --all`. Plan-level `<verification>` suite re-run clean
(202 passed, ruff clean, mypy clean, watermark 35/35).
