---
phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur
plan: 08
subsystem: bench-hardware
tags: [avrdude, uno, flash-provenance, read-back, falsification, cross-flash, on-device]

requires:
  - phase: 160-01
    provides: "rig-pins.json (avrdude/objcopy/pio pins, arms.*.venv_bin, forbidden_flags/binaries, config_dir)"
  - phase: 160-02
    provides: "images/ (six arm-tagged .hex files) + BUILD-MANIFEST.json's per-image hex_span and measured_divergence_finding"
  - phase: 160-04
    provides: "tools/probe_board.py, tools/gate_record.py"
  - phase: 160-05
    provides: "tools/judge_readback.py"
  - phase: 160-06
    provides: "PROCEDURE.md's P-01..P-11 step sequence and its Standing bench rules"
  - phase: 160-07
    provides: "bench/EVIDENCE.jsonl's pinned _schema, tools/render_evidence.py, tools/run_gates.sh"
provides:
  - "The uno flash+read-back chain proven on a real device for the first time in this project's history: signature probe, PlatformIO flash, independent avrdude 8.1 read-back judged against the flashed arm's own hex extent"
  - "D-03 on uno: a real deliberate wrong-arm cross-flash observed producing a MISMATCH (22367/26026 differing bytes), then a correction observed matching, both recorded in CROSSFLASH.md and appended to EVIDENCE.jsonl"
  - "A read-cost baseline for plans 09/10: ~5.5s wall-clock per avrdude read + objcopy normalize on this chain"
  - "Three rig-tooling bugs found and fixed against real inputs (a wrong avrdude-8.1 stderr format assumption in probe_board.py, a list-vs-dict manifest-shape crash and an arm-agnostic-span defect in judge_readback.py, and a missing git argv0 allowance in gate_record.py), each with new --selftest coverage"
affects: ["160-09", "160-10", "160-13", "161", "162", "163"]

tech-stack:
  added: []
  patterns:
    - "hex_span_expected_by_arm: a per-arm mapping added to rig-pins.json targets.*, consulted first by judge_readback.py's cross_check_hex_span() (keyed by --expect-arm), with the pre-existing flat hex_span_expected kept unedited for backward compatibility -- the general shape for representing a genuinely arm-dependent pinned quantity without breaking any reader that still consults the flat key"
    - "SHA256SUMS.txt informational context moves into '#' comment lines (ignored by `sha256sum -c`), never into a checksum line's filename column -- the filename column must name only a real, already-written file"

key-files:
  created:
    - .planning/v1.34/bench/cells/BRINGUP-uno/probe.json
    - .planning/v1.34/bench/cells/BRINGUP-uno/READBACK-VERDICT.json
    - .planning/v1.34/bench/cells/BRINGUP-uno/flash_readback.bin
    - .planning/v1.34/bench/cells/BRINGUP-uno/judged_span.bin
    - .planning/v1.34/bench/cells/BRINGUP-uno/expected_span.bin
    - .planning/v1.34/bench/cells/BRINGUP-uno/SHA256SUMS.txt
    - .planning/v1.34/bench/cells/BRINGUP-uno/CROSSFLASH.md
    - .planning/v1.34/bench/cells/BRINGUP-uno/crossflash/ (the deliberate-mismatch read-back and its verdict)
    - .planning/v1.34/bench/cells/BRINGUP-uno/logs/ (12 invocation captures + a structured commands index)
  modified:
    - .planning/v1.34/rig-pins.json
    - .planning/v1.34/tools/probe_board.py
    - .planning/v1.34/tools/judge_readback.py
    - .planning/v1.34/tools/gate_record.py
    - .planning/v1.34/bench/EVIDENCE.jsonl
    - .planning/v1.34/bench/EVIDENCE.md

