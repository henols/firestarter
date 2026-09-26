---
phase: 162-chip-11-part-dev-test-sweep-on-the-reference-rig
plan: 02
subsystem: bench, rig-tooling
tags: [bench, rig-tooling, host-only, wave-0, evidence-writer, schema, no-hardware]

requires:
  - phase: 162-01
    provides: "rig-pins.json's eleven-part chips map and capture_provenance.py's derived --chip choices"
provides:
  - "bench/CHIP-EVIDENCE.jsonl — the chip sweep's own append-only record, sibling to bench/EVIDENCE.jsonl, sharing its 9-column locked core and adding a 62-column chip-sweep extension set (71 record_keys total)"
  - "tools/append_chip_evidence.py — the deriving writer that turns a dev-test report + provenance + read-back verdict into one CHIP-EVIDENCE.jsonl row, copying the report out of the frozen config dir and removing the source so the pinned config-dir digest is restored"
  - "rig-pins.json chips[*].family_label — an algorithm-keyed label sourced from v1.16's PROTOCOL-LEDGER.json, so no tool needs its own chip-slug-to-label literal"
affects: [162-05, 162-06, 162-07, 162-08, 162-09, 162-10]

tech-stack:
  added: []
  patterns:
    - "RECORD_KEYS read fresh from the target JSONL's own _schema on every call, never a module-level constant — the tool and the file cannot drift"
    - "A config-dir 'pristine' assertion performed by temporarily moving the position's own expected files OUTSIDE the tree for one canonical compute_config_dir_sha() call, then restoring them — never a re-derived SHA walk, and never a same-directory rename (which a rglob(...).is_file() walk still finds)"

key-files:
  created:
    - .planning/v1.34/bench/CHIP-EVIDENCE.jsonl
    - .planning/v1.34/tools/append_chip_evidence.py
  modified:
    - .planning/v1.34/rig-pins.json

key-decisions:
  - "Rule 2 deviation: added family_label to every rig-pins.json chips[*] entry, looked up by algorithm -> hex bucket against v1.16 PROTOCOL-LEDGER.json's proposed_name table (EPROM-STD, EPROM-QUICK, EPROM-LEGACY, FLASH-AMD-STD, FLASH-AMD-ALT, SRAM-STD) — the plan forbids a chip-slug-to-label dictionary literal inside the tool, and rig-pins.json had no label field for the appender to read"
  - "The copy-out's 'assert pristine before' step is implemented against the position's own two report files temporarily relocated to an OS temp directory (not merely renamed in place) for the duration of one check_arms.compute_config_dir_sha() call — resolves an apparent contradiction in the literal plan wording (dev test always writes its report into the config dir BEFORE this tool is ever invoked, so a literal whole-tree-equals-pristine check would always fail) while never re-deriving the SHA walk itself"
  - "Added --arms-provenance (defaulted, not in the plan's enumerated flag list) as the source of the pristine config_dir_sha pin, since check_arms.py's own docstring establishes arms-provenance.json — not rig-pins.json — as where that pin is recorded"
  - "vpp_firmware_mv and dedup_query_outcome are both scraped from --console-log via small, cited regexes (hardware.py's %u.%uV wire-frame format; submit.py's three off-TTY console strings) rather than given dedicated structured CLI inputs neither the plan's flag list nor any upstream artifact supplies"

requirements-completed: []

coverage:
  - id: D1
    description: "CHIP-EVIDENCE.jsonl's schema-only line: 9 locked columns byte-identical to EVIDENCE.jsonl's, 62 extension columns in the pinned order, record_keys = locked + extension with no duplicates, position_count_expected=11, primary_arm=v133, chip_sc04_rule states 10 + N against the roadmap's 11 + N"
    requirement: "CHIP-01"
    verification:
      - kind: unit
        ref: "python3 -c assertion scripts over CHIP-EVIDENCE.jsonl (see 162-02-PLAN.md Task 1 verify block); gate_record.py --jsonl CHIP-EVIDENCE.jsonl --pins rig-pins.json"
        status: pass
    human_judgment: false
  - id: D2
    description: "append_chip_evidence.py derives every machine field, copies the dev-test report out of the frozen config dir and removes the source, refuses eleven distinct incomplete-position shapes by name, and delegates every shared guarantee to its owning sibling"
    requirement: "CHIP-02"
    verification:
      - kind: unit
        ref: "python3 append_chip_evidence.py --selftest (18/18 legs: 7 positive + 11 negative)"
        status: pass
    human_judgment: false
  - id: D3
    description: "run_gates.sh reports 13/13 tool selftests (append_chip_evidence.py is the 13th) and 5/5 live gates, exit 0, with EVIDENCE.jsonl byte-unchanged and both sub-repo porcelains empty"
    verification:
      - kind: integration
        ref: "bash .planning/v1.34/tools/run_gates.sh; RC=$? (read directly, never piped)"
        status: pass
    human_judgment: false

