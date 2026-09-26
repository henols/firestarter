# Deferred items — Phase 154

Out-of-scope discoveries found during execution. Logged, not fixed.

## D1 — Malformed stray `/workspaces/platformio.ini` breaks any meta-root `pio` invocation

**Found during:** Plan 01, Task 3 (capturing tool versions).

`/workspaces/platformio.ini` exists as an untracked, gitignored 21 KB file
(`.gitignore:20` ignores `platformio.ini`, so it is invisible to `git status`). It is
malformed — duplicate `[platformio]` section at line 26 — so **any** `pio` invocation
whose cwd is `/workspaces` dies:

```
platformio.project.exception.InvalidProjectConfError: Invalid '/workspaces/platformio.ini'
(project configuration file): 'While reading from '/workspaces/platformio.ini' [line 26]:
section 'platformio' already exists'
```

Even a bare `pio --version` crashes (it prints the version, then dies in the atexit
telemetry hook when it tries to resolve `core_dir` from the project config).

**Impact on this phase:** none, provided every oracle invocation in plans 06-11 does
`cd /workspaces/firestarter` first. Recorded in
`.planning/v1.33/baseline-pre-sweep.md` §6 as a TRAP.

**Why deferred:** the file is not tracked by any of the three repos, is not this phase's
work, and Phase 154's scope is comment text only. Fixing or deleting it is a devcontainer
hygiene change with no requirement behind it.

**Suggested disposition:** delete it, or repair the duplicate section, in a separate
housekeeping task. Verify with `pio --version` exiting 0.

## D2 — Research finding F7's module count is 9; measured is 7

**Found during:** Plan 01, Task 2 (verifying the porcelain-assertion constraint).

F7 states "9 modules assert git porcelain". Grep of both repos this session finds **7**
modules: 4 in `firestarter_app/tests/` (`test_cap03_ack_layout_parity.py`,
`test_py32_flash_map_host.py`, `test_json_key_parity.py`, `test_py32_asset_name_host.py`)
and 3 in `firestarter/tests/` (`test_requirement_case_mapping_v131.py`,
`test_trace_segment_exhaustiveness_v131.py`, `test_flash_path_record_sync.py`).

**The load-bearing half of F7 is confirmed:** every one of the 7 asserts on the
**firmware** repo, so `firestarter_app`'s untracked files are harmless to all gates.

**Why deferred:** the count does not change any decision. F7's conclusion stands. The
delta is recorded rather than corrected in either direction, per this phase's
measure-both-sides rule.

## D3 — The manifest's `source_text` side is the WORKING TREE, not `pre_sweep_shas`

**Found during:** Plan 05, Task 2 (dry-running the finished tool against the real
13,692-record manifest as a scale check).

`build_citation_manifest.py` reads every `source_text` from the file **on disk**, while the
header records `pre_sweep_shas` = each sub-repo's `git rev-parse HEAD` at generation time.
For the 169 clean candidate files those coincide. For the **two** files plan 03 had already
modified in `firestarter_app`'s working tree — `tests/test_dispatch_mirror.py` and
`tests/test_sdp_table_parity.py` — they do not: measured, `6bfa645:./tests/test_dispatch_mirror.py`
is 222 lines and the working tree is 362, so old lines ≥ 23 shift by **+5**.

**Measured consequence:** the 7 manifest records targeting `test_dispatch_mirror.py` are all
recognised as **fixed points** and the tool is a correct no-op on them, because their recorded
`source_text` is the post-plan-03 text that already sits at the recorded line. The
fixed-point-first ordering is what turned a stale anchor into a safe no-op instead of a wrong
rewrite — the exact property SWEEP-11 asks for.

