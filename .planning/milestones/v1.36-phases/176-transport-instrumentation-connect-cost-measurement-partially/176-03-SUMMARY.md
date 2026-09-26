---
phase: 176-transport-instrumentation-connect-cost-measurement-partially
plan: 03
subsystem: instrumentation
tags: [transport-health, ring-fence, gate-1.8d, dev-test, diagnostic-report, serial-comm]

requires:
  - phase: 176-transport-instrumentation-connect-cost-measurement-partially
    provides: "plan 176-02's timeouts/probe_timeouts scoping, seven-key transport_health pin, MEAS-02/03 recorded basis"
provides:
  - "resync_length_missing and resync_body_truncated wired end to end from the two re-sync branches inside _read_and_parse_lines, the last two of RPT-C1's four named sites"
  - "The v1.9 ring-fence SHA-256 deliberately re-pinned from 6d9e4fe4b67b78c110418305113b275174f16b2ecc9e0f55fbf5d9a623398184 to 8b77800003a44fb21f2054fe8d0584e804648a76e52c3f23f55f06df74127b41, with the Phase 176 re-pin argument recorded in the test docstring alongside the surviving Phase 65-01 paragraph"
  - "transport_health at its final nine keys; both new counters placed in _SUSPECT_SCANNED_FIELDS (a re-sync is genuinely abnormal on a healthy link)"
  - "The adjacency case proven: a single get_response call whose stream re-syncs on a truncated frame and then times out raises BOTH resync_body_truncated and timeouts by exactly one each"
  - "The re-pinned fence proven to still discriminate: a one-line body change is SEEN red with the GATE-1.8d VIOLATION message before being restored"
affects: [176-04, 176-05]

