---
phase: 121-dev-test-fix-gates-docs-redesign
verified: 2026-07-29T00:00:00Z
status: passed
score: 10/10 success criteria verified (9/9 must-have requirements confirmed live)
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 121: `dev test` FIX + GATES + DOCS + REDESIGN Verification Report

**Phase Goal:** Community-facing evidence about this milestone's work is trustworthy before it's ever
collected — `dev test` stops falsely reporting a phantom erase pass on `0x0D` chips, the new
SDP-capability logic has a proven non-hollow gate, the documentation matches what the code actually
does, and the operator's broader `dev test` redesign (no flags, UV-scoped destructiveness with a
stop-and-ask partial-write mode, ask-to-file-an-issue with dedup, `gh`-first submission) lands.

**Verified:** 2026-07-29
**Status:** passed
**Re-verification:** No — initial verification

## Method

This report does not trust `SUMMARY.md`/`121-NONREGRESSION.md` claims. Every truth below was
re-derived directly against the live `firestarter_app`/`firestarter` submodule trees at their
current tip commits (`firestarter_app@c3c9424`, `firestarter@48c36e5`, both clean apart from the
named pre-existing dirt), independently of any plan's own self-report. Test suite / native-suite
green (1134/0, 141/141) was independently re-run by the orchestrator before dispatch and is treated
as established per the task's instructions; this report re-derives the nine requirement-level
claims and the phase's own three adjudication points from source.

## Goal Achievement

