# Phase 195: Partial Writes Stop Destroying the Page — Research

**Researched:** 2026-09-16
**Domain:** AVR firmware (protocol `0x05` page-write flash) + Python host pre-flight gating, dual-repo lockstep
**Confidence:** HIGH on the defect mechanism, the code sites, the measured budgets and the regression surface. MEDIUM on the datasheet timing figures (manufacturer document obtained through a third-party mirror). The fix-shape choice is a **recommendation**, not a finding.

---

## Summary

The defect is one line of arithmetic and one missing piece of knowledge. `flash_5v_page_write_execute`
decides "start a page load" with `is_page_start || is_first_byte` and "commit the page" with
`reached_page_end || is_last_byte`. The two `|| ...` clauses exist so that a chunk that does not begin
or end on a page boundary still produces a syntactically complete page cycle — and that is exactly the
corruption: the W29C020 datasheet states that on an internal page write, **"Any byte that is not loaded
will be erased to `FF hex`"**. A page cycle driven over a partial load therefore erases every byte of
that physical page the operator did not send. The host then reports `successful`, because "successful"
means only that the state machine completed without an `ERROR` frame.

Phase 194 already landed everything this phase needs underneath it: the real page size reaches
`handle->page_size` for all 27 protocol `0x05` parts, the firmware refuses rather than guesses when it
cannot resolve one, and the host carries a working two-layer fail-closed pre-flight gate
(`page_size_gate.py`) that runs **before any serial byte is emitted**. This phase is the second half of
the same seam, and the host gate is a ready-made template for it.

Two measurements decide the fix-shape fork before any taste is involved. First, the firmware cannot
read the device between byte loads — the datasheet's `TBLC` load window closes 200 µs after the last
byte and the device commits — so a firmware read-modify-write must stage the whole physical page in RAM
**before** the SDP unlock. A 512-byte staging buffer was measured in-session: it leaves **142 bytes** of
RAM on `uno` and **213 bytes** on `leonardo` for the entire call stack. That is not a tight fit, it is a
guaranteed stack overflow. Second, the firmware never learns the total write length — the host sends
`address` but not a payload size — so a firmware-only refusal fires at the *last* chunk, after earlier
chunks have already been programmed. "Refuses and leaves the device unchanged" is therefore only
achievable **host-side, pre-connect**.

**Primary recommendation:** ship a two-layer refusal — a host pre-flight predicate
(`start % page_size == 0 && payload_len % page_size == 0`, modelled line-for-line on
`page_size_gate.require_page_size`) plus a firmware per-chunk guard that refuses a chunk whose
`address` or `data_size` is not page-aligned and performs zero register writes. D-2 explicitly permits
this shape, it costs no RAM, and it is the only shape that can honestly claim "the device is
unchanged". If the operator wants partial writes to still *work*, add host-side alignment
(read the head/tail page, splice, issue an aligned write) as a **separable second strand** — it needs
no firmware RAM and no firmware change, and it can land later without reopening the safety requirement.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Deciding a write is unsafe *before the device is touched* | Host (`firestarter_app`, pre-connect predicate) | — | Only the host knows the total payload length; the firmware sees one chunk at a time and never learns the end. "Leaves the device unchanged" is unachievable anywhere else. |
| Refusing an unsafe page cycle whatever the host did | Firmware (`flash_5v_page.cpp`) | — | The firmware is the last line of defence against an old host, a third-party host, or a future host bug. A host-only fix leaves the silicon defenceless. |
| Naming the refusal to the operator | Message catalog (`tools/catalog/messages.toml`, meta repo) | Host renderer (`messages.py`) | Firmware emits a numeric id only; the format string lives host-side. Generated in the meta repo, never in a sub-repo. |
| Preserving the untouched bytes of a page (if chosen) | Host (read head/tail page, splice, write aligned) | — | Measured: a firmware page buffer is unaffordable on `uno` at 512 B. The host has RAM, a working region-read path and the page size. |
| Knowing the physical page size | Chip database → wire `page-size` → `handle->page_size` | — | Landed by Phase 194; not re-derived here (D-3). |
| Proving the outcome on silicon | Bench (operator rig + agent over USB passthrough) | Native Unity suite | D-4: a green native test is not sufficient for a defect found on a bench. |

---

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| WRITE-01 | A partial or unaligned `0x05` write preserves every untouched byte of the touched page, **or** refuses with a named error and leaves the device unchanged | §1 names the exact mechanism and the three loss directions; §3 compares both permitted shapes with measured RAM/flash/behaviour evidence; §3(b) gives the smallest correct predicate and the exact two insertion points, already proven by the Phase 194 sibling gate |
| WRITE-02 | No `0x05` write reports `successful` when bytes outside the requested range were erased | §2 traces the success path to `eprom_operations.py:2096-2099` and shows the two levers (pre-flight exception → no success line; firmware `ERROR` frame → `is_ok=False` → `"Write to X failed."`). §3(b)-override-trap names the one way a plan could accidentally violate this |
| WRITE-03 | Both loss directions demonstrated on real silicon | §6 prescribes the full bench procedure in `194-w29c020-bench-transcript.md` format, incl. the pre-fix reproduction step that is the only way to *demonstrate loss* once the fix lands, and the operator-only vs agent-drivable split |

**No `195-CONTEXT.md` exists.** The operator chose to plan without one, so this research carries no
`## User Constraints` section. The binding constraints are therefore `.planning/REQUIREMENTS.md`
D-1…D-5 (quoted where used), the ROADMAP Phase 195 success criteria, and `/workspaces/CLAUDE.md`.
The fix-shape decision is **OPEN** and is the planner's to make; §3 exists to make it decidable.

---

## 1. The defect, precisely

### 1a. The site

`[VERIFIED: /workspaces/firestarter_fw/src/proms/flash_5v_page.cpp:80-112, read this session at branch `v1.39-protocol-0x05-write-correctness` (firmware HEAD `c2b8baa`)]` — verbatim, post-Phase-194:

```c
void flash_5v_page_write_execute(firestarter_handle_t* handle) {
    uint32_t page_mask;
    if (!flash_5v_page_mask(handle->page_size, &page_mask)) {
        LOG_ERROR_ID_U16(MSG_ERR_FL4_PAGE_SIZE, handle->page_size);
        handle->response_code = RESPONSE_CODE_ERROR;
        return;
    }
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint32_t address = handle->address + i;
        uint8_t expected = handle->data_buffer[i];

        /* SDP 3-byte unlock at the start of each page load (AMD/JEDEC SDP).
         * W29C040 ships with Software Data Protection enabled; without this
         * sequence the page-buffer write is silently rejected.
         * Call per-page-START (not per-byte) — calling per-byte would abort
         * the current page load and restart it after each byte. */
        bool is_page_start = (address & page_mask) == 0;
        bool is_first_byte = (i == 0);
        if (is_page_start || is_first_byte) {
            flash_execute_command(FLASH_ENABLE_WRITE);
        }

        handle->firestarter_set_data(handle, address, expected);

        bool reached_page_end = ((address + 1) & page_mask) == 0;
        bool is_last_byte = i == handle->data_size - 1;
        if (reached_page_end || is_last_byte) {
            if (!flash_5v_page_wait_for_page_write(handle, address, expected)) {
                return;
            }
        }
    }
}
```

**The two clauses that are the defect are `|| is_first_byte` (line 98) and `|| is_last_byte`
(line 106).** They are not bugs in isolation — they exist so a chunk always produces a complete
page cycle. They become data loss because of what the silicon does with a *partially loaded* page.

### 1b. The mechanism, from the part's own datasheet

`[CITED: W29C020 datasheet, Winbond, Revision A3, publication date February 1998, § "Page Write Mode" — PDF fetched in-session (21 pages) and text-extracted, mirror `https://www.tvsat.com.pl/pdf/w/w29c020_win.pdf`]`, verbatim:

> "The W29C020 is written (erased/programmed) on a page basis. Every page contains 128 bytes of data.
> If a byte of data within a page is to be changed, data for the entire page must be loaded into the
> device. **Any byte that is not loaded will be erased to "FF hex" during the write operation of the
> page.**"

and, on the load window:

> "If the host loads a second byte into the page buffer within a byte-load cycle time (TBLC) of 200 µS
> after the initial byte-load cycle, the W29C020 will stay in the page load cycle. Additional bytes can
> then be loaded consecutively. **The page load cycle will be terminated and the internal write
> (erase/program) cycle will start if no additional byte is loaded into the page buffer.**"

and, on addressing within the page:

> "A7 to A17 specify the page address. All bytes that are loaded into the page buffer must have the same
> page address. A0 to A6 specify the byte address within the page. The bytes may be loaded in any order;
> sequential loading is not required. In the internal write cycle, all data in the page buffers, i.e.,
> 128 bytes of data, are written simultaneously into the memory array."