key-decisions:
  - "Flashed the control arm first (task 2's baseline) and left it on the board at teardown (task 3's correction), exactly matching the plan's own stated intent -- the arm on the board at the end is the one this plan leaves behind deliberately, not incidentally."
  - "Resolved the plan-vs-rig-pins arm-span inconsistency by treating BUILD-MANIFEST.json's per-image hex_span as authoritative (it is what judge_readback.py's own cross-check already enforces) and recording judged_span_bytes=26026 for the control arm, not the plan's originally-stated 22952 (which is v133's span). rig-pins.json's targets.*.hex_span_expected is arm-agnostic for a genuinely arm-dependent quantity; fixed by adding a per-arm hex_span_expected_by_arm map for all three targets (uno/uno328pb/leonardo) so plans 09/10 inherit the fix rather than re-discovering the same gap."
  - "controller_string is recorded as 'not measured -- <reason>', not left blank and not faked: `hw`'s CLI handler (cli_handlers.py:969) calls `_build_op_flags()` with zero kwargs, so FLAG_VERBOSE is never forwarded onto the wire regardless of the CLI's own -v flag, so firmware's FLAG_VERBOSE-gated MSG_INFO_FW line is never emitted by `hw` -- confirmed live, pre- and post-flash. This is a genuine host-app limitation and out of scope for this phase to fix (D-16: no product-code changes); it will recur identically for every future cell's controller_string via capture_provenance.py's identical hw-based probe until a host-app fix forwards verbose into hw's wire flags."
  - "PlatformIO's avrdude resolution is PER-ENV, not a single choice, and is never a violation of this rig's forbidden-binary rule: `uno`/`leonardo` resolve avrdude 6.3 (protocols `arduino`/`avr109`, both of which 6.3 can drive), `uno328pb` resolves avrdude 8.1 (protocol `urclock`, which 6.3 cannot drive at all -- MiniCore's ATmega328PB.json pins ~1.80100.0 for exactly this reason). There is no target on which PlatformIO hands a protocol to an avrdude build incapable of it, so no override of PlatformIO's resolution is needed on any target. Corrected 2026-08-27 per orchestrator spot-check from an earlier draft that stated this as a general property of the upload path rather than per-env -- full measurement table in CROSSFLASH.md and the Findings section below. `rig-pins.json`'s `forbidden_binaries` entry governs this rig's own direct invocations only (probe_board.py, judge_readback.py, both of which correctly used the pinned 8.1 binary exclusively); D-01's separation-of-code-paths property still holds."

requirements-completed: []

coverage:
  - id: D1
    description: "Task 1 (operator-physical gate): device node re-verified against a pre-gate enumeration, operator's board declaration and socket-state declaration recorded verbatim and cross-checked against the avrdude signature probe -- they agree"
    verification:
      - kind: other
        ref: "probe.json's device_node_enumeration_check + operator_probe_agreement fields (this SUMMARY quotes the agreement); no CLI equivalent exists for a physical checkpoint"
        status: pass
    human_judgment: false
  - id: D2
    description: "Task 2: the uno read chain proven on a real device -- signature probe, control-arm flash via PlatformIO, independent avrdude 8.1 read-back (32768 B) judged true against the control arm's own hex extent (26026 B, the arm-correct value), whole-flash SHA recorded distinct and unjudged, ~5.5s cost baseline recorded"
    requirement: "RIG-01"
    verification:
      - kind: unit
        ref: "python3 .planning/v1.34/tools/judge_readback.py --target uno --port /dev/ttyACM0 --flashed-arm control --expect-arm control ... -- rc=0, judged_match=true, judged_span_bytes=26026"
        status: pass
      - kind: other
        ref: "cd .planning/v1.34/bench/cells/BRINGUP-uno && sha256sum -c SHA256SUMS.txt -- both judged_span.bin and flash_readback.bin report OK"
        status: pass
    human_judgment: false
  - id: D3
    description: "Task 3 (D-03): deliberate v1.33-on-uno cross-flash judged against the control arm's hex reported a real MISMATCH (rc=1, 22367/26026 differing bytes, first offsets/bytes recorded), the whole-flash SHA independently confirmed the content moved, then the correction flash was observed matching again with a byte-identical whole-flash SHA to the pre-crossflash baseline; one bring-up row appended to bench/EVIDENCE.jsonl, gate-green"
    requirement: "RIG-01"
    verification:
      - kind: unit
        ref: "python3 .planning/v1.34/tools/judge_readback.py --target uno --port /dev/ttyACM0 --flashed-arm v133 --expect-arm control ... -- rc=1, judged_match=false, diff_count=22367"
        status: pass
      - kind: unit
        ref: "python3 .planning/v1.34/tools/gate_record.py --jsonl .planning/v1.34/bench/EVIDENCE.jsonl -- rc=0, 0 violations"
        status: pass
      - kind: other
        ref: "python3 .planning/v1.34/tools/render_evidence.py --jsonl ... --target ... --check -- rc=0, matches a fresh render"
        status: pass
      - kind: other
        ref: "bash .planning/v1.34/tools/run_gates.sh -- rc=0, 11/11 tool selftests + 5/5 live gates, ALL GATES PASSED"
        status: pass
    human_judgment: false

