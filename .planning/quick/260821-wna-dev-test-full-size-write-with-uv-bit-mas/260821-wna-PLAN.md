---
quick_id: 260821-wna
phase: quick-260821-wna
plan: 01
type: execute
wave: 1
depends_on: []
commits_land_in: firestarter_app
files_modified:
  - firestarter_app/firestarter/chip_test.py
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/diagnostic_report.py
  - firestarter_app/tests/fake_chip.py
  - firestarter_app/tests/test_uv_mask.py
  - firestarter_app/tests/test_chip_test.py
  - firestarter_app/tests/test_chip_test_sdp_leg.py
  - firestarter_app/tests/test_dev_test_cmd.py
  - firestarter_app/tests/test_diagnostic_report.py
autonomous: true
requirements: [QUICK-260821-wna]

must_haves:
  truths:
    - "On a non-UV chip, `dev test`'s primary write/verify pass covers the FULL device: the pattern handed to `write_eprom` is `memory-size` bytes long, not 256 (D-D)."
    - "On a protocol-0x05 (flash4) chip the primary write/verify pass covers the device MINUS the first and last 16 KiB boot blocks, and the excluded region is named in the report with its reason; a flash4 part whose whole device is boot block (the three 32 KiB rows) falls back to the small fixed region with a stated reason and is never reported as a plain FAIL (D-D)."
    - "On a UV EPROM the write pattern is bit-masked by what is physically on the chip: the bytes handed to `write_eprom` are `C & D` where `C` is the slot's read-back content and `D` is the unchanged address-derived pattern, and the verify compares against that same masked image (D-A)."
    - "A UV slot is only selected when the masked write clears at least `_UV_MIN_CLEARED_BITS` bits AND the resulting image retains at least `_UV_MIN_RETAINED_BITS` one-bits; both thresholds are named module constants with the reasoning in a comment (D-B, Claude's discretion)."
    - "A slot holding 0x00 (or any slot whose masked image would be degenerate) can NEVER be reported as a write pass: `WriteTarget.__post_init__` REFUSES to construct such a target, and the write step has no path to OK without a constructed target -- it records SKIPPED with a reason naming saturation (D-B, the absent-chip false-green family)."
    - "When the current slot is saturated the selector advances to the next slot by READING candidate slots off the chip; no slot cursor is written to `~/.firestarter`, the config dir, or any file (D-B)."
    - "A UV EPROM that `check_eprom_blank` reports blank, on a run whose write scope permits it, gets a full-device masked write (which for a blank part equals the plain address-derived pattern) (D-C)."
    - "`derive_plan` stays a pure DB-only function: it decides the region and a new `Step.region_policy` and performs ZERO chip reads; the bit-mask is computed at execution time and reaches the verify step by being carried on the write step's `StepResult`, never re-derived (Claude's discretion, D-02/D-07 seam)."
    - "The write region start now reaches the wire: `write_eprom`/`verify_eprom` are called with `address_str` for any region whose start is non-zero, and the read-back used by the oracle is region-scoped via `address_str`/`size_str` and sliced at the region's ABSOLUTE offset."
    - "The SDP leg's six ops keep the small region they get today at the same write_scope -- they are not widened to the full device (D-D)."
    - "`_UV_WRITE_REGION_LENGTH` remains a module constant and remains the SLOT width; only the full-device paths take their width from `memory-size`, and only after `memory-size` passes a sanity check. The SC4 / D-01 comments are AMENDED in place to name the reversal and its bound, never deleted (D-E)."
    - "A single short line names the write coverage whenever the write was NOT the full device -- which slot, how many bits were clearable, or why nothing was written (D-F) -- rendered from the report's own single-source dict, adding no console call and no new helper to `dev_test`'s body."
    - "All three `dev test` console gates stay green with no change to their expected sets: `_HANDLER_FUNCTION_NAMES`, `_EXPECTED_DEV_TEST_REFERENCED_HELPERS` (still exactly six names) and the syrupy `dev --help` snapshot."
    - "`_ALWAYS_WRITES_PASS_COUNT` is still 6 and the test that DERIVES it from a live `derive_plan` still measures 6; the constant was not edited."
    - "`chip_database.json` is untouched and `tools/build_db.py` is untouched -- no DB field was added or hand-edited."
    - "The full `firestarter_app` suite, `ruff check`, `ruff format --check` and scoped `mypy` over the three touched modules are green locally on the devcontainer's Python 3.12; CI's Python 3.11 leg is NOT claimed, and the pre-existing `tools/check_mypy_watermark.py` numpy/mypy environment failure is NOT claimed as fixed."
  artifacts:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/fake_chip.py
    - firestarter_app/tests/test_uv_mask.py
    - firestarter_app/firestarter/diagnostic_report.py
  key_links:
    - "`derive_plan` -> `Step.write_region` + `Step.region_policy` -> `_dispatch_multi_run`'s execution-time resolver: the region is still decided once in the pure function; the MASK is execution-time only."
    - "write step's `StepResult.write_target` -> `run_plan`'s `WriteContext` -> the verify step's dispatch: the verify's region and expected image are the write's ACTUAL resolved ones, never a second derivation."
    - "`operator.read_eprom(..., address_str=, size_str=)` -> `eprom_operations._write_to_file`'s `file_handle.seek(ABSOLUTE address)` -> the engine's slice at `[start:start+length]`: a region read produces a hole-padded, memory-size-long file, so the slice is load-bearing and the test double must reproduce the seek."
    - "`_dispatch_sdp_leg`'s length gate (`len(actual) != region_length`) -> the now region-scoped read-back: with a whole-device read that gate can only pass against a region-sized test double, which is why it needs the region read."
    - "`chip_test.OP_WRITE`/`OP_WRITE_PARTIAL` + `StepResult.write_target` -> `DiagnosticReport._step_dict` / `render()` -> the tester's console line and the saved JSON provenance."
    - "`_resolve_write_scope`'s prompt -> the operator's consent -> which of the two D-C outcomes (full-device-if-blank vs slot-only) the run may take."
