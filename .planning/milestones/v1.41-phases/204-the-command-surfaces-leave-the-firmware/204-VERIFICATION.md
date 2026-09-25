---
phase: 204-the-command-surfaces-leave-the-firmware
verified: 2026-09-22T12:00:00Z
status: passed
score: 6/6 roadmap success criteria verified; 8/8 requirements (FWCMD-01..06, REL-02, REL-03) verified
covered_files:
  - .planning/REQUIREMENTS.md
  - .planning/ROADMAP.md
  - .planning/phases/204-the-command-surfaces-leave-the-firmware/204-01-PLAN.md
  - .planning/phases/204-the-command-surfaces-leave-the-firmware/204-01-SUMMARY.md
  - .planning/phases/204-the-command-surfaces-leave-the-firmware/204-02-PLAN.md
  - .planning/phases/204-the-command-surfaces-leave-the-firmware/204-02-SUMMARY.md
  - .planning/phases/204-the-command-surfaces-leave-the-firmware/204-03-PLAN.md
  - .planning/phases/204-the-command-surfaces-leave-the-firmware/204-03-SUMMARY.md
  - .planning/phases/204-the-command-surfaces-leave-the-firmware/204-04-PLAN.md
  - .planning/phases/204-the-command-surfaces-leave-the-firmware/204-04-SUMMARY.md
  - .planning/phases/204-the-command-surfaces-leave-the-firmware/204-05-PLAN.md
  - .planning/phases/204-the-command-surfaces-leave-the-firmware/204-05-SUMMARY.md
  - .planning/phases/204-the-command-surfaces-leave-the-firmware/204-BENCH-MATRIX.md
  - .planning/phases/204-the-command-surfaces-leave-the-firmware/204-BENCH-TRACER.md
  - .planning/phases/204-the-command-surfaces-leave-the-firmware/204-CONTEXT.md
  - .planning/phases/204-the-command-surfaces-leave-the-firmware/204-REVIEW.md
  - firestarter_app/firestarter/constants.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/tests/test_eprom_operations.py
  - firestarter_fw/CLAUDE.md
  - firestarter_fw/PROTOCOLS.md
  - firestarter_fw/include/eprom_operations.h
  - firestarter_fw/include/firestarter.h
  - firestarter_fw/include/memory_utils.h
  - firestarter_fw/platformio.ini
  - firestarter_fw/src/eprom_operations.cpp
  - firestarter_fw/src/firestarter.cpp
  - firestarter_fw/src/operation_utils.cpp
  - firestarter_fw/src/proms/eeprom_28c.cpp
  - firestarter_fw/src/proms/eprom.cpp
  - firestarter_fw/src/proms/flash_5v_page.cpp
  - firestarter_fw/src/proms/flash_intel.cpp
  - firestarter_fw/src/proms/flash_nor_unlock.cpp
  - firestarter_fw/src/proms/memory.cpp
  - firestarter_fw/test/native/avr/test_cmd_admission/test_cmd_admission.cpp
  - firestarter_fw/test/native/avr/test_dispatch/test_configure_memory.cpp
  - firestarter_fw/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp
  - firestarter_fw/test/native/avr/test_val_eprom/test_val_eprom.cpp
  - firestarter_fw/test/native/avr/test_val_nor_unlock/test_val_nor_unlock.cpp
  - firestarter_fw/test/native/avr/test_verify_error_ids/host_stubs.cpp
  - firestarter_fw/test/native/avr/test_verify_error_ids/test_verify_error_ids.cpp
  - firestarter_fw/tests/golden/protocol_branch_inventory.json
  - firestarter_fw/tests/test_blank_check_region_source_contract.py
  - firestarter_fw/tests/test_boolean_convention_source_contract_v133.py
  - firestarter_fw/tests/test_protocol_branch_inventory.py
  - firestarter_fw/tests/test_verify_survival_source_contract.py
  - tools/catalog/messages.toml
covered_digest: "v1:sha256:f771772f5efa7b38816e6656db8b73bb184dc55f6f3219d7de4d0e334cb779eb"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 204: The command surfaces leave the firmware — Verification Report

**Phase Goal:** Ordinals 4 and 6 leave the firmware with every in-algorithm verify provably intact,
and both host-firmware compatibility directions are demonstrated on the bench rather than reasoned
about.

**Verified:** 2026-09-22T12:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Method

