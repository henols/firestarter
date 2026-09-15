---
title: Sweep gate dispositions — milestone v1.33, Phase 154
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "02"
measured: 2026-08-23
status: AUTHORITATIVE — the record that accounts for every gate this sweep can reach
requirements: [SWEEP-06]
---

# Sweep gate dispositions — v1.33 Phase 154

Every gate the sweep can reach is either **controlled** (a control exists or is added — plan
03 adds SWEEP-07's controls) or **recorded here as a named exposure with its cause**. A gate
absent from this file is an unrecorded exposure. Three sections: the 8 app-repo cross-repo
paths (D-05, SWEEP-06), the 22 non-comment-stripping firmware-repo gates (research F4,
Ruling D), and the blob-sha exemptions (research F3, Ruling B).

---

## Section A — the 8 app-repo cross-repo paths (D-05, SWEEP-06)

`firestarter_app/tests/scan_paths.py::ALL_CROSS_REPO_PATHS` is the authoritative,
non-derived inventory (read directly from the module, not re-derived by grep — its own
docstring explains why a mechanical derivation re-creates the `firestarter` name-collision
trap). Hit counts below are **measured by `survey_provenance.py`** against each path
individually, not copied from research.

| Path | Measured hits | Disposition | Cause |
|---|---|---|---|
| `test/native/avr/_shared/sdp_bus_config.h` | **0** | Generated — `tools/gen_sdp_bus_config.py` | 0 hits → provably needs no generator fix. Output never edited. |
| `test/native/avr/_shared/validation_matrix.h` | **0** | Generated — `tools/gen_validation_header.py` | 0 hits → provably needs no generator fix. Output never edited. |
| `doc/PROTOCOLS.md` | **2** | **Out of scope** (explicit ruling, not silence) | Outside the sweep's globs (`154-CONTEXT.md` `<domain>` names `firestarter/{src,include,test}` only). `test_dispatch_mirror.py`'s markdown leg reads it; that leg is unaffected because this file is never edited. |
| `include/firestarter.h` | **2** | In sweep | D-01 procedure applies; `CAP-01` at this file is D-02-exempt vocabulary. |
| `src/proms/eeprom_28c.cpp` | **33** | In sweep, **own plan** (SWEEP-08) | Densest file in the corpus; two comment-blind gate mechanisms live here (D-06 below). |
| `src/firestarter.cpp` | **8** | In sweep, **minus** the D-02 no-touch region (`:182-200`) | `test_cap03_ack_layout_parity.py` pins that block's raw text verbatim. |
| `src/json_parser.c` | **7** | In sweep | D-05's table said 8; measured (this session and research, matching) is 7. |
| `test/native/avr/test_dispatch/test_configure_memory.cpp` | **4** | In sweep, narrow treatment (D-04, test file) | — |

**SWEEP-06's "fixed at their generators or shown to need no fix" is discharged by
measurement:** both generated headers carry a **measured zero** provenance hits, so no
generator change is required and their output is never edited.

### D-06's comment-sensitivity table for the 7 app-repo test-side gates (corrected)

| Gate | Strips comments? | Negative control? | Verdict |
|---|---|---|---|
| `test_cap03_ack_layout_parity.py` | yes (`_strip_comments`) — but deliberately reads **raw** text for the pinned comment | yes | **Comment-SENSITIVE by design** → D-02 no-touch region |
| `test_json_key_parity.py` | no — matches `_KEY_STRING_RE` PROGMEM declarations, a code construct | yes — `planted_json_parser_key_string_drift.c`, `planted_json_parser_undispatched_key.c` | **Safe**, already proven safe |
| `test_revision_constants_parity.py` | yes | yes (28 fixture refs) | Safe |
| `test_check_no_log_in_sdp_window.py` | yes (in its `tools/` checker) | yes (35 refs, incl. the comment-not-a-call control) | Safe |
| `test_check_is_memory_cmd_no_ifdef.py` | yes | yes (25 refs) | Safe |
| `test_sdp_table_parity.py` | **no** | **no** | **The one genuinely dangerous gate.** No comment stripping, no planted-violation fixture. Research F2 **proved** it fail-open: `0xA0`→`0x10` (SDP lock → chip erase) reported **5 passed**. **Correction to the writeup's "Negative control? no" reading:** it *does* ship a non-vacuity leg (`test_altered_temp_copy_fails_parity_non_vacuous`) and a purpose-built `FIRESTARTER_SDP_SRC` planting seam — what it actually lacks is a control exercising either comment-blind mechanism (the `_PAIR_RE` literal-in-comment collision, and the comment-blind brace slice). Plan 03 adds that control. |
| `test_dispatch_mirror.py` | **no** | **no** | Uncontrolled. C++ leg (`test_configure_memory.cpp`) in sweep scope; markdown leg (`doc/PROTOCOLS.md`) out of globs. Plan 03 adds the C++ leg's controls. |

---

## Section B — the 22 non-comment-stripping firmware-repo gates (research F4, Ruling D)

**SWEEP-06's requirement text is NOT expanded.** It stands exactly as written over the 8
app-repo paths above. The 22 firmware-repo gates below are **dispositioned and recorded as
a named exposure where warranted**, not controlled by this phase — building 22 planted
controls is a separate follow-on phase (filed at the end of this section).

Research assumption A3 flags that the 22 were originally classified by mechanical
presence/absence of a `_strip_comments`-named helper **inside the test file itself**, rather
than by reading each gate's actual extraction mechanism (which may live in a subprocess
script, or may not be a text-pattern scan of comment content at all). Every row below was
re-classified by reading the gate's own mechanism; every `EXPOSURE` row says so explicitly,
per A3.

