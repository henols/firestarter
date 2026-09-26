# Phase 126: Flash-Persistent Config via a Storage-Backend Seam - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-31
**Phase:** 126-flash-persistent-config-via-a-storage-backend-seam-highest-r
**Areas discussed:** Test venue & the 141/17 pin, Storage seam API contract, py32 flash map & install, Blank/corrupt-slot behavior

**Area selection:** all four offered gray areas were selected.

---

## Test venue & the 141/17 pin

### Q1 — Where does the six-function fake-backend suite run?

| Option | Description | Selected |
|--------|-------------|----------|
| pytest + g++ under `tests/` (Recommended) | Phase 125's precedent; leaves the pinned 141 cases / 17 suites untouched. Runs in zero CI legs on this branch, so it is a local-run-recorded-verbatim proof | ✓ |
| New PIO `test/native/` suite | A real Unity suite, CI-covered — but moves both pinned numbers inside the phase whose premise is that nothing else moved | |
| Both — PIO suite + pytest harness | Costs the re-baseline anyway, plus two harness idioms in one phase | |

**User's choice:** pytest + g++ under `tests/`
**Notes:** → D-01.

### Q2 — What is actually under test, the shipped algorithm or a copy?

| Option | Description | Selected |
|--------|-------------|----------|
| HAL-free core, shared (Recommended) | Dual-slot logic takes injected read/erase/program primitives; the same `.cpp` is compiled by the py32 backend and by the host test | ✓ |
| Compile the py32 `.cpp` with a fake HAL shim | Same-file fidelity, no extra TU — but the stub header becomes an unversioned mirror of a pinned FetchContent SDK | |
| Independent fake reimplementation in the test | Fastest — but proves a copy behaves; the hollow-gate shape Phases 118/124 each unwound | |

**User's choice:** HAL-free core, shared
**Notes:** → D-02. Recorded in CONTEXT `<specifics>` as the most consequential decision in the phase.

### Q3 — Where does that core live?

| Option | Description | Selected |
|--------|-------------|----------|
| `platform/py32f071/src/` (Recommended) | ARM-only; host test compiles by explicit path. Zero new bytes in any AVR build | ✓ |
| `src/` (shared common code) | Platform-neutral and reusable — but compiles into all three AVR targets, needing a three-target measurement | |
| Header-only in `include/` | No TU at all — but invisible to `check_cmake_manifest.py`'s reverse check | |

**User's choice:** `platform/py32f071/src/`
**Notes:** → D-03.

### Q4 — How is Criterion 3's "empty git diff on the test file" discharged?

| Option | Description | Selected |
|--------|-------------|----------|
| Two commits + blob-SHA re-hash (Recommended) | Test written against pre-refactor code, proven green, blob SHA recorded; path-scoped diff is corroboration only | ✓ |
| Two commits + path-scoped `git diff` | The ROADMAP's literal wording — the mechanism twice recorded as able to pass on a wrong path | |
| Test written after the refactor | Cheaper — but it never observed the behaviour it claims to match | |

**User's choice:** Two commits + blob-SHA re-hash
**Notes:** → D-04. Surfaced a follow-on the planner must handle: the test file must name **both** the pre- and post-refactor TU paths from the start, or the empty-diff proof is unsatisfiable. Recorded as a Discretion default.

---

## Storage seam API contract

### Q1 — What shape do the two backend functions take?

| Option | Description | Selected |
|--------|-------------|----------|
| `bool` load / `bool` save (Recommended) | py32 reports "no valid record" honestly; AVR returns true unconditionally so AVR behaviour stays byte-identical | ✓ |
| `void` load / `void` save | Literal mirror of `EEPROM.get`/`put` — but blank becomes indistinguishable from loaded zeros | |
| Richer status enum | Diagnostic value — but invents vocabulary with no consumer | |

**User's choice:** `bool` load / `bool` save
**Notes:** → D-06.

### Q2 — Which functions stay common vs cross into the backend?

| Option | Description | Selected |
|--------|-------------|----------|
| All four stay common (Recommended) | Only the two byte-blob calls cross the seam; PR #48's `config.cpp` is deleted, not reconciled | ✓ |
| Validation also per-platform | Would re-create the exact duplication that produced PR #48's drift | |
| `CONFIG_START` offset per-platform | Cleaner separation — but CFG-04 asserts offset 48 explicitly | |

**User's choice:** All four stay common
**Notes:** → D-07. Follow-on recorded: `CONFIG_START 48` is an EEPROM address and moves into the AVR backend TU; CFG-04's test asserts it there.

### Q3 — Where does the AVR EEPROM backend TU live, and what happens to the ARM manifest?

