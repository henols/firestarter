---
phase: 204-the-command-surfaces-leave-the-firmware
plan: 01

subsystem: firmware-protocol
tags: [protocol-retirement, dispatch, bench-tracer, avr, pio-upload, pypi-legitimacy-gate, leonardo]

requires:
  - phase: 203-the-write-guard-moves-up-a-layer
    provides: "the host-side write guard and write --verify, which make it safe to remove CMD_VERIFY/CMD_BLANK_CHECK from the firmware at all"
  - phase: 202-one-comparison-engine-on-the-host
    provides: "the host-side comparison engine that already routes verify/blank through COMMAND_READ, so no live host path composes the retired ordinals"
provides:
  - "ordinal 6 (CMD_VERIFY / COMMAND_VERIFY) fully removed from both the firmware and host command ladders, in a lockstep commit pair"
  - "a reserved-ordinal note at both gaps, naming the retirement release and the never-reuse reason"
  - "a source-contract gate re-anchored at 8 forwarding calls / 8 admitted ordinals"
  - "proof that `pio run -e leonardo -t upload` reaches the attached board from this devcontainer"
  - "a bench-observed refusal of a real published host (3.0.0b49) on the retired ordinal, and a served control on the still-live ordinal, in the same session"
  - "an amended FWCMD-05 / ROADMAP criterion 3 naming four real failure ids instead of one wrong one"
affects: [204-03-blank-check-retirement, 204-05-bench-matrix, 207-release-and-docs]

actuals:
  tokens: 12200
  tasks: 3
  commits: 6

tech-stack:
  added: []
  patterns:
    - "Reserved-ordinal note at the gap, mirrored on both ladders (firmware header + host constants), naming the release and the never-reuse reason — repeats for ordinal 4 in plan 03"
    - "Package-legitimacy blocking-human gate before installing a SUS-flagged PyPI package into a throwaway venv, never into a project environment"
    - "Throwaway old-host venv provisioned via uv, outside both sub-repos, for bench legs that need the artifact a real user actually has"

key-files:
  created:
    - .planning/phases/204-the-command-surfaces-leave-the-firmware/204-BENCH-TRACER.md
  modified:
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - firestarter_fw/include/firestarter.h
    - firestarter_fw/include/eprom_operations.h
    - firestarter_fw/include/memory_utils.h
    - firestarter_fw/src/firestarter.cpp
    - firestarter_fw/src/eprom_operations.cpp
    - firestarter_fw/src/proms/memory.cpp
    - firestarter_fw/tests/test_boolean_convention_source_contract_v133.py
    - firestarter_fw/test/native/avr/test_dispatch/test_configure_memory.cpp
    - firestarter_fw/test/native/avr/test_cmd_admission/test_cmd_admission.cpp
    - firestarter_app/firestarter/constants.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/tests/test_eprom_operations.py

key-decisions:
  - "FWCMD-05 and ROADMAP criterion 3 amended (D-03) before any source was touched: three real failure ids (MSG_ERR_MAX_PULSES, MSG_ERR_ENERGY_CAP, MSG_ERR_OP_TIMEOUT) replace the one wrong id (MSG_ERR_VERIFY) that was previously pinned to all three named sites."
  - "Tracer scope is ordinal 6 only (Fork B) — ordinal 4 (CMD_BLANK_CHECK) stays live through this plan and is plan 03's work. This is what makes the bench run's positive control (blank still served) possible."
  - "The pre-3.1.0 host leg used the published 3.0.0b49 PyPI wheel, not a reconstruction, per the human-approved package-legitimacy gate (Task 2b)."
  - "The devcontainer's $HOME/.local/share tree turned out to be ephemeral across the infrastructure interruption between Task 2 and Task 3 — the durable Python 3.11 install and .venv311 were rebuilt identically to Task 1's recipe before bench work began. No committed artifact was affected; .venv311 is gitignored."
  - "-f/--force was used on all three bench-leg CLI invocations (read x2, verify, blank) to bypass a known-noisy VPP monitor reading that does not route to the socket, rather than let a false chip-ID/VPP precondition abort legs that do not otherwise depend on it."

requirements-completed: [FWCMD-01, FWCMD-02, FWCMD-03, FWCMD-05, FWCMD-06, REL-03]

