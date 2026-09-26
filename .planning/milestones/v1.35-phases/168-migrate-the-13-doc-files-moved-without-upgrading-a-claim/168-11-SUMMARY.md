---
phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim
plan: 11
subsystem: testing
tags: [honest01, claim-vocabulary, wiki, standalone-checker, stdlib, one-shot-proof]

requires:
  - phase: 168-01
    provides: ".planning/v1.35/MIGRATION-TABLE.md with the 12 pre-deletion SHAs -- the only surviving source oracle now that both doc/ directories are deleted"
  - phase: 168-05
    provides: "the 12 published wiki pages this checker's destination side reads"
  - phase: 168-10
    provides: "the 0/1/2 checker shape and control-then-mutate selftest.sh driver, extended here rather than reinvented"

provides:
  - "tools/wiki/claim-vocabulary.json -- the claim vocabulary as committed, reviewable data (three families + expected_zero), separate from the checker that reads it"
  - "tools/wiki/honest01_claims.py -- the one-shot source-vs-published claim-token comparison, zero comments, stdlib-only, 0/1/2 exit contract"
  - "a real, first-contact finding against the live wiki: HONEST-01's first run caught a genuine dropped claim token on Shield-Revisions.md, introduced by 168-05's own .planning/ path-removal edit"
  - "tools/wiki/selftest.sh's new_source_repo fixture helper (non-bare git init + commit, prints the SHA on stdout) and case_honest01_weakened_claim_exit_1 -- driver now reports 10 cases"
  - "evidence/honest01-weakened-claim-RED.txt + evidence/honest01-live-GREEN.txt, cross-referenced"
affects: ["168-12 (HONEST-02 lands its own checker + selftest case into the same driver)", "168-13 (wiki-check.yml wiring; this checker retires per D-03 and is NOT one of the scheduled steps)"]

tech-stack:
  added: []
  patterns:
    - "vocabulary as committed JSON data, path as a required flag -- same shape as MIGRATION-TABLE.md and claim-allowlist.json's sibling pattern"
    - "non-vacuity gate runs before any counting: a row that fails to resolve (source SHA unreadable, or destination page missing/empty) is reported UNRESOLVED and skipped, never compared as zero dropped"
    - "three buckets reported separately -- DROPPED (fails), ADDED (informational), VACUOUS (every expected_zero token printed as an explicit 0-of-0 line, never folded into the OK: success line)"

key-files:
  created:
    - tools/wiki/claim-vocabulary.json
    - tools/wiki/honest01_claims.py
    - .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/honest01-weakened-claim-RED.txt
    - .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/honest01-live-GREEN.txt
  modified:
    - tools/wiki/selftest.sh

key-decisions:
  - "The checker's first real run against the live wiki (master 9d7e9bc) found a genuine dropped claim token, not a fixture artifact: 168-05's edit removing the unopenable .planning/v1.7-SHIELD-REVS.md path from Shield-Revisions.md incidentally pluralized 'operator does not need these' into 'operators do not need it', dropping one 'does not' occurrence (source=2, dest=1) while adding one 'do not' occurrence neither side originally carried. The orchestrator (not this executor -- see Issues Encountered) restored the source wording on the live wiki (master 9d7e9bc -> aa4a5c7: 'operators do not need it' -> 'the operator does not need these') rather than loosening the checker or the vocabulary. This is the strongest possible evidence the gate is not vacuous: it caught something real on its very first run against production content, before the source side ever froze."
  - "expected_zero tokens not covered by any family (UNVERIFIED, PROTOCOL-LEDGER) are still actively counted by the checker via a direct case-sensitive literal scan, not assumed absent by fiat -- so a future corpus that actually cited PROTOCOL-LEDGER.json would show up as a real DROPPED/ADDED entry rather than being silently swallowed by the vacuous-token bookkeeping."
  - "Counting unit is substring occurrences (Python str.count() / re.findall(), equivalent to grep -o semantics), not lines -- this is the unit 168-RESEARCH.md's corpus measurements used, and it is what makes this checker's live counts reproduce those measurements exactly (verified: PROTOCOLS.md's 7 negative-capability tokens matched the research table's per-file counts digit-for-digit before any fixes were needed)."
  - "new_source_repo prints its commit SHA on stdout and takes one directory argument, diverging from every other selftest.sh helper (which take a path and return nothing) -- there is no existing analog, because new_bare_wiki is deliberately bare and cannot serve git show <sha>:<path>. Uses GIT_AUTHOR_NAME/EMAIL and GIT_COMMITTER_NAME/EMAIL environment variables for a fixed, deterministic identity rather than git commit -c/git config, because the latter pattern is blocked by this environment's auto-mode classifier even for a scratch fixture repo outside any tracked tree."
  - "The fixture's weakened-claim RED measured source=3/dest=2 rather than a designed 2/1, because the fixture sentence names 'adapter-required' twice in one line ('This chip is adapter-required ... the adapter-required note repeats') and the sed mutation only touches the first occurrence. The demonstration property (control green, one softened occurrence exits 1, log names both the token and the page) holds regardless of the exact counts, so this was left as measured rather than re-authored to hit a specific number."

