---
title: 206-SESSION-COST — SESS-02's bench figure for the session lease, the connect-census derivation beside it, and the pre-registered keep-or-revert threshold
date: 2026-09-23
context: >
  Phase 206 plan 03 landed `EpromOperator.lease()` (commit `3853b55`) default-off, behind one call
  site in `cli_handlers.dev_test`, with its revert rehearsed clean and its exact revert target
  recorded in `206-03-SUMMARY.md`. SESS-02 is the requirement no tier below the physical one can
  answer: whether the lease is worth keeping, measured, not derived. This document is created in
  plan 04's task 1 — before the bench task runs — following `205-SESSION-COST.md`'s section
  structure and its rule that a measured figure and a derived figure are never blended into one
  number.
---

# 206-SESSION-COST — SESS-02's measured saving, the derivation beside it, and the keep-or-revert application

## 1. What is being counted

Before this plan's bench task, a `dev test <chip>` plan opens and tears down a serial link on
**every** `EpromOperator` call — one `_setup_operation` → `find_and_connect` → `_disconnect_programmer`
round trip per call, each one closing the port on exit, which de-asserts DTR and resets the attached
Leonardo (`reference_held_rail_dtr_reset_hold_script`, cited at `206-RESEARCH.md` Q5). Plan 03's
`EpromOperator.lease()` (commit `3853b55`, default off) holds one validated link open across every
`EpromOperator` call inside `cli_handlers.dev_test`'s `run_plan(...)` for the duration of the call,
instead of one open-and-teardown per call.

**This document counts the wall-clock a complete `dev test <chip>` plan saves when the lease is
active, against the identical plan with the lease reverted, on the same part, the same board, the
same session, no reflash or reseat between arms.** `HardwareManager`'s own connects (the pre-plan
identity read, the voltage sampler inside each write step) are a **different class with its own
connects** and were deliberately left outside the lease (Fork F5, `206-RESEARCH.md`); they are not
collapsed by this change and their cost is unaffected either way. What this document measures is
therefore a **lower bound** on what a wider lease (Fork F5 option (b)) could save, not the full
connect-term total a plan opens.

`dev test` writes to the chip on every run and energizes VPP and VPE (`cli_handlers.py:2879`,
cited at `206-RESEARCH.md` Q6); every run counted here is a genuine, destructive bench run, never
a dry run or a mock.

## 2. The measured wall-clock (both arms)

**pending** — this section is filled by plan 04's task 3, after the operator-initiated bench
checkpoint (task 2) reports its numbers. The table shape is seeded here so the bench task fills a
form rather than inventing a layout under time pressure, following `205-SESSION-COST.md` §2's
method: `time` around the whole `firestarter dev test <chip>` subprocess, an ODD N of at least 3
per arm, alternating nothing — one arm run to completion, then the other, same part, same board, no
reflash or reseat between them, figures to three decimal places.

**Cold arm (lease commit `3853b55` reverted, i.e. `d723cf7` + `3853b55` both reverted per § 5's
corrected recipe — see below):**

| Run | Wall clock |
|---|---|
| 1 | pending |
| 2 | pending |
| 3 | pending |
| **Median** | pending |
| Min | pending |
| Max | pending |

**Leased arm (lease commit `3853b55` present, at its current HEAD):**

| Run | Wall clock |
|---|---|
| 1 | pending |
| 2 | pending |
| 3 | pending |
| **Median** | pending |
| Min | pending |
| Max | pending |

**Re-anchored connect-cost median (this session, this rig):** pending — `firestarter dev ...
--mode connect-cost --samples 10` against the confirmed port, per `206-RESEARCH.md` Q6, replacing
a citation of the 2026-09-04 Phase 203 figure with a current one.

**Part, shield revision, and port identity confirmed by the operator:** pending — asked at the
bench, never assumed. `hw_revision` cannot distinguish the three shields the operator owns
(`user_shield_revisions`); `ttyACM*` numbers shuffle across a replug
(`feedback_verify_port_identity_each_task`).

