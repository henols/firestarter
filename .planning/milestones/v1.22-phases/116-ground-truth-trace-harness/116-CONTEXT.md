# Phase 116: GROUND TRUTH + TRACE HARNESS - Context

**Gathered:** 2026-07-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the **oracle** — a native (host-side, no-hardware) bus-trace harness able to prove
byte-exactly what the protocol `0x0D` SDP command sequence emits, together with the
RED-baseline evidence that today's shipped sequence does not reach silicon.

**In scope (TRACE-01..06):**
- Extend the native recording stub (`test/native/avr/_shared/host_stubs_common.inc`) behind a
  **new opt-in flag** so data bytes and `/CE`//`/OE` edges are recorded in the *same ordered
  stream* as register writes — with every pre-existing native suite byte-exact when the new
  flag is compiled in but not opted into.
- A new `0x0D` SDP trace suite pinning the exact ordered `(LSB, MSB, data, CE-pulse)` stream
  for each of the four `0x0D` pinouts — **RED against today's tree**.
- Four first-class planted-fault negative traces, each independently proven to go RED.
- Replace the call-ordered scripted `mock_get_data` with an **address-keyed** version, retiring
  the fixture that cements the inverted `(0x5555, 0x20)` check as expected behaviour.
- A DB-invariant host test pinning `chip_id_check: false` across all 84 `algorithm == 13` entries.
- A written premise-verification artifact settling whether `write at28c256` aborts at INIT on
  `3.0.0b11`, plus the PROJECT.md correction that finding implies.

**Explicitly NOT in scope — this phase changes ZERO production behaviour.** No edit to
`eeprom_28c.cpp`, `flash_utils.{h,cpp}`, `memory.cpp`, or any `src/` file. The fix is Phase 117.
The harness-before-fix ordering is a non-negotiable milestone invariant: a fix landed before its
oracle exists is unverifiable (the abandoned commit `0052c42` swapped the SDP tables and still
reported "22 tests PASS (zero-diff)").

**Validation ceiling applies from the first commit.** No AT28C part is on the bench. See
`.planning/REQUIREMENTS.md` §"Validation Ceiling" for the exact permitted and forbidden claims.
Nothing this phase produces may be described as evidence about AT28C silicon state.

</domain>

<decisions>
## Implementation Decisions

### RED-baseline mechanics

- **D-01:** The RED `0x0D` SDP trace suite is **parked out of `platformio.ini`'s `test_filter`
  allowlist** with a named `TODO(v1.22 Phase 117)`. `pio test -e native` stays green throughout
  Phase 116, so GATE-03 keeps meaning something. **Phase 117's one-line addition of that suite to
  the allowlist IS the RED→GREEN proof.** Rejected: adding it to the allowlist and accepting a red
  native suite for the rest of the milestone (a real regression during 117 would hide inside
  expected noise); rejected: `TEST_IGNORE_MESSAGE` markers (IGNORED does not demonstrate RED, so it
  adds ceremony without adding evidence).

- **D-02:** The RED evidence is pinned as a **committed fixture in the firmware sub-repo** —
  `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` — carrying the verbatim
  expected-vs-actual divergence. It lives next to the code it describes, survives `.planning/`
  archival, and lets a Phase-117 reviewer diff the recorded actual stream against the fixed one
  without checking out an old tree. (A `.planning/`-only transcript was rejected as too easily
  orphaned from the code.)

- **D-03:** TRACE-01's recording extension gets its **own permanently-GREEN suite**, separate from
  the RED `0x0D` suite, and **enters `test_filter` immediately**. The recorder is a capability with
  no dependency on the fix, so it can be green on day one: it proves ordered capture correctly
  interleaves register writes, data bytes and CE/OE edges, and that flag-off behaviour is
  byte-identical to today. This keeps GATE-03 covering the harness while the `0x0D` suite is parked.

