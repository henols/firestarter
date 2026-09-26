---
phase: 144-tests-build-verification
plan: 04
subsystem: testing
tags: [pytest, golden-trace, gate, d-18, firmware, state-machine]

# Dependency graph
requires:
  - phase: 144-tests-build-verification
    provides: "144-03's re-frozen firestarter/test/native/avr/_shared/eprom_v131_expected.h (91/115/59 entries, new post-v1.31 cadence) and the unchanged eprom_v131_expected_prechange.h (198/221/201 entries, blob ca3e09f164e6e1c541ecb63d15bbebf5bce41d70)"
provides:
  - "firestarter/tests/test_trace_segment_exhaustiveness_v131.py -- D-07's machine-checked exhaustiveness gate, partitioning all 885 entries across both streams into six named, attributed segments"
  - "Two D-18 planted-violation proofs (unclassifiable pin, length-preserving delete+duplicate) with RED and GREEN transcripts"
  - "Per-segment old-vs-new count table (via __main__), evidence for plan 144-07's record"
affects: [144-07]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-failure-mode state machine: a hard vocabulary check (_validate_known_primitive) raises immediately on a truly foreign (kind,pin); a separate, non-tautological group-shape scan leaves an in-vocabulary-but-malformed entry OUT of every segment set instead of raising, so the exhaustiveness assertion in the calling test (not the state machine itself) is what a delete+duplicate mutation actually trips"
    - "Import-time env seams (FIRESTARTER_TRACE_SEGMENT_SCAN_NEW / _PRECHANGE) restricted to overriding a scan PATH only, never a segment name or the 885 denominator"
    - "Independent recount as a known-answer oracle: pulse_windows + verify_windows == an OE-strobe count computed WITHOUT reading segs at all, proving the classifier is not merely self-consistent"
    - "_run_gate_in_subprocess extended to accept multiple node ids in one child-process run (Plant B scopes to two legs at once)"
    - "Attribution map carries a non-empty citation for every segment name unconditionally, including one (teardown) that is never populated in either stream -- recorded explicitly as zero, never omitted"

key-files:
  created:
    - firestarter/tests/test_trace_segment_exhaustiveness_v131.py
  modified: []

key-decisions:
  - "State machine raises (_validate_known_primitive) only on a (kind,pin) combination outside the five-pin/four-kind vocabulary entirely -- never on a group-shape mismatch. An in-vocabulary entry that fails to complete a recognised 4/5/3-entry group idiom is left uncovered by every segment rather than raised, which is what makes test_every_entry_falls_in_exactly_one_segment's own union/disjointness assertion a genuine, non-tautological check rather than one that is trivially true by construction of a consuming parser"
  - "route_assert (the segment name) covers every CONTROL_REGISTER latch group that still has data/CE activity after it -- both the initial HV-route assert AND any later route release that is not the stream's final group -- per D-07's own naming; this is stated explicitly in the module so a future reader is not confused by a 'release' group living under an '_assert' name"
  - "Plant A mutates PROTO_07's index 21 (the OUTPUT_ENABLE-assert toggle) to pin=0x40 via a single deterministic .replace(...,1) against a literal-plus-position-comment anchor; Plant B mutates PROTO_07's index 22 (a payload data write) into a duplicate of index 10 (a CE-low strobe), verified empirically (via a throwaway probe script, discarded before commit) to produce a length-preserving gap at indices [22, 23] without raising"
  - "requirements-completed left empty in this SUMMARY, matching plan 144-01's precedent: this plan is explicitly forbidden from ticking TEST-06 -- plan 144-07 owns the consolidated eight-requirement flip"

patterns-established:
  - "A structural exhaustiveness gate over a merged strobe+timing trace needs TWO distinct failure modes (vocabulary vs. shape), not one, or a length-preserving corruption cannot be distinguished from a foreign-primitive corruption in the RED transcript"

requirements-completed: []  # Intentional -- see key-decisions. This plan evidences TEST-06; plan 144-07 flips it.

