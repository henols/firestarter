---
phase: 204-the-command-surfaces-leave-the-firmware
plan: 04

subsystem: firmware-protocol
tags: [message-catalog, codegen-proof, documentation-repair, citation-repair, requirements-reconciliation, deferred-requirement]

requires:
  - phase: 204-01
    provides: "ordinal 6 (CMD_VERIFY / COMMAND_VERIFY) retired end to end; the reserved-ordinal note shape at include/firestarter.h that this plan's D-06 catalog comments and CLAUDE.md repair cite"
  - phase: 204-03
    provides: "ordinal 4 (CMD_BLANK_CHECK / COMMAND_BLANK_CHECK) retired end to end; the pre-deletion tree state that made every citation this plan repairs genuinely false rather than merely about to become false"
provides:
  - "the two orphaned catalog debug ids (DBG_VERIFY_PROM 0x08, DBG_BLANK_CHECK_PROM 0x0B) annotated with their retired-emit-site and never-reuse reason, with a proof the annotation is inert to codegen"
  - "all five firmware documentation citations the ordinal sweep staled, repaired -- plus one pre-existing fabricated test citation found and fixed while touching the same row"
  - "CMP-F1's forward-compatibility finding recorded in REQUIREMENTS.md, and the ROADMAP.md paragraph that nominated phase 204 for the DONE-based clean stop corrected in place to record the offer and the decline (D-12)"
  - "FWCMD-01, FWCMD-02 and FWCMD-03 reconciled from Pending to Complete in REQUIREMENTS.md"
affects: [204-05-bench-matrix, 205-preflights-leave, 207-release-and-docs]

actuals:
  tokens: 5590
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Catalog per-entry comment placed AFTER the [[table.array]] marker and BEFORE its first key, so a split-on-marker presence check finds the annotation in the SAME block as the entry it describes, not the preceding one."
    - "Natural-language paraphrase of a retired C identifier in prose (\"the standalone verify and blank-check command surfaces\", \"blank-check ordinal\") rather than the literal token, so a documentation-only edit does not itself reintroduce the string a source-presence gate forbids."
    - "Doc-only commit BEFORE re-running a whole-repo-porcelain-sensitive test leg, not after -- an uncommitted doc edit trips porcelain gates unrelated to the edit's own content, and committing first restores the baseline the gate expects."

key-files:
  modified:
    - tools/catalog/messages.toml
    - firestarter_fw/CLAUDE.md
    - firestarter_fw/PROTOCOLS.md
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "Placed the two catalog comments between the `[[debug.messages]]` array-of-tables marker and the entry's `id =` line, not before the marker -- the plan's own verify script splits the file on the literal marker string, and a comment placed before the marker lands in the PRECEDING entry's block, making the presence assertion report the wrong entry count (measured: 4 matching blocks instead of 2 on first attempt, corrected by repositioning)."
  - "Rephrased two doc repairs to avoid the literal `CMD_VERIFY` / `CMD_BLANK_CHECK` identifiers even in explanatory prose about their retirement -- the acceptance criterion is textual absence of the identifier anywhere in the file, not just in a still-live context, and an early draft using the identifiers to explain their own retirement failed that check on first run."
  - "Committed the two firmware documentation files BEFORE re-running `pytest tests/`, not after -- with the edits uncommitted, two additional tests in test_trace_segment_exhaustiveness_v131.py failed on an unrelated whole-repo-porcelain assertion (checking `git status --porcelain` of the whole firmware repo, not just the files this plan touched). Committing restored the tree to the expected clean baseline and the failure count returned to exactly 17, all confined to test_flash_path_record_sync.py, matching the measured pre-plan baseline."
  - "Marked FWCMD-01/02/03 Complete in a separate, later commit rather than folding it into Task 3's own commit -- Task 3's acceptance criteria required its commit to touch exactly REQUIREMENTS.md and ROADMAP.md's CMP-F1/nomination content with no requirement checkbox changing state, so the wave-context-instructed reconciliation is its own commit."

requirements-completed: [FWCMD-02, FWCMD-03]

