---
phase: 122-close-honesty-ledger-community-ask-release-decision
plan: 10
subsystem: release-comms
tags: [honesty-ledger, community-reply, claim-scanner, sdp, at28c, gh11, gh12]
dependency_graph:
  requires:
    - 122-LEDGER.md (permitted-wording source, and the C-5/D-14 divergence's prior flag)
    - 122-CUT.md (observed cut tag, referenced only via `pip install --pre`, never hardcoded)
    - 122-CHANNELS.md (both channels verified public before this draft was authored)
  provides:
    - 122-GH11-COMMENT.md (committed, unposted gh#11 follow-up draft)
    - 122-GH12-COMMENT.md (committed, unposted gh#12 reply draft)
  affects:
    - 122-11 (D-16 operator wording review reads both drafts, including the flagged divergence below)
    - 122-12 (delivery via `gh issue comment --body-file`, after the review)
tech_stack:
  added: []
  patterns:
    - "community comment drafted as a committed file, delivered later via --body-file, never an inline string"
    - "locked-decision divergence applied and flagged in the same commit, never silently rewritten"
key_files:
  created:
    - .planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-GH11-COMMENT.md
    - .planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-GH12-COMMENT.md
  modified: []
decisions: []
metrics:
  duration_minutes: 25
  tasks_completed: 3
  files_created: 2
  files_modified: 0
  completed_date: "2026-07-30"
status: complete
---

# Phase 122 Plan 10: gh#11 Follow-Up and gh#12 Reply Drafts Summary

Wrote and committed two outward-facing GitHub comment drafts — a gh#11 follow-up crediting the
community reproduction and asking for a plain write+verify re-test, and a gh#12 reply answering the
maintainer's own unanswered 2024 design question with the shipped auto-unlock policy — both gated
green by the Wave 0 claim scanner and a draft-specific overclaim-shape check, and both carrying the
corrected (not D-14's prescribed) answer to `No-Hazmats`. Nothing was posted.

## What Was Built

**`122-GH11-COMMENT.md`** (72 lines) — addressed to `datapaganism`. Covers, in order: thanks and
credit for the 2026-07-27 real-hardware reproduction; both defects named (the `/WE`-inhibited command
emitter, and the page-verify **conflation**, described explicitly as a conflation and not a
sampling-rate defect, per PROJECT.md's FOURTH CORRECTION item 2); the 2024-vs-beta explanation
including the `0x005555` timeout address and the explicit "not a regression" framing; the beta install
path (`pip install --pre --upgrade firestarter`, `firestarter fw --install`); a "what is proven / what
is not" section ending in the canonical caveat; and the two-part ask — plain `write` + `verify` first,
`dev test` second and optional, with the always-writes warning stated before the `dev test` mention.
Issue-stays-open statement present.

**`122-GH12-COMMENT.md`** (78 lines) — addressed to the thread generally (author `humbertocsjr`).
Covers, in order: the maintainer's own 2024 question quoted and answered with all four policy elements
(auto-unlock default-on-and-reported, `--skip-sdp-unlock`, `dev sdp <chip> enable|disable`, the
deferred re-lock with its stated hazard reason); a short mention of the underlying command-emitter/
inverted-check defects with a pointer to the gh#11 write-up for the long version; the capability
boundary (43 allowed / 41 refused of the 84-chip bucket, FRAM parts and the pre-SDP `2804`/`2816`/
`2817` generation named, refusal framed as deliberate); a "what is proven / what is not" section ending
in the canonical caveat; three inline answers (SST39SF deferred with its VPP-safety point already
satisfied stated; the 2025 write failure re-framed on the confirmed app-1.3.44 + firmware-1.4.2 +
`ClearCommError` facts — see the A1 disposition below — as a pre-3.0 transport bug, inviting a fresh
report; and the corrected `No-Hazmats` answer, by size class, stating the refusal plainly, naming the
open deferrals, and offering to look at their actual failure); and a closing statement that the issue
stays open plus the beta install path.

## A1 Disposition: CONFIRMED

Per Task 3's instruction, one focused re-retrieval attempt was made against the per-comment API
payload rather than the summarized issue view, which is where the truncation research flagged as A1
originates:

```
$ gh api repos/henols/firestarter_prom/issues/12/comments --paginate
```

`pdr0663`'s 2025-06-21 comment (id `4948689856`), read from that payload's `body` field in full,
contains both facts A1 flagged as unconfirmed, verbatim:

> `[DEBUG:RURP:210] O: FW: 1.4.2:uno, HW: Rev2, Cmd: 0x02`
>
> `[ERROR:EPROM:362] Error while sending data: ClearCommError failed (PermissionError(13, 'The device does not recognize the command.', None, 22))`

Both the firmware version (`1.4.2`) and the exception-path string (`ClearCommError`) are present and
unambiguous in the full per-comment body — the summarized/paraphrased view research consulted earlier
had truncated the comment before this text. **Disposition: CONFIRMED**, with the quoted substrings
above as evidence. Per the acceptance criteria, `122-GH12-COMMENT.md` therefore names both facts
(`version 1.3.44 with firmware 1.4.2`, `a Windows `ClearCommError` during the send`) — it does **not**
paste the raw traceback or the full debug dump verbatim into the public draft; only the two confirmed
facts are stated, in the reply's own prose, per the outward-facing hygiene constraint against pasting
local/workstation output.

## Gate Results

**Pass 1 — claim scanner**, both files via the env seam:

```
PASS: scanned 122-GH11-COMMENT.md, 122-GH12-COMMENT.md; 2 file(s) carry the required silicon caveat (this PASS is the mechanizable half of criterion 4 only -- see the module docstring's explicit non-claim)
```

Exit code 0. Both file names appear in the single `PASS:` line. `check_permitted_claims.py`'s pattern
set (`FORBIDDEN_PATTERNS`, `REQUIRED_CAVEAT_PATTERN`, `_DEFAULT_TARGETS`) was not modified — confirmed
by `git status --short check_permitted_claims.py` showing no change and by the file not appearing in
this plan's `files_modified`.

**Pass 2 — overclaim-shape check** (the draft-specific check the scanner does not cover):

```
$ grep -ciE 'AT28C[^.]{0,80}(should )?now work' 122-GH11-COMMENT.md
0
$ grep -ciE 'AT28C[^.]{0,80}(should )?now work' 122-GH12-COMMENT.md
0
```

Zero matches in both files.

**Pass 3 — hygiene**, both files: zero matches for `/workspaces/`, `/dev/tty`, `PERSONAL_ACCESS_TOKEN`,
`GITHUB_TOKEN`, `PYPI_API_TOKEN`, `Traceback`, `PS D:`, `workstation`; zero matches for internal
vocabulary (`D-NN`, `C-NN`, `CLOSE-0`, `FIX-0`, `LOCK-0`, `HOST-0`, `DEVTEST-0`, `TRACE-0`, `SDP-F[0-9]`);
zero matches for `all 84`; fence-marker count (` ``` `) is 0 in both files (even). All acceptance-
criteria greps from the plan re-run clean:

| Check | gh#11 | gh#12 |
|---|---|---|
| `wc -l` | 72 (≥30) | 78 (≥30) |
| canonical caveat present | yes | yes |
| `0x005555` present | yes | n/a |
| "always writes" present | yes | n/a |
| first `verify` line < first `dev test` line | 56 < 61 | n/a |
| `--skip-sdp-unlock` / `dev sdp` present | n/a | yes / yes |
| `43` / `2816` present | n/a | yes / yes |

## Flagged D-14 Divergence — for the 122-11 operator review

**What CONTEXT D-14 said** (quoted in substance, per `122-CONTEXT.md:185`): the reply to `No-Hazmats`
should tell them their AT28C parts should now work.

**What was measured** (RESEARCH C-5, re-confirmed against the live 84-chip `0x0D` allow-set derivation
in `122-LEDGER.md`): all 19 of 19 parts on the 24-pin `DIP24_2816` pinout are refused by the SDP
allow-set — 7 as `pre-SDP generation`, 12 as `unrecognised`. The shipped `dev sdp --help` text states
this refusal itself. Because every 2K×8 entry in the 84-chip bucket sits on that same pinout (RESEARCH
A4), the conclusion holds for any 2K×8 part `No-Hazmats` owns — they never named a specific part
number, only "2K x 8".

**What this plan did**: `122-GH12-COMMENT.md`'s `No-Hazmats` answer is phrased by size class rather
than by an assumed part number, states the refusal plainly ("a 2K×8 part in this chip family is not in
the allowed set above"), names the two open deferrals for that generation (datasheet verification of
the magic addresses; the socket-pin question for that footprint), and notes that another thread
participant already recommended a supported alternative part.

**What the operator is being asked to decide**: at the 122-11 wording review, accept this corrected
answer as written, or overturn it in favor of some other framing. This is an explicit decision, not a
fait accompli — the divergence from the locked D-14 text is already recorded in `122-LEDGER.md`'s
"Mechanism corrections recorded here, not in `REQUIREMENTS.md`" section (item 3) and in
`.planning/PROJECT.md`'s EIGHTH CORRECTION (item 3). This SUMMARY is the third place it is recorded,
consistent with both.

## Delivery Pre-Brief (for plan 122-12)

- Both `henols/firestarter_prom` issues **11** and **12** stay **OPEN**. Neither is closed by this
  plan or by the eventual delivery.
- Delivery is exactly:
  ```
  gh issue comment 11 --repo henols/firestarter_prom --body-file 122-GH11-COMMENT.md
  gh issue comment 12 --repo henols/firestarter_prom --body-file 122-GH12-COMMENT.md
  ```
- **Forbidden flags on that delivery, with no exception**: `--label`, `--add-label`, `-l`, `--web`,
  `--editor`. The first three abort the command outright on a missing label (per D-13's research;
  neither issue carries any label today, so any of the three would abort *before* the comment was
  created), and the latter two open an interactive surface this pipeline cannot drive.

## Both Issues Still OPEN, Comment Counts Unchanged

```
$ gh issue view 11 --repo henols/firestarter_prom --json comments,state -q '{comments:(.comments|length), state}'
{"comments":12,"state":"OPEN"}
$ gh issue view 12 --repo henols/firestarter_prom --json comments,state -q '{comments:(.comments|length), state}'
{"comments":8,"state":"OPEN"}
```

Matches `122-08-SUMMARY.md`'s recorded baseline (12/8, both OPEN) exactly. Nothing was posted by this
plan.

## Deviations from Plan

None. The plan's default expectation for A1 was NOT CONFIRMED (with both facts dropped); the actual
outcome was CONFIRMED via the per-comment API payload, which the plan explicitly allowed for as one of
its two acceptable dispositions. No auto-fix, no scope escape, no forbidden action.

## Requirements

`requirements: [CLOSE-02]` in this plan's frontmatter — **not ticked**. CLOSE-02 spans multiple plans
and closes only in 122-13, after both comments are actually posted (122-12) and verified byte-equal to
these committed drafts. No `REQUIREMENTS.md` edit was made by this plan.

## Self-Check: PASSED

- `122-GH11-COMMENT.md` exists: FOUND
- `122-GH12-COMMENT.md` exists: FOUND
- Commit `ab97bd4` (both drafts): FOUND in `git log --oneline`
- Claim scanner exit code 0 with both files named in one `PASS:` line: CONFIRMED
- Overclaim-shape grep returns 0 on both files: CONFIRMED
- Issue 11/12 comment counts unchanged (12/8) and both OPEN: CONFIRMED
