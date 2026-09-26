---
phase: 162-chip-11-part-dev-test-sweep-on-the-reference-rig
plan: 04
subsystem: bench, rig-tooling
tags: [bench, rig-tooling, host-only, wave-4, render-steps, procedure-amendment, no-hardware]

requires:
  - phase: 162-02
    provides: "bench/CHIP-EVIDENCE.jsonl's schema and tools/append_chip_evidence.py"
  - phase: 162-03
    provides: "tools/render_chip_evidence.py, bench/CHIP-EVIDENCE.md, and the two chip live gates already wired into run_gates.sh (14/14 selftests, 7/7 live gates baseline)"
provides:
  - "tools/render_steps.py's --section {P,C} argument — the two hardcoded parser facts (section heading, step-id pattern) generalised; two new --selftest legs; every pre-existing invocation (default section P) byte-identical to before"
  - "PROCEDURE.md Amendment 4 — the header/§Scope correction naming two cell shapes, the widened $CHIP token row + new $CHIP_TOKEN token, the new '## Chip-sweep step list' H2 (C-01..C-09), and the re-pinned ~/.firestarter mtime baseline inside P-11"
  - "run_gates.sh's render_steps.py live gate extended to render and diff BOTH sections (P and C) inside one gate — suite still 14/14 selftests, 7/7 live gates, exit 0"
affects: [162-05, 162-06, 162-07, 162-08, 162-09, 162-10]

tech-stack:
  added: []
  patterns:
    - "A parser/renderer generalised along exactly the two axes that differ between its two use sites (section heading, step-id pattern) while every other property (duplicate-id refusal, strict ascending order, arm-annotation domain check, fail-closed missing/empty-section refusal) stays shared code, selected via a single --section argument defaulting to the original behaviour"
    - "Procedure-document prose must never embed a literal '## <Heading Name>' substring outside the real heading itself — several of this plan's own verify scripts use a naive first-occurrence t.find('## X') rather than a line-anchored regex, and an early mid-sentence mention of the same string silently redirects the search to the wrong offset (caught and fixed three times during this plan; see Issues Encountered)"

key-files:
  created: []
  modified:
    - .planning/v1.34/tools/render_steps.py
    - .planning/v1.34/PROCEDURE.md
    - .planning/v1.34/tools/run_gates.sh

key-decisions:
  - "C-02's fenced command block is a rig-pins.json lookup (prints part/pin-count/VPP-target) rather than a repeat of C-03's firmware vpp read — C-02 is the operator handover (seat, JP4, and the physical multimeter reading at the two pot-group boundaries only); C-03 is the once-per-part firmware VPP reading. Keeping them as distinct, non-redundant commands matches the plan's own separation of 'operator handover' from 'firmware VPP reading'"
  - "C-08's fenced command block cites P-04 by reference (a comment line pointing at the '### P-04' heading above) rather than reproducing its git-checkout/pio-upload/judge_readback.py argv a second time, per the plan's explicit 'shared by reference and never by copy' instruction; the block's own literal commands are the parts unique to C-08 (the control-arm dev-test re-run and its append_chip_evidence.py call)"
  - "Amendment 4's own prose, and the Chip-sweep step list's opening paragraph, avoid ever writing the literal substrings '## Step list', '## Chip-sweep step list', or 'Amendment 4' outside their one real heading/label location — several of Task 2's own verify scripts locate sections via subprocess.run + str.find() (not a line-anchored regex), so an early mid-sentence occurrence of the same string silently breaks the slice. Discovered and fixed three times while iterating (see Issues Encountered); resolved by referring to sections in prose without the leading '##' and to the amendment as 'the amendment recorded at the bottom of this file' before its own heading"

requirements-completed: []