coverage:
  - id: D1
    description: "FWCMD-05 and ROADMAP Phase 204 criterion 3 amended to name four distinct failure ids per their real raise sites, forbidding the false 0xAF pin on the data-poll wait"
    requirement: FWCMD-05
    verification:
      - kind: unit
        ref: "command: python3 -c region-scoped id-presence check over REQUIREMENTS.md FWCMD-05 and ROADMAP.md Phase 204 criterion 3 (see task 1 <verify>)"
        status: pass
    human_judgment: false
  - id: D2
    description: "firestarter_app/.venv311 runs Python 3.11.16 with an editable install of the working tree and the test extra"
    requirement: null
    verification:
      - kind: unit
        ref: "command: .venv311/bin/python -c interpreter/editable-path assertion (task 1 and re-verified task 3 after environment rebuild)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Ordinal 6 removed from every firmware site that referenced it and from the host COMMAND ladder, in one lockstep commit pair, with reserved-ordinal notes at both gaps; all four firmware CI legs and the host suite green"
    requirement: FWCMD-01
    verification:
      - kind: unit
        ref: "command: pio test -e native (237/237), pio test -e native_nodevtools (237/237), pytest tests/ (293 passed / 17 pre-existing unrelated red), pio run -e leonardo (24082/28672 B)"
        status: pass
      - kind: unit
        ref: "command: firestarter_app .venv311/bin/python -m pytest tests/ -k 'not no_programmer_found' (2306 passed / 2 deselected)"
        status: pass
    human_judgment: false
  - id: D4
    description: "memory_verify_execute still defined and still called from the eprom program loop's plus-final verify arm — the milestone's D-7 red line"
    requirement: FWCMD-02
    verification:
      - kind: unit
        ref: "command: python3 source-presence assertion over src/proms/memory.cpp and src/proms/eprom.cpp (task 2 <verify>, first leg)"
        status: pass
    human_judgment: false
  - id: D5
    description: "pio run -e leonardo -t upload proven to reach the attached Leonardo from this devcontainer — the phase's single largest unproven assumption"
    requirement: null
    verification:
      - kind: manual_procedural
        ref: "204-BENCH-TRACER.md § '(b) Flash — the A5 probe' — avrdude: 24082 bytes of flash written / verified, exit 0"
        status: pass
    human_judgment: false
  - id: D6
    description: "Published 3.0.0b49 host explicitly refused on ordinal 6 (Unknown command: 6) and served on ordinal 4 (not-blank verdict, no unknown-command line) in the same session; the seated part's 65536 bytes byte-identical before and after"
    requirement: FWCMD-06
    verification:
      - kind: manual_procedural
        ref: "204-BENCH-TRACER.md §§ (f), (g), (h) — refusal transcript exit 1 / 3.55s, served transcript exit 1 (not-blank verdict) / 3.8s no unknown-command line, cmp exits 0 over 65536 bytes"
        status: pass
    human_judgment: true
    rationale: "The task's own <human-check> asks a human to confirm the seated part is genuinely a W27C512 with non-blank content. The un-forced read reported a chip-ID mismatch (0x1818 vs the database's expected 0xda08), most plausibly explained by this rig's already-documented VPP-sensing unreliability rather than a wrong part, but this is inference, not a measurement — flagged in 204-BENCH-TRACER.md and logged to WINDOWS.md (kind: unmet-truth) rather than silently assumed. The behavioral claims (refused/served/byte-identical) are proven regardless of exact chip identity, since both legs and both reads address the same physical part; only the specific-chip label in the record's title rests on the operator's original placement."
  - id: D7
    description: "REL-03: a pre-3.1.0 host against 3.1.0b1 (working-tree) firmware fails verify with a refusal the user can act on and no hardware side effect"
    requirement: REL-03
    verification:
      - kind: manual_procedural
        ref: "204-BENCH-TRACER.md § (f) and § (h) — refusal names the offending ordinal, no hang, byte-identical read-back"
        status: pass
    human_judgment: false

duration: "3h 59m (from Task 1's first commit at 05:02:05Z to Task 3's final commit at 09:04:23Z; includes an infrastructure interruption and a blocking-human checkpoint wait, not pure active-execution time)"
completed: 2026-09-22
status: complete
---

# Phase 204 Plan 01: Ordinal 6 retired end-to-end, and the upload path proven on real silicon

