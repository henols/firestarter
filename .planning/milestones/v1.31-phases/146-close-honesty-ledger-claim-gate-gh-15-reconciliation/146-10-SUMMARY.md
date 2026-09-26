---
phase: 146-close-honesty-ledger-claim-gate-gh-15-reconciliation
plan: 10
subsystem: docs
tags: [release-notes, claim-gate, CLOSE-05, honesty-ledger]
dependency-graph:
  requires: ["146-08 (146-LEDGER.md)"]
  provides: ["146-RELEASE-NOTES-fw.md", "146-RELEASE-NOTES-app.md"]
  affects: ["146-12 (blocking wording review)", "146-13 (CLOSE-05 tick)"]
tech-stack:
  added: []
  patterns: ["version-agnostic release draft with a single cut-time placeholder", "boundaries stated inside the headline section rather than saved for the end"]
key-files:
  created:
    - .planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-RELEASE-NOTES-fw.md
    - .planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-RELEASE-NOTES-app.md
    - .planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-10-SUMMARY.md
  modified: []
decisions: []
metrics:
  duration: "~30min"
  completed: 2026-08-17
status: complete
---

# Phase 146 Plan 10: Draft the firmware and host release-notes bodies Summary

Drafted `146-RELEASE-NOTES-fw.md` and `146-RELEASE-NOTES-app.md` — version-agnostic firmware and
host prerelease bodies for CLOSE-05, each carrying its bench/controller-class/ARM (firmware) or
timeout/progress/pulse-override (host) boundaries stated in a stranger's terms, both gating green
against the claim gate individually on the **first attempt** (no rewording needed), and both
committed as drafts behind plan 146-12's blocking wording review.

## What was built

**Task 1 — firmware body.** `146-RELEASE-NOTES-fw.md` (7590 bytes) follows the `130-RELEASE-NOTES-fw.md`
spine (named headline section, boundaries stated immediately inside it) with the donor's
claim-word-bearing headings renamed (`## What is proven, stated exactly` → `## What is established`;
`## What is NOT proven` → `## What this release does not establish`). One placeholder token near the
top (`[FILLED IN AT CUT TIME FROM THE OBSERVED RELEASE LISTING — a placeholder, never computed here]`),
no literal prerelease version string anywhere. The headline section states, immediately: the bench
scope (one part/controller/shield revision — Winbond W27C512, `0xda08`, `leonardo`, Rev 2.0), the two
skips (`0x08` needs an AM27C020, `0x0B` needs an M2716/M2732, neither inferred from the `0x07`
result), the controller-class progress boundary (`leonardo`-only, compiled out structurally on
`uno`/`uno328pb`), and the ARM `py32f071` state exactly as `146-ARM-BUILD-RECORD.md` observed it
(one local compile, explicitly a delta and not CI parity, no PY32F071 board anywhere in this
project, neither repository's CI has run any of this milestone's code).

**Task 2 — host body.** `146-RELEASE-NOTES-app.md` (5294 bytes) follows the leaner
`137-RELEASE-NOTES-app.md` spine (install line, what-the-release-page-carries sentence, per-change
what-then-why, an also-in-this-release section, an established/not-established section, an ask)
with its asymmetry heading renamed (`## What is proven, and what is not` → `## What is established,
and what is not`). Describes three user-visible changes in a stranger's terms: long writes no
longer time out and report intra-block progress (`leonardo`-only, with the never-reaches-100%
cosmetic artefact named and filed as backlog 999.30, and the byte-exact guarantee stated so a
partial bar cannot be read as a partial write); a max-pulse failure now names the address and
pulse count instead of surfacing as an opaque transport error; and the `--pulse-us` override, its
bound provenance, its purpose and where the persistent database value lives. Also documents the
corrected write-option surface (`-b`/`--no-blank-check`'s corrected long name, the newly separate
`--skip-erase` carrying its warning at full strength). Both bodies were committed together in one
commit, per this plan's own instruction (`git commit` after Task 2, not after Task 1 — the plan's
own action text for Task 1 says "Do not commit yet").

## Gate runs (PASS lines and negative controls)

**Task 1, firmware body alone**, first attempt:
```
gate_rc=0
PASS: scanned 146-RELEASE-NOTES-fw.md; 1 of 1 caveat-required file(s) carry every caveat their own
rule demands; 0 file(s) carry no caveat requirement under D-11 (...)
```
Second leg: `version_literals=0 claim_word=0 sections=6`. Third leg: `missing=0 narrowing=1
headline_boundary=2` (both "skipped-with-reason" and "one part" present in the first `## ` section,
confirmed by the `awk '/^## /{c++} c<2'` slice). **Negative control performed**: stripping the
headline section's "skipped-with-reason"/"one part" boundary lines from a `/tmp/gsd146` scratch
copy and re-running the same `awk` slice reports `negative_control_headline_boundary=0` — the
locator is live, not vacuous.

