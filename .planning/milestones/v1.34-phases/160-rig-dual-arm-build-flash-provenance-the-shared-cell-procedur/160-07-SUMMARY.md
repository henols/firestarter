---
phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur
plan: 07
subsystem: bench-evidence
tags: [evidence, jsonl, renderer, gate-suite, determinism, append-only]

requires:
  - phase: 160-01
    provides: "rig-pins.json (avrdude/pio pins, forbidden_flags, arms.*.venv_bin, config_dir, tool_conventions.entry_point_idiom); arms-provenance.json's config_dir_sha"
  - phase: 160-03
    provides: "bench/IMAGE-PLAN.json's 21-position table and artifact_volume_policy this schema's artifact_volume_policy_ref points at"
  - phase: 160-04
    provides: "tools/gate_record.py — reused unmodified; its JSONL header contract (record_keys + outcome_values) is exactly what this plan's _schema must satisfy"
  - phase: 160-05
    provides: "tools/judge_readback.py and tools/judge_wrv.py's verdict-field vocabulary (fw_readback_sha_judged, sha_verdict_judged, verdict_disagreement, etc.) carried into evid_extension_columns"
  - phase: 160-06
    provides: "PROCEDURE.md's P-11 (the evidence-append step this schema serves) and tools/render_steps.py (invoked as a live gate in run_gates.sh)"
provides:
  - "bench/EVIDENCE.jsonl — the canonical, append-only per-position evidence record with its line-1 _schema header pinned: 9 locked_columns (byte-identical to v1.15/v1.18), 30 evid_extension_columns, record_keys, a two-state outcome_domain/outcome_values, position_count_expected=20, the bring-up exclusion, and the close-out counting rule as an equation over rows"
  - "tools/render_evidence.py — renders bench/EVIDENCE.md deterministically from EVIDENCE.jsonl, proves it was not hand-edited via --check (byte-compare + unified diff), and appends new rows atomically with prefix-unchanged enforcement"
  - "bench/EVIDENCE.md — the rendered human-readable view, generated from the header-only JSONL (empty position tables, reconciliation 0 of 20), --check green"
  - "tools/run_gates.sh — discovers and runs every tool's --selftest plus 5 live gates, accumulate-then-report, fails closed on missing/empty discovery, states its own two automation gaps"
affects: ["161", "162", "163", "165", "166"]

tech-stack:
  added: []
  patterns:
    - "A schema header carries BOTH its D-15-pinned field name (outcome_domain) and the exact field name the already-authored gate_record.py reads (outcome_values), both set to the identical two-value list — this is the mechanism that makes 'the schema has exactly one source of truth' actually hold for a tool that is reused, not re-implemented"
    - "render_evidence.py's --append takes an injectable _pre_write_hook (mirrors touch_1200.py's injected clock/sleep and judge_readback.py's pure-function/subprocess-wrapper split) so the append-only prefix-unchanged race can be exercised deterministically in --selftest without a real concurrent process"
    - "run_gates.sh's tool-advertises-a-selftest check greps for the literal argparse-registered '\"--selftest\"' token (double-quoted), not a loose substring -- a docstring merely mentioning the flag in prose must not count as advertising it (caught live during this plan's own red-leg fixture authoring)"

key-files:
  created:
    - .planning/v1.34/bench/EVIDENCE.jsonl
    - .planning/v1.34/bench/EVIDENCE.md
    - .planning/v1.34/tools/render_evidence.py
    - .planning/v1.34/tools/run_gates.sh
  modified: []

