# Phase 160: RIG — Dual-Arm Build, Flash Provenance & the Shared Cell Procedure - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-25
**Phase:** 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedure
**Areas discussed:** Flash proof & arm identity, Host-arm switching, The W→R→V oracle, Per-cell record shape

**Area selection:** all four offered areas were selected.

---

## Flash proof & arm identity

### Q1 — How does a cell prove the board is carrying the named arm?

| Option | Description | Selected |
|--------|-------------|----------|
| Independent avrdude read-back | A separate `avrdude -U flash:r:<file>:r` pass after upload, SHA-compared against the uploaded image. Arm-agnostic, works on all three targets, the only check that catches the identical-version-string blind spot. One extra invocation per flash. | ✓ |
| avrdude's own verify pass | Rely on avrdude's built-in `-U flash:w:<hex>:i` verify. Cheaper and it IS a read-back rather than a bare exit code — but it is the upload tool judging its own upload, and no independent artifact is produced. | |
| Per-arm build marker | Bump `include/version.h` on one arm so the handshake self-identifies. Makes every later identity check trivial — but mutates the image under test, breaking Phase 145 D-16. | |

**User's choice:** Independent avrdude read-back
**Notes:** Grounded on the discussion-time measurement that both firmware arms carry the identical `VERSION "3.0.0b22"` literal and both host arms the identical `__version__ = "3.0.0b32"`.

### Q2 — What address range does the read-back SHA compare cover?

| Option | Description | Selected |
|--------|-------------|----------|
| Hex extent judged, whole flash recorded | Judge the `.hex`'s own address span; record the whole-32768 B read-back SHA separately as an unjudged provenance datum. No bootloader base addresses to pin, and the raw figure stays available to Phase 165. | ✓ |
| Hex extent only | Judge and record only the `.hex` extent. Simplest — but bootloader-region damage is invisible for the whole milestone. | |
| Full flash, named exclusion windows | Compare all 32768 B with per-target bootloader exclusion windows (optiboot 512 B / urclock 384 B / Caterina 4096 B) pinned. Strictest — but a differing installed bootloader build throws spurious diffs the rig must then adjudicate. | |

**User's choice:** Hex extent judged, whole flash recorded
**Notes:** Context: `board_upload.maximum_size = 32768` on all three envs means the linker no longer protects the bootloader region, so a full-flash read spans regions the `.hex` never covers.

### Q3 — How is the wrong-arm detection proven able to fail?

| Option | Description | Selected |
|--------|-------------|----------|
| Real wrong-arm flash, all 3 targets | On each target: deliberately flash the other arm, observe and record the MISMATCH, then flash the correct arm and observe the match. Exercises the full chain per target — and the chain genuinely differs (urclock / arduino / avr109). 3 extra flash cycles. | ✓ |
| Real wrong-arm flash on Leonardo only | Full cross-flash once on the reference rig; comparator-only proof on the other two. One extra flash cycle — but avr109 becomes the only chain proven end-to-end. | |
| Comparator-only, all 3 targets | SHA-compare a good read-back against the other arm's hex, observe mismatch. Zero extra flash cycles — but it proves only that two different files hash differently and never exercises the read-back path. | |

**User's choice:** Real wrong-arm flash, all 3 targets
**Notes:** Consistent with the standing memory that bench boards are a firmware-flash testbed with standing approval, so extra flash cycles are cheap.

### Q4 — Where do the six built images (2 arms × 3 targets) live?

| Option | Description | Selected |
|--------|-------------|----------|
| Commit the 6 hex files | `.planning/v1.34/images/` with `SHA256SUMS.txt`, ~450 KB. Exact bytes stay re-flashable regardless of toolchain drift; makes RIG-05 literally true. Phase 145 precedent. | ✓ |
| Record only, rebuild on demand | Record source SHAs, toolchain versions and image hashes; rebuild when needed. Clean repo — but SC#1's divergence escape clause becomes the expected path. | |
| Commit hex + the read-back bins | Everything, including every per-cell read-back `.bin`. Maximum auditability, a few hundred KB more and some tree noise. | |

**User's choice:** Commit the 6 hex files
**Notes:** Discussion-time check found no `__DATE__` / `__TIME__` / `__FILE__` anywhere in `firestarter/src/` or `firestarter/include/`, so byte-identical rebuilds are plausible against the baseline's pinned toolchain.

**Not asked (decided mechanically):** whether the read-back runs at every cell flash or only at bring-up — Phase 161's BOARD-02 SC#2 already mandates per-cell.

---

## Host-arm switching

### Q1 — How does the bench switch between the two host-app arms?

