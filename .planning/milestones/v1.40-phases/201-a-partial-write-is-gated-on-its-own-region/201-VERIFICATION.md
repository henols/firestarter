---
phase: 201-a-partial-write-is-gated-on-its-own-region
verified: 2026-09-20T09:47:54Z
status: passed
score: 3/3 must-haves verified
covered_files:
  - ".planning/REQUIREMENTS.md"
  - ".planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-01-PLAN.md"
  - ".planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-01-SUMMARY.md"
  - ".planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-02-PLAN.md"
  - ".planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-02-SUMMARY.md"
  - ".planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-03-PLAN.md"
  - ".planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-03-SUMMARY.md"
  - ".planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-04-PLAN.md"
  - ".planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-04-SUMMARY.md"
  - ".planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-05-PLAN.md"
  - ".planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-05-SUMMARY.md"
  - ".planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-06-PLAN.md"
  - ".planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-06-SUMMARY.md"
  - ".planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-BENCH-RECORD.md"
  - ".planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-REVIEW.md"
  - "firestarter_app/firestarter/constants.py"
  - "firestarter_app/firestarter/eprom_operations.py"
  - "firestarter_app/tests/fake_chip.py"
  - "firestarter_app/tests/test_chip_test_uv_slot_write.py"
  - "firestarter_app/tests/test_eprom_operations.py"
  - "firestarter_fw/include/firestarter.h"
  - "firestarter_fw/include/memory_utils.h"
  - "firestarter_fw/src/eprom_operations.cpp"
  - "firestarter_fw/src/json_parser.c"
  - "firestarter_fw/src/proms/eprom.cpp"
  - "firestarter_fw/src/proms/memory.cpp"
  - "firestarter_fw/test/native/avr/test_val_eprom/host_stubs.cpp"
  - "firestarter_fw/test/native/avr/test_val_eprom/test_val_eprom.cpp"
  - "firestarter_fw/tests/golden/protocol_branch_inventory.json"
  - "firestarter_fw/tests/test_blank_check_region_source_contract.py"
  - "firestarter_fw/tests/test_progress_emission_is_leonardo_only.py"
covered_digest: "v1:sha256:24c2aee228d531a86ddda8198d2ad2b401625297fb992e3b6744283d90cc4cb7"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 201: A Partial Write Is Gated On Its Own Region — Verification Report

**Phase Goal:** Close backlog 999.44's live firmware half, so a non-erasable part holding data
anywhere stops being unwritable everywhere.

