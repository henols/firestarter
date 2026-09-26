---
phase: 117-fix-remap-aware-0x0d-emitter-honest-completion-signal
verified: 2026-07-28T00:00:00Z
status: passed
score: 6/6 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 117: FIX — remap-aware `0x0D` emitter + honest completion signal Verification Report

**Phase Goal:** Make the SDP-disable sequence firmware already ships actually reach silicon, and
replace its inverted success check with one that isn't anti-correlated with success — proven by
flipping Phase 116's RED suite to GREEN, with zero change to the shared code the bench-proven
`0x05`/`0x06`/`0x07` families depend on.

**Verified:** 2026-07-28
**Status:** passed
**Re-verification:** No — initial verification

**Validation ceiling honored in this report:** the permitted claim is that the SDP-disable sequence
is *emitted* exactly as specified, byte-exact against a golden register trace, across all four
`0x0D` pinouts. Nothing below claims SDP was disabled on real silicon, that gh#11's symptom is gone
on hardware, or anything about AT28C silicon state. `0x0D` stays `UNVERIFIED`; `PROTOCOL-LEDGER`,
`support_status`, and the 84-chip count were not touched by this phase (confirmed — no diff to
`.planning/v1.16/ledger/`) and remain Phase 122's business.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The Phase 116 `0x0D` SDP trace suite, RED at phase start, is GREEN at phase end for all four `0x0D` pinouts | ✓ VERIFIED | Independently re-ran `pio test -e native -f "*test_eeprom28c_sdp*"`: 8/8 pass (full suite run below shows it inside the 108/108 total). `git diff e5b9e87..b30b91c -- test/.../test_eeprom28c_sdp.cpp` is **empty** — the RED→GREEN flip came from the production commit only, not a relaxed oracle. Cases 1-3 (`DIP28_28C256`/`DIP28_28C64`/`DIP24_2816`) prove stream equality against `SDP_FIXED_*`; cases 4-5 (`DIP32_28C512_EEPROM`, AT28C010/040) prove the A16-A18 staleness gap closes. |
| 2 | `flash_utils.{h,cpp}`, `flash_5v_page.cpp`, `flash_nor_unlock.cpp` byte-untouched; `0x05`/`0x06`/`0x07`/`0x10`/SRAM golden traces byte-identical | ✓ VERIFIED | Literal blob SHA comparison `git rev-parse ada4bdc:<path>` vs `git rev-parse HEAD:<path>` — all six frozen paths (4 production + `_shared/sdp_expected.h` + `_shared/sdp_bus_config.h`) match exactly. Independently re-ran `pio test -e native`: `test_val_eprom`, `test_val_nor_unlock`, `test_val_5v_page`, `test_val_flash_intel`, `test_val_sram` all pass unchanged (part of 108/108 total). |
| 3 | `eeprom28c_wait_for_write(handle, 0x5555, 0x20)` no longer exists; replacement's success condition can't be satisfied by an ignored sequence | ✓ VERIFIED | `grep -c 'eeprom28c_wait_for_write' src/proms/eeprom_28c.cpp` = 0 (function and forward declaration both deleted). Replacement `eeprom28c_wait_for_sdp_completion` is advisory-only — read the function body: it never writes `handle->response_code` and never logs, on any path (D-05). It cannot "report success" at all; the conclusion is deferred to the page-write poll, which has a real written byte to compare. Case 8 / `test_case8_completion_poll_preserves_prior_severity` permanently proves a prior WARNING survives even when the poll can never settle. |
| 4 | Native test asserts SDP-disable's terminal byte and chip-erase's terminal byte are distinct constants | ✓ VERIFIED | `test_fix05_terminal_byte_and_table_identity_guards` in `test_sdp_harness.cpp` pins `EEPROM_SDP_DISABLE[5].byte == 0x20`, `FLASH_ERASE[5].byte == 0x10`, asserts distinct-object pointers, and the exactly-one-differing-field property. **Independently re-executed the anti-hollow proof myself**: mutated the production terminal byte to `0x10`, re-ran `pio test -e native -f "*test_sdp_harness*"` — both `test_fix05_terminal_byte_and_table_identity_guards` and `test_fix05_guard_rejects_planted_terminal_mutation` went RED as expected; restored the file, re-ran, confirmed clean `git diff` and 15/15 GREEN. |
| 5 | For the 18 chips ≥64 KB, the fixed emitter closes the A16-A18 staleness gap as a verified by-product, not a separate change | ✓ VERIFIED | `eeprom_28c.cpp`'s emitter routes every command byte through `handle->firestarter_set_data` → `memory_set_data` → `mem_util_remap_address_bus`, which rewrites `CONTROL_REGISTER` on every address change — a single routing change, no separate remap code added. Proven as a by-product by test cases 4-5 (`DIP32_28C512_EEPROM`) in `test_eeprom28c_sdp.cpp`, both GREEN. |
| 6 | Per-page write polling corrected so a partial write cannot report success; native test plants a partial-write scenario the old poll would have passed and the fix fails | ✓ VERIFIED | `test_fix06_planted_partial_write_fails_fixed_path_and_passes_legacy_poll` in `test_val_eeprom28c.cpp` runs the fixed path (asserts `RESPONSE_CODE_ERROR`) and, in the same test, an executable replica of the deleted last-byte-equality poll against the identical planted mock (asserts `TRUE`, i.e. the old check would have passed). Paired with an isolation control (`test_fix06_clean_page_write_succeeds_isolation_control`) and a page-boundary window case. All 6 cases in `test_val_eeprom28c` GREEN (part of the 108/108 run). |

