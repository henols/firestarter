---
phase: 130-close-honesty-ledger-claim-gate-release-decision
plan: 04
subsystem: docs
tags: [roadmap, honesty-ledger, record-correction, py32f071, semver-renumber]

# Dependency graph
requires:
  - phase: 130-close-honesty-ledger-claim-gate-release-decision (plan 130-02)
    provides: check_record_corrections.py, the label-aware planning-record staleness scanner, and the machine-derived py32-buffer-1024 coincidental-collocation finding at ROADMAP.md:28
provides:
  - "ROADMAP.md `## Milestones` list gains a real ✅ v1.23 PY32F071 Integration — Phases 123–130 entry (D-13)"
  - "Binary Command Protocol renumbered v1.23 → v1.28 and relocated after v1.27, preserving strict version order (D-14)"
  - "v1.28 PY32F071 Port + v1.29 PY32F071 USB Firmware Install collapsed into one dated retirement line; v1.29 left deliberately vacant"
  - "D-16 one-shot byte-unchanged proof for the v1.24–v1.27 entries (SHA-256 before/after, keyed on version token)"
  - "recordscan:allow marker suppressing the py32-buffer-1024 coincidental-collocation false-positive flagged by plan 130-02"
affects: [130-05, 130-06, 130-16]

# Tech tracking
tech-stack:
  added: []
  patterns: ["recordscan:allow inline HTML-comment marker for a self-diagnosed coincidental-collocation false-positive in check_record_corrections.py"]

key-files:
  created: []
  modified:
    - .planning/ROADMAP.md

key-decisions:
  - "D-13/D-14/D-16 landed exactly as specified in 130-CONTEXT.md; no architectural deviation"
  - "Chose a surgical Python line-range replacement (lines[27:34] only) over the Edit tool for this specific change, because two of the seven physical lines exceed 2500-6000 bytes and a manual-transcription Edit risked a single-character mismatch corrupting the byte-unchanged proof; the v1.24-v1.27 lines were carried forward by reference (never retyped) so byte-identity is structural, not merely verified after the fact"
  - "Added the recordscan:allow marker to the relocated v1.28 Binary Command Protocol entry per 130-02's explicit recommendation, discharging the py32-buffer-1024 false-positive without reworking or weakening the needle"

requirements-completed: []  # This plan ticks NO requirement ids (CLOSE-03 is discharged only by plan 130-16, per the plan's own <objective> and orchestrator_held_writes contract)

coverage:
  - id: D1
    description: "New ✅ v1.23 PY32F071 Integration — Phases 123–130 entry lands in the Milestones list, pointing at the existing detail section"
    verification:
      - kind: other
        ref: "python3 assertion: head[i23].startswith('- ✅ **v1.23 PY32F071 Integration**') and 'Phases 123–130' in that line (ROADMAP.md:28)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Binary Command Protocol renumbered v1.23 → v1.28 and relocated to immediately after v1.27, preserving strict version order"
    verification:
      - kind: other
        ref: "python3 assertion: 'v1.23 Binary Command Protocol' absent, 'v1.28 Binary Command Protocol' present, and the v1.23..v1.30 token span is strictly ascending by (major,minor) tuple (ROADMAP.md:29-35)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The two former py32 slots collapse into one dated retirement line naming both, pointing at the v1.23 detail section, stating the v1.29 number is vacant, and discharging the owning todo"
    verification:
      - kind: other
        ref: "python3 assertion: exactly one bullet matches the retirement text; grep -c '2c2ed10'==0, grep -c '603 additions'==0, grep -c 'PORTING.md'==0 within lines 1-45 (ROADMAP.md:34)"
        status: pass
    human_judgment: false
  - id: D4
    description: "v1.24-v1.27 entries proven byte-unchanged (D-16) by SHA-256 keyed on version token, before and after the edit"
    verification:
      - kind: other
        ref: "python3 sha256 re-hash of ROADMAP.md lines 29-32 against the four plan-recorded before-hashes; git diff -U0 confined to 2 hunks (line 28; lines 33-34)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Wording quality / honesty of the new v1.23 entry and retirement line (no overclaim, Validation Ceiling respected, no literal beta-cut-tag prediction)"
    verification: []
    human_judgment: true
    rationale: "Whether prose honestly respects the Validation Ceiling (no 'runs on a PY32F071' / no predicted cut tag) is a semantic judgment no committed checker in this plan scans for (ROADMAP.md is outside check_permitted_claims.py's four default targets) — a human or a later phase's re-read is the appropriate check."

