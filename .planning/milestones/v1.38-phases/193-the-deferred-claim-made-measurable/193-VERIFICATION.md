---
phase: 193-the-deferred-claim-made-measurable
verified: 2026-09-14T11:53:12Z
status: passed
score: 4/4 must-haves verified
covered_files:
  - ".planning/REQUIREMENTS.md"
  - ".planning/notes/gitmodules-archaeology-trap.md"
  - ".planning/phases/193-the-deferred-claim-made-measurable/193-01-PLAN.md"
  - ".planning/phases/193-the-deferred-claim-made-measurable/193-01-SUMMARY.md"
  - ".planning/phases/193-the-deferred-claim-made-measurable/193-02-PLAN.md"
  - ".planning/phases/193-the-deferred-claim-made-measurable/193-02-SUMMARY.md"
  - ".planning/phases/193-the-deferred-claim-made-measurable/193-03-PLAN.md"
  - ".planning/phases/193-the-deferred-claim-made-measurable/193-03-SUMMARY.md"
  - ".planning/phases/193-the-deferred-claim-made-measurable/193-04-PLAN.md"
  - ".planning/phases/193-the-deferred-claim-made-measurable/193-04-SUMMARY.md"
  - ".planning/phases/193-the-deferred-claim-made-measurable/193-05-PLAN.md"
  - ".planning/phases/193-the-deferred-claim-made-measurable/193-05-SUMMARY.md"
  - ".planning/phases/193-the-deferred-claim-made-measurable/193-CONTEXT.md"
  - ".planning/phases/193-the-deferred-claim-made-measurable/193-REVIEW.md"
  - ".planning/phases/193-the-deferred-claim-made-measurable/COVERAGE.md"
  - ".planning/seeds/SEED-claim-firestarter-slug.md"
  - "CLAUDE.md"
  - "tools/adoption/pypi_version_share.sh"
covered_digest: "v1:sha256:a70673eb63fb1cf883fce28cfac473a6a42e08ad92255cfff8af7ec8141e6e99"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 193: The Deferred Claim, Made Measurable — Verification Report

**Phase Goal:** The seed that carries the destructive act has a trigger someone can evaluate. The
two things that make the eventual failure survivable are written down where the person doing it
will meet them.

**Verified:** 2026-09-14T11:53:12Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | An instrument reports per-version download share for `firestarter`. The seed's trigger names a threshold and window rather than "once adoption has moved". | ✓ VERIFIED | `./tools/adoption/pypi_version_share.sh` run live by this verifier. Exit 0. Printed `window: 2026-06-16 .. 2026-09-13`, `fixed_downloads_ge_2_0_9: 17`, `at_risk_downloads_2_0_7: 116`, `fixed_share_pct: 12.8`, `TRIGGER: NOT MET`. This matches D-09's authoring-time baseline exactly. `SEED-claim-firestarter-slug.md`'s `trigger_condition` frontmatter states the same numeric threshold. It names the instrument by path. |
| 2 | The instrument's record states what it cannot see. Installed base is unobservable. Download share is a proxy. The never-upgrade residual is unreachable. | ✓ VERIFIED | Live run printed a `WHAT THIS DOES NOT MEASURE` block. It covers all four required points. Installed base is not observable. Download share is a proxy. A never-reinstalling user generates zero downloads and stays invisible. The pre-2.0.7 tail is "outside the instrument's reach entirely." The phrase `a necessary condition, never a sufficient one` appears verbatim in the printed output. |
| 3 | The no-Releases-on-the-meta-repo rule is recorded with its mechanism, not just its instruction. | ✓ VERIFIED | `CLAUDE.md:79` states the rule ("must never publish a GitHub Release — bare milestone tags only"). It states the mechanism inline: `v1.36` parses as PEP 440 `1.36`. `Version("3.0.0b29") >= Version("1.36")` reads true. `fw` reports firmware current forever. It cites `.planning/notes/999.9-repo-rename-impact-analysis.md` § "Standing rule this must produce" by content, not line number. That section exists at that heading in the cited note. It carries the full `_compare_versions` walkthrough. `CLAUDE.md` does NOT duplicate the walkthrough (D-14 honored). |
| 4 | The `.gitmodules` history trap carries a workaround demonstrated for both an existing clone and a fresh clone at a pre-rename ref. | ✓ VERIFIED | `.planning/notes/gitmodules-archaeology-trap.md` documents both workarounds as ordered procedures. Each cites an executed transcript. `evidence/193-gate-03-fresh-clone.txt` and `evidence/193-gate-03-existing-clone.txt` show real `mktemp -d`-scoped executions. Both ran against the published `v1.35` tag. Before/after observables prove the `.git/config` override survives a checkout. `submodule update` honors that override. A third transcript, `193-gate-03-submodule-sync-hazard.txt`, demonstrates a hazard that would otherwise silently undo either workaround, and fixes it. `CLAUDE.md:14` points at the note from the repository-structure area. |