Overlap ("touches?") is answered from `survey_provenance.py`'s per-file hit table (task 1/2
of this plan), never by guess.

| # | Module | Source path(s) scanned | Touches a hit-bearing file? | Disposition | Cause |
|---|---|---|---|---|---|
| 1 | `test_check_erase_no_vpp.py` | `scripts/check_erase_no_vpp.py` (subprocess) → `src/proms/eeprom_28c.cpp` | Yes — `eeprom_28c.cpp` (33 hits) | **control** | The invoked checker script (`check_erase_no_vpp.py`) defines and calls `_strip_comments` internally before its brace-matched scan. A3's blind spot exactly: the stripper lives in the subprocessed script, not in the test file the original grep checked. |
| 2 | `test_check_landing_range.py` | `scripts/check_landing_range.py` (subprocess) — git-log commit-presence over named files (`include/rurp_platform_compat.h`, `include/avr/pgmspace.h`, `platform/py32f071/`) | No — neither named file carries a measured hit | **no-overlap** | Mechanism is git-history commit-shape (which commits carry which file paths), not a text/comment scan; structurally immune to comment-only edits regardless. |
| 3 | `test_check_orphan_provisional.py` | `scripts/check_orphan_provisional.py` (subprocess) — repo-wide `RURP_*_PROVISIONAL` macro/consumer scan | Yes (repo-wide `include`/`src` scan reaches hit-bearing files) | **control** | The invoked checker defines and calls `_strip_comments` internally. Same A3 blind spot as #1. |
| 4 | `test_check_cmake_manifest.py` | `scripts/check_cmake_manifest.py` (subprocess) — `platform/py32f071/CMakeLists.txt` `set()` source-list membership by **filename** | Manifest file itself is out of glob scope; the source *filenames* it checks for membership include several hit-bearing files, but only their presence-in-list is checked | **control** | Mechanism is filename-list membership (does `flash_5v_page.cpp` appear in the manifest's `set()`?), never file **content**. A comment-only edit inside a file changes nothing this gate reads. |
| 5 | `test_checker_convention.py` | `scripts/` + `tests/` (the checker/test files themselves — a meta convention gate) | No — neither `scripts/` nor `tests/` is a sweep target | **no-overlap** | The sweep's globs are `firestarter/{src,include,test}` (singular `test`); this gate scans the firmware repo's own Python gate suite and its checker scripts, neither of which the sweep touches. |
| 6 | `test_config_schema_pinned.py` | `include/rurp_types.h` (0 hits), `include/rurp_shield.h` (4 hits), `platform/py32f071/src/config_storage_dualslot.h` (out of scope), `src/rurp_config_utils.cpp` (0 hits) | Yes — `rurp_shield.h` | **control** | Verified safe (research F3): computes struct-field SHAs / structural violations at runtime and contains no blob-SHA literal; its declared-field extraction targets struct syntax, not comment text. |
| 7 | `test_vpp_seam_manual_on_every_board.py` | `include/rurp_vpp.h` (1 hit), `src/rurp_vpp.cpp` (1 hit), `platformio.ini`, py32 board header/CMake | Yes — both `rurp_vpp.h` and `rurp_vpp.cpp` | **EXPOSURE** | `_expected_header_error_text()`/`_expected_source_error_text()` use `re.search(r'#\s*error\s+"([^"]*)"', text)` on the **raw, unstripped** file text with no stripper anywhere in this module. A `#error "..."`-shaped string sitting inside a reflowed comment above the real directive would satisfy `.search()`'s first-match semantics before the code reaches it — the same first-match-wins shape research proved fail-open in `test_sdp_table_parity.py` (F2). Classified by reading the gate's own regex, per A3's instruction, not by presence/absence of a named stripper. |
| 8 | `test_flash_geometry_recorded_before_linker.py` | `platform/py32f071/CONFIG-STORAGE.md`, `platform/py32f071/linker/PY32F071xB_FLASH.ld` | No — both under `platform/`, entirely outside the sweep's `{src,include,test}` globs | **no-overlap** | — |
| 9 | `test_config_storage_seam_shape.py` | `include/rurp_shield.h` (4 hits), `include/rurp_config_storage.h` (1 hit), `src/rurp_config_utils.cpp` (0 hits), `src/boards/rurp_config_storage_eeprom.cpp` (0 hits) | Yes — `rurp_shield.h`, `rurp_config_storage.h` | **control** | Verified safe (research F3, and independently confirmed this session): the module defines its own `_COMMENT_RE = re.compile(r"/\*.*?\*/\|//[^\n]*", re.DOTALL)` and strips before its declaration-extraction logic. Computes SHAs at runtime; contains no blob-SHA literal. |
| 10 | `test_check_size_baseline.py` | `scripts/check_size_baseline.py` (subprocess) — `scripts/baseline/size_baseline.json` byte/case-count comparison against a live `pio` build | Reads compiled-artifact byte counts, not source text | **control** | Structurally immune, same class as SWEEP-05's own oracle: `154-RESEARCH.md`'s Validation Architecture measured that deleting 1,827 comment lines across 31 files left both `.elf` and `.hex` unchanged (project sources compile with no `-g`). A byte-count comparator cannot be perturbed by a comment-only sweep. |
| 11 | `test_check_build_warnings.py` | `scripts/check_build_warnings.py` (subprocess) — parses captured `pio run`/`pio test` compiler-warning output against `scripts/baseline/size_baseline.json`'s `warnings` policy | Reads compiler **output**, not source text | **control** | Same structural-immunity class as #10: a comment-only edit cannot change what the compiler emits to stderr. |
| 12 | `test_config_storage_design_vendored.py` | `platform/py32f071/CONFIG-STORAGE.md` | No — `.md` under `platform/`, outside both the extension list and the sweep globs | **no-overlap** | — |
| 13 | `test_config_storage_eeprom_regression.py` | `src/rurp_config_utils.cpp`, `src/boards/rurp_config_storage_eeprom.cpp` (both filtered to files that exist at collection time) | No — both files measured at **0** hits | **no-overlap** | Neither candidate source file carries a provenance hit. |
| 14 | `test_py32_flash_map.py` | `platform/py32f071/{linker/PY32F071xB_FLASH.ld, CMakeLists.txt, CONFIG-STORAGE.md, src/config_storage_flash.cpp, src/config_storage_dualslot.cpp, src/config.cpp}` | No — all under `platform/`, outside the sweep globs | **no-overlap** | This module also defines its own `_COMMENT_RE` and strips before its HAL-call extraction, as a second, independent reason it would be safe even if its targets were in scope. |
| 15 | `test_check_release_assets.py` | `scripts/check_release_assets.py` (subprocess) — built `.hex` presence/size + `scripts/baseline/size_baseline.json` + `.github/workflows/beta-build.yml` | Reads build-artifact presence, not source text | **control** | Structurally immune, same class as #10/#11. |
| 16 | `test_flash_path_record_sync.py` | `platform/py32f071/{FLASH-PATH-AND-PCB.md, README.md, linker/PY32F071xB_FLASH.ld}`, a `.planning/` meta doc, whole-repo git porcelain | No — all named targets are under `platform/` or `.planning/`, outside the sweep globs | **no-overlap** | This is also the D-11 ordering gate (whole-repo porcelain must be clean before the host suite runs); unrelated to comment content. |
| 17 | `test_pr45_non_ancestry.py` | git-log ancestry (`--is-ancestor`-style reachability against `feature/common-vpp-calibration`) + blob-content divergence of `include/rurp_vpp.h` / `src/rurp_vpp.cpp` against PR #45's historical blobs | Yes — both files, but against a **fixed historical comparison point**, not live content matching | **control** | The assertion is "not identical to / not descended from PR #45's blobs." Both seam files already diverge from PR #45's content today (they were authored after PR #45 closed); a comment-only sweep can only widen that divergence, never narrow it back toward equality with the banned historical blobs. Monotonic — structurally immune in the direction that matters. |
| 18 | `test_golden_trace_identity_eprom_v131.py` | `tests/golden/eprom_v131_trace_inventory.json` (blob-sha sidecar) + `test/native/avr/_shared/eprom_v131_expected.h` + `_CONSUMERS` `#include`-presence check | Yes — `eprom_v131_expected.h` (4 hits) | **control** — cross-referenced to **Section C** | This is one of the four F3 blob-sha-pinned gates. `eprom_v131_expected.h` is **exempted from the sweep entirely** (Section C); the `_CONSUMERS` check only verifies an `#include` directive is still present, which a comment-only edit cannot remove. |
| 19 | `test_config_storage_dualslot.py` | `platform/py32f071/src/config_storage_dualslot.cpp` (primary target); `include/` passed only as a path argument (not read for pattern-matching) | No — primary target is under `platform/`, outside the sweep globs | **no-overlap** | — |
| 20 | `test_golden_trace_identity.py` | `tests/golden/sdp_expected_inventory.json` (blob-sha sidecar) + `test/native/avr/_shared/sdp_expected.h` + `_CONSUMERS` `#include`-presence check | Yes — `sdp_expected.h` (3 hits) | **control** — cross-referenced to **Section C** | Same shape as #18: the pinned header is exempted (Section C); the consumer check is `#include`-presence only. |
| 21 | `test_update_version.py` | none of the real repo's files — every test builds a synthetic `version.h` fresh under `tmp_path` and monkeypatches the script's `header_file` constant to point at it | No — never reads the real `include/version.h` | **no-overlap** | Pure unit test against synthetic fixtures; the real firmware tree is never touched by any assertion in this module. |
| 22 | `test_pinmap_guard_fires.py` | `include/boards/py32f071_pinmap_guard.h` (1 hit), `include/boards/py32f071_rurp_shield.h` (2 hits) | Yes — both files | **EXPOSURE** | `_expected_error_text()` uses `re.search(r'#error\s+"([^"]*)"', text)` on raw text with no stripper — same first-match-wins shape as #7. The test does also invoke a **real preprocessor** to prove the guard fires functionally, which is a genuine oracle for the *compile behaviour*; the exposure is narrower than #7 (only the expected-text extraction, not the guard's actual firing, is comment-blind), but is still real and unverified. |

**Summary:** 5 `control` gates in the 22 have their own genuine comment-blind mechanism
(`_strip_comments` in the invoked checker, `_COMMENT_RE` defined locally, or structural
immunity via byte-count/build-artifact/git-ancestry comparison); 2 (`#18`, `#20`) are
`control` by cross-reference to Section C's blob-sha exemption; 2 (`#7`, `#22`) are genuine
`EXPOSURE`; the remaining 13 are `no-overlap` because the sweep never touches the specific
file(s) each one reads.

**Deferred / follow-on, filed here, not built here:** the two `EXPOSURE` rows (`#7`
`test_vpp_seam_manual_on_every_board.py`, `#22` `test_pinmap_guard_fires.py`) need
planted-violation controls of the same shape SWEEP-07 builds for `test_sdp_table_parity.py`
and `test_dispatch_mirror.py` — a decoy `#error "..."` string inside a comment placed above
the real directive, proven to either get caught or not. **This is a real follow-on phase,
not built in Phase 154.** Building controls for all 22 gates (even the `no-overlap` and
structurally-immune `control` rows, as defense in depth) is a larger, separate follow-on
also filed here rather than scoped into this phase.

---

## Section C — the blob-sha exemptions (research F3, Ruling B)

Four committed golden sidecars in the **firmware** repo pin `git rev-parse HEAD:<path>`
blob SHAs of five source files carrying **30** provenance hits, and no regeneration tool
exists in this repo today.

**Ruling B: regenerate `eprom_params_citations.json` only.** `src/proms/eprom_params.cpp`
is one of SWEEP-01's five *named* keep-and-reflow examples (`eprom_params.cpp:61` — the
fail-closed-return rationale), so it must still be swept and delivered, not exempted. Its
one pinning sidecar this plan commits to regenerating is `eprom_params_citations.json`
(plan 07, same commit as the firmware sweep).