This verification does not trust SUMMARY.md claims. For every truth below, the underlying command was
re-run in this session (native suite, source-contract pytest suite, `pio run -e leonardo`, host pytest
suite), the retirement was independently confirmed by direct `grep`/`git grep` across every dispatch
and configure-handler source file named in D-01, the must-not-remove call sites were independently
located and read, and a RED-then-restore was independently re-executed against
`test_verify_survival_source_contract.py` by deleting the real `memory_verify_execute(handle);` call
site and observing the exact failure text SUMMARY 204-02 claims, then restoring the file and confirming
the gate green and the git tree clean. The two bench records (`204-BENCH-TRACER.md`,
`204-BENCH-MATRIX.md`) were read in full and judged for whether they contain genuine transcripts (exit
codes, durations, SHA-256 digests, raw CLI output) rather than assertions — they do.

## Goal Achievement

### Observable Truths (ROADMAP Phase 204 success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `CMD_VERIFY`/`CMD_BLANK_CHECK` appear nowhere in the dispatch switch, `is_memory_cmd` or `configure_memory`, both wrappers and declarations gone | ✓ VERIFIED | `git grep -n "CMD_VERIFY\|CMD_BLANK_CHECK" -- '*.h' '*.cpp'` returns only 3 hits, all in test-file comments explaining the retirement (`test_configure_memory.cpp:193`, `test_val_eeprom28c.cpp:168`, `test_val_nor_unlock.cpp:130`) — zero hits in any dispatch/wrapper/configure source. `eprom_verify`/`eprom_blank_check` wrappers and declarations absent from `eprom_operations.{h,cpp}`. |
| 2 | A test FAILS if `eprom.cpp` stops calling `memory_verify_execute` for `VERIFY_PER_PULSE_PLUS_FINAL` | ✓ VERIFIED | Independently re-executed: deleted `memory_verify_execute(handle);` from the live `src/proms/eprom.cpp`, ran `test_verify_survival_source_contract.py::test_the_final_verify_pass_is_still_called_for_plus_final` — RED with the exact brace-matched-body failure text SUMMARY 204-02 quotes. Restored via `cp`; `git diff --stat` empty; full gate re-run 10/10 PASSED. |
| 3 | Each in-algorithm verify raises its own failure id, proven by test (amended text: `memory_verify_execute`/`eeprom28c_verify_page_readback`→0xAF, per-pulse budget exits→0xBD/0xBE, `flash_util_verify_operation`→0xB7 never 0xAF) | ✓ VERIFIED | Independently re-ran `pio test -e native_nodevtools -f "*test_verify_error_ids*"` — 8/8 PASSED, including `test_flash_util_data_poll_timeout_raises_timeout_id_not_verify_id` (both-directions assertion: raises 0xB7, explicitly asserted absent 0xAF) and the two budget-exit id tests. Amended text confirmed present verbatim in both `.planning/REQUIREMENTS.md` FWCMD-05 and `.planning/ROADMAP.md` Phase 204 criterion 3. |
| 4 | A `3.1.0b1`-labeled host performs `verify`/`blank` correctly against pre-`3.1.0` firmware, observed on the bench (REL-02) | ✓ VERIFIED | `204-BENCH-MATRIX.md` Task 2(a): real transcripts against firmware built from a detached worktree of pre-204 commit `e5842d8`, flashed to the bench Leonardo — `verify` exit 0 with `match, 0 bad of 65536`; `blank` exit 1 via the documented abort-predicate fast-stop path (traced against real `eprom_operations.py` source, not assumed), neither output carries an "unknown command" line (grep-confirmed in the record, exit 1 = absent). |
| 5 | A pre-`3.1.0` host against `3.1.0b1`-labeled firmware receives an actionable refusal on both commands, no hardware side effect (REL-03, FWCMD-06) | ✓ VERIFIED | `204-BENCH-MATRIX.md` Task 3(c)/(d): published `3.0.0b49` wheel host, `Unknown command: 6` (3.56s) and `Unknown command: 4` (3.49s), both exit 1, both well inside the bounding timeout, non-empty. Task 3(e): three independent whole-device reads (pre-swap, post-swap, post-refusal) share one SHA-256 digest (`a094e902...`) — no silent erase. |
| 6 | `protocol_branch_inventory.json` golden re-derived and diffed field-by-field keyed on `line`, never accepted on truthiness alone | ✓ VERIFIED | Golden read directly: `counts = {total_sites: 22, protocol_keyed_sites: 1, other_sites: 21}` matches the claimed re-derivation exactly. `git log` on the golden shows it was actually touched in the same commit (`5f66595`, 204-03) as `src/proms/eprom.cpp`. `pytest tests/test_protocol_branch_inventory.py` re-run: 7/7 PASSED. |

