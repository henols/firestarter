---
phase: quick-260821-wna
plan: "01"
subsystem: testing
tags: [dev-test, chip-test, uv-eprom, diagnostic-report, cli-handlers, firestarter_app]

# Dependency graph
requires:
  - phase: quick-260807-kaq
    provides: erase-then-blank-check step ordering in derive_plan
provides:
  - Non-UV `dev test` primary write/verify pass covers the FULL device (minus flash4 boot blocks)
  - UV-EPROM writes are bit-masked (`C & D`) against the chip's own content, slot-selected by probing
  - Structural vacuous-pass guard (`WriteTarget.__post_init__`) refusing a saturated/degenerate write
  - Write-coverage provenance in the diagnostic report JSON and console (schema 1.6)
  - Truthful UV consent prompt describing the new full-device-if-blank ceiling
affects: [dev-test-cli, chip-test-engine, diagnostic-report-schema]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Execution-time mask resolution seam (WriteContext) separate from derive_plan's pure region/policy decision"
    - "Structural non-registry discipline (LEG-15): locate a step by field shape, never by comparing StepResult.op against a specific OP_* constant, inside a declared non-registry unit"

key-files:
  created:
    - firestarter_app/tests/test_uv_mask.py
    - firestarter_app/tests/fake_chip.py
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_chip_test.py
    - firestarter_app/tests/test_chip_test_sdp_leg.py
    - firestarter_app/tests/test_dev_test_cmd.py
    - firestarter_app/tests/test_diagnostic_report.py

key-decisions:
  - "_UV_MIN_CLEARED_BITS / _UV_MIN_RETAINED_BITS both set to 64 (of 2048 bits in a 256-byte slot) -- per-slot, not per-byte, floors (Claude's discretion, D-B)"
  - "Slot selection probes uv_slot_starts in 4096-byte (16-slot) reads, never persisting a cursor -- the chip's own content is the state (D-B)"
  - "The write step is located structurally (destructive=True + write_region is not None, first such step in plan order) inside DiagnosticReport, never by comparing against OP_WRITE/OP_WRITE_PARTIAL -- required by the pre-existing LEG-15 non-registry discipline"
  - "SDP-leg region stays fixed/small (leg_region) even when the chip's own write is widened to full-device -- D-D keeps the leg proving the lock mechanism, not coverage"

requirements-completed: [QUICK-260821-wna]

coverage:
  - id: D1
    description: "Non-UV dev test write/verify covers the full device (flash4 excludes its two boot blocks, naming the exclusion even on success)"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_full_device_write_non_uv_covers_whole_device"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_full_device_write_flash4_carves_out_boot_blocks"
        status: pass
    human_judgment: false
  - id: D2
    description: "UV EPROM write is bit-masked (C & D) against the chip's own probed content; blank UV chip on a consenting run gets the full-device pattern (D-C)"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_uv_used_chip_write_is_genuinely_masked_and_verify_reads_the_region"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_uv_virgin_full_scope_gets_full_device_masked_write"
        status: pass
    human_judgment: false
  - id: D3
    description: "A saturated or 0x00 slot can never be reported as a write pass; the run SKIPs and names saturation, write_eprom is never called"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_every_slot_saturated_write_is_skipped_never_ok"
        status: pass
      - kind: unit
        ref: "tests/test_uv_mask.py#test_write_target_refuses_masked_target_below_cleared_floor"
        status: pass
    human_judgment: false
  - id: D4
    description: "No slot cursor is ever persisted to disk during UV slot selection"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_probe_never_persists_a_slot_cursor_to_disk"
        status: pass
    human_judgment: false
  - id: D5
    description: "Write-coverage provenance reaches both the saved JSON (schema 1.6 additive keys) and the console, end to end through the real CLI"
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py#TestWriteCoverageProvenanceD_F::test_used_uv_chip_cli_run_carries_slot_region_in_json_and_console"
        status: pass
    human_judgment: false
  - id: D6
    description: "The three dev test console gates and _ALWAYS_WRITES_PASS_COUNT stay green with their expected sets unedited; chip_database.json and tools/build_db.py untouched"
    verification:
      - kind: unit
        ref: "tests/test_check_devtest_orchestrator.py, tests/test_characterization.py, tests/test_check_diagnostic_report_claims.py"
        status: pass
      - kind: other
        ref: "git diff --stat beta -- firestarter/data/chip_database.json tools/build_db.py (empty)"
        status: pass
    human_judgment: false
  - id: D7
    description: "D-D's disclosure half reaches the operator: a successful flash4 boot-block carve names the exclusion, and a whole-device-boot-block fixed-policy fallback states its real refusal reason (never borrowed UV slot wording) -- in both the JSON write_coverage key and the console row"
    verification:
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_successful_flash4_carve_discloses_boot_block_exclusion_in_json"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_successful_flash4_carve_discloses_boot_block_exclusion_in_console"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_whole_device_boot_block_fallback_discloses_refusal_not_uv_wording"
        status: pass
    human_judgment: false