coverage:
  - id: D1
    description: "Six-segment state machine (init, route_assert, address_set, pulse, verify_read, teardown) partitions all 885 entries (620 pre-change + 265 new) across six arrays by set equality over range(len(array)) plus pairwise disjointness -- never a count sum"
    requirement: "TEST-06"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_trace_segment_exhaustiveness_v131.py#test_every_entry_falls_in_exactly_one_segment"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_trace_segment_exhaustiveness_v131.py#test_prechange_arrays_parse_to_the_recorded_lengths"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_trace_segment_exhaustiveness_v131.py#test_new_arrays_parse_to_the_captured_lengths"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_trace_segment_exhaustiveness_v131.py#test_total_attributed_entry_count_is_885"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every present segment carries a named attributing decision from Phases 140-143, including teardown's explicit zero-entry contribution (Phase 143 D-09/D-10: a successful block leaves the HV route energised)"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_trace_segment_exhaustiveness_v131.py#test_every_present_segment_has_a_named_attribution"
        status: pass
    human_judgment: false
  - id: D3
    description: "Known-answer self-test: pre-change 0x07 yields 7 pulse windows + 12 verify reads, matching an independently recounted total of 19 OUTPUT_ENABLE strobes -- proving the state machine is not merely self-consistent"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_trace_segment_exhaustiveness_v131.py#test_pre_change_0x07_pulse_and_verify_counts_match_the_output_enable_toggles"
        status: pass
    human_judgment: false
  - id: D4
    description: "Self-protection: two-half non-vacuity self-check, no-skip self-check, and concatenation-built needle-hygiene self-check"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_trace_segment_exhaustiveness_v131.py#test_scan_targets_are_non_vacuous"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_trace_segment_exhaustiveness_v131.py#test_this_module_cannot_be_silently_skipped"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_trace_segment_exhaustiveness_v131.py#test_own_needles_do_not_appear_verbatim_in_this_module"
        status: pass
    human_judgment: false
  - id: D5
    description: "D-18 proof: both planted violations (an unclassifiable pin; a length-preserving delete+duplicate) produce a locating RED in a child process; the GREEN is attributed to a non-empty two-stream parse with the known-answer self-test passing"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_trace_segment_exhaustiveness_v131.py#test_planted_unclassifiable_entry_is_located"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_trace_segment_exhaustiveness_v131.py#test_planted_delete_and_duplicate_defeats_a_count_only_check"
        status: pass
    human_judgment: false
  - id: D6
    description: "No file under firestarter/src/ or firestarter/test/ touched; neither fixture modified; whole firmware pytest suite green with zero regressions; native_trace_v131 still 5/5"
    verification:
      - kind: other
        ref: "git diff --stat HEAD -- src/ (0 lines); git status --porcelain -- src/ test/ (empty); python3 -m pytest tests/ -q (312 passed, up from the 301 pre-plan baseline); pio test -e native_trace_v131 (5/5 passed)"
        status: pass
    human_judgment: false

# Metrics
duration: ~34min
completed: 2026-08-14
status: complete
---

# Phase 144 Plan 04: Trace Segment Exhaustiveness Gate Summary

**A six-segment state machine partitions all 885 v1.31 trace entries (620 pre-change + 265 new) by set equality and disjointness, proving TEST-06's attribution is complete -- not merely counted -- with both D-18 plants seen RED for genuinely distinct reasons.**

## Performance

- **Duration:** ~34 min
- **Completed:** 2026-08-14T08:08:19Z
- **Tasks:** 2 completed
- **Files created:** 1 (`firestarter/tests/test_trace_segment_exhaustiveness_v131.py`, 1234 lines)

## Accomplishments

- Authored a standalone pytest gate that independently re-parses BOTH the frozen pre-change fixture
  (`eprom_v131_expected_prechange.h`, 620 entries) and the new post-v1.31 fixture
  (`eprom_v131_expected.h`, 265 entries), walking each of the six arrays with a structural state
  machine keyed on `kind`/`pin`/`value`/`us` and the `OUTPUT_ENABLE` toggle -- never on fixture
  comments, since the new capture carries only positional `/* N */` index comments.