actuals:
  tokens: 6130
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Unconditional counter, never probe_scope()-routed: record_resync_length_missing()/record_resync_body_truncated() differ from record_response_timeout() in that a re-sync means the same thing whether or not a probe is in progress, so neither is routed by ambient scope state"
    - "Deliberate ring-fence re-pin under a blocking-human checkpoint, with the digest, the phase, what changed and the not-a-transport-path-change argument accumulated in the test docstring rather than replacing the prior re-pin's paragraph (same shape as the Phase 65-01 precedent)"
    - "Anti-vacuity against a merged-counter failure mode: a swap weakening (w3) that keeps the total count identical while breaking both per-counter assertions, proving the legs are per-counter and not a sum"
    - "Anti-vacuity against fence neutering: after a deliberate re-pin, a fifth weakening (a one-line body change) is SEEN red against the NEW pin before the pin is trusted"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/transport_counters.py
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_serial_comm.py
    - firestarter_app/tests/test_transport_counters.py
    - firestarter_app/tests/test_diagnostic_report.py
    - firestarter_app/tests/test_blast_radius_invariance.py
    - firestarter_app/tests/fixtures/reports/*.json (16 files, two added lines each)

key-decisions:
  - "Checkpoint answer: **approved** (transcribed verbatim, see below). The deliberate re-pin route was taken; the logging-handler fallback (RESEARCH section 7 Option 2) was not needed."
  - "Placed both counter increments strictly between each branch's existing logger.warning(...) call and its existing continue, per the plan's placement discipline -- no read, no branch on a wire byte, no start_time write."
  - "For the ring-fence anti-vacuity weakening (rc_fence), chose the whitespace-only-line variant over the swap-a-call-name variant (both are named as acceptable in the plan) -- it is unambiguous as a pure textual change with zero semantic overlap with weakening w3's swap, keeping the two anti-vacuity legs conceptually distinct in the transcript."
  - "Recorded the new Phase 176 re-pin paragraph directly below the updated Pinned SHA-256 header line, ahead of the surviving Phase 65-01 paragraph -- reverse-chronological, matching how the header itself was already updated in place at the prior re-pin."

requirements-completed: []

coverage:
  - id: D1
    description: "A magic preamble with no length bytes behind it raises resync_length_missing by exactly one and moves no other counter"
    requirement: "RPT-C1"
    verification:
      - kind: unit
        ref: "tests/test_transport_counters.py#test_magic_preamble_with_no_length_bytes_raises_resync_length_missing_and_nothing_else"
        status: pass
    human_judgment: false
  - id: D2
    description: "A declared frame length longer than the bytes available raises resync_body_truncated by exactly one and moves no other counter"
    requirement: "RPT-C1"
    verification:
      - kind: unit
        ref: "tests/test_transport_counters.py#test_declared_length_longer_than_body_raises_resync_body_truncated_and_nothing_else"
        status: pass
    human_judgment: false
  - id: D3
    description: "The adjacency case: a single get_response call whose stream first re-syncs on a truncated frame and then runs out of time raises BOTH resync_body_truncated and timeouts by exactly one each -- neither merged nor suppressing the other"
    requirement: "RPT-C1"
    verification:
      - kind: unit
        ref: "tests/test_transport_counters.py#test_truncated_frame_then_timeout_raises_both_resync_body_truncated_and_timeouts"
        status: pass
    human_judgment: false
  - id: D4
    description: "The ring-fence test is green against a deliberately re-pinned digest, with the Phase 176 argument recorded in the docstring alongside the surviving Phase 65-01 paragraph and the GATE-1.8d VIOLATION message unchanged"
    requirement: "RPT-C1"
    verification:
      - kind: unit
        ref: "tests/test_serial_comm.py#test_read_and_parse_lines_ringfence_unchanged"
        status: pass
      - kind: other
        ref: "evidence/176-03-ringfence-and-resync.txt (digest_matches_pin=True, digest_changed=True, records_phase_176=True, keeps_65_01_paragraph=True, keeps_violation_message=True)"
        status: pass
    human_judgment: false
  - id: D5
    description: "All four RPT-C1 sites now increment a real, report-reachable counter; transport_health carries nine keys, both new counters placed in the suspicion domain"
    requirement: "RPT-C1, RPT-C2"
    verification:
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_transport_not_measured"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_to_dict_transport_health_key_list_is_pinned"
        status: pass
    human_judgment: false
  - id: D6
    description: "Phase 174 oracle green before and after at 114 passed, nine-key pin, all 16 snapshots regenerated in the same commit as the production change (two insertions, zero deletions each)"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py + tests/test_rekey_ledger.py (114 passed)"
        status: pass
      - kind: other
        ref: "tools/snapshot_report_shapes.py --check (exit 0, 16 files, two insertions each)"
        status: pass
    human_judgment: false
  - id: D7
    description: "Anti-vacuity: both counter sites and the adjacency leg SEEN red under four independent weakenings (including a swap proving the legs are per-counter, not a sum), and the re-pinned fence SEEN red under a one-line body change before being restored"
    verification:
      - kind: other
        ref: "evidence/176-03-anti-vacuity-red-green.txt (rc_w1..rc_w4=1, rc_fence=1, rc_clean=0, >=5 failed lines, final N passed)"
        status: pass
    human_judgment: false
  - id: D8
    description: "Full app suite green (2190 passed, up from 2183 at wave 2 close), ruff clean, mypy watermark unmoved at 35, zero comment lines added to any file this plan touched"
    verification:
      - kind: unit
        ref: "pytest tests/ (2190 passed, 32 snapshots passed)"
        status: pass
      - kind: other
        ref: "ruff check / ruff format --check / tools/check_mypy_watermark.py (35, watermark: 35)"
        status: pass
    human_judgment: false

duration: 50min
completed: 2026-09-04
status: complete
---

# Phase 176 Plan 03: Both re-sync counters wired inside the v1.9 ring fence, digest re-pinned deliberately Summary

**The two remaining RPT-C1 sites -- `resync_length_missing` and `resync_body_truncated` -- are now wired from inside `_read_and_parse_lines`, the v1.9 ring-fence's SHA-256 was deliberately re-pinned from `6d9e4fe4b67b78c110418305113b275174f16b2ecc9e0f55fbf5d9a623398184` to `8b77800003a44fb21f2054fe8d0584e804648a76e52c3f23f55f06df74127b41` under an operator-approved blocking-human checkpoint, and `transport_health` now carries its final nine keys.**

## Checkpoint Resolution

**Checkpoint:** "Checkpoint: approve the deliberate v1.9 ring-fence re-pin before it lands" (`gate="blocking-human"`)

**Operator's answer, transcribed verbatim:** `approved`

Per the checkpoint's own `<acceptance_criteria>`, this was resolved by the orchestrator before this executor was spawned; the orchestrator's own pre-checkpoint verification (fence header names exactly four invariants, both re-sync branches are shaped `if <cond>: logger.warning(...); continue` with no read/branch/`start_time` write added, the Phase 65-01 precedent is real, v1.9 is paused since 2026-06-01 at Phase 44) is recorded verbatim in this plan's dispatch context. Task 1 proceeded directly on `approved`; the logging-handler fallback (RESEARCH section 7 Option 2) was never invoked.

**Digest transition:**
- **Previous (pinned at Phase 65-01):** `6d9e4fe4b67b78c110418305113b275174f16b2ecc9e0f55fbf5d9a623398184`
- **New (pinned at Phase 176 plan 03):** `8b77800003a44fb21f2054fe8d0584e804648a76e52c3f23f55f06df74127b41`
- **Argument (recorded in `tests/test_serial_comm.py`'s `test_read_and_parse_lines_ringfence_unchanged` docstring, same shape as the Phase 65-01 paragraph):** both re-sync branches now call `transport_counters.record_resync_length_missing()` / `.record_resync_body_truncated()` beside their existing `logger.warning(...)`, before the existing `continue`. Not a transport-path change: no new `read()` call, no new branch on a wire byte, and no write to `start_time`, so none of the byte-by-byte read loop, the magic-preamble dispatch, the frame-length read, or the timeout reset semantics is affected.

## Performance

- **Duration:** ~50 min (includes a ~7 min full-suite run)
- **Started:** 2026-09-04T21:33:00Z (approx, immediately after 176-02 closed)
- **Completed:** 2026-09-04T22:23:00Z
- **Tasks:** 2 (Task 1 instrumentation + re-pin, Task 2 anti-vacuity)
- **Files modified:** 4 production files + 4 test files + 16 snapshot fixtures (all in one commit)

## Accomplishments

- `transport_counters.py` gained `resync_length_missing`/`resync_body_truncated` counters and `record_resync_length_missing()`/`record_resync_body_truncated()` -- unconditional increments, explicitly never routed by `probe_scope()` (documented distinction from `record_response_timeout()`).
- `serial_comm.py`'s two re-sync branches inside `_read_and_parse_lines` each gained exactly one increment line, placed between the existing `logger.warning(...)` and the existing `continue`. This is the only change to the ring-fenced generator body.
- `tests/test_serial_comm.py`'s `_PINNED_SHA256` re-pinned to the new digest, with a Phase 176 paragraph recorded in the docstring alongside the surviving Phase 65-01 paragraph and the `GATE-1.8d VIOLATION` assertion message left byte-identical.
- `diagnostic_report.py`: `TransportHealth` gained both fields in alphabetical position among the counters, both are substituted in `_transport_dict()`, both are in `_SUSPECT_SCANNED_FIELDS` (a re-sync is genuinely abnormal on a healthy link), and the class docstring now lists all five wired counters across Phase 176 plans 01-03.
- `cli_handlers.py`'s `dev_test` assigns both new fields from the existing post-`run_plan` snapshot, in the same block as the three earlier assignments.
- `tests/test_transport_counters.py` gained three new tests: the two direct re-sync legs (driven through `_read_and_parse_lines` directly so the timeout site is not also tripped) and the adjacency case (driven through `get_response`, where tripping both `resync_body_truncated` and `timeouts` on one call is the point).
- Phase 174's `_TRANSPORT_HEALTH_KEYS` pin moved from seven keys to the final nine (sorted), the next-key guard was dropped and replaced with an exact-nine-entries assertion, `test_transport_not_measured`'s key tuple extended, and all 16 committed report snapshots were regenerated in the SAME commit as the production change -- two added lines each, zero deletions, `--check` confirms zero drift.
- Task 2's anti-vacuity round recorded in `evidence/176-03-anti-vacuity-red-green.txt`: w1 (deleted the length-missing increment), w2 (deleted the body-truncated increment), w3 (swapped the two increments -- breaks both per-counter legs while a naive total-count assertion would still pass, proving the legs are per-counter), w4 (deleted the pre-existing `timeouts` increment in `get_response` -- breaks the adjacency leg specifically while the two direct re-sync legs stay green). A fifth weakening then proved the re-pinned fence still discriminates: a whitespace-only line added inside `_read_and_parse_lines`'s body was SEEN red with the `GATE-1.8d VIOLATION` message before being restored. All five weakenings restored to a clean, all-green working tree (confirmed via `git status --porcelain`) before this SUMMARY was written.

## Task Commits

Committed atomically inside the `firestarter_app` submodule (on `gsd/v1.36-dev-test-fidelity`):

1. **Task 1: Instrument both re-sync branches and re-pin the ring-fence digest in the same commit** - `1483181` (feat)

Task 2 (anti-vacuity) produced no separate commit: every weakening was reverted via `git checkout -- firestarter/serial_comm.py` before the next weakening, and the working tree was confirmed clean (`git status --porcelain`, no output) before this SUMMARY was written. The evidence transcripts are the durable record of Task 2's work.

**Plan metadata:** not committed in `/workspaces` -- see Deviations below (this run's execution-context instructions override the plan's own `<output>` section, which called for a second `/workspaces` commit).

## Files Created/Modified

- `firestarter_app/firestarter/transport_counters.py` - two new unconditional counters + `record_resync_length_missing()`/`record_resync_body_truncated()`
- `firestarter_app/firestarter/serial_comm.py` - one increment line added to each re-sync branch inside `_read_and_parse_lines` (the ONLY change to the ring-fenced body)
- `firestarter_app/firestarter/diagnostic_report.py` - `TransportHealth` gains both fields, both in `_SUSPECT_SCANNED_FIELDS`, docstrings updated
- `firestarter_app/firestarter/cli_handlers.py` - `dev_test` assigns both new fields from the snapshot
- `firestarter_app/tests/test_serial_comm.py` - `_PINNED_SHA256` re-pinned, Phase 176 paragraph added to the docstring
- `firestarter_app/tests/test_transport_counters.py` - three new tests for the two re-sync sites and the adjacency case
- `firestarter_app/tests/test_diagnostic_report.py` - `test_transport_not_measured` extended with both new field names
- `firestarter_app/tests/test_blast_radius_invariance.py` - `_TRANSPORT_HEALTH_KEYS` pin moved to nine keys, next-key guard replaced with an exact-count assertion
- `firestarter_app/tests/fixtures/reports/*.json` (16 files) - regenerated snapshots carrying both new counters

## Decisions Made

- Checkpoint answered `approved`; deliberate re-pin route taken (see Checkpoint Resolution above).
- Chose the whitespace-only-line variant for the Task 2 fence-still-bites weakening, to keep it conceptually distinct from w3's swap.
- Recorded the new re-pin paragraph immediately below the updated header line, ahead of the surviving Phase 65-01 paragraph (reverse-chronological).

## Deviations from Plan

None - plan executed exactly as written. The checkpoint was pre-resolved by the orchestrator with a verbatim `approved` answer, and Task 1/Task 2 proceeded on that basis exactly per their own `<action>` and `<acceptance_criteria>` text. The only deliberate departure from the plan's own `<output>` instructions is the second `/workspaces` commit, which this run's execution-context instructions explicitly override (see below).

**[Execution-context override] Second `/workspaces` commit not made**
- **Found during:** reading this run's execution-context instructions before Task 1
- **Issue:** `176-03-PLAN.md`'s own `<output>` section calls for a second plain `git commit` in `/workspaces` carrying the gitlink and the `.planning` evidence.
- **Fix:** Per this run's explicit override ("Write `176-03-SUMMARY.md` and `evidence/*.txt` ... and leave them UNCOMMITTED -- the orchestrator commits meta-repo files after the wave"), `176-03-SUMMARY.md` and both evidence files are left uncommitted in `/workspaces`. The `firestarter_app` gitlink is also left dirty, as instructed.
- **Files affected:** `.planning/phases/176-transport-instrumentation-connect-cost-measurement-partially/176-03-SUMMARY.md`, `evidence/176-03-ringfence-and-resync.txt`, `evidence/176-03-anti-vacuity-red-green.txt`
- **Verification:** `git status --short` at `/workspaces` shows exactly the gitlink diff plus the two untracked evidence files; no other drift.
- **Committed in:** N/A (deliberately left uncommitted per this run's instructions)

---

**Total deviations:** 1 (execution-context override, not a plan deviation in the Rule 1-4 sense). **Impact on plan:** None on production behavior; purely a commit-boundary instruction from this run's dispatch context.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All four RPT-C1 sites are now wired end to end: `decode_failures`, `timeouts`, `probe_timeouts` (plans 01-02) and `resync_length_missing`/`resync_body_truncated` (this plan). `transport_health` is at its final nine keys.
- The v1.9 ring-fence has been deliberately re-pinned once more, with the full history (Phase 65-01, Phase 176 plan 03) preserved in the test docstring for the next reader.
- The Phase 174 oracle is green at 114 passed, matching the precondition measured before this plan touched anything. Full app suite: 2190 passed (up from 2183 at wave 2 close), 32 snapshot checks passed; `ruff check`, `ruff format --check` and the mypy watermark (`35 (watermark: 35)`) all hold.
- RPT-C1 and RPT-C2 remain Pending per this plan's own `<output>` instruction not to mark any requirement Complete -- a later plan in this phase closes them once the whole software half is sealed.
- No blockers for 176-04.

## Self-Check: PASSED

- `firestarter_app/firestarter/transport_counters.py` exists and contains `def record_resync_length_missing`: confirmed.
- `firestarter_app/firestarter/serial_comm.py` contains both `record_resync_length_missing()` and `record_resync_body_truncated()` calls: confirmed.
- `firestarter_app/tests/test_transport_counters.py` contains `resync_body_truncated`: confirmed.
- Commit `1483181` exists in `firestarter_app`'s `git log`: confirmed.
- `tests/test_blast_radius_invariance.py` + `tests/test_rekey_ledger.py` at 114 passed both before and after this plan: confirmed.
- Full `firestarter_app` suite at 2190 passed, 32 snapshots passed, exit code 0: confirmed.
- `ruff check`, `ruff format --check`, mypy watermark (`35 (watermark: 35)`): confirmed.
- `evidence/176-03-ringfence-and-resync.txt` and `evidence/176-03-anti-vacuity-red-green.txt` both exist with all required markers (`rc=0` x3, `rc_w1..rc_w4=1`, `rc_fence=1`, `rc_clean=0`, `GATE-1.8d VIOLATION`): confirmed.
- `firestarter_app` working tree clean (`git status --porcelain`, no output) after all anti-vacuity weakenings were restored: confirmed.
- Zero comment lines added to any file created or edited this plan (`transport_counters.py`, `serial_comm.py`, `diagnostic_report.py`, `cli_handlers.py`, `test_transport_counters.py` all checked with `/usr/bin/grep`): confirmed.

---
*Phase: 176-transport-instrumentation-connect-cost-measurement-partially*
*Completed: 2026-09-04*