- **D-04:** The four planted-fault negatives are **committed and permanently re-runnable, injected
  in-TU** — never by mutating production source (which this phase may not touch):
  - unlock-table-mutated-to-`0x10` and lock-table-swapped-for-write-prefix become **test-local
    `byte_flip_t` copies** fed through the same emitter and asserted to produce a *different*
    stream. These live in the always-green harness suite (D-03).
  - the `LOG_`-inside-the-timing-window negative needs a **source-scan checker plus a planted
    fixture source file** — the v1.21 SAFE-03 / `FIRESTARTER_DEVTEST_SRC` env-override shape.
  - `protocol != 0x0D` reaching `configure_not_implemented()`/`0xBB` is a **plain positive test**
    (existing `test_not_implemented` pattern).

  Rejected: a one-time local mutation with a recorded transcript (the proof becomes a screenshot;
  nothing stops a later refactor re-hollowing the harness). Rejected: a `tools/` script that
  patches/runs/reverts tracked source (new and risky pattern; leaves a dirty tree on abort).

### Trace fidelity and expected form

- **D-05:** The recorder gets its elision behaviour by **`#include`ing the real
  `firestarter/include/rurp_register_utils.h`** under the new opt-in flag — *not* by replicating
  production's cache-compare. Zero drift by construction: the elision IS production's.

  **Verified during discussion:** `rurp_write_to_register`
  (`firestarter/include/rurp_register_utils.h:24`) returns early when the cached LSB/MSB/CONTROL
  value is unchanged; the current stub
  (`firestarter/test/native/avr/_shared/host_stubs_common.inc:71`) records unconditionally. The SDP
  sequence addresses `0x5555` three times, so a raw call-log asserts register writes the shield
  never sees. Research finding 10 warns explicitly that a test *counting* register writes draws the
  wrong conclusion.

  **Viability confirmed:** that header is a header-with-definitions included only by
  `src/boards/*.cpp`, which `[env:native]`'s `src_filter = +<proms/>` excludes — so there is no
  duplicate-definition conflict. Its `rurp_internal_write_to_register` body is native-safe (the Uno
  `PORTD` block is `#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)`-gated off) and
  calls only `rurp_write_data_buffer` / `rurp_set_control_pin` / `delayMicroseconds`, all already
  stubbed.

  **Two consequences, accepted:**
  1. The recording hooks move **down** to `rurp_write_data_buffer` and `rurp_set_control_pin`, so the
     stream becomes **latch-strobe-shaped** — finer-grained than today's one-entry-per-register-write.
  2. The header's real cache-backed `rurp_read_from_register` replaces the return-0 stub, but
     **only inside new-flag suites**. The existing `HOST_STUBS_RECORD_BUS` suites
     (`test_val_eprom`, `test_val_eeprom28c`, `test_val_nor_unlock`, `test_val_5v_page`,
     `test_val_flash_intel`, `test_val_sram`) must keep today's exact behaviour — this is the
     byte-exactness half of TRACE-01 and is a hard success criterion.

  Rejected: a hand-replica of the cache-compare (the v1.18 WR-01 approach) — simpler blast radius,
  but a silent divergence if production caching ever changes, mitigated only by a comment.

- **D-06:** The expected stream is a **literal tuple array** per case — a static array of
  `{kind, reg-or-pin, value}` entries, compared element-by-element with a
  `TEST_ASSERT_..._MESSAGE` that **names the diverging index**. Matches how
  `test_val_5v_page.cpp` already asserts, keeps everything inside Unity, and makes Phase 117's
  diff a readable change to data rather than to a blob. Rejected: a golden text-trace string
  (needs a rendering layer that itself needs a test; whitespace churn becomes a test failure).
  A failure-time text renderer is permitted but optional — see Claude's Discretion.

- **D-07:** Edge recording is **scoped to what `0x0D` actually touches** — `rurp_write_data_buffer`
  bytes plus the `chip_enable`/`chip_disable` and `chip_input`/`chip_output` transitions the
  `eeprom_28c` + `flash_utils` paths call, enough to pin `(LSB, MSB, data, CE-pulse)` per TRACE-02
  and no more. Rejected: recording every side-effecting `rurp_*` call — future-proofs Phases
  118–121 but widens the surface and makes the flag-off byte-exactness argument harder to make.

