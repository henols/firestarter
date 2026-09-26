# Phase 117: FIX — remap-aware `0x0D` emitter + honest completion signal - Context

**Gathered:** 2026-07-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the SDP-disable sequence firmware already ships **actually reach silicon**, and replace its
inverted success check with one that is not anti-correlated with success — proven by flipping
Phase 116's parked RED suite to GREEN, with zero change to the shared code the bench-proven
`0x05`/`0x06`/`0x07` families depend on.

**In scope (FIX-01..06):**
- A `0x0D`-local, remap-aware command emitter built on `handle->firestarter_set_data`, replacing
  `flash_execute_command(EEPROM_SDP_DISABLE)` (FIX-01). Closes the A16–A18 upper-address staleness
  gap for the 18 chips ≥64 KB as a **by-product** of routing through the full remap, not as a
  separate change (FIX-03).
- Deletion of `eeprom28c_wait_for_write(handle, 0x5555, 0x20)` from the write-init path, replaced
  by a `t_WC` wait plus a bounded DQ6 toggle-bit poll (FIX-02).
- `flash_utils.{h,cpp}`, `flash_5v_page.cpp`, `flash_nor_unlock.cpp` **byte-untouched**; the
  `0x05`/`0x06`/`0x07`/`0x10`/SRAM golden traces **byte-identical** (FIX-04).
- Terminal-byte constant guards proving SDP-disable (`…0x20`) and `FLASH_ERASE` (`…0x10`) are not
  the same object — the one-nibble chip-erase hazard (FIX-05).
- Correction of `eeprom28c_write_execute`'s per-page polling so a partial write cannot report
  success (FIX-06).
