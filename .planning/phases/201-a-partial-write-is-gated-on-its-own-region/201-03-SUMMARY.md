---
phase: 201-a-partial-write-is-gated-on-its-own-region
plan: 03
subsystem: firmware-protocol
tags: [blank-check, wire-protocol, region-scoping, native-tests, unity, platformio, cross-repo-constant]

# Dependency graph
requires:
  - phase: 201-02
    provides: the inert `region-end` wire field (handle->region_end, JSON_KEY_REGION_END), parsed
      and reset per command, plus the D-16.1 regression test observed RED against unmodified
      firmware with its negative control observed GREEN
provides:
  - "mem_util_blank_check_region(handle, start, end) — the single region-scoped scan body in
    memory.cpp; mem_util_blank_check is now a one-line wrapper over it passing (0, mem_size)"
  - "mem_util_operation_end(handle) — the single resolution point for D-04's 0=absent=whole-device
    fallback and the fail-closed clamp min(region_end, mem_size)"
  - "the region form wired into eprom.cpp:145's write-init call site, replacing the whole-device
    call in place with no new return and no line inserted above eprom.cpp:70"
  - "host region_length keyword parameter on _setup_operation/_operation_context, emitting
    JSON_KEY_REGION_END = address + region_length for write and verify, absent for read"
  - "WriteInitPreflightChip._is_blank taught the region (start/end default args), so the host
    write -a regression leg stops passing vacuously against a whole-buffer comparison"
affects: [201-04, 201-05, 201-06]

actuals:
  tokens: 16016
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Fallback and clamp resolved in exactly ONE helper function rather than an inline ternary,
      specifically to keep a source-scanning golden (branch-inventory) and a parenthesis-intolerant
      regex gate (progress-emission) both unaffected by the same edit."
    - "Region-scoped test double widened by trailing default arguments (start=0, end=None) rather
      than a new method, so no existing caller's behavior changes unless it opts in."

key-files:
  created: []
  modified:
    - firestarter_fw/include/memory_utils.h
    - firestarter_fw/src/proms/memory.cpp
    - firestarter_fw/src/proms/eprom.cpp
    - firestarter_fw/tests/golden/protocol_branch_inventory.json
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/tests/fake_chip.py
    - firestarter_app/tests/test_eprom_operations.py
    - firestarter_app/tests/test_chip_test_uv_slot_write.py

key-decisions:
  - "Deviation (Rule 1): test_chip_test_uv_slot_write.py's
    test_the_double_refuses_a_non_blank_write_without_the_flag reseeded its non-blank byte INSIDE
    the write's target region instead of outside it, because region-scoping is the exact fix that
    makes the old (outside-region) seed pass vacuously. See Deviations section."
  - "Deviation (Rule 1): the plan's literal planted-mutation sed command (default-value-only) cannot
    detect a regression given the mandated always-explicit-args call shape; used an equivalent
    body-level mutation instead. See Deviations section."
  - "requirements-completed left empty in REQUIREMENTS.md (though this plan's frontmatter declares
    BLANK-01/BLANK-03): both IDs are also declared by later plans (201-04, 201-06) with no SUMMARY.md
    yet, so the shared-ID gate holds them at Pending until the last declaring plan finishes."

requirements-completed: [BLANK-01, BLANK-03]