---

<objective>
Make `firestarter dev test` write the full device wherever that is physically possible,
and on UV-erasable EPROMs write into whatever cells are still writable -- bit-masking the
address-derived pattern by the chip's own content and advancing to the next slot when the
current one is saturated -- so a used UV part stays testable without a UV eraser.

Purpose: `dev test` writes 256 bytes to every chip in every mode today, so it never
validates a whole device, and its UV consent prompt asks about writing "the WHOLE device"
while both answers produce the same 256-byte window. This closes both.

Output: full-device write/verify on non-UV parts (boot blocks carved out on flash4),
execution-time bit-masked slot writes on UV parts with a structural vacuous-pass guard,
per-step write-coverage provenance in the report, and a truthful consent prompt.

Host-only. `firestarter_app/` only; no firmware change (full-device and arbitrary-region
writes already exist in the protocol). Commits land INSIDE `firestarter_app/` on branch
`quick-devtest-fullsize-write`.
</objective>

<execution_context>
@/workspaces/.claude/gsd-core/workflows/execute-plan.md
@/workspaces/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/quick/260821-wna-dev-test-full-size-write-with-uv-bit-mas/260821-wna-CONTEXT.md
@CLAUDE.md
@firestarter_app/CLAUDE.md
@firestarter_app/firestarter/chip_test.py
@firestarter_app/firestarter/cli_handlers.py
@firestarter_app/firestarter/diagnostic_report.py
</context>

<measured_findings>
## Measured at plan time (2026-08-21) — read this before writing code

The CONTEXT.md baseline table was re-measured against the live database by calling
`derive_plan` directly. **It is confirmed exactly, row for row**: M27C512 `(65280, 256)`
at both scopes, AT28C256 `(0, 256)` at full and `(32512, 256)` at partial, W27C512
`(0, 256)` at full and `(65280, 256)` at partial. No CONTEXT.md number is overridden.

Six further measurements were taken that CONTEXT.md does not state and that change how
this work must be built:

**M-1 — the region START never reaches the wire today.** `_dispatch_multi_run` calls
`operator.write_eprom(name, eprom_data, tmp_source_path)` positionally, with no
`address_str`. `_setup_operation` only sets the command's address key when an address
argument is supplied, so every write lands at address 0. The "top-anchored window" is
therefore **pattern content only, not placement**: on a UV part the bytes written at
address 0 are the bytes derived from address 0xFF00. The verify happens to agree because
`classify_fingerprint` compares over the common prefix. Making the region real means
threading `address_str` through the write, the verify and the read-back.

**M-2 — the read-back is a whole-device read.** Both `_dispatch_multi_run` and
`_dispatch_sdp_leg` call `operator.read_eprom(name, eprom_data, output_file=...)` with no
`address_str`/`size_str`. `_dispatch_sdp_leg` then gates on
`len(actual) != region_length`. On a real AT28C256 that is `32768 != 256`, i.e. BAD on
every leg step; it only passes because every current test double writes exactly the
region-sized payload. Region-scoping the read-back is a prerequisite for the masked
verify AND repairs that gate. Treat the repair as in scope and prove it with a test whose
double returns a full-size image.

**M-3 — `read_eprom` seeks to the ABSOLUTE address.** `_main_phase_read_data` passes the
absolute address to the callback and `_write_to_file` does `file_handle.seek(address)`.
A region read of `(0xFF00, 0x100)` therefore produces a **65536-byte hole-padded file**
whose real bytes sit at offset 0xFF00. The engine must slice `[start:start+length]` after
every region read, and the test double must reproduce the seek — a double that writes the
payload at offset 0 would make the slice look correct while testing nothing.