### bus_config provenance

- **D-08:** The four pinouts' `bus_config_t` values are **generated from the host's own
  derivation** — a generator imports `firestarter_app`'s real `database.py` /
  `convert_to_programmer` path (the same code that produced the research's 11/14/14/20 `rw`-line
  numbers) and emits a committed header of `bus_config_t` literals. The test's `bus_config` is then
  byte-identical to what the wire would actually carry, and a `pinouts.json` change breaks the
  generator rather than silently staling the golden. Precedent:
  `firestarter/tools/gen_validation_header.py` → `test/native/avr/_shared/validation_matrix.h`.
  Rejected: hand-coded literals with a derivation comment — the harness's ground truth would be a
  transcription, exactly the staleness class Pitfall 9 names, and `pinouts.json` has moved twice in
  four milestones (Phase 94 `page_size`, Phase 98 `rw-pin`).

- **D-09:** Coverage is **one representative per pinout, plus at least one extra
  `DIP32_28C512_EEPROM` size band.** The four pinouts are `DIP28_28C256`, `DIP28_28C64`,
  `DIP24_2816`, `DIP32_28C512_EEPROM` (AT28C256 / AT28C64 / AT28C16 / AT28C010-class). The DIP32
  pinout alone spans 64 KB–512 KB and the A16–A18 staleness Phase 117 must close (FIX-03) differs
  across that range, so a single DIP32 case would leave FIX-03 landing without a band-distinguishing
  trace. Rejected: all 84 rows table-driven (84 goldens to regenerate on any legitimate change; a
  failure report naming 84 rows when one pinout regresses). Rejected: exactly 4 (no band coverage).

- **D-10:** The generated header is **committed with a `DO NOT EDIT` banner and a CI drift gate**
  that regenerates and diffs — following the established `messages.h`/`messages.py` and
  `validation_matrix.h` convention in this repo, so a hand-edit or an un-regenerated `pinouts.json`
  change fails CI. This is convention, not new machinery.

- **D-11:** **The generator runs host-side; the drift gate is host-side.** The generator lives in
  `firestarter_app/tools/` (where `database.py` is), emits the header, and the header is
  **committed under `firestarter/test/native/avr/_shared/`**. The drift gate is a
  `firestarter_app` pytest that regenerates and diffs against the firmware repo's committed copy,
  **skipping cleanly when the firmware submodule is absent** — the exact `FW_ABSENT` skipif shape
  `firestarter_app/tests/test_revision_constants_parity.py` already uses for firmware↔host parity.
  Rejected: a firmware-side generator importing the host package (introduces a firmware→host import
  direction that does not exist today; firmware CI has no reason to install the host package).
  Rejected: a meta-repo source of truth synced down à la `messages.toml` (that source is
  hand-authored; here the source is the host's live code, so the meta repo would hold a *derived*
  artifact — a third copy to keep honest).

### TRACE-04 anti-hollow

- **D-12:** `test_eeprom28c_chip_id` is **migrated and split**, and the old directory retired:
  - The identity-gate assertions that do **not** hinge on the SDP outcome —
    `mismatching_chip_id_errors`, `zero_chip_id_skips_check`,
    `mismatching_chip_id_with_force_warns` — move onto the **address-keyed** mock and into the
    **always-green** suite (D-03), so they finally execute in CI.
  - `test_eeprom28c_matching_chip_id_proceeds` moves into the **RED-parked** suite (D-01). With an
    address-keyed mock returning virgin `0xFF` at `0x5555`, the inverted
    `eeprom28c_wait_for_write(handle, 0x5555, 0x20)` check times out → `MSG_ERR_EEPROM_TIMEOUT` →
    `RESPONSE_CODE_ERROR`, so this test goes RED today. **That failure IS TRACE-06's INIT-abort
    evidence** — TRACE-04 and TRACE-06 share one mechanism.
  - The `s_mock_bytes[2] = 0x20; /* satisfies eeprom28c_wait_for_write(0x5555, 0x20) */` fixture at
    `test_eeprom28c_chip_id.cpp:104` must not survive in that form anywhere (TRACE-04 success
    criterion 4).

  Rejected: fixing the mock in place while the suite stays parked — TRACE-04's wording would be
  satisfied while the assertion never runs, which is precisely the hollow-gate class this milestone
  exists to avoid.

