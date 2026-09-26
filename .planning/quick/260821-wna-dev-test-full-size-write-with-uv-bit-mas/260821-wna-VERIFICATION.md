---
quick_id: 260821-wna
verified: 2026-08-22T00:00:00Z
status: passed
score: 16/16 must-haves verified (15 on the first pass; the 16th after the gap below was fixed)
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "On a protocol-0x05 (flash4) chip the primary write/verify pass covers the device MINUS the first and last 16 KiB boot blocks, and the excluded region is named in the report with its reason; a flash4 part whose whole device is boot block (the three 32 KiB rows) falls back to the small fixed region with a stated reason and is never reported as a plain FAIL (D-D)."
    status: partial
    reason: >
      The region computation and no-plain-FAIL behavior are correctly implemented and
      verified by live execution. But the "named in the report with its reason" clause is
      FALSE: `derive_plan` computes a correct exclusion/refusal reason string and stores it
      on `Step.reason`, but that string is never threaded into `StepResult.reason` on a
      successful (OK) write. `_write_coverage_line()` and `_step_dict()` both read only
      `StepResult.reason` (always `""` on a clean OK verdict), never `Step.reason`. As a
      result: (a) a genuine flash4 boot-block carve-out (e.g. W29C040) that succeeds
      produces NO "write coverage" row at all -- the exclusion is completely invisible in
      the console, the saved JSON, and the markdown table; (b) the whole-device-is-
      boot-block fallback case (e.g. AT29C256/AT29C257/AT29LV256, all three 32 KiB flash4
      rows) instead renders a misleading UV-slot-shaped line -- `"write coverage: slot 0x0
      (256 bytes), 0 bits clearable"` -- which looks like a saturated UV slot warning on a
      chip that isn't even UV, and never states the real reason (the boot blocks cover the
      entire device). This is reproducible with the project's own `FakeChip` double via
      `derive_plan` + `run_plan` + `DiagnosticReport.render()` -- see evidence below.
    artifacts:
      - path: firestarter_app/firestarter/chip_test.py
        issue: >
          `_dispatch_multi_run`'s OP_WRITE/OP_WRITE_PARTIAL branch (~line 2717-2722)
          unconditionally sets the local `reason = ""` on a clean (non-diverged) OK
          verdict, discarding `step.reason` (the `region_reason` string `derive_plan` set
          for the flash4 carve/fallback case). `StepResult.write_target` (region/pattern/
          bits) DOES carry through correctly -- only the human-readable reason string is
          lost.
      - path: firestarter_app/firestarter/diagnostic_report.py
        issue: >
          `_write_coverage_line()` (~line 502) and `_step_dict()` (~line 664) both read
          `step_row["reason"]`, sourced from `StepResult.reason` only. Neither function has
          access to (or reads) `Step.reason` -- the `Plan.steps[write_step_index].reason`
          value `render()` already holds a reference to via `write_step = self.plan.steps
          [write_step_index]` a few lines above the call. The full-device branch (`if
          policy == REGION_POLICY_FULL_DEVICE: return reason or None`) silently returns
          `None` (no row) whenever the (always-empty) `StepResult.reason` is falsy; the
          fixed-policy branch ignores `reason` entirely and always synthesizes a
          "slot/region ... bits clearable" line even when the underlying cause was a
          refusal reason, not a slot selection.
    missing:
      - "Thread `write_step.reason` (the Step-level, derive_plan-computed exclusion/refusal string) into `_write_coverage_line()`'s full-device and fixed-policy branches -- e.g. pass `write_step.reason` alongside `write_step.region_policy` into `_write_coverage_line`, and prefer it over the always-empty `StepResult.reason` when non-empty."
      - "Add a test that actually renders the report (or inspects `to_dict()`'s `steps[]` reason/`write coverage` console row) for a flash4 chip whose write step SUCCEEDS with a boot-block carve-out (e.g. W29C040) and asserts the boot-block exclusion text appears -- the existing `test_full_device_write_flash4_carves_out_boot_blocks` only checks `write_target.region`/`address_str`, never the report disclosure."
      - "Add the equivalent test for the whole-device-is-boot-block fallback case (AT29C256/AT29C257/AT29LV256) asserting the rendered/JSON reason states the boot-block cause, not a misleading '0 bits clearable' UV-slot-shaped line."