duration: ~2h
completed: 2026-08-27
status: complete
---

# Phase 160 Plan 08: BRINGUP-uno — Flash + Read-Back Provenance Proven on a Real Device Summary

**Proved the avrdude flash read-back chain on a real Arduino Uno for the first time in this project's history — a control-arm flash judged matching by an independent read-back, then a deliberate v1.33-on-uno cross-flash judged against the control arm's hex producing a real, measured MISMATCH (22367/26026 differing bytes), then a clean correction — while finding and fixing three genuine rig-tooling defects that would otherwise have broken this chain (and, for one of them, every later cell in the milestone) on first real-device contact.**

## Performance

- **Duration:** ~2h (includes three in-phase tool bug fixes, each with new selftest coverage)
- **Tasks:** 3/3 (Task 1 operator gate pre-satisfied by the orchestrator; Tasks 2-3 executed and committed)
- **Files modified:** 6 tracked files modified (rig-pins.json, probe_board.py, judge_readback.py, gate_record.py, EVIDENCE.jsonl, EVIDENCE.md), ~30 files created under `bench/cells/BRINGUP-uno/`

## Accomplishments

- **Operator gate (Task 1) — already satisfied.** The orchestrator's pre-gate enumeration found exactly one serial node, `/dev/ttyACM0`, which appeared at 05:27 on 2026-08-27 after the phase had halted with no node present at all. The operator declared the board as "Arduino Uno (ATmega328P)" and the socket state as "Yes — shield on, chip removed." Both declarations are recorded verbatim in `probe.json` and cross-checked against the avrdude signature probe in Task 2 — they agree.
- **Task 2 — the uno read chain proven on the device.** `probe_board.py` identified the board as `atmega328p` via signature `0x1e950f` (the known-good value for this board), agreeing with the operator's declaration. The control arm's firmware (`8695ee5`) was flashed via `pio run -t upload -e uno` (26026 B written, PlatformIO's own upload-time verify also passed). An independent `judge_readback.py` invocation then read back all 32768 B of flash via a separate avrdude 8.1 invocation (`-A` explicit) and judged the `[0, 26026)` prefix against the control arm's own hex extent: `judged_match=true`, `sha_actual_judged == sha_expected_judged`, and a distinct `sha_whole_flash_unjudged` recorded alongside, never consulted in the match decision. Read cost: ~5.5 s wall-clock (three consecutive timed runs: 5.495 s, 5.505 s, 5.493 s) — the baseline plans 09/10 need. `controller_string` was attempted twice (pre- and post-flash) via `firestarter -v -p /dev/ttyACM0 hw` and recorded as `"not measured — <reason>"` both times (see Deviations).
- **Task 3 — D-03 proven able to fail, then corrected.** The v1.33 arm (`5759dc8`) was deliberately flashed to the same board (PlatformIO build report confirmed 22952 B — its own known span, not a stale cache) and its read-back judged against the **control** arm's hex extent: `judge_readback.py` exited **non-zero** with `judged_match=false`, **22367 of 26026** judged bytes differing (86% — not a marginal signal), first differing offsets and byte values recorded. The whole-flash SHA independently confirmed the flash content moved (`944b73f6...` vs. Task 2's `d9eb943a...`). The negative control **FIRED** — observed, not merely configured. The control arm was then re-flashed and re-judged: `judged_match=true` again, with a whole-flash SHA byte-identical to Task 2's baseline (`d9eb943a...`), confirming a clean, verified correction. `CROSSFLASH.md` records all three events in order with their literal commands, verdicts, and the FIRED statement. One bring-up row (`cell_id=BRINGUP-uno`, `position_id=BRINGUP-uno__control__none`, `outcome=validated`) was appended to `bench/EVIDENCE.jsonl` via `render_evidence.py --append`; `EVIDENCE.md` was re-rendered (`--check` green); `gate_record.py --jsonl` is green (0 violations); the 20-position reconciliation correctly still shows 0/20 (the bring-up row is excluded by its `BRINGUP-` prefix).
- **Board left in a known state.** The board carries the **control** arm at teardown, per the plan's own instruction. `firestarter/`'s working tree was restored to its starting branch (`gsd/v1.33-source-hygiene-firmware-size-reduction`) after the three checkouts this plan performed; both `firestarter/` and `firestarter_app/` submodules are confirmed porcelain-clean.
- **Full gate suite green.** `bash .planning/v1.34/tools/run_gates.sh` — 11/11 tool selftests, 5/5 live gates, `ALL GATES PASSED`, run both mid-plan (after the tooling fixes) and again as the final pre-commit check.