coverage:
  - id: D1
    description: "render_steps.py learns a second, independently gated section: --section {P,C} (default P, byte-identical to every pre-existing invocation), generalising only the section heading and the step-id pattern; two new --selftest legs (a combined 11-P/9-C positive fixture rendering arm-identically, and a symmetric negative pair proving a C-NN heading inside '## Step list' and a P-NN heading inside the chip section are each refused by name under the wrong section)"
    requirement: "CHIP-01"
    verification:
      - kind: unit
        ref: "python3 render_steps.py --selftest (9/9 legs: 7 original + 2 new)"
        status: pass
      - kind: integration
        ref: "render_steps.py --arm {control,v133} --section {P,C} against the real PROCEDURE.md: P=11 lines, C=9 lines, both arm-identical, both exit 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "PROCEDURE.md Amendment 4: header + Scope corrected to name two cell shapes; $CHIP token row widened to the eleven-part inventory plus a new $CHIP_TOKEN token; a new '## Chip-sweep step list' H2 with C-01..C-09 (each carrying a fenced command block, Performer: and Record field(s): clauses), sharing P-01/P-02/P-04/P-06/P-11 by reference and naming P-03/P-05/P-07/P-08/P-09/P-10 as not applicable with a reason each; the ~/.firestarter mtime baseline re-pinned inside P-11 (the only line inside '## Step list' that changed, and it carries the epoch value); Amendment 4 itself with 8 numbered (a)/(b) items and a (c) cell roster; no [arm: ...] annotation marker added to real text"
    requirement: "CHIP-02"
    verification:
      - kind: unit
        ref: "python3 - <<'PY' scripted assertions from 162-04-PLAN.md Task 2's <verify> blocks: P-NN heading byte-equality vs HEAD, Step-list diff scoped to the epoch-bearing mtime line, live-mtime match, C-01..C-09 structural checks, Arm-substitution table widened, Amendment 4 clause/cell-roster/marker-first checks — all PASS"
        status: pass
    human_judgment: false
  - id: D3
    description: "run_gates.sh's existing render_steps.py live gate extended to render and diff BOTH sections (four renders total) inside one gate — no eighth gate added; suite measures 14/14 tool selftests + 7/7 live gates, exit 0 (full and --quick, read directly, never piped); a planted [arm: control] marker on C-01 in a scratch copy of PROCEDURE.md is observed to make the two chip-section renders differ, and the real PROCEDURE.md is byte-unchanged by that check"
    requirement: "CHIP-01"
    verification:
      - kind: integration
        ref: "bash .planning/v1.34/tools/run_gates.sh; RC=$? (full and --quick, read directly); planted-marker negative-control transcript"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-08-28
status: complete
---

# Phase 162 Plan 04: render_steps.py second section + PROCEDURE.md Amendment 4 Summary

**Taught `render_steps.py` a `--section {P,C}` argument (default `P`, byte-identical to every prior invocation), wrote `PROCEDURE.md` Amendment 4 — a corrected header/§Scope naming two cell shapes, a widened `$CHIP` token row plus a new `$CHIP_TOKEN` token, a new `## Chip-sweep step list` H2 with nine prescriptive `C-01`…`C-09` steps, and the `~/.firestarter` mtime baseline re-pinned inside `P-11` — then extended `run_gates.sh`'s existing `render_steps.py` live gate to cover both sections inside one gate, holding the suite at 14/14 selftests and 7/7 live gates.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-08-28T17:06:27Z (approx, after the prior-wave tracking commit)
- **Completed:** 2026-08-28T17:26:03Z
- **Tasks:** 3/3 completed
- **Files modified:** 3 (`render_steps.py`, `PROCEDURE.md`, `run_gates.sh`)

## Accomplishments

- **`render_steps.py`'s `--section` argument, as built:** generalised exactly the two hardcoded
  facts the plan named — the section heading `extract_step_list_section()` looks for
  (`## Step list` for `P`, `## Chip-sweep step list` for `C`) and the two-digit id pattern
  `validate_steps()` enforces (`P-\d\d` / `C-\d\d`) — via two small lookup dicts
  (`_SECTION_HEADING_RE`, `_SECTION_HEADING_NAME`, `_SECTION_ID_RE`, `_SECTION_ID_LABEL`).
  Every other property (duplicate-id refusal, strict ascending numeric order, the arm-annotation
  domain check, the fail-closed missing/empty-section refusal) is unchanged and shared between
  both sections. `--section` defaults to `P`, so `run_gates.sh`'s two pre-existing calls and every
  other pre-existing invocation are byte-identical to before this argument existed.