So: **the erase is implicit, whole-page, and unconditional.** The firmware never issues an erase; the
part erases the page as part of committing it. Whatever was not loaded is gone. This is also why
`FLAG_CAN_ERASE` is deliberately clear for protocol `0x05` and `erase` answers `Not supported`
(gh#68's own "Related" note, and `flash4_erase_gate.py`).

Three consequences the planner must keep separate:

- The firmware's `flash_5v_page_wait_for_page_write` poll is *not* what commits the page — the device
  commits by itself 200 µs after the last load. The poll only observes completion.
- There is no way to "abort" a page cycle once bytes are loaded. Refusal must happen **before** the
  first `firestarter_set_data` of that page.
- "Bytes may be loaded in any order" means a read-modify-write does not have to preserve order — but
  every byte must be loaded before the window closes, which is why a mid-load read is impossible.

### 1c. The loss directions — WRITE-03 names two; the code produces three

Let `P` = page size, `S` = start address (`-a`), `L` = payload length (file size), `C` = chunk size
(`DATA_BUFFER_SIZE`: 512 on uno, 1024 on leonardo).

| # | Direction | Predicate | Mechanism |
|---|---|---|---|
| **1** | **Leading loss** — bytes *before* `S` | `S % P != 0` | On the first chunk, `i == 0` fires `is_first_byte`, so the SDP unlock starts a page load mid-page. The page commits with `[page_start, S)` never loaded → those bytes erase to `0xFF`. Confirmed on silicon in gh#68: `write w29c020 probe2.bin -a 0x40` erased `0x000-0x03F`. |
| **2** | **Trailing loss** — bytes *after* `S+L` | `(S + L) % P != 0` | On the final chunk, `is_last_byte` fires and the page commits with `[S+L, page_end)` never loaded → erased. Confirmed on silicon in gh#68: a 64-byte file at `-a 0x0` erased `0x040-0x07F`. |
| **3** | **Interior loss at chunk boundaries** — bytes *inside* the requested range | `S % P != 0` **and** `L > C` | Not named by gh#68 (its probes were single-chunk, 64 bytes). `handle->address += handle->data_size` after each chunk `[VERIFIED: firestarter_fw/src/eprom_operations.cpp:142]`, so with `S = 0x40`, `C = 512`, `P = 128`: chunk 1 spans `0x40-0x23F` and its `is_last_byte` commits page `0x200-0x27F` holding only `0x200-0x23F`; chunk 2 starts at `0x240`, `is_first_byte` re-opens that same page and commits it holding only `0x240-0x27F` — **erasing `0x200-0x23F`, which chunk 1 had just written**. One page destroyed per chunk boundary, inside the range the operator asked for. |

Direction 3 is a **derived prediction from the source and the datasheet, not an observed silicon
result** — it has never been run. It is cheap to add to the bench sheet (§6, optional case E) and it
strengthens the case that a partial write cannot be made safe by patching only the ends.

### 1d. Why Phase 194 was a prerequisite and did not fix this

`[CITED: .planning/v1.39/194-page-size-27-row-record.md §5]` — verbatim: *"It does not prove the
partial/unaligned-write defect (gh#68) is fixed. That is Phase 195's subject. A correct page size does
not by itself stop a partial write from erasing the rest of a page it was not asked to touch."* The
dependency runs the other way: any fix here — refusal predicate or read-modify-write — is arithmetic
**on the page size**, so on the 9 previously under-sized parts a pre-194 fix would have computed the
wrong boundary and corrupted them while claiming to protect them.

---

## 2. Where `successful` is reported, and what WRITE-02 turns on

The chain, end to end `[VERIFIED: each line read this session]`:

| Step | File:line | What happens |
|---|---|---|
| 1 | `firestarter_fw/src/proms/flash_5v_page.cpp:107` | On a verify-poll timeout only, sets `RESPONSE_CODE_ERROR`. A partial page load produces **no** error — the poll reads back the last byte the firmware itself wrote, which is present and correct. The collateral damage is invisible to this check by construction. |
| 2 | `firestarter_fw/src/eprom_operations.cpp:138-143` | `op_execute_function(...)` then `handle->address += handle->data_size` and continue. |
| 3 | `firestarter_app/firestarter/eprom_operations.py:779-795` | `_main_phase_send_data`: any `ERROR`-typed response raises `EpromOperationError` (`_raise_for_error_response`). No error frame → loop continues to the `MAIN` response and returns. |
| 4 | `firestarter_app/firestarter/eprom_operations.py:2032-2039` | `is_ok, _ = self._run_state_machine(...)` — `is_ok` means *"the three-phase state machine completed without an ERROR frame"*, nothing more. |
| 5 | **`firestarter_app/firestarter/eprom_operations.py:2096-2099`** | The success line, verbatim: `if is_ok:` / `logger.info(f"Write to {eprom_name.upper()} successful ({time.time() - start_time:.2f}s).")` — with the `else:` arm at `:2101` emitting `f"Write to {eprom_name.upper()} failed."` |
| 6 | `firestarter_app/firestarter/cli_handlers.py:766-785` | `ok = app.eprom_operator.write_eprom(...)` → `sys.exit(0 if ok else 1)`. |

**So `successful` currently asserts protocol completion, not data integrity.** There is no third state.

**What WRITE-02 requires changing — two levers, both already built in this codebase:**

1. **Pre-flight refusal (host).** A guard raising before `_operation_context` is entered means step 4
   never runs, so step 5 never runs. `map_typed_errors` renders the exception text verbatim and exits
   non-zero. This is exactly how `PageSizeUnavailableError` behaves today
   `[VERIFIED: firestarter_app/firestarter/page_size_gate.py:63-88 + tests/test_page_size_write_refusal.py:67-79]`.
2. **Firmware refusal (device).** An `ERROR` frame at step 1 propagates to step 3 as an exception →
   `is_ok = False` → `"Write to X failed."` at `:2101`. Also already proven
   `[VERIFIED: test_val_5v_page.cpp:342-367, `test_5v_page_write_execute_refuses_with_no_page_size`]`.

**The trap for the planner.** gh#68's remedy 2 suggests refusing *"behind an explicit override flag"*.
An override that proceeds and then prints `Write to X successful` **violates WRITE-02 literally** —
the requirement is unconditional ("No protocol `0x05` write reports `successful` when bytes outside the
requested address range were erased"). If an override is offered at all, its outcome line must not be
the plain success line. Recommendation: do not ship an override in this phase; it is a separable
usability decision and it is the single easiest way to fail this phase's own requirement.

---

## 3. The fix-shape fork — the evidence

D-2, verbatim `[CITED: .planning/REQUIREMENTS.md:24]`: *"**Refusing is an acceptable fix.**
Read-modify-write is not assumed. A firmware that declines an unsafe partial write with a clear error
resolves WRITE-01 — losing the operation is strictly better than losing the chip."*

### 3a. Shape (a) — read-modify-write **in the firmware**

**Can it read mid-write? Yes, the primitive exists — but it cannot be used mid-page-load.**
`handle->firestarter_get_data` is assigned unconditionally for every protocol
`[VERIFIED: firestarter_fw/src/proms/memory.cpp:78-79]`:

```c
    handle->firestarter_get_data = memory_get_data;
    handle->firestarter_set_data = memory_set_data;
```

and `flash_5v_page_wait_for_page_write` already calls it *during* a write operation
`[VERIFIED: flash_5v_page.cpp:119]`. So the mechanical route exists. What forbids interleaving is the
datasheet: the load window (`TBLC` = 200 µs) closes on the first gap, and the device then commits.
A read costs an address set, a bus-direction flip, a settling delay and a strobe
`[VERIFIED: memory.cpp:319-336 — `rurp_chip_output(); ... rurp_set_data_input(); ...` plus an optional
settling delay]`. Therefore **the whole physical page must be staged in RAM before the SDP unlock**.

**Measured RAM cost of that staging buffer** (reversible in-session experiment: a referenced
`static uint8_t` array added to `flash_5v_page.cpp`, both envs rebuilt, file restored and byte-identity
re-confirmed by `md5sum` + empty `git status --porcelain`):

| Staging buffer | `uno` RAM used / 2048 | free for stack | `leonardo` RAM used / 2560 | free for stack |
|---|---|---|---|---|
| **none (today)** | **1394 B (68.1 %)** | **654 B** | **1835 B (71.7 %)** | **725 B** |
| 128 B | 1522 B (74.3 %) | 526 B | 1963 B (76.7 %) | 597 B |
| 256 B | 1650 B (80.6 %) | 398 B | 2091 B (81.7 %) | 469 B |
| **512 B** | **1906 B (93.1 %)** | **142 B** | **2347 B (91.7 %)** | **213 B** |

`[VERIFIED: pio run -e uno / -e leonardo, in-session, PlatformIO "Advanced Memory Usage" line]`

**Read this as a hard stop, not a budget.** The AVR figure is `.data + .bss`; everything left is stack
*and* heap for the whole firmware, including the JSON parser, the COBS framer and the serial buffers.
512 B leaves 142 B on an `uno`. That is a stack overflow, not a tight fit.

**Is the page always smaller than the chunk buffer? Yes — and it is the wrong question.**
`[VERIFIED: in-session enumeration of the 27 `algorithm: 5` rows in
`firestarter_app/firestarter/data/chip_database.json`]`:

```
page-size distribution: {64: 3, 128: 16, 256: 6, 512: 2}
  page 64:  AT29C256, AT29C257, AT29LV256
  page 128: AE29F1008, AE29F2008, AT29BV010A, AT29C512, AT29C010A, AT29LV512, SST29EE010,
            SST29EE020, SST29EE512, SST29LE010, SST29LE020, SST29LE512, W29C010, W29C020,
            W29C512, W29EE011
  page 256: AE29F4008, AT29BV020, AT29BV040A, AT29C020, AT29C040A, W29C040
  page 512: AT29BV040, AT29C040
```

Max page 512 = `DATA_BUFFER_SIZE` on uno `[VERIFIED: firestarter_fw/include/firestarter.h:16-18,189 —
`#define DATA_BUFFER_SIZE 512` and `char data_buffer[DATA_BUFFER_SIZE];`]`. So the page is never
*larger* than the chunk buffer — but `data_buffer` is occupied by the incoming payload, so it cannot
double as the staging buffer, and the staging buffer is a **second** allocation. 25 of 27 parts have
`P <= 256`; only `AT29BV040,AT29LV040` and `AT29C040` are 512.

**Two further costs of firmware RMW, both structural:**

- **Double page cycles at chunk boundaries.** Because the firmware never learns the total length
  (§3b), an RMW must restore the page tail at every chunk end, and the next chunk must then re-program
  the same page. That is 2 erase/program cycles for each boundary page against a part rated
  *"Typical page write (erase/program) cycles: 100/1K/10K"* `[CITED: W29C020 datasheet, Features]` —
  wear on the lowest-rated devices in the family.
- **Time.** Each restored byte costs one read (address set + settle + strobe) before the load; each page
  commit costs up to 10 ms `[CITED: W29C020 datasheet, "Page write (erase/program) cycle: 10 mS (max.)"]`.
  For a partial write this is bounded and small; for the double-cycle case it doubles the page commits.

**Verdict on (a): not viable in firmware as a general fix.** It is viable only if the phase accepts a
per-part capability split (RMW for `P <= 128` or `<= 256`, refusal for the rest), which means shipping
two behaviours for one protocol and a bench matrix that has to prove both. Note that the 2 parts it
would fail on (`AT29BV040`, `AT29C040`) are also 2 of the 9 parts with no silicon evidence at all
`[CITED: 194-page-size-27-row-record.md §2]`.

### 3b. Shape (b) — refuse

**The smallest correct predicate**, with `P = page_size`, `S = start address`, `L = payload length`:

```
S % P == 0   AND   L % P == 0
```

Equivalently, with the mask Phase 194 already computes: `(S & (P-1)) == 0 && (L & (P-1)) == 0`.
`L % P == 0` is exactly `(S + L) % P == 0` given the first clause, and it is the more natural form
host-side because `L` is `os.path.getsize(input_file)`.

**Where it must live, and why the layer matters.** The firmware **does not know `L`**
`[VERIFIED: firestarter_app/firestarter/eprom_operations.py:480-497 — only `address` and, for reads,
`memory-size` are injected into the command dict; there is no write-length field]` and
`[VERIFIED: firestarter_fw/src/json_parser.c:56,130 — `const char key_address[] PROGMEM = "address";`
and `FIELD(key_address, address, 0)`; no length key exists]`. A firmware-only guard therefore fires on
the **last** chunk, by which time every earlier chunk has been programmed. That satisfies "no byte
outside the requested range was erased" but **not** "leaves the device unchanged". WRITE-01's refusal
branch is only honestly satisfiable **host-side, pre-connect**.

**The two insertion points are already built and tested** — this is the Phase 194 sibling gate, one
plan old:

| Layer | Exact site | Today |
|---|---|---|
| CLI pre-flight | `firestarter_app/firestarter/cli_handlers.py:764` | `page_size_gate.require_page_size(eprom, eprom_data, "write")`, immediately before `app.eprom_operator.write_eprom(...)` at `:766` |
| Operator layer (covers `dev test` and every non-CLI caller) | `firestarter_app/firestarter/eprom_operations.py:2009` | `require_page_size(eprom_name, eprom_data_dict, "write")`, immediately before `with self._operation_context(...)` at `:2011` — **the port opens inside that context, not before** |

Both call sites already receive everything the new predicate needs: `eprom_data`/`eprom_data_dict`
carries the wire `page-size`; `address_str` and `input_file_path` are `write_eprom` parameters.
`page_size_gate.py` is a pure predicate module with no I/O `[VERIFIED: page_size_gate.py:16-19 docstring]`
and its test module `tests/test_page_size_write_refusal.py` (9 tests, all 4 properties: refusal before
`_operation_context`, pass-through, no-op for other algorithms/operations, verbatim rendering with no
`"Programmer error: "` prefix) is a drop-in template.

**⚠ `map_typed_errors` ordering.** A new exception subclassing `EpromOperationError` needs **its own
`except` arm above the generic arm**, or the message is prefixed with `"Programmer error: "`
`[VERIFIED: cli_handlers.py:188-221 — `ChipNotImplementedError` at :205, `PageSizeUnavailableError`
at :218, the generic `EpromOperationError` arm at :220; pinned by
`test_page_size_unavailable_renders_verbatim_with_no_generic_prefix`]`.

**What refusing breaks, measured — not estimated:**

| Caller | Today | Under the predicate |
|---|---|---|
| `firestarter write <chip> <file>` (no `-a`), file size a multiple of `P` | works | **works** — the overwhelmingly common case: `P ∈ {64,128,256,512}` and ROM images are almost always power-of-two sized |
| `firestarter write <chip> <file>` with an odd-sized file (e.g. 1000 B) | silently erases the tail of the last page | **refused** — a real, if uncommon, regression |
| `firestarter write <chip> patch.bin -a <unaligned>` | silently erases up to `P-1` neighbours in both directions | **refused** — this is gh#68's headline use case, *"the normal way to patch part of a ROM image"* |
| `firestarter verify` / `read` / `blank-check` / `erase` | unaffected | unaffected — the predicate is write-only, like `_WRITE_OPERATIONS = frozenset({"write"})` |
| **`dev test` write step** | writes **256 bytes at address 0** `[VERIFIED: chip_test.py:2112-2113,2133 — `_WRITE_REGION_START = 0`, `_WRITE_REGION_LENGTH = 256`, `_DEFAULT_REGION = (_WRITE_REGION_START, _WRITE_REGION_LENGTH)`; `_write_region_for` returns the engine default for every non-UV part, and `_address_arg(0)` returns `None`]` | **aligned, and therefore unaffected, for `P ∈ {64,128,256}` — which is 25 of 27 parts, including all four validated ones.** It becomes a **partial page and is refused** on the 2 parts with `P = 512` (`AT29BV040,AT29LV040` and `AT29C040`), neither of which has ever been tested on silicon |
| Resume / offset paths | none exist — `write` has no `--size`, no resume, and no offset beyond `-a` `[VERIFIED: cli_handlers.py:578-633, the full `write` option list: `-b/--no-blank-check`, `--skip-erase`, `-f/--force`, `-a/--address`, `--vpe-as-vpp`, `--pulse-us`, `--skip-sdp-unlock`]` | — |
| UV `dev test` slot writes (`_UV_WRITE_REGION_LENGTH`) | protocol `0x07`/`0x08`/`0x0B` only | not reachable — the predicate is keyed on `algorithm == 5` |

**Which of the four validated parts would start refusing operations that work today? None.**
`W29C020` (P=128), `W29C040` (P=256), `AE29F2008` (P=128) all take `dev test`'s 256-byte
region-at-zero as a whole number of pages; `SST39SF020` is not a protocol `0x05` part at all (§7).

**Firmware half of (b).** A per-chunk guard `((handle->address & page_mask) != 0 ||
(handle->data_size & page_mask) != 0)` placed immediately after the existing page-mask resolution
(before the loop) refuses the chunk and performs zero register writes. It is compatible with every
legitimate aligned host write: with `S % P == 0` and `L % P == 0`, and `P | C` for every `P ∈
{64,128,256,512}` and `C ∈ {512,1024}`, every chunk starts page-aligned and carries a whole number of
pages, including the final short chunk (`L mod C` is divisible by `P` whenever `P | L` and `P | C`).
This is the same arithmetic 194-CONTEXT recorded: *"on a page-aligned contiguous write every chunk
boundary is also a page boundary"* `[CITED: 194-CONTEXT.md §Integration Points]`.

**Cost of (b):** zero RAM. Flash: a mask test and a `LOG_ERROR_ID_*` call site — for comparison,
Phase 194's whole resolve-or-refuse block (validator + refusal + two `&` substitutions) measured
**+6 B** on each env `[CITED: 194-RESEARCH.md §R2 flash measurement table]`. Headroom today is 10 640 B
(`uno`) and 4 938 B (`leonardo`) — §8.

### 3c. Shape (c) — hybrids

Three are coherent; one is recommended.

| Hybrid | Shape | Evidence |
|---|---|---|
| **c1 — host aligns, firmware refuses** | Host reads the head page and tail page, splices the payload over them, and issues a **page-aligned** write; firmware refuses any misaligned chunk as a backstop | **No firmware RAM cost** (the buffer lives in Python), works at every page size including 512, and keeps the `-a <unaligned>` use case *working*. Needs: `operator.read_eprom(..., address_str=, size_str=)` — the region-read primitive already exists and is used exactly this way by `chip_test._read_region` `[VERIFIED: chip_test.py:2885-2915]`. Cost: a second and third serial connection before the write (each sub-second — 194's transcript measured a 2048-byte read at 0.36 s), plus the honest caveat that a read failure must abort rather than proceed |
| **c2 — RMW where the page fits, refuse otherwise** | Firmware RMW for `P <= 128` (or 256), refusal for the rest | Splits one protocol into two behaviours; the refusal branch then applies to exactly the parts with **zero** silicon evidence. Bench matrix doubles. Not recommended |
| **c3 — refuse only when the firmware cannot read back** | — | Rejected: the firmware can *always* read; what it cannot do is read *mid-load*. The predicate would be constant-true and the hybrid collapses into (a) |

### 3d. Recommendation (a recommendation, not a finding)

**Ship (b) as the phase's core — the two-layer refusal — and treat c1's host-side alignment as a
separable second strand the planner may include or defer.**

Reasoning, visible:

1. D-2 explicitly permits refusal and states the preference order: *"losing the operation is strictly
   better than losing the chip"*. The milestone's own title is *"Never report success over bytes you
   erased"* — refusal satisfies it completely.
2. Shape (a) in firmware is **measured out of RAM** at 512 B and only viable as a per-part split.
3. Only a **host pre-flight** refusal can claim "leaves the device unchanged", because the firmware
   never learns the payload length. This is a structural fact, not a design preference.
4. The host template is one phase old, tested, and lives at the exact two call sites this needs. The
   plan is small, and small is what lets the bench evidence (D-4) be the expensive part.
5. Refusal's measured blast radius is narrow: no validated part regresses, no `dev test` run on a
   validated part regresses, and the only `dev test` casualty is 2 never-tested parts.
6. c1 restores the lost capability without touching the RAM ceiling, and can land after the refusal
   without reopening WRITE-01/02 — the refusal makes the chip safe, c1 makes the operation convenient.
   Sequencing it second is strictly cheaper than sequencing it first.

**If the planner takes c1 in this phase**, note that the firmware guard must still ship, otherwise
WRITE-02 rests entirely on a host the operator can downgrade (the same skew hazard already filed for
Phase 194 at `.planning/todos/pending/new-host-old-firmware-0x05-page-size-skew.md`).

---

## 4. Message catalog — and the band is now full

### 4a. ⚠ The ERROR band `0xA0–0xBF` is fully spent

`[VERIFIED: in-session parse of `/workspaces/tools/catalog/messages.toml` — 132 messages total;
`ERROR 0xa0-0xbf: used=32 free=[]`]`. Phase 194 spent the last free id, `0xBF`, on
`MSG_ERR_FL4_PAGE_SIZE` `[VERIFIED: messages.toml:700-706]`, verbatim:

```toml
[[messages]]
id          = 0xBF
name        = "MSG_ERR_FL4_PAGE_SIZE"
severity    = "ERROR"
format      = "page size %u rejected -- write refused"
params      = [{ type = "u16", render = "dec" }]
wire_format = "id_frame"
```

**So this phase inherits the band decision Phase 194 deliberately deferred.** It is filed as
`.planning/todos/pending/error-message-band-a0-bf-exhausted.md` (`resolves_phase:` empty), whose own
conclusion is that the next ERROR-severity id *"most likely 0xC0, extending the same band, but that is
the next phase's call to make and record."*

**Free space, measured:** `0xC0–0xDF` is entirely unallocated (32 ids); `0x80–0x9F` (WARN band) has 24
free from `0x88`; `0xE0–0xEF` (DATA) has 10 free `[VERIFIED: same in-session parse]`.

**Mechanically, `0xC0` works.** Severity is an explicit catalog field, not derived from the id range:
`codegen.py` Rule 7 validates only the `severity` string `[VERIFIED: tools/catalog/codegen.py:268-272]`,
and every firmware emit macro is identical regardless of severity — `LOG_ERROR_ID`, `LOG_WARN_ID` and
`LOG_OK_ID` all expand to the same `LOG_ID(id)` / `rurp_log_id((id), NULL, 0)`
`[VERIFIED: firestarter_fw/include/logging_id.h:28,105,114,123]`. The host decoder takes severity from
the catalog entry, not the band `[VERIFIED: firestarter_app/firestarter/serial_comm.py:535 —
`type=decoded.severity`]`.

**The guard that will judge the choice:**
`firestarter_app/tests/test_protection_status_catalog.py::test_error_band_fully_spent_0xa0_through_0xbf`
asserts `set(range(0xA0, 0xC0))` are all present and all `SEVERITY_ERROR` `[VERIFIED: that file,
lines 74-100]`. Minting `0xC0` with `severity = "ERROR"` leaves that test **green** — it asserts the
band is full, not that nothing exists above it. No test asserts "every ERROR id is below `0xC0`"
`[VERIFIED: /usr/bin/grep for `SEVERITY_ERROR` across `firestarter_app/tests/` returns only
`test_protection_status_catalog.py`]`.

**Planner decision (see §12 U1):** mint `0xC0` as ERROR and record the convention in `messages.toml`'s
header comment, closing the pending todo — or mint nothing and reuse the refusal shape below.

### 4b. Do the two refusals need separate ids?

Phase 195 needs **one** new id if the firmware guard emits its own message. Options:

- **One new id (recommended shape):** `MSG_ERR_FL4_PAGE_ALIGN`, `severity = "ERROR"`, with a
  `u32` param carrying the offending address or a `u16` carrying the offending `data_size` so the
  operator can tell which of the two clauses fired. Precedent for a parameterised refusal is `0xBF`
  itself.
- **Zero new ids:** reuse `MSG_ERR_FL4_PAGE_SIZE` (`0xBF`). **Rejected** — its format string says
  *"page size %u rejected"*, which is untrue here (the page size is fine; the address is not), and
  Phase 194 already rejected exactly this class of misleading reuse for exactly this reason
  `[CITED: 194-RESEARCH.md §R3 reuse-candidate table]`.

### 4c. The exact commands — generated ONLY in the meta repo

`[VERIFIED: /workspaces/tools/catalog/messages.toml:1-8]`, verbatim header:

```
# Firestarter v1.2 log-message catalog (canonical source — meta-repo authoritative)
#
# DO NOT REORDER ENTRIES. Codegen sorts by id ascending; the source file order
# is preserved for human-edit diff readability.
#
# Distribution: copied byte-identically into firestarter/tools/catalog/ and
# firestarter_app/tools/catalog/ by tools/catalog/sync_to_subrepos.sh.
# Edit ONLY this meta-repo copy; run the sync script after every edit.
```

(The header's "firestarter/tools/catalog/" wording is pre-rename prose; the script itself is correct —
see below.)

From the meta-repo root `/workspaces`:

```bash
# 1. Edit the canonical catalog — this file and no other:
#    tools/catalog/messages.toml
#    Insert position: after the 0xBF stanza (messages.toml:700-706), before the
#    "# DATA (0xE0..0xEF)" banner at :708-710.

# 2. Validate (cheap, optional):
python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check

# 3. Regenerate AND sync both sub-repos — one command does both:
bash tools/catalog/sync_to_subrepos.sh

# 4. Confirm exactly two generated files moved:
git -C firestarter_fw status --porcelain   # expect: include/messages.h
git -C firestarter_app status --porcelain  # expect: firestarter/messages.py
```

`[VERIFIED: tools/catalog/sync_to_subrepos.sh:12-13,24-25,35-70]` — it rewrites exactly two files,
`firestarter_fw/include/messages.h` and `firestarter_app/firestarter/messages.py`, and its roots are
**already post-rename correct** (`FS_ROOT="$META_REPO_CATALOG/../../firestarter_fw"`).

**⚠ Three standing traps, all still live:**

1. **`ruff` must be on PATH** or the script prints `WARNING: ruff not found -- messages.py written
   WITHOUT normalization` and the committed file carries pure-formatting drift
   `[VERIFIED: sync_to_subrepos.sh:69 `command -v ruff` branch]`. **`ruff` is NOT on PATH in this
   devcontainer** `[VERIFIED: `which ruff` → not found, in-session]`. It is present inside a
   `.[test]` virtualenv (`ruff 0.16.7`). Activate the venv, or prepend its `bin`, before running the
   sync.
2. **No CI gate catches a forgotten sync** `[CITED: 194-RESEARCH.md §R3, re-confirmed: the meta repo
   has no `.github/workflows/` at all]`. Make the sync an explicit task step with a `git status` check.
3. **Never hand-edit** `firestarter_fw/include/messages.h` or `firestarter_app/firestarter/messages.py`.
   Both are generated artefacts.

---

## 5. Native test surface

### 5a. What runs, and where

| Tree | Nature | CI |
|---|---|---|
| `firestarter_fw/test/native/avr/<suite>/` | PlatformIO **Unity C++**, cross-compiled against host libc + ArduinoFake | **Yes** — `pio test -e native` and `pio test -e native_nodevtools` |
| `firestarter_fw/tests/*.py` | Python source-scanner / record-sync suite, **30 modules** | **Yes** — `pytest tests/ -v` (on pushes/PRs to `main`/`beta` only) |
| `firestarter_app/tests/*.py` | Host pytest suite | **Yes** — `ci.yml`, Python **3.11** floor, `--cov-fail-under=70` |

**Measured green baselines on this branch, in-session:**

- `pio test -e native` → **`208 test cases: 208 succeeded in 00:01:18.747`**
- `firestarter_app` full suite on Python 3.11.16 → **`1896 passed in 151.02s`**, 32 snapshots passed
- `pio run -e uno` → `21616/32256 B`; `pio run -e leonardo` → `23734/28672 B` (byte-identical to
  194-06's recorded figures)

### 5b. The suite to extend — do not create a new one

**`firestarter_fw/test/native/avr/test_val_5v_page/`.** It already drives
`flash_5v_page_write_execute` through the dispatched pointer, is registered in **both** native envs
(so no `platformio.ini` change), and carries the whole oracle apparatus Phase 194 built
`[VERIFIED: test_val_5v_page/test_val_5v_page.cpp, read this session]`:

| Helper | Lines | What it gives a partial-write test |
|---|---|---|
| `drive_page_boundary_case(mem_size, page_size, data_size)` | 363-377 | A ready handle driver — **but it hard-codes `h.address = 0`**. A partial-write test needs an `address` parameter; add a sibling driver rather than mutating this one (7 boundary cases depend on it) |
| `count_sdp_signatures(int* out_indices, int max_out)` | 246-268 | Counts **and positions** every SDP unlock in the recording. Immune to register-write elision by construction (the three unlock addresses differ from every data address) |
| `bus_recording_count()` / `recorded_reg(i)` / `recorded_data(i)` / `clear_bus_recording()` | `_shared/host_stubs_common.inc:180-183` | The raw recorded `(reg, data)` stream — enough to reconstruct which addresses were driven |
| `bus_recording_saturated()` | `_shared/host_stubs_common.inc:184` | The **non-vacuity check**. Phase 194 raised the cap to 4096 behind an `#ifndef` and added this signal precisely so a boundary assertion cannot pass vacuously |

`[VERIFIED: host_stubs_common.inc:168-190]`, verbatim:

```c
#elif defined(HOST_STUBS_RECORD_BUS)
#ifndef HOST_STUBS_MAX_RECORDING
#define HOST_STUBS_MAX_RECORDING 4096
#endif
...
extern "C" bool bus_recording_saturated() { return s_bus_recording_count >= HOST_STUBS_MAX_RECORDING; }
```

Recording density is **3 records per written byte + 11 for the SDP prefix**
`[CITED: 194-RESEARCH.md §R5 probe measurements]`, so the 4096 cap saturates at ~1361 data bytes —
ample for any partial-write case (`P <= 512`).

### 5c. The oracle a partial-write test should use

Assert on **SDP signature count and position**, plus `response_code`. Concretely, for the refusal shape:

| Case | `h.address` | `h.page_size` | `h.data_size` | Must assert |
|---|---|---|---|---|
| unaligned start | `64` | `128` | `128` | `response_code == RESPONSE_CODE_ERROR` **and** `bus_recording_count() == 0` |
| non-page-multiple length | `0` | `128` | `64` | same |
| both | `64` | `128` | `64` | same |
| positive control | `0` | `128` | `256` | `RESPONSE_CODE_OK`, `count_sdp_signatures(...) == 2`, `!bus_recording_saturated()` |

`bus_recording_count() == 0` is the load-bearing half — "refuses" without "performed no write" is not
WRITE-01. This mirrors `test_5v_page_write_execute_refuses_with_no_page_size` exactly
`[VERIFIED: test_val_5v_page.cpp:342-361]`.

For an RMW shape, the same recording gives the oracle for free: the stub's
`rurp_read_data_buffer()` returns `0` `[VERIFIED: host_stubs_common.inc:225-229]`, so restored bytes
appear in the recording as additional data writes at the addresses **outside** the requested range —
a directly checkable "the page was fully loaded" assertion.

### 5d. The known traps, restated because they still bite

1. **The stubs record no time.** `delay()`/`delayMicroseconds()` are unstubbed; a trace diff cannot
   prove timing `[CITED: 194-RESEARCH.md §R5]`. Any `TBLC`-window claim is a **bench** claim, never a
   native one. Keep `data_buffer` all-zero so `flash_5v_page_wait_for_page_write`'s poll converges on
   iteration 1 (the stub read returns 0).
2. **A golden trace with matching ids can miss a WARN/ERROR fork.** A refusal must be asserted with an
   explicit negative (`RESPONSE_CODE_ERROR` **and** zero recorded writes), never by "the expected ids
   appear".
3. **Register-write elision is not modelled** under `HOST_STUBS_RECORD_BUS`; do **not** switch this
   suite to `HOST_STUBS_REAL_REGISTER_UTILS` (it redefines six symbols and would move the 15+ existing
   green cases). Key the oracle on the SDP signature, which no cache-compare can elide.
4. **Host gates that scan firmware source fail OPEN on renames.** Two app test modules read firmware
   paths — `tests/test_page_size_invariants.py` and `tests/test_py32_flash_map_host.py`
   `[VERIFIED: /usr/bin/grep for firmware paths across `firestarter_app/tests/`]`. If this phase
   renames anything in `flash_5v_page.cpp`, re-run those two specifically and confirm they still find
   their targets.
5. **`firestarter_fw/tests/test_write_path_source_contract_v131.py` scans the whole tree**
   (`_SCAN_TREE_DIRS = ("src", "include", "lib", "platform")`) for every `delayMicroseconds(...)` call
   and requires each argument to be a literal or a clamped value
   `[VERIFIED: that file, lines 216-217, 259-296, 499]`. `flash_5v_page.cpp:118` currently passes
   `delayMicroseconds(10)` — a literal. **Any new non-literal delay added by this phase trips that
   gate.**
6. **`firestarter_fw/tests/test_flash_path_record_sync.py` is RED on this branch already**, for an
   unrelated reason: it hard-codes `.planning/v1.23-FLASH-PATH-DECISION.md`, which a concurrent session
   relocated to `.planning/milestones/`. 17 failures, documented and dispositioned as out of scope
   `[CITED: .planning/phases/194-.../deferred-items.md §D1]`. **Do not read those 17 as this phase's
   regressions**, and budget for the fact that `pytest tests/` in `firestarter_fw` is not currently
   all-green.

---

## 6. Bench evidence (WRITE-03, D-4)

### 6a. The part, and why

**`W29C020`.** Confirmed from the shipped database in-session: `alg=5 page_size=128 raw=128
size=262144`, chip id `0x0000da45`, part-number row `W29C020,W29C020C,W29C022`
`[VERIFIED: in-session read of `firestarter_app/firestarter/data/chip_database.json`]`. It is row 24 of
the 27-row record, marked *"equal (already correct pre-Phase-194)"*
`[CITED: .planning/v1.39/194-page-size-27-row-record.md §1]` — so a result on it isolates gh#68 from
gh#67 exactly as criterion 3 demands, and it is the part both defects were originally reproduced on.
Board: the **Leonardo** on the operator's rig (a Leonardo is exempt from the chip-out-before-sideload
rule, so the part can stay seated across a firmware flash — 194-07 relied on this).

### 6b. The procedure

Follow `194-w29c020-bench-transcript.md`'s section structure exactly: §1 rig as the operator described
it, §2 rig identity re-confirmed (not merely trusted), §3 firmware built from source and flashed with
its `bootloader-guard` size line as attribution evidence, §4 chip-ID confirmation → pattern → write →
read-back with every command verbatim, §5 what this proves and what it does not.

**The critical sequencing point: the loss can only be demonstrated with PRE-fix firmware.** Once the
fix lands, a partial write either refuses or preserves — so criterion 3's "both loss directions are
demonstrated on real silicon" requires a **before** leg. Flash the pre-195 build first (this branch's
current tip builds it: `leonardo 23734/28672 B`), capture the loss, then flash the fixed build and
re-run the identical commands.

| Step | Command shape | Proves |
|---|---|---|
| **A. Baseline** | write a 512-byte pattern at `0x0` (4 pages of 128), `read -s 512`, `sha256sum` both | the rig and the part are good; gives the known-good reference image |
| **B. Trailing loss (PRE-fix)** | `firestarter --port <p> write W29C020 probe64.bin` where `probe64.bin` is 64 bytes of `0x55`; then `read -s 512` | bytes `0x040-0x07F` read `0xFF` though they held the baseline pattern; the CLI still printed `Write to W29C020 successful` |
| **C. Leading loss (PRE-fix)** | re-apply A, then `write W29C020 probe64b.bin -a 0x40` (64 bytes of `0x66`); `read -s 512` | bytes `0x000-0x03F` read `0xFF` — erased *before* the start address; success still reported |
| **D. Blast radius** | same read-back | pages `0x080-0x0FF` and beyond are intact — confirms the damage is confined to the touched 128-byte page, which independently re-confirms `P = 128` |
| **E. (optional) Interior loss** | re-apply a 2048-byte baseline, then `write` a 1024-byte file at `-a 0x40`; `read -s 2048` | tests §1c direction 3 — a chunk-boundary page destroyed *inside* the requested range. Never yet observed; a genuine new finding either way |
| **F. Flash the fix** | `pio run -e leonardo && pio run -t upload -e leonardo --upload-port <p>` | record the `bootloader-guard` line; re-identify the port after the 1200bps-touch reset (the node number *will* change) |
| **G. Post-fix, both directions** | repeat B and C verbatim | refusal shape: a named error, exit non-zero, **and a read-back proving the device is byte-identical to the baseline**. RMW shape: the write succeeds and the read-back equals baseline-with-the-patch-applied |
| **H. No-regression** | repeat 194-07's aligned 2048-byte / 16-page write + read-back | the fix did not break the case that works today |

**Pattern generation rule** (reuse 194-07's, it is designed to expose misplaced boundaries):
`byte[i] = ((i // 128) * 17 + (i % 128)) & 0xFF` — varies within a page and differs between adjacent
pages, so any erased run shows up as `0xFF` at a regular interval.

**Hard bench rules that apply here** (all standing project rules, restated so the plan does not
rediscover them):

- **Never pass `-b`/`--no-blank-check` or `--skip-erase` on this path.** 194-07 records the reason.
- **Confirm the part by chip-ID, never by the printed marking** (`firestarter -v --port <p> id W29C020`,
  expect `Chip ID check passed`).
- **Re-verify the port identity for every task** — `ttyACM*` numbers shuffle across replug, and the
  Leonardo bootloader touch causes exactly that. 194-07 shows the sysfs-path route that distinguishes
  "same board, new node" from "different board".
- **The shield revision is asked, never inferred** (`hw` cannot distinguish the operator's three shields).
- The `W29C020`'s two 8 KB boot blocks are **optional** and are evidently not locked on the operator's
  part (gh#68 wrote at `0x000` successfully) `[CITED: W29C020 datasheet, "8K Byte Boot Block (Optional)"]`.
  If a write at `0x000` ever refuses with a boot-block error, move the probes to a mid-device page
  instead of debugging the phase's own fix.

### 6c. Operator-only vs agent-drivable

| Step | Who | Why |
|---|---|---|
| Seating/removing the part, stating the shield revision, any photograph, any multimeter reading | **Operator only** | Standing project rule |
| Everything else — `pio run`, `pio run -t upload`, `firestarter id/write/read/verify`, sysfs port identification, hashing, diffing | **Agent, over USB passthrough** | Precedent: 194-07 ran the whole flash-and-write sequence this way |
| Flashing firmware to the bench boards | **Agent, no per-flash ask** | Standing OK: bench boards are a firmware-flash testbed |

---

## 7. Regression surface for criterion 4 — and one correction

**Where the validation is recorded:** `/workspaces/VALIDATED-EPROMS.md` at the meta-repo root, owned by
the `devtest-triage` skill. **It is generated — never hand-edit it.** The skill's own instruction:
*"The ledger is generated — never edit it by hand. `eprom_ledger.py` owns its format"*, with
`python3 .claude/skills/devtest-triage/scripts/eprom_ledger.py check` exiting 1 if the file differs
from a fresh render `[VERIFIED: .claude/skills/devtest-triage/SKILL.md §4]`.

**The rows, verbatim from the ledger `[VERIFIED: /workspaces/VALIDATED-EPROMS.md, "Validated chips" table]`:**

| Chip | Family | Size | Chip ID | Host | Firmware | Issues | Validated |
|---|---|---|---|---|---|---|---|
| AE29F2008 | PROTO_FLASH_5V_PAGE | 256 KiB | `0xDA45` | 3.0.0b37 | 3.0.0b25 | #61 | 2026-09-10 |
| W29C020 | PROTO_FLASH_5V_PAGE | 256 KiB | `0xDA45` | 3.0.0b33 | 3.0.0b22 | #52 | 2026-08-31 |
| W29C040 | PROTO_FLASH_5V_PAGE | 512 KiB | `0xDA46` | 3.0.0b33 | 3.0.0b22 | #48 | 2026-08-31 |
| SST39SF020 | **PROTO_FLASH_NOR_UNLOCK** | 256 KiB | `0xBFB6` | 3.0.0b15 | not reported | #25 | 2026-08-08 |

### ⚠ Correction the planner needs: `SST39SF020` is **not** a protocol `0x05` part

The ROADMAP criterion and gh#68 both name *"the four validated parts (`w29c020`, `w29c040`,
`sst39sf020`, `AE29F2008`)"*. Measured against the shipped database
`[VERIFIED: in-session read of `firestarter_app/firestarter/data/chip_database.json`]`:

```
ASD        AE29F2008                 alg=5 page_size=128 raw=128 size=262144
SST        SST39SF020,SST39SF020A    alg=6 page_size=None raw=0 size=262144
WINBOND    W29C020,W29C020C,W29C022  alg=5 page_size=128 raw=128 size=262144
WINBOND    W29C040,W29C042           alg=5 page_size=256 raw=256 size=524288
```

`SST39SF020` is `algorithm: 6` — `PROTO_FLASH_NOR_UNLOCK`, a sector-erase NOR part handled by
`flash_nor_unlock.cpp`, which `flash_5v_page_write_execute` never touches. **It cannot regress from
this phase's change, and it cannot be re-checked "against whatever behaviour this phase lands", because
no behaviour this phase lands applies to it.** Record this as a measured scope correction rather than
running a vacuous bench pass on it. (The claim in gh#68 that the defect affects `sst39sf020` is
incorrect for the same reason; worth a note in the issue reply.)

### What a re-check should consist of

| Part | Route | Rationale |
|---|---|---|
| **W29C020** | **Bench.** Steps A–H of §6 | It is the reproduction part, the phase's own evidence vehicle, and already on the rig |
| **AE29F2008** | **Database identity + (optional) bench** | The ledger's own Notes state: *"AE29F2008 and W29C020 are the same silicon under two names. Their database entries are identical on every field, including chip ID `0xDA45`. A finding on one applies to the other"* `[VERIFIED: VALIDATED-EPROMS.md §Notes]`. Re-check by asserting field identity of the two rows in a host test; bench only if the operator has the physical part to hand |
| **W29C040** | **Native + database check; bench only if the part is on hand** | `P = 256`, a geometry `W29C020` does not cover. The 7-geometry native boundary suite already exercises `(524288, 256)` `[VERIFIED: test_val_5v_page.cpp:450-462, `test_5v_page_write_execute_boundary_524288_256`,
driving `drive_page_boundary_case(524288, 256, 512)`]`; extend the same table with the partial-write cases and `P = 256` is covered by construction |
| **SST39SF020** | **Neither — record the scope correction** | Protocol `0x06`; out of the defect's blast radius entirely |

**Also worth a line in the record:** `dev test`'s write region is 256 bytes at address 0, which is a
whole number of pages for `P ∈ {64, 128, 256}`. All three protocol-`0x05` validated parts are in that
set, so **no validated part's `dev test` run changes under the refusal shape** — that is the cleanest
statement of criterion 4 the phase can make, and it is a measurable one.

---

## 8. Size and RAM budget

**Measured on this branch, in-session** (`pio run`, bootloader-guard line + PlatformIO memory usage):

| env | flash used | safe ceiling | margin | RAM used | RAM total | free |
|---|---|---|---|---|---|---|
| `uno` | **21 616 B** | 32 256 B (512 B bootloader reserved) | **10 640 B** | **1 394 B** | 2 048 B | **654 B** |
| `leonardo` | **23 734 B** | 28 672 B (4 096 B bootloader reserved) | **4 938 B** | **1 835 B** | 2 560 B | **725 B** |

Both figures are byte-identical to `194-06-SUMMARY.md`'s, confirming the tree is the committed one.

**Flash is not the constraint.** The comparable Phase 194 change — a validator, a refusal branch and
two mask substitutions — measured **+6 B** on each env `[CITED: 194-RESEARCH.md §R2]`. A refusal
predicate is the same order. Even `leonardo`'s 4 938 B is ample.

**RAM is the constraint, and only for shape (a)** — see §3a's measured table. Nothing in shapes (b) or
(c1) allocates firmware RAM.

**⚠ Two corrections to the brief's premises:**

1. **There is no `size_baseline.json` watermark gate on this branch.** `scripts/check_size_baseline.py`
   and `tests/test_check_size_baseline.py` were deleted by `bb9982d` *("chore: retire the never-run
   size/warnings/release gates and the sub-repo codegen drift gate")* — only stale `__pycache__` entries
   remain `[VERIFIED: `find` for `size_baseline` → only `.pyc`; `git log --diff-filter=D`]`. The only
   size enforcement is `bootloader_guard.py`.
2. `bootloader_guard.py` enforces per-env ceilings from `DEVICE_FLASH_BYTES = 32768` minus
   `BOOTLOADER_BYTES = {"uno": 512, "uno328pb": 384, "leonardo": 4096}`
   `[VERIFIED: firestarter_fw/bootloader_guard.py:14-20]` — hence leonardo's real ceiling of 28 672.
   It runs as a PlatformIO post-build hook on ELF relink, so a source-only change that does not relink
   will not re-check it. Every plan task that edits firmware source should print the guard line.

---

## 9. Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| A pre-connect write refusal | A new ad-hoc check inside `write_eprom`'s body | `page_size_gate.py`'s module shape + its two existing call sites (`cli_handlers.py:764`, `eprom_operations.py:2009`) | Pure predicate, no I/O, already proven to fire before `_operation_context`; its 9-test module is a copy-paste template |
| A typed, verbatim-rendered error | `raise EpromOperationError(...)` | A new `EpromOperationError` subclass in `exceptions.py` **plus its own `except` arm above the generic one** in `map_typed_errors` | Without the dedicated arm the message gets a `"Programmer error: "` prefix — pinned by an existing test |
| Deciding "is this a protocol 0x05 part?" | A new constant or a capability-flag test | `flash4_erase_gate.FLASH4_PROTOCOL_ID`, imported | Single-sourced across both existing gates; a flag-based predicate silently widens the refusal |
| A page mask in firmware | A new `%`-based computation | The existing `flash_5v_page_mask(uint16_t, uint32_t*)` + `page_mask` already resolved at the top of `write_execute` | Already validates 0 / power-of-two / ceiling; `%` by a variable divisor links `__udivmodsi4` and costs hot-loop cycles |
| A new native suite | A new `test_*` directory | Extend `test/native/avr/test_val_5v_page/` | Registered in both envs already; carries the SDP-signature oracle and the saturation guard |
| A new message id by hand | Editing `messages.h` / `messages.py` | `tools/catalog/messages.toml` + `bash tools/catalog/sync_to_subrepos.sh` | Both artefacts are generated; sub-repos consume, never generate |
| A page size | Any derivation from capacity | `handle->page_size` / the wire `page-size` | D-3: *"The page size comes from the database, not a second derivation."* |
| Editing `VALIDATED-EPROMS.md` | Hand-editing a row | `.claude/skills/devtest-triage/scripts/eprom_ledger.py add` / `check` | The file is generated; a hand edit fails `check` |

**Key insight:** every seam this phase needs was built one phase ago for the sibling defect. The
temptation to invent is the main risk to plan quality here, not the difficulty of the fix.

---

## 10. Common Pitfalls

### Pitfall 1: A firmware-only refusal that claims "the device is unchanged"
**What goes wrong:** the firmware refuses at the final, partial chunk — after N-1 chunks were
programmed. The plan then asserts WRITE-01's "leaves the device unchanged", which is false.
**Why:** the firmware never receives the total payload length (§3b).
**Avoid:** the *authoritative* refusal is host-side pre-connect; the firmware guard is a backstop whose
claim is narrower ("no page was partially loaded"), and the plan must word it that way.
**Warning sign:** a success criterion phrased as "the firmware refuses and the device is unchanged"
with no host-layer task.

### Pitfall 2: Testing the refusal only with a single-chunk write
**What goes wrong:** every partial-write native case uses `data_size <= 512`, so the chunk-boundary
behaviour (§1c direction 3) is never exercised and a fix that only patches the ends passes.
**Avoid:** include at least one multi-chunk case, driving `write_execute` repeatedly with an advancing
`handle->address` — the faithful model of the real chunked path, and the documented workaround for
`DATA_BUFFER_SIZE` capping one call at 512 bytes.

### Pitfall 3: Spending a new ERROR id without deciding the band
**What goes wrong:** `0xA0–0xBF` is full; a plan picks `0xC0` silently and a future reader cannot tell
whether the band was extended deliberately or by accident.
**Avoid:** record the convention in `messages.toml`'s header and close
`.planning/todos/pending/error-message-band-a0-bf-exhausted.md` in the same commit.

### Pitfall 4: Forgetting the catalog sync, or running it without `ruff`
**What goes wrong:** the firmware compiles against a stale `messages.h` (undefined id) or
`messages.py` lands unnormalised and shows formatting drift. Nothing in CI catches either.
**Avoid:** explicit sync task + `git status` check in both sub-repos; `ruff` on PATH first.

### Pitfall 5: Reading `firestarter_fw`'s `pytest tests/` red legs as this phase's regressions
**What goes wrong:** 17 pre-existing failures in `test_flash_path_record_sync.py` (a relocated
`.planning` path) get attributed to this phase.
**Avoid:** record the pre-state before the first edit; the disposition is already written up in
Phase 194's `deferred-items.md`.

### Pitfall 6: Writing any comment into product source
**What goes wrong:** a plan says "add a comment explaining the alignment rule". `/workspaces/CLAUDE.md`
forbids **all** comments in `firestarter_fw/` and `firestarter_app/` source, and says a plan cannot
override it.
**Avoid:** rationale goes in `195-SUMMARY.md`, the requirements traceability, or the commit message.
Note that Python **docstrings are not comments** (Click docstrings are user-facing `--help` text), and
the citation gate never scans them — which is how `page_size_gate.py`'s explanatory docstring is legal.

### Pitfall 7: A planning citation reaching source
**What goes wrong:** `planning_citation_gate.py` fails CI in both repos on `.planning`, `ROADMAP.md`,
`Phase 195`, `D-2`, `WRITE-01`, etc. appearing in any scanned file's **comments or code**
`[CITED: 194-RESEARCH.md §R4, gate rules quoted verbatim there]`.
**Avoid:** name nothing from `.planning/` in source, including test files under `test/` and `tests/`.

### Pitfall 8: `-a` semantics on `read` vs `write`
**What goes wrong:** a bench read-back is sliced from offset 0 of the output file.
**Why:** a region read writes real bytes at the **absolute** offset (`file_handle.seek(address)`), so
the file is hole-padded ahead of them `[VERIFIED: chip_test.py `_read_region` docstring]`.
**Avoid:** read from `0x0` with an explicit `-s` covering the whole probe window, as 194-07 did.

---

## 11. Code Examples

### The host gate to mirror (existing, working, tested)

```python
# firestarter_app/firestarter/page_size_gate.py:80-88 — VERBATIM, the shape to copy
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

### The two call sites, verbatim as they stand today

```python
# firestarter_app/firestarter/cli_handlers.py:762-766
    if not jp5_gate.confirm_or_refuse(eprom, eprom_data.get("bus-config"), "write"):
        sys.exit(1)
    page_size_gate.require_page_size(eprom, eprom_data, "write")

    ok = app.eprom_operator.write_eprom(
```

```python
# firestarter_app/firestarter/eprom_operations.py:2003-2011
        require_acknowledged(
            eprom_name,
            eprom_data_dict.get("bus-config"),
            "write",
            pin1_hazard_acknowledged,
        )
        require_page_size(eprom_name, eprom_data_dict, "write")

        with self._operation_context(
```

An alignment guard belongs immediately after `require_page_size` at both sites. At the operator layer
it has `address_str` and `input_file_path` in scope, so the payload length is
`os.path.getsize(input_file_path)` and the start is `parse_address(address_str) or 0` — the same
parser `_setup_operation` uses `[VERIFIED: eprom_operations.py:481-486]`.

### The firmware refusal to mirror (existing)

```c
/* firestarter_fw/src/proms/flash_5v_page.cpp:80-86 — VERBATIM */
void flash_5v_page_write_execute(firestarter_handle_t* handle) {
    uint32_t page_mask;
    if (!flash_5v_page_mask(handle->page_size, &page_mask)) {
        LOG_ERROR_ID_U16(MSG_ERR_FL4_PAGE_SIZE, handle->page_size);
        handle->response_code = RESPONSE_CODE_ERROR;
        return;
    }
```

### The native refusal assertion to mirror (existing)

```c
/* firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp:357-360 — VERBATIM */
    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "a write with no resolvable page size must refuse");
    TEST_ASSERT_EQUAL_MESSAGE(0, bus_recording_count(),
        "a refused write must perform zero register writes");
```

---

## 12. Open Questions — the planner decides

**U1. Which id band the new ERROR message comes from.** `0xA0–0xBF` is full (§4a). `0xC0` is
mechanically free and needs no codegen change, and the existing band guard stays green. The decision is
a project-wide catalog convention, already filed as a pending todo by Phase 194.
*Recommendation:* mint `0xC0` as `severity = "ERROR"`, record the convention in `messages.toml`'s
header comment, and close the todo in the same commit — the convention question does not get cheaper by
deferring it a second time.

**U2. The fix shape.** §3. *Recommendation:* two-layer refusal now; host-side alignment (c1) as a
separable strand. **This is the operator's call as much as the planner's** — it changes what
`firestarter write -a <unaligned>` does for real users, and D-2 makes both answers legitimate.

**U3. Whether to ship an override flag.** gh#68 suggests one. §2's trap: an override that prints the
plain success line violates WRITE-02 literally. *Recommendation:* no override in this phase.

**U4. Whether the firmware guard refuses or warns on a misaligned chunk when the host is already
aligned.** If c1 lands, every legitimate chunk is aligned, so the guard can be a hard refusal with no
false positives (§3b arithmetic). If only (b) lands, the guard is likewise never hit by a passing
host-side predicate. Either way, refusal is safe. *Recommendation:* refuse.

**U5. Whether to also close `.planning/todos/pending/host-page-size-gate-accepts-invalid-values.md`.**
That todo (filed from 194-REVIEW warning 1) asks for the host gate to apply the same power-of-two and
ceiling test the firmware applies, so the two layers agree on which page sizes are valid. It touches
the exact module this phase extends, is a few lines, and its test legs are the same shape.
*Recommendation:* fold it in — the marginal cost inside this phase is near zero and it prevents the
next reader from finding two half-agreeing predicates.

**U6. Whether direction 3 (interior chunk-boundary loss) is in scope for the bench.** It has never
been observed; it is cheap to add as bench case E; and it is the strongest single argument against any
"patch only the ends" fix. *Recommendation:* include it, and record the result either way.

---

## 13. Environment Availability

| Dependency | Required by | Available | Version | Note / fallback |
|------------|-------------|-----------|---------|-----------------|
| PlatformIO (`pio`) | firmware build + native tests | ✓ | `/usr/local/bin/pio` | `pio run -e uno` 1.8 s, `pio test -e native` 79 s |
| `avr-gcc` toolchain | both AVR envs | ✓ | via PlatformIO | both envs built and measured in-session |
| Python 3.11 interpreter | app CI floor | **✗ broken** | — | **`firestarter_app/.venv311` is dead**: its `bin/python` symlinks to `/home/vscode/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin/python3.11`, which no longer exists. Recreate with `uv venv --python 3.11` (downloads 3.11.16, ~29 MiB) |
| `uv` | recreating the 3.11 venv | ✓ | `/usr/local/bin/uv` | **must set `UV_CACHE_DIR`** — `~/.cache/uv` is not writable and `uv` fails hard with `Permission denied (os error 13)`. Same class as the `gh run view` cache trap |
| Devcontainer default Python | — | ✓ | 3.12.14 | **Masks app CI**, which is 3.11. Do not run the host suite on 3.12 and call it green |
| `ruff` | `sync_to_subrepos.sh` normalisation | **✗ on PATH** | 0.16.7 inside a `.[test]` venv | Without it the sync prints a WARNING and writes unnormalised `messages.py`. Prepend the venv `bin` to PATH before syncing |
| `gh` | reading gh#68, replying on the issue | ✓ | — | **set `XDG_CACHE_HOME`** for `gh run view --log`; `issue view` and `api` are unaffected |
| `pdftotext` | datasheet inspection | ✗ | — | Fallback used and proven this session: `pip install --target <dir> pypdf` then `PdfReader(...).extract_text()` |
| Bench rig (Leonardo + Rev 2.0 shield + W29C020) | WRITE-03 | operator-held | — | Present and used by 194-07 on 2026-09-15. Port node number is not stable across replug |
| Network egress (PyPI, datasheet mirrors) | venv creation, datasheets | ✓ | — | both exercised in-session |

**Missing with no fallback:** none.
**Missing with fallback:** Python 3.11 venv (recreate), `ruff` on PATH (use the venv), `pdftotext`
(use `pypdf`).

**No external packages are installed by this phase**, so the Package Legitimacy Audit is not
applicable: the firmware adds no library, and the host change uses only the standard library and
modules already in `firestarter_app`. If a plan proposes any new dependency, run the legitimacy gate
before accepting it.

---

## 14. Project Constraints (from CLAUDE.md and the CI gates)

1. **No comments in product source, at all.** `/workspaces/CLAUDE.md` § "Source code comments — hard
   rule": *"Write no comments into product source"* under `firestarter_fw/` and `firestarter_app/`,
   *"not overridable by a plan, task, skill, or subagent instruction"*. Planners must not write
   "add a comment citing X" into a plan, and "a comment exists" must not be an acceptance criterion.
   Docstrings are exempt; Click docstrings are user-facing `--help` text.
2. **No planning citations in scanned source.** `planning_citation_gate.py` runs in both sub-repos' CI
   over `firestarter tests tools` (app) and `src include test tests scripts platform tools ...`
   (firmware). Forbidden: `.planning`, `ROADMAP.md`/`REQUIREMENTS.md`/`STATE.md`, `Phase NNN`,
   `D-NN`-style decision ids, `XXXX-NN` requirement ids. Python docstrings are never scanned.
3. **`chip_database.json` is GENERATED** — never hand-edited; fix `tools/build_db.py` and regenerate.
   (This phase should need no database change at all: D-3 and Phase 194 already delivered the page size.)
4. **Messages are generated only in the meta repo**; sub-repos consume synced artefacts.
5. **`VALIDATED-EPROMS.md` is generated** by `eprom_ledger.py`; `check` fails on a hand edit.
6. **Branching:** work on `v1.39-protocol-0x05-write-correctness` in **all three** repos — already true
   this session `[VERIFIED: `git branch --show-current` in all three]`. Never `beta`, never `main`.
   `main` is protected in all three repos; this project's close targets `beta`.
7. **Gitlink advances per phase** since v1.36 — expect to advance both submodule pointers in the meta
   repo as part of this phase's commits.
8. **`git clean -Xdf` is forbidden** here — it destroys GSD state and bench artefacts. Remove scratch
   files by explicit path.
9. **App CI floor is Python 3.11** with `--cov-fail-under=70`; `firestarter_app/tools/` is outside
   `ruff` and `mypy` scope, so hold any change there to the same standard by hand.
10. **The devcontainer `grep` is ugrep and honours `.gitignore`** — it silently under-scans. Use
    `/usr/bin/grep` or a `bash` script for any gate evidence. (All greps in this document used
    `/usr/bin/grep`.)

---

## 15. Security Domain

| ASVS category | Applies | Control |
|---|---|---|
| V5 Input Validation | **yes** | The new alignment predicate is itself a validation control, and it must be **fail-closed**: absent or unparseable inputs (no page size, unreadable file, unparseable `-a`) must refuse, never proceed. `page_size_gate.py`'s docstring states the polarity to copy, deliberately the opposite of `flash4_erase_gate`'s fail-open. The firmware's `page_size` field already saturates at `0xFFFF` at parse time and is rejected by the validator |
| V2/V3/V4 Auth / Session / Access control | no | No network surface, no identity, no multi-user state |
| V6 Cryptography | no | The write path carries a CRC8-CCITT integrity check on data frames, not a security control |
| V12 File handling | **yes, narrowly** | The payload length now becomes a **control input**, not just data. `os.path.getsize` on a path the user supplied is the input; a symlink or a file that changes between the size check and the read would defeat the predicate. Low severity (local, single-user tool) but worth a note: read the size from the opened handle where practical |

**Threat model for this phase, stated plainly:** the adversary is not a person; it is a silent
data-destroying default. The STRIDE category is **Tampering** (data destroyed without the operator's
intent) compounded by **Repudiation** (the tool reports success, so nothing records that it happened).
The control is refusal plus an honest outcome line. Untrusted-input surfaces touched: the chip name and
`-a` value from the CLI, the wire dict from the database (including `~/.firestarter/database.json`
overrides, which bypass `build_db.py`'s validator — see U5), and the firmware's `page_size` field from
the JSON parser.

---

## 16. Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | The other 26 protocol `0x05` parts share the W29C020's "unloaded bytes erase to `0xFF`" page-write semantics | §1b | Low. It is the defining property of the JEDEC 5 V page-write class (it is why `FLAG_CAN_ERASE` is cleared for this protocol), and the AT29C020 datasheet independently states sector-based reprogramming with the whole sector loaded and simultaneously programmed. But only the W29C020 datasheet was read verbatim this session |
| A2 | The `TBLC` window (200 µs on W29C020; ~150 µs quoted for the AT29 family) makes a mid-page-load device read impossible | §3a | **Medium and load-bearing** — it is the reason firmware RMW needs a whole-page staging buffer. It follows directly from the quoted datasheet sentence ("the page load cycle will be terminated ... if no additional byte is loaded"), but no one has attempted a mid-load read on silicon to falsify it. A falsification attempt is a bench experiment, not a plan blocker; the RAM measurement independently rules out the 512-byte case regardless |
| A3 | Interior chunk-boundary loss (§1c direction 3) occurs on silicon | §1c, §6 case E | Low risk to the phase — it is derived from source read verbatim plus A1. It has never been observed. If wrong, it removes one bench case and one argument; it changes no recommendation |
| A4 | A 512-byte staging buffer would overflow the stack on `uno`/`leonardo` | §3a | Low. 142 B / 213 B of remaining RAM for the whole call stack is not a judgement call. Not falsified by running it — the measurement is of `.data + .bss`, and no stack-depth profile was taken |
| A5 | `dev test` is the only non-CLI caller that issues protocol `0x05` writes | §3b | Low. Grepped `write_eprom` call sites across `firestarter_app/firestarter/`; `chip_test.py` and `cli_handlers.py` are the callers found |
| A6 | Host-side region reads are accurate enough to build a read-modify-write on (shape c1) | §3c | Medium, and only if c1 is chosen. 194-07's 2048-byte read-back was byte-identical, which is evidence for it, but a c1 plan should verify a head/tail page read explicitly before relying on it |

---

## 17. Sources

### Primary (measured in-session, HIGH confidence)
- `firestarter_fw/src/proms/flash_5v_page.cpp` (whole file), `src/eprom_operations.cpp:110-170`,
  `src/proms/memory.cpp:39-120,319-372`, `include/firestarter.h:175-200`, `include/logging_id.h:1-130`,
  `src/json_parser.c` (address/page-size FIELD rows), `bootloader_guard.py`
- `firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp`,
  `test/native/avr/_shared/host_stubs_common.inc:160-240`
- `firestarter_app/firestarter/page_size_gate.py`, `exceptions.py`, `cli_handlers.py:578-790`,
  `eprom_operations.py:380-560, 735-845, 1968-2105`, `chip_test.py:2112-2133, 2448-2476, 2860-2915`
- `firestarter_app/firestarter/data/chip_database.json` (in-session enumeration of all 27
  `algorithm: 5` rows and the four ledger parts)
- `/workspaces/tools/catalog/messages.toml` (in-session full parse: 132 messages, per-band free lists),
  `tools/catalog/sync_to_subrepos.sh`, `tools/catalog/codegen.py:268-272`
- `/workspaces/VALIDATED-EPROMS.md`, `.claude/skills/devtest-triage/SKILL.md`
- Builds and suites run in-session: `pio run -e uno`, `pio run -e leonardo`, `pio test -e native`
  (208/208), `firestarter_app` full pytest on 3.11.16 (1896 passed), and the reversible 128/256/512-byte
  RAM experiments (file restored, `md5sum` and `git status --porcelain` re-verified)
- `gh issue view 68 -R henols/firestarter` — the defect report with its bench evidence

### Secondary (documents read this session, MEDIUM confidence)
- W29C020 datasheet, Winbond, Revision A3 (Feb 1998), 21 pages — fetched and text-extracted in-session
  from the mirror `https://www.tvsat.com.pl/pdf/w/w29c020_win.pdf`. Quoted verbatim in §1b.
  Manufacturer-original copies also indexed at `https://www.100y.com.tw/pdf_file/W29C020C.pdf` and
  `https://datasheet.octopart.com/W29C020C-90B-Winbond-datasheet-181529584.pdf`
- `.planning/phases/194-.../194-RESEARCH.md` (§R2 flash deltas, §R3 catalog mechanics, §R4 gate sweep,
  §R5 native harness), `194-CONTEXT.md`, `194-07-SUMMARY.md`, `deferred-items.md`
- `.planning/v1.39/194-page-size-27-row-record.md`, `.planning/v1.39/194-w29c020-bench-transcript.md`
- `.planning/todos/pending/error-message-band-a0-bf-exhausted.md`,
  `host-page-size-gate-accepts-invalid-values.md`, `new-host-old-firmware-0x05-page-size-skew.md`

### Tertiary (LOW confidence, not relied on)
- WebSearch summaries of AT29C040/AT29C family programming behaviour — used only as corroboration for
  A1; no claim in this document rests on them alone
- `.planning/graphs/graph.json` queried for `flash_5v_page` and `page_size`; **the graph is 26 h stale
  (`stale: true`)** and still lists the deleted `flash_5v_page_page_size` symbol and pre-194 test names.
  Treat its semantic relationships as approximate; nothing here was derived from it

### Not consulted
- The 9 previously under-sized parts' datasheets (not this phase's subject)
- `origin/beta` firmware history (Phase 194 already established the fix is not on `beta`)

---

## 18. Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| Defect mechanism and code sites | HIGH | Source read verbatim this session; datasheet quoted verbatim; silicon evidence in gh#68 |
| Where `successful` is reported | HIGH | Full chain read, line by line |
| Fix-shape comparison | HIGH on the constraints (RAM measured, protocol-length gap verified, `dev test` region verified), **recommendation-level** on the choice |
| Message catalog state | HIGH | Full in-session parse; band exhaustion independently confirmed by an existing host test |
| Native test surface | HIGH | Harness read; 208/208 re-run this session |
| Bench procedure | MEDIUM-HIGH | Modelled on an executed transcript from 2026-09-15; the pre-fix reproduction leg has not itself been rehearsed |
| Regression surface | HIGH | Ledger and database both read; the `SST39SF020` protocol correction is measured, not inferred |
| Size/RAM budget | HIGH | Measured on this branch, both envs, with the experiment reverted and byte-identity re-confirmed |

**Research date:** 2026-09-16
**Valid until:** ~2026-10-16 for the code-site claims (stable, single-branch), or until the next commit
touching `flash_5v_page.cpp`, `page_size_gate.py`, `messages.toml` or `chip_database.json` — whichever
comes first. The RAM/flash figures are valid for firmware HEAD `c2b8baa` and must be re-measured after
any firmware change.
