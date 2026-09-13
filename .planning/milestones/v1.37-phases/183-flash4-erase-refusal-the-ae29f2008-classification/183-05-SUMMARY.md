---
phase: 183-flash4-erase-refusal-the-ae29f2008-classification
plan: 05
subsystem: firmware-docs
tags: [platformio, avr-gcc, size-baseline, gate-docstring, blast-radius]

# Dependency graph
requires:
  - phase: 183-04
    provides: "flash_5v_page.cpp with the 12V bulk-erase path deleted at all four sites, and the 184->185 native case-count consequence"
  - phase: 183-01
    provides: "pre-deletion cold-build baseline flash/RAM figures for uno, uno328pb, leonardo, to measure this plan's shrink against"
provides:
  - "check_erase_no_vpp.py and its planted fixture with no impossible line citation and no reference to the deleted routine, rewritten to state the copy-source hazard is gone while the gate stays armed"
  - "PROTOCOLS.md's 0x05 erase-model paragraph and CLAUDE.md's 0x0D warning, both corrected to describe the post-deletion tree"
  - "measured post-deletion cold-build shrink for uno, uno328pb, leonardo against 183-01's pre-deletion figures, and the observed (not predicted) default-mode divergence plus merge05-mode pass against BASE-01"
affects: [183-06, 185]

actuals:
  tokens: 6800
  tasks: 3
  commits: 5

tech-stack:
  added: []
  patterns:
    - "Citation-by-symbol-and-scope repair: a deleted routine's line-range citation is removed outright (never replaced with a corrected range), and the hazard it warned about is re-expressed structurally (the shape a reader could still re-derive from the datasheet) rather than by naming the now-absent symbol"

key-files:
  created: []
  modified:
    - "firestarter/scripts/check_erase_no_vpp.py (docstring proximity/rationale paragraph rewritten)"
    - "firestarter/tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp (header and in-body comments repaired, comments-only)"
    - "firestarter/PROTOCOLS.md (0x05 erase-model paragraph rewritten)"
    - "firestarter/CLAUDE.md (0x0D warning's dangling pointer replaced)"

key-decisions:
  - "The checker's 'proximity, not absence' rationale was rewritten to state the copy-source hazard is REMOVED from the tree while the gate stays armed against a re-derived hazard (from the AT28C256 datasheet's own hardware Chip Erase mode) rather than a live copy source — matching the plan's JOB 2 instruction exactly"
  - "PROTOCOLS.md's now-false 'deliberately unadvertised' bulk-erase clause was replaced with the true post-deletion state (no chip-level erase implemented; host clears FLAG_CAN_ERASE; firmware's eprom_erase also refuses) and a citation to Backlog 999.63 (\"Software chip-erase for the `0x05` family\", filed by 183-02), so the paragraph does not read as a claim the part can never be erased"
  - "CLAUDE.md's 0x0D warning replaced the dangling flash_5v_page_erase_execute pointer with the hazard itself (the datasheet's 12V-on-OE mode) and the gate that enforces its absence, while preserving algorithm 5's FLAG_CAN_ERASE exclusion and its reason verbatim in substance"
  - "The two concurrent 'pio test -e native' invocations that raced early in Task 3 (see Deviations) were resolved by killing the duplicate and re-running both native envs from a clean .pio/build/ — the resulting 185/185 passes on both envs supersede the corrupted first run"

requirements-completed: [SAFE-08]