**Score:** 6/6 truths verified (0 present-but-behavior-unverified — every behavior-dependent claim
above was proven by a test I personally executed, not merely read as source).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| FIX-01 | 117-01 (oracle) + 117-02 (fix) | Remap-aware `0x0D`-local emitter replaces `flash_execute_command(EEPROM_SDP_DISABLE)` | ✓ SATISFIED | `grep -c 'flash_execute_command' eeprom_28c.cpp` (code lines) = 0; `eeprom28c_emit_command_sequence` present and called from `eeprom28c_write_init`; cases 1-5 GREEN. |
| FIX-02 | 117-01 + 117-02 | Inverted `(0x5555, 0x20)` read-back deleted, not salvaged; replacement not anti-correlated with success | ✓ SATISFIED | `eeprom28c_wait_for_write` gone; `eeprom28c_wait_for_sdp_completion` never writes `response_code`; case 8 GREEN. |
| FIX-03 | 117-02 | A16-A18 staleness gap closed for 18 chips ≥64 KB, as a by-product | ✓ SATISFIED | Same routing change as FIX-01; cases 4-5 (`DIP32_28C512_EEPROM`) GREEN, no separate remap code added. |
| FIX-04 | 117-05 (gate) | Frozen firmware files/goldens byte-untouched | ✓ SATISFIED | Blob-SHA equality independently re-verified against `ada4bdc` for all 6 frozen paths; other-family suites green. |
| FIX-05 | 117-04 | Terminal-byte constant guards + table-identity cross-guard | ✓ SATISFIED | `test_fix05_terminal_byte_and_table_identity_guards` + planted-mutation counterpart; anti-hollow proof independently re-executed by this verifier. |
| FIX-06 | 117-03 | Per-page polling corrected; partial write cannot report success | ✓ SATISFIED | `eeprom28c_wait_for_page_write` (DQ7-only) split from `eeprom28c_verify_page_readback` (always-on read-back); `eeprom28c_wait_for_write` (the conflated function) fully removed; 3 new cases GREEN. |

No orphaned requirements — `.planning/REQUIREMENTS.md`'s Phase 117 row set (FIX-01..06) exactly
matches the six IDs claimed across plans 117-01 through 117-05, and REQUIREMENTS.md shows all six
`Complete`.