| Option | Description | Selected |
|--------|-------------|----------|
| `src/boards/` + swap the exclusion (Recommended) | New TU gets a `# PY32_EXCLUDED:` line; `rurp_config_utils.cpp` is added to `FIRESTARTER_COMMON_SOURCES` and its existing exclusion deleted | ✓ |
| `src/` top level | Keeps the two config TUs adjacent — but puts AVR-only hardware code outside `boards/` | |
| `#ifdef __AVR__` inside the policy file | Cheapest diff — but "per-platform backend" becomes true only because the file says so | |

**User's choice:** `src/boards/` + swap the exclusion
**Notes:** → D-08. The exclusion being removed carries its own in-tree comment naming Phase 126.

### Q4 — Who includes `include/rurp_config_storage.h`?

| Option | Description | Selected |
|--------|-------------|----------|
| Only the three TUs that need it (Recommended) | `rurp_shield.h` untouched; the four public declarations stay where they are | ✓ |
| Declare it in `rurp_shield.h` | One config header — but that header reaches 46 TUs including 14 native `host_stubs.cpp`, the exact C-1 surface | |
| No header — extern declarations in the policy TU | Smallest surface — but the seam becomes invisible and a future platform has nothing to implement against | |

**User's choice:** Only the three TUs that need it
**Notes:** → D-09. Phase 125's C-1 (141/141 → 17 suites / 0) applied before the fact.

---

## py32 flash map & install

**Grounding fact established before the questions:** the host's `py32_dfu.py` erases only the sectors needed for the payload (`erase_addresses(layout, base, len(payload), …)`, `:750`); `FLASH_BASE`/`FLASH_SIZE` (`:107–108`) are a refusal envelope (`:648`), not an erase bound.

### Q1 — Where do the two config pages sit?

| Option | Description | Selected |
|--------|-------------|----------|
| Top of flash, `FLASH` LENGTH shrunk (Recommended) | DFU erase is payload-scoped so an install preserves them; a future bottom-of-flash bootloader never forces config to move | ✓ |
| Bottom, after a reserved bootloader region | Keeps bootloader-adjacent things together — but shrinks app flash for code that does not exist | |
| Fixed addresses, LENGTH left at 128K | Smallest linker diff — but overlap becomes a convention | |

**User's choice:** Top of flash, `FLASH` LENGTH shrunk
**Notes:** → D-10.

### Q2 — How is the reservation expressed?

| Option | Description | Selected |
|--------|-------------|----------|
| Second `MEMORY` region + `PROVIDE` symbols (Recommended) | Linker structurally enforces non-overlap; the erase-unit property is readable in one place | ✓ |
| `PROVIDE` symbols only, one FLASH region | Fewer moving parts — but overlap is convention, not constraint | |
| Compile-time defines in the CMake target | Criterion 5 says "linker symbols", and it splits the map across two files | |

**User's choice:** Second `MEMORY` region + `PROVIDE` symbols
**Notes:** → D-11.

### Q3 — Who owns host `FLASH_BASE`/`FLASH_SIZE` consistency, given Phase 127 runs in parallel?

| Option | Description | Selected |
|--------|-------------|----------|
| 126 records the contract + a gate, 127 satisfies it (Recommended) | Stays firmware-only; `FLASH_SIZE` stays the physical 128 KiB refusal envelope; consistency becomes a test | ✓ |
| 126 edits the host file directly | Guarantees agreement — but the file only exists on an unmerged branch 127 then merges over | |
| Defer the whole host half to Phase 127 | Criterion 5 names the consistency explicitly; "the later phase will look" is how a flash-map disagreement survives to a board | |

**User's choice:** 126 records the contract + a gate, 127 satisfies it
**Notes:** → D-12. Two checked facts recorded for Phase 127: `scan_paths.py`'s `CROSS_REPO_TEST_PATHS` has no linker-script entry, and BASE-02 requires repo-presence keyed on `../firestarter/.git`.

### Q4 — Does this phase reserve bootloader flash?

| Option | Description | Selected |
|--------|-------------|----------|
| No — config only; 129 records the intent (Recommended) | A reservation with no implementation and no consumer comes back with a consumer attached, or not at all | |
| Yes — reserve a bootloader region now | 129 could cite a real address for both — but the size would be a guess | |
| Reserve a symbolic zero-length placeholder | Names the address so 129 cites a symbol; trivially resized later | ✓ |

**User's choice:** Reserve a symbolic zero-length placeholder — **operator override of the recommendation.**
**Notes:** A factual wrinkle was surfaced in response and accepted: a top-of-flash config region grows downward without moving anything, but a bottom-of-flash bootloader placeholder does **not** — giving it non-zero length moves the app's `ORIGIN`, a flash-map migration rather than a resize.

### Q4b — Given that, what does the placeholder assert?

| Option | Description | Selected |
|--------|-------------|----------|
| Named seam + honest non-claim (Recommended) | Zero-length region with a comment stating both why it exists and that resizing it is a migration; 129 records the budget as an intent with that cost attached | ✓ |
| Pick a real size now instead | App `ORIGIN` never moves again — but it is a guess about code that does not exist | |
| Drop the placeholder | Cleanest linker script — but 129 would have no in-tree symbol to cite | |