---

# Quick Task 260821-wna Verification Report

**Task Goal:** Make `firestarter dev test` write the full device where physically
possible, and on UV-erasable EPROMs write a bit-masked pattern into whichever slot still
has writable bits — selecting the next slot when the current one is saturated — so UV
parts stay testable without a UV eraser.

**Verified:** 2026-08-22
**Status:** gaps_found
**Branch/commits verified:** `firestarter_app` submodule, branch `quick-devtest-fullsize-write`, 7 commits (`719268b`, `71efded`, `05e0869`, `95005b7`, `fb39828`, `57c1b8f`, `496f6ef`), all confirmed present in `git log` off `beta` tip `f7d3caf`.

## Method

All findings below are from live code execution against the real, on-disk `EpromDatabase`
and the project's own `tests/fake_chip.py::FakeChip` double — not from reading comments or
trusting SUMMARY.md. The full `firestarter_app` test suite was re-run in full (1893 passed,
0 failed, 221.92s) and `ruff check` / `ruff format --check` / scoped `mypy` were re-run
independently. A live programmer board is attached at `/dev/ttyACM0`; the two
`test_no_programmer_found_*` tests were run in isolation and both passed (no environmental
regression to discount).

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Non-UV full device write, pattern is `memory-size` bytes (D-D) | VERIFIED | Live `derive_plan`+`run_plan` on AT28C256/W27C512: `write` step region `(0, 32768)`/`(0, 65536)`, `write_eprom` called with `address_str=None` (start 0) |
| 2 | Flash4 boot-block exclusion, named in report with reason, no plain FAIL (D-D) | **FAILED (partial)** | Region computation and no-FAIL behavior confirmed true; report-disclosure clause reproducibly FALSE — see Gap below |
| 3 | UV bit-masking `P = C & D`, verify against same masked image (D-A) | VERIFIED | `test_uv_used_chip_write_is_genuinely_masked_and_verify_reads_the_region` passed live; manually confirmed `mask_write_pattern` arithmetic |
| 4 | UV slot selection floors are named module constants with reasoning comment (D-B) | VERIFIED | `_UV_MIN_CLEARED_BITS = _UV_MIN_RETAINED_BITS = 64` at chip_test.py:1790-1791, with a reasoning comment above |
| 5 | Degenerate/saturated slot structurally can't report OK; SKIPPED naming saturation (D-B) | VERIFIED | `test_every_slot_saturated_write_is_skipped_never_ok` passed live: `write_eprom` never called, verdict SKIPPED, reason names saturation |
| 6 | Slot advance probes the chip; no cursor persisted to disk (D-B) | VERIFIED | `test_probe_never_persists_a_slot_cursor_to_disk` passed live against a throwaway `FIRESTARTER_CONFIG_DIR` |
| 7 | Blank UV chip + permitting scope gets full-device masked write (D-C) | VERIFIED | Live run: `FakeChip.virgin_uv(65536)` + `write_scope="full"` on M27C512 → write region `(0, 65536)`, `masked=True`, 2×`write_eprom(address_str=None)` |
| 8 | `derive_plan` stays pure/DB-only; mask computed execution-time, carried on `StepResult` (D-02/D-07) | VERIFIED | `derive_plan` reads only `db.get_eprom`/`convert_to_programmer`; mask lives in `_resolve_write_target`, region/policy read-only downstream |
| 9 | Region start reaches the wire via `address_str`; region-scoped absolute-offset reads (M-1/M-3) | VERIFIED | `test_full_device_write_flash4_carves_out_boot_blocks`: `write_eprom` called with `address_str="0x4000"` for a `(16384, 491520)` region; `_read_region` slices `[start:start+length]` off an absolute-offset file |
| 10 | SDP leg stays small/fixed regardless of chip's own write-policy widening (D-D) | VERIFIED | Live `derive_plan` on AT28C256 full scope: write `(0, 32768)` full-device, all six SDP-leg ops `(0, 256)` fixed |
| 11 | `_UV_WRITE_REGION_LENGTH` stays module constant/slot width; SC4/D-01 comments amended not deleted (D-E) | VERIFIED | Comment block at chip_test.py:1749-1758 explicitly "AMENDED (quick task 260821-wna, D-B/D-E)"; `full_device_region`'s sanity check (positive, multiple of slot width, ≤ 16 MiB) confirmed via code read and the AT29C256/W29C040 exercises above |
| 12 | Single short "write coverage" line for non-full-device writes, from report's own dict, no new `dev_test` console call (D-F) | VERIFIED | `test_used_uv_chip_cli_run_carries_slot_region_in_json_and_console` passed live; `dev_test()`'s body has no coverage-line code — it lives entirely in `DiagnosticReport.render()` |
| 13 | All three console gates stay green, unedited expected sets | VERIFIED | `test_check_devtest_orchestrator.py`, `test_characterization.py`, `test_check_diagnostic_report_claims.py` — 66/66 passed live |
| 14 | `_ALWAYS_WRITES_PASS_COUNT` still 6, still derived (not restated) from a live plan | VERIFIED | Constant = 6 (cli_handlers.py:2492); `test_pass_count_is_derived_from_a_live_plan_never_a_literal` passed live |
| 15 | `chip_database.json` / `tools/build_db.py` untouched | VERIFIED | `git diff --stat beta..HEAD -- firestarter/data/chip_database.json tools/build_db.py` is empty |
| 16 | Full suite/ruff/scoped mypy green; CI 3.11 and watermark not claimed | VERIFIED | 1893 passed, 0 failed (live re-run); ruff check/format clean; scoped mypy clean except pre-existing `submit.py:695` error, confirmed introduced 2026-07-28 (`d4f81300`), unrelated to this task |

