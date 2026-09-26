---
phase: 145-bench-validation
plan: 08
subsystem: bench-validation
tags: [bench, w27c512, 0x07, leonardo, d-10, d-14, verdict, record-close]
status: complete
requires:
  - "145-07 Gate 3 run (the recorded --pulse-us 4688 measurement this plan verdicts)"
  - "145-06 Gate 2 closure (VALIDATED, 3/3 on both oracles)"
  - "145-02 Gate 0 BENCH-02/BENCH-03 dispositions"
provides:
  - "145-BENCH-LOG.md closed: FINAL Gate 3 verdict, D-10 both halves, Not measured, carry-forwards, phase VERDICT, session-end line"
  - "SHA256SUMS.txt completed to 50 rows covering every produced binary"
  - "Post-bench tripwire result and end-of-phase BENCH-03 re-confirmation"
affects:
  - "145-09 (the requirement flip this record is the evidence for)"
  - "Phase 146 (the honesty ledger will cite this record's verdict and boundaries)"
tech-stack:
  added: []
  patterns:
    - "Two-way discharge (machine + operator) with the contradiction stated, not reconciled"
    - "Broken acceptance locators replaced with negative controls, substitution recorded"
key-files:
  created:
    - .planning/phases/145-bench-validation/145-08-SUMMARY.md
  modified:
    - .planning/phases/145-bench-validation/145-BENCH-LOG.md
    - .planning/phases/145-bench-validation/SHA256SUMS.txt
    - .planning/phases/145-bench-validation/logs/eyeson_rerun_pulse4688.operator_paste.log
decisions:
  - "D-10's eyes-on half recorded as COLLECTED but row 27's smooth-vs-end-burst discriminator recorded as skipped-with-reason -- the operator's four words contain neither term"
  - "The eyes-on re-run declared OBSERVATIONAL ONLY; Gate 3's measurement stays 145-07's, so the eyes-on half cannot have been fitted to a fresh count"
  - "The MAIN write bar never reaching 100% recorded as a new finding, cosmetic/UX only, carried forward with no v1.31 owner (D-16 forbids the fix here)"
  - "Three acceptance locators remade with negative controls rather than reshaping evidence to satisfy them"
  - "ROADMAP's 145-08 checkbox ticked by hand rather than by the roadmap verb, to avoid the whole-file reformat blast radius"
metrics:
  duration_minutes: 54
  completed: 2026-08-17
  tasks: 3
  commits: 4
  files_changed: 4
---

# Phase 145 Plan 08: Close the Record Summary

Closed `145-BENCH-LOG.md` with D-10's eyes-on half captured verbatim, a new never-reaches-100% progress-bar finding surfaced by that half, the FINAL Gate 3 verdict, and a phase VERDICT answering all four ROADMAP criteria in D-14's vocabulary — with 16 un-taken readings named and 12 carry-forwards, 10 of them with `no v1.31 owner`.

## What was built

Three commits of record content plus a metadata commit:

| Task | What | Commit |
|---|---|---|
| 1 | D-10 eyes-on half, the 99% bar finding, the stated contradiction, the third oracle, the FINAL Gate 3 verdict | `f2b37779` |
| 2 | Not measured (16 rows), carry-forward hand-offs (12 rows), the phase VERDICT | `3fa2cd75` |
| 3 | Post-bench tripwire, end-of-phase BENCH-03 re-confirmation, 51-row artifact inventory, D-16 closing assertion | `82912a0c` |

## The operator's eyes-on statement — verbatim

Their **complete** free-text description, quoted exactly as typed, uncleaned:

> It looked ok

That is the entirety of their prose — four words. They then pasted the full terminal transcript.

**Provenance.** `145-07`'s Gate 3 run executed inside a background agent, so the operator had no live terminal. Offered "record as NOT COLLECTED" or a foreground re-run, they **selected the re-run and executed it themselves** in their own terminal. The full artifact is `logs/eyeson_rerun_pulse4688.operator_paste.log`, committed and hashed.

**The re-run is OBSERVATIONAL ONLY.** Gate 3's recorded measurement remains `145-07`'s run (`logs/pulse4688.stderr.raw`, `logs/frames_pulse4688.txt`). Nothing was re-measured or re-extracted, so the eyes-on half cannot have been fitted to a fresh count.

**What the operator did NOT say, recorded as such:** no per-block movement count, no characterisation of the motion as smooth or stepped, no comment on the bar percentage. Everything else in that section is orchestrator-derived from the pasted text and labelled as derived.

## The `Gate 3 verdict:` line, verbatim

