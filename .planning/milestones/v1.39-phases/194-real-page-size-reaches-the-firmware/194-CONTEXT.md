# Phase 194: Real Page Size Reaches the Firmware - Context

**Gathered:** 2026-09-15
**Status:** Ready for planning

<domain>
## Phase Boundary

The protocol `0x05` write path stops deriving a page size from total device capacity and consumes
the part's recorded page size, for **all 27** `algorithm: 5` parts — not only the 9 known to be
wrong. A write that cannot resolve a real page size refuses instead of guessing.

**In scope:** the generator's page-size emit arm (`firestarter_app/tools/build_db.py`), the
regenerated `chip_database.json`, a host pre-flight refusal, the firmware's
`flash_5v_page.cpp` consumption + refusal, the tests and goldens those move, and the 27-row
measurement record.

**Not in scope:** the partial/unaligned-write defect itself (gh#68 — that is Phase 195), any other
protocol, the `0x0D` delivery rule from Phase 149, and the stable firmware channel (D-5). A correct
page size does not by itself stop a partial write erasing the rest of the page.

**Measured starting state (2026-09-15, verified not assumed):**

| | |
|---|---|
| `algorithm: 5` rows in `chip_database.json` | 27 |
| carrying `programming.infoic_page_size_raw` | 27 of 27 |
| carrying `programming.page_size` today | **2** (`W29C020` 128, `W29C040` 256 — both datasheet-curated, both equal to their raw value) |
| derived page **==** real page | **18** |
| derived page **<** real page (always by exactly 2×) | **9** |
| derived page **>** real page | **0** |
| rows carrying `page_size` across the whole 746-row database | 20 (18 `0x0D`-native + 2 curated `0x05`) |

**Not fixed on `beta`.** Checked against `origin/beta` in both sub-repos, not `main`:
`src/proms/flash_5v_page.cpp`, `tools/build_db.py` and `firestarter/data/chip_database.json` are
each **byte-identical** to the working branch. `beta` has 27 `algorithm: 5` rows with 2 carrying
`page_size`, exactly as here. The data is present and correct. Nothing connects it to `0x05`.

</domain>

<decisions>
## Implementation Decisions

### Where the page size comes from

- **D-01: No hand-curated page sizes at all — `build_db.py` reflects infoic ground truth and the
  database is generated from that truth.** `_PAGE_SIZE_BY_PART` (`build_db.py:102`) is **removed**,
  along with its two entries and the emit arm that reads it. This is output-neutral: both entries
  are `0x05`, and both already equal their raw upstream value, so no emitted number changes as a
  consequence of the removal. — **Reversibility:** reversible — the table is 14 lines and its two
  values are recorded here and in `git log`.

- **D-02: Provenance keying is KEPT and extended to `0x05`.** The emit condition becomes: the row's
  **own upstream** `protocol_id` is `0x0D` **or** `0x05` → emit `raw_page_size`. It does **not**
  go flat across every row.

  The distinction is load-bearing and must not be flattened by a later agent. Phase 149's D-01/D-04
  established that a page value read out of a record filed under another algorithm says nothing
  about a page-write buffer — the 66 promoted `0x0D` rows arrived as `0x07`/`0x0B` (UV-EPROM, no
  page-write mechanism at all), and **31 of them carry a raw `page_size` of literally `1`**. Those
  66 stay omitted and keep the firmware's `AT28C_PAGE_SIZE_FALLBACK` floor. Two FRAM parts
  (`FM28V020`, `MB85R256H`) ride that handler by pinout promotion and have no page buffer whatever.

  `0x05` qualifies under exactly the rule that qualified the 18 `0x0D` rows: `classify()` arm 4
  (`build_db.py:348`) passes `0x05` through untouched, and arm 2's DIP28 promotion **explicitly
  excludes it** (`build_db.py:332`: "AT29C256/AT29LV256, proto 0x05 is NOT a 28C"). Every
  `algorithm: 5` row is therefore upstream-native `0x05`. **Research must check this by joining
  all 27 against the pinned upstream XML** — the same all-84 join Phase 149 ran — rather than
  inferring it from `classify()`'s arms alone.

  **Result: 20 → 45 `page_size` carriers** (18 `0x0D`-native + 27 `0x05`-native + 0 curated).
  — **Reversibility:** costly — the emitted database is a published artifact consumed by every
  installed host, and three gates plus a golden pin the current count.

- **D-03: The generator asserts what it emits, fail-closed.** `build_db.py` raises and writes **no
  database** if an emitted `page_size` is not a power of two within range — the same shape as
  `interpret_timing`'s existing fatal on an unparseable `pulse_delay` (`build_db.py:378-384`), and
  the shape backlog **999.57** proposes for `size_bytes`. It costs nothing today: all 45 emitted
  values are already 64/128/256/512. Its purpose is that a future infoic refresh cannot ship a
  value the firmware would refuse. — **Reversibility:** reversible.

- **D-04: `infoic_page_size_raw` is untouched** and stays the raw provenance axis, per Phase 149's
  D-02. It is not read on the wire and not read by the host.

### What the firmware does with it

- **D-05: Fail closed — no page size, no write.** When `handle->page_size` is absent, `0`, or fails
  validation on a `0x05` write, the firmware **refuses with a named error** and performs no write.
  It does not fall back to a derivation, and it does not guess.

  The reason a fallback has no safe value: a wrong page size is not a degraded mode in either
  direction. Too small → two page-write cycles commit into one physical page and the second erases
  the first (gh#67). Too large → the device's own load window closes at its real page boundary and
  auto-commits mid-load, past the point the firmware polls. Only an exact value is safe.
  — **Reversibility:** costly — reintroducing a fallback later means restoring a code path this
  phase deliberately removes, and re-arguing why guessing is acceptable.

- **D-06: `flash_5v_page_page_size()` is REMOVED, not retained as a fallback.**
  (`firestarter_fw/src/proms/flash_5v_page.cpp:27-31`.) The silent-corruption path leaves the
  binary rather than lingering behind a condition. Its block comment is removed with it — and per
  `CLAUDE.md`'s hard rule, no replacement comment is written into the source.
  — **Reversibility:** reversible — recoverable from `git show`.

- **D-07: The refusal is enforced in BOTH the host and the firmware.** The host refuses a `0x05`
  write **before any serial byte** when the resolved chip carries no `page_size` — the fail-closed
  in-host guard pattern established in v1.12 (`ProtocolNotImplementedError`) and v1.20 (the
  algorithm-presence guard). The firmware refuses independently, because it is the only layer that
  can protect the silicon from any caller. The host's message names the chip. The firmware's message
  is an error id. — **Reversibility:** reversible.

### How PAGE-02 is measured

- **D-08: A host data test over all 27 rows AND a native firmware consumption test.** Both, not
  either.
  - **Host:** extend `firestarter_app/tests/test_page_size_invariants.py` to a 27-row table that
    asserts, for every `algorithm: 5` part, (a) the emitted `page_size` equals the part's real page,
    **and** (b) for exactly the 18, that it also equals what the old derivation produced. The
    no-regression half of success criterion 2 is thereby **measured**, not asserted.
  - **Firmware:** a native test that drives `flash_5v_page_write_execute` over the 27
    `(mem_size, page_size)` pairs and asserts the page-start and page-commit boundaries land where
    the real page says. This is the half that matters: the host has been sending a correct
    `page-size: 128` on every `w29c020` write all along, and the firmware discards it — a
    host-only test would have passed throughout the defect's entire life.
  — **Reversibility:** reversible.

- **D-09: The firmware INFO log is NOT funded in this phase.** The pending todo
  `runtime-info-log-naming-the-effective-page-size.md` is tagged `resolves_phase: 194` and was
  reviewed and **not folded**. D-08's two tests cover all 27 at zero flash cost. The INFO log would
  cost a message id and a PROGMEM string against the Leonardo ceiling, and covers only the parts
  actually run. The todo stays pending, unmodified, with its `resolves_phase` tag intact.
  — **Reversibility:** reversible.

### Bench coverage

- **D-10: PAGE-03 cannot be met from current inventory — a `W29C512` is being ordered.** Every
  `0x05` part with bench history in this project (`W29C020`, `W29C040`, `sst39sf020`, `AE29F2008`)
  sits in the **correct 18**. Writing to one proves the 18 did not regress. It cannot prove the 9
  were fixed.

  `W29C512` was chosen over `AT29C040` and `AT29C020` because it is the same Winbond `W29C` family
  as the two `0x05` parts already bench-proven on this rig — socket, VPP routing, SDP unlock and
  the chip-ID path are all known-good, so **the page size is the only new variable**, which is what
  isolates the fix. At 64 KB it also writes fast.

  ⚠ **Name-collision hazard, carry this into the bench plan:** `W29C512` (Winbond `0x05` page-write
  flash, 128-byte page) is a **third distinct part** from `W27C512` (Winbond EEPROM, 12 V,
  algorithm `0x07` — the part actually on this bench) and `M27C512` (ST UV, 13 V). Check the
  seated part by **chip-ID**, never by the marking.

- **D-11: The software half lands now. PAGE-03's hardware leg is held OPEN.** The generator change,
  the firmware consumption + refusal, the 27-row measurement and a no-regression silicon run on a
  part from the 18 (`W29C020` — the part both gh#67 and gh#68 were reproduced on) all land in this
  phase. PAGE-03's hardware leg closes when the `W29C512` arrives.

  This is the hardware-gated-deferral shape v1.13/v1.14/v1.15 already use. It does **not** license
  marking PAGE-03 Complete: success criterion 4 requires the record to state which of the 9 were
  exercised on hardware and which rest on the database comparison, and those two must not be
  conflated. Until the part arrives that split reads **0 of 9 on hardware, 9 of 9 on the database
  comparison**. Phase 195 depends on Phase 194 and is unblocked by the software half.
  — **Reversibility:** reversible.

### Deferred out of this phase

- **D-12: The new-host / old-firmware skew is filed, not fixed.** A new host sends `page-size`. Old
  firmware ignores it and still derives — so the 9 corrupt silently and the user still sees
  `successful`. The host does **not** gate on firmware version for `0x05` writes in this phase.
  File it as a backlog item. Noted for whoever picks it up: `_probe_port`'s `[\d.x]+` truncates the
  prerelease suffix, so the host cannot distinguish `b11` from `b12` — any version boundary must
  sit where the numeric part alone is decisive. — **Reversibility:** reversible.

### Claude's Discretion

- **Where the 27-row record lives** — the operator said "you decide". Decision: a **committed
  artifact under `.planning/v1.39/`**, a 27-row table (part · size · derived · real · verdict ·
  evidence class) following the `.planning/v1.33/sweep-outcome-record.md` precedent, with
  `194-SUMMARY.md` citing it rather than duplicating it. Reasoning: Phase 195 and the gh#67 reply
  both need to cite it, it survives the milestone archive, and it avoids the self-regenerating-
  golden hazard this project has been bitten by (`audit-coverage-matrix` mutating its own ledger).

- **The mask-vs-`%` implementation shape** (see Existing Code Insights) and the naming of the
  refusal error id are left to research and planning.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone intent and locked decisions
- `.planning/REQUIREMENTS.md` — PAGE-01/02/03 verbatim. D-1 (silent corruption is the milestone),
  D-3 (page size comes from the database, not a second derivation), D-4 (bench validation required),
  D-5 (stable channel out of scope). Also §Out of Scope.
- `.planning/ROADMAP.md` §"Phase 194: Real Page Size Reaches the Firmware" — the four success
  criteria and the "Prior art — check before building a new seam" note.
- `.planning/PROJECT.md` §"Current Milestone: v1.39" — the activation decisions D-1…D-5.

### Prior art — the page-size seam already exists (READ FIRST)
- `.planning/milestones/v1.32-phases/149-firmware-page-size-seam-dual-repo-lockstep/149-CONTEXT.md`
  §"Implementation Decisions" — **D-01** provenance keying and the measured all-84 upstream join,
  **D-02** reuse of `programming.page_size` + "the host needs ZERO code change", **D-03** emit for
  corroborated rows including no-change ones, **D-04** why the 66 promoted rows keep the floor.
  This phase extends D-01/D-02. It must not reverse them.
- `.planning/todos/pending/promoted-0x0d-rows-keep-the-64-byte-floor.md` — the measured
  four-way provenance table and the 11 rows at 16/32 whose floor safety is **unproven, not
  disproven**. Adjacent to this phase, deliberately not in scope.
- `.planning/todos/pending/runtime-info-log-naming-the-effective-page-size.md` — tagged
  `resolves_phase: 194`. Reviewed and **not folded** (D-09). Its "Edit point" section is the
  authority if a later phase funds it: the catalog, never `include/messages.h`.

### Firmware
- `firestarter_fw/src/proms/flash_5v_page.cpp:27-31` — `flash_5v_page_page_size()`, the derivation
  being removed (D-06). `:82,92,100` — the `%`-by-variable-divisor page arithmetic being replaced.
- `firestarter_fw/src/proms/eeprom_28c.cpp:392-410` — `eeprom28c_page_mask()`. The reference
  implementation for validation and for the mask form. Its own comment states why `%` by a variable
  divisor is forbidden here.
- `firestarter_fw/include/firestarter.h:186` — `uint16_t page_size` on the handle, "0 = absent".
- `firestarter_fw/src/json_parser.c:70,150-156,271-280` — the `page-size` wire key, its FIELD row,
  and the per-command reset to 0.
- `firestarter_fw/test/native/avr/test_read_timing/test_read_timing_params.cpp:136-419` — the
  existing `page-size` **parse** tests. They prove parsing only. Nothing today tests consumption.

### Host
- `firestarter_app/tools/build_db.py:102-115` — `_PAGE_SIZE_BY_PART`, deleted by D-01.
- `firestarter_app/tools/build_db.py:696-714` — the provenance-keyed emit arm extended by D-02.
- `firestarter_app/tools/build_db.py:332,348` — `classify()` arm 2's explicit `0x05` exclusion and
  arm 4's pass-through, the basis for the upstream-native claim.
- `firestarter_app/tools/build_db.py:378-384` — `interpret_timing`'s fatal-on-unparseable, the
  shape D-03 mirrors.
- `firestarter_app/firestarter/database.py:401-415` and `:545-554` — the `page_size` carry and the
  algorithm-agnostic `page-size` wire emit. Both already work. No change is expected here.
- `firestarter_app/firestarter/constants.py:141-149` — `JSON_KEY_PAGE_SIZE` and its firmware-sync
  note.

### Gates that pin the current shape — these move deliberately, not incidentally
- `firestarter_app/tests/test_page_size_invariants.py` — asserts exactly **20** carriers
  (18 native + 2 curated) across 746 rows. Becomes 45 native + 0 curated.
- `firestarter_app/tests/test_vcc_margin_rail.py:234-248` — asserts
  `len(build_db._PAGE_SIZE_BY_PART) == 2`. D-01 removes the dict this gate names.
- `firestarter_app/tests/golden/chip_database_field_inventory.json:14` — records the count of 20 and
  carries a `how_to_update` instructing an **independent re-derivation**, never a hand edit.

### Issues
- https://github.com/henols/firestarter/issues/67 — gh#67, this phase's defect, with the operator's
  bench evidence (`W29C020`, Leonardo, Rev 2.0-class shield, fw `3.0.0b22`, host `3.0.0b38`).
- https://github.com/henols/firestarter/issues/68 — gh#68, Phase 195's defect. Read for the
  boundary, do not fix here.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **The whole wire seam already exists and needs no new plumbing.** Phase 149 built it:
  `page-size` (hyphen) → `handle->page_size` (underscore), `uint16_t`, reset to 0 per command,
  validated at parse. `database.py:553` emits it **algorithm-agnostically**. The consequence worth
  stating plainly: **the host already sends `page-size: 128` on every `w29c020` write today and
  `flash_5v_page.cpp` throws it away.** Phase 194 is two small seams — one generator arm, one
  handler read — not a new transport.
- **`eeprom28c_page_mask()`** (`eeprom_28c.cpp:401-410`) is a complete, reviewed reference for
  validation: reject `0` explicitly **before** the power-of-two test (`0 & (0-1) == 0` admits zero
  on an unsigned type), then accept power-of-two within a **board-invariant** ceiling
  (`AT28C_PAGE_SIZE_MAX 512`, deliberately not `DATA_BUFFER_SIZE`, so the rule is identical on
  every build). Note the behavioural difference to carry across: `eeprom_28c` **falls back**,
  but `flash_5v_page` must **refuse** (D-05).

### Established Patterns

- **Mask, never `%`.** `eeprom_28c.cpp:412-418` resolves the page mask **once** outside the byte
  loop, and its comment states why: a runtime `%` by a variable divisor pulls `__udivmodsi4` into a
  build with no flash headroom. `flash_5v_page.cpp:92,100` uses exactly that forbidden `%` today.
  Adopting the mask form may **free** flash rather than cost it — worth measuring, because it bears
  on whether D-09's INFO log could ever be funded.
- **Resolve once, outside the loop, in `operation_main` — not `write_init`.** `eeprom_28c.cpp`'s
  comment gives both reasons: `write_init` returns early on a chip-ID mismatch, and the native
  suites drive `operation_main` directly without ever calling `operation_init`.
- **Fail closed in the host before any serial byte** — v1.12's `0xBB` / `ProtocolNotImplementedError`
  and v1.20's algorithm-presence guard. D-07 follows it.
- **The database is GENERATED.** `chip_database.json` is never hand-edited. Fix the generator and
  regenerate. The field-inventory golden's own `how_to_update` demands an independent
  re-derivation.

### Integration Points

- `build_db.py` emit arm → regenerated `chip_database.json` → `database.py` `_map_data` →
  `get_data_for_command` → wire `page-size` → `json_parser.c` FIELD row → `handle->page_size` →
  `flash_5v_page_write_execute`. Every link but the first and last already exists and is tested.
- **Chunking is not a hazard here, and this was checked.** The host chunk size is
  `firmware_max_chunk` = `DATA_BUFFER_SIZE` exactly (512 Uno / 1024 Leonardo,
  `eprom_operations.py:416-429`), both powers of two. The largest real page among the 27 is 512, so
  on a page-aligned contiguous write every chunk boundary is also a page boundary. Unaligned starts
  are a different matter — and they are Phase 195's, not this phase's.

### Known blind spots for the native test author

- Native trace stubs miss register-write elision unless `rurp_register_utils.h` is included in
  `host_stubs`, and they record **no time** (`delay()` is unstubbed) — a trace diff cannot prove
  timing.
- A golden trace whose message ids match can still miss a WARN/ERROR fork. A refusal path needs its
  own mismatch test, not only a matching-id trace.

</code_context>

<specifics>
## Specific Ideas

- The operator's framing, verbatim in substance: *"no curated rows, the build_db.py must reflect the
  ground truth from infoic and generate the database after the truth."* That is D-01, and it is
  stronger than the option originally put forward (which would have kept the curated table and
  merely added an arm beside it).
- The operator's first instinct was to ask whether the page size was already in infoic and whether
  `beta` had already fixed this. Both were checked before answering: yes to the first, no to the
  second. That check is recorded in §Phase Boundary so no downstream agent repeats it.
- Independent corroboration for the raw values, worth reusing in the record: the AT29C020 datasheet
  states reprogramming is sector-based with "256 bytes of data loaded into the device and then
  simultaneously programmed", matching `infoic_page_size_raw: 256` for that part without going
  through infoic at all. The load window closes ~150 µs after the last byte transition, after which
  the device commits the whole sector — the mechanism behind gh#68.

</specifics>

<deferred>
## Deferred Ideas

- **New-host / old-firmware version skew for `0x05` writes** (D-12) — file as a backlog item. The
  host would send `page-size` to firmware that ignores it, leaving the 9 corrupting silently.
  Includes the `_probe_port` prerelease-truncation caveat.
- **A firmware INFO log naming the effective page size** (D-09) — stays as the pending todo
  `runtime-info-log-naming-the-effective-page-size.md`, `resolves_phase: 194` tag intact. Revisit
  when there is measured Leonardo flash headroom. The mask-for-`%` swap in this same file may
  create some.
- **The same defect class in the other 12 protocols** — out of scope per `REQUIREMENTS.md`. If found,
  file it.
- **The 11 promoted `0x0D` rows at raw 16/32** whose 64-byte floor safety is unproven — Phase 149's
  D-04, unchanged by this phase, still pending.

### Reviewed Todos (not folded)

- **"Runtime INFO log naming the effective page size firmware actually used"**
  (`.planning/todos/pending/runtime-info-log-naming-the-effective-page-size.md`, tagged
  `resolves_phase: 194`) — reviewed, **not folded**. D-08's two tests satisfy PAGE-02 across all 27
  at zero flash cost. The INFO log costs a message id against the Leonardo ceiling and covers only
  the parts actually run. Left pending and unmodified.
- **"66 promoted 0x0D rows keep the 64-byte page floor"**
  (`.planning/todos/pending/promoted-0x0d-rows-keep-the-64-byte-floor.md`) — reviewed, **not
  folded**. `0x0D`, not `0x05`. It is adjacent, and D-02 deliberately leaves the `0x0D` rule untouched.

</deferred>

---

*Phase: 194-real-page-size-reaches-the-firmware*
*Context gathered: 2026-09-15*
