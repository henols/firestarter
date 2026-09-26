---
phase: 09-delete-old-log-macros-measure-flash-savings
plan: 04
type: execute
wave: 3
depends_on: [09-02-atomic-legacy-deletion-and-version-bump]
files_modified:
  - firestarter/test/native/avr/_shared/host_stubs_common.inc
autonomous: true
requirements:
  - LFW-03
requirements_addressed:
  - LFW-03
tags:
  - logging
  - tests
  - native-stubs
user_setup: []
must_haves:
  truths:
    - "host_stubs_common.inc no longer defines the 8 dead LOG_*_MSG PROGMEM string externs (lines 45-53 in pre-Phase-9 state)"
    - "host_stubs_common.inc no longer defines the dead rurp_log + rurp_log_P no-op stubs (lines 55-67 in pre-Phase-9 state)"
    - "The 4 per-suite host_stubs.cpp files (test_dispatch, test_messages, test_flash_intel_vpp, test_eeprom28c_chip_id) are unchanged — they #include the common .inc only"
    - "The surviving stubs at lines 69-170 of host_stubs_common.inc (rurp_write_to_register, rurp_read_from_register, etc.) are untouched"
    - "pio test -e native -f '*test_dispatch*' -f '*test_messages*' reports 22+ PASS (same as Phase 8 close)"
  artifacts:
    - path: "firestarter/test/native/avr/_shared/host_stubs_common.inc"
      provides: "Trimmed shared native-test stub (only ID-frame + register surfaces remain)"
      contains: "rurp_log_id"
  key_links:
    - from: "firestarter/test/native/avr/_shared/host_stubs_common.inc"
      to: "firestarter/include/rurp_shield.h"
      via: "the surviving rurp_log_id / rurp_log_id_wide stubs match the (preserved) production decls"
      pattern: "rurp_log_id"
---

<objective>
Trim the shared native-test stub file `firestarter/test/native/avr/_shared/host_stubs_common.inc` lines 45-67 to remove the 8 dead `LOG_*_MSG` PROGMEM string externs and the 2 dead `rurp_log` / `rurp_log_P` no-op stubs. After Plan 02 deleted the production-side symbols, these test-side stubs are dead-link material — the native build no longer references any of them. Implements decision D-03 from `09-CONTEXT.md`.

This plan depends on Plan 02 (the production deletion). Trying to land Plan 04 before Plan 02 would leave the production firmware still referencing `LOG_OK_MSG` / `rurp_log` etc., and the native build would lose its link-resolution. Plan 04 runs only after Plan 02's atomic deletion lands.

Purpose: keep the native test surface in sync with the production surface. The 8 LOG_*_MSG externs and the 2 rurp_log no-op stubs survived Phase 8 as a "delete them when the production symbols go" item; Phase 9 closes that loop.
Output: A single-file commit trimming `host_stubs_common.inc` lines 45-67. `pio test -e native -f '*test_dispatch*' -f '*test_messages*'` must report ≥ 22 PASS (unchanged vs Phase 8 close).
</objective>

<execution_context>
@/workspaces/firestarter_prom/.claude/get-shit-done/workflows/execute-plan.md
@/workspaces/firestarter_prom/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-CONTEXT.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-RESEARCH.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-PATTERNS.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-02-SUMMARY.md
@firestarter/CLAUDE.md
@firestarter/test/native/avr/_shared/host_stubs_common.inc

<interfaces>
<!-- Exact diff for host_stubs_common.inc lines 45-67. Source: 09-RESEARCH.md §"File-Fate Audits" → "host_stubs_common.inc — TRIM" + 09-PATTERNS.md §"Pattern Assignment 6". -->

Lines 45-67 (current state — block to delete):
```
/* PROGMEM log-tag strings — defined in src/logging.c on AVR; replicated here
 * so the [env:native] link finds them. The PSTR() macro in the pgmspace stub
 * is a no-op, so these are plain const char[] in the host binary. */
extern "C" {
const char LOG_OK_MSG[] PROGMEM = "OK";
const char LOG_INIT_DONE_MSG[] PROGMEM = "INIT";
const char LOG_MAIN_DONE_MSG[] PROGMEM = "MAIN";
const char LOG_END_DONE_MSG[] PROGMEM = "END";
const char LOG_INFO_MSG[] PROGMEM = "INFO";
const char LOG_DATA_MSG[] PROGMEM = "DATA";
const char LOG_WARN_MSG[] PROGMEM = "WARN";
const char LOG_ERROR_MSG[] PROGMEM = "ERROR";
}

/* rurp_log* — no-op on host. The dispatch tests never read serial output;
 * test_messages exercises rurp_log_id (binary frame path) which does not
 * route through these text-frame helpers. */
extern "C" void rurp_log(PGM_P type, const char* msg) {
    (void)type;
    (void)msg;
}

extern "C" void rurp_log_P(PGM_P type, PGM_P msg) {
    (void)type;
    (void)msg;
}
```

