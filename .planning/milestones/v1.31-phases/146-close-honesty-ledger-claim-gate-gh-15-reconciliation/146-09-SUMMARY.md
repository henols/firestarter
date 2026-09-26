---
phase: 146-close-honesty-ledger-claim-gate-gh-15-reconciliation
plan: 09
subsystem: docs
tags: [gh-15, close-04, claim-gate, honesty-ledger, reconciliation]

requires:
  - phase: 146-close-honesty-ledger-claim-gate-gh-15-reconciliation (plan 08)
    provides: 146-LEDGER.md, whose ceiling wording, bench-scope wording and claim table this plan's
      drift checks are read against
  - phase: 139-gh-15-correction-outward
    provides: 139-GH15-ORIGINAL-CRITERIA.md (the nine boxes as filed) and 139-GH15-COMMENT.md (the
      correction wording this plan quotes verbatim in the disposition table)
  - phase: 146-close-honesty-ledger-claim-gate-gh-15-reconciliation (plan 03)
    provides: 146-ARM-BUILD-RECORD.md's box-9 sentence, reused near-verbatim
provides:
  - "146-GH15-RECONCILIATION.md: the nine gh#15 acceptance boxes reproduced verbatim and graded
    under CLOSE-04, the public correction to our own earlier gh#15 comment, and one bench-boundary
    paragraph -- frozen and gate-green"
affects: [146-11 (register), 146-12 (posts this file to gh#15 behind a blocking operator gate), 146-13 (CLOSE coverage)]

tech-stack:
  added: []
  patterns:
    - "Grade the ORIGINAL filed text, not an amended criteria set, so a stranger who never saw the
      correcting comment still gets the whole story from one artifact (D-08)."
    - "Cite a forbidden-literal-bearing source paragraph by file:line and paraphrase it, rather than
      quoting it, when the artifact being written is itself scanned by the same forbidden-phrase gate."

key-files:
  created:
    - .planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-GH15-RECONCILIATION.md
    - .planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-09-SUMMARY.md
  modified: []

key-decisions:
  - "None of the nine boxes is graded not-reachable-on-this-hardware. The 6.25 V ceiling bounds what
    any implementation of gh#15 can buy on this hardware, but it is a hardware property, not a
    property of any one box's literal wording, so it travels as a named narrowing on boxes 5, 7 and
    9 rather than standing in as a fourth box's whole disposition. The literal token still appears in
    the artifact's orientation paragraph, defining CLOSE-04's three-way vocabulary and stating this
    explicitly, which is what the plan's must_haves artifact spec asks this file to contain."
  - "The high-voltage-disable box (7) and the all-targets-build box (9) are graded met-as-corrected,
    not met, even though our own earlier gh#15 comment's disposition table called box 7 unchanged/kept.
    This plan's own grading rules (not the prior comment's table) govern: box 7 carries a real
    narrowing (operation-level disable is a source contract, not behavioural) that a bare met would
    have hidden."
  - "Box 5's own separate energy-cap-value correction is folded into 'The public correction' section
    rather than repeated in the disposition table's column three, to avoid duplicating the same fact
    in two places in one artifact; the disposition row for box 5 points to that section."

requirements-completed: []

# CLOSE-04 is not ticked by this plan -- 146-13 owns all CLOSE checkbox flips. Requirements frontmatter
# on 146-09-PLAN.md lists CLOSE-04, but this plan's own prohibitions (item 7) forbid ticking it here.

metrics:
  duration: ~50min
  completed: 2026-08-17
status: complete
---

# Phase 146 Plan 09: gh#15 Reconciliation Summary

**`146-GH15-RECONCILIATION.md` grades gh#15's nine acceptance boxes as originally filed under
CLOSE-04's three-literal vocabulary, corrects our own earlier public comment's wrong justification
for the `0x0B` energy cap, and states one bench-boundary paragraph — frozen, and green under the
claim gate run against it alone.**

## Performance

- **Duration:** ~50 min
- **Tasks:** 2/2 completed
- **Files modified:** 2 (both created)

## Accomplishments

- Reproduced gh#15's nine acceptance boxes byte-identical to the filed text (diffed directly against
  `139-GH15-ORIGINAL-CRITERIA.md`; zero-line diff after stripping the source header and checkbox
  markers), then graded each with exactly one of CLOSE-04's three literals.