duration: 33min
completed: 2026-08-28
status: complete
---

# Phase 162 Plan 02: CHIP-EVIDENCE.jsonl Schema + append_chip_evidence.py Summary

**Created the chip sweep's own append-only record (`bench/CHIP-EVIDENCE.jsonl`, 71 record_keys: 9 locked + 62 extension) and `append_chip_evidence.py`, the deriving writer that turns a `dev test` report plus provenance plus a read-back verdict into one row, copying the report out of the frozen config dir and removing the source so the pinned config-dir digest is restored — `run_gates.sh` now reports 13/13 tool selftests and 5/5 live gates, exit 0.**

## Performance

- **Duration:** ~33 min
- **Started:** 2026-08-28T16:16:33Z (approx, after the prior-wave tracking commit)
- **Completed:** 2026-08-28T16:49:06Z
- **Tasks:** 2/2 completed
- **Files modified:** 1 modified (rig-pins.json, Rule 2 deviation), 2 created

## Accomplishments

- `bench/CHIP-EVIDENCE.jsonl` created holding exactly one line: a `_schema` header whose
  nine `locked_columns` (`chip`, `family`, `board`, `shield`, `blank_state`, `op`, `sha256`,
  `verdict`, `anomalies`) are byte-identical to `EVIDENCE.jsonl`'s, and whose 62
  `evid_extension_columns` are pinned in the exact order the plan's acceptance table
  specifies. `record_keys` (71 entries) satisfies `locked_columns + evid_extension_columns`
  with no duplicates. `position_count_expected` is `11`, `primary_arm` is `"v133"`.
  `close01_counting_rule` and `chip_sc04_rule` are both stated as equations over rows, and
  `chip_sc04_rule` states total runs as `10 + N` on the same line as the roadmap's `11 + N`
  reading, naming the deliberate deviation under D-06/D-14. `not_measured_convention` and
  `jsonl_convention` are byte-equal to `EVIDENCE.jsonl`'s apart from filename substitutions.
  `gate_record.py --jsonl CHIP-EVIDENCE.jsonl --pins rig-pins.json` validates it with 0
  violations and no new argument. `EVIDENCE.jsonl` stayed byte-unchanged throughout.
- `append_chip_evidence.py` built as a full sibling to `append_evidence.py`: stdlib-only,
  imports `gate_record`, `render_evidence`, `check_arms` and `capture_provenance` via the
  `importlib.util.spec_from_file_location` house idiom, and never re-implements the
  `not measured` regex, the JSONL append, or the config-dir SHA walk. Every per-step lookup
  (`step_verdicts`, `step_run_counts`, `write_target`, `write_coverage`, `uv_slot`, ...)
  accepts both `write` and `write-partial` op strings. `RECORD_KEYS` is never a module-level
  constant — it is read from the target JSONL's own `_schema` on every call. The `family`
  column's label is read from `rig-pins.json`'s own `family_label` field, never a two-part
  literal inside the tool, and `algorithm` is hard-indexed (no `.get(..., 0)` default).