**Verified:** 2026-09-20T09:47:54Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A write into a blank region of a non-blank, non-erasable part succeeds. | VERIFIED | `201-BENCH-RECORD.md` § "M27C512 confirming run": chip-ID `0x203D` confirmed twice on the M27C512; `firestarter info m27c512` independently re-run during this verification confirms `Type: UV-EPROM`, `Can be erased: no (UV erase only)`; `database.py:573-579` (`firestarter_app`) confirms `FLAG_CAN_ERASE` is set only for `electrical-type in (EEPROM, Flash/EEPROM)` — UV-EPROM never qualifies, so the part is genuinely non-erasable, not merely labelled so. Full-device read-back showed 271 non-blank bytes on *both* sides of the chosen target (`0x000000`-`0x00000F` and `0x00FF01`-`0x00FFFF`); the write at `0x008000` (64 bytes) succeeded and verify was clean. Commit SHAs `af47bf4` (pre-fix) and `e5842d8` (post-fix) cited in the record were independently confirmed to exist and match their stated commit messages in `firestarter_fw`. |
| 2 | The standalone blank-check command and the erase-end check are unchanged, chunked resumption included. | VERIFIED | `mem_util_blank_check` (`memory.cpp:540-542`) is a one-line wrapper `mem_util_blank_check_region(handle, 0, handle->mem_size)` — dispatch to it is untouched at all nine reference sites (verified by reading `eprom.cpp:53,57`, `flash_intel.cpp:62,95`, `flash_nor_unlock.cpp:44,105`, `flash_5v_page.cpp:47`, `eeprom_28c.cpp:151`, and independently by `tests/test_blank_check_region_source_contract.py`, run this session: 9/9 passed). Native characterization tests written in plan 201-01 *before* the split (`test_blank_check_resumes_across_chunks_and_restores_the_cursor`, `test_erase_end_blank_check_scans_from_zero`) still exist and pass (confirmed: `pio test -e native -f "*test_val_eprom*"`, 13/13 passed, run this session). The bench record's own RED-half blank-check output is byte-for-byte identical to the GREEN-half's (`ERROR: Not blank, at 0x000000, v: 0xa5`, both runs) — the standalone command's behaviour is unchanged on real silicon, not merely in software. |
| 3 | A regression test covers a non-blank non-erasable part — the case whose absence is why this shipped. | VERIFIED | `test_write_init_accepts_blank_region_on_non_blank_part` was authored and run in plan 201-02, observed RED against unmodified firmware (verbatim transcript captured in `201-02-SUMMARY.md`, commit `af47bf4`), then observed GREEN after plan 201-03's fix (verbatim transcript in `201-03-SUMMARY.md`, commit `76fd3c7`). Its paired negative control (`test_write_init_still_refuses_when_target_region_is_non_blank`) was green throughout. Both tests still exist and pass in the current tree (confirmed this session, native suite 13/13 and full `native_nodevtools` 237/237). Host-side coverage of the same case (`test_write_into_blank_region_of_non_blank_part_succeeds` in `test_eprom_operations.py` against a `fake_chip.py` that now models the region, not the whole buffer) also passes (6/6 region-related legs, confirmed this session). |

