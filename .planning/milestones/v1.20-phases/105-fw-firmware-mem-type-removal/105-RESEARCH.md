# Phase 105: FW — Firmware `mem_type` Removal - Research

**Researched:** 2026-07-02
**Domain:** Arduino C++ firmware (PlatformIO) — dispatch-chain deletion / wire-contract change
**Confidence:** HIGH (all findings grounded against actual submodule code, not assumptions)

## Summary

Phase 105 is a firmware-only **pure-removal** phase: delete the `mem_type` fallback dispatch
chain in `memory.cpp`, drop `handle->mem_type` from the struct, stop parsing the `type` JSON
field, and retire the `0xAE` message + `TYPE_*` constants. I grounded every CONTEXT.md line
reference against the actual code in the `firestarter/` submodule. The CONTEXT line numbers are
accurate to within a line or two, and the D-04/D-05/D-06 decisions are mechanically sound.

**Two findings materially expand what CONTEXT anticipated:**
1. **BLOCKER-class prerequisite (D-01):** The submodule is currently on `v1.19-protocol-naming-labels`,
   and neither local `beta` nor `origin/beta` contains the v1.19 layer (no `proto_constants.h`,
   raw-hex dispatch, old handler names). The D-01 setup action (merge v1.19→beta, fork v1.20 off
   beta) has **NOT been performed**. It MUST happen before Phase 105 planning/execution references
   are valid — see finding #1 below. The good news: the *current* `v1.19` checkout is exactly what
   post-merge beta will look like, so all line references in this document are correct **once the
   merge lands**.
2. **`json_parser.c` `type` removal is 4 touchpoints, not 2.** CONTEXT names lines 307 and 64.
   The actual removal also requires deleting the forward declaration (line 21) and the
   `key_parsers[]` table entry (line 78). Missing either is a compile error.

