# 146 Replan Brief — plans 05…13

> **Filename provenance (added 2026-08-18 by `/gsd-complete-milestone`).** This file was authored as
> `146-REPLAN-BRIEF.md` and renamed to `146-RESCOPE-BRIEF.md` at milestone close. Reason: GSD's plan
> scanner (`bin/lib/plan-scan.cjs`, `isRootPlanFile`) falls back to a loose `/PLAN/i` match on any
> `*.md` in a phase directory, so the substring "REPLAN" made this brief count as a **14th plan** in
> Phase 146 — which has 13. That phantom plan drove `implementation_complete: false`, and with it a
> `phase_complete: false` for a phase that is closed, plus `completed_phases: 8` / `percent: 89` in
> `STATE.md`. No file in this project referenced this brief by name, so the rename changes no
> citation. The scanner behaviour is a real upstream defect and is filed as a todo, not fixed here.
> Content below is byte-unchanged from the original.

**Created:** 2026-08-17 · **Author:** `/gsd-execute-phase 146` orchestrator · **Trigger:** operator decision

Execution of Phase 146 halted at **4 of 13** plans. Plans `146-01`…`146-04` are complete, committed, and
Self-Check PASSED — **nothing about them is being reverted or re-planned.** Plans `146-05`…`146-13` are being
re-planned leaner. This brief is the contract for that replan.

---

## 1. Why the replan

The planner's *emission* is sound. Measured across all 13 plan files on disk:

| Check | Result |
|---|---|
| `bash -n` over every `<automated>` leg | **0 / 216** failures |
| HTML-entity corruption (`&amp;&amp;` — the recorded prior defect) | **0** — did not recur |
| `/tmp/gsd146` redirects missing their `mkdir` | **0** — 57/57 carry it (fix `6560f9a8` held) |
| cwd-unanchored legs | **0 / 216** — all 23 relative `git -C firestarter` legs are preceded by `cd /workspaces` |
| `verify.key-links` resolution | verified for every plan checked |

The defect is **specification, not emission**, in two forms:

1. **Acceptance criteria unreachable by construction.** `146-03` hit two in a single task: a negative control
   demanding *non-zero* `firestarter` porcelain while the same task mandated an out-of-tree build, and a gate
   tally that only prints on the success path being demanded while that gate was RED. `146-02` hit a leg it
   could satisfy only by re-anchoring the path.
2. **Weight.** 4,779 plan lines / 456 KB for a documentation-only close phase — ~370 lines per plan and
   **216 verify legs across 34 tasks** (6.4 per task). Executors consumed 200–215K tokens each.

`gsd-plan-checker` passed all of the above at **ZERO blockers and ZERO warnings**, so its verification does not
catch unreachable criteria. Do not treat a checker pass as evidence of reachability.

Three of the four executors had to *record a plan defect rather than satisfy it*. Each did so correctly — no
false green landed. That is the behaviour the replan must preserve while removing the need for it.

---

## 2. Hard constraints on the new plans

**Budget**
- **≤150 lines** per `PLAN.md`.
- **≤3 `<automated>` legs per task.** Prefer one decisive leg over three corroborating ones.
- Total across all nine plans should land near **~1,200 lines**, versus ~3,400 today.

**Reachability — the defect class being eliminated**
- Every `<acceptance_criteria>` entry must be satisfiable *given the other constraints stated in the same
  task*. Before writing a criterion, check it against that task's own mandates.
- Never demand output from a branch that cannot execute in the state the task creates.
- Never demand a state the same task forbids (the `146-03` porcelain contradiction).
- If a value is only obtainable on a gate's success path, do not demand it while that gate is expected RED —
  name the alternative oracle instead.

**Leg hygiene (all measured live this phase)**
- Assert the **printed integer**, never `grep`'s exit status — `grep -c` exits 1 on a zero count, so a
  "must be 0" leg arrives with rc=1 and the statuses invert across an edit.
- Absolute repo paths: `git -C /workspaces/firestarter`, never `git -C firestarter`. The relative form passes
  **vacuously** from the wrong cwd (git fails; `wc -l` counts zero lines of output).
- `mkdir -p` before any redirect into a scratch directory.
- Cite forbidden or false text by `file:line` — **never reproduce the literal**. The self-reference trap has
  fired **five** times this phase; every plan that assumed a prose edit was inert was wrong.

---

## 3. What must not change

- **Decisions D-01…D-14** in `146-CONTEXT.md`, plus operator decisions **OD-A** (gh#15 box 9 graded on an
  observed ARM build) and **OD-B** (the eighth correction). Still binding.
- **Wave and dependency structure**, exactly as-is:
  `05, 06` (w2) → `07, 08` (w3) → `09, 10` (w4) → `11` (w5) → `12` (w6) → `13` (w7).
- **Frontmatter keys**: `phase, plan, type, wave, depends_on, commits_land_in, reads_repos, files_modified,`
  `autonomous, requirements, must_haves`. `commits_land_in` and `reads_repos` are load-bearing — the
  orchestrator uses them to decide worktree isolation, and worktrees leave submodules empty.
- **Requirement ticking**: `146-13` is the **only** plan permitted to tick CLOSE-01…CLOSE-05. Every other plan
  leaves all five rows `Pending` in both `REQUIREMENTS.md` and the ROADMAP coverage table.
- **`146-12` and `146-13` stay `autonomous: false`** with blocking operator gates. `146-12`: freeze → blocking
  wording review → blocking authorization → **one** gh issue comment → byte-verify. `146-13`: blocking gate
  before any tick. Both read and record the **resolved** auto-mode value and halt on any non-`false` value.
  Resolved value for this run: **`false`**.
