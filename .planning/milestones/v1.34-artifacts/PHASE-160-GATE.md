# Phase 160 Gate — RIG: Dual-Arm Build, Flash Provenance & the Shared Cell Procedure

**Status: APPROVED — 2026-08-27.** The operator's verbatim response: **"Approved — close
Phase 160"**. This document was assembled by the executor as part of presenting Plan 13 Task
3's `checkpoint:human-verify` gate, then updated in place (this header and the "Operator
sign-off" section only) to record the response once given. Every path below exists on disk as
of this writing; every number below is read out of the cited artifact, not restated from a
plan SUMMARY. Sections §1-§7 below, including every non-claim and every carried-forward item,
are unchanged from the version the operator reviewed — nothing was softened, dropped, or
reworded to secure the approval; the sign-off in §"Operator sign-off" states explicitly that
those limits were presented and accepted, not merely disclosed.

What this gate decided: whether the rig is trustworthy enough that twenty evidence positions
(Phases 161-163) may rest on it. The operator's approval releases those phases; nothing beyond
this phase's own bring-up had run on the bench before this approval, and the bench itself is
left exactly as §7 describes for Phase 161 to inherit.

---

## 1. The three cross-flash falsifications

Each of the three read-chain targets was flashed with the *wrong* arm, judged by the same
independent-avrdude-read-back detector against the *intended* arm's hex, and the detector was
required to actually report a mismatch — not merely be theoretically capable of one.

| Target | Record | Differing bytes (judged span) | Negative control |
|---|---|---|---|
| `uno` (plan 08) | `.planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-uno/CROSSFLASH.md` (Event 2) | **22367 of 26026** (86%) | **FIRED** — "The negative control FIRED. The wrong-arm detector was exercised for real ... and it correctly reported MISMATCH with measured, non-trivial evidence" |
| `uno328pb` (plan 09) | `.planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-uno328pb/CROSSFLASH.md` (Event 2) | **22300 of 26066** judged bytes actually compared (85.6%; 8 vector-excluded bytes are a separate, disclosed non-claim, §6) | **FIRED** — "The negative control FIRED ... correctly reported MISMATCH with measured, non-trivial evidence (22300 of 26066 judged bytes differing, 85.6%)" |
| `leonardo` (plan 10) | `.planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-leonardo/CROSSFLASH.md` (Event 2) | **24454 of 28170** (86.8%) | **FIRED** — "The negative control FIRED ... correctly reported MISMATCH with measured, non-trivial evidence (24454 of 28170 judged bytes differing, 86.8%)" |

**Cross-target rollup:** `.planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-leonardo/CROSSFLASH.md`,
"## Cross-target rollup — D-03 complete across all three targets". Quoted verbatim: "D-03 is
complete across all three targets. Each chain's wrong-arm detector has been exercised by a
real, deliberate device flash of the *other* arm, judged by an independent avrdude read-back
against the *intended* arm's hex extent, and each one reported MISMATCH with measured,
non-trivial evidence (all three in the 85-87% range) rather than being inferred from another
target's proof." Each event's correction (a third, re-flash-and-rejudge event on every target)
is recorded matching in the same file.

## 2. The reconstruction falsification

- **Reconstruction:** `.planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/RECONSTRUCTION.md`
- **Classified diff:** `.planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/RECONSTRUCTION-DIFF.md`
- **Rounds it took:** **3** — round 1 (original record) found 1 record insufficiency; round 2
  (record fixed) confirmed the fix and found 1 prescription ambiguity; round 3 (both fixes
  applied) confirmed both closures.
- **Divergence counts by kind:** record insufficiency = **1** (fixed: `capture_provenance.py`
  gained `image_mask`/`image_stamp_width`/`image_sha`, re-captured via a new
  `--patch-image-plan` mode, zero device I/O); prescription ambiguity = **1** (fixed:
  `PROCEDURE.md` `P-11` gained a literal command block, Amendment 2); cosmetic = **6**;
  not-a-divergence = **1**.
- **Closing statement, quoted from `RECONSTRUCTION-DIFF.md`:** "Round 3's command set and
  physical setup are equivalent to the prescription with **zero** values sourced from
  anywhere but the two inputs ... No command in the final (round 3) reconstruction has a bare
  application name as its first token, and the shield revision was correctly resolved from the
  record in every round."
- **One disclosed, not-backfilled finding this exercise also surfaced:** `BRINGUP-wrv`'s own
  actual `P-11` teardown (Phase 160 Plan 12) never re-ran `probe_board.py` at all, a genuine
  compliance gap against the (now-amended) prescription — see §6, non-claims.

## 3. The gate-birth ledger