**Score:** 15/16 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/chip_test.py` | Region/mask/slot arithmetic, execution-time resolver | VERIFIED (substantive, wired) | 862-line diff; `mask_write_pattern`, `bits_cleared_by`, `bits_retained_by`, `uv_slot_starts`, `full_device_region`, `WriteTarget`, `_resolve_write_target` all present, exercised by live tests |
| `firestarter_app/tests/fake_chip.py` | UV-physics + absolute-offset test double | VERIFIED | 236 lines, genuine AND-write physics and seek-reproducing reads, used across `test_chip_test.py`/`test_dev_test_cmd.py` |
| `firestarter_app/tests/test_uv_mask.py` | Pure arithmetic/guard tests | VERIFIED | 279 lines, new file, collected and passing |
| `firestarter_app/firestarter/diagnostic_report.py` | Schema 1.6, D-F console row | VERIFIED with a defect | Schema bump and additive keys present and wired; the coverage-row content is INCOMPLETE for the flash4 disclosure case (see Gap) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `derive_plan` → `Step.write_region`/`region_policy` → execution-time resolver | region decided once, mask execution-time | WIRED | Confirmed: `derive_plan` never touches chip; `_resolve_write_target` reads `step.write_region`/`region_policy`/`full_device_permitted` read-only |
| write `StepResult.write_target` → `WriteContext` → verify dispatch | verify uses the write's actual resolved target | WIRED | Confirmed via `test_uv_used_chip_write_is_genuinely_masked_and_verify_reads_the_region` (verify OK against the masked image) |
| `operator.read_eprom(address_str=, size_str=)` → `_write_to_file` seek → `_read_region` slice | absolute-offset region reads | WIRED | Confirmed via `test_sdp_leg_readback_reproduces_absolute_offset_seek` and manual `_read_region` trace |
| `_dispatch_sdp_leg` length gate → region-scoped read-back | M-2 fix | WIRED | Confirmed via `test_sdp_leg_length_gate_passes_against_a_full_size_readback_double` |
| `Step.reason` (derive_plan's exclusion/refusal text) → `StepResult.reason` → `DiagnosticReport` console/JSON | write-coverage disclosure (D-D/D-F) | **NOT WIRED** | `Step.reason` is set correctly by `derive_plan` but the OK-verdict path in `_dispatch_multi_run` overwrites `StepResult.reason` with `""`; `_write_coverage_line`/`_step_dict` read only `StepResult.reason`. Live-reproduced below. |
| `_resolve_write_scope`'s prompt → operator consent → D-C outcome | truthful UV consent (D-C) | WIRED | Prompt text confirmed accurate; `test_uv_prompt_names_both_outcomes` passed live |

### Live Reproduction of the Gap

```
$ python3 - <<'EOF'
... derive_plan("W29C040", db, write_scope="full") + run_plan(plan, FakeChip.non_uv(524288), db)
... report.render(console)
EOF
StepResult: write OK ''      # <- reason lost; Step.reason held the boot-block exclusion text
StepResult: verify OK ''
# rendered table has NO "write coverage" row at all
```

```
$ python3 - <<'EOF'
... derive_plan("AT29C256", db, write_scope="full") + run_plan(plan, FakeChip.non_uv(32768), db)
... report.render(console)
EOF
│ write coverage     │ slot 0x0 (256 bytes), 0 bits clearable │
```
AT29C256 is a non-UV EEPROM whose entire 32 KiB is boot block (protocol 0x05); the write
correctly fell back to the pre-existing `(0, 256)` region and correctly returned OK (never
a plain FAIL) — but the rendered line is a UV-slot-shaped "0 bits clearable" message, not
the real reason ("flash4 boot blocks cover the entire 32768-byte device"), which
`derive_plan` had already computed and stored on `Step.reason` at plan time.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full suite | `python -m pytest tests/ -q -o addopts=""` | 1893 passed, 0 failed, 221.92s | PASS |
| Ruff lint | `ruff check chip_test.py cli_handlers.py diagnostic_report.py` | All checks passed | PASS |
| Ruff format | `ruff format --check ...` | 3 files already formatted | PASS |
| Scoped mypy | `mypy chip_test.py cli_handlers.py diagnostic_report.py` | 1 pre-existing error in submit.py (unclaimed, unrelated) | PASS |
| Console gates | 3 gate test files | 66/66 passed | PASS |
| `test_no_programmer_found_*` (board attached at /dev/ttyACM0) | isolated run | 2/2 passed | PASS — no environmental regression |
| 9 targeted behavioral tests (D-A/B/C/D) | `pytest -k "..."` | 9/9 passed | PASS |
| D-F CLI provenance test | `TestWriteCoverageProvenanceD_F` | 1/1 passed | PASS |
| SDP leg M-2/M-3 fix tests | 2 targeted tests | 2/2 passed | PASS |
| Constant-derivation test | `test_pass_count_is_derived_from_a_live_plan_never_a_literal` | 1/1 passed | PASS |
| Live `derive_plan` region table (M27C512/AT28C256/W27C512/W29C040) | direct script | Matches SUMMARY's claimed table exactly | PASS |
| Live flash4 whole-device-boot-block fallback (AT29C257/AT29C256/AT29LV256) | direct script | Falls back correctly, but reason is lost in report | **FAIL (see gap)** |

### Requirements Coverage

| Requirement | Description | Status | Evidence |
|-------------|-------------|--------|----------|
| QUICK-260821-wna | Full-device write on non-UV chips; bit-masked slot-selected writes on UV chips | PARTIAL | 15/16 must-have truths hold; the flash4 report-disclosure clause of the D-D truth fails |

### Anti-Patterns Found

None. No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers in any of the 9 touched
files. No stub returns, no hardcoded empty data flowing to output.

## Gaps Summary

Six of the seven `verify_these_specifically` items check out cleanly against live code
execution: D-C's virgin-UV-gets-full-device-write, D-D's non-UV full-size coverage with
capped SDP legs, D-E's amended (not deleted) SC4/D-01 comments with the slot width staying
a module constant, the region-start-reaches-the-wire fix (`address_str` threading), and
`_ALWAYS_WRITES_PASS_COUNT` staying derived and unedited are all genuinely implemented and
covered by tests that actually exercise the claimed behavior.

The seventh item — D-D's boot-block exclusion "handled... with a visible stated reason" —
is only half-true. The *mechanism* (region computation, fallback, never-a-plain-FAIL) is
solid. But the *disclosure* the plan explicitly required ("named in the report with its
reason") does not reach the console, the saved JSON, or the markdown table: `Step.reason`
(set correctly by `derive_plan`) is discarded on every successful write and replaced with
an empty string before `DiagnosticReport` ever sees it. The existing test suite did not
catch this because the two tests that exercise the flash4 carve-out
(`test_full_device_write_flash4_carves_out_boot_blocks`,
`test_derive_plan_full_device_region_flash4_carves_boot_blocks`) both check region/pattern/
`Step.reason` at the `Plan`/`WriteTarget` level, never the rendered report or the JSON
`reason` field the D-D must-have actually names. This is a real coverage gap in the
executor's own test suite, not a nitpick — a community `dev test` run against a flash4 part
today gets either total silence or an actively misleading "0 bits clearable" line where the
plan promised a stated reason.

---

*Verified: 2026-08-22*
*Verifier: Claude (gsd-verifier)*


## Resolution (2026-08-22)

The single gap above — D-D's *disclosure* half — was fixed in `1868ab3`
(`fix(260821-wna): D-D disclosure was reading the wrong reason field`) and
independently re-verified by the orchestrator. Status flipped
`gaps_found` -> `passed` on that evidence, not on the executor's claim.

**Root cause.** `derive_plan` records the exclusion/refusal text on
`Step.reason` (plan-time), but `_dispatch_multi_run` clears
`StepResult.reason` to `""` on any clean OK write (`chip_test.py:2723`), and
`_write_coverage_line` read only `StepResult.reason`. So the full-device
branch's `return reason or None` yielded `None` on exactly the successful
path, and the `fixed` policy branch fell through to UV slot wording.

**Fix.** `_write_coverage_line(result, step)` now reads `step.reason` for the
disclosure; the "N bits clearable" phrasing is gated on `target.masked` so it
can no longer appear on a non-UV part; and the line is computed once into an
additive `write_coverage` JSON key so it reaches the filed-issue JSON as well
as the console.

**Independent re-verification** (orchestrator, on the exact clean-OK-write
condition that hid the gap — `StepResult.reason == ""`):

| chip | policy | rendered coverage line |
|---|---|---|
| W29C040 | `full-device` | names the first/last 16384-byte flash4 boot-block exclusion |
| AT29C256 | `fixed` | states the refusal reason; no "bits clearable" |
| AT29C257 | `fixed` | states the refusal reason; no "bits clearable" |
| AT29LV256 | `fixed` | states the refusal reason; no "bits clearable" |

**Why it escaped a green suite** — worth keeping, it is a recurring shape in
this project: the pre-fix tests asserted `write_target.region`,
`address_str` and `Step.reason`, but never rendered the report or read the
JSON. 1893 passing tests therefore coexisted with an operator-invisible
exclusion. The 5 tests added with the fix drive `derive_plan` + `run_plan` +
`render()`/`to_dict()` end-to-end, so the disclosure itself is now gated.

**Post-fix gates, run by the orchestrator (not the executor):** full suite
1898 passed / exit 0 / 32 snapshots; `ruff check` and `ruff format --check`
clean; `chip_database.json` and `tools/build_db.py` untouched vs `beta`.