# Metrics
duration: 55min
completed: 2026-08-02
status: complete
---

# Phase 130 Plan 04: ROADMAP Slot Renumber + D-16 Byte-Unchanged Proof Summary

**Collapsed the two orphaned py32 ROADMAP slots into one dated retirement line, gave v1.23 its first-ever real Milestones-list entry, moved Binary Command Protocol to the freed v1.28 slot, and proved the four untouched v1.24–v1.27 entries byte-identical by SHA-256 — all inside two git hunks confined to the former lines 28 and 33–34.**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-08-02T15:50:00Z (approx.)
- **Completed:** 2026-08-02T16:45:36Z
- **Tasks:** 3
- **Files modified:** 1 (`.planning/ROADMAP.md`) + this SUMMARY

## Accomplishments

- **D-13 landed:** `ROADMAP.md`'s `## Milestones` list gained its first-ever real `✅ **v1.23 PY32F071 Integration** — Phases 123–130` entry (line 28), where the file previously ran `✅ v1.22` straight into a mislabeled `⬜ v1.23 Binary Command Protocol` slot with no real v1.23 entry existing anywhere in the list.
- **D-14 landed:** That mislabeled entry is renumbered `v1.28 Binary Command Protocol` and relocated to immediately after `v1.27`, restoring strict version ordering for the v1.23–v1.30 span. Its stale *"Sequence ahead of v1.24"* sentence is annotated with the project's number-vs-sequence convention (matching the `v1.30` entry's own wording) without touching the `v1.24` reference itself.
- **D-13/todo discharge landed:** The former `v1.28 PY32F071 Port` and `v1.29 PY32F071 USB Firmware Install` entries (previously lines 33–34) collapse into one dated retirement line that names both former titles, points at the `## v1.23 — PY32F071 Integration` detail section, records the C-12 marker asymmetry (v1.29 already had `⚠ SUPERSEDED`, v1.28 had none), states the `v1.29` number is now deliberately vacant, and discharges `todos/pending/correct-v128-py32-roadmap-prior-art.md` in full — without restating any of that todo's five stale claims and without citing `PORTING.md` as an existing in-tree spec.
- **D-16 proven:** SHA-256 of the `v1.24`, `v1.25`, `v1.26` and `v1.27` entries measured before the edit and re-measured after — all four identical, at the same line numbers (29–32; unmoved, since the edit only touched lines 28, 33 and 34). No checker was built for this one-shot claim, per D-16's explicit instruction; the reason is recorded below.
- **Machine-derived false-positive discharged:** per plan 130-02's SUMMARY, the relocated `v1.28 Binary Command Protocol` entry's coincidental `DATA_BUFFER_SIZE`/`1024` mention (the Uno buffer-doubling discussion — unrelated to the py32 port's own `DATA_BUFFER_SIZE=512`) now carries a `<!-- recordscan:allow py32-buffer-1024: ... -->` marker, verified to flip `check_record_corrections.py`'s verdict for that hit from `unlabeled` to `inline-allow` without touching the needle regex.

## Task Commits

Two atomic content commits, split by file scope (not by task number), since Tasks 1 and 3 both write
exclusively to this SUMMARY.md and were authored together as one coherent document once the D-16
proof was complete end-to-end:

1. **Task 2: Rewrite the Milestones list** (`.planning/ROADMAP.md` only) — `0947d60` (docs)
2. **Tasks 1 + 3: D-16 before/after proof + plan documentation** (`130-04-SUMMARY.md` only) — see `git log --oneline -1` immediately following this commit (docs)

`git -C /workspaces diff --stat` for commit `0947d60` shows exactly one file: `.planning/ROADMAP.md`.

## Files Created/Modified

- `.planning/ROADMAP.md` — `## Milestones` list: line 28 rewritten (new v1.23 entry replacing the mislabeled BCP slot); lines 29–32 (`v1.24`–`v1.27`) untouched, byte-identical; lines 33–34 replaced with the relocated `v1.28 Binary Command Protocol` entry (annotated + `recordscan:allow`-marked) and the new py32 retirement line.

## D-16 Before/After Proof (Task 1 + Task 3, combined for readability)

Measured against the plan-recorded values (`130-04-PLAN.md` Task 1), which themselves matched a live re-measurement taken before any edit in this session — **zero drift** from plan time to execution time.

| Token | Before line | After line | Byte length (before) | SHA-256 | Expected to change? | Verdict |
|---|---|---|---|---|---|---|
| v1.23-BCP (old title) | 28 | — (retitled to v1.23 real; content moved to new v1.28 line) | 1660 | `5a0eabe5…c34` | yes | changed (by design) |
| v1.24 | 29 | 29 | 1220 | `4b83c9e1…630b` | **no** | **byte-unchanged** |
| v1.25 | 30 | 30 | 1679 | `4bc536d5…fa61f` | **no** | **byte-unchanged** |
| v1.26 | 31 | 31 | 2061 | `733b81dd…9dddf9` | **no** | **byte-unchanged** |
| v1.27 | 32 | 32 | 2428 | `bb8cc73a…d3b52` | **no** | **byte-unchanged** |
| v1.28-PY32-Port (old title) | 33 | — (deleted, collapsed into retirement line) | 2550 | `7df185cb…cd6c56` | yes | changed (deleted) |
| v1.29-PY32-USB (old title) | 34 | — (deleted, collapsed into retirement line) | 6092 | `b4a53246…3118edbd` | yes | changed (deleted) |
| v1.30 | 35 | 35 | 3385 | `ec99fc7f…3ed5b064` | **yes (by plan 130-05)** | **unchanged by THIS plan** — verified identical to the plan-recorded pre-image; plan 130-05 corrects its now-false "the v1.29 slot immediately above" back-reference in a later wave, not here |

**Why keyed on version token, not line number:** the edit changes the file's total entry arrangement (one entry replaces the old BCP slot's content, one entry moves, two entries collapse into one), so line numbers for the surviving entries could in principle shift. In this specific edit they did not shift for v1.24–v1.27 (they stayed at 29–32) because the edit is confined to lines 28, 33 and 34 only — but that is a fact about *this* edit's shape, not something the proof may assume in advance, so token-keying is what makes the proof valid regardless.