One line per rig tool, naming the deliberately broken input its negative leg used and the plan
SUMMARY where that red was recorded. Every one of the twelve tools has at least one recorded
red observation; none is a gap.

| Tool | Deliberately broken input observed red | Recorded in |
|---|---|---|
| `check_rebuild.py` | a nonexistent `--images` path, and a hand-corrupted copy of a genuinely committed image compared against the real `SHA256SUMS.txt` | `160-02-SUMMARY.md` |
| `gen_addr_image.py` | `--stamp-width 16` on a 262144 B size (refused, exit 2) and a bad-usage invocation | `160-03-SUMMARY.md` |
| `check_arms.py` | a deliberately wrong `--expect-config-sha` against the two real live arms | `160-03-SUMMARY.md` |
| `probe_board.py` | unparseable avrdude stderr and an MCU-mismatch, against a fabricated fake-avrdude fixture | `160-04-SUMMARY.md` |
| `capture_provenance.py` | missing `--shield-rev` and an out-of-set `--shield-rev` value, live | `160-04-SUMMARY.md`; extended selftest coverage (image-plan resolver + `--patch-image-plan`, both positive and negative legs) added and exercised this plan — `bench/cells/BRINGUP-wrv/RECONSTRUCTION-DIFF.md`, "RI-1" |
| `gate_record.py` | out-of-domain `outcome`, a bare-argv0 command, and a forbidden-flag command, against hand-written fixture JSON | `160-04-SUMMARY.md` |
| `judge_readback.py` | short read-back, corrupted-prefix mismatch, cross-arm expectation, and the `PENDING-xshowvector` placeholder refusal, against hand-built fixtures — **and**, on real silicon, the three D-03 cross-flash MISMATCHes in §1 | `160-05-SUMMARY.md`; `160-08/09/10-SUMMARY.md` |
| `judge_wrv.py` | the Pitfall 6 false-green leg (three self-consistent but wrong reads, app-verdict PASS) against hand-built fixtures | `160-05-SUMMARY.md` |
| `touch_1200.py` | a non-existent port path | `160-05-SUMMARY.md` |
| `render_steps.py` | a temporary, deliberately arm-conditional copy of the real `PROCEDURE.md` | `160-06-SUMMARY.md` |
| `render_evidence.py` | a one-character-edited copy of `EVIDENCE.md` (never the committed file) | `160-07-SUMMARY.md` |
| `run_gates.sh` | a one-file tools directory whose file advertises no `--selftest`, and an empty tools directory | `160-07-SUMMARY.md` |

## 4. The suite result

```
$ bash .planning/milestones/v1.34-artifacts/tools/run_gates.sh
...
===== run_gates.sh SUMMARY =====
  tool self-tests run: 11 / 11
  mode: full
ALL GATES PASSED
```

**Exit status: 0.** Tool self-tests run: **11 / 11** (the twelfth entry, `run_gates.sh`
itself, is the runner, not a self-testing subject). Live gates run: **5 / 5**
(`check_rebuild.py`, `check_arms.py`, `render_steps.py`, `render_evidence.py --check`,
`gate_record.py`). Run immediately before this document was assembled, with no `__pycache__`
artifact under `.planning/milestones/v1.34-artifacts/tools/` skewing a filesystem-glob-based tool count (a stray,
gitignored bytecode-cache directory was found and removed by this plan's Task 2 while filling
the validation map — a filesystem artifact, not a source change).

## 5. The record state

Read from `.planning/milestones/v1.34-artifacts/bench/EVIDENCE.jsonl` / `EVIDENCE.md` directly:

- **Bring-up rows: 4** — `BRINGUP-uno__control__none`, `BRINGUP-uno328pb__control__none`,
  `BRINGUP-leonardo__control__none`, `BRINGUP-wrv__v133__w27c512`.
- **Sweep rows: 0.**
- **Reconciliation, quoted verbatim from `bench/EVIDENCE.md`'s own "## Reconciliation"
  section:** "0 validated + 0 skipped-with-reason = 0 of 20 positions accounted for (20 not
  yet recorded)."

This phase produced rig evidence and zero sweep evidence, exactly as its own success criteria
require — no row bearing a sweep cell id (`A1`, `A2`, `A3/B2`, `B1`, `B3`) exists anywhere in
the canonical record.

## 6. The non-claims

Every limit this phase carries, one per line, collected from the artifacts rather than from
memory:

- **No target's flash check used a named alternative.** All three read chains (`uno`,
  `uno328pb`, `leonardo`) took RIG-01 SC#2's Branch A — a proven full 32768 B read-back —
  never the partial-span-read alternative branch. Quoted from
  `BRINGUP-leonardo/CROSSFLASH.md`: "No named alternative is in force anywhere in this
  milestone's RIG-01 SC#2 claim." There is therefore no "named alternative mistaken for a
  full-span proof" risk anywhere in this phase's own record — but see the next line for a
  related, narrower limit.