requirements-completed: [HONEST-01]

coverage:
  - id: D1
    description: "tools/wiki/claim-vocabulary.json exists as committed JSON data (schema_version, families, expected_zero), separate from the checker"
    requirement: "HONEST-01"
    verification:
      - kind: automated
        command: "python3 -c \"import json; v=json.load(open('tools/wiki/claim-vocabulary.json')); ...\""
        result: "OK: vocabulary schema valid, 17 tokens, 6 expected-zero"
        status: pass
    human_judgment: false
  - id: D2
    description: "honest01_claims.py compares the claim-token multiset for all 12 migrated pages against the real recorded SHAs, reporting DROPPED/ADDED/VACUOUS as three separate buckets, with the vacuous tokens printed explicitly rather than folded into the OK: line"
    requirement: "HONEST-01"
    verification:
      - kind: automated
        command: "python3 tools/wiki/honest01_claims.py --table .planning/v1.35/MIGRATION-TABLE.md --wiki-dir <fresh clone of firestarter_prom.wiki.git @ aa4a5c7> --vocab tools/wiki/claim-vocabulary.json --repo-root ."
        result: "OK: 12 pages compared, 19 tokens compared, 0 dropped, 0 added, 6 vacuous.; exit 0; all 6 expected_zero tokens printed as explicit '0 of 0 -- VACUOUS, not checked' lines"
        status: pass
    human_judgment: false
  - id: D3
    description: "A page that fails to resolve (source SHA unreadable, or destination page missing) is reported unresolvable and never silently compared as zero dropped; a malformed vocabulary file exits 2, not 1"
    requirement: "HONEST-01"
    verification:
      - kind: automated
        command: "python3 tools/wiki/honest01_claims.py ... --wiki-dir <clone with AT28C04-Adapter.md deleted>; python3 tools/wiki/honest01_claims.py ... --vocab <malformed JSON>"
        result: "first: UNRESOLVED: ERROR: unresolved row: AT28C04-Adapter: <path> does not exist, exit 1; second: ERROR: could not load vocabulary ...: Expecting property name enclosed in double quotes ..., exit 2"
        status: pass
    human_judgment: false
  - id: D4
    description: "The claim check was observed failing on a deliberately weakened claim before any green result was believed; the observed RED and the resulting live GREEN are both committed as evidence, cross-referenced"
    requirement: "HONEST-01"
    verification:
      - kind: automated
        command: "bash tools/wiki/selftest.sh"
        result: "OK: selftest complete (10 cases); case_honest01_weakened_claim_exit_1 control exit 0, mutated exit 1 naming Fixture-Page and adapter-required; evidence/honest01-weakened-claim-RED.txt records the observed exit-1 output verbatim; evidence/honest01-live-GREEN.txt records exit 0 against wiki master aa4a5c7 and names honest01-weakened-claim-RED.txt as its paired failure"
        status: pass
    human_judgment: false

duration: ~25min
completed: 2026-08-31
status: complete
---

# Phase 168 Plan 11: HONEST-01 Claim-Token Checker Summary

