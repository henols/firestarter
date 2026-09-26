---
phase: 171-stray-the-root-level-documentation-files
verified: 2026-09-01T00:00:00Z
status: passed
score: 12/12 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 171: STRAY — The Root-Level Documentation Files Verification Report

**Phase Goal:** Nothing is left sitting at a repository root that a reader could mistake for maintained documentation or for a policy the project does not actually have.
**Verified:** 2026-09-01
**Status:** passed
**Re-verification:** No — initial verification

All commands below were independently re-run against the live codebase (meta repo, `firestarter_app` submodule at `c1416a6`, `firestarter` submodule at `c26562a`, and a **freshly cloned** copy of `firestarter_prom.wiki.git`, not the executor's working clone). Every SUMMARY.md claim checked against the codebase corroborated exactly — no discrepancies found.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria + PLAN must_haves)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1: `things.md` is not left at the repo root under that name (wiki page or deleted) | ✓ VERIFIED | `firestarter_app/things.md` absent from working tree and `HEAD` (re-run: `git cat-file -e HEAD:things.md` fails, rc=128). Deleted (not relocated) per D-05 — its one fact ("avrdude also ships inside the Arduino IDE and PlatformIO") is already on the live wiki `Home.md:16-18`, confirmed by direct grep against the fresh clone. |
| 2 | SC2: `SECURITY.md` is a genuine policy or removed; the Phase 69 audit record no longer occupies the path GitHub surfaces as the security policy | ✓ VERIFIED | Absent from `firestarter_app` working tree and `HEAD`. `origin/main` also confirmed to never have carried it (`git cat-file -e origin/main:SECURITY.md` fails; `gh api .../community/profile -q .files.security_policy` returns null, honestly recorded as a **vacuous** check both before and after — this phase *prevented* a latent misrepresentation, it did not remediate a live one, and every summary states this framing accurately, not as an overclaim). Canonical record confirmed intact at `.planning/milestones/v1.12-phases/69-cli-command-surface-robustness-audit/69-SECURITY.md` (76 lines, present). D-02 must-NOT guard re-run: zero hits for "report a vulnerability" / "security policy" / "responsible disclosure" anywhere in `firestarter_app` outside `.planning/`. |
| 3 | SC3: `autocomplete.md` folded into README or published as wiki page; nothing links to old root path | ✓ VERIFIED | Deleted from `firestarter_app` root (not folded into README — D-03's deliberate choice, and the deletion commit's stat confirms `README.md` untouched). Published as `Shell-Completion` on the **live** wiki: fresh clone shows `Shell-Completion.md` present, `wiki.py links --source-dir <fresh-clone>` → rc=0, `OK: 10 pages, ...`. Nothing links to the old path — sweep re-run finds only the one permitted historical hit (`RED-BASELINE.md:637`) plus the phase's own provenance rows in `MIGRATION-TABLE.md` (a recoverability citation, not a dead link, as documented). |
| 4 | 171-01 D1: `Shell-Completion.md` shape matches the other nine pages | ✓ VERIFIED | Re-run against fresh clone: `sed -n '3,5p' Shell-Completion.md` → `---`, blank line, `# Shell Completion` — exact match to the exemplar shape. |
| 5 | 171-01 D1: all six source sections survive verbatim | ✓ VERIFIED | Re-run: `### Bash`, `### Zsh`, `### Fish`, `### PowerShell`, `### pipx Installations`, `### Migrating from a previous Firestarter` all present in the fresh clone. |
| 6 | 171-01: logo/nav wiring correct | ✓ VERIFIED | Logo `<img src>` on `Shell-Completion.md` is byte-identical to all nine sibling pages (grep across `*.md` yields one unique line) and resolves HTTP 200 (re-checked live). `_Sidebar.md` and `Home.md` both list the page — confirmed by the `wiki.py links` `OK: 10 pages` / `all listed in _Sidebar.md` output. |
| 7 | 171-02: single committed deletion touching exactly three paths | ✓ VERIFIED | `git show c1416a6 --stat` re-run: `SECURITY.md \| 53 --`, `autocomplete.md \| 69 --`, `things.md \| 7 --`, `3 files changed, 129 deletions(-)` — matches SUMMARY exactly. Pre-existing unrelated `tools/build_db.py` modification confirmed still present and unstaged. |
| 8 | 171-02: all three files recoverable at `d56424e1979...` with matching sha256-16 | ✓ VERIFIED | Re-run independently: `things.md`=`637974e9dcab7870`, `SECURITY.md`=`35077cac80e15a8a`, `autocomplete.md`=`6e3a0116f2a3759f` — all three match the recorded fingerprints exactly. |
| 9 | 171-02: sdist manifest unaffected (clean-tree oracle) | ✓ VERIFIED | Evidence file `171-02-sdist-clean-tree-diff.txt` inspected: before=173, after=173, diff rc=0, zero filename matches. Cause of the working-tree false-positive trap correctly avoided (not re-built by the verifier, per the task's explicit instruction not to build the sdist from the working tree). |
| 10 | 171-02: py3.11 suite passes | ✓ VERIFIED (via recorded evidence) | Evidence file `171-02-py311-suite.txt` inspected: `1955 passed, 1 warning in 290.27s`, 32 snapshots passed, 0 failed/error, interpreter confirmed 3.11.16. Not re-run in full (5-minute suite; per verification-discipline guidance to avoid re-running the full suite when recorded evidence is available and consistent with all other independently-verified facts). |
| 11 | 171-03: `MIGRATION-TABLE.md` provenance correct and does not corrupt `parse_migration_table` | ✓ VERIFIED | Re-ran `honest01_claims.parse_migration_table` directly: 8 SHA-bearing rows, `Shell-Completion` present as the eighth with `Moved in: 171`, zero deletion rows leaked through. `git diff` for commit `6e87db0b` confirmed 14 insertions / 0 deletions, append-only. "Removed without ever being published" section confirmed present with both `things.md` and `SECURITY.md` rows, each with a working recovery command. |
| 12 | 171-04: meta gitlinks equal submodule HEADs | ✓ VERIFIED | Re-run: `git ls-tree HEAD firestarter firestarter_app` → `c26562ae...` / `c1416a695...`; `git -C firestarter rev-parse HEAD` / `git -C firestarter_app rev-parse HEAD` match exactly. `git status --short` at meta shows no `M firestarter`/`M firestarter_app` markers — clean. |

**Score:** 12/12 truths verified (0 present-but-behavior-unverified)

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| LEGACY-04 | 171-02, 171-03, 171-04 | `things.md` disposed | ✓ SATISFIED | Deleted, recoverable, provenance-recorded, marked `[x]` in `REQUIREMENTS.md:58` and traceability table `:174` |
| LEGACY-05 | 171-02, 171-03, 171-04 | `SECURITY.md` disposed, no misrepresentation | ✓ SATISFIED | Deleted, no replacement (D-02 guard clean), canonical record intact, marked `[x]` `REQUIREMENTS.md:59`/`:175` |
| LEGACY-07 | 171-01, 171-02, 171-03, 171-04 | `autocomplete.md` disposed | ✓ SATISFIED | Live on wiki as `Shell-Completion` (fresh-clone proof), deleted from root, marked `[x]` `REQUIREMENTS.md:61`/`:176` |

No orphaned requirements — `REQUIREMENTS.md`'s Phase 171 mapping contains exactly these three IDs, all claimed by plan frontmatter, all satisfied.

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| wiki `Home.md` Reference list | wiki `Shell-Completion.md` | markdown link | ✓ WIRED | `wiki.py links` fresh-clone run: `OK: 10 pages, all reachable from Home.md` |
| wiki `_Sidebar.md` | wiki `Shell-Completion.md` | bullet entry | ✓ WIRED | Same run: `all listed in _Sidebar.md` |
| `MIGRATION-TABLE.md` main-table row | live wiki page `Shell-Completion` | Wiki page column | ✓ WIRED | Row present at line 20, matches exemplar shape, cites full SHA |
| deletion rows | frozen pre-deletion blobs | inline-code recovery command | ✓ WIRED | Both commands verified to resolve (`git show d56424e...:things.md` / `:SECURITY.md` both succeed with matching hashes) |
| meta gitlink `firestarter_app` | submodule commit `c1416a6` | `git ls-tree` equality | ✓ WIRED | Confirmed equal |

### Anti-Patterns Found

None. No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers introduced by this phase's changes (`MIGRATION-TABLE.md` diff is pure factual provenance prose; wiki page content is a relocation of existing accurate text with three cosmetic shape corrections, not new authored content — consistent with D-03/D-04's "relocate and correct only" constraint).

### Prohibitions (must_haves.prohibitions)

| Statement | Verification Tier | Status |
|---|---|---|
| No security-reporting statement added anywhere (D-02) — 171-01 & 171-02 | judgment | ✓ RESOLVED — re-run grep, zero hits, confirmed independently |
| No new topic authored (no Installing-avrdude page, no salvaged hackaday.io link, no Breaking-Changes version heading) — 171-01 | judgment | ✓ RESOLVED — confirmed: no `hackaday` hit on `Home.md`, no avrdude-named page exists, no argcomplete/Click mention on `Breaking-Changes.md` |
| `firestarter_app/README.md` not edited — 171-02 | judgment | ✓ RESOLVED — deletion commit stat lists exactly 3 paths, none `README.md` |
| `tools/build_db.py`'s pre-existing modification not swept in — 171-02 | judgment | ✓ RESOLVED — confirmed still `M`, unrelated to any phase-171 commit |
| Gitlink bump does not sweep in `dev-test-sequence-cost-model.md` — 171-04 | judgment | ✓ RESOLVED — confirmed still dirty, last touching commit predates phase 171 |

No test-tier prohibitions declared in this phase's plans; all are judgment-tier and all independently re-verified as held (not merely accepted on SUMMARY's word).