### Observable Truths — the ten ROADMAP Success Criteria

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `dev test` on a `0x0D` chip shows erase `NA` with a named reason, never `OK` | ✓ VERIFIED | Live `derive_plan('AT28C256', db, write_scope='full')`: `erase` step `supported=False`, `reason="protocol 0x0D (28C family) has no erase operation; each page write auto-erases internally"` — no `FLAG_CAN_ERASE` mention, matching the Claude's-Discretion constraint that the reason must name the family fact, not the flag mechanism. `database.py:convert_to_programmer` confirmed to exclude `algorithm in {5, 13}` from `FLAG_CAN_ERASE` with the reversal comment in place. |
| 2 | Satisfied by Phase 119, landed early | ✓ N/A (out of this phase's scope by design) | ROADMAP explicitly marks this criterion satisfied upstream; Phase 121 owns only the host half, covered by #1. |
| 3 | Capability-gate AST check has a companion pytest proving the gate fails on a planted violation | ✓ VERIFIED | `python3 tools/check_sdp_capability_invariants.py` on real `sdp_capability.py` → `PASS: ... 0 permit-by-default, 0 widenable-allow-set` (exit 0). Run against `FIRESTARTER_SDP_CAPABILITY_SRC=tests/fixtures/planted_permit_by_default.py` → `FAIL: 2 permit-by-default violation(s)` (exit 1). Run against `tests/fixtures/planted_widenable_allowset.py` → `FAIL: 1 widenable-allow-set violation(s)` (exit 1). Both planted fixtures independently produce a real, differently-worded failure — not hollow. |
| 4 | Named docs no longer describe pre-fix SDP behavior; state `0x0D` has no erase | ✓ VERIFIED | All 8 named docs exist and were read directly: `firestarter/doc/PROTOCOLS.md` §1.6 (explicit "no erase operation at all" + full corrected SDP sequence description + `FLAG_CAN_ERASE` cleared explanation), `firestarter/CLAUDE.md` (§"Protocol 0x0D notes"), `firestarter_app/doc/lockable-proms.md` (§17 AT28C16 row corrected to "No — no SDP command decoder at all"), `firestarter_app/doc/protocol-id.md` (0x0D row states "no erase operation at all"), both READMEs (explicit "dev test writes to the chip" warnings), plus the D-17-widened `doc/community-validation.md` and `doc/beta-testing-install.md` (both carry the always-writes warning and the `write-partial` ladder-tag explanation). |
| 5 | Full non-regression set green (native, `check_dispatch.py`, host pytest, ruff/format at CI py3.9/3.11 targets, `diff_db.py` identity) | ✓ VERIFIED | Independently re-spot-checked: `check_dispatch.py` → PASS (746 chips, 0 regressions); `diff_db.py` → PASS, "still exactly 2 explained changes" (`PGSZ_PAGE_SIZE`, 0 new, 0 removed); `check_devtest_orchestrator.py` → PASS. Native 141/141 and host pytest 1134/0 already independently re-run by the orchestrator per task framing (not re-duplicated here to avoid a redundant full-suite run). |
| 6 | `dev test` takes no flags at all | ✓ VERIFIED | Live `inspect.signature(cli_handlers.dev_test.callback)` → `(app: 'AppContext', chip: str) -> None`; `dev_test.params` → `['chip']` only. `CliRunner` invocation of `dev test SOMECHIP --destructive` / `--output-dir .` / `-y` / `--yes` / `--submit` each returns exit code 2 with `Error: No such option: ...`. |
| 7 | Destructiveness scoped to UV-erasable EPROMs only, on an explicit structural axis | ✓ VERIFIED | Live measurement against the real 746-entry `chip_database.json`: `is_uv_eprom(full)` (keyed on `electrical-type == "UV-EPROM"`) matches exactly **301/301** UV parts; the prior `algorithm==0x0B` execution-time proxy matches only **32/301** — reproducing the RESEARCH-cited gap exactly. `_resolve_write_scope` reads `_is_uv_eprom(app, chip)` from `app.db.get_eprom(chip)` (the full DB dict), never a `resolve_chip` programmer dict. |
| 8 | Stop-and-ask third mode: yes → full device, no → small region | ✓ VERIFIED | `_resolve_write_scope` source read directly: not-UV → `"full"`, no prompt; UV + non-interactive → `"partial"`, no prompt (D-03); UV + interactive → asks, `Confirm.ask(..., default=False)`, yes→`"full"`, no→`"partial"`. `OP_WRITE_PARTIAL = "write-partial"` confirmed present in the live `_DESTRUCTIVE_OPS` frozenset (`{OP_WRITE, OP_WRITE_PARTIAL, OP_ERASE}`), so the chip-ID/destructive gate covers it. `tests/test_dev_test_cmd.py -k TestUVOnlyStopAndAsk` (4 legs) pass live. |
| 9 | Every run asks whether to file an issue; dedup check runs first | ✓ VERIFIED | `submit_report` source read directly: Step 3 calls `find_prior_report_fn(fingerprint, run_fn=run_fn)` immediately after building the sanitized body/title and *before* the TTY branch — runs on every reached path, TTY or not. The off-TTY branch (Step 4) prints the dedup outcome and returns without ever calling `confirm_fn`. The interactive branch (Step 5) always asks — a duplicate asks to comment, a clean/unknown result asks the normal filing question, worded as "you appear to have already reported this," never a certainty. |
| 10 | `gh`-first submission; negative argv for `--label` et al. | ✓ VERIFIED | `tests/test_submit.py` deny-set constant (lines ~409-435) enumerates long *and* short forms: `--label`/`-l` (implied), `--assignee`/`-a`, `--milestone`/`-m`, `--project`/`-p` for `gh issue create`, plus `--delete-last`/`--edit-last`/`--yes`/`-w`/`--web`/`-e`/`--editor` for the new `comment_via_gh` path. `python3 -m pytest tests/test_submit.py -q` → 96/96 pass live. |

**Score:** 10/10 ROADMAP success criteria verified (criterion 2 verified as correctly out-of-scope-here).

### Requirement Rows — independent re-verification (not trusting SUMMARY/REQUIREMENTS.md ticks)

| Requirement | Status | Independent evidence |
|---|---|---|
| DEVTEST-01 | ✓ SATISFIED | See truth #1. `database.py`'s `FLAG_CAN_ERASE` exclusion for `algorithm in {5, 13}` read directly from source with the reversal comment; live `derive_plan` output confirms the NA erase step and family-fact reason. `tests/test_chip_test.py -k devtest01` (2 tests) pass live. |
| DEVTEST-02 | ✓ SATISFIED | See truth #6 — signature and each flag's `Error: No such option` reproduced live in this session. |
| DEVTEST-03 | ✓ SATISFIED | See truth #7 — 301/301 vs 32/301 reproduced live against the actual 746-entry DB in this session, not read from a SUMMARY figure. |
| DEVTEST-04 | ✓ SATISFIED | See truth #8 — `_resolve_write_scope`'s three branches read directly from source; `OP_WRITE_PARTIAL` membership in `_DESTRUCTIVE_OPS` confirmed by grep of the live file; `TestUVOnlyStopAndAsk` (4 legs) re-run live, all pass. |
| DEVTEST-05 | ✓ SATISFIED | See truth #9 — `submit_report`'s step order read directly from source (dedup call precedes the TTY branch on every path). |
| DEVTEST-06 | ✓ SATISFIED | See truth #10 — deny-set constants and `test_submit.py` (96/96) re-run live. |
| GATE-01 | ✓ SATISFIED | See truth #3 — `check_sdp_capability_invariants.py` re-run live against real source (exit 0) and both planted fixtures (exit 1 each, differently-worded failures). |
| GATE-02 | ✓ SATISFIED | See truth #4 — all 8 named docs read directly, each carrying the required `0x0D`-has-no-erase / always-writes statements. |
| GATE-03 | ✓ SATISFIED | `check_dispatch.py`, `check_devtest_orchestrator.py`, `diff_db.py` re-run live (all PASS); native 141/141 and host pytest 1134/0 already independently confirmed by the orchestrator per the task's "already established" list, treated as current. Both sub-repo trees clean (`git status --porcelain`) apart from the named pre-existing dirt. |

**All nine phase-owned requirement rows independently confirmed SATISFIED against the live tree — none ticked on a claim that does not hold.**

### The Three Adjudication Points

**1. Plan 121-12's "a generated firmware header changes" premise.**
Confirmed factually wrong about the *mechanism*, but the underlying *intent* (D-15's symmetric
honesty caveat on both SDP report lines) was fully and correctly satisfied. Verified directly:
`firestarter/include/messages.h` carries only numeric `#define MSG_INFO_SDP_UNLOCK_DONE_US 0x5F`
— zero diff confirmed via `git diff 30b1c40 8c2e177 -- include/messages.h` (empty). The format
string change landed correctly in `tools/catalog/messages.toml` (`git show 8c2e177` shows the
7-line diff changing the format string) and regenerated into `firestarter_app/firestarter/messages.py`
(`format="SDP unlock sequence emitted in %lu us; protection state is not readable"`, confirmed live
by grep). This is the same class of "stated mechanism narrower than intent" seen repeatedly this
milestone (LOCK-04, LOCK-06, HOST-04) — **verdict: does not undermine D-15's intent; it is a wrong
prediction about which artifact would carry the text, correctly self-corrected in the commit
message itself** ("`include/messages.h` unaffected (id defines only; format strings are decoded
host-side, not embedded in the C++ header)"). Not a gap.

**2. The six requirement rows ticked by Plan 121-14 (GATE-03, DEVTEST-01/02/03/04, GATE-01) contrary
to the plan's own literal "Tick GATE-03 only" line.**
Each of the six was independently re-derived from the live tree in this verification session
(above table) — not re-read from any SUMMARY or from `121-14`'s own claim. **All six hold.** The
orchestrator-cited rationale (commit `2492154` reverted plan `121-08`'s premature `DEVTEST-01` tick
and left explicit REQUIREMENTS.md prose delegating re-closure to Plan `121-14`) is corroborated:
`git log` shows `2492154 docs(phase-121): revert premature DEVTEST-01 tick — 121-14 owns requirement
re-verification` sitting between wave 5 and wave 6 commits, consistent with the timeline. **Verdict:
the six ticks are legitimate — a requirement ticked on a claim that does not hold would be worse
than an unticked one, but in this case every claim independently holds.**

**3. Plan 121-14's self-reported live-ledger mutation, "reverted before committing."**
Investigated directly rather than taken on faith. `git log --oneline -- .planning/v1.3-defect-coverage-ids.json`
shows the ledger's last commit is `e819d11` (a Phase-11-era commit, long before this milestone) —
**no commit anywhere in Phase 121's range touches this file**, and `git diff HEAD -- .planning/v1.3-defect-coverage-ids.json`
is empty. The ledger genuinely has 78 keys in its committed (unmutated) state.

**However, the literal instruction "confirm no commit in this phase contains `DEFECT-COV-78` through
`DEFECT-COV-95`" does NOT hold** — those exact identifiers **do** appear in the committed golden
(`tests/golden/v1.3-COVERAGE-MATRIX.md`), and appear starting at the very first phase commit,
`098702c` (Plan 121-01's regen), *before* any DEVTEST code existed in the tree. Traced the full
causality: `git log --oneline 96e0622..HEAD -- tests/golden/v1.3-COVERAGE-MATRIX.md` shows **exactly
one** commit touched that file in the entire phase (`098702c`), and `git diff 098702c HEAD --
tests/golden/v1.3-COVERAGE-MATRIX.md` is empty — confirming Task 2's "second regen proven
byte-identical" claim independently. The `DEFECT-COV-78..95` renumbering is a byproduct of Plan
98's DIP32_STD → DIP32_27C020 pinout-split (cited in `098702c`'s own commit message) recomputing
cluster groupings against the pre-existing, unmutated 78-entry ledger — **not** a leak of Plan
121-14's later scratch-copy mistake into any commit.

**Verdict: the substance of the concern (did a mutated/inflated ledger leak into a commit) is
answered NO — the ledger is provably unmutated across the whole phase and only one legitimate,
pre-DEVTEST regeneration touched the golden.** The literal grep instruction was based on an
imprecise premise (assuming `78-95` was necessarily 121-14-mistake-specific); this is recorded as a
**WARNING-level note, not a BLOCKER**, since independent forensic tracing fully explains the
provenance and finds no tampering.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter_app/tools/check_sdp_capability_invariants.py` | GATE-01 AST gate | ✓ VERIFIED | Exists, exit 0 on real source, exit 1 on both planted fixtures with distinct violation messages |
| `firestarter_app/tests/fixtures/planted_permit_by_default.py` | Planted Class-1 violation | ✓ VERIFIED | Present; trips the gate with 2 named violations |
| `firestarter_app/tests/fixtures/planted_widenable_allowset.py` | Planted Class-2 violation | ✓ VERIFIED | Present; trips the gate with 1 named violation |
| `firestarter_app/firestarter/database.py` | `FLAG_CAN_ERASE` cleared for 0x0D | ✓ VERIFIED | `algorithm in {5, 13}` exclusion present with reversal comment |
| `firestarter_app/firestarter/chip_test.py` | `OP_WRITE_PARTIAL`, `is_uv_eprom`, `_write_region_for` read-not-guess | ✓ VERIFIED | All three present and correctly wired |
| `firestarter_app/firestarter/cli_handlers.py` | Zero-option `dev_test`, `_resolve_write_scope`, always-writes notice | ✓ VERIFIED | Signature, notice text, and branch logic all confirmed live |
| `firestarter_app/firestarter/submit.py` | `find_prior_report`, `comment_via_gh`, restructured `submit_report` | ✓ VERIFIED | Dedup-first step order confirmed by direct source read |
| 8 named docs (both sub-repos) | GATE-02 corrections | ✓ VERIFIED | All 8 exist with required content |
| `firestarter/tools/catalog/messages.toml` + mirrors | D-15 caveat symmetry | ✓ VERIFIED | `messages.toml` diff correct; `messages.py` regenerated correctly; `messages.h` correctly zero-diff (id-only header) |
| `.planning/phases/121-.../121-NONREGRESSION.md` | Phase audit record | ✓ VERIFIED | Present, eight-section shape, validation-ceiling review clean |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `database.py:convert_to_programmer` | `chip_test.py:derive_plan` | `FLAG_CAN_ERASE` bit read by `derive_plan`'s existing generic NA-erase branch | ✓ WIRED | Live `derive_plan` output shows the erase step correctly NA with the family-fact reason, no flag-name leakage |
| `cli_handlers.py:dev_test` | `chip_test.py:derive_plan` | `write_scope=` kwarg carrying `_resolve_write_scope`'s decision | ✓ WIRED | Source read confirms `derive_plan(chip, app.db, write_scope=write_scope)` |
| `chip_test.py:_DESTRUCTIVE_OPS` | `chip_test.py` chip-ID gate | `OP_WRITE_PARTIAL` membership | ✓ WIRED | Confirmed present in the live frozenset; `TestUVOnlyStopAndAsk` legs pass |
| `submit.py:submit_report` | `submit.py:find_prior_report` | Called before the TTY branch on every path | ✓ WIRED | Source read confirms ordering |
| `tools/catalog/messages.toml` | `firestarter_app/firestarter/messages.py` | codegen mirror regeneration | ✓ WIRED | Text confirmed identical in intent between the two |

### Anti-Patterns Found

Scanned every non-test `.py` file touched by the phase (`git diff --name-only 96e0622..HEAD`) for
`TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`/"not yet implemented"/"coming soon". One match: a
`ProtocolNotImplementedError` message in `cli_handlers.py` containing "not yet implemented in the
firmware" — confirmed via `git blame` to be a pre-existing line from commit `711aa939` (2026-06-11,
unrelated Phase-38-era work), not touched by this phase. No debt markers found in any file this
phase actually changed.

### Requirements Coverage

All nine phase-owned requirement ids (DEVTEST-01..06, GATE-01..03) are SATISFIED per the table
above. `CLOSE-01`/`02`/`03` correctly remain unticked and Pending (Phase 122 scope) — confirmed via
direct read of `REQUIREMENTS.md`. No orphaned requirements found for this phase.

### Validation Ceiling

No AT28C part was on the bench during this phase. `0x0D` correctly stays `UNVERIFIED`; zero chips
changed `support_status` (confirmed live: `diff_db.py`'s only 2 changed chips are the unrelated
Phase-94 `page_size` addition on `W29C020`/`W29C040` families); the 84-chip count is unchanged
(untouched by any Phase-121 work). No affirmative claim anywhere in the phase's docs or artifacts
states SDP was demonstrated on real silicon — confirmed by grep of the phase directory and of
`121-NONREGRESSION.md`'s own validation-ceiling review. Absence of silicon validation is the
correct, expected outcome and is not reported as a gap.

### Human Verification Required

None. Every truth in this phase is either a code-structural fact (options removed, flags cleared,
frozenset membership, AST gate behavior) or a documentation-content fact, all independently
checkable and checked without a live board.

## Gaps Summary

No gaps found. All ten ROADMAP success criteria hold, all nine requirement rows independently
re-verified against the live tree, and all three adjudication points investigated to a clear
verdict:

1. Plan 121-12's mechanism prediction was wrong but its intent was fully satisfied — not a gap.
2. The six requirement ticks by Plan 121-14 are legitimate — each independently re-verified true.
3. The `DEFECT-COV-78..95` literal check does not hold as worded, but forensic tracing shows this
   is a benign byproduct of the one authorized, pre-DEVTEST golden regeneration against a
   provably-unmutated ledger — not evidence of a leaked mistake. Recorded here as a WARNING-level
   note for the record, not a BLOCKER, since the substantive integrity question (did anything
   tainted reach a commit) is answered NO with direct evidence.

Phase goal achieved: community-facing `dev test` evidence is now trustworthy (no phantom erase
pass), the SDP-capability gate is proven non-hollow, the 8 named docs match reality, and all six
elements of the operator's `dev test` redesign are live and independently confirmed. Ready to
proceed to Phase 122.

---

*Verified: 2026-07-29*
*Verifier: Claude (gsd-verifier)*