**Score:** 4/4 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tools/adoption/pypi_version_share.sh` | Runnable, credential-free GATE-01 instrument | ✓ VERIFIED | Executed directly. Exit 0. Contains `sql-clickhouse.clickhouse.com`. Mode 0755. |
| `CLAUDE.md` | GATE-02 rule and mechanism citation. GATE-03 pointer. Fixed `tools/` inventory. | ✓ VERIFIED | Both additions present. The `tools/` line now names `tools/catalog/` and `tools/adoption/`. Without this fix, the line would have been false after this phase's own addition. |
| `.planning/notes/gitmodules-archaeology-trap.md` | Dedicated GATE-03 note with both workarounds and transcripts | ✓ VERIFIED | Present. Cites all three transcripts. Carries a `## Honest limits` section. |
| `.planning/seeds/SEED-claim-firestarter-slug.md` | Rewritten `trigger_condition` with threshold and window | ✓ VERIFIED | Frontmatter parses cleanly via GSD's own `extractFrontmatter` (see Data-Flow Trace). `status: dormant` is intact. |
| `.planning/phases/193-.../evidence/*.txt` (5 files) | Executed transcripts | ✓ VERIFIED | All 5 present and committed. Content matches the disposition claims. |
| `.planning/phases/193-.../COVERAGE.md` | API coverage matrix | ✓ VERIFIED | Present. Documents the ClickHouse integration and the rejected fallbacks (pypistats, GitHub release-asset counts). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `tools/adoption/pypi_version_share.sh` | `pypi.pypi_downloads_per_day_by_version_by_installer_by_type` | `curl -G` with `user=play` query-string param | ✓ WIRED | Confirmed by live execution returning real data |
| `SEED-claim-firestarter-slug.md` | `tools/adoption/pypi_version_share.sh` | seed names the instrument by path | ✓ WIRED | `trigger_condition` and prose both name the script path |
| `CLAUDE.md` | `.planning/notes/999.9-repo-rename-impact-analysis.md` § "Standing rule this must produce" | citation by section heading | ✓ WIRED | Section exists verbatim at that heading |
| `CLAUDE.md` | `.planning/notes/gitmodules-archaeology-trap.md` | citation from repository-structure paragraph | ✓ WIRED | Confirmed present at `CLAUDE.md:14` |
| `.planning/notes/gitmodules-archaeology-trap.md` | `evidence/193-gate-03-*.txt` | banked-evidence citations by filename and reading number | ✓ WIRED | All three transcripts cited and exist |

### Data-Flow Trace — Frontmatter Parse-Safety (the sharpest trap named in this phase)

| Artifact | What Was Tested | Method | Result |
|----------|-------|--------|--------|
| `SEED-claim-firestarter-slug.md` | `trigger_condition:` frontmatter parses under GSD's own parser and `status` reads `dormant` | Ran `extractFrontmatter()` from `/workspaces/.claude/gsd-core/bin/lib/frontmatter.cjs` directly against the file | All four keys (`title`, `trigger_condition`, `planted_date`, `status`) parsed. `status: "dormant"` confirmed. The `>-` YAML folded-scalar form avoids the backtick-leading-scalar trap. |

### Behavioral Verification

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Instrument runs and produces a verdict plus caveat block | `./tools/adoption/pypi_version_share.sh` | Exit 0. Printed the window, three numbers, a threshold line, `TRIGGER: NOT MET`, and the full `WHAT THIS DOES NOT MEASURE` block. | ✓ PASS |
| WR-01 fix (numeric guard on `rows_matched`/`trigger_met`) is present in the committed script | `/usr/bin/grep` for the `case "$rows_matched" in ''|*[!0-9]*)` guard | The guard is present. It sits at the location commit `fd4bec6a` describes. | ✓ PASS |
| Seed frontmatter parses with all 4 keys and `status: dormant` | GSD's own `extractFrontmatter()` | All 4 keys present. `status: dormant`. | ✓ PASS |
| No GSD process commentary (`GATE-0N`, `D-NN`, `Phase 19N`) in reader-facing files | `/usr/bin/grep -iE "GATE-0[123]|D-[0-9]{2}|phase 19[0-9]"` over `CLAUDE.md` and the script | Zero matches in either file. One unrelated `D-06` hit sits inside `CLAUDE.md`'s own generic "no comments" rule text. That text is not phase-193 content. | ✓ PASS |
| No credential material leaked into GATE-03 transcripts | `/usr/bin/grep -iE "ssh|token|BEGIN.*KEY|password"` over all 3 transcripts | Zero matches | ✓ PASS |
| No line-number citations in the two new or edited GATE files | `/usr/bin/grep` for `line [0-9]+` pattern | Zero matches in `gitmodules-archaeology-trap.md` or `CLAUDE.md` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| GATE-01 | 193-01, 193-02 | Adoption instrument and measurable seed trigger | ✓ SATISFIED | Instrument runs live. Seed frontmatter carries D-09's numbers and parses. |
| GATE-02 | 193-05 | No-Releases rule recorded with its mechanism | ✓ SATISFIED | `CLAUDE.md:79`. Mechanism cited by section heading. |
| GATE-03 | 193-03, 193-04, 193-05 | `.gitmodules` trap documented with both workarounds demonstrated | ✓ SATISFIED | Note plus 3 executed transcripts. Pointer in `CLAUDE.md:14`. |

