---
title: Host tools/ retirement — twenty-six scripts to six, on the operator's own decision, no successor
date: 2026-09-13
context: v1.37 Phase 188, D-01 through D-25 — measured against the live repositories, before and after
  each deletion, and against the eight plan SUMMARY files that did the work.
---

# Host `tools/` retirement (Phase 188)

## VERDICT

**`firestarter_app/tools/` went from twenty-six scripts to six, on the operator's own decision, not on
this phase's analysis.** Six of this phase's seven requirements resolve to **RETIRED, not delivered** —
the questions the roadmap asked were answered by subtraction. Only TOOLS-05 (no `.planning/` citations
under `tools/`) produced work, and it now applies to six files instead of twenty-four. **No successor
guard was authored for anything this phase retired: no new `check_*.py` script, no new CI step, no new
hook, in any of the three repositories, for any reason.** The operator's own framing, stated before any
deletion: *"I believe that they aren't bringing any value at all to the projects."*

This note carries what D-23 requires: one line per retired item naming what it guarded and why it went,
the eight disclosed costs in one place, the OD-1-to-D-25 supersession by name, the deleted regression-guard
prose verbatim, the TOOLS-04 disposition tension, and the residual-gap statement — naming a gap and filing
one are different acts, and this note performs only the first.

## 1. What was retired, one line each, with the measured line count from the plan that deleted it

**The ten `check_*.py` gates (D-01) — all retired, no exceptions, measured at deletion:**

| Gate | Lines | What it guarded | Deleted in |
|---|---:|---|---|
| `check_diagnostic_report_claims.py` | 269 | AST scan for forbidden diagnostic-report claim patterns | 188-03 |
| `check_dispatch.py` | 510 | The host dispatch-model invariant (see §2, cost 5) | 188-03 |
| `check_devtest_orchestrator.py` | 666 | `_HANDLER_FUNCTION_NAMES` orchestrator-registration parity | 188-04 |
| `check_is_memory_cmd_no_ifdef.py` | 340 | `is_memory_cmd()` carries no `#ifdef` | 188-04 |
| `check_mypy_watermark.py` | 238 | The CI-named mypy type-error watermark floor | 188-04 |
| `check_no_community_support_status_write.py` | 261 | No write of a forbidden community-support status string | 188-04 |
| `check_no_exists_proxy.py` | 366 | No proxy re-implementation of an `exists()` check | 188-04 |
| `check_no_log_in_sdp_window.py` | 438 | No logging call inside the SDP timing window | 188-04 |
| `check_protection_readability_invariants.py` | 524 | Protection-readability structural invariants | 188-04 |
| `check_sdp_capability_invariants.py` | 364 | SDP capability structural invariants | 188-04 |

Ten gates, **3,976 measured lines** (CONTEXT.md's pre-phase estimate was 3,985; the 9-line gap is the
estimate-vs-measured variance the record should carry honestly, not round away). Their own test suites —
3,537 lines across 188-03/188-04 — went with them, along with seven planted-violation fixtures and the
scan-path pair (§ below).

**The six GSD-process tools (D-04) — all retired, measured at deletion, 4,144 lines total:**

| Tool | Lines | What it guarded | Disposition |
|---|---:|---|---|
| `audit_coverage_matrix.py` | 1,952 | Mints `DEFECT-COV-NN` IDs into the committed coverage ledger | retired |
| `diff_db.py` | 984 | Chip-database diff for the devtest-rootcause procedure | **relocated**, not retired — see §5 |
| `measure_plan_shapes.py` | 370 | The frozen half of a v1.36 Phase 175 no-drop proof | retired |
| `measure_part_number_delta.py` | 303 | A v1.36 Phase 174 part-number-delta drift oracle | retired |
| `snapshot_report_shapes.py` | 190 | Regenerated the 19 committed report-shape snapshots (WR-01 — see §2, cost 7) | retired |
| `build_devtest_issue_corpus.py` | 345 | Built the devtest issue-corpus fixture | retired |

