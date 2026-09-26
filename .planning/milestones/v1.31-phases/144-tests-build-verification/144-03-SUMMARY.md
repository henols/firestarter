---
phase: 144-tests-build-verification
plan: 03
subsystem: testing
tags: [platformio, unity, native-test, golden-trace, git-blob-identity, pytest, firmware]

# Dependency graph
requires:
  - phase: 138-preconditions-baseline
    provides: "the pre-change eprom_v131_expected.h fixture (198/221/201 entries) this plan preserves by rename, and its blob SHA ca3e09f164e6e1c541ecb63d15bbebf5bce41d70"
  - phase: 141-per-byte-program-loop
    provides: "141-NEW-TRACE.md's capture command sequence (cited, its stale 91/119/59 arrays explicitly never pasted) and the loop rewrite that this plan's fresh capture actually measures"
  - phase: 144-01-and-02 (wave sequencing only)
    provides: "a clean firmware working tree at Wave 2's start -- test_flash_path_record_sync.py asserts the whole repo's porcelain, so this plan's own commit had to be the only uncommitted state in play"
provides:
  - "The pre-change golden trace preserved intact at test/native/avr/_shared/eprom_v131_expected_prechange.h, blob ca3e09f164e6e1c541ecb63d15bbebf5bce41d70, included by nothing"
  - "A fresh, empirical post-v1.31 capture at test/native/avr/_shared/eprom_v131_expected.h totalling 91/115/59 entries, validated against three stale-paste discriminators before a single line was pasted"
  - "A re-derived tests/golden/eprom_v131_trace_inventory.json arming the six-assertion identity gate for v1.32 drift detection"
  - "native_trace_v131 retired from RED to 5/5 -- the milestone's first standing RED"
  - "Two independent-parser scripts (/tmp/gsd-144/count_arrays.py, count_kinds.py), each validated against the prechange file's known 198/221/201 before being trusted on new data -- reusable by later plans"
