---
phase: 194-real-page-size-reaches-the-firmware
verified: 2026-09-15T00:00:00Z
status: passed
score: 4/4 must-haves verified
covered_files: [".planning/REQUIREMENTS.md", ".planning/phases/194-real-page-size-reaches-the-firmware/194-01-PLAN.md", ".planning/phases/194-real-page-size-reaches-the-firmware/194-01-SUMMARY.md", ".planning/phases/194-real-page-size-reaches-the-firmware/194-02-PLAN.md", ".planning/phases/194-real-page-size-reaches-the-firmware/194-02-SUMMARY.md", ".planning/phases/194-real-page-size-reaches-the-firmware/194-03-PLAN.md", ".planning/phases/194-real-page-size-reaches-the-firmware/194-03-SUMMARY.md", ".planning/phases/194-real-page-size-reaches-the-firmware/194-04-PLAN.md", ".planning/phases/194-real-page-size-reaches-the-firmware/194-04-SUMMARY.md", ".planning/phases/194-real-page-size-reaches-the-firmware/194-05-PLAN.md", ".planning/phases/194-real-page-size-reaches-the-firmware/194-05-SUMMARY.md", ".planning/phases/194-real-page-size-reaches-the-firmware/194-06-PLAN.md", ".planning/phases/194-real-page-size-reaches-the-firmware/194-06-SUMMARY.md", ".planning/phases/194-real-page-size-reaches-the-firmware/194-07-PLAN.md", ".planning/phases/194-real-page-size-reaches-the-firmware/194-07-SUMMARY.md", ".planning/phases/194-real-page-size-reaches-the-firmware/194-CONTEXT.md", ".planning/phases/194-real-page-size-reaches-the-firmware/194-REVIEW.md", ".planning/phases/194-real-page-size-reaches-the-firmware/deferred-items.md", ".planning/v1.39/194-page-size-27-row-record.md", ".planning/v1.39/194-w29c020-bench-transcript.md", "firestarter_app/firestarter/cli_handlers.py", "firestarter_app/firestarter/constants.py", "firestarter_app/firestarter/data/chip_database.json", "firestarter_app/firestarter/database.py", "firestarter_app/firestarter/eprom_operations.py", "firestarter_app/firestarter/exceptions.py", "firestarter_app/firestarter/messages.py", "firestarter_app/firestarter/page_size_gate.py", "firestarter_app/tests/golden/chip_database_field_inventory.json", "firestarter_app/tests/golden/wire_dict_expected_deltas_194.json", "firestarter_app/tests/test_page_size_invariants.py", "firestarter_app/tests/test_page_size_write_refusal.py", "firestarter_app/tests/test_vcc_margin_rail.py", "firestarter_app/tests/test_wire_dict_equivalence.py", "firestarter_app/tools/build_db.py", "firestarter_fw/include/firestarter.h", "firestarter_fw/include/messages.h", "firestarter_fw/src/json_parser.c", "firestarter_fw/src/proms/flash_5v_page.cpp", "firestarter_fw/test/native/avr/_shared/host_stubs_common.inc", "firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp", "tools/catalog/messages.toml"]
covered_digest: "v1:sha256:734eed7626a305bcc6425e1e29e529f65d7a2bfd036a5781227e74cac3a4293f"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 194: Real Page Size Reaches the Firmware Verification Report

**Phase Goal:** The protocol `0x05` write path uses each part's recorded page size. It does not
use a value derived from total device size. This is true across all 27 parts, not just the 9
known to be wrong.

