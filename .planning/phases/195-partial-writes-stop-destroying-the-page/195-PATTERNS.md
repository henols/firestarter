# Phase 195: Partial Writes Stop Destroying the Page — Pattern Map

**Mapped:** 2026-09-16
**Files analyzed:** 12 (7 MODIFY, 5 CREATE; 2 of the 12 are generated artefacts, never hand-edited)
**Analogs found:** 10 / 12 (2 need no analog — they are regenerated)
**Sweep tool:** `/usr/bin/grep` only (the devcontainer `grep` is ugrep and honours `.gitignore`).
**Tracked-source gate:** every analog path below was confirmed with `git ls-files` in its own
repository (meta `/workspaces`, `firestarter_app`, `firestarter_fw`). No gitignored mirror path appears here.

**Scope note.** The file list is derived from RESEARCH.md §3b/§4/§5/§6/§7 and §11, under the research's
own primary recommendation (shape (b): host pre-flight refusal + firmware backstop). If the planner
takes hybrid **c1** (host-side alignment) as well, it adds a strand inside `eprom_operations.py` only —
no new analog is needed, see §c1 note at the end of the Pattern Assignments.

---

## File Classification

Repo column: `M` = meta (`/workspaces`), `A` = `firestarter_app`, `F` = `firestarter_fw`.

| Repo | New/Modified File | Action | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|---|---|
| M | `tools/catalog/messages.toml` | MODIFY | config (codegen input) | transform | the `MSG_ERR_FL4_PAGE_SIZE` stanza at `:700-706` | exact |
| M | `.planning/v1.39/195-w29c020-partial-write-bench-transcript.md` | CREATE | doc artefact | batch record | `.planning/v1.39/194-w29c020-bench-transcript.md` | exact |
| M | `VALIDATED-EPROMS.md` | REGENERATE | generated ledger | batch | **none — generated** by `.claude/skills/devtest-triage/scripts/eprom_ledger.py` | n/a |
| A | `firestarter/page_size_gate.py` (or a sibling `page_align_gate.py`) | MODIFY-or-CREATE | utility (pure predicate) | request-response | `page_size_gate.require_page_size` `:63-88` | exact (same module) |
| A | `firestarter/exceptions.py` | MODIFY | model (exception) | request-response | `PageSizeUnavailableError` `:92-102` | exact |
| A | `firestarter/cli_handlers.py` | MODIFY | controller (CLI) | request-response | call site `:764`; `map_typed_errors` arm `:218-219` | exact |
| A | `firestarter/eprom_operations.py` | MODIFY | service (operator) | request-response | `require_page_size(...)` call at `:2009`; `parse_address` use at `:481-486` | exact |
| A | `tests/test_page_size_alignment_refusal.py` | CREATE | test (host pytest) | request-response | `tests/test_page_size_write_refusal.py` (9 tests, 4 properties) | exact |
| F | `src/proms/flash_5v_page.cpp` | MODIFY | handler (prom) | streaming (byte loop) | its own refusal block `:80-86` | exact (same file) |
| F | `include/messages.h` | REGENERATE | build output | — | **none — generated** | n/a |
| F | `test/native/avr/test_val_5v_page/test_val_5v_page.cpp` | MODIFY | test (native Unity) | streaming | its own `test_5v_page_write_execute_refuses_with_no_page_size` `:342-361` + `drive_page_boundary_case` `:363-377` | exact |
| M | `.planning/todos/pending/error-message-band-a0-bf-exhausted.md` (+ optionally `host-page-size-gate-accepts-invalid-values.md`) | RESOLVE/MOVE | process artefact | — | the project's own `todos/pending` → resolved convention | n/a |

**Test-tree attribution.** The firmware test file is in the PlatformIO `test/native/avr/` tree, run by
CI as `pio test -e native` and `pio test -e native_nodevtools`. `test_val_5v_page` is already registered
in both envs, so **no `platformio.ini` change is required**. The separate `firestarter_fw/tests/*.py`
scanner tree holds no file this phase touches — but see the two fail-open scanners in §Shared Patterns.

---

## Pattern Assignments