### Artifact Verification (Level 1-3)

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter/src/proms/eeprom_28c.cpp` | New emitter, completion poll, page-write split, D-13 comment | ✓ VERIFIED | Read in full. Contains `eeprom28c_emit_command_sequence`, `eeprom28c_wait_for_sdp_completion`, `eeprom28c_wait_for_page_write`, `eeprom28c_verify_page_readback`, four/two named timing constants, `EEPROM_SDP_DISABLE` external linkage, `PAGE_SIZE 64` D-13 comment with the AT28MC010/AT28C010 counter-example. All wired into `eeprom28c_write_init`/`eeprom28c_write_execute`. |
| `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` | D-01/D-02 edits, 8 cases | ✓ VERIFIED | 8 `RUN_TEST` entries; zero `mock_set_data_keyed`; six `NOT_EQUAL(RESPONSE_CODE_ERROR)` asserts; zero `EQUAL(RESPONSE_CODE_ERROR)`. Passed when I ran it. |
| `firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp` | FIX-05 guard + planted counterpart | ✓ VERIFIED | 15 `RUN_TEST` entries; `sdp_tables_identical` helper; both new cases present, registered, and independently re-verified to fail under a planted mutation. |
| `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` | FIX-06 3 new cases | ✓ VERIFIED | 6 `RUN_TEST` entries (3 pre-existing + 3 new); side-by-side old-vs-new contrast, isolation control, page-boundary window all present and passing. |
| `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` | RED capture, GREEN capture, FIX-04 gate, correction | ✓ VERIFIED | Contains `## Post-suite-edit RED baseline`, `## GREEN after the Phase 117 fix`, `## FIX-04 non-regression gate`, and the `> CORRECTION` block for the host-side regression (see Findings below). |
| `firestarter/platformio.ini` | `test_filter` entry added | ✓ VERIFIED | `native/avr/test_eeprom28c_sdp` present exactly once; `-I` entry unduplicated. |
| `firestarter_app/tests/test_sdp_table_parity.py`, `tools/check_no_log_in_sdp_window.py` | Re-anchored append-only after regression | ✓ VERIFIED | `git diff 36a9bb5..9dd11a9` confirms append-only pattern additions, no deletions of prior anchors; independently re-ran host tests: all pass. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `eeprom28c_write_init` | `eeprom28c_emit_command_sequence` | direct call, `handle->firestarter_set_data` loop | ✓ WIRED | Read in `eeprom_28c.cpp`; routes through `memory_set_data`/`mem_util_remap_address_bus`. |
| `eeprom28c_write_init` | `eeprom28c_wait_for_sdp_completion` | direct call, unguarded | ✓ WIRED | Replaces the deleted guarded call; verified no `response_code`/`LOG_` inside. |
| `eeprom28c_write_execute` | `eeprom28c_wait_for_page_write` + `eeprom28c_verify_page_readback` | flush-branch calls in order, window-indexed | ✓ WIRED | Both called on `page_end \|\| last_byte`; window advances by `i + 1`. |
| `test_sdp_harness.cpp` | production `EEPROM_SDP_DISABLE` | `extern const byte_flip_t EEPROM_SDP_DISABLE[6];` | ✓ WIRED | Matching extern declaration in both TUs; linkage change confirmed in `eeprom_28c.cpp`; guard reads the real array (proven by the mutation test flipping RED when the production array changed). |

### Data-Flow Trace (Level 4)

Not applicable — this phase is firmware protocol/timing logic, not a UI or dashboard rendering
fetched data. The "data flow" equivalent (does the emitted byte stream reach the real bus-write
function, not a stub) is what Key Link Verification above and the byte-exact golden-trace
comparisons in cases 1-5 establish.

### Behavioral Spot-Checks / Test Execution (independently re-run by this verifier)

| Behavior | Command | Result | Status |
|---|---|---|---|
| Full native suite | `pio test -e native` (from `/workspaces/firestarter`) | `108 test cases: 108 succeeded`, 16 suites, exit 0 | ✓ PASS |
| Uno board build | `pio run -e uno` | `SUCCESS`, Flash 23390/32256 (72.5%) | ✓ PASS |
| Leonardo board build | `pio run -e leonardo` | `SUCCESS`, Flash 25528/28672 (89.0%) | ✓ PASS |
| FIX-05 anti-hollow (re-executed independently, not just read) | Mutate `EEPROM_SDP_DISABLE[5].byte` to `0x10`, run `pio test -e native -f "*test_sdp_harness*"`, restore, re-run | RED (2 cases failed as expected) → restore → 15/15 GREEN, clean `git diff` | ✓ PASS |
| Frozen-artifact blob SHA equality | `git rev-parse ada4bdc:<path>` vs `git rev-parse HEAD:<path>` for all 6 frozen paths | All 6 match | ✓ PASS |
| Suite-file diff between RED and GREEN commits | `git diff e5b9e87..b30b91c -- test/.../test_eeprom28c_sdp.cpp` | Empty | ✓ PASS |
| Host regression-gate fix's tests | `python -m pytest tests/test_sdp_table_parity.py tests/test_check_no_log_in_sdp_window.py -q` (from `/workspaces/firestarter_app`) | 10 passed | ✓ PASS |
| Full host suite | `python -m pytest tests/ -q` | 1 failure: `test_audit_coverage_matrix::test_golden_file_matches` | ✓ PASS (confirmed unrelated below) |

