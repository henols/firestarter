# Phase 121: `dev test` FIX + GATES + DOCS + REDESIGN — Research

**Researched:** 2026-07-29
**Domain:** Python host-CLI refactor of a closed op vocabulary + safety-gate design + cross-repo doc/codegen non-regression
**Confidence:** HIGH (every load-bearing claim below was executed against the live milestone-branch tree in this session)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Copied verbatim from `121-CONTEXT.md` `<decisions>`. **The planner MUST honor these; this research does not re-open any of them.** Where research found a stated *mechanism* narrower or wider than reality, the correction is recorded in `## Corrections to CONTEXT.md / ROADMAP Framings` below and the decision's *intent* is preserved — the established project response (LOCK-04, LOCK-06, HOST-04, D-06, D-17).

- **D-01: The stop-and-ask is UV-only; every other family is written in full, unprompted.**
  `dev test at28c256` — this milestone's own family — writes the whole part with no prompt. Rejected: asking on every writable part. Rejected: the literal reading in which non-UV parts are never written.
- **D-02: UV-ness is decided once in `derive_plan` and carried on the `Plan`/`Step`.** `run_plan` and `_write_region_for` **read** that decision and never re-derive UV-ness. Rejected: widening the execution-time set to `{0x07, 0x08, 0x0B}`. **Rejected on a hard constraint:** putting `electrical-type`/`is_uv` into `convert_to_programmer` (`_setup_operation` does `command_dict = eprom_data_dict.copy()`). Rejected: threading the raw `electrical-type` string as a separate argument.
- **D-03: Off-TTY defaults to "no" — the 256 B window is written.** An absent TTY is treated as a declined prompt rather than absent consent. Rejected: marking write/verify `SKIPPED`. Rejected: refusing the whole command off-TTY.
- **D-04: `dev test` always writes, and the docs must say so loudly.** v1.21's *"non-destructive by default"* premise is **gone entirely**; no read-only mode survives. Help text, the **first line of output**, `doc/community-validation.md`, `doc/beta-testing-install.md` and both READMEs must state plainly that `dev test` writes. Rejected: a `--read-only` flag. Rejected: a three-way full/partial/none ask.
- **D-05: All four current options are removed; `dev test <chip>` takes zero options.** `--destructive`, `-y/--yes`, `--submit`, `--output-dir`. Rejected: keeping `--output-dir`. Rejected: keeping `--submit`.
- **D-06: A seventh op string `OP_WRITE_PARTIAL` joins the vocabulary.** Rejected: six strings + a `scope` field. Rejected: encoding scope only in the free-text `reason`.
- **D-07: `verify` stays a single string.** The vocabulary stops at seven. Rejected: adding `verify-partial`.
- **D-08: A partial run still auto-tags `ladder_state = community-reported`.** `count_agreeing` groups by `dedup_fingerprint`, and D-06 changes that hash, so a partial run can **never** cross-agree with a full run toward N≥2. Rejected: refusing the tag. Rejected: a distinct `community-reported-partial` tag.
- **D-09: Dedup is a `gh` query on the fingerprint, authored by `@me`.** `gh issue list --repo henols/firestarter_prom --author @me --search <shorthash> --state all`. **No local ledger.** Rejected: a config-dir fingerprint ledger. Rejected: both sources.
- **D-10: When the query cannot run, ask anyway and say so plainly.** Rejected: defaulting the prompt to "no". Rejected: skipping the ask entirely without `gh`.
- **D-11: On a duplicate, name the issue and offer to comment this run's evidence.** The negative-argv discipline extends to `gh issue comment`. Rejected: naming the issue and filing nothing. Rejected: offering a new issue anyway.
- **D-12: `FLAG_CAN_ERASE` is cleared for algorithm `0x0D` in `convert_to_programmer`.** Reverses `database.py:591`'s *"must stay unchanged"* note. Rejected: a scoped `0x0D` arm in `derive_plan` plus a separate flag-surface fix. Rejected: the scoped arm alone.
- **D-13: `--skip-erase` and `-b` on a `0x0D` chip warn and proceed.** The exact shape of HOST-02's D-18. Rejected: refusing the flag. Rejected: documentation only.
- **D-14: One AST checker denies two violation classes, with a planted fixture per class.** Class 1 — permit-by-default; Class 2 — a widenable allow-set. The existing AST import-purity leg at `tests/test_sdp_capability.py:640` stays. Rejected: either class alone.
- **D-15: `tools/catalog/messages.toml`'s `0x5F` caveat is fixed here, with both mirrors regenerated.** Edit **only** `messages.toml`, then regenerate. Rejected: deferring to Phase 122. Rejected: leaving it to Phase 120 D-10's host line alone.
- **D-16: `firestarter_app/doc/lockable-proms.md` is committed as-is with §17 fixed, no provenance header.** An **owned trade-off**. Rejected: relocating to `.planning/notes/`. Rejected: a provenance header.
- **D-17: GATE-02's named doc list is widened, and `REQUIREMENTS.md` is not edited.** Added: `doc/community-validation.md`, `doc/beta-testing-install.md`.
- **D-18: The stale audit-matrix golden is regenerated FIRST, as its own commit.** Commit 1 regenerates the pre-existing drift **alone**, with zero DEVTEST code in the tree. Rejected: one combined regen at the end. Rejected: a named GATE-03 exception.
- **D-19: The no-programmer-found characterization tests are hardened to pass with a board attached.** Patch the real port-enumeration seam. **Operator-authorised scope addition.** Rejected: proving green with no board attached.

### Claude's Discretion

- **Every user-facing string.** Two constraints: the always-writes notice must be **unconditional and first**, and D-12's `NA` erase reason must name the **family fact** (*"protocol 0x0D — the 28C family has no erase operation"*), never the flag mechanism.
- **Bump the report's `schema_version`.**
- **Keep `dev test`'s `0/1/2` exit-code tri-state unchanged.**
- **How D-02's decision is carried** — a field on `Plan`, a field on `Step`, or both.
- **Where the two planted fixtures live and how the checker is pointed at them.**
- **Whether the b11 back-compat in D-06 is a tolerant parser or an explicit legacy-vocabulary constant.**
- **Plan ordering**, subject to four hard constraints: D-18's golden regen is the **first** commit; D-06's op string must precede the renderer/`to_dict`/golden work that consumes it; D-02's plan-side decision must precede the execution-layer read; and D-15's `messages.toml` edit must precede both mirror regenerations.

### Deferred Ideas (OUT OF SCOPE)

- `dev test`'s release-channel disposition (999.15 / gh#8) — recorded, **not acted on**.
- A read-only `dev test` mode — its own phase.
- Hardening/removing `derive_plan`'s vestigial `locked_destructive` — a separate cleanup if this phase only states it dead in-source.
- The wider CLI flag re-design (`-f/--force`'s two meanings, `-b`'s opposite polarity, a project-wide `-y` idiom).
- The end-to-end `infoic.xml` `page_size` decode phase (not yet in ROADMAP.md).
- Widening `_probe_port`'s `[\d.x]+` version capture.
- Widening the trace recorder to a third strobe kind.
- `DIP24_2816`'s missing `static-high-pins` (SDP-F8); datasheet verification of the SDP magic addresses (SDP-F7).
- Unity-teardown SIGABRT root cause; recording every side-effecting `rurp_*` call; all-84-chips table-driven trace coverage.
- `prove-pio-dev-flag-fails-closed.md` items 1-3.
- `decode-infoic-flags-bits-14-15-protect-metadata.md` (requires a DB regeneration — forbidden this milestone).
- `fold-response-code-into-log-macro.md`.
- **Any `chip_database.json` change, any `support_status` change, any `PROTOCOL-LEDGER` entry, any `build_db.py` change.**
- **Re-opening the SDP-capability partition itself (43 ALLOW / 41 REFUSE).** GATE-01 **guards** it; it does not revisit it.
- Phase 122's closeout comments, the honesty ledger, the `beta`-push decision, the version bump.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description (from `REQUIREMENTS.md`) | Research Support |
|----|--------------------------------------|------------------|
| **DEVTEST-01** | `OP_ERASE` marked `NA` for protocol `0x0D` with a named reason (host half; firmware half landed in Phase 119) | §F-1 (D-12 is the root-cause fix and its full blast radius is measured: exactly 2 host tests invert, 0 firmware tests, 0 DB/`diff_db` impact); §F-2 (the `derive_plan` NA branch that fires for free); Pitfall 9 (the reason string must name the family fact) |
| **DEVTEST-02** | `dev test` takes **no flags** | §F-9 — exact, *scoped* blast radius: 20 of 23 test methods in `test_dev_test_cmd.py`; 4 other `dev` sub-commands own an unrelated `--output-dir` and `dev sdp` owns an unrelated `-y` — **these must not be touched**. Pitfall 6 corrects CONTEXT's claim that `check_devtest_orchestrator.py` will trip |
| **DEVTEST-03** | Destructiveness scoped to UV-erasable EPROMs on an explicit structural axis | §F-3 — all three candidate axes counted against the live DB (32/301 vs 329 incl. 28 non-UV vs 301/301); D-02's axis is the only exact one; the 28 over-included parts are enumerated by name |
| **DEVTEST-04** | Stop-and-ask; yes → full device, no → a small part (a third mode needing a new representation) | §F-4 — the minimal representation change is a 1-line signature widening (`_dispatch_multi_run` currently discards the `Step`); `_write_region_for`'s 256 B top-anchored window already exists. **Pitfall 1** is the dominant risk: an unhandled 7th op string calls `erase_eprom` and reports `OK` (proven empirically) |
| **DEVTEST-05** | Every run asks whether to file; dedup check runs first | §F-5 — the D-09 argv was executed live against the real tracker and returned the real matching issue; the no-match/failure signals are distinguished; the search-index lag trap is named |
| **DEVTEST-06** | `gh`-first submission; assert the **negative** argv for `gh issue create --label` | §F-5, §F-6 — the existing negative-argv idiom asserts only the long form; `gh issue create` also accepts `-l`, `-a`, `-m`, `-p`, all write/triage-gated. `gh issue comment` has **no** label flag at all — the meaningful negatives there are `--delete-last`/`--edit-last`/`--yes`/`--web`/`--editor` |
| **GATE-01** | AST capability gate + planted-violation pytest proving it fails | §F-6 — the in-tree precedent's exact shape, its two fixture-injection seams, and a **proven** coverage hole (a violation in an unlisted helper passes silently, EXIT=0) |
| **GATE-02** | Docs corrected where they describe behaviour that does not reach silicon | §F-7 — all 8 targets verified present, tracked status confirmed, and the specific stale lines located |
| **GATE-03** | Full non-regression set green | §F-8 — every command executed with its exact baseline; **two live CI-vs-devcontainer divergences found**, one of which (Pitfall 2) directly collides with D-18's golden regen |
</phase_requirements>

---

## Summary

This phase is not a feature addition; it is a **contract inversion** on a command whose entire v1.21 architecture was built to make a destructive operation structurally unreachable. `derive_plan` omits write/erase/verify from `Plan.steps` when `destructive=False` and records them on an advisory `Plan.locked_destructive` list whose docstring forbids `run_plan` from iterating it. D-04 deletes the reason that architecture existed: every run now writes. The engineering work is therefore mostly *subtraction plus one careful addition* — remove four CLI options, remove the non-destructive branch's reason to exist, add a seventh op string and a UV consent gate, and prove nothing silently fell through.

Three of this phase's stated mechanisms are narrower or wider than reality, and **all three shrink the work** — continuing the exact pattern CONTEXT.md `<specifics>` already identified for LOCK-04/LOCK-06/HOST-04. `diagnostic_report.py`'s renderer and `to_dict` are fully op-string-agnostic (verified: `_step_dict` passes `result.op` through; `render` iterates `d["steps"]` generically), so D-06 needs **zero** edits there. `tools/audit_coverage_matrix.py` reads only `chip_database.json` plus a `.planning` ledger and has no op vocabulary, so **this phase does not change the coverage matrix at all** — the golden regen (D-18) is a pure refresh of a pre-existing DB-driven drift introduced at Phase 98's `362bfa0`, and the second regen at phase end is expected to be a no-op. And the "82 references across 6 test files" figure is an over-count that conflates four *other* `dev` sub-commands' identically-named `--output-dir`; the true, scoped figure is **20 of 23 test methods in one file**.

Against that shrinkage stand two risks the phase artifacts do not yet name, both verified empirically in this session. **First:** adding `OP_WRITE_PARTIAL = "write-partial"` without an explicit `_dispatch_multi_run` branch makes the step call `operator.erase_eprom()` twice and report `OK` — the host mirror of exactly the phantom-success class Phase 119 fixed in firmware, reproduced here in a single tool call. And if the new op is not added to the *live* `_DESTRUCTIVE_OPS` frozenset, a chip-ID mismatch will no longer gate the partial write. **Second:** `ruff format --check` is green in this devcontainer (ruff 0.15.20) and **RED under the version CI resolves** (ruff 0.16.0, from the unpinned `ruff>=0.15.14`), and the one file it wants to reformat is `tests/golden/v1.3-COVERAGE-MATRIX.md` — the very golden D-18 regenerates, whose byte-identity is asserted by `test_golden_file_matches`. Running `ruff format` (not `--check`) during this phase corrupts the golden and turns two gates against each other. The devcontainer-masks-CI memory is real, but its mechanism is the **unpinned ruff version**, not the Python version: ruff and mypy are config-pinned to `py39` and behave identically on any interpreter, and a py3.9 pytest run is **structurally impossible** because `syrupy>=5.0` requires Python ≥3.10.

**Primary recommendation:** Sequence the phase as (1) golden regen alone, (2) a fail-closed `_dispatch_step`/`_dispatch_multi_run` guard *before* the 7th op string exists, (3) D-02's plan-side UV decision + `Step`-carried region, (4) `OP_WRITE_PARTIAL` + `_DESTRUCTIVE_OPS`, (5) D-12 + its two test inversions, (6) D-05's option removal + gate allow-list extension, (7) submission/dedup, (8) GATE-01's checker + fixtures, (9) D-15 catalog via `tools/catalog/sync_to_subrepos.sh`, (10) docs, (11) the nine-row sweep run under a `uv`-provisioned Python 3.11 with CI-resolved ruff. Resolve the `tests/golden` ruff-format collision with `extend-exclude = ["tests/golden"]` before any `ruff format` runs.

---

## Corrections to CONTEXT.md / ROADMAP Framings

Each verified live in this session. Per the established pattern (LOCK-04, LOCK-06, HOST-04, D-06, D-17): **satisfy the intent, record the correction in phase artifacts, do NOT edit `REQUIREMENTS.md`.**