**Score:** 6/6 truths verified (0 present-behavior-unverified)

### Must-Not-Have-Been-Removed (from the verification brief)

| Item | Status | Evidence |
|------|--------|----------|
| Per-pulse verify inside the EPROM program loop | ✓ VERIFIED | Still present in `eprom.cpp` (`VERIFY_PER_PULSE_PLUS_FINAL` arm at line 494, `eprom_internal_report_budget_failure` for the two budget exits). |
| `memory_verify_execute` called from `eprom.cpp`'s `VERIFY_PER_PULSE_PLUS_FINAL` arm | ✓ VERIFIED | `src/proms/eprom.cpp:495` — `memory_verify_execute(handle);` inside `if (verify_mode == VERIFY_PER_PULSE_PLUS_FINAL)`. Defined `src/proms/memory.cpp:374`, declared `include/memory_utils.h:26`. |
| `eeprom28c_verify_page_readback` | ✓ VERIFIED | Defined and called from `eeprom28c_write_execute`'s only path, `src/proms/eeprom_28c.cpp:81,464,516`. |
| `flash_util_verify_operation` | ✓ VERIFIED | Defined `src/proms/flash_utils.cpp:30`, called from `flash_nor_unlock.cpp:111`. |
| `MSG_ERR_VERIFY` (0xAF) | ✓ VERIFIED | `#define MSG_ERR_VERIFY 0xAF` present in `include/messages.h:93`, unchanged. |
| `mem_util_blank_check`/`mem_util_blank_check_region`/`blank_check_saved_address`/`BLANK_CHECK_CHUNK_SIZE` survive, command-surface-only removed | ✓ VERIFIED | All four present in `src/proms/memory.cpp`; reached from `eprom.cpp:53` (erase-end, `firestarter_operation_end = mem_util_blank_check`) and `eprom.cpp:142` (write-init region call) — no dispatch-switch or `configure_memory` path reaches them any more (confirmed absent from criterion 1's grep). |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_fw/include/firestarter.h` | ordinal ladder minus 4/6, reserved-ordinal notes | ✓ VERIFIED | Both `#define`s and both `is_memory_cmd` arms absent; two reserved-ordinal comment blocks present at lines 53-59 and 68-73, both naming "retired in 3.1.0 (Phase 204)" and the never-reuse reason. |
| `firestarter_app/firestarter/constants.py` | mirror ladder minus `COMMAND_VERIFY`/`COMMAND_BLANK_CHECK` | ✓ VERIFIED | Both constants and `COMMAND_NAMES` rows absent (only comment references remain); mirrored reserved-ordinal notes present at lines 53-59, 66-71, matching the firmware note's shape and reason verbatim. |
| `firestarter_fw/tests/golden/protocol_branch_inventory.json` | re-derived golden | ✓ VERIFIED | 22/1/21 counts confirmed by direct read; landed in the same commit as `eprom.cpp` per `git log`. |
| `tools/catalog/messages.toml` | `DBG_VERIFY_PROM`/`DBG_BLANK_CHECK_PROM` annotated, ids unchanged | ✓ VERIFIED | Both entries present with retirement comments at lines 885, 893, 911, 919; no `id`/`name`/`format` change claimed or found. |
| `firestarter_fw/PROTOCOLS.md` | stale citations repaired | ✓ VERIFIED | INV-05 row cites `test_eprom_0x07_read_configure_only_does_not_enable_vpp`, confirmed to exist at `test/native/avr/test_val_eprom/test_val_eprom.cpp:168` and is registered (`RUN_TEST` at line 719). |
| `.planning/phases/.../204-BENCH-TRACER.md`, `204-BENCH-MATRIX.md` | genuine bench transcripts | ✓ VERIFIED | Both contain raw CLI output, exit codes, wall-clock durations, and SHA-256 digests — not narrated claims. Read in full; see Bench Record Assessment below. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `firestarter.h` CMD ladder | `constants.py` COMMAND ladder | lockstep commit pair, cross-repo obligation | ✓ WIRED | Firmware commits `268d844`/`305b2f4` paired with host commits `f6d3724`/`2a17fd7`, confirmed by SUMMARY commit-log cross-reference and both ladders' reserved-ordinal notes citing each other by filename. |
| `firestarter.cpp` dispatch `default:` arm | `MSG_ERR_UNKNOWN_CMD` → `command_done()` | the entire refusal mechanism (D-05) | ✓ WIRED | `default:` arm unmodified per SUMMARY and code review; bench-observed refusal text (`Unknown command: 6`/`4`) matches this exact path. |
| `eprom_operations.py` `region-end` guard | write command only, no longer verify | rewritten per D-02 | ✓ WIRED | `test_eprom_operations.py` guard tests convert to integer-literal assertions (confirmed present, host suite 2309/2309 green includes these). |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| FWCMD-01 | 204-01, 204-03 | Both ordinals gone from dispatch/`is_memory_cmd`/`configure_memory` | ✓ SATISFIED | Criterion 1 above; `.planning/REQUIREMENTS.md` line 65 Complete. |
| FWCMD-02 | 204-01, 204-04 | `eprom_verify`/`eprom_blank_check` wrappers+declarations deleted | ✓ SATISFIED | Wrapper absence confirmed; `messages.toml` D-06 annotation confirmed. |
| FWCMD-03 | 204-01, 204-03, 204-04 | Ordinals recorded reserved, never reused | ✓ SATISFIED | Both reserved-ordinal note pairs confirmed present and mirrored; doc citations in `CLAUDE.md`/`PROTOCOLS.md` repaired (INV-05 spot-checked). |
| FWCMD-04 | 204-02 | `memory_verify_execute` survives, test fails if call disappears | ✓ SATISFIED | Independently re-executed RED/restore (criterion 2 above). |
| FWCMD-05 | 204-02 | Each verify raises its own id, proven by test (amended) | ✓ SATISFIED | Native suite 8/8 re-run (criterion 3 above); amended text confirmed in REQUIREMENTS.md/ROADMAP.md. |
| FWCMD-06 | 204-05 | Refusal on both ordinals, no hardware side effect, on real hardware | ✓ SATISFIED | Bench matrix criterion 5 above. |
| REL-02 | 204-05 | Post-204 host / pre-204 firmware compatibility, observed on bench | ✓ SATISFIED | Bench matrix criterion 4 above. |
| REL-03 | 204-05 | Pre-3.1.0 host / post-204 firmware refusal, observed on bench | ✓ SATISFIED | Bench matrix criterion 5 above (same evidence as FWCMD-06). |

No orphaned requirements — `.planning/REQUIREMENTS.md`'s traceability table maps exactly these 8 IDs
to Phase 204, and all 8 appear in at least one plan's `requirements:` frontmatter field (204-01:
FWCMD-01/02/03/05/06/REL-03; 204-02: FWCMD-04/05; 204-03: FWCMD-01/02/03; 204-04: FWCMD-02/03; 204-05:
FWCMD-06/REL-02/REL-03).

