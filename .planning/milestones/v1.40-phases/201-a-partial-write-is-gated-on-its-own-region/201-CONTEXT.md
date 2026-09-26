# Phase 201: A partial write is gated on its own region - Context

**Gathered:** 2026-09-19
**Status:** Ready for planning

<domain>
## Phase Boundary

The write-init blank check stops gating a partial write on the whole device. A non-erasable part
holding data anywhere stops being unwritable everywhere.

**In scope:** one new wire field carrying the region, the firmware seam that consumes it in
`eprom.cpp`'s write-init path, the region-scoped blank-check implementation in `memory.cpp`, the
regression test whose absence is why this shipped, and one bench session on real silicon.

**Out of scope:** the host half of backlog 999.44 (**already shipped** — see D-01), the standalone
`CMD_BLANK_CHECK` command's behaviour, the erase-end check's behaviour, the other two write-init
blank-check call sites (D-09), any refusal-policy change, and the VPP checks that run in
`eprom_generic_init` above the blank check.

**This is the only firmware change and the only dual-repo lockstep in v1.40.**

</domain>

<decisions>
## Implementation Decisions

### What is already true, measured before deciding anything

- **D-01:** **The host half of 999.44 is already shipped — this phase is the firmware half only.**
  The todo prescribes two halves: (a) region-scope the firmware write-init check, (b) pass
  `FLAG_SKIP_BLANK_CHECK` on `uv-slot` writes in `chip_test.py`. Half (b) landed in v1.36 Phase 179
  and quick `260821-wna`; it is live at `firestarter_app/firestarter/chip_test.py:3310`
  (`FLAG_SKIP_BLANK_CHECK if _is_monotonic_masked_target(resolved_target) else 0`) and pinned by
  `tests/test_chip_test_uv_slot_write.py`. The ROADMAP's phrase "999.44's **live firmware half**" is
  literal. **Nothing in this phase touches `chip_test.py`'s flag decision.**

- **D-02:** **The firmware cannot know the write length at INIT, so the region end must be supplied.**
  Measured, not assumed: `handle->data_size` is written only by `op_get_message`'s `'#'` arm
  (`firestarter_fw/src/operation_utils.cpp:145-152`), which runs in MAIN;
  `_execute_operation_house_keeping` runs INIT strictly before MAIN
  (`firestarter_fw/src/operation_utils.cpp:167-190`). At the moment
  `eprom_internal_write_init_body` calls the blank check, the only region information on the handle
  is `handle->address`. **This is the fact that eliminates every firmware-only option.**

### Where the region comes from

- **D-03:** **A new wire field, shaped exactly like `page_size`.** A `FIELD(...)` entry in
  `firestarter_fw/src/json_parser.c`, a new `firestarter_handle_t` member reset per command in
  `json_parse` exactly as `chip_id` and `page_size` are, and a host-side emit in the programmer dict.
  Chosen over narrowing `memory-size` and over a firmware-only change. **Name it for the region, not
  for writing** — `region-size` on the wire, `handle->region_size` in the firmware — because D-06
  puts it on `CMD_VERIFY` as well.
  — **Reversibility:** costly — removing a wire field after a beta cut means a host that sends a key
  the firmware no longer parses. The `0 = absent` semantics in D-04 are what make that survivable in
  both directions.

- **D-04:** **Absent (`0`) means whole device — byte-identical to today.** New firmware paired with an
  old host behaves exactly as the current firmware does; the relaxation happens only when a host
  explicitly asks for it. **This deliberately INVERTS Phase 194's `page_size` precedent**, where
  absent means refuse. The inversion is the point: `page_size` guarded a *destructive* write, where
  refusing is the safe direction. This field guards a *relaxation*, where falling back to the
  stricter existing behaviour is the safe direction. Do not "correct" this to match `page_size`
  without re-reading this sentence.

- **D-05:** **The host sends it on every write, not only when `--address` is given.** One code path,
  no branch on address presence. **Named consequence, accepted rather than discovered later:** a
  4 KiB file written to a blank-required 64 KiB part stops blank-checking the 60 KiB it will not
  touch. That is the same defect in a milder dress, and it is being fixed in the same motion rather
  than left as a special case.

