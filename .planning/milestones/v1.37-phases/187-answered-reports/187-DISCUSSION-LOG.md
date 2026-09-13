# Phase 187: Answered Reports - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-12
**Phase:** 187-Answered Reports
**Areas discussed:** Release seam for REPLY-03/04; gh#9 — already answered once; How far to retract the
2026-08-08 triage; Labels and metadata, not just comments

**Mode notes:** `workflow.discuss_mode` = `discuss`; no flags; `ADVISOR_MODE` false (no USER-PROFILE.md).
`workflow.research_before_questions` is `true` but no web search was run — every area was decided from
measurements taken in-repo and from this project's own precedent, and the orchestrator said so at the
point of skipping rather than performing a hollow search.

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Release seam for REPLY-03/04 | jp5_gate.py and flash4_erase_gate.py not on origin/beta; no v1.37 PR exists | ✓ |
| gh#9 — already answered once | The 2026-09-02 comment already delivers REPLY-07's closing reply | ✓ |
| How far to retract the 2026-08-08 triage | Reporter's explanation on gh#28 was later validated by Phase 179 | ✓ |
| Labels and metadata, not just comments | cause:database on gh#23 vs the reporter's rig-fault account | ✓ |

**User's choice:** all four.

---

## Release seam for REPLY-03/04

### Q1 — How does 187 resolve replies describing unmerged code?

| Option | Description | Selected |
|--------|-------------|----------|
| 187 owns the merge + cut, then posts | Phase 152 D-04's route: PRs to beta in all three repos, cuts fire, versions read from `gh release list`, then post | ✓ |
| Post now, worded as landed-not-released | Cheaper, unblocks reporters faster, but gh#60/#62 get nothing runnable | |
| Split the timing per issue | REPLY-01/02 now against b38; REPLY-03/04 after the cut | |

**User's choice:** 187 owns the merge + cut, then posts.
**Notes:** Measured at discussion time — `firestarter/jp5_gate.py` absent from `origin/beta`; app 33
commits ahead, firmware 9 ahead; zero open v1.37 PRs in any repo. App `3.0.0b38` is byte-for-byte
`origin/beta` HEAD, so v1.36's work IS installable today; v1.37's is not.

### Q2 — Which repositories merge?

| Option | Description | Selected |
|--------|-------------|----------|
| All three — app, firmware, meta | Two cuts fire (app + fw); meta cuts nothing | ✓ |
| App + firmware only; meta waits for close | Avoids stranding 187's own tail behind a mid-phase merge | |
| App only | Every gate is host-side, so fw is not strictly needed | |

**User's choice:** all three.
**Notes:** Firmware is not docs-only — `src/proms/flash_5v_page.cpp` loses 52 lines (SAFE-08's unreachable
12 V bulk-erase arm). Behaviour-neutral, but a real code edit.

### Q3 — What is left for `/gsd-complete-milestone` and `/gsd-ship`?

| Option | Description | Selected |
|--------|-------------|----------|
| 187 ships; close is archive-only | 187's PRs and cuts ARE the v1.37 ship; close is hand-archival | ✓ |
| 187 merges app + fw; meta merges at close | Keeps 187's own record inside the milestone merge | |
| 187 merges, then re-merges its own tail at close | Nothing stranded, at the cost of an extra PR | |

**User's choice:** 187 ships; close is archive-only.
**Notes:** Accepts the known v1.35 pattern — the close tail does not reach `beta`.

### Q4 — Tag, and what reporters are told to install?

| Option | Description | Selected |
|--------|-------------|----------|
| No tag; replies name the pre-release versions | Same call as v1.36; `pip install --pre -U firestarter` | ✓ |
| Tag v1.37 as part of 187's ship | Follows v1.35 Phase 173 | |
| Decide the tag after the cut lands | Keeps the phase unblocked either way | |

**User's choice:** no tag; replies name the pre-release versions.

---

## gh#9 — already answered once

### Q1 — How is REPLY-07 handled given Phase 173 already posted a closing reply?

| Option | Description | Selected |
|--------|-------------|----------|
| Discharge it; repair the false record | Mark REPLY-07 Complete citing issuecomment-5511487546; correct ROADMAP:5424; post nothing new | ✓ |
| Post a short v1.37 addendum anyway | Satisfies the literal verb, adds noise to a pinned orientation issue | |
| Close gh#9 as done | Reverses Phase 173's operator-approved decision to keep it open and pinned | |

