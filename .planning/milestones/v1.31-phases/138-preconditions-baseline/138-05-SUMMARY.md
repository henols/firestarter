---
phase: 138-preconditions-baseline
plan: 05
subsystem: testing
tags: [platformio, unity, native-tests, host-stubs, trace-capture, eprom, golden-fixture, pytest, identity-gate]

# Dependency graph
requires:
  - phase: 138-03
    provides: "HOST_STUBS_RECORD_TIMING merged strobe+timing recorder, eprom_v131_expected.h comparator machinery (no frozen arrays yet), and the three per-protocol empirical dump files (session scratchpad)"
provides:
  - "EPROM_V131_TRACE_PROTO_07/_08/_0B: three frozen, empirically-captured merged strobe+timing arrays (198/221/201 entries) with provenance banners, consumed by full ordered positional equality"
  - "tests/golden/eprom_v131_trace_inventory.json + tests/test_golden_trace_identity_eprom_v131.py: a parallel, independent two-mechanism immutability pin for the fixture (D-04), proven to fail on three distinct break classes and restored"
  - "138-03-TRACE-CAPTURE.md Freeze record: committed blob SHA, break-class observations table, and the full re-measured firmware green state"
affects: [Phase 144 TEST-06 (diffs the new cadence against these three frozen arrays), 138-07 (discharges PREP-03 itself)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Mechanical dump-to-array grouping: a throwaway parser script re-derives pass/byte-group boundaries from the raw empirical dump via a strict grammar, rather than hand-transcribing 620 literal entries -- 100% grammar consumption is itself the correctness proof"
    - "Two-independent-mechanisms fixture pin (D-04), applied a second time in this repo: blob-SHA identity + per-array name/entry-count inventory + consumer-inclusion check, landed in one commit with the fixture it pins"
    - "Break-class proof before trust: three distinct planted breaks (blob SHA, inventory count, consumer-inclusion), each observed RED on exactly one leg and restored, before the gate's PASS is trusted"

key-files:
  created:
    - firestarter/tests/golden/eprom_v131_trace_inventory.json
    - firestarter/tests/test_golden_trace_identity_eprom_v131.py
  modified:
    - firestarter/test/native/avr/_shared/eprom_v131_expected.h
    - firestarter/test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp
    - .planning/phases/138-preconditions-baseline/138-03-TRACE-CAPTURE.md

key-decisions:
  - "Landed Task 1's fixture/suite changes and Task 2's inventory/gate in ONE amended firmware commit (67d6061), per the plan's own explicit repo_topology instruction and Task 2's literal 'git show --stat HEAD lists all three' acceptance criterion -- amending a just-created, unpushed local commit to honor an explicit plan-mandated commit structure, not a correction of a code mistake"
  - "Used a throwaway Python grammar-parser (scratchpad only, never committed) to mechanically re-derive pass/byte-group boundaries and verify byte-for-byte fidelity against the raw dumps, rather than hand-transcribing 620 literal array entries"
  - "recorded_at_head in the new inventory JSON is a point-in-time reference (Task 1's pre-amend commit SHA), matching the pre-existing SDP inventory's own non-self-referential convention -- verified live against the real analog file, not assumed"

requirements-completed: []

# Coverage metadata
coverage:
  - id: D1
    description: "Three empirically-captured merged strobe+timing streams (EPROM_V131_TRACE_PROTO_07/_08/_0B) frozen as literal arrays with provenance banners naming chip/pinout/bus_config/seed and >=5 non-obvious behaviours each; the three protocol cases in test_trace_eprom_v131.cpp switched to full ordered positional equality as the primary assertion, keeping overflow/determinism/response-code checks"
    verification:
      - kind: integration
        ref: "pio test -e native_trace_v131 -- 5 test cases: 5 succeeded (2 smoke + 3 protocol, each now asserting v131_assert_stream_equals)"
        status: pass
      - kind: other
        ref: "programmatic byte-for-byte re-derivation check: every array's parsed {kind,pin,value,us} sequence identical to the raw empirical dump, verified both before and after the header was written to disk"
        status: pass
    human_judgment: false
  - id: D2
    description: "The frozen assertion proven non-vacuous: a deliberate one-byte perturbation in the 0x07 array produced RED naming the diverging index and both values, while 0x08/0x0B stayed green; restored and re-confirmed GREEN"
    verification:
      - kind: integration
        ref: "pio test -e native_trace_v131 with a planted perturbation -- observed FAILED: 'diverges at index 15 -- expected {kind=1 pin=0 value=0x99 us=0}, recorded {kind=1 pin=0 value=0x3C us=0}'; restored, re-ran, 5/5 PASSED"
        status: pass
    human_judgment: false
  - id: D3
    description: "The fixture pinned by two independent mechanisms (blob-SHA + per-array name/entry-count inventory + consumer-inclusion check), landed in the same firmware commit as the fixture, without touching the pre-existing SDP identity gate"
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/test_golden_trace_identity_eprom_v131.py -q -- 6 passed"
        status: pass
      - kind: other
        ref: "git show --stat 67d6061 lists all four files (header, suite .cpp, inventory json, gate py); git diff --stat HEAD~1 -- tests/test_golden_trace_identity.py is empty"
        status: pass
    human_judgment: false
  - id: D4
    description: "Three distinct break classes (blob SHA, inventory entry count, consumer-inclusion) each independently observed RED on exactly the intended leg while the other five legs stayed green, then cleanly restored; a Freeze record appended to 138-03-TRACE-CAPTURE.md with the observations table and the full re-measured firmware green state"
    verification:
      - kind: other
        ref: "three break-and-restore cycles this session (138-03-TRACE-CAPTURE.md section 8); pio test -e native / -e native_nodevtools (141/141, 17 suites each), -e native_pinmap_provisional (10, 1 suite), -e native_trace_v131 (5, 1 suite), python3 -m pytest tests/ -q in place (227 passed, 0 failed)"
        status: pass
    human_judgment: false

# Metrics
duration: 45min
completed: 2026-08-09
status: complete
---

# Phase 138 Plan 05: Preconditions & Baseline — Golden-Trace Freeze Summary

**Three empirically-captured 27C write-loop traces (198/221/201 merged entries) frozen as literal arrays with provenance banners, pinned by a parallel two-mechanism identity gate that was proven to fail on three independent break classes before being trusted.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-08-08T23:30:36Z (approx., per STATE.md's pre-execution timestamp)
- **Completed:** 2026-08-09T00:16:00Z
- **Tasks:** 3
- **Files modified:** 5 (2 created, 3 modified)

## Accomplishments

- Pasted `EPROM_V131_TRACE_PROTO_07/_08/_0B` into `eprom_v131_expected.h` as literal, byte-for-byte
  verified-identical arrays (198/221/201 entries, matching 138-03's measured merged lengths exactly),
  each with a provenance banner naming the chip, pinout key, derived `bus_config`, the seeded
  target bytes with converge-after values, an explicit empirical-capture claim, and five-plus
  non-obvious behaviours per array — including two genuinely new findings surfaced while writing
  accurate comments: `mem_util_calculate_top_address_register`'s hardcoded `pins==28`
  `CTRL_ADDRESS_LINE_17` correction (0x07 only), and AM2716's `static_high_mask` realized as a
  permanent one-time MSB=0x20 latch (0x0B only, never elided again after the first byte). Switched
  all three protocol cases in `test_trace_eprom_v131.cpp` from soundness-only assertions to full
  ordered positional equality (`v131_assert_stream_equals`) as the primary check, keeping the
  pre-existing overflow/determinism/response-code assertions. Proved the frozen assertion
  non-vacuous with a real perturb-observe-RED-restore-observe-GREEN cycle.
- Authored `tests/golden/eprom_v131_trace_inventory.json` and
  `tests/test_golden_trace_identity_eprom_v131.py` — a parallel module (never a refactor of, or
  import from, the pre-existing `test_golden_trace_identity.py`) copying the SDP fixture's proven
  six-assertion, two-independent-mechanism pin exactly, with `_FIXTURE_PATH`/`_INVENTORY_JSON`/
  `_CONSUMERS`/`_ARRAY_DECL_RE` re-pointed and the non-vacuity floor set to 3. 6/6 passed.
- Exercised three distinct break classes against the live gate — blob SHA, inventory entry count,
  and consumer-inclusion — each observed RED on exactly its intended assertion (naming the
  diverging index/value or the missing include) while the other five legs stayed green, then
  cleanly restored. Re-measured the full firmware green state after the freeze: `native` and
  `native_nodevtools` both 141/141 cases across 17 suites, `native_pinmap_provisional` 10/10 across
  1 suite, `native_trace_v131` 5/5, and `python3 -m pytest tests/ -q` run in place inside
  `/workspaces/firestarter` at 227 passed / 0 failed (221 pre-existing + 6 new). Appended a Freeze
  record with all of this to `138-03-TRACE-CAPTURE.md`.

## Task Commits

Tasks 1 and 2 landed together in **one** firmware commit, per the plan's own explicit
`repo_topology` instruction ("the fixture and its inventory land in ONE firmware commit") and Task
2's literal acceptance criterion ("`git show --stat HEAD` lists all three"): Task 1 was committed
first, then Task 2's two new files were staged and the commit was **amended** (not a fresh commit)
to fold both tasks' firmware-file changes into a single, unpushed, local commit — see Issues
Encountered for why.

1. **Task 1: Paste the three empirical arrays and switch the cases to full positional equality** —
   initially committed as `3dad645`, superseded by the amend below (same content, folded into Task
   2's commit) — `firestarter`
2. **Task 2: Commit the inventory and the parallel identity gate in one firmware commit** —
   `67d6061` (feat) — `firestarter` — combined commit covering all four files from Tasks 1+2:
   `eprom_v131_expected.h`, `test_trace_eprom_v131.cpp`, `eprom_v131_trace_inventory.json`,
   `test_golden_trace_identity_eprom_v131.py`
3. **Task 3: Prove the identity gate fails, then re-establish the full firmware green state** —
   `8ac7a476` (docs) — meta (`138-03-TRACE-CAPTURE.md` Freeze record). No firmware commit for Task
   3 itself: all three break-class experiments were planted, observed, and fully reverted in the
   working tree before this commit — `git -C firestarter status --porcelain` was empty when it ran.

**Plan metadata:** (this commit, immediately following) — meta

## Files Created/Modified

- `firestarter/test/native/avr/_shared/eprom_v131_expected.h` (modified, +447/-11 lines) — three
  frozen arrays + provenance banners, replacing the "none yet" placeholder
- `firestarter/test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp` (modified) — the
  three protocol cases now assert full positional equality as their primary check
- `firestarter/tests/golden/eprom_v131_trace_inventory.json` (created) — blob SHA + per-array
  name/entry-count inventory + `frozen_for`/`measured_entry_counts`/`overflow_observed`
- `firestarter/tests/test_golden_trace_identity_eprom_v131.py` (created) — parallel six-assertion
  identity gate, 244 lines
- `.planning/phases/138-preconditions-baseline/138-03-TRACE-CAPTURE.md` (modified, +86 lines) —
  Freeze record section appended

## Decisions Made

- **Amend over a fresh commit for the Tasks 1+2 combination**: the plan's `repo_topology` note and
  Task 2's own acceptance criterion both explicitly require the fixture header, the inventory JSON,
  and the consuming `.cpp` to land in the **same** commit. Since Task 1 had already been committed
  separately (following the standard per-task commit protocol), the only way to satisfy this
  explicit, doubly-stated plan requirement was to amend that commit once Task 2's files were ready
  — done entirely locally, before any push, on a commit I had created moments earlier.
- **Mechanical grammar-parser over hand-transcription**: wrote a throwaway Python script
  (scratchpad only) that re-derives pass/byte-group boundaries from the raw dump via a strict
  grammar matching `eprom.cpp`/`memory.cpp`'s real structure (VPP-enable, per-pass VPE/P1
  assert→program→release→verify, with independently-elidable LSB/MSB/CONTROL latches). The parser
  achieving 100% consumption of all three dumps with zero adjustment is itself strong evidence the
  structural model — and therefore the grouping/comments — is correct, and a programmatic
  before/after diff against the raw dumps proved zero value was altered by the transcription.
- **`recorded_at_head` as a point-in-time, non-self-referential reference**: checked the
  pre-existing SDP inventory's own `recorded_at_head` against real git history and found it points
  to an unrelated Phase 124 Plan 02 commit, not the commit that added the fixture it describes —
  confirming this field is purely descriptive (asserted by none of the six tests) and that using
  Task 1's pre-amend commit SHA here is a legitimate, precedent-matching choice.

## Deviations from Plan

None — plan executed exactly as written. All three tasks' automated `<verify>` blocks and every
acceptance criterion in `138-05-PLAN.md` passed; no bug, missing functionality, or architectural
question arose that required a Rule 1-4 classification. Two process-level issues did require
problem-solving mid-execution — see Issues Encountered.

## Issues Encountered

- **Commit-ordering self-correction (not a code defect).** I initially committed Task 1 as its own
  atomic commit (standard per-task protocol), then discovered Task 2's acceptance criteria required
  header+inventory+suite-`.cpp` in the **same** commit. Resolved by staging Task 2's two new files
  and running `git commit --amend` on Task 1's just-created, unpushed commit — combining both
  tasks' firmware-file changes into the single commit (`67d6061`) the plan's own repo topology
  mandates. No push occurred at any point; no shared history was rewritten.
- **A pre-authored gate leg was genuinely unreachable on the first attempt — caught live, exactly
  as the plan's known-traps note warned.** My first attempt at Task 3's Leg 1 (blob-SHA break)
  edited the fixture header in the working tree only, ran the gate, and it stayed green — silently.
  The reason: `test_blob_sha_matches_the_recorded_inventory` compares against
  `git rev-parse HEAD:<path>` (the **committed** blob), never the live file, so an uncommitted edit
  is invisible to it by design. I recognized this was the "unreachable leg" trap rather than a
  green pass, committed the perturbation temporarily (`HEAD:<path>` then actually changed),
  re-ran, observed the intended RED with both SHAs named, and restored via `git reset --soft
  HEAD~1` + `git checkout HEAD -- <path>` (the latter chosen deliberately over bare
  `git checkout -- <path>`, which restores from the index — still holding the perturbed content
  after a `--soft` reset — not from `HEAD`; this second, more subtle trap was also caught live
  before trusting the restore).
- **Two of the plan's own acceptance-criteria lines are imprecise, verified against the trusted
  analog rather than force-satisfied.** (1) `grep -c 'pytest.skip\|@pytest.mark.skipif'
  tests/test_golden_trace_identity_eprom_v131.py` is stated to be `0`, but the self-scanning test
  this file must carry (mirroring the analog exactly) necessarily contains both substrings as
  comparison string literals — a plain grep cannot distinguish "an active skip call" from "a string
  literal checking for one." Confirmed the pre-existing, trusted `test_golden_trace_identity.py`
  returns the identical count (2) for the identical reason before concluding this criterion's
  literal text is unsatisfiable for any correct implementation of this pattern; the real test
  (`test_git_is_required_not_optional`, which uses line-anchored `startswith()`) passes. (2) The
  plan states the SDP inventory has "eight" `meta` keys; the real file has seven. Copied all seven
  plus the three new v1.31-specific keys (ten total), matching the intent rather than an
  arithmetic slip in the planning documentation. Neither observation changed anything about the
  deliverable itself — both are noted here per the "measurement wins over a stated/derived figure"
  precedent this phase has already established twice (RESEARCH's 174-strobe estimate, D-06/D-07).

## User Setup Required

None — no external service configuration required. All work is native (host-side) test
infrastructure plus a meta-repo documentation append.

## Next Phase Readiness

- All three of Phase 144's TEST-06 prerequisites are in place: a real, empirically-captured
  pre-change trace exists for all three protocols, frozen and pinned by two independent
  mechanisms, with a proven-non-vacuous full-stream comparator ready to diff the new cadence
  against once Phase 141 lands.
- **PREP-03 remains open** (`[ ]` in `REQUIREMENTS.md`) — this plan produces further evidence
  toward it but ticks nothing, per its own `may_tick_requirements: []`. Plan 138-07 is the plan
  that discharges PREP-03.
- The existing SDP identity gate (`tests/test_golden_trace_identity.py`) is confirmed byte-unchanged
  (`git diff --stat HEAD~1` empty) and still self-enforcing (its own six assertions were not
  touched, imported from, or parameterised).
- No push, no CI dispatch, and no write-path (`src/`) edit occurred at any point in this plan —
  confirmed via `git status --porcelain src/` before, during (after each break-restore cycle), and
  after every task.
- The throwaway grammar-parser script used to derive the array groupings lives only in the session
  scratchpad (`/tmp/.../138-05-work/`), was never committed, and is not needed again — the frozen
  arrays are now the durable artifact.

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter/test/native/avr/_shared/eprom_v131_expected.h`
- FOUND: `/workspaces/firestarter/test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp`
- FOUND: `/workspaces/firestarter/tests/golden/eprom_v131_trace_inventory.json`
- FOUND: `/workspaces/firestarter/tests/test_golden_trace_identity_eprom_v131.py`
- FOUND: `/workspaces/.planning/phases/138-preconditions-baseline/138-03-TRACE-CAPTURE.md`
- FOUND commit (firestarter): `67d6061`
- FOUND commit (meta): `8ac7a476`
- CONFIRMED not-in-firestarter: `8ac7a476` (correctly meta-only)

No missing items.

---
*Phase: 138-preconditions-baseline*
*Completed: 2026-08-09*
