---
phase: 161-board-board-sweep-three-boards-on-rev-2-0
plan: 02
subsystem: infra
tags: [bench, rig-tooling, pre-proof, uno328pb, leonardo, caterina, avr109, urclock, no-sweep-position]

# Dependency graph
requires:
  - phase: 161-board-board-sweep-three-boards-on-rev-2-0 (plan 01)
    provides: append_evidence.py, PROCEDURE.md Amendment 3
provides:
  - "BRINGUP-uno328pb-v133/READBACK-VERDICT.json — first-ever v1.33-arm judged match on an ATmega328PB (D-10 closed)"
  - "BRINGUP-leonardo-provenance/PREPROOF.md — the measured, copy-runnable A3/B2 P-02 command sequence for a Leonardo/Caterina target"
  - "capture_provenance.py --board-probe-json / --no-image-plan — two additive seams, default behavior unchanged"
affects: [161-03, 161-04, 161-05]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-phase Caterina timing model: the ~8s inactivity window governs only the bootloader
       phase (touch onset -> avr109 probe completing, measured ~3.5-3.8s); once that probe's
       own avr109-exit resets the MCU back to the application, a separate ~2s USB
       re-enumeration settle is required before the next serial call, after which no further
       time pressure applies"
    - "Additive tool seam: an optional flag that lets a caller substitute an already-obtained
       probe result for a tool's own internal re-probe, keeping the default (flag omitted)
       code path byte-identical to prior behavior"

key-files:
  created:
    - .planning/v1.34/bench/cells/BRINGUP-uno328pb-v133/ (READBACK-VERDICT.json, PREPROOF.md, board_probe.json, flash_readback.bin, expected_span.bin, judged_span.bin, SHA256SUMS.txt, logs/)
    - .planning/v1.34/bench/cells/BRINGUP-leonardo-provenance/ (provenance_BRINGUP-leonardo-provenance.json, PREPROOF.md, board_probe.json, touch.json, check_arms_teardown.json, logs/)
  modified:
    - .planning/v1.34/tools/capture_provenance.py (two additive optional flags + two new small functions + 6 new selftest legs)
    - .planning/STATE.md (SAFETY line hand-edited)

key-decisions:
  - "capture_provenance.py needed two minimal additive seams, not one, discovered live rather
     than assumed from the plan text: --board-probe-json (skip the tool's internal
     probe_board.py re-probe, consuming an already-obtained JSON instead) fixes the measured
     avr109-exit/USB-re-enumeration race between the tool's own internal board-signature and
     hw probes; --no-image-plan (explicit not-measured placeholder for the three image_* fields)
     fixes a second, independent, non-hardware blocker -- bench/IMAGE-PLAN.json has no row for
     either bring-up cell and never will, since neither ever generates a chip image."
  - "The Caterina '~8s window' figure governs only the bootloader phase, not the whole chain.
     Measured: a hw call landing at 9.223s from touch onset still succeeded, because avrdude's
     own avr109-session exit (from the board-signature probe) had already reset the MCU into
     the application well before that -- the relevant constraint past that point is a ~2s
     settle for USB re-enumeration, not the bootloader's inactivity timer."
  - "Rev 2.2 (fitted for the Leonardo pre-proof) is documented as a carrier only -- its ADC/hw
     readings are explicitly non-authoritative for shield identity (standing bench rule 6) and
     are not treated as a SHIELD-04 result; A3/B2 will run with Rev 2.0, not Rev 2.2."

requirements-completed: []  # This plan de-risks BOARD-02/BOARD-03; it closes neither (no sweep position produced, per plan's own instruction)