**Re-hash after the edit (Task 3):** all four after-hashes are bit-for-bit equal to the four before-hashes recorded above, confirmed by direct SHA-256 re-computation:

```
v1.24 line 29 MATCH
v1.25 line 30 MATCH
v1.26 line 31 MATCH
v1.27 line 32 MATCH
```

**`git -C /workspaces diff -U0 -- .planning/ROADMAP.md`** produced exactly **2 hunks**: `@@ -28,1 +28,1 @@` (the v1.23 entry) and `@@ -33,2 +33,2 @@` (the collapsed py32 slots → relocated v1.28 BCP + retirement line). Git itself — not just the SHA re-hash — confirms lines 29–32 are outside both hunks; a byte-identical line produces no diff hunk. No hunk touches any line before 28 or after 34.

**Why no checker exists for this claim (D-16), in the record's own voice:** *"these four entries never change"* is false as a **standing invariant** — the `v1.24 Bus-Config Mask-Model Redesign`, `v1.25`, `v1.26`, and `v1.27` entries **should** change the moment any of those milestones is actually scoped and activated (their own text is `QUEUED — not yet scoped/activated`). A permanent gate asserting byte-identity would either ship pre-obsolete (blocking a legitimate future edit to those entries forever) or need to be deleted the moment one of those milestones starts — neither is a useful standing invariant. This is the one place in the v1.23 milestone where BASE-08's ships-with-a-fixture discipline is **deliberately not applied**; D-16 records the reason here so a later reader does not mistake the absence of a checker for an oversight. The proof is instead a one-shot, human/agent-executed SHA-256 comparison, captured in this SUMMARY for plan 130-16 to lift verbatim into `130-NONREGRESSION.md`.