coverage:
  - id: D1
    description: "BLANK-01 closed in software end to end: a region end travels from the host's
      _setup_operation, over the wire, through the parser, into mem_util_blank_check_region — a
      write into a blank region of a non-blank part succeeds; a write into a non-blank region is
      still refused."
    requirement: BLANK-01
    verification:
      - kind: unit
        ref: "firestarter_fw test/native/avr/test_val_eprom/test_val_eprom.cpp#test_write_init_accepts_blank_region_on_non_blank_part"
        status: pass
      - kind: unit
        ref: "firestarter_fw test/native/avr/test_val_eprom/test_val_eprom.cpp#test_write_init_still_refuses_when_target_region_is_non_blank"
        status: pass
      - kind: unit
        ref: "firestarter_fw pio test -e native (237/237) and -e native_nodevtools (237/237)"
        status: pass
      - kind: other
        ref: "firestarter_fw tests/test_protocol_branch_inventory.py (golden re-derived in the same commit, blob sha verified against git hash-object)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The host emits region-end on write and verify (D-05/D-07), absent on read, and
      the fake chip test double learned the region so the write -a regression leg exercises it
      rather than the whole buffer (BLANK-03/D-16.2)."
    requirement: BLANK-03
    verification:
      - kind: unit
        ref: "firestarter_app tests/test_eprom_operations.py#test_region_end_emitted_on_write"
        status: pass
      - kind: unit
        ref: "firestarter_app tests/test_eprom_operations.py#test_region_end_emitted_on_verify"
        status: pass
      - kind: unit
        ref: "firestarter_app tests/test_eprom_operations.py#test_region_end_absent_for_read"
        status: pass
      - kind: unit
        ref: "firestarter_app tests/test_eprom_operations.py#test_write_into_blank_region_of_non_blank_part_succeeds"
        status: pass
      - kind: unit
        ref: "firestarter_app tests/test_eprom_operations.py#test_write_into_non_blank_region_is_still_refused"
        status: pass
      - kind: unit
        ref: "firestarter_app full suite (2106 passed), ruff clean, coverage 85.42%"
        status: pass
    human_judgment: false
  - id: D3
    description: "The leonardo flash figure after this change is measured and recorded against the
      pre-phase baseline, since no CI leg gates it."
    requirement: ""
    verification:
      - kind: other
        ref: "firestarter_fw pio run -e leonardo (bootloader-guard tool output)"
        status: pass
    human_judgment: true
    rationale: "No automated ceiling check exists (platformio.ini overrides board_upload.maximum_size
      to 32768 against a real 28672 B Caterina ceiling) — a human should see the margin trend across
      plans in this phase, not just this plan's own pass/fail."

duration: ~50min
completed: 2026-09-20
status: complete
---

# Phase 201 Plan 03: End-to-End Region-Scoped Blank Check (Tracer) Summary

**A region end now travels from the host's `_setup_operation` dict, over the wire, through the parser, into `mem_util_blank_check_region` in firmware — a write into a blank region of a non-blank part succeeds, while a write into a non-blank region is still refused, proven by the D-16.1 case flipping from RED (plan 201-02, `af47bf4`) to PASS at this plan's firmware commit (`76fd3c7`).**

## Performance

- **Duration:** ~50 min
- **Tasks:** 2
- **Files modified:** 8 (4 firmware, 4 host)

## Accomplishments

