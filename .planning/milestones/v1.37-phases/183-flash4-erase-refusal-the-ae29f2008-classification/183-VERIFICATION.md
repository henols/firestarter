---
phase: 183-flash4-erase-refusal-the-ae29f2008-classification
verified: 2026-09-11T00:00:00Z
status: passed
score: 18/18 must-haves verified
covered_files:
  - .planning/REQUIREMENTS.md
  - .planning/ROADMAP.md
  - .planning/notes/ae29f2008-classification-verdict.md
  - .planning/phases/183-flash4-erase-refusal-the-ae29f2008-classification/183-01-PLAN.md
  - .planning/phases/183-flash4-erase-refusal-the-ae29f2008-classification/183-01-SUMMARY.md
  - .planning/phases/183-flash4-erase-refusal-the-ae29f2008-classification/183-02-PLAN.md
  - .planning/phases/183-flash4-erase-refusal-the-ae29f2008-classification/183-02-SUMMARY.md
  - .planning/phases/183-flash4-erase-refusal-the-ae29f2008-classification/183-03-PLAN.md
  - .planning/phases/183-flash4-erase-refusal-the-ae29f2008-classification/183-03-SUMMARY.md
  - .planning/phases/183-flash4-erase-refusal-the-ae29f2008-classification/183-04-PLAN.md
  - .planning/phases/183-flash4-erase-refusal-the-ae29f2008-classification/183-04-SUMMARY.md
  - .planning/phases/183-flash4-erase-refusal-the-ae29f2008-classification/183-05-PLAN.md
  - .planning/phases/183-flash4-erase-refusal-the-ae29f2008-classification/183-05-SUMMARY.md
  - .planning/phases/183-flash4-erase-refusal-the-ae29f2008-classification/183-06-PLAN.md
  - .planning/phases/183-flash4-erase-refusal-the-ae29f2008-classification/183-06-SUMMARY.md
  - .planning/phases/183-flash4-erase-refusal-the-ae29f2008-classification/183-REVIEW.md
  - .planning/phases/183-flash4-erase-refusal-the-ae29f2008-classification/deferred-items.md
  # Submodule files reviewed but not fingerprintable by verification.fingerprint (root-escape guard
  # rejects paths outside the meta-repo git root); pinned instead by submodule HEAD commits below.
covered_digest: "v1:sha256:4ef9dd07bc7c4af748ff88c224d68eb5a695c724bfd72553c93b22dbd77b58e7"
submodule_heads_reviewed:
  firestarter: e44ba6f2a4971ad97a8f31e3696593e898aa935f
  firestarter_app: 5a915ea432f8bf013da67df487fc6ab43e6db908
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 17/18
  gaps_closed:
    - "ROADMAP.md Phase 183 success criterion 2 accurately describes how the SAFE-07 mechanism was chosen"
  gaps_remaining: []
  regressions: []
human_verification: []
---

# Phase 183: Flash4 Erase Refusal & the AE29F2008 Classification Verification Report