## Task Commits

1. **Task 2: Prove the uno read chain — signature, flash a known arm, -A read, judged match** — `4e721916` (feat)
2. **Task 3: D-03 on uno — deliberate wrong-arm flash, observed MISMATCH, then the correction** — `46ec599e` (feat)

**Plan metadata:** committed below (this SUMMARY + STATE.md/ROADMAP.md)

## Files Created/Modified

- `.planning/v1.34/bench/cells/BRINGUP-uno/probe.json` — signature-probe result + operator-declaration cross-check + device-node enumeration check + controller_string (not-measured, with reason)
- `.planning/v1.34/bench/cells/BRINGUP-uno/READBACK-VERDICT.json` — final (post-correction) judged verdict: `judged_match=true`, `judged_span_bytes=26026`, both arm args `control`, elapsed-time baseline
- `.planning/v1.34/bench/cells/BRINGUP-uno/flash_readback.bin`, `judged_span.bin`, `expected_span.bin` — the 32768 B read-back, its judged prefix, and the objcopy-normalized reference, all for the final (control) state
- `.planning/v1.34/bench/cells/BRINGUP-uno/SHA256SUMS.txt` — verifies with `sha256sum -c`
- `.planning/v1.34/bench/cells/BRINGUP-uno/CROSSFLASH.md` — the D-03 human-readable record (three events, offsets, FIRED statement, teardown arm)
- `.planning/v1.34/bench/cells/BRINGUP-uno/crossflash/` — the deliberate-mismatch read-back and its own verdict/SHA files, kept separate from the final (control) state above
- `.planning/v1.34/bench/cells/BRINGUP-uno/logs/` — 12 invocation captures (stdout/stderr per step) plus `04_pio_upload_control.cmd.json` and `all_commands.json` (structured argv+cwd records)
- `.planning/v1.34/rig-pins.json` — added `hex_span_expected_by_arm` (all three targets) and `git_binary`
- `.planning/v1.34/tools/probe_board.py` — new parser for avrdude 8.1's actual stderr wording, new selftest legs
- `.planning/v1.34/tools/judge_readback.py` — manifest-list normalization, per-arm span consult, real `cwd` recording, a real `judged_span.bin` + fixed `SHA256SUMS.txt` format, new selftest legs
- `.planning/v1.34/tools/gate_record.py` — `git_binary` added to the allowed argv0 set, new selftest leg
- `.planning/v1.34/bench/EVIDENCE.jsonl`, `EVIDENCE.md` — one bring-up row appended and rendered

## Decisions Made