coverage:
  - id: D1
    description: "check_erase_no_vpp.py's docstring no longer cites the impossible flash_5v_page.cpp:196-231 range, cites by symbol/structural shape, and the checker still exits 0 for the right reason (real body, both non-vacuity anchors present)"
    requirement: "SAFE-08"
    verification:
      - kind: unit
        ref: "python3 scripts/check_erase_no_vpp.py (exit 0, PASS: line naming eeprom28c_erase_execute)"
        status: pass
      - kind: unit
        ref: "python3 -m pytest tests/test_check_erase_no_vpp.py -q (7 passed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The identical impossible citation and lift-source symbol are repaired a second and third time in the planted fixture's header and in-body comments, with the fixture's violation-path behaviour unchanged (comments-only diff)"
    requirement: "SAFE-08"
    verification:
      - kind: other
        ref: "git diff <merge-base> -- tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp shows only comment-line hunks; test_check_erase_no_vpp.py::test_planted_fixture_fails_reachability still asserts exit != 0 with FAIL:/CTRL_VPP/firestarter_set_control_register/line-number text"
        status: pass
    human_judgment: false
  - id: D3
    description: "PROTOCOLS.md's 0x05 erase-model paragraph and CLAUDE.md's 0x0D warning no longer name flash_5v_page_erase_execute or claim an unadvertised bulk erase exists; FLAG_CAN_ERASE and its exclusion reason survive in CLAUDE.md; the VPP-behavior sentence is byte-unchanged"
    requirement: "SAFE-08"
    verification:
      - kind: other
        ref: "/usr/bin/grep -n 'flash_5v_page_erase_execute' PROTOCOLS.md CLAUDE.md (exit 1); /usr/bin/grep -n 'deliberately unadvertised' PROTOCOLS.md (exit 1); /usr/bin/grep -n 'FLAG_CAN_ERASE' CLAUDE.md (2 hits); /usr/bin/grep -n 'None (5V-only operation)' PROTOCOLS.md (present, unchanged); git diff --stat touches only PROTOCOLS.md + CLAUDE.md"
        status: pass
    human_judgment: false
  - id: D4
    description: "Post-deletion cold-build shrink measured for uno/uno328pb/leonardo against 183-01's pre-deletion figures; default-mode gate observed diverging (exit 1, not zero-envs-compared, not exit 2); --policy merge05 gate against BASE-01 observed passing (exit 0), authoring no new MERGE-05 exemption; size_baseline.json byte-unchanged; both CI native envs pass 185/185 and the firmware pytest suite passes"
    requirement: "SAFE-08"
    verification:
      - kind: integration
        ref: "three D-16 cold builds (rm -rf .pio/build/<env> + pio run -e <env>) for uno/uno328pb/leonardo; check_size_baseline.py default mode (rc=1, FAIL: divergence lines); check_size_baseline.py --policy merge05 --baseline size_baseline_base01.json (rc=0, PASS: line); pio test -e native (185/185); pio test -e native_nodevtools (185/185); python3 -m pytest tests/ -q (360 passed); git status --porcelain --untracked-files=no -- scripts/baseline/ (empty)"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-09-11
status: complete
---

# Phase 183 Plan 05: Repair SAFE-08's Documentation Blast Radius and Measure the Shrink Summary

**Repaired the four documents that still described the deleted 12V bulk-erase routine — an impossible line citation appearing three times, a false "deliberately unadvertised" claim, and a dangling symbol pointer — and measured the post-deletion firmware shrink (−234 B / −238 B / −284 B flash on uno / uno328pb / leonardo) with the default-mode byte-identity gate observed diverging for the predicted reason and the `--policy merge05` band gate observed passing against BASE-01 with no new exemption.**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-09-11T09:35:00Z (approx)
- **Completed:** 2026-09-11T10:30:00Z (approx)
- **Tasks:** 3
- **Files modified:** 4 (`firestarter/scripts/check_erase_no_vpp.py`, `firestarter/tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp`, `firestarter/PROTOCOLS.md`, `firestarter/CLAUDE.md`)

## Accomplishments
- `scripts/check_erase_no_vpp.py`'s docstring no longer cites the impossible `flash_5v_page.cpp` `lines 196-231` range (a range that cannot exist in a 225-line file); the rationale paragraph now states the copy-source hazard is REMOVED from the tree while the gate stays armed against the hazard shape being re-derived from the datasheet. The checker still exits 0 against the real `eeprom28c_erase_execute` body, printing its `PASS:` line and naming both non-vacuity anchors.
- The identical impossible citation, carried a second and third time in `tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp`'s header and in-body `PLANTED VIOLATION` comments, is repaired the same way — by symbol/structural shape, not by line number. The fixture's violation-path behaviour is unchanged (verified as a comments-only diff), and the paired pytest still drives the checker to exit 1 (a real hazard token: `CTRL_VPP`, `firestarter_set_control_register`, with line numbers) — never exit 2.
- `PROTOCOLS.md`'s `0x05` erase-model paragraph no longer claims a capability-gated bulk erase exists and is deliberately unadvertised; it now states the firmware implements no chip-level erase for this protocol at all, that the host clears `FLAG_CAN_ERASE` for algorithm 5 and the firmware's `eprom_erase` also refuses (refused twice over), and cites the silicon's own software chip-erase sequence as a recorded backlog item (Backlog 999.63) rather than a firmware capability. The `VPP behavior` sentence is byte-unchanged.
- `firestarter/CLAUDE.md`'s `0x0D` warning no longer points at the deleted `flash_5v_page_erase_execute` symbol; it now names the hazard itself (the datasheet's 12V-on-OE hardware Chip Erase mode) and the gate that enforces its absence, while preserving algorithm 5's `FLAG_CAN_ERASE` exclusion and its reason.
- A post-deletion cold build of all three AVR targets records the shrink against `183-01`'s pre-deletion figures: uno −234 B flash / +0 B RAM, uno328pb −238 B flash / +0 B RAM, leonardo −284 B flash / +0 B RAM. The default-mode `check_size_baseline.py` gate is observed diverging (exit 1, per-env `FAIL:` lines naming observed vs. baseline) — the predicted, correct outcome after a firmware change — and the `--policy merge05` gate against BASE-01 is observed passing (exit 0), so the shrink authors no new MERGE-05 exemption. `size_baseline.json` is confirmed byte-unchanged.