**Task 2, each body alone**, first attempt, both green:
```
--- 146-RELEASE-NOTES-fw.md rc=0
PASS: scanned 146-RELEASE-NOTES-fw.md; 1 of 1 caveat-required file(s) carry every caveat...
--- 146-RELEASE-NOTES-app.md rc=0
PASS: scanned 146-RELEASE-NOTES-app.md; 1 of 1 caveat-required file(s) carry every caveat...
green_bodies=2
```
Second leg (app body): `version_literals=0 claim_word=0 missing=0 byte_exact=1 narrowing=1`.

**Negative control (caveat locator, app body)**: stripping `6.25` and `[Ss]ilicon[- ][Mm]argin`
from a scratch copy and running the gate against it:
```
negative_control_rc=1
FAIL: 2 file(s) missing a required 6.25 V ceiling caveat:
  /tmp/gsd146/app_stripped.md: missing required caveat [ceiling-narrowing]: expected a phrase
    matching 'the silicon-margin narrowing that ceiling implies'
  /tmp/gsd146/app_stripped.md: missing required caveat [ceiling-voltage]: expected a phrase
    matching 'the ~6.25 V program-VCC ceiling'
```
The gate itself (not a plan-local grep) named both missing labels — the caveat locator is live.

**Explicitly not run or asserted**: the all-five default-mode run and the fixture suite's
armed-against-real-files leg. Per this plan's own prohibition and the orchestrator's measured
baseline, 146-11 owns both of those observations.

## Placeholder counts

Exactly **one** placeholder token in each body, both using the identical bracketed phrasing
`[FILLED IN AT CUT TIME FROM THE OBSERVED RELEASE LISTING — a placeholder, never computed here]`,
placed once near the top of each file under a `**Version:**` line. Zero literal prerelease version
strings (`version_literals=0` in both bodies).

## Ledger-row mapping (established items, one line per item)

**Firmware body → `146-LEDGER.md`'s four-column claim table:**
1. "A single `protocol_id`-keyed table carries each 27C protocol's shape..." → **Row 1** (Parameter-table dispatch).
2. "The per-byte loop as shipped: fixed-width pulses, verified after each one..." → **Row 2** (Per-byte pulse-to-verify loop, as it ships).
3. "A byte that fails to verify within its protocol's pulse backstop aborts the block..." → **Row 3** (Hard-fail at budget, with address and pulse-count reporting).
4. "One routing-mask function now drives both the pre-write voltage check and every write and error exit..." → **Row 4** (High-voltage routing consolidation and its exit asymmetry).
5. "All three AVR targets build and pass, carrying a named, commit-attributed +96 B flash-band exemption..." → **Row 7** (Test and build position), citing the MERGE-05 exemption from the ledger's opening section.

**Firmware body → not-established items**, each mapped to the ledger's negative space / non-claim cells:
1. "No comparative claim" → ledger Row 2's non-claim cell + "The ceiling, then the asymmetric coverage" §"no comparative claim" (145 D-08).
2. "No claim... about how closely this matches any datasheet's own timing" → ledger §"What no test, gate or review can close", item 4 (paraphrased, cited by line range in the ledger, not quoted here either — the source wording carries a forbidden compound).
3. "`0x08` and `0x0B` remain unvalidated" → ledger negative-space rows 6/7.
4. "Root cause of intermittent single-byte margin failure remains open" → ledger negative-space row 5.
5. "Program-window rail's behaviour under load never instrumented" → ledger negative-space row 4.