**Per-step verdict diff (clause 3):** pending — one run in each arm, per-step verdict and status
table captured and diffed.

## 3. The derivation over the connect census (labelled as a derivation, not a measurement)

**Connect census — structure VERIFIED by reading each call site, totals DERIVED, never measured**
(`206-RESEARCH.md` Q5):

| Where | Connects | Class | Inside the lease? |
|---|---|---|---|
| `read_programmer_identity` (pre-plan) | 1 | `HardwareManager` | No (Fork F5) |
| id step | 1 | `EpromOperator` | Yes |
| read step | `runs` (= 3) | `EpromOperator` | Yes |
| write step, per cycle | 5–6 (sampler before 2 + `write_eprom` 1 + guard read 0–1 + sampler after 2) | mixed | Sampler (4) no; `write_eprom`/guard read yes |
| verify step, per cycle | 1, +1 on the final cycle if the step failed | `EpromOperator` | Yes |
| erase step, per cycle | 1 | `EpromOperator` | Yes |
| blank-check step, per cycle | 1 | `EpromOperator` | Yes |

**Derived total for an erasable full-device part at `runs=3` (this phase's default): ~29–33
connects.** This is a re-scaling of the validated structural model in
`.planning/notes/dev-test-sequence-cost-model.md`, which reports 22 (sst27sf512-class), 32
(at28c256, SDP leg), 18 (w29c040) connects **at `runs=2`**, validated 13-predicted/13-observed on
a `--fast` run — **that note's connect counts are cited for their structure only; its verify
mechanics and its absolute seconds are stale: verify moved to the host in Phase 202, its first
waste pattern was closed in Phase 177, and every one of its figures is modelled at `runs=2` while
the default is now three, so its totals are re-scaled here, never quoted directly.**

**The D-05/Fork-F5 cap: ~12 of those ~29–33 connects survive the lease.** The sampler
(`sample_vpp_mv` + `sample_vpe_mv`, `HardwareManager`) costs 4 connects per write step and stays
outside the lease by design (Fork F5, `206-RESEARCH.md`); at three cycles that is **12 connects per
plan, unaffected either way.** Plus the one pre-plan identity read, also `HardwareManager`, also
outside the lease. **So roughly a third to just over a third of a plan's connects are outside the
lease, and the measured saving must be read against that cap** — a plan that opens ~30 connects
today cannot show a saving equivalent to removing all 30 of them; at most ~17–20 connects
(`EpromOperator`'s own: id, read×3, write/verify/erase/blank-check per cycle) are collapsible.

**Derived connect-term saving, at the Leonardo-class connect median.** `EpromOperator.measure_connect_cost`
(reached as `firestarter dev ... --mode connect-cost --samples N`) produced a cited **2.607 s**
Leonardo-class median (`203-SESSION-COST.md` §2, N=10, port pinned, measured 2026-09-04) — **this
figure is re-anchored on the day of the bench run in § 2 above rather than cited as current here.**
Applying the ~17–20 collapsible-connect estimate to that median: **~44–52 s of connect-term
overhead is the theoretical ceiling on what the lease can remove from a plan**, out of a modelled
plan total in the ~100–150 s range at `runs=3` (re-scaled from the cost model's `runs=2` ~121.8 s
figure, itself citing stale absolute seconds per the caveat above).

**Sanity check, cited from `205-SESSION-COST.md` § 5:** that document pre-registers this phase's
own expectation — *"the saving SESS-01 should expect to measure is closer to the derivation's
~2.6s than to this document's ~10.6s, because most of [the] measured figure is read traffic that a
leased session does not eliminate."* The lease removes **connect overhead only**; it does not
touch read/write/verify/blank-check payload traffic, which is unaffected either way. A measured
saving nearer the connect-term derivation above than to the plan's whole read/write traffic budget
is therefore the expected shape of the result, not a surprise to explain away.

**No figure in this section blends a measured term with a derived one.** Every row above is
derived; § 2 is where measured figures land, and § 5's provenance table keeps the two apart term by
term.

## 4. Explicit non-measurement statement — what this record does NOT claim

**pending** — stubbed here for plan 04's task 3 to complete once the bench arm is measured. Per
`205-SESSION-COST.md` § 6's discipline, this section must name: which part and shield revision were
actually measured and which families and board classes therefore remain uncovered; that
`HardwareManager`'s connects (the pre-plan identity read, the sampler) stayed outside the lease, so
the measured figure is a lower bound on what a wider lease (Fork F5 option (b)) could save, not a
projection of it; and that this document supersedes nothing in `205-SESSION-COST.md` or
`203-SESSION-COST.md` — their own measured connect medians are cited here, not re-measured.

## 5. The keep-or-revert application (D-07)

**D-07, pre-registered in `206-04-PLAN.md` before the bench task ran, verbatim.** The lease is
KEPT only if all three clauses hold on the reference part and board class:

1. it removes **at least 15.0 percent** of the plan's median wall clock;
2. **and** the removed time is **at least five times** the measurement's own spread (max minus
   min, taken over the wider of the two arms);
3. **and** no step's verdict differs from the pre-lease arm for the same physical outcome.

Below any clause, the single lease commit is reverted and the number is recorded. Rationale for 15
percent: the derived connect-term saving (§ 3 above, ~44–52 s theoretical ceiling against a
~100–150 s modelled plan) is far above it, so a measured result *below* 15 percent is itself
evidence the lease is not doing what it was built to do rather than evidence that 15 percent was
too demanding. Clause 2 stops a noisy measurement from deciding a structural question. Clause 3
makes DEVTEST-03 a gate on SESS-01 rather than a separate concern — a faster run that changed a
verdict has not paid, it has cost.

**Exact boundary, stated one step either side.** At **exactly 15.0 percent** (the rounded value,
per the arithmetic contract below) the lease is **KEPT**. At **14.9 percent** it is **REVERTED**.
Clause 2's "at least five times the spread" is **inclusive at exactly five times** — a removed
time equal to precisely 5.000× the spread passes clause 2.

**The arithmetic contract, stated before the number exists:**

- Every individual wall-clock figure, both medians, and both spreads are recorded to **three
  decimal places**, matching `205-SESSION-COST.md` and `203-SESSION-COST.md`.
- Each arm runs an **odd N of at least 3**, so the median is an **observed value** (the middle
  run), never the average of two adjacent runs.
- The percentage is computed as `(cold_median − leased_median) / cold_median × 100`, using the
  two medians only (never a mean of individual runs).
- The percentage is **rounded half-up to one decimal place** — a value ending exactly in `.05`
  rounds to the next tenth up (e.g. `14.95` rounds to `15.0`, not down to `14.9`). This is the
  stated tie-break: round-half-up, away from the boundary that would otherwise leave a borderline
  result undecided.
- Clause 1's comparison against `15.0` is made **on the rounded value**, never on the unrounded
  percentage. A measurement that rounds to `15.0` clears clause 1; one that rounds to `14.9` does
  not.
- Clause 2's spread is `max − min` over whichever arm has the wider spread of the two, also to
  three decimal places, and the "five times" comparison is made on the unrounded removed-time
  figure (cold median minus leased median) against that spread.

A measurement protocol that leaves its own rounding rule unstated is how a borderline result
becomes an argument; this contract exists so the decision was already made before the number
existed.

**Corrected revert recipe — supersedes the single-sha instruction in `206-03-SUMMARY.md`.**
`206-03-SUMMARY.md`'s "THE LEASE REVERT TARGET" section names commit `3853b55` alone as the
revert target, rehearsed clean via `git revert --no-commit 3853b55` — **but that rehearsal was
performed BEFORE commit `d723cf7` (the test-infrastructure catch-up commit, landed as part of the
same plan 03) existed.** `d723cf7` modifies `tests/test_session_lease.py`, which a revert of
`3853b55` alone now wants to delete, so a plain `git revert 3853b55` on the current tree
**conflicts** (modify/delete on `tests/test_session_lease.py`).

The corrected, current-HEAD recipe, re-measured against `firestarter_app@d723cf7` (this phase's
present HEAD) on 2026-09-23:

- `git revert --no-commit 3853b55` alone → **CONFLICT** (modify/delete on
  `tests/test_session_lease.py`). Do not use.
- `git revert --no-commit d723cf7 3853b55` (in that order — the follow-up commit first, then the
  lease commit) → **applies with zero conflicts**. The resulting tree runs **2357 passed, 0
  failed** on `.venv311`. `fa6c8e8` (the permanent `setup_command` extraction, kept regardless of
  the outcome per `206-RESEARCH.md` Q7's "Commit A") is correctly retained — it is never part of
  either revert.

**If the outcome (§ this document reaches once § 2 is measured) requires a revert, this is the
recipe task 3 uses: `git revert d723cf7 3853b55`, in that order, as one action inside
`firestarter_app` on `v1.41-verification-to-host`.** This correction is recorded here — in the
plan's own session-cost record, not only in a later SUMMARY — precisely so the stale single-sha
instruction is not the standing reference for anyone reverting `3853b55` after this document is
written.

*Provenance of this correction:* re-measured and reported by the orchestrator dispatching this
plan (2026-09-23, against `firestarter_app@d723cf7`, tree restored clean afterward); not
independently re-rehearsed inside this executor session, whose sandbox denies the destructive git
operations (`git revert --no-commit` + `git reset --hard`) that a from-scratch rehearsal would
require. The orchestrator's report is treated as authoritative here because it is the same class of
mechanical, machine-checkable claim (`git revert --no-commit` exit status plus a full pytest run)
that `206-03-SUMMARY.md`'s own rehearsal used, and because the underlying facts — `d723cf7` touches
`tests/test_session_lease.py`, and a revert of `3853b55` alone wants to delete that same file — are
independently visible from `git show --name-only d723cf7` and `git show --name-only 3853b55`
without running the revert itself.

**§ 5's outcome — filled by plan 04's task 3 once § 2 is measured:** pending. This is where the
three clauses above are evaluated against the measured numbers, with computed values and a
pass-or-fail verdict for each, and where the kept-or-reverted action is recorded.

## Provenance table

| Term | Value | Measured or derived | Source |
|---|---|---|---|
| Leonardo-class connect median (cited, 2026-09-04) | 2.607 s (min 2.606s, max 2.676s, N=10) | measured, cited from Phase 203 | `203-SESSION-COST.md` §2, `176-MEASUREMENT.md` §4b |
| Leonardo-class connect median (re-anchored, this session) | pending | measured (to be re-anchored) | § 2 above, `EpromOperator.measure_connect_cost` |
| Connect census (structure) | see § 3 table | derived (structure verified by reading call sites) | `206-RESEARCH.md` Q5 |
| Derived total connects per plan, `runs=3` | ~29–33 | derived (re-scaled from `runs=2`) | this document § 3, `.planning/notes/dev-test-sequence-cost-model.md` (stale absolute seconds, connect counts only) |
| Connects surviving the lease (`HardwareManager`, D-05/F5) | ~12 (+1 pre-plan) | derived | this document § 3, `206-RESEARCH.md` Q5 Fork F5 |
| Derived connect-term saving ceiling, Leonardo-class | ~44–52 s | derived | this document § 3 |
| Cold-arm plan median (this rig, this part) | pending | measured | this document § 2 |
| Leased-arm plan median (this rig, this part) | pending | measured | this document § 2 |
| Measured saving (cold − leased) | pending | measured | this document § 2, § 5 |
| Measured saving, percent of cold median, rounded half-up | pending | measured (computed from two measured medians) | this document § 5 |
| Lease revert target — corrected recipe | `git revert d723cf7 3853b55` | derived (mechanical git-history fact; re-measured by the orchestrator, see § 5) | this document § 5, `206-03-SUMMARY.md` (superseded single-sha instruction), orchestrator finding 2026-09-23 |
| SESS-02 status | pending | n/a | this document § 5, `.planning/REQUIREMENTS.md` |

---
*Phase: 206-dev-test-keeps-its-fidelity-on-one-session*
*Written: 2026-09-23*