**Retired `CMD_VERIFY`/`COMMAND_VERIFY` from both command ladders in one lockstep commit pair, then flashed the swept firmware to the bench Leonardo and watched the published `3.0.0b49` host be refused by name on the retired ordinal while still being served on the ordinal not yet retired — with the chip's 65536 bytes proven byte-identical across the run.**

## Performance

- **Duration:** ~3h 59m wall-clock across three sessions (Task 1 commit → Task 3 commit), including an infrastructure interruption between Task 2 and Task 3 and the blocking-human package-legitimacy checkpoint wait. Active execution time is materially less than the wall-clock span.
- **Started:** 2026-09-22T05:02:05Z (Task 1 first commit)
- **Completed:** 2026-09-22T09:04:23Z (final commit)
- **Tasks:** 3 automated/tracer tasks + 1 checkpoint (Task 2b, closed by human "approved")
- **Files modified:** 15 across three repositories (3 meta, 9 firmware, 3 host)

## Accomplishments

- Rebuilt the host test interpreter (`firestarter_app/.venv311`, Python 3.11.16, editable install with the test extra) and established the pre-source app-suite baseline, then amended `FWCMD-05` and `ROADMAP.md` Phase 204 criterion 3 to name the four real failure ids per D-03, replacing one wrong id with three proven ones.
- Retired ordinal 6 (`CMD_VERIFY` / `COMMAND_VERIFY`) end to end: deleted from the firmware CMD ladder, `is_memory_cmd`, the dispatch switch, the operation wrapper and its declaration, and `configure_memory`'s switch; deleted from the host COMMAND ladder and `COMMAND_NAMES`; reserved-ordinal notes added at both gaps; three native/source-contract gates re-anchored from a census of 9 to 8; all four firmware CI legs and the host suite green.
- Proved `pio run -e leonardo -t upload` reaches the attached board from this devcontainer for the first time ever — 24082 bytes written and verified by avrdude, exit 0.
- Ran the tracer's two-sided bench control on real silicon: a published `3.0.0b49` host explicitly refused on the retired ordinal (`Unknown command: 6`, 3.55s, no hang) and served on the still-live ordinal (not-blank verdict, 3.8s, no unknown-command line) in the same session, with the seated part's 65536 bytes byte-identical before and after (`cmp` exit 0).

## Task Commits

Each task was committed atomically. This plan spans three repositories; commits are grouped by task.

1. **Task 1: Make the instruments runnable and the requirement true** — meta `c3724e27` (docs)
2. **Task 2: Wire ordinal 6 out of the firmware and the host, one lockstep commit pair** — firmware `268d844`, host `f6d3724`, meta gitlink advance `5e675d35` (feat/feat/chore)
3. **Task 2b: Package-legitimacy gate** — checkpoint, no commit; closed by human response "approved"
4. **Task 3: Flash the tracer firmware and watch a real published host be refused** — meta `239622b0` (bench record), meta `af3f9d42` (chip-ID flag addendum) (docs/docs)

**Plan metadata:** this SUMMARY's own commit, made after this file.

_Total: 6 commits across three repositories (4 meta, 1 firmware, 1 host)._

## Files Created/Modified

- `.planning/phases/204-the-command-surfaces-leave-the-firmware/204-BENCH-TRACER.md` — the tracer bench record: rig identity, flash transcript, refusal/served transcripts, three SHA-256 digests, D-07 label substitution, and the flagged chip-ID confirmation item.
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` — FWCMD-05 and Phase 204 criterion 3 amended (D-03), before/after text below.
- `firestarter_fw/include/firestarter.h` — ordinal 6's `#define` and `is_memory_cmd` arm deleted; reserved-ordinal note added; predicate comment corrected to 8 macros, no source-scan gate claim.
- `firestarter_fw/src/firestarter.cpp` — ordinal 6's dispatch arm deleted; `default:` arm untouched (it is the entire refusal mechanism).
- `firestarter_fw/src/eprom_operations.cpp`, `firestarter_fw/include/eprom_operations.h` — `eprom_verify` wrapper and declaration deleted; `_process_incoming_data` untouched.
- `firestarter_fw/src/proms/memory.cpp` — `configure_memory`'s ordinal-6 arm deleted; `memory_verify_execute` untouched and re-documented as the surviving final-pass verify.
- `firestarter_fw/include/memory_utils.h` — `memory_verify_execute`'s doc comment rewritten to describe its actual post-204 role.
- Three firmware test files — re-anchored from a census of 9 to 8 forwarding calls / admitted ordinals.
- `firestarter_app/firestarter/constants.py` — `COMMAND_VERIFY` and its `COMMAND_NAMES` row deleted; mirror reserved-ordinal note added; stale SDP-block citations repaired.
- `firestarter_app/firestarter/eprom_operations.py` — `region-end` guard changed from a one-member tuple to an equality against the write command; two stale Phase 202 comments rewritten.
- `firestarter_app/tests/test_eprom_operations.py` — the two guard tests converted from importing the deleted symbol to asserting against integer literals.

