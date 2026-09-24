---
phase: 205-the-pre-flights-leave-the-firmware
plan: "04"
subsystem: firmware, host-cli, testing
tags: [control-flag-retirement, wire-protocol, source-contract-gate, write-guard, avr, python]

requires:
  - phase: 205-03
    provides: "The firmware write-init/erase-end blank-check machinery deleted, all four firmware CI legs green, FLAG_SKIP_BLANK_CHECK itself untouched and deferred to this plan."
  - phase: 203-the-write-guard-moves-up-a-layer
    provides: "The host-side write_blank_guard.py predicate module and its requires_blank_check function, whose decision this plan re-keys."
provides:
  - "FLAG_SKIP_BLANK_CHECK (0x08) is gone from both the firmware control-flag ladder and constants.py's flag block, with a reserved-gap record on each side naming the release, phase, counterpart and never-reuse mechanism (FWBLANK-04)."
  - "write -b and dev test's masked UV slot write reach write_blank_guard.requires_blank_check through a new keyword-only blank_check_requested parameter on write_eprom, with every existing caller of write_eprom and build_flags left byte-identical."
  - "A firmware absence-and-reserved-gap leg and a host counterpart leg, both gating the retirement mechanically."
affects: [205-05, 205-06, 205-07, 206]

actuals:
  tokens: 21700
  tasks: 2
  commits: 4
  commits_by_repo:
    firestarter_fw: 1
    firestarter_app: 1
    meta: 2

tech-stack:
  added: []
  patterns:
    - "A retired wire bit's reserved-gap record names the value and the behaviour it used to select, never the macro/constant identifier -- because the record itself would otherwise be a hit on the repository-wide absence scan it coexists with. Applied on both the firmware header and constants.py."
    - "A keyword-only signal added to a function already carrying one keyword-only parameter (write_eprom's suppress_verdict_line) is a safe, additive re-plumb of a retired positional wire bit: every existing positional caller (build_flags' four positional parameters, write_eprom's ~40 positional bool test call sites) stays untouched by construction."
    - "When a behaviour-preserving re-plumb is verified (not assumed) to leave a frozen fingerprint/hash unchanged, the planned re-key commit becomes a no-op -- recorded as a measured finding rather than forced by copying a value from a simulation."

key-files:
  created: []
  modified:
    - firestarter_fw/include/firestarter.h
    - firestarter_fw/CLAUDE.md
    - firestarter_fw/src/firestarter.cpp
    - firestarter_fw/src/json_parser.c
    - firestarter_fw/src/proms/eeprom_28c.cpp
    - firestarter_fw/src/proms/flash_5v_page.cpp
    - firestarter_fw/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp
    - firestarter_fw/test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp
    - firestarter_fw/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp
    - firestarter_fw/test/native/avr/test_read_timing/test_read_timing_params.cpp
    - firestarter_fw/test/native/avr/test_sdp_harness/test_sdp_harness.cpp
    - firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp
    - firestarter_fw/test/native/avr/test_val_eprom/test_val_eprom.cpp
    - firestarter_fw/test/native/avr/test_val_flash_intel/test_val_flash_intel.cpp
    - firestarter_fw/test/native/avr/test_verify_error_ids/test_verify_error_ids.cpp
    - firestarter_fw/tests/test_config_schema_pinned.py
    - firestarter_fw/tests/test_verify_survival_source_contract.py
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/firestarter/constants.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/firestarter/write_blank_guard.py
    - firestarter_app/tests/fake_chip.py
    - firestarter_app/tests/test_chip_test_uv_slot_write.py
    - firestarter_app/tests/test_cli_handlers.py
    - firestarter_app/tests/test_eprom_operations.py
    - firestarter_app/tests/test_write_blank_guard.py
    - firestarter_app/tests/test_write_blank_guard_pinning.py
    - .planning/phases/205-the-pre-flights-leave-the-firmware/deferred-items.md