- Proved exhaustiveness by set equality over `range(len(array))` plus pairwise disjointness for all
  six arrays, never a count sum -- a count match alone would hide a double-count paired with a drop.
- Built an attribution map (`_SEGMENT_ATTRIBUTION`) naming a Phase 140-143 decision for every one of
  the six segment names, including `teardown`'s zero-entry contribution recorded explicitly (Phase
  143 D-09/D-10: a successful block leaves the HV route energised, so neither successful-block capture
  contains a teardown group at all).
- Passed the F-07 known-answer self-test: pre-change `0x07` yields exactly 7 pulse windows and 12
  verify-read windows, matching an *independently recounted* total of 19 `OUTPUT_ENABLE` strobes --
  proof the state machine is not merely self-consistent.
- Proved the gate under D-18 with two planted violations, both run in a child process (the two
  `FIRESTARTER_TRACE_SEGMENT_SCAN_*` seams bind at import; `monkeypatch.setenv` cannot reach them):
  an unclassifiable pin (`0x40`) that the state machine raises on immediately with a locating message,
  and a length-preserving delete-and-duplicate that a count-only check would have passed but the
  set-equality assertion still catches.
- Left every `src/` file and both fixture headers byte-unchanged; the whole firmware pytest suite grew
  from 301 to 312 passed with zero regressions, and `native_trace_v131` remained 5/5.

## Task Commits

Each task was committed atomically (inside `firestarter/`, on the milestone branch):

1. **Task 1: Author the six-segment state machine, the partition assertion and the attribution map** -
   `9be07ba` (test) -- module docstring, both env seams, the parse technique (re-implemented, never
   imported, from `test_golden_trace_identity_eprom_v131.py`), the six-segment state machine
   (`_segment_indices`), the frozen `_SEGMENT_ATTRIBUTION` map, and Coverage 1-9 (parse lengths,
   exhaustiveness, attribution completeness, the known-answer self-test, the 885 total, two-half
   non-vacuity, no-skip, needle hygiene), plus the `__main__` per-segment table.
2. **Task 2: Prove both D-18 planted violations in a child process, and record the RED/GREEN pair** -
   `6cc4795` (test) -- `_run_gate_in_subprocess` (extended to accept multiple node ids in one child
   run), the fail-closed git helpers, and Coverage 10-11 (Plant A: unclassifiable pin; Plant B:
   length-preserving delete+duplicate).

**Plan metadata:** committed together with this SUMMARY (see final commit below, in the superproject).

## Files Created/Modified

- `firestarter/tests/test_trace_segment_exhaustiveness_v131.py` (new, 1234 lines) -- the exhaustiveness
  gate: `_parse_arrays_with_fields`/`_strip_comments` (the field-capturing parse technique, verified
  against all 620 pre-change entries by RESEARCH), `_segment_indices` and its three group-idiom
  matchers (`_matches_latch_group`, `_matches_payload_group`, `_matches_ce_window`), the frozen
  `_SEGMENT_ATTRIBUTION` map, eleven test functions (Coverage 1-11), the D-18 planted-violation
  machinery (`_run_gate_in_subprocess`, `_resolve_git`, `_git_hash_object`, `_git_porcelain`), and a
  `__main__` block printing the per-segment old-vs-new table for all three protocols.

## Decisions Made

- **Two distinct failure modes, deliberately.** `_validate_known_primitive` raises immediately (a hard,
  locating `AssertionError`) only when an entry's `(kind, pin)` is outside the five-pin/four-kind
  vocabulary entirely -- Plant A's exact shape. An entry that IS in-vocabulary but fails to complete
  any of the three recognised group idioms (4-entry latch group, 5-entry pulse-payload group, 3-entry
  chip-enable window) is left OUT of every segment's set instead of being raised on. This is what makes
  `test_every_entry_falls_in_exactly_one_segment`'s own union/disjointness assertion a *genuine* check:
  a naive "consume entries in a single advancing pass, raise on any shape mismatch" design would
  trivially guarantee full coverage by construction whenever it did not raise, which would make Plant
  B's length-preserving delete+duplicate indistinguishable in shape from Plant A's foreign-pin case (both
  would just be "some raised AssertionError"). Verified empirically before authoring the real gate, via
  a throwaway probe script (discarded, never committed) that confirmed both real fixtures still parse
  to a full, disjoint six-way partition under this lenient design, and that a specific delete+duplicate
  mutation produces a genuine two-entry gap (indices 22-23) without raising.
