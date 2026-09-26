---
title: Reply on gh#12 (and correct the b14 app release notes) after `dev sdp` is retired
date: 2026-07-31
priority: medium
blocked_by: the removal shipping — provisional milestone v1.30 (queued NEXT after v1.23, from Backlog 999.25). Do not post before the removal is real.
resolves_phase: 152  # v1.30 CLOSE-06 was held open by design; re-homed to v1.32 Phase 152 (OUT-01). NOTE 2026-08-20: this comment previously read "where `write --sdp-relock` actually exists to be named" -- that premise is now FALSE. Phase 150 was deferred back to Backlog 999.28 on 2026-08-20, so the command does not exist in v1.32 either and the 2026-08-03 amendment below (do NOT name it as available) is STILL the operative instruction, for a second release. OUT-01/OUT-04 were amended to match, and OUT-05's claim gate now rejects any text naming it as shipped.
---

# gh#12 follow-up owed once `dev sdp` is retired

`firestarter dev sdp <chip> enable|disable` is named in two outward-facing artifacts published
**2026-07-30**, one day before the decision to remove it:

- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-GH12-COMMENT.md:15`
  — posted to [gh#12](https://github.com/henols/firestarter_prom/issues/12), the thread whose
  reporter had to build a separate Arduino to disable SDP before Firestarter could write at all
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-RELEASE-NOTES-app.md:12,22`
  — the `3.0.0b14` app release notes

The removal is decided in
[`.planning/notes/sdp-surface-retirement-and-behavioral-proof.md`](../../notes/sdp-surface-retirement-and-behavioral-proof.md)
and scoped as Backlog Phase 999.25.

## ⚠ STILL AMENDED — and now for a second release (2026-08-20)

`write --sdp-relock` was promoted into v1.32 as Phase 150 on 2026-08-18, which would have made the
original point 1 true again — and was then **deferred back out on 2026-08-20** (operator decision, at
the discuss step, nothing created). **So the 2026-08-03 amendment below stands unchanged and is the
operative instruction.** Do not restore the original wording. The reply now has to admit the withdrawal
has spanned two releases: v1.30 removed the surface, and v1.32 — the milestone scoped to restore it —
did not. v1.32's OUT-05 claim gate exists partly to catch a reply that gets this wrong.

## ⚠ AMENDED 2026-08-03 — `write --sdp-relock` did NOT ship; point 1 below was rewritten

The reply's original point 1 named `write --sdp-relock` as the deliberate-lock replacement. **That is
now false.** v1.30 **Phase 135**, which was to land it, was deferred out of the milestone by operator
decision on 2026-08-03 and filed as ROADMAP Backlog **999.28**. Phase 132 still deletes `dev sdp` —
**both halves** — in v1.30. So the milestone removes the deliberate-protection surface and ships **no
replacement**.

Posting the original wording would tell a stranger to run a command that does not exist in the release
being announced. That is the same overclaim class as v1.22's C-5 correction, in the very thread this
reply exists to be honest with. See `.planning/todos/pending/write-sdp-relock-deferred.md`.

## What the reply must say

1. **The command is gone. `disable`'s behaviour survives; `enable`'s does not.** Unlock is already
   `write`'s default behaviour (auto-unlock on every protocol-`0x0D` write, declinable via
   `--skip-sdp-unlock`) — so `dev sdp disable` is genuinely redundant, not merely dropped. The
   deliberate **lock** is **withdrawn with no replacement in this release**, tracked as Backlog 999.28.
   Do **not** name `write --sdp-relock` as available. If it helps the reporter, it is fine to say the
   design is settled and the work is queued — but as *queued*, never as shipped, and without promising a
   version.
2. **Name the rewording honestly.** gh#12 asked for "enable/disable". After v1.30 it gets `disable`'s
   effect automatically and **no `enable` at all**. Say both halves plainly — including that a user who
   wants a part left protected currently has no supported way to do it, and cannot read the protection
   bit back to check. Do not present this as if it were the original ask satisfied.
3. **State the gain, without overclaiming it.** The lock is now *testable* — `dev test` on an
   SDP-capable part locks it, attempts a write without unlocking, and checks the chip is unchanged.
   That is the first oracle this feature has ever had. It remains **untested on real AT28C
   silicon**; `0x0D` stays `UNVERIFIED`. Do not let "now provable" drift into "now proven" — the
   same overclaim class as v1.22's C-5 correction.
4. **Ask for the run.** A reporter with an AT28C is exactly who can close the evidence gap: one
   `firestarter dev test <chip>` and the report it files.

## Constraints

- Outward-facing → **operator-reviewed before posting**, never auto-approved. `--auto`/`--chain`
  auto-approves human-verify checkpoints, so gate this separately
  (`reference_auto_mode_autoapproves_outward_facing_gates`).