| # | Stated | Verified reality | Effect on work |
|---|--------|------------------|----------------|
| C-1 | D-06: *"owned task work: … `diagnostic_report.py`'s renderer and `to_dict`"* | `diagnostic_report.py` imports only `BannerCounts, Plan, StepResult` (`:49`) — **no `OP_*` import, no literal op string anywhere**. `_step_dict` (`:382-391`) passes `result.op` straight through; `render` (`:453-458`) iterates `d["steps"]` generically. `[VERIFIED: grep + read]` | **Shrinks.** Zero `diagnostic_report.py` edits needed for the new op string. Only the optional `SCHEMA_VERSION` bump (`:55`, currently `"1.1"`). |
| C-2 | D-06 / D-18: the `tests/test_audit_coverage_matrix.py` golden is part of D-06's ripple; D-18: *"this phase genuinely changes the matrix"* | `tools/audit_coverage_matrix.py` reads only `chip_database.json` + `.planning/v1.3-defect-coverage-ids.json`; it has **zero** `chip_test`/`diagnostic_report`/`OP_`/`dev test` references (its `"id"` keys are `BENCH-NN` requirement ids). Its `EpromDatabase` import is `# noqa: F401`, unused. The live drift is a **pinout split**: golden shows `DIP32_STD 127`, produced shows `DIP32_27C020 88` + `DIP32_STD 39`, traced by `git log -S` to `362bfa0 feat(98-01)`. `[VERIFIED: read + regenerate + difflib + git log -S]` | **Shrinks.** D-18's regen-first ordering is still correct and cheap, but the *second* regen at phase end should be a **no-op**; if it is not, something unexpected touched the DB and that is a finding, not a routine refresh. D-18's rejection reasoning ("the exception would hide a real expected change") no longer holds — but the chosen action is still the right one. |
| C-3 | D-05: *"Ripple to own as task work: **82 references across 6 test files**"* | Literal flag-string references **scoped to `dev test`**: `--destructive` 10, `--output-dir` 11, `--submit` 2, `-y` 2 → 25 total, of which 23 are in `tests/test_dev_test_cmd.py` and 2 are the declaration sites in `cli_handlers.py`. The other 46+ belong to **`dev consistency-check` (`:1193`), `dev write-cycle` (`:1284`), `dev fault-inject` (`:1350`), `dev validate-family` (`:1570`), and `dev sdp` (`:2025`)** and must NOT be touched. Test-method granularity: **20 of 23** methods in `test_dev_test_cmd.py`. `[VERIFIED: AST-scoped count script]` | **Shrinks and sharpens.** The separate, larger ripple is the `derive_plan(destructive=…)` **kwarg** — 32 of 80 test functions in `test_chip_test.py` — which is a distinct decision (Open Question 1). |
| C-4 | D-05: *"`tools/check_devtest_orchestrator.py` … **fails closed when its scoped scan matches zero functions**" → "D-05 will trip it if the allow-list is not updated"* | `_scan_target_functions` filters on **function names**, not options (`:295-303`). Removing four `@click.option` decorators does not rename `dev_test`, so the gate **will not trip**. The real hazard is the inverse and it is **proven**: a `force=True` + raw-wire-dict violation placed in a *new, unlisted* helper yields `PASS … EXIT=0`; the identical violation inside `dev_test` yields `FAIL … EXIT=1`. `[VERIFIED: two fixture runs via FIRESTARTER_DEVTEST_HANDLER]` | **Redirects.** The mandatory task is not "avoid tripping the gate" but "extend `_HANDLER_FUNCTION_NAMES` to every new helper, or the gate silently under-covers this phase's new code." Note `_is_uv_eprom` is **already** in the allow-list (`:131`) and **does not exist** anywhere in the tree — a leftover speculative name from Phase 112. Landing D-02's handler-side helper under that exact name is free coverage. |
| C-5 | D-06: *"the `chip_test.py` frozensets `_DESTRUCTIVE_OPS` and `_MULTI_RUN_OPS`"* | `_DESTRUCTIVE_OPS` is **live** — the chip-ID destructive gate at `chip_test.py:587`. `_MULTI_RUN_OPS` (`:457`) has **zero references** anywhere in `firestarter/`, `tools/`, or `tests/`. `[VERIFIED: grep]` | **Splits by severity.** `_DESTRUCTIVE_OPS` is **safety-critical** (Pitfall 1b). `_MULTI_RUN_OPS` is documentation-only; updating it is cosmetic, and the phase may reasonably state it dead in-source instead. |
| C-6 | `<specifics>`: *"`count_applicable`'s N-of-M banner never fires again"* | The banner row is rendered **unconditionally** (`diagnostic_report.py:465`), so it always prints. And it is not uninformative: `n_ran` excludes `NA`/`SKIPPED`, so whenever the chip-ID destructive gate closes or `resolve_chip` refuses a step, `N < M` still holds and the banner still carries signal. `[VERIFIED: read]` | **Corrects.** `locked_steps` becomes permanently `[]`; the banner itself stays meaningful. Do not delete it as dead. |
| C-7 | D-15: *"Edit **only** `messages.toml`, then regenerate `firestarter/include/messages.h` and `firestarter_app/firestarter/messages.py`"* | There are **three** byte-identical `messages.toml` copies (meta `/workspaces/tools/catalog/`, `firestarter/tools/catalog/`, `firestarter_app/tools/catalog/`, all md5 `02acddb9…`). `tools/catalog/sync_to_subrepos.sh` is the single command that copies the meta catalog to both sub-repos **and** runs both codegens. `[VERIFIED: md5sum + read]` | **Widens the mechanism, not the intent.** Edit the **meta** copy, then run `bash tools/catalog/sync_to_subrepos.sh`. Editing a sub-repo copy directly breaks the three-way `cmp` invariant. |
| C-8 | D-13: *"`--skip-erase` **and `-b`** on a `0x0D` chip warn and proceed. One line stating this family has no erase to skip"* | Since Phase 92's decouple, `-b`/`--no-blank-check` skips **only** the blank check and no longer implies skip-erase (`cli_handlers.py:270-276, 538-541`). A "no erase to skip" warning on `-b` would be **factually wrong**, and `-b` is genuinely *useful* on `0x0D` (ROADMAP criterion 4: *"`-b` is required for a non-blank AT28C"* precisely because there is no erase to make it blank). `[VERIFIED: read]` | **Splits.** The **warn** belongs on `--skip-erase` only. `-b`'s `0x0D` treatment is a **GATE-02 documentation** statement, not a runtime warning. |
| C-9 | `REQUIREMENTS.md:88` cites SAFE-01's lock at `cli_handlers.py:1758-1760` | The `--destructive` option declaration is at `cli_handlers.py:1838-1846`; `dev_test` is `:1880-2018`. `[VERIFIED: read]` | Line-number drift only. Use the anchors in §F-9. |

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| UV-ness determination (DEVTEST-03) | **Pure compute** (`chip_test.py`) | — | D-02 fixes the decision point at `derive_plan`, the only layer holding the `full` DB dict. The programmer dict is the wire payload verbatim (`eprom_operations.py:333`), so it cannot carry the answer. |
| Write-region selection (DEVTEST-04) | **Pure compute** (`chip_test.py:_write_region_for`) | — | Already exists; must be converted from *guessing* to *reading* a plan-carried decision. Region **width** stays a module constant (SC4) — a DB entry must never widen it. |
| Consent prompt / TTY detection (DEVTEST-04, D-03) | **CLI handler** (`cli_handlers.py`) | — | `_is_interactive()` (`:1802-1809`) is the monkeypatchable seam; `chip_test.py` must stay bench-free and prompt-free (orchestrator-only contract, SAFE-03). |
| Erase-capability advertisement (DEVTEST-01) | **DB transform** (`database.py:convert_to_programmer`) | Firmware (`eprom_operations.cpp:36`, `operation_utils.cpp`) | D-12 is a *runtime* transform; the DB file carries no `flags` key. Firmware already refuses twice over (see §F-1). |
| Dedup query + issue filing (DEVTEST-05/06) | **Submission module** (`submit.py`) | CLI handler (orchestration order) | `submit.py` is already orchestrator-only and scanned in full by the gate. The `gh` shell-out belongs here, never in `chip_test.py`. |
| Capability-set invariance (GATE-01) | **Build-time tool** (`tools/check_sdp_capability_*.py`) | pytest (anti-hollow proof) | An AST gate cannot live in production code; the planted-violation proof cannot live in the gate. |
| Message-catalog wording (D-15) | **Meta-repo catalog** (`/workspaces/tools/catalog/messages.toml`) | Both sub-repo mirrors (generated) | Codegen-generated artefacts must never be hand-edited. |
| Docs (GATE-02) | **Both sub-repos' `doc/` + READMEs + `CLAUDE.md`** | — | Cross-repo; §F-7 enumerates all 8 with tracked status. |

---

## Findings

### F-1 — DEVTEST-01: D-12's blast radius is fully bounded, and smaller than feared

`database.py:convert_to_programmer` sets `FLAG_CAN_ERASE` (0x02) for every `electrical-type ∈ {EEPROM, Flash/EEPROM}` part with `algorithm != 5` (`:582-595`). All **84** protocol-`0x0D` chips qualify (66 `EEPROM` + 18 `Flash/EEPROM`) `[VERIFIED: DB enumeration]`.

Host readers of the flag, exhaustively `[VERIFIED: grep across firestarter/ + tools/]`:

| Site | Nature | D-12 impact |
|------|--------|-------------|
| `database.py:594` | the setter | the edit itself |
| `chip_test.py:343` (`can_erase = bool(prog.get("flags",0) & FLAG_CAN_ERASE)`) | **behavioural** | the intended effect — `derive_plan`'s existing generic `else` branch (`:411-423`) produces the `NA` erase step for free |
| `serial_comm.py:549` | inside `_log_command_details`, guarded by `logger.isEnabledFor(logging.DEBUG)` | none (DEBUG-only) |
| `cli_handlers.py:272, 539` | prose comments | none |
| `messages.py`, `constants.py`, `messages.toml`, `build_db.py`, `diff_db.py` | id/constant/prose | none |

