---
phase: 130-close-honesty-ledger-claim-gate-release-decision
plan: 03
subsystem: firmware
tags: [usb, py32f071, pid-codes, flash-path-record, cross-repo-sync-gate, arm-build]

requires:
  - phase: 129-flash-path-decision-and-pcb-requirements
    provides: "The two-layer [SHARED:S1]..[SHARED:S5] flash-path record and the 41-leg cross-repo sync gate (tests/test_flash_path_record_sync.py)."
provides:
  - "py32 USB device descriptor presents pid.codes' documented private-testing pair 1209:0001 instead of Puya Semiconductor's registered 0x36B7/0xFFFF."
  - "In-source provenance-and-warning comment below the two #ifndef/#endif guards in usb_cdc.c."
  - "Rewritten section 5(a)/5(d) in both flash-path record copies, byte-identical, 41-leg gate green."
  - "A local ARM delta pass proving the descriptor change is confined to one translation unit, recorded honestly (not as a byte-identity or absolute-size claim)."
affects: ["130-13", "130-14", "130-16 (gitlink bump, requirement ticking, ROADMAP/close)"]

tech-stack:
  added: []
  patterns: ["D-11 firmware value-swap under an unchanged D-17 ship gate", "cross-repo [SHARED:S4] body rewrite proven by sha256 equality of the extracted section, not by a whole-file diff"]

key-files:
  created: []
  modified:
    - firestarter/platform/py32f071/src/usb_cdc.c
    - firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md
    - .planning/v1.23-FLASH-PATH-DECISION.md

key-decisions:
  - "D-17 upheld: section 5(c) and test_flash_path_record_sync.py's _L2_SHIP_GATE constant are byte-unchanged; the ship-gate tension is carried as an owned residual, not resolved by amending the gate."
  - "The pid.codes warning is worded as an ask ('should'), never a requirement ('must'), per RESEARCH C-6."
  - "No absolute ARM flash/RAM figure is reported as a milestone figure; the ARM claim is a confined delta only (D-07)."

patterns-established:
  - "When a [SHARED:S*] body must change, author the replacement text once and apply it verbatim to both copies, then prove equality via the test module's own _extract_shared_section + sha256, never via a whole-file diff (whole-file diff is expected to differ outside the shared span)."

requirements-completed: []

coverage:
  - id: D1
    description: "py32 USB descriptor swapped from Puya's registered 0x36B7/0xFFFF to pid.codes' documented private-testing pair 1209:0001, with an in-source provenance-and-warning comment."
    verification:
      - kind: unit
        ref: "firestarter/tests/test_flash_path_record_sync.py (41 legs, full suite)"
        status: pass
      - kind: integration
        ref: "cd firestarter && pio test -e native (141 test cases)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Section 5(a) and 5(d) of the [SHARED:S4] flash-path record rewritten identically in both copies; 5(c) ship gate and _L2_SHIP_GATE proven byte-unchanged."
    verification:
      - kind: unit
        ref: "firestarter/tests/test_flash_path_record_sync.py::TestFlashPathRecordSync::test_vid_pid_decision_and_ship_gate[meta] and [fw]"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_flash_path_record_sync.py -k shared_sections_match (S4 leg)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Local ARM pass recorded as a confined-delta claim for the descriptor change (no byte-identity or absolute-size overclaim)."
    verification:
      - kind: other
        ref: "local cmake -S platform/py32f071 -B build/py32f071 -G Ninja + cmake --build build/py32f071, pre-edit and post-edit"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-08-02
status: complete
---

# Phase 130 Plan 03: PY32 USB Descriptor Swap + Flash-Path Record Rewrite Summary

**py32 USB descriptor swapped from Puya Semiconductor's registered 0x36B7/0xFFFF to pid.codes' documented private-testing pair 1209:0001 (D-11), with the [SHARED:S4] flash-path record rewritten identically in both copies and D-17's ship gate proven byte-unchanged.**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-08-02T16:31:35Z
- **Tasks:** 3/3 completed
- **Files modified:** 3 (`usb_cdc.c`, `FLASH-PATH-AND-PCB.md`, `v1.23-FLASH-PATH-DECISION.md`)

## Accomplishments

