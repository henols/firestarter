---
phase: 195-partial-writes-stop-destroying-the-page
verified: 2026-09-16T00:00:00Z
status: human_needed
score: 4/4 must-haves verified
covered_files:
  - .planning/REQUIREMENTS.md
  - .planning/phases/195-partial-writes-stop-destroying-the-page/195-01-PLAN.md
  - .planning/phases/195-partial-writes-stop-destroying-the-page/195-01-SUMMARY.md
  - .planning/phases/195-partial-writes-stop-destroying-the-page/195-02-PLAN.md
  - .planning/phases/195-partial-writes-stop-destroying-the-page/195-02-SUMMARY.md
  - .planning/phases/195-partial-writes-stop-destroying-the-page/195-03-PLAN.md
  - .planning/phases/195-partial-writes-stop-destroying-the-page/195-03-SUMMARY.md
  - .planning/phases/195-partial-writes-stop-destroying-the-page/195-04-PLAN.md
  - .planning/phases/195-partial-writes-stop-destroying-the-page/195-04-SUMMARY.md
  - .planning/phases/195-partial-writes-stop-destroying-the-page/195-05-PLAN.md
  - .planning/phases/195-partial-writes-stop-destroying-the-page/195-05-SUMMARY.md
  - .planning/phases/195-partial-writes-stop-destroying-the-page/195-REVIEW.md
  - .planning/v1.39/195-partial-write-refusal-record.md
  - .planning/v1.39/195-w29c020-partial-write-bench-transcript.md
  - VALIDATED-EPROMS.md
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/firestarter/exceptions.py
  - firestarter_app/firestarter/messages.py
  - firestarter_app/firestarter/page_size_gate.py
  - firestarter_app/tests/test_page_size_alignment_refusal.py
  - firestarter_app/tests/test_page_size_write_refusal.py
  - firestarter_app/tests/test_validated_parts_regression_surface.py
  - firestarter_fw/include/messages.h
  - firestarter_fw/src/proms/flash_5v_page.cpp
  - firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp
  - tools/catalog/messages.toml
covered_digest: "v1:sha256:3270c183277db0746b8687599d24a18302e38e5c40752384e37e5b288961560b"
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Decide whether WR-01 (require_page_alignment accepts a negative address string as falsely 'aligned') needs a fix before this phase is considered fully closed."
    expected: "Either (a) accept as known, filed debt with an explicit override/todo, or (b) require a fix (reject negative start before the modulo check) before closing."
    why_human: "Live-reproduced against the current tree (firestarter write W29C020 ... -a -256 passes the host guard with no refusal). The code review (195-REVIEW.md WR-01) could not determine what firestarter_fw's json_parser.c does with a negative address on the wire, so whether this can actually cause an out-of-range or unintended write is unresolved by static analysis and the phase's own bench evidence never exercised a negative address. It is outside the literal scope of the four ROADMAP success criteria (which are about page alignment/length, not address sign), so it does not fail a truth, but it is a live, reproducible gap in the exact code area (write-address validation) this phase's charter concerns, and no artifact in this phase closes it or files it as a todo."
---

# Phase 195: Partial Writes Stop Destroying the Page Verification Report