### Manual-Only / Deferred Items (per task's verification_discipline — not gaps)

| Item | Disposition | Verifier's independent check |
|---|---|---|
| Wiki push to `firestarter_prom.wiki.git` | Human-action, approved and performed | Confirmed: fresh clone HEAD is `bf787fb156bb...`, matching the recorded push SHA |
| Rendered-page visual inspection | **Waived by operator** ("approved — skip the look") | Recorded as a waiver per SUMMARY, not counted as a performed check. The mechanical substitutes that did run (title exact, logo HTTP 200 + identical across all pages, both nav entries, six sections, page shape) were independently re-verified above and all hold. |
| GitHub Security-tab observation | Correctly deferred to milestone merge | Confirmed vacuous today: `origin/main` never had `SECURITY.md`; `community/profile` API returns null now, would have returned null regardless of this phase's work |
| `wiki-check.yml` red/green status | Correctly no-action (unregistered workflow, no run exists) | Confirmed: workflow absent from `origin/main`; `gh workflow list --all` scope not re-checked (out of scope for this phase, already documented in the out-of-scope ledger) |

None of these four items are gaps. All are either performed-and-verified (push) or deliberately, correctly resolved as non-actionable given measured facts (waiver / vacuous-today deferral / no-action). No open human-verification item remains for this phase.