| Option | Description | Selected |
|--------|-------------|----------|
| Two worktrees, two venvs | Each arm a worktree with its own venv and editable install. The arm is named by the invoked binary path, so it appears verbatim in the recorded command line. Setup cost; each venv must be verified by printing `firestarter.__file__`. | ✓ (Claude's call) |
| In-place git checkout | `git checkout <sha>` in `/workspaces/firestarter_app`; the existing editable install follows. Zero setup — but the arm is implicit in the working tree and a forgotten checkout silently mis-arms a cell. | |
| Two full clones, two venvs | Same isolation, independent clones. Sidesteps worktree pitfalls at the cost of a second clone and two remotes. | |

**User's choice:** "You decide" → Claude chose **two worktrees, two venvs**
**Notes:** Rationale given: it is the only option where the arm appears in the command line RIG-05 requires, both arms stay callable without a checkout step, and `firestarter.__file__` gives positive per-invocation proof — which matters because `--version` reports `3.0.0b32` on both arms. Two follow-on constraints flagged: an editable install does not follow a worktree, and a pre-existing user-site editable install means bare `firestarter` on PATH resolves to a third un-named arm.

### Q2 — How is `~/.firestarter` config state handled across the two arms?

| Option | Description | Selected |
|--------|-------------|----------|
| One frozen shared config dir | One `FIRESTARTER_CONFIG_DIR` for both arms, seeded at bring-up, content SHA recorded per cell and re-verified after each. Keeps the A/B variable to the code alone; any config write becomes a visible event. | ✓ |
| Separate config dir per arm | No cross-contamination — but the two dirs can legitimately diverge, adding a second variable to a one-variable comparison. | |
| Default ~/.firestarter, unmanaged | Least ceremony, closest to real user behaviour — and nothing detects a config write that changes a later cell's inputs. | |

**User's choice:** One frozen shared config dir
**Notes:** `firestarter/config.py:25` honours `FIRESTARTER_CONFIG_DIR` as a deliberate isolation seam. No `~/.firestarter` existed at discussion time — clean slate.

### Q3 — What proves, in the record, which host arm actually ran a cell?

| Option | Description | Selected |
|--------|-------------|----------|
| Triple: SHA + porcelain + `__file__` | `git rev-parse HEAD` names the arm, empty `git status --porcelain` proves the tree is that commit and nothing more, `firestarter.__file__` proves the venv resolves into that worktree. | ✓ |
| SHA + `__file__` | Two fields instead of three — but a stray uncommitted edit rides into a cell invisibly. | |
| Worktree path in the command line | The absolute venv binary path is the proof. No capture step — but it proves which binary ran, not what state the worktree was in. | |

**User's choice:** Triple: SHA + porcelain + `__file__`

**Not asked (decided mechanically):** both arms run on one interpreter (devcontainer py3.12, not the py3.11 CI floor) — same interpreter for both, so not an A/B confound; recorded once and stated as a Phase 166 non-claim.

---

## The W→R→V oracle

### Q1 — What performs the reads, and what judges them?

| Option | Description | Selected |
|--------|-------------|----------|
| `dev consistency-check` produces, phase script judges | `--runs 3 --output-dir --keep-files` produces per-run binaries; a phase-owned script computes the judged SHA over the full device size. The app's own 0/1/2 verdict is recorded but unjudged; disagreement is itself a finding. Satisfies RIG-04 and Phase 145 D-06. | ✓ |
| Plain `read` ×N produces, phase script judges | Same independent judgement, but exercises only the user-facing read path — `dev consistency-check` is beta-channel-gated. Costs N invocations, loses the tool's divergence report. | |
| Both paths, once each per cell | Broadest coverage; roughly doubles read time across 20 positions. | |

**User's choice:** `dev consistency-check` produces, phase script judges
**Notes:** D-06's "judge ≠ subject" bites harder here than in v1.31 because the host app is itself an arm variable. Flagged for the honesty ledger: the judged evidence chain runs through a dev-tools-gated command stable users do not have.

### Q2 — Does the control arm get N=3 too?

| Option | Description | Selected |
|--------|-------------|----------|
| Conditional — control N=3 only on a v1.33 disagreement | N=3 on the v1.33 arm at every position; control arm single read, escalating to N=3 only where the v1.33 arm's reads disagree. Mirrors CHIP-04's "control re-run for every divergence and for no other". | ✓ |
| Symmetric — N=3 on both arms everywhere | No asymmetry to explain; a read-stability delta is directly attributable. Costs 40 extra reads, 10 on the 256 KiB W29C020. | |
| As specified — v1.33 arm only | RIG-04's bare letter, cheapest — but a v1.33-arm instability finding would be unattributable. | |

**User's choice:** Conditional — control N=3 only on a v1.33 disagreement

### Q3 — What image gets written at each position?

| Option | Description | Selected |
|--------|-------------|----------|
| Distinct per (cell × chip × arm) | 20 distinct seed-derived address-attributable images. Every write flips real bits regardless of what the previous arm left, so LOOP-06's no-op path cannot produce a green; address-attribution faults become visible. | ✓ |
| Distinct per arm, shared across cells | Four images. Still defeats the no-op trap — but a cross-cell address-attribution fault passes unnoticed. | |
| One image per chip, used everywhere | Two images, trivial cross-cell comparison — but walks into the LOOP-06 hazard on the milestone's headline arm. | |

**User's choice:** Distinct per (cell × chip × arm)
**Notes:** Raised with the standing evidence that `dev test`'s second write emits zero pulses on 329/746 parts because LOOP-06 skips already-correct bytes; and that while an erase almost certainly neutralises this, Phase 145 D-03 explicitly refused to assume the erase ran on this bench.

---

## Per-cell record shape

### Q1 — How is the per-cell provenance block produced?

| Option | Description | Selected |
|--------|-------------|----------|
| Phase-owned script emits JSON | `capture_provenance.py` gathers every machine-readable field and requires the operator-declared shield revision as an argument, refusing to run without it. Discharges RIG-05 by mechanism rather than by discipline. | ✓ |
| PROCEDURE.md checklist, filled by hand | No tooling — but RIG-05's falsification test then measures the transcriber, and a mistyped SHA is indistinguishable from a real one. | |
| Hybrid — script for machine fields, prose for the rest | Less tooling, more rigour than transcription — but two record formats to reconcile, and Phase 166's arithmetic reaches only half of it. | |

**User's choice:** Phase-owned script emits JSON

### Q2 — What is the canonical form of the evidence record Phases 161–166 fill?

| Option | Description | Selected |
|--------|-------------|----------|
| JSONL canonical, Markdown rendered from it | Append-only `EVIDENCE.jsonl`, one row per position, `locked_columns` pinned at Phase 160; `EVIDENCE.md` generated, never hand-edited. CLOSE-01's arithmetic becomes a script, so a silent gap is structurally impossible. | ✓ |
| Paired `EVIDENCE.{md,json}`, both hand-maintained | The proven v1.15 / v1.18 shape; Markdown stays freely editable — but the two can drift and CLOSE-01 is only as good as the last sync. | |
| Markdown-primary, per-cell JSON sidecars | Phase 145's shape scaled up; each cell's machine record sits next to its cell — but Phase 166 must walk and merge ~20 sidecars, and the merge can be got wrong. | |

**User's choice:** JSONL canonical, Markdown rendered from it

### Q3 — How is "reconstructing the run from the record alone" actually tested?

| Option | Description | Selected |
|--------|-------------|----------|
| Script gate per cell + one fresh-context reconstruction | A script gates every cell record for field presence and command re-parse; once, against the bring-up record before any sweep cell runs, a fresh context given only the record and procedure emits the setup it would use, diffed against the prescription. | ✓ |
| Script completeness gate only | Fully mechanical — but proves the record has all its fields, not that someone holding only it could rebuild the rig. | |
| One fresh-context reconstruction only | Tests the real property with least machinery — but cells 2 through 20 go unchecked. | |

**User's choice:** Script gate per cell + one fresh-context reconstruction

**Not asked (decided mechanically):** the signature probe is a phase-owned tool reusing the `avrdude-mcu-detection-fallback` todo's mechanism, with the todo staying pending (folding its product deliverable would be an Out-of-Scope product-code change); and all rig-shaped artifacts live at `.planning/v1.34/`, following the `.planning/v1.15/bench/` precedent.

---

## Claude's Discretion

- **Host-arm switching mechanism** — user answered "You decide". Claude chose two worktrees + two venvs. CONTEXT.md records that the load-bearing property is the arm appearing in the invoked binary path, not the worktree mechanism itself; two full clones is a permitted substitution, in-place checkout is not.
- **Outcome taxonomy** — decided without asking: cell outcome stays Phase 145 D-14's two-state axis (validated / skipped-with-reason); RCA-04's three-state axis (v1.33-caused / pre-existing / inconclusive) applies only to Phase 165 triage of an already-recorded failure.
- **Left open for research/planning** — PROCEDURE.md's exact step ordering and two-chip rotation; the mid-sweep halt policy (Phase 145 D-13 halted and handed to `/gsd-debug`; v1.34 has Phase 165 as triage owner, so the policy needs restating rather than inheriting); and whether write duration is wall-clock or scraped from app output.

## Deferred Ideas

- Product-side `firestarter fw -i --detect-mcu` (the folded todo's deliverable half) — mechanism reused, product change stays pending.
- Neutralizing the user-site editable install rather than forbidding bare `firestarter` by procedure.
- Building the two arm venvs on py3.11 to match CI instead of the devcontainer's 3.12.
- Full-flash compare with pinned bootloader exclusion windows (D-02's rejected option).
- Symmetric N=3 on both arms at every position (D-11's rejected option) — available as a Phase 161 escalation.