See `key-decisions` in the frontmatter for the full list with rationale. Summary: flashed and left the control arm per the plan's own intent; resolved the arm-span inconsistency by treating BUILD-MANIFEST.json's per-image `hex_span` as authoritative and fixing `rig-pins.json`/`judge_readback.py` to represent it per-arm; recorded `controller_string` as a genuine, reasoned non-claim rather than fixing or faking it (fixing would violate the D-16 no-product-code-changes boundary); recorded PlatformIO's internal avrdude-6.3 usage as a Finding, not a violation.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 — Missing critical functionality] `rig-pins.json`'s `hex_span_expected` is arm-agnostic for a genuinely arm-dependent quantity**
- **Found during:** Task 2, before running `judge_readback.py` for real — flagged explicitly in this plan's own defect-resolution instructions and confirmed against `BUILD-MANIFEST.json`'s `measured_divergence_finding` (control's `uno` hex_span is 26026 B, v133's is 22952 B, ~3 KB apart, root-caused there to PR #55's VPE-settle amortisation plus Phase 158's size reduction landing only on the v1.33 side).
- **Issue:** `rig-pins.json` pinned a single flat `hex_span_expected` value per target, equal to the v133 arm's own span. Flashing and judging the **control** arm (as Task 2 requires, control-first) would have `judge_readback.py`'s own `cross_check_hex_span()` reject a correctly-flashed control-arm read-back as "not the artifact the manifest describes," because the objcopy output size (26026) would disagree with the flat expected value (22952).
- **Fix:** Added `hex_span_expected_by_arm` (`{"control": ..., "v133": ...}`) to all three `targets.*` entries in `rig-pins.json`, with an explanatory `hex_span_expected_note` on each; kept the flat `hex_span_expected` unedited for backward compatibility. Fixed `judge_readback.py`'s `cross_check_hex_span()` to consult the per-arm map first, keyed by `--expect-arm`, falling back to the flat value only when the map or the arm key is absent.
- **Files modified:** `.planning/v1.34/rig-pins.json`, `.planning/v1.34/tools/judge_readback.py`
- **Verification:** `judge_readback.py --selftest` gained two new positive legs (per-arm override; the other arm's value still catches a genuine mismatch) plus a leg for the related list-shape fix below — 13/13 legs pass. Live: Task 2's real invocation judged the control arm's read-back against `judged_span_bytes=26026` (not the plan's originally-stated, wrong 22952) and passed.
- **Committed in:** `4e721916` (Task 2 commit)

**2. [Rule 1 — Bug] `judge_readback.py`'s manifest cross-check assumed a dict shape; the real `BUILD-MANIFEST.json` is a list**
- **Found during:** Task 2, while tracing `cross_check_hex_span()`'s manifest lookup before the first live invocation.
- **Issue:** `manifest.get("images", {})` followed by `images.get(hex_path.name)` — but `BUILD-MANIFEST.json`'s `images` field is a **list** of per-image dicts (each keyed by its own `"file"` field), not a dict keyed by filename. The tool's own pre-existing `--selftest` fixture only ever exercised the dict shape (`{"images": {hex_path.name: {...}}}`), so this was never caught before running against the real file — where `.get()` on a list raises `AttributeError`, not a controlled `FAIL:` line.
- **Fix:** `cross_check_hex_span()` now normalizes a list-shaped `images` field into a dict keyed by each entry's `"file"` value before lookup.
- **Files modified:** `.planning/v1.34/tools/judge_readback.py`
- **Verification:** New selftest leg constructs a list-shaped manifest fixture matching the real file's actual shape and confirms it is normalized and matched, not crashed on.
- **Committed in:** `4e721916` (Task 2 commit)

**3. [Rule 1 — Bug] `judge_readback.py`'s recorded `commands[].cwd` was hardcoded `None`**
- **Found during:** Task 2, while reviewing `READBACK-VERDICT.json`'s first real output against the plan's acceptance criterion "the literal argv plus working directory of each is recorded."
- **Issue:** `run_avrdude_read()`/`run_objcopy_normalize()` returned `{"argv": argv, "cwd": None}` unconditionally, regardless of where the subprocess actually ran.
- **Fix:** Both helpers now record `str(Path.cwd())` as the actual invocation cwd.
- **Files modified:** `.planning/v1.34/tools/judge_readback.py`
- **Verification:** Live: `READBACK-VERDICT.json`'s `commands[].cwd` now reads `/workspaces` for both the avrdude read and the objcopy normalize, matching where they actually ran.
- **Committed in:** `4e721916` (Task 2 commit)

**4. [Rule 1 — Bug] `judge_readback.py`'s `SHA256SUMS.txt` did not verify with `sha256sum -c`**
- **Found during:** Task 2, running the plan's own acceptance check `cd $D && sha256sum -c SHA256SUMS.txt`.
- **Issue:** The written file named a `judged_span.bin` that was never actually written to disk (only its bytes were hashed, in memory), and its second line's filename column carried the literal text `flash_readback.bin (UNJUDGED - whole flash)` — a string `sha256sum -c` cannot resolve as a filename. Both defects make verification fail outright, contradicting this task's own acceptance criterion.
- **Fix:** `judged_span.bin` is now written to disk for real (the judged prefix bytes). The annotation about which line is unjudged moved into `#`-prefixed comment lines (ignored by `sha256sum -c`); the two data lines now name only real, already-present files (`judged_span.bin`, `flash_readback.bin`).
- **Files modified:** `.planning/v1.34/tools/judge_readback.py`
- **Verification:** Live: `sha256sum -c SHA256SUMS.txt` in the cell directory reports `judged_span.bin: OK` and `flash_readback.bin: OK`.
- **Committed in:** `4e721916` (Task 2 commit)

**5. [Rule 1 — Bug] `probe_board.py`'s regexes were written against an avrdude wording the pinned avrdude 8.1 no longer emits**
- **Found during:** Task 2's very first live probe invocation, which failed with `FAIL: neither parse route matched avrdude stderr`.
- **Issue:** avrdude 8.1's real stderr (on both the deliberately-wrong-`-p` route and the correct-`-p` route) reads `Device signature = 1E 95 0F (ATmega328P, ATA6614Q, LGT8F328P)`, optionally followed by `Error: expected signature for <wrong-part> is <hex>` on a mismatch. Neither `_ROUTE1_RE` (`"connected part (\w+)"`) nor `_ROUTE2_SIG_RE`/`_ROUTE2_GUESS_RE` (`"device signature = (0x...)"`/`"\(probably (\w+)\)"`) matches this wording at all — this would have been a hard rig failure on the tool's very first real-device invocation, contradicting the docstring's claim that the mechanism was bench-verified (that verification predates this container's pinned avrdude 8.1).
- **Fix:** Added `_parse_sig81()`, a new parser for the `"Device signature = XX XX XX (Name, ...)"` line, tried by both `parse_route1()` (after the old pattern) and `parse_route2()` (after its old patterns) — so a live device now identifies correctly via Route 1 directly, extracting both the real measured signature hex and the first parenthesised part name. The old-format regexes are kept unchanged for robustness/backward compatibility.
- **Files modified:** `.planning/v1.34/tools/probe_board.py`
- **Verification:** New selftest legs added for both the mismatch-flavoured and match-flavoured real avrdude 8.1 fixtures (verbatim-captured wording) — both parse correctly to `atmega328p` / `0x1e950f`. Live: the real device probe now succeeds, `OK: board identified as atmega328p via route1 (signature 0x1e950f)`.
- **Committed in:** `4e721916` (Task 2 commit)

