---
phase: 147-report-provenance-every-dev-test-report-names-its-firmware
plan: "06"
subsystem: testing
tags: [devtest-triage, skill, firmware-identity, provenance, checkpoint]

requires:
  - phase: 147-01
    provides: ".gitignore un-ignore for .claude/skills/ and the tracked skill baseline"
  - phase: 147-03
    provides: "NOT_REPORTED literal + schema_version 1.4 in firestarter.diagnostic_report"
  - phase: 147-05
    provides: "NOT_REPORTED / _NOT_ATTRIBUTABLE literals in tools/parse_devtest_issue.py"
provides:
  - "Firmware-identity line in the devtest-triage skill's show render, with an explicit not-attributable clause when absent"
  - "Fixed bare-null hardware-revision rendering in the same render"
  - "Two frozen, committed issue-body fixtures (null-identity, populated-identity) for offline/hermetic render verification"
  - "Regenerated SKILL.md #2 transcript matching real script output"
  - "Third-of-three NOT_REPORTED marker literal, proven equal to the other two by an executed check"
  - "Human-confirmed attribution judgement closing ROADMAP criterion #5 for the skill surface"
affects: [devtest-triage, devtest-rootcause, PROV-05, PROV-06]

tech-stack:
  added: []
  patterns:
    - "Skills own their scripts: the third marker literal is a local module constant, not an import from firestarter_app, so the skill keeps working if the app repo moves"
    - "is-None-or-empty-string substitution idiom for rendering absent/blank fields, replacing bare f-string interpolation"

key-files:
  created:
    - .claude/skills/devtest-triage/fixtures/dev-test-at28c256-null-identity.md
    - .claude/skills/devtest-triage/fixtures/dev-test-at28c256-populated-identity.md
  modified:
    - .claude/skills/devtest-triage/scripts/devtest_issues.py
    - .claude/skills/devtest-triage/SKILL.md

key-decisions:
  - "Manual-only checkpoint (W-4, ROADMAP criterion #5) was answered by a genuine human verdict, not auto-approved — auto-mode was confirmed inactive for this run"
  - "137-character firmware line wrap was surfaced explicitly to the human as a Part A judgement item and accepted, rather than silently absorbed"
  - "Marker parity and the attribution judgement rest on this checkpoint, not on any automated test — an app-repo test subprocess-invoking /workspaces/.claude/ would fail OPEN in standalone CI"

requirements-completed: [PROV-05, PROV-06]

coverage:
  - id: D1
    description: "devtest-triage skill's show render names the firmware identity and refuses attribution explicitly when absent"
    requirement: "PROV-06"
    verification:
      - kind: manual_procedural
        ref: "checkpoint Task 3, Part A/B — human verdict recorded verbatim below"
        status: pass
    human_judgment: true
    rationale: "ROADMAP criterion #5 is a judgement criterion ('a triager can attribute the report') with no assertion that expresses a human's ability to answer it; an app-repo test reaching into /workspaces/.claude/ fails OPEN in standalone CI (RESEARCH P-6)"
  - id: D2
    description: "Bare-null hardware-revision rendering fixed; third marker literal proven equal across all three modules"
    requirement: "PROV-05"
    verification:
      - kind: unit
        ref: "Task 2 automated verify legs — three-way NOT_REPORTED parity check, is-None-or-empty substitution behavior legs"
        status: pass
    human_judgment: false

duration: 40min
completed: 2026-08-18
status: complete
---

# Phase 147 Plan 06: Skill-render firmware identity + checkpoint evidence Summary

**devtest-triage skill's `show` render now names the firmware identity (or explicitly refuses
attribution), fixes its bare-null hardware-revision rendering, and closes ROADMAP criterion #5 with a
human-confirmed verdict on two frozen fixtures.**

## Status

**All three tasks complete.** Tasks 1 and 2 are committed (`8b18ce74`, `eb5fc638`). Task 3, the blocking
`checkpoint:human-verify`, has received an explicit human verdict approving both Part A and Part B (see
"Task 3 — Human Verdict" below). This plan is done.

## Task 1 — Frozen fixtures + before-image (commit `8b18ce74`)