- **Two new `--selftest` leg names, as landed** (9/9 total, up from 7/7):
  1. `positive (Amendment 4): a fixture with an 11-step P section and a 9-step C section renders
     9 lines under --section C and 11 under --section P, each arm-identical`
  2. `negative (Amendment 4): a 'C-NN' heading inside '## Step list' is refused naming the id and
     the P-NN pattern, and symmetrically a 'P-NN' heading inside the chip section is refused
     under --section C naming the id and the C-NN pattern`
- **`C-01`…`C-09` titles, as landed, with their performer split:**
  - `C-01` — Assert the frozen config dir is pristine (Claude)
  - `C-02` — Seat the part; set JP4 and the pot as this position requires (operator)
  - `C-03` — One firmware VPP reading for this part (Claude)
  - `C-04` — Capture provenance for this position (Claude)
  - `C-05` — Run dev test under the size-class ceiling, fully logged (Claude)
  - `C-06` — Read-divergence follow-up, only when the report says the two read runs diverged (Claude)
  - `C-07` — Append the row, then re-render and check (Claude)
  - `C-08` — Divergence arbitration, with the chip unmoved (Claude)
  - `C-09` — Per-wave gate (Claude)
  Five `P` steps are shared by reference (`P-01`, `P-02`, `P-04`, `P-06`, `P-11`); six are named
  explicitly not applicable with their own reason each (`P-03`, `P-05`, `P-07`, `P-08`, `P-09`,
  `P-10`).
- **The measured `~/.firestarter` four values, old and new, and the recurrence count:** path
  `/home/vscode/.firestarter`; one file `config.json`, 30 bytes; sha256
  `b323867c1f01b22a705dd9caf003ab7302a249fe46772f5b02e44aaa2760dd79` (unchanged); tree sha
  `423546cd37b5b45d9654e5acd07bd7e2a3c9e1df77e4d5feb79951bf37329951` (unchanged); mtime
  `1787817565` (`2026-08-27 07:59:25 UTC`, the Amendment-3 pin) → `1787854674`
  (`2026-08-27 18:17:54 UTC`, measured live at the moment this amendment was written) — the
  **fourth** recurrence, the first three being Phase 161's cells `A1`, `A2`, `A3/B2`.
- **Per-section render line counts, measured against the real `PROCEDURE.md`:** `--section P`
  (default): 11 lines, `--arm control` byte-identical to `--arm v133`. `--section C`: 9 lines,
  same arm-identity property. Both exit 0.
- **Negative-control transcript for the planted marker:** planted `[arm: control]` on the real
  `C-01` heading text inside a **scratch copy** of `PROCEDURE.md` at `/tmp/162-04-scratch-
  procedure.md`; `render_steps.py --section C` against the scratch copy for `control` vs `v133`
  produced two **different** renders (`cmp -s` returned non-zero) — the gate's new half observed
  to fire, not merely configured. `git diff --quiet -- .planning/v1.34/PROCEDURE.md` confirmed the
  real file was untouched by the check.
- **Measured `run_gates.sh` counts and exit code:** full run — `tool self-tests run: 14 / 14`,
  7 `live gate PASS` lines (independently counted), `ALL GATES PASSED`, exit `0`. `--quick` —
  same 14/14 selftests, exit `0`, output shows `section P: diff empty, control=11 v133=11 lines;
  section C: diff empty, control=9 v133=9 lines`. `ls .planning/v1.34/tools/*.py | wc -l` = **14**
  (no new tool file). `bench/EVIDENCE.jsonl`, `bench/EVIDENCE.md`, `bench/CHIP-EVIDENCE.jsonl`,
  `bench/CHIP-EVIDENCE.md` confirmed byte-unchanged throughout (`git status --porcelain` empty for
  all four). Both sub-repo porcelains (`git -C firestarter status --porcelain`, `git -C
  firestarter_app status --porcelain`) stayed empty for the whole plan.