- Corrected our own earlier public gh#15 comment's wrong justification for the `0x0B` energy cap —
  the value (50000 µs) has a genuine primary-datasheet basis; the published reason ("100 × 500 µs …
  the classic 2716 total programming time") did not — citing `140-PARAM-TABLE-RECORD.md:259` and the
  in-place firmware-doc correction already landed at `firestarter/doc/PROTOCOLS.md:255-259`.
- Wrote one bench-boundary paragraph carrying all five required facts and satisfying both of the
  claim gate's caveat labels (`ceiling-voltage`, `ceiling-narrowing`) by content, not by label name.
- Ran the claim gate against the artifact alone: **exit 0** on the first attempt. Ran it in default
  mode as an informational reading only: **exit 1**, naming the two artifacts 146-10 has not yet
  authored — exactly the expected state for this wave.
- Ran and recorded four negative controls, each showing the corresponding locator can fail.
- Ran three drift checks against `146-LEDGER.md` — no divergence found in any of the three.
- Froze the artifact and recorded its blob SHA and byte count below (not in `146-CITATIONS.md`, per
  this plan's own instruction, to avoid racing 146-10 in the same wave).

## Task Commits

1. **Task 1: Write the reconciliation** — combined with Task 2 into a single commit (`146-09-PLAN.md`
   instructs Task 1 not to commit; Task 2 is verification-only against the already-written file) —
   `4a3a220c` (docs)

**Plan metadata:** commit pending below (STATE.md + ROADMAP.md, separate from the artifact commit)

## Files Created/Modified

- `.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-GH15-RECONCILIATION.md` —
  the reconciliation artifact: nine boxes reproduced verbatim, a nine-row disposition table, the
  public correction section, and the bench-boundary paragraph.
- `.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-09-SUMMARY.md` — this
  file.

## Disposition-row readings

| # | Disposition |
|---|---|
| 1 | met-as-corrected (separate-handlers premise replaced by one shared per-byte loop plus a `const` table) |
| 2 | met (no new `chip_database.json` algorithm field; `protocol_id` remains the single dispatch key) |
| 3 | met-as-corrected (`EPROM_STD`'s `1 ms` constant corrected to a `1000 us` fallback over a 50–1000 us database range) |
| 4 | met-as-corrected (`EPROM_QUICK`'s "own handler" and "fixed" premises both corrected) |
| 5 | met-as-corrected (`EPROM_LEGACY`'s `50000 us` bug corrected to a `500 us` fallback; adaptive loop confirmed gone) |
| 6 | met (block-mismatch/adaptive-pulse-growth algorithm confirmed removed, not retained under another name) |
| 7 | met-as-corrected (VPP disable narrowed: per-block error-exit disable vs. operation-level source contract vs. deliberate energised-on-success state) |
| 8 | met (test coverage narrowed: dispatch now means table-row selection; one coverage claim bounded to the emitted control-register stream) |
| 9 | met-as-corrected (three AVR targets measured plus the ARM target's one observed local build, explicitly not CI parity) |

Row count and disposition-literal count both verified at 9/9 by the plan's own automated leg
(`numbered_rows=9 valid_disposition_rows=9`).

## Negative-control readings (all four scratch copies discarded after use)

1. **Tenth numbered row added** (`/tmp/gsd146/recon_10row.md`, discarded): row-count locator reported
   `control1_row_count=10` — the row-count leg can fail.
2. **Invented disposition token** (`/tmp/gsd146/recon_bad_token.md`, discarded, box 2's cell changed
   to `**sorta-met**`): valid-disposition-row count dropped to `control2_valid_rows=8` — the
   disposition-literal leg can fail.
3. **Public-correction section deleted** (`/tmp/gsd146/recon_no_correction.md`, discarded): both of
   its anchors reported missing — `control3_100seconds=missing control3_twpr=missing` — the
   token-presence leg can fail.
4. **Voltage figure and silicon-margin phrase stripped** (`/tmp/gsd146/recon_stripped.md`, discarded):
   the **gate itself** (`146-check-claims.py`, not a plan-local grep) exited non-zero —
   `control4_gate_rc=1` — naming both missing labels verbatim:
   ```
   FAIL: 2 file(s) missing a required 6.25 V ceiling caveat:
     /tmp/gsd146/recon_stripped.md: missing required caveat [ceiling-narrowing]: expected a phrase matching 'the silicon-margin narrowing that ceiling implies'
     /tmp/gsd146/recon_stripped.md: missing required caveat [ceiling-voltage]: expected a phrase matching 'the ~6.25 V program-VCC ceiling'
   ```

## Claim gate runs against the real artifact

- **Positional mode** (`python3 146-check-claims.py 146-GH15-RECONCILIATION.md`): **exit 0**.
  ```
  PASS: scanned 146-GH15-RECONCILIATION.md; 1 of 1 caveat-required file(s) carry every caveat their
  own rule demands; 0 file(s) carry no caveat requirement under D-11 (this PASS is compliance with
  the forbidden-phrase table and the per-file caveat rules only -- see the module docstring's
  explicit non-claim, and note that CLOSE-01 also requires the fixture suite and the real-file plant
  transcript)
  ```
- **Default mode** (no argument), run informationally only, drawing no conclusion beyond what it
  names: **exit 1**, `FAIL: scan target(s) not found on disk ... ['.../146-RELEASE-NOTES-fw.md',
  '.../146-RELEASE-NOTES-app.md']`. This is the expected reading for this wave: 146-10 executes
  concurrently and has not yet authored either release body; 146-11 owns the all-five run and its
  register entry. Landing this plan's own file did not change the count of missing default targets
  from 2 to anything else, which is the correct outcome — this plan does not shrink that list by
  stubbing the other two files.

## Drift checks against `146-LEDGER.md` (no divergence found; nothing edited)

1. **Bench scope.** Ledger (`146-LEDGER.md:166-170`, itself quoting `145-BENCH-LOG.md`'s boundary 3):
   "the Winbond **W27C512**, chip-id **`0xda08`**; controller **`leonardo`**; shield **Rev 2.0**, read
   off the silkscreen by the operator because the EEPROM `hw_revision` byte cannot distinguish 2.0
   from 2.2 from the modified Rev 0." This artifact's bench paragraph: "the Winbond W27C512, chip-id
   `0xda08` — on one controller, `leonardo`, with one shield revision read off the silkscreen by the
   operator because the stored `hw_revision` byte cannot distinguish Rev 2.0 from Rev 2.2 from a
   modified Rev 0." Same part, same controller, same revision, same instrument fact. No divergence.
2. **Ceiling statement.** Ledger (`146-LEDGER.md:111-114`, quoting `.planning/REQUIREMENTS.md`): "The
   ~**6.25 V** program-VCC all four vendor algorithms assume for threshold margin is **unreachable on
   this shield** ... This milestone buys *timing / pulse-count / verify* fidelity and **not**
   silicon-margin fidelity." This artifact: "the raised program-VCC all four vendor algorithms assume
   for threshold margin, roughly **6.25 V**, is unreachable on this shield, so what this milestone
   buys is timing, pulse-count and verify fidelity and not **silicon-margin** fidelity." Same claim,
   same scope, same non-claim. No divergence.
3. **Claim-table permission check.** Every positive statement this artifact makes about shipped
   behaviour maps onto a `PERMITTED` row in `146-LEDGER.md`'s four-column claim table: box 1's
   table-driven-loop description maps to row 1; box 7's VPP routing/source-contract description maps
   to row 4; box 8's dispatch/coverage narrowings map to row 7; box 9's AVR/ARM figures map to row 7;
   the bench paragraph's single-part validation and skip dispositions map to row 2 and the ledger's
   "asymmetric coverage" section. No sentence in this artifact asserts anything the ledger's table
   marks `FORBIDDEN` or leaves unaddressed — in particular, no comparative claim and no
   datasheet-conformance claim in either direction, matching the ledger's own non-claims. No
   divergence.

## Freeze values (register entry deferred to 146-11, per this plan's own instruction)

- **Blob SHA:** `a36ee805a5a645f6d1010b409cd6cfb5434a56d1`
- **Byte count (`wc -c`):** `13260`
- `fw_porcelain=0`, `app_porcelain=7` (both matching the orchestrator's pre-existing-dirt baseline,
  unmoved by this plan), `citations_untouched=0` (`146-CITATIONS.md` was not touched by this plan).

These values are recorded here, not in `146-CITATIONS.md`, because 146-10 executes concurrently in
this same wave and a second appender to that register would race it. 146-11 owns the register's next
section; 146-12 re-measures the freeze inside its own posting task.

## Deviations from Plan

None — plan executed as written. One judgment call, recorded as a decision above rather than a
deviation: no box was graded `not-reachable-on-this-hardware`, because the plan's own per-box grading
rules (re-read carefully) assign one of `met` or `met-as-corrected` to each of the nine boxes and
never call for the third literal on any specific box. The literal string itself is still present in
the artifact (in the orientation paragraph, explaining the vocabulary and why the third disposition
is unused here), which is what the plan's `must_haves.artifacts[].contains` field for this file asks
for — this satisfies that field honestly rather than manufacturing a false "unreachable" grading for
a box that is not actually ungraded.

## Stub Tracking

None. No hardcoded empty values, no placeholder text, no unwired data source in this artifact.

## Threat Flags

None. This plan creates a documentation artifact only; no new network endpoint, auth path, file
access pattern, or schema change at a trust boundary is introduced.

## Self-Check: PASSED

- FOUND: `146-GH15-RECONCILIATION.md`
- FOUND: commit `4a3a220c`
