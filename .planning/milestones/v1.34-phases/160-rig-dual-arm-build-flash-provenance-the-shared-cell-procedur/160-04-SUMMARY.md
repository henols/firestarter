---
phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur
plan: 04
subsystem: bench-tooling
tags: [bench, provenance, avrdude, signature, gate, argparse]

requires:
  - phase: 160-01
    provides: "rig-pins.json (avrdude binary/conf/forbidden_binaries, per-target mcu/programmer/baud, arm venv_bin/venv_python/worktree/app_sha, chips, forbidden_flags, pio_binary/pio_project_dir, config_dir, uv_cache_dir)"
  - phase: 160-03
    provides: "tools/check_arms.py (the standing D-06/D-07/D-08 host-arm verifier this plan reuses) and tools/gen_addr_image.py (the sys.exit(main(sys.argv)) entry-point precedent this plan's other two tools deliberately did NOT follow)"
provides:
  - "tools/probe_board.py — board identity by avrdude signature (D-14), two bench-verified parse routes, the uno328pb urclock bootloader interrogation"
  - "tools/capture_provenance.py — required-argument-or-refuse per-cell provenance collector (D-13)"
  - "tools/gate_record.py — record completeness / command-line re-parse / two-state outcome domain gate (D-17 script half, D-18)"
affects: ["160-05", "160-09", "160-11", "160-12", "160-13"]

tech-stack:
  added: []
  patterns:
    - "Pure parse/decide functions kept separate from subprocess-invoking wrappers in all three tools (decide_identity, _interpret_file_probe, _interpret_hw_probe, check_required_fields/check_commands/check_outcome) — --selftest exercises the pure functions directly, with fabricated stderr/JSON fixtures, no device and no subprocess involved"
    - "A probe never returns ok=True with a null value; every failure path is a hard non-zero exit (probe_board.py, capture_provenance.py) — the analog's None-on-failure return was rejected per RESEARCH's explicit warning"
    - "gate_record.py reads its required-key list and outcome domain from a _schema block embedded in the record under examination (single-object --cell mode carries its own _schema; --jsonl mode's line 1 is that same header), never from a module constant"
    - "The anti-fabrication 'not measured — <reason>' convention is a first-class accepted value in gate_record.py's field-presence check, not merely tolerated prose"

key-files:
  created:
    - .planning/v1.34/tools/probe_board.py
    - .planning/v1.34/tools/capture_provenance.py
    - .planning/v1.34/tools/gate_record.py
  modified: []

key-decisions:
  - "probe_board.py's Route 1 deliberately-wrong -p is a fixed constant (m2560/ATmega2560) rather than the todo's example value (m328p) — m2560 is guaranteed to differ from all three bench targets (atmega328p/atmega328pb/atmega32u4), so the mismatch message fires no matter which board is actually attached, where m328p would fail to fire on the uno target itself"
  - "capture_provenance.py's __file__ probe is a local, literal copy of check_arms.py's check_file_probe (not a delegated call) so this tool's own source carries the load-bearing -P flag textually, per this plan's acceptance criteria; the other four host-arm probes (git HEAD, porcelain, config-dir SHA, interpreter, dependency-freeze) ARE delegated to check_arms.py, so a divergence between the two tools' results on those axes is a finding, per this phase's key_links"
  - "capture_provenance.py's real (non-selftest) invocation path is unrunnable in this session by design — it requires a live board (board signature, controller: string) and a readback_verdict.json artifact judge_readback.py (a later plan) has not been written yet. This plan's job, per its own 'Requirement completion' note, is the tooling only; the live per-cell capture is plan 11's. --selftest exercises every testable code path without a device."
  - "capture_provenance.py's eeprom_calibration field only captures the coarse hw_revision bucket (via the same `hw` command used for controller_string) — raw R16/R14R15 ohm values have no read-back CLI path in this app version (firestarter config is write-only). Recorded as 'not measured — <reason>' per this project's anti-fabrication convention rather than fabricated or omitted; gate_record.py's field-presence check explicitly recognizes this shape as valid, not blank."
  - "capture_provenance.py derives the read-back verdict artifact's path by convention (<milestone>/bench/cells/<cell_slug>/readback_verdict.json) rather than via a new CLI flag, because the plan's frozen flag list (--cell-id/--position-id/--arm/--target/--port/--chip/--shield-rev/--pins/--out/--selftest) has no slot for one; this matches the D-16 bench/cells/<cell-id>/ layout already fixed by 160-01/03's decisions and should be honored by judge_readback.py (plan 05) when it lands"
  - "gate_record.py's --cell mode validates a record that itself carries a top-level _schema key (the same shape as an EVIDENCE.jsonl header, merged into one object) rather than a bare capture_provenance.py-style record with no schema at all — this lets both modes share every check function unchanged, and is consistent with the plan's own conflation of --cell and --jsonl validation rules under one prose description"
  - "Forbidden-flag detection in gate_record.py's check_commands intersects the recorded argv (as a set of strings) against rig-pins.json's forbidden_flags, so it catches an exact-token match (e.g. '--force') regardless of its position in the argv list, rather than requiring a fixed argument position"