> **Gate 3 verdict (resumed session — FINAL): VALIDATED, with two named skipped-with-reason items.**

Its six named elements: run completion at exit 0 / `Write to W27C512 successful (30.94s).` — `validated`; Claim B HOLDS on 4/4 blocks — `validated`; `--pulse-us` on silicon — `validated`; the above-4687 µs budget-mechanism proof — `validated` with its non-claim intact; A1 — `validated` as a derived per-BYTE upper bound, with the multi-pulse regime `skipped-with-reason`; the eyes-on half — `validated` as collected, with row 27's discriminator `skipped-with-reason`.

## The phase `VERDICT:` sentence, verbatim

> **Phase 145 — Bench Validation: `validated`**, on all four ROADMAP success criteria — criterion 1 `validated`, criterion 2 `skipped-with-reason` (AM27C020 named), criterion 3 `skipped-with-reason` (M2716 and M2732 named), criterion 4 `validated` at Gate 0 and re-confirmed at the tip.

All four ROADMAP criteria are quoted **verbatim** in the record (verified programmatically after unwrapping the blockquotes).

## The D-10 contradiction — stated, not reconciled

**Operator impression:** "It looked ok". **Artifact:** the bar terminated at **99.02 %** on that run and short of 100 % on all five other writes this phase. Neither side is suppressed and they are not massaged into agreement. A bar stopping one frame short is not something a casual observer would flag — which is the argument **for** requiring both halves, not against the operator.

## NEW FINDING — the MAIN write bar never reaches 100 %

Re-verified independently from the raw captures (`tr '\r' '\n' | grep bytes | tail -1`) rather than taken on trust:

| Run | Final bar | Bytes | % |
|---|---|---|---|
| Gate 3 required run (145-07) | `0x0fd8/0x1000` | 4056/4096 | 99.02 |
| Gate 3 eyes-on re-run | `0x0fd8/0x1000` | 4056/4096 | 99.02 |
| **Gate 3 companion DB-pulse run** | `0x0eb0/0x1000` | 3760/4096 | **91.80** |
| Gate 2 cycle 1 | `0xfeb0/0x10000` | 65200/65536 | 99.49 |
| Gate 2 cycle 2 | `0xfeb3/0x10000` | 65203/65536 | 99.50 |
| Gate 2 cycle 3 | `0xfeb0/0x10000` | 65200/65536 | 99.49 |

**Divergence from the briefed figures, recorded not applied silently.** The brief listed **five** writes at ~99 %. Re-verification found a **sixth** — the companion database-pulse run at **91.80 %**. That sixth point is what proves the mechanism rather than merely restating it.

**Mechanism established:** the final bar value equals the **last firmware progress-frame position exactly**, in all six runs — no final frame is emitted at completion. Fewer frames therefore means a lower final percentage, which is why the DB-pulse run (1 frame/block) stops further back than the 4688 µs run (6 frames/block). The **INIT** blank-check bar **does** reach `0x10000/0x10000` in every capture, so this is MAIN-bar-specific.

**Scope: cosmetic/UX only** — all six writes verified byte-exact, so no correctness claim is affected. **Out of scope to fix here** (D-16). Carried forward with **`no v1.31 owner`**.

## A third oracle for Claim A/B

The operator's paste shows exactly 6 `DATA:` decode lines between each pair of `OK: Request data` boundaries across 4 blocks = **24 frames**, uniform 164-byte step — matching `145-07`'s `intra_block_frames=24` **exactly**, from a separate invocation. These are protocol-decode lines, not tqdm redraws, so it is independent of both the extractor and `145-07`'s `-v` decode. **Corroboration only; it does not change Gate 3's recorded verdict.**

## Carry-forward hand-offs — complete list with owners

| # | Item | Owner |
|---|---|---|
| 1 | A1's per-pulse overhead inside a multi-pulse retry loop | **none — `no v1.31 owner`** |
| 2 | Row 27's "smoothly moving bar, not an end-burst" discriminator | **none — `no v1.31 owner`** |
| 3 | The MAIN write bar never reaching 100 % (new) | **none — `no v1.31 owner`** |
| 4 | Program-window VPP / internal VCC under load (FUT-08 hypothesis) | **none — `no v1.31 owner`** |
| 5 | Root cause of the intermittent single-byte margin failure | **none — `no v1.31 owner`** |
| 6 | `0x08` (AM27C020) bench validation | **none — `no v1.31 owner`** |
| 7 | `0x0B` (M2716/M2732) bench validation | **Phase 79 plan `79-03`** — a real successor, parked, but not in v1.31 |
| 8 | A true-UV `0x07` data point (TMS27C512) | **none — `no v1.31 owner`** |
| 9 | The 6.25 V program-VCC evidence ceiling | **the milestone's accepted debt — not this phase's** |
| 10 | MERGE-05's +96 B leonardo band breach — adjudication | **the operator**, as a milestone requirements judgement |
| 11 | T-145-45 — a threat-register entry asserting a firmware mitigation that does not exist | **none for the fix; Phase 146 may judge the wording** |
| 12 | RQ-4's superseded frames-per-block table | **none — `no v1.31 owner`** |