**User's choice:** Named seam + honest non-claim
**Notes:** → D-13. The planner must implement it as chosen — not quietly upgrade it to a real reservation, not quietly drop it.

---

## Blank/corrupt-slot behavior

### Q1 — What does py32 do at first boot?

| Option | Description | Selected |
|--------|-------------|----------|
| Persist immediately — policy unchanged (Recommended) | `rurp_validate_config`'s write-back fires exactly as on AVR; one policy, one behaviour, both platforms | ✓ |
| RAM-only until an explicit save | No startup flash write — but forks validate by platform, the exact drift CFG-07 requires deleted | |
| Persist, deferred until after USB enumerates | Most defensive — but invents a lifecycle hook no other platform has | |

**User's choice:** Persist immediately — policy unchanged
**Notes:** → D-14. The startup flash-stall cost is unmeasurable without a PCB and is recorded as *not measured*, never as *acceptable*.

### Q2 — What does the backend return when both slots fail CRC?

| Option | Description | Selected |
|--------|-------------|----------|
| Both return false; policy can't tell them apart (Recommended) | One recovery path to test; the two tests stay separately named and assert the same outcome from different inputs | ✓ |
| Distinguish them for logging | Real diagnostic value — but needs the declined status enum plus a `messages.toml` round-trip | |
| Corrupt-both is fatal — refuse to run | Safest reading — but would brick a unit on the first flash-wear event | |

**User's choice:** Both return false
**Notes:** → D-15.

### Q3 — What does "interrupted write" mean concretely?

| Option | Description | Selected |
|--------|-------------|----------|
| Erase-then-program the INACTIVE slot, CRC last (Recommended) | The active slot is untouched until the new one is complete — blob `4b1a441`'s stated property; fake aborts at each step boundary | ✓ |
| Torn-write at arbitrary byte offsets | Stronger property — but a much larger matrix against unobservable controller behaviour | |
| Power-loss as random 0xFF/garbage fill | Broad coverage — but the patterns are invented, so a pass proves the model | |

**User's choice:** Erase-then-program the INACTIVE slot, CRC last
**Notes:** → D-16.

### Q4 — Do we vendor `StoredConfiguration` verbatim?

| Option | Description | Selected |
|--------|-------------|----------|
| Verbatim, with the struct embedded unchanged (Recommended) | Every field earns its place; embedding `rurp_configuration_t` byte-for-byte makes CFG-07's "schema unchanged" structurally true | ✓ |
| Narrow it — drop magic and length | Smaller record — but deviates from the one design this phase is chartered to vendor | |
| Redesign the wrapper | CFG-01 asks for the closed-PR design vendored with superseded parts marked, not replaced | |

**User's choice:** Verbatim, with the struct embedded unchanged
**Notes:** → D-17. Recorded explicitly: the wrapper's `version` (u16) is **not** `CONFIG_VERSION` (`char[6] "VER06"`).

---

## Claude's Discretion

Locked as defaults with stated reasoning in CONTEXT.md `<decisions>` § "Claude's Discretion":

- CRC32 implementation — bitwise reflected `0xEDB88320`, no table, in the HAL-free core TU, anchored by a known-answer vector.
- Sequence-number wraparound — `uint32_t` monotonic, no rollover branch (flash endurance bounds it far below 2³²).
- Where CFG-01's vendored design lives — a focused `platform/py32f071/CONFIG-STORAGE.md` with a SUPERSEDED block, **not** a restoration of `PORTING.md` under its own name.
- How CFG-02's page size is recorded and its commit-ordering proven (`git rev-list --is-ancestor` as an exit code).
- Evidence artifact — `126-NONREGRESSION.md` in the `123-/124-/125-` row shape.
- The CFG-04 test's compile-target stability across the refactor.
- Plan/wave decomposition and commit granularity, subject to the forced AVR-first ordering.
- The push gate — no task runs `git push`/`gh workflow run`; the plan prints and stops.

## Deferred Ideas

- Distinguishing blank from both-corrupt on the wire.
- A richer backend status enum.
- Reserving real bootloader flash (FUT-N05).
- Torn-write and random-fill power-loss test matrices.
- Deferring the first-boot flush until after USB enumeration.
- Proving a DFU install preserves config (needs silicon — carry as a non-claim to Phase 130).
- Shrinking the host's `FLASH_SIZE` to the app region.
- A native no-op storage backend so the policy layer could be natively tested.
- FUT-ARMSIZE — ARM flash/RAM as a checked-in baseline with a RAM ceiling.

14 todos matched on generic keywords; **none folded**. See CONTEXT.md `<deferred>` § "Reviewed Todos".