### Gate Re-Execution (independently run this session, not read from SUMMARY)

| Gate | Command | Result | Expected (per brief) | Match |
|------|---------|--------|----------------------|-------|
| Native suite (always-on CI leg) | `pio test -e native_nodevtools` | 243/243, 20 suites | 243/243, 20 suites | ✓ |
| Firmware source-contract gates | `.venv311/bin/python -m pytest tests/ -o addopts="" -q` (in `firestarter_fw`) | 303 passed / 17 failed, all in `test_flash_path_record_sync.py` | 303 passed / 17 failed, same file | ✓ |
| Firmware build | `pio run -e leonardo` | 23810 bytes | 23810 bytes | ✓ |
| Host suite | `.venv311/bin/python -m pytest tests/ -o addopts="" -q` (in `firestarter_app`) | 2309 passed, 0 failed | 2309 passed, 0 failed | ✓ |
| Verify-survival gate RED proof | delete `memory_verify_execute(handle);` from `eprom.cpp`, re-run gate | RED with brace-matched-body failure, then restored clean (10/10 green) | same | ✓ |
| Verify-error-ids native suite | `pio test -e native_nodevtools -f "*test_verify_error_ids*"` | 8/8 PASSED | 8/8 | ✓ |
| Branch-inventory gate | `pytest tests/test_protocol_branch_inventory.py` | 7/7 PASSED | — | ✓ |