- **D-06:** **The field bounds the write path too, not only the blank check** — the region end
  replaces `mem_size` in `_process_incoming_data`'s done-condition
  (`firestarter_fw/src/eprom_operations.cpp:90`), its `MSG_ERR_OUT_OF_RANGE` refusal (`:128`), and
  the write loop's own progress denominator (`firestarter_fw/src/proms/eprom.cpp:397`).

  **There are three `MSG_DATA_PROGRESS` denominators and only one of them is this one.** Verified
  during this discussion, because getting it wrong would breach BLANK-02:
  - `firestarter_fw/src/operation_utils.cpp:235` — inside `_single_step_operation_callback`, reached
    **only** when `handle->cmd == CMD_BLANK_CHECK`. That is the standalone command. **It must not
    move.**
  - `firestarter_fw/src/proms/memory.cpp:510` — inside the blank-check scan itself, guarded by
    `if (handle->cmd != CMD_BLANK_CHECK)`, so it is the **write-init and erase-end** emit. It should
    report against whichever range its own call is scanning, which falls out for free once D-09's
    form carries `start`/`end` — `mem_size` for the erase-end whole-device scan, the region end for
    write-init. **Note the clamp two lines above it** (`memory.cpp:501-502`,
    `if (handle->address > handle->mem_size) handle->address = handle->mem_size;`) is keyed on
    `mem_size` and must become `end`-relative in the region form, or the final progress frame of a
    region scan reports past the region.
  - `firestarter_fw/src/proms/eprom.cpp:397` — the per-byte write-loop emit, Leonardo-only. **This is
    the one this decision moves.**

  **Verified cheap before locking it:** `_apply_write_progress`
  (`firestarter_app/firestarter/eprom_operations.py:690-729`) already **discards** the frame's total
  (`absolute, _total_ignored = map(int, ...)`) and its docstring says why — the bar is started with
  the file size while the frame carries the chip's memory size, so honouring it would tear the bar
  down and rebuild it on every frame. **So the operator-visible progress bar does not move.** The
  change makes the two agree for the first time, which retires the *reason* that workaround exists
  (retiring the workaround itself is deferred, not in scope).
  Under D-05 the host and firmware agree on the region by construction, so the out-of-range refusal
  should never fire in normal operation — it becomes a fail-closed guard against a host/file
  mismatch rather than a live path.

- **D-07:** **The host sends the field on `CMD_VERIFY` too.** `_process_incoming_data` is shared by
  `eprom_write` and `eprom_verify` (`firestarter_fw/src/eprom_operations.cpp:23-31`), so D-06 bounds
  verify whether or not the host cooperates. Sending it makes write and verify agree on where the
  operation ends. Verify is the step that adjudicates a write; the two disagreeing on bounds is a
  divergence someone would eventually trip over.

- **D-08:** **`mem_size` keeps meaning device size. It is not narrowed.** Recorded because the
  cheaper-looking alternative is actively unsafe: `eeprom28c_check_chip_id`
  (`firestarter_fw/src/proms/eeprom_28c.cpp:190`) derives `mfr_addr = handle->mem_size - 64` and
  **drives 12 V on A9 at that address**, and it is called from `eeprom28c_write_init` (`:343`). A host
  that narrowed `memory-size` on writes would put 12 V on A9 of an arbitrary address on every partial
  AT28C write. Scoping the narrowing per-protocol was considered and rejected separately: it would
  add a host-side algorithm branch, which is precisely what v1.20 removed and what the
  no-second-selector gate exists to prevent. `flash_intel.cpp`, `flash_nor_unlock.cpp` and
  `flash_utils.cpp` read `mem_size` nowhere; `eprom.cpp` reads it only for the progress denominator.

### The firmware seam

