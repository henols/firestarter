---
phase: 98
reviewers: [claude]
reviewed_at: 2026-06-30T13:42:43Z
plans_reviewed: [98-01-PLAN.md, 98-02-PLAN.md]
reviewer_note: >-
  Only the `claude` CLI was available on this devcontainer, and the session runs
  inside Claude Code. Per operator decision, the claude CLI was invoked anyway as a
  fresh, separate-context reviewer. This is a fresh-context pass within the same model
  family — NOT a true cross-vendor independent review. Weight findings accordingly.
---

# Cross-AI Plan Review — Phase 98

> ⚠ **Single-reviewer review.** No independent external (cross-vendor) AI CLI was
> available — only `claude`, run as a fresh separate session. There is no consensus
> to triangulate; treat the findings below as one fresh-context perspective, not
> multi-model agreement.

## Claude Review

# Cross-AI Plan Review — Phase 98: FIX the 0x08 32-Pin Write/VPP Path

## 1. Summary

These are competent, disciplined plans that faithfully execute the locked decisions (D-01..D-06): clean host→firmware wave ordering, a correctly size-keyed D-04 alias guard, strong golden-trace revert discipline, and honest framing of the "blind fix" residual. The execution risk is low — they will almost certainly produce green tests and a clean diff. **The deeper risk is that the fix, by the project's own evidence, is a physical no-op at the failing address (0x000000), so the Phase-99 bench is set up to fail-as-predicted while Phase 98 ships well-tested but inert changes.** The RCA's central conclusion (RC-1) rests on code analysis with the one decisive physical measurement (pin-1/pin-31 DMM) never actually taken, and the plans build the entire fix on top of that unmeasured link. The plans are honest about not over-claiming, but they under-state how strongly the analysis predicts "still 0 bits" on silicon.

## 2. Strengths

- **Dependency ordering is correct and explicit.** Host pinout (Plan 01) defines the bus-config shape that the firmware branch + tests (Plan 02) consume; `depends_on: ["98-01"]` and the SUMMARY-as-contract handoff are sound.
- **D-04 alias guard is genuinely defense-in-depth.** Host structural scoping (`proto_id==0x08 && mem_size<=262144` → `DIP32_27C020`) *plus* the firmware `mem_size<=262144` belt is the right model, and the `mem_size<=262144 ⟺ A18-unused` reasoning is datasheet-sound for the AMD 27C-series (256K = A0–A17; A18 lands on pin 31 only at ≥512K).
- **Golden-trace revert discipline (Plan 02 Task 3) is precise.** It correctly anticipates Pitfall 2 (bless re-pins all four `.inc` files) and gates on `git diff --exit-code` for 0x07/0x0B/chip-id. The mandatory mismatch/failure-case test (P89 CR-01 lesson) is correctly carried.
- **Q1/Q2 resolution is rigorous** — ruling out `static-high-pins` (HIGH ≠ PGM=VIL, no inversion in the latch path) and confirming no new wire field is needed is well-evidenced and keeps the lockstep blast radius at zero.
- **Honest about the Phase-99 residual** — both plans explicitly forbid over-claiming that bits will flip on silicon.

## 3. Concerns

