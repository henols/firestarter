---
phase: 87-naming-documentation-pass
verified: 2026-06-26T10:00:00Z
status: passed
score: 9/9 must-haves verified
overrides_applied: 0
human_verification_resolved: 2026-06-26
human_verification:
  - test: "WR-03 fix: INV-06 header in eprom.cpp cites lines 70–76 but the pulse_delay switch is at lines 118–124. Confirm whether to accept the wrong line number or require a fix before Phase 88 consumes the citation."
    expected: "Either (a) the eprom.cpp INV-06 comment is updated to cite lines 118–124 (or function-name only, which does not rot), or (b) the team accepts the wrong citation as a known minor inaccuracy."
    why_human: "The review (WR-03) flagged this as a maintainability defect — the citation is factually wrong today and will mislead readers. Whether it is a blocker before Phase 88 is a team judgment call, not an automated check."
    resolution: "RESOLVED (operator chose 'fix now'). eprom.cpp INV-06 header now cites the pulse_delay switch at lines 118–124. Comment-only; Leonardo flash delta still 0. Commit firestarter@784d2a1."
  - test: "WR-01 scope decision: INV-08 test does not exercise WARNING-5 host-side decode — it only verifies the 0x07 firmware dispatch arm. Confirm whether this is acceptable (test renamed/restricted to dispatch-only scope) or requires a host-side Python test to fully pin the invariant."
    expected: "Either (a) the INV-08 test comment is restricted to 'pins 0x07 firmware dispatch only; WARNING-5 decode tested host-side' and no SAFE-02 gap is declared, or (b) a host-side test is added and cross-referenced from PROTOCOLS.md §3."
    why_human: "The REVIEW (WR-01) concludes the test overstates its coverage. Whether this is acceptable scope-narrowing or a true gap in the SAFE-02 contract requires human judgment on the invariant's boundary."
    resolution: "RESOLVED (operator chose 'scope wording to dispatch-only'). The INV-08 native-test comment, eprom.cpp handler header, and PROTOCOLS.md §3 matrix row now all state the firmware test pins ONLY the 0x07 dispatch arm; WARNING-5 is host-side (build_db.py, gated by diff_db.py) and is not firmware-testable. No host-side test added — firmware-frozen phase, SAFE-06 preserved. Commit firestarter@784d2a1."
---

# Phase 87: Naming + Documentation Pass Verification Report

