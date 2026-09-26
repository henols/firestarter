---
title: gh#9 was already discharged eight days before REPLY-07 was filed, and nothing caught it — plus the Phase 187 reply ledger
date: 2026-09-12
context: v1.37 Phase 187, REPLY-01 through REPLY-07 — measured against the live henols/firestarter_prom
  API in Plan 187-12, reconciled against the 187-05 before-capture and the five posting plans'
  own approval/transcript evidence
---

# gh#9 staleness finding, and the Phase 187 reply ledger (D-09)

## 1. The gh#9 staleness finding

**What was claimed, and where.** Five live sites, all under `.planning/`, asserted that gh#9 still
owed a closing reply: `.planning/ROADMAP.md:5409-5411` ("gh#9 remains partially owed... what it
needs is a closing reply or a close-as-done"), `.planning/ROADMAP.md:5424` ("gh#9 still owes a
closing reply"), `.planning/ROADMAP.md:502` (Phase 187 success criterion 4, "gh#9 carries a closing
reply or is closed as done"), and `.planning/REQUIREMENTS.md:118-119` and `:217` — REPLY-07 itself,
filed 2026-09-10, and its traceability row, both reading the same claim.

**What was true.** Phase 173 had already posted an operator-approved body verbatim as
[`#issuecomment-5511487546`](https://github.com/henols/firestarter_prom/issues/9#issuecomment-5511487546)
on **2026-09-02T14:50:37Z**, byte-identical to
`.planning/milestones/v1.35-phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/bodies/173-gh9.md`
(`173-07-SUMMARY.md:115-118`), and then deliberately left gh#9 **open and pinned** via the GraphQL
`pinIssue` mutation. Re-verified live in this plan: the comment's `created_at` and `updated_at`
timestamps are identical (`2026-09-02T14:50:37Z` both), proving it was never edited since; the
`pinnedIssues` GraphQL query returns `totalCount: 1`, naming issue 9, state OPEN, unchanged from the
187-05 before-capture. Nothing about gh#9 changed at any point during Phase 187.

**The window.** REPLY-07 was filed 2026-09-10 — **eight days** after the claim it makes ("gh#9 still
owes a closing reply") became false at 2026-09-02T14:50:37Z. A requirement was promoted directly off
a record that had already been stale for over a week, and nothing in the intervening activation or
planning steps caught it.

**What was repaired, and where** (D-07's five-site repair set, completed by Plan 187-01):

1. `.planning/ROADMAP.md:5409-5411` — the "gh#9 remains partially owed" block, including its heading.
2. `.planning/ROADMAP.md:5424` — "gh#9 still owes a closing reply."
3. `.planning/ROADMAP.md:502` — Phase 187 success criterion 4, amended with the reason recorded.
4. `.planning/REQUIREMENTS.md:118` — REPLY-07 itself, amended and marked Complete with the comment URL.
5. `.planning/REQUIREMENTS.md:217` — the REPLY-07 traceability row, Pending → Complete.

**What was deliberately not repaired, and why:**

- `.planning/ROADMAP.md:967` and `:1224` — both describe gh#9 as "the pinned orientation issue"
  describing a configured end state. Both are **literally true today** and were correctly excluded
  from the repair set rather than widened into.
- Every hit under `.planning/milestones/` — **historical-by-intent**. `.planning/` → `.planning/`
  citations into archived milestone material are never repaired; doing so would destroy the record
  of what was believed at the time, which is precisely the evidence this finding depends on.
  Re-measured in this plan, using the same command RESEARCH used: `/usr/bin/grep -rn "gh#9"
  .planning/milestones --include=*.md -l | wc -l` returns **33** files. (An earlier figure of 10 for
  this same count was wrong and is not restated here as a correction of that number — it is a fresh
  measurement, taken in this plan, of the same live fact.)

## 2. Per-issue reply ledger

Six rows: the five issues this phase replied to, plus gh#9, on which this phase posted nothing.

| Issue | Body file | Comment URL | Versions named | Labels added | Label withheld (reason) | Disposition |
|---|---|---|---|---|---|---|
| [gh#60](https://github.com/henols/firestarter_prom/issues/60) — JP5 8 Mbit warning | `evidence/bodies/187-gh60.md` | https://github.com/henols/firestarter_prom/issues/60#issuecomment-5646849372 | app `3.0.0b39` | `fix:released` (replacing `enhancement`) | none | **Closed, COMPLETED** — the feature request shipped in a released version (D-15) |
| [gh#62](https://github.com/henols/firestarter_prom/issues/62) — AE29F2008 erase refusal | `evidence/bodies/187-gh62.md` | https://github.com/henols/firestarter_prom/issues/62#issuecomment-5646897010 | app `3.0.0b39` | `cause:firmware` (issue had zero labels before) | none | **Left OPEN** — the refusal is correct, but the software chip-erase capability (backlog 999.63) is real, undelivered work (D-15) |
| [gh#23](https://github.com/henols/firestarter_prom/issues/23) — w27e257 FAIL | `evidence/bodies/187-gh23.md` | https://github.com/henols/firestarter_prom/issues/23#issuecomment-5647009393 | app `3.0.0b39`, firmware `3.0.0b27` | `cause:rig`, `needs:report` (`cause:database` retained) | none withheld | **Left OPEN** — REPLY-06, awaiting the reporter's re-run/response |
| [gh#28](https://github.com/henols/firestarter_prom/issues/28) — m27c512 FAIL | `evidence/bodies/187-gh28.md` | https://github.com/henols/firestarter_prom/issues/28#issuecomment-5647056983 | app `3.0.0b39`, firmware `3.0.0b27` | `needs:report` (`dev-test`, `cause:harness` retained) | `fix:released` (only the harness/reporting fix shipped; the M27C512 `vdd`/`vcc` database defect did not) | **Left OPEN** — REPLY-06, awaiting the reporter's re-run/response |
| [gh#31](https://github.com/henols/firestarter_prom/issues/31) — m27c1001 INCONCLUSIVE | `evidence/bodies/187-gh31.md` | https://github.com/henols/firestarter_prom/issues/31#issuecomment-5647114539 | app `3.0.0b39`, firmware `3.0.0b27` | `needs:report` (`dev-test`, `cause:harness`, `cause:database` retained) | `fix:released` (only the harness/reporting fix shipped; the M27C1001 pin-30 database defect did not) | **Left OPEN** — REPLY-06, awaiting the reporter's re-run/response |
| [gh#9](https://github.com/henols/firestarter_prom/issues/9) — Repository Structure and Contribution Guide | n/a — no post in this phase | https://github.com/henols/firestarter_prom/issues/9#issuecomment-5511487546 (posted by **Phase 173**, 2026-09-02, not this phase) | n/a | none changed | n/a | **Left OPEN and pinned** — already the deliberate, configured end state; this phase posted nothing new and changed nothing about it (D-06) |

## 3. Pinned permalink SHA

Every `.planning/notes/` link in every reply body posted by this phase pins the same single commit:
the meta merge SHA **`ebd80b53b06b49678e41f12d31136f5b9d3edd26`** (PR #69, `firestarter_prom`,
`origin/beta` after merge — `187-MERGE-RECORD.md` § 1 and § 5).

Both anchors used by the two `.planning/notes/` documents the replies cite, so a future reader can
resolve either link without re-deriving a slug:

- https://github.com/henols/firestarter_prom/blob/ebd80b53b06b49678e41f12d31136f5b9d3edd26/.planning/notes/jumper-display-ground-truth.md#which-operations-energize-socket-pin-1--the-answer-to-gh60
- https://github.com/henols/firestarter_prom/blob/ebd80b53b06b49678e41f12d31136f5b9d3edd26/.planning/notes/ae29f2008-classification-verdict.md#why-the-reporters---force-erase-worked-and-why-that-is-not-a-licence

The versions the replies name were both **read after the cut, never predicted**: app `3.0.0b39`
(`evidence/187-03-app-version.txt`, cross-confirmed on PyPI), firmware `3.0.0b27`
(`evidence/187-04-fw-version.txt`, GitHub Releases only — no PyPI step for that repository).

## 4. Disposition of the finding — named, and nothing filed

**This phase files zero backlog items, zero todos and zero successor requirements against the gh#9
staleness finding.** The branch taken is exactly the one the operator has taken at this same fork
before: name the finding, on the record, in the place a future reader will look — and file nothing
against it. No "verify upstream claims against the live API before promoting a backlog stub" guard
item is created here, and CLAIM-09's shape (a fail-closed scan-path existence check) is not read as
licensing one either; the two are different problems.

The predecessors that took the same branch, by phase and decision: **Phase 184 D-05/D-06** (retiring
the three-way dispatch invariant with no successor guard, against the orchestrator's own
recommendation) and **Phase 185 D-01/D-04** ("name it, file nothing" for the catalog-sync-check
retirement). This ledger states its zero count explicitly — rather than omitting a "backlog items
generated" section entirely, the way 182/183/184/185's verdict documents each carry one — so a later
reader does not mistake the absence of that section for an oversight.

## 5. The residual gap, named explicitly

The capability gh#23's reporter actually needs — detecting a mis-wired VPP at the socket, as
distinct from a healthy boost-regulator rail reading — is not built and is not filed here either.
SAFE-03 already established that the rail reading alone cannot prove socket routing (measured at
4.9 V on the disabled-boost-regulator path, decisively below the ~6 V logic-level threshold), so
this is new hardware-side detection work, not a host-software fix, and it would change the verdict
of a fresh `dev test w27e257` run for exactly the failure mode this reporter hit. Recorded here,
under the same discipline as Section 4, and not filed as a backlog item.