**Phase Goal:** A partial or unaligned write either leaves the rest of the physical page intact, or
refuses and changes nothing — and in no case reports success over bytes it erased.
**Verified:** 2026-09-16
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | A partial or unaligned write to a protocol `0x05` part preserves every touched byte, **or** refuses with a named error and leaves the device unchanged | ✓ VERIFIED | Refusal branch chosen (D-01). Firmware guard confirmed at `firestarter_fw/src/proms/flash_5v_page.cpp:87-95` — refuses with `\|\|` (not `&&`) before the `for` loop, zero register writes on the refused path. Host guard confirmed at `firestarter_app/firestarter/page_size_gate.py:132-183` (`require_page_alignment`), wired into both `eprom_operations.py:2009-2011` and `cli_handlers.py:767-770`, ahead of `_operation_context`/port-open. **Behaviorally proven on real silicon**: `195-w29c020-partial-write-bench-transcript.md` §4h — post-fix build refuses the identical trailing/leading/interior commands, exits 1, prints no success line, and a full read-back hashes identical to the pre-refusal baseline (`sha256` match), proving the device is provably unchanged rather than merely asserted. The transcript explicitly attributes all three refusals to the **host** layer (no `Connecting...` line preceded any error) and does not claim the firmware-layer refusal alone leaves the device unchanged — matching the required narrower claim (D-01 §3, review-context item 1). |
| 2 | No protocol `0x05` write reports `successful` when bytes outside the requested range were erased | ✓ VERIFIED | Pre-fix bench legs (`§4d`, `§4e`, `§4g`) reproduce the defect: `Write to W29C020 successful` printed while `sha256`-confirmed erasure occurred outside the requested range (trailing, leading, and — on a corrected 2048B payload — interior). Post-fix bench legs (`§4h`) for the identical commands: exit 1, no success line, device unchanged. Native suite independently proves the same invariant for every rejected class (`test_5v_page_write_execute_refuses_unaligned_start`, `..._refuses_partial_length`, `..._refuses_unaligned_start_and_partial_length`, `..._refuses_single_byte_payload`, `..._refuses_unaligned_second_chunk`) — each asserts `RESPONSE_CODE_ERROR` **and** `bus_recording_count() == 0`, run live: 38/38 pass in `pio test -e native -f "*test_val_5v_page*"`. |
| 3 | Both loss directions demonstrated on real silicon (before-start and after-end), on a part whose page size is already correct, isolating this from Phase 194's defect | ✓ VERIFIED | `W29C020` confirmed already-correct pre-Phase-194 (`.planning/v1.39/194-page-size-27-row-record.md:51` — "equal (already correct pre-Phase-194)"). Bench transcript §4d (trailing loss, `0x040-0x07F` erased) and §4e (leading loss, `0x000-0x03F` erased) both captured against a pre-fix build with exact byte ranges, `sha256` baselines, and the defective success line recorded. The derived third (interior chunk-boundary) direction is explicitly and correctly framed in both the transcript (§4g: "This is the first silicon observation of direction 3... previously derived from source... never run") and `REQUIREMENTS.md` ("a bonus finding beyond what WRITE-03 requires, not a substitute for the two directions it names") — no overclaim found. |
| 4 | The four validated parts (`W29C020`, `W29C040`, `SST39SF020`, `AE29F2008`) are re-checked against the new behaviour | ✓ VERIFIED | Independently confirmed from the shipped database (not merely from the plan's own test): `SST39SF020,SST39SF020A` carries `algorithm: 6` (verified live: `{'algorithm': 6, ...}`), **not** `FLASH4_PROTOCOL_ID` (`5`) — it never traverses `flash_5v_page.cpp` and the D-07 scope reduction is sound. `AE29F2008` and `W29C020,W29C020C,W29C022` are byte-identical rows except `part_number` (both `algorithm: 5`, `page_size: 128`, `chip_id_value: 0x0000da45`) — confirmed live — so the W29C020 bench result applies to AE29F2008 by database-proven silicon identity. `W29C040,W29C042` carries `algorithm: 5`, `page_size: 256`, covered by the native 7+2-geometry boundary suite (`accepts_aligned_two_chunk_p256`, etc.). `test_validated_parts_regression_surface.py` — 5/5 passing, run live. `VALIDATED-EPROMS.md` records the `SST39SF020` scope correction in `## Notes`, verified present. |

**Score:** 4/4 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `tools/catalog/messages.toml` / `firestarter_fw/include/messages.h` / `firestarter_app/firestarter/messages.py` | `MSG_ERR_FL4_PAGE_ALIGN` at `0xC0`, ERROR severity, u24+u16 params | ✓ VERIFIED | Confirmed present and generated in all three; `codegen.py --check` → `OK: catalog valid (79 messages, version 1)`. |
| `firestarter_fw/src/proms/flash_5v_page.cpp` | Per-chunk alignment guard before the byte loop | ✓ VERIFIED | Guard at line 87, `for` loop at line 96 — guard strictly precedes the loop; both refusal paths `return` before any `firestarter_set_data` call. |
| `firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` | Full rejection/acceptance matrix, incl. interior chunk-boundary case | ✓ VERIFIED | 9 new `RUN_TEST` registrations confirmed by name; full file run live: 38/38 cases pass. |
| `firestarter_app/firestarter/page_size_gate.py` | `require_page_alignment`, `_ACCEPTED_PAGE_SIZES` | ✓ VERIFIED | Both present; `_ACCEPTED_PAGE_SIZES` used inside `require_page_size` (line 128) but **not** inside `require_page_alignment` (WR-03, see Anti-Patterns). |
| `firestarter_app/firestarter/exceptions.py` | `PageAlignmentError(EpromOperationError)` | ✓ VERIFIED | Present, correct subclass. |
| `firestarter_app/firestarter/cli_handlers.py` | Pre-flight call + dedicated `except PageAlignmentError` arm above generic `EpromOperationError` | ✓ VERIFIED | Confirmed at lines 767-770 (call) and 219-221 (arm, above line 223's generic arm). |
| `firestarter_app/firestarter/eprom_operations.py` | Operator-layer call before `_operation_context` | ✓ VERIFIED | Confirmed at lines 2009-2011, ahead of the context manager. |
| `firestarter_app/tests/test_page_size_alignment_refusal.py`, `test_page_size_write_refusal.py`, `test_validated_parts_regression_surface.py` | Full property/regression matrices | ✓ VERIFIED | Run live: 29 + 21 + (5 of the 21) passed, 0 failures. |
| `.planning/v1.39/195-partial-write-refusal-record.md` | Phase decision record | ✓ VERIFIED | 6 sections present, explicit authority-boundary statement in §6. |
| `.planning/v1.39/195-w29c020-partial-write-bench-transcript.md` | Silicon evidence | ✓ VERIFIED | 5 sections, explicit scope-limitation statement in §5, hashes and exact byte ranges recorded throughout. |
| `VALIDATED-EPROMS.md` | `SST39SF020` scope-correction Notes bullet | ✓ VERIFIED | Present, table unchanged (27 rows). |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `tools/catalog/messages.toml` | `firestarter_fw/include/messages.h`, `firestarter_app/firestarter/messages.py` | `sync_to_subrepos.sh` | WIRED | All three define `MSG_ERR_FL4_PAGE_ALIGN` = `0xC0`, confirmed by direct grep. |
| `page_size_gate.require_page_alignment` | `eprom_operations.py` / `cli_handlers.py` | direct call, both call sites ahead of `require_page_size` in source order per-repo | WIRED | Confirmed: both files call `require_page_size(...)` then `require_page_alignment(...)`, in that order, before any port/context opens. |
| `exceptions.PageAlignmentError` | `cli_handlers.map_typed_errors` | dedicated `except` arm | WIRED | Confirmed arm present above the generic `EpromOperationError` arm; independently confirmed correct via a direct-decorator test (`test_page_alignment_error_renders_verbatim_with_no_generic_prefix`) that bypasses the CLI-duplicate-gate confound (see WR-02 below). |
| `flash_5v_page.cpp page_mask` | new alignment guard | reused, not recomputed | WIRED | Confirmed: guard condition uses `page_mask` (bitmask `&`), no `%` operator against `handle->address`/`handle->data_size` anywhere in the file. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Firmware refuses unaligned/partial chunk with zero register writes; page-exact chunk still succeeds | `pio test -e native -f "*test_val_5v_page*"` | `38 test cases: 38 succeeded` | ✓ PASS |
| Host refuses unaligned/partial write pre-connect; page-exact write reaches the operation context | `pytest tests/test_page_size_alignment_refusal.py` | `29 passed` | ✓ PASS |
| Host rejects invalid recorded page sizes (96/1024/65535), accepts valid ones | `pytest tests/test_page_size_write_refusal.py` | `16 passed` (part of 21 combined) | ✓ PASS |
| Criterion 4's four-part regression surface measured from the shipped database | `pytest tests/test_validated_parts_regression_surface.py` | `5 passed` | ✓ PASS |
| Catalog validity | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` | `OK: catalog valid (79 messages, version 1)` | ✓ PASS |
| Negative-address alignment gate (WR-01 live reproduction) | `require_page_alignment('W29C020', {...page-size:128}, 'write', '-256', <128B file>)` | No exception raised — treated as aligned | ✗ FAIL (see Anti-Patterns / Human Verification) |

### Probe Execution

Not applicable — this phase's evidence is native/host unit tests plus a hand-driven silicon bench
session (`.planning/v1.39/195-w29c020-partial-write-bench-transcript.md`), not a `scripts/*/tests/probe-*.sh` convention. No such probes exist for this phase; skipped per Step 7c's discovery scope.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| WRITE-01 | 01, 02, 03, 04, 05 | Partial/unaligned write preserves or refuses+leaves-unchanged | ✓ SATISFIED | Bench §4h + native 38/38 + host 29+21 passing; `REQUIREMENTS.md` citation checked and accurate |
| WRITE-02 | 01, 03, 04, 05 | No `successful` report over erased-outside-range bytes | ✓ SATISFIED | Bench §4d/§4e/§4g (defect on pre-fix) + §4h (no success line post-fix); citation accurate |
| WRITE-03 | 05 | Both loss directions on real silicon, isolated from PAGE-01/02 | ✓ SATISFIED | Bench §4d (trailing), §4e (leading), W29C020 confirmed already-correct pre-Phase-194; citation accurate |

No orphaned requirements: `WRITE-01`, `WRITE-02`, `WRITE-03` are the only IDs REQUIREMENTS.md maps to
Phase 195, and all three appear in at least one plan's `requirements:` frontmatter field.

### Anti-Patterns Found

Carried forward from `195-REVIEW.md` (a required-reading input to this verification) and
independently re-reproduced live against the current tree — not merely cited from the review.

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `firestarter_app/firestarter/page_size_gate.py` | 154-156 | `require_page_alignment`'s modulo check does not reject a negative parsed address; `-256 % 128 == 0` in Python reads as "aligned" | ⚠️ Warning (elevated to human verification below) | Live-reproduced: `firestarter write W29C020 ... -a -256` passes the host guard with no refusal. Downstream firmware handling of a negative wire address is unconfirmed (review's own words: "I cannot fully verify"). Not shown to reproduce this phase's specific WRITE-02 defect (both plausible downstream outcomes remain page-aligned or get caught elsewhere), but it is a live gap in write-address validation, in the exact module this phase shipped. |
| `firestarter_app/tests/test_page_size_alignment_refusal.py` | 332-350 | `test_page_alignment_error_renders_through_cli_write_command` never reaches the mocked `operator.write_eprom` — the CLI's own duplicate `require_page_alignment` call fires first for the chosen (genuinely misaligned) inputs | ⚠️ Warning | Live-reproduced (`operator.write_eprom.called == False`). Test-quality gap only: the property it claims to prove (map_typed_errors renders a `PageAlignmentError` raised deep inside `write_eprom`) is independently proven by `test_page_alignment_error_renders_verbatim_with_no_generic_prefix` (a direct-decorator test) and by the bench transcript's real end-to-end CLI runs (§4h), so production behavior is not in doubt — only this one test's name/docstring overclaims what it covers. |
| `firestarter_app/firestarter/page_size_gate.py` | 132-183 | `require_page_alignment` does not itself validate `page_size` membership in `_ACCEPTED_PAGE_SIZES` before using it as a modulus; relies on caller-ordering (`require_page_size` always called first) | ⚠️ Warning | Confirmed: `_ACCEPTED_PAGE_SIZES` referenced only inside `require_page_size` (line 128), not inside `require_page_alignment`. Both current call sites confirmed to call `require_page_size` immediately before `require_page_alignment`, so no live defect today; fragile against a future standalone caller. |
| `firestarter_app/firestarter/page_size_gate.py` | 168-173 | `os.path.getsize` on a directory path does not raise, so a directory `input_file` sails through as "page-exact" and later crashes with an unhandled `IsADirectoryError` | ℹ️ Info | Pre-existing crash class, one function call later regardless of this guard; UX gap, not a data-corruption risk. |

No 🛑 Blocker anti-patterns and no unresolved debt markers (`TBD`/`FIXME`/`XXX`) found in any file
this phase modified — confirmed by direct grep across all 8 touched production/test files.

### Human Verification Required

1. **Decide whether WR-01 needs a fix before this phase closes**
   - **Test:** Run `firestarter write W29C020 <64-byte-file> -a -256` (or equivalent, against
     `require_page_alignment` directly) against the current tree.
   - **Expected:** Either the guard refuses (fix applied) or the project explicitly accepts this as
     known, filed debt (a todo, or a VERIFICATION override).
   - **Why human:** This is a live, reproducible gap in write-address validation in the exact module
     this phase shipped (`page_size_gate.require_page_alignment`), and the code review itself could
     not resolve what happens once a negative address crosses the wire into firmware — both
     plausible outcomes it names are "bad" in different ways. It falls outside the four ROADMAP
     success criteria's literal wording (which concern page alignment/length, not address sign), so
     it is not marked as a failed truth, but no artifact in this phase's five plans fixes it or files
     it as a todo (the three todos plan 04 filed — host-side splicing, override-flag contract,
     dev-test region rounding — do not cover it), and the code review's suggested one-line fix
     (`if start < 0: raise PageAlignmentError(...)`) remains unapplied as of this verification.

### Gaps Summary

No must-have truth failed. All four ROADMAP success criteria are verified with concrete,
independently-reproduced evidence: live-run native tests (38/38), live-run host tests (29+21+5
passing), live database queries confirming the criterion-4 scope reduction, and the committed
silicon bench transcript's hashes and byte ranges cross-checked against its own claims (no
overclaim found on the refusal-branch-only "device unchanged" claim, the criterion-4 SST39SF020
scope reduction, or the interior-loss finding's "beyond WRITE-03" framing — all three of the
verification context's flagged scrutiny points held up).

The phase is marked `human_needed` rather than `passed` solely because of one unresolved,
live-reproduced code-review WARNING (WR-01) that touches this phase's own charter (write-time data
safety) and was neither fixed nor filed as accepted debt. The other two review WARNINGs (WR-02,
WR-03) and the one INFO finding are recorded for completeness but do not, on inspection, represent
open data-safety risk — WR-02 is a test-quality gap covered by other passing evidence, WR-03 is a
non-live "fragile but not wrong today" ordering dependency, and IN-01 is a pre-existing UX gap.

---

_Verified: 2026-09-16_
_Verifier: Claude (gsd-verifier)_