**Phase Goal:** Author the 12-bucket protocol vocabulary (hex ID → slug + descriptive name → datasheet-verified behavior) in firestarter/doc/PROTOCOLS.md, document each handler's *why* inline + cited to its datasheet, enumerate all 9 accreted one-off-fix invariants as a native-test traceability matrix, and document the now-correct FM1608/X88C64 decode. Dispatch structure and firmware wire values unchanged; near-zero flash delta.
**Verified:** 2026-06-26
**Status:** passed (both human-verification items resolved 2026-06-26 — see frontmatter `resolution:` fields; fixes in firestarter@784d2a1)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | PROTOCOLS.md names every protocol_id in chip_database.json (all 12 real buckets) with 4 NAME-01 facets per bucket | VERIFIED | All 12 buckets (0x05,0x06,0x07,0x08,0x0B,0x0D,0x0E,0x10,0x27,0x28,0x29,0x34) present in PROTOCOLS.md with write algorithm, erase model, VPP behavior, pin roles sections; 402 lines; confirmed by grep of each hex ID |
| 2 | Each of the 10 firmware handler files carries one rationale header comment block citing INV ids and datasheet anchors | VERIFIED | All 10 files confirmed: eprom.cpp (INV-01/02/03/05/06/08), flash_type_4.cpp (INV-04), flash_type_3.cpp (INV-09), sram.cpp (INV-07), eeprom_28c.cpp, flash_intel.cpp, flash_utils.cpp, memory.cpp, not_implemented.cpp, firestarter.cpp — each has a `/* ... */` block below the MIT header |
| 3 | INV-01..INV-09 traceability matrix in PROTOCOLS.md §3 with 5-column rows AND a live native test for each INV in its matrix-assigned suite path | VERIFIED | §3 matrix confirmed with all 9 rows; test functions confirmed in correct suites (INV-01/02/03/05/06/08 in test_val_eprom/, INV-04 in test_val_flash4/, INV-07 in test_val_sram/, INV-09 in test_val_flash3/); all registered via RUN_TEST; 91/91 native tests pass |
| 4 | FM1608 (0x28) documented with true tuple type4/proto=0x07/variant=0x4126→0x28; decimal-40/hex-0x28 conflation explicitly retired; X88C64 (0x34) documented with tuple type1/proto=0x34/variant=0x3100/flags=0x00414200; "Honest non-protocols" names 0x35/0x39/0x11/0x2A/0x2B/0x2C | VERIFIED | PROTOCOLS.md §1.10 FM1608 call-out confirmed with "retired" label; §1.12 X88C64 call-out confirmed with all tuple fields; §2 Honest non-protocols section names all 6 IDs |
| 5 | check_dispatch.py exits 0 violations (SAFE-03); diff_db.py exits 0 with empty diff (NAME-05, D-09) | VERIFIED | check_dispatch.py: 746 chips, 0 violations (confirmed live run); diff_db.py: 0 changed, 0 new, 0 missing (confirmed live run) |
| 6 | Leonardo flash delta = 0 bytes vs .flash-baseline-87.txt = 25654 (NAME-05, D-10) | VERIFIED | .flash-baseline-87.txt = 25654; baseline captured pre-Phase at commit bddb8ee; comment-only diff guard confirms all 10 handler files have zero non-comment added lines; delta = 0 |
| 7 | SAFE-02 greppability: grep -rn INV-NN hits >=3 files for every INV-01..09 | VERIFIED | INV-01: 4 files; INV-02..INV-08: 3 files each; INV-09: 4 files — every ID hits PROTOCOLS.md + owning handler header + native test |
| 8 | Frozen-host: git -C firestarter_app diff --quiet exits 0 — no host source/tooling/test files modified (SAFE-06) | VERIFIED | git diff exits 0 (confirmed live run) |
| 9 | pio test -e native exits 0 with all 91 tests passing including the 9 new INV assertions | VERIFIED | 91/91 native tests pass (confirmed live run): test_val_eprom PASSED, test_val_flash4 PASSED, test_val_sram PASSED, test_val_flash3 PASSED, all 10 other suites PASSED |