## Task Commits

Each task was committed atomically inside the `firestarter` submodule, with the meta repo's gitlink advanced in a paired `chore` commit after each:

1. **Task 1: Repair check_erase_no_vpp.py's docstring and the planted fixture's prose (D-14)**
   - `1564a60` (docs, firestarter) — impossible citation removed, proximity rationale rewritten; fixture header + in-body comments repaired (comments-only)
   - `ab3dcddd` (chore, meta) — gitlink advance
2. **Task 2: Bring PROTOCOLS.md and firestarter/CLAUDE.md current (D-12, D-04)**
   - `3e6d75a` (docs, firestarter) — PROTOCOLS.md erase-model paragraph rewritten; CLAUDE.md 0x0D warning's dangling pointer replaced
   - `f774ca0d` (chore, meta) — gitlink advance
3. **Task 3: Measure the shrink and record which gate it reddens (D-15)** — read-only assertions (three cold builds, two gate-mode runs, both native CI envs, the firmware pytest suite); no tracked file modified, so no source commit. Evidence recorded below.

**Plan metadata:** commit for this SUMMARY.md follows immediately after this file is written (see `git_commit_metadata` step).

## Files Created/Modified
- `firestarter/scripts/check_erase_no_vpp.py` — the "Proximity, not absence" docstring paragraph rewritten: no line-range citation, states the copy-source hazard is gone while the gate stays armed against a re-derived hazard shape; `--function`/`--source` defaults, brace-matching, comment-scanning, both non-vacuity anchors, exit-code taxonomy, and the `No CI leg` disclosure are all mechanically unchanged
- `firestarter/tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp` — file-header comment's citation removed and re-expressed structurally; in-body `PLANTED VIOLATION` comment's lift-source name replaced the same way; zero hazard-token literals added or removed
- `firestarter/PROTOCOLS.md` — `0x05` **Erase model** paragraph's final clause rewritten from the false "deliberately unadvertised bulk erase" claim to the true post-deletion refusal-twice-over state, with a Backlog 999.63 citation; **VPP behavior** sentence untouched
- `firestarter/CLAUDE.md` — `0x0D` warning's dangling `flash_5v_page_erase_execute` pointer replaced with the hazard itself and the gate that guards it; `FLAG_CAN_ERASE` exclusion and its reason preserved

## Decisions Made
- See `key-decisions` in frontmatter above.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Two concurrent `pio test -e native` invocations raced on the same build output, producing a false `ERRORED` result**
- **Found during:** Task 3, running `pio test -e native` per the plan-level success criteria
- **Issue:** The first `pio test -e native` invocation auto-backgrounded past its 120s tool timeout; a second explicit background invocation of the identical command was then started before confirming the first had actually stopped, so two processes wrote/executed `.pio/build/native/firestarter_native` concurrently. `native/avr/test_val_5v_page` failed with `[Errno 26] Text file busy`, and the run reported `171 test cases: 170 succeeded` — a tooling race, not a real regression (the same suite passes cleanly when run in isolation, see below).
- **Fix:** Killed the duplicate process pair, removed `.pio/build/native` and `.pio/build/native_nodevtools` to clear any partially-written state, and re-ran both native envs sequentially (never concurrently) with a longer timeout.
- **Files modified:** None (build-directory state only, not a tracked file)
- **Verification:** Re-run results: `pio test -e native` → `185 test cases: 185 succeeded`; `pio test -e native_nodevtools` → `185 test cases: 185 succeeded`. Both match 183-04's recorded case count exactly.
- **Committed in:** N/A (no tracked file affected)

