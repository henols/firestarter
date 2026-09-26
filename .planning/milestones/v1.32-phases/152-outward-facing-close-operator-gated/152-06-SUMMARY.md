---
phase: 152-outward-facing-close-operator-gated
plan: 06
subsystem: outward-facing-record
tags: [gh21, gh32, claim-gate, draft-only, OUT-02]
dependency-graph:
  requires: [152-01, 152-02, 152-03, 152-04]
  provides: [152-GH21-COMMENT.md draft]
  affects: [152-15 (posts this draft after the beta merges)]
tech-stack:
  added: []
  patterns: ["152-check-claims.py env-seam scan (FIRESTARTER_CLAIMSCAN_TARGETS_152)"]
key-files:
  created:
    - .planning/phases/152-outward-facing-close-operator-gated/152-GH21-COMMENT.md
  modified: []
decisions:
  - "Used the exact wording from fixtures/clean_control.md for gh#32's closure ('gh#32 was closed on 2026-08-08 as a duplicate fold into gh#21, which stays open') to avoid the narrowed issue-closed gate row."
  - "Named no source-scanning checker script as the erase-hazard control, per the plan's prohibition against citing check_dispatch.py or check_erase_no_vpp.py outward."
  - "Used 'checked against real AT28C hardware' rather than 'verified ... silicon' to avoid the verified-on-silicon false-positive trap noted in known_gate_traps."
metrics:
  duration: "~35 min"
  completed: "2026-08-21"
status: complete
---

# Phase 152 Plan 06: Author the gh#21 comment draft (gh#32 folded) Summary

Authored `152-GH21-COMMENT.md` — the OUT-02 draft quoting the reporter's own report-body strings
(`fw_board_identity: null` and the falsified erase-NA reason), separating the host-side blank-check
fix from the firmware-side write-path fix, naming both install halves, and transcribing what remains
unproven. The draft is frozen and committed; it posts nothing and is not network-facing. Plan 152-15
posts it after the beta merges land.

## Task 1 — Live re-measurement (verbatim)

Re-measured on 2026-08-21, ~15 hours after RESEARCH §D's 2026-08-21 baseline. **No delta found —
every fact matches RESEARCH exactly.**

- `gh issue view 21 --repo henols/firestarter_prom --json number,title,state,author,createdAt,comments`:
  - `number`: 21
  - `title`: "[dev test] at28c256 — FAIL (00e121446ceb)"
  - `state`: **OPEN**
  - `author.login`: **AndersBNielsen**
  - `createdAt`: 2026-08-06T08:21:06Z
  - `comments`: **2** — both authored by `henols`, at `2026-08-08T09:31:07Z` and `2026-08-08T09:46:28Z`
    (the consolidated-reports table and the `devtest-triage` datasheet cross-check). Matches the
    RESEARCH §D baseline of 2.
- `gh issue view 21 --repo henols/firestarter_prom --json body --jq '.body'` — six extracted fields,
  verbatim:
  - `host_version`: `"3.0.0b15"`
  - `fw_board_identity`: `null`
  - `hw_revision`: `"Rev 2.0-class, Override HW: Rev 2.3"`
  - `protocol`: `"13"`
  - `schema_version`: `"1.2"`
  - `generated`: `"2026-08-06T08:20:45Z"`
  - erase step's full reason string: `"protocol 0x0D (28C family) has no erase operation; each page
    write auto-erases internally"`
  - per-step verdict table: id=NA, read=OK, blank-check=BAD, write=BAD (fingerprint
    "indeterminate"), verify=BAD (fingerprint "indeterminate"), erase=NA
- `gh issue view 32 --repo henols/firestarter_prom --json state,stateReason,closedAt`:
  - `state`: **CLOSED**
  - `stateReason`: **COMPLETED**
  - `closedAt`: **2026-08-08T09:31:09Z**
- `git -C /workspaces/firestarter_app show origin/beta:firestarter/cli_handlers.py | grep -n
  fw_board_identity`:
  ```
  2508:    # fw_board_identity stays None: EpromOperator.comm is a transient
  2517:        fw_board_identity=None,
  ```
  **The provenance defect is confirmed still live on the published branch** — 2 matches, both
  confirming `fw_board_identity` is hardcoded `None` at `cli_handlers.py:2514`. This is why the draft
  is authored now but posted only in Plan 152-15, after Plan 152-11's merge.

**Acceptance criteria for Task 1 — all confirmed:**
- `gh issue view 21 --json state --jq '.state'` → `OPEN` ✓
- `gh issue view 32 --json state --jq '.state'` → `CLOSED` ✓
- `grep -c fw_board_identity` on `origin/beta:cli_handlers.py` → 2 (≥1) ✓

## Task 2 — Authoring and gate verification