coverage:
  - id: D1
    description: "DBG_VERIFY_PROM (0x08) and DBG_BLANK_CHECK_PROM (0x0B) keep their catalog entries unchanged in id/name/format/params, each gaining a comment naming its retired emit site, the 3.1.0 release, and the never-reuse reason"
    requirement: FWCMD-02
    verification:
      - kind: unit
        ref: "command: python3 presence/comment-count assertion over tools/catalog/messages.toml (see Task 1 Commits section) -- both ids present, exactly one annotated block each, both name 3.1.0"
        status: pass
    human_judgment: false
  - id: D2
    description: "Regenerating the cpp header and the python module from the amended catalog to a temporary path produces output byte-identical to what firestarter_fw and firestarter_app already carry; the catalog validator exits zero; neither sub-repo has a modified file after this task; the sync script was not run"
    requirement: FWCMD-02
    verification:
      - kind: unit
        ref: "command: python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check (validator); two mktemp-target regenerations diffed against firestarter_fw/include/messages.h and firestarter_app/firestarter/messages.py; git status --porcelain in both sub-repos"
        status: pass
    human_judgment: false
  - id: D3
    description: "Neither firestarter_fw/CLAUDE.md nor PROTOCOLS.md names either retired ordinal identifier anywhere, including in the prose explaining their retirement"
    requirement: FWCMD-03
    verification:
      - kind: unit
        ref: "command: python3 source-absence assertion for CMD_VERIFY / CMD_BLANK_CHECK over both files, run after the commit"
        status: pass
    human_judgment: false
  - id: D4
    description: "The native-test-registration paragraph states the measured two-line cost and names the shared native_base platformio.ini section as the reason, replacing the stale four-line claim"
    requirement: null
    verification:
      - kind: unit
        ref: "command: python3 assertion that 'four new lines' is absent and 'native_base' is present in firestarter_fw/CLAUDE.md, plus a direct read of platformio.ini's [native_base] test_filter/-I lists confirming both native environments extend it"
        status: pass
    human_judgment: false
  - id: D5
    description: "The INV-05 row is restated without the retired ordinal and its citation repointed from a test name absent anywhere in the tree to a real test that asserts the invariant"
    requirement: null
    verification:
      - kind: unit
        ref: "command: git grep -in for the old name (test_inv05_eprom_vpp_skip_on_read, zero hits before and after); python3 assertion confirming the stale name is absent and exactly one INV-05 row exists; direct read confirming test_eprom_0x07_read_configure_only_does_not_enable_vpp exists at test/native/avr/test_val_eprom/test_val_eprom.cpp and asserts VPP is not set at CMD_READ configure time for protocol 0x07"
        status: pass
    human_judgment: false
  - id: D6
    description: "Both firmware test trees stay at their measured baseline after the documentation commit: pytest tests/ 17 failed (all confined to test_flash_path_record_sync.py) / 303 passed, pio test -e native_nodevtools 243/243"
    requirement: null
    verification:
      - kind: unit
        ref: "command: pytest tests/ -o addopts=\"\" -p no:cacheprovider -q (post-commit); pio test -e native_nodevtools"
        status: pass
    human_judgment: false
  - id: D7
    description: "The commit in firestarter_fw touches exactly CLAUDE.md and PROTOCOLS.md"
    requirement: null
    verification:
      - kind: unit
        ref: "command: git show --name-only --format=\"\" HEAD in firestarter_fw"
        status: pass
    human_judgment: false
  - id: D8
    description: "CMP-F1's row carries the forward-compatibility finding and names where it came from; the ROADMAP.md paragraph records the offer and the decline and points at D-12; no requirement checkbox changes state in that commit"
    requirement: null
    verification:
      - kind: unit
        ref: "command: python3 row-content assertions over REQUIREMENTS.md and ROADMAP.md (forward-compatible/204 present; D-12/declined present); before/after '- [x]' count comparison over REQUIREMENTS.md across the commit (16 -> 16, unchanged)"
        status: pass
    human_judgment: false
  - id: D9
    description: "FWCMD-01, FWCMD-02 and FWCMD-03 are reconciled from Pending to Complete in REQUIREMENTS.md's checkbox list and traceability table, in their own commit separate from the CMP-F1/roadmap record commit"
    requirement: null
    verification:
      - kind: unit
        ref: "command: git diff --stat + git diff content review confirming exactly the six intended `- [ ]`/`Pending` -> `- [x]`/`Complete` line changes, no other line touched"
        status: pass
    human_judgment: false
  - id: D10
    description: "All three repositories stay on v1.41-verification-to-host throughout; no branch is beta at any point; nothing is pushed; the meta gitlink for firestarter_fw advances to match its new HEAD after the documentation commit"
    requirement: null
    verification:
      - kind: unit
        ref: "command: git rev-parse --abbrev-ref HEAD in each of the three repositories (all v1.41-verification-to-host); git ls-tree HEAD firestarter_fw firestarter_app compared against each sub-repo's git rev-parse HEAD (match)"
        status: pass
    human_judgment: false