affects: [144-04, 144-05, 144-07]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Independent re-derivation validated against a known-answer input (the prechange file's recorded 198/221/201) before being trusted on new data -- never assume a fresh parser is correct on its first real use"
    - "One-commit atomic landing for a rename + new-capture + re-derived-inventory triple, with meta.recorded_at_head deliberately naming the commit's PARENT (the same offset convention protocol_branch_inventory.json established in Phase 142/143)"
    - "Fixture content built by mechanical extraction (sed line-ranges from the recorder's own dump) rather than hand-retyped from memory, for any block the plan forbids hand-deriving"

key-files:
  created:
    - firestarter/test/native/avr/_shared/eprom_v131_expected_prechange.h
  modified:
    - firestarter/test/native/avr/_shared/eprom_v131_expected.h
    - firestarter/tests/golden/eprom_v131_trace_inventory.json

key-decisions:
  - "D-05: pure git mv preserves the pre-change blob byte-for-byte; git hash-object on the renamed path reprints ca3e09f164e6e1c541ecb63d15bbebf5bce41d70, the whole of the proof since a git blob SHA is content-only and path-independent"
  - "D-06: the new capture must be empirical only -- validated against all three F-06 stale-paste discriminators (banner totals 91/115/59 not 141-NEW-TRACE.md's stale 91/119/59; both overflow flags 0; 6-vs-5 Unity case count via DIRECT binary invocation) before a single line was pasted"
  - "D-08: rename + new fixture + re-derived inventory land in exactly ONE commit so the identity gate is never transiently RED for a reason that is really a git exit code; the prechange header is explicitly recorded as NOT machine-checked by any gate (a named non-claim, not silently implied coverage)"
  - "requirements-completed left empty in this SUMMARY: this plan is scoped to TEST-06 evidence, not to flip it -- plan 144-07 owns the consolidated eight-requirement flip, and REQUIREMENTS.md/ROADMAP.md coverage tables were not touched"

patterns-established:
  - "A throwaway independent parser must be run against a KNOWN-ANSWER input first (here: the prechange file's recorded 198/221/201) before its output is trusted on genuinely new data -- this is what makes 'independent re-derivation' meaningfully independent rather than merely a second copy of the same bug"

requirements-completed: []  # Intentional -- see key-decisions. This plan evidences TEST-06; plan 144-07 flips it.

coverage:
  - id: D1
    description: "Pre-change golden trace preserved as a historical artifact via pure git-mv rename; Phase-138 blob still resolves at HEAD: after the rename (D-05)"
    requirement: "TEST-06"
    verification:
      - kind: other
        ref: "git hash-object test/native/avr/_shared/eprom_v131_expected_prechange.h -> ca3e09f164e6e1c541ecb63d15bbebf5bce41d70; git rev-parse HEAD:test/native/avr/_shared/eprom_v131_expected_prechange.h -> ca3e09f164e6e1c541ecb63d15bbebf5bce41d70"
        status: pass
    human_judgment: false
  - id: D2
    description: "Fresh post-v1.31 trace captured empirically from the shipped recorder (never hand-derived, never 141-NEW-TRACE.md's stale arrays), validated against three stale-paste discriminators, totals 91/115/59 (D-06)"
    requirement: "TEST-06"
    verification:
      - kind: other
        ref: "trace_dump.txt banners: total=91/115/59 for _07/_08/_0B, strobe_overflow=0 timing_overflow=0 on all three (never the stale 91/119/59)"
        status: pass
      - kind: unit
        ref: "count_arrays.py / count_kinds.py validated against prechange (198/221/201, 142+56/157+64/142+59) before being applied to the new fixture (91/115/59, 66+25/84+31/42+17)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Six-assertion identity gate re-armed GREEN on the new fixture; all three paths (rename, new fixture, inventory) landed in ONE commit (D-08, F-05)"
    requirement: "TEST-06"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_golden_trace_identity_eprom_v131.py -- 6 passed"
        status: pass
      - kind: other
        ref: "git show --stat --name-only HEAD (commit 2684252) lists exactly 3 paths, none under src/"
        status: pass
      - kind: unit
        ref: "firestarter/tests/ full suite -- 301 passed, 0 failed"
        status: pass
    human_judgment: false
  - id: D4
    description: "native_trace_v131 runs 5 cases with 0 failed -- the milestone's first standing RED retired"
    requirement: "TEST-06"
    verification:
      - kind: unit
        ref: "pio test -e native_trace_v131 -- 5 test cases: 5 succeeded (was 3 failed / 2 succeeded pre-capture)"
        status: pass
    human_judgment: false

# Metrics
duration: ~24min
completed: 2026-08-14
status: complete
---

# Phase 144 Plan 03: Retire the Frozen Trace's Standing RED Summary

**Froze Phase 138's pre-change golden trace as a byte-identical historical artifact by pure rename, captured a fresh empirical post-v1.31 trace (91/115/59 entries, not 141-NEW-TRACE.md's stale 91/119/59), and re-armed the six-assertion identity gate in ONE commit -- `native_trace_v131` goes from 3-failed/2-succeeded to 5/5.**

## Performance

- **Duration:** ~24 min
- **Started:** 2026-08-14T07:05:11Z
- **Completed:** 2026-08-14T07:28:49Z
- **Tasks:** 2 completed
- **Files modified:** 3 (1 created via rename, 2 rewritten)

## Accomplishments

- Renamed `test/native/avr/_shared/eprom_v131_expected.h` to `eprom_v131_expected_prechange.h` via pure
  `git mv`, byte-untouched -- `git hash-object` on the renamed path reprints Phase 138's exact blob
  `ca3e09f164e6e1c541ecb63d15bbebf5bce41d70` both pre-staging and, after the commit, at `HEAD:`.