## Task Commits

1. **Task 1: Teach render_steps.py a second, gated section** - `788c5456` (feat)
2. **Task 2: Write PROCEDURE.md Amendment 4 and the C-01…C-09 chip-sweep step list** - `7cfa63e0` (docs)
3. **Task 3: Extend the render_steps live gate to both sections and re-measure 14/14, 7/7** - `2d7d39d8` (feat)

**Plan metadata:** committed via this SUMMARY + STATE.md update (docs commit follows)

## Files Created/Modified

- `.planning/v1.34/tools/render_steps.py` — `--section {P,C}` argument, generalised
  `extract_step_list_section()`/`validate_steps()`, 2 new `--selftest` legs (9/9 total)
- `.planning/v1.34/PROCEDURE.md` — header + §Scope correction, widened `## Arm substitution`
  token table, new `## Chip-sweep step list` H2 (`C-01`…`C-09`), one re-pinned mtime value inside
  `P-11`, Amendment 4
- `.planning/v1.34/tools/run_gates.sh` — `render_steps.py` live-gate block extended to both
  sections (still one gate), header comment updated

## Decisions Made

- **C-02's command block is a `rig-pins.json` lookup, not a repeat of C-03's firmware VPP read.**
  C-02 is the operator handover (seat the part, set JP4, and — only at the two pot-group
  boundaries — request the operator's one multimeter reading); C-03 is the once-per-part firmware
  VPP reading via the arm's `vpp` subcommand. Giving C-02 its own non-redundant command (deriving
  the part's pin-count/package/VPP-target from `rig-pins.json` so Claude states measured facts,
  never recalled ones) satisfies the "no prose-only steps" requirement without duplicating C-03.
- **C-08 cites `P-04` by reference rather than reproducing its argv.** The plan's opening
  paragraph and clause (a)(2) both say the five shared steps apply "by reference, never by copy";
  C-08's fenced block therefore carries a comment line pointing at the `### P-04` heading plus the
  literal commands unique to C-08 itself (the control-arm `dev test` re-run and its
  `append_chip_evidence.py` call naming `control_rerun_for`).
- **Amendment 4 and the Chip-sweep step list's opening paragraph avoid writing `## Step list`,
  `## Chip-sweep step list`, or `Amendment 4` as literal substrings anywhere before their one real
  heading/label.** Several of this plan's own verify scripts (Task 2's Arm-substitution check and
  the Amendment-4-clause check) locate content via `str.find()` of the first occurrence rather
  than a line-anchored regex; an earlier mid-sentence mention of the same string silently redirects
  the slice to the wrong offset. See Issues Encountered for the three instances this was caught
  and fixed live during execution.
- **Only `run_gates.sh` was staged for Task 3's commit,** not all three files the plan's Task 3
  action text names ("Commit render_steps.py, PROCEDURE.md and run_gates.sh as one change") —
  `render_steps.py` and `PROCEDURE.md` had already been committed atomically in Tasks 1 and 2 per
  this executor's per-task commit protocol, so no further changes to those two files remained
  uncommitted at Task 3. This is a git-mechanics difference, not a content deviation: all three
  files carry exactly the changes the plan specifies, split across three atomic commits instead
  of one combined commit.

## Deviations from Plan

None — plan executed exactly as written. The three items above (C-02's command choice, C-08's
by-reference command block, and the literal-substring avoidance) are implementation choices within
the plan's own explicit instructions, not departures from its intent or any acceptance criterion.
The Task 3 single-file commit is a git-mechanics consequence of this executor's mandatory per-task
atomic-commit protocol, not a scope or content change.

## Known Stubs