**6. [Rule 2 — Missing critical functionality] `gate_record.py`'s `check_commands()` had no allowance for `git` at all**
- **Found during:** Task 3, while validating the constructed `EVIDENCE.jsonl` row's `commands` field (which must include the firmware-arm `git checkout` per `PROCEDURE.md` P-04's own literal command block) against `gate_record.py` before appending.
- **Issue:** `_allowed_argv0_set()` only ever populated arm `venv_bin` paths, the pinned `avrdude.binary`, and `pio_binary` — `git` was not in the set, and `rig-pins.json` did not even pin a `git` binary path. Any `commands` entry recording the firmware-arm checkout (required by P-04, and therefore by every future sweep-phase cell too) would be flagged as "not one of the two pinned arm binaries or a pinned rig-owned executable," regardless of whether the argv0 was absolute. This would have broken `gate_record.py --jsonl` for every EVIDENCE row in Phases 161-163 that followed the procedure literally.
- **Fix:** Pinned `git_binary` in `rig-pins.json` (measured via `which git`, never resolved from `PATH`, consistent with this rig's standing convention for avrdude/objcopy/pio). Added it to `gate_record.py`'s `_allowed_argv0_set()`.
- **Files modified:** `.planning/v1.34/rig-pins.json` (committed in the Task 2 commit, since both `hex_span_expected_by_arm` and `git_binary` land in the same file), `.planning/v1.34/tools/gate_record.py`
- **Verification:** New selftest leg constructs a record whose `commands` includes a `git_binary` checkout entry and confirms it validates cleanly. Live: the constructed `BRINGUP-uno` EVIDENCE row (whose `commands` field includes three `git checkout` invocations) validates with 0 violations via `gate_record.validate_object()`, and `gate_record.py --jsonl` on the full file is green.
- **Committed in:** `46ec599e` (Task 3 commit)

**Total deviations:** 6 auto-fixed (1 Rule 2 arm-span defect explicitly named by the plan itself, 4 Rule 1 bugs found live against real device/file inputs, 1 further Rule 2 gap found while building the evidence row). All found and fixed in-phase, all with new `--selftest` coverage, all verified live against the real device or the real committed files before the corresponding task's commit.

### Findings (recorded, not fixed — out of scope or not a violation)

**1. `controller_string` is not measurable via the documented `hw` probe.** `firestarter_app/firestarter/cli_handlers.py:969`'s `hw` command handler calls `_build_op_flags()` with zero keyword arguments, so `verbose` is always `False` there regardless of the CLI's own `-v`/`--verbose` flag — `FLAG_VERBOSE` (0x80) is therefore never set on the wire command `hw` sends. Firmware's `MSG_INFO_FW` echo line (`firestarter.cpp:150`) is gated by `is_flag_set(FLAG_VERBOSE)` (`include/logging_id.h`), so it is never emitted by `hw`, regardless of CLI verbosity or which arm's firmware is running. Confirmed live twice (pre-flash and post-flash-of-control) via `firestarter -v -p /dev/ttyACM0 hw`; neither capture (`logs/03_hw_probe_pre_flash.stdout.log`, `logs/06_hw_probe_post_flash.stdout.log`) contains an `I:`/`INFO:` FW line. This is a genuine host-app limitation. **Not fixed** — the D-16 boundary explicitly forbids product-code changes in this phase (`firestarter_app` is out of scope). Recorded as `"not measured — <reason>"` per the project's standing anti-fabrication convention. **This will recur identically for every future cell's `controller_string`** via `capture_provenance.py`'s identical `hw`-based probe, until a future host-app fix forwards `verbose` into `hw`'s wire flags — flagged here so Phases 161-163 don't mistake a repeated `"not measured"` field for a new bug.

**2. PlatformIO's avrdude resolution is PER-ENV, not a single choice — corrected 2026-08-27 per orchestrator spot-check.** The first version of this finding (recorded in this plan's task-2 commit message) stated that "PlatformIO's own upload path for `uno` resolved and invoked avrdude 6.3 internally," which is accurate for `uno` but reads as a general property of the upload path — the distinction matters most on exactly the target plan 09 flashes next. Measured from cwd `/workspaces/firestarter`:

  | env | `pio pkg list` avrdude | required | protocol |
  |---|---|---|---|
  | `uno` | `tool-avrdude @ 1.60300.200527` (6.3) | `~1.60300.0` | `arduino` |
  | `uno328pb` | `tool-avrdude @ 1.80100.0` (8.1) | `~1.80100.0` | `urclock` |
  | `leonardo` | `tool-avrdude @ 1.60300.200527` (6.3) | `~1.60300.0` | `avr109` |

  Capability check (each binary's own `-C` conf supplied explicitly, since 6.3's shipped conf path is a dead hardcoded path and `-c '?type'` without `-C` fails for that unrelated reason): `avrdude 6.3 -c '?type' | grep -c urclock` → 0 (6.3 has no urclock programmer id at all); `avrdude 8.1 -c '?type' | grep -c urclock` → 1; `avrdude 6.3 -c avr109 -p atmega32u4 -P /dev/null -n` gets past option-parse to a real port-open attempt (fails only because `/dev/null` isn't a serial device) — `avrdude.conf:903` defines `id = "avr109"` for 6.3 (its `-c '?type'` SUMMARY listing omits it, but the id is real and accepted). **Conclusion: there is no target on which PlatformIO hands a protocol to an avrdude build that cannot drive it.** PlatformIO resolves 8.1 precisely where `urclock` is required (MiniCore's `ATmega328PB.json` declares `protocol=urclock` and pins `~1.80100.0`) and resolves 6.3 for `uno`/`leonardo`, both of whose protocols (`arduino`, `avr109`) 6.3 is capable of driving. **No override of PlatformIO's avrdude resolution is needed on any of the three targets** — plan 09 should not spend a cycle forcing 8.1 that `uno328pb` already gets, and plan 10 should not read a `leonardo` log's 6.3 as a forbidden-binary violation; it is neither forbidden in that context nor incapable of the `avr109` protocol it is asked to drive. `rig-pins.json`'s `forbidden_binaries` entry governs this rig's own **direct** avrdude invocations only (`probe_board.py`, `judge_readback.py`, both of which correctly used the pinned 8.1 binary exclusively throughout) and does not conflict with PlatformIO's internal per-env resolution — D-01's separation-of-code-paths property still holds. Full measurement detail: `CROSSFLASH.md`'s "Finding: PlatformIO's avrdude resolution is per-env" section.

