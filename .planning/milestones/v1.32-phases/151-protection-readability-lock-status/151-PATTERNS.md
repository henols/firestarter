# Phase 151: protection-readability-lock-status — Pattern Map

**Mapped:** 2026-08-20
**Files analyzed:** 24 (9 new host files + 2 new host fixtures + 13 modified across both sub-repos + meta `messages.toml`)
**Analogs found:** 22 / 24 (2 have **no analog — must be authored**: the three-axis literal-table gate rules, and the `(class_token, reason)` two-function split)

> Names below in `<angle>` form are *proposed* names, offered so the planner has one concrete
> vocabulary instead of a placeholder. Substitute freely; the structural claims do not depend on them.
>
> Proposed names used throughout: module `firestarter_app/firestarter/protection_readability.py`;
> command-layer module `firestarter_app/firestarter/lock_status.py`; gate
> `firestarter_app/tools/check_protection_readability_invariants.py`; firmware `CMD_READ_PROTECTION`.

---

## File Classification

| New/Modified file | Role | Data flow | Closest analog | Match |
|---|---|---|---|---|
| `firestarter_app/firestarter/protection_readability.py` (new) | curated-data model + pure predicate | transform (pure) | `firestarter_app/firestarter/sdp_capability.py` | **role-match, one-axis→three-axis gap** |
| `firestarter_app/firestarter/lock_status.py` (new, see §3) | service (response-consuming classifier) | request-response | `firestarter_app/firestarter/sdp_honesty.py:67-92` | role-match |
| `firestarter_app/tools/check_protection_readability_invariants.py` (new) | AST source-scan gate | batch/transform | `firestarter_app/tools/check_sdp_capability_invariants.py` | **exact for scaffolding, no analog for the new rule shapes** |
| `firestarter_app/tests/test_check_protection_readability.py` (new) | test (subprocess gate pairing) | file-I/O + subprocess | `firestarter_app/tests/test_check_sdp_capability.py` (9 legs) | exact |
| `firestarter_app/tests/fixtures/planted_protection_permit_by_default.py` (new) | test fixture (planted violation) | — | `firestarter_app/tests/fixtures/planted_permit_by_default.py` | exact |
| `firestarter_app/tests/fixtures/planted_protection_widenable.py` (new) | test fixture (planted violation) | — | `firestarter_app/tests/fixtures/planted_widenable_allowset.py` | exact |
| `firestarter_app/tests/test_lock_status_class_partition.py` (new, **D-12**) | test (invariant over DB) | batch | `firestarter_app/tests/test_sdp_db_invariant.py` (census literals + `test_partition_flags_a_moved_chip_via_db_field_non_vacuous:629`) | exact |
| `firestarter_app/tests/test_lock_status_resolution.py` (new) | test (unit, table-driven) | transform | `firestarter_app/tests/test_sdp_capability.py` | exact |
| `firestarter_app/tests/test_lock_status_cli.py` (new) | test (CLI surface matrix) | request-response | `firestarter_app/tests/test_dev_group_channel_gating.py` + `tests/test_cli_handlers.py` | role-match |
| `firestarter_app/tests/test_lock_status_wire.py` (new) | test (frame build/parse) | request-response | `firestarter_app/tests/test_revision_constants_parity.py` (parity) — **frame-level: no direct analog, closest is any `serial_comm` unit suite** | partial |
| `firestarter_app/tests/test_protect_flags_doc_measurements.py` (new, DATA-06) | test (doc↔DB invariant) | file-I/O + batch | `firestarter_app/tests/test_b15_page_size_corroboration.py` (untouched guard at `:246`) | exact |
| `firestarter_app/tests/test_protection_table_citations.py` (new) | test (invariant over doc) | file-I/O | `firestarter_app/tests/test_lockable_proms_doc_claims.py:63/85/114/129` | exact |
| `firestarter_app/firestarter/cli_handlers.py` (mod) | controller | request-response | itself, `:1471-1507` (`dev addr`) | exact |
| `firestarter_app/firestarter/channel.py` (mod) | config | — | itself, `BETA_ONLY_DEV_COMMANDS:57-64` | exact |
| `firestarter_app/firestarter/sdp_honesty.py` (mod) | utility (prose carrier) | — | itself, `:67-92` | exact |
| `firestarter_app/firestarter/constants.py` (mod) | config | — | itself, `:77-102` | exact |
| `firestarter_app/doc/infoic-field-dictionary.md` (mod) | doc | — | itself, `### page_size` at `:241-249` | exact |
| `firestarter_app/doc/package-details.md`, `doc/protocol-flags.md` (mod) | doc pointers | — | **no in-tree one-line-pointer precedent** — see §5 | none |
| `firestarter/include/firestarter.h` (mod) | config (wire enum) | — | itself, `CMD_SDP_UNLOCK/LOCK:85-86` + `is_memory_cmd:135-142` | exact |
| `firestarter/src/firestarter.cpp` (mod) | middleware (admission) | request-response | itself, `:77` ordinal gate | exact (but see §4a) |
| `firestarter/src/proms/flash_utils.{cpp,h}` (mod) | utility (bus sequences) | file-I/O-like (bus) | `flash_util_get_chip_id` at `flash_utils.cpp:81-87`; `byte_flip_t` tables at `flash_utils.h:30-59` | exact |
| `firestarter/src/proms/flash_nor_unlock.cpp`, `flash_5v_page.cpp` (mod) | dispatcher arms | event-driven | `configure_flash_nor_unlock:31-51` / `configure_flash_5v_page:40-59` | exact |
| `firestarter/scripts/check_size_baseline.py` (mod) | config (adjudicated literal) | — | `MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES` block, `:186-240` | exact |
| `firestarter/tests/test_check_size_baseline.py` (mod) | test (tripwire fixtures) | file-I/O | itself (`fullflash` family) — **sever onto a new `*_v151*` family** | exact |
| `tools/catalog/messages.toml` (meta, mod) | config (codegen source) | — | existing `MSG_ERR_*` rows | exact |