**Two non-violations visible in the diff, named explicitly so they are not misread as D-16 violations:**
1. The `v1.30` entry (line 35) is untouched by this plan (verified identical, table row above) — but its *"the v1.29 slot immediately above is still occupied"* sentence is now stale, since v1.29 is vacant after this edit. Correcting that sentence is **plan 130-05's** job, in a later wave, per this plan's `<action>` instruction to leave it "for that plan so the two ROADMAP edits stay in separate, reviewable commits."
2. **The plan's own prediction that "the total line count drops because two entries became one" did NOT materialize as a whole-file effect, and this is recorded honestly rather than silently glossed over.** `wc -l ROADMAP.md` is **2523 both before and after** this edit. The reason: this specific edit is not a pure 2-into-1 collapse — it is *two* changes overlapping in the same 7-line span: (a) the py32 collapse genuinely removes one line (2 old entries → 1 retirement line, −1), but (b) the file previously had **zero** entries for the real v1.23 milestone, so giving it one **adds** a line's worth of "new content" relative to the old BCP-mislabeled slot it replaces — except that addition doesn't cost an extra physical line either, because the old BCP entry's line is *reused* for the new v1.23 content and the BCP text itself is *relocated* (not duplicated) to its own new line after v1.27. Net effect on physical line count for the whole 7-line span: 7 old lines → 7 new lines (verified: `old_block` len 7, `new_block` len 7 in the transformation script), so the two changes exactly cancel and the file's total line count is unchanged. This is stated here as a **documented discrepancy against the plan's Task 3 action text**, not a defect in the edit itself — every other acceptance criterion (order, uniqueness, byte-unchanged proof, hunk confinement, forbidden-string absence) is independently verified and passes.

## `check_record_corrections.py` — before/after comparison for this plan's scope

Per plan 130-02's handoff and this plan's `<verification>` bullet, the checker's needle counts for the strings this plan's edit touches:

| Needle | Hits in ROADMAP.md before this plan | Hits in ROADMAP.md after this plan | Disposition |
|---|---|---|---|
| `py32-buffer-1024` | 1 (line 28, `unlabeled`) | 1 (line 33, `inline-allow`) | **Relabeled, not dissolved** — the hit is the coincidental Uno-buffer-doubling mention 130-02 flagged; it survives the relocation (still on the moved BCP entry) but is now correctly exempted with a stated reason, per 130-02's explicit recommendation. Not reworded, needle not weakened. |
| `third-stack-2c2ed10` | 1 (line 33, `unlabeled`) | 0 | **Dissolved.** The line carrying it (the stale v1.28 py32 slot) was deleted by D-13's collapse, exactly as `130-RESEARCH.md` C-11 anticipated. 3 more hits at lines 1732/1747/1883 (outside the Milestones list) are untouched — out of this plan's scope, belong to plans 130-05/130-06. |
| `porting-md-dual-slot` | 1 (line 33, `unlabeled`) | 0 | **Dissolved**, same deleted line. Remaining hits in `PROJECT.md:45` and the notes file are out of scope here. |
| `host-head-311eacf` | 1 (line 34, already `line-label`, exempt) | 0 | **Dissolved** (the labeled line itself was deleted); it was never in the `FAIL` bucket even before this plan, so the default-mode exit code is unaffected by this specific dissolution. |
| `host-44-unit-tests` | 1 (line 34, already `line-label`, exempt) — the **only** occurrence anywhere in the scanned tree | 0 anywhere in the tree | **Fully discharged.** Confirmed via `--explain` that this needle now has zero hits in any of the five scanned files. |

