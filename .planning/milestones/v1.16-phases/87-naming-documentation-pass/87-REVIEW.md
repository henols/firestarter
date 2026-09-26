---
phase: 87-naming-documentation-pass
reviewed: 2026-06-26T00:00:00Z
depth: standard
files_reviewed: 14
files_reviewed_list:
  - firestarter/src/firestarter.cpp
  - firestarter/src/proms/eeprom_28c.cpp
  - firestarter/src/proms/eprom.cpp
  - firestarter/src/proms/flash_intel.cpp
  - firestarter/src/proms/flash_type_3.cpp
  - firestarter/src/proms/flash_type_4.cpp
  - firestarter/src/proms/flash_utils.cpp
  - firestarter/src/proms/memory.cpp
  - firestarter/src/proms/not_implemented.cpp
  - firestarter/src/proms/sram.cpp
  - firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp
  - firestarter/test/native/avr/test_val_flash3/test_val_flash3.cpp
  - firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp
  - firestarter/test/native/avr/test_val_sram/test_val_sram.cpp
findings:
  critical: 0
  warning: 3
  info: 5
  total: 8
status: issues_found
---

# Phase 87: Code Review Report

**Reviewed:** 2026-06-26
**Depth:** standard
**Files Reviewed:** 14
**Status:** issues_found

## Summary

Phase 87 is a frozen-world naming + documentation pass. The review confirmed
the two structural claims of the phase and then adversarially examined the new
test assertions:

1. **Frozen-world holds.** All 10 `src/` handler files received comment-only
   changes. I filtered every added/removed line through a comment-stripping
   grep across the full diff (`bddb8ee^..HEAD`) and found zero non-comment
   added or deleted lines in any of the 10 handler files — including
   `flash_type_4.cpp`, which shows `9 deletions` in the diffstat purely because
   an old comment block was replaced by a longer one. No executable, PROGMEM,
   or PSTR code changed. This matches the 0-byte Leonardo flash-delta gate
   (`.flash-baseline-87.txt` = 25654).

2. **The 9 new test assertions compile and pass.** I built and ran the four
   affected native suites (`pio test -e native`); all 33 cases pass including
   INV-01..INV-09. The INV-03 (P1-as-VPP flip), INV-04 (256B page-size
   discrimination), and INV-06 (per-protocol pulse-delay defaults) tests are
   genuinely discriminating — they would go RED on a real regression, and I
   traced each against the actual handler source to confirm the asserted
   side-effect path is reachable and non-tautological.

The findings below are quality issues, not correctness defects. The most
material is **INV-08**, whose test cannot actually detect the regression it
claims to guard (the WARNING-5 reclassification lives in host-side Python, not
firmware), so it is effectively a duplicate of the existing 0x07 dispatch test
under a misleading name. No BLOCKER-class issues were found.

## Warnings

### WR-01: INV-08 test does not exercise the invariant it claims to cover

**File:** `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp:419-441`
**Issue:** `test_inv08_eprom_warning5_decode_preserved` claims to verify that the
Phase-86 variant decode correctly classifies UV-EPROM (0x07) vs 28C EE-EPROM
(0x0D) parts and that "WARNING-5 has not re-activated". But WARNING-5 was a
host-side `build_db.py` Rule-2 reclassification — it lives entirely in the
Python DB-generation layer, not in the firmware. The test only asserts that
firmware dispatch of `protocol==0x07` reaches `configure_eprom` and wires
`firestarter_operation_main` (and the same for CMD_READ). That dispatch is a
frozen structural fact in `memory.cpp:121-124`; the test can never go RED for a
WARNING-5 regression because no Phase-86 logic exists in the firmware to break.
It is functionally a duplicate of the existing dispatch coverage, dressed in an
INV-08 name. This risks giving false confidence that INV-08 is firmware-tested.
**Fix:** Either (a) demote the comment to state plainly that this only pins the
0x07→`configure_eprom` firmware dispatch arm and that the actual WARNING-5
decode invariant is covered by a host-side Python test (cite that test), or
(b) move the INV-08 traceability assertion to the host-side `build_db.py` /
`classify()` test suite where the decode actually executes. As written, the
comment overstates what is verified.

### WR-02: INV-09 CMD_ERASE branch tests only configure, not the erase execute path

