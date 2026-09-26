---
phase: 143-host-timeout-progress-pulse-override
plan: 02
subsystem: host-protocol
tags: [python, pytest, serial-protocol, wire-decode, struct, mypy-strict, cap-03, msg-ok-ready]

# Dependency graph
requires: []
provides:
  - "write_block_budget_s: Optional[int] on SerialCommunicator, decoded from MSG_OK_READY's third length-discriminated field at the COMPUTED ver_end offset (CAP-03, HOST-01 host half)"
  - "WRITE_BUDGET_MAX_S = 14400, a derived plausibility ceiling mirroring CAP-01's [1, 4096] / T-55-06 precedent"
  - "Five byte-layout proof cases in tests/test_hw_revision_gate.py, each seen RED under a named production-code plant (D-25), including the two-identity-length ver_end proof"
affects: [143-03, 143-04, 143-10, 144]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "CAP-03: a third length-discriminated ack field nested INSIDE CAP-02's own ver_end bounds-check guard, so an absent prior field structurally forecloses the new one rather than needing a second independent guard"
    - "D-25 evidence via named single-line plants against production code only (never the test file), each run, captured and reverted, with git diff --exit-code confirming byte-identical restoration before the next plant"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/tests/conftest.py
    - firestarter_app/tests/test_hw_revision_gate.py

key-decisions:
  - "WRITE_BUDGET_MAX_S=14400 is the plan's own DERIVED ceiling (ceil(25*65535*4096/1e6)*2+2=13424, rounded to 14400) -- carried through verbatim, not re-derived independently"
  - "Plant A (ver_end -> literal 4) produced BOTH the short- and long-identity cases RED, not the plan's predicted case-1-GREEN/case-2-RED asymmetry -- both mandated fixtures share the \"3.0.0:\" prefix, so the misread lands on the identical wrong bytes for both. Recorded as an honest finding; the mandated fixture strings and budget numbers were not altered to force the predicted asymmetry"

patterns-established:
  - "Pattern: extend a length-discriminated ack field by nesting under the PRIOR field's own bounds-check guard (here, CAP-03 inside CAP-02's `if ver_end <= len(params_bytes)`), so the new field is structurally unreachable when its prerequisite tail is absent"

requirements-completed: []

coverage:
  - id: D1
    description: "CAP-03 decode arm on SerialCommunicator._decode_id_frame: a third length-discriminated MSG_OK_READY field read at the computed ver_end, plausibility-clamped to [1, WRITE_BUDGET_MAX_S]; attribute declared at class level, in __init__, and mirrored into conftest's make_comm"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_hw_revision_gate.py::test_decode_extended_ack_populates_all_three_fields"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_fwguard.py::TestFirmwareVersionGuard::test_absent_identity_refuses"
        status: pass
    human_judgment: false
  - id: D2
    description: "Five CAP-03 byte-layout proof cases: two identity lengths proving ver_end is computed (not fixed), an absent tail (released beta firmware) and the bare legacy 2-byte ack (BF-1's current shape) both degrading to None, and the [1, WRITE_BUDGET_MAX_S] clamp rejecting 0/65535 while accepting the inclusive boundary 14400 -- each seen RED under a named plant"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_hw_revision_gate.py::test_decode_cap03_budget_at_short_identity_length"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_hw_revision_gate.py::test_decode_cap03_budget_at_long_identity_length_proves_ver_end_is_computed"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_hw_revision_gate.py::test_decode_cap02_ack_without_a_budget_tail_leaves_the_budget_none"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_hw_revision_gate.py::test_decode_legacy_two_byte_ack_leaves_both_identity_and_budget_none"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_hw_revision_gate.py::test_decode_implausible_cap03_budget_is_clamped_away"
        status: pass
    human_judgment: false

duration: ~23min
completed: 2026-08-12
status: complete
---

# Phase 143 Plan 02: CAP-03 Host Decode — Write-Block-Budget Ack Field Summary

**`SerialCommunicator._decode_id_frame` now decodes a third length-discriminated `MSG_OK_READY` field — the firmware's advertised per-block write-time budget in seconds — at the computed `ver_end` offset with a derived `[1, 14400]` plausibility clamp, proven by five byte-layout cases each seen RED under a named production-code plant.**