- **`uno328pb`'s comparison excludes 8 bytes.** Under the `vector-exclusion` judged-span
  policy (`BOOTLOADER.md`, derived from a live `-xshowvector` interrogation), the reset vector
  `[0,4)` and the SPM_Ready interrupt vector `[100,104)` — 8 bytes total, out of a 26074 B
  judged extent — are excluded from every byte comparison on this target, because `urclock`
  itself patches those bytes on upload. This detector **cannot see** a fault confined entirely
  to those 8 bytes; it can and did see everything else (22300 of 26066 remaining judged bytes
  differing under the deliberate cross-flash, §1). This is a scope exclusion of a bootloader
  mechanism's own known patch, not a weakened detector — but it is a real bytes-not-covered
  limit and is stated as one.
- **Both host arms ran on the devcontainer interpreter (Python 3.12.14, `provenance.json`
  `interpreter` field), not the app-CI floor (Python 3.11).** Standing project memory records
  that the devcontainer's 3.12 interpreter has previously masked a CI-only defect
  (`reference_devcontainer_py312_masks_ci_py39`). Nothing in this phase's own record proves
  this rig's tooling behaves identically under 3.11.
- **The judged evidence chain runs through a command stable-channel users do not have.**
  `dev consistency-check` is one of `firestarter_app/firestarter/channel.py`'s
  `BETA_ONLY_DEV_COMMANDS`; both arms self-report `3.0.0b32` (a prerelease), so the command
  stays registered for this rig, but a stable-channel install of either arm would not expose
  it. RIG-04's independent-SHA judgment is unaffected (`judge_wrv.py` computes its own SHA
  regardless of which command produced the read files), but the specific read-set command
  this phase used is a dev-channel-only surface.
- **The 262144-byte read size is proven by fixture, not yet on silicon.** `judge_wrv.py`'s
  `--selftest` exercises both members of its `_VALID_SIZES` domain (65536 and 262144) in code;
  only 65536 B (W27C512, `BRINGUP-wrv`) has been exercised against real hardware in this
  phase. The 262144 B path (W29C020) is Phase 161's first on-silicon exercise of that size.
- **Every value in this phase's canonical records that reads as `not measured` carries its own
  blocking reason on the same line** (`bench/cells/BRINGUP-wrv/provenance.json`):
  `controller_string` ("the `hw` CLI subcommand's handler ... never forwards the CLI's
  `-v`/`--verbose` into the wire command's `flags` field, so `FLAG_VERBOSE` is never set ...
  a genuine host-app limitation, out of scope for this phase to fix"); `hw_revision_bucket`
  ("`hw` command's revision line not found in this session's output"); `r16_ohms` and
  `r14r15_ohms` ("no read-back CLI path exists ...; firestarter config is write-only in this
  app version" — independently cross-checked against the operator's own "can't read them"
  answer, `POT.md`).
- **An open, disclosed, not-silently-resolved rig-hygiene item:** `~/.firestarter` was found
  to exist at `BRINGUP-wrv`'s Plan 12 teardown (a directory the frozen
  `FIRESTARTER_CONFIG_DIR` seam is supposed to make unnecessary), traced circumstantially to
  an unlogged prior invocation, with the frozen config directory itself independently
  confirmed unaffected (`check_arms.py --expect-config-sha`, exit 0). Removal was attempted
  and denied by sandbox policy. Recorded in `provenance.json`'s `commands[]` and
  `EVIDENCE.jsonl`'s `anomalies` field; not cleared as of this gate.
- **A second, distinct open item found by this plan's own reconstruction exercise:**
  `BRINGUP-wrv`'s actual `P-11` teardown (Plan 12) never re-ran `probe_board.py` at all — only
  the config-directory check ran — a genuine compliance gap against `PROCEDURE.md`'s
  (pre-Amendment-2) prose prescription. `PROCEDURE.md` now carries the missing literal command
  (Amendment 2), so this cannot recur, but `BRINGUP-wrv`'s own board-identity-since-`P-02`
  assurance was never re-confirmed at its teardown and is not backfilled here (doing so would
  require an avrdude signature probe against a board this plan's own constraints forbid
  touching while a chip is seated). See `RECONSTRUCTION-DIFF.md`, PA-1.
- **argv is rarely recorded across the bring-up cells as a whole.** `bench/cells/BRINGUP-wrv/`
  contains zero `*.cmd.json` sidecar files; `bench/cells/BRINGUP-uno/` contains exactly one
  (`logs/04_pio_upload_control.cmd.json`). Every cell logs stdout/stderr for nearly every
  step, but almost none records the literal argv that produced it. `gate_record.py`'s argv
  re-parse (`check_commands`) therefore has structurally little to inspect across most of
  this phase's own logged steps — RIG-05's "recorded command line" property is demonstrated
  on the identity-capture and position-capture invocations `provenance.json` itself carries,
  but is **not** demonstrated as a general property of every logged step in every cell.