- The copy-out (PD-3) is implemented as: assert the frozen config dir's digest matches
  `arms-provenance.json`'s pristine pin with this position's own two expected report files
  temporarily relocated to an OS temp directory for the duration of one
  `check_arms.compute_config_dir_sha()` call (see "Deviations" for why a same-directory
  rename doesn't work and why this ordering needed reinterpreting); read + derive from the
  report; copy both files to `<cell-dir>/reports/<position_id>.{json,md}` (containment
  checked via `capture_provenance.resolve_out_path`); verify both copies' SHA-256 match
  their sources; remove the two source files only (never the `reports/` directory); assert
  the digest again with a plain, unmodified `compute_config_dir_sha()` call; then append via
  `render_evidence.append_row_to_file`.
- `--selftest` carries all 18 named legs (7 positive + 11 negative), each asserting on a
  named reason substring, all green (list below).
- `run_gates.sh` reports **13/13 tool selftests, 5/5 live gates, exit 0** (read directly).
  `.planning/v1.34/tools/` holds exactly 13 `.py` files. Both sub-repo porcelains (`git -C
  /workspaces/firestarter status --porcelain`, `git -C /workspaces/firestarter_app status
  --porcelain`) are empty.

## Task Commits

1. **Task 1: Write CHIP-EVIDENCE.jsonl's _schema — the sibling record shape** - `6484874a` (feat), preceded by `7189332c` (fix — Rule 2 deviation, see below)
2. **Task 2: Build append_chip_evidence.py — derive, copy out, remove, refuse, append** - `5be59ece` (feat)

**Plan metadata:** committed via this SUMMARY + STATE.md update (docs commit follows)

## Files Created/Modified

- `.planning/v1.34/bench/CHIP-EVIDENCE.jsonl` — new, schema-only line 1, 71 `record_keys`
- `.planning/v1.34/tools/append_chip_evidence.py` — new, 1795 lines, 18-leg `--selftest`
- `.planning/v1.34/rig-pins.json` — `family_label` added to all 11 `chips[*]` entries (Rule 2 deviation, see below); `chips_note`/`chips_family_label_source` extended

## Decisions Made

- **The final `record_keys` count and split:** 9 locked + 62 extension = **71** `record_keys`.
  No column was added to or renamed from the plan's table — the 62 extension columns are
  exactly as enumerated, in the pinned order.
- **The appender's argument surface as built, and its one divergence from the proposal:**
  all 25 flags the plan named are present (`--position-id`, `--arm`, `--chip`,
  `--chip-token`, `--cell-dir`, `--report-json`, `--report-md`, `--provenance`,
  `--readback`, `--exit-code`, `--console-log`, `--commands-extra`, `--pins`, `--jsonl`,
  `--verdict-file`, `--anomalies-file`, `--vpp-real-mv`, `--prior-disposition-file`,
  `--divergence-verdict`, `--known-carried`, `--control-rerun-for`, `--named-absence`,
  `--jp4`, `--reseat-count`, `--dry-run`, `--selftest`). One flag was **added** beyond the
  plan's enumerated list: **`--arms-provenance`** (defaulted to
  `<milestone>/arms-provenance.json`), because `check_arms.py`'s own docstring establishes
  that file — not `rig-pins.json` — as where the pristine `config_dir_sha` pin lives
  (`compute_config_dir_sha()`'s docstring: "matches the exact scheme recorded in
  arms-provenance.json's config_dir_sha"), and `run_gates.sh` itself already reads that same
  file for the identical purpose when invoking `check_arms.py`.
- **The copy-out ordering, reinterpreted, and why:** the plan's literal wording ("assert the
  live config-dir digest equals the pristine pin ... THEN read the report JSON") cannot hold
  literally, because `firestarter dev test <chip>` unconditionally persists its report into
  `<config_dir>/reports/` *before* this tool is ever invoked — so at invocation time the
  frozen dir already differs from the milestone's one-time pristine pin by exactly the
  report this position produced. Implemented instead as: compute
  `check_arms.compute_config_dir_sha()` with this position's own two expected report files
  temporarily **moved to an OS temp directory** (not merely renamed in place — a
  same-directory rename is still a file the `rglob(...).is_file()` walk finds) for the
  duration of the call, then restored. This lets a genuinely dirty dir (a stray leftover
  file from an earlier incomplete run) still fail, named by path, while the position's own
  legitimate report is not mistaken for dirt. The digest walk itself is never re-derived —
  `check_arms.compute_config_dir_sha()` is the only function called, both before (with files
  set aside) and after (plain, nothing set aside) removal.
- **Which sibling supplied the digest walk:** `check_arms.py`'s `compute_config_dir_sha()`,
  unmodified, called via the same `spec_from_file_location` idiom every other sibling
  delegation uses.
- **The three `dedup_query_outcome` detection strings, as implemented:** scraped from
  `--console-log` against `submit.py`'s own off-TTY branch strings — `"you appear to have
  already reported this"` → `prior report found`; `"the duplicate check could not run"` →
  `duplicate check could not run (gh absent, unauthenticated, or offline)`; neither string
  present but a `https://github.com/henols/firestarter_prom/issues/new?` URL line is →
  `duplicate check ran, no prior report found`. None of the three present → a `not measured
  — <reason>` fallback (not one of the plan's 11 named negative legs, so this is a soft
  fallback rather than a hard refusal).
- **`vpp_firmware_mv` derivation:** scraped from `--console-log` via a small regex mirroring
  `hardware.py`'s own `"%u.%uV"` wire-frame format (`hardware.py`'s `_VOLTAGE_RE`), cited not
  imported — the standalone `firestarter vpp` command's console line is the only place this
  value exists, and neither the plan's flag list nor any upstream JSON artifact carries it.