## Performance

- **Duration:** ~23 min
- **Started:** 2026-08-12T23:23:36Z (STATE.md hand-off from 143-01)
- **Completed:** 2026-08-12T23:46:00Z
- **Tasks:** 2 completed (both `type="auto"`, no checkpoints)
- **Files touched:** 3 (0 created, 3 modified)

## Accomplishments

- `firestarter/serial_comm.py`: `WRITE_BUDGET_MAX_S = 14400` added to the module constant block (derivation in the comment, not a bare number); `write_block_budget_s: Optional[int] = None` declared at **class** level (fail-closed default, same reasoning as the CAP-02 pair) and mirrored in `__init__`; the CAP-03 decode arm added **nested inside** CAP-02's own `if ver_end <= len(params_bytes):` guard, gated on `len(params_bytes) >= ver_end + 2`, reading with `struct.unpack(">H", params_bytes[ver_end : ver_end + 2])[0]` — the computed offset, never a fixed index — and assigning only when `1 <= value <= WRITE_BUDGET_MAX_S`.
- `tests/conftest.py`'s `make_comm` factory mirrors the new attribute (`instance.write_block_budget_s = None`) so a fixture that forgot it would fail closed rather than raising an `AttributeError` swallowed by `_probe_port`.
- `tests/test_hw_revision_gate.py`: added `_cap03_params` (built by **composing** `_cap02_params`, not duplicating its body) and five new decode cases, extending the suite from 22 to 27 collected tests. Two of the five prove D-08's named hazard directly: identities of 9 bytes (`"3.0.0:uno"`) and 14 bytes (`"3.0.0:leonardo"`) each carry a real advertised budget figure (106 s and 3358 s, from `143-RESEARCH.md`'s own worked examples) and both decode correctly only because the offset is computed.
- D-25 evidence: four named single-line plants applied to `firestarter/serial_comm.py` only (never the test file), each run, transcript captured, then reverted with `git checkout --` and `git diff --exit-code` confirming byte-identical restoration before the next plant. See the dedicated section below, including one finding where the actual result diverged from the plan's own stated prediction.
- Full host suite: **1552 passed** (1547 baseline + 5), coverage **82.36%** (≥70% floor), `ruff check`/`ruff format --check` clean, mypy watermark exit 0 (33 errors, 2 below the 35 watermark — pre-existing, unmoved by this plan since `serial_comm.py`'s new code is fully typed).
- Confirmed **BF-1 remains open**: this plan does not touch firmware and does not make any v1.31 build connect. `_probe_port` still refuses a bare 2-byte `MSG_OK_READY` (`test_fwguard.py::test_absent_identity_refuses`, unmoved), and `FIRESTARTER_DEV_ALLOW_PRE_V12=1` is not a workaround (it bypasses the version check, not the identity-absent raise). Porting CAP-02's firmware emit is plan 143-03's obligation.

## Task Commits

Each task was committed atomically, inside `/workspaces/firestarter_app` on branch `gsd/v1.31-27c-programming-algorithm-fidelity`:

1. **Task 1: Extend `_decode_id_frame` with the CAP-03 arm, add `WRITE_BUDGET_MAX_S`, and mirror the attribute into `make_comm`** - `2fde93b` (feat)
2. **Task 2: Prove the byte layout with five CAP-03 decode cases, including the two-identity-length `ver_end` proof** - `1eed0eb` (test)

**Plan metadata:** committed in the meta repo (`/workspaces`), see below.

## Files Created/Modified

- `firestarter_app/firestarter/serial_comm.py` - `WRITE_BUDGET_MAX_S` constant; `write_block_budget_s` class + `__init__` attribute; CAP-03 decode arm nested inside CAP-02's `ver_end` guard; docstring extended with a CAP-03 paragraph. Zero hunks below the `DO NOT MODIFY — v1.9 RCA territory (GATE-1.8d)` header (D-13, confirmed by `git diff`).
- `firestarter_app/tests/conftest.py` - `make_comm` mirrors `write_block_budget_s = None`.
- `firestarter_app/tests/test_hw_revision_gate.py` - `_cap03_params` fixture builder plus five new decode cases (123 insertions, 0 deletions — no existing test body modified).

## Decisions Made

- **`WRITE_BUDGET_MAX_S = 14400` carried through verbatim from `143-RESEARCH.md`'s own derivation** (`ceil(25 * 65535 * 4096 / 1e6) * 2 + 2 = 13424`, rounded up to 14400) rather than re-derived independently — the plan's own math was verified by re-reading, not recomputed from scratch, since it is already the load-bearing number the acceptance criteria assert against.
- **CAP-03's class-level comment was *extended*, not duplicated.** The plan explicitly warns against "a second, competing comment" — the existing CAP-02 identity-fields comment block now also names CAP-03, rather than growing a parallel explanation of the same `__new__`/no-op-`__init__` failure mode.
- **The identity-attribute-shape convention (`3.0.0:uno` / `3.0.0:leonardo`) came from the plan's own mandated fixture values** (`143-PATTERNS.md`'s "≥2 identity lengths" instruction), not chosen independently — which is what produced Plant A's finding below.