requirements-completed: []

coverage:
  - id: D1
    description: "probe_board.py authored — board identity by avrdude signature via two bench-verified parse routes, uno328pb urclock bootloader interrogation, and the forbidden-binary refusal — Task 1"
    requirement: "RIG-02"
    verification:
      - kind: unit
        ref: "python3 .planning/v1.34/tools/probe_board.py --selftest (rc=0, 3 positive + 3 negative legs PASS)"
        status: pass
      - kind: other
        ref: "live invocation against a fake-avrdude fixture: unparseable-stderr leg and mcu-mismatch leg both observed red (rc=1, FAIL: ... quoted in this SUMMARY)"
        status: pass
    human_judgment: false
  - id: D2
    description: "capture_provenance.py authored — gathers every machine-readable per-cell field itself and refuses to run without the operator-declared --shield-rev (required=True, no default, closed choices) — Task 2"
    requirement: "RIG-02"
    verification:
      - kind: unit
        ref: "python3 .planning/v1.34/tools/capture_provenance.py --selftest (rc=0, all documented positive + negative legs PASS)"
        status: pass
      - kind: other
        ref: "live invocation: missing --shield-rev and out-of-set --shield-rev both observed red (rc=2, argparse error text quoted in this SUMMARY)"
        status: pass
    human_judgment: false
  - id: D3
    description: "gate_record.py authored — validates a single cell record or a whole EVIDENCE.jsonl against a schema read from the record itself: field presence/placeholder, command-line re-parse (absolute-arm-path, forbidden-flag, pio-cwd), two-state outcome domain, cross-oracle consistency, config-dir integrity — Task 3"
    requirement: "RIG-05"
    verification:
      - kind: unit
        ref: "python3 .planning/v1.34/tools/gate_record.py --selftest (rc=0, 2 positive + 12 negative legs PASS)"
        status: pass
      - kind: other
        ref: "live invocation against hand-written fixtures outside --selftest: out-of-domain outcome, bare-argv0, and forbidden-flag legs all observed red (rc=1, FAIL: ... quoted in this SUMMARY)"
        status: pass
      - kind: unit
        ref: "python3 -c AST scan across all three tools: no subprocess call passes shell=True, no 64-hex-char SHA literal outside a docstring"
        status: pass
    human_judgment: false

duration: ~55min
completed: 2026-08-26
status: complete
---

# Phase 160 Plan 04: The Signature Probe, the Provenance Collector, and the Record Gate Summary

**Authored the three tools that turn RIG-02 and RIG-05 from discipline into mechanism: `probe_board.py` identifies a board by avrdude signature alone (never a handshake), `capture_provenance.py` refuses to run without the operator-declared shield revision and fails hard rather than nulling any other field, and `gate_record.py` judges a cell record's completeness, its command lines, and its two-state outcome domain against a schema it reads from the record itself.**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-08-26T21:38Z (context load)
- **Completed:** 2026-08-26T22:05Z
- **Tasks:** 3/3, all `type="auto"`
- **Files modified:** 3 created, 0 modified

## Accomplishments

