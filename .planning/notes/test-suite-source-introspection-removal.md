---
title: Source-introspecting tests removed from firestarter_app
date: 2026-09-14
context: /gsd-explore session on test relevance; operator ruling on source-text scanning
---

## The ruling

The operator ruled that **source-text scanning is not a legitimate testing technique**, and that the
ruling covers `ast`-based introspection as well as literal substring matching — "not from any tests
in the projects". A follow-on instruction set the keep criterion: **only data-driven tests that
exercise production code stay.**

"Production code" here is the shipped pip package (`firestarter/`, including its `data/*.json`).
Reading `chip_database.json` or `pinouts.json` and asserting on parsed records is a data-driven test
and stays. Reading a `.py`, `.c`, `.h`, `.md`, `.yml` or `.toml` file and asserting about its
contents does not, whatever the matcher.

## What triggered it

The v1.38 submodule rename (`firestarter/` to `firestarter_fw/`, commit `28cbf110`) moved the
sibling checkout out from under `tests/fw_presence.py`, whose `FW_ROOT` was hardcoded as
`<app repo>/../firestarter`. `FW_REPO_PRESENT` went false and all 71 `@requires_fw` legs began
skipping. No CI workflow in either repository sets `FIRESTARTER_FW_ROOT` or checks out the firmware,
so those legs had never run in CI at all — only in a devcontainer sibling layout.

Measured with `FIRESTARTER_FW_ROOT=/workspaces/firestarter_fw`, the whole suite was
**2145 passed, 0 failed, 0 skipped**: the gates were not masking a real failure, they were merely
unreachable. That is the failure mode of the technique — host-side source-scanning gates fail open,
and nothing goes red to announce that coverage has stopped.

## How the removal set was determined

Regex classification of the test sources gave answers ranging from 80 to 205 tests depending on the
heuristic — the same brittleness the ruling rejects. The set was instead measured empirically: a
pytest plugin patched `builtins.open`, `Path.open`, `Path.read_text` and `Path.read_bytes` and
recorded the resolved path of every read per test nodeid across a full run.

Result: **129 tests read source or docs at runtime; 377 read `.json`/`.xml` data.** The 129 defined
the removal set; the 377 stayed.

## What went

- **24 test modules deleted.** Cross-repo parity scanners (`test_json_key_parity`,
  `test_sdp_table_parity`, `test_revision_constants_parity`, `test_parse_gate_admission`,
  `test_cap03_ack_layout_parity`), the firmware-presence gate and its census
  (`test_fw_presence`, `test_skip_census`), source censuses (`test_voltage_field_census`,
  `test_readback_inventory`, `test_numeric_schema_source_scan`), doc-claim scanners
  (`test_lockable_proms_doc_claims`), config/CI scanners (`test_python_floor_agreement`,
  `test_runtime_dependencies`, `test_py32_packaging`, `test_pyusb_gating`), generator goldens
  (`test_gen_validation_header`, `test_sdp_bus_config_drift`), and tooling tests that never touched
  the shipped package (`test_update_version`, `test_matrix_schema`, `test_gen_test_image`,
  `test_devtest_issue_corpus`, `test_variant_decode_evidence_stability`).
- **`tests/fw_presence.py`** and the scaffolding that existed only to be scanned: the
  `fake_firestarter/` fixture repo and 11 `planted_*` fixture files.
- **~54 individual tests** surgically removed from modules that keep their behavioural coverage.

Roughly a third of what went tested the scanning machinery rather than the product —
`test_a_planted_*_reddens_the_pin`, `test_scan_targets_are_non_vacuous`,
`test_gate_fails_closed_on_an_unreadable_firmware_path`, `test_this_module_cannot_be_silently_skipped`.
Three tests in `test_readback_inventory` asserted on **docstring prose**.

## What is now unguarded — stated, not hidden

These invariants had a scanner and now have nothing. None had working CI enforcement before the
removal, so no enforcement was actually lost; the claim of enforcement was.

| Invariant | Was "guarded" by |
|---|---|
| host `COMMAND_*` / `FLAG_*` vs `firestarter_fw/include/firestarter.h` | `test_revision_constants_parity` |
| `REVISION_*` vs `rurp_shield.h` | `test_revision_constants_parity` |
| SDP disable table vs `eeprom_28c.cpp` | `test_sdp_table_parity` |
| JSON wire keys vs `json_parser.c` | `test_json_key_parity` |
| CAP-03 ack byte layout across the seam | `test_cap03_ack_layout_parity` |
| committed `validation_matrix.h` / `sdp_bus_config.h` vs their generators | the two generator goldens |
| Python floor agreement across `pyproject.toml` and four workflows | `test_python_floor_agreement` |

**The replacement for the first five is codegen, not another test.** `tools/catalog/codegen.py`
already generates `firestarter/messages.py` and `firestarter_fw/include/messages.h` from one
`messages.toml`; parity by construction leaves nothing to assert. **The replacement for the
generated headers is a build step** — regenerate in CI and fail on a dirty tree — not a test that
reads the committed artifact back.

## Standing rule this produces

A test may not open a source or documentation file and assert about its contents. If an invariant
spans two files, generate both from one source rather than testing that they agree.