**3. Bonus fact for plan 10 (leonardo): the 1200-baud touch is PlatformIO's own job on the flash path, not `touch_1200.py`'s.** `~/.platformio/platforms/atmelavr/boards/leonardo.json`'s `upload` block carries `"use_1200bps_touch": true` and `"wait_for_upload_port": true` alongside `"protocol": "avr109"` — PlatformIO performs the 1200-baud touch and the port re-enumeration wait itself as part of `pio run -t upload -e leonardo`. `tools/touch_1200.py` is therefore needed for the **direct-avrdude read-back** plan 10 runs outside PlatformIO (the `judge_readback.py` step, a separate avrdude invocation per D-01 that does not go through PlatformIO's upload machinery), not for the flash step. This does not contradict `touch_1200.py`'s own standing note that real re-enumeration behavior on this board is unproven until plan 10 actually runs it — it only narrows which step needs the tool. Full detail: `CROSSFLASH.md`'s "Bonus fact for plan 10" section.

## Issues Encountered

None beyond the six deviations and two findings documented above, all resolved or explicitly scoped-out before their task's commit. No unresolved blockers.

## User Setup Required

None — the operator's Task 1 gate (board attachment, chip removal, node/board declaration) was already satisfied by the orchestrator before this plan began executing, per this plan's `<task_1_operator_gate_ALREADY_SATISFIED>` instructions.