- `tools/probe_board.py` implements both bench-verified avrdude signature parse routes (Route 1: deliberately-wrong `-p`, parses avrdude's "connected part ... differs in signature" message; Route 2: verbose correct `-p`, parses the hex device signature and the parenthesised "probably" part guess), tries Route 1 first and falls back to Route 2, and exits non-zero with the captured stderr quoted when neither route parses — never the null identity the closest analog (the pending todo's sketch) would return. Resolves the avrdude binary/conf from `rig-pins.json` only (never PATH) and refuses a binary listed in `forbidden_binaries`. Carries the `--show-urclock` mode (valid only for `--target uno328pb`) running all four urclock bootloader-interrogation probes (`-xshowall`/`-xshowvector`/`-xshowbootsize`/`-xshowversion`), recording each probe's raw output even on error — Pitfall 3's resolution mechanism, ready before any read-back comparator is armed.
- `tools/capture_provenance.py` gathers every machine-readable per-cell field itself: board signature (invokes `probe_board.py`), the port's `controller:` string plus the hw-revision bucket (invokes the arm binary's own local `hw` command, never a network-resolving command), the read-back verdict artifact's judged and whole-flash SHAs, the host arm's SHA/porcelain/`__file__` triple (reusing `check_arms.py`'s probe functions for three of the four legs, with a local literal copy of the `-P` `__file__` probe so the flag is textually present in this tool's own source), the shared config-dir SHA, the interpreter version, and the dependency-freeze SHA. Refuses to run without `--shield-rev` (`required=True`, no default, closed to exactly `Rev 2.0` / `Rev 2.2` / `Modified Rev 0`). `--cell-id` is validated against a `[A-Za-z0-9_-]+(/[A-Za-z0-9_-]+)*` character-class regex — rejecting `..`, absolute paths, and any other character — before `cell_slug` replaces `/` with `-`. `--out` is resolved to an absolute path and its parent asserted inside `.planning/v1.34/` before any write. Every probe failure is a hard non-zero exit; the EEPROM-calibration field records `"not measured — <reason>"` for the two ohm values that have no read-back CLI path in this app version, rather than fabricating or silently omitting them. Writes atomically via a temp file plus `os.replace`.
- `tools/gate_record.py` validates a single cell record (`--cell`) or a whole `EVIDENCE.jsonl` (`--jsonl`), reading the required-field list and the permitted outcome domain from a `_schema` block on the record/header under examination rather than from a constant in the tool. Checks accumulate across a run rather than stopping at the first failure: field presence/non-nullity (treating "missing" and "still a placeholder" as the same failure, with the project's `"not measured — <reason>"` convention explicitly recognized as valid), command-line re-parse (first token must be an absolute path equal to one of the two pinned arm binaries or a pinned rig-owned executable — the pinned avrdude, the pinned PlatformIO binary, or the system interpreter invoking a script under `.planning/v1.34/tools/`; any forbidden flag from `rig-pins.json` is rejected by name; a `pio` command recorded with the wrong working directory is rejected), the two-state outcome domain (D-18 — any third state is rejected, naming that the three-state axis belongs only to Phase 165's triage classification), a cross-oracle consistency check (a validated outcome whose written/read SHAs disagree, or a judged-SHA-verdict/app-verdict disagreement, is reported as a finding rather than resolved), and config-dir integrity (recomputes the shared config dir's SHA via `check_arms.py`'s canonical `compute_config_dir_sha()` and compares against any recorded value). Fails closed on a missing or empty input file. No SHA is ever hardcoded in the tool.
- All three tools' `--selftest` modes pass (0/0/0 exit codes) with every documented positive and negative leg named individually.
- The plan's required "observed red, not merely authored" legs were all exercised live outside `--selftest` and are quoted below: `probe_board.py`'s unparseable-stderr and mcu-mismatch legs (against a fabricated fake-avrdude fixture, since no board is attached this session); `capture_provenance.py`'s missing-`--shield-rev` and out-of-set-`--shield-rev` refusals; `gate_record.py`'s out-of-domain-outcome, bare-argv0, and forbidden-flag legs (against hand-written fixture JSON files, using the real `rig-pins.json`).
- An AST scan across all three files (the plan's own verify block) confirms zero `subprocess` calls with `shell=True` and zero hardcoded 64-hex-character SHA literals outside a docstring.
- Both sub-repos (`firestarter`, `firestarter_app`) and the meta repo (aside from this plan's own three new files, `STATE.md`/`ROADMAP.md`/this SUMMARY) confirmed porcelain-clean throughout.

## Task Commits

1. **Task 1: Author `tools/probe_board.py`** — `3465177b` (feat)
2. **Task 2: Author `tools/capture_provenance.py`** — `88e5a31a` (feat)
3. **Task 3: Author `tools/gate_record.py`** — `c0b8f57b` (feat)

**Plan metadata:** committed below (this SUMMARY + STATE.md/ROADMAP.md)

## Files Created/Modified

- `.planning/v1.34/tools/probe_board.py` — board identity by avrdude signature (Task 1)
- `.planning/v1.34/tools/capture_provenance.py` — required-argument-or-refuse provenance collector (Task 2)
- `.planning/v1.34/tools/gate_record.py` — record completeness / command-line / outcome-domain gate (Task 3)

## Decisions Made

See `key-decisions` in the frontmatter above for the full list with rationale. Summary:

- Route 1's deliberately-wrong `-p` is the fixed constant `m2560`, chosen to differ from all three bench targets so the mismatch fires regardless of which board is attached — the todo's own worked example (`m328p`) would fail to fire when the target itself is a plain Uno.
- `capture_provenance.py`'s `__file__` probe is a local literal copy of `check_arms.py`'s logic (not delegated) purely so the `-P` flag is textually present in this tool's own source per the plan's acceptance criteria; the other four host-arm probes ARE delegated, by design, per this phase's key_links ("a divergence between the two tools' results is itself a finding").
- `capture_provenance.py`'s real invocation path cannot be exercised live this session (no board attached, and `judge_readback.py` — the tool that would write the read-back verdict artifact this tool consumes by convention — is a later plan). This is expected: this plan's own "Requirement completion" section states the live per-cell capture lands in plan 11. `--selftest` exercises every code path that does not require a device.
- `eeprom_calibration`'s R16/R14R15 ohm values are recorded as `"not measured — <reason>"`, never fabricated: `firestarter config` is write-only in this app version and no CLI subcommand reads calibration back.
- The read-back verdict artifact's path is a filesystem convention (`bench/cells/<cell_slug>/readback_verdict.json`) rather than a new CLI flag, because the plan's flag list is frozen and has no slot for one. Plan 05's `judge_readback.py` should write to this exact path.
- `gate_record.py`'s `--cell` mode expects a record that itself embeds a `_schema` block (matching an `EVIDENCE.jsonl` header's shape), not a bare `capture_provenance.py`-style record — this lets one set of check functions serve both `--cell` and `--jsonl` modes unchanged, consistent with the plan's own prose describing identical checks for "both modes."

## Deviations from Plan

None — plan executed as written. The items above are documented design decisions within genuinely open implementation choices (the plan describes behavior and constraints, not exact algorithms for the wrong-`-p` constant, the schema-embedding shape, or the verdict-artifact path), not deviations from anything the plan specified.

## Issues Encountered

**Observed-red evidence, per the plan's acceptance criteria.**

`probe_board.py` — unparseable-stderr leg, live against a fake-avrdude fixture (no board attached this session):
```
$ python3 .planning/v1.34/tools/probe_board.py --target uno --port /dev/null --pins <fixture-pins-pointing-at-a-fake-avrdude-that-emits-garbage-stderr>
FAIL: neither parse route matched avrdude stderr: 'avrdude: some unrelated diagnostic text with no signature information\n\navrdude: some unrelated diagnostic text with no signature information'
(exit 1)
```

`probe_board.py` — mcu-mismatch leg, live against a fake-avrdude fixture that always reports a 328PB signature while `--target uno` expects `atmega328p`:
```
$ python3 .planning/v1.34/tools/probe_board.py --target uno --port /dev/null --pins <fixture-pins-pointing-at-a-fake-avrdude-that-always-reports-328PB>
FAIL: connected part 'atmega328pb' does not match expected mcu 'atmega328p' for target 'uno'
(exit 1)
```

`capture_provenance.py` — missing `--shield-rev`:
```
$ python3 .planning/v1.34/tools/capture_provenance.py --cell-id BRINGUP-wrv --position-id x --arm v133 --target uno --port /dev/null --chip w27c512 --out /tmp/p.json
usage: capture_provenance.py [-h] --cell-id CELL_ID --position-id POSITION_ID --arm {control,v133} --target {uno,uno328pb,leonardo} --port PORT --chip {w27c512,w29c020} --shield-rev {Rev 2.0,Rev 2.2,Modified Rev 0} [--pins PINS] [--out OUT] [--selftest]
capture_provenance.py: error: the following arguments are required: --shield-rev
(exit 2)
```

`capture_provenance.py` — out-of-set `--shield-rev`:
```
$ python3 .planning/v1.34/tools/capture_provenance.py ... --shield-rev "Rev 1.0" --out /tmp/p.json
capture_provenance.py: error: argument --shield-rev: invalid choice: 'Rev 1.0' (choose from Rev 2.0, Rev 2.2, Modified Rev 0)
(exit 2)
```

`gate_record.py` — out-of-domain outcome, bare-argv0, and forbidden-flag legs, live against hand-written fixture JSON files (using the real `rig-pins.json`, not a `--selftest` fixture):
```
$ python3 .planning/v1.34/tools/gate_record.py --cell outcome_domain.json --pins .planning/v1.34/rig-pins.json
FAIL: outcome 'inconclusive' is outside the two-state domain ['skipped-with-reason', 'validated'] -- a third state belongs only to Phase 165's triage classification of a failure after the fact, never to a cell result
(exit 1)

$ python3 .planning/v1.34/tools/gate_record.py --cell bare_argv0.json --pins .planning/v1.34/rig-pins.json
FAIL: commands[0]: first token 'firestarter' is not an absolute path -- a bare invocation would resolve to the un-named user-site editable install
(exit 1)

$ python3 .planning/v1.34/tools/gate_record.py --cell forbidden_flag.json --pins .planning/v1.34/rig-pins.json
FAIL: commands[0]: forbidden flag(s) ['--force'] present -- Phase 145 D-17's withdrawn permission is enforced mechanically here
(exit 1)
```

No blocking issues.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `tools/probe_board.py` is ready for plan 09's `judged_span_policy` work: its `--show-urclock` mode records the raw urclock probe output plan 09 needs before replacing the `uno328pb` `PENDING-xshowvector` placeholder.
- `tools/capture_provenance.py` is ready for plan 11's live per-cell capture, with one dependency plan 05 must satisfy first: `judge_readback.py` must write `<milestone>/bench/cells/<cell_slug>/readback_verdict.json` with `judged_sha256`/`whole_flash_sha256` keys, at the exact path this tool reads by convention.
- `tools/gate_record.py` is ready for plan 13's per-cell gating and Phase 166's `EVIDENCE.jsonl` close-time validation; both consumers should embed a `_schema` block (`record_keys` + `outcome_values`) in whatever record/header shape they produce, since this gate deliberately never falls back to an internal constant.
- RIG-02 and RIG-05 are intentionally **not** marked complete, per this plan's own "Requirement completion" section: RIG-02's live per-cell capture lands in plan 11, and RIG-05's fresh-context reconstruction half lands in plan 13. `REQUIREMENTS.md` stays `Pending` for both.
- No blockers.

## Self-Check: PASSED

- `FOUND: .planning/v1.34/tools/probe_board.py`
- `FOUND: .planning/v1.34/tools/capture_provenance.py`
- `FOUND: .planning/v1.34/tools/gate_record.py`
- `FOUND: commit 3465177b` (Task 1)
- `FOUND: commit 88e5a31a` (Task 2)
- `FOUND: commit c0b8f57b` (Task 3)
- `python3 .planning/v1.34/tools/probe_board.py --selftest` → rc=0
- `python3 .planning/v1.34/tools/capture_provenance.py --selftest` → rc=0
- `python3 .planning/v1.34/tools/gate_record.py --selftest` → rc=0
- `git -C /workspaces/firestarter status --porcelain` → empty
- `git -C /workspaces/firestarter_app status --porcelain` → empty

---
*Phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur*
*Completed: 2026-08-26*
