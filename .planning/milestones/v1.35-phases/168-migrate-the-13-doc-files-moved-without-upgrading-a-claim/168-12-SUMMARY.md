---
phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim
plan: 12
subsystem: testing
tags: [honest02, wiki, standing-gate, stdlib, standalone-checker, claim-allowlist]

requires:
  - phase: 168-03
    provides: "the regenerated firestarter_app/firestarter/data/chip_database.json this checker resolves claims against"
  - phase: 168-05
    provides: "the 11 firestarter-claim-stamp comments and 3 firestarter-claims-begin/end regions this checker reads"
  - phase: 168-11
    provides: "the 0/1/2 checker shape, the control-then-mutate selftest.sh driver (at 10 cases before this plan), and honest01_claims.py as the sibling style to match"

provides:
  - "tools/wiki/honest02_truth.py -- the standing three-leg truth gate: stamp presence, delimited-region claim resolution, stamp freshness. Zero comments, stdlib-only, 0/1/2 exit contract"
  - "tools/wiki/claim-allowlist.json -- 21 reasoned exceptions (15 part tokens, 6 algorithm tokens), each with a mandatory non-empty reason, bounded to what the three delimited regions actually need"
  - "the corrected, measured shape of the resolve leg: a claim signature defined as 'at least one token that resolves against the database', not 'shaped like one' -- shape-only matching false-positives on Home.md's incidental part-number mentions and Beta-Testing-Install.md's board/MCU identifiers (328PB, ATmega328PB, uno328pb)"
  - "tools/wiki/selftest.sh's case_honest02_absent_part_number_exit_1 -- one green control plus three mutations (UNRESOLVED, MISSING STAMP, STALE STAMP), each textually distinct; driver now reports 11 cases"
  - "evidence/honest02-fixture-RED.txt (the observed UNRESOLVED fixture failure) + evidence/honest02-live-run.txt (a clean exit-0 run against a fresh clone of the live wiki, first attempt, no correction needed) + evidence/selftest-9-cases.txt (full run, actual count 11)"
affects: ["168-13 (wires honest02_truth.py into wiki-check.yml as a scheduled standing gate, alongside wiki.py links and dispatch_mirror.py)"]

tech-stack:
  added: []
  patterns:
    - "the resolve leg is scoped to explicitly delimited firestarter-claims-begin/end regions, never free text -- the falsification measured in 168-RESEARCH.md (3% resolve rate on Lockable-PROMs' 209 bold tokens; 11/20 false-positive algorithm coincidences on Shield-Revisions' zero-part-number page) is corrected here exactly as the plan specifies"
    - "a page-navigation exclusion set (Home.md, How-To-Edit-This-Wiki.md, _Sidebar.md, _Footer.md) is applied before any claim-signature evaluation, mirroring wiki.py's own NAV_EXCLUDED_PAGES precedent -- these are wiki-mechanics pages, not chip/protocol reference content, and How-To-Edit-This-Wiki.md says so of itself"
    - "part-number-shaped-token extraction excludes three syntactic shapes that are never part numbers in this corpus -- bare voltage (5V, 12V), bare capacity (512K, 1M), bare pin count (24PIN) -- collapsing what would otherwise be a much larger, noisier allowlist down to 21 entries that map onto real naming conventions (minipro IC2_ALG_* constant fragments, elided vendor-family shorthand, pin/bus descriptors, self-documented phantom/out-of-scope protocol IDs)"
    - "three outcome vocabularies (MISSING STAMP / UNRESOLVED / STALE STAMP) plus one named non-failure (UNCHECKED (stamp only)) so a database disagreement, a navigation-shaped problem and 'nobody has re-verified since the database changed' never arrive as one indistinguishable red"

key-files:
  created:
    - tools/wiki/honest02_truth.py
    - tools/wiki/claim-allowlist.json
    - .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/honest02-fixture-RED.txt
    - .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/honest02-live-run.txt
    - .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/selftest-9-cases.txt
  modified:
    - tools/wiki/selftest.sh

