# Phase 137 plan 137-04 — RELOCK-07 Confirmation, C-1 Disposition, Pre-flight Recommendation

**Purpose:** the fourth of Phase 137's four named claim-gate artifacts (`137-LEDGER.md`,
`137-DECISION.md` — this file, `137-RELEASE-NOTES-app.md`, `137-GH12-COMMENT.md`). Three
self-contained sections, each closing out one obligation this plan owns.

---

## 1. RELOCK-07 confirmation

The stale `--sdp-relock` "v1.23+" deferral label is fixed at both live occurrences — the carry-forward
table row in `.planning/STATE.md` and the decision-log table row in `.planning/PROJECT.md` — both now
reading **Backlog 999.28** in place of the version label. Fresh-measured at this plan's own execution
(2026-08-05), the live lines were `.planning/STATE.md:972` and `.planning/PROJECT.md:844` — a fifth
drift from the `634`/`823` pair this requirement had itself cited (measured 2026-08-03). All four
citation sites named by the requirement's own text — `REQUIREMENTS.md`'s RELOCK-07 itself,
`PROJECT.md`'s own "Stale labels this milestone fixes" paragraph, the design note
(`sdp-surface-retirement-and-behavioral-proof.md`) §8, and `ROADMAP.md`'s v1.30 milestone-list
entry — now agree on these terminal values, each appending its own correction rather than
overwriting its prior text, per this project's standing append-only-correction convention. RELOCK-07
is ticked **Complete** in `REQUIREMENTS.md`.

**No AT28C silicon was tested during this milestone** — restated here per this document's own
Removed/RELOCK-adjacent content, though RELOCK-07 itself is a pure documentation fix with no
silicon-adjacent claim of its own.

---

## 2. Operator-batch item C-1 disposition

**Finding:** `build_db_diff`'s `ladder_state` no longer reaches `community-reported` for a
genuinely-passing ALLOW chip. Once the SDP leg is genuinely reachable end to end, an all-OK run
attaches an `"indeterminate"`-classified `Fingerprint` on the baseline/restored steps — 134-02's own
"attach in every arm" design meeting `classify_fingerprint`'s four-bucket design, which has no
dedicated "perfect match" bucket. Measured by 134-03; confirmed-and-deferred, not absorbed, by
134-06 (`134-RECORD.md` §6 residual 4).

**Disposition: defer-with-owner.** `diagnostic_report.py` / `classify_fingerprint` are both outside
every Phase 137 plan's declared file scope. Fixing the four-bucket classifier here — inside the
milestone's own honesty-close phase — would be an undeclared scope expansion, the exact opposite of
what this phase exists to do: this phase closes the milestone honestly, it does not open new work
inside itself. The finding is real and chip-content-independent (not a fixture artifact), so it is
not accepted-and-dropped either — it is named, owned, and filed:

- Filed as `.planning/todos/pending/build-db-diff-ladder-state-community-reported-regression.md`,
  citing `134-RECORD.md` §6 residual 4 verbatim, with `Owner: henols` (matching this project's
  established convention for a genuinely-unowned finding needing a human decision, e.g.
  `at28c256-write-path-failure-gh20.md`).
- `.planning/v1.30-OPERATOR-BATCH.md`'s C-1 row updated from "needs a disposition before close" to
  name this exact disposition, the filed todo's path, and the owner.

**The underlying `classify_fingerprint`/`ladder_state` code is NOT touched by this plan** — the
disposition is defer-with-owner, not fix-in-place. No code file is modified by plan 137-04.

---

## 3. Pre-flight recommendation — beta-only close

Per the standing operator instruction ("nothing is stable until the operator says so" — beta-only
at every milestone close, unbroken across v1.11 through v1.23), **this phase recommends v1.30 stays
on the `--pre`/beta channel at close.** Nothing in Phase 137 implies or requests a stable-channel
promotion:

- PyPI `info.version` is not touched by anything in this plan.
- No firmware or host artifact is published, tagged, or promoted by this document.
- This recommendation is a record of what Phase 137 concludes, not an action — this file pushes,
  merges, and publishes nothing itself.

Two items still require the operator directly before the milestone can actually close (cross-
referencing `.planning/v1.30-OPERATOR-BATCH.md` §A):

- **A-1** — approve the gh#12 follow-up reply wording (draft ready at
  `.planning/v1.30-GH12-REPLY-DRAFT.md`), then post it. Outward-facing; blocking; cannot be
  delegated.
- **A-2** — push the branch and open the PR to `beta`. Outward-facing; opening the PR is safe, but
  merging it pushes `beta` and auto-fires CI (a repeat risk named at the v1.21 close).

Nothing in this section changes the disposition of A-3 (how CLOSE-06 is ticked), which remains a
question for the plan that owns CLOSE-06 (137-05), not this one.

---

## Summary of what this artifact proves

1. RELOCK-07's label-and-citation chain is closed with fresh-measured terminal values, not another
   entry in the drift.
2. C-1 has a real, named-owner disposition (defer-with-owner) instead of a silent disappearance at
   close — filed as a backlog todo, cross-linked in both directions, batch row updated.
3. This phase's own recommendation is recorded in writing, before any push, merge, or publish
   action — beta-only, consistent with every prior milestone close in this project.