## Decisions Made

- **D-03 amendment (verbatim before/after), FWCMD-05** — recovered from `git show c3724e27`:
  - **Before:** `- [ ] **FWCMD-05**: the per-pulse verify, `eeprom28c_verify_page_readback` and `flash_util_verify_operation` are behaviourally unchanged, and `MSG_ERR_VERIFY` (0xAF) is still raised by each.`
  - **After:** `- [ ] **FWCMD-05**: each in-algorithm verify still raises its own failure id on failure, proven by test and not by inspection: `memory_verify_execute` and `eeprom28c_verify_page_readback` raise `MSG_ERR_VERIFY` (0xAF); the per-pulse verify's budget exits raise `MSG_ERR_MAX_PULSES` (0xBD) and `MSG_ERR_ENERGY_CAP` (0xBE); `flash_util_verify_operation` is a DQ7 data-poll wait and raises `MSG_ERR_OP_TIMEOUT` (0xB7) — it can never raise 0xAF, and asserting that it does would be a false pin. Each assertion names the id, not merely a generic error response code (operator decision, 2026-09-21, recorded as D-03 in `phases/204-the-command-surfaces-leave-the-firmware/204-CONTEXT.md`; this requirement previously claimed `MSG_ERR_VERIFY` (0xAF) was still raised by all three named sites — measurement against the live source showed only `eeprom28c_verify_page_readback` actually raises 0xAF, the per-pulse verify's budget exits raise two different ids, and `flash_util_verify_operation` has no compare-and-report path at all and can never raise 0xAF).`

- **D-03 amendment (verbatim before/after), ROADMAP.md Phase 204 criterion 3:**
  - **Before:** `3. The per-pulse verify, `eeprom28c_verify_page_readback` and `flash_util_verify_operation` each still raise `MSG_ERR_VERIFY` on a mismatch, proven by test and not by inspection.`
  - **After:** `3. Each in-algorithm verify still raises its own failure id on failure, proven by test and not by inspection: `memory_verify_execute` and `eeprom28c_verify_page_readback` raise `MSG_ERR_VERIFY` (0xAF); the per-pulse verify's budget exits raise `MSG_ERR_MAX_PULSES` (0xBD) and `MSG_ERR_ENERGY_CAP` (0xBE); `flash_util_verify_operation` is a DQ7 data-poll wait and raises `MSG_ERR_OP_TIMEOUT` (0xB7) — it can never raise 0xAF, and asserting that it does would be a false pin. *(Amended 2026-09-21 per 204-CONTEXT.md D-03; previously claimed all three named sites still raise `MSG_ERR_VERIFY` — measurement against the live source showed only `eeprom28c_verify_page_readback` actually does, the per-pulse verify's budget exits raise two different ids, and `flash_util_verify_operation` has no compare-and-report path at all and can never raise 0xAF.)*`