- **`route_assert` names both assert AND release groups.** Per D-07's own segmentation table, any
  `CONTROL_REGISTER` latch group with more data/CE activity after it is `route_assert`, regardless of
  whether its `value` is turning the HV route ON or OFF -- only the (never-observed, in either stream)
  trailing group after the very last data/CE strobe is `teardown`. Stated explicitly in the module so a
  future reader is not confused by a "release" group living under an "`_assert`" segment name.
- **Plant targets chosen for deterministic, unambiguous `.replace(...,1)` anchoring.** Both plants anchor
  on a literal entry-plus-position-comment string (e.g. `"{2, 0x04, 0x01, 0UL}, /* 21 */"`), which is
  unique enough (position comments restart per array, so the same literal text can appear once per
  array, but `.replace(...,1)` deterministically hits the first -- always inside `PROTO_07`, confirmed by
  index arithmetic before authoring) that the mutation's target array and index were known in advance,
  rather than discovered after the fact.

## Deviations from Plan

None - plan executed exactly as written. The state machine's exact algorithmic shape (vocabulary-check
vs. group-idiom-scan, as described above) was an implementation decision within the plan's explicit
constraints (set equality over `range(len(array))` plus disjointness; a locating raise for anything
"it cannot classify"; never a count sum; never keyed on comments; never testing the out-of-range 9-bit
control value), not a deviation from any of them.

## Issues Encountered

Two failure modes of my own module tripped its own naming checks before the first commit, both caught
and fixed during Task 1's own verification (i.e., before any commit, not a mid-task auto-fix under the
deviation rules):

- The module docstring's own prose (`"...copied structurally from test_golden_trace_identity_eprom_v131.py..."`)
  contained the literal substring `"from test_golden_trace_identity"`, tripping the plan's own
  `grep -c "from test_golden_trace_identity" ... | grep -x 0` verification step. Reworded to `"...defined
  in test_golden_trace_identity_eprom_v131.py..."`.