- **D-13:** The **Unity-teardown SIGABRT flake debt stays deferred.** `test_eeprom28c_chip_id` and
  `test_flash_intel_vpp` are parked in `platformio.ini` as a documented pre-existing
  parallel-build filesystem race (Phase 17 WR-01 / Phase 20 verification, carry-forward debt in
  v1.4 `MILESTONES.md` "Known Gaps"). Phase 116 reaches into the former **only** to the extent
  D-12's migration requires; it does not attempt the root cause. Chasing an unbounded debugging
  task inside the one phase the whole milestone's ordering rests on is not an acceptable trade —
  and D-12 means the assertions that matter run anyway, via a new home.

- **D-14:** TRACE-06 produces `116-PREMISE.md` **and Phase 116 applies the PROJECT.md correction
  itself** — a third ⚠ correction block, in this phase, not deferred to the Phase-122 close.
  PROJECT.md already carries two such blocks, so it is the established idiom, and every downstream
  researcher for Phases 117–122 reads that file: leaving a premise this phase disproved in place
  for six phases actively misinforms them.

### Claude's Discretion

- **Suite/directory naming** for the new RED `0x0D` suite and the always-green harness suite. The
  operator set aside the question of whether the name should anticipate Phases 118–119 reusing it;
  choose sensibly (the D-02 fixture path assumes `test_eeprom28c_sdp/`, but that is illustrative,
  not binding).
- **Whether to add a failure-time text renderer** on top of D-06's tuple-array assert, for
  diagnostic messages only. Permitted; the tuple array remains the single source of truth and any
  renderer needs its own test.
- **The exact `{kind, reg-or-pin, value}` entry layout**, the new opt-in flag's name, and the
  recording-buffer capacity (today `HOST_STUBS_MAX_RECORDING 256` — a strobe-shaped stream is
  finer-grained, so check the SDP sequence fits with headroom).
- **TRACE-05's exact home and form** — set aside during discussion. Which test file, and whether it
  asserts the literal count `84` or derives it. Precedents on hand:
  `firestarter_app/tests/test_check_dispatch_invariants.py`, `tests/test_diff_db_gate.py`. Note it
  is a natural companion to D-11's host-side drift-gate pytest.
- **Representative chip selection** within D-09's bands, and how many extra DIP32 bands beyond the
  required one.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone framing and constraints (read first)
- `.planning/REQUIREMENTS.md` — TRACE-01..06 verbatim; the **Locked decisions** table; and
  §"Validation Ceiling", which states the exact permitted and forbidden claims. **Never write or
  accept a plan or success criterion that crosses that line.**
- `.planning/ROADMAP.md` §v1.22 → "Phase Details" → "Phase 116" — the six success criteria this
  phase is verified against, plus the five non-negotiable ordering invariants.
- `.planning/PROJECT.md` §"Current Milestone: v1.22" — both ⚠ correction blocks. **D-14 adds a
  third block here in this phase.**