coverage:
  - id: D1
    description: "D-10 pre-proof: v1.33 arm flashed to an ATmega328PB and independently read back to a judged match against the v133 arm's own 23000-byte span, both vector exclusions applied, raw-span SHAs never compared"
    verification:
      - kind: manual_procedural
        ref: "judge_readback.py --target uno328pb --flashed-arm v133 --expect-arm v133: judged_match=true, judged_span_bytes=23000, vector_exclusions_applied has both entries (offset 0, offset 100)"
        status: pass
    human_judgment: false
  - id: D2
    description: "A3/B2's P-02 has an evidence-backed, copy-runnable command sequence for a Leonardo/Caterina target, and capture_provenance.py is known to complete on a Leonardo (with the two seams this plan added)"
    verification:
      - kind: manual_procedural
        ref: "capture_provenance.py --board-probe-json ... --no-image-plan --pending-readback completed rc=0 on the live Leonardo; provenance_BRINGUP-leonardo-provenance.json has captured_at_step=2, target_env=leonardo, arm=v133, non-null board_signature=0x1e9587"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both pre-proofs recorded as bring-up cells with no EVIDENCE.jsonl row; run_gates.sh stays 12/12 tool selftests + 5/5 live gates after capture_provenance.py's changes"
    verification:
      - kind: unit
        ref: "python3 .planning/v1.34/tools/capture_provenance.py --selftest (31/31 legs, exit 0)"
        status: pass
      - kind: unit
        ref: "bash .planning/v1.34/tools/run_gates.sh (12/12 selftests, 5/5 live gates, exit 0, captured directly)"
        status: pass
    human_judgment: false

# Metrics
duration: ~34min (executor wall-clock; excludes two operator checkpoint wait intervals)
completed: 2026-08-27
status: complete
---

# Phase 161 Plan 02: Two Bring-Up Pre-Proofs — D-10 (uno328pb) + A3/B2 P-02 (Leonardo) Summary

**Closed the D-10 gap (first-ever v1.33-arm judged flash/read-back match on an ATmega328PB, 23000 B, both vector exclusions applied) and established the measured, copy-runnable A3/B2 `P-02` sequence for the Leonardo/Caterina target, adding two minimal additive seams to `capture_provenance.py` after discovering — live, not from the plan text — that its own two internal device probes race avrdude's avr109-exit reset.**

## Performance

- **Duration:** ~34 min executor wall-clock (12:33–13:07 UTC), across two operator checkpoints
- **Completed:** 2026-08-27T13:06:51Z
- **Tasks:** 5 (2 operator checkpoints, 3 automated)
- **Files modified:** 2 code/doc files (`capture_provenance.py`, `STATE.md`), plus 2 new bench-cell directories (~55 new files)

## Accomplishments