### Out-of-Scope Ledger

`.planning/phases/171-stray-the-root-level-documentation-files/evidence/171-03-out-of-scope-ledger.md` exists and names all required items, confirmed by direct read: `Protocol-Flags`/`Protocol-ID` table drift (item 1), the `wiki-check.yml --wiki-dir` defect (item 2), the unregistered `wiki-check.yml` workflow (item 3), plus five more (historical `RED-BASELINE.md` hit, the pre-existing `build_db.py` modification, the gitignored `SOURCES.txt` false-positive cause, the stale `blob/main` copy, and the deferred Security-tab observation). Eight items total, matching the SUMMARY's claim exactly.

### Expected Dirt Confirmed Untouched

- `firestarter_app/tools/build_db.py` — still modified, unrelated content, not part of any phase-171 commit
- `.planning/config.json` — still modified (`_auto_chain_active` diff), last touching commit `d503c747` predates phase 171
- `.planning/notes/dev-test-sequence-cost-model.md` — still modified, last touching commit predates phase 171

### Gaps Summary

None. Every SUMMARY.md claim checked against the codebase corroborated exactly. All 19 V-rows from `171-VALIDATION.md` are accounted for (V-01–V-16, V-19 independently re-run by this verifier with matching results; V-17/V-18 confirmed present and internally consistent in their cited evidence files, not re-run in full per the standard guidance against re-running a multi-minute full suite when the recorded evidence is otherwise fully corroborated). No stub, no orphaned artifact, no broken key link, no smuggled security statement, no authored-not-relocated content, no requirement left unaccounted for.

---

_Verified: 2026-09-01_
_Verifier: Claude (gsd-verifier)_