- **App-suite baseline before any source was touched (task 1):** 2308/2308 passed.
- **Firmware suite after task 2:** `pio test -e native` 237/237, `pio test -e native_nodevtools` 237/237, `pio run -e leonardo` 24082/28672 B, source-contract gate suite 73/73, `pytest tests/` 293 passed / 17 failed — all 17 confined to `tests/test_flash_path_record_sync.py`, the pre-existing whole-repo-porcelain red the plan's own `fails_when` names as out of scope.
- **Host suite after task 2:** targeted suites 73/73, `ruff check`/`ruff format --check` clean, `pytest tests/` 2306 passed / 2 deselected (`no_programmer_found_*`, expected with a board attached).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Rebuilt the ephemeral `$HOME/.local/share` tree before bench work**
- **Found during:** Task 3, step (a)/(b), before flashing
- **Issue:** Between the Task 2b checkpoint and this continuation, an infrastructure interruption evidently reset the devcontainer's `$HOME/.local/share` tree (ephemeral, unlike the `/workspaces` bind mount): the durable Python 3.11.16 install and `firestarter_app/.venv311`, both built in Task 1, were gone. `/workspaces` and all git history were unaffected.
- **Fix:** Re-ran Task 1's exact recipe — `uv python install 3.11`, `uv venv --python 3.11 .venv311`, `uv pip install -e '.[test]'` — and re-verified against Task 1's own acceptance command before proceeding. No source file, no commit, and no plan output was affected; `.venv311` is self-ignoring and was never a committed artifact.
- **Files modified:** none (rebuild of a gitignored virtual environment only)
- **Verification:** re-ran Task 1's acceptance check; interpreter resolves under the durable install path, editable install resolves under `/workspaces/firestarter_app/`.
- **Committed in:** not applicable (no source change)

**2. [Rule 3 - Blocking] `-f`/`--force` used on all four bench-leg CLI invocations**
- **Found during:** Task 3, step (c) — the un-forced baseline read aborted at the chip-ID check
- **Issue:** This rig's VPP monitor is already-documented as not routing to the socket (project record) and its reading fluctuated across this session (4.9V too low, then 13.0V too high, with no operator intervention between reads). Without `-f`, `read`/`verify`/`blank` all abort at the VPP-dependent chip-ID check before reaching the property this task actually needed to observe.
- **Fix:** Used the CLI's own documented `-f`/`--force` flag (`"Force, even if the VPP or chip id doesn't match"`) on all four invocations. This does not weaken the observations the task needed: the retired-ordinal refusal never reaches the chip-ID/VPP-dependent code path at all (it is refused before `configure_memory` runs), and the served blank-check control's actual result — "not blank, first mismatch at 0x000000" — is unaffected by the VPP-check bypass.
- **Files modified:** none (CLI flag only)
- **Verification:** transcripts captured in `204-BENCH-TRACER.md`; the negative and positive controls both produced the predicted, distinct outcomes.
- **Committed in:** `239622b0` (bench record)

---

**Total deviations:** 2 auto-fixed (both Rule 3 — blocking environmental issues, neither touching product source). **Impact on plan:** Both were necessary to complete the task as designed; neither is scope creep and neither weakens any claim the bench record makes.

## Issues Encountered

- **Chip-ID readback mismatch, flagged rather than silently resolved.** The un-forced first read reported `Chip ID 0x1818 does not match expected ID 0xda08` (the database's `chip_id_value` for `W27C512,W27E512`). This is most plausibly the same VPP-sensing unreliability already recorded for this rig — the returned bytes (`18 18`) match the repeating low-address data pattern already present in the array rather than a recognizable device-ID encoding, consistent with the ID-sense step not actually reaching elevated-VPP mode. This is inference, not a measurement. Recorded in `204-BENCH-TRACER.md` and logged to `.planning/WINDOWS.md` (entry 3, kind `unmet-truth`, status `open`) for operator/UAT confirmation rather than assumed away. It does not affect the validity of the refused/served/byte-identical claims, which hold for whatever physical part was in the socket throughout the run.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 03 (ordinal 4 retirement) can proceed: the gate re-anchor pattern, the reserved-ordinal note shape, and the host guard-test literal-conversion pattern are all established here and repeat directly.
- Plan 05 (four-role bench matrix) inherits a working `$HOME/.local/share/gsd-204-oldhost-venv` and a proven `pio run -e leonardo -t upload` path — no re-discovery needed, though the venv should be re-verified present at that plan's start given this plan's own experience with the ephemeral home tree.
- **Outstanding for UAT / operator confirmation:** the chip-ID mismatch flagged above (`.planning/WINDOWS.md` entry 3) — confirm the seated part is genuinely a W27C512 before treating this record's part-identity claim as fully closed. The behavioral claims (refusal/served/byte-identical) do not depend on this confirmation.
- No branch in any of the three repositories touched `beta` at any point; all three remain on `v1.41-verification-to-host`.

---
*Phase: 204-the-command-surfaces-leave-the-firmware*
*Completed: 2026-09-22*
