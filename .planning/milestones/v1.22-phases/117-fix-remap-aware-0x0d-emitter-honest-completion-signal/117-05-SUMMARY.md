---
phase: 117-fix-remap-aware-0x0d-emitter-honest-completion-signal
plan: 05
subsystem: testing
tags: [platformio, unity, native-test, avr, sdp, at28c, eeprom28c, non-regression-gate, blob-sha]

# Dependency graph
requires:
  - phase: 117-fix-remap-aware-0x0d-emitter-honest-completion-signal
    provides: "plan 117-01's RED capture, plan 117-02's remap-aware fix + GREEN capture, plan 117-03's FIX-06 split, plan 117-04's FIX-05 guards — the four commits this gate measures against"
provides:
  - "FIX-04: literal git blob-SHA equality proof (all six FIX-04-frozen artifacts unchanged from phase base ada4bdc7)"
  - "Full native-suite non-regression proof (108/108) and both board builds' figures + a measured Leonardo flash delta"
  - "Host-untouched proof (firestarter_app committed history unmoved) and no-new-constant proof (messages.h/firestarter.h unchanged)"
  - "A committed, re-runnable ## FIX-04 non-regression gate (Phase 117 close) section in RED-BASELINE.md joining the RED (117-01) and GREEN (117-02) records"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Content-addressed identity proof as the phase-close gate: literal git blob SHAs measured at the phase base commit, embedded in the plan and re-checked at the phase's last plan, are immune to a wrong diff base, a rebase, or an amend."
    - "Explicit-exclusion recording for pre-existing dirty state: firestarter_app's committed history (HEAD unmoved) is the load-bearing proof; its pre-existing uncommitted .gitignore change and untracked files are named and dated, not silently ignored and not falsely claimed clean."

key-files:
  created: []
  modified:
    - firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Recorded the measured Leonardo flash delta (+204 B) as-is, contradicting the research prediction of net-negative, rather than reframing the arithmetic to fit the prediction — the plan requires the measured number either way, with no threshold claim."
  - "Recorded firestarter_app's pre-existing dirty working tree (.gitignore + 5 untracked files) as an explicit, named exclusion rather than claiming a clean tree, per the plan's submodule_commit_protocol instruction — the phase's actual host-untouched criterion is the unmoved commit history (36a9bb5), which does hold."
  - "Ticked FIX-04 only in REQUIREMENTS.md after independently verifying FIX-01, FIX-02, FIX-03, FIX-05, FIX-06 were already Complete — per the plan's requirement-scoping guard and the standing .planning memory about executors mis-marking multi-plan requirements."

requirements-completed: [FIX-04]

coverage:
  - id: D1
    description: "All six FIX-04-frozen artifacts (4 production files + 2 shared golden headers) are byte-identical to the phase base by literal git blob SHA"
    requirement: FIX-04
    verification:
      - kind: unit
        ref: "chained `test \"$(git rev-parse HEAD:<path>)\" = <expected>` command over all six paths printed GATE_OK; git diff --exit-code HEAD -- <six paths> exited 0; git log --oneline -1 for each path named a pre-Phase-117 commit"
        status: pass
    human_judgment: false
  - id: D2
    description: "The other five 0x0D-adjacent protocol families' golden-trace suites (test_val_eprom, test_val_nor_unlock, test_val_5v_page, test_val_flash_intel, test_val_sram) pass unchanged"
    requirement: FIX-04
    verification:
      - kind: unit
        ref: "pio test -e native -f \"*<name>*\" for each: 6/6, 4/4, 8/8, 3/3, 6/6, all PASSED"
        status: pass
    human_judgment: false
  - id: D3
    description: "Full native suite green at the explained case count (95 + 8 + 3 + 2 = 108), both board targets build, and the Leonardo flash delta versus the phase base is measured"
    requirement: FIX-04
    verification:
      - kind: unit
        ref: "pio test -e native: 108 test cases, 108 succeeded, exit 0, 16 suites; pio run -e leonardo / -e uno both SUCCESS; scratch git worktree build of ada4bdc7 measured Leonardo 25324/28672 B vs this commit's 25528/28672 B (+204 B delta)"
        status: pass
    human_judgment: false
  - id: D4
    description: "No firestarter_app file changed anywhere in the phase's committed history, and no new MSG_*/FLAG_* value was introduced"
    requirement: FIX-04
    verification:
      - kind: unit
        ref: "git -C firestarter_app log --oneline -1 names 36a9bb5 (unmoved since before the phase); git diff --exit-code ada4bdc7 HEAD -- include/messages.h include/firestarter.h exits 0"
        status: pass
    human_judgment: false
  - id: D5
    description: "Exactly six paths changed across the whole phase, none FIX-04-frozen; the gate record and validation-ceiling statement are committed"
    requirement: FIX-04
    verification:
      - kind: unit
        ref: "git diff --name-only ada4bdc7 HEAD | sort lists exactly platformio.ini, src/proms/eeprom_28c.cpp, test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md, test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp, test/native/avr/test_sdp_harness/test_sdp_harness.cpp, test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp (6 total); grep -c for the new section header, '66 of 84', and all six blob SHAs verbatim all passed; git show --stat --name-only HEAD lists exactly one file"
        status: pass
    human_judgment: false

