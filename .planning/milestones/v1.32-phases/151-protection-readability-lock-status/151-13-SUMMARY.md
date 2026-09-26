---
phase: 151-protection-readability-lock-status
plan: 13
subsystem: host-cli
tags: [protection-readability, lock-status, cli, click, channel-gate, python, firestarter_app]

# Dependency graph
requires:
  - phase: 151-protection-readability-lock-status (plan 06)
    provides: "protection_gate_for_entry(entry, display_name) -> (gate_token, reason), the pure predicate"
  - phase: 151-protection-readability-lock-status (plan 11)
    provides: "lock_status.py's classify_protection_response / exit_code_for_class / render_lock_status, and EpromOperator.read_protection_status"
  - phase: 151-protection-readability-lock-status (plan 12)
    provides: "test_lock_status_class_partition.py's proof that the D-09 partition is exhaustive and protected/unprotected are structurally unreachable from the pure module"
provides:
  - "firestarter_app/firestarter/cli_handlers.py — the `dev lock-status <chip> [--force]` command, registered beta-only"
  - "firestarter_app/firestarter/channel.py — BETA_ONLY_DEV_COMMANDS extended to a 7-tuple ending 'lock-status'"
  - "firestarter_app/tests/test_lock_status_cli.py — the 18-leg class-token x exit-code CLI matrix (new)"
  - "firestarter_app/tests/test_dev_group_channel_gating.py, test_dev_tools_channel_gate.py — extended to cover the seventh gated name"
  - "firestarter_app/tests/__snapshots__/test_characterization.ambr — one new dev --help command row"