**Host body → `146-LEDGER.md`:**
1. "One 27C protocol, `0x07`, validated end to end..." → **Row 2** + "The asymmetric coverage" §"What was validated, and on what."
2. "The `--pulse-us` override exercised on that same part" → **Row 6** (Per-run pulse override, with its bound-provenance narrowed).
3. "The corrected write-option documentation... matches the shipped CLI help text" → `146-CORRECTIONS.md` rows A-1/A-2 (cited in the ledger's "Mechanism corrections" section as host-README adjacency findings owed to plan 146-07).
4. "Both this project's test suites pass locally at measured counts" → **Row 8** (The CI position).

**Host body → not-established items:**
1. "`0x08`/`0x0B` remain unvalidated, skipped-with-reason" → ledger negative-space rows 6/7.
2. "No comparative claim" → ledger Row 2's non-claim cell (145 D-08).
3. "No CI run has exercised any of this milestone's code" → **Row 8**'s load-bearing non-claim.
4. "The residual timeout gap is board-specific" → `143-HOST-RECORD.md` §5 non-claim item 5 (4687 µs `leonardo` / 9375 µs `uno`, cited verbatim from that record's own figures).
5. "The raised program-VCC ceiling" → the ledger's leading "The ceiling" section (quoted from `REQUIREMENTS.md` §"Evidence ceiling").

## Three cross-checks against the firmware body and the host README

**1. Ceiling wording.**
Firmware body: *"The hardware fact that matters most: the raised program-VCC the vendor algorithms
assume for threshold margin — around **6.25 V** above nominal — is unreachable on this shield,
which has no VCC-raise path. This release buys timing, pulse-count and verify fidelity, and **not**
silicon-margin fidelity."*
`firestarter_app/README.md:332-335`: *"The raised program-VCC (around **6.25 V**) some vendor write
algorithms assume for threshold margin is unreachable on this shield, which has no VCC-raise path.
What this host and firmware can deliver is timing, pulse-count and verify fidelity — not
silicon-margin fidelity. This is a hardware-bound limitation, recorded rather than attempted."*
**No divergence** — both name the same figure and the same fidelity/not-fidelity split. No edit
needed.

**2. Controller-class boundary.**
Firmware body: *"Intra-block progress arrives on the `leonardo` controller class only. On
`uno`/`uno328pb`-class controllers the emission is compiled out of the firmware structurally, not
merely absent by chance..."*
`firestarter_app/README.md`: **measured absent** — a whole-file grep for `leonardo|SERIAL_ON_IO|
intra-block|uno328pb|progress|timeout|budget|percent|100%|bar\b` finds only the board-choice
enumeration lines (`:223`, `:251`, `:268`, `:273`, `:276`) and one unrelated `timeout` reference in
a firmware-version-mismatch sentence (`:100`); the app README documents **no** controller-class
progress boundary anywhere. **This is not a divergence** — the README makes no claim the release
note contradicts, it simply does not cover the topic — so no body was edited for this cross-check.
Recorded here as a measured finding rather than a presupposed match, per this plan's own
deviation-recording standard.

**3. Override's bound provenance.**
Firmware body: *"That bound is parity with another programmer's own integer pulse-width field — it
is **not** a wire-type or hardware limit."*
`firestarter_app/README.md:316-317`: *"This bound is parity with another programmer's own integer
width (a uint16), **not** a wire-type or hardware limit. The override replaces the value the host
already sends for this run only — it introduces no new wire field and does not edit the
database..."*
**No divergence** — same provenance, same "not a wire-type or hardware limit" framing, same
no-new-wire-field statement. No edit needed.

## Freeze — blob SHAs and byte counts (recorded here, not in `146-CITATIONS.md`)

| File | `git hash-object` | `wc -c` |
|---|---|---|
| `146-RELEASE-NOTES-fw.md` | `7c5c708eb6037e669d44f13f66a0772e8898c585` | 7590 |
| `146-RELEASE-NOTES-app.md` | `2a9faafdcd53310cae377059d790e78d4c575a1d` | 5294 |

Recorded here per this plan's own instruction, because `146-CITATIONS.md` is 146-11's to touch and
a concurrent sibling must not append to it.

## Deviations from Plan

### Auto-fixed Issues

None — the plan's own action text was followable as written, and both bodies gated green on the
first attempt with no rewording needed.

### Recorded findings (not defects — measured, not presupposed)

**1. Cross-check 2 (controller-class boundary) found no host-README text to compare against.**
`firestarter_app/README.md` documents the `--pulse-us` override and the ceiling paragraph (from
146-07) but never mentions the `leonardo`-only intra-block progress boundary anywhere. This is
recorded as a measured absence, not a divergence requiring a body edit — see "Three cross-checks"
item 2 above.

## D-01 / D-06 / D-11 status

**D-01 held.** No push, merge, tag, release creation, workflow dispatch or package-index publish at
any point. Both bodies are committed **drafts**, explicitly stated as such in both files' own
prose (implicitly, via the placeholder and the absence of any tag) and here: nothing was pushed,
cut, tagged or published in this plan.

**D-06 held.** `fw_porcelain=0` (measured immediately after the commit); `firestarter_app` porcelain
unchanged at its pre-existing 7 lines. Neither sub-repo was created, edited or deleted at any point
— this plan only read `firestarter/doc/PROTOCOLS.md`, `firestarter/README.md`, `firestarter/CLAUDE.md`,
`firestarter_app/README.md` and `firestarter_app/firestarter/cli_handlers.py:546-610` for source
material.

**D-11 held.** Both bodies gate green individually in positional-argument mode (`green_bodies=2`).
No assertion is made anywhere in this plan or its verification about the all-five default-mode run
or the fixture suite's armed-against-real-files leg — both are 146-11's to observe.

**No CLOSE requirement ticked by this plan** (146-13 owns CLOSE-01…CLOSE-05). No `146-CITATIONS.md`
edit. No ROADMAP coverage row moved by Task 1 or Task 2 — the ROADMAP checkbox flip for this plan's
own `- [ ] 146-10-PLAN.md` line happens in a separate, final hand-edited commit per this plan's
`state_and_roadmap_protocol`.

## Self-Check: PASSED

- `146-RELEASE-NOTES-fw.md` exists: FOUND (7590 bytes, blob `7c5c708e`).
- `146-RELEASE-NOTES-app.md` exists: FOUND (5294 bytes, blob `2a9faafd`).
- Commit `1d1bf6c7` exists in `git log`: FOUND.
- Claim gate green against each body alone, both attempts: confirmed by direct re-run above.