key-decisions:
  - "The internal -b re-plumb mechanism (Claude's discretion, per CONTEXT.md): a keyword-only `blank_check_requested: bool = True` parameter on `write_eprom`, threaded to `write_blank_guard.requires_blank_check` as its own third keyword-only parameter of the same name. Both production callers of `build_flags`/`write_eprom` stay positionally untouched, matching Phase 203's `suppress_verdict_line` precedent exactly."
  - "Fork C's 'rename the attribute' instruction was read narrowly: the CLASS name `WriteInitPreflightChip` was NOT renamed (it is imported by three files outside this plan's declared `<files>` lists -- test_eprom_operations.py, test_write_blank_guard.py, and tests/fixtures/report_shapes.py, the last of which is outside either task's file list entirely), because renaming it would force an undeclared-file edit to honor task 3's single-file-commit contract's spirit and would exceed task 2's own declared scope. Instead: the class docstring was rewritten to state explicitly that it models pre-3.1.0 firmware, and a NEW attribute (`blank_check_requested_seen`) was added alongside the existing `write_flags_seen` (which now stays frozen at 0 for every production caller) to carry the explicit-signal recording role the four re-anchored legs needed. Recorded here because a literal reading of 'rename the attribute' might expect the class itself renamed."
  - "Task 3 (re-key the frozen dedup_fingerprint) is a MEASURED NO-OP. RESEARCH's own instruction was followed literally: re-derive rather than copy the simulation's value (eba362ab0a75). The actual re-derived value for `uv-slot-write-pass` is `927571e5110f` -- IDENTICAL to the value already frozen in `tests/fixtures/report_shapes.py`, verified twice (before and after the FakeChip.write_eprom base-class fix documented below). This is not a coincidental match to research's number (which differs); it is the tree disagreeing with a measurement made against a different simulated re-plumb, exactly the case CONTEXT.md's probe_disposition anticipates ('the tree wins'). The reason: this plan's chosen mechanism (an explicit keyword mirroring the exact same accept/refuse decision the wire bit drove) preserves the write step's outcome byte-for-byte across both write cycles, so no StepResult -- and therefore no dedup_fingerprint input -- moves. No commit was made for task 3; there is no file to change and forcing an edit to satisfy the acceptance criterion's letter would fabricate a re-key that never happened."
  - "[Rule 3 - Blocking] `firestarter_app/firestarter/cli_handlers.py` was added to task 2's edit set even though it is outside that task's declared `<files>` list. Without threading `blank_check_requested=blank_check` into the `write()` handler's `write_eprom(...)` call, `-b` would silently stop bypassing the guard the moment `build_flags` stopped composing the wire bit -- a straight regression the plan's own success criterion 4 ('write -b ... still reach requires_blank_check') requires. This is the CLI-side half of D-04's explicit 'write -b reaches the guard as an explicit host-side signal' instruction; the plan's own file list for this exact behaviour was simply incomplete."
  - "[Rule 3 - Blocking] The BASE `FakeChip.write_eprom` (not just the `WriteInitPreflightChip` subclass) needed the new keyword-only `blank_check_requested` parameter too. `chip_test.py`'s dispatch now passes it unconditionally to every operator double reachable through `run_plan`/`_dispatch_multi_run`, and ten tests across `test_chip_test.py` and `test_dev_test_cmd.py` construct a bare `FakeChip` directly -- all ten failed with `TypeError: got an unexpected keyword argument` until this was added. The base class accepts and discards the value (it models no blank-check pre-flight at all); only the subclass acts on it."

requirements-completed: [FWBLANK-04]