**Verified:** 2026-09-15
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The page size used by `flash_5v_page_write_execute` originates in the chip database, not a size-bracket derivation | ✓ VERIFIED | `firestarter_fw/src/proms/flash_5v_page.cpp:75-79` reads only `handle->page_size`, via `flash_5v_page_mask()`. The old bracket function `flash_5v_page_page_size(mem_size)` (`<=65536→64 / <=262144→128 / else→256`) no longer exists in the firmware tree. `grep -rn "flash_5v_page_page_size"` across `firestarter_fw/src` and `firestarter_fw/include` returns nothing. `handle->mem_size` is never read in the write-execute function body — confirmed by direct read. Only `handle->page_size`, `handle->address`, `handle->data_size`, and `handle->data_buffer` are used. |
| 2 | For all 27 protocol-`0x05` parts, the firmware-used page size equals the part's recorded real page. This is measured across the whole set, not asserted for the 9 alone. The other 18 do not regress. | ✓ VERIFIED | Independently re-derived, not trusted from the phase's own record. A live read of `firestarter_app/firestarter/data/chip_database.json` (verifier's own `python3` script, this session) shows 746 total rows, 45 rows carrying `programming.page_size`, and exactly 27 `algorithm: 5` rows. Every one of the 27 has `page_size == infoic_page_size_raw`, and every value is a power of two in [1,512]. The verifier separately reimplemented the exact removed firmware bracket function, read from `git show d8cf708:src/proms/flash_5v_page.cpp`, and ran it against all 27 rows' `electrical.size_bytes`. That reproduces exactly 18 "equal" and 9 "under 2×" rows. The 9 named parts match `.planning/v1.39/194-page-size-27-row-record.md` §2 exactly. The firmware native suite was re-run this session (`pio test -e native`): 208/208 passed. This includes 7 distinct `(mem_size, page_size)` boundary cases and one case that deliberately supplies a wrong `mem_size`, proving capacity plays no role at runtime. Four host test files were re-run this session: 34/34 passed. |
| 3 | A contiguous multi-page write to one of the 9 previously under-sized parts reads back byte-identical on real silicon, with the transcript committed | ✗ NOT MET, by design (D-10/D-11). The honesty of the record was confirmed instead. | `.planning/v1.39/194-w29c020-bench-transcript.md` is committed and documents a real bench run. The part run was `W29C020` — row 24 of the 27-row record. `W29C020` is one of the **18 already-correct** parts, not one of the 9. The transcript's own §5 states this plainly. It quotes the run as "structurally incapable of proving any of the 9 were fixed, because `W29C020`'s derived page size was never wrong." `.planning/REQUIREMENTS.md` PAGE-03 is marked `[ ]` (open). Its status note states the same caveat. No sentence in either document implies a part from the 9 was confirmed. |
| 4 | The record states which of the 9 were exercised on hardware, and which rest on the database comparison alone. The two are not conflated. | ✓ VERIFIED | `194-page-size-27-row-record.md` §2 states "0 of 9 on hardware, 9 of 9 on the database comparison" and names all 9 parts. `194-w29c020-bench-transcript.md` §5 repeats the same 9-part list and the same "0 of 9" statement, and cites the record. `REQUIREMENTS.md`'s PAGE-03 status note repeats the same split a third time. All three documents agree. Native and database evidence covers all 27 parts. Real-silicon no-regression evidence covers one of the 18. The two evidence classes are never merged into a single claim in these three artifacts. |

**Score:** 3 of 4 truths pass outright. Truth 3 is an intentionally-unmet criterion. Its
must-have was the honesty of the record, not the outcome — that must-have is met. Overall
must-have coverage: 4/4.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_fw/src/proms/flash_5v_page.cpp` | Consumes `handle->page_size` only. Old derivation removed. Fail-closed refusal. | ✓ VERIFIED | `flash_5v_page_mask()` enforces power-of-two ≤512 and rejects 0. `flash_5v_page_page_size()` is absent. The refusal path sets `RESPONSE_CODE_ERROR` and returns before any register write. |
| `firestarter_app/tools/build_db.py` | No part-keyed page-size table. Provenance-keyed emit. Fail-closed validator. | ✓ VERIFIED | `_PAGE_SIZE_BY_PART` is absent — grep finds no definition. The emit arm keys on `_upstream_proto_id in (0x0D, 0x05)`. A whole-database validator raises `ValueError` on any emitted `page_size` that is not a power of two in range. |
| `firestarter_app/firestarter/page_size_gate.py` | `require_page_size` pre-connect refusal | ✓ VERIFIED | Present as a pure predicate. Called from both `eprom_operations.py:2009` and `cli_handlers.py:764`, before `_operation_context` or the port opens. |
| `firestarter_app/firestarter/exceptions.py` | `PageSizeUnavailableError` | ✓ VERIFIED | Defined at line 92, a subclass of `EpromOperationError`. |
| `.planning/v1.39/194-page-size-27-row-record.md` | 27-row measurement, evidence-class split | ✓ VERIFIED | All 27 rows match the independently re-derived data. §2 states "0 of 9 on hardware, 9 of 9 on the database comparison." |
| `.planning/v1.39/194-w29c020-bench-transcript.md` | Committed silicon transcript, honest scope | ✓ VERIFIED | Chip-ID confirmed, not the printed marking. A 2048-byte, 16-page pattern gives a byte-identical read-back. The app's own `verify` subcommand also reports success, an independent path to the same result. §5 states plainly that the run does not apply to the 9. |
| `firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` | 7 boundary cases, one wrong-`mem_size` case, 4 refusal cases, one positive control | ✓ VERIFIED | All present in the `RUN_TEST` list: the 7 `test_5v_page_write_execute_boundary_*` cases, `..._ignores_mem_size_entirely`, the four `..._refuses_*` cases, and `..._positive_control_valid_page_size`. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `chip_database.json` (`programming.page_size`) | wire `page-size` key | `database.py` `_map_data`/`convert_to_programmer` | ✓ WIRED | `194-w29c020-bench-transcript.md` §4a shows the host resolving and using the database row directly. `test_wire_dict_equivalence.py` (re-run, passed) proves the delta layer for all 25 newly-emitting rows. |
| wire `page-size` | `handle->page_size` | `json_parser.c` FIELD row, reset to 0 per command | ✓ WIRED | `json_parser.c:151` `FIELD(key_page_size, page_size, 0)`. `:275` resets it per command. |
| `handle->page_size` | write-loop page arithmetic | `flash_5v_page_mask()` inside `flash_5v_page_write_execute` | ✓ WIRED | Confirmed by direct code read. Native boundary tests pass. |
| host pre-flight gate | operator write call | `require_page_size()`, called before `_operation_context` or the serial port opens | ✓ WIRED | Grep-confirmed call sites in both `eprom_operations.py` and `cli_handlers.py`. `test_page_size_write_refusal.py` proves no port opens on refusal (re-run, passed). |

### Behavioral Spot-Checks / Test Re-Runs

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Firmware native suite, re-run this session (not trusted from SUMMARY) | `pio test -e native` | 208/208 succeeded | ✓ PASS |
| Host page-size test files, re-run this session | `pytest tests/test_page_size_invariants.py tests/test_page_size_write_refusal.py tests/test_wire_dict_equivalence.py tests/test_vcc_margin_rail.py -o addopts="" -q` | 34 passed | ✓ PASS |
| Old-derivation reproduction against all 27 rows (verifier's own script, not sourced from any phase artifact) | ad hoc `python3` script reimplementing the removed bracket function | 18 equal, 9 under. Exact part-name match to the record. | ✓ PASS |
| Debt-marker scan of all files this phase touched | `grep -n -E "TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER"` | no matches | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| PAGE-01 | 194-01, 194-02, 194-05, 194-06 | Page size from database, not device-size derivation | ✓ SATISFIED | Marked `[x]` in REQUIREMENTS.md. Code and test evidence above confirm it. |
| PAGE-02 | 194-01, 194-02, 194-03, 194-04, 194-06 | Measured correct across all 27. No regression on the 18. | ✓ SATISFIED | Marked `[x]`. The independently re-derived 27-row split matches exactly. |
| PAGE-03 | 194-06, 194-07 | Silicon read-back for one of the 9 | ✗ INTENTIONALLY OPEN | Marked `[ ]`, correctly. This is a hardware-gated deferral (D-10/D-11), honestly documented. A W29C512 is on order. |

No orphaned requirements. `.planning/REQUIREMENTS.md`'s PAGE section maps exactly to
PAGE-01/02/03, all declared across the 7 plans' `requirements:` frontmatter.

### Anti-Patterns Found

None. The debt-marker scan covered every file this phase touched — firmware, host, tests, and
planning artifacts. It returned zero matches for `TBD`, `FIXME`, `XXX`, `TODO`, `HACK`, or
`PLACEHOLDER`.

### Known Reviewed Findings (not gaps)

- `194-REVIEW.md` WR-01: the host `page_size_gate.py` checks only truthiness, not
  power-of-two-≤512. A bad `~/.firestarter/database.json` override would pass the host gate and
  fail only in the firmware. Confirmed present in code. Deliberately deferred, and filed at
  `.planning/todos/pending/host-page-size-gate-accepts-invalid-values.md`. This is not a
  phase-goal blocker: the generator's own fail-closed validator guarantees the shipped database
  never contains such a value. Only a hand-edited user override is affected, and that is a
  pre-existing class of risk this phase does not introduce.
- `194-REVIEW.md` WR-02 (the generator aborts the whole build rather than skip-and-warn on one bad
  upstream `page_size` of 0), and IN-01/IN-02: reviewed, no action required in this phase, and
  correctly not re-raised as new gaps here.

### Human Verification Required

None. Every criterion resolves to VERIFIED, except criterion 3, which resolves to a correctly
and honestly documented deliberate non-completion, per the phase's own explicit design (D-10,
D-11). No item needs a human judgment call beyond what REQUIREMENTS.md and the transcript already
record plainly.

### Gaps Summary

No gaps. All four success criteria were confirmed against the codebase directly, not against
SUMMARY.md claims:

1. **Criterion 1** (page size originates in the database): verified by reading the firmware
   source. The old derivation function is fully removed and unreferenced.
2. **Criterion 2** (all 27 measured, no regression on the 18): verified by an independent
   re-derivation from the live `chip_database.json`, plus a from-scratch reimplementation of the
   deleted bracket function. Both match the phase's own record exactly. The native and host test
   suites were also re-run fresh.
3. **Criterion 3** (silicon read-back on one of the 9): genuinely not met, as designed. Per D-10,
   no part from the 9 was on the bench, and a W29C512 is on order. Verified that neither the
   transcript nor REQUIREMENTS.md overstates what was actually run.
4. **Criterion 4** (evidence classes not conflated): verified across three independent
   documents — the 27-row record, the bench transcript, and REQUIREMENTS.md itself. All three
   state "0 of 9 on hardware, 9 of 9 on the database comparison" consistently.

The phase goal is achieved and independently confirmed: protocol `0x05` writes use the database
page size across all 27 parts, not a capacity-derived guess. PAGE-03's hardware leg is correctly
and honestly left open, pending hardware arrival. This is the intended, documented phase boundary
(D-11), not a gap.

---

_Verified: 2026-09-15_
_Verifier: Claude (gsd-verifier)_