- A comment explaining WHY no segmentation rule may test the 9-bit `CTRL_VPP_VPE_DROP_ENABLE` value
  itself contained the literal string it was warning against, tripping the plan's
  `grep -c "0x100" ... | grep -x 0` verification step. Reworded to describe the value in prose ("one bit
  wider than the recorded 8-bit `value` field can hold") without spelling out the literal.

Both were caught by running the plan's own `<verify>` automated steps before staging anything, and
required no design change -- only rewording comments that happened to self-match the gate's own
exclusion checks.

Additionally, both planted-violation tests' own final S2-ceremony assertion
(`_git_porcelain(_REPO_ROOT) == ""`) legitimately failed when the module was run BEFORE its own Task 2
commit, because the module file itself (mid-edit) was the sole dirty entry in the tree -- an instance of
the same chicken-and-egg plan 144-01's own SUMMARY documented ("Issues Encountered" there). Resolved
identically: confirmed every OTHER assertion in both plants (returncode, message content, hash equality)
passed first, then committed Task 2, then re-ran to confirm full GREEN (11/11) with a clean porcelain --
no code change was needed.

## User Setup Required

None - no external service configuration required.

## D-18 Evidence (verbatim)

### RED transcript 1 -- Plant A: `test_planted_unclassifiable_entry_is_located`

Reproduced by replacing PROTO_07's `OUTPUT_ENABLE`-assert toggle at positional index 21
(`{2, 0x04, 0x01, 0UL}, /* 21 */`) with `{2, 0x40, 0x01, 0UL}, /* 21 */` in a scratch copy of the new
fixture, pointing `FIRESTARTER_TRACE_SEGMENT_SCAN_NEW` at it, and running only
`test_every_entry_falls_in_exactly_one_segment` in a child process:

```
RETURNCODE: 1
=== STDOUT ===
F                                                                        [100%]
=================================== FAILURES ===================================
________________ test_every_entry_falls_in_exactly_one_segment _________________

    def test_every_entry_falls_in_exactly_one_segment():
        """Coverage 3 -- D-07's core assertion. ..."""
        streams = (("prechange", _SCAN_PRECHANGE), ("new", _SCAN_NEW))
        for stream_label, path in streams:
            for array_name, entries in _parse_arrays_with_fields(path):
                label = f"{array_name} ({stream_label})"
>               segs = _segment_indices(entries, array_name=label)

tests/test_trace_segment_exhaustiveness_v131.py:622:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests/test_trace_segment_exhaustiveness_v131.py:465: in _segment_indices
    _validate_known_primitive(e, i, array_name)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

entry = (2, 64, 1, 0), index = 21
array_name = 'EPROM_V131_TRACE_PROTO_07 (new)'

    def _validate_known_primitive(entry, index, array_name):
        """..."""
        kind, pin, value, us = entry
        if kind == _KIND_STROBE_DATA:
            return
        if kind == _KIND_STROBE_PIN:
            if pin in (_PIN_LSB, _PIN_MSB, _PIN_OE, _PIN_CTRL, _PIN_CE):
                return
>           raise AssertionError(
                f"{array_name}: index {index} is unclassifiable -- "
                f"{_format_entry(entry)} matches none of the five known pins "
                f"(LSB=0x{_PIN_LSB:02X}, MSB=0x{_PIN_MSB:02X}, OE=0x{_PIN_OE:02X}, "
                f"CTRL=0x{_PIN_CTRL:02X}, CE=0x{_PIN_CE:02X})."
            )
E           AssertionError: EPROM_V131_TRACE_PROTO_07 (new): index 21 is unclassifiable -- (kind=2, pin=0x40, value=0x01, us=0) matches none of the five known pins (LSB=0x01, MSB=0x02, OE=0x04, CTRL=0x08, CE=0x20).

tests/test_trace_segment_exhaustiveness_v131.py:378: AssertionError
1 failed in 0.07s
```

The RED names the array (`EPROM_V131_TRACE_PROTO_07 (new)`), the positional index (`21`), and the full
`(kind,pin,value,us)` tuple including `0x40` -- never a bare count.

### RED transcript 2 -- Plant B: `test_planted_delete_and_duplicate_defeats_a_count_only_check`

Reproduced by replacing PROTO_07's payload data write at positional index 22
(`{1, 0x00, 0x55, 0UL}, /* 22 */`) with a duplicate of index 10's CE-low strobe
(`{2, 0x20, 0x00, 0UL}`) in a scratch copy of the new fixture -- so `PROTO_07`'s parsed length is
UNCHANGED (91 before, 91 after: a count-only check would have passed this mutation) -- and running both
`test_every_entry_falls_in_exactly_one_segment` and `test_new_arrays_parse_to_the_captured_lengths` in a
single child process:

```
real PROTO_07 length: 91
mutated PROTO_07 length: 91
(length UNCHANGED -- a count-only check would PASS this mutation)

RETURNCODE: 1
=== STDOUT ===
F.                                                                       [100%]
=================================== FAILURES ===================================
________________ test_every_entry_falls_in_exactly_one_segment _________________

    def test_every_entry_falls_in_exactly_one_segment():
        """Coverage 3 -- D-07's core assertion. ..."""
        ...
                missing = sorted(full_range - union)
                if missing:
                    detail = ", ".join(
                        f"index {idx} {_format_entry(entries[idx])}" for idx in missing
                    )
>                   raise AssertionError(
                        f"{label}: the union of the six segment index sets does "
                        f"NOT equal set(range(len(entries))) -- {len(missing)} "
                        f"index(es) uncovered by any segment: {detail}. A "
                        "count-only check (comparing totals) would NOT have "
                        "caught this -- coverage, not count, is what this "
                        "assertion proves."
                    )
E                   AssertionError: EPROM_V131_TRACE_PROTO_07 (new): the union of the six segment index sets does NOT equal set(range(len(entries))) -- 2 index(es) uncovered by any segment: index 22 (kind=2, pin=0x20, value=0x00, us=0), index 23 (kind=3, pin=0x00, value=0x00, us=3). A count-only check (comparing totals) would NOT have caught this -- coverage, not count, is what this assertion proves.

tests/test_trace_segment_exhaustiveness_v131.py:633: AssertionError
1 failed, 1 passed in 0.10s
```

`1 failed, 1 passed` -- the parse-lengths leg (`test_new_arrays_parse_to_the_captured_lengths`) PASSES,
proving the array length really is unchanged at 91, while the partition leg fails with an explicit
`"does NOT equal set(range(len(entries)))"` message naming the two uncovered indices -- the failure is
attributable to the set-equality assertion specifically, never to a length mismatch.

### GREEN -- full-module run, attributed to a non-empty two-stream parse

```
$ python3 -m pytest tests/test_trace_segment_exhaustiveness_v131.py -v
tests/test_trace_segment_exhaustiveness_v131.py::test_prechange_arrays_parse_to_the_recorded_lengths PASSED
tests/test_trace_segment_exhaustiveness_v131.py::test_new_arrays_parse_to_the_captured_lengths PASSED
tests/test_trace_segment_exhaustiveness_v131.py::test_every_entry_falls_in_exactly_one_segment PASSED
tests/test_trace_segment_exhaustiveness_v131.py::test_every_present_segment_has_a_named_attribution PASSED
tests/test_trace_segment_exhaustiveness_v131.py::test_pre_change_0x07_pulse_and_verify_counts_match_the_output_enable_toggles PASSED
tests/test_trace_segment_exhaustiveness_v131.py::test_total_attributed_entry_count_is_885 PASSED
tests/test_trace_segment_exhaustiveness_v131.py::test_scan_targets_are_non_vacuous PASSED
tests/test_trace_segment_exhaustiveness_v131.py::test_this_module_cannot_be_silently_skipped PASSED
tests/test_trace_segment_exhaustiveness_v131.py::test_own_needles_do_not_appear_verbatim_in_this_module PASSED
tests/test_trace_segment_exhaustiveness_v131.py::test_planted_unclassifiable_entry_is_located PASSED
tests/test_trace_segment_exhaustiveness_v131.py::test_planted_delete_and_duplicate_defeats_a_count_only_check PASSED

============================== 11 passed in 2.17s ===============================
```

The non-vacuity leg's own figures, confirmed against the real (non-seam-redirected) tree -- this GREEN is
attributed to a non-empty two-stream parse, never an unreachable leg:

| Stream | Arrays | Combined entries |
|---|---|---|
| pre-change | 3 (198 + 221 + 201) | 620 |
| new | 3 (91 + 115 + 59) | 265 |
| **Total** | **6** | **885** |

Known-answer figures (`test_pre_change_0x07_pulse_and_verify_counts_match_the_output_enable_toggles`):
**7 pulse windows + 12 verify-read windows = 19**, exactly matching an independently recounted total of
`OUTPUT_ENABLE` strobes on the pre-change `0x07` array.

Attributed-total figures (`test_total_attributed_entry_count_is_885`): pre-change subtotal **620**, new
subtotal **265**, grand total **885** -- all derived from `_segment_indices`'s own returned sets, never
from the raw parsed length alone.

### Whole-repo confirmation

```
$ git status --porcelain
(empty)
$ python3 -m pytest tests/ -q
312 passed in 16.49s
$ python3 -m pytest tests/test_golden_trace_identity_eprom_v131.py tests/test_protocol_branch_inventory.py tests/test_checker_convention.py -q
20 passed in 0.15s
$ git diff --stat HEAD -- src/
(empty)
$ git rev-parse HEAD:test/native/avr/_shared/eprom_v131_expected_prechange.h
ca3e09f164e6e1c541ecb63d15bbebf5bce41d70
$ pio test -e native_trace_v131
5 test cases: 5 succeeded
```

312 passed is the 144-03 baseline of 301 plus this plan's 11 new tests, with zero regressions. The three
named goldens/conventions this plan must leave undisturbed all pass. No file under `src/` changed across
either commit, and the pre-change fixture's blob SHA is unchanged from the value 144-03 froze it at.

## Per-Segment Old-vs-New Table (evidence for plan 144-07's record)

```
===== Protocol 0x07 (EPROM_V131_TRACE_PROTO_07) =====
segment           pre-change     new   delta
init                       5       5      +0
route_assert              31       4     -27
address_set               72      24     -48
pulse                     42      18     -24
verify_read               48      40      -8
teardown                    0       0      +0
TOTAL                    198      91    -107

===== Protocol 0x08 (EPROM_V131_TRACE_PROTO_08) =====
segment           pre-change     new   delta
init                       5       5      +0
route_assert              54      28     -26
address_set               72      24     -48
pulse                     42      18     -24
verify_read               48      40      -8
teardown                    0       0      +0
TOTAL                    221     115    -106

===== Protocol 0x0B (EPROM_V131_TRACE_PROTO_0B) =====
segment           pre-change     new   delta
init                       5       5      +0
route_assert              30       0     -30
address_set               76      12     -64
pulse                     42      18     -24
verify_read               48      24     -24
teardown                    0       0      +0
TOTAL                    201      59    -142
```

Each row's attribution (per `_SEGMENT_ATTRIBUTION`, full citations in the module):

| Segment | Attributed to |
|---|---|
| `init` | Phase 140 (`eprom_params_t.vpp_path`) + Phase 142 (`eprom_hv_route_mask()`) |
| `route_assert` | Phase 142 D-01/D-02 (route mask survives `set_address()`, so this group latches once per block instead of once per pass) |
| `address_set` | Phase 141 D-01 (the shared per-byte loop latches each address once per byte-visit, not once per old-cadence pass) |
| `pulse` | Phase 140 (DB pulse width, fixed) + Phase 141 D-01/D-02 (fixed-width pulse, verify, repeat) |
| `verify_read` | Phase 140 (`verify_mode`) + Phase 141 D-01/D-06 (per-pulse verify + the FF-rule's final-pass carve-out) |
| `teardown` | Phase 143 D-09/D-10 (a successful block leaves the route energised -- zero entries in either stream, recorded explicitly) |

**Honest boundary, restated:** this gate proves the attribution is COMPLETE (every one of the 885
entries lands in exactly one named segment, and every present segment names a decision) -- it does NOT
prove any single citation above is CORRECT. Correctness of "why" is the phase record's own judgement.

## Next Phase Readiness

- The exhaustiveness gate exists, passes, and is proven under D-18. Plan 144-07 can now cite
  `firestarter/tests/test_trace_segment_exhaustiveness_v131.py` as the machine-checked evidence for
  TEST-06 when it performs the consolidated eight-requirement flip, and can paste the per-segment
  table above directly into its record.
- `firestarter/src/`, `firestarter/test/` (both fixture headers), `scripts/check_*.py` (FLOOR=6) and
  `tests/fixtures/` (FIXTURE_FLOOR=15) are untouched; the D-04 "no `src/` edit this phase" invariant
  holds after this plan.
- No blockers for the next plan in this phase's wave structure.

## Self-Check: PASSED

- `firestarter/tests/test_trace_segment_exhaustiveness_v131.py` -- FOUND on disk.
- `.planning/phases/144-tests-build-verification/144-04-SUMMARY.md` -- FOUND on disk.
- Commit `9be07ba` (Task 1, firestarter submodule) -- FOUND in `git log --oneline --all`.
- Commit `6cc4795` (Task 2, firestarter submodule) -- FOUND in `git log --oneline --all`.

---
*Phase: 144-tests-build-verification*
*Completed: 2026-08-14*