- **D-09:** **`mem_util_blank_check_region(handle, start, end)` holds the scan; `mem_util_blank_check`
  becomes a one-line whole-device wrapper passing `(0, handle->mem_size)`.** One code path, so the
  four callers cannot drift, and the region form is unit-testable in isolation. This satisfies
  BLANK-02's "a region-scoped variant or a start/end parameter — **not** an edit in place".
  **The chunking mechanics favour it:** for write-init, `blank_check_saved_address` and the region
  start are *the same value*, so the region form is literally "do not reset the cursor to 0, and stop
  at `end` instead of `handle->mem_size`". The `handle->cmd == CMD_BLANK_CHECK` branch already inside
  the scan (the Uno `com_mode` emit fork) is untouched.

- **D-10:** **Only `eprom.cpp:145` changes. `flash_intel.cpp:95` and `flash_nor_unlock.cpp:105` do
  not.** Those two protocols' parts carry `FLAG_CAN_ERASE`, so the erase immediately above leaves the
  device blank and the check passes trivially — the same mechanism that hid this defect for its whole
  life. BLANK-01, BLANK-02 and BLANK-03 are all satisfied by `eprom.cpp` alone.

- **D-11:** **The record states the latency is one flag deep, as a named non-claim.** Calling the
  other two sites "latent" without this would be wrong: `--skip-erase` sets `FLAG_SKIP_ERASE`, no
  erase runs, and the whole-device check fires identically on an erasable part — including on the
  three validated flash parts. Saying so is what makes a later "why was this not fixed everywhere"
  answerable, and it is the shape Phase 194 used for the 18 parts it did not exercise. **It is also
  the mechanism D-12 relies on for the rehearsal part**, so it must be stated, not merely known.

### The proof

- **D-12:** **Two parts: W27C512 rehearses, TMS27C512 confirms.**
  - **W27C512** (`0xDA08`, validated 2026-08-31, `electrical.type: EEPROM` → `FLAG_CAN_ERASE` set)
    driven with `--skip-erase`. Electrically erasable, so RED→GREEN can be rehearsed as many times as
    it takes without consuming anything, on a code path that is byte-identical per D-11.
  - **TMS27C512** (`0x9785`, validated 2026-09-12 on fw `3.0.0b27`, `electrical.type: UV-EPROM` →
    `FLAG_CAN_ERASE` clear) for **one** confirming run, so criterion 1's own words — *non-erasable* —
    rest on the thing itself rather than on a proxy argument.

  The erase axis was measured, not assumed: `FLAG_CAN_ERASE` is set at
  `firestarter_app/firestarter/database.py:577-579` from `electrical-type ∈ {EEPROM, Flash/EEPROM}`
  and `algo != 5`, and nothing else.

- **D-13:** **AM27C020 is NOT the bench part, despite being the part in the transcript.** v1.18
  recorded its write path as effective-but-marginal on the operator's own bench — write #1 landed
  60/64 bytes, write #2 landed 0/64 — and it never graduated (FUT-08). A failed write on it would be
  uninterpretable, and a successful one would be unrepeatable. It is cited as the defect's origin,
  never as its proof.

- **D-14:** **The bench run gates the phase.** Unlike v1.39's PAGE-03, whose hardware leg was held
  open because nobody had a `W29C512`, the silicon here is on hand and validated. Software lands,
  bench runs, then the phase closes. No D-11-shaped deferral is authorised for this criterion.