coverage:
  - id: D1
    description: "FLAG_SKIP_BLANK_CHECK is deleted from the firmware control-flag ladder with a reserved-gap record at the 0x08 gap naming the release, phase, host counterpart and never-reuse mechanism. The DEV_TOOLS-gated debug flag-dump emit that read it is removed, and test_config_schema_pinned.py's shifted line pins move in the same commit. The two anti-regression comments and the json_parser.c FIELD_MASK example are rewritten without naming the retired identifier. A new absence-and-reserved-gap leg gates it; the pre-existing reserved-marker leg is re-anchored from a floor of two records to three."
    requirement: FWBLANK-04
    verification:
      - kind: unit
        ref: "firestarter_fw/tests/test_verify_survival_source_contract.py::test_the_retired_control_flag_is_absent_and_its_gap_is_recorded"
        status: pass
      - kind: unit
        ref: "firestarter_fw/tests/test_verify_survival_source_contract.py::test_all_three_reserved_gaps_carry_a_recorded_reason"
        status: pass
      - kind: integration
        ref: "pio test -e native (241/241), pio test -e native_nodevtools (241/241), pytest tests/ (316/316), pio run (uno/uno328pb/leonardo all SUCCESS)"
        status: pass
      - kind: other
        ref: "git grep -n FLAG_SKIP_BLANK_CHECK -- src/ include/ test/ CLAUDE.md PROTOCOLS.md (excl. the survival gate module) -> exit 1, no matches"
        status: pass
    human_judgment: false
  - id: D2
    description: "FLAG_SKIP_BLANK_CHECK is deleted from constants.py's flag block with a matching reserved-gap record. write -b and dev test's masked UV slot write reach write_blank_guard.requires_blank_check through write_eprom's new keyword-only blank_check_requested parameter, with build_flags' and write_eprom's existing positional callers byte-identical. 14 legs across 5 test modules are re-anchored onto the explicit signal or the wire-composition invariant it replaced; a new host ladder leg gates the retirement itself."
    requirement: FWBLANK-04
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_eprom_operations.py::test_the_retired_control_flag_is_absent_and_its_gap_is_recorded"
        status: pass
      - kind: integration
        ref: "pytest tests/ (2319/2319 incl. 36 snapshots), collect-only pass shows no collection errors"
        status: pass
      - kind: other
        ref: "git grep -n FLAG_SKIP_BLANK_CHECK -- firestarter/ tests/fake_chip.py -> exit 1, no matches; ruff check + ruff format --check both clean"
        status: pass
    human_judgment: false
  - id: D3
    description: "The frozen dedup_fingerprint literal for uv-slot-write-pass in tests/fixtures/report_shapes.py was re-measured against the tree this plan produced and found UNCHANGED (927571e5110f both before and after) -- a verified no-op, not a forced re-key. No commit was made for task 3."
    verification:
      - kind: other
        ref: "python -c one-liner computing dedup_fingerprint(build_shape('uv-slot-write-pass')) against the post-task-2 tree, run twice (before and after the FakeChip base-class fix) -- 927571e5110f both times, matching the value already committed"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_blast_radius_invariance.py (67/67, unmodified)"
        status: pass
    human_judgment: false

duration: 130min
completed: 2026-09-22
status: complete
---

# Phase 205 Plan 04: The skip-blank-check control flag leaves both ladders Summary

**FLAG_SKIP_BLANK_CHECK (0x08) is retired from the firmware and constants.py in a firmware-first commit pair, with `write -b` and `dev test`'s masked UV slot write re-plumbed onto `write_eprom`'s new `blank_check_requested` keyword -- and the planned frozen-fingerprint re-key turned out, when measured against the real tree, to be a no-op.**

## Performance

- **Duration:** ~130 min
- **Started:** 2026-09-22 (session start)
- **Completed:** 2026-09-22
- **Tasks:** 2 of the plan's 3 tasks produced a commit (task 3 measured no-op)
- **Files modified:** 17 in `firestarter_fw`, 12 in `firestarter_app`, 2 gitlink advances + 1 deferred-items ledger in the meta repo

## Accomplishments

