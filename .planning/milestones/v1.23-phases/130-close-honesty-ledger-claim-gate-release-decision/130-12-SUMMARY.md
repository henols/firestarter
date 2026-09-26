---
phase: 130-close-honesty-ledger-claim-gate-release-decision
plan: 12
subsystem: release-process
tags: [release-notes, honesty-ledger, claim-gate, py32f071, usb-identity, dfu]

requires:
  - phase: 130-close-honesty-ledger-claim-gate-release-decision plan 11
    provides: 130-LEDGER.md, the single permitted-wording source both bodies match
provides:
  - 130-RELEASE-NOTES-fw.md, the committed-draft firmware b15 release body
  - 130-RELEASE-NOTES-app.md, the committed-draft host app b15 release body
affects: [130-13, 130-14, 130-15, 130-16]

tech-stack:
  added: []
  patterns: ["hand-written release body + mechanical claim-scanner + blocking human wording review, never a scanner-only gate"]

key-files:
  created:
    - .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-RELEASE-NOTES-fw.md
    - .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-RELEASE-NOTES-app.md
  modified: []

key-decisions:
  - "Both bodies use two separately headed sections (## What is proven / ## What is NOT proven) rather than the 122 app analog's single combined heading, to satisfy this plan's explicit two-section acceptance criterion."
  - "The words verified/validated/works end to end are avoided entirely in both bodies (not just proximity-scoped to a py32 token), including omitting VERIFIED/CITED sourcing tags that the ledger itself uses internally — those tags belong to the ledger's audit vocabulary, not to outward-facing prose."
  - "The host suite's cited total (1303 tests) is sourced to 130-RESEARCH.md C-13 (measured this session, on the milestone tip) rather than to 127-NONREGRESSION.md's older 1293 figure, because it is the more current re-measurement and 130-LEDGER.md itself carries no single numeric host-suite-total row to cite instead."
  - "Neither body names a tag literal (3.0.0b15 does not appear in either); the bodies refer only to 'this release,' consistent with CONSTRAINT 5 (the observed tag is read after the cut, by plan 130-15)."

patterns-established:
  - "USB-identity disclosure prose: state the interim id, its private-testing status, that it is not an allocated PID, and that the project's own ship gate is unchanged and unsatisfied by the disclosure -- without using the words satisfied/amended/resolved, and without reproducing any FORBIDDEN_PATTERNS phrase even in negated form."

requirements-completed: []  # This plan ticks no requirement ids. CLOSE-02 is discharged by plan 130-16 alone.

coverage: []

duration: 45min
completed: 2026-08-02
status: complete
---

# Phase 130 Plan 12: Hand-Written b15 Release Bodies Summary

**Two committed-draft release bodies (firmware + host app), both scanner-green against `check_permitted_claims.py`, mutually consistent with `130-LEDGER.md`, and posted nowhere — the D-02 operator wording review is queued as step 1 of plan 130-14's hand-off procedure.**

## Performance

- **Duration:** 45 min
- **Started:** 2026-08-02T17:52:00Z (approx.)
- **Completed:** 2026-08-02T18:37:07Z
- **Tasks:** 2
- **Files modified:** 2 created (plus this SUMMARY)

## Accomplishments

- Wrote `130-RELEASE-NOTES-fw.md` — the firmware b15 body, carrying the milestone headline (a PY32F071 image now publishes as a real release asset), the beta-only `_BOARD_CHOICES` gating, the D-11 USB identity statement, the PCB-05 socket-empty instruction with its provisional-pin-map reasoning, and separately headed proven / not-proven sections.
- Wrote `130-RELEASE-NOTES-app.md` — the host app b15 body, leading with the `pip install --pre --upgrade firestarter` command and the zero-assets fact, naming the DFU install path and its beta-only gate, and carrying the same caveat and mock-only ceiling discipline.
- Both bodies pass `check_permitted_claims.py` when named explicitly (`PASS:` exit 0 each), and the default-mode run now transitions to naming only `130-DECISION.md` as missing — the second observation of D-15's all-or-nothing arming, exactly as this plan's `<gate_behavior_you_must_expect>` predicted.
- Confirmed via read-only `gh release list` that `3.0.0b14` remains the newest release in both `henols/firestarter` and `henols/firestarter_app` — nothing was posted by this plan.