- **D-01 no-push boundary**: no push, merge, tag, or workflow dispatch anywhere in the phase.

---

## 4. Measured starting state (waves 1–2) — plan against this, not against the original research

**Artifacts that now exist** in the phase directory: `146-CITATIONS.md` (§§0–3), `146-check-claims.py`,
`146-check-close03-docs.py`, `146-DOC-CHECK-RECORD.md`, `146-ARM-BUILD-RECORD.md`, `arm-build/`,
`fixtures/` (5 files), `test_check_claims_v131.py`, and SUMMARYs for 01–04.

**Gate states, as measured at HEAD:**

| Gate | State | Note |
|---|---|---|
| `146-check-claims.py` | **RED**, fail-closed | 4 of 5 ship targets not authored yet: `146-LEDGER.md`, `146-CORRECTIONS.md`, `146-GH15-RECONCILIATION.md`, both release bodies. Working as designed. |
| `test_check_claims_v131.py` | **14 green, leg 9 RED** | Leg 9 is the fail-closed missing-target branch. Suite exits 0 with only leg 9 deselected; no `xfail`/`skip` in the file. Leg 9's GREEN belongs to `146-11`. |
| `146-check-close03-docs.py` | **RED** | 7 unsatisfied topics across 4/4 targets; `program-vcc-ceiling` absent from all four. |
| `check_record_corrections.py` (Phase 130) | **PASS, rc=0** | **See the correction below — this is not what plans 01–04 reported.** |

**CORRECTED 2026-08-17 — this section was wrong when first written.** The Phase 130 record-gate RED at
`.planning/STATE.md:11` is **already closed**, but *not* by `146-04` as originally stated here. It was closed by
**`91a06604`**, a commit made by an interrupted `146-05` executor, whose own message records the flip
(`rc=1 -> rc=0`, `unlabeled 1 -> 0`).

Settled by testing the needle `(?=.*arm-none-eabi-gcc)(?=.*absent)` — `check_record_corrections.py:261-263` — against
each historical `STATE.md` blob: it sits on **line 11** at `d2c212f1`, at `083e4e5f`, and at every `146-04` commit
through its last (`0accb44e`), and is **gone from line 11 at `91a06604`**. A second, exempt match at line 1140
persists throughout, which is why the file scans rc=0 with it still present.

Consequences of the error, all corrected in the replanned `146-05`:
- `146-04-SUMMARY.md`'s report that the gate was still RED after its own write is **ACCURATE**. The first version of
  this brief called it an inaccurate under-claim; that accusation was unfounded and must not be recorded anywhere.
- `146-05` is **partially executed**, not unstarted. Two commits landed before the interrupt and are reachable from
  HEAD: `91a06604` (the record-gate correction, `STATE.md`) and `8df5e564` (the two ROADMAP correction blocks at
  `:169` and `:396` plus the 143 D-01 charter discharge at `:394`). `grep -c 'CORRECTION (Phase 146'` is already **2**
  in `ROADMAP.md` and **0** in both `PROJECT.md` and `REQUIREMENTS.md`.
- **There is no `146-05-SUMMARY.md`.** Commits without a SUMMARY is the safe-resume anomaly condition; the replanned
  `146-05` resolves it by *verifying* the landed half and re-landing none of it.
- The committed text already cites register rows **C-1**, **C-2** and **C-9** in `146-CORRECTIONS.md`, and that file
  **does not exist yet**. Those citations dangle until `146-05` Task 3 writes it; the register must carry those ids.

The substantive point stands: the sentence asserted the ARM toolchain was absent, and `146-03` measured that
**false**. The record must say so.

**Other measured facts:**
- ARM: **GREEN arm observed** — `py32f071` compiled, 44/44 ninja edges, one `firestarter_py32f071.hex` at
  **78769 B**, SDK resolved to `0ed2f4b4`. The **delta-not-CI-parity** caveat is mandatory and travels with the
  result: four bare-metal library packages arrived as automatic apt dependencies. **No `999.32` stub was
  created** — the RED arm did not fire.
- Three citation forms measured safe against the claim gate by `146-04`: the hyphenated form of a two-word
  forbidden phrase, a fixture filename, and a pattern written as its own regex. The bare hyphenated pattern
  **label id** does hit. Re-scan rather than trusting this.
- Working trees: `firestarter` porcelain **0** lines, `firestarter_app` **7** (pre-existing untracked). Both
  sub-repo suites assert whole-repo porcelain.
- `F-140-07` is already corrected in place in `firestarter/doc/PROTOCOLS.md` §1.5 by `140-06` — only the public
  gh#15 half plus four `.planning` sites remain owed.
- `143 D-01`'s PROJECT.md half has **no false-statement site**: a negative grep for the clause returns zero
  hits in `PROJECT.md`. It is a ROADMAP-only correction, and the non-finding is itself recorded. Wording for
  this is preserved out-of-tree at `146-05-orphaned-PROJECT-edit.diff` (from the interrupted executor) and may
  be reused — but it cited register rows in a file that did not exist, so any reuse must land the register
  first.

**Broken tooling — do not call:**
- `state.advance-plan` — reads the phase number `146` as a plan number, returns `{"advanced": false,
  "reason": "last_plan"}` with plans still to run, flips `status: executing → verifying`, and clobbers
  `last_activity_desc`.
- `state.begin-phase` / `state.planned-phase` — clobber `last_activity_desc` and regress `percent`.
- Any `gsd-tools query commit` — it stages **all** changes.
- `roadmap.update-plan-progress <phase>` has behaved correctly four times (one line, its own checkbox), but
  snapshot and diff it anyway.

Hand-edit shared files, always snapshot → change → `diff`.