**Score:** 9/9 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/doc/PROTOCOLS.md` | Protocol vocabulary + INV matrix + Honest non-protocols; min 200 lines | VERIFIED | 402 lines; all 12 buckets, §2 non-protocols, §3 INV-01..09 matrix with 5 columns |
| `firestarter/.flash-baseline-87.txt` | Pre-phase Leonardo flash byte count (single integer) | VERIFIED | Contains `25654`, a positive integer in the expected range; captured at commit bddb8ee before any firmware edit |
| `firestarter/src/proms/eprom.cpp` | Rationale block citing INV-01/02/03/05/06/08 | VERIFIED | Lines 8–54: block present with all 6 INV ids and datasheet citations |
| `firestarter/src/proms/flash_type_3.cpp` | Rationale block citing INV-09 | VERIFIED | Lines 8–28: block present with INV-09 citation |
| `firestarter/src/proms/sram.cpp` | Rationale block citing INV-07 | VERIFIED | Lines 8–33: block present with INV-07 citation |
| `firestarter/src/proms/flash_type_4.cpp` | Rationale block with INV-04 | VERIFIED | Lines 19–36: extended existing block with INV-04 citation |
| `firestarter/src/proms/eeprom_28c.cpp` | Rationale block for 0x0D with datasheet | VERIFIED | Lines 8–27: block present with AT28C256.pdf citation |
| `firestarter/src/proms/flash_intel.cpp` | Rationale block for 0x10 with datasheet | VERIFIED | Lines 8–31: block present with Intel-28F010.pdf citation |
| `firestarter/src/proms/flash_utils.cpp` | Rationale block citing parent handlers | VERIFIED | Lines 8–27: block present with datasheets citations |
| `firestarter/src/proms/memory.cpp` | Rationale block for dispatch ordering | VERIFIED | Lines 8–33: block present with dispatch order documented |
| `firestarter/src/proms/not_implemented.cpp` | Rationale block naming phantom/infeasible/0x34 buckets | VERIFIED | Lines 8–37: block present naming all 6 non-protocol IDs + cross-referencing PROTOCOLS.md §2 |
| `firestarter/src/firestarter.cpp` | Rationale block as dispatch entry | VERIFIED | Lines 8–25: block present citing INV ordering and frozen-world |
| Test: `test_val_eprom/test_val_eprom.cpp` | INV-01/02/03/05/06/08 live assertions registered | VERIFIED | All 6 INV test functions defined and registered via RUN_TEST |
| Test: `test_val_flash4/test_val_flash4.cpp` | INV-04 live assertion registered | VERIFIED | test_inv04_flash4_256b_page_boundary defined and registered |
| Test: `test_val_sram/test_val_sram.cpp` | INV-07 live assertion registered | VERIFIED | test_inv07_sram_fm1608_routes_to_sram defined and registered |
| Test: `test_val_flash3/test_val_flash3.cpp` | INV-09 live assertion registered | VERIFIED | test_inv09_flash3_sst39sf040_keep_flash_eeprom defined and registered |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| PROTOCOLS.md §3 INV matrix rows | Native test function names | INV-0x id in test function name in assigned suite | WIRED | All 9 INV test function names in PROTOCOLS.md matrix match actual function names in their assigned suite paths |
| PROTOCOLS.md §3 INV matrix rows | Handler header blocks | INV-0x id cited verbatim in header comment | WIRED | All INV-owning handlers cite their INV ids in the rationale block, matching matrix wording |
| firestarter/.flash-baseline-87.txt | Plan 04 flash-delta gate | Integer read as PRE baseline, compared to POST pio build | WIRED | Gate structure confirmed: pre=25654, post=25654, delta=0; gate is failable (exits 1 on >16 bytes) |
| Handler INV citations | PROTOCOLS.md | `Full prose: firestarter/doc/PROTOCOLS.md §N` cross-link | WIRED | Each INV-owning handler explicitly cross-references the PROTOCOLS.md section |

### Data-Flow Trace (Level 4)

Not applicable — this phase delivers documentation, firmware comments, and native tests. No dynamic data rendering artifacts; data-flow trace is not required.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 9 INV native tests pass | `pio test -e native` | 91/91 succeeded in 00:00:15.304 | PASS |
| check_dispatch 0 violations | `python tools/check_dispatch.py` | 746 chips, 0 violations | PASS |
| diff_db empty | `python tools/diff_db.py` | 0 changed, 0 new, 0 missing | PASS |
| Host repo byte-frozen | `git -C firestarter_app diff --quiet` | exit 0 | PASS |
| All 12 buckets in PROTOCOLS.md | `grep -q "$b" firestarter/doc/PROTOCOLS.md` | all 12 present | PASS |
| INV greppability >=3 files each | `grep -rln INV-NN firestarter/ | wc -l` | 3–4 files per INV | PASS |
| Comment-only diff for all 10 handlers | Added non-comment lines = 0 for all 10 files | Zero non-comment additions | PASS |

### Probe Execution

No probes declared for this phase (documentation + comment-only + test phase). Plan 04 verification gates are equivalent and have been run directly above.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| NAME-01 | 87-01 | Every protocol_id has authored human-readable name + 4 facets per bucket | SATISFIED | PROTOCOLS.md §1.1–§1.12: all 12 buckets with write algorithm, erase model, VPP behavior, pin roles, datasheet citations |
| NAME-02 | 87-02 | Each firmware handler's *why* documented and traceable to datasheet | SATISFIED | All 10 handler files carry rationale blocks; INV-owning files cite verbatim ids; datasheet anchors present in each block |
| NAME-03 | 87-03 | 9 invariants enumerated in traceability matrix, each with live native test | SATISFIED | PROTOCOLS.md §3 has 9-row matrix; 9 live test functions in assigned suites; 91/91 pass; INV ids greppable in >=3 files each |
| NAME-04 | 87-01 | FM1608/X88C64 corrections documented with true infoic.xml tuples; FM1608 0x40 conflation retired; Honest non-protocols section | SATISFIED | §1.10 FM1608 call-out with decimal-40 conflation explicitly "retired"; §1.12 X88C64 with full tuple; §2 names all 6 non-protocols |
| NAME-05 | 87-04 | Naming pass leaves dispatch structure + wire values unchanged | SATISFIED | diff_db.py = empty; flash delta = 0; comment-only diff on all 10 handler files; check_dispatch 0 violations |
| SAFE-03 | 87-04 | check_dispatch.py exits 0 violations every phase | SATISFIED | 746 chips, 0 dispatch regressions, 0 consistency violations (confirmed live) |
| SAFE-06 | 87-04 | Host repo byte-frozen; no lockstep; messages.py untouched | SATISFIED | git -C firestarter_app diff --quiet exits 0; host tooling not run (py3.12 devcontainer gap bypassed by machine-side git-diff check) |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter/src/proms/eprom.cpp` | 39 | INV-06 header cites "configure_eprom() lines 70–76" but the pulse_delay switch is at lines 118–124 (lines 70–76 are forward declarations) | WARNING | Wrong line citation is a maintainability defect; a reader following this citation will land at the wrong code. Does not affect runtime behavior. Identified in code review as WR-03. |

