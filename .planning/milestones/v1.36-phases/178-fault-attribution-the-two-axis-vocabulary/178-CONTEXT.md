# Phase 178: Fault Attribution — the Two-Axis Vocabulary - Context

**Gathered:** 2026-09-06
**Status:** Ready for planning

<domain>
## Phase Boundary

A run that failed to *execute validly* — a half-seated cable, a transport fault —
stops being reported as a verdict on the chip. The tool never spends a chip's
`BAD` on a fault that was never the chip's.

The vehicle is the **OCP Test & Validation two-axis model**: a **status** axis
(did the run execute validly — `COMPLETE` / `ERROR` / `SKIP`) held separately
from the existing **result** axis (the verdict on the part — the five current
`VERDICT_*` values). ATTR-04 forbids a sixth `verdict` value, so the status axis
is a **separate additive field**, and it is kept **out of the dedup hash**.

**Scope is host-only** (`firestarter_app/`). No firmware change. The single
firmware read in this phase is evidentiary: confirming what
`hw_read_voltage` actually asserts, for the ATTR-06 honesty sentence.

**Not in this phase:** reviving `classify_fingerprint`'s dead `FP_TRANSPORT`
bucket; the T4 machine-readable reason key; any rig-sanity leg that claims to
prove socket continuity (RIG-01, deferred — the only instrument available
measures the rail, not the socket).

## Inherited constraints

- **Phase 176** supplies the transport counters this phase's classification reads.
- **Phase 177** supplies the fingerprint gate this phase's fault-mode reasoning consumes.
- **Phase 174** supplies the blast-radius invariance oracle and the re-key ledger.
  Ledger row `RK-174-09-p178-status-axis-must-not-rekey-reanchored` pins
  `sst27sf512-full-all-ok` at `14d306256076` with `after_hash=None`, waiting on
  this phase's confirmation.
- **Project rule, absolute:** no comments in source code, at all.
- **CI is py3.11.** The devcontainer default 3.12 masks it. Use
  `firestarter_app/.venv311/bin/python`.
</domain>

<decisions>
## Implementation Decisions

### The two axes

- **D-01:** A transport-faulted step carries result axis `VERDICT_SKIPPED` and status axis `ERROR`. `SKIPPED` is the only one of the four legal result values that keeps the destructive-write gate `_id_step_closes_gate` (`chip_test.py:1930-1941`, keyed on `(VERDICT_BAD, VERDICT_SKIPPED)`) **closed** while also preserving the fault reason in both the filed markdown table and the exported JSON. `marginal` and `NA` both open that gate; `NA` additionally suppresses the reason to `-`/`""` (`submit.py:203-217`, `diagnostic_report.py:793`); `OK` is a false-green. `_id_step_closes_gate` is therefore left **unchanged**, and that non-change is itself an asserted truth.

- **D-02:** The status field is `StepResult.status`, values `"COMPLETE"` / `"ERROR"` / `"SKIP"`, defaulting to `COMPLETE`, with a derived top-level `DiagnosticReport.run_status`. This is OCP's own field name and enum, which is the most literal reading of ATTR-01's "following the OCP Test & Validation two-axis model". Constants `STATUS_COMPLETE` / `STATUS_ERROR` / `STATUS_SKIP` sit beside the existing `VERDICT_*` block at `chip_test.py:935-939`. The collision with the database's `support_status` is disambiguated **in the field's docstring, not in its name** — the same discipline `sdp_hold_state` uses.

- **D-03:** Adopt the OCP **vocabulary only**. No `ocptv` package, no new runtime dependency of any kind.

### What the status axis changes

- **D-04:** Three consumers are widened to consult the **status axis before** the verdict fold, and only these three. `submit.overall_verdict` (`submit.py:140-153`) → the title; `build_db_diff`'s ladder (`diagnostic_report.py:365-384`) → an `ERROR` guard arm ahead of the existing ladder, landing on inconclusive rather than letting the third arm propose a broken run for `community-reported` graduation; `_dev_test_exit_code` (`cli_handlers.py:2130-2157`) → the exit code.

- **D-05:** The issue title for a transport fault reads `INCONCLUSIVE (harness)`, reusing the existing `INCONCLUSIVE` token so the `devtest-triage` regex and its `SOFT` set keep classifying it with **zero** triage-tooling change. The cause goes in the title body as the parenthetical qualifier. No new title token is introduced, and Phase 181's triage file is not touched.