`grep -c "no v1.31 owner"` over the record returns **30**.

**Inherited from Phase 144:** H6 **DISCHARGED**. H7 **not discharged as clean** — `145-03` answered it green at 26906 B, then the debug session's `ebe9cb3` (27002 B, +96 B) went red underneath the answer.

**D-09's re-seat allowance: UNCONSUMED** — never spent in either session; no re-seat was ever performed.

## Suite results against baselines

| Suite | Result | Baseline | Match |
|---|---|---|---|
| Firmware, full | **314 passed**, 0 failed, 19.62 s | 312 | **no — +2** |
| Host, full | **1590 passed**, 0 failed, 30 snapshots, 244.75 s | not baselined | n/a |
| Host sibling-porcelain subset | **38 passed**, 0 failed | 38 | yes |

Both run with `-o addopts=` cleared so the count line was visible. Firmware porcelain asserted **0** before *and* after both runs.

**The +2 is recorded as a divergence with its cause, not explained away.** Gate 0's 312 was measured against `a594173d`; every post-2026-08-17 run is against `ebe9cb3`, and the debug session's `eb563d2` + `ebe9cb3` changed **13 files under `tests/`** (`+574/-76`), adding two tests. No plan in this phase touched them.

## End-of-phase BENCH-03 against Gate 0

| Leg | Result at the tip | Gate 0 | Identical |
|---|---|---|---|
| merge-base | `4d18b645ab18a2d2465f0f623062e9249eb24132` | same | yes |
| 1 — `chip_database.json` diff | **0 bytes** | 0 | yes |
| 2 — generator-inputs diff | **0 bytes** | 0 | yes |
| 3 — AST write-locus checker | PASS, **exit 0** | same | yes |
| 4a — digest | `3befbaad7bbb…e913479` | same | yes |
| 4b — histogram | **746 total / 736 supported / 9 adapter-required / 1 protocol-not-implemented** | same | yes |
| caveat — benign mentions | **3** | 3 | yes |

Every figure matches exactly; no discrepancy to record. `tools/build_db.py` was **not** invoked.

## Artifact inventory totals

| Check | Result |
|---|---|
| Evidence artifacts | **51 files, 1300110 bytes** (1269.6 KiB) — 5 images+generator, 1 extractor, 4 read-backs, 9 `run_NN.bin`, 31 logs, 1 manifest |
| `sha256sum -c SHA256SUMS.txt` | **exit 0**, **50 OK**, **0 FAILED** |
| `git check-ignore` over every file | **0** — nothing gitignored |
| `git ls-files` vs on-disk | **75 = 75** — nothing untracked |
| Forbidden directory names (`consistency-check-*`, `firestarter-runs/`, `write-cycle-*`) | **0** |

**Manifest history:** 14 rows at plan start → **36 appended** → **50**. The 14 pre-existing rows were verified `OK` before the append and are **byte-identical after** (`head -14` diffs clean). **No cycle 1–3 artifact and neither `write_cycle1_attempt1.*` file was overwritten or re-hashed.**

## Assertions remade (with negative controls)