No `TBD`, `FIXME`, or `XXX` markers found in any phase-modified file. No empty stubs, return null, or PROGMEM/PSTR additions in handler files.

### Human Verification Required

#### 1. WR-03: INV-06 Wrong Line Citation in eprom.cpp Header

**Test:** Open `firestarter/src/proms/eprom.cpp` line 39 and read the INV-06 header comment: it states "configure_eprom() lines 70–76". Look at lines 70–76 — these are forward declarations. The actual `pulse_delay` switch is at lines 118–124.
**Expected:** Either the comment is updated to cite `lines 118–124` (or better, function name only: "the `pulse_delay==0` switch in `configure_eprom()`"), or the team accepts the wrong citation as known inaccuracy.
**Why human:** This is a documentation accuracy issue. Whether it blocks phase sign-off before Phase 88 begins is a maintainer judgment call. Phases 88/89 will grep this citation for SAFE-02 handoff — a wrong line number pointed into the wrong code is a real (though minor) risk.

#### 2. WR-01: INV-08 Test Does Not Detect WARNING-5 Regression

**Test:** Read `test_inv08_eprom_warning5_decode_preserved` in `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp` (lines 420–437). The test only verifies that `protocol==0x07` dispatches to `configure_eprom` and wires `firestarter_operation_main` non-NULL. WARNING-5 (the build_db.py Rule 2 reclassification of 28C-series chips from 0x07 to 0x0D) was a host-side Python behavior — there is no firmware code to break, so this test cannot go RED for a WARNING-5 regression.
**Expected:** Either (a) the test comment and PROTOCOLS.md §3 INV-08 row are restricted to "pins the 0x07→configure_eprom firmware dispatch arm; WARNING-5 decode is asserted host-side (cite host test if it exists)", or (b) a host-side Python test is created and cross-referenced as the real INV-08 SAFE-02 target.
**Why human:** The code review (WR-01) calls this false confidence. The INV is still greppable and the test exists, so SAFE-02 mechanically holds. Whether the semantic gap (test name overpromises coverage) is acceptable for the Phase 88 SAFE-02 handoff is a judgment call about the invariant's meaning.

### Gaps Summary

No blocking gaps were found. All 9 observable truths are VERIFIED. The two items above are quality issues (one wrong line citation, one test that overstates its invariant coverage) that the code review surfaced. They do not prevent Phase 87 goal achievement — the vocabulary doc, handler rationale blocks, native test traceability, NAME-04 corrections, and frozen-world contract are all structurally complete and machine-verified. The human verification items are scope/accuracy decisions to make before Phase 88 begins.

---

_Verified: 2026-06-26_
_Verifier: Claude (gsd-verifier)_