- **[HIGH] The fix is a physical no-op at address 0 by the research's own analysis.** Pre-fix, pin 31 = line 22 = CONTROL bit 6, and *at addr 0 line 22 is already cleared → pin 31 is already at VIL* (the program-active level), yet 0 bits program. Post-fix, the firmware "deliberately holds line 22 LOW." Same physical result: LOW. For the failing address the new code produces byte-identical register state to the old code (this is exactly why A5 anticipates the 0x08 golden trace *won't change*). A fix that holds a pin at the level it already sits at cannot flip the symptom. The plans treat this as "residual to close at Phase 99," but it is closer to a *prediction of Phase-99 failure*. This should be surfaced as the dominant risk, not a footnote.
- **[HIGH] The RC-1 verdict rests on an unmeasured link, and a measurement path existed.** Per 97-RCA-FINDINGS, RC-2 (VPP/P1 routing) was exonerated *by code only* — pin-1 and pin-31 DMM were tooling-blocked. But a workaround (`hold_rail.py`, port held open) is documented in memory/the debug doc. Spending the blind belt-and-suspenders fix before taking the one measurement that would distinguish RC-1 from RC-2/RC-5 is a process gap. If the real cause is RC-2 level/routing or silicon, none of Phase 98 touches it.
- **[HIGH] The TDD RED state in Plan 02 may be unsatisfiable honestly.** Plan 02 Task 1 requires Test A (corrected-path) to be RED pre-fix, asserting "line 22 held at program-active LOW." But with the `DIP32_27C020` bus-config (pin 31 off the bus) and addr 0, line 22 is *already* LOW pre-fix. The test can only go RED by checking for an *implementation artifact the fix uniquely emits* (e.g., an extra explicit CONTROL-register write before `chip_enable`) rather than a behavioral/physical difference. That makes the RED→GREEN cycle verify code shape, not silicon behavior — circular with the "blind fix" caveat and weak assurance for a hardware fix. The plan doesn't acknowledge this tension.
- **[MEDIUM] Unbounded blast radius of the host pinout reassignment.** The size-keyed arm reassigns *every* ≤256K 0x08 32-pin chip (all 128K + 256K parts among the 127 on 0x08/DIP32_STD) to `DIP32_27C020` + the firmware PGM branch — not just AM27C020. Plan 01 Task 2's `diff_db` verification only spot-checks three named parts (AM27C020/AM27C040/AM27C080). There is no enumeration or per-chip datasheet check that pin 31 is genuinely PGM (vs. some other role) on *each* reassigned non-AMD part. A vendor whose ≤256K 0x08 part uses pin 31 differently would be silently mis-mapped, and the firmware hold-LOW applied to it.
- **[MEDIUM] Possible regression of a currently-working ≤256K 0x08 chip with no coverage.** Golden traces cover only 0x07/0x08/0x0B representatives. If any other ≤256K 0x08 32-pin chip writes correctly today (pin-31-as-address happening to work), removing pin 31 from its bus + firmware hold-LOW would break it, and neither `check_dispatch` nor the golden guard would catch a structurally-valid behavioral change.
- **[MEDIUM] The "per-byte CE pulse P1-hold" extension appears already covered.** Research states P1 is held across the *entire* `program_mismatched_bytes` buffer loop, which strictly encompasses every per-byte CE pulse. Extending it "to the per-byte pulse" is likely a literal no-op. This is a locked D-01 "suspenders," but it adds shared-program-pulse churn (raising regression risk) for an inert change.
- **[LOW] SAFE-02 cannot be locally proven this phase.** No py3.11 binary in the devcontainer; the plan correctly allows "mark CI-pending." Acceptable, but it means a stated success criterion closes unverified locally and depends entirely on CI.
- **[LOW] The diff gate is self-referential within Plan 01.** Re-baselining `chip_database.baseline.json` in the same plan/commit that introduces the DB change makes `diff_db` green by construction; the real review surface becomes the git diff of the baseline file itself. Standard for this repo, but worth an explicit reviewer callout.

## 4. Suggestions

- **Before executing the blind fix, take the DMM measurement that was tooling-blocked.** Use the documented `hold_rail.py` (port-held-open) workaround to read pin 1 and pin 31 during a held program window. If pin 31 is already VIL and pin 1 is genuinely ≥12.5V at the socket, that *confirms the fix will be inert* and redirects the milestone toward RC-2-level / silicon / a not-yet-considered cause — saving a wasted bench trip.
- **State the predicted Phase-99 outcome explicitly in both SUMMARYs.** "Under RC-1, addr-0 register state is unchanged by this fix; if Phase 99 still shows 0 bits at addr 0, that is consistent with the analysis, not a new failure." This protects against mis-reading a predicted null result as a fresh bug.
- **Make Test A assert a behavioral discriminator, not an artifact.** If the only RED-able signal is an extra register write, say so plainly and label the test as verifying *code structure (deliberate PGM assert exists)*, decoupled from any silicon claim. Add an explicit note that a green Test A does **not** imply bits will flip.
- **Enumerate every chip that flips to `DIP32_27C020`** in Plan 01 Task 2 (not just the 3 named parts) and record the count + a per-chip pin-31-role spot-check in the SUMMARY. Add a `diff_db` assertion on the *total number* of reassigned rows so an unexpectedly large blast radius trips the gate.
- **Consider scoping `DIP32_27C020` to AM27C020 (and explicitly-verified siblings) only**, rather than the whole ≤256K class, until each additional part's pin-31 role is datasheet-confirmed. This contains the regression surface to the one chip the RCA actually studied.
- **Add a regression assertion for an unrelated ≤256K 0x08 chip** if one exists in the golden set, so the pinout reassignment's effect on non-AM27C020 parts is observable.