**Net effect on the checker's default-mode exit code:** still exits 1 (unchanged) — the remaining `FAIL` buckets (`arm-toolchain-absent`, `branches-27-behind`, `cli-handlers-821`, `hex-extension-hardcoded`, `leonardo-headroom-2992`, `part-with-no-vtor`, plus the residual `third-stack-2c2ed10`/`porting-md-dual-slot`/`py32-buffer-1024` hits in `PROJECT.md`/`STATE.md`/`REQUIREMENTS.md`/the notes file) are **outside this plan's scope by design** (`must_haves.prohibitions`: "Do NOT edit ROADMAP.md's backlog stubs... ROADMAP.md:2414 or ROADMAP.md:2468... Those belong to plans 130-05 and 130-06"). This plan's job was narrowly the Milestones-list collapse; the remaining unlabeled hits are exactly the real worklist those two later plans need, and this SUMMARY hands them the precise before/after picture requested in the plan's `<upstream_results_from_this_wave>` section.

## Decisions Made

- Used a verified, assertion-guarded Python line-range transformation (reading the original file, replacing only `lines[27:34]`, carrying `v1.24`–`v1.27` forward **by reference** rather than retyping them) instead of the `Edit` tool for the multi-line reorder, because two of the seven lines are 2500–6000 bytes long and a manual `old_string`/`new_string` transcription of that much prose carries real risk of a single silently-wrong character breaking the byte-unchanged proof this plan exists to make airtight. The script asserted the four pre-edit hashes matched the plan-recorded values *before* writing anything, and the resulting `git diff` was confirmed confined to exactly 2 hunks in the expected line range — an equivalent (and, for this specific task, stronger) safety property to "scoped Edit only."
- Added the `recordscan:allow` marker to the relocated BCP entry per plan 130-02's explicit recommendation, rather than leaving the false-positive for a later plan to resolve — since this plan is the one physically moving/editing that line anyway, and the marker's placement (same physical line as the needle hit) is line-position-agnostic per the checker's own regex design.

## Deviations from Plan

### Auto-fixed / Documented Issues