**Primary recommendation:** Execute the D-01 v1.19→beta lockstep merge + v1.20 fork as the
Wave-0 setup step, THEN delete the fallback in one commit (dispatch chain + `TYPE_*` + `0xAE`
per SC#3) and the struct/parser field in a second commit, THEN delete the two named test cases
and adjust `make_handle()`. Add one minimal `protocol == 0 → not_implemented` assertion to keep
SC#1 provable (D-06 resolution below).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Protocol dispatch | Firmware (`memory.cpp`) | — | `configure_memory()` owns the dispatch decision |
| Wire-field parse | Firmware (`json_parser.c`) | Host (emit, Phase 106) | fw parses; host emits — split across 105/106 |
| Fail-closed error | Firmware (`not_implemented.cpp`) | — | `configure_not_implemented()` returns 0xBB |
| Dispatch regression proof | Host tool (`check_dispatch.py`) | Firmware native tests | simulates every DB chip's dispatch path |

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FW-01 | `protocol == 0` fail-closes; delete `mem_type` fallback (steps 7–11) | `memory.cpp:122–137` is the exact chain to delete; guard at `:117` collapses per D-04; `configure_not_implemented()` already the terminal handler |
| FW-02 | Remove `mem_type` from struct; `json_parser.c` stops extracting `type` | `firestarter.h:88`; json_parser.c has **4** touchpoints (21/64/78/306-308) — see finding #4 |
| FW-03 | Retire `0xAE` + `TYPE_*` constants in lockstep | `messages.h:83` (`0xAE`); `memory.cpp:27–30` (`TYPE_*`); all confined, no external refs |
| WIRE-01 | Remove `type` from host→fw JSON contract (fw side) | fw stops parsing `type`; unknown-field-skip makes host-still-emitting harmless (verified: parser table is allowlist-based) |

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** v1.20 sub-repo branches fork off **beta, only after v1.19 is merged into beta first.**
  Operator authorized merging v1.19→beta, then forking v1.20 off updated beta. (STATE VERIFIED
  NOT YET DONE — see finding #1.)
- **D-02:** Authorization is for the **v1.19 branch merge only** — NOT the beta release cut. The
  `3.0.0bXX` tag + gitlink bump stay operator-gated; gitlinks stay PINNED (`2d93379` fw /
  `e0bdea4` app). Apply to BOTH sub-repos in lockstep.
- **D-03:** The v1.19→beta merge is a **setup action before Phase 105 execution**, not part of
  discussion. NOT done during discussion.
- **D-04:** Collapse to **one terminal fail-closed exit.** Replace the `if (handle->protocol != 0)
  { configure_not_implemented(handle); return; }` guard (`memory.cpp:117`) with an unconditional
  terminal `configure_not_implemented(handle); return;` after all recognized dispatch arms.
  `protocol == 0` and any unknown non-zero protocol share ONE fail-closed exit. Recognized arms
  (steps 1–6b) stay unchanged.
- **D-05:** **Delete the fallback-specific test cases**, don't rewrite them. Remove
  `test_protocol_zero_with_mem_type_eprom_dispatches_eprom` from BOTH suites and the
  `test_unknown_protocol_with_unknown_mem_type_errors` case. Rely on `test_not_implemented`'s
  generic coverage (0x11 / 0x2A / 0x2B / 0x2C + 0x99) for fail-closed proof. No "type field
  ignored" test required.
- **D-06 (coverage flag — NOT a re-decision):** SC#1 is `protocol == 0 → 0xBB via
  configure_not_implemented()`. The deleted `test_protocol_zero_...` case is currently the ONLY
  `protocol == 0` test. `test_not_implemented` covers unknown **non-zero** (0x99) but not zero.
  Planner/verifier MUST confirm SC#1 stays provable — either explicitly accept generic coverage
  OR add a single minimal `protocol == 0 → configure_not_implemented` assertion. Do not silently
  ship without resolving.

### Claude's Discretion
- Exact grouping of edits into commits — but SC#3 requires the `0xAE` + `TYPE_*` retirement to
  land **in the same commit** as the dispatch-chain deletion (no orphaned dead constants).
  Removing `handle->mem_type` forces the json_parser `type` removal together (references deleted
  field).
- Whether `make_handle(protocol, mem_type, cmd)` in the two native suites keeps or drops its
  `mem_type` parameter after the struct field is removed (mechanical; field no longer exists).

### Deferred Ideas (OUT OF SCOPE)
- **LEGACY-01 (v2):** `FLAG_VPE_AS_VPP (0x10)` removal.
- **LEGACY-02 (v2):** Rename `EPROM_LEGACY (0x0B)` label + scrub "legacy fallback" prose.
- **Phase 106 (this milestone):** Host emit-side `type` removal + `_ALGO_MEM_TYPE` / derived
  `mem_type` / "Generic Flash (legacy fallback only)" default removal + in-host `algorithm`
  rejection. Completes WIRE-01.
- **Phase 107 (close):** Doc updates (`CLAUDE.md` steps 7–11, `PROTOCOLS.md`, JSON wire-field
  docs) + breaking-change/changelog + full non-regression re-verification.
- **Beta release cut (operator-gated):** `3.0.0bXX` tag + gitlink bump.

## Standard Stack

No new packages. This is a deletion phase in an existing PlatformIO/Arduino C++ + Unity test
codebase. No `## Package Legitimacy Audit` needed (no external packages installed).

| Tool | Version/Source | Purpose |
|------|----------------|---------|
| PlatformIO CLI | `/usr/local/bin/pio` and `/usr/local/bin/platformio` (both present) `[VERIFIED: which]` | build + native test runner |
| Unity | via `test_framework = unity` in `[env:native]` `[VERIFIED: platformio.ini:71]` | native dispatch tests |

## Finding #1 — BLOCKER-CLASS: v1.19→beta merge NOT yet performed (D-01 prerequisite)

**Status: the D-01 setup action has NOT been executed. This gates the whole phase.** `[VERIFIED: git]`

Current submodule state (`/workspaces/firestarter`):
- Checked-out branch: **`v1.19-protocol-naming-labels`** (HEAD `96b3138`), NOT a v1.20 branch.
- **No `v1.20-*` branch exists** in the fw sub-repo (`git branch -a` — none).
- Local `beta` and `origin/beta` do **NOT** contain `include/proto_constants.h`
  (`git ls-tree beta include/proto_constants.h` → empty; same for `origin/beta`).
- The v1.19 layer (proto_constants.h, `flash_nor_unlock.cpp`/`flash_5v_page.cpp` renamed handlers,
  `doc/PROTOCOLS.md`, PROTO_-named dispatch) exists **only on the `v1.19-protocol-naming-labels`
  branch** — matching CONTEXT D-01's "all 15 v1.19 commits unmerged" claim exactly.

**Why this is a blocker, not a nitpick:** Phase 105's edits reference `PROTO_*` tokens
(`memory.cpp:75–104`), `include/proto_constants.h`, and the renamed handler files. If the planner
or executor forks v1.20 off the *current* `beta`, those references do not exist and the phase
premise collapses (a Phase-70-style collision). Per D-01/D-03 the fix is a **setup action before
execution**: merge `v1.19-protocol-naming-labels` → `beta` in BOTH sub-repos in lockstep, then
fork `v1.20-...` off the updated `beta`. Per D-02 this is the branch merge ONLY — no tag, no
gitlink bump (gitlinks stay PINNED `2d93379` fw / `e0bdea4` app).

**Mitigating fact (why the rest of this research is still valid):** The current `v1.19` checkout
IS what post-merge beta will contain. Every line number and code quotation below is taken from
that checkout, so they are correct **once the merge lands**. The planner should treat the D-01
merge as Wave-0 and gate all subsequent waves behind it.

**Recommendation for orchestrator:** Surface the D-01 merge as an explicit setup task /
`checkpoint:human-verify` before planning execution. Do NOT let the planner assume beta is ready.

## Architecture Patterns

### System Data Flow (dispatch)

```
host JSON  ──serial──▶  json_parser.c (allowlist parse: key_parsers[] table)
                              │  algorithm → handle->protocol
                              │  type      → handle->mem_type   ◀── DELETE (Phase 105)
                              ▼
                        configure_memory()  (memory.cpp)
                              │
              ┌───────────────┴───────────────────────────────┐
              │ steps 1–6b: if (protocol == PROTO_*) →         │  KEEP (unchanged)
              │             configure_<handler>(); return;     │
              │ step 6a: 0x11/0x2A/0x2B/0x2C → not_implemented  │
              │ step 6b: protocol != 0      → not_implemented   │  ◀── D-04: collapse
              ├───────────────────────────────────────────────┤
              │ steps 7–11: mem_type fallback chain            │  ◀── DELETE (Phase 105)
              │   TYPE_EPROM→eprom, TYPE_SRAM→sram, ...         │
              │   else → LOG_ERROR(MSG_ERR_MEM_TYPE_UNSUPPORTED)│
              └───────────────────────────────────────────────┘
                              ▼  (after D-04 collapse)
                     configure_not_implemented(handle); return;   ← single terminal exit
```

### D-04 collapse — mechanically verified correct

Current tail of `configure_memory()` (`memory.cpp`) `[VERIFIED: Read]`:
```cpp
// line 108-112: step 6a — named infeasibility arms (KEEP)
if (handle->protocol == 0x11 || handle->protocol == 0x2A ||
    handle->protocol == 0x2B || handle->protocol == 0x2C) {
    configure_not_implemented(handle);
    return;
}
// line 117-120: step 6b guard (D-04: this becomes the unconditional terminal)
if (handle->protocol != 0) {
    configure_not_implemented(handle);
    return;
}
// line 122-137: steps 7–11 mem_type fallback (DELETE ENTIRELY)
if (handle->mem_type == TYPE_EPROM) { configure_eprom(handle); return; }
else if (handle->mem_type == TYPE_SRAM) { configure_sram(handle); return; }
else if (handle->mem_type == TYPE_FLASH_TYPE_3) { configure_flash_nor_unlock(handle); return; }
else if (handle->mem_type == TYPE_FLASH_TYPE_4) { configure_flash_5v_page(handle); return; }
LOG_ERROR_ID_U8(MSG_ERR_MEM_TYPE_UNSUPPORTED, handle->mem_type);
handle->response_code = RESPONSE_CODE_ERROR;
```

**D-04 result:** delete lines 122–137 entirely, and change the `if (handle->protocol != 0)` guard
(117-120) into an unconditional terminal:
```cpp
    // Fail-closed: protocol == 0 or any unrecognized non-zero protocol.
    configure_not_implemented(handle);
    return;
}
```
Keep the named-infeasibility arm (108-112) above it. Both `protocol == 0` and unknown non-zero now
share the single terminal `configure_not_implemented()` — exactly D-04's intent. This is correct:
`configure_not_implemented()` sets `RESPONSE_CODE_ERROR` + returns `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED
(0xBB)` and leaves all three op pointers NULL (verified by `test_not_implemented` assertions).

## Grounded line references (all VERIFIED against current v1.19 checkout)

| CONTEXT claim | Actual (verified) | Match? |
|---------------|-------------------|--------|
| `memory.cpp` guard ~117 | `memory.cpp:117` `if (handle->protocol != 0)` | ✅ exact |
| `memory.cpp` fallback steps 7–11 ~122–138 | `memory.cpp:122–137` (chain 123-135, error 136-137) | ✅ within 1 line |
| `memory.cpp` `TYPE_*` defines ~27–30 | `memory.cpp:27–30` (`TYPE_EPROM 1`, `TYPE_FLASH_TYPE_3 3`, `TYPE_SRAM 4`, `TYPE_FLASH_TYPE_4 5`) | ✅ exact |
| `firestarter.h` `uint8_t mem_type;` ~88 | `firestarter.h:88` `uint8_t mem_type;` | ✅ exact |
| `json_parser.c` `extract_int("type",…)` ~307 | `json_parser.c:503` (inside `get_type()`, body 306-308) | ✅ exact |
| `json_parser.c` `key_type[] PROGMEM = "type"` ~64 | `json_parser.c:75` | ✅ exact |
| `messages.h` `MSG_ERR_MEM_TYPE_UNSUPPORTED 0xAE` ~83 | `messages.h:83` | ✅ exact |
| `rurp_serial_utils.cpp:374` `0xAE` = CRC table byte, DO NOT TOUCH | `:377` is a CRC8_TABLE row (`0xAE, 0xA9, 0xA0, …`) — confirmed table data | ✅ leave untouched |

## Finding #3 — `mem_type` consumers: exactly as CONTEXT claimed (+ 2 test files)

Full-tree grep for `mem_type` / `->mem_type` / `.mem_type` `[VERIFIED: grep]`. Consumers:
1. **`firestarter.h:88`** — struct field declaration (DELETE).
2. **`memory.cpp:123/126/129/132/136`** — dispatch chain reads (DELETE with the chain).
3. **`json_parser.c:503`** — populate (DELETE — see finding #4 for full touchpoint list).
4. **`test/native/avr/test_dispatch/test_configure_memory.cpp:58/61`** — `make_handle()` param + `h.mem_type = mem_type;`.
5. **`test/native/avr/test_not_implemented/test_not_implemented.cpp:39/42`** — same `make_handle()` pattern.

**No unanticipated firmware consumers.** CONTEXT's "exactly two firmware consumers + test
`make_handle()`" is accurate. The comment references at `memory.cpp:115/116/122` are prose (delete
with the block). Test comment references at `test_configure_memory.cpp:10/21/23/149/151/157/158`
and `test_not_implemented.cpp:97` are comments in the deleted-test regions.

## Finding #4 — `json_parser.c` `type` removal is 4 touchpoints (CONTEXT named 2)

CONTEXT lists only `:307` and `:64`. The parser is an **allowlist table** (`key_parsers[]`), so a
clean removal without a dangling reference requires **all four**: `[VERIFIED: Read]`
1. **`:21`** — forward declaration: `bool get_type(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);`
2. **`:64`** — `const char key_type[] PROGMEM = "type";`
3. **`:78`** — table entry `{key_type, get_type},` inside `key_parsers[]` (line 78, middle of a 3-per-row block)
4. **`:306–308`** — the `get_type()` function body (`extract_int("type", handle->mem_type);`)

Removing only 307+64 leaves `get_type` referenced at :21 and :78 (link/compile error) and an
orphaned function. Delete all four together. **WIRE-01 unknown-field-skip is real:** the parser
only dispatches keys present in `key_parsers[]`, so once `key_type`/`get_type` are gone, a host
still emitting `"type"` is silently ignored (the field just isn't in the allowlist). No test
required per D-05.

## Finding #5 — `0xAE` and `TYPE_*` are fully self-contained (SC#3 clean)

- `MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE)`: only two references tree-wide — the `#define` at
  `messages.h:83` and its single use at `memory.cpp:136` (deleted with the chain). `[VERIFIED: grep]`
- The `0xAE` at `rurp_serial_utils.cpp:374` is a **CRC8 lookup-table byte** (surrounded by
  `0xA9, 0xA0, 0xA7, 0xB2, 0xB5, 0xBC, 0xBB, …`) — NOT a message code. **Do not touch.** `[VERIFIED: Read]`
- `test_messages` (`test_rurp_log_id.cpp`) does NOT reference `0xAE`/`MEM_TYPE` (uses `0xB1` as
  its example) — removing the message will not break it. `[VERIFIED: grep]`
- `TYPE_EPROM/SRAM/FLASH_TYPE_3/FLASH_TYPE_4`: defined only at `memory.cpp:27–30`, used only at
  `memory.cpp:123–132`. The only other occurrences are `/* TYPE_EPROM = 1 */` comments in the two
  deleted test cases. `[VERIFIED: grep]`

**SC#3 (same commit):** the `0xAE` `#define`, the `TYPE_*` `#define`s, and the fallback chain
deletion belong in ONE commit — verified there are no orphaned readers left after deletion.

## Finding #6 — Native tests + D-06 resolution

### Test cases to delete (D-05) — exact names verified `[VERIFIED: Read]`

| Suite | Case to delete | Line | Note |
|-------|----------------|------|------|
| `test_dispatch/test_configure_memory.cpp` | `test_protocol_zero_with_mem_type_eprom_dispatches_eprom` | 159-163 (RUN_TEST :219) | asserts deleted fallback |
| `test_dispatch/test_configure_memory.cpp` | `test_unknown_protocol_with_unknown_mem_type_errors` | 151-155 (RUN_TEST :218) | uses `make_handle(0, 99, …)` |
| `test_not_implemented/test_not_implemented.cpp` | `test_protocol_zero_with_mem_type_eprom_dispatches_eprom` | 100-104 (RUN_TEST :121) | asserts deleted fallback |

`make_handle()` signature (BOTH suites, identical): `make_handle(uint32_t protocol, uint8_t
mem_type, uint8_t cmd)` — takes a `mem_type` param and sets `h.mem_type = mem_type;`. After the
struct field is removed, `h.mem_type = mem_type;` must be deleted; the `mem_type` param becomes
vestigial (drop it or keep-and-ignore per Claude's Discretion). **Every surviving `make_handle(...)`
call passes `0` for mem_type, so dropping the param means editing ~19 call sites in test_configure_memory
and ~6 in test_not_implemented — keeping the param (ignored) is the lower-churn mechanical choice.**

### D-06 RESOLUTION (evidence-based)

`test_not_implemented` covers: `0x11, 0x2A, 0x2B, 0x2C` (named-infeasible) and `0x99` (unknown
non-zero) — all asserting `RESPONSE_CODE_ERROR` + all-NULL op pointers. It covers unknown
**non-zero** only. The single existing `protocol == 0` test is
`test_protocol_zero_with_mem_type_eprom_dispatches_eprom`, which D-05 deletes. `[VERIFIED: Read]`

**After deletion, SC#1 (`protocol == 0 → 0xBB via configure_not_implemented()`) has ZERO test
coverage.** SC#1 is a named success criterion, so leaving it unprovable is a gap.

**Recommendation: ADD one minimal assertion** to `test_not_implemented.cpp` (the fail-closed home):
```cpp
/* SC#1 (Phase 105): protocol == 0 now fail-closes (no mem_type fallback). */
void test_protocol_zero_fail_closes_not_implemented(void) {
    firestarter_handle_t h = make_handle(0, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
    TEST_ASSERT_NULL(h.firestarter_operation_init);
    TEST_ASSERT_NULL(h.firestarter_operation_main);
    TEST_ASSERT_NULL(h.firestarter_operation_end);
}
```
This is the **inverse** of the deleted fallback test (asserts fail-closed, not dispatch) — it does
NOT contradict D-05 ("delete fallback-*specific* cases"). It is the cheapest way to make SC#1
provable. The alternative (accept generic 0x99 coverage as sufficient) leaves SC#1's literal
`protocol == 0` claim untested — not recommended for a named criterion.

**Interaction note for the planner:** the deleted `test_unknown_protocol_with_unknown_mem_type_errors`
uses `make_handle(0, 99, …)` and asserts `RESPONSE_CODE_ERROR`. After the D-04 collapse this test
would actually **still pass** (protocol==0 now fail-closes to ERROR). D-05 deletes it anyway because
its *intent* (proving the mem_type=99 error path) is gone. The recommended new test above is the
clean replacement that pins the new intent.

## Finding #7 — Non-regression gates (SC#4 / GATE-01 / SAFE-01)

### Every real chip is protocol-dispatched — fallback is DEAD code
`[VERIFIED: python over chip_database.json]` All **746** chips in `chip_database.json` have a
non-zero `algorithm`. **Zero** chips have `algorithm == 0`/`None`. Therefore no real DB chip can
ever reach the `protocol == 0` mem_type fallback — it is dead code for every shipping chip. This is
the SAFE-01 / SC#4 proof: removing the fallback changes behavior for **no** real chip.

### The v1.16 "golden register traces" = `test_val_*` suites (protocol-keyed, unaffected)
`[VERIFIED: Read + platformio.ini]` The validation-matrix golden traces live in
`test/native/avr/_shared/validation_matrix.h` (`VAL_FAMILIES[]`, 11 entries) + the six
`test_val_*` suites (`test_val_eprom`, `test_val_eeprom28c`, `test_val_nor_unlock`,
`test_val_5v_page`, `test_val_flash_intel`, `test_val_sram`). `VAL_FAMILIES` is keyed on
`protocol` + `handler_name` ONLY — **no `mem_type` reference anywhere in `test_val_*`** (grep
returned nothing). Removing the mem_type fallback cannot affect them. Generated by
`tools/gen_validation_header.py` from `tools/validation_matrix_spec.json` — do not hand-edit.

### `check_dispatch.py` lives in the HOST repo (Phase 106 territory) — but stays green in 105
`[VERIFIED: find + Read]` `check_dispatch.py` is at **`firestarter_app/tools/check_dispatch.py`**,
NOT in the firmware repo. It simulates firmware dispatch for every DB chip. Its `dispatch()`
function (lines 133-157) mirrors the firmware: protocol-prefix arms first (135-146), then
`if protocol != 0: return "not_implemented"` (149-150), then the `_ALGO_MEM_TYPE` mem_type
fallback (151-157). Because all 746 chips have non-zero protocol, every chip resolves in the
protocol-prefix block and NEVER reaches the fallback — so `check_dispatch.py` reports 0 violations
regardless of the firmware change. **Phase 105 does not touch it** (host repo). Updating
`check_dispatch.py`'s mirror to drop `_ALGO_MEM_TYPE` is Phase 106/107 work (it references
`database.py::_ALGO_MEM_TYPE`). For Phase 105, running it is a *cross-repo* non-regression check
that will pass unchanged.

### Dispatch-mirror guard
The "dispatch-mirror guard" referenced in CONTEXT is `check_dispatch.py`'s role of asserting the
firmware dispatch order matches the host simulation. There is no separate firmware-repo mirror
script. The frame/COBS golden vectors (`test_frame_vectors`, `frame_vectors.h`) and the
version-string golden (`tests/golden/stable-*.h`) are unrelated to dispatch and unaffected.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Fail-closed terminal for protocol==0 | new error path | existing `configure_not_implemented(handle)` | already returns 0xBB + NULL pointers + sets RESPONSE_CODE_ERROR; already the target of steps 6a/6b |
| Proving fallback was dead | manual chip audit | `check_dispatch.py` (host) + the 746-chip algorithm scan | already simulates every DB chip's dispatch |
| Protocol dispatch enumeration | new list | `VAL_FAMILIES[]` + `test_configure_memory.cpp` per-protocol tests | one test per KNOWN_PROTOCOLS entry already exists |

## Common Pitfalls

### Pitfall 1: Forking v1.20 off un-merged beta
**What goes wrong:** `PROTO_*` tokens, `proto_constants.h`, renamed handlers don't exist → every
Phase 105 reference is wrong; compile fails or collides.
**How to avoid:** Execute the D-01 merge (v1.19→beta, both sub-repos, lockstep, no tag) BEFORE
forking v1.20. Verify `git ls-tree beta include/proto_constants.h` is non-empty first.

### Pitfall 2: Deleting only 2 of 4 `type`-parse touchpoints in json_parser.c
**What goes wrong:** deleting `get_type` body + `key_type` but leaving the `:21` forward decl or
`:78` table entry → compile/link error (`get_type` undefined or `key_type` undefined).
**How to avoid:** delete all four (21, 64, 78, 306-308) in one edit.

### Pitfall 3: Orphaned dead constants (SC#3 violation)
**What goes wrong:** removing the fallback chain but leaving `TYPE_*` (`memory.cpp:27-30`) or
`0xAE` (`messages.h:83`) as dead `#define`s.
**How to avoid:** SC#3 mandates same-commit removal. After deletion, `grep -rn "TYPE_EPROM\|0xAE"`
should show only the CRC-table byte at `rurp_serial_utils.cpp:374`.

### Pitfall 4: Touching the CRC8 table byte
**What goes wrong:** editing `0xAE` at `rurp_serial_utils.cpp:374` corrupts the CRC8 lookup table →
every framed message fails CRC.
**How to avoid:** it is table DATA, not a message ref. Leave it.

### Pitfall 5: Leaving SC#1 unprovable after D-05 deletions
**What goes wrong:** all `protocol == 0` coverage removed; SC#1 (`protocol == 0 → 0xBB`) has no
test.
**How to avoid:** add the minimal `test_protocol_zero_fail_closes_not_implemented` assertion
(Finding #6).

### Pitfall 6: `make_handle()` call-site churn
**What goes wrong:** dropping the `mem_type` param forces editing ~25 call sites across two files;
easy to miss one → compile error.
**How to avoid:** keeping the (now-ignored) param is lower-churn; either way delete only the
`h.mem_type = mem_type;` line inside `make_handle()`.

## Code Examples

### Native test invocation (verified commands)
```bash
# Source: firestarter/CLAUDE.md + platformio.ini [env:native]; pio + platformio both on PATH
cd firestarter
pio test -e native                            # every native suite (incl. test_dispatch, test_not_implemented, test_val_*)
pio test -e native -f "*test_dispatch*"       # just the configure_memory dispatch suite
pio test -e native -f "*test_not_implemented*"
pio run -e uno                                # AVR build sanity (Uno)
pio run -e leonardo                           # AVR build sanity (Leonardo)
```

### Cross-repo non-regression (host, for SC#4 spot-check)
```bash
cd firestarter_app
python tools/check_dispatch.py                # exit 0 = every chip resolves + no SRAM→eprom hazard
```

## Runtime State Inventory

This is a firmware source refactor. Reviewing the 5 categories for completeness:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — the `mem_type`/`type` axis is a per-command wire field + in-RAM struct field; nothing persisted (no EEPROM/DB key uses it). Verified: `mem_type` grep shows only struct + dispatch + parser. | none |
| Live service config | None — no external service embeds `mem_type`. The host still emits `type` on the wire until Phase 106; unknown-field-skip makes that harmless. | none (Phase 106 removes host emit) |
| OS-registered state | None — firmware-only. | none |
| Secrets/env vars | None. | none |
| Build artifacts | Firmware `.pio/build/*` objects reference `memory.cpp`/`json_parser.c` — auto-rebuilt by `pio`. No stale registered artifact carries the removed symbols. | rebuild via `pio run` |

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Dispatch on `mem_type` with protocol as override | Dispatch on `protocol` only; `mem_type` fallback for protocol==0 | v1.16 (protocol-first) / Phase 64 fail-closed | Phase 105 removes the last vestige |
| `protocol == 0` silently falls back to mem_type | `protocol == 0` fail-closes to 0xBB | Phase 105 (this) | breaking wire-contract change (WIRE-01) |
| Wire carries `type` + `algorithm` | Wire carries `algorithm` only | Phase 105 (fw stops parsing) + Phase 106 (host stops emitting) | fw-first ordering safe via unknown-field-skip |

**Deprecated/outdated after this phase:** `handle->mem_type`, `TYPE_*` constants,
`MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE)`, the `type` JSON key parse.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Keeping the vestigial `mem_type` param in `make_handle()` (vs dropping it) is acceptable; it's Claude's Discretion per CONTEXT | Finding #6 | Low — mechanical; both compile; operator explicitly left it to discretion |
| A2 | The recommended `test_protocol_zero_fail_closes_not_implemented` addition satisfies D-06 without contradicting D-05 | Finding #6 | Low — D-06 explicitly permits "add a single minimal assertion (the inverse of the deleted fallback test)" |

*All other findings are VERIFIED against the current submodule checkout — no assumed facts.*

## Open Questions

1. **Has the D-01 v1.19→beta merge been performed since discussion?**
   - What we know: as of this research (git state on `v1.19-protocol-naming-labels`, beta lacks
     proto_constants.h), it has NOT.
   - What's unclear: whether the operator/orchestrator runs it as the Wave-0 setup before planning
     execution.
   - Recommendation: orchestrator must confirm/execute the merge (both sub-repos, no tag, gitlinks
     PINNED) before Phase 105 execution. Treat as a hard gate.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO (`pio`/`platformio`) | build + native tests | ✓ | `/usr/local/bin/pio` + `/usr/local/bin/platformio` | — |
| Python 3 | `check_dispatch.py` (host, SC#4 spot-check) | ✓ | system python3 | — |
| AVR toolchain (uno/leonardo) | `pio run -e uno/leonardo` sanity | ✓ (PlatformIO packages present at `~/.platformio/packages`) | — | native tests are the primary gate; AVR build is sanity-only |

**Missing dependencies with no fallback:** none.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Unity (via PlatformIO `[env:native]`) |
| Config file | `firestarter/platformio.ini` (`[env:native]`, line 69) |
| Quick run command | `pio test -e native -f "*test_dispatch*"` |
| Full suite command | `pio test -e native` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FW-01 | `protocol == 0` → fail-closed 0xBB | unit | `pio test -e native -f "*test_not_implemented*"` | ⚠️ NEEDS new `test_protocol_zero_fail_closes_not_implemented` (Wave-0/1, D-06) |
| FW-01 | every KNOWN_PROTOCOLS entry still dispatches | unit | `pio test -e native -f "*test_dispatch*"` | ✅ existing per-protocol tests |
| FW-02 | struct/parser field removed (compiles) | build | `pio test -e native` (link proves symbol gone) | ✅ compile is the check |
| FW-03 | `0xAE`/`TYPE_*` gone, no orphans | build + grep | `pio run -e uno` + `grep -rn "TYPE_EPROM\|MSG_ERR_MEM_TYPE" firestarter/` | ✅ grep + build |
| WIRE-01 | `type` field unknown-field-skipped | structural | (no test per D-05; parser allowlist proves it) | n/a |
| SC#4 | fallback dead for all real chips | integration | `cd firestarter_app && python tools/check_dispatch.py` | ✅ existing |

### Sampling Rate
- **Per task commit:** `pio test -e native -f "*test_dispatch*"` + `pio test -e native -f "*test_not_implemented*"`
- **Per wave merge:** `pio test -e native` (full native suite, all `test_val_*` golden traces)
- **Phase gate:** full `pio test -e native` green + `pio run -e uno` + `pio run -e leonardo` build + `check_dispatch.py` exit 0

### Wave 0 Gaps
- [ ] `test/native/avr/test_not_implemented/test_not_implemented.cpp` — add
  `test_protocol_zero_fail_closes_not_implemented` (covers SC#1 / FW-01, D-06). This is the ONLY
  net-new test; everything else is deletion.

*(No framework install needed — Unity + native env already configured.)*

## Security Domain

`security_enforcement` posture: this is a pure-removal firmware refactor with a safety-relevant
invariant. The relevant control is the **fail-closed dispatch** (12V-VPP hazard mitigation,
T-64-01 / BLOCKER-2): after removal, `protocol == 0` and any unknown protocol reach
`configure_not_implemented()` with zero hardware side effects. This *strengthens* the invariant
(removes the last path where an unknown/zero protocol could reach a VPP-enabling handler via
mem_type). No new attack surface. No ASVS web categories apply (embedded firmware, no auth/network
tier). The one hazard-relevant assertion: SAFE-01 — every dispatchable chip still routes to its
identical handler via `protocol` — is proven by the 746-chip scan (all non-zero) + the `test_val_*`
protocol-keyed golden traces + `check_dispatch.py`'s SRAM-never-reaches-configure_eprom guard.

## Sources

### Primary (HIGH confidence)
- `firestarter/src/proms/memory.cpp` (Read) — dispatch chain, guard, TYPE_* defines
- `firestarter/include/firestarter.h` (Read) — `mem_type` struct field
- `firestarter/src/json_parser.c` (Read) — 4 `type`-parse touchpoints
- `firestarter/include/messages.h` (Read) — `0xAE` define
- `firestarter/include/proto_constants.h` (Read) — v1.19 PROTO_ layer
- `firestarter/src/boards/rurp_serial_utils.cpp:374` (Read) — CRC8 table byte
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` (Read) — dispatch tests
- `firestarter/test/native/avr/test_not_implemented/test_not_implemented.cpp` (Read) — fail-closed tests
- `firestarter/test/native/avr/_shared/validation_matrix.h` (Read) — golden trace matrix
- `firestarter/platformio.ini` (Read) — native env config
- `firestarter_app/tools/check_dispatch.py` (Read) — host dispatch mirror
- `firestarter_app/firestarter/data/chip_database.json` (python scan) — 746 chips, 0 with algorithm==0
- git state (`git branch`, `git ls-tree beta`) — D-01 merge NOT performed

### Secondary (MEDIUM confidence)
- `firestarter/CLAUDE.md`, `firestarter_app/CLAUDE.md` — dispatch contract prose, lockstep rules

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new packages; existing PlatformIO/Unity verified present
- Architecture (dispatch shape, D-04 collapse): HIGH — quoted from actual current code
- Line references: HIGH — all verified against v1.19 checkout, accurate to ±1 line
- Non-regression proof: HIGH — 746-chip scan + protocol-keyed golden traces verified
- D-01 blocker: HIGH — git state directly inspected

**Research date:** 2026-07-02
**Valid until:** until the D-01 v1.19→beta merge lands (line numbers may shift by ±1 if beta had
divergent commits; verify `git ls-tree beta include/proto_constants.h` non-empty and re-grep the
8 line refs before executing). Stable otherwise (~30 days).
