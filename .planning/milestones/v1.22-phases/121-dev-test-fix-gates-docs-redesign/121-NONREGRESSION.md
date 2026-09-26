# Phase 121 Non-Regression Sweep — `dev test` FIX + GATES + DOCS + REDESIGN, closed at GATE-03

**Written:** 2026-07-29 (Plan 121-14)
**Firmware phase base:** `0048b3d` (Phase 119's own sweep HEAD) · **Host phase base:** `96e0622` (confirmed by `121-RESEARCH.md`) · **Meta phase base:** the commit preceding `121-01`'s golden regen
**Firmware HEAD at this sweep:** `48c36e569c8ddfd3daa8aea7e55c5bbc79b48b08` · **Host HEAD at this sweep:** `c3c9424f7a299c6ff3498a15620e5235cf72a782`

This is the single artifact a later reader should open to answer "what did Phase 121 change, and
what did it prove unchanged, at the phase's actual final commit". Per the mandatory discipline
inherited from `119-NONREGRESSION.md` §CORRECTION-4 and restated by `120-NONREGRESSION.md`, every
row below was **re-executed in this session** — nothing here is copied from a prior plan's
SUMMARY. Where a prior plan's SUMMARY made a claim this document re-checks it against the live
tree and says so.

---

## 1. The claim, as precise statements

Each statement below is individually checkable against the artifacts named in §2-§4, not merely
asserted:

1. **An unmapped `dev test` op string cannot reach a chip-mutating operator method.** The
   fail-closed arm added ahead of `OP_WRITE_PARTIAL` (Plan 121-02) means `_dispatch_step` /
   `_dispatch_multi_run` never fall through to `erase_eprom` for an op they do not recognise —
   verified structurally present in `_DESTRUCTIVE_OPS`/dispatch and by the still-green
   `test_chip_test.py` suite (§4, row-adjacent host pytest count).
2. **UV-ness is decided once, from the exact `electrical-type` axis, and only read downstream.**
   `chip_test.is_uv_eprom(full)` measures **301/301** against the live 746-entry DB (re-derived
   live this session, §"Requirement Row Re-Verification" below); `_is_uv_eprom` in
   `cli_handlers.py` reads it from `app.db.get_eprom(chip)` — never `resolve_chip`'s programmer
   dict.
3. **The partial write is inside the chip-ID destructive gate.** `OP_WRITE_PARTIAL` is a live
   member of `_DESTRUCTIVE_OPS` (confirmed: `frozenset({'erase', 'write-partial', 'write'})`),
   so a chip-ID mismatch gates it exactly like a full write.
4. **The erase step is `NA` on `0x0D` with an actionable, family-fact reason.** Confirmed live
   this session: `derive_plan('AT28C256', db, write_scope='full')`'s erase step reads
   `supported=False`, `reason="protocol 0x0D (28C family) has no erase operation; each page write
   auto-erases internally"` — the string contains `0x0D`, not `FLAG_CAN_ERASE`.
5. **`dev test <chip>` takes no options and always writes.** Confirmed live: the handler's
   callback signature is `(app, chip)`; each of the five removed flag spellings
   (`--destructive`, `--output-dir`, `-y`, `--yes`, `--submit`) errors `No such option` at exit
   code 2 when passed.
6. **Every run runs the dedup check, then asks.** `submit_report`'s Step 3
   (`find_prior_report_fn`) is called unconditionally, before the Step 5 ask, on every reached
   path including off-TTY — confirmed by reading the live source and by the green
   `test_submit.py` dedup/ordering legs (§ Requirement Row Re-Verification).
7. **The docs say so.** All eight GATE-02-named docs across both sub-repos carry the no-erase
   statement (firmware-side four) and the always-writes statement with zero residual
   "non-destructive" wording (host tester-facing three) — grepped live, not trusted from
   `121-13-SUMMARY.md`'s own assertion (§ Requirement Row Re-Verification).

Everything else this phase touched — the catalog string (D-15), the SDP-capability gate
(GATE-01), the audit-matrix golden (D-18) — is covered in its own section below.

---

## 2. The command-by-gate matrix

Every command below was executed in this session at the phase's final commit
(`firestarter@48c36e5`, `firestarter_app@c3c9424`). "Baseline" is `121-RESEARCH.md` §F-8's
measured figures (this phase's own start-of-phase baseline) unless noted otherwise.

| # | Gate | Exact command | Result this sweep | vs. baseline |
|---|---|---|---|---|
| 1 | Firmware native suite | `cd firestarter && pio test -e native` | **141/141 PASSED**, 17 groups | Unchanged (F-8 row 1) |
| 2 | Firmware native, no `DEV_TOOLS` | `pio test -e native_nodevtools` | **141/141 PASSED**, identical to row 1 | Unchanged (F-8 row 1b) |
| 3 | AVR builds | `pio run` (uno, uno328pb, leonardo) | **3/3 SUCCESS** — Leonardo 26072/28672, Uno 23932/32256, uno328pb 23976/32384 | **Unchanged from Phase 119's final measurement** — confirms `121-12`'s finding that the messages.toml edit produced a byte-identical `messages.h` |
| 4 | Host pytest, devcontainer interpreter | `python3 -m pytest tests/` (Python 3.12.13) | **1134 passed, 0 failed** in 51.83s; "29 snapshots passed" | **CHANGED BY DESIGN** — up from baseline 1051/1052 (F-8 row 2/3); this phase added ~83 new tests across 121-01..13. Matches `121-13-SUMMARY.md`'s own recorded 1134, independently reproduced |
| 5 | Host pytest, CI-parity Python 3.11 | `uv`-provisioned `/tmp/venv311/bin/python -m pytest tests/` (Python 3.11.15) | **1134 passed, 0 failed** in 52.39s — identical failure set (none) to row 4 | Confirms parity holds across the devcontainer/CI-target interpreter split |
| 6 | Coverage gate | `/tmp/venv311/bin/python -m pytest tests/ --cov=firestarter --cov-fail-under=70` | **81.86%** — passes with 11.9 pts headroom | Baseline was 82.47%/81.91%/81.86% across 121-08/09/11's own runs — consistent, no regression |
| 7 | `ruff check` | `/tmp/venv311/bin/ruff check firestarter/ tests/ tools/` (ruff **0.16.0**, the CI-resolved version) | **4 errors, 3 files** (`tools/audit_coverage_matrix.py` I001, `tools/catalog/codegen.py` I001, `tools/catalog/codegen_vectors.py` I001+UP031) | **CHANGED BY DESIGN, but not this phase's diff** — `git -C firestarter_app diff --stat 96e0622..HEAD -- <these 4 files + .github/scripts/update_version.py>` is **empty**: none of these files were touched by any Phase 121 plan. Pre-existing findings, same class as F-8 row 5's baseline. **The devcontainer's own globally-installed `ruff` has since drifted to 0.16.0 as well** (confirmed: `ruff --version` on `PATH` → 0.16.0) — RESEARCH's Pitfall 2 divergence (0.15.20 vs 0.16.0) is **no longer reproducible in this environment**; both now agree. The CI-resolved version is still the one reported here per the plan's mandate. |
| 8 | `ruff format --check` | `/tmp/venv311/bin/ruff format --check firestarter/ tests/ tools/` (ruff 0.16.0) | **3 files would be reformatted** (same 3 files as row 7, plus `tools/check_mypy_watermark.py`) | Same empty-diff proof as row 7 — pre-existing, not in this phase's diff. `tests/golden/` and `tests/fixtures/` stay excluded via `pyproject.toml`'s `extend-exclude` (Plan 121-01, D-18's collision-prevention edit) — confirmed present and unchanged |
| 9 | mypy watermark | `/tmp/venv311/bin/python tools/check_mypy_watermark.py` | `mypy errors: 1 (watermark: 35)` — 34 below | Unchanged from F-8 row 7 |
| 10 | `check_dispatch.py` | `python3 tools/check_dispatch.py` | **PASS** — 746 scanned, 736 supported, 10 non-dispatchable, 0 regressions, 0 consistency violations | Unchanged |
| 11 | `check_devtest_orchestrator.py` | `python3 tools/check_devtest_orchestrator.py` | **PASS** — scanned `chip_test.py`, `cli_handlers.py`, `submit.py`; 0 VPP-set, 0 raw-wire-dict, 0 `--force`; firmware untouched (host-only, asserted) | **Allow-list grew this phase** (Plan 121-09 added `_is_uv_eprom`/`_resolve_write_scope`; RESEARCH C-4's mandatory fix) — confirmed the gate still passes non-vacuously with the extended list |
| 12 | `check_sdp_capability_invariants.py` (**NEW this phase, GATE-01**) | `python3 tools/check_sdp_capability_invariants.py` | **PASS** — `0 permit-by-default, 0 widenable-allow-set`, `SDP_CAPABLE_TOKENS` bound exactly 1 time | New row — did not exist before Plan 121-03 |
| 13 | `check_no_community_support_status_write.py` | `python3 tools/check_no_community_support_status_write.py` | **PASS** — scanned `diagnostic_report.py`, `parse_devtest_issue.py`; 0 support_status writes | Unchanged (pre-existing gate) |
| 14 | `check_no_log_in_sdp_window.py` | `python3 tools/check_no_log_in_sdp_window.py` | **PASS** — resolved target `.../firestarter/src/proms/eeprom_28c.cpp`, emitter lines 298-314, poll lines 348-361 | Unchanged; resolved path confirmed to **exist** (both-directions rename check, §4) |
| 15 | `check_is_memory_cmd_no_ifdef.py` | `python3 tools/check_is_memory_cmd_no_ifdef.py` | **PASS** — resolved target `.../firestarter/include/firestarter.h`, predicate body lines 109-123, exactly 8 commands | Unchanged; resolved path confirmed to **exist** |
| 16 | `diff_db.py` identity | `python3 tools/diff_db.py` | **`PASS: all 2 changed chips explained (0 new chips confirmed; 0 chips removed from baseline)`** | **Identity here means "still exactly 2 explained `PGSZ_PAGE_SIZE` changes" — NOT zero.** The two changes are the pre-existing Phase 94 `W29C020,W29C020C,W29C022` / `W29C040,W29C042` page-size entries. A verifier expecting a zero-diff misreads this gate. |
| 17 | Catalog validity, both sub-repos | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` (run from both `firestarter/` and `firestarter_app/`) | **`OK: catalog valid (73 messages, version 1)`**, both exit 0 | Unchanged in message count; `0x5F`'s format string changed (D-15), version stayed 1 |
| 18 | Codegen drift, firmware header | regenerate `firestarter/include/messages.h`, `git diff --exit-code` | **NO DRIFT** | Confirms Plan 121-12's own finding: the C++ header carries only numeric id `#define`s, so the `0x5F` format-string edit is invisible there — zero reflow risk realised |
| 19 | Codegen drift, host module | regenerate `firestarter_app/firestarter/messages.py`, `git diff --exit-code` | **NO DRIFT** | Unchanged |
| 20 | Three-way catalog identity | `md5sum` on all three `messages.toml` copies | **Identical** — `8c9f79af841537310e2db197decc62b2` | Matches Plan 121-12's recorded md5 exactly |
| 21 | Remaining nine-row named pytest modules | `pytest tests/test_check_no_log_in_sdp_window.py tests/test_sdp_table_parity.py tests/test_check_is_memory_cmd_no_ifdef.py tests/test_sdp_bus_config_drift.py tests/test_revision_constants_parity.py tests/test_dispatch_mirror.py tests/test_check_devtest_orchestrator.py tests/test_check_sdp_capability.py` | **62 passed** in 1.89s | Includes GATE-01's new 9-leg module (`test_check_sdp_capability.py`, row 12's companion) |
| 22 | `gen_sdp_bus_config.py` | `python3 tools/gen_sdp_bus_config.py` | **`OK: wrote .../_shared/sdp_bus_config.h`**; `git -C firestarter status --porcelain` on that path empty afterward | Idempotent, no drift |
| 23 | Second audit-matrix regeneration (D-18/C-2) | see §3 | **Byte-identical to golden** (`cmp` exit 0, both 186034 bytes) | **Proven no-op**, per C-2's prediction (§3) |

**No row is marked from memory or from a prior plan's SUMMARY.** Every command above was executed
in this session; where a figure matched a prior SUMMARY's own claim, that match was itself
verified by re-running the command, not by reading the SUMMARY.

---

## 3. Golden and generated-artifact identity

**The coverage-matrix golden's one intentional refresh (Plan 121-01) and the proven no-op second
regeneration (this plan).** Plan 121-01 regenerated `tests/golden/v1.3-COVERAGE-MATRIX.md` as its
own first commit, alone, with zero DEVTEST code in the tree — closing a pre-existing 1403-byte
drift traced to Phase 98's pinout split (`362bfa0`), unrelated to this phase's own work (RESEARCH
C-2). This sweep re-ran the generator a **second** time against the same committed ledger
(`.planning/v1.3-defect-coverage-ids.json`) and diffed the output against the now-committed
golden:

```
$ python3 -c "from tools.audit_coverage_matrix import generate_matrix; \
    generate_matrix(output='/tmp/regen_matrix.md', ledger_path='.../.planning/v1.3-defect-coverage-ids.json')"
$ cmp /tmp/regen_matrix.md tests/golden/v1.3-COVERAGE-MATRIX.md && echo BYTE-IDENTICAL
BYTE-IDENTICAL
$ wc -c /tmp/regen_matrix.md tests/golden/v1.3-COVERAGE-MATRIX.md
186034 /tmp/regen_matrix.md
186034 tests/golden/v1.3-COVERAGE-MATRIX.md
$ git -C firestarter_app status --porcelain tests/golden/
(empty)
```

**This confirms RESEARCH C-2's prediction exactly**: `tools/audit_coverage_matrix.py` reads only
`chip_database.json` and the `.planning` ledger, and has no `dev test`/`OP_*`/`chip_test`
vocabulary at all — so this phase's `OP_WRITE_PARTIAL` addition, UV-axis redesign, and every other
DEVTEST change genuinely could not move the matrix, and did not. Had this second regeneration
produced a non-empty diff, the correct response would have been to **stop and investigate**, not
to silently regenerate the golden a second time — D-18's entire purpose is to make that scenario
visible rather than mask it. No such investigation was needed.

**The three-way catalog identity and both codegen drift gates** are recorded in full in §2 rows
17-20. **No firmware `.cpp` or `.h` file other than the generated `messages.h` was touched by this
phase** — confirmed by the phase-scoped firmware diff:

```
$ git -C firestarter diff --stat 0048b3d..HEAD
CLAUDE.md                   | 13 ++++++++++++-
README.md                   |  7 +++++++
doc/PROTOCOLS.md            |  4 ++--
tools/catalog/messages.toml |  8 +++++++-
4 files changed, 28 insertions(+), 4 deletions(-)
```

Three of those four are documentation (`CLAUDE.md`, `README.md`, `doc/PROTOCOLS.md` — GATE-02).
**The one non-doc file is `tools/catalog/messages.toml`** (D-15's catalog edit) — confirming
`121-12-SUMMARY.md`'s own framing: **this phase's firmware footprint is not docs-only**, but it is
narrower than 121-12's own must-have language predicted ("a generated firmware header changes").
Independently re-verified in this sweep (§2 row 18): `firestarter/include/messages.h` regenerates
to a **zero diff** — the C++ header carries only numeric id `#define`s; the changed format string
lives entirely in the host-side `messages.py` (§2 row 19, which does show the expected
one-field diff, already committed). The compiled firmware is therefore unchanged even though a
tracked firmware **source** file (the catalog mirror) is not byte-identical to phase base — the
catalog-sync CI red-until-milestone-merge expectation (§7) still holds on that basis alone.

---

## 4. The nine-row cross-repo gate table (from `119-NONREGRESSION.md` §CORRECTION-4)

Re-run and re-recorded at this phase's final commit, per Phases 120 and 121's mandatory
inheritance of this checklist. Row identifiers follow `119-NONREGRESSION.md`'s own numbering.

| # | Gate | Command | Verdict this sweep |
|---|---|---|---|
| 1 | `check_no_log_in_sdp_window.py` (HIGH-risk — firmware source scan) | `python3 tools/check_no_log_in_sdp_window.py` | **PASS**, resolved path `.../firestarter/src/proms/eeprom_28c.cpp` **confirmed to exist** (`ls -la` in this sweep). D-15's catalog edit does not touch this file — the emitter/poll line numbers (298-314/348-361) are unchanged. |
| 2 | `test_check_no_log_in_sdp_window.py` | (in §2 row 21's combined run) | **PASS** |
| 3 | `test_sdp_table_parity.py` (MEDIUM-risk) | (in §2 row 21's combined run) | **PASS** |
| 4 | `check_is_memory_cmd_no_ifdef.py` (firmware source scan) | `python3 tools/check_is_memory_cmd_no_ifdef.py` | **PASS**, resolved path `.../firestarter/include/firestarter.h` **confirmed to exist**, predicate body lines 109-123, exactly 8 commands |
| 5 | `gen_sdp_bus_config.py` (generator) | `python3 tools/gen_sdp_bus_config.py` | **PASS**, `git -C firestarter status --porcelain` on that path empty afterward — idempotent, no drift |
| 6 | `test_sdp_bus_config_drift.py` | (in §2 row 21's combined run) | **PASS** |
| 7 | `test_revision_constants_parity.py` | (in §2 row 21's combined run) | **PASS** — unchanged test count/shape this phase (no `CMD_*`/`FLAG_*` value added by Phase 121) |
| 8 | `test_dispatch_mirror.py` | (in §2 row 21's combined run) | **PASS** |
| 9 | `check_dispatch.py` + `check_devtest_orchestrator.py` | `python3 tools/check_dispatch.py` then `python3 tools/check_devtest_orchestrator.py` | **PASS** both — `check_dispatch.py` unchanged (746/736/10/0/0); `check_devtest_orchestrator.py`'s allow-list **grew** this phase (Plan 121-09's `_is_uv_eprom`/`_resolve_write_scope`) and the gate confirmed non-vacuous against the extended list |

**Cross-repo rename check, both directions, explicitly.** This phase touched firmware (D-15's
catalog edit, landing in Plan 121-12). For each host gate that scans firmware source text (rows
1 and 4 above), the resolved target path was confirmed to **exist** on disk in this sweep, not
merely assumed from the PASS line. **The reverse direction — a firmware-side gate scanning host
source text — does not exist as an architecture in this project**: a repo-wide grep of
`firestarter/tools/` for `firestarter_app` returns only prose comments in the catalog files
(`messages.toml`, `codegen_vectors.py`, `frame-vectors.toml`) documenting the sync-script
relationship, never a source-scanning gate. So the "both directions" obligation resolves to: the
one real direction (host-scans-firmware) is proven non-vacuous by path, and the other direction is
confirmed **not to exist** rather than silently assumed absent.

**Every row PASS.** No row was accepted on the strength of an earlier plan's SUMMARY alone — each
command above was re-run in this sweep, at the phase's final commit.

---

## Requirement Row Re-Verification (row by row, against the live tree)

Every one of the phase's nine requirement ids was independently re-checked against the live tree
in this sweep — not against any SUMMARY's own assertion. Each row below states the command or
assertion used.

| Requirement | Independent check performed this sweep | Result |
|---|---|---|
| **DEVTEST-01** | `derive_plan('AT28C256', db, write_scope='full')` — read the erase `Step`'s `supported`/`reason` fields directly; ran `pytest tests/test_chip_test.py -k devtest01` | `supported=False`, `reason` names `0x0D`/`28C family`, never `FLAG_CAN_ERASE`; 2/2 tests pass |
| **DEVTEST-02** | Read `inspect.signature(cli_handlers.dev_test.callback)`; invoked `dev test AT28C256 <flag>` via `CliRunner` for each of `--destructive`/`--output-dir`/`-y`/`--yes`/`--submit` | signature is `(app, chip)`; every flag → `No such option`, exit 2 |
| **DEVTEST-03** | Computed `is_uv_eprom` coverage against the live 746-entry `chip_database.json` via `EpromDatabase.get_eproms()` | 301/301 UV-EPROM entries covered; old `algorithm==0x0B` proxy covers only 32/301 (0 false positives either way) |
| **DEVTEST-04** | Read the live `_DESTRUCTIVE_OPS` frozenset; ran `pytest tests/test_dev_test_cmd.py -k TestUVOnlyStopAndAsk` | `OP_WRITE_PARTIAL` present in `_DESTRUCTIVE_OPS`; 4/4 branch legs (non-UV/UV-yes/UV-no/UV-off-TTY) pass |
| **DEVTEST-05** | Read `submit_report`'s live source for step ordering; ran `pytest tests/test_submit.py -k "dedup or argv or deny"` | Step 3 (dedup) confirmed unconditional and before Step 5 (ask) in source; 27/27 tests pass |
| **DEVTEST-06** | Ran `pytest tests/test_submit.py -k "negative or permission_gated or mutating"` | 16/16 deny-set legs pass (both `gh issue create` and `gh issue comment` paths, long and short flag forms) |
| **GATE-01** | Ran `tools/check_sdp_capability_invariants.py` against real source, then against each of the two planted-violation fixtures via `FIRESTARTER_SDP_CAPABILITY_SRC` | Real source: exit 0, PASS. Each planted fixture: exit 1, named violation reported |
| **GATE-02** | `grep -ci` for the required statements across all eight named docs in both sub-repos | No-erase statement present in all 4 firmware/protocol docs; always-writes statement present and "non-destructive" absent from all 3 tester-facing docs; `doc/lockable-proms.md` confirmed tracked |
| **GATE-03** | The full sweep in §2/§4 above | Green at every row, both interpreters, both ruff/format checks recorded with version, `diff_db.py` identity confirmed as "2, not 0" |

**All nine rows verify.** None required a report of a non-holding claim.

---

## 5. Corrections recorded, not acted on in `REQUIREMENTS.md`

Per the established response this milestone has used since LOCK-04/LOCK-06/HOST-04 (Phase 119/120):
**satisfy the intent, record the correction in phase artifacts, do not edit `REQUIREMENTS.md`'s
own wording.** Every correction `121-RESEARCH.md` recorded, restated here for a reader who does
not open that file:

| # | Stated | Verified reality | What the phase did instead |
|---|---|---|---|
| C-1 | D-06: `diagnostic_report.py`'s renderer and `to_dict` are "owned task work" for the new op string | The renderer/`to_dict` are fully op-string-agnostic — no `OP_*` import, no literal op string anywhere; `_step_dict` passes `result.op` straight through | **Zero edits** to `diagnostic_report.py`'s renderer; only the optional `SCHEMA_VERSION` bump landed (Plan 121-07) |
| C-2 | D-06/D-18: the audit-matrix golden is part of D-06's ripple; "this phase genuinely changes the matrix" | `tools/audit_coverage_matrix.py` has zero `chip_test`/`OP_*`/`dev test` references; the pre-existing drift was a Phase-98 pinout split, unrelated to this phase | D-18's regen-first-and-alone ordering stood; the **second** regeneration (this plan) was proven byte-identical (§3) — confirming the matrix genuinely did not move this phase |
| C-3 | D-05: "82 references across 6 test files" need reworking for the flag removal | The `dev test`-scoped ripple is 25 literal references, 23 in one file (`test_dev_test_cmd.py`); the other 46+ belong to four **other** `dev` sub-commands' identically-named `--output-dir`/`-y` and must not be touched | Plan 121-09 touched only `test_dev_test_cmd.py` (26 tests after rework, was 23); the four sibling `dev` command test modules confirmed untouched and green |
| C-4 | D-05: `check_devtest_orchestrator.py` "fails closed when its scoped scan matches zero functions" would trip on the flag removal | The gate filters on function **names**, not options — removing `@click.option` decorators does not rename `dev_test`; the real hazard is the **inverse** (a violation in a new, unlisted helper passes vacuously, proven live in RESEARCH) | Plan 121-09 extended `_HANDLER_FUNCTION_NAMES` with `_is_uv_eprom`/`_resolve_write_scope` and added a permanent completeness pytest so no name can dangle again — this sweep's §2 row 11 re-confirms the gate non-vacuous against the grown list |
| C-5 | D-06: "the `chip_test.py` frozensets `_DESTRUCTIVE_OPS` and `_MULTI_RUN_OPS`" are both owned task work | `_DESTRUCTIVE_OPS` is live (the chip-ID safety gate); `_MULTI_RUN_OPS` had **zero** references anywhere in the tree at research time | **Deliberate deviation from the research recommendation** (documented in `STATE.md`): rather than stating `_MULTI_RUN_OPS` dead in-source, Plan 121-06 made it **live** as the fail-closed dispatch allow-list (`_dispatch_multi_run`'s Pitfall-1a guard reads it), so both frozensets are now safety-critical, not one live and one cosmetic |
| C-6 | `<specifics>`: `count_applicable`'s N-of-M banner "never fires again" once every run writes | The banner row renders unconditionally and `n_ran` excludes NA/SKIPPED, so it still carries signal whenever the chip-ID gate closes | `locked_destructive` was **kept**, not deleted — `derive_plan`'s `write_scope` parameter is genuinely three-valued (`"none"`/`"partial"`/`"full"`) at the API level (Plan 121-05's deliberate choice, per `STATE.md`), even though the live `dev_test` handler never invokes it with `"none"` under D-04's always-writes contract. This makes 121-05 a pure refactor rather than a narrowing, and keeps the banner's own machinery live for any future caller that does pass `"none"` |
| C-7 | D-15: "edit only `messages.toml`, then regenerate" | There are three byte-identical `messages.toml` copies; `tools/catalog/sync_to_subrepos.sh` is the one command that copies the meta catalog to both sub-repos **and** regenerates both codegen artifacts | Plan 121-12 edited the **meta** copy only, then ran `sync_to_subrepos.sh` — never hand-copied or hand-normalised any generated file. Re-confirmed in this sweep (§2 rows 17-20) |
| C-8 | D-13 (as originally worded): "`--skip-erase` and `-b` on a `0x0D` chip warn and proceed" | `-b`/`--no-blank-check` has skipped only the blank check since Phase 92's decouple — it no longer implies skip-erase, and is genuinely useful on `0x0D` (required for a non-blank AT28C, since there is no erase to make it blank) | The **warn** landed on `--skip-erase` only (Plan 121-10); `-b`'s `0x0D` treatment became a **documentation** statement (GATE-02, Plan 121-13), not a runtime warning — a factually-wrong warning on `-b` was avoided |
| C-9 | `REQUIREMENTS.md:88` cites SAFE-01's lock at `cli_handlers.py:1758-1760` | Line-number drift only — the actual anchors moved to `:1838-1846` (declaration) / `:1880` (`dev_test` def) by the time plans executed | Plans used the live anchors, not the cited ones; no requirement wording was edited for a line-number drift |
| D-06 (own correction) | ROADMAP framing: the closed six/seven-string op vocabulary is "consumed by the issue parser" | `tools/parse_devtest_issue.py` has **no op vocabulary at all** — it keys on the `[dev test]` title marker, `schema_version` presence, and `dedup_fingerprint` grouping; it never reads step ops or verdicts | Recorded as a correction to the ROADMAP's own framing (D-06); `REQUIREMENTS.md` and `ROADMAP.md` text left unedited per the established response |
| D-17 (own correction) | GATE-02's requirement text names five docs + both READMEs | D-04's always-writes reality most affects two docs GATE-02's literal text never named: `doc/community-validation.md` and `doc/beta-testing-install.md` | Plan 121-13 corrected both anyway (the named-list **widening**), recorded the correction in the traceability sentence, and left `REQUIREMENTS.md`'s own GATE-02 wording unedited |

**Established response restated explicitly, so no future reader misreads any of the above as an
open gap:** satisfy the intent, record the correction, do not edit `REQUIREMENTS.md`'s stated
mechanism. Every row above was intent-satisfied; none is an open item.

---

## 6. The three recorded reversals

This phase carries **three** reversals, each named as a reversal per the established
`119-NONREGRESSION.md`/`120-NONREGRESSION.md` discipline (a policy reversal is recorded as a
reversal, with its constraints named, never silently absorbed):

1. **The `dev test` redesign itself.** Operator directive 2026-07-29 (Phase 120 D-20 amendment,
   folded into Phase 121) reverses **three** locked decisions:
   - Phase 112 Plan 04's deliberate removal of all interactive prompts from `dev test`
     (`112-UAT.md`) — this phase reintroduces exactly one prompt, the UV-only stop-and-ask
     (DEVTEST-04).
   - SAFE-01's lock that `--destructive` is CLI-only and never read from config/environment
     (`cli_handlers.py:1758-1760`, now `:1838-1846`) — this phase removes the flag entirely
     (DEVTEST-02), so the lock's own subject no longer exists.
   - SAFE-03's statement that interactive input was reduced to "only" the confirm prompt — this
     phase adds a second interactive point (the filing ask, DEVTEST-05) and reframes destructive
     confirmation around the UV axis rather than a blanket `--destructive` gate.
   Constraint carried: the reversal does not re-open Phase 109's original destructiveness-gate
   *safety* concern — it re-scopes the gate from "all writable parts" to "UV-erasable parts only"
   (DEVTEST-03), a narrower and more precise axis than the one SAFE-01 originally locked around.

2. **The erase-capability note in the database transform (D-12).** `database.py:591` (now
   rewritten) previously carried an explicit note that leaving `FLAG_CAN_ERASE` set on protocol
   `0x0D` was firmware-inert and "must stay unchanged" (a Phase 121 D-03-era note, itself
   predating this phase). D-12 reverses that **policy**, not the underlying **fact**: the `0x0D`
   firmware path genuinely never reads the flag — that half of the old note remains true — but an
   inert-but-false capability advertisement is still false, and DEVTEST-01 needed the host to stop
   making it. The rewritten comment block (quoted in full in `121-08-SUMMARY.md`) states this
   explicitly as a reversal, names the blast radius re-verification performed before landing it,
   and names the one benign behavioural delta (`firestarter erase` on `0x0D` now refused one layer
   earlier, same wire id).

3. **v1.21's submission contract (SUB-01/SUB-02).** `.planning/milestones/v1.21-REQUIREMENTS.md`
   locks `--submit` as *"explicit + interactive-only; never on a bare run."* DEVTEST-05
   contradicts that outright: every `dev test` run now asks whether to file an issue, with no
   flag required. The v1.21 archive's own SUB-01/SUB-02 wording was **not edited** — Phase 120's
   D-20 amendment recorded the reversal as a new entry in the "Deferred by operator decision"
   section of the live `REQUIREMENTS.md` (line 114), and this plan's independent re-verification
   (DEVTEST-05's row above) confirms the reversal is fully landed: `submit_report` is reached
   unconditionally, with no `--submit` flag surviving to gate it (DEVTEST-02 removed it).

Each reversal's constraint (what does NOT change alongside the reversed policy) is named above so
a future reader does not treat the reversal as unbounded.

---

## 7. Known and explained conditions — never silent

**1. The meta `.github/workflows/catalog-sync-check.yml` remains expected-red-until-milestone-merge.**
Unchanged cause, re-confirmed in this sweep: it checks out both `firestarter` and `firestarter_app`
at `ref: main` (lines 33/40), and v1.22 has not merged to `main` in either sub-repo. Not this
phase's damage — the Phase 118/119/120 pattern continues. **This phase's real firmware footprint
is narrower than that CI gate's failure would suggest**: the only tracked firmware file this phase
changed outside documentation is `tools/catalog/messages.toml` (§3), and the compiled
`messages.h` is byte-identical to phase base.

**2. A py3.9 pytest run is structurally impossible, reproduced live in this sweep.** `[test]`
requires `syrupy>=5.0`, and every `syrupy>=5.0` release requires Python ≥3.10 (the one
`2026.4.6...` release that would satisfy `>=5.0` on 3.9 is yanked). Provisioning a real Python
3.9.25 via `uv` and attempting `uv pip install -e '.[test]'` against it fails to resolve, with `uv`
naming the exact conflict:

```
$ uv venv --python 3.9 /tmp/venv39 && uv pip install --python /tmp/venv39/bin/python -e '.[test]'
...
And because firestarter[test]==3.0.0b11 depends on syrupy>=5.0, we can conclude that
firestarter[test]==3.0.0b11 cannot be used.
...your requirements are unsatisfiable.
```

**Two consequences follow, both recorded rather than smoothed over:** (a) the milestone's py3.9
support claim rests entirely on **config-pinned** tooling — `ruff`'s `target-version = "py39"` and
`mypy`'s `python_version = "3.9"` — plus the `requires-python = ">=3.9"` packaging classifier, not
on any executed test run; (b) **ruff at the `py39` target does not diagnose 3.10-only syntax** (a
probe file containing a `match` statement and a bare `int | None` runtime annotation produces only
style diagnostics, no version error, per `121-RESEARCH.md`'s own probe) — so ruff's presence is not
itself a py3.9 compatibility gate, only a style-linter running under a pinned target.

**3. The GitHub issue-search index's eventual consistency limits `find_prior_report`'s dedup
check, by design, not by oversight.** A `dev test` filed seconds earlier may not yet be returnable
by `gh issue list --search`. `find_prior_report`'s own docstring records this (Plan 121-11), and
the ask is worded "you appear to have already reported this" — hedged, never a certainty. This is
not engineered around because `count_agreeing` groups by `dedup_fingerprint` on arrival, so a
duplicate still lands **visibly grouped** rather than silently lost — the limitation is bounded by
that downstream grouping, not eliminated.

**4. Assumption A1 (comment-permission for `gh issue comment`) is non-load-bearing by design.**
DEVTEST-06/D-11's `comment_via_gh` assumes a public repo needs only an authenticated `gh` account,
never write access, to comment — true for `henols/firestarter_prom` today. The phase did **not**
add a human-verify checkpoint for this assumption (a deliberate choice, named in `STATE.md`'s
"three deliberate deviations"): if the assumption is ever wrong, `comment_via_gh` degrades exactly
like `submit_via_gh` — a failed `gh` call falls back to the browser tier pointed at the existing
issue (`test_duplicate_comment_fails_falls_back_to_browser_on_existing_issue`, Plan 121-11). The
assumption's truth value is therefore irrelevant to correctness; a checkpoint would have added
process cost for no safety gain.

**5. D-03's owned trade-off: an off-TTY `dev test` run writes to silicon without anyone
consenting.** An absent TTY is treated as a **declined prompt**, not absent consent — so a piped
or CI run still writes the UV-only 256-byte partial region (never the full device; the region
width is a module constant, `_UV_WRITE_REGION_LENGTH`, never DB-sourced — SC4). This was put to
the operator explicitly as a real cost (today's off-TTY default writes nothing at all) and chosen
anyway, because the milestone's own purpose is community write-evidence and a silent-no-write
off-TTY default would defeat that purpose. The consequence is bounded to a small, fixed region and
mitigated only by the unconditional, first-printed always-writes notice (DEVTEST-04's own
mechanism) and by the docs (GATE-02) — there is no runtime confirmation gate for the off-TTY case,
by design, and this document does not pretend otherwise.

---

## 8. Deliberately not taken

Recorded here so the next owner finds these as explicit decisions, not inherited silence:

**1. Deleting the advisory `Plan.locked_destructive` field and its N-of-M banner.** Declined.
Under D-04's always-writes contract, `dev_test`'s own handler never populates
`locked_destructive` (it is always empty in that command's live path) — but `derive_plan`'s
`write_scope` parameter is genuinely three-valued at the API level (`"none"`/`"partial"`/`"full"`,
Plan 121-05), and `count_applicable`'s banner logic still reads `locked_destructive` correctly for
any future caller that does pass `"none"`. Deleting the field would have required deleting or
reworking that generic machinery for a narrowing this phase does not need; kept intact instead.

**2. Deleting `_MULTI_RUN_OPS` as dead code.** RESEARCH found it had zero references at research
time and recommended stating it dead in-source. **Declined** — Plan 121-06 instead made it
**live**, repurposing it as the fail-closed dispatch allow-list `_dispatch_multi_run` checks before
falling through to any op arm (Pitfall 1a's mitigation). This is a deliberate deviation from the
research recommendation, recorded in `STATE.md`, and it makes both `_DESTRUCTIVE_OPS` and
`_MULTI_RUN_OPS` safety-critical rather than one live and one cosmetic.

**3. Pinning the ruff version instead of excluding the golden directory.** RESEARCH's Pitfall 2
named two fixes for the `ruff format`-vs-golden collision: pin `ruff==0.15.*` in `[test]`
(freezing lint hygiene project-wide), or `extend-exclude = ["tests/golden", "tests/fixtures"]`.
Plan 121-01 chose the exclude — narrower, does not freeze the whole project's tooling to an old
ruff release. **Note recorded in this sweep:** the devcontainer's own globally-installed `ruff`
has since drifted to 0.16.0 (matching the CI-resolved version), so Pitfall 2's original
divergence is no longer reproducible here — but the `extend-exclude` fix remains correct and in
place regardless of whether the divergence currently reproduces.

**4. Adding a partner `OP_VERIFY_PARTIAL` op string (D-07).** Declined — a verify's region is
definitionally the preceding write's region; it never has independent scope, so a distinct string
would encode zero new information. The vocabulary stops at seven strings
(`id`/`read`/`blank-check`/`write`/`verify`/`erase`/`write-partial`).

**5. Adding a `--read-only` mode (D-04).** Declined — would cost a flag DEVTEST-02 removes, and
would partially walk back the "zero options" contract. If community feedback later shows testers
want a safe first-contact sweep, it wants its own phase and its own flag-surface decision — not
folded in here.

**6. A provenance/uncertainty header on `doc/lockable-proms.md` (D-16).** Declined. The document
ships ~300 rows compiled from third-party datasheets with no statement of its evidentiary basis,
in the exact milestone whose validation ceiling forbids claims about SDP behaviour on real
silicon. This is an **owned trade-off**, put to the operator explicitly and chosen anyway — the
first 10 lines of the file are confirmed byte-identical to the pre-commit working tree (no header
was added), recorded here so no downstream agent re-opens it.

---

## Validation-Ceiling Review

Every sentence in this document was read against `.planning/REQUIREMENTS.md`'s Validation Ceiling
section before this plan's final commit. The review's outcome:

- **Zero affirmative claims that SDP, or the `0x0D` erase model, has been demonstrated on real
  AT28C silicon appear anywhere in this document.** Every claim above has a software artifact as
  its subject — a git blob/md5 identity, a `pio run` size report, a pytest exit code, a source-read
  confirmation, a `cmp` byte comparison — never a silicon observation.
- **No AT28C part was on the bench during this phase.** This sweep performed zero hardware
  operations; every command in §2/§4 ran against native/host test doubles or static source
  analysis. The three attached devices (`/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0`) were used
  only for `pio run`'s build step (no upload, no serial I/O).
- **`0x0D` stays `UNVERIFIED`.** Nothing in this phase's changes — the catalog string (D-15), the
  `FLAG_CAN_ERASE` clear (D-12), the `dev test` redesign, or GATE-01's AST gate — touches or claims
  to touch the `PROTOCOL-LEDGER`'s `0x0D` entry.
- **Zero chips changed `support_status`.** Confirmed by this sweep's own `diff_db.py` identity
  check (§2 row 16): the only two changed chips are the pre-existing Phase-94 `PGSZ_PAGE_SIZE`
  entries, neither a `support_status` change.
- **The 84-chip count is unchanged.** No entry was added to or removed from the `0x0D` bucket by
  this phase; `check_dispatch.py`'s re-run (§2 row 10) confirms the same 746-scanned / 736-supported
  / 10-non-dispatchable figures as every prior phase's sweep.

This document sits entirely on the permitted side of the ceiling. The permitted closing claim
(*"The SDP lock and unlock sequences are emitted exactly as specified, verified byte-exact by
golden register trace across all four `0x0D` pinouts, with a documented and measured host-side
timing assumption"*) is unaffected and unextended by anything in this phase; the forbidden claim
(*"SDP lock/unlock works on an AT28C256"*) appears nowhere in this document, in any form.

---

## Sweep Summary

| Gate | Result |
|---|---|
| Native (`native`) | 141/141, 17 suites |
| Native (`native_nodevtools`) | 141/141 — identical |
| AVR builds (`pio run`) | 3/3 SUCCESS, unchanged from Phase 119's final measurement |
| Host pytest, devcontainer (3.12.13) | 1134 passed, 0 failed |
| Host pytest, CI-parity venv (3.11.15) | 1134 passed, 0 failed — identical |
| Coverage | 81.86% (floor 70%) |
| `ruff check` / `format --check` (0.16.0, CI-resolved) | 4 pre-existing findings, 0 in this phase's diff |
| mypy watermark | 1 error (watermark 35, 34 below) |
| `check_dispatch.py` | PASS, 0 regressions |
| `check_devtest_orchestrator.py` | PASS, allow-list extended and confirmed non-vacuous |
| `check_sdp_capability_invariants.py` (NEW, GATE-01) | PASS on real source; FAILS correctly on both planted classes |
| `diff_db.py` | PASS — 2 explained changes, 0 new, 0 removed (identity ≠ zero) |
| Catalog three-way identity + both codegen drift gates | Clean, md5 `8c9f79af841537310e2db197decc62b2` |
| Second audit-matrix regeneration | Byte-identical to golden — proven no-op |
| Both sub-repo working trees | Clean by `git status --porcelain` (only named pre-existing dirt); tips `firestarter@48c36e5`, `firestarter_app@c3c9424` |
| py3.9 pytest | Structurally impossible (reproduced live); py3.9 claim rests on config-pinned ruff/mypy + classifier |

**All nine requirement rows re-verified against the live tree. `GATE-03`, `DEVTEST-01`,
`DEVTEST-02`, `DEVTEST-03`, `DEVTEST-04` and `GATE-01` ticked by this plan. `DEVTEST-05`,
`DEVTEST-06` and `GATE-02` (already Complete) left byte-intact. `CLOSE-01`/`02`/`03` remain
unticked — Phase 122's own scope.**