**The two CI mirrors (D-07) — both retired, 525 lines:** `ci_parity.sh` (162 lines) and
`ci_replica_venv.sh` (363 lines) existed to make the mypy watermark leg trustworthy against a Python 3.12
devcontainer; D-02's removal of mypy from CI removed their reason to exist.

**The one orphan (D-15) — retired on judgment, 263 lines:** `derive_sdp_partition.py` had no test and no
code reference anywhere in any of the three repositories; its only consumer record was `STATE.md` prose.
Retired on the operator's judgment about its value, not on the reference-count evidence this same audit
had already retracted once (see §5's TOOLS-04 discussion for the parallel).

**The frame-vector apparatus (D-08) — retired on both sides, 949 host lines + 1,142 firmware lines:**
host: `tools/catalog/codegen_vectors.py` (418), `tools/catalog/frame-vectors.toml` (120),
`firestarter/frame_vectors.py` (129), `tests/test_frame_vectors.py` (282, 13 tests). Firmware:
`tools/catalog/codegen_vectors.py` (418), `tools/catalog/frame-vectors.toml` (120),
`include/frame_vectors.h` (57), and the three-file `test/native/avr/test_frame_vectors/` suite (29 + 119
+ 399 = 547 lines, 6 `RUN_TEST` cases). This was the only mechanism in either repository proving host and
firmware encode/decode the identical COBS-framed wire bytes (see §2, cost 1).

**The scan-path pair (D-13) — retired, 561 lines:** `tests/scan_paths.py` (354) and
`tests/test_scan_paths_resolve.py` (207) indexed eleven tool resolvers and six cross-repo test paths,
including the one guard against a firmware rename silently flipping host test modules from pass to skip
(see §2, cost 3).

**The mypy CI leg (D-02) — retired, no replacement:** `ci.yml`'s `mypy type check (watermark gate)` step
(two lines: name + run) deleted in the same commit as `check_mypy_watermark.py`, along with three
comment-mentions of "mypy" elsewhere in the same file (the D-07 gate-steps header enumeration, a
CI-runs-on-every-branch historical note, and the `ci-py32` job's own "runs no ruff/ruff-format/mypy/..."
comment). Zero occurrences of "mypy" remain anywhere in `ci.yml`.

## 2. The eight disclosed costs, each stated as a loss

**Cost 1 (D-08).** Nothing now proves host and firmware agree on the same wire bytes. The frame-vector
apparatus was a live, byte-level cross-repo contract test — not a zero-findings AST checker like the ten
gates — asserting both the encode and decode legs of the COBS frame contract against a frozen golden-vector
catalog, on both sides of the wire. `firestarter_app/tests/test_cobs.py` independently covers the
COBS/CRC8 algorithm on the host side alone; nothing covers agreement between the two implementations. If
host and firmware framing ever diverge, nothing will catch it.

**Cost 2 (D-12).** A code-level scan still cannot distinguish a live operator tool from a dead one, on a
smaller directory. TOOLS-02's consumer-declaration convention — and the fail-closed check that would have
asserted it — were both dropped rather than built. The audit's central finding stands unaddressed: this
same scan already misclassified `ci_replica_venv.sh` and `derive_sdp_partition.py` as dead weight once
(see `host-tools-checker-apparatus-audit.md`'s "CORRECTED" section), and the next cleanup pass on the
remaining six survivors inherits that exact blind spot.

**Cost 3 (D-13).** The measured defect where a firmware rename silently flips host test modules from
PASS to SKIP at exit 0 is no longer guarded. `tests/scan_paths.py`'s fail-closed resolver — the only
thing in either repository that caught this — was deleted with the tools it indexed. Phase 184 repaired
one instance of this defect eight days before this phase ran; nothing now prevents a recurrence.

**Cost 4 (D-15).** `derive_sdp_partition.py` was retired on the operator's judgment about its value, not
on the reference-count evidence the audit had already retracted for this exact tool. That is a
qualitatively different kind of retirement from the other nine tools in this section — those failed a
"what breaks if this is deleted that the unit tests would not already catch" test; this one passed that
test (it had a live, standalone verification role, `STATE.md:768-770`) and was retired anyway, on a
values judgment the operator is entitled to make but this note is obligated to flag as distinct.

**Cost 5 (surfaced during execution — the dispatch gate's own electrical-safety invariant).**
`check_dispatch.py`'s own AST enforcement — that the host's memory-type-to-write-handler dispatch model
(`_ALGO_MEM_TYPE`, `_SRAM_PROTOCOLS`, `KNOWN_PROTOCOLS`) stays structurally consistent — is gone with the
gate family (D-01). A memory-type misclassification here is exactly the shape of error that would route
a part through the wrong voltage handler. This is a distinct loss from cost 8 below: this one is the
AST-level structural check the gate itself performed; cost 8 is the six wire-contract suites' own
runtime proof, which is the last thing that stood in this AST check's place once it was gone.

**Cost 6 (surfaced during execution — the now-decorative lock-status AST leg).**
`tests/test_lock_status_class_partition.py::test_silicon_only_tokens_never_appear_in_a_return_value_ast`
is now decorative: its planted-fixture pairing (`test_planted_fixture_fails_the_gate_seam_naming_class1`,
routed through the retired protection-readability gate) was deleted with the gate family (D-01), so
nothing left proves the AST rule can ever fail. The assertion still runs and still passes; it no longer
has a failing case to distinguish itself from a tautology. Recorded live in `WINDOWS.md` entry 8.

**Cost 7 (D-25's own — WR-01 died with its regenerator).** Snapshot-drift coverage — every one of the 19
committed report-shape snapshots byte-compared against a fresh regeneration
(`test_committed_snapshot_matches_a_fresh_regeneration`) — ceased to exist the moment D-01 and D-04
deleted `snapshot_report_shapes.py`, the tool that produced the comparison target. **No replacement was
authored and none is to be.** This is stated as a decision, not an oversight: the nineteen snapshot files
themselves stay (a surviving test, `test_shape_ids_frozen_hashes_ladder_pins_and_snapshots_agree`, still
asserts `SHAPE_IDS == {p.stem for p in fixtures/reports/*.json}`), but nothing any longer proves those
frozen files still match what the renderer would produce today. Recorded live in `WINDOWS.md` entry 6.

**Cost 8 (D-25's own — the six wire-contract suites' BLOCKER-2 invariant has no coverage at all).**
`test_val_wire_5v_page.py`, `test_val_wire_sram.py`, `test_val_wire_eeprom28c.py`, `test_val_wire_eprom.py`,
`test_val_wire_flash_intel.py`, and `test_val_wire_nor_unlock.py` were the host's own automated proof that
each chip family's wire dictionary routes to the electrically-correct handler and **never** to
`configure_eprom` for a 5V SRAM part — the BLOCKER-2 electrical-safety invariant, where a 12V VPP applied
to a 5V part is hardware destruction. All 38 tests across the six suites were deleted as consumers of the
retired `check_dispatch.py`'s symbols (D-25). **Any drift in that routing while these suites are absent is
not retroactively detectable.** The operator was shown these six suites by name, and this exact cost, at
the 188-02 blocking-human gate, before choosing "Delete the consumers." This is an accepted, disclosed
loss, not a defect this phase introduced unknowingly.

## 3. The OD-1-to-D-25 supersession, stated plainly

The orchestrator's prior ruling **OD-1** held that the four orphaned library symbols consumed only by
test modules (`dispatch`/`_ALGO_MEM_TYPE`/`_SRAM_PROTOCOLS`/`KNOWN_PROTOCOLS` from `check_dispatch.py`;
`render_shape` from `snapshot_report_shapes.py`; `_HANDLER_FUNCTION_NAMES` from
`check_devtest_orchestrator.py`; `FORBIDDEN_PATTERNS` from `check_diagnostic_report_claims.py`) would
**relocate into the test tier**, with their consuming tests repaired to import from the new location. This
plan does not follow OD-1. **D-25 supersedes it**, at two gates:

**Gate one (188-02 Task 2, `blocking-human`).** Shown a live census of all four symbols' consumers
(90 tests, 11 modules, measured by `pytest --co` not by grep) and told the gate half of every one of the
four source files is retired either way, the operator answered verbatim: **"Delete the consumers."** That
is the un-offered alternative — OD-1 never put deletion to the operator — chosen deliberately, with the
six `test_val_wire_*` wire-contract suites and their BLOCKER-2 invariant (cost 8, above) named as
casualties before the answer was given.

**Gate two (the replanning pass, before 188-03/188-04 ran).** Re-measurement found the first gate's own
framing had understated the blast radius: eleven modules consume the four symbols, not eight, and
whole-module deletion of all eleven would cost 247 collected tests, not the ~105 the operator had been
priced at. The 157-test gap included 68 tests in `test_blast_radius_invariance.py` — the v1.36 Phase 174
blast-radius oracle (GATE-01/02/03, D-07/D-10), the milestone's hard-ordered first-and-alone gate against
a silent `dedup_fingerprint` re-key, never named at the first gate. Shown that, the operator chose
**surgical** deletion: seven modules deleted whole, four mixed modules trimmed of only their
symbol-consuming tests, the rest left standing.

**Measured outcome.** The four symbols were **not** relocated. No relocation helper module —
`tests/dispatch_model.py`, `tests/report_claim_patterns.py`, `tests/report_shape_renderer.py`, or
`tests/devtest_handler_names.py` — exists anywhere in the tree; a repo-wide `git ls-files` check for all
four names returns nothing. **Ninety consuming tests were deleted, and only those ninety — zero collateral.**
Collected-count boundaries, measured at every step (never a passed count, since a module
that stops collecting reports zero results and disappears silently): baseline 2373 → 188-03 Task 1: 2368
→ 188-03 Task 2: 2307 → 188-04 Task 1: 2262 → 188-04 Task 2: 2175 → 188-05: 2142 → 2129 (final, after the
frame-vector apparatus and the six process tools were also retired — a separate subtraction that arrives
in the same commits, not part of the 90). **One test that imported a derived constant from a deleted
module was repaired rather than deleted** — `tests/test_chip_test.py::test_run_status_is_complete_when_no_step_errored`,
whose in-function import of `_ALL_OPS`/`_MULTIWORD_OP_VALUES` from the deleted
`check_devtest_orchestrator.py` was replaced with the same two comprehensions derived in-function from
`firestarter.chip_test` — which is precisely what kept the collateral at zero instead of at ninety-one.

Do not read 90 as this phase's whole subtraction. 2373 − 90 = 2283 is a state the suite never occupied at
any boundary — D-01 and D-04 retired the ten gates' and six tools' own 3,537+1,625 lines of test modules
in the same commits as the consumer deletions, and those are a separate subtraction that happens to land
together. The end state is 2129 collected, not 2175 — the coverage figure D-25's replan named as its own
projected floor, before 188-05's further tool retirements subtracted a further 46.

## 4. The deleted regression-guard prose, quoted verbatim

`firestarter_app/CLAUDE.md` carried this paragraph, deleted by plan 188-04 in the same commit as
`check_dispatch.py`'s own consumers (`check_dispatch.py` itself had already gone in 188-03):

```
Regression guard: `tools/check_dispatch.py` asserts (a) no chip routes to
`configure_eprom` on a pinout with no vpp-pin (structural, type-string-independent —
GATE-03 primary guard); (b) no `DIP28_2764` chip with a 5V-EEPROM type routes to
`configure_eprom` (WARNING-5 type-keyed guard, covers the A14-hazard that the
structural guard cannot catch because DIP28_2764 does have a vpp-pin).
```

The 12V-hazard paragraph this sentence followed — the manufacturer list and the seven-chip exception
sentence describing the 12V-on-pin-1 hardware-damage path across roughly 23 28C-family EEPROMs — stays in
full, unedited. Only the sentence naming the now-deleted gate is gone. No replacement guard names this
invariant anywhere in the tree; a reader of `CLAUDE.md` today has no way to learn that this structural
property was ever machine-checked, other than by reading this note or the git history that removed it.

## 5. TOOLS-04's disposition tension, and why TOOLS-05 alone carries the checked box

D-22 lists TOOLS-04 under **RETIRED**, and the requirement ledger amended by this plan (§ below) writes
RETIRED. But TOOLS-04's own wording — each of the six GSD-process tools "is placed by name" — reads, on a
literal parse, as **satisfied** rather than retired: all six were in fact placed by name. Five were
deleted (a placement decision, not an absence of one) and the sixth, `diff_db.py`, was **relocated** into
`.claude/skills/devtest-rootcause/scripts/` as a skill-owned copy (D-05) — the one placement in this whole
phase that is not a subtraction.

D-22 chose RETIRED anyway, and it demonstrably knew how to mint a bespoke category when it wanted one — it
gave TOOLS-03 exactly that ("satisfied by family retirement," not RETIRED and not Complete). This note
does not resolve that tension by inventing a third word here; it records both readings and states which
one the ledger follows. The ledger follows RETIRED because the requirement's underlying **purpose** — what
should earn a permanent place in the published package repository — was answered by subtraction for five
of the six tools, and the one exception (`diff_db.py`) is a relocation *out of* that repository, not an
argument for it staying. "Each is placed by name" is technically true of all six; "each earned its place
in the shipped package" is true of none. The ledger's disposition tracks the second question, because that
is the question TOOLS-04 exists to answer.

This is also why **TOOLS-05 carries the only checked box in the TOOLS block**: it is the sole requirement,
of these seven, that produced work rather than absence. The five other RETIRED requirements and the one
"satisfied by family retirement" requirement were all answered by deciding not to build; TOOLS-05's six
survivors were genuinely swept, by hand, of every planning citation — a thing that did not exist before
this phase and does now.

## 6. Two further facts a later reader would otherwise rediscover the hard way

**The coverage-matrix checker's last measured behaviour.** Before its deletion, `audit_coverage_matrix.py
--check` was measured (188-05) to exit **1**, printing **zero bytes** on both stdout and stderr, on
either of its two failure paths (the new-finding branch and the missing-`DEFECT-COV-00` branch,
`audit_coverage_matrix.py:1499-1509`). TOOLS-07 asked for this to be fixed or explained; D-06 dissolves
the requirement by deleting the tool instead, so this figure is the tool's epitaph, not a repaired
behaviour.

**`tools/baseline/dispatch_baseline.json` is now orphaned data, and stays.** It has zero consumers after
this phase's deletions, but D-14 scopes this phase to scripts, not data files under `tools/`; the file is
retained, untouched, and undecided by this note — a future pass may find it, this one does not.

## 7. The residual gap, stated in the form the analog note uses

No successor guard and no backlog item are filed for any of the eight costs above, or for anything named
in this note. **This is deliberate, on the operator's own decision (D-23), not an oversight and not
something this note argues against.** Each gap is real, each is named in full above, and each could in
principle be closed by a differently-scoped mechanism — a unit test where an AST gate once stood, a
narrower two-way check where a three-way one was retired, a declared-consumer convention where none now
exists. The operator was shown these costs and declined every guard. **Naming a gap and filing a gap are
different acts; this note performs only the first.**