**Exempt the other four pinned files from the sweep**, each named with the sidecar that
pins it and its measured hit count:

| File | Hits | Pinning sidecar |
|---|---|---|
| `include/eprom_params.h` | 1 | `tests/golden/eprom_params_citations.json` |
| `src/proms/eprom.cpp` | 20 | `tests/golden/protocol_branch_inventory.json` |
| `test/native/avr/_shared/eprom_v131_expected.h` | 4 | `tests/golden/eprom_v131_trace_inventory.json` |
| `test/native/avr/_shared/sdp_expected.h` | 3 | `tests/golden/sdp_expected_inventory.json` |

**Total exempted: 28 of 615 hit lines.** Cause, stated in one sentence: **an un-swept file
that looks swept is worse than a recorded exemption** — leaving these four with their
provenance comments intact and named here is honest; sweeping them without regenerating
their sidecars would turn four gates RED for a reason a reader would misdiagnose as a
comment-sweep defect (Pitfall 6, `154-RESEARCH.md`).

### The double-pin consequence, discovered while planning (Ruling B does not name it)

`src/proms/eprom_params.cpp` is pinned by **two** sidecars — `eprom_params_citations.json`
**and** `protocol_branch_inventory.json` — verified directly against both files' `meta.blob_shas`
maps this session (both currently read `5dffe841aeb7013f9f53e9991a6248b203ae22da`). Sweeping
it (per Ruling B, since it is a named keep-and-reflow file, not exempted) requires updating
the `src/proms/eprom_params.cpp` entry in **both** `meta.blob_shas` maps, in the same
firmware commit, and leaving the `src/proms/eprom.cpp` entry in `protocol_branch_inventory.json`
**untouched** because that file is exempt.