key-decisions:
  - "The claim signature (leg 1's gate for 'does this page need a stamp at all') is defined as resolution against the database, not mere alphanumeric shape. Measured directly against the live corpus: a shape-only signature ('contains any token with a letter and a digit') incorrectly flags Home.md (its 'AT28C04/AT28C16' cross-reference prose both resolve as real part numbers even though Home.md makes no claim about either chip) and Beta-Testing-Install.md (328PB/ATmega328PB/uno328pb are board/MCU identifiers, not EPROM part numbers, and none resolves). Requiring resolution, plus excluding the four navigation/mechanics pages by name, produces exactly the measured target: 11 of 12 content pages match the signature (Beta-Testing-Install correctly excluded), and all 11 already carry a stamp."
  - "Inline code spans (single backticks) are NOT stripped before token extraction, only triple-backtick fenced blocks are -- the corpus writes almost every hex/part-number claim as inline code (`0x07`, `AT28C04`), and honest01_claims.py's strip_code_spans (which strips both) is the wrong tool reused for the wrong purpose here. Verified directly: stripping inline code drops Community-Validation.md's and Package-Details.md's only resolving tokens, which would have wrongly excused them from the stamp requirement they already (correctly) satisfy."
  - "Part-number-token extraction excludes three syntactic shapes -- bare voltage (\\d+(\\.\\d+)?V), bare capacity (\\d+[KM]), bare pin count (\\d+PIN) -- because without the exclusion the three delimited regions report a wall of non-resolving noise (12V, 512K, 24PIN, ...) that has nothing to do with a part number being wrong. This is a refinement of what counts as 'part-number-shaped', not a loosening of the resolve check: every token that survives extraction still must resolve or be allowlisted with a stated reason."
  - "The allowlist's 21 entries fall into four measured, named categories rather than being an unexplained token dump: fragments of minipro's IC2_ALG_* constant-naming axis (9 entries -- a namespace structurally disjoint from the chip database's part_number field), elided vendor-family shorthand naming a family rather than one catalogued part (4 entries, same convention protection_readability.py:20-28 documents), pin/bus descriptors that were never part numbers (2 entries), and protocol IDs the claims regions' own tables already self-document as phantom or out-of-scope (6 entries) -- none of these are unverified assumptions; each reason cites the region's own text."
  - "The live run against a fresh clone (master aa4a5c7) came back clean on the first attempt -- exit 0, 11 matched/0 missing, 3 regions/60 claims/8 unchecked, 0 stale -- so no correction was needed before the phase closes, unlike 168-11's first live run which found a real dropped claim."

requirements-completed: [HONEST-02]

coverage:
  - id: D1
    description: "tools/wiki/honest02_truth.py exists as a standalone, stdlib-only, zero-comment checker with the 0/1/2 exit contract, implementing all three legs (stamp presence, delimited-region resolution, stamp freshness) with distinct, non-substring outcome vocabularies"
    requirement: "HONEST-02"
    verification:
      - kind: automated
        command: "python3 tools/wiki/honest02_truth.py --wiki-dir <fresh clone of firestarter_prom.wiki.git @ aa4a5c7> --db firestarter_app/firestarter/data/chip_database.json --allowlist tools/wiki/claim-allowlist.json"
        result: "LEG 1: 12 pages scanned, 11 matched, 0 missing. LEG 2: 3 regions found, 60 claims checked, 8 pages stamp-only unchecked (each named). LEG 3: 11 stamps checked against db-sha256-16=ccbc8d2c4866a5af, 0 stale. OK: ...; exit 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "A nonexistent database path or allowlist path, an empty wiki directory, and an allowlist entry with an empty reason all exit 2 (not 1), with a message naming the failure"
    requirement: "HONEST-02"
    verification:
      - kind: automated
        command: "python3 tools/wiki/honest02_truth.py --wiki-dir <clone> --db /nonexistent/db.json --allowlist tools/wiki/claim-allowlist.json; ... --wiki-dir <empty dir> ...; python3 -c injecting an empty-reason allowlist entry"
        result: "ERROR: --db not found ...; exit 2 / ERROR: ... contains zero content pages ...; exit 2 / ERROR: allowlist part_tokens entry has an empty token or reason ...; exit 2"
        status: pass
    human_judgment: false
  - id: D3
    description: "Removing a stamp, mutating a resolving claims-region token to one absent from the database, and altering a stamp's recorded hash each produce exit 1 with three textually distinct messages (MISSING STAMP / UNRESOLVED / STALE STAMP), none a substring of another"
    requirement: "HONEST-02"
    verification:
      - kind: automated
        command: "bash tools/wiki/selftest.sh (case_honest02_absent_part_number_exit_1: control + 3 mutations)"
        result: "control exit 0; absent-part mutation exit 1 naming GHOSTPART01 and UNRESOLVED; missing-stamp mutation exit 1 naming Fixture-Chip-Page.md and MISSING STAMP; stale-stamp mutation exit 1 with STALE STAMP and no UNRESOLVED text. All PASS in the evidence table"
        status: pass
    human_judgment: false
  - id: D4
    description: "The check has been demonstrated failing on a fixture (three ways) and has been run once against the real published wiki, with the outcome recorded whatever it was"
    requirement: "HONEST-02"
    verification:
      - kind: automated
        command: "bash tools/wiki/selftest.sh; evidence/honest02-fixture-RED.txt; evidence/honest02-live-run.txt"
        result: "OK: selftest complete (11 cases), exit 0, all PASS. evidence/honest02-fixture-RED.txt records the observed UNRESOLVED exit-1 output verbatim. evidence/honest02-live-run.txt records a clean exit-0 run against wiki master aa4a5c7 and the real chip_database.json, first attempt, no correction needed"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-08-31