- **`prior_disposition`/`prior_disposition_source`/`prior_dispositions_all`:**
  `--prior-disposition-file`'s content is split into non-blank lines; the first line is the
  "newest" `prior_disposition`; the full line list is `prior_dispositions_all`;
  `prior_disposition_source` is a best-effort regex extraction of a `vX.Y ... NN` citation
  from the newest line, falling back to a `not measured — <reason>` shape when the prose
  carries no recognizable citation. This is a documented, defensible interpretation of an
  ambiguous column spec, not gated by any of the 18 selftest legs.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added `family_label` to every `rig-pins.json` chips entry**
- **Found during:** Task 2 (deriving the `family` locked column)
- **Issue:** The plan requires `family`'s label to be "taken from the pin map — not from a
  two-part literal inside the tool," and the acceptance criteria explicitly forbid a
  chip-slug-to-label dictionary literal in `append_chip_evidence.py`. `rig-pins.json`'s
  `chips` map had no label field at all.
- **Fix:** Added `family_label` to all 11 `chips[*]` entries, looked up programmatically by
  algorithm → hex bucket (`"0x%02X" % algorithm`) against v1.16's
  `PROTOCOL-LEDGER.json`'s `rows[*].bucket` → `rows[*].proposed_name` table (all six buckets
  this milestone's 11 parts use — `EPROM-STD`, `EPROM-QUICK`, `EPROM-LEGACY`,
  `FLASH-AMD-STD`, `FLASH-AMD-ALT`, `SRAM-STD` — were present; zero misses). Added
  `chips_family_label_source` documenting the derivation. FM1608's algorithm 40 (`0x28`)
  correctly resolves to `SRAM-STD`, matching `PROTOCOL-LEDGER.md`'s own NAME-04 correction of
  v1.15 `EVIDENCE.md`'s stale `0x40 (SRAM_STD / FRAM)` label.
- **Files modified:** `.planning/v1.34/rig-pins.json`
- **Verification:** `run_gates.sh` reconfirmed 12/12 selftests + 5/5 live gates, exit 0,
  immediately after this edit and before Task 1 began; `family_label` present and
  correct on all 11 entries.
- **Committed in:** `7189332c` (separate commit, before Task 1)

---

**Total deviations:** 1 auto-fixed (Rule 2 — missing critical functionality)
**Impact on plan:** Necessary for the plan's own explicit prohibition against a family-label
literal inside the tool. No scope creep — the edit is additive (one new field per chip entry
plus one new note) and every pre-existing `chips[*]` field is byte-unchanged.

## Known Stubs

None. `prior_disposition_source`'s regex-based citation extraction is a best-effort
derivation over free-text human prose, not a stub — it degrades honestly to a named
`not measured — <reason>` shape rather than fabricating a citation, and no plan
requirement or selftest leg depends on it succeeding.

## Threat Flags

None beyond what the plan's own `<threat_model>` already covers (T-162-06 through T-162-12,
T-162-SC). No new network endpoint, auth path, or schema change at a trust boundary was
introduced.

## Issues Encountered

- The plan's literal copy-out step ordering ("assert pristine BEFORE reading the report")
  cannot hold as written, since `dev test` always persists its report into the config dir
  before this tool runs. Resolved per "Decisions Made" above (move-aside-then-restore
  against the position's own expected files) — a Rule 3 blocking-issue fix, not a
  deviation from the plan's intent (a dirty config dir is still caught and named; a
  pristine one still passes; the frozen digest is still verified restored after removal).
- The `_assert_pristine_ignoring_expected` helper's first implementation renamed the
  position's report files IN PLACE (same directory, new suffix) rather than moving them
  fully outside the tree; `compute_config_dir_sha`'s `rglob(...).is_file()` walk still found
  the renamed file, so the "before" check always failed even on a clean fixture. Fixed by
  relocating the files to a genuinely separate OS temp directory for the duration of the
  check, then restoring them — caught by the selftest's own positive legs before this
  SUMMARY was written, not discovered later.

## Next Steps

Plans 162-05 through 162-10 can now invoke `append_chip_evidence.py` for each of the ten
primary v133 positions plus the 2516 named absence and any divergence-driven control
re-runs, citing `CHIP-EVIDENCE.jsonl`'s schema for the counting/exclusion rules and this
tool's 18-leg selftest for the refusal behavior it can rely on.

## Self-Check: PASSED

All created/modified files verified present on disk (`CHIP-EVIDENCE.jsonl`,
`append_chip_evidence.py`, `rig-pins.json`'s `family_label` additions); all three task/fix
commit hashes (`7189332c`, `6484874a`, `5be59ece`) verified present in
`git log --oneline --all`.