**What Phase 159 must do about it:** the app-side "old" anchor for the composite map is the
**plan 12 commit** (which contains plan 03's edits), not `6bfa6453d1bac232eb81ab35fa7f14b50b0b291a`.
This is precisely why `--pre-sweep-sha` is an argv argument that beats the header. Nothing needs
fixing in the manifest.

**Why deferred:** correcting it would mean regenerating plan 04's committed manifest, and D-11
reserves `firestarter_app`'s single commit for plan 12. Recorded, not corrected.

## D4 — 15 manifest records against `.planning/STATE.md` no longer bind

**Found during:** Plan 05, Task 2 (the same real-manifest dry run).

All 15 "binding is ambiguous" residues in the real dry run are in `.planning/STATE.md`, whose
line numbers have drifted since plan 04 generated the manifest — every plan's `state_updates`
step rewrites it. The tool **refuses** rather than guessing, which is the intended fail-closed
behaviour, and it names each one.

**Why deferred:** STATE.md is machine-maintained bookkeeping, not source provenance. The honest
options are to re-generate the manifest immediately before Phase 159's remap, or to exclude
`.planning/STATE.md` from the citation corpus. Either is a Phase 159 / SWEEP-12 decision, not a
plan 05 one.

## D5 — 152 mid-comment provenance-token lines have no survey hit to anchor them

**Found during:** Plan 07, Task 1 (building the worklist).

`survey_provenance.py`'s regex requires the token to sit **immediately after** a comment
opener, so a token deeper inside a comment line is not a hit. Measured over
`firestarter/{src,include}` with a token-anywhere scan restricted to comment lines:

| When | Mid-comment-only lines (no survey hit) |
|---|---|
| before plan 07 | **203** |
| after plan 07 | **152** |

Plan 07 removed 51 of them as a side-effect of §2's unit-of-edit rule (every D-01 token in a
block being edited is stripped). Of the surviving 152, **28** are in `src/proms/eprom.cpp` and
**7** in `include/eprom_params.h` — both Ruling B exempted — leaving **117** in files this plan
swept to 0 *hits*. Largest remaining: `include/firestarter.h` 18, `include/rurp_config_storage.h`
12, `include/rurp_pinout.h` 10, `src/proms/memory.cpp` 9, `include/rurp_hw_rev_utils.h` 9
(a file with **zero** survey hits at all), `include/eprom_budget.h` 8, `include/eprom.h` 8.

**Why deferred:** no survey hit anchors them, so they are outside the worklist authority
plan 07 was given (`survey_provenance.py --group fw-src --group fw-include` is the plan's
named worklist). Several sit in long structural file-header blocks whose section headings
*are* decision IDs (`WHY EXACTLY TWO FUNCTIONS (D-06):`), which is a prose-restructuring job,
not a token strip. Removing them is a second, uniform mechanical pass — and the host repo
will have the same population, so it should be decided once for both repos, not per plan.

**Suggested disposition:** a follow-on plan (or a widened `survey_provenance.py` mode:
`--token-anywhere`) that measures both repos and sweeps them together. The byte-identity
oracle covers the firmware half of that work exactly as it covered this one.

## D6 — `test_config_schema_pinned.py` pins exact source LINE NUMBERS; Section B classified it "control — safe"

**Found during:** Plan 07, Task 3 (firmware gate suite after the sweep).

`sweep-gate-dispositions.md` §B row 6 dispositioned `test_config_schema_pinned.py` as
**control**, on the verified basis that "its declared-field extraction targets struct syntax,
not comment text". That is true of the struct legs — but the module carries a **second**
mechanism the row does not mention: `_C14_CONSUMER_SITES` is a 9-tuple of
`(path, exact 1-indexed line number, function name)`, asserted by
`_consumer_census_violations`. A comment-only edit that changes a file's line count breaks it,
and this sweep did: `test_the_seven_consumers_call_only_the_public_api` went **RED** with
5 named violations.

Repaired in plan 07 by re-pinning to the live call sites (`firestarter.cpp` 41→38, 119→115,
125→121; `hardware_operations.cpp` 107→106, 119→118), with the shift and its cause recorded
in the tuple's own comment — the file's established idiom, which already carried two earlier
re-pins for the same class of cause (+1 from an added `#include`, +15 from a widened comment
block). Module back to 17/17.

