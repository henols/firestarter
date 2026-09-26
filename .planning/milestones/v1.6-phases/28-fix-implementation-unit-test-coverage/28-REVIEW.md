---
phase: 28-fix-implementation-unit-test-coverage
reviewed: 2026-05-26T00:00:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - firestarter/src/boards/leonardo_rurp_shield.cpp
  - firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp
findings:
  critical: 0
  warning: 0
  info: 3
  total: 3
status: issues_found
---

# Phase 28: Code Review Report

**Reviewed:** 2026-05-26
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found (Info-only — no Blockers, no Warnings)

## Summary

This phase is a desk-side **revert** of the broken Phase 28 v1 fix
(`437339b6` — "clear PORTD/PORTC/PORTE data-bit pullups in
rurp_set_data_input"), paired with a manual prune of the now-obsolete Unity
test case that asserted the reverted behavior. The revert is **mechanically
clean**:

1. `leonardo_rurp_shield.cpp::rurp_set_data_input()` matches its
   pre-Phase-28 shape (`fdb1ed5`) **exactly** — DDRx-clears only, no PORTx
   writes. Confirmed via `git diff fdb1ed5 HEAD -- src/boards/leonardo_rurp_shield.cpp`:
   the *only* delta from baseline is the two `_NOP()` settling delays in
   `rurp_read_data_buffer` (commit `4f205e58`, intentionally retained per
   phase context: Plan 28-04 stays drafted-but-not-executed).
2. The deleted `test_rurp_set_data_input_clears_data_pullups_leonardo`
   function and its `RUN_TEST(...)` invocation are both gone. No stale
   `extern`, forward declaration, or symbol leak in the source file or
   `host_stubs.cpp`. `pio test -e native -f "*test_data_input*"` passes
   1/1 locally (matches phase context claim).
3. No other file in `firestarter/src/` or `firestarter/test/` references
   the deleted test name.

The three Info findings below are all **documentation hygiene** — stale
comments inside the surviving test file that still describe the deleted
test and the now-abandoned "Wave A / Wave B / FIX-02" RED-bar narrative.
None affect correctness or test-pass status. They're worth listing
because future readers of `test_rurp_set_data_input.cpp` will be
confused by a 35-line header docstring that describes two RUN_TEST
cases when only one survives.

No security issues, no AVR-register correctness issues, no undefined
behavior, no memory safety concerns. Per the adversarial stance: I
specifically looked for (a) a `PORTD &= ~PORTD_DATA_MASK` left
dangling after the revert, (b) a forgotten `_NOP()` removal that would
have re-opened the read-buffer regression, (c) `_BV(5)` / `_BV(6)`
typos in `rurp_write_data_buffer` that the revert might expose, and
(d) any `extern` declaration of the deleted Unity function in
`host_stubs.cpp` or a sibling TU. None found.

## Info

### IN-01: Stale file-header docstring describes the deleted test

**File:** `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp:7-25`
**Issue:** The file's top-of-file docstring still announces "**Two**
Unity RUN_TEST cases under the include-as-source pattern" and then
enumerates them as items `1.` and `2.` — but item 1
(`test_rurp_set_data_input_clears_data_pullups_leonardo`) was deleted
in commit `efd203a`. A reader scanning the file header in isolation
will be told there are two tests, then read the body and find only
one. The "FIX-02 first half" / "RED-bar witness" / "Pre-fix code at
src/boards/leonardo_rurp_shield.cpp lines 137-141" wording also
refers to a code shape (PORTx-clear) that no longer exists in the
production source and was deliberately reverted as harmful.

**Fix:** Rewrite the file-header docstring (lines 7-42) to reflect
the post-revert reality. A minimal version:
```cpp
/*
 * Phase 28 re-iteration — regression guard for rurp_read_data_buffer.
 *
 * Native-host Unity test using the include-as-source pattern
 * (RESEARCH.md Q2 Option D + PATTERNS.md Excerpt 2). One RUN_TEST
 * case:
 *
 *   test_rurp_read_data_buffer_reassembles_data_bus
 *      Regression guard around rurp_read_data_buffer()'s shift-and-
 *      mask reassembly logic. Guards against accidentally breaking
 *      the bit map while editing the read function (e.g. the _NOP()
 *      settling delays added by commit 4f205e58).
 *
 * Phase 28 v1 also carried a test_rurp_set_data_input_clears_data_
 * pullups_leonardo case asserting that rurp_set_data_input() clears
 * PORTx data bits. That fix was reverted in commit ea25174 after
 * bench verification showed it caused a 99%-zeros regression on
 * Leonardo (Plan 27-05 verdict); the corresponding test was pruned
 * with it.
 *
 * Native-test integration uses the include-as-source pattern: this
 * TU #defines ARDUINO_AVR_LEONARDO and then #includes the production
 * Leonardo board source directly. See PATTERNS.md Excerpt 2.
 *
 * RCA: .planning/v1.6-EVIDENCE.md §"Phase 27 — RCA Findings".
 */
```

### IN-02: Stale "Wave A / Wave B" terminology inside surviving test docstring

**File:** `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp:94-100`
**Issue:** The block comment above `test_rurp_read_data_buffer_reassembles_data_bus`
still says "Wave B Commit 2 inserts _NOP() settling delays" and
"Guards against accidentally breaking the bit map while editing the
read function". The "Wave A / Wave B" split is Phase 28 v1
plan-internal language; after the revert, `4f205e58` is just "the
_NOP fix" with no Wave/Commit numbering. Doesn't affect compilation
or test pass-rate, but it ties this file to a discarded plan
structure.

**Fix:** Replace "Wave B Commit 2" with "commit 4f205e58" (the
SHA-named, plan-independent anchor). Suggested:
```cpp
/* ----------------------------------------------------------------
 * Regression guard for rurp_read_data_buffer bit-mapping.
 *
 * The bit-mapping logic at leonardo_rurp_shield.cpp:128-138 is
 * unchanged across the Phase 28 _NOP-settling commit (4f205e58)
 * and its revert. This case guards against accidentally breaking
 * the shift-and-mask reassembly while editing the read function.
 * ...
```

### IN-03: Stale line-number references inside test docstring

**File:** `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp:52-53, 97, 102`
**Issue:** The comments reference specific line numbers in
`leonardo_rurp_shield.cpp` that no longer match the post-revert
source:
- Line 52-53: "uses _BV extensively at lines 96-104 (rurp_write_data_buffer) and 119-126 (rurp_read_data_buffer)" — `rurp_read_data_buffer` is now at lines 112-139 (the `_NOP()` insertions + the longer datasheet-citation comment shifted everything down).
- Line 97: "bit-mapping logic at lines 119-126 is unchanged" — the bit-mapping block is now at lines 128-138.
- Line 102: "Bit map (per leonardo_rurp_shield.cpp:119-126)" — same drift.

These are not bugs (the file still compiles, the test still passes),
but the line-number citations will mislead anyone using them to
navigate the source.

**Fix:** Either (a) update the line numbers to match current source
(128-138 for the bit-mapping block; 112-139 for the full
`rurp_read_data_buffer`; the _BV usage now spans lines 96-110 and
129-136), or (b) drop the line numbers entirely and reference by
function name only — more drift-resilient. Recommended approach
(b):
```cpp
/* ...the included leonardo_rurp_shield.cpp uses _BV extensively in
 * rurp_write_data_buffer and rurp_read_data_buffer, so we must
 * define it before the source-include. */
```

---

## Notes on what I checked and found CLEAN

These are not findings — they're explicit nulls so the next reviewer
doesn't re-walk the same ground:

- **Revert completeness vs `fdb1ed5`:** `diff <(git show HEAD:src/boards/leonardo_rurp_shield.cpp) <(git show fdb1ed5:src/boards/leonardo_rurp_shield.cpp)` shows the only delta is the two `_NOP()` calls + the explanatory comment block in `rurp_read_data_buffer`. The `rurp_set_data_input` function is byte-for-byte identical to baseline. Clean.
- **No orphaned references to deleted test:** `grep -rn "test_rurp_set_data_input_clears_data_pullups_leonardo" firestarter/` returns exactly one hit — line 13 of the test file itself, inside the stale file-header docstring (covered by IN-01). No `extern`, no `RUN_TEST`, no forward declaration anywhere else.
- **`host_stubs.cpp` consistency:** The stub file at `test/native/avr/test_data_input/host_stubs.cpp` is unchanged and still link-clean — its only stubs are `Serial_::operator bool`, `rurp_read_voltage_mv`, and `rurp_get_config`. None of these reference the deleted test, and all are still needed (`rurp_get_config` is pulled in by the header-inlined `rurp_get_hardware_revision`, etc.).
- **No `_BV` typos in `rurp_write_data_buffer`:** Re-checked the bit map at lines 96-104. `D0→PD2` shifts by 2, `D2→PD1` shifts right by 1, `D3→PD0` shifts right by 3 — all consistent with the matching read at lines 129-136. The revert does not expose any pre-existing bit-map bug.
- **AVR register safety:** All `PORTx` / `DDRx` / `PINx` accesses are masked read-modify-write (`PORT = (PORT & ~MASK) | val`). No bare `PORTx = X` assignments that would clobber neighboring control pins (D12/D13 on PORTD/PORTC). The Uno-side `rurp_set_data_input` at `uno_rurp_shield.cpp:120-129` uses a bare `PORTD = 0x00` and IS clean only because Uno has no control-pin overlap with PORTD; the Leonardo's PORTD bit 6 = D12 control line is exactly why the pullup-clear sketch was harmful and had to be reverted. The current Leonardo code's DDRx-only-clear preserves that invariant.
- **Unit test still passes:** `pio test -e native -f "*test_data_input*"` reports `1 test cases: 1 succeeded in 00:00:00.711` (matches phase-context claim of 1 PASS / 0 FAIL).
- **No new `console.log`-equivalent / debug artifacts:** No `Serial.print*`, no `LOG_DEBUG_MSG`, no `#warning`, no `TODO`/`FIXME`/`XXX`/`HACK` inserted by this phase's edits.
- **No security surface:** Pure AVR register manipulation in a host-stubbed unit test + a hardware-driver `void → void` function. No string handling, no parsing, no I/O.

---

_Reviewed: 2026-05-26_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