status: complete
---

# Phase 168 Plan 12: HONEST-02 Truth Checker Summary

**Built the standing three-leg wiki truth gate (`tools/wiki/honest02_truth.py`) and its 21-entry reasoned allowlist, correcting the plan's own falsified resolve-leg design by scoping it to three explicitly delimited claim regions instead of scraping free text — and, unlike the sibling HONEST-01 checker's first live run, this one came back clean against the real wiki on the first attempt.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-08-31T11:40:00Z (approx.)
- **Tasks:** 3 completed, all `type="auto"`

## Accomplishments

- Wrote `tools/wiki/honest02_truth.py`: loads the chip database once into two resolution sets (uppercased part numbers, comma-split; distinct `programming.algorithm` integers), loads the reasoned allowlist, then runs three legs with distinct outcome vocabularies:
  - **Leg 1 (stamp present):** a page "matches the claim signature" if at least one token *resolves* against the database (not merely looks like a part number or hex byte) — measured necessary because a shape-only signature false-positives on Home.md's incidental "AT28C04/AT28C16" cross-reference prose (both resolve, neither is a claim) and on Beta-Testing-Install.md's board/MCU identifiers (328PB, ATmega328PB, uno328pb — none resolves). Four navigation/mechanics pages (`Home.md`, `How-To-Edit-This-Wiki.md`, `_Sidebar.md`, `_Footer.md`) are excluded before signature evaluation, mirroring `wiki.py`'s own `NAV_EXCLUDED_PAGES` precedent. Result against the live corpus: 12 pages scanned, 11 matched, 0 missing stamp.
  - **Leg 2 (delimited claims resolve):** extracts part-number- and hex-shaped tokens **only** from inside `firestarter-claims-begin/end` regions, resolves each against the database or the allowlist, and reports a stamped-but-regionless page as `UNCHECKED (stamp only)` on its own named line — never folded into a pass. Result: 3 regions found (Programming-Protocols §0, AT28C04-Adapter, Protocol-ID), 60 claims checked, 8 pages named as stamp-only unchecked (Community-Validation, Infoic-Field-Dictionary, Lockable-PROMs, Package-Details, Pinout-Safety-Review, Protocol-Flags, SRAM-and-NVRAM-Behavior, Shield-Revisions).
  - **Leg 3 (stamp freshness):** compares each stamp's recorded truncated-sha256 to the database's current hash, reporting a mismatch as `STALE STAMP` — a distinct outcome from `UNRESOLVED`, textually and semantically. Result: 11 stamps checked against `db-sha256-16=ccbc8d2c4866a5af` (confirmed still current — 168-03's regenerated database and 168-05's freshly-computed stamp still agree), 0 stale.
  - Zero `#` comments in the file body (only the shebang), matching `honest01_claims.py`'s convention; the rationale lives in the module docstring, which also states the algorithm-13-promoted-row trap and explains why it does not apply to anything this checker computes.