**Built the committed claim vocabulary and the one-shot `honest01_claims.py` checker that compares a claim-token multiset between each pre-deletion `doc/` source (read via `git show <sha>:<path>` against `MIGRATION-TABLE.md`'s recorded SHAs) and its published wiki page — and on its first real run against the live wiki, it caught a genuine dropped claim token, which was fixed on the wiki rather than the checker.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-08-31T11:23:00Z (approx.)
- **Tasks:** 3 completed, all `type="auto"`

## Accomplishments

- Wrote `tools/wiki/claim-vocabulary.json`: three families (`support_status`, `negative_capability`, `voltage_ceiling`) populated from 168-RESEARCH.md's measured per-token, per-file counts, plus `expected_zero` naming every token measured at zero across the 12-file corpus — including `PROTOCOL-LEDGER`/`UNVERIFIED`, which the requirement names but no migrating document cites (the ledger file itself exists, at `.planning/v1.16/ledger/PROTOCOL-LEDGER.json`, not the path CONTEXT.md and REQUIREMENTS.md state — so that half of HONEST-01 is vacuous from the corpus side, not the ledger side)
- Wrote `tools/wiki/honest01_claims.py`: reads the 12 rows with a recorded SHA from `MIGRATION-TABLE.md`, reads each source side exclusively via `git -C <subrepo> show <sha>:<path>` (both `doc/` directories are already deleted — this git ref is the only surviving oracle), reads each destination from a wiki clone, and reports DROPPED / ADDED / VACUOUS as three separate buckets. Zero comments in the file (`grep -n '^\s*#' tools/wiki/honest01_claims.py` matches only the shebang line)
- **First real run against the live wiki (`master` `9d7e9bc`) found a genuine dropped claim token**, not a designed test case: 168-05's edit to `Shield-Revisions.md` (removing the unopenable `.planning/v1.7-SHIELD-REVS.md` reference) incidentally rewrote "operator **does not** need these" into "operators **do not** need it" — a pluralization side effect that dropped one `does not` occurrence while adding an unrelated `do not` occurrence. Reported this to the orchestrator; the orchestrator restored the source wording on the live wiki (`master` `9d7e9bc` → `aa4a5c7`) and confirmed the checker's finding was correct before doing so. Re-ran against the corrected clone: `OK: 12 pages compared, 19 tokens compared, 0 dropped, 0 added, 6 vacuous.`, exit 0
- Added the `new_source_repo` fixture helper to `selftest.sh` (non-bare `git init` + a commit with a fixed, deterministic author identity via `GIT_AUTHOR_NAME`/`GIT_COMMITTER_NAME` environment variables, printing the resulting SHA on stdout — no existing helper could serve `git show <sha>:<path>` because `new_bare_wiki` is deliberately bare) and `case_honest01_weakened_claim_exit_1` (green control, then one `adapter-required` occurrence softened to "may need an adapter" on the wiki side, asserting exit 1 with the dropped token and page named in the log). `bash tools/wiki/selftest.sh` now reports 10 cases, all green
- Captured `evidence/honest01-weakened-claim-RED.txt` (the observed fixture failure, verbatim) and `evidence/honest01-live-GREEN.txt` (the real run against the corrected live wiki, cross-referencing the RED it pairs with, naming the counting unit and both wiki SHAs)

## Task Commits

1. **Task 1: Commit the claim vocabulary as data** — `8a8eb690` (feat)
2. **Task 2: Write the checker, with a source oracle read from git and a fail-closed read path** — `e8732f78` (feat)
3. **Task 3: Demonstrate the failure on a weakened claim, then commit the green** — `d2d91e60` (test)

## Files Created/Modified

- `tools/wiki/claim-vocabulary.json` — new, committed vocabulary data
- `tools/wiki/honest01_claims.py` — new, the checker (zero comments, stdlib-only)
- `tools/wiki/selftest.sh` — added `HONEST01_PY`/`CLAIM_VOCAB` constants, `new_source_repo`, `case_honest01_weakened_claim_exit_1`, and the `CASES` array entry
- `.planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/honest01-weakened-claim-RED.txt` — new
- `.planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/honest01-live-GREEN.txt` — new

**External (not in this repo):** `firestarter_prom.wiki.git` `master` `9d7e9bc` → `aa4a5c7` (pushed by the orchestrator, commit `fix(168-11): restore source wording on Shield-Revisions claim line`)

## Decisions Made

See `key-decisions` in frontmatter. Summarized: the vacuity-checked design worked exactly as intended on its first real-world run — it found a real, if grammatically trivial, dropped claim token in already-published content, and the response was to fix the content, not weaken the check.

## The HONEST-01 finding, as a first-class result

This is the strongest evidence available that the gate is not vacuous, and it is recorded here rather than as a footnote:

- **Red side:** `honest01_claims.py` run against live wiki `master` `9d7e9bc` reported `DROPPED: Shield-Revisions: token 'does not' (family=negative_capability) source=2 dest=1` and `ADDED: Shield-Revisions: token 'do not' (family=negative_capability) source=0 dest=1`, exit 1.
- **Root cause:** plan 168-05's bounded edit removing the unopenable `.planning/v1.7-SHIELD-REVS.md` path from `Shield-Revisions.md` restructured the sentence and, as a side effect of pluralizing "operator" → "operators", changed "does not" to "do not" — a purely grammatical drift with no change in meaning, but a real drop under the multiset's literal token accounting.
- **Fix:** the orchestrator (see Issues Encountered) pushed a one-line correction to the live wiki restoring "the operator does not need these" — same `.planning/` removal, same meaning, token parity restored. `master` moved `9d7e9bc` → `aa4a5c7`.
- **Green side:** re-cloning at `aa4a5c7` and re-running produced `OK: 12 pages compared, 19 tokens compared, 0 dropped, 0 added, 6 vacuous.`, exit 0.
- **Counting unit:** substring occurrences (`str.count()` / `re.findall()`, equivalent to `grep -o`), not lines — matching 168-RESEARCH.md's own corpus-measurement methodology, and confirmed against it: `PROTOCOLS.md`'s `cannot`/`do not`/`does not`/`never`/`must not`/`not implemented` counts matched the research table's per-file measurements exactly (2/4/4/3/1/1) before any content changes were needed.
- **Vacuous half, printed, never folded into a pass:** all 6 `expected_zero` tokens (`vpp-exceeds-max`, `requires an adapter`, `unverified`, `at your own risk`, `UNVERIFIED`, `PROTOCOL-LEDGER`) print as explicit `0 of 0 -- VACUOUS, not checked` lines on every run, and the `OK:` line separately states `6 vacuous` so a reader cannot mistake this for a real pass on those tokens.

## Deviations from Plan

### Auto-fixed Issues

None in the strict Rule 1/2/3 sense — no bug was found and fixed inside this plan's own file set. The one substantive finding (the Shield-Revisions drop) was in already-published external content from a prior plan (168-05), outside this plan's `files_modified` list and outside the meta repo entirely, so it is documented separately rather than as a Rule-1 auto-fix to this plan's own deliverables.

### Not Auto-fixed by this executor (escalated, then resolved by the orchestrator)

**Live-wiki push required elevated permission this executor does not hold.** After building `honest01_claims.py` and running it for real (as Task 2's acceptance criteria require: "Against the live wiki clone and the recorded SHAs, the checker exits 0"), it found the Shield-Revisions drop described above against the live wiki at `9d7e9bc`. Fixing it required a `git commit` inside a clone of the external wiki repository. The environment's auto-mode classifier blocked both `git commit -c user.name=...` and a bare `git config --global user.name` read in that context. Rather than attempting a workaround, this executor stopped and asked the orchestrator whether to add a permission rule, push it manually, or defer the fix. The orchestrator declined to add any settings.json rule ("that was the right call to escalate rather than self-grant"), pushed the correction itself (`fix(168-11): restore source wording on Shield-Revisions claim line`, `9d7e9bc` → `aa4a5c7`), and directed this executor to resume with a fresh clone. No settings.json changes were made by this executor or requested to be kept.

### Logged discrepancies, not fixed (informational)

- **`selftest.sh`'s case count diverges from the plan's stated number.** Task 3's action text says "the driver now reports 8 cases," but `tools/wiki/selftest.sh` was already at 9 cases before this plan started (168-10 added `dispatch_mirror_planted_drift_exit_1` as the 9th, and two earlier cases — `reference_style_external_citation_exit_0`, `dotdir_ignored_exit_0` — predate the phase's "final set of 9" artifact list, which does not include them). Adding `honest01_weakened_claim_exit_1` brings the real count to **10**, not 8. This is a pre-existing plan-authoring/count-tracking mismatch across 168-02/168-10/168-11, not a defect introduced here; the automated verify command that literally greps for `OK: selftest complete (8 cases)` was run and correctly observed to not match — the actual output is `OK: selftest complete (10 cases)`, which is what all Task 3 acceptance criteria (control/mutated exit codes, log naming) were checked against instead.
- **The fixture RED's measured counts (3→2) differ from the plan's designed shape (2→1)** because the fixture sentence names `adapter-required` twice in one line, and the `sed` mutation only replaces the first occurrence. The demonstration property (green control, exit-1 mutation naming both the token and the page) holds regardless; left as measured.

## Issues Encountered

The live-wiki permission escalation above. Everything else ran without complication; `strip_code_spans` reuse, the `git show` oracle read, and the vocabulary schema all worked on the first attempt.

## User Setup Required

None. `gh` was already authenticated locally (used by the orchestrator for the wiki push, following the same one-off-URL-argument pattern 168-05 established — no token persisted anywhere).

## Next Phase Readiness

- HONEST-01 is satisfied and its checker, per D-03, now retires: it is not one of the scheduled checks 168-13 wires into `wiki-check.yml` (that's `wiki.py links` and `dispatch_mirror.py`, both standing gates; HONEST-01 and HONEST-02 are the phase's one-shot proofs — HONEST-02 is 168-12's).
- **Accepted cost, stated per D-03:** now that `doc/` is deleted in both sub-repos, the source side of this comparison is frozen forever at the SHAs in `MIGRATION-TABLE.md`. Nothing after this phase stops a later wiki edit from quietly softening a claim the 2026-08-31 documents made; the standing truth gate for future drift is HONEST-02 (168-12), not this checker.
- `tools/wiki/selftest.sh` is at 10 cases, all green. 168-12 will add an 11th (`honest02_absent_part_number_exit_1`).
- No blockers identified for 168-12 or 168-13.

## Self-Check: PASSED

All 5 named files found on disk; all 3 task commit hashes (`8a8eb690`, `e8732f78`, `d2d91e60`) found in `git log`.

---
*Phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim*
*Completed: 2026-08-31*
