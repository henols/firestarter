---
phase: 151-protection-readability-lock-status
plan: 04
subsystem: protection-readability
tags: [datasheet-sourcing, lock-status, evidence-ceiling, dual-repo-read-only]
dependency-graph:
  requires: []
  provides:
    - "151-SEQUENCES.md: pinned 0x06 AMD Autoselect sector-protect-verify byte table with full citations"
    - "151-SEQUENCES.md: pinned 0x05 Winbond Product-ID boot-block-status byte table with full citations"
    - "OD-4 evidence-ceiling framing stated verbatim (change detector, not a correctness proof)"
  affects:
    - "151-08 (transcribes these tables verbatim into firestarter/include/flash_utils.h)"
tech-stack:
  added: []
  patterns:
    - "datasheet-derived sequence pinning with vendor/document/revision/page/§section citation comments (no element-wise proof possible, per OD-4)"
key-files:
  created:
    - .planning/phases/151-protection-readability-lock-status/151-SEQUENCES.md
  modified: []
decisions:
  - "Operator selected `web-sourced-with-citation` at the plan's Task 1 checkpoint (2026-08-20), restated as final — the sourcing question is not to be re-raised."
  - "The 0x06 read address (SA)+0x02 CONFIRMS CONTEXT.md D-02's prose rather than correcting it."
  - "The 0x05 boot-block-status address/decode is the artifact's lowest-confidence citation, sourced by structural analogy to the already-working manufacturer/device word pair, and flagged explicitly as such — bounded in practice by D-07's --force/unadjudicated_probe gate."
metrics:
  duration: "~35 min"
  completed: 2026-08-20
status: complete
---

# Phase 151 Plan 04: Protection-Status Read Sequences Summary

Sourced and pinned both the `0x06` AMD Autoselect sector-protect-verify and the `0x05` Winbond
Product-ID boot-block-status read sequences as literal byte tables with full
`vendor / document / revision / page / §section` citations in
`.planning/phases/151-protection-readability-lock-status/151-SEQUENCES.md`, under the operator's
explicit `web-sourced-with-citation` checkpoint decision — before any firmware transcribes them.

## What happened

**Task 1 (checkpoint:decision, blocking):** Presented the operator with the two sourcing-path
options from the plan (`operator-drops-pdfs` vs `web-sourced-with-citation`), with the measured
context (no in-tree datasheet covers any `W29C0xx` part; `W27C020.pdf` and `SST39SF0x0A.pdf` are
both traps; `firestarter/doc/PROTOCOLS.md:97,100,103`'s `datasheets/0x05-FLASH-AMD-STD/` citations
do not resolve in the working tree). The orchestrator returned the operator's decision:
**`web-sourced-with-citation`**, selected and restated as final on 2026-08-20.

**Task 2 (auto):** Authored `151-SEQUENCES.md` with all six required `##` headings:

- **`## Sourcing path taken`** — records the operator's decision, its date, and the
  evidence-limitation sentence in plain words: every citation in the artifact points at a document
  not locally held, so a future reader cannot re-check page/section numbers without fetching the
  document.
- **`## Sequence A` (`0x06`)** — mode entry/exit pinned as byte-identical to the existing
  `FLASH_ENABLE_ID`/`FLASH_DISABLE_ID` tables (zero new bytes there); the read address `(SA)+0x02`
  cited to the AMD Am29F040B Autoselect table (Rev. F, p. 11, §"Autoselect Mode"), corroborated by
  `lockable-proms.md`'s own `[1]`/`[4]` footnotes — this **confirms** CONTEXT.md's D-02 prose rather
  than correcting it; decode stated mode-specifically (x8: `00h` unprotected / `01h` protected)
  rather than repeating `lockable-proms.md`'s "generally" hedge; the sector-address problem recorded
  as a design constraint, with the single device-global address named as `SA=0x0000` → read `0x0002`
  per `151-DESIGN.md` §2.
- **`## Sequence B` (`0x05`)** — Product-ID mode entry stated as the same `AA/55/90` as
  `FLASH_ENABLE_ID` (a finding, not an assumption, corroborated by this project's own working
  `flash_util_get_chip_id` chip-ID read on this exact part); status address `0x0002` by structural
  analogy to the already-verified manufacturer/device word pair, decode `0xFF`/`0xFE` corroborated
  by the host's own existing "FF/FE lockout bit" wording
  (`firestarter_app/firestarter/eprom_operations.py:171-172`) — explicitly flagged as **the
  artifact's lowest-confidence citation**, since no Winbond `W29C0xx` datasheet is held anywhere in
  this container; boot-block geometry (`_BOOT_BLOCK_SIZE = 0x4000`) explicitly **not reused**, with
  the 8 KB vs 16 KiB discrepancy recorded.
- **`## What a test over these tables can establish`** — states, using the required words, that the
  strongest available test is a pinned byte table plus citation, a **change detector, not a
  correctness proof**, because `infoic.xml`'s `config` field is the literal string `"NULL"` on all
  101 `0x05` and all 897 `0x06` entries.
- **`## What no artifact may claim`** — all five prohibited claims named: sequence correctness/
  validation; that the `0x05` read returns the correct status; that `0x06` has been exercised on
  silicon (**software-proven and unrun on silicon**); that the v1.17 W29C040 RCA is closed; anything
  about AT28C/`0x0D` silicon validation.
- **`## Measured facts a later reader should not re-derive`** — the broken `PROTOCOLS.md` citations,
  `FLASH_ENABLE_WRITE_PROTECTION`'s dead-code status, `infoic.xml`'s `chip_id` as a mode-entry-only
  positive control, the `W29C020`/`W29C020C`/`W29C022` aliasing/ambiguity pointer to
  `151-DESIGN.md` §5/§6 (not adjudicated here — out of this plan's scope), and the datasheet-tooling
  absence.

## Verification

Both automated `<verify>` legs from the plan passed:

- `test -f` + literal-string `grep -qF` check for `'change detector, not a correctness proof'`,
  `'software-proven and unrun on silicon'`, `'0x5555'`, `'0x2AAA'`, `'Sourcing path taken'` — all
  present.
- The Python structural check (all six `##` headings present; both `## Sequence A` and
  `## Sequence B` bodies each contain a `§`, a page reference, and a revision reference) — passed
  (`OK`).
- No new tracked `.pdf` added to `firestarter_app/datasheets/` (the 4 untracked PDFs counted by the
  plan's grep check pre-date this plan's execution — part of the phase's already-measured 7-file/
  3-tracked inventory).
- `git -C firestarter_app diff --stat pyproject.toml` — empty. No extractor was needed under the
  `web-sourced-with-citation` path.

## Deviations from Plan

None — plan executed exactly as written, including the checkpoint pause and resumption on the
operator's explicit decision.

## Known Stubs

None. The artifact is prose/citation content, not code; there is no rendering path with an empty
data source to stub.

## Threat Flags

None. This plan reads existing repo files and writes one new markdown artifact under
`.planning/`; it introduces no new network endpoint, auth path, file-access pattern, or schema
change at a trust boundary. The threat register's own T-151-14..17/T-151-SC mitigations (citation
discipline, prohibited-claims list, no PDF/extractor added) are satisfied as recorded above.

## Self-Check: PASSED

- `FOUND: .planning/phases/151-protection-readability-lock-status/151-SEQUENCES.md`
- `FOUND: 0d7b46bc` (Task 2 commit, verified via `git log --oneline`)