None. Every `C-NN` step's command block is a literal, runnable invocation (using this
procedure's own substitution tokens, never expanded) — none is a placeholder pending a later plan.
Bracketed `<...>` values inside `C-04`/`C-05`/`C-07`/`C-08`'s command blocks (e.g. `<the pinned
config_dir_sha, from arms-provenance.json>`, `<PD-14 ceiling for this size class, seconds>`) are
the same style of runtime-supplied placeholder already used throughout the pre-existing `P-04`,
`P-07` and `P-09` bodies (e.g. `<fw_sha for {control|v133}>`), not new stub debt.

## Threat Flags

None beyond what the plan's own `<threat_model>` already covers (T-162-18 through T-162-22,
T-162-SC). No new network endpoint, auth path, file-access pattern, or schema change at a trust
boundary was introduced — this plan is prose (`PROCEDURE.md`) and a parser/gate extension only.

## Issues Encountered

- **Naive `str.find()` in three of this plan's own verify scripts collides with mid-sentence
  mentions of the same heading/label text.** Caught three times while drafting:
  1. Correction A's original header sentence wrote `` `## Chip-sweep step list` section instead
     of `## Step list` `` — this embeds the literal substring `## Step list` near the top of the
     file, before the real heading. The Arm-substitution verify script
     (`t.find('## Arm substitution'); t.find('## Step list')`) then sliced `t[i:j]` with `j < i`,
     producing an **empty** section and failing every subsequent slug assertion. Fixed by
     rewording to "the Chip-sweep step list section (see below) instead of the Step list section"
     — no `##` prefix in prose.
  2. The §Scope insertion originally wrote the same two heading-like substrings
     (`` `## Step list`'s `P-01`…`P-11` `` and `` under `` `## Chip-sweep step list` ``), even
     earlier in the file than Correction A. Same fix pattern applied.
  3. The Chip-sweep step list's own opening paragraph and the `$CHIP`/`$CHIP_TOKEN` table rows
     originally wrote `(Amendment 4, Phase 162)` / `(Amendment 4 widens this row...)` /
     `(Amendment 4)` — three occurrences of the literal string `Amendment 4` before the real
     `**Amendment 4 — ...**` paragraph at the file's bottom. The Amendment-4-clause verify script
     (`i=t.find('Amendment 4'); a=t[i:i+12000]`) then anchored on the *first* occurrence, 800+
     lines before the real amendment text, and the `(a) What changed:` assertion failed because
     that window never reached the real paragraph. Fixed by rewording all three to "the amendment
     recorded at the bottom of this file" / "Phase 162's amendment, recorded at the bottom of this
     file" — no literal `Amendment 4` substring anywhere before its own heading.
  All three were caught and fixed inline while iterating through the plan's own `<verify>` blocks,
  before any commit — not discovered after the fact. Each fix is a wording-only change; no
  acceptance criterion's substance changed.

## Next Steps

Plan 162-05 begins the bench sweep proper: seat W27C512 (already seated) and W27E512, run
`C-01`…`C-09` for each, and produce the first two rows in `bench/CHIP-EVIDENCE.jsonl`. This plan's
Wave 0 desk work is now fully discharged — `rig-pins.json`'s eleven-part map (162-01),
`bench/CHIP-EVIDENCE.jsonl`'s schema and `append_chip_evidence.py` (162-02),
`render_chip_evidence.py` and its two live gates (162-03), and now the amended `PROCEDURE.md` plus
`render_steps.py`'s second gated section and `run_gates.sh`'s extended live gate (162-04). No part
has been seated for the sweep and no `CHIP-EVIDENCE.jsonl` row exists yet — both remain exactly as
162-03 left them.

## Self-Check: PASSED

All modified files verified present on disk with the expected content (`render_steps.py`'s
`--section` argument and 9-leg selftest; `PROCEDURE.md`'s Amendment 4, widened Arm substitution
table, and `## Chip-sweep step list` section; `run_gates.sh`'s two-section `render_steps.py` gate
block). All three task commit hashes (`788c5456`, `7cfa63e0`, `2d7d39d8`) verified present in
`git log --oneline --all`. Final `bash .planning/v1.34/tools/run_gates.sh` re-run after all three
commits: 14/14 tool selftests, 7/7 live gates, exit 0.