- **Task 1:** `firestarter/platform/py32f071/src/usb_cdc.c` line 20 (`FIRESTARTER_USB_VID`) changed `0x36B7U` → `0x1209U`; line 24 (`FIRESTARTER_USB_PID`) changed `0xFFFFU` → `0x0001U`. Both remain inside their original `#ifndef`/`#endif` guards — no structural change, `USB_DEVICE_DESCRIPTOR_INIT` untouched. A new provenance-and-warning comment block was added directly below the second `#endif` (line 25), stating: what the pair is (pid.codes' documented private-testing id, not allocated); the warning worded as an ask per pid.codes' terms (RESEARCH C-6: "should", never "must"); what it replaced (Puya Semiconductor's registered `0x36B7`/`0xFFFF`, copied verbatim from the pinned SDK's own CDC example); and where the decision lives (both copies of the flash-path record, section 5, with the (c) ship gate stated as unchanged).
- **Task 2:** Section 5(a) ("What the descriptor currently presents, and where it came from") and 5(d) ("What this phase does and does not change") were rewritten identically, character-for-character, in both `.planning/v1.23-FLASH-PATH-DECISION.md` and `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md`. 5(a) now describes the post-D-11 state while retaining the full provenance record of the superseded `0x36B7`/`0xFFFF` pair (Puya Semiconductor, `usbd_cdc_if.c` lines 9–10, `pycdc.inf` lines 28/31, the pinned `GIT_TAG`). 5(d) now states `usb_cdc.c` **is** edited this phase under D-11, reversing Phase 129 D-06, and that section 5(c)'s ship gate is unchanged and still binds. Sections 5(b), 5(c), 5(e), and the closing shared-verbatim sentence were left byte-unchanged in both copies; `tests/test_flash_path_record_sync.py` was not touched at all.
- **Task 3:** A local ARM pass was run both before and after the descriptor edit (pinned SDK, `arm-none-eabi-gcc` 14.2.1 / `cmake` 4.4.0 / `ninja` 1.13.0, all measured present — see drift note below). Configure and build exited 0 in both states. The rebuild after restoring the edit recompiled **exactly one** translation unit (`usb_cdc.c.obj`) plus the final link — no other object changed. The `.hex` image's SHA-256 differs between the two builds (confirming the descriptor bytes actually changed), while the `.text`/`.data`/`.bss` totals are numerically identical at both the object and ELF level (996/16/2258 and 27260/112/5888 respectively, in both states) — a size-neutral content change, reported here strictly as a delta, never as byte-identity.

## Task Commits

Each task was committed atomically. Task 1 and the firmware half of Task 2 are commits **inside the `firestarter` submodule** on `v1.23-py32f071-integration`; the meta half of Task 2 is a commit **in the meta repo**. Task 3 produced no code change (its output is this SUMMARY) and made no additional commit.

1. **Task 1: Change the two USB descriptor #define values and add the source warning** — `firestarter@c96b576` (`feat(130-03): swap py32 USB descriptor to pid.codes 1209:0001`)
2. **Task 2 (firmware copy): Rewrite section 5(a)/5(d) in FLASH-PATH-AND-PCB.md** — `firestarter@05c20bf` (`docs(130-03): rewrite [SHARED:S4] 5(a)/5(d) for the D-11 descriptor swap`)
2. **Task 2 (meta copy): Rewrite section 5(a)/5(d) in v1.23-FLASH-PATH-DECISION.md** — meta `8aa25f0` (`docs(130-03): rewrite [SHARED:S4] 5(a)/5(d) for the D-11 descriptor swap`)
3. **Task 3: Local ARM pass and confined-delta record** — no additional commit (recorded here; `build/` was never staged, see below)

**Plan metadata:** this SUMMARY, committed separately (see below) — no gitlink bump, no ROADMAP/STATE/REQUIREMENTS edit per this plan's `<orchestrator_held_writes>`.

## Files Created/Modified

- `firestarter/platform/py32f071/src/usb_cdc.c` — `FIRESTARTER_USB_VID`/`FIRESTARTER_USB_PID` swapped to pid.codes' `1209:0001`; provenance-and-warning comment added below line 25.
- `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md` — `[SHARED:S4]` 5(a)/5(d) rewritten.
- `.planning/v1.23-FLASH-PATH-DECISION.md` — `[SHARED:S4]` 5(a)/5(d) rewritten (identical body to the firmware copy).

## Decisions Made

- **D-17 upheld, not re-litigated.** Section 5(c) and `test_flash_path_record_sync.py`'s `_L2_SHIP_GATE` constant were left byte-unchanged. Proof: `git -C firestarter diff -- tests/test_flash_path_record_sync.py` is empty, and both `[meta]`/`[fw]` parametrizations of `test_vid_pid_decision_and_ship_gate` pass, which asserts `_L2_SHIP_GATE` is a verbatim substring of the extracted section-5 body in both copies.
- **The warning is worded as an ask, not a requirement**, per RESEARCH C-6 (pid.codes' terms say "should", not "must") — this applies both to the in-source comment (Task 1) and to 5(a)'s restatement of that comment (Task 2).
- **No absolute ARM figure is reported as a milestone figure.** The measured ELF totals (27260/112/5888 text/data/bss, both pre- and post-edit) are reported purely as inputs to the delta claim ("this object changed, that object's size is unchanged, the overall image size is unchanged, but the image content is not byte-identical"), per D-07.

## Deviations from Plan

None — plan executed exactly as written. One incidental finding surfaced during Task 3's acceptance-criteria check, recorded below rather than fixed (out of this plan's file scope).

### Findings (not fixed — out of scope)

**1. `firestarter/build/` is not covered by `.gitignore`.** Task 3's acceptance criteria required confirming `build/` is ignored, and instructed *"if it is not, do not add it to the commit"* — it explicitly does not ask this plan to fix `.gitignore` (which is not in this plan's `files_modified`). `firestarter/.gitignore` currently ignores `.pio` (the PlatformIO/AVR build output) but has no entry for `build/` (the CMake/ARM build output introduced by Phase 123's composite ARM build action). The build directory was created for this task's local ARM pass, verified never staged (`git status --short` inside the submodule showed only `?? build/` before cleanup), and then removed (`rm -rf build/`) rather than committed or left dangling. A future phase should add `build/` to `firestarter/.gitignore`; not done here because `.gitignore` is outside this plan's `files_modified` scope.

## Environment-Availability Drift (RESEARCH row correction)

`130-RESEARCH.md`'s Environment Availability finding recorded `arm-none-eabi-gcc`/`cmake`/`ninja` as **absent but installable**. Measured at execution time (2026-08-02), all three are **present**:

- `arm-none-eabi-gcc (15:14.2.rel1-1) 14.2.1 20241119`
- `cmake version 4.4.0`
- `ninja 1.13.0.git.kitware.jobserver-pipe-1`

This is a drift in the helpful direction — no toolchain installation was needed or performed this plan.

## ARM Pass — Confined-Delta Record (Task 3)

Sequence run against the pinned CMake/Ninja composite-action commands (`cmake -S platform/py32f071 -B build/py32f071 -G Ninja -DCMAKE_BUILD_TYPE=Release` / `cmake --build build/py32f071`):

| State | Configure exit | Build exit | ELF text/data/bss | `usb_cdc.c.obj` text/data/bss | `.hex` SHA-256 |
|---|---|---|---|---|---|
| Pre-edit (`usb_cdc.c` restored to `c96b576^`) | 0 | 0 | 27260 / 112 / 5888 | 996 / 16 / 2258 | `9599a625b1bc7357ec512952f76ee27c6897fabd1c7a1eb4645068c1935913dc` |
| Post-edit (restored to committed HEAD, incremental rebuild) | — (no reconfigure needed) | 0 | 27260 / 112 / 5888 | 996 / 16 / 2258 | `91da9edf1bcc5cb513684afbe5e2c1ba5c3fd5993b2d4656adda4cd33312eeeb` |

- `ls build/py32f071/firestarter_*.hex` listed exactly one file, `firestarter_py32f071.hex`, in both states — matching `asset_candidates("py32f071")[0]`'s binding (REL-04).
- The incremental rebuild's Ninja log shows exactly two build steps: `Building C object CMakeFiles/firestarter_py32f071.elf.dir/src/usb_cdc.c.obj` and `Linking CXX executable firestarter_py32f071.elf` — **one** changed translation unit (`usb_cdc.c`) plus its necessary relink; no other object recompiled.
- **The permitted claim, stated precisely:** the ARM target still configures and compiles cleanly in both states; the recompile is confined to `usb_cdc.c`'s object; the object's and the image's `.text`/`.data`/`.bss` sizes are numerically unchanged (996/16/2258 and 27260/112/5888 respectively) — a size-neutral value swap, not a structural change. **This is not a byte-identity claim**: the two `.hex` files have different SHA-256 hashes, because the descriptor bytes (VID/PID) changed by design (RESEARCH/plan explicitly forbid claiming byte-identity here). No absolute ARM flash/RAM figure from this local build is reported as a milestone figure (D-07) — the 27260/112/5888 figures above are reported only as inputs to the pre/post delta, and are not comparable to any CI-measured figure.
- `firestarter/build/` was never staged or committed (`git status --short` showed no tracked changes from it); it was removed after this record was captured. See "Findings" above regarding `.gitignore`.

## Sync-Gate Proof (Task 2)

- `cd firestarter && FIRESTARTER_META_ROOT=/workspaces python3 -m pytest tests/test_flash_path_record_sync.py -q` → **41 passed, 0 failed** (same leg count as before the edit — no leg skipped or lost).
- `-k "shared_sections_match"` → 5 passed (all five `[SHARED:S*]` keys, S4 included).
- `-k "vid_pid_decision_and_ship_gate"` → 2 passed (`[meta]` and `[fw]` parametrizations — the `_L2_SHIP_GATE` byte-exact leg; both passing proves 5(c) was not touched). This is the leg that asserts every `_S4_NEEDLES` token is present in both copies' extracted section-5 body.
- `git -C firestarter diff -- tests/test_flash_path_record_sync.py` → empty.
- The two extracted `[SHARED:S4]` bodies (via the test module's own `_extract_shared_section`) hash **equal**: `cf8f749332dee7a1c6cab96ca5fecb68b6100914721f1d09476697cd965998f3` for both the meta and the firmware copy. (Whole-file `git diff` between the two copies is **not** empty, by design — they differ outside section 5.)
- `git -C /workspaces diff --stat -- .planning/v1.23-FLASH-PATH-DECISION.md` shows two hunks (one at 5(a), one at 5(d)); neither overlaps lines 200–204 (section 5(c), the ship gate).
- `cd firestarter && python3 -m pytest tests/ -q` → **221 passed, 0 failed**.
- `cd firestarter && pio test -e native` → **141 test cases, 141 succeeded**; `usb_cdc.c` (py32-only TU) does not appear in the native build log.

## Gitlink / Requirement Status (unchanged by this plan, as required)

- `git -C /workspaces diff --cached --stat` never showed `firestarter` — the gitlink was **not** bumped or staged. `git -C /workspaces status --short` shows `M firestarter` (expected: the submodule's working commit moved locally; the gitlink pointer in the meta repo's index is untouched).
- No requirement id is ticked by this plan. `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, `PROJECT.md` were not modified.

## Issues Encountered

None beyond the `.gitignore` finding above.

## Next Phase Readiness

- The D-11 descriptor swap and its lockstep record update are complete and committed inside the `firestarter` submodule (`c96b576`, `05c20bf`) and the meta repo (`8aa25f0`), all on their respective milestone branches, ready for a later plan (130-13/130-14/130-16) to bump the gitlink.
- D-17's ship gate (section 5(c), `_L2_SHIP_GATE`) remains an owned residual: no board ships and no release advertises a USB identity until a real PID allocation exists under VID `0x1209`. This plan changes nothing about that gate's binding force.
- `firestarter/build/`'s missing `.gitignore` entry is a small, low-risk finding for a future phase to pick up; it did not block this plan and nothing was committed as a result of it.

---
*Phase: 130-close-honesty-ledger-claim-gate-release-decision*
*Completed: 2026-08-02*

## Self-Check: PASSED

- FOUND: `firestarter/platform/py32f071/src/usb_cdc.c`
- FOUND: `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md`
- FOUND: `.planning/v1.23-FLASH-PATH-DECISION.md`
- FOUND: `.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-03-SUMMARY.md`
- FOUND: `firestarter@c96b576` (Task 1 commit)
- FOUND: `firestarter@05c20bf` (Task 2 firmware-copy commit)
- FOUND: meta `8aa25f0` (Task 2 meta-copy commit)
- FOUND: meta `e233426` (plan-completion SUMMARY commit)
- `git -C /workspaces diff --cached --stat -- firestarter` → empty (gitlink not staged)
- `git -C firestarter rev-parse --abbrev-ref HEAD` → `v1.23-py32f071-integration` (not detached)