key-decisions:
  - "The header carries both 'outcome_domain' (this plan's own pinned D-15/D-18 field name) and 'outcome_values' (the field name tools/gate_record.py's check_outcome() already reads from an EVIDENCE.jsonl header, verified by reading gate_record.py's source rather than assumed) with identical two-value lists. Without outcome_values, gate_record.py --jsonl would flag every future row's outcome field as 'no outcome_values domain to check it against' the moment Phase 161 appends its first row -- a Rule 2 fix (missing critical functionality) applied before any row exists, so the substrate is actually consumable by the tool the plan says to reuse rather than re-implement."
  - "render_evidence.py's tables render ALL 39 record_keys columns (not a curated subset) because the plan pins record_keys as the schema's one source of truth for row shape and gives no narrower column list for the rendered view; with zero rows today this produces a wide-but-empty table, which is the literal 'empty position table' the plan's action text anticipates."
  - "The reconciliation arithmetic is (validated rows) + (skipped-with-reason rows) = accounted, vs position_count_expected -- read directly off the plan's own counting-rule phrase ('positions holding a result, plus positions holding a named reason for absence, equals 20') rather than inventing a different formula; both terms come from the outcome field on non-bring-up rows only."
  - "run_gates.sh reads check_arms.py's --expect-config-sha dynamically from arms-provenance.json's config_dir_sha at run time instead of hardcoding the SHA literal in the script -- consistent with this project's standing 'no SHA is ever hardcoded' convention (stated explicitly in gate_record.py's own docstring)."
  - "The tool-advertises-a-selftest discovery check greps for the double-quoted literal '\"--selftest\"' rather than the bare substring '--selftest'. Found and fixed during this plan's own red-leg authoring: a first fixture tool's docstring literally contained the prose '--selftest' without quotes and was wrongly treated as advertising the mode by a looser grep; tightening to the double-quoted argparse-registration literal (verified present in all 11 real tools, including gen_addr_image.py's non-argparse `if rest[:1] == [\"--selftest\"]:` check) closed the false positive."

requirements-completed: []

coverage:
  - id: D1
    description: "bench/EVIDENCE.jsonl initialized with its pinned _schema header — 9 locked_columns byte-identical to v1.15/v1.18, 30 evid_extension_columns, record_keys, two-state outcome domain (both names), position_count_expected=20, bring-up exclusion, close-out counting rule, anti-fabrication conventions, no timestamp anywhere — Task 1"
    requirement: "RIG-05"
    verification:
      - kind: unit
        ref: "python3 -c \"...\" plan's exact structural check (locked_columns byte-identity vs both prior milestones, record_keys order/no-dupes, outcome_domain len==2, position_count_expected==20, no timestamp regex match, all 30 extension columns present) — rc=0, quoted in this SUMMARY"
        status: pass
      - kind: unit
        ref: "python3 .planning/v1.34/tools/gate_record.py --jsonl .planning/v1.34/bench/EVIDENCE.jsonl — rc=0, 'PASS: gate_record validated ... with 0 violations'"
        status: pass
    human_judgment: false
  - id: D2
    description: "tools/render_evidence.py authored (render/--check/--append/--selftest) and bench/EVIDENCE.md rendered from the header-only JSONL; --check observed green against the real file then observed red against a one-character-edited copy, without touching the committed file — Task 2"
    requirement: "RIG-05"
    verification:
      - kind: unit
        ref: "python3 .planning/v1.34/tools/render_evidence.py --selftest — rc=0, 3 positive + 7 negative legs, all named"
        status: pass
      - kind: other
        ref: "plan's exact bash verify block (render-twice byte-identical via cmp, --check green against the real committed EVIDENCE.md, --check red against a hand-edited copy, fail-closed on an empty --jsonl) — rc=0, quoted in this SUMMARY"
        status: pass
      - kind: other
        ref: "markdown property check (no timestamp regex match, 'never hand-edited' present, '20' present in the reconciliation) — rc=0"
        status: pass
    human_judgment: false
  - id: D3
    description: "tools/run_gates.sh authored — discovers and runs every tool's --selftest (11/11), runs 5 live gates, accumulate-then-report, --quick skips only the arms/images gates, fails closed on discovery, header names both automation gaps — Task 3"
    requirement: "RIG-05"
    verification:
      - kind: other
        ref: "bash .planning/v1.34/tools/run_gates.sh — rc=0, 11/11 selftests + 5/5 live gates PASS (quoted in this SUMMARY)"
        status: pass
      - kind: other
        ref: "bash .planning/v1.34/tools/run_gates.sh --quick — rc=0, 11/11 selftests + 3/3 quick-mode live gates PASS, states which 2 gates were skipped"
        status: pass
      - kind: other
        ref: "observed red twice against temporary (never-committed) fixtures: a one-file tools dir whose file advertises no --selftest (rc=1, file named); an empty tools dir (rc=2) — both quoted in this SUMMARY"
        status: pass
      - kind: unit
        ref: "plan's exact header/coverage grep block (set -euo pipefail, 'Exit codes', 'cannot be automated', '--quick', selftest-count >= tool-count) — rc=0, all assertions pass"
        status: pass
    human_judgment: false

duration: ~70min
completed: 2026-08-26
status: complete
---