## Task Commits

Each task was committed atomically:

1. **Task 1: Write 130-RELEASE-NOTES-fw.md — the firmware b15 body** - `660eb99` (docs)
2. **Task 2: Write 130-RELEASE-NOTES-app.md — the host app b15 body** - `afeef8b` (docs)

**Plan metadata:** this SUMMARY's own commit (docs: complete plan)

## Files Created/Modified

- `.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-RELEASE-NOTES-fw.md` - the firmware b15 committed draft
- `.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-RELEASE-NOTES-app.md` - the host app b15 committed draft

## Decisions Made

- **Two separately headed sections in both bodies**, not the 122 app analog's single combined heading. The plan's acceptance criteria for both tasks explicitly require "two separately headed sections exist for proven and not-proven"; the 122 app analog used one heading (`## What is proven, and what is not`). Followed the plan's literal criterion over the analog's shape for the app body.
- **Avoided the words verified/validated/works-end-to-end entirely**, everywhere in both bodies, rather than relying on `check_permitted_claims.py`'s 3-line proximity window (D-16) to keep them clear of a `py32` token. This includes omitting the ledger's own `[VERIFIED: ...]` / `[CITED: ...]` sourcing-key tags from the outward-facing prose — those tags are the ledger's internal audit vocabulary (per `130-LEDGER.md`'s own "Sourcing key" section), not language for a stranger-facing release note, and every occurrence of the bare word "verified" risked tripping the plan's grep-based acceptance criterion regardless of proximity to a py32 token.
- **Host suite figure sourced to 130-RESEARCH.md C-13's 1303, not 127-NONREGRESSION.md's 1293.** `130-LEDGER.md` itself carries no single row stating a host-suite total; the closest tier row ("The DFU sequence exercised against descriptors and mocks generally") cites `127-NONREGRESSION.md` §2/§5 for the DFU-specific behavior, not a whole-suite count. `130-RESEARCH.md` C-13 measured `1303 passed in 115.66s` this session, on the milestone tip, specifically framed as the figure the app b15 cut is gated on — the more current and more directly relevant number. Recorded here explicitly since it is not a literal ledger-row citation.
- **No tag literal in either body.** Both refer only to "this release"; `3.0.0b15` appears nowhere, satisfying CONSTRAINT 5 (the observed tag is read after the cut, by plan 130-15) without needing a placeholder token that might itself read oddly in outward-facing prose.

## Every proven-section figure, traced to its source

**Firmware body:**

| Figure in `130-RELEASE-NOTES-fw.md` | Source |
|---|---|
| "The PY32F071 target builds clean and links a complete image inside CI... CI run `30722352902`, 22 of 22 steps succeeded" | `130-LEDGER.md` CI-compile-only tier, row "The ARM target configures and compiles" |
| "The published image's version string matches the version CI embeds... that same run's own step summary" | `130-LEDGER.md` CI-compile-only tier, row "The version string is embedded correctly" |
| "A deliberately broken ARM build was rehearsed... CI run `30722537152`" | `130-LEDGER.md` CI-compile-only tier, row "A deliberately-broken ARM leg cannot silently take down the AVR release" |
| "Leonardo -56 B, Uno +22 B, uno328pb +28 B, RAM unchanged" | `130-LEDGER.md` AVR-measured tier, row "AVR flash and RAM recorded for all three targets" |
| "native suite... 141 test cases across 17 suites" | `130-LEDGER.md` AVR-measured tier, row "The native suite passes at its recorded count" |
| "The host app's own test suite passes in full... 1303 tests" | `130-RESEARCH.md` C-13 (measured this session on the milestone tip) — see Decisions Made above; not a literal ledger row |
| "The DFU install sequence... exercised against synthetic USB device descriptors and a mock USB transport" | `130-LEDGER.md` mock-only tier, row "The DFU sequence exercised against descriptors and mocks generally" |
| "The DFU protocol's opcode literals are anchored against the published USB DFU 1.1 specification" | `130-LEDGER.md` mock-only tier, row "DFU opcode anchoring, independently sourced where possible" |