- Wrote `tools/wiki/claim-allowlist.json`: 21 entries (15 part tokens, 6 algorithm tokens), every one with a mandatory, non-empty, specific reason citing the claims region's own text — 9 are fragments of minipro's `IC2_ALG_*` constant-naming axis (a namespace disjoint from the database's `part_number` field), 4 are elided vendor-family shorthand naming a family rather than one catalogued part (the same convention `protection_readability.py:20-28` documents), 2 are pin/bus descriptors that were never part numbers (`DQ7`, `8051BUS`), and 6 are protocol IDs the regions' own tables already self-document as phantom (`0x35`/`0x39` — "0 DB chips, dispatch-preserved for forward-compat") or infeasible/out-of-scope (`0x11`/`0x2A`/`0x2B`/`0x2C` — "out of scope, §2.2"). Not a bulk import of the ~200 non-resolving tokens measured elsewhere in the corpus; those live outside any region and stay out of scope by construction.
- Added `case_honest02_absent_part_number_exit_1` to `tools/wiki/selftest.sh`: a green control (a minimal 2-row fixture database against which a fixture page's part token and algorithm hex token both resolve) followed by three separate mutations from the same base — a region token renamed to one absent from the fixture database (`UNRESOLVED`), the page's stamp deleted (`MISSING STAMP`), and the stamp's recorded hash altered (`STALE STAMP`, asserted to *not* also trigger `UNRESOLVED`). All four sub-cases PASS. `bash tools/wiki/selftest.sh` now reports **11** cases (168-11 had already put the real count at 10 before this plan started; the plan's own projected "9" inherited the same stale-count pattern 168-11's summary already flagged for 168-02/168-10/168-11).
- Ran `honest02_truth.py` once against a **fresh** clone of the live wiki (`master` `aa4a5c7`) and the real `chip_database.json`: **exit 0 on the first attempt**, no correction needed — unlike 168-11's HONEST-01 first live run, which found and required fixing a real dropped claim.

## Task Commits

1. **Task 1: Write the three-leg truth checker with distinct outcomes per leg** — `9c98b5b8` (feat)
2. **Task 2: Commit the reasoned allowlist** — `7412a840` (feat)
3. **Task 3: Demonstrate the failure twice — on a fixture and against the real wiki** — `b9ef816d` (test)

## Files Created/Modified

- `tools/wiki/honest02_truth.py` — new, the checker (zero comments, stdlib-only)
- `tools/wiki/claim-allowlist.json` — new, 21 reasoned entries
- `tools/wiki/selftest.sh` — added `HONEST02_PY`/`CLAIM_ALLOWLIST` constants, `case_honest02_absent_part_number_exit_1`, and the `CASES` array entry
- `.planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/honest02-fixture-RED.txt` — new
- `.planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/honest02-live-run.txt` — new
- `.planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/selftest-9-cases.txt` — new (filename kept per plan's `files_modified`; content states the real count is 11)
- `.planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/honest01-weakened-claim-RED.txt` — regenerated as a side effect of re-running the full `selftest.sh` (only the fixture's dynamically-generated git SHA changed; same content otherwise)

## Decisions Made

See `key-decisions` in frontmatter. Summarized: the plan's own falsified free-text resolve leg is corrected exactly as instructed (scoped to the three delimited regions, `Shield-Revisions.md` given no region), and the additional design gap the plan left open — precisely how to define "matches the claim signature" for leg 1 without also flagging navigation pages and non-claim identifiers — is resolved by requiring database *resolution* (not shape) plus an explicit navigation-page exclusion, both measured against the real corpus before being locked in.

## Deviations from Plan

### Auto-fixed Issues

None in the Rule 1/2/3 sense — this plan built new files from scratch rather than modifying existing broken code. The design corrections below are documented as decisions (the plan explicitly asked for a corrected leg-2 design and left leg-1's precise signature and the extraction regex's precision to be determined from measurement) rather than as bug fixes to prior work.

### Logged discrepancies, not fixed (informational)

- **`selftest.sh`'s case count is 11, not the "9" the plan's action text and acceptance criteria state.** 168-11's own summary already documented that the plan-authored pattern-map projection undercounted (it said 8, the real count was 10 even before 168-11's own case was added). This plan's action text repeats the same stale arithmetic ("the driver now reports 9 cases"). The verify command's literal `grep -q 'OK: selftest complete (9 cases)'` does not match; `bash tools/wiki/selftest.sh`'s actual, correctly-observed output is `OK: selftest complete (11 cases)`, which is what every other acceptance criterion (control/mutation exit codes, message content, evidence files) was checked against instead — consistent with how 168-11 handled the identical situation one plan earlier.
- **`evidence/selftest-9-cases.txt` is named for a count of 9 but documents 11.** The plan's `files_modified` list fixes this exact filename; renaming it was out of scope for this plan (168-13 or a later cleanup pass owns any rename sweep). The file's own captured content states the correct count on its last line.

## Issues Encountered

None. The database hash, allowlist design and checker logic were all validated against the real live wiki clone and the real chip database before being locked in, and every acceptance-criterion command in the plan was run and matched on the first implementation.

## User Setup Required

None.

## Next Phase Readiness

- HONEST-02's checker, allowlist and demonstrated failures are all done. `REQUIREMENTS.md`'s HONEST-02 row is deliberately left `Pending`, not flipped to `Complete`, by this plan: ROADMAP criterion 5 requires the check to "run on a schedule or dispatch," and per D-07/D-10 HONEST-02 is a **standing** gate (unlike HONEST-01's one-shot proof) that is not yet wired into any CI workflow — that wiring is explicitly 168-13's task ("Rewrite `wiki-check.yml` as a scheduled clone-driven job"). Marking the requirement complete here, before the schedule exists, would repeat the premature-multi-plan-completion mistake this project's own history has already been burned by. 168-13 should flip it once the schedule lands.
- `tools/wiki/selftest.sh` is at 11 cases, all green.
- The live-wiki state HONEST-02 asserts as of this plan: `master` `aa4a5c7`, database hash `ccbc8d2c4866a5af`, 11/11 stamped, 3/3 regions clean, 0/0 stale. Nothing on the live wiki needs correction before 168-13 runs.
- No blockers identified for 168-13.

## Self-Check: PASSED

All 5 named created files found on disk; all 3 task commit hashes (`9c98b5b8`, `7412a840`, `b9ef816d`) found in `git log`.

---
*Phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim*
*Completed: 2026-08-31*