Two verified facts that bound the regeneration, so plan 07 knows exactly how narrow the
edit is:

1. **Neither sidecar's non-`blob_shas` content depends on `eprom_params.cpp`'s line
   numbers.** `eprom_params_citations.json`'s `cells` array carries
   `row`/`column`/`value`/`basis`/`reasoned_from`/`notes` — no line field at all (verified:
   `cells[0]` keys are exactly those six). `protocol_branch_inventory.json`'s line-bearing
   `sites` array (`line`/`predicate`/`keyed_on`/`tier`/`class`/`reason`) is extracted from
   `src/proms/eprom.cpp` **only** — `eprom.cpp` is exempt and unedited, so `sites` needs no
   change — and its separate `params_table` scan of `eprom_params.cpp` is
   **comment-stripped** already (verified: `protocol_branch_inventory.json` has a
   `params_table` key, and the extraction that produces it strips comments before parsing),
   so it is immune to the sweep's comment-only edit regardless.
2. **The gate's own instruction is to re-derive the SHA, not hand-edit it.**
   `test_eprom_params_citations.py`'s failure message says exactly this. It is satisfied by
   `git hash-object src/proms/eprom_params.cpp` run against the post-sweep working tree,
   since a blob SHA is content-addressed and will equal what `git rev-parse
   HEAD:src/proms/eprom_params.cpp` reports once the sweep commit lands.

### `src/proms/eprom.cpp`'s standing and whether exempting it changes the manifest's shape

`src/proms/eprom.cpp` is the **most-cited file in `.planning/` at 627 citations**
(research-measured). Its exemption from this sweep raises a real question for plan 04's
citation manifest: does exempting a file change the manifest's row set?

**Answer: no**, unless plan 04's own measurement contradicts it. The manifest is generated
over the pre-sweep **candidate** set — every file under the sweep's globs carrying at least
one hit, which includes `eprom.cpp` regardless of whether it ends up exempted afterward.
Recording a citation into a file that turns out untouched is harmless: its `source_text`
still matches at its recorded line, so Phase 159's fixed-point round-trip check makes that
record a no-op rewrite. Exempting a file changes only the *actual swept set* that plan 12's
staleness marker names, never the manifest's row set — the manifest is built from what
*could* have moved, not from what did.
