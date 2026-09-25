# Spec: Trim the submodule CLAUDE.md files and retire the PY32 twin

## Context

`firestarter_fw/CLAUDE.md` (433 lines) and `firestarter_app/CLAUDE.md` (221 lines) hold real value:
commands, CI traps and safety invariants. About half of each file is noise:

- **Duplicated** in `agent-os/standards/`: constant pairs, retired ordinals, codegen rule, native-suite
  registration, ack layout / "0 = not sent", HV teardown.
- **Derivable from code, and it drifts**: key-file lists, the dispatch order and handler table, the 27C
  per-row table, the energy-cap arithmetic, the list of mypy-strict modules (which says "Do not trust
  this list").
- **Stale**: the PY32 flash-path section. It describes a twin of
  `.planning/milestones/v1.23-FLASH-PATH-DECISION.md`, and meta commit `1ea94a1e` deleted that file.
  There are also GSD-era references ("v1.37 Phase 182").

The files stay in the submodules, because Claude Code loads them only when it works in that subtree,
and because each submodule can be checked out on its own. The root CLAUDE.md gets a pointer to the
standards index. It has no such pointer today.

The PY32 twin guard (`tests/test_flash_path_record_sync.py`, 1146 lines, plus
`tests/meta_presence.py`) reads the meta repo and scans text. It breaks
`testing/standalone-checkout` and `testing/no-source-introspection`. Its parent file is gone, so
`platform/py32f071/FLASH-PATH-AND-PCB.md` becomes the only record.

## Shaping decisions

- **D-1. Scope**: trim both submodule CLAUDE.md files in place, retire the PY32 twin, and add a
  standards pointer to the root CLAUDE.md. Do not merge the files into the root.
- **D-2. Branches**: use the current branches. fw and app are on `v1.42-jumper-display`, meta is on
  `experiment/agent-os`. Advance the gitlinks in meta. Do not push.
- **D-3. PY32 doc**: `FLASH-PATH-AND-PCB.md` becomes authoritative. Delete the twin test and
  `meta_presence.py`. Do not recover the parent-only sections (§1, §7–9). Name meta commit
  `1ea94a1e^` as the place where they still exist.
- **D-4. Standards**: `testing/no-source-introspection`, `testing/standalone-checkout`,
  `protocol/duplicated-constants`, `protocol/retired-ordinals`, `protocol/message-catalog`.
- **D-5. Keep/drop rule**: keep a line only if the code or CI config does not show it, **and** getting
  it wrong is costly (publishes a release, damages a part, gives a false green, or edits a generated
  file). If a standard covers it, replace it with a one-line pointer to that standard.

## Task 1: Save spec documentation

Create `agent-os/specs/2026-09-25-1929-claude-md-trim-py32-twin/` with:

- **plan.md**: this plan.
- **shape.md**: scope, D-1..D-5, and the context (visuals: none. references: the info-jumper-table
  spec as the format model. product: the mission's "honest claims" and "fail closed" rules).
- **standards.md**: the full text of the 5 standards in D-4.
- **references.md**: `agent-os/standards/index.yml` (the target of the pointers), and
  `agent-os/specs/2026-09-25-1503-info-jumper-table/` (the format).
- No `visuals/` folder.

## Task 2: Retire the PY32 twin (firestarter_fw)

1. Delete `tests/test_flash_path_record_sync.py` and `tests/meta_presence.py`. No other module imports
   `meta_presence`. `test_jsmn_token_layout_source_contract_v158.py:108` and
   `test_trace_segment_exhaustiveness_v131.py:114,894` only name it in docstrings or comments. Leave
   those two files alone, because they are legacy source contracts and are out of scope.
2. `platform/py32f071/FLASH-PATH-AND-PCB.md`:
   - Replace the header (lines 3–5) with a statement that this file is the record for the PY32F071
     flash path and PCB, and that the retired meta parent (silicon corrections §1.6, rejected routes,
     obligations, open questions) is in meta history at `1ea94a1e^`.
   - Remove the `[SHARED:Sn]` suffixes from the 5 headings.
   - Remove the 5 footers that say "This section is shared verbatim with ...".
   - Rewrite each sentence that points to the missing parent or to a missing `.planning/` file (lines
     98, 116, 120, 145, 151). Keep the technical fact. Remove the dead pointer. Do not rewrite other
     prose.
3. `platform/py32f071/linker/PY32F071xB_FLASH.ld:12`: remove the `.planning/v1.23-...` pointer from
   the comment.
4. `platform/py32f071/src/usb_cdc.c:42` says "section 5". Change it to the section name
   ("USB vendor and product identity"), because the section is no longer numbered by marker.
5. `platform/py32f071/README.md:148` already points to the section by name. No change.
6. Commit: `test: retire the PY32 flash-path twin; the fw doc is now the record`.

## Task 3: Trim `firestarter_fw/CLAUDE.md` (target about 120 lines)

**Keep**, and make shorter where you can:
- Build commands and the environment list.
- The CI table: `build.yml` cuts a **stable** release on a push to `main`, and `beta-build.yml`
  publishes on **every** push to `beta` (it has no path filter). Also keep the `build.yml` path-ignore
  list and the fact that `pytest` needs `fetch-depth: 0`.
- The two test trees, as one line with a pointer to `testing/no-source-introspection`.
- Dev-tools channel: the stable image refuses the dev commands, the `PLATFORMIO_BUILD_FLAGS` build
  gives a local beta image, and CI checks both directions.
- Dispatch invariants (short): dispatch uses `handle->protocol` only. SRAM protocols never go to
  `configure_eprom` (12V hazard). Unknown, zero and infeasible values go to
  `configure_not_implemented()` (fail closed). The pin-map gate runs before dispatch. For the exact
  order, read `configure_memory` in `src/proms/memory.cpp`.
- The 27C facts the code does not show: a successful block leaves the HV route on, and
  `command_done()` clears it. Progress `0xE0` is time-keyed and sent on leonardo/native only (the Uno
  frame-loss chain). There is no program-VCC raise (an accepted limit). Where the values are:
  `eprom_params.cpp`.
- The `0x08` drop bit and the jumper routing (JP3/JP4/JP5, measured versus inferred). Remove the
  "v1.37 Phase 182" provenance, and keep the date and the board.
- 0x0D: never implement the 12V hardware chip erase. Algorithm 5 never gets `FLAG_CAN_ERASE`.
  `write` does no blank check. The protocol is UNVERIFIED on silicon.
- `--pulse-us` is not a wire limit. The limit is `MSG_ERR_PULSE_TOO_WIDE`, on `0x0B` only.
- `messages.h` is generated. Point to `protocol/message-catalog`.
- The hardware-revision ADC bands: they detect the A3-net composition, not R41. If you change the
  defines, update the wiki page `Shield Revisions` in the same change.
- The native environment: which units compile, and that the stubs are no-ops. Point to
  `testing/native-firmware-tests` for how to add a suite.

**Drop**:
- The handler table.
- The numbered dispatch list. Replace it with the invariants above.
- The 27C per-row table.
- The energy-cap arithmetic.
- The ack byte layout. Point to `protocol/rollout-compatibility`.
- The key-files list.
- The constants and flags lists. Point to `protocol/duplicated-constants` and
  `protocol/retired-ordinals`.
- The whole PY32 flash-path section, and its environment variables.
- The repeated "legacy source scan, not a guard" caveats.
- The 0x0D erase-sequence bytes (they are in the code).

Commit: `docs: trim CLAUDE.md to what the code and standards do not say`.

## Task 4: Trim `firestarter_app/CLAUDE.md` (target about 80 lines)

**Keep**:
- The dev commands.
- CI runs Python 3.11, and a green run on the devcontainer's newer Python proves nothing.
- The CI steps in one short list: the ruff scope, coverage 70, the py32 job.
- A `beta` push publishes to PyPI, the workflow has no path filter, and PyPI never takes the same
  version two times.
- mypy is not a CI gate. The strict modules are listed in `pyproject.toml` (remove the list here).
- `tools/` is outside every CI gate.
- The data-flow diagram.
- `chip_database.json` is generated. Point to `chipdb/fix-the-decoder`.
- The two places that add to the generated data (`extra_chips.json`, `datasheet_overrides.json`).
- `part_number` can hold several comma-separated names.
- The pinned minipro commit.
- The release-channel gate, and that an environment-variable gate fails open (only
  `FIRESTARTER_DEV_TOOLS=1` is allowed).
- The 0x0D promotion: both arms, "do not make either arm wider", and why (12V on pin 1, which is A14
  on those parts). Keep the seven chips that stay on 0x07.
- The `py32_dfu.py` note: no test on silicon covers it.
- `REVISION_*` pairs with `rurp_shield.h`. This is the one pair that `duplicated-constants` does not
  list. Also keep `0xFF` / `0xFE`.

**Drop**:
- The key-files list, except `py32_dfu.py` and `compare.py` (the one comparison engine).
- The wire-protocol JSON example.
- The list of 16 pinout keys.
- The `KNOWN_PROTOCOLS` list.
- The ruff rule-selection detail, except "a `# noqa` outside `E,F,I,UP` has no effect".
- The constants table. Point to `protocol/duplicated-constants` and `protocol/retired-ordinals`, and
  keep only the `REVISION_*` row.

Commit: `docs: trim CLAUDE.md to what the code and standards do not say`.

## Task 5: Root CLAUDE.md and gitlinks (meta)

1. Add a `## Standards` section: "Before you change protocol, chip-database, firmware, host or test
   code, read the relevant standard in `agent-os/standards/` (index: `index.yml`). The submodule
   CLAUDE.md files point to them and do not repeat them."
2. Keep the two "Read `firestarter_*/CLAUDE.md`" lines. They are harmless, and they help when a file
   is opened from the root.
3. Commit the spec folder, the root edit and the advanced gitlinks for both submodules:
   `docs: trim submodule CLAUDE.md files, retire the PY32 twin; advance submodules`.

## Task 6: Memory hygiene

- Delete `reference_flash_path_record_sync_asserts_whole_repo_porcelain.md` and its line in
  MEMORY.md, because the test no longer exists.
- Add no new memory. The decisions are recorded in the spec.

## Verification

- fw: `pytest tests/ -q` in a **fresh clone** of `firestarter_fw` (`testing/standalone-checkout`). It
  must stay green. The only expected change in the count is the twin tests that are gone. Compare the
  count with a run before the change.
- fw: `pio test -e native_nodevtools` is not affected (no C change except comments). Run it once as a
  check.
- `grep -rn "\.planning\|SHARED:S\|meta_presence\|FIRESTARTER_META_ROOT" firestarter_fw/platform
  firestarter_fw/CLAUDE.md` finds nothing.
- `grep -n "Phase [0-9]\|v1\.[0-9][0-9] Phase" firestarter_*/CLAUDE.md` finds nothing.
- Read each trimmed CLAUDE.md against D-5. Each pointer must name a standard file that exists
  (`ls agent-os/standards/<path>.md`).
- `git status` is clean in all three repos after the commits, and the meta gitlinks match the
  submodule HEADs.