**User's choice:** discharge it; repair the false record.
**Notes:** Verified live — `pinnedIssues` on prom returns `#9`. `173-07-SUMMARY.md:115-118` records the
post, the byte-identity read-back, and the deliberate leave-open-and-pin.

### Q2 — How wide is the repair?

| Option | Description | Selected |
|--------|-------------|----------|
| The five measured live sites, and stop | ROADMAP:5409-5411, :5424, :502; REQUIREMENTS:118, :217 | ✓ |
| Widen to a general owed-replies audit | Re-check gh#5, #7, #11, #14 against the live API too | |
| Amend only; leave the backlog prose alone | Smallest edit; leaves two live false sentences standing | |

**User's choice:** the five measured live sites, and stop.
**Notes:** Carries Phase 184's D-01 discipline forward by name. `ROADMAP:967` and `:1224` are live but
**true** (gh#9 "stays open as the pinned orientation issue") and are not repaired; the 10 hits under
`.planning/milestones/` are historical-by-intent.

### Q3 — What about the recurrence?

| Option | Description | Selected |
|--------|-------------|----------|
| Record it in a notes/ verdict; file nothing | Matches 184 D-05/D-06 and 185 D-01/D-04 | ✓ |
| File a backlog item for an upstream-claim check | CLAIM-09's shape applied to planning records | |
| Name it in the phase SUMMARY only | Breaks the 182–185 standalone-verdict-note pattern | |

**User's choice:** record it in a notes/ verdict; file nothing.

### Q4 — What does that note cover?

| Option | Description | Selected |
|--------|-------------|----------|
| One note: gh#9 finding + full reply ledger | Single durable record a future reader checks | ✓ |
| Two notes — verdict and ledger separate | Cleaner categories, two files to keep in sync | |
| Note for gh#9; ledger stays in the phase dir | Strongest precedent match (173-UPSTREAM-REPLIES.md) | |

**User's choice:** one note covering both.

---

## How far to retract the 2026-08-08 triage

### Q1 — Retraction posture

| Option | Description | Selected |
|--------|-------------|----------|
| Concede attribution fully, keep the findings standing | Reporters were right about attribution; the datasheet findings are unfixed and independently true | ✓ |
| Retract the datasheet analysis outright | Discards three measured defects no other record tracks | |
| State both; let the re-run decide | Most neutral, but reads as not having listened on gh#28 | |

**User's choice:** concede attribution fully, keep the findings standing.
**Notes:** Measured against the shipped database — `W27E257 vpp_mv=13500` (unfixed), `ST M27C512
vdd=6500/vcc=5000` (unfixed), `ST M27C1001 DIP32_27C020` pin-30 (unfixed). v1.36 fixed none of the three;
it changed attribution and reporting. Also: `W27E257` is `EEPROM`, so Phase 179's UV work does not apply
to gh#23; `M27C512` and `M27C1001` are both `UV-EPROM`, so it does.

### Q2 — REPLY-01's overclaim on gh#23

| Option | Description | Selected |
|--------|-------------|----------|
| State the limit plainly; amend REPLY-01 in-phase | Following 183 D-08 / 184 D-03 / 185 D-02 | ✓ |
| Keep REPLY-01's wording; let the reply carry the nuance | Leaves a requirement whose literal reading is an overclaim | |
| Also file the gap as a backlog item | Adds a VPP socket-detection item; new hardware-side work | |

**User's choice:** state the limit plainly; amend REPLY-01 in-phase.
**Notes:** `chip_test.py:2599` fires the status axis only on `(SerialError, HardwareOperationError)`.
gh#23's fault — VPP not hooked up — raises neither. `diagnostic_report.py:55-68` says it in its own words:
*"a rig with VPP unhooked still reads a healthy rail."* A fresh run would still read `write BAD, verify
BAD`. Also flagged: no `w27e257` PASS issue exists in the tracker, so the concession must not imply one.

### Q3 — Caveats carried into the re-run asks

| Option | Description | Selected |
|--------|-------------|----------|
| Carry both; fold the UV todo into the phase | UV write-shortcut divergence on gh#28/#31; gh#68 cross-link on gh#62 | ✓ |
| Carry gh#68 only | Leaves out an internal todo | |
| Neither — keep the asks clean | Risks a gh#28 PASS being read as "write works now" | |

**User's choice:** carry both.
**Notes:** The UV todo is folded as reply material only; its exported-key question stays pending.

### Q4 — The same reporters' other open issues

| Option | Description | Selected |
|--------|-------------|----------|
| Deferred idea; one sentence of acknowledgement | dim20's reply acknowledges gh#65/#66 without a timeline | ✓ |
| Strictly out of scope, say nothing | Cleanest boundary | |
| Pull gh#65/#66 into 187 | Scope this phase was explicitly not given | |

**User's choice:** deferred idea; one sentence of acknowledgement.

---

## Labels and metadata, not just comments

### Q1 — Does 187 change labels?

| Option | Description | Selected |
|--------|-------------|----------|
| Relabel deliberately, per issue, in the reply commit | Reply body names which label moved and why; no fix:released on gh#28/#31 | ✓ |
| Comment-only; no label changes | Leaves gh#23 tagged only cause:database | |
| Relabel including fix:released on gh#28/#31 | Invites a reading the measurements do not support | |

**User's choice:** relabel deliberately, per issue, stated in the reply body.

### Q2 — Gate structure across six replies, three PRs and two cuts

| Option | Description | Selected |
|--------|-------------|----------|
| Per-artifact blocking gate; agents post | Phase 152 D-03 extended to the merges; byte-identical read-back per Phase 173 | ✓ |
| Two gates: one for the ship, one batch for the replies | Fewer interruptions; one approval covers six public acts | |
| Agents never post; you run a commands file | Structurally safest; 152 rejected it for convenience | |

**User's choice:** per-artifact blocking gate; agents post.
**Notes:** D-5 stands — the phase must not run under `--auto`/`--chain`, which auto-approve human-verify
gates; `autonomous: false` is not self-protecting against them.

### Q3 — Do gh#60 and gh#62 close?

| Option | Description | Selected |
|--------|-------------|----------|
| Close gh#60; leave gh#62 open | Delivered feature request closes; the 0x05 chip-erase capability is real and backlogged as 999.63 | ✓ |
| Close both | Closes a capability request on our own reading | |
| Leave both open pending reporter confirmation | Most conservative; holds a delivered feature open indefinitely | |

**User's choice:** close gh#60; leave gh#62 open.

### Q4 — Register and length

| Option | Description | Selected |
|--------|-------------|----------|
| Short and plain; evidence linked, not inlined | Concession or answer in the first two sentences; notes/ linked for detail | ✓ |
| Keep the dense evidence-first house style | The style that produced three one-line rejections | |
| Verbatim where the record says verbatim, short elsewhere | Most literal D-09 compliance; one reply reads very differently | |

**User's choice:** short and plain; evidence linked.
**Notes:** Verified that linking works — `henols/firestarter_prom` is PUBLIC and `.planning/notes/` is on
`beta` (26 entries). Locked consequences: commit-SHA permalinks only (branch links rot, `main` lags
`beta`), and the meta merge must land before any reply posts.

---

## Claude's Discretion

- Exact prose of each reply body, subject to the register decision and the per-artifact operator gate.
- Phase-directory file naming (`187-GH{N}-COMMENT.md` per Phase 152 is the obvious precedent).
- Which commit SHA each permalink pins; how the `notes/` document is sectioned.
- Plan and wave decomposition, and where the record repairs sit relative to the ship.

## Deferred Ideas

- Answer gh#65 (`MX27C4000`) and gh#66 (`MBM27C4001`) — own phase.
- gh#21 (`at28c256`, `needs:report`) — still awaiting a fresh run.
- Detect a mis-wired VPP at the socket — the capability gh#23 actually needs. Deliberately **not** filed
  as a backlog item, under the "name it, file nothing" decision.
- Fix the three standing datasheet defects (`W27E257` `vpp_mv`, the `vdd != vcc` gap across 358 rows,
  `M27C1001` pin 30) — restated as open in the replies, fixed nowhere here.
- The `0x05` software chip-erase — already backlog 999.63, with the W29C020C boot-block caveat.