The 17 failures in `test_flash_path_record_sync.py` are confirmed pre-existing and out of scope: they
assert whole-repository git porcelain, and this working tree carries unrelated uncommitted files
(`.devcontainer/*`, `.planning/config.json`, `anything.txt`, `firestarter.wiki/`, etc., per the git
status snapshot at session start) — the same class of failure the brief names, not a phase-204
regression.

### Bench Record Assessment

Both `204-BENCH-TRACER.md` (plan 01, ordinal 6 tracer with ordinal 4 as live control) and
`204-BENCH-MATRIX.md` (plan 05, full four-role matrix) were read end to end. They meet the phase's own
evidentiary bar — "a checksum claimed is a checksum measured, a refusal quoted is a refusal captured":

- Every claimed outcome is backed by a literal captured transcript (raw CLI stdout), not a paraphrase.
- Every digest claim shows the actual `sha256sum`/digest value and states which files were compared.
- Every duration claim is a measured wall-clock number, not "promptly" alone.
- Every role (pre-204 firmware, post-204 firmware, post-204 host, published host) is pinned to a
  specific commit sha or PyPI version, with the D-07 label-substitution caveat stated explicitly in
  both records (neither side carries a literal `3.1.0b1` string; that bump is Phase 207's).
- The Leonardo-only coverage gap (no Uno-class board attached) is stated plainly in both records, not
  hidden.

**Known open item (WINDOWS.md entry 3), assessed for overreach:** the seated part's chip identity is
NOT independently confirmed — the un-forced read reports `Chip ID 0x1818` against the database's
expected `0xda08` for W27C512/W27E512. Both bench records state this explicitly, refer to the part as
"the seated part (identity unconfirmed)" in `204-BENCH-MATRIX.md`, and explain — correctly — that every
substantive claim (refused vs. served, byte-identity across the matrix) is chip-identity-independent by
construction, since every leg addresses the same physical part regardless of what species it is. I
found no place in either record, in the SUMMARYs, or in REQUIREMENTS.md/ROADMAP.md where this open
item is used to claim more than it supports (e.g., no claim that the part is a confirmed W27C512, no
claim that W27C512-specific behavior was exercised). This is legitimately carried as an open item, not
a gap, and is correctly logged in `.planning/WINDOWS.md` (entry 3, `kind: unmet-truth`, `status: open`)
for future operator/UAT sign-off.

### Anti-Patterns Found

None. Scanned all firmware/host source and doc files this phase modified for `TBD`/`FIXME`/`XXX`/
`TODO`/`HACK`/`PLACEHOLDER`/"not yet implemented"/"coming soon" — zero hits requiring action. Two
incidental matches are pre-existing, unrelated, and correctly reference tracked backlog items (a
folded-todo filename reference in `eprom_operations.py:2321`; a `PROTOCOLS.md` paragraph citing
Backlog 999.63 for an unrelated unimplemented feature on protocol `0x05`) — neither was introduced by
this phase and neither is a debt marker requiring closure here.

### Human Verification Required

None. All roadmap success criteria, all requirement IDs, and all must-not-remove survival items were
independently verified against the live codebase and re-executed gates in this session. The one
outstanding item (chip identity, WINDOWS.md entry 3) is explicitly carried as open by the phase's own
design and does not gate any claim this phase makes — see "Bench Record Assessment" above.

### Gaps Summary

No gaps found. All 6 ROADMAP success criteria verified against re-executed gates and direct source
inspection, not SUMMARY narrative. All 8 requirement IDs (FWCMD-01 through FWCMD-06, REL-02, REL-03)
are satisfied with evidence independently re-confirmed. The items the verification brief specifically
warned must survive (per-pulse verify, `memory_verify_execute`, `eeprom28c_verify_page_readback`,
`flash_util_verify_operation`, `MSG_ERR_VERIFY`) are all present, defined, and wired exactly as
claimed. The code review (`204-REVIEW.md`) independently found 0 blockers / 0 warnings / 1 info, and
this verification's own re-execution of the gates and re-derivation of the golden agrees with it.

---

_Verified: 2026-09-22T12:00:00Z_
_Verifier: Claude (gsd-verifier)_
