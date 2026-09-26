---
phase: 172-policy-one-tracker-protected-main
plan: 02
subsystem: infra
tags: [github, issue-templates, policy-02, devtest-triage]

requires:
  - phase: 172-policy-one-tracker-protected-main (plan 01)
    provides: the live Contributing wiki page these templates and their evidence trail reference
provides:
  - Four .github/ISSUE_TEMPLATE/ files (bug-report.yml, feature-request.yml, dev-test-report.md, config.yml) on the milestone branch, structurally validated
  - A recorded package-legitimacy decision (declined install, option B) and its accepted weaker guarantee
affects: [172-07 (carries these files to main via PR), 172-08 (proves them live)]

actuals:
  tokens: 9500
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns: [zero-install structural YAML validation fallback for GitHub issue-forms schema compliance]

key-files:
  created:
    - .github/ISSUE_TEMPLATE/bug-report.yml
    - .github/ISSUE_TEMPLATE/feature-request.yml
    - .github/ISSUE_TEMPLATE/dev-test-report.md
    - .github/ISSUE_TEMPLATE/config.yml
    - .planning/phases/172-policy-one-tracker-protected-main/evidence/172-02-package-legitimacy.txt
    - .planning/phases/172-policy-one-tracker-protected-main/evidence/172-02-issue-forms-validation.txt
  modified: []

key-decisions:
  - "Package-legitimacy gate resolved by human as option B: declined the check-jsonschema install (PyPI verdict SUS, too-new/unknown-downloads) despite countervailing metadata (98 releases since 2021, python-jsonschema org maintainer) weighed and still declined."
  - "Shipped validation is a zero-install structural assertion (Python stdlib only): top-level key subset check plus body[].type enum check. This is a strictly weaker guarantee than schema validation (additionalProperties: false) and does not catch a misplaced attribute or illegal nested key. Recorded plainly, not glossed."
  - "dev-test-report.md's hand-fill section uses bold emphasis instead of an H2 markdown heading (deviation from the plan's literal 'under an H2' instruction) because the plan's own verify script greps for any line matching '^ *#' as a comment-ban and a markdown H2 heading trips that same pattern. Bold preserves the visual separation without colliding with the no-comment gate."

requirements-completed: [POLICY-02]

coverage:
  - id: D1
    description: "bug-report.yml and feature-request.yml issue forms exist, are comment-free, use only documented top-level keys and body[].type values, and the bug form's four required fields carry the firmware README's four report-content bullets"
    requirement: "POLICY-02"
    verification:
      - kind: other
        ref: "structural grep/awk checks in 172-02-PLAN.md Task 2 <verify> (both automated legs), run against the committed files"
        status: pass
    human_judgment: true
    rationale: "The plan's success criteria describe these forms as 'schema-valid' (via check-jsonschema/SchemaStore additionalProperties:false validation). The package-legitimacy gate was declined (option B), so what actually shipped is a weaker zero-install structural check, not full schema validation. A human should confirm this reduced guarantee is acceptable before these files reach main via 172-07."
  - id: D2
    description: "dev-test-report.md routes the reader to 'firestarter dev test <chip> --submit', uses the [chip report] title marker (not the [dev test] marker devtest-triage keys on), and config.yml keeps blank_issues_enabled: true with one wiki contact_links entry"
    requirement: "POLICY-02"
    verification:
      - kind: other
        ref: "structural grep/python checks in 172-02-PLAN.md Task 3 <verify> (both automated legs), run against the committed files"
        status: pass
    human_judgment: true
    rationale: "Same structural-vs-schema gap as D1 for config.yml's vendor.github-issue-config validation. Also: the marker-collision avoidance (D-06) is explicitly a judgment-tier check per the plan's own threat model (T-172-07) — no mechanical check reaches the devtest-triage skill itself, which lives outside this repository."
  - id: D3
    description: "Package-legitimacy gate for check-jsonschema resolved: human declined the install (option B), decision and weaker-guarantee statement recorded in evidence/172-02-package-legitimacy.txt"
    requirement: "POLICY-02"
    verification:
      - kind: other
        ref: ".planning/phases/172-policy-one-tracker-protected-main/evidence/172-02-package-legitimacy.txt"
        status: pass
    human_judgment: false