- **D-06:** The process exit code is widened even though criterion 2 names only "the overall verdict and the auto-generated issue title" — an exit `0` on a run that did not execute validly is a false-green in scripts. Status `ERROR` is added as a **code-2 candidate through `_EXIT_CODE_PRECEDENCE`**, never as a numeric `max`, following the shipped non-verdict-term precedent `sdp_oracle_not_run` already set in that same helper.

- **D-07:** `SCHEMA_VERSION` moves `1.7` → `1.8`. An exported key is being added and the version should say so. Both parsers match `schema_version` by presence only and the dedup hash never reads it, so this is mechanically free; Phase 181 still takes it to `2.0` on its deletions.

### ATTR-04 — the hash must not move

- **D-08:** The new field is excluded from `dedup_fingerprint` (`diagnostic_report.py:248-300`) by **writing no `parts.append` for it**. That function builds its hash input from an explicit five-entry allow-list with no reflection over dataclass fields, so exclusion is by construction, not by a filter that could later be inverted.

- **D-09:** `RK-174-09`'s `after_hash` stays `None`. Declaring a non-move is what `test_no_declared_row_has_after_hash_equal_to_before_hash` (`tests/test_rekey_ledger.py:332`) calls a bookkeeping error. The confirmation is the green oracle plus the MILESTONES.md prose recording that ATTR-04 was measured and held.

- **D-10:** The ATTR-04 confirmation needs a **second, positive leg** or it is vacuous: build two reports differing **only** in the status axis and assert their `dedup_fingerprint` values are equal. A green invariance oracle alone proves only that nothing already-frozen moved — it cannot prove the new field is out of the hash, because no frozen shape carries one yet.

### Honesty constraints

- **D-11:** `is_submittable` is left **byte-unchanged**. The milestone research (`.planning/research/SUMMARY.md:132`, `FEATURES.md:348`) lists a run-validity term on `is_submittable` as a Phase 178 deliverable (T3); ATTR-05 and success criterion 4 forbid it. **ATTR-05 wins and T3 is void.** Auto-classification changes the title and disposition only; the offer to file always stands.

- **D-12:** `transport_suspect` is **reported, never folded into status**. Three of its seven scanned counters are permanently `None`, so deriving a status from it would fabricate confidence. The trigger for status `ERROR` is the `(SerialError, HardwareOperationError)` exception arm.

- **D-13:** ATTR-06's own parenthetical is **repaired in the same commit** as the report sentence it governs. The requirement says `hw_read_voltage` "sets `CTRL_VPP_REGULATOR_ENABLE`"; the `CMD_READ_VPP` branch at `firestarter/src/hardware_operations.cpp:27` sets `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE` — two bits, not one. The substantive claim survives unchanged: neither branch sets any of `CTRL_VPP_A9_ENABLE` / `CTRL_VPE_ENABLE` / `CTRL_VPP_P1_ENABLE`, so no socket-routing bit is asserted and a rig with VPP unhooked still reads a healthy rail.

- **D-14:** The ATTR-06 sentence must land in the **rendered report output**, not in a docstring or a code comment. Nothing this phase ships may claim to detect a disconnected VPP jumper from a rail reading.

### Out of scope, recorded

- **D-15:** The T4 "machine-readable reason key" from the milestone research is **out of scope**. No ATTR requirement mentions it, and adding an unrequested field grows the frozen-key surface this milestone is trying to hold still.

- **D-16:** Reviving `classify_fingerprint`'s `FP_TRANSPORT` bucket is **out of scope**. It is dead code on this branch (`_run_cycle_block` hard-codes `runs=1` at `chip_test.py:1598`, and every fingerprint-bearing op sits inside the cycle block — confirmed structurally and by a measured probe across three chips). ATTR-01..06 does not ask for a fingerprint status.
</decisions>

<constraints>
## Verification Constraints

- The interpreter is `firestarter_app/.venv311/bin/python` (py3.11, matching CI).
- `pytest` addopts are `-ra -q`; a count line needs `-o addopts=""`.
- `grep` in this devcontainer is ugrep and honors `.gitignore`, silently under-scanning. Use `/usr/bin/grep` for any evidence-grade scan.
- Registering the reserved shape `attr01-status-axis-transport-fault` costs **seven** coordinated edits, not the four named in `177-02-SUMMARY.md` — that count omits `_PINNED_SHAPE_ID_SET` and the `tests/fixtures/reports/*.json` snapshot, both enforced by tests at `test_blast_radius_invariance.py:559` and `:727`.
- `tests/test_dev_test_cmd.py:2014-2037` exists to prove the destructive gate closes on this exact path. Under D-01 it should stay green; if it goes RED, D-01 has been violated.
</constraints>