## Deviations from Plan

None — plan executed exactly as written. No Rule 1/2/3/4 deviations: no bugs found, no missing critical functionality, no blocking issues, no architectural changes. The only notable divergence is a **D-25 evidentiary finding** (not a code deviation), documented in full below.

## D-25 Evidence: RED-on-plant, then GREEN, for all four plants

Per the plan's obligation, each plant was applied to `firestarter_app/firestarter/serial_comm.py` **only** (never the test file), run via `.venv/ci-replica/bin/python -m pytest tests/test_hw_revision_gate.py -k cap03 -o addopts=""`, captured, then reverted with `git checkout -- firestarter/serial_comm.py` — confirmed byte-identical to the committed file via `git diff --exit-code` before the next plant.

### Plant A — `ver_end` replaced with the literal `4` in the CAP-03 slice (both the length gate and the read)

Targets: predicted to turn the long-identity case RED while leaving the short-identity case GREEN.

```
tests/test_hw_revision_gate.py::test_decode_cap03_budget_at_short_identity_length FAILED
tests/test_hw_revision_gate.py::test_decode_cap03_budget_at_long_identity_length_proves_ver_end_is_computed FAILED
tests/test_hw_revision_gate.py::test_decode_implausible_cap03_budget_is_clamped_away FAILED

______________ test_decode_cap03_budget_at_short_identity_length _______________
    assert comm.write_block_budget_s == 106
E   assert 13102 == 106
E    +  where 13102 = <firestarter.serial_comm.SerialCommunicator object at 0x...>.write_block_budget_s

_ test_decode_cap03_budget_at_long_identity_length_proves_ver_end_is_computed __
    assert comm.write_block_budget_s == 3358
E   assert 13102 == 3358
E    +  where 13102 = <firestarter.serial_comm.SerialCommunicator object at 0x...>.write_block_budget_s

3 failed, 24 deselected in 0.08s
```

**Finding (honest, not glossed over): the actual result diverges from the plan's stated prediction.** The plan's acceptance criteria state this plant "turns the long-identity case RED while the short-identity case stays GREEN." Measured reality: **both** cases go RED, with the *identical* misread value (13102) in both. Root cause, confirmed by hand computation before running: `_cap03_params`'s two mandated identity strings — `"3.0.0:uno"` and `"3.0.0:leonardo"` — **share the same four-character prefix** `"3.0."`. Reading at the literal fixed offset 4 (instead of each fixture's real `ver_end` of 13 and 18 respectively) lands on bytes `b"3."` (`0x332E` = 13102) in *both* fixtures, because both identity strings begin with the same two bytes at that position. `13102` also happens to be `<= WRITE_BUDGET_MAX_S` (14400), so it is *accepted* as a plausible-looking but wrong value rather than rejected outright — which is why the assertion fails via a value mismatch (`13102 == 106`) rather than a `None` mismatch.