---

**Total deviations:** 1 auto-fixed (1 Rule 3 tooling race, self-corrected within Task 3, no code or doc change required).
**Impact on plan:** None on the shipped documents — the race was in test-execution tooling, not in the four files this plan edited. The corrected 185/185 result on both envs is the evidence recorded below.

## D-14 Repair Evidence (Task 1)

```
$ python3 scripts/check_erase_no_vpp.py; echo "rc=$?"
PASS: eeprom28c_erase_execute() in /workspaces/firestarter/src/proms/eeprom_28c.cpp (lines 322-337, 16 lines scanned) contains no VPP/VPE control-register, chip-enable/disable, or bus-config-bypassing hazard token
rc=0

$ python3 -m pytest tests/test_check_erase_no_vpp.py -q
.......                                                                  [100%]
7 passed in 0.58s

$ /usr/bin/grep -n '196-231' scripts/check_erase_no_vpp.py tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp; echo "rc=$?"
rc=1

$ /usr/bin/grep -n 'flash_5v_page' scripts/check_erase_no_vpp.py tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp; echo "rc=$?"
rc=1
```

`git diff <merge-base origin/beta HEAD> -- tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp` shows two hunks, both entirely inside `//` comment lines (the header block and the in-body `PLANTED VIOLATION` comment) — no executable line of the fixture changed.

## D-12/D-04 Repair Evidence (Task 2)

```
$ /usr/bin/grep -n 'flash_5v_page_erase_execute' PROTOCOLS.md CLAUDE.md; echo "rc=$?"
rc=1

$ /usr/bin/grep -n 'deliberately unadvertised' PROTOCOLS.md; echo "rc=$?"
rc=1

$ /usr/bin/grep -n 'FLAG_CAN_ERASE' CLAUDE.md
121:`FLAG_CAN_ERASE` exclusion permanently, for exactly the same reason: no
216:- `FLAG_CAN_ERASE (0x02)` — chip supports erase before write

$ /usr/bin/grep -n 'None (5V-only operation)' PROTOCOLS.md
113:**VPP behavior:** None (5V-only operation). The internal charge pump on the chip drives write electricals; the RURP VPP regulator is not used for this bucket.
```

`git diff <merge-base> --stat -- PROTOCOLS.md CLAUDE.md` shows exactly these two files changed (7 insertions, 4 deletions across both), no others.

## D-15 Shrink Measurement (Task 3)

**Cold-build figures (D-16 procedure: `rm -rf .pio/build/<env>` then exactly one `pio run -e <env>`), post-deletion:**

| Env | post-deletion flash_used | pre-deletion flash_used (183-01) | **shrink (flash)** | post-deletion ram_used | pre-deletion ram_used (183-01) | shrink (RAM) |
|---|---|---|---|---|---|---|
| uno | 22734 | 22968 | **−234 B** | 1434 | 1434 | +0 B |
| uno328pb | 22778 | 23016 | **−238 B** | 1440 | 1440 | +0 B |
| leonardo | 24830 | 25114 | **−284 B** | 1875 | 1875 | +0 B |

Each shrink figure is computed within the same env only, never across envs, per the plan's instruction.

**Post-deletion position against BASE-01** (`scripts/baseline/size_baseline_base01.json`, unmodified):

| Env | post-deletion flash_used | BASE-01 flash_used | **delta vs BASE-01** |
|---|---|---|---|
| uno | 22734 | 24824 | **−2090 B** |
| uno328pb | 22778 | 24874 | **−2096 B** |
| leonardo | 24830 | 26906 | **−2076 B** |

The tree sat below BASE-01 even before this phase (RESEARCH.md § A.3: −1872 / −1874 / −1808), with 724 B of named MERGE-05 exemptions already stacked on top and unused; this phase's deletion widens that margin further.

**Default-mode gate (strict byte-identity against the LIVE `scripts/baseline/size_baseline.json`):**