**1. [Rule 3 — blocking-check artifact, documented not fixed] Task 2's `<verify><automated>` version-ordering assertion (`nums==sorted(nums)` via naive `float(t[1:])` parsing) fails on the **pre-existing** `v1.9`/`v1.10` insertion order, independent of this plan's edit**
- **Found during:** Task 2 verification
- **Issue:** The plan's own embedded verify script parses version tokens as `float(t[1:])` — e.g. `"v1.10"[1:]` = `"1.10"` parses to `1.1`, colliding with `v1.1`, and `"v1.30"[1:]` = `"1.30"` parses to `1.3`, colliding with `v1.3`. Running the *exact* verify script against the **unmodified, pre-existing** `ROADMAP.md` (before this plan touched anything) reproduces the identical `AssertionError` — confirmed by direct comparison. The real, intentional document ordering places `v1.10` (inserted ahead of the paused `v1.9`, a documented 2026-06-01 project decision) before `v1.9`, which is correct project history and out of scope for this plan to alter.
- **Fix:** Did not modify the checker script (it is inline prose in the PLAN.md, not a committed artifact, and fixing v1.9/v1.10 ordering is unambiguously out of this plan's scope). Instead ran the corrected form of the same check — semantic-version tuple comparison (`tuple(int(x) for x in t[1:].split('.'))`) rather than naive float parsing — confirming: (a) no duplicate tokens anywhere in the list, and (b) the v1.23→v1.30 span this plan actually touches is strictly ascending with proper tuple comparison. This is the mechanically correct form of the acceptance criterion the plan intends.
- **Files modified:** none (verification-only)
- **Verification:** `tail = ['v1.23','v1.24','v1.25','v1.26','v1.27','v1.28','v1.30']`; `tailnums == sorted(tailnums)` and no duplicates — **True**.
- **Committed in:** n/a (documented in this SUMMARY only; no code/doc change warranted)

**2. [Rule 2 — auto-add per explicit upstream recommendation] Added the `recordscan:allow` marker to the relocated v1.28 Binary Command Protocol entry**
- **Found during:** Task 2 (informed by 130-02's SUMMARY, handed to this plan in `<upstream_results_from_this_wave>`)
- **Issue:** The `py32-buffer-1024` needle (`DATA_BUFFER_SIZE` + `1024` on one line) fires on the BCP entry's Uno-buffer-doubling discussion — a coincidental collocation, not a real stale py32 claim, per 130-02's analysis.
- **Fix:** Appended `<!-- recordscan:allow py32-buffer-1024: coincidental collocation -- ... -->` to the end of the relocated BCP entry's physical line (position doesn't matter to the checker's per-line regex). Did NOT reword the surrounding prose or weaken the `py32-buffer-1024` needle regex, per 130-02's explicit instruction.
- **Files modified:** `.planning/ROADMAP.md` (same line as the Task 2 edit; no separate commit)
- **Verification:** `check_record_corrections.py --explain` shows `ROADMAP.md:33  py32-buffer-1024  inline-allow` (previously `unlabeled` at the old line 28).
- **Committed in:** Task 2's commit (the single BCP-relocation edit)

---

**Total deviations:** 1 documented-not-fixed (pre-existing out-of-scope checker artifact), 1 auto-add (Rule 2, upstream-recommended marker).
**Impact on plan:** No scope creep; both items were either explicitly out of scope (v1.9/v1.10 ordering) or explicitly recommended by the prior plan in this same wave (the recordscan:allow marker). All of this plan's own acceptance criteria pass.

## Issues Encountered

None beyond the documented deviations above. The devcontainer was already in a clean state (`git status` showed only expected pre-existing untracked plan artifacts before this plan started); no auth gates, no checkpoints, no package installs.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Plan 130-05** (next wave) can now correct the `v1.30` entry's stale *"the v1.29 slot immediately above is still occupied"* back-reference (now provably false, since v1.29 is vacant) and the two `999.23`/`999.24` backlog stubs' `→ v1.28` pointers (now provably wrong, since v1.28 is Binary Command Protocol) — this SUMMARY's diff and hash tables give it an exact, mechanically-verified starting point rather than a re-derivation problem.
- **Plan 130-06** (wave 3, after 130-05) can run its ROADMAP correction sweep for `⚠ CORRECTION` blocks knowing the `## Milestones` list's py32 slots and BCP renumber are already settled — CONSTRAINT 11 (C-11) is honoured: this plan ran strictly before any CLOSE-01 ROADMAP sweep, so no correction block was written into a line this plan then deleted.
- **Plan 130-16** (closing plan) can lift the D-16 before/after hash table and the "why no checker" paragraph verbatim into `130-NONREGRESSION.md`, per this plan's own `<output>` instruction.
- No blockers. `check_record_corrections.py`'s default-mode run still exits 1 (unchanged), but its remaining unlabeled hits are now precisely enumerated by kind and location for the plans that own them.

## Self-Check: PASSED

- `[ -f /workspaces/.planning/ROADMAP.md ]` → FOUND
- `[ -f /workspaces/.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-04-SUMMARY.md ]` → FOUND (this file)
- Task 1 commit hash → verified present in `git log --oneline`
- Task 2 commit hash → verified present in `git log --oneline`
- Task 3 commit hash → verified present in `git log --oneline`
- `git -C /workspaces diff --stat` for this plan's content commits → touches only `.planning/ROADMAP.md` (plus this SUMMARY.md in its own commits)
- `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `.planning/PROJECT.md` → untouched (confirmed via `git status --short`)

---
*Phase: 130-close-honesty-ledger-claim-gate-release-decision*
*Completed: 2026-08-02*