## 5. Risk Assessment

**Overall risk: MEDIUM–HIGH.**

*Execution* risk is LOW — the plans are well-structured, the waves are correctly ordered, the D-04 guard is sound, and the test/trace discipline is strong; they will almost certainly land green. The elevated rating comes from *goal* risk: the project's own evidence indicates this fix does not change the physical signal at the failing address, so the milestone's actual objective (bits flip on real silicon) is at serious risk, and the central RCA conclusion stands on a physical measurement that was never taken despite an available workaround. There is also a real-but-bounded regression surface (the whole ≤256K 0x08 class reassigned with only three parts spot-checked). The plans are intellectually honest about the residual, which mitigates the blast radius — but they should treat "inert at addr 0" as the headline expected outcome and take the deferred DMM measurement before, not after, spending the blind fix and a bench trip.

---

## Consensus Summary

*Only one reviewer (claude, fresh-context) participated — no cross-reviewer consensus is available.* The single review's highest-priority signal, carried forward verbatim for the planner:

### Agreed Strengths
- Correct, explicit host→firmware wave ordering (`98-01` → `98-02`).
- D-04 alias guard is genuine defense-in-depth (host structural scope + firmware `mem_size<=262144` belt), datasheet-sound for the AMD 27C series.
- Golden-trace revert discipline (Plan 02 Task 3) precisely anticipates the bless-re-pins-all-four-`.inc` pitfall and carries the P89 CR-01 mismatch-test lesson.

### Agreed Concerns (highest priority)
- **[HIGH] The fix may be a physical no-op at address 0.** Pre-fix, pin 31 (line 22 / CONTROL bit 6) is *already* at VIL at addr 0, yet 0 bits program. Post-fix deliberately holds the same line LOW — byte-identical register state at the failing address. A pin held at the level it already sits at cannot flip the symptom. This should be the headline expected outcome, not a Phase-99 footnote.
- **[HIGH] RC-1 rests on an unmeasured link.** The decisive pin-1/pin-31 DMM measurement was never taken (tooling-blocked), but a `hold_rail.py` port-held-open workaround is documented. The blind belt-and-suspenders fix is being spent before the one measurement that would distinguish RC-1 from RC-2/RC-5/silicon.
- **[HIGH] TDD RED state in Plan 02 may be unsatisfiable honestly.** With `DIP32_27C020` (pin 31 off the bus) at addr 0, line 22 is already LOW pre-fix; Test A can only go RED against an implementation artifact (an extra explicit CONTROL write), verifying code shape rather than physical behavior.
- **[MEDIUM] Unbounded blast radius** of the size-keyed host pinout reassignment — *every* ≤256K 0x08 32-pin part flips to `DIP32_27C020` + firmware hold-LOW, but `diff_db` only spot-checks 3 named AMD parts. No per-chip pin-31-role check for the other reassigned non-AMD parts.
- **[MEDIUM] The per-byte CE-pulse P1-hold extension is likely an inert no-op** (P1 is already held across the entire mismatched-bytes loop) yet adds shared-program-pulse churn / regression surface.

### Divergent Views
- N/A — single reviewer.

### Suggested actions before / during execution
1. Take the tooling-blocked DMM measurement (pin 1 ≥12.5V? pin 31 already VIL?) via `hold_rail.py` *before* spending the blind fix — it could confirm the fix is inert and redirect the milestone.
2. State the predicted Phase-99 outcome explicitly in both plan SUMMARYs ("addr-0 register state unchanged by this fix; still-0-bits is consistent with RC-1, not a new bug").
3. Enumerate *every* chip that flips to `DIP32_27C020` (not just 3) and add a `diff_db` assertion on the total reassigned-row count to trip on an unexpectedly large blast radius. Consider scoping `DIP32_27C020` to AM27C020 + datasheet-verified siblings only.
4. Label Test A as verifying code structure (deliberate PGM assert exists), decoupled from any silicon claim.