duration: ~5h
completed: 2026-08-22
status: complete
---

# Quick Task 260821-wna: dev test full-size write with UV bit-masked slot selection Summary

**`dev test` now writes the whole device on non-UV chips (flash4 boot blocks excluded) and, on UV-erasable EPROMs, bit-masks the address-derived pattern against the chip's own probed content — advancing to the next 256-byte slot when the current one is saturated, with a structural guard that makes a vacuous "pass" on a dead/absent chip impossible to construct.**

**Post-ship follow-up (addressed in this same task, commit `1868ab3`):** the initial 1893-test-green implementation shipped D-D's coverage MECHANISM correctly but silently dropped its DISCLOSURE half — a successful flash4 boot-block carve reported nothing, and a whole-device-boot-block fallback rendered misleading UV wording. Fixed by reading the plan-time `Step.reason` instead of the execution-time `StepResult.reason` (which is legitimately cleared on a clean write); see Deviation 4 below for the full account.

## Performance

- **Duration:** ~5h (six tasks, large surface area across chip_test.py/diagnostic_report.py/cli_handlers.py)
- **Tasks:** 6 completed (all from the plan)
- **Files modified:** 9 (2 new test files, 7 modified)

## Accomplishments

- Non-UV `dev test` primary write/verify pass now covers the FULL device; a protocol-0x05 (flash4) part excludes its two permanently-locked 16 KiB boot blocks and names the exclusion in the report even on a successful carve-out; the three 32 KiB flash4 rows whose whole device is boot block fall back to the pre-existing small region with a stated reason.
- UV-EPROM writes are bit-masked (`C & D`) against the chip's own content: the engine probes candidate slots top-down in 4096-byte reads, evaluates each against two per-slot bit-count floors (`_UV_MIN_CLEARED_BITS`/`_UV_MIN_RETAINED_BITS`, both 64), and takes the first serviceable slot — no cursor is ever persisted, the chip's content is the state.
- `WriteTarget.__post_init__` is the structural vacuous-pass guard: it refuses to construct a target whose pattern length disagrees with its region, is degenerate (all-0x00/all-0xFF), or (when masked) clears/retains too few bits. Every OK verdict downstream is reachable only through an instance of this class; a saturated/refused write SKIPs with a reason naming saturation and `write_eprom` is never called.
- A blank UV chip on a consenting ("full") run gets a full-device masked write (D-C); the same chip on "partial" scope, or a used chip on either scope, gets a single masked slot — the consent literal now means "ceiling", not "window width".
- `derive_plan` decides the region and a new `Step.region_policy`/`Step.full_device_permitted` purely from the DB, with zero chip access; the mask is resolved entirely at execution time (`_resolve_write_target`, threaded through a new `WriteContext`).
- The region start now reaches the wire: `write_eprom`/`verify_eprom` carry `address_str` for any non-zero region start, and every region read-back (probe, write/verify fingerprint, and the SDP leg's own oracle) is region-scoped and sliced via `_read_region`, fixing the pre-existing whole-device-read gap that only "worked" because every prior test double happened to write exactly a region-sized payload.
- Write-coverage provenance reaches the report: schema 1.5 → 1.6 adds five additive per-step keys (region start/length, bits cleared/retained, current-content source), and `render()` gains one console row naming the slot/exclusion/refusal whenever the write did not plainly cover the full device.
- The UV consent prompt and its surrounding comments now describe what the two answers actually do post-D-C, closing the inert-prompt defect this task exists to fix.

## Task Commits

Each task was committed atomically:

1. **Task 1: Pure masking, slot and region arithmetic** - `719268b` (feat)
2. **Task 2: derive_plan decides the region POLICY, purely from the DB** - `71efded` (feat)
3. **Task 3: A fake chip double modeling UV physics and absolute-offset reads** - `05e0869` (test)
4. **Task 4: Execution-time mask, slot selection and region-scoped I/O** - `95005b7` (feat)
5. **Task 5: Write-coverage provenance in the report and the one-line warning** - `fb39828` (feat)
   - Follow-up fix (found running Task 6's full-suite gate): `496f6ef` (fix) — the D-F coverage row's write-step lookup violated the pre-existing `test_non_registry_still_has_no_ops` LEG-15 discipline (comparing `StepResult.op` against `OP_WRITE`/`OP_WRITE_PARTIAL` inside `DiagnosticReport`, a declared op-vocabulary non-registry). Relocated the lookup to a structural test (first step with `destructive=True` and a non-`None` `write_region`) instead.
6. **Task 6: Truthful UV consent prompt, then the whole gate set** - `57c1b8f` (docs)
7. **Post-ship follow-up: D-D disclosure was reading the wrong reason field** - `1868ab3` (fix) — coordinator-reported gap, addressed before completing this task; see Deviation 4 below.

**Plan metadata:** not yet committed — orchestrator handles the docs commit per this task's repo mechanics.

## Files Created/Modified

- `firestarter_app/firestarter/chip_test.py` - pure masking/slot/region arithmetic (`mask_write_pattern`, `bits_cleared_by`, `bits_retained_by`, `uv_slot_starts`, `full_device_region`, `WriteTarget`); `Step.region_policy`/`full_device_permitted`; `derive_plan`'s policy decision; `_address_arg`/`_size_arg`/`_read_region`/`_resolve_write_target`; `WriteContext`; `_dispatch_multi_run`/`_dispatch_sdp_leg` execution-time wiring
- `firestarter_app/firestarter/diagnostic_report.py` - schema 1.6 additive per-step keys; the D-F write-coverage console row; comment recording the deliberate `dedup_fingerprint` residual
- `firestarter_app/firestarter/cli_handlers.py` - truthful UV consent prompt and design-history comments
- `firestarter_app/tests/test_uv_mask.py` (new) - pure arithmetic/`WriteTarget` guard tests
- `firestarter_app/tests/fake_chip.py` (new) - `FakeChip` operator double modeling UV AND-write physics and absolute-offset reads
- `firestarter_app/tests/test_chip_test.py` - region-policy tests, FakeChip-driven execution-time behavioural tests, retargeted region tests
- `firestarter_app/tests/test_chip_test_sdp_leg.py` - two new region-scoped-readback legs
- `firestarter_app/tests/test_dev_test_cmd.py` - `address_str`-aware operator-double retrofits, retargeted exit-precedence test, prompt-text test, CLI-level write-coverage leg
- `firestarter_app/tests/test_diagnostic_report.py` - renamed/updated schema-version-pinning tests

## Decisions Made

- **Bit-count floors (D-B, Claude's discretion):** `_UV_MIN_CLEARED_BITS = _UV_MIN_RETAINED_BITS = 64`, both per-SLOT not per-byte. A virgin 256-byte slot offers 1024 clearable and 1024 retained bits (the address-derived pattern's popcount is exactly 1024 over any 256-byte slot); 64 accepts a slot with ~6% of its virgin headroom left while staying far above a single-bit anomaly or transport glitch, and the retained floor is what makes an all-0x00 read-back structurally unable to satisfy `WriteTarget`.
- **Probe block size:** `_UV_PROBE_BLOCK_LENGTH = 4096` (16 slots per read) — cost proportional to blocks read, not slots evaluated.
- **Sanity ceiling (D-E):** `_MAX_FULL_DEVICE_LENGTH = 1 << 24` (16 MiB) — largest shipped device measured at 1 MiB across 8 rows; 16 MiB leaves headroom for a future part while refusing an absurd override.
- **SDP leg stays small (D-D):** the six leg steps keep `leg_region` (computed by the pre-existing formula) regardless of the chip's own write's new policy — the leg proves the lock mechanism, not coverage, and AT28C256 alone carries six region-sized write-shaped leg ops that would otherwise become six full-device transfers per run.
- **Mask computed only at execution time:** `derive_plan` remains a pure, zero-chip-access function (proven by the existing spy-db test, unmodified); the mask lives entirely in `_resolve_write_target`, reached via the new `WriteContext` threaded through `run_plan`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] D-F coverage row violated the LEG-15 op-vocabulary non-registry discipline**
- **Found during:** Task 6 (running the full gate set)
- **Issue:** `render()`'s write-step lookup compared `StepResult.op` against `OP_WRITE`/`OP_WRITE_PARTIAL` inside `DiagnosticReport` — a class `tests/test_op_registration_parity.py` declares as carrying ZERO op vocabulary (`test_non_registry_still_has_no_ops`), re-measured every run by an AST walk.
- **Fix:** Located the write step structurally instead — the first step in `plan.steps` (in the same order as `self.results`) carrying `destructive=True` AND a non-`None` `write_region`. `verify` never sets `destructive`; `erase` never carries `write_region`; the SDP leg's six steps always come last. Dropped the now-unused `OP_WRITE`/`OP_WRITE_PARTIAL` import.
- **Files modified:** `firestarter_app/firestarter/diagnostic_report.py`
- **Verification:** `tests/test_op_registration_parity.py` (7/7 pass); full suite re-run green (1893 passed)
- **Committed in:** `496f6ef`

**2. [Rule 1 - Bug] Task-3 fixture retrofit exposed a pre-existing SDP-leg length-gate fragility (M-2)**
- **Found during:** Task 3 (full test_dev_test_cmd.py/test_chip_test_sdp_leg.py suite run)
- **Issue:** `make_leaked_lock_operator`/`make_held_lock_operator`/`make_restore_failed_operator` originally REPLACED their internal state wholesale on every write (rather than modeling a persistent whole-device buffer). Once `make_clean_operator`'s `read_eprom` was fixed to write real content (needed so UV probes see plausible data instead of an empty file), a naive "persistent whole-device buffer" retrofit of the other three doubles would have made the SDP leg's read-back return the WHOLE device rather than the leg's own small region, breaking the leg's pre-existing length gate for chips whose shipped write region was widened by this task (M-2's exact finding, now reachable one task earlier than expected).
- **Fix:** Kept these three doubles' pre-existing "replace state wholesale on each write" model (matching their actual pre-task behavior) while adding `address_str`/`size_str` acceptance and absolute-offset seek reproduction — deliberately NOT introducing a persistent whole-device buffer, since every ALLOW chip's SDP-leg region in this suite starts at address 0 and would not exercise the new code anyway.
- **Files modified:** `firestarter_app/tests/test_dev_test_cmd.py`
- **Verification:** `tests/test_dev_test_cmd.py` (56/56, later 58/58) and `tests/test_chip_test_sdp_leg.py` (80/80, later 82/82) both pass
- **Committed in:** `05e0869`

**3. [Rule 1 - Bug] `make_clean_operator`'s dead-write-path incidental behavior was relied on by one exit-precedence test**
- **Found during:** Task 4 (full test_dev_test_cmd.py run after wiring `_dispatch_multi_run`)
- **Issue:** `test_bad_and_notrun_exits_1_not_2` relied on `make_clean_operator`'s PRE-Task-3 `read_eprom` (which wrote no file at all) to accidentally produce a BAD verdict via the SDP leg's length gate. Task 3's fix (giving `make_clean_operator` a genuine all-0xFF read-back) turned that same scenario into a `marginal` verdict (correct-length, degenerate-content arm) instead of BAD, breaking this test's specific need for a BAD verdict to prove D-14's precedence rule.
- **Fix:** Added a purpose-built short-read override (`read_eprom` writing zero bytes) scoped to only this one test, leaving `make_clean_operator`'s shared default behavior — now honestly "clean" end to end — unchanged for every other test.
- **Files modified:** `firestarter_app/tests/test_dev_test_cmd.py`
- **Verification:** `test_bad_and_notrun_exits_1_not_2` passes; full `test_dev_test_cmd.py` suite green
- **Committed in:** `95005b7`

**4. [Rule 1 - Bug, post-ship] D-D's disclosure half was reading the wrong reason field**
- **Found during:** Post-completion coordinator review, reproduced directly against the shipped code (not caught by the 1893-test green suite, because no existing test rendered the report or read its JSON `reason`/coverage field for either affected chip -- every assertion on these two paths checked `write_target.region`/`address_str`/`Step.reason` directly).
- **Issue:** `_write_coverage_line` read `StepResult.reason`, which `_dispatch_multi_run` legitimately clears to `""` on a clean OK write. Consequence: a SUCCESSFUL flash4 boot-block carve (W29C040) disclosed NOTHING to the operator (`report line = None`), and a whole-device-is-boot-block `fixed`-policy fallback (AT29C256/AT29C257/AT29LV256) rendered misleading UV slot wording (`"slot 0x0 (256 bytes), 0 bits clearable"`) on a chip that was never masked. Both violate CONTEXT.md D-D's "excluded with a stated, visible reason rather than reported as a FAIL... a silent pass is not [acceptable]".
- **Fix:** `_write_coverage_line` now reads the PLAN-TIME `Step.reason` (`derive_plan`'s own disclosure, set even on a successful carve) instead of `StepResult.reason`; the `fixed`-policy branch states that real reason instead of borrowing UV slot wording. The line is computed ONCE, in `to_dict()`/`_step_dict` (a new additive `write_coverage` per-step JSON key), so it reaches both the saved JSON (what gets filed on issues) and the console -- `render()` now just reads that same key rather than recomputing. The write step is still located structurally (`DiagnosticReport._write_step_index`), preserving the LEG-15 discipline `496f6ef` already established.
- **Files modified:** `firestarter_app/firestarter/diagnostic_report.py`, `firestarter_app/tests/test_diagnostic_report.py`
- **Verification:** 5 new tests drive real `derive_plan`+`run_plan`+`render()`/`to_dict()` against real DB chips (W29C040 successful carve; AT29C256/AT29C257/AT29LV256 whole-device fallback) and assert BOTH the JSON `write_coverage` key and the console row -- all pass; full suite re-run green (1898 passed); `tests/test_op_registration_parity.py` still 7/7 (LEG-15 discipline intact); ruff check/format clean; scoped mypy clean.
- **Committed in:** `1868ab3`

---

**Total deviations:** 4 auto-fixed (3 during execution + 1 post-ship follow-up, all Rule 1 - bugs; none were scope changes)
**Impact on plan:** All four fixes were necessary for correctness; none narrowed the plan's scope or weakened an assertion. Deviation 4 closes a real gap in D-D's disclosure requirement that a fully green test suite had not exercised.

## Test Disposition — every RED test named in the plan's hazard list

- **`test_dev_test_cmd.py`'s positional `write_eprom` side-effect (`_capture_region_and_write_ok`)** — RETARGETED: added `*_args, **_kwargs` so the new `address_str` keyword does not `TypeError`. Behavior/assertions unchanged.
- **Three operator-double closures (`make_leaked_lock_operator`/`make_held_lock_operator`/`make_restore_failed_operator`)** — RETARGETED: added `address_str`/`size_str` acceptance and absolute-offset seek reproduction while deliberately preserving their pre-existing "replace state wholesale" model (see Deviation 2 above for why a persistent-buffer retrofit was rejected).
- **`test_chip_test.py` region groups:**
  - **736-793** (`test_derive_plan_partial_same_ops_as_full_different_region`) — UNCHANGED: still passes verbatim; M8720's full-vs-partial region values changed numerically but the test's own assertions (`!=`/`==` comparisons, never a hardcoded tuple) hold regardless.
  - **1440-1460, 1500-1560** (fingerprint / `_write_region_for` group) — UNCHANGED: `_write_region_for` itself is untouched by this task; every test in this group still passes verbatim.
  - **1636-1665** (`test_write_region_via_run_plan_uses_the_plan_carried_window`, `test_write_region_via_run_plan_uv_part_full_scope_uses_full_window`) — RETARGETED: the partial-scope test now uses `_writes_fill_at_requested_region(0xFF)` (a virgin-chip-shaped probe double) instead of a fixed-offset-0 payload, since the write is now resolved via the probe mechanism rather than a bare region copy — the final captured bytes are unchanged (`generate_pattern(65280, 256)`) because a virgin slot's mask is a no-op. The full-scope test is explicitly retargeted to prove D-C: the OLD assertion ("full" == "partial"'s window) is superseded — a blank chip on "full" scope now gets the FULL-DEVICE pattern, not the top slot; the old assertion is preserved as a comment for the historical record.
- **`test_schema_version_is_one_five`** — RETARGETED (renamed `test_schema_version_is_one_six`): asserts `SCHEMA_VERSION == "1.6"` and the single-sourced literal count for `"1.6"`, matching the plan's own 1.5 → 1.6 bump.

No test was deleted; every retarget is documented above with its reason.

## Post-Change Region/Policy Table (verification step 7)

Measured against the live database, post-implementation:

| Chip | Scope | `is_uv` | Steps `(op, region_policy, write_region)` |
|---|---|---|---|
| M27C512 | full | True | `write` uv-slot `(65280, 256)`; `verify` uv-slot `(65280, 256)` |
| M27C512 | partial | True | `write-partial` uv-slot `(65280, 256)`; `verify` uv-slot `(65280, 256)` |
| AT28C256 | full | False | `write` full-device `(0, 32768)`; `verify` full-device `(0, 32768)`; six SDP-leg ops fixed `(0, 256)` |
| AT28C256 | partial | False | `write-partial` fixed `(32512, 256)`; `verify` fixed `(32512, 256)`; six SDP-leg ops fixed `(32512, 256)` |
| W27C512 | full | False | `write` full-device `(0, 65536)`; `verify` full-device `(0, 65536)` |
| W27C512 | partial | False | `write-partial` fixed `(65280, 256)`; `verify` fixed `(65280, 256)` |
| W29C040 | full | False | `write` full-device `(16384, 491520)`; `verify` full-device `(16384, 491520)` |
| W29C040 | partial | False | `write-partial` fixed `(524032, 256)`; `verify` fixed `(524032, 256)` |

**Plan-time baseline (unchanged, confirmed exactly by the plan's own measured findings):** M27C512 `(65280, 256)` at both scopes; AT28C256 `(0, 256)` at full / `(32512, 256)` at partial; W27C512 `(0, 256)` at full / `(65280, 256)` at partial. W29C040 was not in the plan-time baseline table (added by this task's measured findings, M-4).

**The delta this task ships:** every non-UV chip's `write_scope="full"` region widened from `(0, 256)` to the full device (minus flash4's boot blocks for W29C040); every UV chip's region tuple is numerically UNCHANGED at either scope (the widening for UV parts is a NEW execution-time possibility — D-C's full-device-if-blank branch — not a change to `Step.write_region` itself); partial-scope non-UV regions are unchanged.