**Pre-existing, unrelated failure confirmed by direct diff:** `tests/test_audit_coverage_matrix.py`
is byte-identical between `firestarter_app@36a9bb5` (phase base) and HEAD — the file was never
touched by Phase 117, and the test reads the chip database, not any firmware path. This is
carried debt since v1.21, correctly excluded from this phase's scope.

### Anti-Patterns Found

None. Scanned all six changed firmware files plus the two changed host files for `TBD`/`FIXME`/`XXX`
— zero hits. No stub returns, no placeholder comments, no empty handlers found in the read-through
of `eeprom_28c.cpp` or the modified test files.

## Finding Requiring Explicit Disposition (per orchestrator instruction — not papered over)

**What happened:** After plan 117-05 committed and asserted "zero `firestarter_app` files changed
anywhere in the phase," the phase's own regression gate (run before this verification) discovered
that 117-02's and 117-03's firmware changes broke four Phase-116 host-side test gates in
`firestarter_app` (`tests/test_sdp_table_parity.py` ×3, `tests/test_check_no_log_in_sdp_window.py`
×1) that scan `eeprom_28c.cpp` source text for pre-Phase-117 identifiers/declaration syntax. Both
failure modes are fail-closed (`ValueError`/exit 1), never a silent pass, and were proven to be
Phase-117-caused (not pre-existing) via the `FIRESTARTER_SDP_SRC` injection seam. The gates were
fixed append-only under explicit operator authorization in `firestarter_app@9dd11a9`, and both the
originally-false claim in `firestarter@cdf71a1`'s `RED-BASELINE.md` section and `117-05-SUMMARY.md`
were corrected in place (`firestarter@f8d10a5` for the firmware record; a `POST-CLOSE CORRECTION`
block appended to the SUMMARY) rather than left standing.

**My verdict:** This is a genuine deviation from the phase's self-declared "firmware-only, zero
`firestarter_app` change" intent, and it is honestly worth flagging — a plan-coverage gap (no plan
in this phase's five contained a task to update the Phase-116 host gates for the new identifiers)
that only surfaced at a regression gate run after formal plan completion. **It does not, however,
violate FIX-04 or ROADMAP success criterion 2 as literally written** — both are scoped exclusively
to `flash_utils.{h,cpp}`, `flash_5v_page.cpp`, `flash_nor_unlock.cpp`, and the named golden traces,
none of which live in `firestarter_app`; I independently confirmed all six frozen paths byte-
identical by blob SHA. It also does not violate the firmware-before-host ordering invariant as
scoped in `117-CONTEXT.md` (which concerns wire/protocol/CLI surfaces) — the two changed host files
are source-scanning `pytest` test gates with no `MSG_*`, `FLAG_*`, command, or serialized-field
change; I independently confirmed `include/messages.h`/`include/firestarter.h` are unchanged from
`ada4bdc`, and re-ran both fixed host tests (pass) and the full host suite (only the known-unrelated
`test_audit_coverage_matrix` failure remains). The fix itself is minimal, append-only (superseded
patterns retained per the project's anti-hollow contract, verified via diff), and non-behavioral.

**Disposition:** Not a blocker for this phase's six requirements or its ROADMAP success criteria.
Recorded here as a WARNING for human awareness because it means Phase 117 touched a file outside
its declared single-repo scope under an ad-hoc "operator authorization" path rather than a planned
task — worth a retrospective note for Phase 118-122 planning (each of which also touches shared
Phase-116-authored gates) so the same category of gap is anticipated rather than caught late again.

## Human Verification Required

None. Every ROADMAP success criterion and every FIX-01..06 requirement was verified either by direct
code reading (byte-level: blob SHAs, grep counts, function-body inspection) or by tests this
verifier personally executed (full native suite, both board builds, the FIX-05 anti-hollow mutation
proof re-run independently, the host regression-gate tests, the full host suite). No claim in this
report exceeds the validation ceiling — every verified truth's subject is code/test behavior, never
AT28C silicon state.

## Gaps Summary

No gaps. All six ROADMAP success criteria and all six FIX-01..06 requirements are verified against
the actual codebase state, not SUMMARY.md narrative. One process finding (the host-side regression
gate breakage, honestly disclosed and corrected in the project's own records) is documented above
for human awareness but does not block phase completion.

---

_Verified: 2026-07-28_
_Verifier: Claude (gsd-verifier)_