# Metrics
duration: 24min
completed: 2026-07-28
status: complete
---

# Phase 117 Plan 05: FIX-04 Non-Regression Gate (Phase 117 Close) Summary

**Proved all six FIX-04-frozen artifacts byte-identical to the phase base by literal git blob SHA, ran the full 108/108 native suite plus both board builds with a measured +204 B Leonardo flash delta, confirmed `firestarter_app`'s committed history unmoved and no new `MSG_*`/`FLAG_*` value anywhere in the phase, and committed a re-runnable `## FIX-04 non-regression gate (Phase 117 close)` section closing the requirement ledger six of six.**

## Performance

- **Duration:** ~24 min
- **Started:** 2026-07-28T10:20:00Z
- **Completed:** 2026-07-28T10:44:45Z
- **Tasks:** 2
- **Files modified:** 2 (one in `firestarter/`, one in the meta repo)

## Accomplishments

- All six FIX-04-frozen artifacts — `src/proms/flash_utils.cpp`, `include/flash_utils.h`, `src/proms/flash_5v_page.cpp`, `src/proms/flash_nor_unlock.cpp`, `test/native/avr/_shared/sdp_expected.h`, `test/native/avr/_shared/sdp_bus_config.h` — proven byte-identical to the phase base `ada4bdc728118bd3d0f93ea444e9b60954191ddd` by literal git blob SHA. All six match the plan's expected values exactly; the chained verification command printed `GATE_OK`. `git log --oneline -1` on each path names a pre-Phase-117 commit (Phase 116, Phase 104, or earlier), confirming the most recent touch to any frozen path predates this phase.
- The five other `0x0D`-adjacent protocol families' golden-trace suites all pass unchanged: `test_val_eprom` (6/6), `test_val_nor_unlock` (4/4), `test_val_5v_page` (8/8), `test_val_flash_intel` (3/3), `test_val_sram` (6/6). The pre-existing KNOWN-FLAKY `test_flash_intel_vpp` documented at `platformio.ini:72-77` turns out not to be in `[env:native]`'s `test_filter` allowlist at all, so it never runs under this env and had nothing to report.
- Full `pio test -e native`: **108/108 test cases succeeded, exit code 0**, across all 16 allowlisted suites, none `FAILED` or `ERRORED`. Arithmetic explained: pre-phase baseline 95 (Phase 116 close) + 8 (`test_eeprom28c_sdp`, plan 117-01) + 3 (`test_val_eeprom28c`, plan 117-03) + 2 (`test_sdp_harness`, plan 117-04) = 108. Observed matches exactly.
- Both `pio run -e leonardo` and `pio run -e uno` report `SUCCESS`: Leonardo 25528/28672 bytes flash (89.0%), 1998/2560 bytes RAM (78.0%); Uno 23390/32256 bytes flash (72.5%), 1559/2048 bytes RAM (76.1%).
- **Measured Leonardo flash delta vs phase base: +204 bytes.** A scratch `git worktree` was checked out at `ada4bdc728118bd3d0f93ea444e9b60954191ddd`, built with `pio run -e leonardo` (result: 25324/28672 bytes, 88.3%), and removed afterward (`git worktree list` confirmed back to 1 entry). The measured delta contradicts `.planning/research/SUMMARY.md`'s prediction of net-negative — the phase's four new file-static functions and the `window_start`-indexed read-back outweigh the shed call site. Recorded as measured, with no threshold claim (Phase 119's LOCK-06 owns the 3348 B headroom criterion).
- `firestarter_app`'s committed history is confirmed unmoved across the whole phase: `git -C firestarter_app log --oneline -1` still names `36a9bb5`. `git diff --exit-code ada4bdc7 HEAD -- include/messages.h include/firestarter.h` exits `0` — no new `MSG_*` id, no new `FLAG_*` value anywhere in the phase.
- `git diff --name-only ada4bdc7 HEAD | sort` lists exactly six paths across the whole phase, none FIX-04-frozen: `platformio.ini`, `src/proms/eeprom_28c.cpp`, `test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md`, `test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`, `test/native/avr/test_sdp_harness/test_sdp_harness.cpp`, `test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp`.
- A new `## FIX-04 non-regression gate (Phase 117 close)` section was appended to `RED-BASELINE.md` (purely additive — `git diff --stat` shows 213 insertions, 0 deletions), joining the RED (117-01) and GREEN (117-02) records. It carries the blob-SHA table, the five-suite result table, the full-suite arithmetic, both board figures and the signed flash delta, the host-untouched/no-new-constant results, a validation-ceiling statement citing `DS20006432B §6.6.2 p.10` / `DS20006386B p.10`, the CORRECTION 4 "66 of 84" framing, and pointers to the 117-03 and 117-04 planted-violation proofs.
- `.planning/REQUIREMENTS.md`: verified FIX-01, FIX-02, FIX-03, FIX-05, FIX-06 already `Complete`; ticked **FIX-04** and set its Traceability row to `Complete`. Six of six for Phase 117.

## Task Commits

1. **Task 1 (verification only, no file writes)** — no commit; blob-SHA and other-family suite results feed Task 2's gate record.
2. **Task 2: gate record appended to RED-BASELINE.md** — `cdf71a1` (docs, firestarter submodule)

**Plan metadata:** this SUMMARY + STATE.md/ROADMAP.md/REQUIREMENTS.md update, in the meta repo (see `<final_commit>`).

_Note: this is a firmware-submodule-only code change (the gate section); the meta repo's `REQUIREMENTS.md` FIX-04 tick and this SUMMARY are a separate commit in the meta repo._

## Files Created/Modified

- `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` — Appended `## FIX-04 non-regression gate (Phase 117 close)`, an 8-subsection record: (1) the six-row blob-SHA table with expected/observed/match columns and the exact command; (2) the five other-family suite results; (3) the full-suite arithmetic and result; (4) both board figures and the measured Leonardo flash delta with the scratch-worktree method; (5) the host-untouched proof and the exact six-path diff list; (6) the validation-ceiling statement and CORRECTION 4 framing; (7) pointers to the 117-03/117-04 planted-violation proofs; (8) a one-line gate result (PASS). Purely additive — no existing line touched, no deletion anywhere in the file (confirmed via `git diff` deletion-line count = 0).
- `.planning/REQUIREMENTS.md` — `FIX-04` checkbox ticked and its Traceability row set to `Complete`. No other line touched (confirmed via `git diff`).

## Decisions Made

- Recorded the measured Leonardo flash delta (+204 B) exactly as observed, even though it contradicts the research prediction of net-negative — the plan requires the measured number either way, with no threshold claim, and restating a prediction over a measurement would itself cross the "code as subject" discipline this phase is built on.
- Recorded `firestarter_app`'s pre-existing dirty working tree (uncommitted `.gitignore` change dated 2026-07-10, plus five pre-existing untracked files) as an explicit, named exclusion in the gate section rather than either silently ignoring it or falsely asserting a clean tree — per the plan's `submodule_commit_protocol` instruction. The load-bearing host-untouched criterion — that `firestarter_app`'s committed history (`36a9bb5`) is unmoved — does hold and is what the gate actually certifies.
- Verified FIX-01/02/03/05/06 were already ticked `Complete` in `REQUIREMENTS.md` before ticking FIX-04, per the plan's "Requirement scoping" section and the standing `.planning` memory about executors mis-marking multi-plan requirements (`reference_executors_prematurely_mark_requirements_complete.md`). Touched no other requirement row (OBS-, LOCK-, HOST-, DEVTEST-, GATE-, CLOSE- rows all confirmed unchanged via `git diff`).
- Task 1 produced no file changes (verification-only), so no commit was made for it in isolation — its results feed directly into Task 2's single gate-record commit, consistent with the plan's own file-scope (`RED-BASELINE.md` is the only file either task modifies).

## Deviations from Plan

None — plan executed exactly as written. All Task 1 and Task 2 acceptance criteria and automated verify gates passed on the first attempt; no auto-fixes, no blocking issues, no architectural questions.

## Issues Encountered

> **POST-CLOSE CORRECTION — the host-untouched claim in this SUMMARY is superseded (Phase 117 regression gate, 2026-07-28).**
>
> This SUMMARY's `zero firestarter_app files changed` / `committed history unmoved at 36a9bb5` statements were true when written and are now **false**. The phase's regression gate — run after this plan committed, before phase verification — found that Phase 117 broke **four Phase-116 host-side gates** that scan `eeprom_28c.cpp`'s source text and were keyed to pre-117 identifiers and declaration syntax:
>
> - `tests/test_sdp_table_parity.py` (3 cases) — `_extract_byte_flip_pairs`'s declaration regex requires **empty** brackets (`NAME[] =`); 117-02 changed the definition to `EEPROM_SDP_DISABLE[6] = {`, because a C++ `extern` declaration cannot name an incomplete array type. Regex matched zero times → `ValueError`.
> - `tests/test_check_no_log_in_sdp_window.py::test_checker_exits_zero_on_clean_source` — `check_no_log_in_sdp_window.py`'s emit anchor was `flash_execute_command(EEPROM_SDP_DISABLE)` (replaced by 117-02) and its wait anchor was `eeprom28c_wait_for_write(` (deleted outright by 117-03). Both tuples matched zero times → checker exit 1.
>
> **Proven Phase-117-caused, not pre-existing debt:** injecting phase-base `ada4bdc`'s `eeprom_28c.cpp` via the `FIRESTARTER_SDP_SRC` env seam flips the parity cases green, and the base source contains both anchors (emit ×1, wait ×4). Host CI runs these (`ci.yml` → `pytest --cov`; `beta-release.yml` → `pytest tests/ -v`), so the host suite and any beta cut were red. Both gates fail **closed**, never a silent pass — and Phase 116 anticipated this exact case in its own comments (*"ADD the new anchor … rather than deleting this gate"*); Phase 117's five plans simply had no task that did so. **This is a plan-coverage gap, not an implementation defect.**
>
> **Fixed under operator authorization at the regression gate:**
> - `firestarter_app@9dd11a9` — `fix(117): re-anchor Phase-116 host SDP gates onto the Phase-117 emitter`. Both anchor tuples extended **append-only** (superseded patterns retained, per the anti-hollow contract); parity bracket group widened to `\[\s*\d*\s*\]`, still requiring the trailing `=` so it matches only the initializer and never the bare `extern` declaration. Array bytes unchanged. ruff check + format clean.
> - `firestarter@f8d10a5` — the same correction appended to the committed `## FIX-04 non-regression gate` section in `RED-BASELINE.md`, so the firmware-side record is not left asserting something false.
>
> **Narrowed claim that IS true, and that the ordering invariant actually needs:** Phase 117 introduced **no wire, protocol, or behavioral change on the host** — no `MSG_*`, no `FLAG_*`, no command, no CLI surface, no serialized field. The two changed host files are source-scanning **test gates**, which cannot participate in firmware/host version skew. The firmware-before-host ordering invariant is intact. FIX-04's substantive content — the six frozen artifacts byte-identical by blob SHA, goldens not regenerated, other families' traces unchanged — is **unaffected** and still holds. `firestarter_app`'s pre-existing dirty working tree was left untouched; meta gitlink still not bumped.
>
> **Remaining known-red, proven unrelated:** `test_audit_coverage_matrix::test_golden_file_matches` is the only other host failure. It fails identically with the two gate fixes stashed away and reads the chip database, referencing no firmware path — the same stale golden carried since v1.21, needing its own regeneration commit.

`test_flash_intel_vpp` — named in the plan as the expected KNOWN-FLAKY exception — turned out not to be reachable at all under `pio test -e native` (it is absent from `[env:native]`'s `test_filter` allowlist), so the "no suite other than KNOWN-FLAKY reports FAILED/ERRORED" criterion was satisfied vacuously rather than by observing and citing an actual `[ERRORED]` line; this is recorded explicitly in the gate section rather than silently treated as identical to the plan's anticipated scenario.

## Validation Ceiling Compliance

Every claim in this SUMMARY and in the committed gate section has code as its subject: a blob SHA matched another blob SHA, a suite exited zero, a binary's flash usage was measured, a commit history's tip was unmoved. No sentence claims SDP was actually disabled on a chip, makes any claim about AT28C silicon state, or claims gh#11's symptom is gone on hardware. `0x0D` stays `UNVERIFIED`. `PROTOCOL-LEDGER`, `support_status`, and the 84-chip count were not touched — those remain Phase 122's business.

## Deferrals and Named Hooks (unchanged, restated per 117-CONTEXT.md `<deferred>`)

Per Task 2(f), the following stay deferred and were **not** acted on by this plan or this phase:

- **The end-to-end `infoic.xml` → `page_size` decode.** Still **not inserted into ROADMAP.md** — insert with `/gsd-phase` after Phase 117, noting the `.planning` memory `reference_new_milestone_phases_clear_destructive.md` warning about destructive phase operations in this repo.
- **Widening the trace recorder to a third strobe kind** (data-bus direction). D-12 took the production half only (one explicit `rurp_set_data_output()` call in plan 117-02's emitter); `RED-BASELINE.md` §"Declined widening, recorded as an open hook (D-07 scoping)" remains Phase 118's named hook and was **not** re-scoped by this plan — confirmed via `git diff` showing zero deletions inside that section.
- **SDP-F7** (datasheet verification of SDP magic addresses for AT28C040 / AT28C16 / AT28C04) — recorded UNVERIFIED per size band, unchanged.
- **SDP-F8** (`DIP24_2816` has no `static-high-pins` key, 19 chips with `static_high_mask == 0`) — the remap fix does **not** address it; this plan recorded what the trace shows and did not act on it.
- **The Unity-teardown SIGABRT root cause** (`test_flash_intel_vpp`'s pre-existing debt since Phase 17 WR-01 / Phase 20) — unattempted, unchanged.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 117 is closed: FIX-01 through FIX-06 all `Complete` in `.planning/REQUIREMENTS.md`, six of six.
- Phase 118 (Observability, OBS-01..05) is unblocked and inherits: `eeprom28c_emit_command_sequence`'s explicit `(handle, sequence, length)` signature (reusable without a second refactor); the named Phase-118 hook on widening the trace recorder to a third strobe kind; the KNOWN-FLAKY `test_flash_intel_vpp` root-cause deferral.
- Phase 119 (SDP Lock, LOCK-01..06) is unblocked and inherits: `EEPROM_SDP_DISABLE`'s external linkage (plan 117-02); the measured Leonardo flash figure (25528/28672 B, +204 B vs phase base) as its LOCK-06 headroom-criterion baseline.
- No blockers. `firestarter/src/` remains confined to `eeprom_28c.cpp` across the whole phase; this plan's only firmware-tree write is the appended, purely-additive `RED-BASELINE.md` gate section.

---
*Phase: 117-fix-remap-aware-0x0d-emitter-honest-completion-signal*
*Completed: 2026-07-28*

## Self-Check: PASSED

- FOUND: `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md`
- FOUND: `.planning/REQUIREMENTS.md`
- FOUND: `.planning/phases/117-fix-remap-aware-0x0d-emitter-honest-completion-signal/117-05-SUMMARY.md`
- FOUND: commit `cdf71a1` in `firestarter` submodule history