| # | Broken check | Defect | Replacement |
|---|---|---|---|
| 1 | `grep -A5 -i "eyes-on" \| grep -qv "NOT YET RUN"` | **False GREEN** — `grep -qv` succeeds on any non-matching line, and 8 prose mentions of "eyes-on" pre-existed. Passed against a record with no eyes-on statement in it. | `awk '/^## Operator eyes-on \(D-10\)/,0' \| grep -c -E '^> It looked ok$'` → **1**; deleting the quote → **0** |
| 2 | `grep -A4 "Gate 3 verdict" \| grep -qv "NOT YET RUN"` | **False GREEN** — matched session 1's `NOT REACHED` line and passed before this plan wrote anything | `grep -c -E '^\*\*Gate 3 verdict \(resumed session . FINAL\):'` → **1**; `grep -c -E '^\*\*Gate 3 verdict'` → **2** |
| 3 | `grep -ciE "\binconclusive\b\|\bpartial pass\b"` must be **0** | **Cannot fail for the right reason.** Returns 4, all *denials* of the state (D-14's own taxonomy). Driving it to 0 would mean **deleting the phase's taxonomy statement to satisfy a locator.** | `grep -ciE '\*\*[^*]{0,24}\b(inconclusive\|partial pass)\b[^*]{0,24}\*\*'` → **0** whole-file; injecting an emphasised literal → **1** |
| 3b | (first fix attempt for #3) | **Self-matching grep** — it matched its own negative-control literal quoted in the substitution list, returning 1 | Negative control **described** rather than written in matching form, so the check covers the whole file with nothing excluded |
| 4 | (byte-vs-character) first form of check #1 used `.` to span the heading's em dash | **False RED** — `—` is 3 UTF-8 bytes and this `awk` matches bytes, so the range never opened and it returned 0 against a correct record | Pattern truncated before the em dash |
| 5 | `git diff … -- ROADMAP.md \| grep -c '^[+-][^+-]'` in my own final sweep | **False ZERO** — the diff's `-`/`+` marker collides with the markdown list bullet, so a changed `- [ ] …` line renders as `-- [ ] …` and `[^+-]` rejects it. It reported **0 changed lines** over a file that had genuinely changed. | `git diff --numstat` → **`1 1 .planning/ROADMAP.md`**, plus reading the committed line back with `git show HEAD:…` |

**The brief predicted a sixth process hazard; #5 above is it, and it was mine.** It was caught only because the result (zero ROADMAP changes) contradicted an edit I knew I had made — which is the general lesson: **a check that agrees with what you want is the one to re-derive.**

**No evidence was reshaped to satisfy any locator.** Consequence recorded: documenting substitution #3 raised the plain-word `inconclusive` count from 4 to **11**, which is the honest cost of recording the fix.

## Divergences from the plan and the brief, recorded

1. **The briefed 99%-bar table was incomplete.** Five writes were listed; a **sixth** (the Gate 3 companion DB-pulse run, **91.80 %**) exists and is the one that proves the mechanism. Recorded rather than applied silently.
2. **The plan's Task 2 acceptance criterion demands a zero-line ROADMAP diff**, but the executor's mandated state-update step ticks the plan's own ROADMAP checkbox. **Resolved by scope:** the *prohibition* is on flipping **requirement** checkboxes, and `145-08-PLAN.md`'s plan-progress checkbox is not one. `REQUIREMENTS.md` is **byte-identical** to its pre-plan snapshot and `BENCH-01`/`02`/`03` remain `[ ]`/Pending. The conflict is recorded, not suppressed.
3. **`gsd-tools` state verbs clobbered `last_activity_desc` on every invocation** — twice observed, replacing it with the truncated garbage `145-05 complete. See`. Repaired by hand after the verbs ran, with a snapshot-and-diff proving exactly three intended lines changed.
4. **The `roadmap.update-plan-progress` verb was not used.** Its `_normalizeMd` reformats the whole file and `phase.complete` is known to clobber unrelated phases' `**Plans:**` lines. The single checkbox was hand-edited instead, with a diff proving one changed line.
5. **The plan's `sha256sum -c` criterion assumed the nine `run_NN.bin` files were already hashed.** They were not — 36 of 50 digests were missing. Appended rather than treated as covered.

## What this plan did NOT prove

- **No comparative claim.** No control run exists (D-08); the 22.84 s pre-v1.31 figure is a recorded historical number, not a control.
- **No datasheet-conformance claim**, in either direction — the 6.25 V program-VCC ceiling is unreachable on this shield.
- **Scope is one part, one controller, one shield revision** — W27C512 `0xda08`, `leonardo`, Rev 2.0. Nothing extrapolates. Progress emission is compiled out on `SERIAL_ON_IO`, so nothing here speaks for Uno-class boards.
- **`0x08` and `0x0B` are fixed in the golden trace only, never on a part**; their dispositions are never inferred from `0x07`.
- **Gate 2 and Gate 3 both ran on a build carrying MERGE-05's open +96 B breach**, deliberately not adjudicated.
- **The single-byte margin failure is mitigated, not explained** — ~17 clean cycles is not a root cause.
- **No independent host-side SHA compare over either Gate 3 write**; no BENCH-01 evidence rests on that gate.
- **No requirement checkbox was flipped** — `145-09` owns that behind its own operator gate.

## Operator gates

The eyes-on half was **already collected** before this plan ran, so Task 1's gate was not re-presented. **No other human-verify gate was reached**, and none was self-approved. `autonomous: false`; no `AskUserQuestion` capability was available, so any gate reached would have been handed back.

## Self-Check: PASSED

All claimed files exist and all claimed commits are in `git log`.