duration: ~15min (this continuation segment; Task 1's checkpoint wait time excluded)
completed: 2026-09-01
status: complete
---

# Phase 172 Plan 02: Issue Templates Summary

**Four `.github/ISSUE_TEMPLATE/` files for `firestarter_prom` (bug report, feature request, chip-validation report, chooser config), validated with a zero-install structural check after the human declined the `check-jsonschema` package-legitimacy gate.**

## Performance

- **Duration:** ~15 min (continuation segment)
- **Completed:** 2026-09-01T18:26:25Z
- **Tasks:** 3 (1 checkpoint resolution + 2 build tasks)
- **Files modified:** 6 created (4 templates, 2 evidence files)

## Accomplishments
- `bug-report.yml`: schema-shaped issue form with required fields for firestarter version, firmware version, board (`uno`/`uno328pb`/`leonardo`/`not sure`), shield revision, and steps to reproduce — the four bullets `firestarter/README.md:73-81` asks a reporter to include, now required rather than merely requested
- `feature-request.yml`: problem/proposal/area issue form, `enhancement` label
- `dev-test-report.md`: routes the reader to `firestarter dev test <chip> --submit`; uses `[chip report] ` as its title prefix, deliberately NOT the `[dev test] ` marker `devtest-triage` and `submit.py`'s `build_title` key on, so a hand-filled report is never mistaken for a machine-generated one (D-06)
- `config.yml`: `blank_issues_enabled: true`, protecting the browser-prefill tier of `firestarter dev test --submit` (`submit.py:283`), plus one `contact_links` entry to the wiki
- Package-legitimacy gate (Task 1) resolved and recorded: human declined the `check-jsonschema` install (option B) despite the countervailing PyPI metadata (98 releases since 2021, maintained by the `python-jsonschema` org) also being weighed

## Task Commits

Each task was committed atomically:

1. **Task 1: Record package-legitimacy gate resolution** - `09449fe6` (docs)
2. **Task 2: Author bug-report and feature-request issue forms** - `7d797ab6` (feat)
3. **Task 3: Author chip-validation template and config.yml** - `1fffc3d5` (feat)

**Plan metadata:** committed separately below.

## Files Created/Modified
- `.github/ISSUE_TEMPLATE/bug-report.yml` - Bug report issue form
- `.github/ISSUE_TEMPLATE/feature-request.yml` - Feature request issue form
- `.github/ISSUE_TEMPLATE/dev-test-report.md` - Chip-validation Markdown template, routes to the CLI
- `.github/ISSUE_TEMPLATE/config.yml` - Issue chooser config, `blank_issues_enabled: true`
- `.planning/phases/172-policy-one-tracker-protected-main/evidence/172-02-package-legitimacy.txt` - Package audit verdict, countervailing metadata, human decision B, weaker-guarantee statement
- `.planning/phases/172-policy-one-tracker-protected-main/evidence/172-02-issue-forms-validation.txt` - Structural validation results for all four files

## Decisions Made
- **Option B (declined install)**, taken by the human at the Task 1 checkpoint on 2026-09-01, after being shown both the SUS verdict and the countervailing metadata (98 releases since 2021, `python-jsonschema` org maintainer). The `too-new` audit signal keys on the latest release date, which fires on any actively maintained package — this was stated to the human but did not override the verdict.
- **Zero-install structural fallback** implemented in Python/bash standard tooling only: top-level key subset check (`name description title labels projects assignees type body`) plus `body[].type` enum check (`checkboxes dropdown input markdown textarea upload`). No `yaml`/PyYAML import was needed since the checks operate on raw grep/awk over the YAML text, not a parsed structure.
- **`[chip report] ` chosen as the hand-fill title marker** (Claude's discretion per plan), distinct from `[dev test] `, reads correctly to a human, and collides with nothing already filed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Markdown H2 heading collided with the plan's own no-comment verify grep**
- **Found during:** Task 3 (authoring `dev-test-report.md`)
- **Issue:** The plan's action text asks for the hand-fill section to sit "under an H2", but the plan's own `<verify>` block runs `! grep -rq '^ *#' .github/ISSUE_TEMPLATE/` as a blanket comment-ban. A Markdown `## Hand-fill (...)` heading starts with `#` and trips that same pattern — the action instruction and the verify gate are in direct conflict.
- **Fix:** Used bold emphasis (`**Hand-fill (if you cannot run the command)**`) instead of an H2 heading. Preserves the visual separation the plan wanted without colliding with the no-comment gate, which exists to forbid actual comments (YAML `#` lines, HTML `<!-- -->`), not Markdown structure.
- **Files modified:** `.github/ISSUE_TEMPLATE/dev-test-report.md`
- **Verification:** Re-ran the full Task 3 `<verify>` block after the fix — both automated legs pass (`LEG1: PASS`, front-matter python check `OK`)
- **Committed in:** `1fffc3d5` (Task 3 commit)

**2. [Package-legitimacy gate resolution — not a code deviation, recorded per resume instructions] Declined `check-jsonschema` install**
- **Found during:** Task 1 (checkpoint, resolved before this continuation began)
- **Issue:** The phase's package-legitimacy audit returned SUS for `check-jsonschema` on PyPI (`too-new`, `unknown-downloads`)
- **Resolution:** Human chose option B — decline the install. No venv was created, no `pip`/`uv pip install` command was run anywhere in this plan.
- **Resulting guarantee, stated plainly:** the shipped validation is a structural assertion only. It catches a mistyped `body[].type` and an unexpected top-level key. It does **not** catch a misplaced attribute or an illegal nested key, which the `vendor.github-issue-forms` / `vendor.github-issue-config` SchemaStore schemas (`additionalProperties: false`) would have caught. A malformed form therefore fails at GitHub render time rather than here. This is a recorded, accepted reduction in guarantee, not a claim of equivalent coverage.
- **Files modified:** `.planning/phases/172-policy-one-tracker-protected-main/evidence/172-02-package-legitimacy.txt`
- **Committed in:** `09449fe6` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking — plan-script H2/comment-grep conflict), plus 1 recorded checkpoint resolution (package-legitimacy decline, not a code deviation)
**Impact on plan:** The H2-to-bold fix is cosmetic and preserves intent. The declined install means POLICY-02's "schema-valid" success-criteria language is not literally true for this plan's output — the actual guarantee is weaker and is recorded in both evidence files and this Summary's `coverage` block (`human_judgment: true` on D1/D2) rather than glossed over.

## Issues Encountered
None beyond the deviations documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All four `.github/ISSUE_TEMPLATE/` files exist on the milestone branch, comment-free, and pass the structural validation this plan's declined install left available.
- The four firmware-README bullets are now required form fields, so plan 172-04 can trim them from `firestarter/README.md` without losing them.
- The host CLI's two submission tiers (`gh issue create` and the browser prefill) are both intact — `submit.py` was not touched and `blank_issues_enabled: true` protects the prefill tier.
- **Carried forward, not resolved here:** these files do nothing until they reach `main` (plan 172-07 carries them via PR; plan 172-08 proves them live). Also carried forward: the weaker-than-schema validation guarantee should be revisited if `check-jsonschema`'s PyPI trust signal changes, or if the operator wants the stronger check run manually at a later date before the 172-07 PR merges.

---
*Phase: 172-policy-one-tracker-protected-main*
*Completed: 2026-09-01*

## Self-Check: PASSED

All 7 created files verified present on disk (`.github/ISSUE_TEMPLATE/*.yml`, `*.md`, both evidence files, this SUMMARY). All 4 task/plan commits (`09449fe6`, `7d797ab6`, `1fffc3d5`, `4ebc5e58`) verified present in `git log`.