Firmware readers `[VERIFIED: grep across src/ include/ test/]`: `eprom_operations.cpp:36` (`eprom_erase`'s precondition), `flash_5v_page.cpp:67`, `flash_nor_unlock.cpp:79`, `flash_intel.cpp:125`, `eprom.cpp:100`, `firestarter.cpp:88` (DEBUG log). **`src/proms/eeprom_28c.cpp` contains no `FLAG_CAN_ERASE` reference at all** — confirming `database.py:591`'s "firmware-inert on 0x0D" claim is factually true; D-12 reverses the *policy*, not the fact.

**One real behavioural change, benign and worth recording:** today `firestarter erase at28c256` passes `eprom_erase`'s `FLAG_CAN_ERASE` precondition and is then refused by Phase 119's NULL-`main` guard. After D-12 it is refused **earlier**, by `eprom_operations.cpp:36`. Both emit **`MSG_ERR_NOT_SUPPORTED`** `[VERIFIED: read both sites]`, so the observable wire id is unchanged.

Native-test exposure is **nil, confirmed by reading the code rather than trusting the claim**: `test_eeprom28c_sdp.cpp` case 25 constructs its handle with `ctrl_flags 0` (no `FLAG_CAN_ERASE`) and calls `op_execute_simple_operation` **directly**, with an in-source comment stating it *"deliberately bypass[es] `eprom_erase`'s own EARLIER `FLAG_CAN_ERASE` precondition check"*. `[VERIFIED: read test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp:1436-1475]`

**The two host tests that invert** — both confirmed to route through the real `convert_to_programmer`:

- `tests/test_database_conversion.py::test_convert_at28c256_flash_eeprom_flag_can_erase` (`:97-104`) — `assert out["flags"] & FLAG_CAN_ERASE`
- `tests/test_eprom_operations.py::test_sdp_command_flags_carry_the_db_can_erase_bit` (`:1128-1159`) — `assert captured["command_dict"]["flags"] == 2`; its helper `_at28c256_programmer_dict()` (`:1011-1017`) calls `resolve_chip` → `convert_to_programmer`, so this is a genuine inversion, not a hardcoded fixture.

`tests/test_val_wire_5v_page.py` is **unaffected, confirmed not assumed**: its two legs pin W29C040 (`0x05`, flags `0x00`) and W27C512 (`0x07`, flag set) — neither is `0x0D`. A repo-wide grep for `flags == 2` / `flags == 0x02` / `"flags": 2` returns **exactly one** hit, the `test_eprom_operations.py:1159` above. `[VERIFIED: grep]`

`diff_db.py` identity is unbreakable by D-12: `chip_database.json` entry keys are `{electrical, part_number, pinout, programming, support_status}` — **no `flags` key exists**. `[VERIFIED: key enumeration over all 746 entries]`

### F-2 — The op vocabulary and its true consumer set

`OP_ID/OP_READ/OP_BLANK_CHECK/OP_WRITE/OP_VERIFY/OP_ERASE` are defined at `chip_test.py:273-278`. Exhaustive consumer set `[VERIFIED: repo-wide grep]`:

| Consumer | Depends how | Phase-121 action |
|----------|-------------|------------------|
| `chip_test.py:352-423` (`derive_plan`) | constructs `Step(op=…)` | add the partial write step |
| `chip_test.py:453` `_DESTRUCTIVE_OPS` | **live** — chip-ID gate at `:587` | **MUST add the new op** (Pitfall 1b) |
| `chip_test.py:457` `_MULTI_RUN_OPS` | **dead** — zero references | cosmetic / state dead |
| `chip_test.py:734-746` (`_dispatch_step`) | `if/if/if` then **fall-through** to `_dispatch_multi_run` | **MUST gain a fail-closed arm** (Pitfall 1a) |
| `chip_test.py:866-889` (`_dispatch_multi_run`) | `if OP_WRITE / elif OP_VERIFY / else: # OP_ERASE` | **MUST gain an explicit arm** (Pitfall 1a) |
| `chip_test.py:964` `_RAN_VERDICTS` | verdicts only, not ops | none |
| `cli_handlers.py:37, 1790` | imports **`OP_ID` only** | none |
| `diagnostic_report.py` | **nothing** — op-agnostic (C-1) | none (optional `SCHEMA_VERSION`) |
| `tools/parse_devtest_issue.py` | **nothing** — keys on `[dev test]` title (`:59`), `schema_version` by presence (`:99`), `dedup_fingerprint` (`:180`) | none — confirms D-06's own correction |
| `tools/audit_coverage_matrix.py` | **nothing** (C-2) | none |
| `submit.py:190-197` (`build_body`) | renders `step.get('op')` generically | none |
| `tests/test_chip_test.py:53-58, 533-1523` | imports all six; ~95 usages | rework |

`dedup_fingerprint` (`diagnostic_report.py:174-199`) hashes `f"{op}={verdict}:{cls}"`, so D-06's differentiation-for-free claim holds. `build_db_diff` (`:250-285`) keys **only** on the verdict set, so D-08's zero-code-change claim holds. Both `[VERIFIED: read]`.

### F-3 — DEVTEST-03: the axis pick, decided with counts

All figures measured against the live `firestarter/data/chip_database.json` (746 entries) `[VERIFIED: enumeration script]`:

`electrical.type` distribution: UV-EPROM **301**, Flash/EEPROM **274**, EEPROM **95**, SRAM **75**, FRAM **1**.

UV-EPROM by `programming.algorithm`: `0x07` → 163, `0x08` → 106, `0x0B` → 32.

| Candidate axis | Selects | UV covered | Non-UV wrongly included | Verdict |
|---|---|---|---|---|
| **A. `algorithm == 0x0B`** (today's `_write_region_for` execution-time proxy) | 32 | **32 / 301 (10.6 %)** | 0 | **Reject.** Under D-01, the 269 missed UV parts each receive an **unprompted full-device write** — irrecoverable without a lamp. |
| **B. `algorithm ∈ {0x07, 0x08, 0x0B}`** (the widening D-02 rejected) | 329 | **301 / 301 (100 %)** | **28**, all `EEPROM` | Reject, as D-02 did. Conservative-safe, but forfeits `0x0B ⟹ UV` exclusivity and costs those 28 parts their full round-trip evidence. |
| **C. `full["electrical-type"] == "UV-EPROM"`** decided in `derive_plan` (**D-02**) | 301 | **301 / 301 (100 %)** | 0 | **Adopt — and it is the only exact axis.** |

**Recommendation: D-02's axis C, unchanged.** The count is decisive: it is the only option that is simultaneously complete and exact.

The 28 parts axis B would over-include, by name — worth naming because the list includes the operator's own bench chip:

> `ALI(Acer)/M8720` · `LINKAGE/LG28C010, LG28C020, LG28C040` · `MACRONIX/MX26C1000, MX26C2000, MX26C4000` · `PTC/PT28C010, PT28C020, PT28C040` · `SST/SST27SF010, SST27SF020, SST27SF256, SST27SF512, SST27VF010, SST27VF020, SST27VF256, SST27VF512, SST37VF010, SST37VF020, SST37VF040, SST37VF512` · `WINBOND/W27C01…, W27C02…, W27C04…, W27C257, `**`W27C512,W27E512`**`, W27E257`

**Consequence of axis C the planner must own and state in-source:** under D-01 + axis C, `W27C512` is `electrical-type == "EEPROM"` → **non-UV → full-device write, no prompt**. `.planning` memory `reference_st_m27c512_vs_winbond_w27c512.md` records that the Winbond `W27C512` and the ST `M27C512` are routinely confused; `M27C512` **is** UV-EPROM and *does* get the prompt. A tester who types the wrong "512" gets a different destructiveness class with no warning beyond D-04's unconditional notice. This strengthens the case for D-04's notice being first and unconditional.

The PATT-03 defect D-02 closes as a side effect, demonstrated live `[VERIFIED: executed `_write_region_for` on both dict shapes]`:

| Chip | etype | algo | `_write_region_for(full)` | `_write_region_for(prog)` ← what production passes |
|---|---|---|---|---|
| `M27C512` | UV-EPROM | 0x07 | `(65280, 256)` | **`(0, 256)`** ← wrong window |
| `AM27C020` | UV-EPROM | 0x08 | `(261888, 256)` | **`(0, 256)`** ← wrong window |
| `AT28C256` | EEPROM | 0x0D | `(0, 256)` | `(0, 256)` |
| `W27C512` | EEPROM | 0x07 | `(0, 256)` | `(0, 256)` |

### F-4 — DEVTEST-04: the minimal partial-write representation

The 256 B "small part" already exists: `_UV_WRITE_REGION_LENGTH = 256` (`chip_test.py:626`), top-anchored at `mem_size - 256` (`:664-667`), with the width sourced from the module constant and never from a DB field (SC4). **No new region helper is needed.**

The one structural obstacle is that the `Step` is discarded before the region is chosen `[VERIFIED: read call chain]`:

```
run_plan(plan, …)                                   # has plan AND step
  └─ _run_step(name, step, operator, db, …)         # has step
       └─ _dispatch_step(name, step, eprom_data, …) # has step
            └─ _dispatch_multi_run(step.op, name, eprom_data, …)   # ← step LOST; only the op string survives
                 └─ _write_region_for(eprom_data)   # must therefore GUESS from the programmer dict
```

**Minimal change:** widen `_dispatch_multi_run`'s signature to receive the `Step` (or just the region tuple) and pass it at the single call site `chip_test.py:744-746`. `_write_region_for` then *reads* rather than guesses, exactly as D-02 requires. This is a one-parameter change plus one call site.

**Recommended container split** (D-02 leaves the container to discretion):

- `Plan.is_uv: bool` — the *decision*, made once in `derive_plan` from the `full` dict. The handler reads it to decide whether to prompt at all.
- `Step.write_region: tuple[int, int] | None` — the *consequence*, carried down the existing call chain to `_dispatch_multi_run`.

**The prompt-ordering problem the planner must solve explicitly.** `derive_plan` builds `Plan.steps` *before* the handler can prompt, but the prompt answer determines the write scope. Three shapes, in preference order:

1. **`derive_plan(name, db, *, write_scope="full"|"partial")` plus a pure `chip_test.is_uv_eprom(full)` predicate** the handler calls first. Keeps the UV decision inside `chip_test` (D-02's spirit — one module owns it), keeps `derive_plan` pure and single-call, and gives the gate a nameable helper. **Bonus:** `check_devtest_orchestrator.py:131` already lists `_is_uv_eprom` in `_HANDLER_FUNCTION_NAMES` for a helper that never landed — landing the handler-side wrapper under that exact name is free gate coverage.
2. `derive_plan` returns a full-write plan carrying `is_uv`; a pure `apply_partial_write_scope(plan) -> Plan` mutates the write step afterwards. Testable, but two functions can now disagree about the region.
3. Two `derive_plan` calls. **Reject** — T-109-08 and D-01 both forbid a second derivation.

**`locked_destructive` becomes permanently empty.** Under D-04 there is no non-destructive path, so nothing is ever locked. Per `<specifics>`, do not leave it as vestigial scaffolding whose docstring describes a contract nothing enforces. `count_applicable` (`:1000-1002`) reads it, and the banner still carries signal via the chip-ID gate (C-6) — so **state it dead in-source and keep the field**; actual removal is the deferred cleanup.

### F-5 — DEVTEST-05/06: dedup + `gh`-first, executed live

Environment: `gh 2.95.0`, authenticated as `henols`, token scopes `gist, read:org, repo, workflow`. `[VERIFIED: gh --version, gh auth status]`

**D-09's argv works verbatim.** Executed against the real tracker `[VERIFIED: live run]`:

```bash
gh issue list --repo henols/firestarter_prom --author @me --search "a6915f4437ee" --state all
# → [{"number":18,"title":"[dev test] fm1608 — PASS (a6915f4437ee)",
#     "url":"https://github.com/henols/firestarter_prom/issues/18"}]
```

There is already a real `[dev test]` report on the tracker (issue #18, chip `fm1608`, fingerprint `a6915f4437ee`) — a live end-to-end fixture for the dedup path.

**Signal table — the planner must distinguish these three, they are not the same** `[VERIFIED: live runs]`:

| Condition | exit | stdout | Correct handling |
|---|---|---|---|
| duplicate found | 0 | non-empty JSON array | D-11: name the issue, offer `gh issue comment` |
| **no duplicate** | **0** | **empty** | proceed to the normal filing ask |
| `gh` unauthenticated / offline | **4** | empty; stderr `To get started with GitHub CLI, please run: gh auth login` | **D-10:** ask anyway, plus the explicit "duplicate check could not run" line |
| `gh auth status` unauthenticated | 1 | — | same as above |

Exit 0 covers **both** "found" and "not found" — so a bare exit-code check silently conflates a clean run with a missing duplicate. Key on the parsed payload, and always pass `--json number,title,url` rather than parsing the default human table.

**`gh issue comment` (D-11) argv surface** `[VERIFIED: gh issue comment --help]`: flags are `-b/--body`, `-F/--body-file`, `--create-if-none`, `--delete-last`, `--edit-last`, `-e/--editor`, `-w/--web`, `--yes`, plus inherited `-R/--repo`. There is **no label/assignee/milestone/project flag at all**, so commenting is inherently permission-independent in argv terms. The meaningful negatives to assert are therefore **`--delete-last`, `--edit-last`, `--yes`, `--web`, `--editor`** (each mutates or hijacks), and the meaningful positives are `-R/--repo SUBMIT_REPO` (never cwd-inferred) and `--body-file -` (stdin, no length cap — mirrors `submit_via_gh:252-268`).

**`gh issue create`'s write-gated flags are broader than the existing test asserts** `[VERIFIED: gh issue create --help]`: `-l/--label`, `-a/--assignee`, `-m/--milestone`, `-p/--project` — and `--project` explicitly warns *"Adding an issue to projects requires authorization with the `project` scope."* The existing idiom (`tests/test_submit.py:301-320`) asserts only `"--label" not in argv` and the `gsd-inbox` value. **Extend it to the short forms and the other three flags** — `-l` alone would defeat the current assertion.

`submit_report`'s current step order (`submit.py:365-468`) is: refuse-gate → sanitize+build → off-TTY print-and-return → on-TTY confirm → tier dispatch. D-05/D-09/D-10/D-11 restructure it to: refuse-gate → sanitize+build → **dedup query** → filing ask (always) → duplicate branch (`gh issue comment`) or create branch → tier dispatch. Note `submit_report` is called from `cli_handlers.py:2007-2010` behind `if submit:` — which D-05 removes, making the call unconditional.

**Trap: GitHub's issue-search index is eventually consistent.** A just-filed issue is not immediately returnable by `--search`. Two tests should exist per the `reference_dev_test_absent_chip_false_green_trap.md` discipline: assert **what was and was not called** (`run_fn.call_args`), never merely the exit status.

### F-6 — GATE-01: the gate precedent, and a proven coverage hole

**In-tree precedents.** `tools/check_devtest_orchestrator.py` is D-14's shape template: three deny classes in one `ast.NodeVisitor`, three env-override fixture seams (`FIRESTARTER_DEVTEST_SRC` / `_HANDLER` / `_SUBMIT`), a scoped name-filtered walk for the large pre-existing module, and a fail-closed `if not scanned:` guard (`:397-403`). `tools/check_is_memory_cmd_no_ifdef.py` is the fixture-injection template (`FIRESTARTER_CMD_ADMISSION_SRC`, with `if not os.path.isfile(path)` → fail-closed at `:293-294`). Existing planted fixtures live in `tests/fixtures/`: `planted_constants_fw_missing.h`, `planted_constants_host_missing.h`, `planted_constants_value_drift.h`, `planted_ifdef_in_predicate.h`, `planted_log_in_window.cpp`. `[VERIFIED: read + ls]`

**GATE-01's target surface** (`sdp_capability.py`, leave its shape intact): `SDP_PROTOCOL_ID = 13` (`:58`), `SDP_CAPABLE_TOKENS` — a `frozenset` of **65 string literals** (`:70-149`), `FRAM_TOKENS` (`:156`), `PRE_SDP_NAMED_TOKENS` (`:161-176`), `REASON_*` (`:180-184`), `split_part_number_tokens` (`:187`), `sdp_capability_for_entry` (`:201`), `sdp_capability` (`:266`). The two `return True` sites are `:263` (the sole allow, dominated by the `unrecognised` membership test at `:248`) and `:281` (the thin name-keyed wrapper). `tests/test_sdp_capability.py` has 12 test functions including the AST import-purity leg at `:640` — GATE-01 **adds to** this file, does not replace it.

**The proven coverage hole** `[VERIFIED: two live fixture runs]`. A `force=True` keyword **and** a raw wire-dict literal placed in a *new helper not named in `_HANDLER_FUNCTION_NAMES`*:

```
$ FIRESTARTER_DEVTEST_HANDLER=/tmp/.../handler_fixture.py python3 tools/check_devtest_orchestrator.py
PASS: scanned …; 0 VPP-set, 0 raw-wire-dict, 0 --force; firmware untouched   EXIT=0   ← silently missed
```

The identical violation moved inside `dev_test` fails correctly (`EXIT=1`, both buckets reported). **Therefore:** every helper this phase adds to `cli_handlers.py` for the UV ask, the dedup check, and the filing ask must be added to `_HANDLER_FUNCTION_NAMES` (`:126-136`), or the orchestrator gate under-covers exactly the new code. Land the UV helper as `_is_uv_eprom` — already listed, currently pointing at nothing.

**Non-vacuity by path, not only by planted violation.** The known trap (`reference_firmware_renames_break_host_source_scanning_gates.md`) is a gate aimed at a path that no longer exists passing vacuously. GATE-01's new checker targets a **host** file in its own repo, which lowers the cross-repo risk — but the discipline still applies: assert the resolved target path `os.path.isfile`, fail closed on a zero-symbol scan (Class 2's subject `SDP_CAPABLE_TOKENS` must be found **exactly once**), and print the resolved path in the PASS line so a future reader can see what was actually scanned.

### F-7 — GATE-02: all eight doc targets, verified

`[VERIFIED: existence + git ls-files per sub-repo]`

| Target | Lines | Tracked | Stale content located |
|---|---|---|---|
| `firestarter/doc/PROTOCOLS.md` | 438 | yes | §1.6 at `:178`. `:185` *"Firmware permanently disables SDP via a 6-cycle sequence before writing"* — pre-fix wording. `:188` *"The `FLAG_CAN_ERASE` and `electrical.type == "EEPROM"` derivation is authoritative"* — **D-12 makes this false for `0x0D`**. `:90` repeats the erase-model claim. `:50` is the 0x0D row of the bucket table (84 chips). |
| `firestarter/CLAUDE.md` | 183 | yes | GATE-02 target |
| `firestarter_app/doc/lockable-proms.md` | 398 | **NO — untracked** | D-16: commit as-is with §17's `AT28C16` row fixed, no provenance header. Confirmed untracked; `SECURITY.md` and `write_test_port.sh` are likewise untracked in the working tree. |
| `firestarter_app/doc/protocol-id.md` | 53 | yes | GATE-02 target |
| `firestarter/README.md` | 122 | yes | GATE-02 target |
| `firestarter_app/README.md` | 707 | yes | `:131` already documents the flag-free form (*"hand off into `firestarter dev test <chip>`"*) — needs the always-writes warning, not a flag edit |
| `firestarter_app/doc/community-validation.md` | 156 | yes | `:7`, `:26-29` ladder taxonomy, `:78-101` the N≥2 rule, `:113-116` triage. D-08's fingerprint-based GRAD-01 argument belongs at `:80`. |
| `firestarter_app/doc/beta-testing-install.md` | 203 | yes | **`:182` says *"This runs a non-destructive-by-default capability sweep"*** — the single most wrong line in the doc set under D-04. Also `:11`, `:24`, `:152`, `:167`, `:179`. |

D-15's catalog target `[VERIFIED: read]` — `firestarter/tools/catalog/messages.toml:284-290` (`0x5F MSG_INFO_SDP_UNLOCK_DONE_US`, format `"SDP unlock emitted in %lu us"`) must mirror `:306-312` (`0x61 MSG_INFO_SDP_LOCK_DONE_US`, format `"SDP lock sequence emitted in %lu us; protection state is not readable"`).

### F-8 — GATE-03: the real commands and the measured baseline

Everything below was executed in this session, from `/workspaces/firestarter_app` unless noted. Both submodules confirmed on `v1.22-at28c-software-data-protection-lifecycle` (`firestarter_app` @ `96e0622`, `firestarter` @ `0048b3d`) `[VERIFIED]`.

| # | Gate | Exact command | Baseline result |
|---|---|---|---|
| 1 | Firmware native suite | `cd /workspaces/firestarter && pio test -e native` | **141/141 PASSED** in 22.5 s (17 test groups) |
| 1b | Firmware native, no DEV_TOOLS | `cd /workspaces/firestarter && pio test -e native_nodevtools` | **141/141 PASSED** in 37.0 s |
| 2 | Host pytest | `python3 -m pytest tests/ -p no:cacheprovider --tb=no -q` | **1 failed, 1051 passed** in 48 s — the single failure is `test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` |
| 3 | Host pytest, **CI parity (py3.11)** | see §Environment Availability for the `uv` recipe, then `/tmp/venv311/bin/python -m pytest tests/ …` | **1 failed, 1051 passed** in 45 s — identical failure set |
| 4 | Coverage gate | `pytest tests/ --cov=firestarter --cov-fail-under=70` | **82.47 %** — passes with 12.5 pts headroom |
| 5 | ruff lint | `ruff check firestarter/ tests/` | **All checks passed!** (0.15.20 and 0.16.0 agree) |
| 6 | ruff format | `ruff format --check firestarter/ tests/` | **0.15.20 → 98 files already formatted. 0.16.0 (what CI resolves) → "1 file would be reformatted"** — see **Pitfall 2** |
| 7 | mypy watermark | `python3 tools/check_mypy_watermark.py` | `mypy errors: 1 (watermark: 35)` — 34 below, passes |
| 8 | `check_dispatch.py` | `python3 tools/check_dispatch.py` | PASS — 746 chips scanned, 736 supported, 10 non-dispatchable, 0 regressions |
| 9 | `check_devtest_orchestrator.py` | `python3 tools/check_devtest_orchestrator.py` | PASS — 0 VPP-set / 0 raw-wire-dict / 0 `--force` |
| 10 | `check_no_community_support_status_write.py` | `python3 tools/check_no_community_support_status_write.py` | PASS |
| 11 | `check_no_log_in_sdp_window.py` | `python3 tools/check_no_log_in_sdp_window.py` | PASS — emitter lines 298-314, poll lines 348-361 |
| 12 | `check_is_memory_cmd_no_ifdef.py` | `python3 tools/check_is_memory_cmd_no_ifdef.py` | PASS — predicate body lines 109-123, exactly 8 commands |
| 13 | **`diff_db.py` identity** | `python3 tools/diff_db.py` | **`PASS: all 2 changed chips explained (0 new, 0 removed)`, exit 0** — see note below |
| 14 | Catalog validity | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` | (run in both sub-repos; catalog is 73 messages, version 1) |
| 15 | Codegen drift, firmware | `cd /workspaces && python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --language cpp --target firestarter/include/messages.h && cd firestarter && git diff --exit-code include/messages.h` | **NO DRIFT** |
| 16 | Codegen drift, host | `cd /workspaces && python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --language python --target firestarter_app/firestarter/messages.py && cd firestarter_app && git diff --exit-code firestarter/messages.py` | **NO DRIFT** |
| 17 | Three-way catalog identity | `cmp` the three `messages.toml` copies | identical (md5 `02acddb9b70024879512012a7b9dd2b9`) |
| 18 | Remaining nine-row rows | `pytest tests/test_check_no_log_in_sdp_window.py tests/test_sdp_table_parity.py tests/test_check_is_memory_cmd_no_ifdef.py tests/test_sdp_bus_config_drift.py tests/test_revision_constants_parity.py tests/test_dispatch_mirror.py tests/test_check_devtest_orchestrator.py -q` + `python3 tools/gen_sdp_bus_config.py` | all inside the green 1051 |

**`diff_db.py` identity means "still exactly 2 explained changes", not "zero".** The baseline is 2 `[PGSZ_PAGE_SIZE]` changes (`W29C020,W29C020C,W29C022` page_size=128; `W29C040,W29C042` page_size=256) from Phase 94, with 0 new and 0 missing. A planner or verifier expecting a zero-diff will misread this gate.

**Known-red / known-flaky, current status** `[VERIFIED]`:

- `test_audit_coverage_matrix.py::test_golden_file_matches` — **genuinely red, pre-existing.** 186034 vs 184631 bytes, first divergence at index 1178 (`' '` vs `'|'`), 1268 vs 1266 lines, 21 diff hunks, 1169 diff lines. Cause is a **pinout split**, not a renderer change: golden has `DIP32_STD 127`, produced has `DIP32_27C020 88` + `DIP32_STD 39`, traced to `362bfa0 feat(98-01)`. D-18's regen is a pure refresh. **The ledger is not mutated by the run** (verified byte-identical after), so the regen is deterministic.
- `tests/test_no_programmer_found_read` / `_erase` (D-19's target) — **PASSED in this session with three live devices attached** (`/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0`). So the flake is **intermittent, not deterministic**; D-19 must not be validated by "it passes now". The hardening (patch the real port-enumeration seam, not only `comports`) is still correct; the proof must be a negative-call assertion, not a green run.
- Meta `.github/workflows/catalog-sync-check.yml` — expected-red-until-milestone-merge (checks out both sub-repos at `ref: main`). Phase 118/119 pattern; not this phase's damage.
- `firestarter/.github/workflows/build.yml`'s `native_nodevtools` step — inert on this branch (`on: push: branches: [main]`); the local `pio test -e native_nodevtools` run is the in-phase proof.

### F-9 — DEVTEST-02: the option-removal blast radius, scoped

`dev_test`'s four options and their exact anchors `[VERIFIED: read + AST handler mapping]`:

| Option | Declaration | Owner |
|---|---|---|
| `--destructive` | `cli_handlers.py:1838-1846` | `dev_test` (`def` at `:1880`) |
| `--output-dir` | `cli_handlers.py:1844-1855` | `dev_test` |
| `-y/--yes` | `cli_handlers.py:1856-1863` | `dev_test` |
| `--submit` | `cli_handlers.py:1864-1874` | `dev_test` |

**Identically-named options on OTHER commands — DO NOT TOUCH:** `--output-dir` at `:1193` (`dev_consistency_check`), `:1284` (`dev_write_cycle`), `:1350` (`dev_fault_inject`), `:1570` (`dev_validate_family`); `-y/--yes` at `:2025` (`dev_sdp`). This is the source of C-3's over-count. Their test references are equally off-limits: `test_matrix_artifact.py` (8 × `--output-dir`), `test_validate_family_cmd.py` (11), `test_validate_oracle.py` (9), `test_dev_sdp_cmd.py` (11 × `-y`), `test_consistency_check.py` (18 × `output_dir`), `test_eprom_operations.py` (12).

**The 20 of 23 `test_dev_test_cmd.py` methods that pass a removed flag** `[VERIFIED: AST scan]`:

`test_clean_destructive_run_exits_0` · `test_bad_write_outcome_exits_1` · `test_marginal_disagreement_exits_2` · `test_chip_id_mismatch_exits_1` · `test_non_destructive_run_never_dispatches_verify` · `test_off_tty_no_confirm_prompt` · `test_on_tty_destructive_confirm_gates` · `test_on_tty_declining_confirm_aborts_before_write` · `test_yes_bypasses_confirm_on_a_tty` · `test_destructive_run_fills_split_voltage_slots` · `test_non_destructive_run_fills_standalone_voltage_slots` · `test_output_dir_writes_exactly_two_hyphenated_files` · `test_no_output_dir_writes_to_default_reports_dir` · `test_json_artifact_is_report_to_dict` · `test_hw_revision_auto_captured_end_to_end` · `test_md_artifact_contains_fenced_json_block` · `test_bare_run_never_calls_submit_report` · `test_submit_flag_calls_submit_report_once_with_report_chip_json_file` · `test_submit_off_tty_end_to_end_never_opens_browser_or_runs_gh` · `test_dev_test_present_but_unsupported_still_sweeps`

Handler internals that must survive D-05 unchanged: **SAFE-04's `get_eprom`-emptiness hard-fail** (`:1932-1933`), `_is_interactive` (`:1802-1809`), `_verdict_code`/`_VERDICT_EXIT_CODES` (`:1739-1750`), `_sanitize_chip_token` (`:1753-1768`), `_chip_id_fields` (`:1771-1799`). `_make_sampler` (`:1812-1833`) is currently built only `if destructive` (`:1958`) — under D-04 it is always built, and the `if not destructive:` standalone-voltage branch (`:1963-1968`) becomes unreachable. `--output-dir`'s removal is genuinely free: the default is already `Path(get_config_dir()) / "reports"` (`:1988`) and `get_config_dir()` resolves `FIRESTARTER_CONFIG_DIR` **at call time** (`config.py:22-32`), so the env seam fully replaces the flag.

---

## Runtime State Inventory

This phase renames no symbol across repos and migrates no data, but the rename/refactor discipline still applies because it changes a **serialized vocabulary** consumed by artefacts already in the wild.

| Category | Items Found | Action Required |
|---|---|---|
| **Stored data** | `<config dir>/reports/dev-test-<chip>.{json,md}` on every tester's machine, written unconditionally (`cli_handlers.py:1985-2003`). Existing files carry `schema_version "1.1"` and the six-string vocabulary. Not a datastore, but is the input `tools/parse_devtest_issue.py` and `count_agreeing` read. | **Code edit only, no migration.** `parse_devtest_issue.py` accepts `schema_version` by **presence** (`:99`), so a bump breaks nothing. D-06's b11 back-compat must keep old six-string bodies parsing — cover it with a test using a literal b11-shaped body. |
| **Live service config** | `henols/firestarter_prom` GitHub issues. **Confirmed live:** issue #18 `[dev test] fm1608 — PASS (a6915f4437ee)`, authored by `henols`. Its embedded JSON carries the old vocabulary. Also: 3.0.0b11 in the wild still misfiles `--submit` into `firestarter_app` (`project_issue_tracking_centralized_firestarter_prom.md`); `SUBMIT_REPO` on **this branch** is already correct (`submit.py:73`). | **None required.** Read-only. Do NOT retro-edit existing issues. Use #18 as a live dedup fixture. |
| **OS-registered state** | None. `dev test` registers no OS-level task, service, or scheduled job. | **None — verified by grep for `Task Scheduler`/`launchd`/`systemd`/`pm2` across `firestarter/`: zero hits.** |
| **Secrets / env vars** | `FIRESTARTER_CONFIG_DIR` (report location; unchanged and now load-bearing since `--output-dir` goes away). `FIRESTARTER_DEVTEST_SRC`/`_HANDLER`/`_SUBMIT`, `FIRESTARTER_CMD_ADMISSION_SRC`, `FIRESTARTER_SDP_SRC`, `FIRESTARTER_DB_FILE` — gate fixture seams; GATE-01's new gate adds one more. `GH_TOKEN`/`GH_CONFIG_DIR` are read by `gh`, never by this code. | **None renamed.** Name GATE-01's new seam consistently (`FIRESTARTER_SDP_CAPABILITY_SRC`) and give it the same fail-closed `isfile` guard. |
| **Build artifacts / installed packages** | `firestarter_app/firestarter/messages.py` and `firestarter/include/messages.h` are **codegen-generated** and both currently drift-free. D-15 regenerates both. `firestarter_app.egg-info` from `pip install -e .` — unaffected (no `pyproject.toml` rename). `firestarter_app/tools/__pycache__` present. | **Regenerate via `bash tools/catalog/sync_to_subrepos.sh`, never by hand** (`reference_firmware_messages_h_is_codegen_generated.md`, `reference_codegen_ruff_clean_emitter.md`). |

---

## Common Pitfalls

### Pitfall 1a — A new op string reaching `_dispatch_multi_run` unhandled calls `erase_eprom()` and reports `OK`

**Severity: highest in this phase.** **What goes wrong:** `_dispatch_step` (`chip_test.py:734-746`) tests `OP_ID`, `OP_BLANK_CHECK`, `OP_READ` and then **falls through** to `_dispatch_multi_run`, whose dispatch is `if op == OP_WRITE / elif op == OP_VERIFY / else: # OP_ERASE` (`:878-887`). An unrecognized op therefore lands in the erase arm.

**Proven empirically in this session** `[VERIFIED: executed]`:

```python
res = _dispatch_multi_run("write-partial", "AT28C256", {"memory-size": 32768}, op, runs=2)
# operator calls : ['erase_eprom', 'erase_eprom']
# verdict        : OK   | StepResult.op: write-partial
```

**Why it happens:** the same architectural shape Phase 119 fixed in firmware — an unconfigured command falling through to a default that reports success having done the wrong thing. LOCK-04 fixed it at the firmware op layer; the host has the identical defect and nobody has looked.

**How to avoid:** land a **fail-closed arm before the new op string exists** — an explicit `else: return StepResult(op=op, verdict=VERDICT_BAD, reason="unhandled op …", run_count=0)` in `_dispatch_multi_run` (and/or `_dispatch_step`). This is the host mirror of Phase 119 D-06/D-07 and closes the class for every future op, not just this one.

**Warning signs:** a `write-partial` step reporting `OK` on a UV-EPROM (which has no electrical erase) would actually surface as `BAD`; on an **EEPROM** it silently succeeds while erasing the part. Test with the negative-call assertion (`erase_eprom.assert_not_called()`), never the exit code — `reference_dev_test_absent_chip_false_green_trap.md`.

### Pitfall 1b — Omitting the new op from `_DESTRUCTIVE_OPS` disables the chip-ID safety gate for the partial write

**What goes wrong:** `run_plan:587` reads `if step.op in _DESTRUCTIVE_OPS and destructive_gate_closed`. `_DESTRUCTIVE_OPS = frozenset({OP_WRITE, OP_ERASE})` (`:453`) is the **only live** use of that frozenset. A `write-partial` step absent from it is **not** gated by a chip-ID mismatch — it writes to a misidentified chip.

**Why it happens:** C-5 shows `_MULTI_RUN_OPS` is dead, so a reader who checks "are the frozensets updated?" superficially may treat both as equally cosmetic.

**How to avoid:** add `OP_WRITE_PARTIAL` to `_DESTRUCTIVE_OPS` and pin it with a test that closes the gate (id `BAD`) and asserts the partial write is `SKIPPED` with `_DESTRUCTIVE_GATE_REASON`. `tests/test_chip_test.py:785-792` is the exact existing idiom for `OP_WRITE`.

### Pitfall 2 — `ruff format --check` is green here and RED under the ruff version CI resolves — and the file it wants to reformat is D-18's golden

**What goes wrong, measured** `[VERIFIED: both versions run]`:

```
ruff 0.15.20 (devcontainer):  ruff format --check firestarter/ tests/  → 98 files already formatted
ruff 0.16.0  (CI-resolved):   ruff format --check firestarter/ tests/  → 1 file would be reformatted
                              → tests/golden/v1.3-COVERAGE-MATRIX.md
```

ruff 0.16 formats Python code blocks embedded in markdown. The block it targets is the `build_db.py:415-423` predicate quoted verbatim inside the matrix, at golden line ~447.

**Why it happens:** `pyproject.toml` `[project.optional-dependencies] test` pins `ruff>=0.15.14` with **no upper bound**, and CI runs `pip install -e .[test]` fresh on every job — so CI gets whatever ruff is newest at run time. `[tool.ruff]` declares **no `exclude`/`extend-exclude`**, so `tests/golden/` is in scope. This is the true mechanism behind `reference_devcontainer_py312_masks_ci_py39.md` — **not** the interpreter version (see Pitfall 3).

**Why it is worse than a normal format nit:** `test_golden_file_matches` asserts the golden is **byte-identical** to `audit_coverage_matrix.py`'s output. If any plan runs `ruff format` (without `--check`), the golden is rewritten and the test goes red — and re-running the generator un-does the format fix. Two gates in a loop, straddling D-18's first commit.

**How to avoid:** before any `ruff format` runs, add to `[tool.ruff]`:

```toml
extend-exclude = ["tests/golden"]
```

Alternatives, both worse: pin `ruff==0.15.*` in `[test]` (freezes lint hygiene project-wide); or reformat the snippet inside `audit_coverage_matrix.py`'s source so the emitted golden is 0.16-clean (couples a generator's string literals to a formatter version).

**Warning signs:** any `ruff format --check` result that differs between `ruff --version` 0.15.x and 0.16.x. Always report the ruff version alongside the verdict.

### Pitfall 3 — "ruff/format against the py3.9/3.11 CI targets" is partly impossible and partly a no-op; the useful parity run is py3.11 pytest

**What goes wrong:** GATE-03's wording sends the planner after four things, of which only one is both real and useful.

**Measured facts** `[VERIFIED]`:

- **ruff is config-pinned** (`pyproject.toml:92 target-version = "py39"`) → identical on any interpreter. Running it under a py3.11 venv changes nothing *about the target*; only the ruff **version** matters (Pitfall 2).
- **mypy is config-pinned** (`:111 python_version = "3.9"`, with the in-file note that mypy 2.1.0 rejects the CLI flag) → same.
- **A py3.9 pytest run is structurally impossible**: `[test]` requires `syrupy>=5.0`, and `syrupy>=5.0.0` requires `Python>=3.10`. `uv pip install -e '.[test]'` on py3.9.25 fails to resolve. So `requires-python = ">=3.9"` is a *runtime-package* claim the test suite cannot verify.
- **The devcontainer has no py3.9 or py3.11 interpreter** — only `/usr/local/bin/python3.12` and `/usr/bin/python3.13`.
- **ruff at `target-version = py39` does NOT catch 3.10-only syntax.** A probe file containing a `match` statement and a runtime `int | None` annotation produced only `D100`/`I001`/`F401` — no version diagnostic. So ruff is not a py3.9 compatibility gate.

**How to avoid:** interpret GATE-03 as (a) ruff/mypy at their pinned `py39` config, run with **the ruff version CI resolves**; (b) pytest on a real **Python 3.11**; (c) record that a py3.9 pytest run is impossible by dependency construction, so the milestone's py3.9 support claim rests on ruff/mypy config plus the classifier, not on a test run. See §Environment Availability for the verified `uv` recipe.

### Pitfall 4 — `derive_plan`'s `full` dict and `run_plan`'s programmer dict are different shapes, and only one knows about UV

**What goes wrong:** `_write_region_for` accepts either shape (`chip_test.py:660-663`) and the `electrical-type` leg is only ever satisfied by the `full` dict used in bench-free unit tests. In production, `_dispatch_multi_run` receives `resolve_chip`'s programmer dict, so only the `algorithm == 0x0B` leg can fire — the 32-of-301 miss. A unit test written against the `full` dict **passes while production is wrong** (F-3's table shows `M27C512` at `(65280,256)` vs `(0,256)`).

**How to avoid:** every test of the new UV/region behaviour must go through `run_plan`/`resolve_chip` (the production shape), not `_write_region_for(full)` directly. Assert on the region that `operator.write_eprom` actually received. Once D-02 lands, delete the `electrical-type` leg from `_write_region_for` entirely — leaving it lets a `full`-shaped test keep masking the real path.

### Pitfall 5 — D-15 touches firmware, so the cross-repo source-scanning gates are live in both directions

**What goes wrong:** `reference_firmware_renames_break_host_source_scanning_gates.md` — 4× in Phase 117, 4 pytest repairs in Phase 118. `firestarter_app` gates that scan firmware source text (`check_no_log_in_sdp_window.py` → `firestarter/src/proms/eeprom_28c.cpp`; `check_is_memory_cmd_no_ifdef.py` → `firestarter/include/firestarter.h`) break silently on a firmware rename, and a gate pointed at a missing path passes **vacuously**.

**Bounded here:** D-15 edits only `messages.toml` (plus generated mirrors) and two firmware docs — no `.cpp`/`.h` symbol renames. Neither host gate scans `messages.h` or `messages.toml`. So exposure is low — **but PROJECT.md FOURTH CORRECTION item 4 requires an explicit task from Phase 118 onward regardless**, and the check is cheap (rows 11-12 of §F-8).

**Also:** PROJECT.md SEVENTH CORRECTION item 9 — a path-scoped `git diff` passes **vacuously**. Prove firmware cleanliness with `git -C firestarter status --porcelain` being empty (or containing exactly the expected files), never with `git diff -- <path>` on a path nothing touched.

### Pitfall 6 — `--label`'s short form defeats the existing negative-argv assertion

**What goes wrong:** `tests/test_submit.py:301-320` asserts `"--label" not in argv` and that `GSD_INBOX_LABEL`/`"gsd-inbox"` are absent. `gh issue create` also accepts **`-l`** (plus `-a/--assignee`, `-m/--milestone`, `-p/--project`, all write/triage-gated) `[VERIFIED: gh issue create --help]`. An argv carrying `-l gsd-inbox` would fail the value check but pass the flag check; `-a`/`-m`/`-p` would pass entirely.

**How to avoid:** extend the idiom to a **deny-set** of `{"--label","-l","--assignee","-a","--milestone","-m","--project","-p"}` for `create`, and `{"--delete-last","--edit-last","--yes","--web","-w","--editor","-e"}` for `comment`. Keep `assert "shell" not in run_fn.call_args.kwargs` and the list-argv assertion (T-113-01's command-injection control).

### Pitfall 7 — GitHub's issue-search index is eventually consistent, so a fresh filing is invisible to the dedup query

**What goes wrong:** D-09 keys dedup on `gh issue list --search`, which hits GitHub's search index, not the issues API directly. An issue filed seconds earlier may not appear. Two consecutive `dev test` runs can both file.

**Why it matters less than it looks:** D-10's fail-open reasoning already covers it — `count_agreeing` groups by `dedup_fingerprint` on arrival, so a duplicate lands **visibly grouped**. Record it as a known limitation rather than engineering around it, and never present the dedup check as a guarantee in the user-facing string.

### Pitfall 8 — `run_plan`'s N≥2 default means every write runs twice

**What goes wrong:** `run_plan(runs=2)` is the default and `runs < 2` is rejected outright (`:566-577`). Every destructive op runs **`runs` times** (`:877`). Under D-04 a non-UV chip therefore receives **two full-device writes** per `dev test` invocation, and a UV chip two 256 B writes. The user-facing notice must not say "writes the chip" when it writes it twice; and the wear/time cost on a 262144-byte `AM27C020` is not incidental.

**How to avoid:** state the run count in the D-04 notice, or state it in the docs. Do not change `runs` — the AM27C020 write#1 60/64 vs write#2 0/64 case is exactly why the N≥2 marginal policy exists (D-05/D-06).

### Pitfall 9 — The `NA` erase reason must name the family fact, and `derive_plan`'s existing reason strings do not

**What goes wrong:** with `FLAG_CAN_ERASE` cleared, `derive_plan` falls into its generic `else` and emits **`"FLAG_CAN_ERASE not set for this chip"`** (`:417`) — the flag mechanism, which is exactly what CONTEXT's Claude's-Discretion constraint forbids. DEVTEST-01 requires *a named reason a community tester can act on*.

**How to avoid:** add a `0x0D`-specific reason arm *inside the existing `else`* (not a new `if can_erase` branch — D-12 deliberately routes through the generic path), yielding something like *"protocol 0x0D — the 28C family has no erase operation; each page write auto-erases internally"*. Note the sibling arms already do this correctly for `0x05` (`:413`) and UV (`:415`).

### Pitfall 10 — Executors prematurely mark multi-plan requirements Complete

Four occurrences in Phase 116. This phase has **nine** requirement ids across many plans. **Name the allowed `DEVTEST-NN`/`GATE-NN` ids in every dispatch prompt** and re-check `REQUIREMENTS.md` after each plan (`reference_executors_prematurely_mark_requirements_complete.md`). GATE-03 in particular can only be ticked by the final sweep.

### Anti-Patterns to Avoid

- **Exit-code-only tests for `dev test`.** The load-bearing assertion in the absent-chip work was `read_hardware_revision_value.assert_not_called()`. D-03's off-TTY path, D-09's dedup path, and Pitfall 1a all need negative-call assertions.
- **A second divergence implementation.** `_diff_offsets` (`chip_test.py:93-105`) is the ONE divergence primitive (D-04 mandate).
- **Hand-editing `messages.h` / `messages.py`.** Codegen only, and never hand-normalise the raw output.
- **Sourcing the write-region WIDTH from a DB field.** SC4: a malicious/misconfigured DB entry must not widen the window.
- **Putting the `gh` shell-out anywhere but `submit.py`.** `chip_test.py` is scanned in full by the orchestrator gate and must stay bench- and shell-free.
- **`git diff -- <path>` as a cleanliness proof.** Vacuous. Use `git status --porcelain`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Small write window for UV parts | a new region chooser | `_write_region_for` + `_UV_WRITE_REGION_LENGTH` (`chip_test.py:626, 640-670`) | DEVTEST-04's "small part" already exists, top-anchored, width-locked to a module constant |
| TTY detection for D-03 | `sys.stdin.isatty()` inline | `_is_interactive()` (`cli_handlers.py:1799-1806`) | `CliRunner.invoke` replaces `sys.stdin`; only the function-level seam survives monkeypatching |
| Warn-and-proceed on a vacuous flag (D-13) | new wording/shape | `cli_handlers.py:586-598` (HOST-02 D-18's `--skip-sdp-unlock` block) | exact precedent, exact tone, already tested |
| `gh` shell-out (D-09/D-11) | `subprocess` with a shell string | `submit_via_gh`'s list-argv + `run_fn` seam (`submit.py:235-277`) | permission-independent by construction; T-113-01's injection control; already mock-testable |
| Negative-argv proof | a bespoke assertion | `tests/test_submit.py:301-320` idiom, extended per Pitfall 6 | the project's established shape |
| AST deny-gate (GATE-01) | a fresh checker design | `tools/check_devtest_orchestrator.py` (multi-class + fail-closed) | in-tree precedent D-14 explicitly names |
| Planted-violation fixture injection | ad-hoc temp files in the test | `FIRESTARTER_*_SRC` env seam + `tests/fixtures/planted_*` | `check_is_memory_cmd_no_ifdef.py`'s pattern; fails closed on a missing path |
| Report location override | keep `--output-dir` | `get_config_dir()` reading `FIRESTARTER_CONFIG_DIR` at call time (`config.py:22-32`) | fully replaces the flag; D-05's premise verified |
| Catalog mirror sync (D-15) | copy files by hand | `bash tools/catalog/sync_to_subrepos.sh` | copies to **both** sub-repos, runs **both** codegens, asserts the three-way identity (C-7) |
| Absent-chip hard fail | a `resolve_chip` refusal check | SAFE-04's `get_eprom`-emptiness gate (`cli_handlers.py:1929-1930`) | keyed off DB emptiness so an in-DB-but-unsupported chip still sweeps |
| PII scrubbing for the issue body | new regexes | `sanitize_dict` / `_SCRUBS` (`submit.py:92-143`) | every vector has its own test; a missed vector fails OPEN |

**Key insight:** almost everything DEVTEST-04 and DEVTEST-06 "need" already exists and is already tested. The genuinely new code is small: one op string, one fail-closed dispatch arm, one plan-carried decision, one prompt, one `gh` query, one AST gate. The risk is concentrated in what *silently keeps working* when the new pieces are wired wrong.

---

## Architecture Patterns

### System Architecture Diagram — `dev test` after Phase 121

```
                       user: `firestarter dev test <chip>`   (no options — DEVTEST-02)
                                        │
                                        ▼
                    ┌───────────────────────────────────────────┐
                    │  cli_handlers.dev_test  (orchestrator)    │
                    └───────────────────────────────────────────┘
                                        │
        (1) ALWAYS-WRITES NOTICE ───────┤  unconditional, FIRST line (D-04)
                                        │
        (2) SAFE-04 hard fail ──────────┤  app.db.get_eprom(chip) empty? → ChipNotFoundError
                                        │  (before ANY hardware is energized)
                                        ▼
                    ┌───────────────────────────────────────────┐
                    │  chip_test.is_uv_eprom(full)              │  ◄── DEVTEST-03 axis C:
                    │  full["electrical-type"] == "UV-EPROM"    │      301/301 exact
                    └───────────────────────────────────────────┘
                              │                       │
                       UV ────┤                       ├──── non-UV
                              ▼                       │
              ┌───────────────────────────┐           │
              │ _is_interactive()?        │           │  no prompt (D-01)
              └───────────────────────────┘           │
                   TTY │        │ off-TTY (D-03)      │
              ask ─────┤        └─► treat as "no" ────┤
                  yes/no                              │
                    │                                 │
                    ▼                                 ▼
             write_scope="partial"            write_scope="full"
             (256 B top-anchored)             (whole device)
                    └─────────────┬───────────────────┘
                                  ▼
                    ┌───────────────────────────────────────────┐
                    │ chip_test.derive_plan(name, db,           │
                    │                       write_scope=…)      │  ◄── reads `full` dict ONLY;
                    │  · Plan.is_uv                             │      never resolve_chip
                    │  · Step.write_region  (D-02 carried)      │
                    │  · OP_ERASE → NA on 0x0D (DEVTEST-01,     │
                    │    via D-12's cleared FLAG_CAN_ERASE)     │
                    └───────────────────────────────────────────┘
                                  ▼
                    ┌───────────────────────────────────────────┐
                    │ chip_test.run_plan(plan, operator, db)    │
                    │   per step: resolve_chip (guard-HONORING) │
                    │   id FIRST → destructive_gate             │
                    │   _DESTRUCTIVE_OPS must include the new   │
                    │   partial op, or the gate misses it ⚠     │
                    │   _dispatch_step → _dispatch_multi_run    │
                    │     ⚠ FAIL-CLOSED arm required: an        │
                    │       unhandled op falls into erase_eprom │
                    │   _write_region_for READS Step.write_region│
                    └───────────────────────────────────────────┘
                                  │ list[StepResult]
                                  ▼
                    ┌───────────────────────────────────────────┐
                    │ diagnostic_report.DiagnosticReport        │
                    │   to_dict() → schema_version, steps,      │
                    │     banner, voltage, db_diff,             │
                    │     dedup_fingerprint (hashes op names)   │
                    │   build_db_diff → ladder_state            │
                    │     (keys on VERDICTS only — D-08 free)   │
                    │   ** op-string-AGNOSTIC: no edits (C-1) **│
                    └───────────────────────────────────────────┘
                          │                          │
                          ▼                          ▼
        <config dir>/reports/dev-test-<chip>.{json,md}   console render
                          │
                          ▼
                    ┌───────────────────────────────────────────┐
                    │ submit.submit_report  (ALWAYS reached)    │
                    │  1 is_submittable refuse gate             │
                    │  2 sanitize_dict → build_body/build_title │
                    │  3 DEDUP: gh issue list --repo … --author  │
                    │    @me --search <shorthash> --state all   │
                    │      exit 0 + rows → duplicate            │
                    │      exit 0 + empty → no duplicate        │
                    │      exit≠0 → say "could not check" (D-10)│
                    │  4 ASK (every run — DEVTEST-05)           │
                    │  5a duplicate → gh issue comment          │
                    │  5b new → gh issue create (tier 1)        │
                    │         └─ fallback → browser URL (tier 2)│
                    │  negative argv asserted on BOTH (D-06/⚠P6)│
                    └───────────────────────────────────────────┘
                                  ▼
                    exit code = max(_verdict_code(r)) — 0/1/2 unchanged
```

### Pattern 1 — Fail-closed dispatch at the host op layer (Phase 119 LOCK-04, ported to Python)

**What:** never let an unrecognized op reach a default that performs an action.
**When to use:** the moment `OP_WRITE_PARTIAL` is contemplated — land the guard **first**, in its own commit, with a RED-then-GREEN proof.

```python
# firestarter/chip_test.py — _dispatch_multi_run, replacing the bare `else: # OP_ERASE`
    for _ in range(runs):
        if op == OP_WRITE or op == OP_WRITE_PARTIAL:
            _sample(sampler, "before")
            outcomes.append(operator.write_eprom(name, eprom_data, tmp_source_path))
            _sample(sampler, "after")
        elif op == OP_VERIFY:
            outcomes.append(operator.verify_eprom(name, eprom_data, tmp_source_path))
        elif op == OP_ERASE:
            outcomes.append(operator.erase_eprom(name, eprom_data))
        else:
            # Host mirror of Phase 119 D-06/D-07: an unconfigured op must NEVER
            # fall through to a destructive default. Before this arm existed,
            # `_dispatch_multi_run("write-partial", ...)` called erase_eprom()
            # twice and reported OK (proven, 121-RESEARCH Pitfall 1a).
            return StepResult(
                op=op, verdict=VERDICT_BAD, run_count=0,
                reason=f"{op}: no dispatch arm in _dispatch_multi_run "
                       "(refused fail-closed rather than falling through to erase)",
            )
```

### Pattern 2 — Decide once in the layer that has exact information; read it downstream

**What:** D-02. `derive_plan` holds the `full` dict; the execution layer holds only the programmer dict, which is the wire payload verbatim (`eprom_operations.py:333`) and therefore cannot be extended.
**When to use:** any per-chip property the execution layer currently infers from `algorithm`.

```python
# Source: chip_test.py:640-670 (current), restructured per D-02
def _write_region_for(step: Step, eprom_data: dict[str, Any]) -> tuple[int, int]:
    """READ the region derive_plan already decided. Never re-derive UV-ness here:
    the programmer dict this receives at execution time carries `algorithm` but
    NOT `electrical-type`, and `algorithm == 0x0B` matches only 32 of 301 UV
    parts (measured). Under D-01 a missed UV part receives an unprompted
    full-device write, so a guess here is a chip-destroying bug, not a coverage gap.
    """
    if step.write_region is not None:
        return step.write_region
    return _WRITE_REGION_START, _WRITE_REGION_LENGTH
```

### Pattern 3 — Warn-and-proceed on a vacuous flag (HOST-02 D-18 → D-13)

```python
# Source: cli_handlers.py:586-598, the exact template D-13 follows
    elif skip_erase and is_protocol_0x0d:
        click.echo(
            f"{eprom.upper()}: --skip-erase has nothing to skip on this chip's "
            "protocol — the 28C family (protocol 0x0D) has no erase operation at "
            "all; each page write auto-erases internally. Proceeding with a "
            "normal write."
        )
```

Note per C-8: this arm belongs on `--skip-erase` **only**, never on `-b`.

### Pattern 4 — The dedup query, with all three signals distinguished

```python
# Source: argv executed live against henols/firestarter_prom in this session
def find_prior_report(fingerprint: str, *, run_fn=subprocess.run) -> tuple[str | None, bool]:
    """Return (issue_url_or_None, check_ran). LIST argv, never a shell string.

    exit 0 + rows  -> duplicate found          -> (url, True)
    exit 0 + empty -> no duplicate             -> (None, True)
    exit != 0      -> gh absent/unauth/offline -> (None, False)  [D-10: ask anyway,
                      and say the duplicate check could not run]
    """
    proc = run_fn(
        ["gh", "issue", "list", "--repo", SUBMIT_REPO, "--author", "@me",
         "--search", fingerprint, "--state", "all",
         "--json", "number,title,url", "--limit", "20"],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        return None, False
    rows = json.loads(proc.stdout or "[]")
    return (rows[0]["url"] if rows else None), True
```

### Pattern 5 — Non-vacuous gate: prove the path AND the planted violation

```python
# tests/test_check_sdp_capability.py
def test_gate_is_not_vacuous_by_path():
    """A gate aimed at a missing path passes vacuously — the documented
    cross-repo failure mode. Assert the real target resolves BEFORE trusting PASS."""
    assert Path(check_sdp_capability._DEFAULT_SDP_CAPABILITY_SRC).is_file()

def test_gate_fails_closed_on_a_missing_target(tmp_path):
    env = {**os.environ, "FIRESTARTER_SDP_CAPABILITY_SRC": str(tmp_path / "nope.py")}
    assert subprocess.run([sys.executable, GATE], env=env).returncode == 1

def test_class2_planted_widenable_allowset_is_caught(tmp_path):
    f = tmp_path / "planted_widenable_allowset.py"
    f.write_text("SDP_CAPABLE_TOKENS = frozenset(t for t in load())\n")   # comprehension, not literals
    env = {**os.environ, "FIRESTARTER_SDP_CAPABILITY_SRC": str(f)}
    assert subprocess.run([sys.executable, GATE], env=env).returncode == 1
```

---

## Standard Stack

No new runtime dependency is needed. Everything this phase requires is already in the tree or on the host.

### Core (existing, unchanged)

| Library | Version | Purpose | Why standard |
|---|---|---|---|
| `click` | (per `pyproject.toml` deps) | CLI; `@dev.command`, `@click.option` | already the whole CLI surface (Phase 41 CLI-01..04) |
| `rich` | ″ | `Console`, `Confirm.ask` for the D-01 prompt | already imported at `cli_handlers.py:31-32`; `submit.py:58` |
| `pytest` | ≥8.0 | host suite | CI gate |
| `syrupy` | ≥5.0 | snapshot tests (29 snapshots) | **requires Python ≥3.10** — see Pitfall 3 |
| `ruff` | **≥0.15.14, unpinned** | lint + format gate | **the unpinned upper bound is Pitfall 2's root cause** |
| `mypy` | ≥2.1.0 | watermark gate, strict on 8 modules incl. `cli_handlers.py` | `tools/check_mypy_watermark.py` |
| `pytest-cov` | ≥7.1.0 | `--cov-fail-under=70` (currently 82.47 %) | CI gate |
| stdlib `ast` | — | GATE-01's checker | every in-tree gate uses it; structural > substring (v1.21 SAFE-03, 118 D-06, 119 D-04, 120 D-12) |
| stdlib `subprocess` | — | `gh` shell-out with **list** argv | T-113-01 injection control |
| `gh` CLI | **2.95.0 present, authenticated** | dedup query + create + comment | external tool, not a package dep |
| PlatformIO | `pio` on PATH | `pio test -e native` / `-e native_nodevtools` | firmware suite |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|---|---|---|
| `gh issue list --search` for dedup | `gh api /search/issues` | same index, same eventual-consistency lag, more argv surface — no gain |
| `gh` for dedup | a config-dir fingerprint ledger | rejected at D-09; "same user" degrades to "same machine", and a browser-tier URL open would write a ledger entry for an issue never submitted |
| `extend-exclude = ["tests/golden"]` | pinning `ruff==0.15.*` | pinning freezes lint hygiene project-wide for one markdown file |
| a py3.9 pytest run | ruff/mypy at `py39` config + the classifier | a py3.9 run is impossible (`syrupy` floor) |

**Installation:** none. Verification of the one external tool:

```bash
gh --version && gh auth status     # 2.95.0, authenticated as henols  [VERIFIED]
```

## Package Legitimacy Audit

**This phase installs no external packages.** No new entry is added to `[project.dependencies]` or `[project.optional-dependencies]`; no `npm`/`pip`/`cargo` install is required. Every library named above is already resolved in the committed `pyproject.toml` and was exercised in this session.

| Package | Registry | Verdict | Disposition |
|---|---|---|---|
| *(none added)* | — | — | — |

**Packages removed due to `[SLOP]` verdict:** none.
**Packages flagged as suspicious `[SUS]`:** none.

The one dependency-adjacent action the planner may consider is **tightening** an existing pin (`ruff`) or adding `extend-exclude` — neither introduces a new package. `gh` is an OS-level CLI already installed at `/usr/bin/gh`, not a package dependency.

---

## Validation Architecture

`workflow.nyquist_validation` is absent from `.planning/config.json` → treated as enabled.

### Test Framework

| Property | Value |
|---|---|
| Framework (host) | `pytest` ≥8.0 + `syrupy` ≥5.0 (29 snapshots) + `pytest-cov` ≥7.1.0 |
| Framework (firmware) | PlatformIO / Unity, envs `native` and `native_nodevtools` |
| Config file | `/workspaces/firestarter_app/pyproject.toml` (`[tool.ruff]`, `[tool.mypy]`); `/workspaces/firestarter/platformio.ini` |
| Quick run command | `python3 -m pytest tests/test_chip_test.py tests/test_dev_test_cmd.py tests/test_diagnostic_report.py tests/test_submit.py -q` (~5 s) |
| Full suite command | `python3 -m pytest tests/ --cov=firestarter --cov-fail-under=70 -q` (~50 s) + `cd /workspaces/firestarter && pio test -e native` (~23 s) |

### Phase Requirements → Test Map

| Req | Behavior | Type | Automated command | File exists? |
|---|---|---|---|---|
| DEVTEST-01 | `OP_ERASE` is `NA` on `0x0D` with a family-fact reason | unit | `pytest tests/test_chip_test.py -k "erase and 0x0d or na_erase" -x` | ❌ new legs in existing file |
| DEVTEST-01 | `convert_to_programmer` clears `FLAG_CAN_ERASE` on `0x0D` | unit | `pytest tests/test_database_conversion.py -k flag_can_erase -x` | ✅ (2 legs **invert**) |
| DEVTEST-01 | wire `flags` for `at28c256` is 0, not 2 | integration | `pytest tests/test_eprom_operations.py -k can_erase_bit -x` | ✅ (**inverts**) |
| DEVTEST-02 | `dev test <chip>` accepts no options; each removed flag errors | unit | `pytest tests/test_dev_test_cmd.py -k "no_options or rejects_flag" -x` | ❌ new; 20 of 23 existing methods rework |
| DEVTEST-02 | the 4 other `dev` sub-commands keep their `--output-dir`/`-y` | regression | `pytest tests/test_matrix_artifact.py tests/test_validate_family_cmd.py tests/test_validate_oracle.py tests/test_dev_sdp_cmd.py -q` | ✅ must stay green untouched |
| DEVTEST-03 | UV-ness decided in `derive_plan`; 301/301 exact | unit | `pytest tests/test_chip_test.py -k is_uv -x` | ❌ new |
| DEVTEST-03 | production path (programmer dict) gets the right region — Pitfall 4 | integration | `pytest tests/test_chip_test.py -k write_region_via_run_plan -x` | ❌ new; must NOT test `_write_region_for(full)` |
| DEVTEST-04 | yes → full device; no → 256 B top-anchored | unit | `pytest tests/test_dev_test_cmd.py -k "uv_ask" -x` | ❌ new |
| DEVTEST-04 | off-TTY → partial, and it really writes (D-03) | unit | `pytest tests/test_dev_test_cmd.py -k off_tty_partial -x` — assert `write_eprom` **called** with the 256 B region | ❌ new |
| DEVTEST-04 | **unhandled op never reaches `erase_eprom`** (Pitfall 1a) | unit | `pytest tests/test_chip_test.py -k unhandled_op_fails_closed -x` — `erase_eprom.assert_not_called()` | ❌ new — **highest priority** |
| DEVTEST-04 | partial write is chip-ID gated (Pitfall 1b) | unit | `pytest tests/test_chip_test.py -k partial_write_gated_on_id_mismatch -x` | ❌ new |
| DEVTEST-04 | `dedup_fingerprint` differs partial vs full (D-06/D-08) | unit | `pytest tests/test_diagnostic_report.py -k fingerprint_partial -x` | ❌ new |
| DEVTEST-04 | b11 six-string bodies still parse | unit | `pytest tests/test_parse_devtest_issue.py -k legacy_vocabulary -x` | ❌ new |
| DEVTEST-05 | every run asks; dedup runs first | unit | `pytest tests/test_submit.py -k "always_asks or dedup_first" -x` | ❌ new |
| DEVTEST-05 | `gh` failure → ask anyway + explicit line (D-10) | unit | `pytest tests/test_submit.py -k dedup_check_unavailable -x` | ❌ new |
| DEVTEST-06 | `create` argv carries no write-gated flag incl. short forms (Pitfall 6) | unit | `pytest tests/test_submit.py -k permission_gated -x` | ✅ **extend** `:301-320` |
| DEVTEST-06 | `comment` argv carries no mutating flag; targets `SUBMIT_REPO` | unit | `pytest tests/test_submit.py -k comment_argv -x` | ❌ new |
| GATE-01 | checker fails on each planted class | unit | `pytest tests/test_check_sdp_capability.py -q` | ❌ new file + 2 fixtures |
| GATE-01 | checker is non-vacuous by path | unit | same file, `test_gate_is_not_vacuous_by_path` | ❌ new |
| GATE-01 | new `dev test` helpers are gate-covered (F-6 hole) | unit | `pytest tests/test_check_devtest_orchestrator.py -q` + a leg asserting every new helper name is in `_HANDLER_FUNCTION_NAMES` | ✅ extend (14 tests) |
| GATE-02 | docs contain no pre-fix SDP/erase claim | manual-only | doc review — no automatable oracle for prose accuracy | n/a |
| GATE-03 | full nine-row sweep | integration | §F-8 rows 1-18, under the py3.11 venv with CI-resolved ruff | ✅ all exist |

### Sampling Rate

- **Per task commit:** `python3 -m pytest tests/test_chip_test.py tests/test_dev_test_cmd.py -q` (~5 s)
- **Per wave merge:** `python3 -m pytest tests/ -q` + `cd /workspaces/firestarter && pio test -e native`
- **Phase gate:** the full §F-8 table, run under `/tmp/venv311` with the CI-resolved ruff version, before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_check_sdp_capability.py` — GATE-01's companion pytest (new file)
- [ ] `tests/fixtures/planted_permit_by_default.py` — D-14 Class 1 fixture
- [ ] `tests/fixtures/planted_widenable_allowset.py` — D-14 Class 2 fixture
- [ ] `tools/check_sdp_capability_invariants.py` — GATE-01's checker (new)
- [ ] `[tool.ruff] extend-exclude = ["tests/golden"]` — **must land before any `ruff format` run** (Pitfall 2)
- [ ] The Pitfall 1a fail-closed dispatch arm + its RED-then-GREEN test — **before** `OP_WRITE_PARTIAL` exists
- [ ] Framework install: none needed (`pip install -e '.[test]'` already satisfied)

---

## Security Domain

`security_enforcement` is absent from `.planning/config.json` → treated as enabled.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | **no** (delegated) | Authentication to GitHub is entirely `gh`'s (`gh auth status`); no token is read, stored, or logged by this code. Verified: no `GH_TOKEN`/`GITHUB_TOKEN` reference anywhere in `firestarter/`. |
| V3 Session Management | no | no sessions |
| V4 Access Control | **yes** | The whole `gh` design is permission-minimising: the create argv is permission-independent by construction (`submit.py:235-277`), and D-06's negative-argv discipline is the control. Extend the deny-set per Pitfall 6. |
| V5 Input Validation | **yes** | `_sanitize_chip_token` (`:1753-1768`) prevents an arbitrary chip name escaping the report directory. `sanitize_dict` (`submit.py:126-143`) is the PII backstop — a missed vector **fails OPEN** into a PUBLIC issue body. The dedup fingerprint injected into `--search` is a 12-char sha256 hex slice, so it carries no metacharacter, but the list-argv rule must still be asserted. |
| V6 Cryptography | **no** (non-security use) | `hashlib.sha256` in `dedup_fingerprint` is a distribution primitive, not a security control (T-113-06, stated in-source). Do not "harden" it. |
| V12 Files & Resources | **yes** | Report path is `Path(get_config_dir()) / "reports"` with `mkdir(parents=True, exist_ok=True)`; temp pattern files are `NamedTemporaryFile(delete=False)` with an `unlink` in a `finally` (`chip_test.py:916-921`). |
| V14 Configuration | **yes** | `FIRESTARTER_CONFIG_DIR` becomes the *only* report-location control once `--output-dir` is removed. SAFE-01's "never from config or environment" applies to **consent**, not to paths — do not accidentally re-introduce an env-readable consent path. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard mitigation |
|---|---|---|
| Command injection via the `gh` shell-out | Elevation of Privilege | list argv, never a shell string; `assert "shell" not in run_fn.call_args.kwargs` (T-113-01) |
| PII leak into a **public** GitHub issue | Information Disclosure | `sanitize_dict`'s 7 `_SCRUBS` + username pattern; each vector has its own test; `submit_via_browser` names only `saved_json_path.name`, never the full path |
| Path traversal via a crafted chip name | Tampering | `_sanitize_chip_token` allow-lists `[alnum]`, `-`, `_`, `.` |
| **Silent destructive misdispatch** (Pitfall 1a) | Tampering / Repudiation | fail-closed dispatch arm; the report must never claim `OK` for an action not performed (117 D-05, 118 D-02, 119 D-12, 120 D-11) |
| **Unconsented write to silicon** (D-03, owned) | Tampering | mitigated only by D-04's unconditional first-line notice and the docs — this is an accepted, operator-chosen trade-off, recorded not engineered away |
| Widened SDP allow-set via a user's `~/.firestarter/database.json` | Tampering | `sdp_capability.py` is a static fail-closed allow-list; GATE-01 Class 2 is the structural control preventing the set becoming inferrable/mutable |
| Write-window widening via a malicious DB entry | Tampering | region **width** is a module constant (`_UV_WRITE_REGION_LENGTH`), never a DB field (SC4) |

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| Python (devcontainer default) | host suite | ✓ | 3.12.13 (`/usr/local/bin/python3`) | — |
| **Python 3.11 (CI parity)** | GATE-03 pytest parity | ✗ **not preinstalled** | — | **`uv`-provisioned, verified working** (recipe below) |
| **Python 3.9 (`requires-python` floor)** | GATE-03's literal wording | ✗ | — | **None — impossible.** `syrupy>=5.0` requires Python ≥3.10; `uv pip install -e '.[test]'` fails to resolve on 3.9.25 |
| `uv` | provisioning 3.11 | ✓ | at `/usr/local/bin/uv` | needs `UV_CACHE_DIR`/`UV_PYTHON_INSTALL_DIR` overrides — `~/.cache/uv` is **not writable** (`Permission denied`) |
| `ruff` (devcontainer) | lint/format | ✓ | **0.15.20** | — |
| `ruff` (CI-resolved) | the version CI actually gets | ✓ via the parity venv | **0.16.0** | — **use this one for the GATE-03 verdict** (Pitfall 2) |
| `mypy` | watermark gate | ✓ | 2.1.0 | — |
| `pio` / PlatformIO | firmware native suite | ✓ | `/usr/local/bin/pio` | — |
| `gh` CLI | DEVTEST-05/06 | ✓ | **2.95.0, authenticated as `henols`** (scopes `gist, read:org, repo, workflow`) | D-10's fail-open path; unauth exit is **4** |
| Live programmer boards | not needed by this phase | ✓ | `/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0` attached | — |
| GSD knowledge graph | context enrichment | ✓ file present, ✗ **useless** | 671 h stale, **400 commits behind** (`f4150b8` vs `55ccd14`); all three capability queries returned 0 nodes | none — this research used direct code reading instead |
| Network / GitHub API | live `gh` verification | ✓ | — | — |

**Verified CI-parity recipe** (executed successfully in this session):

```bash
export UV_CACHE_DIR=/tmp/uvcache UV_PYTHON_INSTALL_DIR=/tmp/uvpy
uv python install 3.11                                  # → CPython 3.11.15
uv venv --python 3.11 /tmp/venv311
cd /workspaces/firestarter_app
uv pip install --python /tmp/venv311/bin/python -e '.[test]'   # resolves ruff 0.16.0
/tmp/venv311/bin/python -m pytest tests/ -q                    # 1 failed, 1051 passed
/tmp/venv311/bin/ruff check firestarter/ tests/                # All checks passed!
/tmp/venv311/bin/ruff format --check firestarter/ tests/       # 1 file would be reformatted ⚠
/tmp/venv311/bin/python tools/check_mypy_watermark.py          # 1 error (watermark 35)
/tmp/venv311/bin/python -m pytest tests/ --cov=firestarter --cov-fail-under=70   # 82.47%
```

**Missing dependencies with no fallback:** Python 3.9 for a pytest run — structurally impossible (`syrupy` floor). GATE-03's py3.9 clause must be satisfied by ruff/mypy's pinned `py39` config, and that limitation recorded.

**Missing dependencies with fallback:** Python 3.11 — provision with `uv` per the recipe above.

---

## Project Constraints (from CLAUDE.md)

### `/workspaces/CLAUDE.md` (meta)

- **Repo layout:** meta tracks only `.planning/` and `.claude/`; code lives in the `firestarter/` and `firestarter_app/` sub-repos. Neither sub-repo is committed to the meta repo.
- **`firestarter_app/firestarter/constants.py` ↔ `firestarter/include/firestarter.h` must change together** — flag bits and command codes are duplicated. **This phase does not change any flag bit value** (`FLAG_CAN_ERASE` stays `0x02`); D-12 changes only *when the host sets it*. No constants edit is required, and adding one would trigger `tests/test_revision_constants_parity.py`.
- **Serial-protocol changes must be kept in sync** between `serial_comm.py` and `firestarter.cpp`. Not applicable — no wire-format change.
- **`chip_database.json` is generated — do NOT edit by hand.** Reinforces the out-of-scope lock.

### `/workspaces/firestarter_app/CLAUDE.md`

- **Tooling gate (v1.8):** `ruff check` + `ruff format --check` + `mypy` (strict on 8 modules, **`cli_handlers.py` among them**) + `pytest --cov-fail-under=70`, all enforced by `.github/workflows/ci.yml`, with `pre-commit` mirroring the hook order. **Consequence:** every new function added to `cli_handlers.py` needs full type annotations (`disallow_untyped_defs = true` for that module). `chip_test.py`, `submit.py`, `diagnostic_report.py`, and `database.py` are **not** in the strict island, so they are only watermark-tracked (currently 1 error against a 35 watermark).
- **`tools/check_dispatch.py` is the WARNING-5 regression guard** — asserts (a) structurally that no chip routes to `configure_eprom` on a vpp-pin-less pinout, and (b) type-keyed that no `DIP28_2764` 5V-EEPROM routes to `configure_eprom`. Must stay green (§F-8 row 8).
- **`build_db.py`'s `0x07 → 0x0D` override** for ~23 28C-family parts is the reason the `0x0D` bucket has 84 members. Out of scope to touch.
- Documented sub-repo doc-lockstep rule: `firestarter/doc/SHIELD-REVISIONS.md` mirrors four sections of meta `.planning/v1.7-SHIELD-REVS.md`. Not touched by GATE-02's list.

No `.claude/skills/` or `.agents/skills/` directory exists in this repo — no project skills to honor. `[VERIFIED: ls]`

---

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|---|---|---|---|
| `dev test` non-destructive by default; `--destructive` opt-in | **Always writes**; UV parts prompted, others unprompted | **this phase** (D-01/D-03/D-04) | reverses SAFE-01, Phase 109 D-01, Phase 112 Plan 04, and v1.21 SUB-01/02 — **three recorded reversals** |
| `--submit` explicit + interactive-only, never on a bare run | every run asks | **this phase** (DEVTEST-05) | the third reversal; `REQUIREMENTS.md:114` already records it |
| `FLAG_CAN_ERASE` set on `0x0D` because it is firmware-inert | cleared for `0x0D` | **this phase** (D-12) | reverses `database.py:591`'s explicit "must stay unchanged" |
| `mem_type`/`type` axis for firmware dispatch | `protocol_id` / `algorithm` only | v1.20 (breaking) | the hard constraint behind D-02's rejected alternative — the programmer dict must not regain a type field |
| `write -b` implied skip-erase | `-b` skips only the blank check; `--skip-erase` is explicit | Phase 92 | **C-8**: makes D-13's `-b` clause factually wrong; the warn belongs on `--skip-erase` |
| Curated 37/47 then interim 74/10 SDP partitions | **43 ALLOW / 41 REFUSE** derived from `infoic.xml` `INFOIC2PLUS` `flags` bit 15 @ `a8efaedc` | Phase 120 | GATE-01 guards this set's **shape**, never its correctness |
| Silent `RESPONSE_CODE_OK` on a NULL `firestarter_operation_main` | generic op-layer refusal → `MSG_ERR_NOT_SUPPORTED` + `RESPONSE_CODE_ERROR` | Phase 119 (D-06/D-07) | DEVTEST-01's firmware half; **and the pattern the host still needs** (Pitfall 1a) |
| `ruff format` ignored markdown code blocks | ruff 0.16 formats them | ruff 0.16.0 | **Pitfall 2** — the newly-in-scope file is D-18's golden |

**Deprecated / outdated in the phase inputs:**

- ROADMAP's *"closed six-string set consumed by the issue parser"* — the parser has no op vocabulary (already corrected by D-06; re-verified here).
- CONTEXT D-06's *"`diagnostic_report.py`'s renderer and `to_dict`"* — op-agnostic (C-1).
- CONTEXT D-18's *"this phase genuinely changes the matrix"* — it does not (C-2).
- CONTEXT D-05's *"82 references across 6 test files"* and *"D-05 will trip [the orchestrator gate]"* (C-3, C-4).
- `REQUIREMENTS.md:88`'s `cli_handlers.py:1758-1760` anchor — now `:1838-1846` (C-9).

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | `gh issue comment` on a **public** repo requires only an authenticated account, never write access | §F-5 / D-11 | D-11's permission-independence claim fails for community testers → the duplicate path silently errors for exactly the users it targets. **Not verified in this session** — verifying it destructively would post a real comment to `henols/firestarter_prom`. The *argv* surface is verified (`gh issue comment --help` has no write-gated flag); the *server-side* permission is assumed. **Recommend a `checkpoint:human-verify` task**: the operator (or a second GitHub account with no write access) comments once on a throwaway issue. |
| A2 | `gh issue create --label` **aborts before creating** when the label does not pre-exist or the user lacks write access | §F-5 / DEVTEST-06 | If it merely warns, the negative-argv discipline is defensive rather than load-bearing. Taken from `.planning` memory `reference_gh_label_argv_needs_preexisting_label_and_write_access.md` and PROJECT.md SEVENTH CORRECTION item 4 — a prior in-project finding, but re-verifying it would create a real issue. The `-l` short-form gap (Pitfall 6) is a real hardening regardless of A2's truth. |
| A3 | GitHub's issue-search index is eventually consistent, so a just-filed issue may not appear in `--search` | Pitfall 7 | Under-states dedup reliability (harmless) or over-states it (a duplicate slips through). D-10's `count_agreeing` fingerprint grouping already absorbs the failure mode either way. |
| A4 | CI resolves `ruff 0.16.0` today because `[test]` pins `ruff>=0.15.14` with no upper bound | Pitfall 2 | The version CI resolves drifts over time — it may already be newer. The **mechanism** (unpinned floor + fresh install per job) is verified; the specific version is a snapshot. Re-check with `uv pip install` in the parity venv at plan time rather than trusting `0.16.0`. |
| A5 | The devcontainer's live `/dev/ttyACM*` devices are the reason `test_no_programmer_found_*` is *sometimes* red | §F-8 / D-19 | If the flake has another cause, D-19's port-enumeration-seam fix will not stop it. Both tests **passed** in this session with three devices attached, so the correlation is unproven here. D-19's fix is still correct on its own terms (a monkeypatch that a real device can defeat is a weak monkeypatch). |
| A6 | `firestarter_app/doc/lockable-proms.md`'s ~300 rows are compiled from third-party datasheets | D-16 | Bears on D-16's owned trade-off, not on any code path. Sourced from CONTEXT.md; not independently audited row-by-row here. §17's `AT28C16` row is separately known wrong (SEVENTH CORRECTION item 6). |

**Every other factual claim in this document is tagged `[VERIFIED: …]` at its point of use** and was produced by executing a command or reading a file on the milestone branch in this session.

---

## Open Questions

1. **Does `derive_plan` keep its `destructive` kwarg?**
   - *What we know:* D-04 removes every non-destructive caller. `destructive=` appears 63 times (47 in `tests/test_chip_test.py`, 14 in `chip_test.py`, 1 in `cli_handlers.py`, 1 in `tests/test_provenance.py`), and **32 of 80** test functions in `test_chip_test.py` use it. `locked_destructive` becomes permanently `[]`.
   - *What's unclear:* whether the kwarg is removed (largest test churn, cleanest final shape), retained as always-`True` (smallest churn, leaves a permanently-dead branch), or **replaced** by `write_scope="full"|"partial"` (F-4's option 1, which subsumes it).
   - *Recommendation:* **replace it with `write_scope`.** It is the same signature slot, it is what DEVTEST-04 actually needs, and it makes the dead `destructive=False` branch impossible to reach by construction rather than by convention. Budget the `test_chip_test.py` rework explicitly — it is the single largest mechanical item in the phase and is **not** the 20-of-23 figure from `test_dev_test_cmd.py`.

2. **Where does the always-writes notice sit relative to SAFE-04's hard fail?**
   - *What we know:* handler order is `_is_interactive` (`:1912`) → `--destructive` confirm (`:1919`) → SAFE-04 `get_eprom` check (`:1932`) → `derive_plan` (`:1935`) → `read_hardware_revision_value` (`:1947`, energizes hardware). D-04 requires the notice be *"unconditional and first"*.
   - *What's unclear:* whether printing it before SAFE-04 (so an unknown chip also sees it) satisfies or violates "unconditional".
   - *Recommendation:* print it **first, before SAFE-04**. "Unconditional" is the stronger reading, an unknown chip seeing the notice is harmless and honest, and it guarantees the notice precedes anything that energizes the shield.

3. **How is the `ruff format` / golden collision resolved, and in which commit?**
   - *What we know:* `extend-exclude = ["tests/golden"]` is the smallest fix; the collision is live today and independent of this phase; D-18 mandates the golden regen be commit 1.
   - *What's unclear:* whether the exclude lands **before** commit 1 (so commit 1's "host pytest GREEN" proof is trustworthy) or alongside it.
   - *Recommendation:* land the exclude **in commit 1, together with the golden regen**, and record it as a discovered pre-existing CI defect. D-18's goal is that the phase's matrix delta be attributable in isolation — an unrelated formatter collision in the same file would defeat exactly that.

4. **Is `_MULTI_RUN_OPS` updated, deleted, or documented dead?**
   - *What we know:* zero references anywhere. D-06 names it as task work.
   - *Recommendation:* update it **and** add an in-source note that it is currently unreferenced, mirroring the `<specifics>` instruction about `locked_destructive`. Deleting it is a behaviour-free cleanup that would make a future reader wonder whether the N≥2 policy lost a guard.

5. **Does GATE-01's Class 1 need to handle `sdp_capability`'s second `return True` site?**
   - *What we know:* `sdp_capability_for_entry` returns `True` once at `:263`, lexically dominated by the `unrecognised` membership test at `:248`. `sdp_capability` at `:281` is a one-line delegating wrapper with no literal `return True`.
   - *What's unclear:* whether D-14's "any `return (True, …)` not lexically dominated by a membership test against `SDP_CAPABLE_TOKENS`" rule needs a whitelist for a pure delegation.
   - *Recommendation:* scope Class 1 to `return` statements whose value is a **tuple literal** starting with a `True` constant. That matches `:263` exactly and ignores delegating returns without needing a whitelist.

---

## Sources

### Primary (HIGH confidence) — executed or read on the milestone branch in this session

- `firestarter_app/firestarter/chip_test.py` (full, 1009 lines) — op vocabulary `:272-278`, `Step` `:281-296`, `Plan` `:298-316`, `derive_plan` `:318-427`, `_DESTRUCTIVE_OPS`/`_MULTI_RUN_OPS` `:453-457`, `run_plan` `:512-597`, region constants `:614-637`, `_write_region_for` `:640-670`, `_dispatch_step` `:711-746`, `_dispatch_multi_run` `:833-937`, `count_applicable` `:984-1008`
- `firestarter_app/firestarter/cli_handlers.py` `:240-289`, `:490-613`, `:1730-2038` — `_build_op_flags`, `write` + HOST-02 D-18 warn block, `dev_test` and all four options, `_is_interactive`, `_make_sampler`, `_VERDICT_EXIT_CODES`
- `firestarter_app/firestarter/database.py` `:525-598` — `convert_to_programmer`, the `FLAG_CAN_ERASE` block and its D-03 note
- `firestarter_app/firestarter/diagnostic_report.py` `:130-509` — `is_submittable`, `dedup_fingerprint`, `_LADDER_*`, `build_db_diff`, `_step_dict`, `to_dict`, `render`
- `firestarter_app/firestarter/submit.py` (full, 469 lines) — `SUBMIT_REPO`, `GSD_INBOX_LABEL`, `_SCRUBS`, `sanitize_dict`, `build_title/body/issue_url`, `gh_available`, `submit_via_gh`, `submit_via_browser`, `submit_report`
- `firestarter_app/firestarter/sdp_capability.py` (full, 282 lines) — GATE-01's target surface
- `firestarter_app/tools/check_devtest_orchestrator.py` (full, 432 lines) — D-14's shape precedent; the source of the C-4 correction
- `firestarter_app/tools/check_is_memory_cmd_no_ifdef.py`, `tools/audit_coverage_matrix.py`, `tools/parse_devtest_issue.py`, `tools/diff_db.py`, `tools/check_dispatch.py`
- `firestarter_app/tests/` — `test_audit_coverage_matrix.py:576-645`, `test_submit.py:295-325`, `test_database_conversion.py:90-112`, `test_eprom_operations.py:1011-1165`, `test_val_wire_5v_page.py:135-150`
- `firestarter/src/eprom_operations.cpp:28-48`, `src/proms/eeprom_28c.cpp:189-220`, `test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp:1412-1475`, `tools/catalog/messages.toml:284-313`, `platformio.ini`, `doc/PROTOCOLS.md`
- `/workspaces/tools/catalog/sync_to_subrepos.sh` (full)
- `firestarter_app/pyproject.toml`, `.github/workflows/ci.yml`, `CLAUDE.md`; `/workspaces/CLAUDE.md`
- **Commands executed:** `pio test -e native` (141/141) · `pio test -e native_nodevtools` (141/141) · `pytest tests/` on 3.12 and on `uv`-provisioned 3.11 (1F/1051P both) · `pytest --cov-fail-under=70` (82.47 %) · `ruff check`/`ruff format --check` on 0.15.20 **and** 0.16.0 · `check_mypy_watermark.py` · `check_dispatch.py` · `check_devtest_orchestrator.py` (plus two planted-fixture runs proving the C-4 coverage hole) · `check_no_community_support_status_write.py` · `check_no_log_in_sdp_window.py` · `check_is_memory_cmd_no_ifdef.py` · `diff_db.py` · both `codegen.py` drift gates · `md5sum` on all three catalogs · `gh --version`/`auth status`/`issue list` (5 variants incl. unauthenticated) · `gh issue create --help`/`issue comment --help` · a DB enumeration script over all 746 entries · a live `_dispatch_multi_run("write-partial", …)` misdispatch reproduction · a live `_write_region_for` full-vs-programmer-dict comparison · `generate_matrix` + `difflib` against the golden · `git log -S DIP32_27C020`
- `.planning/phases/121-.../121-CONTEXT.md`, `.planning/REQUIREMENTS.md` (`:67`, `:84-98`, `:114`, `:191-212`, §Validation Ceiling), `.planning/phases/119-.../119-NONREGRESSION.md` §5 (the nine-row table), `.planning/config.json`

### Secondary (MEDIUM confidence)

- `gh issue comment --help` / `gh issue create --help` output — authoritative for the **argv surface**; the server-side permission model behind A1/A2 is not established by `--help` text
- `.planning` memories: `reference_devcontainer_py312_masks_ci_py39.md` (mechanism corrected here to the unpinned ruff version), `reference_audit_coverage_matrix_golden_stale.md`, `reference_dev_test_absent_chip_false_green_trap.md`, `reference_gh_label_argv_needs_preexisting_label_and_write_access.md`, `reference_firmware_renames_break_host_source_scanning_gates.md`, `reference_executors_prematurely_mark_requirements_complete.md`, `reference_firmware_messages_h_is_codegen_generated.md`, `reference_codegen_ruff_clean_emitter.md`, `reference_st_m27c512_vs_winbond_w27c512.md`, `reference_write_b_skips_erase.md`, `project_issue_tracking_centralized_firestarter_prom.md`

### Tertiary (LOW confidence)

- GSD knowledge graph at `.planning/graphs/graph.json` — **not used.** 671 h stale, 400 commits behind (`f4150b8` vs `55ccd14`), and all three capability queries (`dev test sweep`, `submission issue filing`, `capability gate`) returned zero nodes. Any semantic relationship it would have offered should be treated as absent, not approximate. Direct code reading replaced it entirely.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| Op-vocabulary consumer set (F-2) | **HIGH** | exhaustive repo-wide grep plus reads of every hit; three CONTEXT/ROADMAP framings corrected against the live tree |
| UV axis counts (F-3) | **HIGH** | enumerated all 746 DB entries; all three axes counted; the 28 over-included parts listed by name; the PATT-03 divergence executed |
| Partial-write representation (F-4) | **HIGH** | full call chain read; the erase misdispatch reproduced in one tool call |
| D-12 blast radius (F-1) | **HIGH** | every host and firmware reader enumerated; both inverting tests traced to the real transform; the "no native test pins the flags" claim verified by reading case 25's `ctrl_flags 0` |
| Dedup / `gh` argv (F-5) | **HIGH** for argv + exit codes (executed live against the real tracker, returned the real issue #18); **MEDIUM** for `gh issue comment` server-side permissions (A1 — not destructively verified) |
| GATE-01 precedent + coverage hole (F-6) | **HIGH** | precedents read in full; the hole proven with two fixture runs and opposite exit codes |
| Non-regression baseline (F-8) | **HIGH** | all 18 rows executed with recorded output, on both 3.12 and a CI-parity 3.11 |
| Pitfall 2 (ruff version divergence) | **HIGH** | both ruff versions run; the exact file and hunk identified; `[tool.ruff]` confirmed to have no exclude |
| Pitfall 3 (py3.9/3.11 targets) | **HIGH** | py3.9 install failure reproduced with its resolver message; ruff's inability to flag 3.10-only syntax probed directly |
| Doc target list (F-7) | **HIGH** for existence/tracked status/stale-line location; **MEDIUM** for what the corrected prose should say (Claude's discretion + operator review) |
| GATE-02 prose accuracy | **MEDIUM** | no automatable oracle exists for "this sentence describes behaviour that reaches silicon"; human review required |

**Research date:** 2026-07-29
**Valid until:** **2026-08-05 (7 days)** — fast-moving on two axes: the CI-resolved `ruff` version drifts under an unpinned floor (A4), and the `henols/firestarter_prom` issue set changes as community reports arrive. The code-anchored findings (file:line, counts, dispatch shape) are stable for the life of the milestone branch; re-run §F-8 at plan time rather than trusting these baselines if either sub-repo advances.