- The surgical edits to `test_eeprom28c_sdp` required to make the RED→GREEN flip honest (see D-01,
  D-02, D-03 — this was **not** anticipated by Phase 116's D-01 and is load-bearing).

**Explicitly NOT in scope:**
- Per-chip page size. `PAGE_SIZE 64` stays as a documented conservative floor (D-13). The
  end-to-end `infoic.xml` → DB → wire → firmware `page_size` decode is a **new phase**, decided
  during this discussion and specified in `<deferred>` — **not yet inserted into ROADMAP.md**.
- Observability (report lines, `FLAG_SKIP_SDP_UNLOCK`, `AT28C_TBLC_MAX_US`, `micros()` timing) —
  Phase 118 (OBS-01..05).
- SDP-**enable**, `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK`, `is_memory_cmd()`, `configure_eeprom28c`'s
  `default:` → `MSG_ERR_NOT_SUPPORTED` arm — Phase 119 (LOCK-01..06).
- Any host/CLI/wire surface — Phase 120 (HOST-01..06). The firmware-before-host ordering invariant
  is non-negotiable.
- Widening the trace recorder to a third strobe kind (data-bus direction) — a named Phase-118 hook
  (D-12).

**Validation ceiling applies from the first commit.** No AT28C part is on the bench. See
`.planning/REQUIREMENTS.md` §"Validation Ceiling" for the exact permitted and forbidden claims.
Nothing this phase produces may be described as evidence about AT28C silicon state — every claim's
subject is the code, never the chip.

</domain>

<decisions>
## Implementation Decisions

### RED→GREEN mechanics — Phase 116's D-01 does NOT hold as written

Phase 116's D-01 promised *"Phase 117's one-line addition of that suite to the allowlist IS the
RED→GREEN proof."* **That is not achievable.** Two structural conflicts were found in
`test_eeprom28c_sdp.cpp` during this discussion, both verified by reading the suite:

1. `drive_write_init` (:169-176) reassigns `h->firestarter_set_data = mock_set_data_keyed`, a
   **no-op**. FIX-01 routes the emitter through exactly that pointer, so post-fix the recorded
   stream for cases 1-5 would be **empty** — the suite stays RED for a reason unrelated to the fix.
2. Cases 1-5 each assert `TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code)` — TRACE-06's
   INIT-abort evidence. FIX-02 deliberately removes that abort, so **five assertions flip RED**
   post-fix.

Cases 4-7 are otherwise genuinely self-repairing once conflict 1 is resolved.

- **D-01:** **Un-mock `set_data` in the suite.** Keep only the `get_data` mock — that is the one
  that collapses `eeprom28c_wait_for_write`'s 2000-iteration poll to zero strobes and makes
  full-stream equality possible at all. Drop `h->firestarter_set_data = mock_set_data_keyed` from
  `drive_write_init`, `drive_write_init_after_real_read`, and cases 6-7. This makes the two halves
  of the suite consistent: its own `drive_reference_emitter` already drives the real
  `memory_set_data`. Rejected: having the emitter call `memory_set_data` directly to leave the
  suite untouched — that is production code shaped by a test mock, it contradicts FIX-01's stated
  "built on `handle->firestarter_set_data`", and it would leave the emitter unmockable for Phases
  118/119, which both need to drive it.

- **D-02:** **Flip the five response-code assertions AND add one permanent severity-preservation
  regression case.** The five become "must not be ERROR" post-fix. The new case proves a future
  unconditional `response_code` overwrite fails — the exact fork the v1.16 Phase-89 CR-01
  regression slipped through (`.planning` memory
  `reference_golden_trace_misses_severity_fork.md`). The frozen historical record of the
  INIT-abort stays where it already is and needs no new home: `116-PREMISE.md` and
  `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md`, both committed with verbatim
  captured output. Rejected: an executable frozen replica of the old shipped emitter + inverted
  check — strongest evidence retention, but it is a second copy of deleted production code that
  can rot silently.

- **D-03:** **Two-commit discipline, capture the middle.** Commit 1 = the `test_filter` line plus
  the D-01/D-02 suite edits **only**, against the still-unfixed production tree → run the suite,
  capture the verbatim RED output, append it to `RED-BASELINE.md` as the post-edit baseline.
  Commit 2 = the production fix → same command, GREEN. The captured intermediate is the anti-hollow
  proof; a reviewer sees both states from the committed record. Rejected: a single commit citing
  the existing baseline — that captured "before" predates the suite edits, so it cannot prove the
  *edited* suite was ever RED.

### FIX-02 — the honest completion signal

- **D-04:** **`t_WC` wait + a bounded DQ6 toggle-bit poll**, the poll issued through
  `handle->firestarter_get_data`. Rejected: a bare `t_WC` delay with no poll at all; rejected:
  deleting the wait entirely (drops the `t_WC` guarantee, so the first page write can land inside
  the SDP-disable internal write cycle).

- **D-05:** **The poll NEVER writes `handle->response_code`** — advisory only. A stuck internal
  cycle stays silent here and surfaces as the first page write's DQ7-poll failure (FIX-06): one
  failure path for one fault, and clobbering severity becomes structurally impossible rather than
  merely avoided. D-02's new regression case then proves that by construction. Rejected:
  escalate-only-if-currently-OK (severity-monotonic, but a second error path for the same fault);
  rejected: unconditional ERROR (this **is** today's defect — RED-BASELINE case 7).

- **D-06 (Claude's Discretion, delegated by the operator):** the exact poll shape — unconditional
  `delay(t_WC)` then poll, versus the poll bounded *by* `t_WC` as a deadline. Decide against the
  datasheet wording. **Hard constraint either way:** the completion path must emit **zero bus
  traffic outside `handle->firestarter_get_data`**. A `fu_flash_data_poll()`-style direct-`rurp_*`
  poll would add strobes and break cases 1-5's full-stream equality. A named constant for the
  timing bound is expected (Phase 118's OBS-03 will cite `AT28C_TBLC_MAX_US = 100` at every
  timing-window call site; a `t_WC` constant here is its sibling, not a duplicate).

### FIX-06 — partial writes cannot report success

The actual defect is a **conflation**, not merely a sampling rate: today
`eeprom28c_wait_for_write(address, data)` at `eeprom_28c.cpp:122` is asked to answer both "is the
internal cycle done" and "did the data land", and can answer neither honestly — its equality
compare passes spuriously whenever the old byte already equalled the new one (blank `0xFF`
regions, unchanged bytes), which is exactly gh#11's shape.

- **D-07:** **Separate the two jobs.** A DQ7-**complement** poll answers completion (the canonical
  AT28C protocol: DQ7 reads the complement of the last byte written while the cycle is in
  progress); a **read-back of every byte just written** answers whether the data landed. Rejected:
  DQ7 poll only (relies on the host's verify pass; a rejected page still reports firmware-side
  success); rejected: read-back only (leaves an equality compare doing completion-detection duty —
  the conflation itself).

- **D-08:** **The read-back is always on, with no opt-out.** Firmware owns the truth about whether
  its own page write landed; reporting success it cannot substantiate is the defect. An opt-out
  would need a `FLAG_*` value landing in lockstep across `firestarter.h` ↔ `constants.py`, which
  is explicitly Phase 120's HOST-03 scope, and firmware-before-host forbids emitting it early.
  Redundancy with the host's own verify pass is **accepted**: the host's pass proves the image
  landed; this one proves *this page's write cycle* landed, and only the second can attribute a
  failure to a page. Rejected: overloading `FLAG_SKIP_BLANK_CHECK` as the opt-out (it already
  carries two meanings — see `.planning` memory `reference_write_b_skips_erase.md` — a third makes
  it actively misleading).

- **D-09:** **The old-versus-new contrast is executable, side by side in one test.** A test-local
  replica of the old last-byte-equality poll asserted to **PASS** the planted partial write, beside
  the real fixed path asserted to **FAIL** it. Both halves run in CI forever, so SC6's
  "would have passed" claim cannot decay into prose in a markdown file. Planted scenario shape:
  the mock accepts the page's **last** byte but leaves an **earlier** byte at its old value.
  Rejected: asserting only that the fixed path fails, citing the record for the rest.

### FIX-01/FIX-05 — emitter construction and the table guards

- **D-10:** **Keep the `0x0D`-local table; cross-guard both copies.** The emitter drives
  `EEPROM_SDP_DISABLE` (`eeprom_28c.cpp:24`), keeping FIX-01's "`0x0D`-local" framing literal and
  leaving the FIX-04-frozen `flash_utils.h` untouched. Note the duplication is real and
  pre-existing: `FLASH_DISABLE_WRITE_PROTECTION` (`flash_utils.h:53`) is byte-identical, and it is
  the table Phase 116's reference emitter and always-green harness drive. Rejected: deleting the
  local copy and driving the shared table — one table, but it makes `0x0D` depend on the frozen
  shared header and cuts against Phase 119's LOCK-05, which deliberately *preserves* a duplicate
  table rather than deduping.

- **D-11:** **FIX-05's guard does double duty**, as a native test asserting all of:
  `EEPROM_SDP_DISABLE`'s terminal byte is `0x20`; `FLASH_ERASE`'s terminal byte is `0x10`; they are
  distinct objects (the one-nibble chip-erase hazard); **and** `EEPROM_SDP_DISABLE` is byte-identical
  to `FLASH_DISABLE_WRITE_PROTECTION`, so D-10's duplication can never silently diverge from the
  table the Phase-116 harness compares against.

- **D-12:** **Pick up the data-direction hook, but do not widen the recorder.** Add one explicit
  `rurp_set_data_output()` in the `0x0D` emitter. Verified during discussion: `memory_set_data`
  (`memory.cpp:228`) never sets bus direction; `memory_get_data` sets **input** (`memory.cpp:186`);
  direction is otherwise restored only as a *side effect* of a non-elided register write
  (`rurp_register_utils.h:78`) — and `eeprom28c_check_chip_id` leaves the bus in INPUT immediately
  upstream of the sequence. The explicit call makes the guarantee explicit instead of incidental
  and restores parity with what the shipped `fu_flash_flip_data` did, so it is **not** a behavior
  regression. It is invisible to the existing goldens because D-07 of Phase 116 scoped recording to
  `rurp_write_data_buffer` + `rurp_set_control_pin`, so **no `SDP_FIXED_*` regeneration is needed**.
  Recording the direction calls as a third strobe kind stays RED-BASELINE's named **Phase-118
  hook** — Phase 116 declined it partly because the extra stub guards were never verified to
  compile, and taking it here would force regeneration of `_shared/sdp_expected.h` plus
  `test_sdp_harness`'s reference-emitter guards.

### Page size — deliberately NOT a band table

- **D-13:** **`PAGE_SIZE 64` stays, as a documented conservative floor.** The operator's initial
  decision was to fold per-chip page size into this phase; the pinned `infoic.xml` data gathered
  during this discussion showed that a `mem_size`-derived band table would be **wrong**:
  `AT28MC010` (128 KB) carries `page_size = 0x0040` (64) while `AT28C010` (128 KB) carries
  `0x0080` (128) — same density, different page size. 64 is the **conservative** direction: a
  smaller flush granularity issues two legal write cycles into one physical page, never an
  overrun. It is also self-checking once D-07's read-back lands, which verifies whatever
  granularity is used. Record the reasoning in the source so a later editor reads this as
  deliberate, not overlooked. The real per-chip value is delivered by the new phase in
  `<deferred>`.

### Claude's Discretion

- **The poll shape left open by D-06** (delay-then-poll vs. `t_WC`-as-deadline) and the poll's read address.
  Constraint: it must read through `handle->firestarter_get_data`. Note that a read through
  `memory_get_data` folds `READ_FLAG` into `DIP32_28C512_EEPROM`'s CONTROL bit `0x10` — the same
  stale-state mechanism RED-BASELINE case 5 exploits — so the following `set_data` must be relied
  on to recompute CONTROL (it does, via `mem_util_set_address`).
- **Whether to rename the five case functions.** They currently read
  `test_caseN_..._shipped_stream_diverges_from_fixed`, which post-fix asserts the opposite of its
  own name. Names that assert the opposite of what they test are how oracles rot — but the smaller
  diff keeps `RED-BASELINE.md`'s cross-references literal. Either is acceptable; if renamed, update
  the suite header comment and `RED-BASELINE.md`'s "What Phase 117 must do" section in the same
  commit.
- **The emitter's exact signature and name**, and whether it takes the table + length or a
  `sizeof`-style macro mirroring `flash_execute_command`. It must be shaped so Phases 118 (skip
  flag, report lines around it) and 119 (standalone `CMD_SDP_LOCK`/`UNLOCK` driving it with no
  payload) can reuse it without a second refactor.
- **Where FIX-05's terminal-byte guard lives** — the always-green `test_sdp_harness` (already in
  `test_filter`, so it is protected independently of the RED→GREEN flip) or the newly-enabled
  `test_eeprom28c_sdp`. The former is the safer home.
- **Where FIX-06's partial-write test lives.** `test_val_eeprom28c` is already in `test_filter` and
  is the `0x0D` suite; **verified during discussion that it only asserts VPP-free configure (3
  cases, none drives `write_init`/`write_execute`)**, so adding write-path cases there breaks no
  existing golden.
- **The planted mock's exact shape** for D-09, and whether the read-back's mismatch path reports
  the failing address (today's poll bare-`return`s mid-buffer via `MSG_ERR_EEPROM_TIMEOUT` with the
  address but no per-byte attribution).
- **Whether the read-back covers only bytes in the current chunk or the whole physical page**
  including bytes written by a prior chunk.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone framing and constraints (read first)
- `.planning/REQUIREMENTS.md` — FIX-01..06 verbatim; the **Locked decisions** table; and
  §"Validation Ceiling", which states the exact permitted and forbidden claims. **Never write or
  accept a plan or success criterion that crosses that line.**
- `.planning/ROADMAP.md` §v1.22 → "Phase Details" → "Phase 117" — the six success criteria this
  phase is verified against, plus the five non-negotiable ordering invariants (harness-before-fix,
  fix-before-observe, observe-before-lock, firmware-before-host,
  `dev-test`-fix-before-closeout).
- `.planning/PROJECT.md` §"Current Milestone: v1.22" — all three ⚠ correction blocks, including
  Phase 116's CORRECTION 4 (**66 of 84**, not "all 84").
- `.planning/research/SUMMARY.md` — the 4-stream adjudicated synthesis. Load-bearing here:
  §"Adjudicated Conflicts" CONFLICT 3 (truncation is *structural* → **no per-part SDP magic-address
  tables**), §"Critical Pitfalls" 1–2 (the false-success trap), and §"Findings That Must Not Be
  Dropped" items 5, 7, 10.

### Phase 116's output — this phase's oracle (read all four)
- `.planning/phases/116-ground-truth-trace-harness/116-CONTEXT.md` — D-01 through D-14. **D-01's
  "one-line diff" promise does not hold; see D-01/D-02/D-03 above.**
- `.planning/phases/116-ground-truth-trace-harness/116-PREMISE.md` — TRACE-06's INIT-abort finding
  and CORRECTION 4's per-pinout inhibit table. The frozen record D-02 relies on.
- `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` — the seven cases, their
  verbatim RED output, the first-divergence table, and §"Declined widening, recorded as an open
  hook" (D-12's subject). D-03 appends to this file.
- `.planning/phases/116-ground-truth-trace-harness/116-VERIFICATION.md` — what was actually proven
  (6/6) versus assumed.

### Firmware — the code this phase changes
- `firestarter/src/proms/eeprom_28c.cpp` — `EEPROM_SDP_DISABLE[]` at :26-33; `PAGE_SIZE 64` at :19
  (D-13); `eeprom28c_write_init` at :97 (the `flash_execute_command` call at :109 and the inverted
  check at :111); `eeprom28c_write_execute` at :119 (the page poll at :125-131);
  `eeprom28c_wait_for_write` at :135 (the unconditional `RESPONSE_CODE_ERROR` at :153 that destroys
  severity).
- `firestarter/src/proms/memory.cpp` — `memory_set_data` at :224 (FIX-01's target; note it does
  **not** set bus direction), `memory_get_data`'s `rurp_set_data_input()` at :183,
  `mem_util_remap_address_bus` at :258-282 (the remap `fu_flash_fast_address` skips).
- `firestarter/include/rurp_register_utils.h` — `rurp_write_to_register` at :24 (cache-compare
  elision), and `rurp_set_data_output()` at :78 (D-12's incidental-restoration mechanism).
- `firestarter/platformio.ini` §`[env:native]` — the `test_filter` allowlist and its PARKED comment
  block at :86-97 (D-03's commit 1 edits both), plus the per-suite `-I` entries.

### Firmware — code this phase READS but must NOT modify (FIX-04)
- `firestarter/src/proms/flash_utils.cpp` — `flash_util_byte_flipping` at :20-27,
  `fu_flash_flip_data` at :52-59 (note its `rurp_set_data_output()` at :53 — D-12's parity
  argument), `fu_flash_fast_address` at :61-66 (writes **only** LSB/MSB; never `CONTROL_REGISTER`
  — the bypass at the root of both defects).
- `firestarter/include/flash_utils.h` — `FLASH_ERASE[]` at :34-41 (terminal `0x10`),
  `FLASH_DISABLE_WRITE_PROTECTION[]` at :53-60 (terminal `0x20`),
  `FLASH_ENABLE_WRITE_PROTECTION[]` at :48-52 (Phase 119's LOCK-05 preserves this). **Frozen.**
- `firestarter/src/proms/flash_5v_page.cpp` — **frozen**, but `flash_5v_page_page_size(mem_size)`
  at :27 is the in-tree precedent a firmware-local page-size helper would have copied (D-13
  rejects it for `0x0D`; the new phase supersedes it).

### Firmware — the test surfaces
- `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` — the parked RED suite.
  `drive_reference_emitter` at :155, `drive_write_init` at :169 and
  `drive_write_init_after_real_read` at :191 (D-01's edit points), cases 1-3 at :~211-250 (D-02's
  response-code asserts), cases 4-5 (self-repairing), cases 6-7 at :~371-415.
- `firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp` — the always-green harness
  suite; its own `drive_reference_emitter` at :121 and the five reference-emitter guard cases.
  Candidate home for FIX-05's guard.
- `firestarter/test/native/avr/_shared/sdp_expected.h` — the `SDP_FIXED_*` arrays and
  `sdp_assert_stream_equals`. **D-12 is scoped so these need no regeneration.**
- `firestarter/test/native/avr/_shared/sdp_bus_config.h` — the generated `DO NOT EDIT`
  `bus_config_t` literals (Phase 116 D-08/D-10/D-11) and its host-side drift gate.
- `firestarter/test/native/avr/_shared/host_stubs_common.inc` — the recorder; the
  `HOST_STUBS_RECORD_BUS` / `HOST_STUBS_REAL_REGISTER_UTILS` opt-in contract and the list of suites
  that MUST NOT define the flags.
- `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` — the `0x0D` Tier-1
  suite. **Verified: 3 cases, VPP-free configure only, no write-path drive.** Candidate home for
  FIX-06's test.

### Host (`firestarter_app`) — read-only for this phase; the new phase's subject
- `firestarter_app/tools/build_db.py` — `MINIPRO_XML_URL` at :17-20 (pinned commit `a8efaedc`),
  `PROTOCOL_MAP` at :48-67 (a **pass-through** of the XML's `protocol_id`), `_PAGE_SIZE_BY_PART` at
  :146-160 (the 2-entry curated map and its `[CITED:]`-only discipline), the
  `<database type='INFOIC2PLUS'>` scoping at :450 and `proto_id` read at :478, the page_size
  emission at :753-765, and the `DIP24_2816` named rule arm at :560-580.
- `firestarter_app/firestarter/constants.py` — `JSON_KEY_PAGE_SIZE = "page-size"` at :111 with its
  **currently-false** "Firmware sync: json_parser.c (key_page_size)" comment at :107.
- `firestarter_app/doc/infoic-field-dictionary.md` §`page_size` at :241-245 — defines `0` / `1` as
  "not applicable to the device type" (the sentinel policy in `<deferred>`).

### Project conventions
- `firestarter/CLAUDE.md` — the `[env:native]` layout, the dispatch order source-of-truth, and the
  reuse pattern for adding a suite.
- `CLAUDE.md` (meta) — the constants/flag-bit duplication rule between `constants.py` and
  `firestarter.h` (relevant to why D-08 refuses a new flag here).

</canonical_refs>

<code_context>
## Existing Code Insights

### Verified facts established during this discussion (do not re-derive)
- **`memory_set_data` never sets bus direction.** `memory.cpp:228`. `memory_get_data` sets
  **input** at :183. Direction is restored only as a side effect of a non-elided register write
  (`rurp_register_utils.h:78`). `eeprom28c_check_chip_id`'s reads sit immediately upstream of the
  SDP sequence, so the sequence's first write relies on its address differing from the cached one.
  It does today — but incidentally. D-12 makes it explicit.
- **`test_val_eeprom28c` has 3 cases, all VPP-free-configure assertions**, none driving
  `write_init`/`write_execute`. No `0x0D` write-path golden exists there to break.
- **`FLASH_DISABLE_WRITE_PROTECTION` and `EEPROM_SDP_DISABLE` are byte-identical** —
  `flash_utils.h:53-60` vs `eeprom_28c.cpp:26-33`. The Phase 116 harness drives the former; the
  production path drives the latter. D-10/D-11 pin them together rather than deduping.
- **`page-size` does not exist end to end.** `JSON_KEY_PAGE_SIZE` exists in `constants.py` with a
  "Firmware sync" comment, but firmware has **no** `page_size` in `json_parser.c` or
  `firestarter.h`, and `eprom_operations.py` never emits it. Only `flash_5v_page.cpp:27` has a
  local `mem_size` heuristic. PROJECT.md's "Established fact" is confirmed; the `constants.py`
  comment is false. Phase 94 landed the DB-side map plus the constant name and nothing else.
- **`infoic.xml` page_size values** (pinned commit `a8efaedc`, `<database type='INFOIC2PLUS'>`,
  DIP-only, `protocol_id == 0x0D`): **14 rows**, `0x0040`=64 (×3: AT28MC010, WE128K8, WE256K8) and
  `0x0080`=128 (×11: AT28C010, AT28C040, AT28LV010, AT28MC020, AT28MC040, 28C010…). **No `0x0001`
  sentinel among them.** The DB has **84** `algorithm == 13` entries, so ~70 acquire `0x0D` other
  than from a `protocol_id == 0x0D` row — and *their* source rows commonly carry the `0x0001`
  sentinel. See `<deferred>`.
- **`W29C040` = `0x0100` (256) and `W29C020` = `0x0080` (128) in the XML — identical to the
  curated datasheet-cited values.** The "XML wins" precedence rule is therefore an empirical no-op
  for the bench-proven `0x05` family. This retires a concern raised during discussion.

### Reusable Assets
- **`handle->firestarter_set_data`** — already `memory_set_data` after `configure_memory`, already
  remap-aware, already the function `eeprom28c_write_execute` uses. FIX-01 is a change at an
  existing call site, not new machinery.
- **`flash_5v_page.cpp`'s page-write + DQ7 shape** — the in-tree precedent for D-07's
  poll/read-back split (`is_page_start` / `reached_page_end` at :91/:99). Frozen, so copy the
  shape, do not refactor into shared code.
- **The Phase 116 harness end to end** — `sdp_assert_stream_equals`, `sdp_snapshot`,
  `clear_strobes`/`strobe_count`/`strobe_overflowed`, `reset_register_cache`, and the address-keyed
  `mock_get_data_keyed`. Phase 117 consumes all of it; it builds no new trace machinery.
- **v1.21 SAFE-03 / DISP-01 planted-violation fixtures** — the anti-hollow shape D-09's
  side-by-side contrast follows.

### Established Patterns
- **`[env:native]` uses a positive `test_filter` allowlist** — a suite is invisible to
  `pio test -e native` until its line is added, **and** it needs an `-I` entry (already present for
  `test_eeprom28c_sdp`). This is what makes D-03's park-then-enable work as a proof mechanism.
- **Assert on the ordered stream's content, never on a count** — register-write elision is
  invisible to a call-counting test (Phase 116 research finding 10).
- **Golden traces need an explicit failure/mismatch case, not only a matching one** — the v1.16
  Phase-89 CR-01 severity slip. D-02's new case is this rule applied to `response_code`.
- **Anti-hollow discipline is mandatory**: every gate ships a planted-violation fixture proving the
  gate actually fails. AST/structural scans over substring greps, because these files' own
  docstrings describe the invariants in prose.
- **Executors prematurely mark multi-plan requirements Complete** — happened 4× in Phase 116
  (`.planning` memory `reference_executors_prematurely_mark_requirements_complete.md`). Name the
  allowed FIX-NN IDs in each dispatch prompt and check `REQUIREMENTS.md` after every plan.

### Integration Points
- `eeprom_28c.cpp` — the sole production file this phase edits. Every FIX-01..06 change lands here.
- `platformio.ini` `[env:native]` `test_filter` — one line, in D-03's commit 1.
- `test_eeprom28c_sdp/` — D-01/D-02 edits plus D-03's `RED-BASELINE.md` append.
- `test_sdp_harness/` or `test_val_eeprom28c/` — FIX-05's guard and FIX-06's test (discretion).

### Setup precondition (verify at plan time, do not assume)
`firestarter` is on `v1.22-at28c-software-data-protection-lifecycle` (verified
`git branch --show-current`, 2026-07-28). Confirm `firestarter_app` the same way before any
sub-repo write. Phase 117's production changes are **firmware-only** — no `firestarter_app` file
should change in this phase.

</code_context>

<specifics>
## Specific Ideas

- **Phase 116's D-01 was optimistic and this phase must say so out loud.** The RED→GREEN flip is
  four edits, not one line: `test_filter`, the `set_data` un-mock, the five response-code
  assertions, and one new regression case. Silently editing the oracle to make the fix pass is the
  precise failure mode this milestone's ordering invariant exists to prevent — hence D-03's
  captured intermediate state.
- **The completion signal's honesty is about what it does NOT claim.** The old check was
  anti-correlated with success because it read back a byte the datasheets say is never written. The
  replacement's virtue is that a non-responding part produces "settled DQ6" immediately and the
  code draws no conclusion from it (D-05) — the conclusion is deferred to the page write's own
  poll, which has a real written byte to compare against.
- **FIX-06 is a conflation bug, not a sampling-rate bug.** "1 byte in 64" undersells it: polling
  the page's last byte is the *canonical* AT28C completion protocol. The defect is that the same
  read is also serving as the data-landed proof, via an equality compare that passes whenever
  old == new. Frame it that way in the plan or the fix will be aimed at the wrong thing.
- **`page_size` turned out to be present in `infoic.xml` after all** — the operator's instinct was
  right, and the field dictionary marks it CONFIRMED. What is missing is the decode, the wire, and
  the firmware parse. The 14-vs-84 provenance gap is what turns this from a one-line change into
  its own phase.
- **CORRECTION 4 (66 of 84) is load-bearing for how success is described.** `DIP24_2816`'s 19 chips
  are inhibited on the `0x2AAA` loads, not the `0x5555` loads; `DIP32_28C512_EEPROM`'s 18 are
  inhibited 0-of-6 from a fresh boot and only hazardous under a stale upper-address bit. Any plan
  prose saying "the `0x5555` writes are inhibited" is wrong for 19 chips.

</specifics>

<deferred>
## Deferred Ideas

### NEW PHASE — end-to-end `infoic.xml` `page_size` decode (operator-decided 2026-07-28)

**Not yet inserted into ROADMAP.md.** Insert with `/gsd-phase` after Phase 117 — note the
`.planning` memory `reference_new_milestone_phases_clear_destructive.md` warning about destructive
phase operations in this repo.

Locked decisions for that phase, made during this discussion:
- **Build the full path**: `infoic.xml` → `build_db.py` → `chip_database.json` → wire → 
  `json_parser.c` → `handle` → handler. This makes `constants.py:107`'s "Firmware sync" comment
  true for the first time.
- **Whole DB, XML wins on conflict.** Empirically a no-op for the curated `0x05` entries: XML and
  datasheet agree (W29C040 = 256, W29C020 = 128).
- **`0x0000` and `0x0001` both mean "not applicable" → omit the field → firmware default.** Matches
  the field dictionary's own wording and the existing "page_size absent → firmware heuristic"
  contract at `build_db.py:143`. An unknown non-sentinel value should fail the build, never be
  guessed.
- **Needs `/gsd-plan-phase --research-phase`.** Open questions research must settle first:
  1. **The 14-vs-84 provenance gap.** Only 14 DIP rows in `<database type='INFOIC2PLUS'>` carry
     `protocol_id == 0x0D`. Which XML row supplies `page_size` for the other ~70, given
     `PROTOCOL_MAP` is a pass-through and `classify()`/rule arms are what assign `0x0D`? The
     comment at `build_db.py:568` claims `DIP24_2816` chips "arrive from infoic.xml with proto_id
     0x0D", which the scan above does not corroborate — settle it.
  2. **`CLOSE-01`'s wording.** Adding a field to 84 DB rows produces a `diff_db.py` delta. CLOSE-01
     requires "the 84-chip count unchanged (confirmed via `diff_db.py` identity)". The *count* and
     `support_status` are unchanged; the field set is not. STATE.md already records a tolerated
     "pre-existing Phase-94 `PGSZ_PAGE_SIZE` delta", so restate CLOSE-01 as count-and-status
     identity with this delta named and phase-attributed.
  3. **`PGSZ-01` provenance tagging.** The curated map forbids `[ASSUMED]` and requires an in-repo
     datasheet `[CITED:]`. XML-sourced values are a third provenance class (upstream vendor data) —
     needs its own tag, not a misuse of either existing one.
  4. **The firmware-before-host ordering.** `json_parser.c` silently skips unknown fields and
     firmware falls back when `page_size == 0`, so host-emits-early is harmless (the v1.20 D-01
     precedent reasons identically) — but the plan order should still be FW-parse-first.

### Carried from Phase 116, still deferred
- **Widening the trace recorder to a third strobe kind** (data-bus direction). D-12 takes the
  production half only. RED-BASELINE §"Declined widening" is the named hook; Phase 118's owner.
- **Unity-teardown SIGABRT root cause** — `test_eeprom28c_chip_id` (now retired) and
  `test_flash_intel_vpp`. Pre-existing debt since Phase 17 WR-01 / Phase 20.
- **Recording every side-effecting `rurp_*` call** — rejected half of Phase 116's D-07.
- **All-84-chips table-driven trace coverage** — rejected half of Phase 116's D-09.
- **`DIP24_2816` has no `static-high-pins` key** (`static_high_mask == 0`, 19 chips). Tracked as
  **SDP-F8** in REQUIREMENTS.md §Future Requirements. The Phase-117 remap fix does **not** address
  it — record what the trace shows, do not act on it.
- **Datasheet verification of SDP magic addresses for AT28C040 / AT28C16 / AT28C04** — SDP-F7,
  recorded UNVERIFIED per size band. Note `116-PREMISE.md` §4 found two of the three cited
  datasheet PDFs absent from the tree by filename and the third unconfirmed.

### Reviewed Todos (not folded)
`todo.match-phase 117` returned matches on generic keyword overlap only; none touches the `0x0D`
write path, the SDP sequence, or the native harness. Same disposition as Phase 116:
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md` (firmware, 0.9) — VPP
  checks on reads; `0x0D` is VPP-free, and this phase touches no VPP path.
- `avrdude-mcu-detection-fallback.md` (0.6) — flashing/recovery, unrelated.
- `cobs-decoder-framelevel-deadline-wr01.md` (0.6) — v1.10 transport follow-up.
- `fix-jp4-labels-and-rev2-revision-block.md` (0.6) — jumper display, unrelated.

</deferred>

---

*Phase: 117-FIX — remap-aware `0x0D` emitter + honest completion signal*
*Context gathered: 2026-07-28*