- **D-10 pre-proof (uno328pb):** flashed the v1.33 firmware arm to a bare ATmega328PB (no shield, no chip — operator-confirmed) via `pio run -t upload -e uno328pb` from `/workspaces/firestarter`, then proved it with `judge_readback.py`: `judged_match=true`, `judged_span_bytes=23000` (the v133 arm's own span, never the control-arm 26074, never the legacy flat scalar), both vector exclusions applied unchanged from their control-arm-derived offsets (no `rig-pins.json` change needed). The two raw-span SHAs (`sha_actual_judged`/`sha_expected_judged`) were recorded but never compared, per the pre-proof's own load-bearing prohibition.
- **A3/B2 `P-02` pre-proof (Leonardo):** reproduced the predicted failure exactly (`probe_board.py` and `capture_provenance.py`'s internal board-signature probe both refuse against application firmware, rc=1, ~6s, no `avr109` handshake), then discovered a **second, previously-unrecorded failure mode**: `capture_provenance.py`'s own internal board-signature probe, immediately followed by its own internal `hw` probe, races avrdude's `avr109` session exit — the exit resets the Leonardo into the application, causing a brief USB re-enumeration that the very next serial open can land inside of (measured: rc=1 at 4.644s from touch onset, port `ENOENT`, confirmed by the node's mtime advancing). Isolated and measured the fix: a **~2s settle** between the internal board probe and the `hw` call. Also discovered a **third, independent, non-hardware blocker**: `bench/IMAGE-PLAN.json` has no row for either bring-up position and never will (neither generates a chip image), and `capture_provenance.py` resolves that lookup unconditionally regardless of `--pending-readback` or timing.
- **Two additive seams added to `capture_provenance.py`:** `--board-probe-json PATH` (consume an already-obtained `probe_board.py` result, skipping the internal re-probe) and `--no-image-plan` (explicit not-measured placeholder for a position with no `bench/IMAGE-PLAN.json` row). Both extracted as small, independently-testable functions (`resolve_board_signature_from_json`, `build_no_image_plan_reason`) with 6 new `--selftest` legs (31/31 total, exit 0). The default (both flags omitted) code path is byte-identical to before — confirmed via `git diff`'s `else` branches.
- **`capture_provenance.py` completed end-to-end on a Leonardo for the first time**, using the seams: `touch_1200.py` (bare settle-only mode, no `--wait-new-port`) → `probe_board.py` → 2s sleep → `capture_provenance.py --board-probe-json ... --no-image-plan --pending-readback`, rc=0, `board_signature=0x1e9587`, `shield_rev_declared="Rev 2.2"`.
- **`run_gates.sh` re-confirmed at 12/12 tool selftests + 5/5 live gates, exit 0**, captured directly, after the `capture_provenance.py` changes.
- **Both pre-proofs recorded as bring-up cells with no `EVIDENCE.jsonl` row** — `EVIDENCE.jsonl` confirmed byte-unchanged since Phase 160 Plan 12 (5 lines, 4 pre-existing bring-up rows, none added by this plan) — with the reasoning (`BRINGUP-` prefix, no `WRV-VERDICT.json` ever produced, `append_evidence.py` structurally refuses without one) written into both `PREPROOF.md` files.
- **`~/.firestarter` re-verified unchanged from the Amendment 3 baseline** (all four pinned values match exactly) and `check_arms.py --expect-config-sha` re-confirmed the frozen `FIRESTARTER_CONFIG_DIR` SHA, with both assertions genuinely exercised (every invocation this plan made set `FIRESTARTER_CONFIG_DIR` inline, per standing bench rule 9).

## Task Commits

Each task was committed atomically:

1. **Task 1: P-01 mount bare uno328pb, report node** - checkpoint only, no code commit (operator confirmed "uno328pb is on ttyUSB0"; the STALE STATE.md `ttyACM0` Uno attribution the checkpoint had quoted was corrected out-of-band by the orchestrator, `0e8ac6fb`)
2. **Task 2: D-10 pre-proof — flash v1.33 to uno328pb, judge read-back** - `e2c3b348` (feat)
3. **Task 3: P-01 mount Leonardo + Rev 2.2 shield, declare** - checkpoint only, no code commit (operator: "Leonardo, rev 2.2, socket empty" — declaration recorded verbatim in `PREPROOF.md`; a genuine deviation from the checkpoint script was also recorded — the uno328pb was never unplugged)
4. **Task 4: Leonardo P-02 pre-proof — capture_provenance.py seams + working sequence** - `06f4198a` (feat)
5. **Task 5: record pre-proof outcomes, hand bench to A1** - `f79a7ac6` (docs)

**Plan metadata:** _pending — this SUMMARY's own commit_

## Files Created/Modified

- `.planning/v1.34/bench/cells/BRINGUP-uno328pb-v133/` — `READBACK-VERDICT.json` (judged_match=true, judged_span_bytes=23000), `board_probe.json` (atmega328pb, 0x1e9516), `flash_readback.bin` (32768 B), `expected_span.bin`/`judged_span.bin` (23000 B), `SHA256SUMS.txt`, `PREPROOF.md`, `logs/` (4 invocation pairs)
- `.planning/v1.34/bench/cells/BRINGUP-leonardo-provenance/` — `provenance_BRINGUP-leonardo-provenance.json` (the completed record), `board_probe.json` (atmega32u4, 0x1e9587), `touch.json`/`touch_attempt2.json`/`touch_attempt3.json` (the three measurement cycles), `check_arms_teardown.json`, `PREPROOF.md` (364 lines: declaration, deviation note, the full measured attempt sequence, the working prescription), `logs/` (7 invocation groups)
- `.planning/v1.34/tools/capture_provenance.py` — added `--board-probe-json`/`--no-image-plan` argparse flags, `resolve_board_signature_from_json()`, `build_no_image_plan_reason()`, 6 new `--selftest` legs; default code paths unchanged (additive only, confirmed via diff)
- `.planning/STATE.md` — SAFETY line hand-edited: chipped Uno now disconnected (off the bus, confirmed by descriptor absence), Leonardo (Rev 2.2 carrier) and uno328pb (v1.33 flashed, judged) both bare and attached, next-step pointer updated to plan 161-03/A1

## Decisions Made

- **`capture_provenance.py` needed two seams, not the one the plan anticipated.** The plan's own text predicted only a timing-related seam ("can `capture_provenance.py` consume those two already-obtained results, or does it need a seam?"). Live measurement surfaced a second, independent, non-hardware blocker (the unconditional `bench/IMAGE-PLAN.json` lookup) that would have failed this position regardless of timing. Both were fixed with the smallest additive change each required, keeping the default path for every real sweep position untouched.
- **The Caterina "~8s window" is a bootloader-phase-only constraint, not a whole-chain budget.** Measured directly: a successful `hw` call landed at 9.223s from touch onset — past the nominal figure — because the relevant timer (Caterina's own inactivity timeout) was already moot by then; the MCU had reset into the application seconds earlier. The actual constraint discovered is a ~2s USB re-enumeration settle between the tool's two internal device-touching probes, which is a different, previously-unmeasured concern from the touch-to-bootloader-probe window BRINGUP-leonardo (Phase 160 Plan 10) had already measured.
- **Rev 2.2 (this plan's Leonardo carrier) is explicitly non-transferable to A3/B2's shield-identity result.** A3/B2 will fit Rev 2.0. Both `PREPROOF.md` files and the SUMMARY state this so a later reader does not mistake this pre-proof's ADC/`hw` readings for a SHIELD-04 datum.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug, discovered live] `capture_provenance.py`'s two internal device probes race avrdude's avr109-exit reset on a Caterina target**
- **Found during:** Task 4, Attempt 2 (touch → immediate `capture_provenance.py` invocation, no settle)
- **Issue:** `probe_board_signature()`'s `avr109` session ends with avrdude's own "leave prog mode"/"exit bootloader" exchange, which resets the ATmega32U4 into the application immediately — causing a brief USB re-enumeration. The tool's very next internal call, `probe_controller_string()` (`hw`), can land while that re-enumeration is in flight, producing port `ENOENT` (measured: rc=1 at 4.644s from touch onset; node mtime confirmed advancing).
- **Fix:** Added `--board-probe-json PATH`, letting the caller run `probe_board.py` externally, insert a measured ~2s settle, then invoke `capture_provenance.py` with its internal re-probe skipped — its first live-port action is then the (now-safe) `hw` call.
- **Files modified:** `.planning/v1.34/tools/capture_provenance.py`
- **Verification:** `--selftest` (3 new legs for `resolve_board_signature_from_json`) + a live end-to-end run on the actual Leonardo, rc=0.
- **Committed in:** `06f4198a` (Task 4 commit)

**2. [Rule 1/3 - Blocking, discovered live] `capture_provenance.py` unconditionally requires a `bench/IMAGE-PLAN.json` row that this bring-up position will never have**
- **Found during:** Task 4, isolated check of `resolve_image_plan_fields('BRINGUP-leonardo-provenance', ...)` before designing the seam
- **Issue:** Neither of this plan's two pre-proof cells generates a chip image (no chip write ever runs), so neither has, or ever will have, an `IMAGE-PLAN.json` row — a permanent condition, unlike `--pending-readback`'s temporarily-pending semantics. The lookup runs unconditionally in `main()`, independent of `--pending-readback` or hardware timing, and hard-refuses on a missing row.
- **Fix:** Added `--no-image-plan`, writing the three `image_*` fields as an explicit `"not measured — <reason>"` placeholder naming the position id and the reason, per the project's anti-fabrication recording discipline. Default (flag omitted) unchanged — every real sweep/chip-write position keeps the hard refusal.
- **Files modified:** `.planning/v1.34/tools/capture_provenance.py`
- **Verification:** `--selftest` (2 new legs for `build_no_image_plan_reason`) + the live end-to-end run.
- **Committed in:** `06f4198a` (Task 4 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1/3, both discovered live rather than anticipated by the plan text; both are additive `capture_provenance.py` seams gated by `run_gates.sh` at 12/12 + 5/5 after the change).
**Impact on plan:** No scope creep — both fixes are exactly the "possible new tool seam (only if measured necessary)" the plan's own frontmatter anticipated, scoped to the smallest change each required, with the default code path for every real sweep position left byte-identical.

## Issues Encountered

- **Task 3's checkpoint script was not followed literally by the operator** — the uno328pb was never unplugged before the Leonardo was fitted with its shield; the operator fitted Rev 2.2 to the already-attached Leonardo in place. This left two live serial nodes (`/dev/ttyACM0` Leonardo, `/dev/ttyUSB0` uno328pb) present throughout Task 4. Not a blocker: every avrdude/probe/`capture_provenance.py` invocation in this plan already passed an explicit `--port`, so autodetection was never at risk. Recorded verbatim in `BRINGUP-leonardo-provenance/PREPROOF.md` as a genuine deviation, not papered over.
- **`STATE.md`'s SAFETY line was stale at Task 1's checkpoint dispatch** — it named `/dev/ttyACM0` as the chipped Uno's node, but sysfs descriptors showed the nodes had shuffled (`ttyACM0` was actually the Leonardo, `ttyACM1` the Uno). The orchestrator corrected this out-of-band before Task 2 (`0e8ac6fb`) and instructed that no node in this plan be re-derived from `STATE.md` prose — every node used below was re-enumerated and identity-checked by descriptor or avrdude signature instead.

## Known Stubs

None. Both `READBACK-VERDICT.json` and `provenance_BRINGUP-leonardo-provenance.json` carry either real measured values or an explicit `"not measured — <reason>"` placeholder for every field — no blank or fabricated value anywhere in either record.

## Threat Flags

None beyond the plan's own `<threat_model>` (T-161-06..10, T-161-SC), all of which this plan's execution satisfies as designed: port identity was re-enumerated and signature-checked at every swap (T-161-06); the correct firmware arm was asserted before flashing, with an independent `judge_readback.py` proof, never avrdude's own verify pass (T-161-07); `judged_match` plus a runtime `hex_span_expected_by_arm` lookup was the sole verdict criterion, never a raw-SHA comparison (T-161-08); both `capture_provenance.py` seams are additive-only with their own selftest legs and a full `run_gates.sh` re-run at 12/12+5/5 (T-161-09); no chip was ever seated in this plan, so no chip-destructive path was reachable (T-161-10).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Plan 161-03 (cell A1)** inherits: the chipped Uno (Rev 2.0 shield, W27C512 seated, v1.33 arm flashed, pot at 12.0V) sitting **disconnected** on the bench, confirmed off the bus by descriptor absence. A1's own `P-01` must reconnect it and remove the chip as part of that same handover, because A1's `P-02` runs an avrdude signature probe and the Uno-class chip-out rule covers signature probes, not only writes.
- **Plan 161-04 (cell A2)** inherits: `BRINGUP-uno328pb-v133/READBACK-VERDICT.json` as a proven, in-hand v1.33-arm flash/read-back result on this exact MCU — a read-back mismatch at A2 is no longer a first-attempt unknown; it is now interpretable against a known-good prior result.
- **Plan 161-05 (cell A3/B2)** inherits: `BRINGUP-leonardo-provenance/PREPROOF.md`'s measured, copy-runnable `P-02` command sequence (`touch_1200.py` → `probe_board.py` → 2s settle → `capture_provenance.py --board-probe-json ...`), and the two `capture_provenance.py` seams already landed and gated. `--no-image-plan` is explicitly **not** part of A3/B2's own prescription (every real sweep position has an `IMAGE-PLAN.json` row); `--board-probe-json` and the 2s settle are.
- Neither pre-proof cell added an `EVIDENCE.jsonl` row or marked any `BOARD-0N` requirement complete, per this plan's own instruction — both remain open for their respective sweep cells.
- Both sub-repos (`firestarter/`, `firestarter_app/`) confirmed byte-unchanged (`git status --porcelain` empty) throughout, verified again at Task 5's teardown.

---
*Phase: 161-board-board-sweep-three-boards-on-rev-2-0*
*Completed: 2026-08-27*

## Self-Check: PASSED

All claimed files verified present on disk; all claimed commit hashes (`e2c3b348`, `06f4198a`, `f79a7ac6`, `0e8ac6fb`) verified in `git log --oneline --all`.