**App body** (figures not already listed above):

| Figure in `130-RELEASE-NOTES-app.md` | Source |
|---|---|
| "The host test suite passes in full... 1303 tests" | `130-RESEARCH.md` C-13, as above |
| "A CI leg installs the `py32` extra and exercises the real `pyusb` import and its actual API surface" | `130-LEDGER.md` negative-space section, HOST-04 bullet, citing `127-NONREGRESSION.md` §3/§6 |
| "The DFU install sequence, including the dialect fork... exercised against synthetic USB device descriptors and a mock transport" | `130-LEDGER.md` mock-only tier, row "The DFU sequence exercised against descriptors and mocks generally" |

## Fact-by-fact agreement table between the two bodies

Every fact stated in both bodies, quoted from each, confirmed to agree rather than merely asserted as consistent:

| Fact | Firmware body's wording | App body's wording | Agree? |
|---|---|---|---|
| No PY32F071 hardware exists | "Nothing in this milestone has ever run on this silicon, and nothing in it can — there is no PY32F071 circuit board anywhere in this project" | "Nothing in this milestone has ever run on this silicon, and nothing in it can." | Yes — identical claim, near-identical wording |
| `firestarter_py32f071.hex` is new this release | "new in this release — `firestarter_py32f071.hex`" | "including, for the first time, `firestarter_py32f071.hex`" | Yes |
| Host suite total | "The host app's own test suite passes in full at its currently recorded total, 1303 tests." | "The host test suite passes in full at its currently recorded total, 1303 tests." | Yes — identical figure and near-identical sentence |
| DFU sequence exercised against mocks/synthetic descriptors | "exercised against synthetic USB device descriptors and a mock USB transport, never against a real device" | "exercised against synthetic USB device descriptors and a mock transport across the host test suite" | Yes |
| Mock-only readback ceiling | "The DFU readback is checked against a mock only... never against a real bootloader." | "The readback-and-verify step... has been checked against a mock device only... never a real bootloader." | Yes |
| Beta-only gate mechanism | "All three are driven by `_BOARD_CHOICES`, a list computed from your installed app's version the moment its CLI module is imported" | "`_BOARD_CHOICES`... is computed from your installed app's version the moment the CLI module is imported" | Yes — near-identical wording |
| No environment-variable escape hatch | "There is no environment variable that turns any of this on early." | "There is no environment variable that turns any of this on early" | Yes — identical sentence |
| Two-claims-never-conflated rule | "A firmware install completing... says nothing about the assembled device driving a PROM's control signals." | "A successful install here means only that bytes were transferred... it says nothing about the assembled programmer working." | Yes — same rule, independently worded |
| USB identity (`1209:0001`) | Full D-11 statement present | Not mentioned (app body instead notes DFU discovery is by USB interface class, not vendor/product id — a distinct fact about the *bootloader's* identity, not the *application descriptor* `usb_cdc.c` sets) | Not contradictory — different subsystems, both individually accurate per `v1.23-FLASH-PATH-DECISION.md` §5(d) |
| ARM CI compile evidence, native suite count, mypy-debt finding, UM1504 residual | Each appears in only one body | Each appears in only one body | Not contradictory — each is scoped to the repo/subsystem it actually describes |

No contradiction found between the two bodies on any fact both mention.

## Claim gate observations (verbatim)

**Firmware body, named explicitly:**
```
PASS: scanned ../130-close-honesty-ledger-claim-gate-release-decision/130-RELEASE-NOTES-fw.md; 1 file(s) carry the required silicon caveat (this PASS is the mechanizable half of the honesty criterion only -- see the module docstring's explicit non-claim)
```
exit 0.

**App body, named explicitly:**
```
PASS: scanned ../130-close-honesty-ledger-claim-gate-release-decision/130-RELEASE-NOTES-app.md; 1 file(s) carry the required silicon caveat (this PASS is the mechanizable half of the honesty criterion only -- see the module docstring's explicit non-claim)
```
exit 0.

**Default mode, after both commits:**
```
FAIL: armed (at least one of the 4 named v1.23 closing artifacts exists) but not all 4 exist -- a half-written close is a hard failure (D-15). Missing: ['/workspaces/.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-DECISION.md']
```
exit 1. **Confirmed: names only `130-DECISION.md`** — three of the four contracted artifacts (`130-LEDGER.md`, `130-RELEASE-NOTES-fw.md`, `130-RELEASE-NOTES-app.md`) now exist; only `130-DECISION.md` (plan 130-13's deliverable) is missing. This is the expected, correct state per this plan's `<gate_behavior_you_must_expect>` — no stub was created to change it.

`python3 -m pytest test_check_permitted_claims.py -q` → `11 passed`, confirmed both before and after both commits.

`grep -c '3.0.0b15'` → `0` in both bodies. `grep -c 'required by pid.codes'` → `0` in both bodies. `grep -ciE '\b(verified|validated|works end to end)\b'` → `0` in both bodies (no citation exception needed — the words were avoided entirely).

`gh release list --repo henols/firestarter --limit 3` and `gh release list --repo henols/firestarter_app --limit 3` both show `3.0.0b14` as the newest release — confirmed both before and after this plan's commits. Both are read-only commands; no privileged command (`gh release create/edit/delete`, `gh workflow run`, `git push`, `git merge` into `beta`, `git tag`, `twine upload`) appears anywhere in this plan's transcript.

## D-02 operator review — owed, not performed here

Per the plan's own design and this phase's structural gate: **neither body has been read and approved by the operator.** That review is **not** a checkpoint in this plan (a `<human-check>` block was read and internalized, not executed as a stop-and-wait gate, per the plan's own reasoning that `--auto`/`--chain` auto-approve human-verify checkpoints, making a checkpoint here decoration rather than protection). The review is queued as step 1 of plan 130-14's written hand-off procedure, ahead of any merge or posting command — no task in this plan, and no other plan executed so far, contains `gh release create`, `gh release edit`, `gh release delete`, `gh workflow run`, `git push`, `git merge` into `beta`, `git tag`, or `twine upload`.

## Deviations from Plan

None — plan executed exactly as written. Two content choices are recorded under "Decisions Made" above (two-heading structure for the app body per the plan's own literal acceptance criterion; the 1303 host-suite figure's exact provenance) because they involved judgment calls worth making explicit, not because they deviate from the plan's instructions.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `130-DECISION.md` (plan 130-13) is the only remaining artifact before the claim gate goes fully green in default mode.
- Both release bodies are ready for the D-02 operator wording review once plan 130-14 queues it; nothing further is needed from this plan to unblock that review.
- No requirement id was ticked by this plan (CLOSE-02 remains the sole responsibility of plan 130-16).

## Self-Check: PASSED

- FOUND: `130-RELEASE-NOTES-fw.md`
- FOUND: `130-RELEASE-NOTES-app.md`
- FOUND: commit `660eb99` (Task 1)
- FOUND: commit `afeef8b` (Task 2)
- Confirmed: `git rev-parse --abbrev-ref HEAD` → `gsd/v1.23-py32f071-integration`

---
*Phase: 130-close-honesty-ledger-claim-gate-release-decision*
*Completed: 2026-08-02*