- `.planning/research/SUMMARY.md` — the 4-stream adjudicated synthesis. Load-bearing for this
  phase: §"Adjudicated Conflicts" CONFLICT 3 (truncation is *structural*, so **no per-part SDP
  magic-address tables**), §"Critical Pitfalls" 1–2 (the false-success trap; the harness cannot see
  what it claims to prove), §"PROVEN vs PREDICTED" (the INIT-abort row is TRACE-06's target), and
  §"Findings That Must Not Be Dropped" items 5, 7 and 10.

### Firmware — the harness surfaces this phase touches
- `firestarter/test/native/avr/_shared/host_stubs_common.inc` — the recording stub. Lines 41–81
  carry the existing `HOST_STUBS_RECORD_BUS` opt-in contract and the explicit list of suites that
  **MUST NOT** define it. `rurp_write_data_buffer` at :98 is the no-op stub research finding 5
  identifies as the reason the harness cannot today distinguish lock from unlock from erase.
- `firestarter/include/rurp_register_utils.h` — `rurp_write_to_register` at :24 (the cache-compare
  elision D-05 depends on), `rurp_internal_write_to_register` at :63, `rurp_read_from_register` at
  :91. Header-with-definitions, included only by `src/boards/*.cpp`.
- `firestarter/platformio.ini` §`[env:native]` — the `test_filter` allowlist (D-01, D-03) and the
  per-suite `-I` include paths; also the KNOWN-FLAKY comment block D-13 defers.
- `firestarter/test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp` — the scripted
  call-ordered mock TRACE-04 retires; **:104 is the exact fixture** that cements the inverted check.
- `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` — the existing `0x0D`
  Tier-1 suite; its `make_handle` and recording-assert shape are the closest in-tree analog.
- `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` — the strongest existing trace
  assertion in the tree (~:200, address-MSBs only). This is the bar D-06 raises.
- `firestarter/test/native/avr/_shared/validation_matrix.h` + `firestarter/tools/` — the
  generated-header + `DO NOT EDIT` banner precedent D-10 follows.

### Firmware — production code this phase READS but must NOT modify
- `firestarter/src/proms/eeprom_28c.cpp` — `EEPROM_SDP_DISABLE[]` at :26-33; `configure_eeprom28c`
  at :34-47 (no `default:` arm today); `eeprom28c_write_init` at :97 (the `flash_execute_command`
  call and the inverted `(0x5555, 0x20)` check); `eeprom28c_write_execute` at :118 (the
  1-byte-in-64 page poll); `PAGE_SIZE 64` hard-coded at :19.
- `firestarter/src/proms/flash_utils.cpp` — `flash_util_byte_flipping` at :20-27,
  `fu_flash_flip_data` at :51-58, and `fu_flash_fast_address` at :60-66 (writes **only** LSB/MSB —
  the bypass at the root of both defects).
- `firestarter/src/proms/memory.cpp` — `memory_set_data` at :224 and
  `mem_util_remap_address_bus` at :258-282 (the remap `fu_flash_fast_address` skips).
- `firestarter/include/firestarter.h` — `bus_config_t` at :75-82 (the struct D-08's generator emits)
  and `firestarter_handle_t.bus_config` at :100.

### Host (`firestarter_app`) — D-11 and TRACE-05
- `firestarter_app/firestarter/database.py` — the `convert_to_programmer` / bus-config derivation
  D-08's generator must import rather than reimplement.
- `firestarter_app/firestarter/data/pinouts.json` — the four `0x0D` pinouts: `DIP28_28C256`,
  `DIP28_28C64`, `DIP24_2816`, `DIP32_28C512_EEPROM`.
- `firestarter_app/tests/test_revision_constants_parity.py` — the `FW_ABSENT` skipif shape D-11's
  drift gate copies.
- `firestarter_app/tests/test_check_dispatch_invariants.py`, `firestarter_app/tests/test_diff_db_gate.py`
  — DB-invariant test precedents for TRACE-05.

### Project conventions
- `CLAUDE.md` (meta), `firestarter/CLAUDE.md` — the native-test environment section, the
  `[env:native]` layout, and the reuse pattern for adding a suite.
- `.planning/notes/dev-test-unknown-chip-fail-fast.md` — not this phase's subject, but the
  reference example of how this project records a load-bearing distinction so a later editor does
  not "fix" the wrong branch. `116-PREMISE.md` (D-14) should read like it.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`HOST_STUBS_RECORD_BUS`** (`host_stubs_common.inc:54-80`) — the opt-in recording pattern
  already exists and already documents its own contract ("flag off = today's no-op behavior is
  preserved byte-exactly"). TRACE-01's new flag is a **second** opt-in layered on the same
  convention, not a redesign. Its own introduction (Phase 71 HARN-01 / D-04) is the in-tree
  precedent for the capability upgrade.
- **`rurp_register_utils.h`** — supplies production's cache-compare and latch-strobe sequencing for
  free under D-05; no replica needed, and it is not linked into `[env:native]` today so there is no
  ODR conflict.
- **`tools/gen_validation_header.py` → `_shared/validation_matrix.h`** — the exact
  generator + committed-header + `DO NOT EDIT` banner shape D-08/D-10 need, already in this repo
  and already covered by `firestarter_app/tests/test_gen_validation_header.py`.
- **`test_val_eeprom28c`'s `make_handle` / `assert_no_vpp_in_recording`** — the handle-construction
  and recording-assert idiom to extend, including the note that `configure_memory()` overwrites
  `firestarter_get_data` so a test must re-assign its mock afterwards (D-10 of Phase 1 Plan 01-01,
  restated at `test_eeprom28c_chip_id.cpp:93-99`).
- **`test_not_implemented`** — the ready-made pattern for D-04's `protocol != 0x0D` → `0xBB` negative.
- **v1.21 SAFE-03 / DISP-01 planted-violation fixtures + `FIRESTARTER_DEVTEST_SRC` env-override** —
  the anti-hollow source-scan shape D-04's `LOG_`-in-window negative copies.
- **`FW_ABSENT` skipif in `test_revision_constants_parity.py`** — D-11's cross-repo gate mechanism.

### Established Patterns
- **`[env:native]` uses a positive `test_filter` allowlist**, not `test_ignore` (a documented PIO
  quirk). A new suite is invisible to `pio test -e native` until its line is added — which is
  exactly what makes D-01's park-then-add-in-117 work as a proof mechanism, and it also means a new
  suite needs both a `test_filter` entry **and** an `-I` build-flag entry when it is time to enable it.
- **Anti-hollow discipline is mandatory in this project**: every gate ships with a planted-violation
  fixture proving the gate actually fails (v1.12 hollow-GATE-03 debt → v1.21 Phase 109 SAFE-03,
  Phase 114 DISP-01). AST/structural scans are preferred over substring greps, because these files'
  own docstrings describe the invariants in prose and false-positive a grep (Phase 109 SAFE-02 and
  Phase 110 lessons, both recorded in STATE.md).
- **Generated artifacts are committed with a `DO NOT EDIT` banner and guarded by a CI drift gate**
  (`messages.h`/`messages.py` from `messages.toml`; `validation_matrix.h`). Never hand-edit.
- **Golden traces need an explicit failure/mismatch case**, not only a matching one — the v1.16
  Phase 89 CR-01 regression was an ERROR→WARNING severity slip that byte-identical golden traces
  missed. D-12's split preserves the mismatch and force-warning cases for exactly this reason.
- **Register-write elision is invisible to a call-counting test** (research finding 10). Assert on
  the ordered stream's content, never on a count.

### Integration Points
- `host_stubs_common.inc` — the single edit point for the recorder; every suite's
  `host_stubs.cpp` `#include`s it, so the flag-off byte-exactness argument covers all 14 suites at
  once.
- `platformio.ini` `[env:native]` — `test_filter` + `-I` entries for the always-green harness suite
  now (D-03), and the parked RED suite's line in Phase 117 (D-01).
- `firestarter/test/native/avr/_shared/` — landing spot for D-08's generated `bus_config` header,
  alongside `validation_matrix.h`.
- `firestarter_app/tools/` + `firestarter_app/tests/` — D-11's generator and drift gate.
- `.planning/PROJECT.md` — D-14's third ⚠ correction block.

### Setup precondition (verify at plan time, do not assume)
Both submodules are currently on **`v1.21-community-chip-validation-command`**
(`git branch --show-current` in each, 2026-07-27). ROADMAP says v1.22 forks off **`beta`**, since
v1.21 is merged there in both sub-repos — reversing the v1.15/v1.21 fork-off-the-previous-version
exception. **Verify with `git` before the first commit**; every prior base exception in this project
began as a confident assumption.

</code_context>

<specifics>
## Specific Ideas

- **The RED→GREEN proof must be a one-line diff.** Phase 117 adding the parked suite to
  `test_filter` is the whole ceremony — deliberately small and unmistakable.
- **The elision finding was verified in the tree during this discussion, not taken from research.**
  `rurp_register_utils.h:24` returns early on an unchanged cached LSB/MSB/CONTROL value; the SDP
  sequence addresses `0x5555` three times. Any expected stream built from a raw call-log would
  assert register writes that never leave the MCU.
- **TRACE-04 and TRACE-06 share one mechanism** (D-12): the address-keyed mock returning virgin
  `0xFF` makes `test_eeprom28c_matching_chip_id_proceeds` fail, and *that failure* is the
  INIT-abort evidence. Plan them together; do not build two separate proofs.
- **The generator must import the host's real derivation, not reimplement it** — it is the same
  code path that produced the research's `rw`-line numbers 11/14/14/20 (DIP pins 21/27/27/30) versus
  22 for `DIP32_SST39SF040`. A reimplementation would be a second thing that can be wrong.
- **`116-PREMISE.md` should read like `.planning/notes/dev-test-unknown-chip-fail-fast.md`** — state
  the finding, the evidence, and *why the distinction is load-bearing*, so a later editor does not
  undo it.

</specifics>

<deferred>
## Deferred Ideas

- **Unity-teardown SIGABRT root cause** (D-13) — re-enabling `test_eeprom28c_chip_id` and
  `test_flash_intel_vpp` in `test_filter`. Pre-existing debt since Phase 17 WR-01 / Phase 20;
  documented in `platformio.ini` and v1.4 `MILESTONES.md` "Known Gaps". Not this phase.
- **Recording every side-effecting `rurp_*` call** (rejected half of D-07) — would future-proof
  Phases 118–121's trace needs. Revisit if 118/119 find the scoped recorder insufficient.
- **All-84-chips table-driven trace coverage** (rejected half of D-09) — revisit only if a
  per-chip defect is ever suspected within a pinout.
- **`PAGE_SIZE 64` hard-coded at `eeprom_28c.cpp:19`** while AT28C010's page is 128 B and
  AT28C040's is 256 B (18 chips affected — same class as the v1.17 W29C040 bug). Named explicitly
  in research finding 9 as a real, adjacent, **explicit deferral, not silence**. Not a v1.22
  requirement.
- **`DIP24_2816` has no `static-high-pins` key** (`static_high_mask == 0`, so VCC/bus line 13 is
  not force-driven for 19 chips, unlike `DIP24_2716`/`DIP24_2732`). Tracked as **SDP-F8** in
  REQUIREMENTS.md §Future Requirements; the Phase-117 remap fix does **not** address it. The
  Phase-116 trace for that pinout will make it visible in the recorded stream — record what is
  observed, do not act on it.
- **Datasheet verification of SDP magic addresses for AT28C040 / AT28C16 / AT28C04** — SDP-F7,
  recorded UNVERIFIED per size band rather than assumed. Low risk given truncation is structural.

### Reviewed Todos (not folded)
All five matches from `todo.match-phase 116` scored 0.6 on generic keyword overlap only; none
touches tracing, `0x0D`, or the native harness. Reviewed and left in the backlog:
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md` (firmware) — VPP
  checks on reads; `0x0D` is VPP-free, unrelated to the harness.
- `avrdude-mcu-detection-fallback.md` (low) — flashing/recovery, not tracing.
- `cobs-decoder-framelevel-deadline-wr01.md` (medium) — v1.10 transport follow-up.
- `decode-infoic-flags-bits-14-15-protect-metadata.md` — DB-build-time protection metadata; note
  REQUIREMENTS.md §Out of Scope already rejects a generic `locked` DB boolean for v1.22.
- (5th, same class.)

</deferred>

---

*Phase: 116-GROUND TRUTH + TRACE HARNESS*
*Context gathered: 2026-07-27*