- `FLAG_SKIP_BLANK_CHECK` is gone from `include/firestarter.h`'s control-flag ladder and from `firestarter/constants.py`'s flag block, in neither case leaving `0x08` or the identifier anywhere except the two reserved-gap records, each naming the release, the phase, the counterpart ladder, and the never-reuse mechanism (an already-shipped host still composes `0x08`).
- The firmware absence leg's RED was captured against the pre-edit tree (found the identifier in exactly the four expected sites: the two ladders, the debug emit, and the two anti-regression comments) before the sweep landed; the host absence leg's RED was captured the same way, against a temporarily-restored pre-edit tree, before the host sweep landed.
- `write -b` and `dev test`'s masked UV slot write (`chip_test.py`'s one non-CLI producer of the retired bit) both now reach `write_blank_guard.requires_blank_check` through `write_eprom`'s new keyword-only `blank_check_requested` parameter -- every existing positional caller of `build_flags` (2) and `write_eprom` (~40 test call sites) is untouched.
- 11 native Unity lines across 8 suites are re-keyed onto surviving flags or dropped where the flag was inert; `test_read_timing_params.cpp`'s saturation proof is re-keyed onto `FLAG_VPE_AS_VPP` rather than dropped, preserving its FIELD_MASK-does-not-saturate claim. `test_val_5v_page.cpp` needed prose-only rewrites (all six references live in comments/messages).
- 14 host legs across 5 modules are re-anchored onto the explicit `blank_check_requested` signal or onto the now-invariant wire composition (`_build_op_flags(blank_check=False)` composes no bit at all any more, on either `write` or `erase`).
- The planned dedup_fingerprint re-key (task 3) is a measured no-op: re-deriving `uv-slot-write-pass`'s fingerprint against the real post-task-2 tree produces `927571e5110f`, identical to the value already frozen -- because this plan's chosen re-plumb mechanism preserves the exact write-step outcome the wire bit produced. No third commit exists; `tests/test_blast_radius_invariance.py` was never touched and never went red.
- All four firmware CI legs green at the firmware commit; the whole host suite (2319/2319, 36 snapshots) green at the host commit, with `ruff check`/`ruff format --check` both clean.

## Task Commits

Each task was committed atomically, except task 3 (measured no-op, see Deviations):

1. **Task 1: the bit leaves the firmware, with its reserved record and every gate it moves** — `9061dd1` (feat, in `firestarter_fw`)
2. **Task 2: the bit leaves the host, and -b becomes an explicit signal** — `9a82478` (feat, in `firestarter_app`)
3. **Task 3: re-key the frozen dedup fingerprint, in its own commit** — NO COMMIT. Measured against the real tree, the value does not move (see Deviations and Decisions).

**Gitlink advances:** `6ace58fc` (chore, meta, firmware to `9061dd1`), `a138038b` (chore, meta, host to `9a82478`).

_Note: no TDD tasks in this plan; both landed commits required a captured RED transcript before their new absence leg's commit, per the plan's own discipline (see "RED Transcripts" below)._

## Files Created/Modified