**Why recorded here:** the *disposition table* is wrong, not the repair. Any later
line-shifting phase in this milestone (155–158 all shift lines) will trip the same leg, and
§B's "control" verdict tells a reader it cannot. A repo-wide grep this session finds this is
the **only** executable line-number pin over swept firmware paths in either repo
(`firestarter_app`'s two `file:line` references are docstring prose, not assertions).

**Suggested disposition:** amend §B row 6 to `control (struct legs) + LINE-PINNED (consumer
census)` when the dispositions file is next touched, and name the census in Phases 155–158's
success criteria.

## D7 — ~~BLOCKER~~ **RESOLVED in plan 11**: plan 07's `firestarter/src/firestarter.cpp` sweep broke a host gate that pins the literal string `"Phase 151"`

**Found during:** Plan 09, Task 2 (first full host-suite run of the phase).
**Severity:** was a BLOCKER for plan 12's phase gate. **CLEARED 2026-08-23 by plan 11**, as an
orchestrator-assigned task beyond that plan's written scope.

**Resolution (plan 11, Task 3) — the pin moved from the LABEL to the CLAIM.** Option 2 (restore
the label in firmware source) was rejected outright: it would mean shipping a phase label in
swept firmware source, defeating the phase. Option 1 was taken and strengthened:

- `test_diagnostic_range_unchanged_with_phase_151_comment` →
  `test_diagnostic_range_unchanged_with_stated_choice_comment`;
  `_PHASE_151_LOOKBACK_CHARS` → `_STATED_CHOICE_LOOKBACK_CHARS`.
- `assert "Phase 151" in preceding_text` → `assert not _missing_stated_choice_phrases(...)`
  over a **four-phrase conjunction**, ALL of which must be present:
  `CMD_LOCK_STATUS (16)`, `CMD_READ_VPP (11)`, `this is a CHOICE`, `DBG_* diagnostic`.
  None is provenance, so no future sweep can break it the way this one broke the label pin.
- **Proven strictly stronger, not merely different.** Against a planted
  `// Phase 151 touched this block.` replacing the whole comment block, the OLD pin passes
  **vacuously** and the new conjunction reports all four phrases missing. Against a planted
  removal of the deliberateness sentence and the `DBG_*` consequence (both ordinals kept), it
  reports `missing ['this is a CHOICE', 'DBG_* diagnostic']`. Both plants run in a throwaway
  `git clone --shared` of the swept firmware tree; the real repo was never written to (still
  exactly 93 modified paths afterwards) and the clone was deleted.
- A committed checkable negative was added as **leg 5**
  (`test_non_vacuity_control_reports_absent_stated_choice`), mirroring the module's own leg-4
  synthetic-string idiom (this module cannot `monkeypatch.setenv` `FIRESTARTER_FW_ROOT` —
  `fw_presence.py` binds `FW_ROOT` at import time, correction C-15), asserting BOTH directions
  so the control cannot pass by reporting absence unconditionally.

**Measured outcome:** module 3 passed / 1 failed → **5 passed**. Clean clone carrying both
repos' swept blobs committed: **1976 passed / 0 failed / 0 skipped** (1975 + leg 5). Real
D-11-dirty tree: 1965 passed / 11 failed = 1976, all 11 the `_git_porcelain` class. Plan 12's
phase gate is unblocked, and must still run only AFTER both sub-repo commits land.

**The class remains worth naming for future phases:** this was the third comment-sensitive host
gate over firmware source, and the only one pinning a *provenance label itself*. Any later phase
that deletes provenance from firmware source should grep the host test suite for the label
before deleting it.

---

### Original filing (kept verbatim for the record)

`firestarter_app/tests/test_parse_gate_admission.py::test_diagnostic_range_unchanged_with_phase_151_comment`
asserts `"Phase 151" in preceding_text` over the raw text of
`fw_path("src", "firestarter.cpp")` — a 1200-character lookback window above the
`handle->cmd > CMD_IDLE && handle->cmd < CMD_READ_VPP` diagnostic-range guard
(`test_parse_gate_admission.py:141` `_PHASE_151_LOOKBACK_CHARS`, assertion at :175).

Plan 07 stripped that exact label:

```diff
-    // Phase 151 (LOCK-02, OD-3): CMD_LOCK_STATUS (16) is numerically greater
-    // than CMD_READ_VPP (11), so it falls outside this range by construction
-    // -- this is a CHOICE recorded here, not a discovery made on the bench.
+    // CMD_LOCK_STATUS (16) is numerically greater than CMD_READ_VPP (11), so
+    // it falls outside this range by construction -- this is a CHOICE
+    // recorded here, not a discovery made on the bench.
```

Measured: `git show 8695ee52:src/firestarter.cpp | grep -c 'Phase 151'` = **3**;
`grep -c 'Phase 151' src/firestarter.cpp` on the swept tree = **0**.

**Why plan 07 did not see it.** Plan 07 ran the *firmware* repo's Python gate suite
(323 legs) and a nine-module comment-sensitive host subset in a clean clone. This module
was in neither set. It is a **third** comment-sensitive host gate over firmware source,
beyond the two `sweep-gate-dispositions.md` already names (`test_cap03_ack_layout_parity.py`'s
`_WIRE_LAYOUT_COMMENT`, and D6's `test_config_schema_pinned.py` line pins) — and unlike
those two it pins a **provenance label itself**, which is precisely what this phase deletes.
It is the `reference_firmware_renames_break_host_source_scanning_gates` class, inverted:
the gate does not fail open, it fails closed on the sweep's intended outcome.

**Measured impact:** it is the ONE genuine failure in the whole host suite. A clean
`--shared` clone carrying both repos' swept blobs committed runs
**1 failed / 1971 passed / 3 skipped** — this leg is the single failure.

**Why not repaired in plan 09.** The two candidate fixes both land outside this plan's
`<domain>` (`firestarter_app/firestarter` only):
1. Retarget the pin in `firestarter_app/tests/test_parse_gate_admission.py` — **plan 11's**
   file, and a judgment call about what should replace `"Phase 151"` (the sentence's real
   content is "CMD_LOCK_STATUS (16) > CMD_READ_VPP (11), so it falls outside this range by
   construction -- a CHOICE, not a discovery", which survives the sweep intact and is the
   obvious substitute anchor).
2. Restore the label in `firestarter/src/firestarter.cpp` under a D-02-style exemption —
   **plan 07's** file, and it would mean shipping a phase label in swept firmware source.

**Suggested disposition:** plan 11 re-anchors the assertion onto the surviving sentence
(e.g. `"this is a CHOICE recorded here"` plus `"CMD_LOCK_STATUS (16)"`), which pins the
*decision* rather than the *phase number* and is what the leg's own docstring says it is
for ("DESIGN.md §7's stated choice ... must be recorded there, not left to be
rediscovered"). Plan 12 must not run its phase gate before this is done.

## D8 — app-pkg mid-comment provenance tokens (236 lines) and non-comment-line tokens (335) left unswept, measured

**Found during:** Plan 09, Task 2.

Same class as D5, measured on the host side. In `firestarter_app/firestarter`:

| Population | Pre-sweep | Post-sweep | Cause |
|---|---|---|---|
| `#`-comment lines carrying a D-01 token NOT adjacent to the opener | **313** | **236** | outside the survey regex (it requires adjacency); 77 fell incidentally to the §2 unit-of-edit rule inside blocks that were being edited anyway |
| Token occurrences on non-`#` lines (docstrings + string literals) | **335** across 22 files | **335**, unchanged | outside the corpus by definition; proven unchanged by the AST-equality oracle (all 20 modified files' `ast.dump` digests identical) |

236 is nearly twice this plan's whole measured corpus (132), and 335 more sit in
docstrings. Neither has a measurement behind it that would justify sweeping it inside a
plan scoped to 132 hits, so both are recorded rather than swept — the same call plan 07
made for the firmware half (D5).

**One concrete instance worth naming separately:** `chip_test.py:440`'s
`_SDP_LOCKED_REASON = 'write_scope="none": {op} omitted (D-18)'` is a **shipped
user-facing string literal** carrying a decision ID. It reaches `dev test` reports a
community tester reads. That is a real product-surface leak of a planning ID, not a
comment, and fixing it is a behaviour change (a report-text change with a snapshot to
re-pin), so it is out of any comment-sweep plan's scope.

**Suggested disposition:** fold D5 and D8 into one `--token-anywhere` follow-on that
decides both repos together; file the `_SDP_LOCKED_REASON` leak as its own todo, since it
needs a snapshot update rather than a comment edit.

## D9 — Pre-existing `ruff check` findings in `firestarter_app/tools` (unrelated to the sweep)

**Found during:** Plan 10, Task 2 (ruff sanity check after the app-tools sweep).

`ruff check tools/` reports 4 pre-existing errors, none touching a line this plan edited:

- `tools/catalog/codegen_vectors.py:35-36` — unsorted import block (`tomllib` after
  `pathlib`).
- `tools/catalog/codegen_vectors.py:189` — `UP031` (`"0x%02X" % b` instead of a format
  spec).
- `tools/audit_coverage_matrix.py:37-46` — unsorted import block (the `firestarter.database`
  import with its `# noqa: F401` trailing comment).

Verified out-of-scope by re-running `ruff check tools/` against a `git stash`-restored
pre-sweep tree: identical 4 errors, byte-for-byte same messages, before this plan touched
anything. (Note: `git stash` was used here on the plain `firestarter_app` checkout, which
is not a Claude Code worktree — `.git` is a real directory, not the worktree-linking file —
so the shared-`refs/stash`-across-worktrees hazard the destructive-git-prohibition section
warns about does not apply to this repo layout. State was verified fully intact via
`git status --short` and a hit-count re-check after the pop. Future executions should still
prefer the throwaway-branch technique over `git stash` as the safer default.)

**Why deferred:** out of this plan's `<files>` scope (`diff_db.py`, `check_dispatch.py`,
`build_db.py`, and the six task-2 files) and unrelated to comment provenance. Fixing import
order or format-spec style is a separate lint-hygiene task.

**Suggested disposition:** a small follow-on `ruff --fix` pass over `firestarter_app/tools`,
reviewed for the one `--unsafe-fixes`-only hidden fix before applying.