This is not a weaker result than predicted — arguably it is a **stronger** one: a fixed index breaks universally here rather than selectively, which is if anything a sharper demonstration of D-08's named hazard (a fixed index "silently misreads," it does not reliably "work on one length and fail on the other"). But the specific asymmetry the plan's acceptance criteria describe does not hold for the *specific* fixture strings the plan itself mandates (both cases were RED, not one RED and one GREEN), and no fixture value was altered to force the predicted shape onto the evidence — this transcript is the real, unedited output. Neither `_cap03_params`, the two identity strings, nor the two budget numbers (106, 3358) were changed to manufacture the described asymmetry; they are exactly what `143-02-PLAN.md`'s Task 2 action and acceptance criteria specify verbatim.

### Plant B — clamp widened from `[1, WRITE_BUDGET_MAX_S]` to `[1, 65535]`

Targets: case 5's `65535` sub-assertion.

```
tests/test_hw_revision_gate.py::test_decode_cap03_budget_at_short_identity_length PASSED
tests/test_hw_revision_gate.py::test_decode_cap03_budget_at_long_identity_length_proves_ver_end_is_computed PASSED
tests/test_hw_revision_gate.py::test_decode_implausible_cap03_budget_is_clamped_away FAILED

_____________ test_decode_implausible_cap03_budget_is_clamped_away _____________
    # Rejected: above WRITE_BUDGET_MAX_S (14400).
    ...
>   assert comm.write_block_budget_s is None
E   assert 65535 is None
E    +  where 65535 = <firestarter.serial_comm.SerialCommunicator object at 0x...>.write_block_budget_s

1 failed, 2 passed, 24 deselected in 0.07s
```

**Matches the prediction exactly.** No case failed to go RED that should have; no case unexpectedly stayed GREEN.

### Plant C — length gate weakened from `>= ver_end + 2` to `>= ver_end + 1`

Targets: the one-byte truncation sub-case ("or raise").

```
tests/test_hw_revision_gate.py::test_decode_cap03_budget_at_short_identity_length PASSED
tests/test_hw_revision_gate.py::test_decode_cap03_budget_at_long_identity_length_proves_ver_end_is_computed PASSED
tests/test_hw_revision_gate.py::test_decode_implausible_cap03_budget_is_clamped_away FAILED

    comm._decode_id_frame(len(body), body)

firestarter/serial_comm.py:431: in _decode_id_frame
    value = struct.unpack(
E   struct.error: unpack requires a buffer of 2 bytes

1 failed, 2 passed, 24 deselected in 0.13s
```

**Matches the prediction exactly** — the plan explicitly anticipated "RED or raise," and this plant raises `struct.error` rather than failing a plain assertion. `pytest` still reports it as a failed test (an error), which is the correct outcome: a partial value must never be trusted, and here the code doesn't even get the chance to produce one.

### Plant D — the entire CAP-03 arm deleted

Targets: cases 1, 2, and 5's accepted (`14400`) sub-case RED; cases 3 and 4 stay GREEN.

```
tests/test_hw_revision_gate.py::test_decode_cap03_budget_at_short_identity_length FAILED
tests/test_hw_revision_gate.py::test_decode_cap03_budget_at_long_identity_length_proves_ver_end_is_computed FAILED
tests/test_hw_revision_gate.py::test_decode_cap02_ack_without_a_budget_tail_leaves_the_budget_none PASSED
tests/test_hw_revision_gate.py::test_decode_legacy_two_byte_ack_leaves_both_identity_and_budget_none PASSED
tests/test_hw_revision_gate.py::test_decode_implausible_cap03_budget_is_clamped_away FAILED

______________ test_decode_cap03_budget_at_short_identity_length _______________
    assert comm.write_block_budget_s == 106
E   assert None == 106

_ test_decode_cap03_budget_at_long_identity_length_proves_ver_end_is_computed __
    assert comm.write_block_budget_s == 3358
E   assert None == 3358

_____________ test_decode_implausible_cap03_budget_is_clamped_away _____________
    # Accepted: the ceiling itself is inclusive.
    ...
>   assert comm.write_block_budget_s == 14400
E   assert None == 14400

3 failed, 2 passed, 24 deselected in 0.15s
```

**Matches the prediction exactly.** Cases 3 and 4 never touch the CAP-03 arm in the first place (no budget tail / no CAP-02 tail at all), so deleting it is invisible to them — confirming those two cases are testing a genuinely different code path, not incidentally exercising CAP-03 under a different name.