No orphaned requirements. `REQUIREMENTS.md` §GATE lists exactly GATE-01, GATE-02 and GATE-03. All three are claimed across the 5 plans' `requirements:` frontmatter. 193-01 claims GATE-01. 193-02 claims GATE-01. 193-03 claims GATE-03. 193-04 claims GATE-03. 193-05 claims GATE-02 and GATE-03.

### Prohibitions (must_haves.prohibitions, judgment-tier)

The 5 plans declare 19 judgment-tier prohibitions. The categories are transparency, safety, privacy and values. This verifier confirmed each one against the delivered artifacts.

- **193-01 (4 prohibitions):** softening the threshold's meaning. A quiet or flagless verdict-without-caveat path. Rendering an unmeasured state as measured. Implying the pre-2.0.7 tail is reachable. All four were confirmed against the live script output and source. None was violated.
- **193-02 (3 prohibitions):** implying a met trigger authorizes the rename, asserting a readiness leg true on the wrong ref, and softening the accepted residual. The seed's own text satisfies these: "A met trigger is a measurement, not an authorisation. A human decides." Its ref-scoped `origin/main` and `origin/beta` checklist adds the same scoping directly.
- **193-03 (4 prohibitions):** recording a breakage that has not happened, mutating the operator's working clone, presenting dirty state as the trap, and committing credentials. The "Honest limits" section satisfies these. So does the already-known finding that the operator's clone stayed untouched. So does the credential grep above.
- **193-04 (4 prohibitions):** presenting the projection as observed. Presenting an invented workaround as one of the two prescribed workarounds. Omitting the sync-hazard warning. Citing by line number.
  The note's "Honest limits" §(b) labels the post-claim failure a "projection." The one-shot variant is labeled "supplementary," not a replacement. The sync hazard gets its own section. No line-number citations were found.
- **193-05 (4 prohibitions):** restating the walkthrough, citing by line number, leaving a self-falsified sentence standing, and stating the rule without its reason. The walkthrough is cited, not duplicated. No line numbers were found. The `tools/` inventory line was fixed in the same edit that added the citation depending on it. The mechanism is stated inline before the citation.

No prohibition was found violated. Each resolves as a non-authoritative LLM-judge pass. This is flagged here per the judgment-tier soft-gate rule, for human awareness, not as a blocking gap.

### Anti-Patterns Found

None. A scan for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER|not yet implemented|coming soon` covered the four primary phase artifacts. It returned one incidental hit. `gitmodules-archaeology-trap.md` describes git's own "empty placeholder directories" behavior. That is not a stub. It is a factual description of `--no-recurse-submodules`.

### Human Verification Required

None. This verifier confirmed every must-have by direct execution of the instrument. It confirmed the seed frontmatter by direct parsing, through GSD's own library. It confirmed every other claim by direct file or grep inspection against transcripts already produced by real command execution, not narrated.

### Declined Options Not Reintroduced (D-01/D-03 verification)

This verifier confirmed the following are absent from the delivered script. No staleness or freshness gate exists beyond the `rows_matched` shape guard. No second data path exists. BigQuery and `pypi_raw` are recorded as fallbacks in comments only, and neither is ever called. No scheduled run exists. No CI scaffolding exists — `.github/workflows/` does not exist in the meta repo. The `rows_matched`/`trigger_met` numeric-shape guard added by the WR-01 fix is a correctness guard. It refuses a verdict on a bad response. D-01's carve-out explicitly permits this: "a minimal 'did the query return rows at all' guard is ordinary correctness and is permitted."

### Gaps Summary

No gaps found. This verifier independently confirmed all four ROADMAP success criteria against live execution and direct file inspection, not against SUMMARY.md narrative alone. The one code-review Warning (WR-01) was fixed and committed (`fd4bec6a`) prior to this verification. Its fix is present in the current script and works as intended. The one Info finding (IN-01, the unused `ch_today` column) remains open by design. It is not a gap against any must-have.

---

_Verified: 2026-09-14T11:53:12Z_
_Verifier: Claude (gsd-verifier)_