`152-GH21-COMMENT.md` was authored with six sections: (1) what the report already told us, quoting
`fw_board_identity: null` and naming host version `3.0.0b15`; (2) the erase step's reason string is no
longer true, quoted verbatim, with the software six-byte chip-erase sequence named as the reason
chosen (12 V on this pinout's pin is the hazard avoided); (3) the write and blank-check verdicts as two
separate fixes — host-side (blank-check step now not-applicable) and firmware-side (pre-write blank
check removed, override flag never sent by the host's `dev test` write step, so only v1.32 firmware
picks up the fix); (4) gh#32's closure, in the wording already validated clean in
`fixtures/clean_control.md`;
(5) what's still unproven, transcribing RESEARCH §B-10's list and containing the mandated sentence;
(6) the ask, naming both install halves (`pip install --pre firestarter` and `firestarter fw
--install`) and framing either outcome as useful, without promising a result.

**Verbatim verification output (the plan's `<automated>` block, run exactly):**

```
PASS: scanned 152-GH21-COMMENT.md; 1 of 1 caveat-required file(s) carry every caveat their own rule
demands; 0 file(s) carry no caveat requirement (this PASS is compliance with the forbidden-phrase
table and the per-file caveat rule only -- see the module docstring's explicit non-claim, and note
that a green run alone does not discharge D-03's per-artifact blocking operator wording review)
GATE rc=0
fw_board_identity => 1
auto-erase => 3
fw --install => 1
dev test => 4
gh#32 => 2
No AT28C part was tested at any point in v1.32 => 1
```

(The literal string `support_status` was not found in the draft (0 matches), and neither was
`check_dispatch`. `grep -ciE 'page.size'` was also 0. The report's own host version tag count via
`grep -cE '3\.0\.0b[0-9]+'` was 1 — matching the single quote of `3.0.0b15` in section 1, with no
other release tag appearing anywhere in the draft.)

All acceptance criteria pass, including the exact-count requirement on the mandated caveat sentence
(one initial pass landed the sentence split across a line wrap by the 80-column formatting, which
`grep -c` (no `-i`, whole-string literal) counted as 0; the line was re-joined and the gate re-run
green — see Deviations below).

The paired fixture suite (`test_check_claims_152.py`, 30 legs) was also re-run for extra confidence:
`30 passed in 0.74s`.

## Task 3 — Freeze and handoff data for Plan 152-15

- **Blob SHA:** `5dc0001ffc1e50cc250d9d8f54f5941c4316a0f6`
- **Commit SHA:** `10be45d93be36187e165a3461f44a63609188c29` (short: `10be45d9`)
- **⚠ The blob SHA proves what we intended to send and never what GitHub stored.** The landed proof is
  the body re-read and diff Plan 152-15 performs after posting — per RESEARCH §D-5, body-content
  re-read is the only sound post-check; `updatedAt` is never an oracle (it bumps on comment creation,
  not on edit, and is `null` on every comment at creation time regardless).
- **Baseline comment count Plan 152-15 re-captures immediately before posting:** **2**, captured
  2026-08-21T15:16:17Z via `gh issue view 21 --repo henols/firestarter_prom --json comments --jq
  '.comments | length'`. Plan 152-15 must assert a delta of exactly 1 against this baseline
  immediately before posting, and again immediately after.
- **The exact `gh` invocation Plan 152-15 will use to post:**
  ```
  gh issue comment 21 --repo henols/firestarter_prom --body-file .planning/phases/152-outward-facing-close-operator-gated/152-GH21-COMMENT.md
  ```
- **The exact verification invocation Plan 152-15 will use afterwards:**
  ```
  gh issue view 21 --repo henols/firestarter_prom --json comments --jq '.comments[-1].body' | diff -u - .planning/phases/152-outward-facing-close-operator-gated/152-GH21-COMMENT.md
  ```
- `git status --porcelain -- .../152-GH21-COMMENT.md` is empty — the draft is committed, not dirty.
- `git rev-parse --abbrev-ref HEAD` after committing: `gsd/v1.32-at28c-write-path-root-cause-report-provenance`
  — confirmed still the milestone branch.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The mandated caveat sentence was split by an 80-column line wrap**
- **Found during:** Task 2 verification
- **Issue:** The first draft wrapped "No AT28C part was tested at any point in\nv1.32 — ..." across
  two lines to keep prose at ~100 chars/line, which broke the literal-substring match the acceptance
  criteria and the gate's `no-at28c-part-tested` required-caveat pattern both depend on
  (`grep -c 'No AT28C part was tested at any point in v1.32'` returned 0, and the gate's own
  regex — which tolerates `\s+` between words — still passed, so this was caught by the plan's
  stricter literal-grep acceptance criterion, not by the gate itself).
- **Fix:** Reflowed the paragraph so the mandated sentence sits on one physical line as its own
  sentence, immediately after a paragraph break.
- **Files modified:** `152-GH21-COMMENT.md`
- **Commit:** folded into `10be45d9` (caught before the first and only commit of this file).

No other deviations. Every prohibition in the plan's `must_haves.prohibitions` was honored literally:
no network write of any kind occurred; gh#21 remains open throughout and its body was not edited;
gh#32 was not reopened; no AT28C silicon result, a page-size validation claim, a `0x0D` graduation, or
a community-support-field change was claimed (the literal `support_status` string and any spelling of
"page size" both grep to 0 occurrences in the draft); `-b`/`--no-blank-check` was not recommended; the
deferred deliberate-protection command was not named (Backlog 999.28 was not named either, since the
plan did not require it here and the draft never needed to raise the relock command); no
source-scanning checker script was named as the erase-hazard control; the page-size seam was not
offered as an explanation for the reporter's failure.

## Known Stubs

None. This plan produces a static document; there is no runtime data flow to stub.

## Threat Flags

None. No new network endpoint, auth path, file-access pattern, or schema change was introduced — this
plan authors a draft markdown file and performs read-only `gh`/`git` measurements.

No AT28C part was tested at any point in v1.32.

This ships software-proven and unvalidated on silicon.

## Self-Check: PASSED

- `152-GH21-COMMENT.md` exists: **FOUND**
  (`test -f /workspaces/.planning/phases/152-outward-facing-close-operator-gated/152-GH21-COMMENT.md`)
- Commit `10be45d9` exists: **FOUND** (`git log --oneline --all | grep 10be45d9`)
- Gate re-run on the committed file: rc=0, confirmed above.