### `firestarter_app/firestarter/page_size_gate.py` (utility, pure predicate)

**Analog: the module itself.** This is the one-phase-old sibling gate and it is a drop-in template —
the new predicate is `S % P == 0 && L % P == 0` in the same shape, at the same layer.

**Guard shape to copy verbatim** (`page_size_gate.py:80-88`):

```python
    if operation not in _WRITE_OPERATIONS:
        return
    if not requires_page_size(programmer_data):
        return
    page_size = (programmer_data or {}).get(JSON_KEY_PAGE_SIZE)
    if not page_size:
        raise PageSizeUnavailableError(
            _REFUSAL_FORMAT.format(chip_name=chip_name.upper())
        )
```

Three properties to carry across:

1. **Two early returns before the predicate** — non-write operations and non-`0x05` parts return first,
   so the gate can never widen. `_WRITE_OPERATIONS = frozenset({"write"})` (`:40`).
2. **The protocol id is imported, never re-declared** (`:38`):
   `from firestarter.flash4_erase_gate import FLASH4_PROTOCOL_ID`. Do the same; a flag-based predicate
   silently widens the refusal.
3. **Module-level refusal format string** (`:42-46`) rendered with `chip_name.upper()`. The new message
   should likewise name the chip and state both offending values (start, length, page size).