- Do **not** post before the removal has actually shipped, or the thread will name a command that
  still exists.
- The b14 release notes are historical and already published — correct the *next* release notes,
  do not rewrite the shipped ones.
- **Do not name `write --sdp-relock` as an available command** (see the amendment above). The "Removed"
  mapping in the next release notes must read `dev sdp disable` → `write` (automatic) and
  `dev sdp enable` → *withdrawn, no replacement, tracked as Backlog 999.28*.

---

## ✅ RESOLVED 2026-08-21 — v1.32 Phase 152, plan 152-14 (OUT-01)

**Posted:** [gh#12 comment](https://github.com/henols/firestarter_prom/issues/12#issuecomment-5373440001)
— id `IC_kwDOSX4ER88AAAABQEgwAQ`, created `2026-08-21T18:00:19Z`. Comment count 10 → 11 (delta exactly
one). gh#12 is **still OPEN** and was not closed. Comments 1–10 verified unchanged by id and creation
date against the pre-post capture; the issue's `updatedAt` bumped to the post timestamp, which is a
new-comment side effect and not a body-edit oracle.

The posted body is character-for-character the frozen draft
(`152-GH12-COMMENT.md`, blob `cd4a62c527e3ba5efb5b5f9f4fc9f004da99f041`) except that GitHub appended one
trailing newline: 4313 bytes stored vs 4314 read back, equal after `rstrip('\n')`. The claim gate, run
over the read-back body under its real basename, exits 0.

### Which of the four "what the reply must say" points the posted text discharges

1. **DISCHARGED, and more strictly than this todo required.** The posted text says the command is gone,
   that `disable`'s behaviour survives as `write`'s default-on auto-unlock (declinable via
   `--skip-sdp-unlock`) and so was genuinely redundant, and that `enable` is withdrawn with no
   replacement, tracked as Backlog 999.28. The deferred command is **never named anywhere in the body**.
   This todo permitted saying the design is settled and the work is queued; the posted text does **not**
   say that either — after a second deferral it says only that the item is tracked and that no version
   is being promised. That is the stricter reading and it is deliberate.
2. **DISCHARGED.** Both halves are stated plainly — "You asked for both, and what you get is one of them
   automatically and none of the other" — together with the consequence that a user wanting a part left
   protected has no supported way to do it, and the separate limitation that the protection bit cannot
   be read back, so nothing can show a protected part is protected.
3. **PARTIALLY DISCHARGED — the constraint fully, the specific gain framing superseded.** This todo was
   written 2026-07-31 and framed the gain as "the lock is now *testable*: `dev test` on an SDP-capable
   part locks it, attempts a write without unlocking, and checks the chip is unchanged." That framing
   pre-dates v1.30's retirement of the `dev sdp` surface and v1.32's addition of `dev lock-status`, and
   the posted text does **not** make that claim. What it states instead is `lock-status` (refusal as the
   feature, beta-channel only, requiring matched firmware), the removal of the pre-write blank check,
   the standalone software erase step, and firmware-identifying `dev test` reports. The load-bearing
   half of point 3 — do not let "now provable" drift into "now proven" — is discharged: the body carries
   "No AT28C part was tested at any point in v1.32" and claims no silicon validation anywhere. A future
   reader should not take this row as evidence that the 2026-07-31 testability framing was published.
4. **DISCHARGED, and strengthened.** The ask names **both** install halves — `pip install --pre
   firestarter` *and* `firestarter fw --install` — with the reason stated: the write-path change lives in
   the firmware and the host's test step sends no override flag, so on older firmware the old failure
   reproduces exactly. A request naming only the pip install would have been a broken request.

### Constraints

- **"Correct the next release notes, do not rewrite the shipped ones" — DISCHARGED** by this same phase:
  `152-RELEASE-NOTES-app.md` targets `3.0.0b23`, the version actually cut by this milestone's merge. The
  historical `3.0.0b14` notes are untouched.
- **"Do not name `write --sdp-relock` as an available command" — DISCHARGED.** The literal string does
  not appear in the posted body at all. OUT-05's claim gate is armed against exactly this class and was
  seen to reject a planted violation before this post was made.
- **"Operator-reviewed before posting, never auto-approved" — NOT DISCHARGED AS WRITTEN.** See the
  provenance note in `152-14-SUMMARY.md`: D-03's per-artifact wording review was **delegated to the
  agent by the operator**, not performed by the operator. `152-check-not-auto.py` returned rc=0
  immediately before the post and `workflow._auto_chain_active` was verifiably `false`, so no auto or
  chained run approved this — but the human read this constraint asks for did not happen, and this row
  must not be read as saying it did.