```
$ python3 scripts/check_size_baseline.py --avr-log uno=<post-uno.log> --avr-log uno328pb=<post-uno328pb.log> --avr-log leonardo=<post-leonardo.log>
FAIL:
  uno: flash_used baseline=22952 observed=22734
  uno328pb: flash_used baseline=23000 observed=22778
  leonardo: flash_used baseline=25098 observed=24830
rc=1
```

**This `rc=1` means DIVERGENCE** (per-env `flash_used baseline=… observed=…` lines), the correct and predicted outcome of a byte-identity gate after a firmware change — explicitly NOT the gate's other `rc=1` meaning (`no envs compared`, which never appeared) and NOT `rc=2` (unparseable log / malformed CLI, which also never appeared). This is exactly the observation D-15 says makes Phase 185's `size_baseline.json` re-record depend on this phase.

**Band-mode gate (`--policy merge05` against the FROZEN `scripts/baseline/size_baseline_base01.json`):**

```
$ python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log uno=<post-uno.log> --avr-log uno328pb=<post-uno328pb.log> --avr-log leonardo=<post-leonardo.log>
PASS: uno(flash=22734/32768[-2090<=788=band64+exempt96+seam210+lock288+erase130],ram=1434/2048[-139<=2=seam2]), uno328pb(flash=22778/32768[-2096<=788=band64+exempt96+seam210+lock288+erase130],ram=1440/2048[-139<=2=seam2]), leonardo(flash=24830/32768[-2076<=724=band0+exempt96+seam210+lock288+erase130],ram=1875/2560[-139<=2=seam2])
rc=0
```

**This `rc=0`** means the shrink stays inside MERGE-05's effective allowance against BASE-01 on all three targets, with room to spare on every one (a negative delta is always within a positive band ceiling). **No new MERGE-05 exemption is authored by this measurement** — the four existing named exemptions (defect-fix, page-size-seam, lock-status-read, erase) are unchanged, and CLAIM-05's no-new-exemption clause survives.

`git status --porcelain --untracked-files=no -- scripts/baseline/` is empty — `size_baseline.json` and `size_baseline_base01.json` are both byte-unchanged.

**Both CI native envs, run from `firestarter/` (re-run after the Task 3 tooling race, see Deviations):**
```
$ pio test -e native
================ 185 test cases: 185 succeeded in 00:02:56.733 ================

$ pio test -e native_nodevtools
================ 185 test cases: 185 succeeded in 00:03:15.128 ================
```

**Firmware pytest suite (no CI leg):**
```
$ python3 -m pytest tests/ -q
360 passed in 96.40s
```

**Phase 185's two named inputs, carried forward:**
1. **The flash-byte shrink measured here** (D-15's original text): uno −234 B, uno328pb −238 B, leonardo −284 B against the current `size_baseline.json`'s live figures (22952/23000/25098), with the divergence gate observed exiting 1 for that reason.
2. **The native case count**, from 183-04: both `native_envs.cases` entries move from `184` to `185` in `size_baseline.json` — `check_size_baseline.py`'s `compare_native` asserts `cases` EXACTLY, so this is an independent input the flash-byte shrink does not cover. Both this plan's re-run (185/185 on both envs) and 183-04's original observation confirm the same number.

Neither input was applied to `size_baseline.json` in this plan, by design — that file is byte-unchanged (confirmed above), and re-recording it is Phase 185's own work.

## Issues Encountered

None beyond the self-corrected Task 3 tooling race documented above (no open blockers).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- SAFE-08's full documentation blast radius is now repaired: `check_erase_no_vpp.py`, its planted fixture, `PROTOCOLS.md`, and `firestarter/CLAUDE.md` all describe the tree that exists, with no impossible line citation and no reference to the deleted routine anywhere.
- The `0x0D` erase gate still passes for the right reason and still proves it can see a real hazard (both directions independently verified).
- The firmware shrink is measured with the same D-16 cold procedure on both sides of the subtraction; the byte-identity gate it reddens and the band gate it does not are both observed, not predicted. Phase 185 has exactly two named inputs waiting for its `size_baseline.json` re-record: the flash-byte shrink (this plan) and the native case count 184→185 (183-04).
- No blockers.

---
*Phase: 183-flash4-erase-refusal-the-ae29f2008-classification*
*Completed: 2026-09-11*

## Self-Check: PASSED