**Phase Goal:** A refusal that is right for a reason names the part — the reason is recorded and
answered to the reporter in Phase 187's REPLY-03, not printed — and the open question behind gh#62 —
whether this part is classified correctly at all — gets a recorded answer instead of an assumption.
**Verified:** 2026-09-11 (re-verification)
**Status:** passed
**Re-verification:** Yes — after gap closure (ROADMAP.md Phase 183 criterion 2 amended in commit
`dc309bf8`, closing the single gap from the initial pass)

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `firestarter erase <flash4 part>` prints exactly one line, `Erase not supported for <EPROM>`, naming the part, with no cause and no alternative | ✓ VERIFIED | `firestarter_app/firestarter/flash4_erase_gate.py::refusal_text`; `cli_handlers.erase` calls it; live invocation confirmed `Erase not supported for SST39SF040`; `tests/test_flash4_erase_gate.py::test_refusal_text_is_one_line_and_carries_no_forbidden_content` passes (22/22 gate tests re-run) |
| 2 | The refusal fires before the serial port opens — no `Connecting` line, `erase_eprom` never called | ✓ VERIFIED | `cli_handlers.py` diff: gate call sits between `resolve_chip` (no I/O) and `jp5_gate`/`app.eprom_operator.erase_eprom`; `resolve_chip`'s own docstring and body confirm no serial byte is emitted; integration test `test_cli_erase_on_flash4_part_refuses_pre_connect_with_one_line` passes |
| 3 | Default exit 1; `--ignore-unsupported` flips to exit 0 only, byte-identical printed line on both legs | ✓ VERIFIED | `test_cli_erase_ignore_unsupported_exits_0_with_byte_identical_output` passes; re-ran full `test_flash4_erase_gate.py` (22/22) |
| 4 | `flash4_erase_gate.py` is a pure, import-pure predicate module, sibling to `jp5_gate.py`/`sdp_capability.py`, no part-number literal | ✓ VERIFIED | Read module in full: docstrings only, imports limited to `__future__`/`typing`, no `#` comments, no literal part numbers; `test_module_source_contains_no_shipped_part_number_literal` passes |
| 5 | The predicate keys on the same `algorithm` value `database.convert_to_programmer`'s `algo not in (5,)` exclusion reads | ✓ VERIFIED | `flash4_erase_gate.FLASH4_PROTOCOL_ID = 5`; `database.py:581` `if algo not in (5,): simple_flags \|= FLAG_CAN_ERASE`; `test_predicate_matches_real_database_algorithm_5_rows_exactly` passes, iterating every shipped part number |
| 6 | The gate fails OPEN on missing/None/empty/key-less input | ✓ VERIFIED | `is_flash4`'s body: `if not programmer_data: return False`; `test_is_flash4_fails_open_on_absent_evidence` (parametrized) passes |
| 7 | A non-algorithm-5 part still reaches `erase_eprom` — no scope widening | ✓ VERIFIED | `test_cli_erase_on_non_flash4_part_still_reaches_operator` passes |
| 8 | No mention of `--force`/forged-identity workaround anywhere in the refusal path | ✓ VERIFIED | `refusal_text` returns only `"Erase not supported for {chip_name}"`; forbidden-substring test passes; `/usr/bin/grep` of the module and handler diff shows no `force` token in the refusal path |
| 9 | SAFE-07: all three candidate mechanisms (M1/M2/M3) priced, M1 measured via a reverted probe, M2/M3 recorded as structural zeros with reasons, none omitted | ✓ VERIFIED | `183-01-SUMMARY.md`'s three-row pricing table; probe reverted (`git status --porcelain` clean in `firestarter`, confirmed); M1 = +12 B flash / +0 B RAM on all three AVR targets |
| 10 | The firmware backstop (`eprom_erase`'s `FLAG_CAN_ERASE` refusal in `eprom_operations.cpp`) is byte-unchanged | ✓ VERIFIED | `git diff origin/beta HEAD -- src/eprom_operations.cpp` in `firestarter` is empty |
| 11 | `configure_flash_5v_page`'s `CMD_ERASE` arm and `flash_5v_page_erase_execute` are deleted at all four sites (fwd decl, switch arm, erase-on-write block, definition) | ✓ VERIFIED | `git diff origin/beta HEAD -- src/proms/flash_5v_page.cpp` shows exactly these four deletions and nothing else added back |
| 12 | Even with `FLAG_CAN_ERASE` wrongly set, one `flash_5v_page_write_init` call energises no VPP rail — proved by a test, not just by deletion | ✓ VERIFIED (behavioral) | Named test `test_5v_page_write_init_no_vpp_with_flag_can_erase_set` re-run in isolation (`pio test -e native -f 'native/avr/test_val_5v_page'`) — 15/15 pass, including this case; RED-before/GREEN-after evidence independently corroborated in `183-04-SUMMARY.md` |
| 13 | `test_val_5v_page.cpp` carries no reference to the deleted symbol or a stale line range | ✓ VERIFIED | `/usr/bin/grep -n 'flash_5v_page_erase_execute\|flash_5v_page.cpp:196-231\|with_flag_clear'` — no matches |
| 14 | Disposition (a): `flash_5v_page_write_init` and its `firestarter_operation_init` assignment are KEPT (not deleted, pointer not nulled) | ✓ VERIFIED | Diff shows the function retained with only the erase-on-write block removed; the guard `if (!is_operation_in_progress(handle))` and its `RESPONSE_CODE_ERROR` return are intact |
| 15 | D-13's unreachability statement is precise — the arm's *assignment* runs every INIT, only the installed *function pointer* is never called; never "the arm never runs" | ✓ VERIFIED | `183-06-SUMMARY.md` Adjudication 4 states it in exactly the required form; `/usr/bin/grep -rn "the arm never runs"` across the phase's own artifacts and both submodules returns no instance of the forbidden phrasing in any delivered record |
| 16 | Native case count moves 184→185 on both `native` and `native_nodevtools`, recorded as a second Phase 185 input | ✓ VERIFIED | Re-ran `pio test -e native`: 185/185; matches orchestrator's independent `native_nodevtools` re-measurement; `ROADMAP.md` Phase 185 `**Depends on:**` line names both the flash shrink and the 184→185 case count |
| 17 | SAFE-09 verdict is stated as equivalence-based, never as a direct AE29F2008 datasheet reading; the equivalence chain (upstream `infoic.xml` row, shared `chip_id` with W29C020C, W29C020C datasheet facts) is present; `chip_database.json`/`build_db.py` byte-unchanged | ✓ VERIFIED | `.planning/notes/ae29f2008-classification-verdict.md` states plainly: "This verdict is equivalence-based, not a direct datasheet reading... No primary AE29F2008 datasheet was retrieved or read"; `git diff --stat 4adf719 HEAD -- firestarter/data/chip_database.json tools/build_db.py tools/DECODE-NOTES.md` in `firestarter_app` is empty |
| 18 | ROADMAP.md Phase 183 success criterion 2 accurately describes how the SAFE-07 mechanism was chosen | ✓ VERIFIED | Amended in commit `dc309bf8`: "All three candidate mechanisms carry a firmware-flash figure — M1 a measured one, M2 and M3 structural zeros stated with the reason the zero is structural — and the record states the grounds the choice was actually made on. **AMENDED by Phase 183 alongside criterion 1 (D-08):** the original wording said 'both' of two mechanisms and that the choice cites those figures. Pricing found no flash cliff (M1 is +12 B on every target), so the figures did not decide it; M3 was chosen on D-02 grounds..." Names all three candidates, correctly marks M1 measured vs. M2/M3 structural zero, states D-02 (pre-connect) as the actual deciding ground, quotes the original superseded wording verbatim, and cites `183-01-SUMMARY.md` as the source — matching REQUIREMENTS.md's SAFE-07 Trace note verbatim in substance and 183-01-SUMMARY.md's own words ("The flash figures did not decide this choice... M3 was chosen on D-02 grounds") exactly. Reads as a transparent relocation (states what changed and why), not a quiet rewrite — same discipline already applied to criterion 1 and the Goal by 183-06 |

**Score:** 18/18 truths verified (0 present, behavior-unverified)

### Requirements Amendment Integrity (SAFE-06/D-07/D-08/D-09) — scrutinized closely

`.planning/REQUIREMENTS.md` § SAFE-06 and `.planning/ROADMAP.md` Phase 183's Goal and criterion 1 were
both checked against the amendment discipline the task called for: does the amendment read as a
**relocation** (pointing at where the cause and alternative went) or a **quiet scope cut**?

- REQUIREMENTS.md SAFE-06: "**AMENDED by Phase 183 under D-07/D-08:** the operator chose this
  one-line shape knowingly, with the conflict against this requirement's original wording — which had
  promised the refusal state its cause and its alternative — stated on the record before the choice
  was made. The cause and the alternative are not dropped; they move to Phase 187's REPLY-03 (D-09)."
  This names the original promise, names the conflict, and names the destination. **Relocation, not
  scope cut — confirmed.**
- ROADMAP.md Phase 183 Goal (amended): "...the reason is recorded and answered to the reporter in
  Phase 187's REPLY-03, not printed..." — same discipline, same destination named.
- ROADMAP.md Phase 183 criterion 1 (amended): quotes the shipped `Erase not supported for <EPROM>`
  line shape and explicitly states "the cause and the alternative are answered in Phase 187's REPLY-03
  (D-09), not printed here." **Confirmed.**

This amendment integrity check passes cleanly on all three passages. The one place amendment
discipline was NOT applied — criterion 2 — is captured as the phase's single gap above, not folded
into this section, because it is a different criterion (the mechanism-pricing one, not SAFE-06's
wording).

### Code Review Dispositions (WR-01/WR-02/WR-03) — judged

- **WR-01** (false universal claim in `check_erase_no_vpp.py`'s rewritten rationale): **FIXED, confirmed
  in the tree.** The rationale now explicitly names `eprom_internal_erase()` in `eprom.cpp` as the
  structurally similar pattern that does still exist, exactly matching the review's suggested fix. Read
  the live paragraph (`firestarter/scripts/check_erase_no_vpp.py` lines ~26-40) — the false
  "nothing... anywhere in the codebase" claim is gone.
- **WR-02** (`flash_5v_page_write_init` now dead branching around an empty body): **left in place,
  disposition defensible.** `183-04`'s own must_have text requires "the immediately adjacent
  `if (!is_operation_in_progress(handle))` guard and its `RESPONSE_CODE_ERROR` early return intact —
  only the `FLAG_CAN_ERASE` block is removed, not the block it was nested beside." Collapsing the
  function to `(void)handle;` per WR-02's suggested fix would satisfy the review comment but would also
  touch the guard structure the phase's own must_have pins in place; leaving it is a legitimate,
  disclosed trade-off (a maintainer readability nit vs. a phase must_have), not a hidden defect — it
  changes no externally observable behavior, confirmed by the review itself.
- **WR-03** (unused `rurp_pinout.h` include): **deferred, disposition defensible.** Confirmed by
  independent grep — no remaining reference to any `rurp_pinout.h` symbol in `flash_5v_page.cpp`.
  Removing the include would not change the measured flash figures (an unused include costs nothing
  in the object file), so the stated reason for deferring ("removing it would change the flash figures
  183-05 just measured") is not itself precisely accurate — but the deferral causes no harm: it is a
  one-line, zero-risk cleanup left for a future pass, and 183-05's shrink figures are correct
  regardless of whether this include is ever removed. Not a gap; recorded here as an observation only.

### GSD-Identifier and Comment-Discipline Sweep (`/workspaces/CLAUDE.md` hard rule)

Diffed every file this phase added or changed in both submodules (`git diff origin/beta HEAD` in
`firestarter`; `git diff 4adf719 HEAD` in `firestarter_app`) for `SAFE-0`, `D-0`/`D-1`/`D-2`x,
`Phase 183`, `183-0[1-6]` in **added** lines only: zero matches in either repository. The new
`flash4_erase_gate.py` module is docstring-only (no `#` comments). Two explanatory (non-GSD) block
comments were added to `test_val_5v_page.cpp` describing test factory intent; this matches the
file's own pre-existing convention (extensive block comments throughout, predating this phase) and
carries no GSD identifier — noted here for completeness, not treated as a violation of the phase's
own must_haves, which scope the no-GSD-identifier check to the files this phase changed.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter_app/firestarter/flash4_erase_gate.py` | Pure predicate, `FLASH4_PROTOCOL_ID`/`is_flash4`/`refusal_text` | ✓ VERIFIED | 79 lines, exports match exactly, import-pure, no comments |
| `firestarter_app/tests/test_flash4_erase_gate.py` | Board-free proof | ✓ VERIFIED | 273 lines, 22 tests, all pass |
| `firestarter_app/firestarter/cli_handlers.py` | Pre-connect gate + `--ignore-unsupported` | ✓ VERIFIED | Wired between `resolve_chip` and `jp5_gate`/`erase_eprom` |
| `firestarter/src/proms/flash_5v_page.cpp` | 12V erase path removed | ✓ VERIFIED | All 4 sites confirmed deleted via diff |
| `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` | Non-vacuous no-VPP proof | ✓ VERIFIED | New case passes in isolation; stale refs removed |
| `.planning/notes/ae29f2008-classification-verdict.md` | SAFE-09 record | ✓ VERIFIED | 220 lines, equivalence-based framing explicit, evidence chain present |
| `.planning/REQUIREMENTS.md` | SAFE-06 amended, SAFE-06..09 complete | ✓ VERIFIED | Amendment reads as relocation; all four checkboxes `[x]` with Trace pointers |
| `.planning/ROADMAP.md` | Phase 183 Goal/criterion 1/criterion 2 amended, Phase 185 dependency added | ✓ VERIFIED | Goal, criterion 1, and criterion 2 (commit `dc309bf8`) all correctly amended, relocation-style |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `cli_handlers.erase` | `flash4_erase_gate.is_flash4` | pre-connect call between `resolve_chip` and `erase_eprom` | ✓ WIRED | Confirmed by diff and by passing integration tests |
| `flash4_erase_gate.py` | `database.py` | shared `algorithm`/`algo not in (5,)` source of truth | ✓ WIRED | `FLASH4_PROTOCOL_ID = 5` matches `database.py:581` exactly |
| `flash_5v_page.cpp` | `operation_utils.cpp` | `CMD_ERASE` on `0x05` now falls to switch default, refused by NULL-`main` guard | ✓ WIRED | Confirmed by reading the deletion diff; `eprom_erase`'s `FLAG_CAN_ERASE` check returns before the pointer is ever dereferenced |
| `.planning/notes/ae29f2008-classification-verdict.md` | `build_db.py` | `classify()`'s flash-family pass-through | ✓ WIRED | Verdict cites `tools/build_db.py:356` `if proto_id in {0x05, 0x06, 0x0D, 0x10}:`, re-verified live |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Refusal text shape | `python -c "from firestarter.flash4_erase_gate import refusal_text; print(refusal_text('sst39sf040'))"` | `Erase not supported for SST39SF040` | ✓ PASS |
| Fail-open on absent evidence | `is_flash4(None)`, `is_flash4({})` | both `False` | ✓ PASS |
| Fail-correct on algorithm 5 | `is_flash4({'algorithm': 5})` | `True`; `{'algorithm': 6}` → `False` | ✓ PASS |
| Named behavioral invariant (no-VPP with FLAG_CAN_ERASE set) | `pio test -e native -f 'native/avr/test_val_5v_page'` | 15/15 pass, target case passes | ✓ PASS |
| Full native suite case count | `pio test -e native` | 185/185 | ✓ PASS |
| `check_erase_no_vpp.py` still passes for the right reason | `python3 scripts/check_erase_no_vpp.py` | `PASS: eeprom28c_erase_execute()...` rc=0 | ✓ PASS |
| flash4 gate suite | `pytest tests/test_flash4_erase_gate.py` | 22 passed | ✓ PASS |
| App regression subset (erase/jp5/sdp/flash4/characterization) | `pytest tests/ -k "erase or jp5 or sdp or flash4 or characterization"` | 354 passed | ✓ PASS |
| Gitlinks match submodule HEADs | `git ls-tree HEAD -- firestarter{,_app}` vs `git -C ... rev-parse HEAD` | exact match, both | ✓ PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` convention applies to this phase; `check_erase_no_vpp.py` and
`check_size_baseline.py` (Python gate scripts, not shell probes) were exercised directly above and
in the orchestrator's independently-measured evidence block (both re-confirmed consistent by this
verification: `check_erase_no_vpp.py` rc=0 for the real body, native suites 185/185).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| SAFE-06 | 183-03, 183-06 | Flash4 erase refusal names the part, no cause/alternative in CLI | ✓ SATISFIED | `flash4_erase_gate.py` + 22 tests; REQUIREMENTS.md amended as relocation |
| SAFE-07 | 183-01 | Firmware-flash cost measured before mechanism chosen | ✓ SATISFIED | Three-row M1/M2/M3 pricing table, probe reverted, D-02 decision recorded; ROADMAP.md criterion 2 amended to match (commit `dc309bf8`) |
| SAFE-08 | 183-04, 183-05 | Unreachable `CMD_ERASE` arm adjudicated, deletion or retention with reason | ✓ SATISFIED | Deleted at all 4 sites; docs/blast-radius repaired; shrink measured; backstop untouched |
| SAFE-09 | 183-02 | AE29F2008 classification investigated, conclusion recorded, no hand-edit | ✓ SATISFIED | Equivalence-based verdict recorded; `chip_database.json` byte-unchanged |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s only Phase-183-scoped IDs are SAFE-06
through SAFE-09, and all four appear in a plan's `requirements:` frontmatter.

### Anti-Patterns Found

None blocking. No `TBD`/`FIXME`/`XXX` markers found in any file this phase added or changed in
either submodule. No hardcoded stub returns, no empty handlers, no placeholder text.

### Human Verification Required

None. All must-haves resolved to VERIFIED or FAILED programmatically; no item required visual,
real-time, or external-service judgment.

### Gaps Summary

None. The single gap from the initial pass (17/18) — `.planning/ROADMAP.md` Phase 183 success
criterion 2 undercounting the candidate set and misstating the deciding factor — was closed in
commit `dc309bf8`. The amended text was re-checked on the same standard applied to criterion 1 and
the SAFE-06 amendment:

- **Names all three candidates and the measured/structural split:** "All three candidate mechanisms
  carry a firmware-flash figure — M1 a measured one, M2 and M3 structural zeros stated with the
  reason the zero is structural." Matches `183-01-SUMMARY.md`'s three-row pricing table exactly.
- **States the actual deciding ground:** "the record states the grounds the choice was actually made
  on... M3 was chosen on D-02 grounds — M1 and M2 both fire only after `Connecting... OK`, and a
  pre-connect refusal was the requirement." This is D-02, not the flash figures — consistent with
  `183-01-SUMMARY.md`'s own words ("The flash figures did not decide this choice") and with
  `REQUIREMENTS.md`'s SAFE-07 Trace note ("M3... chosen on D-02 grounds, not the flash figures").
- **Reads as a transparent relocation, not a quiet rewrite:** the amendment carries an inline
  `**AMENDED by Phase 183 alongside criterion 1 (D-08):**` note that quotes the original wording
  verbatim ("the original wording said 'both' of two mechanisms and that the choice cites those
  figures") and states why it changed ("Pricing found no flash cliff... so the figures did not decide
  it"), and names its source (`183-01-SUMMARY.md`). This is the same discipline 183-06 applied to
  SAFE-06 and criterion 1 — if anything more explicit, since it carries an inline provenance note
  criterion 1's own rewrite did not. No evidence of the wording being quietly edited to fit the
  outcome without disclosure; the disclosure is present and accurate.
- **No source changed** — `git show dc309bf8 --stat` touches only `.planning/ROADMAP.md` (7
  insertions, 1 deletion), confirming nothing else was altered to manufacture this pass.

All 18 truths are now VERIFIED. SAFE-06 through SAFE-09's functional delivery, the firmware backstop,
the deleted 12V erase path and its behavioral proof, the equivalence-based SAFE-09 verdict, the D-13
precise unreachability wording, the review dispositions, and the no-GSD-identifier discipline on all
phase-touched source remain verified directly against the codebase from the initial pass — nothing
executable changed between passes, so those findings are carried forward unchanged.

---

*Verified: 2026-09-11 (initial pass) / 2026-09-11 (re-verification after gap closure, commit `dc309bf8`)*
*Verifier: Claude (gsd-verifier)*