### `firestarter_fw`
- `include/firestarter.h` — deleted `FLAG_SKIP_BLANK_CHECK 0x08`; added the reserved-gap record between `FLAG_SKIP_ERASE` and `FLAG_VPE_AS_VPP`.
- `CLAUDE.md` — replaced the flag's documentation row with a reserved note in the same table.
- `src/firestarter.cpp` — deleted the `DBG_FLAG_SKIP_BLANK` debug emit line (shifted `test_config_schema_pinned.py`'s two lower pins by one).
- `src/json_parser.c` — the `FIELD_MASK` policy comment's example flag changed from `FLAG_SKIP_BLANK_CHECK` to `FLAG_VPE_AS_VPP`; the comment's point (saturation would fail open) is unchanged.
- `src/proms/eeprom_28c.cpp`, `src/proms/flash_5v_page.cpp` — the two anti-regression comments rewritten to warn about the behaviour (the host owns this refusal as of 3.1.0) rather than naming a bit that no longer exists.
- `test/native/avr/test_val_eprom/test_val_eprom.cpp` — `make_handle`/`make_write_handle` re-keyed to `FLAG_SKIP_ERASE` alone; the `make_region_handle` factory comment rewritten (its factual claim about "the blank-check axis" no longer applies since write-init performs none at all).
- `test/native/avr/test_val_flash_intel/test_val_flash_intel.cpp`, `test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp`, `test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp`, `test/native/avr/test_verify_error_ids/test_verify_error_ids.cpp` — handle-construction re-keys, comment rewrites where present.
- `test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`, `test/native/avr/test_sdp_harness/test_sdp_harness.cpp` — four handle-factory assignments dropped (protocol `0x0D` never wired a real blank-check pre-flight); two assertion-message prose rewrites.
- `test/native/avr/test_read_timing/test_read_timing_params.cpp` — the saturation leg's flag literal re-keyed onto `FLAG_VPE_AS_VPP`, not dropped, per the plan's explicit instruction.
- `test/native/avr/test_val_5v_page/test_val_5v_page.cpp` — six prose-only rewrites (comments and `TEST_ASSERT` messages); no code changed.
- `tests/test_config_schema_pinned.py` — `_C14_CONSUMER_SITES`' two `src/firestarter.cpp` lines re-derived: 102→101, 108→107; 38 unmoved, exactly as measured.
- `tests/test_verify_survival_source_contract.py` — new Coverage 15 (`test_the_retired_control_flag_is_absent_and_its_gap_is_recorded`), a new concatenation-built `_NEEDLE_RETIRED_FLAG`, a positional gap-containment regex, and Coverage 10 renamed/re-anchored from a floor of two to three (`test_all_three_reserved_gaps_carry_a_recorded_reason`). Also corrected a pre-existing docstring gap (Coverage 14 was missing from the top-of-module numbered list since Phase 205 Plan 03 added it).

### `firestarter_app`
- `firestarter/constants.py` — deleted `FLAG_SKIP_BLANK_CHECK = 0x08`; added the reserved-gap record.
- `firestarter/eprom_operations.py` — `build_flags` no longer composes any bit for `blank_check` (docstring updated); `write_eprom` gained the keyword-only `blank_check_requested: bool = True` parameter, threaded to `requires_blank_check`; the stale `FLAG_SKIP_BLANK_CHECK` mention in a nearby state-comment rewritten.
- `firestarter/chip_test.py` — removed the import; the masked UV slot write now computes `blank_check_requested = not _is_monotonic_masked_target(...)` and passes it as a keyword instead of composing a wire flag; two stale comments rewritten (one, at the old `mem_util_blank_check` mention, described a firmware function Phase 205 Plan 03 already deleted).
- `firestarter/serial_comm.py` — removed the import and the debug flag-dump row.
- `firestarter/write_blank_guard.py` — removed the import; `requires_blank_check` gained the keyword-only `blank_check_requested: bool = True` parameter and now decides on it directly; module docstring's tense corrected (Phase 205 already landed, not "removes"); `GUARDED_PROTOCOL_IDS`' three stale firmware citations rewritten to the past tense.
- `firestarter/cli_handlers.py` — **[deviation, see Decisions]** the `write()` handler now passes `blank_check_requested=blank_check` to `write_eprom`.
- `tests/fake_chip.py` — removed the import; `WriteInitPreflightChip`'s docstring rewritten to state it models pre-3.1.0 firmware explicitly; its `write_eprom` re-keyed onto the new keyword, with a new `blank_check_requested_seen` list added alongside the now-frozen-at-zero `write_flags_seen`; the base `FakeChip.write_eprom` **[deviation, see Decisions]** also gained (and discards) the same keyword for signature compatibility.
- `tests/test_eprom_operations.py` — `test_build_flags_no_blank_check_sets_no_wire_bit` (re-anchored, renamed); new `test_the_retired_control_flag_is_absent_and_its_gap_is_recorded` following Phase 204's executed shape.
- `tests/test_write_blank_guard.py` — one leg re-anchored (renamed to `test_requires_blank_check_false_with_blank_check_requested_false`); `_drive_write_eprom` gained a `blank_check_requested` passthrough parameter; two integration legs re-anchored.
- `tests/test_write_blank_guard_pinning.py` — import removed; four legs re-anchored (module docstring's Coverage-7 description updated too).
- `tests/test_chip_test_uv_slot_write.py` — import removed; module docstring and two per-leg docstrings/citations corrected; three legs re-anchored (module import + 3 code sites = the "four" sites the plan named).
- `tests/test_cli_handlers.py` — three legs re-anchored (`test_write_no_blank_check_polarity`, `test_write_b_decouples_skip_erase_phase92`, `test_erase_blank_check_polarity` — the last re-anchored onto a wire-composition-invariance assertion since `_build_op_flags` no longer distinguishes `-b` from its absence on `erase` either).

### Meta repo
- `firestarter_fw`, `firestarter_app` gitlinks advanced.
- `.planning/phases/205-the-pre-flights-leave-the-firmware/deferred-items.md` — new; three out-of-scope stale-citation findings (see Deviations).

## Decisions Made

See the frontmatter `key-decisions` block for full reasoning. In one sentence each:

1. `-b`'s internal re-plumb mechanism is a keyword-only `blank_check_requested` parameter on `write_eprom`, threaded to `requires_blank_check` as its own keyword, mirroring Phase 203's `suppress_verdict_line` precedent exactly.
2. Fork C's "rename the attribute" was read as adding a new attribute (`blank_check_requested_seen`) and rewriting the docstring, not renaming the `WriteInitPreflightChip` class itself, because the class name is imported by a file outside either task's declared scope.
3. Task 3's re-key is a measured no-op — the real tree's fingerprint does not move, verified twice, and no commit exists for it.
4. `cli_handlers.py`'s `write()` handler needed the new keyword threaded through (Rule 3, blocking) — otherwise `-b` would silently stop working.
5. The base `FakeChip.write_eprom` needed the new keyword too (Rule 3, blocking) — ten tests construct it directly and `chip_test.py`'s dispatch now passes the keyword unconditionally.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `cli_handlers.py`'s `write()` handler needed the new keyword threaded through, though the file is outside task 2's declared `<files>` list**
- **Found during:** Task 2, after removing `build_flags`' wire-bit composition and adding `write_eprom`'s `blank_check_requested` keyword, while tracing every path that must reach it for `write -b` to keep working.
- **Issue:** The plan's task 2 `<files>` list does not include `firestarter_app/firestarter/cli_handlers.py`, but the CLI's `write` command is the ONLY production caller of `write_eprom` outside `chip_test.py`, and without threading the new keyword there, `-b` would silently stop bypassing the guard — success criterion 4 requires it to keep working.
- **Fix:** Added `blank_check_requested=blank_check` to the `write()` handler's `write_eprom(...)` call.
- **Files modified:** `firestarter_app/firestarter/cli_handlers.py`
- **Verification:** `tests/test_cli_handlers.py::test_write_no_blank_check_polarity` and `::test_write_b_decouples_skip_erase_phase92` (re-anchored, see below) pass; full suite green.
- **Committed in:** `9a82478` (Task 2 commit)

**2. [Rule 3 - Blocking] `tests/fake_chip.py`'s base `FakeChip.write_eprom` needed the new keyword too**
- **Found during:** Task 2's full-suite verification run — 10 tests in `test_chip_test.py` and `test_dev_test_cmd.py` failed with `TypeError: FakeChip.write_eprom() got an unexpected keyword argument 'blank_check_requested'`.
- **Issue:** `chip_test.py`'s dispatch now passes `blank_check_requested` unconditionally to every operator double reachable through `run_plan`/`_dispatch_multi_run`. These 10 tests construct a bare `FakeChip` directly (not the `WriteInitPreflightChip` subclass this plan's own `<files>` list names), which had no such parameter.
- **Fix:** Added `*, blank_check_requested: bool = True` to the base class's `write_eprom`, accepted and discarded (the base double models no blank-check pre-flight at all).
- **Files modified:** `firestarter_app/tests/fake_chip.py`
- **Verification:** `pytest tests/test_chip_test.py tests/test_dev_test_cmd.py` — 231/231 pass; full suite re-run 2319/2319.
- **Committed in:** `9a82478` (Task 2 commit)

**3. [Rule 1 - unrelated pre-existing drift, logged not fixed] Three stale prose citations of the retired identifier outside either task's declared file lists**
- **Found during:** Task 2, while grepping broadly for `FLAG_SKIP_BLANK_CHECK` beyond the plan's own two-path absence-gate scope (`firestarter/` and `tests/fake_chip.py`).
- **Issue:** `cli_handlers.py:1102` cites a firmware line Phase 205 Plan 03 already deleted (`flash_nor_unlock.cpp:41`) as "commented out" (it is gone outright); `tests/test_uv_mask.py:201` and `tests/fixtures/report_shapes.py:653` both still name the retired identifier in prose describing the pre-retirement mechanism. None is scanned by this plan's own absence gates, and none is in either task's declared `<files>` list.
- **Fix:** NOT fixed — logged to `deferred-items.md` per the scope-boundary rule (pre-existing/out-of-scope, not caused by this plan's own edits to those specific lines).
- **Files modified:** none (documentation only, in `.planning/phases/205-the-pre-flights-leave-the-firmware/deferred-items.md`)
- **Verification:** N/A — deferred.
- **Committed in:** N/A (recorded, not fixed)

---

**Total deviations:** 2 auto-fixed (both Rule 3, blocking), 1 logged-not-fixed (Rule 1, pre-existing, out of scope).
**Impact on plan:** Both auto-fixes were necessary for `-b` and the host suite to keep working at all — no scope creep beyond what FWBLANK-04 itself requires. The logged item is cosmetic prose staleness with zero behavioural effect.

## RED Transcripts

**Task 1 (firmware)** — `test_all_three_reserved_gaps_carry_a_recorded_reason` and `test_the_retired_control_flag_is_absent_and_its_gap_is_recorded`, captured by backing up the edited files, `git checkout --` restoring the pre-edit tree, running the two legs, then restoring the edited files from backup (no `git stash` used):

```
tests/test_verify_survival_source_contract.py::test_all_three_reserved_gaps_carry_a_recorded_reason FAILED
tests/test_verify_survival_source_contract.py::test_the_retired_control_flag_is_absent_and_its_gap_is_recorded FAILED
...
E       AssertionError: expected the reserved marker to appear at least three times in
E       include/firestarter.h ..., found 2 -- a reserved record is missing at one of the three gaps.
...
E       AssertionError: found the retired control flag's identifier surviving in a firmware
E       source or header ...
E         Got:
E         src/firestarter.cpp
E         include/firestarter.h
E         src/proms/flash_5v_page.cpp
E         src/proms/eeprom_28c.cpp
2 failed, 13 deselected in 0.12s
```
Both failed for the intended reason — found the identifier in exactly the four expected sites, and the marker count was 2 (not yet 3).

**Task 2 (host)** — `test_the_retired_control_flag_is_absent_and_its_gap_is_recorded`, captured the same way (backup, `git checkout --` restore of all 8 then-edited production/test files, run a standalone copy of the new test against the restored tree, restore edits from backup):

```
FAILED test_retired_flag_red.py::test_the_retired_control_flag_is_absent_and_its_gap_is_recorded
E       AssertionError: constants.py must not define FLAG_SKIP_BLANK_CHECK -- retired in
E       Phase 205 Plan 04 (FWBLANK-04)
E       assert not True
E        +  where True = hasattr(<module 'firestarter.constants' ...>, 'FLAG_SKIP_BLANK_CHECK')
1 failed in 0.25s
```
Failed for the intended reason — found the symbol still defined.

## Issues Encountered

None beyond the deviations documented above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `FLAG_SKIP_BLANK_CHECK` is gone from both repositories, in source, header, test and documentation, except the two reserved-gap records (which name the bit by value, never by identifier).
- All four firmware CI legs green at `9061dd1`; the whole host suite (2319/2319) green at `9a82478`; `ruff check`/`ruff format --check` clean.
- Both meta gitlinks advanced; no branch in any of the three repositories is `beta` at any point in this plan's execution.
- The D-04 accepted regression (a post-205 host driving pre-205 firmware no longer suppresses the firmware's surviving pre-flight on `write -b` or `dev test`'s masked UV slot writes) is unchanged by this plan's specific implementation choice — it is a consequence of the retirement itself, not of how `-b` was re-plumbed host-side. Plan 07's B3 leg still needs to observe it on silicon; REL-04 still needs to document it in Phase 207.
- Three pre-existing stale prose citations of the retired identifier, outside this plan's scope, are logged in `deferred-items.md` for a future pass.
- `firestarter_app/tests/fixtures/report_shapes.py`'s `uv-slot-write-pass` frozen fingerprint (`927571e5110f`) is CONFIRMED unmoved by this plan's re-plumb — any future plan touching this area should re-verify rather than assume it is now free to change without a re-key.

---
*Phase: 205-the-pre-flights-leave-the-firmware*
*Completed: 2026-09-22*

## Self-Check: PASSED