# Phase 160 Plan 07: The Evidence Substrate — Schema, Renderer, and Gate Suite Summary

**Pinned `bench/EVIDENCE.jsonl`'s append-only `_schema` header (9 locked columns byte-identical to v1.15/v1.18, 30 v1.34 extension columns, a two-state outcome domain, the 20-position close-out counting rule), authored `render_evidence.py` to render `bench/EVIDENCE.md` deterministically and prove non-hand-editing via `--check`, and wired the whole host-side gate set into `run_gates.sh` — observed green in full and `--quick`, and observed red on both of its own discovery-failure shapes.**

## Performance

- **Duration:** ~70 min
- **Started:** 2026-08-26T23:10Z (context load)
- **Completed:** 2026-08-26T23:37Z
- **Tasks:** 3/3, all `type="auto"`
- **Files modified:** 4 created, 0 modified

## Accomplishments

- `bench/EVIDENCE.jsonl` holds exactly one line: a `_schema` header whose `locked_columns` (`chip, family, board, shield, blank_state, op, sha256, verdict, anomalies`) is verified byte-identical against both `.planning/v1.15/bench/EVIDENCE.json` and `.planning/v1.18/bench/EVIDENCE.json`, extended by 30 `evid_extension_columns` this milestone's dual-arm judge/provenance pipeline actually produces (`position_id`, `fw_readback_sha_judged`, `sha_verdict_judged`, `verdict_disagreement`, `commands`, `outcome`, etc.). `record_keys` is the fixed concatenation (39 keys, no duplicates). `outcome_domain` (this plan's pinned name) and `outcome_values` (the name `tools/gate_record.py`'s already-authored `check_outcome()` reads) both carry the identical two-value list `["validated", "skipped-with-reason"]`. `position_count_expected` is 20, `bringup_cell_id_prefix` is `"BRINGUP-"`, and `bringup_row_exclusion`/`close01_counting_rule` write the 20-position reconciliation down as an equation over rows rather than leaving it to a human count. `not_measured_convention` and `negative_control_convention` carry the anti-fabrication rules into the record itself. No timestamp appears anywhere in the file (regex-verified).
- `tools/render_evidence.py` (stdlib-only, `sys.exit(main())`) renders `bench/EVIDENCE.md` deterministically from the JSONL: rows sorted by `position_id`, no timestamp/hostname, LF endings, one JSON-encoded cell format. `--check` re-renders in memory and byte-compares against the committed target — the leg with no Python analog in this tree (`tools/catalog/codegen.py --check` validates its own source; it doesn't diff a render against a separately committed file) — printing a unified diff and exiting non-zero on divergence. `--append` validates a new row against the schema's `record_keys` (rejects a missing declared key, an extra undeclared key, an out-of-domain `outcome`, or a duplicate `position_id`), re-reads the file immediately before writing to assert the existing prefix is byte-unchanged, and writes atomically via temp-file-plus-`os.replace` — never a plain `open(..., "a")`.
- `bench/EVIDENCE.md` was rendered from the header-only `EVIDENCE.jsonl`: an empty "Positions" table, an empty "Bring-up rows" table (both correctly wide — 39 columns — since no narrower column list is pinned), and a "Reconciliation" section reading `0 validated + 0 skipped-with-reason = 0 of 20 positions accounted for (20 not yet recorded).` `--check` against the committed file is green.
- `tools/run_gates.sh` discovers every `*.py` under `tools/` (11 found), asserts each advertises a `--selftest` mode by grepping for the literal double-quoted argparse token `"--selftest"` (tightened after catching a false positive against a fixture whose docstring merely *mentioned* the flag in prose), and runs it — 11/11 pass. It then runs 5 live gates: `check_rebuild.py` (committed `images/` self-check against `SHA256SUMS.txt`), `check_arms.py` (both live host arms, `--expect-config-sha` read dynamically from `arms-provenance.json`, never hardcoded), `render_steps.py`'s SC#3 empty-diff check (`--arm control` vs `--arm v133` against the real `PROCEDURE.md`, both render 11 lines, diff empty), `render_evidence.py --check`, and `gate_record.py --jsonl`. All 5 pass. `--quick` skips only `check_rebuild.py` and `check_arms.py` (the two needing images/arms); the other three live gates and all 11 selftests still run. Failure style is accumulate-then-report (stated in the header against `check-migration.sh`'s bail-on-first-assertion precedent). Header names the exit-code table (0/1/2) and the two things this suite cannot automate: the deliberate wrong-arm cross-flash (D-03, plans 08-10) and the fresh-context record reconstruction (RIG-05's actual claim, plan 13).
- Observed red twice against temporary, never-committed fixtures: a one-file tools directory whose file advertises no `--selftest` (`FAIL: no_selftest_tool.py does not advertise a --selftest mode`, exit 1) and an empty tools directory (`FAIL: discovery found zero *.py files ... a suite that finds nothing must fail, not pass`, exit 2). Both fixtures lived under the scratchpad directory and left nothing behind; `git status --short .planning/v1.34/tools/` shows only the intended new file.
- All three tools' `--selftest` modes and the whole `run_gates.sh` suite were re-run after every fix; final state is green in both full and `--quick` mode. Both sub-repos (`firestarter`, `firestarter_app`) confirmed porcelain-clean throughout — this plan touches only meta-repo `.planning/v1.34/` files.

## Task Commits

1. **Task 1: Initialize `bench/EVIDENCE.jsonl` with its pinned `_schema` header** — `97cb817b` (feat)
2. **Task 2: Author `tools/render_evidence.py` and render `bench/EVIDENCE.md`** — `b6b2b0d3` (feat)
3. **Task 3: Author `tools/run_gates.sh`** — `bde61e30` (feat)

**Plan metadata:** committed below (this SUMMARY + STATE.md/ROADMAP.md)

## Files Created/Modified

- `.planning/v1.34/bench/EVIDENCE.jsonl` — canonical append-only per-position evidence record, header-only (Task 1)
- `.planning/v1.34/bench/EVIDENCE.md` — rendered human view, generated by `render_evidence.py`, never hand-edited (Task 2)
- `.planning/v1.34/tools/render_evidence.py` — the JSONL→MD renderer, `--check`, `--append`, `--selftest` (Task 2)
- `.planning/v1.34/tools/run_gates.sh` — the full host-side gate suite, `--quick` (Task 3)

## Decisions Made

See `key-decisions` in the frontmatter for the full list with rationale. Summary:

- The header carries both `outcome_domain` (this plan's pinned name) and `outcome_values` (the name `gate_record.py` actually reads), identical values, so the already-authored gate tool remains genuinely usable against this schema without modification.
- `render_evidence.py`'s tables render all 39 `record_keys` columns, matching the plan's "one source of truth for row shape" framing rather than inventing a narrower display list.
- Reconciliation arithmetic follows the plan's own phrase literally: validated + skipped-with-reason vs. `position_count_expected`.
- `run_gates.sh` reads `check_arms.py`'s expected config-dir SHA dynamically from `arms-provenance.json` at run time, never as a literal in the script, per the project's standing "no SHA is ever hardcoded" convention.
- The self-test-advertisement discovery check greps for the double-quoted argparse literal `"--selftest"`, not the bare substring, after a fixture false-positive during this plan's own authoring caught the looser check.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical functionality] Added `outcome_values` alongside the plan's pinned `outcome_domain`**
- **Found during:** Task 1, before committing — reasoning through the key_link "`_schema.record_keys` → `gate_record.py` reads the required key set from this header ... so the schema has exactly one source of truth" against `gate_record.py`'s actual source (read in full per `<files_to_read>`).
- **Issue:** The plan pins the field name `outcome_domain`, but `tools/gate_record.py`'s `check_outcome()` (already authored, reused unmodified per plan instruction) reads `schema.get("outcome_values")`. Shipping only `outcome_domain` would make `gate_record.py --jsonl` report a violation ("schema has no outcome_values domain to check it against") on the very first row Phase 161 appends — defeating the stated purpose of reusing the tool rather than re-implementing its check.
- **Fix:** Added `outcome_values` to the header with the identical two-value list, plus an `outcome_values_note` explaining the duplication is deliberate (one source of truth expressed under two field names for two different consumers: this plan's pinned naming, and the already-shipped tool's actual read path).
- **Files modified:** `.planning/v1.34/bench/EVIDENCE.jsonl`
- **Verification:** `gate_record.py --jsonl` returns rc=0 with "0 violations" against the header-only file (confirmed both before commit and in the live `run_gates.sh` run).
- **Committed in:** `97cb817b` (Task 1 commit — found and fixed before the first commit)

**2. [Rule 1 - Bug] Tightened `run_gates.sh`'s self-test-advertisement grep from a loose substring to the double-quoted argparse literal**
- **Found during:** Task 3, while authoring the required "observed red" fixture for a tool that advertises no `--selftest` mode.
- **Issue:** My first fixture tool's docstring read `"""A deliberately non-conforming tool fixture: no --selftest mode at all."""` — plain prose mentioning the flag with no surrounding quotes. `run_gates.sh`'s original check (`grep -q -- '--selftest' "$tool"`) matched that prose and wrongly treated the fixture as advertising a self-test mode, running it (the fixture's stub `main()` printed a message and returned 0), which would have silently defeated the whole point of the red-leg test.
- **Fix:** Tightened the grep pattern to the double-quoted literal `'"--selftest"'` — the exact token every real tool's `add_argument("--selftest", ...)` or `if rest[:1] == ["--selftest"]:` check contains (verified present in all 11 real tools via `grep -c -- '"--selftest"' *.py`), which a prose mention without quotes does not match.
- **Files modified:** `.planning/v1.34/tools/run_gates.sh`
- **Verification:** Re-ran the fixed fixture (a docstring using unquoted prose "no self test mode of any kind") — correctly caught, `FAIL: no_selftest_tool.py does not advertise a --selftest mode`, exit 1. Re-ran the full and `--quick` suites against the real tools directory afterward — still 11/11 selftests pass, both exit 0.
- **Committed in:** `bde61e30` (Task 3 commit — found and fixed before the first commit)

---

**Total deviations:** 2 auto-fixed (1 Rule 2 missing-critical-functionality, 1 Rule 1 bug), both found and fixed during authoring, before any task commit. Neither changed scope.
**Impact on plan:** Both fixes were necessary for the deliverables to actually work as the plan describes — the first makes the schema genuinely consumable by the tool the plan says to reuse; the second makes the discovery check's own negative leg trustworthy rather than a false pass.

## Issues Encountered

None beyond the two deviations above, both resolved before their task's commit. No blocking issues, no auth gates (no external service or hardware interaction in this plan — explicitly stated in the plan's own load-bearing traps: "No hardware is attached and this plan must not require any").

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The evidence substrate is pinned. Phases 161-163 append real position rows via `render_evidence.py --append` (or directly, following its documented validation contract); the schema's `record_keys` is the one source of truth for row shape, and `gate_record.py --jsonl` — already reusable against this file's actual field names — is the standing per-wave check.
- `run_gates.sh` is ready to run as the per-wave-merge gate for Phases 161-166, per this plan's own header. Its two named automation gaps (wrong-arm cross-flash; fresh-context reconstruction) are unchanged obligations for plans 08-10 and 13 respectively — a green `run_gates.sh` run proves the substrate, not the phase.
- RIG-05 is deliberately **not** marked complete, per this plan's own "Requirement completion" section: this plan closes the *substrate* half only (a record shape that carries every field a re-run needs, and a whole-file gate that reads its schema from the record itself). RIG-05's actual claim — that a cell can be re-run from the written record alone — is discharged by plan 13's fresh-context reconstruction. `REQUIREMENTS.md` stays unchanged for RIG-05.
- No other requirement's status changed. No blockers.

## Self-Check: PASSED

- `FOUND: .planning/v1.34/bench/EVIDENCE.jsonl`
- `FOUND: .planning/v1.34/bench/EVIDENCE.md`
- `FOUND: .planning/v1.34/tools/render_evidence.py`
- `FOUND: .planning/v1.34/tools/run_gates.sh`
- `FOUND: commit 97cb817b` (Task 1)
- `FOUND: commit b6b2b0d3` (Task 2)
- `FOUND: commit bde61e30` (Task 3)
- `python3 .planning/v1.34/tools/render_evidence.py --selftest` → rc=0 (3 positive + 7 negative legs)
- `python3 .planning/v1.34/tools/gate_record.py --jsonl .planning/v1.34/bench/EVIDENCE.jsonl` → rc=0
- `bash .planning/v1.34/tools/run_gates.sh` → rc=0 (11/11 selftests + 5/5 live gates)
- `bash .planning/v1.34/tools/run_gates.sh --quick` → rc=0 (11/11 selftests + 3/3 live gates)
- `git -C /workspaces/firestarter status --porcelain` → empty
- `git -C /workspaces/firestarter_app status --porcelain` → empty

---
*Phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur*
*Completed: 2026-08-26*