duration: "~20min (commit-to-commit span 10:40:58Z-10:45:22Z for the four meta+fw commits; reading, catalog proof, doc repair drafting and verification preceded the first commit)"
completed: 2026-09-22
status: complete
---

# Phase 204 Plan 4: The orphaned-id, documentation and deferral record closed out

**Annotated the two orphaned catalog debug ids with a proven-inert codegen comment, repaired all five documentation citations the ordinal sweep staled plus one pre-existing fabricated test name, and recorded CMP-F1's forward-compatibility finding while correcting the roadmap's declined nomination -- with FWCMD-01/02/03 reconciled to Complete.**

## Performance

- **Duration:** ~20 min (see frontmatter `duration` for the measured commit span; reading and verification preceded it)
- **Started:** 2026-09-22 (session start; no fixed epoch recorded)
- **Completed:** 2026-09-22T10:46:10Z
- **Tasks:** 3 automated tasks, no checkpoints, plus one wave-context-instructed requirements reconciliation
- **Files modified:** 7 across two repositories (1 meta catalog file, 2 firmware docs, 4 meta planning files) plus 1 meta gitlink advance

## Accomplishments

- `DBG_VERIFY_PROM` (0x08) and `DBG_BLANK_CHECK_PROM` (0x0B) each gained a comment recording their retired emit site (the wrappers plans 01/03 deleted), the `3.1.0` release, and the never-reuse reason (D-06) -- with a measured proof that the annotation changes no generated output: both `messages.h` and `messages.py` regenerate byte-identical to what both sub-repos already carry, to a temporary path, never in place.
- Repaired all five stale firmware documentation citations named in the plan: `CLAUDE.md`'s protocol-dispatch summary (now names only `CMD_READ`/`CMD_WRITE`, with a clause on the retired surfaces), `CLAUDE.md`'s native-test-registration cost (corrected 4 lines -> 2, naming the shared `[native_base]` `platformio.ini` section as the reason), `PROTOCOLS.md`'s VPP-behaviour sentence (restated for the read path alone), `PROTOCOLS.md`'s erase-model paragraph's final clause (blank is now a host-side read-and-compare sending no ordinal, not a firmware handler arm), and the INV-05 row (restated without the retired ordinal, cited test repointed to a real one).
- Found and fixed one pre-existing defect while repairing the INV-05 row: its citation, `test_inv05_eprom_vpp_skip_on_read`, exists nowhere in the tree (`git grep` confirms zero hits before and after this plan). Repointed to `test_eprom_0x07_read_configure_only_does_not_enable_vpp` in `test/native/avr/test_val_eprom/test_val_eprom.cpp`, a real test that asserts VPP is not set at `CMD_READ` configure time for protocol `0x07` -- exactly the invariant the row states.
- CMP-F1 in `.planning/REQUIREMENTS.md` now carries the measured forward-compatibility finding behind D-12: pre-`3.1.0` firmware's `op_get_message` already parses `"DONE"` into its own enumeration value and `op_wait_for_ack` already ignores it, so a future host sending it degrades to today's one-second timeout path -- the change is forward-compatible by construction. The row also states why both sides must move together (the host's `_drive_region_compare` discrimination keys on the timeout error code a clean stop would no longer produce).
- The `.planning/ROADMAP.md` paragraph nominating phase 204 by name for the `DONE`-based clean stop is corrected in place, not deleted, to record that it was offered there and declined (D-12), with the reason and a pointer to the phase CONTEXT decision.
- FWCMD-01, FWCMD-02 and FWCMD-03 reconciled from Pending to Complete in `.planning/REQUIREMENTS.md` (both checkbox list and traceability table), per the wave-context instruction -- FWCMD-01 was deliberately left unmarked by plan 03 pending this plan's completion of FWCMD-02/03.

## Task Commits

This plan spans two repositories; commits are grouped by task, plus the meta repository's gitlink advance and the requirements reconciliation.

1. **Task 1: Comment the two orphaned debug ids, prove codegen output unchanged** -- meta `694acce3` (docs)
2. **Task 2: Repair every firmware documentation citation the sweep staled** -- firmware `24e3fdf` (docs)
3. **Task 3: Record the deferred clean stop on CMP-F1, correct the roadmap's nomination** -- meta `4f68d871` (docs)
4. **Gitlink advance: firestarter_fw -> 24e3fdf** -- meta `a678048e` (chore)
5. **Requirements reconciliation: FWCMD-01/02/03 -> Complete, mark plan progress** -- meta `b3f859ed` (docs)

**Plan metadata:** this SUMMARY's own commit, made after this file, together with `.planning/STATE.md`.

_Total: 4 commits in the meta repository (measured: `git rev-list --count 48793c2d..HEAD` before the SUMMARY commit = 4), 1 commit in `firestarter_fw`, 0 commits in `firestarter_app` (untouched by this plan). `plan_head_before` (meta): `48793c2d6ddf163625e044c8c90d9ce1fe3706fb`._

## Files Created/Modified

- `tools/catalog/messages.toml` -- two comment blocks added, no entry's id/name/format/params changed (Task 1).
- `firestarter_fw/CLAUDE.md` -- dispatch-summary sentence and native-test-registration paragraph repaired (Task 2).
- `firestarter_fw/PROTOCOLS.md` -- VPP-behaviour sentence, erase-model final clause, and the INV-05 row repaired (Task 2).
- `.planning/REQUIREMENTS.md` -- CMP-F1 row extended with the D-12 finding (Task 3); FWCMD-01/02/03 marked Complete (reconciliation).
- `.planning/ROADMAP.md` -- the clean-stop nomination paragraph corrected in place (Task 3); the 204-04-PLAN.md wave-4 checkbox marked complete (reconciliation).
- `.planning/STATE.md` -- frontmatter and Session section updated to reflect this plan's completion.

## Decisions Made

See frontmatter `key-decisions` for the three implementation decisions (catalog comment placement relative to the array-of-tables marker; avoiding literal retired identifiers even in explanatory prose; committing the doc repair before re-running the porcelain-sensitive pytest leg).

## Deviations from Plan

None beyond the two self-corrections captured in `key-decisions` above (comment placement, identifier phrasing), both caught and fixed by the plan's own verify scripts before any commit landed -- neither reached a committed state in its broken form, so neither is tracked as a deviation rule application; they are documented as decisions instead.

## Issues Encountered

The plan's task 2 acceptance criteria implicitly assumed a clean starting tree when running `pytest tests/` before the commit. With the two documentation edits uncommitted, two additional legs in `test_trace_segment_exhaustiveness_v131.py` failed on a whole-repo-porcelain assertion unrelated to this plan's content (19 failed instead of the expected 17). Resolved by committing the documentation files first, then re-running the leg, which returned to the measured 17-failure baseline (all confined to `test_flash_path_record_sync.py`) and 243/243 on `native_nodevtools`. No source or test file was altered to work around this; the tree was simply put back into the state the gate expects.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 204-05 (the four-role bench matrix on silicon) can proceed. It needs no record-keeping from this plan beyond what already exists; the D-07 label-substitution note in `204-CONTEXT.md` is unaffected by this plan.
- All catalog, documentation and planning-record work FWCMD-02 and FWCMD-03 required is complete; FWCMD-06, REL-02 and REL-03 remain Pending and are 204-05's declared scope.
- Both firmware test trees are at their pre-plan-04 measured baseline: `pytest tests/` 303 passed / 17 failed (all `test_flash_path_record_sync.py`), `pio test -e native_nodevtools` 243/243.
- All three repositories remain on `v1.41-verification-to-host`; no branch touched `beta` at any point; nothing was pushed. Meta gitlinks match both sub-repos' HEADs.

---
*Phase: 204-the-command-surfaces-leave-the-firmware*
*Completed: 2026-09-22*

## Self-Check: PASSED

All key files verified present on disk (`tools/catalog/messages.toml`, `firestarter_fw/CLAUDE.md`, `firestarter_fw/PROTOCOLS.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`); all five commits (`694acce3`, `4f68d871`, `a678048e`, `b3f859ed` in the meta repository; `24e3fdf` in `firestarter_fw`) verified present in `git log --oneline --all` in their respective repositories.