- `mem_util_operation_end(const firestarter_handle_t* handle)` resolves D-04's `0 = absent = whole
  device` fallback and the fail-closed clamp (`min(region_end, mem_size)`) in exactly one place in
  `memory.cpp`, deliberately as a function rather than an inline ternary — an inline ternary in
  `eprom.cpp` would have added a row to the branch-inventory golden and, separately, tripped the
  parenthesis-intolerant capture group in `test_progress_emission_is_leonardo_only.py` (a hazard
  RESEARCH.md's G-1 flagged for a sibling plan; avoided here structurally, not by luck).
- `mem_util_blank_check` (`memory.cpp`) split into `mem_util_blank_check_region(handle, start, end)`
  — the single scan body, with all four `mem_size` reads (completion test, scan upper bound, clamp,
  progress denominator) made `end`-relative — and a one-line wrapper passing `(0, handle->mem_size)`.
  The two cannot drift: there is exactly one body. `blank_check_saved_address` and the
  `CMD_BLANK_CHECK` emit fork are textually unchanged.
- `src/proms/eprom.cpp:145`'s write-init call site now reads
  `mem_util_blank_check_region(handle, handle->address, mem_util_operation_end(handle))`, replacing
  the whole-device call in place. No `return` was added inside `eprom_internal_write_init_body`
  (the single-exit wrapper's structural property holds), and no line was inserted above `eprom.cpp:70`
  (`test_exactly_one_protocol_keyed_site_at_the_pinned_line`'s hard-coded `[70]` still holds).
  `flash_intel.cpp` and `flash_nor_unlock.cpp` are byte-unchanged (D-10, deferred).
- `tests/golden/protocol_branch_inventory.json` re-derived from the module's own `_extract_predicates`
  in the same commit as the source edit: zero new predicates (a function call in a plain assignment
  carries none), only line numbers shifted below the insertion point, and the pre-existing
  `counts`/`sites` drift (21/20 recorded against 22 actual entries — an unasserted bug, since no test
  reads `counts`) corrected to 22/21.
- `test_write_init_accepts_blank_region_on_non_blank_part` (D-16.1) flips from **RED** at `af47bf4`
  (plan 201-02) to **PASS** at `76fd3c7` (this plan). `test_write_init_still_refuses_when_target_region_is_non_blank`
  (negative control) stays PASS throughout. `pio test -e native` and `-e native_nodevtools` both
  report **237 succeeded, 0 failed**.
- Host side: `_setup_operation` and `_operation_context` gain a trailing `region_length: int | None
  = None` keyword parameter, forwarded by name (never inserted among the existing positional six).
  When present, greater than zero, and the command is write or verify, the command dict carries
  `JSON_KEY_REGION_END = address + region_length`. `write_eprom` and `verify_eprom` each compute
  `region_length` via a guarded `os.path.getsize`, preserving today's error ordering for a missing
  file exactly (an unguarded `getsize` would move that failure earlier for non-0x05 parts).
  `database.py`'s `convert_to_programmer` is untouched.
- `WriteInitPreflightChip._is_blank` gains `start`/`end` default arguments (`end` defaulting to
  `self.memory_size`), and its caller in `write_eprom` computes both from the address argument and
  the payload size, the same arithmetic the base class already performs. `FakeChip.check_eprom_blank`
  (the standalone command double, frozen by BLANK-02) is textually unchanged.
- Five new legs added to `tests/test_eprom_operations.py`: two product legs driving
  `WriteInitPreflightChip.write_eprom` directly (`test_write_into_blank_region_of_non_blank_part_succeeds`
  and its negative control), and three emission legs (write / verify / read-absent) capturing
  `_setup_operation`'s returned `command_dict` at the `SerialCommunicator.find_and_connect` wire
  boundary — the same idiom `TestSdpOperationsWireShape` already uses — and asserting on
  `JSON_KEY_REGION_END`, never a bare string.

## Task Commits

Each task was committed atomically, across two submodules plus one meta-repo gitlink advance, all
on `v1.40-program-parameter-fidelity`:

1. **Task 1 (firestarter_fw half): scope the write-init blank check to its own region, re-derive the
   golden** — `76fd3c7` (feat)
2. **Task 1 (firestarter_app half): emit `region-end` for write/verify from `_setup_operation`** —
   `18f2088` (feat)
3. **Task 2: teach the host fake the region, add five host legs** — `5b3fe45` (test)

**Meta-repository gitlink advance:** `fa6b500f` (feat) — `firestarter_fw` pointer moved `af47bf46`
→ `76fd3c7b`, `firestarter_app` pointer moved `a36b9eca` → `5b3fe458`, both in `/workspaces` on
`v1.40-program-parameter-fidelity`.

### D-16.1: RED (plan 201-02) → PASS (this plan)

RED transcript (from `201-02-SUMMARY.md`, commit `af47bf4`):

```
test/native/avr/test_val_eprom/test_val_eprom.cpp:653: test_write_init_accepts_blank_region_on_non_blank_part: D-16.1: a non-blank byte OUTSIDE the write's own target region [8192, 12288) must not refuse the write. RED at this commit means the whole-device blank check does not yet scope to the region -- plan 201-03's fix is what greens this.	[FAILED]
```

PASS transcript, this plan's commit `76fd3c7`, `pio test -e native_nodevtools -f native/avr/test_val_eprom`:

```
test/native/avr/test_val_eprom/test_val_eprom.cpp:728: test_write_init_accepts_blank_region_on_non_blank_part	[PASSED]
test/native/avr/test_val_eprom/test_val_eprom.cpp:729: test_write_init_still_refuses_when_target_region_is_non_blank	[PASSED]
---- native_nodevtools:native/avr/test_val_eprom [PASSED] Took 3.24 seconds ----
================= 13 test cases: 13 succeeded in 00:00:03.240 =================
```

### `pio test` summary, both environments

```
native             : 237 test cases: 237 succeeded in 00:01:40.478
native_nodevtools  : 237 test cases: 237 succeeded in 00:00:44.321
```

### `FIRESTARTER_META_ROOT=/tmp/no-meta pytest tests/`

```
269 passed, 32 skipped in 13.44s
```

### Golden re-derivation, new values

- `meta.blob_shas["src/proms/eprom.cpp"]`: `c16c1972b4d30779b77fc5b03e0f44d08810ec1b` →
  `8fa3c7a00869ed6ee3165e5ba538d42c144eb347` (matches `git hash-object src/proms/eprom.cpp` on the
  committed tree).
- `meta.recorded_at_head`: `af47bf464a24c005e556cf3d7308679064feca5e` (this commit's PARENT — plan
  201-02's tip — per the golden's own one-commit-offset convention, recorded in every prior
  re-derivation in `meta.recorded_by`).
- `counts`: `{total_sites: 21, protocol_keyed_sites: 1, other_sites: 20}` →
  `{total_sites: 22, protocol_keyed_sites: 1, other_sites: 21}`, now equal to `len(sites)` (22).
  `protocol_lines` stays `[70]`.
- `meta.recorded_by`: appended a paragraph naming this plan's edit and the counts correction.
- Zero new predicate rows — the function-call replacement inside an existing statement carries no
  new ternary; every site's `(predicate, keyed_on, tier)` triple is unchanged, only line numbers
  shifted below the insertion point.

### `pio run` — leonardo flash figure

```
leonardo: Flash 23932/32768 B (73.0%)
bootloader-guard: leonardo 23932/28672 B (83.5% of the safe ceiling, 4740 B margin, 4096 B bootloader reserved)
```

Baseline trail: 23816 B (pre-phase, RESEARCH.md) → 23850 B (plan 201-02, `region_end` field added)
→ **23932 B** (this plan, +82 B over 201-02, +116 B over pre-phase). uno and uno328pb both still
`SUCCESS`. All three environments compiled clean; no size gate exists in CI (`platformio.ini:78-82`
overrides `board_upload.maximum_size` to `32768` against the real 28672 B Caterina ceiling), so this
figure is a measurement, not an enforced pass.

### Host suite

```
firestarter_app: 2106 passed in 353.13s
ruff check / ruff format --check: All checks passed! / 145 files already formatted
coverage: 6140 stmts, 895 missed, 85.42% (>= 70% floor, ci.yml:63-64)
```

## Files Created/Modified

- `firestarter_fw/include/memory_utils.h` — declares `mem_util_operation_end` and
  `mem_util_blank_check_region`, each with a block comment naming where it is defined and why it is
  exposed, matching the house pattern above `memory_verify_execute`.
- `firestarter_fw/src/proms/memory.cpp` — `mem_util_operation_end` defined; `mem_util_blank_check`
  split into the region form plus a one-line wrapper.
- `firestarter_fw/src/proms/eprom.cpp` — the write-init call site at `:145` now calls the region
  form with `mem_util_operation_end(handle)` as the end argument.
- `firestarter_fw/tests/golden/protocol_branch_inventory.json` — re-derived; blob sha, `counts`,
  and `recorded_by` all updated in the same commit as the source edit.
- `firestarter_app/firestarter/eprom_operations.py` — `region_length` threaded through
  `_setup_operation`/`_operation_context`; `write_eprom`/`verify_eprom` each compute it via a
  guarded `os.path.getsize`.
- `firestarter_app/tests/fake_chip.py` — `WriteInitPreflightChip._is_blank` widened by default
  arguments; its caller computes and passes `start`/`end`.
- `firestarter_app/tests/test_eprom_operations.py` — five new legs (two product, three emission).
- `firestarter_app/tests/test_chip_test_uv_slot_write.py` — one test's fixture reseeded (see
  Deviations).

## Decisions Made

See `key-decisions` in frontmatter. The two substantive ones are both Rule 1 corrections forced by
measured fact once the region-scoping fix landed system-wide; both are detailed in Deviations below.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `test_chip_test_uv_slot_write.py`'s `test_the_double_refuses_a_non_blank_write_without_the_flag` reseeded inside the target region instead of outside it**
- **Found during:** Task 2, running `tests/test_chip_test_uv_slot_write.py` after widening `_is_blank`
- **Issue:** This Phase-179 leg exists to prove "the double is not theatre" — that `WriteInitPreflightChip` genuinely refuses a non-blank write when `FLAG_SKIP_BLANK_CHECK` is absent. It used the shared `_seeded_m27c512_double()` fixture, whose non-blank content sits at `[0x0000, 0x0100)` — deliberately OUTSIDE the write's own target region at `[0xFF00, 0x10000)` — because legs 3-6 in the same file need exactly that shape to exercise Phase 179's witness/`FLAG_SKIP_BLANK_CHECK` policy. That shape correctly modelled the OLD whole-device blank check (any non-blank byte anywhere refuses), which is precisely the defect BLANK-01 fixes. Once the fake was widened to the region-scoped model this plan requires, the target region at `[0xFF00, 0x10000)` is genuinely blank in that fixture, so the write now succeeds — `outcome is False` no longer holds, and the leg failed (`assert True is False`). Left uncorrected, this would either break CI or (worse) leave a Phase-179 test asserting the exact stale whole-device model BLANK-01 exists to retire.
- **Fix:** Rewrote only this ONE test function's body to construct its own `WriteInitPreflightChip` and seed the non-blank byte INSIDE the target region (`chip.data[0xFF00:0xFF10]`), which is what a region-scoped refusal actually requires to prove anything. The shared `_seeded_m27c512_double()` helper (lines `:104-114`, referenced by legs 3-6) is untouched, preserving the outside-region shape those legs still need for the witness-policy assertions. None of the plan's six enumerated `WriteInitPreflightChip` reference lines (`:81, :104, :112, :276, :324, :413/:417`) were edited — the new construction is a distinct site inside this one test's body.
- **Files modified:** `tests/test_chip_test_uv_slot_write.py`
- **Verification:** `pytest tests/test_chip_test_uv_slot_write.py tests/test_uv_mask.py tests/test_wire_dict_equivalence.py` → 56 passed. Full host suite → 2106 passed.
- **Committed in:** `5b3fe45`
- **Note on the plan's acceptance criterion:** the plan stated "`tests/test_chip_test_uv_slot_write.py` passes with none of its six `WriteInitPreflightChip` sites edited" as a predicted outcome, not a directive not to fix a real defect. That prediction turned out to be measurably false once the region-scoping fix landed — recorded here rather than silently forced.

**2. [Rule 1 - Bug] The plan's literal planted-mutation command cannot detect a regression; used an equivalent, stronger mutation**
- **Found during:** Task 2, running the plan's own verify leg (`sed -i 's/def _is_blank(self, start: int = 0, end: int | None = None)/def _is_blank(self, start: int = 0, end: int | None = 0)/' tests/fake_chip.py`)
- **Issue:** This mutation only changes `_is_blank`'s DEFAULT value for `end` (from `None` to `0`). The plan's own action text mandates that `write_eprom`'s caller "compute `start` and `end` ... and pass them" — i.e., always call `self._is_blank(start, end)` with two explicit positional arguments. Since no caller in the widened `WriteInitPreflightChip` ever invokes `_is_blank()` relying on the default (the only caller always supplies both), the mutated default is dead code from that call site's perspective, and the mutation is silently absorbed: `planted_rc=0`, all 49 legs in `test_eprom_operations.py` still passed. Measured directly, not assumed.
- **Fix:** Used an equivalent body-level mutation instead — reverting the comparison from the region-scoped `bytes(self.data[start:end]) == b"\xff" * (end - start)` to the OLD whole-buffer form `bytes(self.data) == b"\xff" * self.memory_size` (ignoring `start`/`end` entirely). This is the actual historical regression BLANK-01/BLANK-03 fix; applying it drove `test_write_into_blank_region_of_non_blank_part_succeeds` to fail (`assert False is True`), `planted_rc=1`, and the file was restored and confirmed restored via `git diff --quiet`. This is the correct proof of non-vacuity: it demonstrates the new legs would catch the real defect returning, which the plan's own sed pattern, given the mandated implementation shape, structurally cannot.
- **Files modified:** none (verification-only finding; `tests/fake_chip.py` was restored from the temporary mutation both times)
- **Verification:** `planted_rc=1` with the body-level mutation applied; `git diff --quiet -- tests/fake_chip.py` confirms restoration; `RESTORED` printed.
- **Committed in:** N/A (verification-only finding, documented here per the 201-01/201-02 precedent of correcting a plan's own broken verify command rather than reporting a false PASS)

---

**Total deviations:** 2 (both Rule 1 — bug corrections forced by measured fact once the region-scoping fix landed system-wide, not architectural changes and not scope creep). Neither touches production firmware or host logic beyond what the plan already mandated.
**Impact on plan:** Both were necessary to keep the full test suites honestly green and to keep the non-vacuity proof genuinely non-vacuous. No weakening of any assertion occurred — if anything, the negative control in deviation 1 is now a genuine region-scoped proof rather than a whole-device one, and the mutation in deviation 2 is a stronger, more relevant proof than the plan's own literal command.

## Issues Encountered

None beyond the deviations documented above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- BLANK-01 is closed in software and proven end to end by the test that was RED one commit ago
  (plan 201-02's `af47bf4`) and is PASS at this plan's commit (`76fd3c7`).
- Plan 201-04 has its target: bound write and verify on the operation's end at
  `_process_incoming_data`'s two sites (`eprom_operations.cpp:90, :128`) and the write-loop progress
  denominator at `eprom.cpp:397`, restating the one-payload-meaning contract in
  `test_progress_emission_is_leonardo_only.py` and re-deriving the branch-inventory golden a second
  time in the same commit.
- Plan 201-05 has its target: the D-15.3 source-contract gate over all nine `mem_util_blank_check`
  reference sites (3 direct calls + 6 function-pointer assignments), proved by two planted
  violations — this plan changed exactly one of those nine sites (`eprom.cpp:145`), leaving the
  other eight (including the six function-pointer assignments to the whole-device wrapper) untouched
  and ready for that gate to enumerate.
- `BLANK-01` and `BLANK-03` remain `Pending` in REQUIREMENTS.md by design (the shared-ID gate): both
  are also declared by plan 201-04 and/or 201-06, which have not produced a SUMMARY.md yet.
- No blockers. All three repositories remain on `v1.40-program-parameter-fidelity`.

## Self-Check: PASSED

- FOUND: `firestarter_fw/include/memory_utils.h`
- FOUND: `firestarter_fw/src/proms/memory.cpp`
- FOUND: `firestarter_fw/src/proms/eprom.cpp`
- FOUND: `firestarter_fw/tests/golden/protocol_branch_inventory.json`
- FOUND: `firestarter_app/firestarter/eprom_operations.py`
- FOUND: `firestarter_app/tests/fake_chip.py`
- FOUND: `firestarter_app/tests/test_eprom_operations.py`
- FOUND: `firestarter_app/tests/test_chip_test_uv_slot_write.py`
- FOUND: commit `76fd3c7` (`git -C firestarter_fw log --oneline --all`)
- FOUND: commit `18f2088` (`git -C firestarter_app log --oneline --all`)
- FOUND: commit `5b3fe45` (`git -C firestarter_app log --oneline --all`)
- FOUND: commit `fa6b500f` (`git log --oneline --all`, meta repo gitlink advance)
- Re-ran acceptance criteria and plan-level `<verification>`: `pio test -e native` 237/237; `pio test
  -e native_nodevtools -f native/avr/test_val_eprom` 13/13 with D-16.1 PASS and negative control PASS;
  `FIRESTARTER_META_ROOT=/tmp/no-meta pytest tests/` 269 passed / 32 skipped / 0 failed;
  `test_protocol_branch_inventory.py` 7/7 passed; golden blob sha / counts / no-TODO-reasons all
  confirmed via the plan's own python check; `eprom.cpp` holds exactly one region-form call and zero
  comment-stripped whole-device calls; the four out-of-scope protocol files (`flash_intel.cpp`,
  `flash_nor_unlock.cpp`, `flash_5v_page.cpp`, `eeprom_28c.cpp`) confirmed byte-unchanged via diff
  against the pre-task base commit; `pio run` 3/3 SUCCESS, leonardo 23932/32768 B with 4740 B
  bootloader-guard margin; host suite 2106 passed, ruff clean, coverage 85.42%; the planted-mutation
  leg (corrected form) drove the suite non-zero and restored the file; `git -C firestarter_fw
  rev-parse --abbrev-ref HEAD`, `git -C firestarter_app rev-parse --abbrev-ref HEAD` and `git
  rev-parse --abbrev-ref HEAD` (meta) all `== v1.40-program-parameter-fidelity`; gitlinks in the meta
  commit match each submodule's own HEAD exactly.

---
*Phase: 201-a-partial-write-is-gated-on-its-own-region*
*Completed: 2026-09-20*