- **D-15:** **BLANK-02's proof is the two native tests plus a source-contract gate — not a trace
  diff.** (Claude's decision, delegated by the operator.)
  1. **Native, multi-chunk resumption** — a part larger than `BLANK_CHECK_CHUNK_SIZE` (8192) driven
     through `CMD_BLANK_CHECK` across several calls, asserting the cursor advances and is restored to
     `blank_check_saved_address` at completion. This is the contract the todo names by name.
  2. **Native, erase-end arm** — `eprom.cpp:53`'s `firestarter_operation_end = mem_util_blank_check`
     with an erasable part, asserting it still scans from 0.
  3. **Source-contract gate** — a `firestarter_fw/tests/*.py` scan asserting the whole-device entry
     point still passes `(0, mem_size)` and that no caller but write-init passes a region, so a later
     edit cannot quietly widen the relaxation. The shape `test_write_path_source_contract_v131.py`
     established.
  **Explicitly not the golden trace diff.** The todo's own closing line: the native trace stubs
  record no time and miss register-write elision, so a trace diff cannot carry this change. The
  branch-inventory golden must still be re-derived (see D-17) — that is an obligation this phase
  incurs, not evidence it produces.

- **D-16:** **BLANK-03's regression test is four artefacts, one of which is evidence rather than a
  test.** (Claude's decision, delegated by the operator.)
  1. **Native — the test whose absence the todo names.** In `test/native/avr/test_val_eprom`: seed
     the `firestarter_get_data` mock non-blank *outside* the region, drive `eprom_write_init` with
     `ctrl_flags = 0` and a region set, assert `response_code != RESPONSE_CODE_ERROR`. Runs in CI on
     both `native` and `native_nodevtools`. **Goes RED before the fix**, per the todo.
  2. **Host — the product bug (the todo's consequence 1).** `write -a` end to end against
     `fake_chip.py`. **Caveat that must reach the planner:** `fake_chip._is_blank()`
     (`firestarter_app/tests/fake_chip.py:265-268`) compares the whole buffer against
     `b"\xff" * memory_size` and `write_eprom` gates on it at `:282` — the fake models the
     whole-device check exactly, so this leg passes **vacuously** unless the fake learns the region.
     `tests/test_uv_mask.py:201` leans on the fake's current behaviour, so that is a coupled edit.
  3. **Host — constants and wire parity.** The new field pinned so the host key and the
     `json_parser.c` `FIELD` entry cannot drift, per CLAUDE.md's cross-repo obligation. The firmware
     side of that obligation is the `_Static_assert` on the handle member's offset
     (`firestarter_fw/src/json_parser.c:164-166`).
  4. **The bench transcript — committed as evidence, labelled as evidence.** The shape Phase 194 plan
     07 used for its `W29C020` run. It cannot re-run in CI and the record must not imply it can.

### Claude's Discretion

- The wire key's exact spelling and unit (length versus end address), the firmware member's type
  (a 512 KiB part needs 20 bits, so `uint32_t`), and where in `_setup_operation` the host computes
  it. Constrained only by D-03's naming rationale and by the `_Static_assert` offset column.
- Where the region-scoped call sits inside `eprom_internal_write_init_body` relative to the existing
  `FLAG_SKIP_BLANK_CHECK` guard, provided the single-exit HV wrapper at `eprom.cpp:152-158` still
  sees every exit.
- Test file names, fixture shapes, and how the RED-first state is captured — provided the native leg
  in D-16.1 is *seen* to be RED before the fix lands, not asserted to have been.
- Whether the two native legs in D-15 live in `test_val_eprom` or a new test directory.

### Folded Todos

- **`.planning/todos/pending/2026-08-30-write-init-blank-check-is-whole-device.md`** — backlog
  999.44. This IS the phase: the `AM27C020` bench transcript, the three consequences (product bug,
  defeated UV slot design, report blames the chip), the two-half fix, and the "regression test that
  does not exist". Half (b) is already shipped per D-01; this phase closes half (a), and closing it
  retires the todo.
- **`.planning/todos/pending/2026-09-08-uv-write-shortcut-disclosure-key.md`** — filed because
  `dev test m27c512` passes on a non-blank UV part via `FLAG_SKIP_BLANK_CHECK` while
  `firestarter write -a` is refused by the identical firmware, with nothing disclosing the
  divergence. **This phase removes the premise.** After it, `write -a` into a blank region succeeds,
  so the two paths converge for the blank-region case. The residual divergence is narrower and
  differently shaped: `dev test` still passes the flag for a *masked* write into a
  partially-programmed slot, where the target is not blank. The phase should record which of the
  todo's two proposed answers ("both, or neither") the narrowed divergence now warrants, rather than
  leave it pointing at a Phase 181 that has closed.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### This phase's scope and its source
- `.planning/ROADMAP.md` § "Phase 201: A partial write is gated on its own region" — the goal, the
  three success criteria, and the bench-gated marking in the v1.40 phase table.
- `.planning/REQUIREMENTS.md` § "BLANK — a partial write is gated on the region it writes" —
  BLANK-01, BLANK-02, BLANK-03 in full.
- `.planning/todos/pending/2026-08-30-write-init-blank-check-is-whole-device.md` — **the primary
  source.** Carries the bench transcript, the "why it stayed hidden" analysis, the three
  consequences, the explicit two-half fix with its "(a) alone is insufficient / (b) alone is
  insufficient" reasoning, and the closing warning about trace stubs. Read this before anything else.
- `.planning/todos/pending/2026-09-08-uv-write-shortcut-disclosure-key.md` — the divergence this
  phase collapses; folded per the Folded Todos section.

### The firmware code this phase changes
- `firestarter_fw/src/proms/memory.cpp:425-513` — `mem_util_blank_check` (`:450`), the
  `blank_check_saved_address` static and its "do not replace with a heap allocation" rationale,
  `BLANK_CHECK_CHUNK_SIZE`, the `handle->cmd == CMD_BLANK_CHECK` emit fork at `:480`, and the
  `mem_size`-keyed clamp and write-init/erase-end progress emit at `:501-510`.
- `firestarter_fw/src/proms/eprom.cpp:128-158` — `eprom_internal_write_init_body` and the
  single-exit HV wrapper whose "a `return` added inside the body later cannot bypass it" property
  the region call must not break. `:45-63` for the other two callers (`CMD_ERASE`'s
  `firestarter_operation_end`, `CMD_BLANK_CHECK`'s `firestarter_operation_main`).
- `firestarter_fw/src/eprom_operations.cpp:86-144` — `_process_incoming_data`, shared by write and
  verify; the three `mem_size` sites D-06 moves.
- `firestarter_fw/src/operation_utils.cpp:112-190` — `op_get_message` (`data_size` is set at `:152`)
  and `_execute_operation_house_keeping_func` (the INIT-before-MAIN ordering that D-02 rests on).
  `:229-236` is the standalone-`CMD_BLANK_CHECK` progress emit that BLANK-02 protects.
- `firestarter_fw/src/json_parser.c:120-170` — the `FIELD(...)` table, the per-command reset block,
  and the offset `_Static_assert` the new member must satisfy.
- `firestarter_fw/include/firestarter.h:168-215` — the handle struct, and `page_size`'s comment as
  the template for the new member's own.

### Gates this phase will redden, and how
- `firestarter_fw/tests/test_protocol_branch_inventory.py` + `tests/golden/protocol_branch_inventory.json`
  — pins `src/proms/eprom.cpp`'s **blob SHA** and **every branch predicate positionally** on
  `(line, predicate, keyed_on, tier)`, currently 21 sites including
  `{"line": 144, "predicate": "if (!is_flag_set(FLAG_SKIP_BLANK_CHECK))"}`. **Any** edit to that file
  reddens it. The golden's own `meta.recorded_at_head` note records that the re-derivation and the
  source change must land in the **same commit**.
- `firestarter_fw/tests/test_write_path_source_contract_v131.py` — the shape D-15.3's new gate
  should follow.
- `firestarter_app/tests/fake_chip.py:265-288` — models the whole-device check; see D-16.2 for why
  this is a coupled edit and not a local one.
- `firestarter_app/tests/test_uv_mask.py:201` — depends on the fake's current blank semantics.

### Cross-repo obligations
- `/workspaces/CLAUDE.md` § "Cross-repo obligations" — serial-protocol changes must stay in sync
  between `serial_comm.py` and `firestarter.cpp`; constants and flag bits are duplicated between
  `constants.py` and three firmware headers and **must change in the same commit pair**. This phase
  adds a wire field, so both clauses bind.
- `/workspaces/CLAUDE.md` § "Milestone close and branch protection" — **a push to `beta` in either
  sub-repo PUBLISHES.** Neither beta workflow carries a path filter.

### Where the host half already landed (do not re-do)
- `firestarter_app/firestarter/chip_test.py:3310` — the shipped `FLAG_SKIP_BLANK_CHECK` decision.
- `firestarter_app/tests/test_chip_test_uv_slot_write.py` — its regression coverage, including
  `test_the_blank_check_adjudication_is_what_lifts_the_run_to_pass`.

### Precedent for the wire field's shape
- `.planning/ROADMAP.md` § "Phase 194: Real Page Size Reaches the Firmware" — the `page_size` wire
  field, its cross-cutting constraint ("a protocol 0x05 write with no resolvable page size produces
  no write at all"), and the four-plan host/firmware split. **D-04 inverts that constraint's
  direction on purpose** — read D-04 before treating Phase 194 as the template for absent-semantics.

### Why the alternative mechanism was rejected
- `firestarter_fw/src/proms/eeprom_28c.cpp:171-195` and `:339-347` — the `mem_size - 64` → 12 V on A9
  derivation reached from `eeprom28c_write_init`, which is what makes narrowing `memory-size` on
  writes a hardware-safety problem rather than a style preference (D-08).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`page_size` is a complete worked example of this exact change.** A per-chip value delivered over
  the wire, `0 = absent`, reset per command in `json_parse`, with an offset `_Static_assert` and a
  host/firmware constants-parity test. The new field copies its shape end to end; only the
  absent-semantics differ, deliberately (D-04).
- **`mem_util_blank_check`'s chunking already threads the cursor through a saved address.** The
  region form needs no new state: `blank_check_saved_address` and the region start coincide on the
  write-init path, so the change is "do not reset to 0" plus "stop at `end`".
- **`test/native/avr/test_val_5v_page/test_val_5v_page.cpp:200-230, 785-820`** — the established
  pattern for driving a write-init through the dispatched pointer with `FLAG_CAN_ERASE` and
  `FLAG_SKIP_BLANK_CHECK` explicitly cleared, and for asserting on `is_operation_in_progress` as the
  observable that the blank check ran. Directly reusable for D-16.1.
- **`firestarter write --skip-erase`** already exists (`cli_handlers.py:573`) and is explicitly
  decoupled from `-b` (`:342` — "`-b`/`--no-blank-check` does NOT imply skip-erase"). This is what
  makes the W27C512 rehearsal in D-12 possible without a DB edit.

### Established Patterns
- **Two other protocols solved this by deletion, not by scoping.** `eeprom_28c.cpp:379-385` and
  `flash_5v_page.cpp:74-78` both removed their pre-write blank check outright, each with the same
  reasoning: "a false precondition that made a non-blank part un-writable without a flag", and each
  with an explicit "`FLAG_SKIP_BLANK_CHECK` is consequently UNREAD here — do not restore the
  conditional because the bit looks orphaned." Deletion is not the right answer for UV parts (a
  programmed bit cannot be un-programmed, so the precondition is real there), but the planner should
  know this precedent exists before proposing it.
- **Exact counts asserted as equalities and proved non-vacuous by a planted mutation** — the
  discipline established in Phase 199 and carried through Phase 200's census.
- **Firmware CI is exactly three legs:** `pio test -e native`, `pio test -e native_nodevtools`, and
  `pytest tests/ -v` (`.github/workflows/build.yml:109-130`). There is **no size-baseline gate in
  CI** — `scripts/check_size_baseline.py` is gone, leaving only `__pycache__` artefacts. Flash
  headroom is still a physical constraint (Leonardo's real ceiling is 28672, not 32768) but nothing
  automated will catch a regression, so any size claim must be measured deliberately.

### Integration Points
- `firestarter_fw/src/proms/eprom.cpp:144-145` — the one call site that changes.
- `firestarter_fw/src/proms/memory.cpp:450` — where the region implementation lands and the
  whole-device wrapper stays.
- `firestarter_fw/src/json_parser.c` — the `FIELD` table entry and the per-command reset.
- `firestarter_app/firestarter/database.py:520-580` — `convert_to_programmer`'s wire dict, where
  `page-size` is conditionally added and `flags` is computed; the natural home for the new key.
- `firestarter_app/firestarter/eprom_operations.py:479-497` — `_setup_operation`, which already does
  exactly this narrowing arithmetic for `COMMAND_READ` (`command_dict["memory-size"] = addr + read_size`).
  The write path knows its file size at `:762` (`file_size = os.path.getsize(input_file_path)`), but
  the command dict is built and sent before that, so the planner must confirm where the size is
  available early enough.

### Integration risks named during discussion
- **`fake_chip.py` will pass vacuously** unless it learns the region (D-16.2).
- **`test_protocol_branch_inventory.py` reddens on any `eprom.cpp` edit**, and its re-derivation must
  land in the same commit as the source change.
- **A `beta` push publishes.** This is a dual-repo lockstep phase; decide the scope of any beta push
  before making it.

</code_context>

<specifics>
## Specific Ideas

- **The bench transcript to reproduce first, then invert.** The todo's own `AM27C020` run is the
  template for the RED shape:
  ```
  blank-check   BAD  Not blank, at 0x000000, v: 0x02
  write-partial BAD  Programmer error during init: Not blank, at 0x000000, v: 0x02
  verify        BAD  0xfe != 0xff at 0x03ff00
  ```
  The `verify` line is what proves the target slot was blank — actual `0xFF` at the slot start, while
  the write was refused on account of a byte 262 KB away. The GREEN transcript is the same three
  steps with the middle one passing.
- **The rehearsal recipe, stated concretely:** `firestarter write <file> -a <addr> --skip-erase` on a
  W27C512 whose low addresses hold data and whose target region is blank. `FLAG_CAN_ERASE` is set but
  `FLAG_SKIP_ERASE` suppresses the erase, so `eprom_internal_write_init_body` reaches the blank check
  with a non-blank device — the identical code path a UV part takes, and repeatable because the part
  is electrically erasable.
- **Two "512"s, and they are not interchangeable here.** W27C512 (Winbond, `0xDA08`, EEPROM, 12 V)
  is the *rehearsal* part precisely because it is erasable. M27C512 / TMS27C512 (UV-EPROM, 13 V) are
  the *confirming* class precisely because they are not. Confirm by chip-ID, never by the name on the
  package.

</specifics>

<deferred>
## Deferred Ideas

- **Region-scoping `flash_intel.cpp:95` and `flash_nor_unlock.cpp:105`.** Out of scope per D-10. The
  defect is one `--skip-erase` deep on those parts (D-11), so this is a real follow-up, not a
  theoretical one. It needs its own bench budget.
- **Deleting those two write-init blank checks outright**, following the precedent
  `eeprom_28c.cpp:379` and `flash_5v_page.cpp:74` already set twice. Coherent, but a deletion nothing
  in BLANK-01..03 asks for, and it would need its own argument about whether those protocols' silicon
  really auto-erases.
- **Retiring `_apply_write_progress`'s total-discarding workaround.** D-06 makes the firmware's
  denominator agree with the host's bar for the first time, which removes the *reason* the workaround
  exists. Removing the workaround itself is a separate, host-only change with its own regression
  surface.
- **Whether the new field should also reach `CMD_READ`**, replacing the `memory-size` overload that
  `_setup_operation:495` currently uses for read narrowing. That overload is the thing D-08 declines
  to extend; unifying the two would be cleaner and is entirely out of scope here.
- **Re-anchoring a firmware size baseline.** There is no size gate in CI any more. Restoring one is
  its own decision, and memory records that re-anchoring `size_baseline.json` reddens four legs and
  needs a new fixture family.

### Reviewed Todos (not folded)

- **`.planning/todos/pending/2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md`**
  — scored highest on keyword match ("blank", "check", area `firmware`), and it does touch the
  blank-check path. Not folded: it is about `read` and standalone `blank-check`, operations that do
  not drive VPP. A *write* does drive VPP, so `eprom_check_vpp` running above this phase's blank
  check is correct and unchanged. It also carries `resolves_phase: 84`, long closed.

</deferred>

---

*Phase: 201-a-partial-write-is-gated-on-its-own-region*
*Context gathered: 2026-09-19*