## Next Phase Readiness

- The `uno` read chain is proven end-to-end and known-able-to-fail. Plans 09 (`uno328pb`) and 10 (`leonardo`) can proceed with their own chains, inheriting the fixed `hex_span_expected_by_arm` shape in `rig-pins.json` for their own targets and the `git_binary` allowance in `gate_record.py`.
- Plan 09 must still separately resolve `uno328pb`'s own `judged_span_policy: PENDING-xshowvector` placeholder — untouched by this plan's fixes, a different field for a different reason (Pitfall 3's vector-bootloader concern, not the arm-span defect this plan resolved).
- RIG-01 is **not** marked complete (per this plan's own "Requirement completion" section — it closes SC#2 for `uno` only; plans 09/10 must do the same for the other two targets before RIG-01 as a whole can close). `REQUIREMENTS.md` is left unchanged.
- `controller_string`'s non-measurability is a standing fact for every future cell in this milestone, not just this bring-up — carried forward as a Finding above so Phases 161-163 don't re-investigate it as a new anomaly. PlatformIO's per-env avrdude resolution (6.3 for `uno`/`leonardo`, 8.1 for `uno328pb`) is fully accounted for and requires no override on any target — plan 09 and plan 10 can proceed without re-deriving this. Plan 10 additionally inherits the leonardo 1200-baud-touch scoping fact above (PlatformIO's job on the flash path; `touch_1200.py`'s job only for the direct-avrdude read-back).

## Self-Check: PASSED

- `FOUND: .planning/v1.34/bench/cells/BRINGUP-uno/probe.json`
- `FOUND: .planning/v1.34/bench/cells/BRINGUP-uno/READBACK-VERDICT.json`
- `FOUND: .planning/v1.34/bench/cells/BRINGUP-uno/flash_readback.bin` (32768 B)
- `FOUND: .planning/v1.34/bench/cells/BRINGUP-uno/SHA256SUMS.txt` (verifies via `sha256sum -c`)
- `FOUND: .planning/v1.34/bench/cells/BRINGUP-uno/CROSSFLASH.md`
- `FOUND: .planning/v1.34/bench/cells/BRINGUP-uno/crossflash/READBACK-VERDICT.json`
- `FOUND: .planning/v1.34/bench/EVIDENCE.jsonl` (2 lines: header + BRINGUP-uno row)
- `FOUND: commit 4e721916` (Task 2)
- `FOUND: commit 46ec599e` (Task 3)
- `python3 .planning/v1.34/tools/probe_board.py --selftest` → rc=0 (9 legs)
- `python3 .planning/v1.34/tools/judge_readback.py --selftest` → rc=0 (13 legs)
- `python3 .planning/v1.34/tools/gate_record.py --selftest` → rc=0 (15 legs)
- `python3 .planning/v1.34/tools/gate_record.py --jsonl .planning/v1.34/bench/EVIDENCE.jsonl` → rc=0, 0 violations
- `python3 .planning/v1.34/tools/render_evidence.py --jsonl ... --target ... --check` → rc=0
- `bash .planning/v1.34/tools/run_gates.sh` → rc=0, 11/11 selftests + 5/5 live gates, ALL GATES PASSED
- `git -C /workspaces/firestarter status --porcelain` → empty
- `git -C /workspaces/firestarter_app status --porcelain` → empty

---
*Phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur*
*Completed: 2026-08-27*