Created `.claude/skills/devtest-triage/fixtures/dev-test-at28c256-null-identity.md`
(`schema_version` `"1.2"`, `host_version` `"3.0.0b15"`, `fw_board_identity: null`, populated
`hw_revision`, chip `at28c256`, protocol `0x0D`, `dedup_fingerprint` `00e121446ceb` — matching the real
gh#21/#32 shape SKILL.md's own worked example already documents) and
`dev-test-at28c256-populated-identity.md` (same shape, `schema_version` `"1.4"`, `host_version`
`"3.0.0b21"`, `fw_board_identity` `"3.0.0b19:leonardo"`).

**Before-image — unmodified script, null-identity fixture:**

```
#?  at28c256  —  FAIL
  schema      1.2   generated 2026-08-07T12:07:39Z
  host        3.0.0b15   hw Rev 2.0-class, Override HW: Rev 2.3
  protocol    0x0D   chip at28c256
  fingerprint 00e121446ceb

  step         verdict    reason
  id           NA         no chip-id in DB entry
  read         OK         
  blank-check  BAD        
  write        BAD        
  verify       BAD        
  erase        NA         protocol 0x0D (28C family) has no erase operation; each page ...

  voltage     vpp 11800 -> 11800 mV   vpe 13700 -> 13700 mV
  db_diff     status=supported  ladder=community-fail

  ROUTE: FAIL — datasheet cross-check needed. Failing: blank-check, write, verify
  NA means the step does not apply to this family — never report it as a failure.
```

**Before-image — unmodified script, populated-identity fixture:**

```
#?  at28c256  —  FAIL
  schema      1.4   generated 2026-08-18T10:00:00Z
  host        3.0.0b21   hw Rev 2.0-class, Override HW: Rev 2.3
  protocol    0x0D   chip at28c256
  fingerprint 00e121446ceb

  step         verdict    reason
  id           NA         no chip-id in DB entry
  read         OK         
  blank-check  BAD        
  write        BAD        
  verify       BAD        
  erase        NA         protocol 0x0D (28C family) has no erase operation; each page ...

  voltage     vpp 11800 -> 11800 mV   vpe 13700 -> 13700 mV
  db_diff     status=supported  ladder=community-fail

  ROUTE: FAIL — datasheet cross-check needed. Failing: blank-check, write, verify
  NA means the step does not apply to this family — never report it as a failure.
```

Both runs exit 0. Neither shows a firmware line at all — that is the defect this plan's Task 2 fixes.
(Note: the plan's action text describes the defect as "a bare-null hardware-revision rendering and no
firmware line at all"; this fixture's `hw_revision` is intentionally populated per its own acceptance
criteria, so the bare-null-revision half of that sentence does not apply to this particular fixture — the
missing firmware line is the defect actually captured here. `hw_revision`'s own bare-null defect (D-12) is
still fixed in Task 2's code change, just not exercised by this fixture's `auto_capture.hw_revision`
value, which is deliberately populated so the identity marker and the revision marker stay independently
observable.)

## Task 2 — Firmware line, is-None-or-empty substitution, SKILL.md transcript (commit `eb5fc638`)

- Added `NOT_REPORTED = "not reported"` (literal #3 of three) and `NOT_ATTRIBUTABLE` module constants to
  `devtest_issues.py`.
- `cmd_show`'s `host`/`hw` row now uses an explicit `is None or == ""` substitution to `NOT_REPORTED`
  (mirrors the `cid_e is not None` idiom already in the file) instead of a bare f-string interpolation.
- Added a labelled `firmware` row directly after `host … hw …`: the real identity when present, or
  `NOT_REPORTED -- NOT_ATTRIBUTABLE` when absent.
- Regenerated `SKILL.md` §2's transcript from the edited script's real output against the null-identity
  fixture, verified programmatically to be present verbatim in the file (Python `assert ... in content`
  check, not a manual read), and added a short note on the populated-identity fixture's differing
  `firmware` row.
- Three-way marker-literal parity proven by an executed check importing `NOT_REPORTED` from
  `firestarter.diagnostic_report`, `tools.parse_devtest_issue`, and the skill script by file path:
  `all three marker literals equal: 'not reported'`.

**All Task 1/2 `<automated>` verify legs executed and exit 0**, including:
- the three-way marker parity leg,
- both `show --body-file` behavior legs (firmware line present + not-attributable clause; populated case
  carries no not-attributable clause),
- the `_summarize` non-regression check (`git diff` shows no hunk touching `_summarize`),
- the forbidden-claim-vocabulary grep (`0` hits for `verified fixed|confirmed working|now works|now
  proven|dev test proves|silicon`),
- the `firestarter` import / `eval`/`exec`/`shell=True`/`os.system` contract greps (both `0`).

**No app-repo change, no gitlink bump.** `cd /workspaces/firestarter_app && git status --porcelain`
prints exactly the 7 pre-existing untracked-file lines recorded before this plan started (`.planning/
config.json`, `SECURITY.md`, four `datasheets/*.pdf`, `write_test_port.sh`) — unchanged, no new entries,
no tracked-file modifications. Full app suite re-run: `1616 passed, 1 warning in 272.60s` — identical to
the 147-05 baseline, confirming no app↔meta coupling was introduced.

`git log --oneline -3` in the meta repo:
```
eb5fc638 feat(147-06): add firmware identity line to devtest-triage skill render, fix bare-null hw revision
8b18ce74 test(147-06): commit frozen null/populated identity fixtures for devtest-triage skill render
cc8d9642 chore(147-05): bump firestarter_app gitlink; update state/roadmap/requirements
```
Exactly two commits from this plan, no gitlink touched.

## Task 3 — the four render outputs (checkpoint evidence)

**Command 1 — skill `show --body-file`, null-identity fixture:**
```
$ python3 /workspaces/.claude/skills/devtest-triage/scripts/devtest_issues.py show --body-file /workspaces/.claude/skills/devtest-triage/fixtures/dev-test-at28c256-null-identity.md --title '[dev test] at28c256 — FAIL'
#?  at28c256  —  FAIL
  schema      1.2   generated 2026-08-07T12:07:39Z
  host        3.0.0b15   hw Rev 2.0-class, Override HW: Rev 2.3
  firmware    not reported -- NOT attributable to a firmware version -- ask the reporter for a fresh dev test run on a current host build
  protocol    0x0D   chip at28c256
  fingerprint 00e121446ceb

  step         verdict    reason
  id           NA         no chip-id in DB entry
  read         OK         
  blank-check  BAD        
  write        BAD        
  verify       BAD        
  erase        NA         protocol 0x0D (28C family) has no erase operation; each page ...

  voltage     vpp 11800 -> 11800 mV   vpe 13700 -> 13700 mV
  db_diff     status=supported  ladder=community-fail

  ROUTE: FAIL — datasheet cross-check needed. Failing: blank-check, write, verify
  NA means the step does not apply to this family — never report it as a failure.
Exit: 0
```

**Command 2 — skill `show --body-file`, populated-identity fixture:**
```
$ python3 /workspaces/.claude/skills/devtest-triage/scripts/devtest_issues.py show --body-file /workspaces/.claude/skills/devtest-triage/fixtures/dev-test-at28c256-populated-identity.md --title '[dev test] at28c256 — FAIL'
#?  at28c256  —  FAIL
  schema      1.4   generated 2026-08-18T10:00:00Z
  host        3.0.0b21   hw Rev 2.0-class, Override HW: Rev 2.3
  firmware    3.0.0b19:leonardo
  protocol    0x0D   chip at28c256
  fingerprint 00e121446ceb

  step         verdict    reason
  id           NA         no chip-id in DB entry
  read         OK         
  blank-check  BAD        
  write        BAD        
  verify       BAD        
  erase        NA         protocol 0x0D (28C family) has no erase operation; each page ...

  voltage     vpp 11800 -> 11800 mV   vpe 13700 -> 13700 mV
  db_diff     status=supported  ladder=community-fail

  ROUTE: FAIL — datasheet cross-check needed. Failing: blank-check, write, verify
  NA means the step does not apply to this family — never report it as a failure.
Exit: 0
```

**Command 3 — app parser, null-identity fixture:**
```
$ cd /workspaces/firestarter_app && python3 tools/parse_devtest_issue.py --title '[dev test] at28c256 — FAIL' --body-file /workspaces/.claude/skills/devtest-triage/fixtures/dev-test-at28c256-null-identity.md
dev test triage -- at28c256
  schema_version:          1.2
  host_version:            3.0.0b15
  fw_board_identity:       not reported -- NOT attributable to a firmware version -- ask the reporter for a fresh dev test run on a current host build
  dedup_fingerprint:       00e121446ceb
  current_support_status: supported
  proposed_disposition:   suggests: candidate for community-fail (advisory)
  ladder_state:           community-fail
Exit: 0
```

**Command 4 — app parser, populated-identity fixture:**
```
$ cd /workspaces/firestarter_app && python3 tools/parse_devtest_issue.py --title '[dev test] at28c256 — FAIL' --body-file /workspaces/.claude/skills/devtest-triage/fixtures/dev-test-at28c256-populated-identity.md
dev test triage -- at28c256
  schema_version:          1.4
  host_version:            3.0.0b21
  fw_board_identity:       3.0.0b19:leonardo
  dedup_fingerprint:       00e121446ceb
  current_support_status: supported
  proposed_disposition:   suggests: candidate for community-fail (advisory)
  ladder_state:           community-fail
Exit: 0
```

**`SKILL.md` §2's fenced transcript (regenerated in Task 2, to compare against Command 1's output):**
```
#?  at28c256  —  FAIL
  schema      1.2   generated 2026-08-07T12:07:39Z
  host        3.0.0b15   hw Rev 2.0-class, Override HW: Rev 2.3
  firmware    not reported -- NOT attributable to a firmware version -- ask the reporter for a fresh dev test run on a current host build
  protocol    0x0D   chip at28c256
  fingerprint 00e121446ceb

  step         verdict    reason
  id           NA         no chip-id in DB entry
  read         OK         
  blank-check  BAD        
  write        BAD        
  verify       BAD        
  erase        NA         protocol 0x0D (28C family) has no erase operation; each page ...

  voltage     vpp 11800 -> 11800 mV   vpe 13700 -> 13700 mV
  db_diff     status=supported  ladder=community-fail

  ROUTE: FAIL — datasheet cross-check needed. Failing: blank-check, write, verify
  NA means the step does not apply to this family — never report it as a failure.
```
Confirmed programmatically (not by eye) to be byte-identical to Command 1's output as a substring check
during Task 2.

## Task 3 — Human Verdict

A human ran/read the four render outputs above, side by side with Task 1's before-image, and returned
an explicit verdict on both parts. This verdict was **not** auto-approved: auto-mode was confirmed
inactive for this run (`workflow._auto_chain_active: false`, `check auto-mode --pick active` = `false`),
so the checkpoint's own prohibition on `--auto`/`--chain` self-approval did not apply and the verdict
below is a genuine human judgement.

**Part A — APPROVED.** Verdict as given: "Part A approved" — the render is correct and reads as one
coherent block; the 137-character firmware-line wrapping is acceptable.

Supporting detail surfaced to the human before this verdict was given, and accepted by them as part of
it: the null-fixture render's `firmware` line measures **137 characters**, against a next-widest line of
90 characters in the same render. This width was raised explicitly as a Part A step-4 judgement item
(does the render still read as one coherent block on a normal terminal width), and the human's approval
of Part A includes an explicit acceptance of that wrap width — it is not silently absorbed into a
generic "looks fine."

**Part B — APPROVED.** Verdict as given: "Part B approved" — from the populated-fixture render alone,
the firmware version that produced the report is answerable as `3.0.0b19:leonardo` (Command 2 and
Command 4 above); from the null-fixture render, the absent case is an explicit refusal
(`not reported -- NOT attributable to a firmware version -- ask the reporter for a fresh dev test run on
a current host build`) that names the next action rather than showing a blank, a bare null, or silence
(Command 1 and Command 3 above). The human further confirmed the Evidence Ceiling boundary from step 7:
neither render claims the `0x0D` write path works, is fixed, or is proven; neither claims a
support-status change; neither reads as closing gh#21/#32/#11/#12. Both renders make a report
attributable and say so in those terms, nothing more.

**Corroborating evidence, independently re-verified before this gate was presented** (this corroborates
the human verdict above — it does not substitute for it; per this plan's `<output>` contract, the skill
script's marker parity and the criterion-#5 judgement rest on the human checkpoint, not on any automated
test):

- `SKILL.md` §2's fenced transcript is byte-identical to the live null-fixture render output, confirmed
  by a programmatic comparison finding exactly one matching fenced block.
- Neither render contains the substring `None` nor a standalone `null` token.
- The three-way `NOT_REPORTED` marker parity was re-confirmed by direct import:
  `firestarter.diagnostic_report`, `tools/parse_devtest_issue.py`, and
  `.claude/skills/devtest-triage/scripts/devtest_issues.py` all equal `'not reported'`.
- No forbidden-claim vocabulary (`proven`, `is fixed`, `works now`, `silicon`, `support_status changed`,
  `gh#21`, `gh#32`, `gh#11`, `gh#12`) appears in either render.
- `/workspaces/firestarter_app` porcelain output is byte-unchanged from the pre-dispatch baseline (the
  same 7 pre-existing untracked entries, no new entries, no tracked-file modifications).
- Both commits' `--stat` output names exactly the four expected files; no `.claude/channels`, no
  `.claude/settings*`, no submodule gitlink in either.

**Evidence Ceiling held.** Nothing recorded in this SUMMARY says or implies the `0x0D` write path is
proven, graduates `0x0D` out of `UNVERIFIED`, changes any `support_status`, or reads as closing
gh#21/#32/#11/#12. This plan made future `dev test` reports attributable to a firmware version on both
triage surfaces; it proves nothing about the write path itself.

**Outcome:** PROV-05 and PROV-06 are satisfied for the skill surface. ROADMAP criterion #5 is confirmed
by direct human judgement on both the populated and absent cases. All three marker literals
(`firestarter.diagnostic_report`, `tools/parse_devtest_issue.py`,
`.claude/skills/devtest-triage/scripts/devtest_issues.py`) are proven equal. This plan is complete.