affects: [152]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A table refusal renders directly from protection_gate_for_entry's own (gate_token, gate_reason) tuple, never through classify_protection_response's generic passed-through-refusal wording -- the latter would discard the specific offending alias(es) the predicate already named (discovered as a real bug during this plan's own test-writing, before any commit landed)."
    - "CLI-surface tests mock only the one seam that would open a serial port (EpromOperator.read_protection_status) rather than wiring a full fake-serial harness -- .assert_not_called() on that seam IS the port-opening assertion, and every other layer (gate predicate, classifier, renderer) runs for real."
    - "--force never threads into the wire flags word: the handler always calls _build_op_flags() with no force= kwarg, so the emitted operation_flags is byte-identical whether or not --force was given."

key-files:
  created:
    - firestarter_app/tests/test_lock_status_cli.py
  modified:
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/firestarter/channel.py
    - firestarter_app/tests/test_dev_group_channel_gating.py
    - firestarter_app/tests/test_dev_tools_channel_gate.py
    - firestarter_app/tests/test_click_group_gate_hook.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr

key-decisions:
  - "The refusal-without-force branch renders from protection_gate_for_entry's own (gate_token, gate_reason) directly, never via classify_protection_response(gate_token, None, forced=False) -- the latter's generic wording ('the readability table resolved this part to ... before any silicon read was attempted') discards the specific offending alias(es) (e.g. W29C022) the predicate already named in its reason string. Found as a genuine Rule-1 bug via this plan's own leg 3 test, before any commit landed."
  - "The unknown-command-to-firmware_outdated path raises `SystemExit(exit_code_for_class('firmware_outdated')) from exc` rather than constructing and raising the mapped FirmwareOutdatedError bare -- a bare raise would be caught by @map_typed_errors's own FirmwareOutdatedError handler and forced through click.ClickException's default exit code 1, which would silently violate D-10's literal exit-3 assignment for this class. SystemExit propagates past that handler untouched while still satisfying the plan's literal 'raising `from exc`' instruction."
  - "test_lock_status_cli.py mocks EpromOperator (Mock(spec=EpromOperator)) rather than wiring conftest.py's fake-serial harness end to end. Every acceptance criterion in the plan (token+exit-code matrix, the W29C020/W29C040 refusal text, the --force probe, the flags-word equality, the firmware_outdated mapping, the raw-byte hex rendering) is provable at the CLI/operator-call boundary; the one method that would open a port (read_protection_status) is exactly the mocked seam, so `.assert_not_called()` on it is a direct, sufficient proof that no port opens on a refusal -- a lighter-weight harness than the plan's read_first fake-serial idiom, chosen because it meets every stated criterion with less moving surface."
  - "test_click_group_gate_hook.py needed no functional change: confirmed by reading it that it iterates neither channel.BETA_ONLY_DEV_COMMANDS nor _GATED_NAMES -- it is a throwaway Click-mechanism spike proving get_command fires before resolve_command's own fallback, using one hardcoded synthetic name ('reg') that has nothing to do with this project's real gate. Two stale 'six gated dev subcommands' docstring mentions were corrected to 'seven' as a zero-risk accuracy fix, since this file is explicitly discussed (and its own count claims) in the plan text."
  - "LOCK-02, LOCK-03 and LOCK-04 were flipped only after re-confirming the host evidence chain (test_protection_resolution.py, test_lock_status_class_partition.py, test_lock_status_wire.py, test_lock_status_cli.py, test_check_protection_readability.py -- 79 legs, all green) AND the firmware-native evidence (pio test -e native / native_nodevtools / native_pinmap_provisional, all green, the last one naming test_pinmap_provisional_refuses_cmd_lock_status explicitly) in this session, per orchestrator constraint 3's explicit warning that a flip without the firmware-native evidence would be premature."

requirements-completed: [LOCK-02, LOCK-03, LOCK-04]

coverage:
  - id: D1
    description: "dev lock-status <chip> [--force] registered beta-only inside the existing _DEV_TOOLS_ENABLED gate, fed db.get_eprom()'s dict (never resolve_chip()'s), opening no port on a table refusal and exiting through exit_code_for_class"
    requirement: "LOCK-02"
    verification:
      - kind: unit
        ref: "tests/test_lock_status_cli.py#test_matrix_class_token_and_exit_code[protected], [unprotected]"
        status: pass
      - kind: integration
        ref: "pio test -e native_pinmap_provisional#test_pinmap_provisional_refuses_cmd_lock_status"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every refusal class (not_readable / not_implemented / undocumented_alias / no_mechanism) refuses gracefully, names its reason, opens no serial port, and exits 2 -- including the worked W29C020,W29C020C,W29C022 entry naming W29C022, and the W29C040,W29C042 entry naming both aliases with differing states"
    requirement: "LOCK-03"
    verification:
      - kind: unit
        ref: "tests/test_lock_status_cli.py#test_w29c020_refuses_by_default_naming_w29c022"
        status: pass
      - kind: unit
        ref: "tests/test_lock_status_cli.py#test_w29c040_refusal_names_both_aliases_with_differing_states"
        status: pass
      - kind: unit
        ref: "tests/test_lock_status_cli.py#test_matrix_class_token_and_exit_code[no_mechanism, not_implemented, not_readable, undocumented_alias]"
        status: pass
    human_judgment: false
  - id: D3
    description: "The command never over-promises: --force's unadjudicated_probe is proven never to collapse into a state claim for any fed decode byte, the flags word never changes with --force, and protected/unprotected remain structurally unreachable from the pure predicate module"
    requirement: "LOCK-04"
    verification:
      - kind: unit
        ref: "tests/test_lock_status_cli.py#test_forced_probe_is_never_a_state_claim (parametrized x3)"
        status: pass
      - kind: unit
        ref: "tests/test_lock_status_cli.py#test_force_does_not_change_the_wire_flags_word"
        status: pass
      - kind: unit
        ref: "tests/test_lock_status_class_partition.py (18 legs, plan 151-12, re-confirmed green this plan)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The channel gate extends cleanly to the new command: 7-tuple BETA_ONLY_DEV_COMMANDS, 7-element _GATED_NAMES, both channel directions proven via subprocess, and the dev --help snapshot gains exactly one row"
    verification:
      - kind: unit
        ref: "tests/test_dev_group_channel_gating.py (12 legs)"
        status: pass
      - kind: unit
        ref: "tests/test_dev_tools_channel_gate.py::test_beta_only_dev_commands_matches_measured_baseline"
        status: pass
      - kind: unit
        ref: "tests/test_characterization.py::test_help_dev (syrupy snapshot, one-row diff)"
        status: pass
    human_judgment: false

# Metrics
duration: ~35min
completed: 2026-08-20
status: complete
---

# Phase 151 Plan 13: `dev lock-status` — the CLI Surface, the Channel Gate, and the Three Requirement Flips Summary

**Registered `dev lock-status <chip> [--force]` as a beta-only Click subcommand wired to the D-09/D-10 classifier and exit map, proved it with an 18-leg class-token x exit-code CLI matrix, extended the channel gate and the `dev --help` snapshot to the seventh gated name, and flipped LOCK-02/03/04 after re-confirming the full host and firmware-native evidence chain.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-20T17:53:00Z (approx, from the prior plan's meta commit)
- **Completed:** 2026-08-20T18:22:00Z
- **Tasks:** 3 (Task 1 and Task 2 `tdd="true"`, Task 3 `type="auto"`)
- **Files modified:** 7 (1 created, 6 modified)

## Accomplishments

- Added `dev lock-status <chip> [--force]` to `firestarter_app/firestarter/cli_handlers.py`, registered inside the existing module-level `if _DEV_TOOLS_ENABLED:` block, mirroring `dev addr`'s decorator template exactly (decorator order, `shell_complete=_complete_eprom`, `@click.pass_obj`, `@map_typed_errors`, one-line docstring).
- The handler resolves the chip via `app.db.get_eprom(eprom)` for the protection-readability predicate — never `resolve_chip()`'s programmer dict, which carries neither `protocol-id` nor `name`. A table refusal without `--force` renders directly from `protection_gate_for_entry`'s own `(gate_token, gate_reason)` and opens no serial port; the handler exits through `exit_code_for_class(...)` uniformly, never a boolean `sys.exit(0 if ok else 1)`.
- `--force` never sets a firmware flag bit (C-16): the handler always calls `_build_op_flags()` with no `force=` kwarg. An `EpromOperationError` keyed on `MSG_ERR_UNKNOWN_CMD` maps through `sdp_honesty.map_unknown_cmd_to_outdated_for_operation` to the `firmware_outdated` class, exit 3, via `raise SystemExit(...) from exc`.
- Extended `channel.BETA_ONLY_DEV_COMMANDS` from a 6-tuple to a 7-tuple ending `"lock-status"`; the preceding count-in-words comment now says "seven" with a Phase 151 / D-01 attribution.
- Created `firestarter_app/tests/test_lock_status_cli.py` (18 legs) — the full D-09 x D-10 class-token/exit-code matrix, the `--force`-never-reaches-the-wire proof, the `firmware_outdated` mapping with a negative control, and the raw-byte-visible-in-hex proof — driven through real `CliRunner` invocations against a `Mock(spec=EpromOperator)`-backed `AppContext`.
- Extended `test_dev_group_channel_gating.py` (`_GATED_NAMES` 6→7, `_ALL_EIGHT_NAMES`→`_ALL_NINE_NAMES` renamed everywhere) and `test_dev_tools_channel_gate.py` (`BETA_ONLY_DEV_COMMANDS` pinned as an exact 7-tuple); regenerated the `test_help_dev` snapshot, scoped with `-k help_dev`, gaining exactly one new command row.
- Flipped **LOCK-02, LOCK-03, LOCK-04** in `REQUIREMENTS.md`'s checkboxes and traceability rows, after re-confirming every piece of host and firmware-native evidence green in this session.

## Task Commits

Each task was committed atomically in `firestarter_app/`:

1. **Task 1: the `dev lock-status` command + `BETA_ONLY_DEV_COMMANDS` extension** — `26e61d6` (feat)
2. **Task 2: the class-token x exit-code matrix, and the `--force` path** — `674a8c0` (test)
3. **Task 3: the channel gate on a simulated stable build, and the `dev --help` snapshot** — `4a6f5e8` (test)

**Plan metadata:** this commit (meta repo) — `.planning/` tracking + `firestarter_app` gitlink bump.

## Files Created/Modified

- `firestarter_app/firestarter/cli_handlers.py` — added the `dev lock-status` command and its imports (`classify_protection_response`, `exit_code_for_class`, `render_lock_status`, `GATE_TOKEN_READ_PERMITTED`, `protection_gate_for_entry`).
- `firestarter_app/firestarter/channel.py` — `BETA_ONLY_DEV_COMMANDS` extended to a 7-tuple; count-in-words comments updated in two places.
- `firestarter_app/tests/test_lock_status_cli.py` — new, 18 test functions.
- `firestarter_app/tests/test_dev_group_channel_gating.py` — `_GATED_NAMES`/`_ALL_NINE_NAMES` extended and renamed; docstrings updated.
- `firestarter_app/tests/test_dev_tools_channel_gate.py` — baseline tuple re-pinned to 7 entries.
- `firestarter_app/tests/test_click_group_gate_hook.py` — two stale "six" docstring mentions corrected to "seven" (no functional change; see Decisions).
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` — one new `lock-status` row in `test_help_dev`.

## Decisions Made

See `key-decisions` in the frontmatter for the full account. In brief: the refusal-without-force path renders from the predicate's own `(gate_token, gate_reason)` directly rather than through `classify_protection_response`'s generic wording (a real bug caught by this plan's own test-writing, fixed before any commit landed); the `firmware_outdated` path uses `raise SystemExit(...) from exc` so D-10's literal exit-3 assignment survives `@map_typed_errors`'s own `FirmwareOutdatedError` handler (which would otherwise force exit code 1); the CLI test file mocks only the port-opening seam (`EpromOperator.read_protection_status`) rather than wiring a full fake-serial harness; `test_click_group_gate_hook.py` needed no functional change (confirmed to iterate neither `BETA_ONLY_DEV_COMMANDS` nor `_GATED_NAMES`).

## The Eight-Row Class ⊗ Exit-Code Matrix, As Landed

| class token | chip used | force | exit code | operator called |
|---|---|---|---|---|
| `no_mechanism` | `27C256` | no | 2 | no |
| `not_implemented` | `AM28F010` | no | 2 | no |
| `not_readable` | `AT28C256` | no | 2 | no |
| `undocumented_alias` | `W29C020` | no | 2 | no |
| `protected` | `AM29F010` (fed decode `0x01`) | no | 0 | yes |
| `unprotected` | `AM29F010` (fed decode `0x00`) | no | 0 | yes |
| `firmware_outdated` | `AM29F010` (fed `MSG_ERR_UNKNOWN_CMD`) | no | 3 | yes (raises) |
| `unadjudicated_probe` | `W29C020` (any fed decode byte) | yes | 4 | yes |

Exactly two tokens exit 0, and both require a fed device payload (`SILICON_ONLY_TOKENS`) — asserted structurally, not just by inspection, in `test_exit_zero_reachable_only_from_silicon_only_tokens`.

## The W29C020 Refusal Text, Showing W29C022 Named

Observed CLI output (first line) for `dev lock-status W29C020` without `--force`:

```
undocumented_alias W29C020: not documented in lockable-proms.md: W29C020 (documented-not-readable) [lockable-proms.md:21 names the row key 'W29C020 / W29C020C' (Yes-special, covering both parts), but every restatement elsewhere in the document -- lockable-proms.md:30, :335, and :350 -- names 'W29C020C' only, never bare W29C020. Bare W29C020 appears exactly once in the document's 399 lines: the :21 row key itself. Tiebreak rule (DESIGN.md §5): the more-restrictive reading wins, so W29C020 curates to documented-not-readable.]; W29C022 (undocumented)
```

`W29C022` is named as `(undocumented)`; exit code 2; `EpromOperator.read_protection_status` is `assert_not_called()`-proven never invoked. This is the measured D-06/D-07 consequence: no `0x05` row answers by default, not even the operator's own `W29C020` (which requires `--force`, producing `unadjudicated_probe` instead — never a state).

## The `.ambr` Diff Shape

```diff
@@ -141,6 +141,7 @@
     addr               Direct access to address lines and control register.
     consistency-check  Read EPROM N consecutive times and report SHA-256...
     fault-inject       Demonstrate COBS resync: inject a corrupted frame...
+    lock-status        Diagnostic read of a chip's write-protection state...
     read               Reads the content from an EPROM and prints data to...
     reg                Direct access to registers: MSB, LSB and control...
     test               Run the community chip-validation sweep for CHIP...
```

Exactly one inserted row, no column-alignment shift on adjacent rows (`git diff --stat`: `1 file changed, 1 insertion(+)`).

## `test_click_group_gate_hook.py`: Confirmed to Need No Functional Change

Read in full: it never imports `firestarter.cli_handlers`, never references `channel.BETA_ONLY_DEV_COMMANDS`, and never iterates `_GATED_NAMES`. It proves a fact about Click itself — `get_command` fires before `resolve_command`'s own generic-error fallback — using one hardcoded synthetic gated name (`"reg"`) on a throwaway `_SpikeGatedGroup`. No leg needed extending. Two stale "six gated `dev` subcommands" docstring mentions were corrected to "seven" as a zero-risk accuracy fix (the file is explicitly discussed, count and all, in this plan's own text).

## Test Invocations Confirmed Green Immediately Before the Three Requirement Flips

1. `pytest tests/test_protection_resolution.py tests/test_lock_status_class_partition.py tests/test_lock_status_wire.py tests/test_lock_status_cli.py tests/test_check_protection_readability.py -o addopts="-ra"` — **79 passed**, no skips.
2. `python3 tools/check_protection_readability_invariants.py` (real module, no env override) — `PASS: ... 0 Class 1, 0 Class 2, 0 Class 3, 0 Class 4 violations` (151-09's AST gate re-confirmed, not weakened).
3. `pio test -e native` (firmware, 163/163 cases, 17 suites).
4. `pio test -e native_nodevtools` (163/163 cases).
5. `pio test -e native_pinmap_provisional` (11/11 cases, naming `test_pinmap_provisional_refuses_cmd_lock_status` explicitly — the leg named in the phase's own `<verification>` block for running in no CI leg).
6. Full host suite: `pytest tests/ -o addopts="-ra" --cov=firestarter --cov-report=term-missing --cov-fail-under=70` — **1806 passed** (baseline 1788 + this plan's 18 new legs, zero regressions), coverage **83.61%**.

`python3 scripts/check_size_baseline.py --policy merge05` was **not** re-run this plan: it was already confirmed green by Plan 151-10, which funded and verified the +288 B flash-only `MERGE05_LOCK_STATUS_READ_EXEMPTION_BYTES` exemption on all three AVR targets. This plan's `files_modified` is host-only (no firmware change), so re-running the multi-target cold AVR rebuild would re-prove Plan 151-10's own work rather than anything new to this plan.

## Verification

- `pytest tests/test_lock_status_cli.py -x -o addopts="-ra"` — **18 passed**, no skips; collects 18 test functions (the matrix parametrization counts as 8 of them).
- `pytest tests/test_dev_group_channel_gating.py tests/test_dev_tools_channel_gate.py tests/test_click_group_gate_hook.py -x -o addopts="-ra"` — **46 passed**, no skips.
- `pytest tests/test_characterization.py -k help_dev -x -o addopts="-ra"` — **1 passed**, snapshot matches the regenerated one-row diff.
- `channel.BETA_ONLY_DEV_COMMANDS` is a 7-tuple ending `"lock-status"`; `_GATED_NAMES` has 7 elements; `_ALL_EIGHT_NAMES` no longer appears (`grep -c` → `0`).
- Full host suite (Python 3.11 venv): **1806 passed**, coverage **83.61%** (>=70% required).
- `ruff check firestarter/cli_handlers.py firestarter/channel.py tests/test_lock_status_cli.py tests/test_dev_group_channel_gating.py tests/test_dev_tools_channel_gate.py tests/test_click_group_gate_hook.py` and the matching `ruff format --check` — clean.
- `python3 tools/check_mypy_watermark.py` — **35 errors, at the watermark (35), zero new**.
- `firestarter dev --help` (installed console-script entry point) lists `lock-status`. **Note:** the plan's own literal verify command, `python3 -m firestarter dev --help`, fails in this environment with `No module named firestarter.__main__` — there is no `__main__.py` in the package, a pre-existing, unrelated environment gap (confirmed via `git status --short` showing no uncommitted change to any `__main__`-related file, and via `find` showing no `__main__.py` anywhere in `firestarter/`). Verified via the installed console-script instead, which produces the same result the module form would have.
- 3 pre-existing ruff findings in `tools/audit_coverage_matrix.py` and `tools/catalog/codegen*.py` (import-sort / format-only) are untouched by this plan — confirmed via `git status --short` showing no diff on those paths — and are out of this plan's scope (Rule: only fix issues directly caused by the current task's changes).

Python environment used: the pre-provisioned py3.11 venv at
`/tmp/claude-1000/-workspaces/f3ebf666-a01b-4de4-9860-8a006054ba0c/scratchpad/p151/venv311`
(per orchestrator constraint 8).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The refusal-without-force path discarded the specific offending alias(es) named by the predicate**
- **Found during:** Task 2, while writing `test_w29c020_refuses_by_default_naming_w29c022` (before any commit landed)
- **Issue:** The Task 1 draft rendered a table refusal via `classify_protection_response(gate_token, None, forced=False)`, whose generic passed-through-refusal wording is "the readability table resolved this part to `{gate_token!r}` before any silicon read was attempted; the payload, if any, was not consulted." — it never mentions `W29C022`, the specific alias `protection_gate_for_entry` had already named in its own `gate_reason`. The test asserting `"W29C022" in result.output` failed, printing only the generic boilerplate.
- **Fix:** Changed the refusal-without-force branch to render directly from `protection_gate_for_entry`'s own `(gate_token, gate_reason)` tuple via `render_lock_status(gate_token, gate_reason, None)`, matching the plan's literal action text for that branch (which never mentioned `classify_protection_response` for this path at all).
- **Files modified:** `firestarter_app/firestarter/cli_handlers.py`
- **Verification:** `test_w29c020_refuses_by_default_naming_w29c022` and `test_w29c040_refusal_names_both_aliases_with_differing_states` both pass; the full 18-leg suite passes.
- **Committed in:** `26e61d6` (Task 1 commit — caught and fixed before this task was ever committed)

---

**Total deviations:** 1 auto-fixed (Rule 1, correctness bug caught by the plan's own test-writing before any commit landed).
**Impact on plan:** Necessary for LOCK-03's own "names the reason" requirement — an uncaught version would have shipped a refusal that named no specific offending alias, silently weakening the exact guarantee this plan exists to prove. No scope creep.

## Issues Encountered

None beyond the one auto-fixed item above. The `python3 -m firestarter` module-invocation gap (see Verification) is a pre-existing environment condition, not an issue caused by this plan's changes, and was not fixed (out of scope — no `__main__.py` exists anywhere in the package, unrelated to `lock-status`).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `dev lock-status` is fully wired, tested, and gated; LOCK-01 through LOCK-04 are all `Complete` in `REQUIREMENTS.md`.
- Phase 151's only remaining plan is `151-14` (the non-autonomous bench session) — this plan makes no bench-only claim and adds no bench-dependent artifact; `151-14`'s three legs (A/B/C) are unaffected by anything landed here.
- Phase 152 (Outward-Facing Close) can now cite `dev lock-status` as shipped, beta-only, with the D-07/D-06 refusal behavior proven — OUT-04 names `lock-status`, which now genuinely exists in the announced version.
- `firestarter_app` gitlink bumped to `4a6f5e8`.

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/cli_handlers.py
- FOUND: firestarter_app/firestarter/channel.py
- FOUND: firestarter_app/tests/test_lock_status_cli.py
- FOUND: firestarter_app/tests/test_dev_group_channel_gating.py
- FOUND: firestarter_app/tests/test_dev_tools_channel_gate.py
- FOUND: firestarter_app/tests/test_click_group_gate_hook.py
- FOUND: firestarter_app/tests/__snapshots__/test_characterization.ambr
- FOUND commit: 26e61d6
- FOUND commit: 674a8c0
- FOUND commit: 4a6f5e8

---
*Phase: 151-protection-readability-lock-status*
*Completed: 2026-08-20*