---

## Pattern Assignments

### 1. `firestarter_app/firestarter/protection_readability.py` — THE consequential mapping

**Analog:** `firestarter_app/firestarter/sdp_capability.py`. Do not re-read the whole file; the four
load-bearing shape facts are:

1. **Module docstring is lettered provenance** — `(a)`…`(h)` paragraphs at `sdp_capability.py:1-41`,
   each one a separate claim (fail-closed rationale, source commit + axis, counts, "nothing reads it at
   runtime", derivation-artifact path, ground-truth probes, negative controls, future-generation note).
   The new module's letters change subject: source is `doc/lockable-proms.md` §Key vocabulary + per-row
   datasheets, and the "counts" letter carries the 126-family/`0x05`/`0x06` census.
2. **Import purity, asserted as a literal invariant** — `:45-51`: top-level imports are a subset of
   `{__future__, typing}`, with `Mapping` deliberately taken from `typing` (`# noqa: UP035`) *to keep the
   invariant literal*. Copy this comment-plus-noqa verbatim; an existing AST purity test asserts it.
3. **One literal collection per axis, each bound exactly once** — `SDP_CAPABLE_TOKENS:79-158`,
   `FRAM_TOKENS:165`, `PRE_SDP_NAMED_TOKENS:170-185`. Vendor names are *comments inside the display*
   (`# ATMEL`, `# CATALYST(CSI)`), which is where per-row citations go.
4. **Reason fragments are module constants** — `:187-193` (`REASON_NOT_FOUND` …), so tests assert stable
   substrings, never sentences.

**The generalisation the analog cannot give you (one-axis boolean → three-axis, three-state).**
`sdp_capability.py` holds ONE literal `frozenset` and the gate's Class 2(b) is written for exactly that
shape (`_is_clean_frozenset_of_literals_call`, `check_sdp_capability_invariants.py:220-232`). Two viable
containers, with the gate consequence spelled out:

**Option A (recommended) — set-per-readability-state + two reporting-only mappings.**

```python
READABILITY_STATES: tuple[str, ...] = (
    "documented-readable", "documented-not-readable", "undocumented",
)

# W29C020C — lockable-proms.md §1 "Yes—special, read boot-block status in
# Product ID mode"; Winbond W29C020C datasheet rev. <r>, §<s> p.<p>.
DOCUMENTED_READABLE_TOKENS: frozenset[str] = frozenset({"W29C020C", ...})
DOCUMENTED_NOT_READABLE_TOKENS: frozenset[str] = frozenset({...})
```

- **Gate cost: zero new AST rules for the readability axis.** Each symbol is checked by the *existing*
  `_is_clean_frozenset_of_literals_call` + `_module_level_token_set_bindings` logic, parameterised over a
  `_TOKEN_SET_NAMES` tuple instead of the single `_TOKEN_SET_NAME` at `check_sdp_capability_invariants.py:90`.
  `undocumented` needs no set — it is the *complement*, which is exactly what makes it fail-closed.
- Mechanism and permanence do not gate answering (D-06 keys only on readability), so they may live in a
  literal `dict` display (mechanism/permanence) consumed only by prose. The gate rule for them is
  weaker-by-design and that must be *stated* in the gate docstring, not left implicit.

**Option B — one `PROTECTION_TABLE: Mapping[str, tuple[str, str, str]]` literal dict.**
Reads better as a table (one row = one family, three axes adjacent) but requires a **new, authored**
Class 2(b′): `_is_literal_str_to_tuple_of_str_mapping` — an `ast.Dict` whose every key is a string
`Constant` and every value an `ast.Tuple` of string `Constant`s, additionally asserting each value tuple's
element 1 ∈ `READABILITY_STATES`. Also breaks Class 1(a) dominance detection: `PROTECTION_TABLE[token][1]`
is a `Subscript`, not a `Compare`, so `_is_membership_test_against_token_set`
(`check_sdp_capability_invariants.py:100-109`) would no longer fire and the permit path would look
undominated. Option B is only safe if the resolution code is *required* to spell the guard as
`if token not in PROTECTION_TABLE:` first.

**Recommendation for the planner:** Option A. It preserves the gate's strongest existing property
(literal-`frozenset`-only) for free on the one axis that gates behaviour, and confines invention to a
documented-as-weaker reporting mapping.

---

### 2. The AST gate pair

**Analogs:** `firestarter_app/tools/check_sdp_capability_invariants.py` (364 lines) +
`firestarter_app/tests/test_check_sdp_capability.py` (248 lines, 9 legs) +
`firestarter_app/tests/fixtures/planted_permit_by_default.py` / `planted_widenable_allowset.py`.

**Gate skeleton to copy, in order** (`check_sdp_capability_invariants.py`):
- `:1-65` docstring: violation classes enumerated `Class 1(a)/(b)`, `Class 2(a)/(b)/(c)`, then an
  explicit **"Anti-hollow contract"** paragraph naming the paired test file and both fixture paths, then
  an **"Exit codes"** paragraph. All four parts are load-bearing convention.
- `:76-87` the env-override seam — `_HERE = os.path.dirname(__file__)`, a `_DEFAULT_*_SRC` joined
  `_HERE/".."/firestarter/<mod>.py`, then `os.environ.get("FIRESTARTER_<X>_SRC", _DEFAULT_*_SRC)`.
  ⚠ The `_HERE`-relative default is fine here (`tools/` is a fixed sibling of `firestarter/`); this is
  **not** the `check_permitted_claims.py` `_HERE` failure mode D-12 rules out, because the target is not
  phase-relative.
- `:310-360` `main()`: fail-closed on missing file → `ERROR:` on **stderr** + rc 1; fail-closed on
  `SyntaxError`; fail-closed on symbol-count ≠ 1 (`:244-250`); PASS line **names the resolved relpath and
  the binding count** (`:355-359`).
- `_print_bucket` (`:302-307`) caps output at 20 with an `... and N more` tail.

**Invocation seam (measured):** the paired test shells out — `test_check_sdp_capability.py:58-68`:
`subprocess.run([sys.executable, "tools/check_<gate>.py"], cwd=str(_FA_DIR), env={**os.environ, **overrides})`,
with `_FA_DIR = Path(__file__).parent.parent`. It also *imports* `_DEFAULT_SDP_CAPABILITY_SRC` from the
tool (`:48`) purely for leg 2's "default target exists on disk" non-vacuity check. There is **no** CLI
entry point and no pytest-internal call of `main()`.

**Nine legs to mirror** (`test_check_sdp_capability.py` docstring `:14-36`): clean-pass; default-target-exists;
PASS-line-names-file; Class 1 planted; Class 2 planted; Class 1 fixture *also* reports bare-except (one
violation must not mask the other); clean fixture through the same seam still passes; missing path
fail-closed; zero-symbol fail-closed. Legs 7-9 write their fixtures inline to `tmp_path`; only legs 4-6
use committed fixture files.

**What a planted fixture actually contains** (both are ~30 lines, import nothing from `firestarter`):
- `planted_permit_by_default.py:19-30` — a real `SDP_CAPABLE_TOKENS = frozenset({"AT28C256"})`, then a
  function preserving the production tuple-return shape whose only `return` is `True, f"..."` with **no**
  `in SDP_CAPABLE_TOKENS` compare earlier in the body, plus a `except:  # noqa: E722` planted for Class 1(b).
- `planted_widenable_allowset.py:19-30` — Class 2(b) as `frozenset(token for token in _load_tokens_from_somewhere())`
  (generator over a runtime call), then Class 2(c) as `SDP_CAPABLE_TOKENS |= frozenset({"EXTRA_WIDENED_TOKEN"})`.
- Both docstrings open with *"Deliberately-violating fixture … This file must never be imported."*

For 151, `planted_protection_permit_by_default.py` must return the **class token literal**
`"unprotected"` (not `True`) undominated — that is simultaneously the Class-1 fixture and D-12 leg 4's
required planted fixture, so one file serves both if the gate's Class 1(a) is generalised from
"tuple whose first element is `True`" to "tuple whose first element is a string `Constant` in
`_SILICON_ONLY_TOKENS = frozenset({"protected", "unprotected"})`".

---

### 3. `(bool, reason)` → `(class_token, reason)`, and where the split falls

**Analog, exact current shape** — `sdp_capability.py:210-272`:

```python
def sdp_capability_for_entry(entry: Mapping[str, Any] | None, display_name: str) -> tuple[bool, str]:
    if not entry: return False, f"{display_name.upper()}: {REASON_NOT_FOUND}"
    if "protocol-id" not in entry: raise KeyError(...)          # :229-238, hard-fail, 10-line message
    if entry["protocol-id"] != SDP_PROTOCOL_ID: return False, (...)
    tokens = split_part_number_tokens(entry.get("name") or display_name)
    if any(t in FRAM_TOKENS for t in tokens): return False, (...)
    unrecognised = [t for t in tokens if t not in SDP_CAPABLE_TOKENS]
    if unrecognised:
        described = [f"{t} (pre-SDP generation)" if t in PRE_SDP_NAMED_TOKENS else f"{t} (unrecognised)" ...]
        return False, f"...{REASON_NOT_CAPABLE}: {', '.join(described)}. ..."
    return True, f"{display_name.upper()}: {REASON_ALLOWED}"
```

Two reusable specifics: the **guard cascade returns early per refusal reason** (no single exit), and the
`described` list comprehension is precisely the mechanism D-06 needs — it already *names the offending
tokens with a per-token annotation*. For 151 the annotation becomes the alias's readability state, which
is how the `W29C022` leg and the C-6 "set of aliases in different states" leg are both satisfied by one
comprehension. Also copy the thin name-keyed wrapper at `:275-290` (`sdp_capability(chip_name, db)`).

**The split, named.** `protected`/`unprotected` must be structurally unreachable from the pure path
(D-12 leg 4), so:

| Function | Home | Signature | May return |
|---|---|---|---|
| `protection_gate_for_entry` | `protection_readability.py` (pure; no serial, no click) | `(entry: Mapping[str, Any] \| None, display_name: str) -> tuple[str, str]` | `read_permitted`, `not_readable`, `not_implemented`, `undocumented_alias`, `no_mechanism` |
| `classify_protection_response` | `lock_status.py` (response-consuming) | `(gate_token: str, response: bytes \| Mapping, *, forced: bool) -> tuple[str, str]` | `protected`, `unprotected`, `unadjudicated_probe`, `firmware_outdated` |

`read_permitted` is a **gate** token, not one of D-09's eight output classes — the CLI never prints it.
That asymmetry is what makes the AST leg non-decorative: the gate asserts the literals `"protected"` and
`"unprotected"` never appear as (or inside) a `Return` value anywhere in `protection_readability.py`.

**Exit-code mapping (D-10)** belongs beside `classify_protection_response`, as an explicit literal dict
`str -> int` — **not** a `max()` over severities. Precedent for why: `dev test`'s
`max(1,2)` precedence defect. Mirror `cli_handlers.py`'s existing terminal idiom `sys.exit(0 if ok else 1)`
by widening to `sys.exit(_EXIT_BY_CLASS[token])`.

**Refusal prose (D-11).** `sdp_honesty.py` is 92 lines, three functions, and the shapes to copy are:
`unreadable_state_caveat():33-42` returns the sentence *alone* (a caveat clause with no preamble);
`emission_summary():45-64` **composes** it by calling it rather than duplicating (`:63`) and uppercases
`chip_name` itself; `map_unknown_cmd_to_outdated():67-92` keys on `exc.error_code != MSG_ERR_UNKNOWN_CMD`,
**returns** a constructed `FirmwareOutdatedError` (never raises) so the caller owns `raise ... from exc`,
and ends its message with `"upgrade with 'firestarter fw --install'."`. D-04's generalisation is a
`mode: str` → operation-label widening of `:89-91`'s f-string, or a sibling with the same return-not-raise
contract. Its import-set invariant comment (`:22-28`, "no `click`") must survive the edit.

---

### 4. Firmware

**a. Wire enum + admission.** `firestarter.h:58-92` is a flat `#define` ladder ending at
`CMD_HW_VERSION 15`; `is_memory_cmd()` at `:135-142` is a `switch` of bare `case CMD_*:` labels (literal
set `{1,2,3,4,5,6,9,10}`, pinned by `firestarter/tests/test_cmd_admission.cpp:66`). The new
`CMD_READ_PROTECTION 16` needs (i) the define with a comment in `CMD_SDP_LOCK`'s style, (ii) a `case`
in `is_memory_cmd` — noting `rurp_pinmap_guard.h:37-63` *delegates* to `is_memory_cmd` so the provisional-
pinmap refusal follows automatically, and `tools/check_is_memory_cmd_no_ifdef.py` forbids any preprocessor
conditional inside the predicate body, (iii) the ordinal parse gate at `firestarter.cpp:74`
(`if (handle->cmd < CMD_READ_VPP)`) — RESEARCH §"The ordinal parse gate" `:487-543` settles the fork as
option (a), `is_memory_cmd(handle->cmd) || handle->cmd < CMD_READ_VPP`. The second ordinal range at
`firestarter.cpp:132-142` gates debug lines only and its own comment says it was deliberately not
converted; leaving it is consistent, but a cmd-16 command then produces no debug output — state that
choice rather than discovering it on the bench.

**b. Dispatch arm shape.** `configure_flash_nor_unlock` (`flash_nor_unlock.cpp:31-51`) and
`configure_flash_5v_page` (`flash_5v_page.cpp:40-59`) are identical in form:

```c
void configure_flash_nor_unlock(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_FLASH);
    handle->firestarter_operation_init = flash_nor_unlock_generic_init;   // 0x06 only
    switch (handle->cmd) {
    case CMD_CHECK_CHIP_ID:
        handle->firestarter_operation_init = NULL;
        handle->firestarter_operation_main = flash_nor_unlock_check_chip_id_execute;
        break;
    }
}
```

`CMD_CHECK_CHIP_ID` is the arm to copy: it is the only *query* arm — it nulls `operation_init` and sets
only `operation_main`. A new `case CMD_READ_PROTECTION:` arm in each of the two files, pointing at
`flash_<family>_read_protection_execute`, is the whole dispatch change. Note `flash_5v_page.cpp` has no
`operation_init` default, so its arm omits the `= NULL` line.

**c. Sequence + table shape.** `flash_utils.h:30-59` — every table is
`const byte_flip_t <NAME>[] = { {0x5555, 0xAA}, {0x2AAA, 0x55}, {0x5555, <opcode>}, };`, i.e. the
AMD/JEDEC two-byte unlock prefix plus one opcode byte; `FLASH_DISABLE_WRITE_PROTECTION:53-59` shows the
six-entry double-prefix form. Emission is
`flash_util_byte_flipping(handle, TABLE, sizeof(TABLE)/sizeof(byte_flip_t))`, whose body
(`flash_utils.cpp:22-28`) brackets the flips with `CTRL_READ_WRITE, 0` on both sides. The read to copy is
`flash_util_get_chip_id` (`flash_utils.cpp:81-87`) — five lines: `flash_execute_command(FLASH_ENABLE_ID)`,
two `handle->firestarter_get_data(handle, 0x0000/0x0001)`, `flash_execute_command(FLASH_DISABLE_ID)`. A
protect-verify read is *that function with a different read address*, so declaring it beside
`flash_util_get_chip_id` in `flash_utils.h:65-69` (which documents itself as shared between
`flash_nor_unlock` and `flash_5v_page` "to avoid duplicating the sequence") is both the byte-cheapest and
the precedented placement. `flash_util_check_chip_id_execute:88-104` is the model for the
`FLAG_FORCE`-downgrades-error-to-warning convention D-07 reuses
(`is_flag_set(FLAG_FORCE)` → `LOG_WARN_ID_BYTES` + `RESPONSE_CODE_WARNING`, else `LOG_ERROR_ID_BYTES` +
`RESPONSE_CODE_ERROR`).

**d. The third MERGE-05 exemption — exact textual shape.** `check_size_baseline.py:186-240`. An exemption
is a **~55-line comment block above a one-line constant**, in this fixed order:

1. Phase + requirement attribution, and the single-consumer claim
   (*"the single place this literal lives is `_merge05_flash_allowance()` below"*).
2. **"What the N bytes ARE"** — an itemised inventory of the code that grew, each item named, plus the
   **SHA attribution**: *"from this phase's own firmware commits 58c6a3c (…) and 28bf089 (…)"*, plus
   *"Measured at exactly +210 B on all three AVR targets (uno, uno328pb, leonardo) against BASE-01, minus
   the already-admitted 96 B defect-fix exemption above"*, plus a pointer to the phase's own
   `…-SIZE-TRANSCRIPTS.md` *"for the cold `rm -rf` + `pio run` capture this figure was read from"*, plus
   an explicit zero-byte note for anything considered and measured at 0.
3. **"WHY an exemption"** — three named rejected alternatives, each as its own `- NOT …` bullet:
   NOT a re-anchor of `size_baseline_base01.json` (with BASE-01's byte figures restated inline:
   *"uno 24824, uno328pb 24874, leonardo 26906"*), NOT a widening of `MERGE05_UNO_CLASS_FLASH_BAND`
   (stays 64 B) or the leonardo 0 B band, NOT a shrink of the feature.
4. *"The growth is instead NAMED here, so it is admitted in one visible, attributable place rather than
   laundered into a moved reference point."*
5. **"The tripwire stays ARMED at the new floor"** — naming the exact test that proves it and the
   arithmetic: *"`test_policy_merge05_fires_on_leonardo_growth` feeds a planted log one byte past the new
   leonardo allowance (0 + 96 + 210 = 306 B) and asserts exit 1."*
6. **SCOPE line** (flash only / RAM handled by the separate constant immediately below).
7. An Evidence-Ceiling sentence: *"The change this constant funds is software-proven and unvalidated on
   silicon … no AT28C part was involved."* For 151 this becomes the D-03/leg-D wording
   (`0x06` unrun on silicon; `0x05` a capped probe).
8. `MERGE05_<NAME>_EXEMPTION_BYTES = <N>`.

Then **`_merge05_flash_allowance()`** (`:405-419`) — the sole consumer. Its docstring at `:400-412`
states the never-sum rule (*"returned SEPARATELY, never summed into one another, so every message can
show the full decomposition"*). A third exemption widens the return tuple to 5+ values and the
`allowance = band + defect_exemption + seam_exemption + <new>` line, and every message string in
`compare_avr_policy_merge05` (`:441-460`) must print the new term. If the new bytes also move RAM, the
paired `MERGE05_*_RAM_EXEMPTION_BYTES` + `_merge05_ram_allowance()` (`:422-432`) is the precedent —
note that resolver currently returns a *single* label, so a second RAM exemption is a real change of shape.

**e. Tripwire fixtures.** `firestarter/tests/test_check_size_baseline.py` — 14 legs, 8 redden. Per
memory and VALIDATION §Wave 0: **sever the affected legs onto a NEW `*_v151*` fixture family**, never
edit the `fullflash` family in place, and never write "fixtures byte-unchanged" as a criterion.

---

### 5. Documentation patterns

**`doc/infoic-field-dictionary.md` per-field entry** — the exact shape, `:241-249`:

```markdown
### `page_size` (uint32 hex) — CONFIRMED

**Source:** [`database.c#L598`](…/src/database.c#L598) @ `a8efaedc`

Page-write size for EEPROM/Flash. Typically 64 or 128 bytes for 28C-family; …
```

So: `### \`<field>\` (<type>) — <STATUS>` where STATUS ∈ {`CONFIRMED`, `UNKNOWN`, or a compound like
`:107`'s *"CONFIRMED for decoded bits; UNKNOWN for bits 3/6/7"*}; a bolded `**Source:**` line with a
deep link to the upstream file+line pinned `@ a8efaedc`; then prose. DATA-06's section is the first that
must additionally carry (i) the *emitted-field* measurements (D-14's figures), (ii) an explicit
*no runtime consumer* statement naming Backlog 999.28, and (iii) a citation of
`tests/test_sdp_db_invariant.py::test_sdp_partition_matches_infoic_derived_field_element_wise` (`:584-621`).
The file also ends with a `## Summary: build_db.py Known Bugs vs Correct Semantics` section at `:277` —
check whether a new row is owed there.

**The two one-line pointers: no analog.** `doc/package-details.md:43-44` and `doc/protocol-flags.md:24-25`
are pure 4/5-column bit tables with no prose, no footnote and no cross-reference convention anywhere in
either file. The pointer must be **authored**. Cheapest shape that survives the doc-parsing test in
`test_protect_flags_doc_measurements.py`: one italic line immediately under each table, e.g.
`*Bits 14/15 document minipro's bit semantics. For what the emitted `protect_off_before` /
`protect_on_after` fields mean at runtime, see [infoic-field-dictionary.md](infoic-field-dictionary.md#…).*`
— a stable relative link the test can assert as a substring in both files.

**Doc-invariant test shape** — `tests/test_lockable_proms_doc_claims.py`: module-level
`_FA_DIR = Path(__file__).parent.parent`, `_DOC_FILE = _FA_DIR / "doc" / "<file>.md"`, a
`_read_doc_text()` helper, pre-compiled `re` patterns as module constants with a comment explaining
*why the pattern is a real checkable negative* (`:52-58`), and per-leg docstrings citing the historical
line (*"`:295`'s row … Landed by c3c9424 (121-13); this test durably gates it going forward"*). Note the
line citations are described as *historical* — the assertions match on text, never on line number.

**Untouched-guard shape** — `test_b15_page_size_corroboration.py:246-262`
(`test_sdp_capability_module_untouched_this_plan`): import the module, assert a distinctive docstring
substring still present, with a failure message saying *"if it changed for a legitimate reason, this
assertion should be updated by whichever plan makes that change, not silently ignored."* This is D-16's
`sdp_capability.py`-untouched leg verbatim, modulo the substring.

---

### 6. `dev` command registration + channel gate

**Analog:** `cli_handlers.py:1469-1505` (`dev addr`). The template is exact:

```python
if _DEV_TOOLS_ENABLED:

    @dev.command(name="addr")
    @click.argument("eprom", shell_complete=_complete_eprom)
    @click.option("-i", "--input-enable", "input_enable", is_flag=True, help="…")
    @click.pass_obj
    @map_typed_errors
    def dev_addr(app: AppContext, eprom: str, …) -> None:
        """One-line help string — this is what `dev --help` renders."""
        eprom_data = resolve_chip(eprom, db=app.db)
        ok = app.eprom_operator.dev_set_address_mode(…)
        sys.exit(0 if ok else 1)
```

Copy: the `if _DEV_TOOLS_ENABLED:` **module-level** block (registration is the real gate, not the tuple),
the decorator order (`@dev.command` → `@click.argument`/`@click.option` → `@click.pass_obj` →
`@map_typed_errors`), the `shell_complete=_complete_eprom`, and terminal `sys.exit(...)`.

**Diverge in exactly one place:** `resolve_chip(eprom, db=app.db)` returns the *programmer* dict, which
carries neither `protocol-id` nor `name` — the trap `protection_gate_for_entry` hard-fails on. Use the
`write` handler's idiom instead, `cli_handlers.py:713-726`:

```python
    sdp_entry = app.db.get_eprom(eprom)
    is_protocol_0x0d = bool(sdp_entry) and sdp_entry.get("protocol-id") == SDP_PROTOCOL_ID
```

with its comment *"decided here, in the handler, because this is the last place with both the chip NAME
and `app.db`"*. Both dicts are likely needed: `get_eprom()` for the predicate, `resolve_chip()` for the
firmware operation.

**`channel.py:57-64`** — `BETA_ONLY_DEV_COMMANDS: tuple[str, ...]` is a flat 6-tuple of subcommand-name
strings preceded by a comment that (a) states the count in words, (b) cites the measured baseline, and
(c) says explicitly that *"the actual gate is non-registration of the six `@dev.command` blocks, not
membership in this tuple"*. Adding `"lock-status"` therefore requires updating "six"→"seven" in that
comment and in `BETA_ONLY_BOARDS`-style prose; `tests/test_dev_tools_channel_gate.py:150-158` pins the
exact tuple, and `test_dev_group_channel_gating.py`'s `_GATED_NAMES` goes 6→7.

**`constants.py:56-102`** — flat `COMMAND_* = <int>` ladder mirroring `firestarter.h`, then a
`COMMAND_NAMES` dict whose comment at `:68-76` warns the entries are **load-bearing** (dereferenced by
`_setup_operation` and `_operation_context` in `eprom_operations.py`; a missing key is a `KeyError` at
operation setup). One new `COMMAND_READ_PROTECTION = 16` plus its `COMMAND_NAMES` row.

---

## Shared Patterns

### Fail-closed hard-fail on a wrong-shaped dict
**Source:** `firestarter_app/firestarter/sdp_capability.py:229-238`
**Apply to:** every new pure predicate. A `raise KeyError` with a ~10-line message that names the likely
caller mistake (`resolve_chip()`/`convert_to_programmer()`) and cites the historical vacuity
(`check_eprom_blank`'s `_SRAM_PROTO_IDS` short-circuit). Never a `.get(..., default)`.

### Reason fragments as module constants
**Source:** `sdp_capability.py:187-193`
**Apply to:** `protection_readability.py`, `lock_status.py`. Tests assert the constant, not the sentence.
Under D-08 the *class token* is the primary assertion and the reason fragment is secondary.

### Anti-hollow gate contract
**Source:** `tools/check_sdp_capability_invariants.py:43-64`
**Apply to:** the new gate. Real `ast.parse` walk; paired pytest with a committed planted fixture per
class; fail-closed on missing path, unparsable source, and zero-symbol scan; PASS line names the target.

### Env-override injection seam
**Source:** `check_sdp_capability_invariants.py:85-87` + `test_check_sdp_capability.py:58-68`
**Apply to:** the new gate and its test. Also mirrored by `FIRESTARTER_DEVTEST_SRC` and
`FIRESTARTER_CMD_ADMISSION_SRC` — three prior instances, so the convention is settled.

### Census figures pinned as literals
**Source:** `tests/test_sdp_db_invariant.py` (`43`/`41`/`84`) and `test_b15_page_size_corroboration.py:230-243`
(pins the *set*, not just the count, with a symmetric-difference failure message)
**Apply to:** D-12 leg 3. Pin the set where the set is small enough to read; pin counts plus the set
identity where it is not.

### Synthetic-mutation non-vacuity control
**Source:** `tests/test_sdp_db_invariant.py:629-680` (`test_partition_flags_a_moved_chip_via_db_field_non_vacuous`)
**Apply to:** D-12 leg 6. Shape: build a `synthetic_db_before` dict of 2 rows (one that moves, one
untouched control), assert the *fixture setup* first with a `"Fixture setup error: …"` message, then
build `synthetic_db_after` and assert the invariant raises **naming the moved row and not the control**.

### Named, SHA-attributed firmware growth
**Source:** `firestarter/scripts/check_size_baseline.py:186-240` + `:405-419`
**Apply to:** the new exemption. Never re-anchor the baseline, never widen a band, never sum exemptions.

---

## No Analog Found

| File / element | Role | Why | Closest structural cousin |
|---|---|---|---|
| Class 2(b′) AST rule for a **three-axis** literal table | gate rule | The existing rule is hard-wired to `frozenset(<display of str literals>)` for **one** symbol (`_TOKEN_SET_NAME`, a bare `str`). Three axes and three states have no precedent. | `_is_clean_frozenset_of_literals_call` (`:220-232`) — extensible per §1 Option A by parameterising `_TOKEN_SET_NAME` → a tuple of names; **Option B needs a genuinely new dict-literal matcher.** |
| The gate/output **token split** (`read_permitted` never printed) | design | No two-function pure/impure split exists in this tree; `sdp_capability` is pure-only and `sdp_honesty` is prose-only. | `sdp_honesty.map_unknown_cmd_to_outdated` (returns-not-raises so the caller owns the terminal decision) — the same "compute, don't act" instinct, one function short of the pattern. |
| One-line cross-reference pointers in `doc/package-details.md` / `doc/protocol-flags.md` | doc | Both files are bare bit tables; no footnote, prose or cross-link convention exists in either. | Must be authored — see §5 for a proposed shape the DATA-06 test can assert. |
| `test_lock_status_wire.py` — frame build/parse at unit level | test | Host wire tests in this tree are parity gates over *constants*, not frame round-trips; `test_revision_constants_parity.py` **fails OPEN** without the sibling repo. | `tests/fixtures/fake_firestarter` (a fake device seam already in the fixtures dir) is the nearest mechanism; the planner should confirm what it exposes before assuming a frame-level harness exists. |

---

## Metadata

**Analog search scope:** `firestarter_app/{firestarter,tools,tests,doc}/`,
`firestarter/{include,src/proms,src,scripts,tests}/`, `.planning/phases/151-*/`.
**Files read this pass:** 18.
**Pattern extraction date:** 2026-08-20.