Lines 69-170 (surviving stubs — DO NOT touch):
- `rurp_write_to_register`, `rurp_read_from_register`, `rurp_set_data_*`, etc.
- The `PGM_P` typedef stays in scope (referenced by other AVR macros — DO NOT remove)
- The 4 per-suite `host_stubs.cpp` files each `#include "../_shared/host_stubs_common.inc"` and do not duplicate the symbols — no per-suite edits needed.

The 4 sibling `avr/pgmspace.h` shim files contain comment-only references to `rurp_log` / `rurp_log_P` (per 09-RESEARCH.md line 318); those are comments, not declarations. DO NOT edit the shim files.
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Delete the 8 LOG_*_MSG PROGMEM stubs + 2 rurp_log no-op stubs from host_stubs_common.inc</name>
  <read_first>
    - firestarter/test/native/avr/_shared/host_stubs_common.inc (read the whole file — it is ~170 lines; the deletion is at lines 45-67)
    - firestarter/test/native/avr/test_dispatch/host_stubs.cpp (read the file — ~36 lines — to confirm it only `#include`s the common .inc and does not duplicate symbols)
    - firestarter/test/native/avr/test_messages/host_stubs.cpp (same)
    - firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp (same)
    - firestarter/test/native/avr/test_eeprom28c_chip_id/host_stubs.cpp (same)
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-RESEARCH.md §"File-Fate Audits" → "host_stubs_common.inc — TRIM"
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-PATTERNS.md §"Pattern Assignment 6"
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-CONTEXT.md §"LFW-05 bootstrap path" → D-03
  </read_first>
  <files>firestarter/test/native/avr/_shared/host_stubs_common.inc</files>
  <behavior>
    - Before: lines 45-67 of `host_stubs_common.inc` contain the 8 `LOG_*_MSG` PROGMEM externs inside an `extern "C" { ... }` block + a comment paragraph above them, followed by the 2 `extern "C" void rurp_log(...)` / `extern "C" void rurp_log_P(...)` no-op stubs + their introductory comment paragraph
    - After: lines 45-67 are deleted in their entirety (23 lines including blank lines between the two sub-blocks)
    - The comment paragraph above line 45 ("PROGMEM log-tag strings — defined in src/logging.c on AVR...") is part of the deletion
    - The comment paragraph at lines 59-61 ("rurp_log* — no-op on host. The dispatch tests never read serial output...") is part of the deletion
    - All surviving stubs from line 69 onward are untouched
  </behavior>
  <action>
    At `firestarter/test/native/avr/_shared/host_stubs_common.inc:45-67`, delete the 23-line block exactly as shown in 09-RESEARCH.md §"File-Fate Audits" → "host_stubs_common.inc — TRIM" (the diff block reproduced in `<interfaces>` above). The deletion spans:

    - The 3-line comment paragraph starting `/* PROGMEM log-tag strings — defined in src/logging.c on AVR;`
    - The `extern "C" {` opening brace line
    - The 8 `const char LOG_*_MSG[] PROGMEM = "...";` lines (LOG_OK_MSG, LOG_INIT_DONE_MSG, LOG_MAIN_DONE_MSG, LOG_END_DONE_MSG, LOG_INFO_MSG, LOG_DATA_MSG, LOG_WARN_MSG, LOG_ERROR_MSG)
    - The `}` closing brace line
    - The blank separator line
    - The 3-line comment paragraph starting `/* rurp_log* — no-op on host.`
    - The 4-line `extern "C" void rurp_log(PGM_P type, const char* msg) { (void)type; (void)msg; }` block
    - The blank separator line
    - The 4-line `extern "C" void rurp_log_P(PGM_P type, PGM_P msg) { (void)type; (void)msg; }` block

    Do NOT delete anything from line 68 onward (the surviving register-surface stubs). Do NOT touch the `PGM_P` typedef (referenced by other AVR macros per 09-RESEARCH.md line 318). Do NOT touch any of the 4 per-suite `host_stubs.cpp` files (they only `#include` the common .inc and do not duplicate symbols).
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_prom/firestarter &amp;&amp; [ "$(grep -c 'LOG_OK_MSG\|LOG_INIT_DONE_MSG\|LOG_MAIN_DONE_MSG\|LOG_END_DONE_MSG\|LOG_INFO_MSG\|LOG_DATA_MSG\|LOG_WARN_MSG\|LOG_ERROR_MSG' test/native/avr/_shared/host_stubs_common.inc)" = "0" ] &amp;&amp; [ "$(grep -E 'rurp_log\(|rurp_log_P\(' test/native/avr/_shared/host_stubs_common.inc | wc -l)" = "0" ] &amp;&amp; grep -q 'rurp_write_to_register\|rurp_read_from_register' test/native/avr/_shared/host_stubs_common.inc &amp;&amp; pio test -e native -f '*test_dispatch*' -f '*test_messages*' 2>&amp;1 | tail -5 | grep -qE '(PASSED|22|23|24)'</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c 'LOG_OK_MSG' firestarter/test/native/avr/_shared/host_stubs_common.inc` returns 0
    - `grep -c 'LOG_INIT_DONE_MSG\|LOG_MAIN_DONE_MSG\|LOG_END_DONE_MSG\|LOG_INFO_MSG\|LOG_DATA_MSG\|LOG_WARN_MSG\|LOG_ERROR_MSG' firestarter/test/native/avr/_shared/host_stubs_common.inc` returns 0
    - `grep -E 'extern "C" void rurp_log\(|extern "C" void rurp_log_P\(' firestarter/test/native/avr/_shared/host_stubs_common.inc | wc -l` returns 0
    - The file still contains surviving stubs — verified by `grep -c 'rurp_write_to_register\|rurp_read_from_register' firestarter/test/native/avr/_shared/host_stubs_common.inc` returning ≥ 1
    - `cd firestarter && pio test -e native -f '*test_dispatch*' -f '*test_messages*'` reports ≥ 22 PASS (same as Phase 8 close per `09-RESEARCH.md` §"Validation Architecture")
    - The 4 sibling `host_stubs.cpp` files are unchanged (`git diff firestarter/test/native/avr/test_dispatch/host_stubs.cpp` and similar return empty)
  </acceptance_criteria>
  <done>
    - 23-line block at lines 45-67 of `host_stubs_common.inc` is deleted
    - Native dispatch + messages test suites both green (≥ 22 PASS)
    - The surviving register-surface stubs are untouched
    - LFW-03 closure: the last test-side references to `LOG_*_MSG` / `rurp_log` / `rurp_log_P` are gone
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| production source ↔ native-test stub | The `[env:native]` build cross-compiles `src/proms/*.cpp` against a stub layer. If the production source removes a symbol but the stub still defines it, the stub becomes dead-link material (no functional risk, just code smell). If the production source still requires a symbol but the stub removes it, the native link fails. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-09-04-01 | Denial of Service | Native link failure if Plan 04 runs before Plan 02 (production symbols still reference `LOG_*_MSG` etc.) | mitigate | `depends_on: [02]` in this plan's frontmatter forces Wave 3 ordering. Plan 02's atomic deletion must complete first. The acceptance criterion runs `pio test -e native` which would fail loudly if the production source still required any of the deleted symbols. |
| T-09-04-02 | Tampering | Accidental deletion of a surviving stub (e.g., `rurp_write_to_register`) during the lines 45-67 trim | mitigate | Task 1's acceptance criterion explicitly verifies the surviving stubs survive (`grep -c 'rurp_write_to_register\|rurp_read_from_register'` returns ≥ 1) AND the native test suite stays green. Any over-deletion would surface as a link failure or test failure. |
| T-09-04-03 | Information Disclosure | Comment-only references to `rurp_log` in the 4 sibling `avr/pgmspace.h` shim files become stale | accept | Per 09-RESEARCH.md line 318 the shim-file references are pure comments describing why `PGM_P` is needed. The `PGM_P` typedef stays in scope (referenced by other AVR macros). The stale comment is informational drift, not a functional issue. Optional Phase 10 cleanup item; not Phase 9 scope. |
</threat_model>

<verification>
### Plan-level acceptance gate

```bash
# 1. Zero LOG_*_MSG externs in the common stub
[ "$(grep -c 'LOG_OK_MSG\|LOG_INIT_DONE_MSG\|LOG_MAIN_DONE_MSG\|LOG_END_DONE_MSG\|LOG_INFO_MSG\|LOG_DATA_MSG\|LOG_WARN_MSG\|LOG_ERROR_MSG' firestarter/test/native/avr/_shared/host_stubs_common.inc)" = "0" ] || { echo "FAIL: LOG_*_MSG still present"; exit 1; }
# 2. Zero rurp_log / rurp_log_P stub definitions
[ "$(grep -E 'extern "C" void rurp_log\(|extern "C" void rurp_log_P\(' firestarter/test/native/avr/_shared/host_stubs_common.inc | wc -l)" = "0" ] || { echo "FAIL: rurp_log stubs"; exit 1; }
# 3. Surviving stubs intact
grep -q 'rurp_write_to_register\|rurp_read_from_register' firestarter/test/native/avr/_shared/host_stubs_common.inc || { echo "FAIL: surviving stubs gone"; exit 1; }
# 4. Native tests still green
cd firestarter && pio test -e native -f '*test_dispatch*' -f '*test_messages*' 2>&1 | tail -5 | grep -qE '(PASSED|22|23|24)' || { echo "FAIL: native test"; exit 1; }
echo "PLAN 04 GREEN"
```
</verification>

<success_criteria>
- Lines 45-67 of `host_stubs_common.inc` are deleted (the 8 LOG_*_MSG PROGMEM externs + the rurp_log / rurp_log_P no-op stubs + their comment paragraphs)
- The surviving stubs at lines 69-170 are untouched
- `pio test -e native -f '*test_dispatch*' -f '*test_messages*'` reports ≥ 22 PASS
- D-03 follow-on requirement is closed: the test surface no longer references deleted production symbols
</success_criteria>

<output>
After completion, create `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-04-SUMMARY.md` recording:
- Line range deleted (45-67) and total lines removed
- Symbols removed: 8 LOG_*_MSG externs + 2 rurp_log/rurp_log_P stubs
- pio test -e native output (≥ 22 PASS)
- Confirmation that the 4 per-suite host_stubs.cpp files are unchanged
</output>
