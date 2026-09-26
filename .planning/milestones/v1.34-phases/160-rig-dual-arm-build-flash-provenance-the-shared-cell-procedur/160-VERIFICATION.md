---
phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur
verified: 2026-08-27T09:41:38Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 160: RIG — Dual-Arm Build, Flash Provenance & the Shared Cell Procedure Verification Report

**Phase Goal:** Build and name both arms (control fw `8695ee5` / app `6bfa645`; v1.33 = the fw#56 /
app#54 PR heads) for all three AVR targets; make a flash provable by device read-back rather than
by an upload exit code; write the one arm-agnostic per-cell procedure both arms follow; fix the
oracle as full-device read-back SHA equality with N=3 read stability on the v1.33 arm; and make the
per-cell record self-sufficient for a re-run. Nothing on the bench may run before this phase closes.

**Verified:** 2026-08-27T09:41:38Z
**Status:** passed
**Re-verification:** No — initial verification

## Method note

This is a meta-repo phase whose entire deliverable is bench tooling and records under
`.planning/v1.34/`; no product code was touched. Verification was performed by (1) hashing every
committed artifact directly rather than trusting SUMMARY prose, (2) running the phase's own
`run_gates.sh` (11/11 tool self-tests + 5/5 live gates, exit code measured directly — never through
a pipe), (3) reading the actual judge/probe tool source to confirm the oracle logic described in
SUMMARYs is what the code does, and (4) diffing `PHASE-160-GATE.md` across its two committed
revisions to confirm the sign-off did not rewrite the disclosed limits. No avrdude, `pio` upload,
signature probe, or chip read/write/erase was run — all checks were host-side (hashing, gate
scripts, file/JSON inspection) per the phase's own "nothing on the bench may run" constraint. Both
submodules (`firestarter`, `firestarter_app`) were confirmed porcelain-clean at their pre-existing
HEADs (`5759dc8d`, `cb189a9b`), consistent with the phase's claim that firmware source is
byte-unchanged.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Both arms build for all three AVR targets from named source SHAs, each image hashed, rebuild reproduces the hash | ✓ VERIFIED | `images/SHA256SUMS.txt` hashes verified against actual `.hex` bytes (`sha256sum -c` → 6/6 OK); `images/REBUILD-CHECK.json` shows `all_identical: true`, `divergences: []` across all 6 (arm, env) pairs; `BUILD-MANIFEST.json` records `built_at_commit.control = 8695ee5...`, `built_at_commit.v133 = 5759dc8d...` (current `firestarter` submodule HEAD) |
| 2 | Flash confirmed by device read-back, not exit code; the check is proven able to fail (wrong-arm cross-flash detected and recorded) | ✓ VERIFIED | `bench/cells/BRINGUP-{uno,uno328pb,leonardo}/crossflash/READBACK-VERDICT.json` all show `judged_match: false`, `flashed_arm: "v133"` vs `expect_arm: "control"`; `CROSSFLASH.md` differing-byte counts match exactly: uno 22367/26026, uno328pb 22300/26066 (8 B vector-excluded), leonardo 24454/28170; the successful (non-crossflash) verdicts at the cell top level show `judged_match: true` for the correctly-flashed arm |
| 3 | `.planning/v1.34/PROCEDURE.md` exists, arm-agnostic, no step differs between arms; diff of two arms' step lists is empty | ✓ VERIFIED | `PROCEDURE.md` has 11 ordered steps (P-01…P-11) plus H1/H2 halt branches, standing bench rules, and forbidden-invocations table; `diff <(render_steps.py --arm control) <(render_steps.py --arm v133))` against the real file is byte-empty (exit 0); `render_steps.py --selftest` passes its own falsification leg (an `[arm: control]`-annotated fixture produces a non-empty diff) — the gate is proven able to go red |
| 4 | Write→read→verify oracle is full-device SHA equality against the written image (never exit code); v1.33 arm additionally records N=3 reads resolving to one SHA | ✓ VERIFIED | `bench/cells/BRINGUP-wrv/WRV-VERDICT.json`: `written_sha` and all 3 `read_shas` identical, `distinct_read_shas: 1`, `n3_disagreement: false`, `sha_verdict_judged: "match"`; `judge_wrv.py` source confirms judgment is against `written_bytes`'s own SHA, with the app's own 0/1/2 recorded separately as `app_verdict_unjudged` and a `verdict_disagreement` cross-check that never substitutes the app's verdict for the judged one — read `--selftest` also demonstrates a "self-consistent but wrong" case producing `mismatch` + `verdict_disagreement: true` |
| 5 | Per-cell record self-sufficient for a re-run — reconstruction from the record alone matches the prescribed setup, zero fields from session memory | ✓ VERIFIED | `bench/cells/BRINGUP-wrv/RECONSTRUCTION.md` (485 lines) + `RECONSTRUCTION-DIFF.md` (216 lines) record 3 rounds; round 1 found a genuine record insufficiency (fixed at `capture_provenance.py`), round 2 found a genuine prescription ambiguity (fixed via `PROCEDURE.md` Amendment 2), round 3 confirmed both closures; closing statement states "zero values sourced from anywhere but the two inputs" |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.planning/v1.34/images/{SHA256SUMS.txt,BUILD-MANIFEST.json,REBUILD-CHECK.json}` | 6 images, hashes, rebuild proof | ✓ VERIFIED | All present; hashes verified against actual bytes; rebuild all-identical |
| `.planning/v1.34/PROCEDURE.md` | Arm-agnostic 11-step procedure | ✓ VERIFIED | 36 KB, 11 steps + halt branches + 2 amendments, empty-diff gate passes |
| `.planning/v1.34/tools/render_steps.py` | SC#3 empty-diff gate, falsifiable | ✓ VERIFIED | `--selftest` 7/7 legs pass including the falsification leg |
| `.planning/v1.34/tools/judge_readback.py` | Independent read-back judge | ✓ VERIFIED | `--selftest` passes; used live in all 3 cross-flash records |
| `.planning/v1.34/tools/judge_wrv.py` | Full-device SHA judge vs written image | ✓ VERIFIED | `--selftest` passes 7 legs including the Pitfall-6 false-green case; used live in `BRINGUP-wrv` |
| `.planning/v1.34/tools/capture_provenance.py` / `gate_record.py` / `probe_board.py` | Provenance capture, record gate, signature probe | ✓ VERIFIED | All `--selftest` pass; `gate_record.py` enforces field completeness, forbidden flags (`--force`, `-b` non-avrdude), two-state outcome domain |
| `.planning/v1.34/PHASE-160-GATE.md` | Operator sign-off document | ✓ VERIFIED | Status: APPROVED, verbatim operator response recorded; diff against pre-signoff revision shows only header + sign-off section changed (242→256 lines), §1-§7 unchanged |
| `.planning/v1.34/bench/cells/BRINGUP-wrv/{RECONSTRUCTION.md,RECONSTRUCTION-DIFF.md}` | D-17 self-sufficiency proof | ✓ VERIFIED | 3-round reconstruction, 2 real fixes driven, present and read in full |
| `.planning/v1.34/tools/run_gates.sh` | Full gate suite | ✓ VERIFIED | Direct (non-piped) exit code 0; 11/11 tool self-tests + 5/5 live gates pass |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `PROCEDURE.md` step ids | `capture_provenance.py` `captured_at_step` | RIG-02 before-any-test-step ordering | ✓ WIRED | `provenance.json` in `BRINGUP-wrv` carries `captured_at_step`; field-presence enforced by `gate_record.py` |
| `render_steps.py` | SC#3 diff gate | live gate in `run_gates.sh` | ✓ WIRED | `run_gates.sh` output: "live gate PASS: render_steps.py -- diff empty, control=11 v133=11 lines" |
| `judge_wrv.py` | `BRINGUP-wrv/WRV-VERDICT.json` | on-device write→read→verify judgment | ✓ WIRED | Verdict artifact present, judged against `written_sha`, not app exit code |
| `PHASE-160-GATE.md` §6 non-claims | operator sign-off | explicit presentation before approval | ✓ WIRED | Sign-off section states each disclosed limit was "presented... explicitly, not merely disclosed" before the verbatim "Approved" response |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|----------------|--------------|--------|----------|
| RIG-01 | 160-01, 02, 05, 08, 09, 10 | Flash either named arm to any of 3 AVR targets, confirmed by device read-back | ✓ SATISFIED | 6 images built + hashed; read-back judge wired and exercised on all 3 targets; wrong-arm MISMATCH observed on all 3 |
| RIG-02 | 160-01, 03, 04, 11 | Every cell run records identity-by-signature, controller string, shield rev, fw/app SHA, chip part/package before testing | ✓ SATISFIED | `capture_provenance.py` enforces required-or-refuse fields; `probe_board.py` provides signature (not handshake) identity; exercised live in `BRINGUP-wrv/provenance.json` |
| RIG-03 | 160-06 | One arm-agnostic procedure both arms follow identically | ✓ SATISFIED | `PROCEDURE.md` + `render_steps.py` empty-diff gate, falsification-tested |
| RIG-04 | 160-03, 05, 12 | Full-device SHA equality oracle, never exit code; v1.33 N=3 read stability | ✓ SATISFIED | `judge_wrv.py` judged against written image; `BRINGUP-wrv/WRV-VERDICT.json` shows N=3 agreement |
| RIG-05 | 160-04, 07, 13 | Per-cell record self-sufficient for re-run without session memory | ✓ SATISFIED | 3-round D-17 reconstruction with 2 real fixes; `gate_record.py` argv/field enforcement |

All 5 requirement IDs declared across the phase's plans (RIG-01…05) are accounted for and marked
Complete in both `.planning/REQUIREMENTS.md` and the phase's own plans. No orphaned requirements
found — `REQUIREMENTS.md`'s BOARD-01…03 (Phase 161+) are correctly left unchecked as future-phase
work, not orphaned Phase 160 requirements.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `tools/gate_record.py` | 73, 589 | Literal strings `"TBD"`/`"TODO"` etc. | ℹ️ Info | Part of the placeholder-value *detection* set and a test fixture — not a debt marker in the deliverable itself |

No unresolved `TBD`/`FIXME`/`XXX`/`HACK` debt markers found in any file the phase modified. The one
`avrdude-mcu-detection-fallback` todo referenced by this phase was annotated additively only
(`status: pending`, `resolves_phase: null` both confirmed unchanged) — verified directly against
`.planning/todos/pending/avrdude-mcu-detection-fallback.md`.

### Behavioral Spot-Checks / Probe Execution

| Probe/Check | Command | Result | Status |
|---|---|---|---|
| Full gate suite | `bash .planning/v1.34/tools/run_gates.sh` (direct exit code) | `ALL GATES PASSED`, exit 0 | ✓ PASS |
| `render_steps.py` empty-diff (real file) | `diff <(render_steps.py --arm control) <(render_steps.py --arm v133)` | empty | ✓ PASS |
| `render_steps.py` falsification leg | `--selftest` | 7/7 legs pass, including the arm-conditional negative | ✓ PASS |
| `judge_wrv.py` Pitfall-6 false-green leg | `--selftest` | self-consistent-but-wrong case correctly flagged `mismatch` + `verdict_disagreement` | ✓ PASS |
| Image hash integrity | `sha256sum -c SHA256SUMS.txt` | 6/6 OK | ✓ PASS |
| Submodule cleanliness | `git status --short` in both submodules | empty (porcelain-clean) | ✓ PASS |

### Known, Previously-Disclosed Limits (confirmed recorded, not new gaps)

All six items in the operator's accepted carry-forward list are confirmed present in
`PHASE-160-GATE.md` §6 and/or `EVIDENCE.jsonl`/`provenance.json`:

1. `~/.firestarter` stray directory (07:59:25, `{"port": "/dev/ttyACM0"}`) — recorded, not deleted (sandbox denies), frozen config dir independently confirmed unaffected.
2. `BRINGUP-wrv` P-11 teardown never re-ran `probe_board.py` — Amendment 2 adds the missing command to `PROCEDURE.md`; the gap itself is not backfilled (correctly disclosed as such).
3. Sparse argv recording (0 `.cmd.json` in `BRINGUP-wrv`, 1 in `BRINGUP-uno`) — recorded as a scope limit on RIG-05's "recorded command line" property.
4. 4x recurring plan-authoring defect (hardcoded arm-agnostic constants in `<automated>` verify legs) — recorded; `rig-pins.json` gained `hex_span_expected_by_arm` as the fix.
5. Wave 6 false shield declaration — retained visibly marked SUPERSEDED in `EVIDENCE.jsonl`, not erased.
6. ~20 latent rig-tooling defects found only on first hardware contact — recorded as a method finding in §6.

None of these are raised as new gaps; they were verified present in the record exactly as the
operator accepted them.

### Human Verification Required

None. All must-haves resolved to VERIFIED via direct artifact inspection and gate execution; no
behavior-dependent truth was left unexercised, and no visual/real-time/external-service check was
in scope for this host-side, meta-repo-only phase.

### Gaps Summary

No gaps found. All 5 observable truths verified, all required artifacts exist/are substantive/are
wired, all key links confirmed, all 5 requirement IDs satisfied with evidence, no unresolved debt
markers, and the operator sign-off is confirmed genuine (not a rewrite-to-please diff). The phase
goal — both arms built and named for all three AVR targets, flash provable by device read-back with
a demonstrated wrong-arm detection, one arm-agnostic procedure with a falsifiable empty-diff gate,
the full-device SHA oracle with N=3 read stability judged against the written image (not the app's
own exit code), and a per-cell record proven self-sufficient across three reconstruction rounds —
is achieved and evidenced in the codebase, not merely claimed in SUMMARY prose.

---

_Verified: 2026-08-27T09:41:38Z_
_Verifier: Claude (gsd-verifier)_