## Non-Claims (explicitly not verified)

- **`python tools/check_mypy_watermark.py`** — cannot run in this devcontainer at all: numpy's bundled stubs use a 3.12-only `type` statement, so mypy exits 2 before checking anything. This is a pre-existing, previously-verified environment incompatibility (confirmed again this session, not newly discovered), independent of this task's changes.
- **CI's Python 3.11 leg** — unproven locally; this devcontainer runs Python 3.12. No 3.12-only syntax was introduced (`from __future__ import annotations` is already in place project-wide; no `match`, no PEP 695 `type` statements were added).
- **Bench/hardware behaviour** — no silicon was touched by this task; every verification above is against `FakeChip` (a bench-free double) or the real, on-disk `EpromDatabase`.

## Bench-Runtime Consequence of D-D (recorded, not mitigated)

A full-device write/verify pass on a large non-UV part is now several device-length transfers at 250000 baud (read x2, write x2, verify x2, read-back) rather than the prior fixed 256-byte window — for the largest shipped devices (1 MiB, 8 rows measured at plan time) this is minutes rather than seconds. No size cap was added to avoid this cost: D-D explicitly mandates full-device coverage, and a cap would be an unauthorized scope reduction of a locked decision.

## Issues Encountered

None beyond the three auto-fixed deviations documented above, all surfaced by running the full test suite between tasks as the plan's sequencing requires.