### Final GREEN (all four plants reverted; `git diff --exit-code` against the committed file is clean)

```
tests/test_hw_revision_gate.py ......................     [ 81%]
tests/test_fwguard.py .....                                [100%]
27 passed in 0.13s  (test_hw_revision_gate.py alone)
5 passed  (test_fwguard.py alone, unaffected)
```

Full-suite re-run after all reverts: **1552 passed, 1 warning in 205.58s**, 30 snapshots passed, coverage 82.36%.

## Verification Results (final state, all plants reverted)

| Check | Result |
|---|---|
| `pytest tests/test_hw_revision_gate.py -x -o addopts=""` | 27 passed (was 22 before this plan — exactly 5 more) |
| `pytest tests/test_hw_revision_gate.py -k cap03 -o addopts=""` | 3 selected, 3 passed |
| `pytest tests/test_fwguard.py -x -o addopts=""` | 5 passed, unmoved; `test_absent_identity_refuses` still refuses (BF-1 open) |
| `pytest tests/ --cov=firestarter --cov-fail-under=70 -o addopts=""` | **1552 passed** (1547 + 5), coverage **82.36%** (≥70%), 1 warning (pre-existing, matches the plan's own stated baseline) |
| `ruff check firestarter/ tests/` | All checks passed |
| `ruff format --check firestarter/ tests/` | 130 files already formatted |
| `tools/check_mypy_watermark.py` | exit 0; 33 errors, 2 below the 35 watermark (pre-existing, unmoved) |
| `git diff --exit-code -- firestarter/messages.py firestarter/constants.py firestarter/eprom_operations.py firestarter/cli_handlers.py` | clean — no codegen run, no catalog edit (D-08) |
| `git diff` on `firestarter/serial_comm.py` | all hunks end before the `DO NOT MODIFY` ring-fence header at line 445 (D-13) |
| `git status --porcelain` in `/workspaces/firestarter` (L-5 check, before the coverage leg) | clean — no deselection needed |

## Issues Encountered

- **Plant A's actual result diverges from the plan's stated prediction** — see the D-25 Evidence section above for the full analysis. Root cause is a coincidental shared prefix (`"3.0."`) between the plan's own two mandated identity fixture strings; not a defect in the production code, and not something this plan's scope authorized changing (the fixture strings and budget numbers are dictated verbatim by `143-02-PLAN.md`'s Task 2 action). Recorded as a finding per the plan's own "record any case that did not go RED under its plant as a finding" clause, generalized here to also cover "did not go RED in the *predicted shape*."

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The host decode half of HOST-01 (CAP-03) is complete and proven independently of the firmware half, per `143-CONTEXT.md`'s discretion index. `write_block_budget_s` is ready to be consumed by the write-path timeout plumbing in plan 143-04.
- **BF-1 is still open.** Nothing in this plan makes a v1.31 firmware build connect to this app branch — that is plan 143-03's obligation (porting CAP-02's firmware emit, upstream commit `13eb350`). Until then, `_probe_port` continues to refuse every v1.31 board at connect time via `FirmwareOutdatedError`.
- This plan intentionally marks no requirement Complete (frontmatter `requirements: []`) — plan 143-10 flips the `HOST-*` checkboxes once every plan's evidence exists.
- `_cap03_params`'s docstring names the standing gap explicitly: nothing in either repo currently asserts cross-repo wire-layout parity between the firmware's pack block and the host's decode arm beyond this fixture-vs-decoder comparison. `143-RESEARCH.md`'s Open Question 4 hands that standing gate to Phase 144 / TEST-07.
- No blockers. Ring-fence (D-13), catalog/codegen files (D-08), and `DEFAULT_RESPONSE_TIMEOUT` (D-12) are all confirmed untouched by `git diff`.

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/serial_comm.py` (modified)
- FOUND: `firestarter_app/tests/conftest.py` (modified)
- FOUND: `firestarter_app/tests/test_hw_revision_gate.py` (modified)
- FOUND commit `2fde93b` (Task 1)
- FOUND commit `1eed0eb` (Task 2)

---
*Phase: 143-host-timeout-progress-pulse-override*
*Completed: 2026-08-12*