**Fail-closed polarity is stated in the module docstring (`:21-25`)** and must be preserved: an
unreadable input file, an unparseable `-a`, or an absent page size refuses. Docstrings are legal here
(the citation gate never scans them, and CLAUDE.md's no-comments rule does not cover them) — **this
module's explanatory prose is a docstring, not a comment; do not add a `#` comment anywhere.**

**Placement decision the planner owns:** extend `page_size_gate.py` with a second public function
(`require_page_alignment(...)`) or add a sibling module. Extending is cheaper and keeps `_WRITE_OPERATIONS`
and `FLASH4_PROTOCOL_ID` single-sourced; the module's own name is the only argument against it.

---

### `firestarter_app/firestarter/exceptions.py` (model, request-response)

**Analog:** `PageSizeUnavailableError`, `exceptions.py:92-102` — same base class, same pre-connect
contract, docstring already states the property this phase wants:

```python
class PageSizeUnavailableError(EpromOperationError):
    """Raised when a protocol 0x05 write targets a chip with no recorded page size.

    Fired by page_size_gate.require_page_size before any wire dict reaches the
    transport and before any serial byte is emitted — the host will not drive
    hardware for a protocol 0x05 chip whose page size is unknown. A guessed
    page size on this protocol destroys data in both directions, so absent
    evidence is never treated as safe.
    """

    pass
```

Subclass `EpromOperationError` the same way. **⚠ Subclassing `EpromOperationError` is only half the
job** — see the next section's ordering constraint.

---

### `firestarter_app/firestarter/cli_handlers.py` (controller, request-response)

**Analog 1 — the `map_typed_errors` arm and its ordering constraint** (`cli_handlers.py:218-221`,
read this session, verbatim):

```python
        except PageSizeUnavailableError as e:
            raise click.ClickException(str(e)) from e
        except EpromOperationError as e:
            raise click.ClickException(f"Programmer error: {e}") from e
```

A new `EpromOperationError` subclass **must get its own arm above the generic one** or its message is
prefixed with `"Programmer error: "`. Pinned by the existing
`test_page_size_unavailable_renders_verbatim_with_no_generic_prefix`.

**Analog 2 — the call site** (`cli_handlers.py:762-766`, verbatim; the alignment guard goes immediately
after `require_page_size`, still before `write_eprom`, which is the first line touching serial):

```python
    if not jp5_gate.confirm_or_refuse(eprom, eprom_data.get("bus-config"), "write"):
        sys.exit(1)
    page_size_gate.require_page_size(eprom, eprom_data, "write")

    ok = app.eprom_operator.write_eprom(
```

`eprom_data` is the fully resolved wire dict; `input_file` and `address` are in scope at this site.

---

### `firestarter_app/firestarter/eprom_operations.py` (service, request-response)

**Analog 1 — the operator-layer call site** (`eprom_operations.py:2003-2011`, verbatim). This is the
layer that also covers `dev test` and every non-CLI caller; the port opens **inside**
`_operation_context`, not before it:

```python
        require_acknowledged(
            eprom_name,
            eprom_data_dict.get("bus-config"),
            "write",
            pin1_hazard_acknowledged,
        )
        require_page_size(eprom_name, eprom_data_dict, "write")

        with self._operation_context(
```

Both guards are called bare (module-level import, not `module.fn`) at this layer, and prefixed
(`page_size_gate.require_page_size`) at the CLI layer. Match whichever layer you are editing.

**Analog 2 — the address parser to reuse** (`eprom_operations.py:481-483`, inside `_setup_operation`):

```python
                addr = parse_address(address) or 0
                command_dict["address"] = addr
```

The payload length is `os.path.getsize(input_file_path)`; the start is `parse_address(address_str) or 0`.
**Note the divergence to carry:** `_setup_operation` *logs and returns* on `ValueError`
(`:484-486`). The new guard must **raise**, not return — fail-closed, matching `require_page_size`.

---

### `firestarter_app/tests/test_page_size_alignment_refusal.py` (test) — CREATE

**Analog:** `firestarter_app/tests/test_page_size_write_refusal.py` (176 lines, 9 tests). Copy its
whole structure; it is the sibling gate's test module.

**Module-docstring four-property contract to mirror** (`:11-24` — properties, not prose):

1. Refusal — `write_eprom` raises, naming the chip, **before `_operation_context` is entered**.
2. Pass-through — an aligned write reaches `_operation_context` (proves it is not a blanket refusal).
3. No-op — another algorithm, and a non-write operation, both pass without raising.
4. Rendering — surfaces through `map_typed_errors` verbatim, **no `"Programmer error:"` prefix**.

**Fixture pattern — build wire dicts from the live database, do not fabricate them** (`:47-64`):

```python
def _protocol_0x05_data_missing_page_size() -> dict:
    """A real, resolved wire dict for a protocol 0x05 part, with `page-size`
    stripped ..."""
    db = EpromDatabase(skip_local_override=True)
    eprom_data = dict(db.convert_to_programmer(db.get_eprom("W29C020")))
    eprom_data.pop("page-size", None)
    return eprom_data
```

Use `W29C020` (P=128) for the `0x05` cases and `W27C512` for the other-algorithm case, exactly as this
module does.

**The load-bearing assertion pattern** (`:73-79`) — `ctx_mock.assert_not_called()` is what proves
"no serial byte was emitted":

```python
    with patch.object(EpromOperator, "_operation_context") as ctx_mock:
        with pytest.raises(PageSizeUnavailableError) as exc_info:
            operator.write_eprom("W29C020", eprom_data, "in.bin")
        ctx_mock.assert_not_called()

    assert "W29C020" in str(exc_info.value)
```

**Pass-through arm mock shape** (`:95-100`) — needed because the aligned case must actually proceed:

```python
        ctx_mock.return_value.__enter__ = Mock(return_value=(None, 0, "write"))
        ctx_mock.return_value.__exit__ = Mock(return_value=False)
```

**⚠ New requirement this analog does not cover:** the alignment predicate reads the payload **length**,
so the test needs a real file on disk (`tmp_path`) rather than the string `"in.bin"` these tests pass.
Size the fixtures: `128` bytes (aligned), `64` bytes (non-multiple length), and an aligned length at an
unaligned `address_str="0x40"`.

---

### `firestarter_fw/src/proms/flash_5v_page.cpp` (handler, streaming)

**Analog: the file's own Phase 194 refusal block** (`flash_5v_page.cpp:80-86`, verbatim). Both the
shape and the position are the pattern — the guard sits **before the loop**, so zero register writes
have happened when it returns:

```c
void flash_5v_page_write_execute(firestarter_handle_t* handle) {
    uint32_t page_mask;
    if (!flash_5v_page_mask(handle->page_size, &page_mask)) {
        LOG_ERROR_ID_U16(MSG_ERR_FL4_PAGE_SIZE, handle->page_size);
        handle->response_code = RESPONSE_CODE_ERROR;
        return;
    }
```

Three elements to copy exactly: `LOG_ERROR_ID_*(id, value)` → `handle->response_code =
RESPONSE_CODE_ERROR;` → `return;`. Put the new alignment guard **immediately after this block**, using
the `page_mask` it just resolved:
`((handle->address & page_mask) != 0 || (handle->data_size & page_mask) != 0)`.

**Macro selection analog** — the emit macro must match the catalog param width. In-file precedents:
`LOG_ERROR_ID_U16` at `:83` (u16 param) and `LOG_ERROR_ID_BYTES(MSG_ERR_FL4_VERIFY_TIMEOUT, _b, 5)` at
`:132` with the manual big-endian byte pack at `:126-131` — that is the in-file pattern if the new
message carries both the address and the size.

**The two clauses to remove or neutralise are `|| is_first_byte` (`:98`) and `|| is_last_byte` (`:106`)** —
but note the refusal shape may leave them in place, since a page-aligned chunk makes them redundant
rather than wrong. That is a plan decision, not a pattern one.

**⚠ No comment.** The block comment at `:91-95` documents the SDP call, not the defect. If the guard
makes any existing comment false, **delete the false clause; write no replacement** (CLAUDE.md, hard
rule). Rationale goes in `195-SUMMARY.md` or the commit message.

**⚠ `delayMicroseconds` gate.** `firestarter_fw/tests/test_write_path_source_contract_v131.py` scans
`src include lib platform` and requires every `delayMicroseconds(...)` argument to be a literal or a
clamped value. `:118` is `delayMicroseconds(10)` today. Any new non-literal delay trips that gate.

---

### `tools/catalog/messages.toml` (config, codegen input) — meta repo only

**Analog:** the `MSG_ERR_FL4_PAGE_SIZE` stanza, `tools/catalog/messages.toml:700-706` — same handler
prefix, same `wire_format`, single scalar param, minted by the sibling phase:

```toml
[[messages]]
id          = 0xBF
name        = "MSG_ERR_FL4_PAGE_SIZE"
severity    = "ERROR"
format      = "page size %u rejected -- write refused"
params      = [{ type = "u16", render = "dec" }]
wire_format = "id_frame"
```

**For a two-param message**, the analog one stanza earlier is `MSG_ERR_ENERGY_CAP` at `:690-698` —
the list form with `render = "hex_addr"` on a `u24` address:

```toml
params = [
    { type = "u24", render = "hex_addr" },
    { type = "u8" },
]
```

**Insertion position:** immediately after the `0xBF` stanza (`:700-706`) and before the
`# ---` DATA banner at `:708-710`. The file header's rule: *"DO NOT REORDER ENTRIES. Codegen sorts by
id ascending; the source file order is preserved for human-edit diff readability."*

**Sync pattern — the whole of it, run from `/workspaces`:**

```bash
python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check
bash tools/catalog/sync_to_subrepos.sh
git -C firestarter_fw status --porcelain    # expect: include/messages.h
git -C firestarter_app status --porcelain   # expect: firestarter/messages.py
```

**⚠ `ruff` is not on PATH in this devcontainer** — the script then writes `messages.py` unnormalised
with only a WARNING, and no CI gate catches it. Prepend the `.[test]` venv's `bin` before syncing.

---

### `firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` (test, streaming)

**Analog 1 — the refusal case, verbatim** (`:342-361`). This is a line-for-line template; the only
changes are the handle fields and the messages:

```c
void test_5v_page_write_execute_refuses_with_no_page_size(void) {
    firestarter_handle_t h = {};
    h.protocol       = 0x05;
    h.cmd            = CMD_WRITE;
    h.response_code  = RESPONSE_CODE_OK;
    h.chip_id        = 0;
    h.mem_size       = 65536;
    h.page_size      = 0;
    h.address        = 0;
    h.data_size      = 128;
    configure_memory(&h);
    clear_bus_recording();

    h.firestarter_operation_main(&h);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "a write with no resolvable page size must refuse");
    TEST_ASSERT_EQUAL_MESSAGE(0, bus_recording_count(),
        "a refused write must perform zero register writes");
}
```

`bus_recording_count() == 0` is the load-bearing half — "refuses" without "performed no write" does not
satisfy WRITE-01. Keep both assertions in every new refusal case.

**Analog 2 — the positive-control / non-vacuity triple** (`:440-447`, from the boundary cases):

```c
    TEST_ASSERT_FALSE_MESSAGE(bus_recording_saturated(),
        "recorder saturated -- the boundary assertion below would be vacuous");
    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code,
        "non-vacuity control: the write must have actually run");
    TEST_ASSERT_EQUAL_MESSAGE(2, sig_count,
        "exactly two SDP signatures across a two-page span -- ...");
```

`bus_recording_saturated()` lives in `test/native/avr/_shared/host_stubs_common.inc:184` behind
`HOST_STUBS_MAX_RECORDING` (`#ifndef`-guarded, default 4096 → ~1361 data bytes). No change needed for
`P <= 512` cases.

**Analog 3 — the parameterised driver** (`:363-377`):

```c
static firestarter_handle_t drive_page_boundary_case(uint32_t mem_size, uint16_t page_size, uint32_t data_size) {
    firestarter_handle_t h = {};
    ...
    h.address        = 0;
    h.data_size      = data_size;
    configure_memory(&h);
    clear_bus_recording();

    h.firestarter_operation_main(&h);
    return h;
}
```

**⚠ It hard-codes `h.address = 0`, and 7 existing boundary cases depend on it. Add a sibling driver
with an `address` parameter; do not mutate this one.**

**Analog 4 — the multi-chunk drive pattern** (`test_5v_page_write_execute_boundary_524288_512`,
`:464-480`): call `firestarter_operation_main`, then reassign `h.address` / `h.data_size` and call
again. That is the faithful model of the chunked host path (Pitfall 2 in RESEARCH §10) and the only way
to exercise interior chunk-boundary loss.

**Registration:** add `RUN_TEST(...)` lines in the existing block at `:759-790`, grouped with the
other `write_execute` cases (`:763-781`).

---

### `.planning/v1.39/195-*-bench-transcript.md` (doc artefact, batch) — CREATE

**Analog:** `.planning/v1.39/194-w29c020-bench-transcript.md` (303 lines, tracked, meta repo). Copy its
frontmatter shape verbatim:

```markdown
---
title: W29C020 no-regression bench transcript — protocol 0x05, milestone v1.39 Phase 194
phase: 194-real-page-size-reaches-the-firmware
plan: "07"
measured: 2026-09-15
status: AUTHORITATIVE — the silicon no-regression half of D-11. Not authoritative for any of the 9 previously under-sized parts. See §5.
pairs_with: .planning/v1.39/194-page-size-27-row-record.md
requirements: [PAGE-03 (hardware no-regression half only — hardware leg for the 9 held OPEN)]
---
```

**Section structure to follow exactly** (its own headings, verified this session):

| § | Heading | What it must contain here |
|---|---|---|
| — | opening line | *"Every figure below carries the verbatim command that produced it. Nothing here is carried forward from research or from another plan without a citation."* |
| 1 | The rig, as the operator described it | seated part, **shield revision as an operator statement, never inferred**, port, parts availability |
| 2 | Rig identity, re-confirmed (not merely trusted) | `ls -la /dev/ttyACM*`, the USB sysfs `idVendor/idProduct/manufacturer/product` read, and the **post-flash port re-identification** (the Leonardo 1200bps touch renumbers the node) |
| 3 | Firmware flashed, and the version under test | build from source + the `bootloader-guard` size line as attribution evidence. **This phase needs this section twice** — pre-fix build (loss reproduction) and post-fix build |
| 4 | Chip-ID confirmation, write, and read-back | 4a chip-ID (never the printed marking), 4b pattern generation rule and size, 4c the write, 4d the read-back comparison, 4e negative control recorded **as skipped, with the reason** |
| 5 | What this transcript proves, and what it does not | the honest scope limit; 194's §5 is the model |

**Pattern generation rule to reuse** (194-07's, designed to expose misplaced boundaries):
`byte[i] = ((i // 128) * 17 + (i % 128)) & 0xFF`.

**Read-back gotcha to carry:** a region read seeks to the **absolute** offset, so read from `0x0` with
an explicit `-s` covering the whole probe window, as 194-07 did.

---

### `VALIDATED-EPROMS.md` — regenerate, never hand-edit

**No content analog — the pattern is the tool.** The file is generated by
`.claude/skills/devtest-triage/scripts/eprom_ledger.py`, which exposes `list`, `write`, `check`, `add`:

```bash
python3 .claude/skills/devtest-triage/scripts/eprom_ledger.py check   # exit 1 if it differs from a fresh render
python3 .claude/skills/devtest-triage/scripts/eprom_ledger.py add ...
python3 .claude/skills/devtest-triage/scripts/eprom_ledger.py write
```

The rows this phase's criterion 4 touches, verbatim from the current file: `AE29F2008`, `W29C020`,
`W29C040` (all `PROTO_FLASH_5V_PAGE`) and `SST39SF020` (`PROTO_FLASH_NOR_UNLOCK`, **algorithm `0x06` —
out of this phase's blast radius entirely**, per RESEARCH §7). The `## Notes` section is where the
"AE29F2008 and W29C020 are the same silicon" finding already lives — the analog for recording a
by-identity re-check rather than a bench pass.

---

### Plan-file shape (for the planner)

**Analog:** `.planning/phases/194-real-page-size-reaches-the-firmware/194-05-PLAN.md:1-16`. 6 of 7 of
that phase's plans carry `commits_land_in:`, which is what keeps a sub-repo commit landing in the right
repository:

```yaml
---
phase: 194-real-page-size-reaches-the-firmware
plan: 05
type: execute
wave: 2
depends_on: [194-01]
commits_land_in: [firestarter_app]
files_modified:
  - firestarter_app/firestarter/page_size_gate.py
  ...
autonomous: true
requirements: [PAGE-01]
---
```

194-05 is also the closest analog for *this* phase's host plan by content — same two call sites, same
exception, same test module.

---

### If the planner takes hybrid c1 (host-side alignment)

No new analog is needed. The read primitive is `EpromOperator.read_eprom(..., address_str=, size_str=)`,
used exactly this way by `chip_test._read_region` (`chip_test.py:2885-2915`) — that is the analog for
"read the head/tail page, splice, issue an aligned write". The refusal strand above still ships as the
backstop; c1 only changes what the host does *before* the predicate is evaluated.

---

## Shared Patterns

### Fail-closed refusal before any I/O
**Sources:** `firestarter/page_size_gate.py:80-88` (the predicate + raise),
`firestarter/exceptions.py:92-102` (the exception class), `cli_handlers.py:218-219` (the dedicated
`except` arm), `cli_handlers.py:764` + `eprom_operations.py:2009` (both call sites).
**Apply to:** the new alignment guard, its exception, and both call sites. **Never** `raise
EpromOperationError(...)` directly — the generic arm prefixes `"Programmer error: "`.

### Refuse before the first register write
**Source:** `firestarter_fw/src/proms/flash_5v_page.cpp:80-86`.
**Apply to:** the firmware alignment guard. Position it before the loop, assert
`bus_recording_count() == 0` in the test. A page load cannot be aborted once bytes are loaded.

### Non-vacuity beside every new assertion
**Sources:** `test_val_5v_page.cpp:330-336` (`bus_recording_saturated()` + `RESPONSE_CODE_OK` control
beside the count); `tests/test_page_size_write_refusal.py:92-104` (the pass-through case beside every
refusal case).
**Apply to:** every new native refusal case and every new host refusal test. A refusal test without its
pass-through twin cannot distinguish a working gate from a blanket refusal.

### Generated artefact — regenerate, never hand-edit
| Artefact | Regenerated by | Gate |
|---|---|---|
| `firestarter_fw/include/messages.h` | `bash tools/catalog/sync_to_subrepos.sh` (meta repo only) | none in CI — check `git status` by hand |
| `firestarter_app/firestarter/messages.py` | same script, then `ruff format` | none in CI; `ruff` must be on PATH |
| `/workspaces/VALIDATED-EPROMS.md` | `eprom_ledger.py write` | `eprom_ledger.py check` exits 1 on a hand edit |

### No comments in product source (hard rule, not overridable)
`/workspaces/CLAUDE.md`: write **no** comments under `firestarter_fw/` or `firestarter_app/`. Where a
comment this phase falsifies exists, **delete the false clause with no replacement**. Rationale belongs
in `195-SUMMARY.md`, REQUIREMENTS traceability, or the commit message. Python **docstrings are not
comments** — `page_size_gate.py`'s explanatory module docstring and
`test_page_size_write_refusal.py`'s property list are both legal and are the right home for the new
gate's rationale. C/C++ has no such exemption.

### Planning-citation gate scope
`planning_citation_gate.py` runs in both sub-repos' CI over app `firestarter tests tools` and firmware
`src include test tests scripts platform tools`. Forbidden in comments *and code*: `.planning`,
`ROADMAP.md`/`REQUIREMENTS.md`, `Phase NNN`, `D-NN`, `WRITE-NN`. Python docstrings are never scanned —
which is why `test_page_size_write_refusal.py:7` legitimately names its origin phase. **Do not copy
that line into a C/C++ file.**

### Host gates that scan firmware source fail OPEN on renames
`firestarter_app/tests/test_page_size_invariants.py` and `tests/test_py32_flash_map_host.py` read
firmware paths. If this phase renames anything in `flash_5v_page.cpp`, re-run those two specifically and
confirm they still find their targets.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `firestarter_fw/include/messages.h` | build output | — | Generated by `tools/catalog/sync_to_subrepos.sh` in the meta repo. Never hand-edited; the pattern is the regeneration command. |
| `firestarter_app/firestarter/messages.py` | build output | — | Same script. `ruff`-normalised; unnormalised output is a silent WARNING, not an error. |
| `/workspaces/VALIDATED-EPROMS.md` | generated ledger | batch | Generated by `eprom_ledger.py`; the pattern is `add` + `write` + `check`, not the file's text. |

No file in this phase lacks a usable analog for reasons of novelty. **Every seam this phase needs was
built one phase ago for the sibling defect** — the risk to plan quality here is invention, not difficulty.

---

## Corrected / Confirmed Citations

| Source | Citation | Status |
|---|---|---|
| RESEARCH §11 | `cli_handlers.py:762-766` (call site) | **Confirmed verbatim** this session |
| RESEARCH §11 | `eprom_operations.py:2003-2011` (call site) | **Confirmed verbatim** this session |
| RESEARCH §11 | `page_size_gate.py:80-88` | **Confirmed verbatim** this session |
| RESEARCH §11 | `flash_5v_page.cpp:80-86` | **Confirmed verbatim** this session |
| RESEARCH §2 | `page_size_gate.py:63-88` (the function) | Signature at `:63-67`; docstring `:68-79`; body `:80-88` |
| RESEARCH §3b | `exceptions.py` PageSizeUnavailableError | Class at **`:92-102`** (RESEARCH cites the analogous `:74-89` for `ChipNotImplementedError`) |
| RESEARCH §5b | `test_val_5v_page.cpp:342-367` refusal case | Body is **`:342-361`**; the next function (`drive_page_boundary_case`) starts at `:363` |
| RESEARCH §4a | messages.toml `0xBF` stanza `:700-706` | **Confirmed**; DATA banner at `:708-710` |
| RESEARCH §7 | `VALIDATED-EPROMS.md` rows | **Confirmed**; note the live file has `Vendor` and `VCC` columns the research's quoted table omits |

---

## Metadata

**Analog search scope:** `/workspaces/tools/catalog/`, `/workspaces/.planning/v1.39/`,
`/workspaces/.claude/skills/devtest-triage/`, `firestarter_app/{firestarter,tests}/`,
`firestarter_fw/{src,include,test,tests}/`.
**Search tool:** `/usr/bin/grep` exclusively.
**Tracked-source verification:** `git ls-files` per repository — all 13 analog paths tracked; no
gitignored mirror path emitted.
**Pattern extraction date:** 2026-09-16