**M-4 — the general boot-block rule exists in host code, not in the DB.**
`eprom_operations.py` carries `_BOOT_BLOCK_SIZE = 0x4000` ("W29C040 §6.6 defines two 16K
boot blocks (first and last)") and `_FLASH4_PROTOCOL_ID = 5` with the note that boot-block
lockout is specific to protocol 0x05. So D-D's exclusion is **protocol-keyed, not
part-keyed**. Measured flash4 population: 27 rows, sizes `{32768: 3, 65536: 5, 131072: 7,
262144: 6, 524288: 6}` — for the three 32 KiB rows the two boot blocks cover the entire
device, so a full write is structurally impossible and those must fall back to the fixed
small region with a stated reason.

**M-5 — size and page-size facts.** 746 rows; largest device is 1 MiB (8 rows); every
size is a power of two >= 512. All 301 UV rows have `page-size` `None`, so a 256-byte
slot needs no page-alignment reasoning. Consequence to accept, not work around: a
full-device pass on a 512 KiB part is roughly seven device-length transfers at 250000 baud
(read x2, write x2, verify x2, read-back), i.e. minutes rather than seconds. That is what
D-D asks for; do not add a size cap to avoid it.

**M-6 — the pass count and the gates are unaffected.** `_ALWAYS_WRITES_PASS_COUNT` is
derived by `tests/test_dev_test_cmd.py` as `runs` (2) for the single write step plus one
per supported SDP-leg write op (4) = 6. This plan adds no write STEP, so the derivation
still measures 6 — do not edit the constant. `mypy firestarter/chip_test.py` is currently
clean; `mypy` over `cli_handlers.py`/`diagnostic_report.py` surfaces exactly one
PRE-EXISTING error, `firestarter/submit.py:695`, which is not ours to fix.
`python tools/check_mypy_watermark.py` cannot run in this devcontainer at all (numpy's
bundled stubs use a 3.12-only `type` statement; mypy exits 2) — verified pre-existing by
quick task 260821-spg's own summary. Do not claim that gate.
</measured_findings>

<constraints>
- `firestarter/data/chip_database.json` is GENERATED. Do not edit it. Do not add a DB
  field, and do not touch `tools/build_db.py` — nothing here needs a new DB field.
- Python 3.11 is the CI floor. No `match`, no PEP 695 `type` statements, no 3.12-only
  syntax. `from __future__ import annotations` is already in place.
- `tools/check_devtest_orchestrator.py` scans `chip_test.py` and `cli_handlers.py` and
  DENIES: VPP-set call names, a dict literal carrying >= 2 wire-protocol keys, `force=True`
  or a force flag literal, and broad exception handlers. New code must use narrow
  exception tuples only, and must not build any dict that looks like a wire command.
  Keeping the new pure-compute helpers INSIDE `chip_test.py` (rather than a new module) is
  deliberate: a new module would fall outside that checker's scan targets.
- Do not add a top-level key to `DiagnosticReport.to_dict()`; per-step keys inside
  `steps[]` only. `dedup_fingerprint` must keep reading only op/verdict/classification.
- `tools/check_diagnostic_report_claims.py` scans `diagnostic_report.py` string literals
  for claim language. Keep new literals descriptive and measurement-shaped.
- Never persist a slot cursor anywhere. The chip's content is the state.
- Never weaken an existing assertion to make it pass. Each RED test is a decision:
  retarget it at the new intended behaviour and say so, or delete it only when it tested
  behaviour that is deliberately gone.
</constraints>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Pure masking, slot and region arithmetic in chip_test.py</name>
  <files>firestarter_app/firestarter/chip_test.py, firestarter_app/tests/test_uv_mask.py</files>
  <behavior>
    - `mask_write_pattern(b"\xf0\x0f", b"\xff\xff")` returns `b"\xf0\x0f"`; masking is commutative-AND per byte; unequal lengths raise rather than silently truncate.
    - `bits_cleared_by(current, desired)` counts bits set in `current` and clear in `desired`; a fully saturated slot (`current` all 0x00) returns 0.
    - `bits_retained_by(current, desired)` counts bits set in BOTH; equals `popcount(mask_write_pattern(...))`.
    - `WriteTarget` construction REFUSES (raises `ValueError`) when: the pattern length disagrees with the region length; the pattern is all-0x00 or all-0xFF; the target is masked and `bits_cleared` is below `_UV_MIN_CLEARED_BITS`; the target is masked and `bits_retained` is below `_UV_MIN_RETAINED_BITS`.
    - Slot candidates for a 65536-byte device at a 256-byte slot width are 256 starts, ordered TOP-DOWN, first `65280`, last `0`.
    - `full_device_region` for a non-flash4 32768-byte chip is `(0, 32768)`; for a 524288-byte protocol-0x05 chip it is `(16384, 491520)`; for a 32768-byte protocol-0x05 chip it is a REFUSAL carrying a reason naming the boot blocks; for a `memory-size` that is absent, zero, not a multiple of the slot width, or above the sanity ceiling it is a REFUSAL carrying a reason.
    - Over any single 256-byte slot the address-derived pattern takes 256 distinct byte values, so a masked image can contain at most one 0xFF byte — an all-0xFF masked image is unreachable by construction, and the existing `_FF_RATIO_THRESHOLD` blank/contact detector therefore still fires on a genuine contact fault against a masked expectation.
  </behavior>
  <action>
Add the pure, bench-free arithmetic to `chip_test.py` (its own stated job: "pure compute
over host-side byte arrays"). No chip access, no operator calls, no imports beyond the
stdlib already present.

Constants, each with a comment carrying its reasoning:
- Keep `_UV_WRITE_REGION_LENGTH = 256` as-is and AMEND its existing comment: it is now the
  UV SLOT width per D-B, it is still an engine module constant never sourced from a DB
  field, and it is the bound D-E requires on the DB-derived-width reversal. Do not delete
  the SC4 wording; extend it.
- `_UV_MIN_CLEARED_BITS` and `_UV_MIN_RETAINED_BITS`, both per-SLOT (not per-byte) and
  both 64 of the 2048 bits in a slot. Justify in the comment: the verdict is per-slot so a
  per-byte rule would reject slots that are serviceable in aggregate; a virgin slot offers
  1024 clearable and 1024 retained bits (measured: the pattern's popcount over a 256-byte
  slot is exactly 1024), so 64 accepts a slot with only ~6% of its virgin headroom left
  while being far above anything a single-bit anomaly or a transport glitch could account
  for; and the retained floor is what makes an all-0x00 read-back unable to match the
  expected image.
- `_UV_PROBE_BLOCK_LENGTH = 4096` — how many bytes one probe read covers (16 slots per
  read), so a probe costs serial round trips proportional to blocks, not slots.
- `_FLASH4_BOOT_BLOCK_LENGTH = 0x4000` — a MIRROR of `eprom_operations._BOOT_BLOCK_SIZE`.
  Name that constant and `_FLASH4_PROTOCOL_ID` as the source of truth in the comment, and
  say why it is mirrored rather than imported: `chip_test.py` deliberately keeps no
  dependency on `eprom_operations.py` (the same reasoning `_diff_offsets` already records).
  Reuse the existing `_PROTOCOL_FLASH4` for the protocol id rather than adding a second.
- `_MAX_FULL_DEVICE_LENGTH = 1 << 24` — the sanity ceiling D-E demands before any
  DB-derived width is honoured. Comment: largest shipped device measured at 1 MiB across 8
  rows, so 16 MiB leaves room for a future part while refusing an absurd override value.

Region policy vocabulary (plain module-level strings, mirroring how this module already
carries its op vocabulary): `REGION_POLICY_FIXED`, `REGION_POLICY_FULL_DEVICE`,
`REGION_POLICY_UV_SLOT`.

Pure functions:
- `mask_write_pattern(current, desired)` — the D-A arithmetic, per-byte AND. Raise
  `ValueError` on a length disagreement; a silent truncation here is the empty-read-back
  trap in a new costume.
- `bits_cleared_by(current, desired)` and `bits_retained_by(current, desired)` — use
  `int.bit_count()` on a per-byte basis or a precomputed table; both are 3.11-safe.
- `uv_slot_starts(mem_size, slot_length)` — top-down ordered starts, empty when the device
  cannot hold one slot. Top-down is deliberate: it preserves the existing top-anchored
  convention and leaves the low address space (where a used EPROM's real payload usually
  lives) untouched longest.
- `full_device_region(mem_size, protocol)` — returns either a `(start, length)` tuple or a
  refusal reason string, never both. Order the checks: sanity-check `mem_size` first
  (positive, a multiple of `_UV_WRITE_REGION_LENGTH`, at or below
  `_MAX_FULL_DEVICE_LENGTH`), then apply the flash4 carve-out. Its docstring is the D-E
  disclosure point: state that this is the ONE place a write WIDTH is derived from a DB
  field, name SC4 and D-01, and state the bound — the slot width stays a module constant,
  and this width is honoured only after the sanity check above.
- `@dataclass(frozen=True) class WriteTarget` with `region`, `pattern`, `masked`,
  `bits_cleared`, `bits_retained`, `current_source`, and a `__post_init__` that enforces
  the four refusals in the behaviour block. This `__post_init__` IS the vacuous-pass
  guard: make its docstring say so, naming the absent-chip false-green trap as the family
  it belongs to. Every OK verdict downstream must be reachable only through an instance of
  this class.

Write `tests/test_uv_mask.py` covering every bullet in the behaviour block, one assertion
family per test, each named for the property it pins. Include a non-vacuity leg for the
`__post_init__` refusals: build a VALID target first in the same test so the refusal legs
cannot be passing because the constructor rejects everything.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app && python -m pytest tests/test_uv_mask.py -o addopts="" -q && ruff check firestarter/chip_test.py tests/test_uv_mask.py && ruff format --check firestarter/chip_test.py tests/test_uv_mask.py && mypy firestarter/chip_test.py</automated>
  </verify>
  <done>`tests/test_uv_mask.py` passes; `mypy firestarter/chip_test.py` reports no issues; `grep -n "SC4" firestarter/chip_test.py` still finds the amended UV-width comments (they were extended, not removed).</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: derive_plan decides the region POLICY, purely from the DB</name>
  <files>firestarter_app/firestarter/chip_test.py, firestarter_app/tests/test_chip_test.py</files>
  <behavior>
    - AT28C256 (EEPROM, 32768 B) at `write_scope="full"`: write and verify steps carry `region_policy` full-device and `write_region == (0, 32768)`.
    - W29C040 (Flash/EEPROM, protocol 5, 524288 B) at full: write/verify carry `(16384, 491520)` and a reason string naming the excluded boot blocks.
    - A protocol-5, 32768 B row at full: write/verify fall back to `region_policy` fixed with `(0, 256)` and a reason naming the boot blocks as covering the whole device.
    - M27C512 (UV, 65536 B) at full: `region_policy` uv-slot, `write_region == (65280, 256)` as the FIRST slot candidate; at partial: uv-slot with the same first candidate but the scope forbids the full-device outcome.
    - The six SDP-leg steps keep the region they get today at the same scope — `(0, 256)` at full for AT28C256 — and carry `region_policy` fixed. They are never widened to the full device.
    - `write_scope="none"` is unchanged: no write/verify steps, `write_region is None`.
    - A hostile DB dict (`memory-size` of 2**40, or 300, or missing) never widens the window: the write step falls back to `region_policy` fixed with the pre-existing small region and a stated reason.
    - `derive_plan` still performs zero chip access: the spy-db test that asserts only `get_eprom` and `convert_to_programmer` are called stays green.
  </behavior>
  <action>
Add `region_policy: str = REGION_POLICY_FIXED` to `Step` and extend its docstring: the
policy is set once by `derive_plan` alongside `write_region`; downstream code may only
READ it; the MASK it enables is execution-time and is never computed here.

In `derive_plan`, replace the current two-branch region computation with a policy
decision, keeping the existing shape (one small block, comments in place, nothing moved):

- `write_scope="none"` -> region `None`, policy fixed. Unchanged.
- UV part (either scope) -> policy uv-slot, region = the FIRST slot candidate from
  `uv_slot_starts(...)`, which for every shipped UV size is exactly today's top-anchored
  window, so the derived tuple for M27C512 is unchanged. Fall back to
  `_top_anchored_or_default(full)` with policy fixed when the device cannot hold a slot.
  The scope literal still matters and still reaches the executor: `partial` forbids the
  full-device outcome, `full` permits it (D-C).
- Non-UV at `full` -> ask `full_device_region(mem_size, protocol)`. A tuple gives policy
  full-device with that region. A refusal gives policy fixed with `_DEFAULT_REGION` and the
  refusal reason recorded on the step's `reason` field so it reaches the report (D-D's
  "stated, visible reason rather than a FAIL").
- Non-UV at `partial` -> unchanged: `_top_anchored_or_default(full)`, policy fixed.

Compute a SECOND region for the SDP leg, `leg_region`, by exactly today's formula
(`_DEFAULT_REGION` at full, `_top_anchored_or_default(full)` at partial) and use it for the
six leg steps. Comment why: D-D keeps the leg small because it proves the lock mechanism
rather than coverage, and AT28C256's plan carries eight region-sized write-shaped ops that
would otherwise become eight full-device transfers per run. Note in the same comment that
the leg's live path is always the full scope (SDP-ALLOW chips are all non-UV, D-17), so
`leg_region` is `(0, 256)` on every reachable run and the leg's wire behaviour is unchanged.

Amend, do not delete, the `Step.write_region` docstring's SC4 sentence and `derive_plan`'s
matching paragraph: state that the WIDTH now comes from `memory-size` for the full-device
policy only, name SC4 and D-01, state that this reverses that threat model on those paths
deliberately, and state the bound (slot width still a module constant; the DB width is
honoured only after `full_device_region`'s sanity check).

Update the existing region tests in `tests/test_chip_test.py` to the new intended
behaviour rather than deleting them: the pair around the full-vs-partial region
distinction, the partial-window and missing-`memory-size` fallback pair, and the
`_write_region_for` group including the hostile-`eprom_data` SC4 leg (that leg must stay —
it proves the executor still refuses to take a width from `eprom_data`). Add the new legs
from the behaviour block.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app && python -m pytest tests/test_chip_test.py tests/test_chip_test_blank_check_order.py -o addopts="" -q && python -m pytest tests/test_dev_test_cmd.py -o addopts="" -q -k "pass_count" && mypy firestarter/chip_test.py</automated>
  </verify>
  <done>`tests/test_chip_test.py` passes with the new policy legs; the live-derived write-pass count still measures 6 without `_ALWAYS_WRITES_PASS_COUNT` being edited; the spy-db no-chip-access test is still green.</done>
</task>

<task type="auto">
  <name>Task 3: A fake chip double that models UV physics and absolute-offset reads</name>
  <files>firestarter_app/tests/fake_chip.py, firestarter_app/tests/test_dev_test_cmd.py, firestarter_app/tests/test_chip_test_sdp_leg.py</files>
  <action>
Create `tests/fake_chip.py` — a helper module, not a test module (no `test_` prefix, so
pytest does not collect it). It backs every behavioural test in Task 4, and without it
those tests would be theatre.

`FakeChip` holds a `bytearray` of `memory_size` and a family mode:
- `uv=True` — a write ANDs into the existing content (`existing & incoming`), which is the
  physical fact D-A is built on. A fresh instance is all-0xFF.
- `uv=False` — a write overwrites.

It exposes operator-shaped methods matching the real `EpromOperator` signatures:
- `write_eprom(name, eprom_data, input_file_path, operation_flags=0, address_str=None, pulse_us=0)`
  — resolve the start with the same rule the host uses (hex when the string carries `0x`,
  else decimal; `None` means 0), apply the file's bytes from there, return the configured
  bool.
- `verify_eprom(name, eprom_data, input_file_path, operation_flags=0, address_str=None)` —
  compare the file against the chip at that start and return the comparison result, so a
  masked verify is a genuine oracle rather than a canned `True`.
- `read_eprom(name, eprom_data, output_file=None, operation_flags=0, address_str=None, size_str=None)`
  — **write the requested bytes at their ABSOLUTE offset**, reproducing
  `_write_to_file`'s `file_handle.seek(address)` (finding M-3). With no address/size, write
  the whole device. This is the single most important property of this double: a double
  that wrote the payload at offset 0 would make the engine's slice look correct while
  testing nothing. Put that sentence in the docstring.
- `check_eprom_blank`, `check_eprom_id`, `erase_eprom`, `sdp_lock`, `sdp_unlock` — driven
  off the real backing array where meaningful (`check_eprom_blank` returns whether the
  array is all-0xFF), configurable otherwise.

Provide constructors for the shapes Task 4 needs: a virgin UV chip; a UV chip with a
chosen slot pre-saturated (its content set to the bitwise complement of the pattern for
that slot, so `bits_cleared_by` there is high but the masked image is all-zero) ; a UV chip
with a chosen slot set to 0x00; a UV chip with arbitrary prior content; and a non-UV chip.
Also expose a call log so a test can assert which addresses and sizes were requested.

Then retrofit the existing doubles so the new `address_str` keyword does not TypeError:
`make_clean_operator` needs a `read_eprom` side effect that actually writes plausible
content at absolute offsets (a `Mock` returning `True` and writing no file makes every
probe read empty, which would turn every UV write into a saturation refusal), and the
inner `_write`/`_read` closures in `make_leaked_lock_operator` / `make_held_lock_operator`
and in `test_chip_test_sdp_leg.py`'s read-back doubles need the new keyword accepted and
the absolute-offset seek reproduced. Prefer delegating them to `FakeChip` over widening
each closure by hand where that does not disturb what the test is pinning.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app && python -c "
import sys; sys.path.insert(0, 'tests')
from fake_chip import FakeChip
from firestarter.chip_test import generate_pattern, mask_write_pattern
import tempfile, pathlib
c = FakeChip(memory_size=65536, uv=True)
d = pathlib.Path(tempfile.mkdtemp())
p = d / 'pat.bin'; p.write_bytes(generate_pattern(65280, 256))
assert c.write_eprom('M27C512', {}, str(p), address_str='0xFF00')
out = d / 'rb.bin'
assert c.read_eprom('M27C512', {}, output_file=str(out), address_str='0xFF00', size_str='0x100')
raw = out.read_bytes()
assert len(raw) == 65536, ('absolute-offset seek not reproduced', len(raw))
assert raw[65280:65536] == generate_pattern(65280, 256)
assert c.write_eprom('M27C512', {}, str(p), address_str='0xFF00')
assert c.read_eprom('M27C512', {}, output_file=str(out), address_str='0xFF00', size_str='0x100')
assert out.read_bytes()[65280:] == mask_write_pattern(generate_pattern(65280,256), generate_pattern(65280,256))
print('fake chip: absolute-offset read and UV AND-write OK')
" && python -m pytest tests/test_dev_test_cmd.py tests/test_chip_test_sdp_leg.py -o addopts="" -q && ruff check tests/fake_chip.py && ruff format --check tests/fake_chip.py</automated>
  </verify>
  <done>The inline check prints its OK line, proving the double writes region reads at their absolute offset and ANDs UV writes; the two retrofitted suites pass unchanged in intent.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 4: Execution-time mask, slot selection and region-scoped I/O</name>
  <files>firestarter_app/firestarter/chip_test.py, firestarter_app/tests/test_chip_test.py, firestarter_app/tests/test_chip_test_sdp_leg.py</files>
  <behavior>
    - Non-UV full-device: `write_eprom` receives a `memory-size`-long file, `address_str` is `None` because the region starts at 0, and the verify receives the same image.
    - flash4 carve-out: `write_eprom` receives `address_str` naming 0x4000 and a file of `memory-size - 32768` bytes.
    - UV virgin (blank-check OK, scope full): `write_eprom` receives a `memory-size`-long file equal to the plain address-derived pattern, and the step is OK.
    - UV virgin, scope partial: the write is a single top slot, not the whole device — the scope literal is honoured.
    - UV used chip: the file `write_eprom` receives equals `mask_write_pattern(slot_content, generate_pattern(slot_start, slot_length))`, and the read-back the fingerprint is built from is the region slice, not the device prefix.
    - Slot advance: on a chip whose top slot was already written with this pattern, the selector skips it and targets the next slot down; `address_str` names that slot.
    - Vacuous pass: on a chip whose top slot is 0x00, that slot is never targeted. On a chip where EVERY slot is saturated, the write step verdict is SKIPPED with a reason naming saturation and the need for a UV erase, the verify step is SKIPPED too, `write_eprom` is never called, and no step reports OK for the write.
    - No file is created or written outside the temp dir the engine already uses: a slot cursor is never persisted (assert nothing new appears under a patched config dir).
    - The SDP leg's length gate passes against a double that returns a FULL-SIZE image, because the read-back is now region-scoped and sliced.
    - Run-fatal exceptions raised during a probe read still escape `run_plan` (the existing precedence matrix is unchanged), and a transport-level probe failure degrades only the write step.
  </behavior>
  <action>
Wire the execution half. Keep `run_plan`'s flat shape; add no new exception-handling
policy — put the resolution INSIDE the existing dispatch try/except so
`_run_step_untimed`'s already-ordered clauses cover it and the precedence matrix test
stays meaningful.

New execution helpers in `chip_test.py`:
- `_address_arg(start)` — returns `None` when the start is 0, else a `0x`-prefixed hex
  string. The `None` case is load-bearing: it keeps every region-at-zero call byte-identical
  to today's wire behaviour, since `_setup_operation` only sets the command's address key
  when an argument is supplied. Say that in the docstring.
- `_size_arg(length)` — the matching `0x`-prefixed size string for a read.
- `_read_region(operator, name, eprom_data, start, length)` — one region read into a temp
  dir, then `[start:start+length]` off the file (finding M-3), returning `b""` on any
  `OSError` or short result. This is the ONE place the slice lives; every read-back goes
  through it.
- `_resolve_write_target(name, step, eprom_data, operator, *, chip_is_blank)` — the
  execution-time resolver, and the only place a mask is computed:
  * fixed policy -> an unmasked `WriteTarget` over `step.write_region`.
  * full-device policy -> an unmasked `WriteTarget` over `step.write_region`.
  * uv-slot policy, chip reported blank AND the plan's scope permits the full-device
    outcome -> a masked `WriteTarget` over the full-device region with the mask taken as
    all-0xFF, `current_source` recording that the image came from the blank-check rather
    than a probe read (D-C). Derive the bit counts from the pattern itself; do not read the
    device again.
    Carry the scope decision from `derive_plan` onto the step so this branch needs no new
    parameter — a boolean field on `Step` set only by `derive_plan` (e.g. whether the
    full-device outcome is permitted) is the cleanest form; keep it read-only downstream.
  * uv-slot policy otherwise -> probe. Walk `uv_slot_starts` in `_UV_PROBE_BLOCK_LENGTH`
    -sized reads, evaluate each slot inside the block with `bits_cleared_by` /
    `bits_retained_by`, and take the FIRST slot whose counts satisfy both thresholds.
    Return the masked target, or a refusal string when the walk exhausts the device. Never
    write a cursor anywhere; the probe reads ARE the state lookup.
- `WriteContext` — a small mutable dataclass carrying `chip_is_blank: bool | None`,
  `target: WriteTarget | None` and `refusal: str`, threaded as ONE keyword-only parameter
  (default `None`) through `_run_step`, `_run_step_untimed`, `_dispatch_step` and
  `_dispatch_multi_run`. Do not thread it into `_dispatch_sdp` or `_dispatch_sdp_leg`:
  those keep `_write_region_for` and the fixed leg region.

In `run_plan`: create one `WriteContext`; after a blank-check step record its verdict on
it; pass it to every `_run_step` call; after a write step copy the result's resolved target
(and, when there is none, the refusal reason) onto it so the verify step inherits the
write's ACTUAL region and expected image. Comment that this is the D-07 seam moved to
execution time: the region is still `derive_plan`'s, the mask is not, and the verify never
re-derives either.

In `_dispatch_multi_run`:
- add `write_target` to `StepResult` (additive field, default `None`) and set it on the
  write step's result.
- for a write op, resolve the target (or return SKIPPED with the refusal reason — the
  saturated-chip path, which must never be OK).
- for a verify op with a non-fixed policy, use the inherited target; when there is none,
  return SKIPPED naming the write's refusal.
- use `target.pattern` for the temp source file and `target.region` for the fingerprint's
  `addr_base`, and pass `address_str=_address_arg(start)` to `write_eprom` and
  `verify_eprom`.
- replace the whole-device read-back with `_read_region(...)` over the target's region.
- keep the verdict model exactly as it is (per-run operator bool, marginal on
  disagreement, fingerprint as attached evidence). The vacuous-pass guard is structural —
  it lives in `WriteTarget.__post_init__` and in the SKIPPED refusal path — not in a new
  verdict rule.

In `_dispatch_sdp_leg`: replace its whole-device read-back with `_read_region(...)` over
the leg region and pass `address_str=_address_arg(start)` on its `write_eprom` call. Extend
the length-gate comment: the gate was previously satisfiable only by a region-sized double
(finding M-2), and a region-scoped read is what makes it a real gate on hardware.

Add the behavioural tests against `FakeChip` through `run_plan` (not through the CLI) so
each property is pinned at the engine seam, plus the two `_dispatch_sdp_leg` legs.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app && python -m pytest tests/test_chip_test.py tests/test_chip_test_sdp_leg.py tests/test_chip_test_timing.py tests/test_uv_mask.py -o addopts="" -q && mypy firestarter/chip_test.py && ruff check firestarter/chip_test.py tests/ && ruff format --check firestarter/chip_test.py tests/</automated>
  </verify>
  <done>Every behaviour bullet has a named passing test; the saturated-chip case proves `write_eprom` was never called and no step reported OK for the write; the SDP-leg length gate passes against a full-size read-back double; `mypy firestarter/chip_test.py` is clean.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 5: Write-coverage provenance in the report and the one-line warning</name>
  <files>firestarter_app/firestarter/diagnostic_report.py, firestarter_app/tests/test_diagnostic_report.py, firestarter_app/tests/test_dev_test_cmd.py</files>
  <behavior>
    - `to_dict()["steps"][i]` for a write or verify step carries additive keys naming the region start, the region length, the bits cleared, the bits retained and the source of the current image; all are `None` on a step with no resolved target.
    - `to_dict()`'s TOP-LEVEL key set is unchanged, and `dedup_fingerprint` is byte-identical for two runs that differ only in which slot was chosen.
    - `SCHEMA_VERSION` is bumped one minor step and the single test that pins the literal version is updated to the new value, keeping the imported-constant assertion beside it.
    - `render()` emits ONE extra row, only when the write did not cover the full device: naming the slot range and the clearable-bit count for a slot write, the excluded range and reason for a carved-out write, or the saturation reason when nothing was written. On a full-device write no extra row appears.
    - A CLI-level run over a used UV chip writes a saved JSON whose write step carries the slot region, and the console output contains the coverage line.
  </behavior>
  <action>
Extend `_step_dict` with the additive per-step keys read off `StepResult.write_target`
(`diagnostic_report.py` already imports from `chip_test`, so import the two write op
constants too). Additive INSIDE `steps[]` only — do not add a top-level key, because the
top-level shape is pinned elsewhere and `parse_devtest_issue.py` consumes it.

Bump `SCHEMA_VERSION` by one minor step and update the single version-pinning test,
including its docstring line naming what the new version added, matching how the 1.5 bump
recorded `duration_s`. Leave every other site importing the constant.

Add the coverage row to `render()`, derived from the same `to_dict()` output `render`
already consumes — never a second field list, and never a re-parse of the JSON string.
Keep it to one row with a short value. Keep the literals measurement-shaped: name the
region, the byte count and the bit count, or the reason nothing was written. Do not use
claim language (the claims checker scans this file's literals).

State in a comment beside the new keys the deliberate residual: `dedup_fingerprint`
intentionally does NOT distinguish a full-device UV run from a slot run, because the
chosen slot is volatile by design — keying it into the hash would make every UV run its
own group and destroy the N>=2 agreement `count_agreeing` depends on. The coverage is
recorded as provenance instead.

Add the CLI-level leg to `tests/test_dev_test_cmd.py` driving a used UV `FakeChip` through
the real `dev test` command and asserting both surfaces (saved JSON and console).
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app && python -m pytest tests/test_diagnostic_report.py tests/test_dev_test_cmd.py tests/test_parse_devtest_issue.py tests/test_submit.py tests/test_provenance.py tests/test_check_diagnostic_report_claims.py -o addopts="" -q && ! mypy firestarter/chip_test.py firestarter/diagnostic_report.py firestarter/cli_handlers.py 2>&1 | grep -E "^firestarter/(chip_test|diagnostic_report|cli_handlers)\.py:"</automated>
  </verify>
  <done>The report suites pass; `python tools/check_diagnostic_report_claims.py` exits 0 via its pytest wrapper; the schema-version pin test names the new version; scoped mypy reports nothing against the three touched modules (the pre-existing `submit.py:695` error is untouched and unclaimed).</done>
</task>

<task type="auto">
  <name>Task 6: Truthful UV consent prompt, then the whole gate set</name>
  <files>firestarter_app/firestarter/cli_handlers.py, firestarter_app/tests/test_dev_test_cmd.py</files>
  <action>
Rewrite `_resolve_write_scope`'s UV prompt so it describes what the two answers now
actually do (D-C). The scope literal's meaning has changed from "how wide is the window" to
"what is the consent ceiling", so say so plainly and briefly: yes permits the whole device
to be written when the chip is blank and otherwise writes one 256-byte slot; no writes one
256-byte slot only. Keep the existing framing that neither answer is read-only or
non-destructive, and keep the default-to-decline behaviour and the injected `confirm_fn`
seam. Update the three numbered branch descriptions in the docstring to match, and update
the `ALWAYS WRITES` comment block above `dev_test` (the design-history comments quick task
260821-spg moved out of the docstring) so it no longer describes both UV answers as the
same 256-byte window.

Do NOT change `dev_test`'s body or its docstring. That is what keeps all three console
gates untouched: `_HANDLER_FUNCTION_NAMES` and `_EXPECTED_DEV_TEST_REFERENCED_HELPERS` both
stay at their current contents (six referenced helpers), and the syrupy `dev --help`
snapshot does not move. Prove it rather than assert it — the verify command below runs all
three.

Add a test asserting the prompt text mentions both outcomes (blank-device and slot) so a
future edit cannot silently make it inert again, and keep the existing branch tests
(no-TTY, yes, no) green.

Then run the whole gate set and record results honestly in the summary: full suite, ruff
lint, ruff format, scoped mypy, and the tool gates via their pytest wrappers. Record two
NON-claims explicitly: `python tools/check_mypy_watermark.py` cannot run in this
devcontainer (pre-existing numpy/mypy incompatibility, verified before this task started),
and CI's Python 3.11 leg is unproven locally. Also record the expected runtime
consequence of D-D for a bench operator: a full-device pass on a large part is now several
device-length transfers at 250000 baud, i.e. minutes rather than seconds.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app && python -m pytest tests/ -o addopts="" -q && ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/ && python -m pytest tests/test_check_devtest_orchestrator.py tests/test_characterization.py tests/test_check_diagnostic_report_claims.py -o addopts="" -q && git -C /workspaces/firestarter_app diff --stat beta -- firestarter/data/chip_database.json tools/build_db.py | grep -c . | grep -qx 0</automated>
  </verify>
  <done>Full suite green; ruff lint and format clean; the three console gates green with their expected sets unedited; the final command confirms neither the generated database nor the generator was modified.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| `chip_database.json` / `~/.firestarter/database.json` -> host | A user-override DB entry can supply a hostile `memory-size`, which this task newly lets influence a write WIDTH |
| host -> silicon | A write region computed wrongly destroys cells that cannot be recovered without a UV lamp |
| chip read-back -> verdict | A degenerate read-back (all-0x00 / all-0xFF) can launder a dead bus or an absent chip into a pass |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-wna-01 | Tampering | `full_device_region` DB-derived width (D-E reversal) | high | mitigate | Sanity-check `memory-size` before honouring it: positive, a multiple of the slot width, at or below `_MAX_FULL_DEVICE_LENGTH`; a failing value falls back to the pre-existing fixed region with a stated reason. The slot width stays a module constant. Tested with a 2**40 override. |
| T-wna-02 | Tampering | `_write_region_for` / `eprom_data` | high | mitigate | Keep the existing SC4 leg proving the executor refuses to take a width from `eprom_data`; the executor reads only `Step.write_region`, which `derive_plan` set. |
| T-wna-03 | Spoofing | degenerate read-back as a pass | critical | mitigate | `WriteTarget.__post_init__` refuses an all-0x00 / all-0xFF expected image and refuses a masked target below either bit threshold, so no OK verdict is reachable for a saturated slot; the saturated path is SKIPPED with a stated reason. Tested on a 0x00 slot and on an all-saturated chip. |
| T-wna-04 | Denial of service | full-device write on a 1 MiB part | medium | accept | D-D mandates full-device coverage; the cost is bounded (largest shipped device is 1 MiB) and is now visible per step via the existing `duration_s` field and the new coverage row. No size cap is added, because a cap would be a scope reduction of a locked decision. |
| T-wna-05 | Information disclosure | new report keys / console row | low | mitigate | The added values are addresses and bit counts derived from the host's own pattern; no tester-supplied identity or path text is added, and `dedup_fingerprint` still excludes every volatile field. |
| T-wna-06 | Tampering | UV write lands at the wrong address | critical | mitigate | `_address_arg` returns `None` for a zero start so every existing region-at-zero call is byte-identical on the wire; a non-zero start is passed explicitly and asserted in tests against a `FakeChip` that models the real absolute-offset semantics. |
| T-wna-SC | Tampering | npm/pip/cargo installs | high | mitigate | No package is installed by this task; no dependency is added to `pyproject.toml`. The legitimacy gate is not engaged. |
</threat_model>

<verification>
1. `cd /workspaces/firestarter_app && python -m pytest tests/ -o addopts="" -q` — full suite green.
2. `cd /workspaces/firestarter_app && ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/` — clean.
3. `cd /workspaces/firestarter_app && ! mypy firestarter/chip_test.py firestarter/diagnostic_report.py firestarter/cli_handlers.py 2>&1 | grep -E "^firestarter/(chip_test|diagnostic_report|cli_handlers)\.py:"` — no error attributed to a touched module.
4. `cd /workspaces/firestarter_app && python -m pytest tests/test_check_devtest_orchestrator.py tests/test_characterization.py tests/test_check_diagnostic_report_claims.py -o addopts="" -q` — the three console/claim gates.
5. `cd /workspaces/firestarter_app && python -m pytest tests/test_dev_test_cmd.py -o addopts="" -q -k "pass_count"` — the live-derived write-pass count still measures 6.
6. `cd /workspaces/firestarter_app && git status --short firestarter/data/chip_database.json tools/build_db.py` — empty output.
7. `cd /workspaces/firestarter_app && python -c "
from firestarter.database import EpromDatabase
from firestarter.chip_test import derive_plan
db = EpromDatabase()
for chip in ['M27C512','AT28C256','W27C512','W29C040']:
    for scope in ['full','partial']:
        p = derive_plan(chip, db, write_scope=scope)
        rows = [(s.op, s.region_policy, s.write_region) for s in p.steps if s.write_region is not None]
        print(chip, scope, p.is_uv, rows)
"` — the post-change region/policy table, to be pasted into the SUMMARY beside the plan-time baseline so the change is legible.

NOT verified and not to be claimed: `python tools/check_mypy_watermark.py` (pre-existing
numpy/mypy incompatibility in this devcontainer — mypy exits 2 before checking anything);
CI's Python 3.11 leg; any bench/hardware behaviour. No silicon is touched by this task.
</verification>

<success_criteria>
- A non-UV chip's primary write/verify pass covers the full device, minus the two 16 KiB
  boot blocks on protocol 0x05, with the exclusion and its reason visible in the report.
- A UV chip's write is `C & D` over a slot the engine picked by reading the chip, and a
  blank UV chip on a consenting run gets the full-device pattern.
- A saturated or 0x00 slot cannot be reported as a pass by any path, and the run says so.
- No slot cursor exists on disk.
- `derive_plan` still reads only the DB; the mask is execution-time only.
- The three `dev test` console gates and `_ALWAYS_WRITES_PASS_COUNT` are untouched.
- `chip_database.json` and `tools/build_db.py` are untouched.
- Full suite, ruff and scoped mypy green locally; the two named non-claims recorded.
</success_criteria>

<output>
Create `.planning/quick/260821-wna-dev-test-full-size-write-with-uv-bit-mas/260821-wna-SUMMARY.md` when done.

Record in it: the post-change region/policy table from verification step 7 beside the
plan-time baseline; the disposition of every test that went RED (retargeted / deleted with
reason / unchanged); the chosen threshold values and why; the two non-claims (mypy
watermark gate, CI 3.11); and the bench-runtime consequence of full-device coverage.
</output>