- **A shell-level `FOO=bar cmd` env-var assignment never appears in any recorded argv, by
  construction** — the shell strips it before exec, so an argv-based check can never detect a
  missing `FIRESTARTER_CONFIG_DIR` prefix. The only detectors that exist today are the two
  `P-11` teardown assertions (`~/.firestarter` absence; the frozen directory's own SHA), and
  per the open item above, they must run at every cell's own teardown to be meaningful — a
  cell whose teardown skips them (as `BRINGUP-wrv`'s did for the first assertion's sibling
  probe) carries this same structural blind spot.
- **A plan-authoring defect class (an arm-agnostic or otherwise-hardcoded literal in a task's
  own `<automated>` verify leg) recurred at least four times across this phase** (plans 08, 09,
  10's hardcoded-span verify legs; plan 12's literal-string `"consistency-check"` grep against
  the app's real `"Consistency check: PASS"` output), each caught and corrected in-flight by
  the executing agent rather than by any gate. `rig-pins.json` gained
  `hex_span_expected_by_arm` as a direct result. This is a finding about the planning method
  this phase used, not merely about the tools it produced; Phase 161-163 will inherit
  similarly-authored verify legs across twenty positions, where a wrong literal would be
  twenty false results rather than one or two.
- **A false physical claim was recorded and then superseded in place, not silently corrected**
  (Wave 6, this milestone's own record-honesty standard). The incident is retained, visibly
  marked superseded, in this milestone's evidence trail as the demonstrated instance of the
  exact failure mode (a wrong declaration entering the record) this milestone exists to catch
  — caught by the operator, not by a gate, which is itself a finding about where this phase's
  gates do and do not reach.
- **Roughly twenty latent rig-tooling defects were found across waves 5-9, and every one of
  them had a passing fixture-based `--selftest` and failed on first contact with real
  hardware.** This is the strongest single argument this phase has produced in favour of
  bring-up-before-production ordering — a finding about the *method*, not only about the
  tools — and it is why Phase 161-163's own first cells should expect, not be surprised by,
  a first-contact discovery or two of their own.

## 7. The rig state left standing

Read from `.planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/provenance.json` and Plan 12's own closing
statement:

- **Board:** Arduino Uno, ATmega328P, signature `0x1e950f`.
- **Shield:** Rev 2.0 (operator-declared from silkscreen).
- **Chip:** W27C512 (DIP28), **seated**.
- **Rail:** VPP confirmed at 12.0 V (one confirming reading; internal VCC 4.7 V).
- **Arm on the board:** v1.33 (`fw_sha 5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`), flashed and
  proven (`fw_readback_sha_judged == fw_readback_sha_whole_flash`'s judged half matches).
- **Port:** `/dev/ttyACM0`.

No avrdude firmware operation (upload, read-back, or signature probe) has run against this
board while the chip is seated since Plan 11's task 3 seated it. This is exactly the state
Phase 161's first cell inherits.

---

## Operator sign-off

**This gate was never auto-approvable, under any auto-advance or chained mode**, and it was
not auto-approved — the response below is the operator's own, given after review.

**Operator's verbatim response:** *"Approved — close Phase 160"*

**What was presented before that response, explicitly, not merely disclosed in a document
the operator may not have opened:** the three cross-flash falsifications and their
differing-byte counts (§1); the three-round D-17 reconstruction, including that **rounds 1
and 2 each FAILED** and each failure drove a real fix (§2); the full carried-forward list —
the `~/.firestarter` seam-and-log escape, `BRINGUP-wrv`'s un-re-run `P-11` board probe, the
sparse argv recording and its consequence for RIG-05's scope, the 4x arm-agnostic-constant
plan-authoring pattern, the Wave 6 superseded false declaration, and the ~20 latent tooling
defects found only on real hardware (§6); the rig state Phase 161 inherits (§7); and the
`run_gates.sh` result (§4). The operator was offered two named alternatives — strengthening a
named artifact first, or fixing the argv-recording gap first — and **chose approval with the
limits accepted as stated**, not resolved and not softened.

**Decision recorded:** **APPROVED**, 2026-08-27. Phase 160's own falsification and
record-honesty work is complete; this gate discharges RIG-05 (`.planning/REQUIREMENTS.md`)
and the phase itself. Phase completion (`ROADMAP.md`/`STATE.md` phase-level fields) and the
release of Phases 161-163 are the orchestrator's next step, not this document's.