- Captured a fresh trace at this phase's tip from the shipped recorder: cold-built
  `native_trace_v131` with `PLATFORMIO_BUILD_FLAGS="-D EPROM_V131_TRACE_DUMP"`, ran the linked binary
  DIRECTLY (never `pio test`, which swallows `printf`), and validated the dump against all three F-06
  stale-paste discriminators before pasting a single line: banner totals `91`/`115`/`59` (not
  `141-NEW-TRACE.md`'s stale `91`/`119`/`59`), `strobe_overflow=0 timing_overflow=0` on all three, and a
  6-case dump-build summary versus a 5-case plain-build summary (confirmed via direct binary invocation
  of each; the `pio test` wrapper itself shows an unrelated pre-existing quirk, see Issues Encountered).
- Wrote the new fixture at the old path by mechanical extraction (`sed` line-ranges from the recorder's
  own dump into the array bodies) rather than hand-retyping, eliminating transcription risk for data the
  plan forbids hand-deriving. All non-array content -- include guard, typedef, four kind macros,
  `v131_merged_length`, `v131_merged_at` + splice rule, every assertion helper, and the three
  `sizeof`-derived `_LEN` macros -- verified byte-for-byte identical to the prechange file (`diff` reports
  nothing on lines 38-211 of each).
- Re-derived `tests/golden/eprom_v131_trace_inventory.json` by two independent throwaway parsers
  (`count_arrays.py`, `count_kinds.py`), each validated against the prechange file's known-answer
  `198/221/201` (and `142+56/157+64/142+59` strobe+timing split) before being trusted on the new data.
  `meta.blob_sha` is the pre-staging `git hash-object`; `meta.recorded_at_head` deliberately names this
  commit's PARENT, mirroring `protocol_branch_inventory.json`'s established one-commit-offset convention.
  Added `meta.prechange_header_non_claim`, naming D-08's non-claim explicitly: the prechange header is
  NOT machine-checked by any gate.
- Landed the rename, the new fixture, and the inventory in exactly ONE commit (`2684252`), naming all
  three array movements (`198→91`, `221→115`, `201→59`) and their attributing phases in the message.
  `native_trace_v131` now runs 5 test cases, 0 failed -- the milestone's first standing RED retired.

## Task Commits

Both tasks land in a single commit by design (D-08/F-05 forbid splitting them):

1. **Task 1: Capture the new trace cold, rename the old fixture, write the new one** -- staged but not
   committed (per plan instruction: "Do NOT commit yet — task 2 completes the one-commit unit").
2. **Task 2: Re-derive the inventory, land all three paths in ONE commit, and re-arm the identity gate**
   - `2684252` (test, firestarter submodule) — the renamed prechange header, the rewritten fixture, and
     the re-derived inventory, all three paths in one commit.

**Plan metadata:** committed together with this SUMMARY (see final commit below).

## Files Created/Modified

- `firestarter/test/native/avr/_shared/eprom_v131_expected_prechange.h` (new, via `git mv`) — the frozen
  pre-change 27C write-loop trace (198/221/201 merged entries), byte-identical to the pre-rename file,
  blob `ca3e09f164e6e1c541ecb63d15bbebf5bce41d70`; `#include`d by nothing.
- `firestarter/test/native/avr/_shared/eprom_v131_expected.h` (rewritten) — the fresh post-v1.31 capture
  (91/115/59 merged entries); all shared code (typedef, kind macros, `v131_merged_length`,
  `v131_merged_at`, assertion helpers, `_LEN` macros) preserved byte-for-byte; every array body pasted
  verbatim from the recorder's own dump, each entry retaining only its own `/* N */` positional-index
  comment (no hand-authored per-segment comments, unlike the pre-change file's convention).
- `firestarter/tests/golden/eprom_v131_trace_inventory.json` (rewritten) — re-derived `meta.blob_sha`,
  `meta.recorded_at_head`, `meta.measured_entry_counts`, `meta.overflow_observed`, `arrays[].entries`,
  and a repointed `meta.frozen_for` (now arms v1.32 drift detection); `meta.why_two_checks` and
  `meta.how_to_update` preserved verbatim; new `meta.prechange_header_non_claim` field.

## Decisions Made

- **D-05 (rename proof is a single fact):** because a git blob SHA is content-only and path-independent,
  confirming `git hash-object` on the renamed path reprints the exact pre-rename SHA is the *entire* proof
  that nothing moved — no further diffing was needed.
- **D-06 (three discriminators, checked before trusting any line):** the dump was validated against (a)
  banner totals `91`/`115`/`59` — a `0x08` total of `119` would have been positive proof of a stale paste
  from `141-NEW-TRACE.md`; (b) `strobe_overflow=0 timing_overflow=0` on all three; (c) a 6-case dump-build
  summary vs. a 5-case plain-build summary, confirmed via direct binary invocation of each (the built
  binary's own Unity summary, not the `pio test` wrapper — see Issues Encountered for why).
- **Mechanical extraction over hand-retyping:** the three array bodies were extracted via `sed` line-ranges
  directly from `trace_dump.txt` rather than typed by hand into the Write tool, and the shared code block
  was extracted via `sed` from the renamed prechange file rather than retyped from memory — both to
  eliminate transcription risk for content the plan explicitly forbids hand-deriving or hand-correcting.
- **D-08 (one commit, named non-claim):** landing the rename, new fixture, and inventory in one commit is
  what keeps `test_golden_trace_identity_eprom_v131.py`'s `HEAD:`-based blob check from ever observing a
  transient mismatch that is really just "the inventory hasn't caught up to the fixture yet." The
  inventory's new `meta.prechange_header_non_claim` field states explicitly that nothing gate-asserts the
  prechange header — a named absence, not a silent gap.
- **`requirements-completed: []`, deliberately:** this plan is scoped to TEST-06 evidence, not to flip it —
  populating this field (or editing REQUIREMENTS.md/ROADMAP.md) would read as a soft tick that plan 144-07
  alone is authorized to make. The `coverage:` block's per-deliverable `requirement:` field still links
  D1-D4 to TEST-06 for traceability without implying completion.

## Deviations from Plan

None - plan executed exactly as written. The capture totals (91/115/59), the rename mechanics, the
preserved-verbatim code block, the one-commit landing, and the inventory's re-derived fields all match
the plan's `<action>` text exactly. No `src/` file was touched; no seventh native env or `platformio.ini`
edit occurred; no `*_v131` env name was fed to `check_size_baseline.py` or `check_build_warnings.py`.

## Issues Encountered

While validating F-06 discriminator (c) (dump build reads more cases than the plain build), I first ran
`pio test -e native_trace_v131` (the wrapper, not the raw binary) against a still-dump-flagged build and
observed `Program received signal SIGQUIT (Quit)` followed by a summary line reading
`6 test cases: 3 failed, 2 succeeded` — mathematically inconsistent (3+2=5, not 6) and reproducible even
after a full `rm -rf .pio/build/native_trace_v131` + rebuild without the dump flag. This is a pre-existing
`pio test` wrapper quirk, not something introduced by this plan: `141-NEW-TRACE.md` §3 records the
identical anomaly ("Both the dump binary's own Unity summary line and the normal `pio test
-e native_trace_v131` invocation report the identical result: 6 test cases: 3 failed, 2 succeeded") when
run against a build that had 3 failing cases. Running the built binary DIRECTLY (bypassing the `pio test`
wrapper), as the plan's own action text specifies, sidesteps the quirk entirely and gives the authoritative
counts used throughout this SUMMARY (6 for the dump build, 5 for the plain build, both via direct
invocation). Once the new fixture made all cases pass, `pio test -e native_trace_v131`'s wrapper output
also read correctly (`5 test cases: 5 succeeded`, no SIGQUIT) — the quirk appears tied to Unity's larger
failure-message output volume, not to case count itself. No code change was needed; this is recorded for
transparency since it could otherwise look like a build-cache bug.

## Verbatim Evidence

### The three capture banners (F-06 discriminators (a) and (b), from `/tmp/gsd-144/trace_dump.txt`)

```
##### EPROM_V131_TRACE_PROTO_07 total=91 strobe_overflow=0 timing_overflow=0
##### EPROM_V131_TRACE_PROTO_08 total=115 strobe_overflow=0 timing_overflow=0
##### EPROM_V131_TRACE_PROTO_0B total=59 strobe_overflow=0 timing_overflow=0
```

Never `141-NEW-TRACE.md`'s stale `91`/`119`/`59` — the `0x08` total here is `115`, confirming this is a
fresh capture, not a stale paste.

### F-06 discriminator (c): dump build (6 cases) vs. plain build (5 cases), via direct binary invocation

Dump build (`.pio/build/native_trace_v131/firestarter_native`, built with
`PLATFORMIO_BUILD_FLAGS="-D EPROM_V131_TRACE_DUMP"`), run directly:

```
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:383:test_smoke_setup_leaves_both_recorders_clean:PASS
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:384:test_smoke_timing_hook_fires_for_delay_and_delaymicroseconds:PASS
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:176:test_protocol_0x07_am27c512_capture_is_sound_and_deterministic:FAIL: Expected 198 Was 91. 0x07 AM27C512 DIP28_27512
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:176:test_protocol_0x08_am27c020_capture_is_sound_and_deterministic:FAIL: Expected 221 Was 115. 0x08 AM27C020 DIP32_27C020
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:176:test_protocol_0x0B_am2716_capture_is_sound_and_deterministic:FAIL: Expected 201 Was 59. 0x0B AM2716 DIP24_2716
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:392:test_dump_v131_traces:PASS

-----------------------
6 Tests 3 Failures 0 Ignored
FAIL
```

Plain build (no dump flag, cold rebuild), run directly, BEFORE the new fixture replaced the old one:

```
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:383:test_smoke_setup_leaves_both_recorders_clean:PASS
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:384:test_smoke_timing_hook_fires_for_delay_and_delaymicroseconds:PASS
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:176:test_protocol_0x07_am27c512_capture_is_sound_and_deterministic:FAIL: Expected 198 Was 91. 0x07 AM27C512 DIP28_27512
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:176:test_protocol_0x08_am27c020_capture_is_sound_and_deterministic:FAIL: Expected 221 Was 115. 0x08 AM27C020 DIP32_27C020
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:176:test_protocol_0x0B_am2716_capture_is_sound_and_deterministic:FAIL: Expected 201 Was 59. 0x0B AM2716 DIP24_2716

-----------------------
5 Tests 3 Failures 0 Ignored
FAIL
```

6 vs. 5 confirmed — the dump build genuinely registers one extra case (`test_dump_v131_traces`) behind
`#ifdef EPROM_V131_TRACE_DUMP`.

### Phase 143 adds ZERO entries — two independent reasons, both confirmed (not merely "as predicted")

1. `millis()` is pinned to `AlwaysReturn(0)` in `test_trace_eprom_v131.cpp:92`, and the guard at
   `eprom.cpp:399` is `if ((uint32_t)(millis() - last_emit_ms) >= EPROM_PROGRESS_EMIT_INTERVAL_MS)` with
   `last_emit_ms = millis()` at `:327` — so `0 - 0 = 0 >= 1000` is false forever; the 1000 ms interval
   guard can never fire in this harness.
2. Independently: the progress emit is a `Serial` frame (`LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, …)`), and
   the recorders capture only register strobes (`STROBE_KIND_DATA`/`STROBE_KIND_PIN`) and
   `delay`/`delayMicroseconds` timings — never `Serial` writes. So even an advancing clock could not have
   added a trace entry.

Both totals (`91`/`115`/`59`) landed exactly as measured with no adjustment for Phase 143 — consistent
with both reasons above independently predicting zero added frames.

### Prechange blob-SHA confirmation

```
$ git hash-object test/native/avr/_shared/eprom_v131_expected_prechange.h   # pre-staging
ca3e09f164e6e1c541ecb63d15bbebf5bce41d70
$ git rev-parse HEAD:test/native/avr/_shared/eprom_v131_expected_prechange.h   # post-commit
ca3e09f164e6e1c541ecb63d15bbebf5bce41d70
```

Identical — Phase 138's blob survives the rename and the commit intact.

### New fixture: pre-staging hash vs. post-commit HEAD:

```
$ git hash-object test/native/avr/_shared/eprom_v131_expected.h   # pre-staging (worktree)
8c956f431b3691dadb493946955680576279510b
$ git rev-parse HEAD:test/native/avr/_shared/eprom_v131_expected.h   # post-commit
8c956f431b3691dadb493946955680576279510b
$ git rev-parse HEAD~1   # meta.recorded_at_head names the commit's PARENT, by design (D-08)
7b2ba16caefb940e4aadbd90015f9925ce2593b8
```

### Identity gate transcript (post-commit)

```
$ python3 -m pytest tests/test_golden_trace_identity_eprom_v131.py -q -rs
......                                                                   [100%]
6 passed in 0.05s
```

### `native_trace_v131` transcript (post-commit, retiring the standing RED)

```
$ pio test -e native_trace_v131
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:383: test_smoke_setup_leaves_both_recorders_clean	[PASSED]
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:384: test_smoke_timing_hook_fires_for_delay_and_delaymicroseconds	[PASSED]
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:387: test_protocol_0x07_am27c512_capture_is_sound_and_deterministic	[PASSED]
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:388: test_protocol_0x08_am27c020_capture_is_sound_and_deterministic	[PASSED]
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:389: test_protocol_0x0B_am2716_capture_is_sound_and_deterministic	[PASSED]
native_trace_v131:native/avr/test_trace_eprom_v131 [PASSED] Took 10.94 seconds

================== 5 test cases: 5 succeeded in 00:00:10.940 ==================
```

### D-08's named non-claim (verbatim from `meta.prechange_header_non_claim`)

> D-08's named non-claim: with a single inventory record here, nothing gate-asserts
> `test/native/avr/_shared/eprom_v131_expected_prechange.h`. Its preserved blob
> `ca3e09f164e6e1c541ecb63d15bbebf5bce41d70` stays hand-verifiable via
> `git rev-parse HEAD:test/native/avr/_shared/eprom_v131_expected_prechange.h` and is cited in the phase
> record (144-03-SUMMARY.md), but it is NOT machine-checked by this or any other gate. No second inventory
> record is added to close this gap -- deferred work.

### Whole-repo confirmation

```
$ git status --porcelain
(empty)
$ python3 -m pytest tests/ -q
301 passed in 15.16s
$ python3 -m pytest tests/test_protocol_branch_inventory.py -q
7 passed in 0.06s
$ git show --stat --name-only HEAD | grep -c "^firestarter\|^src/"
0
```

301 passed matches the prior-work baseline exactly (no tests added or removed by this plan — only fixture
data changed). `test_protocol_branch_inventory.py`'s 7 tests confirm both `src/` blob pins (D-04) are
untouched throughout.

## Known Stubs

None — this plan modifies only a native test fixture and a JSON golden-trace inventory; no application
code, no UI components, and no stub patterns (hardcoded empty values, placeholder text, unwired data
sources) apply.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `native_trace_v131` is 5/5 — plan 144-04 can now diff the preserved pre-change arrays (198/221/201 in
  `eprom_v131_expected_prechange.h`) against the new post-change arrays (91/115/59 in
  `eprom_v131_expected.h`) for its structural six-segment exhaustiveness gate, using the 885 = 620 + 265
  denominator this plan's counts confirm (620 = 198+221+201 pre-change; 265 = 91+115+59 new).
- `/tmp/gsd-144/count_arrays.py` and `/tmp/gsd-144/count_kinds.py` remain on disk (scratch, not committed)
  for later plans in this phase to reuse, per the plan's own artifact list.
- `firestarter/src/` remains untouched this plan; both `protocol_branch_inventory.json` blob pins
  (`cedc88dc…`, `5dffe841…`) stay green.
- No `*_v131` env name was fed to `check_size_baseline.py` or `check_build_warnings.py` — plan 144-05 still
  owns that measurement, untouched by this plan.
- No blockers for plan 144-04.

## Self-Check: PASSED

- `firestarter/test/native/avr/_shared/eprom_v131_expected_prechange.h` -- FOUND on disk.
- `firestarter/test/native/avr/_shared/eprom_v131_expected.h` -- FOUND on disk.
- `firestarter/tests/golden/eprom_v131_trace_inventory.json` -- FOUND on disk.
- `.planning/phases/144-tests-build-verification/144-03-SUMMARY.md` -- FOUND on disk.
- Commit `2684252` (Task 2, firestarter submodule) -- FOUND in `git log --oneline --all`.

---
*Phase: 144-tests-build-verification*
*Completed: 2026-08-14*