**File:** `firestarter/test/native/avr/test_val_flash3/test_val_flash3.cpp:155-163`
**Issue:** The INV-09 test's second block is commented "Repeat for CMD_ERASE to
confirm the full 0x06 dispatch stays in flash3", but it only calls
`configure_memory(&he)` and `assert_no_vpp_in_recording()`. It never invokes
`he.firestarter_operation_main`, so the flash3 erase *execute* path is never
exercised. The claim "full 0x06 dispatch" overstates the coverage: the erase
handler itself (`flash3_erase_execute`, which does write CTL bits) is not
verified to be VPP-safe by this assertion. The flash4 sibling test (INV-04)
correctly drives `firestarter_operation_main`; this one does not.
**Fix:** Either correct the comment to say "configure-phase only" (matching what
the code does), or extend the test to call `he.firestarter_operation_main(&he)`
after a `clear_bus_recording()` and re-assert no-VPP across the erase execute
phase (mirroring INV-04's pattern). Prefer the latter so the assertion matches
its stated intent.

### WR-03: INV-06 default-pulse-delay header comment cites the wrong source lines

**File:** `firestarter/src/proms/eprom.cpp:39`
**Issue:** The INV-06 header block states "pulse-delay defaults per protocol
(configure_eprom() lines 70–76)". The actual default-setting switch is at
`eprom.cpp:118-124`; lines 70–76 are forward declarations. The corresponding
test comment (`test_val_eprom.cpp` INV-06) correctly cites lines 118–124, so the
two now disagree. Since the entire point of Phase 87 is durable naming/citation
accuracy that Phases 88-89 will rely on (SAFE-02 handoff contract), a wrong
line citation in the canonical handler header is a maintainability defect: it
points a future reader at the wrong code.
**Fix:** Update the eprom.cpp INV-06 header to cite lines 118–124 (or, better,
cite the function-and-symbol "the `pulse_delay==0` switch in `configure_eprom()`"
without a brittle line number, since line numbers rot on every edit).

## Info

### IN-01: INV-04 final comment contains abandoned reasoning (three rejected approaches)

**File:** `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp:256-289`
**Issue:** The INV-04 doc comment walks through three different test-design
approaches ("Better approach:", "Actually the cleanest...", "Distinguishing
proof:") before arriving at the one actually implemented (65 bytes from addr 0).
The abandoned-reasoning narrative — including a paragraph that concludes a
candidate approach gives "no discrimination on count alone" — is left inline.
It is correct but confusing: a reader must discard most of the comment to find
the operative rationale. The actual test logic is sound and discriminating
(verified: page_size=256 → 1 SDP, page_size=64 → 2 SDPs).
**Fix:** Trim the comment to the single final rationale (65-byte write from
addr 0, expected SDP count = 1, with the page_size=64 contrast). Move design
alternatives to the plan/summary artifact if they need preserving.

### IN-02: INV-09 comment names SST39SF040 but the handle is sized as a 512 KB AM29F040

**File:** `firestarter/test/native/avr/test_val_flash3/test_val_flash3.cpp:60-67,139`
**Issue:** The INV-09 test repeatedly references "SST39SF040" (a 512 KB / 4 Mbit
part) in its name and comments, but `make_handle()` sets `mem_size = 524288`
with the inline comment "512 KB (AM29F040)". SST39SF040 is also 512 KB so the
size is coincidentally fine, but the cited part name and the inline size comment
disagree. For a documentation-pass phase whose deliverable is naming accuracy,
this internal inconsistency is worth tidying. (Not a correctness issue —
`configure_flash3` does not branch on `mem_size`.)
**Fix:** Make the part name consistent — either rename the test/comments to
AM29F040, or update the `make_handle` inline comment to "(SST39SF040)".

### IN-03: flash4 recording buffer is near its 256-entry cap for the INV-04 path

**File:** `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp:328-348`
**Issue:** `HOST_STUBS_MAX_RECORDING` is 256 (`_shared/host_stubs_common.inc:55`).
The INV-04 65-byte write records roughly 6 (SDP) + 65×3 (set_data) + 3 (final
poll) ≈ 204 register writes after `clear_bus_recording()` — comfortably under
256 today, but with little headroom. If a future edit increases `data_size` in
this test or adds per-byte polling, the recording would silently truncate at
256 and `count_sdp_occurrences()` could under-count without any assertion
firing (the stub drops writes past the cap silently). Latent fragility, not a
current bug.
**Fix:** Add a guard assertion that `bus_recording_count() < HOST_STUBS_MAX_RECORDING`
(or `!= 256`) in the INV-04 test so a future overflow fails loudly rather than
silently changing the SDP count.

### IN-04: INV-01 header attributes the 0x0B VPP enable solely to eprom_write_execute()

**File:** `firestarter/src/proms/eprom.cpp:12-16`
**Issue:** The INV-01 header says the firmware sets CTRL_VPP_REGULATOR_ENABLE
"see eprom_write_execute()". The 0x0B direct-VPE regulator enable actually fires
in two places: `eprom_check_vpp()` (lines 266-268, reached via the init path the
INV-01 test exercises) and `eprom_write_execute()` (lines 192-201). The INV-01
test passes via the `eprom_check_vpp` path during `firestarter_operation_init`,
not via `eprom_write_execute`. Minor citation imprecision in the canonical
header.
**Fix:** Cite both `eprom_check_vpp()` and `eprom_write_execute()` for the 0x0B
direct-VPE regulator-enable, since the init-phase path goes through the former.

### IN-05: Phase-86 / host-decode claims embedded in firmware comments may rot

**File:** `firestarter/src/proms/eprom.cpp:48-53`, `firestarter/src/proms/sram.cpp:24-29`, `firestarter/src/proms/flash_type_3.cpp` (INV-09 block)
**Issue:** Several handler header blocks now assert host-side facts (e.g. FM1608
raw `type=4/proto=0x07/variant=0x4126 → algorithm=0x28`, "Phase 86 removed
build_db.py Rule 2", "the JSON algorithm field is 0x28"). These are accurate
today, but they couple firmware source comments to host-repo (`firestarter_app`)
DB-generation behavior that the firmware build can never verify. If the host
decode changes, these comments silently become wrong with no CI signal. This is
inherent to the cross-repo documentation goal, but worth flagging as
maintenance debt.
**Fix:** Where practical, point these comments at the authoritative host-side
artifact (e.g. "see firestarter_app classify() / DEC-05") rather than restating
the derived wire values inline, so there is a single source of truth to keep in
sync.

---

_Reviewed: 2026-06-26_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