## User Setup Required

None — no external service configuration required. Host-only change; no firmware modification; no dependency added.

## Next Phase Readiness

- All 6 plan tasks complete; full `firestarter_app` suite green (1898 tests, including the post-ship follow-up fix's 5 new tests), ruff lint/format clean, scoped mypy clean (only the pre-existing, unclaimed `submit.py:695` error present), `chip_database.json`/`tools/build_db.py` untouched.
- Commits land on branch `quick-devtest-fullsize-write` inside the `firestarter_app` submodule; the meta-repo gitlink re-pin and docs commit are the orchestrator's responsibility per this task's repo mechanics.
- No blockers. A future bench session should exercise a real full-device write on a large EEPROM (AT28C256/W27C512-class) and a real UV part's probe-and-mask path — this task's guarantees are proven against `FakeChip`, not silicon.

---
*Quick task: 260821-wna*
*Completed: 2026-08-22*

## Self-Check: PASSED

- All 9 created/modified files verified present on disk (`tests/test_uv_mask.py`, `tests/fake_chip.py`, `firestarter/chip_test.py`, `firestarter/diagnostic_report.py`, `firestarter/cli_handlers.py`, `tests/test_chip_test.py`, `tests/test_chip_test_sdp_leg.py`, `tests/test_dev_test_cmd.py`, `tests/test_diagnostic_report.py`).
- All 8 commit hashes verified present in `git log` (`719268b`, `71efded`, `05e0869`, `95005b7`, `fb39828`, `57c1b8f`, `496f6ef`, `1868ab3`).
- Full `firestarter_app` suite re-run green (post-follow-up-fix): 1898 passed, 0 failed.
- Reproduced the coordinator's exact two repro cases directly (bypassing the CLI, calling `_write_coverage_line` with hand-built `Step`/`StepResult` objects mirroring their printed `Step.reason` values): W29C040's carve now discloses the boot-block exclusion (previously `None`); AT29C256's whole-device fallback now discloses the real refusal reason and no longer says "bits clearable".