**Score:** 3/3 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_fw/include/memory_utils.h` | declares `mem_util_operation_end`, `mem_util_blank_check_region` | VERIFIED | Both declared, matches plan 201-03/04 design |
| `firestarter_fw/src/proms/memory.cpp` | `mem_util_operation_end` (fallback+clamp), `mem_util_blank_check_region` (scan body), `mem_util_blank_check` (wrapper) | VERIFIED | All three present exactly as designed (`memory.cpp:456-542`); wired and used |
| `firestarter_fw/src/proms/eprom.cpp` | write-init calls region form at exactly one site | VERIFIED | `eprom.cpp:145`, single call inside `eprom_internal_write_init_body`, confirmed by source-contract gate |
| `firestarter_fw/src/json_parser.c` | `region-end` wire field, parsed and reset to 0 per command | VERIFIED | `key_region_end` PROGMEM string, `FIELD` row, reset block present and commented with the fail-open rationale (`json_parser.c:75,158,296`) |
| `firestarter_fw/src/eprom_operations.cpp` | write/verify bound on `op_end` not `mem_size` | VERIFIED | `_process_incoming_data` uses `mem_util_operation_end(handle)` at done-check and out-of-range guard (`:90,95,128`) |
| `firestarter_fw/tests/test_blank_check_region_source_contract.py` | source-contract gate over nine reference sites | VERIFIED | Exists, substantive (9 test functions matching the plan's documented coverage list), run this session: 9/9 passed |
| `firestarter_app/firestarter/eprom_operations.py` | emits `region-end` from `_setup_operation` | VERIFIED | Confirmed via `test_eprom_operations.py` region-emission legs passing |
| `firestarter_app/tests/fake_chip.py` | `_is_blank` learns the region | VERIFIED | `_is_blank(start, end)` present with region-aware comment (`fake_chip.py:77-101`) |
| `.planning/phases/.../201-BENCH-RECORD.md` | silicon evidence for criterion 1 | VERIFIED | 563-line record, cross-checked against git history and the live chip database this session |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `mem_util_blank_check` | `mem_util_blank_check_region` | one-line wrapper `(0, mem_size)` | WIRED | `memory.cpp:540-542` |
| write-init body | `mem_util_blank_check_region` | `mem_util_blank_check_region(handle, handle->address, mem_util_operation_end(handle))` | WIRED | `eprom.cpp:145` |
| `_process_incoming_data` | `mem_util_operation_end` | done-check and out-of-range guard | WIRED | `eprom_operations.cpp:95,100,128` |
| host `_setup_operation` | firmware `json_parser.c` | wire key `region-end` | WIRED (evidenced on real hardware) | Bench record's confirming run showed the firmware's write progress denominator move to `0x8040` (`region_end`), which only happens if the host's emitted `region-end` was correctly parsed into `handle->region_end` by `json_parse()` and consumed by `mem_util_operation_end` — this is an end-to-end proof of the wire link, on real silicon, distinct from and stronger than a unit test |
| `write_eprom`/`verify_eprom` | `WriteInitPreflightChip._is_blank` (host fake) | region-scoped comparison | WIRED | `test_eprom_operations.py` region legs pass against the updated fake |

### Data-Flow Trace

Not primarily applicable — this phase is a firmware/protocol change, not a UI data-rendering
change. The relevant "data flow" is the wire-protocol path traced under Key Link Verification
above (host → JSON → firmware struct field → scan bound), confirmed both by native/host tests and
by the bench record's live-hardware transcript.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Native `test_val_eprom` suite (BLANK-02 chunking/erase-end pins + BLANK-03 RED/GREEN pair) | `pio test -e native -f "*test_val_eprom*"` | 13/13 passed | PASS |
| Full native suite, both CI envs | `pio test -e native_nodevtools` | 237/237 passed | PASS |
| Firmware source-contract gate (nine-site census) | `pytest tests/test_blank_check_region_source_contract.py` | 9/9 passed | PASS |
| Progress-emission gate (`op_end` denominator restated) | `pytest tests/test_progress_emission_is_leonardo_only.py` | 11/11 passed | PASS |
| Branch-inventory golden re-derivation check | `pytest tests/test_protocol_branch_inventory.py` | 7/7 passed | PASS |
| Host region-emission/write legs | `pytest tests/test_eprom_operations.py -k "region_end or blank_region"` | 6/6 passed | PASS |
| Host UV-slot-write double | `pytest tests/test_chip_test_uv_slot_write.py` | 12/12 passed | PASS |
| M27C512 database classification (independent re-check of bench record's premise) | `firestarter info m27c512` | `Type: UV-EPROM`, `Can be erased: no (UV erase only)` | PASS — matches bench record verbatim |

All checks above were re-run independently during this verification (not merely trusted from
SUMMARY.md or the orchestrator's prior measurement), and all match the orchestrator's
independently-reported counts (237/237 native, etc.).

### Probe Execution

Not applicable — no `scripts/*/tests/probe-*.sh` probes are declared or referenced by this phase's
plans or success criteria.

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| BLANK-01 | 201-03, 201-04, 201-06 | Write-init blank check scoped to the region being written | SATISFIED | Region form landed (`eprom.cpp:145`), bench-confirmed on silicon (M27C512) |
| BLANK-02 | 201-01, 201-04, 201-05 | Standalone blank-check and erase-end unchanged, chunking still resumes | SATISFIED | Wrapper unchanged, characterization tests pass, source-contract gate added, bench record shows byte-identical standalone output pre/post fix |
| BLANK-03 | 201-02, 201-03, 201-06 | UV part with data outside target slot accepts a slot write, proved by regression test | SATISFIED | RED (201-02) → GREEN (201-03) native test, host `fake_chip.py` region-aware test, M27C512 silicon confirmation |

No orphaned requirements: REQUIREMENTS.md maps exactly BLANK-01/02/03 to Phase 201, and all three
appear in at least one plan's `requirements:` frontmatter field (cross-checked above).

### Anti-Patterns Found

None. Scanned all 15 code-review-listed changed files (firmware and host) for `TBD`/`FIXME`/`XXX`
and `TODO`/`HACK`/`PLACEHOLDER` markers via `git grep` (not bare `grep`, per this project's ugrep
`.gitignore`-honoring gotcha) — zero matches in either category.

### Code Review Findings (201-REVIEW.md, carried forward)

Two WARNING-level findings, no BLOCKER-level findings, filed by the phase's own code review:

- **WR-01** — `region-end` has no unit test that parses raw JSON through `json_parse()`; every
  existing test sets `handle->region_end` directly on the C struct. Independently confirmed by
  `git grep -n "region_end" test/native/` — both matches set the field directly, none parse JSON.
  **Judgment:** this is a real automated-test-coverage gap and should be tracked as a follow-up
  (the review's own suggested fix is cheap: two cases following the existing `read_settling_us`
  pattern). It does **not** undermine any of this phase's three success criteria: the bench
  session's confirming run (criterion 1) drove the write through the *actual* host→firmware wire
  protocol, meaning the real `json_parse()` path parsed a genuine `"region-end"` key and the
  firmware's behaviour (progress denominator `0x8040`, matching `region_end`) could only be
  produced if that parse succeeded — so the mechanism this gap is about was, in fact, exercised
  end-to-end on real hardware even though no automated regression pins it. Not a gap against a
  must-have; recommend filing a todo.
- **WR-02** — `mem_util_blank_check_region` fail-opens silently (reports "blank" having scanned
  zero bytes) if ever called with `start > end`; the reviewer confirmed this cannot happen today
  because the only call site shares the same `handle->address >= op_end` guard downstream, but the
  safety property lives in a different function than the one that would need it. **Judgment:** a
  real defensive-programming gap, correctly scoped as non-blocking by the review (confirmed today's
  single call site cannot trigger it) — not a gap against any of this phase's must-haves.

Neither warning is disputed by this verification; both are accurately characterized by the review
as non-blocking. Recommend the operator file both as todos before milestone close, since neither
appears yet in `.planning/todos/pending/`.

### Human Verification Required

None. Criterion 1's silicon proof is not an item deferred to a human-in-the-loop checkpoint after
this verification — it is a completed, thoroughly-documented bench session (201-BENCH-RECORD.md)
that this verification independently cross-checked against git history and the live chip database.
Both operator-authorized deviations (TMS27C512 → ST M27C512 substitution; target address `0x00FF00`
→ `0x008000`) are recorded in the bench record with explicit rationale and the authorizing party
named ("the operator, at the Task 3 checkpoint"), satisfying D-16.4's evidentiary requirements.

### Gaps Summary

No gaps found. All three success criteria are met on evidence independently re-verified during this
session (not merely re-stated from SUMMARY.md):

1. **Silicon proof (criterion 1):** re-confirmed the M27C512's non-erasable classification directly
   against the live chip database (`firestarter info m27c512`) and the `FLAG_CAN_ERASE` derivation
   logic in `database.py`, and confirmed the cited commit SHAs (`af47bf4`, `e5842d8`) exist and match
   their stated messages.
2. **Unchanged whole-device paths (criterion 2):** re-ran the native characterization suite and the
   new source-contract gate; both pass, and the bench record's own transcripts show byte-identical
   standalone blank-check output before and after the fix.
3. **RED-before-GREEN regression (criterion 3):** traced the RED transcript in `201-02-SUMMARY.md`
   and the GREEN transcript in `201-03-SUMMARY.md`, and confirmed both tests still exist and pass in
   the current tree, plus the host-side equivalent.

Two non-blocking code-review WARNINGs (WR-01, WR-02) remain open as follow-up items; neither
undermines a must-have or a success criterion.

---

_Verified: 2026-09-20T09:47:54Z_
_Verifier: Claude (gsd-verifier)_
