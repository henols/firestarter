---
phase: 161-board-board-sweep-three-boards-on-rev-2-0
verified: 2026-08-27T19:01:00Z
status: passed
score: 11/11 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 161: Board Sweep, Three Boards on Rev 2.0 — Verification Report

**Phase Goal:** Cells A1 (Uno), A2 (uno328pb) and A3/B2 (Leonardo) on the Rev 2.0 shield, each
control arm first then v1.33 arm, each arm against W27C512 and W29C020 — 12 evidence positions
with measured write durations. A2's program failure is **captured on both arms**, not assumed
from Backlog 999.2. A3/B2 is executed here, once, for both sweeps.

**Verified:** 2026-08-27T19:01:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Twelve unique sweep positions exist in EVIDENCE.jsonl (4 per cell x 3 cells), none blank/inferred | ✓ VERIFIED | `EVIDENCE.jsonl` has 17 lines: 1 `_schema` header + 16 rows. 16 rows = 12 sweep rows (`A1__*`, `A2__*`, `A3-B2__*`, each x4) + 4 non-sweep `BRINGUP-*` rows. `position_id` set is 16/16 unique, no duplicates. |
| 2 | Every one of the 12 positions carries a measured write duration, including the 4 that failed | ✓ VERIFIED | All 12 rows have non-null `write_duration_wallclock_s` (A2's four: 15.813 / 4.019 / 10.245 / 14.288 s). `write_duration_app_reported_s` is `"not measured — <reason>"` on the 4 A2 rows (the write never reached a success line) — the correct `not_measured` convention, not a blank. |
| 3 | A2's four failures are observed with symptom, not assumed from Backlog 999.2 | ✓ VERIFIED | Each A2 row's `verdict`/`anomalies` opens "Observed, not asserted" and states where the MAIN phase stopped and the host's exact printed text (e.g. `"Communication error during WRITE: Timeout... /dev/ttyUSB0"`, firmware `"ERROR: Timeout verifying 0x15 at 0x00007f (got 0x13)"`, chip-ID mismatch `0x303` then a firmware pulse-convergence diagnosis, and a bare connect-level timeout before INIT). All four mechanisms are distinct and named. Backlog 999.2 is cited only as prior art alongside the observation, never in place of it. All four were genuinely attempted (full command sequences and read-backs recorded), none skipped for being expected to fail. |
| 4 | A3/B2 executed exactly once, four rows (one per arm x chip) | ✓ VERIFIED | Exactly 4 rows carry `cell_id == "A3/B2"` (`position_id` prefix `A3-B2__`), one per (control/v133 x w27c512/w29c020). No second row for any A3/B2 position anywhere in the 16-row file. |
| 5 | `captured_at_step == 2` on all 12 sweep-position provenance JSONs | ✓ VERIFIED | Checked all 12 `provenance_*.json` files under `bench/cells/A1/`, `A2/`, `A3-B2/` directly — every one reports `captured_at_step: 2`. |
| 6 | Verdicts come from the judged SHA oracle, not app exit code or avrdude verify | ✓ VERIFIED | All 12 `WRV-VERDICT_*.json` files carry `sha_verdict_judged` as the recorded verdict field, distinct from `app_verdict_unjudged` — and the two visibly diverge on 3 of A2's 4 positions (e.g. `A2__control__w27c512`: `app_verdict_unjudged=0` but `sha_verdict_judged=mismatch`), proving the SHA judge is the actual oracle, not a restatement of the app's own exit code. |
| 7 | Arm-correct spans used per target, vector-exclusion vs hex-extent policy respected | ✓ VERIFIED | `rig-pins.json` values match exactly: uno control 26026/v133 22952 (`hex-extent`), uno328pb control 26074/v133 23000 (`vector-exclusion`), leonardo control 28170/v133 25098 (`hex-extent`). `EVIDENCE.jsonl`'s `fw_readback_judged_span_bytes` matches these per row. A2/`CELL.md` explicitly reads `hex_span_expected_by_arm.control`/`.v133` at assertion time and uses `judged_match` (never raw-SHA equality) on uno328pb, correctly not flagging the expected raw-span SHA inequality as a defect. |
| 8 | Committed-on-failure policy honored: A1 0 tracked, A2 11 tracked, A3/B2 0 tracked | ✓ VERIFIED | `git ls-files` filtered to `cells/*/reads/*.bin` and `cells/*/written.bin` (the exact `.gitignore`-exempted paths) returns 0 for A1, 11 for A2 (run_01/02/03 + written.bin across 4 positions, with an extra `attempt1_run_01.bin` for the re-seated position), 0 for A3-B2 — exactly the expected pattern. |
| 9 | No product code touched; firestarter gitlink at v1.33 `5759dc8d` | ✓ VERIFIED | `git -C firestarter status --porcelain` and `git -C firestarter_app status --porcelain` both empty. `git submodule status` shows firestarter pinned at `5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463` (v1.23-164-g5759dc8), matching the phase's stated control gitlink. |
| 10 | Gate suite green: 12/12 selftests, 5/5 live gates, exit 0, read directly (not piped) | ✓ VERIFIED | Ran `bash .planning/v1.34/tools/run_gates.sh > logfile 2>&1; echo $?` — captured exit code directly, not through a pipe. Output: `tool self-tests run: 12 / 12`, all 5 live gates (`check_rebuild.py`, `check_arms.py`, `render_steps.py`, `render_evidence.py --check`, `gate_record.py`) PASS, `ALL GATES PASSED`, exit code 0. |
| 11 | D-11 leave-state recorded accurately: Leonardo, Rev 2.0, v1.33 arm, W27C512 seated, VPP in-band | ✓ VERIFIED | `A3-B2/CELL.md`'s P-11 leave-state and `STATE.md`'s SAFETY line both state: Leonardo connected `/dev/ttyACM0`, Rev 2.0 mounted, v1.33 arm (fw `5759dc8d`), W27C512 seated, pot untouched since P-06 (firmware 12.3 V / meter 11.44 V, in band per `eprom.cpp:713`/`:736`). Explicitly the only cell of the three ending with a chip seated. |

**Score:** 11/11 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `bench/EVIDENCE.jsonl` | 12 sweep rows + prior bring-up rows, no dupes | ✓ VERIFIED | 16 non-schema rows, all unique `position_id` |
| `bench/cells/A1/{CELL.md,provenance_*.json x4,WRV-VERDICT_*.json x4}` | full A1 cell record | ✓ VERIFIED | All present, all 4 positions `validated`, `match` |
| `bench/cells/A2/{CELL.md,provenance_*.json x4,WRV-VERDICT_*.json x4}` | full A2 cell record | ✓ VERIFIED | All present, all 4 positions `skipped-with-reason` with named, observed failure |
| `bench/cells/A3-B2/{CELL.md,provenance_*.json x4,WRV-VERDICT_*.json x4}` | full A3/B2 cell record | ✓ VERIFIED | All present, all 4 positions `validated`, `match`, two N=3-stable v1.33 reads |
| `bench/cells/BRINGUP-uno328pb-v133/READBACK-VERDICT.json` | v1.33 328PB pre-proof, judged match | ✓ VERIFIED | `judged_match: true`, `sha_actual_judged` != `sha_expected_judged` by design (vector-exclusion) |
| `bench/cells/BRINGUP-leonardo-provenance/PREPROOF.md` | Leonardo provenance sequence recorded | ✓ VERIFIED | Present with recorded touch/probe attempts and a working sequence |
| `.planning/v1.34/PROCEDURE.md` Amendment 3 | per-position path clauses | ✓ VERIFIED | Amendment 3 clauses (1)-(4) present, cross-referenced from P-07/P-09/P-11 in all three sweep cells |
| `.planning/v1.34/tools/run_gates.sh` | 12/12 + 5/5, exit 0 | ✓ VERIFIED | Run directly, confirmed |

### Key Link Verification

| From | To | Via | Status |
|------|----|----|--------|
| A1 control W29C020 wall-clock (97.937 s) | D-08 derived ceiling for A2/A3-B2 W29C020 | `391.748 s = 4x97.937 s`, cited in A2/A3-B2 verdict prose | ✓ WIRED |
| `BRINGUP-uno328pb-v133/READBACK-VERDICT.json` | A2's second P-04 (v133 flash judge) | v133 span pre-proven before live A2 attempt, cited in A2/CELL.md | ✓ WIRED |
| `BRINGUP-leonardo-provenance/PREPROOF.md` | A3/B2's P-02 | working touch/probe sequence followed, cited in A3-B2/CELL.md | ✓ WIRED |
| Each position's `WRV-VERDICT_<id>.json` | `EVIDENCE.jsonl` row via `append_evidence.py` | 12/12 rows present, `render_evidence.py --check` green | ✓ WIRED |
| A3/B2 leave-state | Phase 162 CHIP-01 precondition | STATE.md SAFETY line and CELL.md P-11 both record it | ✓ WIRED |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| BOARD-01 | 161-03 | Cell A1 completes both arms x both chips, every result recorded | ✓ SATISFIED | 4/4 A1 positions `validated`, clean `match` |
| BOARD-02 | 161-04 | Cell A2 completes both arms x both chips, expected failure captured on both arms | ✓ SATISFIED | 4/4 A2 positions attempted, observed, distinct failure mechanisms recorded |
| BOARD-03 | 161-05 (+161-02 pre-proof) | Cell A3/B2 completes both arms x both chips, comparable to v1.31's reference rig | ✓ SATISFIED | 4/4 A3/B2 positions `validated`, `match`, executed exactly once |
| BOARD-04 | 161-03/04/05 | Each cell records measured write duration per arm | ✓ SATISFIED | All 12 positions carry `write_duration_wallclock_s`; v1.31 0.37 s spread compared honestly, never as a single-figure comparison |

No orphaned requirements: `REQUIREMENTS.md` traceability table maps exactly BOARD-01…04 to Phase 161, all four appear in plan frontmatter `requirements:` fields across 161-01 through 161-05.

### Anti-Patterns Found

None. Scanned all committed `CELL.md`, `EVIDENCE.md`, `EVIDENCE.jsonl`, `WRV-VERDICT_*.json`, and `provenance_*.json` files under `bench/` for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`/stub patterns. One incidental match of the word "placeholder" in `A2/CELL.md` refers to the literal CLI flag name `--pending-readback` (a value, not a debt marker) — not a stub. No debt markers found anywhere in phase-produced artifacts.

### Probe / Gate Execution

| Check | Command | Result | Status |
|-------|---------|--------|--------|
| Full gate suite | `bash .planning/v1.34/tools/run_gates.sh` (exit read directly) | 12/12 selftests, 5/5 live gates, `ALL GATES PASSED`, exit 0 | ✓ PASS |

### Honesty Assessment (adversarial read of claims vs. record)

- **A2 failures:** all four positions open with "Observed, not asserted" and cite Backlog 999.2 only as prior art alongside the direct observation (host stdout/stderr, on-chip read-back bytes, firmware-diagnosed error strings). No position substitutes the backlog citation for an observation. PASS.
- **VPP ADC ratiometric finding:** consistently phrased as "CONSISTENT WITH... not established," explicitly noting three points against one meter cannot separate gain from offset. Never overstated as proven. PASS.
- **Forward supersession of A2's low-VPP hypothesis:** `161-05-SUMMARY.md` explicitly states it revises A2's hypothesis "forward... without editing 161-04-SUMMARY.md," and `git log` on both `161-04-SUMMARY.md` and `bench/cells/A2/CELL.md` confirms neither file was touched after its own original commit — the supersession is genuinely a new record pointing back, not a silent edit. PASS.
- **A2's N=3 instability:** recorded and left UNDETERMINED (escalation blocked by the ADC fault); A3/B2's stable N=3 result on the same chip/arm is explicitly offered "not as its resolution," with the confounding variables (board, VPP rail, calibration) named. PASS.
- **A1's Uno VPP:** `161-05-SUMMARY.md` states plainly "A1's Uno was never meter-checked... does not assert A1 ran low, and does not assert it did not" — stated in both directions as required. PASS.
- **v1.31 0.37 s comparison:** every occurrence (CELL.md, EVIDENCE.md, SUMMARY.md) explicitly labels 0.37 s as a spread across three writes, and explicitly states v1.34 has one write per position so "there is no v1.34 spread to set against it," with the phrase "never... a single v1.34 figure 'compared to 0.37 s'" appearing verbatim. PASS — no overclaim found.
- **Write durations:** stated as individual data points (wall-clock plus app-reported pair), never framed as a spread or statistic beyond what a single measurement supports. PASS.

No overclaim was found in the record. The known/expected items (A2's `skipped-with-reason` outcome domain, the carried Phase 160 `commands: []` sparse-argv limitation, `~/.firestarter/config.json` drift recurrence, A2's escalation left UNRUN, untracked root `package.json`/`package-lock.json`) are all present exactly as flagged as non-gaps in the verification brief and are not counted against the phase.

### Human Verification Required

None. All must-haves were verifiable directly against committed artifacts, JSONL records, and a live gate-suite run.

### Gaps Summary

No gaps found. All 11 observable truths verified directly against the codebase (not SUMMARY.md claims): the 12 evidence positions exist, are unique, and are not inferred; A2's four failures are genuinely observed with distinct symptoms rather than assumed from Backlog 999.2; A3/B2 was executed exactly once; provenance capture step, judged-SHA oracle use, arm-correct span policy, and the committed-on-failure `.gitignore` policy all check out byte-for-byte against the actual files; no product code was touched; the gate suite passes 12/12 + 5/5 with a directly-read exit code of 0; and the leave-state for Phase 162 is recorded accurately. The record's honesty claims (ratiometric VPP finding stated as an inference, forward supersession without silent edits, A1's VPP left genuinely undetermined, the v1.31 timing comparison correctly framed as spread-vs-datapoint) all hold up against direct inspection of the committed files and git history.

---

_Verified: 2026-08-27T19:01:00Z_
_Verifier: Claude (gsd-verifier)_
